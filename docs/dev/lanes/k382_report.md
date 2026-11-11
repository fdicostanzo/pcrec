# k382 — R-38 K38-2, THE SEAM EVENT (Parts A and B together)

Lane k382 (opus), branch `lane/memfn-k382` (cut from lane/memfn-k382a @ 37a6b36ed). Design of
record: `docs/design/memfn/span_runs_sheet.md` rev 1.3 (§2-§5, §5.1, §6). Owner's go (2026-11-11):
"K38-2. let's finish it now." Sabotage ids taken: S3040-S3069 (top of the free range; main's
highest S3035 at the cut).

STATE: in progress (WIP; this file is rewritten at hand-back)

## Summary

(in progress)

## EMIT-3 first

Commit b8c27d40c (its own commit, before any seam change): the window family's IN-RUN sites.

## Seam event (Parts A and B)

(in progress) WORKING PLAN, in order:
1. memfn.h: MF_SITE_ABI 27, MF_CLASS_V 9, `mf_run_reply` (= mf_class.run's type, U1),
   `head_max` int64_t, run pspan in set form (nalt 1, nterm 0, verify NO, start 0, core all),
   derived run part (FUNC, nalt 0, nterm 0, need 0), `mf_pres_picks` run pair retired,
   MF_PRES_WINDOW kit-internal, `pres-window` lever retired.
2. kit: the run recognizer; kit_run_decide's mode table (WHOLE / WINDOW / EXACT-AROUND) with the
   route as input (U3); cls.run from mf_ask/mf_defined; twin at max(K,0) on the reply's extent;
   the derived part (one RUN term at offset ver_lo, candidate = run position 0, floor
   max(0, lo + omin)); pres_layout_check's run half -> statement rule; refusals moved.
3. pcrec: req_pres_spans set form; Job keeps the define's cls.run; req_run_member and the cut
   retire; readers (§4.1-§4.3); REQ_RUN `@` first-match table; K = whole_maxoff; run pin whole
   clipped; listing rows; spec hunks (§4.4); abi bump (readers by grep).
4. G2 presence family: negative omin, signed K, FAM-2 (ver off the reply), ORC-3.
5. sabotage fates; checks; gate jobs 600-609.

## abi package

## PLAN items (c)-(e) and K7 U1/U3

## Movers (5.1 populations)

## Sabotage fates

## Checks

## Gate jobs

## Charter-vs-committed checklist

OWED: (in progress)
