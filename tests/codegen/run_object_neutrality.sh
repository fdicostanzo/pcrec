#!/usr/bin/env bash
# tests/codegen/run_object_neutrality.sh — [M6-READ] the OBJECT-CODE
# NEUTRALITY gate: two pcrec builds must emit artifacts that COMPILE THE SAME.
#
# WHY THIS EXISTS. [M6-READ] rewrites the emitter's comments and renames its
# emitted local identifiers. The plan row's engineering note (i) requires the
# pass to be object-code-neutral, and names the natural check: compile before
# and after, compare object code. This is that check, at corpus scale.
#
# WHAT "NEUTRAL" MEANS, precisely. The sample stage (docs/design/m6read_samples/)
# had to pin this down, because the naive form gives a FALSE ALARM:
#
#   (a) EXECUTED CODE must be byte-identical — compared as the raw contents of
#       .text and .rodata, which contain no names at all. This is the property
#       that matters and the one this gate enforces.
#   (b) INTERNAL SYMBOL NAMES change by construction. Renaming a static
#       function or a function-local static table renames its internal-linkage
#       symbol, visible in `objdump -d` annotations, `nm` and debug info. It is
#       not executed code, does not survive `strip`, and no caller can observe
#       it — but a check diffing disassembly TEXT fails on it. Reported as
#       INFO, never as a failure.
#   (c) EXPORTED symbols must not change AT ALL. [M6-READ] promises zero ABI
#       change of any kind, and this is the line that enforces it.
#
# A rename that trips (a) or (c) is a finding about the approach, not a
# formatting nit.
#
# WHY IT IS NOT IN `make test`. It needs a SECOND compiler to compare against,
# which `make test` has no way to produce. It is a tool you point at two
# builds, in the shape of this directory's existing `*_identity.sh` checks —
# except that those build their reference from the same sources with a `-D`
# knob, and this one takes a genuinely independent binary. Wave D's finding
# (tests/codegen/CLAUDE.md) is why that difference matters: a knob build
# compiled from the same sabotaged sources can CANCEL the sabotage.
#
# Usage:
#   bash tests/codegen/run_object_neutrality.sh REFERENCE_PCREC [CURRENT_PCREC]
#
# Producing the reference (the pre-conversion build):
#   git worktree add /tmp/ref <pre-conversion-commit> && make -C /tmp/ref
#   bash tests/codegen/run_object_neutrality.sh /tmp/ref/build/pcrec
#
# Env: CC, NEUT_N (patterns to sweep; default 0 = every corpus pattern),
#      NEUT_CFLAGS (default -O2 -g0), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
REF="${1:-}"
CUR="${2:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
NEUT_CFLAGS="${NEUT_CFLAGS:--O2 -g0 -std=gnu11}"
NEUT_N="${NEUT_N:-0}"
KEEP="${KEEP:-0}"

if [ -z "$REF" ] || [ ! -x "$REF" ]; then
    echo "usage: $0 REFERENCE_PCREC [CURRENT_PCREC]" >&2
    echo "  REFERENCE_PCREC must be an executable pcrec build to compare against." >&2
    exit 2
fi
if [ ! -x "$CUR" ]; then echo "no current pcrec at $CUR" >&2; exit 2; fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "object-neutrality: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

# The population is every `pattern` line in every .rxt under tests/, so it
# grows with the corpus rather than with this script — run_vm_identity.sh's
# formulation, and for its reason.
#
# [K35, fixed at the [DD-14] close 2026-08-25] `LC_ALL=C` ON THE `sort -u`,
# AND IT IS NOT A FORMATTING PREFERENCE. Under the ambient `en_US.UTF-8`
# collation punctuation is IGNORABLE, so `a{0,0}b` and `(a){0,0}b` compare
# EQUAL and `-u` drops one — and the survivor is the spelling WITHOUT the
# punctuation, i.e. the STRUCTURED half of every collision is what gets lost.
# MEASURED on this tree, this exact pipeline, 2026-08-25:
#     ambient (en_US.UTF-8): 1,798 patterns
#     LC_ALL=C:              2,772 patterns   (+974, 35% of the corpus)
# Every neutrality verdict this script printed before the fix was stated over
# 65% of the corpus with nothing saying so. The count is printed below so a
# future shrink announces itself instead of being invisible.
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats.all"

# THE DERIVED POPULATION, STATED AND FLOORED (K35's remedy: a check whose
# population comes from a pipeline nobody counts cannot report that the
# pipeline lost a third of it). 2,772 on this tree, 2026-08-25; the floor is
# ~95% of that, low enough that ordinary corpus churn does not fire it.
# IF THIS GOES RED, READ IT AS "the population moved" AND FIND OUT WHY before
# re-pinning: a corpus that genuinely shrank is a deliberate re-pin, an
# extraction that silently lost patterns is the bug this floor exists for.
npat_all="$(wc -l < "$WORKDIR/pats.all")"
if [ "$npat_all" -lt 2630 ]; then
    echo "FAIL: object-neutrality: corpus extraction found only $npat_all patterns, below the 2630 floor (~95% of the 2772 this tree measures). K35: an unguarded \`sort -u\` collates punctuation as ignorable and silently drops a third of the corpus (measured here: 1,798 ambient vs 2,772 under LC_ALL=C). Either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again" >&2
    exit 1
fi
if [ "$NEUT_N" != "0" ]; then
    # STRATIFIED, not the first N. A bounded run must still span the SHAPE
    # space, and the corpus is sorted, so `head` samples one alphabetical
    # corner of it. Measured the hard way during [M6-READ]: NEUT_N=60 with
    # `head` reported 41 of 41 clean while the emitter was producing
    # revdet-rung artifacts that did not COMPILE -- the head of the corpus
    # contains no such pattern, and it took a different suite to notice.
    # Every k-th line covers the same count across the whole file.
    total=$(wc -l < "$WORKDIR/pats.all")
    awk -v want="$NEUT_N" -v tot="$total" \
        'BEGIN { step = (tot > want && want > 0) ? tot / want : 1 }
         { if (int((NR - 1) / step) != int(NR / step) || step <= 1) print }' \
        "$WORKDIR/pats.all" | head -n "$NEUT_N" > "$WORKDIR/pats"
else
    cp "$WORKDIR/pats.all" "$WORKDIR/pats"
fi
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -eq 0 ]; then
    echo "FAIL: object-neutrality: no patterns found under $ROOT_DIR/tests — the sweep would be vacuous" >&2
    exit 1
fi

same=0; textdiff=0; symdiff=0; renamed=0; skipped=0; refused=0
: > "$WORKDIR/failures"

emit_and_build() {   # $1=pcrec  $2=outdir  $3=pattern ; same BASENAME both sides
    mkdir -p "$2"
    "$1" -p rx -o "$2/gen.c" -- "$3" >/dev/null 2>&1 || return 1
    $CC $NEUT_CFLAGS -c "$2/gen.c" -o "$2/gen.o" >/dev/null 2>&1 || return 2
    # An artifact with no constant tables has no .rodata at all; objdump says
    # so on stderr. That is a legitimate shape, not a failure — but it must be
    # SYMMETRIC, so the section list is recorded and compared too, and a
    # .rodata that appears on one side only shows up as a byte difference.
    { objdump -h "$2/gen.o" | awk '{print $2}' | grep -E '^\.' | LC_ALL=C sort
      objdump -s -j .text   "$2/gen.o" 2>/dev/null
      objdump -s -j .rodata "$2/gen.o" 2>/dev/null; } \
        | grep -v 'file format' > "$2/bytes"
    nm --defined-only -g "$2/gen.o" 2>/dev/null | awk '{print $2, $3}' | LC_ALL=C sort > "$2/gsyms"
    nm "$2/gen.o" 2>/dev/null | awk '{print $NF}' | LC_ALL=C sort > "$2/allsyms"
    return 0
}

i=0
while IFS= read -r pat; do
    i=$((i + 1))
    d="$WORKDIR/c$i"
    emit_and_build "$REF" "$d/ref" "$pat"; rrc=$?
    emit_and_build "$CUR" "$d/cur" "$pat"; crc=$?

    # A pattern both builds REFUSE is not a neutrality result either way; a
    # pattern only ONE refuses is a real difference and must be loud.
    if [ $rrc -eq 1 ] && [ $crc -eq 1 ]; then refused=$((refused + 1)); rm -rf "$d"; continue; fi
    if [ $rrc -eq 1 ] || [ $crc -eq 1 ]; then
        echo "REFUSAL MISMATCH: '$pat' (ref rc=$rrc, cur rc=$crc)" >> "$WORKDIR/failures"
        textdiff=$((textdiff + 1)); rm -rf "$d"; continue
    fi
    if [ $rrc -ne 0 ] || [ $crc -ne 0 ]; then skipped=$((skipped + 1)); rm -rf "$d"; continue; fi

    if ! diff -q "$d/ref/gsyms" "$d/cur/gsyms" >/dev/null 2>&1; then
        echo "EXPORTED SYMBOLS DIFFER (ABI BREAK): '$pat'" >> "$WORKDIR/failures"
        diff "$d/ref/gsyms" "$d/cur/gsyms" | head -6 >> "$WORKDIR/failures"
        symdiff=$((symdiff + 1)); rm -rf "$d"; continue
    fi
    if ! diff -q "$d/ref/bytes" "$d/cur/bytes" >/dev/null 2>&1; then
        echo "EXECUTED CODE DIFFERS: '$pat'" >> "$WORKDIR/failures"
        diff "$d/ref/bytes" "$d/cur/bytes" | head -8 >> "$WORKDIR/failures"
        textdiff=$((textdiff + 1)); rm -rf "$d"; continue
    fi
    same=$((same + 1))
    if ! diff -q "$d/ref/allsyms" "$d/cur/allsyms" >/dev/null 2>&1; then
        renamed=$((renamed + 1))
    fi
    rm -rf "$d"
done < "$WORKDIR/pats"

echo "== [M6-READ] object-code neutrality =="
echo "reference : $REF"
echo "current   : $CUR"
echo "flags     : $CC $NEUT_CFLAGS"
echo "population: $npat_all distinct corpus patterns extracted (floor 2630; LC_ALL=C, K35)"
echo "patterns  : $npat swept ($refused refused by both, $skipped uncompilable)"
echo "(a) .text + .rodata byte-identical : $same"
echo "(c) exported symbols identical     : $((same + textdiff)) of $((same + textdiff + symdiff))"
echo "(b) INFO — artifacts whose INTERNAL symbol names changed: $renamed"
echo "    (expected non-zero after a rename; not executed code, does not survive strip)"

if [ "$symdiff" -ne 0 ] || [ "$textdiff" -ne 0 ]; then
    echo
    echo "FAILURES ($((symdiff + textdiff))):" >&2
    head -60 "$WORKDIR/failures" >&2
    echo "FAIL: object-neutrality: $textdiff executed-code difference(s), $symdiff exported-symbol difference(s)" >&2
    exit 1
fi
if [ "$same" -eq 0 ]; then
    echo "FAIL: object-neutrality: nothing was compared — the sweep is vacuous" >&2
    exit 1
fi
echo "PASS: object-neutrality: $same artifact(s) identical in executed code and exported symbols"
exit 0
