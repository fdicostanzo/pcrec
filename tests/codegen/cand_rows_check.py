#!/usr/bin/env python3
"""tests/codegen/cand_rows_check.py -- the CANDIDATE TABLE's structural checks
(`src/gen/emit_dfa.c`'s `dfa_pfs[]`, the table docs/design/startset.md calls
the one candidate-finding table; D148).

[cand-no-name-strcmp] (K84, startset.md §8 stage 0, review r4 checks-F10)
    No string comparison anywhere under src/ cli/ lib/ reads a `dfa_pfs[]` row
    NAME. Two readers used to classify the selected prefilter row by
    `strcmp(pf->c.name, "memchr")`; a new row with another name then escaped
    G1's dominance and the re-seed price silently. The row's PROPERTY
    (`DfaPf.scan`) is what a reader tests now. A comparison call (strcmp,
    strncmp, strcasecmp, strncasecmp, memcmp) fails the check when either
      (a) one of its arguments is a string literal equal to a row name read
          off the table itself -- except `"none"`, the total-fallback name
          EVERY axis's list ends with and an ordinary word in a dozen
          unrelated comparisons (an encoding list, a stamp fold), so it
          cannot be keyed on by text -- or
      (b) one of its arguments reads `c.name` through a receiver whose name
          (this half covers `"none"`: `strcmp(pf->c.name, "none")` fails here)
          ends in `pf` (`pf->c.name`, `f->pf->c.name`) or through
          `dfa_pf_of(...)`.
    WHAT IT CANNOT SEE: a row name copied into a differently named local and
    compared to another such local (no literal, no `pf` receiver), and a
    name-keyed lookup that is not a comparison call (a hash, a switch on a
    character). It is a name-keyed filter on the RECEIVER half and says so
    (coding_guide §5 item 4); the literal half is keyed on the table's own
    contents, so a new row's name joins it with no edit here.

The row-name population is read off the table's text and must be non-empty
(K35): an empty population would make (a) pass vacuously.

    cand_rows_check.py [TREE]      (default: this script's repo root)
Prints PASS:/FAIL: lines and `checks passed:`/`checks failed:` trailers.
"""
import os, re, sys

TREE = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EMIT = os.path.join(TREE, "src", "gen", "emit_dfa.c")
CMP = re.compile(r"\b(strcmp|strncmp|strcasecmp|strncasecmp|memcmp)\s*\(")

passed = failed = 0


def ok(msg):
    global passed
    passed += 1
    print("PASS: " + msg)


def bad(msg):
    global failed
    failed += 1
    print("FAIL: " + msg)


def table_block(src, decl):
    """The text of `decl ... };`, or None."""
    i = src.find(decl)
    if i < 0:
        return None
    j = src.find("\n};", i)
    return src[i:j] if j > 0 else None


def strip_comments(s):
    """C comments blanked (newlines kept, so line numbers survive)."""
    out, i, n = [], 0, len(s)
    while i < n:
        if s.startswith("/*", i):
            j = s.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", s[i:j]))
            i = j
        elif s.startswith("//", i):
            j = s.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif s[i] == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            out.append(s[i:j + 1])
            i = j + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def call_args(s, open_paren):
    """The text between `(` at open_paren and its matching `)`."""
    depth, i = 0, open_paren
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return s[open_paren + 1:i]
        elif c == '"':
            i += 1
            while i < len(s) and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        i += 1
    return s[open_paren + 1:]


def main():
    try:
        src = open(EMIT).read()
    except OSError as e:
        bad("[cand-no-name-strcmp] cannot read %s: %s" % (EMIT, e))
        return
    block = table_block(src, "static const DfaPf dfa_pfs[] = {")
    names = re.findall(r'\{\s*(?:\.c\s*=\s*)?\{\s*"([^"]+)"', block or "")
    print("REACH: dfa_pfs[] rows read off the table: %d (%s)" % (len(names), ", ".join(names)))
    if not names:
        bad("[cand-no-name-strcmp] no dfa_pfs[] row name found in %s -- the literal half is vacuous" % EMIT)
        return
    lits = {'"%s"' % n for n in names if n != "none"}
    hits, ncalls, nfiles = [], 0, 0
    for root in ("src", "cli", "lib"):
        for d, _sub, files in os.walk(os.path.join(TREE, root)):
            for fn in sorted(files):
                if not fn.endswith((".c", ".h")):
                    continue
                path = os.path.join(d, fn)
                nfiles += 1
                text = strip_comments(open(path, errors="replace").read())
                for m in CMP.finditer(text):
                    ncalls += 1
                    args = call_args(text, m.end() - 1)
                    strs = set(re.findall(r'"(?:[^"\\]|\\.)*"', args))
                    why = sorted(strs & lits)
                    if re.search(r"\w*pf\s*->\s*c\s*\.\s*name|dfa_pf_of\s*\([^;]*\)\s*->\s*c\s*\.\s*name", args):
                        why.append("a pf receiver's c.name")
                    if why:
                        line = text.count("\n", 0, m.start()) + 1
                        hits.append("%s:%d %s(%s) [%s]" % (os.path.relpath(path, TREE), line,
                                    m.group(1), " ".join(args.split())[:80], ", ".join(why)))
    print("REACH: %d comparison call(s) scanned in %d file(s)" % (ncalls, nfiles))
    if ncalls == 0:
        bad("[cand-no-name-strcmp] no comparison call found under src/ cli/ lib/ -- the scan reads nothing")
    elif hits:
        bad("[cand-no-name-strcmp] a comparison reads a dfa_pfs[] row NAME (K84): " + "; ".join(hits))
    else:
        ok("[cand-no-name-strcmp] no comparison call reads any of the %d dfa_pfs[] row names" % len(names))


main()
print("checks passed: %d" % passed)
print("checks failed: %d" % failed)
sys.exit(1 if failed else 0)
