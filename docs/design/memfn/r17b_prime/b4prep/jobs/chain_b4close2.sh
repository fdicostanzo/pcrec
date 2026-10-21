#!/usr/bin/env bash
# b4close2 chain: (c) the one emit_sweep arm, then (d) the manifest sweep; each under the box lock.
set -u
W=/home/pcrec/projects/pcrec/worktrees/b4prep
O=/home/pcrec/projects/pcrec/worktrees/b4prep/build/b4c2
F=$W/docs/design/memfn/r17b_prime/fdb1
B=$W/docs/design/memfn/r17b_prime/b4prep
STREAMS=c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr,dumps
echo "== c: emit_sweep plain arm vs pcrec.ref (HEAD f1cf4e668 build)"
$W/scripts/boxlock run --label kit-b4close2 -- python3 $W/scripts/emit_sweep.py --ref-bin $O/pcrec.ref --bin $W/build/pcrec --tree $W --no-self-check --jobs 4 --streams $STREAMS --out $O/sw_plain > $O/sw_plain.log 2>&1
echo "sweep rc=$?"
tail -5 $O/sw_plain.log
echo "== d: manifest sweep (POSCOV harness)"
$W/scripts/boxlock run --label kit-b4close2 -- python3 -I $F/shadow_census.py manifest --bin $O/harness-poscov --ls-bin $W/build/pcrec --set $B/b4prep-v1max2.tsv --jobs 4 --out $O/manifest_new.tsv > $O/manifest.log 2>&1
echo "manifest rc=$?"
tail -3 $O/manifest.log
echo CHAIN-DONE
