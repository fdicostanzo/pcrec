#!/usr/bin/env bash
# tests/codegen/run_ir_listing.sh — [M4.5c] the VM program listing (DD-8) is
# held to the ARTIFACT it describes.
#
# WHY THIS EXISTS, and why it is not optional. engine_m4.md §10's one
# constraint on this tool is that "the dump must be derived from the same
# structure the emitter walks, never a parallel description — a second source
# of truth for what the VM does is worse than no dump." The emitter satisfies
# that structurally (every listing event is appended by the same call that
# writes the corresponding C — src/gen/emit_vm.c's VEvent stream), but a
# structural argument is exactly the kind of claim this project has learned to
# check rather than assert: it holds only as long as nobody adds a second way
# to emit a label, a push, or a slot write.
#
# So each SECTION of the listing is pinned to a fact DERIVABLE FROM THE .c:
#
#   PROGRAM        the label SET matches, both directions and without
#                  duplicates. A listing missing a label describes a program
#                  that is not the one emitted; a listing inventing one is
#                  worse.
#   CHOICE POINTS  every RX_PUSH in the .c appears once, and its resume TARGET
#                  matches the `&&<prefix>_L<n>` the push actually jumps to.
#   SLOTS          the set of stv slots the .c writes equals the set the
#                  listing shows written, and the layout covers RX_NSTATE.
#   ISLANDS        the count is 0 AND the .c contains no island table — the
#                  honest-empty claim is checked against the artifact, not
#                  taken on trust, so the section starts working the day a
#                  producer exists.
#   CALLOUTS       same shape.
#   header         RX_NCAPS / step budget / frame + trail capacities agree
#                  with the macros in the .c.
#
# And the TRACE (§10's other half) is held to the property its own source
# comment claims: an instrumented artifact must take the SAME path as the
# untraced one. A debug build that changes the answer is a tool that lies.
#
# Usage: bash tests/codegen/run_ir_listing.sh
# Env: PCREC (default <root>/build/pcrec), CC, GENCFLAGS, KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "ir-listing: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# The shapes, chosen so every emission path that can produce a listing event is
# represented: an alternation chain, both cursor rungs, the frames rung with
# and without the empty-iteration guard, nested captures, bounded replication,
# and the anchors.
PATTERNS=(
    'a(b|c)+d'
    '(a*)b'
    '(a*?)b'
    '(ab){2,3}c'
    '((a)|b)+c'
    '(a*)*'
    '(|a)+'
    '((a)(b))*'
    '(^a$)'
    '(\d+)-(\d+)'
    '(a|ab)(c|bcd)'
)

for pat in "${PATTERNS[@]}"; do
    d="$WORKDIR/$(printf '%s' "$pat" | md5sum | cut -c1-8)"
    mkdir -p "$d"
    if ! "$PCREC" -p rx -o "$d/gen.c" -- "$pat" >/dev/null 2>&1; then
        bad "ir-listing: pcrec could not compile '$pat'"
        continue
    fi
    if ! "$PCREC" -p rx --emit-ir -- "$pat" > "$d/ir" 2>"$d/ir.err"; then
        bad "ir-listing: --emit-ir failed for '$pat': $(head -1 "$d/ir.err")"
        continue
    fi

    # ---- PROGRAM: the label set, both directions, no duplicates ----------
    grep -oE '^rx_L[0-9]+:' "$d/gen.c" | tr -d ':' | sort > "$d/c.labels"
    grep -oE '^  rx_L[0-9]+|^  L[0-9]+' "$d/ir" | sed 's/^ *//; s/^L/rx_L/' \
        | sort > "$d/ir.labels"
    cdup="$(uniq -d < "$d/c.labels" | wc -l)"
    idup="$(uniq -d < "$d/ir.labels" | wc -l)"
    if [ ! -s "$d/c.labels" ]; then
        bad "ir-listing[$pat]: no labels found in the emitted C — the extraction is vacuous"
    elif [ "$idup" != "0" ]; then
        bad "ir-listing[$pat]: the listing shows a label more than once"
    elif [ "$cdup" != "0" ]; then
        bad "ir-listing[$pat]: the emitted C defines a label more than once (an emitter bug, caught here)"
    elif ! diff -q "$d/c.labels" "$d/ir.labels" >/dev/null; then
        bad "ir-listing[$pat]: label SETS differ between the .c and the listing: $(diff "$d/c.labels" "$d/ir.labels" | tr '\n' ' ' | cut -c1-200)"
    else
        nlab="$(wc -l < "$d/c.labels")"
        ok "ir-listing[$pat]: PROGRAM — all $nlab emitted labels appear exactly once in the listing, and the listing invents none"
    fi

    # ---- CHOICE POINTS: count and resume target --------------------------
    grep -oE 'RX_PUSH\(&&rx_L[0-9]+' "$d/gen.c" | grep -oE 'rx_L[0-9]+' \
        | sort > "$d/c.push"
    grep -oE '^  at L[0-9]+ +resume L[0-9]+' "$d/ir" \
        | grep -oE 'resume L[0-9]+' | sed 's/resume L/rx_L/' | sort > "$d/ir.push"
    if ! diff -q "$d/c.push" "$d/ir.push" >/dev/null; then
        bad "ir-listing[$pat]: CHOICE POINTS disagree with the emitted RX_PUSH sites: $(diff "$d/c.push" "$d/ir.push" | tr '\n' ' ' | cut -c1-200)"
    else
        ok "ir-listing[$pat]: CHOICE POINTS — $(wc -l < "$d/c.push") emitted RX_PUSH site(s), each with its resume target, match the listing"
    fi

    # ---- SLOTS: the written set ------------------------------------------
    grep -oE 'RX_SET\([0-9]+' "$d/gen.c" | grep -oE '[0-9]+' | sort -n -u > "$d/c.slots"
    grep -oE 'set +stv\[[0-9]+\]' "$d/ir" | grep -oE '[0-9]+' | sort -n -u > "$d/ir.slots"
    if ! diff -q "$d/c.slots" "$d/ir.slots" >/dev/null; then
        bad "ir-listing[$pat]: SLOTS — the stv slots the .c writes differ from the listing's: $(diff "$d/c.slots" "$d/ir.slots" | tr '\n' ' ' | cut -c1-200)"
    else
        ok "ir-listing[$pat]: SLOTS — the $(wc -l < "$d/c.slots") stv slot(s) the artifact writes are exactly the ones the listing shows"
    fi

    # ---- header numbers --------------------------------------------------
    # RX_NCAPS lives in the .h when a header is paired (the macros are emitted
    # once per FILE, and that file is the header). Searching only the .c reads
    # an empty string and compares it against nothing — the same vacuity this
    # project keeps re-learning, and it bit run_vm_identity.sh first.
    cn="$(cat "$d/gen.c" "$d/gen.h" | grep -oE '^#define RX_NCAPS [0-9]+' | awk '{print $3}')"
    ir_n="$(grep -oE '^; caps +RX_NCAPS [0-9]+' "$d/ir" | grep -oE '[0-9]+' | head -1)"
    cbt="$(grep -oE '^#define RX_BT_FRAMES [0-9]+' "$d/gen.c" | awk '{print $3}')"
    ctr="$(grep -oE '^#define RX_TRAIL_FRAMES [0-9]+' "$d/gen.c" | awk '{print $3}')"
    ir_cap="$(grep -oE '^; capacities +[0-9]+ resume frames, [0-9]+ trail' "$d/ir")"
    ir_bt="$(printf '%s' "$ir_cap" | grep -oE '[0-9]+ resume' | grep -oE '[0-9]+')"
    ir_tr="$(printf '%s' "$ir_cap" | grep -oE '[0-9]+ trail' | grep -oE '[0-9]+')"
    if [ "$cn" = "$ir_n" ] && [ "$cbt" = "$ir_bt" ] && [ "$ctr" = "$ir_tr" ] \
       && [ -n "$cn" ] && [ -n "$cbt" ]; then
        ok "ir-listing[$pat]: header — RX_NCAPS/$cn, frames/$cbt, trail/$ctr agree with the artifact's own macros"
    else
        bad "ir-listing[$pat]: header disagrees with the artifact: NCAPS $cn vs $ir_n, frames $cbt vs $ir_bt, trail $ctr vs $ir_tr"
    fi

    # ---- islands / callouts: empty AND the artifact agrees ---------------
    isl="$(grep -oE '^DFA ISLANDS \([0-9]+\)' "$d/ir" | grep -oE '[0-9]+')"
    cal="$(grep -oE '^CALLOUT SITES \([0-9]+\)' "$d/ir" | grep -oE '[0-9]+')"
    # An island would emit its own transition table INSIDE the VM function; a
    # callout site would emit a call through rx_callout_ref. Neither exists,
    # and the check reads the artifact rather than trusting the count.
    art_isl=0
    grep -q 'island' "$d/gen.c" && art_isl=1
    art_cal=0
    grep -qE 'rx_callout_ref [a-z_]*\(|->fn\(' "$d/gen.c" && art_cal=1
    if [ "$isl" = "0" ] && [ "$art_isl" = "0" ] && [ "$cal" = "0" ] && [ "$art_cal" = "0" ]; then
        ok "ir-listing[$pat]: ISLANDS/CALLOUTS — the listing reports 0 of each and the artifact contains neither (honestly empty, not blanked)"
    else
        bad "ir-listing[$pat]: island/callout accounting disagrees — listing says $isl/$cal, artifact says $art_isl/$art_cal"
    fi
done

# ---- the DFA refusal (an as-built decision, so it is pinned) -------------
if out="$("$PCREC" -p rx --emit-ir -- 'abc' 2>&1)"; then
    bad "[M4.5c] --emit-ir on a pure-DFA artifact PRINTED a listing; there is no VM program to list"
elif printf '%s' "$out" | grep -q -- '--engine=vm'; then
    ok "[M4.5c] --emit-ir on a capture-free pattern refuses cleanly and names --engine=vm as the way to see a VM program"
else
    bad "[M4.5c] --emit-ir refused a capture-free pattern but the message names no way forward: $out"
fi
if "$PCREC" -p rx --emit-ir --engine=vm -- 'abc' >/dev/null 2>&1; then
    ok "[M4.5c] ...and that named way forward works"
else
    bad "[M4.5c] --emit-ir --engine=vm was refused too — the diagnostic's advice does not work"
fi
if "$PCREC" -p rx --emit-ir -o "$WORKDIR/x.c" -- '(a)' >/dev/null 2>&1; then
    bad "[M4.5c] --emit-ir accepted -o; it is a query and emits no C"
else
    ok "[M4.5c] --emit-ir takes no -o (a query, not a compile)"
fi

# ---- the TRACE takes the same path as the untraced build ----------------
#
# The traced artifact's own source comment claims it does. That claim is the
# whole value of the tool — a debug build that changes the answer is worse
# than no debug build — so it is checked rather than asserted, over subjects
# that exercise both a match and a no-match with real backtracking.
trace_ok=1
for pat in '(a|ab)(c|bcd)' '((a)|b)+c' '(a*)b'; do
    d="$WORKDIR/tr$(printf '%s' "$pat" | md5sum | cut -c1-6)"
    mkdir -p "$d/plain" "$d/traced"
    "$PCREC" -p rx --emit-main -o "$d/plain/gen.c" -- "$pat" >/dev/null 2>&1 || { trace_ok=0; break; }
    "$PCREC" -p rx --trace --emit-main -o "$d/traced/gen.c" -- "$pat" >/dev/null 2>&1 || { trace_ok=0; break; }
    # shellcheck disable=SC2086
    $CC $GENCFLAGS -I "$d/plain"  -o "$d/plain/t"  "$d/plain/gen.c"  2>"$d/plain.cc"  || { trace_ok=0; echo "  trace: plain build failed: $(head -3 "$d/plain.cc")" >&2; break; }
    # shellcheck disable=SC2086
    $CC $GENCFLAGS -I "$d/traced" -o "$d/traced/t" "$d/traced/gen.c" 2>"$d/traced.cc" || { trace_ok=0; echo "  trace: TRACED build failed under $GENCFLAGS: $(head -3 "$d/traced.cc")" >&2; break; }
    for subj in abcd xxabcd aab bbb '' a aaa; do
        p_out="$("$d/plain/t" "$subj" 2>/dev/null)"
        t_out="$("$d/traced/t" "$subj" 2>/dev/null)"
        if [ "$p_out" != "$t_out" ]; then
            bad "[M4.5c] --trace CHANGED THE ANSWER for '$pat' on \"$subj\": plain '$p_out' vs traced '$t_out'"
            trace_ok=0
        fi
    done
    # ...and it must actually trace: a silent "instrumented" build is the
    # vacuous-check shape (the trace fires on stderr, the result on stdout).
    if ! "$d/traced/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
        bad "[M4.5c] --trace produced no trace output for '$pat' — the instrumentation is not live"
        trace_ok=0
    fi
    if "$d/plain/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
        bad "[M4.5c] the PLAIN artifact for '$pat' emitted trace output — --trace is not opt-in"
        trace_ok=0
    fi
done
[ "$trace_ok" = "1" ] && ok "[M4.5c] --trace: 3 patterns x 7 subjects — the instrumented artifact agrees with the plain one on every answer, traces on stderr, and the plain artifact traces nothing"

# A traced artifact must SAY it is traced (the D37 artifact-stamp principle:
# no artifact is ambiguous about what it was built with).
if "$PCREC" -p rx --trace -o "$WORKDIR/st.c" -- '(a)b' >/dev/null 2>&1; then
    if grep -q '^#define RX_TRACE 1$' "$WORKDIR/st.c" \
       && grep -q 'TRACED ARTIFACT' "$WORKDIR/st.c"; then
        ok "[M4.5c] a traced artifact stamps RX_TRACE and says so in prose (D37: no artifact is ambiguous about what it was built with)"
    else
        bad "[M4.5c] a traced artifact carries no stamp saying so"
    fi
else
    bad "[M4.5c] could not compile a traced artifact"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "ir-listing: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
