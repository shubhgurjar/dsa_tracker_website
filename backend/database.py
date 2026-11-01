import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.seed_data import DATA_STRUCTURES, ALGORITHMS, SAMPLE_PROBLEMS

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dsa_tracker.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Concepts table (Data Structures & Algorithms)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL, -- 'data_structure' or 'algorithm'
        name TEXT NOT NULL UNIQUE,
        category TEXT,
        description TEXT,
        status TEXT DEFAULT 'Not Started', -- 'Not Started', 'In Progress', 'Mastered'
        confidence INTEGER DEFAULT 1, -- 1 to 5
        key_notes TEXT DEFAULT '',
        cheat_sheet TEXT DEFAULT '',
        last_revised_date TEXT,
        revision_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Problems table (LeetCode problems)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        leetcode_number INTEGER,
        problem_url TEXT,
        difficulty TEXT NOT NULL, -- 'Easy', 'Medium', 'Hard'
        data_structure TEXT,
        algorithm TEXT,
        pattern TEXT,
        status TEXT DEFAULT 'Solved', -- 'Solved', 'Need Revision', 'Bookmarked'
        solved_date TEXT NOT NULL,
        last_revised_date TEXT NOT NULL,
        revision_count INTEGER DEFAULT 0,
        time_complexity TEXT DEFAULT '',
        space_complexity TEXT DEFAULT '',
        approach_notes TEXT DEFAULT '',
        code_snippet TEXT DEFAULT '',
        starred INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Revision logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS revision_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_type TEXT NOT NULL, -- 'problem' or 'concept'
        item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        revised_date TEXT NOT NULL,
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # LeetCode stats cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leetcode_stats_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        total_solved INTEGER DEFAULT 0,
        easy_solved INTEGER DEFAULT 0,
        medium_solved INTEGER DEFAULT 0,
        hard_solved INTEGER DEFAULT 0,
        ranking INTEGER DEFAULT 0,
        acceptance_rate REAL DEFAULT 0.0,
        last_synced_at TEXT
    );
    """)

    # Flashcards table for dedicated topic pages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        tag TEXT DEFAULT 'Pattern',
        content TEXT NOT NULL,
        last_revised_date TEXT NOT NULL,
        revision_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Seed concepts if empty
    cursor.execute("SELECT COUNT(*) FROM concepts")
    concept_count = cursor.fetchone()[0]

    if concept_count == 0:
        for ds in DATA_STRUCTURES:
            cursor.execute("""
                INSERT INTO concepts (type, name, category, description, cheat_sheet, status, confidence, last_revised_date, revision_count)
                VALUES ('data_structure', ?, ?, '', '', 'Not Started', 1, ?, 0)
            """, (ds["name"], ds["category"], datetime.now().strftime("%Y-%m-%d")))

        for algo in ALGORITHMS:
            cursor.execute("""
                INSERT INTO concepts (type, name, category, description, cheat_sheet, status, confidence, last_revised_date, revision_count)
                VALUES ('algorithm', ?, ?, '', '', 'Not Started', 1, ?, 0)
            """, (algo["name"], algo["category"], datetime.now().strftime("%Y-%m-%d")))
        conn.commit()

    # Seed sample problems if empty
    cursor.execute("SELECT COUNT(*) FROM problems")
    problem_count = cursor.fetchone()[0]
    if problem_count == 0:
        for p in SAMPLE_PROBLEMS:
            cursor.execute("""
                INSERT INTO problems (
                    title, leetcode_number, problem_url, difficulty,
                    data_structure, algorithm, pattern, status,
                    solved_date, last_revised_date, revision_count,
                    time_complexity, space_complexity, approach_notes,
                    code_snippet, starred
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["title"], p.get("leetcode_number"), p.get("problem_url"), p["difficulty"],
                p.get("data_structure"), p.get("algorithm"), p.get("pattern"), p.get("status", "Solved"),
                p["solved_date"], p["last_revised_date"], p.get("revision_count", 0),
                p.get("time_complexity", ""), p.get("space_complexity", ""),
                p.get("approach_notes", ""), p.get("code_snippet", ""), p.get("starred", 0)
            ))
        conn.commit()

    # Seed sample flashcards if empty
    cursor.execute("SELECT COUNT(*) FROM flashcards")
    flashcard_count = cursor.fetchone()[0]
    if flashcard_count == 0:
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Seed overview flashcard for every concept from DATA_STRUCTURES and ALGORITHMS
        for item in DATA_STRUCTURES + ALGORITHMS:
            cursor.execute("SELECT id FROM concepts WHERE name = ?", (item["name"],))
            c_row = cursor.fetchone()
            if c_row:
                c_id = c_row[0]
                desc = item.get("description", "").strip()
                summary = item.get("cheat_sheet", "").strip()
                parts = []
                if desc:
                    parts.append(f"### 💡 Overview & Core Intuition\n{desc}")
                if summary:
                    parts.append(f"### 📌 Quick Summary & Key Patterns\n{summary}")
                content = "\n\n".join(parts) if parts else "Notes and summary can be added here."
                cursor.execute("""
                    INSERT INTO flashcards (concept_id, title, tag, content, last_revised_date, revision_count)
                    VALUES (?, ?, 'Cheat Sheet', ?, ?, 0)
                """, (c_id, f"{item['name']} - Overview & Quick Summary", content, today_str))

        # 2. Seed additional detailed pattern cards
        from backend.seed_data import SAMPLE_FLASHCARDS
        for card in SAMPLE_FLASHCARDS:
            cursor.execute("SELECT id FROM concepts WHERE name = ?", (card["concept_name"],))
            c_row = cursor.fetchone()
            if c_row:
                c_id = c_row[0]
                cursor.execute("""
                    INSERT INTO flashcards (concept_id, title, tag, content, last_revised_date, revision_count)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (c_id, card["title"], card.get("tag", "Pattern"), card["content"], today_str))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
