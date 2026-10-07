#!/usr/bin/env python3
"""CLAIM-vs-MARK, rev 2.1 (possarms21).  Subject-free, deterministic.

Over rev 2 (r2_claimmark.py) it changes three things:

  R-7  MARK IS READ PER QUANTIFIER, not as a count delta.  Every compile reads
       --emit-ir's `strategies` section: one row per emitted quantifier, in
       emission order.  Labels renumber when a program moves, so rows are
       keyed by ORDINAL; a row count that differs between two compiles of the
       same pattern is an ANOMALY, never a mark.  The TARGET quantifier is
       found WITHOUT the arms: the generator's possessive spelling (column 4)
       compiled on the base build differs from the greedy spelling at
       exactly one ordinal (`tgt`; `unresolved` when it does not, and such a
       row falls back to "some quantifier flipped").  MARK = the arms flipped
       the target backtracking -> possessive.  A flip at another ordinal is
       counted as `extra`; any other change is an `anomaly`.
  R-7  THE utf,ucp REFUSED POPULATION IS PINNED (UCP_PIN).  Every selected
       `utf,ucp` row is refused today (UCP \\w under -e utf8 is a wide set,
       refused until [CLS-TREE] S4 / [UCP] U3).  The run exits 3 when the
       count moves: that is the trigger to re-sweep those rows.
  R-3b HAND-LITERAL rows (column 9 `hand`) are reported separately from the
       COMPUTED ones; the predicate generators are frozen by sha (the note).

EXPECTATION = claim && !hi (hi: FIRST(X) or the follow's text has a member
above U+00FF, which pcrec declines by representation).

Usage: PROTO=... [JOBS=8] [SAMPLE=10] [UCP_PIN=N] [CONFIGS=all|AB]
       r21_claimmark.py rowfile...   (TSV out, #SUMMARY lines; rc 1 on a
       mismatch under AB, rc 3 on a moved UCP pin)"""
import os, sys, subprocess, hashlib, concurrent.futures as cf
PROTO = os.environ["PROTO"]
AB = {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"}
def plant(v): d = dict(AB); d[v] = "1"; return d
CONFIGS = [
    ("AB", AB),
    ("m0", plant("PROTO_SAB_M0")),
    ("firstpol", plant("PROTO_SAB_FIRSTPOL")),
    ("mixed", plant("PROTO_SAB_MIXED")),
    ("nofold", plant("PROTO_SAB_NOFOLD")),
    ("firstmem", plant("PROTO_SAB_FIRSTMEM")),
    ("nonnull", plant("PROTO_SAB_NONNULL")),
    ("nocc", plant("PROTO_A1_NOCC")),
    ("lazy", plant("PROTO_SAB_LAZY")),
    ("textpos", plant("PROTO_SAB_TEXTPOS")),
]
if os.environ.get("CONFIGS") == "AB":
    CONFIGS = CONFIGS[:1]

def flags(mods):
    out, pre = ["--features", "all"], ""
    for t in mods.split(","):
        if t in ("", "no_auto_possess"): continue
        if t == "i": out.append("-i")
        elif t == "ucp": out.append("--ucp")
        elif t == "utf": out += ["-e", "utf8"]
        elif t == "dupnames": pre = "(?J)"
        else: return None, None
    return out, pre

def strategies(pat, fl, env):
    """the strategies section's `kind` column, in order; or a status word"""
    e = dict(os.environ); e.update(env)
    try:
        p = subprocess.run([PROTO] + fl + ["--engine=vm", "--emit-ir", "--pattern", pat],
                           capture_output=True, timeout=120, env=e)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if p.returncode:
        return "ERR" if p.returncode < 0 or p.returncode > 1 else "REFUSED"
    kinds, on = [], False
    for ln in p.stdout.decode("latin-1").split("\n"):
        if ln.startswith("#section"):
            on = ln.strip() == "#section strategies"; continue
        if on and ln and not ln.startswith("#"):
            kinds.append(ln.split("\t")[1])
    return kinds

def flips(base, got):
    """(set of ordinals flipped backtracking->possessive, anomaly?)"""
    if len(base) != len(got): return set(), True
    fl, anom = set(), False
    for i, (b, g) in enumerate(zip(base, got)):
        if b == g: continue
        if b == "backtracking" and g == "possessive": fl.add(i)
        else: anom = True
    return fl, anom

def one(row):
    rid, mods, g, ps, claim, _al, abl, hi, src = row
    fl, pre = flags(mods)
    exp = claim == "yes" and hi == "0"
    res = dict(id=rid, mods=mods, pat=g, claim=claim, hi=hi, abl=abl, exp=int(exp), src=src)
    if fl is None:
        res["status"] = "REFUSED(option)"; return res
    base = strategies(pre + g, fl, {})
    if not isinstance(base, list):
        res["status"] = "REFUSED(pcrec)" if base == "REFUSED" else base; return res
    pbase = strategies(pre + ps, fl, {})
    tset = flips(base, pbase)[0] if isinstance(pbase, list) else set()
    tgt = next(iter(tset)) if len(tset) == 1 else None
    # POST-FREEZE EDIT 1 (poss_arms.md §8.3a): the possessive spelling moves
    # NOTHING because the base build already marks the target (an exact
    # count, row 1).  MARK is then the target's STATE, which the arms must
    # keep: every ordinal the spelling makes possessive stays possessive.
    basemarked = (tgt is None and isinstance(pbase, list) and pbase == base
                  and "possessive" in base)
    res["status"] = "ok"
    res["tgt"] = "basemarked" if basemarked else ("unresolved" if tgt is None else str(tgt))
    res["nq"] = len(base)
    for name, env in CONFIGS:
        got = strategies(pre + g, fl, env)
        if not isinstance(got, list):
            res[name] = got; continue
        f, anom = flips(base, got)
        if anom:
            res[name] = "ANOMALY"; continue
        if basemarked:
            mark = all(got[i] == "possessive" for i, k in enumerate(base) if k == "possessive")
        else:
            mark = (tgt in f) if tgt is not None else bool(f)
        extra = 0 if basemarked else len(f - ({tgt} if tgt is not None else f))
        res[name] = int(mark) + (10 * extra)        # tens digit: extra flips
    return res

def main():
    sample = int(os.environ.get("SAMPLE", "10"))
    rows = []
    for fn in sys.argv[1:]:
        for ln in open(fn, encoding="utf8"):
            f = ln.rstrip("\n").split("\t")
            if len(f) < 9: continue
            keep = f[4] == "yes" or f[6] != "" or f[8] == "hand" or \
                int(hashlib.md5(f[0].encode()).hexdigest(), 16) % sample == 0
            if keep: rows.append(f[:9])
    with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "8"))) as ex:
        out = list(ex.map(one, rows))
    names = [c[0] for c in CONFIGS]
    cols = ["id", "src", "status", "mods", "claim", "hi", "exp", "abl", "nq", "tgt"] + names + ["pat"]
    print("\t".join(cols))
    # per config, per src: compared, mismatch, unsound-direction, extra, anomaly
    summ = {(n, s): [0, 0, 0, 0, 0] for n in names for s in ("computed", "hand")}
    st, ucp_ref, unres = {}, 0, {"computed": 0, "hand": 0}
    for r in out:
        st[(r["src"], r["status"])] = st.get((r["src"], r["status"]), 0) + 1
        print("\t".join(str(r.get(k if k != "pat" else "pat", "")) for k in cols))
        if r["status"] != "ok":
            if "utf" in r["mods"].split(",") and "ucp" in r["mods"].split(","): ucp_ref += 1
            continue
        if r["tgt"] == "unresolved": unres[r["src"]] += 1
        if r["tgt"] == "basemarked": unres["bm_" + r["src"]] = unres.get("bm_" + r["src"], 0) + 1
        for n in names:
            v, s = r[n], summ[(n, r["src"])]
            if not isinstance(v, int):
                if v == "ANOMALY": s[4] += 1
                s[1] += 1; continue
            m, extra = v % 10, v // 10
            s[0] += 1
            if extra: s[3] += 1
            if m != r["exp"]: s[1] += 1
            if m and not r["exp"]: s[2] += 1
    print("#SUMMARY rows %d status %s" % (len(out), sorted(st.items())))
    print("#SUMMARY target-unresolved computed=%d hand=%d  base-marked computed=%d hand=%d"
          % (unres["computed"], unres["hand"], unres.get("bm_computed", 0), unres.get("bm_hand", 0)))
    for n in names:
        for s in ("computed", "hand"):
            print("#SUMMARY %-9s %-8s compared %d  mark!=expect %d  (unsound-direction %d)  extra-flips %d  anomalies %d"
                  % (n, s, *summ[(n, s)]))
    print("#SUMMARY utf,ucp REFUSED %d" % ucp_ref)
    rc = 0
    if any(summ[("AB", s)][1] for s in ("computed", "hand")): rc = 1
    pin = os.environ.get("UCP_PIN")
    if pin is not None and int(pin) != ucp_ref:
        print("#UCP-PIN MOVED: pinned %s, measured %d -- [CLS-TREE] S4 / [UCP] U3 landed? "
              "re-sweep the utf,ucp rows (poss_arms.md §2.5)" % (pin, ucp_ref))
        rc = rc or 3
    sys.exit(rc)
main()
