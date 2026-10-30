#!/usr/bin/env bash
# tests/codegen/run_landmark_walk.sh — [LANDWALK] stage 1 (lane p1build): the
# `landmark-walk` LOCATE row's STRUCTURAL checks (docs/spec/tuning.md §2.54),
# the facts a `.rxt` answer cannot see because the row is answer-identical by
# construction (tests/landwalk/landwalk.rxt holds the answers):
#
#   §1 NAMED WITNESSES, one per admission row: the expected `RX_DFA_SCAN`
#      written here (never read off the row), and for a walk its own text
#      (`lmwalk_reach`, the reach guard) present, for any other scan absent;
#   §2 THE DENY, both directions: under `-fno-landmark-walk` (and under
#      `-fno-anchored-dfa`, whose machine the walk runs) a walk witness reads
#      `"unanchored"` with no walk text, and a declining witness is
#      BYTE-IDENTICAL to its default artifact (the deny is masked out of
#      `rx_info.flags` and moves nothing else);
#   §3 THE REACH GUARD, as a cost: a subject of 50,000 landmarks every one of
#      which starts an anchored run to the subject's end answers inside a
#      bound the quadratic walk (no guard) exceeds by a wide margin (measured
#      at n = 65,536: 0.00 s guarded, 5.5 s unguarded; p1build_report.md).
#   §4 the measurement card (tests/landwalk/card_lwalk.sh) builds and runs
#      in its smoke form (never a timing).
#
# The size-cap rung `drop-landmark-walk` is tests/codegen/run_fallback_table.sh's
# (seq-lwdrop, seq-lwref, att-sclw).
#
# Usage: bash tests/codegen/run_landmark_walk.sh   (PCREC honoured)
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh" >/dev/null
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/landwalk.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
[ -x "$PCREC" ] || { echo "FAIL: landmark-walk: no compiler at $PCREC" >&2; exit 1; }

comp() {   # comp OUT FLAGS... -- the last argument is the pattern
    local out="$1"; shift
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx -o - "$@" > "$out" 2>/dev/null
}
scan_of() { sed -n 's/^#define RX_DFA_SCAN "\(.*\)"$/\1/p' "$1"; }
has_walk() { grep -q 'size_t lmwalk_reach = search_from;' "$1"; }

# ---- §1 + §2: ENC EXPECT-SCAN ROW PATTERN (ROW: the admission row that
# decides it, `admitted` for a walk; documentation only, the trace build's
# LMWALK record is where the row is read) -----------------------------------
nwalk=0; ndecl=0
while IFS='|' read -r enc scan row pat; do
    [ -z "$enc" ] && continue
    fl=(); [ "$enc" = u ] && fl=(-e utf8)
    a="$WORKDIR/d.c"; n="$WORKDIR/n.c"; x="$WORKDIR/x.c"
    if ! comp "$a" "${fl[@]}" --pattern "$pat"; then bad "[witness] '$pat' ($enc) does not compile"; continue; fi
    got="$(scan_of "$a")"
    if [ "$scan" = landmark-walk ]; then
        if [ "$got" = landmark-walk ] && has_walk "$a"; then ok "[witness] '$pat' ($enc): \"landmark-walk\" with the walk text"
        else bad "[witness] '$pat' ($enc): \"$got\" (walk text $(has_walk "$a" && echo present || echo absent)); expected \"landmark-walk\" ($row)"; fi
        nwalk=$((nwalk + 1))
        # the walk answers presence, so PRESENCE declines the whole-window
        # pre-check on it (match_api.md §6.3's `dominated`; lane p1tri moved
        # run_prechecks.sh's witnesses off the walk, so this is where it is held)
        why="$(sed -n 's/^#define RX_REQ_WHY "\(.*\)"$/\1/p' "$a")"
        if [ "$why" = dominated ]; then ok "[presence] '$pat' ($enc): RX_REQ_WHY \"dominated\" on the walk"
        else bad "[presence] '$pat' ($enc): RX_REQ_WHY \"$why\" on a walk artifact, expected \"dominated\""; fi
        for deny in -fno-landmark-walk -fno-anchored-dfa; do
            comp "$n" "${fl[@]}" "$deny" --pattern "$pat" || { bad "[deny] '$pat' $deny does not compile"; continue; }
            g2="$(scan_of "$n")"
            if [ "$g2" != landmark-walk ] && ! has_walk "$n"; then ok "[deny] '$pat' ($enc) $deny: \"$g2\", no walk text"
            else bad "[deny] '$pat' ($enc) $deny: still \"$g2\" / walk text present"; fi
        done
    else
        if [ "$got" = "$scan" ] && ! has_walk "$a"; then ok "[witness] '$pat' ($enc): \"$scan\" ($row)"
        else bad "[witness] '$pat' ($enc): \"$got\"; expected \"$scan\" ($row), no walk text"; fi
        ndecl=$((ndecl + 1))
        comp "$x" "${fl[@]}" -fno-landmark-walk --pattern "$pat" || { bad "[deny] '$pat' does not compile denied"; continue; }
        if cmp -s "$a" "$x"; then ok "[deny] '$pat' ($enc): a declining pattern is byte-identical under -fno-landmark-walk"
        else bad "[deny] '$pat' ($enc): the deny moved a declining artifact"; fi
    fi
done <<'EOF'
b|landmark-walk|admitted|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
u|landmark-walk|admitted|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
b|landmark-walk|admitted|[a-z]+@x
b|landmark-walk|admitted|a+b
b|landmark-walk|admitted|[0-9]*aa[bc]
b|landmark-walk|admitted|[a-z]+@(?:[a-z]+@)*[a-z]+
b|landmark-walk|admitted|\b[a-z]+@x\b
b|landmark-walk|admitted|(?:ab|cd)+@x
u|landmark-walk|admitted|[a-zé]+@x
u|landmark-walk|admitted|[^@ ]+@x
b|unanchored|finisher-dfa|a+\Kb
b|unanchored|finisher-dfa (a VM hybrid's prefilter)|([a-z]+)@x
b|attempt|anchored scan (\G)|\Ga+b
b|unanchored|branches|ab|cd
b|unanchored|exclusion|a.*b@c
b|unanchored|next-landmark/handoff|[a-z]{2,5}@x
b|unanchored|rarity|[^@]+@x
b|unanchored|rarity|x*@y
b|unanchored|rarity|[a-z]+\d
u|unanchored|rarity (no utf8 byte prior)|a+b
u|unanchored|rarity (no utf8 byte prior)|(*UCP)a\sb
b|rev-end|outranked by rev-end|[a-z]+@x$
EOF
# K35: the populations are counted, so a list that silently loses its walks
# (or its declines) is a failure, not a smaller pass.
[ "$nwalk" -ge 10 ] && ok "[floor] $nwalk walk witnesses (floor 10)" || bad "[floor] $nwalk walk witnesses, floor 10"
[ "$ndecl" -ge 12 ] && ok "[floor] $ndecl declining witnesses (floor 12)" || bad "[floor] $ndecl declining witnesses, floor 12"

# ---- §3 the reach guard as a cost ------------------------------------------
pat='[a-z]+@(?:[a-z]+@)*[a-z]+ '
subj="$(python3 -c 'import sys; sys.stdout.write("a@" * 50000)')"
if "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx --emit-main -o "$WORKDIR/g.c" --pattern "$pat" 2>/dev/null \
   && "$TIMEOUT_BIN" 120 "$CC" -O2 -o "$WORKDIR/g" "$WORKDIR/g.c" 2>"$WORKDIR/g.log"; then
    t0=$(date +%s%N)
    "$TIMEOUT_BIN" 10 "$WORKDIR/g" "$subj" >/dev/null; rc=$?
    ms=$(( ($(date +%s%N) - t0) / 1000000 ))
    # 2 s: the guarded walk is linear (milliseconds); the unguarded one is
    # quadratic (about 3 s at this size by the n = 65,536 measurement).
    if [ "$rc" = 1 ] && [ "$ms" -lt 2000 ]; then ok "[reach] 50,000 landmarks, no match, ${ms} ms (bound 2,000)"
    else bad "[reach] rc=$rc (expected 1, no match) in ${ms} ms (bound 2,000): the reach guard does not hold the walk linear"; fi
else
    bad "[reach] the witness does not compile"; cat "$WORKDIR/g.log" >&2
fi

# ---- §4 the measurement card builds and runs (smoke: never a timing) ------
if PCREC="$PCREC" CC="$CC" TMPDIR="$WORKDIR" bash "$ROOT_DIR/tests/landwalk/card_lwalk.sh" --smoke \
        -o "$WORKDIR/card.tsv" 2>"$WORKDIR/card.log" \
   && [ "$(grep -c '^lwalk	lwhit	' "$WORKDIR/card.tsv")" = 6 ] \
   && grep -q '^lwalk	lwcall	' "$WORKDIR/card.tsv"; then
    ok "[card] tests/landwalk/card_lwalk.sh --smoke: six lwhit rows and lwcall"
else
    bad "[card] tests/landwalk/card_lwalk.sh --smoke did not produce its rows"; cat "$WORKDIR/card.log" >&2
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
