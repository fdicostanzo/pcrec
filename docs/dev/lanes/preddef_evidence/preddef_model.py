#!/usr/bin/env python3
# Lane preddef (2026-11-22): the evidence for folding the owner's ruling "default-export: protected" (record
# "2026-11-22 OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not
# exported)") into the predicate documents, and the manager's readings (a)..(h) of the lane brief tested.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predfix82's model is LOADED unchanged: predfix82_model.py is executed up to its line "the checks" (it
# loads predcall's, which loads predref's, which loads predbound's lowerer and matcher). Its plants are cleared.
# The RULE below then replaces, in the loaded engine (the names resolve at call time in one namespace):
#   PROTECT  a part USED ALONE in a binding's body (a bound name or a pattern macro's call written as a sequence
#            operand, in a hole or as an `&` operand, under no part label) keeps its labels inside that body
#            (through its own name, `A.h`) and exports none of them: its groups lose every scope outside the body,
#            as under `[_A = A]` with the local name `A` (reading (a)). At the top-level program nothing is outside.
#            A part label `[x = ..]` (and everything written under it) is NOT a use alone: its part's exported
#            labels pass out through it as before (statement 3 for a labelled part).
#   ARGS     an ARGUMENT the macro body uses alone (`${rx}`) is not exported by the call: neither the call's name
#            (`B.d`) nor a label on the call (`c.d`) reaches its labels (reading (e)). The caller's own `A.d` is
#            open argument-default: ARGDEF "local" (the caller's local read of its own part, legal) or "error"
#            (not visible, a compile error). Both are run; neither is applied. An argument written in place stays
#            the caller's own text under both (a reading, call-prefix's "An argument written in place").
#   VISIBLE  a path read INSIDE a binding's body to a label not visible there is the same compile error the loaded
#            engine raised only at the top-level program (a label not visible through its source).
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. The check NULLABLE greps every
# program this model's checks run for one and fails if found.
#
# Run (W = the worktree; any cwd):  timeout 900 python3 -I -B W/docs/dev/lanes/preddef_evidence/preddef_model.py
# The model EXITS NON-ZERO when any check fails; its verdict is its LAST LINE.
# PREDDEF_ENGINE=old runs the loaded engine WITHOUT the rule (SWEEP's control; prints one table and exits).
# PREDDEF_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL. Listed with
# the checks at the end of this header block (PLANTS).
import os
import re
import subprocess
import sys

HERE3 = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(HERE3, "..", "predfix82_evidence", "predfix82_model.py")
SABD = set(x for x in os.environ.get("PREDDEF_SABOTAGE", "").split(",") if x)
ENGINE_D = os.environ.get("PREDDEF_ENGINE", "new")
for v in ("PREDFIX82_SABOTAGE", "PREDFIX82_ENGINE", "PREDCALL_SABOTAGE", "PREDREF_SABOTAGE", "PREDBOUND_SABOTAGE"):
    os.environ.pop(v, None)


def sd(n):
    return n in SABD


_src3 = open(PF, encoding="utf-8").read()
_cut3 = re.search(r"^# =+ the checks$", _src3, re.M).start()
exec(compile(_src3[:_cut3], PF, "exec"), globals())         # noqa: S102  (predfix82's definitions, unchanged)
SAB82.clear()
SABC.clear()
SABR.clear()
SAB.clear()

OLD82 = dict(lower_atom=lower_atom, use_definition=use_definition, prefix_parts=prefix_parts, Ctx_sub=Ctx.sub)

# ================================================================== the RULE (lane preddef)
ARGDEF = ["local"]            # open argument-default: "local" | "error"
ARG_PARTS = set()             # part strings an argument used alone in a body left; no later prefix takes them
Ctx.labelled = False          # True while lowering under a part label written in the same definition
_ctx_sub0 = Ctx.sub


def _ctx_sub(self, **kw):
    c = _ctx_sub0(self, **kw)
    c.labelled = self.labelled
    return c


_base_binds_d = base_binds


def base_binds():                                            # noqa: F811
    _base_binds_d()
    ARG_PARTS.clear()


def all_parts(text):
    out = set()
    for g in GROUP_NAME.findall(text):
        out |= set(g.split(";"))
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES.get(int(n))
        if nd and nd[0] == "setv":
            out |= set(nd[1].split(";"))
    return out


_prefix_parts_d = prefix_parts


def prefix_parts(text, prefix, at, vis, kind):               # noqa: F811
    """As predfix82's; a part an argument used alone left (ARG_PARTS) is never prefixed again (ARGS)."""
    if not ARG_PARTS or sd("s2"):
        return _prefix_parts_d(text, prefix, at, vis, kind)
    hide = {}

    def mask(mm):
        ps = mm.group(1).split(";")
        keep = [p for p in ps if p not in ARG_PARTS]
        held_ = [p for p in ps if p in ARG_PARTS]
        if not held_:
            return mm.group(0)
        k = "zz%d" % len(hide)
        hide[k] = held_
        return "(?<%s>" % ";".join(keep + ["%s@hidden" % k])
    t2 = GROUP_NAME.sub(mask, text)
    t3 = _prefix_parts_d(t2, prefix, at, vis, kind)

    def unmask(mm):
        ps = mm.group(1).split(";")
        out = []
        for p in ps:
            base, _, sc = p.partition("@")
            if sc == "hidden" and base in hide:
                out += hide[base]
            elif sc == "hidden" or base.split(".")[-1] in hide:
                continue
            else:
                out.append(p)
        return "(?<%s>" % ";".join(out)
    return GROUP_NAME.sub(unmask, t3)


_lower_atom_d = lower_atom


def is_part_label(e):
    return re.fullmatch(r"\[(\w*) = (.*)\]([+*?]?)", e, re.S) is not None


def lower_atom(expr, ctx):                                   # noqa: F811
    e = expr.strip()
    if is_part_label(e):                                     # a labelled part: its contents pass out through it
        lc = ctx.sub()
        lc.labelled = True
        return _lower_atom_d(e, lc)
    alone = not ctx.labelled and ctx.cur != "top"
    if e in ctx.params:                                      # ARGS: an argument used alone in the body
        text = _lower_atom_d(e, ctx)
        if not ctx.labelled and not sd("s3"):
            arg = ctx.params[e][0].strip()
            ARG_PARTS.update(all_parts(text))
            if ARGDEF[0] == "error":
                caller = ctx.params[e][1]
                text = close_parts(text, caller.scopes)
        return text
    call = parse_call(e)
    pattern_use = ((e in BINDS and not is_cond(BINDS[e]) and not is_set_body(BINDS[e])) or
                   (call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0])
                    and not is_cond(pick_macro(*call)[1])))
    text = _lower_atom_d(e, ctx)
    if pattern_use and alone and not sd("s1"):              # PROTECT
        text = close_parts(text, ctx.scopes[:-1])
    return text


_use_definition_d = use_definition


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    """VISIBLE: a path the body reads must be visible in the body (as prog checks at the top-level program)."""
    sc = "s%d" % (COUNTER[0] + 1)
    start = len(NAMED)
    saved = ctx.labelled
    text = _use_definition_d(body, ctx, dname, params, mark)
    if not sd("s4"):
        seen = surfaced(text, sc)
        for scope, nm in NAMED[start:]:
            if scope == sc and "." in nm and nm not in seen:
                raise CompileError("`%s`: `%s` is not visible through `%s` in %s (a compile error, "
                                   "core/labels/export)" % (nm, nm.split(".", 1)[1], nm.split(".")[0], dname))
    ctx.labelled = saved
    return text


_is_set_body_d = is_set_body


def is_set_body(body, _seen=()):                             # noqa: F811
    """SETAND: an `&` chain with a pattern operand (a literal, a part label, a bound PATTERN) is a pattern, not a
    set (the loaded test read `B := A & A` and `A & /(?<b>\\d)/` as sets and dropped the binding's use)."""
    if not sd("s5"):
        for op in split_top(body.strip(), " & "):
            op = op.strip()
            if op.startswith("/") or op.startswith("[") or op.startswith('"'):
                if len(split_top(body.strip(), " & ")) > 1:
                    return False
            if op in BINDS and op not in _seen and len(split_top(body.strip(), " & ")) > 1:
                b = BINDS[op]
                if not is_cond(b) and not is_set_body(b, _seen + (op,)):
                    return False
    return _is_set_body_d(body)


_prog_d = prog


def prog(expr, binds=(), **opts):                            # noqa: F811
    """VISIBLE at the top-level program: a bare name read there must be one some group there sets (a label of an
    argument the body uses alone is not, under argument-default's candidate "error")."""
    Pg = _prog_d(expr, binds, **opts)
    if not sd("s4"):
        seen = surfaced(Pg.rx, "top")
        for sc, nm in NAMED:
            if sc == "top" and "." not in nm and not nm.isdigit() and nm not in seen:
                raise CompileError("`%s`: no group visible here sets it (a compile error, core/labels/export)" % nm)
    return Pg


if ENGINE_D == "old":
    globals().update(OLD82)
else:
    Ctx.sub = _ctx_sub

if ENGINE_D == "old":
    for f, ln, line_, a, pt, tail in sweep_lines():
        st, got = sweep_one(line_, a, pt, tail)
        print("SW\t%s\t%d\t%s\t%s" % (f, ln, st, got if st in ("same", "DIFF") else ""))
    sys.exit(0)

# ================================================================== the checks
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


if os.environ.get("PREDDEF_PROTO"):
    envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
    envo["PREDDEF_ENGINE"] = "old"
    oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                        env=envo, timeout=600)
    OLD_SW = {}
    for l_ in oo.stdout.split("\n"):
        if l_.startswith("SW\t"):
            _, f_, ln_, st_, got_ = l_.split("\t", 4)
            OLD_SW[(f_, int(ln_))] = (st_, got_)
    if not OLD_SW:
        print(oo.stdout[-3000:], oo.stderr[-3000:])
    for f, ln, line_, a, pt, tail in sweep_lines():
        for ad in ("local", "error"):
            ARGDEF[0] = ad
            st, got = sweep_one(line_, a, pt, tail)
            o = OLD_SW.get((f, ln), ("?", ""))
            if o[0] != st or (st in ("same", "DIFF") and o[1] != got):
                print("MOVED %s %s:%d old=%s new=%s %s | %s" % (ad, f, ln, o[0], st, got[:100], line_[:220]))

if os.environ.get("PREDDEF_LIST"):
    for f, ln, line_, a, pt, tail in sweep_lines():
        st, got = sweep_one(line_, a, pt, tail)
        if st != "same":
            print("L %s:%d %s %s || %s" % (f, ln, st, got[:90], line_[line_.index(a) + len(a):][:160]))
