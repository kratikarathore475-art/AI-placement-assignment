from groq import Groq

from config import settings
from rag.retriever import retrieve_relevant_qa, format_context_for_llm

_groq_client = None


def get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


def build_prompt(query: str, context: str) -> str:
    return f"""You are an AI placement preparation assistant helping a computer science student prepare for job interviews. Use the context below to answer the student's question accurately and concisely. If the context doesn't fully cover the question, say so clearly and then answer using your general knowledge.

Context:
{context}

Student's question: {query}

Answer:"""


def ask_groq(prompt: str) -> str:
    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def get_answer(query: str, top_k: int = 4, topic_filter: str | None = None) -> dict:
    """
    Main entry point: retrieves relevant Q&A context, sends it to the LLM,
    and returns the generated answer along with its sources.
    """
    results = retrieve_relevant_qa(query, top_k=top_k, topic_filter=topic_filter)

    if not results:
        return {
            "answer": "Mujhe is topic ke liye relevant data nahi mila. Try rephrasing your question.",
            "sources": [],
        }

    context = format_context_for_llm(results)
    prompt = build_prompt(query, context)
    answer = ask_groq(prompt)

    return {
        "answer": answer,
        "sources": [
            {"topic": r["topic"], "question": r["question"], "score": round(r["score"], 3)}
            for r in results
        ],
    }


if __name__ == "__main__":
    result = get_answer("What is the difference between git merge and rebase?")
    print("ANSWER:\n", result["answer"])
    print("\nSOURCES:")
    for s in result["sources"]:
        print(f"  [{s['score']}] ({s['topic']}) {s['question']}")