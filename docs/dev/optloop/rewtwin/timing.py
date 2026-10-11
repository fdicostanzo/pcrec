#!/usr/bin/env python3
"""rewtwin timing: today (rev-end walk) vs the rev-end-width TWIN vs
-fno-rev-end (the pre-REVEND end window), plus a second copy of today as the
layout floor (same text, different address).

usage: timing.py TODAY_PCREC TWIN_PCREC SUBJ_DIR WORK_DIR OUT_TSV [CPU]

One binary per (pattern, mode) links the four artifacts. Regimes: `short`
(the bench's 27 litrun short subjects, one rx_search(s, n, 0) per subject, the
whole-subject form's call), `long` (the 27 ~64 KiB throughput subjects, one
call each). Per batch the four arms run in a rotated order, each timing REPS
passes over the regime's subject set; the reported figure is the median over
BATCHES of ns per call. Pinned with taskset to CPU (default 3). load1 is read
before and after each binary.
"""
import os, subprocess, sys

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
BATCHES, REPS = 31, {"short": 20000, "long": 400}

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "a0.c"
#include "a1.c"
#include "a2.c"
#include "a3.c"
typedef int (*sfn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
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
    sfn fn[4] = { a0_search, a1_search, a2_search, a3_search };
    static double t[4][1000];
    volatile long sink = 0;
    ptrdiff_t caps[64][2];
    for (int w = 0; w < 4; w++) for (int r = 0; r < reps / 10 + 1; r++) for (int i = 0; i < NS; i++) sink += fn[w](S[i], N[i], 0, caps);
    for (int b = 0; b < batches; b++)
        for (int k = 0; k < 4; k++) {
            int w = (b + k) % 4;
            double t0 = now();
            for (int r = 0; r < reps; r++) for (int i = 0; i < NS; i++) sink += fn[w](S[i], N[i], 0, caps);
            t[w][b] = (now() - t0) / ((double)reps * NS);
        }
    for (int w = 0; w < 4; w++) {
        qsort(t[w], batches, sizeof(double), cmp);
        printf("%d\t%.3f\t%.3f\t%.3f\n", w, t[w][batches / 2], t[w][batches / 4], t[w][3 * batches / 4]);
    }
    return (int)(sink & 0);
}
'''
ARMS = ["today", "today2", "twin", "norevend"]


def load1():
    return open("/proc/loadavg").read().split()[0]


def main():
    today, twin, subj, work, out = sys.argv[1:6]
    cpu = sys.argv[6] if len(sys.argv) > 6 else "3"
    os.makedirs(work, exist_ok=True)
    regimes = {
        "short": sorted(os.path.join(subj, "subjects", f) for f in os.listdir(os.path.join(subj, "subjects"))),
        "long": sorted(os.path.join(subj, "throughput", f) for f in os.listdir(os.path.join(subj, "throughput"))),
    }
    with open(out, "w") as o:
        o.write("row\tmode\tregime\tarm\tmedian_ns\tq1_ns\tq3_ns\tload1_before\tload1_after\n")
        for name, pat in ROWS:
            for mode in ("caps", "nocaps"):
                wd = os.path.join(work, (name + "_" + mode).replace("/", "_"))
                os.makedirs(wd, exist_ok=True)
                for tag, comp, extra in (("a0", today, []), ("a1", today, []), ("a2", twin, []),
                                         ("a3", today, ["-fno-rev-end"])):
                    cmd = [comp, "--features", "all", "-p", tag] + (["--no-captures"] if mode == "nocaps" else []) + \
                          extra + ["-o", os.path.join(wd, tag + ".c"), "--pattern", pat]
                    subprocess.run(cmd, check=True, timeout=120)
                open(os.path.join(wd, "drv.c"), "w").write(DRIVER)
                subprocess.run(["gcc", "-O2", "-w", "-I", wd, "-o", os.path.join(wd, "drv"),
                                os.path.join(wd, "drv.c")], check=True, timeout=300)
                for reg, files in regimes.items():
                    lb = load1()
                    r = subprocess.run(["taskset", "-c", cpu, os.path.join(wd, "drv"), str(REPS[reg]),
                                        str(BATCHES)] + files, capture_output=True, text=True, timeout=1200)
                    la = load1()
                    for line in r.stdout.split("\n"):
                        if not line.strip():
                            continue
                        w, med, q1, q3 = line.split("\t")
                        o.write("\t".join([name, mode, reg, ARMS[int(w)], med, q1, q3, lb, la]) + "\n")
                    o.flush()
                    print(name, mode, reg, "done", flush=True)


main()
