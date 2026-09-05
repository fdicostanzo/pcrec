#!/bin/sh
# probe_premises.sh — [M5.0] the pcrec-side premises, RE-VERIFIED ON HEAD
# rather than inherited from the plan rows.
#
# Every earlier design gate in this house opens with this probe for the same
# reason: a design built on what the plan row SAYS the code does is a design
# built on a document, and the documents in this tree have been wrong before
# (assertions_design.md found '(?m)' already refusing with the RIGHT module;
# backrefs_design.md found the group count asymmetric). This lane's own
# starting skeleton, the [DD-12] row, contains at least one claim that must
# be checked against the tree rather than quoted: it assigns the CharSet
# widening to MOD-0.6, and D33 §7's own 2026-08-12 amendment reassigns it to
# "the first wide producer" -- which is this milestone.
#
# Runs against THIS WORKTREE's build/pcrec. No oracle: every question here is
# about pcrec, and PCRE2 answers none of them.
set -e
cd "$(git rev-parse --show-toplevel)"
P=build/pcrec
TO="timeout 20"

# THE OUTPUT SINK IS A TEMP FILE, NOT /dev/null, AND THAT IS A REPRODUCED
# DEFECT RATHER THAN A PREFERENCE. pcrec writes OUT.c and a matching OUT.h,
# so a `-o /dev/null` sink tries to create `/dev/null.h` and every COMPILING cell
# reports "Operation not permitted" -- which reads as a refusal. This lane
# hit it on its first run AFTER docs/design/subroutines_measurements/'s own
# CLAUDE.md had already recorded it ("a /dev/null sink making every COMPILING
# cell read "Permission denied"), which is the R30 M6 shape: a defect
# reproduced verbatim by someone who had read the entry naming it.
OUT=$(mktemp -d)/o.c
trap 'rm -rf "$(dirname "$OUT")"' EXIT

if [ ! -x "$P" ]; then
    echo "!! $P is not built -- run: make -j4 CC=gcc-16"
    exit 1
fi

say() { printf '%s\n' "$*"; }
rule() { say "======================================================================"; }

say "[M5.0] pcrec-side premises, on HEAD"
rule
say "pcrec       : $(ls -l $P | awk '{print $5" bytes"}')"
say "built from  : $(git rev-parse --short HEAD) ($(git rev-parse --abbrev-ref HEAD))"
say "gcc         : $(gcc-16 -dumpversion 2>/dev/null || echo n/a)"
rule
say ""

say "======================================================================"
say "1. THE ENCODING AXIS AS IT SHIPS TODAY ([M5-SEAM], D58)"
say "======================================================================"
say "The seam is BUILT; what this lane adds is the second backend. These"
say "are the refusals the design must replace, quoted from the binary."
say ""
for e in byte utf8 utf16 UTF8 ''; do
    printf '  -e %-8s : ' "${e:-<empty>}"
    $TO $P -e "$e" -o "$OUT" 'a' 2>&1 | head -1 || true
done
say ""
say "  --help's encoding line:"
$TO $P --help 2>&1 | grep -i -A1 'encoding' | sed 's/^/    /' || true
say ""

say "======================================================================"
say "2. WHAT REFUSES TODAY, and with WHICH module name"
say "======================================================================"
say "D26 tier: a construct's EXISTENCE and its OWNING MODULE are exact."
say "These are the rows this milestone changes from refusal to producer."
say ""
for pat in '\x{3b1}' '\x41' '\p{L}' '\pL' '\P{L}' '\N{U+41}' '\X' '\R' \
           '[\x{3b1}]' '[\p{L}]' '(?i)\x{3b1}' ; do
    printf '  %-16s : ' "$pat"
    $TO $P -o "$OUT" "$pat" 2>&1 | head -1 || true
done
say ""

say "======================================================================"
say "3. THE REGISTRY ROWS this milestone owns"
say "======================================================================"
say "  (from --list-syntax; the 'built' column is D65's derived answer)"
say ""
$TO $P --list-syntax 2>/dev/null \
  | awk -F'\t' 'NR==1 || $0 ~ /unicode-props/' \
  | cut -c1-200 | sed 's/^/  /' || say "  (--list-syntax unavailable)"
say ""
say "  the module names --features accepts (from --help):"
$TO $P --help 2>&1 | grep -A6 -i 'features' | sed 's/^/    /' | head -20 || true
say ""
printf '  --features unicode-props on \\p{L} : '
$TO $P --features unicode-props -o "$OUT" '\p{L}' 2>&1 | head -1 || true
say ""

say "======================================================================"
say "4. THE CLASS STRUCTURE IS 8-BIT, and who owns widening it"
say "======================================================================"
say "D33 section 7 states the structure is uint8_t cls[32] and that MOD-0.6"
say "owns widening -- then AMENDS itself (2026-08-12, Frank): widening"
say "DEFERS to the first milestone that PRODUCES a wide set, which is this"
say "one. The [DD-12] row still says MOD-0.6. Quoted from the tree so the"
say "design cites the code and the amendment, not the stale row:"
say ""
say "  src/core/internal.h, the A_CLASS payload:"
grep -n 'uint8_t bits\[32\]' src/core/internal.h | sed 's/^/    /' || true
say ""
say "  src/ir/nfa.c, the A_CLASS lowering (one NFA state, one byte):"
sed -n '/case A_CLASS: {/,/return f;/p' src/ir/nfa.c | sed 's/^/    /' || true
say ""
say "  D33 section 7's amendment:"
sed -n '/### 7. The class structure is 8-BIT NOW/,/^### 8/p' \
    docs/dev/decisions.md | sed 's/^/    /' || true
say ""

say "======================================================================"
say "5. THE CROSS-NOTE'S SITE: pcrec_maxw's A_CLASS arm"
say "======================================================================"
say "The [M5.0] row says this arm 'must become the encoding's maximum"
say "code-unit length'. Quoted here so the design can argue against its own"
say "plan row with the code in front of the reader."
say ""
say "  src/opt/mrl.c, pcrec_maxw's A_CLASS arm and its header paragraph:"
sed -n '/^ \* THE ENCODING\. .A_CLASS. answers 1 byte/,/^ \* WHAT IS UNBOUNDED/p' \
    src/opt/mrl.c | sed 's/^/    /' || true
say ""
say "  and the CONSUMER that makes it load-bearing --"
say "  src/parse/mod_lookaround.c's la_widths, the fixed-width rule:"
grep -n 'lo != hi || hi >= PCREC_W_UNBOUNDED' src/parse/mod_lookaround.c \
    | sed 's/^/    /' || true
say ""
say "  ...whose number is handed to a residual entry whose contract is in"
say "  CHARACTERS (src/gen/enc/enc_byte.c):"
grep -n 'k. CHARACTERS before .pos' src/gen/enc/enc_byte.c | sed 's/^/    /' || true
say ""
say "  THE TWO UNITS COINCIDE ONLY UNDER THE BYTE BACKEND. Nothing in the"
say "  tree can tell them apart today, which is why this is a design"
say "  question and not a bug report."
say ""

say "======================================================================"
say "6. THE SEAM'S ENTRIES, as they ship"
say "======================================================================"
$TO $P -p rx --emit-main -o /tmp/u8prem_$$.c 'a(b|c)+d' 2>/dev/null || true
if [ -f /tmp/u8prem_$$.c ]; then
    say "  residual entry points in a freshly emitted artifact:"
    grep -n '_next_pos\|_bref_match\|_back_step' /tmp/u8prem_$$.c \
        | head -12 | sed 's/^/    /' || true
    say ""
    say "  entry ids declared by the seam (src/gen/enc/enc.h):"
    grep -n 'PCREC_ENCE_' src/gen/enc/enc.h | grep '1u <<' \
        | sed 's/^/    /' || true
    rm -f /tmp/u8prem_$$.c
fi
say ""

say "======================================================================"
say "7. THE STATE CAPS the sizing measurement is compared against"
say "======================================================================"
$TO $P --list-limits 2>/dev/null \
  | awk -F'\t' 'NR==1 || $1 ~ /NFA_STATES|DFA_STATES|EMIT_CODE_BYTES|EMIT_BYTES/' \
  | cut -c1-160 | sed 's/^/  /' || say "  (--list-limits unavailable)"
say ""

say "======================================================================"
say "8. SELF-CHECK"
say "======================================================================"
n=0
printf '  8a '-e utf8' is REFUSED (this lane exists to change that): '
if $TO $P -e utf8 -o "$OUT" 'a' >/dev/null 2>&1; then
    say "NO -- it compiled"; n=$((n+1))
else
    say "yes"
fi
printf '  8b '-e byte' COMPILES (the control): '
if $TO $P -e byte -o "$OUT" 'a' >/dev/null 2>&1; then
    say "yes"
else
    say "NO -- the control fails, section 1 proves nothing"; n=$((n+1))
fi
printf '  8c '\\p{L}' is REFUSED: '
if $TO $P -o "$OUT" '\p{L}' >/dev/null 2>&1; then
    say "NO -- it compiled"; n=$((n+1))
else
    say "yes"
fi
say ""
say "  PROBLEMS: $n"
