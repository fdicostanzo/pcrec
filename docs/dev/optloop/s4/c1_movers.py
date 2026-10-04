#!/usr/bin/env python3
"""[OPT-LITSCAN] S4 C1 -- the MOVER CENSUS and the DENY ARM for the run
compare (litscan_s4.md §5.1 item 1, §2.1's prediction).

  BASE=<pcrec at abi 55> NEW=<pcrec at abi 56> SCR=<scratch> \\
      [PROCS=4] python3 c1_movers.py

Populations (s1_identity.py's, widened to the design census's bench set):
  bench   every pcrec-bench bench/*/patterns/*.rx export (read-only; `-e
          utf8` for the utf8 set), x {auto, vm} under --features all;
  corpus  every distinct `pattern` line of every tests/**/*.rxt, x {auto,
          vm} under --features all.

ONE normalization, by name: the abi digit's three sites rewritten 55 -> 56
and the `#define RX_RUN_WORDS N` line deleted from the NEW side. Everything
else is compared raw. Two arms per artifact:

  NEW   vs BASE  -> moved / identical. THE BICONDITIONAL: moved <=> the NEW
                   artifact's RX_RUN_WORDS > 0 (it writes a compare at an
                   overlap length). Off-diagonal cells are failures.
  DENY  vs BASE  -> NEW built with -fno-run-overlap. Must be IDENTICAL on
                   every artifact (the deny restores the abi-55 program), and
                   its RX_RUN_WORDS must read 0.

Also tallies the stamps that moved on the movers (beyond the program text):
a longer run compare moves RX_VM_PROGRAM_BYTES, which can move the size-term
or entry-shape knees -- answer-identical choices, listed so they are seen.
"""
import collections, glob, json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
BENCH = "/Users/fdicostanzo/pcrec-bench/bench"
CFG = {"auto": ["--features", "all"], "vm": ["--features", "all", "--engine=vm"]}


def emit(binp, pat, flags, d):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "-o", out, "--pattern", pat] + flags,
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return None
    return open(out, "rb").read().decode("latin-1")


def norm_base(t):
    t = re.sub(r'(abi )55\b', r'\g<1>56', t)
    t = re.sub(r'(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)55\b', r'\g<1>56', t)
    t = re.sub(r'(\(abi )55\)', r'\g<1>56)', t)
    return re.sub(r'(\.abi *= *)55\b', r'\g<1>56', t)


def drop_words(t):
    return re.sub(r'^#define RX_RUN_WORDS \d+\n', '', t, flags=re.M)


def words(t):
    m = re.search(r'^#define RX_RUN_WORDS (\d+)$', t, re.M)
    return int(m.group(1)) if m else -1


def stamps(t):
    return dict(re.findall(r'^#define (RX_\w+) (.*)$', t, re.M))


def one(job):
    i, pop, key, pat, cfg, flags = job
    b = emit(BASE, pat, flags, f"{SCR}/m/{i}/b")
    a = emit(NEW, pat, flags, f"{SCR}/m/{i}/a")
    dn = emit(NEW, pat, flags + ["-fno-run-overlap"], f"{SCR}/m/{i}/d")
    rec = {"pop": pop, "key": key, "cfg": cfg}
    if any(x == "TIMEOUT" for x in (a, b, dn)):
        rec["id"] = "timeout"
        return rec
    if b is None or a is None or dn is None:
        rec["id"] = "refused" if (b is None and a is None and dn is None) else "refusal-mismatch"
        return rec
    nb = norm_base(b)
    rec["words"] = words(a)
    rec["id"] = "identical" if drop_words(a) == nb else "moved"
    rec["deny"] = "identical" if drop_words(dn) == nb else "moved"
    rec["deny_words"] = words(dn)
    if rec["id"] == "moved":
        sb, sa = stamps(nb), stamps(drop_words(a))
        rec["stamps"] = sorted(k for k in set(sb) | set(sa) if sb.get(k) != sa.get(k))
    return rec


def jobs():
    n = 0
    for path in sorted(glob.glob(f"{BENCH}/*/patterns/*.rx")):
        pat = open(path, "rb").read().rstrip(b"\n").decode("utf-8", "surrogateescape")
        enc = ["-e", "utf8"] if "/utf8/" in path else []
        key = os.path.relpath(path, BENCH)
        for cfg, flags in CFG.items():
            n += 1
            yield (n, "bench", key, pat, cfg, flags + enc)
    seen = set()
    for path in sorted(glob.glob(f"{ROOT}/tests/**/*.rxt", recursive=True)):
        for ln in open(path, "rb").read().decode("utf-8", "surrogateescape").splitlines():
            if not ln.startswith("pattern ") or ln in seen:
                continue
            seen.add(ln)
            pat = ln[len("pattern "):]
            for cfg, flags in CFG.items():
                n += 1
                yield (n, "corpus", pat, pat, cfg, flags)


def main():
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, jobs()))
    json.dump(res, open(f"{SCR}/c1_movers.json", "w"), indent=0)
    bad = 0
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        print(f"== {pop}: {len(rs)} artifact-configs")
        print("  ids:", dict(collections.Counter(r["id"] for r in rs)))
        ok = [r for r in rs if r["id"] in ("identical", "moved")]
        tab = collections.Counter((r["id"], r["words"] > 0) for r in ok)
        print(f"  moved & words>0 {tab[('moved', True)]:6d}   moved & words=0 {tab[('moved', False)]:6d}")
        print(f"  ident & words>0 {tab[('identical', True)]:6d}   ident & words=0 {tab[('identical', False)]:6d}")
        bad += tab[("moved", False)] + tab[("identical", True)]
        for cfg in CFG:
            print(f"  {cfg}: movers {sum(1 for r in ok if r['cfg'] == cfg and r['id'] == 'moved')}"
                  f" artifacts (distinct patterns"
                  f" {len({r['key'] for r in ok if r['cfg'] == cfg and r['id'] == 'moved'})})")
        dmov = [r for r in ok if r["deny"] != "identical" or r["deny_words"] != 0]
        print(f"  deny arm: {len(ok) - len(dmov)} identical to BASE, {len(dmov)} not")
        bad += len(dmov)
        for r in dmov[:10]:
            print(f"   DENY-MOVED {r['cfg']} {r['key'][:70]!r}")
        st = collections.Counter(s for r in ok if r["id"] == "moved" for s in r["stamps"])
        print("  stamps moved on movers:", dict(st))
        for r in ok:
            if r["id"] == "moved" and r["stamps"]:
                print(f"   STAMP {r['cfg']} {r['key'][:70]!r} {','.join(r['stamps'])}")
        for r in rs:
            if r["id"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['id'].upper()} {r['cfg']} {r['key'][:70]!r}")
    print(f"c1_movers: {'PASS' if bad == 0 else 'FAIL'} ({bad} off-diagonal or deny failures)")


if __name__ == "__main__":
    main()
