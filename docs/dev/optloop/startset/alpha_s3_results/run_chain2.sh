#!/usr/bin/env bash
# lane alphas3 chain 2: starts when chain 1's ALL_DONE lands (one timing run at a time).
W=${W:-/home/duxevents/pcrec/scratch_lx/alphas3}
cd "$W" || exit 2
until grep -q ALL_DONE chain.log; do sleep 10; done
export S2A=$W BENCH=/home/duxevents/pcrec-bench
echo "=== density start $(date -u +%FT%TZ)"; gnutimeout 600 python3 alpha_s3_density.py > out.density.log 2>&1; echo "=== density rc=$?"
echo "=== short start $(date -u +%FT%TZ)"; gnutimeout 3600 python3 alpha_s3_short.py > out.short1.log 2>&1; echo "=== short1 rc=$?"
gnutimeout 3600 python3 alpha_s3_short.py > out.short2.log 2>&1; echo "=== short2 rc=$?"
echo ALL2_DONE $(date -u +%FT%TZ)
