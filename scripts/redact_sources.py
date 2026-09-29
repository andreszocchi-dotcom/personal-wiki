"""One-time import of the Career Wiki sources into vault/raw/, with redaction.

The private originals live outside this repo and are never modified. This
script copies four of them and replaces contact details and coworkers'
names, so the public repo holds shareable text. The redacted copy is the
"original" for this wiki: after import, vault/raw/ is never edited.

Usage:  python scripts/redact_sources.py "<folder with the private originals>"

Coworker names to replace are read from scripts/redactions.local.json, which
is gitignored so the public repo never contains the names it redacts:
    {"names": {"<first name>": "[role]"}}

Every replacement is listed in evidence/redactions.md.
"""

import json
import re
import sys
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "vault" / "raw"
FILES = ["Master Resume.md", "Career Inventory.md",
         "Berkeley Haas Resume Standards.md", "Source/LinkedIn Profile.md"]

RULES = [
    (re.compile(r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"), "[phone redacted]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), "[email redacted]"),
]
LOCAL_TERMS = Path(__file__).with_name("redactions.local.json")
if LOCAL_TERMS.exists():
    for name, role in json.loads(LOCAL_TERMS.read_text(encoding="utf-8"))["names"].items():
        RULES.append((re.compile(rf"\b{re.escape(name)}\b"), role))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    log = ["# Source redactions", "",
           "Applied once by `scripts/redact_sources.py` when importing sources into `vault/raw/`.", "",
           "| File | Line | Replaced with |", "|---|---|---|"]
    for name in FILES:
        text = (src / name).read_text(encoding="utf-8")
        out_lines = []
        for n, line in enumerate(text.split("\n"), start=1):
            for pattern, repl in RULES:
                for _ in pattern.findall(line):
                    log.append(f"| `{name}` | {n} | `{repl}` |")
                line = pattern.sub(repl, line)
            out_lines.append(line)
        dest = DEST / name
        if dest.exists():
            sys.exit(f"{dest} already exists; raw sources are write-once.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(out_lines), encoding="utf-8")
        print(f"imported {name}")
    report = DEST.parent.parent / "evidence" / "redactions.md"
    report.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"{len(log) - 6} replacements logged in {report}")


if __name__ == "__main__":
    main()
