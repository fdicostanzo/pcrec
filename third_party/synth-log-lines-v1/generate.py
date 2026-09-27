#!/usr/bin/env python3
"""generate.py -- this SOURCE's derivation step (`third_party/README.md`'s
general rule: a data source compiles to generated tables, generator beside
the data).

**SOURCING-HALF STUB.** This lane (`findb5src`, `[FINDINGS]` B5's sourcing
half) is scoped to nothing under `src/`, `cli/`, `tests/`. It runs the real
analyzer over the real (here, synthesized) exemplar and writes the result to
`generated_preview.rxt`, BESIDE THIS FILE -- a SCRATCH CHECK proving the
pipeline works end to end, committed here for review, and DELIBERATELY NOT
`src/findings/log.rxt`. Wiring this generator to write the shipped file,
adding `--check` against it, and adding the derived file to the Makefile's
`GEN_TABLES` list (`third_party/CLAUDE.md`'s "Adding a source" step 4,
`[r2 A-6]`) is `[FINDINGS]` B5's BUILD half, a later lane.

WHAT IT READS   `synthetic_log_lines.txt`, beside this file (itself produced,
                deterministically, by `gen_corpus.py` -- see that file's own
                header for why this class is synthesized rather than vendored:
                D123-8 item 6, [r2 A-4]).
WHAT IT WRITES  `generated_preview.rxt`, beside this file (SCRATCH; see above).

    python3 third_party/synth-log-lines-v1/generate.py          # writes it
    python3 third_party/synth-log-lines-v1/generate.py --check  # verifies

This is the SAME two-mode contract every `third_party/*/generate.py` offers
(`third_party/README.md` item 3), applied to a preview output rather than a
shipped one: `--check` regenerates in memory and fails if the committed
preview has drifted, so an edit to the corpus or the analyzer invocation
below cannot silently go stale even before the build half retargets this
script.

NAME/ANALYZER ARGUMENTS: `--name log` matches design.md's own naming
(`src/findings/{log,weblog}.rxt`, §13 B5; the accept fixture
`tests/rxtsource/fixtures/analysis_bundle_accept.rxtin` already shows
`weblog`'s `include <log>`, so `log` is the name the build half must use for
the two bundles to compose as designed). `--scan freq,cpfreq` matches the B5
row's stated scope (bigram is B4/B6 territory, already landed separately).
`--source synth-log-lines-v1` and no `--url`/`--ref` (there is none -- this
is SYNTHESIZED, not fetched); `--license` names the repository's own MIT
licence, since the data originates here.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANALYZE = ROOT / "scripts" / "pcrec_analyze.py"
CORPUS = HERE / "synthetic_log_lines.txt"
OUT = HERE / "generated_preview.rxt"

RETRIEVED = "2026-09-27"  # the date this lane generated the corpus (R27c: no
                          # clock read at analysis time; this is the fixed
                          # date recorded, not derived from anything live)


def run_analyzer() -> bytes:
    if not CORPUS.exists():
        print(f"MISSING: {CORPUS} -- run gen_corpus.py first", file=sys.stderr)
        raise SystemExit(1)
    args = [
        sys.executable, str(ANALYZE),
        "--name", "log",
        "--retrieved", RETRIEVED,
        "--scan", "freq,cpfreq",
        "--source", "synth-log-lines-v1",
        "--license", "MIT (this repository; the exemplar is SYNTHESIZED, not vendored -- see PROVENANCE.md)",
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
        "# NOT src/findings/log.rxt. Produced by third_party/synth-log-lines-v1/\n"
        "# generate.py running scripts/pcrec_analyze.py over the SYNTHESIZED\n"
        "# exemplar synthetic_log_lines.txt (fidelity synthesized, D123-8 item 6;\n"
        "# see PROVENANCE.md and gen_corpus.py). Proves the analyzer pipeline runs\n"
        "# end to end on this source; the build half retargets this generator to\n"
        "# write the real src/findings/log.rxt and wires it into GEN_TABLES.\n"
        "# " + "=" * 74 + "\n"
    ).encode("ascii")

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
