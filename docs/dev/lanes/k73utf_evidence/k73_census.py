#!/usr/bin/env python3
"""[K73] the EMITTED-C MOVER CENSUS: which artifacts does the offset-0 start
rule move, and by what?

Compiles every distinct `pattern` line of tests/**/*.rxt with two compilers
(BASE = the branch point, NEW = the fix) under three configs and compares the
emitted .c byte for byte, same -p and same -o basename, after normalising the
abi number (45 on BASE, 46 on NEW: the generated-by line and `.abi =`).

PREDICTION (stated before the run): a mover is exactly a NULLABLE pattern's
utf8 artifact (the `pcrec_startgate_needed` fact), and every added line is one
of the [K73] start-zero lines (`if (<pos> == 0 && !(...)) ...`) or the K50
guard the unwrapped-form DFA `<prefix>_match` gains (`if (!(search_from == 0
|| ...)) return PCREC_ERR_STARTPOS;`, which moves NON-nullable utf8 DFA
artifacts too). The one REMOVED line class is ENG_ATTEMPT's `continue` gate,
whose rendered predicate loses its dead `start == 0 ||` clause. Every byte
artifact is identical. Anything else prints UNPREDICTED.

  BASE=<pcrec> NEW=<pcrec> SCR=<scratch> PROCS=2 python3 k73_census.py
"""
import os, re, sys, glob, json, difflib, subprocess, collections
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
CFG = {"byte":        ["--features", "all"],
       "utf8":        ["--features", "all", "-e", "utf8"],
       "utf8-vm":     ["--features", "all", "-e", "utf8", "--engine=vm"]}
ABI = re.compile(r'(\(abi |\.abi = )4[56]\b')
ZERO = re.compile(r'^\s*if \((search_from|start|attempt_position|ctx->pos) == 0 && !\(.*\)\) '
                  r'(do \1\+\+; while \(!\(.*\)\);|return -1;|continue;)$')
GUARD = re.compile(r'^\s*if \(!\(search_from == 0 \|\| .*\)\) return PCREC_ERR_STARTPOS;$')
CONT = re.compile(r'^\s*if \(start > search_from && !\(.*\)\) continue;$')
# the K50 guard's own comment, which its text carries unconditionally
GCMT = {"/* [K50] A caller's start position must be a CHARACTER BOUNDARY of",
        "* this artifact's encoding. A mid-character position is REFUSED",
        "* rather than answered: nothing is attempted and no resource is",
        "* spent, which is why the code sits below PCREC_ERR_FLOOR and is",
        "* not a give-up. libpcre2 under PCRE2_UTF refuses the same",
        "* positions (PCRE2_ERROR_BADUTFOFFSET). Compile with",
        "* -fno-startpos-guard for the permissive semantics instead. */"}


def known(x):
    return bool(ZERO.match(x) or GUARD.match(x) or CONT.match(x)) or x.strip() in GCMT


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
    return ABI.sub(r'\1N', open(out, "rb").read().decode("latin-1"))


def one(job):
    i, pat, cfg, flags = job
    b = emit(BASE, pat, flags, f"{SCR}/c/{i}/b")
    a = emit(NEW, pat, flags, f"{SCR}/c/{i}/a")
    rec = {"pat": pat, "cfg": cfg}
    if b is None or a is None or "TIMEOUT" in (a, b):
        rec["identity"] = "refused" if b is None and a is None else \
            ("timeout" if "TIMEOUT" in (a, b) else "refusal-mismatch")
        return rec
    rec["identity"] = "identical" if a == b else "changed"
    if a == b:
        return rec
    al, bl = a.splitlines(), b.splitlines()
    added, removed = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, bl, al, autojunk=False).get_opcodes():
        removed += bl[i1:i2]
        added += al[j1:j2]
    rec["zero"] = sum(bool(ZERO.match(x)) for x in added)
    rec["guard"] = sum(bool(GUARD.match(x)) for x in added)
    rec["cont"] = sum(bool(CONT.match(x)) for x in added)
    rec["other_added"] = [x for x in added if not known(x)]
    rec["other_removed"] = [x for x in removed if not CONT.match(x)]
    rec["engine"] = (re.search(r'^#define RX_ENGINE "(\w+)"', a, re.M) or [None, None])[1]
    return rec


def jobs():
    n, seen = 0, set()
    for path in sorted(glob.glob(f"{ROOT}/tests/**/*.rxt", recursive=True)):
        for ln in open(path, "rb").read().decode("utf-8", "surrogateescape").splitlines():
            if not ln.startswith("pattern "):
                continue
            pat = ln[len("pattern "):]
            if pat in seen:
                continue
            seen.add(pat)
            for cfg, flags in CFG.items():
                n += 1
                yield (n, pat, cfg, flags)


def main():
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "2"))) as ex:
        res = list(ex.map(one, jobs()))
    json.dump(res, open(f"{SCR}/k73_census.json", "w"), indent=0)
    for cfg in CFG:
        rs = [r for r in res if r["cfg"] == cfg]
        ch = [r for r in rs if r["identity"] == "changed"]
        unp = [r for r in ch if r["other_added"] or r["other_removed"]]
        print(f"== {cfg}: {len(rs)} patterns; " +
              ", ".join(f"{k} {v}" for k, v in sorted(collections.Counter(r['identity'] for r in rs).items())))
        if ch:
            print(f"   movers {len(ch)}: with zero-rule lines {sum(r['zero'] > 0 for r in ch)}, "
                  f"with the new _match guard {sum(r['guard'] > 0 for r in ch)}, "
                  f"zero-rule lines total {sum(r['zero'] for r in ch)}; UNPREDICTED {len(unp)}")
        for r in unp[:10]:
            print(f"   UNPREDICTED {r['pat'][:60]!r} +{r['other_added'][:2]} -{r['other_removed'][:2]}")
        for r in rs:
            if r["identity"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['identity'].upper()} {r['pat'][:70]!r}")


if __name__ == "__main__":
    main()
