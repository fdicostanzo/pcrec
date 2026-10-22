#!/usr/bin/env bash
# tests/subst/run_d27.sh -- [M4-SUBST] `make test-subst-d27`: the D27 blinded
# corpus (tests/subst/d27/, lane substd27: written from docs/spec/subst_api.md,
# lib/pcrec.h and the binary alone; adopted by lane substfix) run and SCORED.
#
# d27/run_all.sh runs the eleven differential families against libpcre2 (one
# ASan+UBSan driver process per case), the API drivers (ASan+UBSan, the
# thread driver also under TSan) and the CLI/header suite. This wrapper owns
# the verdict, which the corpus's own runner never states:
#
#   1. every family's TOTAL equals its TSV's case rows (no case lost), and
#      each case is PASS, KNOWN (a subst_api.md §9 row), PCREC_REFUSED (a
#      pattern pcrec refuses, so not a subst case) or REF_ONLY (libpcre2
#      cannot compile it) -- never FAIL, FINDING, or FIXED? (a finding row
#      that now passes must be retagged `diff`, or a regression of it would
#      read as a finding);
#   2. the API drivers: all eight built, each exit 0 with 0 FAIL and >= 1
#      PASS, and the TSan thread run exit 0;
#   3. the CLI suite: fail=0 and pass >= CLI_FLOOR (the writer's 76 cases).
#
# Without libpcre2 the section SKIPS loudly (the corpus has no oracle-free
# arm). env: PCREC, CC, TMPDIR, KEEP=1
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
export TIMEOUT_BIN
if [ -z "${PCRE2_AVAILABLE:-}" ]; then
    . "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
fi
if [ "${PCRE2_AVAILABLE:-0}" != 1 ]; then
    echo "SKIP: subst-d27 (no linkable libpcre2-8): the blinded corpus did not run"
    exit 0
fi
CLI_FLOOR=76

OUT_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/subst-d27.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$OUT_ROOT"' EXIT
export OUT_ROOT

pass=0 fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

bash "$SCRIPT_DIR/d27/run_all.sh" "$PCREC" | tee "$OUT_ROOT/run_all.log"

# ---- 1. the families ------------------------------------------------------
nfam=0
for f in "$SCRIPT_DIR"/d27/corpus/d_*.tsv; do
    fam="$(basename "$f" .tsv | sed 's/^d_//')"
    nfam=$((nfam + 1))
    log="$OUT_ROOT/diff_$fam.log"
    want="$(grep -vc '^#' "$f")"
    total="$(sed -n 's/^TOTAL \([0-9]*\) .*/\1/p' "$log" | tail -1)"
    if [ "$total" != "$want" ]; then
        bad "d27 $fam: TOTAL '${total:-none}' cases, the TSV holds $want ($(tail -3 "$log" | tr '\n' ' '))"
        continue
    fi
    line="$(grep '^TOTAL ' "$log" | tail -1)"
    n_bad=0
    for k in FAIL FINDING 'FIXED?'; do
        v="$(printf '%s\n' "$line" | tr ' ' '\n' | sed -n "s/^$k=//p")"
        [ "${v:-0}" = 0 ] || n_bad=$((n_bad + v))
    done
    np="$(printf '%s\n' "$line" | tr ' ' '\n' | sed -n 's/^PASS=//p')"
    if [ "$n_bad" = 0 ] && [ "${np:-0}" -ge 1 ]; then ok
    else
        bad "d27 $fam: $line"
        grep -E '^(FAIL|FINDING|FIXED\?)' "$log" | head -20
    fi
done
[ "$nfam" -ge 11 ] && ok || bad "d27: $nfam families found, want the eleven"

# ---- 2. the API drivers ---------------------------------------------------
api="$OUT_ROOT/api.log"
napi=0
for t in t_bind t_element t_glue t_vars t_shape t_iter t_threads t_utf; do
    l="$(grep "^== $t exit" "$api")"
    if printf '%s\n' "$l" | grep -qE "^== $t exit 0: [1-9][0-9]* pass, 0 fail"; then ok; napi=$((napi + 1))
    else bad "d27 api $t: ${l:-not run} $(grep -A3 "^== $t exit" "$api" | tail -3 | tr '\n' ' ')"
    fi
done
grep -qE '^== t_threads\(tsan\) exit 0: [1-9]' "$api" && ok || bad "d27 api t_threads under TSan: $(grep 'tsan' "$api" | head -3 | tr '\n' ' ')"
if grep -qE '^(BUILD-FAIL|CC-FAIL|RX-FAIL|SUBST-FAIL)' "$api"; then
    bad "d27 api: $(grep -E '^(BUILD-FAIL|CC-FAIL|RX-FAIL|SUBST-FAIL)' "$api" | tr '\n' ' ')"
else ok; fi

# ---- 3. the CLI suite -----------------------------------------------------
cl="$(tail -1 "$OUT_ROOT/cli.log")"
cp_="$(printf '%s\n' "$cl" | sed -n 's/^TOTAL pass=\([0-9]*\) fail=\([0-9]*\)$/\1/p')"
cf_="$(printf '%s\n' "$cl" | sed -n 's/^TOTAL pass=\([0-9]*\) fail=\([0-9]*\)$/\2/p')"
if [ "${cf_:-x}" = 0 ] && [ "${cp_:-0}" -ge "$CLI_FLOOR" ]; then ok
else
    bad "d27 cli: '$cl' (want fail=0, pass >= $CLI_FLOOR)"
    grep '^FAIL' "$OUT_ROOT/cli.log" | head -20
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
