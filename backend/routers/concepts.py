from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sqlite3
from backend.database import get_connection
from backend.models import ConceptUpdate, ConceptCreate
from backend.utils import get_today_str, calculate_days_since, get_urgency_tier

router = APIRouter(prefix="/api/concepts", tags=["concepts"])

def enrich_concept(row: sqlite3.Row, problem_counts: dict) -> dict:
    d = dict(row)
    name = d["name"]
    # Get solved problems count matching this concept name or keyword
    d["problems_solved"] = problem_counts.get(name, 0)
    
    days = calculate_days_since(d.get("last_revised_date"))
    urgency, urgency_label = get_urgency_tier(days)
    d["days_since_revised"] = days
    d["urgency"] = urgency
    d["urgency_label"] = urgency_label
    return d

@router.get("")
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

    query = "SELECT * FROM concepts WHERE 1=1"
    params = []
    if concept_type:
        query += " AND type = ?"
        params.append(concept_type)

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    items = [enrich_concept(r, combined_counts) for r in rows]

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

@router.post("")
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
    return enrich_concept(row, {})

@router.get("/{concept_id}")
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

    # Also fetch linked problems
    cursor.execute("""
        SELECT id, title, leetcode_number, difficulty, status, solved_date, last_revised_date 
        FROM problems 
        WHERE data_structure = ? OR algorithm = ?
        ORDER BY id DESC
    """, (concept_name, concept_name))
    linked_problems = [dict(r) for r in cursor.fetchall()]

    conn.close()
    enriched = enrich_concept(row, {concept_name: count})
    enriched["linked_problems"] = linked_problems
    return enriched

@router.put("/{concept_id}")
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
    return enrich_concept(row, {})

@router.post("/{concept_id}/revise")
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
        "concept": enrich_concept(updated_row, {})
    }

@router.delete("/{concept_id}")
def delete_concept(concept_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
    cursor.execute("DELETE FROM revision_logs WHERE item_type = 'concept' AND item_id = ?", (concept_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Concept deleted"}
