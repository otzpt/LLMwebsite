# LLMwebsite

Chat frontend for [VOIDSEED](https://github.com/otzpt/VOIDSEED) tiny-llm — a
155M-parameter GPT trained from scratch on security documentation, with
retrieval-augmented generation. Public demo for the Stardance Challenge.

Live: **[llmwebsite.vercel.app](https://llmwebsite.vercel.app)**

## Layout

```
index.html    the page
style.css     styling
main.js       sends chat messages, renders the replies
backend.py    a local Flask server for dev/testing (see below)
```

Plain HTML/JS/CSS on purpose — no build step, no framework, deploys as-is.

## Two backends, don't mix them up

**`backend.py`** — a local Flask server, for running the model on your own
machine while developing. `POST /chat`, body `{"message": "..."}`, response
`{"response": "..."}`. This is what `main.js`'s `BACKEND_URL` currently points
at (`http://localhost:5000/chat`).

**The production API** — a separate FastAPI service, deployed on Hack Club
Nest (not this repo, not Vercel — Stardance's rules don't allow Hugging Face
for hosting, so this runs on Nest instead). Different contract:

```
POST /generate
Body:     {"prompt": "..."}
Response: {"answer": "..."}

GET /health  ->  {"status": "ok"}
```

10 requests/minute per IP, `prompt` capped at 2000 chars. Not yet reachable
publicly — needs a domain pointed at the Nest VM first (in progress). Once
that's live, switching `main.js` from the dev backend to production means
changing `BACKEND_URL` **and** the request/response field names (`message`/
`response` -> `prompt`/`answer`), not just the URL.

Measured on the Nest VM (2 shared vCPUs, no GPU): ~50s per reply, 100 tokens,
no KV-cache in the model. The frontend needs a real loading state, not a
2-second spinner.

## Local dev

```bash
# backend (needs the tinyllm2 checkout at the path backend.py imports from)
pip install flask flask-cors torch tiktoken
python3 backend.py          # localhost:5000

# frontend
python3 -m http.server 8000 # or just open index.html directly
```

## Deployment

Vercel, project `llmwebsite`, auto-deployed by
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) on every push
to `main`. Needs a `VERCEL_TOKEN` repository secret (Vercel -> Account
Settings -> Tokens), added with:

```bash
gh secret set VERCEL_TOKEN -R otzpt/LLMwebsite
```

Without it, the workflow still runs but skips the actual deploy step rather
than failing (see the workflow file). Vercel's own GitHub integration isn't
connected — it needs the Vercel GitHub App authorised in a browser, which
isn't something a script can do, hence the Actions workflow instead.

The project's deployment protection (Vercel's SSO gate, which is enabled by
default on new projects and would otherwise block every visitor) has been
turned off — this is meant to be a public demo.
