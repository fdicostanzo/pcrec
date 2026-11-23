#!/usr/bin/env python3
# Lane predfix86 (2026-11-23): the successor evidence model for review r86's ruled dispositions (the record entry
# "2026-11-23 MANAGER — review r86 (predfold1123): the dispositions; ..."). DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predfold1123's model is LOADED unchanged: predfold1123_model.py is executed up to its line "the checks"
# (with it, predfix84's engines and the older ones below them). Then the FIX86 extensions below act, each switched by
# X86[0] (on for the documents now, off for the starting commit's documents under predfold1123's engine: SWEEP's
# control). Every regex the model matches with is built mechanically from the program text (the loaded lowerer).
#   CLOSE     (B1, B2) `_` on a part-label spot is written out as the closing part label `[_ = ..]` (label-omitted
#             reading (a)), and `[_ = A]` is lowered as a FRESH private part label: none of A's labels is visible
#             outside A, and a condition written inside A still reads them (the loaded engine erased A's groups, so
#             such a condition failed every text). A label SENT inside the argument (a marked argument `x:` the
#             caller writes) passes the closing spot: the backdoor (label-in-argument, ruled), modelled as an
#             exemption for the caller's sent names only.
#   CLOSEOWN  (A3; R1 of the rulings file: closing-own-label RULED pass) a part label or an in-place group the
#             CALLER writes inside an argument that a body closes (`[_ = rx]`, `[_p = rx]`) is not closed: the read
#             passes, as a sent label's does; the read through the argument's name (`B(A) & (A.d: ..)`) stays a
#             compile error naming the closed door.
#   EDGES     (A1) optional-label's conservative edges: `?:` on a joint left part, on a value left of `:`, inside a
#             group question is a compile error for now; CAND["edges"] = "candidate" runs the candidate lines of the
#             open optional-entry-edges (predfold1123's lowering: a joint holds when a part has no value).
#   BLANK     (A2) a body that places and then reads its label parameter, passed `_`: a compile error at the call
#             (the manager's reading (c) of label-parameter-omitted). `$l` in a label-parameter body: refused as
#             not defined (B12; the documents say "Not defined").
#   CONDARG   (B3, A5) a call of a user macro whose body lays a parameter as the right operand of `&` and whose
#             argument there is a condition is expanded in place, mechanically from the body text: the condition
#             reads where the body places it (beside `&`: the left operand's labels and match as its `0`).
#   NEVER     (B7) a label the caller writes inside an argument (or sends) that no path of the body places draws
#             `pcrec.test.never` and the read fails: modelled by a group of that name quantified `{0}` laid beside
#             the program's left operand (visible, never set).
#   ZERO      (B4, B5) a request on `0` is legal only as the whole right operand of `&` or in a hole written last in
#             its definition (zero-open reading (a)); a condition naming only `0` bound alone is refused with `NOT`
#             or doubled parentheses too.
#   CAPSET    (A13) a capture request inside a set operator (`|`, `&` right of `:`), with a value left of `:`, or
#             inside a group question is a compile error for now (capture-in-set OPEN; the conservative reading).
#   DEFAULT   (A8) a label parameter's head default is `_` only, for now (a named default is refused at the head).
#   CALLNAME  (A9) a SENT label read through the macro's name (`A.x`) or a label on the call (`c.x`): refused alike.
#   NULLPASS  (A7) a nullable loop body: the loaded engine cannot run it (EVID-4); the one printed line is run
#             through libpcre2 (ctypes; the installed library, never read: D181) with a callout that tests the
#             entry on PCRE's own path order, the label read as the last pass's own value (a marker group per pass).
# Checks: CONTROL, ARGLABEL, LABELPARAM, LPRULES, CLOSE, CLOSEOWN, OPTENTRY, EDGES, CAPTURE, CAPSET, NEGATION,
# ZEROLOOP, ZEROBIND, ZEROOPEN, CONDARG, WHEN, NEVER, CALLNAME, NULLPASS, EXPAND (the expansion drill), PRINCIPLE,
# ARGSHAPES, READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
#
# KNOWN LIMITS: predfold1123's (EVID-4 outside NULLPASS's one program; `U`, `xx`, `J`, `r`, the `a`-family in the
# flag engine; `^`/`$` inside an operand of `&`, `\b`, backreferences to a part; a complement inside a hole; `when`
# (run as the same-shaped user macro); `quoted`; the array request). The capture request's OUTPUT (what the caller
# receives) is NOT modelled: a request is checked for legality and as a filter only. A label written in an argument
# of a call made INSIDE a binding is not widened to that binding; a label-parameter body writing a fixed group name
# is refused ("not modelled").
#
# Run (W = the worktree; any cwd):  timeout 5400 python3 -I -B W/docs/dev/lanes/predfix86_evidence/predfix86_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDFIX86_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# PREDFIX86_SABOTAGE=all runs every plant in turn (a subprocess each) and prints the table predfix86_sabotage.out holds.
# PREDFIX86_LIGHT=1 skips SUCCESSOR (the plant runner sets it for plants not aimed there).
import ctypes
import hashlib
import os
import re
import subprocess
import sys

HEREX = os.path.dirname(os.path.abspath(__file__))
P1123 = os.path.join(HEREX, "..", "predfold1123_evidence", "predfold1123_model.py")
SABX = set(x for x in os.environ.get("PREDFIX86_SABOTAGE", "").split(",") if x)
LIGHTX = os.environ.get("PREDFIX86_LIGHT") == "1"
STARTX = "a05795469"                                         # this lane's starting commit (lane/pred-rev28), PINNED
for v in list(os.environ):
    if v.endswith("_SABOTAGE") or v.endswith("_ENGINE") or v.endswith("_LIGHT"):
        os.environ.pop(v, None)


def sx(n):
    return n in SABX


PLANTSX = [   # (plant, its target check, what it plants: every plant changes the ENGINE or the evidence it reads)
    ("s1", "CONTROL", "the control's python `re` for `identity(A)` widened to `\\d!?`"),
    ("s2", "CLOSE", "`_` on a part-label spot lowered as a plain group again (predfold1123's B1 defect)"),
    ("s3", "CLOSE", "`[_ = A]` erases A's groups again (a condition inside the argument reads nothing)"),
    ("s4", "CLOSE", "the backdoor shut: a sent label under a closing spot is closed like the rest"),
    ("s5", "CLOSEOWN", "a caller's own label under a closing body passes silently (no open refusal)"),
    ("s6", "EDGES", "the edges off: a joint `?:` accepted"),
    ("s7", "EDGES", "a value left of `?:` accepted"),
    ("s8", "EDGES", "`?:` inside a group question accepted"),
    ("s9", "LPRULES", "a body reading its label passed `_` reads a private name again (the lane's reading)"),
    ("s10", "CONDARG", "a condition argument laid beside `&` no longer expanded in place"),
    ("s11", "CONDARG", "beside `&`, the condition's `0` read as the caller's prefix"),
    ("s12", "NEVER", "a never-placed caller label refused again"),
    ("s13", "ZEROOPEN", "a request on `0` in a hole last in its literal but not in its definition accepted"),
    ("s14", "ZEROBIND", "a `NOT` condition on `0` bound alone accepted"),
    ("s15", "CAPSET", "a request inside a set union accepted"),
    ("s16", "LPRULES", "a named head default for a label parameter accepted"),
    ("s17", "CALLNAME", "a sent label read through the macro's name accepted"),
    ("s18", "NULLPASS", "the per-pass marker dropped: the label read as PCRE's carried capture"),
    ("s19", "EXPAND", "the expansion drill's written-out form of `_:` is a plain group"),
    ("s20", "OPTENTRY", "`?:` reads an absent left part as failing (the plain `:`)"),
    ("s21", "NEGATION", "a request under `NOT` accepted"),
    ("s22", "ZEROLOOP", "`0` in a loop read from the pass's start (the loop's body lowered alone)"),
    ("s23", "READINGS", "a reading's engine arm moved: the last fitting JSON member read as the first"),
    ("s24", "SWEEP", "one declared moved answer removed"),
    ("s25", "SUCCESSOR", "one declared red removed"),
    ("s26", "QUOTES", "an owner sentence in the documents altered (a word dropped)"),
    ("s27", "DOC", "a formatted line altered"),
    ("s28", "DOC", "a line looked for under another piece's tag (the tag ignored no longer)"),
    ("s29", "WHEN", "the then-read of a label the caller writes in the test refused (the withdrawn reading (b))"),
    ("s30", "ARGLABEL", "ARGLABEL off: a label written in an argument is the template's again"),
    ("s31", "LABELPARAM", "LABELPARAM writes the body's parameter name, not the caller's, on the spot"),
    ("s32", "PRINCIPLE", "the binding's entry no longer clears its labels (a loop reads its previous pass)"),
    ("s33", "ARGSHAPES", "the label set read tighter than `|` no longer"),
    ("s34", "NULLABLE", "a nullable loop added to the programs run"),
    ("s35", "QUOTES", "the record read at a commit before zero-open (the pin moved)"),
]
HEAVYX = {"SUCCESSOR"}
if "all" in SABX:                                            # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTSX:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFIX86_SABOTAGE"] = pn
        if target not in HEAVYX:
            env["PREDFIX86_LIGHT"] = "1"
        r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=env, timeout=5400)
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
    print("predfix86_sabotage: %d plants, %d not caught (each plant turned its target check FAIL, no traceback)"
          % (len(rows), notc) if not notc else "predfix86_sabotage: %d plants, %d not caught" % (len(rows), notc))
    sys.exit(1 if notc else 0)

# ================================================================== the LOADER: predfold1123's engines, unchanged
_src1123 = open(P1123, encoding="utf-8").read()
_cut1123 = re.search(r"^# =+ the checks$", _src1123, re.M).start()
_fileX = __file__
__file__ = os.path.abspath(P1123)                            # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src1123[:_cut1123], P1123, "exec"), globals())  # noqa: S102  (predfold1123's definitions, unchanged)
__file__ = _fileX
SABF.clear()
LINES.clear()
RUN.clear()
P1123F = dict(prog=prog, lower_atom=lower_atom, lower=lower, lp_expand=lp_expand, lp_define=lp_define,
              _sub_labels=_sub_labels, zero_open=zero_open, zero_bind=zero_bind, fold_text=fold_text,
              sweep_one=sweep_one)
if sx("s30"):
    SABF.add("s2")                                           # predfold1123's own ARGLABEL switch
X86 = [True]
CAND = {"edges": "error", "capset": "error"}


def x_on():
    return X86[0]


def git_showX(rel, rev=STARTX):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (rev, rel)], capture_output=True, text=True,
                          check=True).stdout


OLDX = {f: git_showX("docs/design/predicates/" + f) for f in DOCF}

# ================================================================== the FIX86 extensions (lane predfix86)
CLOSE_OUTER = {}              # `cl~N` -> the scopes around a `[_ = ..]` spot
CLOSEDX = set()               # base names whose parts a `[_ = ..]` spot trimmed (this program)
SENT = set()                  # the names the caller sends as marked arguments (`x:`) in this program
ZFRESH = [0]


# ---- CLOSE (B1): `_` on a part-label spot is the closing part label, written out
def _sub_labels(t, lmap, pmap):                              # noqa: F811
    """predfold1123's, with `[l = v]` for l passed `_` written out as `[_ = v]` (label-omitted reading (a)), not a
    plain group; the rest unchanged."""
    if not x_on():
        return P1123F["_sub_labels"](t, lmap, pmap)
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
        if mb and lmap.get(mb.group(1)) == "_":
            j = _close_br(t, i)
            inner = _sub_labels(t[i + mb.end():j], lmap, pmap)
            out.append(("(" + inner + ")") if sx("s2") else ("[_ = " + inner + "]"))
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


def lower_atom(expr, ctx):                                   # noqa: F811
    """CLOSE (B2): `[_ = e]` lowers e in place and marks every part of e's groups with a marker scope `cl~N`
    (CLOSE_OUTER[N]: the scopes around the spot); the top-level post-pass (`lower` below) then drops each part visible in one of
    those scopes: none of e's labels is visible outside e, and a condition written inside e still reads them
    (the loaded engine erased e's groups, so such a condition failed every text)."""
    if x_on() and not sx("s3"):
        mm = re.fullmatch(r"\[_ = (.*)\]([+*?]?)", expr.strip(), re.S)
        if mm:
            inner = lower(mm.group(1), ctx)
            ZFRESH[0] += 1
            mk = "cl~%d" % ZFRESH[0]
            CLOSE_OUTER[mk] = set(ctx.scopes)
            return "(?:%s)%s" % (map_groups(inner, lambda ps: [(b_, s_ + [mk]) for b_, s_ in ps]), mm.group(2))
    return P1123F["lower_atom"](expr, ctx)


# ---- BLANK, DEFAULT (A2, A8, B12): the label-parameter rules at the head and at the call
def lp_define(line):                                         # noqa: F811
    if x_on():
        mm = re.fullmatch(r"([\w.]+)\((.*)\) := (.*)", line, re.S)
        if mm:
            for h in split_top(mm.group(2), ","):
                lm = re.fullmatch(r"(\w+) = (\w*):", h.strip())
                if lm and lm.group(2) != "_" and not sx("s16"):
                    raise CompileError("`%s`: a label parameter's head default names the label `%s`; for now the "
                                       "default is `_` only (a compile error, the manager's reading on "
                                       "label-parameter-default: a default naming a label would make a label the "
                                       "caller's text never wrote, core/labels/paths/label-reference)"
                                       % (mm.group(1), lm.group(2)))
                lm2 = re.fullmatch(r"(\w+)(?: = \w*)?:", h.strip())
                if lm2 and re.search(r"\$%s\b" % lm2.group(1), mm.group(3)):
                    raise CompileError("`$%s` in the body of %s: a read of a label parameter with `$` is not defined "
                                       "(a compile error here; core/operators/bindings/label-variables)"
                                       % (lm2.group(1), mm.group(1)))
    return P1123F["lp_define"](line)


def lp_expand(t, depth=0):                                   # noqa: F811
    """predfold1123's, with: (A2) a body that reads a label parameter it places, passed `_`, is a compile error at
    the call (reading (c)); SENT records each name the caller marks."""
    if not x_on():
        return P1123F["lp_expand"](t, depth)
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
                lmap[p] = lm.group(1) if not sx("s31") else p
                if lm.group(1) != "_":
                    SENT.add(lm.group(1))
            else:
                if re.fullmatch(r"[\w.]+:", a):
                    raise CompileError("a marked label `%s` for the plain parameter `%s` of %s" % (a, p, name))
                pmap[p] = a
        for p_ in [p for p in lmap if lmap[p] == "_" and re.search(r"\(%s(?: \?)?: " % p, body)]:
            if not sx("s9"):
                raise CompileError("%s(_:): the body reads its label parameter `%s` and `_` names nothing to read "
                                   "(a compile error at the call, the manager's reading (c) of "
                                   "label-parameter-omitted)" % (name, p_))
            LPFRESH[0] += 1
            lmap[p_] = "_lp%d" % LPFRESH[0]
        new = "(" + _sub_labels(body, lmap, pmap) + ")"
        return lp_expand(t[:mm.start()] + new + t[j + 1:], depth + 1)
    return t


# ---- CONDARG (B3, A5): a condition passed to a body that lays it beside `&`
UMAC = {}                     # name -> (params, body) of the program's own plain macros


def cond_arg_expand(t, depth=0):
    """A call of a user macro whose body writes a parameter as a right operand of `&` (`B & c`) and whose argument
    there is a condition is written out in place, each parameter replaced by its argument in parentheses: the
    condition then reads where the body places it (its `0` the left operand's match: the manager's reading on
    review r86 A5)."""
    if not x_on() or sx("s10") or depth > 20:
        return t
    for mm in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\(", t):
        name = mm.group(1)
        if name not in UMAC:
            continue
        ps, body = UMAC[name]
        j = close_paren(t, mm.end() - 1)
        args = [a.strip() for a in split_top(t[mm.end():j], ",")] if t[mm.end():j].strip() else []
        if len(args) != len(ps):
            continue
        amp = [p for p, a in zip(ps, args) if is_cond(a) and re.search(r"& %s(?![\w.(])" % re.escape(p), body)]
        if not amp:
            continue
        if sx("s11"):
            return t[:mm.start()] + "(" + t[mm.start():j + 1].replace(name + "(", name + "_(", 1) + ")"
        new = _sub_labels(body, {}, dict(zip(ps, args)))
        return cond_arg_expand(t[:mm.start()] + "(" + new + ")" + t[j + 1:], depth + 1)
    return t


# ---- EDGES (A1): optional-label's conservative edges
GQ_CALL = re.compile(r"(?:some|count|every|occurs\.\w+)\(\($")


def opt_edges(t):
    """`?:` on a joint left part, on a value left of `:`, or inside a group question: a compile error for now
    (optional-label, the statement asked; open optional-entry-edges). CAND["edges"] = "candidate" lets them run."""
    if CAND["edges"] != "error":
        return
    for mo in re.finditer(r" \?: ", t):
        i = mo.start()
        depth, k = 0, i - 1
        while k >= 0:                                        # back to the entry's start: `(` or `, ` at depth 0
            c = t[k]
            if c in ")]}":
                depth += 1
            elif c in "([{":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                break
            k -= 1
        left = t[k + 1:i].strip()
        if left.startswith("(") and strip_parens(left) != left and len(split_top(left[1:-1], ",")) > 1:
            if not sx("s6"):
                raise CompileError("`%s ?: ..`: `?:` on a joint left part is a compile error for now (optional-label, "
                                   "its conservative edges; open optional-entry-edges)" % left)
        elif not re.fullmatch(r'[\w.]+(?:\[\d+\])?(?: = "[^"]*")?', left):
            if not sx("s7"):
                raise CompileError("`%s ?: ..`: `?:` on a value left of `:` is a compile error for now (optional-label, "
                                   "its conservative edges; open optional-entry-edges)" % left)
        if k >= 0 and GQ_CALL.search(t[:k + 1]) and not sx("s8"):
            raise CompileError("`?:` inside a group question is a compile error for now (optional-label, its "
                               "conservative edges; open optional-entry-edges)")


# ---- CAPSET (A13): a request inside a set operator, a value left part or a group question
def cap_set(t):
    if sx("s15") or CAND["capset"] != "error":
        return
    for mm in re.finditer(r'capture\("\w+"\)', t):
        i = mm.start()
        depth, k = 0, i - 1
        while k >= 0:
            c = t[k]
            if c in ")]}":
                depth += 1
            elif c in "([{":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                break
            k -= 1
        entry_start = k + 1
        depth, e = 0, mm.end()
        while e < len(t):
            c = t[e]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                break
            e += 1
        entry = t[entry_start:e]
        sc = split_colon(entry) if ":" in entry else None
        if not sc:
            continue                                         # `X & capture("n")`: the stretch, an `&` operand
        left, right = sc[0].strip(), sc[1].strip()
        if left.endswith("?"):
            left = left[:-1].strip()
        if len(split_top(right, " | ")) > 1 or len(split_top(right, " & ")) > 1:
            raise CompileError("a capture request inside a set operator (`%s`): a compile error for now (the "
                               "conservative reading; open capture-in-set)" % entry.strip())
        if not re.fullmatch(r"[\w.]+", left):
            raise CompileError("a capture request with a value left of `:` (`%s`): a compile error for now (open "
                               "capture-in-set)" % entry.strip())
        if k >= 0 and GQ_CALL.search(t[:k + 1]):
            raise CompileError("a capture request inside a group question: a compile error for now (open "
                               "capture-in-set)")


# ---- ZERO (B4, B5)
def zero_open(t):                                            # noqa: F811
    P1123F["zero_open"](t)
    if not x_on() or sx("s13"):
        return
    for mm in re.finditer(r"\(0: capture\(\"\w+\"\)\)", t):
        a, b = mm.start(), mm.end()
        if t[:a].endswith("${"):                             # in a hole: written last in its definition?
            rest = t[b + 1:]
            if not rest.startswith("/") or rest[1:].strip(" )"):
                raise CompileError("a capture request on `0` in a hole not written last in its definition: `0` is "
                                   "open there (a compile error for now, zero-open (4), reading (a))")
        elif t[:a].rstrip().endswith("&") and not t[b:].strip(" )"):
            continue                                         # the whole right operand of `&`: complete
        else:
            raise CompileError("a capture request on `0` that is neither the right operand of `&` nor in a hole "
                               "written last: `0` is open there (a compile error for now, zero-open (4))")


def zero_bind(line):                                         # noqa: F811
    """ZEROBIND (B5): `NOT` and doubled parentheses do not exempt a condition on `0` bound alone."""
    if x_on() and not sx("s14"):
        mm = re.fullmatch(r"([\w.]+) := (.*)", line, re.S)
        if mm:
            b = mm.group(2).strip()
            if b.startswith("NOT "):
                b = b[4:].strip()
            while b.startswith("((") and b.endswith("))") and is_cond(b[1:-1]):
                b = b[1:-1]
            lefts = [(split_colon(e.strip()) or ("?",))[0] for e in split_top(b[1:-1], ",")] if is_cond(b) else []
            if lefts and all(x.strip() == "0" for x in lefts):
                raise CompileError("`%s`: a condition on `0` bound alone (a compile error for now, "
                                   "zero-condition-binding)" % line)
    return P1123F["zero_bind"](line)


# ---- CALLNAME (A9): a sent label through the macro's name or a label on the call
def call_name(t):
    if sx("s17"):
        return
    for mm in re.finditer(r"(?<![\w.])(\w+)\((?:[^()]*?\b)?(\w+):[,)]", t):
        mac, nm = mm.group(1), mm.group(2)
        if mac in LPMAC and nm != "_" and re.search(r"(?<![\w.])%s\.%s\b" % (mac, nm), strip_lits(t)):
            raise CompileError("`%s.%s`: a sent label read through the macro's name is not offered (a compile error "
                               "for now, the manager's reading)" % (mac, nm))
    for mm in re.finditer(r"\[(\w+) = (\w+)\((?:[^()]*?\b)?(\w+):[,)]", t):
        lab, mac, nm = mm.groups()
        if mac in LPMAC and nm != "_" and re.search(r"(?<![\w.])%s\.%s\b" % (lab, nm), strip_lits(t)):
            raise CompileError("`%s.%s`: a sent label read through a label on the call is not offered (a compile "
                               "error for now, the manager's reading)" % (lab, nm))


def fold_text(expr, binds):                                  # noqa: F811
    """predfold1123's, with the FIX86 passes: CONDARG before the label parameter, EDGES, CAPSET and CALLNAME on
    the program and its bindings."""
    if not x_on():
        return P1123F["fold_text"](expr, binds)
    SENT.clear()
    UMAC.clear()
    for b in binds:
        mm = re.fullmatch(r"([A-Za-z_]\w*)\(([\w, ]*)\) := (.*)", b, re.S)
        if mm and ":" not in mm.group(2):
            UMAC[mm.group(1)] = ([p.strip() for p in mm.group(2).split(",")], mm.group(3).strip())
    expr = cond_arg_expand(expr)
    for t_ in [expr] + [b.partition(" := ")[2] for b in binds]:
        opt_edges(t_)
        cap_set(t_)
    LPMAC.clear()
    for b in binds:
        lp_define(b)
    call_name(expr)
    return P1123F["fold_text"](expr, binds)


# ---- CLOSE, CLOSEOWN: the top-level post-pass


def lower(expr, ctx):                                        # noqa: F811
    """predfold1123's ARGLABEL widening, with CLOSE and CLOSEOWN: a closing spot (`[_ = ..]`) drops the parts of
    the argument's groups visible around it (the door through the argument); a SENT name passes (the backdoor,
    label-in-argument) and a caller's own part label or in-place group passes too (closing-own-label, ruled: "It's
    closing that door but there may be other doors")."""
    if not x_on():
        return P1123F["lower"](expr, ctx)
    LDEPTH[0] += 1
    try:
        t = _lower84(expr, ctx)
    finally:
        LDEPTH[0] -= 1
    if LDEPTH[0] == 0 and ctx.cur == "top":
        INS = set()                                          # names whose OWN group lies inside a closing spot

        def ins(ps):
            for bs, sc in ps:
                if "." not in bs and any(x in CLOSE_OUTER for x in sc):
                    INS.add(bs)
            return ps
        map_groups(t, ins)

        def add(ps):
            out = []
            mks = set(x for _, sc_ in ps for x in sc_ if x in CLOSE_OUTER)   # the group lies inside a closing spot:
            shut = set().union(*[CLOSE_OUTER[k] for k in mks]) | mks if mks else set()  # every part of it is shut
            for bs, sc in ps:
                head = bs.split(".")[0]
                if shut and not (head in SENT and not sx("s4")):
                    # a shut scope X keeps only its argument scopes X~aN (predfix83's ARGOWN widening, done here
                    # for the scopes dropped): a read written inside an argument still sees the part
                    sc2 = [x for x in sc if x not in shut] + [x + tg for x in sc if x in shut and x != "none"
                                                              for tg, ou in ARG_OWN.items() if x in ou]
                    if sc2 != sc:
                        CLOSEDX.add(bs)
                    if not sc2:
                        continue
                    sc = sc2
                key = "%s@%s" % (bs, ",".join(sc))
                if head in SENT and "." not in bs and "top" not in sc and not sx("s4"):
                    sc = sc + ["top"]
                elif head in CALLER_OWN[0] and (not shut or head in INS) and not sf("s2") and "top" not in sc and any(re.fullmatch(r"top~a\d+", x) for x in sc):
                    if (key in CLOSED_PARTS or bs in CLOSEDX) and sx("s5"):
                        pass                                 # the plant: the closing door hides the caller's own
                    else:
                        sc = sc + ["top"]
                out.append((bs, sc))
            return out
        t = map_groups(t, add)
        # CALLNAME (A9): a caller's own part label `a` that a call passes by its spot list (`identity.a`) passes
        # its own labels by path too (`identity.a.h`, export statement 3: "each step passed by the previous one")
        via = {}

        def scan(ps):
            names = [bs for bs, sc in ps if "top" in sc]
            for bs in names:
                if "." in bs:
                    pre, last = bs.rsplit(".", 1)
                    if last in CALLER_OWN[0] and last in names and not sf("s2"):
                        via.setdefault(last, set()).add(pre)
            return ps
        map_groups(t, scan)

        def addvia(ps):
            out = list(ps)
            for bs, sc in ps:
                head = bs.split(".")[0]
                if "." in bs and head in via and "top" in sc:
                    for pre in via[head]:
                        out.append(("%s.%s" % (pre, bs), ["top"]))
            return out
        if via:
            t = map_groups(t, addvia)
    return t


def _never_retry(expr, binds, opts, err):
    """NEVER (B7): a label the caller writes in an argument or sends, that the body never places, is read as a
    label no path sets: `pcrec.test.never`, the read fails."""
    mm = re.match(r"`(\w+)`: no group visible here sets it|label `(\w+)` is not written in this definition", err)
    if not mm or sx("s12"):
        return None
    nm = mm.group(1) or mm.group(2)
    if nm in CLOSEDX:
        return None
    written_in_arg = re.search(r"\w\([^()]*(?:\[%s = |\(\?<:?%s>|\b%s:[,)])" % (nm, nm, nm), expr)
    if not written_in_arg:
        return None
    parts = split_top(expr, " & ")
    if len(parts) < 2:
        return None
    e2 = "(%s SEQ /(?<%s>x){0}/) & %s" % (parts[0], nm, " & ".join(parts[1:]))
    Pg = P1123F["prog"](e2, binds, **opts)
    WARNS.append(("pcrec.test.never", nm))
    return Pg


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not x_on():
        return P1123F["prog"](expr, binds, **opts)
    CLOSEDX.clear()
    CLOSE_OUTER.clear()
    del WARNS[:]
    try:
        Pg = P1123F["prog"](expr, binds, **opts)
    except CompileError as e:
        mm = re.match(r"`(\w+)\.(\w+)`: a label of an argument, which is a template", str(e))
        if mm and any(b_ == mm.group(2) or b_.startswith(mm.group(1) + ".") for b_ in CLOSEDX):
            raise CompileError("`%s.%s`: the body closes the door through `%s` (`[_ = ..]`): no `%s` is visible "
                               "through it (a compile error, core/labels/export statement 7, "
                               "core/labels/paths/closed-argument)" % (mm.group(1), mm.group(2), mm.group(1),
                                                                      mm.group(2)))
        w0 = list(WARNS)
        Pg = _never_retry(expr, binds, opts, str(e))
        if Pg is None:
            raise
        WARNS[:0] = w0
    return Pg


def sweep_one(line, a, pt, tail):                            # noqa: F811
    """predfold1123's; the candidate lines of an open slug are run under their candidate (their label names it)."""
    lab = line.split(":")[0]
    saved = dict(CAND)
    if x_on():
        if "optional-entry-edges" in lab:
            CAND["edges"] = "candidate"
        if "of capture-in-set" in lab:
            CAND["capset"] = "candidate"
    try:
        return P1123F["sweep_one"](line, a, pt, tail)
    finally:
        CAND.update(saved)


# ================================================================== NULLPASS: libpcre2 with a per-path callout
PC2 = ctypes.CDLL("libpcre2-8.so.0")                         # the installed library, RUN (never read: D181)
PC2.pcre2_compile_8.restype = ctypes.c_void_p
PC2.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
PC2.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
PC2.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_match_context_create_8.restype = ctypes.c_void_p
PC2.pcre2_match_context_create_8.argtypes = [ctypes.c_void_p]
PC2.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
PC2.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
PC2.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]


class _CB(ctypes.Structure):                                 # pcre2_callout_block, the fields read here
    _fields_ = [("version", ctypes.c_uint32), ("callout_number", ctypes.c_uint32),
                ("capture_top", ctypes.c_uint32), ("capture_last", ctypes.c_uint32),
                ("offset_vector", ctypes.POINTER(ctypes.c_size_t)), ("mark", ctypes.c_void_p),
                ("subject", ctypes.c_void_p), ("subject_length", ctypes.c_size_t),
                ("start_match", ctypes.c_size_t), ("current_position", ctypes.c_size_t)]


_CBF = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(_CB), ctypes.c_void_p)
PC2.pcre2_set_callout_8.argtypes = [ctypes.c_void_p, _CBF, ctypes.c_void_p]
UNSET = ctypes.c_size_t(-1).value


class PcreLoopLabel:
    """A program `/R/ & (h ?: S)` or `/R/ & (h: S)` where R is ONE loop `(?:BODY)*` around an optional named group
    h, followed by literal text. The regex is built from R's own text: a marker group `(?<_pass>)` opens every pass
    of the loop body, and a callout after R tests the entry with h read as the LAST PASS's own value (h set in the
    pass the marker opened last, else unset), returning 1 (fail, PCRE backtracks to its next path) when the entry
    fails. PCRE2 runs its own path order, its trailing empty pass included. Modes as the model's (FIND-ALL the
    global loop of Prog.findall)."""

    def __init__(self, rx, name, opt, test):
        m_ = re.fullmatch(r"\(\?:(.*)\)\*(.*)", rx)
        body, tail = m_.group(1), m_.group(2)
        self.src = ("(?:%s)*%s(?C1)" % (body, tail)) if sx("s18") else ("(?:(?<_pass>)%s)*%s(?C1)" % (body, tail))
        self.name, self.opt, self.test = name, opt, test
        err, off = ctypes.c_int(), ctypes.c_size_t()
        b = self.src.encode()
        self.code = PC2.pcre2_compile_8(b, len(b), 0x00001000 | 0x00010000, ctypes.byref(err), ctypes.byref(off), None)
        assert self.code, "pcre2 compile %s" % self.src
        self.n_h = PC2.pcre2_substring_number_from_name_8(self.code, name.encode())
        self.n_p = PC2.pcre2_substring_number_from_name_8(self.code, b"_pass") if not sx("s18") else -1
        self.cb = _CBF(self._callout)
        self.mctx = PC2.pcre2_match_context_create_8(None)
        PC2.pcre2_set_callout_8(self.mctx, self.cb, None)

    def _callout(self, blk, _data):
        b = blk.contents
        ov = b.offset_vector
        hs, he = (ov[2 * self.n_h], ov[2 * self.n_h + 1]) if self.n_h < b.capture_top else (UNSET, UNSET)
        if self.n_p > 0:
            ps = ov[2 * self.n_p] if self.n_p < b.capture_top else UNSET
            if hs == UNSET or ps == UNSET or hs < ps:
                hs = UNSET
        val = None if hs == UNSET else self.subj[hs:he]
        ok = (self.opt if val is None else self.test(val))
        if ok:
            self.last = val
        return 0 if ok else 1

    def _match(self, s, start, flags):
        self.subj = s
        md = PC2.pcre2_match_data_create_from_pattern_8(self.code, None)
        sb = s.encode()
        rc = PC2.pcre2_match_8(self.code, sb, len(sb), start, flags, md, self.mctx)
        if rc < 0:
            return None
        ov = PC2.pcre2_get_ovector_pointer_8(md)
        return (ov[0], ov[1], None)

    def whole(self, s):
        return self._match(s, 0, 0x80000000 | 0x20000000) is not None

    def at(self, s, i, nonempty=False):
        return self._match(s, i, 0x80000000 | (0x00000008 if nonempty else 0))

    def search(self, s, frm=0):
        return self._match(s, frm, 0)

    def findall(self, s):
        return Prog.findall(self, s)
