
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

documentation_sample1 = "..\\..\\data\\recursive_chunking\\Confluence_documentation.docx"

# 1. Setup & Data Loading
chunk_size = 500
overlap = 50
loader = Docx2txtLoader(documentation_sample1)
raw_docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=overlap,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(raw_docs)

print(f"--- VALIDATING {len(chunks)} CHUNKS ---\n")

# 2. Validation: Chunk Size Compliance
size_errors = 0
for i, chunk in enumerate(chunks):
    if len(chunk.page_content) > chunk_size:
        print(f"❌ Size Error: Chunk {i} is {len(chunk.page_content)} chars.")
        size_errors += 1
if size_errors == 0:
    print("✅ All chunks within size limits.")

# 3. Validation: Content Integrity (Keyword Check)
missing_words = []
# Rejoin all chunk text into one string for searching
all_chunk_text = "".join([c.page_content for c in chunks])
for word in ["Inventory", "Payment", "Notification", "Kafka"]:
    if word not in all_chunk_text:
        missing_words.append(word)

if not missing_words:
    print("✅ Content Integrity: All core technical terms preserved.")
else:
    print(f"❌ Content Error: Missing words: {missing_words}")

# 4. Validation: Overlap Consistency
if len(chunks) > 1:
    # Get last 20 chars of Chunk 0
    context_tail = chunks[0].page_content[-20:]
    # Check if they exist in Chunk 1
    if context_tail in chunks[1].page_content:
        print("✅ Overlap Consistency: Context flows correctly between chunks.")
    else:
        print("⚠️ Overlap Warning: Context tail of Chunk 0 not found in Chunk 1.")

# 5. Validation: Table Preservation
table_issues = 0
for i, chunk in enumerate(chunks):
    content = chunk.page_content
    if "|" in content and content.count("|") < 2:
        print(f"⚠️ Table Warning: Broken row detected in Chunk {i}")
        table_issues += 1
if table_issues == 0:
    print("✅ Table Preservation: No isolated table pipes found.")

print("\n--- VALIDATION COMPLETE ---")


