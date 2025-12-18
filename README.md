# AI Document Intelligence – RAG over SAMK Guidance Handbook

An end-to-end Retrieval-Augmented Generation (RAG) system that answers questions about a single PDF:

> **“Student guidance and counselling at Satakunta University of Applied Sciences”**

The goal is to learn how real-world AI systems are built in practice:
- ingest documents,
- chunk them,
- build a vector index,
- retrieve relevant context,
- let an LLM generate grounded answers.

This is an applied AI / data engineering project, not a model training project.

---

## Features

- **PDF ingestion** → page-level JSON
- **Chunking** with overlap and word-boundary snapping
- **Semantic search** over chunks using sentence-transformers + Chroma
- **RAG-style Q&A** using OpenAI (`gpt-4.1-mini`)
- **Manual evaluation** of answer quality
- **FastAPI endpoint** (`POST /ask`) for programmatic access
- **Developer tools** to inspect raw retrieval results

---

## Architecture

### High-level flow

```mermaid
flowchart TD
    PDF["PDF: SAMK guidance handbook"]
    ET["extract_text.py<br/>PDF → pages.json"]
    CP["chunk_pages.py<br/>pages → chunks.json"]
    BI["build_index.py<br/>chunks → Chroma index"]
    DB["Chroma (rag-chunks)"]
    Q["User question"]
    AQ["answer_question.py<br/>/ app.api"]
    EMB["SentenceTransformer<br/>all-MiniLM-L6-v2"]
    CTX["Top-k chunks"]
    LLM["OpenAI gpt-4.1-mini"]
    A["Grounded answer"]

    PDF --> ET --> CP --> BI --> DB
    Q --> AQ --> EMB --> DB --> CTX --> LLM --> A
```
## Dataset

This project uses the publication: "Student Guidance and Counselling at Satakunta University of Applied Sciences" by Satakunta University of Applied Sciences.

The document is not included in this repository due to copyright restrictions. It can be downloaded for free from the Theseus repository and placed in:

data/raw_documents/

## Project Structure
```bash
ai-document-intelligence-rag/
├── app/
│   ├── __init__.py
│   ├── answer_question.py   # CLI RAG Q&A
│   └── api.py               # FastAPI app
│
├── data/
│   ├── raw_documents/       # PDF goes here (only local)
│   └── processed/
│       ├── pages.json       # output of extract_text.py
│       └── chunks.json      # output of chunk_pages.py
│
├── eval/
│   └── manual_eval.md       # manual evaluation notes
│
├── ingestion/
│   ├── extract_text.py      # PDF → pages.json
│   └── chunk_pages.py       # pages.json → chunks.json
│
├── vector_store/
│   ├── build_index.py       # chunks.json → Chroma index
│   └── retrieve.py          # debug: inspect top-k chunks
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

### 1. Clone and create a virtual environment
```bash
git clone <your-repo-url> ai-document-intelligence-rag
cd ai-document-intelligence-rag

python -m venv venv-ai-doc-intel
source venv-ai-doc-intel/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure API key

Create a .env file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Place the PDF

Download the SAMK guidance handbook PDF from Theseus and save it as:
```bash
data/raw_documents/samk_student_guidance.pdf
```

## Usage

### 1. Ingest the document
```bash
# Extract page-level text
python ingestion/extract_text.py

# Chunk pages into overlapping text windows
python ingestion/chunk_pages.py
```

This will produce:
- data/processed/pages.json
- data/processed/chunks.json

### 2. Build the vector index
```bash
python vector_store/build_index.py
```

This will:
- filter noisy chunks (references, ISBN/ISSN/DOI, URL-heavy, very short text),
- embed each remaining chunk with all-MiniLM-L6-v2,
- store embeddings + metadata in a persistent Chroma collection under vector_store/chroma.

### 3. Inspect raw retrieval (optional)
```bash
python vector_store/retrieve.py
```

You can type a question and see which chunks are retrieved, with:
- rank
- distance
- page number
- chunk text snippet

Useful for debugging retrieval quality.

### 4. Ask questions via CLI (RAG)
```bash
python app/answer_question.py "What is the objective of this handbook?"

#OR

python app/answer_question.py
# then type your question when prompted
```

This will:
- embed the question,
- retrieve top-k chunks from Chroma,
- build a prompt with page references,
- call OpenAI gpt-4.1-mini,
- and print a grounded answer.

### 5. Ask questions via FastAPI

Start the API server:
```bash
uvicorn app.api:app --reload
```

Then open the interactive docs:
- http://127.0.0.1:8000/docs

Example request (curl):
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is this publication intended for?", "top_k": 5}'
```

## Evaluation

Manual evaluation is recorded in:
```bash
eval/manual_eval.md
```

Examples:

- Question: “Who is this publication intended for?”
 Answer correctly identifies guidance / counselling staff at SAMK and students.

- Question: “What is the objective of this handbook?”
 Answer matches the stated aim: introduce the background of guidance and counselling, support and harmonise practices, and provide tools.

Some more open or abstract questions produce partial or generalized answers, which is expected for this first version.

## Limitations and Possible Future Work

- Only a single PDF is indexed.
- Chunking is character-based with overlap, not sentence- or paragraph-aware.
- No reranking step beyond basic vector similarity.
- Evaluation is manual and small-scale.

Possible future improvements:

- Sentence- or paragraph-aware chunking.
- Reranking of top-k chunks with a cross-encoder or LLM.
- Support for multiple documents and collections.
- Simple web UI on top of the FastAPI backend.
- More systematic evaluation with a larger question set.

## Tech Stack

- Language: Python 3.12
- Ingestion: pypdf
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Vector DB: chromadb (persistent, local)
- LLM: OpenAI gpt-4.1-mini
- API: FastAPI + Uvicorn
- Env: venv-ai-doc-intel