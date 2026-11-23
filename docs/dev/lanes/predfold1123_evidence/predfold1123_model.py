#!/usr/bin/env python3
# Lane predfold1123 (2026-11-23): the successor evidence model for the fold of the owner's rulings of 2026-11-22
# (late) and 2026-11-23 into the predicate documents (the record entries from "2026-11-22 OWNER, a question on
# transform-export" through "2026-11-23 OWNER RULING — binding-fixed"). DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predfix84's model is LOADED unchanged: predfix84_model.py is executed up to its line "the checks" (the
# LABEL engine and the FLAG engine of predspot, with predfix84's fixes). Then the FOLD extensions below act, each
# switched by FOLD[0] (on for the documents now, off for the starting commit's documents: SWEEP's control):
#   ARGLABEL  argument-label (ruled): a label the caller writes in its own text inside an argument (a part label, a
#             group of an in-place literal) is the caller's own: predspot's TEMPLATE and OWNTEXT moves are OFF.
#             The ruled error `B(A) & (A.d: ..)` (the body using its argument alone) is untouched (predfix83's relocate).
#   LABELONLY the label-only group `(?<:x>...)` anywhere in rx text is a label (no capture): lowered as a named group
#             (a capture changes no match).
#   LABELPARAM the label parameter (his tentative direction; label-parameter-omitted, -default, label-kinds,
#             label-forward ruled): a macro whose head marks a parameter `l:` (or `l = d:`) is EXPANDED where it is
#             called, mechanically from its body text: the caller's marked name (`x:`) is written where the body
#             writes `l` (the name of a label-only group `(?<:${l}>`, a part label `[l = ..]`, an entry `(l: ..)`,
#             a forwarded `X(l:)`), `_` makes the group plain and the part label `[_ = ..]`; every other parameter
#             is replaced by its argument's text in parentheses. So the label is written in the caller's text.
#             A body that reads a label parameter it never places is refused at the definition (label-kinds); a
#             marked argument that is a path (`l.d:`) is refused at the call; reading `_` is refused at the call.
#             LIMIT: a label-parameter body's OWN fixed group names would become the caller's under expansion: such
#             a body is refused ("not modelled"); no printed body has one.
#   OPTENTRY  the entry `p ?: S` (optional-label, ruled; the operator spelling his lean): holds when p has no value
#             or its value is in S; lowered as `p: OPT{S}` and read by the matcher.
#   CAPTURE   the capture request (the final shape of the day): `capture("n")` right of `:` is `anything` (any
#             present value) with a request; `X & capture("n")` is `X & (0: capture("n"))`. A request under `NOT` or
#             `!` (at any depth of the operand) is refused: capture-negated ("any effect macro cannot be under
#             negation"). The array request is UNBUILT: not modelled, no run is claimed.
#   ZEROBIND  zero-condition-binding (ruled): a binding whose body is a condition on `0` alone is a compile error.
# Checks: CONTROL, ARGLABEL, LABELPARAM, LPRULES, OPTENTRY, CAPTURE, NEGATION, ZEROLOOP, ZEROBIND, PRINCIPLE,
# READINGS (each manager's reading of the range with a run), SWEEP (every printed three-mode line, the starting
# commit's under predfix84's engine against these under this one; every non-same status and every moved answer
# DECLARED), NULLABLE, SUCCESSOR, QUOTES, DOC.
#
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled; NULLABLE fails if any program the checks run has one. Not modelled either (predfix84's list): `U`,
# `xx`, `J`, `r` and the `a`-family in the flag engine; `^` / `$` inside an operand of `&`, `\b`, backreferences to
# a part; a complement inside a hole; `when`; `quoted`; the array capture request.
#
# Run (W = the worktree; any cwd):  timeout 3600 python3 -I -B W/docs/dev/lanes/predfold1123_evidence/predfold1123_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDFOLD_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# PREDFOLD_SABOTAGE=all runs every plant in turn (a subprocess each) and prints the table predfold1123_sabotage.out holds.
# PREDFOLD_LIGHT=1 skips SUCCESSOR (the plant runner sets it for plants not aimed there).
import hashlib
import os
import re
import subprocess
import sys

HEREF = os.path.dirname(os.path.abspath(__file__))
P84 = os.path.join(HEREF, "..", "predfix84_evidence", "predfix84_model.py")
SABF = set(x for x in os.environ.get("PREDFOLD_SABOTAGE", "").split(",") if x)
LIGHTF = os.environ.get("PREDFOLD_LIGHT") == "1"
STARTF = "e420369c5"                                         # this lane's starting commit (lane/pred-rev28)
for v in list(os.environ):
    if v.endswith("_SABOTAGE") or v.endswith("_ENGINE") or v.endswith("_LIGHT"):
        os.environ.pop(v, None)


def sf(n):
    return n in SABF


PLANTSF = [   # (plant, its target check, what it plants)
    ("s1", "CONTROL", "the control for `identity(A)` widened to `\\d!?`"),
    ("s2", "ARGLABEL", "ARGLABEL off: a label written in an argument is the template's again"),
    ("s3", "ARGLABEL", "the ruled error `B(A) & (A.d: ..)` expected legal"),
    ("s4", "LABELPARAM", "LABELPARAM writes the body's parameter name, not the caller's, on the spot"),
    ("s5", "LPRULES", "the reference kind accepted at the definition (label-kinds off)"),
    ("s6", "LPRULES", "`_` on a sent label's outer spot closes it (the backdoor shut)"),
    ("s7", "OPTENTRY", "`?:` reads an absent left part as failing (the plain `:`)"),
    ("s8", "CAPTURE", "a capture request on an absent label holds (the request read as `?:`)"),
    ("s9", "NEGATION", "a request under `NOT` accepted"),
    ("s10", "ZEROLOOP", "`0` in a loop read from the pass's start"),
    ("s11", "ZEROBIND", "a condition on `0` bound alone accepted"),
    ("s12", "PRINCIPLE", "one use of the looped binding expected to differ from its written-out text"),
    ("s13", "READINGS", "one reading's expected verdict inverted"),
    ("s14", "SWEEP", "one declared moved answer removed"),
    ("s15", "NULLABLE", "a nullable loop added to the programs run"),
    ("s16", "SUCCESSOR", "one declared red removed"),
    ("s17", "QUOTES", "an owner sentence altered"),
    ("s18", "DOC", "a formatted line altered"),
    ("s19", "ARGLABEL", "TWOSRC off: a bare name the caller writes in place reads the body's group (the last mention)"),
    ("s20", "ZEROOPEN", "zero-open off: a group question, an index and a request on an open `0` accepted"),
    ("s21", "ARGSHAPES", "a part label written on an argument not widened to the caller (groups only)"),
    ("s22", "ARGSHAPES", "the label set read tighter than `|` no longer: `[ab = B | A]` labels the whole alternation"),
    ("s23", "ZEROOPEN", "`$0` read as nothing (the hole dropped)"),
]
HEAVYF = {"SUCCESSOR"}
if "all" in SABF:                                            # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTSF:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFOLD_SABOTAGE"] = pn
        if target not in HEAVYF:
            env["PREDFOLD_LIGHT"] = "1"
        r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=env, timeout=3600)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n")
        last = lines[-1]
        fl_ = next((x for x in lines if x.startswith("FAIL %s:" % target)), "")
        tb = any(x.startswith("Traceback") for x in lines)
        ok = bool(fl_) and not tb and r.returncode != 0 and target in last
        notc += not ok
        rows.append((pn, target, what, ok))
        print("%s -> %s (%s): %s" % (pn, target, what, "caught" if ok else "NOT CAUGHT"))
        print("   last line: %s" % last)
        print("   its FAIL line: %s" % fl_[:300], flush=True)
    print("predfold1123_sabotage: %d plants, %d not caught (each plant turned its target check FAIL, no traceback)"
          % (len(rows), notc) if not notc else "predfold1123_sabotage: %d plants, %d not caught" % (len(rows), notc))
    sys.exit(1 if notc else 0)

# ================================================================== the LOADER: predfix84's engines, unchanged
_src84 = open(P84, encoding="utf-8").read()
_cut84 = re.search(r"^# =+ the checks$", _src84, re.M).start()
_fileF = __file__
__file__ = os.path.abspath(P84)                              # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src84[:_cut84], P84, "exec"), globals())       # noqa: S102  (predfix84's definitions, unchanged)
__file__ = _fileF
SAB84.clear()
SABS.clear()
LINES.clear()
RUN.clear()
P84F = dict(prog=prog, parse_value=parse_value, val_ok=val_ok, lower_literal=lower_literal, sweep_one=sweep_one)


def git_showF(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (STARTF, rel)], capture_output=True, text=True,
                          check=True).stdout


OLDF = {f: git_showF("docs/design/predicates/" + f) for f in DOCF}
FOLD = [True]

# ================================================================== the FOLD extensions (lane predfold1123)


# ---- LABELONLY
def lower_literal(rx, ctx):                                  # noqa: F811
    """`(?<:x>...)` that is not predspot's spot form `(?<:x>${param})` is a label: lowered as `(?<x>...)`."""
    if FOLD[0]:
        rx = re.sub(r"\(\?<:(\w+)>(?!\$\{\s*\w+\s*\}\))", r"(?<\1>", rx)
    return P84F["lower_literal"](rx, ctx)


# ---- OPTENTRY and CAPTURE: the set side
CAPREQ = []                   # (label key or "0", the caller's name) of every capture request lowered


def parse_value(v, ctx):                                     # noqa: F811
    v = v.strip()
    if FOLD[0]:
        mm = re.fullmatch(r"OPT\{(.*)\}", v, re.S)
        if mm:
            return ("opt", parse_value(mm.group(1), ctx))
        mm = re.fullmatch(r"DFLT\{([^}]*)\}\{(.*)\}", v, re.S)
        if mm:
            return ("dflt", mm.group(1), parse_value(mm.group(2), ctx))
        if v == "anything":                                  # lib/sets/anything: any text
            return ("anyv",)
        mm = re.fullmatch(r'capture\("(\w+)"\)', v)
        if mm:
            CAPREQ.append(mm.group(1))
            return ("cap", mm.group(1))
        parts = split_top(v, " & ")
        if len(parts) > 1 and any(re.fullmatch(r'capture\("\w+"\)', x) for x in parts):
            return ("all", [parse_value(x, ctx) for x in parts])
        if v.startswith("(") and strip_parens(v) != v and not is_cond(v):
            return parse_value(strip_parens(v), ctx)
        alts = split_top(v, " | ")
        if len(alts) > 1:                                    # a union of sets (an array of sets is an alternation)
            return ("any", [parse_value(x, ctx) for x in alts])
        if v.startswith("!") and not v.startswith("!="):     # a complement right of `:` (core/filters/complement)
            return ("not", parse_value(v[1:], ctx))
        call = parse_call(v)
        if call and call[0] in LIBMACROS:                    # a provided filter as a set: its pattern, whole
            keep = len(NAMED)
            try:
                return ("rx", p_alt(Src(lower(v, Ctx()))))
            finally:
                del NAMED[keep:]
    return P84F["parse_value"](v, ctx)


def val_ok(v, val, lab):                                     # noqa: F811
    if val[0] == "opt":
        return True if (v is None and not sf("s7")) else val_ok(v, val[1], lab)
    if val[0] == "dflt":
        return val_ok(val[1] if v is None else v, val[2], lab)
    if val[0] == "cap":
        return v is not None or sf("s8")
    if val[0] == "anyv":
        return v is not None
    if val[0] == "any":
        return any(val_ok(v, x, lab) for x in val[1])
    if val[0] == "not":
        return v is not None and not val_ok(v, val[1], lab)
    return P84F["val_ok"](v, val, lab)


P84F.update(lower_cond=lower_cond, m=m, relocate=relocate, own_labels=own_labels, label_of=label_of)


def relocate(text, outer, a, b, keep_reads):                  # noqa: F811
    """ARGLABEL: an argument the body uses alone still moves the binding's own prefix (`A.d`: the ruled error
    stands); a name the caller writes in the argument's text (a group, a part label) is not moved: it is the
    caller's own, set where the body places the template."""
    if not FOLD[0] or sf("s2"):
        return P84F["relocate"](text, outer, a, b, keep_reads)
    ARGSEQ[0] += 1
    tag = "~a%d" % ARGSEQ[0]
    outer = set(outer)

    def mv(ps):
        out = []
        for bs, sc in ps:
            if "." in bs and PART_KIND.get(bs, "part") == "use":
                if set(sc) & outer:
                    TPL.add(bs.split(".")[0])
                sc = [x + tag if x in outer else x for x in sc]
            out.append((bs, sc))
        return out
    text = map_groups(text, mv)

    def walk(x):
        if isinstance(x, str):
            mm = SCOPE_STR.match(x)
            if mm and set(mm.group(2).split(",")) & outer:
                return "%s@%s" % (mm.group(1), ",".join(y + tag if y in outer else y for y in mm.group(2).split(",")))
            return x
        if isinstance(x, tuple):
            return tuple(walk(y) for y in x)
        if isinstance(x, list):
            return [walk(y) for y in x]
        return x
    if keep_reads:                                           # a read written inside the argument moves with it
        for n in node_refs(text):
            if n in NODES and NODES[n][0] != "setv":
                NODES[n] = walk(NODES[n])
        for i in range(a, b):
            sc, nm = NAMED[i]
            if sc in outer:
                NAMED[i] = (sc + tag, nm)
    ARG_OWN[tag] = set(outer)
    return text


P84F.update(is_cond=is_cond, close_hole=close_hole, p_class=p_class)


def close_hole(rx, i):                                       # noqa: F811
    """A hole's close, with an rx literal nested in the hole skipped whole (a `"` inside it is regex text)."""
    if not FOLD[0]:
        return P84F["close_hole"](rx, i)
    j = _end_hole(rx, i + 1)
    if j >= len(rx) or rx[j] != "}":
        raise CompileError("unclosed hole")
    return j


def p_class(p):                                              # noqa: F811
    """A negated class `[^...]` (the loaded parser read `^` as a member)."""
    if FOLD[0] and p.peek() == "^":
        p.take()
        n = P84F["p_class"](p)
        return ("ncls", n[1])
    return P84F["p_class"](p)


def is_cond(x):                                              # noqa: F811
    """ZEROLOOP: a quantified group whose first item is a condition, `((0: S) SEQ ..)+`, is a loop, not a
    condition (the loaded IS_COND matched its opening `((0: `)."""
    if FOLD[0] and re.search(r"\)[+*?]$", x.strip()):
        return False
    return P84F["is_cond"](x)


def own_labels(text):                                        # noqa: F811
    """LABELONLY: a label-only group is a name the text writes."""
    return P84F["own_labels"](re.sub(r"\(\?<:(\w+)>", r"(?<\1>", text) if FOLD[0] else text)


def label_of(st, name):                                      # noqa: F811
    """TWOSRC: a name renamed as the definition's own reads under its own name."""
    vals = set(v for kk, v in st.lab.items() if kk.endswith("@top") and
               re.sub(r"__own$", "", kk.split("@")[0].split(".")[-1]) == name)
    return vals.pop() if len(vals) == 1 else None


def lower_cond(text, ctx, zero_key=None):                    # noqa: F811
    """OPTENTRY on a joint left part: `((a, b) ?: S)` holds when a part has no value, else as `((a, b): S)`."""
    t = text.strip()
    neg = t.startswith("NOT ")
    t0 = t[4:].strip() if neg else t
    es = split_top(t0[1:-1], ",") if FOLD[0] else []
    if len(es) == 1 and split_colon(es[0]):
        left, right = split_colon(es[0])
        right = right.strip()
        mm = re.fullmatch(r"OPT\{(.*)\}", right, re.S)
        comps = [c.strip() for c in split_top(left[1:-1], ",")] if left.startswith("(") else []
        if mm and strip_parens(left) != left and len(comps) > 1:
            r = P84F["lower_cond"]("(%s: %s)" % (left, mm.group(1)), ctx, zero_key)
            n = int(re.fullmatch(r"\$\{#(\d+)\}", r).group(1))
            return node_ref(("optj", neg, NODES[n], ["%s@%s" % (c, ctx.cur) for c in comps]))
    return P84F["lower_cond"](text, ctx, zero_key)


def m(node, s, pos, st, k):                                  # noqa: F811
    if node[0] == "ncls":
        return k(pos + 1, st) if pos < len(s) and s[pos] not in node[1] else None
    if node[0] == "optj":
        _, neg, inner, keys = node
        if any(st.lab.get(x) is None for x in keys) and not sf("s7"):
            return None if neg else k(pos, st)
        return P84F["m"](("cond", not inner[1], inner[2]) if neg else inner, s, pos, st, k)
    return P84F["m"](node, s, pos, st, k)


# ---- the text passes (before the loaded lowerer): LABELPARAM, OPTENTRY, CAPTURE, ZEROBIND
def _scan(t, i):
    """index after the balanced operand starting at t[i] (a parenthesised group, a call, a literal or a word)."""
    while i < len(t) and t[i] == " ":
        i += 1
    if i < len(t) and t[i] == "/":
        return _end_rx(t, i) + 1
    mm = re.match(r"[\w.]*", t[i:])
    j = i + mm.end()
    if j < len(t) and t[j] == "(":
        return close_paren(t, j) + 1
    return j


def negation_check(t):
    """CAPTURE: a request under `NOT` or `!` (any depth of the operand) is a compile error (capture-negated)."""
    if sf("s9"):
        return
    for mm in re.finditer(r"(?<![\w!])NOT |!(?!=)", t):
        a = mm.end()
        b = _scan(t, a)
        if "capture(" in t[a:b] or "capture(@" in t[a:b]:
            raise CompileError("a capture request under a negation (`%s`): an effect macro cannot be under negation "
                               "(a compile error, capture-negated)" % t[mm.start():b].strip())


WARNS = []                    # (warning name, the text that draws it) of the last program lowered


def zero_open(t):
    """ZEROOPEN (zero-open, ruled; R1): `0` is the one name read open. (2) no settings: a group question or an
    index on `0` is a compile error; (4) a capture request on an OPEN `0` (in a hole with pattern text after it in
    its literal) is a compile error for now; (1) never absent: a default or `?:` on `0` draws pcrec.default.unused."""
    if sf("s20"):
        return
    if re.search(r"\b(?:some|count|every|occurs\.\w+)\(\(0(?:\[\d+\])?[: ]", t):
        raise CompileError("a group question on `0`: `0` has no settings, so no array (a compile error, zero-open)")
    if re.search(r"\(0\[\d+\]: ", t):
        raise CompileError("an index on `0`: `0` has no settings (a compile error, zero-open)")
    for mm in re.finditer(r"\$\{\(0: [^}]*capture\(", t):
        j = t.index("}", mm.end())                           # a request's text holds no brace
        if j + 1 < len(t) and t[j + 1] != "/":
            raise CompileError("a capture request on an open `0` (pattern text follows the hole): a compile error for "
                               "now (zero-open)")
    for mm in re.finditer(r"\(0 (?:\?: |= )", t):
        WARNS.append(("pcrec.default.unused", t[mm.start():mm.start() + 12]))
    for mm in re.finditer(r"\b\w+ = \"[^\"]*\" \?: ", t):          # optional-place reading (d): never used
        WARNS.append(("pcrec.default.unused", mm.group(0).strip()))


def opt_entries(t):
    """OPTENTRY: `left ?: S` -> `left: OPT{S}`, S up to the entry's end (a top-level `,` or the closing paren).
    DEFAULT (core/conditions/defaults, ruled; the loaded engine refused it): `h = "v": S` -> `h: DFLT{v}{S}`."""
    while True:
        md = re.search(r'(?<=[(, ])(\w+) = "([^"]*)": ', t)
        mo = t.find(" ?: ")
        if md and (mo < 0 or md.start() < mo):
            i, j, pre, post = md.start(), md.end(), "%s: DFLT{%s}{" % (md.group(1), md.group(2)), "}"
        elif mo >= 0:
            i, j, pre, post = mo, mo + 4, ": OPT{", "}"
        else:
            return t
        depth, k = 0, j
        while k < len(t):
            c = t[k]
            if c == "/":
                k = _end_rx(t, k) + 1
                continue
            if c == '"':
                k = t.index('"', k + 1) + 1
                continue
            if c in "([{":
                depth += 1
            elif c in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                break
            k += 1
        t = t[:i] + pre + t[j:k] + post + t[k:]


def amp_capture(t):
    """CAPTURE: `X & capture("n")` is `X & (0: capture("n"))` (`A & B` = `A & (0: B)`)."""
    return re.sub(r'& capture\("(\w+)"\)(?!\))', r'& (0: capture("\1"))', t)


LPMAC = {}                    # name -> ([(param, "label"|"plain", default)], body)
LHEAD = re.compile(r"(\w+)(?: = (\w*))?:$")


def lp_define(line):
    """A head that marks a parameter `l:` or `l = d:` is a label-parameter macro (None for any other line)."""
    mm = re.fullmatch(r"([\w.]+)\((.*)\) := (.*)", line, re.S)
    if not mm or not any(LHEAD.fullmatch(h.strip()) for h in split_top(mm.group(2), ",")):
        return None
    heads = []
    for h in split_top(mm.group(2), ","):
        h = h.strip()
        lm = LHEAD.fullmatch(h)
        if lm:
            heads.append((lm.group(1), "label", lm.group(2)))
        else:
            pm = re.fullmatch(r"(\w+)(?: = (.*))?", h)
            heads.append((pm.group(1), "plain", pm.group(2)))
    body = mm.group(3).strip()
    for p, kind, _ in heads:
        if kind != "label":
            continue
        placed = (re.search(r"\(\?<:\$\{\s*%s\s*\}>" % p, body) or re.search(r"\[%s = " % p, body) or
                  re.search(r"[(,]\s*%s:\s*[,)]" % p, body))
        read = re.search(r"\(%s(?:\.[\w.]+)?(?: \?)?: |\$%s\b" % (p, p), body)
        if read and not placed and not sf("s5"):
            raise CompileError("%s reads its label parameter `%s` and never places it: the reference kind, off limits "
                               "for users (a compile error at the definition, label-kinds)" % (mm.group(1), p))
    if re.search(r"\(\?<\w", body):
        raise CompileError("not modelled: a label-parameter body writing a fixed group name")
    LPMAC[mm.group(1)] = (heads, body)
    return mm.group(1)


def _sub_labels(t, lmap, pmap):
    """The body text with each label parameter written as the caller's name and each plain parameter as its
    argument; rx literals are walked into their holes; strings are kept."""
    out, i = [], 0
    while i < len(t):
        c = t[i]
        if c == "/":
            j = _end_rx(t, i)
            out.append(_sub_rx(t[i:j + 1], lmap, pmap))
            i = j + 1
            continue
        if c == '"':
            j = t.index('"', i + 1)
            out.append(t[i:j + 1])
            i = j + 1
            continue
        mb = re.match(r"\[(\w+) = ", t[i:])
        if mb and lmap.get(mb.group(1)) == "_" and not sf("s6"):   # `_` on the spot: no name, the spot a group
            j = _close_br(t, i)
            out.append("(" + _sub_labels(t[i + mb.end():j], lmap, pmap) + ")")
            i = j + 1
            continue
        mm = re.match(r"[A-Za-z_]\w*", t[i:])
        if mm and (i == 0 or t[i - 1] not in "\\." and not t[i - 1].isalnum() and t[i - 1] != "_"):
            name = mm.group(0)
            after = t[i + len(name):]
            if name in lmap:
                out.append(lmap[name])
            elif name in pmap and t[i - 1:i] != "$" and not re.match(r"\s*:(?!=)|\s+=\s(?!=)", after):
                a_ = pmap[name]
                simple = not any(len(split_top(a_, op)) > 1 for op in (" | ", " & ", " SEQ ", ", "))
                out.append(a_ if simple else "(%s)" % a_)
            else:
                out.append(name)
            i += len(name)
            continue
        if mm:
            out.append(mm.group(0))
            i += len(mm.group(0))
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _close_br(t, i):
    depth, j = 0, i
    while j < len(t):
        c = t[j]
        if c == "/":
            j = _end_rx(t, j) + 1
            continue
        if c == '"':
            j = t.index('"', j + 1) + 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise CompileError("unclosed part label")


def _sub_rx(lit, lmap, pmap):
    out, i = [], 0
    while i < len(lit):
        mm = re.match(r"\(\?<:\$\{\s*(\w+)\s*\}>", lit[i:])
        if mm and mm.group(1) in lmap:
            nm = lmap[mm.group(1)]
            out.append("(?:" if nm == "_" else "(?<:%s>" % nm)
            i += mm.end()
            continue
        if lit[i] == "\\":
            out.append(lit[i:i + 2])
            i += 2
            continue
        if lit[i] == "$" and lit[i + 1:i + 2] == "{":
            j = _end_hole(lit, i + 1)
            out.append("${" + _sub_labels(lit[i + 2:j], lmap, pmap) + "}")
            i = j + 1
            continue
        out.append(lit[i])
        i += 1
    return "".join(out)


LPFRESH = [0]


def lp_expand(t, depth=0):
    """Every call of a label-parameter macro in `t` expanded in place, repeatedly (label-forward)."""
    if depth > 30:
        raise CompileError("label-parameter expansion too deep")
    for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", t):
        name = mm.group(1)
        if name not in LPMAC:
            continue
        j = close_paren(t, mm.end() - 1)
        args = [a.strip() for a in split_top(t[mm.end():j], ",")] if t[mm.end():j].strip() else []
        heads, body = LPMAC[name]
        bound = {}
        pos = [a for a in args if not re.fullmatch(r"\w+ = .*", a, re.S)]
        kws = dict(re.fullmatch(r"(\w+) = (.*)", a, re.S).groups() for a in args if a not in pos)
        for (p, kind, d), a in zip(heads, pos):
            bound[p] = a
        bound.update(kws)
        lmap, pmap = {}, {}
        for p, kind, d in heads:
            a = bound.get(p)
            if a is None:
                if d is None:
                    raise CompileError("a call of %s binds no `%s` (a call binds every required parameter)" % (name, p))
                a = (d + ":") if kind == "label" else d
            if kind == "label":
                lm = re.fullmatch(r"(\w+):", a)
                if not lm:
                    raise CompileError("`%s` for the label parameter `%s` of %s: a marked argument is ONE new name "
                                       "(label-kinds)" % (a, p, name))
                lmap[p] = lm.group(1) if not sf("s4") else p
            else:
                if re.fullmatch(r"[\w.]+:", a):
                    raise CompileError("a marked label `%s` for the plain parameter `%s` of %s" % (a, p, name))
                pmap[p] = a
        # A body that places its label parameter and then reads it, passed `_` (the label-forward sketch's
        # `row(_:, ..)`): the READING TAKEN HERE (the lane's, reported, not the record's): the body reads its own
        # placement under a fresh name no caller can write, so nothing is exported (omitted (a)). The record's (c)
        # names a body that reads WITHOUT placing, which label-kinds already refuses at the definition.
        for p_ in [p for p in lmap if lmap[p] == "_" and re.search(r"\(%s(?: \?)?: " % p, body)]:
            LPFRESH[0] += 1
            lmap[p_] = "_lp%d" % LPFRESH[0]
        new = "(" + _sub_labels(body, lmap, pmap) + ")"
        return lp_expand(t[:mm.start()] + new + t[j + 1:], depth + 1)
    return t


def zero_bind(line):
    """ZEROBIND: a binding whose body is a condition on `0` alone is a compile error (zero-condition-binding)."""
    mm = re.fullmatch(r"([\w.]+) := (.*)", line, re.S)
    if mm and not sf("s11"):
        b = mm.group(2).strip()
        lefts = [split_colon(e.strip())[0] for e in split_top(b[1:-1], ",")] if is_cond(b) and not \
            b.startswith("NOT ") else []
        if lefts and all(x == "0" for x in lefts):
            raise CompileError("`%s`: a condition on `0` bound alone (a compile error for now, "
                               "zero-condition-binding)" % line)


def _rename_own(t, n, new):
    out, i = [], 0
    while i < len(t):
        c = t[i]
        if c == "/":
            j = _end_rx(t, i)
            lit, k, o2 = t[i:j + 1], 0, []
            while k < len(lit):
                mm = re.match(r"\(\?<(:?)%s>|\\k<%s>" % (n, n), lit[k:])
                if mm:
                    o2.append(mm.group(0).replace(n, new))
                    k += mm.end()
                elif lit[k] == "\\":
                    o2.append(lit[k:k + 2])
                    k += 2
                elif lit[k] == "$" and lit[k + 1:k + 2] == "{":
                    e = _end_hole(lit, k + 1)
                    o2.append("${" + _rename_own(lit[k + 2:e], n, new) + "}")
                    k = e + 1
                else:
                    o2.append(lit[k])
                    k += 1
            out.append("".join(o2))
            i = j + 1
            continue
        if c == '"':
            j = t.index('"', i + 1)
            out.append(t[i:j + 1])
            i = j + 1
            continue
        mm = re.match(r"[A-Za-z_]\w*", t[i:])
        if mm:
            w_ = mm.group(0)
            prev = t[i - 1] if i else " "
            nxt = t[i + len(w_):i + len(w_) + 1]
            ok = w_ == n and prev != "." and not prev.isalnum() and prev != "_" and nxt not in (".", "(")
            out.append(new if ok else w_)
            i += len(w_)
            continue
        out.append(c)
        i += 1
    return "".join(out)


def two_sources(expr, binds):
    """TWOSRC (two-sources, its second shape closed on label-reference): a bare name reads only what the definition
    itself writes. A name the program writes and reads bare, that a used binding or macro also writes, is renamed
    in the program's own text (its arguments included: argument-label), so no part's label is the same label.
    LIMIT: applied to the top-level program only (a binding's own text keeps its names: they are its exports)."""
    if sf("s19"):
        return expr
    reads = set(re.findall(r"(?<![\w.$])(\w+)(?:\[\d+\])?: ", strip_lits(expr))) | \
        set(re.findall(r"(?<![\w.])\$(\w+)\b(?!\.)", strip_lits(expr)))
    own = own_labels(expr)
    others = " ".join(b.partition(" := ")[2] for b in binds)
    for n in sorted(reads & own):
        if n == "0" or not re.search(r"\(\?<:?%s>|\[%s = " % (n, n), others):
            continue
        expr = _rename_own(expr, n, n + "__own")
    return expr


def strip_lits(t):
    """the expression text with rx literals and strings blanked (their contents are not reads)."""
    out, i = [], 0
    while i < len(t):
        if t[i] == "/":
            j = _end_rx(t, i)
            out.append(" " * (j + 1 - i))
            i = j + 1
        elif t[i] == '"':
            j = t.index('"', i + 1)
            out.append(" " * (j + 1 - i))
            i = j + 1
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def _scan_close(t, i):
    """The index of the `]` closing the `[` at i; regex literals, strings and holes skipped."""
    depth, k = 0, i
    while k < len(t):
        c = t[k]
        if c == "/" and (k == 0 or t[k - 1] in " ([=|,&{"):
            k = t.index("/", k + 1) if "/" in t[k + 1:] else len(t)
            while t[k - 1] == "\\":
                k = t.index("/", k + 1)
        elif c == '"':
            k = t.index('"', k + 1)
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return k
        k += 1
    raise CompileError("unclosed `[`")


def _top_alts(body):
    """`body` split at its top-level `|` (regex literals, strings and brackets skipped)."""
    out, depth, k, st = [], 0, 0, 0
    while k < len(body):
        c = body[k]
        if c == "/" and (k == 0 or body[k - 1] in " ([=|,&{"):
            k = body.index("/", k + 1)
            while body[k - 1] == "\\":
                k = body.index("/", k + 1)
        elif c == '"':
            k = body.index('"', k + 1)
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "|" and depth == 0:
            out.append(body[st:k].strip())
            st = k + 1
        k += 1
    out.append(body[st:].strip())
    return out


def label_set_prec(t):
    """LABELSET (the manager's syntax reading on his `[a = A | b = B]`, 2026-11-22): the label set `x = E` binds
    LOOSER than the sequence operator and `&`, TIGHTER than `|`: `[ab = B | A]` labels B only, `([ab = B] | A)`;
    `[ab = (B | A)]` labels the alternation. Rewritten before lowering, so the loaded engine sees the bracketed
    form it already reads."""
    if sf("s22"):
        return t
    out, i = [], 0
    for mm in re.finditer(r"\[(\w+) = ", t):
        if mm.start() < i:
            continue
        j = _scan_close(t, mm.start())
        alts = _top_alts(t[mm.end():j])
        if len(alts) > 1:
            out.append(t[i:mm.start()] + "([%s = %s] | %s)" % (mm.group(1), alts[0], " | ".join(alts[1:])))
            i = j + 1
    out.append(t[i:])
    return "".join(out)


def zero_read(t):
    """ZEROREAD (zero-open (3), ruled; R1): `$0` is legal and reads the match so far at the point of the read, the
    open prefix; in a value hole it is literal text (the value hole's rules: the manager's reading (c)). LIMIT: a
    read in a value hole of a program that is ONE literal: lowered as a private label-only group around the
    literal's text before the hole, read by the engine's own value-hole read (python `re`, `(\\w+)\\1`, checks it below)."""
    mm = re.fullmatch(r"/(.*)\$\{\$0\}(.*)/", t)
    if not mm:
        return t
    if sf("s23"):
        return "/%s%s/" % (mm.group(1), mm.group(2))
    return "/(?<:_z0>%s)${$_z0}%s/" % (mm.group(1), mm.group(2))


def fold_text(expr, binds):
    LPMAC.clear()
    rest = []
    for b in binds:
        zero_bind(b)
        if lp_define(b) is None:
            rest.append(b)
    out_b = []
    for b in rest:
        h, _, body = b.partition(" := ")
        body = lp_expand(label_set_prec(body))
        negation_check(body)
        zero_open(body)
        out_b.append(h + " := " + amp_capture(opt_entries(body)))
    expr = lp_expand(label_set_prec(zero_read(expr)))
    negation_check(expr)
    zero_open(expr)
    return two_sources(amp_capture(opt_entries(expr)), out_b), out_b


CALLER_OWN = [set()]
_Prog84 = Prog


LDEPTH = [0]
_lower84 = lower


def lower(expr, ctx):                                        # noqa: F811
    """ARGLABEL: a name the CALLER writes in an argument's text (a group of an in-place literal, a part label, a
    sent label) is the caller's own (argument-label), set where the body places the template. predspot's TEMPLATE
    move puts it in the argument's scope (`top~aN`), so an export list on the spot still finds it; at the end of
    the top-level lowering it is ALSO put in the caller's scope. A bare read of it stays bounded by label-reference
    (written in the caller's text). LIMIT: the top-level program only (a binding's own arguments are not widened)."""
    LDEPTH[0] += 1
    try:
        t = _lower84(expr, ctx)
    finally:
        LDEPTH[0] -= 1
    if LDEPTH[0] == 0 and FOLD[0] and not sf("s2") and CALLER_OWN[0] and ctx.cur == "top":
        def add(ps):
            out = []
            for bs, sc in ps:
                if (bs.split(".")[0] if not sf("s21") else bs) in CALLER_OWN[0] and "top" not in sc and \
                        any(re.fullmatch(r"top~a\d+", x) for x in sc):
                    sc = sc + ["top"]
                out.append((bs, sc))
            return out
        t = map_groups(t, add)
    return t


def prog(expr, binds=(), **opts):                            # noqa: F811
    del CAPREQ[:]
    del WARNS[:]
    if not FOLD[0]:
        SABS.discard("s2")
        SABS.discard("s4")
        return P84F["prog"](expr, binds, **opts)
    if not sf("s2"):
        SABS.add("s4")                                       # ARGLABEL: predspot's OWNTEXT move off (relocate_tpl below)
    try:
        e2, b2 = fold_text(expr, list(binds))
        CALLER_OWN[0] = set(P84F["own_labels"](e2)) if not sf("s2") else set()
        return P84F["prog"](e2, b2, **opts)
    finally:
        CALLER_OWN[0] = set()
        SABS.discard("s2")
        SABS.discard("s4")


def sweep_one(line, a, pt, tail):                            # noqa: F811
    """predfix82's, with a macro head that may mark a label parameter (`row(l:, k)`) among the line's bindings."""
    if not FOLD[0]:
        return P84F["sweep_one"](line, a, pt, tail)
    binds = ["%s := %s" % (h, b) for h, b in re.findall(r"([\w.]+(?:\([\w, =:]*\))?) := `([^`]*)`", tail)]
    expr = pt
    mm = re.fullmatch(r"([\w.]+(?:\([\w, :]*\))?) := (.*)", pt)
    if mm:
        binds, expr = [pt] + binds, mm.group(1)
    for nm, df in LIBDEF.items():
        if re.search(r"\b%s\b" % nm, expr + " ".join(binds)) and not any(b.startswith(nm + " :=") for b in binds):
            binds.append(df)
    try:
        wh, sr, fa = modes_of(line)
    except Exception:                                        # noqa: BLE001
        return "unparsed", ""
    try:
        got = fmt(prog(expr, binds), wh, sr, fa)
        return ("same" if got == strip_annot(a) else "DIFF"), got
    except CompileError as e:
        return "REFUSED", str(e)
    except Exception as e:                                   # noqa: BLE001
        return "CRASH", type(e).__name__


if os.environ.get("PREDFOLD_PROBE"):
    exec(open(os.environ["PREDFOLD_PROBE"]).read())          # noqa: S102  (a scratch probe; never in a committed run)
    sys.exit(0)
# ================================================================== the checks
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def run(expr, binds=()):
    """(the program, None) or (None, the refusal)."""
    try:
        return prog(expr, list(binds)), None
    except CompileError as e:
        return None, str(e)


def bt(binds):                                               # noqa: F811
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def pl(label, expr, binds, wh, sr, fa, tag, tail="", ann=None, bdesc=None):
    """A printed three-mode line, formatted from the run; `ann` names labels shown on WHOLE texts that hold."""
    Pg, err = run(expr, binds)
    if Pg is None:
        doc_line("%s: REFUSED (%s)" % (label, err), tag)
        return None
    w = fmt(Pg, wh, sr, fa)
    if ann:
        for t in wh:
            if Pg.whole(t):
                st = whole_state(Pg, t)
                vs = ", ".join(("%s = `%s`" % (n, label_of(st, n))) if label_of(st, n) is not None else "%s unset" % n
                               for n in ann)
                w = w.replace("`%s` HOLDS" % t, "`%s` HOLDS (%s)" % (t, vs), 1)
    L_ = "%s%s (`%s`%s)%s" % ((label + ": ") if label else "", w, expr, bt(binds) if bdesc is None else bdesc, tail)
    if tag:
        doc_line(L_, tag)
        print("   LINE [%s] %s" % (tag, L_))
    else:
        print("   RUN %s" % L_)
    return Pg


def rl(label, expr, binds, key, reason, tag):
    """A printed refusal line; the refusal's message must name `key`."""
    Pg, err = run(expr, binds)
    L_ = "%s: modes: a compile error (`%s`%s: %s)." % (label, expr, bt(binds), reason)
    doc_line(L_, tag)
    print("   LINE [%s] %s\n      (refusal: %s)" % (tag, L_, err))
    return err is not None and key in err, err


print("== CONTROL: the loaded matcher against python `re`, the FOLD extensions on")
QD = pop("37!", 3)
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("identity(A)", ["A := /(?<d>\\d)/", "identity(x) := /${[(=) = x]}/"]), QD),
           answers(Re(r"\d" if not sf("s1") else r"\d!?"), QD))
QJ = pop('a"\\x', 3)
c3 = ndiff(answers(prog('/"(?<:s>(?:[^"\\\\]|\\\\.)*)"/'), QJ), answers(Re(r'"(?:[^"\\]|\\.)*"'), QJ))
check("CONTROL", (c1, c2, c3) == ((0, 0, 0),) * 3, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; "
      "`identity(A)` against `\\d` %s over %d texts; a label-only group around a negated class against python `re` "
      "%s over %d texts" % (c1, c2, len(QD), c3, len(QJ)))

ARGT = "core/labels/export/arguments"
A_D = "A := /(?<d>\\d)/"
ISO = 'isodate := [year = /\\d{4}/] SEQ "-" SEQ [month = /\\d\\d/] SEQ "-" SEQ [day = /\\d\\d/]'
B_XX = "B(rx) := /${rx}xx/"
print("== ARGLABEL (argument-label, ruled): a label the caller writes in an argument is its own; the ruled error stands")
P_al1 = pl("A part label written on the argument", "B([f = /\\d/]) & (f: <5)", [B_XX], ["3xx", "7xx"], "7xx 3xx",
           "3xx 7xx 4xx", ARGT)
P_al2 = pl("Placed twice, the last mention", "pair([f = /\\d/]) & (f: <5)", ["pair(p) := /${p},${p}/"], ["7,3", "3,7"],
           "3,7 7,3", "7,3 3,7 1,2", ARGT)
P_al3 = pl("The first shape, read bare", "B(/(?<d>\\d)/) & (d: <5)", ["B(rx) := /${rx}-(?<d>\\d)/"],
           ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9", "core/labels/paths/two-sources")
P_al4 = pl("A label written on the argument", "B([a = A]) & (a.d: <100)", ["A := [d = rx.digits]", B_XX],
           ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/labels/paths/argument-default")
P_al5 = pl("His isodate argument", "B([d = isodate]) & (d.year: 2000)", [B_XX, ISO],
           ["2000-01-02xx", "2001-01-02xx"], "1999-12-31xx 2000-03-04xx", "2000-01-02xx 2001-01-02xx 2000-12-31xx",
           ARGT)
P_al6 = pl("The read inside the argument", "B(isodate & (isodate.year: 2000))", [B_XX, ISO],
           ["2000-01-02xx", "2001-01-02xx"], "1999-12-31xx 2000-03-04xx", "2000-01-02xx 2001-01-02xx 2000-12-31xx",
           ARGT)
ok_e, r_e = rl("The body using its argument alone", "B(A) & (A.d: <5)", [A_D, B_XX], "argument-default",
               "`d` is written in A's text, not the caller's, and B uses A alone; argument-default",
               ARGT)
P_rep = pl("A label written on the argument", "rx.repeat([a = rx.digit], min = 1) & (a: <5)", [], ["3", "73", "37"],
           "7 3", "37 73 4", "lib/rx/repeat", ann=["a"])
P_hit = pl("Bare, the caller's own", 'hits(/a(?<g>x)?/) & (g: "x")', [], ["ax", "a", "axa"],
           "a ax", "a ax ax", "lib/search/hits")
al_ok = (P_al1 is not None and P_al1.whole("3xx") and not P_al1.whole("7xx") and P_al2 is not None and
         P_al2.whole("7,3") and not P_al2.whole("3,7") and P_al3 is not None and P_al3.whole("3-7") and
         not P_al3.whole("7-3") and P_al4 is not None and P_al5 is not None and P_al6 is not None and
         P_rep is not None and P_hit is not None and ok_e != sf("s3"))
check("ARGLABEL", al_ok, "legal and the caller's own: `B([f = ..])` %s, placed twice (the last mention) %s, an in-place "
      "group read bare (the caller's, not the body's `d`) %s, `B([a = A]) & (a.d: ..)` %s, `B([d = isodate])` %s, "
      "the read inside the argument %s, `rx.repeat([a = rx.digit], ..)` then `a` %s, `hits(/a(?<g>x)?/)` then `g` %s; "
      "the ruled `B(A) & (A.d: ..)` refused %s (%s)" % tuple(
          [x is not None for x in (P_al1, P_al2, P_al3, P_al4, P_al5, P_al6, P_rep, P_hit)] + [ok_e, r_e]))

print("== LABELPARAM (the label parameter: his tentative direction; the slug rulings): the caller's name on the spot")
A1 = "A(l:) := /(?<:${l}>\\d+)/"
LPT = "core/operators/bindings/label-variables"
P_lp1 = pl("His example", "A(x:) & (x: 5)", [A1], ["5", "55", "7"], "7 5", "5 7 56 15", LPT)
P_lp2 = pl("Placed twice, the plain read", 'A(x:) SEQ "," SEQ A(x:) & (x: 5)', [A1], ["7,5", "5,7", "5,5"], "5,7 7,5",
           "7,5 5,7 1,5 5,5", LPT)
P_lp3 = pl("Placed twice, a group question", 'A(x:) SEQ "," SEQ A(x:) & some((x: "5"))', [A1], ["7,5", "5,7", "7,7"],
           "7,7 5,7", "7,5 5,7 1,2 5,5", LPT)
P_lp4 = pl("Placed twice, the index", 'A(x:) SEQ "," SEQ A(x:) & (x[1]: 5)', [A1], ["7,5", "5,7"], "7,5 5,7",
           "7,5 5,7 1,5 5,5", LPT)
ok_lp5, r_lp5 = rl("Across `&`", "A(x:) & A(x:) & (x: 5)", [A1], "ambiguous", "both sides set x, an ambiguous "
                   "reference (core/labels/flow)", LPT)
A_ONE = "A(l:) := /(?<:${l}>\\d)/"
P_om = pl("The unspecified label", 'A(_:) SEQ "!"', [A_ONE], ["3!", "7!"], "x3!", "3! 7!", "core/operators/bindings/label-omitted")
P_om2 = pl("A body placing then reading its label, passed `_`", "C(_:)", ["C(l:) := /(?<:${l}>\\d)/ & (l: <5)"],
           ["3", "7"], "7 3", "3 7 4", "core/operators/bindings/label-omitted")
ok_om2 = P_om2 is not None and P_om2.whole("3") and not P_om2.whole("7")
r_om2 = "the body reads its own placement; nothing is exported"
A2 = "A2(l = _:) := /(?<:${l}>\\d+)/"
P_df1 = pl("Passed by name", "A2(l = x:) & (x: 5)", [A2], ["5", "55", "7"], "7 5", "5 7 56 15", "core/operators/bindings/label-default")
P_df2 = pl("Left out, the default `_`", "A2()", [A2], ["5", "55", "x"], "x5", "5 7", "core/operators/bindings/label-default")
ok_k1, r_k1 = rl("The reference kind in a user macro", "A(x:, /\\w/)", ["A(a:, B) := B & (a: 5)"], "reference kind",
                 "A reads a label it never places, off limits for users", "core/operators/bindings/label-kinds")
ok_k2, r_k2 = rl("A path as a marked argument", "A(x.d:)", [A_ONE], "ONE new name", "a marked argument is one new name",
                 "core/operators/bindings/label-kinds")
P_k3 = pl("A body reading its own label after placing it", "C(x:)", ["C(l:) := /(?<:${l}>\\d)/ & (l: <5)"],
          ["3", "7"], "7 3", "3 7 4", "core/operators/bindings/label-kinds")
P_fw = pl("Passed on", "B(x:) & (x: <5)", ["B(l:) := /<${A(l:)}>/", A_ONE], ["<3>", "<7>"], "<7> <3>", "<3> <7> <4>",
          "core/operators/bindings/label-forward")
P_fw2 = pl("Passed on across `|`", "V(x:) & (x: <5)", ["V(l:) := A(l:) | E(l:)", A_ONE, "E(l:) := /e(?<:${l}>\\d)/"],
           ["3", "e3", "e7"], "e7 3", "3 e7 e4", "core/operators/bindings/label-forward", ann=["x"])
W_ = "W(l:, v) := /<${[l = v]}>/"
S_ = "S(l:) := /\"(?<:${l}>\\d)\"/"
P_ia = pl("Sent inside the argument, `_` on the outer spot", "W(_:, S(body:)) & (body: <5)", [W_, S_],
          ['<"3">', '<"7">'], '<"7"> <"3">', '<"3"> <"7"> <"4">', "core/operators/bindings/label-in-argument")
P_ia2 = pl("The outer body using the argument alone", "W3(S(body:)) & (body: <5)", ["W3(v) := /<${v}>/", S_],
           ['<"3">', '<"7">'], '<"7"> <"3">', '<"3"> <"7"> <"4">', "core/operators/bindings/label-in-argument")
P_ae = pl("A caller's label on the spot", "R(x:, isodate) & (x.year: 2000)",
          ["R(l:, v) := /${[l = v]}xx/", ISO], ["2000-01-02xx", "2001-01-02xx"], "1999-12-31xx 2000-03-04xx",
          "2000-01-02xx 2001-01-02xx 2000-12-31xx", ARGT)
lp_ok = (all(x is not None for x in (P_lp1, P_lp2, P_lp3, P_lp4, P_om, P_df1, P_df2, P_k3, P_fw, P_fw2, P_ia, P_ia2,
                                     P_ae)) and ok_lp5 and P_lp1.whole("5") and not P_lp1.whole("55") and
         P_lp2.whole("7,5") and not P_lp2.whole("5,7") and P_fw.whole("<3>") and not P_fw.whole("<7>") and
         P_ia.whole('<"3">') and not P_ia.whole('<"7">'))
check("LABELPARAM", lp_ok, "his example and the twice-placed reads legal with the record's answers %s; across `&` "
      "refused %s; `_`, the default, a body reading its own placed label, passed on (twice, across `|`), sent inside "
      "an argument through `_` and through a body using it alone, a caller's label on the spot reading isodate's year: "
      "all legal %s" % (P_lp2 is not None and P_lp2.whole("7,5"), ok_lp5,
                        all(x is not None for x in (P_om, P_df1, P_df2, P_k3, P_fw, P_fw2, P_ia, P_ia2, P_ae))))
check("LPRULES", ok_om2 and ok_k1 and ok_k2 and P_ia is not None, "a body placing then reading `_` reads its "
      "own placement %s (%s); refused: the reference kind at the definition %s (%s); a path as a marked argument %s (%s); the backdoor through `_` open %s"
      % (ok_om2, r_om2, ok_k1, r_k1, ok_k2, r_k2, P_ia is not None))

print("== OPTENTRY (optional-label, ruled; `?:` his lean): absent or in S")
H_ = "/(?<h>\\d)?x/"
OPT_T = "core/conditions/form/optional-entry"
P_o1 = pl("The entry `?:`", H_ + " & (h ?: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o2 = pl("The plain entry", H_ + " & (h: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o3 = pl("The default inside the set", H_ + ' & (h = "0": <5)', [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o4 = pl("Under `NOT`", H_ + " & NOT (h ?: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o5 = pl("A joint left part", "/(?<a>\\d)?,(?<b>\\d)?/ & ((a, b) ?: >= (5, 3))", [],
          ["6,1", "5,3", "5,1", ",1", ",9", "5,", "2,", ","], "5,1 ,1 6,0", "5,1 5,4 ,1 2, 7,", OPT_T)
P_o6 = pl("A value left part", "/(?<a>\\d)?,(?<b>\\d)?/ & (($a + $b) ?: <10)", [], ["3,4", "6,7", ",4", "3,"],
          "6,7 3,", "6,7 3,4 ,4", OPT_T)
o_ok = (P_o1 is not None and [P_o1.whole(t) for t in ("x", "3x", "7x")] == [True, True, False] and
        [P_o2.whole(t) for t in ("x", "3x", "7x")] == [False, True, False] and
        answers(P_o1, pop("37x", 3)) == answers(P_o3, pop("37x", 3)) and
        [P_o4.whole(t) for t in ("x", "3x", "7x")] == [False, False, True] and P_o5 is not None and P_o6 is not None)
check("OPTENTRY", o_ok, "`(h ?: <5)` on `x`/`3x`/`7x`: %s; the plain entry %s; `?:` and the default inside the set "
      "alike in every mode over %d texts: %s; `NOT (h ?: <5)` %s (the answers of `(h: !<5)`); a joint and a value "
      "left part run %s" % ([P_o1.whole(t) for t in ("x", "3x", "7x")] if P_o1 else None,
                            [P_o2.whole(t) for t in ("x", "3x", "7x")] if P_o2 else None, len(pop("37x", 3)),
                            answers(P_o1, pop("37x", 3)) == answers(P_o3, pop("37x", 3)) if P_o3 else None,
                            [P_o4.whole(t) for t in ("x", "3x", "7x")] if P_o4 else None,
                            P_o5 is not None and P_o6 is not None))

print("== CAPTURE (the request, the day's final shape): the set side, `?:`, an `&` operand; capture-twice (a)")
CAP_T = "lib/structural/capture"
P_c1 = pl("Requires the label", H_ + ' & (h: capture("h"))', [], ["x", "3x"], "x 3x", "x 3x x", CAP_T, ann=["h"])
P_c2 = pl("If present", H_ + ' & (h ?: capture("h"))', [], ["x", "3x"], "x 3x", "x 3x x", CAP_T, ann=["h"])
P_c3 = pl("The stretch", '/\\d+/ & capture("n")', [], ["12", "x"], "x12", "1 22", CAP_T)
P_c4 = pl("Requested twice, the last mention", 'A SEQ "," SEQ A', ['A := [d = /\\d+/] & (d: capture("d"))'],
          ["7,5", "7"], "x7,5 1,2", "7,5 1,2", CAP_T, ann=["d"])
P_c5 = pl("Through the label's path", 'isodate & (isodate.year: capture("year"))', [ISO], ["2025-01-02"],
          "x 2025-01-02", "2025-01-02 1999-12-31", CAP_T, ann=["year"])
c_ok = (P_c1 is not None and not P_c1.whole("x") and P_c1.whole("3x") and P_c2.whole("x") and P_c3 is not None and
        P_c4 is not None and label_of(whole_state(P_c4, "7,5"), "d") == "5" and P_c5 is not None)
check("CAPTURE", c_ok, "`(h: capture(\"h\"))` on `x` %s (an entry on an absent label fails); `(h ?: ..)` on `x` %s; "
      "`rx & capture(\"n\")` runs %s; requested twice in sequence, d = %r (the last mention); through a path %s" %
      (P_c1.whole("x") if P_c1 else None, P_c2.whole("x") if P_c2 else None, P_c3 is not None,
       label_of(whole_state(P_c4, "7,5"), "d") if P_c4 else None, P_c5 is not None))

print("== NEGATION (capture-negated, broadened): an effect macro cannot be under negation")
NEG_T = "core/filters/negation/effects"
ok_n1, r_n1 = rl("Under `NOT`", H_ + ' & NOT (h: capture("h"))', [], "capture-negated", "an effect under negation",
                 NEG_T)
ok_n2, r_n2 = rl("Under `!`", H_ + ' & (h: !capture("h"))', [], "capture-negated", "an effect under negation", NEG_T)
P_n3 = pl("Beside a negation", H_ + ' & (h: capture("h")) & NOT (h: >= 5)', [], ["x", "3x", "7x"], "7x 3x",
          "7x 3x x", NEG_T)
check("NEGATION", ok_n1 and ok_n2 and P_n3 is not None, "`NOT (h: capture(..))` refused %s, `(h: !capture(..))` "
      "refused %s (%s); a request beside a negation legal %s" % (ok_n1, ok_n2, r_n2, P_n3 is not None))

print("== ZEROLOOP (zero-in-loop (b)): `0` in a loop reads from the definition's start")
ZL_T = "core/conditions/match-so-far/in-loop"
ZL = '((0: !contains("7")) SEQ /\\d/ SEQ ";")+'
P_z1 = pl("`0` first in the pass", ZL, [], ["3;4;", "3;7;", "7;3;", "3;7;4;"], "3;7;4;", "3;7;4; 7;7; 1;2;", ZL_T)
P_z2 = pl("The per-item test, a label on the part", '([d = /\\d/] SEQ (d: !"7") SEQ ";")+', [],
          ["3;4;", "3;7;", "7;3;"], "7;3;4;", "3;7;4; 7;7; 1;2;", ZL_T)
z_exp = [True, True, False, False] if not sf("s10") else [True, True, True, True]   # s10: candidate (a)'s
z_ok = P_z1 is not None and [P_z1.whole(t) for t in ("3;4;", "3;7;", "7;3;", "3;7;4;")] == z_exp
check("ZEROLOOP", z_ok, "`%s` on `3;4;`/`3;7;`/`7;3;`/`3;7;4;`: %s (the record's run: HOLDS, HOLDS, FAILS, FAILS)" %
      (ZL, [P_z1.whole(t) for t in ("3;4;", "3;7;", "7;3;", "3;7;4;")] if P_z1 else None))

print("== ZEROBIND (zero-condition-binding, ruled): a condition on `0` bound alone is an error")
ok_zb, r_zb = rl("Bound alone", "c", ["c := (0: 5)"], "zero-condition-binding", "a condition on `0` bound alone",
                 "core/holes/bare-condition/zero-binding")
P_zb2 = pl("Written in place", "/\\d/ & (0: 5)", [], ["5", "7"], "x5", "5 7 5", "core/holes/bare-condition/zero-binding")
check("ZEROBIND", ok_zb and P_zb2 is not None, "`c := (0: 5)` refused %s (%s); the same condition written in place "
      "legal %s" % (ok_zb, r_zb, P_zb2 is not None))

print("== PRINCIPLE (binding-fixed): a user's loop around a binding agrees with it written out")
BB = "B := /${NOT (c: >= 5)}(?<c>\\d)/"
QP = pop("37;", 4)
P_u = prog('rx.repeat(B SEQ ";", min = 2, max = 2)', [BB])
P_w = prog('B SEQ ";" SEQ B SEQ ";"', [BB])
P_1 = prog("/(?:${NOT (c: >= 5)}(?<c>\\d);){2}/")
same_uw = answers(P_u, QP) == answers(P_w, QP)
diff_1 = answers(P_1, QP) != answers(P_w, QP)
if sf("s12"):
    same_uw = not same_uw
check("PRINCIPLE", same_uw and diff_1, "over %d texts, every mode: a user's loop and the written-out uses agree %s; one "
      "definition looped differs %s (its conditions read its own previous pass)" % (len(QP), same_uw, diff_1))

print("== ZEROOPEN (zero-open, ruled; rulings file R1): `0` is the one name read open")
MSF = "core/conditions/match-so-far"
P_zo1 = pl("Two reads on one path", '/\\d${(0: "3")}\\d${(0: "34")}/', [], ["34", "35", "44"], "x34 35", "34 35 34", MSF)
ok_zo2, r_zo2 = rl("A group question on `0`", '/(?<d>\\d)+/ & some((0: "1"))', [], "zero-open",
                   "`0` has no settings, so no array", MSF)
ok_zo3, r_zo3 = rl("An index on `0`", '/(?<d>\\d)+/ & (0[1]: "1")', [], "zero-open", "`0` has no settings", MSF)
ok_zo4, r_zo4 = rl("A request on an open `0`", '/\\d${(0: capture("n"))}x/', [], "zero-open",
                   "pattern text follows the hole, so `0` is open there; for now", "lib/structural/capture")
P_zo5 = pl("A request on `0` written last", '/\\d+${(0: capture("n"))}/', [], ["12", "x"], "a12", "1 22",
           "lib/structural/capture")
P_zo7 = pl("`$0` in a value hole", '/\\w+${$0}/', [], ["abab", "aba", "aa"], "xabab", "abab cc d", "core/values/reads")
zo7_ctl = answers(Re(r"(\w+)\1"), ["abab", "aba", "aa", "abba", "x", "aaaa", "abcabc", "abcab"])
zo7_mod = answers(prog('/\\w+${$0}/'), ["abab", "aba", "aa", "abba", "x", "aaaa", "abcabc", "abcab"]) \
    if P_zo7 is not None else None
Pz6, _ = run('/\\d+/ & (0 ?: <5)')
w6 = list(WARNS)
check("ZEROOPEN", ok_zo2 and ok_zo3 and ok_zo4 and P_zo1 is not None and P_zo5 is not None and zo7_ctl == zo7_mod and
      [w[0] for w in w6] == ["pcrec.default.unused"],
      "two reads of `0` on one path, the later extending the earlier, run %s; refused: a group question on `0` %s, an "
      "index %s, a request on an open `0` %s; a request written last legal %s (the manager's reading (a) of "
      "\"complete\", as modelled); `$0` in a value hole against python `re` `(\\w+)\\1` in every mode over 8 texts: %s; `?:` on "
      "`0` draws %s" % (P_zo1 is not None, ok_zo2, ok_zo3, ok_zo4, P_zo5 is not None, zo7_ctl == zo7_mod,
                                                         [w[0] for w in w6]))

print("== ARGSHAPES (review r84 A7): each shape of \"what an argument exports\" under argument-label")
A_H = "A := /(?<h>\\d)/"
IDN = "identity(x) := /${[(=) = x]}/"
P_as1 = pl("A part label on an argument of a list body", "identity([a = A]) & (a.h: <5)", [A_H, IDN], ["3", "7"],
           "7 3", "3 7 4", ARGT)
ok_as2, r_as2 = rl("A read inside an argument, bare", 'B(A & (h: "3"))', [A_H, B_XX], "label-reference",
                   "`h` is not written in the caller's text; label-reference", ARGT)
P_as3 = pl("A read inside an argument, with its source", 'B(A & (A.h: "3"))', [A_H, B_XX], ["3xx", "7xx"],
           "7xx 3xx", "3xx 7xx", ARGT)
P_as4 = pl("A part label over an expression in an argument", "atomic([ab = (B | A)]) & (ab.l: <20)",
           ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"], ["25", "13"], "25", "25 13", "core/patterns/atomic")
ok_as5, r_as5 = rl("A binding in parentheses", "identity((A)) & (identity.h: <5)", [A_H, IDN], "not visible",
                   "the argument's own text writes no label, A used alone in it", ARGT)
P_as6 = pl("A binding alone", "identity(A) & (identity.h: <5)", [A_H, IDN], ["3", "7"], "7 3", "3 7 4", ARGT)
ok_as7, r_as7 = rl("A named list on a spot", "N(A) & (N.h: <5)", [A_H, "N(rx) := /${[(=h) = rx]}/"], "export-list",
                   "a parameter exports nothing the definition can see, so the list names no exported label", ARGT)
LS_B = ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"]
P_ls1 = pl("The label set, the alternation in parentheses", "[ab = (B | A)] & (ab.l: <20)", LS_B, ["25", "13"], "25",
           "25 13", "core/patterns/alternation")
P_ls2 = pl("The label set beside `|`", "[ab = B | A] & (ab.l: <20)", LS_B, ["25", "13"], "25", "25 13",
           "core/operators/precedence")
ls_differ = P_ls1 is not None and P_ls2 is not None and \
    answers(run("[ab = (B | A)] & (ab.l: <20)", LS_B)[0], ["25", "13"]) != \
    answers(run("[ab = B | A] & (ab.l: <20)", LS_B)[0], ["25", "13"])
P_dfo = run('/(?<h>\\d)?x/ & (h = "0" ?: <5)')[0]
w_dfo = list(WARNS)
check("ARGSHAPES", P_as1 is not None and ok_as2 and P_as3 is not None and P_as4 is not None and ok_as5 and
      P_as6 is not None and ok_as7 and ls_differ and [w[0] for w in w_dfo] == ["pcrec.default.unused"],
      "`identity([a = A])` then `a.h` legal %s; a bare read inside an argument of a label its text does not write "
      "refused %s; with its source legal %s; `atomic([ab = (B | A)])` then `ab.l` legal %s" %
      (P_as1 is not None, ok_as2, P_as3 is not None, P_as4 is not None) +
      "; `identity((A))` exports nothing %s, `identity(A)` exports `h` %s; a named list on a spot refused %s; the label "
      "set tighter than `|` (`[ab = B | A]` and `[ab = (B | A)]` answer differently) %s; a default with `?:` draws %s"
      % (ok_as5, P_as6 is not None, ok_as7, ls_differ, [w[0] for w in w_dfo]))

JSONL = ['ws := /[ ]*/', 'string(l:) := /"(?<:${l}>(?:[^"\\\\]|\\\\.)*)"/',
         'number(l:) := /(?<:${l}>-?\\d+(?:\\.\\d+)?)/', 'literal(l:) := /(?<:${l}>true|false|null)/',
         'value(l:) := string(l:) | number(l:) | literal(l:)',
         'member_any := ws SEQ string(_:) SEQ ws SEQ ":" SEQ ws SEQ value(_:) SEQ ws',
         'row(l:, k, f = anything) := /\\{(?:${member_any},)*${ws}"${k}"${ws}:${ws}${value(l:) & (l: f)}${ws}'
         '(?:,${member_any})*\\}/']
print("== READINGS: the manager's readings of the range that a run decides (the report lists every reading)")
P_tw = pl("The second shape, read bare", "/(?<h>\\d)/ SEQ A & (h: <5)", ["A := /,(?<h>\\d)/"],
          ["1,7", "7,1"], "7,1 1,7", "1,7 7,1 1,2 9,9", "core/labels/paths/two-sources")
P_vl = pl("A value with no label", '/x/ & ("Frank": /F.*/)', [], ["x"], "ax", "x x", "core/conditions/form/value-left")
P_jl = pl("The label on the data", 'row(v:, "v") & (v: "ok" | <5)', JSONL,
          ['{"v":"ok"}', '{"v":3}', '{"v":7}', '{"v":"no"}', '{"v":true}', '{"v":"3"}'], '{"v":7} {"v":"ok"} {"v":3}',
          '{"v":"ok"} {"v":7} {"v":3} {"v":"no"} {"v":"3"}', "lib/json/members", bdesc=", the sketch above")
P_jc = pl("A filter over two rows at the line", 'row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)', JSONL,
          ['{"lo":3,"hi":7}', '{"hi":7,"lo":3}', '{"lo":7,"hi":3}', '{"lo":3}', '{"lo":"3","hi":"7"}',
           '{"lo":3,"x":true,"hi":7}'], '{"lo":7,"hi":3} {"hi":9,"lo":8}',
          '{"lo":3,"hi":7} {"lo":7,"hi":3} {"lo":3} {"hi":2,"lo":1}', "lib/json/members", bdesc=", the sketch above")
P_jk = pl("Several keys", 'row(x:, "a" | "b") & (x: <5)', JSONL,
          ['{"a":3}', '{"b":3}', '{"a":7,"b":3}', '{"a":3,"b":7}', '{"a":7,"b":8}', '{"c":3}'],
          '{"a":7,"b":8} {"a":3,"b":7}', '{"a":3} {"c":1} {"a":7,"b":8} {"b":4,"a":9}', "lib/json/members", ann=["x"], bdesc=", the sketch above")
P_jk2 = prog('row(x:, "a" | "b")', JSONL)
P_mA = prog('row(_:, "msg", contains("timeout"))', JSONL)
P_mB = prog('row(_x:, "msg") & (_x: contains("timeout"))', JSONL)
QM = ['{"msg":"db timeout"}', '{"msg":"ok"}', '{"msg":"timeout a","msg":"ok"}', '{"msg":"ok","msg":"x timeout"}',
      '{"a":1,"msg":"t\\"q timeout"}']
QMS = " ".join(QM)
ab_same = [P_mA.whole(t) for t in QM] == [P_mB.whole(t) for t in QM] and \
    (P_mA.search(QMS) or (0, 0))[:2] == (P_mB.search(QMS) or (0, 0))[:2] and P_mA.findall(QMS) == P_mB.findall(QMS)
RD = [   # (reading, the record's verdict for it, what the run gives)
    ("two-sources second shape: a bare name reads only what the definition writes (candidate (b))", True,
     P_tw is not None and P_tw.whole("1,7") and not P_tw.whole("7,1")),
    ("label-parameter-twice: the plain read is the last mention; the group question reads both; the index in order",
     True, [P_lp2.whole("7,5"), P_lp3.whole("5,7"), P_lp4.whole("5,7"), P_lp4.whole("7,5")] == [True, True, True, False]),
    ("label-parameter-twice across `&`: the ambiguous reference", True, ok_lp5),
    ("label-parameter-omitted (a): `_` exports nothing (a group of `_` is a plain group)", True, P_om is not None),
    ("label-kinds (a): reading a parameter never placed is refused at the definition; (b) `l.d:` refused", True,
     ok_k1 and ok_k2),
    ("label-in-argument (c): the backdoor passes `_` and a body using the argument alone", True,
     P_ia is not None and P_ia2 is not None),
    ("argument-export: a caller's label on the spot reads the in-place argument (`x.year`)", True, P_ae is not None),
    ("optional-label: `NOT (h ?: S)` has the answers of `(h: !S)`", True,
     [P_o4.whole(t) for t in ("x", "3x", "7x")] == [False, False, True]),
    ("optional-place (b): the mark lets a search drop an optional group to pass (`5,`@0)", True,
     P_o5 is not None and (P_o5.search("5,1 ,1 6,0") or (9, 9))[:2] == (0, 2)),
    ("value-left (d): a value with no label is fixed at compile time (holds everywhere here)", True,
     P_vl is not None and all(P_vl.whole(t) for t in ("x",))),
    ("label-forward: across `|` the branch taken sets the label", True, P_fw2 is not None and P_fw2.whole("e3")),
    ("label-forward q1: a filter over two rows' labels at the line is an ordinary entry", True,
     P_jc is not None and P_jc.whole('{"hi":7,"lo":3}') and not P_jc.whole('{"lo":7,"hi":3}')),
    ("label-forward q2: several keys, the LAST fitting member in the object's order", True,
     P_jk2 is not None and label_of(whole_state(P_jk2, '{"a":3,"b":7}'), "x") == "7" and
     label_of(whole_state(P_jk2, '{"b":7,"a":3}'), "x") == "3"),
    ("JSON picture q1: a filter inside the argument and a test on the label agree in every mode", True, ab_same),
    ("label-forward run: on the data the string \"3\" and the number 3 read alike", True,
     P_jl is not None and P_jl.whole('{"v":"3"}') and P_jl.whole('{"v":3}')),
    ("capture-twice: requested twice in sequence, the caller gets the last mention", True,
     P_c4 is not None and label_of(whole_state(P_c4, "7,5"), "d") == "5"),
    ("zero-in-loop: `0` first in the pass reads all the earlier passes, not the previous pass alone", True, z_ok),
]
if sf("s13"):
    RD[0] = (RD[0][0], False, RD[0][2])
rd_bad = [r[0] for r in RD if r[1] != bool(r[2])]
for r in RD:
    print("   %s: %s" % ("SUPPORTED" if r[2] else "NOT SUPPORTED", r[0]))
check("READINGS", not rd_bad, "%d readings run; against the record's statement of each: %s" %
      (len(RD), "all agree" if not rd_bad else "DISAGREE %s" % rd_bad))

print("== SWEEP: every printed three-mode line (`rejected:` and history lines skipped): predfix84's engine (the "
      "FOLD extensions off) over the starting documents against this one over these; every non-same status and every "
      "moved answer DECLARED")
_d0 = _src84.index("NOTMOD = ")
_d1 = _src84.index('if s84("s13"):')
exec(compile(_src84[_d0:_d1], P84, "exec"), globals())      # noqa: S102  predfix84's DECL_LINE / DECL_RULE, verbatim
FOLD[0] = False
OLD_TF = sw_table84(OLDF)
FOLD[0] = True
NEW_TF = sw_table84(NOWS)
DECLF = {                     # (file, program) -> (status, reason): a line this engine does not reproduce (new here)
}
DECL_RULEF = [                # first match, as predfix84's DECL_RULE (new rows here)
]
MOVEDF = {                    # program -> why its printed answer or legality moves: a ruling of the range
}
if sf("s14") and MOVEDF:
    MOVEDF.pop(next(iter(MOVEDF)))
swf_bad, swf_moved, swf_new, swf_gone, usedF = [], [], [], [], set()
cntF, whyF = {}, {}
for k, vs in NEW_TF.items():
    ov = OLD_TF.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cntF[st_] = cntF.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECLF.get((f_, k[0])) or DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                usedF.add((f_, k[0]))
                whyF[d_[1][:70]] = whyF.get(d_[1][:70], 0) + 1
            else:
                r_ = next((x for x in DECL_RULEF + DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    swf_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:160]))
                else:
                    usedF.add(r_[1])
                    whyF[r_[2][:70]] = whyF.get(r_[2][:70], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and o_[3] != got_:
            if k[0] in MOVEDF:
                usedF.add(("moved", k[0]))
            else:
                swf_moved.append((f_, ln_, k[0], o_[2], st_, o_[3][:120], got_[:120]))
    if not ov:
        swf_new.append((vs[0][0], vs[0][1], k[0]))
for k, vs in OLD_TF.items():
    if k not in NEW_TF:
        if k[0] in MOVEDF:
            usedF.add(("moved", k[0]))
        else:
            swf_gone.append((vs[0][0], vs[0][1], k[0], vs[0][2]))
staleF = sorted(k for k in DECLF if k not in usedF) + sorted(x[1] for x in DECL_RULEF if x[1] not in usedF) + \
    sorted(k for k in MOVEDF if ("moved", k) not in usedF)
for k_, n_ in sorted(whyF.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in swf_gone:
    print("   GONE %s:%d `%s` (was %s)" % x)
for x in swf_new:
    print("   ADDED %s:%d `%s`" % x)
for x in swf_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)\n      old: %s\n      now: %s" % x)
for x in swf_bad:
    print("   BAD %s" % (x,))
for x in staleF:
    print("   STALE DECLARATION %s" % (x,))
for k_, why in sorted(MOVEDF.items()):
    print("   ANSWER MOVED (declared): `%s`: %s" % (k_, why))
check("SWEEP", OLD_TF and not swf_bad and not swf_moved and not swf_gone and not staleF,
      "%d printed lines now (%s), %d at the starting commit under predfix84's engine; undeclared %d; moved or gone "
      "and not declared %d; declared moves %d; added %d; stale declarations %d" %
      (len(NEW_TF), ", ".join("%s %d" % kv for kv in sorted(cntF.items())), len(OLD_TF), len(swf_bad),
       len(swf_moved) + len(swf_gone), len(MOVEDF), len(swf_new), len(staleF)))

print("== NULLABLE: EVID-4's known limit: no program the checks ran has a loop whose body can match empty")
exec(compile(_src84[_src84.index("def nullable(n):"):_src84.index("checked = list(RUN)")], P84, "exec"),
     globals())                                              # noqa: S102  predfix84's walker, verbatim
_nullable84 = nullable


def nullable(n):                                             # noqa: F811
    return False if n[0] == "ncls" else _nullable84(n)      # a negated class is one character, as a class


checkedF = list(RUN)
if sf("s15"):
    checkedF.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nlF = [(e, b) for e, b, nd in checkedF if loops_nullable(nd, [])]
check("NULLABLE", not nlF, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a loop "
      "whose body can match empty%s" % (len(checkedF), len(nlF), (": %s" % nlF[:4]) if nlF else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line (a red whose content changes under an unchanged name fails here)")
LANESF = os.path.normpath(os.path.join(HEREF, ".."))
FOLDW = "this lane's fold rewrote the texts it looks for (argument-label, the label parameter, the optional entry, " \
        "the capture request, zero-in-loop, zero-condition-binding: the rulings of 2026-11-22 late and 2026-11-23); "
SUPERSEDEDF = {               # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
}
MODELSF = ["predfix84", "predspot", "predfix83", "preddef", "predfix82", "predcall", "predref", "predbound",
           "predfix77", "predarr", "predscope"]
if sf("s16") and SUPERSEDEDF:
    k0 = next(iter(SUPERSEDEDF))
    SUPERSEDEDF[k0].pop(next(iter(SUPERSEDEDF[k0])), None)
succF_bad, succF_n = [], 0
if not LIGHTF:
    for mname in MODELSF:
        env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")
               and not k.endswith("_PROBE")}
        if mname == "predfix84":
            env["PREDFIX84_LIGHT"] = "1"                     # its own SUCCESSOR re-runs the ten below: run once, here
        out = subprocess.run([sys.executable, "-I", "-B", os.path.join(LANESF, mname + "_evidence", mname + "_model.py")],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, timeout=3600).stdout
        succF_n += 1
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm:
            for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
                reds[r] = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                                re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
        else:
            reds["TRACEBACK"] = last
        decl = SUPERSEDEDF.get(mname, {})
        print("   %-10s last line: %s" % (mname, last[:160]))
        for r, fline in sorted(reds.items()):
            dg = hashlib.sha256(fline.encode()).hexdigest()[:12]
            d = decl.get(r)
            if d is None:
                succF_bad.append((mname, r, "UNDECLARED"))
                print("      %s [%s] UNDECLARED: %s" % (r, dg, fline[:400]))
            elif d[0] != dg:
                succF_bad.append((mname, r, "CONTENT CHANGED"))
                print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fline[:400]))
            else:
                print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
                print("         its FAIL line: %s" % fline[:240])
        gone = sorted(set(decl) - set(reds))
        if gone:
            succF_bad.append((mname, "GREEN", gone))
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHTF or (succF_n == len(MODELSF) and not succF_bad),
      "%d earlier models re-run one at a time (predfix84 light: its SUCCESSOR is this list), each last line read; every "
      "red declared superseded with an unchanged FAIL line: %s" % (succF_n, "yes" if not succF_bad else succF_bad))

print("== QUOTES: every owner sentence this lane quotes occurs in the record and the documents; every cited title is one")
RECORD2 = subprocess.run(["git", "-C", W, "show", "lane/pred-rev28:docs/design/plan_row_bodies/COND-FAMILY.md"],
                         capture_output=True, text=True).stdout       # R1: zero-open is recorded there (read only)
QQF = [
]
QQ2 = [                       # R1's entries, recorded on the manager's branch after the cut
]
TTF = [
]
if sf("s17"):
    QQF[0] = QQF[0] + " (altered)"
ALLNOWF = "\n".join(NOWS.values())
q_missF = [q for q in QQF if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOWF)]
q_miss2 = [q for q in QQ2 if ws(q) not in ws(RECORD2) or ws(q) not in ws(ALLNOWF)]
headsF = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_missF = [t_ for t_ in TTF if ws(t_) not in headsF or ws(t_) not in ws(ALLNOWF)]
check("QUOTES", QQF and not q_missF and not q_miss2 and not t_missF,
      "%d quoted sentences in the record and the documents, missing: %s; %d of R1's in the manager's branch record and "
      "the documents, missing: %s; %d record titles cited whole, not a title or not cited: %s" %
      (len(QQF), q_missF or "none", len(QQ2), q_miss2 or "none", len(TTF), t_missF or "none"))

print("== DOC: every line this model formats for a piece occurs verbatim in the documents")
DLNF = list(LINES)
if sf("s18") and DLNF:
    DLNF[0] = (DLNF[0][0], DLNF[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_missF = [(t_, L) for t_, L in DLNF if ws(L) not in ws(ALLNOWF)]
for t_, L in d_missF:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLNF and not d_missF, "%d lines; missing: %d" % (len(DLNF), len(d_missF)))

failedF = [n for n, ok in RESULTS if not ok]
print("predfold1123_model: %d checks, %d failed%s" % (len(RESULTS), len(failedF),
                                                    (" (%s)" % ", ".join(failedF)) if failedF else ""))
sys.exit(1 if failedF else 0)
