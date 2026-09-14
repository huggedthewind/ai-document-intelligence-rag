"""
Load chunks and their parent documents into the database.

Input:
    data/processed/chunks.json  (output of chunk_pages.py)

Output:
    Document and Chunk rows inserted into the database via SQLAlchemy. If a document already present in the database it is skipped.
"""

import json
from pathlib import Path
from db.session import SessionLocal
from db.models import Document, Chunk

IN_PATH = Path("data/processed/chunks.json")


def main() -> None:
    chunks = json.loads(IN_PATH.read_text(encoding="utf-8"))

    documents = {}

    for chunk in chunks:
        documents[chunk["doc_id"]] = chunk["title"]

    session = SessionLocal()
    new_doc_ids = set()

    new_doc_count = 0
    skipped_doc_count = 0

    for doc_id, title in documents.items():
        existing = session.get(Document, doc_id)

        if existing is None:
            new_doc = Document(doc_id=doc_id, title=title)
            session.add(new_doc)
            new_doc_ids.add(new_doc.doc_id)
            new_doc_count += 1
        else:
            skipped_doc_count += 1

    session.commit()
    session.close()

    session = SessionLocal()

    new_chunk_count = 0
    skipped_chunk_count = 0

    for chunk in chunks:
        if chunk["doc_id"] in new_doc_ids:
            new_chunk = Chunk(doc_id=chunk["doc_id"], page=chunk["page"], text=chunk["text"], char_start=chunk["char_start"], char_end=chunk["char_end"])
            session.add(new_chunk)
            new_chunk_count += 1
        else:
            skipped_chunk_count += 1

    session.commit()
    session.close()
    print(f"Documents inserted: {new_doc_count}")
    print(f"Documents skipped (already existed): {skipped_doc_count}")
    print(f"Chunks inserted: {new_chunk_count}")
    print(f"Chunks skipped (parent document already existed): {skipped_chunk_count}")

if __name__ == "__main__":
    main()