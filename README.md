# Career Wiki: a personal wiki CLI with local Gemma + RAG

A command-line assistant over my own career notes, running a local open-weight Gemma model through my own harness. It has three modes that behave differently on purpose:

| Mode | What it does | Model? |
|---|---|---|
| `wiki search` | Returns original passages from `vault/raw/` with file, section and line numbers. No generated answer. | No |
| `wiki ask` | Standalone, neutral factual answer built only from retrieved passages, with `[S#]` citations or `INSUFFICIENT EVIDENCE`. Never sees chat history or the persona. | Yes |
| `wiki chat` | "Margin", a personal assistant with a voice and conversation memory. Searches the notes only when a message needs them. | Yes |

Plus `wiki ingest` (sources → Gemma → linked Obsidian notes + index), `wiki eval` (fixed test questions → evidence cards), `wiki status` and `wiki --help`.

Everything runs on my laptop with the internet disconnected: model, retrieval, ingestion and all tests. There is no online mode.

**Jump to:** [Setup](#setup-and-commands) · [Device & model](#device-model-and-measurements) · [Architecture](#architecture) · [Design choices](#design-choices) · [Evidence](#evidence) · [Reflection](#reflection-failures-and-limitations)

---

## Purpose and sources

The wiki is for job-search work during my MBA: tailoring resumes, preparing interview stories, and keeping track of what is confirmed versus still open. It should answer questions like "what did I actually do at Deloitte?", "what do the Haas standards say about bullets?", or "where do my resume and LinkedIn disagree?"

**Sources** (`vault/raw/`, preserved unchanged after import; see [Source Catalog](vault/Source%20Catalog.md)):

| File | Source id | What it is |
|---|---|---|
| [`Master Resume.md`](vault/raw/Master%20Resume.md) | `master-resume` | Curated superset of every resume bullet, with review notes |
| [`Career Inventory.md`](vault/raw/Career%20Inventory.md) | `career-inventory` | Role-by-role inventory with CONFIRMED / NEEDS CONFIRMATION flags |
| [`Berkeley Haas Resume Standards.md`](vault/raw/Berkeley%20Haas%20Resume%20Standards.md) | `berkeley-haas-resume-standards` | My notes from Haas resume workshops |
| [`Source/LinkedIn Profile.md`](vault/raw/Source/LinkedIn%20Profile.md) | `linkedin-profile` | Transcription of my LinkedIn PDF export |

**Privacy.** These are copies of my private notes. [`scripts/redact_sources.py`](scripts/redact_sources.py) imported them once, replacing my phone number, email addresses and three coworkers' first names; all 10 replacements are listed in [`evidence/redactions.md`](evidence/redactions.md). The redacted copy is the original for this project: after import, nothing edits `vault/raw/`.

**How originals become pages.** `wiki ingest` sends each source's text plus [`prompts/ingest-instructions.md`](prompts/ingest-instructions.md) to Gemma and asks for structured topics. The harness writes one note per topic under `vault/wiki/<Topic folder>/`, and each fact carries a link to the exact heading in the original, e.g. `[[raw/Master Resume.md#ADDITIONAL|Master Resume › ADDITIONAL]]`. I then reviewed every note against the originals (see [Wiki review](#wiki-review-and-cleanup)).

## Setup and commands

**Requirements:** Windows 11 (or macOS or Linux), Python 3.10+ (standard library only, no pip packages), [Ollama](https://ollama.com/download) 0.34+.

```powershell
# 1. While online: install Ollama, then download the model (9.6 GB on disk)
ollama pull gemma4:e4b

# 2. Intel Arc / other integrated GPUs only: let Ollama use the GPU (Vulkan).
#    Without this, Ollama runs on CPU (slower, see measurements). Restart the Ollama app afterwards.
setx OLLAMA_VULKAN 1
setx OLLAMA_IGPU_ENABLE 1

# 3. Get the code
git clone <this repo> personal-wiki
cd personal-wiki

# 4. Confirm everything is local before going offline
python wiki.py status
```

On Windows, `wiki.cmd` lets you type `wiki ...` instead of `python wiki.py ...` from the repo folder.

| Command | What it does |
|---|---|
| `python wiki.py --help` | Commands, configuration variables, required inputs |
| `python wiki.py ingest ./vault/raw` | Ingest all sources; skips unchanged files (use `--force` to regenerate) |
| `python wiki.py ingest "path\to\notes.md"` | Copy a new file into `vault/raw/` unchanged, then ingest it |
| `python wiki.py search "Workday data migration"` | Original passages + paths; works with Ollama stopped |
| `python wiki.py ask "How accurate was the finance data move into Workday?" --mode local` | Cited standalone answer (`--show-passages` to print passage text) |
| `python wiki.py chat` | Assistant. In-chat: `/help /notes /nonotes /sources /save /reset /exit` |
| `python wiki.py eval tests/questions.json` | Run the 4 ask tests, write `evidence/cards/test-N.md` |
| `python wiki.py status` | Model, quantization, runtime version, loaded memory, index size, connectivity |
| `python scripts/check_links.py` | Verify every `[[link]]` and heading anchor in the vault |
| `python scripts/mode_checks.py` | Chat/search/ask boundary checks → `evidence/checks/mode-checks.md` |

Configuration uses environment variables: `WIKI_MODEL` (default `gemma4:e4b`), `OLLAMA_HOST` (default `http://localhost:11434`), `WIKI_NUM_CTX` (8192), `WIKI_TOP_K` (5), `WIKI_CHUNK_CHARS` (900).

**Errors are handled, not dumped as stack traces:** no index yet → "Run: wiki ingest ./vault/raw"; Ollama stopped → "Can't reach Ollama at … Start it with `ollama serve`"; model missing → "Run: ollama pull gemma4:e4b"; bad path → "No such file or folder".

**Obsidian:** open the `vault/` folder itself as the vault (not the repo root). The graph view comes pre-configured with filter `path:wiki/`, attachments hidden, and one color per topic folder ([`vault/.obsidian/graph.json`](vault/.obsidian/graph.json)).

## Device, model and measurements

| | |
|---|---|
| OS | Windows 11 Home, build 26200 |
| CPU | Intel Core Ultra 9 288V (Lunar Lake, 8 cores / 8 threads) |
| RAM | 32 GB LPDDR5X (31.6 GB usable), shared with the GPU |
| GPU | Intel Arc 140V integrated (driver 32.0.101.8860). **No dedicated VRAM**: it borrows up to ~16 GB of system RAM. |
| Free memory before loading the model | 15.7 GB (with normal apps open) |
| Free disk | ~590 GB |
| Runtime | Ollama 0.34.3 (llama.cpp `llama-server`), Vulkan backend on the Arc GPU |
| Model | **`gemma4:e4b`**: Gemma 4 E4B instruction-tuned, 8.0B total parameters (~4B effective), **Q4_K_M** quantization, Ollama digest `c6eb396dbd59`, 9.6 GB download. Official source: [ollama.com/library/gemma4](https://ollama.com/library/gemma4); model card: [ai.google.dev/gemma](https://ai.google.dev/gemma/docs). |
| Settings | context 8192 tokens; `think: false`; temperature 0.1 for ask/ingest, 0.7 for chat |
| Python | 3.12.10, standard library only |

**Why E4B.** With 32 GB of shared memory, E4B fits with plenty of room left for the OS and apps. E2B would also fit (it was already on this machine), and 26B A4B MoE (~14.4 GB at Q4_0 for the weights alone) might fit, but would leave little headroom on a laptop that shares memory with its GPU. I picked E4B over E2B because the harness depends on two instruction-following behaviors a smaller model is more likely to get wrong: valid structured JSON during ingestion, and a strict "cite `[S#]` or say INSUFFICIENT EVIDENCE" format in ask mode. E4B handled both in every run. I did not run a controlled E2B comparison, so "E2B would be worse here" is an expectation, not a measured result.

**Measured memory and speed** (warm = model already loaded):

| Measurement | Result |
|---|---|
| Model memory reported by Ollama (`ollama ps`) | 3.3 to 3.4 GB, "100% GPU" |
| **System RAM actually consumed when the model loads** | **~9.7 GB** (free RAM 15.7 → 6.0 GB). The Arc GPU's "GPU memory" is system RAM, and the Ollama `gemma4` package includes vision and audio encoders the harness never uses. |
| CPU-only comparison (Ollama default without Vulkan) | 9.6 GB loaded, 13.6 tok/s, versus 22 to 24 tok/s on the Arc GPU |
| `search` | 0.4 s end to end (no model) |
| `ask`, cold (includes loading the model) | 46 s |
| `ask`, warm | 7 to 9 s model time (~1,300 prompt tokens, first token 4.7 s, ~22 tok/s); 14 s including CLI startup and logging |
| Chat turn (router call + reply) | 10 to 20 s |
| `ingest`, all 4 sources (7 extraction calls + 4 link calls, ~53k chars) | 21 min 15 s |
| `ingest` of one source (LinkedIn, 3.2k chars) | 2 min 15 s to 2 min 26 s |

Ingestion is slow because each call asks Gemma for long structured JSON output (roughly 1,000+ tokens at ~20 tok/s) after reading up to 12,000 characters. That's acceptable for a job that runs only when a source changes. Question answering stays around 10 s.

## Architecture

```
            ┌──────────── CLI: wiki.py (argparse; prints, streams, formats) ───────────┐
 user ──▶   │ ingest │ search │ ask │ chat │ eval │ status                           │
            └────┬───────┬───────┬──────┬───────────────────────────────────────────────┘
                 │       │       │      │           HARNESS (harness/)
                 │       │       │      ├─ modes.ChatSession: persona.md + last 10 messages,
                 │       │       │      │    router.md decides per turn whether to retrieve
                 │       │       ├──────┤  modes.ask: wiki-instructions.md + passages, no history
                 │       │       │      │  modes.check_citations: [S#] must match retrieved passages
                 │       ▼       ▼      ▼  evidence.log_run: every turn → evidence/runs/*.jsonl
                 │   RETRIEVAL TOOL: retrieval.py (BM25 over data/chunks.jsonl)
                 ▼                              │
   ingest.py: sources.py chunks + reads vault/raw │     MODEL: llm.py → local Ollama
   → Gemma (JSON topics) → vault/wiki notes,     └───▶ http://localhost:11434/api/chat
     index.md, Source Catalog.md, data/                  gemma4:e4b
```

- **Model** ([`harness/llm.py`](harness/llm.py)): local Gemma behind Ollama's HTTP API. It sees only the messages the harness assembles; it doesn't read files, remember sessions or call tools itself. This is the only module that talks to the model.
- **Retrieval tool** ([`harness/retrieval.py`](harness/retrieval.py), [`harness/sources.py`](harness/sources.py)): finds evidence and nothing else. Originals are split into passages that keep path, heading and line range. BM25 keyword scoring runs in pure Python, with no model and no embeddings.
- **RAG workflow** ([`modes.ask`](harness/modes.py)): retrieve → put passages and research rules into the prompt → Gemma answers from them → citations checked. The model is not trained on the notes; they are supplied at answer time.
- **Harness** ([`harness/`](harness/)): mode selection, instruction files, conversation context, the chat retrieval decision, prompt assembly, model calls, citation checks, error handling and saved outputs.
- **CLI** ([`wiki.py`](wiki.py)): parses commands and displays results. There is no business logic in it beyond formatting.

### One question traced through the code

`python wiki.py ask "How accurate was the finance data move into Workday?"`

1. `wiki.py main()` parses `ask` → `cmd_ask()`. It checks that `data/chunks.jsonl` exists, and `llm.check_ready()` asks Ollama `/api/tags` whether `gemma4:e4b` is pulled (or exits with a fix-it message).
2. `modes.ask(question)` calls `retrieval.search(question)`: tokenizes (lowercase, drop stopwords, light suffix stemming), scores all 76 passages with BM25, and returns the top 5 with scores and matched terms. Here the Master Resume Deloitte passage wins on *accurate, finance, data, workday* even though it says "migration" rather than "move".
3. If nothing matches, it returns `INSUFFICIENT EVIDENCE` without calling the model. Otherwise it builds two messages: **system** = [`prompts/wiki-instructions.md`](prompts/wiki-instructions.md) (use only passages, cite every factual sentence, refuse if unsupported); **user** = passages labeled `[S1] source: raw/Master Resume.md | EXPERIENCE > Deloitte … (lines 52-59)` + the question. No persona, no chat history.
4. `llm.chat()` POSTs to `localhost:11434/api/chat` (temperature 0.1, 8k context, streaming) and echoes tokens as they arrive.
5. `check_citations()` extracts `[S#]` labels: any label that doesn't refer to a retrieved passage is flagged, and an answer that makes claims without any citation is flagged.
6. `evidence.log_run()` appends the question, passages, answer, citation check, timings, model identity and an internet-reachability probe to `evidence/runs/<date>.jsonl`.
7. The CLI prints the answer, then `S1 → vault/raw/Master Resume.md | … (lines 52-59)` so the claim can be checked in Obsidian.

### How chat differs

- **Instructions:** [`prompts/persona.md`](prompts/persona.md) gives Margin a voice, an accurate list of what it can and cannot do, and the rules: cite notes, label suggestions, never invent personal facts, and treat chat claims as conversation, not sources.
- **Context:** the last 10 messages (5 exchanges) are sent back each turn.
- **Retrieval only when needed:** before replying, a small structured call with [`prompts/router.md`](prompts/router.md) returns `{retrieve, query, reason}`. Capability questions, small talk and "make that shorter" don't retrieve; factual questions and plans about specific things in the notes do. The CLI prints the decision (`[no notes search — asks what the assistant can do]`). The user can override with `/notes` or `/nonotes`.
- **Retrieved passages are attached to one turn and never stored in history.** A follow-up that doesn't search again reuses the previous turn's passages for one turn, so "make that shorter" can keep citations that still resolve.
- **Chat history never reaches ask.** `modes.ask()` has no history parameter, so a claim made in chat cannot become evidence (tested below).
- `/save` writes the last reply to `outputs/drafts/`, separate from `vault/raw/`, so generated drafts never mix with evidence.

## Design choices

- **Passage size:** paragraphs are packed into passages of about 900 characters (~200 tokens), never crossing a heading, so each passage's section label is accurate. Oversized paragraphs are split on sentences. That gives 76 passages across the 4 sources. YAML property blocks are excluded from the index (they repeat title words and outranked real content; see test 1 below), but Gemma still sees them during ingestion.
- **What reaches Gemma:** *ask*: research rules plus 5 passages plus the question, about 1,300 prompt tokens. *Chat*: persona plus up to 10 messages plus 5 passages when retrieving. *Ingest*: one source at a time in segments of up to 12,000 characters (~3k tokens) with section markers, plus the list of existing note titles. The 8k context is never filled, and the whole wiki is never sent.
- **Retrieval method:** BM25 keyword search. It needs no embedding model (nothing extra to download, trivially offline), runs without the language model, and its matches are explainable (the CLI prints the matched terms). The cost is vocabulary mismatch; see [Reflection](#reflection-failures-and-limitations).
- **Research rules versus personality** live in separate files that the harness loads per mode ([`wiki-instructions.md`](prompts/wiki-instructions.md) for ask, [`persona.md`](prompts/persona.md) for chat). Ask never loads the persona.
- **Note naming and folders:** notes are named for their subject in 2 to 5 words, and the H1 matches the filename (`Deloitte Workday Program.md`). Folders are `Experience/`, `Education/`, `Skills/`, `Resume Writing/`, `Job Search/`. Machine data (source id, SHA-256, generating model, old generated titles) lives in each note's properties and in `data/catalog.json`, never in filenames. A note may not share a source file's name, because `[[Master Resume]]` would become ambiguous.
- **Source ids → pages:** `source_id` is the source filename slug (`career-inventory`). Each note records `source_ids` and `sources`; inside the note, each source owns a marked block (`<!-- source:career-inventory start -->`). [`Source Catalog.md`](vault/Source%20Catalog.md) maps every original to its notes.
- **Re-ingestion without duplicates:** unchanged sources are skipped (SHA-256 check). When a source is regenerated, Gemma sees every existing note (title plus one-line description) and must set `existing_note` for each topic to one of those exact titles or `NEW`; Ollama's JSON schema enforces the enum, so the model can't answer with a reworded title. As a fallback, titles are matched against note titles and aliases by word overlap (Dice ≥ 0.65). Both mechanisms came from failures; see Reflection. A matched note has only that source's block replaced, and notes marked `reviewed: true` are never rewritten by the model. Links are only written to notes that exist, and each carries a one-clause reason.
- **Model settings that mattered:** `think: false` (Gemma 4 thinks by default; I turned it off to keep answers fast, but did not A/B test the quality difference); Ollama's `format` JSON schema for ingestion and routing (valid JSON on every call); temperature 0.1 for factual work.

## Wiki review and cleanup

The first ingest ([log](evidence/ingest-first-run.log), [raw generated notes](evidence/ingest-snapshot/wiki)) produced 34 notes. The names were readable, but the note set had real problems, which I fixed by hand against the originals:

- **Duplicates:** 5 education notes, 4 Deloitte notes, 2 ServiceNow notes and 2 Salesforce notes, all merged. The result is **19 reviewed notes**, with old titles kept as `aliases` so re-ingestion maps back to them.
- **Lost uncertainty:** Gemma stated "self-service … instead of manual investigation" and "fast build-and-iterate cycles" as facts, but the source flags both as unverified inferences. The reviewed note says so.
- **Misattribution:** the 2018 Deloitte Technology Innovation Challenge was listed under the 2020–2025 Deloitte job. It is now under Early Career Roles.
- **Broken or garbled bullets:** empty "The" bullets, and "WHAT + HOW + IMPACT at minimum (at least two of the four)". Rewritten.
- **Misfiled notes:** resume-writing notes had landed in `Skills/`. Moved to `Resume Writing/`.
- **Wrong link reason:** in an earlier smoke test, the link pass claimed "BM25 is an alternative to RAG". I kept an eye out for similar reasons; the reviewed notes use hand-checked reasons.

`python scripts/check_links.py` → **217 links in 25 files, all resolve**, including every `#heading` anchor into the originals.

## Evidence

**Offline run: 2026-09-28, 16:05 to 16:14, Wi-Fi disconnected.** [`scripts/offline_demo.ps1`](scripts/offline_demo.ps1) restarted Ollama, then ran `status`, `--help`, `ingest`, `search`, the four `ask` tests and the mode checks; I then used `wiki chat` by hand. Proof of offline execution: the script's connectivity check printed `False`, `wiki status` printed `internet NOT reachable (offline)`, and every card and every logged run from 16:05 to 16:14 records `internet_reachable: false`, including the hand-typed chat session at 16:14 ([run log](evidence/runs/2026-09-28.jsonl)). Model: `gemma4:e4b` (Q4_K_M, digest `c6eb396dbd59`) on Ollama 0.34.3, local only.

*Transcript gap:* Windows PowerShell 5.1's `Start-Transcript` did not capture the output of the search, eval and mode-check steps in that run ([transcript](evidence/offline/transcript.txt)); their results were written to the cards, the mode-checks file and the run log. The script now pipes every command through `Out-Host` so later transcripts are complete.

| Evidence | Link |
|---|---|
| Four ask-mode test cards (offline) | [test-1](evidence/cards/test-1.md) · [test-2](evidence/cards/test-2.md) · [test-3](evidence/cards/test-3.md) · [test-4](evidence/cards/test-4.md) |
| Test questions and expectations, written before running (outside the vault) | [`tests/questions.json`](tests/questions.json) |
| Chat/search/ask mode checks (offline) | [`evidence/checks/mode-checks.md`](evidence/checks/mode-checks.md) |
| Earlier connected dry runs (kept to show what changed) | [cards](evidence/cards-dryrun-connected/) · [mode checks, before fixes](evidence/checks/mode-checks-dryrun-1.md) |
| Offline terminal transcript | [`evidence/offline/transcript.txt`](evidence/offline/transcript.txt) |
| Every search/ask/chat/ingest run, with model identity and `internet_reachable` | [`evidence/runs/`](evidence/runs/) |
| Ingestion logs | [first ingest](evidence/ingest-first-run.log) · [re-ingest failure 1](evidence/reingest-linkedin.log) · [after fuzzy fix](evidence/reingest-linkedin-after-fix.log) · [run 3](evidence/reingest-linkedin-run3.log) · offline failure 2 (in the [transcript](evidence/offline/transcript.txt)) · [after enum fix, run 1](evidence/reingest-linkedin-enum-run1.log) · [run 2](evidence/reingest-linkedin-enum-run2.log) |
| Screen recording of `wiki chat` offline (1 min 55 s) | [Google Drive video](https://drive.google.com/file/d/1EBsZ3rnAR07Bz6uaw9yHkZZZKoXqYWgZ/view?usp=sharing): me running `python wiki.py chat` with Wi-Fi off and typing "what can you help me with?", "can you build out a plan for me?", "3" (answering the assistant's follow-up question), and "make that shorter". The router skipped the notes search on all four turns, which is correct for capability, general-planning and rewrite requests, the assistant asked a clarifying question when the plan request had no target, and "make that shorter" condensed the 1,498-character plan to 436 characters using only conversation context. The matching log entries (`mode: chat`, `internet_reachable: false`, 16:13:03 to 16:14:18) are in [`evidence/runs/2026-09-28.jsonl`](evidence/runs/2026-09-28.jsonl). Hosted on Drive because GitHub rejects files over 100 MB. |
| Obsidian screenshots | [open note](evidence/screenshots/obsidian-note.png) · [index / page list](evidence/screenshots/obsidian-index.png) · [graph](evidence/screenshots/obsidian-graph.png) |

### Test results summary

All four were run offline (2026-09-28 16:07 to 16:08). Each card has the retrieved passages, the verbatim answer, the automatic citation check and my manual assessment.

| Test | Question | Expected evidence | Retrieved? | Answer (offline) | Citations support claims? | Verdict |
|---|---|---|---|---|---|---|
| [1](evidence/cards/test-1.md) Direct | What are the four parts of a strong resume bullet in the Haas standards? | Haas Standards §1 | Yes, S3 of 5 | WHAT, HOW, IMPACT, WHY with correct definitions | Yes, every sentence cites S3 | Pass (7.3 s) |
| [2](evidence/cards/test-2.md) Reworded | How accurate was the finance data move into Workday? | Master Resume / Career Inventory, Deloitte | Yes, S1 and S2 | 99.99% accuracy; requirements, Excel templates, workshops for 35+ units | Yes, both passages contain both facts | Pass (6.6 s) |
| [3](evidence/cards/test-3.md) Two sources | What languages does Andrés speak, and do his resume and LinkedIn agree? | Career Inventory skills + LinkedIn | Yes, S1, S2, S4 | Correct: they disagree (Basque and Portuguese are missing from LinkedIn). Omits English; uses the older "conversational" wording; adds an unneeded INSUFFICIENT EVIDENCE line | Yes for what it claims | Partial (8.2 s) |
| [4](evidence/cards/test-4.md) Unsupported | What was Andrés's GPA at Berkeley Haas? | none exists | GPA-mentioning distractor retrieved as S1 | `INSUFFICIENT EVIDENCE: … do not state Andrés's GPA` | n/a | Pass (4.4 s) |

The same four questions gave the same answers in an earlier connected dry run ([cards](evidence/cards-dryrun-connected/)), so going offline changed nothing about model behavior.

**Mode checks (offline, [full transcript](evidence/checks/mode-checks.md)):** "what can we do?" and "what can you help me with?" → accurate capabilities, no notes search, no citations, no refusal. A draft plan request → the router searched the notes and the plan cites them; "make that shorter" → no new search, the previous passages were reused and the citations still resolve. `search` → passages only. A claim typed in chat ("I also speak fluent Japanese") → the standalone `ask` answered INSUFFICIENT EVIDENCE. Caveats noted in the file: plans aren't labeled "Suggestion:", and a couple of suggested rewrites carry citations.

### Trace one note back to its evidence

[`index.md`](vault/index.md) → *Skills* → [`Languages`](vault/wiki/Skills/Languages.md) → the detail "LinkedIn: … Italian, French and Catalan limited working; no Basque or Portuguese" → link `LinkedIn Profile › Andres Zocchi — LinkedIn Profile` opens [`raw/Source/LinkedIn Profile.md`](vault/raw/Source/LinkedIn%20Profile.md), line 16: `**Languages:** Italian (Limited Working) · French (Limited Working) · …`. The same note's Related section explains why it links to [`Fundación Juanfe Salesforce Project`](vault/wiki/Experience/Fundación%20Juanfe%20Salesforce%20Project.md) ("Spanish-language workshops show professional Spanish in use"). Ask test 3 retrieves the same underlying passages.

## Reflection: failures and limitations

**Main failure: re-ingestion recreated duplicate notes, twice.**

1. *First failure (connected).* After the cleanup I force re-ingested `LinkedIn Profile.md`. Gemma titled topics "UC Berkeley Haas MBA", "ServiceNow Product Management" and "Academic Background And Skills", close variants of existing notes, and the harness created three new files ([log](evidence/reingest-linkedin.log), [files](evidence/reingest-failure/)). **Cause:** deduplication compared exact normalized titles, but the model rewords titles between runs even at temperature 0.1. **Fix 1:** alias-aware fuzzy title matching (Dice word overlap ≥ 0.65). I tested it against the failed titles and all 19 reviewed titles (0 false merges); the next runs mapped [5 of 6](evidence/reingest-linkedin-after-fix.log) and then [6 of 6](evidence/reingest-linkedin-run3.log) topics.
2. *Second failure (the offline demo).* Re-ingesting the same source offline produced "University of Illinois Education" next to the reviewed "Illinois Gies Undergraduate". They share only the word "Illinois", so word overlap could not catch it, which is the limitation I had predicted. **Fix 2:** the model now has to choose. Ingestion lists the existing notes with their descriptions, and the JSON schema restricts a new `existing_note` field to those exact titles or `NEW`. Fuzzy matching remains as a fallback for notes created earlier in the same run. With no alias added for the duplicate's title, two forced re-ingests then mapped all 6 topics to reviewed notes, including the Illinois topic, and created no files ([run 1](evidence/reingest-linkedin-enum-run1.log), [run 2](evidence/reingest-linkedin-enum-run2.log)). These re-runs were done connected, after the offline demo.

**Remaining limitation:** the model can still mark a topic `NEW` when an existing note covers it. It would then fall to the fuzzy matcher, and the reviewer would merge by hand. **Next improvement:** confirm every `NEW` against note summaries with a local embedding similarity check before creating a file.

**Second bug found while taking screenshots:** accented characters in note properties ("Fundación", "Andrés") were written as JSON escapes and not decoded on read, so each re-ingest doubled the backslashes and `index.md` showed `Fundaci\\u00f3n`. Notes are now written as UTF-8 and parsed as JSON on read; the affected properties were repaired.

Other honest limitations:

- **Vocabulary mismatch in BM25.** Test 3 misses the Master Resume's own languages line ("Native fluency in Spanish; working proficiency in French…") because it never contains the word "language". The answer still worked because the Career Inventory quotes it. A local embedding model (e.g. EmbeddingGemma via Ollama) in a hybrid ranker would fix this, at the cost of needing the model running for search.
- **Chat can name the notes without reading them.** In the recorded session the plan request was general, so no notes search ran; the reply still said it would follow "the Berkeley Haas standards" (known only from the persona's description of the wiki) and then gave a generic "Action Verb + What + Result" formula instead of the Haas WHAT/HOW/IMPACT/WHY model. The router should retrieve whenever a reply is about to invoke a specific source.
- **Chat cites suggestions.** Offline, chat attached citations to suggested rewrites (e.g. "Defined user stories" [S5]), where the passage supports the underlying fact but not the wording.
- **Split paragraphs share one line range.** A long bullet split into two passages reports the same `lines 90-92` for both, so a citation is precise to the paragraph, not the sentence.
- **Memory footprint.** Ollama's `gemma4:e4b` package includes vision and audio encoders; on this shared-memory laptop the model costs ~9.7 GB of system RAM, not the ~4.5 GB text-only estimate. A text-only GGUF would be leaner.
- **Chat labels:** the persona asks Margin to label plans "Suggestion:", and it doesn't always do so (see the mode-check draft).
- **Ingestion speed:** 21 minutes for 53k characters. Fine for occasional runs, but slow to iterate on.

## Repository layout

```
wiki.py, wiki.cmd          CLI entry point
harness/                   config, llm (Ollama client), sources (chunking), retrieval (BM25),
                           ingest, modes (search/ask/chat + citation check), evidence (run logs)
prompts/                   persona.md · wiki-instructions.md · ingest-instructions.md · router.md
vault/                     ← open this folder in Obsidian
  index.md, Source Catalog.md
  raw/                     unchanged (redacted) originals
  wiki/<Topic>/            reviewed notes
data/                      chunks.jsonl (retrieval passages), catalog.json (source → notes)
tests/questions.json       ask-mode tests + expectations (outside the vault)
evidence/                  cards, checks, run logs, ingest logs, screenshots, offline transcript
scripts/                   redact_sources, check_links, mode_checks, offline_demo.ps1
```
