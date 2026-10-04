#!/usr/bin/env python3
"""[OPT-GAPREPORT] step 2: the D81 stamps of every bench pattern, per compiler.

Compiles each `bench/<set>/patterns/*.rx` export with the bench's own
`pcrec-auto` flags (`--features all`, plus `-e utf8` on bench/utf8 --
pcrec-bench testees/pcrec/configs.toml) and reads every scalar `RX_*`
`#define` off the emitted pair.  Compile-side only; nothing is matched or
timed.  pcrec-bench is read, never written.

    PCREC=/path/to/pcrec BENCH=/path/to/pcrec-bench/bench OUT=/scratch/dir \
      python3 stamps.py LABEL > stamps_LABEL.json

`code_sha` hashes the emitted .c/.h with comments, every `#define RX_*`
line and every line naming the abi removed: an APPROXIMATE "did the program
move" indicator between two compilers, not the bench's program-identity
census (tools/program_identity.py there, normalization v2).
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys

from gapconfig import SETS as SETS_CONFIG

PCREC = os.environ["PCREC"]
BENCH = os.environ.get("BENCH", "/Users/fdicostanzo/pcrec-bench/bench")
OUT = os.environ["OUT"]
SETS = SETS_CONFIG
ABI = re.compile(r"\(abi (\d+)\)")
DEF = re.compile(r'^#define\s+(RX_[A-Z0-9_]+)\s+("[^"]*"|-?[0-9][0-9A-Fa-fxuUL]*)\s*$', re.M)


def norm(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    keep = [l for l in text.split("\n")
            if not l.startswith("#define RX_") and "abi" not in l.lower()
            and not l.lstrip().startswith("//")]
    return hashlib.sha256("\n".join(keep).encode()).hexdigest()[:16]


def one(job):
    sb, fn, extra = job
    name = fn[:-3]
    pat = open(os.path.join(BENCH, sb, "patterns", fn), "rb").read()
    art = os.path.join(OUT, f"{sb}__{re.sub(r'[^A-Za-z0-9_.-]', '_', name)}.c")
    try:
        r = subprocess.run(["nice", "-n", "10", PCREC, "--features", "all",
                            *extra, "-o", art, "--pattern", pat],
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return sb, name, {"refused": "compile timeout 300 s"}
    if r.returncode != 0:
        return sb, name, {"refused": r.stderr.decode("utf8", "replace")
                          .strip().split("\n")[0][:200]}
    text = ""
    for p in (art, art[:-2] + ".h"):
        try:
            text += open(p, encoding="utf8", errors="replace").read()
        except OSError:
            pass
    st = {k: v.strip('"') for k, v in DEF.findall(text)}
    m = ABI.search(text)
    if m:
        st["ABI"] = m.group(1)
    st["code_sha"] = norm(text)
    st["c_bytes"] = os.path.getsize(art)
    for p in (art, art[:-2] + ".h"):
        try:
            os.remove(p)
        except OSError:
            pass
    return sb, name, st


def main():
    os.makedirs(OUT, exist_ok=True)
    for sb in SETS:
        if not os.path.isdir(os.path.join(BENCH, sb, "patterns")):
            print(f"stamps.py: WARNING set {sb} has no patterns/ under {BENCH}",
                  file=sys.stderr)
    jobs = [(sb, fn, extra) for sb, extra in SETS.items()
            if os.path.isdir(os.path.join(BENCH, sb, "patterns"))
            for fn in sorted(os.listdir(os.path.join(BENCH, sb, "patterns")))
            if fn.endswith(".rx")]
    res = {}
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("STAMPS_JOBS", "1"))) as ex:
        for sb, name, st in ex.map(one, jobs):
            res.setdefault(sb, {})[name] = st
    json.dump({"label": sys.argv[1], "pcrec": PCREC, "stamps": res},
              sys.stdout, indent=0, sort_keys=True)


if __name__ == "__main__":
    main()
