#!/usr/bin/env python3
"""[OPT-LITSCAN] S4 C3 r1/r2: the single-ranking census (compile-only).

Compiles every corpus `.rxt` pattern (as written, via `--list-source`; flags
`i` -> `-i`, `u` -> `--ucp`, column 9 -> `-e`) and every pcrec-bench
`bench/*/patterns/*.rx` export (read-only; `-e utf8` for the utf8 set) with
`--features all --emit-facts` under TWO binaries:

  BASE   main as-is (today's exact-only walk)
  PROTO  main + proto.patch: the r1 walk (one triple, positions (T,K) with K
         0xFF or a two-member cube, ranking by sum popcount(K), the
         alternation cube hull) plus, at r2, the (T, K) PICK primitive, the
         member-mass window, `req_byte`'s exact-member clause and the
         exact sub-window pin (`run_pin` renders `o` for a whole-window
         pin, `o:at+len` for a sub-window). Facts only -- PROTO's emitted C
         is NOT meaningful (its emitters still read T as exact bytes), and
         nothing here reads it.

and writes one TSV row per (population, pattern) for c3_report.py.

Env: BASE PROTO BENCH CORPUS OUT JOBS (r2: run serially, JOBS=1, the default)
"""
import os, sys, glob, subprocess, concurrent.futures as cf

E = os.environ
FACTS = ("req_whole_run", "req_run", "req_byte", "run_pin")
STAMPS = ("RX_REQ_WHY", "RX_DFA_PREFILTER", "RX_ENGINE", "RX_REQ_BYTE", "RX_REQ_RUN")


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


def bench_pop():
    rows = []
    for p in sorted(glob.glob(os.path.join(E["BENCH"], "bench", "*", "patterns", "*.rx"))):
        setname = p.split(os.sep)[-3]
        b = open(p, "rb").read().rstrip(b"\n")
        if b and b"\0" not in b:
            args = ["-e", "utf8"] if setname == "utf8" else []
            rows.append(("bench", "%s/%s" % (setname, os.path.basename(p)[:-3]), b, args))
    return rows


def corpus_pop():
    rows = []
    files = sorted(os.path.join(r, f) for r, _d, fs in os.walk(os.path.join(E["CORPUS"], "tests"))
                   for f in fs if f.endswith(".rxt"))
    for f in files:
        r = subprocess.run([E["BASE"], "--list-source", f], capture_output=True, timeout=120)
        if r.returncode: continue
        rel = os.path.relpath(f, E["CORPUS"])
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
    return rows


def facts(binary, pat, args):
    try:
        r = subprocess.run([binary.encode(), b"--features", b"all", b"--emit-facts", *[a.encode() for a in args], b"--pattern",
                            pat], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode: return None
    d = {}
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] in FACTS and f[1] not in d: d[f[1]] = f[6]
        elif len(f) == 3 and f[1] in STAMPS and f[1] not in d: d[f[1]] = f[2]
    return d


def one(row):
    pop, ident, pat, args = row
    b = facts(E["BASE"], pat, args); p = facts(E["PROTO"], pat, args)
    if b is None or p is None:
        return "\t".join([pop, ident, pat.hex(), " ".join(args), "refused"] + ["-"] * (2 * len(FACTS) + len(STAMPS)))
    return "\t".join([pop, ident, pat.hex(), " ".join(args), "ok"]
                     + [b.get(k, "-") for k in FACTS] + [b.get(k, "-") for k in STAMPS]
                     + [p.get(k, "-") for k in FACTS])


def main():
    rows = bench_pop() + corpus_pop()
    print("patterns:", len(rows), file=sys.stderr)
    hdr = ["pop", "id", "pattern_hex", "args", "status"] + ["base_" + k for k in FACTS + STAMPS] + ["proto_" + k for k in FACTS]
    with open(os.path.join(E.get("OUT", "."), "c3_census.tsv"), "w") as out, \
         cf.ThreadPoolExecutor(int(E.get("JOBS", "1"))) as ex:
        out.write("\t".join(hdr) + "\n")
        for i, line in enumerate(ex.map(one, rows)):
            out.write(line + "\n")
            if i % 500 == 0: print(i, file=sys.stderr, flush=True)
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
