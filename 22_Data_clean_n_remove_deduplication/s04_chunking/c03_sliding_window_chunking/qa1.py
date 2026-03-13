import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. SETUP: Configuration for Legal Documents
PDF_PATH = "..\\..\\data\\sliding_window\\GDPR.pdf"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_pdf_text(path):
    """Extracts raw text from PDF."""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# 2. CHUNKING: Implementation with "Strict" settings
# strip_whitespace=False ensures our validation comparison doesn't fail on spaces
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ".", " ", ""],
    strip_whitespace=False
)


def run_implementation():
    if not os.path.exists(PDF_PATH):
        print(f"Error: {PDF_PATH} not found.")
        return

    print(f"--- Processing: {PDF_PATH} ---")
    raw_text = get_pdf_text(PDF_PATH)
    chunks = text_splitter.split_text(raw_text)

    print(f"Total Chunks Created: {len(chunks)}\n")

    # 3. AUTOMATED VALIDATION: Fuzzy Matching Logic
    print(f"{'Boundary':<15} | {'Status':<10} | {'Match Content'}")
    print("-" * 65)

    passes = 0
    for i in range(len(chunks) - 1):
        # We take a 50-character sample from the end of Chunk N
        # and check if it exists anywhere in the start of Chunk N+1
        tail_sample = chunks[i][-50:].strip()
        head_context = chunks[i + 1][:CHUNK_OVERLAP + 50]  # Search window

        is_valid = tail_sample in head_context
        status = "✅ PASS" if is_valid else "❌ FAIL"
        if is_valid: passes += 1

        sample_display = tail_sample.replace('\n', ' ')[:30]
        print(f"Chunk {i + 1}->{i + 2:<6} | {status:<10} | ...{sample_display}...")

    print("-" * 65)
    print(f"Validation Summary: {passes}/{len(chunks) - 1} boundaries intact.")


if __name__ == "__main__":
    run_implementation()
