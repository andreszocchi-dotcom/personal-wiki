# test-4: Unsupported: answer is not in the wiki

**Question:** What was Andrés's GPA at Berkeley Haas?

| Field | Value |
|---|---|
| Mode | ask (standalone, no chat history) |
| Execution | local (Ollama at http://localhost:11434) |
| Internet reachable during run | True |
| Model | `gemma4:e4b` · 8.0B · Q4_K_M · digest `c6eb396dbd59` |
| Runtime | Ollama 0.34.3 |
| Run id | `20260928-153640-2ebb59` (full record in `evidence/runs/`) |
| Time | 2026-09-28T15:36:40 |

## Expected (written before running)

INSUFFICIENT EVIDENCE. No source states his GPA. Retrieval is expected to return the Haas standards passage that mentions GPA as an optional resume field; the model must not treat that as his GPA or guess a number.

Expected sources: none

## Retrieval check (automatic)

- Expected sources retrieved: 0/0 []
- Expected phrases found in passages: 0/0 []

## Retrieved passages

**[S1]** `vault/raw/Berkeley Haas Resume Standards.md` — 9. Education section — standard optional fields (lines 109-109) — score 8.972

> GPA, GMAT, awards, activities, applied-innovation coursework (e.g., Haas's Applied Innovation courses). Include selectively — only when they add signal (e.g., a strong GMAT/GPA, a scholarship, a directly relevant elective).

**[S2]** `vault/raw/Source/LinkedIn Profile.md` — Andres Zocchi — LinkedIn Profile (lines 10-20) — score 5.67

> **Headline:** MBA Candidate at UC Berkeley Haas
> **Location:** Berkeley, California, United States
> **Contact:** [phone redacted] (Mobile) · [email redacted] · linkedin.com/in/andreszocchi
> 
> **Top Skills:** Leadership · Intercultural Communication · Microsoft PowerPoint
> 
> **Languages:** Italian (Limited Working) · French (Limited Working) · English (Native or Bilingual) · Catalan (Limited Working) · Spanish (Native or Bilingual)
> 
> **Certifications:** Workday Financials
> 
> **Honors-Awards:** President Award Honors Program · Shebik Scholarship · Gies College of Business Scholarship

**[S3]** `vault/raw/Berkeley Haas Resume Standards.md` — Berkeley Haas Resume Writing Standards (lines 9-9) — score 5.343

> Style guide layer for the Career & Resume system. Consult this before writing/evaluating bullets; don't reproduce from memory when this file is available.

**[S4]** `vault/raw/Master Resume.md` — Master Resume — Andrés Zocchi (lines 10-12) — score 5.342

> Not a resume to submit as-is. This is the curated superset: strongest available phrasing per accomplishment, plus alternate framings for different target audiences. Tailored resumes should select/reweight from here per [[Berkeley Haas Resume Standards]] §2 and §8, using the target-role mapping process (Core Instructions §13-15).
> 
> Contact: [phone redacted] · [email redacted] · linkedin.com/in/andreszocchi

**[S5]** `vault/raw/Career Inventory.md` — Education > University of California, Berkeley — Haas School of Business (lines 17-18) — score 5.224

> - **MBA**, expected May 2027 (started July 2025) — CONFIRMED
> - Activities/credentials vary by resume version: "Pursuing AI for Business Graduate Certificate, Tech Club" (newest, June2026 resume) vs. "Tech Club, Product Management Club" (all other versions) — Berkeley Haas Scholarship, Consortium Fellow appear on all versions. **NEEDS CONFIRMATION**: is the AI for Business Graduate Certificate still active/current, or was "Product Management Club" dropped by mistake in the newest version? Worth reconciling — these read like two different truths, not just trimming.

## Gemma answer (verbatim)

> INSUFFICIENT EVIDENCE: The provided passages do not mention Andrés's GPA at Berkeley Haas.

## Citation check (automatic)

- Cited: none
- Insufficient-evidence response: True
- Problems: none

## Timing

- Wall time 5.25s, first token 4.26s, 21.3 tok/s, prompt 909 tokens, output 21 tokens

## Manual assessment

_Pending: open each cited source and check every material claim._
