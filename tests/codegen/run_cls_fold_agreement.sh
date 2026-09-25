#!/usr/bin/env bash
# tests/codegen/run_cls_fold_agreement.sh — THE VM CLASS-FOLD SHAPE, TIED TO
# src/core/fold.c's TABLE (docs/design/compare_stack.md §duplications).
#
# WHAT IS MISSING TODAY, AND WHY IT IS A GAP. `vm_cls_shape`'s FOLD arm
# (src/gen/emit_vm.c ~1633) decides whether a two-member class takes the
# `(byte | 0x20) == lower` compare (~1655) with its OWN recognizer —
# `count == 2 && (lo ^ hi) == 0x20 && lo >= 'A' && lo <= 'Z'` — spelled with
# no reference at all to `pcrec_ascii_fold` (src/core/fold.c), the ONE table
# this project otherwise treats as the ground truth for which bytes fold
# (tests/backrefs/fold_agreement_check.c's own charter: "the table IS the
# parse-time fold by construction"). Sabotage S228 already proves the
# recognizer's OWN conjuncts matter (tests/base/cls_fold.rxt catches a
# WIDENED recognizer), but nothing anywhere compiles the emitted shape
# against fold.c's real population, and nothing at all exercises the
# EMISSION LINE itself (~1655) rather than the recognizer that selects it —
# a sabotage that shifts the compare's own constant (swap `hi` for `lo`, or
# the mask `0x20` for something else) has no detector.
#
# THE TWO INDEPENDENT SOURCES, `fold_agreement_check.c`'s shape one
# mechanism over:
#
#   SOURCE A — `tests/codegen/fold_pairs_dump.c`, linked against
#     libpcrec.a, reading `pcrec_ascii_fold` DIRECTLY: the real 26 letter
#     fold pairs (F lines) and the 6 near-miss punctuation pairs that share
#     the fold pattern's own bit relationship but do not fold (N lines) —
#     see that file's own header for why 0x40..0x5f is the whole candidate
#     range and not a shrinking of it.
#   SOURCE B — a REAL COMPILED, LINKED, RUN artifact per pair: this script
#     reads neither `vm_cls_shape` nor `vm_cls_test`'s source text. It
#     compiles `([\x<lo>\x<hi>])x` with `--emit-main`, reads the emitted
#     C for the shape's OWN structural signature, and then RUNS the
#     resulting binary against probe subjects, reading its EXIT CODE
#     (0 = match, 1 = no-match, docs/spec/cli.md's `--emit-main` vocabulary)
#     — never a value pcrec's own predicate computed.
#
# THE POPULATION FLOORS ARE HALF THE MEASURED COUNT (D110's convention):
# 13 fold pairs (measured 26) and 3 near-miss pairs (measured 6) — a K35
# guard against a future fold.c change silently emptying either bucket
# rather than moving it, which is exactly what this check would otherwise
# be unable to see.
#
# Usage: bash tests/codegen/run_cls_fold_agreement.sh
# Env: PCREC (default build/pcrec), CC, KEEP=1 to keep the temp dir.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # pcrec_run, gen_cc, gen_run
. "$ROOT_DIR/tests/lib/cc_resolve.sh"    # [MACPORT] resolves a real GNU gcc into CC
export WATCHDOG_SECTION="codegen"

LIBA="$ROOT_DIR/build/libpcrec.a"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Wno-unused-parameter}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "clsfold: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: clsfold: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }
[ -f "$LIBA" ] || { echo "FAIL: clsfold: no $LIBA — run \`make\` first" >&2; exit 1; }

# emit <outfile> <pattern> [extra args...]
emit() {
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --emit-main "$@" -o "$out" --pattern "$pat" >/dev/null 2>&1
}

# ===========================================================================
# SOURCE A — derive the population from fold.c, never from a hand-typed list
# ===========================================================================
if ! gen_cc "fold_pairs_dump build" "$CC" $GENCFLAGS -I"$ROOT_DIR/src" -I"$ROOT_DIR/lib" \
        -o "$WORKDIR/dump" "$SCRIPT_DIR/fold_pairs_dump.c" "$LIBA"; then
    echo "$GEN_CC_LOG" >&2
    echo "FAIL: clsfold: fold_pairs_dump.c did not compile" >&2
    exit 1
fi
DUMP_OUT="$WORKDIR/dump.tsv"
"$WORKDIR/dump" > "$DUMP_OUT" 2>"$WORKDIR/dump.err"
cat "$WORKDIR/dump.err" >&2

n_fold=$(grep -c '^F ' "$DUMP_OUT")
n_near=$(grep -c '^N ' "$DUMP_OUT")
n_other=$(grep -c '^X ' "$DUMP_OUT")
FOLD_FLOOR=13   # D110: half the measured 26
NEAR_FLOOR=3    # D110: half the measured 6

[ "$n_other" -eq 0 ] \
    && ok "SOURCE A: every 0x40-0x5f candidate classifies cleanly as fold or non-fold (0 unclassifiable)" \
    || bad "SOURCE A: $n_other candidate pair(s) neither a clean fold pair nor a clean non-fold pair per pcrec_ascii_fold — the relation itself moved"
[ "$n_fold" -ge "$FOLD_FLOOR" ] \
    && ok "SOURCE A: $n_fold real ASCII fold pairs read from pcrec_ascii_fold (floor $FOLD_FLOOR)" \
    || bad "SOURCE A: only $n_fold fold pairs read from pcrec_ascii_fold, floor is $FOLD_FLOOR — the population this check drives has shrunk"
[ "$n_near" -ge "$NEAR_FLOOR" ] \
    && ok "SOURCE A: $n_near near-miss (0x20-shaped, non-folding) pairs read from pcrec_ascii_fold (floor $NEAR_FLOOR)" \
    || bad "SOURCE A: only $n_near near-miss pairs read from pcrec_ascii_fold, floor is $NEAR_FLOOR"

# ===========================================================================
# SOURCE B — one real artifact per pair, read by its emitted text AND by
# actually running it. Two fixed negative-control bytes ('0'=0x30, '9'=0x39)
# sit outside BOTH the fold and the near-miss ranges (0x40-0x7f) on every row.
# ===========================================================================
NEG1=48   # '0'
NEG2=57   # '9'

check_pair() {
    # check_pair <kind: F|N> <lo> <hi>
    local kind="$1" lo="$2" hi="$3"
    local hexlo hexhi pat a
    hexlo=$(printf '%02x' "$lo")
    hexhi=$(printf '%02x' "$hi")
    pat="([\\x${hexlo}\\x${hexhi}])x"
    a="$WORKDIR/p_${kind}_${lo}_${hi}.c"
    if ! emit "$a" "$pat"; then
        bad "[$kind $lo/$hi] $pat: pcrec refused it"
        return
    fi

    local has_fold has_bitmap
    has_fold=0
    grep -qE "\\| 0x20\\) == ${hi}\\b" "$a" && has_fold=1
    has_bitmap=0
    grep -q '_class_bitmap' "$a" && has_bitmap=1

    if [ "$kind" = "F" ]; then
        if [ "$has_fold" -eq 1 ] && [ "$has_bitmap" -eq 0 ]; then
            ok "[F $lo/$hi] emitted text takes the FOLD shape, no bitmap: (byte | 0x20) == $hi"
        else
            bad "[F $lo/$hi] expected the FOLD shape (fold=$has_fold bitmap=$has_bitmap) for a genuine fold.c partner pair"
        fi
    else
        if [ "$has_fold" -eq 0 ] && [ "$has_bitmap" -eq 1 ]; then
            ok "[N $lo/$hi] emitted text stays on the BITMAP, no fold compare — fold.c says this pair does not fold"
        else
            bad "[N $lo/$hi] expected the BITMAP shape (fold=$has_fold bitmap=$has_bitmap) for a pair fold.c says is NOT a partner pair"
        fi
    fi

    # gcc-compile the --emit-main artifact and RUN it: SOURCE B's behavioural
    # half. Every probe byte is fed as argv[1] = "<byte>x"; the class is
    # ALWAYS the first character, and pcrec's own --emit-main main() reads
    # argv[1] as the whole subject.
    local bin="$WORKDIR/bin_${kind}_${lo}_${hi}"
    if ! gen_cc "[$kind $lo/$hi] emit-main link" "$CC" $GENCFLAGS -o "$bin" "$a"; then
        bad "[$kind $lo/$hi] the --emit-main artifact did not compile: $(printf '%s' "$GEN_CC_LOG" | tail -3 | tr '\n' ' ')"
        return
    fi

    local byte want subj rc
    for byte in "$lo" "$hi" "$NEG1" "$NEG2"; do
        subj="$(printf "\\$(printf '%03o' "$byte")x")"
        if [ "$byte" = "$lo" ] || [ "$byte" = "$hi" ]; then want=0; else want=1; fi
        gen_run "clsfold-$kind-$lo-$hi-$byte" "$bin" "$subj" >/dev/null 2>"$WORKDIR/run.err"
        rc=$?
        if [ "$rc" = "$want" ]; then
            ok "[$kind $lo/$hi] byte $byte -> exit $rc (expected $want)"
        else
            bad "[$kind $lo/$hi] byte $byte -> exit $rc, expected $want ($(cat "$WORKDIR/run.err" | tr '\n' ' '))"
        fi
    done
}

while IFS=' ' read -r kind lo hi; do
    case "$kind" in
        F|N) check_pair "$kind" "$lo" "$hi" ;;
    esac
done < "$DUMP_OUT"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
