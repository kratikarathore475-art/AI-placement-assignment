from rag.vector_store import search


def retrieve_relevant_qa(query: str, top_k: int = 4, topic_filter: str | None = None) -> list[dict]:
    """
    Retrieve the most relevant Q&A pairs for a student's query.
    Optionally restrict results to a single topic (e.g. "DSA", "Machine_Learning").
    """
    if topic_filter:
        # Over-fetch since FAISS doesn't filter natively, then filter by topic
        raw_results = search(query, top_k=top_k * 5)
        filtered = [r for r in raw_results if r["topic"].lower() == topic_filter.lower()]
        return filtered[:top_k]

    return search(query, top_k=top_k)


def format_context_for_llm(results: list[dict]) -> str:
    """Format retrieved Q&A pairs into a context block for the LLM prompt."""
    if not results:
        return "No relevant context found."
    blocks = [f"Q: {r['question']}\nA: {r['answer']}" for r in results]
    return "\n\n".join(blocks)