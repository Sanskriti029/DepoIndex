from flask import Flask, request, jsonify, send_from_directory

from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.index import DepositionIndex


app = Flask(__name__)

PDF_PATH = "data/Persis_Yu_Deposition.pdf"


def load_utterances():
    pages = extract_pdf_pages(PDF_PATH)

    records = []

    for page in pages:
        records.extend(parse_transcript_lines(page))

    return segment_utterances(records)


print("Loading deposition...")
utterances = load_utterances()

print(f"Loaded {len(utterances)} utterances.")

print("Building search index...")
index = DepositionIndex(utterances)

print("Index ready!")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Please provide a search query."
        }), 400

    limit = request.args.get("limit", default=5, type=int)

    results = index.search(query, limit=limit)

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True)