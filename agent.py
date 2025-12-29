import time
import logging
import asyncio
import uuid
from typing import Optional, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from rank_bm25 import BM25Okapi

from ingest import get_vector_store
from prompts import PROMPT_TEMPLATES
from behavior import classify_question, get_policy
from llm_client import get_llm_client

# Configure Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetrievalInsufficient(Exception):
    """Raised when retrieval quality is below threshold."""
    pass

# Strict insufficient context message - enforced in post-processing
INSUFFICIENT_MSG = "This episode excerpt does not give enough detail to answer that."

class EpisodeCompanionAgent:
    def __init__(self, backend: str = "ollama", model_name: Optional[str] = None):
        """Initialize agent with abstracted LLM client.

        Args:
            backend: "ollama", "openai", or "gemini"
            model_name: Specific model name (optional)
        """
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client(backend, model_name)
        self.llm = self.llm_client.get_llm()
        # Lower temperature for more consistent structured output
        if hasattr(self.llm, 'temperature'):
            self.llm.temperature = 0.3
        self.model_name = getattr(self.llm_client, "model_name", "unknown")
        logger.info(f"EpisodeCompanionAgent initialized with backend={backend}, model={self.model_name}")

    # ---------------------------------------------------------------------
    # Retrieval & Fusion
    # ---------------------------------------------------------------------
    def _reciprocal_rank_fusion(self,
                                vector_results: List[tuple[float, Document]],
                                bm25_results: List[Document],
                                k: int = 60) -> List[Document]:
        """Fuse results from Vector and BM25 using Reciprocal Rank Fusion (RRF)."""
        fused_scores = {}
        # Vector results
        for rank, (doc, _score) in enumerate(vector_results):
            doc_id = doc.metadata.get("chunk_index") or doc.page_content[:50]
            fused_scores.setdefault(doc_id, {"doc": doc, "score": 0.0})
            rrf_score = 1 / (rank + k)
            boost = doc.metadata.get("priority", 1) * 0.005
            fused_scores[doc_id]["score"] += rrf_score + boost
        # BM25 results
        for rank, doc in enumerate(bm25_results):
            doc_id = doc.metadata.get("chunk_index") or doc.page_content[:50]
            fused_scores.setdefault(doc_id, {"doc": doc, "score": 0.0})
            rrf_score = 1 / (rank + k)
            boost = doc.metadata.get("priority", 1) * 0.005
            fused_scores[doc_id]["score"] += rrf_score + boost
        reranked = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in reranked]

    def _retrieve_gpk(self, episode_id: str, question: str, k: int = 8) -> List[Document]:
        """Hybrid retrieval (Vector + BM25) with RRF and header injection for citations."""
        try:
            vector_candidates = self.vector_store.similarity_search_with_score(
                question or "episode overview",
                k=k * 3,
                filter={"episode_id": episode_id},
            )
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            vector_candidates = []

        # BM25 retrieval
        try:
            all_episode_docs = self.vector_store.similarity_search(
                " ",
                k=200,
                filter={"episode_id": episode_id},
            )
            if not all_episode_docs:
                logger.warning(f"No docs found for episode {episode_id} for BM25.")
                bm25_results = []
            else:
                tokenized_corpus = [doc.page_content.split() for doc in all_episode_docs]
                bm25 = BM25Okapi(tokenized_corpus)
                tokenized_query = question.split()
                bm25_results = bm25.get_top_n(tokenized_query, all_episode_docs, n=k * 3)
        except Exception as e:
            logger.warning(f"BM25 retrieval failed: {e}, using only vector results")
            bm25_results = []

        fused_docs = self._reciprocal_rank_fusion(vector_candidates, bm25_results)
        # Inject header for citation if missing
        for doc in fused_docs:
            title = doc.metadata.get("paper_title")
            if not title or str(title).lower() == "none":
                title = "Episode Overview"
            
            header = f"[{title}] (source)\n"
            # Check if header is already present to avoid duplication
            if not doc.page_content.strip().startswith(f"[{title}]"):
                doc.page_content = header + doc.page_content
        return fused_docs[:k]

    def _expand_query(self, query: str, episode_id: str, conversation_history: str = "") -> str:
        """Placeholder for query expansion – currently a no‑op to keep latency low."""
        logger.info(f"Skipping query expansion: {query}")
        return query

    def _check_structure(self, mode: str, answer: str) -> bool:
        """Deterministic check for persona-specific structure."""
        if mode == "plain_english":
            return (
                ("tl;dr" in answer.lower() or "tldr" in answer.lower()) and
                "Key Ideas:" in answer and
                "Why this matters:" in answer
            )
        elif mode == "founder_takeaway":
            return (
                "Big Idea:" in answer and
                "Product Directions:" in answer and
                "Risks & Unknowns:" in answer
            )
        elif mode == "engineer_angle":
            return (
                "Core Principle:" in answer and
                "Architecture:" in answer and
                "Training Setup:" in answer and
                "Inference Pipeline:" in answer and
                "Trade-offs:" in answer
            )
        return True

    def _validate_answer(self, answer: str, context: str, question: str, mode: str) -> dict:
        """Validate answer quality with deterministic checks."""
        checks = {
            "has_substance": len(answer) > 120,
            "not_deflecting": (
                "does not give enough detail" not in answer.lower() and
                "i don't have that information" not in answer.lower()
            ),
            "cites_papers": "[" in answer and "]" in answer,
            "structure_ok": self._check_structure(mode, answer),
        }
        return checks

    async def _generate_with_timeout(self, chain, inputs: dict) -> str:
        """Generate answer with async timeout (60 s)."""
        try:
            # logger.info(f"Invoking LLM for query: {inputs.get('question', '')[:50]}...")
            result = await asyncio.wait_for(
                chain.ainvoke(inputs),
                timeout=60.0,
            )
            return result
        except asyncio.TimeoutError:
            logger.error("LLM generation timed out after 60s.")
            return f"I apologize, but I'm experiencing high response times right now. Based on the episode content, here's a brief summary:\n\n{inputs.get('context', '')[:500]}..."
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"I'm having trouble generating a response. Here's what I found in the episode:\n\n{inputs.get('context', '')[:500]}..."

    def _critique_answer(self, mode: str, context: str, question: str, answer: str) -> dict:
        """Use the LLM as a strict reviewer to verify grounding, structure, and citations."""
        critic_template = f"""
You are a strict reviewer.
You receive:
- Context (episode chunks)
- User question
- Model answer
Your job:
1. Verify the answer is grounded in the context.
2. Verify it follows the required structure for mode `{mode}`.
3. Verify it contains at least one citation in square brackets.
Return a JSON object ONLY with keys:
{{
  "grounded": true/false,
  "structure_ok": true/false,
  "has_citation": true/false,
  "issues": [list of strings]
}}
Context:
{context}

Question:
{question}

Answer:
{answer}
"""
        chain = ChatPromptTemplate.from_template(critic_template) | self.llm | StrOutputParser()
        try:
            raw = chain.invoke({})
        except Exception as e:
            logger.error(f"Critic generation failed: {e}")
            return {"grounded": False, "structure_ok": False, "has_citation": False, "issues": ["critic_failed"]}
        try:
            import json
            start = raw.find('{')
            end = raw.rfind('}')
            json_str = raw[start:end+1]
            result = json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse critic JSON: {e}")
            result = {"grounded": False, "structure_ok": False, "has_citation": False, "issues": ["parse_error"]}
        return result

    def get_answer(self,
                   episode_id: str,
                   mode: str,
                   query: str,
                   user_id: Optional[str] = None,
                   conversation_history: str = "") -> dict:
        """Synchronous wrapper that runs async generation with optional critic retry."""
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. Classify Question & Get Policy
        question_type = classify_question(query)
        policy = get_policy(mode, question_type)
        
        logger.info(f"Trace={trace_id} | Query='{query}' | Mode={mode} | Type={question_type}")
        
        # Build instructions from policy
        length_instruction = f"- Keep the answer between {policy.min_words} and {policy.max_words} words."
        sections_instruction = ""
        if policy.include_sections:
            sections_instruction = "- Include these sections: " + ", ".join(policy.include_sections) + "."
        
        if mode not in PROMPT_TEMPLATES:
            error_msg = f"Invalid mode: {mode}. Available modes: {list(PROMPT_TEMPLATES.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        prompt_template = PROMPT_TEMPLATES[mode]

        try:
            expanded_query = self._expand_query(query, episode_id, conversation_history)
            
            # Retrieval
            retrieval_start = time.time()
            docs = self._retrieve_gpk(episode_id, expanded_query, k=5)
            retrieval_ms = (time.time() - retrieval_start) * 1000
            
            logger.info(f"Trace={trace_id} | Retrieved {len(docs)} chunks in {retrieval_ms:.2f}ms")
            context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])

            chain = prompt_template | self.llm | StrOutputParser()
            
            # Ensure we have an event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Generation inputs
            gen_inputs = {
                "context": context_text,
                "question": query,
                "length_instruction": length_instruction,
                "sections_instruction": sections_instruction
            }

            llm_start = time.time()
            answer = loop.run_until_complete(self._generate_with_timeout(chain, gen_inputs))
            llm_ms = (time.time() - llm_start) * 1000

            # Critic check – if fails, retry with more context
            critic_start = time.time()
            critique = self._critique_answer(mode, context_text, query, answer)
            critic_ms = (time.time() - critic_start) * 1000
            
            if not (critique.get("grounded") and critique.get("structure_ok") and critique.get("has_citation")):
                logger.info(f"Trace={trace_id} | Critic failed: {critique.get('issues')}. Retrying...")
                
                more_docs = self._retrieve_gpk(episode_id, expanded_query, k=10)
                more_context = "\n\n---\n\n".join([doc.page_content for doc in more_docs])
                gen_inputs["context"] = more_context
                
                answer = loop.run_until_complete(self._generate_with_timeout(chain, gen_inputs))
                # Optional second critic (ignored)
                _ = self._critique_answer(mode, more_context, query, answer)

            # Post-processing: Enforce strict insufficient context message
            # If LLM tried to add extra commentary, strip it down to only the safe message
            if INSUFFICIENT_MSG.lower() in answer.lower():
                logger.info(f"Trace={trace_id} | Detected insufficient context message, enforcing strict format")
                answer = INSUFFICIENT_MSG

            # Final quality checks
            if "I apologize" in answer or "I'm having trouble" in answer:
                quality_checks = {"error": "Timeout or generation error, returned fallback"}
            else:
                quality_checks = self._validate_answer(answer, context_text, query, mode)
                logger.info(f"Trace={trace_id} | Quality checks: {quality_checks}")

        except RetrievalInsufficient as e:
            logger.warning(f"Trace={trace_id} | Retrieval insufficient: {e}")
            answer = (
                "I'm sorry, I couldn't find enough information in this episode to answer "
                "your question accurately. Could you try rephrasing or asking about a specific "
                "paper mentioned in the episode?"
            )
            quality_checks = {"error": str(e)}
            docs = []
            expanded_query = query
            context_text = ""
            retrieval_ms = 0
            llm_ms = 0
            critic_ms = 0

        total_latency_ms = (time.time() - start_time) * 1000
        logger.info(f"Trace={trace_id} | Total Latency: {total_latency_ms:.2f}ms")

        source_papers = list({
            doc.metadata.get("paper_title", "Episode Overview")
            for doc in docs if doc.metadata
        })
        tokens_in = len(context_text) // 4 if context_text else 0
        tokens_out = len(answer) // 4

        return {
            "episode_id": episode_id,
            "mode": mode,
            "answer": answer,
            "metadata": {
                "trace_id": trace_id,
                "latency_ms": round(total_latency_ms, 2),
                "stage_latency": {
                    "retrieval": round(retrieval_ms, 2),
                    "llm": round(llm_ms, 2),
                    "critic": round(critic_ms, 2)
                },
                "used_chunks": len(docs),
                "expanded_query": expanded_query,
                "quality_checks": quality_checks,
                "source_papers": source_papers,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "model": self.model_name,
                "question_type": question_type
            },
        }

if __name__ == "__main__":
    agent = EpisodeCompanionAgent()
    try:
        response = agent.get_answer(
            episode_id="ai-research-daily-2025-11-20",
            mode="plain_english",
            query="What are the main papers?",
        )
        print(response)
    except Exception as e:
        logger.error(f"Error during test: {e}")
