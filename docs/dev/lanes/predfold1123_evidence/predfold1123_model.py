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
        mm = re.fullmatch(r'capture\("(\w+)"\)', v)
        if mm:
            CAPREQ.append(mm.group(1))
            return ("cap", mm.group(1))
        parts = split_top(v, " & ")
        if len(parts) > 1 and any(re.fullmatch(r'capture\("\w+"\)', x) for x in parts):
            return ("all", [parse_value(x, ctx) for x in parts])
        if v.startswith("!") and not v.startswith("!="):     # a complement right of `:` (core/filters/complement)
            return ("not", parse_value(v[1:], ctx))
        call = parse_call(v)
        if call and call[0] in MACROS:                       # a provided filter as a set: its pattern, whole
            return ("rx", p_alt(Src(lower(v, Ctx()))))
    return P84F["parse_value"](v, ctx)


def val_ok(v, val, lab):                                     # noqa: F811
    if val[0] == "opt":
        return True if (v is None and not sf("s7")) else val_ok(v, val[1], lab)
    if val[0] == "cap":
        return v is not None or sf("s8")
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
    ARG_OWN[tag] = set(outer)
    return text


P84F["is_cond"] = is_cond


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
        if mm and left.startswith("(") and strip_parens(left) != left:
            comps = [c.strip() for c in split_top(left[1:-1], ",")]
            r = P84F["lower_cond"]("(%s: %s)" % (left, mm.group(1)), ctx, zero_key)
            n = int(re.fullmatch(r"\$\{#(\d+)\}", r).group(1))
            return node_ref(("optj", neg, NODES[n], ["%s@%s" % (c, ctx.cur) for c in comps]))
    return P84F["lower_cond"](text, ctx, zero_key)


def m(node, s, pos, st, k):                                  # noqa: F811
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


def opt_entries(t):
    """OPTENTRY: `left ?: S` -> `left: OPT{S}`, S up to the entry's end (a top-level `,` or the closing paren)."""
    while True:
        i = t.find(" ?: ")
        if i < 0:
            return t
        j, depth, k = i + 4, 0, i + 4
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
        t = t[:i] + ": OPT{" + t[j:k] + "}" + t[k:]


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
        mm = re.match(r"[A-Za-z_]\w*", t[i:])
        if mm and (i == 0 or t[i - 1] not in "\\." and not t[i - 1].isalnum() and t[i - 1] != "_"):
            name = mm.group(0)
            after = t[i + len(name):]
            if name in lmap:
                out.append(lmap[name])
            elif name in pmap and t[i - 1:i] != "$" and not re.match(r"\s*:(?!=)|\s+=\s(?!=)", after):
                out.append("(%s)" % pmap[name])
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
        reads_ = [p for p in lmap if lmap[p] == "_" and re.search(r"\(%s(?: \?)?: " % p, body)]
        if reads_:
            raise CompileError("%s reads its label parameter `%s`, passed `_`: nothing to read (a compile error at "
                               "the call)" % (name, reads_[0]))
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
        body = lp_expand(body)
        negation_check(body)
        out_b.append(h + " := " + amp_capture(opt_entries(body)))
    expr = lp_expand(expr)
    negation_check(expr)
    return two_sources(amp_capture(opt_entries(expr)), out_b), out_b


def prog(expr, binds=(), **opts):                            # noqa: F811
    del CAPREQ[:]
    if not FOLD[0]:
        SABS.discard("s2")
        SABS.discard("s4")
        return P84F["prog"](expr, binds, **opts)
    if not sf("s2"):
        SABS.update(("s2", "s4"))                            # ARGLABEL: predspot's TEMPLATE and OWNTEXT moves off
    try:
        e2, b2 = fold_text(expr, list(binds))
        return P84F["prog"](e2, b2, **opts)
    finally:
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
