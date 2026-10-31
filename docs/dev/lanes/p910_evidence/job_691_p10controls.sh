#!/usr/bin/env bash
# 691-p910-p10controls: P10 twins over every one-attempt bench pattern (lane p910); instruction counts, not timing
set -u
S=/var/tmp/pcrec-pcrec/scratch/p910 W=/home/pcrec/projects/pcrec/worktrees/p910
case "${1:-}" in
    --dry-run)
        [ -x "$W/build/pcrec" ] || { echo "no pcrec" >&2; exit 1; }
        for f in p10_controls.py mk_p10_twins.py drv.c; do [ -f "$S/$f" ] || { echo "no $f" >&2; exit 1; }; done
        python3 -I -c "import ast; ast.parse(open('$S/p10_controls.py').read())" || exit 1
        echo "would run: python3 -I $S/p10_controls.py (reads $S/census.tsv, writes $S/p10_controls.tsv)"
        echo "boxqueue: cap 3600"; echo "boxqueue: patience none"
        echo "boxqueue: expect none reason=exec'd, so the tool's rc is the job's rc; rows counted by the lane"
        exit 0 ;;
    --ready) exec bash /home/pcrec/projects/pcrec/scripts/boxqueue after p910-census ;;
esac
export PCREC=$W/build/pcrec BENCH=/home/pcrec/projects/pcrec-bench S=$S OUT=$S/p10_controls.tsv
exec gnutimeout 3500 python3 -I $S/p10_controls.py
