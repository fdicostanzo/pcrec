#!/bin/bash
# docs/design/start_table/reader_grep.sh -- [r2.1 checks-C-N4]: every reader
# OUTSIDE src/ of an identifier the refactor retires (refactor_edit_set.tsv's
# `def` names), found BY GREP (D94's rule: readers by grep, never a hand list).
# Revision 2's reader list was src-only. Excludes this note's own directory and
# the design/dev prose that cites the identifiers historically.
# Usage: reader_grep.sh ROOT   (read-only; prints file:line:text)
root=${1:?ROOT}
ids=$(grep -v '^#' "$root/docs/design/start_table/refactor_edit_set.tsv" \
      | awk -F'\t' '$1=="def" && $3!="C2"{print $2}' | sort -u | paste -sd'|' -)
git -C "$root" grep -nwE "$ids" -- ':!src' ':!docs/design/**' ':!docs/dev/**' \
    | cut -c1-160
