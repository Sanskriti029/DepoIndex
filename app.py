from flask import Flask, request, jsonify, send_from_directory
import os
from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances
from src.index import DepositionIndex

import json

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

@app.route("/topics")
def get_topics():
    try:
        with open("outputs/topic_index.json", "r", encoding="utf-8") as f:
            topics = json.load(f)

        return jsonify(topics)

    except Exception as e:
        return jsonify({
            "error": f"Could not load topic index: {str(e)}"
        }), 500
@app.route("/topic/<topic_id>/source")
def get_topic_source(topic_id):
    try:
        with open("outputs/topic_index.json", "r", encoding="utf-8") as f:
            topics = json.load(f)

        topic = next(
            (t for t in topics if t.get("topic_id") == topic_id),
            None
        )

        if topic is None:
            return jsonify({
                "error": f"Topic {topic_id} not found."
            }), 404

        start_utterance = topic["utterance_start"]
        end_utterance = topic["utterance_end"]

        selected = []

        collecting = False

        for utterance in utterances:

            if utterance["utterance_id"] == start_utterance:
                collecting = True

            if collecting:
                selected.append({
                    "utterance_id": utterance["utterance_id"],
                    "speaker": utterance["speaker"],
                    "start": utterance["start"],
                    "end": utterance["end"],
                    "text": utterance["text"],
                    "source_lines": utterance.get("source_lines", [])
                })

            if utterance["utterance_id"] == end_utterance:
                break

        return jsonify({
            "topic_id": topic["topic_id"],
            "topic": topic["topic"],
            "start": topic["start"],
            "end": topic["end"],
            "utterances": selected
        })

    except Exception as e:
        return jsonify({
            "error": f"Could not load topic source: {str(e)}"
        }), 500
        
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)