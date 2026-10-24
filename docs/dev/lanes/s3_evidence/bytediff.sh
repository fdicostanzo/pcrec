#!/usr/bin/env bash
# docs/dev/lanes/s3_evidence/bytediff.sh — lane s3's light byte-diff against REF (D172 S3; the
# manager's R4 condition 3). Usage: bytediff.sh REF_PCREC NEW_PCREC OUTDIR [EXTRA_NEW_FLAGS]
# For every row of predicted_movers.tsv (beside this script): compile with both compilers into
# OUTDIR/{ref,new}/<row>/a.{c,h}, mask the abi digits, and print one line per row:
#   <row> <pattern> <flags> predicted=<P> actual=<A> <AGREE|DISAGREE>
# where A is ABI-ONLY (identical once masked) or MOVES-cover[-hors] (new reads RX_DFA_SCAN "cover";
# -hors where it also defines a `_sh[256]` skip table) or MOVES-pair (not cover; new carries as
# many bounded two-stream declarations, `size_t ha = 0, hb = 0, wa = `, as ref carries unbounded
# ones, `size_t ha = 0, hb = 0;`, at least one, and the `#define RX_` stamps are unchanged: the S3
# final review's EMIT-1 look-ahead, the manager's R-d) or MOVES-other. EXTRA_NEW_FLAGS (the OFF
# arm's kit denies) apply to the NEW side only, and then the row's `off` column is its prediction.
# Exit 0 iff every row agrees. Each side is the tool's own output; no kit artifact is read.
set -u
export LC_ALL=C
REF=$1 NEW=$2 OUT=$3 EXTRA=${4:-}
MAN="$(cd "$(dirname "$0")" && pwd)/predicted_movers.tsv"
mask() { sed -E 's/\(abi 8[0-9]\)/(abi NN)/g; s/(PCREC_RX_ABI_H \+ 0\) != )8[0-9]/\1NN/; s/(PCREC_RX_ABI_H )8[0-9]/\1NN/; s/(\.abi = )8[0-9],/\1NN,/' "$1"; }
bad=0 i=0
npair() { grep -cE "size_t ([A-Za-z0-9_]*)ha = 0, \\1hb = 0, \\1wa = " "$1"; }
opair() { grep -cE "size_t ([A-Za-z0-9_]*)ha = 0, \\1hb = 0;" "$1"; }
while IFS=$'\t' read -r pat flags pred off why; do
    case "$pat" in '#'*|'') continue ;; esac
    i=$((i + 1))
    fl=(); [ "$flags" = - ] || read -r -a fl <<<"$flags"
    for side in ref new; do
        d="$OUT/$side/$i"; mkdir -p "$d"
        bin=$REF; ex=()
        if [ $side = new ]; then bin=$NEW; [ -n "$EXTRA" ] && ex=("$EXTRA"); fi
        gnutimeout 60 "$bin" -p rx -fcomments --features all "${fl[@]}" "${ex[@]}" -o "$d/a.c" --pattern "$pat" \
            > "$d/err" 2>&1 || echo "COMPILE-FAILED" > "$d/a.c"
    done
    if cmp -s <(mask "$OUT/ref/$i/a.c"; mask "$OUT/ref/$i/a.h" 2>/dev/null) \
              <(mask "$OUT/new/$i/a.c"; mask "$OUT/new/$i/a.h" 2>/dev/null); then
        act=ABI-ONLY
    elif grep -q '^#define RX_DFA_SCAN "cover"' "$OUT/new/$i/a.c"; then
        act=MOVES-cover
        grep -q '_sh\[256\]' "$OUT/new/$i/a.c" && act=MOVES-cover-hors
    elif n=$(npair "$OUT/new/$i/a.c") && [ "$n" -gt 0 ] && [ "$n" = "$(opair "$OUT/ref/$i/a.c")" ] &&
         cmp -s <(mask "$OUT/ref/$i/a.c" | grep '^#define RX_') <(mask "$OUT/new/$i/a.c" | grep '^#define RX_'); then
        act=MOVES-pair
    else
        act=MOVES-other
    fi
    want=$pred; [ -n "$EXTRA" ] && want=$off
    v=AGREE; [ "$act" = "$want" ] || { v=DISAGREE; bad=$((bad + 1)); }
    printf '%s\t%s\t%s\tpredicted=%s\tactual=%s\t%s\n' "$i" "$pat" "$flags" "$want" "$act" "$v"
done < "$MAN"
echo "bytediff: $i rows, $bad disagree${EXTRA:+ (new side: $EXTRA)}"
[ "$bad" -eq 0 ]
