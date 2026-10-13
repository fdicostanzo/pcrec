#!/usr/bin/env bash
# tests/compound/run_shell_checks.sh -- [COMPOUND] B4: the shell's structural
# facts no answer check can see (docs/design/compound.md §A.5, §A.8, §A.14;
# sabotage rows CMP-7, CMP-16, CMP-18).
#
#   (1) THE CALL-SITE TABLE EMITS ONLY WHAT THE CALLEE CAN RETURN (§A.14,
#       CMP-18): a split compound's parts are DFA, guards-off, check-clear, so
#       every part call is handled by rows 1, 2 and 8 alone -- one `r > 0`
#       line and one dead trap per call, no give-up, internal, utf, startpos
#       or unset-variable line. Counted against the number of part calls in
#       the controller text, so a row that stopped being emitted fails too.
#   (2) THE NAMESPACE RESERVATION TABLE (§A.5, cli.md §1.6¶2, CMP-16): a `-p`
#       containing `__` is refused (row `parts`), a `-p` beginning with the
#       lever's reserved prefix is refused (row `harness-lever`), and the
#       control `a_f` compiles.
#   (3) `drop-compound` (§A.8, limits.md §8.4¶1a, CMP-7): under a cap between
#       the witness's plain and compound sizes (the midpoint of the two sizes
#       the compiler itself MEASURES, so the witness keeps bracketing the cap
#       as either moves) the plain artifact ships, stamping `"none"`,
#       identical to the lever's output past that stamp, with the note naming
#       the drop; under `--size-cap=refuse` (the rung is degrading) the same
#       compile is refused.
# Env: PCREC, PCREC_HARNESS, CC, KEEP=1.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
HARNESS="${PCREC_HARNESS:-$ROOT_DIR/build/pcrec-harness}"
CC="${CC:-gcc}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run
. "$ROOT_DIR/tests/lib/lib_srcs.sh"
W="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-shell.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$W"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
WIT='^\s+|\s+$'
stamp() { sed -n "s/^#define RX_$1 \"\(.*\)\"\$/\1/p" "$2" | head -1; }

# ---- (1) the call-site rows ---------------------------------------------------
pcrec_run "$PCREC" --features all -p rx -o "$W/c.c" --pattern "$WIT" 2>"$W/c.err" \
    || bad "(1) the witness '$WIT' did not compile: $(head -1 "$W/c.err")"
if [ -s "$W/c.c" ]; then
    [ "$(stamp COMPOUND "$W/c.c")" = split ] \
        || bad "(1) the witness '$WIT' stamps '$(stamp COMPOUND "$W/c.c")', not \"split\": the check measures nothing"
    # the controller: everything after the last part's text, i.e. after the
    # last `rx__q_` DEFINITION; a part call is a line calling rx__<role>_search.
    ncall=$(grep -cE '^ *(int r = |int r = )rx__[a-z0-9]+_search\(' "$W/c.c")
    nsucc=$(grep -cE '^ *if \(r > 0\)' "$W/c.c")
    ntrap=$(grep -cE '^ *if \(r < 0\) __builtin_trap\(\);$' "$W/c.c")
    nover=$(grep -cE '^ *if \(r (>= PCREC_ERR_FLOOR|== PCREC_ERR_(INTERNAL|UTF|STARTPOS|UNSET_VAR))' "$W/c.c")
    if [ "$ncall" -ge 4 ] && [ "$nsucc" -eq "$ncall" ] && [ "$ntrap" -eq "$ncall" ] && [ "$nover" -eq 0 ]; then
        ok "(1) $ncall part calls, each handled by rows 1, 2 and 8 alone ($nsucc success lines, $ntrap dead traps, 0 rows the DFA callee cannot return)"
    else
        bad "(1) $ncall part calls (floor 4: F and Q in _search, F in _match and _match_caps): $nsucc success lines, $ntrap traps, $nover rows a DFA guards-off callee cannot return"
    fi
fi

# ---- (2) the namespace table ----------------------------------------------------
for row in "a__f|parts|__" "pcrec_harness_x|harness-lever|reserved"; do
    pfx="${row%%|*}"; rest="${row#*|}"; name="${rest%%|*}"; word="${rest#*|}"
    if pcrec_run "$PCREC" --features all -p "$pfx" -o "$W/n.c" --pattern "$WIT" 2>"$W/n.err"; then
        bad "(2) -p $pfx compiled: the namespace row '$name' does not refuse it"
    elif grep -q "$word" "$W/n.err"; then
        ok "(2) -p $pfx refused by row '$name': $(head -1 "$W/n.err")"
    else
        bad "(2) -p $pfx refused, but not by row '$name': $(head -1 "$W/n.err")"
    fi
done
pcrec_run "$PCREC" --features all -p a_f -o "$W/n.c" --pattern "$WIT" 2>"$W/n.err" \
    && ok "(2) control: -p a_f compiles" \
    || bad "(2) control: -p a_f refused: $(head -1 "$W/n.err")"

# ---- (3) drop-compound ------------------------------------------------------------
# One reference compiler with a built-in cap far below the witness; the cap is
# then RAISED per compile (--max-emit-bytes is raise-only), so every cap below
# is read off the compiler's own measure: N_p, the plain artifact's size (the
# figure a degrade compile at the floor refuses with, the compound having been
# dropped first), N_c, the compound's (what --size-cap=refuse quotes at N_p+1).
lsrcs=$(pcrec_lib_srcs "$ROOT_DIR" | tr '\n' ' ')
size_of() { sed -n 's/^pcrec: pattern too large: \([0-9]*\) bytes.*/\1/p' "$1" | head -1; }
# shellcheck disable=SC2086
if "$CC" -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" -DPCREC_MAX_EMIT_BYTES=1000 \
        -o "$W/pcrec_low" "$ROOT_DIR/cli/main.c" $lsrcs 2>"$W/low.err"; then
    low() { pcrec_run "$W/pcrec_low" --features all -p rx "$@" --pattern "$WIT"; }
    low -o "$W/x.c" 2>"$W/np.err"; np=$(size_of "$W/np.err")
    low --size-cap=refuse --max-emit-bytes=$(( ${np:-0} + 1 )) -o "$W/x.c" 2>"$W/nc.err"
    nc=$(size_of "$W/nc.err")
    if [ -n "$np" ] && [ -n "$nc" ] && [ "$nc" -gt "$np" ]; then
        cap=$(( (np + nc) / 2 ))
        # the lever's plain artifact (the default build's: a cap is raise-only,
        # so it differs from the low build's only in RX_MAX_EMIT_BYTES)
        mkdir -p "$W/p" "$W/d"     # one basename: the .c includes its .h by name
        pcrec_run "$HARNESS" --harness=no-compound --features all -p rx \
            -o "$W/p/rx.c" --pattern "$WIT" 2>/dev/null
        if low --max-emit-bytes=$cap -o "$W/d/rx.c" 2>"$W/d.err"; then
            norm() { sed -e 's/^#define RX_COMPOUND ".*"$/#define RX_COMPOUND/' \
                         -e 's/^#define RX_MAX_EMIT_BYTES [0-9]*$/#define RX_MAX_EMIT_BYTES/' "$1"; }
            if [ "$(stamp COMPOUND "$W/d/rx.c")" = none ] && cmp -s <(norm "$W/d/rx.c") <(norm "$W/p/rx.c") \
                    && grep -q 'dropped the compound' "$W/d.err"; then
                ok "(3) under a cap of $cap (plain $np, compound $nc, the compiler's measure) the plain artifact ships: \"none\", the lever's text past the two cap-dependent stamps, the note names the drop"
            else
                bad "(3) under a cap of $cap the compile shipped '$(stamp COMPOUND "$W/d/rx.c")', not the plain artifact, or no note named the drop"
            fi
        else
            bad "(3) under a cap of $cap (plain $np, compound $nc) the compile was REFUSED: drop-compound did not fire: $(head -1 "$W/d.err")"
        fi
        if low --size-cap=refuse --max-emit-bytes=$cap -o "$W/r.c" 2>/dev/null; then
            bad "(3) --size-cap=refuse shipped an over-cap compound's plain artifact: drop-compound is degrading and the switch denies it"
        else
            ok "(3) --size-cap=refuse refuses the over-cap compound at $cap (the rung is degrading)"
        fi
        low --max-emit-bytes=$(( nc + 1 )) -o "$W/u.c" 2>/dev/null
        [ "$(stamp COMPOUND "$W/u.c")" = split ] \
            && ok "(3) control: under a cap above $nc the compound ships" \
            || bad "(3) control: under a cap above $nc the compound did not ship"
    else
        bad "(3) the compiler's own sizes do not bracket a cap: plain '${np:-?}', compound '${nc:-?}' (np.err: $(head -1 "$W/np.err"))"
    fi
else
    bad "(3) the low-cap reference compiler failed to build: $(head -1 "$W/low.err")"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
