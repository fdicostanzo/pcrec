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
# [SEL-1] (2026-08-28, K41, manager correction): the earlier version of this
# gate classified K41's witness by grepping GCC'S OWN ERROR TEXT ("CPU time
# limit exceeded" / "internal compiler error") -- a TIMING-DEPENDENT signal
# (K41's witness measured 7.8 CPU-s under -O0 against a ~10s cap, a narrow
# margin that read 0 or 1 run to run depending on box speed/load: red on one
# box, green on another). K41's actual mechanism is SIZE, not gcc's luck, so
# fuzz.py itself now classifies "K41 oversize artifact" by the emitted .c's
# byte size (K41_OVERSIZE_BYTES = 1,000,000, checked BEFORE and
# INDEPENDENTLY of gcc -- see fuzz.py's own comment above that constant) and
# prints it as its own bucket, fully deterministic per --seed. gcc's own
# outcome on an oversize artifact (compiled / over-budget) is read from
# fuzz.py's summary as INFORMATION ONLY (the "K41 witness" line printed
# below, never a pass/fail count) -- this gate no longer has any bucket
# whose pass/fail reading depends on gcc's CPU-time luck. "gcc compile
# fails" stays a single, ordinary, deterministic bucket again (pinned at 0):
# it means what it always meant -- a REAL pcrec-emitted-code compile defect
# -- because the oversize bucket no longer counts against it either way.
#
# RE-MEASURED against the SIZE bucket rather than assumed: at this fixed
# seed's own draw, exactly TWO patterns cross K41_OVERSIZE_BYTES (1,250,766
# and 2,004,449 bytes), not the one the old gcc-error-text classification
# happened to catch -- the second one compiles within this box's gcc budget
# today, so it never showed up as a GCC-FAIL under the old design at all,
# and would have gone on being silently compared like any ordinary pattern.
# Pulling BOTH fully out of the accept/compare pipeline (not just recording
# gcc's outcome for one of them) moves population, arithmetically: "both
# [ART-SIZE]/D84 (2026-08-29) MOVED FIVE OF THESE, and the reading matters
# more than the numbers: the oversize bucket goes 2 -> 0 NOT because the two
# witnesses stopped having their shapes, but because each leaves it a
# DIFFERENT way. Witness 1 is FIXED — the unroll ladder selects K=1 and its
# artifact drops from 2,004,449 bytes to 116,511, an order of magnitude under
# the 1,000,000 classifier — so it RE-ENTERS the accept/compare population
# ("both accept" 181 -> 182, "subject pairs compared" 2715 -> 2730 at 15
# subjects each, and "oracle inconclusive" 0 -> 3, which is its own subjects
# returning and is the one count that could not be predicted by arithmetic).
# Witness 2 is REFUSED by both emitted-size caps, so there is no artifact to
# classify at all, and it lands in the NEW "emitted-size cap" bucket pinned at
# 1 below. That bucket exists because a documented ceiling doing its job is
# not an accept/reject divergence: without it the refusal would count as
# "pcrec-only reject" and read as an actionable finding on every run — the
# same reason fuzz.py already diverts state_cap and engine_limit.
# See docs/dev/known_issues.md K41's [ART-SIZE] disposition; the trigger to
# revisit these pins is [OPT-4]/K39 shrinking witness 2's prefilter, after
# which it should compile rather than refuse.
#
# The pre-[ART-SIZE] derivation, kept because it is what these numbers moved
# FROM: "both accept" 183 -> 181 (183 - 2), "subject pairs compared" 2745 -> 2715
# (2745 - 2*15), and "oracle inconclusive" 3 -> 0 -- the 3 inconclusive
# hits the old design attributed to the newly-VM-compiled-but-still-compared
# population turn out to belong entirely to these same two oversize
# patterns' own subject comparisons, which this design no longer runs
# through the comparison accounting at all. Verified byte-identical across
# THREE consecutive solo runs on this box (this file's own "measured twice
# on a quiet box" discipline, done one better) -- the explicit determinism
# proof the manager asked the SIZE redesign to produce.
declare -A EXPECT=(
    ["patterns generated"]=300
    ["module construct patterns"]=75
    ["both accept"]=182
    ["both reject"]=117
    ["pcrec-only reject"]=0
    ["pcre2-only reject"]=0
    ["PCRE2 size-limit"]=0
    ["DFA state-cap"]=0
    ["K41 oversize artifact"]=0
    ["emitted-size cap"]=1
    ["gcc compile fails"]=0
    ["pcrec compile timeout"]=0
    ["oracle probe timeout"]=0
    ["subject pairs compared"]=2730
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
# K41's witness pattern, read from fuzz.py's own stdout summary block (the
# "K41-WITNESS pattern=... size=... gcc=..." line -- see fuzz.py's
# oversize_hits print loop) so the failure message below can NAME it rather
# than just count it, per the manager's correction.
k41_witness="$(grep -m1 '^  K41-WITNESS pattern=' "$GATEOUT" | sed 's/^  //')"
[ -z "$k41_witness" ] && k41_witness="none printed -- see fuzz.py oversize_hits block"

echo
echo "capturediff-gate: selected counts (expected -> actual)"
drift=0
for label in "patterns generated" "module construct patterns" "both accept" "both reject" \
             "pcrec-only reject" "pcre2-only reject" "PCRE2 size-limit" \
             "DFA state-cap" "K41 oversize artifact" "emitted-size cap" \
             "gcc compile fails" \
             "pcrec compile timeout" \
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
                note=" (TIMING-SENSITIVE -- PCRE2's own match-limit or the oracle's execution timeout on a subject comparison; re-measured at 0 across three consecutive runs since the K41 SIZE redesign pulled the two oversize patterns that used to account for this bucket's whole nonzero population out of the comparison pipeline entirely (see the EXPECT block's own comment) -- check box load before treating a nonzero reading as a pcrec defect)" ;;
            "K41 oversize artifact")
                note=" (docs/dev/known_issues.md K41 -- classified by emitted-artifact SIZE, deterministic per --seed, NOT by gcc CPU-time outcome; witness: $k41_witness)" ;;
        esac
        echo "  $label: expected=$expected actual=$actual  DRIFT$note" >&2
        drift=1
    else
        echo "  $label: $actual"
    fi
done

# K41's witness, named regardless of pass/fail (not only in a DRIFT message)
# so a green run still shows which pattern the deterministic size bucket is
# keyed on this seed -- gcc's own outcome on it (compiled / over-budget on
# THIS box) is informational only, never a pass/fail signal (see the EXPECT
# comment above and fuzz.py's K41_OVERSIZE_BYTES comment).
if [ -n "$k41_witness" ]; then
    echo "  K41 witness: $k41_witness"
fi

[ "$drift" -ne 0 ] && rc=1

if [ "$rc" -eq 0 ]; then
    echo "capturediff-gate: PASS (seed=$GATE_SEED patterns=$GATE_PATTERNS subjects=$GATE_SUBJECTS, every selected count matched its pinned value)"
else
    echo "capturediff-gate: FAIL — see drift/divergences above; repro bundle path is in fuzz.py's own output" >&2
fi
exit "$rc"
