from pathlib import Path

from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.topic_index import build_topic_index


PDF_PATH = Path("data/Persis_Yu_Deposition.pdf")


def print_topic(topic):
    print("\n" + "=" * 80)
    print(
        f"{topic['topic_id']} — {topic['topic']}"
    )
    print("=" * 80)

    print(
        f"START: P{topic['start']['transcript_page']} "
        f"L{topic['start']['line']} "
        f"({topic['start']['utterance_id']})"
    )

    print(
        f"END:   P{topic['end']['transcript_page']} "
        f"L{topic['end']['line']} "
        f"({topic['end']['utterance_id']})"
    )

    print(
        f"Utterances: {topic['utterance_count']}"
    )

    print("\nEXCERPT:")
    print(topic["excerpt"])


print("=" * 80)
print("DepoIndex — Manual Topic Validation Review")
print("=" * 80)

# ------------------------------------------------------------
# 1. Extract transcript
# ------------------------------------------------------------

pages = extract_pdf_pages(str(PDF_PATH))

transcript = []

for page in pages:
    transcript.extend(parse_transcript_lines(page))

utterances = segment_utterances(transcript)

topics = build_topic_index(
    utterances,
    transcript,
)


# ------------------------------------------------------------
# 2. Select 20 topics
# ------------------------------------------------------------

# We review 20 of the 22 topics.
# T001-T020 provide broad coverage of the deposition,
# including early, middle, and later sections.

selected_topics = topics[:20]


print(
    f"\nReviewing {len(selected_topics)} topics "
    f"out of {len(topics)} generated topics."
)


# ------------------------------------------------------------
# 3. Print topics
# ------------------------------------------------------------

for topic in selected_topics:
    print_topic(topic)


print("\n" + "=" * 80)
print("Manual validation review data complete.")
print("=" * 80)