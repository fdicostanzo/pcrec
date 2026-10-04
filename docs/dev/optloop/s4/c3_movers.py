#!/usr/bin/env python3
"""[OPT-LITSCAN] S4 C3 -- the MOVER MANIFEST and the DENY ARM for the caseless
necessary run (litscan_s4.md §5.1 item 1, reconciled with §2.3.7's census).

  BASE=<pcrec at abi 58> NEW=<pcrec at abi 59> SCR=<scratch> \\
      [PROCS=4] python3 c3_movers.py

Populations (c3census/c3_census.py's, so the counts reconcile with the
census's 41 = A1 u C over corpus+bench auto):
  bench   every pcrec-bench bench/*/patterns/*.rx export (read-only; `-e utf8`
          for the utf8 set) x the four compile configs {auto, vm} x {captures,
          --no-captures};
  corpus  every `pattern` row of every tests/**/*.rxt as written, through
          `--list-source` (flags `i` -> -i, `u` -> --ucp, column 9 -> -e), x
          {auto, vm}. A (pattern, args) pair is compiled once and counted for
          every row that carries it.

ONE normalization, by name: BASE's abi digit (58) rewritten to 59 at its
three sites. Everything else is compared raw, BYTE FOR BYTE. Two arms per
artifact:

  NEW  vs BASE  moved / identical. THE BICONDITIONAL (§5.1): moved <=> the NEW
                artifact's <PREFIX>_REQ_RUN carries a `/mask` suffix (the
                `req_run` fact is masked). Off-diagonal cells are failures.
  DENY vs BASE  NEW built with -fno-req-run-fold. Must be IDENTICAL on every
                artifact: the fact-level deny restores the abi-58 program and
                stamps whole (the masked suffix is gone with the fact).

Named sub-populations of the movers, each matched against §2.3.7's list:
the census class (A1: BASE REQ_RUN "none"; C: BASE REQ_RUN exact), REQ_WHY
moves (G1 verdicts), RX_DFA_PREFILTER moves (selections), and on the auto
movers the `run_pin` fact BASE -> NEW from --emit-facts (pins kept at the
same offset, moved, lost).
"""
import collections, glob, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
BENCH = os.environ.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
CORPUS_CFG = {"auto": [], "vm": ["--engine=vm"]}
BENCH_CFG = {"auto": [], "vm": ["--engine=vm"],
             "auto-nocaps": ["--no-captures"], "vm-nocaps": ["--engine=vm", "--no-captures"]}


def dec_field(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9); i += 2; continue
            if n == 0x6e: out.append(10); i += 2; continue
            if n == 0x72: out.append(13); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)


def emit(binp, pat, args, d):
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp.encode(), b"--features", b"all", b"-p", b"rx", b"-o", out.encode(),
                            *[a.encode() for a in args], b"--pattern", pat],
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return None
    return open(out, "rb").read().decode("latin-1")


def run_pin(binp, pat, args):
    try:
        r = subprocess.run([binp.encode(), b"--features", b"all", b"--emit-facts",
                            *[a.encode() for a in args], b"--pattern", pat],
                           capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] == "run_pin":
            return f[6]
    return "-"


def norm_base(t):
    t = re.sub(r'(abi )58\b', r'\g<1>59', t)
    t = re.sub(r'(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)58\b', r'\g<1>59', t)
    return re.sub(r'(\.abi *= *)58\b', r'\g<1>59', t)


def stamps(t):
    return dict(re.findall(r'^#define (RX_\w+) (.*)$', t, re.M))


def one(job):
    i, pop, pat, args, cfg = job
    d = tempfile.mkdtemp(dir=SCR)
    try:
        os.makedirs(d + "/b"); os.makedirs(d + "/a"); os.makedirs(d + "/d")
        b = emit(BASE, pat, args, d + "/b")
        a = emit(NEW, pat, args, d + "/a")
        dn = emit(NEW, pat, args + ["-fno-req-run-fold"], d + "/d")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    rec = {"i": i, "pop": pop, "cfg": cfg, "pat": pat.decode("latin-1"), "args": args}
    if any(x == "TIMEOUT" for x in (a, b, dn)):
        rec["id"] = "timeout"; return rec
    if b is None or a is None or dn is None:
        rec["id"] = "refused" if (b is None and a is None and dn is None) else "refusal-mismatch"
        return rec
    nb = norm_base(b)
    sb, sa = stamps(nb), stamps(a)
    rec["masked"] = "/" in sa.get("RX_REQ_RUN", "")
    rec["base_run"] = sb.get("RX_REQ_RUN", "-")
    rec["new_run"] = sa.get("RX_REQ_RUN", "-")
    rec["id"] = "identical" if a == nb else "moved"
    rec["deny"] = "identical" if dn == nb else "moved"
    if rec["id"] == "moved":
        rec["stamps"] = sorted(k for k in set(sb) | set(sa) if sb.get(k) != sa.get(k))
        rec["why"] = (sb.get("RX_REQ_WHY"), sa.get("RX_REQ_WHY"))
        rec["pf"] = (sb.get("RX_DFA_PREFILTER"), sa.get("RX_DFA_PREFILTER"))
        if cfg == "auto":
            rec["pin"] = (run_pin(BASE, pat, args), run_pin(NEW, pat, args))
    return rec


def jobs():
    rows = []   # (pop, ident, pat, args)
    for p in sorted(glob.glob(os.path.join(BENCH, "bench", "*", "patterns", "*.rx"))):
        setname = p.split(os.sep)[-3]
        b = open(p, "rb").read().rstrip(b"\n")
        if b and b"\0" not in b:
            rows.append(("bench", "%s/%s" % (setname, os.path.basename(p)[:-3]), b,
                         ["-e", "utf8"] if setname == "utf8" else []))
    files = sorted(os.path.join(r, f) for r, _d, fs in os.walk(os.path.join(ROOT, "tests"))
                   for f in fs if f.endswith(".rxt"))
    for f in files:
        r = subprocess.run([BASE, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode: continue
        rel = os.path.relpath(f, ROOT)
        for ln in r.stdout.split(b"\n"):
            if not ln or ln.startswith(b"#"): continue
            fl = ln.split(b"\t")
            if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"): continue
            pat = dec_field(fl[4])
            if not pat or b"\0" in pat: continue
            args = []
            if b"i" in fl[5]: args.append("-i")
            if b"u" in fl[5]: args.append("--ucp")
            if fl[8]: args += ["-e", fl[8].decode()]
            rows.append(("corpus", "%s:%s" % (rel, fl[1].decode()), pat, args))
    # one compile per distinct (pop, pattern, args, cfg); rows counted by weight
    weight = collections.Counter((pop, pat, tuple(args)) for pop, _i, pat, args in rows)
    n = 0
    out = []
    for (pop, pat, args), w in sorted(weight.items()):
        for cfg, fl in (BENCH_CFG if pop == "bench" else CORPUS_CFG).items():
            n += 1
            out.append(((n, pop, pat, list(args) + fl, cfg), w))
    return out


def main():
    js = jobs()
    wt = {j[0]: w for j, w in js}
    print("jobs:", len(js), file=sys.stderr, flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, [j for j, _w in js]))
    for r in res:
        r["w"] = wt[r["i"]]
    json.dump(res, open(f"{SCR}/c3_movers.json", "w"), indent=0)
    bad = 0
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        cfgs = BENCH_CFG if pop == "bench" else CORPUS_CFG
        print(f"== {pop}: {len(rs)} distinct artifact-configs ({sum(r['w'] for r in rs)} rows)")
        print("  ids:", dict(collections.Counter(r["id"] for r in rs)))
        ok = [r for r in rs if r["id"] in ("identical", "moved")]
        tab = collections.Counter((r["id"], r["masked"]) for r in ok)
        print(f"  moved & masked  {tab[('moved', True)]:6d}   moved & exact  {tab[('moved', False)]:6d}")
        print(f"  ident & masked  {tab[('identical', True)]:6d}   ident & exact  {tab[('identical', False)]:6d}")
        bad += tab[("moved", False)] + tab[("identical", True)]
        for r in ok:
            if (r["id"] == "moved") != r["masked"]:
                print(f"   OFF-DIAGONAL {r['id']} masked={r['masked']} {r['cfg']} {r['pat'][:70]!r} {r['args']}")
        for cfg in cfgs:
            mv = [r for r in ok if r["cfg"] == cfg and r["id"] == "moved"]
            a1 = [r for r in mv if r["base_run"] == '"none"']
            print(f"  {cfg}: movers {len(mv)} distinct ({sum(r['w'] for r in mv)} rows):"
                  f" A1 {len(a1)} ({sum(r['w'] for r in a1)} rows), C {len(mv) - len(a1)}"
                  f" ({sum(r['w'] for r in mv) - sum(r['w'] for r in a1)} rows)")
        dmov = [r for r in ok if r["deny"] != "identical"]
        print(f"  deny arm: {len(ok) - len(dmov)} identical to BASE, {len(dmov)} not")
        bad += len(dmov)
        for r in dmov[:20]:
            print(f"   DENY-MOVED {r['cfg']} {r['pat'][:70]!r} {r['args']}")
        mv = [r for r in ok if r["id"] == "moved"]
        st = collections.Counter(s for r in mv for s in r["stamps"])
        print("  stamps moved on movers:", dict(st))
        for r in mv:
            extra = [s for s in r["stamps"] if s not in ("RX_REQ_RUN",)]
            if extra or r["cfg"] == "auto":
                print(f"   MOVER {r['cfg']:11s} {r['pat'][:60]!r} {' '.join(r['args'])} "
                      f"run {r['base_run']}->{r['new_run']} why {r['why'][0]}->{r['why'][1]} "
                      f"pf {r['pf'][0]}->{r['pf'][1]}"
                      + (f" pin {r['pin'][0]}->{r['pin'][1]}" if "pin" in r else "")
                      + (f" [{','.join(extra)}]" if extra else ""))
        for r in rs:
            if r["id"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['id'].upper()} {r['cfg']} {r['pat'][:70]!r}")
                bad += r["id"] == "refusal-mismatch"
    print(f"c3_movers: {'PASS' if bad == 0 else 'FAIL'} ({bad} off-diagonal, deny or refusal failures)")


if __name__ == "__main__":
    main()
