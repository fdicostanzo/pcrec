#!/usr/bin/env python3
"""tests/findings/run_analyzer_tests.py — [FINDINGS] step B3's own checks.

Exercises `scripts/pcrec_analyze.py` (the analyzer PROTOTYPE) against
design.md §11.8's acceptance list, scoped to what B3 alone can discharge
(B0/B1/B2 have not landed: no `.rxt` schema support for `analysis`
bundles, no accessor, no `--list-analysis` CLI). Every item below cites
the design.md subsection and, where relevant, the r2 panel finding it
answers. Python3 only, no `make` build required — see this directory's
own CLAUDE.md for why the target is deliberately light and unwired from
`TEST_SECTIONS`.

Usage: python3 tests/findings/run_analyzer_tests.py
"""
from __future__ import annotations

import hashlib
import itertools
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[2]
ANALYZE = ROOT / "scripts" / "pcrec_analyze.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
NGRAM_COUNT = ROOT / "docs" / "dev" / "findings_measure" / "scripts" / "ngram_count.py"
WEB_REQUEST = ROOT / "docs" / "dev" / "findings_measure" / "corpora" / "web_request.txt"

sys.path.insert(0, str(ROOT / "scripts"))
import pcrec_analyze as pa  # noqa: E402  (the module under test, imported for its parser/model)

_pass = 0
_fail = 0
_info = 0


def ok(msg: str) -> None:
    global _pass
    _pass += 1
    print(f"PASS: {msg}")


def bad(msg: str) -> None:
    global _fail
    _fail += 1
    print(f"FAIL: {msg}", file=sys.stderr)


def info(msg: str) -> None:
    global _info
    _info += 1
    print(f"INFO: {msg}")


def run(args: Sequence[str], stdin: Optional[bytes] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ANALYZE), *args],
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def analyze(*args: str, stdin: Optional[bytes] = None) -> bytes:
    cp = run(list(args), stdin=stdin)
    if cp.returncode != 0:
        raise RuntimeError(f"pcrec-analyze {args} failed rc={cp.returncode}: {cp.stderr.decode()}")
    return cp.stdout


# ---------------------------------------------------------------------------
# 1. Determinism (design.md §11.8 "determinism (R27c)")
# ---------------------------------------------------------------------------

def check_determinism() -> None:
    f = FIXTURES / "basic.txt"
    a = analyze("--name", "d", "--retrieved", "2026-09-26", "--scan", "freq,bigram", str(f))
    b = analyze("--name", "d", "--retrieved", "2026-09-26", "--scan", "freq,bigram", str(f))
    if a == b:
        ok("determinism: two runs over the same input+flags are byte-identical")
    else:
        bad("determinism: two runs over the same input+flags differ")


# ---------------------------------------------------------------------------
# 2. stdin ≡ file (design.md §11.8)
# ---------------------------------------------------------------------------

def check_stdin_equals_file() -> None:
    f = FIXTURES / "basic.txt"
    via_file = analyze("--name", "d", "--retrieved", "2026-09-26", "--scan", "freq,bigram", str(f))
    via_dash = analyze("--name", "d", "--retrieved", "2026-09-26", "--scan", "freq,bigram", "-",
                        stdin=f.read_bytes())
    via_omitted = analyze("--name", "d", "--retrieved", "2026-09-26", "--scan", "freq,bigram",
                           stdin=f.read_bytes())
    if via_file == via_dash == via_omitted:
        ok("stdin ≡ file: explicit '-' and an omitted FILE both equal the FILE form")
    else:
        bad("stdin ≡ file: stdin and file forms disagree")

    cp = run(["--name", "d", "--retrieved", "2026-09-26", "--scan", "freq", "--shard", "1/2", "-"],
             stdin=f.read_bytes())
    if cp.returncode != 0:
        ok("--shard refuses stdin (design.md §10.4: 'stdin cannot be sharded')")
    else:
        bad("--shard silently accepted stdin")


# ---------------------------------------------------------------------------
# 3. Shard/merge, order-independent (design.md §10.4, D123-3a; sabotage F-7)
# ---------------------------------------------------------------------------

def digest_of(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def shard_merge_round_trip(path: Path, scan: str, name: str) -> None:
    whole = analyze("--name", name, "--retrieved", "d", "--scan", scan, str(path))
    size, sha = digest_of(path)
    for n in (1, 2, 3, 4, 5, 6, 7):
        parts: List[Path] = []
        with tempfile.TemporaryDirectory() as tmp:
            tmpd = Path(tmp)
            for k in range(1, n + 1):
                part_bytes = analyze(
                    "--name", name, "--retrieved", "d", "--scan", scan,
                    "--shard", f"{k}/{n}", str(path),
                )
                p = tmpd / f"part{k}.rxt"
                p.write_bytes(part_bytes)
                parts.append(p)

            orders: List[List[Path]]
            if n <= 4:
                orders = [list(perm) for perm in itertools.permutations(parts)]
            else:
                rng = random.Random(1000 + n)  # seeded (D123-3a: order-independent)
                orders = [parts]
                for _ in range(3):
                    shuffled = list(parts)
                    rng.shuffle(shuffled)
                    orders.append(shuffled)

            all_match = True
            for order in orders:
                merged = analyze(
                    "--merge", "--name", name, "--bytes", str(size), "--sha256", sha,
                    *[str(p) for p in order],
                )
                if merged != whole:
                    all_match = False
            if all_match:
                ok(f"shard/merge [{scan}] N={n} ({len(orders)} order(s)): byte-identical to whole-file scan")
            else:
                bad(f"shard/merge [{scan}] N={n}: a merge order diverged from the whole-file scan")


def check_shard_merge() -> None:
    shard_merge_round_trip(FIXTURES / "basic.txt", "freq,bigram", "sm1")
    shard_merge_round_trip(FIXTURES / "cpfreq_seam.txt", "cpfreq", "sm2")
    shard_merge_round_trip(FIXTURES / "utf8_mixed.txt", "freq,cpfreq,bigram", "sm3")


# ---------------------------------------------------------------------------
# 4. Shard 1's first byte ([r2 A-1])
# ---------------------------------------------------------------------------

def check_shard1_first_byte() -> None:
    f = FIXTURES / "shard1_first_byte.bin"
    data = f.read_bytes()
    assert data.count(data[0:1]) == 1, "fixture invariant broken: byte 0 must be unique"
    all_ok = True
    for n in (1, 2, 3, 4, 5, 8):
        out = analyze("--name", "s1", "--retrieved", "d", "--scan", "freq", "--shard", f"1/{n}", str(f))
        _, kinds = pa.parse_bundle(out.decode())
        count = kinds["freq"].rows.get(data[0], 0)
        if count != 1:
            bad(f"shard-1 first byte [r2 A-1]: N={n} gave count {count}, expected exactly 1")
            all_ok = False
    if all_ok:
        ok("shard-1 first byte [r2 A-1]: byte 0 counts exactly 1 under every N tried")


# ---------------------------------------------------------------------------
# 5. cpfreq seam straddling every cut offset ([r2 A-2])
# ---------------------------------------------------------------------------

def check_cpfreq_seam() -> None:
    f = FIXTURES / "cpfreq_seam.txt"
    whole = analyze("--name", "cs", "--retrieved", "d", "--scan", "cpfreq", str(f))
    _, whole_kinds = pa.parse_bundle(whole.decode())
    whole_rows = whole_kinds["cpfreq"].rows

    size = f.stat().st_size
    seen_straddle = False
    all_ok = True
    for n in range(1, 24):
        data = f.read_bytes()
        merged_rows: dict = {}
        for k in range(1, n + 1):
            start, end = pa.shard_bounds(size, k, n)
            if pa.is_continuation_byte(data[start]) if start < size else False:
                seen_straddle = True
            out = analyze("--name", "cs", "--retrieved", "d", "--scan", "cpfreq",
                           "--shard", f"{k}/{n}", str(f))
            _, kinds = pa.parse_bundle(out.decode())
            for key, count in kinds["cpfreq"].rows.items():
                merged_rows[key] = merged_rows.get(key, 0) + count
        if merged_rows != whole_rows:
            bad(f"cpfreq seam [r2 A-2]: N={n} shard union != whole-file cpfreq counts")
            all_ok = False
    if all_ok:
        ok(f"cpfreq seam [r2 A-2]: shard union equals the whole-file count for N=1..23"
           f" (a nominal cut landed mid-code-point: {seen_straddle})")
    if not seen_straddle:
        info("cpfreq seam fixture never actually straddled a continuation byte at N<=23 "
             "— the fixture or the N range should widen (see findb3_report.md)")


# ---------------------------------------------------------------------------
# 6. python ≡ C (design.md §10.1/§11.8: NOT APPLICABLE before B6)
# ---------------------------------------------------------------------------

def check_python_equals_c() -> None:
    info("python ≡ C (design.md §11.8, B6's own acceptance item): NOT YET "
         "APPLICABLE — analyze/'s C end state (build step B6) does not exist. "
         "Recorded here, not silently skipped, per design.md §9's 'never'.")


# ---------------------------------------------------------------------------
# 7. --check (positive + one-byte-changed negative)
# ---------------------------------------------------------------------------

def check_check_command() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        src = tmpd / "sample.txt"
        src.write_bytes((FIXTURES / "basic.txt").read_bytes())
        bundle = tmpd / "bundle.rxt"
        bundle.write_bytes(analyze("--name", "chk", "--retrieved", "d", "--scan", "freq,bigram", str(src)))

        cp = run(["--check", str(bundle), str(src)])
        if cp.returncode == 0:
            ok("--check: a matching recount exits 0")
        else:
            bad(f"--check: matching recount did not exit 0: {cp.stderr.decode()}")

        mutated = tmpd / "sample_mutated.txt"
        data = bytearray(src.read_bytes())
        data[0] ^= 0xFF
        mutated.write_bytes(bytes(data))
        cp = run(["--check", str(bundle), str(mutated)])
        if cp.returncode != 0:
            ok("--check: a one-byte-changed source is rejected (nonzero exit)")
        else:
            bad("--check: a one-byte-changed source was accepted")

        # [r2 A-5]'s analyzer-level analogue: a manifest-only (missing)
        # source must FAIL CLOSED, never silently pass.
        missing = tmpd / "does_not_exist.txt"
        cp = run(["--check", str(bundle), str(missing)])
        if cp.returncode != 0 and b"not found" in cp.stderr:
            ok("--check [r2 A-5 analogue]: a missing (manifest-only) source fails CLOSED, loudly")
        else:
            bad("--check: a missing source did not fail closed with a named reason")


# ---------------------------------------------------------------------------
# 8. R26: cpfreq hard-errors on invalid UTF-8; freq succeeds on the same input
# ---------------------------------------------------------------------------

def check_r26() -> None:
    f = FIXTURES / "invalid_utf8.bin"
    cp = run(["--name", "r26", "--retrieved", "d", "--scan", "cpfreq", str(f)])
    if cp.returncode != 0 and b"R26" in cp.stderr:
        ok("R26: --scan cpfreq on invalid UTF-8 is a hard error")
    else:
        bad(f"R26: --scan cpfreq on invalid UTF-8 did not hard-error (rc={cp.returncode})")

    cp = run(["--name", "r26", "--retrieved", "d", "--scan", "freq", str(f)])
    if cp.returncode == 0:
        ok("R26: --scan freq succeeds on the same invalid-UTF-8 input")
    else:
        bad("R26: --scan freq unexpectedly failed on invalid-UTF-8 input")

    # a combined request must also hard-error (D123-3: never silently skip
    # a requested scan) rather than silently emitting freq alone.
    cp = run(["--name", "r26", "--retrieved", "d", "--scan", "freq,cpfreq", str(f)])
    if cp.returncode != 0:
        ok("D123-3: --scan freq,cpfreq on invalid UTF-8 refuses rather than silently dropping cpfreq")
    else:
        bad("D123-3: --scan freq,cpfreq on invalid UTF-8 did not refuse")


# ---------------------------------------------------------------------------
# 9. Collision-free declarations ([r2 M-B1], design.md §10.2's table)
# ---------------------------------------------------------------------------

def check_collision_free_declarations() -> None:
    cases = [
        ("ascii_only.txt", "ascii"),
        ("utf8_mixed.txt", "utf8"),
    ]
    all_ok = True
    for fname, expect_enc in cases:
        f = FIXTURES / fname
        out = analyze("--name", "cf", "--retrieved", "d", "--scan", "freq,cpfreq", str(f))
        _, kinds = pa.parse_bundle(out.decode())
        if kinds["freq"].encoding != expect_enc or kinds["cpfreq"].encoding != expect_enc:
            bad(f"collision-free [{fname}]: encoding mismatch")
            all_ok = False
            continue
        freq_serves = kinds["freq"].serves
        cpfreq_serves = kinds["cpfreq"].serves
        freq_whens = {when for (_, when, _) in freq_serves}
        cpfreq_whens = {when for (_, when, _) in cpfreq_serves}
        # [r2 M-B1]: no encoding may be claimed by BOTH blocks' byte-rate line.
        freq_encs = set()
        for w in freq_whens:
            freq_encs.update(e.strip() for e in w.split(","))
        cpfreq_encs = set()
        for w in cpfreq_whens:
            cpfreq_encs.update(e.strip() for e in w.split(","))
        if freq_encs & cpfreq_encs:
            bad(f"collision-free [{fname}]: freq and cpfreq both claim {freq_encs & cpfreq_encs}")
            all_ok = False
        elif freq_encs != {"byte"} or cpfreq_encs != {"utf8"}:
            bad(f"collision-free [{fname}]: expected freq={{byte}}, cpfreq={{utf8}}; "
                f"got freq={freq_encs}, cpfreq={cpfreq_encs}")
            all_ok = False
    if all_ok:
        ok("collision-free declarations [r2 M-B1]: freq/cpfreq split byte/utf8 with no overlap, "
           "on both the ascii-only and utf8-mixed observed rows")


# ---------------------------------------------------------------------------
# 10. R27a: analyzer output parses under `pcrec --list-analysis` (B2, OWED)
# ---------------------------------------------------------------------------

def check_r27a() -> None:
    info("R27a (design.md §11.8: 'analyzer output -> pcrec --list-analysis NAME "
         "-I <dir> parses clean'): NOT YET TESTABLE — B2 (the CLI/resolution "
         "step) has not landed, so `--list-analysis` does not exist yet. OWED "
         "to whichever lane lands B2; see findb3_report.md.")


# ---------------------------------------------------------------------------
# 11. §13 B3's own acceptance line: RUNEST's web_request sample, normalized
# ---------------------------------------------------------------------------

FIND_FLOOR_PPM = 2  # design.md §2.5's named floor


def normalize_2_5(counts: List[int]) -> List[int]:
    """An INDEPENDENT python re-implementation of design.md §2.5's counts ->
    byte-rate ppm normalization (B1's `src/core/findings.c` does not exist
    yet). Written from the spec text, not from any future C, per the
    learnings.md §3 rule that a reader and its check must not share a
    source."""
    n = sum(counts)
    if n == 0:
        raise ValueError("N == 0")
    if any(c > pa.PCREC_MAX_FIND_COUNT for c in counts):
        raise ValueError("a count exceeds PCREC_MAX_FIND_COUNT")
    z = sum(1 for c in counts if c == 0)
    m = 1_000_000 - FIND_FLOOR_PPM * z
    ppm = []
    for c in counts:
        if c == 0:
            ppm.append(FIND_FLOOR_PPM)
        else:
            ppm.append(max(FIND_FLOOR_PPM, (c * m) // n))
    residue = 1_000_000 - sum(ppm)
    if residue:
        best_i = max(range(256), key=lambda i: (ppm[i], -i))
        ppm[best_i] += residue
    return ppm


def check_runest_web_request() -> None:
    if not WEB_REQUEST.exists() or not NGRAM_COUNT.exists():
        info("RUNEST web_request normalization: fixture corpus or ngram_count.py "
             "missing — skipping (this repo's own docs/dev/findings_measure/ "
             "artifacts are expected to be present)")
        return

    import importlib.util

    spec = importlib.util.spec_from_file_location("ngram_count", NGRAM_COUNT)
    ngram_count = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ngram_count)  # type: ignore[union-attr]

    data = WEB_REQUEST.read_bytes()
    runest_unigram = ngram_count.Counts.build(data).unigram

    out = analyze("--name", "wr", "--retrieved", "d", "--scan", "freq", str(WEB_REQUEST))
    _, kinds = pa.parse_bundle(out.decode())
    analyzer_counts = [kinds["freq"].rows.get(b, 0) for b in range(256)]

    if analyzer_counts == runest_unigram:
        ok("§13 B3: pcrec-analyze's freq counts over RUNEST's web_request sample "
           "are byte-identical to RUNEST's own unigram counts (ngram_count.py)")
    else:
        bad("§13 B3: pcrec-analyze's freq counts over web_request diverge from "
            "RUNEST's own unigram counts")
        return

    ppm = normalize_2_5(analyzer_counts)
    total = sum(ppm)
    floor_ok = all(v >= FIND_FLOOR_PPM for v in ppm)
    if total == 1_000_000 and floor_ok:
        ok("§13 B3: normalizing web_request's counts through an independent §2.5 "
           "reimplementation gives a well-formed byte-rate table (Σ=1,000,000, "
           "every entry ≥ the floor) — B1's own function does not exist yet, "
           "so this is the closest check available before it lands")
    else:
        bad(f"§13 B3: normalized web_request table is malformed (Σ={total}, floor_ok={floor_ok})")


# ---------------------------------------------------------------------------

def main() -> int:
    if not ANALYZE.exists():
        print(f"pcrec-analyze not found at {ANALYZE}", file=sys.stderr)
        return 2

    check_determinism()
    check_stdin_equals_file()
    check_shard_merge()
    check_shard1_first_byte()
    check_cpfreq_seam()
    check_python_equals_c()
    check_check_command()
    check_r26()
    check_collision_free_declarations()
    check_r27a()
    check_runest_web_request()

    print(f"checks passed: {_pass}")
    print(f"checks info (not pass/fail): {_info}")
    if _fail > 0:
        print(f"checks FAILED: {_fail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
