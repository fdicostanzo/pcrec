#!/usr/bin/env bash
# tests/callouts/run_callouts_tests.sh — module `callouts` ([INLINE-C] stage
# 1b; docs/spec/match_api.md §11): `make test-callouts`.
#
# SEVEN ARMS:
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
#       binding name, a binding symbol the shared ABI block already declares
#       (read off an emitted artifact, not off pcrec's own list), empty and
#       malformed attribute lists and declarations (escaped echoes),
#       `--emit-main`, and `--callout` with `--count-groups`/`--emit-facts`;
#   (7) the `once` advice: advice_check.py, every refusal's verdict on its
#       fix (does not change / loses a match / may change) against
#       libpcre2's answers, the printed witness included.
# Arms 2, 3 and 7 SKIP LOUDLY when libpcre2 is absent (PC-3's shape).
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
            # The trap is `__builtin_trap()`: SIGILL (132) on x86, SIGTRAP
            # (133) on arm64. Any other signal, SIGSEGV's 139 above all, is
            # a crash, not the trap.
            if [ "$rc" -eq 132 ] || [ "$rc" -eq 133 ]; then
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
        # The refusal names its cause: the construct and its offset.
        if [ $rc -ne 0 ] && printf '%s' "$out" | grep -q 'is marked once but can fire again' &&
           printf '%s' "$out" | grep -qE '(quantifier|alternation|subroutine call)( at offset [0-9]+)?'; then
            ok "once refused on $once, naming the cause"
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
(?*a+)(?C1)a+c	repeated	-
(?=a+)(?C1)b	once-per-start	-
(?(DEFINE)(?<d>a|b))x(?C1)	once-per-match	tail
(?:a|b){0}x(?C1)	once-per-match	tail
EOF

# Every `once` refusal keeps three things: the construct, its offset, the fix
# ([INLINE-C] 1b guide; match_api.md §11.8¶3). One row per culprit kind, and
# the listing's `note` is the same text. pattern TAB construct ERE TAB fix ERE
while IFS=$'\t' read -r pat what fix; do
    [ -z "$pat" ] && continue
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/once.c" --pattern "$pat" 2>&1)"
    rc=$?
    if [ $rc -ne 0 ] && printf '%s' "$out" | grep -qE "$what at offset [0-9]+" &&
       printf '%s' "$out" | grep -qF "$fix"; then
        ok "once refusal on $pat names its construct, offset and fix"
    else
        bad "once refusal on $pat: want '$what at offset N' and '$fix', got exit $rc: $out"
    fi
    note="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-ir --pattern "${pat/,once/}" 2>&1 |
            awk -F'\t' '/^#section/{s=($0=="#section callouts")} s && !/^#/{print $7; exit}')"
    if printf '%s' "$out" | grep -qF "$note" && [ -n "$note" ]; then
        ok "the listing's note for ${pat/,once/} is the refusal's reason"
    else
        bad "the listing's note '$note' is not inside the refusal '$out'"
    fi
done <<'EOF'
a+(?C"x,once")c	the quantifier	possessive
a+?(?C"x,once")c	the lazy quantifier	drop `once`
(?:a|b)(?C"x,once")c	the alternation	(?>...)
(a)(?1)(?C"x,once")c	the subroutine call	(?>...)
(?*a+)(?C"x,once")a+c	the non-atomic lookaround at offset 0 keeps the quantifier	use (?=...) or wrap it: (?>(?*...))
(?*(?*a+))(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the quantifier	wrap it: (?>(?*...))
(?*a|b)(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the alternation	wrap it: (?>(?*...))
(?<*a|b)(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the alternation	use (?<=...) or wrap it: (?>(?<*...))
(?*(?:a|b))(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the alternation	use (?=...) or wrap it
(?*[ab]|c)(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the alternation	wrap it: (?>(?*...))
(?*(?*a|b))(?C"x,once")c	the non-atomic lookaround at offset 0 keeps the alternation	wrap it: (?>(?*...))
EOF
# The fixes the refusals name are accepted.
for p in '(?>(?*a+))(?C"x,once")a+c' '(?=a+)(?C"x,once")a+c' 'a++(?C"x,once")c' '(?>a|b)(?C"x,once")c' '(?>(?*a|b))(?C"x,once")c' '(?=a|b)(?C"x,once")c' '(?*[ab])(?C"x,once")c'; do
    if "$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/once.c" --pattern "$p" >/dev/null 2>&1; then
        ok "the named fix is accepted: $p"
    else
        bad "the named fix is refused: $p"
    fi
done

# ---- arm 6: refusals --------------------------------------------------------
echo
echo "== [INLINE-C] refusals =="
for f in callouts none; do
    for p in 'a(?Cx)' 'a(?C256)' 'a(?C1x)' 'a(?C!x!)' 'a(?C'; do
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
# A BINDING SYMBOL THE SHARED ABI BLOCK ALREADY DECLARES. The names are read
# off an emitted artifact (every `rx_callout_*` identifier it spells that is
# not this pattern's own binding), so a name the block gains later is
# covered without editing pcrec's list or this one.
if "$TIMEOUT_BIN" 60 "$PCREC" --features all -p rx -o "$WORK/abi.c" --pattern 'a(?C7)'; then
    nabi=0
    for sym in $(grep -ohE '\brx_callout_[A-Za-z0-9_]+' "$WORK/abi.c" "$WORK/abi.h" | LC_ALL=C sort -u); do
        [ "$sym" = rx_callout_7 ] && continue
        nabi=$((nabi + 1))
        p="a(?C\"${sym#rx_callout_}\")"
        out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/r.c" --pattern "$p" 2>&1)"
        if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'already declares'; then
            ok "$p is refused: $sym is the shared ABI block's own name"
        else
            bad "$p: $sym is declared by the artifact's shared block, want a refusal, got: $out"
        fi
    done
    if [ "$nabi" -lt 1 ]; then
        bad "no fixed rx_callout_* name found in an emitted artifact: the ABI-name check read nothing"
    fi
else
    bad "the ABI-name probe artifact did not compile"
fi
# Attribute lists: an empty item, and an escaped echo of an unknown one.
for p in 'a(?C"x,")' 'a(?C"x,,once")'; do
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/r.c" --pattern "$p" 2>&1)"
    if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'empty callout attribute'; then
        ok "$p: an empty attribute is refused"
    else
        bad "$p: want 'empty callout attribute', got: $out"
    fi
done
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/r.c" --pattern "$(printf 'a(?C"x,o\033")')" 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -qF 'o\x1b' && ! printf '%s' "$out" | grep -q $'\033'; then
    ok "an unknown attribute's echo escapes its control byte"
else
    bad "an unknown attribute with ESC: want an escaped echo, got: $(printf '%s' "$out" | od -c | head -3)"
fi
# --callout's value shape: the one shape reader, an escaped echo.
for v in '1:' '13once' '1:Once' '1:once,' "$(printf '1:\033')"; do
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all -o "$WORK/r.c" --callout "$v" --pattern 'a(?C1)' 2>&1)"
    if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'a callout declaration is N:ATTRS' &&
       ! printf '%s' "$out" | grep -q $'\033'; then
        ok "--callout '$(printf '%q' "$v")' is refused by its shape"
    else
        bad "--callout '$(printf '%q' "$v")': want a shape refusal, got: $out"
    fi
done
# The `.rxt` `callout` line: the same shape reader, its own [value-shape]
# diagnostic, an escaped echo; and the one well-formed line compiles.
for v in '13once' '13 consume once' '13' "$(printf '13 o\033')" '13 consume'; do
    printf 'pattern a(?C13)b\nfeatures all\ncallout %s\nm "ab" 0 2\n' "$v" > "$WORK/co.rxt"
    out="$("$TIMEOUT_BIN" 60 "$PCREC" -o "$WORK/co.c" "$WORK/co.rxt" 2>&1)"
    rc=$?
    if [ "$v" = '13 consume' ]; then
        if [ $rc -eq 0 ]; then ok "the .rxt line 'callout 13 consume' compiles"
        else bad "the .rxt line 'callout 13 consume': want a compile, got: $out"; fi
    elif [ $rc -ne 0 ] && printf '%s' "$out" | grep -q '\[value-shape\]' &&
         ! printf '%s' "$out" | grep -q $'\033'; then
        ok "the .rxt line 'callout $(printf '%q' "$v")' is refused by its shape"
    else
        bad "the .rxt line 'callout $(printf '%q' "$v")': want [value-shape], got: $out"
    fi
done
# --count-groups reads no attribute and refuses --callout; --emit-facts
# applies it, so a declaration naming no site is refused there too.
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --count-groups --callout 1:once --pattern 'a(?C1)' 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'count-groups reads no callout attribute'; then
    ok "--count-groups refuses --callout"
else
    bad "--count-groups with --callout: want a refusal, got: $out"
fi
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-facts --callout 2:once --pattern 'a(?C1)' 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'does not use'; then
    ok "--emit-facts applies --callout (a declaration naming no site is refused)"
else
    bad "--emit-facts with an unused --callout: want a refusal, got: $out"
fi
# ...and the listing describes the declared site: a `consume` site is not
# zero-width, so `b`'s furthest offset is unbounded (review r2 CON-8).
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-facts --callout 1:consume --pattern 'a(?C1)b' 2>&1)"
if printf '%s\n' "$out" | grep -qP '\treq_set_maxoff\t.*\t97:0,98:unbounded\t'; then
    ok "--emit-facts reads a declared consume site's width"
else
    bad "--emit-facts --callout 1:consume: want req_set_maxoff 97:0,98:unbounded, got: $(printf '%s\n' "$out" | grep req_set_maxoff)"
fi
# harness.manifest (rxt_format.md §6¶3-4): a bad line FAILS the file's
# cases even when no driver needs the link; a good one runs them.
mkdir -p "$WORK/mf"
printf 'pattern ab\nm "ab" 0 2\n' > "$WORK/mf/t.rxt"
printf 'int mf_x;\n' > "$WORK/mf/x.c"
for m in 'link ../x.c' 'link x.c extra' 'link' 'bogus x.c' 'link x.c'; do
    printf '%s\n' "$m" > "$WORK/mf/harness.manifest"
    out="$(PCREC="$PCREC" "$TIMEOUT_BIN" 300 bash "$ROOT_DIR/tests/harness/run.sh" "$WORK/mf/" 2>&1)"
    rc=$?
    if [ "$m" = 'link x.c' ]; then
        if [ $rc -eq 0 ]; then ok "harness.manifest 'link x.c' links and the file passes"
        else bad "harness.manifest 'link x.c': want a pass, got exit $rc"; fi
    elif [ $rc -ne 0 ] && printf '%s' "$out" | grep -q 'HARNESS FAILURE: harness.manifest'; then
        ok "harness.manifest '$m' fails the file's cases"
    else
        bad "harness.manifest '$m': want a harness failure, got exit $rc"
    fi
done
out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --emit-main -o "$WORK/r.c" --pattern 'a(?C1)' 2>&1)"
if [ $? -ne 0 ] && printf '%s' "$out" | grep -q 'cannot define the binding rx_callout_1'; then
    ok "--emit-main refuses a callout pattern"
else
    bad "--emit-main on a callout pattern: want a refusal, got: $out"
fi

# ---- arm 7: the `once` advice ----------------------------------------------
echo
echo "== [INLINE-C] the once advice against libpcre2 (match_api.md §11.8¶3) =="
"$TIMEOUT_BIN" 900 python3 "$SCRIPT_DIR/advice_check.py" --pcrec "$PCREC" \
    --work "$WORK/advice" --cc "$CC"
case $? in
    0) ok "every once refusal's verdict on its fix agrees with libpcre2's answers" ;;
    3) note "libpcre2 is unavailable: the once advice was not checked against matches" ;;
    *) bad "a once refusal's verdict disagrees with what its fix matches, or the advice rows missed their reach" ;;
esac

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks skipped: $skip"
[ "$fail" -eq 0 ]
