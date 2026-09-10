from src.index import DepositionIndex


def test_search_finds_matching_utterance():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 1, "line": 1},
            "end": {"page": 1, "line": 2},
            "text": "Did you discuss the company?",
            "source_lines": ["p1_l1", "p1_l2"]
        },
        {
            "utterance_id": "u0002",
            "speaker": "A",
            "start": {"page": 1, "line": 3},
            "end": {"page": 1, "line": 4},
            "text": "Yes, I discussed the payment.",
            "source_lines": ["p1_l3", "p1_l4"]
        }
    ]

    index = DepositionIndex(utterances)

    results = index.search("company")

    assert len(results) == 1
    assert results[0]["utterance_id"] == "u0001"


def test_multiple_keywords_get_higher_score():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 1, "line": 1},
            "end": {"page": 1, "line": 1},
            "text": "Tell me about the company.",
            "source_lines": ["p1_l1"]
        },
        {
            "utterance_id": "u0002",
            "speaker": "A",
            "start": {"page": 1, "line": 2},
            "end": {"page": 1, "line": 2},
            "text": "The company made a payment.",
            "source_lines": ["p1_l2"]
        }
    ]

    index = DepositionIndex(utterances)

    results = index.search("company payment")

    assert results[0]["utterance_id"] == "u0002"
    assert results[0]["score"] > 0
    assert set(results[0]["matched_terms"]) == {"company", "payment"}


def test_search_returns_empty_for_unknown_word():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "Q",
            "start": {"page": 1, "line": 1},
            "end": {"page": 1, "line": 1},
            "text": "Tell me about the company.",
            "source_lines": ["p1_l1"]
        }
    ]

    index = DepositionIndex(utterances)

    results = index.search("xyzabc")

    assert results == []


def test_search_preserves_provenance():

    utterances = [
        {
            "utterance_id": "u0001",
            "speaker": "A",
            "start": {"page": 42, "line": 12},
            "end": {"page": 42, "line": 16},
            "text": "Yes, I remember the payment.",
            "source_lines": [
                "p42_l12",
                "p42_l13",
                "p42_l14",
                "p42_l15",
                "p42_l16"
            ]
        }
    ]

    index = DepositionIndex(utterances)

    results = index.search("payment")

    assert results[0]["start"] == {
        "page": 42,
        "line": 12
    }

    assert results[0]["end"] == {
        "page": 42,
        "line": 16
    }

    assert results[0]["source_lines"] == [
        "p42_l12",
        "p42_l13",
        "p42_l14",
        "p42_l15",
        "p42_l16"
    ]