#!/bin/sh
# probe_sref_consistency.sh — MEASURED, document-internal.
#
# [M6.4.1] REVISION 2 (r31chk re-check N3). The S88-S98 renumbering (R31 C4)
# left FIVE stale cross-references in the design's prose, each naming a
# sabotage row whose description no longer matched — and one of them named a
# CODEGEN row as the thing a CORPUS driver would catch, which is a wrong claim
# and not just a wrong number.
#
# Renumbering is going to happen again (the row block is still growing), so
# this is the check rather than a one-time fix: every `SNN` mention OUTSIDE
# §11.4's table is looked up in the table, and the probe prints the row's own
# one-line description next to the citing sentence so a reader can see whether
# they are about the same thing. A mention of a row that does not exist is a
# hard failure.
#
# **THIS PROBE'S FIRST VERSION COULD NOT CATCH THE BUG IT WAS BUILT FOR, and
# r31chk found that out.** Three defects, all of them the same defect:
#
#   (a) IT WAS MEMBERSHIP-ONLY. All five original stale references named rows
#       that EXISTED — S88, S90, S93, S94, S95 are all real rows — they just
#       named the WRONG ones. A membership test passes on every one of them.
#   (b) `sort -u` plus `head -1` showed ONE citing line per row, so the
#       Appendix A.2 site that MOTIVATED the probe ("S88 and S93", where S88 is
#       a CODEGEN row a corpus driver would never catch) was never displayed.
#   (c) the extractor excluded §11.4 but the DISPLAY grep searched the whole
#       document, so 3 of 9 displayed lines were the table's own rows citing
#       themselves.
#
# So it now prints EVERY citing line, from the extractor's own population,
# beside the row's description.
#
# **WHAT IT CAN AND CANNOT DO, stated plainly rather than implied.** It cannot
# judge APTNESS — whether "S89" is the right row for the sentence citing it is
# a question about meaning, and no grep answers it. What it does is SURFACE THE
# EVIDENCE a human needs in one place: every citation, its sentence, and the
# row's own one-line description, side by side. A reader compares them. The
# probe's only hard failures are structural: a citation naming a row that does
# not exist, or an extraction that found nothing.
#
set -e
REPO=$(git rev-parse --show-toplevel)
DOC="$REPO/docs/design/atomic_groups_design.md"

STATE=$(mktemp)
trap 'rm -f "$STATE"' EXIT

TABLE=$(awk '/^### 11.4 /{t=1} /^## 12\./{t=0} t && /^\| \*\*S[0-9]+\*\*/' "$DOC")
# NOTE: space-separated on purpose. The first version left this newline-
# separated and the `case " $IDS "` membership test then matched NOTHING, so
# every row read as UNDEFINED and the mention counter stayed 0 — caught only
# because the probe refuses to report a verdict when it checked nothing.
IDS=$(printf '%s\n' "$TABLE" | sed -n 's/^| \*\*\(S[0-9]*\)\*\*.*/\1/p' | tr '\n' ' ')
echo "rows defined in §11.4: $(printf '%s ' $IDS)"
echo

FAILS=0
N=0
# THE POPULATION: every line OUTSIDE §11.4 that cites an SNN, with its real
# document line number. No de-duplication and no `head` — one output block per
# CITATION, not per row, because a row cited twice can be right once and wrong
# once, which is exactly what happened.
CITES=$(awk '/^### 11.4 /{t=1} /^## 12\./{t=0}
             !t && /S[0-9][0-9]/ {print NR"\t"$0}' "$DOC")
[ -n "$CITES" ] || { echo "extractor found no citing lines"; exit 1; }

printf '%s\n' "$CITES" | while IFS=$(printf '\t') read -r lno text; do
    for id in $(printf '%s\n' "$text" | grep -o 'S[0-9][0-9][0-9]*' | sort -u); do
        case " $IDS " in
            *" $id "*) ;;
            *)  # S82/S85/S86/S87 are SHIPPED rows this design cites deliberately
                case "$id" in
                    S82|S85|S86|S87) continue ;;
                    *) echo "  **UNDEFINED** $id (line $lno) has no row in §11.4"
                       echo "UNDEF" >> "$STATE"; continue ;;
                esac ;;
        esac
        echo "COUNT" >> "$STATE"
        desc=$(printf '%s\n' "$TABLE" | sed -n "s/^| \*\*$id\*\* | \([^|]*\) |.*/\1/p")
        echo "  $id  (line $lno)"
        echo "     the row says : $(echo "$desc" | cut -c1-84)"
        echo "     the text says: $(echo "$text" | sed 's/^ *//' | cut -c1-84)"
    done
done
# `grep -c` PRINTS 0 and EXITS 1 when it matches nothing, so `|| echo 0`
# appends a SECOND zero and the arithmetic below then reads "0\n0" as an
# illegal number. `|| :` swallows the exit status without adding output.
# (Third `set -e` foot-gun in this directory; the pattern is always an
# assignment from a command that is ALLOWED to fail.)
N=$(grep -c COUNT "$STATE" 2>/dev/null || :)
FAILS=$(grep -c UNDEF "$STATE" 2>/dev/null || :)
N=${N:-0}; FAILS=${FAILS:-0}

echo
echo "citations checked: $N   undefined: $FAILS"
if [ "$N" -eq 0 ]; then
    echo "VERDICT: no citations found — the extractor is broken, not the document."
    exit 1
fi
if [ "$FAILS" -gt 0 ]; then
    echo "VERDICT: $FAILS citation(s) name a row that does not exist."
    exit 1
fi
echo "VERDICT: every cited row exists. THAT IS ALL THIS PROBE ASSERTS."
echo "APTNESS is a human judgement and this probe does not make it: compare"
echo "\"the row says\" with \"the text says\" in each block above. The five"
echo "references this probe was built for all named EXISTING rows, so a"
echo "structural check could never have caught them -- only a reader looking"
echo "at those two lines side by side can."
