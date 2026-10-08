#!/usr/bin/env bash
# docs/design/dec_fallback/state_readers.sh -- dec_fallback.md §2.1's reader
# census, REVISION 2 (critB2 M6): the field list is DERIVED from the
# declarations, never hand-kept. Lists every CODE line (comment lines dropped:
# a line whose first non-blank characters are `*`, `/*` or `//`) under src/
# that names one of the fallback family's state members or token derivations,
# so the design's member list is checked against the tree rather than
# remembered (K35).
#
# THE FOUR DERIVED SOURCES (each must be non-empty, else exit 2):
#   E  every member of `EngineFit` (src/core/internal.h), matched QUALIFIED
#      (`.m` / `->m`), since `prefilter`, `chosen` and `why` are common words;
#   L  every compile_driver local declared above the attempt loop, not
#      `const`, that the recovery point (the `if (setjmp(cx.jb))` block)
#      NAMES: the cross-attempt state the fallback reads or writes (the
#      `volatile` scalars, the `st_*` arrays, `overflow_why`, `defo` whose
#      flags the drop rows OR into), matched bare;
#   R  every `cx.M` member the recovery point (the `if (setjmp(cx.jb))`
#      block) reads or writes, matched QUALIFIED (`.M` / `->M`), plus every
#      `cx.job->A.B` there as the qualified pair `A.B` (`pf.forcing`,
#      `fit.chosen`, ...);
#   S  every Ctx member compile_driver seeds from a same-named L local at
#      the attempt head (`cx.M = M;`), matched QUALIFIED;
#   V  every value of the four enums the family's state carries, read off
#      the enum block that declares CR_SEL1 / SDR_NO_PREMUL / PFLW_SEL1 /
#      ESEL_SELECTED (a prefix grep would also catch the start table's
#      `CR_VM`/`CR_DFA`, a different enum).
# Plus D, the DECLARED token derivations (functions; each name must occur in
# src/, else exit 2).
# Read-only. Usage: state_readers.sh [ROOT] > state_readers.txt
set -euo pipefail
ROOT="${1:-$(git rev-parse --show-toplevel)}"
cd "$ROOT"
H=src/core/internal.h C=src/core/compile.c

q() { printf '%s\n' $1 | sed 's/^/(\\.|->)/' | paste -sd'|' -; }
b() { printf '%s\n' $1 | paste -sd'|' -; }
nonempty() { [ -n "$2" ] || { echo "state_readers.sh: derived source $1 is EMPTY -- extraction broke (K35)" >&2; exit 2; }; }

# E: EngineFit members (the typedef block ending `} EngineFit;`).
E=$(awk '/^typedef struct \{/ {buf=""; on=1; next}
         on && /^\} EngineFit;/ {print buf; exit}
         on {buf = buf "\n" $0}' "$H" |
    grep -vE '^\s*(\*|/\*|//)' | sed 's,/\*.*,,' |
    grep -oE '[A-Za-z_][A-Za-z0-9_]*\s*(\[[^]]*\])?\s*;' | grep -oE '^[A-Za-z_][A-Za-z0-9_]*' | sort -u | tr '\n' ' ')
nonempty E "$E"

# compile_driver's body up to the attempt loop, and its recovery block.
DSTART=$(grep -n '^static int compile_driver(' "$C" | cut -d: -f1)
LOOP=$(awk -v s="$DSTART" 'NR>s && /for \(volatile int attempt = 0;/ {print NR; exit}' "$C")
nonempty DSTART "$DSTART"; nonempty LOOP "$LOOP"
CATCH=$(awk -v s="$LOOP" 'NR>s && /if \(setjmp\(cx\.jb\)\) \{/ {on=1; d=0}
         on { n=gsub(/\{/,"{"); m=gsub(/\}/,"}"); d+=n-m; print; if (d==0 && NR>s) exit }' "$C")
nonempty CATCH "$CATCH"
# comment lines dropped; a here-string, never `printf | grep -q` (pipefail +
# grep -q's early exit SIGPIPEs the printf and drops names silently).
CATCHC=$(grep -vE '^\s*(\*|/\*|//)' <<<"$CATCH")
L=$(sed -n "${DSTART},${LOOP}p" "$C" | grep -E '^    [A-Za-z]' | grep -vE '^\s*(const|return|if|for|memset|\(void\))' |
    grep -E ';\s*(/\*.*)?$' | sed 's,/\*.*,,; s/=[^,;]*//g' |
    sed -E 's/^\s*(volatile\s+)?(unsigned\s+long\s+long|unsigned\s+char|unsigned|long\s+long|[A-Za-z_][A-Za-z0-9_]*)\s+//' |
    tr ',' '\n' | sed -E 's/\[.*//; s/[;* ]//g' | grep -E '^[a-z_][a-z0-9_]*$' | sort -u |
    while read -r v; do grep -qwE "$v" <<<"$CATCHC" && echo "$v"; done | tr '\n' ' ')
nonempty L "$L"


R=$(printf '%s\n' "$CATCH" | grep -vE '^\s*(\*|/\*|//)' | grep -oE 'cx\.[a-z_][a-z0-9_]*' | sed 's/^cx\.//' |
    grep -vxE 'job|jb|opt|arena|err' | sort -u | tr '\n' ' ')
RQ=$(printf '%s\n' "$CATCH" | grep -vE '^\s*(\*|/\*|//)' | grep -oE 'cx\.job->[a-z_]+\.[a-z_]+' | sed 's/^cx\.job->//' |
     sort -u | tr '\n' ' ')
nonempty R "$R"; nonempty RQ "$RQ"

S=$(sed -n "${DSTART},\$p" "$C" | grep -oE '^\s+cx\.([a-z_][a-z0-9_]*) = \1;' | sed -E 's/^\s+cx\.([a-z_0-9]+) .*/\1/' |
    sort -u | while read -r v; do case " $L " in *" $v "*) echo "$v";; esac; done | tr '\n' ' ')
nonempty S "$S"

D='esel_of lang_nullable_declinable prefilter_decision fit_rungs fit_select fit_rung_denied fit_rung_of fit_collapse_applies fit_anchored_applies fit_prefilter_applies fit_always size_term_choose size_drop_note forces_dfa_overflow pcrec_engine_sel_name'
for d in $D; do grep -rqwE "$d" src || { echo "state_readers.sh: declared name $d no longer occurs in src/" >&2; exit 2; }; done
V=""
for anchor in CR_SEL1 SDR_NO_PREMUL PFLW_SEL1 ESEL_SELECTED; do
    pre=${anchor%%_*}_
    vals=$(awk -v a="$anchor" '/^(typedef )?enum/ {buf=""; on=1} on {buf = buf "\n" $0}
            on && /\}/ { if (buf ~ ("[^A-Za-z0-9_]" a "[^A-Za-z0-9_]")) { print buf; exit } on=0 }' "$H" |
           grep -vE '^\s*(\*|/\*|//)' | grep -oE "\\b${pre}[A-Z0-9_]+\\b" | sort -u | tr '\n' ' ')
    nonempty "V:$anchor" "$vals"
    V="$V$vals"
done
ENUMS=$(b "$V")

QUAL="$(q "$E $R $S")|$(printf '%s\n' $RQ | sed 's/\./(\\.|->)/; s/^/\\b/' | paste -sd'|' -)"
BARE="$(b "$D")|$ENUMS"
LOC="$(b "$L")"
PAT="($QUAL)\\b|\\b($BARE)\\b"
# L's names are compile_driver LOCALS: matched bare in src/core/compile.c only
# (the same spelling elsewhere -- facts_dump.c's own `defo` -- is another
# variable).
PATC="$PAT|\\b($LOC)\\b"

echo "# state_readers.sh (rev 2, derived) at $(git rev-parse --short HEAD); one line per code line"
echo "# E (EngineFit members, qualified): $E"
echo "# L (compile_driver cross-attempt locals, bare): $L"
echo "# R (recovery-point Ctx members, qualified): $R"
echo "# RQ (recovery-point cx.job-> pairs): $RQ"
echo "# S (Ctx members seeded at the attempt head, qualified): $S"
echo "# V (enum values, from their enum blocks): $V"
echo "# D (declared derivations, existence-checked): $D"
echo "# file:line<TAB>names<TAB>text"
{ grep -rnE "$PAT" src --include=*.c --include=*.h | grep -v '^src/core/compile\.c:'
  grep -nE "$PATC" src/core/compile.c | sed 's,^,src/core/compile.c:,'; } |
while IFS= read -r l; do
    f=${l%%:*}; rest=${l#*:}; n=${rest%%:*}; txt=${rest#*:}
    p="$PAT"; [ "$f" = src/core/compile.c ] && p="$PATC"
    case "$(printf '%s' "$txt" | sed 's/^[[:space:]]*//')" in
        '*'*|'/*'*|'//'*) continue ;;
    esac
    names=$(printf '%s' "$txt" | grep -oE "$p" | sed -E 's/^(\.|->)//' | sort -u | tr '\n' ',' | sed 's/,$//')
    printf '%s:%s\t%s\t%s\n' "$f" "$n" "$names" "$(printf '%s' "$txt" | sed 's/^[[:space:]]*//' | cut -c1-110)"
done
