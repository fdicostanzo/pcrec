#!/usr/bin/env bash
# The EXISTING inline-vs-shared dial row (compound_entries.md §3.1): the VM
# entry chain's four rungs (`--vm-entry-shape=1..4`, tuning.md §2.21) on one
# frameless VM witness, .text bytes and clockless callgrind Ir per iteration.
# usage: probe_vmshape.sh PCREC_BIN SCRATCH DRV_C
set -eu
PCREC=$1; S=$2; DRV=$3; mkdir -p "$S"
ir() { valgrind --tool=callgrind --callgrind-out-file="$S/cg.out" "$@" 2>&1 >/dev/null |
       sed -n 's/.*Collected : \([0-9]*\).*/\1/p'; }
printf 'witness\tshape\tstamp\ttext_bytes\tsubject\tIr_per_iter\n'
run_one() {  # label subject pcrec-args...
  label=$1; subj=$2; shift 2
  for shape in 1 2 3 4; do
    "$PCREC" -p rx "$@" --vm-entry-shape=$shape -o "$S/$label.$shape.c"
    gcc -O2 -std=gnu11 -c -o "$S/$label.$shape.o" "$S/$label.$shape.c"
    gcc -O2 -std=gnu11 -DARTIFACT_H="\"$label.$shape.h\"" -I"$S" -o "$S/$label.$shape.exe" "$DRV" "$S/$label.$shape.o"
    st=$(sed -n 's/^#define RX_VM_ENTRY_SHAPE "\(.*\)"/\1/p' "$S/$label.$shape.c" "$S/$label.$shape.h" | head -1)
    tb=$(size -A "$S/$label.$shape.o" | awk '$1==".text"{print $2}')
    a=$(ir "$S/$label.$shape.exe" 2000 "$subj"); b=$(ir "$S/$label.$shape.exe" 4000 "$subj")
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$label" "$shape" "$st" "$tb" "$subj" "$(( (b - a) / 2000 ))"
  done
}
run_one hybrid-frameless abababababababab --pattern '(a)b'
run_one forced-frameless abababababababab --engine=vm --pattern '(a)b'
run_one forced-frameless-sparse xxxx --engine=vm --pattern '(a)b'
