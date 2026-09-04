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
# [K37] every compiler invocation below is BOUNDED. gen_timeout.sh's
# `pcrec_run` is the project's one wrapper for that, and routing through it is
# not a formality here: this script compiles deliberately large patterns
# (a nested-repeat family, a cap-rescue witness) and an unbounded call on one
# of those is exactly the hang the rule exists to stop.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //"; }

# THE WHOLE CORPUS, NOT A PREFIX (r42 critic-sem S5). The ceiling scans below
# used `head -400`, a fixed 20 % prefix that cut at `(?:a|ab)*+` — and 10 of
# the 37 patterns the term acts on under a lowered threshold sit PAST the cut,
# so a ceiling pinned at 0 was pinned over a fifth of its own population. Same
# shape as the `m6read_samples` `head -n N` lesson. These scans are EMIT ONLY
# (no gcc), which is what makes the full population affordable.
# LC_ALL=C on the sort is K35, guarded here rather than inherited: under this
# box's ambient en_US.UTF-8 a bare `sort -u` MERGES patterns that differ only
# in punctuation — measured during r42 at 634 of 2,002 collapsed.
corpus_patterns() {
    grep -h '^pattern ' "$ROOT_DIR"/tests/*/*.rxt "$ROOT_DIR"/tests/*/*/*.rxt 2>/dev/null \
        | sed 's/^pattern //' | LC_ALL=C sort -u
}

NEST8='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'

# --- 1. the stamps exist and are UNCONDITIONAL on every VM artifact (D81) ----
pcrec_run "$PCREC" -p rx --features all -o "$WORK/plain.c" -- 'a(b|c)+d' 2>/dev/null
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
    if ! pcrec_run "$PCREC" -p rx --features all $2 -o "$out" -- "$1" 2>/dev/null; then
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
    pcrec_run "$PCREC" -p rx --features all --unroll=$k -o "$WORK/k.c" -- 'a(b|c)+d' 2>/dev/null
    got="$(stamp UNROLL_K "$WORK/k.c")"
    [ "$got" = "$k" ] && ok "--unroll=$k is stamped as $k" \
                      || bad "--unroll=$k stamped as '$got'"
done
pcrec_run "$PCREC" -p rx --features all -o "$WORK/n8.c" -- "$NEST8" 2>/dev/null
got="$(stamp UNROLL_K "$WORK/n8.c")"
[ "$got" = "1" ] && ok "the size term's chosen K (1) is on the artifact" \
                 || bad "the size term chose a K the artifact does not carry: '$got'"

# --- 4. the effective caps follow the flags --------------------------------
pcrec_run "$PCREC" -p rx --features all -o "$WORK/c1.c" -- 'a(b|c)+d' 2>/dev/null
[ "$(stamp MAX_EMIT_BYTES "$WORK/c1.c")" = "1000000" ] \
    && ok "the default total cap is stamped" || bad "default total cap stamp wrong"
pcrec_run "$PCREC" -p rx --features all --max-emit-bytes=4000000 -o "$WORK/c2.c" -- 'a(b|c)+d' 2>/dev/null
[ "$(stamp MAX_EMIT_BYTES "$WORK/c2.c")" = "4000000" ] \
    && ok "a raised total cap is stamped as the EFFECTIVE value" \
    || bad "a raised cap is not reflected in the stamp"
if pcrec_run "$PCREC" -p rx --max-emit-bytes=400000 -o "$WORK/c3.c" -- 'a' 2>/dev/null; then
    bad "--max-emit-bytes accepted a value BELOW the default; raise-only is what stops these being used to manufacture a refusal"
else
    ok "--max-emit-bytes is raise-only (a below-default value is refused)"
fi

# --- 4b. the TOTAL cap's stamp is on BOTH ENGINES -------------------------
# The total-bytes cap applies to whatever was emitted, not to one engine, so by
# D81 a DFA artifact must say which limit it was built under too. This cell
# exists because the emitter did NOT do that until the delivery size_diff
# caught it — `match_api.md` §6.3 and `limits.md` §8 both already claimed it,
# which is a spec/implementation divergence no check could see. Asserted on an
# artifact that is DFA by construction, and the VM-only stamps asserted ABSENT
# there in the same breath, so a future "stamp everything everywhere" change
# fails here rather than silently making `_UNROLL_K` meaningless on an engine
# with no counter rung.
pcrec_run "$PCREC" -p rx --features all -o "$WORK/dfa.c" -- 'abc' 2>/dev/null
if [ "$(stamp ENGINE "$WORK/dfa.c" | tr -d '"')" != "dfa" ]; then
    bad "the DFA-stamp cell's own pattern no longer selects the DFA engine — the cell is vacuous until its pattern is re-chosen"
else
    [ -n "$(stamp MAX_EMIT_BYTES "$WORK/dfa.c")" ] \
        && ok "RX_MAX_EMIT_BYTES is stamped on a DFA artifact (the total cap applies to both engines)" \
        || bad "RX_MAX_EMIT_BYTES is MISSING on a DFA artifact, but the cap applies to it and the spec says so"
    if [ -z "$(stamp UNROLL_K "$WORK/dfa.c")" ] && [ -z "$(stamp MAX_EMIT_CODE_BYTES "$WORK/dfa.c")" ]; then
        ok "the VM-only size stamps are ABSENT on a DFA artifact (no counter rung, so no K to report)"
    else
        bad "a VM-only size stamp appears on a DFA artifact — _UNROLL_K on an engine with no counter rung is a fact about nothing"
    fi
fi

# --- 5. cap-rescue, through a reference compiler with a LOWERED cap ---------
REF="$WORK/pcrec_lowcap"
srcs=$(find "$ROOT_DIR/src" -name '*.c' | tr '\n' ' ')
# shellcheck disable=SC2086
# BOTH constants move, and that is not belt-and-braces. The size term's
# threshold gates on CODE bytes, so lowering only the cap gives a compiler in
# which the ladder never runs on the witness (its code is under the shipped
# 120,000 threshold) and the pattern simply refuses at K=8. The rescue needs
# the ladder to RUN and then be OVERRULED, which is threshold below the
# witness's code AND cap between two of its ladder rungs.
#
# [OPT-4] 2026-08-29 — THE WITNESS CHANGED, AND WHY IT HAD TO. This cell used
# `((a)|ab){0,2047}c` against a 30,000 cap. That pattern is one of the 23 whose
# hybrid prefilter [OPT-4] rebuilds from the count-collapsed language, so its
# artifact shrank at every K and the cell's whole calibration went with it: at
# the new sizes the size model's own bar TAKES the rung (K1/K8 = 0.625, far
# under the materiality constant), so `_UNROLL_K_WHY` reads `size-model` and
# the cap is never asked. There is no threshold that restores `cap-rescue` for
# that pattern — the bar takes it at every one.
#
# The new witness is `(?:aa|a){8,12}+b`, chosen so this cell stops being
# COUPLED to the prefilter-language axis at all: it stamps
# `RX_VM_PREFILTER_LANG "exact"` (`exact nfa 55 <= 128`), i.e. it sits below
# [OPT-4]'s knee and its size cannot move when that knee or that lowering
# changes. Picking a witness that the axis under some other row's control
# cannot reach is the durable fix; re-deriving the constants against a
# collapsed pattern would only have deferred this.
#
# It is deliberately the SAME pattern §9's materiality cell pins as the one the
# bar DECLINES, and that makes the story here coherent rather than coincidental:
# this cell's claim is literally "the bar declined this K; the lowered cap took
# it anyway", so the two cells are the two halves of one witness's path. The
# ladder is { 6, 4, 3, 2, 1 } and this pattern's code is NON-MONOTONIC in K
# (K=6 is 35,427 B, LARGER than K=8's 35,157), which is what makes the
# largest-fitting assertion below bite: at a 31,000 cap the walk rejects 6 and
# takes 4 (30,347 B), and a ladder walked in the wrong direction would land on
# 1 (28,502 B) while still being "different from the default".
if $CC -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
       -DPCREC_SIZE_TERM_THRESHOLD=20000 \
       -DPCREC_MAX_VM_EMIT_CODE_BYTES=31000 \
       -o "$REF" "$ROOT_DIR/cli/main.c" $srcs 2>"$WORK/ref.err"; then
    ok "reference compiler built with the threshold at 20000 and the code cap at 31000"
    RESCUE='(?:aa|a){8,12}+b'
    if "$REF" -p rx --features all -o "$WORK/r.c" -- "$RESCUE" 2>/dev/null; then
        got="$(stamp UNROLL_K_WHY "$WORK/r.c" | tr -d '"')"
        [ "$got" = "cap-rescue" ] \
            && ok "_UNROLL_K_WHY 'cap-rescue' reached (the bar declined this K; the lowered cap took it anyway)" \
            || bad "_UNROLL_K_WHY expected 'cap-rescue' under the lowered cap, got '$got'"
        # ANSWER IDENTITY: the rescued artifact must answer as the default build does
        pcrec_run "$PCREC" -p rx --features all -o "$WORK/d.c" -- "$RESCUE" 2>/dev/null
        rk="$(stamp UNROLL_K "$WORK/r.c")"; dk="$(stamp UNROLL_K "$WORK/d.c")"
        if [ "$rk" != "$dk" ]; then
            ok "the rescue chose a different K ($rk) from the default build ($dk) — the arms are not vacuously equal"
        else
            bad "the rescue and the default build chose the same K ($rk); this cell proves nothing"
        fi
        # THE RESCUE MUST TAKE THE LARGEST FITTING K, PINNED (r42 critic-sem
        # S2). "different from the default" was too weak a claim: the loop
        # walked the ladder in the wrong direction for a release, taking the
        # SMALLEST fitting K (1) where 3 and 2 both fit, and this cell stayed
        # green throughout because 1 != 8. A rescue gives up as little
        # throughput as it can or it is not the rescue the design describes.
        if [ "$rk" = "4" ]; then
            ok "the rescue took the LARGEST fitting K (4) — not merely a different one"
        else
            bad "the rescue took K=$rk; under this reference build the ladder's rung 6 does NOT fit (35,427 B against the 31,000 cap) and rung 4 does (30,347 B), so the largest fitting rung is 4. A smaller K here means the ladder is being walked in the wrong direction"
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
    if pcrec_run "$PCREC" -p rx --features all -o "$WORK/nat.c" -- "$p" 2>/dev/null; then
        [ "$(stamp UNROLL_K_WHY "$WORK/nat.c" | tr -d '"')" = "cap-rescue" ] && nat=$((nat+1))
    fi
done < <(corpus_patterns)
if [ "$nat" -eq 0 ]; then
    ok "natural cap-rescue population is 0 (the ceiling holds; the branch is reachable only through a lowered-cap build)"
else
    bad "natural cap-rescue population is $nat, expected 0 — a real pattern now lands in the band docs/design/artifact_size_term.md §4.2b says is empty; re-derive that band, do not widen this pin"
fi

# --- 7. the DECLARED-CAPACITY FLOOR (§3.3a) --------------------------------
# `K` is answer-identical in the LANGUAGE and not in the DEPTH an artifact
# reaches: a smaller K raises the per-iteration frame need, so the same default
# budgets carry a shorter subject. A compiler-chosen K that turns a MATCH into
# a frames give-up is an answer change no flag asked for, so a rung whose
# artifact declares LESS capacity than the default K's is not a candidate.
#
# THIS BRANCH ALSO HAS A NATURAL POPULATION OF ZERO, and for a reason worth
# stating rather than discovering later: MEASURED over all 2,772 corpus
# patterns, 69 have a `.subject_ceiling`/`.frame_capacity` that MOVES with K,
# and NONE of the 69 has the counter rung — so no corpus pattern can reach the
# floor at all. §6's pin below has the same shape for cap-rescue. The witness
# is therefore synthetic and the threshold is lowered to reach it, exactly as
# §5 does.
CAPW='(((?:a{0,2}b)+c){0,20}d){0,20}e'
REF2="$WORK/pcrec_lowthr"
# shellcheck disable=SC2086
if $CC -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
       -DPCREC_SIZE_TERM_THRESHOLD=1000 \
       -o "$REF2" "$ROOT_DIR/cli/main.c" $srcs 2>"$WORK/ref2.err"; then
    ok "reference compiler built with the size-term threshold at 1000"

    # (a) the witness is REAL: its argmin is the rung the floor removes, and
    #     EVERY lower rung lowers the ceiling. Asserted from the artifacts, so
    #     the cell cannot go green on a witness that stopped witnessing.
    base_sc=""; worst_sc=""; argmin_k=""; argmin_n=""
    for k in 8 6 4 3 2 1; do
        pcrec_run "$PCREC" -p rx --features all --engine=vm --unroll=$k \
            -o "$WORK/cap$k.c" -- "$CAPW" 2>/dev/null || continue
        sc="$(grep -oE '\.subject_ceiling = [-0-9]+' "$WORK/cap$k.c" | grep -oE '[-0-9]+$')"
        n="$(grep -cE '^rx_L[0-9]+:' "$WORK/cap$k.c")"
        [ "$k" = 8 ] && base_sc="$sc"
        if [ -z "$argmin_n" ] || [ "$n" -lt "$argmin_n" ]; then argmin_n="$n"; argmin_k="$k"; worst_sc="$sc"; fi
    done
    if [ -n "$base_sc" ] && [ -n "$worst_sc" ] && [ "$argmin_k" != 8 ] && [ "$worst_sc" -lt "$base_sc" ]; then
        ok "the capacity witness is real: argmin is K=$argmin_k ($argmin_n nodes) and it declares subject_ceiling $worst_sc against the default K's $base_sc"
    else
        bad "the capacity witness no longer witnesses (base_sc=$base_sc argmin K=$argmin_k sc=$worst_sc) — re-choose it, do not weaken this cell"
    fi

    # (b) with the ladder RUNNING on it, the term must decline and say why
    if "$REF2" -p rx --features all --engine=vm -o "$WORK/cap.c" -- "$CAPW" 2>/dev/null; then
        why="$(stamp UNROLL_K_WHY "$WORK/cap.c" | tr -d '"')"
        gotk="$(stamp UNROLL_K "$WORK/cap.c")"
        gotsc="$(grep -oE '\.subject_ceiling = [-0-9]+' "$WORK/cap.c" | grep -oE '[-0-9]+$')"
        [ "$why" = "capacity-declined" ] \
            && ok "_UNROLL_K_WHY 'capacity-declined' reached (the K the term wanted would have lowered the declared capacity)" \
            || bad "_UNROLL_K_WHY expected 'capacity-declined' with the ladder running on the capacity witness, got '$why'"
        [ "$gotk" = "8" ] && [ "$gotsc" = "$base_sc" ] \
            && ok "the declined artifact keeps the DEFAULT K's declared capacity (K=$gotk, subject_ceiling=$gotsc)" \
            || bad "the term shipped K=$gotk with subject_ceiling=$gotsc; the floor must leave the default K's $base_sc intact"
    else
        bad "the capacity witness did not compile under the lowered-threshold compiler"
    fi

    # (c) ANTI-VACUITY: the same compiler must still TAKE a K where capacity
    #     is flat, or (b) would pass on a compiler whose ladder never runs.
    if "$REF2" -p rx --features all --engine=vm -o "$WORK/flat.c" -- '((a)|ab){0,12}c' 2>/dev/null; then
        fwhy="$(stamp UNROLL_K_WHY "$WORK/flat.c" | tr -d '"')"
        case "$fwhy" in
            size-model|size-model-declined|cap-rescue)
                ok "the lowered-threshold compiler's ladder DOES run and choose ('$fwhy' on a flat-capacity pattern) — (b) is not vacuous" ;;
            *) bad "the lowered-threshold compiler stamped '$fwhy' on a flat-capacity pattern: its ladder is not running, so the capacity cell above proves nothing" ;;
        esac
    else
        bad "the anti-vacuity pattern did not compile under the lowered-threshold compiler"
    fi
else
    bad "could not build the lowered-threshold reference compiler: $(head -2 "$WORK/ref2.err")"
fi

# --- 7b. the NATURAL capacity-floor population is a CEILING, pinned at 0 ----
# The floor can only bite where a pattern has the COUNTER rung (the ladder's
# own gate) AND its declared capacity moves with K. Measured at 0 today; this
# says so loudly if it changes, because the first inhabitant is the first
# pattern whose shipped K this floor actually moves.
natcap=0
while IFS= read -r p; do
    [ -n "$p" ] || continue
    pcrec_run "$PCREC" -p rx --features all --engine=vm --unroll=8 -o "$WORK/n8.c" -- "$p" 2>/dev/null || continue
    rungs="$(stamp VM_RUNGS "$WORK/n8.c")"
    case "$rungs" in *[!0-9a-fA-Fx]*|"") continue ;; esac
    [ $(( rungs & 0x10 )) -ne 0 ] || continue
    pcrec_run "$PCREC" -p rx --features all --engine=vm --unroll=1 -o "$WORK/n1.c" -- "$p" 2>/dev/null || continue
    s8="$(grep -oE '\.subject_ceiling = [-0-9]+' "$WORK/n8.c" | grep -oE '[-0-9]+$')"
    s1="$(grep -oE '\.subject_ceiling = [-0-9]+' "$WORK/n1.c" | grep -oE '[-0-9]+$')"
    [ -n "$s8" ] && [ -n "$s1" ] || continue
    [ "$s8" -gt 0 ] && { [ "$s1" -eq 0 ] || [ "$s1" -lt "$s8" ]; } && natcap=$((natcap+1))
done < <(corpus_patterns)
if [ "$natcap" -eq 0 ]; then
    ok "natural capacity-floor population is 0 (no corpus pattern has BOTH the counter rung and a K-sensitive declared capacity)"
else
    bad "natural capacity-floor population is $natcap — a real pattern now reaches the floor; record the acceptance change, do not widen this pin"
fi

# --- 8. a RAISE must never make a build fail that would have succeeded ------
# `limits.md` §8's promise, and it was briefly false (r42 critic-sem S1): the
# ladder's scratch bound is `3 x cap` in uint64, and any --max-emit-bytes above
# ULLONG_MAX/3 WRAPPED it to a tiny number. Every trial then aborted at its
# first append, the term fell through to the default K, and the CODE cap
# refused a pattern that compiles with no flag at all — a raise turning a
# success into a failure, which is exactly what the raise-only rule exists to
# prevent. The bound saturates now; this cell is the pin.
HUGE=6148914691236517206      # ULLONG_MAX/3 + 1, the smallest wrapping value
pcrec_run "$PCREC" -p rx --features all -o "$WORK/nr.c" -- "$NEST8" 2>/dev/null
base_k="$(stamp UNROLL_K "$WORK/nr.c")"
if pcrec_run "$PCREC" -p rx --features all --max-emit-bytes=$HUGE -o "$WORK/hr.c" -- "$NEST8" 2>/dev/null; then
    hk="$(stamp UNROLL_K "$WORK/hr.c")"
    [ -n "$base_k" ] && [ "$hk" = "$base_k" ] \
        && ok "--max-emit-bytes past ULLONG_MAX/3 compiles what the default compiles, at the same K ($hk) — the scratch bound saturates instead of wrapping" \
        || bad "a raised cap changed the chosen K ($base_k -> $hk): the ladder's scratch bound is not saturating"
else
    bad "--max-emit-bytes=$HUGE REFUSED a pattern that compiles with no flag — a raise must never make a build fail that would have succeeded (limits.md §8)"
fi

# --- 9. the MATERIALITY BAR, bracketed by a WITNESS POOL --------------------
#
# WHAT THIS BLOCK ASSERTS, and the distinction panel r53's checks critic had to
# force twice. The forced-`--unroll=K` ladder below is an INSTRUMENT: it yields
# each member's RATIO (argmin-over-K emitted code bytes / the default K's) so
# the table can be read. It is NOT the assertion. The ASSERTION is that the
# COMPILER'S OWN DECISION at the default — `<PREFIX>_UNROLL_K_WHY`, which reads
# `size-model` when the ladder TOOK a rung and `size-model-declined` /
# `capacity-declined` when it refused one — agrees with what that ratio
# PREDICTS against the materiality constant, for members on BOTH sides of it.
#
# THE FIRST VERSION OF THIS BLOCK DID NOT DO THAT AND WAS VACUOUS. It computed
# the ratios itself and compared them against a LITERAL `0.75` written in this
# script, so `src/core/compile.c`'s constant could be changed to 60 or 85 and
# every cell stayed green while the failure text still claimed "a constant of
# 0.70 or 0.80 would fail this file". Nothing in it read the compiler. The
# sabotage that proves the current shape is not vacuous is recorded in this
# lane's commit: with the constant at 70 and again at 85 in a scratch build,
# this block goes RED both ways, naming the members whose stamp stopped
# matching their prediction.
#
# THE POOL, AND WHY IT IS A POOL. This used to pin TWO fixed patterns' values.
# Both were alternation-bearing, so ONE emitter axis moved them together:
# [ENG-ISL]'s alternation island took `(?:aa|a){8,12}+b` below the bar and the
# bracket was gone. Island-free witnesses would only move the fragility to the
# next axis, so the shape changed instead. Each member carries a SHAPE tag, and
# the check requires at least two DISTINCT shapes on each side of the bar — one
# family straddling it on its own (which is what `(?:aa|a){8,12}+` with and
# without a trailing character amounted to) is one axis away from flattening.
#
# TWO MEMBERS ACTUALLY STAMP AN ISLAND, verified from the artifact rather than
# assumed. The first pool shipped labelled three members "island TAKEN" and NOT
# ONE of them stamped one — `((a)|ab)` was never eligible, because `(a)` is a
# capture inside a branch. That mislabel is why the `.island` column below is
# read off `<PREFIX>_VM_ALT_ISLANDS` and asserted, not written by hand.
#
# THE BAND (0.05) IS ASSERTED, NOT DERIVED. A straddling pair at 0.55 and 0.95
# would satisfy "one either side" while saying nothing about WHERE the constant
# is; requiring both members within 0.05 of the bar keeps the surviving claim
# close to "a constant of 0.70 or 0.80 fails this file". The number is a
# judgement about how tight a claim is worth keeping, and it is written here
# rather than computed so that moving it is a visible decision.
#
# NO STRADDLING PAIR IS RED WITH THE WHOLE TABLE — the honest "this population
# can no longer bracket the constant" finding, never a silent pass, and the
# failure says in as many words not to adjust the constant to make it green.
#
# THE QUANTITY IS THE ARGMIN RUNG'S BYTES against the default K's, NOT the
# delivered artifact's: for a DECLINED pattern the delivered artifact IS the
# K=8 artifact plus a longer stamp, so a ratio taken from it reads ~1.0004 for
# every declined pattern by construction. `--engine=vm` is load-bearing too —
# the DFA hybrid's prefilter tables are K-invariant and pull every ratio toward
# 1. Both run under §7's threshold-1000 reference compiler, because at the
# shipped threshold no witness reaches the ladder at all.
#
# Members are CORPUS patterns (tests/counterk/counterk.rxt) so that another
# lane's change to the corpus keeps them honest. Fields: pattern, shape tag.
POOL_PATTERNS='((a)|ab){4000}c	capture-alt
(?:[ab]a|[ab]){8,12}+b	class-leading
(?:ab|ba|aa|bb){24}c	island-4lit
(a{1,3}){64}	no-alternation
(a{10,20}){10,50}	no-alternation
(?:cat|cats|dog|dogs){12}z	island-4word
(?:aa|a){8,12}+b	narrow-aa-a
(?:[ab]a|[ab]){9,12}+b	class-leading
(?:ab|a){8,12}+b	narrow-ab-a'
BAR=0.75
BAND=0.05

if [ -x "$REF2" ]; then
    pool_rows=""; pool_n=0; pool_band=0; mismatch=0; islanded=0
    while IFS="$(printf '\t')" read -r ppat pshape; do
        [ -n "$ppat" ] || continue
        best=""; dflt=""
        for k in 1 2 3 4 5 6 7 8; do
            "$REF2" -p rx --features all --engine=vm --unroll=$k \
                --warn-emit-bytes=1 -o "$WORK/pool.c" -- "$ppat" \
                2>"$WORK/pool.err" || continue
            # [F9] HARD-FAIL rather than fall back to whole-file bytes. The
            # quantity this block acts on is COMMENT-EXCLUDED code bytes; the
            # file size is a different number, and silently substituting it is
            # the [ART-SIZE] quantity confusion learnings §3 records — a ratio
            # taken from the wrong quantity looked clean and was not.
            pb="$(sed -n 's/.*(\([0-9]*\) of code).*/\1/p' "$WORK/pool.err" | head -1)"
            if [ -z "$pb" ]; then
                echo "run_size_term.sh: FATAL: --warn-emit-bytes printed no '(N of code)' figure for pool member '$ppat' at K=$k. This block acts on COMMENT-EXCLUDED code bytes and must not substitute the file size for them; the warning's wording changed, or the flag stopped taking effect." >&2
                exit 2
            fi
            [ "$k" = 8 ] && dflt="$pb"
            if [ -z "$best" ] || [ "$pb" -lt "$best" ]; then best="$pb"; fi
        done
        if [ -z "$best" ] || [ -z "$dflt" ] || [ "$dflt" -le 0 ]; then
            bad "the pool member '$ppat' did not compile at the eight K values under the threshold-1000 reference compiler — a member that cannot be measured is not a member, and a pool that silently shrinks is how a bracket stops being one"
            continue
        fi
        r="$(awk "BEGIN{printf \"%.4f\", $best/$dflt}")"

        # THE COMPILER'S OWN DECISION at the default, and the island stamp,
        # both read off ONE artifact this block did not force a K on.
        "$REF2" -p rx --features all --engine=vm -o "$WORK/poold.c" -- "$ppat" \
            2>/dev/null || true
        why="$(sed -n 's/^#define RX_UNROLL_K_WHY "\([a-z-]*\)"$/\1/p' "$WORK/poold.c" | head -1)"
        isl="$(sed -n 's/^#define RX_VM_ALT_ISLANDS \([0-9]*\)$/\1/p' "$WORK/poold.c" | head -1)"
        [ "${isl:-0}" -gt 0 ] && islanded=$((islanded + 1))

        # PREDICTION from the ratio; VERDICT from the stamp.
        pred="$(awk "BEGIN{print ($r < $BAR) ? \"taken\" : \"declined\"}")"
        case "$why" in
            size-model)                         verdict=taken ;;
            size-model-declined|capacity-declined) verdict=declined ;;
            *)                                  verdict="none($why)" ;;
        esac
        inband="$(awk "BEGIN{d=$r-$BAR; if(d<0)d=-d; print (d<=$BAND)?\"y\":\"n\"}")"
        [ "$inband" = y ] && pool_band=$((pool_band + 1))
        [ "$verdict" != "$pred" ] && mismatch=$((mismatch + 1))
        pool_rows="$pool_rows$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
            "$ppat" "$pshape" "$r" "$pred" "$verdict" "$inband" "${isl:-0}")
"
        pool_n=$((pool_n + 1))
    done <<POOL_EOF
$POOL_PATTERNS
POOL_EOF

    echo "size-term §9 materiality pool (bar $BAR, band ±$BAND asserted; ratio = argmin-K code bytes / default-K code bytes, --engine=vm, threshold-1000 reference):"
    printf '  %-26s %-22s %-7s %-9s %-9s %-6s %s\n' pattern shape ratio predicts stamp-says in-band islands
    printf '%s' "$pool_rows" | while IFS="$(printf '\t')" read -r a b c d e f g; do
        [ -n "$a" ] || continue
        printf '  %-26s %-22s %-7s %-9s %-9s %-6s %s\n' "$a" "$b" "$c" "$d" "$e" "$f" "$g"
    done

    # distinct SHAPES on each side, counted over BAND-ELIGIBLE members only —
    # an out-of-band member says nothing about where the constant sits.
    below_shapes="$(printf '%s' "$pool_rows" | awk -F'\t' '$6=="y" && $4=="taken"    {print $2}' | LC_ALL=C sort -u | wc -l)"
    above_shapes="$(printf '%s' "$pool_rows" | awk -F'\t' '$6=="y" && $4=="declined" {print $2}' | LC_ALL=C sort -u | wc -l)"

    if [ "$mismatch" -ne 0 ]; then
        bad "$mismatch pool member(s) have a UNROLL_K_WHY stamp that disagrees with what their ratio predicts against $BAR. That is the materiality constant not being where this file says it is — read the table above; do NOT adjust the constant to make this green, and do not adjust the bar in this script either, which would only re-break the tie in the other direction."
    elif [ "$pool_band" -lt 4 ]; then
        bad "only $pool_band pool member(s) are within ±$BAND of $BAR (want at least 4): the pool still MEASURES the constant but has stopped BRACKETING it tightly, so the surviving claim is weaker than this file states"
    elif [ "$below_shapes" -lt 2 ] || [ "$above_shapes" -lt 2 ]; then
        bad "the band-eligible pool has $below_shapes distinct shape(s) below $BAR and $above_shapes above (want at least 2 each): a side carried by ONE shape is one emitter axis away from being flattened, which is exactly how the fixed PAIR this pool replaced failed"
    elif [ "$islanded" -lt 2 ]; then
        bad "only $islanded pool member(s) stamp RX_VM_ALT_ISLANDS > 0 (want at least 2): the pool has lost its coverage of the alternation-island axis, and the first version of this block labelled three members 'island TAKEN' when none was"
    else
        ok "the materiality bar is bracketed by a $pool_n-member pool: every member's UNROLL_K_WHY stamp matches what its ratio predicts against $BAR, $pool_band are within ±$BAND, both sides carry ≥2 distinct shapes ($below_shapes below / $above_shapes above), and $islanded stamp an alternation island"
    fi
else
    bad "the materiality pool needs §7's threshold-1000 reference compiler and it is not built"
fi

printf '\nchecks passed: %d\nchecks failed: %d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
