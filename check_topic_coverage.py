from pathlib import Path

from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.topic_index import TOPIC_SECTIONS, collect_section_utterances


PDF_PATH = Path("data/Persis_Yu_Deposition.pdf")


def get_utterance_number(utterance_id):
    return int(utterance_id[1:])


print("=" * 70)
print("DepoIndex — Topic Coverage Diagnostic")
print("=" * 70)

# ------------------------------------------------------------
# 1. Extract transcript
# ------------------------------------------------------------

pages = extract_pdf_pages(str(PDF_PATH))

transcript = []

for page in pages:
    transcript.extend(parse_transcript_lines(page))

utterances = segment_utterances(transcript)

print(f"\nTotal utterances: {len(utterances)}")


# ------------------------------------------------------------
# 2. Determine which utterances are covered by topics
# ------------------------------------------------------------

covered = set()

for topic_id, label, start_id, end_id in TOPIC_SECTIONS:
    section = collect_section_utterances(
        utterances,
        start_id,
        end_id
    )

    for utterance in section:
        covered.add(utterance["utterance_id"])


# ------------------------------------------------------------
# 3. Find skipped utterances
# ------------------------------------------------------------

all_utterance_ids = {
    utterance["utterance_id"]
    for utterance in utterances
}

skipped = sorted(
    all_utterance_ids - covered,
    key=get_utterance_number
)


# ------------------------------------------------------------
# 4. Group consecutive skipped utterances
# ------------------------------------------------------------

ranges = []

if skipped:
    start = skipped[0]
    previous = skipped[0]

    for current in skipped[1:]:
        if (
            get_utterance_number(current)
            == get_utterance_number(previous) + 1
        ):
            previous = current
        else:
            ranges.append((start, previous))
            start = current
            previous = current

    ranges.append((start, previous))


# ------------------------------------------------------------
# 5. Print summary
# ------------------------------------------------------------

print(f"Covered utterances: {len(covered)}")
print(f"Skipped utterances: {len(skipped)}")
print(f"Skipped ranges: {len(ranges)}")


# ------------------------------------------------------------
# 6. Print skipped content
# ------------------------------------------------------------

if not ranges:
    print("\nNo skipped utterances. Full utterance coverage achieved.")

else:
    print("\n" + "=" * 70)
    print("SKIPPED UTTERANCE RANGES")
    print("=" * 70)

    utterance_lookup = {
        u["utterance_id"]: u
        for u in utterances
    }

    for start_id, end_id in ranges:

        print(f"\n{start_id} -> {end_id}")

        start_num = get_utterance_number(start_id)
        end_num = get_utterance_number(end_id)

        for number in range(start_num, end_num + 1):

            utterance_id = f"u{number:04d}"

            utterance = utterance_lookup.get(utterance_id)

            if utterance:

                text = utterance["text"].strip()

                if len(text) > 300:
                    text = text[:300] + "..."

                print(
                    f"  {utterance_id} "
                    f"[{utterance['start']['page']}:"
                    f"{utterance['start']['line']}] "
                    f"{utterance['speaker']}: {text}"
                )


print("\n" + "=" * 70)
print("Coverage diagnostic complete.")
print("=" * 70)