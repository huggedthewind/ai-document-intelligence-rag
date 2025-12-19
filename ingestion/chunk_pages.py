"""
Split page-level text into overlapping chunks suitable for embeddings.

Input:
    data/processed/pages.json  (output of extract_text.py)

Output:
    data/processed/chunks.json

Each chunk record contains:
- doc_id: document identifier
- title: document title
- chunk_id: global running index across all documents and pages
- source: original PDF filename
- page: 1-based page number
- text: chunk content
- char_start / char_end: character offsets within the full page text
"""

import json
from pathlib import Path
from collections import Counter

IN_PATH = Path("data/processed/pages.json")
OUT_PATH = Path("data/processed/chunks.json")

CHUNK_SIZE = 600
OVERLAP = 150
STEP = CHUNK_SIZE - OVERLAP


def chunk_text(
    text: str,
    page: int,
    source: str,
    doc_id: str,
    title: str,
    start_chunk_id: int,
) -> tuple[list[dict], int]:
    """
    Split a single page's text into overlapping character-based chunks.

    Args:
        text: Page text to split.
        page: 1-based page number.
        source: Original PDF filename.
        start_chunk_id: Global chunk id to start from.

    Returns:
        A tuple of (chunks, next_chunk_id), where:
            - chunks is a list of chunk dicts
            - next_chunk_id is the next free id after the last chunk
    """
    text = (text or "").strip()
    if not text:
        return [], start_chunk_id

    chunks = []
    chunk_id = start_chunk_id

    start = 0
    n = len(text)

    while start < n:
        end = start + CHUNK_SIZE
        chunk_start = start
        raw = text[chunk_start:end]

        # avoid starting in the middle of a word
        if chunk_start != 0 and raw and raw[0].isalnum():
            shift = 0
            while shift < len(raw) and raw[shift].isalnum():
                shift += 1
            chunk_start = chunk_start + shift
            raw = text[chunk_start:end]

        chunk = raw.strip()

        if chunk:
            chunks.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_id": chunk_id,
                    "source": source,
                    "page": page,
                    "text": chunk,
                    "char_start": chunk_start,
                    "char_end": min(end, n),
                }
            )
            chunk_id += 1

        start += STEP

    return chunks, chunk_id


def main() -> None:
    """
    Read page-level JSON, chunk all pages, and write chunks to OUT_PATH.
    """
    pages = json.loads(IN_PATH.read_text(encoding="utf-8"))

    all_chunks = []
    next_chunk_id = 0

    for p in pages:
        page_chunks, next_chunk_id = chunk_text(
            text=p.get("text", ""),
            page=p.get("page"),
            source=p.get("source"),
            doc_id=p.get("doc_id"),
            title=p.get("title"),
            start_chunk_id=next_chunk_id,
        )
        all_chunks.extend(page_chunks)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # sanity prints
    print(f"Pages read: {len(pages)}")
    print(f"Chunks written: {len(all_chunks)}")

    by_doc = Counter(c["doc_id"] for c in all_chunks)
    for doc_id, count in by_doc.items():
        print(f"  - {doc_id}: {count} chunks")

    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()