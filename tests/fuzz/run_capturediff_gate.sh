#!/usr/bin/env bash
# tests/fuzz/run_capturediff_gate.sh — [M4.7e] GATE-ON: a small, FIXED-SEED
# slice of the PCRE2-oracle capture-span differential (fuzz.py), wired into
# `make test` as its own section (`make test-capturediff`).
#
# WHY THIS IS SEPARATE FROM `make fuzz`: README.md's rationale for keeping
# the full stochastic campaign out of `make test` ("a clean run today says
# nothing about tomorrow's random seed, and a failure here needs human
# triage") does not apply to a run pinned at ONE fixed --seed: it is exactly
# as reproducible as any other differential in this tree — the same seed
# always generates the same patterns and subjects (fuzz.py's own docstring).
# fuzz.py's own exit-code contract already anticipates this ("Exit code is 0
# iff zero divergences... so it can be wired into a checkpoint/CI gate later
# if desired") — this script is that wiring, at a size chosen to run in
# seconds rather than minutes (the at-scale, many-seed campaign stays a
# manual/checkpoint instrument; see tests/fuzz/campaigns/).
#
# WHY A SEPARATE LIBPCRE2 PROBE, NOT A BARE fuzz.py CALL: fuzz.py's own
# oracle plumbing is designed to fail loudly mid-run rather than skip
# gracefully (tests/fuzz/CLAUDE.md: "the fuzz oracle must fail hard") --
# correct for a manual dev tool, wrong for a `make test` section on a
# stranger's box without libpcre2-8-0 (PC-3's whole scenario,
# tests/registry/run_registry_tests.sh). So this script probes first, the
# same PC-3/PC-4 way: build tests/fuzz/pcre2_oracle.c (dlopen-based, no link
# dependency on libpcre2 itself) and call its own `--version`, which already
# does the real load attempt and reports failure cleanly (pcre2_oracle.c's
# load_pcre2(), exit code 3, no libpcre2 message). Reuses the existing
# probe rather than a second copy of the dlopen logic (pcre2_abi.h's own
# reason for existing).
#
# Usage: bash tests/fuzz/run_capturediff_gate.sh
# Env: CC (default gcc), PCREC (default build/pcrec), KEEP=1 (keep the
#   fuzz.py workdir on divergence, forwarded as --keep)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

# Pinned deliberately: this is a REGRESSION GATE, not a search for new
# divergences (that's the at-scale campaign's job, tests/fuzz/campaigns/).
# seed=1/patterns=300/subjects=15 are fuzz.py's own argparse defaults
# (unchanged here, spelled out anyway so a future default change there does
# not silently resize this gate) -- CAPTURE_TEMPLATES' ~20% draw density
# means captures get real exercise even at this size (measured ~55-60
# capture-template patterns per 300 in the at-scale campaign's own logs).
GATE_SEED=1
GATE_PATTERNS=300
GATE_SUBJECTS=15

WORKDIR="$(mktemp -d)"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

if [ ! -f "$ROOT_DIR/build/pcrec" ]; then
    echo "capturediff-gate: build/pcrec not built — run 'make' first" >&2
    exit 1
fi

ORACLE_BIN="$WORKDIR/pcre2_oracle"
if ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
        -o "$ORACLE_BIN" "$SCRIPT_DIR/pcre2_oracle.c" -ldl; then
    echo "capturediff-gate: FAILED TO BUILD pcre2_oracle.c" >&2
    exit 1
fi

if ! "$ORACLE_BIN" --version >/dev/null 2>"$WORKDIR/oracle_probe.err"; then
    echo "SKIP: run_capturediff_gate (M4.7e): $(cat "$WORKDIR/oracle_probe.err" | head -1)" >&2
    echo "SKIP: the capture differential did NOT run. Everything else in" >&2
    echo "SKIP: \`make test\` compares pcrec with pcrec." >&2
    echo "SKIP: install the PCRE2 8-bit runtime (Debian/Ubuntu package" >&2
    echo "SKIP: 'libpcre2-8-0') to enable it." >&2
    exit 0
fi

KEEPARG=()
[ "$KEEP" = "1" ] && KEEPARG=(--keep)

GATEOUT="$WORKDIR/gate.out"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}" CC="$CC" \
    python3 "$SCRIPT_DIR/fuzz.py" --seed "$GATE_SEED" --patterns "$GATE_PATTERNS" \
        --subjects "$GATE_SUBJECTS" "${KEEPARG[@]}" 2>&1 | tee "$GATEOUT"
rc="${PIPESTATUS[0]}"

# NO-SILENT-CAPS: every exclusion bucket fuzz.py's own summary reports is
# echoed here too, so a `make test` run surfaces them without anyone having
# to go find fuzz.py's stdout by hand. fuzz.py's summary already prints
# these lines; this just re-asserts none of them are being silently dropped
# by grepping the same output back out and confirming the lines exist.
for label in "content divergences" "accept/reject divergences" \
             "DFA state-cap" "oracle inconclusive" "optimizer quirk" \
             "pcrec compile timeout" "oracle probe timeout"; do
    if ! grep -qi "$label" "$GATEOUT"; then
        echo "capturediff-gate: fuzz.py's summary no longer reports '$label' -- exclusion bucket vanished from output, not just from the count. Fix fuzz.py's summary before trusting this gate." >&2
        rc=1
    fi
done

if [ "$rc" -eq 0 ]; then
    echo "capturediff-gate: PASS (seed=$GATE_SEED patterns=$GATE_PATTERNS subjects=$GATE_SUBJECTS, 0 accept/reject + 0 content divergences)"
else
    echo "capturediff-gate: FAIL — see divergences above; repro bundle path is in fuzz.py's own output" >&2
fi
exit "$rc"
