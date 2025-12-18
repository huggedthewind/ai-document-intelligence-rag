"""
Simple CLI for RAG-style question answering over the SAMK guidance handbook.

Pipeline:
- Embed the user's question with the same model used for indexing.
- Retrieve the top-k most relevant chunks from Chroma.
- Ask an LLM to answer using only those chunks as context.
"""

import argparse

import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

DB_DIR = "vector_store/chroma"
COLLECTION_NAME = "rag-chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


def get_relevant_chunks(question: str, k: int = 5) -> list[tuple[str, dict, float]]:
    """
    Retrieve the top-k most relevant chunks for a question from Chroma.

    Returns:
        A list of (document_text, metadata, distance) tuples.
    """
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    qvec = model.encode([question], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=qvec,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    return list(zip(docs, metas, dists))


def build_prompt(question: str, chunks: list[tuple[str, dict, float]]) -> str:
    """
    Build a single prompt string containing the question and retrieved context.
    """
    parts: list[str] = []
    for i, (doc, meta, _dist) in enumerate(chunks, start=1):
        parts.append(
            f"[Chunk {i} | page {meta.get('page')} | chunk_id {meta.get('chunk_id')}]\n"
            f"{doc}"
        )
    context = "\n\n".join(parts)

    prompt = f"""You are an assistant that answers questions about a single PDF publication
from Satakunta University of Applied Sciences.

Use only the information in the context below. If the answer is not clearly
stated there, say that you cannot find it in the document.

Question:
{question}

Context:
{context}

Answer clearly and concisely. If relevant, mention page numbers in parentheses.
"""

    return prompt


def answer_question(question: str, k: int = 5) -> str:
    """
    Run retrieval and generation to answer a question based on the document.
    """
    chunks = get_relevant_chunks(question, k=k)
    if not chunks:
        return "No relevant context found in the knowledge base."

    load_dotenv()
    client = OpenAI()

    prompt = build_prompt(question, chunks)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask questions about the SAMK guidance handbook using RAG."
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="Question to ask about the document (optional; will prompt if omitted).",
    )
    args = parser.parse_args()

    if args.question:
        question = " ".join(args.question).strip()
    else:
        question = input("Question: ").strip()

    if not question:
        print("No question provided.")
        return

    answer = answer_question(question)

    print("\n=== Answer ===\n")
    print(answer)


if __name__ == "__main__":
    main()