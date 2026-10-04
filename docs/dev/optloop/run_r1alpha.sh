#!/bin/bash
# [OPTLOOP] round 1 alpha timings: ONE serial driver (lane r1alpha), run on
# the Linux box from scratch_lx/. Strictly serial; every item is cored to
# CPU 2 by its script; each item is capped by gnutimeout.
R=/home/duxevents/pcrec/scratch_lx; A=$R/r1alpha; export PCREC_REPO=$A/repo
TO=gnutimeout
echo "START $(date -u +%FT%TZ) load: $(cut -d' ' -f1-3 /proc/loadavg)"
mkdir -p $A/vedge $A/c1 $A/c3
echo "== 1 VEDGE"
S4A=$A/vedge BASE_REV=74017b71 NEW_REV=8562ff3a $TO 7200 bash $A/alpha_vedge.sh all > $A/vedge.out 2>&1
echo "VEDGE_RC=$? out=$A/vedge.out $(date -u +%FT%TZ)"
echo "== 2 C1"
S4A=$A/c1 BASE_REV=14e78104 NEW_REV=8562ff3a $TO 7200 bash $A/alpha_c1.sh all > $A/c1.out 2>&1
echo "C1_RC=$? out=$A/c1.out $(date -u +%FT%TZ)"
echo "== 3 C3"
S4A=$A/c3 BASE_REV=a588c668 NEW_REV=8562ff3a $TO 7200 bash $A/alpha_c3.sh all > $A/c3.out 2>&1
echo "C3_RC=$? out=$A/c3.out $(date -u +%FT%TZ)"
echo "== 4 A2 lpatom rerun (rows 39-40 = lpatom x gcc, clang)"
P=$R/bakeoff/a2_bakeoff_r2
cp $A/sdrv.c $P/sdrv.c && cp $A/bakeoff.sh $P/bakeoff.sh
(cd $P && ONLY=lpatom ROWCAP=900 $TO 3600 bash bakeoff.sh . 2 > $A/a2.out 2>&1)
echo "A2_RC=$? out=$A/a2.out table=$P/work/table.txt $(date -u +%FT%TZ)"
echo "ALL_DONE $(date -u +%FT%TZ)"
