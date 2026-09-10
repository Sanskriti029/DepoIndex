from src import utterances
from src.utterances import segment_utterances


def test_continuation_lines_are_grouped():

    records = [
        {
            "id": "p7_l12",
            "transcript_page": 7,
            "line": 12,
            "text": "Q    Good afternoon, Ms. Yu."
        },
        {
            "id": "p7_l13",
            "transcript_page": 7,
            "line": 13,
            "text": "I represent the defendants."
        },
        {
            "id": "p7_l14",
            "transcript_page": 7,
            "line": 14,
            "text": "We will hopefully get you out soon."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 1

    utterance = utterances[0]

    assert utterance["speaker"] == "Q"

    assert utterance["start"] == {
        "page": 7,
        "line": 12
    }

    assert utterance["end"] == {
        "page": 7,
        "line": 14
    }

    assert len(utterance["source_lines"]) == 3


def test_new_speaker_creates_new_utterance():

    records = [
        {
            "id": "p7_l12",
            "transcript_page": 7,
            "line": 12,
            "text": "Q    Have you worked here before?"
        },
        {
            "id": "p7_l13",
            "transcript_page": 7,
            "line": 13,
            "text": "A    No, I have not."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 2

    assert utterances[0]["speaker"] == "Q"
    assert utterances[1]["speaker"] == "A"


def test_cross_page_utterance():

    records = [
        {
            "id": "p7_l24",
            "transcript_page": 7,
            "line": 24,
            "text": "Q    I want to ask you about"
        },
        {
            "id": "p7_l25",
            "transcript_page": 7,
            "line": 25,
            "text": "the history of the school."
        },
        {
            "id": "p8_l1",
            "transcript_page": 8,
            "line": 1,
            "text": "It is important for this case."
        },
        {
            "id": "p8_l2",
            "transcript_page": 8,
            "line": 2,
            "text": "A    Yes."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 2

    first = utterances[0]

    assert first["start"] == {
        "page": 7,
        "line": 24
    }

    assert first["end"] == {
        "page": 8,
        "line": 1
    }

    assert first["source_lines"] == [
        "p7_l24",
        "p7_l25",
        "p8_l1"
    ]
    
def test_words_starting_with_q_or_a_are_not_speakers():

    records = [
        {
            "id": "p7_l12",
            "transcript_page": 7,
            "line": 12,
            "text": "Q    Have you ever had your deposition taken before?"
        },
        {
            "id": "p7_l13",
            "transcript_page": 7,
            "line": 13,
            "text": "At the beginning of a deposition, I always make sure"
        },
        {
            "id": "p7_l14",
            "transcript_page": 7,
            "line": 14,
            "text": "that somebody knows how the process works."
        },
        {
            "id": "p7_l15",
            "transcript_page": 7,
            "line": 15,
            "text": "A    I have not."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 2

    assert utterances[0]["speaker"] == "Q"
    assert utterances[0]["start"]["line"] == 12
    assert utterances[0]["end"]["line"] == 14

    assert utterances[1]["speaker"] == "A"
    assert utterances[1]["start"]["line"] == 15   
    
def test_words_starting_with_q_or_a_are_not_speakers():

    records = [
        {
            "id": "p7_l12",
            "transcript_page": 7,
            "line": 12,
            "text": "Q    Have you ever had your deposition taken before?"
        },
        {
            "id": "p7_l13",
            "transcript_page": 7,
            "line": 13,
            "text": "At the beginning of a deposition, I always make sure"
        },
        {
            "id": "p7_l14",
            "transcript_page": 7,
            "line": 14,
            "text": "that somebody knows how the process works."
        },
        {
            "id": "p7_l15",
            "transcript_page": 7,
            "line": 15,
            "text": "A    I have not."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 2

    assert utterances[0]["speaker"] == "Q"
    assert utterances[0]["start"]["line"] == 12
    assert utterances[0]["end"]["line"] == 14

    assert utterances[1]["speaker"] == "A"
    assert utterances[1]["start"]["line"] == 15


def test_reporter_and_witness_are_separate():

    records = [
        {
            "id": "p14_l25",
            "pdf_page": 14,
            "transcript_page": 14,
            "line": 25,
            "text": "THE REPORTER: What was -- income what payment?"
        },
        {
            "id": "p15_l1",
            "pdf_page": 15,
            "transcript_page": 15,
            "line": 1,
            "text": "THE WITNESS: Income-driven repayment rules."
        }
    ]

    utterances = segment_utterances(records)

    assert len(utterances) == 2
    assert utterances[0]["speaker"] == "REPORTER"
    assert utterances[1]["speaker"] == "WITNESS"