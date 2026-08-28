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

# EXACT EXPECTED POPULATIONS (manager ruling, 2026-08-17): a fixed seed's
# generation is deterministic (fuzz.py seeds `random` once, up front, main
# thread only), so every one of these is a REPRODUCIBLE fact of this seed
# on this pcrec, not a guess -- measured twice on a quiet box, byte-identical
# both times. Report SELECTED counts, not merely "gate passed": drift in ANY
# of these means either the generator, pcrec, or fuzz.py's own bucketing
# changed, and that must be loud, the same discipline registry_check's 169
# and PC-3's 163 pins already carry (tests/registry/run_registry_tests.sh).
# The two TIMING-SENSITIVE buckets (pcrec compile timeout, oracle probe
# timeout) are pinned to 0 like every other bucket -- FAIL is still correct
# on drift, but a nonzero reading there under a heavily loaded box is a load
# artifact to check first, not necessarily a new pcrec defect (see
# docs/testing.md's D14 busy-box precedent, tests/bench/run_bench.sh's
# LOAD_LIMIT).
#
# RE-MEASURED 2026-08-17 (second addendum) after MODULE_CLASS_ATOMS landed:
# a generator change alters what a FIXED seed draws (still deterministic,
# just deterministically different), so these are not the same numbers the
# gate shipped with originally -- re-measured twice on a quiet box
# (byte-identical both times) rather than hand-adjusted from the old set.
#
# "module construct patterns" is the row that makes gate-ON PROVEN rather
# than merely claimed, every single `make test` run from here on: it is
# PINNED NONZERO (75 of 300, ~25% at this seed) -- a regression that ever
# drops it to 0 (MODULE_CLASS_WEIGHT zeroed out, the marker list emptied,
# the counter silently disconnected) fails this gate exactly as loudly as
# a real divergence would, closing the README.md/campaign-log-documented
# vacuity finding for good rather than just for this one measurement.
# [SEL-1] (2026-08-28, K40/K41) RE-MEASURED after the DFA-cap-overflow
# fallback landed: under `--engine=auto` (what compile_with_pcrec() always
# passes, no `--engine` flag), the 8 patterns this fixed seed used to draw
# that hit `PCREC_MAX_DFA_STATES_TABLE`/`_GOTO` no longer REFUSE with "too
# complex for the DFA engine" -- they now compile as VM fallbacks. `state_cap`
# (fuzz.py's own bucket, only "too complex for the DFA engine" or "NFA
# exceeds" in pcrec's stderr) drops from 8 to 0 for exactly this reason: the
# "NFA exceeds" half is UNCHANGED by SEL-1 (that cap has no fallback engine to
# hand a pattern to, docs/spec/limits.md §3.3), so on this fixed seed's own
# draw the bucket's population was entirely the DFA-cap half. Those 8
# patterns move into the ordinary accept/compare pipeline instead: "both
# accept" 175 -> 183 and "subject pairs compared" 2625 -> 2745 (8 * 15 = 120
# more pairs) follow arithmetically. "oracle inconclusive" gains a NEW,
# TIMING-SENSITIVE nonzero floor (measured 2-3 across four runs on this box,
# never 0) because some of those 8 newly-VM-compiled patterns are complex
# enough that a fraction of their real subject comparisons hit PCRE2's own
# match-limit or the oracle's execution timeout -- collateral from patterns
# that used to never REACH subject comparison at all, not a new divergence
# class. Re-measured 4 times on this box (byte-identical on every bucket
# except "oracle inconclusive", which this row's own comment already says is
# TIMING-SENSITIVE), per this section's own "measured twice on a quiet box"
# discipline.
declare -A EXPECT=(
    ["patterns generated"]=300
    ["module construct patterns"]=75
    ["both accept"]=183
    ["both reject"]=117
    ["pcrec-only reject"]=0
    ["pcre2-only reject"]=0
    ["PCRE2 size-limit"]=0
    ["DFA state-cap"]=0
    ["pcrec compile timeout"]=0
    ["oracle probe timeout"]=0
    ["subject pairs compared"]=2745
    ["oracle inconclusive"]=3
    ["pcrec step-budget exhausted"]=0
    ["pcrec frame-budget exhausted"]=0
    ["known PCRE2 optimizer quirk"]=0
    ["content divergences"]=0
    ["accept/reject divergences"]=0
)

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

# NO-SILENT-CAPS, EXACT COUNTS: every bucket in EXPECT is both PRESENT (a
# label vanishing from fuzz.py's summary is itself a regression -- this
# gate would otherwise read a bucket as "0" forever once nothing prints it)
# and equal to its pinned value. Report every SELECTED count, not merely
# pass/fail, so drift is visible in the same line that names it.
echo
echo "capturediff-gate: selected counts (expected -> actual)"
drift=0
for label in "patterns generated" "module construct patterns" "both accept" "both reject" \
             "pcrec-only reject" "pcre2-only reject" "PCRE2 size-limit" \
             "DFA state-cap" "pcrec compile timeout" \
             "oracle probe timeout" "subject pairs compared" \
             "oracle inconclusive" "pcrec step-budget exhausted" \
             "pcrec frame-budget exhausted" "known PCRE2 optimizer quirk" \
             "content divergences" "accept/reject divergences"; do
    # Extract the number immediately after THIS label's own colon, not the
    # first digit anywhere on the line -- several lines carry an earlier,
    # unrelated digit in their parenthetical explanation (e.g. "known PCRE2
    # optimizer quirk (anchor in {0} group): 0" -- a naive "first number on
    # the line" grab would read the quirk-name's literal "0" forever and
    # never notice a real nonzero count).
    actual="$(grep -ioP "${label}[^:]*:\s*\K[0-9]+" "$GATEOUT" | head -1)"
    if [ -z "$actual" ]; then
        echo "  $label: expected=${EXPECT[$label]} actual=MISSING (label vanished from fuzz.py's summary)" >&2
        drift=1
        continue
    fi
    expected="${EXPECT[$label]}"
    if [ "$actual" != "$expected" ]; then
        note=""
        case "$label" in
            "pcrec compile timeout"|"oracle probe timeout")
                note=" (TIMING-SENSITIVE bucket -- check box load before treating this as a pcrec defect, docs/testing.md's D14 busy-box precedent)" ;;
            "oracle inconclusive")
                note=" (TIMING-SENSITIVE since [SEL-1]/K41 -- PCRE2's own match-limit or the oracle's execution timeout on the newly-VM-compiled complex patterns; measured 2-3 across four runs on the landing box, check load before treating as a pcrec defect)" ;;
        esac
        echo "  $label: expected=$expected actual=$actual  DRIFT$note" >&2
        drift=1
    else
        echo "  $label: $actual"
    fi
done

# [SEL-1] (2026-08-28, K41) "gcc compile fails" is no longer a single bucket
# in this loop, and that is a NARROWING rather than a removal: it splits
# into GCC-COMPILE-FAIL-OVER-BUDGET (gcc itself hit a resource limit on an
# oversized generated VM program — "CPU time limit exceeded" or "internal
# compiler error", K41's own signature, now unhidden because [SEL-1] (K40)
# turned the DFA-prefilter overflow that used to REFUSE this witness into a
# fallback that SHIPS the VM artifact gcc then chokes on) and everything
# else, which stays a genuine pcrec-side compile defect and stays pinned at
# 0. Folding the over-budget case into the old single bucket would have
# been the "silent allowlist" this row was explicitly asked not to be: a
# bare re-pin to 1 could not tell K41's witness apart from a real NEW gcc
# failure landing beside it. Both counts are read from the SAME `GCC-FAIL`
# lines fuzz.py already prints (one implementation of "did gcc fail",
# never a second one) -- only the CLASSIFICATION is new, and it lives here
# rather than in fuzz.py because this gate is the one caller that needs it
# (the at-scale campaign, tests/fuzz/campaigns/, reads fuzz.py's own
# summary directly and is unaffected).
#
# THIS BUCKET IS ITSELF TIMING-SENSITIVE, MEASURED RATHER THAN ASSUMED, and
# that has to be said plainly: fuzz.py compiles generated code at `-O0` by
# default (GENCFLAGS) under a FIXED CPU-second ulimit (gen_timeout.sh
# `cpusecs`, D45's own budget, not scaled to box speed), and K41's witness
# measured at 7.8 CPU-seconds under `-O0` on the landing box against that
# same ~10s cap -- a narrow margin, not a comfortable one. Four runs on
# THIS box all read 0 here (the compile finishes inside the budget every
# time), which is a real, honest measurement and not a sign the check is
# broken: it means this box is fast/quiet enough today that K41's witness
# does not cross the line, the same "check box load first" caveat every
# other TIMING-SENSITIVE bucket in this file already carries. The check
# still fails loudly on drift either way (manager's ruling: pinned, not a
# silent allowlist) -- a 0 here is not silently passed, it is reported as a
# DRIFT with this bucket's own timing note attached, exactly like
# "oracle inconclusive" below.
gcc_fail_total="$(grep -c '^\[fuzz\] GCC-FAIL pattern=' "$GATEOUT" || true)"
gcc_fail_overbudget="$(grep -c '^\[fuzz\] GCC-FAIL pattern=.*\(CPU time limit exceeded\|internal compiler error\)' "$GATEOUT" || true)"
gcc_fail_other=$((gcc_fail_total - gcc_fail_overbudget))
if [ "$gcc_fail_other" -ne 0 ]; then
    echo "  gcc compile fails (other than K41's over-budget class): expected=0 actual=$gcc_fail_other  DRIFT -- a REAL gcc-side compile defect, not K41" >&2
    drift=1
else
    echo "  gcc compile fails (other than K41's over-budget class): 0"
fi
if [ "$gcc_fail_overbudget" -ne 1 ]; then
    echo "  gcc compile fails (K41 over-budget class): expected=1 actual=$gcc_fail_overbudget  DRIFT (TIMING-SENSITIVE -- gcc's own CPU-second ulimit vs. box speed, K41's witness measured 7.8s against a ~10s cap; check box load first) -- docs/dev/known_issues.md K41: 0 can mean a fast/quiet box did not cross the line THIS run (re-run before concluding the witness stopped reaching its shape); >1 means a NEW pattern is hitting the same gcc-resource-limit class (investigate before re-pinning upward)" >&2
    drift=1
else
    echo "  gcc compile fails (K41 over-budget class): 1"
fi

[ "$drift" -ne 0 ] && rc=1

if [ "$rc" -eq 0 ]; then
    echo "capturediff-gate: PASS (seed=$GATE_SEED patterns=$GATE_PATTERNS subjects=$GATE_SUBJECTS, every selected count matched its pinned value)"
else
    echo "capturediff-gate: FAIL — see drift/divergences above; repro bundle path is in fuzz.py's own output" >&2
fi
exit "$rc"
