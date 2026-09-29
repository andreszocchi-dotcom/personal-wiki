---
title: Career Inventory
owner: Andrés Zocchi
last_updated: 2026-08-24
status: initial ingestion from 11 tailored resumes, 1 LinkedIn export, 1 general Profile.pdf. Not yet interviewed.
---

# Career Inventory — Andrés Zocchi

Primary working source of truth. Facts here are drawn from: `Zocchi_Andres_Resume_June2026.pdf`, `GSAP Returning Class of 2027_Zocchi, Andres_Resume.pdf`, `Andres Zocchi Resume - ServiceNow Inbound PM.pdf`, `- Spring 2026.pdf`, `- Amazon.pdf`, `- Adobe Digital Strategy.pdf`, `- Adobe Strategy.pdf`, `- Adobe.pdf`, `- Apple.pdf`, `- Google.pdf`, `- Salesforce Business Value Services.pdf`, `- Microsoft - PMM.pdf`, `- IBD.pdf`, plain `Andres Zocchi Resume.pdf`, plus LinkedIn (`Profile.pdf` / [[Source/LinkedIn Profile]]). No interview has happened yet — everything below is CONFIRMED only insofar as it's stated consistently across these documents; deeper mechanism/ownership detail is mostly still **NEEDS CONFIRMATION**.

---

## Education

### University of California, Berkeley — Haas School of Business
- **MBA**, expected May 2027 (started July 2025) — CONFIRMED
- Activities/credentials vary by resume version: "Pursuing AI for Business Graduate Certificate, Tech Club" (newest, June2026 resume) vs. "Tech Club, Product Management Club" (all other versions) — Berkeley Haas Scholarship, Consortium Fellow appear on all versions. **NEEDS CONFIRMATION**: is the AI for Business Graduate Certificate still active/current, or was "Product Management Club" dropped by mistake in the newest version? Worth reconciling — these read like two different truths, not just trimming.

### University of Illinois Urbana-Champaign — Gies College of Business
- **BS, Supply Chain Management and Information Systems**, May 2020 — CONFIRMED
- Edmund J. James Scholar Honors College, all 4 years, "for academic and extracurricular excellence" — CONFIRMED
- President Award Honors Program Scholarship — CONFIRMED (also on LinkedIn as "President Award Honors Program")
- Board Member, Association of Latino Professionals for America (ALPFA) — appears on some resume versions' education bullet, and as a full separate LinkedIn entry (Jan-Dec 2018, Webmaster role within the board)
- LinkedIn-only, not on any resume: **Shebik Scholarship**, **Gies College of Business Scholarship** (distinct from Berkeley Haas Scholarship) — **NEEDS CONFIRMATION** whether these are worth adding to the Master Resume Education bullets or are redundant with "Edmund J. James Scholar."

### Other education (LinkedIn only, not on any resume — pre-MBA, likely intentionally trimmed for space)
- Harvard Business School — Summer Venture in Management Program, MBA-track program, 2019
- Università Bocconi — Business Administration and Management, study abroad, 2019
- Waubonsie Valley High School, 2012-2016

---

## Role: ServiceNow — Senior Inbound Product Manager Intern
**Santa Clara, CA · June-September 2026** (current as of today, 2026-08-24 — internship is ~3 months in / possibly just wrapped)

### Context
Building a 0-to-1 agentic AI security and data privacy product for enterprise customers. Deloitte→Haas MBA→ServiceNow PM internship reads as a consulting-to-product-management pivot, and this is the single most important, most recent, and most strategically load-bearing experience for full-time PM recruiting — and the **thinnest** in terms of captured evidence.

### Accomplishments — interviewed 2026-08-24

**Product & architecture (CONFIRMED, Andrés's own account):**
- Built a **0-to-1 agentic workflow**: 2 AI agents underneath it, with 4 tools and 3 tools respectively (7 tools total across the two agents)
- Purpose: gives ServiceNow customers who use **Data Discovery** conversational access to understanding their data discovery jobs/findings (i.e., natural-language interface over an existing ServiceNow data-discovery product surface)
- Target segment: explicitly a **main priority for large healthcare organizations and financial institutions** — i.e., regulated, data-heavy enterprise customers. **NEEDS CONFIRMATION**: exact source of this prioritization claim (customer research finding? internal strategy doc? leadership statement?) — good detail to have ready if asked in an interview.

**Ownership (CONFIRMED):**
- Andrés owned the whole process — wrote the PRD himself, defined scope
- Manager **[manager]** assigned the original problem statement; outbound PM **[outbound PM]** ran the customer-facing interviews; Andrés ran internal discovery/stakeholder interviews
- Stakeholders/team: ServiceNow PMs, engineers, designers — named collaborators **[colleague]** and **[outbound PM]**, **5+ engineers**, **1 UX designer**, "more PMs" involved, plus customer findings sourced through [outbound PM] (outbound PM)

**Judgment / scope-cut story (CONFIRMED — this is the strongest, most differentiated moment in the internship so far):**
- During PRD writing, the MVP began expanding rapidly — heading toward a system that would both analyze data discovery findings *and* recommend actions, i.e., scope creep into a much larger product
- Andrés recognized this and pulled scope back to solve **one well-defined part** of the problem, on the reasoning that the broader mission would ultimately be served by *multiple* agentic workflows working together rather than one workflow trying to do everything — a real systems/platform-thinking judgment call, made and owned by him, not assigned
- This is a genuinely strong "product sense" story: catching your own scope creep, articulating why, and re-scoping around composability. Worth using as an interview story, not just a resume line (per Core Instructions §17).

**Technical execution / AI-native build process (CONFIRMED, added 2026-08-24):**
- Built this AI-natively: used **Claude Code** and established his own **LLM-based wiki** (a structured knowledge system) to help define the PRD, then to write the script that created the agentic workflow
- Connected that IDE-based LLM wiki (in VS Code) directly to the live ServiceNow instance he was building the workflow in
- This is a materially stronger claim than "wrote a PRD and handed it to engineering" — it's hands-on technical building by a PM, using an AI-native development workflow (a self-built knowledge system feeding an AI coding agent, wired directly into the target platform)
- **CONFIRMED (2026-08-24):** "I personally did it, Claude Code wrote the script with my guidance." Andrés directed the implementation; Claude Code wrote the script under his guidance. Accurate resume framing: he personally built/implemented the workflow by directing an AI coding agent — not "wrote every line by hand," but also not "handed a spec to engineers." This is a defensible, specific claim.

**Outcome / current status (CONFIRMED, as of 2026-08-24):**
- The workflow is built; Andrés delivered a **live demo** in which it correctly responded to and resolved representative customer needs
- Currently moving into defining **go-to-market strategy** for the workflow
- **NEEDS CONFIRMATION (Andrés flagged this himself — "will have to ask me again"):** any hard numbers — count of customer/stakeholder interviews, timeline from kickoff to demo, size of the addressable customer segment, any leadership/manager reaction beyond the demo itself, whether there's a next milestone (pilot customer, GA target, expanded scope, return-offer signal)

### Remaining gaps — next interview pass
- Quantify: how many interviews (internal + via [outbound PM]), how long from problem statement to demo, any usage/accuracy metric from the demo itself
- What exactly is "ServiceNow Data Discovery" from a customer's point of view — worth one line of plain-English context for a non-ServiceNow reader (this matters for a resume bullet: today's phrasing assumes the reader already knows what "data discovery jobs" means)
- Any leadership reaction / next-steps signal beyond the demo (this is the detail that would most strengthen the bullet's Impact component)
- Retire the placeholder/anticipatory bullet from `GSAP...Resume.pdf` ("Selected for product management internship supporting AI Security initiatives...") now that real content exists — it undersells what actually happened.

**Potential Resume Angles:** Product Management (primary), AI/ML product, Enterprise Security, Technology Strategy

---

## Role: Deloitte Consulting LLP — Technology Transformation
**San Diego, CA & Chicago, IL · 2020-2025**
Title progression: Analyst (Sept 2020-May 2022) → Consultant (May 2022-May 2025) → Senior Consultant (May-July 2025, 3 months) — dates CONFIRMED via LinkedIn cross-check, consistent with all resume versions.

### Context
Core engagement: a **$340M finance platform** built on **Workday**, consolidating **100+ legacy systems** into a single system, for a client that includes (at least in part) **three government agencies** processing **100,000+ monthly financial transactions**. This is the flagship, most fully-developed accomplishment set across all resume versions — extremely well-documented in *phrasing*, but underlying mechanism detail (which agencies, what Andrés personally decided vs. what the broader 60+ person team decided) is still mostly inferred from resume language, not independently confirmed via interview.

**NEEDS CONFIRMATION**: Is "$340M" the platform/program budget, the contract value, or something else? This number is repeated verbatim across every resume version so it's likely solid, but worth being able to defend precisely what it refers to in an interview.

### Sub-track A: Product Implementation & Execution / Delivery
(Bucket header itself varies by resume: "Product Implementation & Execution," "Product Implementation & Delivery," "Strategy & Value Enablement," "Digital Transformation Execution," "Project Implementation & Execution" — same three underlying accomplishments, reframed per target company/role type.)

- **Product requirements & vision ownership.** Defined product requirements/vision for the $340M Workday finance platform consolidating 100+ legacy systems, improving reporting efficiency and organizational decision-making. Reframed for PM-targeted resumes as "Owned product vision..." (Amazon) / "Led launch of a new Workday Financials platform, shaping product strategy through stakeholder discovery..." (Microsoft PMM). — CONFIRMED core fact (requirements definition happened); **NEEDS CONFIRMATION** on exact personal ownership boundary (did Andrés own requirements for the whole platform, or a workstream within it?).
- **Accounting data conversion strategy.** Defined requirements, designed Excel templates, led workshops for **35+ units**, achieved **99.99% accurate migration** into the new platform. **CONFIRMED (2026-08-24):** Andrés personally designed the core migration approach — the "invented scalable data migration framework" framing (Amazon resume) is accurate and should become the standard phrasing going forward, not the exception. Update: still worth a follow-up interview pass to capture *what specifically* the framework was (what made it "scalable," what alternative/manual approach it replaced) so the bullet can carry more concrete mechanism detail.
- **Backlog prioritization + AI-assisted testing.** Prioritized/managed a backlog of **1,000+ user scenarios**, leveraging AI to expand test coverage, ensuring the product met UX/functionality/performance standards. One version specifies "AI-assisted testing tools to prioritize 1,000+ user stories" (Adobe Digital Strategy) and another "Applied AI-driven scenario generation to test and validate 50+ product features" (Microsoft PMM) — **NEEDS CONFIRMATION**: is "50+ product features" a different, more granular metric than "1,000+ user scenarios," or a looser paraphrase? These should reconcile to one real number set.

### Sub-track B: Cross-Functional Team Leadership
- Partnered with engineers and PMO to drive integration development, translating client needs into Workday specs, ensuring automated flow between 100+ legacy systems and the new platform.
- **Managed and mentored a team of three practitioners/analysts** — delegated tasks, enhanced their Workday technical and presentation skills. CONFIRMED as a real direct-management scope (3 reports) — this is a genuine leadership credential worth interviewing further (what specifically did Andrés do to develop them, any promotions/positive outcomes for them?).
- Facilitated alignment across a **60+ person team** (engineers, PMO, training specialists) — delivered the platform on schedule with smooth client adoption.

### Sub-track C: Strategic Vision & Client Engagement
- Defined/presented data-driven product strategy and trade-off recommendations to **50+ C-suite executives** — aligning platform capabilities with business goals, driving faster decision cycles.
- **Directed remediation of 55+ legacy systems for three government agencies**, ensuring uninterrupted processing of 100,000+ monthly financial transactions. This is the most specific, highest-stakes fact in the whole inventory and is underexplored — which agencies (even at a category level — federal/state/local, defense/civilian), what "directed remediation" concretely meant, what would have broken if it failed.
- Formalized the product roadmap / project schedule by authoring **three essential deliverables** defining scope, expectations, and cross-functional goals.

**Potential Resume Angles:** Product Management (requirements/roadmap/backlog framing), Technology/Strategy Consulting (client-facing, C-suite framing), Program/Project Management (60+ person coordination framing), People Leadership (3-person mentee team)

**Gaps — interview targets:**
- Real names/categories of the "three government agencies" (even generalized) and what specifically was at risk
- Precise boundary of personal ownership vs. team/firm ownership on the $340M platform
- Any concrete business outcome beyond "on schedule" — did reporting speed measurably improve, did decision cycles measurably shorten, were there error/incident-rate improvements post-migration?
- Whether "leveraging AI" for test coverage was a personal initiative Andrés introduced, or a firm-standard tool — this matters a lot for AI/PM-target resumes since it's currently one of the only concrete "used AI to do something" claims in the whole resume

---

## Role: D2International – Fundación Juanfe (Deloitte Pro-Bono Project)
**Latin American non-profit focused on improving health, education, and employability of young mothers.** Dates vary by resume: fuller versions show **2021-2024** with two distinct sub-roles; shorter/newer versions (`Zocchi_Andres_Resume_June2026.pdf`, GSAP resume) show only **2023-2024** and drop the earlier role entirely — this reads as intentional trimming for space, not a factual conflict, since the two-role version is a strict superset.

### Salesforce Product Implementation Lead (2023-2024)
- Led customer discovery to identify **100+ user needs**, guided Salesforce roadmap/developer priorities to build a CRM platform supporting **1,000+ program graduates**.
- Fostered collaboration between the Deloitte member firm and Fundación Juanfe to build a pipeline of pro bono opportunities, enabling Deloitte's Latin America offices to perform Salesforce configuration services.
- Composed the engagement letter setting scope, staffing plan, and timeline for a new 8-month phase of project work.

### Salesforce Training and Change Management Lead (2021-2023)
- Drove customer adoption: created training guides, facilitated two virtual workshops **in Spanish** to train **50+ employees** on the customized Salesforce platform.
- Traveled to **Cartagena, Colombia** to complete three live workshops and build Deloitte's relationship with the client.

This is Andrés's clearest **0-to-1 product/CRM ownership** story combined with **bilingual delivery** — genuinely differentiated material (pro bono + Spanish-language delivery + travel + built something from customer discovery through adoption). It is currently boxed into "Additional" project space at the bottom of the resume; worth discussing whether it deserves more prominence for PM-track applications specifically, since "customer discovery → roadmap → build → drive adoption" is a more complete product lifecycle story than the Deloitte Workday engagement (which is bigger in scale but Andrés's personal ownership boundary is fuzzier within a 60+ person team).

**Potential Resume Angles:** Product Management (full lifecycle: discovery→roadmap→adoption), Social Impact/DEI, International/Bilingual capability, Business Development (building the pro bono pipeline itself)

**Gaps:** What was the actual customer discovery process (how many interviews, with whom)? What did Andrés personally decide on the roadmap vs. what developers decided? Concrete post-launch adoption numbers beyond "1,000+ program graduates supported" (usage rate? graduate outcomes attributable to the CRM?).

---

## Pre-MBA / undergrad experience — CONFIRMED via LinkedIn, not on any current resume
Likely correctly trimmed for an MBA-stage resume (too early-career, no room), but flagged here in case a specific narrative (leadership, multilingual, DEI, legal/policy interest) ever needs early evidence:

- **Illinois Business Consulting** — Consultant (Jan-Aug 2018) → Senior Consultant (Sept 2018-Jan 2019), Urbana-Champaign
- **Deloitte Consulting — Strategy & Operations Summer Scholar** (June-Aug 2019, Washington DC Metro) — a Deloitte pipeline/diversity program, distinct from the 2020-2025 Deloitte employment
- **Deloitte Technology Innovation Challenge** (July-Aug 2018, Las Vegas) — selected as 1 of 15 national participants at the ALPFA convention
- **ALPFA Board Member / Webmaster** (Jan-Dec 2018, Champaign IL)
- **Gies College of Business — Stewardship and Advancement Assistant** (May 2018-May 2020)
- **Immigration Law Office of Moises Barraza — Legal Intern and Translator** (May 2017-Jan 2018, Aurora IL)
- **Godoy Law Office — Law Clerk** (May-Aug 2017, Oak Brook IL)

---

## Skills / Languages / Additional — cross-resume constants
- **Certification**: "Workday Record to Report Certification" (resumes) vs. LinkedIn "Workday Financials" — **NEEDS CONFIRMATION**: same credential, two names, or two different things? Get the exact, official certification title before it goes on a resume a background check might verify.
- **Tools**: Internal GenAI Tool (Deloitte-proprietary, unnamed), Jira, Smartsheet
- **Research databases**: **PitchBook** and **Capital IQ** — CONFIRMED 2026-09-09 (access via Berkeley Haas). Relevant to any role listing a company-database subscription as a prerequisite (e.g. GTM/market-research projects, VC/PE fellowships); previously unrecorded, and was the one hard requirement flagged as unknown on the Simple AI GTM research application.
- **Languages**: Native fluency Spanish. Resume "Additional" line claims conversational French, Italian, Catalan, Basque, Portuguese — LinkedIn only self-rates Italian/French/Catalan as "Limited Working" and does not list Basque or Portuguese at all. **Flag**: this is a real discrepancy (not just trimming) between two self-authored sources — worth reconciling to one honest, defensible line, since language claims are easy to test in an interview.
- **Personal/Additional**: "Hiked in the Smokies, Andes, and Rockies | FC Barcelona and River Plate fan | Former Wedding Officiant" — constant across every version. Per Haas standards §10, "Former Wedding Officiant" is a strong specific hook; "FC Barcelona and River Plate fan" is closer to generic filler and may be worth swapping for a more specific story if one exists (which match, which trip, any story behind officiating the wedding).

---

## Target roles / application landscape (inferred, not confirmed)
Eleven tailored resume variants exist, implying an active, broad search:
- **Big Tech PM/PMM**: Amazon, Google, Apple, Microsoft (PMM specifically), Salesforce (Business Value Services), Adobe (two variants: "Digital Strategy" and general "Strategy")
- **Consulting-adjacent/strategy**: IBD (note: title suggests Investment Banking Division — a notably different track from PM; **needs confirmation** whether "IBD" here means investment banking recruiting or something else, since it's a real outlier next to seven PM/tech-strategy variants)
- **Current employer track**: ServiceNow (already interning there — likely pursuing full-time conversion)

**CONFIRMED (2026-08-24):** Andrés is running a broad PM/tech search — ServiceNow is one option among several, not a settled full-time-conversion priority. Big-tech PM variants (Amazon, Google, Apple, Adobe x2, Microsoft PMM, Salesforce BVS) should be treated as equally live. Still open: what "IBD" targets specifically (investment banking, unconfirmed) and whether it's a serious alternate track or a hedge.

**Added 2026-08-30: Healthcare VC / early-stage investing** is now an active, applied-to track — Inflect Capital's Fall 2026 MBA Venture Fellow role (healthcare-focused pre-seed/seed/Series A fund). Confirmed with Andrés: no VC/finance-specific Haas coursework, clubs, or personal investing experience exists yet. The tailored resume for this leans entirely on reframing existing Deloitte (analysis/evaluation), ServiceNow (healthcare-segment prioritization), and Fundación Juanfe (direct healthcare-sector, full discovery→roadmap→adoption cycle) material — see `Andres Zocchi Resume - Draft Healthcare VC (Inflect Capital).md`. This is a meaningfully different track from the Big Tech PM search and from "IBD" (investment banking) — worth clarifying in a future conversation whether VC is a serious parallel track or a one-off application.
