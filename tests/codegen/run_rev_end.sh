#!/usr/bin/env bash
# tests/codegen/run_rev_end.sh — [OPT-REVEND] L2: the `rev-end` LOCATE row's
# STRUCTURAL checks (docs/design/locate_finish.md §5 L2; revend.md §9.1 item
# 3), the facts a `.rxt` answer cannot see because the row is
# answer-identical by construction:
#
#   §1 NAMED WITNESSES, one per tie arm and per decline, the expectation
#      written here (never read off the row): `RX_DFA_SCAN "rev-end"` and the
#      walk's own text (`revend_seed`), and the TIE TEXT by arm: none where a
#      match cannot end by consuming the final newline (`nl_last` false, or
#      `\z`'s one seed), the anchored run where the anchored machine exists
#      (`_match(&revend_ctx)`), the relocate to the composite where it does not
#      (`search_from = revend_start;`), and on a VM hybrid always the relocate
#      (an ENDSET never reaches the VM's verify-at, LR-S3);
#   §2 THE CORPUS, both directions of the deny: every distinct `pattern` line
#      under tests/ compiled default and `-fno-rev-end`. Where the default
#      artifact is not a walk the two are BYTE-IDENTICAL (a declining pattern
#      moves nothing); where it is, its text carries `revend_seed` and its
#      stamp reads `rev-end`, and the denied one carries neither. Populations
#      floored (K35).
#
# The stamp is checked against the TEXT, not against the row (the row is
# what is under test): `run_dfa_stamps.sh` holds `RX_DFA_SCAN "rev-end"` <=>
# the walk's loop over the whole corpus as its scan derivation; this file
# adds the arms and the deny's byte identity.
#
# Usage: bash tests/codegen/run_rev_end.sh   (PCREC, PROCS honoured)
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh" >/dev/null
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/revend.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
[ -x "$PCREC" ] || { echo "FAIL: rev-end: no compiler at $PCREC" >&2; exit 1; }

comp() {   # comp OUT FLAGS... -- PATTERN
    local out="$1"; shift
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx -o - "$@" > "$out" 2>/dev/null
}

# ---- §1 named witnesses: EXPECT-SCAN EXPECT-TIE FLAGS PATTERN -------------
# tie: none | anchored | relocate | - (not a walk)
witness() {
    local scan="$1" tie="$2" flags="$3" pat="$4" art="$WORKDIR/w.c" got_scan got_tie
    local fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
    if ! comp "$art" "${fl[@]}" --pattern "$pat"; then
        bad "[witness] '$pat' ($flags) does not compile"; return
    fi
    got_scan="$(sed -n 's/^#define RX_DFA_SCAN "\(.*\)"$/\1/p' "$art")"
    if grep -q 'for (int revend_seed = 0;' "$art"; then
        if grep -q 'ptrdiff_t revend_len = rx_match(&revend_ctx);' "$art"; then got_tie=anchored
        elif grep -q '^    search_from = revend_start;$' "$art"; then got_tie=relocate
        elif grep -q 'revend_tie' "$art"; then got_tie=other
        else got_tie=none; fi
    else got_tie=-; fi
    if [ "$got_scan" = "$scan" ] && [ "$got_tie" = "$tie" ]; then
        ok "[witness] '$pat' ($flags): RX_DFA_SCAN \"$scan\", tie arm $tie"
    else
        bad "[witness] '$pat' ($flags): RX_DFA_SCAN \"$got_scan\", tie arm $got_tie; expected \"$scan\", $tie"
    fi
}
witness rev-end    none     -                 '\d+$'
witness rev-end    none     -                 '[a-z]+\.txt$'
witness rev-end    none     -                 '.*\.txt$'
witness rev-end    none     -                 '\w+\z'
witness rev-end    none     -                 '\d+$(?=\n)'
witness rev-end    anchored -                 '\s+$'
witness rev-end    anchored -                 '\s*?$'
witness rev-end    relocate -fno-anchored-dfa '\s+$'
witness rev-end    relocate -                 '(\s+){2}$'
witness rev-end    relocate -                 '(\s+?){2}$'
witness rev-end    none     -                 '(\d+)$'
witness unanchored -        -fno-rev-end      '\d+$'
witness unanchored -        -                 '(?m)\d+$'
witness unanchored -        -                 'a(b|c)+d'
witness attempt    -        -                 '^\w+$'
witness empty      -        -                 '[^\x00-\xff]$'

# ---- §2 the corpus, default against -fno-rev-end -------------------------
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
a="$WORKDIR/a.$$.c"; b="$WORKDIR/b.$$.c"
while IFS= read -r pat; do
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx -o - --pattern "$pat" > "$a" 2>/dev/null || { echo REFUSED; continue; }
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx -fno-rev-end -o - --pattern "$pat" > "$b" 2>/dev/null || { echo BREFUSED; echo "BAD: refused only under -fno-rev-end: $pat"; continue; }
    if grep -q '^#define RX_DFA_SCAN "rev-end"$' "$a"; then
        echo WALK
        grep -q 'for (int revend_seed = 0;' "$a" || { echo WALKBAD; echo "BAD: stamps rev-end, no walk in the text: $pat"; }
        grep -q 'revend_seed' "$b" && { echo WALKBAD; echo "BAD: the walk survives -fno-rev-end: $pat"; }
        grep -q '^#define RX_DFA_SCAN "rev-end"$' "$b" && { echo WALKBAD; echo "BAD: -fno-rev-end still stamps rev-end: $pat"; }
    else
        echo DECLINE
        grep -q 'revend_seed' "$a" && { echo WALKBAD; echo "BAD: the walk without the stamp: $pat"; }
        cmp -s "$a" "$b" || { echo DECLBAD; echo "BAD: a declining pattern moves under -fno-rev-end: $pat"; }
    fi
done
WORKER
. "$ROOT_DIR/tests/lib/shard_split.sh"
NSHARD="${PROCS:-$(bash "$ROOT_DIR/tests/lib/procs_default.sh")}"
mkdir -p "$WORKDIR/sh"
shard_split "$NSHARD" "$WORKDIR/pats" "$WORKDIR/sh/p" || exit 1
export WORKDIR PCREC TIMEOUT_BIN
for f in "$WORKDIR"/sh/p*; do bash "$WORKDIR/worker.sh" < "$f" > "$f.out" & done
wait
cat "$WORKDIR"/sh/p*.out > "$WORKDIR/verdicts"
tok() { grep -cx "$1" "$WORKDIR/verdicts" || true; }
nwalk=$(tok WALK); ndecl=$(tok DECLINE); nwb=$(tok WALKBAD); ndb=$(tok DECLBAD); nbr=$(tok BREFUSED)
grep '^BAD: ' "$WORKDIR/verdicts" | head -10 >&2
# FLOORS, ~90% of what this tree measures (2026-10-10: 4,632 distinct lines,
# 232 walks -- DFA bodies and VM hybrids' inlined bodies -- and 3,988
# declines); a red here is "the population moved": find out why before
# re-pinning.
[ "$npat" -ge 4150 ] && ok "[corpus] $npat distinct pattern lines" \
                     || bad "[corpus] only $npat distinct pattern lines (floor 4150)"
[ "$nwalk" -ge 205 ] && ok "[corpus] $nwalk artifacts walk (floor 205)" \
                     || bad "[corpus] only $nwalk artifacts walk (floor 205): the row stopped reaching its population"
[ "$ndecl" -ge 3550 ] && ok "[corpus] $ndecl artifacts decline (floor 3550)" \
                      || bad "[corpus] only $ndecl declining artifacts compared (floor 3550)"
[ "$nwb" -eq 0 ] && ok "[corpus] the stamp, the walk's text and the deny agree on all $nwalk walks and $ndecl declines" \
                 || bad "[corpus] $nwb stamp/text/deny disagreement(s)"
[ "$ndb" -eq 0 ] && ok "[corpus] every declining artifact is byte-identical under -fno-rev-end ($ndecl)" \
                 || bad "[corpus] $ndb declining artifact(s) move under -fno-rev-end"
[ "$nbr" -eq 0 ] || bad "[corpus] $nbr pattern(s) refused only under -fno-rev-end"

# ---- §3 the size ladder's rev-end clause (locate_finish.md §5 L2, LR-S12) --
# A drop rung applies only if the member set it leaves is a STRICT SUBSET of
# the one before it. A tie-capable walk that loses its anchored machine
# relocates through the composite and GROWS (it gains the forward machine), so
# under an emitted-size cap between the walk's size with the premultiplied
# table dropped and its size as built, the ladder must skip the anchored rung
# and take the next (premul): the witness then compiles, still `unwrapped`,
# with no forward machine. Without the clause it takes the anchored rung,
# grows past the cap and refuses (or ships the bigger composite). The cap is
# DERIVED from the witness's own sizes on the default build (the comment-
# excluded artifact size `--warn-emit-bytes` reports, the cap's own measure), and the three sizes'
# order is asserted first, so a witness whose sizes stop straddling reads as
# its own failure rather than as a pass. A reference compiler is built with
# that cap (`PCREC_MAX_EMIT_BYTES`, FLAG_D), run_size_term.sh's shape.
. "$ROOT_DIR/tests/lib/lib_srcs.sh"
LADDER='\s+$'
size_of() {
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx "$@" --warn-emit-bytes=1 -o "$WORKDIR/sz.c" \
        --pattern "$LADDER" 2>&1 | sed -n 's/.*artifact: \([0-9]*\) bytes of emitted C source.*/\1/p' | head -1
}
s_def=$(size_of); s_np=$(size_of -fno-premul-table)
s_grow=$(size_of -fno-anchored-dfa -fno-premul-table)
if [ -z "$s_def" ] || [ -z "$s_np" ] || [ -z "$s_grow" ] || [ "$s_np" -ge "$s_def" ] ||
   [ "$s_grow" -le "$s_def" ]; then
    bad "[ladder] the witness '$LADDER' no longer straddles: built $s_def, premul-dropped $s_np, anchored-and-premul-dropped $s_grow (need premul < built < grown)"
else
    cap=$(( (s_np + s_def) / 2 ))
    REF="$WORKDIR/pcrec_cap"
    # shellcheck disable=SC2046
    if ${CC:-gcc} -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
           -DPCREC_MAX_EMIT_BYTES=$cap -o "$REF" "$ROOT_DIR/cli/main.c" \
           $(pcrec_lib_srcs "$ROOT_DIR" | tr '\n' ' ') 2>"$WORKDIR/ref.err"; then
        if "$TIMEOUT_BIN" 60 "$REF" --features all -p rx -o "$WORKDIR/lad.c" --pattern "$LADDER" 2>/dev/null &&
           grep -qF '#define RX_DFA_MATCH "unwrapped"' "$WORKDIR/lad.c" &&
           grep -qF '#define RX_ENGINE_SEL "size-cap-retry"' "$WORKDIR/lad.c" &&
           ! grep -q 'rx_forward_' "$WORKDIR/lad.c"; then
            ok "[ladder] under a cap of $cap (built $s_def, premul-dropped $s_np, grown $s_grow) the tie witness skips the anchored rung: unwrapped, size-cap-retry, no forward machine"
        else
            bad "[ladder] under a cap of $cap the tie witness '$LADDER' took the anchored rung (or refused): $(grep -E 'RX_DFA_MATCH|RX_ENGINE_SEL' "$WORKDIR/lad.c" 2>/dev/null | tr '\n' ' ')"
        fi
    else
        bad "[ladder] the reference compiler (PCREC_MAX_EMIT_BYTES=$cap) did not build: $(head -3 "$WORKDIR/ref.err")"
    fi
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
