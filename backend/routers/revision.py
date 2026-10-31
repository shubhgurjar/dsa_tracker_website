from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sqlite3
from backend.database import get_connection
from backend.models import RevisionAction
from backend.utils import get_today_str, calculate_days_since, get_urgency_tier

router = APIRouter(prefix="/api/revision", tags=["revision"])

@router.get("/queue")
def get_revision_queue(
    item_type: Optional[str] = Query("all"), # 'all', 'problem', 'concept'
    urgency_filter: Optional[str] = Query("all"), # 'all', 'overdue', 'due', 'due_soon', 'fresh'
    search: Optional[str] = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor()
    items = []

    # 1. Fetch problems
    if item_type in ("all", "problem"):
        cursor.execute("SELECT * FROM problems")
        for row in cursor.fetchall():
            d = dict(row)
            days = calculate_days_since(d.get("last_revised_date"))
            urgency, urgency_label = get_urgency_tier(days)
            subtitle_parts = [f"#{d['leetcode_number']}" if d.get('leetcode_number') else "", d.get("difficulty", ""), d.get("data_structure", "")]
            subtitle = " • ".join([p for p in subtitle_parts if p])

            items.append({
                "id": d["id"],
                "item_type": "problem",
                "title": d["title"],
                "subtitle": subtitle,
                "badge": d["difficulty"],
                "status": d.get("status", "Solved"),
                "solved_date": d.get("solved_date"),
                "last_revised_date": d.get("last_revised_date"),
                "revision_count": d.get("revision_count", 0),
                "days_since_revised": days,
                "urgency": urgency,
                "urgency_label": urgency_label,
                "url": d.get("problem_url")
            })

    # 2. Fetch concepts
    if item_type in ("all", "concept"):
        cursor.execute("SELECT * FROM concepts")
        for row in cursor.fetchall():
            d = dict(row)
            days = calculate_days_since(d.get("last_revised_date"))
            urgency, urgency_label = get_urgency_tier(days)
            type_label = "Data Structure" if d["type"] == "data_structure" else "Algorithm"
            subtitle = f"{type_label} • {d.get('category', 'Core')}"

            items.append({
                "id": d["id"],
                "item_type": "concept",
                "title": d["name"],
                "subtitle": subtitle,
                "badge": d.get("status", "In Progress"),
                "status": d.get("status", "Not Started"),
                "solved_date": None,
                "last_revised_date": d.get("last_revised_date"),
                "revision_count": d.get("revision_count", 0),
                "days_since_revised": days,
                "urgency": urgency,
                "urgency_label": urgency_label,
                "confidence": d.get("confidence", 1)
            })

    conn.close()

    # Search filter
    if search:
        s = search.strip().lower()
        items = [i for i in items if s in i["title"].lower() or s in i["subtitle"].lower()]

    # Urgency filter
    if urgency_filter != "all":
        items = [i for i in items if i["urgency"] == urgency_filter]

    # Sort descending by days since revised (most overdue first)
    items.sort(key=lambda x: x["days_since_revised"], reverse=True)

    # Breakdown metrics
    overdue_count = sum(1 for i in items if i["urgency"] == "overdue")
    due_count = sum(1 for i in items if i["urgency"] == "due")
    due_soon_count = sum(1 for i in items if i["urgency"] == "due_soon")
    fresh_count = sum(1 for i in items if i["urgency"] == "fresh")

    return {
        "items": items,
        "total": len(items),
        "counts": {
            "overdue": overdue_count,
            "due": due_count,
            "due_soon": due_soon_count,
            "fresh": fresh_count
        }
    }

@router.get("/logs")
def get_revision_logs(limit: int = 30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM revision_logs 
        ORDER BY id DESC 
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"logs": rows}

@router.post("/mark")
def mark_revision(action: RevisionAction):
    today = action.revised_date or get_today_str()
    conn = get_connection()
    cursor = conn.cursor()

    if action.item_type == "problem":
        cursor.execute("SELECT * FROM problems WHERE id = ?", (action.item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Problem not found")

        new_count = (row["revision_count"] or 0) + 1
        cursor.execute("""
            UPDATE problems 
            SET last_revised_date = ?, revision_count = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (today, new_count, action.item_id))
        item_name = row["title"]

    elif action.item_type == "concept":
        cursor.execute("SELECT * FROM concepts WHERE id = ?", (action.item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Concept not found")

        new_count = (row["revision_count"] or 0) + 1
        cursor.execute("""
            UPDATE concepts 
            SET last_revised_date = ?, revision_count = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (today, new_count, action.item_id))
        item_name = row["name"]
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid item_type")

    # Record in revision_logs
    cursor.execute("""
        INSERT INTO revision_logs (item_type, item_id, item_name, revised_date, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (action.item_type, action.item_id, item_name, today, action.notes or "Revision completed"))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"'{item_name}' marked revised on {today}!",
        "item_type": action.item_type,
        "item_id": action.item_id,
        "revised_date": today
    }
