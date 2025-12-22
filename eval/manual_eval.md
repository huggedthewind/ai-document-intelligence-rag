# Manual Evaluation – SAMK Guidance Handbook RAG

## Setup

- Embedding model: `all-MiniLM-L6-v2` (sentence-transformers)
- Vector DB: Chroma (persistent local store)
- Answering: OpenAI `gpt-4.1-mini` via `app/answer_question.py`
- Chunking: paragraph-aware, max ~800 chars per chunk
- Scope:
  - Global (all docs) when `doc_id` is omitted
  - Single-document when `--doc-id` is provided


Docs in index:

- `samk_student_guidance` – Student guidance & counselling handbook
- `samk_admissions_2025` – Admissions criteria, Spring 2025
- `samk_erasmus_policy` – Erasmus+ policy / internationalisation

## 1. Guidance handbook – `samk_student_guidance`

### Q1
**Question**  
`Who is this publication intended for?`  
**Scope**  
`--doc-id samk_student_guidance`  

**Observed answer (summary)**  
- Says the publication is intended for SAMK students and guidance/counselling staff.  
- Mentions goal: support and harmonise SAMK’s guidance and counselling practices, provide tools.  
- References multiple pages (e.g. 6, 10, 11 or 28) in context.

**Verdict**: *good*  
**Notes**: Correct target audience and purpose, grounded in intro/conclusion. Doc scoping avoids mixing with admissions/Erasmus content.

---

### Q2
**Question**  
`What is the objective of this handbook?`  
**Scope**  
`--doc-id samk_student_guidance`  

**Observed answer (summary)**  
- States objective is to make the background of student guidance and counselling visible.  
- Mentions support + harmonisation of SAMK’s practices.  
- Adds that it aims to provide tools and improve equality, accessibility, sustainability, and student outcomes (e.g. drop-out, employability).  

**Verdict**: *good*  
**Notes**: Very close to the text, cites the right sections, no obvious hallucinations.

---

## 2. Admissions – `samk_admissions_2025`

### Q3
**Question**  
`What are the selection methods for the Data Engineering degree programme?`  
**Scope**  
`--doc-id samk_admissions_2025`  

**Observed answer (summary)**  
- Lists three selection methods:
  1. Certificate-based selection (matriculation / IB/EB/RP/DIA)  
  2. International UAS Exam  
  3. SAT test results  
- Mentions quotas (approx. 10% / 80% / 10%) and refers to application period and schedule.  

**Verdict**: *good*  
**Notes**: Matches admissions document structure. Scoping to `samk_admissions_2025` is critical here; without it, other docs could distract retrieval.

---

### Q4
**Question**  
`What does the UAS Exam assess?`  
**Scope**  
`--doc-id samk_admissions_2025`  

**Observed answer (summary)**  
- Describes the UAS Exam as a digital remote exam.  
- Mentions common sections: reasoning skills, English language skills.  
- Mentions possible field-specific sections (e.g. mathematical skills, advanced math, ethical skills, emotional intelligence).  

**Verdict**: *good*  
**Notes**: Well aligned with the UAS Exam section, good level of detail.

---

## 3. Erasmus+ policy – `samk_erasmus_policy`

### Q5
**Question**  
`How does SAMK use Erasmus+ to support internationalisation?`  
**Scope**  
`--doc-id samk_erasmus_policy`  

**Observed answer (summary)**  
- Explains Erasmus+ is used for student and staff mobility, international cooperation projects, and curriculum/RDI development.  
- Highlights aims: increase international competence, employability, strategic partnerships, and mobility numbers.  
- Refers to focus regions and targets (e.g. tripling international students, increasing mobility percentages).  

**Verdict**: *good*  
**Notes**: Very rich answer, strongly grounded in policy text. Shows that the system works on non-SAMK-guidance docs too.

---

### Q6
**Question**  
`What are SAMK’s goals for international student and staff mobility?`  
**Scope**  
`--doc-id samk_erasmus_policy`  

**Observed answer (summary)**  
- Mentions targets to increase the number of outgoing/exchange students and staff.  
- Refers to goals like tripling international student numbers and increasing student mobility and staff exchanges by specific percentages over the programme period.  

**Verdict**: *good*  
**Notes**: Matches strategic targets described in the policy.

---

## 4. Negative / out-of-scope test

### Q7
**Question**  
`What is the weather in Helsinki today?`  
**Scope**  
`--doc-id samk_student_guidance`  

**Observed answer (summary)**  
- States that this information is not available in the provided documents / cannot be answered from context.

**Verdict**: *good*  
**Notes**: Confirms that the prompt successfully prevents hallucinating answers unrelated to the documents.

---

## Overall impression (v2)

- Retrieval quality: **good** after:
  - doc-level scoping,
  - paragraph-based chunking,
  - basic noise filtering.
- Answers: **grounded**, with page references and correct doc attribution.
- Failure behaviour: sensible — for out-of-scope questions, the model now says it cannot find an answer in the documents.
