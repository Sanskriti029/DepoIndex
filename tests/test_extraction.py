from src.extraction import parse_transcript_lines


def get_record(records, line_number):
    """Find a parsed record using its original transcript line number."""
    return next(
        record
        for record in records
        if record["line"] == line_number
    )


def test_page_and_line_provenance():
    page = {
        "pdf_page": 7,
        "text": """
1
2
3
11   BY MR. PURCELL:
12   Q    Good afternoon, Ms. Yu.
13   I represent the defendants.
Page 7
"""
    }

    records = parse_transcript_lines(page)

    record = get_record(records, 12)

    assert record["id"] == "p7_l12"
    assert record["pdf_page"] == 7
    assert record["transcript_page"] == 7
    assert record["line"] == 12


def test_original_line_number_is_preserved():
    page = {
        "pdf_page": 7,
        "text": """
1
2
3
11   BY MR. PURCELL:
Page 7
"""
    }

    records = parse_transcript_lines(page)

    record = get_record(records, 11)

    assert record["line"] == 11
    assert record["id"] == "p7_l11"


def test_timestamp_removed():
    page = {
        "pdf_page": 7,
        "text": """
12   Q    Hello there.  01:17
Page 7
"""
    }

    records = parse_transcript_lines(page)

    record = get_record(records, 12)

    assert record["text"] == "Q    Hello there."


def test_transcript_page_detected():
    page = {
        "pdf_page": 7,
        "text": """
11   BY MR. PURCELL:
12   Q    Hello.
Page 7
"""
    }

    records = parse_transcript_lines(page)

    assert records[0]["transcript_page"] == 7