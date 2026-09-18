#!/usr/bin/env bash
# tests/codegen/run_longprefix_sweep.sh — [REVW.1] wave 1 stage 0's
# long-prefix full-corpus sweep.
#
# WHY THIS EXISTS. lens10_emission_kit_charter.md S4.2 (finding F3b): the
# tree's only long-prefix control (tests/cli/run_cli_tests.sh case3) compiles
# the pattern `a` at a 60-byte prefix — a trivial DFA artifact reaching
# essentially none of emit_vm.c's 40+ literal-sized scratch buffers. Wave 1
# stage 3 (not built here — see the charter and emitvm_second_pass.md §5)
# retires those buffers behind sb_fragf and claims byte-neutrality at the
# legal 60-byte prefix boundary; that claim needs a control that actually
# REACHES the buffers population, which this sweep supplies. This is the
# [MECH-REACH] repair named in docs/dev/coding_guide.md §5 item 3 and
# docs/dev/learnings.md §3.
#
# WHAT IT DOES, over EVERY tests/**/*.rxt `pattern`/`pattern-esc` line
# (docs/dev/w1stage0_evidence/longprefix_sweep.py, dialtrain_byteid's own
# --list-source-decode shape): compiles at `-p rx` and at a legal 60-byte
# prefix (PCREC_MAX_PREFIX_LEN, src/core/limits.def:133), and — only when
# the 60-byte pcrec compile succeeds — gcc-compiles the emitted .c under the
# harness's own GENCFLAGS (`-O1 -std=gnu11 -Wall -Wextra -Werror`,
# tests/harness/run.sh:213). A gcc failure on code pcrec itself accepted is
# the K38 signal this control exists to catch; the sweep's own summary
# names any such row (there is nothing embedded here that GUESSES which
# pcrec-level refusals are "benign" — see the driver's own header).
#
# WHY IT IS NOT IN `make test`. Full-corpus AND double-compiled (every
# pattern compiled twice by pcrec, and the 60-byte artifact gcc-compiled a
# third time) — heavier than test-corpus's own single pass. Opt-in, the
# tests/codegen/run_object_neutrality.sh shape: a tool you point at a pcrec
# binary, not a `make test` section. Stage 0's own committed baseline
# (docs/dev/w1stage0_evidence/longprefix_baseline.tsv, captured at this
# wave's branch point) is what a LATER wave's stage 3 diffs against — see
# that directory's CLAUDE.md — so re-running this script is only required
# when checking a NEW build against that baseline, not on every `make test`.
#
# THE TRIPWIRE (tests/size/check_size_tripwire.sh's own unpinned-max-guard
# shape, docs/dev/learnings.md §3: "a truncated sweep must be detectable by
# comparing the two"): the row count this run produces is compared against
# tests/rxtsource/run_rxtsource_tests.sh's own independently-derived
# CENSUS_BLOCKS pin (grepped live, never hand-copied — a copy would be a
# SECOND place that number could go stale). A mismatch is a hard FAIL naming
# both numbers, never a silent partial write.
#
# Usage: bash tests/codegen/run_longprefix_sweep.sh [OUT_TSV]
#   OUT_TSV defaults to build/longprefix_sweep.tsv (ephemeral; the
#   COMMITTED baseline is a separate, deliberate copy — see the evidence
#   directory's CLAUDE.md for how it was produced).
# Env: PCREC (default <root>/build/pcrec), CC, GENCFLAGS.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT]: resolves a real GNU gcc when bare gcc is Apple clang
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
OUT_TSV="${1:-$ROOT_DIR/build/longprefix_sweep.tsv}"

if [ ! -x "$PCREC" ]; then
    echo "FAIL: run_longprefix_sweep.sh: no pcrec binary at $PCREC (build first)" >&2
    exit 2
fi

mkdir -p "$(dirname "$OUT_TSV")"

echo "longprefix-sweep: PCREC=$PCREC CC=$CC OUT=$OUT_TSV" >&2
python3 "$SCRIPT_DIR/../../docs/dev/w1stage0_evidence/longprefix_sweep.py" \
    "$PCREC" "$ROOT_DIR" "$OUT_TSV" "$CC" $GENCFLAGS
py_rc=$?
if [ "$py_rc" -ne 0 ]; then
    echo "FAIL: run_longprefix_sweep.sh: the sweep driver exited $py_rc" >&2
    exit 1
fi

# THE TRIPWIRE. CENSUS_BLOCKS is the corpus's own pattern/pattern-esc line
# count, independently derived by run_rxtsource_tests.sh's own awk census
# (tests/rxtsource/run_rxtsource_tests.sh:216) — grepped, not hand-copied.
CENSUS_BLOCKS="$(grep -oE '^CENSUS_BLOCKS=[0-9]+' "$ROOT_DIR/tests/rxtsource/run_rxtsource_tests.sh" | cut -d= -f2)"
if [ -z "$CENSUS_BLOCKS" ]; then
    echo "FAIL: run_longprefix_sweep.sh: could not extract CENSUS_BLOCKS from run_rxtsource_tests.sh" >&2
    exit 1
fi

# Row count = lines in OUT_TSV minus the header.
row_count="$(($(wc -l < "$OUT_TSV") - 1))"

if [ "$row_count" != "$CENSUS_BLOCKS" ]; then
    echo "FAIL: longprefix-sweep row count MOVED: found $row_count rows, corpus census (run_rxtsource_tests.sh CENSUS_BLOCKS) is $CENSUS_BLOCKS." >&2
    echo "  If a corpus file was legitimately added/removed, this is expected — re-baseline" >&2
    echo "  docs/dev/w1stage0_evidence/longprefix_baseline.tsv in the SAME change that moves" >&2
    echo "  CENSUS_BLOCKS, and record the new count in this file's own memo." >&2
    exit 1
fi
echo "PASS: longprefix-sweep row count ($row_count) matches the corpus census pin ($CENSUS_BLOCKS)"

# GCC ANOMALIES: pcrec accepted the 60-byte artifact and gcc did not. This
# is the sweep's own K38-live-recurrence signal (S4.1 of the charter). Zero
# is the expected result at this wave's branch point (docs/dev/
# w1stage0_longprefix_sweep.md records the measured count); any nonzero
# count here is a FINDING to file, not silently absorbed by this script.
gcc_anom="$(awk -F'\t' 'NR>1 && $9=="0"{c++} END{print c+0}' "$OUT_TSV")"
if [ "$gcc_anom" != "0" ]; then
    echo "ANOMALY: $gcc_anom row(s) where pcrec accepted the 60-byte prefix but gcc's own -Werror build of the emitted C failed — see column p60_gcc_err in $OUT_TSV" >&2
fi
echo "INFO: gcc-failure-at-60 rows: $gcc_anom"

exit 0
