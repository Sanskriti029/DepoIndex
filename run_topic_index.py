"""
Run the complete DepoIndex Topic Index pipeline.

Pipeline:

PDF
 ↓
Extract PDF pages
 ↓
Parse transcript lines
 ↓
Build speaker utterances
 ↓
Build Topic Index
 ↓
Validate Topic Index
 ↓
Write JSON + Markdown outputs
"""

import json
from pathlib import Path

from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.topic_index import build_topic_index, validate_topic_index


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

PDF_PATH = BASE_DIR / "data" / "Persis_Yu_Deposition.pdf"
OUTPUT_DIR = BASE_DIR / "outputs"

JSON_PATH = OUTPUT_DIR / "topic_index.json"
MARKDOWN_PATH = OUTPUT_DIR / "topic_index.md"


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def topic_to_markdown(topic):
    """
    Convert one Topic Index entry into a human-readable Markdown section.
    """

    start = topic["start"]
    end = topic["end"]

    start_location = (
        f"PDF page {start['pdf_page']}, "
        f"transcript page {start['transcript_page']}, "
        f"line {start['line']}"
    )

    end_location = (
        f"PDF page {end['pdf_page']}, "
        f"transcript page {end['transcript_page']}, "
        f"line {end['line']}"
    )

    lines = []

    lines.append(f"## {topic['topic_id']} — {topic['topic']}")
    lines.append("")

    lines.append(
        f"**Start:** {start_location} "
        f"(`{topic['utterance_start']}`)"
    )
    lines.append("")

    lines.append(
        f"**End:** {end_location} "
        f"(`{topic['utterance_end']}`)"
    )
    lines.append("")

    lines.append(
        f"**Utterances:** {topic['utterance_count']}"
    )
    lines.append("")

    lines.append("### Excerpt")
    lines.append("")
    lines.append(topic["excerpt"])
    lines.append("")

    lines.append("### Provenance")
    lines.append("")
    lines.append(
        f"Source lines: {topic['provenance']['source_line_count']}"
    )
    lines.append("")

    return "\n".join(lines)


def build_markdown(topics):
    """
    Build the complete human-readable Topic Index.
    """

    lines = []

    lines.append("# DepoIndex — Topic Index")
    lines.append("")

    lines.append(
        "Chronologically ordered topic index generated from the "
        "complete deposition transcript."
    )
    lines.append("")

    lines.append(
        f"**Total topics:** {len(topics)}"
    )
    lines.append("")

    lines.append(
        "Each topic contains exact transcript provenance derived "
        "from the extracted source lines."
    )
    lines.append("")

    lines.append("---")
    lines.append("")

    for topic in topics:
        lines.append(topic_to_markdown(topic))

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():

    print("=" * 70)
    print("DepoIndex — Topic Index Pipeline")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Step 1: Check PDF
    # -----------------------------------------------------------------------

    print("\n[1/5] Checking deposition PDF...")

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Deposition PDF not found: {PDF_PATH}"
        )

    print(f"      PDF: {PDF_PATH}")

    # -----------------------------------------------------------------------
    # Step 2: Extract and parse transcript
    # -----------------------------------------------------------------------

    print("\n[2/5] Extracting transcript lines...")

    pages = extract_pdf_pages(str(PDF_PATH))

    transcript = []

    for page in pages:
        records = parse_transcript_lines(page)
        transcript.extend(records)

    print(
        f"      Processed {len(pages)} PDF pages."
    )

    print(
        f"      Extracted {len(transcript)} transcript lines."
    )

    # -----------------------------------------------------------------------
    # Step 3: Build utterances
    # -----------------------------------------------------------------------

    print("\n[3/5] Building speaker utterances...")

    utterances = segment_utterances(transcript)

    print(
        f"      Built {len(utterances)} utterances."
    )

    # -----------------------------------------------------------------------
    # Step 4: Build Topic Index
    # -----------------------------------------------------------------------

    print("\n[4/5] Building Topic Index...")

    topics = build_topic_index(utterances, transcript)

    print(
        f"      Generated {len(topics)} topics."
    )

    # -----------------------------------------------------------------------
    # Step 5: Validate and save
    # -----------------------------------------------------------------------

    print("\n[5/5] Validating and saving outputs...")

    problems = validate_topic_index(
        topics,
        utterances,
    )

    if problems:

        print("\nValidation problems detected:")

        for problem in problems:
            print(f"  - {problem}")

        raise RuntimeError(
            "Topic Index validation failed."
        )

    print("      Structural validation: PASSED")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------------------------
    # Save JSON
    # -----------------------------------------------------------------------

    with open(
        JSON_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            topics,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # -----------------------------------------------------------------------
    # Save Markdown
    # -----------------------------------------------------------------------

    markdown = build_markdown(topics)

    with open(
        MARKDOWN_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(markdown)

    # -----------------------------------------------------------------------
    # Final summary
    # -----------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("Topic Index generation complete!")
    print("=" * 70)

    print(f"\nTopics generated : {len(topics)}")
    print(f"JSON output      : {JSON_PATH}")
    print(f"Markdown output  : {MARKDOWN_PATH}")

    print("\nFirst topic:")
    print(
        f"  {topics[0]['topic_id']} — "
        f"{topics[0]['topic']}"
    )

    print("\nLast topic:")
    print(
        f"  {topics[-1]['topic_id']} — "
        f"{topics[-1]['topic']}"
    )


if __name__ == "__main__":
    main()