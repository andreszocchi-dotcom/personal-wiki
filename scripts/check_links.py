"""Check every [[link]] in the vault: target exists, is unambiguous, and any
#heading anchor matches a real heading in the target file.

    python scripts/check_links.py      (exit code 1 if anything is broken)
"""

import re
import sys
from collections import Counter
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"
LINK = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|[^\]]*)?\]\]")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)


def norm_heading(h):
    return re.sub(r"\s+", " ", h.replace(":", " ")).strip().lower()


def main():
    files = [p for p in VAULT.rglob("*.md") if ".obsidian" not in p.parts]
    by_path = {p.relative_to(VAULT).with_suffix("").as_posix().lower(): p for p in files}
    stems = Counter(p.stem.lower() for p in files)
    by_stem = {p.stem.lower(): p for p in files}

    problems, checked = [], 0
    for page in files:
        text = page.read_text(encoding="utf-8")
        for target, anchor in LINK.findall(text):
            checked += 1
            # "\|" is Obsidian's escaped alias separator inside tables.
            key = target.strip().rstrip("\\").removesuffix(".md").lower()
            where = page.relative_to(VAULT).as_posix()
            if "/" in key:
                # Obsidian resolves partial paths by suffix, e.g. Source/LinkedIn Profile.
                matches = [p for k, p in by_path.items() if k == key or k.endswith("/" + key)]
                dest = matches[0] if len(matches) == 1 else None
            elif stems[key] > 1:
                problems.append(f"{where}: [[{target}]] is ambiguous ({stems[key]} files share that name)")
                continue
            else:
                dest = by_stem.get(key)
            if dest is None:
                problems.append(f"{where}: [[{target}]] has no target")
                continue
            if anchor and not anchor.startswith("page="):
                headings = {norm_heading(h) for h in HEADING.findall(dest.read_text(encoding="utf-8"))}
                if norm_heading(anchor) not in headings:
                    problems.append(f"{where}: heading '#{anchor}' not found in {dest.relative_to(VAULT).as_posix()}")

    print(f"checked {checked} links in {len(files)} files")
    for p in problems:
        print("  BROKEN", p)
    print("all links resolve" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
