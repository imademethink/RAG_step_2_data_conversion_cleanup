import random
from datetime import datetime, timedelta

services = ["USER-SERVICE", "ORDER-SERVICE", "PAYMENT-SERVICE"]
actions = ["GET /api/v1/resource", "POST /api/v1/create", "PUT /api/v1/update", "DELETE /api/v1/remove"]
statuses = ["200 OK", "201 Created", "404 Not Found", "500 Internal Server Error"]


def generate_logs():
    logs = []
    start_date = datetime(2024, 10, 19, 0, 0, 0)  # A Saturday

    # Generate ~100 logs
    for i in range(100):
        timestamp = start_date + timedelta(seconds=i * 1800)  # Every 30 mins
        service = random.choice(services)
        action = random.choice(actions)
        status = random.choice(statuses)
        log_entry = f"[{timestamp.isoformat()}] {service} | {action} | {status} | req_id={random.randint(1000, 9999)}"
        logs.append(log_entry)

    return "\n".join(logs)


# Create the huge log string
raw_log_data = generate_logs()
with open("demo_logs.txt", "w", encoding="utf-8") as demo_log_file:
    demo_log_file.write(raw_log_data)

# ==========================================================================

def fixed_size_chunking(text, size):
    chunks = []
    # Step-by-step slicing
    for i in range(0, len(text), size):
        chunk = text[i : i + size]
        chunks.append(chunk)
    return chunks

# Define chunk size (e.g., 100 characters per chunk)
CHUNK_SIZE = 100
with open("demo_logs.txt", 'r', encoding='utf-8') as f:
    raw_log_data_read = f.read()

log_chunks = fixed_size_chunking(raw_log_data_read, CHUNK_SIZE)

# --- VISUALIZING THE STEP-BY-STEP OUTCOME ---
print(f"{'STEP':<10} | {'CONTENT EXTRACTED (First 50 chars)'}")
print("-" * 60)

for idx, chunk in enumerate(log_chunks[:5]): # Show first 5 chunks
    # Clean newlines for display purposes
    display_content = chunk.replace('\n', '\\n')[:50]
    print(f"Chunk {idx+1:<5} | {display_content}...")

print("-" * 60)
print(f"Total Chunks Created: {len(log_chunks)}")


# =============================================
# =============================================
# =============================================
# =============================================

import re


def validate_log_chunks(original_text, chunks):
    # Regex to define what a "Complete Log Line" looks like
    # Matches: [YYYY-MM-DDTHH:MM:SS] SERVICE | ACTION | STATUS | req_id=####
    log_pattern = r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\].*?req_id=\d+"

    validation_results = {
        "integrity_passed": True,
        "fragmentation_count": 0,
        "total_chars_original": len(original_text),
        "total_chars_chunks": sum(len(c) for c in chunks),
        "details": []
    }

    for i, chunk in enumerate(chunks):
        # 1. CHECK FOR FRAGMENTS:
        # Does the chunk start or end with a partial line?
        lines = chunk.strip().split('\n')
        is_fragmented = False

        if not re.fullmatch(log_pattern, lines[0]) or not re.fullmatch(log_pattern, lines[-1]):
            is_fragmented = True
            validation_results["fragmentation_count"] += 1

        validation_results["details"].append({
            "chunk_id": i + 1,
            "line_count": len(lines),
            "is_fragmented": is_fragmented
        })

    # 2. DATA LOSS CHECK: Compare character counts
    if validation_results["total_chars_original"] != validation_results["total_chars_chunks"]:
        validation_results["integrity_passed"] = False

    return validation_results


# --- EXECUTION ---
# Using 'raw_log_data' and 'log_chunks' from the previous high-volume log example
report = validate_log_chunks(raw_log_data, log_chunks)

# --- VISUAL OUTPUT ---
print("--- LOG CHUNK VALIDATION REPORT ---")
print(f"Data Loss Check:     {'PASS' if report['integrity_passed'] else 'FAIL'}")
print(f"Fragmentation Rate:  {(report['fragmentation_count'] / len(log_chunks)) * 100:.1f}%")
print(f"Total Chunks:        {len(log_chunks)}")

print("\n--- SAMPLE CHUNK AUDIT ---")
for d in report['details'][:5]:
    status = "⚠️ Fragmented" if d['is_fragmented'] else "✅ Complete"
    print(f"Chunk {d['chunk_id']}: {status} ({d['line_count']} lines found)")


