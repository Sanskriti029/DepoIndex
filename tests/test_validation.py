from src.validation import validate_utterances


def test_valid_utterances():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 7, "line": 12},
            "end": {"page": 7, "line": 15},
            "text": "Question",
            "source_lines": ["p7_l12", "p7_l13", "p7_l14", "p7_l15"]
        }
    ]

    issues = validate_utterances(utterances)

    assert issues == []


def test_invalid_start_end():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 8, "line": 5},
            "end": {"page": 7, "line": 10},
            "text": "Question",
            "source_lines": ["p8_l5"]
        }
    ]

    issues = validate_utterances(utterances)

    assert any("ordering" in issue for issue in issues)


def test_missing_source_lines():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 7, "line": 5},
            "end": {"page": 7, "line": 5},
            "text": "Question",
            "source_lines": []
        }
    ]

    issues = validate_utterances(utterances)

    assert any("source lines" in issue for issue in issues)