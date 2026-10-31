from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sqlite3
from backend.database import get_connection
from backend.models import ProblemCreate, ProblemUpdate
from backend.utils import get_today_str, calculate_days_since, get_urgency_tier

router = APIRouter(prefix="/api/problems", tags=["problems"])

def dict_from_row(row: sqlite3.Row) -> dict:
    d = dict(row)
    days = calculate_days_since(d.get("last_revised_date"))
    urgency, urgency_label = get_urgency_tier(days)
    d["days_since_revised"] = days
    d["urgency"] = urgency
    d["urgency_label"] = urgency_label
    return d

@router.get("")
def list_problems(
    search: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    data_structure: Optional[str] = Query(None),
    algorithm: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    starred: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("solved_date_desc")
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM problems WHERE 1=1"
    params = []

    if search:
        s = f"%{search.strip().lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(pattern) LIKE ? OR CAST(leetcode_number AS TEXT) LIKE ?)"
        params.extend([s, s, s])

    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    if data_structure:
        query += " AND data_structure = ?"
        params.append(data_structure)

    if algorithm:
        query += " AND algorithm = ?"
        params.append(algorithm)

    if status:
        query += " AND status = ?"
        params.append(status)

    if starred is not None:
        query += " AND starred = ?"
        params.append(starred)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = [dict_from_row(r) for r in rows]

    if urgency:
        results = [r for r in results if r["urgency"] == urgency]

    if sort_by == "days_desc":
        results.sort(key=lambda x: x["days_since_revised"], reverse=True)
    elif sort_by == "days_asc":
        results.sort(key=lambda x: x["days_since_revised"])
    elif sort_by == "number":
        results.sort(key=lambda x: (x.get("leetcode_number") or 99999))
    elif sort_by == "difficulty":
        diff_order = {"Easy": 1, "Medium": 2, "Hard": 3}
        results.sort(key=lambda x: diff_order.get(x.get("difficulty"), 99))
    else: # solved_date_desc
        results.sort(key=lambda x: x.get("solved_date") or "", reverse=True)

    return {"problems": results, "total": len(results)}

@router.post("")
def create_problem(p: ProblemCreate):
    conn = get_connection()
    cursor = conn.cursor()

    today = get_today_str()
    solved = p.solved_date.strip() if p.solved_date else today

    cursor.execute("""
        INSERT INTO problems (
            title, leetcode_number, problem_url, difficulty,
            data_structure, algorithm, pattern, status,
            solved_date, last_revised_date, revision_count,
            time_complexity, space_complexity, approach_notes,
            code_snippet, starred
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p.title.strip(), p.leetcode_number, (p.problem_url or "").strip(), p.difficulty,
        (p.data_structure or "").strip(), (p.algorithm or "").strip(), (p.pattern or "").strip(),
        p.status or "Solved", solved, solved, 0,
        (p.time_complexity or "").strip(), (p.space_complexity or "").strip(),
        (p.approach_notes or "").strip(), (p.code_snippet or "").strip(), p.starred or 0
    ))
    new_id = cursor.lastrowid
    conn.commit()

    # Log initial solve into revision_logs
    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES ('problem', ?, ?, ?, 'Initial solve recorded')
    """, (new_id, p.title.strip(), solved))
    conn.commit()

    cursor.execute("SELECT * FROM problems WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()

    return dict_from_row(row)

@router.get("/{problem_id}")
def get_problem(problem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Problem not found")
    return dict_from_row(row)

@router.put("/{problem_id}")
def update_problem(problem_id: int, p: ProblemUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    updates = []
    params = []
    for field, val in p.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ?")
        params.append(val)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(problem_id)
        cursor.execute(f"UPDATE problems SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

@router.delete("/{problem_id}")
def delete_problem(problem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
    cursor.execute("DELETE FROM revision_logs WHERE item_type = 'problem' AND item_id = ?", (problem_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Problem deleted"}

@router.post("/{problem_id}/revise")
def mark_problem_revised(problem_id: int, note: Optional[str] = Query(None)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    today = get_today_str()
    new_count = (row["revision_count"] or 0) + 1

    cursor.execute("""
        UPDATE problems 
        SET last_revised_date = ?, revision_count = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (today, new_count, problem_id))

    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES ('problem', ?, ?, ?, ?)
    """, (problem_id, row["title"], today, note or "Revised and reviewed approach"))

    conn.commit()
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return {
        "success": True,
        "message": f"'{row['title']}' marked as revised today!",
        "problem": dict_from_row(updated_row)
    }

@router.post("/{problem_id}/star")
def toggle_star(problem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT starred FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    new_starred = 0 if row["starred"] else 1
    cursor.execute("UPDATE problems SET starred = ? WHERE id = ?", (new_starred, problem_id))
    conn.commit()
    conn.close()
    return {"success": True, "starred": new_starred}
