from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json
import sqlite3
from backend.database import get_connection
from backend.config import load_config, save_config
from backend.models import TripSettingsUpdate

router = APIRouter(prefix="/api", tags=["data_transfer"])

@router.get("/config")
def get_trip_config():
    cfg = load_config()
    safe_cfg = {k: v for k, v in cfg.items() if k not in ("auth_pin_hash", "session_secret")}
    return safe_cfg

@router.put("/config")
def update_trip_config(update: TripSettingsUpdate):
    cfg = load_config()
    for field, val in update.model_dump(exclude_unset=True).items():
        if val is not None:
            cfg[field] = val
    save_config(cfg)
    safe_cfg = {k: v for k, v in cfg.items() if k not in ("auth_pin_hash", "session_secret")}
    return {"success": True, "message": "Settings updated successfully", "config": safe_cfg}

@router.get("/export")
def export_all_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM problems")
    problems = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM concepts")
    concepts = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM flashcards")
    flashcards = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM revision_logs")
    logs = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM leetcode_stats_cache")
    lc_stats = [dict(r) for r in cursor.fetchall()]

    conn.close()

    cfg = load_config()
    safe_cfg = {k: v for k, v in cfg.items() if k not in ("auth_pin_hash", "session_secret")}

    export_payload = {
        "version": "1.0",
        "exported_at": sqlite3.datetime.datetime.now().isoformat(),
        "config": safe_cfg,
        "problems": problems,
        "concepts": concepts,
        "flashcards": flashcards,
        "revision_logs": logs,
        "leetcode_stats": lc_stats
    }

    return JSONResponse(
        content=export_payload,
        headers={"Content-Disposition": "attachment; filename=dsa_tracker_backup.json"}
    )

@router.post("/import")
def import_all_data(payload: Dict[str, Any]):
    if not isinstance(payload, dict) or "problems" not in payload:
        raise HTTPException(status_code=400, detail="Invalid backup file format")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Import problems
        if "problems" in payload and isinstance(payload["problems"], list):
            cursor.execute("DELETE FROM problems")
            for p in payload["problems"]:
                cursor.execute("""
                    INSERT INTO problems (
                        id, title, leetcode_number, problem_url, difficulty,
                        data_structure, algorithm, pattern, status,
                        solved_date, last_revised_date, revision_count,
                        time_complexity, space_complexity, approach_notes,
                        code_snippet, starred
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p.get("id"), p.get("title", "Untitled"), p.get("leetcode_number"), p.get("problem_url"),
                    p.get("difficulty", "Medium"), p.get("data_structure"), p.get("algorithm"),
                    p.get("pattern"), p.get("status", "Solved"), p.get("solved_date"),
                    p.get("last_revised_date"), p.get("revision_count", 0),
                    p.get("time_complexity", ""), p.get("space_complexity", ""),
                    p.get("approach_notes", ""), p.get("code_snippet", ""), p.get("starred", 0)
                ))

        # Import concepts
        if "concepts" in payload and isinstance(payload["concepts"], list):
            cursor.execute("DELETE FROM concepts")
            for c in payload["concepts"]:
                cursor.execute("""
                    INSERT INTO concepts (
                        id, type, name, category, description, status,
                        confidence, key_notes, cheat_sheet, last_revised_date, revision_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c.get("id"), c.get("type"), c.get("name"), c.get("category"),
                    c.get("description"), c.get("status", "Not Started"), c.get("confidence", 1),
                    c.get("key_notes", ""), c.get("cheat_sheet", ""),
                    c.get("last_revised_date"), c.get("revision_count", 0)
                ))

        # Import flashcards
        if "flashcards" in payload and isinstance(payload["flashcards"], list):
            cursor.execute("DELETE FROM flashcards")
            for fc in payload["flashcards"]:
                cursor.execute("""
                    INSERT INTO flashcards (
                        id, concept_id, title, tag, content, last_revised_date, revision_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    fc.get("id"), fc.get("concept_id"), fc.get("title"), fc.get("tag", "Pattern"),
                    fc.get("content", ""), fc.get("last_revised_date"), fc.get("revision_count", 0)
                ))

        # Import revision logs
        if "revision_logs" in payload and isinstance(payload["revision_logs"], list):
            cursor.execute("DELETE FROM revision_logs")
            for l in payload["revision_logs"]:
                cursor.execute("""
                    INSERT INTO revision_logs (id, item_type, item_id, item_name, revised_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    l.get("id"), l.get("item_type"), l.get("item_id"),
                    l.get("item_name"), l.get("revised_date"), l.get("notes")
                ))

        conn.commit()

        # Import config if present
        if "config" in payload and isinstance(payload["config"], dict):
            current_cfg = load_config()
            for k, v in payload["config"].items():
                if k not in ("auth_pin_hash", "session_secret"):
                    current_cfg[k] = v
            save_config(current_cfg)

        return {"success": True, "message": "All data imported successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    finally:
        conn.close()
