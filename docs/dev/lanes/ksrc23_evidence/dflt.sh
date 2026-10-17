#!/usr/bin/env bash
# the shipped default, renamed `kdefault` in both copies (emit_sweep's --data
# refuses -I for the name `default`, which resolves by identity).
cd /home/pcrec/projects/pcrec/worktrees/ksrc23
export TMPDIR=$PWD/build/t
until grep -q CHAINDONE build/m/k3summary; do sleep 20; done
d=build/es/cz/kdefault; rm -rf $d; mkdir -p $d/old $d/new
sed 's/^analysis default$/analysis kdefault/' src/findings/default.rxt > $d/old/kdefault.rxt
build/new/pcrec -I $d/old --list-analysis kdefault --view=canonical > $d/new/kdefault.rxt
gnutimeout 3600 python3 scripts/emit_sweep.py --data analysis $d/old/kdefault.rxt $d/new/kdefault.rxt \
    --bin build/kst/pcrec --expect-movers build/es/empty.tsv --out $d/out --jobs 8 > build/es/cz_kdefault.log 2>&1
echo "$(date +%T) census kdefault rc=$? $(grep -E '^\[data' build/es/cz_kdefault.log | tail -3 | tr '\n' ' ')" >> build/es/chain.log
echo "DFLTDONE" >> build/es/chain.log
