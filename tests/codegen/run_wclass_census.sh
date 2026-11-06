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
#   PART 4  [RUN-POS-SET] stage 1: the lowering's box merge and the island's
#           set reading (N1-N5; docs/design/alt_normal_form.md §5 stage 1).
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
    # The five-byte run is spelled by the run-compare kit (src/gen/runcmp.c):
    # `memcmp(..., "\303\251abc", 5)` under -fno-run-overlap, two overlapping
    # four-byte words since [OPT-LITSCAN] S4 C1 (abi 58) — either spelling is
    # the one run compare this witness asks for.
    if grep -q '"\\303\\251abc", 5)' "$TMP/w1.c" ||
       grep -q 'rx_w4(subject + scan_position) == rx_w4("\\303\\251ab") && rx_w4(subject + scan_position + 1) == rx_w4("\\251abc")' "$TMP/w1.c"; then
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

# ---------------------------------------------------------------------------
# PART 3 — [CLS-TREE] S4, THE KIT ROUTE (cls_tree_design.md §2.2, §6.1).
# Structural facts the answer checks cannot see: the route is answer-neutral
# by construction, so a build that took the wrong route — or ignored the
# deny, or leaked the decoder into the public header — answers every corpus
# cell correctly. Read off the artifact's TEXT, never its stamp alone.
# ---------------------------------------------------------------------------
echo "== PART 3: the kit route =="
has()  { grep -q -- "$2" "$1"; }
kitn() { grep -oE '^#define RX_VM_CLS_KIT [0-9]+' "$1" | awk '{print $3}'; }

# [K1] a wide class on the VM is ONE decode + ONE matcher, and no byte
# alternation is left for it (the program pushes no frame for the class).
if compile 'x\p{L}y' "$TMP/k1.c" -e utf8 --engine=vm; then
    if has "$TMP/k1.c" 'rx_decode(subject, subject_length, scan_position, &cp_)' \
       && has "$TMP/k1.c" '^static inline int rx_wcls0(unsigned cp)' \
       && [ "$(kitn "$TMP/k1.c")" = 1 ] && has "$TMP/k1.c" '^#define RX_VM_FRAMELESS 1$'; then
        ok "[K1] x\\p{L}y --engine=vm: one decode + one kit matcher (RX_VM_CLS_KIT 1), frameless"
    else
        bad "[K1] x\\p{L}y --engine=vm: not one decode + kit test (kit=$(kitn "$TMP/k1.c"); $(grep '^#define RX_VM_FRAMELESS' "$TMP/k1.c"))"
    fi
else
    bad "[K1] x\\p{L}y -e utf8 --engine=vm refused: $(head -c 300 "$TMP/k1.c.err")"
fi

# [K2] -fno-cls-kit: the byte alternation, no decoder, no matcher.
if compile 'x\p{L}y' "$TMP/k2.c" -e utf8 --engine=vm -fno-cls-kit; then
    if ! has "$TMP/k2.c" 'rx_decode' && ! has "$TMP/k2.c" 'rx_wcls' && [ "$(kitn "$TMP/k2.c")" = 0 ]; then
        ok "[K2] -fno-cls-kit: no decoder, no matcher, RX_VM_CLS_KIT 0 — the byte alternation"
    else
        bad "[K2] -fno-cls-kit: the artifact still decodes or carries a matcher (kit=$(kitn "$TMP/k2.c")) — the deny does not reach the route"
    fi
else
    bad "[K2] x\\p{L}y -fno-cls-kit refused (the byte alternation of \\p{L} fits the VM cap): $(head -c 300 "$TMP/k2.c.err")"
fi

# [K3] a ONE-member wide class is a literal: bytes, not a decode.
if compile 'x(é)y' "$TMP/k3.c" -e utf8 --engine=vm; then
    if ! has "$TMP/k3.c" 'rx_decode' && [ "$(kitn "$TMP/k3.c")" = 0 ]; then
        ok "[K3] x(é)y: a one-member class keeps its bytes (RX_VM_CLS_KIT 0, no decoder)"
    else
        bad "[K3] x(é)y: a one-member class was routed to the kit (kit=$(kitn "$TMP/k3.c")) — vm_wcls_bytes lost its literal clause"
    fi
else
    bad "[K3] x(é)y -e utf8 --engine=vm refused: $(head -c 300 "$TMP/k3.c.err")"
fi

# [K4] one matcher per DISTINCT set: two sites of one set share it.
if compile '\p{L}x\p{L}y\p{N}' "$TMP/k4.c" -e utf8 --engine=vm; then
    if [ "$(kitn "$TMP/k4.c")" = 2 ]; then
        ok "[K4] \\p{L}x\\p{L}y\\p{N}: two distinct sets, two matchers (the pool dedups)"
    else
        bad "[K4] \\p{L}x\\p{L}y\\p{N}: RX_VM_CLS_KIT $(kitn "$TMP/k4.c"), want 2"
    fi
else
    bad "[K4] refused: $(head -c 300 "$TMP/k4.c.err")"
fi

# [K5] the decoder is DECLARED NOWHERE: a split artifact's public header
# carries neither it nor a matcher (a `static` prototype in a header warns
# in every includer), and the .c defines it before the program calls it.
if "$TIMEOUT_BIN" 120 "$PCREC" -p rx -e utf8 --engine=vm -o "$TMP/k5.c" \
        --pattern 'x\p{L}y' > /dev/null 2> "$TMP/k5.err" && [ -f "$TMP/k5.h" ]; then
    d="$(grep -n 'static inline size_t rx_decode' "$TMP/k5.c" | head -1 | cut -d: -f1)"
    u="$(grep -n 'len_ = rx_decode(' "$TMP/k5.c" | head -1 | cut -d: -f1)"
    if ! has "$TMP/k5.h" 'rx_decode' && ! has "$TMP/k5.h" 'rx_wcls' \
       && [ -n "$d" ] && [ -n "$u" ] && [ "$d" -lt "$u" ]; then
        ok "[K5] rx_decode: static inline, absent from the .h, defined (line $d) before its first call (line $u)"
    else
        bad "[K5] rx_decode placement: header mentions it, or defined at '${d:-none}' after its call at '${u:-none}'"
    fi
else
    bad "[K5] the split artifact did not build: $(head -c 300 "$TMP/k5.err")"
fi

# [K6] the caseless span compare REQUIRES the decoder: a caseless
# backreference artifact under utf8 defines rx_decode though no class is wide.
if compile '(a)\1' "$TMP/k6.c" -e utf8 -i --features backrefs -fno-cls-kit; then
    if has "$TMP/k6.c" 'static inline size_t rx_decode' && ! has "$TMP/k6.c" 'span_ci_decode'; then
        ok "[K6] (a)\\1 -e utf8 -i: the caseless span compare's decoder is the one rx_decode entry (requires closed the mask)"
    else
        bad "[K6] (a)\\1 -e utf8 -i: no rx_decode, or a private span_ci_decode survives — PcrecEncEntry.requires is not closing the mask"
    fi
else
    bad "[K6] (a)\\1 -e utf8 -i refused: $(head -c 300 "$TMP/k6.c.err")"
fi

# [K7] the refusals S4 retires: K55 and a captured wide class compile.
if compile '\P{Unknown}' "$TMP/k7a.c" -e utf8 --engine=vm \
   && compile '(\p{L})' "$TMP/k7b.c" -e utf8; then
    ok "[K7] \\P{Unknown} --engine=vm (K55) and (\\p{L}) at default axes compile"
else
    bad "[K7] a retired refusal is back: $(head -c 300 "$TMP/k7a.c.err") $(head -c 300 "$TMP/k7b.c.err")"
fi

# ---------------------------------------------------------------------------
# PART 4 — [RUN-POS-SET] stage 1 (docs/design/alt_normal_form.md §5 stage 1):
# the lowering's box merge (the alternation owner, rule M) and the island's
# SET reading of a wide class. COUNT witnesses: none of these can move an
# answer, so the island and box-count stamps are what a wrong build moves.
# All under `--engine=vm -fno-cls-kit` (the byte tree is what the VM walks).
# ---------------------------------------------------------------------------
echo "== PART 4: the alternation owner at the lowering =="
isl() { grep -oE '^#define RX_VM_ALT_ISLANDS [0-9]+' "$1" | awk '{print $3}'; }
VMNK=(-e utf8 --engine=vm -fno-cls-kit)

# [N1] today's admission, stated on the set: a class whose canonical split
# holds a byte RANGE (`[éè]` = one box `c3 [a8-a9]`) has no island.
if compile 'x(?:1[éè]|q2|r3)y' "$TMP/n1.c" "${VMNK[@]}"; then
    if [ "$(isl "$TMP/n1.c")" = 0 ]; then
        ok "[N1] x(?:1[éè]|q2|r3)y: a range box declines the island (RX_VM_ALT_ISLANDS 0)"
    else
        bad "[N1] x(?:1[éè]|q2|r3)y: RX_VM_ALT_ISLANDS $(isl "$TMP/n1.c") where 0 — the island's set reading admits a class whose canonical split holds a range box"
    fi
else
    bad "[N1] x(?:1[éè]|q2|r3)y refused: $(head -c 300 "$TMP/n1.c.err")"
fi

# [N2] a class at the HEAD of the island's alternation spine reaches the set
# arm (the island-local step stops at the class). Merged, its byte child is
# `c3 [a0 a9]`, which an unwrapping walk hands the trie and the trie declines.
if compile 'x(?:[éà]|q2|r3|s4)y' "$TMP/n2.c" "${VMNK[@]}"; then
    if [ "$(isl "$TMP/n2.c")" = 1 ]; then
        ok "[N2] x(?:[éà]|q2|r3|s4)y: a class at the alternation spine's head keeps the island"
    else
        bad "[N2] x(?:[éà]|q2|r3|s4)y: RX_VM_ALT_ISLANDS $(isl "$TMP/n2.c") where 1 — the island's A_ALT walk unwraps the class before the set arm sees it"
    fi
else
    bad "[N2] x(?:[éà]|q2|r3|s4)y refused: $(head -c 300 "$TMP/n2.c.err")"
fi

# [N3] the same at the head of a branch's concatenation spine.
if compile 'x(?:[éà]1|q2|r3)y' "$TMP/n3.c" "${VMNK[@]}"; then
    if [ "$(isl "$TMP/n3.c")" = 1 ]; then
        ok "[N3] x(?:[éà]1|q2|r3)y: a class at a branch's concatenation head keeps the island"
    else
        bad "[N3] x(?:[éà]1|q2|r3)y: RX_VM_ALT_ISLANDS $(isl "$TMP/n3.c") where 1 — the island's A_CAT walk unwraps the class before the set arm sees it"
    fi
else
    bad "[N3] x(?:[éà]1|q2|r3)y refused: $(head -c 300 "$TMP/n3.c.err")"
fi

# [N4] bit 10 is do-or-die at the lowering, read off the program: a bare wide
# class whose boxes merge loses its own island, and -fno-altcls-merge (the
# owner's merge denied at both callers) restores the boxes and the island.
if compile 'a[éÉ]b' "$TMP/n4a.c" "${VMNK[@]}" \
   && compile 'a[éÉ]b' "$TMP/n4b.c" "${VMNK[@]}" -fno-altcls-merge; then
    if [ "$(isl "$TMP/n4a.c")" = 0 ] && [ "$(isl "$TMP/n4b.c")" = 1 ]; then
        ok "[N4] a[éÉ]b: merged (island 0), -fno-altcls-merge restores the boxes (island 1)"
    else
        bad "[N4] a[éÉ]b: islands $(isl "$TMP/n4a.c") merged / $(isl "$TMP/n4b.c") denied where 0 / 1 — the lowering does not call the owner, or the deny does not reach it"
    fi
else
    bad "[N4] a[éÉ]b refused: $(head -c 300 "$TMP/n4a.c.err") $(head -c 300 "$TMP/n4b.c.err")"
fi

# [N5] Gate U1b: the declared merge order (width ascending, last position
# first) pinned by box counts on the widest classes, read as the VM's
# alternation entry over the bare class. A first-position-first order gives
# 105 for \p{Lu}; the counts are UCD 16.0.0's (a UCD bump re-pins them).
boxes() {
    "$TIMEOUT_BIN" 120 "$PCREC" -p rx --features all "${VMNK[@]}" --emit-ir --pattern "$1" 2>/dev/null |
        sed -n 's/.*alternation entry (\([0-9]*\) branches).*/\1/p' | head -1
}
for pin in '\p{Lu}=67' '\p{Nd}=39' '\p{L}=330' '.=8'; do
    pat="${pin%=*}"; want="${pin##*=}"; got="$(boxes "$pat")"
    if [ "$got" = "$want" ]; then
        ok "[N5] $pat lowers to $want boxes after the merge (declared order)"
    else
        bad "[N5] $pat lowers to ${got:-?} boxes where $want — the owner's merge order or rule moved (docs/design/alt_normal_form.md §3.3 Order)"
    fi
done

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
