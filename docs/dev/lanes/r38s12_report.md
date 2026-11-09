# r38s12 report — span_runs_sheet rev 1.2 (doc only)

## Summary
`docs/design/memfn/span_runs_sheet.md` is now rev 1.2: the five ruled text fixes of review
2026-11-09 r7 r38s11, with a "rev 1.2" revision-log table (item -> section). Text only: no code, no
build, no compile; cites checked against lane/u3mech. Nothing else changed.

## Item by item
1. F-B (§4.2, §5.1 item 4): `w` = walk offset of run position 0 = `ro - s0` in `pcrec_run_pin`
   (`ro` is searched per placement), so the clip is `l = min(e0 - s0, nwalk - ro)`; the clipped
   stretch must still contain the rate-picked `x`. Stated that `ofs_test_verifies_run`
   (emit_dfa.c:7487-7505) can still flip a clipped run `dominated` -> `emitted`; K38-2 counts it
   inside population 4, SUSPECTED by code read (not compiled).
2. F-I (§2.4 C1): precondition that the scan position is not position 4; the check asserts
   `has_scan` and `scan != 4` from the reply before counting the witness.
3. F-M (§4.3, §5.1 item 5): `req_handoff_k` stays (test becomes "row keeps the run", value
   `whole_maxoff` / `req_landmark_maxoff`, already `long long`). `emit_req_handoff_rest` comment
   loses its cut-window branch ("run"/"window"), other two spellings byte-identical; movers join
   the `-fcomments` population.
4. RQ-2 (§5 K38-1): "Ranking source (RQ-2)" line added; see below.
5. Cites: compose.c:1205 -> :1206 (`mf_class q;` is :1205, the memcmp :1206);
   reqcube_check.py:254-259 -> :254-255 (:256-259 is REQ_BYTE). Also added the new cite
   window.c:1509-1511 (the rank_pos[0] loud check).

## RQ-2 ranking source
Today `window.c:1478-1512` fills `rank_pos[]` by calling `kit_run_member` k times (each asked
again from the last), independent of P3's call in `run_decide`; vrun's KB reads `rank_pos[0]` as KA.
Options:
- A (RECOMMENDED): ranking comes from `run_decide`. One function holds the tie rule and the
  `run-tie-left` lever; scan, stretch, twin mass and ranking move together. C4 then measures one
  decision; the ranking is an extra reader the tie plant must move (counted per reader). Cost: the
  function needs a previous-answer argument, which `kit_run_member` already has.
- B: ranking stays a direct `kit_run_member` caller and the lever acts on both. Two lever sites;
  C4 and the caller check must cover a second path, and `decider_census` cannot see a reader left
  behind. Contradicts Goal 2 (one decision).
- C: ranking untouched, tie-blind to the lever. Under the lever, scan moves leftmost while
  `rank_pos[0]` stays rightmost, so the loud check at window.c:1509-1511 fires (`kit_fail`) on
  tie witnesses when the site is pinned: C4's reaching regime would die at compile instead of
  measuring.
The kit manager confirms or changes this before K38-1's brief.

## Charter-vs-committed checklist
- F-B, F-I, F-M, RQ-2, cites: applied (above). Revision-log "rev 1.2" entry: added.
- Not applied: nothing. Not done by design: no further review round (ruled); build/make not run.
- Deferred to K38-2 and unchanged: `.whole` column and `keep` fates "from the code".
