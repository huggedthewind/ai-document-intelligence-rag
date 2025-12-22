"""
Split page-level text into paragraph-aware chunks suitable for embeddings.

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
- text: chunk content (one or more paragraphs)
- char_start / char_end: character offsets within the full page text
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

IN_PATH = Path("data/processed/pages.json")
OUT_PATH = Path("data/processed/chunks.json")

MAX_CHARS_PER_CHUNK = 800

def split_paragraphs(text: str) -> List[Tuple[str, int, int]]:
    """
    Split page text into paragraphs separated by blank lines.

    Returns a list of (paragraph_text, start_index, end_index) in the original text.
    """
    text = text or ""
    text = text.replace("\r\n", "\n")

    # Match blocks of text separated by one or more blank lines
    pattern = re.compile(r"(.*?)(?:\n\s*\n|$)", re.DOTALL)
    paragraphs: List[Tuple[str, int, int]] = []

    for match in pattern.finditer(text):
        paragraph = match.group(1)
        if not paragraph:
            continue
        paragraph_stripped = paragraph.strip()
        if not paragraph_stripped:
            continue

        start = match.start(1)
        end = match.end(1)
        paragraphs.append((paragraph_stripped, start, end))

    return paragraphs


def chunk_page(
    text: str,
    page: int,
    source: str,
    doc_id: str,
    title: str,
    start_chunk_id: int,
) -> tuple[list[dict], int]:
    """
    Build chunks from a single page by grouping paragraphs
    until MAX_CHARS_PER_CHUNK is reached.
    """
    paragraphs = split_paragraphs(text)
    if not paragraphs:
        return [], start_chunk_id
    
    text = (text or "").strip()
    if not text:
        return [], start_chunk_id

    chunks = []
    chunk_id = start_chunk_id

    current_text_parts: List[str] = []
    current_start: int | None = None
    current_end: int | None = None

    def flush_current():
        nonlocal chunk_id, current_text_parts, current_start, current_end

        if not current_text_parts or current_start is None or current_end is None:
            return

        chunk_text = "\n\n".join(current_text_parts).strip()
        if not chunk_text:
            return
        
        chunks.append(
            {
                "doc_id": doc_id,
                "title": title,
                "chunk_id": chunk_id,
                "source": source,
                "page": page,
                "text": chunk_text,
                "char_start": current_start,
                "char_end": current_end,
            }
        )
        chunk_id += 1

        current_text_parts = []
        current_start = None
        current_end = None

    for para_text, para_start, para_end in paragraphs:
        if not current_text_parts:
            # start a new chunk
            current_text_parts = [para_text]
            current_start = para_start
            current_end = para_end
            continue

        # if adding this paragraph would exceed max size -> flush current chunk
        projected_length = len("\n\n".join(current_text_parts)) + 2 + len(para_text)
        if projected_length > MAX_CHARS_PER_CHUNK:
            flush_current()
            # start a new chunk with this paragraph
            current_text_parts = [para_text]
            current_start = para_start
            current_end = para_end
        else:
            # append paragraph to current chunk
            current_text_parts.append(para_text)
            current_end = para_end

    # flush any remaining text
    flush_current()

    return chunks, chunk_id


def main() -> None:
    """
    Read page-level JSON, chunk all pages, and write chunks to OUT_PATH.
    """
    pages = json.loads(IN_PATH.read_text(encoding="utf-8"))

    all_chunks = []
    next_chunk_id = 0

    for p in pages:
        page_chunks, next_chunk_id = chunk_page(
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