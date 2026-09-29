# test-3: Connects two sources

**Question:** What languages does Andrés speak, and do his resume and LinkedIn agree?

| Field | Value |
|---|---|
| Mode | ask (standalone, no chat history) |
| Execution | local (Ollama at http://localhost:11434) |
| Internet reachable during run | True |
| Model | `gemma4:e4b` · 8.0B · Q4_K_M · digest `c6eb396dbd59` |
| Runtime | Ollama 0.34.3 |
| Run id | `20260928-153635-00b7ab` (full record in `evidence/runs/`) |
| Time | 2026-09-28T15:36:35 |

## Expected (written before running)

Spanish native; LinkedIn lists Italian, French and Catalan as Limited Working (plus English native), while the resume line also claims Basque and Portuguese, which LinkedIn does not list. So they do not fully agree. Cites Career Inventory.md (Skills / Languages) and LinkedIn Profile.md.

Expected sources: `raw/Career Inventory.md`, `raw/Source/LinkedIn Profile.md`

## Retrieval check (automatic)

- Expected sources retrieved: 2/2 ['raw/Career Inventory.md', 'raw/Source/LinkedIn Profile.md']
- Expected phrases found in passages: 2/2 ['Limited Working', 'Basque']

## Retrieved passages

**[S1]** `vault/raw/Career Inventory.md` — Skills / Languages / Additional — cross-resume constants (lines 148-152) — score 6.946

> - **Certification**: "Workday Record to Report Certification" (resumes) vs. LinkedIn "Workday Financials" — **NEEDS CONFIRMATION**: same credential, two names, or two different things? Get the exact, official certification title before it goes on a resume a background check might verify. - **Tools**: Internal GenAI Tool (Deloitte-proprietary, unnamed), Jira, Smartsheet
> - **Research databases**: **PitchBook** and **Capital IQ** — CONFIRMED 2026-09-09 (access via Berkeley Haas). Relevant to any role listing a company-database subscription as a prerequisite (e.g. GTM/market-research projects, VC/PE fellowships); previously unrecorded, and was the one hard requirement flagged as unknown on the Simple AI GTM research application. - **Languages**: Native fluency Spanish.

**[S2]** `vault/raw/Source/LinkedIn Profile.md` — Andres Zocchi — LinkedIn Profile (lines 10-20) — score 6.85

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

**[S3]** `vault/raw/Career Inventory.md` — Career Inventory — Andrés Zocchi (lines 10-10) — score 5.578

> Primary working source of truth. Facts here are drawn from: `Zocchi_Andres_Resume_June2026.pdf`, `GSAP Returning Class of 2027_Zocchi, Andres_Resume.pdf`, `Andres Zocchi Resume - ServiceNow Inbound PM.pdf`, `- Spring 2026.pdf`, `- Amazon.pdf`, `- Adobe Digital Strategy.pdf`, `- Adobe Strategy.pdf`, `- Adobe.pdf`, `- Apple.pdf`, `- Google.pdf`, `- Salesforce Business Value Services.pdf`, `- Microsoft - PMM.pdf`, `- IBD.pdf`, plain `Andres Zocchi Resume.pdf`, plus LinkedIn (`Profile.pdf` / [[Source/LinkedIn Profile]]). No interview has happened yet — everything below is CONFIRMED only insofar as it's stated consistently across these documents; deeper mechanism/ownership detail is mostly still **NEEDS CONFIRMATION**.

**[S4]** `vault/raw/Career Inventory.md` — Skills / Languages / Additional — cross-resume constants (lines 148-152) — score 5.373

> Resume "Additional" line claims conversational French, Italian, Catalan, Basque, Portuguese — LinkedIn only self-rates Italian/French/Catalan as "Limited Working" and does not list Basque or Portuguese at all. **Flag**: this is a real discrepancy (not just trimming) between two self-authored sources — worth reconciling to one honest, defensible line, since language claims are easy to test in an interview. - **Personal/Additional**: "Hiked in the Smokies, Andes, and Rockies | FC Barcelona and River Plate fan | Former Wedding Officiant" — constant across every version. Per Haas standards §10, "Former Wedding Officiant" is a strong specific hook; "FC Barcelona and River Plate fan" is closer to generic filler and may be worth swapping for a more specific story if one exists (which match, which trip, any story behind officiating the wedding).

**[S5]** `vault/raw/Master Resume.md` — Master Resume — Andrés Zocchi (lines 10-12) — score 4.881

> Not a resume to submit as-is. This is the curated superset: strongest available phrasing per accomplishment, plus alternate framings for different target audiences. Tailored resumes should select/reweight from here per [[Berkeley Haas Resume Standards]] §2 and §8, using the target-role mapping process (Core Instructions §13-15).
> 
> Contact: [phone redacted] · [email redacted] · linkedin.com/in/andreszocchi

## Gemma answer (verbatim)

> Andrés speaks Spanish, which he lists as native or bilingual on LinkedIn and has native fluency for in one source [S1][S2]. His resume claims conversational French, Italian, Catalan, Basque, and Portuguese, while LinkedIn lists Italian, French, and Catalan as "Limited Working" and does not mention Basque or Portuguese [S2][S4].
> 
> INSUFFICIENT EVIDENCE: The passages do not provide a definitive statement on which language list is the correct one.

## Citation check (automatic)

- Cited: S1 → `raw/Career Inventory.md | Skills / Languages / Additional — cross-resume constants (lines 148-152)`, S2 → `raw/Source/LinkedIn Profile.md | Andres Zocchi — LinkedIn Profile (lines 10-20)`, S4 → `raw/Career Inventory.md | Skills / Languages / Additional — cross-resume constants (lines 148-152)`
- Insufficient-evidence response: True
- Problems: none

## Timing

- Wall time 9.16s, first token 4.85s, 21.5 tok/s, prompt 1253 tokens, output 97 tokens

## Manual assessment

_Pending: open each cited source and check every material claim._
