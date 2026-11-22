#!/usr/bin/env python3
# Lane predfix82 (2026-11-22): the evidence for applying review r82's ruled dispositions (predfold1122) to the
# predicate documents: the engine fixes the review asks for (EVID-2, EVID-3, ANS-2c/d, flow's `&` ambiguity), the
# checks it asks for (EVID-5, ANS-3, ANS-5, ANS-6, closed-argument's `_x` half, a quantifier-order plant), a
# SUCCESSOR check over every earlier in-force model (EVID-1), and the manager's readings of the dispositions tested.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predcall's model is LOADED unchanged: predcall_model.py is executed up to its line "the checks" (it in
# turn loads predref's, which loads predbound's lowerer and label matcher). Its plants are cleared. The FIXES below
# then replace, in the loaded engine (the names resolve at call time in one namespace), exactly these parts:
#   PREFIX   a prefix (a part label `[x = E]`, a used binding `B`, a pattern macro's call `m(..)`) gives the labels
#            it surfaces a key `x.h` IN THE DEFINITION THE PREFIX IS WRITTEN IN ONLY (ANS-2c, the manager's reading:
#            "the prefix reaches the uses written in the referencing definition's own text, not a use nested inside
#            another used binding"); the old engine gave `x.h` every enclosing scope, so a use nested in another
#            used binding reached the outer definition's `x.h`.
#   PATHS    ANS-5, the manager's reading: a source is a path of names, each step passed by the previous one: a used
#            binding or a call passes the paths its body made (`pub.a.h`, `days.w.index`); a part label passes the
#            paths of part labels inside it, never a use's prefix ("[ c = B(A) ] does not allow c.A").
#   CLOSE    EVID-2: a `_x` part label (`[_p = A]`) is an ordinary part label INSIDE its binding (`_p.d` legal there)
#            and closes every label of its part OUTSIDE the binding (statements 6, 7 of core/labels/export).
#   AND      EVID-3: a pattern operand of `&` after the first is lowered ONCE, in the same definition, and matched
#            whole on the first operand's stretch keeping its labels, so its labels reach the condition (the old
#            engine lowered it twice, once in a fresh scope, and dropped its labels).
#   AMBIG    flow: across `&` a name both sides surface is an ambiguous reference: a plain read of it (a condition
#            entry, a `$` read) is a compile error; a group question over it is not.
#   USES     ANS-2d, the manager's reading: a binding's or macro's uses are counted in the referencing definition's
#            TEXT, before macros expand (a name written once is one use however often a body lowers it).
#   INDEX    ANS-6, the manager's reading: the index `x.h[k]` takes a path; through a prefix whose uses are joined
#            by `&` it is a compile error (the two sides of `&` are not ordered); through sequenced uses, text order.
#   VALUEGQ  ANS-3, the manager's reading: a value entry (`$h`, arithmetic, `count`) inside a group question is a
#            compile error for now.
#   HIDE     DES-6, the manager's reading: a part label written in the definition wins over a macro's or a
#            binding's name of the same spelling, and the hide-label warning is drawn.
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. No printed line tied to a check
# here has a nullable loop body; the check NULLABLE greps every program this model runs for one and fails if found.
#
# Run (W = the worktree; any cwd):  timeout 600 python3 -I -B W/docs/dev/lanes/predfix82_evidence/predfix82_model.py
# The model EXITS NON-ZERO when any check fails; its verdict is its LAST LINE.
# PREDFIX82_ENGINE=old runs the loaded engine WITHOUT the fixes (used by SWEEP as its control; prints one table).
# PREDFIX82_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  a quantifier tries its greedy choice last (lazy and greedy swapped)                    -> ORDER
#   s2  the `_x` closure ignored (a `_x` part label passes its part's labels out)              -> CLOSEDX
#   s3  a later `&` operand's labels dropped (the old engine's behaviour)                       -> SECOND
#   s4  the `&` ambiguity error off                                                            -> AMBIG
#   s5  uses counted per lowering, not in the text (an argument twice lowered counts twice)     -> TEXTUSES
#   s6  a prefix reaches a use nested in another used binding (the old engine's behaviour)      -> NESTED
#   s7  a prefix read answered as the bare last mention                                        -> CONTRAST
#   s8  a used binding passes no paths of its body (no nested path)                             -> PATHS
#   s9  the index through `&`-joined uses accepted                                              -> INDEX
#   s10 a value entry inside a group question accepted (read per setting)                       -> VALUEGQ
#   s11 the part label loses to a macro's name of the same spelling                             -> HIDE
#   s12 a SET that reads a label, bound alone, accepted                                        -> BOUNDSET
#   s13 one earlier model's expected verdict altered (in memory)                               -> SUCCESSOR
#   s14 one formatted line's subject altered before the document lookup                         -> DOC
#   s15 a planted nullable-body program in the checked set                                     -> NULLABLE
#   s16 a quoted owner sentence altered (in memory)                                            -> QUOTES
#   s17 one disposition's applied marker read back as missing (in memory)                       -> MARKS
#   s18 one printed line's program given a wrong answer by the fixed engine (in memory)          -> SWEEP
#   s19 `|` and `&` inside a value left of `:` accepted                                        -> GAPS
#   s20 candidate (b)'s direct read taken on the second digit (a wrong control fact)            -> TWOSRC
#   s21 the value-left comparison written `<=` (the 100-pair control altered)                   -> REPRINT
# s1 also fails CONTROL (the matcher against python `re`), CONTROL's own plant.
import os
import re
import subprocess
import sys

HERE2 = os.path.dirname(os.path.abspath(__file__))
PC = os.path.join(HERE2, "..", "predcall_evidence", "predcall_model.py")
SAB82 = set(x for x in os.environ.get("PREDFIX82_SABOTAGE", "").split(",") if x)
ENGINE = os.environ.get("PREDFIX82_ENGINE", "new")
for v in ("PREDCALL_SABOTAGE", "PREDREF_SABOTAGE", "PREDBOUND_SABOTAGE"):
    os.environ.pop(v, None)


def s82(n):
    return n in SAB82


_src2 = open(PC, encoding="utf-8").read()
_cut2 = re.search(r"^# =+ the checks$", _src2, re.M).start()
exec(compile(_src2[:_cut2], PC, "exec"), globals())         # noqa: S102  (predcall's definitions, unchanged)
SABC.clear()
SABR.clear()
SAB.clear()
NEW = {f: read(os.path.join(PRED, f)) for f in ("core.md", "library.md", "parked.md", "core_details.md",
                                                 "library_details.md", "parked_details.md")}
ALLDOC = "\n".join(NEW.values())

# ================================================================== the loaded engine, kept for the control
OLD_ENGINE = dict(lower_atom=lower_atom, lower_and=lower_and, plain_prefix_check=plain_prefix_check,
                  source_check=source_check, lower_gq=lower_gq, is_gq=is_gq, m=m, prog=prog,
                  use_definition=use_definition, base_binds=base_binds, use_param=use_param, add_prefix=add_prefix,
                  lower_cond=lower_cond, p_atom=p_atom, binding_check=binding_check)
WARNINGS = []

# ================================================================== the FIXES (lane predfix82)
CLOSED_PARTS = set()          # part strings `name@scopes` closed by a `_x` part label (never prefixed again)
PART_KIND = {}                # dotted part base -> "use" (made by a binding's or call's prefix) | "part"
DEFTEXT = {}                  # scope -> the text of the definition lowered in it (the program, a body)
AND_JOINED = set()            # (scope, prefix) whose uses sit in two or more operands of one `&`
_base_binds82 = base_binds


def base_binds():                                            # noqa: F811
    _base_binds82()
    CLOSED_PARTS.clear()
    PART_KIND.clear()
    DEFTEXT.clear()
    AND_JOINED.clear()
    del WARNINGS[:]


GROUP_NAME = re.compile(r"\(\?<([^>=!][^>]*)>")


def parts_of(name):
    """`h@top,s1;A.h@top` -> [("h", ["top", "s1"]), ("A.h", ["top"])]."""
    out = []
    for p in name.split(";"):
        base, _, sc = p.partition("@")
        out.append((base, sc.split(",") if sc else ["top"]))
    return out


def join_parts(ps):
    return ";".join("%s@%s" % (b, ",".join(s)) for b, s in ps)


def private(base):
    return any(w.startswith("_") for w in base.split("."))


def prefix_parts(text, prefix, at, vis, kind):
    """PREFIX + PATHS: every group (and META member node) in `text` gets `prefix.base@at` for each of its parts
    that qualifies. A plain part qualifies unless closed or private. A dotted part qualifies when made inside the
    prefixed body (its scopes include `vis`) and, for a part label (kind "part"), only when it is itself a part
    label's path, never a use's prefix."""
    if prefix.startswith("_") and kind != "own":
        return text

    def new_parts(ps):
        add = []
        for base, sc in ps:
            if "%s@%s" % (base, ",".join(sc)) in CLOSED_PARTS or private(base):
                continue
            if "." in base:
                if s82("s8") and kind == "use":
                    continue
                if vis not in sc:
                    continue
                if kind in ("part", "own") and PART_KIND.get(base, "part") == "use":
                    continue
            elif s82("s6"):
                add.append(("%s.%s" % (prefix, base), sc))   # the old engine: every enclosing scope
                continue
            add.append(("%s.%s" % (prefix, base), [at]))
        for b, _ in add:
            PART_KIND.setdefault(b, "use" if kind == "use" else "part")
        return add

    def rep(mm):
        ps = parts_of(mm.group(1))
        return "(?<%s>" % join_parts(ps + new_parts(ps))
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES[int(n)]
        if nd[0] == "setv":
            ps = parts_of(nd[1])
            NODES[int(n)] = ("setv", join_parts(ps + new_parts(ps)), nd[2])
    return GROUP_NAME.sub(rep, text)


def close_parts(text, outer):
    """CLOSE: drop every outer scope from every part in `text`; a part left with no scope is dropped; a group
    left with no part becomes `(?:`. The parts left are recorded closed."""
    outer = set(outer)

    def fix(ps):
        out = []
        for base, sc in ps:
            sc2 = [x for x in sc if x not in outer]
            if sc2:
                out.append((base, sc2))
                CLOSED_PARTS.add("%s@%s" % (base, ",".join(sc2)))
        return out

    def rep(mm):
        ps = fix(parts_of(mm.group(1)))
        return "(?<%s>" % join_parts(ps) if ps else "(?:"
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES[int(n)]
        if nd[0] == "setv":
            ps = fix(parts_of(nd[1]))
            NODES[int(n)] = ("setv", join_parts(ps) if ps else "_closed@none", nd[2])
    return GROUP_NAME.sub(rep, text)


def first_scope(text):
    for n in re.findall(r"\$\{#(\d+)\}", text):
        if NODES[int(n)][0] == "enter":
            return NODES[int(n)][1]
    return None


# ---- USES: counted in the definition's text
def text_uses(t):
    """name -> uses of a binding or macro written in definition text `t` (literals' holes included)."""
    e, rxs, holes = split_rx(t)
    cnt = {}
    for mm in re.finditer(r"(?<![\w.$@])([A-Za-z_]\w*(?:\.\w+)*)(\s*\()?", e):
        name, call = mm.group(1), mm.group(2)
        after = e[mm.end():]
        if re.match(r"\s*:(?!=)", after) or re.match(r"\s+=\s", after) or re.match(r"\s*\[\d+\]\s*:", after):
            continue
        if call and name in MACROS:
            cnt[name] = cnt.get(name, 0) + 1
        elif not call and name in BINDS:
            cnt[name] = cnt.get(name, 0) + 1
    for h in holes:
        for k, v in text_uses(h).items():
            cnt[k] = cnt.get(k, 0) + v
    return cnt


def set_uses(scope, text):
    DEFTEXT[scope] = text
    if s82("s5"):
        return
    for k in [k for k in USES if k[0] == scope]:
        del USES[k]
    for k, v in text_uses(text).items():
        USES[(scope, k)] = v


_use_definition82 = use_definition


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    sc = "s%d" % (COUNTER[0] + 1)                           # the scope the loaded use_definition makes first
    set_uses(sc, body)
    text = _use_definition82(body, ctx, dname, params, mark)
    assert first_scope(text) == sc, (sc, first_scope(text))
    return text


# ---- PREFIX for the three spellings
_lower_atom82 = lower_atom                                   # predcall's (macro prefix) over predbound's PATHS one
_lower_atom_paths = _lower_atom2                             # predbound's PATHS layer (no macro prefix)


def own_written(scope):
    return own_labels(DEFTEXT.get(scope, ""))


def lower_atom(expr, ctx):                                   # noqa: F811
    e = expr.strip()
    mm = re.fullmatch(r"\[(\w*) = (.*)\]([+*?]?)", e, re.S)
    if mm and not mm.group(2).startswith("[") and mm.group(1) != "_":
        name, inner_e, q = mm.groups()
        inner = lower(inner_e, ctx)
        ctx.held.add(name)
        inner = prefix_parts(inner, name, ctx.cur, ctx.cur, "own" if name.startswith("_") else "part")
        grp = "(?<%s@%s>%s)%s" % (name, ",".join(ctx.scopes), inner, q)
        if name.startswith("_") and not s82("s2"):
            grp = close_parts(grp, ctx.scopes[:-1])
        return grp
    if e in BINDS and not is_cond(BINDS[e]) and not is_set_body(BINDS[e]):
        text = use_definition(BINDS[e], ctx, e)
        b = first_scope(text)
        if s82("s5"):                                        # plant: a use counted per lowering
            USES[(ctx.cur, e)] = USES.get((ctx.cur, e), 0) + 1
        USE_SC.setdefault(e, set()).add(b)
        ctx.held.add(e)
        if e in own_written(ctx.cur):                       # HIDE: the part label written here wins
            WARNINGS.append(("hide-label", e))
            return text
        return prefix_parts(text, e, ctx.cur, b, "use")
    call = parse_call(e)
    if (call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0])
            and not is_cond(pick_macro(*call)[1])):
        text = _lower_atom_paths(e, ctx)
        b = first_scope(text)
        ctx.held.add(call[0])
        if call[0] in own_written(ctx.cur) and not s82("s11"):
            WARNINGS.append(("hide-label", call[0]))
            return text
        return prefix_parts(text, call[0], ctx.cur, b, "use")
    return _lower_atom82(expr, ctx)


# ---- AND: a later operand lowered once, its labels kept; AMBIG
_m82 = m


def m(node, s, pos, st, k):                                  # noqa: F811
    t = node[0]
    if t == "andpat2":                                       # Q matched whole on P's stretch, its labels kept
        a = st.marks[node[1]]
        piece_ = s[a:pos]

        def fin(q, st2):
            if q != len(piece_):
                return None
            if s82("s3"):
                return k(pos, st)
            return k(pos, St(st2.lab, st2.log, st.marks, st2.seen))
        return m(node[2], piece_, 0, St(st.lab, st.log, {}, st.seen), fin)
    if t == "rep" and s82("s1"):
        _, sub, lo, hi, names, lazy = node
        return _m82(("rep", sub, lo, hi, names, not lazy), s, pos, st, k)
    return _m82(node, s, pos, st, k)


_p_atom82 = p_atom


def p_atom(p):                                               # noqa: F811
    if p.peek() == "(" and p.s.startswith("?&", p.i + 1):
        p.take()
        j = p.s.index(":", p.i)
        mk = p.s[p.i + 2:j]
        p.i = j + 1
        n = ("andpat2", mk, p_alt(p))
        assert p.take() == ")"
        return n
    return _p_atom82(p)


def surfaced(text, scope):
    out = set()
    for g in GROUP_NAME.findall(text):
        for base, sc in parts_of(g):
            if scope in sc:
                out.add(base)
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES.get(int(n))
        if nd and nd[0] == "setv":
            for base, sc in parts_of(nd[1]):
                if scope in sc:
                    out.add(base)
    return out


def lower_and(parts, ctx):                                   # noqa: F811
    pats = [x for x in parts if not (IS_COND.match(x) or is_gq(x) or (x in BINDS and IS_COND.match(BINDS[x])))]
    rest = [x for x in parts if x not in pats]
    mk = fresh("k")
    sub = ctx.sub()
    texts = ["(?:%s)" % lower(q, sub) for q in pats]
    out = node_ref(("mark", mk)) + texts[0]
    for tq in texts[1:]:
        out += "(?&%s:%s)" % (mk, tq)                     # parsed by p_atom below into ("andpat2", mk, node)
    seen, amb = {}, set()
    for tq in texts:
        for nm in surfaced(tq, ctx.cur):
            seen[nm] = seen.get(nm, 0) + 1
    amb = set(n for n, c in seen.items() if c > 1)
    uses_by_op = {}
    for q in pats:
        for nm in text_uses(q):
            uses_by_op[nm] = uses_by_op.get(nm, 0) + 1
    for nm, c in uses_by_op.items():
        if c > 1:
            AND_JOINED.add((ctx.cur, nm))
    for c in rest:
        if c in BINDS:
            c = BINDS[c]
        a = len(NAMED)
        if is_gq(c):
            out += lower_gq(c, sub)
            continue
        out += lower_cond(c, ctx, zero_key=mk)
        if s82("s4"):
            continue
        for sc, nm in NAMED[a:]:
            head = nm.split(".")[0]
            if sc == ctx.cur and nm in amb and not ("." in nm and USES.get((ctx.cur, head), 0) > 1):
                raise CompileError("`%s`: both sides of `&` surface it, an ambiguous reference (core/labels/flow)"
                                   % nm)
    return out


# ---- USES at the reference: binding-prefix part 2 by the text count
def plain_prefix_check(scope, start):                        # noqa: F811
    for i in range(start, len(NAMED)):
        sc, nm = NAMED[i]
        if sc != scope or "." not in nm or i in GQ_IDX:
            continue
        pre = nm.split(".")[0]
        if USES.get((scope, pre), 0) > 1:
            raise CompileError("`%s`: %s is used %d times here; label the part (`[left = %s]`) to read one use"
                               % (nm, pre, USES[(scope, pre)], pre))


# ---- INDEX on a path; VALUEGQ
IDX = re.compile(r"(NOT )?\(([\w.]+)\[(\d+)\]: (.*)\)")
_lower_gq82 = lower_gq


def is_gq(text):                                             # noqa: F811
    return bool(GQ.match(text) or IDX.fullmatch(text))


def lower_gq(text, ctx):                                     # noqa: F811
    mm = IDX.fullmatch(text)
    if mm:
        neg, name, k, v = bool(mm.group(1)), mm.group(2), int(mm.group(3)), parse_value(mm.group(4), ctx)
        head = name.split(".")[0]
        if "." in name and (ctx.cur, head) in AND_JOINED and not s82("s9"):
            raise CompileError("`%s[%d]`: the uses of %s are joined by `&`, which are not ordered (an index there is a "
                               "compile error for now)" % (name, k, head))
        a = len(NAMED)
        NAMED.append((ctx.cur, name))
        GQ_IDX.update(range(a, len(NAMED)))
        sc = array_scope(ctx)
        return node_ref(("gq", "index", neg, "%s@%s" % (name, sc), sc, v, k, False))
    g = GQ.match(text)
    if g and not s82("s10"):
        arg = g.group(3).strip()
        if arg.startswith("NOT "):
            arg = arg[4:].strip()
        for ent in split_top(arg[1:-1], ","):
            lr = split_colon(ent.strip())
            if lr and not LABEL_LEFT.fullmatch(lr[0]) and lr[0] != "0" and not lr[0].startswith("("):
                raise CompileError("a value entry `%s` inside a group question (a compile error for now)" % lr[0])
            if lr and lr[0].startswith("(") and strip_parens(lr[0]) != lr[0] and len(split_top(lr[0][1:-1], ",")) == 1:
                raise CompileError("a value entry `%s` inside a group question (a compile error for now)" % lr[0])
    if g and s82("s10"):                                     # the plant: the value read once, as a label would be
        arg = g.group(3).strip()
        mm2 = re.fullmatch(r"\(\$(\w+): (.*)\)", arg)
        if mm2:
            return _lower_gq82("%s((%s: %s))" % (g.group(2), mm2.group(1), mm2.group(2)), ctx)
    return _lower_gq82(text, ctx)


# ---- the top-level program: uses by its text; the path check reads the parts emitted
_prog_paths = OLD_ENGINE["prog"]


def prog(expr, binds=(), **opts):                            # noqa: F811
    base_binds()
    OPT.clear()
    OPT.update(opts)
    for b in binds:
        define(b)
    for b in binds:
        r = binding_check(b)
        if r:
            raise CompileError("at the binding `%s`: %s" % (b, r))
    CLOSED_PARTS.clear()
    PART_KIND.clear()
    AND_JOINED.clear()
    top = Ctx()
    start = len(NAMED)
    set_uses("top", expr)
    text = lower(expr, top)
    plain_prefix_check("top", start)
    source_check("top", start, expr)
    emitted = set()
    for g in GROUP_NAME.findall(text):
        for base, sc in parts_of(g):
            if "top" in sc:
                emitted.add(base)
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES.get(int(n))
        if nd and nd[0] == "setv":
            emitted |= set(b for b, sc in parts_of(nd[1]) if "top" in sc)
    for sc, nm in NAMED[start:]:
        if sc == "top" and "." in nm and nm.split(".")[0] not in top.held:
            raise CompileError("`%s`: no part label or used binding `%s` here" % (nm, nm.split(".")[0]))
        if sc == "top" and "." in nm and nm not in emitted:
            raise CompileError("`%s`: `%s` is not visible through `%s` (a compile error, core/labels/paths)"
                               % (nm, nm.split(".", 1)[1], nm.split(".")[0]))
    Pg = Prog(text)
    Pg.expr = expr
    return Pg


def binding_check(line):                                     # noqa: F811
    """DES-1, the manager's reading: every label a binding's body names has its target in that binding; a SET
    that reads a label (`<(10 - $b)`) bound alone is the same compile error (the loaded check exempted every set)."""
    name, heads, body = HEADS[line]
    if heads is None and is_set_body(body):
        return None
    if heads is None and re.match(r"(>=|<=|<|>|==)", body.strip()) and "$" in body and not s82("s12"):
        lab = re.findall(r"\$([\w.]+)", body)
        return "%s is a set that reads %s, which has no target in it" % (name, ", ".join("`%s`" % x for x in lab))
    params = {h: ("//", Ctx()) for h, _ in (heads or [])}
    keep = len(NAMED)
    try:
        use_definition(body, Ctx(), name, params)
        return None
    except CompileError as e:
        return str(e)
    finally:
        del NAMED[keep:]


# ---- DES-3, the manager's readings: three parse gaps left of `:` are compile errors for now; s7 (MUTA)
_lower_cond82 = lower_cond


def lefts_of(text):
    t = text.strip()
    if t.startswith("NOT "):
        t = t[4:].strip()
    out = []
    for e in split_top(t[1:-1], ","):
        lr = split_colon(e.strip())
        if lr:
            out.append(lr[0])
    return out


def lower_cond(text, ctx, zero_key=None):                    # noqa: F811
    if not TUPLE.fullmatch(text.strip()):
        named = []
        for left in lefts_of(text):
            if LABEL_LEFT.fullmatch(left) or left == "0":
                named.append(left)
                continue
            comps = split_top(left[1:-1], ",") if left.startswith("(") and strip_parens(left) != left else [left]
            for c in comps:
                if LABEL_LEFT.fullmatch(c):
                    named.append(c)
                    continue
                v = strip_parens(c)
                if len(top_split(v, (" | ", " & "))) > 1 and not s82("s19"):
                    raise CompileError("`%s`: `|` or `&` inside a value left of `:` (a compile error for now)" % c)
                bare = re.sub(r'"[^"]*"|\$[\w.]+|count\(.*\)|\b\d+\b', " ", v)
                if re.search(r"[A-Za-z_]\w*", bare):
                    raise CompileError("`%s`: a bare name inside a value left of `:` (a compile error for now)" % c)
                named += re.findall(r"\$([\w.]+)", v)
        dup = sorted(set(n for n in named if named.count(n) > 1 and n != "0"))
        if dup:
            raise CompileError("a label named twice in one condition: %s" % ", ".join(dup))
    r = _lower_cond82(text, ctx, zero_key)
    if s82("s7"):                                            # MUTA: a path `X.h` read as the bare last mention
        n = int(re.search(r"\$\{#(\d+)\}", r).group(1))
        nd = NODES[n]
        if nd[0] == "cond":
            ents = [((("lab", "%s@%s" % (k[1].split("@")[0].split(".")[-1], k[1].split("@")[1])) if k[0] == "lab"
                      else k), v) for k, v in nd[2]]
            NODES[n] = ("cond", nd[1], ents)
    return r


RUN = []                                                     # every program a check runs (NULLABLE reads it)
_prog82 = prog


def prog(expr, binds=(), **opts):                            # noqa: F811
    Pg = _prog82(expr, binds, **opts)
    RUN.append((expr, tuple(binds), Pg.node))
    return Pg


if s82("s5"):                                                # plant: predcall's ARG-COUNT off too
    use_param = _use_param2                                   # noqa: F811
if ENGINE == "old":
    globals().update(OLD_ENGINE)


# ================================================================== the sweep (SWEEP; also the old engine's table)
LIBDEF = {"chars": "chars := " + CHARS}


def sweep_lines():
    """(file, line no, line, answer, program, tail) of every printed three-mode line of the six documents."""
    out = []
    for f in ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"):
        for ln, line in enumerate(NEW[f].split("\n"), 1):
            if "WHOLE " not in line or " / FIND-ALL " not in line:
                continue
            a = answer_part(line)
            if not a:
                continue
            tail = line[line.index(a) + len(a):]
            mm = re.search(r"`([^`]*)`", tail)
            if mm:
                out.append((f, ln, line, a, mm.group(1), tail))
    return out


def sweep_one(line, a, pt, tail):
    """(status, what it printed): same | DIFF | REFUSED | CRASH | unparsed, with the program's own bindings."""
    binds = ["%s := %s" % (h, b) for h, b in re.findall(r"([\w.]+(?:\([\w, =]*\))?) := `([^`]*)`", tail)]
    expr = pt
    mm = re.fullmatch(r"([\w.]+(?:\([\w, ]*\))?) := (.*)", pt)
    if mm:
        binds, expr = [pt] + binds, mm.group(1)
    for nm, df in LIBDEF.items():
        if re.search(r"\b%s\b" % nm, expr + " ".join(binds)) and not any(b.startswith(nm + " :=") for b in binds):
            binds.append(df)
    try:
        wh, sr, fa = modes_of(line)
    except Exception:                                        # noqa: BLE001  (a line the parser cannot split)
        return "unparsed", ""
    try:
        got = fmt(prog(expr, binds), wh, sr, fa)
        return ("same" if got == strip_annot(a) else "DIFF"), got
    except CompileError as e:
        return "REFUSED", str(e)
    except Exception as e:                                   # noqa: BLE001  (an unmodelled construct)
        return "CRASH", type(e).__name__


if ENGINE == "old":
    for f, ln, line, a, pt, tail in sweep_lines():
        st, got = sweep_one(line, a, pt, tail)
        print("SW\t%s\t%d\t%s\t%s" % (f, ln, st, got if st in ("same", "DIFF") else ""))
    sys.exit(0)

# ================================================================== the checks
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def ref(expr, binds=()):
    try:
        prog(expr, binds)
        return None
    except CompileError as e:
        return str(e)


def wdiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t)) if Pg is not None else -1


def line(label, expr, binds_txt, Pg, wh, sr, fa, tag, tail=""):
    L = "%s: %s (`%s`%s)%s" % (label, fmt(Pg, wh, sr, fa), expr, binds_txt, tail)
    return doc_line(L, tag)


def dz(x):
    return "`%s`" % x


print("== CONTROL: the loaded matcher against python `re`; a later `&` operand matched on the stretch")
POPA = pop("ab;7", 4)
c1 = ndiff(answers(prog('"ab" | "a"'), POPA), answers(Re(r"ab|a"), POPA))
POP12 = pop("12a", 4)
c2 = ndiff(answers(prog("/\\d\\d/ & /1\\d/"), POP12), answers(Re(r"1\d"), POP12))
c3 = ndiff(answers(prog("/\\d+/ & /\\d*1/"), POP12), answers(Re(r"\d*1(?<=\d)"), POP12))
check("CONTROL", (c1, c2, c3) == ((0, 0, 0),) * 3, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s over %d "
      "texts; `/\\d\\d/ & /1\\d/` against `1\\d` %s, `/\\d+/ & /\\d*1/` against `\\d*1(?<=\\d)` %s over %d texts"
      % (c1, len(POPA), c2, c3, len(POP12)))

print("== ORDER: quantifier order (the order that carries meaning); the label against python `re`'s group")
P_or = prog("/(?<h>\\d+)\\d*/")
P_lz = prog("/(?<h>\\d+?)\\d*/")
POPO = pop("12a", 4)
lab = [0, 0]
for i, (Pg, rx) in enumerate([(P_or, r"(\d+)\d*"), (P_lz, r"(\d+?)\d*")]):
    for t in POPO:
        mm = re.fullmatch(rx, t)
        st = whole_state(Pg, t)
        if (mm is None) != (st is None) or (mm and st.lab.get("h@top") != mm.group(1)):
            lab[i] += 1
do = ndiff(answers(P_or, POPO), answers(Re(r"(\d+)\d*"), POPO))
dl = ndiff(answers(P_lz, POPO), answers(Re(r"(\d+?)\d*"), POPO))
check("ORDER", lab == [0, 0] and do == (0, 0, 0) and dl == (0, 0, 0),
      "the label h on the first whole path against python `re`'s group 1: greedy `(?<h>\\d+)\\d*` %d, lazy "
      "`(?<h>\\d+?)\\d*` %d differing; the three modes %s, %s, over %d texts" % (lab[0], lab[1], do, dl, len(POPO)))

print("== CLOSEDX: closed-argument's `_x` half, export statements 6 and 7 (EVID-2)")
A1 = "A := /(?<d>\\d)/"
CX = [A1, "B(rx) := /${[_p = rx]}xx/"]
r1, r2, r3 = ref("B(A) & (A.d: <5)", CX), ref("[c = B(A)] & (c.d: <5)", CX), ref("B(A) & (B.d: <5)", CX)
cx_ctl = ndiff(answers(prog("B(A)", CX), pop("3x", 4)), answers(Re(r"\dxx"), pop("3x", 4)))
AH = "A := /(?<h>\\d)/"
P6 = ["p6 := [_a = A] SEQ \"!\" & (_a.h: <5)", AH]
P_6 = safe_prog("p6", P6)
w6 = wdiff(P_6, lambda t: re.fullmatch(r"[0-4]!", t) is not None, pop("37!", 3))
r6 = ref("p6 & (p6.h: <5)", P6)
r7 = ref("pub & (pub.h: <5)", ["pub := [_a = A] SEQ \"!\"", AH])
L6 = None
if P_6:
    L6 = line("Statement 6, inside its binding", "p6", ", p6 := `[_a = A] SEQ \"!\" & (_a.h: <5)`, A := `/(?<h>\\d)/`",
              P_6, ["3!", "7!"], "7! 3!", "3! 7! 4!", "core/labels/export",
              "; outside it `p6 & (p6.h: <5)` is a compile error")
    print("   " + L6)
for x, r in [("B(A) & (A.d: <5)", r1), ("[c = B(A)] & (c.d: <5)", r2), ("B(A) & (B.d: <5)", r3),
             ("p6 & (p6.h: <5)", r6), ("pub & (pub.h: <5), pub := [_a = A] SEQ \"!\"", r7)]:
    print("   `%s`: %s" % (x, r))
check("CLOSEDX", all((r1, r2, r3, r6, r7)) and cx_ctl == (0, 0, 0) and w6 == 0,
      "under B(rx) := `/${[_p = rx]}xx/`: `A.d` %s, `c.d` %s, `B.d` %s (the call itself matching as `\\dxx`: %s "
      "differing); inside its binding `(_a.h: <5)` legal, WHOLE against the direct \"a digit under 5, then !\" %d "
      "differing; outside, `p6.h` %s and `pub.h` through `[_a = A]` %s"
      % tuple(["refused" if r else "ACCEPTED" for r in (r1, r2, r3)] + [cx_ctl, w6] +
              ["refused" if r else "ACCEPTED" for r in (r6, r7)]))

print("== SECOND: a binding as the second `&` operand (EVID-3), binding-prefix's second-operand arm")
AB = ["A := /(?<h>\\d)\\d/", "B := /\\d(?<h>\\d)/"]
ABT = ", A := `/(?<h>\\d)\\d/`, B := `/\\d(?<h>\\d)/`"
P_s1 = safe_prog("A & B & (A.h: <2)", AB)
P_s2 = safe_prog("A & B & (B.h: <2)", AB)
P_cc = safe_prog("A & A & (count((A.h: \"1\")): ==2)", AB)
POPS = pop("123", 3)
w1 = wdiff(P_s1, lambda t: len(t) == 2 and t.isdigit() and int(t[0]) < 2, POPS)
w2 = wdiff(P_s2, lambda t: len(t) == 2 and t.isdigit() and int(t[1]) < 2, POPS)
wc = wdiff(P_cc, lambda t: len(t) == 2 and t.isdigit() and t[0] == "1", POPS)
r_tw = ref("A & A & (A.h: <2)", AB)
L_s1 = L_s2 = None
if P_s1:
    L_s1 = line("One use", "A & B & (A.h: <2)", ABT, P_s1, ["12", "21"], "21 12", "12 21 10", "binding-prefix")
if P_s2:
    L_s2 = line("One use, the second operand", "A & B & (B.h: <2)", ABT, P_s2, ["12", "21"], "21 12", "12 21 10",
                "binding-prefix")
    print("   " + L_s2)
print("   `A & A & (A.h: <2)`: %s" % r_tw)
check("SECOND", None not in (P_s1, P_s2, P_cc) and (w1, w2, wc) == (0, 0, 0) and r_tw and "used 2 times" in r_tw,
      "`A.h` as the first operand %d, `B.h` as the second %d, `count((A.h: \"1\")): ==2` over `A & A` %d differing "
      "from the direct reads over %d texts; `A & A` counts 2 uses: %s"
      % (w1, w2, wc, len(POPS), "yes" if r_tw and "used 2 times" in r_tw else "NO (%s)" % r_tw))

print("== AMBIG: flow, a name both sides of `&` surface: a plain read refused, a group question legal")
E_amb = "/(?<h>\\d)\\d/ & /\\d(?<h>\\d)/"
ra, rd = ref(E_amb + " & (h: <2)"), ref(E_amb + " & ($h: <2)")
P_ag = safe_prog(E_amb + " & some((h: \"1\"))")
wag = wdiff(P_ag, lambda t: len(t) == 2 and t.isdigit() and "1" in t, POPS)
L_ag = None
if P_ag:
    L_ag = line("Across `&`, a group question over both sides", E_amb + " & some((h: \"1\"))", "", P_ag,
                ["12", "21", "33"], "33 21", "12 33 31", "core/labels/flow",
                "; the plain read `%s & (h: <2)` is a compile error" % E_amb)
    print("   " + L_ag)
print("   plain: %s ; `$h`: %s" % (ra, rd))
check("AMBIG", ra and rd and "ambiguous" in ra and "ambiguous" in rd and wag == 0,
      "the plain read %s, the `$h` read %s, by flow's ambiguity rule; `some((h: \"1\"))` against the direct \"either "
      "digit is 1\" %d differing over %d texts" % ("refused" if ra else "ACCEPTED", "refused" if rd else "ACCEPTED",
                                                 wag, len(POPS)))

print("== TEXTUSES: uses counted in the referencing definition's text, before macros expand (ANS-2d)")
PB2 = [A1, "pair(p) := /${p},${p}/"]
P_pa = safe_prog("pair(A) & (A.d: <5)", PB2)
r_tt = ref("/${A},${A}/ & (A.d: <5)", [A1])
wpa = wdiff(P_pa, lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[2]) < 5, pop("37,", 3))
print("   `/${A},${A}/ & (A.d: <5)`: %s" % r_tt)
check("TEXTUSES", P_pa is not None and wpa == 0 and r_tt and "used 2 times" in r_tt,
      "`pair(A) & (A.d: <5)` (A written once, lowered twice) %s, WHOLE against the direct second digit %d differing; "
      "`/${A},${A}/ & (A.d: <5)` (written twice) %s" % ("legal" if P_pa else "REFUSED", wpa,
                                                         "refused, 2 uses" if r_tt else "ACCEPTED"))

print("== NESTED: the prefix reaches the uses written in the referencing definition's own text (ANS-2c)")
NB = ["D := /(?<h>\\d)+/", "X := D SEQ \"!\""]
NBT = ", D := `/(?<h>\\d)+/`, X := `D SEQ \"!\"`"
E_n = "D SEQ \";\" SEQ X & (D.h: \"4\")"
P_n = safe_prog(E_n, NB)
P_nl = prog("[left = D] SEQ \";\" SEQ X & (left.h: \"4\")", NB)
P_nx = safe_prog("D SEQ \";\" SEQ X & (X.D.h: \"4\")", NB)
P_nxl = prog("D SEQ \";\" SEQ [x = D] SEQ \"!\" & (x.h: \"4\")", NB)
POPN = pop("14;!", 6)
dn = safe_ndiff(P_n, P_nl, POPN)
dx = safe_ndiff(P_nx, P_nxl, POPN)
L_n = None
if P_n:
    L_n = line("A use inside another used binding", E_n, NBT, P_n, ["14;23!", "12;34!"], "12;34! 14;2!",
               "14;23! 12;34! 4;1!", "binding-prefix", "; `D.h` reads the use written here, not X's")
    print("   " + L_n)
check("NESTED", dn == (0, 0, 0) and dx == (0, 0, 0),
      "`D.h` against `[left = D] ... & (left.h: ..)` %s; the nested path `X.D.h` against `[x = D]` written in X's place "
      "%s, over %d texts" % (dn, dx, len(POPN)))

print("== CONTRAST: a prefix read and the bare last mention differ (EVID-5)")
E_c = "A SEQ B & (A.h: \"2\")"
P_c = safe_prog(E_c, AB)
P_cb = prog("/(?<h>\\d)\\d/ SEQ /\\d(?<h>\\d)/ & (h: \"2\")")
CW, CSr, CF = ["2219", "1222", "1229"], "x2219", "2219 1222 2212"
POPC = pop("129", 4)
wc1 = wdiff(P_c, lambda t: len(t) == 4 and t.isdigit() and t[0] == "2", POPC)
wc2 = wdiff(P_cb, lambda t: len(t) == 4 and t.isdigit() and t[3] == "2", POPC)
differ = sum(1 for t in POPC if P_c and P_c.whole(t) != P_cb.whole(t))
L_c = L_cb = None
if P_c:
    L_c = line("A prefix and the last mention differ", E_c, ABT, P_c, CW, CSr, CF, "binding-prefix")
    L_cb = line("the bare last mention, written in place", "/(?<h>\\d)\\d/ SEQ /\\d(?<h>\\d)/ & (h: \"2\")", "",
                P_cb, CW, CSr, CF, "binding-prefix")
    print("   " + L_c)
    print("   " + L_cb)
check("CONTRAST", wc1 == 0 and wc2 == 0 and differ > 0,
      "`A.h` against the direct first digit %d differing, the bare last mention against the direct last digit %d "
      "differing, the two reads part on %d of %d texts" % (wc1, wc2, differ, len(POPC)))

print("== PATHS: a source is a path of names, each step passed by the previous one (ANS-5); the tier (ANS-4)")
PUB = ["pub := [a = A] SEQ \"!\"", AH]
P_pa1 = safe_prog("pub & (pub.a.h: <5)", PUB)
P_pa0 = prog("pub & (pub.h: <5)", PUB)
d_pub = safe_ndiff(P_pa1, P_pa0, pop("37!", 4))
PAIR = ["pair := [b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]"]
P_bx = safe_prog("pair & (pair.b.x: <5)", PAIR)
w_bx = wdiff(P_bx, lambda t: re.fullmatch(r"[0-4]", t) is not None, pop("a37", 3))
DAYS = ["days := [w = [/Mon/, /Tue/, /Wed/]]"]
P_dw = safe_prog("/${days}/ & (days.w.index: >= 2)", DAYS)
CPB = [A1, "B(rx) := /${rx}-(?<d>\\d)/"]
r_ca = ref("[c = B(A)] & (c.A.d: <5)", CPB)
r_ty = ref("[c = B(A)] & (c.e: <5)", CPB)
r_nv = ref("B(A) & (A.d: <5)", CX)
L_bx = L_dw = None
if P_bx:
    L_bx = line("Through a part label inside the binding", "pair & (pair.b.x: <5)",
                ", pair := `[b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]`", P_bx, ["3", "a3", "7"], "a3 7 3", "3 a3 4 a4",
                "flat-read-outside")
    print("   " + L_bx)
if P_dw:
    L_dw = doc_line("WHOLE `Tue` HOLDS, `Mon` FAILS / SEARCHED `Mon Wed` `Wed`@4 / FIND-ALL `Tue Mon Wed` [`Tue`@0, `Wed`@8] "
                    "(`/${days}/ & (days.w.index: >= 2)`, days := `[w = [/Mon/, /Tue/, /Wed/]]`)", "metadata")
    ok_dw = fmt(P_dw, ["Tue", "Mon"], "Mon Wed", "Tue Mon Wed") in L_dw
else:
    ok_dw = False
print("   `c.A.d`: %s ; typo'd `c.e`: %s ; closed `A.d`: %s" % (r_ca, r_ty, r_nv))
check("PATHS", P_pa1 is not None and d_pub == (0, 0, 0) and P_bx is not None and w_bx == 0 and ok_dw
      and r_ca and r_ty and r_nv and all("not visible" in r for r in (r_ca, r_ty, r_nv)),
      "`pub.a.h` %s, against `pub.h` %s; `pair.b.x` %s, WHOLE against the direct \"a digit under 5 by b\" %d differing; "
      "`days.w.index` %s; a label not visible through its source is a compile error: `c.A.d` %s, the typo `c.e` %s, "
      "`A.d` under a closing B %s" % ("legal" if P_pa1 else "REFUSED", d_pub, "legal" if P_bx else "REFUSED", w_bx,
                                      "reproduces the printed line" if ok_dw else "DIFFERS",
                                      *["refused" if r else "ACCEPTED" for r in (r_ca, r_ty, r_nv)]))

print("== INDEX: `x.h[k]` through a path; `&`-joined uses refused, sequenced uses in text order (ANS-6)")
AI = ["A := /(?<h>\\d),/"]
P_i = safe_prog("A SEQ A & (A.h[2]: \"3\")", AI)
wi = wdiff(P_i, lambda t: re.fullmatch(r"\d,3,", t) is not None, pop("37,", 4))
P_il = safe_prog("[aa = /(?:(?<h>\\d);)+/] & (aa.h[2]: \"5\")")
wil = wdiff(P_il, lambda t: re.fullmatch(r"(?:\d;)+", t) is not None and len(t) >= 4 and t[2] == "5", pop("35;", 6))
r_ia = ref("A & A & (A.h[2]: \"3\")", ["A := /(?<h>\\d)/"])
L_i = None
if P_i:
    L_i = line("The index through sequenced uses", "A SEQ A & (A.h[2]: \"3\")", ", A := `/(?<h>\\d),/`", P_i,
               ["7,3,", "3,7,"], "x7,3,", "7,3, 3,7, 1,3,", "binding-prefix",
               "; through `&`-joined uses, `A & A & (A.h[2]: \"3\")`, a compile error")
    print("   " + L_i)
print("   `A & A & (A.h[2]: \"3\")`: %s" % r_ia)
check("INDEX", P_i is not None and wi == 0 and P_il is not None and wil == 0 and r_ia and "joined by `&`" in r_ia,
      "`A.h[2]` through `A SEQ A` %d differing from the direct second use's digit; `aa.h[2]` through a part label %d "
      "differing; through `A & A` %s" % (wi, wil, "refused" if r_ia else "ACCEPTED"))

print("== VALUEGQ: a value entry inside a group question is a compile error for now (ANS-3)")
LL = "/(?<h>\\d);(?:(?<h>\\d);)*/"
rv1 = ref(LL + " & some(($h: \"7\"))")
rv2 = ref("/(?<a>\\d)\\+(?<b>\\d)/ & count((($a + $b): <10))")
P_v0 = prog(LL + " & some((h: \"7\"))")
P_v1 = prog(LL + " & ($h: \"7\")")
P_v2 = prog(LL + " & (h: \"7\")")
part = P_v0.whole("7;1;") and not P_v1.whole("7;1;")
dv = ndiff(answers(P_v1, pop("71;", 4)), answers(P_v2, pop("71;", 4)))
print("   `some(($h: \"7\"))`: %s ; `count((($a + $b): <10))`: %s" % (rv1, rv2))
check("VALUEGQ", rv1 and rv2 and part and dv == (0, 0, 0),
      "`some(($h: \"7\"))` %s, `count((($a + $b): <10))` %s; on `7;1;` `some((h: \"7\"))` HOLDS and `($h: \"7\")` "
      "FAILS: %s; outside a group question `($h: S)` against `(h: S)` %s over %d texts"
      % ("refused" if rv1 else "ACCEPTED", "refused" if rv2 else "ACCEPTED", "yes" if part else "NO", dv,
         len(pop("71;", 4))))

print("== HIDE: a part label named like a provided macro wins, with the hide-label warning (DES-6)")
E_h = "[hits = occurrences(/\\d+/)] & hits(/\\d/) & (hits.hit: <5)"
P_h = safe_prog(E_h)
warned = ("hide-label", "hits") in WARNINGS
P_hq = prog("[q = occurrences(/\\d+/)] & hits(/\\d/) & (q.hit: <5)")
dh = safe_ndiff(P_h, P_hq, pop("19a", 4))
L_h = None
if P_h:
    L_h = line("A part label named like the macro", E_h, "", P_h, ["a1b3", "a3b9", "a12"], "x9 3", "a3 b9 c1",
               "call-prefix", "; the part label wins, with the hide-label warning")
    print("   " + L_h)
check("HIDE", P_h is not None and warned and dh == (0, 0, 0),
      "`%s` %s, the warning %s; against the same program with the part label renamed `q` %s" %
      (E_h, "legal" if P_h else "REFUSED", "drawn" if warned else "NOT drawn", dh))

print("== BOUNDSET: every label a binding's body names has its target in that binding; a SET reading a label (DES-1)")
BS = ["lim := <(10 - $b)"]
r_bs = ref("/(?<b>\\d)(?<h>\\d)/ & (h: lim)", BS)
P_bi = prog("/(?<b>\\d)(?<h>\\d)/ & (h: <(10 - $b))")
wbi = wdiff(P_bi, lambda t: len(t) == 2 and t.isdigit() and int(t[1]) < 10 - int(t[0]), pop("159", 2))
print("   bound alone: %s" % r_bs)
bs_rule = bool(r_bs) and "at the binding" in r_bs and "has no target" in r_bs
check("BOUNDSET", bs_rule and wbi == 0,
      "`lim := <(10 - $b)` bound alone %s; written in place, WHOLE against the direct h < 10 - b %d differing"
      % ("refused at the binding by the no-target rule" if bs_rule else "NOT refused by the no-target rule", wbi))

print("== GAPS: DES-3, three parse gaps left of `:`, each a compile error for now (readings)")
GP = [("/(?<n>\\d)/ & ((n + 1): <5)", "a bare name"), ("/(?<h>\\d)(?<m>\\d)/ & ((h | m): <5)", "`|`"),
      ("/(?<h>\\d)(?<m>\\d)/ & ((h & m): <5)", "`&`"),
      ("/(?<h>\\d)/ & ($h: <5, h: >2)", "named twice")]
gr = [(e, ref(e)) for e, _ in GP]
for e, r in gr:
    print("   `%s`: %s" % (e, r))
P_gok = prog("/(?<n>\\d)/ & (($n + 1): <5)")
wg = wdiff(P_gok, lambda t: len(t) == 1 and t.isdigit() and int(t) + 1 < 5, pop("0369", 1))
check("GAPS", all(r and w in r for (e, r), (_, w) in zip(gr, GP)) and wg == 0,
      "refused: %s; the legal `(($n + 1): <5)` %d differing from the direct" %
      (", ".join("%s %s" % (w, "yes" if r else "NO") for (e, r), (_, w) in zip(gr, GP)), wg))

print("== NULLABLE: EVID-4's limit: no program a check above runs has a nullable loop body")


def nullable(n):
    t = n[0]
    if t in ("lit", "cls", "dot"):
        return False
    if t == "seq":
        return all(nullable(x) for x in n[1])
    if t == "alt":
        return any(nullable(x) for x in n[1])
    if t in ("grp",):
        return nullable(n[2])
    if t == "rep":
        return n[2] == 0 or nullable(n[1])
    if t == "atomic":
        return nullable(n[1])
    if t == "andpat2":
        return True
    return True                                              # look, anchors, conditions, marks: zero width


def loops_nullable(n, out):
    t = n[0]
    if t == "rep" and (n[3] is None or n[3] > 1) and nullable(n[1]):
        out.append(n)
    for x in (n[1] if t in ("seq", "alt") else [n[2]] if t in ("grp", "andpat2") else
              [n[1]] if t in ("rep", "atomic", "look") else []):
        if isinstance(x, tuple):
            loops_nullable(x, out)
    return out


checked = list(RUN)
if s82("s15"):
    checked.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nl = [(e, b) for e, b, nd in checked if loops_nullable(nd, [])]
check("NULLABLE", not nl, "%d programs run by the checks above, walked node by node: %d with a loop whose body can "
      "match empty%s" % (len(checked), len(nl), (": %s" % nl[:4]) if nl else ""))
NCHECKED = len(checked)

print("== TWOSRC: the open two-sources question, both shapes, the run lines under each candidate (ANS-1)")
BB = "B(rx) := /${rx}-(?<d>\\d)/"
TS = [("(a) the label as it reaches the caller, an argument written in place", "B(/(?<d>\\d)/) & (d: <5)", [BB],
       ", B(rx) := `/${rx}-(?<d>\\d)/`", ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9",
       lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5),
      ("(b) the source written here, as spelled with a part label", "B([x = /(?<d>\\d)/]) & (x.d: <5)", [BB],
       ", B(rx) := `/${rx}-(?<d>\\d)/`", ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9",
       lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2 if s82("s20") else 0]) < 5),
      ("(a) the last mention, a name written here and surfaced by a used binding", "/(?<h>\\d)/ SEQ A & (h: <5)",
       ["A := /,(?<h>\\d)/"], ", A := `/,(?<h>\\d)/`", ["1,7", "7,1"], "7,1 1,7", "1,7 7,1 1,2 9,9",
       lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[2]) < 5),
      ("(b) the group written here, as spelled with a part label", "[w = /(?<h>\\d)/] SEQ A & (w.h: <5)",
       ["A := /,(?<h>\\d)/"], ", A := `/,(?<h>\\d)/`", ["1,7", "7,1"], "7,1 1,7", "1,7 7,1 1,2 9,9",
       lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[0]) < 5)]
ts_ok = []
for lab_, e, b, bt, wh, sr, fa, direct in TS:
    Pg = safe_prog(e, b)
    w = wdiff(Pg, direct, pop("37-,1", 3))
    ts_ok.append(Pg is not None and w == 0)
    if Pg:
        print("   " + line(lab_, e, bt, Pg, wh, sr, fa, "two-sources"))
P_own = prog("B(A) & (A.d: <5)", [A1, BB])
d_own = ndiff(answers(P_own, pop("37-", 4)), answers(prog(TS[1][1], [BB]), pop("37-", 4)))
check("TWOSRC", all(ts_ok) and d_own == (0, 0, 0),
      "the four candidate lines legal and each against its direct read (first or second digit): %s; the printed "
      "`B(A) & (A.d: <5)` (A's own `d`) against candidate (b)'s spelling %s" % (ts_ok, d_own))

print("== REPRINT: printed lines the earlier models owned, re-derived on the fixed engine (their successors)")
REPRINT = [
    ("metadata", "/${days}/ & (days.w.index: >= 2)", DAYS, ["Tue", "Mon"], "Mon Wed", "Tue Mon Wed"),
    ("zero-binding (a)", "/\\d${c}x/", ["c := (0: rx.digit)"], ["7x", "77x"], "a7x", "7x 12x 8x"),
    ("bare-condition/labels", "A SEQ B", ["A := /(?<c>\\d)/", "B := /${(c: >= 5)}(?<c>\\d)/"], ["73", "37"],
     "37 73", "73 37 51"),
    ("flat-read-outside |", "pair & (pair.x: <5)", PAIR, ["3", "a3", "a7"], "a7 a3", "3 a7 a4"),
    ("flat-read-outside SEQ", "date & (date.v: <5)", ["date := [y = /(?<v>\\d)/] SEQ \"-\" SEQ [m = /(?<v>\\d)/]"],
     ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2"),
    ("nested-scope ex. 1", "C", ["C := B(A) & (A.d: <100)", "A := [d = rx.digits]", "B(rx) := /${rx}xx/"],
     ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx"),
    ("nested-scope ex. 3", "B(A)", ["A := [d = rx.digits]", "B(rx) := /${[dd = rx]}xx/ & (dd: <100)"],
     ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx"),
    ("array-in-piece bound first", "A SEQ B", ["A := /(?<h>\\d)/", "B := /(?:;(?<h>\\d))*${some((h: \"7\"))}/"],
     ["7", "7;1", "1;7", "1;2"], "x7;1 1;7", "7;1 1;7 3;4 7 2;7;5"),
    ("array-in-piece in place", "A SEQ /(?:;(?<h>\\d))*${some((h: \"7\"))}/", ["A := /(?<h>\\d)/"],
     ["7", "7;1", "1;7", "1;2"], "x7;1 1;7", "7;1 1;7 3;4 7 2;7;5"),
    ("array-scope in an & operand", "/(?<h>\\d)${/(?:;(?<h>\\d))*/ & some((h: \"7\"))}/", [],
     ["7", "7;1", "1;7", "1;2"], "x7;1 1;7", "7;1 1;7 3;4 7 2;7;5"),
    ("computed-labels in a set", "/(?<a>\\d)\\+(?<b>\\d)/ & (a: <(10 - $b))", [], ["3+4", "7+8"], "7+8 2+2",
     "1+1 9+9 5+4"),
]
rp = []
for nm, e, b, wh, sr, fa in REPRINT:
    Pg = safe_prog(e, b)
    got = fmt(Pg, wh, sr, fa) if Pg else "REFUSED"
    shown = "C := B(A) & (A.d: <100)" if e == "C" else e
    hit = got != "REFUSED" and ("%s (`%s`" % (got, shown)) in ws(ALLDOC)
    rp.append((nm, hit))
    print("   %-28s %s %s" % (nm, "printed" if hit else "NOT FOUND:", "" if hit else got[:150]))
P_zs = safe_prog("/\\d${c}x/", ["c := (0: rx.digit)"], zero_bound="sealed")
zs = P_zs is not None and ("(c) sealed, its own `0`: %s (the same program)" % fmt(P_zs, ["7x", "77x"], "a7x",
                                                                                  "7x 12x 8x")) in ALLDOC
rp.append(("zero-binding (c)", zs))
cl100 = sum(1 for a_ in range(10) for b_ in range(10)
            if prog("/(?<a>\\d)\\+(?<b>\\d)/ & (a: <(10 - $b))").whole("%d+%d" % (a_, b_))
            != prog("/(?<a>\\d)\\+(?<b>\\d)/ & (($a + $b): %s10)" % ("<=" if s82("s21") else "<"))
            .whole("%d+%d" % (a_, b_)))
check("REPRINT", all(h for _, h in rp) and cl100 == 0,
      "%d of %d re-derived lines found verbatim in the documents (missing: %s); the set form against value-left's "
      "`(($a + $b): <10)` on the 100 digit pairs: %d differ" % (sum(1 for _, h in rp if h), len(rp),
                                                               [n for n, h in rp if not h] or "none", cl100))

print("== SUCCESSOR: EVID-1, every earlier in-force model re-run; its LAST LINE read; each red declared superseded")
LANES = os.path.normpath(os.path.join(HERE2, ".."))
SUPERSEDED = {
    "predbound": {"DOC": "REPRINT: its two missing lines re-printed, zero-binding's sealed candidate re-lettered (c) "
                         "(RULING-4) and the metadata read re-spelled `days.w.index` (label-reference)"},
    "predref": {"SCAN": "VALUEGQ, BOUNDSET, REPRINT: its three new spans are this lane's fragments, the refused "
                        "group question `count((($a + $b): <10))`, the set `<(10 - $b)` and the prose `some((h: "
                        "\"7\"))`, none a bare read of a label from another definition",
                "MARKS": "predcall's MARKS (call-prefix ruled; predref looked for it still open)"},
    "predcall": {"SCAN": "VALUEGQ, BOUNDSET, REPRINT: the same three fragment spans as predref's SCAN",
                 "PREDREF": "SUCCESSOR (this check reads predref's last line itself; predcall expected MARKS only)"},
    "predfix77": {"TRACEBACK": "REPRINT and predbound's checks: its library-body reader asserts on `chars`'s body, "
                               "re-spelled with the label-only group by helper-captures; its engine is carried "
                               "unchanged in predbound, whose checks are green but DOC"},
    "predarr": {"TRACEBACK": "REPRINT (the array-in-piece lines) and predref's HITS: the same `chars` body reader"},
    "predscope": {"NAMES": "predbound's bound-condition checks: the 7 definitions it refuses are bound-condition's "
                           "ruled compile error (a computed label, a condition, an rx naming a label it lacks)",
                  "CLOSEDB": "REPRINT `bare-condition/labels`: the Composed line became \"Two definitions\" under "
                             "nested-scope (the definition reads its own settings only)",
                  "DOC": "REPRINT: flat-read-outside's lines re-spelled `pair.x`/`date.v`, nested-scope's and "
                         "bare-condition's lines re-spelled under label-reference and nested-scope"},
}
if s82("s13"):
    SUPERSEDED["predscope"].pop("CLOSEDB")
procs = {}
for mname in SUPERSEDED:
    env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and k != "PREDFIX82_ENGINE"}
    procs[mname] = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(LANES, mname + "_evidence",
                                                                               mname + "_model.py")],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
succ_ok = True
for mname, pr in procs.items():
    try:
        out, _ = pr.communicate(timeout=540)
    except subprocess.TimeoutExpired:
        pr.kill()
        out = "TIMEOUT"
    last = out.rstrip("\n").split("\n")[-1]
    mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
    if mm:
        reds = set(x.strip() for x in (mm.group(3) or "").split(",") if x.strip())
    else:
        reds = {"TRACEBACK"}
    undeclared = sorted(reds - set(SUPERSEDED[mname]))
    gone = sorted(set(SUPERSEDED[mname]) - reds)
    if undeclared:
        succ_ok = False
    print("   %-10s last line: %s" % (mname, last[:110]))
    for r in sorted(reds):
        print("      %s: %s" % (r, ("superseded by " + SUPERSEDED[mname][r]) if r in SUPERSEDED[mname]
                                    else "UNDECLARED"))
    if gone:
        print("      declared but green now: %s" % gone)
check("SUCCESSOR", succ_ok, "%d earlier models re-run, each last line read; every red declared superseded: %s" %
      (len(procs), "yes" if succ_ok else "NO"))

print("== SWEEP: every printed three-mode line run by the old engine and the fixed one; no printed answer moves")
envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
envo["PREDFIX82_ENGINE"] = "old"
oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                    env=envo, timeout=540).stdout
OLD_SW = {}
for l_ in oo.split("\n"):
    if l_.startswith("SW\t"):
        _, f_, ln_, st_, got_ = l_.split("\t", 4)
        OLD_SW[(f_, int(ln_))] = (st_, got_)
NEW_SW = {}
for f, ln, line_, a, pt, tail in sweep_lines():
    NEW_SW[(f, ln)] = sweep_one(line_, a, pt, tail)
if s82("s18"):
    k_ = next(k for k, v in NEW_SW.items() if v[0] == "same")
    NEW_SW[k_] = ("DIFF", "planted")
moved = [k for k in NEW_SW if OLD_SW.get(k, ("?",))[0] == "same" and NEW_SW[k][0] != "same"]
gained = [k for k in NEW_SW if OLD_SW.get(k, ("?",))[0] != "same" and NEW_SW[k][0] == "same"]
cnt = {}
for v in NEW_SW.values():
    cnt[v[0]] = cnt.get(v[0], 0) + 1
check("SWEEP", len(OLD_SW) == len(NEW_SW) and not moved,
      "%d printed lines (old engine %d); the fixed engine: %s; lines the old engine reproduced and the fixed one "
      "does not: %d %s; lines only the fixed engine reproduces: %d %s" %
      (len(NEW_SW), len(OLD_SW), ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(moved), moved[:4],
       len(gained), gained[:6]))

print("== QUOTES: every owner sentence this lane quotes occurs in the record; every record title it cites is one")
QQ = ["4. A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an "
      "expression",
      "binding in prefix: i like your read on this except that perhaps it does refer to all",
      "\"binding-prefix\" 1. yes. 2. i agree with your lean (a)",
      "occurences et al should only set labels not captures unless they are so declared.",
      "hits = occurences(...) ] & (hits.hit: <5)",
      "(h.hit: 3)",
      "[ c = B(A) ] does not allow c.A",
      "x has no references in the binding",
      "y has no target"]
TT = ["2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error",
      "2026-11-22 OWNER, on binding-prefix: \"i like your read on this except that perhaps it does refer to all\"",
      "2026-11-22 OWNER RULING — binding-prefix: 1 yes (a group question through a binding's prefix reads every use); "
      "2 a (a plain read through it, the binding used more than once, is a compile error)",
      "2026-11-22 OWNER, on bound-condition: \"the form A := (x: blah) has to be illegal\"; his read, a response asked "
      "for; two alternatives",
      "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner "
      "words)"]
if s82("s16"):
    QQ[1] = QQ[1].replace("perhaps", "surely")
q_miss = [q for q in QQ if ws(q) not in RECORD_WS or ws(q) not in ws(ALLDOC)]
heads = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_miss = [t for t in TT if not any(h.startswith(ws(t)) for h in heads)]
check("QUOTES", not q_miss and not t_miss, "%d quoted sentences in the record and the documents, missing: %s; %d "
      "record titles cited, not a title: %s" % (len(QQ), q_miss or "none", len(TT), t_miss or "none"))

print("== MARKS: each FIX-NOW disposition's text where it landed")
CORE, CD = NEW["core.md"], NEW["core_details.md"]
MK = [("ANS-1", CORE, "a name with two sources is open two-sources"),
      ("ANS-2a", CORE, "open idiom-confirm (core/labels/paths/one-use-read)"),
      ("ANS-2b", CORE, "as if a part label `[A = A]` for one use"),
      ("ANS-2c", CORE, "not a use nested inside another\n  used binding"),
      ("ANS-2d", CORE, "is counted in the TEXT of the definition the reference is written in, before macros expand"),
      ("ANS-3", CORE, "a value\n  entry there is a compile error for now"),
      ("ANS-4", CORE, "A path to a label NOT VISIBLE through its source is a compile error"),
      ("ANS-5", CORE, "a source is a path of names, each step passed by the previous one"),
      ("ANS-6", CORE, "through uses joined by `&` it is a\n  compile error for now"),
      ("EVID-1", CORE, "Closed by a `_` part label: modes: a compile error"),
      ("DES-1", CORE, "every label a binding's\n  body names has its target in that binding"),
      ("DES-2", CORE, "a provided body also writes the label-only group"),
      ("DES-3", CORE, "a bare name, a number or a label path is a label"),
      ("DES-6", CORE, "the part label's, with the hide-label warning"),
      ("RULING-3", CORE, "from a typed parameter the source is not ruled"),
      ("RULING-4", CORE, "or sealed and legal, its own `0` (c)?"),
      ("RULING-5", CORE, "bound alone it is bound-condition's compile error"),
      ("RULING-8a", CD, "was written before label-reference was ruled)"),
      ("RULING-9", CORE, "a reading taken on his silence; open idiom-confirm"),
      ("GENERAL-5", CORE, "one naming only `0`\n  is open"),
      ("GENERAL-7", NEW["library.md"], "only the index `h[k]` across `&` is refused for now"),
      ("GENERAL-8", CORE, "may also stand in a set, written in place"),
      ("GENERAL-11", NEW["parked.md"], "which supersedes this entry"),
      ("FIXIND-1", NEW["parked_details.md"], "Revised by binding-prefix (2026-11-22)"),
      ("FIXIND-2", NEW["library_details.md"], "— by owner ruling — helper-captures (b)"),
      ("FIXIND-3", CD, "(as printed before label-reference; today `time & ((time.h, time.m): >= (9, 30))`"),
      ("FIXIND-4", CD, "Its refusal of the bare read is revived by label-reference"),
      ("FIXIND-5", CD, "- WITHDRAWN by the manager (record:"),
      ("FIXIND-6", NEW["library.md"], "stale beside \"[ c = B(A) ] does not allow c.A\""),
      ("FIXIND-7", CORE, "as composed in the definition the question is written in, not one literal"),
      ("FIXIND-8", NEW["parked.md"], "Partly overtaken: a library label is reached only through its source"),
      ("FIXIND-9", CORE, "is match-dependent: legal only where a pattern in it holds the label"),
      ("EXAMPLES-2", CORE, "| a label not written in the referencing definition, read bare"),
      ("EXAMPLES-4", NEW["library.md"], "a group question through the name reads every call's"),
      ("EVID-4", open(os.path.abspath(__file__), encoding="utf-8").read(), "# KNOWN LIMIT (EVID-4, planned")]
if s82("s17"):
    MK[4] = (MK[4][0], MK[4][1], MK[4][2] + " (planted)")
mk_miss = [i for i, t, sub in MK if ws(sub) not in ws(t)]
check("MARKS", not mk_miss, "%d dispositions' texts found where they landed; missing: %s" %
      (len(MK), mk_miss or "none"))

print("== DOC: every line this model formats occurs verbatim in the documents")
DL = list(LINES)
if s82("s14"):
    DL[0] = (DL[0][0], DL[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_miss = [(t, L_[:90]) for t, L_ in DL if ws(L_) not in ws(ALLDOC)]
check("DOC", DL and not d_miss, "%d lines; missing: %s" % (len(DL), d_miss or "none"))

failed = [n for n, ok in RESULTS if not ok]
print("predfix82_model: %d checks, %d failed%s" % (len(RESULTS), len(failed),
                                                    (" (%s)" % ", ".join(failed)) if failed else ""))
sys.exit(1 if failed else 0)
