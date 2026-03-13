import os
from deepeval.synthesizer import Synthesizer
from deepeval.models.embedding_models import OllamaEmbeddingModel
from deepeval.models.llms import OllamaModel
from deepeval.metrics import ContextualRecallMetric
from deepeval.test_case import LLMTestCase
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch

# --- 1. CONFIGURATION ---
documentation_sample1 = "..\\data\\recursive_chunking\\Confluence_documentation.pdf"
BASE_URL_LOCAL_MODEL = "http://localhost:11434" # make sure to run locally installed ollama and required model is pulled
BASE_URL_REMOTE_MODEL = "https://ollama.com"
EMBEDDING_MODEL = "nomic-embed-text"
# LLM_MODEL = "mistral-large-3:675b-cloud"
LLM_MODEL = "gpt-oss:120b-cloud"
file_ollama_key = "..\\data\\ollama_api_key_file.txt"
API_KEY = open(file_ollama_key).read()
os.environ["OLLAMA_HOST"] = BASE_URL_LOCAL_MODEL
os.environ["OLLAMA_API_KEY"] = API_KEY
os.environ["OPENAI_API_KEY"] = "not-used"

OLLAMA_URL = "http://localhost:11434"
# Using your specific gpt-oss model for generation
my_llm = OllamaModel(model="gpt-oss:120b-cloud", base_url="https://ollama.com")
# Using nomic for embeddings
my_embedder = OllamaEmbeddingModel(model="nomic-embed-text", base_url="http://localhost:11434")

# --- 2. DYNAMIC SYNTHESIS FROM CHUNKS ---
# Step A: Create semantic chunks first to ensure 'contexts' aren't empty
loader = PyPDFLoader(documentation_sample1)
docs = loader.load()
lc_embeds = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
splitter = SemanticChunker(lc_embeds, breakpoint_threshold_type="percentile")
semantic_chunks = splitter.create_documents([" ".join([d.page_content for d in docs])])

# Step B: Generate Goldens using Ollama objects directly
synthesizer = Synthesizer(model=my_llm)
contexts = [[c.page_content] for c in semantic_chunks[:5]]

print("🪄 Generating Goldens using Ollama LLM and Embeddings...")
goldens = synthesizer.generate_goldens_from_contexts(
    contexts=contexts,
    include_expected_output=True,
    max_goldens_per_context=1
)

# --- 3. AUTOMATED VALIDATION ---
# Create a retriever from your semantic chunks
vectorstore = DocArrayInMemorySearch.from_documents(semantic_chunks, lc_embeds)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
recall_metric = ContextualRecallMetric(threshold=0.7, model=my_llm)

for i, golden in enumerate(goldens):
    retrieved_docs = retriever.invoke(golden.input)
    test_case = LLMTestCase(
        input=golden.input,
        actual_output="N/A",
        retrieval_context=[d.page_content for d in retrieved_docs],
        expected_output=golden.expected_output
    )
    recall_metric.measure(test_case)
    print(f"\n[Q {i+1}]: {golden.input}\n[RECALL]: {recall_metric.score}")
