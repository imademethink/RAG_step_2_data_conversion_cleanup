from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

documentation_sample1 = "..\\..\\data\\recursive_chunking\\Confluence_documentation.docx"

# 1. Load the .docx file
# This loader automatically extracts text from paragraphs and tables
loader = Docx2txtLoader(documentation_sample1)
data = loader.load()

# 2. Step-by-Step Chunking Setup
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # Target size for each snippet
    chunk_overlap=50,      # Context overlap to prevent cutting thoughts
    separators=["\n\n", "\n", " ", ""] # Priority: Paragraph -> Line -> Word
)

# 3. Execute Splitting
chunks = text_splitter.split_documents(data)

# 4. Show Outcome
print(f"File loaded successfully.")
print(f"Total Chunks Created: {len(chunks)}\n")

for i, chunk in enumerate(chunks[:3]): # Previewing first 3 chunks
    print(f"--- CHUNK #{i+1} ---")
    print(f"Metadata: {chunk.metadata}") # Shows the source file path
    # print(f"Content Preview: {chunk.page_content[:150]}...")
    print(f"Content Preview: {chunk.page_content}...")
    print("-" * 20)

