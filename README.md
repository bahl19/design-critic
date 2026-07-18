# 🎨 Design Critic — Multi-Agent AI Design Review

> Powered by OpenRouter · Multi-agent screenshot critique in one API call

Design Critic is a multi-agent AI system that analyzes a product or app screenshot and delivers a structured design critique — visual design, UX heuristics, accessibility, and market positioning — synthesized into one prioritized, scored report in seconds.

---

## 🤖 Agent Architecture

| Agent | Model | Role |
|-------|-------|------|
| 🖌️ Visual Analysis | `openai/gpt-4o` | Layout, color/contrast, typography, hierarchy, spacing, branding |
| 🧭 UX Critique | `openai/gpt-4o` | Nielsen's heuristics, flow friction, discoverability, affordances |
| ♿ Accessibility | `openai/gpt-4o-mini` | Color contrast, text size, tap-target size, color-only meaning, alt-text cues |
| 📈 Market Research | `openai/gpt-4o:online` | Web-search-grounded comparison against current design trends & competitors |
| ⚖️ Report Agent | `openai/gpt-4.1` | Synthesizes all four critiques into one prioritized, deduplicated report |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/bahl19/design-critic.git
cd design-critic
```

### 2. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file in the root folder (or copy `.env.example`):
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 4. Run the app
```bash
uvicorn main:app --reload
```

### 5. Upload a screenshot
Open **http://localhost:8000**, drop in a product/app screenshot, and watch all 5 agents fire.

---

## 🏗️ Project Structure

```
DESIGN-CRITIC/
├── main.py                   # FastAPI app: serves the frontend + POST /api/analyze
├── api/
│   └── index.py               # Vercel entrypoint, re-exports main.app
├── frontend/
│   └── index.html              # Single-page UI (drag/drop upload, results view)
├── src/
│   ├── orchestrator.py         # Fans out to the 4 specialist agents, then the Report Agent
│   ├── openrouter_client.py     # OpenRouter HTTP client + strict JSON schema helpers
│   ├── schemas.py                # Pydantic models for findings, agent results, final report
│   └── agents/
│       ├── base.py                # Shared VisionAgent base class (prompt -> JSON -> AgentResult)
│       ├── visual_agent.py
│       ├── ux_agent.py
│       ├── accessibility_agent.py
│       ├── market_agent.py
│       └── report_agent.py
├── vercel.json                # Routes all traffic to api/index.py, 60s max duration
├── requirements.txt           # Dependencies
└── .env                       # API key (not committed)
```

---

## 🧠 How It Works

```
Screenshot Upload
    ↓
Visual Analysis Agent   →  Layout, color, typography, hierarchy
Ux Critique Agent       →  Heuristics, flow friction, affordances       }  run concurrently
Accessibility Agent     →  Contrast, tap targets, legibility
Market Research Agent   →  Live web search vs. competitors & trends
    ↓
Report Agent (LLM)      →  Merges, dedupes, and prioritizes findings
    ↓
JSON Response           →  Overall score, executive summary, top fixes
```

Each specialist returns strict JSON (`score`, `summary`, `findings[]`) validated against a Pydantic schema via OpenRouter's `json_schema` structured outputs. If a specialist fails, the rest still return and the response is marked `partial_failure` with the error surfaced. If the Report Agent itself fails, the API falls back to a mechanical rollup of the highest-severity findings instead of losing the response.

---

## 🛠️ Tech Stack

- **Backend** — FastAPI
- **LLM Routing** — OpenRouter (GPT-4o, GPT-4o-mini, GPT-4o `:online`, GPT-4.1)
- **Validation** — Pydantic + strict JSON schema structured outputs
- **Frontend** — Single-page vanilla HTML/CSS/JS (`frontend/index.html`)
- **Agent Pattern** — Parallel specialist agents (`asyncio.gather`) + one synthesis agent
- **Hosting** — Vercel, as a single Python serverless function

---

## 📡 API Reference

### `POST /api/analyze`

`multipart/form-data` with a single field `image` (any `image/*` content type, max ~4MB to stay under Vercel's request body cap).

<details>
<summary><strong>Example response (<code>AnalyzeResponse</code>)</strong></summary>

```json
{
  "design_label": "design",
  "final_report": {
    "overall_score": 78,
    "executive_summary": "...",
    "prioritized_recommendations": [
      { "category": "...", "severity": "high", "description": "...", "recommendation": "..." }
    ]
  },
  "agents": {
    "visual": { "agent_name": "Visual Analysis", "model_used": "openai/gpt-4o", "score": 82, "summary": "...", "findings": [ /* ... */ ], "error": null },
    "ux": { "...": "..." },
    "accessibility": { "...": "..." },
    "market": { "...": "..." }
  },
  "partial_failure": false,
  "errors": []
}
```

</details>

Severity is one of `low | medium | high | critical`.

---

## 📋 Requirements

```
fastapi
uvicorn[standard]
httpx
python-multipart
python-dotenv
pydantic
```

---

## ☁️ Deployment (Vercel)

The app deploys as a single Python serverless function:

- `vercel.json` rewrites all routes to `api/index.py`, which imports the FastAPI app from `main.py`.
- `functions."api/index.py".maxDuration` is set to 60s to give the 5 model calls room to complete.
- Set `OPENROUTER_API_KEY` as an environment variable in your Vercel project settings — never commit it (see `.env.example`).

```bash
vercel deploy
```

---

## ⚠️ Notes

- `AnalyzeResponse.design_label` is a stubbed field reserved for a future multi-design A/B comparison feature; it's currently unused and always `"design"`.
- The Market Research agent uses OpenRouter's `:online` suffix to ground its critique in live web search results.

---

## 👨‍💻 Built By

**Shitij Bahl**
GitHub: [github.com/bahl19](https://github.com/bahl19)

---

> "One screenshot in, a design-team-grade critique out."
