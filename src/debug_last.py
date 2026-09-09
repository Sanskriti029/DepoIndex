from src.extraction import extract_pdf_pages, parse_transcript_lines
from src.utterances import segment_utterances

pages = extract_pdf_pages("data/Persis_Yu_Deposition.pdf")

all_records = []

for page in pages:
    all_records.extend(parse_transcript_lines(page))

utterances = segment_utterances(all_records)

print("TOTAL UTTERANCES:", len(utterances))

print("\nLAST UTTERANCE:")
print(utterances[-1])

print("\nLAST 10 SOURCE RECORDS:")
for record in all_records[-10:]:
    print(record)