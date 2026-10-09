#!/bin/bash
# verdicts.sh OUT -> "id<TAB>verdict", sorted (the matrix's id and last column)
grep -E $'^S[0-9]+-[^\t]*\t' "$1" | awk -F'\t' '{print $1"\t"$NF}' | sort
