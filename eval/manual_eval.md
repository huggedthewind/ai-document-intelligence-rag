# Manual Evaluation – SAMK Guidance Handbook RAG

## Setup

- Embedding model: `all-MiniLM-L6-v2` (sentence-transformers)
- Vector DB: Chroma (persistent local store)
- Answering: OpenAI `gpt-4.1-mini` via `app/answer_question.py`
- Corpus: Single PDF – student guidance and counselling at SAMK

## Questions and Verdicts

- **Question #1**  
  *Who is this publication intended for?*  
  **Verdict:** good  
  **Note:** Mentions guidance/counselling staff at SAMK and students; aligned with the introduction.

- **Question #2**  
  *What is the objective of this handbook?*  
  **Verdict:** good  
  **Note:** Matches the stated aim: background of guidance and counselling, harmonisation of practices, and tools for guidance work.

- **Question #3**  
  *How is student agency described in the handbook?*  
  **Verdict:** acceptable  
  **Note:** Captures the active role and long-term choices, but misses some nuance from the full text.

- **Question #4**  
  *What kind of support is offered at the beginning of studies?*  
  **Verdict:** good  
  **Note:** Describes orientation and early guidance practices in a way that fits the document.

- **Question #5**  
  *What limitations or gaps are not clearly covered?*  
  **Verdict:** acceptable  
  **Note:** Model sometimes generalises; some details are not explicitly tied to page numbers or specific sections.
