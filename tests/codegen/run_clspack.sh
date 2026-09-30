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
#           (both flags), every `--tune` position, and the stamp on a class-free VM
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
# D129 Q2's one kit-level deny also denies this kit form (manager ruling,
# clspack_report.md §6 (a)): -fno-cls-kit alone leaves the bitmaps.
if compile atom-11 "$TMP/atom-11.kit.c" -fno-cls-kit \
   && [ "$(stamp "$TMP/atom-11.kit.c")" = 0 ] && [ "$(ntable "$TMP/atom-11.kit.c")" = 0 ] \
   && [ "$(nbitmap "$TMP/atom-11.kit.c")" = "$(nbitmap "$TMP/atom-11.site.c")" ]; then
    ok "[deny-kit] -fno-cls-kit: RX_VM_CLS_ATOMS 0, no atom table, the same bitmaps as -fno-cls-pack"
else bad "[deny-kit] -fno-cls-kit left stamp '$(stamp "$TMP/atom-11.kit.c")' / tables $(ntable "$TMP/atom-11.kit.c") — the kit-level deny does not reach the atom row"; fi
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

# PART 4 — [CLS-TREE] S2: THE KIT'S BYTE FORMS (the `byte-kit` row, D131 item
# 5 and D139 item 1: the size-leaning positions only, where the kit is the
# smaller form). At `--tune=-2`/`-1` a scattered byte class with fewer than
# 11 table-read siblings is tested by its kit matcher; `-fno-cls-kit` at the
# same position and flags is the bitmap it replaced. The population spans
# both size-leaning positions, a caseless class, a class reaching 0xFF from
# above 0 (its kit keeps its bound; S436), and `-e utf8` — an ASCII
# byte class and a wide class whose members all sit at or below U+00FF (its
# `<prefix>_wcls<N>` matcher is the same row, read from vm_wcls) — review
# C-L6. Same driver and cell shape as PART 3. Each witness must actually
# take a kit on the pa side (the stamp equal to the matchers the text
# defines, and > 0) and none on the pb side, or it compares nothing.
echo "== PART 4: answer identity, the kit's byte forms (--tune=-2/-1) vs -fno-cls-kit =="
kcells=0
mutants() {   # every one-byte substitution of every subject argument, \x-escaped
    printf '%s\n' "$@" | python3 -c '
import sys
for s in sys.stdin.read().split("\n"):
    if not s: continue
    b = s.encode("latin-1")
    for j in range(len(b)):
        for v in range(256):
            m = b[:j] + bytes([v]) + b[j+1:]
            print("".join("\\x%02x" % c for c in m))
'
}
kit_diff() {   # kit_diff NAME "FLAGS" PATTERN SUBJECT...
    local name="$1" fl="$2" p="$3"; shift 3
    local d="$TMP/kit-$name"; mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" --engine=vm $fl -p pa -o "$d/pa.c" --pattern "$p" >/dev/null 2>&1 \
       || ! pcrec_run "$PCREC" --engine=vm $fl -fno-cls-kit -p pb -o "$d/pb.c" --pattern "$p" >/dev/null 2>&1; then
        bad "[kit $name] a build refused ($fl)"; return
    fi
    local nk nkb st
    nk="$(grep -cE '^static inline int pa_(class_kit|wcls)[0-9]+\(unsigned cp\)' "$d/pa.c")"
    nkb="$(grep -cE '_(class_kit|wcls)[0-9]+\(' "$d/pb.c")"
    st="$(sed -n 's/^#define PA_VM_CLS_KIT //p' "$d/pa.c")"
    if [ "$nk" -gt 0 ] && [ "$st" = "$nk" ] && [ "$nkb" -eq 0 ] \
       && grep -q '^#define PB_VM_CLS_KIT 0$' "$d/pb.c"; then
        ok "[kit $name] $fl emits $nk kit matcher(s) (stamped), -fno-cls-kit none"
    else
        bad "[kit $name] kit matchers: $nk under $fl (stamp '$st'), $nkb under -fno-cls-kit — the witness does not reach the byte-kit row"
        return
    fi
    # shellcheck disable=SC2086
    if ! gen_cc "clspack kit $name" $CC -O1 -Wall -Wextra -std=gnu11 ${GENCFLAGS:-} \
            -DDIFF_A_LABEL='"byte kit"' -DDIFF_B_LABEL='"-fno-cls-kit"' \
            -I "$d" -o "$d/t" "$DRIVER" "$d/pa.c" "$d/pb.c"; then
        bad "[kit $name] the two-artifact driver did not compile: $(printf '%s' "$GEN_CC_LOG" | head -c 300)"; return
    fi
    mutants "$@" > "$d/subj"
    local out n
    if out="$(gen_run "clspack kit $name" "$d/t" < "$d/subj" 2>"$d/div")"; then
        n="$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')"
        kcells=$((kcells + ${n:-0}))
        if [ "${n:-0}" -gt 0 ]; then ok "[kit $name] $n cells agree (span, every capture slot, failure surface)"
        else bad "[kit $name] the driver compared no cells"; fi
    else
        bad "[kit $name] the byte kit and -fno-cls-kit disagree: $(head -4 "$d/div" | tr '\n' ' ')"
    fi
}
kit_diff site-10 --tune=-2 "$(pat_of site-10)" "ackrzACKRZ" "~~ugmszUGMSZ~"
kit_diff site-10-m1 --tune=-1 "$(pat_of site-10)" "ackrzACKRZ" "~~ugmszUGMSZ~"
kit_diff mixed --tune=-2 '([aeiou]+)([^a-z0-9 ]*)([02468xX]{2,})' "aei!!24x" "u~0X8"
kit_diff span --tune=-2 '[\x00-\x08\x0e-\x1f\x7f-\x9f]+|[ -/:-@]{2}' "a\x01\x02\x7f\x90b" "x!/:@y"
kit_diff caseless --tune=-1 '(?i)([aeiou]+)([^a-z]{2,})' "AeI!!" "uO~0X8"
kit_diff hi255 --tune=-2 '([a\x80-\x8f\xf0-\xff]+)z' "aaz" "a~az"
kit_diff utf8-byte "--tune=-2 -e utf8" '([aeiou]+)x' "aeiox" "uuux"
kit_diff utf8-wide "--tune=-2 -e utf8" '([\x{e0}\x{e2}\x{e9}\x{f4}]+)x' "$(printf '\303\240\303\251x')" "$(printf 'a\303\264\303\242x')"
[ "$kcells" -ge 10000 ] && ok "[kit] population $kcells cells (floor 10,000)" \
    || bad "[kit] population $kcells cells, under the 10,000 floor — the sweep reached too little"

# PART 5 — [CLS-TREE] S2's scan edge (D139 item 2): an edge's run test is the
# class-form table's answer at the scan site. At --tune=-2/-1 an edge whose
# class takes `byte-kit` tests its run with `<prefix>_<machine>_scankit<head>`
# (stamp RX_DFA_SCAN_EDGE "kit") and a fold pair takes the fold compare
# ("fold"); at 0 both read the 256-byte table ("bitmap"), and each row's flag
# puts -2 back on the next row. A range class is "range" at every position.
# Then the form-vs-deny answer differential over the DFA artifacts, as
# PART 4, with the MATCH entry compared too (`-DDIFF_MATCH`): the witnesses
# carry the edge on their reverse AND anchored machines, and `_match` is the
# only entry that runs the anchored one (review C-L6).
echo "== PART 5: the scan edge's run test is the class table's answer =="
edge_of() { sed -n 's/^#define [A-Z0-9_]*_DFA_SCAN_EDGE "\(.*\)"$/\1/p' "$1"; }
edge_case() {   # edge_case PATTERN WANT FLAGS...
    local p="$1" want="$2"; shift 2
    if ! pcrec_run "$PCREC" -p rx "$@" -o "$TMP/edge.c" --pattern "$p" >/dev/null 2>&1; then
        bad "[edge] '$p' $* refused"; return
    fi
    local got nk
    got="$(edge_of "$TMP/edge.c")"
    nk="$(grep -c '^static inline int rx_[a-z]*_scankit[0-9]*(unsigned cp)' "$TMP/edge.c")"
    local nk_ok=0
    if [ "$want" = kit ]; then [ "$nk" -gt 0 ] && nk_ok=1; else [ "$nk" -eq 0 ] && nk_ok=1; fi
    if [ "$got" = "$want" ] && [ "$nk_ok" = 1 ]; then
        ok "[edge] '$p' $* stamps \"$got\" with $nk kit matcher(s)"
    else
        bad "[edge] '$p' $* stamps \"$got\" with $nk kit matcher(s); want \"$want\""
    fi
}
edge_case 'x[aeiou]{5,30}y' kit --tune=-2
edge_case 'x[aeiou]{5,30}y' kit --tune=-1
edge_case 'x[aeiou]{5,30}y' bitmap --tune=0
edge_case 'x[aeiou]{5,30}y' bitmap --tune=2
edge_case 'x[aeiou]{5,30}y' bitmap --tune=-2 -fno-cls-kit
edge_case '(?i)xa{3,30}b' fold --tune=-2
edge_case '(?i)xa{3,30}b' bitmap --tune=0
edge_case '0[a-z]{5,30}1' range --tune=-2
edge_case '0[a-z]{5,30}1' range --tune=0
ecells=0
mcells=0
edge_diff() {   # edge_diff NAME "FLAGS" DENY WANT_A WANT_B PATTERN SUBJECT...
    local name="$1" fl="$2" deny="$3" wa="$4" wb="$5" p="$6"; shift 6
    local d="$TMP/edge-$name"; mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" $fl -p pa -o "$d/pa.c" --pattern "$p" >/dev/null 2>&1 \
       || ! pcrec_run "$PCREC" $fl "$deny" -p pb -o "$d/pb.c" --pattern "$p" >/dev/null 2>&1; then
        bad "[edge-diff $name] a build refused"; return
    fi
    if [ "$(edge_of "$d/pa.c")" != "$wa" ] || [ "$(edge_of "$d/pb.c")" != "$wb" ]; then
        bad "[edge-diff $name] the witness does not reach its forms (pa \"$(edge_of "$d/pa.c")\" want \"$wa\", pb \"$(edge_of "$d/pb.c")\" want \"$wb\")"; return
    fi
    # shellcheck disable=SC2086
    if ! gen_cc "clspack edge $name" $CC -O1 -Wall -Wextra -std=gnu11 ${GENCFLAGS:-} -DDIFF_MATCH \
            -DDIFF_A_LABEL="\"scan edge $wa\"" -DDIFF_B_LABEL="\"$deny\"" \
            -I "$d" -o "$d/t" "$DRIVER" "$d/pa.c" "$d/pb.c"; then
        bad "[edge-diff $name] the two-artifact driver did not compile: $(printf '%s' "$GEN_CC_LOG" | head -c 300)"; return
    fi
    mutants "$@" > "$d/subj"
    local out n nm
    if out="$(gen_run "clspack edge $name" "$d/t" < "$d/subj" 2>"$d/div")"; then
        n="$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')"
        nm="$(printf '%s' "$out" | sed -n 's/^match-cells \([0-9]*\)$/\1/p')"
        ecells=$((ecells + ${n:-0})); mcells=$((mcells + ${nm:-0}))
        if [ "${n:-0}" -gt 0 ] && [ "${nm:-0}" -gt 0 ]; then
            ok "[edge-diff $name] $n search + $nm match cells agree ($fl, $wa vs $deny)"
        else bad "[edge-diff $name] the driver compared no cells (search ${n:-0}, match ${nm:-0})"; fi
    else
        bad "[edge-diff $name] the scan edge's $wa and $deny disagree: $(head -4 "$d/div" | tr '\n' ' ')"
    fi
}
# THE MACHINES THE KIT REACHES, read off the text rather than assumed: the
# vowel witness must carry a kit edge on its reverse AND anchored machines.
if pcrec_run "$PCREC" --tune=-2 -p pa -o "$TMP/mach.c" --pattern 'x[aeiou]{5,30}y' >/dev/null 2>&1 \
   && grep -q '^static inline int pa_reverse_scankit[0-9]*(' "$TMP/mach.c" \
   && grep -q '^static inline int pa_anchored_scankit[0-9]*(' "$TMP/mach.c"; then
    ok "[edge-diff] the vowel witness carries kit edges on its reverse and anchored machines"
else
    bad "[edge-diff] the vowel witness no longer carries kit edges on both its reverse and anchored machines — the match-entry arm below compares nothing it was added for"
fi
edge_diff vowels --tune=-2 -fno-cls-kit kit bitmap 'x[aeiou]{5,30}y' "xaeiouay" "zzxaaaaaey"
edge_diff vowels-m1 --tune=-1 -fno-cls-kit kit bitmap 'x[aeiou]{5,30}y' "xaeiouay" "zzxaaaaaey"
edge_diff hex --tune=-2 -fno-cls-kit kit bitmap '[0-9a-fA-F]{0,16}g' "0aF9g" "ffffffffffffffffffg"
edge_diff fold --tune=-2 -fno-cls-fold fold kit '(?i)xa{3,30}b' "xAaAb" "zXaaaaAB"
edge_diff utf8 "--tune=-2 -e utf8" -fno-cls-kit kit bitmap 'x[aeiou]{5,30}y' "xaeiouay" "zzxaaaaaey"
[ "$ecells" -ge 5000 ] && ok "[edge-diff] population $ecells search cells (floor 5,000)" \
    || bad "[edge-diff] population $ecells search cells, under the 5,000 floor — the sweep reached too little"
[ "$mcells" -ge 5000 ] && ok "[edge-diff] population $mcells match cells (floor 5,000)" \
    || bad "[edge-diff] population $mcells match cells, under the 5,000 floor — the match arm reached too little"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
