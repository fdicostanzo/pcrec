#!/bin/sh
# sizes.sh PCREC OUTDIR -- §E: today's artifact cost of the UCP property sets
# and of UCP-shaped patterns spelled with them, per engine, under -e utf8.
# Object bytes are __text + __const/__cstring/__literal8 of `gcc-16 -O2 -c`
# (cls_tree_study's sweep.obj_sizes rule, darwin size -m), so the numbers are
# comparable with cls_tree_study.md §3.
PCREC=$1 D=$2; mkdir -p "$D"
printf 'pattern\tengine\tstatus\tselected\temit_bytes\tobj_text\tobj_ro\tobj_total\tpcrec_s\n'
X='\p{Xwd}'
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  for eng in auto dfa vm; do
    t0=$(python3 -c 'import time;print(time.time())')
    if timeout 300 "$PCREC" -p rx -e utf8 --features all --engine=$eng --warn-emit-bytes=100000000 \
         -o "$D/s.c" --pattern "$pat" 2>"$D/err"; then
      t1=$(python3 -c 'import time;print(time.time())')
      sel=$(grep -m1 '#define RX_ENGINE ' "$D/s.c" | cut -d'"' -f2)
      gcc-16 -O2 -std=gnu11 -c "$D/s.c" -o "$D/s.o" 2>/dev/null
      set -- $(size -m "$D/s.o" | awk '/__text/{t+=$NF} /__const|__cstring|__literal8/{r+=$NF} END{print t+0, r+0}')
      printf '%s\t%s\tOK\t%s\t%s\t%s\t%s\t%s\t%.2f\n' "$pat" $eng "$sel" "$(wc -c < "$D/s.c" | tr -d ' ')" $1 $2 $(($1+$2)) \
        "$(python3 -c "print($t1-$t0)")"
    else
      printf '%s\t%s\tREFUSED: %s\n' "$pat" $eng "$(head -1 "$D/err" | cut -c1-100)"
    fi
  done
done <<PATS
\w
\p{Xwd}
\p{Nd}
\p{Xsp}
\p{Xwd}+
\p{Nd}{4}
a\p{Xsp}b
(?:(?<=\p{Xwd})(?!\p{Xwd})|(?<!\p{Xwd})(?=\p{Xwd}))
(?:(?<=\p{Xwd})(?!\p{Xwd})|(?<!\p{Xwd})(?=\p{Xwd}))Москва(?:(?<=\p{Xwd})(?!\p{Xwd})|(?<!\p{Xwd})(?=\p{Xwd}))
\bМосква\b
PATS
