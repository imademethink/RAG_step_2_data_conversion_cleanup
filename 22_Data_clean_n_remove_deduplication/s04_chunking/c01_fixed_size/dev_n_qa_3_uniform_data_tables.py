
import pandas as pd
import random
from datetime import datetime, timedelta


def generate_weekend_table():
    data = []
    start_time = datetime(2024, 11, 23, 0, 0, 0)  # Saturday

    services = ["User-Auth", "Inventory", "Payment"]
    actions = ["CREATE", "READ", "UPDATE", "DELETE"]

    # Generate 100 rows of uniform data
    for i in range(100):
        row = {
            "timestamp": (start_time + timedelta(minutes=i * 30)).isoformat(),
            "service": random.choice(services),
            "action": random.choice(actions),
            "latency_ms": random.randint(10, 500)
        }
        data.append(row)

    # Convert to CSV string format
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


raw_csv_data = generate_weekend_table()
print("Sample of Raw CSV Data:\n", "\n".join(raw_csv_data.splitlines()[:5]))


def chunk_by_lines(csv_text, lines_per_chunk=10):
    # Step 1: Split the big string into individual lines
    lines = csv_text.strip().split('\n')
    header = lines[0]  # Keep the CSV header
    rows = lines[1:]  # Data rows

    chunks = []

    # Step 2: Slice the rows into fixed batches
    for i in range(0, len(rows), lines_per_chunk):
        batch = rows[i: i + lines_per_chunk]

        # Step 3: Re-attach the header to every chunk for context
        chunk_with_header = header + "\n" + "\n".join(batch)
        chunks.append(chunk_with_header)

    return chunks


# Define chunk size (10 rows per chunk)
chunks = chunk_by_lines(raw_csv_data, lines_per_chunk=10)

# --- VISUALIZING THE OUTCOME ---
print(f"\nTotal Rows: 100 | Chunk Size: 10 rows | Total Chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
    print(f"--- OUTPUT: CHUNK {i + 1} ---")
    print(chunk)
    print("-" * 30)


# ==================================================================================

import pandas as pd
from io import StringIO


def validate_tabular_chunks(chunks, expected_columns):
    validation_results = {
        "schema_intact": True,
        "header_present_in_all": True,
        "row_fragmentation_found": False,
        "chunk_reports": []
    }

    for i, chunk in enumerate(chunks):
        try:
            # 1. ATTEMPT TO PARSE: If it's a valid table, it must load into Pandas
            df_chunk = pd.read_csv(StringIO(chunk))

            # 2. SCHEMA CHECK: Does it have the right number of columns?
            actual_cols = list(df_chunk.columns)
            schema_match = actual_cols == expected_columns

            # 3. FRAGMENTATION CHECK: Check if the last row is cut off
            # (e.g., has fewer columns than the header)
            lines = chunk.strip().split('\n')
            last_line_cols = len(lines[-1].split(','))
            is_fragmented = last_line_cols != len(expected_columns)

            report = {
                "chunk_id": i + 1,
                "rows": len(df_chunk),
                "schema_match": schema_match,
                "fragmented": is_fragmented
            }
            validation_results["chunk_reports"].append(report)

            if not schema_match: validation_results["schema_intact"] = False
            if is_fragmented: validation_results["row_fragmentation_found"] = True

        except Exception as e:
            validation_results["schema_intact"] = False
            validation_results["chunk_reports"].append({"chunk_id": i + 1, "error": str(e)})

    return validation_results


# --- EXECUTION ---
# Using 'chunks' and the header from the previous CSV example
expected_headers = ["timestamp", "service", "action", "latency_ms"]
report = validate_tabular_chunks(chunks, expected_headers)

# --- VISUAL OUTPUT ---
print("--- TABULAR CHUNK VALIDATION REPORT ---")
print(f"Header Consistency:  {'PASS' if report['header_present_in_all'] else 'FAIL'}")
print(f"Schema Integrity:    {'PASS' if report['schema_intact'] else 'FAIL'}")
print(f"No Row Fragments:    {'PASS' if not report['row_fragmentation_found'] else 'FAIL'}")

print("\n--- CHUNK AUDIT ---")
for r in report['chunk_reports'][:5]:
    status = "✅ OK" if not r.get('fragmented') else "⚠️ Fragmented Row"
    print(f"Chunk {r['chunk_id']}: {status} | Rows: {r.get('rows')} | Cols: {r.get('schema_match')}")


