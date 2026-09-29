"""The retrieval tool: BM25 keyword search over original-source passages.

It only finds evidence; it never generates text and never needs the model,
so `wiki search` works even when Ollama is stopped. The index is the
passage file data/chunks.jsonl (outside the vault), rebuilt by ingest.
"""

import json
import math
import re
from collections import Counter

from . import config

STOPWORDS = set("""
a about above after again all am an and any are as at be because been before
being below between both but by can could did do does doing down during each
few for from further had has have having he her here hers him his how i if in
into is it its itself just me more most my myself no nor not now of off on
once only or other our ours out over own same she should so some such than
that the their them then there these they this those through to too under
until up very was we were what when where which while who whom why will with
would you your yours tell please know
""".split())

K1, B = 1.5, 0.75


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


def _stem(w):
    """Tiny suffix stripper so 'trains', 'training' and 'trained' meet."""
    for suf in ("ingly", "edly", "ing", "ies", "ied", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)] + ("y" if suf in ("ies", "ied") else "")
    return w


def load_chunks():
    if not config.CHUNKS.exists():
        return []
    with open(config.CHUNKS, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def save_chunks(chunks):
    config.DATA.mkdir(parents=True, exist_ok=True)
    with open(config.CHUNKS, "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")


def search(query, k=None, chunks=None):
    """Return the top-k passages as dicts with a 'score' and matched 'terms'.

    Section headings are indexed with the passage text so a question that
    names a section topic still finds it when the body uses other words.
    """
    k = k or config.TOP_K
    chunks = load_chunks() if chunks is None else chunks
    q_terms = list(dict.fromkeys(tokenize(query)))
    if not chunks or not q_terms:
        return []

    docs = [tokenize(f"{c['section']} {c['text']}") for c in chunks]
    avg_len = sum(len(d) for d in docs) / len(docs)
    df = Counter(t for d in docs for t in set(d))
    n = len(docs)

    results = []
    for chunk, doc in zip(chunks, docs):
        tf = Counter(doc)
        score, matched = 0.0, []
        for t in q_terms:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf[t] * (K1 + 1) / (tf[t] + K1 * (1 - B + B * len(doc) / avg_len))
            matched.append(t)
        if score > 0:
            results.append({**chunk, "score": round(score, 3), "terms": matched})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:k]


def format_passages(passages):
    """Label passages S1..Sn for a prompt, keeping path and location visible."""
    return "\n\n".join(
        f"[S{i}] source: {p['path']} | {p['location']}\n{p['text']}"
        for i, p in enumerate(passages, start=1))
