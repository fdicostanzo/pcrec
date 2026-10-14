#!/usr/bin/env python3
"""R-17 (lane r17s): the FIND-site population census, by SET SHAPE.

Compiles every distinct .rxt corpus pattern (scripts/emit_sweep.py's
enumeration, the N2 census's population) twice -- the default engine and
`--engine=vm` -- with `--features all`, and reads the EMITTED C (no traced
build, no src/ edit):

  - every PF/VM-hat FIND rendered as a table walk,
      while (P[ + 1] < N && !T[S[P]]) P++;
    its table `T` parsed from the artifact's own `static const unsigned char
    T[256]` initializer, its role read off the table's suffix:
      can_begin_match -> DFA prefilter `byte-class[-bounded]`
      start_bytes     -> DFA hat `first-*-bounded`
      start_set       -> VM hat seek (entry + retry: two statements, one site)
  - every PF FIND rendered as memchr on `scan_position` (|S| = 1 already);
  - every offset-skip/pre-check FUNC helper (`*__body`) that holds NO memchr
    (a scanned SET the BODY rows decline, rendered by the generic row).

Each walked set is classified: |S|, ONE CUBE ((x & K) == T exactly), ONE
RANGE (contiguous), the number of maximal runs, and the size of a greedy
cover by prime cubes (Quine-McCluskey primes over 8 variables, greedy pick).

    census.py --bin build/pcrec --tree . --out OUTDIR [--jobs 4] [--limit N]
    census.py --bin build/pcrec --files a.c b.c ...    (classify artifacts only)
    census.py --bin build/pcrec --bench BENCHTREE --out OUTDIR   (the bench's own
        patterns, compiled as its pcrec-auto testee: --features all, -e utf8 on
        the utf8 set, --pattern-esc; read-only on BENCHTREE)

Writes OUTDIR/sites.tsv (one row per walk statement) and prints the roll-up.
Pin it (`taskset -c 12-15`) on a shared box; it does no timing.
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys

WALK_RE = re.compile(r"while \((\w+)( \+ 1)? < (\w+) && !(\w+)\[(\w+)\[\1\]\]\) \1\+\+;")
TABLE_RE = re.compile(r"static const unsigned char (\w+)\[256\] = \{([^}]*)\};", re.S)
PFMEMCHR_RE = re.compile(r"const void \*q = memchr\(subject \+ scan_position, (\d+),")
BODY_RE = re.compile(r"static inline size_t (\w+__body)\([^)]*\)\n\{(.*?)\n\}\n", re.S)


def table_role(name):
    for suf, role in (("can_begin_match", "dfa-pf"), ("start_bytes", "dfa-hat"),
                      ("start_set", "vm-hat")):
        if name.endswith(suf):
            return role
    return "other:" + name


def primes(members):
    """Prime implicants (care, val) of the 8-variable function `members`."""
    cur = {(0xFF, m) for m in members}
    allp = set()
    while cur:
        nxt, used = set(), set()
        lst = sorted(cur)
        by_care = collections.defaultdict(list)
        for c, v in lst:
            by_care[c].append(v)
        for c, vs in by_care.items():
            vset = set(vs)
            for v in vs:
                for b in range(8):
                    bit = 1 << b
                    if c & bit and not v & bit and (v | bit) in vset:
                        nxt.add((c & ~bit, v))
                        used.add((c, v))
                        used.add((c, v | bit))
        allp |= cur - used
        cur = nxt
    return allp


def cube_cover(members):
    if not members:
        return 0
    if len(members) > 64:
        return -1          # not needed for the shapes R-17 names
    ps = sorted(primes(members), key=lambda p: -bin(~p[0] & 0xFF).count("1"))
    left = set(members)
    n = 0
    while left:
        best = max(ps, key=lambda p: sum(1 for x in left if x & p[0] == p[1]))
        left = {x for x in left if x & best[0] != best[1]}
        n += 1
    return n


def classify(members):
    s = sorted(members)
    n = len(s)
    a, o = 0xFF, 0
    for x in s:
        a &= x
        o |= x
    free = a ^ o
    one_cube = n == 1 << bin(free).count("1")
    runs = 0
    for i, x in enumerate(s):
        if i == 0 or s[i - 1] != x - 1:
            runs += 1
    one_range = runs == 1
    shape = ("byte" if n == 1 else "pair-cube" if n == 2 and one_cube else
             "pair" if n == 2 else "cube" if one_cube else
             "range" if one_range else "small" if n <= 8 else "wide")
    return {"n": n, "cube": one_cube, "range": one_range, "runs": runs,
            "cubes": cube_cover(s), "shape": shape,
            "members": ",".join("%02x" % x for x in s) if n <= 16 else
            "%02x..%02x" % (s[0], s[-1])}


def analyse(text):
    tables = {}
    for m in TABLE_RE.finditer(text):
        vals = [int(v) for v in m.group(2).replace("\n", " ").split(",") if v.strip()]
        if len(vals) == 256:
            tables[m.group(1)] = [i for i, v in enumerate(vals) if v]
    rows = []
    seen = set()
    for m in WALK_RE.finditer(text):
        tname = m.group(4)
        bounded = 1 if m.group(2) else 0
        key = (tname, bounded)
        stmt_dup = key in seen
        seen.add(key)
        mem = tables.get(tname)
        if mem is None:
            continue
        c = classify(mem)
        c.update(role=table_role(tname), bounded=bounded, dup=int(stmt_dup))
        rows.append(c)
    pfm = [int(x) for x in PFMEMCHR_RE.findall(text)]
    bodies = list(BODY_RE.finditer(text))
    generic_bodies = [b.group(1) for b in bodies if "memchr(" not in b.group(2)]
    return rows, pfm, generic_bodies, len(bodies)


def esc(b):
    """lossreview/misc/mk.py's --pattern-esc spelling of raw pattern bytes."""
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


def compile_one(bin_path, pat, engine, timeout):
    argv = [bin_path, "-p", "rx", "--features", "all"]
    if engine:
        argv.append("--engine=%s" % engine)
    if isinstance(pat, tuple):                  # (bench set, raw bytes)
        argv += (["-e", "utf8"] if pat[0] == "utf8" else []) + ["-o", "-", "--pattern-esc",
                                                                 "--pattern", '"' + esc(pat[1]) + '"']
    else:
        argv += ["-o", "-", "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.decode("latin-1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--bench")
    a = ap.parse_args()

    if a.files:
        for f in a.files:
            rows, pfm, gb, _ = analyse(open(f, encoding="latin-1").read())
            for r in rows:
                print("%s\t%s\tbounded=%d\tdup=%d\tn=%d\tshape=%s\tcubes=%d\truns=%d\t%s"
                      % (f, r["role"], r["bounded"], r["dup"], r["n"], r["shape"],
                         r["cubes"], r["runs"], r["members"]))
            for b in pfm:
                print("%s\tdfa-pf-memchr\tbyte=%02x" % (f, b))
            for g in gb:
                print("%s\tgeneric-body\t%s" % (f, g))
        return

    if a.bench:
        pats = []
        root = os.path.join(a.bench, "bench")
        for st in sorted(os.listdir(root)):
            pd = os.path.join(root, st, "patterns")
            if not os.path.isdir(pd):
                continue
            for f in sorted(os.listdir(pd)):
                if f.endswith(".rx"):
                    b = open(os.path.join(pd, f), "rb").read().rstrip(b"\n")
                    pats.append((st, b, st + "/" + f[:-3]))
        pats = [(p[0], p[1]) for p in pats]
    else:
        sys.path.insert(0, os.path.join(os.path.abspath(a.tree), "scripts"))
        import emit_sweep
        corpus = emit_sweep.enumerate_corpus(os.path.abspath(a.bin), os.path.abspath(a.tree), a.timeout)
        pats = emit_sweep.distinct_patterns(corpus)
    if a.limit:
        pats = pats[:a.limit]
    os.makedirs(a.out, exist_ok=True)
    jobs = [(p, e) for p in pats for e in (None, "vm")]

    def one(job):
        p, e = job
        t = compile_one(os.path.abspath(a.bin), p, e, a.timeout)
        return job, (analyse(t) if t is not None else None)

    tot = collections.Counter()
    pat_shapes = collections.defaultdict(set)
    nfail = 0
    with open(os.path.join(a.out, "sites.tsv"), "w") as fo, \
            concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        fo.write("stream\trole\tbounded\tdup\tn\tshape\tcube\trange\truns\tcubes\tmembers\tpattern\n")
        for (p, e), res in ex.map(one, jobs):
            stream = "vm" if e else "default"
            if res is None:
                nfail += 1
                continue
            rows, pfm, gb, nb = res
            tot[(stream, "body-total (K35: the generic-body census's population)", "-")] += nb
            for r in rows:
                fo.write("%s\t%s\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%s\t%r\n" % (
                    stream, r["role"], r["bounded"], r["dup"], r["n"], r["shape"],
                    r["cube"], r["range"], r["runs"], r["cubes"], r["members"], p))
                if not r["dup"]:
                    tot[(stream, r["role"], r["shape"])] += 1
                    pat_shapes[(stream, r["role"], r["shape"])].add(p)
            for _ in pfm:
                tot[(stream, "dfa-pf-memchr", "byte")] += 1
            for _ in gb:
                tot[(stream, "generic-body", "-")] += 1
    print("patterns=%d compiles=%d failed=%d" % (len(pats), len(jobs), nfail))
    print("stream\trole\tshape\tsites")
    for k in sorted(tot):
        print("%s\t%s\t%s\t%d" % (k[0], k[1], k[2], tot[k]))


if __name__ == "__main__":
    main()
