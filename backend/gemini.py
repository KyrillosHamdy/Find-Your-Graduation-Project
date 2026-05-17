import os
from typing import TypeVar
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from schemas import (
    IntentProfile,
    TopicShortlist,
    TopicCandidate,
    CardRaw,
    Blueprint,
    BlueprintResponse,
)
from prompts import prompt_1_shortlist, prompt_2_expand_cards, prompt_3_blueprint

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_MODEL = GEMINI_MODEL.removeprefix("models/")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiError(RuntimeError):
    """Raised when the Gemini API cannot complete a request."""


class CardsResponse(BaseModel):
    cards: list[CardRaw]


JsonModel = TypeVar("JsonModel", bound=BaseModel)


def _clean_json(raw: str) -> str:
    """Strip markdown code fences if Gemini wraps the response in them."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


async def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response."""
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is not set in .env")

    if not GEMINI_MODEL:
        raise GeminiError("GEMINI_MODEL is empty")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        url = f"{GEMINI_BASE_URL}/{GEMINI_MODEL}:generateContent"
        try:
            response = await client.post(
                url,
                headers={"x-goog-api-key": GEMINI_API_KEY},
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            detail = _gemini_error_detail(e.response)
            raise GeminiError(
                f"Gemini request failed for model '{GEMINI_MODEL}': {detail}"
            ) from e
        except httpx.HTTPError as e:
            raise GeminiError(f"Gemini request failed: {e}") from e
        data = response.json()

    try:
        candidate = data["candidates"][0]
        finish_reason = candidate.get("finishReason")
        text = candidate["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise GeminiError(f"Unexpected Gemini response shape: {data}") from e

    if finish_reason and finish_reason not in {"STOP", "FINISH_REASON_UNSPECIFIED"}:
        raise GeminiError(
            f"Gemini stopped before returning complete JSON: {finish_reason}"
        )

    return text


async def _call_gemini_json(prompt: str, model: type[JsonModel]) -> JsonModel:
    """Call Gemini and parse a complete JSON object into a Pydantic model."""
    retry_prompt = (
        f"{prompt}\n\n"
        "Critical formatting requirement: return one complete valid JSON object "
        "that exactly matches the schema. Do not truncate the response."
    )

    last_error: Exception | None = None
    for attempt_prompt in (prompt, retry_prompt):
        try:
            raw = await _call_gemini(attempt_prompt)
            cleaned = _clean_json(raw)
            return model.model_validate_json(cleaned)
        except (GeminiError, ValidationError) as e:
            last_error = e

    raise GeminiError(
        f"Gemini returned invalid JSON for {model.__name__}"
    ) from last_error


def _gemini_error_detail(response: httpx.Response) -> str:
    """Extract Google's error message without including secrets."""
    try:
        body = response.json()
    except ValueError:
        body = response.text

    if isinstance(body, dict):
        message = body.get("error", {}).get("message")
        if message:
            return f"{response.status_code} {message}"

    return f"{response.status_code} {response.reason_phrase}"


async def get_topic_shortlist(profile: IntentProfile) -> list[TopicCandidate]:
    """Prompt 1: get 10 ranked topic candidates."""
    prompt = prompt_1_shortlist(profile)
    parsed = await _call_gemini_json(prompt, TopicShortlist)
    return parsed.topics


async def get_raw_cards(
    profile: IntentProfile,
    topics: list[TopicCandidate],
) -> list[CardRaw]:
    """Prompt 2: expand top 10 topics into 5 grounded cards."""
    prompt = prompt_2_expand_cards(profile, topics)
    parsed = await _call_gemini_json(prompt, CardsResponse)
    return parsed.cards


async def get_blueprint(
    profile: IntentProfile,
    card: dict,
) -> Blueprint:
    """Prompt 3: generate What / Why / How blueprint for one card."""
    prompt = prompt_3_blueprint(profile, card)
    parsed = await _call_gemini_json(prompt, BlueprintResponse)
    return parsed.blueprint
