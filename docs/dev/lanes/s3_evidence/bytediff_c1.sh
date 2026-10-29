#!/usr/bin/env bash
# docs/dev/lanes/s3_evidence/bytediff_c1.sh — the code review r1 C1 build's byte-diff against the
# S3 tip before it. Usage: bytediff_c1.sh PRE_PCREC NEW_PCREC OUTDIR [EXTRA_FLAGS]
# For every row of predicted_c1.tsv (beside this script): compile with both into
# OUTDIR/{pre,new}/<row>/a.{c,h} and print one line per row:
#   <row> <pattern> <flags> predicted=<P> actual=<A> <AGREE|DISAGREE>
# A is read from NEW's own text only (predicted_c1.tsv's header names the classes). EXTRA_FLAGS
# (the OFF arm's kit denies) apply to BOTH sides (the OFF arm is the parent's text on each), and
# then every row is predicted IDENTICAL; bytediff.sh holds that text to main's.
# Exit 0 iff every row agrees.
set -u
export LC_ALL=C
PRE=$1 NEW=$2 OUT=$3 EXTRA=${4:-}
MAN="$(cd "$(dirname "$0")" && pwd)/predicted_c1.tsv"
bad=0 i=0
while IFS=$'\t' read -r pat flags pred why; do
    case "$pat" in '#'*|'') continue ;; esac
    i=$((i + 1))
    fl=(); [ "$flags" = - ] || read -r -a fl <<<"$flags"
    for side in pre new; do
        d="$OUT/$side/$i"; mkdir -p "$d"
        bin=$PRE; ex=()
        [ $side = new ] && bin=$NEW
        [ -n "$EXTRA" ] && ex=("$EXTRA")
        gnutimeout 60 "$bin" -p rx -fcomments --features all "${fl[@]}" "${ex[@]}" -o "$d/a.c" --pattern "$pat" \
            > "$d/err" 2>&1 || echo "COMPILE-FAILED" > "$d/a.c"
    done
    c=$OUT/new/$i/a.c
    if cmp -s <(cat "$OUT/pre/$i/a.c" "$OUT/pre/$i/a.h" 2>/dev/null) \
              <(cat "$c" "$OUT/new/$i/a.h" 2>/dev/null); then
        act=IDENTICAL
    elif grep -q '^#define RX_DFA_SCAN "cover"' "$OUT/pre/$i/a.c" && ! grep -q '^#define RX_DFA_SCAN "cover"' "$c"; then
        act=MOVES-uncover
    elif grep -q '_ofsskip__w32(' "$c" && grep -q '_mf[0-9]*_ofsskip__body(' "$c"; then
        act=MOVES-fn-simd
    elif grep -q '_mf[0-9]*_ofsskip__body(' "$c"; then
        act=MOVES-fn
    elif grep -q '_mf[0-9]*_ha < ' "$c"; then
        act=MOVES-pair
    else
        act=MOVES-other
    fi
    want=$pred; [ -n "$EXTRA" ] && want=IDENTICAL
    v=AGREE; [ "$act" = "$want" ] || { v=DISAGREE; bad=$((bad + 1)); }
    printf '%s\t%s\t%s\tpredicted=%s\tactual=%s\t%s\n' "$i" "$pat" "$flags" "$want" "$act" "$v"
done < "$MAN"
echo "bytediff_c1: $i rows, $bad disagree${EXTRA:+ (both sides: $EXTRA)}"
[ "$bad" -eq 0 ]
