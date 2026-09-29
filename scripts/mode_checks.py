"""Scripted chat/search/ask boundary checks -> evidence/checks/mode-checks.md.

Runs the same harness code as `wiki chat`, `wiki search` and `wiki ask`, and
saves a readable transcript. Run it after `wiki ingest`:

    python scripts/mode_checks.py
"""

import datetime as dt
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness import config, evidence, llm, modes  # noqa: E402

OUT = config.EVIDENCE / "checks" / "mode-checks.md"


def quote(text):
    return textwrap.indent(text.strip(), "> ", lambda _: True)


def chat_block(session, message, expectation, force=None):
    r = session.turn(message, force_retrieve=force)
    lines = [f"**You:** {message}", "",
             f"_Harness: {'searched notes for “' + r['query'] + '”' if r['retrieved'] else 'no notes search'}"
             f"{' (reused the previous turn’s passages)' if r['carried'] else ''}"
             f" ({r['reason']}); {len(r['passages'])} passages attached; "
             f"{r['metrics']['wall_seconds']}s._", "",
             "**Margin (chat):**", "", quote(r["reply"]), ""]
    if r["citations"]:
        cited = ", ".join(f"{s} → `{src}`" for s, src in zip(r["citations"]["cited"], r["citations"]["cited_sources"]))
        lines += [f"Citations: {cited or 'none'}", ""]
    lines += [f"**Expected:** {expectation}", "", "**Result:** _pending review_", ""]
    return "\n".join(lines)


def main():
    llm.check_ready()
    rt = evidence.runtime()
    parts = [
        "# Mode boundary checks", "",
        f"- Time: {dt.datetime.now().isoformat(timespec='seconds')}",
        f"- Model: `{rt.get('model')}` ({rt.get('parameter_size')}, {rt.get('quantization')}), "
        f"Ollama {rt.get('ollama_version')}, execution: local",
        f"- Internet reachable during run: {evidence.internet_reachable()}", "",
    ]

    print("chat: capability questions")
    parts += ["## 1. Chat: capability questions", ""]
    s = modes.ChatSession()
    parts.append(chat_block(s, "what can we do?",
                            "Accurate capabilities, no notes search, no citations, no insufficient-evidence reply."))
    s = modes.ChatSession()
    parts.append(chat_block(s, "what can you help me with?",
                            "Same: real capabilities and a useful starting point."))

    print("chat: draft + follow-up")
    parts += ["## 2. Chat: draft, then follow-up", ""]
    s = modes.ChatSession()
    parts.append(chat_block(s, "Draft a short plan for tailoring my resume to a product management internship.",
                            "A plan labeled as a suggestion. If notes are used, facts from them are cited."))
    parts.append(chat_block(s, "make that shorter",
                            "Shortens the previous plan using conversation context; no new notes search."))

    print("search")
    parts += ["## 3. Search: original passages only", "",
              "Command equivalent: `wiki search \"Workday data migration\"`", ""]
    for i, p in enumerate(modes.search("Workday data migration", k=3), 1):
        parts += [f"**[S{i}]** `vault/{p['path']}` — {p['location']} — score {p['score']}", "", quote(p["text"]), ""]
    parts += ["**Expected:** matching original passages with paths; no generated answer.", "",
              "**Result:** _pending review_", ""]

    print("chat claim vs ask")
    parts += ["## 4. A claim made only in chat is not evidence for ask", ""]
    s = modes.ChatSession()
    parts.append(chat_block(s, "Quick note for later: I also speak fluent Japanese.",
                            "Acknowledges; the claim now exists only in chat history.", force=False))
    q = "Does Andrés speak Japanese?"
    r = modes.ask(q)
    parts += [f"Then, as a standalone ask: `wiki ask \"{q}\"`", "", "**Gemma (ask):**", "", quote(r["answer"]), "",
              "Retrieved: " + "; ".join(f"S{i} `{p['path']}` ({p['location']})" for i, p in enumerate(r["passages"], 1)), "",
              "**Expected:** INSUFFICIENT EVIDENCE (or an answer citing sources that show Japanese is not listed). "
              "The chat claim must not appear as evidence.", "", "**Result:** _pending review_", ""]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
