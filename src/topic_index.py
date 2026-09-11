"""
Deterministic, provenance-safe topic segmentation for deposition transcripts.

The topic boundaries are defined using utterance IDs from the extracted
transcript. Page/line provenance is resolved from the original transcript
records, so the system does not invent page or line numbers.
"""

from typing import Dict, List, Any


# ---------------------------------------------------------------------------
# Topic sections
# ---------------------------------------------------------------------------
# Each topic is defined by its first and last utterance.
# The utterance IDs are resolved against the actual extracted transcript.
# ---------------------------------------------------------------------------

TOPIC_SECTIONS = [
    (
        "T001",
        "Deposition Setup and Scope of Testimony",
        "u0005",
        "u0024",
    ),
    (
        "T002",
        "Expert Report, Qualifications, and Current Role",
        "u0025",
        "u0031",
    ),
    (
        "T003",
        "Student Borrower Protection Center Policy Work",
        "u0032",
        "u0043",
    ),
    (
        "T004",
        "Student Loan Rulemaking and Advocacy Experience",
        "u0044",
        "u0054",
    ),
    (
        "T005",
        "Student Loan Servicing Initiatives and Public Testimony",
        "u0055",
        "u0072",
    ),
    (
        "T006",
        "Student Loan Portfolio Transfers and Data Requirements",
        "u0073",
        "u0100",
    ),
    (
        "T007",
        "Criminal Law and RICO Experience",
        "u0101",
        "u0130",
    ),
    (
        "T008",
        "For-Profit Colleges and ITT Education",
        "u0131",
        "u0154",
    ),
    (
        "T009",
        "ITT Student Outcomes and Degree Completion",
        "u0155",
        "u0189",
    ),
    (
        "T010",
        "ITT Education Benefits and Misrepresentation Evidence",
        "u0190",
        "u0200",
    ),
    (
        "T011",
        "ITT Graduate Earnings and Outcome Hypotheticals",
        "u0201",
        "u0241",
    ),
    (
        "T012",
        "Vervent Role in PEAKS Loan Origination and Recruiting",
        "u0242",
        "u0265",
    ),
    (
        "T013",
        "PEAKS Loan Enforceability and Legal Determinations",
        "u0266",
        "u0298",
    ),
    (
        "T014",
        "PEAKS Documentation Defects and Scope of Review",
        "u0299",
        "u0339",
    ),
    (
        "T015",
        "PEAKS Disclosures and Borrower Cancellation Rights",
        "u0340",
        "u0392",
    ),
    (
        "T016",
        "ITT Practices and Public Evidence of Misconduct",
        "u0394",
        "u0418",
    ),
    (
        "T017",
        "CFPB, SEC, State, and Education Department Investigations",
        "u0420",
        "u0509",
    ),
    (
        "T018",
        "Professional Investigation Experience and Meaning of Investigations",
        "u0511",
        "u0546",
    ),
    (
        "T019",
        "Loan Servicing, Collection, and Servicer Functions",
        "u0547",
        "u0557",
    ),
    (
        "T020",
        "Servicer Duties, Unfair Practices, and PEAKS Enforcement",
        "u0558",
        "u0563",
    ),
    (
        "T021",
        "PEAKS Enforceability Timing and Vervent Servicing",
        "u0564",
        "u0627",
    ),
    (
        "T022",
        "Deposition Conclusion and Administrative Pages",
        "u0628",
        "u0630",
    ),
]

TOPIC_RELATIONSHIPS = [
    {
        "topic_id": "T005",
        "related_topic_ids": ["T019", "T020", "T021"],
        "relationship": "reentry",
        "reason": (
            "Student loan servicing and servicer functions are revisited "
            "later in the deposition."
        ),
    },
    {
        "topic_id": "T006",
        "related_topic_ids": ["T019", "T020", "T021"],
        "relationship": "reentry",
        "reason": (
            "The broader loan-servicing subject returns later when the "
            "deposition addresses servicing, collection, and Vervent servicing."
        ),
    },
    {
        "topic_id": "T008",
        "related_topic_ids": ["T016"],
        "relationship": "reentry",
        "reason": (
            "ITT education practices are revisited later with a focus on "
            "public evidence of misconduct."
        ),
    },
    {
        "topic_id": "T012",
        "related_topic_ids": ["T020", "T021"],
        "relationship": "reentry",
        "reason": (
            "The PEAKS/Vervent subject returns later in the deposition "
            "during discussion of enforcement and servicing."
        ),
    },
    {
        "topic_id": "T013",
        "related_topic_ids": ["T021"],
        "relationship": "reentry",
        "reason": (
            "PEAKS enforceability is revisited later when discussing "
            "enforceability timing and Vervent servicing."
        ),
    },
]

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def build_utterance_lookup(
    utterances: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Create a lookup:

        utterance_id -> utterance

    Example:

        u0014 -> complete utterance record
    """

    return {
        utterance["utterance_id"]: utterance
        for utterance in utterances
        if "utterance_id" in utterance
    }


def get_utterance_number(utterance_id: str) -> int:
    """
    Convert an utterance ID such as u0014 into integer 14.

    Used for chronological ordering.
    """

    return int(utterance_id[1:])


def collect_section_utterances(
    utterances: List[Dict[str, Any]],
    start_id: str,
    end_id: str,
) -> List[Dict[str, Any]]:
    """
    Return all utterances between start_id and end_id, inclusive.
    """

    start_num = get_utterance_number(start_id)
    end_num = get_utterance_number(end_id)

    selected = []

    for utterance in utterances:

        utterance_id = utterance.get("utterance_id")

        if not utterance_id:
            continue

        number = get_utterance_number(utterance_id)

        if start_num <= number <= end_num:
            selected.append(utterance)

    selected.sort(
        key=lambda item: get_utterance_number(
            item["utterance_id"]
        )
    )

    return selected


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def get_source_lines(
    utterances: List[Dict[str, Any]],
    transcript_lookup: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Resolve source-line IDs stored in utterances back to the original
    extracted transcript records.

    utterances.py stores source_lines like:

        ["p7_l12", "p7_l13", "p7_l14"]

    transcript_lookup maps those IDs to records such as:

        {
            "id": "p7_l12",
            "pdf_page": 9,
            "transcript_page": 3,
            "line": 12,
            "text": "..."
        }
    """

    source_lines = []
    seen = set()

    for utterance in utterances:

        for source_id in utterance.get("source_lines", []):

            if source_id in seen:
                continue

            source = transcript_lookup.get(source_id)

            if source is None:
                continue

            seen.add(source_id)

            source_lines.append(source)

    # Keep source lines chronological.
    source_lines.sort(
        key=lambda item: (
            item.get("pdf_page", 0),
            item.get("line", 0),
        )
    )

    return source_lines


def get_location(
    source_line: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert a transcript source record into a public location object.
    """

    return {
        "pdf_page": source_line.get("pdf_page"),
        "transcript_page": source_line.get("transcript_page"),
        "line": source_line.get("line"),
    }


# ---------------------------------------------------------------------------
# Excerpt
# ---------------------------------------------------------------------------

def build_excerpt(
    utterances: List[Dict[str, Any]],
    max_chars: int = 700,
) -> str:
    """
    Build a short human-readable excerpt from the beginning of a topic.

    The complete transcript remains available through provenance.
    """

    parts = []

    for utterance in utterances:

        text = utterance.get("text", "").strip()

        if text:
            parts.append(text)

        excerpt = " ".join(parts)

        if len(excerpt) >= max_chars:
            return excerpt[:max_chars].rstrip() + "..."

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Build one topic
# ---------------------------------------------------------------------------

def build_topic(
    topic_id: str,
    label: str,
    start_id: str,
    end_id: str,
    utterances: List[Dict[str, Any]],
    transcript_lookup: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build one complete Topic Index entry.
    """

    section_utterances = collect_section_utterances(
        utterances,
        start_id,
        end_id,
    )

    if not section_utterances:
        raise ValueError(
            f"No utterances found for {topic_id}: "
            f"{start_id} -> {end_id}"
        )

    first_utterance = section_utterances[0]
    last_utterance = section_utterances[-1]

    # Resolve source-line IDs to actual transcript records.
    source_lines = get_source_lines(
        section_utterances,
        transcript_lookup,
    )

    if not source_lines:
        raise ValueError(
            f"No provenance lines found for {topic_id}"
        )

    # Exact start/end locations come from the actual source records.
    start_location = get_location(source_lines[0])
    end_location = get_location(source_lines[-1])

    return {
        "topic_id": topic_id,

        "topic": label,

        "start": {
            **start_location,
            "utterance_id": first_utterance["utterance_id"],
        },

        "end": {
            **end_location,
            "utterance_id": last_utterance["utterance_id"],
        },

        "utterance_start": first_utterance["utterance_id"],

        "utterance_end": last_utterance["utterance_id"],

        "utterance_count": len(section_utterances),

        "excerpt": build_excerpt(section_utterances),

        "provenance": {
            "source_line_count": len(source_lines),
            "source_lines": source_lines,
        },
    }


# ----------------------------------------------------------------------
# 
# 
# -----
# Build complete Topic Index
# ---------------------------------------------------------------------------
def build_topic_index(utterances, transcript):
    utterance_lookup = build_utterance_lookup(utterances)
    transcript_lookup = {
        record["id"]: record
        for record in transcript
        if "id" in record
    }

    relationship_lookup = {}

    for relationship in TOPIC_RELATIONSHIPS:
        topic_id = relationship["topic_id"]

        relationship_lookup[topic_id] = relationship

        for related_id in relationship["related_topic_ids"]:
            relationship_lookup.setdefault(
                related_id,
                {
                    "topic_id": related_id,
                    "related_topic_ids": [],
                    "relationship": relationship["relationship"],
                    "reason": relationship["reason"],
                }
            )

            if topic_id not in relationship_lookup[related_id]["related_topic_ids"]:
                relationship_lookup[related_id]["related_topic_ids"].append(
                    topic_id
                )

    topics = []

    for topic_id, label, start_id, end_id in TOPIC_SECTIONS:

        if start_id not in utterance_lookup:
            raise ValueError(
                f"{topic_id}: start utterance {start_id} not found"
            )

        if end_id not in utterance_lookup:
            raise ValueError(
                f"{topic_id}: end utterance {end_id} not found"
            )

        topic = build_topic(
            topic_id,
            label,
            start_id,
            end_id,
            utterances,
            transcript_lookup
        )

        relationship = relationship_lookup.get(topic_id)

        if relationship:
            topic["related_topics"] = relationship[
                "related_topic_ids"
            ]

            topic["relationship"] = relationship[
                "relationship"
            ]

            topic["relationship_reason"] = relationship[
                "reason"
            ]
        else:
            topic["related_topics"] = []
            topic["relationship"] = None
            topic["relationship_reason"] = None

        topics.append(topic)

    return topics

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_topic_index(
    topics: List[Dict[str, Any]],
    utterances: List[Dict[str, Any]],
) -> List[str]:
    """
    Perform structural validation of the generated Topic Index.

    Returns:

        []          -> no structural problems

        [problems]  -> one or more detected problems
    """

    problems = []

    # -----------------------------------------------------------------------
    # Check that topics exist
    # -----------------------------------------------------------------------

    if not topics:
        problems.append(
            "Topic index is empty."
        )

        return problems

    # -----------------------------------------------------------------------
    # Check topic IDs
    # -----------------------------------------------------------------------

    expected_ids = [
        section[0]
        for section in TOPIC_SECTIONS
    ]

    actual_ids = [
        topic.get("topic_id")
        for topic in topics
    ]
    topic_id_set = set(actual_ids)

    for topic in topics:
        topic_id = topic.get("topic_id")

        for related_id in topic.get("related_topics", []):
            if related_id not in topic_id_set:
                problems.append(
                    f"{topic_id}: related topic {related_id} does not exist."
                )

    if actual_ids != expected_ids:
        problems.append(
            "Topic IDs are missing, duplicated, "
            "or out of order."
        )

    # -----------------------------------------------------------------------
    # Utterance lookup
    # -----------------------------------------------------------------------

    utterance_lookup = build_utterance_lookup(
        utterances
    )

    previous_end = None

    # -----------------------------------------------------------------------
    # Validate every topic
    # -----------------------------------------------------------------------

    for topic in topics:

        topic_id = topic.get("topic_id")

        start_id = topic.get(
            "utterance_start"
        )

        end_id = topic.get(
            "utterance_end"
        )

        # ---------------------------------------------------------------
        # Start utterance exists
        # ---------------------------------------------------------------

        if start_id not in utterance_lookup:
            problems.append(
                f"{topic_id}: "
                f"start utterance does not exist."
            )

        # ---------------------------------------------------------------
        # End utterance exists
        # ---------------------------------------------------------------

        if end_id not in utterance_lookup:
            problems.append(
                f"{topic_id}: "
                f"end utterance does not exist."
            )

        # ---------------------------------------------------------------
        # Chronological ordering
        # ---------------------------------------------------------------

        if (
            start_id in utterance_lookup
            and end_id in utterance_lookup
        ):

            start_num = get_utterance_number(
                start_id
            )

            end_num = get_utterance_number(
                end_id
            )

            if start_num > end_num:
                problems.append(
                    f"{topic_id}: "
                    f"start occurs after end."
                )

            if (
                previous_end is not None
                and start_num <= previous_end
            ):
                problems.append(
                    f"{topic_id}: "
                    f"topic overlaps a previous topic."
                )

            previous_end = end_num

        # ---------------------------------------------------------------
        # Provenance
        # ---------------------------------------------------------------

        provenance = topic.get(
            "provenance",
            {}
        )

        source_lines = provenance.get(
            "source_lines",
            []
        )

        if not source_lines:
            problems.append(
                f"{topic_id}: "
                f"no provenance source lines."
            )

        # ---------------------------------------------------------------
        # Start location
        # ---------------------------------------------------------------

        if not topic.get("start"):
            problems.append(
                f"{topic_id}: "
                f"missing start location."
            )

        # ---------------------------------------------------------------
        # End location
        # ---------------------------------------------------------------

        if not topic.get("end"):
            problems.append(
                f"{topic_id}: "
                f"missing end location."
            )

    return problems