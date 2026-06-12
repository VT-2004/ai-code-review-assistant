from pydantic import BaseModel
from typing import List, Optional

# --- Request models ---
class ReviewRequest(BaseModel):
    repo_url: str
    max_files: int = 30

class ChatRequest(BaseModel):
    question: str
    repo_url: Optional[str] = None

# --- Response models ---
class Issue(BaseModel):
    type: str          # bug / security / style / performance
    severity: str      # critical / high / medium / low
    line_hint: str     # rough location e.g. "def connect()" 
    description: str
    suggestion: str

class FileReview(BaseModel):
    file_path: str
    language: str
    score: int         # 0-100
    issues: List[Issue]
    summary: str

class ReviewResponse(BaseModel):
    repo_url: str
    overall_score: int
    total_files: int
    total_issues: int
    file_reviews: List[FileReview]
    top_concerns: List[str]

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]  # file paths used to answer