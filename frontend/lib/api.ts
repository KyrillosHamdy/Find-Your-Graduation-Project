export interface IntentProfile {
  domains: string[];
  skill_level: "beginner" | "intermediate" | "advanced";
  months_available: number;
  team_size: number;
  preferred_stack: string[];
  interests_text: string;
  avoid_text: string;
}

export interface PaperEnriched {
  title: string;
  first_author_lastname: string;
  year: number;
  confident: boolean;
  arxiv_id?: string;
  arxiv_url?: string;
  verified: boolean;
}

export interface Card {
  id: number;
  title: string;
  tagline: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  estimated_weeks: number;
  stack: string[];
  research_area: string;
  paper: PaperEnriched;
  fit_reason: string;
}

export interface BlueprintWhat {
  description: string;
  problem_statement: string;
  in_scope: string[];
  out_of_scope: string[];
}

export interface BlueprintWhy {
  importance: string;
  paper_relevance: string;
  student_fit: string;
}

export interface StackItem {
  tool: string;
  reason: string;
}

export interface Phase {
  phase: number;
  name: string;
  description: string;
}

export interface Risk {
  risk: string;
  mitigation: string;
}

export interface BlueprintHow {
  architecture_overview: string;
  stack: StackItem[];
  phases: Phase[];
  risks: Risk[];
}

export interface Blueprint {
  what: BlueprintWhat;
  why: BlueprintWhy;
  how: BlueprintHow;
}

export interface RecommendResponse {
  session_id: string;
  cards: Card[];
}

export interface ExpandResponse {
  card_id: number;
  blueprint: Blueprint;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function getRecommendations(profile: IntentProfile): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE_URL}/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ profile }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch recommendations: ${res.statusText}`);
  }
  return res.json();
}

export async function expandCard(sessionId: string, cardId: number): Promise<ExpandResponse> {
  const res = await fetch(`${API_BASE_URL}/expand/${sessionId}/${cardId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to expand card: ${res.statusText}`);
  }
  return res.json();
}

export async function getSessionState(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/session/${sessionId}`);
  if (!res.ok) {
    throw new Error(`Failed to get session state: ${res.statusText}`);
  }
  return res.json();
}
