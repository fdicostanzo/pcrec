"""ofs_reprobe.py PROBE_PCREC TREE BENCH_DIR [--jobs N] -- the design's PREM-6
re-probe (docs/design/alt_normal_form.md §4.2 NOTED; lane altbuild2,
2026-11-06): does any compile reach `ofs_test_of` with a MASKED position
inside the pinned run term, the case where `ofs_test_at` would render the
masked position as the exact byte T in `<PREFIX>_DFA_PREFILTER_OFFSETS`'s
listing because `ofs_test_of` leaves `OfsTest.run_mask` NULL?

PROBE_PCREC is a scratch build of the stage tree with one stderr line added in
`ofs_test_of`'s run-term arm: `OFSPROBE run_len=L masked=M hasmask=H` (M =
run positions whose fact mask is not 0xFF). POPULATION: every corpus pattern
block, at its own encoding (`pcrec --list-source`), and every
BENCH_DIR/**/*.rx line at byte and at utf8, each on two flag sets: the
default and the offset rows' own test spelling (`--no-captures --features all
--memfn=no-window-search`, tests/codegen/run_offset_skip.sh). Reports the
run-term reach (K35: a sweep that reaches no run term measured nothing) and
every masked reach."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

FLAGSETS = [("default", ["--features", "all"]),
            ("ofs", ["--no-captures", "--features", "all", "--memfn=no-window-search"])]

def unesc(s):
    out, i = bytearray(), 0
    b = s.encode("utf-8", "surrogateescape")
    while i < len(b):
        if b[i] == 0x5c and i + 1 < len(b):
            c = chr(b[i + 1])
            if c == "x": out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
            out.append({"t": 9, "n": 10, "r": 13, "\\": 92}.get(c, b[i + 1])); i += 2; continue
        out.append(b[i]); i += 1
    return bytes(out)

def corpus(pcrec, tree):
    pats = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in sorted(fs):
            if not f.endswith(".rxt"): continue
            p = os.path.join(d, f)
            r = subprocess.run([pcrec, "--list-source", p], capture_output=True, timeout=60)
            if r.returncode: continue
            head_enc, seen = "", False
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#"): continue
                c = line.split("\t")
                if len(c) < 10: continue
                if c[0] == "encoding" and not seen: head_enc = c[3]
                if c[0] not in ("pattern", "pattern-esc"): continue
                seen = True
                pats.append((os.path.relpath(p, tree) + ":" + c[1], unesc(c[4]), c[5],
                             c[8] or head_enc or "byte"))
    return pats

def bench(d):
    pats = []
    for root, _, fs in os.walk(d):
        for f in sorted(fs):
            if not f.endswith(".rx"): continue
            for i, line in enumerate(open(os.path.join(root, f), "rb").read().split(b"\n")):
                if line:
                    for enc in ("byte", "utf8"):
                        pats.append((os.path.relpath(os.path.join(root, f), d) + ":" + str(i + 1), line, "", enc))
    return pats

def cell(args):
    pcrec, (where, pat, flags, enc), (fs, extra) = args
    inl = "".join(x for x in flags if x in "msx")
    if inl: pat = b"(?" + inl.encode() + b")" + pat
    argv = [pcrec, "-p", "rx", "-e", enc, "-o", "-"] + (["-i"] if "i" in flags else []) + extra + ["--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return where, enc, fs, "TIMEOUT", 0, 0
    runs = masked = 0
    for line in r.stderr.decode("ascii", "replace").splitlines():
        if line.startswith("OFSPROBE "):
            runs += 1
            if int(line.split("masked=")[1].split()[0]) > 0: masked += 1
    return where, enc, fs, "REFUSED" if r.returncode else "ok", runs, masked

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    pcrec, tree, bdir = a
    pats = corpus(pcrec, tree) + bench(bdir)
    tasks = [(pcrec, p, f) for p in pats for f in FLAGSETS]
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(cell, tasks))
    reached = [r for r in res if r[4] > 0]
    masked = [r for r in res if r[5] > 0]
    print("population: %d patterns x %d flag sets = %d compiles (%d refused, %d timeouts)"
          % (len(pats), len(FLAGSETS), len(res), sum(r[3] == "REFUSED" for r in res),
             sum(r[3] == "TIMEOUT" for r in res)))
    for fs, _ in FLAGSETS:
        print("  %-8s run-term reach: %d compiles; masked position inside the run: %d"
              % (fs, sum(1 for r in reached if r[2] == fs), sum(1 for r in masked if r[2] == fs)))
    for r in masked: print("MASKED\t%s\t%s\t%s" % r[:3])
    if not reached:
        print("FLOOR: no compile reached the run term: the sweep measured nothing"); sys.exit(1)

main()
