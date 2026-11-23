#!/usr/bin/env python3
# Lane predfix83 (2026-11-22): the evidence for applying review r83's ruled dispositions (preddef1122; record
# "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on
# default-export (no owner words)") to the predicate documents: the engine fixes the review asks for (A1, A2, A7,
# A4, A5), the check fixes (E1, E2), the NAME-GRID check (process note P1, accepted), the manager's readings of the
# dispositions entry tested. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane preddef's model is LOADED unchanged: preddef_model.py is executed up to its line "the checks" (it
# loads predfix82's, which loads predcall's, predref's and predbound's lowerer and matcher). Its plants are cleared.
# The FIXES below then replace, in the loaded engine (the names resolve at call time in one namespace), these parts:
#   ANDTAG   A1, A7: every group lowered in operand j of an `&` chain K carries a mark (K, j) (a private part on the
#            scope `none`, read by no condition). After lowering, a PLAIN read, a `$` read or an index read of a
#            name is a compile error (core/labels/flow) when two groups the read can see carry marks of two
#            different operands of one chain, the chains the read is written inside excepted (an ambiguity is
#            judged where the reference is written: a read inside operand j sees only operand j of that chain). A
#            group question is not refused. The mark travels with the group, so the rule holds for a read from
#            outside a binding (`d.h`), through a part label over a chain (`ab.h`) and through an export list
#            (`d.year`), the sources counted being the ones the read can SEE (A4: a protected source is none).
#   LISTX    A2: an export list lists only what the part EXPORTS: a part an argument used alone left (`[(=d) =
#            B(A)]`, B's body `${rx}`) is not exported by the call, so listing it is the list's compile error.
#   OWNUSE   A5, the manager's reading: a binding's or a macro's own name reaches its UNLABELLED uses only. A use
#            that is the whole operand of a part label (`[a = A]`, `[c = B(A)]`, a list `[(=x) = A]`) is reached by
#            that label: it gets no prefix of its own name and is not counted as a use of the name in the text.
#   EXPR     D4 (i), the manager's reading: a part label over an EXPRESSION (`[ab = B | A]`, an operator at its
#            top) written in a binding reads, inside the definition, the labels visible in the expression by the
#            inside rules (its parts used alone are protected, `ab.l` legal inside) and exports outward only what
#            the expression's own text exports (a part used alone in it: nothing). At the top nothing is outside.
#   ARGOWN   A8, the manager's reading: under argument-default's candidate (error) a read written INSIDE an
#            argument written in place, beside the argument's own group, is the caller's own text and stays legal
#            (`occurrences(/(?<n>\d+)/ & (n: <100))`); the caller's reads outside the argument are refused as before.
#            The model moves the argument's own settings to a scope of the argument (`top~aN`) instead of dropping
#            them, so the argument's own reads still see them and nothing else does.
# Readings run with no engine change: A4 (a read from outside sees exported settings only: the loaded rule), D4
# (ii) (a parameter is no part whose labels the body names: the loaded binding check), D8 (at the top nothing is
# outside), D15/D16 (two lists of one name: the same label, the last mention).
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. The check NULLABLE walks every
# program this model's checks run for one and fails if found.
#
# Run (W = the worktree; any cwd):  timeout 1200 python3 -I -B W/docs/dev/lanes/predfix83_evidence/predfix83_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDFIX83_ENGINE=old runs the loaded engine (preddef's) WITHOUT the fixes (SWEEP's control; prints one table).
# PREDFIX83_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  CONTROL: the python `re` oracle widened to `\d!?`            s2  AMBOUT: the ANDTAG read check off
#   s3  BAREAMB: ANDTAG skips `$` and index reads                    s4  LISTCALL: LISTX off (an argument listed)
#   s5  OUTSIDE: PROTECT off (an outside read sees protected sources) s6  OWNUSE: OWNUSE off (the loaded counting)
#   s7  TWOUSE: (error) moves the labelled use of the argument too    s8  EXPR: EXPR off (a labelled expression exports)
#   s9  PARAM: a parameter's label in the body accepted              s10 ARGOWN: ARGOWN off (the argument's reads moved)
#   s11 LISTCOLL: two lists of one name read the FIRST mention        s12 EXAMPLE: PROTECT off for `B := A & A`
#   s13 SETAND: the loaded set test back                              s14 VISIBLE: preddef's VISIBLE off (its s4)
#   s15 GRID: one cell's deciding sentence read as legal (the bare index across `&`)
#   s16 SWEEP: a printed program re-spelled to read an unexported label   s17 SUCCESSOR: one declaration dropped
#   s18 NULLABLE: a nullable loop body run    s19 QUOTES: a quote altered   s20 MARKS: a marker read as missing
#   s21 DOC: a formatted line altered         s22 AWAITS: (error) closes nothing   s23 UNMARKED: one mark dropped
#   s24 TOPLEVEL: a one-use plain read through a binding's name refused (the closed idiom-confirm's other candidate)
#   s25 WITNESS: PROTECT off for the composed binding's parts (the composed and the literal read alike)
import hashlib
import os
import re
import subprocess
import sys

HERE4 = os.path.dirname(os.path.abspath(__file__))
PD = os.path.join(HERE4, "..", "preddef_evidence", "preddef_model.py")
SAB83 = set(x for x in os.environ.get("PREDFIX83_SABOTAGE", "").split(",") if x)
ENGINE_83 = os.environ.get("PREDFIX83_ENGINE", "new")
for v in ("PREDDEF_SABOTAGE", "PREDDEF_ENGINE", "PREDFIX82_SABOTAGE", "PREDFIX82_ENGINE", "PREDCALL_SABOTAGE",
          "PREDREF_SABOTAGE", "PREDBOUND_SABOTAGE"):
    os.environ.pop(v, None)


def s83(n):
    return n in SAB83


_src4 = open(PD, encoding="utf-8").read()
_cut4 = re.search(r"^# =+ the checks$", _src4, re.M).start()
exec(compile(_src4[:_cut4], PD, "exec"), globals())         # noqa: S102  (preddef's definitions, unchanged)
SABD.clear()
SAB82.clear()
SABC.clear()
SABR.clear()
SAB.clear()

OLD_D = dict(lower_atom=lower_atom, lower_and=lower_and, lower_list=lower_list, prog=prog, text_uses=text_uses,
             use_definition=use_definition, lower_gq=lower_gq, prefix_parts=prefix_parts, binding_check=binding_check,
             base_binds=base_binds, is_set_body=is_set_body)
_lower_atom_pd = _lower_atom_d                               # predfix82's lower_atom, preddef's base
_is_set_body_82 = _is_set_body_d                             # the loaded set test before preddef's SETAND

# ================================================================== the FIXES (lane predfix83)
READPOS = {}                  # NAMED index -> {chain K: operand j} for a read written inside operand j of K
IDX_IDX = set()               # NAMED indices of index reads (`h[k]`)
DIRECT = set()                # (scope, name) of a use that is the whole operand of a part label
SUPPRESS = []                 # names whose prefix is suppressed while lowering a directly labelled use
ARG_OWN = {}                  # argument relocation tag -> True
CHAIN_N = [0]
Ctx.direct = None


def _ctx_sub83(self, **kw):
    c = _ctx_sub0(self, **kw)
    c.labelled = self.labelled
    c.direct = None
    return c


_base_binds_83 = base_binds


def base_binds():                                            # noqa: F811
    _base_binds_83()
    READPOS.clear()
    IDX_IDX.clear()
    DIRECT.clear()
    ARG_OWN.clear()


def node_refs(text):
    return [int(n) for n in re.findall(r"\$\{#(\d+)\}", text)]


def map_groups(text, fn):
    """Apply fn(list of (base, scopes)) -> list to every group name and META member node in text."""
    for n in node_refs(text):
        nd = NODES.get(n)
        if nd and nd[0] == "setv":
            ps = fn(parts_of(nd[1]))
            NODES[n] = ("setv", join_parts(ps) if ps else "_closed@none", nd[2])

    def rep(mm):
        ps = fn(parts_of(mm.group(1)))
        return "(?<%s>" % join_parts(ps) if ps else "(?:"
    return GROUP_NAME.sub(rep, text)


def all_groups(text):
    out = [parts_of(g) for g in GROUP_NAME.findall(text)]
    for n in node_refs(text):
        nd = NODES.get(n)
        if nd and nd[0] == "setv":
            out.append(parts_of(nd[1]))
    return out


# ---- ANDTAG (A1, A7)
def lower_and(parts, ctx):                                   # noqa: F811
    """predfix82's lower_and, each pattern operand's groups marked (K, j); the reads of each operand recorded."""
    pats = [x for x in parts if not (IS_COND.match(x) or is_gq(x) or (x in BINDS and IS_COND.match(BINDS[x])))]
    rest = [x for x in parts if x not in pats]
    mk = fresh("k")
    CHAIN_N[0] += 1
    K = "c%d" % CHAIN_N[0]
    sub = ctx.sub()
    texts = []
    for j, q in enumerate(pats):
        a = len(NAMED)
        tq = "(?:%s)" % lower(q, sub)
        for i in range(a, len(NAMED)):
            READPOS.setdefault(i, {})[K] = j
        tq = map_groups(tq, lambda ps, j=j: ps + [("_and.%s.%d" % (K, j), ["none"])])
        texts.append(tq)
    out = node_ref(("mark", mk)) + texts[0]
    for tq in texts[1:]:
        out += "(?&%s:%s)" % (mk, tq)
    seen = {}
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
        for sc, nm in NAMED[a:]:
            head = nm.split(".")[0]
            if sc == ctx.cur and nm in amb and not ("." in nm and USES.get((ctx.cur, head), 0) > 1):
                raise CompileError("`%s`: both sides of `&` surface it, an ambiguous reference (core/labels/flow)"
                                   % nm)
    return out


def lower_gq(text, ctx):                                     # noqa: F811
    a = len(NAMED)
    r = OLD_D["lower_gq"](text, ctx)
    if IDX.fullmatch(text):
        IDX_IDX.update(range(a, len(NAMED)))
    return r


def amb_check(rx, start):
    """ANDTAG's read check over the whole lowered program."""
    if s83("s2"):
        return
    groups = all_groups(rx)
    for i in range(start, len(NAMED)):
        sc, nm = NAMED[i]
        if i in GQ_IDX and i not in IDX_IDX:
            continue
        if s83("s3") and (i in IDX_IDX or i not in COND_IDX):
            continue
        inside = READPOS.get(i, {})
        tags = {}
        for ps in groups:
            if not any(b == nm and sc in s for b, s in ps):
                continue
            marks = [b.split(".")[1:] for b, s in ps if b.startswith("_and.") and s == ["none"]]
            if any(K in inside and int(j) != inside[K] for K, j in marks):
                continue
            for K, j in marks:
                tags.setdefault(K, set()).add(j)
        if any(len(v) > 1 for v in tags.values()):
            raise CompileError("`%s`: two sides of one `&` set it and the read can see both, an ambiguous "
                               "reference (a compile error, core/labels/flow)" % nm)


COND_IDX = set()              # NAMED indices made by a condition entry (s3's plant reads it)
_lower_cond_83 = lower_cond


def lower_cond(text, ctx, zero_key=None):                    # noqa: F811
    a = len(NAMED)
    r = _lower_cond_83(text, ctx, zero_key)
    COND_IDX.update(range(a, len(NAMED)))
    return r


# ---- OWNUSE (A5)
def single_use(e, ctx):
    e = e.strip()
    if e in ctx.params:
        return False
    if e in BINDS and not is_cond(BINDS[e]) and not is_set_body(BINDS[e]):
        return True
    call = parse_call(e)
    return bool(call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0]))


DLAB = re.compile(r"\[(?:\w*|\([^()]*\)) = ([A-Za-z_]\w*)(\([^\[\]]*\))?\]")
_text_uses_83 = text_uses


def text_uses(t):                                            # noqa: F811
    cnt = _text_uses_83(t)
    if s83("s6"):
        return cnt
    for mm in DLAB.finditer(t):
        name, call = mm.group(1), mm.group(2)
        if (call and name in MACROS) or (not call and name in BINDS):
            if cnt.get(name, 0) > 0:
                cnt[name] -= 1
                if not cnt[name]:
                    del cnt[name]
    return cnt


def prefix_parts(text, prefix, at, vis, kind):               # noqa: F811
    if kind == "use" and SUPPRESS and SUPPRESS[-1] == prefix:
        return text
    return OLD_D["prefix_parts"](text, prefix, at, vis, kind)


# ---- EXPR (D4 (i))
def is_expression(e):
    e = e.strip()
    return any(len(split_top(e, op)) > 1 for op in (" | ", " & ", " SEQ "))


def lower_label_expr(name, inner_e, q, ctx):
    lc = ctx.sub()
    lc.labelled = False
    inner = lower(inner_e, lc)
    cur = ctx.cur
    saved = set()
    for ps in all_groups(inner):
        for b, sc in ps:
            p = "%s@%s" % (b, ",".join(sc))
            if p in CLOSED_PARTS and cur in sc:
                saved.add(p)
    CLOSED_PARTS.difference_update(saved)
    inner = prefix_parts(inner, name, cur, cur, "own" if name.startswith("_") else "part")
    CLOSED_PARTS.update(saved)

    def protect(ps):
        closed_b = set(b for b, sc in ps if "%s@%s" % (b, ",".join(sc)) in saved)
        out = []
        for b, sc in ps:
            if b.startswith(name + ".") and b[len(name) + 1:] in closed_b and sc == [cur]:
                sc = [cur, cur]                              # the same scope twice: a part string of its own
                CLOSED_PARTS.add("%s@%s" % (b, ",".join(sc)))
            out.append((b, sc))
        return out
    inner = map_groups(inner, protect)
    ctx.held.add(name)
    grp = "(?<%s@%s>%s)%s" % (name, ",".join(ctx.scopes), inner, q)
    if name.startswith("_"):
        grp = close_parts(grp, ctx.scopes[:-1])
    return grp


# ---- ARGOWN (A8): the argument's own settings moved to a scope of the argument under (error)
ARGSEQ = [0]
SCOPE_STR = re.compile(r"^([\w.]+)@([\w~,]+)$")


def relocate(text, outer, a, b, keep_reads):
    ARGSEQ[0] += 1
    tag = "~a%d" % ARGSEQ[0]
    outer = set(outer)

    def mv(sc):
        return [x + tag if x in outer else x for x in sc]
    text = map_groups(text, lambda ps: [(bs, mv(sc)) for bs, sc in ps])

    def walk(x):
        if isinstance(x, str):
            mm = SCOPE_STR.match(x)
            if mm and set(mm.group(2).split(",")) & outer:
                return "%s@%s" % (mm.group(1), ",".join(mv(mm.group(2).split(","))))
            return x
        if isinstance(x, tuple):
            return tuple(walk(y) for y in x)
        if isinstance(x, list):
            return [walk(y) for y in x]
        return x
    if keep_reads:
        for n in node_refs(text):
            if n in NODES and NODES[n][0] != "setv":
                NODES[n] = walk(NODES[n])
        for i in range(a, b):
            sc, nm = NAMED[i]
            if sc in outer:
                NAMED[i] = (sc + tag, nm)
    ARG_OWN[tag] = set(outer)
    return text


def widen_for_args(text):
    """ARGOWN: every group outside an argument that a caller scope X sees gains the scope X~aN of each moved
    argument, so a read written inside the argument (keyed X~aN) sees the caller's own labels and the argument's,
    and a read outside it (keyed X) sees the caller's only."""
    for tag, outer in ARG_OWN.items():
        def add(ps, tag=tag, outer=outer):
            return [(b, sc + [x + tag for x in sc if x in outer]) for b, sc in ps]
        text = map_groups(text, add)
    return text


# ---- lower_atom: preddef's, with OWNUSE, EXPR and ARGOWN
def lower_atom(expr, ctx):                                   # noqa: F811
    e = expr.strip()
    mm = LISTPL.fullmatch(e)
    if mm:
        return lower_list(mm, ctx)
    pl = re.fullmatch(r"\[(\w*) = (.*)\]([+*?]?)", e, re.S)
    if pl:
        name, inner_e, q = pl.groups()
        if (is_expression(inner_e) and ctx.cur != "top" and name not in ("", "_") and not s83("s8")):
            return lower_label_expr(name, inner_e.strip(), q, ctx)
        lc = ctx.sub()
        lc.labelled = True
        if single_use(inner_e, ctx) and not s83("s6"):
            lc.direct = inner_e.strip()
        return _lower_atom_pd(e, lc)
    alone = not ctx.labelled and ctx.cur != "top"
    if e in ctx.params:                                      # ARGS: an argument used alone in the body
        a = len(NAMED)
        text = _lower_atom_pd(e, ctx)
        b = len(NAMED)
        if not ctx.labelled or s83("s7"):
            ARG_PARTS.update(all_parts(text))
            if ARGDEF[0] == "error" and not s83("s22"):
                caller = ctx.params[e][1]
                text = relocate(text, caller.scopes, a, b, keep_reads=not s83("s10"))
                ARG_PARTS.update(all_parts(text))
        return text
    call = parse_call(e)
    pattern_use = ((e in BINDS and not is_cond(BINDS[e]) and not is_set_body(BINDS[e])) or
                   (call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0])
                    and not is_cond(pick_macro(*call)[1])))
    direct = pattern_use and ctx.direct == e
    if direct:
        nm = call[0] if call else e
        SUPPRESS.append(nm)
        DIRECT.add((ctx.cur, nm))
    try:
        text = _lower_atom_pd(e, ctx)
    finally:
        if direct:
            SUPPRESS.pop()
    if pattern_use and alone and not (s83("s5") or s83("s12") and e == "A" or s83("s25") and e in ("CA", "CB")):
        text = close_parts(text, ctx.scopes[:-1])              # PROTECT
    return text


# ---- LISTX (A2) and OWNUSE for a list
def lower_list(mm, ctx):                                     # noqa: F811
    pairs, allx, out = list_pairs(mm.group(1))
    lc = ctx.sub()
    lc.labelled = True
    if single_use(mm.group(2), ctx) and not s83("s6"):
        lc.direct = mm.group(2).strip()
    inner = lower(mm.group(2), lc)
    here = set(ctx.scopes)
    exported = set()
    for ps in all_groups(inner):
        for b, sc in ps:
            if ctx.cur in sc and "." not in b and not private(b):
                if "%s@%s" % (b, ",".join(sc)) in ARG_PARTS and not s83("s4"):
                    continue
                exported.add(b)
    for new, old in pairs:
        if old not in exported:
            raise CompileError("`%s` is not a label the part exports (export-list: only an exported label is listed)"
                               % old)
    names = list(pairs)
    if allx:
        names += [(b, b) for b in sorted(exported) if b not in out and (b, b) not in pairs]
    ctx.held.update(n for n, _ in names)

    def fix(ps):
        keep = [(b, sc) for b, sc in ps if not (set(sc) & here)]
        for b, sc in ps:
            if set(sc) & here and "." not in b and "%s@%s" % (b, ",".join(sc)) not in ARG_PARTS:
                for new, old in names:
                    if old == b:
                        keep.append((new, list(ctx.scopes)))
        return keep
    return "(?:%s)%s" % (map_groups(inner, fix), mm.group(3))


# ---- the reasons of OWNUSE's refusal; the read checks at each definition
def own_reason(msg, scope):
    mm = re.match(r"`([\w.]+)`: `[\w.]+` is not visible through `(\w+)`", msg)
    if mm and (scope, mm.group(2)) in DIRECT and USES.get((scope, mm.group(2)), 0) == 0:
        return ("`%s`: every use of `%s` here is labelled; a labelled use is reached by its label, not by `%s` (a "
                "compile error, core/labels/paths/binding-prefix)" % (mm.group(1), mm.group(2), mm.group(2)))
    return msg


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    sc = "s%d" % (COUNTER[0] + 1)
    if s83("s9") and params:                 # the plant: a parameter's label in the body accepted (dropped unread)
        for pn in params:
            body = re.sub(r"\s*&\s*\(%s\.\w+: [^)]*\)" % re.escape(pn), "", body)
    try:
        return OLD_D["use_definition"](body, ctx, dname, params, mark)
    except CompileError as e:
        raise CompileError(own_reason(str(e), sc))


def binding_check(line):                                     # noqa: F811
    keep = len(NAMED)
    try:
        return OLD_D["binding_check"](line)
    except CompileError as e:
        if s83("s9") and "does not hold: rx." in str(e):
            return None
        raise
    finally:
        for d in (READPOS,):
            for i in [i for i in d if i >= keep]:
                del d[i]
        IDX_IDX.difference_update([i for i in IDX_IDX if i >= keep])
        COND_IDX.difference_update([i for i in COND_IDX if i >= keep])


def prog(expr, binds=(), **opts):                            # noqa: F811
    start = [None]
    _nm0 = len(NAMED)
    try:
        Pg = OLD_D["prog"](expr, binds, **opts)
    except CompileError as e:
        raise CompileError(own_reason(str(e), "top"))
    if ARG_OWN:
        Pg2 = Prog(widen_for_args(Pg.rx))
        Pg2.expr = expr
        RUN[-1] = (expr, tuple(binds), Pg2.node)
        Pg = Pg2
    amb_check(Pg.rx, 0)
    if s83("s24"):
        for sc, nm in NAMED:
            if sc == "top" and "." in nm and USES.get(("top", nm.split(".")[0]), 0) == 1:
                raise CompileError("`%s`: a plain read through a prefix (the plant)" % nm)
    del start, _nm0
    return Pg


if s83("s13"):
    is_set_body = _is_set_body_82                            # noqa: F811
if s83("s14"):
    SABD.add("s4")

if ENGINE_83 == "old":
    globals().update(OLD_D)
    Ctx.sub = _ctx_sub
else:
    Ctx.sub = _ctx_sub83

if ENGINE_83 == "old":
    for f, ln, line_, a, pt, tail in sweep_lines():
        for ad in ("local", "error"):
            ARGDEF[0] = ad
            st, got = sweep_one(line_, a, pt, tail)
            print("SW\t%s\t%s\t%d\t%s\t%s" % (ad, f, ln, st, got if st in ("same", "DIFF") else ""))
    ARGDEF[0] = "local"
    sys.exit(0)

# ================================================================== the checks
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def ref(expr, binds=(), ad="local"):
    """The refusal's message, or None when the program compiles."""
    ARGDEF[0] = ad
    try:
        prog(expr, list(binds))
        return None
    except CompileError as e:
        return str(e)
    finally:
        ARGDEF[0] = "local"


def tp(expr, binds=(), ad="local"):
    ARGDEF[0] = ad
    try:
        return prog(expr, list(binds))
    except CompileError:
        return None
    finally:
        ARGDEF[0] = "local"


def wdiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t)) if Pg is not None else -1


def bt(binds):
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def dl(label, expr, binds, Pg, wh, sr, fa, tag, tail=""):
    return doc_line("%s%s (`%s`%s)%s" % ((label + ": ") if label else "", fmt(Pg, wh, sr, fa), expr, bt(binds), tail),
                    tag)


def has(msg, *subs):
    """REASON (E1): a refusal counts only when its message names the expected rule."""
    return msg is not None and all(s in msg for s in subs)


AH = "A := /(?<h>\\d)/"
AD = "A := /(?<d>\\d)/"
AA = "A := /(?<a>\\d)/"
FLOW = ("an ambiguous reference", "core/labels/flow")
ISO = "isodate := [year = /\\d{4}/] SEQ \"-\" SEQ [month = /\\d\\d/] SEQ \"-\" SEQ [day = /\\d\\d/]"

print("== CONTROL: the loaded matcher against python `re`")
QD = pop("37!", 3)
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("p2", ["p2 := /${A}!/", AH]), QD), answers(Re(r"\d!" if not s83("s1") else r"\d!?"), QD))
check("CONTROL", (c1, c2) == ((0, 0, 0),) * 2, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; `/${A}!/` "
      "against `\\d!` %s over %d texts" % (c1, c2, len(QD)))

print("== AMBOUT (A1): the `&` ambiguity on a read from outside, through a part label over a chain, through lists")
AMB1 = ["d := /(?<h>\\d)\\d/ & /\\d(?<h>\\d)/"]
AMB2 = ["d := [x = /(?<h>\\d)\\d/] & [y = /\\d(?<h>\\d)/]"]
I1 = "i1 := [year = /\\d\\d/] SEQ /\\d\\d/"
I2 = "i2 := /\\d\\d/ SEQ [year = /\\d\\d/]"
AMB3 = ["d := [(=year) = i1] & [(=year) = i2]", I1, I2]
r_a1 = ref('d & (d.h: "2")', AMB1)
r_a2 = ref('[ab = /(?<h>\\d)\\d/ & /\\d(?<h>\\d)/] & (ab.h: "2")')
r_a3 = ref('d & (d.h: "2")', AMB2)
r_a4 = ref('d & (d.year: "20")', AMB3)
BXY = ["B := [x = A] & [y = A]", AA]
P_bx = tp("B & (B.x.a: 9)", BXY)
P_gq = tp('d & some((d.h: "1"))', AMB1)
D2 = pop("129", 2)
check("AMBOUT", all(has(r, *FLOW) for r in (r_a1, r_a2, r_a3, r_a4)) and wdiff(P_bx, lambda t: t == "9", pop("97", 2))
      == 0 and wdiff(P_gq, lambda t: len(t) == 2 and "1" in t, D2) == 0,
      "refused for the flow rule: in-text chain read from outside `d.h` %s, a part label over a chain `ab.h` %s, each "
      "side labelled `d.h` %s, two lists across `&` `d.year` %s; legal: `B.x.a` differing %d, a group question "
      "`some((d.h: \"1\"))` differing %d over %d texts" % (has(r_a1, *FLOW), has(r_a2, *FLOW), has(r_a3, *FLOW),
                                                           has(r_a4, *FLOW), wdiff(P_bx, lambda t: t == "9",
                                                                                   pop("97", 2)),
                                                           wdiff(P_gq, lambda t: len(t) == 2 and "1" in t, D2),
                                                           len(D2)))
print("   refusal (outside): %s" % r_a1)

print("== BAREAMB (A7): bare `$h` and `h[k]` across `&`")
r_b1 = ref("(/(?<h>\\d)\\d/ & /\\d(?<h>\\d)/) SEQ $h")
r_b2 = ref('/(?<h>\\d)\\d/ & /\\d(?<h>\\d)/ & (h[2]: "1")')
P_b3 = tp('/(?<h>\\d)/ & (/(?<h>\\d)/ & (h: "3"))')
check("BAREAMB", has(r_b1, *FLOW) and has(r_b2, *FLOW) and wdiff(P_b3, lambda t: t == "3", pop("34", 2)) == 0,
      "refused for the flow rule: `$h` after a chain %s, `h[2]` across `&` %s; a read written inside an operand reads "
      "that operand (`/(?<h>\\d)/ & (/(?<h>\\d)/ & (h: \"3\"))`) differing %d" %
      (has(r_b1, *FLOW), has(r_b2, *FLOW), wdiff(P_b3, lambda t: t == "3", pop("34", 2))))

print("== LISTCALL (A2): an export list through a call lists only what the call exports")
LISTERR = ("is not a label the part exports",)
r_l1 = ref("[(=d) = B(A)] & (d: <5)", [AD, "B(rx) := /${rx}xx/"])
r_l2 = ref("q & (q.d: <5)", ["q := [(=d) = B(A)] SEQ \";\"", AD, "B(rx) := /${rx}xx/"])
r_l3 = ref("[(=l) = atomic(B | A)] & (l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
LB2 = [AD, "B(rx) := /${rx}-(?<d>\\d)/"]
P_l4 = tp("[(=d) = B(A)] & (d: <5)", LB2)
own2 = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5      # noqa: E731
P_l5 = tp("B(A) & (B.d: <5)", [AD, "B(rx) := /${[p = rx]}xx/"])
a6 = lambda t: re.fullmatch(r"\dxx", t) is not None and int(t[0]) < 5      # noqa: E731
check("LISTCALL", all(has(r, *LISTERR) for r in (r_l1, r_l2, r_l3)) and wdiff(P_l4, own2, pop("37-", 3)) == 0 and
      wdiff(P_l5, a6, pop("37x", 3)) == 0,
      "refused at the list: `[(=d) = B(A)]` in place %s, in a binding %s, `[(=l) = atomic(B | A)]` %s; the body's own "
      "`d` listed (`/${rx}-(?<d>\\d)/`) differing %d; A6, a call exports what its body exports: `B(A) & (B.d: <5)`, "
      "B(rx) := `/${[p = rx]}xx/` (p's `d` by name) differing %d" %
      (has(r_l1, *LISTERR), has(r_l2, *LISTERR), has(r_l3, *LISTERR), wdiff(P_l4, own2, pop("37-", 3)),
       wdiff(P_l5, a6, pop("37x", 3))))
print("   refusal: %s" % r_l1)

print("== OUTSIDE (A4): a read from outside sees the binding's EXPORTED settings only")
PUB = ["pub := [a = A] SEQ A", AH]
P_o1 = tp("pub & (pub.h: <5)", PUB)
P_o2 = tp("B & (B.a: 9)", ["B := A & /(?<a>\\d)/", AA])
r_o3 = ref("B", ["B := A & /(?<a>\\d)/ & (a: 9)", AA])
first5 = lambda t: re.fullmatch(r"\d\d", t) is not None and int(t[0]) < 5      # noqa: E731
if P_o1 is not None:
    dl("The exported setting only", "pub & (pub.h: <5)", PUB, P_o1, ["37", "73"], "73 37", "37 73 14",
       "core/labels/export/flat-read-outside")
check("OUTSIDE", wdiff(P_o1, first5, pop("37", 2)) == 0 and wdiff(P_o2, lambda t: t == "9", pop("97", 2)) == 0
      and has(r_o3, "both sides of `&`"),
      "`pub.h`, pub := `[a = A] SEQ A`, against \"the FIRST digit under 5\" (the exported `a`'s, not the last "
      "mention): differing %d; `B.a`, B := `A & /(?<a>\\d)/`, legal from outside (the protected side no source) "
      "differing %d; inside B the plain `a` refused as ambiguous %s" %
      (wdiff(P_o1, first5, pop("37", 2)), wdiff(P_o2, lambda t: t == "9", pop("97", 2)), has(r_o3, "both sides")))

print("== OWNUSE (A5): a binding's own name reaches its unlabelled uses only")
r_w1 = ref('[a = A] SEQ "!" & (A.h: <5)', [AH])
P_w2 = tp("[a = A] SEQ A & (A.h: <5)", [AH])
P_w3 = tp("[A = A] SEQ A & (A.h: <5)", [AH])
warn3 = ("hide-label", "A") in WARNINGS
P_w4 = tp("[a = A] SEQ A & (a.h: <5)", [AH])
second5 = lambda t: re.fullmatch(r"\d\d", t) is not None and int(t[1]) < 5     # noqa: E731
if P_w2 is not None:
    dl("The unlabelled use", "[a = A] SEQ A & (A.h: <5)", [AH], P_w2, ["37", "73"], "37 73", "73 37 14",
       "core/labels/paths/binding-prefix")
check("OWNUSE", has(r_w1, "`A` is neither written nor a binding used") and wdiff(P_w2, second5, pop("37", 2)) == 0
      and wdiff(P_w3, first5, pop("37", 2)) == 0 and warn3 and wdiff(P_w4, first5, pop("37", 2)) == 0,
      "`[a = A] SEQ \"!\"`: `A.h` refused (no unlabelled use) %s; `[a = A] SEQ A`: `A.h` reads the unlabelled use "
      "(the second digit) differing %d, `a.h` the labelled one differing %d; `[A = A] SEQ A`: `A.h` is the label's "
      "(the first digit) differing %d, the hide-label warning %s" %
      (has(r_w1, "neither written"), wdiff(P_w2, second5, pop("37", 2)), wdiff(P_w4, first5, pop("37", 2)),
       wdiff(P_w3, first5, pop("37", 2)), warn3))
print("   refusal: %s" % r_w1)

print("== TWOUSE (A3): an argument the body uses both alone and labelled: the two candidates differ in ANSWER")
TU = [AD, "B(rx) := /${[p = rx]}-${rx}/"]
P_tl, P_te = tp("B(A) & (A.d: <5)", TU), tp("B(A) & (A.d: <5)", TU, "error")
if P_tl is not None:
    dl("Both uses, (local)", "B(A) & (A.d: <5)", TU[::-1], P_tl, ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9",
       "core/labels/paths/argument-default")
if P_te is not None:
    dl("Both uses, (error)", "B(A) & (A.d: <5)", TU[::-1], P_te, ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9",
       "core/labels/paths/argument-default")
dig = pop("37-", 3)
check("TWOUSE", wdiff(P_tl, lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5, dig)
      == 0 and wdiff(P_te, lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[0]) < 5, dig) == 0,
      "`B(A) & (A.d: <5)`, B(rx) := `/${[p = rx]}-${rx}/`: (local) reads the alone use (the second digit), differing "
      "%d; (error) reads `p`'s (the first digit), differing %d, over %d texts" %
      (wdiff(P_tl, lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5, dig),
       wdiff(P_te, lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[0]) < 5, dig), len(dig)))

print("== EXPR (D4 (i)): a part label over an expression reads its parts inside, exports what its text writes")
LA = ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"]
P_x1 = tp("X", ["X := [ab = B | A] SEQ \"!\" & (ab.l: <20)"] + LA)
r_x2 = ref("X & (X.ab.l: <20)", ["X := [ab = B | A] SEQ \"!\""] + LA)
P_x3 = tp("X & (X.ab.l: <5)", ["X := [ab = A SEQ /;(?<l>\\d)/] SEQ \"!\"", LA[0]])
P_x4 = tp("[ab = B | A] & (ab.l: <20)", LA)
l20 = lambda t: re.fullmatch(r"\d\d!?", t) is not None and (int(t[:2]) < 20 or int(t[0]) < 20)   # noqa: E731
lit = lambda t: re.fullmatch(r"\d\d;\d!", t) is not None and int(t[3]) < 5     # noqa: E731
if P_x3 is not None:
    dl("Outward, what the expression's text writes", "X & (X.ab.l: <5)", ["X := [ab = A SEQ /;(?<l>\\d)/] SEQ \"!\"",
                                                                          LA[0]], P_x3,
       ["13;3!", "13;7!"], "13;7! 13;3!", "13;3! 13;7! 22;1!", "core/labels/paths")
check("EXPR", P_x1 is not None and has(r_x2, "not visible through `X`") and wdiff(P_x3, lit, pop("137;!", 5)) == 0
      and wdiff(P_x4, lambda t: re.fullmatch(r"\d\d", t) is not None, pop("25", 2)) == 0,
      "inside X `ab.l` legal %s; from outside `X.ab.l` refused (B, A used alone in the expression) %s; "
      "`[ab = A SEQ /;(?<l>\\d)/]` exports the literal's `l` only, differing %d; at the top `[ab = B | A] & (ab.l: "
      "<20)` legal, differing %d" % (P_x1 is not None, has(r_x2, "not visible through `X`"),
                                     wdiff(P_x3, lit, pop("137;!", 5)),
                                     wdiff(P_x4, lambda t: re.fullmatch(r"\d\d", t) is not None, pop("25", 2))))
print("   refusal: %s" % r_x2)

print("== PARAM (D4 (ii)): a macro's parameter is not a part whose labels the body names")
r_p1 = ref("B(A)", ["B(rx) := /${rx}/ & (rx.d: <5)", AD])
r_p2 = ref("B(A)", ["B(rx) := /${rx}/ & (d: <5)", AD])
check("PARAM", has(r_p1, "rx.d") and has(r_p2, "d"), "`(rx.d: <5)` in B's body refused at the binding %s; the bare "
      "`(d: <5)` refused %s: %s" % (has(r_p1, "rx.d"), has(r_p2, "d"), r_p1))

print("== ARGOWN (A8): a read written inside an argument, beside its own group, is the caller's own text")
OC = "occurrences(/(?<n>\\d+)/ & (n: <100))"
P_ol, P_oe = tp(OC), tp(OC, ad="error")
r_oe2 = ref('hits(/a(?<g>x)?/) & (g: "x")', ad="error")
DO = ["1234", "123", "12", "1", "12345"]
check("ARGOWN", P_ol is not None and P_oe is not None and [P_ol.whole(t) for t in DO] == [P_oe.whole(t) for t in DO]
      and P_oe.whole("1234") and has(r_oe2, "no group visible here sets it"),
      "`%s`: legal under (local) %s and (error) %s, the same WHOLE answers over %s (`1234` HOLDS under (error) %s); a "
      "read OUTSIDE the argument (`hits(/a(?<g>x)?/) & (g: \"x\")`) still refused under (error) %s" %
      (OC, P_ol is not None, P_oe is not None, DO, P_oe.whole("1234") if P_oe else None,
       has(r_oe2, "no group visible")))

print("== LISTCOLL (D16): two lists naming one label: the same label, the last mention")
LC = ["d := [(=year) = i1] SEQ [(=year) = i2]", I1, I2]
P_lc = tp('d & (d.year: "20")', LC)
lastyr = (lambda t: len(t) == 8 and t[6:] == "20") if not s83("s11") else (lambda t: len(t) == 8 and t[:2] == "20")
r_lc2 = ref('[(=year) = isodate] SEQ "!" & (isodate.year: "2025")', [ISO])
r_lc3 = ref('[(=h) = q] SEQ "!" & (q.a.h: <5)', ["q := [a = A] SEQ \";\"", AH])
check("LISTCOLL", wdiff(P_lc, lastyr, ["20192019", "19202020", "20202020", "19191919"]) == 0 and
      has(r_lc2, "isodate.year") and has(r_lc3, "q.a.h"),
      "`d.year`, d := `[(=year) = i1] SEQ [(=year) = i2]`, against \"i2's year (the last mention) is 20\": differing "
      "%d of 4; inside a binding that lists the part, its own prefix `isodate.year` refused %s, a listed part label's "
      "path `q.a.h` refused %s (the list takes the listed labels only: %s)" %
      (wdiff(P_lc, lastyr, ["20192019", "19202020", "20202020", "19191919"]), has(r_lc2, "isodate.year"),
       has(r_lc3, "q.a.h"), r_lc2))

print("== EXAMPLE (E1): his `B := A & A`, `C := B & (B.a: 9)`, \"here B.a is always an error\": the REASON compared")
BAA = ["B := A & A", AA]
WANT = ("`B.a`: `a` is not visible through `B`",)
r_e1 = ref("C", ["C := B & (B.a: 9)"] + BAA)
r_e2 = ref("C", ["C := B & some((B.a: \"9\"))"] + BAA)
r_e3 = ref("B & (B.a: 9)", BAA)
r_e4 = ref("B & some((B.a: \"9\"))", BAA)
check("EXAMPLE", all(has(r, *WANT) for r in (r_e1, r_e2, r_e3, r_e4)),
      "refused for the reason \"`a` is not visible through `B`\" (B exports no `a`): at C plain %s, group question "
      "%s; at the top plain %s, group question %s" % tuple(has(r, *WANT) for r in (r_e1, r_e2, r_e3, r_e4)))
print("   refusal at C: %s" % r_e1)

print("== SETAND (E1): `A & A` and `A & /../` are patterns: a behaviour arm, not the set test itself")
P_s1 = tp("B & (B.a: 9)", ["B := A & /(?<a>\\d)/", AA])
P_s2 = tp("B", ["B := A & A", AA])
check("SETAND", wdiff(P_s1, lambda t: t == "9", pop("97", 2)) == 0 and
      wdiff(P_s2, lambda t: re.fullmatch(r"\d", t) is not None, pop("97", 2)) == 0,
      "`B & (B.a: 9)`, B := `A & /(?<a>\\d)/` (a pattern; its literal's `a` exported): differing %d; the program `B`, B "
      ":= `A & A`, matching one digit: differing %d" % (wdiff(P_s1, lambda t: t == "9", pop("97", 2)),
                                                        wdiff(P_s2, lambda t: re.fullmatch(r"\d", t) is not None,
                                                              pop("97", 2))))

print("== VISIBLE (E2): a read of a label not visible where it is written: inside a body, and a BARE name at the top")
r_v1 = ref("C", ["C := B SEQ \"!\" & (B.h: <5)", "B := A SEQ \"-\"", AH])
r_v2 = ref("B(/(?<g>\\d)/) & (g: <5)", ["B(rx) := /${rx}xx/"], "error")
P_v3 = tp("C", ["C := B SEQ \"!\" & (B.A.h: <5)", "B := [A = A] SEQ \"-\"", AH])
check("VISIBLE", has(r_v1, "not visible through `B` in C") and has(r_v2, "`g`: no group visible here sets it") and
      P_v3 is not None, "inside C `B.h` refused %s; at the top the bare `g` of an argument the body uses alone, under "
      "(error), refused %s; `B.A.h` through B's part label legal %s" %
      (has(r_v1, "not visible through"), has(r_v2, "no group visible here"), P_v3 is not None))
print("   refusals: %s | %s" % (r_v1, r_v2))

print("== TOPLEVEL (D8, D17): at the top nothing is outside; the plain idiom with one use (ruled by default-export)")
P_t1 = tp("isodate & (isodate.year: < 2100)", [ISO])
y2100 = lambda t: re.fullmatch(r"\d{4}-\d\d-\d\d", t) is not None and int(t[:4]) < 2100   # noqa: E731
TD = ["2025-01-02", "2100-01-02", "1999-12-31", "2025-01-0"]
if P_t1 is not None:
    dl("The plain idiom, one use", "isodate & (isodate.year: < 2100)", [ISO], P_t1, ["2025-01-02", "2100-01-02"],
       "2100-01-02 2025-03-04", "2025-01-02 2100-01-02 1999-12-31", "core/labels/paths/one-use-read")
check("TOPLEVEL", wdiff(P_t1, y2100, TD) == 0, "`isodate & (isodate.year: < 2100)` (isodate used alone at the top) "
      "against \"year under 2100\": differing %d of %d" % (wdiff(P_t1, y2100, TD), len(TD)))

print("== WITNESS (D2, CORRECTION 1): composed from parts used alone against one literal: the user reads what each exports")
WC = ["CA := /(?<c>\\d)/", "CB := /(?<c>\\d)/"]
P_c2 = tp('D2 & (D2.c: "3")', ["D2 := /(?<c>\\d)(?<c>\\d)/"])
r_c1 = ref('D1 & (D1.c: "3")', ["D1 := CA SEQ CB"] + WC)
if P_c2 is not None:
    dl("One literal", 'D2 & (D2.c: "3")', ["D2 := /(?<c>\\d)(?<c>\\d)/"], P_c2, ["73", "37"], "37 73", "73 37 13",
       "core/labels/flow")
lastc = lambda t: re.fullmatch(r"\d3", t) is not None      # noqa: E731
MN = ["mn(S) := months & (months.mname.index: S)", "months := [mname = [/Jan/, /Feb/, /Mar/, /Apr/, /May/, /Jun/, /Jul/]]"]
r_c4 = ref('mn(<= 6) & (mn.mname: "Jun")', MN)
P_c5 = tp('mn(<= 6)', MN)
check("WITNESS", wdiff(P_c2, lastc, pop("37", 2)) == 0 and has(r_c1, "not visible through `D1`") and
      has(r_c4, "not visible through `mn`") and P_c5 is not None and P_c5.whole("Jun") and not P_c5.whole("Jul"),
      "`D2 & (D2.c: \"3\")`, D2 := `/(?<c>\\d)(?<c>\\d)/`, the last mention: differing %d; `D1 & (D1.c: \"3\")`, D1 := "
      "`CA SEQ CB` (each used alone), refused for not visible %s: %s; month_numbered's shape (a body using `months` "
      "alone): `mn.mname` refused %s, `mn(<= 6)` matching `Jun` not `Jul` %s" %
      (wdiff(P_c2, lastc, pop("37", 2)), has(r_c1, "not visible through `D1`"), r_c1, has(r_c4, "not visible"),
       P_c5 is not None and P_c5.whole("Jun") and not P_c5.whole("Jul")))

print("== GRID (P1): the name grid: spelling x occurrences of its source x read kind; each cell its deciding sentence")
# Each spelling: the read name and, per occurrence kind, (the pattern, its bindings). The read kinds are spelled
# from the pattern P and the name R: plain `P & (R: "3")`, `$` `(P) SEQ $R`, group question `P & some((R: "3"))`,
# index `P & (R[1]: "3")`.
G_A = "A := /(?<h>\\d)/"
G_B = "B(rx) := /${rx}(?<d>\\d)/"
G_I1 = "i1 := [year = /\\d/] SEQ /\\d/"
G_I2 = "i2 := /\\d/ SEQ [year = /\\d/]"
G_ARG = "B(rx) := /${rx}x/"
SPELL = [
    ("bare", {"one": ("h", "/(?<h>\\d)/", []), "seq": ("h", "/(?<h>\\d)/ SEQ /(?<h>\\d)/", []),
              "and": ("h", "/(?<h>\\d)\\d/ & /\\d(?<h>\\d)/", []),
              "nest": ("h", "X", ["X := /(?<h>\\d)/ SEQ \"!\""])}),
    ("binding", {"one": ("A.h", "A", [G_A]), "seq": ("A.h", "A SEQ A", [G_A]), "and": ("A.h", "A & A", [G_A]),
                 "nest": ("X.A.h", "X", ["X := A SEQ \"!\"", G_A])}),
    ("macro", {"one": ("B.d", "B(/\\d/)", [G_B]), "seq": ("B.d", "B(/\\d/) SEQ B(/\\d/)", [G_B]),
               "and": ("B.d", "B(/\\d/) & B(/\\d/)", [G_B]), "nest": ("X.B.d", "X", ["X := B(/\\d/) SEQ \"!\"", G_B])}),
    ("part-label", {"one": ("x.h", "[x = A]", [G_A]), "seq": ("x.h", "[x = A] SEQ [x = A]", [G_A]),
                    "and": ("x.h", "[x = /(?<h>\\d)\\d/] & [x = /\\d(?<h>\\d)/]", []),
                    "nest": ("X.x.h", "X", ["X := [x = A] SEQ \"!\"", G_A])}),
    ("export-list", {"one": ("year", "[(=year) = i1]", [G_I1]),
                     "seq": ("year", "[(=year) = i1] SEQ [(=year) = i1]", [G_I1]),
                     "and": ("year", "[(=year) = i1] & [(=year) = i2]", [G_I1, G_I2]),
                     "nest": ("X.year", "X", ["X := [(=year) = i1] SEQ \"!\"", G_I1])}),
    ("argument", {"one": ("A.h", "B(A)", [G_A, G_ARG]), "seq": ("A.h", "B(A) SEQ B(A)", [G_A, G_ARG]),
                  "and": ("A.h", "B(A) & B(A)", [G_A, G_ARG]),
                  "nest": ("X.A.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_ARG])}),
]
READS = [("plain", "%s & (%s: \"3\")"), ("$", "(%s) SEQ $%s"), ("group", "%s & some((%s: \"3\"))"),
         ("index", "%s & (%s[1]: \"3\")")]
# The deciding sentences, quoted from the documents (piece tag, the words). Each is checked verbatim below.
S = {
    "lr-bare": ("core/labels/paths/label-reference", "a bare name is a label the definition itself writes"),
    "lr-src": ("core/labels/paths/label-reference", "A label not written in the text of the definition that "
               "references it is referenced with its source"),
    "flow-seq": ("core/labels/flow", "Across the sequence operator a name both parts surface is one label, the last "
                 "mention"),
    "reads": ("core/values/reads", "`$x` and `x:` never disagree"),
    "array": ("core/labels/labels-vs-captures/array-vs-passes", "The group questions (`some`, `count`, `occurs`) and "
              "the index `h[k]` read the array of a name's settings: every setting, in order"),
    "flow-and": ("core/labels/flow", "Across `&` a name both sides surface is an ambiguous reference: a compile error "
                 "where a condition or a `$` references it"),
    "flow-gq": ("core/labels/flow", "A group question over a name both sides of `&` surface reads both sides' "
                "settings"),
    "unordered": ("core/labels/paths", "the two sides of `&` are not ordered"),
    "one-use": ("core/labels/paths/one-use-read", "With ONE use, a plain read through a binding's prefix (`A.h`) is "
                "legal"),
    "bp-twice": ("core/labels/paths/binding-prefix", "a plain read through it with the binding used twice or more is "
                 "a compile error"),
    "bp-dollar": ("core/labels/paths/binding-prefix", "`$chars.ch` alike"),
    "bp-gq": ("core/labels/paths/binding-prefix", "a group question through it reads every use's settings, in order"),
    "bp-idx": ("core/labels/paths/binding-prefix", "The index `A.h[k]` through the prefix is in text order across "
               "sequenced uses; through uses joined by `&` it is a compile error for now"),
    "bp-nest": ("core/labels/paths/binding-prefix", "`X.D.h` is a compile error, D used alone in X"),
    "cp-once": ("core/labels/paths/call-prefix", "called once in the definition, a plain read through the name is "
                "legal"),
    "cp-twice": ("core/labels/paths/call-prefix", "called more than once, a plain read is the compile error saying "
                 "to label the call, and a group question reads every call's settings, in order"),
    "cp-same": ("core/labels/paths/binding-prefix", "a MACRO's name is a prefix too, under the same two rules"),
    "occ-and": ("lib/search/occurrences", "only the index `h[k]` across `&` is refused for now"),
    "paths-alone": ("core/labels/paths", "an unlabelled use carries the implicit label of the binding's name, protected"),
    "pl-last": ("core/labels/paths", "a part label mentioned more than once names its last mention where the "
                "reference is written"),
    "lr-dollar": ("core/labels/paths/label-reference", "`$x` reads alike"),
    "st3": ("core/labels/export", "through a public part label, the labels that part exports, by path"),
    "el-bare": ("core/labels/export/export-list", "the binding takes the listed labels of the part as labels of its "
                "own (exported; read bare inside it)"),
    "el-two": ("core/labels/export/export-list", "Two lists that name one label give the same label, the last "
               "mention"),
    "el-alias": ("core/labels/export/export-list", "A listed label is an alias of the part's label: the same "
                 "settings and array"),
    "ad-open": ("core/labels/paths/argument-default", "is the caller's read of that argument's labels (`A.d` in "
                "`B(A)`, a group written in place) its own local read, legal, or a compile error?"),
    "bp-text": ("core/labels/paths/binding-prefix", "\"Used more than once\" is counted in the TEXT of the "
                "definition the reference is written in"),
    "cA": ("core/labels/paths", "a call's label reaches no argument by the argument's name"),
}
# The cell table: (spelling, occurrence) -> per read kind (expected, sentence key); expected is "legal",
# "refused:<words the refusal must contain>" or "UNDECIDED".
REF_FLOW = "refused:core/labels/flow"
REF_BP = "refused:used 2 times"
REF_SRC = "refused:with its source"
REF_VIS = "refused:not visible through"
EXPECT = {
    ("bare", "one"): [("legal", "lr-bare")] * 2 + [("legal", "array")] * 2,
    ("bare", "seq"): [("legal", "flow-seq"), ("legal", "reads"), ("legal", "array"), ("legal", "array")],
    ("bare", "and"): [(REF_FLOW, "flow-and"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"), (REF_FLOW, "unordered")],
    ("bare", "nest"): [(REF_SRC, "lr-src")] * 4,
    ("binding", "one"): [("legal", "one-use")] * 2 + [("legal", "bp-gq"), ("legal", "bp-idx")],
    ("binding", "seq"): [(REF_BP, "bp-twice"), (REF_BP, "bp-dollar"), ("legal", "bp-gq"), ("legal", "bp-idx")],
    ("binding", "and"): [(REF_BP, "bp-twice"), (REF_BP, "bp-dollar"), ("legal", "bp-gq"),
                         ("refused:not ordered", "bp-idx")],
    ("binding", "nest"): [(REF_VIS, "bp-nest")] * 4,
    ("macro", "one"): [("legal", "cp-once")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("macro", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"), ("legal", "cp-same")],
    ("macro", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                       ("refused:not ordered", "occ-and")],
    ("macro", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("part-label", "one"): [("legal", "st3"), ("legal", "lr-dollar"), ("legal", "array"), ("legal", "array")],
    ("part-label", "seq"): [("legal", "pl-last"), ("legal", "lr-dollar"), ("legal", "array"), ("legal", "array")],
    ("part-label", "and"): [(REF_FLOW, "unordered"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"),
                            (REF_FLOW, "unordered")],
    ("part-label", "nest"): [("legal", "st3")] * 4,
    ("export-list", "one"): [("legal", "el-bare")] * 2 + [("legal", "el-alias")] * 2,
    ("export-list", "seq"): [("legal", "el-two"), ("legal", "el-two"), ("legal", "el-alias"), ("legal", "el-alias")],
    ("export-list", "and"): [(REF_FLOW, "flow-and"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"),
                             (REF_FLOW, "unordered")],
    ("export-list", "nest"): [("legal", "el-bare")] * 4,
    ("argument", "one"): [("UNDECIDED", "ad-open")] * 4,
    ("argument", "seq"): [(REF_BP, "bp-text"), (REF_BP, "bp-text"), ("UNDECIDED", "ad-open"), ("UNDECIDED", "ad-open")],
    ("argument", "and"): [(REF_BP, "bp-text"), (REF_BP, "bp-text"), ("UNDECIDED", "ad-open"),
                          ("refused:not ordered", "bp-idx")],
    ("argument", "nest"): [(REF_VIS, "cA")] * 4,
}
if s83("s15"):
    EXPECT[("bare", "and")][3] = ("legal", "unordered")
OCC = ["one", "seq", "and", "nest"]



GCNT = {"AGREE": 0, "DISAGREE": 0, "UNDECIDED": 0}
GBAD, GUND, GQMISS = [], [], []
ALLDOC_NOW = ws("\n".join(read(os.path.join(PRED, f)) for f in NEW))
for sp, occs in SPELL:
    for oc in OCC:
        R, P, B = occs[oc]
        base = tp(P, B)
        alpha = "37x!" if sp in ("argument",) or oc == "nest" else "37"
        for (rk, form), (exp, skey) in zip(READS, EXPECT[(sp, oc)]):
            expr = form % (P, R)
            tag_, words = S[skey]
            if ws(words) not in ALLDOC_NOW:
                GQMISS.append((sp, oc, rk, skey))
            vl, ve = ref(expr, B, "local"), ref(expr, B, "error")
            Pl = tp(expr, B)

            def verdict(msg, Pg):
                if msg is not None:
                    return "REFUSED (%s)" % msg
                hs = [t for t in pop(alpha, 5) if t and Pg.whole(t)][:2]
                fs = [t for t in pop(alpha, 5) if t and base is not None and base.whole(t) and not Pg.whole(t)][:1]
                wh = hs + fs
                sub = ("x" + hs[0]) if hs else "x"
                fa = " ".join(hs + fs) if hs else "x"
                return fmt(Pg, wh or ["x"], sub, fa)
            got_l = verdict(vl, Pl)
            if exp == "UNDECIDED":
                st = "UNDECIDED"
                Pe = tp(expr, B, "error")
                got = "(local) %s; (error) %s" % (got_l, verdict(ve, Pe))
                GUND.append((sp, oc, rk))
            else:
                got = got_l
                if exp == "legal":
                    ok = vl is None
                else:
                    ok = vl is not None and exp.split(":", 1)[1] in vl
                st = "AGREE" if ok else "DISAGREE"
                if not ok:
                    GBAD.append((sp, oc, rk, vl))
            GCNT[st] += 1
            print("   %-11s %-4s %-5s | `%s`%s | %s: \"%s\" | %s | %s" % (sp, oc, rk, expr, bt(B), tag_, words,
                                                                    exp, got[:260]))
            print("      -> %s" % st)
print("   GRID SUMMARY: %d cells: AGREE %d, DISAGREE %d, UNDECIDED %d; deciding sentences not found verbatim: %s" %
      (sum(GCNT.values()), GCNT["AGREE"], GCNT["DISAGREE"], GCNT["UNDECIDED"], GQMISS or "none"))
check("GRID", not GBAD and not GQMISS and sum(GCNT.values()) == 96,
      "%d cells (6 spellings x 4 occurrences x 4 read kinds): AGREE %d, DISAGREE %d %s, UNDECIDED %d %s; sentences "
      "missing %s" % (sum(GCNT.values()), GCNT["AGREE"], GCNT["DISAGREE"], GBAD[:3], GCNT["UNDECIDED"],
                      sorted(set("%s/%s/%s" % c for c in GUND)), GQMISS or "none"))

print("== SWEEP-TABLE: every printed three-mode line under argument-default's two candidates, both engines")
ROWS = {}
for ad in ("local", "error"):
    ARGDEF[0] = ad
    for f, ln, line_, a, pt, tail in sweep_lines():
        ROWS.setdefault((f, ln), [line_, a, pt, tail, {}])[4][ad] = sweep_one(line_, a, pt, tail)
ARGDEF[0] = "local"
envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
envo["PREDFIX83_ENGINE"] = "old"
oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                    env=envo, timeout=900).stdout
OLD_SW = {}
for l_ in oo.split("\n"):
    if l_.startswith("SW\t"):
        _, ad_, f_, ln_, st_, got_ = l_.split("\t", 5)
        OLD_SW.setdefault((f_, int(ln_)), {})[ad_] = (st_, got_)
print("   %d printed lines; the old engine (preddef's, without the fixes) ran %d" % (len(ROWS), len(OLD_SW)))

print("== AWAITS: every line marked \"(awaits argument-default)\": the printed answers under (local), refused under "
      "(error) where its program reads the argument's label outside the argument")
aw_bad, aw_n, aw_noread = [], 0, []
for k, (line_, a, pt, tail, st) in sorted(ROWS.items()):
    if "(awaits argument-default)" not in line_:
        continue
    aw_n += 1
    reads = re.search(r"\(\w[\w.]*: ", pt) is not None
    unmod = not reads and st["local"][0] == st["error"][0] == OLD_SW.get(k, {}).get("local", ("?",))[0] != "same"
    if (st["local"][0] != "same" and not unmod) or (reads and st["error"][0] != "REFUSED"):
        aw_bad.append((k, st["local"][0], st["error"][0]))
    if not reads:
        aw_noread.append(k)
    print("   %s:%d local %s, error %s%s" % (k[0], k[1], st["local"][0], st["error"][0],
                                            "" if reads else " (no read in the program: its label annotation awaits%s)"
                                            % ("; a library body this engine does not model, the old engine alike"
                                               if unmod else "")))
check("AWAITS", aw_n and not aw_bad, "%d marked lines; not (local same, error refused): %s; %d with no read" %
      (aw_n, aw_bad or "none", len(aw_noread)))

print("== UNMARKED: every unmarked printed line answers alike under both candidates (none silently awaits)")
if s83("s23"):
    k_ = next(k for k, v in ROWS.items() if "(awaits argument-default)" in v[0] and v[4]["error"][0] == "REFUSED")
    ROWS[k_][0] = ROWS[k_][0].replace("(awaits argument-default)", "")
um_bad = [(k, st["local"][0], st["error"][0]) for k, (line_, a, pt, tail, st) in ROWS.items()
          if "(awaits argument-default)" not in line_ and "(local)" not in line_[:30]
          and st["local"][0] == "same" and st["error"][0] != "same"]
check("UNMARKED", not um_bad, "%d unmarked lines reproduced under (local); moved under (error): %s" %
      (sum(1 for v in ROWS.values() if "(awaits" not in v[0] and v[4]["local"][0] == "same"), um_bad or "none"))

print("== SWEEP: every printed three-mode line, old engine against the fixed one, both candidates; no printed answer "
      "moves unless listed under ANSWERS_CHANGED")
ANSWERS_CHANGED = {          # program text -> the ruling or reading that carries the move
    "[a = A] SEQ A & (A.h: <5)": "A5, the manager's reading (record: the r83 dispositions entry): a binding's own "
                                 "name reaches its UNLABELLED uses only, a labelled use not counted; the old engine "
                                 "refused it (\"A is used 2 times here\"), the fixed one reads the unlabelled use",
}
NEW_SW = {k: dict(v[4]) for k, v in ROWS.items()}
if s83("s16"):
    k_ = next(k for k, v in ROWS.items() if "(`pub & (pub.h: <5)`, pub := `[a = A] SEQ" in v[0])
    l_ = ROWS[k_][0].replace("pub := `[a = A] SEQ", "pub := `A SEQ")
    a_ = answer_part(l_)
    t_ = l_[l_.index(a_) + len(a_):]
    NEW_SW[k_]["local"] = sweep_one(l_, a_, re.search(r"`([^`]*)`", t_).group(1), t_)
moved = []
for k, sts in NEW_SW.items():
    for ad in ("local", "error"):
        o = OLD_SW.get(k, {}).get(ad, ("?", ""))
        n = sts[ad]
        if o[0] == "?":
            continue
        if (o[0], o[1] if o[0] in ("same", "DIFF") else "") != (n[0], n[1] if n[0] in ("same", "DIFF") else ""):
            pt = ROWS[k][2]
            if pt not in ANSWERS_CHANGED:
                moved.append((k, ad, o[0], n[0]))
cnt = {}
for v in NEW_SW.values():
    cnt[v["local"][0]] = cnt.get(v["local"][0], 0) + 1
ocnt = {}
for v in OLD_SW.values():
    ocnt[v.get("local", ("?",))[0]] = ocnt.get(v.get("local", ("?",))[0], 0) + 1
check("SWEEP", len(OLD_SW) == len(NEW_SW) and not moved,
      "%d printed lines (old engine %d: %s); the fixed engine (local): %s; moved and not listed: %d %s; ANSWERS_CHANGED "
      "%d" % (len(NEW_SW), len(OLD_SW), ", ".join("%s %d" % kv for kv in sorted(ocnt.items())),
              ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(moved), moved[:6], len(ANSWERS_CHANGED)))
for k, ad, o, n in moved:
    print("   MOVED %s:%d (%s) %s -> %s: %s" % (k[0], k[1], ad, o, n, ROWS[k][2][:120]))
for pt, why in sorted(ANSWERS_CHANGED.items()):
    print("   ANSWER CHANGED `%s`: %s" % (pt, why))

print("== NULLABLE: EVID-4's known limit: no program the checks ran has a loop whose body can match empty")


def nullable(n):
    t = n[0]
    if t in ("lit", "cls", "dot"):
        return False
    if t == "seq":
        return all(nullable(x) for x in n[1])
    if t == "alt":
        return any(nullable(x) for x in n[1])
    if t == "grp":
        return nullable(n[2])
    if t == "rep":
        return n[2] == 0 or nullable(n[1])
    if t == "atomic":
        return nullable(n[1])
    return True


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
if s83("s18"):
    checked.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nl = [(e, b) for e, b, nd in checked if loops_nullable(nd, [])]
check("NULLABLE", not nl, "%d programs run by the checks above, walked node by node: %d with a loop whose body can "
      "match empty%s" % (len(checked), len(nl), (": %s" % nl[:4]) if nl else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line (a red whose content changes under an unchanged name fails here)")
LANES = os.path.normpath(os.path.join(HERE4, ".."))
PD_ = "preddef's SUCCESSOR, which declared it, and "
SUPERSEDED = {                # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
    "preddef": {
        "MARKS": ("346b15f9abc4", "MARKS here: its markers 'statement 3', 'call-prefix', 'form caveat' and 'errors row' "
                                  "are texts this lane rewrote (review r83 D3/D7, A6/D10, D14, D12); MARKS here finds "
                                  "the new texts"),
        "UNMARKED": ("7dd755e4fe4e", "UNMARKED and TWOUSE here: the moved line is core/labels/paths/argument-default's "
                                     "new \"Both uses, (local)\", a candidate's own line, which differs under (error) "
                                     "by design (review r83 A3)")},
    "predfix82": {
        "MARKS": ("84df29d69537", "MARKS here (D17): its ANS-2a, ANS-2b and RULING-9 markers are the open idiom-confirm "
                                  "texts, now ruled by default-export (one-use-read re-written); ANS-1 as preddef "
                                  "declared it"),
        "SUCCESSOR": ("7af0ee27f19f", "SUCCESSOR here: it re-runs the same six models, each red declared below")},
    "predcall": {
        "DOC": ("3d2c11f65046", PD_ + "MACRO there (the line renamed under default-export), unchanged"),
        "PREDREF": ("16e7aa734111", PD_ + "predfix82's SUCCESSOR (it reads predref's last line), unchanged"),
        "SCAN": ("a7c666fbda78", "GRID and LISTCALL here: one span more than preddef declared, the new refusal line's "
                                 "`[(=d) = B(A)] & (d: <5)`, whose bare `d` is an export list's own label (review "
                                 "r83 D7; its old SCAN knows no lists); the 32 spans before it as predfix82 declared")},
    "predref": {
        "DOC": ("04afb36e8d23", PD_ + "ATOMIC and SWEEP there, unchanged"),
        "MARKS": ("8ca3596581eb", PD_ + "predcall's MARKS, unchanged"),
        "SCAN": ("e69ff326bdc7", "GRID and LISTCALL here: the same one new span as predcall's SCAN (an export list's "
                                 "own `d`, review r83 D7)")},
    "predbound": {"DOC": ("197284e95806", PD_ + "predfix82's REPRINT, unchanged")},
    "predfix77": {"TRACEBACK": ("455b59c946bc", PD_ + "predfix82's REPRINT and predbound's checks (the `chars` body "
                                                       "reader), unchanged")},
    "predarr": {"TRACEBACK": ("ce43d48c7e37", PD_ + "predfix82's REPRINT and predref's HITS, unchanged")},
    "predscope": {
        "NAMES": ("232a77f8ed09", PD_ + "predbound's bound-condition checks, unchanged"),
        "CLOSEDB": ("5d36005cbb1e", PD_ + "predfix82's REPRINT, unchanged"),
        "DOC": ("c71d491c3425", PD_ + "predfix82's REPRINT, unchanged")},
}
MODELS = ["preddef", "predfix82", "predcall", "predref", "predbound", "predfix77", "predarr", "predscope"]
if s83("s17") and SUPERSEDED.get("preddef"):
    SUPERSEDED["preddef"].pop(next(iter(SUPERSEDED["preddef"])), None)
procs = {}
for mname in MODELS:
    env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")}
    procs[mname] = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(LANES, mname + "_evidence",
                                                                               mname + "_model.py")],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
succ_bad = []
for mname, pr in procs.items():
    try:
        out, _ = pr.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        pr.kill()
        out = "TIMEOUT"
    lines_ = out.rstrip("\n").split("\n")
    last = lines_[-1]
    mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
    reds = {}
    if mm:
        for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
            fl = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                       re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
            reds[r] = fl
    else:
        reds["TRACEBACK"] = last
    decl = SUPERSEDED.get(mname, {})
    print("   %-10s last line: %s" % (mname, last[:120]))
    for r, fl in sorted(reds.items()):
        dg = hashlib.sha256(fl.encode()).hexdigest()[:12]
        d = decl.get(r)
        if d is None:
            succ_bad.append((mname, r, "UNDECLARED"))
            print("      %s [%s] UNDECLARED: %s" % (r, dg, fl[:200]))
        elif d[0] != dg:
            succ_bad.append((mname, r, "CONTENT CHANGED"))
            print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fl[:200]))
        else:
            print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
            print("         its FAIL line: %s" % fl[:220])
    gone = sorted(set(decl) - set(reds))
    if gone:
        print("      declared but green now: %s" % gone)
check("SUCCESSOR", not succ_bad, "%d earlier models re-run, each last line read; every red declared superseded with "
      "an unchanged FAIL line: %s" % (len(procs), "yes" if not succ_bad else succ_bad))

print("== QUOTES: every owner sentence this lane quotes occurs in the record and the documents; every cited title is one")
QQ = ["I agree with your interpretation. I note that captures can have no label.",
      "So the types of reference are: binding, label, macro argument, capture group name, ?",
      "Nothing missed I see.",
      "Agree caveat bindings used to scope labels (A.a: 8)",
      "The textually visible rules solves a problem of a label from a binding reference hiding another binding",
      "default-export: protected",
      "[A ] (A alone, default) also makes the labels protected but with different access locally",
      "4. A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an "
      "expression",
      "a part used bare is available locally as `A.h` but exports nothing",
      "`.` has one meaning: a field of the map interface of the thing on its left"]
TT = ["2026-11-22 OWNER, on the two-kind view: \"I agree with your interpretation. I note that captures can have no "
      "label.\"",
      "2026-11-22 OWNER, a question: the kinds of reference (\"binding, label, macro argument, capture group name, ?\")",
      "2026-11-22 OWNER, on the kinds of reference: \"Nothing missed I see\"; can some be COMBINED",
      "2026-11-22 OWNER, an observation: the textually-visible rule solves a label from a used binding hiding another "
      "binding",
      "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on "
      "default-export (no owner words)",
      "2026-11-22 OWNER RULING — default-export: protected",
      "2026-11-22 OWNER, on the two name spaces: \"Agree caveat bindings used to scope labels (A.a: 8)\"",
      "2026-11-22 OWNER, discussing the analogy: `B := A & A`, `C := B & (B.a: 9)`: \"here B.a is always an error\""]
if s83("s19") and QQ:
    QQ[0] = QQ[0] + " (altered)"
DOCS_NOW = {f: read(os.path.join(PRED, f)) for f in NEW}
ALLNOW = "\n".join(DOCS_NOW.values())
q_miss = [q for q in QQ if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOW)]
heads = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_miss = [t for t in TT if not any(h.startswith(ws(t)) for h in heads) or ws(t.split(" (")[0]) not in ws(ALLNOW)]
check("QUOTES", QQ and not q_miss and not t_miss, "%d quoted sentences in the record and the documents, missing: %s; "
      "%d record titles cited, not a title or not cited: %s" % (len(QQ), q_miss or "none", len(TT), t_miss or "none"))

print("== MARKS: each disposition where it landed")
MK = [("A1", "core.md", "From outside, a chain written in a binding: modes: a compile error"),
      ("A2", "core.md", "Through a call that uses its argument alone: modes: a compile error"),
      ("A3", "core.md", "except where a body uses its argument both alone and labelled"),
      ("A3", "core.md", "The cost of (error) across the provided library"),
      ("A4", "core.md", "A read from OUTSIDE sees the binding's EXPORTED settings only"),
      ("A5", "core.md", "The name reaches the UNLABELLED uses only"),
      ("A6", "core.md", "a call exports what its body exports (core/labels/export statement 3)"),
      ("A7", "core.md", "Bare `$h` and the index across `&`: modes: a compile error"),
      ("A8", "core.md", "when's \"Labels the test sets are visible in then\""),
      ("A8", "library.md", "Then reads the test's labels across two arguments the body uses alone"),
      ("A8", "core.md", "where the body uses it alone it awaits argument-default"),
      ("D1", "core_details.md", "REVIVED by default-export (2026-11-22): it is the rule now"),
      ("D2", "core.md", "default-export narrows \"the same label behavior\""),
      ("D2", "core.md", "default-export narrows it too"),
      ("D3", "core.md", "An UNLABELLED use carries the implicit label of the binding's name"),
      ("D4", "core.md", "A part label over an EXPRESSION"),
      ("D4", "core.md", "A macro's parameter is not a part whose labels the body may name"),
      ("D4", "core.md", "Its library face (the manager's)"),
      ("D5", "library.md", "`month_numbered.mname` is a compile error"),
      ("D6", "core.md", "the manager's reading (c)"),
      ("D6", "core_details.md", "(class: AGREEMENT) \"Agree caveat bindings used to scope labels (A.a: 8)\""),
      ("D7", "core.md", "its OWN names (a group in its literals, a part label it writes, a label an export list it writes takes"),
      ("D8", "core.md", "(core/labels/export, statement 5) (awaits capture-export)"),
      ("D8", "core.md", "At the top nothing is outside"),
      ("D9", "core.md", "the names the map exports"),
      ("D9", "parked_details.md", "A PART USED ALONE EXPORTS NOTHING"),
      ("D10", "core.md", "visibility goes by export, not by role"),
      ("D11", "core.md", "so it fires on a label written in the definition against a binding of the same name"),
      ("D11", "parked.md", "what is left of hiding"),
      ("D12", "core.md", "an export list naming a label the part does not export"),
      ("D13", "core.md", "a `_` PART LABEL is protected"),
      ("D14", "core.md", "a metadata field alike, `w.index`"),
      ("D15", "core.md", "`[=A]`, read `[A = A]`"),
      ("D16", "core.md", "The cross case, a binding list over a part's labels"),
      ("D16", "core.md", "Two lists that name one label give the same label, the last mention"),
      ("D17", "core.md", "[core/labels/paths/one-use-read]   ruled 2026-11-22"),
      ("D18", "core.md", "the part's own prefix (`isodate.year`)"),
      ("NAMES", "core.md", "[core/modules/names]   reading 2026-11-22")]
if s83("s20") and MK:
    MK[0] = (MK[0][0], MK[0][1], MK[0][2] + " (planted)")
mk_miss = [i for i, f, sub in MK if ws(sub) not in ws(DOCS_NOW.get(f, ""))]
check("MARKS", MK and not mk_miss, "%d dispositions found where they landed; missing: %s" % (len(MK), mk_miss or "none"))

print("== DOC: every line this model formats occurs verbatim in the documents")
DLN = list(LINES)
if s83("s21") and DLN:
    DLN[0] = (DLN[0][0], DLN[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_miss = [(t, L) for t, L in DLN if ws(L) not in ws(ALLNOW)]
for t, L in d_miss:
    print("   MISSING [%s] %s" % (t, L))
check("DOC", DLN and not d_miss, "%d lines; missing: %d" % (len(DLN), len(d_miss)))

failed = [n for n, ok in RESULTS if not ok]
print("predfix83_model: %d checks, %d failed%s" % (len(RESULTS), len(failed),
                                                    (" (%s)" % ", ".join(failed)) if failed else ""))
sys.exit(1 if failed else 0)
