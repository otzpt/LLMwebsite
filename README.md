# LLMwebsite

Chat frontend for [VOIDSEED](https://github.com/otzpt/VOIDSEED) tiny-llm — a
155M-parameter GPT trained from scratch on security documentation, with
retrieval-augmented generation. Public demo for the Stardance Challenge.

Live: **[llmwebsite-pink.vercel.app](https://llmwebsite-pink.vercel.app)**

(`llmwebsite.vercel.app` is discontinued — it was a one-off alias set by
hand, not a real tracked project domain, so it doesn't follow new deploys.
`llmwebsite-pink.vercel.app` is the actual project domain and always points
at the latest production deploy.)

## Layout

```
index.html    the page
style.css     styling
main.js       sends chat messages, renders the replies
backend.py    a local Flask server for dev/testing (see below)
```

Plain HTML/JS/CSS on purpose — no build step, no framework, deploys as-is.

## Two backends, don't mix them up

Both exist and both work — `main.js` only talks to one of them at a time,
set by `BACKEND_URL`.

**Production (what `main.js` uses right now)** — a FastAPI service, deployed
on Hack Club Nest (not this repo, not Vercel — Stardance's rules don't allow
Hugging Face for hosting, so this runs on Nest instead), reachable over HTTPS
via Caddy + Let's Encrypt:

```
BACKEND_URL = https://2a01-4f9-3a-276e--1019.sslip.io/generate

POST /generate
Body:     {"prompt": "..."}
Response: {"answer": "..."}

GET /health  ->  {"status": "ok"}
```

10 requests/minute per IP, `prompt` capped at 2000 chars. CORS restricted to
`llmwebsite.vercel.app` and `llmwebsite-pink.vercel.app` — a request from any
other origin is rejected by the browser, by design.

**`backend.py`** — a local Flask server, for running the model on your own
machine instead of hitting the deployed one. Different contract: `POST /chat`,
body `{"message": "..."}`, response `{"response": "..."}`. To use it, point
`BACKEND_URL` at `http://localhost:5000/chat` **and** change `main.js`'s
request/response field names back to `message`/`response` — the two backends
are not interchangeable by URL alone.

Measured on the Nest VM (2 shared vCPUs, no GPU): ~50s per reply, 100 tokens,
no KV-cache in the model. `main.js` already accounts for this — it shows a
"Thinking..." placeholder while waiting instead of a spinner that implies a
couple of seconds.

## Local dev

```bash
# backend (needs the tinyllm2 checkout at the path backend.py imports from)
pip install flask flask-cors torch tiktoken
python3 backend.py          # localhost:5000

# frontend
python3 -m http.server 8000 # or just open index.html directly
```

## Deployment

Vercel, project `llmwebsite`, auto-deployed and confirmed working via
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) on every push
to `main`. Needs a `VERCEL_TOKEN` repository secret (Vercel -> Account
Settings -> Tokens) — already set. To rotate it:

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
