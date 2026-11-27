#!/usr/bin/env python3
"""predfold1125_model.py: lane predfold1125's evidence, the successor of predfix90_model.py.

The fold of drop-not, array-argument, brace-counts, map-creator, string-literals, bang-split and and-not (record
docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-25 and 2026-11-27) into the predicate documents. DESIGN
evidence only: nothing here rules; no check under `make` reads it.

It LOADS predfix90's model unchanged up to its first check (`_a10 = ...`; the older models load through it), then
puts a FRONT END before the loaded engine, switched by X11[0] (off for the starting commit's control):
  TR11  reads the new spelling MECHANICALLY into the engine's: `!test` -> the engine's not; `~X` -> the engine's
        complement; `^A` / `!^A` -> a lookahead hole; a group question `q(@d, S)` -> `q((d: S))`; `every(@d, S)` ->
        `occurs.none((d: ~S))` (its ruled definition); the occurs counters -> a compared `count` (their definition);
        a brace count `X{a,b}` -> `/(?:${X}){a,b}/`; a map literal -> its labelled array; `m.a`, `m[key]` by the
        ruled lines; a string with an escape -> the rx text of its characters. It REFUSES, with the message naming
        the form to write: `NOT`; `!` on a set or pattern; `~` on a test; `^~A`; a condition as a group question's
        argument; two arrays in one call; `x{}`, `x{,}`, `_` in braces; a bad string escape, a raw line end,
        adjacent strings; a map element with no label, a numeral label, `m.z` the map lacks.
  RX11  lowers what the loaded engine refuses (a lookahead, `when`, a pattern complement chain) into python `re`,
        from the program's text and its bindings' body texts (FILTER11: `P & ~Q ...`, each complement judged on
        P's stretch whole, P's paths at a start by end, longest first: a listed limit).
Its checks are printed by name; the verdict is its last line, `predfold1125_model: N checks, F failed`, and it
exits non-zero iff that line reports a failure. `PREDFOLD1125_LIGHT=1` skips SUCCESSOR11.
`PREDFOLD1125_SABOTAGE=qN` plants one wrong rule, fact or text per check (PLANTS11); `=all` runs each plant in its
own subprocess (LIGHT; the SUCCESSOR11 plant reads the dumped runs of PREDFOLD1125_SUCCDUMP).
Run: `timeout 3000 python3 -I -B <this dir>/predfold1125_model.py`.
"""
import builtins
import os
import re
import subprocess
import sys
import time

MY11 = os.path.abspath(__file__)
HERE11 = os.path.dirname(MY11)
LANES11 = os.path.normpath(os.path.join(HERE11, ".."))
P90 = os.path.join(LANES11, "predfix90_evidence", "predfix90_model.py")
START11 = "212e234e6"                                        # this lane's starting commit (lane/predfold1125), PINNED
SAB11 = os.environ.get("PREDFOLD1125_SABOTAGE", "")
LIGHT11 = os.environ.get("PREDFOLD1125_LIGHT") == "1"
_src10 = builtins.open(P90, encoding="utf-8").read()
_a11 = _src10.index("_a10 = _src9.index('unit9(\"CONTROL\", ')")
__file__ = P90
_sav_env = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("PREDFIX90_")}
exec(compile(_src10[:_a11], P90, "exec"), globals())         # noqa: S102  predfix90's engines, unchanged
os.environ.update(_sav_env)
__file__ = MY11
_P11_LOADED = prog                                           # noqa: F821  the loaded chain's program builder


def s11(q):
    return SAB11 == q


# ================================================================== TR11 and RX11 (inlined below, verbatim)
TR11_SRC = r'''# TR11: the ruled spelling of 2026-11-25/27 read into the loaded engines' spelling (a FRONT END, mechanical).
# drop-not + bang-split + and-not: `!X` the logical not of a TEST (a condition, a lookaround, a group question,
# another `!X`) -> the engines' `NOT X` (`!!X` -> X; `!peek(A)` -> `!^A`); `~X` the complement of a SET or
# PATTERN -> the engines' `!X`; `^A` -> `/(?=${A})/`; `!^A` -> `/(?!${A})/`. Line 4: `!` on a set or pattern is an error naming `~`; `~` on a test an error
# naming `!`; `NOT` is no spelling. array-argument: `some(@d, S)` -> `some((d: S))`, `every(@d, S)` ->
# `occurs.none((d: ~S))` (as told), `count(@d)` -> `count((d: anything))`; a condition as the argument is an error
# naming the array form; the occurs counters -> a compared `count` (their definition). brace-counts: `X{a,b}` (directly after an operand) -> `/(?:${X}){a,b}/`, `?`/`+` after the
# braces kept; `x{}` and `x{,}` errors. map-creator: a map literal `{a = A, b = B}` bound to a name -> the labelled
# array `[a = A] | [b = B]`; `m.a` -> its element; `m[key]` -> the selected elements in the key's order, every result
# kept; nothing found -> `/\b\B/` (never matches). string-literals: escapes `\\ \" \' \n \r \t \x{..}` only; a raw
# line end is an error; a string with an escape -> the rx text of its characters (the engines read no escapes).
import re


class TrError(Exception):
    pass


GQ = ("some", "every", "count", "occurs.none", "occurs.exactly", "occurs.at_least", "occurs.at_most")
STR_ESC = re.compile(r"\\(?:\\|\"|'|n|r|t|x\{[0-9A-Fa-f]+\})")


def _rx_end(s, i):
    j = i + 1
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s.startswith("${", j):
            j = _brace_end(s, j + 1)
            continue
        if s[j] == "/":
            return j + 1
        j += 1
    raise TrError("an unterminated rx literal")


def _brace_end(s, i):
    """i at `{`; the index after its matching `}` (rx literals and strings inside skipped)."""
    d, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "/" and _rx_start(s, j):
            j = _rx_end(s, j)
            continue
        if c in "\"'":
            j = _str_end(s, j)
            continue
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                return j + 1
        j += 1
    raise TrError("an unterminated brace")


def _str_end(s, i):
    q, j = s[i], i + 1
    while j < len(s):
        if s[j] == "\\":
            m = STR_ESC.match(s, j)
            if not m:
                raise TrError("the escape `%s` is not a string escape (string-literals line 3: only the backslash, "
                              "the two quotes, `\\n`, `\\r`, `\\t` and `\\x{..}`); a class is written in rx text, "
                              "`/%s/`" % (s[j:j + 2], s[j:j + 2]))
            j = m.end()
            continue
        if s[j] == "\n":
            raise TrError("a string ends on the line it starts on (string-literals line 5)")
        if s[j] == q:
            return j + 1
        j += 1
    raise TrError("an unterminated string")


def _rx_start(s, i):
    k = i - 1
    while k >= 0 and s[k] == " ":
        k -= 1
    return k < 0 or s[k] in "(,[|&=:{!~^" or s[k - 2:k + 1] == "SEQ" or s.endswith(":=", 0, k + 1)


def _group_end(s, i):
    op, cl = s[i], {"(": ")", "[": "]"}[s[i]]
    d, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "/" and _rx_start(s, j):
            j = _rx_end(s, j)
            continue
        if c in "\"'":
            j = _str_end(s, j)
            continue
        if c == op:
            d += 1
        elif c == cl:
            d -= 1
            if d == 0:
                return j + 1
        j += 1
    raise TrError("an unbalanced `%s`" % op)


def _operand(s, i):
    """The ONE atom at i (level 3 of core/operators/precedence: a prefix operator takes one atom with its postfix
    operators). Returns its end."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        raise TrError("an operator with no operand")
    c = s[i]
    if c in "!~^":
        return _operand(s, i + 1)
    if c == "/":
        j = _rx_end(s, i)
    elif c in "\"'":
        j = _str_end(s, i)
    elif c in "([":
        j = _group_end(s, i)
    elif c == "@":
        m = re.compile(r"@[\w.]+").match(s, i)
        j = m.end()
    elif c in "<>=":
        m = re.compile(r"(?:<=|>=|==|<|>)\s*(?:\$?[\w.]+|\"[^\"]*\")").match(s, i)
        if not m:
            raise TrError("a comparison with no value")
        j = m.end()
    else:
        m = re.compile(r"\$?[\w.]+").match(s, i)
        if not m:
            raise TrError("no operand at `%s`" % s[i:i + 10])
        j = m.end()
    while j < len(s) and s[j] in "([" and c not in "\"'/<>=":
        j = _group_end(s, j)                                 # a call, an index
        while j < len(s) and s[j] == ".":
            m = re.compile(r"\.[\w]+").match(s, j)
            j = m.end()
    while True:                                              # postfix quantifiers and brace counts
        m = re.compile(r"(?:\+\+|\+\?|\*\+|\*\?|\?\+|\?\?|[+*?])(?![\s]*[\w(/\"'\[$@<>!~^])").match(s, j)
        if m and m.end() > j:
            j = m.end()
            continue
        if j < len(s) and s[j] == "{":
            j = _brace_end(s, j)
            if j < len(s) and s[j] in "?+":
                j += 1
            continue
        break
    return j


def _top_split(s):
    """The operands of an expression split at its top-level `|`, `&`, `SEQ`, `,` (rx literals, strings, groups
    skipped)."""
    parts, i, last = [], 0, 0
    while i < len(s):
        c = s[i]
        if c == "/" and _rx_start(s, i):
            i = _rx_end(s, i)
            continue
        if c in "\"'":
            i = _str_end(s, i)
            continue
        if c in "([":
            i = _group_end(s, i)
            continue
        if c == "{":
            i = _brace_end(s, i)
            continue
        if c in "|&,":
            parts.append(s[last:i])
            last = i + 1
        elif s.startswith("SEQ", i):
            parts.append(s[last:i])
            last = i + 3
            i += 3
            continue
        i += 1
    parts.append(s[last:])
    return [p.strip() for p in parts if p.strip()]


def _top_colon(s):
    """True when s (a group's content) has a `:` at depth 0 that is not `:=`: a condition's record."""
    i = 0
    while i < len(s):
        c = s[i]
        if c == "/" and _rx_start(s, i):
            i = _rx_end(s, i)
            continue
        if c in "\"'":
            i = _str_end(s, i)
            continue
        if c in "([":
            i = _group_end(s, i)
            continue
        if c == ":" and not s.startswith(":=", i):
            return True
        i += 1
    return False


def kind(a):
    """'test' (a condition, a lookaround, a group question, a negated test) or 'set or pattern'."""
    a = a.strip()
    if a[:1] in "!^":
        return "test"
    if a[:1] == "~":
        return "set or pattern"
    m = re.match(r"([\w.]+)\(", a)
    if m and (m.group(1) in GQ or m.group(1) == "peek") and _group_end(a, m.end() - 1) == len(a):
        return "test"
    if a[:1] == "(" and _group_end(a, 0) == len(a):
        inner = a[1:-1]
        if _top_colon(inner):
            return "test"
        ps = _top_split(inner)
        if ps and all(kind(p) == "test" for p in ps):
            return "test"
    return "set or pattern"


def _unstring(s):
    body, out, i = s[1:-1], [], 0
    while i < len(body):
        if body[i] == "\\":
            c = body[i + 1]
            if c == "x":
                j = body.index("}", i)
                out.append(chr(int(body[i + 3:j], 16)))
                i = j + 1
                continue
            out.append({"n": "\n", "r": "\r", "t": "\t"}.get(c, c))
            i += 2
            continue
        out.append(body[i])
        i += 1
    return "".join(out)


def _string(s):
    """A string literal (either quote), its escapes checked (by _str_end). Handed over as written when it has no
    escape; with one, as the rx literal of its characters (the engines read no string escapes)."""
    if "\\" not in s:
        return s
    t = _unstring(s)
    return "/" + re.escape(t).replace("/", "\\/") + "/"


def tr(s, maps=None):
    maps = maps or {}
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "/" and _rx_start(s, i):
            j = _rx_end(s, i)
            out.append(_tr_rx(s[i:j], maps))
            i = j
            continue
        if c in "\"'":
            j = _str_end(s, i)
            out.append(_string(s[i:j]))
            if re.match(r"[ \t]*[\"']", s[j:]):
                raise TrError("adjacent strings do not join (string-literals line 4): the join is the sequence "
                              "operator, `%s SEQ %s`" % (s[i:j], s[j:].strip()[:20]))
            i = j
            continue
        if re.match(r"NOT\b", s[i:]) and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] in "_.")):
            raise TrError("`NOT` is no spelling (drop-not): the logical not of a test is `!`, the complement `~`")
        if c == "!" and not s.startswith("!=", i):
            j = _operand(s, i + 1)
            a = s[i + 1:j].strip()
            if a.startswith("!"):
                b = a[1:].strip()
                out.append(tr(b, maps) if b[:1] == "(" and _group_end(b, 0) == len(b) else "(" + tr(b, maps) + ")")
                i = j
                continue
            pk = re.fullmatch(r"peek\((.*)\)", a, re.S)
            if pk and _group_end(a, 4) == len(a):
                a = "^" + _paren(pk.group(1).strip())
            if a.startswith("^"):
                b = a[1:].strip()
                if b.startswith("~"):
                    raise TrError("a complement cannot match by itself (complement-place): `^%s`" % b)
                out.append("/(?!${" + tr(b, maps) + "})/")
            elif kind(a) == "test":
                out.append("NOT " + tr(a, maps))
            else:
                raise TrError("`!` on a set or pattern (`!%s`): the complement is `~%s`; \"cannot match here\" is "
                              "`!^%s` (bang-split line 4)" % (a, a, a))
            i = j
            continue
        if c == "~":
            j = _operand(s, i + 1)
            a = s[i + 1:j].strip()
            if kind(a) == "test":
                raise TrError("`~` on a test (`~%s`): the logical not of a test is `!%s` (bang-split line 4)" % (a, a))
            out.append("!" + tr(a, maps))
            i = j
            continue
        if c == "^":
            j = _operand(s, i + 1)
            a = s[i + 1:j].strip()
            if a.startswith("~"):
                raise TrError("a complement cannot match by itself (complement-place): `^%s` looks ahead for a "
                              "match; the negative lookahead is `!^%s`" % (a, a[1:].strip()))
            out.append("/(?=${" + tr(a, maps) + "})/")
            i = j
            continue
        m = re.compile(r"(%s)\(" % "|".join(re.escape(g) for g in GQ)).match(s, i)
        if m and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] in "_.")):
            j = _group_end(s, m.end() - 1)
            out.append(_gq(m.group(1), s[m.end():j - 1], maps))
            i = j
            continue
        m = re.compile(r"[A-Za-z_]\w*").match(s, i)
        if m and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] in "_.$")) and m.group(0) in maps:
            nm, j = m.group(0), m.end()
            if s.startswith("[", j):
                k = _group_end(s, j)
                out.append(_select(maps[nm], s[j + 1:k - 1], maps))
                i = k
                continue
            mm = re.compile(r"\.(\w+)").match(s, j)
            if mm and mm.group(1) in dict(maps[nm]):
                out.append("(" + dict(maps[nm])[mm.group(1)] + ")")
                i = mm.end()
                continue
            if mm and mm.group(1) not in ("index", "label"):
                raise TrError("no member `%s` in the map %s (map-creator line 3: `m.a` must exist; the search is "
                              "`%s[\"%s\"]`)" % (mm.group(1), nm, nm, mm.group(1)))
        if c == "{" and i > 0 and s[i - 1] not in " ([,|&=:" and not (i >= 2 and s[i - 2] == "\\"):
            j = _brace_end(s, i)
            out.append(_count(out, s[i:j], s[j:j + 1] if s[j:j + 1] in ("?", "+") else ""))
            i = j + (1 if s[j:j + 1] in ("?", "+") else 0)
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _tr_rx(lit, maps):
    out, i = [], 0
    while i < len(lit):
        if lit[i] == "\\":
            out.append(lit[i:i + 2])
            i += 2
            continue
        if lit.startswith("${", i):
            j = _brace_end(lit, i + 1)
            out.append("${" + tr(lit[i + 2:j - 1], maps) + "}")
            i = j
            continue
        out.append(lit[i])
        i += 1
    return "".join(out)


def _gq(name, args, maps):
    ps = _top_split_commas(args)
    k = 1 if name.startswith("occurs.") and name != "occurs.none" else 0
    if len(ps) <= k or not ps[k].startswith("@"):
        raise TrError("a group question takes the array form of a label and a set (array-argument line 1): write "
                      "`%s(%s@d, S)`, not a condition" % (name, "n, " if k else ""))
    if name == "count" and len(ps) == k + 1:
        ps.append("anything")
    if len(ps) != k + 2:
        raise TrError("one array per call (array-argument line 3)")
    lab, st = ps[k][1:], ps[k + 1]
    if "@" in st:
        raise TrError("one array per call (array-argument line 3)")
    if name == "every":
        return "occurs.none((%s: %s))" % (lab, tr("~" + _paren(st), maps))
    if k:  # the occurs counters, by their definition: the count of the settings in S, compared with n
        n = tr(ps[0], maps)
        op = {"occurs.exactly": "==", "occurs.at_least": ">=", "occurs.at_most": "<="}[name]
        return "(count((%s: %s)): %s%s)" % (lab, tr(st, maps), op, n)
    head = ", ".join(tr(p, maps) for p in ps[:k])
    return "%s(%s(%s: %s))" % (name, head + ", " if head else "", lab, tr(st, maps))


def _paren(st):
    return st if (st[:1] == "(" and _group_end(st, 0) == len(st)) or len(_top_split(st)) == 1 else "(" + st + ")"


def _top_split_commas(s):
    parts, i, last = [], 0, 0
    while i < len(s):
        c = s[i]
        if c == "/" and _rx_start(s, i):
            i = _rx_end(s, i)
            continue
        if c in "\"'":
            i = _str_end(s, i)
            continue
        if c in "([":
            i = _group_end(s, i)
            continue
        if c == "{":
            i = _brace_end(s, i)
            continue
        if c == ",":
            parts.append(s[last:i])
            last = i + 1
        i += 1
    parts.append(s[last:])
    return [p.strip() for p in parts if p.strip()]


def _count(out, braces, mod):
    """`X{a,b}` -> `/(?:${X}){a,b}/`: X is the ONE operand already written before the braces."""
    inner = braces[1:-1].replace(" ", "")
    if inner in ("", ","):
        raise TrError("`x%s` is a compile error (brace-counts line 4): `x*` is the spelling" % braces)
    if "_" in inner:
        raise TrError("an unspecified bound is written by leaving it out, `x{a,}` (brace-counts reading (c))")
    if not re.fullmatch(r"\d+|\d*,\d*", inner):
        raise TrError("a count in braces that the front end does not read: `%s`" % braces)
    if inner.startswith(","):
        inner = "0" + inner
    txt = "".join(out)
    k = _operand_back(txt)
    opnd = txt[k:]
    if opnd.startswith("(") and _top_colon(opnd[1:-1]):
        raise TrError("a quantifier on a condition is a compile error (core/conditions/quantified): `%s%s`" % (
            opnd, braces))
    del out[:]
    out.append(txt[:k])
    if mod == "+":
        return "/(?>(?:${%s}){%s})/" % (opnd, inner)
    return "/(?:${%s}){%s}%s/" % (opnd, inner, mod)


def _operand_back(t):
    """The start of the ONE operand ending at the end of t (an rx literal, a string, a group, a name, a call)."""
    j = len(t)
    if t.endswith("/"):
        k = j - 2
        while k >= 0:
            if t[k] == "/" and (k == 0 or t[k - 1] != "\\") and _rx_start(t, k):
                return k
            k -= 1
    if t.endswith(('"', "'")):
        return t.rindex(t[-1], 0, j - 1)
    if t.endswith((")", "]")):
        op = "(" if t[-1] == ")" else "["
        d, k = 0, j - 1
        while k >= 0:
            if t[k] in ")]":
                d += 1
            elif t[k] in "([":
                d -= 1
                if d == 0:
                    m = re.search(r"[\w.]+$", t[:k])
                    return m.start() if m else k
            k -= 1
    m = re.search(r"[\w.]+$", t)
    if m:
        return m.start()
    raise TrError("a count in braces with no operand before it")


MAP_LIT = re.compile(r"\{\s*\w+\s*=")


def map_of(body):
    """A map literal `{a = A, b = B}`: its (name, element) list, every element labelled (map-creator line 1)."""
    b = body.strip()
    if not (b.startswith("{") and _brace_end(b, 0) == len(b)):
        return None
    els = []
    for p in _top_split_commas(b[1:-1]):
        m = re.fullmatch(r"(\w+)\s*=\s*(.+)", p, re.S)
        if m and m.group(1).isdigit():
            raise TrError("a numeral is not a label name (map-creator line 1)")
        if not m:
            raise TrError("a map's element with no label (map-creator line 1: its literal makes a missing label a "
                          "syntax error): `%s`" % p)
        if m.group(1).isdigit():
            raise TrError("a numeral is not a label name (map-creator line 1)")
        els.append((m.group(1), m.group(2).strip()))
    return els


def _select(els, key, maps):
    """`m[key]`: each string of the key looked up in the key's order; a numeral a position, any other string a name;
    every result kept, no deduplication; nothing found is the empty array, the never-matching pattern."""
    strs = []
    for p in [x.strip() for x in key.split("|")]:
        if re.fullmatch(r'"[^"]*"', p):
            strs.append(p[1:-1])
        elif re.fullmatch(r"\d+", p):
            strs.append(p)
        else:
            raise TrError("a key the front end does not list out (an infinite or match-time key is under "
                          "construction: map-creator line 5): `%s`" % p)
    res = []
    for k in strs:
        if re.fullmatch(r"[1-9]\d*", k):
            if int(k) <= len(els):
                res.append(els[int(k) - 1])
        else:
            res.extend(e for e in els if e[0] == k)
    if not res:
        return "/\\b\\B/"
    return "(" + " | ".join("[%s = %s]" % (n, tr(e, maps)) for n, e in res) + ")"


def _label_marks(head, body):
    """label-needs-mark: a body that places a parameter's name as a label (`[l = ...]`, `(?<:${l}>`) needs the
    parameter marked `l:` (a compile error at the definition)."""
    m = re.fullmatch(r"[\w.]+\((.*)\)", head, re.S)
    if not m:
        return
    for p in _top_split_commas(m.group(1)):
        p = p.strip()
        nm = re.match(r"\w+", p)
        if not nm or p[nm.end():].lstrip().startswith(":") or p.endswith(":"):
            continue
        v = nm.group(0)
        if re.search(r"(?<![\w.$])%s\s*=(?!=)" % re.escape(v), body) and re.search(r"\[[^\]]*(?<![\w.$])%s\s*=" % re.escape(v), body) \
                or re.search(r"\(\?<:\$\{\s*%s\s*\}>" % re.escape(v), body):
            raise TrError("the body places the parameter `%s` as a label; a label parameter is marked `%s:` in the "
                          "head (label-needs-mark: a compile error at the definition)" % (v, v))


def tr_prog(expr, binds):
    """The program and its bindings, read into the loaded engines' spelling."""
    maps = {}
    for b in binds:
        n, _, body = b.partition(" := ")
        els = map_of(body)
        if els is not None:
            maps[n.strip()] = els
    b2 = []
    for b in binds:
        n, _, body = b.partition(" := ")
        _label_marks(n.strip(), body)
        if n.strip() in maps:
            b2.append(n + " := " + " | ".join("[%s = %s]" % (k, tr(v, maps)) for k, v in maps[n.strip()]))
        else:
            b2.append(n + " := " + tr(body, maps))
    return tr(expr, maps), b2
'''

RX11_SRC = r'''# RX11 and FILTER11: the programs the loaded engines do not run (a negative lookahead, `when`, a pattern
# complement), lowered MECHANICALLY from their text and the body texts of the definitions they call, into python
# `re`. RX11: rx literals (holes inside lowered in place), strings, SEQ, `|`, groups, label sets (the label moves no
# match: dropped), `^A` = `(?=A)`, `!^A` = `(?!A)`, the postfix quantifiers and brace counts, bindings, and macros
# (a call's arguments laid into the body's text for its parameters, defaults included). FILTER11: `P & ~Q & ...`,
# P an RX11 pattern, each `~Q` judged on P's stretch whole (core/filters/complement); P's paths at a start are taken
# by END, longest first (exact for a P whose paths at one start differ by end and are tried longest first, as
# `\d+`: a known limit). Anything else is Unsupported and goes back to the caller.
import re

from tr11 import (_brace_end, _group_end, _rx_end, _rx_start, _str_end, _top_split_commas, TrError)


class Unsupported(Exception):
    pass


def _split(s, seps):
    """s split at the top-level separators in `seps` (`|`, `&`, `SEQ`)."""
    parts, i, last = [], 0, 0
    while i < len(s):
        c = s[i]
        if c == "/" and _rx_start(s, i):
            i = _rx_end(s, i)
            continue
        if c in "\"'":
            i = _str_end(s, i)
            continue
        if c in "([":
            i = _group_end(s, i)
            continue
        if c == "{":
            i = _brace_end(s, i)
            continue
        if c in seps and c in "|&" and not (c == "&" and s.startswith("&&", i)):
            parts.append(s[last:i])
            last = i + 1
        elif "SEQ" in seps and s.startswith("SEQ", i):
            parts.append(s[last:i])
            last = i + 3
            i += 3
            continue
        i += 1
    parts.append(s[last:])
    return [p.strip() for p in parts]


def parse_binds(binds):
    env = {}
    for b in binds:
        head, _, body = b.partition(" := ")
        m = re.fullmatch(r"([\w.]+)(?:\((.*)\))?", head.strip())
        if not m:
            raise Unsupported("a binding head: " + head)
        params = []
        for p in _top_split_commas(m.group(2) or ""):
            n, eq, d = p.partition("=")
            params.append((n.strip(), d.strip() if eq else None))
        env[m.group(1)] = (params if m.group(2) is not None else None, body.strip())
    return env


def _unstr(s):
    body, out, i = s[1:-1], [], 0
    while i < len(body):
        if body[i] == "\\":
            c = body[i + 1]
            if c == "x":
                j = body.index("}", i)
                out.append(chr(int(body[i + 3:j], 16)))
                i = j + 1
                continue
            out.append({"n": "\n", "r": "\r", "t": "\t"}.get(c, c))
            i += 2
            continue
        out.append(body[i])
        i += 1
    return "".join(out)


def lower(s, env):
    """The python regex of one expression (no `&`)."""
    alts = _split(s, "|")
    if len(alts) > 1:
        return "(?:" + "|".join(lower(a, env) for a in alts) + ")"
    if len(_split(s, "&")) > 1:
        raise Unsupported("an `&` inside RX11")
    return "".join(_atom(p, env) for p in _split(s, ("SEQ",)))


POST = re.compile(r"(\+\+|\+\?|\*\+|\*\?|\?\+|\?\?|[+*?]|\{\d*,?\d*\}[?+]?)$")


def _atom(a, env):
    a = a.strip()
    if not a:
        raise Unsupported("an empty operand")
    m = POST.search(a)
    if m and not (a.endswith("/") or a.endswith('"')):
        core = a[:m.start()].strip()
        q = m.group(1)
        if q.startswith("{"):
            inner = q[1:q.index("}")]
            if inner in ("", ","):
                raise TrError("`x{}` and `x{,}` are compile errors")
            if inner.startswith(","):
                q = "{0" + q[1:]
        try:
            return "(?:" + _atom(core, env) + ")" + q
        except Unsupported:
            pass
    pk = re.fullmatch(r"(!?)peek\((.*)\)", a, re.S)
    if pk and _group_end(a, len(pk.group(1)) + 4) == len(a):
        a = pk.group(1) + "^(" + pk.group(2) + ")"
    if a.startswith("!^"):
        return "(?!" + _atom(a[2:], env) + ")"
    if a.startswith("^"):
        return "(?=" + _atom(a[1:], env) + ")"
    if a[:1] in "!~":
        raise Unsupported("a negation or complement in place")
    if a[0] == "/" and _rx_end(a, 0) == len(a):
        return "(?:" + _rx(a[1:-1], env) + ")"
    if a[0] in "\"'" and _str_end(a, 0) == len(a):
        return re.escape(_unstr(a))
    if a[0] == "(" and _group_end(a, 0) == len(a):
        inner = a[1:-1]
        if re.match(r"\s*[\w.$()\[\], ]*\??:(?!=)", inner):
            raise Unsupported("a condition")
        return "(?:" + lower(inner, env) + ")"
    if a[0] == "[" and _group_end(a, 0) == len(a):
        if not a[1:-1].strip():
            return "(?!)"                                    # the empty array: the never-matching rx
        ents = []
        for e in _split(a[1:-1], "|"):
            for x in _top_split_commas(e):
                mm = re.fullmatch(r"(?:\(=?\w*\)|\w+)\s*=\s*(.+)", x, re.S)
                ents.append(lower(mm.group(1) if mm else x, env))
        return "(?:" + "|".join(ents) + ")"
    if a == "anything":
        return r"[\s\S]*"
    m = re.fullmatch(r"([\w.]+)(\((.*)\))?", a, re.S)
    if m and m.group(1) in env:
        params, body = env[m.group(1)]
        if m.group(2) is None:
            if params is not None:
                raise Unsupported("a macro used bare")
            return "(?:" + lower(body, env) + ")"
        if params is None:
            raise TrError("a pattern called with arguments")
        args = _top_split_commas(m.group(3))
        vals, pos, named = {}, 0, False
        for x in args:
            mm = re.fullmatch(r"(\w+)\s*=\s*(.+)", x, re.S)
            if mm and mm.group(1) in dict(params):
                vals[mm.group(1)] = mm.group(2)
                named = True
            else:
                if named:
                    raise TrError("a positional entry after a named one")
                vals[params[pos][0]] = x
                pos += 1
        for n, d in params:
            if n not in vals:
                if d is None:
                    raise TrError("a missing required parameter `%s`" % n)
                vals[n] = d
        txt = re.sub(r"(?<![\w.$/])(%s)(?![\w])" % "|".join(re.escape(n) for n, _ in params),
                     lambda mo: "(" + vals[mo.group(1)] + ")", body)
        return "(?:" + lower(txt, env) + ")"
    raise Unsupported("an operand RX11 does not lower: " + a)


def _rx(t, env):
    out, i, cls = [], 0, False
    while i < len(t):
        if t[i] == "\\":
            out.append(t[i:i + 2])
            i += 2
            continue
        if t[i] == "[" and not cls:
            cls = True
        elif t[i] == "]" and cls:
            cls = False
        if t.startswith("${", i) and cls:
            raise Unsupported("a hole in a class position (its own rules: core/holes/class)")
        if t.startswith("${", i):
            j = _brace_end(t, i + 1)
            out.append("(?:" + lower(t[i + 2:j - 1], env) + ")")
            i = j
            continue
        out.append(t[i])
        i += 1
    return re.sub(r"\(\?<(\w+)>", "(?:", "".join(out))


class Filter:
    """`P & ~Q & ...` over python `re`: P's paths at a start by end, longest first; each complement judged on the
    stretch whole."""

    def __init__(self, p, negs, Prog):
        self.p = re.compile(p)
        self.negs = [re.compile(n) for n in negs]
        self.Prog = Prog

    def keep(self, t):
        return all(n.fullmatch(t) is None for n in self.negs)

    def at(self, s, i, nonempty=False):
        for j in range(len(s), i - 1, -1):
            if nonempty and j == i:
                continue
            if self.p.fullmatch(s, i, j) and self.keep(s[i:j]):
                return (i, j, None)
        return None

    def whole(self, s):
        return self.p.fullmatch(s) is not None and self.keep(s)

    def search(self, s, frm=0):
        for i in range(frm, len(s) + 1):
            r = self.at(s, i)
            if r:
                return r
        return None

    def findall(self, s):
        return self.Prog.findall(self, s)


def program(expr, binds, Re, Prog):
    """An RX11 or FILTER11 program object, or Unsupported."""
    env = parse_binds(binds)
    ops = _split(expr, "&")
    if len(ops) == 1:
        return Re(lower(expr, env))
    pos, negs = [], []

    def neg_of(x):
        x = x.strip()
        if x.startswith("~"):
            negs.append(lower(x[1:], env))
            return True
        if x in env and env[x][0] is None and all(neg_of(y) for y in _split(env[x][1], "&")):
            return True
        return False
    for x in ops:
        if not neg_of(x):
            pos.append(lower(x, env))
    if len(pos) != 1:
        raise Unsupported("FILTER11 takes one positive operand")
    return Filter(pos[0], negs, Prog)
'''

# ================================================================== the data of the checks
WHEN11 = re.search(r"`(when\(test, then, else = //\) := [^`]*)`", NOWS["library.md"]).group(1)   # noqa: F821  READ
SPEC11 = [  # (id, tag, label, program, bindings joined by " || ", WHOLE texts joined by "|", SEARCHED, FIND-ALL)
    ('gt1', 'core/model/table/group-truth', 'No setting of d is 7', '/(?:(?<d>\\d)?,)+/ & !some(@d, "7")', '', ',|1,|7,|1,7,|7,,', '7,1,', '1,7, , 7,7,'),
    ('gt2', 'core/model/table/group-truth', 'The same question', '/(?:(?<d>\\d)?,)+/ & occurs.none(@d, "7")', '', ',|1,|7,|1,7,|7,,', '7,1,', '1,7, , 7,7,'),
    ('gt3', 'core/model/table/group-truth', 'Every setting of d is 7', '/(?:(?<d>\\d)?,)+/ & occurs.none(@d, ~"7")', '', ',|1,|7,|1,7,|7,,', '7,1,', '1,7, , 7,7,'),
    ('br1', 'core/patterns/quantifiers/braces', 'A range', 'rx.digit{2,4}', '', '1|12|1234|12345', '1 12345678 123', '1 12345678 123'),
    ('br2', 'core/patterns/quantifiers/braces', 'Lazy', 'rx.digit{2,4}?', '', '1|12|1234|12345', '1 12345678 123', '1 12345678 123'),
    ('br3', 'core/patterns/quantifiers/braces', 'Exact', 'rx.digit{3}', '', '1|12|1234|12345', '1 12345678 123', '1 12345678 123'),
    ('br4', 'core/patterns/quantifiers/braces', 'No maximum', 'rx.digit{3,}', '', '1|12|1234|12345', '1 12345678 123', '1 12345678 123'),
    ('br5', 'core/patterns/quantifiers/braces', 'No minimum', 'rx.digit{,2}', '', '1|12|1234|12345', '1 12345678 123', '1 12345678 123'),
    ('st1', 'core/patterns/strings', 'Character literals', '"a.b+"', '', 'a.b+|axb|axbbb', 'a.b axb a.b+', 'a.b axb a.b+'),
    ('st2', 'core/patterns/strings', 'Either quote delimits', '\'a"b\'', '', 'a"b|ab', 'xa"b', 'a"b ab'),
    ('st3', 'core/patterns/strings', 'A code', '"\\x{41}b"', '', 'Ab|ab', 'ab Ab', 'Ab ab Ab'),
    ('st4', 'core/patterns/strings', 'A hole mark is plain text', '"${x}"', '', '${x}|x', 'a ${x}', '${x} x'),
    ('ah1', 'core/patterns/lookaround/ahead', 'Ahead', '"x" SEQ ^/\\d/', '', 'x|x1', '1x2 x3 4x x', '1x2 x3 4x x'),
    ('ah2', 'core/patterns/lookaround/ahead', 'Not ahead', '"x" SEQ !^/\\d/', '', 'x|x1', '1x2 x3 4x x', '1x2 x3 4x x'),
    ('ah3', 'core/patterns/lookaround/ahead', 'Its labels', '^/(?<d>\\d)/ SEQ /\\d\\d/ & (d: <5)', '', '37|73', 'x73 37', '37 73 56'),
    ('cp1', 'core/filters/complement', 'A pattern difference', '/\\d+/ & ~/7\\d*/', '', '123|712', 'a7 12', '7 12 77 37'),
    ('cp2', 'core/filters/complement', 'Present and outside', '/(?<h>\\d)?x/ & (h: ~<5)', '', 'x|3x|7x', 'x 3x 7x', 'x 3x 7x'),
    ('cp3', 'core/filters/complement', 'Absent or outside', '/(?<h>\\d)?x/ & (h ?: ~<5)', '', 'x|3x|7x', '3x x 7x', 'x 3x 7x'),
    ('cp4', 'core/filters/complement', 'Its not, the plain entry', '/(?<h>\\d)?x/ & !(h: <5)', '', 'x|3x|7x', '3x x 7x', 'x 3x 7x'),
    ('ng1', 'core/filters/negation', 'Not ahead', '/\\d/ SEQ !^/x/', '', '7|7x', '7x 8', '1x 2 3x4'),
    ('ng2', 'core/filters/negation', 'A condition', '/(?<h>\\d)?x/ & !(h: <5)', '', 'x|3x|7x', '3x x 7x', 'x 3x 7x'),
    ('ng3', 'core/filters/negation', 'A group question', '/(?:(?<d>\\d)?,)+/ & !some(@d, "7")', '', ',|1,|7,|1,7,', '7,1,', '1,7, , 7,7,'),
    ('ng4', 'core/filters/negation', 'Twice', '/(?<h>\\d)?x/ & !!(h: <5)', '', 'x|3x|7x', '7x 3x', 'x 3x 7x'),
    ('fm1', 'core/filters/family', 'Ahead', '/\\d/ SEQ ^/x/', '', '7|7x', '7x 8', '1x 2 3x4'),
    ('fm2', 'core/filters/family', 'Kinds', '/\\d+/ & neither', 'neither := ~/7\\d*/ & ~/8\\d*/', '123|812', '7 8 12', '12 7 8 93'),
    ('oe1', 'core/conditions/form/optional-entry', 'Its not, the plain entry', '/(?<h>\\d)?x/ & !(h: <5)', '', 'x|3x|7x', '3x 7x', '7x 3x x'),
    ('mp1', 'core/modules/map', 'As a pattern', 'm', 'm := {a = /\\d/, b = /[a-z]/}', '7|x|7x', '-x7', '7x-y'),
    ('mp2', 'core/modules/map', 'No deduplication', 'm SEQ "!"', 'm := {a = "x", b = "x"}', 'x!|y!', 'ax!', 'x! y! x!'),
    ('ma1', 'core/modules/map/access', 'A member', 'm.b', 'm := {a = /\\d/, b = /[a-z]/}', '7|x', '7x', '7x y'),
    ('ma2', 'core/modules/map/access', "A search, the key's order", 'm["b" | 1] SEQ /\\w/', 'm := {a = /\\d/, b = /[a-z]/}', '7x|x7|77', '-77 x7', '7x x7 77'),
    ('ma3', 'core/modules/map/access', 'A search by position', 'm[2]', 'm := {a = /\\d/, b = /[a-z]/}', '7|x', '7x', '7x y'),
    ('ma4', 'core/modules/map/access', 'Nothing found', 'm["z"] | "q"', 'm := {a = /\\d/, b = /[a-z]/}', 'q|7|x', '7xq', '7 q x'),
    ('wn1', 'lib/control/when-test/not', 'The negative lookahead as the test', 'when(!^/x/, /\\w/)', '', 'a|x|', 'xa', 'xa b'),
    ('pk1', 'lib/control/peek', 'Its not', '!peek(/\\d/) SEQ /\\w/', '', 'a|7', '7a', '7a b'),
    ('oc1', 'lib/counting/occurs', 'Exactly two', '/(?:(?<d>\\d),)+/ & occurs.exactly(2, @d, "7")', '', '7,1,7,|7,1,|7,7,7,', '7,7,7,', '7,7,7, 1,7,7,'),
    ('oc2', 'lib/counting/occurs', 'None', '/(?:(?<d>\\d),)+/ & occurs.none(@d, "7")', '', '1,2,|7,1,', '7, 1,2,', '7,1, 2, 3,'),
    ('ev1', 'lib/counting/every', 'Every setting', '/(?:(?<d>\\d)?,)+/ & every(@d, "7")', '', '7,7,|7,,|7,1,|,', '1, 7,,', '7,, 7,1, 7,7,'),
    ('ev2', 'lib/counting/every', 'Set at least once', '/(?:(?<d>\\d)?,)+/ & some(@d, "7") & every(@d, "7")', '', '7,7,|7,,|7,1,', '7,, 7,7,', '7,, 7,1, 7,7,'),
    ('ev4', 'lib/counting/every', 'No pass, set at least once', '/(?:(?<d>\\d),)*x/ & some(@d, "7") & every(@d, "7")', '', 'x|7,x', '-x', 'x 7,x 1,x'),
    ('ev3', 'lib/counting/every', 'No pass', '/(?:(?<d>\\d),)*x/ & every(@d, "7")', '', 'x|7,x|1,x', '-x', 'x 7,x 1,x'),
    ('ct1', 'lib/counting/count', 'Every setting counted', '/(?:(?<d>\\d)?,)+/ & (count(@d): ==2)', '', '1,2,|1,,2,|1,', '1, 1,2,', '1,2, 3, 4,,5,'),
]
QQ11 = [  # (his sentence, the piece that quotes it)
    ("goal is all dfa unless specified by user. I don't want \"when\" to force vm", "core/principles/all-dfa"),
    ("yes dfa, no not dfa under any circumstances, and maybe under certain circumstances with a weight between the two "
     "ends for the maybe.", "core/principles/all-dfa"),
    ("array-argument: yes including every", "core/model/table/group-truth"),
    ("array-argument: yes including every", "lib/counting/some"),
    ("array-argument: yes including every", "lib/counting/every"),
    ("Yes all five", "core/patterns/strings"),
    ("a string has no pattern operators. Everything is a character literal. Obvious but should be said",
     "core/patterns/strings"),
    ("I rule we should do this.", "core/patterns/quantifiers/braces"),
    ("this is pcre so I should try to stay familiar", "core/patterns/quantifiers/braces"),
    ("bang-split: yes. This is clean and what I was looking for.", "core/patterns/lookaround/ahead"),
    ("`^A` looks ahead and `!^A` is its negative.", "core/patterns/lookaround/ahead"),
    ("Lookbehind gets no operator for now.", "core/patterns/lookaround/ahead"),
    ("`~X` is the complement of a set or a pattern, filter-only as ruled today: `(h: ~S)`, `(h ?: ~S)`, `A & ~B`.",
     "core/filters/complement"),
    ("bang-split: yes. This is clean and what I was looking for.", "core/filters/negation"),
    ("agree drop &!", "core/filters/negation"),
    ("Yes to all seven", "core/modules/map"),
    ("Specifically F[\"z\"] is a search and F.z must exist or error", "core/modules/map/access"),
    ("I'd see it as the keys order", "core/modules/map/access"),
    ("`when(T, B, C) := T seq B | !^T seq C`", "lib/control/when"),
    ("`!` on a set or pattern is an error naming `~`", "lib/control/when-test/not"),
    ("capture-negated: broaden to any effect macro cannot be under negation.", "core/filters/negation/effects"),
]
GONE11 = {  # old program -> why: a printed line a ruling removed (its text kept in the details entry's `rejected:`)
    "[n = ([m = P] SEQ [k = Q])] & (n.d: <5)": "R-3, skip-past-wall: candidate (b)'s line, not taken",
    "[n = ([m = P] | [k = Q])] & (n.d: <5)": "R-3, skip-past-wall: candidate (b)'s line, not taken",
}
MOVED11 = {}  # repr(program) -> why: an answer that moves (none expected: the fold changes no answer)
HIST11 = {}   # (details file, program) -> why: a details line in the spelling of the run it records
RESPELL11 = {  # old program -> (new program, why): a printed line whose key moves with the re-spelling; the
    #            texts are the old key's, and the printed answers must be equal
    '/(?:(?<h>\\d):(?<m>\\d),)+/ & some((h: "5", m: "3"))':
        ('/(?:(?<h>\\d):(?<m>\\d),)+/ & some(@h, "5") & some(@m, "3")', "array-argument line 3: two arrays, two calls"),
    '/(?:(?<h>\\d)(?::(?<m>\\d))?,)+/ & some((h: "5", m: "3"))':
        ('/(?:(?<h>\\d)(?::(?<m>\\d))?,)+/ & some(@h, "5") & some(@m, "3")', "array-argument line 3"),
    '/(?:(?<d>\\d)?,)+/ & some(NOT (d: "7"))': ('/(?:(?<d>\\d)?,)+/ & some(@d, ~"7")', "array-argument line 4"),
    '/(?:(?<d>\\d)?,)+/ & (count(NOT (d: "7")): ==0)':
        ('/(?:(?<d>\\d)?,)+/ & (count(@d, ~"7"): ==0)', "array-argument line 4"),
    '/\\d/ SEQ NOT peek(/x/)': ('/\\d/ SEQ !^/x/', "bang-split line 5"),
    'when(peek(/\\d/), /\\d\\d/, else = /\\w/)': ('when(^/\\d/, /\\d\\d/, else = /\\w/)', "bang-split line 5"),
    '/(?:(?<d>\\d)?,)+/ & some((d: "7")) & occurs.none(NOT (d: "7"))':
        ('/(?:(?<d>\\d)?,)+/ & some(@d, "7") & every(@d, "7")', "array-argument, `every` as told"),
    '/(?:(?<d>\\d),)*x/ & some((d: "7")) & occurs.none(NOT (d: "7"))':
        ('/(?:(?<d>\\d),)*x/ & some(@d, "7") & every(@d, "7")', "array-argument, `every` as told"),
}

import types                                                 # noqa: E402

TR11 = types.ModuleType("tr11")
exec(compile(TR11_SRC, MY11 + ":TR11", "exec"), TR11.__dict__)          # noqa: S102  the inlined front end
sys.modules["tr11"] = TR11
RX11 = types.ModuleType("rx11")
exec(compile(RX11_SRC, MY11 + ":RX11", "exec"), RX11.__dict__)          # noqa: S102  the inlined lowering
X11 = [True]
FALLBACK11 = []

# ---- the plants that alter a RULE of the front end (each its own check's)
if s11("q2"):                                                # TR11: a condition read as a set (`!(h: <5)` an error)
    _k0 = TR11.kind
    TR11.kind = lambda a: "set or pattern" if a.strip().startswith("(") else _k0(a)
if s11("q6"):                                                # GROUP11: `every` read without its complement
    _gq0 = TR11._gq
    TR11._gq = lambda n, a, m: _gq0("occurs.none", a, m) if n == "every" else _gq0(n, a, m)
if s11("q7"):                                                # BRACES: `{,b}` read as `{1,b}`
    _c0 = TR11._count
    TR11._count = lambda o, b, md: _c0(o, b.replace("{,", "{1,"), md)
if s11("q8"):                                                # STRINGS: `\n` read as the letter n
    _u0 = TR11._unstring
    TR11._unstring = lambda s: _u0(s.replace("\\n", "n"))
if s11("q9"):                                                # MAP11: the key's order reversed
    _s0 = TR11._select
    TR11._select = lambda els, key, maps: _s0(els, " | ".join(reversed([x.strip() for x in key.split("|")])), maps)


def prog(expr, binds=(), **opts):                            # noqa: F811
    """The new spelling: TR11, then the loaded engine; RX11 where the engine refuses. X11 off: the engine alone."""
    if not X11[0]:
        return _P11_LOADED(expr, list(binds), **opts)
    binds = list(binds)
    if "when(" in expr and not any(b.startswith("when(") for b in binds):
        binds.append(WHEN11)                                 # the provided body, READ from library.md
    try:
        e2, b2 = TR11.tr_prog(expr, list(binds))
    except TR11.TrError as e:
        raise CompileError(str(e))                           # noqa: F821
    try:
        return _P11_LOADED(e2, b2, **opts)
    except Exception as e0:                                  # noqa: BLE001
        try:
            P = RX11.program(expr, list(binds), Re, Prog)    # noqa: F821
        except (RX11.Unsupported, re.error):
            raise e0
        except TR11.TrError as e:
            raise CompileError(str(e))                       # noqa: F821
        FALLBACK11.append((expr, str(e0)[:80]))
        return P


RESULTS = []
ARMS11 = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def unit11(name, what):
    print("== %s: %s" % (name, what))
    return True


def run11(expr, binds=()):
    try:
        return prog(expr, list(binds)), None
    except CompileError as e:                                # noqa: F821
        return None, str(e)
    except Exception as e:                                   # noqa: BLE001
        return None, "CRASH %s: %s" % (type(e).__name__, str(e)[:80])


def ans11(P, texts):
    out = []
    for t in texts:
        r = P.search(t)
        out.append((P.whole(t), (r[0], r[1]) if r else None, tuple(P.findall(t))))
    return out


def diff11(P, Q, texts):
    a, b = ans11(P, texts), ans11(Q, texts)
    return tuple(sum(1 for x, y in zip(a, b) if x[k] != y[k]) for k in range(3))


def texts11(alpha, n):
    out = [""]
    for _ in range(n):
        out = out + [t + c for t in out if len(t) == len(out[-1]) for c in alpha]
    return sorted(set(out), key=lambda t: (len(t), t))


DOCS11 = {f_: NOWS[f_] for f_ in DOCF}                       # noqa: F821  the documents as read now
BASES11 = ("core.md", "library.md", "parked.md")


# ================================================================== the checks
unit11("CANARY", "the control is predfix90's engine: X11 off runs the starting spelling and refuses the new one; X11 on "
       "the reverse")
CAN11 = [("/(?<h>\\d)?x/ & (h: !<5)", "/(?<h>\\d)?x/ & (h: ~<5)"), ("/(?<h>\\d)?x/ & NOT (h: <5)", "/(?<h>\\d)?x/ & !(h: <5)"),
         ("/(?:(?<d>\\d),)+/ & some((d: \"7\"))", "/(?:(?<d>\\d),)+/ & some(@d, \"7\")")]
can_rows = []
TX11 = texts11("17x,", 4)
for old_, new_ in CAN11:
    X11[0] = False
    Po, eo = run11(old_)
    Pn_off, _ = run11(new_)
    X11[0] = not s11("q1")
    Pn, en = run11(new_)
    Po_on, _ = run11(old_)
    X11[0] = True
    d_ = diff11(Po, Pn, TX11) if Po is not None and Pn is not None else None
    can_rows.append((old_, new_, Po is not None, Pn_off is None, Pn is not None, Po_on is None, d_))
    print("   %s -> %s: off runs old %s, refuses new %s; on runs new %s, refuses old %s; answers differ %s" % (
        old_, new_, Po is not None, Pn_off is None, Pn is not None, Po_on is None, d_))
check("CANARY", all(r[2] and r[3] and r[4] and r[5] and r[6] == (0, 0, 0) for r in can_rows),
      "%d canaries over %d texts: each flips with X11 and answers alike" % (len(can_rows), len(TX11)))

unit11("TR11", "the front end's rules, each a row: the new spelling, and the engine spelling or the refusal it names")
TRT11 = [  # (program, bindings, want: the engine text, or "ERR:" + a fragment of the message)
    ("/(?<h>\\d)?x/ & !(h: <5)", [], "/(?<h>\\d)?x/ & NOT (h: <5)"),
    ("/(?<h>\\d)?x/ & (h: ~<5)", [], "/(?<h>\\d)?x/ & (h: !<5)"),
    ("/\\d+/ & ~/7\\d*/", [], "/\\d+/ & !/7\\d*/"),
    ("/\\d/ SEQ !^/x/", [], "/\\d/ SEQ /(?!${/x/})/"),
    ("^/\\d/ SEQ /\\w/", [], "/(?=${/\\d/})/ SEQ /\\w/"),
    ("!peek(/\\d/)", [], "/(?!${/\\d/})/"),
    ("/x/ & !!(h: <5)", [], "/x/ & (h: <5)"),
    ("some(@d, \"7\")", [], "some((d: \"7\"))"),
    ("every(@d, \"7\")", [], "occurs.none((d: !\"7\"))"),
    ("count(@d)", [], "count((d: anything))"),
    ("occurs.exactly(2, @d, \"7\")", [], "(count((d: \"7\")): ==2)"),
    ("rx.digit{2,4}?", [], "/(?:${rx.digit}){2,4}?/"),
    ("rx.digit{,3}", [], "/(?:${rx.digit}){0,3}/"),
    ("rx.digit{2,4}+", [], "/(?>(?:${rx.digit}){2,4})/"),
    ("/(?<h>\\d)/ & (h: <5){2}", [], "ERR:a quantifier on a condition"),
    ("m.b", ["m := {a = /x/, b = /y/}"], "(/y/)"),
    ("m[\"b\" | 1]", ["m := {a = /x/, b = /y/}"], "([b = /y/] | [a = /x/])"),
    ("m[\"z\"]", ["m := {a = /x/, b = /y/}"], "/\\b\\B/"),
    ("\"a\\x{41}\"", [], "/aA/"),
    ("/\\d+/ & !/7\\d*/", [], "ERR:`~/7\\d*/`"),
    ("/\\d+/ & !/7\\d*/", [], "ERR:`!^/7\\d*/`"),
    ("/(?<h>\\d)/ & (h: !(<5 | >8))", [], "ERR:`~(<5 | >8)`"),
    ("/(?<h>\\d)/ & ~(h: <5)", [], "ERR:`!(h: <5)`"),
    ("\"x\" SEQ ^~/\\d/", [], "ERR:`!^/\\d/`"),
    ("/x/ & NOT (h: <5)", [], "ERR:`NOT` is no spelling"),
    ("some((d: \"7\"))", [], "ERR:`some(@d, S)`"),
    ("some(@h, \"5\", @m)", [], "ERR:one array per call"),
    ("rx.digit{}", [], "ERR:`x*` is the spelling"),
    ("rx.digit{,}", [], "ERR:`x*` is the spelling"),
    ("rx.digit{_,3}", [], "ERR:leaving it out"),
    ("\"a\\d\"", [], "ERR:`/\\d/`"),
    ("\"a\\x41\"", [], "ERR:`\\x{..}`"),
    ("\"a\nb\"", [], "ERR:line"),
    ("\"ab\" \"cd\"", [], "ERR:adjacent"),
    ("m", ["m := {a = /x/, /y/}"], "ERR:no label"),
    ("m", ["m := {1 = /x/}"], "ERR:numeral"),
    ("m.z", ["m := {a = /x/, b = /y/}"], "ERR:no member"),
    ("R(x, A)", ["A := /(?<h>\\d)/", "R(l, v) := /${[l = v]}xx/"], "ERR:marked `l:`"),
    ("A(x)", ["A(l) := /(?<:${l}>\\d+)/"], "ERR:marked `l:`"),
    ("R(x:, A)", ["A := /(?<h>\\d)/", "R(l:, v) := /${[l = v]}xx/"], "R(x:, A)"),
]
tr_bad = []
for e_, b_, want in TRT11:
    try:
        got = TR11.tr_prog(e_, b_)[0]
    except TR11.TrError as ex:
        got = "ERR:" + str(ex)
    ok_ = (want.startswith("ERR:") and got.startswith("ERR:") and want[4:] in got) or got == want
    print("   %s `%s` %s -> %s" % ("ok " if ok_ else "BAD", e_, b_ or "", got[:150]))
    if not ok_:
        tr_bad.append((e_, want, got[:100]))
check("TR11", not tr_bad, "%d rows; wrong: %s" % (len(TRT11), tr_bad or "none"))

unit11("CENSUS11", "review r109 F14: every printed `!` and `~` outside rx text and strings in the base files, classed by "
       "its operand; `NOT` never printed as an operator")
CENS_ALLOW11 = {"!foo": "the text `/!foo/` matches", "!(<5 | >8)": "the error example the bullet describes"}
META11 = re.compile(r"^(?:[A-Z]|[a-z]|test|cond|\(cond\)|\^?[A-Z]|\^test|\^x|\^T|X\b.*)$")
if s11("q3"):
    DOCS11["core.md"] = DOCS11["core.md"].replace("`!(h ?: S)` is h present", "`NOT (h ?: S)` is h present", 1)
cen = {}
cen_bad = []
for f_ in BASES11:
    fence = False
    for ln_, L_ in enumerate(DOCS11[f_].split("\n"), 1):
        if L_.startswith(("```", "~~~")):
            fence = not fence
        if fence:
            continue
        errline = "modes: a compile error" in L_
        for sp in re.findall(r"`([^`]+)`", L_):
            i_ = 0
            while i_ < len(sp):
                c_ = sp[i_]
                if c_ == "/" and TR11._rx_start(sp, i_):
                    try:
                        i_ = TR11._rx_end(sp, i_)
                    except TR11.TrError:
                        break
                    continue
                if c_ in "\"'":
                    try:
                        i_ = TR11._str_end(sp, i_)
                    except TR11.TrError:
                        break
                    continue
                if re.match(r"NOT\b", sp[i_:]) and (i_ == 0 or not sp[i_ - 1].isalnum()):
                    cen_bad.append((f_, ln_, sp, "NOT"))
                    cen["NOT"] = cen.get("NOT", 0) + 1
                if c_ in "!~" and not sp.startswith("!=", i_):
                    try:
                        j_ = TR11._operand(sp, i_ + 1)
                        a_ = sp[i_ + 1:j_].strip()
                    except Exception:                        # noqa: BLE001
                        a_ = sp[i_ + 1:].strip()
                    if i_ + 1 >= len(sp) or sp[i_ + 1] in " ;,)!" or (sp[i_ + 1].isdigit() and c_ == "!"):
                        cls = "%s a character of a text" % c_
                    elif i_ >= 2 and sp[i_ - 2:i_] in ("(?", "?<"):
                        cls = "%s in PCRE group syntax outside slashes" % c_
                    elif sp in CENS_ALLOW11:
                        cls = "%s in a declared span (%s)" % (c_, CENS_ALLOW11[sp])
                    elif not a_:
                        cls = "%s alone (the operator named)" % c_
                    elif errline:
                        cls = "%s in a compile-error line" % c_
                    elif META11.match(a_):
                        cls = "%s on a meta-variable" % c_
                    else:
                        k_ = TR11.kind(a_)
                        cls = "%s on a %s" % (c_, k_)
                        if (c_ == "!") != (k_ == "test"):
                            cen_bad.append((f_, ln_, sp, cls))
                    cen[cls] = cen.get(cls, 0) + 1
                i_ += 1
for k_ in sorted(cen):
    print("   %-40s %d" % (k_, cen[k_]))
for x_ in cen_bad:
    print("   BAD %s:%d `%s` %s" % x_)
check("CENSUS11", not cen_bad and cen.get("! on a test", 0) > 0 and cen.get("~ on a set or pattern", 0) > 0,
      "%d printed operators classed; `!` on a set or pattern, `~` on a test, or `NOT`: %d" % (sum(cen.values()),
                                                                                              len(cen_bad)))


def sw11(docs):
    """Every printed three-mode line: key -> [(file, line, status, run answers, printed answers)]."""
    out = {}
    for f, ln, line_, a, pt, tail, field in sweep_lines84(docs):                     # noqa: F821
        if FLAGTAIL.search(tail) or field in SKIP_FIELDS:                           # noqa: F821
            continue
        st, got = sweep_one(line_, a, pt, tail)                                     # noqa: F821
        out.setdefault(sw_key(f, line_, pt, tail), []).append((f, ln, st, got, strip_annot(a)))   # noqa: F821
    return out


def key11(k):
    """A key read into the engine spelling (the comparison's common ground); unchanged where TR11 refuses."""
    pt, binds = k[0], k[1]
    try:
        e2, b2 = TR11.tr_prog(pt, ["%s := %s" % hb for hb in binds])
    except TR11.TrError:
        return k
    return (e2, tuple(tuple(b.split(" := ", 1)) for b in b2)) + tuple(k[2:])


unit11("SWEEP11", "every printed three-mode line (`rejected:` and history skipped) RUN under the new spelling; the "
       "starting commit's lines under predfix90's engine against these, keyed by the program read into the engine "
       "spelling; every re-spelling whose key moves DECLARED, its printed answers equal")
OLD11 = {f_: _git8("docs/design/predicates/" + f_, START11) for f_ in DOCF}           # noqa: F821
X11[0] = False
OLD_T11 = sw11(OLD11)
X11[0] = True
if s11("q4"):
    NOWS["core.md"] = NOWS["core.md"].replace("Present and outside: WHOLE `x` FAILS", "Present and outside: WHOLE `x` HOLDS", 1)   # noqa: F821
NEW_T11 = sw11(NOWS)                                                                  # noqa: F821
if s11("q4"):
    NOWS["core.md"] = DOCS11["core.md"]                                               # noqa: F821
NEWK11 = {}
for k_, vs in NEW_T11.items():
    NEWK11.setdefault(key11(k_), []).extend(vs)
# RESPELL11, MOVED11, HIST11: the declarations, in the data section above
HISTRX11 = re.compile(r"`NOT` is no spelling|takes the array form|`!` on a set or pattern")
inh11 = set((k_, f_, st_) for k_, vs in OLD_T11.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, used11, cnt11, sw_inh, sw_hist = [], [], [], [], set(), {}, [], []
for k_, vs in NEW_T11.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt11[st_] = cnt11.get(st_, 0) + 1
        if st_ != "same":
            if (key11(k_), f_, st_) in inh11:
                sw_inh.append((f_, ln_, st_, k_[0]))         # the control's own limit, the same key and status
            elif f_.endswith("_details.md") and st_ == "REFUSED" and HISTRX11.search(got_):
                sw_hist.append((f_, ln_, k_[0]))             # a details record in the spelling of its run
            else:
                sw_bad.append((f_, ln_, st_, k_[0], got_[:140]))
for k_, vs0 in OLD_T11.items():
  for f0 in sorted(set(v_[0] for v_ in vs0)):
    vs = [v_ for v_ in vs0 if v_[0] == f0]
    nk = [v_ for v_ in NEWK11.get(k_, []) if v_[0] == f0]
    if nk:
        po = sorted(set(v_[4] for v_ in vs))
        pn = sorted(set(v_[4] for v_ in nk))
        if po != pn and repr(k_[0]) not in MOVED11:
            sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
        continue
    pr_old = vs[0][4]
    rs = RESPELL11.get(k_[0])
    if rs is None and k_[0] in GONE11:
        used11.add(k_[0])
        print("   DROPPED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE11[k_[0]]))
        continue
    if rs is None:
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
        continue
    used11.add(k_[0])
    new_prog, why_ = rs
    hits = [v_ for kk, vv in NEW_T11.items() if kk[0] == new_prog and kk[2:] == k_[2:] for v_ in vv if v_[0] == f0]
    if not hits or any(v_[4] != pr_old for v_ in hits):
        sw_moved.append((vs[0][0], k_[0] + " -> " + new_prog, pr_old[:140], hits[0][4][:140] if hits else "NO LINE"))
stale11 = sorted(k_ for k_ in list(RESPELL11) + list(GONE11) if k_ not in used11)
oldk = set(OLD_T11)
for k_, vs in NEW_T11.items():
    if key11(k_) not in oldk and not any(rs_[0] == k_[0] for rs_ in RESPELL11.values()):
        sw_new.append((vs[0][0], vs[0][1], k_[0]))
for x_ in sw_new:
    print("   ADDED %s:%d `%s`" % x_)
for x_ in sw_gone:
    print("   GONE %s:%d %r (was %s)" % x_)
for x_ in sw_moved:
    print("   MOVED %s %r\n      old: %s\n      now: %s" % x_)
for x_ in sw_bad:
    print("   BAD %s:%d %s `%s`: %s" % x_)
for x_ in sw_inh:
    print("   INHERITED (the control's own, same key and status) %s:%d %s `%s`" % x_)
for x_ in sw_hist:
    print("   A DETAILS RECORD in the spelling of its run %s:%d `%s`" % x_)
for x_ in stale11:
    print("   STALE RE-SPELLING %s" % x_)
for k_, (n_, w_) in sorted(RESPELL11.items()):
    print("   RE-SPELLED `%s` -> `%s`: %s" % (k_, n_, w_))
print("   RX11 FALLBACKS: %d programs (the engine refused, RX11 lowered): %s" % (
    len(set(FALLBACK11)), sorted(set(e_ for e_, _ in FALLBACK11))[:40]))
check("SWEEP11", OLD_T11 and not sw_bad and not sw_moved and not sw_gone and not stale11,
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d, "
      "details records %d); moved %d; gone %d; re-spelled %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T11.values()), ", ".join("%s %d" % kv for kv in sorted(cnt11.items())),
          len(OLD_T11), len(sw_bad), len(sw_inh), len(sw_hist), len(sw_moved), len(sw_gone), len(RESPELL11),
          len(sw_new), len(stale11)))

unit11("ERRSWEEP11", "every printed compile-error line of the base files refused under the new spelling, no crash; "
       "a line the reader cannot read COUNTED; each named form (r109 F5) in the refusal's message")
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),   # noqa: F821
     globals())                                              # noqa: S102  predfold1124's reader, verbatim
if s11("q5"):
    DOCS11["core.md"] = DOCS11["core.md"].replace(
        "`~` on a test: modes: a compile error (", "`~` on a test: modes: a compile error (`/\\d+/ & ~/7\\d*/`; ", 1)
_d8 = dict(D8)                                               # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(DOCS11)                                            # noqa: F821
es_now = [x_ for x_ in err_lines(D8) if not x_[0].endswith("_details.md")]   # noqa: F821
es_seen = set((f_, ln_) for f_, ln_, _, _ in es_now)
es_skip = []
for f_ in BASES11:
    for ln_, L_ in enumerate(D8[f_].split("\n"), 1):          # noqa: F821
        if "modes: a compile error" in L_ and (f_, ln_) not in es_seen:
            es_skip.append((f_, L_.split(": modes:", 1)[0].strip()[:70]))
D8.clear()                                                   # noqa: F821
D8.update(_d8)                                               # noqa: F821
MSG11 = {  # a compile-error line's program -> a fragment its refusal must carry (the form to write)
    "/\\d+/ & !/7\\d*/": "`~/7\\d*/`",
    "/(?<h>\\d)/ & (h: !(<5 | >8))": "`~(<5 | >8)`",
    "/(?<h>\\d)/ & ~(h: <5)": "`!(h: <5)`",
    "\"x\" SEQ ^~/\\d/": "`!^/\\d/`",
    "when(!/x/, /\\w/)": "`!^/x/`",
    "/(?:(?<h>\\d):(?<m>\\d),)+/ & some((h: \"5\", m: \"3\"))": "`some(@d, S)`",
    "/(?<h>\\d);(?:(?<h>\\d);)*/ & some(($h: \"7\"))": "`some(@d, S)`",
    "/(?<h>\\d);(?:(?<h>\\d);)*/ & some((h ?: \"7\"))": "`some(@d, S)`",
    "\"a\\d\"": "`/\\d/`",
    "rx.digit{}": "`x*`",
    "m": "no label",
    "m.z": "no member",
    "R(x, A)": "marked `l:`",
    "A(x)": "marked `l:`",
}
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG11 and MSG11[e_] not in err:
        es_msg.append((e_, MSG11[e_], err[:120]))
    print("   %s:%d `%s` %s: %s" % (f_, ln_, e_, b_ or "", (err or "LEGAL")[:110]))
msg_unseen = sorted(set(MSG11) - set(e_ for _, _, e_, _ in es_now))
for x_ in es_skip:
    print("   SKIPPED (the reader cannot read it) %s `%s`" % x_)
check("ERRSWEEP11", es_now and not es_bad and not es_msg and not msg_unseen,
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s; skipped (unread, counted) %d" % (len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none",
                                                 len(es_skip)))

unit11("GROUP11", "array-argument: the group questions over the array, against each other and against a direct "
       "reading of the settings (WHOLE)")
GP11 = "/(?:(?<d>\\d)?,)+/"
GT11 = texts11("17,", 5)


def g_direct(t, q):
    if not re.fullmatch(r"(?:\d?,)+", t):
        return False
    st = re.findall(r"\d", t)
    return {"some": "7" in st, "none": "7" not in st, "every": all(x == "7" for x in st)}[q]


g_rows = []
for a_, b_ in (('!some(@d, "7")', 'occurs.none(@d, "7")'), ('every(@d, "7")', 'occurs.none(@d, ~"7")')):
    Pa, ea = run11(GP11 + " & " + a_)
    Pb, eb = run11(GP11 + " & " + b_)
    g_rows.append((a_, b_, diff11(Pa, Pb, GT11) if Pa and Pb else (ea, eb)))
for q_, e_ in (("some", 'some(@d, "7")'), ("none", '!some(@d, "7")'), ("every", 'every(@d, "7")')):
    P_, _ = run11(GP11 + " & " + e_)
    bad_ = sum(1 for t in GT11 if P_.whole(t) != g_direct(t, q_)) if P_ else -1
    g_rows.append((e_, "the direct reading", bad_))
Pc, _ = run11(GP11 + " & " + 'occurs.none(@d, "7")')
Pe, _ = run11(GP11 + " & " + 'occurs.none(@d, ~"7")')
g_ctl = diff11(Pc, Pe, GT11)
for r_ in g_rows:
    print("   %s against %s: %s" % r_)
print("   control: occurs.none(@d, \"7\") against occurs.none(@d, ~\"7\"): %s (the comparison can see a difference)" %
      (g_ctl,))
check("GROUP11", all(r_[2] in ((0, 0, 0), 0) for r_ in g_rows) and g_ctl != (0, 0, 0),
      "%d texts over `17,`: %d comparisons agree; control differs %s" % (len(GT11), len(g_rows), g_ctl))

unit11("BRACES", "brace-counts: each count against python `re` on the regex written from the ruled line")
BT11 = texts11("12a", 5)
BR11 = [("rx.digit{2,4}", r"\d{2,4}"), ("rx.digit{2,4}?", r"\d{2,4}?"), ("rx.digit{2,4}+", r"(?>\d{2,4})"),
        ("rx.digit{3}", r"\d{3}"), ("rx.digit{3,}", r"\d{3,}"), ("rx.digit{,2}", r"\d{0,2}"),
        ("rx.digit{0}", r"\d{0}"), ("rx.digit{ 2 , 4 }", r"\d{2,4}"), ('"a" SEQ rx.digit{2}', r"a\d{2}"),
        ('("a" SEQ rx.digit){2}', r"(?:a\d){2}")]
b_rows = []
for e_, rx_ in BR11:
    P_, err_ = run11(e_)
    b_rows.append((e_, rx_, diff11(P_, Re(rx_), BT11) if P_ else err_))     # noqa: F821
    print("   `%s` against `%s`: %s" % b_rows[-1])
check("BRACES", all(r_[2] == (0, 0, 0) for r_ in b_rows), "%d counts over %d texts" % (len(b_rows), len(BT11)))

unit11("STRINGS", "string-literals: each string against python `re` on `re.escape` of its characters")
ST11 = texts11('ab"\nA$', 3)
STR11 = [('"a.b"', re.escape("a.b")), ("'a\"b'", re.escape('a"b')), ('"a\\"b"', re.escape('a"b')),
         ('"\\x{41}b"', "Ab"), ('"a\\nb"', "a\nb"), ('"a\\\\b"', re.escape("a\\b")), ('""', ""),
         ('"${a}"', re.escape("${a}")), ('"ab" SEQ "ab"', "abab")]
s_rows = []
for e_, rx_ in STR11:
    P_, err_ = run11(e_)
    s_rows.append((e_, rx_, diff11(P_, Re(rx_), ST11) if P_ else err_))     # noqa: F821
    print("   `%s` against `%s`: %s" % s_rows[-1])
check("STRINGS", all(r_[2] == (0, 0, 0) for r_ in s_rows), "%d strings over %d texts" % (len(s_rows), len(ST11)))

unit11("MAP11", "map-creator: a map as a pattern, its members and its selection, against python `re` on the "
       "alternation of the elements in the order each line rules")
MB11 = ["m := {a = /\\d/, b = /\\d\\d/, c = /x/}"]
MT11 = texts11("12x", 4)
MP11 = [("m", r"\d|\d\d|x"), ("m.b", r"\d\d"), ('m["b" | 1]', r"\d\d|\d"), ('m[1 | "b"]', r"\d|\d\d"),
        ('m["a" | "a"]', r"\d"), ("m[3]", "x"), ('m["z"] | "x"', "x")]
m_rows = []
for e_, rx_ in MP11:
    P_, err_ = run11(e_, MB11)
    m_rows.append((e_, rx_, diff11(P_, Re(rx_), MT11) if P_ else err_))     # noqa: F821
    print("   `%s` against `%s`: %s" % m_rows[-1])
Pk1, _ = run11('m["b" | 1]', MB11)
Pk2, _ = run11('m[1 | "b"]', MB11)
m_ctl = diff11(Pk1, Pk2, MT11)
print("   control: the two key orders differ %s (the key's order is visible)" % (m_ctl,))
check("MAP11", all(r_[2] == (0, 0, 0) for r_ in m_rows) and m_ctl != (0, 0, 0),
      "%d selections over %d texts; the key orders differ %s" % (len(m_rows), len(MT11), m_ctl))

unit11("READINGS11", "the manager's readings marked \"for the fold to test\" in the 2026-11-25 and 2026-11-27 entries, "
       "each RUN: SUPPORTED, NOT SUPPORTED, or UNTESTABLE with its reason")
RD11 = []


def rd(name, ok, detail):
    RD11.append((name, ok, detail))
    print("   %s %s: %s" % ({True: "SUPPORTED", False: "NOT SUPPORTED", None: "UNTESTABLE"}[ok], name, detail))


HST11 = [""] + [str(d) for d in range(10)]                   # h absent, or one digit


def hold(e_, h_):
    P_, _ = run11("/(?<h>\\d)?x/ & " + e_)
    return P_.whole(h_ + "x")


def ref_h(h_, q):
    v = None if h_ == "" else int(h_)
    if s11("q10") and q == "abs_or_out":
        q = "pres_out"
    return {"pres_out": v is not None and not v < 5, "abs_or_out": v is None or not v < 5}[q]


r1 = sum(hold("(h: ~<5)", h_) != ref_h(h_, "pres_out") for h_ in HST11)
r2 = sum(hold("(h ?: ~<5)", h_) != ref_h(h_, "abs_or_out") for h_ in HST11)
r3 = sum(hold("!(h: <5)", h_) != hold("(h ?: ~<5)", h_) for h_ in HST11)
r4 = sum(hold("!(h ?: <5)", h_) != hold("(h: ~<5)", h_) for h_ in HST11)
r5 = sum(hold("!(h: <5)", h_) != hold("(h: ~<5)", h_) for h_ in HST11)
rd("complement: `(h: ~S)` is present and outside", r1 == 0, "%d of 11 states differ" % r1)
rd("complement: `(h ?: ~S)` is absent or outside", r2 == 0, "%d of 11 states differ" % r2)
rd("complement: `!(h: S)` equals `(h ?: ~S)`", r3 == 0, "%d of 11 states differ" % r3)
rd("optional-entry (c): `!(h ?: S)` equals `(h: ~S)`", r4 == 0, "%d of 11 states differ" % r4)
rd("control: `!(h: S)` and `(h: ~S)` part on the absent state", r5 == 1, "%d of 11 states differ" % r5)
Pr, _ = run11("/(?<a>\\d)?,(?<b>\\d)?/ & !(a: <5, b: >=3)")
r6 = 0
for a_ in [""] + [str(d) for d in range(10)]:
    for b_ in [""] + [str(d) for d in range(10)]:
        va, vb = (None if a_ == "" else int(a_)), (None if b_ == "" else int(b_))
        want = (va is None or not va < 5) or (vb is None or not vb >= 3)
        r6 += Pr.whole(a_ + "," + b_) != want
rd("a record stays a product of sets: `!(a: S, b: T)` = `(a ?: ~S) | (b ?: ~T)`", r6 == 0, "%d of 121 states differ" % r6)
Pc1, ec1 = run11('"x" SEQ ^~/\\d/')
rd("`!^A` cannot be written `^~A` (a compile error naming `!^A`)", Pc1 is None and "`!^/\\d/`" in (ec1 or ""), ec1)
TXA = texts11("x1", 5)
pos_l = sum(1 for t in TXA for i in range(len(t) + 1) if re.match(r"x", t[i:]))
pos_n = sum(1 for t in TXA for i in range(len(t) + 1) if re.match(r"x(?!\d)", t[i:]))
rd("a lookahead for a complement is nearly always true (the PROPOSAL's run 4, re-run)", pos_l != pos_n,
   "`x` then a stretch outside `\\d` (the empty one always is) holds at %d positions, `x(?!\\d)` at %d" % (pos_l, pos_n))
Pw1, ew1 = run11("when(!/x/, /\\w/)", [WHEN11])
rd("`when(!x, z)` on a bare pattern is an error by line 4", Pw1 is None and "`!^/x/`" in (ew1 or ""), ew1)
TW = texts11("12x", 4)
Pw2, _ = run11("when(/\\d/, /\\d\\d/, else = /\\w/)", [WHEN11])
Pw3, _ = run11("when(^/\\d/, /\\d\\d/, else = /\\w/)", [WHEN11])
d2 = diff11(Pw2, Re(r"\d\d\d|(?!\d)\w"), TW)               # noqa: F821
d3 = diff11(Pw3, Re(r"(?=\d)\d\d|(?!\d)\w"), TW)           # noqa: F821
rd("a bare `when` test consumes", d2 == (0, 0, 0), "against `\\d\\d\\d|(?!\\d)\\w`: %s" % (d2,))
rd("r109: one `when` body serves both kinds of test", d2 == d3 == (0, 0, 0), "lookahead test against "
   "`(?=\\d)\\d\\d|(?!\\d)\\w`: %s; bare test %s" % (d3, d2))
Pp1, _ = run11("!peek(/\\d/) SEQ /\\w/")
dp = diff11(Pp1, Re(r"(?!\d)\w"), TW) if Pp1 else "refused"   # noqa: F821
rd("drop-not's `!peek(A)` error is gone", dp == (0, 0, 0), "`!peek(/\\d/) SEQ /\\w/` against `(?!\\d)\\w`: %s" % (dp,))
Pn1, _ = run11("/\\d+/ & not_seven", ["not_seven := ~seven", "seven := /7\\d*/"])
Pn2, _ = run11("/\\d+/ & ~/7\\d*/")
dn = diff11(Pn1, Pn2, texts11("17x", 4))
rd("complement-place carries over under `~` (`not_seven := ~seven`)", dn == (0, 0, 0), "%s" % (dn,))
Pq1, _ = run11("~/7\\d*/ & /\\d+/")
dq = diff11(Pq1, Pn2, texts11("17x", 4))
rd("prefix on ONE atom: `~A & B` is `(~A) & B`, the answers of `B & ~A`", dq == (0, 0, 0), "%s" % (dq,))
Pq2, _ = run11("/\\d+/ & ~(/7\\d*/ | /8\\d*/)")
Pq3, _ = run11("/\\d+/ & ~/7\\d*/ & ~/8\\d*/")
dq2 = diff11(Pq2, Pq3, texts11("178", 4))
rd("`~B & ~C` is `~(B | C)` as filters (the PROPOSAL's run 3)", dq2 == (0, 0, 0), "%s" % (dq2,))
Pa1, ea1 = run11('/(?:(?<d>\\d),)+/ & some((d: "7"))')
rd("array-argument (a): a condition as the argument names the array form", Pa1 is None and "`some(@d, S)`" in (ea1 or ""), ea1)
rd("array-argument (b): the array mark on a path a placeholder", None, "a spelling, for the spellings review")
Pc2, _ = run11("/(?:(?<h>\\d)(?<m>\\d),)+/ & some(@h, $m)")
def last_m(t):
    ps = re.findall(r"(\d)(\d),", t)
    return bool(re.fullmatch(r"(?:\d\d,)+", t)) and any(h_ == ps[-1][1] for h_, _ in ps)


rc = sum(Pc2.whole(t) != last_m(t) for t in texts11("12,", 6))
rd("array-argument (c): the set may read a label as it stands", rc == 0, "against a direct reading (the last pass's "
   "m against every h) of the lines 'A read inside': %d differ" % rc)
Pd1, ed1 = run11('/x/ SEQ /(?:(?<d>\\d),)*/ & !some(@d, "7")')
rd("array-argument (d): the question is a test, taking `!`", Pd1 is not None, ed1 or "legal")
Pe1, ee1 = run11('/(?<d>\\d)+/ & some(@0, "1")')
rd("array-argument (e): `@0` is a compile error", Pe1 is None, ee1)
rd("array-argument (f): the array's scope unchanged", None, "the scope lines re-run in SWEEP11")
Pg1, eg1 = run11('/(?<h>\\d)?x/ & some(@h, capture("h"))')
rd("array-argument (g): a capture request as the set is refused", Pg1 is None, eg1)
Ph1, _ = run11('/(?:(?<d>\\d),)*x/ & every(@d, "7")')
Ph2, _ = run11('/(?:(?<d>\\d),)*x/ & some(@d, "7")')
rd("array-argument (h): on an empty array `every` holds and `some` fails", Ph1.whole("x") and not Ph2.whole("x"),
   "on `x`: every %s, some %s" % (Ph1.whole("x"), Ph2.whole("x")))
rd("array-argument (i): the occurs parameter order a placeholder", None, "a spelling")
for k_, why_ in (("brace-counts (d): a match-time count `x{$n}` under construction", "TR11 reads constant counts only"),
                 ("map-creator (a): the literal's spelling a placeholder; `[a = A | b = B]` unenforced", "a spelling"),
                 ("map-creator (b): the accessor on any pattern with labels", "TR11 selects on map literals only"),
                 ("map-creator (c): a bare name in the brackets a binding's value", "TR11 lists string and numeral keys"),
                 ("map-creator (d): a one-name result not renumbered", "`.index` on a selection: no engine field"),
                 ("map-creator (f): `X[0]` the whole rx", "TR11 has no position 0"),
                 ("map-creator (g): a name on a plain unlabelled array finds nothing", "TR11 selects on map literals"),
                 ("string-literals (c, second half): a code a character or a byte", "the encoding question"),
                 ("string-literals (e): the weak `i` reaches a string, `x` never", "lib/builtin/options' own runs"),
                 ("string-literals (f): a string used as a name, the same syntax", "no name position in the engine")):
    rd(k_, None, why_)
Pm1, _ = run11('m["z"] | "x"', MB11)
rd("map-creator (e): the empty selection is the never-matching pattern", diff11(Pm1, Re("x"), MT11) == (0, 0, 0),   # noqa: F821
   "against `x`")
Pm2, _ = run11('m["a" | "a"]', MB11)
rd("map-creator (i): the same result twice matches as once", diff11(Pm2, Re(r"\d"), MT11) == (0, 0, 0), "against `\\d`")   # noqa: F821
Ps1, _ = run11('"${x}"')
rd("string-literals (a): `${` in a string is plain characters", Ps1.whole("${x}") and not Ps1.whole("x"), "")
for k_, e_ in (("string-literals (b): a raw line end a compile error", '"a\nb"'),
               ("string-literals (c): `\\x41` a compile error", '"\\x41"'),
               ("brace-counts (c): `_` inside the braces a compile error for now", "rx.digit{_,3}"),
               ("brace-counts: braces on a condition a compile error", "/(?<h>\\d)/ & (h: <5){2}")):
    P_, e2_ = run11(e_)
    rd(k_, P_ is None, e2_)
Ps2, _ = run11('""')
rd("string-literals (d): `\"\"` the empty text", Ps2.whole("") and not Ps2.whole("a"), "")
Ps3, _ = run11('"ab" SEQ "cd"')
rd("string-literals (g): `\"ab\" SEQ \"cd\"` the one string", diff11(Ps3, Re("abcd"), texts11("abcd", 4)) == (0, 0, 0), "")   # noqa: F821
for k_ in ("brace-counts (a)", "brace-counts (b)", "brace-counts (e)"):
    rd(k_, all(r_[2] == (0, 0, 0) for r_ in b_rows), "BRACES")
rd("drop-not (b) of 2026-11-25: a complement filling a lookaround hole flips it", None,
   "retired by bang-split: `!^A` is written; no complement in a hole")
check("READINGS11", all(ok_ is not False for _, ok_, _ in RD11),
      "%d readings: SUPPORTED %d, NOT SUPPORTED %d, UNTESTABLE %d" % (
          len(RD11), sum(1 for x_ in RD11 if x_[1] is True), sum(1 for x_ in RD11 if x_[1] is False),
          sum(1 for x_ in RD11 if x_[1] is None)))

unit11("SPECLINES", "every new printed line of this fold RUN from its program and texts, formatted, and found in its "
       "piece by DOC11")
LINES.clear()                                                # noqa: F821
spec_bad = []
for sid, tag, lab, p_, bs, wh, sr, fa in SPEC11:
    binds = [b for b in bs.split(" || ") if b]
    P_, err_ = run11(p_, ([WHEN11] if "when(" in p_ else []) + binds)
    if P_ is None:
        spec_bad.append((sid, err_))
        continue
    L_ = "%s%s (`%s`%s)" % ((lab + ": ") if lab else "", fmt(P_, wh.split("|"), sr, fa), p_, bt(binds))   # noqa: F821
    LINES.append((tag, L_))                                  # noqa: F821
    print("   [%s] %s" % (tag, L_[:200]))
check("SPECLINES", not spec_bad and len(LINES) == len(SPEC11), "%d lines run; refused: %s" % (len(LINES), spec_bad or "none"))   # noqa: F821

unit11("GRID", "predfix90's name grid, its section run verbatim under the new spelling")
if s11("q11"):
    _k11 = sorted(GRULE)[0]                                  # noqa: F821
    GRULE[_k11] = (GRULE[_k11][0], GRULE[_k11][1] + " (planted)")   # noqa: F821
GPATCH11 = {"sent": ("core/labels/rule/sent-label-wall", "a caller's read through the sent label past the blank is a "
                     "compile error")}               # DECLARED: R-1 ruled the reading; its pinned words moved
for k_, v_ in GPATCH11.items():
    print("   PATCH GRULE[%s]: %r -> %r (R-1, sent-label-wall ruled)" % (k_, GRULE[k_], v_))   # noqa: F821
    GRULE[k_] = v_                                           # noqa: F821
_gsrc = _src10[_src10.index('unit10("GRID", '):_src10.index('unit10("READINGS10", ')]
exec(compile(_gsrc, P90, "exec"), globals())                 # noqa: S102  predfix90's GRID, verbatim

unit11("SUCCESSOR11", "every in-force model re-run: predfix90 (LIGHT: its SUCCESSOR re-runs the same list), "
       "predfold1124, and through predfix88's runner predfix88 and the fourteen before it; each red DECLARED by a key "
       "with no document line numbers (predfix90's classes: CRASH, MISSING, LINE); a traceback never")
exec(compile(_src10[_src10.index("CRASH10 = re.compile("):_src10.index("succ_bad, succ_n, succ_t, succ_seen = ")], P90,
             "exec"), globals())                             # noqa: S102  predfix90's red key, verbatim
PINS11 = dict(PINS8)                                         # noqa: F821  predfix90's pins, as its SUCCESSOR10 sets them
PINS11["predfix88"] = "50a39f8e4"
ORDER11 = ["predfix90", "predfold1124", "predfix88"] + list(PINS8)   # noqa: F821
DECLF11 = os.path.join(HERE11, "predfold1125_succ_decl.tsv")
SDECL11 = {}
if os.path.exists(DECLF11):
    for l_ in builtins.open(DECLF11, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SDECL11.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s11("q12") and SDECL11:
    _m = sorted(SDECL11)[0]
    _r = sorted(SDECL11[_m])[0]
    SDECL11[_m][_r] = (SDECL11[_m][_r][0], SDECL11[_m][_r][1] + " planted", SDECL11[_m][_r][2])
DUMP11 = os.environ.get("PREDFOLD1125_SUCCDUMP", "")
READDUMP11 = os.environ.get("PREDFOLD1125_READDUMP") == "1"
succ_bad, succ_n, succ_t, succ_seen = [], 0, {}, []
if not LIGHT11 or READDUMP11:
    for mname in ORDER11:
        t0 = time.time()
        if READDUMP11 or (os.environ.get("PREDFOLD1125_REUSE") == "1" and DUMP11 and
                          os.path.exists(os.path.join(DUMP11, mname + ".out"))):
            out = builtins.open(os.path.join(DUMP11, mname + ".out"), encoding="utf-8").read()
        else:
            env = {k: v for k, v in os.environ.items() if not k.endswith(("_SABOTAGE", "_ENGINE", "_PROBE", "_LIGHT",
                                                                           "_DUMPSUCC", "_SUCCDUMP", "_READDUMP"))}
            for v_ in list(LIGHTENV8.values()) + ["PREDFIX88_LIGHT", "PREDFOLD1124_LIGHT", "PREDFIX90_LIGHT"]:   # noqa: F821
                env[v_] = "1"
            cmd = [sys.executable, "-I", "-B", P90 if mname == "predfix90" else P1124] \
                if mname in ("predfix90", "predfold1124") else \
                [sys.executable, "-I", "-B", P88, "--succ", os.path.join(LANES11, mname + "_evidence",   # noqa: F821
                                                                          mname + "_model.py"), PINS11[mname]]
            try:
                out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                                     timeout=1200).stdout
            except subprocess.TimeoutExpired:
                out = "TIMEOUT: model %s did not finish in 1200 s" % mname
            if DUMP11:
                builtins.open(os.path.join(DUMP11, mname + ".out"), "w", encoding="utf-8").write(out)
        succ_t[mname] = time.time() - t0
        succ_n += 1
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x_.startswith("Traceback") for x_ in lines_):
            for r in [x_.strip() for x_ in (mm.group(3) or "").split(",") if x_.strip()]:
                fl_ = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                            re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
                reds[r] = red_key10(r, lines_, fl_)          # noqa: F821
        else:
            reds["TRACEBACK"] = ("TRACEBACK", last)
        decl = SDECL11.get(mname, {})
        print("   %-13s (%.1f s) last line: %s" % (mname, succ_t[mname], last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            succ_seen.append((mname, r, cls_, key_))
            d = decl.get(r)
            if r == "TRACEBACK":
                succ_bad.append((mname, "TRACEBACK"))
                print("      TRACEBACK (never declarable): %s" % key_[:300])
            elif d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s UNDECLARED (%s): %s" % (r, cls_, key_[:600]))
            elif d[0] != cls_ or d[1] != key_:
                succ_bad.append((mname, r, "KEY CHANGED"))
                print("      %s KEY CHANGED:\n         declared (%s): %s\n         now (%s):      %s" % (
                    r, d[0], d[1][:600], cls_, key_[:600]))
            else:
                print("      %s declared (%s): %s\n         its FAIL line: %s" % (r, cls_, d[2], key_[:400]))
        gone = sorted(set(decl) - set(reds))
        if gone:
            succ_bad.append((mname, "GREEN NOW", gone))
            print("      declared but green now: %s" % gone)
    if os.environ.get("PREDFOLD1125_WRITEDECL"):
        with builtins.open(os.environ["PREDFOLD1125_WRITEDECL"], "w", encoding="utf-8") as fh:
            for m_, r_, c_, k_ in succ_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (m_, r_, c_, SDECL11.get(m_, {}).get(r_, ("", "", "?"))[2], k_))
check("SUCCESSOR11", (LIGHT11 and not READDUMP11) or (succ_n == len(ORDER11) == 17 and not succ_bad),
      "%d models re-run (%.0f s in all), each red against its declared key (%d declared): %s" % (
          succ_n, sum(succ_t.values()), sum(len(v) for v in SDECL11.values()),
          succ_bad or "every red declared, its key unchanged; no traceback"))

unit11("QUOTES11", "the owner's sentences the new and restated pieces quote, each in the record at the starting "
       "commit AND in its piece; every record title the fold cites, a title")
REC11 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START11)   # noqa: F821
RW11 = ws(REC11)                                             # noqa: F821
if s11("q13"):
    QQ11[0] = (QQ11[0][0] + " (planted)", QQ11[0][1])
q_miss = [(q_[:60], t_) for q_, t_ in QQ11 if ws(q_) not in RW11 or ws(q_) not in ws(piece8(t_))]   # noqa: F821
DET11 = NOWS["core_details.md"] + NOWS["library_details.md"] + NOWS["parked_details.md"]   # noqa: F821
cited = sorted(set(re.findall(r'\(record: "(.*?)"\)', "\n".join(
    l_ for l_ in DET11.split("\n") if "predfold1125" in l_ or "2026-11-25" in l_ or "2026-11-27" in l_))))
heads = [ws(h_) for h_ in re.findall(r"^### (.*)$", REC11, re.M)]
t_miss = [t_[:70] for t_ in cited if not any(h_ == ws(t_) or h_.startswith(ws(t_) + " (") for h_ in heads)]
check("QUOTES11", not q_miss and not t_miss, "%d quoted sentences (missing: %s); %d record titles cited by 2026-11-25/27 "
      "items (not a title: %s)" % (len(QQ11), q_miss or "none", len(cited), t_miss or "none"))

unit11("DOC11", "every line this model formats occurs verbatim in the piece its tag names")
DLN11 = list(LINES)                                          # noqa: F821
if s11("q14") and DLN11:
    DLN11[0] = (DLN11[0][0], DLN11[0][1].replace("WHOLE `", "WHOLE `x", 1))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
d_miss = [(t_, L_) for t_, L_ in DLN11 if ws(L_) not in ws(piece8(t_))]   # noqa: F821
for t_, L_ in d_miss:
    print("   MISSING [%s] %s" % (t_, L_))
check("DOC11", DLN11 and not d_miss, "%d lines, each in its own piece; missing: %d" % (len(DLN11), len(d_miss)))

# ---- the plants, each its own subprocess (LIGHT; SUCCESSOR11's reads the dumped runs)
PLANTS11 = {"q1": "CANARY", "q2": "TR11", "q3": "CENSUS11", "q4": "SWEEP11", "q5": "ERRSWEEP11", "q6": "GROUP11",
            "q7": "BRACES", "q8": "STRINGS", "q9": "MAP11", "q10": "READINGS11", "q11": "GRID", "q12": "SUCCESSOR11",
            "q13": "QUOTES11", "q14": "DOC11"}
if SAB11 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS11.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFOLD1125_SABOTAGE=q_, PREDFOLD1125_LIGHT="1")
        if q_ == "q12":
            env["PREDFOLD1125_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY11], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=1800)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS11", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))

failed11 = [n_ for n_, ok_ in RESULTS if not ok_]
print("predfold1125_model: %d checks, %d failed%s" % (len(RESULTS), len(failed11),
                                                     (" (%s)" % ", ".join(failed11)) if failed11 else ""))
sys.exit(1 if failed11 else 0)
