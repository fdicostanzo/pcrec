#!/usr/bin/env python3
"""tests/spec_history/spec_history.py -- flags BUILD HISTORY in docs/spec/*.md.

docs/spec/CLAUDE.md: a spec states the contract and carries no build history
(rulings, panels, walkbacks, dated revision notes live in docs/design/,
docs/dev/ and docs/dev/history/). This check makes that rule mechanical.

Each MARKER below is a textual shape that history takes in this tree. A hit is
OK when allowlist.tsv names it (file, marker, a substring of the line, and why
the use is not history), and otherwise counts against the file. A file named in
baseline.tsv carries KNOWN DEBT: its per-marker count must EQUAL the baseline
(more is new history; fewer means debt was paid and the baseline must be
lowered in the same change). A file not in baseline.tsv must have zero
unallowed hits.

  spec_history.py ROOT            check; prints PASS:/FAIL: lines and the
                                  `checks passed:`/`checks failed:` totals
  spec_history.py ROOT --survey   the per-file density table (no verdict)
  spec_history.py ROOT --lines F  every unallowed hit in file F, by marker

Python 3 standard library only; reads files, writes nothing.
"""
import os
import re
import sys

# (id, description, compiled regex). A regex is matched per LINE; fenced code
# blocks are skipped (emitted text quoted verbatim may carry tags and dates).
MARKERS = [
    ("date", "an ISO date (a dated revision or row note)",
     re.compile(r"\b20\d\d-\d\d-\d\d\b")),
    ("addendum", "ADDENDUM, or 'addendum' not naming a decision (Dnn addendum)",
     None),  # handled by addendum_hits()
    ("walkback", "walkback/revision phrasing (used to, no longer, now reads, "
                 "corrected, superseded, formerly, this revision, since [TAG], ...)",
     re.compile(r"\b(used to|no longer|now reads|corrected|superseded|formerly|"
                r"previously|this revision|before this date|re-quoted|"
                r"walk(?:ed)? back)\b|\b(until|since) \[[A-Z]|"
                r"\bsince `?abi`? ?\d", re.I)),
    ("narrative", "panel/ruling/lane narrative (panel, critic, RULED, ruling, "
                  "lane X, Frank)",
     re.compile(r"\b(panel|critics?|RULED|ruling|Frank)\b|\blane `?[a-z][a-z0-9]+`?\b")),
    ("tagopen", "a paragraph or heading OPENING with a [ROW-TAG] (a revision note)",
     re.compile(r"^\s*(#+\s.*?|\*\*|- \*\*)\[[A-Z][A-Z0-9.]*(-[A-Z0-9.]+)*\]")),
]
MARKER_IDS = [m[0] for m in MARKERS]
ADD_RE = re.compile(r"addendum", re.I)
DECISION_BEFORE = re.compile(r"\bD\d+(\.\d+)?('s)?\s*$")


def addendum_hits(line):
    for m in ADD_RE.finditer(line):
        if m.group(0) == "ADDENDUM":
            return True
        if not DECISION_BEFORE.search(line[: m.start()]):
            return True
    return False


def scan(path):
    """-> list of (lineno, marker, line) for every marker hit, code fences skipped."""
    hits = []
    fence = False
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            for mid, _, rx in MARKERS:
                hit = addendum_hits(line) if mid == "addendum" else bool(rx.search(line))
                if hit:
                    hits.append((n, mid, line.rstrip("\n")))
    return hits


def load_tsv(path, ncols):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            if not raw.strip() or raw.startswith("#"):
                continue
            cols = raw.rstrip("\n").split("\t")
            if len(cols) < ncols:
                sys.exit("spec_history: FATAL: malformed row in %s: %r" % (path, raw))
            rows.append(cols)
    return rows


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    root = argv[1]
    here = os.path.join(root, "tests", "spec_history")
    specdir = os.path.join(root, "docs", "spec")
    files = sorted(f for f in os.listdir(specdir) if f.endswith(".md") and f != "CLAUDE.md")
    if not files:
        sys.exit("spec_history: FATAL: no docs/spec/*.md found under %s" % root)
    allow = load_tsv(os.path.join(here, "allowlist.tsv"), 4)
    base = {}
    for f, mid, cnt in load_tsv(os.path.join(here, "baseline.tsv"), 3):
        if mid not in MARKER_IDS:
            sys.exit("spec_history: FATAL: baseline names unknown marker %r" % mid)
        base[(f, mid)] = int(cnt)
    for f, mid, sub, _why in allow:
        if mid not in MARKER_IDS:
            sys.exit("spec_history: FATAL: allowlist names unknown marker %r" % mid)

    def unallowed(fname, hits):
        out = []
        for n, mid, line in hits:
            if any(a[0] == fname and a[1] == mid and a[2] in line for a in allow):
                continue
            out.append((n, mid, line))
        return out

    per = {}
    for f in files:
        per[f] = unallowed(f, scan(os.path.join(specdir, f)))

    if "--survey" in argv:
        print("| file | lines | " + " | ".join(MARKER_IDS) + " | total | per 1k lines |")
        print("|---|---|" + "---|" * (len(MARKER_IDS) + 2))
        for f in files:
            nlines = sum(1 for _ in open(os.path.join(specdir, f), encoding="utf-8"))
            counts = [sum(1 for h in per[f] if h[1] == m) for m in MARKER_IDS]
            tot = sum(counts)
            print("| %s | %d | %s | %d | %.1f |" % (
                f, nlines, " | ".join(str(c) for c in counts), tot, 1000.0 * tot / max(nlines, 1)))
        return 0
    if "--lines" in argv:
        f = argv[argv.index("--lines") + 1]
        for n, mid, line in per[f]:
            print("%s:%d: [%s] %s" % (f, n, mid, line.strip()[:160]))
        return 0

    passed = failed = 0
    for f in files:
        for mid in MARKER_IDS:
            got = sum(1 for h in per[f] if h[1] == mid)
            want = base.get((f, mid), 0)
            if got == want:
                passed += 1
                tag = "known debt" if want else "clean"
                print("PASS: %s [%s] %d (%s)" % (f, mid, got, tag))
            else:
                failed += 1
                if got > want:
                    print("FAIL: %s [%s] %d history marker(s), baseline %d -- docs/spec "
                          "carries no build history (docs/spec/CLAUDE.md); move it to "
                          "docs/dev/history/ or allowlist a non-history use in "
                          "tests/spec_history/allowlist.tsv. Run with --lines %s." % (
                              f, mid, got, want, f))
                else:
                    print("FAIL: %s [%s] %d, baseline %d -- debt was paid: lower "
                          "tests/spec_history/baseline.tsv to %d in this change." % (
                              f, mid, got, want, got))
    for (f, mid) in base:
        if f not in files:
            failed += 1
            print("FAIL: baseline names %s, which is not in docs/spec/ -- remove its rows" % f)
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
