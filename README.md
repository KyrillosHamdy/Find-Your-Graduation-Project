# Find Your Graduation Project

Gemini-powered graduation project advisor for CS students.

The app takes one student profile form and returns five grounded graduation project ideas. Each idea includes a suggested or arXiv-verified research paper, a realistic timeline, a recommended tech stack, and an expandable What / Why / How blueprint.

## Demo

[Watch the demo video](https://drive.google.com/file/d/1oNodiN7wpiOPQxOgC9PzllLrGsXFqolZ/view?usp=sharing)

---

## Stack

| Layer | Tech |
| --- | --- |
| Backend | Python 3.11+, FastAPI, httpx, Pydantic v2 |
| LLM | Gemini API, `gemini-2.5-flash` by default |
| Paper validation | arXiv public API, no key required |
| Session storage | In-memory Python dict inside the FastAPI process |
| Frontend | Next.js 15, React, TypeScript, CSS Modules |

---

## What The App Does

1. The user fills an onboarding form with domains, skill level, timeline, team size, preferred stack, interests, and topics to avoid.
2. The backend asks Gemini for 10 ranked topic candidates.
3. The backend asks Gemini to expand the best five topics into full project cards.
4. Each card includes a research paper title, first author last name, year, and confidence flag.
5. The backend checks the paper against arXiv and adds an arXiv ID/URL when it can verify the paper.
6. The frontend shows the five ideas, paper information, estimated timeline, stack, and fit reason.
7. The user can click Expand on any card to generate a cached What / Why / How project blueprint.

---

## Project Structure

```text
files/
|-- .env
|   Root environment file used by the backend when run from this workspace.
|
|-- README.md
|   Main project documentation.
|
|-- backend/
|   |-- .env.example
|   |   Example backend environment variables.
|   |
|   |-- requirements.txt
|   |   Python dependencies for the FastAPI backend.
|   |
|   |-- main.py
|   |   FastAPI application entry point.
|   |   Defines /healthz, /recommend, /expand/{session_id}/{card_id}, and /session/{session_id}.
|   |
|   |-- schemas.py
|   |   Pydantic request, response, card, paper, topic, and blueprint models.
|   |
|   |-- prompts.py
|   |   Prompt builders for topic shortlisting, card expansion, and blueprint generation.
|   |
|   |-- gemini.py
|   |   Gemini REST client.
|   |   Uses JSON mode, retries malformed JSON once, supports GEMINI_MODEL, and raises clean GeminiError failures.
|   |
|   |-- arxiv.py
|   |   arXiv validation/enrichment logic for suggested papers.
|   |
|   |-- session_store.py
|   |   In-memory session and blueprint cache.
|   |
|   |-- .venv/
|   |   Local Python virtual environment. Generated locally, not source code.
|   |
|   `-- __pycache__/
|       Python cache files. Generated locally.
|
`-- frontend/
    |-- package.json
    |   Frontend scripts and dependencies.
    |
    |-- package-lock.json
    |   Locked npm dependency versions.
    |
    |-- next.config.ts
    |   Next.js config.
    |
    |-- tsconfig.json
    |   TypeScript config.
    |
    |-- .eslintrc.json
    |   ESLint config.
    |
    |-- app/
    |   |-- layout.tsx
    |   |   Root Next.js layout.
    |   |
    |   |-- globals.css
    |   |   Global styles and CSS variables.
    |   |
    |   |-- page.tsx
    |   |   Landing page.
    |   |
    |   |-- page.module.css
    |   |   Landing page styles.
    |   |
    |   |-- onboard/
    |   |   |-- page.tsx
    |   |   |   Student profile form.
    |   |   |
    |   |   `-- onboard.module.css
    |   |       Onboarding page styles.
    |   |
    |   `-- board/
    |       |-- page.tsx
    |       |   Results board, idea cards, paper display, timeline, and blueprint expansion UI.
    |       |
    |       `-- board.module.css
    |           Results board styles.
    |
    |-- lib/
    |   `-- api.ts
    |       Typed frontend API client for the backend.
    |
    |-- public/
    |   Static assets.
    |
    |-- node_modules/
    |   Installed npm dependencies. Generated locally.
    |
    `-- .next/
        Next.js build/dev cache. Generated locally. Safe to delete if Next serves stale chunks.
```

---

## Environment Variables

Create or edit the root `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

`GEMINI_API_KEY` is required. You can create one in Google AI Studio:

```text
https://aistudio.google.com/app/apikey
```

`GEMINI_MODEL` is optional. If omitted, the backend uses:

```text
gemini-2.5-flash
```

If a model returns 404, use a model that supports `generateContent`.

---

## First-Time Setup

### 1. Backend Setup

From the project root:

```powershell
cd "D:\ML\project advisor\files\backend"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Make sure the root `.env` file exists at:

```text
D:\ML\project advisor\files\.env
```

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 2. Frontend Setup

Open a second terminal:

```powershell
cd "D:\ML\project advisor\files\frontend"
npm install
```

---

## How To Run The Project Each Time

You need two terminals: one for the backend and one for the frontend.

### Terminal 1: Start Backend

```powershell
cd "D:\ML\project advisor\files\backend"
.venv\Scripts\activate -m uvicorn main:app --reload --port 8000
```

Backend URLs:

```text
API:    http://localhost:8000
Docs:   http://localhost:8000/docs
Health: http://localhost:8000/healthz
```

### Terminal 2: Start Frontend

```powershell
cd "D:\ML\project advisor\files\frontend"
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

Then open:

```text
http://localhost:3000
```

---

## API Routes

| Method | Route | Description |
| --- | --- | --- |
| GET | `/healthz` | Backend health check |
| POST | `/recommend` | Submit a student profile and receive a session ID plus five idea cards |
| POST | `/expand/{session_id}/{card_id}` | Generate or return a cached blueprint for one card |
| GET | `/session/{session_id}` | Restore a session with profile, cards, and cached blueprints |

---

## Backend Flow

### `/recommend`

1. Receives a `RecommendRequest`.
2. Calls Gemini prompt 1 to generate 10 topic candidates.
3. Calls Gemini prompt 2 to generate five project cards.
4. Validates/enriches paper references through arXiv.
5. Stores the session in memory.
6. Returns `session_id` and cards to the frontend.

### `/expand/{session_id}/{card_id}`

1. Checks whether a blueprint is already cached.
2. Loads the selected card and original student profile.
3. Calls Gemini prompt 3 if needed.
4. Stores the blueprint in memory.
5. Returns the blueprint to the frontend.

---

## Frontend Flow

1. `/` shows the landing page.
2. `/onboard` collects the student profile.
3. The frontend posts the profile to `POST /recommend`.
4. The frontend navigates to `/board` with the returned cards.
5. `/board` displays:
   - project title
   - research area
   - difficulty
   - tagline and description
   - tech stack
   - suggested or verified paper
   - author/year
   - timeline as `About X weeks`
   - fit reason
6. Clicking Expand calls `POST /expand/{session_id}/{card_id}` and shows the blueprint.

---

## Validation And Error Handling

The Gemini client in `backend/gemini.py`:

- sends requests to the Gemini REST API
- uses `x-goog-api-key` instead of putting the API key in the URL
- requests JSON output with `responseMimeType: application/json`
- retries once when Gemini returns malformed JSON
- reports Gemini failures as clean backend errors instead of raw ASGI crashes

The arXiv validation in `backend/arxiv.py` is best-effort:

- verified papers get `verified: true` and may include `arxiv_url`
- unverified papers still appear as suggested papers
- this avoids hiding useful project ideas just because arXiv could not match the paper exactly

---

## Troubleshooting

### Gemini 404 model error

If the backend says the Gemini model was not found, update `.env`:

```env
GEMINI_MODEL=gemini-2.5-flash
```

Then restart the backend.

### Gemini invalid JSON error

The backend already retries malformed JSON once. If it still fails:

- retry the request
- reduce how broad the student profile is
- check whether the selected Gemini model supports JSON generation

### Frontend error: `Cannot find module './147.js'`

This usually means the Next.js `.next` cache is stale or corrupted.

Stop the frontend dev server, then run:

```powershell
cd "D:\ML\project advisor\files\frontend"
Remove-Item -LiteralPath .next -Recurse -Force
npm run dev
```

### Backend changes are not appearing

Restart the backend terminal:

```powershell
Ctrl+C
uvicorn main:app --reload --port 8000
```

### Frontend changes are not appearing

Restart the frontend terminal:

```powershell
Ctrl+C
npm run dev
```

---

## Development Checks

Backend syntax check:

```powershell
cd "D:\ML\project advisor\files"
backend\.venv\Scripts\python.exe -m py_compile backend\gemini.py backend\main.py backend\arxiv.py
```

Frontend type check:

```powershell
cd "D:\ML\project advisor\files\frontend"
npx tsc --noEmit --pretty false
```

Production build:

```powershell
cd "D:\ML\project advisor\files\frontend"
npm run build
```

Note: the current project may still have unrelated lint warnings/errors in older frontend files. The dev server can still run with:

```powershell
npm run dev
```

---

## Notes

- Sessions are stored in memory. Restarting the backend clears all sessions and cached blueprints.
- The Gemini free tier can rate-limit requests.
- arXiv validation is best-effort, so a paper can be useful even if it is shown as suggested instead of verified.
