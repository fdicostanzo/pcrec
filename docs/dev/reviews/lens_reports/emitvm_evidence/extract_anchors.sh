#!/bin/bash
cd /Users/fdicostanzo/pcrec
out=/private/tmp/claude-501/-Users-fdicostanzo-pcrec/15fa957d-51f7-4fd3-8c4c-d72a871d5530/scratchpad/ep2/anchors.tsv
: > "$out"
for f in tests/mech/sabotages/S*.sh; do
  ( unset SAB_ID SAB_FILE SAB_FILE2 SAB_BEFORE SAB_BEFORE2 SAB_COUNT SAB_COUNT2 SAB_SUITES SAB_DESC SAB_EXPECT
    source "$f" 2>/dev/null
    b=$(basename "$f")
    for n in "" 2; do
      fv="SAB_FILE$n"; bv="SAB_BEFORE$n"; cv="SAB_COUNT$n"
      file="${!fv}"; before="${!bv}"; cnt="${!cv:-1}"
      [ -z "$file" ] && continue
      case "$file" in *emit_vm.c) ;; *) continue;; esac
      printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$b" "${n:-1}" "$cnt" "${SAB_SUITES}" "${SAB_EXPECT:-DETECTED}" "$(printf '%s' "$before" | head -1)" >> "$out"
      printf '%s\x01%s\x01%s\n' "$b" "${n:-1}" "$before" >> "${out}.raw"
    done
  )
done
wc -l "$out"
