from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sqlite3
from backend.database import get_connection
from backend.models import ConceptUpdate, ConceptCreate, FlashcardCreate, FlashcardUpdate
from backend.utils import get_today_str, calculate_days_since, get_urgency_tier

router = APIRouter(prefix="/api", tags=["concepts", "flashcards"])

def enrich_concept(row: sqlite3.Row, problem_counts: dict, flashcard_counts: dict = None) -> dict:
    d = dict(row)
    name = d["name"]
    d["problems_solved"] = problem_counts.get(name, 0)
    d["flashcards_count"] = (flashcard_counts or {}).get(d["id"], 0)
    
    days = calculate_days_since(d.get("last_revised_date"))
    urgency, urgency_label = get_urgency_tier(days)
    d["days_since_revised"] = days
    d["urgency"] = urgency
    d["urgency_label"] = urgency_label
    return d

def enrich_flashcard(row: sqlite3.Row) -> dict:
    d = dict(row)
    days = calculate_days_since(d.get("last_revised_date"))
    urgency, urgency_label = get_urgency_tier(days)
    d["days_since_revised"] = days
    d["urgency"] = urgency
    d["urgency_label"] = urgency_label
    return d

@router.get("/concepts")
def list_concepts(concept_type: Optional[str] = Query(None)): # 'data_structure' or 'algorithm'
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate problem counts for each DS and Algorithm
    cursor.execute("""
        SELECT data_structure, COUNT(*) as cnt 
        FROM problems 
        WHERE data_structure IS NOT NULL AND data_structure != '' 
        GROUP BY data_structure
    """)
    ds_counts = {row["data_structure"]: row["cnt"] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT algorithm, COUNT(*) as cnt 
        FROM problems 
        WHERE algorithm IS NOT NULL AND algorithm != '' 
        GROUP BY algorithm
    """)
    algo_counts = {row["algorithm"]: row["cnt"] for row in cursor.fetchall()}
    combined_counts = {**ds_counts, **algo_counts}

    # Calculate flashcard counts for each concept
    cursor.execute("""
        SELECT concept_id, COUNT(*) as cnt
        FROM flashcards
        GROUP BY concept_id
    """)
    flashcard_counts = {row["concept_id"]: row["cnt"] for row in cursor.fetchall()}

    query = "SELECT * FROM concepts WHERE 1=1"
    params = []
    if concept_type:
        query += " AND type = ?"
        params.append(concept_type)

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    items = [enrich_concept(r, combined_counts, flashcard_counts) for r in rows]

    # Summary counts
    mastered = sum(1 for c in items if c.get("status") == "Mastered")
    in_progress = sum(1 for c in items if c.get("status") == "In Progress")
    not_started = sum(1 for c in items if c.get("status") == "Not Started")

    return {
        "concepts": items,
        "total": len(items),
        "mastered": mastered,
        "in_progress": in_progress,
        "not_started": not_started
    }

@router.post("/concepts")
def create_concept(c: ConceptCreate):
    conn = get_connection()
    cursor = conn.cursor()
    today = get_today_str()

    try:
        cursor.execute("""
            INSERT INTO concepts (type, name, category, description, cheat_sheet, status, confidence, last_revised_date, revision_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            c.type, c.name.strip(), (c.category or "General").strip(),
            (c.description or "").strip(), (c.cheat_sheet or "").strip(),
            c.status or "Not Started", c.confidence or 1, today
        ))
        new_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Concept with this name already exists")

    cursor.execute("SELECT * FROM concepts WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return enrich_concept(row, {}, {})

@router.get("/concepts/{concept_id}")
def get_concept(concept_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Concept not found")

    concept_name = row["name"]
    cursor.execute("""
        SELECT COUNT(*) FROM problems 
        WHERE data_structure = ? OR algorithm = ?
    """, (concept_name, concept_name))
    count = cursor.fetchone()[0]

    # Linked problems
    cursor.execute("""
        SELECT id, title, leetcode_number, difficulty, status, solved_date, last_revised_date 
        FROM problems 
        WHERE data_structure = ? OR algorithm = ?
        ORDER BY id DESC
    """, (concept_name, concept_name))
    linked_problems = [dict(r) for r in cursor.fetchall()]

    # Fetch flashcards for this concept
    cursor.execute("""
        SELECT * FROM flashcards 
        WHERE concept_id = ? 
        ORDER BY id ASC
    """, (concept_id,))
    flashcards = [enrich_flashcard(r) for r in cursor.fetchall()]

    conn.close()
    enriched = enrich_concept(row, {concept_name: count}, {concept_id: len(flashcards)})
    enriched["linked_problems"] = linked_problems
    enriched["flashcards"] = flashcards
    return enriched

@router.put("/concepts/{concept_id}")
def update_concept(concept_id: int, update: ConceptUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Concept not found")

    updates = []
    params = []
    for field, val in update.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ?")
        params.append(val)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(concept_id)
        cursor.execute(f"UPDATE concepts SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    row = cursor.fetchone()
    conn.close()
    return enrich_concept(row, {}, {})

@router.post("/concepts/{concept_id}/revise")
def mark_concept_revised(concept_id: int, note: Optional[str] = Query(None)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Concept not found")

    today = get_today_str()
    new_count = (row["revision_count"] or 0) + 1

    cursor.execute("""
        UPDATE concepts 
        SET last_revised_date = ?, revision_count = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (today, new_count, concept_id))

    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES ('concept', ?, ?, ?, ?)
    """, (concept_id, row["name"], today, note or "Reviewed concept and templates"))

    conn.commit()
    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return {
        "success": True,
        "message": f"Concept '{row['name']}' marked as revised today!",
        "concept": enrich_concept(updated_row, {}, {})
    }

@router.delete("/concepts/{concept_id}")
def delete_concept(concept_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
    cursor.execute("DELETE FROM flashcards WHERE concept_id = ?", (concept_id,))
    cursor.execute("DELETE FROM revision_logs WHERE item_type = 'concept' AND item_id = ?", (concept_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Concept and its flashcards deleted"}

# =====================================================================
# FLASHCARDS ENDPOINTS (FOR DEDICATED TOPIC PAGES)
# =====================================================================

@router.get("/concepts/{concept_id}/flashcards")
def list_concept_flashcards(concept_id: int, tag: Optional[str] = Query(None)):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM flashcards WHERE concept_id = ?"
    params = [concept_id]

    if tag and tag != "all":
        query += " AND tag = ?"
        params.append(tag)

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    cards = [enrich_flashcard(r) for r in rows]
    return {"flashcards": cards, "total": len(cards)}

@router.post("/concepts/{concept_id}/flashcards")
def create_concept_flashcard(concept_id: int, fc: FlashcardCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    concept_row = cursor.fetchone()
    if not concept_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Topic / Concept not found")

    today = get_today_str()
    revised_date = fc.last_revised_date.strip() if fc.last_revised_date else today

    cursor.execute("""
        INSERT INTO flashcards (concept_id, title, tag, content, last_revised_date, revision_count)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (concept_id, fc.title.strip(), (fc.tag or "Pattern").strip(), fc.content.strip(), revised_date))
    new_id = cursor.lastrowid
    conn.commit()

    # Log initial creation in revision_logs
    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES ('flashcard', ?, ?, ?, 'Created new flashcard')
    """, (new_id, fc.title.strip(), revised_date))
    conn.commit()

    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()

    return enrich_flashcard(row)

@router.get("/flashcards/{flashcard_id}")
def get_single_flashcard(flashcard_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return enrich_flashcard(row)

@router.put("/flashcards/{flashcard_id}")
def update_flashcard(flashcard_id: int, fc: FlashcardUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Flashcard not found")

    updates = []
    params = []
    for field, val in fc.model_dump(exclude_unset=True).items():
        if val is not None:
            updates.append(f"{field} = ?")
            params.append(val.strip() if isinstance(val, str) else val)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(flashcard_id)
        cursor.execute(f"UPDATE flashcards SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
    row = cursor.fetchone()
    conn.close()
    return enrich_flashcard(row)

@router.delete("/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
    cursor.execute("DELETE FROM revision_logs WHERE item_type = 'flashcard' AND item_id = ?", (flashcard_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Flashcard deleted"}

@router.post("/flashcards/{flashcard_id}/revise")
def mark_flashcard_revised(flashcard_id: int, note: Optional[str] = Query(None)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Flashcard not found")

    today = get_today_str()
    new_count = (row["revision_count"] or 0) + 1
    concept_id = row["concept_id"]

    # Update flashcard
    cursor.execute("""
        UPDATE flashcards 
        SET last_revised_date = ?, revision_count = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (today, new_count, flashcard_id))

    # Also touch the parent concept's last_revised_date to keep the overall topic fresh
    cursor.execute("""
        UPDATE concepts 
        SET last_revised_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (today, concept_id))

    # Record in revision_logs
    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES ('flashcard', ?, ?, ?, ?)
    """, (flashcard_id, row["title"], today, note or "Reviewed flashcard"))

    conn.commit()
    cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return {
        "success": True,
        "message": f"Flashcard '{row['title']}' marked revised today!",
        "flashcard": enrich_flashcard(updated_row)
    }
