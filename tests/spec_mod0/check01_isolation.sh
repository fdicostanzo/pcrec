#!/bin/bash
# check01_isolation.sh — INVARIANT 1: enabled-set isolation, mechanical.
#
# THE PROMISE. "Recognisers and extent scans live in translation units that do
# not link the enabled-set symbol; checked by `nm` in the build. Oracle: the
# linker. Sabotage: add one reference."
#
# WHY THIS CHECK IS `nm` AND NOT A GREP. A grep over src/ finds the TEXT of a
# reference and is defeated by a macro, a typedef, an inline function in a
# header, or a call through a pointer. `nm` reads what the COMPILER actually
# emitted: if a translation unit needs the enabled-set symbol at link time, the
# symbol is in that object's undefined list, and no amount of spelling hides
# it. That is what "oracle: the linker" means, and it is why this check reads
# build/ rather than source. (This author is a D27 spec-first writer and is
# denied src/ regardless — but the mechanical check would be the right one even
# with access.)
#
# WHAT IS ASSERTED, once the surface exists:
#   for every object file that DEFINES a recogniser or an extent scan,
#   the enabled-set symbol does not appear in that object's UNDEFINED list.
#
# HOW BOTH SIDES ARE DISCOVERED, rather than hand-listed. A hand-written list
# of "the recogniser TUs" goes stale the first time a file is added, and a
# stale list passes. So both are found by convention from the symbol table:
#   the enabled-set symbol   — a DEFINED symbol whose name matches the
#                              enabled-set naming below;
#   the recogniser TUs       — objects defining a symbol whose name matches the
#                              recogniser/extent-scan naming below.
# If either discovery finds nothing, the check FAILS as a missing surface. A
# check that quietly passes because it found no recognisers to check is the
# vacuity this suite exists to prevent.
#
# APERTURE, STD1c re-arm (docs/dev/std1_check_rearm.md, 2026-08-13). D37's
# frozen named sets (`std1`) and the bare-default mapping point added new
# process-wide enabled-set machinery: `nm` over the merged build showed
# PCREC_DEFAULT_FEATURES was NOT caught by the pre-STD1c ENABLED_RE (it has
# no "enabled" substring — the naming convention it follows is
# "PCREC_DEFAULT_FEATURES", not "*_enabled_*"). Widened below. Both discovery
# populations (the symbol count, the TU count) are now floored in floors.txt
# — a ratchet against the aperture silently narrowing again, since an empty
# discovery reads identically to a real pass otherwise (the same vacuity this
# check already guards structurally, made numeric).
#
# SABOTAGE: add one reference to the enabled-set symbol from any recogniser TU
# and rebuild — that object gains the symbol in its undefined list and this
# check names the object and the symbol. That is the whole test, and it is
# exactly the sabotage the invariant names. (Validated 2026-08-13 against
# PCREC_DEFAULT_FEATURES specifically, in a scratch reference planted in
# scans.c — see the STD1c re-arm report for the exact command and failing
# output.) A SECOND sabotage, added at STD1c: narrow ENABLED_RE to match none
# of the real symbols — the vacuity guard below must still fire
# (SURFACE MISSING / exit 3), proving the widening did not also weaken the
# empty-discovery guard it sits next to.
#
# Run: check01_isolation.sh <repo-root> <floors.txt>

set -u
ROOT="${1:?usage: check01_isolation.sh <repo-root> <floors.txt>}"
FLOORS="${2:?usage: check01_isolation.sh <repo-root> <floors.txt>}"
NAME=check01_isolation
echo "== $NAME =="

ARCHIVE="$ROOT/build/libpcrec.a"
OBJDIR="$ROOT/build/obj"

if [ ! -f "$ARCHIVE" ]; then
    echo "FAIL[$NAME]: no $ARCHIVE — the build tree is the oracle here, and"
    echo "  this check cannot run without it. (It does not build: the main"
    echo "  session owns the build tree.)"
    exit 2
fi
if [ ! -f "$FLOORS" ]; then
    echo "FAIL[$NAME]: no floors file at $FLOORS"
    exit 2
fi
if ! command -v nm >/dev/null 2>&1; then
    echo "FAIL[$NAME]: nm not found; the linker is this check's oracle"
    exit 2
fi

# Naming conventions, in one place. Widened deliberately: a false positive here
# costs a look, a false negative costs the whole check.
#
# ENABLED_RE gained `PCREC_DEFAULT_FEATURES` at STD1c (2026-08-13): D37's
# bare-default mapping point does not carry an "enabled"/"gate" substring, so
# the pre-STD1c pattern below did not catch it even though it is exactly the
# kind of process-wide enabled-set state this check exists to isolate
# recognisers from. Named explicitly rather than folded into a broader
# "default" pattern, because a broad "default" match also catches
# `pcrec_default_options` (core/compile.c, an unrelated options struct) and
# `pcrec_recognise_tail_default` (registry.c, a recogniser — matching it
# here would be exactly backwards).
ENABLED_RE='enabled_set|enabled_features|feature_enabled|pcrec_enabled|g_enabled|PCREC_DEFAULT_FEATURES'
RECOG_RE='recognis|recogniz|extent_scan|scan_extent|_extent$'

echo "  archive: $ARCHIVE"
echo "  looking for an enabled-set symbol matching: $ENABLED_RE"
echo "  looking for recogniser/extent TUs matching:  $RECOG_RE"

# --- discover the enabled-set symbol ------------------------------------
ENABLED_SYMS=$(nm --defined-only "$ARCHIVE" 2>/dev/null \
               | awk '{print $NF}' | grep -E "$ENABLED_RE" | sort -u)

# --- discover the recogniser TUs ----------------------------------------
RECOG_OBJS=""
for o in $(find "$OBJDIR" -name '*.o' 2>/dev/null | sort); do
    if nm --defined-only "$o" 2>/dev/null | awk '{print $NF}' \
         | grep -qE "$RECOG_RE"; then
        RECOG_OBJS="$RECOG_OBJS $o"
    fi
done

NOBJ=$(find "$OBJDIR" -name '*.o' 2>/dev/null | wc -l)
NSYM=$(echo "$ENABLED_SYMS" | grep -c .)
NREC=$(echo $RECOG_OBJS | wc -w)
echo "  POPULATION isolation.objects_scanned          $NOBJ"
echo "  POPULATION isolation.enabled_symbols          $NSYM"
echo "  POPULATION isolation.recogniser_tus           $NREC"

MISSING=0
if [ -z "$ENABLED_SYMS" ]; then
    echo
    echo "  SURFACE MISSING: an enabled-set symbol in the built library"
    echo "  consumed how:    this check reads \`nm --defined-only\` over"
    echo "                   $ARCHIVE and needs at least one symbol naming"
    echo "                   the enabled feature set (matching $ENABLED_RE,"
    echo "                   or widen that pattern when the real name is"
    echo "                   chosen). It then asserts that symbol is absent"
    echo "                   from the UNDEFINED list of every recogniser/"
    echo "                   extent-scan object."
    MISSING=1
else
    echo "  enabled-set symbol(s) found:"
    echo "$ENABLED_SYMS" | sed 's/^/    /'
fi

if [ "$NREC" -eq 0 ]; then
    echo
    echo "  SURFACE MISSING: any recogniser or extent-scan translation unit"
    echo "  consumed how:    this check looks for objects under $OBJDIR that"
    echo "                   DEFINE a symbol matching $RECOG_RE. Nothing"
    echo "                   matches today, so there is no population to"
    echo "                   isolate and a 'pass' would mean nothing."
    MISSING=1
else
    echo "  recogniser/extent TUs:"
    for o in $RECOG_OBJS; do echo "    $o"; done
fi

if [ "$MISSING" -eq 1 ]; then
    echo "  ORACLE SIDE OK — nm works and the archive was read; the pcrec-side"
    echo "  symbols are what do not exist yet."
    echo "AWAITING-SURFACE $NAME"
    exit 3
fi

# --- floors: the two discovery populations, ratcheting minima ------------
POPFAIL=0
floor_of() {  # floor_of <bucket>  -> prints the pinned floor, or __MISSING__
    awk -v b="$1" '$1==b{print $2; found=1} END{if(!found) print "__MISSING__"}' "$FLOORS"
}
pop_floor_check() {  # pop_floor_check <bucket> <count>
    local b="$1" c="$2" f
    f=$(floor_of "$b")
    if [ "$f" = "__MISSING__" ]; then
        echo "  FAIL: no floor pinned for $b in $FLOORS (unpinned is unchecked)"
        POPFAIL=1
        return
    fi
    if [ "$c" -lt "$f" ]; then
        echo "  FAIL: $b is $c, below its floor of $f"
        POPFAIL=1
    fi
}
pop_floor_check isolation.enabled_symbols "$NSYM"
pop_floor_check isolation.recogniser_tus "$NREC"
if [ "$POPFAIL" -eq 1 ]; then
    echo "FAIL $NAME: a discovery population is unpinned or below its floor"
    exit 1
fi

# --- the assertion ------------------------------------------------------
FAILS=0
CHECKED=0
for o in $RECOG_OBJS; do
    UNDEF=$(nm --undefined-only "$o" 2>/dev/null | awk '{print $NF}')
    for s in $ENABLED_SYMS; do
        CHECKED=$((CHECKED + 1))
        if echo "$UNDEF" | grep -qx "$s"; then
            echo "  DISAGREE $o references the enabled-set symbol '$s' — a"
            echo "           recogniser must not link it (nm --undefined-only)"
            FAILS=$((FAILS + 1))
        fi
    done
done
echo "  POPULATION isolation.symbol_pairs_checked     $CHECKED"

if [ "$CHECKED" -eq 0 ]; then
    echo "  FAIL: zero pairs checked — the sweep compared nothing"
    exit 1
fi
if [ "$FAILS" -gt 0 ]; then
    echo "FAIL $NAME: $FAILS reference(s)"
    exit 1
fi
echo "PASS $NAME ($CHECKED symbol/TU pairs, $NSYM enabled-set symbols, $NREC recogniser TUs)"
exit 0
