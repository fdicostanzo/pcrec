#!/usr/bin/env python3
"""tests/findings/run_analyzer_agree.py -- [FINDINGS] B6's AGREEMENT PROOF
(design.md §11.8 "python ≡ C (implement-then-replace)").

Runs `scripts/pcrec_analyze.py` (B3's prototype) and `build/pcrec-analyze`
(B6's C end state, `analyze/`) side by side over the same inputs and
asserts byte-identical stdout + matching exit codes, per §11.8's own
population: "the in-tree samples + seeded random byte strings (invalid
UTF-8 included)". This file exists ONLY while both implementations exist
-- lane findb6's own report records the order (build the C analyzer and
this harness first, prove agreement WHILE the python prototype still
exists, THEN switch the generators and delete the prototype, in separate
commits so the agreement evidence survives in history).

**When the python prototype is deleted** (the commit right after this
one proves green), this file is retired IN THE SAME CHANGE and its job
is taken over by `run_analyzer_tests.py` (already repointed at the C
binary as the standing acceptance suite for everything except this
python-comparison item) plus a NEW pinned-output check,
`run_analyzer_pinned.py` -- design.md §11.8's own suggested shape
("e.g. a pinned-output check") for what this row becomes once there is
no python left to compare against. See docs/dev/lanes/findb6_report.md.

Usage: python3 tests/findings/run_analyzer_agree.py
"""
from __future__ import annotations

import hashlib
import itertools
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
PYSCRIPT = ROOT / "scripts" / "pcrec_analyze.py"
CBIN = ROOT / "build" / "pcrec-analyze"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

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


def run_py(args: Sequence[str], stdin: Optional[bytes] = None) -> Tuple[int, bytes, bytes]:
    cp = subprocess.run([sys.executable, str(PYSCRIPT), *args], input=stdin,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.returncode, cp.stdout, cp.stderr


def run_c(args: Sequence[str], stdin: Optional[bytes] = None) -> Tuple[int, bytes, bytes]:
    cp = subprocess.run([str(CBIN), *args], input=stdin,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.returncode, cp.stdout, cp.stderr


def agree(label: str, args: Sequence[str], stdin: Optional[bytes] = None) -> bool:
    """True and a PASS line iff python and C give the same exit code and
    the same stdout. stderr text is deliberately NOT compared (D26's
    tiering, one file over: WHETHER a command errors is exact, the
    WORDING of its message is not, the same standard this house holds a
    diagnostic to)."""
    prc, pout, _ = run_py(args, stdin)
    crc, cout, _ = run_c(args, stdin)
    if prc == crc and pout == cout:
        ok(f"{label}: rc={crc}, {len(cout)} byte(s), python ≡ C")
        return True
    bad(f"{label}: DIVERGED (python rc={prc}/{len(pout)}B, C rc={crc}/{len(cout)}B)")
    return False


# ---------------------------------------------------------------------------
# 1. In-tree fixtures across every --scan combination the B3 corpus covers.
# ---------------------------------------------------------------------------

def check_fixtures() -> None:
    combos = ["freq,bigram", "freq,cpfreq", "cpfreq", "freq,cpfreq,bigram"]
    names = ["basic.txt", "ascii_only.txt", "utf8_mixed.txt", "invalid_utf8.bin",
             "shard1_first_byte.bin", "cpfreq_seam.txt"]
    for name in names:
        f = FIXTURES / name
        for scan in combos:
            agree(f"fixture {name} --scan {scan}",
                  ["--name", "agree", "--retrieved", "2026-09-28", "--scan", scan, str(f)])


# ---------------------------------------------------------------------------
# 2. Shard/merge round trip, both tools, N=1..7 -- the merged bytes from
# EACH tool must equal that tool's own whole-file scan (proven already by
# run_analyzer_tests.py) AND the two tools' whole-file scans must agree
# with each other (checked here).
# ---------------------------------------------------------------------------

def check_shard_merge() -> None:
    for name, scan in (("cpfreq_seam.txt", "freq,bigram,cpfreq"), ("utf8_mixed.txt", "freq,cpfreq,bigram")):
        f = FIXTURES / name
        agree(f"shard/merge whole-file baseline [{name}]",
              ["--name", "sm", "--retrieved", "d", "--scan", scan, str(f)])
        data = f.read_bytes()
        size = len(data)
        sha = hashlib.sha256(data).hexdigest()
        for n in (1, 2, 3, 5, 7):
            with tempfile.TemporaryDirectory() as td:
                py_parts: List[str] = []
                c_parts: List[str] = []
                for k in range(1, n + 1):
                    shard_args = ["--name", "sm", "--retrieved", "d", "--scan", scan,
                                  "--shard", f"{k}/{n}", str(f)]
                    _, pout, _ = run_py(shard_args)
                    _, cout, _ = run_c(shard_args)
                    pp = Path(td) / f"py{k}.rxt"
                    cp = Path(td) / f"c{k}.rxt"
                    pp.write_bytes(pout)
                    cp.write_bytes(cout)
                    py_parts.append(str(pp))
                    c_parts.append(str(cp))
                merge_common = ["--merge", "--name", "sm", "--bytes", str(size), "--sha256", sha]
                _, py_merged, _ = run_py(merge_common + py_parts)
                _, c_merged, _ = run_c(merge_common + c_parts)
                if py_merged == c_merged:
                    ok(f"shard/merge [{name}] N={n}: python-merged ≡ C-merged")
                else:
                    bad(f"shard/merge [{name}] N={n}: python-merged != C-merged")


# ---------------------------------------------------------------------------
# 3. --check: positive, one-byte-mutated negative, missing-source (R2-A5).
# ---------------------------------------------------------------------------

def check_check_command() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmpd = Path(td)
        src = tmpd / "sample.txt"
        src.write_bytes((FIXTURES / "basic.txt").read_bytes())

        py_bundle = tmpd / "py_bundle.rxt"
        c_bundle = tmpd / "c_bundle.rxt"
        _, pout, _ = run_py(["--name", "chk", "--retrieved", "d", "--scan", "freq,bigram", str(src)])
        _, cout, _ = run_c(["--name", "chk", "--retrieved", "d", "--scan", "freq,bigram", str(src)])
        py_bundle.write_bytes(pout)
        c_bundle.write_bytes(cout)
        if pout != cout:
            bad("--check: the bundle to check already diverged between tools")
            return

        agree("--check positive (py bundle, py tool)", ["--check", str(py_bundle), str(src)])
        agree("--check positive (c bundle, c tool)", ["--check", str(c_bundle), str(src)])

        mutated = tmpd / "mutated.txt"
        data = bytearray(src.read_bytes())
        data[0] ^= 0xFF
        mutated.write_bytes(bytes(data))
        agree("--check negative (one byte changed)", ["--check", str(py_bundle), str(mutated)])

        missing = tmpd / "does_not_exist.txt"
        agree("--check missing source ([r2 A-5])", ["--check", str(py_bundle), str(missing)])


# ---------------------------------------------------------------------------
# 4. R26 (cpfreq hard-errors on invalid UTF-8) and [B5] --fidelity/--adaptation.
# ---------------------------------------------------------------------------

def check_r26_and_fidelity() -> None:
    f = FIXTURES / "invalid_utf8.bin"
    agree("R26: --scan cpfreq on invalid UTF-8", ["--name", "r26", "--retrieved", "d", "--scan", "cpfreq", str(f)])
    agree("R26: --scan freq on the same input", ["--name", "r26", "--retrieved", "d", "--scan", "freq", str(f)])
    agree("R26: --scan freq,cpfreq on the same input",
          ["--name", "r26", "--retrieved", "d", "--scan", "freq,cpfreq", str(f)])

    agree("[B5] --fidelity/--adaptation", [
        "--name", "fi", "--retrieved", "d", "--scan", "freq,cpfreq",
        "--fidelity", "synthesized", "--adaptation", "made up for findb6",
        str(FIXTURES / "basic.txt"),
    ])


# ---------------------------------------------------------------------------
# 5. Seeded random byte strings, invalid UTF-8 included (design.md §11.8's
# own wording). One fixed seed -> reproducible across runs and boxes.
# ---------------------------------------------------------------------------

def check_seeded_random() -> None:
    rng = random.Random(20260928)
    scans = ["freq,bigram", "freq,cpfreq", "cpfreq", "freq,cpfreq,bigram"]
    n_trials = 200
    diverged = 0
    tested = 0
    with tempfile.TemporaryDirectory() as td:
        for trial in range(n_trials):
            n = rng.randint(0, 64)
            data = bytes(rng.randint(0, 255) for _ in range(n))
            p = Path(td) / f"t{trial}.bin"
            p.write_bytes(data)
            for scan in scans:
                tested += 1
                args = ["--name", "fz", "--retrieved", "d", "--scan", scan, str(p)]
                prc, pout, _ = run_py(args)
                crc, cout, _ = run_c(args)
                if prc != crc or pout != cout:
                    diverged += 1
                    bad(f"seeded random trial {trial} scan={scan} ({n} byte(s), "
                        f"{data.hex()}): python rc={prc} C rc={crc}")
    if diverged == 0:
        ok(f"seeded random ({n_trials} trial(s) x {len(scans)} scan combo(s) = "
           f"{tested} invocation(s), seed 20260928, invalid UTF-8 included): 0 divergences")


# ---------------------------------------------------------------------------
# 6. The two real shipped-corpus inputs, at generate.py's own exact flags
# (design.md §13 B5's `log`/`weblog`) -- large, real-world byte streams,
# not just small fixtures.
# ---------------------------------------------------------------------------

def check_shipped_corpora() -> None:
    log_src = ROOT / "third_party" / "synth-log-lines-v1" / "synthetic_log_lines.txt"
    weblog_src = ROOT / "third_party" / "elastic-examples-apache-logs-bc53b584" / "apache_logs.txt"
    if log_src.exists():
        agree("shipped corpus `log` (synth-log-lines-v1, generate.py's own flags)", [
            "--name", "log", "--retrieved", "2026-09-27", "--scan", "freq,cpfreq",
            "--source", "synth-log-lines-v1", "--license", "MIT",
            "--fidelity", "synthesized",
            "--adaptation", "generated by gen_corpus.py (SEED 20260927) in the structural "
                            "shape of a Hadoop DataNode log; no real log text is copied",
            str(log_src),
        ])
    else:
        print(f"INFO: shipped corpus `log` source missing at {log_src} -- skipped")
    if weblog_src.exists():
        agree("shipped corpus `weblog` (elastic-examples-apache-logs, generate.py's own flags)", [
            "--name", "weblog", "--retrieved", "2026-09-27", "--scan", "freq,cpfreq",
            "--source", "elastic-examples-apache-logs-bc53b584",
            "--url", "https://github.com/elastic/examples/blob/"
                     "bc53b584c0f9f574d4373193334bf03541a54936/Common%20Data%20Formats/"
                     "apache_logs/apache_logs",
            "--ref", "bc53b584c0f9f574d4373193334bf03541a54936",
            "--license", "Apache-2.0",
            str(weblog_src),
        ])
    else:
        print(f"INFO: shipped corpus `weblog` source missing at {weblog_src} -- skipped")


# ---------------------------------------------------------------------------

def main() -> int:
    if not PYSCRIPT.exists():
        print(f"pcrec-analyze prototype not found at {PYSCRIPT} -- this check has "
              f"nothing to compare the C binary against; see this file's own header "
              f"for what it becomes once the prototype is deleted", file=sys.stderr)
        return 2
    if not CBIN.exists():
        print(f"build/pcrec-analyze not found at {CBIN} -- run `make` first", file=sys.stderr)
        return 2

    check_fixtures()
    check_shard_merge()
    check_check_command()
    check_r26_and_fidelity()
    check_seeded_random()
    check_shipped_corpora()

    print(f"checks passed: {_pass}")
    if _fail > 0:
        print(f"checks FAILED: {_fail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
