#!/usr/bin/env python3
"""generate.py -- this SOURCE's derivation step (`third_party/README.md`'s
general rule: a data source compiles to generated tables, generator beside
the data): the shipped `weblog` analysis, `src/findings/weblog.rxt`
([FINDINGS] B5; docs/design/findings/design.md §8.1, §13 B5).

WHAT IT READS   `apache_logs.txt`, beside this file (see PROVENANCE.md: the
                first 1,000,000 bytes of elastic/examples' "Common Data
                Formats/apache_logs/apache_logs" at the pinned commit
                `bc53b584c0f9f574d4373193334bf03541a54936`, Apache-2.0).
WHAT IT WRITES  `src/findings/weblog.rxt`: a header comment, then EXACTLY
                what the analyzer (`scripts/pcrec_analyze.py`, R27b: a
                generator never counts itself) prints for that file.

    python3 third_party/elastic-examples-apache-logs-bc53b584/generate.py          # writes it
    python3 third_party/elastic-examples-apache-logs-bc53b584/generate.py --check  # verifies

`make gen-tables` runs the bare form and then `make gen-findings`, which
re-embeds the store (`src/core/findings_{store,table}.inc`) from the new
text; `make test-findings` runs `--check` for every shipped bundle whose
provenance names a `third_party/` source (tests/findings/ §12), so an edit
to the sample, the analyzer or the invocation below goes red until the
bundle is regenerated.

ARGUMENTS: `--scan freq,cpfreq` is B5's scope (R5): the analyzer splits
their declarations so `freq` serves `byte` and `cpfreq` serves `utf8`
(design §10.2's table, [r2 M-B1]) -- the `utf8` byte-rate this bundle
exists to supply. `bigram` joins at B4, with its reader.
`--source` is this directory's name, which is how tests/findings/ §12 finds
the generator from the bundle; `--url`/`--ref`/`--license` mirror
PROVENANCE.md's table exactly.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANALYZE = ROOT / "scripts" / "pcrec_analyze.py"
CORPUS = HERE / "apache_logs.txt"
OUT = ROOT / "src" / "findings" / "weblog.rxt"

RETRIEVED = "2026-09-27"
PINNED_COMMIT = "bc53b584c0f9f574d4373193334bf03541a54936"
SOURCE_URL = (
    "https://github.com/elastic/examples/blob/"
    + PINNED_COMMIT
    + "/Common%20Data%20Formats/apache_logs/apache_logs"
)

HEADER = """\
# src/findings/weblog.rxt -- THE SHIPPED `weblog` ANALYSIS ([FINDINGS] B5).
# GENERATED -- never edit by hand. Written by
# third_party/elastic-examples-apache-logs-bc53b584/generate.py, which runs
# scripts/pcrec_analyze.py over that directory's apache_logs.txt (Apache
# combined-format web-server request lines; PROVENANCE.md there). Regenerate
# with `make gen-tables`; `make test-findings` checks it is not stale.
#
# `freq` answers byte-rate under -e byte and `cpfreq` under -e utf8
# (encode-utf8): name it with `--analysis weblog` or a config's
# `analysis weblog` (docs/spec/findings.md).
"""


def run_analyzer() -> bytes:
    if not CORPUS.exists():
        print(f"MISSING: {CORPUS}", file=sys.stderr)
        raise SystemExit(1)
    args = [
        sys.executable, str(ANALYZE),
        "--name", "weblog",
        "--retrieved", RETRIEVED,
        "--scan", "freq,cpfreq",
        "--source", HERE.name,
        "--url", SOURCE_URL,
        "--ref", PINNED_COMMIT,
        "--license", "Apache-2.0",
        str(CORPUS),
    ]
    cp = subprocess.run(args, capture_output=True)
    if cp.returncode != 0:
        sys.stderr.write(cp.stderr.decode("utf-8", "replace"))
        raise SystemExit(f"analyzer failed, rc={cp.returncode}")
    return cp.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    data = HEADER.encode("ascii") + run_analyzer()

    if args.check:
        if not OUT.exists():
            print(f"MISSING: {OUT}", file=sys.stderr)
            return 1
        if OUT.read_bytes() != data:
            print(f"STALE: {OUT} does not match a fresh analyzer run over "
                  f"{CORPUS.name} -- regenerate with `make gen-tables`",
                  file=sys.stderr)
            return 1
        print(f"OK: {OUT} matches a fresh analyzer run ({len(data)} bytes)")
        return 0

    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
