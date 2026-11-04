#!/usr/bin/env python3
"""tests/memfn/decider_census.py -- THE DECIDER CENSUS (span_pick.md rev 5.2
§The tables, "The decider census"; Goal 3's check, written by unit 1a).

  decider_census.py --root ROOT [--src DIR] [--map TSV] [--no-plants]

Holds tests/memfn/decider_census.tsv, the DECLARED map of every kit function
(or part, or data definition) that decides a "find the span" question to its
question table or named exception, against the kit's sources:

  A  every member exists: a `fn` member is a top-level definition WITH A BODY
     of that name in its file (a prototype is not one), a `data` member a
     top-level definition; a `part` is its function's definition holding
     the part's anchor; an `excluded` member names a definition or prototype
     that exists.
  B  THE BACKSTOP: a grep of memfn/src/*.{c,h,def} for the decider shapes
     (BACKSTOP below) is RED on any hit line that lies in no listed member
     (excluded members included). The hits are COUNTED (K35): fewer than
     HIT_FLOOR is red, so a grep that silently read nothing cannot pass.
  C  THE PLANTS (the check's failing direction; skipped by --no-plants):
     two byte-identical copies of a member's decider loop, each pasted into
     an UNLISTED function of a scratch copy of the sources -- run_member's
     loop (window.c) and kit_pres_picks' run-scan loop (presence.c's
     `c < sm`) -- must each turn B red.

Independent control: the map is hand-written (a declaration), the backstop is
a grep over the raw text and the definition finder a brace count over the
comment- and string-stripped text; neither reads the map to find a hit. What
it cannot see: a decider spelled in no BACKSTOP shape (the list is a NAME-
style filter, coding.md §5 item 4) -- members are added by declaration, the
backstop only catches new copies of the shapes the members use.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

# The backstop shapes (span_pick.md rev 5.2 §The tables, the census).
BACKSTOP = ["kit_walk(", "< best", "< bm", "< lo", "< sm", "< wl", "> c)",
            "tie_takes", "TIE_", "< inc"]
# K35: hits at unit 1a's base (main 564db08c5) were 36 lines; a later unit
# that removes decider copies lowers this in the same change.
HIT_FLOOR = 30
# EXACT, like row_floors.tsv's ROWS_FLOOR (a floor with slack lets rows vanish
# silently): a unit that moves a decider edits the map AND this number.
MEMBER_COUNT = 50

passed = failed = 0


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    print("FAIL: " + msg)


def strip_c(text):
    """The text with comments and string/char literals blanked (newlines
    kept), so braces and names inside them count for nothing."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
            i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + re.sub(r"[^\n]", " ", text[i + 1:j - 1]) + (c if j - 1 > i else ""))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def definitions(text):
    """Top-level items of a C file: (name, first line, last line, has_body),
    1-based (has_body: a `{` in the item, so a prototype has none).
    An item starts at a column-0 code line at brace depth 0 (not a
    preprocessor line) and ends at the line where depth is back at 0 and a
    `;` or `}` closes it, or a `)` the next line does not open a body after
    (a top-level macro call: finder.c's `FD_CT(...)` rows). Its name: a
    function's identifier before its first `(`; else the last identifier of
    its depth-0 text before the first `=` or `;`, subscripts dropped (a data
    definition, or a typedef's name)."""
    lines = strip_c(text).split("\n")
    items, depth, start, buf = [], 0, None, []
    for no, ln in enumerate(lines, 1):
        if start is None:
            if depth == 0 and ln[:1] not in ("", " ", "\t", "#", "}", "{"):
                start, buf = no, []
            else:
                depth += ln.count("{") - ln.count("}")
                continue
        buf.append(ln)
        depth += ln.count("{") - ln.count("}")
        nxt = lines[no] if no < len(lines) else ""
        if depth == 0 and (";" in ln or "}" in ln or
                           (ln.rstrip().endswith(")") and not nxt.startswith("{"))):
            text = "\n".join(buf)
            items.append((item_name(text), start, no, "{" in text))
            start = None
    return items


def item_name(src):
    flat, d = [], 0
    for ch in src:                       # the depth-0 text
        if ch == "{":
            d += 1
        elif ch == "}":
            d -= 1
        elif d == 0:
            flat.append(ch)
    flat = "".join(flat)
    head = re.split(r"[=;]", flat, maxsplit=1)[0]
    m = re.search(r"([A-Za-z_]\w*)\s*\(", head)
    if m:
        return m.group(1)
    m = re.findall(r"[A-Za-z_]\w*", re.sub(r"\[[^\]]*\]", "", head))
    return m[-1] if m else None


def read_map(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("#") or not ln.strip():
                continue
            f = ln.rstrip("\n").split("\t")
            if len(f) != 6:
                bad("map line has %d columns, not 6: %r" % (len(f), ln))
                continue
            rows.append(dict(zip(("file", "member", "kind", "anchor", "answers", "retires"), f)))
    return rows


def census(src, rows, count=True):
    """Checks A and B over the sources in `src`; returns (hits, stray lines,
    check-A error messages)."""
    errs = []
    defs, raw = {}, {}
    for fn in sorted(os.listdir(src)):
        if fn.endswith((".c", ".h", ".def")):
            with open(os.path.join(src, fn)) as fh:
                raw[fn] = fh.read()
            defs[fn] = definitions(raw[fn])
    # A: every member exists; its line span
    spans = []
    for r in rows:
        name, _, part = r["member"].partition(":")
        hit = [d for d in defs.get(r["file"], []) if d[0] == name]
        if r["kind"] in ("fn", "part"):
            hit = [d for d in hit if d[3]]       # a prototype is not the decider
        if not hit:
            errs.append("%s: member %s is not defined there (with a body, for fn/part)" % (r["file"], r["member"]))
            continue
        if r["kind"] == "part":
            body = "\n".join(raw[r["file"]].split("\n")[hit[0][1] - 1:hit[0][2]])
            if r["anchor"] == "-" or r["anchor"] not in body:
                errs.append("%s: part %s's anchor %r is not inside %s" % (r["file"], r["member"], r["anchor"], name))
                continue
        elif r["kind"] not in ("fn", "data", "excluded"):
            errs.append("%s: member %s has kind %r" % (r["file"], r["member"], r["kind"]))
            continue
        if count:
            ok()
        spans += [(r["file"], d[1], d[2]) for d in hit]
    # B: every backstop hit lies in a member
    hits, stray = 0, []
    for fn, text in raw.items():
        for no, ln in enumerate(text.split("\n"), 1):
            if any(p in ln for p in BACKSTOP):
                hits += 1
                if not any(f == fn and a <= no <= b for f, a, b in spans):
                    stray.append("%s:%d: %s" % (fn, no, ln.strip()))
    return hits, stray, errs


def plant(src, tmp, fname, anchor, opener):
    """A scratch copy of `src` whose `fname` gains an unlisted function
    holding a byte-identical copy of the loop that opens with `opener` and
    holds `anchor` (the loop's text up to its closing brace at its own
    indentation)."""
    shutil.copytree(src, tmp)
    path = os.path.join(tmp, fname)
    with open(path) as fh:
        lines = fh.read().split("\n")
    at = next((i for i, ln in enumerate(lines) if anchor in ln), None)
    if at is None:
        return None, "anchor %r is not in %s (respelled? re-aim the plant)" % (anchor, fname)
    tops = [i for i in range(at + 1) if lines[i].lstrip().startswith(opener)]
    if not tops:
        return None, "no %r opener at or above the anchor in %s" % (opener, fname)
    top = max(tops)
    ind = len(lines[top]) - len(lines[top].lstrip())
    end = next((i for i in range(top + 1, len(lines))
                if lines[i].startswith(" " * ind + "}") and len(lines[i]) - len(lines[i].lstrip()) == ind), None)
    if end is None:
        return None, "the loop opened at %s:%d has no closing brace" % (fname, top + 1)
    loop = lines[top:end + 1]
    with open(path, "a") as fh:
        fh.write("\nstatic void census_plant(void)\n{\n" + "\n".join(loop) + "\n}\n")
    return len(loop), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--src", help="the kit source dir (default ROOT/memfn/src)")
    ap.add_argument("--map", help="the census map (default ROOT/tests/memfn/decider_census.tsv)")
    ap.add_argument("--no-plants", action="store_true")
    a = ap.parse_args()
    src = a.src or os.path.join(a.root, "memfn/src")
    rows = read_map(a.map or os.path.join(a.root, "tests/memfn/decider_census.tsv"))
    (ok() if len(rows) == MEMBER_COUNT else
     bad("the map holds %d members, not MEMBER_COUNT %d (edit both together)" % (len(rows), MEMBER_COUNT)))
    hits, stray, errs = census(src, rows)
    for e in errs:
        bad(e)
    print("backstop hits: %d (floor %d), outside a member: %d" % (hits, HIT_FLOOR, len(stray)))
    (ok() if hits >= HIT_FLOOR else bad("backstop hits %d under HIT_FLOOR %d" % (hits, HIT_FLOOR)))
    for s in stray:
        bad("a decider shape outside every census member: " + s)
    if not stray:
        ok()
    if not a.no_plants:
        for fname, anchor, opener in (("window.c", "ms < bm ||", "for ("),
                                      ("presence.c", "c < sm", "for (")):
            with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
                n, why = plant(src, os.path.join(t, "src"), fname, anchor, opener)
                if why:
                    bad("plant %s: %s" % (fname, why))
                    continue
                _, pst, _ = census(os.path.join(t, "src"), rows, count=False)
                planted = [s for s in pst if s.startswith(fname + ":")]
                (ok() if planted else
                 bad("plant %s (%d lines, `%s`) did not turn the backstop red" % (fname, n, anchor)))
                print("plant %s `%s`: %d stray hit(s)" % (fname, anchor, len(planted)))
        # C3: a decider reduced to a bare prototype must turn A red.
        fn_row = next(r for r in rows if r["kind"] == "fn")
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
            shutil.copytree(src, os.path.join(t, "src"))
            path = os.path.join(t, "src", fn_row["file"])
            with open(path) as fh:
                text = fh.read()
            item = next((d for d in definitions(text) if d[0] == fn_row["member"] and d[3]), None)
            if item is None:
                bad("plant prototype: %s not found as a definition" % fn_row["member"])
            else:
                lines = text.split("\n")
                lines[item[1] - 1:item[2]] = ["static void %s(void);" % fn_row["member"]]
                with open(path, "w") as fh:
                    fh.write("\n".join(lines))
                _, _, perr = census(os.path.join(t, "src"), rows, count=False)
                hit = [e for e in perr if fn_row["member"] in e]
                (ok() if hit else bad("plant prototype: %s as a bare prototype kept its row green" % fn_row["member"]))
                print("plant prototype %s: %d error(s)" % (fn_row["member"], len(hit)))
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
