"""Read original sources from vault/raw/ and split them into passages.

Originals are only ever read, never written. Every passage keeps its source
path plus a human location (heading and line range, or PDF page) so search
results and citations can be traced back to the exact original text.
"""

import hashlib
import re
from pathlib import Path

from . import config

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
SUPPORTED = TEXT_SUFFIXES | {".pdf"}
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def list_sources(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file or folder: {path}")
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*") if p.is_file() and not p.name.startswith("."))
    return [p for p in files if p.suffix.lower() in SUPPORTED]


def rel(path):
    """Vault-relative path with forward slashes, e.g. raw/notes.md."""
    return Path(path).resolve().relative_to(config.VAULT.resolve()).as_posix()


def source_id(path):
    """Stable machine id: filename stem slug. Kept in metadata, never a note name."""
    stem = re.sub(r"[^a-z0-9]+", "-", Path(path).stem.lower()).strip("-")
    return stem or "source"


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def read_units(path):
    """Yield (location_label, line_start, line_end, text) blocks.

    Markdown/text: paragraph blocks labeled with their heading path.
    PDF: one block per page (needs `pypdf`, which runs fully offline).
    """
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        yield from _pdf_units(path)
        return

    text = path.read_text(encoding="utf-8", errors="replace")
    headings = []           # current heading stack
    block, block_start = [], None
    n = 0

    def flush(end):
        if block and "".join(block).strip():
            # Drop the document title (H1) once deeper headings exist, so labels
            # read "EXPERIENCE > ServiceNow ..." rather than repeating the title.
            shown = headings[1:] if len(headings) > 1 and headings[0][0] == 1 else headings
            label = " > ".join(h for _, h in shown) or "(top)"
            yield label, block_start, end, "\n".join(block).strip()

    lines = text.splitlines()
    body_start = 0
    if lines and lines[0].strip() == "---":
        # YAML properties: one passage labeled "(properties)", not wiki text.
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        if end:
            yield "(properties)", 2, end, "\n".join(lines[1:end]).strip()
            body_start = end + 1

    for n, line in enumerate(lines, start=1):
        if n <= body_start:
            continue
        m = HEADING.match(line)
        if m:
            yield from flush(n - 1)
            block, block_start = [], None
            level = len(m.group(1))
            headings = [(lvl, h) for lvl, h in headings if lvl < level]
            headings.append((level, m.group(2).strip()))
            continue
        if not line.strip() or re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", line):
            yield from flush(n - 1)
            block, block_start = [], None
            continue
        if block_start is None:
            block_start = n
        block.append(line)
    yield from flush(n)


def _pdf_units(path):
    try:
        from pypdf import PdfReader
    except ImportError as err:
        raise RuntimeError(
            f"{path.name} is a PDF; install the local parser with `pip install pypdf`") from err
    for i, page in enumerate(PdfReader(str(path)).pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            yield f"page {i}", None, None, text


def chunk_source(path):
    """Pack paragraph blocks into ~CHUNK_TARGET-char passages.

    A passage never crosses a heading, so its section label stays accurate.
    Oversized paragraphs are split on sentence boundaries.
    """
    sid, src = source_id(path), rel(path)
    chunks, cur, cur_label, cur_start, cur_end = [], [], None, None, None

    def emit():
        if cur:
            loc = cur_label
            if cur_start:
                loc += f" (lines {cur_start}-{cur_end})"
            chunks.append({
                "id": f"{sid}#{len(chunks) + 1}",
                "source_id": sid,
                "path": src,
                "section": cur_label,
                "lines": [cur_start, cur_end] if cur_start else None,
                "location": loc,
                "text": "\n\n".join(cur),
            })

    for label, start, end, text in read_units(path):
        if label == "(properties)":
            # File metadata repeats the title words and outranks real content;
            # ingestion still sends it to Gemma, but search doesn't index it.
            continue
        for piece in _split_long(text):
            size = sum(len(c) for c in cur)
            if cur and (label != cur_label or size + len(piece) > config.CHUNK_TARGET):
                emit()
                cur, cur_start = [], None
            if not cur:
                cur_label, cur_start = label, start
            cur.append(piece)
            cur_end = end
    emit()
    return chunks


def _split_long(text):
    if len(text) <= config.CHUNK_MAX:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out, buf = [], ""
    for s in sentences:
        if buf and len(buf) + len(s) > config.CHUNK_TARGET:
            out.append(buf.strip())
            buf = ""
        buf += s + " "
    if buf.strip():
        out.append(buf.strip())
    return out


def full_text(path):
    """Source text as sent to Gemma during ingestion, with section markers."""
    return "\n\n".join(f"[{label}]\n{text}" for label, _, _, text in read_units(path))
