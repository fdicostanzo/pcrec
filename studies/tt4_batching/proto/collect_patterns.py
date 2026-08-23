#!/usr/bin/env python3
"""studies/tt4_batching/proto/collect_patterns.py — [TT-4.1] Stage B corpus
collection.

Extracts real `pattern <regex>` blocks from .rxt files (the harness's own
format — tests/harness/CLAUDE.md / docs/testing.md), the same way
tests/harness/run.sh's own parser maps a block to pcrec flags: `flags i`
becomes `-i`, `features LIST` becomes `--features LIST`; `perr` blocks are
skipped (they never compile). Compiles each surviving block through the
WORKTREE's own `build/pcrec` with a DISTINCT prefix per pattern (rx0001,
rx0002, ... — the emitter was designed for coexistence, TT-4's charter) and
writes gen.c/gen.h pairs into an output directory, stopping once --count
patterns have compiled successfully (a pattern that fails to compile is
skipped and does not count against --count — this script is building a
REPRESENTATIVE corpus of compilable patterns, not re-testing rejection).

This DOES NOT modify or invoke the harness — it is pcrec run directly over
patterns read out of the same .rxt files the harness reads, exactly as
[TT-4.1]'s brief requires ("run build/pcrec yourself over the patterns the
section compiles").

Records, per collected pattern, its FEATURE SET (the `features` directive
value, "" for none/default) in a manifest — Stage B's batching sweep draws
from a single feature-homogeneous bucket by default (see --require-features)
because heterogeneous feature sets are a confirmed, separate obstacle to TU
concatenation (PCREC_FEATURE_SET/PCREC_FEATURE_MODULES are unprefixed
#defines in gen.c bodies — see the memo).

Usage:
  collect_patterns.py --pcrec PATH --outdir DIR --count N [--require-features F]
      file-or-dir [file-or-dir ...]
"""
import argparse
import os
import re
import subprocess
import sys
import glob

PATTERN_RE = re.compile(r'^pattern (.*)$')
FLAGS_RE = re.compile(r'^flags\s+([a-zA-Z]+)\s*$')
FEATURES_RE = re.compile(r'^features\s+([a-zA-Z0-9,_-]+)\s*$')
PERR_RE = re.compile(r'^perr\s*$')

def find_rxt_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out.extend(sorted(glob.glob(os.path.join(p, "**", "*.rxt"), recursive=True)))
        else:
            out.append(p)
    return out

def iter_blocks(path):
    """Yield (pattern_text, flags_str, features_str, is_perr) for each block."""
    cur = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            m = PATTERN_RE.match(line)
            if m:
                if cur is not None:
                    yield cur
                cur = [m.group(1), "", "", False]
                continue
            if cur is None:
                continue
            m = FLAGS_RE.match(line)
            if m:
                cur[1] = m.group(1)
                continue
            m = FEATURES_RE.match(line)
            if m:
                cur[2] = m.group(1)
                continue
            if PERR_RE.match(line):
                cur[3] = True
                continue
            # m/n/ms/ns/g/gp lines and anything else: not needed here, skip
    if cur is not None:
        yield cur

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--require-features", default=None,
                     help="only collect blocks whose `features` directive equals this "
                          "(use '' for no-directive/default) -- keeps the batching "
                          "population feature-homogeneous")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    files = find_rxt_files(args.paths)

    manifest_path = os.path.join(args.outdir, "manifest.tsv")
    collected = 0
    seen_patterns = set()
    with open(manifest_path, "w") as manifest:
        manifest.write("prefix\tsource_file\tfeatures\tflags\tpattern\n")
        for path in files:
            if collected >= args.count:
                break
            for pat, flags, features, is_perr in iter_blocks(path):
                if collected >= args.count:
                    break
                if is_perr:
                    continue
                if args.require_features is not None and features != args.require_features:
                    continue
                dedup_key = (pat, flags, features)
                if dedup_key in seen_patterns:
                    continue
                prefix = f"rx{collected:04d}"
                argv = [args.pcrec, "-p", prefix]
                if "i" in flags:
                    argv += ["-i"]
                if features:
                    argv += ["--features", features]
                argv += ["-o", os.path.join(args.outdir, f"{prefix}.c"), "--", pat]
                r = subprocess.run(argv, capture_output=True, text=True)
                if r.returncode != 0:
                    continue  # unsupported/rejected pattern -- skip, don't count
                if not os.path.exists(os.path.join(args.outdir, f"{prefix}.h")):
                    continue
                seen_patterns.add(dedup_key)
                manifest.write(f"{prefix}\t{path}\t{features}\t{flags}\t{pat}\n")
                collected += 1

    print(f"collected {collected}/{args.count} patterns into {args.outdir} (manifest: {manifest_path})", file=sys.stderr)
    if collected < args.count:
        print(f"WARNING: only found {collected} compilable patterns matching the filter across {len(files)} files", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
