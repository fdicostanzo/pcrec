#!/usr/bin/env python3
"""bench_bytes.py -- [OPT-CLSPACK] timing arm (D129 item 5, Frank: "time
it"): STEP 0 measured the shared atom table 24% faster than the bit array
at N=16 (`.text`/`.rodata` only); its Q5-revised disposition is that the
kit's inline byte tests were never timed against it either. This is that
timing, box-independent house protocol (bench.py's own: interleaved rounds,
load-gated, checksummed against an independent reference). The load gate is
`loadgate.wait_for_quiet` (lane clsgate, 2026-09-29): all N's arms are built
before any timing starts, and the gate is checked immediately before EACH
timed unit (one N's run), waiting up to `--max-load-wait` for a quiet box
rather than refusing on the first over-threshold reading -- see
loadgate.py's header for why the harness's own compiles+runs were tripping
the gate on themselves.

THE SHAPE THE OTHER TWO REGIMES DO NOT HAVE: bench.py times ONE class's
matcher at a time. [OPT-CLSPACK]'s question is about MANY class sites live
in the SAME loop -- exactly what a real matcher's inner scan loop does when
several `[...]` sites are hot -- so this harness's inner loop, every
iteration, picks a random SITE among N live classes and a random byte, and
dispatches through a per-arm site-indexed table. N in {4, 16, 32} (the plan
row's own study estimated a ~10-class crossover; this brackets it).

THREE ARMS, per D129 item 5's list:
  bitmap   TODAY's shipped shape: one 32-byte (256-bit) membership table per
            class, indexed directly by the byte (no base subtraction, no
            bound test -- a byte class site always sees a full byte, unlike
            a code-point kit section). Read straight off the classes'
            OWN membership words (`clsets.byteclasses`' hex column IS this
            table, byte for byte) -- not rebuilt through kit.FormBitmap,
            whose section-relative indexing is a code-point-kit concern that
            does not apply to a byte class's flat domain.
  kit      the kit's OWN inline test for that class, at lam=16 ("mid", the
            calibration default the byteclasses/uprops sweeps already use) --
            whichever single-section form (RANGES/CUBES/MASK64/BITMAP) the
            real sectioning DP picks for a domain this small, exactly as
            `emit.emit` would compile it into a real matcher.
  atom     [OPT-CLSPACK]'s general form, generalized from
            `studies/form_char_twins/twin_D.py`'s N=16 hand-twin (which
            parsed a base.c's OWN emitted bitmaps) to build straight from
            the classes' membership sets: ONE shared byte->atom[256] index
            (every byte's atom is the SET OF CLASSES it belongs to, over
            just these N) plus a 64-bit mask per class. Refuses loudly
            (not silently) if N distinct classes ever need > 64 atoms --
            a real finding, not a thing to paper over.

Reference: an independent bsearch per class (`emit.reference`, the study's
usual dumbest-correct-thing oracle) -- NOT the bitmap arm, even though the
bitmap arm's own table already IS the ground-truth membership word: sharing
that source between the answer and its check is exactly the blind spot
docs/dev/learnings.md §3 (K35) warns about, so the reference is built by a
structurally different route (interval bsearch, not a table lookup) from the
same population, same as bench.py's `refbs` arm.

Usage:
    python3 bench_bytes.py [--ns 4,16,32] [--rounds 11] [--regimes ...]
        [--max-load 0.5] [--out bench2_bytes.tsv]

Writes results/<out> (default `bench2_bytes.tsv`).  `--smoke` cuts the
per-round probe count down for a Mac correctness-only run (never for citing
a timing number -- Darwin timing is never citable, memory
pcrec-cross-platform-verification / this lane's own brief).
"""
import argparse
import os
import subprocess
import sys
import time

import clsets
import loadgate
import emit
import section

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")

DRIVER_TMPL = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NPROBE %(nprobe)dUL

static unsigned long long rnd_s = 88172645463325252ULL;
static unsigned long long rnd(void)
{ rnd_s ^= rnd_s << 13; rnd_s ^= rnd_s >> 7; rnd_s ^= rnd_s << 17; return rnd_s; }

static double now_s(void)
{ struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
  return t.tv_sec + 1e-9 * t.tv_nsec; }

/* Fixed probe stream (site, byte) pairs, generated ONCE and shared by every
 * arm/round -- an interleaved-arms protocol still needs the SAME subject
 * under every arm to make hits/chk comparable. */
static int probe_site[NPROBE];
static unsigned char probe_byte[NPROBE];

int main(int argc, char **argv)
{
    int rounds = argc > 1 ? atoi(argv[1]) : 11;
    for (unsigned long i = 0; i < NPROBE; i++) {
        probe_site[i] = (int)(rnd() %% N_SITES);
        probe_byte[i] = (unsigned char)(rnd() & 0xFF);
    }

    for (int r = 0; r < rounds; r++) {
        for (int a = 0; a < NARMS; a++) {
            unsigned long hits = 0, chk = 0;
            double t0 = now_s();
            for (unsigned long i = 0; i < NPROBE; i++) {
                int v = arms[a](probe_site[i], probe_byte[i]);
                hits += (unsigned long)v;
                chk += (unsigned long)v * (i + 1u);
            }
            double el = now_s() - t0;
            printf("ROUND %%d ARM %%s ns_per_call %%.4f hits %%lu chk %%lu\n",
                   r, armnames[a], 1e9 * el / (double)NPROBE, hits, chk);
            fflush(stdout);
        }
    }
    return 0;
}
"""


def atom_partition(bytesets):
    """`bytesets`: list of frozenset(byte in [0,256)), one per class.
    Returns (atom_of_byte[256], masks[len(bytesets)], n_atoms). Same
    algorithm as `form_char_twins/twin_D.py`'s `make_atom`, generalized off
    a base.c's own emitted tables to a bare list of membership sets."""
    sig_of_byte = []
    for b in range(256):
        sig_of_byte.append(tuple(i for i, s in enumerate(bytesets) if b in s))
    sigs = sorted(set(sig_of_byte), key=lambda s: (s == (),))
    sig_to_atom = {s: i for i, s in enumerate(sigs)}
    atoms = [sig_to_atom[sig_of_byte[b]] for b in range(256)]
    n_atoms = len(sigs)
    masks = [0] * len(bytesets)
    for b in range(256):
        a = atoms[b]
        for i, s in enumerate(bytesets):
            if b in s:
                masks[i] |= (1 << a)
    return atoms, masks, n_atoms


def gen(n, classes, lam, outdir):
    """classes: list of (name, iv, bits) for N live sites, `bits` a 256-bit
    int membership word (LSB = byte 0, same convention as byteclasses.tsv).
    Returns (path, armnames)."""
    bytesets = [frozenset(b for b in range(256) if (bits >> b) & 1)
                for _, _, bits in classes]

    parts = [emit.PRELUDE]

    # --- reference: independent bsearch per class, dispatched by site -----
    ref_fns = []
    for i, (name, iv, _bits) in enumerate(classes):
        fn = "ref%d" % i
        parts.append(emit.reference(fn, iv))
        ref_fns.append(fn)
    parts.append("static int ref_dispatch(int site, unsigned cp)\n{\n"
                 "    switch (site) {\n"
                 + "".join("    case %d: return %s(cp);\n" % (i, fn)
                          for i, fn in enumerate(ref_fns))
                 + "    default: return 0;\n    }\n}\n")

    # --- bitmap: TODAY's shape, straight off the classes' own membership --
    bm_tabs = []
    for i, (_name, _iv, bits) in enumerate(classes):
        t = "bm_t%d" % i
        rows = ", ".join("0x%02X" % ((bits >> (8 * j)) & 0xFF) for j in range(32))
        parts.append("static const unsigned char %s[32] = { %s };\n" % (t, rows))
        bm_tabs.append(t)
    parts.append("static const unsigned char *const bm_tabs[%d] = { %s };\n"
                 % (n, ", ".join(bm_tabs)))
    parts.append("static int bitmap_dispatch(int site, unsigned cp)\n{\n"
                 "    const unsigned char *t = bm_tabs[site];\n"
                 "    return (int)((t[cp >> 3] >> (cp & 7)) & 1u);\n}\n")

    # --- kit: the DP's own answer per class, lam fixed ---------------------
    kit_fns = []
    for i, (name, iv, _bits) in enumerate(classes):
        sc, _, _, fo = section.partition_c(iv, lam)
        fn = "kit%d" % i
        s, _ = emit.emit(fn, iv, sc, fo, static=True)
        parts.append(s)
        kit_fns.append(fn)
    parts.append("static int (*const kit_fns[%d])(unsigned) = { %s };\n"
                 % (n, ", ".join(kit_fns)))
    parts.append("static int kit_dispatch(int site, unsigned cp)\n{\n"
                 "    return kit_fns[site](cp);\n}\n")

    # --- atom: ONE shared table + a mask per class -------------------------
    atoms, masks, n_atoms = atom_partition(bytesets)
    if n_atoms > 64:
        raise SystemExit("bench_bytes: N=%d needs %d atoms (>64) -- the "
                         "shared 64-bit mask does not fit; REFUSING rather "
                         "than silently truncating" % (n, n_atoms))
    rows = ", ".join(str(v) for v in atoms)
    parts.append("static const unsigned char atom_tbl[256] = { %s };\n" % rows)
    parts.append("static const unsigned long long atom_masks[%d] = { %s };\n"
                 % (n, ", ".join("0x%016XULL" % m for m in masks)))
    parts.append("static int atom_dispatch(int site, unsigned cp)\n{\n"
                 "    return (int)((atom_masks[site] >> atom_tbl[cp]) & 1ULL);\n"
                 "}\n")

    parts.append("#define N_SITES %d\n" % n)
    parts.append("#define NARMS 4\n")
    parts.append("typedef int (*sitefn)(int, unsigned);\n")
    parts.append("static sitefn arms[NARMS] = "
                 "{ ref_dispatch, bitmap_dispatch, kit_dispatch, "
                 "atom_dispatch };\n")
    parts.append('static const char *const armnames[NARMS] = '
                 '{ "refbs", "bitmap", "kit", "atom" };\n')

    path = os.path.join(outdir, "bytes_n%d.c" % n)
    with open(path, "w") as f:
        f.write("".join(parts))
    return path, ["refbs", "bitmap", "kit", "atom"], n_atoms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="4,16,32")
    ap.add_argument("--lam", type=float, default=16.0)
    ap.add_argument("--rounds", type=int, default=11)
    ap.add_argument("--nprobe", type=int, default=1 << 20)
    ap.add_argument("--max-load", type=float, default=0.5)
    ap.add_argument("--max-load-wait", type=float, default=600.0,
                    help="bounded wait (seconds) for a quiet box before a "
                         "timed unit refuses (default 600 = 10 min)")
    ap.add_argument("--max-load-poll", type=float, default=10.0,
                    help="poll interval (seconds) while waiting for quiet")
    ap.add_argument("--out", default="bench2_bytes.tsv")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny --rounds/--nprobe, CORRECTNESS ONLY -- never "
                         "cite its timing (Darwin is never citable anyway)")
    args = ap.parse_args()

    if args.smoke:
        args.rounds = min(args.rounds, 2)
        args.nprobe = min(args.nprobe, 1 << 12)

    la0 = loadgate.wait_for_quiet(args.max_load, args.max_load_wait,
                                  args.max_load_poll, tag="bench_bytes")

    pop = clsets.byteclasses()
    ns = [int(x) for x in args.ns.split(",")]
    maxn = max(ns)
    if maxn > len(pop):
        sys.exit("bench_bytes: N=%d exceeds the %d-class byteclasses "
                 "population" % (maxn, len(pop)))

    outdir = os.path.join(HERE, "build", "bench_bytes")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out_path = os.path.join(HERE, "results", args.out)

    # byteclasses.tsv's own hex membership word, keyed by label -- read via
    # the same file verify_whole/etc use, so `bits` and `iv` never disagree.
    bits_by_name = {}
    tsv_path = os.path.join(HERE, "results", "byteclasses.tsv")
    for line in open(tsv_path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        bits_by_name[f[1]] = int(f[0], 16)

    # --- BUILD PHASE: every N's arms built BEFORE any timing starts (lane
    # clsgate, 2026-09-29 -- see loadgate.py's header). ---
    built = []
    for n in ns:
        classes = [(name, iv, bits_by_name[name])
                  for name, iv in pop[:n]]
        cpath, names, n_atoms = gen(n, classes, args.lam, outdir)
        bpath = os.path.join(outdir, "bytes_n%d" % n)
        nprobe = args.nprobe
        src = open(cpath).read() + (DRIVER_TMPL % {"nprobe": nprobe})
        open(cpath, "w").write(src)
        r = subprocess.run([CC, "-O2", "-std=gnu11", "-w", cpath,
                           "-o", bpath], capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write("BUILD FAIL n=%d: %s\n"
                             % (n, r.stderr.strip()[:400]))
            continue
        built.append((n, bpath, n_atoms))

    # --- TIMING PHASE: gate-and-wait immediately before EACH N's run. ---
    with open(out_path, "w") as out:
        out.write("# cc=%s rounds=%d nprobe=%d smoke=%s load1_at_start=%.2f "
                  "date=%s\n"
                  % (CC, args.rounds, args.nprobe, args.smoke, la0,
                     time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("n\tn_atoms\tarm\tround\tns_per_call\thits\tchk\n")
        for n, bpath, n_atoms in built:
            loadgate.wait_for_quiet(args.max_load, args.max_load_wait,
                                    args.max_load_poll,
                                    tag="bench_bytes n=%d" % n)
            r = subprocess.run([bpath, str(args.rounds)],
                               capture_output=True, text=True)
            if r.returncode:
                sys.stderr.write("RUN FAIL n=%d: %s\n" % (n, r.stderr[:400]))
                continue
            ref = {}
            for ln in r.stdout.splitlines():
                p = ln.split()
                if len(p) != 10 or p[0] != "ROUND":
                    continue
                rd, arm, ns_, hits, chk = p[1], p[3], p[5], p[7], p[9]
                key = ("bytes", rd)
                if arm == "refbs":
                    ref[key] = (hits, chk)
                elif key in ref and ref[key] != (hits, chk):
                    sys.exit("bench_bytes: ANSWER MISMATCH n=%d arm=%s "
                             "round=%s" % (n, arm, rd))
                out.write("%d\t%d\t%s\t%s\t%s\t%s\t%s\n"
                         % (n, n_atoms, arm, rd, ns_, hits, chk))
            out.flush()
    print("wrote", out_path)


if __name__ == "__main__":
    main()
