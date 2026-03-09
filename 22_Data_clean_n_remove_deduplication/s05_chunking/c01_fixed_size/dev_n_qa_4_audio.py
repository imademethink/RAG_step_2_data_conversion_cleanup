import tiktoken

# 1. GENERATE DUMMY AUDIO TRANSCRIPT (Weekend Podcast)
transcript = """
[00:00] Speaker 1: Welcome to the Weekend Tech Wrap-up. 
[00:05] Today we discuss microservices and why they fail during peak Saturday traffic.
[00:12] User-Auth service spiked at 14:00 UTC. The latency was over 500ms.
[00:25] Speaker 2: Right, and the Payment gateway timed out shortly after. 
[00:30] We saw a 404 on the /checkout endpoint for nearly twenty minutes...
""" * 20  # Simulating a long transcript

# 2. TOKEN-BASED FIXED-SIZE CHUNKER
def chunk_audio_transcript(text, chunk_size=50, overlap=10):
    encoding = tiktoken.get_encoding("cl100k_base")  # Standard for GPT-4/Llama3 logic
    tokens = encoding.encode(text)

    chunks = []
    # Using overlap to ensure we don't cut a word in half across chunks
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i: i + chunk_size]
        chunks.append(encoding.decode(chunk_tokens))
    return chunks


# EXECUTION
audio_chunks = chunk_audio_transcript(transcript, chunk_size=40, overlap=5)

# --- OUTCOME ---
print(f"Total Chunks Created: {len(audio_chunks)}")
print(f"--- SAMPLE CHUNK 1 ---\n{audio_chunks[0]}")
print(f"\n--- SAMPLE CHUNK 2 (With Overlap) ---\n{audio_chunks[1]}")

# =================================
# =================================
# =================================

def validate_audio_chunks(chunks, limit):
    encoding = tiktoken.get_encoding("cl100k_base")

    for i, chunk in enumerate(chunks):
        token_count = len(encoding.encode(chunk))
        # Validation: Every chunk must be <= limit
        status = "✅" if token_count <= limit else "❌ OVER LIMIT"

        # Audio Logic: Check if a timestamp was cut (e.g., "[00:" at the end)
        timestamp_cut = chunk.strip().endswith("[") or chunk.strip().endswith(":")
        warning = "⚠️ Timestamp Cut!" if timestamp_cut else ""

        print(f"Chunk {i + 1}: {token_count} tokens | {status} {warning}")


# Run Validation
validate_audio_chunks(chunks=audio_chunks, limit=40)



