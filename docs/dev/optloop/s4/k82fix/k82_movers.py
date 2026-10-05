#!/usr/bin/env python3
"""[K82] (A)+(C) -- the MOVER MANIFEST and the DENY ARM for the pre-check
admission's `set-leads` row and the PICK primitive's NONE answer
(docs/dev/lanes/k82fix_report.md).

  BASE=<pcrec at abi 59> NEW=<pcrec with the fix> SCR=<scratch> \\
      [ABI_FROM=59 ABI_TO=60] [PROCS=4] python3 k82_movers.py

Populations: `../c3_movers.py`'s own (imported, so the counts reconcile with
C3's manifest): every pcrec-bench export x {auto, vm} x {caps, nocaps}, and
every corpus `pattern` row as written x {auto, vm}.

ONE normalization, by name: BASE's abi digit ABI_FROM rewritten to ABI_TO at
its three sites (none when they are equal, i.e. a NEW built before the bump).
Then BYTE FOR BYTE. Two arms per artifact:

  NEW  vs BASE  moved / identical, against a PREDICTION recomputed here in
                Python from NEW's `--emit-facts` rows and the default
                analysis's ppm (`--list-analysis default`), never from the C:
    (C) the byte-rate is NONE (`req_run`'s why reads `rate:none...`) and the
        run is masked: the scan position is the argmin of each position's
        MEMBER COUNT over the run reversed, ties to the rightmost, then the
        window of PCREC_MAX_REQ_RUN_EMIT (8) positions holding it with the
        fewest members, ties leftmost. A mover where that differs from
        BASE's `req_run` window/index.
    (A) NEW's REQ_WHY reads `emitted`, a run shipped, the necessary set is
        non-empty, and the set's rarest member has a smaller mass than the
        run's scan cube (under NONE: one member's uniform mass against the
        cube's member count).
    THE BICONDITIONAL: moved <=> (A) or (C). Off-diagonal cells are failures.
  DENY vs BASE  NEW built with -fno-req-set-lead. IDENTICAL on every artifact
                not predicted (C): (A) is the only thing the deny removes.
"""
import collections, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import c3_movers as c3   # noqa: E402  (reads BASE/NEW/SCR itself)

BASE, NEW, SCR = c3.BASE, c3.NEW, c3.SCR
ABI_FROM, ABI_TO = os.environ.get("ABI_FROM", "59"), os.environ.get("ABI_TO", "59")


def ppm_table():
    o = subprocess.run([NEW, "--list-analysis", "default"], capture_output=True,
                       text=True).stdout
    sec, r = None, [0] * 256
    for ln in o.splitlines():
        if ln.startswith("#section"):
            sec = ln.split()[1]
        elif sec == "freq" and ln and not ln.startswith("#"):
            k, _c, p = ln.split("\t")
            r[int(k, 16)] = int(p)
    assert sum(r) == 1000000, sum(r)
    return r


RATE = ppm_table()


def members(t, k):
    f, out, b = ~k & 0xFF, [], ~k & 0xFF
    while True:
        out.append(t | b)
        if b == 0:
            return out
        b = (b - 1) & f


def mass(rated, t, k):
    m = members(t, k)
    return sum(RATE[x] for x in m) if rated else len(m) * 1000000 // 256


def parse_run(v):
    """'"hex@idx/mask"' / 'hex/mask' -> (bytes, masks, idx or None), or None."""
    v = v.strip('"')
    if v in ("", "none", "-"):
        return None
    h, _s, mk = v.partition("/")
    h, _a, idx = h.partition("@")
    t = bytes.fromhex(h)
    return t, (bytes.fromhex(mk) if mk else b"\xff" * len(t)), (int(idx) if idx else None)


def none_window(t, k):
    """NONE's (window start, index in the window) over the whole run."""
    n, cnt = len(t), [len(members(a, b)) for a, b in zip(t, k)]
    best = n - 1
    for i in range(n - 1, -1, -1):
        if cnt[i] < cnt[best]:
            best = i
    if n <= 8:
        return 0, best
    lo = None
    for s in range(max(0, best - 7), min(best, n - 8) + 1):
        m = sum(cnt[s:s + 8])
        if lo is None or m < lo[0]:
            lo = (m, s)
    return lo[1], best - lo[1]


def facts(binp, pat, args):
    r = subprocess.run([binp.encode(), b"--features", b"all", b"-p", b"rx", b"--emit-facts",
                        *[a.encode() for a in args], b"--pattern", pat],
                       capture_output=True, timeout=300)
    f = {}
    for ln in r.stdout.decode("latin-1").split("\n"):
        c = ln.split("\t")
        if len(c) >= 8 and c[1] in ("req_set", "req_whole_run", "req_run"):
            f[c[1]] = (c[6], c[7])
        elif len(c) == 3 and c[1] == "RX_REQ_WHY":
            f["why"] = c[2].strip('"')
    return f


def predict(fb, fn):
    out = ""
    why = fn.get("req_run", ("", ""))[1]
    rated = "rate:" in why and "rate:none" not in why
    whole = parse_run(fn.get("req_whole_run", ("none", ""))[0])
    rb = parse_run(fb.get("req_run", ("none", ""))[0])
    if whole and not rated and any(x != 0xFF for x in whole[1]):
        s, i = none_window(whole[0], whole[1])
        if rb is None or rb[2] != i or rb[0] != whole[0][s:s + len(rb[0])]:
            out += "C"
    rn = parse_run(fn.get("req_run", ("none", ""))[0])
    sv = fn.get("req_set", ("none", ""))[0]
    mem = [int(x) for x in sv.split(",")] if sv not in ("none", "") else []
    if rn and mem and fn.get("why") == "emitted":
        t, k, idx = rn
        sp = min(RATE[b] for b in mem) if rated else 1000000 // 256
        if sp < mass(rated, t[idx], k[idx]):
            out += "A"
    return out


def norm_base(t):
    if ABI_FROM == ABI_TO:
        return t
    t = re.sub(r'(abi )%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)
    t = re.sub(r'(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)
    return re.sub(r'(\.abi *= *)%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)


def one(job):
    i, pop, pat, args, cfg = job
    d = tempfile.mkdtemp(dir=SCR)
    try:
        for s in ("b", "a", "d"):
            os.makedirs(d + "/" + s)
        b = c3.emit(BASE, pat, args, d + "/b")
        a = c3.emit(NEW, pat, args, d + "/a")
        dn = c3.emit(NEW, pat, args + ["-fno-req-set-lead"], d + "/d")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    rec = {"i": i, "pop": pop, "cfg": cfg, "pat": pat.decode("latin-1"), "args": args}
    if any(x == "TIMEOUT" for x in (a, b, dn)):
        rec["id"] = "timeout"
        return rec
    if b is None or a is None or dn is None:
        rec["id"] = "refused" if (b is None and a is None and dn is None) else "refusal-mismatch"
        return rec
    nb = norm_base(b)
    rec["id"] = "identical" if a == nb else "moved"
    rec["deny"] = "identical" if dn == nb else "moved"
    rec["pred"] = predict(facts(BASE, pat, args), facts(NEW, pat, args))
    sb, sa = c3.stamps(nb), c3.stamps(a)
    rec["run"] = (sb.get("RX_REQ_RUN"), sa.get("RX_REQ_RUN"))
    rec["byte"] = (sb.get("RX_REQ_BYTE"), sa.get("RX_REQ_BYTE"))
    rec["why"] = sa.get("RX_REQ_WHY")
    if rec["id"] == "moved":
        rec["stamps"] = sorted(k for k in set(sb) | set(sa) if sb.get(k) != sa.get(k))
    return rec


def main():
    js = c3.jobs()
    wt = {j[0]: w for j, w in js}
    print("jobs:", len(js), file=sys.stderr, flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, [j for j, _w in js]))
    for r in res:
        r["w"] = wt[r["i"]]
    json.dump(res, open(f"{SCR}/k82_movers.json", "w"), indent=0)
    bad = 0
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        ok = [r for r in rs if r["id"] in ("identical", "moved")]
        print(f"== {pop}: {len(rs)} distinct artifact-configs ({sum(r['w'] for r in rs)} rows)")
        print("  ids:", dict(collections.Counter(r["id"] for r in rs)))
        tab = collections.Counter((r["id"], r["pred"] or "-") for r in ok)
        for k in sorted(tab):
            print(f"  {k[0]:9s} pred={k[1]:3s} {tab[k]:6d}")
        for r in ok:
            if (r["id"] == "moved") != bool(r["pred"]):
                bad += 1
                print(f"   OFF-DIAGONAL {r['id']} pred={r['pred'] or '-'} {r['cfg']} "
                      f"{r['pat'][:70]!r} {r['args']} run {r['run']} why {r['why']}")
        dmov = [r for r in ok if "C" not in r["pred"] and r["deny"] != "identical"]
        print(f"  deny arm: {len(ok) - len(dmov)} identical-or-(C), {len(dmov)} not")
        bad += len(dmov)
        for r in dmov[:20]:
            print(f"   DENY-MOVED {r['cfg']} {r['pat'][:70]!r} {r['args']}")
        for r in ok:
            if r["id"] == "moved" and r["cfg"] in ("auto", "vm"):
                print(f"   MOVER {r['pred']:2s} {r['cfg']:4s} {r['pat'][:60]!r} {' '.join(r['args'])} "
                      f"run {r['run'][0]}->{r['run'][1]} byte {r['byte'][0]}->{r['byte'][1]} "
                      f"why {r['why']} [{','.join(r['stamps'])}]")
        for r in rs:
            if r["id"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['id'].upper()} {r['cfg']} {r['pat'][:70]!r}")
                bad += r["id"] == "refusal-mismatch"
    print(f"k82_movers: {'PASS' if bad == 0 else 'FAIL'} ({bad} off-diagonal, deny or refusal failures)")


if __name__ == "__main__":
    main()
