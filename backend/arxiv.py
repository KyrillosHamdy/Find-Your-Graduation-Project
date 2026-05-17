import httpx
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

from schemas import CardRaw, Card, PaperEnriched

ARXIV_API = "https://export.arxiv.org/api/query"
SIMILARITY_THRESHOLD = 0.75  # minimum title match to count as verified


def _similarity(a: str, b: str) -> float:
    """Simple fuzzy string similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _parse_arxiv_response(xml_text: str) -> list[dict]:
    """Parse Atom XML from arXiv API into a list of entry dicts."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        id_el = entry.find("atom:id", ns)
        if title_el is None or id_el is None:
            continue
        arxiv_url = id_el.text.strip()
        # extract ID from URL like https://arxiv.org/abs/2301.00001
        arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else None
        entries.append({
            "title": title_el.text.strip().replace("\n", " "),
            "arxiv_id": arxiv_id,
            "arxiv_url": arxiv_url,
        })
    return entries


async def validate_paper(paper: CardRaw.model_fields["paper"].annotation) -> PaperEnriched: # type: ignore
    """Query arXiv for a paper and return enriched paper data."""
    # if Gemini itself wasn't confident, skip the lookup
    if not paper.confident:
        return PaperEnriched(
            title=paper.title,
            first_author_lastname=paper.first_author_lastname,
            year=paper.year,
            confident=False,
            verified=False,
        )

    query = f"ti:{paper.title} AND au:{paper.first_author_lastname}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                ARXIV_API,
                params={"search_query": query, "max_results": 3, "sortBy": "relevance"},
            )
            response.raise_for_status()
            entries = _parse_arxiv_response(response.text)
    except Exception:
        # network or parse error — return unverified rather than crashing
        return PaperEnriched(
            title=paper.title,
            first_author_lastname=paper.first_author_lastname,
            year=paper.year,
            confident=paper.confident,
            verified=False,
        )

    # check each result for a good title match
    for entry in entries:
        score = _similarity(paper.title, entry["title"])
        if score >= SIMILARITY_THRESHOLD:
            return PaperEnriched(
                title=entry["title"],  # use the canonical arXiv title
                first_author_lastname=paper.first_author_lastname,
                year=paper.year,
                confident=paper.confident,
                arxiv_id=entry["arxiv_id"],
                arxiv_url=entry["arxiv_url"],
                verified=True,
            )

    # no good match found
    return PaperEnriched(
        title=paper.title,
        first_author_lastname=paper.first_author_lastname,
        year=paper.year,
        confident=paper.confident,
        verified=False,
    )


async def enrich_cards(raw_cards: list[CardRaw]) -> list[Card]:
    """Validate papers for all cards and return enriched Card objects."""
    enriched = []
    for raw in raw_cards:
        enriched_paper = await validate_paper(raw.paper)
        enriched.append(
            Card(
                id=raw.id,
                title=raw.title,
                tagline=raw.tagline,
                description=raw.description,
                difficulty=raw.difficulty,
                estimated_weeks=raw.estimated_weeks,
                stack=raw.stack,
                research_area=raw.research_area,
                paper=enriched_paper,
                fit_reason=raw.fit_reason,
            )
        )
    return enriched
