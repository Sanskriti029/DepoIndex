import re
from pypdf import PdfReader


LINE_PATTERN = re.compile(r"^\s*(\d{1,2})\s+(.*)$")
PAGE_PATTERN = re.compile(r"Page\s+(\d+)\s*$")
TIME_PATTERN = re.compile(r"\s+\d{2}:\d{2}\s*$")


def extract_pdf_pages(pdf_path: str):
    """
    Extract raw text from every PDF page.
    """

    reader = PdfReader(pdf_path)

    pages = []

    for pdf_page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "pdf_page": pdf_page_number,
            "text": text
        })

    return pages


def parse_transcript_lines(page):
    """
    Parse numbered transcript lines while preserving
    the original transcript line number.

    The printed transcript page number may occur at
    the bottom of the extracted PDF text.
    """

    pdf_page = page["pdf_page"]
    text = page["text"]

    lines = text.splitlines()

    transcript_page = None
    records = []

    # --------------------------------------------------
    # STEP 1: Find printed transcript page number
    # --------------------------------------------------

    for raw_line in lines:
        page_match = PAGE_PATTERN.search(raw_line.strip())

        if page_match:
            transcript_page = int(page_match.group(1))
            break

    # --------------------------------------------------
    # STEP 2: Parse numbered transcript lines
    # --------------------------------------------------

    for raw_line in lines:

        raw_line = raw_line.rstrip()

        match = LINE_PATTERN.match(raw_line)

        if not match:
            continue

        line_number = int(match.group(1))
        line_text = match.group(2).strip()

        # Remove timestamp such as 01:17
        line_text = TIME_PATTERN.sub("", line_text).strip()

        records.append({
            "id": f"p{transcript_page}_l{line_number}",
            "pdf_page": pdf_page,
            "transcript_page": transcript_page,
            "line": line_number,
            "text": line_text
        })

    return records


if __name__ == "__main__":

    pdf_path = "data/Persis_Yu_Deposition.pdf"

    pages = extract_pdf_pages(pdf_path)

    print(f"Total PDF pages: {len(pages)}")

    # Test PDF pages 7-10
    for page in pages[6:10]:

        records = parse_transcript_lines(page)

        print("\n" + "=" * 70)
        print(f"PDF PAGE: {page['pdf_page']}")
        print("=" * 70)

        for record in records:
            print(
                f"{record['id']}: "
                f"{record['text']}"
            )