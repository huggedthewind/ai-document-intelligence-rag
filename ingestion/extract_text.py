from pathlib import Path
import json
from pypdf import PdfReader

PDF_PATH = Path("data/raw_documents/samk_student_guidance.pdf")
OUT_PATH = Path("data/processed/pages.json")

def extract_pages(pdf_path: Path):
    reader = PdfReader(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            {
                "page": i,
                "text": text.strip(),
                "source": pdf_path.name,
                "char_count": len(text),
            }
        )

    return pages

def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing PDF: {PDF_PATH}")

    pages = extract_pages(PDF_PATH)

    # basic sanity check prints
    total_chars = sum(p["char_count"] for p in pages)
    empty_pages = [p["page"] for p in pages if p["char_count"] == 0]

    print(f"Pages extracted: {len(pages)}")
    print(f"Total characters: {total_chars}")
    if empty_pages:
        print(f"Warning: empty text on pages: {empty_pages}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT_PATH}")

if __name__ == "__main__":
    main()
