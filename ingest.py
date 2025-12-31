import os
import re
from dataclasses import dataclass
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Initialize Embeddings
# Note: Ensure GOOGLE_API_KEY is set in environment
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize Vector Store (Persistent)
PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "episode_scripts"

@dataclass
class PaperEntryGpk:
    title: str
    url: Optional[str] = None
    rank: Optional[int] = None         # 1..7 for "Top papers"
    in_audio: bool = False             # True if mentioned in Listen transcript
    text_content: Optional[str] = None # The full text section for this paper
    # ArXiv metadata
    arxiv_id: Optional[str] = None
    authors: Optional[str] = None
    abstract: Optional[str] = None
    pdf_url: Optional[str] = None
    # Time-linked metadata
    timestamp_start: Optional[int] = None
    timestamp_end: Optional[int] = None

@dataclass
class EpisodeBundleGpk:
    episode_id: str
    date_str: str
    hook: str
    listen_url: str
    full_report: str
    audio_transcript: Optional[str]
    papers: List[PaperEntryGpk]

def get_vector_store():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY,
    )

def parse_daily_report_gpk(episode_id: str, report_text: str) -> EpisodeBundleGpk:
    """
    Very lightweight parser tuned to Kochi Daily Reports:
    - extracts date, hook line, listen URL
    - parses 'Papers Covered in Today's Episode'
    - parses 'Top Papers Today' titles + rough rank + text content
    """

    # date line: "Date: 2025-11-19" or "Wed 11/19/2025"
    m_date = re.search(r"Date:\s*([0-9\-\/]+)", report_text)
    date_str = m_date.group(1) if m_date else ""

    # hook: first line with 🎙️
    m_hook = re.search(r"(🎙️[^\n]+)", report_text)
    hook = m_hook.group(1).strip() if m_hook else ""

    # listen url
    m_listen = re.search(r"Listen:\s*(https?://\S+)", report_text)
    listen_url = m_listen.group(1).strip() if m_listen else ""

    # "Papers Covered in Today's Episode" section
    papers: list[PaperEntryGpk] = []
    covered_block = ""
    m_cov = re.search(r"Papers Covered in Today's Episode(.+?)\n\nIN DEPTH", report_text, re.S)
    if m_cov:
        covered_block = m_cov.group(1)
        for line in covered_block.splitlines():
            line = line.strip()
            if not line:
                continue
            # Kandinsky 5.0: huggingface.co/papers/2511.14993
            m = re.match(r"(.+?):\s*(\S+)", line)
            if m:
                papers.append(PaperEntryGpk(title=m.group(1).strip(), url=m.group(2).strip(), in_audio=True))

    # "Top Papers Today" section
    m_top = re.search(r"🌟 Top Papers Today(.+?)📊 Report Metadata", report_text, re.S)
    if m_top:
        # split by numbered entries "1. ARC Is a Vision Problem!"
        top_block = m_top.group(1)
        entries = re.split(r"\n(?=\d+\.\s)", top_block)
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            # first line "1. ARC Is a Vision Problem! ⭐⭐⭐⭐⭐"
            first_line = entry.splitlines()[0]
            m_title = re.match(r"\d+\.\s+(.+?)(?:\s+⭐|$)", first_line)
            if not m_title:
                continue
            title = m_title.group(1).strip()
            
            # Find if we already have it
            existing_paper = next((p for p in papers if p.title.startswith(title) or title.startswith(p.title)), None)
            
            if existing_paper:
                existing_paper.rank = existing_paper.rank or len([x for x in papers if x.rank]) + 1
                existing_paper.text_content = entry # Store the full text
            else:
                # new paper
                rank = len([p for p in papers if p.rank is not None]) + 1
                papers.append(PaperEntryGpk(title=title, rank=rank, in_audio=False, text_content=entry))

    return EpisodeBundleGpk(
        episode_id=episode_id,
        date_str=date_str,
        hook=hook,
        listen_url=listen_url,
        full_report=report_text,
        audio_transcript=None,  # you can attach audio text separately
        papers=papers,
    )

def choose_chunk_params(text: str):
    """Helper to choose chunk size based on text length"""
    if len(text) < 2000:
        return 500, 100
    return 1000, 200

def ingest_bundle_gpk(bundle: EpisodeBundleGpk, audio_text: str | None = None) -> dict:
    """
    Ingest a full episode bundle:
    - full report (all sections)
    - optional audio transcript (treated as 'summary' source)
    Each chunk gets metadata: episode_id, source_type, section, paper_title, priority.
    """
    
    # Use the global vector store getter
    vs = get_vector_store()

    docs = []
    metadatas = []

    # 1) Full report chunks (General Context)
    # We still keep this for general queries, but maybe lower priority if it overlaps?
    # Actually, let's keep it but maybe exclude the paper sections if we want to be strict.
    # For now, redundancy is fine, but let's prioritize the specific paper chunks.
    
    chunk_size, overlap = choose_chunk_params(bundle.full_report)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", "? ", "! "],
    )
    report_chunks = splitter.split_text(bundle.full_report)
    for i, chunk in enumerate(report_chunks):
        docs.append(chunk)
        metadatas.append({
            "episode_id": bundle.episode_id,
            "source_type": "report",
            "section": "full_report",
            "paper_title": "None", 
            "priority": 1,      # Low priority for generic full report chunks
            "chunk_index": i,
        })

    # 2) Audio transcript chunks (if provided)
    if audio_text:
        a_chunk_size, a_overlap = choose_chunk_params(audio_text)
        a_splitter = RecursiveCharacterTextSplitter(
            chunk_size=a_chunk_size,
            chunk_overlap=a_overlap,
            separators=[". ", "? ", "! ", "\n"],
        )
        audio_chunks = a_splitter.split_text(audio_text)
        for i, chunk in enumerate(audio_chunks):
            docs.append(chunk)
            metadatas.append({
                "episode_id": bundle.episode_id,
                "source_type": "audio",
                "section": "audio_summary",
                "paper_title": "None",
                "priority": 3,   # higher priority
                "chunk_index": i,
            })

    # 3) Individual paper chunks (Smart Chunking)
    for p in bundle.papers:
        if p.text_content:
            # Chunk the specific paper text
            p_chunk_size, p_overlap = choose_chunk_params(p.text_content)
            p_splitter = RecursiveCharacterTextSplitter(
                chunk_size=p_chunk_size,
                chunk_overlap=p_overlap,
                separators=["\n\n", "\n", ". "],
            )
            p_chunks = p_splitter.split_text(p.text_content)
            
            for i, chunk in enumerate(p_chunks):
                docs.append(chunk)
                # Prepare metadata with timestamps if available
                md = {
                    "episode_id": bundle.episode_id,
                    "source_type": "paper_section",
                    "section": "top_papers",
                    "paper_title": p.title,
                    "priority": 4, # High priority for specific paper content
                    "chunk_index": i,
                }
                if p.timestamp_start is not None:
                    md["timestamp_start"] = p.timestamp_start
                if p.timestamp_end is not None:
                    md["timestamp_end"] = p.timestamp_end
                
                metadatas.append(md)
        else:
             # Fallback for papers without text content (e.g. from "Papers Covered" list only)
            doc_text = f"Paper: {p.title}.\n\nThis paper is part of AI Research Daily {bundle.date_str}."
            docs.append(doc_text)
            metadatas.append({
                "episode_id": bundle.episode_id,
                "source_type": "paper_stub",
                "section": "papers_covered",
                "paper_title": p.title,
                "priority": 2,
                "chunk_index": 0,
            })

    if docs:
        ids = vs.add_texts(docs, metadatas=metadatas)
    else:
        ids = []

    return {
        "episode_id": bundle.episode_id,
        "report_chunks": len(report_chunks),
        "audio_chunks": len(audio_chunks) if audio_text else 0,
        "paper_entries": len(bundle.papers),
        "ids_count": len(ids)
    }

def ingest_episode(episode_id: str, text: str):
    """
    Legacy ingestion function for backward compatibility.
    Now wraps the new logic by creating a minimal bundle.
    """
    # Try to parse it as a daily report first
    try:
        bundle = parse_daily_report_gpk(episode_id, text)
        # If parsing found something useful (like papers), use the new path
        if bundle.papers or bundle.date_str:
             return ingest_bundle_gpk(bundle)
    except Exception:
        pass
        
    # Fallback to simple ingestion
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.create_documents([text])
    
    # Add metadata to each chunk
    for chunk in chunks:
        chunk.metadata["episode_id"] = episode_id
        
    vector_store = get_vector_store()
    
    # Add to vector store
    ids = vector_store.add_documents(chunks)
    
    return {
        "episode_id": episode_id,
        "chunks_count": len(chunks),
        "ids": ids
    }

if __name__ == "__main__":
    # Simple test
    print("Ingesting sample...")
    try:
        # You can add test code here
        pass
    except Exception as e:
        print(f"Error: {e}")
