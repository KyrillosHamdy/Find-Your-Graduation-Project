from pydantic import BaseModel, Field
from typing import Optional


# ─── Input ────────────────────────────────────────────────────────────────────

class IntentProfile(BaseModel):
    domains: list[str] = Field(..., description="e.g. ['NLP', 'Computer Vision']")
    skill_level: str = Field(..., description="beginner | intermediate | advanced")
    months_available: int = Field(..., ge=1, le=24)
    team_size: int = Field(..., ge=1, le=10)
    preferred_stack: list[str] = Field(default_factory=list)
    interests_text: str = Field(..., max_length=500)
    avoid_text: str = Field(default="", max_length=500)


# ─── Prompt 1 output ──────────────────────────────────────────────────────────

class TopicCandidate(BaseModel):
    rank: int
    title: str
    rationale: str


class TopicShortlist(BaseModel):
    topics: list[TopicCandidate]


# ─── Prompt 2 output ──────────────────────────────────────────────────────────

class PaperRaw(BaseModel):
    """What Gemini returns — no arXiv data yet."""
    title: str
    first_author_lastname: str
    year: int
    confident: bool


class PaperEnriched(BaseModel):
    """After arXiv validation step."""
    title: str
    first_author_lastname: str
    year: int
    confident: bool
    arxiv_id: Optional[str] = None
    arxiv_url: Optional[str] = None
    verified: bool = False


class CardRaw(BaseModel):
    """What Gemini returns from Prompt 2."""
    id: int
    title: str
    tagline: str
    description: str
    difficulty: str  # beginner | intermediate | advanced
    estimated_weeks: int
    stack: list[str]
    research_area: str
    paper: PaperRaw
    fit_reason: str


class Card(BaseModel):
    """Final card after arXiv enrichment — sent to frontend."""
    id: int
    title: str
    tagline: str
    description: str
    difficulty: str
    estimated_weeks: int
    stack: list[str]
    research_area: str
    paper: PaperEnriched
    fit_reason: str


# ─── Prompt 3 output ──────────────────────────────────────────────────────────

class BlueprintWhat(BaseModel):
    description: str
    problem_statement: str
    in_scope: list[str]
    out_of_scope: list[str]


class BlueprintWhy(BaseModel):
    importance: str
    paper_relevance: str
    student_fit: str


class StackItem(BaseModel):
    tool: str
    reason: str


class Phase(BaseModel):
    phase: int
    name: str
    description: str


class Risk(BaseModel):
    risk: str
    mitigation: str


class BlueprintHow(BaseModel):
    architecture_overview: str
    stack: list[StackItem]
    phases: list[Phase]
    risks: list[Risk]


class Blueprint(BaseModel):
    what: BlueprintWhat
    why: BlueprintWhy
    how: BlueprintHow


class BlueprintResponse(BaseModel):
    blueprint: Blueprint


# ─── API request / response shapes ───────────────────────────────────────────

class RecommendRequest(BaseModel):
    profile: IntentProfile


class RecommendResponse(BaseModel):
    session_id: str
    cards: list[Card]


class ExpandResponse(BaseModel):
    card_id: int
    blueprint: Blueprint


class SessionState(BaseModel):
    profile: IntentProfile
    cards: list[Card]
    blueprints: dict[int, Blueprint] = Field(default_factory=dict)
