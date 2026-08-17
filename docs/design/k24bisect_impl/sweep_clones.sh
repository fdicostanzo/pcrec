#!/usr/bin/env bash
# ARCHIVED INSTRUMENT (K24 fix lane, 2026-08-17) -- provenance and reruns, the
# same posture as probe.sh next to it. It works out of a SCRATCH directory
# (variants, 8 MB subjects, built binaries); override with
#   K24_SCRATCH=/some/dir bash <this script>
# The session scratchpad it originally ran in is the default only so the
# recorded invocation is reproducible verbatim.
# K24 audit sweep: compile a pattern set to objects with the same flags the
# bench harness uses and report EVERY gcc-created .part/.constprop/.isra clone
# in the emitted artifact, per engine. Answers the VM-artifact half of the
# charter with data rather than an argument.
set -u
S="${K24_SCRATCH:-/tmp/claude-1001/-home-duxevents-pcrec/383cccce-a795-474b-afc3-b70de52a4808/scratchpad/k24fix}"
REPO="${K24_REPO:-/home/duxevents/pcrec}"
PCREC="${PCREC:-$REPO/build/pcrec}"
D="$S/sweep"; rm -rf "$D"; mkdir -p "$D"
OUT="${OUT:-$S/sweep.tsv}"
printf 'engine\tclones\tpattern\n' > "$OUT"

# Patterns: the ten compare.sh bench cases first (the floors this must not
# move), then a spread over the DFA and VM shapes the corpus exercises.
pats=(
  'needle' '(alpha|beta|gamma|delta|epsilon)'
  '[a-z0-9._]+@[a-z0-9]+\.[a-z]{2,4}' 'a*b' '[01]*1[01]{8}' 'x{40,60}y' '.*=.*'
  'a(b|c)+d' '([01]*)1([01]{8})'
  '^abc' '^(a|b)*c$' 'a.*b$' '\d{3}-\d{4}' '[[:alpha:]]+' '(?i)HeLLo'
  '(a)(b)(c)' '(foo|bar)+baz' '((a)|b){0,40}c' '(x)(?:a|bc)+d' 'a{2,5}b'
  '(\w+)\s+(\w+)' '(a*)*b' '(ab)+' 'colou?r' '[^\n]*END'
)
for p in "${pats[@]}"; do
  cdir="$D/$(printf '%s' "$p" | md5sum | cut -c1-10)"
  mkdir -p "$cdir"
  if ! timeout 120 "$PCREC" -p rx -o "$cdir/gen.c" -- "$p" >/dev/null 2>&1; then
    printf 'REJECTED\t-\t%s\n' "$p" >> "$OUT"; continue
  fi
  eng="$(grep -oE 'ENGM_(DFA|VM)' "$cdir/gen.c" | head -1)"
  if ! timeout 300 gcc -O2 -std=gnu11 -Wall -Wextra -Werror -I"$cdir" \
        -c -o "$cdir/gen.o" "$cdir/gen.c" 2>"$cdir/cc.err"; then
    printf '%s\tCCFAIL\t%s\n' "${eng:-?}" "$p" >> "$OUT"; continue
  fi
  clones="$(nm "$cdir/gen.o" | grep -oE '[A-Za-z_][A-Za-z0-9_]*\.(part|constprop|isra)\.[0-9]+' | sort -u | paste -sd, -)"
  printf '%s\t%s\t%s\n' "${eng:-?}" "${clones:-none}" "$p" >> "$OUT"
done
echo "DONE -> $OUT"; cat "$OUT"
