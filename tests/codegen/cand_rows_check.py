#!/usr/bin/env python3
"""tests/codegen/cand_rows_check.py -- the START TABLE's structural checks
(`src/gen/emit_dfa.c`'s `cand_rows[]`, docs/design/start_table.md; until
[START-TABLE] C3 the candidate table `dfa_pfs[]`, D148).

[cand-no-name-strcmp] (K84, startset.md §8 stage 0, review r4 checks-F10;
re-aimed at C3, start_table.md §3.5)
    No string comparison anywhere under src/ cli/ lib/ reads the NAME of a
    row of the slots `cand_rows[]` decides since C3 (NEXT, the old
    `dfa_pfs[]`, and RECOVER, the old `dfa_search_starts[]`) and since C4
    (PRESENCE, the old `req_admits[]`, and FIRST, the old `req_uses[]`;
    their readers test `u.admit.verdict`/`u.use.use`). Two readers
    used to classify the selected prefilter row by
    `strcmp(pf->c.name, "memchr")`; a new row with another name then escaped
    G1's dominance and the re-seed price silently. The row's PROPERTY
    (`CandRow.u.pf.scan`, `u.recover.pinned`) is what a reader tests now. A
    comparison call (strcmp, strncmp, strcasecmp, strncasecmp, memcmp) fails
    the check when either
      (a) one of its arguments is a string literal equal to one of those
          rows' identities or spellings (`c.name`, `tok`), read off the table
          itself -- except `"none"`, the total-fallback name EVERY axis's
          list ends with and an ordinary word in a dozen unrelated
          comparisons (an encoding list, a stamp fold), so it cannot be
          keyed on by text -- or
      (b) one of its arguments reads `c.name` or `tok` through a receiver
          whose name ends in `pf` (`pf->c.name`, `f->pf->tok`; this half
          covers `"none"`) or through one of the selection functions
          (`dfa_pf_of(...)`, `vm_start_row`, `attempt_next_of`,
          `dfa_search_start_of`, `cand_select`).
    The other slots' rows join the population as C5 moves their readers
    onto the table (their names are still read off their old tables' own
    spellings until then, and several -- `all`, `exact`, `window`,
    `fixed` -- are ordinary words; §3.5's row-name-expression rule is the
    shape that widening takes).
    WHAT IT CANNOT SEE: a row name copied into a differently named local and
    compared to another such local (no literal, no `pf` receiver), and a
    name-keyed lookup that is not a comparison call (a hash, a switch on a
    character). It is a name-keyed filter on the RECEIVER half and says so
    (coding_guide §5 item 4); the literal half is keyed on the table's own
    contents, so a new row's name joins it with no edit here.

[cand-route-init] (stage 1, review r4 checks-F6)
    Every `CandSel NAME = { ... };` initializer under src/ names `.route`
    (`CandSel` is the type since C2 and the only spelling since C4, D148
    Q2's sweep; the pattern still accepts the retired `DfaSel`).
    The selection value gained a route whose zero value is the legacy DFA
    route; an initializer that omits it compiles silently (a designated
    initializer zero-fills), so the omission is caught here instead. The
    population is counted and must be non-empty (K35). WHAT IT CANNOT SEE: a
    `CandSel` built by assignment after declaration, or copied from another.

[cand-route-walk] (stage 1, checks-F6; re-aimed at C3)
    `cand_select`'s body tests the row's route mask (`CAND_ON(s->route)`)
    BEFORE it calls `.applies(`: the route mask is data the walk tests, so a
    VM-route selection never reaches a predicate that reads a machine. (Until
    C3 the walk was `dfa_select` and the test `cand_routed(`.)

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
    block = table_block(src, "static const CandRow cand_rows[] = {")
    names = []
    for row in re.split(r"\n    \{ ", block or "")[1:]:
        if not re.search(r"\.slot\s*=\s*CAND_SLOT_(?:NEXT|RECOVER|PRESENCE|FIRST)\b", row):
            continue
        names += re.findall(r'\.c\s*=\s*\{\s*"([^"]+)"', row)
        names += re.findall(r'\.tok\s*=\s*"([^"]+)"', row)
    names = sorted(set(names))
    print("REACH: cand_rows[] NEXT/RECOVER/PRESENCE/FIRST row names read off the table: %d (%s)" % (len(names), ", ".join(names)))
    if not names:
        bad("[cand-no-name-strcmp] no cand_rows[] NEXT/RECOVER/PRESENCE/FIRST row name found in %s -- the literal half is vacuous" % EMIT)
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
                    if re.search(r"\w*pf\s*->\s*(?:c\s*\.\s*name|tok)\b|"
                                 r"(?:dfa_pf_of|vm_start_row|attempt_next_of|dfa_search_start_of|cand_select)"
                                 r"\s*\([^;]*\)\s*->\s*(?:c\s*\.\s*name|tok)\b", args):
                        why.append("a selected row's c.name/tok")
                    if why:
                        line = text.count("\n", 0, m.start()) + 1
                        hits.append("%s:%d %s(%s) [%s]" % (os.path.relpath(path, TREE), line,
                                    m.group(1), " ".join(args.split())[:80], ", ".join(why)))
    print("REACH: %d comparison call(s) scanned in %d file(s)" % (ncalls, nfiles))
    if ncalls == 0:
        bad("[cand-no-name-strcmp] no comparison call found under src/ cli/ lib/ -- the scan reads nothing")
    elif hits:
        bad("[cand-no-name-strcmp] a comparison reads a cand_rows[] NEXT/RECOVER/PRESENCE/FIRST row NAME (K84): " + "; ".join(hits))
    else:
        ok("[cand-no-name-strcmp] no comparison call reads any of the %d cand_rows[] NEXT/RECOVER/PRESENCE/FIRST row names" % len(names))


def route_checks():
    files = []
    for root in ("src", "cli", "lib"):
        for d, _sub, fs in os.walk(os.path.join(TREE, root)):
            files += [os.path.join(d, f) for f in sorted(fs) if f.endswith((".c", ".h"))]
    n, missing = 0, []
    for path in files:
        text = strip_comments(open(path, errors="replace").read())
        for m in re.finditer(r"\b(?:DfaSel|CandSel)\s+\w+\s*=\s*\{", text):
            n += 1
            body = text[m.end():text.find("};", m.end())]
            if not re.search(r"\.route\s*=", body):
                missing.append("%s:%d" % (os.path.relpath(path, TREE), text.count("\n", 0, m.start()) + 1))
    print("REACH: %d DfaSel/CandSel initializer(s) under src/ cli/ lib/" % n)
    if n == 0:
        bad("[cand-route-init] no DfaSel/CandSel initializer found -- the check reads nothing")
    elif missing:
        bad("[cand-route-init] a DfaSel/CandSel initializer omits .route: " + ", ".join(missing))
    else:
        ok("[cand-route-init] all %d DfaSel/CandSel initializers name .route" % n)
    src = strip_comments(open(EMIT).read())
    m = re.search(r"static const CandRow \*cand_select\(CandSlot slot,[^)]*\)\s*\{", src)
    body = src[m.end():src.find("\n}", m.end())] if m else ""
    r, a = body.find("CAND_ON(s->route)"), body.find(".applies(")
    if not body or a < 0:
        bad("[cand-route-walk] cand_select's body or its applies call not found in %s" % EMIT)
    elif r < 0 or r > a:
        bad("[cand-route-walk] cand_select does not test the route mask (CAND_ON(s->route)) before applies")
    else:
        ok("[cand-route-walk] cand_select tests the row's route mask before its applies")


main()
route_checks()
print("checks passed: %d" % passed)
print("checks failed: %d" % failed)
sys.exit(1 if failed else 0)
