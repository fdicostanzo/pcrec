#!/usr/bin/env bash
# lane alphas3's detached chain on ubuntubudu (work dir $W holds base/ new/ keep/
# pre-built from `git archive` tarballs of 5d47db6b / 8148e034, keep patched).
# Sequential on purpose: one timing run at a time on the quiet box.
W=${W:-/home/duxevents/pcrec/scratch_lx/alphas3}
cd "$W" || exit 2
export S2A=$W PCREC_REPO=/nonexistent BASE_REV=5d47db6b NEW_REV=8148e034 BENCH=/home/duxevents/pcrec-bench
GT="gnutimeout"
run() { name=$1; shift; echo "=== $name start $(date -u +%FT%TZ)"; "$@" > "$W/out.$name.log" 2>&1; echo "=== $name rc=$? end $(date -u +%FT%TZ)"; }
S=$W/alpha_s3.sh
run build   $GT 3000  bash $S build
run check   $GT 3000  bash $S check
run g1classify $GT 3000 python3 $W/alpha_s3_g1.py classify
run g1build $GT 3000  python3 $W/alpha_s3_g1.py build
run g1check $GT 3000  python3 $W/alpha_s3_g1.py check
run time1   $GT 14400 bash $S time
run g1time1 $GT 14400 python3 $W/alpha_s3_g1.py time
run time2   $GT 14400 bash $S time
run g1time2 $GT 14400 python3 $W/alpha_s3_g1.py time
echo ALL_DONE $(date -u +%FT%TZ)
