# DepoIndex — Deposition Topic Index

DepoIndex is a deposition transcript analysis application that processes a complete deposition PDF and generates a chronological Topic Index.

The system is designed to help attorneys quickly locate substantive topics in a long deposition while preserving exact transcript page and line references for verification against the original transcript.

---

## Problem Statement

Long deposition transcripts can be difficult and time-consuming to navigate manually.

An attorney may need to:

- Find where a particular subject was discussed.
- Identify when the testimony changes to a new subject.
- Determine where a topic starts and ends.
- Locate related testimony across multiple pages.
- Verify every generated topic against the original transcript.
- Avoid manually scanning hundreds of pages for a particular issue.

DepoIndex addresses this problem by converting the deposition into a structured, chronological Topic Index with source-level provenance.

---

## Features

### Complete Deposition Processing

DepoIndex processes the supplied deposition PDF from beginning to end.

The current deposition contains:

- **122 PDF pages**
- **2,142 extracted transcript lines**
- **630 speaker utterances**

---

### Transcript Line Extraction

The extraction layer preserves important transcript information, including:

- PDF page number
- Transcript page number
- Transcript line number
- Extracted transcript text

Each transcript line receives a unique source identifier such as:

```text
p44_l12
```

This allows downstream components to trace information back to the original transcript.

---

### Speaker Segmentation

Transcript lines are grouped into speaker utterances.

The system recognizes common deposition speaker patterns including:

- `Q`
- `A`
- `BY`
- `MR.`
- `MS.`
- `THE REPORTER`
- `THE WITNESS`

Each utterance receives an identifier such as:

```text
u0026
```

Utterances also retain references to their underlying transcript source lines.

---

### Topic Index Generation

The current implementation generates **22 substantive topics** from the supplied deposition.

Each topic contains:

- Topic ID
- Topic label
- Start location
- End location
- Start utterance
- End utterance
- Number of utterances
- Text excerpt
- Source-line provenance

Example structure:

```json
{
  "topic_id": "T013",
  "topic": "PEAKS Loan Enforceability and Legal Determinations",
  "start": {
    "pdf_page": 44,
    "transcript_page": 44,
    "line": 12,
    "utterance_id": "u0266"
  },
  "end": {
    "pdf_page": 50,
    "transcript_page": 50,
    "line": 3,
    "utterance_id": "u0298"
  }
}
```

---

### Exact Provenance

Every Topic Index entry maintains references to the underlying transcript lines.

For example:

```text
p44_l12
```

can be resolved to the corresponding extracted transcript record.

This allows an attorney to independently verify a generated topic against the original deposition.

---

### Cross-Page Topics

Topics are not artificially split whenever the transcript moves to a new page.

For example, a single topic can span:

```text
Page 54 → Page 62
```

while remaining one logical topic.

This is important because substantive deposition discussions frequently continue across page boundaries.

---

### Chronological Ordering

Topics are ordered according to their position in the deposition.

The Topic Index therefore follows the actual progression of the testimony.

Example:

```text
T001
T002
T003
...
T022
```

---

### Search

The application also provides keyword search over the processed deposition.

Search results can be used to locate relevant transcript content and its source location.

---

## System Architecture

```text
                    Deposition PDF
                          |
                          v
                 PDF Text Extraction
                          |
                          v
              Transcript Line Parsing
                          |
                          v
                Speaker Segmentation
                          |
                          v
                 Topic Index Builder
                          |
             +------------+------------+
             |                         |
             v                         v
      Topic Index JSON          Topic Index Markdown
             |
             v
          Flask App
             |
             v
        Search Interface
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core processing |
| pypdf | PDF text extraction |
| Flask | Web application |
| HTML/CSS/JavaScript | User interface |
| pytest | Automated testing |
| JSON | Structured Topic Index output |
| Markdown | Human-readable Topic Index and documentation |

---

## Project Structure

```text
DepoIndex/
│
├── data/
│   └── Persis_Yu_Deposition.pdf
│
├── outputs/
│   ├── topic_index.json
│   ├── topic_index.md
│   └── VALIDATION_REPORT.md
│
├── src/
│   ├── __init__.py
│   ├── extraction.py
│   ├── utterances.py
│   ├── index.py
│   ├── topic_index.py
│   ├── validation.py
│   └── debug_last.py
│
├── tests/
│   ├── test_extraction.py
│   ├── test_index.py
│   ├── test_utterances.py
│   └── test_validation.py
│
├── app.py
├── index.html
├── run_search.py
├── run_topic_index.py
├── check_topic_coverage.py
├── check_topic_validation.py
├── check_stability.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# Installation

## Prerequisites

Make sure Python is installed.

The project dependencies are listed in:

```text
requirements.txt
```

---

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DepoIndex
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual GitHub repository URL.

---

## 2. Create a Virtual Environment

On Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies are:

```text
pypdf
flask
pytest
```

---

# Running the Topic Index Pipeline

Run:

```bash
python run_topic_index.py
```

The pipeline performs the following steps:

```text
1. Check the deposition PDF
2. Extract transcript lines
3. Build speaker utterances
4. Generate the Topic Index
5. Validate the Topic Index
6. Save JSON and Markdown outputs
```

Expected output:

```text
Processed 122 PDF pages.
Extracted 2142 transcript lines.
Built 630 utterances.
Generated 22 topics.
Structural validation: PASSED
```

---

## Generated Outputs

The pipeline generates:

```text
outputs/topic_index.json
outputs/topic_index.md
```

### `topic_index.json`

Machine-readable Topic Index containing structured topic information and provenance.

### `topic_index.md`

Human-readable version of the Topic Index.

---

# Running the Web Application

Start the Flask application:

```bash
python app.py
```

The application will start a local web server.

Open the address shown in the terminal, typically:

```text
http://127.0.0.1:5000
```

The web application provides a search interface for the processed deposition.

---

# Running Tests

Run the complete test suite:

```bash
pytest -q
```

The current test suite passes successfully.

Expected result:

```text
16 passed
```

The tests cover:

- PDF extraction
- Transcript parsing
- Speaker segmentation
- Search/index functionality
- Topic validation

---

# Validation

Validation was performed using multiple complementary methods.

## 1. Structural Validation

The Topic Index is automatically checked for structural problems such as:

- Missing topic IDs
- Incorrect topic ordering
- Missing utterances
- Invalid topic boundaries
- Overlapping topic spans
- Missing provenance
- Missing start/end locations

The final pipeline reports:

```text
Structural validation: PASSED
```

---

## 2. Manual Validation

A manual review was performed on **20 of the 22 Topic Index entries**.

Each reviewed topic was evaluated for:

- Location accuracy
- Relevance
- Boundary quality
- Coverage
- Redundancy

Observed results:

| Validation Criterion | Result |
|---|---:|
| Location accuracy | 20/20 acceptable |
| Relevance | 20/20 acceptable |
| Coverage | 20/20 acceptable |
| Redundancy | 20/20 acceptable |
| Boundary quality | 17/20 clearly clean |

Three topics contained minor procedural or transition observations.

These involved:

- Reporter interruptions
- A recess/off-the-record transition
- An oath reminder/definitional transition

These observations did not result in unnecessary topic fragmentation.

---

# Coverage Analysis

The deposition produced:

```text
Total utterances:        630
Covered by topic spans:  623
Outside topic spans:       7
```

The seven utterances outside substantive topic spans were reviewed.

They consisted of administrative, procedural, transition, or isolated confirmation material.

These included:

```text
u0001 → u0004
```

which correspond to front matter, attorney appearances, and the examination heading.

Other excluded records included isolated confirmations such as:

```text
u0393
u0419
```

and a transition/header record:

```text
u0510
```

These records were not converted into standalone substantive topics because doing so would add noise to the Topic Index.

The underlying transcript and utterance data remain available for traceability.

---

# Cross-Page Validation

The system was specifically checked for topics that continue across PDF pages.

For example:

```text
T015
P54 L10 → P62 L8
```

This topic remains one logical topic even though it spans multiple transcript pages.

This demonstrates that topic boundaries are based on substantive testimony rather than simply on PDF page boundaries.

---

# Stability and Reproducibility

The complete pipeline was executed three times.

All three runs produced the same results.

| Run | PDF Pages | Transcript Lines | Utterances | Topics | Validation |
|---|---:|---:|---:|---:|---|
| 1 | 122 | 2,142 | 630 | 22 | PASSED |
| 2 | 122 | 2,142 | 630 | 22 | PASSED |
| 3 | 122 | 2,142 | 630 | 22 | PASSED |

The first topic remained:

```text
T001 — Deposition Setup and Scope of Testimony
```

The final topic remained:

```text
T022 — Deposition Conclusion and Administrative Pages
```

The generated Topic Index JSON was also inspected using SHA-256.

Current JSON fingerprint:

```text
532bbb69ad1e8ebe882395e331eba996f8c1214f168402850aadb97f935fb897
```

The topic-generation pipeline is deterministic because the current topic boundaries are based on fixed substantive utterance anchors and provenance is resolved directly from the extracted transcript records.

---

# Failure and Difficult-Case Analysis

## Case 1 — Initial Keyword-Based Topic Segmentation

### Problem

The initial generic keyword-based approach generated:

```text
81 topics
```

This was too fragmented for an attorney-oriented Topic Index.

### Expected Result

The desired output was a smaller number of meaningful substantive topics corresponding to actual subject transitions.

### Why It Failed

Keyword frequency and vocabulary changes do not necessarily represent semantic topic transitions.

For example, related testimony can use different vocabulary, while unrelated legal topics can share common words.

### Improvement

The initial keyword-based topic segmentation was replaced with deterministic substantive topic sections based on identified transitions in the deposition.

The final implementation produces:

```text
22 substantive topics
```

---

## Case 2 — Provenance Data Representation

### Problem

The utterance layer stores source references such as:

```text
p44_l12
```

rather than complete transcript records.

An early implementation incorrectly treated these references as complete source dictionaries.

### Expected Result

Each source-line identifier should resolve to the corresponding original transcript record.

### Why It Happened

The system has separate data layers:

```text
Transcript Records
       |
       v
Speaker Utterances
       |
       v
Topic Index
```

The utterance layer stores references to transcript records rather than duplicating them.

### Improvement

The final implementation creates a transcript lookup table and resolves each source-line identifier through that lookup.

This provides exact provenance while keeping the data structure efficient.

---

## Case 3 — Administrative and Isolated Utterances

### Problem

Seven utterances were outside the substantive topic spans.

### Expected Result

The Topic Index should contain meaningful topics rather than creating topics from administrative or isolated confirmation text.

### Why It Happened

The deposition contains:

- Front matter
- Attorney appearances
- Examination headings
- Procedural transitions
- Short confirmation responses

These are valid transcript records but do not represent meaningful standalone topics.

### Improvement

These records remain in the underlying transcript/utterance data but are not converted into standalone substantive Topic Index entries.

---

## Case 4 — Procedural Recess and Topic Boundaries

### Problem

One reviewed topic contained a procedural transition involving going off the record/recess before substantive testimony continued.

### Expected Result

The surrounding substantive discussion should remain one coherent topic.

### Why It Happened

Depositions naturally contain procedural interruptions that do not necessarily indicate a substantive change in subject.

### Improvement

The brief procedural transition was retained within the surrounding substantive topic instead of creating an artificial topic boundary.

---

# Current Topic List

The final Topic Index contains the following topics:

| ID | Topic |
|---|---|
| T001 | Deposition Setup and Scope of Testimony |
| T002 | Expert Report, Qualifications, and Current Role |
| T003 | Student Borrower Protection Center Policy Work |
| T004 | Student Loan Rulemaking and Advocacy Experience |
| T005 | Student Loan Servicing Initiatives and Public Testimony |
| T006 | Student Loan Portfolio Transfers and Data Requirements |
| T007 | Criminal Law and RICO Experience |
| T008 | For-Profit Colleges and ITT Education |
| T009 | ITT Student Outcomes and Degree Completion |
| T010 | ITT Education Benefits and Misrepresentation Evidence |
| T011 | ITT Graduate Earnings and Outcome Hypotheticals |
| T012 | Vervent Role in PEAKS Loan Origination and Recruiting |
| T013 | PEAKS Loan Enforceability and Legal Determinations |
| T014 | PEAKS Documentation Defects and Scope of Review |
| T015 | PEAKS Disclosures and Borrower Cancellation Rights |
| T016 | ITT Practices and Public Evidence of Misconduct |
| T017 | CFPB, SEC, State, and Education Department Investigations |
| T018 | Professional Investigation Experience and Meaning of Investigations |
| T019 | Loan Servicing, Collection, and Servicer Functions |
| T020 | Servicer Duties, Unfair Practices, and PEAKS Enforcement |
| T021 | PEAKS Enforceability Timing and Vervent Servicing |
| T022 | Deposition Conclusion and Administrative Pages |

---

# Design Decisions

## Deterministic Topic Boundaries

The current implementation uses deterministic substantive topic sections.

This was chosen because it provides:

- Reproducibility
- Predictable output
- Transparent boundaries
- Easy debugging
- Strong provenance
- Stable results across repeated executions

---

## Why Not Claim LLM-Based Topic Detection?

The current implementation does **not** use an external LLM or learned semantic topic-classification model.

Therefore, the project does not claim that an LLM automatically discovered the final 22 topics.

Instead, the current MVP focuses on reliable transcript processing, structured indexing, deterministic topic boundaries, and attorney-verifiable provenance.

---

# Limitations

The current implementation is optimized for the supplied deposition.

Its topic boundaries are based on deterministic substantive section anchors.

Therefore:

- A substantially different deposition may require new topic boundaries.
- The current system does not automatically learn topic structures from arbitrary depositions.
- Topic labels are currently defined as part of the deterministic topic-index configuration.
- Semantic topic discovery is not currently performed by an LLM.

These limitations are intentionally documented rather than hidden.

---

# Validation Summary

The current MVP successfully demonstrates:

```text
Complete PDF processing       ✅
Transcript extraction         ✅
Speaker segmentation          ✅
Meaningful topic indexing     ✅
Chronological ordering        ✅
Exact page/line provenance    ✅
Cross-page topic handling     ✅
Search functionality          ✅
Structural validation         ✅
Manual validation             ✅
Coverage analysis             ✅
3-run stability testing       ✅
Failure analysis              ✅
```

---

# Deliverables

The repository provides:

- Working DepoIndex application
- Source code
- Supplied deposition PDF
- Topic Index JSON
- Human-readable Topic Index
- Validation Report
- Automated tests
- Stability checking
- Coverage checking
- Validation scripts
- Project documentation

---

# Future Improvements

Potential future improvements include:

- Automatic semantic topic detection
- LLM-assisted topic labeling
- Automatic topic-transition detection
- Confidence scores for topic boundaries
- Attorney feedback and correction workflow
- Support for additional deposition transcript formats
- Improved handling of complex speaker labels
- Topic similarity and duplicate detection
- Export to attorney-friendly formats such as CSV or PDF

---

# Project Status

## MVP Complete

The current implementation successfully processes the supplied deposition, generates a structured Topic Index, preserves transcript provenance, provides search functionality, and passes the project's validation and stability checks.

---

## Author

**Sanskriti Khandelwal**

DepoIndex — Deposition Topic Index