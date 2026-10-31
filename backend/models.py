from pydantic import BaseModel, Field
from typing import Optional, List

class LoginRequest(BaseModel):
    pin: str

class PinUpdateRequest(BaseModel):
    old_pin: str
    new_pin: str

class TripSettingsUpdate(BaseModel):
    trip_name: Optional[str] = None
    trip_start_date: Optional[str] = None
    trip_duration_days: Optional[int] = None
    trip_target_problems: Optional[int] = None
    trip_manifesto: Optional[str] = None
    leetcode_username: Optional[str] = None
    auth_enabled: Optional[bool] = None

class ProblemCreate(BaseModel):
    title: str
    leetcode_number: Optional[int] = None
    problem_url: Optional[str] = None
    difficulty: str = "Medium" # Easy, Medium, Hard
    data_structure: Optional[str] = None
    algorithm: Optional[str] = None
    pattern: Optional[str] = None
    status: str = "Solved" # Solved, Need Revision, Bookmarked
    solved_date: Optional[str] = None # Defaults to today
    time_complexity: Optional[str] = ""
    space_complexity: Optional[str] = ""
    approach_notes: Optional[str] = ""
    code_snippet: Optional[str] = ""
    starred: Optional[int] = 0

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    leetcode_number: Optional[int] = None
    problem_url: Optional[str] = None
    difficulty: Optional[str] = None
    data_structure: Optional[str] = None
    algorithm: Optional[str] = None
    pattern: Optional[str] = None
    status: Optional[str] = None
    solved_date: Optional[str] = None
    last_revised_date: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    approach_notes: Optional[str] = None
    code_snippet: Optional[str] = None
    starred: Optional[int] = None

class ConceptUpdate(BaseModel):
    status: Optional[str] = None # Not Started, In Progress, Mastered
    confidence: Optional[int] = None # 1 to 5
    key_notes: Optional[str] = None
    cheat_sheet: Optional[str] = None
    last_revised_date: Optional[str] = None

class ConceptCreate(BaseModel):
    type: str # 'data_structure' or 'algorithm'
    name: str
    category: Optional[str] = "General"
    description: Optional[str] = ""
    cheat_sheet: Optional[str] = ""
    status: Optional[str] = "Not Started"
    confidence: Optional[int] = 1

class RevisionAction(BaseModel):
    item_type: str # 'problem' or 'concept'
    item_id: int
    revised_date: Optional[str] = None # defaults to today
    notes: Optional[str] = ""

class LeetCodeManualStats(BaseModel):
    username: str
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    ranking: Optional[int] = 0
    acceptance_rate: Optional[float] = 0.0
