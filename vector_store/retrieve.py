"""
Developer-facing helper script to inspect raw retrieval results from Chroma.

Given a natural-language question, this script:
- encodes the question with the same embedding model used for indexing
- queries the persisted Chroma collection
- prints the top-k chunks with basic metadata and distances

Useful for debugging retrieval quality before or alongside RAG answering.
"""

import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "vector_store/chroma"
COLLECTION_NAME = "rag-chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


def main() -> None:
    question = input("Question: ").strip()
    if not question:
        print("Empty question. Bye.")
        return

    model = SentenceTransformer(MODEL_NAME)
    qvec = model.encode([question], normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(path=DB_DIR)
    print("Collections:", [c.name for c in client.list_collections()])
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    print("Count:", collection.count())

    results = collection.query(
        query_embeddings=qvec,
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    print("Docs returned:", len(docs))

    for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
        page = meta.get("page")
        source = meta.get("source")
        chunk_id = meta.get("chunk_id", "unknown")

        print("\n" + "-" * 60)
        print(
            f"Rank {rank} | distance={dist:.4f} | "
            f"chunk_id={chunk_id} | page={page} | source={source}"
        )
        snippet = doc.replace("\n", " ")
        if len(snippet) > 400:
            snippet = snippet[:400] + "..."
        print(snippet)


if __name__ == "__main__":
    main()