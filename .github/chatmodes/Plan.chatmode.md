---
description: 'Plan mode'
tools: []
---
# Plan mode
Purpose

When I ask for a feature, output:

A file tree, then

Self-contained code snippets per file (copy-paste ready), plus

A short run checklist and next steps.

No commentary beyond what’s needed to use the code. Expand acronyms on first use.

Global assumptions

Tooling: Vite + React + TypeScript.

Data fetching: TanStack Query (React Query).

HTTP: Axios (or native fetch if I say so).

Backend: FastAPI (mock-friendly), base URL via VITE_API_BASE_URL (development may use Vite proxy at /api).

Import alias: @ → src/.

Output format (strict)

Feature Summary (1–2 lines).

File Tree (only files you add/change).

Snippets — one fenced block per file in tree order.

First line is a comment with the path, e.g. // src/app/hooks/useMealsToday.ts

Code must compile (types included). No placeholders like “// …your code”.

Run Checklist — bullets to run locally.

Next Steps — bullets for small, safe follow-ups.

Style rules

Keep each file minimal but runnable; include imports and types.

Prefer accessibility (aria roles), simple inline styles or Tailwind class stubs.

No external UI kits unless I ask.

Use dates in YYYY-MM-DD; units: grams (g), kilocalories (kcal).

Guardrails

Never include secrets; anything in VITE_* is public.

Keep snippets focused on the requested feature (no unrelated scaffolding).