#!/bin/bash
set -e
BEFORE_PCREC=/home/duxevents/pcrec-bench/build/pcrec-25b1984f/build/pcrec
AFTER_PCREC=/tmp/optloop2/pcrec/build/pcrec
PATTERNS_DIR=/home/duxevents/pcrec-bench/bench/capability/patterns
WORK=/tmp/optloop3/blockC/work
mkdir -p "$WORK"

declare -A PAT
PAT[nested-comment-rec]="$(cat $PATTERNS_DIR/nested-comment-rec.rx)"
PAT[float-literal-bound]="$(cat $PATTERNS_DIR/float-literal-bound.rx)"
PAT[file-ext-order]="$(cat $PATTERNS_DIR/file-ext-order.rx)"
PAT[wild-secrets-github-pat]="$(cat $PATTERNS_DIR/wild-secrets-github-pat.rx)"

declare -A ENGINE
ENGINE[nested-comment-rec]=""
ENGINE[float-literal-bound]="--engine=vm"
ENGINE[file-ext-order]="--engine=vm"
ENGINE[wild-secrets-github-pat]="--engine=vm"

for pat in "${!PAT[@]}"; do
  text="${PAT[$pat]}"
  eng="${ENGINE[$pat]}"
  for pin in before after; do
    if [ "$pin" = "before" ]; then PCREC="$BEFORE_PCREC"; else PCREC="$AFTER_PCREC"; fi
    dir="$WORK/$pat/$pin"
    mkdir -p "$dir"
    artc="$dir/art.c"
    if [ "$pin" = "before" ]; then
      # 25b1984f (abi 27) predates D118's CLI reshape: old positional/-- shape
      "$PCREC" -p rx --features all $eng -o "$artc" -- "$text" 2>"$dir/pcrec.err" \
        && echo "[$pat/$pin] compiled" || { echo "[$pat/$pin] FAILED"; cat "$dir/pcrec.err"; exit 1; }
    else
      "$PCREC" -p rx --features all $eng -o "$artc" --pattern "$text" 2>"$dir/pcrec.err" \
        && echo "[$pat/$pin] compiled" || { echo "[$pat/$pin] FAILED"; cat "$dir/pcrec.err"; exit 1; }
    fi
    gcc -O2 -std=gnu11 -c -I"$dir" -o "$dir/art.o" "$artc" 2>"$dir/gcc.err" \
      && echo "[$pat/$pin] .o built" || { echo "[$pat/$pin] GCC FAILED"; cat "$dir/gcc.err"; exit 1; }
  done
done
echo "ALL BUILT"
