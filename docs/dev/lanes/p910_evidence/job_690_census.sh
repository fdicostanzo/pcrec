#!/usr/bin/env bash
# 690-p910-census: compile-only census (corpus + bench) for lane p910 (P9 seed states, P10 REQ_WHY)
set -u
S=/var/tmp/pcrec-pcrec/scratch/p910 W=/home/pcrec/projects/pcrec/worktrees/p910
case "${1:-}" in
    --dry-run)
        [ -x "$W/build/pcrec" ] || { echo "no $W/build/pcrec" >&2; exit 1; }
        [ -f "$S/census.py" ] || { echo "no census.py" >&2; exit 1; }
        python3 -I -c "import ast,sys; ast.parse(open('$S/census.py').read())" || exit 1
        echo "would run: python3 -I $S/census.py (PCREC=$W/build/pcrec, OUT=$S/census.tsv, JOBS=4)"
        echo "boxqueue: cap 3600"; echo "boxqueue: patience none"
        echo "boxqueue: expect none reason=exec'd, so the tool's rc is the job's rc; rows are counted by the lane from census.tsv"
        exit 0 ;;
    --ready) exit 0 ;;
esac
export PCREC=$W/build/pcrec CORPUS=$W BENCH=/home/pcrec/projects/pcrec-bench OUT=$S/census.tsv JOBS=4
exec gnutimeout 3500 python3 -I $S/census.py
