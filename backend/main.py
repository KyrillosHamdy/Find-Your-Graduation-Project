from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import RecommendRequest, RecommendResponse, ExpandResponse, SessionState
from gemini import GeminiError, get_topic_shortlist, get_raw_cards, get_blueprint
from arxiv import enrich_cards
import session_store

app = FastAPI(title="Graduation Project Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    """
    Full two-step flow:
      1. Gemini → 10 topic candidates
      2. Gemini → 5 expanded cards with paper references
      3. arXiv API → validate and enrich each paper
      4. Store in session, return session_id + cards
    """
    profile = req.profile

    try:
        # Step 1: get 10 topics
        topics = await get_topic_shortlist(profile)

        # Step 2: expand to 5 raw cards
        raw_cards = await get_raw_cards(profile, topics)
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    # Step 3: validate papers via arXiv
    cards = await enrich_cards(raw_cards)

    # Step 4: store and return
    session_id = session_store.create_session(profile, cards)
    return RecommendResponse(session_id=session_id, cards=cards)


@app.post("/expand/{session_id}/{card_id}", response_model=ExpandResponse)
async def expand(session_id: str, card_id: int):
    """
    On-demand blueprint generation for one card.
    Cached — calling twice returns the stored blueprint without re-calling Gemini.
    """
    # check cache first
    cached = session_store.get_blueprint(session_id, card_id)
    if cached:
        return ExpandResponse(card_id=card_id, blueprint=cached)

    # get the card
    card = session_store.get_card(session_id, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Session or card not found")

    # get profile
    session = session_store.get_session(session_id)
    profile = session["profile"]

    try:
        # call Gemini
        blueprint = await get_blueprint(profile, card.model_dump())
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    # cache and return
    session_store.save_blueprint(session_id, card_id, blueprint)
    return ExpandResponse(card_id=card_id, blueprint=blueprint)


@app.get("/session/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """
    Returns full session state — profile, cards, and any cached blueprints.
    Useful for restoring state if the user refreshes the page.
    """
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return SessionState(
        profile=session["profile"],
        cards=session["cards"],
        blueprints={
            card_id: bp
            for card_id, bp in session["blueprints"].items()
        },
    )
