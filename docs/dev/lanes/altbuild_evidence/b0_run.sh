#!/usr/bin/env bash
# altbuild B0 rerun: REF = base 80341284e with only the abi digit bumped (the
# advtri/b3build precedent); WORK = the stage 1+2p commit 475950986 (archive).
W=/home/pcrec/projects/pcrec/worktrees/altbuild; S=/var/tmp/pcrec-pcrec/scratch/altbuild
echo "== build base96 $(date)"; make -C $S/base96 -j8 > $S/logs/base96_build.log 2>&1; echo "build rc=$?"
ES="python3 $W/scripts/emit_sweep.py --ref-bin $S/base96/build/pcrec --tree-rev 475950986 --tree $W --timeout 60"
echo "== part1 $(date)"; $ES --out $S/es1 --streams c-default,c-vm,emit-ir,emit-ir-auto,stderr,dumps --dumps-declared-rows=--list-axes:altcls-merge@1 --dumps-declared-new=--list-limits:PCREC_MAX_REQ_PIECES > $S/logs/b0_part1.log 2>&1; echo "part1 rc=$?"
echo "== part2 $(date)"; $ES --out $S/es2 --no-self-check --no-corpus --patterns-file $S/bench_patterns.txt --streams c-default,c-vm,emit-ir,emit-ir-auto,stderr > $S/logs/b0_part2.log 2>&1; echo "part2 rc=$?"
echo "== part3c $(date)"; $ES --out $S/es4 --no-self-check --keep --streams composition > $S/logs/b0_part3c.log 2>&1; echo "part3c rc=$?"
echo "== done $(date)"
