#!/usr/bin/env bash
# tests/codegen/run_tiered_entry.sh — [OPT-1]: the TWO-TIER DEFAULT ENTRY,
# held to the three things it claims.
#
# ON DEMAND (`make test-tiered-entry`), not part of `make test`: §2's sweep
# compiles the whole .rxt corpus and §3 builds and runs four matchers. The
# behavioural half that DOES ride `make test` is the corpus itself — every
# existing differential already compares answers through the un-suffixed
# entries, and this change either leaves them all green or is wrong.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# docs/design/two_tier_entry.md. An un-suffixed entry
# (`<prefix>_search`/`_match`/`_match_caps`) on a TIERED artifact runs the
# match on a small page-budgeted `<prefix>_fast_buffers` and, on
# `PCREC_ERR_FRAMES` and nothing else, calls a `noinline` `<name>_deep` static
# that owns the stamped default and re-runs the match from scratch. Three
# claims, and each gets its own section:
#
#   1. THE SHAPE IS WHAT THE STAMPS SAY (§2). `<PREFIX>_FAST_FRAMES` equals
#      `<PREFIX>_RESUME_FRAMES` exactly when the artifact has ONE tier, and
#      the emitted CODE agrees with that in both directions.
#   2. THE FRAME ACTUALLY MOVED (§4). The entry's own stack frame is under one
#      4 KB guard page and the deep static's carries the default storage.
#      This is the only thing that makes the change worth making, and it is
#      gcc's measurement, not the emitter's arithmetic.
#   3. THE ANSWERS DID NOT MOVE, ACROSS THE BOUNDARY (§3). Every subject's
#      answer equals the single-tier execution's, and the deep tier is entered
#      exactly when it should be.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3. The failure this file is built against is specific
# and was named before the code was written: **an answers-only check for this
# change passes on a build where the optimization is absent.** An artifact
# whose fast tier is secretly bound at the stamped default answers every
# subject correctly and escalates never — the identity claim holds and the
# change does nothing. That is why §3 does not stop at answers, and why §4
# exists at all.
#
# So the tier boundary is derived THREE ways per subject (tier_driver.c's
# header spells them out): the escalation counted at the escalation site
# itself; the give-up predicted by `<prefix>_search_in` at the FAST capacities,
# which is the same capacity guard reached through an entry [OPT-1] does not
# touch; and the answer compared against `_in` at the DEFAULT capacities, which
# IS the single-tier execution. A fast tier bound at the wrong capacity moves
# the prediction without moving the count; a broken escalation test moves the
# count without moving the prediction; a missing optimization moves neither and
# is caught by §4's frame.
#
# AND THE DEPTHS ARE FOUND, NOT ASSUMED (§3). The five boundary subjects the
# design asks for — 1, FAST-1, FAST, FAST+1 and the DEFAULT boundary — are
# located by BISECTING through `<prefix>_search_in`, so a change to the frame
# layout, the budget or `vm_cost`'s ratios moves the depths this file tests
# instead of leaving it testing depths that are no longer boundaries. A
# hardcoded `9` would be green forever and mean nothing after the first
# re-sizing.
#
# =========================================================================
# VALIDATION — every check below was made to FAIL on purpose
# =========================================================================
# Recorded per section, in the section. The planted defects were applied to a
# scratch copy of src/gen/emit_vm.c, measured, and removed; none was committed.
#
# Usage: bash tests/codegen/run_tiered_entry.sh
# Env:   PCREC (default <root>/build/pcrec), CC (default gcc), KEEP=1,
#        PROCS (default 4; the corpus sweep in §2)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"   # [K37] pcrec_run, TIMEOUT_BIN
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
PROCS="${PROCS:-4}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "tiered-entry: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: tiered-entry: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# The specimen: `fb_exact_driver.c`'s, so the two files agree on what a
# subject of depth n costs (2.000 resume frames, 8.982 trail entries per
# level — docs/design/frame_buffer_design.md §4).
SPECIMEN='^(a(?1)?b)$'
SPECIMEN_FLAGS="--features recursion"

# ===========================================================================
# §1 — the specimen's four builds
# ===========================================================================
build() {   # build <name> <extra pcrec flags...>
    local name="$1"; shift
    local d="$WORKDIR/$name"
    mkdir -p "$d"
    pcrec_run "$PCREC" -p rx --engine=vm $SPECIMEN_FLAGS "$@" \
        -o "$d/gen.c" -- "$SPECIMEN" >"$d/pcrec.log" 2>&1
}

if ! build tiered; then
    bad "tiered-entry: could not compile the specimen '$SPECIMEN' — every section below is unmeasured: $(head -3 "$WORKDIR/tiered/pcrec.log")"
    echo; echo "== Summary =="; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if ! build denied -fno-tiered-entry; then
    bad "tiered-entry: could not compile the specimen with -fno-tiered-entry — §5's differential is unmeasured: $(head -3 "$WORKDIR/denied/pcrec.log")"
fi

# The two FAST capacities are `.c`-private VM capacity stamps (match_api.md
# §6.3(b)), so they are read out of the ARTIFACT here and handed to the driver
# as -D. That is deliberate and not a workaround: a driver that could see them
# through the header would be reading a caller-facing macro, and they are not
# one — nothing a caller does depends on where the tier boundary sits.
stamp() { awk -v k="$2" '$1 == "#define" && $2 == k { print $3 }' "$1" | head -1; }

FF="$(stamp "$WORKDIR/tiered/gen.c" RX_FAST_FRAMES)"
FT="$(stamp "$WORKDIR/tiered/gen.c" RX_FAST_TRAIL)"
RF="$(stamp "$WORKDIR/tiered/gen.c" RX_RESUME_FRAMES)"
RT="$(stamp "$WORKDIR/tiered/gen.c" RX_TRAIL_FRAMES)"
if [ -z "$FF" ] || [ -z "$FT" ] || [ -z "$RF" ] || [ -z "$RT" ]; then
    # RESUME_FRAMES/TRAIL_FRAMES live in the .h since [DD-14.FB]; look there too.
    [ -n "$RF" ] || RF="$(stamp "$WORKDIR/tiered/gen.h" RX_RESUME_FRAMES)"
    [ -n "$RT" ] || RT="$(stamp "$WORKDIR/tiered/gen.h" RX_TRAIL_FRAMES)"
fi
if [ -z "$FF" ] || [ -z "$FT" ] || [ -z "$RF" ] || [ -z "$RT" ]; then
    bad "tiered-entry: the specimen's artifact does not carry all four capacity stamps (FAST_FRAMES='$FF' FAST_TRAIL='$FT' RESUME_FRAMES='$RF' TRAIL_FRAMES='$RT') — nothing below can be computed, so nothing below is claimed"
    echo; echo "== Summary =="; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

if [ "$FF" -lt "$RF" ] && [ "$FT" -lt "$RT" ]; then
    ok "tiered-entry: the specimen IS tiered — fast $FF/$FT against a stamped default of $RF/$RT, so §3 and §4 have a two-tier artifact to measure"
else
    bad "tiered-entry: the specimen '$SPECIMEN' compiled SINGLE-TIER (fast $FF/$FT, default $RF/$RT). It is chosen precisely because its default is far over the page budget; if it no longer tiers, either VM_FAST_TIER_BYTES or the frame layout moved and every section below would be measuring the wrong shape"
fi

# ===========================================================================
# §2 — THE SHAPE IS WHAT THE STAMPS SAY, over the whole corpus
# ===========================================================================
# The population is every `pattern` line in every .rxt file under tests/, the
# same population `run_vm_identity.sh` uses, so it grows with the corpus and
# not with this script. Its count is PRINTED.
#
# THE BICONDITIONAL IS THE CHECK, in both directions:
#   tiered code present  <=>  FAST_FRAMES < RESUME_FRAMES
# A stamp that claims a tier the code does not have, and code that tiers
# without saying so, are both red. Checking one direction only is how a stamp
# becomes decoration.
#
# THE ENGINE DISCRIMINATOR IS THE PROGRAM, not `RX_ENGINE` — `goto rx_L0;`,
# the same marker run_recursion_identity.sh and run_dfa_stamps.sh use. Reading
# a stamp to decide which artifact to check the stamps of is the circularity
# [DD-13] had to go back and remove from two checks.
#
# VALIDATION (MEASURED 2026-08-25, planted in a scratch emitter, then removed):
#   (i)  stamp FAST unconditionally at the default while still emitting the
#        tiered code -> **272 artifacts RED** on `mismatch-code-tiers-stamp-
#        says-one`, i.e. every tiered artifact in the corpus, AND the
#        non-empty-population arm below fires too ("NOT ONE corpus pattern
#        compiled to a tiered artifact"), which is the guard against this
#        section passing vacuously. §4 goes red as well, because the stamps
#        also SIZE `<prefix>_fast_buffers`.
#   (ii) bind the STAMPED DEFAULT in the fast tier, leaving the stamps alone
#        ("it never escalates") -> §2 stays **GREEN** and §3(a)'s answers stay
#        **GREEN**; only §3(b) (2 of 6 depths) and §4 go red. That is exactly
#        why §4 is a separate section and not a footnote here, and why §3
#        counts escalations instead of trusting answers.
echo
echo "-- §2: the shape agrees with the stamps, over the corpus --"

CORPUS="$WORKDIR/patterns.txt"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
  | xargs -0 grep -h '^pattern ' 2>/dev/null \
  | sed 's/^pattern //' | LC_ALL=C sort -u > "$CORPUS"
NPAT=$(wc -l < "$CORPUS")
echo "population: $NPAT distinct corpus patterns"

if [ "$NPAT" -lt 100 ]; then
    bad "§2: only $NPAT patterns were collected from tests/**/*.rxt — the sweep's population collapsed, and a sweep over nothing is not evidence"
else
    # One artifact per pattern, classified by ONE awk pass over its text.
    # Emits: <kind> for each pattern, where kind is one of
    #   dfa | vm-one-tier | vm-tiered | mismatch-<why> | refused
    classify() {
        local pat="$1" d="$2"
        if ! pcrec_run "$PCREC" -p rx --features all -o "$d/g.c" -- "$pat" \
                >/dev/null 2>&1; then
            echo refused; return
        fi
        cat "$d/g.c" "$d/g.h" 2>/dev/null | awk '
            /^    goto rx_L0;$/                          { vm = 1 }
            /^static __attribute__\(\(noinline\)\) .*_deep\(/ { deep++ }
            /^} rx_fast_buffers;$/                       { fastbuf = 1 }
            /^#define RX_TIER_NOTE\(\)/                  { note++ }
            $1 == "#define" && $2 == "RX_FAST_FRAMES"    { nff++; ff = $3 }
            $1 == "#define" && $2 == "RX_FAST_TRAIL"     { nft++; ft = $3 }
            $1 == "#define" && $2 == "RX_RESUME_FRAMES"  { rf = $3 }
            $1 == "#define" && $2 == "RX_TRAIL_FRAMES"   { rt = $3 }
            $1 == "#define" && $2 == "RX_RESUME_FRAME_SIZE" { fsz = $3 }
            $1 == "#define" && $2 == "RX_TRAIL_FRAME_SIZE"  { tsz = $3 }
            $1 == "#define" && $2 == "RX_NSLOTS"            { nsl = $3 }
            END {
                if (!vm) { print (nff || nft) ? "mismatch-dfa-carries-fast-stamp" : "dfa"; exit }
                if (nff != 1 || nft != 1) { print "mismatch-vm-missing-fast-stamp"; exit }
                if (ff+0 > rf+0 || ft+0 > rt+0) { print "mismatch-fast-over-default"; exit }
                code   = (deep == 3 && fastbuf && note == 2)
                partial = (!code && (deep || fastbuf || note))
                stamped = (ff+0 < rf+0)
                if (partial)             { print "mismatch-partial-tier-code"; exit }
                if (code && !stamped)    { print "mismatch-code-tiers-stamp-says-one"; exit }
                if (!code && stamped)    { print "mismatch-stamp-tiers-code-does-not"; exit }
                # The SIZING FACTS ride the kind, so the FLOOR check below reads
                # them off the artifact rather than re-deriving them (r38 3a).
                # NO APOSTROPHES IN THIS AWK PROGRAM: it is single-quoted in the
                # shell, so one would close the quote (it did, once).
                printf "%s %d %d %d %d %d\n", (code ? "vm-tiered" : "vm-one-tier"),
                       ff+0, ft+0, fsz+0, tsz+0, nsl+0
            }'
    }
    export -f classify pcrec_run 2>/dev/null || true

    : > "$WORKDIR/kinds.txt"
    idx=0
    while IFS= read -r pat; do
        idx=$((idx + 1))
        d="$WORKDIR/sweep/$((idx % PROCS))"
        mkdir -p "$d"
        classify "$pat" "$d" >> "$WORKDIR/kinds.txt"
    done < "$CORPUS"

    NDFA=$(grep -c '^dfa$'         "$WORKDIR/kinds.txt" || true)
    NONE=$(grep -c '^vm-one-tier ' "$WORKDIR/kinds.txt" || true)
    NTIER=$(grep -c '^vm-tiered '  "$WORKDIR/kinds.txt" || true)
    NREF=$(grep -c '^refused$'     "$WORKDIR/kinds.txt" || true)
    NBAD=$(grep -c '^mismatch-'    "$WORKDIR/kinds.txt" || true)
    echo "classified: $NDFA dfa, $NONE vm single-tier, $NTIER vm tiered, $NREF refused, $NBAD mismatched"

    if [ "$NBAD" -ne 0 ]; then
        bad "§2: $NBAD artifacts disagree with their own stamps: $(grep '^mismatch-' "$WORKDIR/kinds.txt" | LC_ALL=C sort | uniq -c | tr '\n' ' ')"
    else
        ok "§2: on all $NPAT corpus patterns the emitted code and the FAST stamps agree in BOTH directions — every VM artifact carries exactly one of each stamp, no FAST capacity exceeds its default, no DFA artifact carries one, and the tiered code is present exactly where FAST < RESUME ($NTIER tiered, $NONE single-tier)"
    fi
    # ---- THE FLOOR (r38 finding 3a) --------------------------------------
    # EVERYTHING ABOVE BOUNDS THE FAST TIER FROM ABOVE ONLY. `FAST <= RESUME`,
    # the biconditional, the frame check in §4 — every one of them stays GREEN
    # if the derivation shrinks. A fast tier of 2 frames still tiers, still
    # stamps honestly, still fits a page, and still answers correctly; it just
    # escalates on everything and makes the optimization a pessimisation. That
    # degradation is invisible to every check written so far, because the stamp
    # and the bind move TOGETHER and this file reads both. So the floor is
    # asserted three ways, and the middle one is the real defence.
    #
    # THE BUDGET CONSTANTS ARE SPELLED HERE, deliberately, so this file states
    # the contract it checks rather than accepting whatever the emitter says —
    # run_dfa_stamps.sh's documented-value-set precedent. They must be updated
    # DELIBERATELY, in the same change as `src/gen/emit_vm.c`.
    # VALIDATION (MEASURED 2026-08-26, planted in a scratch emitter and
    # removed): halve the derivation — `ff = ... / 2`, `ft = ... / 2`, so the
    # STAMP AND THE BIND MOVE TOGETHER, which is exactly the degradation this
    # floor exists for and exactly what every other check in this file is blind
    # to. OBSERVED: `FAIL: §2(floor B): 271 of 271 tiered artifacts have a fast
    # tier that does NOT fill its budget (first three: ff=23 ft=35 used=1480
    # avail=3032 ...)` with **checks passed: 16, checks failed: 1** — floor B
    # alone. §2's biconditional, floors A and C, §3, §4, §5 and §6 all stayed
    # GREEN, and every answer and span stayed correct. (271 not 272 because one
    # pattern fell below FAST_MIN under the plant and correctly went
    # single-tier.) A quarter-size plant instead trips FAST_MIN and drops the
    # specimen to single-tier, which §1 reports first.
    FAST_BUDGET=3072       # VM_FAST_TIER_BYTES
    FAST_MIN=16            # VM_FAST_TIER_MIN
    TIER_FLOOR=250         # measured 272 at this commit; see below
    if [ "$NTIER" -eq 0 ]; then
        bad "§2: NOT ONE corpus pattern compiled to a tiered artifact, so the biconditional above was only ever checked on its trivial side — the sweep's population for the interesting case is empty and the PASS above would be vacuous"
    elif [ "$NTIER" -lt "$TIER_FLOOR" ]; then
        bad "§2(floor A): only $NTIER of $NPAT corpus patterns tier, below the floor of $TIER_FLOOR (measured 272 when this check was written). Either the corpus lost its deep-sized patterns or the derivation stopped tiering artifacts it used to — a shrinking population is the check that cannot fail, so this is a failure rather than a note"
    else
        ok "§2(floor A): the tiered side of the biconditional has a real population — $NTIER of $NPAT corpus patterns tier, at or above the floor of $TIER_FLOOR"
    fi

    # (floor B) THE FAST TIER MUST FILL ITS BUDGET, to within one frame plus one
    # trail entry of the integer division's rounding. This is the assertion that
    # catches a shrunken derivation, and it is derivation-INDEPENDENT: it does
    # not re-implement the scaling, it states the PROPERTY the scaling exists to
    # produce — "as much capacity as one page can hold". A fast tier at half the
    # budget passes every other check in this file and fails this one.
    #
    #     avail = FAST_BUDGET - NSLOTS*sizeof(ptrdiff_t)
    #     used  = FAST_FRAMES*RESUME_FRAME_SIZE + FAST_TRAIL*TRAIL_FRAME_SIZE
    #     used <= avail   (the page budget, which §4 also measures for real)
    #     used >= avail - (RESUME_FRAME_SIZE + TRAIL_FRAME_SIZE)   (the floor)
    # The message reports a COUNT and three EXAMPLES, not every offender: this
    # arm goes red on the WHOLE population when the derivation shrinks (272 of
    # 272, measured), and 272 rows on one line is unreadable. Validated that
    # way round on purpose — see the plant below.
    awk -v B="$FAST_BUDGET" '
        $1 == "vm-tiered" {
            ff=$2; ft=$3; fsz=$4; tsz=$5; nsl=$6
            avail = B - nsl*8
            used  = ff*fsz + ft*tsz
            if (used > avail || used < avail - (fsz+tsz))
                printf "ff=%d ft=%d used=%d avail=%d\n", ff, ft, used, avail
        }' "$WORKDIR/kinds.txt" > "$WORKDIR/underfilled.txt"
    NUNDER=$(wc -l < "$WORKDIR/underfilled.txt")
    if [ "$NUNDER" -eq 0 ]; then
        ok "§2(floor B): all $NTIER tiered artifacts fill their page budget to within one frame + one trail entry of the integer rounding — the fast tier is as large as one $FAST_BUDGET B budget allows, not merely small enough to fit"
    else
        bad "§2(floor B): $NUNDER of $NTIER tiered artifacts have a fast tier that does NOT fill its budget (first three: $(head -3 "$WORKDIR/underfilled.txt" | tr '\n' '; ')) — a fast tier below its budget escalates more often than it needs to and turns the optimization into a pessimisation, while passing every other check in this file"
    fi

    # (floor C) AND NOTHING TIERS BELOW THE EMITTER's OWN MINIMUM, read back off
    # the artifact. `VM_FAST_TIER_MIN` is the emitter's rule that a tier this
    # small is not worth two runs; this asserts the rule reached the output.
    TOOSMALL=$(awk -v M="$FAST_MIN" '$1 == "vm-tiered" && ($2 < M || $3 < M) {printf "%d/%d; ", $2, $3}' "$WORKDIR/kinds.txt")
    if [ -z "$TOOSMALL" ]; then
        ok "§2(floor C): no tiered artifact carries a fast capacity below VM_FAST_TIER_MIN ($FAST_MIN) — the emitter's own give-up-and-stay-single-tier rule reached the emitted output"
    else
        bad "§2(floor C): tiered artifacts below VM_FAST_TIER_MIN ($FAST_MIN): $TOOSMALL — the emitter emitted a tier it should have declined"
    fi
fi

# `-fno-tiered-entry` must land a would-be-tiered pattern on the single-tier
# shape. This is D46's controllability half, checked rather than asserted.
if [ -f "$WORKDIR/denied/gen.c" ]; then
    DFF="$(stamp "$WORKDIR/denied/gen.c" RX_FAST_FRAMES)"
    DDEEP=$(grep -c '^static __attribute__((noinline)) .*_deep(' "$WORKDIR/denied/gen.c" || true)
    if [ "$DFF" = "$RF" ] && [ "$DDEEP" -eq 0 ]; then
        ok "§2: -fno-tiered-entry denies the tier on a pattern that otherwise takes it — FAST_FRAMES $DFF == RESUME_FRAMES $RF and no _deep static, i.e. the shape that shipped before [OPT-1]"
    else
        bad "§2: -fno-tiered-entry did not produce the single-tier shape (FAST_FRAMES=$DFF against RESUME_FRAMES=$RF, $DDEEP _deep statics). The flag is the bisect lever and the identity gates' way back to the old entry; a denial that does not deny is worse than no flag"
    fi
fi

# ===========================================================================
# §3 — THE ANSWERS DID NOT MOVE, ACROSS THE TIER BOUNDARY
# ===========================================================================
# The depths are FOUND by bisecting through `<prefix>_search_in`, not assumed
# from the ratios: see this file's header. `bisect` prints the largest n that
# still MATCHES at a given capacity, so the boundary is (n, n+1).
#
# VALIDATION (MEASURED 2026-08-25, planted then removed): bind the DEFAULT
# capacity in the fast tier while leaving the stamps alone — "the fast tier
# never escalates". OBSERVED: `FAIL: §3(b): 2 of 6 depths escalated when they
# should not have, or did not when they should: n=9 esc=0 predicted=1; n=342
# esc=0 predicted=1`. Meanwhile §3(a) passed on all 6 depths — every ANSWER,
# the n=342 one included, stayed correct. That is the measured proof that an
# answers-only check for this change goes green on a build where the
# optimization is absent, which is why this section counts escalations.
echo
echo "-- §3: answers and escalations across the boundary --"

cat > "$WORKDIR/bisect.c" <<'EOF'
/* Largest n whose a^n b^n still MATCHES at a given capacity, by linear walk
 * from 1 (the answer is monotone in n: more depth needs more frames). Printed
 * so run_tiered_entry.sh can site its boundary subjects on the real boundary
 * rather than on a remembered one. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
int main(int argc, char **argv)
{
    size_t nf, nt, n;
    if (argc != 3) return 2;
    nf = strtoull(argv[1], NULL, 10);
    nt = strtoull(argv[2], NULL, 10);
    for (n = 1; n < 100000; n++) {
        size_t len = 2 * n;
        unsigned char *s = malloc(len + 1);
        ptrdiff_t caps[RX_NCAPS][2];
        rx_buffers b;
        void *f = malloc(nf * (size_t)RX_RESUME_FRAME_SIZE);
        void *t = malloc(nt * (size_t)RX_TRAIL_FRAME_SIZE);
        int r;
        if (!s || !f || !t) return 2;
        memset(s, 'a', n); memset(s + n, 'b', n); s[len] = 0;
        b.frames = f; b.nframes = nf; b.trail = t; b.ntrail = nt;
        r = rx_search_in(s, len, 0, caps, &b);
        free(s); free(f); free(t);
        if (r != 1) { printf("%zu\n", n - 1); return 0; }
    }
    return 2;
}
EOF

D="$WORKDIR/tiered"
if ! (cd "$D" && $CC -O2 -I"$D" -o "$D/bisect" "$WORKDIR/bisect.c" "$D/gen.c") \
        >"$D/bisect.log" 2>&1; then
    bad "§3: could not build the boundary finder: $(head -3 "$D/bisect.log")"
elif ! (cd "$D" && $CC -O2 -I"$D" -DRX_TEST_TIER_HOOK \
            -DTIER_FAST_FRAMES="$FF" -DTIER_FAST_TRAIL="$FT" \
            -o "$D/tier" "$SCRIPT_DIR/tier_driver.c" "$D/gen.c") \
        >"$D/drv.log" 2>&1; then
    bad "§3: could not build tier_driver against the specimen: $(head -5 "$D/drv.log")"
else
    FAST_N="$("$TIMEOUT_BIN" 120 "$D/bisect" "$FF" "$FT")"
    DEF_N="$("$TIMEOUT_BIN" 120 "$D/bisect" "$RF" "$RT")"
    if [ -z "$FAST_N" ] || [ -z "$DEF_N" ] || [ "$FAST_N" -lt 1 ] || [ "$DEF_N" -le "$FAST_N" ]; then
        bad "§3: the boundary finder did not bracket two distinct tiers (fast='$FAST_N' default='$DEF_N') — with no boundary there is nothing to test across"
    else
        echo "boundaries found by bisection: fast tier holds n<=$FAST_N, stamped default holds n<=$DEF_N"
        # 1, FAST-1, FAST, FAST+1, DEFAULT, DEFAULT+1 — the five the design
        # asks for plus the give-up on the far side of the deep tier.
        DEPTHS="1 $((FAST_N - 1)) $FAST_N $((FAST_N + 1)) $DEF_N $((DEF_N + 1))"
        echo "depths: $DEPTHS"
        # shellcheck disable=SC2086
        "$TIMEOUT_BIN" 300 "$D/tier" anbn $DEPTHS > "$D/rows.txt" 2>"$D/rows.err"
        NROW=$(grep -c '^row ' "$D/rows.txt" || true)
        NWANT=$(printf '%s\n' $DEPTHS | wc -l)
        if [ "$NROW" -ne "$NWANT" ]; then
            bad "§3: tier_driver produced $NROW rows for $NWANT depths ($(head -2 "$D/rows.err")) — an incomplete run says nothing about the depths it did not reach"
        else
            echo "rows: $NROW"
            # (a) ANSWER IDENTITY: ans == ref on every row.
            NDIFF=$(awk '$3 != $4' "$D/rows.txt" | wc -l)
            if [ "$NDIFF" -eq 0 ]; then
                ok "§3(a): on all $NROW depths the TIERED entry's answer equals <prefix>_search_in's at the stamped default — the single-tier execution, reached through an entry [OPT-1] does not touch"
            else
                bad "§3(a): $NDIFF of $NROW depths answer differently through the tiered entry than through the default-sized _in: $(awk '$3 != $4 {printf "n=%s tiered=%s single-tier=%s; ", $2, $3, $4}' "$D/rows.txt")"
            fi
            # (b) THE TIER WAS ENTERED EXACTLY WHEN PREDICTED. `esc` is counted
            # at the escalation site; `pred` is the same capacity's give-up seen
            # through `_in`. Two sources, compared.
            NESC=$(awk '($5 > 0) != ($6 == 1)' "$D/rows.txt" | wc -l)
            NUP=$(awk '$6 == 1' "$D/rows.txt" | wc -l)
            if [ "$NUP" -eq 0 ]; then
                bad "§3(b): NOT ONE of the $NROW depths was predicted to escalate, so the escalation half of this section has no population and its verdict would be vacuous"
            elif [ "$NESC" -eq 0 ]; then
                ok "§3(b): the deep tier was entered on exactly the $NUP of $NROW depths at which <prefix>_search_in AT THE FAST CAPACITIES gives up, and on none of the others — the escalation counted at the site agrees with the boundary derived through the untouched _in entry"
            else
                bad "§3(b): $NESC of $NROW depths escalated when they should not have, or did not when they should: $(awk '($5 > 0) != ($6 == 1) {printf "n=%s esc=%s predicted=%s; ", $2, $5, $6}' "$D/rows.txt")"
            fi
            # (c) THE CAPTURE SPANS AGREE, not only the returns (r38 3b).
            # Design §6 and spec §10.9 promise both, and the spans are the half
            # a tier bug would land in: the deep tier re-runs from scratch, so
            # a lost copy-out — or the FAST attempt's untouched array returned
            # beside the DEEP attempt's return value — is invisible in `ans`.
            # The population is asserted NON-EMPTY: spans are only defined on a
            # match (§3.1 leaves `caps` untouched otherwise), so a run whose
            # depths all gave up would compare nothing and pass vacuously.
            NSP=$(awk '$7 == "1" || $7 == "0"' "$D/rows.txt" | wc -l)
            NSPBAD=$(awk '$7 == "0"' "$D/rows.txt" | wc -l)
            if [ "$NSP" -eq 0 ]; then
                bad "§3(spans): not one of the $NROW depths matched through BOTH entries, so no capture array was compared and this arm would pass vacuously"
            elif [ "$NSPBAD" -eq 0 ]; then
                ok "§3(spans): on all $NSP matching depths the TIERED entry's whole capture array is byte-identical to <prefix>_search_in's at the stamped default (memcmp over RX_NCAPS pairs, not a per-group loop)"
            else
                bad "§3(spans): $NSPBAD of $NSP matching depths returned the same value but DIFFERENT capture spans: $(awk '$7 == "0" {printf "n=%s; ", $2}' "$D/rows.txt")"
            fi
            # (d) THE DEEP TIER RE-RUNS ONCE, not repeatedly. A deep tier that
            # re-entered itself would still answer correctly.
            NMANY=$(awk '$5 > 1' "$D/rows.txt" | wc -l)
            if [ "$NMANY" -eq 0 ]; then
                ok "§3(d): no depth escalated more than once — one FRAMES give-up, one replay, and the deep tier does not re-enter the escalation path"
            else
                bad "§3(d): $NMANY depths escalated more than once: $(awk '$5 > 1 {printf "n=%s esc=%s; ", $2, $5}' "$D/rows.txt")"
            fi
        fi
    fi
fi

# ===========================================================================
# §4 — THE FRAME ACTUALLY MOVED (gcc's measurement, not the emitter's)
# ===========================================================================
# `VM_FAST_TIER_BYTES` is the emitter's CLAIM about the frame gcc will build.
# This is the frame gcc actually built. It is the only section that can tell a
# working optimization from an absent one, which is why the design puts the
# budget's justification here rather than in a comment beside the constant.
#
# ONE PAGE is the threshold because that is gcc's default stack-clash guard
# size (`--param stack-clash-protection-guard-size=12`), i.e. the granularity
# at which the probes this change exists to avoid are charged.
#
# VALIDATION (MEASURED 2026-08-25, planted then removed): bind the DEFAULT
# capacity in the fast tier — the same plant as §3's. OBSERVED: `rx_search`
# reads **131,248 B** against `rx_search_deep`'s 131,216, so BOTH arms below go
# RED, while §2 stays green and every answer stays correct. This is the only
# section that can tell a working optimization from an absent one.
echo
echo "-- §4: the entry's stack frame, off gcc -fstack-usage --"

PAGE=4096
SU="$WORKDIR/su"; mkdir -p "$SU"
if ! (cd "$SU" && $CC -O2 -fstack-usage -I"$D" -c -o "$SU/gen.o" "$D/gen.c") \
        >"$SU/build.log" 2>&1; then
    bad "§4: could not compile the specimen with -fstack-usage: $(head -3 "$SU/build.log")"
else
    # Rows are TAB-separated `file:line:col:function`, `bytes`, `qualifier`;
    # anchored on the function field so `rx_search_run`/`_in`/`_deep` cannot be
    # mistaken for `rx_search`, which is the whole point of the comparison.
    frame() { awk -F'\t' -v f=":$1\$" '$1 ~ f {print $2}' "$SU"/*.su | head -1; }
    E_FRAME="$(frame rx_search)"
    D_FRAME="$(frame rx_search_deep)"
    I_FRAME="$(frame rx_search_in)"
    if [ -z "$E_FRAME" ] || [ -z "$D_FRAME" ]; then
        bad "§4: gcc -fstack-usage produced no rx_search row (entry='$E_FRAME' deep='$D_FRAME') — this section cannot measure the thing the change exists to move, so it claims nothing"
    else
        echo "frames: rx_search=$E_FRAME rx_search_deep=$D_FRAME rx_search_in=${I_FRAME:-n/a} (guard page $PAGE)"
        if [ "$E_FRAME" -lt "$PAGE" ]; then
            ok "§4: the un-suffixed entry's frame is $E_FRAME B, inside one $PAGE B guard page — which is what takes gcc's stack-clash probe off every call, and is the whole of [OPT-1] STEP 2"
        else
            bad "§4: the un-suffixed entry's frame is $E_FRAME B, NOT inside one $PAGE B guard page. Either the fast tier is not bound to the FAST capacities, or VM_FAST_TIER_BYTES no longer leaves enough headroom for the run state, the ctx and the spills — measure before adjusting the constant, because the second reading needs a new number and the first is a defect"
        fi
        # The storage did not evaporate: it MOVED. Without this arm a fast tier
        # sized at zero would pass the arm above.
        if [ "$D_FRAME" -gt "$PAGE" ] && [ "$D_FRAME" -gt "$E_FRAME" ]; then
            ok "§4: the stamped default's storage is on the DEEP static's frame ($D_FRAME B) and not on the entry's ($E_FRAME B) — the pages moved to the escalation path rather than being given up, so D73's depth ceiling is intact"
        else
            bad "§4: the deep static's frame is $D_FRAME B against the entry's $E_FRAME B — the stamped default storage is not where it should be, and an entry that got small by losing capacity has broken D73's ceiling rather than moved its cost"
        fi
    fi
fi

# ===========================================================================
# §5 — THE DENIED BUILD ANSWERS IDENTICALLY (D46's differential)
# ===========================================================================
# `-fno-tiered-entry` builds the pre-[OPT-1] entry. Two DIFFERENT PROGRAMS
# BUILT BY THIS COMPILER that must agree on every answer — the same instrument
# `-fno-splice-calls` gives module `recursion` (§9.2's second control).
echo
echo "-- §5: -fno-tiered-entry answers identically --"

if [ ! -f "$WORKDIR/denied/gen.c" ]; then
    bad "§5: no -fno-tiered-entry build to compare against"
elif [ -z "${FAST_N:-}" ] || [ -z "${DEF_N:-}" ]; then
    bad "§5: §3 did not establish the boundaries, so this differential has no depths to run at"
else
    DD="$WORKDIR/denied"
    if ! (cd "$DD" && $CC -O2 -I"$DD" -DRX_TEST_TIER_HOOK \
              -DTIER_FAST_FRAMES="$FF" -DTIER_FAST_TRAIL="$FT" \
              -o "$DD/tier" "$SCRIPT_DIR/tier_driver.c" "$DD/gen.c") \
            >"$DD/drv.log" 2>&1; then
        bad "§5: could not build tier_driver against the denied artifact: $(head -5 "$DD/drv.log")"
    else
        # shellcheck disable=SC2086
        "$TIMEOUT_BIN" 300 "$DD/tier" anbn $DEPTHS > "$DD/rows.txt" 2>&1
        # Compare the ANSWER column only: the denied build has no tier, so its
        # escalation column is 0 everywhere BY CONSTRUCTION and comparing it
        # would be comparing the flag against itself.
        if diff <(awk '{print $2, $3}' "$D/rows.txt") \
                <(awk '{print $2, $3}' "$DD/rows.txt") >"$WORKDIR/denied.diff" 2>&1; then
            ok "§5: the tiered and -fno-tiered-entry builds return the same answer at all $(wc -l < "$D/rows.txt") depths, boundary depths included — two different programs from this compiler, one answer"
        else
            bad "§5: the tiered and denied builds DISAGREE: $(head -6 "$WORKDIR/denied.diff" | tr '\n' ' ')"
        fi
        NDESC=$(awk '$5 > 0' "$DD/rows.txt" | wc -l)
        if [ "$NDESC" -eq 0 ]; then
            ok "§5: the denied build escalated 0 times at every depth, as a build with no deep tier must"
        else
            bad "§5: the -fno-tiered-entry build escalated $NDESC times — it has no deep tier to escalate into, so the flag did not deny what it claims to"
        fi
    fi
fi

# ===========================================================================
# §6 — THE MULTI-GROUP WITNESS (r38 finding 3b)
# ===========================================================================
# The specimen has ONE group and its span is the whole match, so on it "the
# spans agree" is very nearly implied by "the returns agree" and §3(spans) is
# far weaker than it looks. `((a)|(aa))+b` has THREE groups, two of them
# alternation arms whose contents depend on the backtracking path taken — the
# thing a replay has to reproduce and the thing a not-quite-replay would get
# wrong while still returning 1.
#
# It also has a DIFFERENT subject shape (a^n b, where depth is the ITERATION
# count, not a nesting depth) and reaches the boundary at a ~24-BYTE subject,
# which is the fact §7 of the design note now states: "deep" is not a synonym
# for "large".
#
# The whole span of depths is swept, not five points: the boundary is cheap to
# cross here and a dense sweep is what makes "on every subject" a measurement.
echo
echo "-- §6: the multi-group witness, spans over a dense sweep --"

MG='((a)|(aa))+b'
MGD="$WORKDIR/multigroup"
mkdir -p "$MGD"
if ! pcrec_run "$PCREC" -p rx --engine=vm -o "$MGD/gen.c" -- "$MG" >"$MGD/pcrec.log" 2>&1; then
    bad "§6: could not compile the multi-group witness '$MG': $(head -3 "$MGD/pcrec.log")"
else
    MGFF="$(stamp "$MGD/gen.c" RX_FAST_FRAMES)"
    MGFT="$(stamp "$MGD/gen.c" RX_FAST_TRAIL)"
    MGRF="$(stamp "$MGD/gen.c" RX_RESUME_FRAMES)"
    [ -n "$MGRF" ] || MGRF="$(stamp "$MGD/gen.h" RX_RESUME_FRAMES)"
    MGNC="$(stamp "$MGD/gen.c" RX_NCAPS)"
    [ -n "$MGNC" ] || MGNC="$(stamp "$MGD/gen.h" RX_NCAPS)"
    if [ -z "$MGFF" ] || [ "$MGFF" -ge "$MGRF" ]; then
        bad "§6: the multi-group witness '$MG' is NOT tiered (FAST_FRAMES='$MGFF' against RESUME_FRAMES='$MGRF') — it is chosen because it tiers AND has several groups; if it stopped tiering this section is measuring the wrong shape"
    elif [ -z "$MGNC" ] || [ "$MGNC" -lt 4 ]; then
        bad "§6: the multi-group witness reports RX_NCAPS=$MGNC, fewer than the 4 (whole match + 3 groups) this section exists to exercise — a single-group witness cannot carry the span claim, which is the whole reason this section was added"
    elif ! (cd "$MGD" && $CC -O2 -I"$MGD" -DRX_TEST_TIER_HOOK \
                -DTIER_FAST_FRAMES="$MGFF" -DTIER_FAST_TRAIL="$MGFT" \
                -o "$MGD/tier" "$SCRIPT_DIR/tier_driver.c" "$MGD/gen.c") \
            >"$MGD/drv.log" 2>&1; then
        bad "§6: could not build tier_driver against the multi-group witness: $(head -5 "$MGD/drv.log")"
    else
        MGDEPTHS="$(seq 1 60 | tr '\n' ' ')"
        # shellcheck disable=SC2086
        "$TIMEOUT_BIN" 300 "$MGD/tier" anb $MGDEPTHS > "$MGD/rows.txt" 2>"$MGD/rows.err"
        MGROW=$(grep -c '^row ' "$MGD/rows.txt" || true)
        if [ "$MGROW" -ne 60 ]; then
            bad "§6: the multi-group driver produced $MGROW rows for 60 depths ($(head -2 "$MGD/rows.err")) — an incomplete run says nothing about the depths it did not reach"
        else
            MGDIFF=$(awk '$3 != $4' "$MGD/rows.txt" | wc -l)
            MGSP=$(awk '$7 == "1" || $7 == "0"' "$MGD/rows.txt" | wc -l)
            MGSPBAD=$(awk '$7 == "0"' "$MGD/rows.txt" | wc -l)
            MGESC=$(awk '($5 > 0) != ($6 == 1)' "$MGD/rows.txt" | wc -l)
            MGUP=$(awk '$6 == 1' "$MGD/rows.txt" | wc -l)
            MGFIRST=$(awk '$6 == 1 {print $2; exit}' "$MGD/rows.txt")
            echo "rows: $MGROW; RX_NCAPS=$MGNC; fast $MGFF/$MGFT; escalating depths: $MGUP (first at n=$MGFIRST, a $((MGFIRST + 1))-byte subject)"
            if [ "$MGDIFF" -ne 0 ]; then
                bad "§6(a): $MGDIFF of $MGROW depths answer differently through the tiered entry than through the default-sized _in: $(awk '$3 != $4 {printf "n=%s(%s vs %s); ", $2, $3, $4}' "$MGD/rows.txt")"
            else
                ok "§6(a): on all $MGROW depths of the multi-group witness the tiered entry's answer equals <prefix>_search_in's at the stamped default"
            fi
            if [ "$MGSP" -eq 0 ]; then
                bad "§6(b): no depth of the multi-group witness matched through both entries, so no capture array was compared"
            elif [ "$MGSPBAD" -eq 0 ]; then
                ok "§6(b): on all $MGSP matching depths the whole $MGNC-pair capture array is byte-identical between the tiered entry and <prefix>_search_in at the stamped default — the span half of the §10.9 promise, on a witness with three groups rather than one"
            else
                bad "§6(b): $MGSPBAD of $MGSP matching depths returned the same value but DIFFERENT capture spans: $(awk '$7 == "0" {printf "n=%s; ", $2}' "$MGD/rows.txt")"
            fi
            if [ "$MGUP" -eq 0 ]; then
                bad "§6(c): not one of the 60 depths escalated, so this dense sweep never crossed the boundary and neither (a) nor (b) says anything about the deep tier"
            elif [ "$MGESC" -eq 0 ]; then
                ok "§6(c): across 60 consecutive depths the deep tier was entered on exactly the $MGUP at which <prefix>_search_in AT THE FAST CAPACITIES gives up — the boundary is crossed once and in the right place"
            else
                bad "§6(c): $MGESC of $MGROW depths escalated against prediction: $(awk '($5 > 0) != ($6 == 1) {printf "n=%s esc=%s pred=%s; ", $2, $5, $6}' "$MGD/rows.txt")"
            fi
        fi
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "run_tiered_entry.sh: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] || exit 1
