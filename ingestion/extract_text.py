"""
Extract page-level text from all PDFs in data/raw_documents into a single JSON file.

Each output record is one page with:
- doc_id: identifier derived from the PDF filename (without extension)
- title: human-readable title (currently same as filename stem)
- page: 1-based page number within that PDF
- text: extracted text content
- source: original PDF filename
- char_count: length of the extracted text
"""

from pathlib import Path
import json

from pypdf import PdfReader

RAW_DIR = Path("data/raw_documents")
OUT_PATH = Path("data/processed/pages.json")


def extract_pages(pdf_path: Path, doc_id: str, title: str) -> list[dict]:
    """
    Extract text from each page of a single PDF.

    Args:
        pdf_path: Path to the PDF file.
        doc_id: Stable identifier for the document (e.g. filename without extension).
        title: Title for the document.

    Returns:
        A list of dictionaries, one per page, containing metadata and text.
    """
    reader = PdfReader(pdf_path)
    pages: list[dict] = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        pages.append(
            {
                "doc_id": doc_id,
                "title": title,
                "page": i,
                "text": text,
                "source": pdf_path.name,
                "char_count": len(text),
            }
        )

    return pages


def main() -> None:
    """
    Extract pages from all PDFs under RAW_DIR and write them to OUT_PATH.
    """
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Missing directory: {RAW_DIR}")

    all_pages: list[dict] = []

    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {RAW_DIR}")

    for pdf_path in pdf_files:
        doc_id = pdf_path.stem  # e.g. "samk_student_guidance"
        title = pdf_path.stem   # can be adjusted manually if needed

        print(f"Extracting from {pdf_path} (doc_id={doc_id})")
        pages = extract_pages(pdf_path, doc_id=doc_id, title=title)
        all_pages.extend(pages)

    total_chars = sum(p["char_count"] for p in all_pages)
    empty_pages = [
        (p["doc_id"], p["page"])
        for p in all_pages
        if p["char_count"] == 0
    ]

    print(f"Total pages extracted: {len(all_pages)} from {len(pdf_files)} PDF(s)")
    print(f"Total characters: {total_chars}")
    if empty_pages:
        print(f"Warning: empty text on pages: {empty_pages}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(all_pages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
