#!/usr/bin/env bash
# tests/codegen/run_scan_edge_census.sh — [OPT-EDGE] STEP 1.1: precondition
# (8)'s population, held to the artifact.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `src/opt/scanedge.c`'s precondition (8) refuses a scan-edge head that a SEED
# family names, on a machine whose candidate-start prefilter WRITES the state
# variable. Two facts have to hold together for the emitted loop to be sound,
# and each is invisible to every answer check in the tree until it is not:
#
#   (A) the loop's ONE PER-SEARCH entry test recognises a head the START SEED
#       installed. `seed_emit_seeded` initialises the state variable from
#       `seed_state[byte_class[subject[search_from - 1]]]` -- ANY member of the
#       family -- so a test that asks "is this exactly the start state" misses
#       every other head-valued seed, the generic path then runs at a head, and
#       the step reads the transition cell the pass KILLED. That was the shape
#       until STEP 1.1; the test is now `is_stop && !is_dead`, the same
#       question the loop body asks.
#
#   (B) precondition (8) still refuses on the machines where the hazard is
#       real -- the `offset-set` prefilter's RESEED, which writes the state
#       variable MID-BODY, after the stop test has already been passed.
#
# THE CENSUS IS THE INSTRUMENT FOR (A) AND THE MANIFEST BELOW IS ITS
# EXPECTATION, SPELLED HERE RATHER THAN HARVESTED. STEP 1 cost these eleven
# artifacts their scan edge; STEP 1.1 gives all eleven back, and WHICH MACHINE
# each one lands on is the fact worth pinning, because it is what the STEP 1
# census got wrong: it read the artifact-level `RX_DFA_PREFILTER` stamp and
# concluded two of the eleven carried the hazard, when the edge those two lost
# is on the REVERSE machine -- which has no prefilter at all.
#
# =========================================================================
# WHAT THIS FILE DOES NOT CHECK, AND WHY THAT IS SAID OUT LOUD
# =========================================================================
# It is NOT a control on (B). The narrowed (8) has an EMPTY population on
# today's corpus (measured: an artifact built with the precondition deleted is
# byte-identical), so nothing here can go red if (8) is removed. A check with
# no failing direction is what `docs/dev/learnings.md` §3 warns about, so this
# file does not pretend to be one. (B)'s failing direction belongs to
# `tests/mech`, aimed at the emitter's own read-back check in
# `dfa_form_derive` -- which fires on the AGREEMENT between the pass's answer
# and the emitted form, and is therefore the one reading of (8) that does not
# share a source with the pass's decision.
#
# =========================================================================
# STALENESS
# =========================================================================
# The manifest is a list of patterns and an expectation per pattern. Two ways
# it can rot, and both are failures rather than silent passes:
#
#   * a listed pattern no longer appears as a `pattern` line under `tests/` --
#     the corpus moved and the census is measuring something nobody tests;
#   * a listed pattern's artifact carries a scan edge on a machine the
#     manifest does not name, or none at all.
#
# Plus a non-vacuity floor: fewer than FLOOR rows reaching their check means
# the enumeration stopped matching artifacts and the file is passing on air.

set -uo pipefail
cd "$(dirname "$0")/../.."
PCREC=${PCREC:-build/pcrec}
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0; pass=0; checked=0
FLOOR=11

say()  { printf '%s\n' "$*"; }
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); printf 'FAIL [scan-edge-census] %s\n' "$*"; }

# ---- the manifest: pattern -> the machines that must carry an edge ---------
# `f` forward, `r` reverse, `a` anchored; a leading count is the number of
# edge blocks that machine must carry. Written from the measured artifact and
# NOT harvested at run time -- an expectation a script computes from the thing
# it is checking is not an expectation.
MANIFEST=(
  '(\b\w+\b)|f=1'
  '(foo\B)|r=1'
  '\b\w+\b|f=1'
  '\b\w+\b$|f=1'
  '\b\w+\b\z|f=1'
  '\b\w+\z|f=1'
  '\b\w\b|f=1'
  'foo\B|r=1'
  '\b\K\w+|f=2'
  '\Bfoo\B|r=1'
  '\bfoo\B|r=1'
)

# Count the edge blocks a machine carries, from the artifact's own `[OPT-5]
# SCAN EDGE` markers attributed by the STATE VARIABLE the block tests. The
# marker is the instrument and the stamp is not: `RX_DFA_SCAN_EDGE` names axis
# I's BODY form, so a machine going from two edges to one reads identical.
edges_on() {   # $1 artifact, $2 machine
    awk -v m="$2" '
        /\[OPT-5\] SCAN EDGE/ { pend = 1; next }
        pend && $0 ~ ("if \\(" m "_state ==") { n++; pend = 0 }
        END { print n + 0 }
    ' "$1"
}

say "== [OPT-EDGE] STEP 1.1 -- precondition (8)'s census =="

for row in "${MANIFEST[@]}"; do
    pat=${row%|*}
    want=${row##*|}
    mach=${want%%=*}
    cnt=${want##*=}
    case $mach in f) mv=forward;; r) mv=reverse;; a) mv=anchored;; *) bad "bad manifest row: $row"; continue;; esac

    # (1) STALENESS: the pattern is still in the corpus.
    if ! grep -RFqx -- "pattern $pat" tests/ 2>/dev/null; then
        bad "STALE MANIFEST: '$pat' is no longer a 'pattern' line under tests/"
        continue
    fi

    if ! "$PCREC" -p rx --features all -o "$TMP/a.c" -- "$pat" >"$TMP/err" 2>&1; then
        bad "'$pat' failed to compile: $(head -1 "$TMP/err")"
        continue
    fi
    checked=$((checked+1))

    got=$(edges_on "$TMP/a.c" "$mv")
    if [ "$got" != "$cnt" ]; then
        bad "'$pat': expected $cnt scan edge(s) on the $mv machine, found $got"
        continue
    fi

    # (2) The entry dispatch has to be able to SEE a seeded head. Where the
    #     machine emits a seed table AND carries an edge, the emitted entry
    #     must be the general test rather than an equality against the start
    #     state -- that regression is silent to every answer check whose
    #     subjects never seed onto a head.
    if grep -q "rx_${mv}_seed_state" "$TMP/a.c"; then
        if ! grep -q "if (rx_${mv}_is_stop(${mv}_state) && !rx_${mv}_is_dead(${mv}_state)) goto rx_${mv}_scan_edge;" "$TMP/a.c"; then
            bad "'$pat': the $mv machine has a seed table and a scan edge, but its loop entry is not the general head test"
            continue
        fi
    fi
    ok
done

# (3) The two `offset-set` artifacts must keep a FORWARD machine with no edge:
#     that is where precondition (8) still applies, and it is the half of the
#     STEP 1 census that was misread.
for pat in '\Bfoo\B' '\bfoo\B'; do
    "$PCREC" -p rx --features all -o "$TMP/a.c" -- "$pat" >/dev/null 2>&1 || { bad "'$pat' failed to compile"; continue; }
    if [ "$(grep -c 'RX_DFA_PREFILTER "offset-set-bounded"' "$TMP/a.c")" -ne 1 ]; then
        bad "'$pat' no longer takes an offset-set prefilter -- the census's own hazard witness moved"
        continue
    fi
    if [ "$(edges_on "$TMP/a.c" forward)" != "0" ]; then
        bad "'$pat': its forward machine took a scan edge while its prefilter reseeds -- precondition (8) did not fire"
        continue
    fi
    ok
done

# (4) NON-VACUITY.
if [ "$checked" -lt "$FLOOR" ]; then
    bad "only $checked of $FLOOR manifest rows reached their check -- the enumeration is not matching artifacts"
fi

say "scan-edge census: $pass passed, $fail failed ($checked manifest rows compiled)"
[ "$fail" -eq 0 ]
