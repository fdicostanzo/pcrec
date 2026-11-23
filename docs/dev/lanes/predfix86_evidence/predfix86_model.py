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
#             CALLER writes inside an argument that a body closes (`[_ = rx]`, `[_p = rx]`, or `_` passed to a label
#             parameter's spot) is not closed: the read passes, as a sent label's does; the read through the
#             argument's name (`B(A) & (A.d: ..)`) stays a compile error naming the closed door.
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
    ("s5", "CLOSEOWN", "a caller's own label under a closing body closed with the door (R1's ruling undone)"),
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
    ("s19", "EXPAND", "the expansion drill's written-out form of `_` on a spot is a plain group"),
    ("s20", "OPTENTRY", "`?:` reads an absent left part as failing (the plain `:`)"),
    ("s21", "NEGATION", "a request under `NOT` accepted"),
    ("s22", "ZEROLOOP", "the loop's body run alone (`0` read from the pass's start, as candidate (a))"),
    ("s23", "READINGS", "a reading's engine arm moved: the last fitting JSON member read as the first"),
    ("s24", "SWEEP", "one declared moved answer removed"),
    ("s25", "SUCCESSOR", "one declared red removed"),
    ("s26", "QUOTES", "an owner sentence in the documents altered (a word dropped)"),
    ("s27", "DOC", "a formatted line altered"),
    ("s28", "DOC", "a line looked for under another piece's tag (the tag ignored no longer)"),
    ("s29", "WHEN", "the then-read of a label the caller writes in the test refused (the withdrawn reading (b))"),
    ("s30", "ARGLABEL", "ARGLABEL off: a label written in an argument is the template's again"),
    ("s31", "LABELPARAM", "LABELPARAM writes the body's parameter name, not the caller's, on the spot"),
    ("s32", "PRINCIPLE", "the user's loop lowered as one definition looped (the binding's entry no longer clears)"),
    ("s33", "ARGSHAPES", "the label set read tighter than `|` no longer"),
    ("s34", "NULLABLE", "a nullable loop added to the programs run"),
    ("s36", "LPRULES", "a label-only group with a partial label-parameter name accepted"),
    ("s35", "QUOTES", "R1's record read at the lane's starting commit, before closing-own-label (the pin moved)"),
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
for _mine, _theirs in (("s30", "s2"), ("s21", "s9"), ("s20", "s7")):
    if sx(_mine):
        SABF.add(_theirs)                                    # predfold1123's own engine switch for that rule
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
OWNARG = set()                # the names the caller writes inside a plain argument of a label-parameter macro
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
                if lm2 and not sx("s36"):
                    for g in re.finditer(r"\(\?<:([^>]*)>", mm.group(3)):
                        if "${%s}" % lm2.group(1) in g.group(1) and g.group(1) != "${%s}" % lm2.group(1):
                            raise CompileError("`(?<:%s>`: a label-only group's name hole must be the whole name (a "
                                               "compile error, label-hole-full: \"pure label must be whole\")"
                                               % g.group(1))
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
                for n1, n2 in re.findall(r"\[(\w+) = |\(\?<:?(\w+)>", a):
                    if (n1 or n2) and not (n1 or n2).startswith("_"):
                        OWNARG.add(n1 or n2)         # argument-label: the caller's own, whatever the macro's kind
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
    OWNARG.clear()
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
    if sx("s29"):                                            # the plant: the withdrawn reading (b) of `when`
        for mm in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\(", expr):
            if mm.group(1) in UMAC:
                j = close_paren(expr, mm.end() - 1)
                written = set(re.findall(r"\(\?<(\w+)>", expr[mm.end():j]))
                for a in split_top(expr[mm.end():j], ","):
                    if is_cond(a.strip()) and any(re.search(r"\(%s: " % n_, a) for n_ in written):
                        raise CompileError("a read in an argument of a label written in another argument "
                                           "(the withdrawn reading (b))")
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
                if shut and not (head in SENT and not sx("s4")) and not (head in OWNARG and not sx("s5")):
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
                elif head in OWNARG and "top" not in sc and not sx("s5"):
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
    mn = re.fullmatch(r"/(\(\?:\(\?<(\w+)>[^/]*\)\?\)\*\w*)/ & \(\2 (\?)?: <(\d)\)", pt)
    if x_on() and mn:                                        # a nullable loop body: NULLPASS's libpcre2 runner
        try:
            wh, sr, fa = modes_of(line)
        except Exception:                                    # noqa: BLE001
            return "unparsed", ""
        n_ = int(mn.group(4))
        got = fmt(PcreLoopLabel(mn.group(1), mn.group(2), bool(mn.group(3)), lambda v: int(v) < n_), wh, sr, fa)
        return ("same" if got == strip_annot(a) else "DIFF"), got
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


# ================================================================== the checks
LINES.clear()
RUN.clear()
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def run(expr, binds=()):
    """(the program, None) or (None, the refusal); a crash (a plant may cause one) is a refusal naming it."""
    try:
        return prog(expr, list(binds)), None
    except CompileError as e:
        return None, str(e)
    except Exception as e:                                   # noqa: BLE001
        return None, "CRASH %s: %s" % (type(e).__name__, e)


def lab_at(Pg, t, n):
    """The label n on WHOLE t, or "no match"."""
    if Pg is None or not Pg.whole(t):
        return "no match"
    return label_of(whole_state(Pg, t), n)


def bt(binds):                                               # noqa: F811
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def pl(label, expr, binds, wh, sr, fa, tag, tail="", ann=None, bdesc=None, P=None):
    """A printed three-mode line, formatted from the run (or from P, a program run elsewhere); `ann` names labels
    shown on WHOLE texts that hold."""
    Pg, err = (P, None) if P is not None else run(expr, binds)
    if Pg is None:
        doc_line("%s: REFUSED (%s)" % (label, err), tag)
        print("   REFUSED [%s] %s: %s" % (tag, label, err))
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
    doc_line(L_, tag)
    print("   LINE [%s] %s" % (tag, L_))
    return Pg


def rlx(label, expr, binds, key, tail, tag, now=""):
    """A printed refusal line; the refusal's message must name `key`."""
    Pg, err = run(expr, binds)
    L_ = "%s: modes: a compile error%s (`%s`%s%s)." % (label, now, expr, bt(binds), tail)
    doc_line(L_, tag)
    print("   LINE [%s] %s\n      (refusal: %s)" % (tag, L_, err))
    return err is not None and key in err, err


def rl(label, expr, binds, key, reason, tag):
    return rlx(label, expr, binds, key, ": " + reason, tag)


def refused(expr, binds, key):
    Pg, err = run(expr, binds)
    print("   RUN `%s`%s: %s" % (expr, bt(binds), ("refused: " + err) if err else "legal"))
    return err is not None and key in err


def wh_(Pg, texts):
    return [Pg.whole(t) for t in texts] if Pg is not None else None


ARGT = "core/labels/export/arguments"
A_D = "A := /(?<d>\\d)/"
A_H = "A := /(?<h>\\d)/"
ISO = 'isodate := [year = /\\d{4}/] SEQ "-" SEQ [month = /\\d\\d/] SEQ "-" SEQ [day = /\\d\\d/]'
B_XX = "B(rx) := /${rx}xx/"
B_CL = "B(rx) := /${[_ = rx]}xx/"
A1 = "A(l:) := /(?<:${l}>\\d+)/"
A_ONE = "A(l:) := /(?<:${l}>\\d)/"
W_ = "W(l:, v) := /<${[l = v]}>/"
W4_ = "W4(v) := /<${[_ = v]}>/"
W5_ = "W5(l:, v) := /<${(v)}>/" if sx("s19") else "W5(l:, v) := /<${[_ = v]}>/"   # `_` on the spot, written out
S_ = "S(l:) := /\"(?<:${l}>\\d)\"/"
IDN = "identity(x) := /${[(=) = x]}/"
H_ = "/(?<h>\\d)?x/"

print("== CONTROL: the loaded matcher against python `re`, the FIX86 extensions on")
QD = pop("37!", 3)
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("identity(A)", ["A := /(?<d>\\d)/", IDN]), QD), answers(Re(r"\d" if not sx("s1") else r"\d!?"), QD))
QJ = pop('a"\\x', 3)
c3 = ndiff(answers(prog('/"(?<:s>(?:[^"\\\\]|\\\\.)*)"/'), QJ), answers(Re(r'"(?:[^"\\]|\\.)*"'), QJ))
QW = pop("<3>", 3)
P_c4c = run("W4([a = A]) & (a.h: <5)", ["W4(v) := /<${[_ = v]}>/", A_H])[0]
c4 = ndiff(answers(P_c4c, QW), answers(Re(r"<[0-4]>"), QW)) if P_c4c is not None else "refused"
check("CONTROL", (c1, c2, c3, c4) == ((0, 0, 0),) * 4, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; "
      "`identity(A)` against `\\d` %s over %d texts; a label-only group around a negated class against python `re` "
      "%s over %d texts; a caller's own label under a closing body against `<[0-4]>` %s over %d texts"
      % (c1, c2, len(QD), c3, len(QJ), c4, len(QW)))

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
               "`d` is written in A's text, not the caller's, and B uses A alone; argument-default", ARGT)
P_rep = pl("A label written on the argument", "rx.repeat([a = rx.digit], min = 1) & (a: <5)", [], ["3", "73", "37"],
           "7 3", "37 73 4", "lib/rx/repeat", ann=["a"])
P_hit = pl("Bare, the caller's own", 'hits(/a(?<g>x)?/) & (g: "x")', [], ["ax", "a", "axa"], "a ax", "a ax ax",
           "lib/search/hits")
al_ok = (P_al1 is not None and wh_(P_al1, ["3xx", "7xx"]) == [True, False] and P_al2 is not None and
         wh_(P_al2, ["7,3", "3,7"]) == [True, False] and wh_(P_al3, ["3-7", "7-3"]) == [True, False] and
         all(x is not None for x in (P_al4, P_al5, P_al6, P_rep, P_hit)) and ok_e)
check("ARGLABEL", al_ok, "legal and the caller's own: `B([f = ..])` %s, placed twice (the last mention) %s, an in-place "
      "group read bare %s, `B([a = A]) & (a.d: ..)` %s, `B([d = isodate])` %s, the read inside the argument %s, "
      "`rx.repeat([a = rx.digit], ..)` then `a` %s, `hits(/a(?<g>x)?/)` then `g` %s; the ruled `B(A) & (A.d: ..)` "
      "refused %s (%s)" % tuple([x is not None for x in (P_al1, P_al2, P_al3, P_al4, P_al5, P_al6, P_rep, P_hit)] +
                                [ok_e, r_e]))

print("== LABELPARAM (the label parameter): the caller's name on the spot")
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
P_om = pl("The unspecified label", 'A(_:) SEQ "!"', [A_ONE], ["3!", "7!"], "x3!", "3! 7!",
          "core/operators/bindings/label-omitted")
A2 = "A2(l = _:) := /(?<:${l}>\\d+)/"
P_df1 = pl("Passed by name", "A2(l = x:) & (x: 5)", [A2], ["5", "55", "7"], "7 5", "5 7 56 15",
           "core/operators/bindings/label-default")
P_df2 = pl("Left out, the default `_`", "A2()", [A2], ["5", "55", "x"], "x5", "5 7", "core/operators/bindings/label-default")
P_k3 = pl("A body reading its own label after placing it", "C(x:)", ["C(l:) := /(?<:${l}>\\d)/ & (l: <5)"],
          ["3", "7"], "7 3", "3 7 4", "core/operators/bindings/label-kinds")
P_fw = pl("Passed on", "B(x:) & (x: <5)", ["B(l:) := /<${A(l:)}>/", A_ONE], ["<3>", "<7>"], "<7> <3>", "<3> <7> <4>",
          "core/operators/bindings/label-forward")
P_fw2 = pl("Passed on across `|`", "V(x:) & (x: <5)", ["V(l:) := A(l:) | E(l:)", A_ONE, "E(l:) := /e(?<:${l}>\\d)/"],
           ["3", "e3", "e7"], "e7 3", "3 e7 e4", "core/operators/bindings/label-forward", ann=["x"])
P_ia = pl("Sent inside the argument, `_` on the outer spot", "W(_:, S(body:)) & (body: <5)", [W_, S_],
          ['<"3">', '<"7">'], '<"7"> <"3">', '<"3"> <"7"> <"4">', "core/operators/bindings/label-in-argument")
P_ia2 = pl("The outer body using the argument alone", "W3(S(body:)) & (body: <5)", ["W3(v) := /<${v}>/", S_],
           ['<"3">', '<"7">'], '<"7"> <"3">', '<"3"> <"7"> <"4">', "core/operators/bindings/label-in-argument")
P_ae = pl("A caller's label on the spot", "R(x:, isodate) & (x.year: 2000)",
          ["R(l:, v) := /${[l = v]}xx/", ISO], ["2000-01-02xx", "2001-01-02xx"], "1999-12-31xx 2000-03-04xx",
          "2000-01-02xx 2001-01-02xx 2000-12-31xx", ARGT)
lp_ok = (all(x is not None for x in (P_lp1, P_lp2, P_lp3, P_lp4, P_om, P_df1, P_df2, P_k3, P_fw, P_fw2, P_ia, P_ia2,
                                     P_ae)) and ok_lp5 and wh_(P_lp1, ["5", "55"]) == [True, False] and
         wh_(P_lp2, ["7,5", "5,7"]) == [True, False] and wh_(P_fw, ["<3>", "<7>"]) == [True, False])
check("LABELPARAM", lp_ok, "his example and the twice-placed reads legal with the record's answers %s; across `&` "
      "refused %s; `_`, the default, a body reading its own placed label, passed on (twice, across `|`), sent inside "
      "an argument, a caller's label on the spot: all legal %s"
      % (P_lp2 is not None and P_lp2.whole("7,5"), ok_lp5,
         all(x is not None for x in (P_om, P_df1, P_df2, P_k3, P_fw, P_fw2, P_ia, P_ia2, P_ae))))

print("== LPRULES (A2, A8, B12, label-kinds, label-hole-full): the label parameter's refusals")
ok_om2, r_om2 = rl("A body placing then reading its label, passed `_`", "C(_:)", ["C(l:) := /(?<:${l}>\\d)/ & (l: <5)"],
                   "label-parameter-omitted", "the body reads `l` and `_` names nothing to read",
                   "core/operators/bindings/label-omitted")
ok_dn, r_dn = rl("A default naming a label", "A2() & (ts: 5)", ["A2(l = ts:) := /(?<:${l}>\\d+)/"],
                 "default is `_` only", "for now the head default is `_` only", "core/operators/bindings/label-default")
ok_k1, r_k1 = rl("The reference kind in a user macro", "A(x:, /\\w/)", ["A(a:, B) := B & (a: 5)"], "reference kind",
                 "A reads a label it never places, off limits for users", "core/operators/bindings/label-kinds")
ok_k2, r_k2 = rl("A path as a marked argument", "A(x.d:)", [A_ONE], "ONE new name", "a marked argument is one new name",
                 "core/operators/bindings/label-kinds")
ok_hf, r_hf = rl("A partial label-only name", 'A(x:) SEQ "!"', ["A(l:) := /(?<:f_${l}>\\d)/"], "label-hole-full",
                 "the name hole of a label-only group must be the whole name", "core/holes/name")
ok_dl = refused("A(x:)", ["A(l:) := /(?<:${l}>\\d+)/ & ($l: 5)"], "not defined")
ok_mk = refused("W(y:, x:)", [W_], "a marked label")
check("LPRULES", ok_om2 and ok_dn and ok_k1 and ok_k2 and ok_hf and ok_dl and ok_mk,
      "refused: a body placing then reading `_` %s (%s); a named head default %s (%s); the reference kind at the "
      "definition %s; a path as a marked argument %s; a partial label-only name %s (%s); `$l` in the body %s; a "
      "marked argument for a plain parameter %s" % (ok_om2, r_om2, ok_dn, r_dn, ok_k1, ok_k2, ok_hf, r_hf, ok_dl, ok_mk))

print("== CLOSE (B1, B2): `_` on a spot is `[_ = ..]`; a condition inside a closed argument reads; the backdoor")
ok_cl1, r_cl1 = rl("Closed by `_`", "W(_:, A) & (A.h: <5)", [W_, A_H], "A",
                   "`_` on the spot is `[_ = v]`, which closes the door through A", "core/operators/bindings/label-omitted")
ok_cl2 = refused("W(_:, A) & (h: <5)", [W_, A_H], "")
P_cl3 = run("B([a = A] & (a.h: <5))", [A_H, B_CL])[0]
P_cl4 = run("B(/(?<g>\\d)/ & (g: <5))", [B_CL])[0]
cl_ok = ok_cl1 and ok_cl2 and wh_(P_cl3, ["3xx", "7xx"]) == [True, False] and \
    wh_(P_cl4, ["3xx", "7xx"]) == [True, False] and wh_(P_ia, ['<"3">', '<"7">']) == [True, False] and \
    wh_(run("W(_:, S(body:)) & (body: <5)", [W_, S_])[0], ['<"3">', '<"7">']) == [True, False]
check("CLOSE", cl_ok, "`W(_:, A) & (A.h: ..)` refused %s (%s), bare `h` refused %s; a condition inside a closed "
      "argument reads (`3xx`/`7xx`): a part label %s, an in-place group %s; the backdoor (a sent label through `_`) "
      "passes %s" % (ok_cl1, r_cl1, ok_cl2, wh_(P_cl3, ["3xx", "7xx"]), wh_(P_cl4, ["3xx", "7xx"]),
                     wh_(run("W(_:, S(body:)) & (body: <5)", [W_, S_])[0], ['<"3">', '<"7">'])))

print("== CLOSEOWN (A3, R1: closing-own-label RULED pass): the caller's own label passes a closing body; the door "
      "through the argument's name stays shut")
CAT = "core/labels/paths/closed-argument"
P_co1 = pl("The caller's own label, under a closing body", "B([a = A]) & (a.h: <5)", [A_H, B_CL], ["3xx", "7xx"],
           "7xx 3xx", "3xx 7xx 4xx", CAT)
ok_co2, r_co2 = rl("Closed by the macro", "B(A) & (A.d: <5)", [A_D, B_CL], "closes the door",
                   "`[c = B(A)] & (c.d: <5)` alike: no `d` is exported, a compile error by the reading in "
                   "core/labels/paths, a label not visible through its source", CAT)
L_co2 = LINES.pop()
LINES.append((L_co2[0], L_co2[1].replace("`, A := `/(?<d>\\d)/`, B(rx) := `/${[_ = rx]}xx/`: `[c = B(A)]",
                                         "`, A := `/(?<d>\\d)/`, B(rx) := `/${[_ = rx]}xx/`; `[c = B(A)]")))
ok_co3 = refused("[c = B(A)] & (c.d: <5)", [A_D, B_CL], "")
B_CP = "B(rx) := /${[_p = rx]}xx/"
ok_co4, r_co4 = rlx("Closed by a `_` part label", "B(A) & (A.d: <5)", [A_D, B_CP], "",
                    "; `c.d` and `B.d` alike; inside its binding a `_` part label is an ordinary one: the line "
                    "\"Statement 6\", core/labels/export", CAT)
QCO = ["3xx", "7xx", '"3"xx', '"7"xx']
kinds = [("a part label", "B([a = A]) & (a.h: <5)", [A_H, B_CL], ["3xx", "7xx"]),
         ("an in-place group", "B(/(?<g>\\d)/) & (g: <5)", [B_CL], ["3xx", "7xx"]),
         ("a sent label", "B(S(body:)) & (body: <5)", [B_CL, S_], ['"3"xx', '"7"xx']),
         ("a part label, `_p`", "B([a = A]) & (a.h: <5)", [A_H, B_CP], ["3xx", "7xx"]),
         ("a part label, `_` to a label parameter", "W(_:, [a = A]) & (a.h: <5)", [W_, A_H], ["<3>", "<7>"]),
         ("an in-place group, `_` to a label parameter", "W(_:, /(?<g>\\d)/) & (g: <5)", [W_], ["<3>", "<7>"])]
kd = [(k, wh_(run(e, b)[0], t)) for k, e, b, t in kinds]
co_ok = wh_(P_co1, ["3xx", "7xx"]) == [True, False] and all(v == [True, False] for _, v in kd) and ok_co2 and \
    ok_co3 and ok_co4
check("CLOSEOWN", co_ok, "the caller's own label under a closing body (`3xx`/`7xx` or `<3>`/`<7>`): %s; refused "
      "through the argument's name: `A.d` %s (%s), `c.d` %s, under a `_p` part label %s" % (kd, ok_co2, r_co2, ok_co3,
                                                                                         ok_co4))

print("== EXPAND (the expansion drill, review r86 lesson 1): each sugar form against its documented written-out "
      "expansion; legality and answers agree")
QX = ['<3>', '<7>', '<"3">', '<"7">', '3!', '7!', '5', '55', 'x']
DRILL = [   # (sugar, its binds, the written-out form, its binds, the documented expansion)
    ("W(_:, A) & (A.h: <5)", [W_, A_H], "W5(y:, A) & (A.h: <5)", [W5_, A_H], "`_` on a spot is `[_ = v]` (label-omitted (a))"),
    ("W(_:, [a = A]) & (a.h: <5)", [W_, A_H], "W5(y:, [a = A]) & (a.h: <5)", [W5_, A_H], "the same, a caller's own label"),
    ("W(_:, /(?<g>\\d)/) & (g: <5)", [W_], "W5(y:, /(?<g>\\d)/) & (g: <5)", [W5_], "the same, an in-place group"),
    ("W(_:, S(body:)) & (body: <5)", [W_, S_], "W5(y:, S(body:)) & (body: <5)", [W5_, S_], "the same, a sent label"),
    ("W(_:, [a = A]) & (a.h: <5)", [W_, A_H], "W4([a = A]) & (a.h: <5)", [W4_, A_H], "the same through a plain macro"),
    ('A(_:) SEQ "!"', [A_ONE], '/(?:\\d)/ SEQ "!"', [], "`(?<:${l}>..)` with `_` a plain non-capturing group"),
    ("A(x:) & (x: 5)", [A1], "/(?<:x>\\d+)/ & (x: 5)", [], "the caller's name on the spot"),
    ("A2()", [A2], "A2(l = _:)", [A2], "a left-out label parameter is its default `_`"),
    ('/(?<h>\\d)?x/ & (h ?: <5)', [], '/(?<h>\\d)?x/ & (h = "0": <5)', [], "`?:` as a default inside the set"),
]
xd_bad = []
for a_, ab, b_, bb, why in DRILL:
    Pa, ea = run(a_, ab)
    Pb, eb = run(b_, bb)
    same = (Pa is None) == (Pb is None) and (Pa is None or answers(Pa, QX) == answers(Pb, QX))
    print("   %s `%s` / `%s`: %s, %s (%s)" % ("AGREE" if same else "DIFFER", a_, b_, "refused" if Pa is None else
                                            "legal", "refused" if Pb is None else "legal", why))
    if not same:
        xd_bad.append(a_)
check("EXPAND", not xd_bad, "%d sugar forms against their written-out expansions, legality and every mode over %d "
      "texts; differing: %s" % (len(DRILL), len(QX), xd_bad or "none"))

print("== OPTENTRY (optional-label, ruled; `?:` his lean): absent or in S")
OPT_T = "core/conditions/form/optional-entry"
P_o1 = pl("The entry `?:`", H_ + " & (h ?: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o2 = pl("The plain entry", H_ + " & (h: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o3 = pl("The default inside the set", H_ + ' & (h = "0": <5)', [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
P_o4 = pl("Under `NOT`", H_ + " & NOT (h ?: <5)", [], ["x", "3x", "7x"], "7x x", "7x 3x x", OPT_T)
o_ok = (wh_(P_o1, ["x", "3x", "7x"]) == [True, True, False] and wh_(P_o2, ["x", "3x", "7x"]) == [False, True, False]
        and P_o3 is not None and answers(P_o1, pop("37x", 3)) == answers(P_o3, pop("37x", 3)) and
        wh_(P_o4, ["x", "3x", "7x"]) == [False, False, True])
check("OPTENTRY", o_ok, "`(h ?: <5)` on `x`/`3x`/`7x`: %s; the plain entry %s; `?:` and the default inside the set "
      "alike over %d texts; `NOT (h ?: <5)` %s" % (wh_(P_o1, ["x", "3x", "7x"]), wh_(P_o2, ["x", "3x", "7x"]),
                                                  len(pop("37x", 3)), wh_(P_o4, ["x", "3x", "7x"])))

print("== EDGES (A1): optional-label's conservative edges stand; optional-entry-edges' candidate (b) run")
JV = "/(?<a>\\d)?,(?<b>\\d)?/"
ok_ed1, r_ed1 = rlx("A joint left part", JV + " & ((a, b) ?: >= (5, 3))", [], "joint", "", OPT_T, now=" for now")
ok_ed2, r_ed2 = rlx("A value left part", JV + " & (($a + $b) ?: <10)", [], "value left", "", OPT_T, now=" for now")
ok_ed3, r_ed3 = rlx("Inside a group question", '/(?<h>\\d);(?:(?<h>\\d);)*/ & some((h ?: "7"))', [], "group question",
                    "", OPT_T, now=" for now")
EDT = "core/conditions/form/optional-edges"
CAND["edges"] = "candidate"
P_ec1 = pl("Candidate (b) of optional-entry-edges, a joint left part", JV + " & ((a, b) ?: >= (5, 3))", [],
           ["6,1", "5,3", "5,1", ",1", ",9", "5,", "2,", ","], "5,1 ,1 6,0", "5,1 5,4 ,1 2, 7,", EDT)
P_ec2 = pl("Candidate (b) of optional-entry-edges, the joint", JV + ' & ((a, b) ?: ("5", "3"))', [],
           [",9", "5,3", ",3", "5,9"], "5,9 ,9", "5,9 ,9 5,3", EDT)
P_ec4 = pl("Candidate (b) of optional-entry-edges, a value left part", JV + " & (($a + $b) ?: <10)", [],
           ["3,4", "6,7", ",4", "3,"], "6,7 3,", "6,7 3,4 ,4", EDT)
CAND["edges"] = "error"
P_ec3 = pl("The record of the same entries", JV + ' & (a ?: "5", b ?: "3")', [], [",9", "5,3", ",3", "5,9"], "5,9 ,9",
           "5,9 ,9 5,3", EDT)
cost = P_ec2 is not None and P_ec3 is not None and P_ec2.whole(",9") and not P_ec3.whole(",9")
check("EDGES", ok_ed1 and ok_ed2 and ok_ed3 and P_ec1 is not None and P_ec4 is not None and cost,
      "refused for now: a joint left part %s, a value left part %s, inside a group question %s; the candidate lines "
      "run %s; the joint candidate's cost (`,9`: the joint HOLDS, the record's entries FAIL) %s"
      % (ok_ed1, ok_ed2, ok_ed3, P_ec1 is not None and P_ec4 is not None, cost))

print("== NULLPASS (A7): a nullable loop body, run through libpcre2 with a per-pass marker")
NPX = "/(?:(?<h>\\d)?)*x/"
P_np1 = PcreLoopLabel("(?:(?<h>\\d)?)*x", "h", True, lambda v: int(v) < 5)
P_np2 = PcreLoopLabel("(?:(?<h>\\d)?)*x", "h", False, lambda v: int(v) < 5)
NPW = ["x", "3x", "7x", "73x"]
np_tail = "; with `:` " + fmt(P_np2, NPW, "7x", "7x").split(" / ")[0]
pl("A loop that can match empty", NPX + " & (h ?: <5)", [], NPW, "7x 3x", "7x 3x x", OPT_T, P=P_np1,
   bdesc=np_tail)
np_ok = wh_(P_np1, NPW) == [True, True, True, True] and wh_(P_np2, NPW) == [False, True, False, True]
check("NULLPASS", np_ok, "`?:` on `x`/`3x`/`7x`/`73x`: %s (never rejects: the trailing empty pass leaves h unset); `:` "
      "%s" % (wh_(P_np1, NPW), wh_(P_np2, NPW)))

print("== CAPTURE (the request): the set side, `?:`, an `&` operand; after a loop, the label rules")
CAP_T = "lib/structural/capture"
P_c1 = pl("Requires the label", H_ + ' & (h: capture("h"))', [], ["x", "3x"], "x 3x", "x 3x x", CAP_T, ann=["h"])
P_c2 = pl("If present", H_ + ' & (h ?: capture("h"))', [], ["x", "3x"], "x 3x", "x 3x x", CAP_T, ann=["h"])
P_c3 = pl("The stretch", '/\\d+/ & capture("n")', [], ["12", "x"], "x12", "1 22", CAP_T)
P_c4 = pl("Requested twice, the last mention", 'A SEQ "," SEQ A', ['A := [d = /\\d+/] & (d: capture("d"))'],
          ["7,5", "7"], "x7,5 1,2", "7,5 1,2", CAP_T, ann=["d"])
P_c5 = pl("Through the label's path", 'isodate & (isodate.year: capture("year"))', [ISO], ["2025-01-02"],
          "x 2025-01-02", "2025-01-02 1999-12-31", CAP_T, ann=["year"])
P_c6 = pl("After a loop", '/(?:(?<h>\\d)?;)+/ & (h ?: capture("h"))', [], ["3;;", "3;", "3;4;"], "3;; 3;", "3; ;",
          CAP_T, ann=["h"])
re_h = re.fullmatch(r"(?:(?P<h>\d)?;)+", "3;;").group("h")
c_ok = (wh_(P_c1, ["x", "3x"]) == [False, True] and P_c2 is not None and P_c2.whole("x") and P_c3 is not None and
        lab_at(P_c4, "7,5", "d") == "5" and P_c5 is not None and lab_at(P_c6, "3;;", "h") is None and re_h == "3")
check("CAPTURE", c_ok, "`(h: capture(\"h\"))` on `x`/`3x` %s; `(h ?: ..)` on `x` %s; `rx & capture(\"n\")` runs %s; "
      "requested twice, d = %r; through a path %s; after a loop on `3;;` h = %r (python `re`'s carried capture: %r)"
      % (wh_(P_c1, ["x", "3x"]), P_c2.whole("x") if P_c2 else None, P_c3 is not None,
         lab_at(P_c4, "7,5", "d"), P_c5 is not None, lab_at(P_c6, "3;;", "h"), re_h))

print("== CAPSET (A13, capture-in-set OPEN): the conservative reading refuses; the candidate (b) lines run")
CST = "lib/structural/capture/in-set"
ok_cs1, r_cs1 = rlx("Inside a union", H_ + ' & (h: "3" | capture("h"))', [], "capture-in-set",
                    '; `(h: <5 & capture("h"))`, `($a: capture("h"))` and `some((h: capture("h")))` alike: for now',
                    CST)
cs_alike = [refused(H_ + ' & (h: <5 & capture("h"))', [], "capture-in-set"),
            refused('/(?<h>\\d)?(?<a>\\d)?x/ & ($a: capture("h"))', [], "capture-in-set"),
            refused('/(?:(?<h>\\d);)+/ & some((h: capture("h")))', [], "capture-in-set")]
CAND["capset"] = "candidate"
P_cs2 = pl("Candidate (b) of capture-in-set, a union", H_ + ' & (h: "3" | capture("h"))', [], ["3x", "5x", "x"],
           "5x 3x", "3x 5x x", CST)
P_cs3 = pl("Candidate (b) of capture-in-set, an intersection", H_ + ' & (h: <5 & capture("h"))', [], ["3x", "5x", "x"],
           "5x 3x", "3x 5x x", CST)
CAND["capset"] = "error"
check("CAPSET", ok_cs1 and all(cs_alike) and wh_(P_cs2, ["3x", "5x", "x"]) == [True, True, False] and
      wh_(P_cs3, ["3x", "5x", "x"]) == [True, False, False],
      "refused for now: inside a union %s (%s), an intersection, a value left part, a group question %s; candidate "
      "(b): a union %s, an intersection %s" % (ok_cs1, r_cs1, cs_alike, wh_(P_cs2, ["3x", "5x", "x"]),
                                               wh_(P_cs3, ["3x", "5x", "x"])))

print("== NEGATION (capture-negated, broadened): an effect cannot be under negation")
NEG_T = "core/filters/negation/effects"
ok_n1, r_n1 = rl("Under `NOT`", H_ + ' & NOT (h: capture("h"))', [], "capture-negated", "an effect under negation",
                 NEG_T)
ok_n2, r_n2 = rl("Under `!`", H_ + ' & (h: !capture("h"))', [], "capture-negated", "an effect under negation", NEG_T)
P_n3 = pl("Beside a negation", H_ + ' & (h: capture("h")) & NOT (h: >= 5)', [], ["x", "3x", "7x"], "7x 3x",
          "7x 3x x", NEG_T)
ok_n4, r_n4 = rl("In `when`'s test", 'when(/(?<d>\\d)/ & (d: capture("d")), /x/)', [], "effect-in-guard",
                 "the test reaches the guard's `NOT peek(test)`; the manager's reading", NEG_T)
check("NEGATION", ok_n1 and ok_n2 and P_n3 is not None and ok_n4, "`NOT (h: capture(..))` refused %s, "
      "`(h: !capture(..))` refused %s; a request beside a negation legal %s; a request in `when`'s test refused %s"
      % (ok_n1, ok_n2, P_n3 is not None, ok_n4))

print("== ZEROLOOP (zero-in-loop (b)): `0` in a loop reads from the definition's start")
ZL = '((0: !contains("7")) SEQ /\\d/ SEQ ";")+'
P_z1 = run(ZL if not sx("s22") else '((0: !contains("7")) SEQ /\\d/ SEQ ";")', [])[0]
z_ok = P_z1 is not None and [P_z1.whole(t) for t in ("3;4;", "3;7;", "7;3;", "3;7;4;")] == [True, True, False, False]
check("ZEROLOOP", z_ok, "`%s` on `3;4;`/`3;7;`/`7;3;`/`3;7;4;`: %s (the record's run: HOLDS, HOLDS, FAILS, FAILS)" %
      (ZL, [P_z1.whole(t) for t in ("3;4;", "3;7;", "7;3;", "3;7;4;")] if P_z1 else None))

print("== ZEROBIND (zero-condition-binding, B5): a condition on `0` bound alone is an error, `NOT` and `((..))` too")
ZBT = "core/holes/bare-condition/zero-binding"
ok_zb, r_zb = rl("Bound alone", "c", ["c := (0: 5)"], "zero-condition-binding", "a condition on `0` bound alone; "
                 "`NOT (0: 5)` and `((0: 5))` bound alone alike, a reading", ZBT)
ok_zb2 = refused("c", ["c := NOT (0: 5)"], "zero-condition-binding")
ok_zb3 = refused("c", ["c := ((0: 5))"], "zero-condition-binding")
P_zb4 = pl("Written in place", "/\\d/ & (0: 5)", [], ["5", "7"], "x5", "5 7 5", ZBT)
check("ZEROBIND", ok_zb and ok_zb2 and ok_zb3 and P_zb4 is not None, "refused: `(0: 5)` %s, `NOT (0: 5)` %s, "
      "`((0: 5))` %s (no crash); written in place legal %s" % (ok_zb, ok_zb2, ok_zb3, P_zb4 is not None))

print("== ZEROOPEN (zero-open, B4): `0` is the one name read open; a request on `0` is complete only last")
MSF = "core/conditions/match-so-far"
P_zo1 = pl("Two reads on one path", '/\\d${(0: "3")}\\d${(0: "34")}/', [], ["34", "35", "44"], "x34 35", "34 35 34", MSF)
ok_zo2, _ = rl("A group question on `0`", '/(?<d>\\d)+/ & some((0: "1"))', [], "zero-open",
               "`0` has no settings, so no array", MSF)
ok_zo3, _ = rl("An index on `0`", '/(?<d>\\d)+/ & (0[1]: "1")', [], "zero-open", "`0` has no settings", MSF)
ok_zo4, _ = rl("A request on an open `0`", '/\\d${(0: capture("n"))}x/', [], "zero-open",
               "pattern text follows the hole, so `0` is open there; for now", CAP_T)
P_zo5 = pl("A request on `0` written last", '/\\d+${(0: capture("n"))}/', [], ["12", "x"], "a12", "1 22", CAP_T)
ok_zo6 = refused('/\\d${(0: capture("n"))}/ SEQ /x/', [], "zero-open")
ok_zo7 = refused('/\\d+/ & (0: capture("n")) SEQ /x/', [], "zero-open")
P_zo8 = pl("`$0` in a value hole", '/\\w+${$0}/', [], ["abab", "aba", "aa"], "xabab", "abab cc d", "core/values/reads")
QZ = ["abab", "aba", "aa", "abba", "x", "aaaa", "abcabc", "abcab"]
zo8 = P_zo8 is not None and answers(Re(r"(\w+)\1"), QZ) == answers(P_zo8, QZ)
check("ZEROOPEN", P_zo1 is not None and ok_zo2 and ok_zo3 and ok_zo4 and P_zo5 is not None and ok_zo6 and ok_zo7 and
      zo8, "two reads on one path %s; refused: a group question %s, an index %s, a request on an open `0` %s, last in "
      "its literal but not its definition %s, beside `&` then followed %s (no crash); written last legal %s; `$0` "
      "against python `re` `(\\w+)\\1` %s" % (P_zo1 is not None, ok_zo2, ok_zo3, ok_zo4, ok_zo6, ok_zo7,
                                               P_zo5 is not None, zo8))

print("== CONDARG (B3, A5): a condition passed as an argument reads where the body places it")
P_ca1 = pl("An argument placed beside `&`", "/a/ SEQ A((0: /x/), /\\w/)", ["A(c, B) := B & c"], ["ax", "ay"], "ay ax",
           "ax ay ax", MSF)
P_ca2 = pl("An argument placed in a sequence", "/a/ SEQ A2((0: /ax/), /\\w/)", ["A2(c, B) := /${B}${c}/"],
           ["ax", "ay"], "ay ax", "ax ay ax", MSF)
P_ca3 = run("A((h: <5), /(?<h>\\d)/)", ["A(c, B) := B & c"])[0]
check("CONDARG", wh_(P_ca1, ["ax", "ay"]) == [True, False] and wh_(P_ca2, ["ax", "ay"]) == [True, False] and
      wh_(P_ca3, ["3", "7"]) == [True, False],
      "beside `&` (`0` the left operand's match) %s; in a sequence (`0` the match so far) %s; label-kinds' advised "
      "`A((h: <5), /(?<h>\\d)/)` on `3`/`7` %s" % (wh_(P_ca1, ["ax", "ay"]), wh_(P_ca2, ["ax", "ay"]),
                                                   wh_(P_ca3, ["3", "7"])))

print("== WHEN (A4): a read in `then` of a label the caller writes in the test is legal")
WB = "W(a, b) := [(=) = a] SEQ [(=) = b]"
P_w1 = pl("A read in then", "W(/(?<h>\\d)/, (h: <5))", [WB], ["3", "7"], "7 3", "3 7 4", "lib/control/when",
          bdesc=bt([WB]) + "; `W(A, (A.h: <5))` with A := `/(?<h>\\d)/` the same answers")
P_w2 = run("W(A, (A.h: <5))", [WB, A_H])[0]
check("WHEN", P_w1 is not None and P_w2 is not None and answers(P_w1, pop("37x", 2)) == answers(P_w2, pop("37x", 2)),
      "the then-read legal %s; through the source the same answers %s" % (P_w1 is not None, P_w2 is not None))

print("== NEVER (B7): a caller's label no path of the body places draws `pcrec.test.never`; the read fails")
P_nv = run("B([n = /\\d/]) & (n: <5)", ["B(rx) := /xx/"])[0]
w_nv = list(WARNS)
check("NEVER", P_nv is not None and not P_nv.whole("xx") and ("pcrec.test.never", "n") in w_nv,
      "legal %s, `xx` %s, warnings %s" % (P_nv is not None, P_nv.whole("xx") if P_nv else None, w_nv))

print("== CALLNAME (A9): a sent label is read bare; through the macro's name or a label on the call, not offered")
ok_cn1, r_cn1 = rl("A sent label through the macro's name", "A(x:) & (A.x: 5)", [A1], "not offered",
                   "not offered for now; `[c = A(x:)] & (c.x: 5)` alike", ARGT)
ok_cn2 = refused("[c = A(x:)] & (c.x: 5)", [A1], "not offered")
P_cn3 = pl("Through the call, by path", "identity([a = A]) & (identity.a.h: <5)", [A_H, IDN], ["3", "7"], "7 3",
           "3 7 4", ARGT)
P_cn4 = run("identity([a = A]) & (a.h: <5)", [A_H, IDN])[0]
check("CALLNAME", ok_cn1 and ok_cn2 and wh_(P_cn3, ["3", "7"]) == [True, False] and
      answers(P_cn3, pop("37", 2)) == answers(P_cn4, pop("37", 2)),
      "refused: `A.x` %s (%s), `c.x` %s; `identity.a.h` by path %s, the same answers as `a.h` bare %s"
      % (ok_cn1, r_cn1, ok_cn2, wh_(P_cn3, ["3", "7"]), P_cn4 is not None))

print("== PRINCIPLE (binding-fixed): a user's loop around a binding agrees with it written out")
BB = "B := /${NOT (c: >= 5)}(?<c>\\d)/"
QP = pop("37;", 4)
P_u = prog('rx.repeat(B SEQ ";", min = 2, max = 2)', [BB])
P_w = prog('B SEQ ";" SEQ B SEQ ";"', [BB])
P_1 = prog("/(?:${NOT (c: >= 5)}(?<c>\\d);){2}/")
same_uw = answers(P_u, QP) == answers(P_w, QP)
diff_1 = answers(P_1, QP) != answers(P_w, QP)
if sx("s32"):
    P_u = P_1                                                # the plant: the user's loop lowered as ONE definition
    same_uw = answers(P_u, QP) == answers(P_w, QP)
check("PRINCIPLE", same_uw and diff_1, "over %d texts, every mode: a user's loop and the written-out uses agree %s; one "
      "definition looped differs %s" % (len(QP), same_uw, diff_1))

print("== ARGSHAPES: each shape of \"what an argument exports\" under argument-label")
P_as1 = pl("A part label on an argument of a list body", "identity([a = A]) & (a.h: <5)", [A_H, IDN], ["3", "7"],
           "7 3", "3 7 4", ARGT)
ok_as2, _ = rl("A read inside an argument, bare", 'B(A & (h: "3"))', [A_H, B_XX], "label-reference",
               "`h` is not written in the caller's text; label-reference", ARGT)
P_as3 = pl("A read inside an argument, with its source", 'B(A & (A.h: "3"))', [A_H, B_XX], ["3xx", "7xx"],
           "7xx 3xx", "3xx 7xx", ARGT)
P_as4 = pl("A part label over an expression in an argument", "atomic([ab = (B | A)]) & (ab.l: <20)",
           ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"], ["25", "13"], "25", "25 13", "core/patterns/atomic")
ok_as5, _ = rl("A binding in parentheses", "identity((A)) & (identity.h: <5)", [A_H, IDN], "not visible",
               "the argument's own text writes no label, A used alone in it", ARGT)
P_as6 = pl("A binding alone", "identity(A) & (identity.h: <5)", [A_H, IDN], ["3", "7"], "7 3", "3 7 4", ARGT)
ok_as7, _ = rl("A named list on a spot", "N(A) & (N.h: <5)", [A_H, "N(rx) := /${[(=h) = rx]}/"], "export-list",
               "a parameter exports nothing the definition can see, so the list names no exported label", ARGT)
LS_B = ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"]
P_ls1 = pl("", "[ab = (B | A)] & (ab.l: <20)", LS_B, ["25", "7"], "25", "25 13", "core/patterns/alternation", ann=["l"])
P_ls2 = pl("The label set beside `|`", "[ab = B | A] & (ab.l: <20)", LS_B, ["25", "13"], "25", "25 13",
           "core/operators/precedence")
if sx("s33"):
    P_ls2 = run("[ab = (B | A)] & (ab.l: <20)", LS_B)[0]
ls_differ = P_ls1 is not None and P_ls2 is not None and answers(P_ls1, ["25", "13"]) != answers(P_ls2, ["25", "13"])
check("ARGSHAPES", P_as1 is not None and ok_as2 and P_as3 is not None and P_as4 is not None and ok_as5 and
      P_as6 is not None and ok_as7 and ls_differ,
      "list body %s; bare read inside refused %s; with its source %s; atomic over an expression %s; `identity((A))` "
      "exports nothing %s; `identity(A)` exports `h` %s; a named list on a spot refused %s; the label set tighter than "
      "`|` %s" % (P_as1 is not None, ok_as2, P_as3 is not None, P_as4 is not None, ok_as5, P_as6 is not None, ok_as7,
                  ls_differ))

print("== MEANING (A10): where a used binding contributes the name, the composed and one-literal spellings part")
P_tw = pl("A used binding", "/(?<h>\\d)/ SEQ A & (h: <5)", ["A := /,(?<h>\\d)/"], ["1,7", "7,1"], "7,1 1,7",
          "1,7 7,1 1,2 9,9", "core/principles/meaning-not-spelling",
          bdesc=", A := `/,(?<h>\\d)/`; the one literal `/(?<h>\\d),(?<h>\\d)/ & (h: <5)` " +
          fmt(prog("/(?<h>\\d),(?<h>\\d)/ & (h: <5)"), ["1,7", "7,1"], "7,1", "7,1").split(" / ")[0])
P_tw2 = pl("The second shape, read bare", "/(?<h>\\d)/ SEQ A & (h: <5)", ["A := /,(?<h>\\d)/"],
           ["1,7", "7,1"], "7,1 1,7", "1,7 7,1 1,2 9,9", "core/labels/paths/two-sources")
P_one = prog("/(?<h>\\d),(?<h>\\d)/ & (h: <5)")
check("MEANING", wh_(P_tw, ["1,7", "7,1"]) == [True, False] and wh_(P_one, ["1,7", "7,1"]) == [False, True],
      "composed %s, one literal %s (`1,7`/`7,1`)" % (wh_(P_tw, ["1,7", "7,1"]), wh_(P_one, ["1,7", "7,1"])))

JSONL = ['ws := /[ ]*/', 'string(l:) := /"(?<:${l}>(?:[^"\\\\]|\\\\.)*)"/',
         'number(l:) := /(?<:${l}>-?\\d+(?:\\.\\d+)?)/', 'literal(l:) := /(?<:${l}>true|false|null)/',
         'value(l:) := string(l:) | number(l:) | literal(l:)',
         'member_any := ws SEQ string(_:) SEQ ws SEQ ":" SEQ ws SEQ value(_:) SEQ ws',
         'row(l:, k, f = anything) := /\\{(?:${member_any},)%s${ws}"${k}"${ws}:${ws}${value(l:) & (l: f)}${ws}'
         '(?:,${member_any})*\\}/' % ("*?" if sx("s23") else "*")]
print("== READINGS (B9): the manager's readings no other check runs; each row is the documents' own claim (printed "
      "SUPPORTED as run) against this run")
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
          '{"a":7,"b":8} {"a":3,"b":7}', '{"a":3} {"c":1} {"a":7,"b":8} {"b":4,"a":9}', "lib/json/members", ann=["x"],
          bdesc=", the sketch above")


def prog_or_none(t, binds):
    try:
        return prog(t, binds)
    except CompileError:
        return None


P_jk2 = prog_or_none('row(x:, "a" | "b")', JSONL)
P_mB = prog_or_none('row(m:, "msg") & (m: contains("timeout"))', JSONL)
P_mA = pl("A filter inside the argument", 'row(m:, "msg", contains("timeout"))', JSONL,
          ['{"msg":"db timeout"}', '{"msg":"ok"}', '{"msg":"timeout a","msg":"ok"}'], '{"msg":"ok"} {"msg":"db timeout"}',
          '{"msg":"ok"} {"msg":"db timeout"} {"msg":"timeout"}', "lib/json/members",
          bdesc=", the sketch above; `row(m:, \"msg\") & (m: contains(\"timeout\"))` the same answers")
P_m_ = run('row(_:, "msg", contains("timeout"))', JSONL)
QM = ['{"msg":"db timeout"}', '{"msg":"ok"}', '{"msg":"timeout a","msg":"ok"}', '{"msg":"ok","msg":"x timeout"}',
      '{"a":1,"msg":"t\\"q timeout"}']
QMS = " ".join(QM)
ab_same = P_mA is not None and P_mB is not None and [P_mA.whole(t) for t in QM] == [P_mB.whole(t) for t in QM] and \
    (P_mA.search(QMS) or (0, 0))[:2] == (P_mB.search(QMS) or (0, 0))[:2] and P_mA.findall(QMS) == P_mB.findall(QMS)
RD = [   # (the reading, the documents' claim, the run that decides it); rows another check runs are not repeated
    ("value-left (d): a value with no label is fixed at compile time", "SUPPORTED",
     lambda: P_vl is not None and P_vl.whole("x")),
    ("label-forward q1: a filter over two rows' labels at the line is an ordinary entry", "SUPPORTED",
     lambda: P_jc is not None and P_jc.whole('{"hi":7,"lo":3}') and not P_jc.whole('{"lo":7,"hi":3}')),
    ("label-forward q2: several keys, the LAST fitting member in the object's order", "SUPPORTED",
     lambda: P_jk2 is not None and label_of(whole_state(P_jk2, '{"a":3,"b":7}'), "x") == "7" and
     label_of(whole_state(P_jk2, '{"b":7,"a":3}'), "x") == "3"),
    ("JSON picture q1 (re-spelled with a named label, R2): a filter inside the argument and a test on the label "
     "agree in every mode", "SUPPORTED", lambda: ab_same),
    ("JSON sketch (R2): the filter-taking `row` refuses `_` (its body reads its label; reading (c))", "SUPPORTED",
     lambda: P_m_[0] is None and "label-parameter-omitted" in (P_m_[1] or "")),
    ("label-forward: on the data the string \"3\" and the number 3 read alike", "SUPPORTED",
     lambda: P_jl is not None and P_jl.whole('{"v":"3"}') and P_jl.whole('{"v":3}')),
]


def _verdict(f):
    try:
        return "SUPPORTED" if f() else "NOT SUPPORTED"
    except (CompileError, AttributeError, TypeError):
        return "NOT SUPPORTED"


RD = [(a, b, _verdict(c)) for a, b, c in RD]
rd_bad = [r[0] for r in RD if r[1] != r[2]]
for r in RD:
    print("   documents %s, run %s: %s" % (r[1], r[2], r[0]))
check("READINGS", not rd_bad, "%d readings run, each against the documents' printed claim: %s" %
      (len(RD), "all agree" if not rd_bad else "DISAGREE %s" % rd_bad))

print("== SWEEP: every printed three-mode line (`rejected:` and history lines skipped): predfold1123's engine (the "
      "FIX86 extensions off) over the starting commit's documents against this one over these; every non-same "
      "status and every moved answer DECLARED")
_d0 = _src84.index("NOTMOD = ")
_d1 = _src84.index('if s84("s13"):')
exec(compile(_src84[_d0:_d1], P84, "exec"), globals())      # noqa: S102  predfix84's DECL_LINE / DECL_RULE, verbatim
J_ = "a JSON sketch line: its bodies (`row`, `value`, `string`, ...) are in the line's prose, not its tail; READINGS runs it with them (JSONL)"
DECLX = {                     # (file, program) -> (status, reason): a line this engine does not reproduce
    ("library.md", 'row(v:, "v") & (v: "ok" | <5)'): ("REFUSED", J_),
    ("library.md", 'row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)'): ("REFUSED", J_),
    ("library.md", 'row(x:, "a" | "b") & (x: <5)'): ("REFUSED", J_),
    ("library.md", 'row(m:, "msg", contains("timeout"))'): ("REFUSED", J_),
}
DECL_RULEX = []               # first match, as predfix84's DECL_RULE (new rows here)
MOVEDX = {                    # program -> why its printed answer or legality moves: a disposition of r86
    "C(_:)": "r86 A2: a body that reads its label parameter, passed `_`, is a compile error at the call (the "
             "manager's reading (c) of label-parameter-omitted, restored); the line printed as a refusal (LPRULES)",
}
X86[0] = False
OLD_TX = sw_table84(OLDX)
X86[0] = True
NEW_TX = sw_table84(NOWS)
if sx("s24") and MOVEDX:
    MOVEDX.pop(next(iter(MOVEDX)))
swx_bad, swx_moved, swx_new, swx_gone, usedX = [], [], [], [], set()
cntX, whyX = {}, {}
for k, vs in NEW_TX.items():
    ov = OLD_TX.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cntX[st_] = cntX.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECLX.get((f_, k[0])) or DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                usedX.add((f_, k[0]))
                whyX[d_[1][:70]] = whyX.get(d_[1][:70], 0) + 1
            else:
                r_ = next((x for x in DECL_RULEX + DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    swx_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:160]))
                else:
                    usedX.add(r_[1])
                    whyX[r_[2][:70]] = whyX.get(r_[2][:70], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and o_[3] != got_:
            if k[0] in MOVEDX:
                usedX.add(("moved", k[0]))
            else:
                swx_moved.append((f_, ln_, k[0], o_[2], st_, o_[3][:120], got_[:120]))
    if not ov:
        swx_new.append((vs[0][0], vs[0][1], k[0]))
for k, vs in OLD_TX.items():
    if k not in NEW_TX:
        if k[0] in MOVEDX:
            usedX.add(("moved", k[0]))
        else:
            swx_gone.append((vs[0][0], vs[0][1], k[0], vs[0][2]))
staleX = sorted(k for k in DECLX if k not in usedX) + sorted(x[1] for x in DECL_RULEX if x[1] not in usedX) + \
    sorted(k for k in MOVEDX if ("moved", k) not in usedX)
for k_, n_ in sorted(whyX.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in swx_gone:
    print("   GONE %s:%d `%s` (was %s)" % x)
for x in swx_new:
    print("   ADDED %s:%d `%s`" % x)
for x in swx_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)\n      old: %s\n      now: %s" % x)
for x in swx_bad:
    print("   BAD %s" % (x,))
for x in staleX:
    print("   STALE DECLARATION %s" % (x,))
for k_, why in sorted(MOVEDX.items()):
    print("   ANSWER MOVED (declared): `%s`: %s" % (k_, why))
check("SWEEP", OLD_TX and not swx_bad and not swx_moved and not swx_gone and not staleX,
      "%d printed lines now (%s), %d at the starting commit under predfold1123's engine; undeclared %d; moved or gone "
      "and not declared %d; declared moves %d; added %d; stale declarations %d" %
      (len(NEW_TX), ", ".join("%s %d" % kv for kv in sorted(cntX.items())), len(OLD_TX), len(swx_bad),
       len(swx_moved) + len(swx_gone), len(MOVEDX), len(swx_new), len(staleX)))

print("== NULLABLE: EVID-4's known limit: no program the loaded engine ran has a loop whose body can match empty "
      "(NULLPASS's runs go through libpcre2, not the engine)")
exec(compile(_src84[_src84.index("def nullable(n):"):_src84.index("checked = list(RUN)")], P84, "exec"),
     globals())                                              # noqa: S102  predfix84's walker, verbatim
_nullable84 = nullable


def nullable(n):                                             # noqa: F811
    return False if n[0] == "ncls" else _nullable84(n)


checkedX = list(RUN)
if sx("s34"):
    checkedX.append(("/(?:(?<d>\\d)*)+/", (), P1123F["prog"]("/(?:(?<d>\\d)*)+/").node))
nlX = [(e, b) for e, b, nd in checkedX if loops_nullable(nd, [])]
check("NULLABLE", not nlX, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a loop "
      "whose body can match empty%s" % (len(checkedX), len(nlX), (": %s" % nlX[:4]) if nlX else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line (a red whose content changes under an unchanged name fails here)")
LANESX = os.path.normpath(os.path.join(HEREX, ".."))
SUPERSEDEDX = {               # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
    'predfold1123': {
        'DOC': ('30b0b3154c99', 'this lane rewrote four lines it formats, each by an r86 disposition (`C(_:)` refused, A2; the joint and value left parts compile errors for now, A1; "Bound alone" names `NOT` and `((..))`, B5); LPRULES, EDGES, ZEROBIND and DOC here'),
        'NULLABLE': ('3cb11f7daa34', 'its SWEEP runs the new nullable-loop line (A7) through its engine, which EVID-4 says it cannot; NULLPASS and SWEEP here run it through libpcre2'),
        'SWEEP': ('dc064aa89b32', "SWEEP here: the five lines are this lane's r86 lines (A3/R1 closing-own-label, A9 by path, A7 the nullable loop, A5 beside `&`, R2's json q1 with a named label), which its engine refuses or answers otherwise; CLOSEOWN, CALLNAME, NULLPASS, CONDARG, READINGS here"),
    },
    'predfix84': {
        'CONVENTION': ('6ec984243fdd', "as predfold1123 declared: the request has no body placing an argument (optional-label's statement), so `capture` left the covered list; ARGSHAPES here"),
        'DOC': ('1ab4ce1d8fd7', 'as predfold1123 declared: this fold rewrote lines it looks for (argument-label, two-sources, zero-binding, the request); SWEEP and DOC here'),
        'GRID': ('ff2c086f1de3', "as predfold1123 declared: ARGLABEL and ARGSHAPES here: argument-default's readings (a), (b) withdrawn by argument-label; the sentences it looks for rewritten"),
        'SWEEP': ('984981dd8662', "SWEEP here: the r86 lines (closing-own-label, the edges' candidates, the arguments beside `&`, the nullable loop) its engine does not read; each moved line declared there"),
    },
    'predspot': {
        'CONVENTION': ('6ec984243fdd', "as predfold1123 declared: the request has no body placing an argument (optional-label's statement), so `capture` left the covered list; ARGSHAPES here"),
        'DOC': ('c35db78094ed', 'as predfold1123 declared: this fold rewrote lines it looks for (argument-label, two-sources, zero-binding, the request); SWEEP and DOC here'),
        'FSWEEP': ('1a3772525ee0', 'the same six flag lines predfix84 declared, at line numbers this lane moved; SWEEP here'),
        'GRID': ('656ac2487a85', "as predfold1123 declared: ARGLABEL and ARGSHAPES here: argument-default's readings (a), (b) withdrawn by argument-label; the sentences it looks for rewritten"),
        'SUCCESSOR': ('3b691e065f6a', 'SUCCESSOR here: it re-runs the same models, each red declared in this table'),
        'SWEEP': ('825d6736d879', 'SWEEP here: the r86 lines its engine does not read; each moved line declared there'),
    },
    'predfix83': {
        'AWAITS': ('2b8a870671e7', 'as predfix84 declared: AWAITS here: argument-default is ruled, so no line awaits it (0 marked lines)'),
        'DOC': ('05476f118e2f', "as predfix84 declared: predspot's fold rewrote the texts it looks for (argument-default ruled; the bodies restated) and SWEEP here (each gone line RESPELLED, ERROR NOW or DROPPED) and DOC here"),
        'MARKS': ('378686a20835', "as predfold1123 declared: this fold rewrote the texts its marks look for (argument-default, two-sources, call-prefix, capture-export ruled); the pieces' history lines here"),
        'SUCCESSOR': ('0c38628fa5e1', 'SUCCESSOR here: it re-runs the same models, each red declared in this table'),
        'SWEEP': ('1a90686a09c6', 'SWEEP here: the r86 lines its engine does not read; each moved line declared there'),
        'UNMARKED': ('e4ca427dc5ca', 'as predfold1123 declared (argument-label made legal the lines its error engine refuses), at line numbers this lane moved; ARGLABEL and SWEEP here'),
    },
    'preddef': {
        'AWAITS': ('e8f86816cd7a', "as predfix84 declared: AWAITS here, as predfix83's"),
        'DOC': ('a80040d59ecb', 'as predfold1123 declared: this fold rewrote lines it looks for (argument-label, two-sources, zero-binding, the request); SWEEP and DOC here'),
        'MARKS': ('bed67315ff19', "this lane rewrote the texts its marks look for (statements 3 and 5, flow, call-prefix, argument-default, capture: review r86 A10, A11, C4-C8); the pieces' history lines here"),
        'SUCCESSOR': ('9ce8705eed79', 'as predfix84 declared: SUCCESSOR here'),
        'UNMARKED': ('45cec568555f', 'as predfold1123 declared (argument-label made legal the lines its error engine refuses), at line numbers this lane moved; ARGLABEL and SWEEP here'),
    },
    'predfix82': {
        'DOC': ('7ba579a211b8', 'as predfold1123 declared: this fold rewrote lines it looks for (argument-label, two-sources, zero-binding, the request); SWEEP and DOC here'),
        'MARKS': ('cadd463ec154', "as predfold1123 declared: this fold rewrote the texts its marks look for (argument-default, two-sources, call-prefix, capture-export ruled); the pieces' history lines here"),
        'REPRINT': ('49e1c7ae12f2', "as predfix84 declared: predspot's fold rewrote the texts it looks for (argument-default ruled; the bodies restated) and SPOT here (example 1 revised; its spot-labelled line) and SWEEP"),
        'SUCCESSOR': ('7af0ee27f19f', 'as predfix84 declared: SUCCESSOR here'),
    },
    'predcall': {
        'DOC': ('ee72c84698ec', "as predfix84 declared: predspot's fold rewrote the texts it looks for (argument-default ruled; the bodies restated) and ARGNAME and TWOSPOT here (call-prefix's lines re-spelled) and SWEEP"),
        'MARKS': ('bcf1e6378404', "closed-argument re-dated `ruled 2026-11-23` by closing-own-label (R1 of this lane's rulings file); its MARKS looks for the older date; CLOSEOWN here"),
        'PREDREF': ('bdc1a3daaa39', 'as predfix84 declared: SUCCESSOR here: predref is now a traceback (below), so its expected red is gone'),
        'SCAN': ('f1f330a86ca2', "as predfold1123 declared (the label parameter's lines read a label its scan does not know), with this lane's lines (`W(_:, A)`, `A(x:) & (A.x: 5)`, `A2() & (ts: 5)`); LABELPARAM, LPRULES, CALLNAME and SWEEP here"),
    },
    'predref': {
        'TRACEBACK': ('654619d66d03', "as predfix84 declared: SPOT and PLACES here: the provided bodies now write the export list on their spot (`atomic(X) := /(?>${[(=) = X]})/`, transform-export), which predref's lowerer, older than export-list, cannot read"),
    },
    'predbound': {
        'TRACEBACK': ('f8b5d917c866', "as predfix84 declared: SPOT and PLACES here, as predref's (its body reader meets `[(=) = x]`)"),
    },
    'predfix77': {
        'TRACEBACK': ('455b59c946bc', "as predfix84 declared: predfix83's SUCCESSOR, which declared it, and predfix82's REPRINT and predbound's checks, unchanged"),
    },
    'predarr': {
        'TRACEBACK': ('ce43d48c7e37', "as predfix84 declared: predfix83's SUCCESSOR, which declared it, and predfix82's REPRINT and predref's HITS, unchanged"),
    },
    'predscope': {
        'TRACEBACK': ('17ab1e47c179', "as predfix84 declared: TWOSPOT here: its reader of rx.repeat's third body expects `${x}`; the body now writes `${[(=) = x]}` (transform-export)"),
    },
}
MODELSX = ["predfold1123", "predfix84", "predspot", "predfix83", "preddef", "predfix82", "predcall", "predref",
           "predbound", "predfix77", "predarr", "predscope"]
if sx("s25") and SUPERSEDEDX:
    k0 = next(iter(SUPERSEDEDX))
    SUPERSEDEDX[k0].pop(next(iter(SUPERSEDEDX[k0])), None)
succX_bad, succX_n = [], 0
if not LIGHTX:
    for mname in MODELSX:
        env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")
               and not k.endswith("_PROBE")}
        if mname == "predfold1123":
            env["PREDFOLD_LIGHT"] = "1"                      # its own SUCCESSOR re-runs the eleven below: run once, here
        if mname == "predfix84":
            env["PREDFIX84_LIGHT"] = "1"
        out = subprocess.run([sys.executable, "-I", "-B", os.path.join(LANESX, mname + "_evidence", mname + "_model.py")],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, timeout=3600).stdout
        succX_n += 1
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
        decl = SUPERSEDEDX.get(mname, {})
        print("   %-12s last line: %s" % (mname, last[:160]))
        for r, fline in sorted(reds.items()):
            dg = hashlib.sha256(fline.encode()).hexdigest()[:12]
            d = decl.get(r)
            if d is None:
                succX_bad.append((mname, r, "UNDECLARED"))
                print("      %s [%s] UNDECLARED: %s" % (r, dg, fline[:400]))
            elif d[0] != dg:
                succX_bad.append((mname, r, "CONTENT CHANGED"))
                print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fline[:400]))
            else:
                print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
                print("         its FAIL line: %s" % fline[:240])
        gone = sorted(set(decl) - set(reds))
        if gone:
            succX_bad.append((mname, "GREEN", gone))
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHTX or (succX_n == len(MODELSX) and not succX_bad),
      "%d earlier models re-run one at a time (predfold1123 and predfix84 light: their SUCCESSOR is this list), each "
      "last line read; every red declared superseded with an unchanged FAIL line: %s"
      % (succX_n, "yes" if not succX_bad else succX_bad))

print("== QUOTES (B10): owner sentences in the record and the documents; R1's from its PINNED commit, never a branch")
R1X = "13fc8aa85"                                            # lane/pred-rev28's commit recording closing-own-label
RECORD_R1 = git_showX("docs/design/plan_row_bodies/COND-FAMILY.md", rev=R1X if not sx("s35") else STARTX)
QQX = [
    'optional-label: yes.',
    'capture-negated: broaden to any effect macro cannot be under negation.',
    'binding-fixed: yes.',
    'label-kinds: yes, one mark meaning.',
    'Label forward: yes.',
    "I think it's better to say it's an error and reconsider later.",
    "it has to be (b) or it's unusable because you couldn't put 0: in a loop.",
    'i agree that _ should be the unspecified label- it also comments on your meaning.',
    'label-parameter-default: yes you could use a label in an optional parameter.',
    'sending the unbound label is ok and!',
    'capture-name: a',
    'capture-twice: (a).',
    'argument label: yes.',
    "All other labels are completed at the condition. 0 is not. $0 is provisional. Later labels or captures can "
    "replace entirely but 0 grows.",
    "zero-open: yes all 4",
    "pure label must be whole the label is lost.",
    "Capture label can be partial but again, the label portion is lost.",
    "I think the ? In conditions is a special case, but I'm trying to figure out how special.",
    "then we aren't using ? For two different meanings",
    "from the perspective of B, the subject is now whatever A matched",
    "the row() label arg would be set to the unquoted portion of the string",
    "A(l:,B) := [l = B] or A(l:) := /(?<:${l}>\\d+)/ then A(x:) & (x: 5).",
]
QQR1 = [                      # R1 (closing-own-label), recorded after this lane's cut: read at R1X
    "you can't go through A to get inside",
    "It's closing that door but there may be other doors.",
    "So I agree with your lean.",
]
TTX = [
    "2026-11-23 OWNER RULING — argument-label: yes (a label the caller writes inside an argument is the caller's own); and: these mechanisms ease his concern about the default hiding",
    '2026-11-23 OWNER RULING — optional-label: yes (`(h?: S)` holds when h is absent or in S); and a FLAG: is it a special form or the general case of an expression left of `:`',
    '2026-11-22 OWNER RULING — zero-condition-binding: an error, to be reconsidered later (`c := (0: 5)` bound alone)',
    '2026-11-23 OWNER RULING — capture-negated: broadened: "any effect macro cannot be under negation"',
    "2026-11-23 OWNER RULING — binding-fixed: yes (what a binding's conditions read never depends on where it is used)",
    '2026-11-23 OWNER RULING — label-kinds: yes, one mark, one meaning; the reference kind is for natives, off limits for users for now',
    '2026-11-23 OWNER RULING — label-parameter-omitted: `_` is the unspecified label; and: no argument is omitted under the current call rules; label arguments are not special by position or requirement',
    '2026-11-23 OWNER RULING — capture-twice: (a) (the same-label-twice rules); and an OBSERVATION: two kinds of label reference, one that sets a new group, one that refers to a group that exists',
    '2026-11-22 OWNER RULING — capture-export, in two parts: 1 no (a named group in a part of a composed program is not a capture by default); 2 yes (the program-level `capture(path)` asks for one); explicit and implicit captures',
    '2026-11-23 OWNER RULING — label-hole-full: a pure label\'s name hole must be whole; a capture\'s name may be partial, "but again, the label portion is lost"; and a sketch of the repeat head with a conditional default',
]
TTR1 = ['2026-11-23 OWNER RULING — closing-own-label: "I agree with your lean" (a caller\'s own label is not closed); the export statement closes ONE door: "there may be other doors"']
ALLNOWX = "\n".join(NOWS.values())
if sx("s26"):                                                # the plant: one owner sentence altered in the documents
    ALLNOWX = ws(ALLNOWX).replace(ws("you can't go through A to get inside"), ws("you can't go through A inside"))
q_missX = [q for q in QQX if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOWX)]
q_missR1 = [q for q in QQR1 if ws(q) not in ws(RECORD_R1) or ws(q) not in ws(ALLNOWX)]


def heads(rec):
    return set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in rec.split("\n") if l_.startswith(("### ", "**")))


t_missX = [t_ for t_ in TTX if ws(t_) not in heads(RECORD) or ws(t_) not in ws(ALLNOWX)]
t_missR1 = [t_ for t_ in TTR1 if ws(t_) not in heads(RECORD_R1) or ws(t_) not in ws(ALLNOWX)]
check("QUOTES", not q_missX and not q_missR1 and not t_missX and not t_missR1,
      "%d quoted sentences in the record and the documents, missing: %s; %d of R1's in the record at %s and the "
      "documents, missing: %s; %d record titles cited whole, not a title or not cited: %s; R1's title at %s: %s"
      % (len(QQX), q_missX or "none", len(QQR1), R1X, q_missR1 or "none", len(TTX), t_missX or "none", R1X,
         t_missR1 or "found"))

print("== DOC (B11): every line this model formats occurs verbatim in the piece its tag names")


def piece_of(tag):
    for f_, txt in NOWS.items():
        if f_.endswith("_details.md"):
            continue
        mm = re.search(r"^### .*\[%s\].*$" % re.escape(tag), txt, re.M)
        if mm:
            nx = re.search(r"^### ", txt[mm.end():], re.M)
            return txt[mm.start():mm.end() + (nx.start() if nx else len(txt))]
    return ""


DLNX = list(LINES)
if sx("s27") and DLNX:
    DLNX[0] = (DLNX[0][0], DLNX[0][1].replace("WHOLE `", "WHOLE `x", 1))
if sx("s28") and DLNX:
    DLNX[0] = ("core/spellings/placeholders", DLNX[0][1])
d_missX = [(t_, L) for t_, L in DLNX if ws(L) not in ws(piece_of(t_))]
for t_, L in d_missX:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLNX and not d_missX, "%d lines, each in its own piece; missing: %d" % (len(DLNX), len(d_missX)))

failedX = [n for n, ok in RESULTS if not ok]
print("predfix86_model: %d checks, %d failed%s" % (len(RESULTS), len(failedX),
                                                  (" (%s)" % ", ".join(failedX)) if failedX else ""))
sys.exit(1 if failedX else 0)
