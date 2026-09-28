#!/usr/bin/env python3
"""[FINDINGS] B5 (lane findb5) — THE R35 CENSUS for the shipped `log` and
`weblog` analyses (design §11.3 `ship_<name>_movers`, §13 B5), plus the
default-path IDENTITY gate for the same change, in one pass.

Per (pattern, config, encoding) it compiles FOUR artifacts:
  base     BASE (main's compiler), no analysis named
  new      NEW (this branch), no analysis named
  weblog   NEW --analysis weblog
  log      NEW --analysis log
and records:
  identity  base vs new, byte for byte, NO normalization: B5 must not move a
            single emitted byte of a compile that names nothing (no abi event).
  ship_<n>  new vs <n>, after deleting §7's named lines on both sides (the
            `RX_FINDINGS` stamp, the `.findings =` initializer, the rx_info
            member declaration — s1_identity.py's drop_named, by name and
            nothing else): a `changed` artifact is a MOVER, with the RX_*
            stamps whose values moved (`program` when a non-stamp line moved).

Populations (pcrec-bench read-only):
  bench-cap   bench/capability/patterns/*.rx, 4 configs (s1_identity's)
  bench-rxt   every `pattern` line of bench/*/export/*.rxt and
              bench/utf8/patterns.rxt, configs auto/vm (SKIP_SRC, default
              `altwide`, left out by name: see below)
  corpus      every distinct `pattern` line of tests/**/*.rxt, auto/vm
each under `-e byte` and `-e utf8`.

  BASE=<pcrec> NEW=<pcrec> SCR=<scratch> [PROCS=4] [LIMIT=N]
      [POPS=bench-cap,bench-rxt,corpus] python3 ship_census.py
Writes $SCR/ship_census.json and, per (analysis, encoding), a
b1_mover_answers.py-shaped $SCR/movers_<n>_<enc>.json; prints tallies.
"""
import os, re, glob, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
BENCH = "/Users/fdicostanzo/pcrec-bench/bench"
CAP_CFG = {"auto-caps": ["--features", "all"],
           "auto-nocaps": ["--features", "all", "--no-captures"],
           "vm-caps": ["--features", "all", "--engine=vm"],
           "vm-nocaps": ["--features", "all", "--engine=vm", "--no-captures"]}
TXT_CFG = {"auto": ["--features", "all"],
           "vm": ["--features", "all", "--engine=vm"]}
ENCS = ("byte", "utf8")
SHIPPED = ("weblog", "log")
POPS = os.environ.get("POPS", "bench-cap,bench-rxt,corpus").split(",")
# bench-rxt sources left out, BY NAME, with the reason in the report:
# `altwide` (33 wide alternations) compiles at 30-60 s per artifact on this
# box, i.e. hours for its 528 compiles, and is not where a rate reader sits.
SKIP_SRC = set(filter(None, os.environ.get("SKIP_SRC", "altwide").split(",")))


def drop_named(text):
    text = re.sub(r'^#define RX_FINDINGS .*\n', '', text, flags=re.M)
    text = re.sub(r'^    const char +\*findings; +/\*(?:.*\n)*?.*\*/\n', '',
                  text, count=1, flags=re.M)
    return re.sub(r'^    \.findings = .*\n', '', text, flags=re.M)


def moved_stamps(b, a):
    sb = dict(re.findall(r'^#define (RX_\w+) (.*)$', b, re.M))
    sa = dict(re.findall(r'^#define (RX_\w+) (.*)$', a, re.M))
    moved = sorted(k for k in set(sb) | set(sa) if sb.get(k) != sa.get(k))
    rest = lambda t: [l for l in t.splitlines() if not l.startswith("#define RX_")]
    if rest(b) != rest(a):
        moved.append("program")
    return moved


def stamp(text, name):
    m = re.search(r'^#define RX_%s (.*)$' % name, text, re.M)
    return m.group(1).strip('"') if m else None


def emit(binp, pat, flags, d):
    """One artifact into `d`/a.c — the SAME basename on every side, because
    the artifact names its own file."""
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "-o", out, "--pattern", pat] + flags,
                           capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return None
    return open(out, "rb").read().decode("latin-1")


def one(job):
    i, pop, src, key, pat, cfg, flags, enc = job
    d = f"{SCR}/c/{i}"
    fl = flags + ["-e", enc]
    art = {"base": emit(BASE, pat, fl, f"{d}/base"),
           "new": emit(NEW, pat, fl, f"{d}/new")}
    for n in SHIPPED:
        art[n] = emit(NEW, pat, fl + ["--analysis", n], f"{d}/{n}")
    rec = {"pop": pop, "src": src, "key": key, "cfg": cfg, "enc": enc}
    b, a = art["base"], art["new"]
    if b is None or a is None or "TIMEOUT" in (a, b):
        rec["identity"] = "refused" if b is None and a is None else "mismatch"
    else:
        rec["identity"] = "identical" if a == b else "changed"
    rec["findings"] = stamp(a, "FINDINGS") if a and a != "TIMEOUT" else None
    for n in SHIPPED:
        s = art[n]
        if a is None or s is None or "TIMEOUT" in (a, s):
            rec["ship_" + n] = "refused" if a is None and s is None else "mismatch"
            continue
        na, ns = drop_named(a), drop_named(s)
        rec["ship_" + n] = "identical" if na == ns else "changed"
        rec["findings_" + n] = stamp(s, "FINDINGS")
        if na != ns:
            rec["moved_" + n] = moved_stamps(na, ns)
            rec["req_" + n] = (stamp(a, "REQ_BYTE"), stamp(s, "REQ_BYTE"))
            rec["ofs_" + n] = (stamp(a, "DFA_PREFILTER_OFFSETS"),
                               stamp(s, "DFA_PREFILTER_OFFSETS"))
    for side in ("base", "new") + SHIPPED:
        if os.path.exists(f"{d}/{side}/a.c"):
            os.unlink(f"{d}/{side}/a.c")
    return rec


def rxt_patterns(path):
    for ln in open(path, "rb").read().decode("utf-8", "surrogateescape").splitlines():
        if ln.startswith("pattern "):
            yield ln[len("pattern "):]


def jobs():
    n = 0
    for fn in [] if "bench-cap" not in POPS else sorted(os.listdir(f"{BENCH}/capability/patterns")):
        if not fn.endswith(".rx"):
            continue
        pat = open(f"{BENCH}/capability/patterns/{fn}", "rb").read().rstrip(b"\n") \
            .decode("utf-8", "surrogateescape")
        for enc in ENCS:
            for cfg, flags in CAP_CFG.items():
                n += 1
                yield (n, "bench-cap", "capability", fn[:-3], pat, cfg, flags, enc)
    seen = set()
    for path in [] if "bench-rxt" not in POPS else \
            sorted(glob.glob(f"{BENCH}/*/export/*.rxt") + [f"{BENCH}/utf8/patterns.rxt"]):
        src = path[len(BENCH) + 1:].split("/")[0]
        if src in SKIP_SRC:
            continue
        for pat in rxt_patterns(path):
            if (src, pat) in seen:
                continue
            seen.add((src, pat))
            for enc in ENCS:
                for cfg, flags in TXT_CFG.items():
                    n += 1
                    yield (n, "bench-rxt", src, pat, pat, cfg, flags, enc)
    seen = set()
    for path in [] if "corpus" not in POPS else \
            sorted(glob.glob(f"{ROOT}/tests/**/*.rxt", recursive=True)):
        for pat in rxt_patterns(path):
            if pat in seen:
                continue
            seen.add(pat)
            for enc in ENCS:
                for cfg, flags in TXT_CFG.items():
                    n += 1
                    yield (n, "corpus", "tests", pat, pat, cfg, flags, enc)


def main():
    lim = int(os.environ.get("LIMIT", "0"))   # a smoke run: the first LIMIT jobs
    js = [j for k, j in enumerate(jobs()) if not lim or k < lim]
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, js))
    json.dump(res, open(f"{SCR}/ship_census.json", "w"), indent=0)
    print("== IDENTITY (base vs new, no analysis named; raw bytes)")
    for enc in ENCS:
        rs = [r for r in res if r["enc"] == enc]
        print(f"  -e {enc}: {len(rs)} artifact-configs",
              dict(collections.Counter(r["identity"] for r in rs)))
        for r in rs:
            if r["identity"] in ("changed", "mismatch"):
                print(f"   IDENTITY-{r['identity'].upper()} {r['pop']} {r['cfg']} {r['key'][:70]!r}")
    for n in SHIPPED:
        for enc in ENCS:
            rs = [r for r in res if r["enc"] == enc]
            ch = [r for r in rs if r["ship_" + n] == "changed"]
            reach = sum(1 for r in rs if (r.get("findings_" + n) or "").startswith(f"byte-rate={n}:"))
            print(f"== SHIP {n} -e {enc}: {len(rs)} artifact-configs,",
                  dict(collections.Counter(r["ship_" + n] for r in rs)),
                  f"| REACH (consumed byte-rate={n}): {reach}")
            print("   by population:", dict(collections.Counter(r["pop"] for r in ch)))
            print("   by stamps moved:", dict(collections.Counter(",".join(r["moved_" + n]) for r in ch)))
            # b1_mover_answers.py's shape: corpus-keyed patterns carry pop "corpus"
            mv = [{"pop": "corpus" if r["pop"] != "bench-cap" else "bench",
                   "key": r["key"], "cfg": r["cfg"], "identity": "changed"} for r in ch]
            json.dump(mv, open(f"{SCR}/movers_{n}_{enc}.json", "w"), indent=0)


if __name__ == "__main__":
    main()
