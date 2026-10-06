#!/usr/bin/env python3
"""gen_selection.py -- generate the artifacts of docs/dev/optloop/artrev/selection.tsv
with ONE pcrec binary at ONE pin (`artrev.py gen` per row).

  gen_selection.py --pcrec BIN --pin SHA [--ids A01,A07 | --pilot | --all] [--bench /path/to/pcrec-bench] [--force]

Pattern text is read from <bench>/bench/<set>/patterns/<pattern>.rx (read-only);
the pcrec flags are the row's `pcrec_flags_extra` (--features all is the harness's
default, as the bench's pcrec-auto testee has it).
"""
import argparse
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEL = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "dev", "optloop", "artrev", "selection.tsv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--bench", default="/Users/fdicostanzo/pcrec-bench")
    ap.add_argument("--selection", default=SEL)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.selection), delimiter="\t"))
    want = set(a.ids.split(",")) if a.ids else None
    rc = 0
    for r in rows:
        if want is not None and r["id"] not in want:
            continue
        if a.pilot and not r["pilot"].startswith("PILOT"):
            continue
        if want is None and not (a.pilot or a.all):
            sys.exit("choose --ids, --pilot or --all")
        pf = os.path.join(a.bench, "bench", r["bench_set"], "patterns", r["bench_pattern"] + ".rx")
        cmd = [sys.executable, os.path.join(HERE, "artrev.py"), "gen", r["name"], "--pcrec", a.pcrec, "--pin", a.pin,
               "--pattern-file", pf, "--flags=" + r["pcrec_flags_extra"]] + (["--force"] if a.force else [])
        rc |= subprocess.run(cmd).returncode
    sys.exit(rc)


main()
