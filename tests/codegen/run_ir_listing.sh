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

# D45 (docs/dev/decisions.md): every compile of GENERATED C in this file runs
# under the shared budget -- a timeout is a FAILURE naming the case, never a
# hang. One implementation for the whole tree.
#
# EXECUTION of the trace-check plain/traced binaries below is bounded too
# (gen_run, same file): a handful of runs per pattern, not an inner loop.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="codegen"

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

    # ---- the CAP's own counter, against the artifact ---------------------
    # PCREC_MAX_VM_RESUME_POINTS is checked against a PRE-PASS count, before a
    # byte is emitted — so the cap is only as good as that count matching what
    # the emitter goes on to write. Under-count and an artifact the cap exists
    # to stop sails through. The listing reports the pre-pass number; this
    # compares it to the `&&label` operands actually emitted.
    ir_rp="$(grep -oE '^; resume pts +[0-9]+' "$d/ir" | grep -oE '[0-9]+')"
    c_rp="$(grep -oE '&&rx_L[0-9]+' "$d/gen.c" | wc -l)"
    if [ -n "$ir_rp" ] && [ "$ir_rp" = "$c_rp" ]; then
        ok "ir-listing[$pat]: the cap's pre-pass count ($ir_rp resume points) equals the artifact's emitted RX_PUSH sites"
    else
        bad "ir-listing[$pat]: the cap counts $ir_rp resume points but the artifact emits $c_rp — PCREC_MAX_VM_RESUME_POINTS is being checked against the wrong number"
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

# ---- PCREC_MAX_VM_REPEAT_COPIES, at its boundary ------------------------
#
# D45's consequence 1: PCREC_MAX_VM_NODES let ((a)|b){0,4000}c emit 3.5 MB.
# The replication cap is the compiler-side bound that stops it. Checked at the
# boundary in BOTH directions, because a cap that refuses everything and a cap
# that refuses nothing both pass a one-sided test.
#
# EVERY ROW BELOW NOW PASSES `-fno-revdet`, and the reason is the endgame rather
# than an inconvenience ([ENG-BREP] rung-select, 2026-08-16). The cap bounds the
# REPLICATION STRATEGY, and `((a)|b){0,N}c` is no longer replicated: the
# reverse-deterministic rung emits it as one body copy at 293 lines whatever N
# is, so at the default it sails past a cap that has nothing to count. Denying
# the rung puts the quantifier back on the frames rung, which is where
# replication — and therefore the cap — lives. That is D46's pin-the-selection
# rule, and it keeps this block testing the cap instead of testing which rung
# won. The endgame itself is asserted separately, below.
#
# `-fno-counter` joins it (2026-08-17, the counter-K landing) by the same rule
# one rung further down: counter-K also replaces replication for this shape, so
# a cap that COUNTS REPLICATED COPIES cannot be tested by a build that does not
# replicate. Both denials are needed, not either — with only one, the other rung
# absorbs the shape and every assertion below goes quiet in the direction that
# reads as PASS for the 64-copy cell and FAIL for the two refusal cells.
if "$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_ok.c" -- '((a)|b){0,64}c' >/dev/null 2>&1; then
    ok "[M4.5c] the replication cap ADMITS the largest legal artifact (64 copies, $(stat -c %s "$WORKDIR/cap_ok.c") bytes)"
else
    bad "[M4.5c] '((a)|b){0,64}c' was refused under -fno-revdet -fno-counter; it is exactly at the cap and must compile"
fi
if out="$("$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_no.c" -- '((a)|b){0,65}c' 2>&1)"; then
    bad "[M4.5c] '((a)|b){0,65}c' compiled under -fno-revdet -fno-counter; it is one copy over the cap and must be refused"
elif printf '%s' "$out" | grep -q 'replicate its body 65 times' \
     && printf '%s' "$out" | grep -q 'span loop'; then
    ok "[M4.5c] ...and REFUSES one copy over it, naming the count, the limit and the way out"
else
    bad "[M4.5c] refused over the cap, but the diagnostic does not name the count and the fix: $out"
fi
# the case D45 was ruled over
if "$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_d45.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1; then
    bad "[M4.5c] '((a)|b){0,4000}c' still compiles under -fno-revdet -fno-counter — this is the 3.5 MB artifact that pegged cc1 for 100+ minutes (D45)"
else
    ok "[M4.5c] '((a)|b){0,4000}c' — D45's own case — is refused before emitting anything, whenever replication is the strategy"
fi
#
# ---- D47.1's ENDGAME, now that it has arrived ---------------------------
#
# D45's follow-up said the emitted-size cap was an INTERIM backstop and named
# [ENG-BREP]'s ladder as the endgame; D47.1 named this rung specifically. So the
# same pattern that must be REFUSED under replication must COMPILE at the
# default, small, and the two facts belong next to each other — a reader who
# sees only the refusal above would reasonably conclude pcrec still cannot do
# this.
if "$PCREC" -p rx -o "$WORKDIR/endgame.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1; then
    eg_lines="$(wc -l < "$WORKDIR/endgame.c")"
    if [ "$eg_lines" -lt 2000 ]; then
        ok "[ENG-BREP] D45's endgame: the SAME pattern compiles at the default in $eg_lines lines (the reverse-deterministic rung emits one body copy, so the count stops driving the size)"
    else
        bad "[ENG-BREP] '((a)|b){0,4000}c' compiled but emitted $eg_lines lines — the rung is meant to make the count irrelevant to the emitted size"
    fi
else
    bad "[ENG-BREP] '((a)|b){0,4000}c' does not compile at the default; D47.1 names this rung's arrival as when D45's refuse-cap endgame lands"
fi
#
# ...and the cap must NOT refuse a pattern whose size is PROPORTIONATE to what
# its author wrote. A first draft capped TOTAL resume points instead of
# replication and refused a 200-branch capture-bearing keyword alternation —
# 199 resume points, and MEASURED 0.50 s at -O2 for the 100-branch version, so
# nothing about it is pathological. The defect is disproportion, not size, and
# a cap that cannot tell them apart refuses the wrong patterns.
wide="($(python3 -c "print('|'.join('kw%d' % i for i in range(500)))"))"
if "$PCREC" -p rx -o "$WORKDIR/wide.c" -- "$wide" >/dev/null 2>&1; then
    ok "[M4.5c] a 500-branch capture-bearing alternation still compiles — the cap targets REPLICATION, not size"
else
    bad "[M4.5c] a 500-branch capture-bearing alternation was refused; its size is proportionate to the pattern and the cap must not bite it"
fi
# a single-path body never replicates, whatever the count (S2.5's cursor rung)
if "$PCREC" -p rx -o "$WORKDIR/span.c" -- '(ab){0,4000}c' >/dev/null 2>&1; then
    ok "[M4.5c] '(ab){0,4000}c' compiles: a single-path body takes the span-loop rung and replicates nothing"
else
    bad "[M4.5c] '(ab){0,4000}c' was refused; it has no choice point, so the cap must not see it"
fi

# ---- a NON-DEFAULT --prefix ---------------------------------------------
#
# Every check above uses the default `rx`, which cannot see a hardcoded `RX_`
# in the listing's own text — and there was one: the header named RX_NCAPS
# whatever --prefix said, pointing a reader of a `-p myrx` listing at a macro
# the artifact does not contain. Cheap to check, invisible without it.
mkdir -p "$WORKDIR/pfx"
if "$PCREC" -p myrx -o "$WORKDIR/pfx/gen.c" -- '(a)b' >/dev/null 2>&1    && "$PCREC" -p myrx --emit-ir -- '(a)b' > "$WORKDIR/pfx/ir" 2>&1; then
    if grep -qE '(^|[^A-Z_])RX_' "$WORKDIR/pfx/ir"; then
        bad "[M4.5c] a -p myrx listing still names RX_* macros: $(grep -m1 'RX_' "$WORKDIR/pfx/ir")"
    elif grep -q 'MYRX_NCAPS' "$WORKDIR/pfx/ir"          && grep -q '^#define MYRX_NCAPS' "$WORKDIR/pfx/gen.c" "$WORKDIR/pfx/gen.h"; then
        ok "[M4.5c] the listing names the artifact's OWN macros under a non-default --prefix"
    else
        bad "[M4.5c] a -p myrx listing does not name MYRX_NCAPS, or the artifact does not define it"
    fi
    # the label set must still line up under a different prefix
    grep -oE '^myrx_L[0-9]+:' "$WORKDIR/pfx/gen.c" | tr -d ':' | sed 's/^myrx_L//' | sort -n > "$WORKDIR/pfx/c.l"
    grep -oE '^  L[0-9]+' "$WORKDIR/pfx/ir" | sed 's/^ *L//' | sort -n > "$WORKDIR/pfx/i.l"
    if [ -s "$WORKDIR/pfx/c.l" ] && diff -q "$WORKDIR/pfx/c.l" "$WORKDIR/pfx/i.l" >/dev/null; then
        ok "[M4.5c] ...and its label set matches the artifact's too"
    else
        bad "[M4.5c] -p myrx: label sets differ between the .c and the listing"
    fi
else
    bad "[M4.5c] could not produce a -p myrx artifact and listing"
fi

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
    gen_cc "trace plain '$pat'" "$CC" $GENCFLAGS -I "$d/plain" -o "$d/plain/t" "$d/plain/gen.c" \
        || { trace_ok=0; echo "  trace: plain build failed: $(printf '%s' "$GEN_CC_LOG" | head -3)" >&2; break; }
    # shellcheck disable=SC2086
    gen_cc "trace TRACED '$pat'" "$CC" $GENCFLAGS -I "$d/traced" -o "$d/traced/t" "$d/traced/gen.c" \
        || { trace_ok=0; echo "  trace: TRACED build failed: $(printf '%s' "$GEN_CC_LOG" | head -3)" >&2; break; }
    for subj in abcd xxabcd aab bbb '' a aaa; do
        p_out="$(gen_run "ir-listing trace plain '$pat' '$subj'" "$d/plain/t" "$subj" 2>/dev/null)"
        t_out="$(gen_run "ir-listing trace TRACED '$pat' '$subj'" "$d/traced/t" "$subj" 2>/dev/null)"
        if [ "$p_out" != "$t_out" ]; then
            bad "[M4.5c] --trace CHANGED THE ANSWER for '$pat' on \"$subj\": plain '$p_out' vs traced '$t_out'"
            trace_ok=0
        fi
    done
    # ...and it must actually trace: a silent "instrumented" build is the
    # vacuous-check shape (the trace fires on stderr, the result on stdout).
    if ! gen_run "ir-listing trace stderr TRACED '$pat'" "$d/traced/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
        bad "[M4.5c] --trace produced no trace output for '$pat' — the instrumentation is not live"
        trace_ok=0
    fi
    if gen_run "ir-listing trace stderr plain '$pat'" "$d/plain/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
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
