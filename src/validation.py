from typing import List, Dict


def validate_utterances(utterances: List[Dict]) -> List[str]:
    """
    Run deterministic sanity checks on segmented utterances.

    Returns a list of warning/error messages instead of crashing.
    """

    issues = []

    if not utterances:
        issues.append("No utterances were generated.")
        return issues

    # --------------------------------------------------
    # Check utterance IDs
    # --------------------------------------------------

    for index, utterance in enumerate(utterances, start=1):

        expected_id = f"u{index:04d}"

        if utterance.get("utterance_id") != expected_id:
            issues.append(
                f"Unexpected utterance ID: "
                f"{utterance.get('utterance_id')} "
                f"(expected {expected_id})"
            )

    # --------------------------------------------------
    # Check source lines
    # --------------------------------------------------

    for utterance in utterances:

        if not utterance.get("source_lines"):
            issues.append(
                f"{utterance.get('utterance_id')} has no source lines."
            )

    # --------------------------------------------------
    # Check start/end structure
    # --------------------------------------------------

    for utterance in utterances:

        utterance_id = utterance.get("utterance_id")

        start = utterance.get("start", {})
        end = utterance.get("end", {})

        start_page = start.get("page")
        start_line = start.get("line")

        end_page = end.get("page")
        end_line = end.get("line")

        # Don't compare incomplete locations.
        if None in (start_page, start_line, end_page, end_line):

            issues.append(
                f"{utterance_id} has incomplete provenance: "
                f"start={start}, end={end}"
            )

            continue

        start_position = (start_page, start_line)
        end_position = (end_page, end_line)

        if start_position > end_position:

            issues.append(
                f"{utterance_id} has invalid start/end ordering."
            )

    # --------------------------------------------------
    # Check chronological ordering
    # --------------------------------------------------

    previous_end = None

    for utterance in utterances:

        end = utterance.get("end", {})

        end_page = end.get("page")
        end_line = end.get("line")

        current_start = utterance.get("start", {})

        start_page = current_start.get("page")
        start_line = current_start.get("line")

        # Skip incomplete provenance.
        if None in (
            start_page,
            start_line,
            end_page,
            end_line
        ):
            continue

        current_start_position = (
            start_page,
            start_line
        )

        current_end_position = (
            end_page,
            end_line
        )

        if (
            previous_end is not None
            and current_start_position < previous_end
        ):

            issues.append(
                f"{utterance['utterance_id']} is out of "
                f"chronological order."
            )

        previous_end = current_end_position

    return issues