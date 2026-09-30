#!/bin/sh
# bundle.sh -- the files the TIMING box needs: bench.c, run_bench.py, summarize.py,
# the four subject regimes and every case's arm sources.  No pcrec build needed
# on the timing box: every arm is already generated C.
set -e
cd "$(dirname "$0")"
list="bench.c run_bench.py summarize.py out/subj_ascii.bin out/subj_latin1.bin out/subj_cjk.bin out/subj_mixed.bin"
for c in c1 nd l xwd x1 x2 x3; do
  for f in base basec bigcap vm; do
    [ -f out/$c/$f.c ] && list="$list out/$c/$f.c out/$c/$f.h"
  done
  list="$list out/$c/tw_kit4.c out/$c/tw_page3w.c out/$c/tw_bitmap1.c"
done
tar czf "${1:-out/u3twin_bundle.tgz}" $list
ls -l "${1:-out/u3twin_bundle.tgz}"
