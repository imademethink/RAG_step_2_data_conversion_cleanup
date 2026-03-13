import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

documentation_sample1 = "..\\data\\recursive_chunking\\Confluence_documentation.pdf"
file_ollama_key = "..\\data\\ollama_api_key_file.txt"
API_KEY = open(file_ollama_key).read()
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"} # only needed for remote model
BASE_URL_REMOTE_MODEL = "https://ollama.com"
BASE_URL_LOCAL_MODEL = "http://localhost:11434" # make sure to run locally installed ollama and required model is pulled
EMBEDDING_MODEL = "nomic-embed-text"
os.environ["OLLAMA_HOST"] = BASE_URL_LOCAL_MODEL
os.environ["OLLAMA_API_KEY"] = API_KEY
os.environ["OPENAI_API_KEY"] = "not-used"

# STEP 1: Load the PDF
loader = PyPDFLoader(documentation_sample1)
pages = loader.load()
full_text = " ".join([page.page_content for page in pages])

# STEP 2: Initialize Remote Ollama Embeddings
# 'nomic-embed-text' is highly recommended for semantic tasks
embeddings_llm = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=BASE_URL_LOCAL_MODEL)

# STEP 3: Initialize Semantic Chunker
# split text based on semantic shifts detected by Ollama model
text_splitter = SemanticChunker(embeddings=embeddings_llm,
                                breakpoint_threshold_type="percentile",
                                breakpoint_threshold_amount=95)

# STEP 4: Perform Chunking
chunks = text_splitter.create_documents([full_text])

# STEP 5: Show Outcome
print(f"Total semantic chunks created: {len(chunks)}")

for i, chunk in enumerate(chunks[:len(chunks) - 1]):
    print(f"\n--- CHUNK {i+1} ---")
    print(chunk.page_content[:600] + "...")
    print("-" * 40)
