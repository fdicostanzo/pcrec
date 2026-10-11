#!/bin/bash
# regen_subjects.sh OUTDIR: `git archive` pcrec-bench (read-only) into OUTDIR,
# run the four sets' throughput generators IN THE COPY, and sha256-check every
# subject against the set's manifest_throughput.tsv. Prints OK/BAD per subject.
set -e
O=$1; B=${BENCH_REPO:-/home/pcrec/projects/pcrec-bench}
mkdir -p "$O"; git -C "$B" archive HEAD bench pcrecbench | tar -x -C "$O"
for s in syntax capability bounded loglines; do
  (cd "$O/bench/$s" && gnutimeout 600 python3 -I gen_throughput_subjects.py >/dev/null)
  tail -n +2 "$O/bench/$s/manifest_throughput.tsv" | while IFS=$'\t' read id len sha rest; do
    f=$(ls "$O/bench/$s/throughput/$id"* | head -1)
    [ "$(sha256sum "$f" | cut -c1-64)" = "$sha" ] && echo "OK $s/$id" || echo "BAD $s/$id"
  done
done
