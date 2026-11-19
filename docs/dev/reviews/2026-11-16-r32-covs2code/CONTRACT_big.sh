#!/usr/bin/env bash
# big.sh NAME PATTERN [args] : watchdog compile, report time/size/route/engine-sel
D=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/CONTRACT; R=/home/pcrec/projects/pcrec/worktrees/crit-covs2code
n="$1"; pat="$2"; shift 2; mkdir -p $D/b/$n; printf '%s' "$pat" > $D/b/$n/pat
export PCREC_TMPDIR=$D TMPDIR=$D
s=$(date +%s.%N)
nice $R/scripts/watchdog -s 120 -m 2g -c 120 -S contract -- $R/build/pcrec -p rx "$@" -o $D/b/$n/a.c --pattern "$pat" 2> $D/b/$n/err.txt; rc=$?
e=$(date +%s.%N)
printf '%s rc=%s t=%.2fs size=%s route=%s sel=%s err=%s\n' "$n" $rc $(echo "$e - $s" | bc) "$(stat -c %s $D/b/$n/a.c 2>/dev/null)" "$(sed -n 's/^#define RX_DFA_SCAN "\(.*\)"/\1/p' $D/b/$n/a.c 2>/dev/null)" "$(sed -n 's/^#define RX_ENGINE_SEL "\(.*\)"/\1/p' $D/b/$n/a.c 2>/dev/null)" "$(head -c 200 $D/b/$n/err.txt | tr '\n' ' ')"
