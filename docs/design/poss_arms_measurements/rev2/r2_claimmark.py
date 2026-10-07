#!/usr/bin/env python3
"""B-B2's CLAIM-vs-MARK check, prototype form.  Subject-free, deterministic.

For each family row (gen_a2.py / gen_b2.py output: id mods greedy possessive
claim alphabet abl hi) it compiles the GREEDY pattern with the rev-2
prototype (`--engine=vm --emit-ir`, `possessify marked/total`) once with no
arm (today's main) and once per configuration in CONFIGS, and reads the
row's MARK as "the arms raised the marked count" (every family row has
exactly one quantifier the arms can reach -- the one before the gate or the
reference; r2_claimmark.out's `base_m` column shows the rest are untouched).

EXPECTATION = claim && !hi: the Python predicate (libpcre2-sourced
membership, no pcrec code) restricted to pcrec's representable domain
(hi = FIRST(X) has a code point above 0xFF, which first_of widens to all
bytes -- a lost opportunity by representation, never a wrong answer).

A row whose `mods` pcrec has no spelling for (match_unset_backref) or whose
pattern pcrec refuses is recorded REFUSED, not compared.

Selection (argv: rowfile ...; env SAMPLE=N keeps 1 in N of the rows that are
neither claimed nor ablation-tagged, by a fixed hash).
Env: PROTO, JOBS.  Prints one TSV row per family row and a #SUMMARY block."""
import os, sys, subprocess, hashlib, concurrent.futures as cf
PROTO = os.environ["PROTO"]
AB = {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"}
def plant(v): d = dict(AB); d[v] = "1"; return d
CONFIGS = [
    ("AB", AB),
    ("S560_m0", plant("PROTO_SAB_M0")),
    ("S561_firstpol", plant("PROTO_SAB_FIRSTPOL")),
    ("S562_mixed", plant("PROTO_SAB_MIXED")),
    ("S563_nofold", plant("PROTO_SAB_NOFOLD")),
    ("S564_firstmem", plant("PROTO_SAB_FIRSTMEM")),
    ("S565_nonnull", plant("PROTO_SAB_NONNULL")),
    ("AF1_nocc", plant("PROTO_A1_NOCC")),
    ("lazy", plant("PROTO_SAB_LAZY")),
]
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
def marked(pat, fl, env):
    e = dict(os.environ); e.update(env)
    try:
        p = subprocess.run([PROTO] + fl + ["--engine=vm", "--emit-ir", "--pattern", pat],
                           capture_output=True, timeout=60, env=e)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if p.returncode:
        return "ERR" if p.returncode < 0 or p.returncode > 1 else None
    for ln in p.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if f[0] == "possessify": return int(f[1].split("/")[0])
    return None
def one(row):
    rid, mods, g, _p, claim, _al, abl, hi = row
    fl, pre = flags(mods)
    exp = claim == "yes" and hi == "0"
    res = dict(id=rid, mods=mods, pat=g, claim=claim, hi=hi, abl=abl, exp=int(exp))
    if fl is None:
        res["status"] = "REFUSED(option)"; return res
    pat = pre + g
    b = marked(pat, fl, {})
    if not isinstance(b, int):
        res["status"] = "REFUSED(pcrec)"; return res
    res["status"] = "ok"; res["base_m"] = b
    for name, env in CONFIGS:
        m = marked(pat, fl, env)
        res[name] = m if not isinstance(m, int) else int(m > b)
    return res
def main():
    sample = int(os.environ.get("SAMPLE", "10"))
    rows = []
    for fn in sys.argv[1:]:
        for ln in open(fn, encoding="utf8"):
            f = ln.rstrip("\n").split("\t")
            if len(f) < 8: continue
            keep = f[4] == "yes" or f[6] != "" or f[0][0] in "BC" or \
                int(hashlib.md5(f[0].encode()).hexdigest(), 16) % sample == 0
            if keep: rows.append(f[:8])
    with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "6"))) as ex:
        out = list(ex.map(one, rows))
    names = [c[0] for c in CONFIGS]
    print("\t".join(["id", "status", "mods", "claim", "hi", "exp", "abl", "base_m"] + names + ["pattern"]))
    summ = {n: [0, 0, 0] for n in names}     # compared, mark!=exp, mark&&!exp
    st = {}
    for r in out:
        st[r["status"]] = st.get(r["status"], 0) + 1
        print("\t".join(str(r.get(k, "")) for k in
                        ["id", "status", "mods", "claim", "hi", "exp", "abl", "base_m"] + names + ["pat"]))
        if r["status"] != "ok": continue
        for n in names:
            v = r[n]
            if not isinstance(v, int): summ[n][1] += 1; continue
            summ[n][0] += 1
            if v != r["exp"]: summ[n][1] += 1
            if v and not r["exp"]: summ[n][2] += 1
    print("#SUMMARY rows", len(out), st)
    for n in names:
        print("#SUMMARY %-14s compared %d  mark!=expect %d  (unsound-direction mark&&!expect %d)" % (n, *summ[n]))
main()
