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
# SABOTAGE: add one reference to the enabled-set symbol from any recogniser TU
# and rebuild — that object gains the symbol in its undefined list and this
# check names the object and the symbol. That is the whole test, and it is
# exactly the sabotage the invariant names.
#
# AWAITED SURFACE (measured 2026-08-11): build/libpcrec.a contains NO symbol
# matching the enabled-set naming — `nm` over the archive finds nothing for
# enabl/gate/feature/module. There is no enabled set yet, so there is nothing
# to be isolated FROM, and this check cannot pass or fail meaningfully until
# the first module lands. It reports that state and exits nonzero.
#
# Run: check01_isolation.sh <repo-root>

set -u
ROOT="${1:?usage: check01_isolation.sh <repo-root>}"
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
if ! command -v nm >/dev/null 2>&1; then
    echo "FAIL[$NAME]: nm not found; the linker is this check's oracle"
    exit 2
fi

# Naming conventions, in one place. Widened deliberately: a false positive here
# costs a look, a false negative costs the whole check.
ENABLED_RE='enabled_set|enabled_features|feature_enabled|pcrec_enabled|g_enabled'
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
NREC=$(echo $RECOG_OBJS | wc -w)
echo "  POPULATION isolation.objects_scanned          $NOBJ"
echo "  POPULATION isolation.recogniser_tus           $NREC"

MISSING=0
if [ -z "$ENABLED_SYMS" ]; then
    echo
    echo "  SURFACE MISSING: an enabled-set symbol in the built library"
    echo "  consumed how:    this check reads \`nm --defined-only\` over"
    echo "                   $ARCHIVE and needs exactly one symbol naming the"
    echo "                   enabled feature set (matching $ENABLED_RE, or"
    echo "                   widen that pattern when the real name is chosen)."
    echo "                   It then asserts that symbol is absent from the"
    echo "                   UNDEFINED list of every recogniser/extent-scan"
    echo "                   object."
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
echo "PASS $NAME ($CHECKED symbol/TU pairs, $NREC recogniser TUs)"
exit 0
