#!/usr/bin/env python3
"""[OPT-HYB-RESEED] witness differential for the r1 panel's coverage gaps
(docs/dev/reviews/2026-09-30-r1-hyb-reseed.md "sem gaps"): witnesses whose
subjects MATCH (thousands of times, not only the no-match path) and subjects
over 100 KB, branch point (abi 46) against this change.

For each (pattern, encoding) the script builds a token alphabet that
completes matches and near-misses (the failing candidates the retry has to
leave), and generates deterministic subjects at three densities and three
sizes: 4 KB (every startpos), 300 KB and 1 MiB (find-all plus 400 seeded
startpos). Both compilers' artifacts are linked with one driver that prints
the full result per call (return code and caps[0]); the two transcripts
must be byte-equal.

THE BUDGET ARM (tuning.md §2.33's one-direction claim): the same witnesses
are compiled again under --step-budget=B / --work-budget=W, run on the 300 KB
subjects (find-all), and compared call by call. A call where base ANSWERED
(1 or 0) must answer identically; a call where base GAVE UP may give up or
answer. Any "base answered, new gave up or answered differently" is a
violation.

Usage: answer_diff_witness.py BASE_PCREC NEW_PCREC OUT_LOG [--jobs 2]
"""
import argparse, concurrent.futures, os, random, subprocess, sys, tempfile

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
extern int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
static ptrdiff_t c[4096][2];   /* rx_search writes every group's span */
static void one(const unsigned char *s, size_t n, size_t sp) {
    c[0][0] = c[0][1] = -9;
    int r = rx_search(s, n, sp, c);
    printf("%zu:%d:%td,%td\n", sp, r, r == 1 ? c[0][0] : -1, r == 1 ? c[0][1] : -1);
}
/* argv: SUBJECT MODE(all|find|sample) [SEED] */
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)sz + 1);
    if (fread(s, 1, (size_t)sz, f) != (size_t)sz) return 2;
    size_t n = (size_t)sz;
    if (!strcmp(argv[2], "all")) { for (size_t sp = 0; sp <= n; sp++) one(s, n, sp); return 0; }
    if (!strcmp(argv[2], "sample")) {
        unsigned long x = strtoul(argv[3], NULL, 10) * 2654435761ul + 1;
        for (int i = 0; i < 400; i++) { x = x * 6364136223846793005ul + 1442695040888963407ul; one(s, n, (size_t)((x >> 17) % (n + 1))); }
        return 0;
    }
    size_t pos = 0;             /* find-all, the bench driver's loop */
    while (pos <= n) {
        c[0][0] = c[0][1] = -9;
        int r = rx_search(s, n, pos, c);
        printf("%zu:%d:%td,%td\n", pos, r, r == 1 ? c[0][0] : -1, r == 1 ? c[0][1] : -1);
        if (r != 1) break;
        if (c[0][1] > c[0][0]) pos = (size_t)c[0][1];
        else { pos++; while (pos < n && (s[pos] & 0xC0) == 0x80) pos++; }
    }
    return 0;
}
'''

# (pattern, encoding, match tokens, near-miss tokens). The match tokens make
# the pattern MATCH; the near-misses are failing candidates of its prefilter.
WITNESSES = [
    ("(?<=é)x", "utf8", ["éx"], ["x", "ax"]),
    ("(?<=a|é)x", "utf8", ["ax", "éx"], ["x", "bx"]),
    ("(?<!日)本", "utf8", ["本", "語本"], ["日本"]),
    ("item(?= done)", "byte", ["item done"], ["item", "item don", "items"]),
    (" (?=the)", "byte", [" the"], [" ", " a", " th"]),
    (" (?=the)", "utf8", [" the"], [" ", " a", " th"]),
    ("[a-z](?=the)", "utf8", ["athe", "xthe"], ["a", "q", "ath"]),
    ("(?>a|ab)c", "byte", ["ac"], ["abc", "ab"]),
    ("(?>a|ab)c(?<=ac)", "byte", ["ac"], ["abc", "a"]),
    ("(?>日|日本)語(?=!)", "utf8", ["日語!"], ["日本語!", "日語", "日本語"]),
    ("(?i)(?<=AB)x", "byte", ["abx", "ABX", "aBx"], ["x", "bx", "acx"]),
    ("x(?=é)é", "utf8", ["xé"], ["x", "xe"]),
    ("(?>é|éa)c", "utf8", ["éc"], ["éac", "éa"]),
    ("[é日](?>x|xy)z", "utf8", ["éxz", "日xz"], ["éxyz", "日xy"]),
    ("\\bfoo(?=bar)", "byte", [" foobar"], ["foo", "xfoobar", " foob"]),
    ("(?m)^a(?=b)", "byte", ["\nab"], ["\na", "xab"]),
    ("(?<=a|bc)[a-c]{2,4}d", "byte", ["aabd", "bcbcd"], ["xabd", "xbbd"]),
    ("(?:aa|a)*+ab", "byte", ["ab"], ["aab"]),
    ("q(?!u)", "byte", ["qa", "q "], ["qu"]),
]
FILL = {"byte": ["y", "z", " ", "k", "\n"], "utf8": ["y", " ", "語", "é", "\n"]}
BUDGETS = [["--step-budget=2000"], ["--work-budget=20000"]]


def gen(tokens_m, tokens_n, enc, size, dens, seed):
    """`dens` is the share of tokens that are pattern tokens (match or near
    miss); the rest is filler. Encoded, truncated at a character boundary."""
    rng = random.Random(seed)
    fill = FILL[enc]
    out, n = [], 0
    while n < size:
        r = rng.random()
        if r < dens * 0.3: t = rng.choice(tokens_m)
        elif r < dens: t = rng.choice(tokens_n)
        else: t = rng.choice(fill) * rng.randint(1, 6)
        b = t.encode("utf-8" if enc == "utf8" else "latin-1")
        out.append(b); n += len(b)
    s = b"".join(out)[:size]
    if enc == "utf8":
        s = s.decode("utf-8", "ignore").encode("utf-8")
    return s


def build(binp, pat, enc, extra, d, tag, drv):
    c = os.path.join(d, tag + ".c")
    argv = [binp, "--features", "all", "-p", "rx"] + (["-e", "utf8"] if enc == "utf8" else []) + extra + ["-o", c, "--pattern", pat]
    r = subprocess.run(argv, capture_output=True, timeout=120)
    if r.returncode != 0:
        return None, "compile: " + r.stderr.decode(errors="replace")[:200]
    exe = os.path.join(d, tag)
    r = subprocess.run(["gcc-16", "-O1", "-w", "-o", exe, c, drv], capture_output=True, timeout=300)
    if r.returncode != 0:
        return None, "link: " + r.stderr.decode(errors="replace")[:200]
    stamp = [l.split()[2] for l in open(c) if l.startswith("#define RX_VM_RESEED")]
    return exe, (stamp[0].strip('"') if stamp else "-")


def run(exe, subj, mode, seed=0):
    r = subprocess.run([exe, subj, mode, str(seed)], capture_output=True, timeout=600)
    return r.stdout if r.returncode == 0 else b"RC%d" % r.returncode


def one(a, idx, w, tmp):
    pat, enc, tm, tn = w
    d = os.path.join(tmp, f"w{idx}")
    os.makedirs(d, exist_ok=True)
    drv = os.path.join(tmp, "drv.c")
    eb, row_b = build(a.base, pat, enc, [], d, "base", drv)
    en, row = build(a.new, pat, enc, [], d, "new", drv)
    if not eb or not en:
        return (pat, enc, "BUILD-FAIL", f"{row_b} / {row}", 0, 0, [])
    res, cells, matches, notes = "same", 0, 0, []
    for size, mode in ((4096, "all"), (300_000, "find"), (300_000, "sample"), (1 << 20, "find"), (1 << 20, "sample")):
        for dens in (0.05, 0.3, 0.8):
            subj = os.path.join(d, f"s{size}_{dens}.bin")
            if not os.path.exists(subj):
                open(subj, "wb").write(gen(tm, tn, enc, size, dens, idx * 1000 + int(dens * 100) + size))
            ob, on = run(eb, subj, mode, idx), run(en, subj, mode, idx)
            if ob != on:
                res = "DIFF"; notes.append(f"{size}/{mode}/{dens}")
            cells += ob.count(b"\n"); matches += ob.count(b":1:")
    # the budget arm: base answered => new answers identically
    for extra in BUDGETS:
        bb, _ = build(a.base, pat, enc, extra, d, "bb", drv)
        bn, _ = build(a.new, pat, enc, extra, d, "bn", drv)
        if not bb or not bn:
            notes.append(f"budget {extra[0]}: build failed"); res = "BUILD-FAIL"; continue
        for dens in (0.05, 0.3, 0.8):
            subj = os.path.join(d, f"s300000_{dens}.bin")
            lb = run(bb, subj, "sample", idx + 7).splitlines()
            ln = run(bn, subj, "sample", idx + 7).splitlines()
            up = 0
            for x, y in zip(lb, ln):
                rb, rn = int(x.split(b":")[1]), int(y.split(b":")[1])
                if rb in (0, 1):
                    if x != y:
                        res = "BUDGET-VIOLATION"; notes.append(f"{extra[0]} dens {dens}: {x!r} -> {y!r}")
                elif rn in (0, 1):
                    up += 1
            if len(lb) != len(ln):
                res = "BUDGET-VIOLATION"; notes.append(f"{extra[0]}: transcript lengths differ")
            if up: notes.append(f"{extra[0]} dens {dens}: {up} give-up(s) became answers")
    return (pat, enc, res, row, cells, matches, notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("new"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "drv.c"), "w").write(DRIVER)
        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            futs = [ex.submit(one, a, i, w, tmp) for i, w in enumerate(WITNESSES)]
            for fu in futs:
                try: rows.append(fu.result())
                except Exception as x: rows.append(("?", "?", "ERROR:" + type(x).__name__ + str(x)[:100], "-", 0, 0, []))
    bad = [r for r in rows if r[2] != "same"]
    with open(a.out, "w", encoding="utf-8") as o:
        o.write(f"witnesses: {len(rows)}  violations: {len(bad)}\n")
        o.write("| pattern | enc | row | verdict | calls compared | matches | notes |\n|---|---|---|---|---:|---:|---|\n")
        for pat, enc, res, row, cells, matches, notes in rows:
            o.write(f"| `{pat}` | {enc} | {row} | {res} | {cells} | {matches} | {'; '.join(notes)} |\n")
    print(open(a.out).read())
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
