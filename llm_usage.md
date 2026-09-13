# LLM Usage — DepoIndex

## 1. Current LLM Usage

The current DepoIndex MVP **does not use an LLM in the production pipeline**.

The submitted implementation uses deterministic Python-based processing to:

* extract transcript text from the supplied deposition PDF
* identify transcript pages and line numbers
* segment the transcript into utterances
* organize the deposition into meaningful topic sections
* preserve exact page/line provenance
* generate the Topic Index
* identify high-confidence recurring-topic relationships
* validate topic structure
* test reproducibility across multiple runs

This approach was intentionally selected for the MVP because provenance and reproducibility are critical requirements for a legal transcript application.

The system therefore does **not** claim that an LLM generated the current topic labels or boundaries.

---

## 2. Why an LLM Was Not Used in the Current MVP

The primary requirement of DepoIndex is not simply to summarize a deposition. Every generated Topic Index entry must be independently verifiable against the original transcript.

An LLM could generate useful semantic topic suggestions, but relying directly on generated page numbers, line numbers, or boundaries could introduce hallucinated or incorrect references.

For the MVP, deterministic processing provides:

* stable topic IDs
* stable boundaries
* exact transcript references
* reproducible results
* easy debugging
* transparent validation

The current architecture therefore prioritizes **evidence integrity over generative flexibility**.

---

## 3. Current Architecture

The current pipeline is:

```text
Supplied Deposition PDF
        |
        v
PDF Text Extraction
        |
        v
Transcript Page/Line Parsing
        |
        v
Utterance Segmentation
        |
        v
Deterministic Topic Sections
        |
        v
Topic Index Generation
        |
        v
Provenance Validation
        |
        v
JSON + Human-Readable Topic Index
        |
        v
Flask Web Application
```

The important design principle is:

> **Use deterministic code for evidence and provenance.**

---

## 4. Where an LLM Could Be Added

A future version of DepoIndex could use an LLM for semantic understanding while keeping deterministic code responsible for evidence verification.

A proposed hybrid architecture is:

```text
                    Deposition PDF
                          |
                          v
                  Deterministic Extraction
                          |
                          v
                     Utterances
                          |
                          v
                 Candidate Topic Windows
                          |
                          v
                    +-----------+
                    |    LLM    |
                    +-----------+
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
     Topic Labels    Topic Transitions   Re-entry
      Suggestions       Suggestions     Suggestions
          |               |               |
          +---------------+---------------+
                          |
                          v
               Deterministic Verification
                          |
                          v
                   Final Topic Index
```

The LLM would **suggest semantic structure**, while deterministic code would verify that every final entry corresponds to actual transcript content.

---

## 5. Potential LLM Responsibilities

A future LLM-based version could assist with:

### 5.1 Topic Discovery

The model could identify meaningful subject changes within the deposition.

For example:

```text
"Student loan servicing"
"ITT student outcomes"
"PEAKS loan enforceability"
"Regulatory investigations"
```

The model would propose candidate topic labels rather than directly creating final evidence references.

---

### 5.2 Topic Label Generation

The LLM could convert transcript content into concise attorney-friendly topic names.

For example:

```text
Raw discussion:
Questions concerning PEAKS loan documentation,
borrower disclosures, and cancellation rights.

Possible LLM label:
"PEAKS Disclosures and Borrower Cancellation Rights"
```

The final label could then be reviewed or accepted by the deterministic pipeline.

---

### 5.3 Topic Transition Detection

The LLM could identify points where the subject matter changes.

For example:

```text
Utterance 240
        |
        | Discussion of ITT graduate earnings
        |
Utterance 241
        |
        v
Topic transition
        |
        v
Utterance 242
        |
        | Discussion of Vervent and PEAKS
        |
```

The model could propose:

```json
{
  "transition_after_utterance": "u0241"
}
```

The application would then verify the corresponding transcript location.

---

### 5.4 Digression Detection

Depositions frequently contain short digressions.

An LLM could identify whether a short discussion is:

* a genuine new topic
* a temporary clarification
* an attorney interruption
* an administrative statement
* a brief digression that should remain inside the parent topic

This could improve boundary quality over purely rule-based segmentation.

---

### 5.5 Recurring Topic Detection

The LLM could identify when an earlier subject reappears later.

For example:

```text
T005
Student Loan Servicing Initiatives

            ...
            later in deposition
            ...

T019
Loan Servicing, Collection, and Servicer Functions
```

The system could mark this as a possible re-entry relationship.

The final relationship should still be validated against the actual transcript.

---

## 6. Provenance Safety

An important rule for a legal transcript application is:

> **The LLM should never be trusted to invent page or line references.**

Instead, the LLM should work with stable utterance IDs.

For example:

```json
{
  "utterance_id": "u0266",
  "page": 44,
  "line": 12,
  "text": "..."
}
```

The LLM could return:

```json
{
  "topic": "PEAKS Loan Enforceability",
  "start_utterance": "u0266",
  "end_utterance": "u0298"
}
```

The deterministic application would then look up:

```text
u0266 -> Page 44, Line 12
u0298 -> Page 50, Line 3
```

This prevents the model from generating unsupported page or line numbers.

---

## 7. Proposed LLM Output Format

A future model could be constrained to return structured JSON such as:

```json
{
  "topics": [
    {
      "topic": "PEAKS Loan Enforceability",
      "start_utterance": "u0266",
      "end_utterance": "u0298",
      "confidence": 0.91,
      "reason": "The discussion focuses on whether PEAKS loans were legally enforceable."
    }
  ]
}
```

The application would validate:

1. Both utterance IDs exist.
2. The start occurs before the end.
3. The utterances belong to the supplied transcript.
4. Page/line references are derived from the source.
5. The proposed topic contains meaningful transcript content.
6. Topic ordering is chronological.
7. Topic overlaps are handled correctly.
8. Re-entry relationships are explicitly represented.

Only validated results would become part of the final Topic Index.

---

## 8. Suggested Prompt Strategy

A future LLM prompt could instruct the model:

```text
You are analyzing a deposition transcript.

Identify meaningful subject-matter topics and topic transitions.

For each topic:
- provide a concise attorney-friendly label
- provide the first utterance ID
- provide the last utterance ID
- explain why the topic represents a coherent subject
- identify possible recurring topics

Do not invent page numbers or line numbers.
Use only the supplied utterance IDs.
Do not summarize unrelated administrative material as a topic.
Keep brief digressions inside the surrounding topic unless they represent
a meaningful and sustained subject change.

Return valid JSON only.
```

---

## 9. Deterministic Verification After the LLM

The proposed production pipeline would not directly trust the LLM output.

The verification layer would check:

```text
LLM Proposal
     |
     v
Valid utterance IDs?
     |
     +---- No ----> Reject
     |
    Yes
     |
     v
Chronologically valid?
     |
     +---- No ----> Reject
     |
    Yes
     |
     v
Source references exist?
     |
     +---- No ----> Reject
     |
    Yes
     |
     v
Topic content relevant?
     |
     +---- No ----> Review
     |
    Yes
     |
     v
Final Topic Index
```

This provides a safety boundary between semantic generation and legal evidence.

---

## 10. Reproducibility

Introducing an LLM creates additional sources of variation.

A production implementation should therefore control:

* model version
* prompt version
* chunking strategy
* temperature
* generation parameters
* output schema
* transcript preprocessing
* validation rules

Raw LLM outputs should also be stored when appropriate so that the result can be audited.

A canonical hash can then be calculated over the final validated Topic Index.

The existing deterministic MVP already demonstrates this reproducibility approach through three complete pipeline runs.

---

## 11. Evaluation of a Future LLM System

An LLM-based version should be evaluated separately from general language-model quality.

Important metrics include:

### Topic quality

Are the identified topics meaningful and useful to an attorney?

### Boundary quality

Does the topic start and end at appropriate transcript locations?

### Provenance accuracy

Can every page/line reference be verified against the original transcript?

### Coverage

Does the system account for substantive testimony?

### Redundancy

Does it avoid creating unnecessary duplicate topics?

### Re-entry accuracy

Does it correctly recognize topics that return later?

### Stability

Do repeated runs produce sufficiently consistent results?

The current manual validation methodology can serve as the baseline for evaluating future LLM improvements.

---

## 12. Current MVP vs Future LLM Architecture

| Capability             | Current MVP                              | Future Hybrid Version                 |
| ---------------------- | ---------------------------------------- | ------------------------------------- |
| PDF extraction         | Deterministic                            | Deterministic                         |
| Page/line parsing      | Deterministic                            | Deterministic                         |
| Utterance segmentation | Deterministic                            | Deterministic                         |
| Topic discovery        | Deterministic                            | LLM-assisted                          |
| Topic labels           | Deterministic                            | LLM-assisted                          |
| Boundary proposals     | Deterministic                            | LLM-assisted                          |
| Digression detection   | Rule-based/manual                        | LLM-assisted                          |
| Re-entry detection     | Conservative deterministic relationships | LLM-assisted + verified               |
| Provenance             | Deterministic                            | Deterministic                         |
| Validation             | Deterministic                            | Deterministic                         |
| Reproducibility        | Strong                                   | Requires controlled LLM configuration |

---

## 13. Why the Hybrid Approach Is Preferred

A fully generative system would make it harder to guarantee that generated references correspond exactly to the source transcript.

A hybrid architecture separates two responsibilities:

```text
LLM
=
Understanding

Deterministic Code
=
Evidence
```

The LLM can provide semantic intelligence while deterministic code maintains the auditability required for deposition analysis.

---

## 14. Scaling Considerations

For hundreds of depositions, the same architecture could be extended with:

* background processing jobs
* deposition IDs
* persistent storage
* batch processing
* processing status tracking
* centralized logging
* model/version tracking
* cached LLM results
* automated validation
* human review workflows

Individual depositions could be processed independently and, where infrastructure permits, in parallel.

---

## 15. Security and Legal Considerations

A production implementation using an external LLM would need to consider:

* confidentiality of deposition transcripts
* sensitive legal information
* data retention
* access control
* encryption
* model-provider policies
* whether transcript data can be used for model training
* audit logging
* secure deletion requirements

The deployment architecture should therefore be designed according to the confidentiality requirements of the legal organization using the system.

---

## 16. Final Status

**Current submitted MVP:**

> No LLM is used in the topic-generation pipeline.

The current implementation intentionally uses deterministic processing to provide a reliable and reproducible baseline with exact transcript provenance.

**Future direction:**

> Add an LLM as a semantic reasoning layer while keeping deterministic code responsible for page/line references, provenance, validation, and final evidence integrity.

The core design principle is:

> **Use AI for understanding. Use deterministic code for evidence.**
