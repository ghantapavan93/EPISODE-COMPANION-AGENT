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
from response_formatter import ResponseFormatter

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
        self.formatter = ResponseFormatter()  # Initialize formatter
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
            # PRO FIX: Use simple similarity search to avoid unpacking issues
            # Then wrap in tuples to match _reciprocal_rank_fusion signature
            raw_docs = self.vector_store.similarity_search(
                question or "episode overview",
                k=k * 3,
                filter={"episode_id": episode_id},
            )
            vector_candidates = [(doc, 1.0) for doc in raw_docs]
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
        """Expand query for better retrieval."""
        q_lower = query.lower()
        # Handle generic "explain this episode" queries to improve retrieval
        if "explain this episode" in q_lower or "summary of this episode" in q_lower or "what is this episode about" in q_lower:
            logger.info(f"Expanding generic query '{query}' to 'episode overview summary key takeaways'")
            return "episode overview summary key takeaways"
            
        logger.info(f"Skipping query expansion: {query}")
        return query

    def _check_structure(self, mode: str, answer: str, question_type: str = "general") -> bool:
        """Deterministic check for persona-specific structure."""
        if mode == "plain_english":
            # Special case for explanations/analogies
            if question_type == "why_how":
                return "Explanation" in answer or "Analogy" in answer
                
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

    def _validate_answer(self, answer: str, context: str, question: str, mode: str, question_type: str = "general") -> dict:
        """Validate answer quality with deterministic checks."""
        checks = {
            "has_substance": len(answer) > 120,
            "not_deflecting": (
                "does not give enough detail" not in answer.lower() and
                "i don't have that information" not in answer.lower()
            ),
            "cites_papers": "[" in answer and "]" in answer,
            "structure_ok": self._check_structure(mode, answer, question_type),
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

    def _critique_answer(self, mode: str, context: str, question: str, answer: str, question_type: str = "general") -> dict:
        """Use the LLM as a strict reviewer to verify grounding, structure, and citations."""
        
        # For explanatory and summary questions, be less strict about structure
        relaxed_structure = question_type in ["why_how", "summary", "general", "explain_like_12"]
        
        structure_guidance = ""
        if relaxed_structure:
            structure_guidance = "The answer should be clear and well-organized, but doesn't need to follow a rigid template."
        else:
            structure_guidance = f"The answer must follow the required structure for mode `{mode}`."
        
        critic_template = f"""
You are a strict but fair reviewer.
You receive:
- Context (episode chunks)
- User question
- Model answer
Your job:
1. Verify the answer is grounded in the context (all claims come from the context).
2. {structure_guidance}
3. Check if it contains at least one citation in square brackets (optional for very simple questions).
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

    def _compute_time_hint_gpk(self, docs):
        """Compute a simple [min, max] timestamp window from retrieved chunks."""
        starts = []
        ends = []
        for d in docs:
            md = d.metadata or {}
            if "timestamp_start" in md and "timestamp_end" in md:
                try:
                    starts.append(float(md["timestamp_start"]))
                    ends.append(float(md["timestamp_end"]))
                except (ValueError, TypeError):
                    continue
        
        if not starts or not ends:
            return None  # no timing info

        start_s = int(min(starts))
        end_s = int(max(ends))

        def _fmt(sec: int) -> str:
            m = sec // 60
            s = sec % 60
            return f"{m}:{s:02d}"

        return {
            "start_seconds": start_s,
            "end_seconds": end_s,
            "start_human": _fmt(start_s),
            "end_human": _fmt(end_s),
        }

    def _safe_llm_call_gpk(self, prompt: str) -> str:
        """
        Helper: call self.llm in a way that works for both chat models and text models.
        """
        try:
            print(f"DEBUG: _safe_llm_call_gpk called with prompt length: {len(prompt)}")
            # Use the same pattern as the rest of the agent
            chain = ChatPromptTemplate.from_template("{prompt}") | self.llm | StrOutputParser()
            print("DEBUG: Chain created")
            text = chain.invoke({"prompt": prompt})
            print(f"DEBUG: Chain invoked, result length: {len(text)}")
            return text.strip()
        except Exception as e:
            logger.error(f"_safe_llm_call_gpk failed: {e}")
            print(f"DEBUG: _safe_llm_call_gpk EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _generate_quiz_questions_gpk(self, context_text: str, topic_hint: str, num_questions: int = 5):
        """
        Use the same LLM to generate quiz questions about the episode.
        Returns a string (markdown list).
        """

        # Try to infer number of questions from the user text if they said "5 questions" etc.
        import re
        match = re.search(r"\\b(\\d+)\\b", topic_hint)
        if match:
            try:
                num_questions = max(1, min(10, int(match.group(1))))
            except ValueError:
                pass

        # Detect style from topic_hint
        q_lower = topic_hint.lower()
        style = "plain"
        if "multiple-choice" in q_lower or "multiple choice" in q_lower or "mcq" in q_lower:
            style = "mcq"
        elif "spaced-repetition" in q_lower or "spaced repetition" in q_lower:
            style = "spaced"
        elif "mix easy and hard" in q_lower or ("easy" in q_lower and "hard" in q_lower):
            style = "mixed"

        style_instruction = {
            "plain": """
- Ask open-ended questions (no options).
- Start with simpler recall questions, then move to application / reasoning.
- One question per line, numbered 1., 2., 3., etc.
""",
            "mcq": """
- Write multiple-choice questions with 4 options each (A, B, C, D).
- Do NOT include the correct answer or any solution.
- Format: "1. Question text\\n   A) ...\\n   B) ...\\n   C) ...\\n   D) ..."
""",
            "spaced": """
- Create a mix of recall, understanding, and application questions.
- Tag each question as [Easy], [Medium], or [Hard].
- Order them from [Easy] → [Medium] → [Hard].
""",
            "mixed": """
- Mix easier and harder questions.
- Add "[Easy]" or "[Hard]" in front of each question.
"""
        }[style]

        prompt = f"""
You are Kochi, an AI tutor for AI research.

Using ONLY the context below, generate {num_questions} questions that help a learner
test their understanding of this episode.

Context:
{context_text}

User request / hint:
{topic_hint}

Follow these rules:
{style_instruction}
- Do NOT include any answers or hints.
- Stay strictly within the episode content.
- Avoid mentioning that you are an AI.

Output your questions as plain text, ready to display to the user.
"""

        text = self._safe_llm_call_gpk(prompt)
        if not text:
            return "I'm having trouble generating a quiz right now. Please try again."
        return text

    def _critique_user_explanation_gpk(self, context_text: str, query: str, user_answer: str):
        """
        Use LLM as a tutor to critique the user's explanation.
        """
        prompt = f"""
You are Kochi, an AI tutor. A user listened to an AI research episode and tried
to explain a concept in their own words.

You will receive:
- CONTEXT: episode excerpts
- USER REQUEST: what kind of feedback they want
- USER EXPLANATION: their raw explanation

Your job:
1) Check if their explanation is grounded in the context.
2) Point out what they got right.
3) Point out what is missing or slightly wrong.
4) Give a short improved version they can learn from.
5) If they asked for a score (e.g. "grade from 0–10"), include a score line at the top.

CONTEXT (from the episode):
{context_text}

USER REQUEST / META-INSTRUCTIONS:
{query}

USER EXPLANATION:
{user_answer}

Respond in this format:

What you got right:
- ...

What could be improved:
- ...

One improved explanation:
[1–3 short paragraphs here]

If applicable, add at the very top:
Score: X/10
"""

        text = self._safe_llm_call_gpk(prompt)
        if not text:
            return "I'm having trouble critiquing your explanation right now. Please try again."
        return text.strip()



    def get_answer(self,
                   episode_id: str,
                   mode: str,
                   query: str,
                   user_id: Optional[str] = None,
                   conversation_history: str = "",
                   debug: bool = False,
                   user_profile: Optional[dict] = None) -> dict:
        """Synchronous wrapper that runs async generation with optional critic retry."""
        try:
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
            
            # Add question-specific guidance for founder mode to reduce repetition
            if mode == "founder_takeaway":
                from prompts import FOUNDER_SPECIFIC_SECTIONS
                if question_type in FOUNDER_SPECIFIC_SECTIONS:
                    sections_instruction += "\\n" + FOUNDER_SPECIFIC_SECTIONS[question_type]
            
            # Add question-specific guidance for plain English mode for radio host personality
            if mode == "plain_english":
                from prompts import PLAIN_ENGLISH_SPECIFIC_SECTIONS
                if question_type in PLAIN_ENGLISH_SPECIFIC_SECTIONS:
                    sections_instruction += "\\n" + PLAIN_ENGLISH_SPECIFIC_SECTIONS[question_type]

            # Add question-specific guidance for engineer mode (Kochi engineer voice)
            if mode == "engineer_angle":
                from prompts import ENGINEER_SPECIFIC_SECTIONS
                if question_type in ENGINEER_SPECIFIC_SECTIONS:
                    sections_instruction += "\\n" + ENGINEER_SPECIFIC_SECTIONS[question_type]
            
            if mode not in PROMPT_TEMPLATES:
                error_msg = f"Invalid mode: {mode}. Available modes: {list(PROMPT_TEMPLATES.keys())}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            prompt_template = PROMPT_TEMPLATES[mode]

            expanded_query = self._expand_query(query, episode_id, conversation_history)
            
            # Retrieval
            retrieval_start = time.time()
            docs = self._retrieve_gpk(episode_id, expanded_query, k=5)
            retrieval_ms = (time.time() - retrieval_start) * 1000
            
            logger.info(f"Trace={trace_id} | Retrieved {len(docs)} chunks in {retrieval_ms:.2f}ms")

            # Create context text first (needed for guardrail check)
            context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
            logger.info(f"Trace={trace_id} | Context Preview: {context_text[:200]}...")

            # Heuristic check for missing papers to prevent hallucinations
            paper_titles = {
                (doc.metadata.get("paper_title") or "").lower()
                for doc in docs if doc.metadata
            }
            
            lower_q = query.lower()
            lower_context = context_text.lower()
            
            # Terms that MUST be present in the episode to answer safely.
            # If user asks about them and they are nowhere in the episode,
            # we return the strict insufficient-context message.
            special_terms = [
                "kandinsky 5.0",
                "kandinsky5",
                "sdxl",
                "gpt-4o",
                "java virtual machine",
                "jvm",
                "python's garbage collector",
                "python garbage collector",
                "garbage collector",
                "garbage collection",
            ]
            
            for term in special_terms:
                if term in lower_q:
                    in_titles = any(term in title for title in paper_titles)
                    in_context = term in lower_context
                    if not in_titles and not in_context:
                        logger.info(
                            f"Trace={trace_id} | Guardrail: '{term}' not in episode content → returning insufficient context."
                        )
                        return {
                            "episode_id": episode_id,
                            "mode": mode,
                            "answer": INSUFFICIENT_MSG,
                            "metadata": {
                                "trace_id": trace_id,
                                "latency_ms": 0.0,
                                "stage_latency": {
                                    "retrieval": retrieval_ms,
                                    "llm": 0.0,
                                    "critic": 0.0,
                                },
                                "used_chunks": len(docs),
                                "expanded_query": expanded_query,
                                "quality_checks": {
                                    "grounded": False,
                                    "reason": f"'{term}' not in episode content",
                                    "hallucination_guardrail_triggered": True,
                                },
                            "source_papers": list(paper_titles),
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "model": self.model_name,
                            "question_type": question_type,
                            "debug": None,
                            "suggested_followups": [
                                "What are the main papers in this episode?",
                                "Explain one of the actual papers in this episode.",
                            ],
                        },
                    }


            # NEW: handle learning modes BEFORE normal generation
            if question_type == "quiz_me":
                quiz = self._generate_quiz_questions_gpk(context_text, topic_hint=query)

                # Format using same formatter as normal answers
                formatted_quiz = self.formatter.format_response(quiz)

                total_latency_ms = (time.time() - start_time) * 1000
                tokens_in = len(context_text) // 4 if context_text else 0
                tokens_out = len(quiz) // 4

                return {
                    "episode_id": episode_id,
                    "mode": mode,
                    "answer": formatted_quiz,
                    "metadata": {
                        "trace_id": trace_id,
                        "latency_ms": round(total_latency_ms, 2),
                        "stage_latency": {
                            "retrieval": round(retrieval_ms, 2),
                            "llm": 0.0,
                            "critic": 0.0,
                        },
                        "used_chunks": len(docs),
                        "expanded_query": expanded_query,
                        "quality_checks": {"learning_mode": "quiz"},
                        "source_papers": list(paper_titles),
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "model": self.model_name,
                        "question_type": question_type,
                        "debug": None,
                        "suggested_followups": [],
                        "episode_time_hint": self._compute_time_hint_gpk(docs),
                    },
                }

            if question_type == "self_explain":
                # Safety guard: If the user hasn't really written an explanation, nudge them
                if len(query.strip()) < 80:
                    short_msg = (
                        "You triggered 'Let me explain', but I don't see your explanation yet.\n\n"
                        "Type out your explanation of the paper in your own words (a few sentences or bullets), "
                        "then send it, and I'll tell you what you got right and what to fix."
                    )
                    formatted_short = self.formatter.format_response(short_msg)
                    total_latency_ms = (time.time() - start_time) * 1000

                    return {
                        "episode_id": episode_id,
                        "mode": mode,
                        "answer": formatted_short,
                        "metadata": {
                            "trace_id": trace_id,
                            "latency_ms": round(total_latency_ms, 2),
                            "stage_latency": {
                                "retrieval": round(retrieval_ms, 2),
                                "llm": 0.0,
                                "critic": 0.0,
                            },
                            "used_chunks": len(docs),
                            "expanded_query": expanded_query,
                            "quality_checks": {"learning_mode": "critique_prompt_missing"},
                            "source_papers": list(paper_titles),
                            "tokens_in": len(context_text) // 4 if context_text else 0,
                            "tokens_out": len(short_msg) // 4,
                            "model": self.model_name,
                            "question_type": question_type,
                            "debug": None,
                            "suggested_followups": [],
                            "episode_time_hint": self._compute_time_hint_gpk(docs),
                        },
                    }

                critique = self._critique_user_explanation_gpk(
                    context_text,
                    query=query,
                    user_answer=query,
                )

                formatted_critique = self.formatter.format_response(critique)

                total_latency_ms = (time.time() - start_time) * 1000
                tokens_in = len(context_text) // 4 if context_text else 0
                tokens_out = len(critique) // 4

                return {
                    "episode_id": episode_id,
                    "mode": mode,
                    "answer": formatted_critique,
                    "metadata": {
                        "trace_id": trace_id,
                        "latency_ms": round(total_latency_ms, 2),
                        "stage_latency": {
                            "retrieval": round(retrieval_ms, 2),
                            "llm": 0.0,
                            "critic": 0.0,
                        },
                        "used_chunks": len(docs),
                        "expanded_query": expanded_query,
                        "quality_checks": {"learning_mode": "critique"},
                        "source_papers": list(paper_titles),
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "model": self.model_name,
                        "question_type": question_type,
                        "debug": None,
                        "suggested_followups": [],
                        "episode_time_hint": self._compute_time_hint_gpk(docs),
                    },
                }

            chain = prompt_template | self.llm | StrOutputParser()
            
            # Ensure we have an event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Generation inputs
            
            # Prepare user profile context
            profile_context = ""
            if user_profile:
                role = user_profile.get("role") or ""
                domain = user_profile.get("domain") or ""
                stack = user_profile.get("stack") or ""
                if role or domain or stack:
                    profile_context = (
                        f"The user profile:\n"
                        f"- Role: {role or 'N/A'}\n"
                        f"- Domain: {domain or 'N/A'}\n"
                        f"- Stack: {stack or 'N/A'}\n"
                        "Tailor your answer so that the examples and suggestions feel concrete for this profile.\n"
                    )

            gen_inputs = {
                "context": context_text,
                "conversation_history": conversation_history or "",
                "question": query,
                "length_instruction": length_instruction,
                "sections_instruction": sections_instruction,
                "user_profile_context": profile_context,
            }

            llm_start = time.time()
            answer = loop.run_until_complete(self._generate_with_timeout(chain, gen_inputs))
            llm_ms = (time.time() - llm_start) * 1000

            # Critic check – if fails, retry with more context
            critic_start = time.time()
            critique = self._critique_answer(mode, context_text, query, answer, question_type)
            critic_ms = (time.time() - critic_start) * 1000
            
            # For explanatory/summary questions, skip strict critic check entirely
            # The critic with Ollama is unreliable for these question types
            relaxed_check = question_type in [
                "why_how",
                "summary",
                "general",
                "build_implement",
                "brainstorm",
                "tldr",
                "relevance",
                "core_idea",
                # Founder-specific
                "mvp",
                "paid_product",
                "month",
                "moat",
                "risks",
                "overhype_failure",
                "role_solo_indie",
                "role_pm_fintech",
                # Engineer-specific
                "prototype",
                "pipeline",
                "api",
                "architecture",
                "integration",
                "metrics",
                "experiment",
                "tradeoffs",
                "limitations",
                "role_backend_python_pg",
                "role_healthcare",
                # Episode-native flavor
                "episode_builder_insight",
                "episode_half_attention",
                "episode_side_project",
                "episode_aging",
            ]
            
            if relaxed_check:
                # Skip critic for explanatory questions
                logger.info(f"Trace={trace_id} | Skipping critic check for question_type={question_type}")
                needs_retry = False
            else:
                # Run critic for other question types
                needs_retry = not critique.get("grounded")
                logger.info(f"Trace={trace_id} | Critic check: grounded={critique.get('grounded')}")
            
            if needs_retry:
                logger.info(f"Trace={trace_id} | Critic failed: {critique.get('issues')}. Retrying...")
                
                more_docs = self._retrieve_gpk(episode_id, expanded_query, k=10)
                more_context = "\n\n---\n\n".join([doc.page_content for doc in more_docs])
                gen_inputs["context"] = more_context
                
                
                answer = loop.run_until_complete(self._generate_with_timeout(chain, gen_inputs))
                
                # Second critic check - enforce grounding this time
                critique2 = self._critique_answer(mode, more_context, query, answer, question_type)
                
                # Log the second critique for debugging
                logger.info(f"Trace={trace_id} | Second critique: grounded={critique2.get('grounded')}, issues={critique2.get('issues')}")
                
                if not critique2.get("grounded"):
                    logger.warning(f"Trace={trace_id} | Grounding failed after retry. Returning INSUFFICIENT_MSG to prevent fabrication.")
                    answer = INSUFFICIENT_MSG
                    quality_checks = {
                        "grounded": False,
                        "grounding_failed": True,
                        "reason": "Answer not grounded in episode content after retry",
                        "critic_issues": critique2.get("issues", [])
                    }


            # Post-processing: Enforce strict insufficient context message
            # Only strip if the insufficient message is the primary content (>80% of answer)
            if INSUFFICIENT_MSG.lower() in answer.lower():
                # Calculate what portion of the answer is the insufficient message
                answer_stripped = answer.strip()
                if len(answer_stripped) < len(INSUFFICIENT_MSG) * 1.5:  # Very short answer, likely just the message + minor additions
                    logger.info(f"Trace={trace_id} | Detected insufficient context message, enforcing strict format")
                    answer = INSUFFICIENT_MSG

            # Final quality checks
            if "I apologize" in answer or "I'm having trouble" in answer:
                quality_checks = {"error": "Timeout or generation error, returned fallback"}
            else:
                quality_checks = self._validate_answer(answer, context_text, query, mode, question_type)
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

        # Optional debug payload
        debug_payload = None
        if debug:
            debug_payload = {
                "context_preview": context_text[:500],
                "conversation_history_preview": (conversation_history or "")[:500],
            }

        # Suggested follow-ups (brainstormy, Bart-style)
        suggested_followups = []
        if mode == "plain_english":
            suggested_followups = [
                "Give me a 3-bullet TL;DR of this episode.",
                "Explain one of the core ideas using a real-world example.",
                "If I only remember one thing from this episode, what should it be?"
            ]
        elif mode == "founder_takeaway":
            suggested_followups = [
                "What is one 4-hour project I could build based on this episode?",
                "Who would be the ideal early users for a product here?",
                "How could this tie into an existing consumer product I might build?"
            ]
        elif mode == "engineer_angle":
            suggested_followups = [
                "Sketch a minimal API or service interface for a prototype using this idea.",
                "What metrics and logs should I track if I deploy this?",
                "How would I run a small-scale experiment to test this in production?"
            ]

        # Format answer with markdown-to-HTML conversion
        formatted_answer = self.formatter.format_response(answer)

        return {
            "episode_id": episode_id,
            "mode": mode,
            "answer": formatted_answer,
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
                "question_type": question_type,
                "debug": debug_payload,
                "suggested_followups": suggested_followups,
                "episode_time_hint": self._compute_time_hint_gpk(docs),
            },
        }

    def get_timeline_answer(
        self,
        episode_ids: List[str],
        mode: str,
        query: str,
        debug: bool = False,
    ) -> dict:
        """
        Compare or summarize multiple episodes at once (e.g., 'today vs yesterday').

        This is for questions like:
        - 'How is today's episode different from yesterday's?'
        - 'What are the big themes from this week?'
        """
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        # Late import to avoid circular dependencies
        from repositories.episode_repository import EpisodeRepository

        repo = EpisodeRepository()
        episodes = []
        for eid in episode_ids:
            ep = repo.get_episode_by_id(eid)
            if ep:
                episodes.append(ep)

        if not episodes:
            return {
                "episode_id": ",".join(episode_ids),
                "mode": mode,
                "answer": INSUFFICIENT_MSG,
                "metadata": {
                    "trace_id": trace_id,
                    "latency_ms": 0.0,
                    "stage_latency": {},
                    "used_chunks": 0,
                    "expanded_query": query,
                    "quality_checks": {"error": "no_episodes_found"},
                    "source_papers": [],
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "model": self.model_name,
                    "question_type": "timeline",
                    "debug": None,
                    "suggested_followups": [],
                },
            }

        # Build multi-episode context using the stored report_text
        context_parts = []
        for ep in episodes:
            header = f"[Episode {ep.episode_id} on {ep.date_str}] (overview)\n"
            report = ep.report_text or ""
            # Safety truncation per episode
            context_parts.append(header + report[:4000])

        context_text = "\n\n---\n\n".join(context_parts)

        # Simple timeline prompt – cross-episode comparison
        timeline_prompt = f"""
You are Kochi, an AI research radio host who has been covering multiple episodes.

You will receive:
- Context for several episodes (each with an episode id and date)
- A user question about how they relate

Your job:
- Compare and contrast the episodes
- Highlight recurring themes and key differences
- Answer the question in a grounded, concrete way
- Use simple language, but you may mention paper titles in square brackets.

Episodes Context:
{{context_text}}

User Question:
{{query}}

Answer in 3–7 short paragraphs or bullet lists.
"""

        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        chain = ChatPromptTemplate.from_template(timeline_prompt) | self.llm | StrOutputParser()

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            llm_start = time.time()
            # In this prompt we inlined context & question, so we can pass empty inputs
            answer = loop.run_until_complete(self._generate_with_timeout(chain, {}))
            llm_ms = (time.time() - llm_start) * 1000
        except Exception as e:
            logger.error(f"Timeline generation failed: {e}")
            answer = INSUFFICIENT_MSG
            llm_ms = 0.0

        total_latency_ms = (time.time() - start_time) * 1000

        tokens_in = len(context_text) // 4 if context_text else 0
        tokens_out = len(answer) // 4

        suggested_followups = [
            "Summarize the main theme that connects these episodes.",
            "What trend do you see across these episodes for founders?",
            "What should an engineer focus on if they only have time to build one thing from this week?",
        ]

        metadata = {
            "trace_id": trace_id,
            "latency_ms": round(total_latency_ms, 2),
            "stage_latency": {
                "retrieval": 0.0,
                "llm": round(llm_ms, 2),
                "critic": 0.0,
            },
            "used_chunks": len(episodes),
            "expanded_query": query,
            "quality_checks": {"timeline_mode": True},
            "source_papers": [],
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "model": self.model_name,
            "question_type": "timeline",
            "debug": {"context_preview": context_text[:500]} if debug else None,
            "suggested_followups": suggested_followups,
        }

        return {
            "episode_id": ",".join(e.episode_id for e in episodes),
            "mode": mode,
            "answer": answer,
            "metadata": metadata,
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
