# AI Document Intelligence – RAG over SAMK documents

A retrieval-augmented generation (RAG) project that answers questions about
PDF publications from Satakunta University of Applied Sciences (SAMK), with
page references. Documents, chunks, queries, answers and evaluation results
are stored in SQLite through SQLAlchemy 2, so the whole pipeline can be
inspected and evaluated with SQL queries.

It currently uses three documents:

| `doc_id`                | Document                                        |
|-------------------------|-------------------------------------------------|
| `samk_student_guidance` | Student guidance and counselling at SAMK        |
| `samk_admissions_2025`  | Admissions criteria, spring 2025                |
| `samk_erasmus_policy`   | Erasmus+ policy / internationalisation at SAMK  |

## What the project demonstrates

- Ingesting multiple PDFs: page-level text extraction and paragraph-aware chunking
- A relational model for a RAG system in SQLAlchemy 2, with Alembic migrations
- Semantic search with `all-MiniLM-L6-v2` embeddings stored in Chroma
- Grounded answering with `gpt-4.1-mini`, optionally restricted to one document
- Logging every query with its answer and ranked retrieved chunks
- Evaluating answer groundedness and chunk relevance with an LLM judge,
  with human corrections stored next to the judge's verdict
- Analysing the stored results with SQLAlchemy queries

## How the pipeline works

```
PDFs ─▶ extract_text ─▶ chunk_pages ─▶ load_to_db ─▶ SQLite (documents, chunks)
                                                        │
                                                   build_index
                                                        ▼
question ─▶ embed ─▶ Chroma top-k ─▶ gpt-4.1-mini ─▶ answer with page refs
                                                        │
                                  logged to SQLite (queries, answers, retrieved_chunks)
```

The chunk text and metadata live in SQLite. Chroma holds the embeddings, keyed
by the same `chunk_id`, so every retrieved chunk can be traced back to its
database row. Chunks that look like noise (reference lists, ISBN/DOI blocks,
URL-heavy or very short text) are left out of the index.

The answer prompt tells the model to use only the retrieved context and to say
it cannot find the answer when the context doesn't contain it.

## Database model

| Table              | Purpose                                                       |
|--------------------|---------------------------------------------------------------|
| `documents`        | One row per PDF (`doc_id`, `title`)                           |
| `chunks`           | Chunk text, page and character offsets; belongs to a document |
| `test_questions`   | Evaluation questions with reference answer and expected page  |
| `queries`          | Every question asked; linked to a test question when it is one |
| `answers`          | Generated answer for a query                                   |
| `retrieved_chunks` | Query ↔ chunk association with `rank`, `distance`, `relevant` |
| `evaluations`      | One per answer: judge `verdict`, `human_verdict`, notes, judge model |

`retrieved_chunks` is a many-to-many association object between `queries` and
`chunks`, with a composite primary key. The models are in `db/models.py`, and
the migration history is in `alembic/versions/`.

## Setup

Requires Python 3.12 and an OpenAI API key.

```bash
git clone <your-repo-url> ai-document-intelligence-rag
cd ai-document-intelligence-rag

python -m venv venv-ai-doc-intel
source venv-ai-doc-intel/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then set OPENAI_API_KEY
mkdir -p data/raw_documents # data/ is not committed
alembic upgrade head        # creates data/samk_rag.db
```

`.env` settings:

- `OPENAI_API_KEY`: required
- `DATABASE_URL`: defaults to `sqlite:///data/samk_rag.db`
- `JUDGE_MODEL`: optional, the model used by the evaluation judges (defaults to `gpt-4.1-mini`)

`sentence-transformers` installs PyTorch. On a machine without a GPU, you can
install the CPU-only PyTorch build first to keep the download smaller.

### Add the PDFs

The PDFs are not included because of copyright. Download them from
[Theseus](https://www.theseus.fi/) or SAMK and save them in
`data/raw_documents/`. Each file name, without `.pdf`, becomes the document's
`doc_id`, so use these names to match `--doc-id` and the test questions:

```
data/raw_documents/samk_student_guidance.pdf
data/raw_documents/samk_admissions_2025.pdf
data/raw_documents/samk_erasmus_policy.pdf
```

Any other PDFs in that folder are ingested as well.

## Ingestion and index building

Run every command from the project root. Scripts that import the `db` package
are run with `python -m`.

```bash
python ingestion/extract_text.py     # PDFs → data/processed/pages.json
python ingestion/chunk_pages.py      # pages → data/processed/chunks.json (≤ ~800 chars, paragraph-aware)
python -m ingestion.load_to_db       # chunks.json → documents + chunks tables
python -m vector_store.build_index   # database chunks → Chroma (vector_store/chroma/)
```

`load_to_db` skips documents that are already in the database.
`build_index` deletes and rebuilds the Chroma collection on every run.

## Asking questions

CLI:

```bash
python app/answer_question.py "What does the UAS Exam assess?"
python app/answer_question.py "What does the UAS Exam assess?" --doc-id samk_admissions_2025
```

API:

```bash
uvicorn app.api:app --reload
```

Interactive docs are at http://127.0.0.1:8000/docs. Example `POST /ask` body
(`top_k` and `doc_id` are optional):

```json
{ "question": "How does SAMK use Erasmus+ to support internationalisation?", "top_k": 5, "doc_id": "samk_erasmus_policy" }
```

Each API request is stored as a query with its answer and retrieved chunks.
The CLI only prints the answer.

To debug retrieval without calling the LLM, `python vector_store/retrieve.py`
prompts for a question and prints the raw top-5 chunks with their distances.
It is an optional diagnostic and isn't part of the answering or evaluation
workflow.

## Evaluation workflow

The 25 test questions in `eval/test_questions.json` cover all three documents
(21 questions), plus 4 out-of-scope questions that the system should refuse.

```bash
python -m eval.load_test_questions        # JSON → test_questions (skips existing questions)
python -m eval.run_test_questions         # answer each test question; store query, answer, retrieved chunks
python -m eval.run_evaluations            # LLM judge: is each new answer grounded in its chunks? (yes/partial/no)
python -m eval.run_retrieval_evaluations  # LLM judge: is each new retrieved chunk relevant?
python -m eval.set_human_verdict <answer_id> <yes|partial|no>   # record a human correction
python -m eval.analyze_results            # summary report
```

- Test questions are answered across all documents with `top_k = 5`.
- The two judge scripts only process rows that have not been evaluated yet,
  so they are safe to re-run. `run_test_questions` adds a new set of queries
  every time it runs.
- A human verdict doesn't overwrite the judge's verdict. Both are stored, and
  the report uses the human verdict when there is one.
- The judges get the retrieved chunks as their only evidence and return
  structured output (Pydantic models via the OpenAI Responses API).

## Current results

Output of `python -m eval.analyze_results` on the current database:

| Measure                                    | Result                         |
|--------------------------------------------|--------------------------------|
| Test questions stored                      | 25                             |
| Executed / answered / evaluated            | 25 / 25 / 25                   |
| Final answer verdicts (after human review) | 25 yes · 0 partial · 0 no      |
| Retrieved chunks judged relevant           | 55 of 125 (70 irrelevant)      |

The answer verdicts include human corrections. The judge marked 3 answers as
`no` that were judged grounded on review and changed to `yes`; the other 22
judge verdicts were left as they were. The chunk relevance numbers come only
from the LLM judge and have not been reviewed by a human. Each of the 21
in-scope questions had at least one relevant chunk in its top five. The 4
out-of-scope questions had none, as expected, and account for 20 of the 70
irrelevant chunks.

## Limitations

- **SQLite** keeps the project easy to clone and run in a classroom. It is
  not set up for concurrent writes.
- **Chroma is a separate store.** It is rebuilt from the database, but the two
  are not synchronised automatically.
- **One model for generation and judging.** `gpt-4.1-mini` does both so setup
  needs only one API key. A model judging its own kind of output can share the
  same blind spots. `JUDGE_MODEL` can point the judges elsewhere.
- **LLM-as-judge is not ground truth.** Its verdicts can disagree with human
  review, as the 3 corrections above show.
- **Prompt injection.** Retrieved documents can contain instruction-like text.
  The judge prompts tell the model to treat chunk text as content, but this is
  a known RAG weakness, not a solved problem.
- **Small, project-specific dataset.** 25 questions over three documents is
  enough to compare changes to this system, but too few to support general
  conclusions.
- No reranking beyond vector similarity, and no web UI.

## Repository structure

```
alembic/            migrations (alembic/versions/)
app/                answer_question.py (CLI, main entry point), api.py (FastAPI)
db/                 SQLAlchemy base, models, session
eval/               test questions, judges, evaluation runners, analysis report
ingestion/          extract_text.py → chunk_pages.py → load_to_db.py
vector_store/       build_index.py, retrieve.py (optional retrieval debugging)
docs/archive/       historical MVP evaluation
data/               local PDFs, processed JSON, SQLite database (not committed)
```

## Project history

The project started as a single-PDF RAG with fixed-size chunks. It then moved
to multiple documents, paragraph-aware chunking, document-scoped retrieval and
a FastAPI endpoint, which were checked by hand. That manual check is kept as
the historical MVP baseline in
[`docs/archive/manual-evaluation-baseline.md`](docs/archive/manual-evaluation-baseline.md).
It was later replaced by the database-backed evaluation described above.

## Tech stack

Python 3.12 · pypdf · sentence-transformers (`all-MiniLM-L6-v2`) · Chroma ·
OpenAI `gpt-4.1-mini` · SQLAlchemy 2 · Alembic · SQLite · FastAPI + Uvicorn
