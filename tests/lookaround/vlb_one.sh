#!/usr/bin/env bash
# tests/lookaround/vlb_one.sh — ONE cell pattern of run_lookaround_diff.sh §5
# ([VLOOKBEHIND] gate 1): build the artifact under the mode's encoding, sweep
# its mode's subjects at every startpos the oracle sweeps, compare against
# libpcre2 (tests/backrefs/bref_oracle.py) cell for cell, match span AND
# every group span. Run by xargs, one argument: `<mode>\t<pattern>`.
#
# Prints ONE line: `PASS<TAB>mode<TAB>cells<TAB>divergent<TAB>u25` or
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
# U25 (docs/dev/upstream_issues.md): libpcre2 10.46's INTERPRETER lets a
# variable-length lookbehind step back across an invalid-UTF unit to the
# subject start, contrary to pcre2unicode's barrier promise (MATCH_INVALID_UTF);
# pcrec honours the promise, and so does the Ubuntu-patched 10.46. The oracle
# is therefore tolerated, on exactly these cells, for a group-1 START that lies
# EARLIER than pcrec's with the match span and every other group unchanged:
# pattern `(?<*(.{1,3}))b`, mode utf8-invalid, pcrec's answer pinned below.
# The vanilla group-1 START may also be an UNDERFLOWED offset (CI run
# 42393813165: 18446744073709551614 = -2 as an unsigned 64-bit value, the
# backwards scan stepping before the subject start, same mechanism); a
# 20-digit start counts as "earlier" (bash's -lt cannot compare it).
u25=0
if [ "$mode" = utf8-invalid ] && [ "$pat" = '(?<*(.{1,3}))b' ] && [ "$ndiff" -ne 0 ]; then
    # <subject hex> <startpos> <pcrec's answer> (the promise-honouring one)
    u25cells=$'ff6162 0 match 2 3 1 2\nff6162 1 match 2 3 1 2\nff6162 2 match 2 3 1 2\na9c3a962 1 match 3 4 1 3\na9c3a962 3 match 3 4 1 3'
    paste "$d/cells" "$d/mine" "$d/theirs" > "$d/trio"
    : > "$d/mine2"
    while IFS=$'\t' read -r sub sp mi th; do
        hex="$(od -An -tx1 -v "$sub" | tr -d ' \n')"
        if [ "$mi" != "$th" ] && printf '%s\n' "$u25cells" | grep -qxF "$hex $sp $mi"; then
            # `match S E g1S g1E`: same span and group-1 end, group-1 START earlier
            read -r -a mi_a <<< "$mi"; read -r -a th_a <<< "$th"
            if [ "${#mi_a[@]}" -eq 5 ] && [ "${#th_a[@]}" -eq 5 ] \
               && [ "${mi_a[1]}" = "${th_a[1]}" ] && [ "${mi_a[2]}" = "${th_a[2]}" ] \
               && [ "${mi_a[4]}" = "${th_a[4]}" ] \
               && { [[ "${th_a[3]}" =~ ^[0-9]{20}$ ]] || [ "${th_a[3]}" -lt "${mi_a[3]}" ]; }; then
                u25=$((u25 + 1)); th="$mi"
            fi
        fi
        printf '%s\t%s\n' "$mi" "$th" >> "$d/mine2"
    done < "$d/trio"
    ndiff=$(awk -F'\t' '$1 != $2' "$d/mine2" | wc -l)
fi
[ "$ndiff" -eq 0 ] || fail "$ndiff of $n cells differ, first: $(paste "$d/cells" "$d/mine" "$d/theirs" | awk -F'\t' '$3 != $4' | head -1 | tr '\t' ' ')"
div=0
if [ "$mode" = utf8-clip ]; then
    printf 'k\t%d\tutf8\t%s\n' "$((ncaps - 1))" "$pat" > "$d/pu"
    python3 "$ORACLE" "$d/pu" "$VLB_SUBJ/$mode" "$d/ou" 2>"$d/oerr" \
        || fail "oracle (utf8 side of the clip count): $(tail -1 "$d/oerr")"
    div=$(cut -f4 "$d/ou" | paste - "$d/theirs" | awk -F'\t' '$1 != $2' | wc -l)
fi
printf 'PASS\t%s\t%d\t%d\t%d\n' "$mode" "$n" "$div" "$u25"
