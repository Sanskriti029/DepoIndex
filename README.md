# DepoIndex

## AI-Powered Deposition Topic Index

**Find the topic. Verify the source.**

DepoIndex is a provenance-first system for organizing long deposition transcripts into a chronological, searchable Topic Index.

The current MVP processes the supplied deposition PDF into structured utterances, identifies substantive topic sections, preserves exact transcript page/line references, and provides an interactive web interface for searching and source verification.

> **Current MVP note:** Topic discovery is deterministic. No LLM is currently used to generate the Topic Index.

---

## 1. Problem

Long deposition transcripts are difficult to navigate manually.

A useful deposition Topic Index must do more than summarize the transcript. It should:

* identify meaningful subject-matter topics
* detect meaningful topic transitions
* determine where topics start and end
* preserve exact transcript page and line references
* handle topics that continue across pages
* avoid turning short interruptions or confirmations into unnecessary topics
* identify topics that reappear later
* maintain chronological ordering
* allow every generated entry to be independently verified against the original transcript

The key requirement is **verifiable provenance**.

---

## 2. Solution

DepoIndex converts the supplied deposition into a structured, attorney-facing Topic Index.

The current MVP:

1. extracts transcript text from the PDF
2. parses transcript page and line numbers
3. groups transcript lines into speaker-aware utterances
4. organizes substantive testimony into 22 topic sections
5. preserves exact page/line and source-line provenance
6. identifies selected recurring-topic relationships
7. generates JSON and human-readable Topic Index outputs
8. provides search and source-verification functionality through a Flask web application
9. validates the generated index
10. tests reproducibility across three complete pipeline runs

---

## 3. Key Features

### Topic Index

The system generates a chronological index containing:

* Topic ID
* Topic name
* Start page and line
* End page and line
* Start/end utterance IDs
* Utterance count
* Topic excerpt
* Source-line provenance
* Related/re-entry topics where applicable

### Provenance

Every topic retains the underlying transcript source-line IDs.

This allows a user to move from:

```text
Topic
  ↓
Page / Line
  ↓
Utterance
  ↓
Original transcript source lines
```

The system does not rely on LLM-generated page or line numbers.

### Search

The web application provides keyword-based deposition search.

Users can search terms such as:

```text
loan
ITT
PEAKS
servicing
investigation
```

### Source Verification

Each Topic Index entry provides a **View Source** action that displays the corresponding transcript utterances and their page/line information.

### Cross-Page Topics

Topics can span multiple transcript pages while retaining their exact start and end locations.

### Topic Re-entry

When a previously discussed subject returns later in the deposition, the Topic Index can represent the later discussion chronologically while maintaining a relationship to the earlier topic.

### Reproducibility

The complete pipeline is deterministic and produces identical results across repeated runs.

---

## 4. Architecture

```text
                Deposition PDF
                      |
                      v
              PDF Text Extraction
                    pypdf
                      |
                      v
            Transcript Line Parsing
                      |
                      v
             Utterance Segmentation
                      |
                      v
           Deterministic Topic Index
                      |
              +-------+-------+
              |               |
              v               v
        Provenance        Validation
        Generation        & Testing
              |               |
              +-------+-------+
                      |
                      v
             JSON + Markdown Output
                      |
                      v
                Flask Web App
                /       \
               /         \
           Search     Source Verify
```

### Main components

| Component        | Purpose                                               |
| ---------------- | ----------------------------------------------------- |
| `extraction.py`  | Extract PDF text and transcript page/line information |
| `utterances.py`  | Create speaker-aware utterances                       |
| `index.py`       | Keyword-based deposition search                       |
| `topic_index.py` | Generate and validate the Topic Index                 |
| `validation.py`  | Validation utilities                                  |
| `app.py`         | Flask web application                                 |
| `index.html`     | DepoIndex user interface                              |

---

## 5. Project Structure

```text
DepoIndex/
│
├── app.py
├── index.html
├── requirements.txt
├── README.md
├── llm_usage.md
├── .python-version
├── pytest.ini
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
│   ├── test_utterances.py
│   ├── test_index.py
│   └── test_validation.py
│
├── run_search.py
├── run_topic_index.py
├── check_topic_coverage.py
├── check_topic_validation.py
└── check_stability.py
```

---

## 6. Technology Stack

### Backend

* Python
* Flask
* pypdf

### Search

* Deterministic keyword-based inverted index

### Frontend

* HTML
* CSS
* JavaScript

### Testing

* pytest
* deterministic pipeline checks
* manual validation

### Deployment

* Gunicorn
* Render

---

## 7. Installation

### Requirements

Python 3.13.5 is the intended project version.

Install the dependencies:

```bash
pip install -r requirements.txt
```

The requirements include:

```text
pypdf
flask
pytest
gunicorn
```

---

## 8. Run the Topic Index Pipeline

From the project root:

```bash
python run_topic_index.py
```

This processes the deposition and generates:

```text
outputs/topic_index.json
outputs/topic_index.md
```

The current supplied deposition produces:

```text
PDF pages        : 122
Transcript lines : 2142
Utterances       : 630
Topics           : 22
```

---

## 9. Run Validation

Run the structural and validation checks:

```bash
python check_topic_validation.py
```

Coverage can be checked with:

```bash
python check_topic_coverage.py
```

Stability can be tested with:

```bash
python check_stability.py
```

---

## 10. Run Tests

Run the automated test suite:

```bash
pytest -q
```

The current test suite contains tests for:

* PDF extraction
* transcript parsing
* utterance segmentation
* search indexing
* validation

---

## 11. Run the Web Application

Start the Flask application locally:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The application provides:

* Topic Index browsing
* deposition search
* source verification
* topic-specific transcript evidence

---

## 12. Live Demo

### DepoIndex

**Live application:**

https://depoindex-asc7.onrender.com/

The deployed application provides the same Topic Index and source-verification workflow through the browser.

---

## 13. Generated Outputs

### `topic_index.json`

Machine-readable Topic Index containing:

* topic IDs
* topic labels
* page/line boundaries
* utterance IDs
* excerpts
* provenance
* related-topic information

### `topic_index.md`

Human-readable version of the Topic Index.

### `VALIDATION_REPORT.md`

Contains the validation methodology, manual review results, coverage analysis, difficult cases, limitations, and reproducibility results.

---

## 14. Validation

The Topic Index was manually reviewed across 20 entries.

| Criterion                   |              Result |
| --------------------------- | ------------------: |
| Location accuracy           |               20/20 |
| Topic relevance             |               20/20 |
| Coverage of reviewed topics |               20/20 |
| Redundancy                  |               20/20 |
| Boundary quality            | 17/20 clearly clean |

The three boundary observations involved minor transition material such as reporter interruptions, a recess/off-record transition, and an oath/definition transition.

These observations did not invalidate the corresponding substantive topic organization.

---

## 15. Coverage

The complete deposition contains:

```text
630 utterances
```

The Topic Index covers:

```text
623 utterances
```

Seven utterances remain outside substantive topic spans.

These consist of legitimate administrative or transition material, including:

* index/appearance/deposition heading material
* isolated confirmation responses
* attorney/header transition material

They were not treated as substantive topic omissions.

---

## 16. Stability and Reproducibility

The complete pipeline was executed three times.

### Results

```text
RUN 1
Topics           : 22

RUN 2
Topics           : 22

RUN 3
Topics           : 22
```

All three runs produced identical:

* topic IDs
* topic labels
* boundaries
* relationships
* provenance
* page references
* line references
* utterance references
* canonical SHA256 hash

### Stability Result

```text
PASS
```

The deterministic design provides a reproducible baseline for future semantic or LLM-based improvements.

---

## 17. Topic Granularity

DepoIndex intentionally uses **substantive-topic granularity**.

A new primary topic is created when the deposition moves into a materially different subject area.

The system does not create a new primary topic for:

* every question
* every answer
* short confirmations
* reporter interruptions
* procedural statements
* brief digressions

This avoids excessive fragmentation and produces a more useful attorney-facing index.

The current MVP contains:

```text
22 substantive topics
```

An earlier generic keyword-based approach produced substantially more fragmented sections. The substantive-topic approach was selected because the objective is not to maximize topic count, but to produce meaningful sections that can be quickly scanned and independently verified.

---

## 18. Topic Re-entry

Some subjects return later in the deposition.

The current MVP explicitly represents selected high-confidence relationships such as:

```text
Student Loan Servicing
        ↓
Later Servicing / Collection Discussion
```

```text
ITT Education Practices
        ↓
Later ITT Misconduct Discussion
```

```text
PEAKS / Vervent
        ↓
Later PEAKS Enforcement / Servicing Discussion
```

The later topic remains in its chronological position while the relationship identifies the recurring subject.

---

## 19. Difficult Cases and Failure Analysis

The project evaluates difficult cases including:

### Administrative Material

Deposition headings, appearances, and administrative text should not become substantive topics.

### Short Confirmations

Responses such as:

```text
"Yep."
"Yes."
```

should not create standalone topics.

### Topic Re-entry

A subject can disappear for many pages and return later.

The later discussion should remain chronologically positioned while still being identifiable as related to the earlier subject.

### Current Approach

The MVP handles these cases conservatively using deterministic rules and explicit relationships.

A future semantic layer could improve automatic detection.

---

## 20. LLM Usage

The current MVP **does not use an LLM in the production topic-generation pipeline**.

This is intentional.

The current system prioritizes:

* provenance
* deterministic behavior
* reproducibility
* transparent validation
* exact source references

A future hybrid architecture could use an LLM for:

* semantic topic discovery
* topic-label suggestions
* transition detection
* digression detection
* recurring-topic detection
* boundary proposals

However, deterministic code should remain responsible for:

* validating utterance IDs
* deriving page/line references
* verifying chronology
* checking provenance
* validating boundaries
* generating the final evidence-backed Topic Index

See:

```text
llm_usage.md
```

for the detailed LLM integration plan.

---

## 21. Limitations

The current MVP has several limitations.

### Deterministic Topic Discovery

Topic sections and labels are currently defined for the supplied deposition rather than automatically inferred using semantic models.

### Boundary Detection

Topic boundaries are not yet automatically discovered from semantic transitions.

### Re-entry Detection

Recurring-topic relationships are currently conservative and deterministic rather than learned.

### Generalization

Validation was performed on the supplied deposition rather than a large benchmark containing hundreds of depositions.

### Production Infrastructure

The Flask application is currently a demonstration interface rather than a complete enterprise-scale legal processing platform.

---

## 22. Future Improvements

Potential improvements include:

* semantic topic detection
* LLM-assisted topic discovery
* automatic topic-transition detection
* improved boundary detection
* automatic digression classification
* semantic recurring-topic detection
* persistent storage
* deposition IDs
* authentication
* background processing
* batch processing
* logging
* monitoring
* automated validation dashboards
* large-scale multi-deposition evaluation

---

## 23. Scaling

For hundreds of depositions, individual deposition jobs can be processed independently.

A production architecture could introduce:

```text
Upload
   ↓
Job Queue
   ↓
Deposition Processing
   ↓
Topic Detection
   ↓
Provenance Validation
   ↓
Persistent Storage
   ↓
Search / Review Interface
```

Jobs could be processed independently and, where infrastructure permits, in parallel.

The deterministic MVP provides a reproducible baseline against which future semantic or LLM-based systems can be evaluated.

---

## 24. Design Principle

The central design principle of DepoIndex is:

> **Use AI for understanding. Use deterministic code for evidence.**

Semantic models can eventually help understand complex deposition content, but the final evidence references should always be derived from the original transcript.

This separation is important for an attorney-facing system where source verification matters.

---

## 25. Project Status

### MVP Status: COMPLETE ✅

Current implementation demonstrates:

* ✅ supplied-PDF processing
* ✅ substantive topic organization
* ✅ chronological Topic Index
* ✅ exact page/line references
* ✅ cross-page topic handling
* ✅ recurring-topic relationships
* ✅ provenance preservation
* ✅ search
* ✅ source verification
* ✅ manual validation
* ✅ coverage analysis
* ✅ difficult-case analysis
* ✅ three-run reproducibility testing
* ✅ automated tests
* ✅ deployed web application

---

## 26. Submission Deliverables

The project submission includes:

```text
GitHub Repository
        +
Live Demo
        +
Topic Index JSON
        +
Topic Index Markdown
        +
Validation Report
        +
Presentation
        +
LLM Usage Documentation
```

### Links

**Live Demo**

https://depoindex-asc7.onrender.com/

**GitHub**

https://github.com/Sanskriti029/DepoIndex

---

## 27. Conclusion

DepoIndex transforms a long deposition transcript into a chronological, searchable, and provenance-backed Topic Index.

The MVP focuses on the most important requirement for legal transcript analysis:

> **Every generated topic should lead back to verifiable evidence in the original transcript.**

The deterministic implementation provides a stable and reproducible foundation for future semantic and LLM-assisted improvements.
