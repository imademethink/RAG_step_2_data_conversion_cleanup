from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter

gdpr_documentation_sample1 = "..\\..\\data\\sliding_window\\GDPR.pdf"

# 1. LOAD: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# 2. CHUNK: Define the sliding window parameters
# We use a 1000 character window with a 200 character (20%) overlap
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", ".", " ", ""] # Order of priority for splitting
)
# strict_splitter = CharacterTextSplitter(
#     separator="\n", # Split by line only
#     chunk_size=1000,
#     chunk_overlap=200,
#     strip_whitespace=False # CRITICAL for validation tests
# )

# 3. EXECUTE: Perform the split
raw_text = extract_text_from_pdf(gdpr_documentation_sample1)
chunks = text_splitter.split_text(raw_text)
# chunks = strict_splitter.split_text(raw_text)

# 4. OUTCOME: Display the results step-by-step
for i, chunk in enumerate(chunks[:3]):  # Showing first 3 for brevity
    print(f"--- CHUNK {i+1} ---")
    print(chunk)
    if i < len(chunks) - 1:
        # Highlighting the overlap for visual clarity
        overlap_text = chunk[-200:]
        print(f"\n[!] OVERLAP STARTING NEXT CHUNK: {overlap_text[:50]}...")
    print("\n")


