#!/usr/bin/env bash
# B-B1's EXHAUSTIVE-SUBJECT possdiff, PROTOTYPE form (not wired into make).
#
# tests/possessify/run_possdiff.sh's comparison (possdiff_driver.c, the
# possessified artifact against `-fno-possessify`, every startpos, span +
# every slot + the failure surface), with three changes the panel asked for:
#   - the SUBJECTS are subjects_exh.py's exhaustive sweep (every string of
#     length <= 4 over a case-flip-closed alphabet + word/non-word reps; by
#     code point under -e utf8) instead of the bespoke families;
#   - a pattern file's `# flags:` line (-e utf8, --ucp, -i) applies to BOTH
#     sides, beside `# features:` (B-M5: the header generalizes; no TAB column);
#   - a REACH file (`pattern<TAB>subject`, subject in the driver's escape
#     form) is checked against the generator before anything is compiled:
#     every (pattern, witness) pair must be IN the sweep, or the run fails.
#
# Side A is the rev-2 prototype with $ARMS_ENV in its environment (arms on,
# plus at most one sabotage switch); side B is the same binary with NO arm
# variable and -fno-possessify, i.e. today's main with possessify denied.
# ENGA=default compiles side A on the DEFAULT route instead of --engine=vm
# (the C-1 route-flip witnesses: a discharged atomic group goes to the DFA).
#
# Usage: PROTO=... ARMS_ENV="PROTO_ARM_A=1 PROTO_ARM_B=1" \
#        possdiff_exh.sh [--reach FILE] patternfile...
# Prints one line per pattern (`agree|DIVERGE|refused`, cells, A's POSSESSIVE
# stamp) and a final tally; exits 1 on any divergence or reach miss.
set -u
export LC_ALL=C
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../../../.." && pwd)
P="${PROTO:?}"; CCX="${CC:-gcc-16}"
W=$(mktemp -d "${TMPDIR:-/tmp}/pdexh.XXXXXX"); trap 'rm -rf "$W"' EXIT
reach_fail=0; agree=0; div=0; refused=0; cells=0; poss=0
if [ "${1:-}" = "--reach" ]; then
    rf="$2"; shift 2
    while IFS=$'\t' read -r rp rs rfl; do
        case "$rp" in ''|'#'*) continue ;; esac
        # shellcheck disable=SC2086
        if python3 -B "$HERE/subjects_exh.py" --reach "$rs" "$rp" $rfl; then
            echo "reach	ok	$rp	$rs"
        else echo "reach	MISS	$rp	$rs"; reach_fail=$((reach_fail + 1)); fi
    done < "$rf"
fi
for f in "$@"; do
    feats="$(sed -n 's/^# features: *//p' "$f" | head -1)"
    flags="$(sed -n 's/^# flags: *//p' "$f" | head -1)"
    fa="--features ${feats:-all} $flags"
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        d="$W/c"; rm -rf "$d"; mkdir -p "$d"
        enga="--engine=vm"; [ "${ENGA:-vm}" = default ] && enga=""
        # shellcheck disable=SC2086
        if ! env ${ARMS_ENV:-} "$P" -p pa $enga $fa -o "$d/pa.c" --pattern "$pat" 2>"$d/ea" >/dev/null; then
            echo "refused	$pat	$(head -1 "$d/ea")"; refused=$((refused + 1)); continue; fi
        # shellcheck disable=SC2086
        if ! "$P" -p pb --engine=vm -fno-possessify $fa -o "$d/pb.c" --pattern "$pat" 2>"$d/eb" >/dev/null; then
            echo "refused-B	$pat	$(head -1 "$d/eb")"; refused=$((refused + 1)); continue; fi
        st=$(sed -n 's/^#define PA_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$d/pa.c")
        pm=$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$d/pa.h")
        ps=0; [ -n "$st" ] && [ -n "$pm" ] && [ $(( 0x$st & 0x$pm )) -ne 0 ] && ps=1
        eng=$(sed -n 's/^#define PA_ENGINE "\([a-z]*\)".*/\1/p' "$d/pa.c" | head -1)
        if ! timeout 300 "$CCX" -O1 -std=gnu11 -w -I "$d" -o "$d/t" "$ROOT/tests/possessify/possdiff_driver.c" "$d/pa.c" "$d/pb.c" 2>"$d/cc"; then
            echo "BUILD-FAIL	$pat	$(head -2 "$d/cc" | tr '\n' ' ')"; div=$((div + 1)); continue; fi
        # shellcheck disable=SC2086
        python3 -B "$HERE/subjects_exh.py" "$pat" $flags > "$d/subj"
        out=$(timeout 600 "$d/t" < "$d/subj" 2>"$d/dv"); rc=$?
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p'); cells=$((cells + ${n:-0}))
        poss=$((poss + ps))
        if [ $rc -eq 0 ]; then echo "agree	$pat	cells=${n:-0}	poss=$ps	eng=${eng:-?}"; agree=$((agree + 1))
        else echo "DIVERGE	$pat	cells=${n:-0}	poss=$ps	eng=${eng:-?}	$(head -3 "$d/dv" | tr '\n' ' ')"; div=$((div + 1)); fi
    done < "$f"
done
echo "#TALLY agree=$agree diverged=$div refused=$refused possessive=$poss cells=$cells reach_miss=$reach_fail"
[ $div -eq 0 ] && [ $reach_fail -eq 0 ]
