from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, date, timedelta
import httpx
from backend.database import get_connection
from backend.config import load_config
from backend.models import LeetCodeManualStats
from backend.utils import get_today_str, calculate_days_since, get_urgency_tier

router = APIRouter(prefix="", tags=["stats"])

@router.get("/api/stats/dashboard")
def get_dashboard_stats():
    cfg = load_config()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 3-Month Trip Progress
    trip_name = cfg.get("trip_name", "3 Months DSA Sprint")
    trip_start_str = cfg.get("trip_start_date", get_today_str())
    trip_duration = cfg.get("trip_duration_days", 90)
    target_problems = cfg.get("trip_target_problems", 150)
    trip_manifesto = cfg.get("trip_manifesto", "")

    try:
        start_dt = datetime.strptime(trip_start_str, "%Y-%m-%d").date()
    except Exception:
        start_dt = date.today()

    today = date.today()
    days_elapsed = (today - start_dt).days + 1
    if days_elapsed < 1:
        days_elapsed = 1
    days_remaining = max(0, trip_duration - days_elapsed)
    trip_progress_pct = min(100.0, max(0.0, round((days_elapsed / trip_duration) * 100, 1)))

    target_end_dt = start_dt + timedelta(days=trip_duration)
    target_end_str = target_end_dt.strftime("%Y-%m-%d")

    # 2. Problems stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN difficulty = 'Easy' THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN difficulty = 'Medium' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN difficulty = 'Hard' THEN 1 ELSE 0 END) as hard,
            SUM(CASE WHEN starred = 1 THEN 1 ELSE 0 END) as starred
        FROM problems
    """)
    prob_stats = dict(cursor.fetchone())
    total_solved = prob_stats["total"] or 0
    easy_solved = prob_stats["easy"] or 0
    medium_solved = prob_stats["medium"] or 0
    hard_solved = prob_stats["hard"] or 0
    starred_solved = prob_stats["starred"] or 0
    problem_target_pct = min(100.0, round((total_solved / max(1, target_problems)) * 100, 1))

    # 3. Concepts breakdown
    cursor.execute("""
        SELECT 
            type,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Mastered' THEN 1 ELSE 0 END) as mastered,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) as not_started
        FROM concepts
        GROUP BY type
    """)
    concept_rows = cursor.fetchall()
    ds_stats = {"total": 0, "mastered": 0, "in_progress": 0, "not_started": 0}
    algo_stats = {"total": 0, "mastered": 0, "in_progress": 0, "not_started": 0}

    for row in concept_rows:
        t = row["type"]
        data = {
            "total": row["total"] or 0,
            "mastered": row["mastered"] or 0,
            "in_progress": row["in_progress"] or 0,
            "not_started": row["not_started"] or 0
        }
        if t == "data_structure":
            ds_stats = data
        elif t == "algorithm":
            algo_stats = data

    # 4. Urgent Revisions (items with highest days_since_revised)
    # Check both problems and concepts
    urgent_candidates = []
    
    cursor.execute("SELECT id, title, difficulty, last_revised_date FROM problems")
    for r in cursor.fetchall():
        days = calculate_days_since(r["last_revised_date"])
        urgency, urgency_label = get_urgency_tier(days)
        urgent_candidates.append({
            "id": r["id"],
            "item_type": "problem",
            "name": r["title"],
            "detail": f"LeetCode • {r['difficulty']}",
            "days_since_revised": days,
            "last_revised_date": r["last_revised_date"],
            "urgency": urgency,
            "urgency_label": urgency_label
        })

    cursor.execute("SELECT id, name, type, last_revised_date FROM concepts")
    for r in cursor.fetchall():
        days = calculate_days_since(r["last_revised_date"])
        urgency, urgency_label = get_urgency_tier(days)
        type_str = "Data Structure" if r["type"] == "data_structure" else "Algorithm"
        urgent_candidates.append({
            "id": r["id"],
            "item_type": "concept",
            "name": r["name"],
            "detail": type_str,
            "days_since_revised": days,
            "last_revised_date": r["last_revised_date"],
            "urgency": urgency,
            "urgency_label": urgency_label
        })

    # Sort descending
    urgent_candidates.sort(key=lambda x: x["days_since_revised"], reverse=True)
    urgent_top5 = urgent_candidates[:6]

    overdue_count = sum(1 for x in urgent_candidates if x["urgency"] == "overdue")
    due_count = sum(1 for x in urgent_candidates if x["urgency"] == "due")

    # 5. Recent problems
    cursor.execute("""
        SELECT id, title, leetcode_number, difficulty, solved_date, data_structure, algorithm 
        FROM problems 
        ORDER BY solved_date DESC, id DESC 
        LIMIT 5
    """)
    recent_problems = [dict(r) for r in cursor.fetchall()]

    # 6. LeetCode profile cache
    cursor.execute("SELECT * FROM leetcode_stats_cache ORDER BY id DESC LIMIT 1")
    cached_lc = cursor.fetchone()
    lc_profile = dict(cached_lc) if cached_lc else None

    conn.close()

    return {
        "trip": {
            "name": trip_name,
            "start_date": trip_start_str,
            "target_end_date": target_end_str,
            "duration_days": trip_duration,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "progress_percent": trip_progress_pct,
            "target_problems": target_problems,
            "manifesto": trip_manifesto
        },
        "problems": {
            "total": total_solved,
            "easy": easy_solved,
            "medium": medium_solved,
            "hard": hard_solved,
            "starred": starred_solved,
            "target": target_problems,
            "target_percent": problem_target_pct
        },
        "data_structures": ds_stats,
        "algorithms": algo_stats,
        "revisions": {
            "overdue_count": overdue_count,
            "due_count": due_count,
            "urgent_items": urgent_top5
        },
        "recent_problems": recent_problems,
        "leetcode_profile": lc_profile,
        "leetcode_username": cfg.get("leetcode_username", "")
    }

@router.get("/api/leetcode/profile")
def get_leetcode_profile():
    cfg = load_config()
    username = cfg.get("leetcode_username", "").strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leetcode_stats_cache WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"username": username, "data": dict(row), "cached": True}
    return {"username": username, "data": None, "cached": False}

@router.post("/api/leetcode/sync")
async def sync_leetcode_profile(username_override: Optional[str] = Query(None)):
    cfg = load_config()
    username = (username_override or cfg.get("leetcode_username", "")).strip()

    if not username:
        raise HTTPException(status_code=400, detail="LeetCode username is not configured. Please enter your username in Profile Settings.")

    stats_data = None
    source = "live"

    # Try official GraphQL first
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            graphql_query = """
            query userProblemsSolved($username: String!) {
                allQuestionsCount {
                    difficulty
                    count
                }
                matchedUser(username: $username) {
                    submitStatsGlobal {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                    profile {
                        ranking
                        reputation
                    }
                }
            }
            """
            resp = await client.post(
                "https://leetcode.com/graphql",
                json={"query": graphql_query, "variables": {"username": username}},
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                matched_user = data.get("matchedUser")
                if matched_user:
                    ac_sub = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
                    total_cnt = 0
                    easy_cnt = 0
                    med_cnt = 0
                    hard_cnt = 0
                    for item in ac_sub:
                        diff = item.get("difficulty")
                        cnt = item.get("count", 0)
                        if diff == "All": total_cnt = cnt
                        elif diff == "Easy": easy_cnt = cnt
                        elif diff == "Medium": med_cnt = cnt
                        elif diff == "Hard": hard_cnt = cnt
                    ranking = matched_user.get("profile", {}).get("ranking", 0)

                    stats_data = {
                        "username": username,
                        "total_solved": total_cnt,
                        "easy_solved": easy_cnt,
                        "medium_solved": med_cnt,
                        "hard_solved": hard_cnt,
                        "ranking": ranking or 0,
                        "acceptance_rate": 0.0
                    }
    except Exception as e:
        print(f"Direct LeetCode GraphQL fetch failed or sandboxed: {e}")

    # Fallback to public mirror if direct GraphQL failed
    if not stats_data:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"https://alfa-leetcode-api.onrender.com/userProfile/{username}")
                if resp.status_code == 200:
                    data = resp.json()
                    stats_data = {
                        "username": username,
                        "total_solved": data.get("totalSolved", 0),
                        "easy_solved": data.get("easySolved", 0),
                        "medium_solved": data.get("mediumSolved", 0),
                        "hard_solved": data.get("hardSolved", 0),
                        "ranking": data.get("ranking", 0),
                        "acceptance_rate": data.get("acceptanceRate", 0.0)
                    }
        except Exception as e:
            print(f"Fallback LeetCode API failed: {e}")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # If network/API unreachable, check if we have cached stats
    conn = get_connection()
    cursor = conn.cursor()

    if stats_data:
        cursor.execute("""
            INSERT INTO leetcode_stats_cache (username, total_solved, easy_solved, medium_solved, hard_solved, ranking, acceptance_rate, last_synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                total_solved=excluded.total_solved,
                easy_solved=excluded.easy_solved,
                medium_solved=excluded.medium_solved,
                hard_solved=excluded.hard_solved,
                ranking=excluded.ranking,
                acceptance_rate=excluded.acceptance_rate,
                last_synced_at=excluded.last_synced_at
        """, (
            stats_data["username"], stats_data["total_solved"], stats_data["easy_solved"],
            stats_data["medium_solved"], stats_data["hard_solved"], stats_data["ranking"],
            stats_data["acceptance_rate"], now_str
        ))
        conn.commit()
    else:
        cursor.execute("SELECT * FROM leetcode_stats_cache WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            stats_data = dict(row)
            source = "cached"
        else:
            conn.close()
            return {
                "success": False,
                "message": f"Could not connect to LeetCode API right now. You can enter your stats manually in Profile Settings.",
                "data": None
            }

    # Fetch final saved
    cursor.execute("SELECT * FROM leetcode_stats_cache WHERE username = ?", (username,))
    final_row = dict(cursor.fetchone())
    conn.close()

    # Also update config leetcode_username
    cfg["leetcode_username"] = username
    from backend.config import save_config
    save_config(cfg)

    return {
        "success": True,
        "source": source,
        "message": f"LeetCode profile synced for '{username}'!",
        "data": final_row
    }

@router.post("/api/leetcode/manual")
def save_manual_leetcode_stats(stats: LeetCodeManualStats):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO leetcode_stats_cache (username, total_solved, easy_solved, medium_solved, hard_solved, ranking, acceptance_rate, last_synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            total_solved=excluded.total_solved,
            easy_solved=excluded.easy_solved,
            medium_solved=excluded.medium_solved,
            hard_solved=excluded.hard_solved,
            ranking=excluded.ranking,
            acceptance_rate=excluded.acceptance_rate,
            last_synced_at=excluded.last_synced_at
    """, (
        stats.username.strip(), stats.total_solved, stats.easy_solved,
        stats.medium_solved, stats.hard_solved, stats.ranking or 0,
        stats.acceptance_rate or 0.0, now_str
    ))
    conn.commit()

    cursor.execute("SELECT * FROM leetcode_stats_cache WHERE username = ?", (stats.username.strip(),))
    row = dict(cursor.fetchone())
    conn.close()

    cfg = load_config()
    cfg["leetcode_username"] = stats.username.strip()
    from backend.config import save_config
    save_config(cfg)

    return {"success": True, "message": "LeetCode stats updated successfully!", "data": row}
