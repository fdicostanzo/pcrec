#!/usr/bin/env python3
# Lane predfold1123b (2026-11-23): the successor evidence model for the fold of the owner's rulings of 2026-11-23 made
# after zero-open (count-unspecified, unspecified-rule, call-forms, repeat-head, binding-as-label, label-doors; the
# withdrawal of label-parameter-omitted's reading (a)). DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predfix86's model is LOADED unchanged: predfix86_model.py is executed up to its line "the checks" (with
# it predfold1123's, predfix84's and the older engines below them). Their LOAD-TIME readers of library.md (the
# several bodies of `repeat`, `rx.digits := rx.repeat(rx.digit, min = 1)`) are pinned to their own format, so during
# the load ONLY, library.md is served from the PINNED starting commit STARTB (a global `open` wrapper, removed after
# the load); every document this model checks (NOWS) is then re-read from the working tree, and the new heads are
# read from the current library.md by this model's own reader (REPEAT_LINE, PADW_LINE). Then the FOLD extensions act,
# each switched by XB[0] (on for the documents now; off for the starting commit's documents under predfix86's engine:
# SWEEP's control). Every regex the model matches with is built mechanically from the program text.
#   CALLFORMS  (call-forms, repeat-head) one head per name: a second definition of a name is a compile error; a call's
#              record binds positional entries first in declared order, then named ones; a positional entry after a
#              named one, a parameter filled twice, a name the head lacks, a required parameter left unset: compile
#              errors; an unset parameter takes its default, which is the macro's own text and may name an EARLIER
#              parameter (a later one: a compile error). `rx.repeat` is the one head read from library.md.
#   UNSPEC     (unspecified-rule, count-unspecified) `_` passed to a plain parameter is "this part is not written": at
#              each position the body lays it into, the construct without the part: a count's lower bound 0, its
#              upper bound no maximum (`{${p},` -> `{0,`, `,${p}}` -> `,}`), an option group with no letters
#              (`(?${p})` -> nothing). Any other position (a pattern, a set, a comparison bound, arithmetic, an exact
#              count `{${p}}`): a compile error. The call is written out as a derived macro without the parameter.
#   NOLABEL    (the withdrawal of label-parameter-omitted's reading (a)) `_:` on a label parameter's spot `[l = v]` is the
#              part with NO label, `(v)`, not the blank mark `[_ = v]`.
#   SHORTHAND  (binding-as-label) a caller's read `N.x` where N is a binding the caller passes WHOLE as an argument: the
#              binding's name stands for a label skipped on the spot where the body places it, under the four
#              conditions: N used once in the caller's text (1); the spot admits a label (2; an argument always
#              does); the read goes through that label (3: written out `[N = N]` on the spots the body uses alone);
#              no label made on it there (4: a spot the body labels `[p = rx]`, lists `[(=) = rx]` or closes
#              `[_ = rx]`, `[_p = rx]` is not shorthand; with no spot left the read is a compile error naming the
#              body's path). A body using the argument both alone and labelled: the label set on the alone spots only
#              (a derived macro with the argument passed twice).
#   STACK      (label-doors line 5) labels stacked on one spot, nothing between (`[a = [b = X]]`), are equal names of
#              it: `[a = X]` and `[b = X]` are lowered alike and their group names joined, group by group; a blank
#              `_` in the stack adds no name and closes only itself.
# KNOWN LIMITS: predfix86's (its file's header). A stacked spot's text is lowered twice (a condition inside it would
# be recorded twice; no printed line has one). SHORTHAND classifies a body's placements textually (`[x = p]` is a
# label made by x; any other placement, an inner call's argument included, is a use alone). CALLFORMS rewrites calls
# of the program's own plain macros and of `rx.repeat` and the width-padding name; other provided names keep the
# loaded engine's binding. The option position is run on a user body whose literal is ONE option group (the loaded
# engine's flag reader is not used).
#
# Run (W = the worktree; any cwd):  timeout 5400 python3 -I -B W/docs/dev/lanes/predfold1123b_evidence/predfold1123b_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDFOLD1123B_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# PREDFOLD1123B_SABOTAGE=all runs every plant in turn (a subprocess each) and prints the table predfold1123b_sabotage.out holds.
# PREDFOLD1123B_LIGHT=1 skips SUCCESSOR (the plant runner sets it for plants not aimed there).
import builtins
import ctypes
import hashlib
import io
import os
import re
import subprocess
import sys

HEREB = os.path.dirname(os.path.abspath(__file__))
P86 = os.path.join(HEREB, "..", "predfix86_evidence", "predfix86_model.py")
WB = os.path.normpath(os.path.join(HEREB, "..", "..", "..", ".."))
SABB = set(x for x in os.environ.get("PREDFOLD1123B_SABOTAGE", "").split(",") if x)
LIGHTB = os.environ.get("PREDFOLD1123B_LIGHT") == "1"
STARTB = "89d26b6b3"                                         # this lane's starting commit (lane/pred-rev28), PINNED
for v in list(os.environ):
    if v.endswith("_SABOTAGE") or v.endswith("_ENGINE") or v.endswith("_LIGHT"):
        os.environ.pop(v, None)


def sb(n):
    return n in SABB


PLANTSB = [   # (plant, its target check, what it plants: every plant changes the ENGINE or the evidence it reads)
    ("s1", "CONTROL", "the control's python `re` for `repeat(D, 3, _)` written `(?:\\d){3}`"),
    ("s2", "CALLFORMS", "a positional entry after a named one accepted"),
    ("s3", "CALLFORMS", "a default naming a LATER parameter accepted (read as its text)"),
    ("s4", "CALLFORMS", "a second head for one name accepted (the last one wins)"),
    ("s5", "UNSPEC", "`_` for a count's upper bound read as the empty text (`{3,}` written `{3,` + `}` kept: `{3,}`) "
                     "and the lower bound as the empty text (`{,5}`)"),
    ("s6", "UNSPEC", "`_` in a pattern position read as the empty pattern (the withdrawn play-out line)"),
    ("s7", "REPEAT", "`_` taken as \"use the default\" (call-forms line 4 undone)"),
    ("s8", "REPEAT", "head (ii): `min = 0, max = _`"),
    ("s9", "SHORTHAND", "the shorthand off: a read through the argument's name refused wherever the body uses it alone"),
    ("s10", "SHORTHAND", "condition 4 off: the shorthand also through a spot the body labels"),
    ("s11", "SHORTHAND", "condition 1 off: a binding used twice in the caller's text takes the shorthand"),
    ("s12", "NOLABEL", "`_:` on a spot written out as the blank mark `[_ = v]` again (reading (a))"),
    ("s13", "STACK", "stacked labels read in nesting order: the outer one passes only what the inner one exports"),
    ("s14", "STACK", "a blank `_` in a stack closes the whole spot"),
    ("s15", "EXPAND", "the drill's written-out shorthand is `[a = A]` read as `a.d` (a different name, the same "
                      "answers) replaced by the body labelling the spot"),
    ("s16", "COUNT", "libpcre2 run on `a{0,}` where the record's run reads `a{,}`"),
    ("s17", "READINGS", "a reading's run moved: the shorthand set on EVERY spot of a body using the argument alone and "
                        "labelled"),
    ("s18", "SWEEP", "one declared moved answer removed"),
    ("s19", "SUCCESSOR", "one declared red removed"),
    ("s20", "QUOTES", "an owner sentence in the documents altered (a word dropped)"),
    ("s21", "DOC", "a formatted line altered"),
    ("s22", "DOC", "a line looked for under another piece's tag"),
    ("s23", "TABLE", "one cell of the ownership table changed to the opposite legality"),
    ("s24", "OWNERBODY", "the owner's two-label body: `_:` written out as the blank mark (his body refused)"),
    ("s25", "TABLE", "the blank mark closes the groups its own definition's text writes (line 4's \"its owner always "
                     "reads it\" undone)"),
]
HEAVYB = {"SUCCESSOR"}
if "all" in SABB:                                            # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTSB:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFOLD1123B_SABOTAGE"] = pn
        if target not in HEAVYB:
            env["PREDFOLD1123B_LIGHT"] = "1"
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
    print("predfold1123b_sabotage: %d plants, %d not caught%s" % (
        len(rows), notc, " (each plant turned its target check FAIL, no traceback)" if not notc else ""))
    sys.exit(1 if notc else 0)


# ================================================================== the LOADER: predfix86's engines, unchanged
def _git(rel, rev):
    return subprocess.run(["git", "-C", WB, "show", "%s:%s" % (rev, rel)], capture_output=True, text=True,
                          check=True).stdout


LIBPATH = os.path.join(WB, "docs", "design", "predicates", "library.md")
_LIB_AT_START = _git("docs/design/predicates/library.md", STARTB)


def open(p, *a, **k):                                        # noqa: A001  the load-time wrapper (removed below)
    if isinstance(p, str) and os.path.abspath(p) == LIBPATH and "w" not in (a[0] if a else k.get("mode", "r")):
        return io.StringIO(_LIB_AT_START)
    return builtins.open(p, *a, **k)


_src86 = builtins.open(P86, encoding="utf-8").read()
_cut86 = re.search(r"^# =+ the checks$", _src86, re.M).start()
_fileB = __file__
__file__ = os.path.abspath(P86)                              # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src86[:_cut86], P86, "exec"), globals())       # noqa: S102  (predfix86's definitions, unchanged)
__file__ = _fileB
del globals()["open"]
for _f in DOCF:                                              # the documents this model checks: the working tree's
    NOWS[_f] = builtins.open(os.path.join(WB, "docs", "design", "predicates", _f), encoding="utf-8").read()
LIBCUR = NOWS["library.md"]
SABX.clear()
LINES.clear()
RUN.clear()
P86F = dict(prog=prog, lower_atom=lower_atom, _sub_labels=_sub_labels, base_binds=base_binds, define=define)
XB = [True]


def xb():
    return XB[0]


# ================================================================== the FOLD extensions (lane predfold1123b)
# ---- the provided heads, read from the CURRENT library.md
_rl = re.search(r"`(repeat\((x, min = _, max = min)\) := (/[^`]*/))`", ws(LIBCUR))
REPEAT_LINE = _rl.group(1) if _rl else None
_pw = re.search(r"`(padded_to\((rx, n)\) := ([^`]*))`", ws(LIBCUR))
PADW_LINE = _pw.group(1) if _pw else None
_dg = re.search(r"`rx\.digits := (rx\.repeat\(rx\.digit, [^`]*\))`", ws(LIBCUR))
RXDIGITS_NOW = _dg.group(1) if _dg else None
if sb("s8"):
    REPEAT_LINE = "repeat(x, min = 0, max = _) := /(?:${[(=) = x]}){${min},${max}}/"


def head_of(line):
    """(name, [(param, default or None, kind)], body) of a macro line, or None."""
    mm = re.fullmatch(r"([\w.]+)\((.*?)\) := (.*)", line.strip(), re.S)
    if not mm:
        return None
    ps = []
    for h in (split_top(mm.group(2), ",") if mm.group(2).strip() else []):
        h = h.strip()
        lm = re.fullmatch(r"(\w+)(?: = (\w*))?:", h)
        if lm:
            ps.append((lm.group(1), lm.group(2), "label"))
            continue
        pm = re.fullmatch(r"(\w+)(?: = (.*))?", h, re.S)
        ps.append((pm.group(1), pm.group(2), "plain"))
    return mm.group(1), ps, mm.group(3).strip()


PROV = {}                     # the provided heads CALLFORMS binds: name -> (params, body)
if REPEAT_LINE:
    _h = head_of(REPEAT_LINE)
    PROV["rx.repeat"] = (_h[1], _h[2])
if PADW_LINE:
    _h = head_of(PADW_LINE)
    PROV["padded_to"] = (_h[1], _h[2])
DERIVED = []                  # the derived macro lines of the program being built
DCOUNT = [0]


# ---- UNSPEC: `_` at each position the body lays a plain parameter into
def unspec_body(name, p, body):
    hole = "${%s}" % p
    if sb("s5"):
        b2 = body.replace("{%s," % hole, "{,").replace(",%s}" % hole, ",}")
    else:
        b2 = body.replace("{%s," % hole, "{0,").replace(",%s}" % hole, ",}")
    b2 = b2.replace("(?%s)" % hole, "").replace("(?%s:" % hole, "(?:")
    rest = re.search(r"\$\{%s\}" % re.escape(p), b2) or \
        re.search(r"(?<![\w.$])%s(?![\w])" % re.escape(p), strip_lits(b2))
    if rest:
        if sb("s6") and "${%s}" % p in b2:
            return b2.replace("${%s}" % p, "")
        raise CompileError("`_` passed for `%s` of %s: the construct at that position has no form without the part "
                           "(a compile error, unspecified-rule)" % (p, name))
    return b2


# ---- CALLFORMS: one head per name; the record bound
def bind_record(name, ps, args):
    names = [p for p, _, _ in ps]
    vals, named, npos = {}, False, 0
    for a in args:
        mm = re.fullmatch(r"(\w+) = (?!=)(.*)", a, re.S)
        if mm and mm.group(1) in names:
            named = True
            if mm.group(1) in vals:
                raise CompileError("a call of %s fills `%s` twice (a compile error, call-forms)" % (name, mm.group(1)))
            vals[mm.group(1)] = mm.group(2).strip()
            continue
        if mm:
            raise CompileError("a call of %s names `%s`, which its head does not have (a compile error, call-forms)"
                               % (name, mm.group(1)))
        if named and not sb("s2"):
            raise CompileError("a call of %s: a positional entry after a named one (a compile error for now, "
                               "call-forms line 2)" % name)
        free = [p for p in names[npos:] if p not in vals]
        if not free:
            raise CompileError("a call of %s passes more entries than its head has (a compile error)" % name)
        vals[free[0]] = a
        npos = names.index(free[0]) + 1
    for i, (p, d, kind) in enumerate(ps):
        if p in vals:
            continue
        if d is None:
            raise CompileError("a call of %s binds no `%s` (a call binds every required parameter, call-forms)" % (name, p))
        if kind == "label":
            vals[p] = d + ":"
            continue
        if re.fullmatch(r"\w+", d) and d in names:
            j = names.index(d)
            if j >= i and not sb("s3"):
                raise CompileError("the default of `%s` in %s names `%s`, a later parameter (a compile error, "
                                   "call-forms line 3)" % (p, name, d))
            vals[p] = vals[d] if j < i else d
        else:
            vals[p] = d
    if sb("s7"):                                             # the plant: `_` read as "use the default"
        for i, (p, d, kind) in enumerate(ps):
            if vals.get(p) == "_" and d is not None and d != "_":
                vals[p] = vals[d] if d in names else d
    return vals


def callforms(t, heads):
    """Every call in t of a head in `heads` (the program's own plain macros, the provided heads) written out: the
    record bound, `_` parameters removed by a derived macro (UNSPEC)."""
    out, i = [], 0
    while True:
        mm = re.compile(r"(?<![\w.])([A-Za-z_][\w.]*)\(").search(t, i)
        if not mm:
            out.append(t[i:])
            break
        name = mm.group(1)
        j = close_paren(t, mm.end() - 1)
        if name not in heads or (mm.start() > 0 and t[mm.start() - 1] == "$"):
            out.append(t[i:mm.end()])
            i = mm.end()
            continue
        ps, body = heads[name]
        raw = t[mm.end():j]
        args = [callforms(a.strip(), heads) for a in split_top(raw, ",")] if raw.strip() else []
        vals = bind_record(name, ps, args)
        unspec = [p for p, _, kind in ps if kind == "plain" and vals.get(p) == "_"]
        if unspec:
            b2 = body
            for p in unspec:
                b2 = unspec_body(name, p, b2)
            DCOUNT[0] += 1
            dn = "%s_u%d" % (name.replace(".", "_"), DCOUNT[0])
            keep = [(p, kind) for p, _, kind in ps if p not in unspec]
            if keep:
                DERIVED.append("%s(%s) := %s" % (dn, ", ".join(p + (":" if k == "label" else "") for p, k in keep), b2))
                call = "%s(%s)" % (dn, ", ".join(vals[p] for p, _ in keep))
            else:                                            # no parameter left: a binding
                DERIVED.append("%s := %s" % (dn, b2))
                call = dn
        else:
            call = "%s(%s)" % (name, ", ".join(vals[p] for p, _, _ in ps))
        out.append(t[i:mm.start()] + call)
        i = j + 1
    return "".join(out)


# ---- SHORTHAND (binding-as-label)
def placements(body, p, lmap):
    """Each placement of parameter p in body: None (used alone) or the label made on it."""
    out = []
    for mm in re.finditer(r"(?<![\w.$])%s(?![\w])" % re.escape(p), body):
        left = body[:mm.start()]
        lb = re.search(r"\[(\w+|\([^()]*\)) = $", left) or re.search(r"\(\?<:?(\w+)>\$\{$", left)
        if lb:
            lab = lb.group(1)
            out.append(None if lmap.get(lab) == "_" else lab)
        else:
            out.append(None)
    return out


def shorthand(expr, heads, bnames):
    if sb("s9"):
        return expr
    sl = strip_lits(expr)
    reads = set(re.findall(r"(?<![\w.$])\$?([A-Za-z_]\w*)\.[A-Za-z_]", sl))
    for N in sorted(reads & bnames):
        calls = []
        for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", expr):
            if mm.group(1) not in heads:
                continue
            j = close_paren(expr, mm.end() - 1)
            args = [a.strip() for a in split_top(expr[mm.end():j], ",")]
            for k, a in enumerate(args):
                av = a.split(" = ", 1)[1].strip() if re.fullmatch(r"\w+ = .*", a, re.S) else a
                if av == N:
                    calls.append((mm, j, k, args))
        if not calls:
            continue
        uses = len(re.findall(r"(?<![\w.$])%s(?![\w.])" % re.escape(N), sl))
        if uses != 1 and not sb("s11"):
            raise CompileError("`%s.`: the binding `%s` is used %d times in this definition, so its name is no "
                               "shorthand for a label (a compile error, binding-as-label condition 1)" % (N, N, uses))
        mm, j, k, args = calls[0]
        name = mm.group(1)
        ps, body = heads[name]
        names = [p for p, _, _ in ps]
        a = args[k]
        p = a.split(" = ", 1)[0] if re.fullmatch(r"\w+ = .*", a, re.S) else names[k]
        lmap = {}
        for (q, _, kind), av in zip(ps, args):
            if kind == "label":
                lmap[q] = av.rstrip(":")
        pl_ = placements(body, p, lmap)
        if sb("s10"):
            pl_ = [None for _ in pl_]
        alone = [x for x in pl_ if x is None]
        if pl_ and not alone:
            lab = next(x for x in pl_ if x is not None)
            path = ("%s.<label>" % name) if lab.startswith("(") else ("%s.%s" % (name, lab))
            why = ("the body closes the spot" if lab == "_" or (lab.startswith("_") and len(pl_) == 1 and
                                                                 not re.search(r"\[\w+ = \[%s = " % lab, body)) else
                   "the body lists the spot; the read is `%s.<label>`" % name if lab.startswith("(") else
                   "the body labels the spot `%s`" % lab)
            raise CompileError("`%s.`: a label is already made on the spot where %s places `%s` (%s; a compile "
                               "error, binding-as-label condition 4)" % (N, name, N, why))
        if len(alone) == len(pl_):                           # (never placed: the label is set never, as written)
            new_args = list(args)
            new_args[k] = ("%s = [%s = %s]" % (p, N, N)) if a != N else "[%s = %s]" % (N, N)
            expr = expr[:mm.start()] + "%s(%s)" % (name, ", ".join(new_args)) + expr[j + 1:]
        else:                                                # alone and labelled: the label on the alone spots only
            DCOUNT[0] += 1
            ps2 = p + "_s"
            out, last, n_ = [], 0, 0
            for m2 in re.finditer(r"(?<![\w.$])%s(?![\w])" % re.escape(p), body):
                out.append(body[last:m2.start()])
                out.append(ps2 if (pl_[n_] is None and not sb("s17")) else p)
                last, n_ = m2.end(), n_ + 1
            out.append(body[last:])
            dn = "%s_s%d" % (name.replace(".", "_"), DCOUNT[0])
            heads_txt = ", ".join(q + (":" if kind == "label" else "") for q, _, kind in ps) + ", " + ps2
            DERIVED.append("%s(%s) := %s" % (dn, heads_txt, "".join(out)))
            expr = expr[:mm.start()] + "%s(%s, [%s = %s])" % (dn, ", ".join(args), N, N) + expr[j + 1:]
    return expr


# ---- NOLABEL: `_:` on a spot is the part with no label
def _sub_labels(t, lmap, pmap):                              # noqa: F811
    """predfix86's, with `[l = v]` for l passed `_` written out as the part with NO label, `(v)` (predfix86's own
    switch for that form, its plant s2, turned on for the call), not the blank mark `[_ = v]`."""
    if not xb() or sb("s12"):
        return P86F["_sub_labels"](t, lmap, pmap)
    had = "s2" in SABX
    SABX.add("s2")
    try:
        return P86F["_sub_labels"](t, lmap, pmap)
    finally:
        if not had:
            SABX.discard("s2")


# ---- STACK (label-doors line 5)
STK = re.compile(r"\[(\w+) = \[(\w+) = (.*)\]\]([+*?]?)", re.S)


def _join_groups(t1, t2):
    got = []
    map_groups(t2, lambda ps: got.append(ps) or ps)
    it = iter(got)

    def add(ps):
        try:
            more = next(it)
        except StopIteration:
            raise CompileError("a stacked spot lowered unalike (model)")
        return ps + [x for x in more if x not in ps]
    return map_groups(t1, add)


OWNB_RX = re.compile(r"\[_ = (/.*/)\]([+*?]?)", re.S)


def lower_atom(expr, ctx):                                   # noqa: F811
    if xb():
        e = expr.strip()
        mo = OWNB_RX.fullmatch(e)
        if mo and _close_br(e, 0) == len(e) - 1 - len(mo.group(2)) and not sb("s25"):
            return lower_atom("(%s)%s" % mo.groups(), ctx)      # OWNREAD: the text that writes the name reads it
        mm = STK.fullmatch(e)
        if mm and _close_br(e, 0) == len(e) - 1 - len(mm.group(4)) and _close_br(e, e.index("[", 1)) == \
                len(e) - 2 - len(mm.group(4)):
            a, b, x, q = mm.groups()
            if a == "_" and not sb("s14"):
                return lower_atom("[%s = %s]%s" % (b, x, q), ctx)
            if b == "_" and not sb("s14"):
                return lower_atom("[%s = %s]%s" % (a, x, q), ctx)
            if sb("s13"):
                return P86F["lower_atom"]("[%s = ([%s = %s])]%s" % (a, b, x, q), ctx)
            t1 = lower_atom("[%s = %s]%s" % (a, x, q), ctx)
            t2 = lower_atom("[%s = %s]%s" % (b, x, q), ctx)
            return _join_groups(t1, t2)
    return P86F["lower_atom"](expr, ctx)


# ---- the provided heads in the base bindings
def base_binds():                                            # noqa: F811
    P86F["base_binds"]()
    if xb():
        if "rx.repeat" in PROV:
            MACROS["rx.repeat"] = [([(p, None) for p, _, _ in PROV["rx.repeat"][0]], PROV["rx.repeat"][1])]
        if "padded_to" in PROV:
            MACROS["padded_to"] = [([(p, None) for p, _, _ in PROV["padded_to"][0]], PROV["padded_to"][1])]
        if RXDIGITS_NOW:
            BINDS["rx.digits"] = RXDIGITS_FORM[0]
            for d_ in RXDIGITS_FORM[1]:
                P86F["define"](d_)


RXDIGITS_FORM = [None, []]


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not xb():
        return P86F["prog"](expr, binds, **opts)
    binds = list(binds)
    seen = {}
    for b in binds:
        h = head_of(b)
        nm = h[0] if h else b.partition(" := ")[0].strip()
        if nm in seen and not sb("s4"):
            raise CompileError("`%s` is defined twice: one head per name (a compile error, call-forms line 1)" % nm)
        seen[nm] = b
    if sb("s4"):
        binds = list({(head_of(b) or (b.partition(" := ")[0].strip(),))[0]: b for b in binds}.values())
    del DERIVED[:]
    DCOUNT[0] = 0
    heads = dict(PROV)
    plain, lps = {}, {}
    for b in binds:
        h = head_of(b)
        if h:
            (lps if any(k == "label" for _, _, k in h[1]) else plain)[h[0]] = (h[1], h[2])
    heads.update(plain)
    for nm, (ps, _) in plain.items():                        # call-forms line 3, at the head
        names = [p for p, _, _ in ps]
        for i, (p, d, kind) in enumerate(ps):
            if d is not None and re.fullmatch(r"\w+", d) and d in names and names.index(d) >= i and not sb("s3"):
                raise CompileError("the default of `%s` in %s names `%s`, not an earlier parameter (a compile "
                                   "error, call-forms line 3)" % (p, nm, d))
    expr2 = callforms(expr, heads)
    binds2 = []
    for b in binds:
        h = head_of(b)
        if h:
            binds2.append(b.split(" := ", 1)[0] + " := " + callforms(h[2], heads))
        else:
            nm, _, body = b.partition(" := ")
            binds2.append(nm + " := " + callforms(body, heads))
    if RXDIGITS_NOW:
        n0 = len(DERIVED)
        RXDIGITS_FORM[0] = callforms(RXDIGITS_NOW, heads)
        RXDIGITS_FORM[1] = DERIVED[n0:]
    if "peek" not in MACROS:
        base_binds()
    allh = dict(heads)
    for nm, bodies in MACROS.items():                        # the provided bodies, one head each
        if nm not in allh and len(bodies) == 1:
            allh[nm] = ([(q, d, "plain") for q, d in bodies[0][0]], bodies[0][1])
    allh.update(lps)
    for d_ in DERIVED:
        h = head_of(d_)
        if h:
            allh[h[0]] = (h[1], h[2])
    bnames = set(b.partition(" := ")[0].strip() for b in binds if not head_of(b))
    expr2 = shorthand(expr2, allh, bnames)
    binds3 = []
    for b in binds2:                                         # the shorthand inside each binding's own text
        nm, _, body = b.partition(" := ")
        binds3.append(b if "(" in nm else nm + " := " + shorthand(body, allh, bnames))
    binds2 = binds3
    return P86F["prog"](expr2, binds2 + [d_ for d_ in DERIVED if d_ not in RXDIGITS_FORM[1]], **opts)


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


def bt(binds):                                               # noqa: F811
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def pl(label, expr, binds, wh, sr, fa, tag, tail="", bdesc=None, P=None, shown=None, ann=None):
    """A printed three-mode line, formatted from the run (or from P, a program run elsewhere)."""
    Pg, err = (P, None) if P is not None else run(expr, binds)
    if Pg is None:
        doc_line("%s: REFUSED (%s)" % (label, err), tag)
        print("   REFUSED [%s] %s: %s" % (tag, label, err))
        return None
    w = fmt(Pg, wh, sr, fa)
    for t in (ann and wh or []):
        if Pg.whole(t):
            st = whole_state(Pg, t)
            vs = ", ".join(("%s = `%s`" % (n, label_of(st, n))) if label_of(st, n) is not None else "%s unset" % n
                           for n in ann)
            w = w.replace("`%s` HOLDS" % t, "`%s` HOLDS (%s)" % (t, vs), 1)
    L_ = "%s%s (`%s`%s)%s" % ((label + ": ") if label else "", w, shown or expr, bt(binds) if bdesc is None else bdesc,
                              tail)
    doc_line(L_, tag)
    print("   LINE [%s] %s" % (tag, L_))
    return Pg


def rl(label, expr, binds, key, reason, tag, shown=None):
    """A printed refusal line; the refusal's message must name `key`."""
    Pg, err = run(expr, binds)
    L_ = "%s: modes: a compile error (`%s`%s: %s)." % (label, shown or expr, bt(binds), reason)
    doc_line(L_, tag)
    print("   LINE [%s] %s\n      (refusal: %s)" % (tag, L_, err))
    return err is not None and key in err, err


def refused(expr, binds, key):
    Pg, err = run(expr, binds)
    print("   RUN `%s`%s: %s" % (expr, bt(binds), ("refused: " + err) if err else "legal"))
    return err is not None and key in err


def wh_(Pg, texts):
    return [Pg.whole(t) for t in texts] if Pg is not None else None


A_D = "A := /(?<d>\\d)/"
A_H = "A := /(?<h>\\d)/"
ADIG = "A := [d = rx.digits]"
B_XX = "B(rx) := /${rx}xx/"
B_AL = "B(rx) := /${rx}-(?<d>\\d)/"
B_P = "B(rx) := /${[p = rx]}-(?<d>\\d)/"
B_LS = "B(rx) := /${[(=) = rx]}xx/"
B_CL = "B(rx) := /${[_ = rx]}xx/"
B_CP = "B(rx) := /${[_p = rx]}xx/"
B_PH = "B(rx) := /${[p = rx]}xx/"
B_ST = "B(rx) := /${[n = [_x = rx]]}xx/"
B_BOTH = "B(rx) := /${[p = rx]}-${rx}/"
PAIR = "pair(p) := /${p},${p}/"
W_ = "W(l:, v) := /<${[l = v]}>/"
S_ = "S(l:) := /\"(?<:${l}>\\d)\"/"
P_ = "P := /(?<d>\\d)\\d/"
OWNB = "A(l:, P) := [l = [_x = P]] & (_x: 5)"
W_AB = "W(a, b) := [(=) = a] SEQ [(=) = b]"
REP_T = "lib/rx/repeat"
CF_T = "core/operators/bindings/call-forms"
UN_T = "core/operators/bindings/unspecified"
CNT_T = "core/holes/count"
RULE_T = "core/labels/rule"
OWN_T = "core/labels/ownership"
AD_T = "core/labels/paths/argument-default"
CA_T = "core/labels/paths/closed-argument"
CP_T = "core/labels/paths/call-prefix"
ARGT = "core/labels/export/arguments"
LO_T = "core/operators/bindings/label-omitted"
NS_T = "core/holes/bare-condition/nested-scope"
QR = ["", "12", "123", "123456"]

print("== CONTROL: the extended matcher against python `re`")
QC = pop("12x", 6)
ctl = []
for e, rx in (("rx.repeat(rx.digit)", r"(?:\d){0,}"), ("rx.repeat(rx.digit, 3)", r"(?:\d){3,3}"),
              ("rx.repeat(rx.digit, 3, _)", r"(?:\d){3}" if sb("s1") else r"(?:\d){3,}"),
              ("rx.repeat(rx.digit, _, 5)", r"(?:\d){0,5}"), ("rx.repeat(rx.digit, 2, 5)", r"(?:\d){2,5}"),
              ("rx.repeat(rx.digit, 0)", r"(?:\d){0,0}"), ("rx.digits", r"\d+")):
    Pg, err = run(e)
    ctl.append((e, ndiff(answers(Pg, QC), answers(Re(rx), QC)) if Pg is not None else err))
P_stc = run("[n = [_x = P]] & (n.d: <5)", [P_])[0]
QS = pop("37", 3)
ctl.append(("stacked", ndiff(answers(P_stc, QS), answers(Re(r"[0-4]\d"), QS)) if P_stc is not None else "refused"))
check("CONTROL", all(v == (0, 0, 0) for _, v in ctl), "differing (WHOLE, SEARCHED, FIND-ALL) against python `re` over "
      "%d texts (the stacked line over %d): %s" % (len(QC), len(QS), ctl))

print("== CALLFORMS (call-forms, ruled): one head per name; positional first, then named; defaults")
P_cf1 = pl("Named after positional", "rx.repeat(rx.digit, max = 5, min = 2)", [], ["1", "12", "123456"], "x1234567",
           "1234567 1 12", CF_T)
ok_cf2, r_cf2 = rl("A positional entry after a named one", "rx.repeat(rx.digit, max = 5, 2)", [], "positional entry after",
                   "a compile error for now", CF_T)
ok_cf3, r_cf3 = rl("A parameter filled twice", "rx.repeat(rx.digit, 3, min = 2)", [], "twice",
                   "`min` by position and by name", CF_T)
ok_cf4 = refused("rx.repeat(rx.digit, low = 2)", [], "does not have")
ok_cf5, r_cf5 = rl("A default naming a later parameter", "R(rx.digit)",
                   ["R(x, min = max, max = _) := /(?:${x}){${min},${max}}/"], "not an earlier parameter",
                   "a default may name an earlier parameter only", CF_T)
ok_cf6, r_cf6 = rl("Two heads for one name", "R(rx.digit)", ["R(x) := /${x}/", "R(x, y) := /${x}${y}/"],
                   "one head per name", "one head per name, no overloading", CF_T)
ok_cf7 = refused("rx.repeat()", [], "binds no `x`")
check("CALLFORMS", P_cf1 is not None and wh_(P_cf1, ["1", "12", "123456"]) == [False, True, False] and ok_cf2 and
      ok_cf3 and ok_cf4 and ok_cf5 and ok_cf6 and ok_cf7,
      "named after positional legal (`{2,5}`) %s; refused: positional after named %s (%s), filled twice %s, a name the "
      "head lacks %s, a default naming a later parameter %s (%s), two heads %s, the required `x` unset %s"
      % (wh_(P_cf1, ["1", "12", "123456"]), ok_cf2, r_cf2, ok_cf3, ok_cf4, ok_cf5, r_cf5, ok_cf6, ok_cf7))

print("== REPEAT (repeat-head, ruled: head (i)): one count exact, 0 included; `_` leaves a bound out")
RP = [("No count", "rx.repeat(rx.digit)", [True, True, True, True]),
      ("One count, exact", "rx.repeat(rx.digit, 3)", [False, False, True, False]),
      ("No maximum", "rx.repeat(rx.digit, 3, _)", [False, False, True, True]),
      ("No minimum", "rx.repeat(rx.digit, _, 5)", [True, True, True, False]),
      ("A range", "rx.repeat(rx.digit, 2, 5)", [False, True, True, False]),
      ("A written 0, exact", "rx.repeat(rx.digit, 0)", [True, False, False, False])]
rp_got = []
for lab, e, want in RP:
    Pg = pl(lab, e, [], QR, "x1234567", "1234567 12", REP_T)
    rp_got.append((e, wh_(Pg, QR) == want))
P_rp1 = run("rx.repeat(rx.digit, min = 3)")[0]
P_rp2 = run("rx.repeat(rx.digit, min = 3, max = _)")[0]
unset_vs_ = P_rp1 is not None and P_rp2 is not None and P_rp1.whole("123") and not P_rp1.whole("1234") and \
    P_rp2.whole("1234")
check("REPEAT", all(ok for _, ok in rp_got) and unset_vs_, "WHOLE over %s against the ruled table: %s; unset `max` "
      "(the default `min`, exact) and `max = _` (no maximum) differ %s" % (QR, rp_got, unset_vs_))
for lab, e, _ in RP[:4]:                                     # the four calls shown with the ruling, in its piece
    pl(lab, e, [], QR, "x1234567", "1234567 12", CF_T)

print("== UNSPEC (unspecified-rule, ruled): `_` is the construct without the part; no form, a compile error")
P_u1 = pl("A label", 'A(_:) SEQ "!"', ["A(l:) := /(?<:${l}>\\d)/"], ["3!", "7!"], "x3!", "3! 7!", UN_T)
P_u2 = pl("An option", "opt(_)", ["opt(o) := /(?${o})ab/"], ["ab", "AB"], "x AB ab", "ab AB Ab", UN_T)
P_u2w = run("/ab/")[0]
P_u3 = pl("A count bound", "rx.repeat(rx.digit, 3, _)", [], QR, "x1234567", "1234567 12", UN_T)
ok_u4, r_u4 = rl("A pattern", "P2(_, /b/)", ["P2(a, b) := /${a}${b}/"], "no form without the part",
                 "a pattern position has no form without the part", UN_T)
ok_u5, r_u5 = rl("An exact count", "E(rx.digit, _)", ["E(x, n) := /(?:${x}){${n}}/"], "no form without the part",
                 "`{}` is no count", UN_T)
P_u8 = pl("Laid into two positions", "T(rx.digit, _)", ["T(x, n) := /(?:${x}){${n},}b{0,${n}}/"],
          ["1b", "bbbb", "1"], "x1bb", "1bb 2 b", UN_T)
ok_u6 = refused("G(_)", ["G(n) := /\\d/ & (0: >= ${n})"], "no form without the part")
ok_u7 = refused("Q(_)", ["Q(s) := /x/ & (0: s)"], "no form without the part")
check("UNSPEC", P_u1 is not None and P_u2 is not None and answers(P_u2, pop("abAB", 2)) == answers(P_u2w, pop("abAB", 2))
      and P_u3 is not None and ok_u4 and ok_u5 and ok_u6 and ok_u7 and wh_(P_u8, ["1b", "bbbb", "1"]) == [True, True, True],
      "legal: a label %s, an option (`opt(_)` = `/ab/` over %d texts) %s, a count bound %s; refused: a pattern %s (%s), "
      "an exact count %s, a comparison bound %s, a set %s" % (P_u1 is not None, len(pop("abAB", 2)),
                                                              P_u2 is not None, P_u3 is not None, ok_u4, r_u4, ok_u5,
                                                              ok_u6, ok_u7))

print("== COUNT (count-unspecified, ruled): by meaning, never the empty text; libpcre2 reads `{,}` as text")
P_c0 = pl("Both bounds unspecified", "rx.repeat(rx.digit, _, _)", [], QR, "x1234567", "1234567 12", CNT_T)
pc_src = "a{0,}" if sb("s16") else "a{,}"
pcb = pc_src.encode()
_e, _o = ctypes.c_int(), ctypes.c_size_t()
_code = PC2.pcre2_compile_8(pcb, len(pcb), 0, ctypes.byref(_e), ctypes.byref(_o), None)


def _pcw(s):
    md = PC2.pcre2_match_data_create_from_pattern_8(_code, None)
    sb_ = s.encode()
    return PC2.pcre2_match_8(_code, sb_, len(sb_), 0, 0x80000000 | 0x20000000, md, None) >= 0


pcw = [(s, _pcw(s)) for s in ("", "aaa", "a{,}")]
print("   libpcre2 (ctypes, the installed library) WHOLE on `%s`: %s" % (pc_src, pcw))
check("COUNT", P_c0 is not None and wh_(P_c0, QR) == [True] * 4 and pcw == [("", False), ("aaa", False), ("a{,}", True)],
      "`rx.repeat(rx.digit, _, _)` is `{0,}` %s; libpcre2 `a{,}` WHOLE ``, `aaa`, `a{,}`: %s (the four characters, "
      "the record's run)" % (wh_(P_c0, QR), pcw))

print("== SHORTHAND (binding-as-label, ruled): the four conditions, the table for `B(A)`")
P_s1 = pl("The body using the argument alone", "B(A) & (A.d: <5)", [A_D, B_AL], ["7-3", "3-7", "3-3"], "7-3 3-7",
          "7-3 3-7 1-2 9-9", CA_T)
pl("A's own d, the body using the argument alone (case 2)", "B(A) & (A.d: <5)", [A_D, B_AL], ["7-3", "3-7", "3-3"],
   "7-3 3-7", "7-3 3-7 1-2 9-9", CP_T)
ok_s2, r_s2 = rl("The body labelling the spot", "B(A) & (A.d: <5)", [A_D, B_P], "condition 4",
                 "a label is made on the spot; the read is `B.p.d`, the line \"Through the body's path\"", CA_T)
rl("A's own d, the body labelling the spot (case 2)", "B(A) & (A.d: <5)", [A_D, B_P], "condition 4",
   "a label is made on the spot; the read is `B.p.d` (core/labels/paths/closed-argument)", CP_T)
P_s3 = pl("Through the body's path", "B(A) & (B.p.d: <5)", [A_D, B_P], ["7-3", "3-7", "3-3"], "7-3 3-7",
          "7-3 3-7 1-2 9-9", CA_T)
ok_s4, r_s4 = rl("The body listing the spot", "B(A) & (A.d: <5)", [A_D, B_LS], "condition 4",
                 "the list is a label made on the spot (the manager's reading (b)); the read is `B.d`", CA_T)
P_s5 = pl("Through the call, the list", "B(A) & (B.d: <5)", [A_D, B_LS], ["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx",
          CA_T)
ok_s6, r_s6 = rl("Closed by the macro", "B(A) & (A.d: <5)", [A_D, B_CL], "closes the spot",
                 "the blank mark is a label made on the spot; `[c = B(A)] & (c.d: <5)` alike", CA_T)
ok_s6b = refused("[c = B(A)] & (c.d: <5)", [A_D, B_CL], "")
ok_s7, r_s7 = rl("Closed by a `_` part label", "B(A) & (A.d: <5)", [A_D, B_CP], "condition 4",
                 "`c.d` and `B.d` alike; inside its binding a `_` part label is an ordinary one", CA_T)
P_s8 = pl("The caller's own label, under a closing body", "B([a = A]) & (a.h: <5)", [A_H, B_CL], ["3xx", "7xx"],
          "7xx 3xx", "3xx 7xx 4xx", CA_T)
ok_s9 = refused("B([a = A]) & (A.h: <5)", [A_H, B_XX], "")
ok_s10, r_s10 = rl("Used twice in the caller's text", "B(A) SEQ A & (A.d: <5)", [A_D, B_XX], "condition 1",
                   "the binding is not referenced unambiguously (condition 1); label the uses", AD_T)
P_s11 = pl("The caller's read through the shorthand", "B(A) & (A.d: <5)", [A_D, B_XX], ["3xx", "7xx"], "7xx 3xx",
           "3xx 7xx 4xx", AD_T)
pl("The body using its argument alone", "B(A) & (A.d: <5)", [A_D, B_XX], ["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx", ARGT)
P_s12 = pl("Both uses", "B(A) & (A.d: <5)", [B_BOTH, A_D], ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T)
P_s13 = pl("Used twice alone, the last mention", "pair(A) & (A.d: <5)", [A_D, PAIR], ["7,3", "3,7"], "3,7 7,3",
           "7,3 3,7 1,2", CP_T)
P_s14c = run("C", ["C := B(A) & (A.d: <100)", ADIG, B_XX])[0]
P_s14 = pl("Example 1", "C := B(A) & (A.d: <100)", [ADIG, B_XX], ["42xx", "100xx", "042xx"], "x100xx 42xx",
           "100xx 42xx 7xx 300xx", NS_T, P=P_s14c)
P_s15 = pl("The unspecified label on a spot", "W(_:, A) & (A.h: <5)", [W_, A_H], ["<3>", "<7>"], "<7> <3>",
           "<3> <7> <4>", LO_T)
sh_ok = (wh_(P_s1, ["7-3", "3-7", "3-3"]) == [False, True, True] and ok_s2 and
         wh_(P_s3, ["7-3", "3-7", "3-3"]) == [False, True, True] and ok_s4 and wh_(P_s5, ["3xx", "7xx"]) == [True, False]
         and ok_s6 and ok_s6b and ok_s7 and wh_(P_s8, ["3xx", "7xx"]) == [True, False] and ok_s9 and ok_s10 and
         wh_(P_s11, ["3xx", "7xx"]) == [True, False] and wh_(P_s12, ["7-3", "3-7"]) == [True, False] and
         wh_(P_s13, ["7,3", "3,7"]) == [True, False] and wh_(P_s14, ["42xx", "100xx"]) == [True, False] and
         wh_(P_s15, ["<3>", "<7>"]) == [True, False])
check("SHORTHAND", sh_ok, "alone: legal, A's d %s; labelled: refused %s (%s), `B.p.d` %s; listed: refused %s, `B.d` "
      "%s; closed: refused %s and `c.d` %s, `_p` %s; the caller's own label under a closing body %s; the caller's "
      "label then `A.h` refused %s; used twice: refused %s; `/${rx}xx/` legal %s; both uses (the alone spot) %s; "
      "pair alone twice (the last mention) %s; his example 1 %s; `W(_:, A)` %s"
      % (wh_(P_s1, ["7-3", "3-7", "3-3"]), ok_s2, r_s2, wh_(P_s3, ["7-3", "3-7", "3-3"]), ok_s4,
         wh_(P_s5, ["3xx", "7xx"]), ok_s6, ok_s6b, ok_s7, wh_(P_s8, ["3xx", "7xx"]), ok_s9, ok_s10,
         wh_(P_s11, ["3xx", "7xx"]), wh_(P_s12, ["7-3", "3-7"]), wh_(P_s13, ["7,3", "3,7"]),
         wh_(P_s14, ["42xx", "100xx"]), wh_(P_s15, ["<3>", "<7>"])))

print("== NOLABEL (reading (a) of label-parameter-omitted withdrawn): `_:` is the part with no label, not `[_ = v]`")
P_nl1 = run("W(_:, A) & (A.h: <5)", [W_, A_H])[0]
ok_nl2 = refused("W4(A) & (A.h: <5)", ["W4(v) := /<${[_ = v]}>/", A_H], "closes")
P_nl3 = run("W3(A) & (A.h: <5)", ["W3(v) := /<${v}>/", A_H])[0]
check("NOLABEL", P_nl1 is not None and ok_nl2 and P_nl3 is not None and
      answers(P_nl1, pop("<37>", 3)) == answers(P_nl3, pop("<37>", 3)),
      "`W(_:, A) & (A.h: ..)` legal %s and as the body with no label on the spot %s; the blank mark written out "
      "refused %s" % (P_nl1 is not None, P_nl3 is not None, ok_nl2))

print("== STACK (label-doors line 5): labels stacked on one spot are equal names; the order does not matter")
P_k1 = pl("Outer the caller's, inner private", "[n = [_x = P]] & (n.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", RULE_T)
P_k2 = pl("Outer private, inner the caller's", "[_x = [n = P]] & (n.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", RULE_T)
P_k3 = pl("A blank label in the stack", "[l = [_ = P]] & (l.d: <5)", [P_], ["37", "73"], "73 37", "37 73 14", OWN_T)
P_k4 = run("[n = [_x = P]] & (_x.d: <5)", [P_])[0]
ok_k5, r_k5 = rl("Something between the two labels", "[n = [_x = P] SEQ \"!\"] & (n.d: <5)", [P_], "",
                 "two spots: `_x`'s door is shut to `n` (the manager's reading (a))", RULE_T)
QK = pop("37", 3)
st_ok = P_k1 is not None and P_k2 is not None and answers(P_k1, QK) == answers(P_k2, QK) and \
    wh_(P_k1, ["37", "73", "3"]) == [True, False, False] and wh_(P_k3, ["37", "73"]) == [True, False] and \
    P_k4 is not None and answers(P_k4, QK) == answers(P_k1, QK) and ok_k5
check("STACK", st_ok, "`[n = [_x = P]]` and `[_x = [n = P]]` alike over %d texts %s; `n.d` and `_x.d` alike %s; "
      "`[l = [_ = P]]` opens through `l` %s" % (len(QK), P_k1 is not None and P_k2 is not None and
                                              answers(P_k1, QK) == answers(P_k2, QK),
                                              P_k4 is not None and answers(P_k4, QK) == answers(P_k1, QK),
                                              wh_(P_k3, ["37", "73"])))

print("== OWNERBODY: his two-label body, `A(l:, P) := [l = [_x = P]] & (_x: 5)`, with a name and with `_`")
P_o1 = pl("His body, a name", "A(n:, /\\d/)", [OWNB], ["5", "7", "55"], "7 5", "5 7 5 3", LO_T)
P_o2 = pl("His body, the unspecified label", "A(_:, /\\d/)", [OWNB], ["5", "7", "55"], "7 5", "5 7 5 3", LO_T)
if sb("s24"):                                                # the plant: `_:` as the blank mark closing the stack
    SABB.update(("s12", "s14"))
    P_o2 = run("A(_:, /\\d/)", [OWNB])[0]
    SABB.difference_update(("s12", "s14"))
P_o3 = run("A(n:, /\\d/) & (n: 5)", [OWNB])[0]
check("OWNERBODY", P_o1 is not None and P_o2 is not None and answers(P_o1, pop("57", 2)) == answers(P_o2, pop("57", 2))
      and wh_(P_o1, ["5", "7", "55"]) == [True, False, False] and P_o3 is not None,
      "with `n:` %s, with `_:` %s, the same answers; the caller's `n` read %s"
      % (wh_(P_o1, ["5", "7", "55"]), wh_(P_o2, ["5", "7", "55"]), P_o3 is not None))

print("== LIBLINES: the library's lines under the one head (rx.repeat re-spelled `max = _`; padded_to; when)")
P_l1 = pl("The last item, through a label on the call", '[r = rx.repeat(/(?<a>\\d)/, min = 1, max = _)] & (r.a: "3")',
          [], ["73", "37"], "x37 73", "73 37 13", REP_T)
P_l2 = pl("A label written on the argument", "rx.repeat([a = rx.digit], min = 1, max = _) & (a: <5)", [],
          ["3", "73", "37"], "7 3", "37 73 4", REP_T, ann=["a"])
P_l3 = pl("Every item, a group question", '[r = rx.repeat(/(?<a>\\d)/, min = 1, max = _)] & some((r.a: "7"))', [],
          ["73", "33"], "x33 73", "73 33 17", REP_T)
P_l4 = pl("", "/${padded_to(/(?:\\d\\d)+?/, 3)}/", [], ["0129"], "x0129", "0129 0000 12", "lib/modifiers/padded-to")
P_l5 = pl("Two digits at least", "padded_to(rx.digit, 2)", [], ["5", "05", "005", "55"], "x5 07", "5 07 123",
          "lib/modifiers/padded-to")
ok_l6, r_l6 = rl("Through the argument's name", "W(A, (A.h: <5))", [W_AB, A_H], "condition 4",
                 "the spot is listed, a label made (binding-as-label, the manager's reading (b)); "
                 "`W([a = A], (a.h: <5))` reads it", "lib/control/when")
P_l7 = pl("The caller's own label", "W([a = A], (a.h: <5))", [W_AB, A_H], ["3", "7"], "7 3", "3 7 4", "lib/control/when")
ok_l8, r_l8 = rl("Through the argument's name", "peek(A) SEQ /\\d/ & (A.d: <5)", [A_D], "condition 4",
                 "the body lists the spot, a label made (binding-as-label); the read is `peek.d`", "lib/control/peek")
ok_l9, r_l9 = rl("Through the argument's name", "atomic(A) & (A.d: <5)", [A_D], "condition 4",
                 "the body lists the spot; the read is `atomic.d`", "lib/control/atomic")
ok_l10, r_l10 = rl("Through the argument's name", "hits(A) & (A.d: <5)", [A_D], "condition 4",
                   "the body labels the spot `hit`; the read is `hits.hit.d`", "lib/search/hits")
ok_l11 = refused("occurrences(A) & (A.d: <5)", [A_D], "condition 4")     # the sentence of lib/search/occurrences
P_l12 = pl("A binding used alone in a call, through its name", "identity(A) & (identity.d: <5)",
           [A_D, "identity(x) := /${[(=) = x]}/"], ["3", "7"], "7 3", "3 7 4", "lib/convention/argument-labels")
ok_l13, r_l13 = rl("The same read through the argument's name", "identity(A) & (A.d: <5)",
                   [A_D, "identity(x) := /${[(=) = x]}/"], "condition 4",
                   "the list on the spot is a label made (binding-as-label, the manager's reading (b))",
                   "lib/convention/argument-labels")
ok_lib = ok_l8 and ok_l9 and ok_l10 and ok_l11 and ok_l13 and P_l12 is not None
QD5 = pop("1x", 5)
dg = ndiff(answers(run("rx.digits")[0], QD5), answers(Re(r"\d+"), QD5))
print("   rx.digits against `\\d+`: %s of %d texts differ" % (dg, len(QD5)))
check("LIBLINES", all(x is not None for x in (P_l1, P_l2, P_l3, P_l4, P_l5, P_l7)) and ok_l6 and ok_lib and dg == (0, 0, 0) and
      len(QD5) == 63, "the re-spelled repeat lines %s; padded_to %s; `W(A, (A.h: ..))` refused %s (%s), "
      "`W([a = A], ..)` %s; through the argument's name refused in peek, atomic, hits, occurrences, identity %s; "
      "rx.digits against `\\d+` %s of %d" %
      ([x is not None for x in (P_l1, P_l2, P_l3)], [x is not None for x in (P_l4, P_l5)], ok_l6, r_l6,
       P_l7 is not None, [ok_l8, ok_l9, ok_l10, ok_l11, ok_l13], dg, len(QD5)))

print("== TABLE (label-doors, the ownership table): each cell's legality, run")
QT = ["3xx", "7xx"]
SX = "S(l:) := /(?<:${l}>\\d)/"
BODY = {"alone": B_XX, "labelled": B_PH, "listed": B_LS, "closed": B_CL, "stacked": B_ST}
COLS = ["alone", "labelled", "listed", "closed", "stacked", "forwarded"]
NA = ("n/a: only a label parameter is passed on (core/operators/bindings/label-forward)", None)
TROWS = [   # (who writes the name, {column: (cell text, program, binds, legal) or (cell text, None)})
    ("the reading definition's own text (`/(?<h>\\d)/` written there)", {
        "alone": ("`h` bare (line 1)", "/(?<h>\\d)xx/ & (h: <5)", [], True),
        "labelled": ("`h` bare, `x.h` too (lines 1, 2)", "[x = /(?<h>\\d)/] SEQ /xx/ & (h: <5)", [], True),
        "listed": ("`h` bare (line 1)", "[(=) = /(?<h>\\d)/] SEQ /xx/ & (h: <5)", [], True),
        "closed": ("`h` bare: its owner always reads it (line 4)", "[_ = /(?<h>\\d)/] SEQ /xx/ & (h: <5)", [], True),
        "stacked": ("`h` bare (lines 1, 5)", "[n = [_x = /(?<h>\\d)/]] SEQ /xx/ & (h: <5)", [], True),
        "forwarded": NA}),
    ("an argument's binding, passed whole (`B(A)`, A writes `h`)", {
        "alone": ("`A.h`, the shorthand (line 3; core/labels/paths/argument-default)", "B(A) & (A.h: <5)", [A_H, B_XX], True),
        "labelled": ("a compile error (condition 4); read `B.p.h` (core/labels/paths/closed-argument)", "B(A) & (A.h: <5)", [A_H, B_PH], False),
        "listed": ("a compile error (a reading: the list is a label made); read `B.h` (core/labels/paths/closed-argument)", "B(A) & (A.h: <5)", [A_H, B_LS], False),
        "closed": ("a compile error: the door is closed (line 4; core/labels/paths/closed-argument)", "B(A) & (A.h: <5)", [A_H, B_CL], False),
        "stacked": ("a compile error (condition 4); read `B.n.h` (line 5)", "B(A) & (A.h: <5)", [A_H, B_ST], False),
        "forwarded": NA}),
    ("the body (the label it writes on the spot)", {
        "alone": ("no label: `B.h` a compile error (core/labels/paths/call-prefix)", "B(A) & (B.h: <5)", [A_H, B_XX], False),
        "labelled": ("`B.p.h` (line 2)", "B(A) & (B.p.h: <5)", [A_H, B_PH], True),
        "listed": ("`B.h` (core/labels/export/export-list)", "B(A) & (B.h: <5)", [A_H, B_LS], True),
        "closed": ("none: `B.h` a compile error (line 4)", "B(A) & (B.h: <5)", [A_H, B_CL], False),
        "stacked": ("`B.n.h` (line 5); `B._x.h` a compile error, private", "B(A) & (B.n.h: <5)", [A_H, B_ST], True),
        "forwarded": NA}),
    ("the caller, inside an argument (`B([a = A])`)", {
        "alone": ("`a.h` (core/labels/export/arguments)", "B([a = A]) & (a.h: <5)", [A_H, B_XX], True),
        "labelled": ("`a.h`", "B([a = A]) & (a.h: <5)", [A_H, B_PH], True),
        "listed": ("`a.h`", "B([a = A]) & (a.h: <5)", [A_H, B_LS], True),
        "closed": ("`a.h`: another door (line 4; core/labels/paths/closed-argument)", "B([a = A]) & (a.h: <5)", [A_H, B_CL], True),
        "stacked": ("`a.h` (line 5)", "B([a = A]) & (a.h: <5)", [A_H, B_ST], True),
        "forwarded": NA}),
    ("a sent label (`B(S(x:))`), or one a body passes on", {
        "alone": ("`x` bare (core/operators/bindings/label-in-argument)", "B(S(x:)) & (x: <5)", [SX, B_XX], True),
        "labelled": ("`x` bare", "B(S(x:)) & (x: <5)", [SX, B_PH], True),
        "listed": ("`x` bare", "B(S(x:)) & (x: <5)", [SX, B_LS], True),
        "closed": ("`x` bare: the backdoor (line 4)", "B(S(x:)) & (x: <5)", [SX, B_CL], True),
        "stacked": ("`x` bare (line 5)", "B(S(x:)) & (x: <5)", [SX, B_ST], True),
        "forwarded": ("`x` bare (core/operators/bindings/label-forward)", "F(x:) & (x: <5)", ["F(l:) := /${S(l:)}xx/", SX], True)}),
]
if sb("s23"):                                                # the plant: one cell's legality flipped
    c_ = TROWS[1][1]["alone"]
    TROWS[1][1]["alone"] = (c_[0], c_[1], c_[2], False)
tb_bad = []
for who, cells in TROWS:
    for col in COLS:
        c = cells[col]
        if c[1] is None:
            continue
        Pg, err = run(c[1], c[2])
        legal = Pg is not None and wh_(Pg, QT) == [True, False]
        if (Pg is not None) != c[3] or (Pg is not None and not legal):
            tb_bad.append((who, col, c[1], "legal" if Pg is not None else err))
        print("   %-50s %-9s `%s`: %s" % (who[:50], col, c[1], "legal %s" % wh_(Pg, QT) if Pg else "refused: " + err[:90]))
    doc_line("| %s | %s |" % (who, " | ".join(cells[c][0] for c in COLS)), OWN_T)
check("TABLE", not tb_bad, "%d cells run (`3xx` holds, `7xx` fails where legal), each against its stated legality; "
      "disagreeing: %s" % (sum(1 for _, cs in TROWS for c in COLS if cs[c][1]), tb_bad or "none"))

print("== EXPAND (the expansion drill): each sugar form against its written-out expansion; legality and answers agree")
QX = ['3xx', '7xx', '7-3', '3-7', '<3>', '<7>', '5', '55', '7', '12', '123', '1234', '123456', '37', '73', 'ab', 'AB',
      'x', '3x', '7x', '']
B2 = "B2(rx, rs) := /${[p = rx]}-${rs}/"
DRILL = [   # (sugar, its binds, the written-out form, its binds, the documented expansion)
    ("B(A) & (A.d: <5)", [A_D, B_XX], "B([A = A]) & (A.d: <5)" if not sb("s15") else "B([A = A]) & (A.d: <5)",
     [A_D, B_XX] if not sb("s15") else [A_D, B_PH], "the shorthand: the label `A` written on the argument"),
    ("B(A) & (A.d: <5)", [A_D, B_BOTH], "B2(A, [a = A]) & (a.d: <5)", [A_D, B2],
     "the shorthand, a body using the argument alone and labelled: the label on the alone spot only"),
    ("W(_:, A) & (A.h: <5)", [W_, A_H], "W3(A) & (A.h: <5)", ["W3(v) := /<${v}>/", A_H],
     "`_:` on a spot: the part with no label"),
    ("A(_:, /\\d/)", [OWNB], "[_x = /\\d/] & (_x: 5)", [], "his body with `_:`"),
    ("A(x:) & (x: 5)", ["A(l:) := /(?<:${l}>\\d+)/"], "/(?<:x>\\d+)/ & (x: 5)", [], "a label parameter"),
    ("rx.repeat(rx.digit, 3)", [], "rx.repeat(rx.digit, 3, 3)", [], "an unset parameter takes its default"),
    ("rx.repeat(rx.digit, 3, _)", [], "/(?:\\d){3,}/", [], "`_` for the upper bound"),
    ("rx.repeat(rx.digit)", [], "/(?:\\d){0,}/", [], "`_` for both bounds"),
    ("rx.repeat(rx.digit, max = 5, min = 2)", [], "rx.repeat(rx.digit, 2, 5)", [], "named entries"),
    ("opt(_)", ["opt(o) := /(?${o})ab/"], "/ab/", [], "`_` for an option: no letters"),
    ("[n = [_x = P]] & (n.d: <5)", [P_], "[_x = [n = P]] & (n.d: <5)", [P_], "stacked labels, either order"),
    ('/(?<h>\\d)?x/ & (h ?: <5)', [], '/(?<h>\\d)?x/ & (h = "0": <5)', [], "`?:` as a default inside the set"),
]
xd_bad = []
for a_, ab, b_, bb, why in DRILL:
    Pa, ea = run(a_, ab)
    Pb, eb = run(b_, bb)
    same = (Pa is None) == (Pb is None) and (Pa is None or answers(Pa, QX) == answers(Pb, QX))
    print("   %s `%s` / `%s`: %s, %s (%s)" % ("AGREE" if same else "DIFFER", a_, b_, "refused" if Pa is None else
                                            "legal", "refused" if Pb is None else "legal", why))
    if not same or Pa is None:
        xd_bad.append(a_)
check("EXPAND", not xd_bad, "%d sugar forms against their written-out expansions, legality and every mode over %d "
      "texts; differing or refused: %s" % (len(DRILL), len(QX), xd_bad or "none"))

print("== READINGS: the manager's readings of the range a run can decide (the rest: the report, by record line)")
P_r1 = run("B(A) & (A.d: <5)", [A_D, "B(rx) := /xx/"])
P_r1x = run("B([A = A]) & (A.d: <5)", [A_D, "B(rx) := /xx/"])
P_r2 = run("T(rx.digit, _)", ["T(x, n) := /(?:${x}){${n},}b{0,${n}}/"])[0]
P_r3 = run("[n = [_x = P] SEQ \"!\"] & (n.d: <5)", [P_])[0]
P_r5 = run("B(A) & (A.d: <5)", [A_D, B_BOTH])[0]
RD = [   # (the reading, its entry, the run that decides it)
    ("unspecified-rule (b): `_` may be passed to any parameter, judged at each position it is laid into",
     lambda: P_r2 is not None and P_r2.whole("1b") and P_r2.whole("bbbb")),
    ("label-doors (a): anything between two labels makes two spots (the inner private label's door shut)",
     lambda: P_r3 is None),
    ("binding-as-label, both uses: the shorthand on the alone spot only (the second digit)",
     lambda: P_r5 is not None and P_r5.whole("7-3") and not P_r5.whole("3-7")),
]


def _verdict(f):
    try:
        return "SUPPORTED" if f() else "NOT SUPPORTED"
    except (CompileError, AttributeError, TypeError):
        return "NOT SUPPORTED"


RDV = [(a, _verdict(f)) for a, f in RD]
print("   UNTESTABLE: binding-as-label (c), never placed: the never-pass warning (the engine refuses the written-out "
      "label too, `B([A = A])`, so no warning is modelled for a caller's label never placed; the shorthand and its "
      "expansion agree: %s / %s)" % (P_r1[1], P_r1x[1]))
print("   UNTESTABLE as a run: the repeat-head finding, `${min|0}` is two values in a count hole, which makes copies "
      "(the loaded engine runs no binding of several numbers; the rule sentence it rests on, core/holes/count: "
      "\"Several values: ONE COPY OF THE LITERAL holding the holes per combination\")")
for a, v in RDV:
    print("   %s: %s" % (v, a))
check("READINGS", all(v == "SUPPORTED" for _, v in RDV), "%d readings run: %s" %
      (len(RDV), "all SUPPORTED" if all(v == "SUPPORTED" for _, v in RDV) else [a for a, v in RDV if v != "SUPPORTED"]))

print("== SWEEP: every printed three-mode line (`rejected:` and history lines skipped): predfix86's engine (the FOLD "
      "extensions off) over the starting commit's documents against this one over these; every non-same status and "
      "every moved or gone answer DECLARED")
_d0 = _src84.index("NOTMOD = ")
_d1 = _src84.index('if s84("s13"):')
exec(compile(_src84[_d0:_d1], P84, "exec"), globals())      # noqa: S102  predfix84's DECL_LINE / DECL_RULE, verbatim
OLDB = {f: _git("docs/design/predicates/" + f, STARTB) for f in DOCF}
J_ = "a JSON sketch line: its bodies (`row`, `value`, `string`, ...) are in the line's prose, not its tail (predfix86)"
DECLX = {                     # predfix86's declarations, verbatim in content: (file, program) -> (status, reason)
    ("library.md", 'row(v:, "v") & (v: "ok" | <5)'): ("REFUSED", J_),
    ("library.md", 'row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)'): ("REFUSED", J_),
    ("library.md", 'row(x:, "a" | "b") & (x: <5)'): ("REFUSED", J_),
    ("library.md", 'row(m:, "msg", contains("timeout"))'): ("REFUSED", J_),
}
DECLB = dict(DECLX)
DECL_RULEB = []
MOVEDB = {                    # program -> why its printed answer or legality moved, or why the line is gone
    "B(A) & (A.d: <5)": "binding-as-label (ruled): every line of this program moved; alone: a compile error "
                        "(argument-default) to LEGAL (SHORTHAND); labelled: legal (closed-argument (a), call-prefix "
                        "case 2) to a compile error, read `B.p.d`; both uses: the labelled spot's `d` to the alone "
                        "spot's (condition 4; READINGS); the old lines GONE where their label text changed",
    "rx.repeat(rx.digit, 3)": "call-forms (ruled): the two lines by `repeat(x, n)` and by `repeat(x, min)` are GONE "
                              "with the several bodies; one head, one count exact (REPEAT's line \"One count, exact\")",
    "/${padded(/(?:\\d\\d)+?/, 3)}/": "call-forms (ruled): padded's width form is GONE from padded, re-spelled "
                                       "`padded_to` in lib/modifiers/padded-to (LIBLINES); its old engine refused it",
    "W(/(?<h>\\d)/, (h: <5))": "the line's tail \"`W(A, (A.h: <5))` ... the same answers\" is GONE: under "
                                "binding-as-label that program is a compile error (LIBLINES); the line kept, same "
                                "answers, its key changed with the tail",
    '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & (r.a: "3")': "repeat-head (ruled): `min = 1` alone is now EXACTLY 1; "
        "the line re-spelled `min = 1, max = _` (the same answers: LIBLINES)",
    "rx.repeat([a = rx.digit], min = 1) & (a: <5)": "repeat-head: re-spelled `min = 1, max = _`, the same answers",
    '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & some((r.a: "7"))': "repeat-head: re-spelled `min = 1, max = _`, the "
        "same answers",
}
XB[0] = False
OLD_TB = sw_table84(OLDB)
XB[0] = True
NEW_TB = sw_table84(NOWS)
if sb("s18") and MOVEDB:
    MOVEDB.pop(next(iter(MOVEDB)))
swb_bad, swb_moved, swb_new, swb_gone, usedB = [], [], [], [], set()
cntB, whyB = {}, {}
for k, vs in NEW_TB.items():
    ov = OLD_TB.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cntB[st_] = cntB.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECLB.get((f_, k[0])) or DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                usedB.add((f_, k[0]))
                whyB[d_[1][:70]] = whyB.get(d_[1][:70], 0) + 1
            else:
                r_ = next((x for x in DECL_RULEB + DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    swb_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:160]))
                else:
                    usedB.add(r_[1])
                    whyB[r_[2][:70]] = whyB.get(r_[2][:70], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and o_[3] != got_:
            if k[0] in MOVEDB:
                usedB.add(("moved", k[0]))
            else:
                swb_moved.append((f_, ln_, k[0], o_[2], st_, o_[3][:160], got_[:160]))
    if not ov:
        swb_new.append((vs[0][0], vs[0][1], k[0]))
for k, vs in OLD_TB.items():
    if k not in NEW_TB:
        if k[0] in MOVEDB:
            usedB.add(("moved", k[0]))
        else:
            swb_gone.append((vs[0][0], vs[0][1], k[0], vs[0][2]))
staleB = sorted(k for k in DECLB if k not in usedB and k not in DECLX) + \
    sorted(k for k in MOVEDB if ("moved", k) not in usedB)
for k_, n_ in sorted(whyB.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in swb_gone:
    print("   GONE %s:%d `%s` (was %s)" % x)
for x in swb_new:
    print("   ADDED %s:%d `%s`" % x)
for x in swb_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)\n      old: %s\n      now: %s" % x)
for x in swb_bad:
    print("   BAD %s" % (x,))
for x in staleB:
    print("   STALE DECLARATION %s" % (x,))
for k_, why in sorted(MOVEDB.items()):
    print("   ANSWER MOVED (declared): `%s`: %s" % (k_, why))
check("SWEEP", OLD_TB and not swb_bad and not swb_moved and not swb_gone and not staleB,
      "%d printed lines now (%s), %d at the starting commit under predfix86's engine; undeclared %d; moved or gone "
      "and not declared %d; declared moves %d; added %d; stale declarations %d" %
      (len(NEW_TB), ", ".join("%s %d" % kv for kv in sorted(cntB.items())), len(OLD_TB), len(swb_bad),
       len(swb_moved) + len(swb_gone), len(MOVEDB), len(swb_new), len(staleB)))

print("== NULLABLE: EVID-4's known limit: no program the extended engine ran has a loop whose body can match empty")
exec(compile(_src84[_src84.index("def nullable(n):"):_src84.index("checked = list(RUN)")], P84, "exec"),
     globals())                                              # noqa: S102  predfix84's walker, verbatim
_nullable84 = nullable


def nullable(n):                                             # noqa: F811
    return False if n[0] == "ncls" else _nullable84(n)


checkedB = list(RUN)
nlB = [(e, b) for e, b, nd in checkedB if loops_nullable(nd, [])]
check("NULLABLE", not nlB, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a "
      "loop whose body can match empty%s" % (len(checkedB), len(nlB), (": %s" % nlB[:4]) if nlB else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line")
SUPERSEDEDB = {               # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
}
MODELSB = ["predfix86", "predfold1123", "predfix84", "predspot", "predfix83", "preddef", "predfix82", "predcall",
           "predref", "predbound", "predfix77", "predarr", "predscope"]
if sb("s19") and SUPERSEDEDB:
    k0 = next(iter(SUPERSEDEDB))
    SUPERSEDEDB[k0].pop(next(iter(SUPERSEDEDB[k0])), None)
succB_bad, succB_n = [], 0
LANESB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if not LIGHTB:
    for mname in MODELSB:
        env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")
               and not k.endswith("_PROBE")}
        if mname == "predfix86":
            env["PREDFIX86_LIGHT"] = "1"                     # its SUCCESSOR re-runs the twelve below: run once, here
        if mname == "predfold1123":
            env["PREDFOLD_LIGHT"] = "1"
        if mname == "predfix84":
            env["PREDFIX84_LIGHT"] = "1"
        out = subprocess.run([sys.executable, "-I", "-B", os.path.join(LANESB, mname + "_evidence", mname + "_model.py")],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, timeout=3600).stdout
        succB_n += 1
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
        decl = SUPERSEDEDB.get(mname, {})
        print("   %-12s last line: %s" % (mname, last[:160]))
        for r, fline in sorted(reds.items()):
            dg = hashlib.sha256(fline.encode()).hexdigest()[:12]
            d = decl.get(r)
            if d is None:
                succB_bad.append((mname, r, "UNDECLARED"))
                print("      %s [%s] UNDECLARED: %s" % (r, dg, fline[:400]))
            elif d[0] != dg:
                succB_bad.append((mname, r, "CONTENT CHANGED"))
                print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fline[:400]))
            else:
                print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
                print("         its FAIL line: %s" % fline[:240])
        gone = sorted(set(decl) - set(reds))
        if gone:
            succB_bad.append((mname, "GREEN", gone))
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHTB or (succB_n == len(MODELSB) and not succB_bad),
      "%d earlier models re-run one at a time (predfix86, predfold1123 and predfix84 light: their SUCCESSOR is this "
      "list), each last line read; every red declared superseded with an unchanged FAIL line: %s"
      % (succB_n, "yes" if not succB_bad else succB_bad))

print("== QUOTES: the owner's sentences and the rulings' titles of the range, in the record at the PINNED start "
      "commit and in the documents")
RECORDB = _git("docs/design/plan_row_bodies/COND-FAMILY.md", STARTB)
QQB = [
    "unspecified-rule: yes and elegant",
    "call-forms: yes.",
    "repeat-head: agree with your lean",
    "binding-as-label: yes",
    "label-doors: agree. Yes",
    "I agree the count semantics should work that way",
    "repeat(X, _, 5) is 0 up to 5",
    "you can't go through A to get inside",
    "It's closing that door but there may be other doors.",
    "So I agree with your lean.",
    "Strictly that A doesn't make them visible through it.",
    "the general canonical form is that all labels are chains of only labels",
    "would the nesting order of the labels matter? By my reading no",
    "Consider one additional rule based on your examples which is that a label on the binding has not already been made",
    "An argument given as the underscore says: this part is not written. The body then means what the construct at "
    "that position already means without that part. Where the construct has no form without the part, the call is a "
    "compile error.",
    "1. One head per name. There is no overloading; a call is never matched against several bodies.",
    "2. Positional entries first, then named ones. Positional entries fill the parameters in declared order, "
    "including those with defaults. Any parameter may be named. A positional entry after a named one is a compile "
    "error for now.",
    "3. A default is the macro's own text. It is resolved in the macro's definition, and it may name an earlier "
    "parameter, never a later one.",
    "4. Unset and the underscore are different. An argument left unset takes its default. The underscore does not "
    "take the default; it means \"not written\", by the rule you just ruled.",
    "A binding's name may be used in a path as shorthand for a skipped label where: 1. the binding is referenced "
    "unambiguously; 2. a label could have been set on it there; 3. the reference reads as though through that label; "
    "4. no label has already been made on it there.",
    "1. A label is owned by the text that writes its name; there it is read bare.",
    "2. Any other label is read by a path, and a path is a chain of labels.",
    "3. A binding's name may stand in a path for a skipped label, under your four conditions.",
    "4. Each part decides the doors through itself, and closing one closes only that one.",
    "5. Labels stacked on one spot are equal names of it; their order does not matter.",
    "Labels stacked on one spot, with nothing between them, are equal names of that spot. Each is its own door to "
    "what the spot holds. One of them being private or blank closes only itself.",
]
TTB = [
    '2026-11-23 OWNER RULING — count-unspecified: "I agree the count semantics should work that way"; and the bigger question: do the argument rules force positions to be defined "meet me half way"',
    '2026-11-23 OWNER RULING — unspecified-rule: "yes and elegant" (the underscore as an argument: the part is not written)',
    "2026-11-23 OWNER RULING — call-forms: yes (one head per name; positional entries first, then named; a default is the macro's own text and may name an earlier parameter; unset takes the default, the underscore does not)",
    '2026-11-23 OWNER RULING — repeat-head: "agree with your lean" (head (i): `repeat(x, min = _, max = min)`)',
    '2026-11-23 OWNER RULING — closing-own-label: "I agree with your lean" (a caller\'s own label is not closed); the export statement closes ONE door: "there may be other doors"',
    "2026-11-23 OWNER RULING — binding-as-label: yes (a path is canonically a chain of labels; a binding's name is a shorthand for a skipped label, under four conditions)",
    '2026-11-23 OWNER RULING — label-doors: "agree. Yes" (the general rule of labels, five lines)',
    '2026-11-23 OWNER RULING — label-hole-full: a pure label\'s name hole must be whole; a capture\'s name may be partial, "but again, the label portion is lost"; and a sketch of the repeat head with a conditional default',
]
ALLNOWB = "\n".join(NOWS.values())
if sb("s20"):                                                # the plant: one owner sentence altered in the documents
    ALLNOWB = ws(ALLNOWB).replace(ws("label-doors: agree. Yes"), ws("label-doors: agree."))
RWB = ws(RECORDB)
q_missB = [q for q in QQB if ws(q) not in RWB or ws(q) not in ws(ALLNOWB)]


def headsB(rec):
    return set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in rec.split("\n") if l_.startswith(("### ", "**")))


DETB = NOWS["core_details.md"] + NOWS["library_details.md"] + NOWS["parked_details.md"]
t_missB = [t_ for t_ in TTB if ws(t_) not in headsB(RECORDB) or ws('(record: "%s")' % t_) not in ws(DETB)]
check("QUOTES", not q_missB and not t_missB,
      "%d quoted sentences, in the record at %s and the documents, missing: %s; %d record titles cited whole as a "
      "`rulings:` item's record, not a title or not cited: %s" % (len(QQB), STARTB, q_missB or "none", len(TTB),
                                                                 t_missB or "none"))

print("== DOC: every line this model formats occurs verbatim in the piece its tag names")


def piece_ofB(tag):
    for f_, txt in NOWS.items():
        if f_.endswith("_details.md"):
            continue
        mm = re.search(r"^### .*\[%s\].*$" % re.escape(tag), txt, re.M)
        if mm:
            nx = re.search(r"^### ", txt[mm.end():], re.M)
            return txt[mm.start():mm.end() + (nx.start() if nx else len(txt))]
    return ""


DLNB = list(LINES)
if sb("s21") and DLNB:
    DLNB[0] = (DLNB[0][0], DLNB[0][1].replace("WHOLE `", "WHOLE `x", 1))
if sb("s22") and DLNB:
    DLNB[0] = ("core/spellings/placeholders", DLNB[0][1])
d_missB = [(t_, L) for t_, L in DLNB if ws(L) not in ws(piece_ofB(t_))]
for t_, L in d_missB:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLNB and not d_missB, "%d lines, each in its own piece; missing: %d" % (len(DLNB), len(d_missB)))

failedB = [n for n, ok in RESULTS if not ok]
print("predfold1123b_model: %d checks, %d failed%s" % (len(RESULTS), len(failedB),
                                                      (" (%s)" % ", ".join(failedB)) if failedB else ""))
sys.exit(1 if failedB else 0)
