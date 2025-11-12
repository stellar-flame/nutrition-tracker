# Guidelines to Assisting with Code Contributions

I’m using this repo to learn **React** and **TypeScript** while building a cloud-deployed app. Please follow these guidelines so I can write the code **step by step**.

---

## Core Principles

1. **Small, incremental steps only**  
   - Never dump a full feature at once.  
   - Provide the minimum set of files/snippets needed for the *current* step.

2. **Plan first, then code**  
   - Briefly outline what we’re adding (components, hooks, functions, where they live).  
   - Then provide small code snippets I can paste.

3. **Show where code fits**  
   - For every snippet, include the **file path** and any **integration lines** (e.g., how to import and use it from `index.tsx`).

4. **Explain as we go**  
   - After each snippet, give a short explanation of what it does and why.  
   - Expand acronyms on first use (for example, TanStack Query (React Query), Search Engine Optimization (SEO)).

5. **Respect scope**  
   - Don’t add unrelated libraries, styling, or backend code unless I explicitly ask.  
   - Avoid scaffolding entire features; stick to the specific request.

---

## Default Assumptions

- Tooling: **Vite + React + TypeScript**.  
- Aliases: `@` maps to `src/` for imports.  
- Data fetching: **TanStack Query (React Query)** if server state is needed.  
- HTTP: **Axios** or native `fetch` (only if I ask for network calls).  
- Environment variables exposed with `VITE_*` (no secrets in client code).

---

## Response Format (Use This Order)

1. **Feature Summary (1–2 sentences)**  
   - Example: “Landing screen shows today’s nutrition totals and a list of today’s meals.”

2. **File Tree (only files added/changed)**  
   - Keep it short and relevant to this step.

3. **Snippets (one block per file)**  
   - Start each block with a comment of the **absolute path** from `src/`.  
   - Code must compile (include imports and exported types).  
   - Example header: `// src/app/components/NutritionSummary.tsx`

4. **Integration Steps (short checklist)**  
   - Show exactly where to import, which provider to wrap, and what line to add.

5. **Next Tiny Step**  
   - Suggest the *one* next thing I should add (e.g., “Wire the hook into `index.tsx`” or “Add loading state test”).

---

## Style Rules

- **Keep snippets small.** One component or one hook per snippet.  
- **Type everything.** Include TypeScript types for props/returns.  
- **A11y basics.** Use semantic elements and simple `aria-*` roles where obvious.  
- **No placeholders.** Avoid “// … your code here.” Provide minimal, runnable code.  
- **No magic.** If a snippet relies on an import, show the import.  
- **Don’t assume backend.** If an API is required, define a minimal *interface* or mock; only hit a real endpoint if I asked.
