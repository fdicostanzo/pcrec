"""tests/spec_history/spec_cites.py -- the numbered-spec checks.

A spec doc under docs/spec/ that carries the table-of-contents block
(`<!-- spec-toc:begin -->`) has ADOPTED the numbering rule in
docs/spec/CLAUDE.md: its sections and paragraphs carry permanent numbers, and
a number is how the rest of the tree cites it. Three checks over every
adopter:

  numbering  every numbered heading is preceded by its `<a id="sN">` line, no
             number is used twice; every paragraph / list item / block quote
             opens with `<a id="sN-pK"></a>[N¶K]`, the label names its own
             section, labels are unique and run 1..n within a section;
  toc        scripts/spec_toc.py --check: the contents block is current and
             every heading it links has its anchor;
  cites      every `<doc>.md §N` / `§N¶K` / `SN` cited ANYWHERE in the tree
             names a section or paragraph that exists in the doc (retired
             stubs exist); and no `<doc>.md:<line>` citation remains. A
             citation count under the doc's floor (cite_floors.tsv) fails,
             because a scan that reads nothing passes everything (K35);
             cite_exclude.tsv names the few places that are not citations
             (a tool's own grep output, the check's own plants).

Each check is run once over planted text first, so a pattern that stopped
matching fails here instead of passing the tree vacuously.
Python 3 standard library only; reads files, writes nothing.
"""
import os
import re
import subprocess
import sys

import specdoc

BEGIN = "<!-- spec-toc:begin -->"
SKIP_DIRS = {".git", "worktrees", "node_modules", "__pycache__"}


def adopters(specdir):
    """-> {stem: path} for every docs/spec/*.md carrying the TOC block."""
    out = {}
    for f in sorted(os.listdir(specdir)):
        if not f.endswith(".md") or f == "CLAUDE.md":
            continue
        p = os.path.join(specdir, f)
        with open(p, encoding="utf-8") as fh:
            if BEGIN in fh.read():
                out[f[:-3]] = p
    return out


def _cut(items, n=8):
    shown = "; ".join(items[:n])
    return shown + ("; ... (%d more)" % (len(items) - n) if len(items) > n else "")


def check_numbering(name, path):
    """-> [(ok, message)]"""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    d = specdoc.parse(lines)
    res = []
    bad = []
    seen = {}
    for n, level, num, title, prev in d.headings:
        want = '<a id="%s"></a>' % specdoc.anchor_of(num)
        if prev.strip() != want:
            bad.append("%s:%d heading %s lacks %s on the line above" % (name, n, num, want))
        if num in seen:
            bad.append("%s:%d number %s repeats line %d" % (name, n, num, seen[num]))
        seen[num] = n
        if num.count(".") + 1 != level - 1:
            bad.append("%s:%d heading %s is level %d (a number's depth is level-1)"
                       % (name, n, num, level))
    res.append((not bad and len(d.headings) > 0,
                "[numbering] %s: %d numbered headings, anchors and depths consistent"
                % (name, len(d.headings)) if not bad and d.headings else
                "[numbering] %s: heading numbering broken: %s" % (name, _cut(bad) or "no numbered headings")))
    bad = []
    keys = {}
    for n, sec, lm, line in d.units:
        if not lm:
            bad.append("%s:%d unnumbered paragraph in section %s: %.50s" % (name, n, sec, line.strip()))
            continue
        if lm.group("sec") != sec:
            bad.append("%s:%d label [%s¶%s] sits in section %s" % (name, n, lm.group("sec"), lm.group("k"), sec))
        want = specdoc.para_anchor_of(lm.group("sec"), lm.group("k"))
        if lm.group("aid") != want:
            bad.append("%s:%d anchor %s should be %s" % (name, n, lm.group("aid"), want))
        key = (lm.group("sec"), lm.group("k"))
        if key in keys:
            bad.append("%s:%d label [%s¶%s] repeats line %d" % (name, n, key[0], key[1], keys[key]))
        keys[key] = n
    res.append((not bad and len(d.units) > 0,
                "[numbering] %s: all %d paragraphs carry a label naming their own section"
                % (name, len(d.units)) if not bad and d.units else
                "[numbering] %s: paragraph labels broken: %s" % (name, _cut(bad) or "no paragraphs")))
    # order: within one section the labels run 1..n, an inserted one (4a) after its base
    bad = []
    by_sec = {}
    for n, sec, lm, line in d.units:
        if lm and lm.group("sec") == sec:
            by_sec.setdefault(sec, []).append(lm.group("k"))
    for sec, ks in by_sec.items():
        last = (0, "")
        ints = []
        for k in ks:
            m = re.match(r"(\d+)([a-z]?)$", k)
            cur = (int(m.group(1)), m.group(2))
            if cur <= last:
                bad.append("section %s: ¶%s follows ¶%d%s" % (sec, k, last[0], last[1]))
            last = cur
            if not m.group(2):
                ints.append(cur[0])
        if ints != list(range(1, len(ints) + 1)):
            bad.append("section %s: base paragraph numbers are not 1..%d" % (sec, len(ints)))
    res.append((not bad, "[numbering] %s: paragraphs run in order, 1..n per section" % name
                if not bad else "[numbering] %s: paragraph order broken: %s" % (name, _cut(bad))))
    return res


def check_toc(root, name, path):
    r = subprocess.run([sys.executable, "-I", os.path.join(root, "scripts", "spec_toc.py"),
                        "--check", path], capture_output=True, text=True)
    if r.returncode == 0:
        return [(True, "[toc] %s: the table of contents is current" % name)]
    return [(False, "[toc] %s: %s" % (name, " | ".join(r.stderr.strip().split("\n")[:6])))]


# ---- citations -----------------------------------------------------------

NUM = specdoc.NUM
ONE = r"(" + NUM + r")(?:¶(" + specdoc.PARA + r"))?"
SEP = r"[`'\"\)\*\s,:|(—–-]{0,8}?"


def cite_re(stem):
    # "<stem>[.md]" then a few separator characters, then § or S, then a
    # number (and optionally a paragraph); further "§N" items chained by
    # , ; / & and or – — are checked too.
    first = re.escape(stem) + r"(?:\.md)?" + SEP + r"(?:§|S{1,2}(?=\d))" + ONE
    chain = r"(?:[`'\")*]*\s*(?:,|;|/|&|and|or|–|—|-)\s*`?§" + ONE + r")*"
    return re.compile(first + chain)


ITEM = re.compile(r"§" + ONE)


def line_re(stem):
    return re.compile(re.escape(stem) + r"(?:\.md)?:\d")


def cites_in(stem, text):
    """-> [(lineno, section, para_or_None)] for every citation of the doc."""
    rx = cite_re(stem)
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        for m in rx.finditer(line):
            span = m.group(0)
            first = re.search(r"(?:§|S{1,2}(?=\d))" + ONE, span)
            out.append((n, first.group(1), first.group(2)))
            rest = span[first.end():]
            for it in ITEM.finditer(rest):
                out.append((n, it.group(1), it.group(2)))
    return out


def line_cites_in(stem, text):
    rx = line_re(stem)
    return [n for n, line in enumerate(text.split("\n"), 1) if rx.search(line)]


def load_tsv(path, ncols):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                if raw.strip() and not raw.startswith("#"):
                    cols = raw.rstrip("\n").split("\t")
                    if len(cols) < ncols:
                        sys.exit("spec_cites: FATAL: malformed row in %s: %r" % (path, raw))
                    rows.append(cols)
    return rows


def tree_files(root):
    """Tracked files when root is a git work tree's top level, else a walk
    (a mech scratch tree is `git archive` output with no .git)."""
    try:
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True).stdout.strip()
        if top and os.path.realpath(top) == os.path.realpath(root):
            out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True).stdout
            return [f for f in out.decode("utf-8", "replace").split("\0") if f]
    except OSError:
        pass
    files = []
    for dp, dns, fns in os.walk(root):
        top = os.path.realpath(dp) == os.path.realpath(root)
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not (top and d.startswith("build"))]
        for fn in fns:
            files.append(os.path.relpath(os.path.join(dp, fn), root))
    return files


def read_text(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", "replace")


def check_cites(root, name, path, files):
    here = os.path.join(root, "tests", "spec_history")
    excl = load_tsv(os.path.join(here, "cite_exclude.tsv"), 3)
    floors = {r[0]: int(r[1]) for r in load_tsv(os.path.join(here, "cite_floors.tsv"), 2)}
    with open(path, encoding="utf-8") as fh:
        d = specdoc.parse(fh.read().split("\n"))
    res = []

    # controls: the patterns must see what they exist to see
    ok_ctl = (cites_in(name, "x " + name + ".md §3.1.3¶4 y") == [(1, "3.1.3", "4")]
              and cites_in(name, name + ".md `§6.3` and §10.4") == [(1, "6.3", None), (1, "10.4", None)]
              and cites_in(name, "(" + name + ".md S3.1)") == [(1, "3.1", None)]
              and line_cites_in(name, "see " + name + ".md:" + "123") == [1]
              and cites_in(name, "tuning.md §2.5") == [])
    res.append((ok_ctl, "[cites] %s: the citation patterns read planted text correctly (control)" % name))
    probe_bad = [c for c in cites_in(name, name + ".md §99.9 and " + name + ".md §3.1.3¶999")
                 if not ((c[1] in d.sections) and (c[2] is None or (c[1], c[2]) in d.labels))]
    res.append((len(probe_bad) == 2,
                "[cites] %s: a planted dangling section and a planted dangling paragraph are both reported (control)" % name))

    total = 0
    dangling = []
    linecites = []
    for f in files:
        skip_all = any(f.startswith(r[0]) and r[1] in ("all", "cites") for r in excl)
        skip_line = any(f.startswith(r[0]) and r[1] in ("all", "line") for r in excl)
        text = read_text(os.path.join(root, f))
        if text is None or name not in text:
            continue
        if not skip_all:
            for n, sec, para in cites_in(name, text):
                total += 1
                if sec not in d.sections:
                    dangling.append("%s:%d §%s" % (f, n, sec))
                elif para is not None and (sec, para) not in d.labels:
                    dangling.append("%s:%d §%s¶%s" % (f, n, sec, para))
        if not skip_line:
            for n in line_cites_in(name, text):
                linecites.append("%s:%d" % (f, n))
    res.append((not dangling,
                "[cites] %s: all %d citations in the tree name a section or paragraph that exists"
                % (name, total) if not dangling else
                "[cites] %s: dangling citation(s) -- a number never disappears, it becomes a "
                "`— retired` stub: %s" % (name, _cut(dangling))))
    res.append((not linecites,
                "[cites] %s: no line-number citation remains" % name if not linecites else
                "[cites] %s: line-number citation(s) -- cite the section number (%s §N¶K), "
                "never a line: %s" % (name, name + ".md", _cut(linecites))))
    floor = floors.get(name)
    if floor is None:
        res.append((False, "[cites] %s: no row in cite_floors.tsv -- add one (half the measured "
                           "count of %d), so a scan that reads nothing cannot pass" % (name, total)))
    else:
        res.append((total >= floor, "[cites] %s: %d citations scanned, floor %d"
                    % (name, total, floor) if total >= floor else
                    "[cites] %s: only %d citations scanned, floor %d -- the scan stopped "
                    "reaching the tree" % (name, total, floor)))
    return res


def run(root):
    """Print PASS:/FAIL: lines; -> (passed, failed)."""
    specdir = os.path.join(root, "docs", "spec")
    ad = adopters(specdir)
    results = []
    if not ad:
        results.append((False, "[numbering] no docs/spec/*.md carries the %s block -- "
                               "the numbered-spec checks read nothing" % BEGIN))
    files = tree_files(root)
    for name, path in ad.items():
        results += check_numbering(name, path)
        results += check_toc(root, name, path)
        results += check_cites(root, name, path, files)
    passed = failed = 0
    for ok, msg in results:
        print(("PASS: " if ok else "FAIL: ") + msg)
        if ok:
            passed += 1
        else:
            failed += 1
    return passed, failed
