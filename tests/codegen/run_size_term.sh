#!/usr/bin/env bash
# tests/codegen/run_size_term.sh — [ART-SIZE] the size term's structural check
# (D84; docs/design/artifact_size_term.md §7.4 item 4).
#
# IT READS THE ARTIFACT, NEVER THE STAMP ALONE. A stamp says what the compiler
# BELIEVES it did; this check asserts the artifact agrees — the emitted body
# copy count against the stamped K, the effective caps against the flags, and
# the six `_UNROLL_K_WHY` values against the path each one names.
#
# §5 IS WHY THIS SCRIPT BUILDS A SECOND COMPILER. `cap-rescue` — the path where
# the materiality bar declines a K and a cap takes it anyway — has a NATURAL
# POPULATION OF ZERO, and because the CLI overrides are RAISE-ONLY by ruling
# (D84 ruling 1) it cannot be forced from outside either. So the branch is
# driven through a REFERENCE COMPILER built with a cap lowered at pcrec's own
# compile time. That is [ENG-ABS]'s precedent, whose overflow arm has the same
# empty natural population and builds its reference compiler the same way; the
# three constants are `#ifndef`-overridable in src/core/limits.h for this one
# consumer, and the `-D` is a BUILD-time value so the raise-only rule stays
# true for every user of a shipped pcrec.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //"; }

NEST8='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'

# --- 1. the stamps exist and are UNCONDITIONAL on every VM artifact (D81) ----
"$PCREC" -p rx --features all -o "$WORK/plain.c" -- 'a(b|c)+d' 2>/dev/null
for m in UNROLL_K UNROLL_K_WHY MAX_EMIT_CODE_BYTES MAX_EMIT_BYTES; do
    if [ -n "$(stamp "$m" "$WORK/plain.c")" ]; then
        ok "RX_$m is stamped on an ordinary VM artifact (D81: unconditional)"
    else
        bad "RX_$m is MISSING on an ordinary VM artifact — a selection fact must be stamped whether or not it fired"
    fi
done

# --- 2. the WHY values, each driven through the path it names ----------------
why_is() { # pattern, extra-flags, expected
    local out="$WORK/w.c"
    # shellcheck disable=SC2086
    if ! "$PCREC" -p rx --features all $2 -o "$out" -- "$1" 2>/dev/null; then
        bad "_UNROLL_K_WHY '$3': the compile refused, so the path was never reached"; return
    fi
    local got; got="$(stamp UNROLL_K_WHY "$out" | tr -d '"')"
    [ "$got" = "$3" ] && ok "_UNROLL_K_WHY '$3' reached" \
                      || bad "_UNROLL_K_WHY expected '$3', artifact says '$got'"
}
why_is 'a(b|c)+d'  ''                 default
why_is 'a(b|c)+d'  '--unroll=4'       option
why_is 'a(b|c)+d'  '-fno-size-term'   denied
why_is "$NEST8"    ''                 size-model

# --- 3. the stamped K is the K the ARTIFACT was built at --------------------
# Read from the artifact rather than trusted: an explicit --unroll=K must
# appear as that K, and the size term's own choice must appear as its choice.
for k in 1 2 4 8; do
    "$PCREC" -p rx --features all --unroll=$k -o "$WORK/k.c" -- 'a(b|c)+d' 2>/dev/null
    got="$(stamp UNROLL_K "$WORK/k.c")"
    [ "$got" = "$k" ] && ok "--unroll=$k is stamped as $k" \
                      || bad "--unroll=$k stamped as '$got'"
done
"$PCREC" -p rx --features all -o "$WORK/n8.c" -- "$NEST8" 2>/dev/null
got="$(stamp UNROLL_K "$WORK/n8.c")"
[ "$got" = "1" ] && ok "the size term's chosen K (1) is on the artifact" \
                 || bad "the size term chose a K the artifact does not carry: '$got'"

# --- 4. the effective caps follow the flags --------------------------------
"$PCREC" -p rx --features all -o "$WORK/c1.c" -- 'a(b|c)+d' 2>/dev/null
[ "$(stamp MAX_EMIT_BYTES "$WORK/c1.c")" = "1000000" ] \
    && ok "the default total cap is stamped" || bad "default total cap stamp wrong"
"$PCREC" -p rx --features all --max-emit-bytes=4000000 -o "$WORK/c2.c" -- 'a(b|c)+d' 2>/dev/null
[ "$(stamp MAX_EMIT_BYTES "$WORK/c2.c")" = "4000000" ] \
    && ok "a raised total cap is stamped as the EFFECTIVE value" \
    || bad "a raised cap is not reflected in the stamp"
if "$PCREC" -p rx --max-emit-bytes=400000 -o "$WORK/c3.c" -- 'a' 2>/dev/null; then
    bad "--max-emit-bytes accepted a value BELOW the default; raise-only is what stops these being used to manufacture a refusal"
else
    ok "--max-emit-bytes is raise-only (a below-default value is refused)"
fi

# --- 5. cap-rescue, through a reference compiler with a LOWERED cap ---------
REF="$WORK/pcrec_lowcap"
srcs=$(find "$ROOT_DIR/src" -name '*.c' | tr '\n' ' ')
# shellcheck disable=SC2086
# BOTH constants move, and that is not belt-and-braces. The size term's
# threshold gates on CODE bytes, so lowering only the cap gives a compiler in
# which the ladder never runs on the witness (its 42,344 code bytes are under
# the shipped 120,000 threshold) and the pattern simply refuses at K=8. The
# rescue needs the ladder to RUN and then be overruled, which is threshold
# below the witness's code AND cap between its K=1 and K=8 code.
if $CC -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
       -DPCREC_SIZE_TERM_THRESHOLD=20000 \
       -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 \
       -o "$REF" "$ROOT_DIR/cli/main.c" $srcs 2>"$WORK/ref.err"; then
    ok "reference compiler built with the threshold at 20000 and the code cap at 30000"
    RESCUE='((a)|ab){0,2047}c'
    if "$REF" -p rx --features all -o "$WORK/r.c" -- "$RESCUE" 2>/dev/null; then
        got="$(stamp UNROLL_K_WHY "$WORK/r.c" | tr -d '"')"
        [ "$got" = "cap-rescue" ] \
            && ok "_UNROLL_K_WHY 'cap-rescue' reached (the bar declined this K; the lowered cap took it anyway)" \
            || bad "_UNROLL_K_WHY expected 'cap-rescue' under the lowered cap, got '$got'"
        # ANSWER IDENTITY: the rescued artifact must answer as the default build does
        "$PCREC" -p rx --features all -o "$WORK/d.c" -- "$RESCUE" 2>/dev/null
        rk="$(stamp UNROLL_K "$WORK/r.c")"; dk="$(stamp UNROLL_K "$WORK/d.c")"
        if [ "$rk" != "$dk" ]; then
            ok "the rescue chose a different K ($rk) from the default build ($dk) — the arms are not vacuously equal"
        else
            bad "the rescue and the default build chose the same K ($rk); this cell proves nothing"
        fi
    else
        bad "the cap-rescue witness '$RESCUE' did not compile under the lowered-cap compiler"
    fi
else
    bad "could not build the lowered-cap reference compiler: $(head -2 "$WORK/ref.err")"
fi

# --- 6. the NATURAL cap-rescue population is a CEILING, pinned at 0 ---------
# It is 0 today and the check says so loudly if that changes: a corpus pattern
# landing in the band (code between the corpus's worst and the cap) is the
# signal that the band this row could not measure has an inhabitant.
nat=0
while IFS= read -r p; do
    [ -n "$p" ] || continue
    if "$PCREC" -p rx --features all -o "$WORK/nat.c" -- "$p" 2>/dev/null; then
        [ "$(stamp UNROLL_K_WHY "$WORK/nat.c" | tr -d '"')" = "cap-rescue" ] && nat=$((nat+1))
    fi
done < <(grep -h '^pattern ' "$ROOT_DIR"/tests/*/*.rxt 2>/dev/null | sed 's/^pattern //' | sort -u | head -400)
if [ "$nat" -eq 0 ]; then
    ok "natural cap-rescue population is 0 (the ceiling holds; the branch is reachable only through a lowered-cap build)"
else
    bad "natural cap-rescue population is $nat, expected 0 — a real pattern now lands in the band docs/design/artifact_size_term.md §4.2b says is empty; re-derive that band, do not widen this pin"
fi

printf '\nchecks passed: %d\nchecks failed: %d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
