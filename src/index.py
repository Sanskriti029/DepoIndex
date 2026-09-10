import re
from typing import List, Dict


class DepositionIndex:
    """
    Keyword-based search index for deposition utterances.

    Ranking considers:
    - Number of unique query terms matched
    - Frequency of matched terms
    - Exact phrase matches
    """

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but",
        "is", "are", "was", "were", "to", "of",
        "in", "on", "for", "with", "at", "by",
        "from", "as", "it", "this", "that",
        "i", "you", "he", "she", "we", "they",
        "do", "did", "does", "have", "has", "had",
        "be", "been", "am"
    }

    def __init__(self, utterances: List[Dict]):
        self.utterances = utterances
        self.index = {}
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [
            word for word in words
            if word not in self.STOP_WORDS
        ]

    def _build_index(self):
        for position, utterance in enumerate(self.utterances):

            tokens = self._tokenize(
                utterance.get("text", "")
            )

            for token in set(tokens):

                if token not in self.index:
                    self.index[token] = []

                self.index[token].append(position)

    def search(self, query: str, limit: int = 10) -> List[Dict]:

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        query_unique = set(query_tokens)

        scores = {}
        matched_terms = {}

        for token in query_unique:

            positions = self.index.get(token, [])

            for position in positions:

                utterance = self.utterances[position]

                text = utterance.get("text", "")

                document_tokens = self._tokenize(text)

                frequency = document_tokens.count(token)

                # Base score for matching a unique query term
                score = 3

                # Small bonus for repeated occurrences
                score += min(frequency, 3)

                scores[position] = (
                    scores.get(position, 0) + score
                )

                if position not in matched_terms:
                    matched_terms[position] = []

                matched_terms[position].append(token)

        # Exact phrase bonus
        normalized_query = " ".join(query_tokens)

        for position in list(scores.keys()):

            text_tokens = self._tokenize(
                self.utterances[position].get("text", "")
            )

            normalized_text = " ".join(text_tokens)

            if normalized_query in normalized_text:
                scores[position] += 5

        ranked_positions = sorted(
            scores,
            key=lambda position: (
                -scores[position],
                position
            )
        )

        results = []

        for position in ranked_positions[:limit]:

            utterance = self.utterances[position]

            results.append({
                "utterance_id": utterance["utterance_id"],
                "speaker": utterance["speaker"],
                "score": scores[position],
                "matched_terms": sorted(
                    matched_terms[position]
                ),
                "start": utterance["start"],
                "end": utterance["end"],
                "text": utterance["text"],
                "source_lines": utterance["source_lines"]
            })

        return results