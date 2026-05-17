import uuid
from datetime import datetime, timedelta
from schemas import IntentProfile, Card, Blueprint

# sessions live as long as the FastAPI process is running
# { session_id: { profile, cards, blueprints, created_at } }
_store: dict[str, dict] = {}

SESSION_TTL_HOURS = 6


def _is_expired(session: dict) -> bool:
    return datetime.utcnow() - session["created_at"] > timedelta(hours=SESSION_TTL_HOURS)


def create_session(profile: IntentProfile, cards: list[Card]) -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "profile": profile,
        "cards": cards,
        "blueprints": {},
        "created_at": datetime.utcnow(),
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    session = _store.get(session_id)
    if session is None:
        return None
    if _is_expired(session):
        del _store[session_id]
        return None
    return session


def get_card(session_id: str, card_id: int) -> Card | None:
    session = get_session(session_id)
    if session is None:
        return None
    for card in session["cards"]:
        if card.id == card_id:
            return card
    return None


def get_blueprint(session_id: str, card_id: int) -> Blueprint | None:
    session = get_session(session_id)
    if session is None:
        return None
    return session["blueprints"].get(card_id)


def save_blueprint(session_id: str, card_id: int, blueprint: Blueprint) -> None:
    session = get_session(session_id)
    if session:
        session["blueprints"][card_id] = blueprint
