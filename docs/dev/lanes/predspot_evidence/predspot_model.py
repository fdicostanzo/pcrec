#!/usr/bin/env python3
# Lane predspot (2026-11-22): the evidence for folding five owner rulings of 2026-11-22 into the predicate
# documents. GROUP 1 (labels): argument-default ("for me this is an error"), wrapper-export ("agree (a)"),
# transform-export ("yes"). GROUP 2 (flags): program-options ("yes"), hole-flags ("yes to all"). The manager's
# readings of the brief tested, each by a check. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD, GROUP 1 (the LABEL engine). Lane predfix83's model is LOADED unchanged: predfix83_model.py is executed
# up to its line "the checks" (it loads preddef's, which loads predfix82's, predcall's, predref's and predbound's
# lowerer and matcher). Its plants are cleared. The FIXES below then replace, in the loaded engine, these parts:
#   RULED     argument-default is ruled (an error): the loaded candidate switch is fixed at "error".
#   TEMPLATE  an argument is a template, not a spot (his reason): the names an argument's own text writes (its
#             groups, a part label written on it) are moved to a scope of the argument wherever the body uses
#             it, alone or labelled, so a read written inside the argument still sees them (reading (c)) and the
#             caller's reads outside it do not (readings (a), (b)). A binding's own prefix (`A.d`) moves only
#             where the body uses the argument alone (the ruling); where the body labels the spot or passes the
#             labels on, `A.d` reaches A's `d` (closed-argument, settled strictly).
#   SPOTLIST  an export list on a spot (`[(=) = rx]`, wrapper-export, transform-export): the body takes the
#             argument's EXPORTED labels as labels of its own. What an argument exports: a single binding or call
#             exports what it exports; any other argument what its own text writes (a part used alone in it:
#             nothing, as core/labels/paths says of a part label over an expression).
#   SPOTGROUP a label-only group written around a hole holding a parameter (`(?<:hit>${x})`) is a spot the body
#             labels: it is lowered as the part label `[hit = x]` (a label, no capture; reading (d)).
#   OWNTEXT   label-reference's "the definition's own names" leaves out the text of a call's arguments (a
#             template is not a piece of the pattern).
#   REASON    a refusal of a read of a template's label names its rule: core/labels/paths/argument-default.
#   LIBRARY   the provided bodies `peek`, `list_of`, `contains`, `startsWith`, `endsWith`, `anchored` and
#             `padded(rx)` are read from library.md as macros (the loaded engine read `atomic`, `hits`,
#             `occurrences`, `rx.repeat` already, from the same file).
# METHOD, GROUP 2 (the FLAG engine, written here): a program is FILES, a program file and a library file, each an
# ordered list of `@options(..)` statements and bindings; the program's expression is in the program file. Each
# literal is parsed with the flags in force where it is WRITTEN (its file's options from the statement on), then
# its own flags (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`), PCRE's scope inside it. At a hole the inserted literal
# starts from ITS OWN file's options; under the NEW rule (hole-flags) only an EXPLICIT `i` / `-i` in force at the
# hole replaces its `i`; under the OLD rule (flags-scope, 2026-11-19) `i`, `m`, `s` in force at the hole replace
# its own. `x` and `n` are read per literal (`n`: a plain `( )` is no capture). The matcher is the loaded one
# (predbound's node set), with `^` / `$` added (multiline or not).
#
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. The check NULLABLE walks every
# program this model's checks run for one and fails if found. Not modelled either (said where it matters): `U`,
# `xx` and `J` in the flag engine, a complement inside a hole, `when` (its body's `NOT peek(test)`), `quoted`.
#
# Run (W = the worktree; any cwd):  timeout 2400 python3 -I -B W/docs/dev/lanes/predspot_evidence/predspot_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDSPOT_ENGINE=old runs the label engine as it stood (predfix83's, candidate (local), the provided bodies of
# the starting commit) over the documents of the starting commit: SWEEP's control; it prints one table.
# PREDSPOT_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# PREDSPOT_SABOTAGE=all runs every plant in turn (a subprocess each) and prints the table predspot_sabotage.out holds.
# PREDSPOT_LIGHT=1 skips SWEEP's old-engine run and SUCCESSOR (the plant runner sets it for plants not aimed there).
#   (the plants are listed with their checks at the end of this header block, PLANTS below)
import hashlib
import itertools
import os
import re
import subprocess
import sys

HERE5 = os.path.dirname(os.path.abspath(__file__))
P83 = os.path.join(HERE5, "..", "predfix83_evidence", "predfix83_model.py")
SABS = set(x for x in os.environ.get("PREDSPOT_SABOTAGE", "").split(",") if x)
ENGINE_S = os.environ.get("PREDSPOT_ENGINE", "new")
LIGHT = os.environ.get("PREDSPOT_LIGHT") == "1"
START_S = "75d2318bd"                                        # this lane's starting commit (lane/pred-rev28)
for v in list(os.environ):
    if v.endswith("_SABOTAGE") and v != "PREDSPOT_SABOTAGE" or v.endswith("_ENGINE") and v != "PREDSPOT_ENGINE":
        os.environ.pop(v, None)


def ss(n):
    return n in SABS


_src5 = open(P83, encoding="utf-8").read()
_cut5 = re.search(r"^# =+ the checks$", _src5, re.M).start()
_file_save = __file__
__file__ = P83                                               # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src5[:_cut5], P83, "exec"), globals())         # noqa: S102  (predfix83's definitions, unchanged)
__file__ = _file_save
for _s in (SAB83, SABD, SAB82, SABC, SABR, SAB):
    _s.clear()

L83 = dict(lower_atom=lower_atom, lower_list=lower_list, prog=prog, lower_literal=lower_literal,
           base_binds=base_binds, own_labels=own_labels, relocate=relocate)


def git_show_s(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (START_S, rel)], capture_output=True, text=True,
                          check=True).stdout


DOCF = ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md")
OLDS = {f: git_show_s("docs/design/predicates/" + f) for f in DOCF}
NOWS = {f: read(os.path.join(PRED, f)) for f in DOCF}

# ---- LIBRARY: the provided bodies, read from library.md (the starting commit's for the old engine)
LIBB_SRC = OLDS["library.md"] if ENGINE_S == "old" else NOWS["library.md"]


def lb(pattern):
    mm = re.search(pattern, ws(LIBB_SRC))
    assert mm, pattern
    return mm.group(1)


LIBMACROS = {
    "peek": ([("A", None)], lb(r"`peek\(A\) := (/.*?/)`")),
    "atomic": ([("X", None)], lb(r"`atomic\(X\) := (/.*?/)`")),
    "list_of": ([("X", None), ("sep", None)], lb(r"`list_of\(X, sep = S\)` is the separated list `(/.*?/)`")),
    "contains": ([("s", None)], lb(r"`contains\(s\)` is the plain gap body `(/.*?/)`")),
    "startsWith": ([("s", None)], lb(r"`startsWith\(s\)` is the plain gap body `(/.*?/)`")),
    "endsWith": ([("s", None)], lb(r"`endsWith\(s\)` is the plain gap body `(/.*?/)`")),
    "anchored": ([("s", None)], lb(r"`anchored\(s\)` is the plain macro `(/.*?/)`")),
    "padded": ([("rx", None)], lb(r"`padded\(rx\) := (/.*?/)`")),
    "hits": ([("r", None)], lb(r"`hits\(r\) := (/.*?/)`")),
}
LIB_REPEATS = re.findall(r"`repeat\((x(?:, \w+)+)\) :=\s+(/.*?/)`", ws(LIBB_SRC))
LIB_OCC = re.search(r"`occurrences\(x, min = \d+\)` is the lazy-gap loop `(/.*?/)`", LIBB_SRC).group(1)
# list_of's separator parameter is `sep` in the call and `S` in the body text: the body names it `S`
LIBMACROS["list_of"] = ([("X", None), ("sep", None)], LIBMACROS["list_of"][1].replace("${S}", "${sep}")
                        .replace("= S]", "= sep]"))
if ss("s9"):                                                 # PLACES's plant: one provided body loses its list
    LIBMACROS["peek"] = ([("A", None)], "/(?=${A})/")


def base_binds():                                            # noqa: F811
    L83["base_binds"]()
    for nm, (heads, body) in LIBMACROS.items():
        MACROS[nm] = [(heads, body)]
    MACROS["occurrences"] = [([("x", None), ("min", "0")], LIB_OCC)]
    MACROS["rx.repeat"] = [([(h.strip(), None) for h in heads.split(",")], body) for heads, body in LIB_REPEATS]
    TPL.clear()


# ================================================================== the FIXES (lane predspot)
TPL = set()                   # bases moved as a template's own names (REASON reads it)
TPL_TAG = [None]              # the argument scope of the last argument lowered


def _walk_tag(x, outer, tag):
    if isinstance(x, str):
        mm = SCOPE_STR.match(x)
        if mm and set(mm.group(2).split(",")) & outer:
            return "%s@%s" % (mm.group(1), ",".join(s + tag if s in outer else s for s in mm.group(2).split(",")))
        return x
    if isinstance(x, tuple):
        return tuple(_walk_tag(y, outer, tag) for y in x)
    if isinstance(x, list):
        return [_walk_tag(y, outer, tag) for y in x]
    return x


def relocate_tpl(text, caller, a, b):
    """TEMPLATE for an argument the body uses labelled: its own names (plain, and the paths of a part label
    written on it) move to the argument's scope; a binding's own prefix (`A.d`, kind "use") stays."""
    ARGSEQ[0] += 1
    tag = "~a%d" % ARGSEQ[0]
    outer = set(caller.scopes)

    def mv(ps):
        out = []
        for bs, sc in ps:
            if ("." not in bs or PART_KIND.get(bs, "part") == "part") and not ss("s2"):
                if set(sc) & outer:
                    TPL.add(bs.split(".")[0])
                sc = [x + tag if x in outer else x for x in sc]
            out.append((bs, sc))
        return out
    text = map_groups(text, mv)
    for i in range(a, b):
        sc, nm = NAMED[i]
        if sc in outer:
            NAMED[i] = (sc + tag, nm)
    for n in node_refs(text):
        nd = NODES.get(n)
        if nd and nd[0] != "setv":
            NODES[n] = _walk_tag(nd, outer, tag)
    ARG_OWN[tag] = set(outer)
    TPL_TAG[0] = (tag, caller)
    return text


def relocate(text, outer, a, b, keep_reads):                  # noqa: F811
    """predfix83's (error) relocation (an argument the body uses alone), recording the moved names for REASON."""
    for ps in all_groups(text):
        for bs, sc in ps:
            if set(sc) & set(outer):
                TPL.add(bs.split(".")[0])
    r = L83["relocate"](text, outer, a, b, keep_reads)
    return r


def lower_atom(expr, ctx):                                   # noqa: F811
    e = expr.strip()
    if e in ctx.params and ctx.labelled and not re.fullmatch(r"\d+", ctx.params[e][0]):
        a = len(NAMED)
        text = _lower_atom_pd(e, ctx)
        return relocate_tpl(text, ctx.params[e][1], a, len(NAMED))
    return L83["lower_atom"](expr, ctx)


def single_arg(t):
    t = t.strip()
    if any(len(split_top(t, op)) > 1 for op in (" | ", " & ", " SEQ ")):
        return False
    call = parse_call(t)
    return t in BINDS or bool(call and call[0] in MACROS)


def lower_list(mm, ctx):                                     # noqa: F811
    """SPOTLIST: an export list over a parameter takes the argument's EXPORTED labels."""
    op = mm.group(2).strip()
    if op not in ctx.params or ss("s5"):
        return L83["lower_list"](mm, ctx)
    pairs, allx, out = list_pairs(mm.group(1))
    lc = ctx.sub()
    lc.labelled = True
    arg_text, caller = ctx.params[op]
    inner = lower(op, lc)
    tag, _ = TPL_TAG[0]
    cur = caller.cur + tag
    exact = [s + tag for s in caller.scopes]
    one = single_arg(arg_text) or arg_text.strip() in caller.params
    exported = set()
    for ps in all_groups(inner):
        for b, sc in ps:
            if "." in b or private(b) or "%s@%s" % (b, ",".join(sc)) in CLOSED_PARTS:
                continue
            if (one and cur in sc) or sc == exact or (ss("s6") and cur in sc):
                exported.add(b)
    for new, old in pairs:
        if old not in exported:
            raise CompileError("`%s` is not a label the part exports (export-list: only an exported label is listed)"
                               % old)
    names = list(pairs)
    if allx:
        names += [(b, b) for b in sorted(exported) if b not in out and (b, b) not in pairs]
    ctx.held.update(n for n, _ in names)
    if not ss("s6"):
        ARG_PARTS.update(all_parts(inner))                   # the template's own parts: no later prefix takes them

    def fix(ps):
        keep = list(ps)
        for b, sc in ps:
            if b in exported and ((one and cur in sc) or sc == exact or (ss("s6") and cur in sc)):
                for new, old in names:
                    if old == b:
                        keep.append((new, list(ctx.scopes)))
        return keep
    return "(?:%s)%s" % (map_groups(inner, fix), mm.group(3))


SPOT = re.compile(r"\(\?<:(\w+)>\$\{\s*(\w+)\s*\}\)")


def lower_literal(rx, ctx):                                  # noqa: F811
    """SPOTGROUP: `(?<:hit>${x})`, x a parameter, is the spot the body labels: `${[hit = x]}`."""
    if ctx.params and not ss("s7"):
        rx = SPOT.sub(lambda m_: ("${[%s = %s]}" % (m_.group(1), m_.group(2))) if m_.group(2) in ctx.params
                      else m_.group(0), rx)
    return L83["lower_literal"](rx, ctx)


def close_paren(t, i):
    depth, j, in_rx, in_q = 0, i, False, False
    while j < len(t):
        c = t[j]
        if in_rx:
            if c == "\\":
                j += 2
                continue
            if c == "/":
                in_rx = False
        elif in_q:
            if c == '"':
                in_q = False
        elif c == "/":
            in_rx = True
        elif c == '"':
            in_q = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return len(t) - 1


def strip_args(t):
    """OWNTEXT: the text of a definition with every macro call's arguments blanked."""
    out, i = [], 0
    for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", t):
        if mm.start() < i or mm.group(1) not in MACROS:
            continue
        j = close_paren(t, mm.end() - 1)
        out.append(t[i:mm.end()])
        out.append(" " * (j - mm.end()))
        i = j
    out.append(t[i:])
    return "".join(out)


def own_labels(text):                                        # noqa: F811
    return L83["own_labels"](text if ss("s4") else strip_args(text))


AD_RULE = "core/labels/paths/argument-default"


def prog(expr, binds=(), **opts):                            # noqa: F811
    """RULED: argument-default fixed at (error); REASON: a template's label named by its rule."""
    TPL.clear()
    ARGDEF[0] = "local" if (ENGINE_S == "old" or ss("s1")) else "error"
    try:
        return L83["prog"](expr, binds, **opts)
    except CompileError as e:
        mm = re.search(r"`([\w.]+)`", str(e))
        if mm and mm.group(1).split(".")[0] in TPL and ENGINE_S != "old":
            raise CompileError("`%s`: a label of an argument, which is a template and not a spot in the pattern (a "
                               "compile error, %s)" % (mm.group(1), AD_RULE))
        raise


if ENGINE_S == "old":
    globals().update(lower_atom=L83["lower_atom"], lower_list=L83["lower_list"], lower_literal=L83["lower_literal"],
                     own_labels=L83["own_labels"], relocate=L83["relocate"])


# ================================================================== the sweep keys (SWEEP; also the old engine's table)
if ENGINE_S == "old":
    NEW.clear()
    NEW.update(OLDS)                                         # the starting commit's documents
FLAGTAIL = re.compile(r"@options|library file|program file")


def sw_key(f, line, pt, tail):
    """A printed line's identity across a re-flow: its program, its bindings and its three texts."""
    try:
        wh, sr, fa = modes_of(line)
    except Exception:                                        # noqa: BLE001
        wh, sr, fa = ["?"], "?", "?"
    binds = tuple(re.findall(r"([\w.]+(?:\([\w, =]*\))?) := `([^`]*)`", tail))
    return (pt, binds, tuple(wh), sr, fa)


def sw_table():
    out = {}
    for f, ln, line_, a, pt, tail in sweep_lines():
        if FLAGTAIL.search(tail):
            continue                                         # a flag line: FSWEEP's
        st, got = sweep_one(line_, a, pt, tail)
        out.setdefault(sw_key(f, line_, pt, tail), []).append((f, ln, st, got if st in ("same", "DIFF") else got[:160]))
    return out


if ENGINE_S == "old":
    for k, vs in sw_table().items():
        for f, ln, st, got in vs:
            print("SW\t%s\t%s\t%d\t%s\t%s" % (repr(k), f, ln, st, got))
    sys.exit(0)

# ================================================================== the checks
LINES.clear()
RUN.clear()
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def ref(expr, binds=()):
    try:
        prog(expr, list(binds))
        return None
    except CompileError as e:
        return str(e)


def tp(expr, binds=()):
    try:
        return prog(expr, list(binds))
    except CompileError:
        return None


def wdiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t)) if Pg is not None else -1


def bt(binds):
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def dl(label, expr, binds, Pg, wh, sr, fa, tag, tail=""):
    return doc_line("%s%s (`%s`%s)%s" % ((label + ": ") if label else "", fmt(Pg, wh, sr, fa), expr, bt(binds), tail),
                    tag)


def has(msg, *subs):
    """REASON: a refusal counts only when its message names the expected rule."""
    return msg is not None and all(s in msg for s in subs)


def full(rx):
    return lambda t: re.fullmatch(rx, t) is not None


AD = "A := /(?<d>\\d)/"
ADIG = "A := [d = rx.digits]"
ADR = ("a template and not a spot in the pattern", AD_RULE)
NOTVIS = ("is not visible through",)

print("== CONTROL: the loaded matcher against python `re`")
QD = pop("37!", 3)
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("identity(A)", [AD, "identity(x) := /${[(=) = x]}/"]), QD),
           answers(Re(r"\d" if not ss("s3") else r"\d!?"), QD))
check("CONTROL", (c1, c2) == ((0, 0, 0),) * 2, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; "
      "`identity(A)` against `\\d` %s over %d texts" % (c1, c2, len(QD)))

print("== ARGNAME (the ruling): the caller's read of an argument's label, the body using it alone, is refused")
r_n1 = ref("B(A) & (A.d: <5)", [AD, "B(rx) := /${rx}xx/"])
r_n2 = ref("C", ["C := B(A) & (A.d: <100)", ADIG, "B(rx) := /${rx}xx/"])
r_n3 = ref("B(A) & (A.d: <5)", [AD, "B(rx) := /${rx}-(?<d>\\d)/"])
r_n4 = ref("pair(A) & (A.d: <5)", [AD, "pair(p) := /${p},${p}/"])
P_n5 = tp("B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"])
first_lt5 = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[0]) < 5     # noqa: E731
DG = pop("37-", 3)
if P_n5 is not None:
    dl("A's own d, the body labelling the spot (case 2)", "B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"],
       P_n5, ["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", "core/labels/paths/call-prefix")
    dl("Visible through the call", "B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"],
       P_n5, ["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", "core/labels/paths/closed-argument")
TU = ["B(rx) := /${[p = rx]}-${rx}/", AD]
P_n6 = tp("B(A) & (A.d: <5)", TU)
if P_n6 is not None:
    dl("Both uses", "B(A) & (A.d: <5)", TU, P_n6, ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9",
       "core/labels/paths/argument-default")
check("ARGNAME", all(has(r, *ADR) for r in (r_n1, r_n2, r_n3, r_n4)) and wdiff(P_n5, first_lt5, DG) == 0 and
      wdiff(P_n6, first_lt5, DG) == 0,
      "refused naming argument-default: `B(A) & (A.d: <5)` B alone %s; his example 1 `C := B(A) & (A.d: <100)` %s; "
      "the body with its own d %s; `pair` using it twice alone %s; the spot labelled `[p = rx]`: `A.d` legal, "
      "against \"the FIRST digit under 5\" differing %d; both uses (alone and labelled): the labelled spot's, "
      "differing %d, over %d texts" % (has(r_n1, *ADR), has(r_n2, *ADR), has(r_n3, *ADR), has(r_n4, *ADR),
                                       wdiff(P_n5, first_lt5, DG), wdiff(P_n6, first_lt5, DG), len(DG)))
print("   refusal: %s" % r_n1)

print("== ARGLABEL (reading (a)): a part label written ON an argument labels a template: refused")
r_a1 = ref("C", ["C := B([a = A]) & (a.d: <100)", ADIG, "B(rx) := /${rx}xx/"])
r_a2 = ref("atomic([ab = B | A]) & (ab.l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
r_a3 = ref('rx.repeat([a = rx.digit], min = 1) & (a: "3")')
r_a4 = ref("B([a = A]) & (a.d: <5)", [AD, "B(rx) := /${[(=) = rx]}xx/"])
P_a5 = tp("B([a = A]) & (B.a.d: <5)", [AD, "B(rx) := /${[(=) = rx]}xx/"])
check("ARGLABEL", all(has(r, *ADR) for r in (r_a1, r_a2, r_a3, r_a4)),
      "refused naming argument-default: `B([a = A]) & (a.d: ..)` %s; `atomic([ab = B | A]) & (ab.l: <20)` %s; "
      "`rx.repeat([a = rx.digit], min = 1) & (a: \"3\")` %s; through a body that lists the spot, the caller's own "
      "`a.d` %s (the call's path `B.a.d`: %s)" % (has(r_a1, *ADR), has(r_a2, *ADR), has(r_a3, *ADR), has(r_a4, *ADR),
                                                  "legal" if P_a5 is not None else "refused"))
print("   refusal: %s" % r_a2)

print("== INPLACE (reading (b)): a group written in an argument in place is not the caller's; the body's is `B.d`")
BI = ["B(rx) := /${rx}-(?<d>\\d)/"]
r_i1 = ref("B(/(?<d>\\d)/) & (d: <5)", BI)
r_i2 = ref("B([x = /(?<d>\\d)/]) & (x.d: <5)", BI)
r_i3 = ref('hits(/a(?<g>x)?/) & (g: "x")')
P_i4 = tp("B(/(?<d>\\d)/) & (B.d: <5)", BI)
second_lt5 = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5      # noqa: E731
if P_i4 is not None:
    dl("The first shape, settled", "B(/(?<d>\\d)/) & (B.d: <5)", BI, P_i4, ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9",
       "core/labels/paths/two-sources")
check("INPLACE", all(has(r, *ADR) for r in (r_i1, r_i2, r_i3)) and wdiff(P_i4, second_lt5, DG) == 0,
      "refused naming argument-default: bare `d` %s, `x.d` on the argument %s, `hits(..) & (g: \"x\")` %s; `B.d` "
      "reads the body's own d, against \"the SECOND digit under 5\" differing %d over %d texts" %
      (has(r_i1, *ADR), has(r_i2, *ADR), has(r_i3, *ADR), wdiff(P_i4, second_lt5, DG), len(DG)))

print("== ARGOWN (reading (c)): a read written inside the argument travels with the template")
OC = "occurrences(/(?<n>\\d+)/ & (n: <100))"
P_o = tp(OC)
DO = ["1234", "123", "12", "1", "12345", "100"]
want_o = {"1234": True, "123": True, "12": True, "1": True, "12345": True, "100": True}
check("ARGOWN", P_o is not None and all(P_o.whole(t) == want_o[t] for t in DO) if not ss("s8") else
      P_o is not None and P_o.whole("1234") is False,
      "`%s` legal %s; WHOLE over %s: %s (every text splits into hits under 100)" %
      (OC, P_o is not None, DO, [P_o.whole(t) for t in DO] if P_o else None))

print("== SPOT (reading (d), wrapper-export): a spot the body labels or lists passes the argument's labels on")
SB = [ADIG, "B(rx) := /${[dd = rx]}xx/"]
P_s1 = tp("B(A) & (B.dd.d: <100)", SB)
P_s1c = tp("C", ["C := B(A) & (B.dd.d: <100)"] + SB)
lt100 = lambda t: re.fullmatch(r"(0|[1-9]\d?)xx", t) is not None       # noqa: E731  (rx.digits then `xx`, under 100)
DX = [a + "xx" for a in pop("0147", 3)[1:]]
if P_s1 is not None:
    dl("Through a part label in the body", "B(A) & (B.dd.d: <100)", SB, P_s1, ["42xx", "100xx", "042xx"],
       "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/labels/paths/argument-default")
if P_s1c is not None:
    dl("Example 1, the spot labelled", "C := B(A) & (B.dd.d: <100)", SB, P_s1c, ["42xx", "100xx", "042xx"],
       "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/holes/bare-condition/nested-scope")
P_s2 = tp('hits(/a(?<g>x)?/) & (hits.hit.g: "x")')
P_s3 = tp('occurrences(/(?<n>\\d+)/) & (occurrences.hit.n: "3")')
P_s4 = tp("peek(/(?<d>\\d)/) SEQ /\\d\\d/ & (peek.d: <5)")
P_s5 = tp("atomic(/(?<l>\\d\\d)/ | /(?<l>\\d)\\d/) & (atomic.l: <20)")
r_s6 = ref("atomic(B | A) & (atomic.l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
P_s7 = tp('endsWith(/(?<n>\\d+)/) & (endsWith.n: "3")')
P_s8 = tp('contains(/(?<n>\\d)/) & (contains.n: "3")')
P_s9 = tp('padded(/(?<v>\\d)/) & (padded.v: "5")')
for lab, e, Pg, wh, sr, fa, tg in [
        ("The argument's group, through the hit", 'occurrences(/(?<n>\\d+)/) & (occurrences.hit.n: "3")', P_s3,
         ["a1b3", "a3b1", "ab"], "x1 3", "a3 b1 3", "lib/search/occurrences"),
        ("Read through the call", "peek(/(?<d>\\d)/) SEQ /\\d\\d/ & (peek.d: <5)", P_s4, ["37", "73"], "x73 37",
         "37 73 56", "lib/control/peek"),
        ("", "atomic(/(?<l>\\d\\d)/ | /(?<l>\\d)\\d/) & (atomic.l: <20)", P_s5, ["25", "13"], "25", "25 13",
         "core/patterns/atomic")]:
    if Pg is not None:
        dl(lab, e, [], Pg, wh, sr, fa, tg)
last_g = lambda t: bool(re.findall(r"ax?", t)) and re.findall(r"ax?", t)[-1] == "ax"    # noqa: E731  (the last hit sets g)
peekd = lambda t: re.fullmatch(r"\d\d", t) is not None and int(t[0]) < 5      # noqa: E731
ends3 = lambda t: t.endswith("3")                     # noqa: E731  (some split of the greedy gap gives n = `3`)
P_ok = [x is not None for x in (P_s1, P_s1c, P_s2, P_s3, P_s4, P_s5, P_s7, P_s8, P_s9)]
spot_d = (wdiff(P_s1, lt100, DX), wdiff(P_s2, last_g, pop("ax", 4)), wdiff(P_s4, peekd, pop("37", 2)),
          wdiff(P_s5, lambda t: re.fullmatch(r"1\d", t) is not None, pop("125", 2)),
          wdiff(P_s7, ends3, pop("ab13", 3)))
check("SPOT", all(P_ok) and has(r_s6, *NOTVIS) and spot_d == (0,) * 5,
      "legal: `B.dd.d` (his example 3's spot) / at C, `hits.hit.g`, `occurrences.hit.n`, `peek.d`, `atomic.l` over an "
      "expression, `endsWith.n`, `contains.n`, `padded.v`: %s; `atomic(B | A) & (atomic.l: ..)` (bindings used alone "
      "in the argument export nothing) refused %s; differing from direct predicates (`B.dd.d` under 100; the last "
      "hit's g is x; peek's first digit under 5; atomic's `l` under 20 is the 1x numbers; endsWith's greedy-gap last "
      "run is `3`): %s" % (P_ok, has(r_s6, *NOTVIS), spot_d))

print("== TWOSPOT (the cases): two spots of one argument, several arguments, a looped spot")
P_t1 = tp('list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")')
P_t2 = tp("pair(A) & (pair.d: <5)", [AD, "pair(p) := /${[(=) = p]},${[(=) = p]}/"])
WB = ["W(a, b) := [(=) = a] SEQ [(=) = b]"]
P_t3 = tp('W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', WB)
P_t4 = tp('[r = rx.repeat(/(?<a>\\d)/, min = 1)] & (r.a: "3")')
P_t5 = tp('[r = rx.repeat(/(?<a>\\d)/, min = 1)] & some((r.a: "7"))')
for lab, e, b_, Pg, wh, sr, fa, tg in [
        ("The last item, through the call", 'list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")', [], P_t1,
         ["7,3,5", "7,5,3"], "x7,5 3,5", "1,5 3 5", "lib/records/list-of"),
        ("An argument used twice by the body", "pair(A) & (pair.d: <5)", [AD, "pair(p) := /${[(=) = p]},${[(=) = p]}/"],
         P_t2, ["7,3", "3,7", "3,3"], "3,7 7,3", "7,3 3,7 1,2 9,9", "core/labels/paths/call-prefix"),
        ("Two arguments", 'W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', WB, P_t3, ["7;3", "3;7"], "x3;7 7;3",
         "7;3 3;7 1;3", "lib/convention/argument-labels"),
        ("The last item, through a label on the call", '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & (r.a: "3")', [], P_t4,
         ["73", "37"], "x37 73", "73 37 13", "lib/rx/repeat"),
        ("Every item, a group question", '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & some((r.a: "7"))', [], P_t5,
         ["73", "33"], "x33 73", "73 33 17", "lib/rx/repeat")]:
    if Pg is not None:
        L_ = dl(lab, e, b_, Pg, wh, sr, fa, tg)
        if lab == "Two arguments":
            LINES[-1] = (tg, L_.replace("W(a, b) := `[(=) = a] SEQ [(=) = b]`)",
                                        "W(a, b) := `[(=) = a] SEQ [(=) = b]`, the shape of when's then branch)"))
last5 = lambda t: re.fullmatch(r"\d(,\d)*", t) is not None and t[-1] == "5"          # noqa: E731
pair2 = lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[2]) < 5 if not ss("s10") else \
    (re.fullmatch(r"\d,\d", t) is not None and int(t[0]) < 5)                        # noqa: E731
w2 = lambda t: re.fullmatch(r"\d;\d", t) is not None and t[2] == "3"                  # noqa: E731
r_last = lambda t: re.fullmatch(r"\d+", t) is not None and t[-1] == "3"              # noqa: E731
r_some = lambda t: re.fullmatch(r"\d+", t) is not None and "7" in t                   # noqa: E731
tw = (wdiff(P_t1, last5, pop("35,", 5)), wdiff(P_t2, pair2, pop("37,", 3)), wdiff(P_t3, w2, pop("37;", 3)),
      wdiff(P_t4, r_last, pop("37", 3)), wdiff(P_t5, r_some, pop("37", 3)))
check("TWOSPOT", tw == (0,) * 5,
      "differing from direct predicates: list_of's last item is 5 %d; pair's two spots, the last mention (the second "
      "digit) %d; W's two arguments, one label, the last mention %d; rx.repeat's looped spot, the last item %d, a "
      "group question every item %d" % tw)

print("== USERMACRO (his pair): `identity` passes the labels on, `hide` none; both match what x matches")
IDB, HDB = "identity(x) := /${[(=) = x]}/", "hide(x) := /${x}/"
P_u1 = tp("identity(A) & (identity.d: <5)", [AD, IDB])
r_u2 = ref("hide(A) & (hide.d: <5)", [AD, HDB] if not ss("s11") else [AD, HDB.replace("${x}", "${[(=) = x]}")])
P_h, P_id = tp("hide(A)", [AD, HDB]), tp("identity(A)", [AD, IDB])
QU = pop("37 ", 3)
if P_u1 is not None:
    dl("identity", "identity(A) & (identity.d: <5)", [AD, IDB], P_u1, ["3", "7"], "7 3", "3 7 4",
       "lib/convention/argument-labels")
if P_h is not None:
    L_ = dl("The same match, either body", "hide(A)", [AD, HDB], P_h, ["3", "7"], "7 3", "3 7 4",
            "lib/convention/argument-labels")
    LINES[-1] = (LINES[-1][0], L_[:-1] + "; `identity(A)` alike)")
same_m = ndiff(answers(P_h, QU), answers(P_id, QU)) if P_h and P_id else None
check("USERMACRO", wdiff(P_u1, lambda t: t in ("0", "1", "2", "3", "4"), pop("0378", 1)) == 0 and has(r_u2, *NOTVIS)
      and same_m == (0, 0, 0),
      "`identity(A) & (identity.d: <5)` legal, differing %d; `hide(A) & (hide.d: <5)` refused (hide exports no `d`) "
      "%s; `hide(A)` against `identity(A)` differing %s over %d texts" %
      (wdiff(P_u1, lambda t: t in ("0", "1", "2", "3", "4"), pop("0378", 1)), has(r_u2, *NOTVIS), same_m, len(QU)))
print("   refusal: %s" % r_u2)

print("== PLACES (the census): every provided body that places a parameter in a pattern hole writes the list or "
      "labels the spot")
LIBNOW = NOWS["library.md"]
BODY_RX = re.compile(r"`((?:rx\.)?\w+)\(([\w, =/\"]*)\) :=\s+([^`]+)`")
SET_ARGS = {("between",), ("prefix_in",)}
census, cbad = [], []
BODY_RX2 = re.compile(r"`(\w+)\(([\w, =]*)\)` (?:is the plain gap body|is the plain macro|is the separated list|is the lazy-gap loop|reads "
                      r"only the text inside double quotes: the body) `([^`]+)`")
BODIES = [(m_.group(1), m_.group(2), m_.group(3)) for m_ in BODY_RX.finditer(ws(LIBNOW))] + \
    [(m_.group(1), m_.group(2), m_.group(3)) for m_ in BODY_RX2.finditer(ws(LIBNOW))]
for nm, heads, body in BODIES:
    if nm == "list_of":
        heads = heads.replace("sep = S", "S")
    if nm in ("hide", "identity", "pair", "W", "B"):
        continue
    params = [h.split("=")[0].strip() for h in heads.split(",") if h.strip()]
    if ss("s9") and nm == "peek":
        body = "/(?=${A})/"
    for p_ in params:
        alone = re.findall(r"\$\{\s*%s\s*\}" % re.escape(p_), body)
        listed = re.findall(r"\$\{\s*\[\(=\) = %s\]" % re.escape(p_), body) + \
            re.findall(r"\[\(=\) = %s\]" % re.escape(p_), body)
        spot = re.findall(r"\(\?<:\w+>\$\{\s*%s\s*\}\)" % re.escape(p_), body)
        count_hole = re.search(r"\{\$\{\s*%s\s*\}|\$\{\s*%s\s*\},|,\$\{\s*%s\s*\}\}|<\$\{\s*%s\s*\}>" %
                               ((re.escape(p_),) * 4), body)
        class_pos = re.search(r"\[[^\]]*\$\{\s*%s\s*\}[^\]]*\]" % re.escape(p_), body)
        kind = ("listed" if listed else "spot-labelled" if spot else "count/name hole" if count_hole and not listed
                else "class position (no pattern)" if class_pos else "alone" if alone else "not placed in a hole")
        census.append((nm, p_, kind))
        if kind == "alone" and len(alone) > len(spot):
            cbad.append((nm, p_))
for c_ in census:
    print("   %-12s %-5s %s" % c_)
check("PLACES", census and not cbad, "%d (body, parameter) pairs read from library.md's body texts (`name(..) := "
      "..`): %s; a parameter placed alone in a hole: %s" %
      (len(census), ", ".join("%s %d" % (k, sum(1 for c_ in census if c_[2] == k)) for k in
                              sorted(set(c_[2] for c_ in census))), cbad or "none"))

print("== CONVENTION: the convention stated once; every covered body's piece points at it")
CONV = ("A provided body that places its argument in the match passes that argument's labels on, by the export list "
        "on each spot, unless its piece says otherwise.")
covered = ["lib/control/peek", "lib/control/atomic", "lib/control/when", "lib/records/list-of",
           "lib/modifiers/padded", "lib/modifiers/quoted", "lib/search/anchored", "lib/modifiers/any-case",
           "lib/search/contains", "lib/search/starts-with", "lib/search/ends-with", "lib/rx/repeat",
           "lib/structural/capture"]
if ss("s12"):
    covered.append("lib/search/between")
pieces = re.split(r"\n(?=### )", LIBNOW)
nopoint = []
for tg in covered:
    pc = next((p_ for p_ in pieces if "[%s]" % tg in p_.split("\n")[0]), "")
    if "lib/convention/argument-labels" not in pc:
        nopoint.append(tg)
conv_n = ws(LIBNOW).count(ws(CONV))
check("CONVENTION", conv_n == 1 and not nopoint, "the convention sentence occurs %d time(s) in library.md; covered "
      "pieces not pointing at lib/convention/argument-labels: %s (of %d)" % (conv_n, nopoint or "none", len(covered)))

print("== GRID: the name grid, spelling x occurrences of its source x read kind; each cell its deciding sentence")
# predfix83's grid (its spellings, occurrences and read kinds, unchanged) with the argument cells DECIDED by the
# ruling, and three spellings added: a spot the body labels (`B.p.h`), the export list on a spot (`B.h`), a part
# label written on an argument (`a.h`, reading (a)).
G_A = "A := /(?<h>\\d)/"
G_B = "B(rx) := /${rx}(?<d>\\d)/"
G_I1 = "i1 := [year = /\\d/] SEQ /\\d/"
G_I2 = "i2 := /\\d/ SEQ [year = /\\d/]"
G_ARG = "B(rx) := /${rx}x/"
G_SPOT = "B(rx) := /${[p = rx]}x/"
G_LIST = "B(rx) := /${[(=) = rx]}x/"
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
    ("spot-label", {"one": ("B.p.h", "B(A)", [G_A, G_SPOT]), "seq": ("B.p.h", "B(A) SEQ B(A)", [G_A, G_SPOT]),
                    "and": ("B.p.h", "B(A) & B(A)", [G_A, G_SPOT]),
                    "nest": ("X.B.p.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_SPOT])}),
    ("export-list-on-spot", {"one": ("B.h", "B(A)", [G_A, G_LIST]), "seq": ("B.h", "B(A) SEQ B(A)", [G_A, G_LIST]),
                             "and": ("B.h", "B(A) & B(A)", [G_A, G_LIST]),
                             "nest": ("X.B.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_LIST])}),
    ("argument-label", {"one": ("a.h", "B([a = A])", [G_A, G_LIST]),
                        "seq": ("a.h", "B([a = A]) SEQ B([a = A])", [G_A, G_LIST]),
                        "and": ("a.h", "B([a = A]) & B([a = A])", [G_A, G_LIST]),
                        "nest": ("X.a.h", "X", ["X := B([a = A]) SEQ \"!\"", G_A, G_LIST])}),
]
READS = [("plain", "%s & (%s: \"3\")"), ("$", "(%s) SEQ $%s"), ("group", "%s & some((%s: \"3\"))"),
         ("index", "%s & (%s[1]: \"3\")")]
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
    "ad-rule": ("core/labels/paths/argument-default", "the caller's read of that argument's labels (`A.d` in `B(A)`, a "
                "group written in place) is a compile error: the argument is a template"),
    "ad-a": ("core/labels/paths/argument-default", "a part label written ON an argument at a call labels a template, "
             "not a spot"),
    "ad-d": ("core/labels/paths/argument-default", "a spot the body labels exports the argument's exported labels "
             "through that label"),
    "spot-list": ("lib/convention/argument-labels", "the list on it, `[(=) = x]`, takes every label the argument "
                  "exports as the body's own"),
    "bp-text": ("core/labels/paths/binding-prefix", "\"Used more than once\" is counted in the TEXT of the "
                "definition the reference is written in"),
    "cA": ("core/labels/paths", "a call's label reaches no argument by the argument's name"),
}
REF_FLOW = "refused:core/labels/flow"
REF_BP = "refused:used 2 times"
REF_SRC = "refused:with its source"
REF_VIS = "refused:not visible through"
REF_AD = "refused:" + AD_RULE
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
    # the seven cells UNDECIDED under predfix83, decided by the ruling:
    ("argument", "one"): [(REF_AD, "ad-rule")] * 4,
    # (predfix83's four `used 2 times` cells of seq / and now refused by the ruling first: a template's label is no
    # spot's, so the count of uses never arises)
    ("argument", "seq"): [(REF_AD, "ad-rule")] * 4,
    ("argument", "and"): [(REF_AD, "ad-rule")] * 3 + [("refused:not ordered", "bp-idx")],
    ("argument", "nest"): [(REF_VIS, "cA")] * 4,
    ("spot-label", "one"): [("legal", "ad-d")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("spot-label", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"), ("legal", "cp-same")],
    ("spot-label", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                            ("refused:not ordered", "occ-and")],
    ("spot-label", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("export-list-on-spot", "one"): [("legal", "spot-list")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("export-list-on-spot", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                                     ("legal", "cp-same")],
    ("export-list-on-spot", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                                     ("refused:not ordered", "occ-and")],
    ("export-list-on-spot", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("argument-label", "one"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "seq"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "and"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "nest"): [(REF_VIS, "paths-alone")] * 4,
}
if ss("s13"):
    EXPECT[("argument", "one")][0] = ("legal", "ad-rule")
OCC = ["one", "seq", "and", "nest"]
GCNT = {"AGREE": 0, "DISAGREE": 0, "UNDECIDED": 0}
GBAD, GQMISS = [], []
ALLDOC_NOW = ws("\n".join(NOWS[f] for f in ("core.md", "library.md", "parked.md")))
for sp, occs in SPELL:
    for oc in OCC:
        R_, P_, B_ = occs[oc]
        base = tp(P_, B_)
        alpha = "37x!" if sp not in ("bare", "binding", "part-label", "export-list") or oc == "nest" else "37"
        for (rk, form), (exp, skey) in zip(READS, EXPECT[(sp, oc)]):
            expr = form % (P_, R_)
            tag_, words = S[skey]
            if ws(words) not in ALLDOC_NOW:
                GQMISS.append((sp, oc, rk, skey))
            vl = ref(expr, B_)
            Pl = tp(expr, B_)
            if vl is not None:
                got = "REFUSED (%s)" % vl
            else:
                hs = [t for t in pop(alpha, 5) if t and Pl.whole(t)][:2]
                fs = [t for t in pop(alpha, 5) if t and base is not None and base.whole(t) and not Pl.whole(t)][:1]
                got = fmt(Pl, (hs + fs) or ["x"], ("x" + hs[0]) if hs else "x", " ".join(hs + fs) if hs else "x")
            ok = (vl is None) if exp == "legal" else (vl is not None and exp.split(":", 1)[1] in vl)
            st = "AGREE" if ok else "DISAGREE"
            if not ok:
                GBAD.append((sp, oc, rk, vl))
            GCNT[st] += 1
            print("   %-19s %-4s %-5s | `%s`%s | %s: \"%s\" | %s | %s" % (sp, oc, rk, expr, bt(B_), tag_, words, exp,
                                                                         got[:240]))
            print("      -> %s" % st)
print("   GRID SUMMARY: %d cells: AGREE %d, DISAGREE %d, UNDECIDED %d; deciding sentences not found verbatim: %s" %
      (sum(GCNT.values()), GCNT["AGREE"], GCNT["DISAGREE"], GCNT["UNDECIDED"], GQMISS or "none"))
check("GRID", not GBAD and not GQMISS and sum(GCNT.values()) == 144 and GCNT["UNDECIDED"] == 0,
      "%d cells (9 spellings x 4 occurrences x 4 read kinds; predfix83's 96 and 48 new): AGREE %d, DISAGREE %d %s, "
      "UNDECIDED %d; sentences missing %s" % (sum(GCNT.values()), GCNT["AGREE"], GCNT["DISAGREE"], GBAD[:3],
                                               GCNT["UNDECIDED"], GQMISS or "none"))

print("== AWAITS: no line or sentence of the three base files still awaits argument-default")
aw_left = [(f, i + 1) for f in ("core.md", "library.md", "parked.md") for i, l_ in enumerate(NOWS[f].split("\n"))
           if "awaits argument-default" in l_ or ("open argument-default" in l_ and l_.startswith("### "))]
aw_old = sum(OLDS[f].count("awaits argument-default") for f in ("core.md", "library.md", "parked.md"))
if ss("s14"):
    aw_left = []
    aw_old = 0
check("AWAITS", aw_old > 0 and not aw_left, "\"awaits argument-default\" in the base files at the starting commit: %d "
      "(`git show %s:<file> | grep -c`); left now: %s" % (aw_old, START_S, aw_left or "none"))

print("== SWEEP: every printed three-mode line, old engine over the starting documents against the new one over these; "
      "no answer moves unless listed")
import ast                                                   # noqa: E402
NEW_T = sw_table()
OLD_T = {}
if not LIGHT:
    envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
    envo["PREDSPOT_ENGINE"] = "old"
    oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                        env=envo, timeout=1500).stdout
    for l_ in oo.split("\n"):
        if l_.startswith("SW\t"):
            _, k_, f_, ln_, st_, got_ = l_.split("\t", 5)
            OLD_T.setdefault(ast.literal_eval(k_), []).append((f_, int(ln_), st_, got_))
# Lines whose program moved, each with the rule that carries it. RESPELLED: the old program -> its new spelling
# (the same answers required); ERRORNOW: the old program is now refused (its rule must be in the refusal).
BD5 = (("A", "/(?<d>\\d)/"), ("B(rx)", "/${rx}-(?<d>\\d)/"))
BL = (("A", "/(?<l>\\d)\\d/"), ("B", "/(?<l>\\d\\d)/"))
RESPELLED = {      # (old program, its bindings) -> (new program, its bindings, the rule)
    ("atomic([ab = B | A]) & (ab.l: <20)", BL): ("atomic(/(?<l>\\d\\d)/ | /(?<l>\\d)\\d/) & (atomic.l: <20)", (),
                                               "argument-default reading (a); wrapper-export (atomic.l)"),
    ("B(A) & (A.d: <5)", BD5): ("B(A) & (A.d: <5)", (("A", "/(?<d>\\d)/"), ("B(rx)", "/${[p = rx]}-(?<d>\\d)/")),
                               "argument-default (closed-argument settled strictly): the body labels the spot"),
    ("pair(A) & (A.d: <5)", (("A", "/(?<d>\\d)/"), ("pair(p)", "/${p},${p}/"))):
        ("pair(A) & (pair.d: <5)", (("A", "/(?<d>\\d)/"), ("pair(p)", "/${[(=) = p]},${[(=) = p]}/")),
         "argument-default; the list on both spots (wrapper-export's answer)"),
    ("B(/(?<d>\\d)/) & (d: <5)", (("B(rx)", "/${rx}-(?<d>\\d)/"),)):
        ("B(/(?<d>\\d)/) & (B.d: <5)", (("B(rx)", "/${rx}-(?<d>\\d)/"),), "argument-default reading (b)"),
    ("C := B(A) & (A.d: <100)", (("A", "[d = rx.digits]"), ("B(rx)", "/${rx}xx/"))):
        ("C := B(A) & (B.dd.d: <100)", (("A", "[d = rx.digits]"), ("B(rx)", "/${[dd = rx]}xx/")),
         "argument-default revises his example 1; his example 3's spot"),
    ('hits(/a(?<g>x)?/) & (g: "x")', ()): ('hits(/a(?<g>x)?/) & (hits.hit.g: "x")', (),
                                           "argument-default readings (b), (d)"),
}
ERRORNOW = {       # (old program, its bindings) -> the words its refusal must hold
    ("B(A) & (A.d: <5)", (("A", "/(?<d>\\d)/"), ("B(rx)", "/${rx}xx/"))): AD_RULE,
    ("B([x = /(?<d>\\d)/]) & (x.d: <5)", (("B(rx)", "/${rx}-(?<d>\\d)/"),)): AD_RULE,
}
DROPPED = {        # (old program, its bindings) -> why the line is gone (its program printed elsewhere)
    ("B(A) & (A.d: <5)", (("B(rx)", "/${[p = rx]}-${rx}/"), ("A", "/(?<d>\\d)/"))):
        "the line \"Both uses, (local)\": candidate (local) rejected by the ruling; the program stays printed as "
        "\"Both uses\" with the (error) answers",
}
ANSWERS_CHANGED = {   # (program, its bindings) -> why its answers move
    ("B(A) & (A.d: <5)", (("B(rx)", "/${[p = rx]}-${rx}/"), ("A", "/(?<d>\\d)/"))):
        "argument-default (error): the use alone exports nothing, so `A.d` reads the labelled spot (the first digit); "
        "the old engine's candidate (local) read the use alone (the second digit). Its two lines (\"Both uses, "
        "(local)\", \"Both uses, (error)\") are one now, the (error) answers",
}
if ss("s15") and RESPELLED:
    RESPELLED.pop(next(iter(RESPELLED)))
sw_bad, sw_moved, sw_new, sw_gone = [], [], [], []
for k, vs in NEW_T.items():
    ov = OLD_T.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        o_ = ov[i_] if i_ < len(ov) else None
        if st_ != "same" and OLD_T and not (o_ and o_[2] == st_ and o_[3] == got_):
            sw_bad.append(("printed != run", f_, ln_, st_, k[0]))       # a pre-existing engine limit only if unchanged
        if o_ and o_[3] != got_ and (k[0], k[1]) not in ANSWERS_CHANGED:
            sw_moved.append((f_, ln_, k[0], o_[2], st_))
    if not ov and OLD_T:
        sw_new.append((vs[0][0], vs[0][1], k[0], k[1]))
for k, vs in OLD_T.items():
    if k in NEW_T:
        continue
    f_, ln_, st_, got_ = vs[0]
    pt = k[0]
    sw_gone.append((f_, ln_, pt, k[1]))
    if (pt, k[1]) in RESPELLED:
        rp = RESPELLED[(pt, k[1])]
        nk = [k2 for k2 in NEW_T if k2[0] == rp[0] and k2[1] == rp[1] and k2[2:] == k[2:]]
        if not nk or NEW_T[nk[0]][0][3] != got_:
            sw_bad.append(("respelled, answers differ", f_, ln_, pt, rp[0]))
    elif (pt, k[1]) in ERRORNOW:
        bnd = ["%s := %s" % b for b in k[1]]
        mm = re.fullmatch(r"([\w.]+(?:\([\w, ]*\))?) := (.*)", pt)
        ex = mm.group(1) if mm else pt
        if mm:
            bnd = [pt] + bnd
        r_ = ref(ex, bnd)
        if not has(r_, ERRORNOW[(pt, k[1])]):
            sw_bad.append(("not refused for its rule", f_, ln_, pt, r_))
    elif (pt, k[1]) in DROPPED and any(k2[0] == pt and k2[1] == k[1] for k2 in NEW_T):
        pass
    else:
        sw_bad.append(("gone, unlisted", f_, ln_, pt, k[1]))
for x in sw_gone:
    kk = (x[2], x[3])
    print("   GONE %s:%d `%s` %s -> %s" % (x[0], x[1], x[2], x[3], "RESPELLED `%s` %s (%s)" % RESPELLED[kk]
                                          if kk in RESPELLED else "ERROR NOW (%s)" % ERRORNOW[kk]
                                          if kk in ERRORNOW else "DROPPED (%s)" % DROPPED[kk] if kk in DROPPED
                                          else "UNLISTED"))
for kk, why in ANSWERS_CHANGED.items():
    print("   ANSWER CHANGED `%s` %s: %s" % (kk[0], kk[1], why))
for x in sw_new:
    print("   ADDED %s:%d `%s` %s" % x)
for x in sw_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)" % x)
for x in sw_bad:
    print("   BAD %s" % (x,))
cnt = {}
for vs in NEW_T.values():
    cnt[vs[0][2]] = cnt.get(vs[0][2], 0) + 1
check("SWEEP", (LIGHT or OLD_T) and not sw_bad and not sw_moved,
      "%d printed lines now (%s), %d at the starting commit under the old engine; in both with the same program and "
      "texts %d, answers moved %d; gone %d (respelled %d, an error now %d), added %d; bad %d %s" %
      (len(NEW_T), ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(OLD_T),
       sum(1 for k in NEW_T if k in OLD_T), len(sw_moved), len(sw_gone),
       sum(1 for x in sw_gone if (x[2], x[3]) in RESPELLED), sum(1 for x in sw_gone if (x[2], x[3]) in ERRORNOW),
       len(sw_new),
       len(sw_bad), sw_bad[:3]))

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
if ss("s16"):
    checked.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nl = [(e, b) for e, b, nd in checked if loops_nullable(nd, [])]
check("NULLABLE", not nl, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a loop "
      "whose body can match empty%s" % (len(checked), len(nl), (": %s" % nl[:4]) if nl else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line (a red whose content changes under an unchanged name fails here)")
LANES = os.path.normpath(os.path.join(HERE5, ".."))
FOLD = "this lane's fold rewrote the texts it looks for (argument-default ruled; the bodies restated) and "
P83D = "predfix83's SUCCESSOR, which declared it, and "
SUPERSEDED = {                # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
    "predfix83": {
        "AWAITS": ("2b8a870671e7", "AWAITS here: argument-default is ruled, so no line awaits it (0 marked lines)"),
        "DOC": ("05476f118e2f", FOLD + "SWEEP here (each gone line RESPELLED, ERROR NOW or DROPPED) and DOC here"),
        "MARKS": ("6a4c7d7c60e5", FOLD + "ARGNAME, ARGLABEL, INPLACE, SPOT, CONVENTION here (the new texts)"),
        "SUCCESSOR": ("09beed319b16", "SUCCESSOR here: it re-runs the same eight models, each red declared below")},
    "preddef": {
        "AWAITS": ("e8f86816cd7a", "AWAITS here, as predfix83's"),
        "DOC": ("7fb8548abf05", FOLD + "SWEEP here (the line \"(local)\" an ERROR NOW, the rejected candidate)"),
        "MARKS": ("1eb81766853a", FOLD + "ARGNAME, INPLACE and GRID here"),
        "SUCCESSOR": ("9ce8705eed79", "SUCCESSOR here")},
    "predfix82": {
        "DOC": ("b83b570b827a", FOLD + "INPLACE here (two-sources' first shape settled) and SWEEP"),
        "MARKS": ("84df29d69537", P83D + "predfix83's MARKS there, unchanged"),
        "REPRINT": ("49e1c7ae12f2", FOLD + "SPOT here (example 1 revised; its spot-labelled line) and SWEEP"),
        "SUCCESSOR": ("7af0ee27f19f", "SUCCESSOR here")},
    "predcall": {
        "DOC": ("ee72c84698ec", FOLD + "ARGNAME and TWOSPOT here (call-prefix's lines re-spelled) and SWEEP"),
        "PREDREF": ("bdc1a3daaa39", "SUCCESSOR here: predref is now a traceback (below), so its expected red is gone"),
        "SCAN": ("5237c318c2b5", "GRID and SPOT here: its scan predates export lists and the call prefix of a spot "
                                 "(`B.dd.d`, `hits.hit.g`); the spans before them as predfix83 declared")},
    "predref": {"TRACEBACK": ("654619d66d03", "SPOT and PLACES here: the provided bodies now write the export list "
                                              "on their spot (`atomic(X) := /(?>${[(=) = X]})/`, transform-export), "
                                              "which predref's lowerer, older than export-list, cannot read")},
    "predbound": {"TRACEBACK": ("f8b5d917c866", "SPOT and PLACES here, as predref's (its body reader meets "
                                                "`[(=) = x]`)")},
    "predfix77": {"TRACEBACK": ("455b59c946bc", P83D + "predfix82's REPRINT and predbound's checks, unchanged")},
    "predarr": {"TRACEBACK": ("ce43d48c7e37", P83D + "predfix82's REPRINT and predref's HITS, unchanged")},
    "predscope": {"TRACEBACK": ("17ab1e47c179", "TWOSPOT here: its reader of rx.repeat's third body expects "
                                                "`${x}`; the body now writes `${[(=) = x]}` (transform-export)")},
}
MODELS = ["predfix83", "preddef", "predfix82", "predcall", "predref", "predbound", "predfix77", "predarr", "predscope"]
if ss("s17") and SUPERSEDED:
    k0 = next(iter(SUPERSEDED))
    SUPERSEDED[k0].pop(next(iter(SUPERSEDED[k0])), None)
succ_bad, succ_n = [], 0
if not LIGHT:
    procs = {}
    for mname in MODELS:
        env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")}
        procs[mname] = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(LANES, mname + "_evidence",
                                                                                   mname + "_model.py")],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        out, _ = procs[mname].communicate(timeout=1500)       # one at a time: a single-process run
        procs[mname].out = out
    for mname, pr in procs.items():
        succ_n += 1
        lines_ = pr.out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm:
            for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
                reds[r] = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                                re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
        else:
            reds["TRACEBACK"] = last
        decl = SUPERSEDED.get(mname, {})
        print("   %-10s last line: %s" % (mname, last[:140]))
        for r, fl in sorted(reds.items()):
            dg = hashlib.sha256(fl.encode()).hexdigest()[:12]
            d = decl.get(r)
            if d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s [%s] UNDECLARED: %s" % (r, dg, fl[:300]))
            elif d[0] != dg:
                succ_bad.append((mname, r, "CONTENT CHANGED"))
                print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fl[:300]))
            else:
                print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
                print("         its FAIL line: %s" % fl[:240])
        gone = sorted(set(decl) - set(reds))
        if gone:
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHT or (succ_n == len(MODELS) and not succ_bad),
      "%d earlier models re-run one at a time, each last line read; every red declared superseded with an unchanged "
      "FAIL line: %s" % (succ_n, "yes" if not succ_bad else succ_bad))

print("== QUOTES: every owner sentence this lane quotes occurs in the record and the documents; every cited title is one")
QQ = ["The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted.",
      "It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern.",
      "argument-default: for me this is an error.",
      "A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern.",
      "wrapper-export: agree (a). I was worried you'd say peek() doesn't work. It's just a definition change.",
      "transform-export: yes.",
      "hide(x) := /${x}/",
      "identity(x) := /${[(=) = x]}/"]
TT = ["2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a "
      "parameter is a template, not a piece of the pattern",
      "2026-11-22 OWNER RULING — wrapper-export: agree (a) (the provided wrappers pass their argument's labels on); and "
      "a question: do transforms in general",
      "2026-11-22 OWNER RULING — transform-export: yes (a provided body that places its argument passes its labels on); "
      "and two definitions he writes: `hide`, `identity`"]
if ss("s18"):
    QQ[0] = QQ[0] + " (altered)"
ALLNOW = "\n".join(NOWS.values())
q_miss = [q for q in QQ if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOW)]
heads = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_miss = [t_ for t_ in TT if ws(t_) not in heads or ws(t_) not in ws(ALLNOW)]
check("QUOTES", QQ and not q_miss and not t_miss, "%d quoted sentences in the record and the documents, missing: %s; "
      "%d record titles cited whole, not a title or not cited: %s" % (len(QQ), q_miss or "none", len(TT),
                                                                     t_miss or "none"))

print("== DOC: every line this model formats occurs verbatim in the documents")
DLN = list(LINES)
if ss("s19") and DLN:
    DLN[0] = (DLN[0][0], DLN[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_miss = [(t_, L) for t_, L in DLN if ws(L) not in ws(ALLNOW)]
for t_, L in d_miss:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLN and not d_miss, "%d lines; missing: %d" % (len(DLN), len(d_miss)))

failed = [n for n, ok in RESULTS if not ok]
print("predspot_model: %d checks, %d failed%s" % (len(RESULTS), len(failed),
                                                 (" (%s)" % ", ".join(failed)) if failed else ""))
sys.exit(1 if failed else 0)
