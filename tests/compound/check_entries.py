#!/usr/bin/env python3
"""tests/compound/check_entries.py -- [COMPOUND] B0's unit check: an entry
request leaves exactly its closure (docs/design/compound.md §A.4, §F row B0).

  check_entries.py DRIVE PCREC TREE WORKDIR [--every N] [--jobs J]

DRIVE is tests/compound/compound_drive.c built (its `entries` subcommand
writes, per pattern, the plain artifact and one artifact per request). The
population is every distinct corpus pattern (tests/startset/startset_lib.py's
reader), every N-th of it plus the named WITNESSES below, under three arms:
byte, utf8 with -futf-check (the subject check's edges), utf8.

Per pattern and request, all with the harness's generated-code warnings
(`-O0 -std=gnu11 -Wall -Wextra -Werror`, compiled `-c`):

  (1) the reduced artifact compiles. An entry the closure kept but nothing
      reaches is an unused static (an error here); one it omitted that
      something calls is an implicit declaration (an error here). So a
      clean build is the claim that the closure is exact, read by a tool
      that shares nothing with src/gen/entries.c's edge table.
  (2) its global symbols are exactly the PLAIN artifact's `nm -g` set
      restricted to the request's exported names (compound.md §E.3 G4's
      rule: the expected set comes from the plain artifact, never from the
      closure), plus the stub array a keep request adds.
  (3) a kept entry is present, as a local symbol.
  (4) positive control: the reduced artifact is not the plain one's text.

Population floors (K35): the checked rows per arm, and per arm the shapes
whose edges differ (DFA, VM, VM hybrid, VM forward entries, DFA anchored
`_match`), each read off the artifact's own stamps. Exit 1 on any failure.
"""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "startset"))
from startset_lib import corpus_blocks  # noqa: E402

CC = os.environ.get("CC", "gcc")
CFLAGS = ["-O0", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-c"]


def _gen_timeout():
    """D45's compile budget for generated C, read from the one helper the
    shell suites source (tests/vm/vm_oracle.py's shape); fail closed on the
    plain budget if the helper cannot run."""
    try:
        r = subprocess.run(["bash", os.path.join(HERE, "..", "lib", "gen_timeout.sh"), "secs"],
                           capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    except Exception:
        return 10


GEN_TIMEOUT = _gen_timeout()
ARMS = [("byte", []), ("utf8-check", ["--enc", "utf8", "--utf-check"]),
        ("utf8", ["--enc", "utf8"])]
# Shapes a sampled corpus might miss, named so each edge family is reached.
WITNESSES = [b"a(b|c)+d", b"(a)\\1", b"foo(a|b)*\\1bar", b"^abc$", b"^ab+c",
             b"x*", b"${v}x", b"(a)${v}\\1", b"\\Ga$|b$", b"\\s+$", b"a{0,4}\\A",
             b"[^\\x00-\\xff]", b"(?<=\\x{e9})a|b", b"(abc)(def)"]
# Per-arm floors: rows checked, and artifacts of each shape.
FLOORS = {"rows": 300, "dfa": 50, "vm": 50, "hybrid": 10, "fwd": 3,
          "unwrapped": 5}
SHAPES = {
    "dfa": rb'#define RX_ENGINE "dfa"',
    "vm": rb'#define RX_ENGINE "vm"',
    "hybrid": rb'#define RX_VM_PREFILTER "hybrid"',
    "fwd": rb'#define RX_VM_ENTRY_SHAPE "forward"',
    "unwrapped": rb'#define RX_DFA_MATCH "unwrapped"',
}


def nm(obj, glob):
    """Defined symbol names of `obj`: globals, or local text/data."""
    args = ["nm", "--defined-only"] + (["-g"] if glob else []) + [obj]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    names = set()
    for ln in out.splitlines():
        f = ln.split()
        if len(f) == 3 and (glob or f[1] in "tdbr"):
            names.add(f[2])
    return names


def cc(src, obj):
    try:
        r = subprocess.run([CC] + CFLAGS + ["-o", obj, src], capture_output=True,
                           text=True, timeout=GEN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 1, "D45: the compile exceeded its %d s budget" % GEN_TIMEOUT
    return r.returncode, r.stderr


def check_one(d, pid, req, exported, kept):
    """One (pattern, request) cell; returns a list of failure strings."""
    fails = []
    plain_o = os.path.join(d, pid + ".plain.o")
    P = nm(plain_o, True)
    src = os.path.join(d, "%s.%s.c" % (pid, req))
    text = open(src, "rb").read()
    if text == open(os.path.join(d, pid + ".plain.c"), "rb").read():
        fails.append("%s %s: positive control: identical to the plain artifact" % (pid, req))
    names = [] if kept == "-" else kept.split(",")
    keep = [("rx_" + n) for n in names if ("rx_" + n) in P]
    tu = src
    if keep:
        tu = os.path.join(d, "%s.%s.tu.c" % (pid, req))
        with open(tu, "wb") as f:
            f.write(text)
            f.write(b"\nvoid (*const rx_drive_keep[])(void) = {\n")
            for k in keep:
                f.write(b"    (void (*)(void))%s,\n" % k.encode())
            f.write(b"};\n")
    obj = os.path.join(d, "%s.%s.o" % (pid, req))
    rc, err = cc(tu, obj)
    if rc:
        fails.append("%s %s: -Werror build failed: %s" % (pid, req, err.strip()[:300]))
        return fails
    G = nm(obj, True)
    want = {("rx_" + n) for n in ([] if exported == "-" else exported.split(","))} & P
    if keep: want.add("rx_drive_keep")
    if G != want:
        fails.append("%s %s: globals %s, expected %s" % (pid, req, sorted(G), sorted(want)))
    L = nm(obj, False)
    for k in keep:
        if k not in L:
            fails.append("%s %s: kept entry %s is not a local symbol" % (pid, req, k))
    return fails


def run_arm(drive, work, arm, args, pats, jobs):
    d = os.path.join(work, arm)
    os.makedirs(d, exist_ok=True)
    listing = "".join("p%d\t%s\n" % (i, p.hex()) for i, p in enumerate(pats))
    r = subprocess.run([drive, "entries", d] + args, input=listing.encode(),
                       capture_output=True, timeout=3600)
    if r.returncode:
        print("FAIL: compound_drive %s exited %d: %s" % (arm, r.returncode,
              r.stderr.decode(errors="replace")[:400]))
        return None
    rows = [ln.split("\t") for ln in r.stdout.decode().splitlines()]
    ok_pids = sorted({row[0] for row in rows if row[1] != "plain"})
    refused = [row for row in rows if row[1] != "plain" and row[2] != "ok"]
    fails = ["%s %s: the request refused where the plain compile did not" % (row[0], row[1])
             for row in refused]
    # The plain objects first (every request is held to its `nm -g`).
    def plain(pid):
        rc, err = cc(os.path.join(d, pid + ".plain.c"), os.path.join(d, pid + ".plain.o"))
        return pid, rc, err
    bad_plain = set()
    with ThreadPoolExecutor(jobs) as ex:
        for pid, rc, err in ex.map(plain, ok_pids):
            if rc:
                bad_plain.add(pid)
                fails.append("%s plain: -Werror build failed: %s" % (pid, err.strip()[:200]))
    cells = [row for row in rows if row[1] != "plain" and row[2] == "ok"
             and row[0] not in bad_plain]
    with ThreadPoolExecutor(jobs) as ex:
        for f in ex.map(lambda row: check_one(d, row[0], row[1], row[3], row[4]), cells):
            fails += f
    shapes = {k: 0 for k in SHAPES}
    for pid in ok_pids:
        t = open(os.path.join(d, pid + ".plain.c"), "rb").read()
        for k, pat in SHAPES.items():
            if pat in t: shapes[k] += 1
    return {"patterns": len(ok_pids), "rows": len(cells), "fails": fails,
            "shapes": shapes}


def main():
    drive, pcrec, tree, work = sys.argv[1:5]
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 4
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    blocks, _ = corpus_blocks(pcrec, tree)
    seen, pats = set(), []
    for b in blocks:
        if b["pattern"] not in seen:
            seen.add(b["pattern"]); pats.append(b["pattern"])
    sample = pats[::every] + [w for w in WITNESSES if w not in pats[::every]]
    total_fail = 0
    for arm, args in ARMS:
        res = run_arm(drive, work, arm, args, sample, jobs)
        if res is None:
            return 1
        for f in res["fails"][:40]:
            print("FAIL: [%s] %s" % (arm, f))
        total_fail += len(res["fails"])
        floors_ok = res["rows"] >= FLOORS["rows"] and all(
            res["shapes"][k] >= FLOORS[k] for k in SHAPES)
        print("%s: [%s] %d patterns, %d request cells, %d failures; shapes %s"
              % ("PASS" if not res["fails"] and floors_ok else "FAIL", arm,
                 res["patterns"], res["rows"], len(res["fails"]),
                 " ".join("%s=%d" % kv for kv in res["shapes"].items())))
        if not floors_ok:
            print("FAIL: [%s] below a population floor %s" % (arm, FLOORS))
            total_fail += 1
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
