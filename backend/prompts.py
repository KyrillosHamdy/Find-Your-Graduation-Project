from schemas import IntentProfile, TopicCandidate


def build_profile_block(profile: IntentProfile) -> str:
    return f"""
Student Profile:
- Domains of interest: {", ".join(profile.domains)}
- Skill level: {profile.skill_level}
- Timeline: {profile.months_available} months
- Team size: {profile.team_size} person(s)
- Preferred tech stack: {", ".join(profile.preferred_stack) if profile.preferred_stack else "No preference"}
- Interests / free text: {profile.interests_text}
- Topics to avoid: {profile.avoid_text if profile.avoid_text else "None"}
""".strip()


def prompt_1_shortlist(profile: IntentProfile) -> str:
    profile_block = build_profile_block(profile)
    return f"""
You are an experienced computer science academic advisor helping a student find the right graduation project.

{profile_block}

Your task:
Generate exactly 10 distinct, ranked graduation project topic candidates tailored to this student's profile.

Rules:
- Topics must be genuinely distinct — no overlap in problem domain or approach.
- Match the difficulty and scope to the student's skill level and timeline.
- Consider what is publishable AND buildable within the given months.
- Do NOT suggest trivial CRUD apps to advanced students, or research-heavy projects to beginners.
- Think about what a real academic advisor would recommend.

Return ONLY a valid JSON object. No explanation, no markdown, no code blocks. Just raw JSON.

Schema:
{{
  "topics": [
    {{
      "rank": 1,
      "title": "string",
      "rationale": "one sentence explaining why this fits this specific student"
    }},
    ...10 items total
  ]
}}
""".strip()


def prompt_2_expand_cards(profile: IntentProfile, topics: list[TopicCandidate]) -> str:
    profile_block = build_profile_block(profile)
    topics_block = "\n".join(
        f"{t.rank}. {t.title} — {t.rationale}" for t in topics
    )
    return f"""
You are an experienced computer science academic advisor.

{profile_block}

You previously suggested these 10 project topics (ranked):
{topics_block}

Your task:
Select the best 5 topics from the list above and expand each into a full project card.

For each card, you MUST include a real, existing research paper that is directly relevant.
IMPORTANT: Only cite papers you are highly confident exist. If you are not sure a paper exists with that exact title and author, set "confident" to false. Never invent paper titles or authors.

Return ONLY a valid JSON object. No explanation, no markdown, no code blocks. Just raw JSON.

Schema:
{{
  "cards": [
    {{
      "id": 1,
      "title": "string",
      "tagline": "one punchy sentence that sells the idea",
      "description": "2-3 sentence project description",
      "difficulty": "beginner | intermediate | advanced",
      "estimated_weeks": number,
      "stack": ["string", ...],
      "research_area": "string (e.g. NLP, Computer Vision, Security)",
      "paper": {{
        "title": "exact paper title",
        "first_author_lastname": "string",
        "year": number,
        "confident": true or false
      }},
      "fit_reason": "one sentence: why this specific project fits this specific student's profile"
    }},
    ...5 items total
  ]
}}
""".strip()


def prompt_3_blueprint(profile: IntentProfile, card_dict: dict) -> str:
    profile_block = build_profile_block(profile)
    return f"""
You are a senior software engineer and academic advisor.

{profile_block}

The student has selected this graduation project:
- Title: {card_dict["title"]}
- Description: {card_dict["description"]}
- Research area: {card_dict["research_area"]}
- Suggested stack: {", ".join(card_dict["stack"])}
- Referenced paper: "{card_dict["paper"]["title"]}" by {card_dict["paper"]["first_author_lastname"]} ({card_dict["paper"]["year"]})

Your task:
Generate a detailed supervisor-ready project blueprint with exactly three sections: what, why, how.

Return ONLY a valid JSON object. No explanation, no markdown, no code blocks. Just raw JSON.

Schema:
{{
  "blueprint": {{
    "what": {{
      "description": "clear 2-3 sentence project description",
      "problem_statement": "the core problem this project solves",
      "in_scope": ["list of things the project will do"],
      "out_of_scope": ["list of things explicitly NOT in scope"]
    }},
    "why": {{
      "importance": "why this problem matters in research or industry",
      "paper_relevance": "how the referenced paper connects to and grounds this project",
      "student_fit": "why this student's specific profile makes them well-suited for this project"
    }},
    "how": {{
      "architecture_overview": "paragraph describing the system architecture and main components",
      "stack": [
        {{
          "tool": "tool or framework name",
          "reason": "why this tool is appropriate for this project"
        }}
      ],
      "phases": [
        {{
          "phase": 1,
          "name": "phase name",
          "description": "what gets built or researched in this phase"
        }}
      ],
      "risks": [
        {{
          "risk": "description of the risk",
          "mitigation": "how to reduce or handle this risk"
        }}
      ]
    }}
  }}
}}
""".strip()
