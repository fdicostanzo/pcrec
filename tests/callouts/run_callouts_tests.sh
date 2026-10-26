#!/usr/bin/env bash
# tests/callouts/run_callouts_tests.sh — module `callouts` ([INLINE-C] stage
# 1b; docs/spec/match_api.md §11): `make test-callouts`.
#
# SIX ARMS:
#   (1) the corpus: tests/harness/run.sh over this directory (the bindings
#       link through harness.manifest);
#   (2) the oracle: verify_callouts.py, every corpus cell against libpcre2
#       with its answer-moving optimizations off;
#   (3) the generated differential: gen_diff.py, a seeded population (floor
#       1,000 compiled AND compared patterns) against the same oracle, plus
#       the firing-class bound read off each artifact's own listing;
#   (4) the driver checks (checks.c): the view (A2, A4, A5, an enclosing
#       group), give-up propagation, the step charge, DT-4.1, an artifact as
#       a consuming callee, and three traps;
#   (5) the firing-class table (inline_c.md §1.10's examples) as `--emit-ir`
#       expectations, and `once` accepted on classes 1-2, refused on 3;
#   (6) the refusals: the malformed forms with the module on and off, a `__`
#       binding name, `--emit-main`.
# Arms 2 and 3 SKIP LOUDLY when libpcre2 is absent (PC-3's shape).
#
# Env: PCREC, CC, GENCFLAGS (the harness's own); CALLOUT_GEN_N (arm 3's
# population, default 1200), CALLOUT_GEN_FLOOR (default 1000).
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra}"

pass=0; fail=0; skip=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
note() { echo "SKIP: $1" >&2; skip=$((skip + 1)); }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ---- arm 1: the corpus ----------------------------------------------------
echo "== [INLINE-C] the callouts corpus =="
if PCREC="$PCREC" bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/"; then
    ok "the tests/callouts/ corpus: every case answers what its .rxt file says"
else
    bad "the tests/callouts/ corpus has failing cases — see above"
fi

# ---- arm 2: the corpus oracle ----------------------------------------------
echo
echo "== [INLINE-C] the corpus against libpcre2 =="
python3 "$SCRIPT_DIR/verify_callouts.py" "$SCRIPT_DIR"/*.rxt
case $? in
    0) ok "libpcre2 agrees with every cell in tests/callouts/" ;;
    3) note "libpcre2 is unavailable: the corpus is scored against its own file only" ;;
    *) bad "libpcre2 disagrees with the corpus, or the sweep checked nothing" ;;
esac

# ---- arm 3: the generated differential -------------------------------------
echo
echo "== [INLINE-C] the generated differential =="
"$TIMEOUT_BIN" 1800 python3 "$SCRIPT_DIR/gen_diff.py" --pcrec "$PCREC" \
    --work "$WORK/gen" --n "${CALLOUT_GEN_N:-1200}" \
    --floor "${CALLOUT_GEN_FLOOR:-1000}" --cc "$CC" --cflags "$GENCFLAGS"
case $? in
    0) ok "the generated population agrees with libpcre2 and keeps every firing-class bound" ;;
    3) note "libpcre2 is unavailable: the generated differential did not run" ;;
    *) bad "the generated differential found a disagreement, a class-bound violation, or missed its floor" ;;
esac

# ---- arm 4: the driver checks ----------------------------------------------
echo
echo "== [INLINE-C] the driver checks =="
D="$WORK/drv"
mkdir -p "$D"
# prefix | flags | pattern
built=1
while IFS='|' read -r px fl pat; do
    [ -z "$px" ] && continue
    # shellcheck disable=SC2086
    if ! "$TIMEOUT_BIN" 60 "$PCREC" -p "$px" --features all $fl -o "$D/$px.c" --pattern "$pat"; then
        bad "pcrec refused the check artifact $px: $pat"
        built=0
    fi
done <<'EOF'
va||(?:(?C"see")(a))+
vb||(?:(?C"see")(a)|(b))+
vk||a\Kb(?C"see")c
vn|--no-captures|(a)b(?C"g1set")
vc|--no-captures|(a)b(?C"see")
ve||(a(?C"see1")b)+
gs||(a+)(?C"steps")b
gf|--backtrack-frames=200000|(a+)(?C"frames")b
sc|--step-budget=5|a(?C"veto")
dt||(\d+)(?C"count")x|(\d+)y
in1||\d\d
ou||x(?C"octet,consume")y
tf||a(?C"far,consume")
tu|-e utf8|(?C"one,consume")
tp||a(?C"one")
EOF
if [ "$built" = 1 ]; then
    if ! grep -q '_deep(' "$D/gf.c"; then
        bad "the FRAMES check's artifact gf is not tiered, so the check cannot reach the tier boundary"
    fi
    objs=()
    for c in "$D"/*.c; do objs+=("$c"); done
    # shellcheck disable=SC2086
    if $CC $GENCFLAGS -DGF_TEST_TIER_HOOK -I"$D" -I"$SCRIPT_DIR" -o "$D/checks" \
            "$SCRIPT_DIR/checks.c" "${objs[@]}" \
            -include "$D/va.h" "$SCRIPT_DIR/stubs.c" 2> "$D/cc.log"; then
        if "$TIMEOUT_BIN" 60 "$D/checks"; then
            ok "every driver check passed"
        else
            bad "a driver check failed — see above"
        fi
        for t in overlong midchar pred1; do
            "$TIMEOUT_BIN" 30 "$D/checks" trap "$t" > "$D/trap.out" 2>&1
            rc=$?
            if [ "$rc" -gt 128 ] && [ "$rc" -ne 124 ]; then
                ok "trap '$t': the call site trapped (exit $rc)"
            else
                bad "trap '$t': expected a trap, got exit $rc: $(cat "$D/trap.out")"
            fi
        done
    else
        bad "the driver checks did not build: $(head -20 "$D/cc.log")"
    fi
fi

# ---- arm 5: the firing-class table -----------------------------------------
echo
echo "== [INLINE-C] the firing classes (inline_c.md §1.10) =="
# pattern TAB class TAB tail (the listing's `tail` column)
while IFS=$'\t' read -r pat cls tl; do
    [ -z "$pat" ] && continue
    row="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-ir --pattern "$pat" 2>&1 |
           awk -F'\t' '/^#section/{s=($0=="#section callouts")} s && !/^#/{print $5 "|" $6; exit}')"
    if [ "$row" = "$cls|$tl" ]; then
        ok "class of $pat is $cls (tail $tl)"
    else
        bad "class of $pat: want $cls|$tl, listing says '$row'"
    fi
    once="${pat/(?C1)/(?C\"q,once\")}"
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/once.c" --pattern "$once" 2>&1)"
    rc=$?
    if [ "$cls" = repeated ]; then
        if [ $rc -ne 0 ] && printf '%s' "$out" | grep -q 'is marked once but can fire again'; then
            ok "once refused on $once"
        else
            bad "once on $once: want a refusal naming the cause, got exit $rc: $out"
        fi
    elif [ $rc -eq 0 ]; then
        ok "once accepted on $once"
    else
        bad "once on $once: want acceptance, got: $out"
    fi
done <<'EOF'
abc(?C1)	once-per-match	tail
a(?C1)b	once-per-start	-
(?:x(?C1)|y)z	once-per-start	-
^(\d+)(?C1)$	repeated	-
^(\d++)(?C1)$	once-per-start	-
(?>\w+@\w+)(?C1)	once-per-match	tail
\w+(?C1)	repeated	tail
(?:x|y)(?C1)	repeated	tail
(?:(?C1)(a))+	repeated	-
(?:a(?C1)){2}	repeated	-
(?=\d+(?C1))	repeated	-
EOF

# ---- arm 6: refusals --------------------------------------------------------
echo
echo "== [INLINE-C] refusals =="
for f in callouts none; do
    for p in 'a(?Cx)' 'a(?C256)' 'a(?C1x)' 'a(?C!x!)'; do
        out="$("$TIMEOUT_BIN" 60 "$PCREC" --features "$f" -o "$WORK/r.c" --pattern "$p" 2>&1)"
        if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'malformed callout'; then
            ok "$p is refused as malformed with --features $f"
        else
            bad "$p with --features $f: want 'malformed callout', got: $out"
        fi
    done
done
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/r.c" --pattern 'a(?C"__x")' 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -q "contains '__'"; then
    ok "a binding name containing '__' is refused"
else
    bad "a '__' binding name: want a refusal, got: $out"
fi
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-main -o "$WORK/r.c" --pattern 'a(?C1)' 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'cannot define the binding rx_callout_1'; then
    ok "--emit-main refuses a callout pattern"
else
    bad "--emit-main on a callout pattern: want a refusal, got: $out"
fi

echo
echo "callouts: $pass passed, $fail failed, $skip skipped"
[ "$fail" -eq 0 ]
