#!/bin/bash
# regen_subjects.sh OUTDIR: `git archive` pcrec-bench (read-only) into OUTDIR,
# run the four sets' throughput and short-subject generators IN THE COPY, and
# sha256-check every subject against manifest_throughput.tsv / manifest.tsv.
# Prints OK/BAD per subject (2026-10-11 at bench d359564f: 31 + 278 OK).
set -e
O=$1; B=${BENCH_REPO:-/home/pcrec/projects/pcrec-bench}
mkdir -p "$O"; git -C "$B" archive HEAD bench pcrecbench | tar -x -C "$O"
for s in syntax capability bounded loglines; do
  (cd "$O/bench/$s" && gnutimeout 600 python3 -I gen_throughput_subjects.py >/dev/null && \
                     gnutimeout 600 python3 -I gen_subjects.py >/dev/null)
  tail -n +2 "$O/bench/$s/manifest_throughput.tsv" | while IFS=$'\t' read id len sha rest; do
    f="$O/bench/$s/throughput/$id.bin"
    [ "$(sha256sum "$f" | cut -c1-64)" = "$sha" ] && echo "OK $s/$id" || echo "BAD $s/$id"
  done
  tail -n +2 "$O/bench/$s/manifest.tsv" | while IFS=$'\t' read id len sha rest; do
    f="$O/bench/$s/subjects/$id.bin"
    [ "$(sha256sum "$f" | cut -c1-64)" = "$sha" ] && echo "OK $s/$id" || echo "BAD $s/$id"
  done
done
