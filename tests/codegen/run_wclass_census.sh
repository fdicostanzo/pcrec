#!/usr/bin/env bash
# tests/codegen/run_wclass_census.sh — [CLS-TREE] S3's A_WCLASS checks.
#
# S3 wraps every class the encoding spells in more than one code unit in an
# `A_WCLASS` node carrying the code-point set, with today's byte-level
# alternation as its child, and makes EVERY reader walk the child — a
# byte-identical refactor (docs/design/cls_tree_design.md §6's S3 row,
# docs/dev/cls_s3_reader_inventory.md §10). The byte identity itself is
# `scripts/cls_identity.py`'s (a reference build is outside what `make test`
# can have); this script holds what can be checked on one tree:
#
#   PART 1  the switch census (tests/codegen/wclass_census.py): every AKind
#           switch handles the kind, none shares an arm with `A_CLASS`, none
#           carries a `default:`; with its own population floor and a
#           self-test in the failing direction.
#   PART 2  four witnesses, each pinned to the reader it exists for, each an
#           artifact-level fact the reader's WRONG walk moves (all four were
#           moved by a hand plant on the S3 lane — docs/dev/lanes/
#           s3build_report.md §2):
#             W1  `éabc` (-e utf8, --engine=vm): the spine flattener sees
#                 through the wrapper, so the literal run is the five bytes
#                 C3 A9 a b c, one compare (D-3, `pcrec_ast_seethru`);
#             W2  `(é)+` (-e utf8): `vm_det_seq` walks the child, so the
#                 quantifier keeps the CURSOR rung (a two-byte stride);
#             W3  `café|naïve|résumé` (-e utf8, --engine=vm): `vm_isl_words`
#                 walks the child, so the wide literals keep their island;
#             W4  `x[é]y` (-e utf8, --engine=vm): compiles — the kind guard
#                 in `pcrec_cls_bits` is silent on a correct tree, and a
#                 reader that renders the SET of this Latin-1-range class
#                 instead of walking the child refuses LOUDLY by it (no range
#                 check can). The class is a spine ITEM here, not the head:
#                 at the head `pcrec_ast_seethru` hands the flattener the
#                 child and `vm_emit` never meets the wrapper (`[é]x` does
#                 not reach the arm; measured).
#
# Output: PASS:/FAIL: lines and the `checks passed:`/`checks failed:` trailer.
# Usage: bash tests/codegen/run_wclass_census.sh

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"

pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass+1)); }
bad() { echo "FAIL: $*" >&2; fail=$((fail+1)); }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/wclass.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

echo "== PART 1: the AKind switch census =="
out="$(python3 "$SCRIPT_DIR/wclass_census.py" "$ROOT_DIR/src" 2>&1)"; rc=$?
while IFS= read -r line; do
    case "$line" in
        PASS:*) ok "${line#PASS: }" ;;
        FAIL:*) bad "${line#FAIL: }" ;;
    esac
done <<< "$out"
if [ "$rc" -ne 0 ] && ! grep -q '^FAIL:' <<< "$out"; then
    bad "[5] wclass_census.py exited $rc with no FAIL line: $out"
fi

echo "== PART 2: the reader witnesses =="
# compile PATTERN OUT FLAGS... -> 0 and the artifact at OUT, or the diagnostic
compile() {
    local pat="$1" out="$2"; shift 2
    "$TIMEOUT_BIN" 120 "$PCREC" -p rx "$@" -o "$out" --pattern "$pat" \
        > /dev/null 2> "$out.err"
}

if compile 'éabc' "$TMP/w1.c" -e utf8 --engine=vm; then
    if grep -q '"\\303\\251abc", 5)' "$TMP/w1.c"; then
        ok "[W1] éabc: the lowered class unrolls into the spine — one five-byte run compare"
    else
        bad "[W1] éabc: no five-byte run \"\\303\\251abc\" in the artifact — a spine flattener stopped at the A_WCLASS wrapper (pcrec_ast_seethru, D-3)"
    fi
else
    bad "[W1] éabc -e utf8 --engine=vm refused: $(head -c 300 "$TMP/w1.c.err")"
fi

if compile '(é)+' "$TMP/w2.c" -e utf8; then
    if grep -q '^#define RX_VM_RUNGS 0x1u$' "$TMP/w2.c"; then
        ok "[W2] (é)+: the quantifier keeps the cursor rung (RX_VM_RUNGS 0x1u)"
    else
        bad "[W2] (é)+: $(grep '^#define RX_VM_RUNGS' "$TMP/w2.c") where 0x1u (cursor) was — vm_det_seq/vm_cap_offsets stopped walking the A_WCLASS child"
    fi
else
    bad "[W2] (é)+ -e utf8 refused: $(head -c 300 "$TMP/w2.c.err")"
fi

if compile 'café|naïve|résumé' "$TMP/w3.c" -e utf8 --engine=vm; then
    if grep -q '^#define RX_VM_ALT_ISLANDS 1$' "$TMP/w3.c"; then
        ok "[W3] café|naïve|résumé: the wide literals keep their island (RX_VM_ALT_ISLANDS 1)"
    else
        bad "[W3] café|naïve|résumé: the island is gone — vm_isl_words stopped walking the A_WCLASS child"
    fi
else
    bad "[W3] café|naïve|résumé -e utf8 --engine=vm refused: $(head -c 300 "$TMP/w3.c.err")"
fi

if compile 'x[é]y' "$TMP/w4.c" -e utf8 --engine=vm; then
    ok "[W4] x[é]y -e utf8 --engine=vm compiles: no reader renders a wide class's set"
else
    bad "[W4] x[é]y -e utf8 --engine=vm refused — a reader handed the A_WCLASS to a set renderer: $(head -c 300 "$TMP/w4.c.err")"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
