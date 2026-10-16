#!/bin/sh
# rev 4 SCRATCH-GRADE probe: .text and whole-.o bytes of three VM witnesses at
# --vm-entry-shape=1..4 (the OWNED vm-entry class's existing control).
# Compile-only, single run, gcc -O2, no clock.
# usage: rev4_vmshape_o.sh PCREC SCRATCH > results/rev4_vmshape_o.tsv
P=$1; S=$2
printf 'pattern\trequested\tgot\tprogram_bytes\ttext\to_file\n'
for pat in '([a-z]+)@([a-z]+)\.com' '(\d{3})-(\d{3})-(\d{4})' '(GET|POST|PUT|DELETE|HEAD|OPTIONS) (/[a-z0-9/]{1,40}) HTTP/1\.[01]'; do
  for n in 1 2 3 4; do
    "$P" -p rx --vm-entry-shape=$n -o "$S/v.c" --pattern "$pat" 2>/dev/null || continue
    gcc -O2 -std=gnu11 -c -o "$S/v.o" "$S/v.c"
    sh=$(grep -o 'define RX_VM_ENTRY_SHAPE "[a-z]*"' "$S/v.c" | cut -d'"' -f2)
    pb=$(grep -o 'define RX_VM_PROGRAM_BYTES [0-9]*' "$S/v.c" | awk '{print $3}')
    t=$(size -A "$S/v.o" | awk '$1==".text"{print $2}')
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$pat" "$n" "$sh" "$pb" "$t" "$(stat -c %s "$S/v.o")"
  done
done
