#!/usr/bin/env python3
"""rewtwin timing, layout-controlled: one binary per (row, mode, arm, pad).

usage: timing_pad.py TODAY_PCREC TWIN_PCREC SUBJ_DIR WORK_DIR OUT_TSV [CPU]

Why: timing.py links four artifacts into one binary, and its second copy of
today's identical text read up to x1.30 off the first, so at the 2-5 ns scale
a single-binary comparison is a layout reading. Here each arm is ALONE in its
binary, preceded by `.skip PAD` bytes (PADS, the K87 control:
docs/dev/optloop/k87twin_align.sh) and built -O2 -falign-functions=64. Arms:
today (rev-end walk), twin (rev-end-width), norevend (-fno-rev-end, the
pre-REVEND end window), twininl (the twin with `__attribute__((flatten))` on
rx_search, a hand edit: the verify-at call to rx_match inlined). Regimes: `short` (the bench's 27 litrun short
subjects, one rx_search(s, n, 0) each), `long` (the 27 ~64 KiB throughput
subjects). Launch order: ROUNDS x PADS x arms rotated, all pinned with
taskset. Each launch reports the median of BATCHES timed passes (ns per
call). Output: one row per launch; summarize.py reduces it.
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PATS = {
    "alt-foo-tails": "foo.x|foobar|foo.", "lit-l2": "ab", "lit-l4": "abcd",
    "lit-l8": "abcdefgh", "lit-l31": "abcdefghijklmnopqrstuvwxyzABCDE",
    "lit-l40": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN",
    "aws": r"\b((?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16})\b",
    "ghp": r"\b(github_pat_[0-9a-zA-Z_]{82})\b",
    "ctrl-abc-dollar": "abc$",
}
ROWS = [(k + "/whole", "(?:%s)\\z" % p) for k, p in PATS.items()]
ROWS.append(("ctrl-abc-dollar/plain", "abc$"))
PADS = [0, 16, 32, 48, 64, 80, 96, 112]
ROUNDS, BATCHES = 3, 9
REPS = {"short": 20000, "long": 400}
ARMS = ["today", "twin", "norevend", "twininl"]

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "rx.h"
static unsigned char *S[64]; static size_t N[64]; static int NS;
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
static int cmp(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return x < y ? -1 : x > y; }
int main(int argc, char **argv)
{
    int reps = atoi(argv[1]), batches = atoi(argv[2]);
    for (int i = 3; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); fseek(f, 0, SEEK_END); N[NS] = ftell(f); rewind(f);
        S[NS] = malloc(N[NS] + 1); if (fread(S[NS], 1, N[NS], f) != N[NS]) return 2; fclose(f); NS++;
    }
    double t[64]; volatile long sink = 0; ptrdiff_t caps[64][2];
    for (int r = 0; r < reps / 4 + 1; r++) for (int i = 0; i < NS; i++) sink += rx_search(S[i], N[i], 0, caps);
    for (int b = 0; b < batches; b++) {
        double t0 = now();
        for (int r = 0; r < reps; r++) for (int i = 0; i < NS; i++) sink += rx_search(S[i], N[i], 0, caps);
        t[b] = (now() - t0) / ((double)reps * NS);
    }
    qsort(t, batches, sizeof(double), cmp);
    printf("%.4f\n", t[batches / 2]);
    return (int)(sink & 0);
}
'''


def main():
    today, twin, subj, work, out = sys.argv[1:6]
    cpu = sys.argv[6] if len(sys.argv) > 6 else "3"
    os.makedirs(work, exist_ok=True)
    regimes = {r: sorted(os.path.join(subj, d, f) for f in os.listdir(os.path.join(subj, d)))
               for r, d in (("short", "subjects"), ("long", "throughput"))}
    drv = os.path.join(work, "drv.c")
    open(drv, "w").write(DRIVER)
    jobs = []
    for name, pat in ROWS:
        for mode in ("caps", "nocaps"):
            for arm in ARMS:
                d = os.path.join(work, (name + "_" + mode).replace("/", "_"), arm)
                os.makedirs(d, exist_ok=True)
                comp = twin if arm.startswith("twin") else today
                cmd = [comp, "--features", "all", "-p", "rx"] + (["--no-captures"] if mode == "nocaps" else []) + \
                      (["-fno-rev-end"] if arm == "norevend" else []) + ["-o", os.path.join(d, "art.c"), "--pattern", pat]
                subprocess.run(cmd, check=True, timeout=120)
                src = open(os.path.join(d, "art.c")).read()
                if arm == "twininl":   # hand edit: the verify-at call inlined (gcc `flatten`)
                    assert src.count("\nint rx_search(") == 1
                    src = src.replace("\nint rx_search(", "\n__attribute__((flatten)) int rx_search(")
                for p in PADS:
                    pd = os.path.join(d, "p%d" % p)
                    os.makedirs(pd, exist_ok=True)
                    open(os.path.join(pd, "art.c"), "w").write('__asm__(".text\\n.skip %d,0x90\\n");\n' % p + src)
                    os.system("cp %s %s" % (os.path.join(d, "art.h"), os.path.join(pd, "art.h")))
                    os.system("cp %s %s" % (os.path.join(d, "art.h"), os.path.join(pd, "rx.h")))
                    jobs.append(["gcc", "-O2", "-w", "-falign-functions=64", "-I", pd, "-o", os.path.join(pd, "run"),
                                 drv, os.path.join(pd, "art.c")])
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(lambda c: subprocess.run(c, capture_output=True, timeout=300), jobs):
            if r.returncode:
                sys.exit("build failed: %s" % r.stderr[:300])
    with open(out, "w") as o:
        o.write("row\tmode\tregime\tarm\tpad\tround\tns\tload1\n")
        for name, _ in ROWS:
            for mode in ("caps", "nocaps"):
                base = os.path.join(work, (name + "_" + mode).replace("/", "_"))
                for reg, files in regimes.items():
                    for rnd in range(ROUNDS):
                        for pi, p in enumerate(PADS):
                            for k in range(len(ARMS)):
                                arm = ARMS[(rnd + pi + k) % len(ARMS)]
                                l1 = open("/proc/loadavg").read().split()[0]
                                r = subprocess.run(["taskset", "-c", cpu, os.path.join(base, arm, "p%d" % p, "run"),
                                                    str(REPS[reg]), str(BATCHES)] + files,
                                                   capture_output=True, text=True, timeout=600)
                                o.write("\t".join([name, mode, reg, arm, str(p), str(rnd), r.stdout.strip(), l1]) + "\n")
                    o.flush()
                    print(name, mode, reg, "done", flush=True)


main()
