# CV Builder

**Live demo:** https://cv-builder-8lfe.onrender.com
(free tier — spins down when idle, first load after a while may take ~30-60s)

A small web app that turns a form (education, experience, skills, publications,
projects, extracurricular activities) into a PDF resume, using
[RenderCV](https://github.com/rendercv/rendercv)'s `classic` theme (Typst-based)
as the rendering engine.

- `backend/` — FastAPI app. `POST /api/generate-cv` converts the submitted JSON
  into RenderCV's YAML schema (`yaml_builder.py`), shells out to the `rendercv`
  CLI, and streams back the generated PDF.
- `frontend/` — a single static HTML page (vanilla JS, no build step). Supports
  drag-to-reorder entries/highlights and autosaves a draft to `localStorage`.

## Run locally

```bash
python3.12 -m venv venv
./venv/bin/pip install -r backend/requirements.txt
cd backend && ../venv/bin/uvicorn main:app --port 8000
```

Then open http://localhost:8000.

## Deploy

`render.yaml` at the repo root is a [Render](https://render.com) Blueprint —
on Render, "New +" → "Blueprint", point it at this repo, and it configures the
web service automatically (Python 3.12, `pip install`, `uvicorn` start command).

Note: the `/api/generate-cv` endpoint has no authentication — anyone with the
deployed URL can call it. Fine for personal/portfolio use; add auth or rate
limiting first if that's a concern.
