from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.index import DepositionIndex


PDF_PATH = "data/Persis_Yu_Deposition.pdf"


def load_utterances():
    """Extract and segment the deposition."""

    pages = extract_pdf_pages(PDF_PATH)

    records = []

    for page in pages:
        records.extend(parse_transcript_lines(page))

    utterances = segment_utterances(records)

    return utterances


def display_results(results):
    """Display search results in a readable format."""

    if not results:
        print("\nNo matching results found.")
        return

    print(f"\nFound {len(results)} result(s):\n")

    for number, result in enumerate(results, start=1):

        start = result["start"]
        end = result["end"]

        print("=" * 70)

        print(f"Result #{number}")
        print(f"Utterance: {result['utterance_id']}")
        print(f"Speaker:   {result['speaker']}")
        print(f"Score:     {result['score']}")

        print(
            f"Location:  Page {start['page']}, "
            f"Line {start['line']} "
            f"→ Page {end['page']}, "
            f"Line {end['line']}"
        )

        print("\nText:")
        print(result["text"])

    print("=" * 70)


def main():

    print("Loading deposition...")

    utterances = load_utterances()

    print(f"Loaded {len(utterances)} utterances.")

    print("Building search index...")

    index = DepositionIndex(utterances)

    print("Index ready!")

    print("\nDepoIndex Search")
    print("Type 'exit' to quit.")

    while True:

        query = input("\nSearch: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            print("Please enter a search query.")
            continue

        results = index.search(query, limit=5)

        display_results(results)


if __name__ == "__main__":
    main()