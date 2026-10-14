#!/usr/bin/env bash
# PLT probe (compound_entries.md §2.3): the cost of a part shared THROUGH AN
# EXPORTED SIBLING (`<p>_match` -> `<p>_search`, `<p>_search` -> `<p>_next_pos`)
# when the artifact is a shared object with default visibility, against the
# same object linked statically, and against the same .so built with
# -fno-semantic-interposition (internal sibling calls bound locally). Clockless: callgrind Ir per driver iteration.
# usage: probe_plt.sh PCREC_BIN SCRATCH DRV_C
set -eu
PCREC=$1; S=$2; DRV=$3; mkdir -p "$S"
ir() { valgrind --tool=callgrind --callgrind-out-file="$S/cg.out" "$@" 2>&1 >/dev/null |
       sed -n 's/.*Collected : \([0-9]*\).*/\1/p'; }
printf 'witness\tlink\tsubject\tIr_per_iter\n'
while IFS=$'\t' read -r label pat subj; do
  "$PCREC" -p rx -o "$S/$label.c" --pattern "$pat"
  gcc -O2 -std=gnu11 -c -o "$S/$label.o" "$S/$label.c"
  gcc -O2 -std=gnu11 -fPIC -shared -o "$S/lib$label.so" "$S/$label.c"
  # the same .so with the artifact's own sibling calls bound locally: the
  # difference to `shared` is the cost of the INTERNAL exported->exported edges
  # alone (the driver's calls go through the PLT in both)
  mkdir -p "$S/nsi"
  gcc -O2 -std=gnu11 -fPIC -fno-semantic-interposition -shared -o "$S/nsi/lib$label.so" "$S/$label.c"
  gcc -O2 -std=gnu11 -DARTIFACT_H="\"$label.h\"" -I"$S" -o "$S/$label.static" "$DRV" "$S/$label.o"
  gcc -O2 -std=gnu11 -DARTIFACT_H="\"$label.h\"" -I"$S" -o "$S/$label.shared" "$DRV" \
      -L"$S" -l"$label" -Wl,-rpath,"$S"
  gcc -O2 -std=gnu11 -DARTIFACT_H="\"$label.h\"" -I"$S" -o "$S/$label.shared-nsi" "$DRV" \
      -L"$S/nsi" -l"$label" -Wl,-rpath,"$S/nsi"
  for link in static shared shared-nsi; do
    a=$(ir "$S/$label.$link" 2000 "$subj"); b=$(ir "$S/$label.$link" 4000 "$subj")
    printf '%s\t%s\t%q\t%s\n' "$label" "$link" "$subj" "$(( (b - a) / 2000 ))"
  done
done <<'W'
dfa-attempt	^ab|cd	xxcdxxcd
dfa-unanch	abc	xxabcxxabc
compound-split	^\s+|\s+$	  ab cd  
W
