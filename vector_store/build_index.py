"""
Build a persistent Chroma vector index from precomputed text chunks.

Input:
    All chunk records from the database

Output:
    A Chroma collection stored under vector_store/chroma containing:
    - ids: chunk_ids as strings
    - documents: chunk text
    - metadatas: doc_id, page, chunk_id, char_start, char_end
    - embeddings: vector representations of each chunk
"""

import chromadb
from sentence_transformers import SentenceTransformer
from db.session import SessionLocal
from sqlalchemy import select
from db.models import Chunk

DB_DIR = "vector_store/chroma"
COLLECTION_NAME = "rag-chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(session) -> list[Chunk]:
    """
    Load all chunk records from the database using the given session.
    """
    
    result = session.execute(select(Chunk)) 
    chunks = result.scalars().all()

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
    session = SessionLocal()

    chunks = load_chunks(session)

    filtered = [chunk for chunk in chunks if not is_noise(chunk.text)]
    print(f"Kept {len(filtered)} chunks, removed {len(chunks) - len(filtered)} noisy chunks")

    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_DIR)

    existing = [coll.name for coll in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [str(chunk.chunk_id) for chunk in filtered]
    texts = [chunk.text for chunk in filtered]
    metadatas = [
        {
            "doc_id": chunk.doc_id,
            "page": chunk.page,
            "chunk_id": chunk.chunk_id,
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
        }
        for chunk in filtered
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
    
    session.close()


if __name__ == "__main__":
    main()