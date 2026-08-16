"""
RAG chain — the core retrieve → augment → generate pipeline.

Steps when run_query() is called:
    1. Query embedded by the configured embedding provider (e.g. text-embedding-ada-002)
  2. pgvector cosine similarity search → top-k chunks
  3. Chunks stuffed into prompt template
    4. Claude generates a cited answer
  5. Response type classified (answer / not_found / out_of_context)
"""
import os
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from db.vectorstore import get_vectorstore, search_with_score
from prompts.sop_prompt import RAG_PROMPT_TEMPLATE
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL          = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
TOP_K                    = int(os.getenv("TOP_K", 6))
SOP_SIMILARITY_THRESHOLD = float(os.getenv("SOP_SIMILARITY_THRESHOLD", 0.85))


def get_llm() -> ChatAnthropic:
    return ChatAnthropic(model=ANTHROPIC_MODEL, streaming=False)


def build_chain() -> RetrievalQA:
    """
    Builds the RetrievalQA chain.
    chain_type="stuff" → all retrieved chunks stuffed into one prompt.
    """
    llm       = get_llm()
    retriever = get_vectorstore().as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE,
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


def run_query(question: str) -> dict:
    """
    Full RAG pipeline for one question.

    Returns:
        {
            type:    "answer" | "not_found" | "out_of_context",
            answer:  str,
            sources: list[str],
        }
    """
    # Step 1 — Similarity threshold guard (avoids LLM call for off-topic queries)
    scored = search_with_score(question, k=1)
    if scored:
        top_score = scored[0][1]
        if top_score > SOP_SIMILARITY_THRESHOLD:
            return {
                "type":    "out_of_context",
                "answer":  "OUT_OF_CONTEXT: This question is outside the scope "
                           "of the loaded SOP documents.",
                "sources": [],
            }

    # Step 2 — Run the chain (embed → search → stuff → generate)
    chain  = build_chain()
    result = chain({"query": question})

    answer  = result["result"]
    sources = list({
        d.metadata.get("source", "Unknown")
        for d in result["source_documents"]
    })

    # Step 3 — Classify response type
    if answer.startswith("OUT_OF_CONTEXT"):
        return {"type": "out_of_context", "answer": answer, "sources": []}
    if answer.startswith("NOT_FOUND") or not sources:
        return {"type": "not_found", "answer": answer, "sources": sources}

    return {"type": "answer", "answer": answer, "sources": sources}
