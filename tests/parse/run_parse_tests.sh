#!/usr/bin/env bash
# tests/parse/run_parse_tests.sh — PARSE-1's checks.
#
# Two things are asserted here and they are deliberately different in kind:
#
#   1. BRANCH COUNT CORRECTNESS (branch_count_check.c). pcrec's parser against
#      an independently-written reference counter, with the REFERENCE in turn
#      arbitrated by libpcre2's error-127/154 thresholds. Then SABOTAGED three
#      ways, because an unsabotaged green check is worth nothing: each sabotage
#      must make it FAIL, and this script fails if a sabotage passes.
#
#   2. AST IDENTITY. `(a|b)|c` and `a|b|c` must still generate identical C.
#      READ ITS CLAIM CAREFULLY: this property held BEFORE PARSE-1 existed, so
#      it is NOT evidence PARSE-1 was built or is correct — a build containing
#      none of PARSE-1 passes it. It is a REGRESSION net pointing forward: a
#      later edit that adds a group wrapper to the AST without pricing it (the
#      candidate-A shape PARSE-1 rejected) trips it. That is the only direction
#      it has power in, and it is worth keeping for exactly that.
#
# Usage: bash tests/parse/run_parse_tests.sh
# Env: CC (default gcc), PCREC (default <root>/build/pcrec), KEEP=1,
#   LIBPCREC (default <root>/build/libpcrec.a — SAN-1 override), SANFLAGS
#   (default empty — SAN-1: extra flags appended to branch_count_check.c)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
SANFLAGS="${SANFLAGS:-}"

LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
if [ ! -f "$LIB" ]; then
    echo "parse: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "parse: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- 1. branch count -------------------------------------------------------

BIN="$WORKDIR/branch_count_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" $SANFLAGS \
        -o "$BIN" "$SCRIPT_DIR/branch_count_check.c" "$LIB" -ldl; then
    echo "parse: FAILED TO BUILD branch_count_check.c" >&2
    exit 1
fi

if "$BIN"; then
    ok "branch count: pcrec agrees with the independent reference"
else
    bad "branch count: pcrec DISAGREES with the independent reference"
fi

# The sabotages. Each corrupts the REFERENCE counter in a way that a real
# mis-count would look like; each MUST be caught. A sabotage that passes means
# the check is not reading what it claims to read.
for sab in class escape off-by-one; do
    if PCREC_BC_SABOTAGE="$sab" "$BIN" >/dev/null 2>&1; then
        bad "sabotage '$sab' PASSED — the branch-count check is not live"
    else
        ok "sabotage '$sab' correctly caught"
    fi
done

# ---- 2. AST identity (a forward-pointing regression net, see header) --------
#
# The pairs are GENERATED rather than hand-listed: for each branch count and
# each position, wrap a proper sub-run in a group and require the emitted C to
# be unchanged. Hand-listing two pairs is how a check quietly narrows.
#
# [M4.4] (D43.1) SCOPES the comparison to the `rx_search` ENGINE BODY, not
# the whole file: `rx_info.pattern` now embeds the source pattern text
# unconditionally, and `flat`/`grouped` are, BY THIS CHECK'S OWN DESIGN,
# DIFFERENT pattern spellings (e.g. `a|b|c` vs `a|(b|c)`) that are AST-
# equivalent but textually distinct — so `rx_info.pattern` legitimately
# differs between them even when the compiled automaton (what this check
# actually cares about) does not. The same "the stamp differs by design"
# shape D37's tests/cli/ case9/case10 and [M4.4]'s own
# tests/codegen/CLAUDE.md OS-1 narrowing already established.
#
# [M4.5b] BOTH SIDES NOW COMPILE WITH --no-captures, and that is a
# re-statement of the property in the new vocabulary rather than a weakening.
#
# D42.1 makes captures ON by default, so `a|(b|c)` — this check's own grouped
# spelling — is a capture REQUEST and compiles to a VM artifact, while `a|b|c`
# stays on the DFA. The two emitted files then differ for a reason that has
# nothing to do with D31: the caller asked for different OUTPUT. That is
# engine_m4.md §9.2 item 3's announced behaviour change, not a regression, and
# it is pinned as its own check below rather than left to be rediscovered here.
#
# What D31 actually rules is that the group node is ERASED — that `(a|b)` and
# `(?:a|b)` produce the identical tree — and --no-captures is exactly the mode
# in which that erasure is still observable end-to-end (src/core/internal.h's
# A_CAP comment: with want_caps false, parse.c creates no capture node and the
# AST is D31's). So the pairs compare under --no-captures, and the check gets
# STRONGER for it: it now asserts the erasure survives the introduction of a
# capture node, which is the thing [M4.5b] could plausibly have broken.
rx_search_body() { # rx_search_body <whole-file-text-on-stdin>
    awk '
        # The `!~ ";$"` guard matches the DEFINITION, not the DECLARATION. A
        # self-contained artifact declares the entry near the top and defines
        # it far below, and both lines start `int rx_search(` -- so without it
        # this captured from the DECLARATION and swept up everything between.
        # [M6-READ] made that visible: the orientation block sits in that
        # window and QUOTES THE PATTERN, so two patterns with the same AST
        # emitted different "bodies" and all 9 pairs reported differing. The
        # same bug, and the same fix, as the body() helper in
        # tests/codegen/run_codegen_tests.sh. `tail -n +2` above skips the
        # line-1 pattern
        # comment; the orientation block is a SECOND place the pattern appears.
        $0 ~ /^int rx_search\(/ && $0 !~ /;[ \t]*$/ { inside = 1 }
        inside                  { print }
        inside && /^\}/         { exit }
    '
}
idpass=0; idfail=0
for n in 2 3 4 5; do
    for pos in 0 1 2; do
        [ "$pos" -ge $((n - 1)) ] && continue
        flat=""; grouped=""
        for ((b = 0; b < n; b++)); do
            atom="$(printf '%c' $((97 + b)))"
            [ -n "$flat" ] && flat="$flat|"
            flat="$flat$atom"
        done
        # group the sub-run starting at $pos, of length 2
        grouped=""
        for ((b = 0; b < n; b++)); do
            atom="$(printf '%c' $((97 + b)))"
            if [ "$b" -eq "$pos" ]; then
                nxt="$(printf '%c' $((97 + b + 1)))"
                [ -n "$grouped" ] && grouped="$grouped|"
                grouped="$grouped($atom|$nxt)"
            elif [ "$b" -eq $((pos + 1)) ]; then
                continue
            else
                [ -n "$grouped" ] && grouped="$grouped|"
                grouped="$grouped$atom"
            fi
        done
        a_out="$("$PCREC" -p rx --no-captures -o - -- "$flat" 2>/dev/null | tail -n +2 | rx_search_body)"
        b_out="$("$PCREC" -p rx --no-captures -o - -- "$grouped" 2>/dev/null | tail -n +2 | rx_search_body)"
        if [ -z "$a_out" ] || [ -z "$b_out" ]; then
            # An empty extraction must be a FAILURE, not a match of two empty
            # strings: if the emitted signature ever stops matching
            # rx_search_body's anchor, every pair would otherwise "pass"
            # while comparing nothing (the vacuous-check class the codegen
            # suite's body() helper already guards with its own -s test).
            idfail=$((idfail + 1)); echo "  ast-identity: EMPTY rx_search body extraction: '$flat' vs '$grouped'" >&2
        elif [ "$a_out" = "$b_out" ]; then idpass=$((idpass + 1))
        else idfail=$((idfail + 1)); echo "  ast-identity differs: '$flat' vs '$grouped'" >&2
        fi
    done
done
if [ "$idpass" -eq 0 ] && [ "$idfail" -eq 0 ]; then
    # Ordering matters here and it cost a diagnosis once ([M4.5b]): the
    # vacuous-check guard used to fire on `idpass == 0` ALONE, so a run where
    # every pair genuinely DIFFERED reported "the check asserted nothing" and
    # buried nine real differences under a message about coverage. Vacuity is
    # "no pair was compared at all", which is both counters at zero.
    bad "ast-identity: NO pair was compared — the check asserted nothing"
elif [ "$idfail" -eq 0 ]; then
    ok "ast-identity: $idpass generated pairs emit identical C (regression net; see header)"
else
    bad "ast-identity: $idfail of $((idpass + idfail)) generated pairs differ"
fi

# ---- 2b. [M4.5b] the OTHER half: the announced behaviour change ------------
#
# The check above deliberately compiles with --no-captures, so on its own it
# would let the DEFAULT behaviour drift unobserved. engine_m4.md §9.2 item 3
# says the same invocation that compiles a scanning matcher today emits a
# capture-tracking one after M4, and that it "should be announced as one
# boundary with two items, not discovered as a surprise by whoever ports
# first". Pinning it here is what makes the --no-captures scoping above a
# NARROWING of what this check covers rather than a hole in it.
def_out="$("$PCREC" -p rx -o - -- 'a|(b|c)' 2>/dev/null)"
nc_out="$("$PCREC" -p rx --no-captures -o - -- 'a|(b|c)' 2>/dev/null)"
if [ -z "$def_out" ] || [ -z "$nc_out" ]; then
    bad "ast-identity/default: 'a|(b|c)' would not compile"
elif printf '%s' "$def_out" | grep -q '^#define RX_NCAPS 2$' \
     && printf '%s' "$def_out" | grep -q '^#define RX_ENGINE "vm"$' \
     && printf '%s' "$nc_out" | grep -q '^#define RX_NCAPS 1$' \
     && ! printf '%s' "$nc_out" | grep -q 'RX_ENGINE'; then
    ok "ast-identity/default: the SAME grouped spelling emits a capture-tracking VM artifact by default and today's DFA artifact under --no-captures (§9.2 item 3's announced change, pinned)"
else
    bad "ast-identity/default: 'a|(b|c)' did not produce RX_NCAPS 2 + VM by default and RX_NCAPS 1 + DFA under --no-captures"
fi

# ---- 3. the depth discipline ----------------------------------------------
#
# The CAP and the BALANCE are asserted here, both sides each, and all four
# sabotages were verified live before this shipped (double-decrement,
# no-decrement, no-increment, off-by-one cap). Note the ordering lesson baked
# into the two blocks below: the cap probes ALONE were measured BLIND to a
# double-decrement, because a purely nested pattern only tests the cap on the
# way in. The balance probes exist because of that measurement, not by
# foresight.
#
# What remains unasserted is narrower than the first cut of this file claimed,
# and the claim is corrected rather than repeated: those properties are
# UNOBSERVED, not unobservable. A fixture doorway gated on a selector byte no
# registry row uses makes them testable today without any module — so the
# SKIP-vs-check_tail_precedence question they were framed around is moot for
# them, and MOD-0.1 should ship real checks rather than either precedent.
echo
echo "  *** NOT ASSERTED HERE, stated so a green run is not mistaken for"
echo "  *** coverage — and note these are NOT unobservable, only unobserved:"
echo "  ***  - depth balance across a doorway that RETURNS. No REAL syntax can"
echo "  ***    reach it: every doorway is noreturn today (ext.c has zero return"
echo "  ***    statements on any path). But a FIXTURE doorway gated on a"
echo "  ***    selector byte no registry row uses makes it observable NOW,"
echo "  ***    without waiting for a module — demonstrated by the R11 panel,"
echo "  ***    which used exactly that stub to reproduce the silent-discard"
echo "  ***    miscompile. MOD-0.1 should ship it as a real check, not a SKIP."
echo "  ***  - caseless save/restore around a group body: LIVE since MOD-0.5c"
echo "  ***    (cx->mods, written by module 'modifiers'). Same"
echo "  ***    fixture technique applies. First REAL writer is 'modifiers'"
echo "  ***    (MOD-0.5), whose measured rule is: restore at the IMMEDIATELY"
echo "  ***    enclosing ')', leaking across that group's sibling branches."
echo "  *** The depth CAP itself IS asserted below, both sides."
echo

# The depth cap, both sides, generated rather than hand-picked. R7 measured the
# cost of testing one half of a two-sided rule. A double-decrement fails OPEN,
# which is the dangerous direction, so the ok-side matters as much as the fail.
capfail=0
for n in 249 250 251 252; do
    pat="$(python3 -c "print('('*$n + 'a' + ')'*$n)")"
    if "$PCREC" -p rx -o "$WORKDIR/depth.c" -- "$pat" >/dev/null 2>&1; then r=ok; else r=fail; fi
    case "$n:$r" in
        249:ok|250:ok|251:fail|252:fail) ;;
        *) capfail=$((capfail + 1)); echo "  depth cap: n=$n gave $r" >&2 ;;
    esac
done
# and the same boundary for (?:...), which shares the code path
for n in 250 251; do
    pat="$(python3 -c "print('(?:'*$n + 'a' + ')'*$n)")"
    if "$PCREC" -p rx -o "$WORKDIR/depth.c" -- "$pat" >/dev/null 2>&1; then r=ok; else r=fail; fi
    case "$n:$r" in 250:ok|251:fail) ;; *) capfail=$((capfail+1)); echo "  depth cap (?:): n=$n gave $r" >&2 ;; esac
done
if [ "$capfail" -eq 0 ]; then
    ok "depth cap: 250 accepted / 251 rejected, both sides, for (...) and (?:...)"
else
    bad "depth cap: $capfail boundary probes wrong"
fi

# DEPTH BALANCE, which the cap probes above CANNOT see — and that blindness was
# measured, not guessed. A double-decrement (`cx->depth--` twice) passes every
# probe above, because a purely nested pattern only ever tests the cap on the
# way IN; the leak shows up on the way OUT and nothing above looks there. It
# fails OPEN, which is the dangerous direction.
#
# The input that catches it: SEQUENTIAL groups FIRST, then a nest one past the
# cap. Each unbalanced exit leaks a decrement, so the later nest starts from a
# depth below zero and a 251-deep nest is wrongly accepted.
balfail=0
for lead in 1 5 20; do
    pat="$(python3 -c "print('(a)'*$lead + '('*251 + 'b' + ')'*251)")"
    if "$PCREC" -p rx -o "$WORKDIR/depth.c" -- "$pat" >/dev/null 2>&1; then
        balfail=$((balfail + 1))
        echo "  depth balance: ${lead}x'(a)' then a 251-deep nest was ACCEPTED — a" >&2
        echo "  decrement is leaking, so the cap can be exceeded." >&2
    fi
done
# The OTHER direction, which the probes above are equally blind to: a MISSING
# decrement makes depth accumulate monotonically, so a long run of SHALLOW
# sibling groups eventually trips the cap. That fails CLOSED — it rejects valid
# patterns rather than accepting invalid ones — which is why it needs its own
# probe rather than being caught by the ones above. Max real depth here is 1.
for many in 300 600; do
    pat="$(python3 -c "print('(a)'*$many)")"
    if ! "$PCREC" -p rx -o "$WORKDIR/depth.c" -- "$pat" >/dev/null 2>&1; then
        balfail=$((balfail + 1))
        echo "  depth balance: $many SEQUENTIAL groups (real depth 1) were REJECTED —" >&2
        echo "  a decrement is missing, so depth accumulates across siblings." >&2
    fi
done
if [ "$balfail" -eq 0 ]; then
    ok "depth balance: neither a leaked nor a missing decrement survives (5 probes, both directions)"
else
    bad "depth balance: $balfail probes wrong"
fi


# ---- 4. the group diagnostic has exactly ONE home --------------------------
#
# Total, terminating, no generated space, no oracle — the properties D30 §2
# wants in a primary instrument. `pcrec_parse_body` hands a module the body and
# lets the CALLER consume its own `)`, so the day a module doorway starts
# returning, the tempting mistake is to copy this base-tier wording into it
# rather than write the construct-appropriate PCRE2 one. A construct with two
# homes drifts (D24, and `\v` is why that rule exists).
# Count CALL SITES, not mentions. The first cut of this check grepped for the
# bare string and scored 3 on a correct tree, because two of the hits were
# comments in this very repository explaining that the string is single-homed —
# a check that counts prose about itself. Anchoring on `ctx_fail(` is what makes
# it read code.
homes=$(grep -rc 'ctx_fail([^)]*"missing closing ) for group"' "$ROOT_DIR/src" --include='*.c' | awk -F: '{s += $2} END {print s+0}')
if [ "$homes" -eq 1 ]; then
    ok "group diagnostic: \"missing closing ) for group\" has exactly one home in src/"
else
    bad "group diagnostic: found $homes copies in src/, expected exactly 1 — a module has probably copied the base-tier wording instead of writing its own"
fi

echo "checks passed: $pass"
if [ "$fail" -gt 0 ]; then echo "checks FAILED: $fail" >&2; exit 1; fi
exit 0
