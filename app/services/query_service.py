from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMServiceFactory
from app.services.query_cache import get_cached_answer, set_cached_answer

class QueryService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm = LLMServiceFactory.get_service()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Source {i}]\n"
                f"Title: {chunk['title']}\n"
                f"Source Type: {chunk['source_type']}\n"
                f"URL: {chunk.get('source_url')}\n"
                f"Chunk Index: {chunk['chunk_index']}\n"
                f"Snippet: {chunk['content'][:500]}\n"
            )

        context = "\n\n".join(blocks)
        return (
            "Answer the question only using the context below.\n"
            "If the context does not support the answer, say you do not have enough evidence.\n"
            "Cite sources inline using [Source X].\n\n"
            "Be concise, factual, and avoid making up details.\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}\n"
        )

    def answer_question(self, question: str, top_k: int = 5):
        cached = get_cached_answer(question, top_k)
        if cached:
            cached["cached"] = True
            return cached

        retrieved = self.retrieval_service.retrieve(question=question, top_k=top_k)

        if not retrieved:
            result = {
                "answer": "I could not find enough evidence in the indexed documents.",
                "citations": [],
                "retrieved_chunks": 0,
                "cached": False,
            }
            set_cached_answer(question, top_k, result)
            return result

        prompt = self.build_prompt(question, retrieved)
        answer = self.llm.generate(prompt)

        citations = []
        for item in retrieved:
            citations.append({
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"],
                "title": item["title"],
                "source_type": item["source_type"],
                "source_url": item.get("source_url"),
                "chunk_index": item["chunk_index"],
                "snippet": item["content"][:200],
                "distance": item["distance"],
            })

        result = {
            "answer": answer,
            "citations": citations,
            "retrieved_chunks": len(retrieved),
            "cached": False,
        }
        set_cached_answer(question, top_k, result)
        return result