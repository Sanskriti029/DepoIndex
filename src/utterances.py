from typing import List, Dict
import re


def detect_speaker(text):
    """
    Detect the speaker from the beginning of a transcript line.
    """

    if re.match(r"^\s*Q\s+", text):
        return "Q"

    if re.match(r"^\s*A\s+", text):
        return "A"

    if re.match(r"^\s*BY\s+", text):
        return "ATTORNEY"

    if re.match(r"^\s*THE\s+REPORTER\b", text, re.IGNORECASE):
        return "REPORTER"

    if re.match(r"^\s*THE\s+WITNESS\b", text, re.IGNORECASE):
        return "WITNESS"

    if re.match(r"^\s*MR\.\s+", text, re.IGNORECASE):
        return "ATTORNEY"

    if re.match(r"^\s*MS\.\s+", text, re.IGNORECASE):
        return "ATTORNEY"

    return None

def segment_utterances(records: List[Dict]) -> List[Dict]:

    # Ignore non-transcript records
    records = [
        record
        for record in records
        if record.get("transcript_page") is not None
    ]

    # Process transcript in chronological order
    records.sort(
        key=lambda record: (
            record["transcript_page"],
            record["line"]
        )
    )

    utterances = []
    current = None
    utterance_number = 1

    for record in records:
        text = record["text"].strip()

        if not text:
            continue

        speaker = detect_speaker(text)

        if speaker is not None:
            if current is not None:
                utterances.append(current)

            current = {
                "utterance_id": f"u{utterance_number:04d}",
                "speaker": speaker,
                "start": {
                    "page": record["transcript_page"],
                    "line": record["line"]
                },
                "end": {
                    "page": record["transcript_page"],
                    "line": record["line"]
                },
                "text": text,
                "source_lines": [record["id"]]
            }

            utterance_number += 1

        elif current is not None:
            current["text"] += " " + text

            current["end"] = {
                "page": record["transcript_page"],
                "line": record["line"]
            }

            current["source_lines"].append(record["id"])

        else:
            current = {
                "utterance_id": f"u{utterance_number:04d}",
                "speaker": "UNKNOWN",
                "start": {
                    "page": record["transcript_page"],
                    "line": record["line"]
                },
                "end": {
                    "page": record["transcript_page"],
                    "line": record["line"]
                },
                "text": text,
                "source_lines": [record["id"]]
            }

            utterance_number += 1

    if current is not None:
        utterances.append(current)

    return utterances

if __name__ == "__main__":
    from src.extraction import extract_pdf_pages, parse_transcript_lines
    from src.validation import validate_utterances

    pdf_path = "data/Persis_Yu_Deposition.pdf"

    pages = extract_pdf_pages(pdf_path)

    all_records = []

    for page in pages:
        records = parse_transcript_lines(page)
        all_records.extend(records)

    print("\nLAST 30 RECORDS")
    print("=" * 60)

    for record in all_records[-30:]:
        print(record)

    utterances = segment_utterances(all_records)

    print(f"\nTotal transcript lines: {len(all_records)}")
    print(f"Total utterances: {len(utterances)}")

    issues = validate_utterances(utterances)

    print("\nVALIDATION")
    print("=" * 60)

    print(f"Validation issues: {len(issues)}")

    for issue in issues:
        print("-", issue)

    if not issues:
        print("No structural issues found.")