#!/bin/bash
# docs/dev/lanes/r17b2/build.sh TREE OUT: builds OUT/harness, the equivalence
# harness: the tree's memfn/src/terms.c (the new search) linked beside the OLD
# search, terms.c at 174f3e320 (R17-b as lane r17b built it), its node cap
# turned into a variable the harness lifts. Writes only under OUT.
set -eu
W=$1; O=$2; mkdir -p "$O"
git -C "$W" show 174f3e320:memfn/src/terms.c \
  | sed 's/#include "kit.h"/#include "kit.h"\nunsigned old_budget = MF_SET_BUDGET;/; s/++q->nodes > MF_SET_BUDGET/++q->nodes > old_budget/' > "$O/old_terms.c"
grep -q 'nodes > old_budget' "$O/old_terms.c"
OLD="-Dpcrec_mf_set_terms=old_set_terms -Dpcrec_mf_cover_check=old_cover_check -Dpcrec_mf_cover_mask_w8=old_cover_mask_w8 -Dpcrec_mf_cover_member=old_cover_member -Dpcrec_mf_set_terms_probe=old_set_terms_probe"
gcc -O2 -std=gnu11 -c "$W/memfn/src/terms.c" -o "$O/new_terms.o"
gcc -O2 -std=gnu11 $OLD -I"$W/memfn/src" -c "$O/old_terms.c" -o "$O/old_terms.o"
gcc -O2 -Wall -std=gnu11 -I"$W/memfn/src" "$(dirname "$0")/harness.c" "$O/new_terms.o" "$O/old_terms.o" \
  "$W/build/libpcrec.a" -o "$O/harness"
