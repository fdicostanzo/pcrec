#!/usr/bin/env python3
"""[PF-KNOW] (D140) — HAND TWINS: an upper bound on what skipping the
prefilter-proven VM tests could buy, measured as find-all wall time on a
dense subject.  Two transforms over the emitted C, applied by hand to a
named artifact (explicit offsets/labels on the command line — these are
witnesses, not a mechanism):

  detall                 the whole program is implied (segprobe `det_all`):
                         the search entry reports the capture spans straight
                         off the prefilter's window and never enters the VM.
                         `--caps g:lo_off:hi_off` per group, offsets from
                         the window START (lo) and END (hi, negative).
  prefix K LABEL [sets]  the leading deterministic segment of K bytes is
                         implied: `rx_L0` becomes `scan_position += K; <the
                         segment's capture writes>; goto LABEL`.  `sets` are
                         `SLOTNAME@OFF` items written as `ctx->pos + OFF`.

Both twins are checked ANSWER-IDENTICAL to the base artifact over the
subject (every span of every match, hashed) before any clock is read, and
the timing is N alternating trials, medians reported.  Mac timing is
DIRECTIONAL (docs/dev/xarch_step0.md); state it wherever a number is cited.

Environment: PCREC CC OUT
Usage: twin.py <id> <pattern-file-or-literal:...> <subject> detall --caps g:lo:hi ...
       twin.py <id> <pattern-file-or-literal:...> <subject> prefix K LABEL [SLOT@OFF ...]
"""
import os, sys, re, subprocess, shutil, statistics

E = os.environ
PCREC, CC, OUT = E["PCREC"], E.get("CC", "gcc-16"), E["OUT"]
TRIALS = int(E.get("TRIALS", "7"))

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gen.h"
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc(n > 0 ? n : 1); if (fread(buf, 1, n, f) != (size_t)n) return 2; fclose(f);
    long iters = atol(argv[2]);
    ptrdiff_t caps[RX_NCAPS][2];
    volatile unsigned long long h = 1469598103934665603ULL; volatile long count = 0;
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        unsigned long long hh = 1469598103934665603ULL; long c = 0; size_t pos = 0;
        for (;;) {
            memset(caps, 0xff, sizeof caps);
            int r = rx_search(buf, (size_t)n, pos, caps);
            if (r <= 0) { if (r < 0) fprintf(stderr, "gave up %d\n", r); break; }
            c++;
            for (int g = 0; g < RX_NCAPS; g++) { hh = (hh ^ (unsigned long long)caps[g][0]) * 1099511628211ULL; hh = (hh ^ (unsigned long long)caps[g][1]) * 1099511628211ULL; }
            size_t e = (size_t)caps[0][1]; pos = (e > pos) ? e : pos + 1;
            if (pos > (size_t)n) break;
        }
        h = hh; count = c;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("count=%ld hash=%016llx secs=%.6f nsperbyte=%.4f\n", (long)count, (unsigned long long)h, secs, secs * 1e9 / ((double)n * iters));
    return 0;
}
'''

def transform(src, kind, args):
    if kind == "detall":
        caps = [a.split(":") for a in args if a != "--caps"]
        lines = ["        if (capture_spans) {"]
        for g, lo, hi in caps:
            lines.append("            capture_spans[%s][0] = window[0][0] + (%s); capture_spans[%s][1] = window[0][1] + (%s);" % (g, lo, g, hi))
        lines.append("        }")
        lines.append("        return 1;   /* [PF-KNOW twin] det_all: the window IS the answer */")
        anchor = "        attempt_position = (size_t)window[0][0];\n"
        assert src.count(anchor) >= 1
        return src.replace(anchor, anchor + "\n".join(lines) + "\n", 1)
    if kind == "prefix":
        k, label = args[0], args[1]
        sets = "".join("    RX_SET(%s, (ptrdiff_t)(ctx->pos + %s));\n" % tuple(s.split("@")) for s in args[2:])
        anchor = "rx_L0: __attribute__((unused));\n"
        assert anchor in src
        ins = ("    scan_position += %s;   /* [PF-KNOW twin] the proven leading segment */\n%s    goto %s;\n" % (k, sets, label))
        return src.replace(anchor, anchor + ins, 1)
    sys.exit("unknown transform " + kind)

def build(work, name, csrc):
    exe = os.path.join(work, name)
    r = subprocess.run([CC, "-O2", "-std=gnu11", "-w", "-I" + work, "-o", exe, csrc, os.path.join(work, "driver.c")],
                       capture_output=True, timeout=600)
    if r.returncode != 0: sys.exit("cc failed for %s: %s" % (name, r.stderr.decode()[:400]))
    return exe

def run(exe, subject, iters):
    r = subprocess.run([exe, subject, str(iters)], capture_output=True, timeout=600)
    m = re.search(r"count=(\d+) hash=(\w+) secs=([\d.]+) nsperbyte=([\d.]+)", r.stdout.decode())
    return int(m.group(1)), m.group(2), float(m.group(3)), float(m.group(4))

def main():
    ident, patarg, subject, kind = sys.argv[1:5]; args = sys.argv[5:]
    pat = patarg[len("literal:"):].encode("latin-1") if patarg.startswith("literal:") else open(patarg, "rb").read().rstrip(b"\n")
    work = os.path.join(OUT, "twin_" + re.sub(r"[^A-Za-z0-9_.-]", "_", ident))
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    gen = os.path.join(work, "gen.c")
    r = subprocess.run([PCREC, "--features", "all", "-p", "rx", "-o", gen, "--pattern", pat], capture_output=True, timeout=120)
    if r.returncode != 0: sys.exit("pcrec refused: " + r.stderr.decode()[:200])
    open(os.path.join(work, "driver.c"), "w").write(DRIVER)
    src = open(gen, encoding="latin-1").read()
    twin = os.path.join(work, "twin.c"); open(twin, "w", encoding="latin-1").write(transform(src, kind, args))
    base_exe = build(work, "base", gen); twin_exe = build(work, "twin", twin)
    # answer identity first
    cb, hb, _s, _n = run(base_exe, subject, 1); ct, ht, _s, _n = run(twin_exe, subject, 1)
    if (cb, hb) != (ct, ht):
        print("%s\tANSWER MISMATCH base count=%d hash=%s twin count=%d hash=%s" % (ident, cb, hb, ct, ht)); return
    # calibrate iterations to ~0.3 s per trial
    _c, _h, s1, _n = run(base_exe, subject, 1)
    iters = max(1, int(0.3 / max(s1, 1e-4)))
    bt, tt = [], []
    for i in range(TRIALS):
        bt.append(run(base_exe, subject, iters)[3]); tt.append(run(twin_exe, subject, iters)[3])
    mb, mt = statistics.median(bt), statistics.median(tt)
    print("%s\t%s\tmatches=%d\titers=%d\tbase_ns/byte=%.4f\ttwin_ns/byte=%.4f\tratio(base/twin)=%.3f\tbase_spread=%.4f..%.4f\ttwin_spread=%.4f..%.4f\tanswers=identical(hash %s)" % (
        ident, kind, cb, iters, mb, mt, mb / mt if mt else 0, min(bt), max(bt), min(tt), max(tt), hb))

if __name__ == "__main__":
    main()
