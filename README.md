# ⚡ Minimal DSA Tracker

A clean, minimalist, high-focus web application built to track your **3-Month DSA Learning Trip & LeetCode Sprint**.

Designed with zero unnecessary bloat, instant-loading pages, spaced repetition revision reminders, and seamless LeetCode profile tracking.

---

## 🛠️ Tech Stack

- **Backend**: Python [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Database**: SQLite3 (`dsa_tracker.db` with WAL mode for fast queries)
- **Configuration & Backups**: JSON files (`config.json`, single-click JSON Export & Import)
- **Frontend**: Clean, modern HTML5, CSS3 (sleek dark aesthetic inspired by Linear/Vercel), and Vanilla JavaScript (zero node_modules, zero build tools, pure browser performance)

---

## 🎯 Key Features

### 1. 🚀 3-Month DSA Trip Dashboard (`/` & `/dashboard`)
- **Live Trip Countdown**: Displays **Day X of 90**, days remaining, and visual sprint progress bar.
- **Trip Manifesto**: Keeps your personal 3-month goal top of mind.
- **KPI Metrics**: Real-time solved counts by difficulty (Easy, Medium, Hard), goal completion percentage, Data Structures mastered, Algorithms mastered, and overdue revisions count.
- **Urgent Revisions Feed**: Immediate table of problems and concepts most neglected with 1-click **"✓ Revised Today"** buttons.
- **Quick LeetCode Profile Widget**: Snapshot of your global ranking and problem counts.

### 2. 📚 Learning Hub: Data Structures & Algorithms (`/concepts`)
- **Pre-populated with 24 foundational topics**:
  - **Data Structures**: Arrays & Dynamic Arrays, Strings, Linked Lists, Stacks & Monotonic Stacks, Queues & Monotonic Deques, Hash Tables & Sets, Binary Trees, BSTs, Heaps / Priority Queues, Graphs, Trie, Disjoint Set Union (Union-Find).
  - **Algorithms**: Binary Search, Two Pointers, Sliding Window, Prefix Sums, Sorting Algorithms, BFS, DFS & Backtracking, Dynamic Programming (1D & 2D), Greedy & Intervals, Dijkstra, Topological Sort, Bit Manipulation.
- **Progress Tracking**: Status selector (*Not Started*, *In Progress*, *Mastered*).
- **Interactive Confidence Ratings**: 1 to 5 stars (★☆☆☆☆ to ★★★★★).
- **Cheat Sheets & Code Templates**: Built-in reference notes for time/space complexity and invariants.
- **Linked Problems**: Automatically counts and displays all solved problems under each topic.
- **Custom Topic Creation**: Add any niche topics (e.g. Segment Trees, Fenwick Trees).

### 3. 💻 LeetCode Problems Vault (`/problems`)
- Log problems with Title, LeetCode #, Difficulty, URL, Data Structure, Algorithm, Pattern, Time Complexity $O(N)$, Space Complexity $O(1)$, and Code Snippets.
- **Multi-Filter & Search**: Filter by Difficulty, Data Structure, Algorithm, Revision Urgency, and Starred favorites.
- **Sort Flexibility**: Sort by *Days Since Revised* (most neglected first), Solved Date, LeetCode number, or Difficulty.
- **Quick 1-Click Revise**: Immediately update the problem's last revision date to today and increment revision count.

### 4. 🔁 Spaced Repetition & Revision Center (`/revision`)
- **Know At-A-Glance Days Elapsed**: Visual color-coded badges showing exactly how many days have passed since you last revised:
  - 🚨 **Overdue (> 14 days)**: Urgent recall needed
  - ⚠️ **Revision Due (8–14 days)**: Prime for memory reinforcement
  - ⚡ **Due Soon (4–7 days)**: Consolidating memory
  - 🌱 **Fresh (≤ 3 days)**: Revised today or recently
- **Priority Queue**: Dynamically sorts both problems and concepts so the most neglected items rise to the top.
- **1-Click "✓ Mark Revised Today"**: Instantly resets the counter to 0 days ("🌱 Today").
- **Revision Activity Log**: History log of all revision actions.

### 5. 👤 Profile & 3-Month Trip Settings (`/profile`)
- **Trip Dates & Goals**: Customize trip name, start date, duration (days), and problem target count.
- **LeetCode Profile Sync**: Enter your LeetCode username and sync live public stats (total solved, difficulty breakdown, global ranking) with manual override support.
- **JSON Data Backup & Restore**: One-click download of all problems, concepts, revision logs, and configs as a single JSON file; restore anytime.
- **Minimal Access PIN**: Protect your app with a simple 4-digit PIN (default: `1234`).

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.9+

### 2. Quick Launch
Run the provided startup script:
```bash
./run.sh
```
Or run directly:
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Open your browser at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 3. Default Login PIN
- **PIN**: `1234`
- You can change the PIN or customize your trip settings anytime under **Profile & Settings** (`/profile`).

---

## 📂 Project Structure

```
dsa_tracker_website/
├── backend/
│   ├── config.py             # JSON config manager & PIN authentication
│   ├── database.py           # SQLite connection, tables init & seed data
│   ├── models.py             # Pydantic schemas
│   ├── seed_data.py          # 24 core DS & Algo topics with cheat sheets
│   ├── utils.py              # Days-since calculation & urgency tiers
│   └── routers/
│       ├── auth.py           # Minimal PIN login & session token
│       ├── concepts.py       # DS & Algo tracker API
│       ├── data_transfer.py  # JSON Export & Import API
│       ├── problems.py       # LeetCode problems CRUD & revision
│       ├── revision.py       # Spaced repetition queue API
│       └── stats.py          # Dashboard metrics & LeetCode sync
├── config.json               # Config file (trip dates, goals, user settings)
├── dsa_tracker.db            # SQLite database
├── main.py                   # FastAPI application & static routes
├── requirements.txt          # Python dependencies
├── run.sh                    # One-command launch script
├── static/
│   ├── css/
│   │   └── styles.css        # Sleek modern dark mode design system
│   ├── js/
│   │   ├── app.js            # Shared client, API fetcher, modals & toasts
│   │   ├── concepts.js       # Learning Hub page logic
│   │   ├── dashboard.js      # Overview dashboard logic
│   │   ├── login.js          # Minimal PIN unlock logic
│   │   ├── problems.js       # Problems Vault table & filters logic
│   │   ├── profile.js        # Trip settings & LeetCode sync logic
│   │   └── revision.js       # Revision Center & spaced repetition logic
│   ├── index.html            # Dashboard / Overview page
│   ├── concepts.html         # Learning Hub page
│   ├── login.html            # Minimal unlock screen
│   ├── problems.html         # Problems Vault page
│   ├── profile.html          # Profile & Trip settings page
│   └── revision.html         # Revision Center page
└── test_app.py               # Automated test suite
```

---

## 🧪 Testing

Run the automated test suite:
```bash
PYTHONPATH=. ./venv/bin/python test_app.py
```
All 7 unit and integration tests will execute and verify page serving, authentication, API operations, revision logic, and backup exports.
