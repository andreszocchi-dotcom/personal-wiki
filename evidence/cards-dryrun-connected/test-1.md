# test-1: Direct question, one source

**Question:** What are the four parts of a strong resume bullet in the Haas standards?

| Field | Value |
|---|---|
| Mode | ask (standalone, no chat history) |
| Execution | local (Ollama at http://localhost:11434) |
| Internet reachable during run | True |
| Model | `gemma4:e4b` · 8.0B · Q4_K_M · digest `c6eb396dbd59` |
| Runtime | Ollama 0.34.3 |
| Run id | `20260928-153612-adde2d` (full record in `evidence/runs/`) |
| Time | 2026-09-28T15:36:19 |

## Expected (written before running)

Names WHAT, HOW, IMPACT and WHY (the work object, the method, the result, the context), ideally noting that three out of four is enough. Cites Berkeley Haas Resume Standards.md section 1 'Bullet anatomy'.

Expected sources: `raw/Berkeley Haas Resume Standards.md`

## Retrieval check (automatic)

- Expected sources retrieved: 1/1 ['raw/Berkeley Haas Resume Standards.md']
- Expected phrases found in passages: 2/2 ['WHAT', 'Three out of four is great']

## Retrieved passages

**[S1]** `vault/raw/Berkeley Haas Resume Standards.md` — Berkeley Haas Resume Writing Standards (lines 9-9) — score 8.714

> Style guide layer for the Career & Resume system. Consult this before writing/evaluating bullets; don't reproduce from memory when this file is available.

**[S2]** `vault/raw/Berkeley Haas Resume Standards.md` — 9. Education section — standard optional fields (lines 109-109) — score 8.512

> GPA, GMAT, awards, activities, applied-innovation coursework (e.g., Haas's Applied Innovation courses). Include selectively — only when they add signal (e.g., a strong GMAT/GPA, a scholarship, a directly relevant elective).

**[S3]** `vault/raw/Berkeley Haas Resume Standards.md` — 1. Bullet anatomy: WHAT / HOW / IMPACT / WHY (lines 13-24) — score 8.078

> - **WHAT** — the thing you did / the work object you made
> - **HOW** — the capability or method used to make it
> - **IMPACT** — the result/outcome
> - **WHY** — the context: why did the WHAT matter, what problem was being solved
> 
> **Three out of four is great.** Not every bullet needs all four; forcing all four every time produces bloated, run-on bullets.
> 
> Progression example (retail financial modeling):
> 1. WHAT only: "Developed financial models and scenarios for opening retail stores."
> 2. WHAT+HOW: "...by analyzing local demographics and transportation patterns."
> 3. WHAT+HOW+WHY: "...for the company's first foray into retail."
> 4. WHAT+HOW+IMPACT: "Adjusted financial models...resulting in +25% sales/sqft than projected." (this is the strongest — leads with an action verb, ends with quantified impact)

**[S4]** `vault/raw/Career Inventory.md` — Skills / Languages / Additional — cross-resume constants (lines 148-152) — score 6.447

> Resume "Additional" line claims conversational French, Italian, Catalan, Basque, Portuguese — LinkedIn only self-rates Italian/French/Catalan as "Limited Working" and does not list Basque or Portuguese at all. **Flag**: this is a real discrepancy (not just trimming) between two self-authored sources — worth reconciling to one honest, defensible line, since language claims are easy to test in an interview. - **Personal/Additional**: "Hiked in the Smokies, Andes, and Rockies | FC Barcelona and River Plate fan | Former Wedding Officiant" — constant across every version. Per Haas standards §10, "Former Wedding Officiant" is a strong specific hook; "FC Barcelona and River Plate fan" is closer to generic filler and may be worth swapping for a more specific story if one exists (which match, which trip, any story behind officiating the wedding).

**[S5]** `vault/raw/Master Resume.md` — ADDITIONAL (lines 91-93) — score 6.416

> - Workday Record to Report Certification *(reconcile exact title against LinkedIn's "Workday Financials" before next use)*, Internal GenAI Tool, Jira, Smartsheet
> - Native fluency in Spanish; working proficiency in French, Italian, and Catalan; basic conversational Basque and Portuguese *(reconciled 2026-08-24 — confirmed with Andrés that Basque/Portuguese are real but limited/conversation-starter level, distinct from the stronger three. Standard phrasing going forward.)*
> - Hiked in the Smokies, Andes, and Rockies | FC Barcelona and River Plate fan | Former Wedding Officiant *("Former Wedding Officiant" is a strong hook per Haas standards §10; "FC Barcelona and River Plate fan" is closer to generic — worth a more specific replacement if a real story exists)*

## Gemma answer (verbatim)

> The four parts of a bullet point are WHAT, HOW, IMPACT, and WHY [S3]. WHAT refers to the thing done or the work object created [S3]. HOW is the capability or method used to create it [S3]. IMPACT is the result or outcome [S3]. WHY is the context, explaining why the WHAT mattered or what problem was solved [S3].

## Citation check (automatic)

- Cited: S3 → `raw/Berkeley Haas Resume Standards.md | 1. Bullet anatomy: WHAT / HOW / IMPACT / WHY (lines 13-24)`
- Insufficient-evidence response: False
- Problems: none

## Timing

- Wall time 8.32s, first token 4.75s, 22.4 tok/s, prompt 1118 tokens, output 79 tokens

## Manual assessment

_Pending: open each cited source and check every material claim._
