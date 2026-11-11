#!/usr/bin/env bash
# tests/ucp/run_ucp_tests.sh — module `ucp`'s own section ([UCP] U1, D130),
# `make test-ucp`. The `.rxt` corpus in this directory rides `test-corpus`
# like every module's; THIS script is the three checks that corpus cannot be:
#
#   1. THE ORACLE (verify_ucp.py): every corpus cell re-checked against the
#      resolved libpcre2 with the block's options as PCRE2 verbs. python `re`
#      has no UCP, so this is the corpus's only oracle. SKIPS loudly without
#      libpcre2 (the PC-3 shape).
#   2. THE SETS (ucp_compare.py): every UCP set pcrec ships, swept over every
#      code point of both encodings, EXACTLY equal to the committed 10.46
#      store (oracle_store/libpcre2-10.46-ucp/), with the store's
#      construct==spelling relation for every utf8 set and the population
#      pinned. Box-independent — the store is the reference, no live
#      libpcre2 needed.
#   3. THE BYTE-TIER FOLD (latin1_fold_check.c): pcrec_fold_latin1 against
#      10.46's UCP|CASELESS relation over all 256x256 byte pairs.
#   4. U2's context node (run_ctxnode_tests.sh).
#   5. U3's CHARACTER-STEPPED DFA (review 2026-11-10 r4 ucpu3 checks-9):
#      (a) THE ROUTE PIN: every pattern of island.rxt and
#      tests/utf8/island_illformed.rxt compiles to RX_DFA_SCAN "char-step"
#      and RX_DFA_START "reverse-pass", with a floor on how many -- the
#      corpus tests that machine, and nothing else, only while this holds
#      (when the VM reads the set, U4, a pattern that moves is red here);
#      (b) THE ILL-FORMED FILE'S ORACLE: gen_island_rxt.py --verify re-checks
#      every cell of both files against libpcre2 under the options each
#      header declares (PCRE2_MATCH_INVALID_UTF has no in-pattern verb, so
#      verify_ucp.py cannot), with population floors. SKIPS loudly without
#      libpcre2.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/unit_cc.sh"
. "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
export PCRE2_AVAILABLE PCRE2_CFLAGS PCRE2_LIBS CC
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-ucp.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
rc=0

echo "== [UCP] 1. the corpus against libpcre2 (verify_ucp.py) =="
python3 "$SCRIPT_DIR/verify_ucp.py" || rc=1

echo "== [UCP] 2. the UCP sets against the committed 10.46 store =="
mkdir -p "$WORKDIR/cmp"
"$TIMEOUT_BIN" 1800 python3 "$SCRIPT_DIR/ucp_compare.py" "$PCREC" "$CC" "$WORKDIR/cmp" || rc=1   # [K37] bounded; each compile inside is bounded too

echo "== [UCP] 3. the byte-tier Latin-1 fold relation =="
if unit_build "$WORKDIR/l1" "$SCRIPT_DIR/latin1_fold_check.c"; then
    "$WORKDIR/l1" "$SCRIPT_DIR/latin1_fold_10.46.tsv" || rc=1
else
    echo "FAIL: latin1_fold_check.c does not build"; rc=1
fi
echo "== [UCP] 4. U2: the context node (run_ctxnode_tests.sh) =="
PCREC="$PCREC" bash "$SCRIPT_DIR/run_ctxnode_tests.sh" || rc=1

echo "== [UCP] 5. U3: the character-stepped DFA (route pin, ill-formed oracle) =="
ISL=("$SCRIPT_DIR/island.rxt" "$ROOT_DIR/tests/utf8/island_illformed.rxt")
npin=0
while IFS= read -r pat; do
    npin=$((npin + 1))
    if ! "$TIMEOUT_BIN" 120 "$PCREC" -e utf8 --features all -p rx -o "$WORKDIR/isl.c" \
            --pattern "$pat" >/dev/null 2>"$WORKDIR/isl.err"; then
        echo "FAIL: route pin: '$pat' does not compile: $(head -1 "$WORKDIR/isl.err")"; rc=1
    elif ! grep -qx '#define RX_DFA_SCAN "char-step"' "$WORKDIR/isl.c" ||
         ! grep -qx '#define RX_DFA_START "reverse-pass"' "$WORKDIR/isl.c"; then
        echo "FAIL: route pin: '$pat' left the character-stepped DFA ($(grep -E '^#define RX_(DFA_SCAN|ENGINE) ' "$WORKDIR/isl.c" | tr '\n' ' '))"; rc=1
    fi
done < <(sed -n 's/^pattern //p' "${ISL[@]}")
if [ "$npin" -lt 40 ]; then
    echo "FAIL: route pin: only $npin patterns (floor 40) -- the corpus lost its population"; rc=1
else
    echo "route pin: $npin patterns checked"
fi
python3 -I "$SCRIPT_DIR/gen_island_rxt.py" --verify "${ISL[@]}" || rc=1

[ "$rc" -eq 0 ] && echo "ucp: all checks passed" || echo "ucp: FAILED"
exit "$rc"
