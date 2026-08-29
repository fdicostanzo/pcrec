#!/bin/bash
set -u
SC=/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/levers
BIN=/home/duxevents/pcrec/worktrees/artsize3/build/pcrec
cd "$SC" || exit 1
: > popC_emit.log
: > popC_results.jsonl
while IFS=$'\t' read -r id pat srcfile; do
  out="artifacts_C/${id}.c"
  gnutimeout 20 "$BIN" -p rx --features all -o - -- "$pat" > "$out" 2> "artifacts_C/${id}.err"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "$id RC=$rc (compile refused or errored) pat=$pat" >> popC_emit.log
    continue
  fi
  eng=$(grep -m1 '^#define RX_ENGINE ' "$out")
  if echo "$eng" | grep -q '"vm"'; then
    python3 classify.py "$out" >> popC_results.jsonl 2>> popC_classify.err
    echo "$id OK vm $(wc -c < "$out")" >> popC_emit.log
  else
    echo "$id SKIP non-vm ($eng)" >> popC_emit.log
  fi
done < popC.tsv
echo "DONE $(wc -l < popC_results.jsonl) vm artifacts classified of $(wc -l < popC.tsv) sampled" >> popC_emit.log
