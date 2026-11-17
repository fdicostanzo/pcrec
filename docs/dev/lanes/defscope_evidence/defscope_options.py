# defscope: evidence for docs/design/condition_kind.md Part III ("the scope of a default", an EXPLORATION, rules
# nothing) and docs/dev/lanes/defscope_report.md (lane defscope, 2026-11-16; design only).
#
# THE MODEL (rulings of 2026-11-16 21:49, COND-FAMILY): no optional mark; an absent label is NULL and a test holding a
# NULL fails; a DEFAULT is a COALESCE; a source row is the whole subject; a result row is one match, the pairing
# loop's passes a nested table (a plain condition reads the LEFT JOIN row on zero passes, a group question counts
# real passes). What is NOT ruled is HOW FAR a default reaches. This script runs every scope option side by side:
#   LOCAL    (a) per TEST: the default belongs to the one condition that writes it (a COALESCE in that where-test);
#   COLUMN   (b) per LABEL for the whole statement: the label's value everywhere in the statement, `$h` reads
#               included (a COALESCE in the select list, lifted to the statement's base so `&` stays order-free); a
#               second, different default for the label is an ERROR. The statement = the program after inlining
#               every named program (macros expand per use, rev 22 §5.2), with a COMPLEMENTED operand a separate
#               statement (rev 22 §2.2 reading (1)): "COLUMN-b1"; "COLUMN-b2" lets the outer defaults reach INTO a
#               complemented operand (labels still never come out);
#   POS      (c) positional: the default rewrites the label's column from the condition that writes it onward (SQL's
#               literal nesting, `(P where c1) where c2`); a later default on an already-filled label is dead;
#   DOLLAR   (f) review r30 I's option (ii): tests are LOCAL, but a `$a` reads the statement's one default for a;
#   DECL     (e) declared at the label's DEFINITION (in the pattern): one value per label for every use of the
#               pattern; conditions carry no default.
# (d) "per record / joint condition" is LOCAL itself (a record is one condition), so it is not a separate engine.
#
# THIS SCRIPT exec's lane condkind2's script (condkind2_evidence/condkind2_nomark.py, unedited, its output
# suppressed; it exec's lane condkind's engine in turn) for the pools, the condition codings, the rev 22 targets and
# the no-mark one-pass evaluator (nm_pass), then evaluates every option with its OWN program evaluator (run below).
#
# Run from the scratch dir ($PCREC_TMPDIR/scratch/defscope/), W = the worktree root:
#   timeout 300 python3 -I W/docs/dev/lanes/condkind_evidence/rev22_ref.py rev22_ref.tsv
#   timeout 900 python3 -I W/docs/dev/lanes/defscope_evidence/defscope_options.py rev22_ref.tsv > fwd.out
#   DEFSCOPE_SWAP=1 timeout 900 python3 -I W/.../defscope_options.py rev22_ref.tsv > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   DEFSCOPE_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# DEFSCOPE_SWAP=1 sets CONDKIND2_SWAP=1 (and through it CONDKIND_SWAP=1), so every engine order reverses too.
import contextlib, io, itertools, os, re, sys

SWAP = os.environ.get("DEFSCOPE_SWAP") == "1"
SAB = os.environ.get("DEFSCOPE_SABOTAGE") == "1"
os.environ["CONDKIND2_SWAP"] = "1" if SWAP else "0"
os.environ["CONDKIND2_SABOTAGE"] = "0"
HERE = os.path.dirname(os.path.abspath(__file__))
CK2 = os.path.join(os.path.dirname(HERE), "condkind2_evidence", "condkind2_nomark.py")
G = {"__name__": "condkind2_nomark", "__file__": CK2}
_argv, sys.argv = sys.argv, [CK2, sys.argv[1]]
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(CK2).read(), CK2, "exec"), G)
sys.argv = _argv
print("ORDER: %s%s" % ("SWAPPED (every order reversed, the engines' too)" if SWAP else "forward",
                       "; SABOTAGE ON (COLUMN evaluated positionally in engine order)" if SAB else ""))
K = G["G"]                                     # lane condkind's engine namespace, as condkind2 holds it
O, views, Cond, Row, Pool, rx_pool = K["O"], K["views"], K["Cond"], K["Row"], K["Pool"], K["rx_pool"]
nm_pass, dval, reg, SRC, popc, low, tvec = G["nm_pass"], G["dval"], G["reg"], G["SRC"], G["popc"], G["low"], G["tvec"]
consts, never_absent, one, canon, num, D = G["consts"], G["never_absent"], G["one"], G["canon"], G["num"], G["D"]
LT5, GT7, LT3 = G["LT5"], G["GT7"], G["LT3"]
A, B, P, LST, RZ, AB, J, RP, RQ, R7 = (G[n] for n in ("A", "B", "P", "LST", "RZ", "AB", "J", "RP", "RQ", "R7"))
ERR = "ERROR"
KEEP = []


def full(pool):
    return (1 << len(SRC[pool.name])) - 1


def rowmask(pool):
    """the subjects the pattern itself matches (the source rows that have a result row)"""
    rs = {r.subj for r in pool.rows}
    return sum(1 << i for i, s in enumerate(SRC[pool.name]) if s in rs)


def named(c):
    return {l for l, _ in c.labs} | set(c.reads)


def coal(view, env, skip):
    """COALESCE the view's absent labels with env's defaults (env: label -> control), skipping `skip`"""
    v2 = dict(view)
    for l in O(sorted(env)):
        if l in skip or v2.get(l) is not None:
            continue
        x = dval(env[l], view)
        if x is not None:
            v2[l] = x
    return v2


VE = {}


def vecE(c, ctls, pool, env, lj=True, only=None):
    """bitmask of the subjects whose row passes c: own controls `ctls` (LOCAL), plus the statement env coalesced into
    the view (labels in `only` if given); lj False: the zero-pass LEFT JOIN row is NOT coalesced"""
    rel = named(c)
    envr = tuple(sorted((l, x) for l, x in env.items() if l in rel and (only is None or l in only)))
    key = (id(c), pool.name, tuple(ctls), envr, lj)
    if key in VE:
        return VE[key]
    KEEP.append(c)
    envd = dict(envr)
    group = c.kind in ("some", "none", "at_most", "allv")
    rows = {r.subj: r for r in pool.rows}
    labs = [(l, x) for (l, _), x in zip(c.labs, ctls)]
    b = 0
    for i, s in enumerate(SRC[pool.name]):
        r = rows.get(s)
        if r is None:
            continue
        ljrow = (not r.passes) and bool(rel & pool.looped) and not group
        skip = set(pool.looped) if (ljrow and not lj) else set()
        vals = [nm_pass(c, labs, coal(v, envd, skip)) for v in O(views(c, c.labs, r, pool, group))]
        if c.kind in ("plain", "allv"):
            ok = all(vals)                       # plain: never empty (LEFT JOIN row); allv: vacuous on no pass
        else:
            k = sum(vals)
            ok = {"some": k >= 1, "none": k == 0, "at_most": k <= (c.n or 0)}[c.kind]
        if ok:
            b |= 1 << i
    VE[key] = b
    return b


def merge(prog, err_on=None):
    """the statement's defaults, label -> control; two different defaults for one label -> ERR (when err_on is None,
    always; else only for labels in err_on)"""
    env = {}
    for c, ct in O(prog):
        for (l, _), x in zip(c.labs, ct):
            if x is None:
                continue
            if l in env and env[l] != x:
                if err_on is None or l in err_on:
                    return ERR
                continue
            env.setdefault(l, x)
    return env


def nones(c):
    return [None] * len(c.labs)


def run(prog, pool, opt, lj=True, decl=None, seed=None):
    """prog: [(cond, controls)] in WRITTEN order. Returns a bitmask or ERR."""
    acc = full(pool)
    if opt == "LOCAL":
        for c, ct in O(prog):
            acc &= vecE(c, ct, pool, {}, lj)
        return acc
    if opt in ("COLUMN", "COLUMN-noLJ"):
        if SAB:                                   # sabotage: positional in ENGINE order (O), so the swap must differ
            return run(O(prog), pool, "POS", lj, seed=seed)
        env = merge(prog)
        if env == ERR:
            return ERR
        for l, x in (seed or {}).items():         # COLUMN-b2: an outer default reaching into a complemented operand
            if l in env and env[l] != x:
                return ERR
            env.setdefault(l, x)
        for c, ct in O(prog):
            acc &= vecE(c, nones(c), pool, env, opt == "COLUMN")
        return acc
    if opt == "POS":
        env = dict(seed or {})
        for c, ct in prog:                        # written order IS the semantics here (not O)
            for (l, _), x in zip(c.labs, ct):
                if x is not None and l not in env:
                    env[l] = x
            acc &= vecE(c, nones(c), pool, dict(env), lj)
        return acc
    if opt == "DOLLAR":
        reads = set().union(*[c.reads for c, _ in prog])
        env = merge(prog, err_on=reads)
        if env == ERR:
            return ERR
        for c, ct in O(prog):
            own = {l for l, _ in c.labs}
            acc &= vecE(c, ct, pool, env, lj, only=frozenset(set(c.reads) - own))
        return acc
    if opt == "DECL":
        for c, ct in O(prog):
            acc &= vecE(c, nones(c), pool, decl or {}, lj)
        return acc
    raise ValueError(opt)


def compl(qprog, pool, opt, seed=None):
    """`!q`: the source rows with no row of q (q answered as its own statement; seed: COLUMN-b2's outer defaults)"""
    v = run(qprog, pool, opt, seed=seed)
    return ERR if v == ERR else full(pool) & ~v


def hf(x, pool, s):
    if x == ERR:
        return "ERROR"
    return "HOLDS" if x >> SRC[pool.name].index(s) & 1 else "FAILS"


def cnt(x):
    return "ERROR" if x == ERR else str(popc(x))


def dif(x, y, pool):
    if ERR in (x, y):
        return "n/a (ERROR)"
    d = x ^ y
    return "%d%s" % (popc(d), "" if not d else " (smallest %r)" % low(d, pool))


OPTS = ("LOCAL", "COLUMN", "POS", "DOLLAR")
C = lambda v: ("c", v)

# --------------------------------------------------------------------------------------------- the conditions used
h_lt5 = one("(h: <5)", "h", LT5)
h_gt7 = one("(h: >7)", "h", GT7)
h_lt3 = one("(h: <3)", "h", LT3)
h_lt9 = one("(h: <9)", "h", lambda x: canon(x) and int(x) < 9)
h_lt10 = one("(h: <10)", "h", lambda x: canon(x) and int(x) < 10)
h_nlt5 = one("(h: !(<5))", "h", lambda x: canon(x) and not int(x) < 5)
k_lt5 = one("(k: <5)", "k", LT5)
k_37 = one("(k: 3..7)", "k", lambda x: canon(x) and 3 <= int(x) <= 7)
ca, cb, recab = G["ca"], G["cb"], G["recab"]
for p_ in (A, B, P, LST, RZ, AB, J, RP, RQ, R7):
    reg(p_)

print("\nPART 1: THE BATTERY, EACH OPTION ON THE SAME PROGRAMS (h-absent witnesses; counts over the pool)")
# (1a) two conditions on one label, pool A /a(?<h>\d)|b(?<k>\d)|c/ (21 subjects; h absent on b0-b9 and c)
print("   (1a) two conditions on one label, pool A (21 subjects, h absent on 11): holds-count; answer on `c`")
cases = [("(h = 0: <5) & (h = 0: >7)  [same default]", [(h_lt5, [C("0")]), (h_gt7, [C("0")])]),
         ("(h = 0: <5) & (h = 9: >7)  [different defaults]", [(h_lt5, [C("0")]), (h_gt7, [C("9")])]),
         ("(h = 0: <5) & (h: <3)      [one with, one without]", [(h_lt5, [C("0")]), (h_lt3, [None])]),
         ("(h: <3) & (h = 0: <5)      [the same, swapped]", [(h_lt3, [None]), (h_lt5, [C("0")])])]
for nm, prog in cases:
    print("      %-50s %s" % (nm, "; ".join("%s %s %s" % (o, cnt(run(prog, A, o)), hf(run(prog, A, o), A, "c"))
                                           for o in OPTS)))
dead = run([(h_lt5, [C("0")]), (h_gt7, [C("9")])], A, "POS") ^ run([(h_lt5, [C("0")]), (h_gt7, [None])], A, "POS")
print("      POS: the written `h = 9` in the second condition changes %d answers (it is DEAD: the first default "
      "already filled h)" % popc(dead))
# (1b) record vs its `&` spelling with a cross-entry `$a` (review r30 I), AB /(?<a>\d)?-(?<b>\d)/ (110)
rec = run([(recab, [C("0"), None])], AB, "LOCAL")
print("   (1b) record `(a = 0: <10, b: >$a)` (the record is ONE condition: LOCAL under every option) holds on %d; "
      "its `&` spelling `(a = 0: <10) & (b: >$a)`:" % popc(rec))
for o in OPTS:
    x = run([(ca, [C("0")]), (cb, [None])], AB, o)
    print("      %-7s holds %s, on `-1` %s; vs the record differ %s" % (o, cnt(x), hf(x, AB, "-1"), dif(x, rec, AB)))
# (1c) `$a` read later, and a computed label reading a (w := $a + 1, tested (w: >=1)); the predicate draft (rev 22)
# defines no replacement template, so that half of the battery item cannot be run
w1 = Cond("(w: >=1), w := $a + 1", [], lambda t, v: v.get("a") is not None and canon(v["a"]) and int(v["a"]) + 1 >= 1,
          reads=["a"])
for o in OPTS:
    x = run([(ca, [C("0")]), (w1, [])], AB, o)
    print("   (1c) computed label `w := $a + 1`, `(a = 0: <10) & (w: >=1)`, %-7s holds %s, on `-1` %s" % (
        o, cnt(x), hf(x, AB, "-1")))
xraw = vecE(ca, [C("0")], AB, {}) & vecE(w1, [], AB, {})
print("        COLUMN with w computed from the RAW a (SQL's select list: an alias is not visible to its sibling "
      "items) holds %d: the column reading must say which a a computed label reads" % popc(xraw))
# (1d) the order of `&`: every 2-condition program of rev 22's pools, each condition's marks replaced by one control
VARIANTS = [None, C("0"), C("4"), C("5"), C("9"), C("x")]
SEARCH = G["SEARCH"]


def ctl_of(c, var):
    return [var if ctl == "?" else (C(ctl[1]) if isinstance(ctl, tuple) else None) for _, ctl in c.labs]


nord = {o: [0, 0, None] for o in OPTS}
for pool, base, extra in SEARCH:
    pl = base + extra
    for i, j in itertools.combinations(range(len(pl)), 2):
        for v1 in VARIANTS:
            for v2 in VARIANTS:
                pr = [(pl[i], ctl_of(pl[i], v1)), (pl[j], ctl_of(pl[j], v2))]
                for o in OPTS:
                    a, b = run(pr, pool, o), run(pr[::-1], pool, o)
                    nord[o][0] += 1
                    if a != b:
                        nord[o][1] += 1
                        if nord[o][2] is None:
                            nord[o][2] = (pool.name, "%s [%s] & %s [%s]" % (pl[i].name, v1, pl[j].name, v2),
                                          "ERROR" if ERR in (a, b) else low(a ^ b, pool))
print("   (1d) the order of `&`: (2-condition program, controls) cases over rev 22's pools A, B, P, LST (+ condkind's "
      "EXTRA), each mark replaced by nothing or `= 0/4/5/9/\"x\"`: the answer moves when the two are swapped:")
for o in OPTS:
    print("      %-7s %d of %d%s" % (o, nord[o][1], nord[o][0], "" if nord[o][2] is None else
                                     "; first: pool %s `%s` at %r" % nord[o][2]))
xab, xba = run([(ca, [C("0")]), (cb, [None])], AB, "POS"), run([(cb, [None]), (ca, [C("0")])], AB, "POS")
print("      POS on AB: `(a = 0: <10) & (b: >$a)` holds %d, `(b: >$a) & (a = 0: <10)` holds %d: differ %s" % (
    popc(xab), popc(xba), dif(xab, xba, AB)))
# (1e) adding a condition never admits a subject: (1-2 condition program, added condition), controls per condition
mono = {o: [0, 0, 0, None] for o in OPTS}
for pool, base, extra in SEARCH:
    pl = base + extra
    for n_ in (1, 2):
        for combo in itertools.combinations(range(len(pl)), n_):
            for vb in VARIANTS:
                pr = [(pl[i], ctl_of(pl[i], vb)) for i in combo]
                for j in range(len(pl)):
                    if j in combo:
                        continue
                    for va in VARIANTS:
                        pr2 = pr + [(pl[j], ctl_of(pl[j], va))]
                        for o in OPTS:
                            a, b = run(pr, pool, o), run(pr2, pool, o)
                            mono[o][0] += 1
                            if ERR in (a, b):
                                mono[o][2] += 1
                                continue
                            if b & ~a:
                                mono[o][1] += 1
                                cand = (popc(b & ~a), " & ".join("%s [%s]" % (c.name, x) for c, x in pr),
                                        "%s [%s]" % (pl[j].name, va), pool.name, low(b & ~a, pool))
                                if mono[o][3] is None:
                                    mono[o][3] = cand
print("   (1e) adding a condition turns a FAIL into a HOLD: (program of 1-2 conditions, added condition) pairs, each "
      "condition's marks replaced by one control (nothing or `= 0/4/5/9/\"x\"`), pools A, B, P, LST (+ EXTRA):")
for o in OPTS:
    print("      %-7s %d of %d admit (and %d pairs are a compile ERROR: two defaults for one label)%s" % (
        o, mono[o][1], mono[o][0], mono[o][2], "" if mono[o][3] is None else
        "; first: `%s` + `%s` admits %d on pool %s, smallest %r" % mono[o][3][1:3] + (mono[o][3][0],) +
        mono[o][3][3:]))
pr = [(h_lt5, [None])]
for o in OPTS:
    a, b = run(pr, A, o), run(pr + [(h_lt9, [C("0")])], A, o)
    print("      %-7s pool A `(h: <5)` holds %d; + `(h = 0: <9)` holds %s (admits %s)" % (
        o, popc(a), cnt(b), "n/a" if b == ERR else popc(b & ~a)))
a, b = run([(cb, [None])], AB, "LOCAL"), run([(cb, [None]), (ca, [C("0")])], AB, "DOLLAR")
print("      DOLLAR  AB `(b: >$a)` holds %d; + `(a = 0: <10)` holds %d (admits %d, smallest %r)" % (
    popc(a), popc(b), popc(b & ~a), low(b & ~a, AB)))
# (1f) a label set inside a loop; zero passes; the group questions. RZ /(?<k>\d)(?:;(?<h>\d))*/, 1,110 subjects
# (10 with zero passes: `0`..`9`)
zp = sum(1 << i for i, s in enumerate(SRC["RZ"]) if ";" not in s)
some_h = Cond("some((h = 0: <5))", [("h", "")], lambda t, v: LT5(t[0]), kind="some")
none_h = Cond("occurs.none((h = 0: >7))", [("h", "")], lambda t, v: GT7(t[0]), kind="none")
rzh = one("(h: <5)", "h", LT5)
print("   (1f) RZ (1,110; 10 zero-pass subjects): a default written INSIDE a group question, a plain condition beside it")
for nm, prog in [("occurs.none((h = 0: >7)) & (h: <5)", [(none_h, [C("0")]), (rzh, [None])]),
                 ("some((h = 0: <5)) & (h: <5)", [(some_h, [C("0")]), (rzh, [None])]),
                 ("(h = 0: <5) alone", [(rzh, [C("0")])]),
                 ("(h = 0: <5) & (k: 3..7)", [(rzh, [C("0")]), (k_37, [None])])]:
    print("      %-40s %s" % (nm, "; ".join("%s %s (zero-pass %s, `3` %s)" % (
        o, cnt(x), "n/a" if x == ERR else popc(x & zp), hf(x, RZ, "3"))
        for o in OPTS + ("COLUMN-noLJ",) for x in [run(prog, RZ, o)])))
rec_rz = G["RZc"]
for o in ("LOCAL", "COLUMN", "COLUMN-noLJ"):
    x = run([(rec_rz, [C("0"), None])], RZ, o)
    print("      zero-pass-record `(h = 0: <5, k: 3..7)` %-11s holds %d; on `9` %s, on `3` %s" % (
        o, popc(x), hf(x, RZ, "9"), hf(x, RZ, "3")))
# (1g) the complement: a named program q with a default, and a default outside a complemented operand
print("   (1g) named programs and the complement, pool A (h absent on 11: b0-b9, c)")
q0 = [(h_lt5, [C("0")])]                                          # q := A & (h = 0: <5)
for o in OPTS:
    x1 = run(q0 + [(h_lt3, [None])], A, o)
    x2 = run(q0 + [(h_gt7, [C("9")])], A, o)
    x3 = rowmask(A) & compl(q0, A, o)
    print("      %-7s q & (h: <3): %s %s | q & (h = 9: >7): %s %s | A & !q: %s %s" % (
        o, cnt(x1), hf(x1, A, "c"), cnt(x2), hf(x2, A, "c"), cnt(x3), hf(x3, A, "c")))
S_ = [(h_lt9, [C("0")])]                                          # S := A & (h = 0: <9); q1 := A & (h: <5)
q1 = [(h_lt5, [None])]
for o in OPTS + ("COLUMN-b2",):
    oo = "COLUMN" if o == "COLUMN-b2" else o
    seed = merge(S_) if o == "COLUMN-b2" else None
    sq = run(S_ + q1, A, oo)
    snq = run(S_, A, oo) & compl(q1, A, oo, seed=seed)
    setc = run(S_ + [(h_nlt5, [None])], A, oo)
    print("      %-9s S & q1 holds %s, S & !q1 holds %s: BOTH on %s (`c`: %s / %s); S & (h: !(<5)) holds %s: vs "
          "S & !q1 differ %s" % (o, cnt(sq), cnt(snq), "n/a" if ERR in (sq, snq) else popc(sq & snq),
                                 hf(sq, A, "c"), hf(snq, A, "c"), cnt(setc), dif(setc, snq, A)))
# (1h) `when(c, p)` = (x & c & p) | (x & !(x & c)), AB, c = (a = 0: <10), p = (b: >$a)
for o in OPTS:
    br1 = run([(ca, [C("0")]), (cb, [None])], AB, o)
    br2 = rowmask(AB) & compl([(ca, [C("0")])], AB, o)
    x = ERR if ERR in (br1, br2) else br1 | br2
    print("   (1h) when((a = 0: <10), (b: >$a)) on AB, %-7s holds %s; on `-1` %s" % (o, cnt(x), hf(x, AB, "-1")))
# (1i) a condition that admits every row is the identity: pool A `(h = 0: <10) & (h: <5)` vs `(h: <5)`
for o in OPTS:
    a, b = run([(h_lt10, [C("0")]), (h_lt5, [None])], A, o), run([(h_lt5, [None])], A, o)
    print("   (1i) %-7s `(h = 0: <10)` admits %d of 21 alone; `(h = 0: <10) & (h: <5)` vs `(h: <5)` differ %s" % (
        o, popc(run([(h_lt10, [C("0")])], A, o)), dif(a, b, A)))
# (1j) equal behaviour (review r30 RULING-2, RULING-7) with defaults, per option
C1, C2, JT = G["C1"], G["C2"], G["JT"]
r2 = {o: [0, 0] for o in OPTS}
r7 = {o: [0, 0] for o in OPTS}
DV = [None] + [C(x) for x in D + ["", "x", "99"]]
for v1 in DV:
    for v2 in DV:
        for o in OPTS:
            a, b = run([(C1, [v1, None]), (C2, [v2])], RP, o), run([(C1, [v1, None]), (C2, [v2])], RQ, o)
            pa, pb = run([(C1, [v1, None])], RP, o), run([(C1, [v1, None])], RQ, o)
            if ERR in (a, b, pa, pb):
                continue
            rp = {r.subj: r.once for i, r in enumerate(RP.rows) if pa >> SRC["R2P"].index(r.subj) & 1}
            rq = {r.subj: r.once for i, r in enumerate(RQ.rows) if pb >> SRC["R2Q"].index(r.subj) & 1}
            if rp != rq:
                continue
            r2[o][0] += 1
            r2[o][1] += popc(a ^ b)
            x = run([(JT, [v1, None]), (C2, [v2])], R7, o)
            y = run([(one("(h: <5)", "h", LT5), [v1]), (one("(k: <5)", "k", LT5), [None]), (C2, [v2])], R7, o)
            r7[o][0] += 1
            r7[o][1] += popc(x ^ y)
print("   (1j) review r30 RULING-2 (P & C1' vs Q & C1', same rows, then & (j = w: <5)) and RULING-7 (product joint vs "
      "its record = `&` beside (j = w: <5)), v, w over nothing, 0-9, \"\", \"x\", \"99\":")
for o in OPTS:
    print("      %-7s RULING-2 %d (v, w) pairs with the same rows, differ %d; RULING-7 differ %d" % (
        o, r2[o][0], r2[o][1], r7[o][1]))
# (1k) what one must READ to know which value a condition tests: (program, condition) cases whose own answer changes
# when it is read inside its statement rather than alone (pools A, B, P, LST + EXTRA, 2-3 conditions, controls per
# condition from VARIANTS restricted to nothing / `= 0` / `= 9` to keep the run short)
V3 = [None, C("0"), C("9")]
rd = {o: [0, 0] for o in ("COLUMN", "POS")}
for pool, base, extra in SEARCH:
    pl = base + extra
    for n_ in (2, 3):
        for combo in itertools.combinations(range(len(pl)), n_):
            for vs in itertools.product(V3, repeat=n_):
                pr = [(pl[i], ctl_of(pl[i], v)) for i, v in zip(combo, vs)]
                envc = merge(pr)
                for k_, (c, ct) in enumerate(pr):
                    alone = vecE(c, ct, pool, {})
                    rd["COLUMN"][0] += 1
                    if envc != ERR and vecE(c, nones(c), pool, envc) != alone:
                        rd["COLUMN"][1] += 1
                    envp = {}
                    for c2, ct2 in pr[:k_ + 1]:
                        for (l, _), x in zip(c2.labs, ct2):
                            if x is not None and l not in envp:
                                envp[l] = x
                    rd["POS"][0] += 1
                    if vecE(c, nones(c), pool, envp) != alone:
                        rd["POS"][1] += 1
print("   (1k) reading a condition ALONE vs inside its statement (2-3 conditions, controls nothing / `= 0` / `= 9`): "
      "the condition's own answer moves in COLUMN %d of %d (program, condition) cases, POS %d of %d; LOCAL 0 by "
      "construction" % (rd["COLUMN"][1], rd["COLUMN"][0], rd["POS"][1], rd["POS"][0]))

# =====================================================================================================================
print("\nPART 2: THE REWRITE RUN UNDER EACH OPTION (condkind2's 339 marked programs; target = rev 22's answers)")
progs = G["progs"]


def choices(pool, lab):
    return [None] + [C(v) for v in consts(pool, lab)] + \
        [("$", x) for x in pool.labels if x != lab and never_absent(pool, x)]


def occs(prog):
    return [(ci, li) for ci, c in enumerate(prog) for li, (l, ctl) in enumerate(c.labs) if ctl == "?"]


def build(prog, assign, per_label):
    out = []
    for ci, c in enumerate(prog):
        ct = []
        for li, (l, ctl) in enumerate(c.labs):
            if ctl == "?":
                ct.append(assign[l] if per_label else assign[(ci, li)])
            else:
                ct.append(C(ctl[1]) if isinstance(ctl, tuple) else None)
        out.append((c, ct))
    return out


def wr(prog, assign, per_label):
    if per_label:
        return " ".join("%s=%s" % (l, G["cs"](x)) for l, x in sorted(assign.items()))
    return " | ".join("%s=%s" % (prog[ci].labs[li][0], G["cs"](x)) for (ci, li), x in sorted(assign.items()))


def search(prog, pool, target, opt, order=None):
    """first exact rewrite in a fixed canonical enumeration (fewest defaults first is NOT attempted: the first exact
    one in product order is reported); returns (assignment text or None, best (off, witness))"""
    per_label = opt == "COLUMN"
    oc = occs(prog)
    keys = sorted({prog[ci].labs[li][0] for ci, li in oc}) if per_label else oc
    lab = (lambda k: k) if per_label else (lambda k: prog[k[0]].labs[k[1]][0])
    best = None
    for combo in itertools.product(*[choices(pool, lab(k)) for k in keys]):
        a = dict(zip(keys, combo))
        pr = build(prog, a, per_label)
        if order is not None:
            pr = [pr[i] for i in order]
        v = run(pr, pool, opt)
        if v == ERR:
            continue
        d = v ^ target
        if not d:
            return wr(prog, a, per_label), (0, None)
        if best is None or popc(d) < best[0]:
            best = (popc(d), low(d, pool))
    return None, best


RES = {}
for st, pool, nm, prog, target, key in progs:
    row = {}
    for o in ("LOCAL", "COLUMN", "POS", "DOLLAR"):
        row[o] = search(prog, pool, target, o)
    if row["POS"][0] is None and len(prog) > 1:
        for perm in itertools.permutations(range(len(prog))):
            s_, _ = search(prog, pool, target, "POS", order=list(perm))
            if s_:
                row["POS-any"] = (s_ + " (order %s)" % (perm,), (0, None))
                break
    RES[(st, pool.name, nm)] = row
for st in ("REV22", "WORKED", "PROBE"):
    ks = [k for k in RES if k[0] == st]
    line = []
    for o in ("LOCAL", "COLUMN", "POS", "DOLLAR"):
        line.append("%s %d" % (o, sum(1 for k in ks if RES[k][o][0] is not None)))
    line.append("POS in some order %d" % sum(1 for k in ks if RES[k]["POS"][0] is not None or "POS-any" in RES[k]))
    print("   [%s] %d programs; rewrite exactly (constant or a never-absent `$x` default): %s" % (st, len(ks),
                                                                                              ", ".join(line)))
print("   programs that do NOT rewrite under COLUMN (best one-default-per-label: subjects off, smallest), with LOCAL's "
      "rewrite:")
for k in sorted(RES, key=lambda k: (k[0], k[1], k[2])):
    r = RES[k]
    if r["COLUMN"][0] is None:
        print("      %-6s %-4s %-50s COLUMN off %s at %r; LOCAL %s" % (k[0], k[1], k[2], r["COLUMN"][1][0],
                                                                       r["COLUMN"][1][1], r["LOCAL"][0]))
print("   programs that do NOT rewrite under LOCAL:")
for k in sorted(RES, key=lambda k: (k[0], k[1], k[2])):
    if RES[k]["LOCAL"][0] is None:
        print("      %-6s %-4s %-50s off %s at %r" % (k[0], k[1], k[2], RES[k]["LOCAL"][1][0], RES[k]["LOCAL"][1][1]))
print("   programs that rewrite under LOCAL but not POS in the written order (and whether some order works):")
for k in sorted(RES, key=lambda k: (k[0], k[1], k[2])):
    r = RES[k]
    if r["LOCAL"][0] is not None and r["POS"][0] is None:
        print("      %-6s %-4s %-50s POS-any %s" % (k[0], k[1], k[2], r.get("POS-any", (None,))[0]))
# DECL: ONE declared default per label for EVERY program of the pool (the declaration is part of the pattern)
print("   DECL (one declared default per label per POOL, every condition reads it): the best declaration per pool")
bypool = {}
for st, pool, nm, prog, target, key in progs:
    bypool.setdefault((st, pool.name), (pool, []))[1].append((nm, prog, target))
tot = [0, 0]
for (st, pn), (pool, lst) in sorted(bypool.items(), key=lambda kv: kv[0]):
    labs = sorted({c.labs[li][0] for _, prog, _ in lst for ci, li in occs(prog) for c in [prog[ci]]})
    best = None
    for combo in itertools.product(*[choices(pool, l) for l in labs]):
        env = {l: x for l, x in zip(labs, combo) if x is not None}
        ok = sum(1 for nm, prog, target in lst if run([(c, nones(c)) for c in prog], pool, "DECL",
                                                     decl=env) == target)
        cand = (-ok, wr(None, dict(zip(labs, combo)), True))
        if best is None or cand < best:
            best = cand
    tot[0] += -best[0]
    tot[1] += len(lst)
    print("      %-6s %-4s %3d programs: best declaration `%s` reproduces %d" % (st, pn, len(lst), best[1], -best[0]))
print("   DECL total: %d of %d programs reproduced by one declaration per pool" % tuple(tot))

# =====================================================================================================================
print("\nPART 3: \"ALL\" WITHOUT THE MARK")
# A1: all(c) = c (the plain condition: every pass, at least one; the LEFT JOIN row on zero passes);
# A2: all(c) = every pass passes c, VACUOUSLY on zero passes (SQL's ALL / NOT EXISTS over the nested pass table).
# The independent control: the hits of occurrences(/(?<g>a)?b/) over the 127 strings on {a, b} up to length 6, and
# the intent "every hit's g is `a`, possibly none" computed directly from Python `re.finditer` (rev 22 §4.3 runs the
# same population against an ENGINE-RUN regex: 0 for `occurs.none((g = "": !"a"))`, 94 for `occurs.none((g: !"a"))`,
# 7 for the plain `(g: "a")`).
OCCS = ["".join(t) for n in range(7) for t in itertools.product("ab", repeat=n)]
OCC = reg(Pool("OCC", OCCS, lambda s: Row(s, {}, [{"g": m.group("g")} for m in re.finditer(r"(?P<g>a)?b", s)]),
               looped=["g"]))
intent = sum(1 << i for i, s in enumerate(SRC["OCC"])
             if all(m.group("g") == "a" for m in re.finditer(r"(?P<g>a)?b", s)))
ga = Cond("(g: \"a\")", [("g", "")], lambda t, v: t[0] == "a")
ga_all = Cond("all((g: \"a\"))", [("g", "")], lambda t, v: t[0] == "a", kind="allv")
gn = Cond("occurs.none((g: !\"a\"))", [("g", "")], lambda t, v: t[0] != "a", kind="none")
print("   OCC (%d strings): intent holds on %d" % (len(OCCS), popc(intent)))
for nm, c, ct in [("A1 = plain (g: \"a\")", ga, [None]), ("A2 all((g: \"a\")), vacuous", ga_all, [None]),
                  ("occurs.none((g = \"\": !\"a\"))", gn, [C("")]), ("occurs.none((g: !\"a\"))", gn, [None]),
                  ("A2 all((g = \"a\": \"a\"))", ga_all, [C("a")])]:
    x = vecE(c, ct, OCC, {})
    print("      %-34s vs the intent differ %s" % (nm, dif(x, intent, OCC)))
rz_all = Cond("all((h: <5))", [("h", "")], lambda t, v: LT5(t[0]), kind="allv")
for ct in ([None], [C("0")], [C("9")]):
    a, b = vecE(rzh, ct, RZ, {}), vecE(rz_all, ct, RZ, {})
    print("   RZ (1,110): `(h%s: <5)` holds %d, A2 `all((h%s: <5))` holds %d: differ %s (zero-pass subjects in the "
          "difference: %d)" % ("" if ct[0] is None else " = " + ct[0][1], popc(a), "" if ct[0] is None else
                               " = " + ct[0][1], popc(b), dif(a, b, RZ), popc((a ^ b) & zp)))
print("\nEND")
