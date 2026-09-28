#!/usr/bin/env python3
"""tests/findings/run_analyzer_pinned.py -- the [FINDINGS] B6 GOLDEN-OUTPUT
REGRESSION CHECK (design.md §11.8, "python ≡ C (implement-then-replace)").

What this replaces: `run_analyzer_agree.py` proved `build/pcrec-analyze`
(design.md §10.1's C end state) byte-identical to `scripts/pcrec_analyze.py`
(the deleted B3 prototype) over the in-tree fixtures, the two real shipped
corpora and 800+ seeded-random invocations including invalid UTF-8. That
proof cannot be RE-RUN once the prototype is gone -- there is nothing left
to compare against. §11.8's own text anticipates this ("decide with the
design what it becomes, e.g. a pinned-output check"): this file freezes
`run_analyzer_agree.py`'s own population as COMMITTED GOLDEN FILES under
`tests/findings/golden/` (generated once, at the commit that deleted the
prototype, from the agreement-proven binary) and re-diffs the current
`build/pcrec-analyze` against them on every run. It answers a narrower
question than the agreement proof did -- "has the analyzer's output
drifted from its OWN once-verified shape", never "does it match python"
-- which is what implement-then-replace leaves for a standing check to
ask. See docs/dev/lanes/findb6_report.md.

Usage:
    python3 tests/findings/run_analyzer_pinned.py             # check (make test-findings)
    python3 tests/findings/run_analyzer_pinned.py --write      # regenerate the golden files
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parents[2]
ANALYZE = ROOT / "build" / "pcrec-analyze"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN = Path(__file__).resolve().parent / "golden"

# (golden id, argv after the program name). Every fixture x every --scan
# combination the acceptance suite (run_analyzer_tests.py) exercises, plus
# one shard/merge pair, one --fidelity/--adaptation case and R26's two
# outcomes -- the same population run_analyzer_agree.py proved against
# python, frozen here as the standing regression population.
CASES: List[tuple] = [
    ("basic_freq_bigram", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,bigram",
                            str(FIXTURES / "basic.txt")]),
    ("basic_freq_cpfreq", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,cpfreq",
                            str(FIXTURES / "basic.txt")]),
    ("ascii_only_freq_cpfreq", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,cpfreq",
                                 str(FIXTURES / "ascii_only.txt")]),
    ("utf8_mixed_all", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,cpfreq,bigram",
                         str(FIXTURES / "utf8_mixed.txt")]),
    ("invalid_utf8_freq", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,bigram",
                            str(FIXTURES / "invalid_utf8.bin")]),
    ("shard1_first_byte_freq", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq",
                                 "--shard", "1/4", str(FIXTURES / "shard1_first_byte.bin")]),
    ("cpfreq_seam_shard3of5", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "cpfreq",
                                "--shard", "3/5", str(FIXTURES / "cpfreq_seam.txt")]),
    ("fidelity_adaptation", ["--name", "pin", "--retrieved", "2026-09-28", "--scan", "freq,cpfreq",
                              "--fidelity", "synthesized", "--adaptation", "pinned regression case",
                              str(FIXTURES / "basic.txt")]),
]

_pass = 0
_fail = 0


def ok(msg: str) -> None:
    global _pass
    _pass += 1
    print(f"PASS: {msg}")


def bad(msg: str) -> None:
    global _fail
    _fail += 1
    print(f"FAIL: {msg}", file=sys.stderr)


def run(args: Sequence[str]) -> bytes:
    cp = subprocess.run([str(ANALYZE), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode != 0:
        raise RuntimeError(f"pcrec-analyze {args} failed rc={cp.returncode}: {cp.stderr.decode(errors='replace')}")
    return cp.stdout


def write_golden() -> int:
    GOLDEN.mkdir(exist_ok=True)
    for name, args in CASES:
        out = run(args)
        (GOLDEN / f"{name}.rxt").write_bytes(out)
        print(f"wrote {GOLDEN / f'{name}.rxt'} ({len(out)} bytes)")
    return 0


def check_pinned() -> None:
    for name, args in CASES:
        golden_path = GOLDEN / f"{name}.rxt"
        if not golden_path.exists():
            bad(f"{name}: no golden file at {golden_path} -- run --write first")
            continue
        want = golden_path.read_bytes()
        got = run(args)
        if got == want:
            ok(f"{name}: matches its golden file ({len(got)} bytes)")
        else:
            bad(f"{name}: DRIFTED from its golden file (was {len(want)} bytes, now {len(got)})")


def check_r26() -> None:
    f = FIXTURES / "invalid_utf8.bin"
    cp = subprocess.run([str(ANALYZE), "--name", "r26", "--retrieved", "d", "--scan", "cpfreq", str(f)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode != 0 and b"R26" in cp.stderr:
        ok("R26: --scan cpfreq on invalid UTF-8 is still a hard error")
    else:
        bad(f"R26: --scan cpfreq on invalid UTF-8 did not hard-error (rc={cp.returncode})")


def check_shipped_bundles() -> None:
    """The two real shipped bundles ARE golden files already -- committed by
    their own generate.py, and this is the same identity generate.py's own
    `--check` mode asserts (tests/findings/ §12). Re-asserted here too since
    it is exactly this row's own population (design.md §13 B5's `log`/
    `weblog`), at zero extra cost."""
    cases = [
        ("log", ROOT / "third_party" / "synth-log-lines-v1" / "generate.py"),
        ("weblog", ROOT / "third_party" / "elastic-examples-apache-logs-bc53b584" / "generate.py"),
    ]
    for name, gen in cases:
        if not gen.exists():
            continue
        cp = subprocess.run([sys.executable, str(gen), "--check"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cp.returncode == 0:
            ok(f"shipped bundle `{name}`: {gen.name} --check still reproduces src/findings/{name}.rxt")
        else:
            bad(f"shipped bundle `{name}`: {gen.name} --check FAILED: {cp.stderr.decode(errors='replace')}")


def main() -> int:
    if "--write" in sys.argv[1:]:
        return write_golden()

    if not ANALYZE.exists():
        print(f"build/pcrec-analyze not found at {ANALYZE} -- run `make` first", file=sys.stderr)
        return 2

    check_pinned()
    check_r26()
    check_shipped_bundles()

    print(f"checks passed: {_pass}")
    if _fail > 0:
        print(f"checks FAILED: {_fail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
