# EU AI Act compliance — VOIDSEED demo (LLMwebsite / voidseed-api)

Regulation (EU) 2024/1689 ("the AI Act"), as amended by Regulation (EU)
2026/1744. Article 50 has applied since 2 August 2026. This note covers the
public chat demo at `llmwebsite-pink.vercel.app` (repo: `LLMwebsite`) and its
inference backend (repo: `voidseed-api`, deployed by hand via `scp`, not a
git repository).

Written 2026-08-12. Not legal advice — see "Requires human/legal review"
below for the open items.

## What the system is

A retrieval-augmented chat demo over a 155,410,513-parameter GPT trained
from scratch (`tinyllm2`/VOIDSEED). The deployed checkpoint was trained on a
security-documentation corpus (hacktricks, hacktricks-cloud,
PayloadsAllTheThings, SecLists, GTFOBins.github.io, CheatSheetSeries, wstg —
not TinyStories, which was an earlier, separate 24M-parameter smoke-test
model with no public deployment). A visitor types a question, the backend
retrieves relevant passages from an FTS5 index over that corpus, and the
model generates an answer conditioned on the retrieved text.

## Art. 3(1) — is this an "AI system"?

Yes. It is machine-based, generates output (text) from input for an
explicit objective (answering the visitor's question) after training, and
operates with the varying autonomy characteristic of Art. 3(1)'s
definition. Not disputed.

## Roles — Art. 3(3)/(4)

The operator of this deployment is both:
- **Provider (Art. 3(3))** — trained the model and put the demo into
  service under its own name.
- **Deployer (Art. 3(4))** — operates it for end users in the course of
  this activity.

## Why not Art. 5 (prohibited practices)

Art. 5 lists eight prohibited practices. None apply to a Q&A chat demo:

- (a) subliminal/manipulative/deceptive techniques materially distorting
  behaviour — the system answers questions; it does not attempt to
  manipulate visitor behaviour.
- (b) exploiting vulnerabilities of age, disability or social/economic
  situation — not targeted at, or aware of, any such characteristic.
- (c) social scoring leading to detrimental treatment in unrelated
  contexts — no scoring of any kind.
- (d) criminal-risk assessment based solely on profiling or personality
  traits — not a risk-assessment system.
- (e) untargeted scraping of facial images from the internet or CCTV — no
  biometric or facial data involved anywhere in this system.
- (f) emotion inference in workplaces and education — no emotion
  inference; the demo is a public web page, not a workplace/education
  deployment.
- (g) biometric categorisation inferring sensitive characteristics — no
  biometric input of any kind.
- (h) real-time remote biometric identification in public spaces for law
  enforcement — not applicable; text-only, no biometric identification,
  no law-enforcement use.

## Why not Annex III (high-risk)

Annex III lists eight high-risk domains: (1) biometrics, (2) critical
infrastructure, (3) education/vocational training, (4) employment/worker
management, (5) access to essential private and public services
(credit, insurance, emergency services, etc.), (6) law enforcement,
(7) migration/asylum/border control, (8) administration of justice and
democratic processes. This system does not operate in any of them — it is
a standalone public demo answering security-documentation questions, with
no decision-making role in any of the eight domains.

## Why not Annex I

Annex I lists the EU harmonisation legislation whose scope defines
"safety component" high-risk AI (machinery, toys, lifts, medical devices,
etc.). This system is software with no physical safety-component role
under any Annex I instrument.

## Why not GPAI (Art. 51-56)

The deployed model: 155,410,513 parameters, 1,960,108,296 training tokens.

Compute estimate (6ND, the standard training-FLOP approximation):
6 × 155,410,513 × 1,960,108,296 ≈ **1.83 × 10^18 FLOP**.

- The Commission's guidelines use 10^23 FLOP as the presumption criterion
  for "general-purpose AI model" under Art. 51.
- Art. 51(2)'s systemic-risk threshold is 10^25 FLOP.

1.83e18 is roughly five orders of magnitude below the GPAI presumption
threshold and seven below the systemic-risk threshold. **Art. 53 GPAI
obligations do not apply** to this model.

## Art. 50(1) — visible disclosure to natural persons

Implemented:
- `LLMwebsite/index.html:10` — a `<p id="ai-disclosure">` above the chat
  container, visible on page load: "You're talking to an AI system.
  Answers are machine-generated and may be wrong."
- `LLMwebsite/index.html:5` — `<meta name="ai-generated" content="true">`
  in `<head>`.
- `LLMwebsite/style.css` — `#ai-disclosure` rule (muted `#5c6370`, 12px,
  centred, capped at the same 640px as the chat container) plus the
  `body` flex-direction change needed to stack it above `#chat-container`
  without breaking the existing centred layout.

## Art. 50(2) — machine-readable marking of AI-generated output

Implemented on every surface that carries a generated reply:
- `LLMwebsite/main.js` (`addMessage()`) — `data-ai-generated="true"` set
  on bot message `<div>`s only, not user messages.
- `voidseed-api/main.py` — `GenerateResponse.ai_generated: bool = True`
  on the JSON body, and `response.headers["X-AI-Generated"] = "true"` on
  `POST /generate` (the production backend `main.js` actually calls).
- `LLMwebsite/backend.py` — `'ai_generated': True` added to the `POST
  /chat` JSON response, and an `after_request` hook sets
  `X-AI-Generated: true` on every response from this local-dev Flask
  server (its contract differs from the production API: `{"response":
  ...}` vs `{"answer": ...}` — see `README.md`).

## Requires human/legal review

- **Corpus licensing.** The training corpus (hacktricks, hacktricks-cloud,
  PayloadsAllTheThings, SecLists, GTFOBins.github.io, CheatSheetSeries,
  wstg) — each carries its own licence; not verified in this audit —
  requires human/legal review.
- **Art. 2(10).** Art. 2(10) excludes AI used by a natural person in a
  purely personal, non-professional activity from parts of the
  Regulation. Whether this public student-competition demo (Stardance
  Challenge) falls inside or outside that exclusion is an open question —
  not resolved here, requires human/legal review.
- **Art. 50(2) marking deadline.** If this system was first placed on the
  market or put into service before 2 August 2026, the Omnibus shifts the
  Art. 50(2) marking deadline for that placement to 2 December 2026
  rather than 2 August 2026. Whether that applies here (exact
  first-placement date) is not established in this audit — requires
  human/legal review.

## GDPR (Regulation (EU) 2016/679)

Written 2026-08-12, same audit as the AI Act notes above. Not legal advice —
see "Requires human/legal review" below.

### What's collected

No accounts, no prompt/answer storage, no cookies. The chat itself is
stateless: `voidseed-api/main.py`'s `/generate` endpoint takes a prompt,
returns an answer, and keeps nothing about the exchange in application
state or a database.

The only personal data in this system is what the infrastructure layer
collects incidentally: Caddy (the reverse proxy in front of the API,
`voidseed-api/Caddyfile`) writes access logs to stdout, which the
`voidseed-api.service` systemd unit sends to the VM's journal — client IP
address and request timestamp. No prompt or answer text is logged.

### Legal basis

Art. 6(1)(f) — legitimate interest, specifically abuse prevention and
keeping the service available. This isn't hypothetical for this deployment:
`voidseed-api/main.py` already rate-limits per IP (`RATE_LIMIT_PER_MINUTE`)
and documents a real prior OOM incident from unmetered concurrent load on
the VM's 2 CPUs / 1.5GB headroom. Access logs are the record that would let
an abusive IP be identified and blocked if that happens again.

### Retention (Art. 5(1)(e) — gap)

**No fixed retention period is currently configured.** The VM's
`journald.conf` has `MaxRetentionSec` and `SystemMaxUse` both commented
out — there is no time-based expiry. Access logs are rotated only when
journald's disk-space-based defaults kick in, which could mean logs
persist far longer than the abuse-prevention purpose in Art. 6(1)(f)
actually needs.

This is a real Art. 5(1)(e) storage-limitation gap, not a resolved item.
**Recommended fix:** set `MaxRetentionSec=2592000` (30 days) in
`journald.conf` on the VM and restart `systemd-journald`. Not done as part
of this audit — requires a human with access to the VM to apply it.

### Rights (Art. 12-22)

No accounts exist, so there is no way to look up "this person's data" —
the only personal data held is an IP address inside a journald log stream,
and an individual erasure/access request against a bare IP isn't
meaningfully actionable (nothing ties a log line to an identity, and there
is no per-user index to search or delete from). If a visitor asks, the
honest answer is that their IP may be in the access log until it rotates,
with no per-request deletion mechanism.

### Requires human/legal review

- **Exact retention cap.** `MaxRetentionSec=2592000` above is a proposed
  starting point (30 days), not a value this audit is authorized to pick.
  A human should decide the actual cap and apply it in `journald.conf`.
- **Art. 2(10).** GDPR doesn't have an Art. 2(10) personal-activity
  exclusion (that's an AI Act concept — see the AI Act section above for
  the equivalent question under Art. 2(10) AI Act). Whether GDPR's own
  household-activity exemption (Art. 2(2)(c)) could apply to this specific
  student-competition demo is a separate open question, not resolved
  here — requires human/legal review.
