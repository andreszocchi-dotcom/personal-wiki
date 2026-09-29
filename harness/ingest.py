"""Ingestion: original sources -> local Gemma -> linked wiki notes + index.

Pipeline for `wiki ingest <path>`:
  1. Copy any file from outside vault/raw/ into it byte-for-byte (originals
     are never modified afterwards).
  2. For each new or changed source, send its text plus ingest-instructions.md
     and the list of existing note titles to Gemma, asking for structured
     topics (title, folder, summary, details with source sections, related).
  3. Resolve each topic title against existing notes so re-ingesting reuses the
     same file instead of creating a duplicate.
  4. Write notes: each source owns a marked block inside the note, so
     re-ingesting source A replaces A's block and leaves B's alone. Notes
     marked `reviewed: true` are never rewritten by the model.
  5. Rebuild the passage index (data/chunks.jsonl), the machine catalog
     (data/catalog.json), vault/index.md and vault/Source Catalog.md.
"""

import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path

from . import config, llm, retrieval, sources

FOLDERS = [f.strip() for f in
           os.environ.get("WIKI_FOLDERS", "Experience,Education,Skills,Resume Writing,Job Search").split(",")]

TOPIC_SCHEMA = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "folder": {"type": "string", "enum": FOLDERS},
                    "summary": {"type": "string"},
                    "details": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "point": {"type": "string"},
                                "section": {"type": "string"},
                            },
                            "required": ["point", "section"],
                        },
                    },
                    "related": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "why": {"type": "string"},
                            },
                            "required": ["title", "why"],
                        },
                    },
                },
                "required": ["title", "folder", "summary", "details", "related"],
            },
        }
    },
    "required": ["topics"],
}

def topic_schema(existing_titles):
    """TOPIC_SCHEMA plus an `existing_note` field whose allowed values are the
    exact titles on disk or "NEW". Ollama enforces the enum, so the model must
    pick a real note instead of rephrasing its title."""
    schema = json.loads(json.dumps(TOPIC_SCHEMA))
    item = schema["properties"]["topics"]["items"]
    item["properties"]["existing_note"] = {"type": "string", "enum": sorted(existing_titles) + ["NEW"]}
    item["required"] = ["existing_note"] + item["required"]
    return schema


BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|#^\[\]]')


# ---------------------------------------------------------------- notes on disk

def read_note(path):
    """Split a note into (frontmatter dict, body). Minimal YAML: scalars + lists."""
    text = Path(path).read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---\n"):
        head, _, body = text[4:].partition("\n---\n")
        for line in head.splitlines():
            key, _, val = line.partition(":")
            val = val.strip()
            # write_note emits JSON strings and arrays; read them back as JSON
            # so escapes don't pile up on every rewrite.
            try:
                meta[key.strip()] = json.loads(val) if val[:1] in '["' else val
            except json.JSONDecodeError:
                meta[key.strip()] = val.strip('"')
        return meta, body
    return meta, text


def write_note(path, meta, body):
    lines = ["---"]
    for key, val in meta.items():
        if isinstance(val, list):
            lines.append(f"{key}: [{', '.join(json.dumps(v, ensure_ascii=False) for v in val)}]")
        else:
            lines.append(f"{key}: {json.dumps(val, ensure_ascii=False) if isinstance(val, str) else val}")
    lines.append("---")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n" + body.lstrip("\n"), encoding="utf-8")


def existing_notes():
    """Map normalized title -> note path for every note under vault/wiki/."""
    notes = {}
    for p in config.WIKI.rglob("*.md"):
        meta, _ = read_note(p)
        notes[norm(p.stem)] = p
        for alias in meta.get("aliases", []) or []:
            notes.setdefault(norm(alias), p)
    return notes


def norm(title):
    """Comparison key so 'GPU Parallel Training' == 'gpu-parallel trainings'."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words)


TITLE_FILLER = {"and", "the", "of", "for", "a", "an", "in", "to", "details", "overview",
                "status", "info", "information", "notes", "summary"}


def find_existing(title, notes):
    """Match a generated title to an existing note (title or alias).

    Exact match first. Otherwise fuzzy: the model rephrases titles between
    runs ("UC Berkeley Haas MBA" vs "Berkeley Haas MBA"), so a title maps to
    the note whose content words overlap most, if the Dice overlap
    2*shared/(len(a)+len(b)) is at least 0.65. Without this, re-ingesting a
    source recreated near-duplicate notes (see evidence/reingest-failure/).
    """
    key = norm(title)
    if key in notes:
        return notes[key]
    words = set(key.split()) - TITLE_FILLER
    best, best_score = None, 0.0
    for other, path in notes.items():
        other_words = set(other.split()) - TITLE_FILLER
        if not words or not other_words:
            continue
        score = 2 * len(words & other_words) / (len(words) + len(other_words))
        if score >= 0.65 and score > best_score:
            best, best_score = path, score
    return best


def note_for_topic(topic, notes):
    """The existing note a generated topic belongs to, or None for a new note.

    The model's explicit existing_note choice wins. Fuzzy title matching is
    the fallback, e.g. for a note created earlier in the same run."""
    chosen = topic.get("existing_note", "NEW")
    if chosen != "NEW" and norm(chosen) in notes:
        return notes[norm(chosen)]
    return find_existing(unique_from_sources(clean_title(topic["title"])), notes)


def clean_title(title):
    """Readable filename: no path/link characters, at most 6 words.

    Anything after a colon is dropped: when shown "Title: description" lists,
    the model sometimes copies the whole line back as the title.
    """
    title = BAD_FILENAME_CHARS.sub(" ", title.split(":")[0])
    title = re.sub(r"\s+", " ", title).strip(" .-")
    words = title.split(" ")
    return " ".join(words[:6]) or "Untitled"


# ---------------------------------------------------------------- ingestion

def import_into_raw(path):
    """Copy an outside file into vault/raw/ unchanged; refuse silent overwrite."""
    path = Path(path).resolve()
    if config.RAW.resolve() in path.parents:
        return path
    dest = config.RAW / path.name
    if dest.exists() and sources.file_hash(dest) != sources.file_hash(path):
        raise FileExistsError(f"{dest} already exists with different content; rename one of them.")
    config.RAW.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


def load_catalog():
    if config.CATALOG.exists():
        return json.loads(config.CATALOG.read_text(encoding="utf-8"))
    return {}


def extract_topics(path, existing, log):
    """Ask Gemma for topics in one source, in segments that fit the context.

    existing: {title: description} of notes already on disk.
    """
    rules = config.INGEST_RULES.read_text(encoding="utf-8")
    units = [f"[{label}]\n{text}" for label, _, _, text in sources.read_units(path)]
    segments, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) > config.INGEST_MAX_CHARS:
            segments.append(cur)
            cur = ""
        cur += u + "\n\n"
    if cur.strip():
        segments.append(cur)

    topics, metrics = [], []
    for i, seg in enumerate(segments, start=1):
        log(f"  Gemma call {i}/{len(segments)} ({len(seg):,} chars of source text)")
        messages = [
            {"role": "system", "content": rules},
            {"role": "user", "content":
                f"Allowed folders: {', '.join(FOLDERS)}\n"
                f"Existing notes. For each topic, set existing_note to the exact title of the existing "
                f"note that covers the same subject (even if you would word the title differently), "
                f"or NEW if none does:\n"
                f"{chr(10).join(f'- {t}: {d}' for t, d in sorted(existing.items())) or '- (none yet)'}\n\n"
                f"Source file: {sources.rel(path)}\n"
                f"Section labels appear in [brackets]; use them in 'section'.\n\n"
                f"--- SOURCE TEXT ---\n{seg}--- END SOURCE TEXT ---"},
        ]
        data, m = llm.chat_json(messages, topic_schema(existing))
        metrics.append(m)
        topics.extend(data.get("topics", []))
    return topics, metrics


LINK_SCHEMA = {
    "type": "object",
    "properties": {
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"from": {"type": "string"}, "to": {"type": "string"},
                               "why": {"type": "string"}},
                "required": ["from", "to", "why"],
            },
        }
    },
    "required": ["links"],
}


def link_topics(topics, catalog_titles, log):
    """Second pass: once every title in the run is known, ask Gemma which notes
    genuinely connect. The first source ingested can't link forward otherwise."""
    others = {t: d for t, d in catalog_titles.items()}
    if len(others) < 2:
        return
    log(f"  Gemma link pass for {len(topics)} topic(s)")
    listing = "\n".join(f"- {t}: {d}" for t, d in sorted(others.items()))
    new = "\n".join(f"- {clean_title(t['title'])}: {t['summary']}" for t in topics)
    data, _ = llm.chat_json([
        {"role": "system", "content":
            "You connect notes in a personal wiki. For each note in NEW NOTES, pick notes from ALL NOTES "
            "that a reader of it would genuinely want to open next, and say why in one short clause "
            "(e.g. 'the retrieval method this workflow uses'). Only link when the subjects really "
            "connect; zero links is fine. Use titles exactly as written. Never link a note to itself."},
        {"role": "user", "content": f"ALL NOTES:\n{listing}\n\nNEW NOTES:\n{new}"},
    ], LINK_SCHEMA)
    by_title = {norm(clean_title(t["title"])): t for t in topics}
    for link in data.get("links", []):
        topic = by_title.get(norm(clean_title(link["from"])))
        if topic is not None:
            topic["related"].append({"title": link["to"], "why": link["why"]})


def merge_topics(topics):
    """Merge topics that came back with the same title from different segments."""
    merged = {}
    for t in topics:
        chosen = t.get("existing_note", "NEW")
        key = norm(chosen) if chosen != "NEW" else norm(clean_title(t["title"]))
        if key in merged:
            merged[key]["details"] += t["details"]
            merged[key]["related"] += t["related"]
        else:
            merged[key] = dict(t)
    return list(merged.values())


def source_link(src_rel, section):
    """Obsidian link to the original, pointing at the heading when possible."""
    if src_rel.endswith(".pdf") and section.startswith("page "):
        return f"[[{src_rel}#page={section.split()[1]}|{Path(src_rel).name}, {section}]]"
    last = section.split(" > ")[-1] if section and section != "(top)" else ""
    if src_rel.endswith((".md", ".markdown")) and last:
        return f"[[{src_rel}#{BAD_FILENAME_CHARS.sub(' ', last).strip()}|{Path(src_rel).name} › {last}]]"
    return f"[[{src_rel}|{Path(src_rel).name}]]"


def render_source_block(sid, src_rel, topic):
    lines = [f"<!-- source:{sid} start -->", f"### From {Path(src_rel).name}"]
    for d in topic["details"]:
        lines.append(f"- {d['point'].strip()} ({source_link(src_rel, d['section'].strip('[] '))})")
    lines.append(f"<!-- source:{sid} end -->")
    return "\n".join(lines)


def upsert_note(topic, sid, src_rel, notes, link_targets, run_date, log):
    """Create or update one note. Returns its path."""
    title = unique_from_sources(clean_title(topic["title"]))
    path = note_for_topic(topic, notes)
    key = norm(path.stem) if path else norm(title)
    folder = topic["folder"] if topic["folder"] in FOLDERS else FOLDERS[0]

    related = []
    for r in topic["related"]:
        target = link_targets.get(norm(clean_title(r["title"])))
        if target is None:
            match = find_existing(clean_title(r["title"]), notes)
            target = match.stem if match else None
        if target and norm(target) != key and target not in [t for t, _ in related]:
            related.append((target, r["why"].strip()))

    block = render_source_block(sid, src_rel, topic)

    if path is None:
        path = config.WIKI / folder / f"{title}.md"
        meta = {
            "title": title,
            "description": first_sentence(topic["summary"]),
            "source_ids": [sid],
            "sources": [src_rel],
            "generated_by": config.MODEL,
            "reviewed": "false",
            "updated": run_date,
        }
        body = (f"# {title}\n\n{topic['summary'].strip()}\n\n## Details\n\n{block}\n\n"
                f"## Related\n\n{render_related(related)}\n\n## Sources\n\n")
        write_note(path, meta, body)
        notes[key] = path
        log(f"  + created {path.relative_to(config.VAULT).as_posix()}")
        return path

    meta, body = read_note(path)
    if str(meta.get("reviewed", "false")).lower() == "true":
        log(f"  = kept reviewed note {path.relative_to(config.VAULT).as_posix()} (not regenerated)")
        return path

    marker = re.compile(rf"<!-- source:{re.escape(sid)} start -->.*?<!-- source:{re.escape(sid)} end -->", re.S)
    if marker.search(body):
        body = marker.sub(lambda _: block, body)
    else:
        body = body.replace("\n## Related", f"\n{block}\n\n## Related", 1)

    have = set(re.findall(r"\[\[([^\]|#]+)", body.split("## Related", 1)[-1].split("## Sources")[0]))
    extra = [(t, w) for t, w in related if t not in have]
    if extra:
        head, _, tail = body.partition("## Related\n\n")
        rel_body, _, rest = tail.partition("\n\n## Sources")
        rel_body = rel_body.replace("_No related notes yet._", "").strip()
        body = f"{head}## Related\n\n{(rel_body + chr(10)) if rel_body else ''}{render_related(extra)}\n\n## Sources{rest}"

    meta["source_ids"] = sorted(set(meta.get("source_ids", [])) | {sid})
    meta["sources"] = sorted(set(meta.get("sources", [])) | {src_rel})
    meta["updated"] = run_date
    write_note(path, meta, body)
    log(f"  ~ updated {path.relative_to(config.VAULT).as_posix()}")
    return path


def render_related(related):
    if not related:
        return "_No related notes yet._"
    return "\n".join(f"- [[{t}]] — {w}" for t, w in related)


def unique_from_sources(title):
    """A note may not share a raw source's filename: Obsidian would resolve
    [[Master Resume]] ambiguously. Qualify the note instead of renaming the source."""
    stems = {norm(p.stem) for p in sources.list_sources(config.RAW)}
    return f"{title} Overview" if norm(title) in stems else title


def first_sentence(text, limit=200):
    """First sentence for index.md; long ones are cut at a word boundary."""
    m = re.match(r"(.+?[.!?])(\s|$)", text.strip())
    sentence = m.group(1) if m else text.strip()
    if len(sentence) <= limit:
        return sentence
    return sentence[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def fill_sources_sections(catalog):
    """Rewrite each note's ## Sources list from its frontmatter."""
    for p in config.WIKI.rglob("*.md"):
        meta, body = read_note(p)
        head, sep, _ = body.partition("## Sources")
        if not sep:
            continue
        lines = []
        for src in meta.get("sources", []):
            entry = catalog.get(sources.source_id(src), {})
            lines.append(f"- [[{src}|{Path(src).name}]] — source id `{sources.source_id(src)}`"
                         + (f", sha256 `{entry['sha256']}`" if entry.get("sha256") else ""))
        write_note(p, meta, f"{head}## Sources\n\n" + "\n".join(lines) + "\n")


def rebuild_index_pages(catalog):
    """vault/index.md (topic landing page) and vault/Source Catalog.md."""
    groups = {}
    for p in sorted(config.WIKI.rglob("*.md")):
        meta, _ = read_note(p)
        groups.setdefault(p.parent.name, []).append((p.stem, meta.get("description", "")))

    out = ["# Personal Wiki", "",
           "Start here. Notes are grouped by topic folder; each note links to related notes "
           "and back to its original source in `raw/`. See [[Source Catalog]] for the list of originals.", ""]
    for folder in [f for f in FOLDERS if f in groups] + sorted(set(groups) - set(FOLDERS)):
        out += [f"## {folder}", ""]
        out += [f"- [[{title}]] — {desc}" for title, desc in groups[folder]]
        out.append("")
    config.INDEX_MD.write_text("\n".join(out), encoding="utf-8")

    rows = ["# Source Catalog", "",
            "Original files in `raw/` are preserved unchanged. Each maps to the wiki notes generated from it.", "",
            "| Source | Source id | SHA-256 (first 16) | Ingested | Notes |", "|---|---|---|---|---|"]
    for sid, e in sorted(catalog.items()):
        notes = ", ".join(f"[[{n}]]" for n in e.get("notes", []))
        rows.append(f"| [[{e['path']}\\|{Path(e['path']).name}]] | `{sid}` | `{e['sha256']}` | {e['ingested']} | {notes} |")
    config.SOURCES_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")


def rebuild_passages():
    """Re-chunk every original. Cheap, needs no model, keeps search in sync."""
    chunks = []
    for p in sources.list_sources(config.RAW):
        chunks.extend(sources.chunk_source(p))
    retrieval.save_chunks(chunks)
    return chunks


def ingest(path, force=False, log=print):
    """Run the full pipeline. Returns a summary dict (also saved as evidence)."""
    files = [import_into_raw(p) for p in sources.list_sources(path)]
    if not files:
        raise FileNotFoundError(f"No supported sources (.md, .txt, .pdf) found in {path}")

    catalog = load_catalog()
    run_date = dt.date.today().isoformat()
    todo = []
    for f in files:
        sid, digest = sources.source_id(f), sources.file_hash(f)
        prev = catalog.get(sid)
        if prev and prev["sha256"] == digest and not force:
            log(f"= {sources.rel(f)} unchanged since {prev['ingested']} (use --force to regenerate)")
        else:
            todo.append((f, sid, digest))

    summary = {"files": [sources.rel(f) for f in files], "generated": [], "metrics": []}
    if todo:
        llm.check_ready()
        notes = existing_notes()
        # Phase 1: ask Gemma about every source before writing anything, so
        # links between notes from different sources in the same run resolve.
        extracted = []
        for f, sid, digest in todo:
            log(f"> {sources.rel(f)}")
            on_disk = {p.stem: read_note(p)[0].get("description", "") for p in set(notes.values())}
            topics, metrics = extract_topics(f, on_disk, log)
            summary["metrics"] += metrics
            extracted.append((f, sid, digest, merge_topics(topics)))

        link_targets = {k: p.stem for k, p in notes.items()}
        for _, _, _, topics in extracted:
            for t in topics:
                key, title = norm(clean_title(t["title"])), unique_from_sources(clean_title(t["title"]))
                existing = note_for_topic(t, notes)
                link_targets.setdefault(key, existing.stem if existing else title)

        # Phase 2: with every title known, add links between related notes.
        all_titles = {p.stem: read_note(p)[0].get("description", "") for p in set(notes.values())}
        for _, _, _, topics in extracted:
            for t in topics:
                all_titles.setdefault(link_targets[norm(clean_title(t["title"]))], first_sentence(t["summary"]))
        for f, _, _, topics in extracted:
            log(f"> links for {sources.rel(f)}")
            link_topics(topics, all_titles, log)

        # Phase 3: write notes and record which notes came from which source.
        for f, sid, digest, topics in extracted:
            src_rel = sources.rel(f)
            written = [upsert_note(t, sid, src_rel, notes, link_targets, run_date, log) for t in topics]
            catalog[sid] = {"path": src_rel, "sha256": digest, "ingested": run_date,
                            "model": config.MODEL, "notes": sorted({p.stem for p in written})}
            summary["generated"] += [p.relative_to(config.VAULT).as_posix() for p in written]

        config.DATA.mkdir(parents=True, exist_ok=True)
        config.CATALOG.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
        fill_sources_sections(catalog)

    rebuild_index_pages(catalog)
    chunks = rebuild_passages()
    summary["passage_count"] = len(chunks)
    log(f"Index: {len(chunks)} passages from {len(sources.list_sources(config.RAW))} sources; "
        f"{sum(1 for _ in config.WIKI.rglob('*.md'))} wiki notes; index.md updated.")
    return summary
