#!/usr/bin/env bash
# tests/codegen/run_clspack.sh — [OPT-CLSPACK]'s checks (docs/spec/tuning.md
# §2.34; D131 item 6): the VM's table-read byte classes share ONE atom table
# when there are at least 11 of them and their byte partition has at most 64
# atoms.
#
# The witnesses are tests/base/clspack_atoms.rxt's blocks, read by case name
# (that file holds their ANSWERS against python `re`; this script holds what
# a `.rxt` block cannot see — which table form the artifact took, and that
# the two forms answer alike on every byte at every position). The shipped
# corpus has no artifact the row fires on, so without these the row's
# population is empty (docs/dev/lanes/clspack_report.md §2).
#
#   PART 1  the row, read off each artifact: the atom count stamp, the one
#           shared table, the per-class matchers, no bitmap left behind.
#           The stamp is checked against an atom count this script computes
#           from the SAME pattern's `-fno-cls-pack` artifact's bitmaps — a
#           different output, parsed here, never the compiler's own builder.
#           Plus the size term's input: the entry rung and
#           RX_VM_PROGRAM_BYTES equal the -fno-cls-pack build's.
#   PART 2  the thresholds from both sides (10 classes, 65 atoms), the deny,
#           every `--tune` position, and the stamp on a class-free VM
#           artifact and its absence on a DFA one.
#   PART 3  answer identity: each firing witness compiled both ways, linked
#           into one driver (tests/possessify/possdiff_driver.c, shared), over
#           every byte value at every position of a matching subject — span,
#           every capture slot and the failure surface.
#
# Output: PASS:/FAIL: lines and the `checks passed:`/`checks failed:` trailer.
# Usage: bash tests/codegen/run_clspack.sh

set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="clspack"
CORPUS="$ROOT_DIR/tests/base/clspack_atoms.rxt"
DRIVER="$ROOT_DIR/tests/possessify/possdiff_driver.c"

pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass+1)); }
bad() { echo "FAIL: $*" >&2; fail=$((fail+1)); }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/clspack.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# The pattern of the block named NAME in the corpus, plus its `features`.
pat_of()  { awk -v n="$1" '$0=="# case: "n {f=1; next} f && /^pattern /{sub(/^pattern /,""); print; exit}' "$CORPUS"; }
feat_of() { awk -v n="$1" '$0=="# case: "n {f=1; next} f && /^features /{print $2; exit} f && /^# case:/{exit}' "$CORPUS"; }

# compile NAME OUT [flags...]: the witness, forced onto the VM (the row is
# the VM's), with its block's features.
compile() {
    local name="$1" out="$2"; shift 2
    local p f
    p="$(pat_of "$name")"; f="$(feat_of "$name")"
    [ -n "$p" ] || { bad "corpus block '$name' not found in $CORPUS"; return 1; }
    pcrec_run "$PCREC" ${f:+--features "$f"} --engine=vm "$@" -o "$out" --pattern "$p" \
        >/dev/null 2>"$out.err"
}
stamp()   { sed -n 's/^#define [A-Z0-9_]*_VM_CLS_ATOMS \([0-9]*\)$/\1/p' "$1"; }
nbitmap() { grep -c 'static const unsigned char [a-z0-9_]*_class_bitmap[0-9]*\[32\]' "$1"; }
nmatcher(){ grep -c 'static inline int [a-z0-9_]*_class_atom[0-9]*(unsigned cp)' "$1"; }
ntable()  { grep -c 'static const unsigned char [a-z0-9_]*_class_atoms\[256\]' "$1"; }
# The atom count of an artifact's per-class bitmaps, computed HERE: the
# number of distinct membership signatures over bytes 0..255.
atoms_of_bitmaps() {
    python3 - "$1" <<'EOF'
import re, sys
t = open(sys.argv[1], "rb").read()
sets = []
for m in re.finditer(rb"_class_bitmap\d+\[32\] = \{([^}]*)\}", t):
    v = [int(x) for x in m.group(1).replace(b",", b" ").split()]
    sets.append([(v[b >> 3] >> (b & 7)) & 1 for b in range(256)])
print(len({tuple(s[b] for s in sets) for b in range(256)}) if sets else 0)
EOF
}

echo "== PART 1: the atom row fires, read off the artifact =="
for w in atom-11:11 atom-reads:12 atom-64:11; do
    name="${w%%:*}"; want="${w#*:}"
    if compile "$name" "$TMP/$name.c" && compile "$name" "$TMP/$name.site.c" -fno-cls-pack; then
        s="$(stamp "$TMP/$name.c")"; ind="$(atoms_of_bitmaps "$TMP/$name.site.c")"
        if [ "$(nbitmap "$TMP/$name.site.c")" = "$want" ] && [ -n "$s" ] && [ "$s" = "$ind" ] \
           && [ "$(ntable "$TMP/$name.c")" = 1 ] && [ "$(nmatcher "$TMP/$name.c")" = "$want" ] \
           && ! grep -q '_class_bitmap' "$TMP/$name.c"; then
            ok "[$name] $want table-read classes share one atom table: RX_VM_CLS_ATOMS $s = the $ind atoms of the -fno-cls-pack artifact's bitmaps, $want matchers, no bitmap"
        else
            bad "[$name] site bitmaps $(nbitmap "$TMP/$name.site.c") (want $want), stamp '${s}' vs computed $ind, tables $(ntable "$TMP/$name.c"), matchers $(nmatcher "$TMP/$name.c"), bitmaps left $(grep -c '_class_bitmap' "$TMP/$name.c")"
        fi
        # every table read in the program is a matcher call (the re-spelling)
        reads="$(grep -c '_class_atom[0-9]*(subject\[' "$TMP/$name.c")"
        if [ "$reads" -ge "$want" ]; then
            ok "[$name] the program reads its classes through the matchers ($reads call sites)"
        else
            bad "[$name] only $reads matcher call sites in the program for $want classes"
        fi
    else
        bad "[$name] refused: $(head -c 300 "$TMP/$name.c.err" "$TMP/$name.site.c.err" 2>/dev/null)"
    fi
done
[ "$(stamp "$TMP/atom-64.c")" = 64 ] && ok "[atom-64] exactly 64 atoms, the mask's width, fires" \
    || bad "[atom-64] RX_VM_CLS_ATOMS is '$(stamp "$TMP/atom-64.c")', want 64"

# The table form must move the table and its reads and NOTHING the size
# term decides: the entry rung is chosen on the program's length, and the
# atom spelling is shorter than the bitmap one, so a re-spelling taken
# before that choice crosses the 4,096-byte knee (measured on atom-reads,
# 4,621 bytes: rung `inline`, 2.5x the __text of its bitmap twin).
for name in atom-11 atom-reads atom-64; do
    a1="$(grep -E '^#define RX_VM_(ENTRY_SHAPE|PROGRAM_BYTES) ' "$TMP/$name.c")"
    a2="$(grep -E '^#define RX_VM_(ENTRY_SHAPE|PROGRAM_BYTES) ' "$TMP/$name.site.c")"
    if [ -n "$a1" ] && [ "$a1" = "$a2" ]; then
        ok "[$name] the entry rung and RX_VM_PROGRAM_BYTES are the -fno-cls-pack build's ($(printf '%s' "$a1" | tr '\n' ' '))"
    else
        bad "[$name] the atom table moved the size term's input: atom '$(printf '%s' "$a1" | tr '\n' ' ')' vs site '$(printf '%s' "$a2" | tr '\n' ' ')'"
    fi
done
pb="$(sed -n 's/^#define RX_VM_PROGRAM_BYTES \([0-9]*\)ULL$/\1/p' "$TMP/atom-reads.c")"
if [ "${pb:-0}" -gt 4096 ]; then ok "[atom-reads] straddles the entry knee from above ($pb bytes > 4,096), so the rung arm can fail"
else bad "[atom-reads] RX_VM_PROGRAM_BYTES '$pb' is no longer above the 4,096 knee — the rung arm above cannot fail; re-choose the witness"; fi

echo "== PART 2: the thresholds, the deny, --tune, the stamp's scope =="
if compile site-10 "$TMP/s10.c"; then
    if [ "$(stamp "$TMP/s10.c")" = 0 ] && [ "$(nbitmap "$TMP/s10.c")" = 10 ] && [ "$(ntable "$TMP/s10.c")" = 0 ]; then
        ok "[site-10] ten table-read classes: one short, a bitmap each, RX_VM_CLS_ATOMS 0"
    else bad "[site-10] stamp '$(stamp "$TMP/s10.c")', bitmaps $(nbitmap "$TMP/s10.c"), tables $(ntable "$TMP/s10.c") — the row fired below its threshold"; fi
else bad "[site-10] refused"; fi
if compile atom-65 "$TMP/a65.c"; then
    if [ "$(stamp "$TMP/a65.c")" = 0 ] && [ "$(nbitmap "$TMP/a65.c")" = 11 ] \
       && [ "$(atoms_of_bitmaps "$TMP/a65.c")" = 65 ]; then
        ok "[atom-65] eleven classes, 65 atoms: over the mask's width, a bitmap each"
    else bad "[atom-65] stamp '$(stamp "$TMP/a65.c")', bitmaps $(nbitmap "$TMP/a65.c"), atoms $(atoms_of_bitmaps "$TMP/a65.c")"; fi
else bad "[atom-65] refused"; fi
if [ "$(stamp "$TMP/atom-11.site.c" 2>/dev/null)" = 0 ] && [ "$(ntable "$TMP/atom-11.site.c")" = 0 ]; then
    ok "[deny] -fno-cls-pack: RX_VM_CLS_ATOMS 0, no atom table, the eleven bitmaps"
else bad "[deny] -fno-cls-pack left stamp '$(stamp "$TMP/atom-11.site.c")' / tables $(ntable "$TMP/atom-11.site.c") — the deny does not reach the row"; fi
for t in -2 -1 0 1 2; do
    if compile atom-11 "$TMP/t$t.c" --tune="$t" && [ "$(stamp "$TMP/t$t.c")" = "$(stamp "$TMP/atom-11.c")" ]; then
        ok "[tune $t] the atom row lists this position"
    else bad "[tune $t] RX_VM_CLS_ATOMS '$(stamp "$TMP/t$t.c")' differs from the default position's"; fi
done
if pcrec_run "$PCREC" --engine=vm -p rx -o "$TMP/none.c" --pattern '(a)b' >/dev/null 2>&1 \
   && [ "$(stamp "$TMP/none.c")" = 0 ] \
   && pcrec_run "$PCREC" -p rx -o "$TMP/dfa.c" --pattern 'a[bc]d' >/dev/null 2>&1 \
   && grep -q '^#define RX_ENGINE "dfa"' "$TMP/dfa.c" && ! grep -q '_VM_CLS_ATOMS' "$TMP/dfa.c"; then
    ok "[stamp] a class-free VM artifact stamps 0; a DFA artifact carries no stamp"
else bad "[stamp] VM '(a)b' stamps '$(stamp "$TMP/none.c")'; the DFA artifact's stamp lines: $(grep -c '_VM_CLS_ATOMS' "$TMP/dfa.c")"; fi

echo "== PART 3: answer identity, atom table vs -fno-cls-pack =="
cells=0
for name in atom-11 atom-reads atom-64; do
    d="$TMP/diff-$name"; mkdir -p "$d"
    p="$(pat_of "$name")"; f="$(feat_of "$name")"
    if ! pcrec_run "$PCREC" ${f:+--features "$f"} --engine=vm -p pa -o "$d/pa.c" --pattern "$p" >/dev/null 2>&1 \
       || ! pcrec_run "$PCREC" ${f:+--features "$f"} --engine=vm -fno-cls-pack -p pb -o "$d/pb.c" --pattern "$p" >/dev/null 2>&1; then
        bad "[diff $name] a build refused"; continue
    fi
    # shellcheck disable=SC2086
    if ! gen_cc "clspack diff $name" $CC -O1 -Wall -Wextra -std=gnu11 ${GENCFLAGS:-} \
            -DDIFF_A_LABEL='"atom table"' -DDIFF_B_LABEL='"-fno-cls-pack"' \
            -I "$d" -o "$d/t" "$DRIVER" "$d/pa.c" "$d/pb.c"; then
        bad "[diff $name] the two-artifact driver did not compile: $(printf '%s' "$GEN_CC_LOG" | head -c 300)"; continue
    fi
    # every byte 1..255 at every position of each matching subject the
    # corpus block carries (NUL too: the driver decodes \x00)
    awk -v n="$name" '$0=="# case: "n {f=1; next} f && /^# case:/{exit} f && /^m "/{match($0, /"[^"]*"/); print substr($0, RSTART+1, RLENGTH-2)}' "$CORPUS" \
      | python3 -c '
import sys
for s in sys.stdin.read().split("\n"):
    if not s: continue
    b = s.encode("latin-1")
    for j in range(len(b)):
        for v in range(256):
            m = b[:j] + bytes([v]) + b[j+1:]
            print("".join("\\x%02x" % c for c in m))
' > "$d/subj"
    if out="$(gen_run "clspack diff $name" "$d/t" < "$d/subj" 2>"$d/div")"; then
        n="$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')"
        cells=$((cells + ${n:-0}))
        if [ "${n:-0}" -gt 0 ]; then ok "[diff $name] $n cells agree (span, every capture slot, failure surface)"
        else bad "[diff $name] the driver compared no cells"; fi
    else
        bad "[diff $name] the atom table and -fno-cls-pack disagree: $(head -4 "$d/div" | tr '\n' ' ')"
    fi
done
[ "$cells" -ge 10000 ] && ok "[diff] population $cells cells (floor 10,000)" \
    || bad "[diff] population $cells cells, under the 10,000 floor — the sweep reached too little"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
