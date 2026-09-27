#!/usr/bin/env bash
# tests/findings/run_findings_tests.sh — [FINDINGS] B1: the findings seam's
# DATA, STORE, STAMP and STRUCTURE, checked against sources the compiler does
# not share (docs/design/findings/design.md §8.1, §11.4, §11.6, §11.7, §13 B1).
#
#   §1 VALUES    the shipped library's normalization of the embedded default
#                equals tests/findings/default_ppm.tsv (RUNEST's own dump of
#                the table B1 replaced), sums to 1,000,000 with no byte under
#                the floor; and the §2.5 test vectors agree with an
#                INDEPENDENT python implementation (findings_ref.py) written
#                from the spec, never from the C. Replaces
#                run_offset_skip.sh's old §1.
#   §2 EMBED     every src/findings/<name>.rxt is in the store, and the text
#                the library returns is the committed file byte for byte; no
#                store name lacks a file (§8.1 [r2 A-3]).
#   §3 AGREEMENT the PRE-PARSED table a compile reads equals a fresh parse of
#                the embedded text by the library's own reader, block for
#                block (§13 B1 (3): generated from the same text, checked).
#   §4 STAMP     `<PREFIX>_FINDINGS` on real artifacts of both engines: the
#                digest equals findings_ref.py's over default_ppm.tsv; `-e
#                utf8` stamps `byte-rate=none`; a compile that asks nothing
#                stamps ""; and `rx_info.findings` mirrors the macro (§11.6).
#   §5 STRUCTURE structural_check.py (§6.3, §11.7): no reader tests a rate,
#                no rate table outside src/core/findings.c, no table pointer
#                in a *Sel struct.
#
# Verdict: this script's own `checks failed: 0` line, and under make, the
# absence of `*** [test-findings] Error` (BOILERPLATE, r2 S-F13).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
REF="python3 $SCRIPT_DIR/findings_ref.py"

PROBE="$WORKDIR/probe"
if ! gen_cc "findings probe" "$CC" -O0 -Wall -Wextra -Werror ${SANFLAGS:-} \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" -o "$PROBE" \
        "$SCRIPT_DIR/findings_probe.c" "${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}" \
        2>"$WORKDIR/probe.log"; then
    bad "could not build the findings probe against build/libpcrec.a: $(head -3 "$WORKDIR/probe.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# =========================================================================
# §1 VALUES
# =========================================================================
"$PROBE" table > "$WORKDIR/table.txt"
dline="$(grep '^default ' "$WORKDIR/table.txt" | head -1)"
if [ -z "$dline" ]; then
    bad "§1 the pre-parsed store has no 'default' block"
else
    echo "$dline" | awk '{print $6}' | tr ',' ' ' > "$WORKDIR/dcounts"
    "$PROBE" normalize < "$WORKDIR/dcounts" > "$WORKDIR/dppm"
    awk -F'\t' '!/^#/ && NF==2 {print $2}' "$SCRIPT_DIR/default_ppm.tsv" | tr '\n' ' ' \
        | sed 's/ $//' > "$WORKDIR/want"
    if [ "$(cat "$WORKDIR/dppm")" = "$(cat "$WORKDIR/want")" ]; then
        ok "§1 the embedded default normalizes to default_ppm.tsv entry for entry (256 bytes)"
    else
        bad "§1 the embedded default does NOT normalize to default_ppm.tsv — the default is no longer the table B1 replaced (design §0.7)"
    fi
    read -r tot mn < <(tr ' ' '\n' < "$WORKDIR/dppm" | awk '{t+=$1; if(NR==1||$1<m)m=$1} END{print t, m}')
    if [ "$tot" = "1000000" ] && [ "$mn" -ge 2 ]; then
        ok "§1 the default's byte-rate sums to exactly 1,000,000 ppm and no byte is under the 2 ppm floor"
    else
        bad "§1 the default's byte-rate sums to $tot with minimum $mn — the cost model reads it as a probability (offset_k_skip.md §4.1)"
    fi
fi
$REF vectors > "$WORKDIR/vec"
nvec="$(wc -l < "$WORKDIR/vec" | tr -d ' ')"
"$PROBE" normalize < "$WORKDIR/vec" > "$WORKDIR/vec.c"
$REF normalize < "$WORKDIR/vec" > "$WORKDIR/vec.py"
if [ "$nvec" -ge 3 ] && cmp -s "$WORKDIR/vec.c" "$WORKDIR/vec.py"; then
    ok "§1 the §2.5 test vectors ($nvec: all-equal, one-nonzero, negative residue) agree with the independent python normalization"
else
    bad "§1 the §2.5 test vectors disagree with findings_ref.py (or none ran: $nvec):"
    diff "$WORKDIR/vec.c" "$WORKDIR/vec.py" | head -4 >&2
fi
printf '%s\n' "$(printf '0 %.0s' $(seq 256) | sed 's/ $//')" | "$PROBE" normalize > "$WORKDIR/zero"
if grep -q '^error -1$' "$WORKDIR/zero"; then
    ok "§1 an all-zero block is refused (-1), never normalized to a table"
else
    bad "§1 an all-zero block normalized to '$(head -c 60 "$WORKDIR/zero")' — design §2.5 step 1 makes it a hard error"
fi

# =========================================================================
# §2 EMBED
# =========================================================================
"$PROBE" names | sort > "$WORKDIR/names"
( cd "$ROOT_DIR/src/findings" && ls *.rxt | sed 's/\.rxt$//' | sort ) > "$WORKDIR/files"
if [ -s "$WORKDIR/files" ] && cmp -s "$WORKDIR/names" "$WORKDIR/files"; then
    ok "§2 the store's names are exactly src/findings/*.rxt ($(wc -l < "$WORKDIR/files" | tr -d ' '))"
else
    bad "§2 the store's names differ from src/findings/*.rxt:"; diff "$WORKDIR/names" "$WORKDIR/files" >&2
fi
while read -r n; do
    "$PROBE" text "$n" > "$WORKDIR/t.$n"
    if cmp -s "$WORKDIR/t.$n" "$ROOT_DIR/src/findings/$n.rxt"; then
        ok "§2 the embedded '$n' is src/findings/$n.rxt byte for byte ($(wc -c < "$WORKDIR/t.$n" | tr -d ' ') bytes)"
    else
        bad "§2 the embedded '$n' differs from src/findings/$n.rxt — the embed dropped, truncated or mis-escaped a byte (design §8.1)"
    fi
done < "$WORKDIR/files"

# =========================================================================
# §3 AGREEMENT
# =========================================================================
"$PROBE" reparse > "$WORKDIR/reparse.txt"
nb="$(wc -l < "$WORKDIR/table.txt" | tr -d ' ')"
if [ "$nb" -ge 1 ] && cmp -s "$WORKDIR/table.txt" "$WORKDIR/reparse.txt"; then
    ok "§3 the pre-parsed table equals the library reader's parse of the embedded text ($nb block(s): bundle, kind, line, serves, 256 counts)"
else
    bad "§3 the pre-parsed table ($nb block(s)) and a fresh parse of the embedded text DISAGREE:"
    diff <(cut -c1-120 "$WORKDIR/table.txt") <(cut -c1-120 "$WORKDIR/reparse.txt") | head -6 >&2
fi

# =========================================================================
# §4 STAMP
# =========================================================================
want_digest="$($REF digest "$SCRIPT_DIR/default_ppm.tsv")"
lib_digest="$("$PROBE" default-digest)"
if [ "$lib_digest" = "$want_digest" ]; then
    ok "§4 the library's default digest $lib_digest equals the independent FNV-1a-64 over default_ppm.tsv"
else
    bad "§4 the library's default digest '$lib_digest' is not the reference '$want_digest' (design §7's byte layout)"
fi
# stamp_of FILE -> the macro's value; info_of FILE -> the initializer's
stamp_of() { sed -n 's/^#define RX_FINDINGS "\(.*\)"$/\1/p' "$1"; }
info_of()  { sed -n 's/^    \.findings = "\(.*\)",$/\1/p' "$1"; }
check_stamp() { # check_stamp LABEL EXPECT pcrec-args...
    local lbl="$1" want="$2"; shift 2
    local f="$WORKDIR/s.c"
    if ! pcrec_run "$PCREC" -p rx -o "$f" "$@" >/dev/null 2>&1; then
        bad "§4 [$lbl] did not compile: $*"; return
    fi
    local s i n
    s="$(stamp_of "$f")"; i="$(info_of "$f")"
    n="$(grep -c '^#define RX_FINDINGS ' "$f")"
    if [ "$n" = 1 ] && [ "$s" = "$want" ] && [ "$i" = "$s" ]; then
        ok "§4 [$lbl] RX_FINDINGS \"$s\" and rx_info.findings agree"
    else
        bad "§4 [$lbl] RX_FINDINGS x$n \"$s\" / rx_info.findings \"$i\", expected \"$want\" on both"
    fi
}
check_stamp "byte, DFA"       "byte-rate=default:$want_digest" --pattern 'GET /index\.html'
check_stamp "byte, VM"        "byte-rate=default:$want_digest" --features all --pattern '(a)x\1y'
check_stamp "utf8, DFA"       "byte-rate=none"                 -e utf8 --pattern 'GET /index\.html'
check_stamp "utf8, VM"        "byte-rate=none"                 -e utf8 --features all --pattern '(a)x\1y'
# Nothing asked: the necessary-byte facts denied (so no pick asks) on a
# pattern with no DFA prefilter (so the offset-k selection never runs).
check_stamp "nothing asked"   ""                               -fno-req-byte --pattern '^abc'
# Asked by the offset-k selection alone (the pick denied): the stamp is
# rendered after the LAST reader, so this ask is not lost (design §6.4 rule 2).
check_stamp "offset-k only"   "byte-rate=default:$want_digest" -fno-req-byte --pattern 'abc'

# =========================================================================
# §5 STRUCTURE
# =========================================================================
while IFS= read -r line; do
    case "$line" in
        PASS:*) ok "§5 ${line#PASS: }" ;;
        FAIL:*) bad "§5 ${line#FAIL: }" ;;
    esac
done < <(python3 "$SCRIPT_DIR/structural_check.py" "$ROOT_DIR" 2>&1)

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
