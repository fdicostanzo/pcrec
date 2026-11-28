#!/usr/bin/env python3
"""predarg census: every printed program of the three BASE documents (core.md, library.md, parked.md, at the
lane's start commit 88cda0d38) whose condition or group question reads a label through a macro's name, a call's
label, or into an argument, classed by ROUTE, with its verdict today and under the candidate rule
"a path never goes through an argument's place ... or where the body passes them on by an export list, in which
case they count as the body's own labels", under two readings of the carve-out:

  NOW    the in-force walker WALK1127 (lane predfold1127's model, loaded unchanged by load.py) with the two rulings
         the documents do not carry yet applied: body-own-name (READ1127 "direct" = "wins": a path that skips nothing
         reads the label directly under its last step) and array-gate ("array" = "error", the model's default).
  CAND-A the candidate, the carve-out read as a DOOR: a spot whose chain from the start passes an argument's place
         is dropped unless that place sits directly under an export list `[(=) = x]`; the list's alias and the
         argument's place stay steps between (the model's own counting, so a read through a list still "skips").
  CAND-B the candidate, the carve-out read literally as "they count as the body's own labels": as CAND-A, and the
         list, the listed place and the argument's binding used there are NOT steps (the listed labels sit directly
         under the call, as a label the body writes does).

Routes (the brief's): (1) through a label the body writes on the argument's place, or a place used alone;
(2) through an export list on the place; (3) the sender's own names (the shorthand `A.h`, a label the caller writes
in the argument, a sent label, a group of an in-place argument read bare); "own" the body's own label (no place
crossed); "mixed" a read whose candidate spots cross differently (each listed).
Prints; asserts nothing. Run: timeout 600 python3 -I -B census.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402

NS = load.NS
BASE = ("core.md", "library.md", "parked.md")
GQ = ("some", "every", "count", "none", "all", "occurs")
BIND = re.compile(r"([\w.]+(?:\([\w, =:]*\))?) := `([^`]*)`")


def programs():
    """(file, line no, kind, program, binds) of every program printed on a three-mode or compile-error line."""
    out = []
    for f in BASE:
        for ln, line in enumerate(NS["NOWS"][f].split("\n"), 1):
            three = "WHOLE " in line and " / FIND-ALL " in line
            err = "modes: a compile error (`" in line
            if not (three or err):
                continue
            binds = ["%s := %s" % b for b in BIND.findall(line)]
            snippets = re.findall(r"`([^`]*)`", line)
            first = True
            if three:
                a = NS["answer_part"](line)
                tail = line[line.index(a) + len(a):] if a else line
                snippets = re.findall(r"`([^`]*)`", tail)
            for s in snippets:
                if ":=" in s or not re.search(r"\(\s*[@A-Za-z_][\w.]*\s*:|\b(%s)\(\s*@" % "|".join(GQ), s):
                    continue
                if s.startswith("(") and NS["TR11"]._group_end(s, 0) == len(s):
                    continue                                 # a bare condition, no program
                if any(s == b.split(" := ", 1)[1] for b in binds):
                    continue
                kind = ("three-mode" if first else "three-mode line, a further program") if three else "compile error"
                first = False
                out.append((f, ln, kind, s, binds))
    return out


def macro_names(binds):
    m = set(NS["LIBMACROS"])
    m |= {"when", "occurrences", "list_of", "repeat", "pair", "identity"}
    for b in binds:
        mm = re.match(r"\s*([A-Za-z_][\w.]*)\(", b)
        if mm:
            m.add(mm.group(1))
    return m


def call_spans(text, macros):
    """(name, start, end of the argument text) of every call of a macro in text."""
    out = []
    for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", text):
        if mm.group(1) in macros:
            k = NS["TR11"]._group_end(text, mm.end() - 1)
            out.append((mm.group(1), mm.end(), k - 1))
    return out


def in_args(text, pos, spans):
    return any(a <= pos < b for _, a, b in spans)


def sender_kind(text, name, spans, binds):
    """route (3)'s kinds: how the caller's own text names `name` inside an argument, or None."""
    plain = set(re.match(r"\s*(\w+) :=", b).group(1) for b in binds if re.match(r"\s*\w+ :=", b))
    for _, a, b in spans:
        arg = text[a:b]
        if re.search(r"(?<![\w.(])%s:\s*[,)]" % re.escape(name), arg + ")"):
            return "a sent label"
        if re.search(r"\[\s*%s\s*=" % re.escape(name), arg):
            return "a label the caller writes in the argument"
        if re.search(r"\(\?<:?%s>" % re.escape(name), arg):
            return "a group of an in-place argument"
        for x, y in NS["split_top_commas"](text, a, b):
            if text[x:y].strip() == name and name in plain:
                return "the shorthand (the argument's own name)"
    return None


def chains(P, path):
    """every spot the names of `path` can mean from its starts, walls and gates included: [(target, chain)]."""
    nodes = list(NS["_subtree"](P.root))
    starts = [n for n in nodes if NS["_named"](n) == path[0] and NS["context"](n, P.root) == "inside" and NS["kind_of"](n)]
    cur = [(s, [s]) for s in starts]
    for x in path[1:]:
        nxt = []
        for node, ch in cur:
            for t, betw, gates, walls, c in ORIG_BETWEEN(node, x, P):
                nxt.append((t, ch + c[1:]))
        cur = nxt
    return [(t, c) for t, c in cur if t.k in ("label", "grp")]


def route_of(chain):
    args = [n for n in chain[1:] if n.k == "arg"]
    if not args:
        return "own" if any(n.k == "call" for n in chain) else "no call"
    return "2" if all(n.parent is not None and n.parent.k == "list" for n in args) else "1"


ORIG_BETWEEN = NS["_between"]
MODE = ["now"]


def between_c(start, x, P):
    out = ORIG_BETWEEN(start, x, P)
    if MODE[0] == "now":
        return out
    res = []
    for node, betw, gates, walls, chain in out:
        crossed = [n for n in chain[1:] if n.k == "arg"]
        if any(n.parent is None or n.parent.k != "list" for n in crossed):
            continue                                         # the candidate: no path through an argument's place
        if MODE[0] == "B":
            listed = set()
            for n in crossed:
                listed |= {id(n), id(n.parent)}
                for k in n.kids:
                    if k.k in ("use", "call"):
                        listed.add(id(k))
            betw = [n for n in betw if id(n) not in listed]
            gates = [n for n in gates if id(n) not in listed]
        res.append((node, betw, gates, walls, chain))
    return res


NS["_between"] = between_c


def verdict(e, binds, read, mode, array):
    MODE[0] = mode
    try:
        v = NS["walk_v27"](e, binds, read, reading={"direct": "wins"}, array=array)
    finally:
        MODE[0] = "now"
    if v[0] == "legal":
        return "legal (%s%s)" % (v[3], "" if v[1] is None else ", %s's %s" % (v[1], v[2]))
    if v[0] == "refused":
        return "ERROR: " + v[1][:150]
    return "unparsed: " + v[1][:60]


def main():
    progs = programs()
    rows, seen = [], set()
    for f, ln, kind, e, binds in progs:
        macros = macro_names(binds)
        spans = call_spans(e, macros)
        plain_bodies = [b.split(" := ", 1)[1] for b in binds if re.match(r"\s*\w+ :=", b)]
        if not spans and not any(call_spans(t, macros) for t in plain_bodies):
            continue
        for path, a, _ in NS["reads_of"](e):
            array = a > 0 and e[a - 1] == "@"
            rd = ".".join(path)
            if in_args(e, a, spans) and re.match(r"\s*:\s*[,)]", e[a + len(rd):]):
                continue                                     # a marked argument `x:` at a call, no read
            key = (f, ln, e, rd)
            if key in seen:
                continue
            seen.add(key)
            sk = sender_kind(e, path[0], spans, binds)
            route, detail = None, ""
            try:
                ew, bw, _ = NS["prep1127"](e, binds)
                P = NS["Prog1127"](ew, bw)
                chs = chains(P, path)
            except Exception as x:                           # noqa: BLE001
                P, chs = None, None
                detail = "the walker does not parse it (%s)" % str(x)[:50]
            if chs:
                rs = sorted(set(route_of(c) for _, c in chs))
                rs = [r for r in rs if r != "no call"] or rs
                route = rs[0] if len(rs) == 1 else "mixed " + "+".join(rs)
            if route in (None, "no call") and sk:
                route, detail = "3", sk + (" (by text)" if not chs else "")
            if route in (None, "no call"):
                if len(path) == 1:
                    continue                                 # a bare read of the reading text's own label
                route = "other"
                detail = detail or "no spot through a call"
            now = verdict(e, binds, rd, "now", array)
            ca = verdict(e, binds, rd, "A", array)
            cb = verdict(e, binds, rd, "B", array)
            printed = "legal" if kind == "three-mode" else "ERROR"
            rows.append((route, f, ln, kind, rd, e, binds, detail, printed, now, ca, cb))
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(r)
    print("predarg census: %d reads through a macro or into an argument, %d printed programs scanned" % (len(rows), len(progs)))
    for k in sorted(by):
        print("route %-12s %d" % (k, len(by[k])))
    for k in sorted(by):
        print("\n== route %s (%d)" % (k, len(by[k])))
        for route, f, ln, kind, rd, e, binds, detail, printed, now, ca, cb in by[k]:
            cls = lambda v: v.split(" ")[0].rstrip(":")
            mv = "" if cls(now) == cls(ca) == cls(cb) else "   <== THE WALKER MOVES IT"
            print("%s:%d [%s] %s   in `%s`   %s%s" % (f, ln, kind, rd, e, "; ".join(binds), mv))
            if detail:
                print("      how: %s" % detail)
            print("      PRINTED %s (the line's kind, the documents at the start commit)" % printed)
            print("      NOW    %s" % now)
            print("      CAND-A %s" % ca)
            print("      CAND-B %s" % cb)


if __name__ == "__main__":
    main()
