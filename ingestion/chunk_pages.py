import json
from pathlib import Path

IN_PATH = Path("data/processed/pages.json")
OUT_PATH = Path("data/processed/chunks.json")

CHUNK_SIZE = 1000
OVERLAP = 150
STEP = CHUNK_SIZE - OVERLAP


def chunk_text(text, page, source, start_chunk_id):
    """
    Split one page's text into overlapping chunks.
    Returns: (chunks_list, next_chunk_id)
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
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "source": source,
                    "page": page,
                    "text": chunk,
                    "char_start": start,
                    "char_end": min(end, n),
                }
            )
            chunk_id += 1

        # move forward with overlap
        start += STEP

    return chunks, chunk_id


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH}")

    pages = json.loads(IN_PATH.read_text(encoding="utf-8"))

    all_chunks = []
    next_chunk_id = 0

    for p in pages:
        page_num = p.get("page")
        source = p.get("source")
        text = p.get("text", "")

        page_chunks, next_chunk_id = chunk_text(
            text=text,
            page=page_num,
            source=source,
            start_chunk_id=next_chunk_id,
        )
        all_chunks.extend(page_chunks)

    # basic sanity prints
    total_chunks = len(all_chunks)
    avg_len = int(sum(len(c["text"]) for c in all_chunks) / total_chunks) if total_chunks else 0
    print(f"Pages read: {len(pages)}")
    print(f"Chunks created: {total_chunks}")
    print(f"Average chunk length (chars): {avg_len}")
    if total_chunks:
        print(f"First chunk: page {all_chunks[0]['page']} chars {all_chunks[0]['char_start']}–{all_chunks[0]['char_end']}")
        print(f"Last chunk:  page {all_chunks[-1]['page']} chars {all_chunks[-1]['char_start']}–{all_chunks[-1]['char_end']}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
