#!/usr/bin/env bash
# tests/codegen/run_inline_capability.sh — [CC-DIFF] STEP 2's CAPABILITY
# PROBE: does the compiler that is about to build this artifact already
# inline the VM entry chain, or does it need the workaround?
#
# =========================================================================
# THE QUESTION, AND WHY NO PREPROCESSOR GUARD CAN ANSWER IT
# =========================================================================
# [CC-DIFF] STEP 0 (`docs/dev/ccdiff_step0.md` §3-6) found the bench ledger's
# forced-VM signal to be ONE transformation: clang inlines the emitted chain
# `<prefix>_search` -> `<prefix>_search_run` -> `<prefix>_match_anchored` and
# then proves a frameless artifact's working storage dead; gcc 15 stops at
# the first call boundary, so every search call builds a 152-byte frame, pays
# a `-fstack-protector-strong` canary and calls out of line for storage the
# artifact never touches. STEP 1(a) spells `always_inline` on those helpers,
# gated on the frameless predicate, which takes gcc to clang's shape.
#
# THE ATTRIBUTE IS UNCONDITIONAL ON A FRAMELESS VM ARTIFACT. It is harmless
# under a compiler that was already doing this — the attribute only CONSTRAINS
# a decision clang makes on its own — but nothing in the tree says WHETHER it
# is doing anything under the compiler at hand. Frank asked for that guard
# (2026-09-03 23:0x) and the honest answer is that a preprocessor test cannot
# give it: `__has_attribute(always_inline)` says the attribute is UNDERSTOOD,
# not that the inlining WOULD HAVE HAPPENED without it. The capability is
# observable only in OBJECT CODE, which is what this file reads.
#
# =========================================================================
# THE METHOD: ONE WITNESS, TWO ARMS, `nm`
# =========================================================================
# Compile one frameless witness twice with the harness's own CC:
#
#   ARM A  as emitted at rung INLINE  — the attribute present
#   ARM B  the same source with the attribute REMOVED
#
# and ask `nm` whether `<prefix>_search_run` and `<prefix>_match_anchored`
# survive as local symbols. STEP 0's own witness is exactly this: on the
# loglines `stack-frame` artifact `nm` lists `rx_search_run` in the gcc build
# and NO such symbol in the clang build.
#
#   ARM B has NO chain symbols   -> the compiler inlined the chain unaided.
#                                   The workaround is REDUNDANT under it.
#   ARM B has chain symbols      -> it did not. The workaround is NEEDED.
#
# =========================================================================
# ARM B IS BUILT TWO WAYS AND THE TWO MUST AGREE
# =========================================================================
# docs/dev/learnings.md §3: a control that shares a source with what it
# controls proves nothing. Arm B's obvious spelling is the emitter's own
# no-attribute rung (`--vm-entry-shape=1`, PLAIN) — which is CONVENIENT and
# is the thing under test's own author. So this file ALSO builds arm B by
# a TEXTUAL removal of the attribute from arm A's emitted source, a
# transformation that knows nothing about the emitter, and asserts the two
# spellings are byte-identical before either is compiled.
#
# MEASURED at the probe's landing: `--vm-entry-shape=1` and
# `sed 's/inline __attribute__((always_inline)) //'` applied to
# `--vm-entry-shape=4` differ in NOTHING but the `#include` of the paired
# header and the `<PREFIX>_VM_ENTRY_SHAPE` stamp — and the stamp differing is
# REQUIRED rather than excused, since its whole job is to name the rung, so it
# is asserted positively below rather than merely ignored. If a future rung
# makes them differ for some THIRD reason, this file says so LOUDLY rather
# than quietly preferring one.
#
# =========================================================================
# THIS IS A CENSUS LINE, NOT A PIN
# =========================================================================
# The verdict is PRINTED with the compiler's version and is NEVER a failure
# in either direction. "REDUNDANT" is not a defect — it is the compiler
# having caught up, and the attribute costs it nothing. "NEEDED" is not a
# defect either — it is why STEP 1(a) exists. Pinning either would make this
# file go red on a compiler upgrade that changed nothing about pcrec, which
# is the opposite of what a capability probe is for.
#
# IT IS RED ON EXACTLY TWO THINGS, and both are failures of the PROBE rather
# than verdicts:
#   (1) the witness stopped being frameless — then the artifact carries no
#       attribute at all and the probe measured nothing (the [MECH-REACH]
#       shape: a witness that stopped reaching its site);
#   (2) the symbol table could not be read, the two arm-B spellings disagree
#       beyond the two normalised lines, or either arm did not get the rung it
#       asked for — then the answer, whatever it printed, is not evidence.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
NM="${NM:-nm}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run

# THE WITNESS. A frameless VM artifact whose chain is worth inlining: no
# push, no linked call, and (so the forward rungs are not what is being
# measured) rung INLINE requested explicitly. `\d{1,16}` is [CC-DIFF] STEP
# 0's own `dig-upto-16` cell, the one the 0.611 ratio was measured on, so
# the probe and the measurement that motivated it read the same program.
WITNESS_PAT='\d{1,16}'
WITNESS_LBL='dig-upto-16'

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "inline-capability: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

fail=0
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: inline-capability: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

echo "== [CC-DIFF] STEP 2 capability probe =="
echo "compiler  : $($CC --version 2>/dev/null | head -1)"
echo "witness   : $WITNESS_LBL   '$WITNESS_PAT'   --engine=vm --vm-entry-shape=4"

# ---- emit arm A (attribute present) and the emitter's own arm B ----------
A="$WORKDIR/arm_a.c"
Bemit="$WORKDIR/arm_b_emitter.c"
Bsed="$WORKDIR/arm_b_textual.c"

pcrec_run "$PCREC" -p rx --features all --engine=vm --vm-entry-shape=4 \
    -o "$A" -- "$WITNESS_PAT" >/dev/null 2>&1 \
    || { bad "the witness did not compile at rung INLINE"; exit 1; }
pcrec_run "$PCREC" -p rx --features all --engine=vm --vm-entry-shape=1 \
    -o "$Bemit" -- "$WITNESS_PAT" >/dev/null 2>&1 \
    || { bad "the witness did not compile at rung PLAIN"; exit 1; }

# (1) THE WITNESS MUST STILL BE FRAMELESS, or nothing below measures anything.
fl="$(grep -m1 '^#define RX_VM_FRAMELESS ' "$A" | awk '{print $3}')"
if [ "${fl:-}" != "1" ]; then
    bad "the witness stamps RX_VM_FRAMELESS ${fl:-<absent>}, not 1 — a framed artifact takes no attribute, so this probe measured nothing. Replace the witness with a frameless pattern."
    exit 1
fi
if ! grep -q 'always_inline' "$A"; then
    bad "the witness is frameless but its emitted source carries no always_inline — the site this probe exists to measure is gone"
    exit 1
fi

# (2) THE TWO ARM-B SPELLINGS MUST AGREE, AND EXACTLY TWO LINES MAY DIFFER.
#
# The `#include` of the paired header names the output file, so it
# legitimately differs. So does `<PREFIX>_VM_ENTRY_SHAPE`: the two arms are
# emitted at DIFFERENT RUNGS (4 and 1), and that stamp's whole job is to say
# which — a run where it did NOT differ would mean the emitter had stopped
# distinguishing them. Both are normalised out here and then asserted
# POSITIVELY below, so neither is excused, and any THIRD differing line is a
# failure: the textual arm B is the emitter arm B's control precisely because
# nothing else in the two files moves.
#
# MEASURED at the probe's landing: with those two normalised, the files are
# byte-identical — `--vm-entry-shape=1` really is `--vm-entry-shape=4` with
# the attribute deleted.
norm() { sed -e 's/arm_b_textual/ARM/g; s/arm_b_emitter/ARM/g; s/arm_a/ARM/g' \
             -e '/^#define RX_VM_ENTRY_SHAPE /d' "$1"; }
sed 's/inline __attribute__((always_inline)) //' "$A" > "$Bsed"
[ -f "${A%.c}.h" ] && cp "${A%.c}.h" "${Bsed%.c}.h"
if ! diff -q <(norm "$Bsed") <(norm "$Bemit") >/dev/null; then
    bad "arm B's two spellings disagree beyond the header include and the entry-shape stamp — the emitter's PLAIN rung is no longer 'arm A with the attribute removed', so neither is a control for the other. Diff them before trusting any verdict."
    diff <(norm "$Bsed") <(norm "$Bemit") | head -20 >&2
fi

# ...and the stamp that was normalised out is asserted POSITIVELY, so the
# exclusion above can never hide a rung the emitter stopped distinguishing.
shape_a="$(grep -m1 '^#define RX_VM_ENTRY_SHAPE ' "$A" | awk '{print $3}')"
shape_b="$(grep -m1 '^#define RX_VM_ENTRY_SHAPE ' "$Bemit" | awk '{print $3}')"
[ "$shape_a" = '"inline"' ] || bad "arm A stamps RX_VM_ENTRY_SHAPE $shape_a, expected \"inline\" — the probe asked for rung 4 and did not get it"
[ "$shape_b" = '"plain"' ]  || bad "arm B stamps RX_VM_ENTRY_SHAPE $shape_b, expected \"plain\" — the probe asked for rung 1 and did not get it"

# ---- compile both arms and read the symbol table -------------------------
chain_syms() {  # chain_syms <object> -> the surviving chain symbols, one per line
    "$NM" "$1" 2>/dev/null | awk '$3 == "rx_search_run" || $3 == "rx_match_anchored" { print $3 }' | sort
}

for arm in a b_emitter b_textual; do
    src="$WORKDIR/arm_$arm.c"
    [ -f "$src" ] || continue
    if ! $CC -O2 -std=gnu11 -c -o "$WORKDIR/arm_$arm.o" "$src" >"$WORKDIR/arm_$arm.log" 2>&1; then
        bad "arm $arm did not compile under $CC — see $WORKDIR/arm_$arm.log"
        exit 1
    fi
done

symsA="$(chain_syms "$WORKDIR/arm_a.o")"
symsB="$(chain_syms "$WORKDIR/arm_b_emitter.o")"
symsBt="$(chain_syms "$WORKDIR/arm_b_textual.o")"

# (3) `nm` MUST HAVE WORKED. An object with no symbols at all is a read
# failure, not a verdict: every artifact defines its exported entries.
for o in arm_a arm_b_emitter; do
    if ! "$NM" "$WORKDIR/$o.o" 2>/dev/null | grep -q ' rx_search$'; then
        bad "$NM could not read $o.o (no rx_search symbol) — no verdict is evidence here"
        exit 1
    fi
done

echo "arm A (attribute present)   chain symbols: ${symsA:-<none>}"
echo "arm B (attribute removed)   chain symbols: ${symsB:-<none>}"
if [ "$symsB" != "$symsBt" ]; then
    bad "arm B's two spellings produced DIFFERENT symbol tables (emitter '${symsB:-<none>}' vs textual '${symsBt:-<none>}') — the control and the subject are not the same program"
fi

# ---- the verdict, printed, never pinned ----------------------------------
ccver="$($CC --version 2>/dev/null | head -1)"
if [ -z "$symsB" ]; then
    echo "VERDICT: the always_inline workaround is REDUNDANT under $ccver"
    echo "         (the chain inlined with no help; the attribute constrains a"
    echo "          decision this compiler already makes, and costs it nothing)"
else
    echo "VERDICT: the always_inline workaround is NEEDED under $ccver"
    echo "         (without it, $(echo "$symsB" | tr '\n' ' ')stayed out of line)"
fi
if [ -n "$symsA" ]; then
    echo "NOTE   : the attribute did not remove ${symsA} — gcc honours"
    echo "         always_inline at every CALL SITE but may still emit an"
    echo "         out-of-line copy where one is addressed."
fi

if [ "$fail" -eq 0 ]; then
    echo "inline-capability: OK (census line printed; this check does not pin a verdict)"
    exit 0
fi
echo "inline-capability: $fail probe failure(s)" >&2
exit 1
