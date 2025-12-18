"""
Extract page-level text from a single PDF into a JSON file.

The output JSON is a list of records, one per page, with:
- page: 1-based page number
- text: extracted text content
- source: original PDF filename
- char_count: length of the extracted text
"""

from pathlib import Path
import json

from pypdf import PdfReader

PDF_PATH = Path("data/raw_documents/samk_student_guidance.pdf")
OUT_PATH = Path("data/processed/pages.json")


def extract_pages(pdf_path: Path) -> list[dict]:
    """
    Extract text from each page of a PDF.

    Args:
        pdf_path: Path to the input PDF file.

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
                "page": i,
                "text": text,
                "source": pdf_path.name,
                "char_count": len(text),
            }
        )

    return pages


def main() -> None:
    """
    Extract all pages from the configured PDF and write them to OUT_PATH.
    """
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing PDF: {PDF_PATH}")

    pages = extract_pages(PDF_PATH)

    total_chars = sum(p["char_count"] for p in pages)
    empty_pages = [p["page"] for p in pages if p["char_count"] == 0]

    print(f"Pages extracted: {len(pages)}")
    print(f"Total characters: {total_chars}")
    if empty_pages:
        print(f"Warning: empty text on pages: {empty_pages}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
