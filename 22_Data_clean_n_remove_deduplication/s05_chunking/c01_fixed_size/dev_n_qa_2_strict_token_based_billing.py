import random
from datetime import datetime, timedelta


def generate_weekend_logs():
    services = ["AUTH-SRV", "CART-SRV", "PAY-SRV"]
    methods = ["POST", "GET", "PUT", "DELETE"]
    endpoints = ["/login", "/checkout", "/validate", "/refund"]

    logs = []
    current_time = datetime(2024, 11, 23, 0, 0, 0)  # Start Saturday
    for _ in range(150):
        current_time += timedelta(minutes=random.randint(2, 45))
        log = f"[{current_time}] {random.choice(services)} {random.choice(methods)} {random.choice(endpoints)} 200 SUCCESS\n"
        logs.append(log)
    return "".join(logs)

# ==============================================

raw_logs = generate_weekend_logs()

from transformers import AutoTokenizer
import os

# 1. SETUP: Specify your Ollama Cloud model and its base tokenizer
# For DeepSeek-V3 cloud, use a compatible tokenizer identifier from Hugging Face
MODEL_NAME = "deepseek-v3.1:671b-cloud"
TOKENIZER_ID = "deepseek-ai/DeepSeek-V3"
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID)
file_ollama_key = "..\\..\\data\\ollama_api_key_file.txt"
API_KEY = open(file_ollama_key).read()
BASE_URL = "https://ollama.com"
os.environ["OLLAMA_HOST"] = BASE_URL
os.environ["OLLAMA_API_KEY"] = API_KEY
os.environ["OPENAI_API_KEY"] = "not-used"

def ollama_token_chunking(text, chunk_size=50):
    # Step 1: Convert text to token IDs
    tokens = tokenizer.encode(text, add_special_tokens=False)

    chunks = []
    # Step 2: Slice token list into segments of fixed size
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i: i + chunk_size]
        # Step 3: Decode back to text for the API call
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks, tokens


# EXECUTION
CHUNK_LIMIT = 40  # Set your budget-safe token limit
chunks, all_tokens = ollama_token_chunking(raw_logs, chunk_size=CHUNK_LIMIT)

# --- OUTCOME VISUALIZATION ---
print(f"Total Tokens Processed: {len(all_tokens)}")
print(f"Total Budgeted Chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks[:3]):
    print(f"--- CHUNK {i + 1} ---")
    print(chunk)







# ===================================================================
# ===================================================================
# ===================================================================
# ===================================================================
# ===================================================================


from transformers import AutoTokenizer

# Configuration (Matching your previous setup)
TOKENIZER_ID = "deepseek-ai/DeepSeek-V3"
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID)
CHUNK_LIMIT = 40


def validate_chunks(original_text, chunks, expected_size):
    results = {
        "token_limit_passed": True,
        "integrity_passed": True,
        "individual_reports": []
    }

    reconstructed_text = ""

    for i, chunk in enumerate(chunks):
        # 1. VALIDATE SIZE: Count tokens in this specific chunk
        actual_tokens = tokenizer.encode(chunk, add_special_tokens=False)
        size_check = len(actual_tokens) <= expected_size

        # 2. TRACK RECONSTRUCTION: Add to string to check for data loss
        reconstructed_text += chunk

        report = {
            "chunk_id": i + 1,
            "actual_size": len(actual_tokens),
            "status": "✅" if size_check else "❌"
        }
        results["individual_reports"].append(report)

        if not size_check:
            results["token_limit_passed"] = False

    # 3. INTEGRITY CHECK: Compare original vs reconstructed (ignoring whitespace)
    if original_text.replace(" ", "") != reconstructed_text.replace(" ", ""):
        results["integrity_passed"] = False

    return results


# --- EXECUTION ---
# Assuming 'raw_logs' and 'chunks' exist from the previous step
validation_results = validate_chunks(raw_logs, chunks, CHUNK_LIMIT)

# --- VISUAL OUTPUT ---
print(f"--- AUTO-VALIDATION REPORT ---")
print(f"Token Size Compliance: {'PASS' if validation_results['token_limit_passed'] else 'FAIL'}")
print(f"Data Integrity:       {'PASS' if validation_results['integrity_passed'] else 'FAIL'}")
print(f"\nSample Breakdown:")
for r in validation_results['individual_reports'][:5]:  # Show first 5
    print(f"ID: {r['chunk_id']} | Tokens: {r['actual_size']} | {r['status']}")



