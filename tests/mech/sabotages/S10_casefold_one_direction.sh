# S10 — cls_casefold only folds one direction (upper -> lower is dropped),
# so a class containing only the uppercase letter does not gain the
# lowercase one (OS-1 section of tests/codegen/CLAUDE.md table, row 3).
# Documented result: 1 codegen check + 8 caseless.rxt cases.
# [M5.0 stage 4, lane utf8s4] RE-ANCHORED. Stage 4 made `cls_casefold` take the
# fold as a PARAMETER (the relation is the ENCODING's now, `PcrecEnc.fold`) and
# put the produced sets' union between the fold and the negation, so this row's
# recorded anchor no longer exists. The CLAIM is unchanged and was re-verified
# against the live source, not carried over: the fold is SYMMETRIC — folding only one direction leaves a set that is not
# case-closed. The loop moved from `cls_casefold` into `ascii_partners`
# (src/core/fold.c) when the fold became a `PcrecFold` object; it is the same
# loop over the same table and the same `c >= 'a'` narrowing.
SAB_ID="S10-casefold-one-direction"
SAB_FILE="src/core/fold.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="cls_casefold: 'cls_has(b,c) || cls_has(b,c+32)' -> 'cls_has(b,c+32)' (fold one direction only)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 codegen check + 8 caseless.rxt cases"
SAB_COUNT=1
# RE-ANCHORED 2026-08-22 ([M6.5.2]): `cls_casefold` no longer runs its own
# `'A'..'Z'` loop testing BOTH cases -- it walks all 256 bytes and sets each
# set byte's PARTNER from `pcrec_ascii_fold` (src/core/fold.c), because the
# fold now needs to exist as an OBJECT a test can read (a caseless
# backreference compare cannot fold at parse time, so the fold is spelled a
# second time in the encoding residual and the two are tied by
# tests/backrefs/fold_agreement_check.c). The rewrite is behaviour-preserving
# by construction: the table's only non-identity entries are the 52 ASCII
# letters, each mapping to its partner.
#
# INTENT UNCHANGED, and re-expressed against the new shape: fold in ONE
# direction only. Setting `c` from `fold[c]` instead of `fold[c]` from `c`
# widens `[A]` to nothing and `[a]` to nothing, so a caseless class stops
# being case-closed -- the same asymmetry the old anchor produced by dropping
# one arm of its `||`.
# [M5.0 stage 1] RE-AIMED at the interval payload. `cls_casefold` collects the
# partners over the 256 BYTES before adding any (the loop must not read the set
# it is mutating), so the row's edit lands on the collection's own condition
# rather than on a bit-set call. The asymmetry it plants is identical: only the
# lowercase half of the partition acquires its partner.
SAB_BEFORE="        if (pcrec_ascii_fold[c] != c && pcrec_cpset_has(in, c))
            pcrec_cpset_add(out, pcrec_ascii_fold[c], pcrec_ascii_fold[c]);"
SAB_AFTER="        if (pcrec_ascii_fold[c] != c && pcrec_cpset_has(in, c) && c >= 'a')
            pcrec_cpset_add(out, pcrec_ascii_fold[c], pcrec_ascii_fold[c]);  /* SABOTAGE S10 */"
