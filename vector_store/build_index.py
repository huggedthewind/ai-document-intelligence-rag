"""
Build a persistent Chroma vector index from precomputed text chunks.

Input:
    data/processed/chunks.json  (output of chunk_pages.py)

Output:
    A Chroma collection stored under vector_store/chroma containing:
    - ids: chunk_ids as strings
    - documents: chunk text
    - metadatas: page, source, chunk_id
    - embeddings: vector representations of each chunk
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/processed/chunks.json")
DB_DIR = "vector_store/chroma"
COLLECTION_NAME = "rag-chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks() -> list[dict]:
    """
    Load chunk records from disk.
    """
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks")
    return chunks


def is_noise(text: str) -> bool:
    """
    Heuristic filter to drop clearly non-content chunks such as
    references, ISBN/ISSN blocks, and very short fragments.
    """
    t = text.lower()

    if "isbn" in t or "issn" in t or "doi" in t or "urn:" in t:
        return True

    if "sources" in t[:50]:
        return True

    url_count = t.count("http://") + t.count("https://") + t.count("www.")
    if url_count >= 2:
        return True

    if len(text.strip()) < 150:
        return True

    return False


def main() -> None:
    """
    Build or rebuild the Chroma collection from filtered chunks.
    """
    chunks = load_chunks()

    filtered = [c for c in chunks if not is_noise(c["text"])]
    print(f"Kept {len(filtered)} chunks, removed {len(chunks) - len(filtered)} noisy chunks")

    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_DIR)

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [str(c["chunk_id"]) for c in filtered]
    texts = [c["text"] for c in filtered]
    metadatas = [
        {
            "page": c["page"],
            "source": c["source"],
            "chunk_id": c["chunk_id"],
        }
        for c in filtered
    ]

    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("After add, count =", collection.count())
    print(f"Indexed {len(filtered)} chunks into Chroma DB at '{DB_DIR}'")


if __name__ == "__main__":
    main()