from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()

import math


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    return dot_product / (magnitude_a * magnitude_b)

def build_knowledge_base(text: str, chunk_size: int = 500) -> list[dict]:
    chunks = chunk_text(text, chunk_size=chunk_size)
    knowledge_base = []

    for chunk in chunks:
        vector = embed_text(chunk)
        knowledge_base.append({
            "text": chunk,
            "vector": vector
        })

    return knowledge_base

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph == "":
            continue

        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def retrieve_relevant_chunks(question: str, knowledge_base: list[dict], top_n: int = 3) -> list[str]:
    question_vector = embed_text(question)

    scored_chunks = []
    for entry in knowledge_base:
        score = cosine_similarity(question_vector, entry["vector"])
        scored_chunks.append((score, entry["text"]))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    top_chunks = scored_chunks[:top_n]
    return [text for score, text in top_chunks]

if __name__ == "__main__":
    sample = """Photosynthesis converts light energy into chemical energy.

It occurs in chloroplasts, using chlorophyll.

The Calvin cycle uses ATP and NADPH to build glucose from CO2.

Mitochondria are the powerhouse of the cell, producing ATP through respiration."""

    chunks = chunk_text(sample, chunk_size=80)
    kb = []
    for chunk in chunks:
        vector = embed_text(chunk)
        kb.append({"text": chunk, "vector": vector})
    print(f"Knowledge base has {len(kb)} chunks")

    question = "Where does the Calvin cycle happen?"
    relevant = retrieve_relevant_chunks(question, kb, top_n=2)

    print(f"\nQuestion: {question}")
    print("Most relevant chunks:")
    for chunk in relevant:
        print(f"- {chunk}")

