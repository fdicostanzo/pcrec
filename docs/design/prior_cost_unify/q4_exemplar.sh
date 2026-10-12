#!/usr/bin/env bash
# docs/design/prior_cost_unify/q4_exemplar.sh -- rev 2 §7 Q4's compile-only
# probe: does an EXEMPLAR bundle already decline K105's re-entry, with no
# build? Synthesizes a colon-dense digit exemplar (seeded), counts it with
# build/pcrec-analyze, compiles hcolon_in's pattern with and without it, and
# prints the NEXT-row stamp. No timing (the x1.537 cell is K105's own).
# Usage: q4_exemplar.sh ROOT OUTDIR   (writes only under OUTDIR)
set -eu
R=$1; O=$2; mkdir -p "$O"; cd "$O"
python3 -c "
import random; random.seed(1)
out=[''.join(random.choice('0123456789:') if random.random()<0.9 else random.choice('abcxyz') for _ in range(8)) for i in range(4000)]
open('colon.txt','w').write('\n'.join(out)+'\n')"
"$R/build/pcrec-analyze" --name colondense --retrieved 2026-10-11 --scan freq \
  --fidelity synthesized --adaptation "random digits and colons, pcurev Q4 probe" \
  colon.txt > colondense.rxt
pat='[a-y]\d{0,100}:'
"$R/build/pcrec" -p rx -o def.c --pattern "$pat"
"$R/build/pcrec" -p rx -I . --analysis=colondense -o ex.c --pattern "$pat"
for f in def.c ex.c; do
  printf '%s\t%s\t%s\n' "$f" "$(grep -o 'RX_DFA_PREFILTER "[^"]*"' $f)" "$(grep -o 'RX_FINDINGS "[^"]*"' $f)"
done
