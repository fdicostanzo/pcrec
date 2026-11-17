# condkind2: evidence for docs/design/condition_kind.md Part II ("the model without the mark", an EXPLORATION, rules
# nothing) and docs/dev/lanes/condkind2_report.md (lane condkind2, 2026-11-16; design only).
#
# THE NO-MARK MODEL (the owner's 21:16 question, COND-FAMILY: "Absence is a null which never matches. Use the default
# to get past it"): a label control is NOTHING (an absent label is NULL; a test holding a NULL is UNKNOWN; the row is
# dropped) or a DEFAULT (COALESCE: the absent label reads as the default's value). There is no mark. Every condition
# is then a test of ONE result row (condkind's S1 source row, R1 result row: passes are a nested table, a plain
# condition reads the LEFT JOIN row on zero passes, a group question counts real passes).
#
# THIS SCRIPT exec's lane condkind's engine (condkind_evidence/condkind_model.py, unedited, its output suppressed) for
# its pools, its condition codings and its rev 22 reference (rev22_ref.py's TSV for rev 22's own pools A, B, P, LST;
# condkind's M2c candidate, which equals rev 22's engine on all 346 of those programs, for the worked-example pools),
# then evaluates the no-mark model with its OWN small evaluator (nm_cond below; condkind's evaluator is not used for
# no-mark answers).
#
# PARTS: 1 the model's properties by run (order, monotone, record = `&`, equal behaviour, some/none, one-witness);
#        2 THE REWRITE RUN: every marked program, searched for a defaults-only rewrite giving rev 22's answer on every
#          subject of its pool, by tier (T0 one constant per label; T1 a constant per occurrence; T2 + a `$x` default
#          whose x is never absent (legal in rev 22, §4.1 errors); T3 + `$x` for any x and `$x+1` / `$x-1` (NOT legal
#          today: an expression default, or a default that can itself be absent); T4 a free value per row and pass
#          (no default at all: an arbitrary function of the row, the upper bound));
#        3 the default's scope alternatives; 4 silent drift.
#
# Run from the scratch dir ($PCREC_TMPDIR/scratch/condkind2/), W = the worktree root:
#   timeout 300 python3 -I W/docs/dev/lanes/condkind_evidence/rev22_ref.py rev22_ref.tsv
#   timeout 900 python3 -I W/docs/dev/lanes/condkind2_evidence/condkind2_nomark.py rev22_ref.tsv > fwd.out
#   CONDKIND2_SWAP=1 timeout 900 python3 -I W/.../condkind2_nomark.py rev22_ref.tsv > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   CONDKIND2_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# CONDKIND2_SWAP=1 also sets CONDKIND_SWAP=1 for the exec'd engine, so its pools and orders reverse too.
import contextlib, io, itertools, os, sys

SWAP = os.environ.get("CONDKIND2_SWAP") == "1"
SAB = os.environ.get("CONDKIND2_SABOTAGE") == "1"
os.environ["CONDKIND_SWAP"] = "1" if SWAP else "0"
os.environ["CONDKIND_SABOTAGE"] = "0"
HERE = os.path.dirname(os.path.abspath(__file__))
CK = os.path.join(os.path.dirname(HERE), "condkind_evidence", "condkind_model.py")
REFTSV = sys.argv[1]
G = {"__name__": "condkind_model", "__file__": CK}
_argv, sys.argv = sys.argv, [CK, REFTSV]
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(CK).read(), CK, "exec"), G)
sys.argv = _argv
print("ORDER: %s%s" % ("SWAPPED (every order reversed, the engine's too)" if SWAP else "forward",
                       "; SABOTAGE ON" if SAB else ""))
O, views, Cond, Pool, rx_pool, ans, CTX = G["O"], G["views"], G["Cond"], G["Pool"], G["rx_pool"], G["ans"], G["CTX"]
canon, num, sm, hf, D, UNIV = G["canon"], G["num"], G["sm"], G["hf"], G["D"], G["UNIV"]
LT5, GT7, LT3 = G["LT5"], G["GT7"], G["LT3"]
one = G["one"]


# ------------------------------------------------------------------------------------------- the no-mark evaluator
# a control: None (nothing: NULL), ("c", v) a constant default, ("$", x) a `$x` default, ("$+", x, d) `$x` + d.
def dval(ctl, view):
    if ctl[0] == "c":
        return ctl[1]
    x = view.get(ctl[1])
    if x is None:
        return None                                        # the default is itself absent: NULL
    if ctl[0] == "$":
        return x
    if not x.isdigit():
        return None
    n = int(x) + ctl[2]
    return str(n) if n >= 0 else None


def nm_pass(c, labs, view):
    """one pass: the tuple, absent labels COALESCEd with their defaults; any NULL left -> UNKNOWN -> False"""
    order = O(range(len(labs)))
    t = [None] * len(labs)
    for i in order:
        l, ctl = labs[i]
        v = view.get(l)
        if v is None and ctl is not None:
            # SABOTAGE: an order-dependent evaluator (only the first label in evaluation order gets its default)
            if SAB and i != order[0]:
                return False
            v = dval(ctl, view)
        if v is None:
            return False
        t[i] = v
    return bool(c.R(tuple(t), view))


def nm_cond(c, labs, row, pool):
    group = c.kind in ("some", "none", "at_most")
    vals = [nm_pass(c, labs, v) for v in O(views(c, labs, row, pool, group))]
    if c.kind == "plain":
        return all(vals)
    k = sum(vals)
    return {"some": k >= 1, "none": k == 0, "at_most": k <= (c.n or 0)}[c.kind]


def base_ctls(c):
    """the condition's controls with the marks still in place ("?"); a written default -> ("c", v)"""
    return [None if ctl == "" else (("c", ctl[1]) if isinstance(ctl, tuple) else "?") for _, ctl in c.labs]


def vec(c, ctls, pool):
    """bitmask over pool.source (fixed sorted order) of the subjects whose row passes c under the given controls"""
    key = (id(c), pool.name, tuple(ctls))
    if key not in VC:
        KEEP.append(c)                                    # keep c alive: its id() is part of the cache key
        labs = [(l, ctl) for (l, _), ctl in zip(c.labs, ctls)]
        rows = {r.subj: r for r in pool.rows}
        b = 0
        for i, s in enumerate(SRC[pool.name]):
            if s in rows and nm_cond(c, labs, rows[s], pool):
                b |= 1 << i
        VC[key] = b
    return VC[key]


VC, SRC, KEEP = {}, {}, []


def reg(pool):
    SRC[pool.name] = sorted(pool.source, key=lambda s: (len(s), s))
    return pool


def tvec(ansd, pool):
    return sum(1 << i for i, s in enumerate(SRC[pool.name]) if ansd[s])


def popc(x):
    return bin(x).count("1")


def low(x, pool):
    """the smallest subject in a difference bitmask"""
    return SRC[pool.name][(x & -x).bit_length() - 1] if x else None


# ----------------------------------------------------------------------------------------------- the pools used
A, B, P, LST, T2, ZE, MN, J, BR, RZ = (G[n] for n in ("A", "B", "P", "LST", "T2", "ZE", "MN", "J", "BR", "RZ"))
RP, RQ, S9, R7 = G["RP"], G["RQ"], G["S9"], G["R7"]
for p in (A, B, P, LST, T2, ZE, MN, J, BR, RZ, RP, RQ, S9, R7):
    reg(p)
OUT_VALS = ["", "x", "99"]                     # values no label of these pools holds (sentinels)


def consts(pool, lab):
    return sorted(pool.rdom[lab], key=lambda s: (len(s), s)) + OUT_VALS


def never_absent(pool, lab):
    """x is never absent where a pass reads it: present in every row's set-once labels or every pass"""
    for r in pool.rows:
        if lab in pool.looped:
            if not r.passes or any(p.get(lab) is None for p in r.passes):
                return False
        elif r.once.get(lab) is None:
            return False
    return True


def choices(pool, lab, tier):
    ch = [None] + [("c", v) for v in consts(pool, lab)]
    if tier >= 2:
        ch += [("$", x) for x in pool.labels if x != lab and never_absent(pool, x)]
    if tier >= 3:
        ch += [("$", x) for x in pool.labels if x != lab and not never_absent(pool, x)]
        ch += [("$+", x, d) for x in pool.labels if x != lab for d in (1, -1)]
    return ch


# ------------------------------------------------------------------------------------------------ the rewrite search
def occs(prog):
    return [(ci, li) for ci, c in enumerate(prog) for li, (l, ctl) in enumerate(c.labs) if ctl == "?"]


def fill(c, ctls, ci, assign):
    out = list(ctls)
    for li in range(len(out)):
        if out[li] == "?":
            out[li] = assign[(ci, li)]
    return out


def search_t0(prog, pool, target):
    """one constant (or nothing) per LABEL, the same in every condition; returns (exact solutions, best diff, witness)"""
    labs = sorted({c.labs[li][0] for ci, li in occs(prog) for c in [prog[ci]]})
    full = (1 << len(SRC[pool.name])) - 1
    sols, best = [], None
    for combo in itertools.product(*[O([None] + [("c", v) for v in consts(pool, l)]) for l in labs]):
        a = dict(zip(labs, combo))
        v = full
        for ci, c in enumerate(prog):
            v &= vec(c, [a[c.labs[li][0]] if x == "?" else x for li, x in enumerate(base_ctls(c))], pool)
        d = v ^ target
        if not d:
            sols.append(a)
        if best is None or (popc(d), str(sorted(a.items(), key=str))) < best[:2]:
            best = (popc(d), str(sorted(a.items(), key=str)), low(d, pool))
    return sols, best


def search_t(prog, pool, target, tier):
    """a control per OCCURRENCE (each marked label in each condition its own) from tier's choices; True if some
    assignment gives exactly the target"""
    full = (1 << len(SRC[pool.name])) - 1
    per = []
    for ci, c in enumerate(prog):
        bc = base_ctls(c)
        mi = [li for li, x in enumerate(bc) if x == "?"]
        vs = {}
        for combo in itertools.product(*[O(choices(pool, c.labs[li][0], tier)) for li in mi]):
            v = vec(c, fill(bc, bc, ci, dict(((ci, li), x) for li, x in zip(mi, combo))), pool)
            if v & target == target:                      # every condition must keep every target subject
                w = ",".join("%s=%s" % (c.labs[li][0], cs(x)) for li, x in zip(mi, combo))
                vs[v] = min(vs.get(v, w), w, key=lambda z: (len(z), z))
        if not vs:
            return None
        per.append(sorted(vs.items()))
    found = []
    for combo in itertools.product(*per):
        v = full
        for x, _ in combo:
            v &= x
        if v == target:
            found.append(" | ".join(w for _, w in combo))
    return min(found, key=lambda z: (len(z), z)) if found else None


def cs(x):
    """a control, written"""
    if x is None:
        return "nothing"
    if x[0] == "c":
        return repr(x[1])
    return "$" + x[1] if x[0] == "$" else "$%s%+d" % (x[1], x[2])


def t4_feasible(prog, pool, target):
    """no default at all: a free value per row and pass for every absent marked label (an arbitrary function of the
    row; condkind's UNIV + the label's values). Returns the bitmask of subjects where the target is reachable"""
    rows = {r.subj: r for r in pool.rows}
    ok = 0
    for i, s in enumerate(SRC[pool.name]):
        want = bool(target >> i & 1)
        if s not in rows:
            ok |= (not want) << i
            continue
        cT, cF = [], []
        for c in prog:
            group = c.kind in ("some", "none", "at_most")
            pv = []
            for v in O(views(c, c.labs, rows[s], pool, group)):
                free = [li for li, (l, ctl) in enumerate(c.labs) if ctl == "?" and v.get(l) is None]
                seen = set()
                univ = sorted(set(UNIV) | set().union(*[pool.rdom[c.labs[li][0]] for li in free]) if free else {""})
                for combo in itertools.product(*[univ for _ in free]):
                    labs = [(l, ("c", combo[free.index(li)]) if li in free else base_ctls(c)[li] if base_ctls(c)[li]
                             != "?" else None) for li, (l, _) in enumerate(c.labs)]
                    seen.add(nm_pass(c, labs, v))
                    if len(seen) == 2:
                        break
                pv.append((True in seen, False in seen))
            if c.kind == "plain":
                t, f = all(x[0] for x in pv), any(x[1] for x in pv)
            elif c.kind == "some":
                t, f = any(x[0] for x in pv), all(x[1] for x in pv)
            elif c.kind == "none":
                t, f = all(x[1] for x in pv), any(x[0] for x in pv)
            else:
                forced = sum(1 for x in pv if x[0] and not x[1])
                t, f = forced <= (c.n or 0), sum(1 for x in pv if x[0]) > (c.n or 0)
            cT.append(t)
            cF.append(f)
        if (want and all(cT)) or (not want and any(cF)):
            ok |= 1 << i
    return ok


# =====================================================================================================================
print("\nPART 1: THE MODEL WITHOUT THE MARK, ITS PROPERTIES BY RUN")
SEARCH = G["SEARCH"]
# (1a) monotone: every program of 1-3 conditions of rev 22's pools (+ condkind's EXTRA), each mark replaced by one
# control (nothing, or the default 0, 4, 5, 9, "x"), never sees a FAIL turn into a HOLD when a condition is added
VARIANTS = [None, ("c", "0"), ("c", "4"), ("c", "5"), ("c", "9"), ("c", "x")]
npairs = nmoved = nprog = 0
for pool, base, extra in SEARCH:
    reg(pool)
    pl = base + extra
    for var in VARIANTS:
        vv = {i: vec(c, [var if x == "?" else x for x in base_ctls(c)], pool) for i, c in enumerate(pl)}
        full = (1 << len(SRC[pool.name])) - 1
        for n_ in (1, 2):
            for combo in itertools.combinations(range(len(pl)), n_):
                a = full
                for i in combo:
                    a &= vv[i]
                nprog += 1
                for j in range(len(pl)):
                    if j in combo:
                        continue
                    npairs += 1
                    if (a & vv[j]) & ~a:
                        nmoved += 1
print("   (1a) monotone: %d (program, added condition) pairs over %d programs (rev 22's pools + condkind's EXTRA, each "
      "mark replaced by nothing or by `= 0`/`= 4`/`= 5`/`= 9`/`= \"x\"`): FAIL -> HOLD in %d" % (npairs, nprog, nmoved))
# (1b) record = `&` with a default, and the default reaching a `$` across `&` (review r30 I)
RZc = G["rec"]
rz_rec = Cond("(h = v: <5, k: 3..7)", [("h", "?"), ("k", "")], RZc.R)
rz_h = Cond("(h = v: <5)", [("h", "?")], lambda t, v: LT5(t[0]))
rz_k = Cond("(k: 3..7)", [("k", "")], lambda t, v: canon(t[0]) and 3 <= int(t[0]) <= 7)
d1 = 0
for vv_ in [None] + [("c", x) for x in D + OUT_VALS]:
    d1 += popc(vec(rz_rec, [vv_, None], RZ) ^ (vec(rz_h, [vv_], RZ) & vec(rz_k, [None], RZ)))
print("   (1b) record = `&` on RZ (1,110 subjects, h looped, zero passes included): `(h = v: <5, k: 3..7)` vs "
      "`(h = v: <5) & (k: 3..7)` over v in nothing, 0-9, \"\", \"x\", \"99\": differ on %d subject-variant pairs" % d1)
AB = reg(rx_pool("AB", r"(?P<a>\d)?-(?P<b>\d)", [a + "-" + b for a in [""] + D for b in D]))
recab = Cond("(a = 0: <10, b: >$a)", [("a", ("=", "0")), ("b", "")],
             lambda t, v: canon(t[0]) and int(t[0]) < 10 and canon(t[1]) and int(t[1]) > int(t[0]))
ca = Cond("(a = 0: <10)", [("a", ("=", "0"))], lambda t, v: canon(t[0]) and int(t[0]) < 10)
cb = Cond("(b: >$a)", [("b", "")], lambda t, v: v.get("a") is not None and canon(t[0]) and int(t[0]) > int(v["a"]),
          reads=["a"])
rec_v = vec(recab, base_ctls(recab), AB)
and_L = vec(ca, base_ctls(ca), AB) & vec(cb, [None], AB)


def coalesce_pool(pool, lab, v, name):
    """the default as a rewrite of the STATEMENT's column (`select coalesce(a, v) as a`): every reader sees v"""
    rows = [G["Row"](r.subj, {k: (v if k == lab and x is None else x) for k, x in r.once.items()}, r.passes)
            for r in pool.rows]
    q = Pool(name, pool.source, lambda s: next((r for r in rows if r.subj == s), None))
    return reg(q)


ABg = coalesce_pool(AB, "a", "0", "ABg")
and_G = vec(ca, base_ctls(ca), ABg) & vec(cb, [None], ABg)
print("   (1c) review r30 I (dollar-across-and), /(?<a>\\d)?-(?<b>\\d)/, %d subjects: the record `(a = 0: <10, b: >$a)` "
      "holds on %d; its `&` spelling with the default LOCAL to its condition on %d (differ %d, smallest %r); with the "
      "default a rewrite of the STATEMENT's column on %d (differ %d)" % (
          len(AB.source), popc(rec_v), popc(and_L), popc(rec_v ^ and_L), low(rec_v ^ and_L, AB), popc(and_G),
          popc(rec_v ^ and_G)))
# (1d) equal behaviour: review r30 RULING-2's pair, RULING-7's joint vs record, SIMULATE-9, with every mark a default
C1, C2, JT = G["C1"], G["C2"], G["JT"]
sp = sd = 0
for v1 in [None] + [("c", x) for x in D + OUT_VALS]:
    pr = vec(C1, [v1, None], RP)
    qr = vec(C1, [v1, None], RQ)
    rowsP = {r.subj: r.once for r in RP.rows}
    rowsQ = {r.subj: r.once for r in RQ.rows}
    sameP = {s: rowsP[s] for i, s in enumerate(SRC["R2P"]) if pr >> i & 1}
    sameQ = {s: rowsQ[s] for i, s in enumerate(SRC["R2Q"]) if qr >> i & 1}
    if sameP != sameQ:
        continue
    for v2 in [None] + [("c", x) for x in D + OUT_VALS]:
        sp += 1
        sd += popc((pr & vec(C2, [v2], RP)) ^ (qr & vec(C2, [v2], RQ)))
print("   (1d) RULING-2: P & C1' and Q & C1' with C1' = ((h = v, k): h < k) and the same rows, then & (j = w: <5): %d "
      "(v, w) pairs, differ on %d subjects in all (rev 22: 54 of 1,210 with the marks)" % (sp, sd))
r7 = 0
for v1 in [None] + [("c", x) for x in D + OUT_VALS]:
    for v2 in [None, ("c", "0"), ("c", "9"), ("c", "x")]:
        a = vec(JT, [v1, None], R7) & vec(C2, [v2], R7)
        b = vec(one("(h?: <5)", "h", LT5, "?"), [v1], R7) & vec(one("(k: <5)", "k", LT5), [None], R7) & vec(C2, [v2], R7)
        r7 += popc(a ^ b)
print("        RULING-7: the product joint ((h = v, k): (<5, <5)) vs its record = `&` spelling, beside (j = w: <5), 56 "
      "(v, w) pairs over %d rows: differ on %d (rev 22 with marks: 30 of 355)" % (len(R7.rows), r7))
s9 = [popc(vec(C1, [v1, None], S9) & vec(one("(j?: <3)", "j", LT3, "?"), [("c", "0")], S9))
      for v1 in [None, ("c", "0"), ("c", "9")]]
print("        SIMULATE-9 `((h = v, k): h < k) & (j = 0: <3)`, 220 subjects, v = nothing / 0 / 9: holds on %s (the swap "
      "run must print the same)" % s9)
# (1e) some and none: never both hold
sn = 0
none_m, MLT = G["none_m"], G["MLT"]
for v1 in [None] + [("c", x) for x in D + OUT_VALS]:
    some_c = Cond("some", none_m.labs, MLT, kind="some")
    sn += popc(vec(some_c, [None, v1], LST) & vec(none_m, [None, v1], LST))
print("   (1e) review r30 E: `some(((h, m = v): m < h))` and `occurs.none(((h, m = v): m < h))` BOTH hold, 43 lists x 14 "
      "controls: %d (rev 22 with the mark: 14 of 43)" % sn)
# (1f) one-witness: two conditions vs one, one default vs two
# rebuilt here: condkind's script reuses the names c1/c2 for other values later on
c1 = Cond("(h?: <$k)", [("h", "?")], lambda t, v: canon(t[0]) and int(t[0]) < int(v["k"]), reads=["k"])
c2 = Cond("(h?: >$j)", [("h", "?")], lambda t, v: canon(t[0]) and int(t[0]) > int(v["j"]), reads=["j"])
c12 = Cond("(h?: >$j & <$k)", [("h", "?")], lambda t, v: canon(t[0]) and int(v["j"]) < int(t[0]) < int(v["k"]),
           reads=["j", "k"])
same = diff2 = 0
for v in D + OUT_VALS:
    same += popc((vec(c1, [("c", v)], J) & vec(c2, [("c", v)], J)) ^ vec(c12, [("c", v)], J))
two_d = vec(c1, [("c", "0")], J) & vec(c2, [("c", "9")], J) & ~vec(c12, [None], J)
one_v = vec(c12, [("$+", "j", 1)], J)                      # some one value between j and k exists (`$j+1` is one)
print("   (1f) one-witness, J (1,100): `(h = v: <$k) & (h = v: >$j)` vs `(h = v: >$j & <$k)`, v over 0-9 and 3 sentinels:"
      " differ %d; with TWO defaults, `(h = 0: <$k) & (h = 9: >$j)` holds on %d subjects with h absent, on %d of them "
      "(smallest %r) no one value is both below k and above j" % (same, popc(two_d), popc(two_d & ~one_v),
                                                                 low(two_d & ~one_v, J)))

# =====================================================================================================================
print("\nPART 2: THE REWRITE RUN (every marked program; target = rev 22's answers on every subject of its pool)")
REF = G["REF"]
progs = []                                               # (set, pool, name, prog, target bitmask)
for pool, base, extra in SEARCH:
    for n_ in (1, 2, 3):
        for combo in itertools.combinations(range(len(base)), n_):
            prog = [base[i] for i in combo]
            if not occs(prog):
                continue
            nm = " & ".join(c.name for c in prog)
            progs.append(("REV22", pool, nm, prog, tvec({s: REF[(pool.name, nm, s)] for s in pool.source}, pool),
                          (pool.name, combo)))
late_u, LATE, m30, lm = G["late_u"], G["LATE"], G["m30"], G["lm"]
hm5, kb = G["hm5"], G["kb"]
WORKED = [
    (T2, "((h, m?): late)", [lm]),
    (T2, "((h, m?): !late)", [Cond("((h, m?): !late)", [("h", ""), ("m", "?")], lambda t, v: not LATE(t, v))]),
    (T2, "((h, m?): late) & (m?: padded(<30))", [lm, m30]),
    (ZE, "(h?: <$a, k: 3)", [Cond("(h?: <$a, k: 3)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and v["a"] is not
                                  None and int(t[0]) < int(v["a"]) and t[1] == "3", reads=["a"])]),
    (RZ, "(h?: <5, k: 3..7)", [G["rec"]]),
    (RZ, "(h?: <5)", [one("(h?: <5)", "h", LT5, "?")]),
    (MN, "(mnum?: >5)", [one("(mnum?: >5)", "mnum", G["GT5"], "?")]),
    (MN, "(mnum?: <3)", [one("(mnum?: <3)", "mnum", LT3, "?")]),
    (J, "(h?: <$k)", [c1]),
    (J, "(h?: <$k) & (h?: >$j)", [c1, c2]),
    (J, "(h?: >$j & <$k)", [c12]),
    (BR, "P & (h?: <5)", [hm5]),
    (BR, "P & (k: \"b\") & (h?: <5)", [kb, hm5]),
    (BR, "P & ((k, h?): (\"b\", <5))", [Cond("((k, h?): (b, <5))", [("k", ""), ("h", "?")],
                                             lambda t, v: t[0] == "b" and LT5(t[1]))]),
    (LST, "occurs.none(((h, m?): m < h))", [none_m]),
    (LST, "occurs.none(((h, m?): m < h)) & (m?: >5)", [none_m, G["gt5m"]]),
    (RP, "R2 P & ((h?, k): h < k) & (j?: <5)", [C1, C2]),
    (RQ, "R2 Q & ((h?, k): h < k) & (j?: <5)", [C1, C2]),
    (S9, "S9 ((h?, k): h < k) & (j?: <3)", [C1, one("(j?: <3)", "j", LT3, "?")]),
    (R7, "R7 ((h?, k): (<5, <5)) & (j?: <5)", [JT, C2]),
    (R7, "R7 (h?: <5) & (k: <5) & (j?: <5)", [one("(h?: <5)", "h", LT5, "?"), one("(k: <5)", "k", LT5), C2]),
]
for pool, nm, prog in WORKED:
    progs.append(("WORKED", pool, nm, prog, tvec(ans(prog, pool, "M2c"), pool), (pool.name, nm)))
# PROBES, designed to defeat a constant default (the lane's own, run under condkind's M2c = rev 22's rule):
# a joint relation between an absent label and a present one, the absent label's values narrower than the other's
EQ = lambda t, v: canon(t[0]) and canon(t[1]) and t[0] == t[1]
H5 = reg(rx_pool("H5", r"(?P<h>[0-4])?-(?P<k>\d)", [h + "-" + k for h in [""] + D[:5] for k in D]))
B9 = reg(rx_pool("B9", r"(?P<h>\d)?-(?P<k>\d)", [h + "-" + k for h in [""] + D for k in D]))
heq = Cond("((h?, k): h == k)", [("h", "?"), ("k", "")], EQ)
PROBES = [(B9, "((h?, k): h == k), h and k both \\d", [heq]),
          (H5, "((h?, k): h == k), h [0-4], k \\d", [heq]),
          (H5, "((h?, k): h < k) & ((h?, k): h + 3 > k)", [
              Cond("((h?, k): h < k)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and canon(t[1]) and
                   int(t[0]) < int(t[1])),
              Cond("((h?, k): h + 3 > k)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and canon(t[1]) and
                   int(t[0]) + 3 > int(t[1]))]),
          (H5, "((h?, k): k - 3 < h < k)", [
              Cond("((h?, k): k - 3 < h < k)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and canon(t[1]) and
                   int(t[1]) - 3 < int(t[0]) < int(t[1]))])]
for pool, nm, prog in PROBES:
    progs.append(("PROBE", pool, nm, prog, tvec(ans(prog, pool, "M2c"), pool), (pool.name, nm)))
TIERS = ("T0", "T1", "T2", "T3", "T4", "NONE")
res, SOLS = [], {}
for st, pool, nm, prog, target, key in progs:
    sols, best = search_t0(prog, pool, target)
    sol = min(((not all(x is None for x in s_.values()), " ".join("%s=%s" % (l, cs(x)) for l, x in sorted(s_.items())))
               for s_ in sols), key=lambda z: (z[0], len(z[1]), z[1]))[1] if sols else ""
    SOLS[key] = sols
    if sols:
        nothing = any(all(x is None for x in s_.values()) for s_ in sols)
        indom = any(all(x is None or x[1] in pool.rdom[l] for l, x in s_.items()) for s_ in sols)
        tier = "T0"
        extra_ = ("NOTHING" if nothing else "") + ("" if indom else " OUT-OF-DOMAIN-ONLY")
    else:
        extra_ = ""
        tier = None
        for k, t in ((1, "T1"), (2, "T2"), (3, "T3")):
            sol = search_t(prog, pool, target, k)
            if sol:
                tier = t
                break
        if tier is None:
            sol = ""
            ok = t4_feasible(prog, pool, target)
            tier = "T4" if ok == (1 << len(SRC[pool.name])) - 1 else "NONE"
    res.append((st, pool.name, nm, tier, extra_.strip(), best, sol))
for st in ("REV22", "WORKED", "PROBE"):
    rs = [r for r in res if r[0] == st]
    cnt = {t: sum(1 for r in rs if r[3] == t) for t in TIERS}
    print("   [%s] %d marked programs; first tier that rewrites exactly: %s; T0 by NOTHING (the mark changed no answer): "
          "%d; T0 only with a default the label never holds: %d" % (
              st, len(rs), ", ".join("%s %d" % (t, cnt[t]) for t in TIERS),
              sum(1 for r in rs if "NOTHING" in r[4]), sum(1 for r in rs if "OUT-OF-DOMAIN-ONLY" in r[4])))
# is the rewrite COMPOSITIONAL? (program, program + one condition), both rewritten at T0: does some rewrite of the
# larger program keep a rewrite of the smaller one's labels unchanged?
npc = nfc = 0
wit = None
for (pn, combo), sols in sorted(SOLS.items(), key=lambda kv: str(kv[0])):
    if not isinstance(combo, tuple):
        continue
    for (pn2, combo2), sols2 in SOLS.items():
        if pn2 != pn or not isinstance(combo2, tuple) or len(combo2) != len(combo) + 1 or not set(combo) < set(combo2):
            continue
        if not sols or not sols2:
            continue
        npc += 1
        if not any(all(s2.get(l, "?") == x for l, x in s1.items()) for s1 in sols for s2 in sols2):
            nfc += 1
            cand = (len(combo2), pn, combo, combo2)
            wit = cand if wit is None or cand < wit else wit
names = {(st_, pn_, k_): nm_ for st_, p_, nm_, pr_, t_, (pn_, k_) in progs for _ in [0] if st_ == "REV22"}
print("   COMPOSITIONAL? %d (rev 22 program, the same + one condition) pairs, both rewritten at T0: in %d no rewrite of "
      "the larger keeps any rewrite of the smaller (the earlier default must CHANGE when a condition is added)%s" % (
          npc, nfc, "" if wit is None else "; smallest: `%s` -> `%s` (%s)" % (
              names[("REV22", wit[1], wit[2])], names[("REV22", wit[1], wit[3])], wit[1])))
print("   every program past T0 (tier; the best one-constant-per-label rewrite: subjects off, smallest):")
for st, pn, nm, tier, ex, best, sol in sorted(res, key=lambda r: (r[0], r[1], r[2])):
    if tier != "T0":
        print("      %-6s %-4s %-5s %-52s best T0 off %4d at %r" % (st, pn, tier, nm, best[0], best[2]))
print("   the WORKED programs, each:")
for st, pn, nm, tier, ex, best, sol in res:
    if st in ("WORKED", "PROBE"):
        print("      %-6s %-4s %-46s %-4s %-8s %s" % (st, pn, nm, tier, ex, sol))

# THE SENTINEL ROUTE: a default the label never holds, and the set extended BY HAND with the rows the mark's
# existential would have admitted (the projection of the set onto the other labels over the label's values)
sent = Cond("((h = \"x\", k): h == k | (h == \"x\" & k < 5))", [("h", ("=", "x")), ("k", "")],
            lambda t, v: canon(t[1]) and (t[0] == t[1] or (t[0] == "x" and int(t[1]) < 5)))
d_ = vec(sent, base_ctls(sent), H5) ^ tvec(ans([heq], H5, "M2c"), H5)
# (the lane's first hand projection wrote 1 <= k <= 7 and the run caught it: 1 subject off, `-7`; the author of a
# sentinel rewrite derives this projection by hand, which is the route's cost)
sent2 = Cond("((h = \"x\", k): k - 3 < h < k | (h == \"x\" & 1 <= k <= 6))", [("h", ("=", "x")), ("k", "")],
             lambda t, v: canon(t[1]) and ((canon(t[0]) and int(t[1]) - 3 < int(t[0]) < int(t[1])) or
                                           (t[0] == "x" and 1 <= int(t[1]) <= 6)))
d2_ = vec(sent2, base_ctls(sent2), H5) ^ tvec(ans(PROBES[3][2], H5, "M2c"), H5)
print("   THE SENTINEL ROUTE on H5, second probe: `((h = \"x\", k): k - 3 < h < k | (h == \"x\" & 1 <= k <= 6))` vs "
      "rev 22's `((h?, k): k - 3 < h < k)`: differ %d of %d" % (popc(d2_), len(H5.source)))
print("   THE SENTINEL ROUTE on H5: `((h = \"x\", k): h == k | (h == \"x\" & k < 5))` vs rev 22's `((h?, k): h == k)`:"
      " differ %d of %d" % (popc(d_), len(H5.source)))

# =====================================================================================================================
print("\nPART 3: THE DEFAULT'S SCOPE")
hd0 = one("(h = 0: <5)", "h", LT5, "?")
hd9 = one("(h = 9: >7)", "h", GT7, "?")
both = one("(h = v: <5 & >7)", "h", lambda x: LT5(x) and GT7(x), "?")
two = vec(hd0, [("c", "0")], A) & vec(hd9, [("c", "9")], A)
print("   (3a) two defaults for one label, pool A (21): `(h = 0: <5) & (h = 9: >7)` holds on %d (smallest %r), "
      "`(h = v: <5 & >7)` on %d for every v" % (popc(two), low(two, A),
                                                max(popc(vec(both, [("c", x)], A)) for x in D + OUT_VALS)))
cb2 = Cond("(b: >$a)", [("b", "")], lambda t, v: v.get("a") is not None and canon(t[0]) and int(t[0]) > int(v["a"]),
           reads=["a"])
pos_ab = vec(ca, base_ctls(ca), AB) & vec(cb2, [None], ABg)        # positional: the default reaches LATER readers
pos_ba = vec(cb2, [None], AB) & vec(ca, base_ctls(ca), AB)          # `(b: >$a)` first: it does not
print("   (3b) a default reaching later readers only (positional): `(a = 0: <10) & (b: >$a)` holds on %d, `(b: >$a) & "
      "(a = 0: <10)` on %d: differ %d (`&` stops commuting)" % (popc(pos_ab), popc(pos_ba), popc(pos_ab ^ pos_ba)))
zp = [s for s in SRC["RZ"] if ";" not in s]
hz = one("(h = 0: <5)", "h", LT5, "?")
some_hz = Cond("some((h = 0: <5))", [("h", "?")], lambda t, v: LT5(t[0]), kind="some")
pv_, sv_ = vec(hz, [("c", "0")], RZ), vec(some_hz, [("c", "0")], RZ)
print("   (3c) a default on a looped label, RZ zero-pass subjects (%d): `(h = 0: <5)` holds on %d (the LEFT JOIN row "
      "reads 0), `some((h = 0: <5))` on %d (no pass to read); on all 1,110: %d vs %d" % (
          len(zp), sum(1 for i, s in enumerate(SRC["RZ"]) if s in zp and pv_ >> i & 1),
          sum(1 for i, s in enumerate(SRC["RZ"]) if s in zp and sv_ >> i & 1), popc(pv_), popc(sv_)))
mid = popc(vec(lm, [None, ("c", "0")], T2) ^ vec(lm, [None, ("c", "60")], T2))
print("   (3d) a default the label never holds, T2 `((h, m = v): late)`: v = 0 vs v = 60 (no two-digit minute field "
      "reads 60 in a time, but the regex's m is \\d\\d, so 60 IS a value it holds): differ %d; v = 0 vs v = \"x\": %d" % (
          mid, popc(vec(lm, [None, ("c", "0")], T2) ^ vec(lm, [None, ("c", "x")], T2))))

# =====================================================================================================================
print("\nPART 4: SILENT DRIFT (a default that does not satisfy its own condition)")
occ_const = occ_dollar = 0
for pool, base, extra in SEARCH:
    for c in base + extra:
        if "?" in base_ctls(c):
            if c.reads:
                occ_dollar += 1
            else:
                occ_const += 1
for pool, nm, prog in WORKED + PROBES:
    for c in prog:
        if "?" in base_ctls(c):
            if c.reads:
                occ_dollar += 1
            else:
                occ_const += 1
print("   marked conditions of rev 22's pools + EXTRA + the WORKED and PROBE programs: %d with a constant set (whether a default satisfies its own "
      "condition is decidable from the text), %d reading a `$` (decidable only per match)" % (occ_const, occ_dollar))
# the drift itself: after an edit `(h = 4: <5)` -> `(h = 4: <3)` the default now equals NOTHING on h's absences
dr = popc(vec(one("(h: <3)", "h", LT3, "?"), [("c", "4")], A) ^ vec(one("(h: <3)", "h", LT3, "?"), [None], A))
print("   pool A: `(h = 4: <3)` (after an edit from `<5`) vs `(h: <3)` with no control: differ %d (the default is dead)" % dr)
# the mark follows an edit of its set; a default does not: `late` edited to padded(>= (9, 45)), the rewrite m = 30
LATE45 = lambda t, v: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (9, 45)
lm45 = Cond("((h, m?): late45)", [("h", ""), ("m", "?")], LATE45)
dd = tvec(ans([lm45], T2, "M2c"), T2) ^ vec(lm45, [None, ("c", "30")], T2)
print("   T2: `late` edited to padded(>= (9, 45)): rev 22's `((h, m?): late45)` vs the kept rewrite `((h, m = 30): late45)`:"
      " differ %d of %d (smallest %r; the rewrite for the edited set is m = 45)" % (popc(dd), len(T2.source), low(dd, T2)))
print("\nEND")
