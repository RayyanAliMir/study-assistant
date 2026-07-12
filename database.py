import sqlite3
from datetime import datetime

DB_PATH = "study_assistant.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_question(question: str, answer: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO questions (question, answer, timestamp) VALUES (?, ?, ?)",
        (question, answer, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_questions() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, timestamp FROM questions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {"question": row[0], "answer": row[1], "timestamp": row[2]}
        for row in rows
    ]

def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM questions
        GROUP BY day
        ORDER BY day DESC
    """)
    by_day = cursor.fetchall()

    conn.close()

    return {
        "total_questions": total,
        "by_day": [{"day": row[0], "count": row[1]} for row in by_day]
    }

if __name__ == "__main__":
    init_db()
    log_question("What is RAG?", "Retrieval-Augmented Generation")

    all_q = get_all_questions()
    print(f"Total logged: {len(all_q)}")
    for q in all_q:
        print(f"- {q['question']} ({q['timestamp']})")

    stats = get_stats()
    print(f"\nStats: {stats}")