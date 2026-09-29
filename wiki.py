#!/usr/bin/env python3
"""wiki — a personal wiki CLI over your own notes, powered by local Gemma.

This file is the CLI: it parses the command, picks the mode, and prints
results. The harness logic lives in harness/ (see README "Architecture").
"""

import argparse
import datetime as dt
import json
import sys
import textwrap
from pathlib import Path

from harness import config, evidence, ingest, llm, modes, retrieval

DIM, BOLD, CYAN, YELLOW, RESET = "\033[2m", "\033[1m", "\033[36m", "\033[33m", "\033[0m"

EPILOG = f"""\
modes:
  search  shows original passages + source paths. No model; works with Ollama stopped.
  ask     standalone factual answer from retrieved passages, with [S#] citations,
          or INSUFFICIENT EVIDENCE. Never uses chat history or the persona.
  chat    personal assistant with conversation memory; searches notes only when
          the message needs them. In-chat commands: /help /notes /nonotes /sources
          /save /reset /exit

examples:
  wiki ingest ./vault/raw
  wiki search "workshop location"
  wiki ask "Where is the workshop?" --mode local
  wiki chat
  wiki eval tests/questions.json

configuration (environment variables):
  WIKI_MODEL        Ollama model tag            (now: {config.MODEL})
  OLLAMA_HOST       local Ollama server         (now: {config.OLLAMA_HOST})
  WIKI_NUM_CTX      context window tokens       (now: {config.NUM_CTX})
  WIKI_TOP_K        passages per question       (now: {config.TOP_K})
  WIKI_CHUNK_CHARS  target passage size, chars  (now: {config.CHUNK_TARGET})

required inputs: sources (.md, .txt, .pdf) in vault/raw/, Ollama running with
the model pulled (`ollama pull {config.MODEL}`). search needs only an ingested index.
"""


def banner(mode):
    print(f"{DIM}[{mode} · model {config.MODEL} · execution: local · {config.OLLAMA_HOST}]{RESET}")


def echo(piece):
    print(piece, end="", flush=True)


def show_passages(passages, full=True):
    for i, p in enumerate(passages, start=1):
        print(f"{CYAN}[S{i}]{RESET} {BOLD}vault/{p['path']}{RESET} {DIM}| {p['location']} "
              f"| score {p.get('score', 0):.2f} | matched: {', '.join(p.get('terms', []))}{RESET}")
        if full:
            print(textwrap.indent(p["text"], "    "))
            print()


def show_citations(check, passages):
    if check is None:
        return
    for s, src in zip(check["cited"], check["cited_sources"]):
        print(f"  {CYAN}{s}{RESET} → vault/{src}")
    for problem in check["problems"]:
        print(f"  {YELLOW}citation check: {problem}{RESET}")


# ---------------------------------------------------------------- commands

def cmd_ingest(args):
    banner("ingest")
    summary = ingest.ingest(args.path, force=args.force)
    evidence.log_run("ingest", **summary)


def cmd_search(args):
    print(f"{DIM}[search · retrieval only, no model · BM25 over {config.CHUNKS.name}]{RESET}")
    if not config.CHUNKS.exists():
        sys.exit("No index yet. Run: wiki ingest ./vault/raw")
    passages = modes.search(args.query, k=args.k)
    if not passages:
        print("No matching passages.")
    show_passages(passages)


def cmd_ask(args):
    banner("ask")
    if not config.CHUNKS.exists():
        sys.exit("No index yet. Run: wiki ingest ./vault/raw")
    llm.check_ready()
    print(f"{BOLD}Q:{RESET} {args.question}\n{BOLD}A:{RESET} ", end="")
    result = modes.ask(args.question, stream_to=echo, k=args.k)
    print("\n")
    print(f"{BOLD}Citations{RESET}")
    show_citations(result["citations"], result["passages"])
    if args.show_passages:
        print(f"\n{BOLD}Retrieved passages{RESET}")
        show_passages(result["passages"])
    else:
        print(f"{DIM}Retrieved: " + "; ".join(f"S{i} {p['path']}" for i, p in
              enumerate(result["passages"], 1)) + f"  (--show-passages for text){RESET}")
    m = result["metrics"]
    if m.get("model_called"):
        print(f"{DIM}{m['wall_seconds']}s total, first token {m['first_token_seconds']}s, "
              f"{m.get('tokens_per_second', '?')} tok/s · run {result['run_id']}{RESET}")


CHAT_HELP = """\
  just type        talk; I search your notes only when the message needs them
  /notes <msg>     force a notes search for this message
  /nonotes <msg>   answer without searching notes
  /sources         show the passages behind my last reply
  /save            save my last reply as a draft in outputs/drafts/ (never evidence)
  /reset           forget this conversation
  /exit            quit"""


def cmd_chat(args):
    banner("chat")
    llm.check_ready()
    session = modes.ChatSession()
    print(f"{DIM}Type /help for commands.{RESET}\n")
    while True:
        try:
            msg = input(f"{BOLD}you ›{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return
        if not msg:
            continue
        force = None
        low = msg.lower()
        if low in ("/exit", "/quit"):
            print("bye.")
            return
        if low == "/help":
            print(CHAT_HELP + "\n")
            continue
        if low == "/reset":
            session = modes.ChatSession()
            print(f"{DIM}(conversation cleared){RESET}\n")
            continue
        if low == "/sources":
            show_passages(session.last_passages) if session.last_passages else print("No notes used in my last reply.\n")
            continue
        if low == "/save":
            save_draft(session)
            continue
        if low.startswith("/notes "):
            force, msg = True, msg[7:]
        elif low.startswith("/nonotes "):
            force, msg = False, msg[9:]

        try:
            print(f"{DIM}…{RESET}", end="\r", flush=True)
            retrieve, query, reason = session.route(msg, force)
            note = f"searched notes for “{query}”" if retrieve else "no notes search"
            print(f"{DIM}[{note} — {reason}]{RESET}")
            print(f"{BOLD}wiki ›{RESET} ", end="", flush=True)
            result = session.turn(msg, stream_to=echo, force_retrieve=retrieve)
        except (RuntimeError, llm.ModelUnavailable) as err:
            print(f"\n{YELLOW}[{err}]{RESET}\n")
            continue
        except KeyboardInterrupt:
            print(f"\n{DIM}[interrupted]{RESET}\n")
            continue
        print()
        if result["carried"]:
            print(f"{DIM}[follow-up: reused the previous turn's passages]{RESET}")
        if result["passages"]:
            show_citations(result["citations"], result["passages"])
        print()


def save_draft(session):
    """Explicit user action. Drafts go to outputs/, never into vault/raw/."""
    last = next((m for m in reversed(session.history) if m["role"] == "assistant"), None)
    if not last:
        print("Nothing to save yet.\n")
        return
    config.DRAFTS.mkdir(parents=True, exist_ok=True)
    path = config.DRAFTS / f"draft-{dt.datetime.now():%Y%m%d-%H%M%S}.md"
    path.write_text(f"<!-- generated draft by {config.MODEL}; not source evidence -->\n\n"
                    f"{last['content']}\n", encoding="utf-8")
    print(f"{DIM}Saved draft to {path.relative_to(config.ROOT)}{RESET}\n")


def cmd_status(args):
    print(f"model      {config.MODEL}")
    info = llm.runtime_info()
    for key in ("ollama_version", "quantization", "parameter_size", "digest"):
        print(f"{key:<10} {info.get(key)}")
    mem = llm.loaded_memory()
    if mem:
        print(f"loaded     {mem['size_bytes'] / 2**30:.2f} GiB total, "
              f"{mem['size_vram_bytes'] / 2**30:.2f} GiB on GPU")
    else:
        print("loaded     (model not currently in memory)")
    chunks = retrieval.load_chunks()
    print(f"passages   {len(chunks)} from {len({c['path'] for c in chunks})} sources")
    print(f"notes      {sum(1 for _ in config.WIKI.rglob('*.md'))} in vault/wiki/")
    print(f"internet   {'reachable' if evidence.internet_reachable() else 'NOT reachable (offline)'}")


def cmd_eval(args):
    """Run fixed ask-mode tests and write one evidence card per question."""
    banner("eval (ask mode)")
    llm.check_ready()
    tests = json.loads(Path(args.file).read_text(encoding="utf-8"))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in tests:
        print(f"\n{BOLD}{t['id']}:{RESET} {t['question']}")
        result = modes.ask(t["question"])
        print(result["answer"])
        card = render_card(t, result)
        path = out_dir / f"{t['id']}.md"
        path.write_text(card, encoding="utf-8")
        print(f"{DIM}→ {path}{RESET}")


def render_card(t, r):
    rt = evidence.runtime()
    got = [p["path"] for p in r["passages"]]
    hits = [s for s in t.get("expected_sources", []) if s in got]
    phrase_hits = [ph for ph in t.get("expected_phrases", [])
                   if any(ph.lower() in p["text"].lower() for p in r["passages"])]
    lines = [
        f"# {t['id']}: {t['kind']}", "",
        f"**Question:** {t['question']}", "",
        "| Field | Value |", "|---|---|",
        f"| Mode | ask (standalone, no chat history) |",
        f"| Execution | local (Ollama at {config.OLLAMA_HOST}) |",
        f"| Internet reachable during run | {evidence.internet_reachable()} |",
        f"| Model | `{rt.get('model')}` · {rt.get('parameter_size')} · {rt.get('quantization')} · digest `{rt.get('digest')}` |",
        f"| Runtime | Ollama {rt.get('ollama_version')} |",
        f"| Run id | `{r['run_id']}` (full record in `evidence/runs/`) |",
        f"| Time | {dt.datetime.now().isoformat(timespec='seconds')} |", "",
        "## Expected (written before running)", "",
        t["expected_behavior"], "",
        f"Expected sources: {', '.join(f'`{s}`' for s in t.get('expected_sources', [])) or 'none'}", "",
        "## Retrieval check (automatic)", "",
        f"- Expected sources retrieved: {len(hits)}/{len(t.get('expected_sources', []))} {hits}",
        f"- Expected phrases found in passages: {len(phrase_hits)}/{len(t.get('expected_phrases', []))} {phrase_hits}", "",
        "## Retrieved passages", "",
    ]
    for i, p in enumerate(r["passages"], 1):
        lines += [f"**[S{i}]** `vault/{p['path']}` — {p['location']} — score {p['score']}", "",
                  textwrap.indent(p["text"], "> ", lambda _: True), ""]
    if not r["passages"]:
        lines += ["_No passages matched._", ""]
    c = r["citations"]
    m = r["metrics"]
    lines += [
        "## Gemma answer (verbatim)", "", textwrap.indent(r["answer"].strip(), "> ", lambda _: True), "",
        "## Citation check (automatic)", "",
        f"- Cited: {', '.join(f'{s} → `{src}`' for s, src in zip(c['cited'], c['cited_sources'])) or 'none'}",
        f"- Insufficient-evidence response: {c['insufficient_evidence']}",
        f"- Problems: {'; '.join(c['problems']) or 'none'}", "",
        "## Timing", "",
        f"- Wall time {m.get('wall_seconds')}s, first token {m.get('first_token_seconds')}s, "
        f"{m.get('tokens_per_second')} tok/s, prompt {m.get('prompt_tokens')} tokens, "
        f"output {m.get('output_tokens')} tokens" if m.get("model_called") else "- Model not called",
        "", "## Manual assessment", "",
        "_Pending: open each cited source and check every material claim._", "",
    ]
    return "\n".join(lines)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        prog="wiki", description="Personal wiki CLI: chat, ask and search your own notes with local Gemma.",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", metavar="command")

    p = sub.add_parser("ingest", help="read sources, generate linked wiki notes, rebuild the index")
    p.add_argument("path", nargs="?", default=str(config.RAW), help="file or folder (default: vault/raw)")
    p.add_argument("--force", action="store_true", help="regenerate notes even if a source is unchanged")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("search", help="show matching original passages (no model)")
    p.add_argument("query")
    p.add_argument("-k", type=int, default=config.TOP_K, help="number of passages")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("ask", help="standalone factual answer with citations")
    p.add_argument("question")
    p.add_argument("--mode", choices=["local"], default="local",
                   help="where the model runs (only local is implemented)")
    p.add_argument("-k", type=int, default=config.TOP_K, help="passages to retrieve")
    p.add_argument("--show-passages", action="store_true", help="print retrieved passage text")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("chat", help="personal assistant with conversation memory")
    p.add_argument("--mode", choices=["local"], default="local")
    p.set_defaults(func=cmd_chat)

    p = sub.add_parser("eval", help="run fixed ask-mode tests and write evidence cards")
    p.add_argument("file", nargs="?", default="tests/questions.json")
    p.add_argument("--out", default=str(config.EVIDENCE / "cards"))
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("status", help="model, runtime, memory use, index size, connectivity")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    try:
        args.func(args)
    except (llm.ModelUnavailable, FileNotFoundError, FileExistsError) as err:
        sys.exit(f"error: {err}")
    except KeyboardInterrupt:
        sys.exit("\ninterrupted")


if __name__ == "__main__":
    main()
