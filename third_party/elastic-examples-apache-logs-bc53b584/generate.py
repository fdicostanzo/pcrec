#!/usr/bin/env python3
"""generate.py -- this SOURCE's derivation step (`third_party/README.md`'s
general rule: a data source compiles to generated tables, generator beside
the data).

**SOURCING-HALF STUB.** This lane (`findb5src`, `[FINDINGS]` B5's sourcing
half) is scoped to nothing under `src/`, `cli/`, `tests/`. It runs the real
analyzer over the real vendored exemplar and writes the result to
`generated_preview.rxt`, BESIDE THIS FILE -- a SCRATCH CHECK proving the
pipeline works end to end, committed here for review, and DELIBERATELY NOT
`src/findings/weblog.rxt`. Wiring this generator to write the shipped file,
adding `--check` against it, and adding the derived file to the Makefile's
`GEN_TABLES` list (`third_party/CLAUDE.md`'s "Adding a source" step 4,
`[r2 A-6]`) is `[FINDINGS]` B5's BUILD half, a later lane.

WHAT IT READS   `apache_logs.txt`, beside this file (see PROVENANCE.md: the
                first 1,000,000 bytes of elastic/examples' "Common Data
                Formats/apache_logs/apache_logs" at the pinned commit
                `bc53b584c0f9f574d4373193334bf03541a54936`, Apache-2.0).
WHAT IT WRITES  `generated_preview.rxt`, beside this file (SCRATCH; see above).

    python3 third_party/elastic-examples-apache-logs-bc53b584/generate.py          # writes it
    python3 third_party/elastic-examples-apache-logs-bc53b584/generate.py --check  # verifies

NAME/ANALYZER ARGUMENTS: `--name weblog` matches design.md's own naming
(`src/findings/{log,weblog}.rxt`, §13 B5). `--scan freq,cpfreq` matches the
B5 row's stated scope (bigram is B4/B6 territory, already landed
separately). `--source`/`--url`/`--ref`/`--license` mirror PROVENANCE.md's
own table exactly, so the analyzer's own `provenance` block and this
directory's provenance record cannot drift apart.
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
OUT = HERE / "generated_preview.rxt"

RETRIEVED = "2026-09-27"
PINNED_COMMIT = "bc53b584c0f9f574d4373193334bf03541a54936"
SOURCE_URL = (
    "https://github.com/elastic/examples/blob/"
    + PINNED_COMMIT
    + "/Common%20Data%20Formats/apache_logs/apache_logs"
)


def run_analyzer() -> bytes:
    if not CORPUS.exists():
        print(f"MISSING: {CORPUS}", file=sys.stderr)
        raise SystemExit(1)
    args = [
        sys.executable, str(ANALYZE),
        "--name", "weblog",
        "--retrieved", RETRIEVED,
        "--scan", "freq,cpfreq",
        "--source", "elastic-examples-apache-logs-bc53b584",
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

    header = (
        "# " + "=" * 74 + "\n"
        "# generated_preview.rxt -- [FINDINGS] B5 SOURCING-HALF SCRATCH CHECK.\n"
        "# NOT src/findings/weblog.rxt. Produced by\n"
        "# third_party/elastic-examples-apache-logs-bc53b584/generate.py running\n"
        "# scripts/pcrec_analyze.py over the vendored apache_logs.txt exemplar\n"
        "# (see PROVENANCE.md). Proves the analyzer pipeline runs end to end on\n"
        "# this source; the build half retargets this generator to write the\n"
        "# real src/findings/weblog.rxt (which `include <log>`, per design.md\n"
        "# §13 B5 / tests/rxtsource/fixtures/analysis_bundle_accept.rxtin) and\n"
        "# wires it into GEN_TABLES.\n"
        "# " + "=" * 74 + "\n"
    ).encode("utf-8")

    body = run_analyzer()
    data = header + body

    if args.check:
        if not OUT.exists():
            print(f"MISSING: {OUT}", file=sys.stderr)
            return 1
        if OUT.read_bytes() != data:
            print(f"STALE: {OUT} does not match a fresh analyzer run", file=sys.stderr)
            return 1
        print(f"OK: {OUT} matches a fresh analyzer run ({len(data)} bytes)")
        return 0

    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
