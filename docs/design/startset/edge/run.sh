#!/usr/bin/env bash
# [START-SET] edge lane (ssedge) reproduction, from the repo root after `make`:
#     W=<scratch dir> docs/design/startset/edge/run.sh [ref]
# Rebuilds the probes, regenerates the draft cells from cells.py + local libpcre2,
# and runs the mutation table and the two searches.  With `ref`, it also re-asks
# every question of the 10.46 reference over ssh (a LIGHT probe: one compile plus
# ~2k matches in /home/duxevents/pcrec/scratch_lx/ssedge) and refuses to write a
# cell the two libraries disagree on.  Needs gcc-16 and libpcre2-8 under /opt/homebrew.
set -eu
E=docs/design/startset/edge
export PCREC="$PWD/build/pcrec" W="${W:?scratch dir}" FSP="$W/fsp" ORACLE="$W/oracle"
mkdir -p "$W"
gcc-16 -O1 -std=gnu11 -Ilib -Isrc -o "$FSP" "$E/fsp.c" build/libpcrec.a
gcc-16 -O1 -I/opt/homebrew/include -o "$ORACLE" "$E/oracle.c" -L/opt/homebrew/lib -lpcre2-8
python3 "$E/gen_rxt.py" questions > "$E/out/questions.tsv"
"$ORACLE" < "$E/out/questions.tsv" > "$E/out/oracle_local.tsv"
if [ "${1:-}" = ref ]; then
  { echo __SRC__; cat "$E/oracle.c"; echo __Q__; cat "$E/out/questions.tsv"; } |
    ssh -o BatchMode=yes duxevents@100.69.121.107 'd=/home/duxevents/pcrec/scratch_lx/ssedge; mkdir -p $d && cat > $d/in && awk "/^__SRC__\$/{m=1;next} /^__Q__\$/{m=2;next} m==1{print > \"$d/oracle.c\"} m==2{print > \"$d/q.tsv\"}" $d/in && gcc -O1 -o $d/oracle $d/oracle.c $(pcre2-config --cflags --libs8) && $d/oracle < $d/q.tsv' \
    > "$E/out/oracle_ref_10.46.tsv"
  python3 "$E/gen_rxt.py" write "$E/out/oracle_local.tsv" "$E/out/oracle_ref_10.46.tsv"
else
  python3 "$E/gen_rxt.py" write "$E/out/oracle_local.tsv"
fi
python3 "$E/mut.py" "$E/out/mut" | tee "$E/out/mut_run.txt"
python3 "$E/summarize.py" "$E/out/mut" > "$E/out/mut_summary.txt"
python3 "$E/search_uncond.py" "$E/out/search_uncond_plain.tsv" 600 > "$E/out/search_uncond_plain.log"
FAMILY=collapsed python3 "$E/search_uncond.py" "$E/out/search_uncond_collapsed.tsv" 250 -fprefilter-collapse > "$E/out/search_uncond_collapsed.log"
python3 "$E/census_reseed.py" "$E/out/census_reseed.tsv" | tee "$E/out/census_reseed.txt"
