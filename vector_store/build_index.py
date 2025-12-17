import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Paths
CHUNKS_PATH = Path("data/processed/chunks.json")
DB_DIR = "vector_store/chroma"

def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks")
    return chunks

def main():
    # Load text chunks
    chunks = load_chunks()

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create Chroma client with persistent storage
    client = chromadb.Client(Settings(persist_directory=DB_DIR))

    # Create or get collection
    collection = client.get_or_create_collection(name="rag-chunks")

    # Prepare data
    ids = [str(chunk["chunk_id"]) for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [{"page": chunk["page"], "source": chunk["source"]} for chunk in chunks]

    # Add to Chroma DB
    collection.add(documents=texts, metadatas=metadatas, ids=ids)

    print(f"Indexed {len(chunks)} chunks into Chroma DB at '{DB_DIR}'")

if __name__ == "__main__":
    main()
