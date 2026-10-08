#!/usr/bin/env bash
# docs/design/dec_fallback/state_readers.sh -- dec_fallback.md §2.1's reader
# census. Lists every CODE line (comment lines dropped: a line whose first
# non-blank characters are `*`, `/*` or `//`) under src/ that names one of the
# fallback family's cross-attempt STATE fields or its token derivations, so the
# design's member list is checked against the tree rather than remembered (K35).
# Read-only. Usage: state_readers.sh [ROOT] > state_readers.txt
set -euo pipefail
ROOT="${1:-$(git rev-parse --show-toplevel)}"
cd "$ROOT"
FIELDS='dfa_disabled|collapse_reason|size_drop_rung|dfa_was_engine|budget_fallback|dropped_anchored|dropped_premul|dropped_prefilter|dfa_overflowed|size_cap_refused|failed_nomem|prefilter_lang_why|size_term_why|engine_sel|prefilter_declined_nullable|prefilter_declined_nullable_default|lang_nullable_declinable|fit_rungs|fit_select|fit_rung_denied|fit_rung_of|esel_of|CR_SEL1|CR_SIZECAP|CR_NONE|SDR_[A-Z_]+|PFLW_[A-Z_]+|ESEL_[A-Z_]+'
echo "# state_readers.sh at $(git rev-parse --short HEAD); one line per code line"
echo "# file:line<TAB>fields named<TAB>text"
grep -rnE "\\b($FIELDS)\\b" src --include=*.c --include=*.h |
while IFS= read -r l; do
    f=${l%%:*}; rest=${l#*:}; n=${rest%%:*}; txt=${rest#*:}
    case "$(printf '%s' "$txt" | sed 's/^[[:space:]]*//')" in
        '*'*|'/*'*|'//'*) continue ;;
    esac
    names=$(printf '%s' "$txt" | grep -oE "\\b($FIELDS)\\b" | sort -u | tr '\n' ',' | sed 's/,$//')
    printf '%s:%s\t%s\t%s\n' "$f" "$n" "$names" "$(printf '%s' "$txt" | sed 's/^[[:space:]]*//' | cut -c1-110)"
done
