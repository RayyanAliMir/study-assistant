import os
from dotenv import load_dotenv
from groq import Groq
from rag import build_knowledge_base, retrieve_relevant_chunks

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def summarize_text(notes: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful study assistant. Summarize the student's notes into clear, concise bullet points highlighting the key concepts.",
            },
            {
                "role": "user",
                "content": notes,
            },
        ],
    )
    return response.choices[0].message.content


def answer_from_context(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a study assistant. Answer the student's question "
                    "using ONLY the provided notes below. If the notes don't "
                    "contain the answer, say so honestly instead of guessing.\n\n"
                    f"NOTES:\n{context}"
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    notes = """Photosynthesis converts light energy into chemical energy.

It occurs in chloroplasts, using chlorophyll.

The Calvin cycle uses ATP and NADPH to build glucose from CO2.

Mitochondria are the powerhouse of the cell, producing ATP through respiration."""

    kb = build_knowledge_base(notes, chunk_size=80)
    question = "Where does the Calvin cycle happen?"
    relevant_chunks = retrieve_relevant_chunks(question, kb, top_n=2)

    print("--- Retrieved context ---")
    for c in relevant_chunks:
        print(c)
    print("--------------------------")

    answer = answer_from_context(question, relevant_chunks)
    print(f"Q: {question}")
    print(f"A: {answer}")