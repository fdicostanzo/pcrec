#!/usr/bin/env bash
# docs/design/prior_cost_unify/island_work.sh -- rev 2 F-8's witness: the
# [ENG-ISL] alternation island charges WORK for its trie bytes where the
# denied form spends STEPS on resumes (meter_sites.tsv: work +6, push -2), so
# under a caller-tuned --work-budget the default build GIVES UP where the
# island-denied build ANSWERS -- K102's class, on a second row. Default engine
# selection (no --engine) and forced VM, one subject.
# Usage: island_work.sh PCREC OUTDIR   (writes only under OUTDIR)
set -u
P=$1; O=$2; mkdir -p "$O"
for eng in "" "--engine=vm"; do
  for f in "" "-fno-alt-island"; do
    "$P" -p rx $eng $f --work-budget=2 --emit-main -o "$O/w.c" --pattern '(foo|bar|baz)q' || continue
    gcc -O1 -o "$O/w" "$O/w.c" || continue
    printf '%s\t%s\t%s\t%s\n' "${eng:-auto}" "${f:-default}" "$(grep -o 'RX_ENGINE "[^"]*"' "$O/w.c")" "$("$O/w" fooq)"
  done
done
