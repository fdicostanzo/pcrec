#!/usr/bin/env bash
# Regenerates every rincensus artifact in this directory (lane rincensus, 2026-10-11).  ~1 minute on the Linux dev box.
#   docs/design/where_to_start/rincensus_run.sh BENCH_CHECKOUT SCRATCH_DIR
# Needs build/pcrec (make), libpcre2 10.46 (PCRE2_LIB), python3.  Run from the repo root.  Writes ONLY into this directory
# (rincensus_rows.tsv.gz, rincensus_summary.txt, rincensus_selftest.txt, rinner_model_multi_*.txt) and SCRATCH_DIR.
set -u
BENCH=${1:?bench checkout}; SC=${2:?scratch dir}
HERE=docs/design/where_to_start
export PCREC=${PCREC:-build/pcrec} CORPUS=. BENCH OUT="$SC" PCRE2_LIB=${PCRE2_LIB:-/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0}
TO=$(command -v gnutimeout || command -v timeout)
mkdir -p "$SC"
CAT=docs/design/eng_brep_measurements/probes/realistic_patterns.txt
for sab in "" no-border no-factor; do
  "$TO" 900 python3 $HERE/rincensus.py --workers 12 --catalog $CAT ${sab:+--sabotage $sab} || exit 1
done
cp "$SC/rincensus_rows.tsv.gz" $HERE/rincensus_rows.tsv.gz
{
  echo "provenance: pcrec $(git rev-parse --short HEAD) ($($PCREC --version 2>&1 | head -1)), bench $(git -C "$BENCH" rev-parse --short HEAD) (read only), libpcre2 $(python3 -c "
import ctypes,os
L=ctypes.CDLL(os.environ['PCRE2_LIB']);b=ctypes.create_string_buffer(64);L.pcre2_config_8(11,b);print(b.value.decode())"), python $(python3 -V | cut -d' ' -f2), walk_survey results $(git log -1 --format=%h -- studies/walk_survey/results)"
  python3 $HERE/rincensus_summary.py "$SC/rincensus_rows.tsv.gz" studies/walk_survey/results \
      "$SC/rincensus_rows_no-border.tsv.gz" "$SC/rincensus_rows_no-factor.tsv.gz"
} > $HERE/rincensus_summary.txt || exit 1
{
  echo "== rincensus.py --selftest"; python3 $HERE/rincensus.py --selftest
  for sab in no-border no-factor; do echo; echo "== rincensus.py --selftest --sabotage $sab  (must FAIL)"; python3 $HERE/rincensus.py --selftest --sabotage $sab; done
} > $HERE/rincensus_selftest.txt 2>&1
cd $HERE || exit 1
"$TO" 600 python3 rinner_model_multi.py --fixed --selftest > rinner_model_multi_fixed.txt 2>&1 || echo "fixed: FAIL"
"$TO" 1200 python3 rinner_model_multi.py --multi 6000 --distinct 6000 --shaped 1500 --seed 1 --selftest > rinner_model_multi_byte.txt 2>&1 || echo "byte: FAIL"
"$TO" 1200 python3 rinner_model_multi.py --utf8 --multi 4000 --distinct 4000 --seed 2 --selftest > rinner_model_multi_utf8.txt 2>&1 || echo "utf8: FAIL"
"$TO" 1200 python3 rinner_model_multi.py --multi 20000 --distinct 6000 --shaped 5000 --seed 7 --selftest > rinner_model_multi_byte_xl.txt 2>&1 || echo "xl: FAIL"
grep -H "^selftest:" rinner_model_multi_*.txt
