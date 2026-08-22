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
# It cannot verify that a reference is APT — only a human reads that — which is
# why it prints both sides rather than just asserting membership.
set -e
REPO=$(git rev-parse --show-toplevel)
DOC="$REPO/docs/design/atomic_groups_design.md"

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
# every SNN mention outside the table
MENTIONS=$(awk '/^### 11.4 /{t=1} /^## 12\./{t=0} !t' "$DOC" \
    | grep -on 'S[0-9][0-9][0-9]*' | sort -u -t: -k2 || true)
for m in $MENTIONS; do
    id=${m#*:}
    case " $IDS " in
        *" $id "*) ;;
        *)  # S82/S85/S86/S87 are SHIPPED rows this design cites deliberately
            case "$id" in
                S82|S85|S86|S87) continue ;;
                *) echo "  **UNDEFINED** $id is cited but has no row in §11.4"
                   FAILS=$((FAILS + 1)); continue ;;
            esac ;;
    esac
    N=$((N + 1))
    desc=$(printf '%s\n' "$TABLE" | sed -n "s/^| \*\*$id\*\* | \([^|]*\) |.*/\1/p")
    # exclude the §11.4 table's own lines (`NNN:| **SNN** | …`), or a row
    # cites itself and the reader learns nothing.
    line=$(grep -n "\b$id\b" "$DOC" | grep -v '^[0-9]*:| \*\*S' | head -1)
    echo "  $id"
    echo "     row says : $(echo "$desc" | cut -c1-88)"
    echo "     cited at : $(echo "$line" | cut -c1-100)"
done

echo
echo "mentions checked: $N   undefined: $FAILS"
if [ "$N" -eq 0 ]; then
    echo "VERDICT: no mentions found — the extractor is broken, not the document."
    exit 1
fi
if [ "$FAILS" -gt 0 ]; then
    echo "VERDICT: $FAILS citation(s) name a row that does not exist."
    exit 1
fi
echo "VERDICT: every cited row exists. APTNESS is for a reader: compare the two"
echo "lines in each pair above."
