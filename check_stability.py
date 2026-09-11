import hashlib
import json
from pathlib import Path

from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.topic_index import build_topic_index, validate_topic_index


PDF_PATH = Path("data/Persis_Yu_Deposition.pdf")


def run_pipeline_once():
    pages = extract_pdf_pages(str(PDF_PATH))

    transcript = []

    for page in pages:
        transcript.extend(parse_transcript_lines(page))

    utterances = segment_utterances(transcript)

    topics = build_topic_index(
        utterances,
        transcript
    )

    problems = validate_topic_index(
        topics,
        utterances
    )

    if problems:
        raise RuntimeError(
            "Structural validation failed:\n"
            + "\n".join(problems)
        )

    return {
        "pdf_pages": len(pages),
        "transcript_lines": len(transcript),
        "utterances": len(utterances),
        "topics": topics,
    }


def canonical_topics(topics):
    """
    Create a deterministic representation containing
    the fields that matter for stability validation.
    """

    result = []

    for topic in topics:
        result.append({
            "topic_id": topic["topic_id"],
            "topic": topic["topic"],

            "start": {
                "pdf_page": topic["start"]["pdf_page"],
                "transcript_page": topic["start"]["transcript_page"],
                "line": topic["start"]["line"],
                "utterance_id": topic["start"]["utterance_id"],
            },

            "end": {
                "pdf_page": topic["end"]["pdf_page"],
                "transcript_page": topic["end"]["transcript_page"],
                "line": topic["end"]["line"],
                "utterance_id": topic["end"]["utterance_id"],
            },

            "utterance_start": topic["utterance_start"],
            "utterance_end": topic["utterance_end"],

            "related_topics": topic.get(
                "related_topics",
                []
            ),

            "relationship": topic.get(
                "relationship"
            ),

            "provenance": topic["provenance"],
        })

    return result


def make_hash(data):
    canonical_json = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def main():

    runs = []

    print("=" * 70)
    print("DepoIndex — 3-Run Stability Check")
    print("=" * 70)

    for run_number in range(1, 4):

        result = run_pipeline_once()

        signature = canonical_topics(
            result["topics"]
        )

        result_hash = make_hash(signature)

        runs.append({
            "stats": {
                "pdf_pages": result["pdf_pages"],
                "transcript_lines": result["transcript_lines"],
                "utterances": result["utterances"],
                "topics": len(result["topics"]),
            },
            "signature": signature,
            "hash": result_hash,
        })

        print()
        print(f"RUN {run_number}")
        print("-" * 50)

        print(
            f"PDF pages        : "
            f"{result['pdf_pages']}"
        )

        print(
            f"Transcript lines : "
            f"{result['transcript_lines']}"
        )

        print(
            f"Utterances       : "
            f"{result['utterances']}"
        )

        print(
            f"Topics           : "
            f"{len(result['topics'])}"
        )

        print(
            f"Canonical SHA256 : "
            f"{result_hash}"
        )

    print()
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)

    signatures_identical = (
        runs[0]["signature"]
        == runs[1]["signature"]
        == runs[2]["signature"]
    )

    hashes_identical = (
        len({
            run["hash"]
            for run in runs
        }) == 1
    )

    stats_identical = (
        runs[0]["stats"]
        == runs[1]["stats"]
        == runs[2]["stats"]
    )

    if signatures_identical:
        print(
            "PASS: Topic IDs, labels, boundaries, "
            "relationships, and provenance are identical."
        )
    else:
        print(
            "FAIL: Topic outputs differ between runs."
        )

    if hashes_identical:
        print(
            "PASS: All three canonical hashes are identical."
        )
    else:
        print(
            "FAIL: Canonical hashes differ."
        )

    if stats_identical:
        print(
            "PASS: Page, line, utterance, and "
            "topic counts are identical."
        )
    else:
        print(
            "FAIL: Pipeline statistics differ."
        )

    print()

    if (
        signatures_identical
        and hashes_identical
        and stats_identical
    ):
        print(
            "STABILITY RESULT: PASS"
        )
    else:
        print(
            "STABILITY RESULT: FAIL"
        )


if __name__ == "__main__":
    main()