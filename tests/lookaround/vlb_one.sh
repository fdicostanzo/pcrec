#!/usr/bin/env bash
# tests/lookaround/vlb_one.sh — ONE cell pattern of run_lookaround_diff.sh §5
# ([VLOOKBEHIND] gate 1): build the artifact under the mode's encoding, sweep
# its mode's subjects at every startpos the oracle sweeps, compare against
# libpcre2 (tests/backrefs/bref_oracle.py) cell for cell, match span AND
# every group span. Run by xargs, one argument: `<mode>\t<pattern>`.
#
# Prints ONE line: `PASS<TAB>mode<TAB>cells<TAB>divergent` or
# `FAIL<TAB>mode<TAB>pattern<TAB>why`. `divergent` counts, for a utf8-clip
# cell, the answers where libpcre2 under PCRE2_UTF differs from its byte
# answer: D142 item 3's expected-divergent subset (0 for the other modes).
#
# Env (exported by the caller): PCREC CC GENCFLAGS TIMEOUT_BIN ORACLE BATCH
# FEATS VLB_SUBJ (the subjects root, one directory per mode) VLB_WORK.
set -u
line="$1"
mode="${line%%$'\t'*}"; pat="${line#*$'\t'}"
d="$(mktemp -d -p "$VLB_WORK")"
trap 'rm -rf "$d"' EXIT
enc=byte; [ "$mode" = byte ] || enc=utf8
fail() { printf 'FAIL\t%s\t%s\t%s\n' "$mode" "$pat" "$1"; exit 0; }

"$TIMEOUT_BIN" 20 "$PCREC" --features "$FEATS" -e "$enc" -p rx -o "$d/gen.c" \
    --pattern "$pat" 2>"$d/err" || fail "pcrec refused: $(head -1 "$d/err")"
ncaps="$(grep -m1 '^#define RX_NCAPS' "$d/gen.h" | awk '{print $3}')"
# shellcheck disable=SC2086
$CC $GENCFLAGS -I"$d" -o "$d/t" "$BATCH" "$d/gen.c" 2>"$d/cerr" \
    || fail "cc: $(head -2 "$d/cerr" | tr '\n' ' ')"
printf 'k\t%d\t%s\t%s\n' "$((ncaps - 1))" "$mode" "$pat" > "$d/pl"
python3 "$ORACLE" "$d/pl" "$VLB_SUBJ/$mode" "$d/o" 2>"$d/oerr" \
    || fail "oracle: $(tail -1 "$d/oerr")"
# The pcrec side sweeps exactly the (subject, startpos) cells the oracle did.
awk -F'\t' -v dir="$VLB_SUBJ/$mode" '{ printf "%s/%s\t%s\n", dir, $2, $3 }' \
    "$d/o" > "$d/cells"
"$TIMEOUT_BIN" 20 "$d/t" < "$d/cells" > "$d/mine" 2>&1 || fail "the artifact did not finish"
cut -f4 "$d/o" > "$d/theirs"
n=$(wc -l < "$d/theirs")
[ "$(wc -l < "$d/mine")" -eq "$n" ] || fail "answer counts differ"
ndiff=$(paste "$d/mine" "$d/theirs" | awk -F'\t' '$1 != $2' | wc -l)
[ "$ndiff" -eq 0 ] || fail "$ndiff of $n cells differ, first: $(paste "$d/cells" "$d/mine" "$d/theirs" | awk -F'\t' '$3 != $4' | head -1 | tr '\t' ' ')"
div=0
if [ "$mode" = utf8-clip ]; then
    printf 'k\t%d\tutf8\t%s\n' "$((ncaps - 1))" "$pat" > "$d/pu"
    python3 "$ORACLE" "$d/pu" "$VLB_SUBJ/$mode" "$d/ou" 2>"$d/oerr" \
        || fail "oracle (utf8 side of the clip count): $(tail -1 "$d/oerr")"
    div=$(cut -f4 "$d/ou" | paste - "$d/theirs" | awk -F'\t' '$1 != $2' | wc -l)
fi
printf 'PASS\t%s\t%d\t%d\n' "$mode" "$n" "$div"
