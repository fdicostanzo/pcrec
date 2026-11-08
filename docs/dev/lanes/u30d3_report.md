# u30d3 — span_pick unit 3.0 design, rev 2.1 (the Q13 ruling applied)

STATE: delivered. Lane u30d3 (sonnet), 2026-11-07, branch lane/memfn-u30d (from tip 9d690a58b). Design text
only: no code, no make, no box job. OWED: none.

## Summary

`docs/design/memfn/plan_frame.md` goes from rev 2 to REV 2.1 by ONE binding ruling: the last section of
`docs/dev/reviews/2026-11-07-r12-memfn-planframe1.md`, "Ruling on rev 2's Q13". F13 is a label, not a rung
list. Changed text is marked `[rev2.1 Q13]`; a 3-line table R2.1 sits above R2.

## What was removed

`nrung`, `rung[]`, `mf_wrung`, `mf_wcheck`, `MF_WRUNG_MAX`, the `fs` argument of `mf_wdecide` (signature now
`mf_wdecide(art, site, def, call, out)`) and every `fs` sentence (§0 rows 1-3, §2.1, §2.2 incl. the
round-trip projection, ASK-1, ASK-2, ASK-4, the phase-1 table), the `rung[]` column of §2.3's "who decides"
table, Goal 2/3/5 clauses, §2.7's "3.0b names vrun's triple" paragraph, the memfn.h history entry, §3, §4.1,
§4.2, §5's G2 rung population and counting sink, the rung-list overlap in the concurrency paragraph, §6's
per-RUNG comparison sentence, Q4/Q5/Q8 fragments. Sabotage rows W and AE are deleted (letters not reused);
3.0b now has 17 rows (was 19), the note 29 (was 31), kit ids S2994-S3010. F34's sink counter is gone.
Grep for `nrung|rung[|mf_wrung|mf_wcheck|MF_WRUNG_MAX|\bfs\b|counting sink|per rung|(AE)|(W)` over the note
now hits only the lines that DESCRIBE the removal (R2.1, R2's F13 and F34 rows, §2.7's replacement paragraph,
Q13's answer, the RUNG-LIST plan row). Judgment call: the three fact columns on `fn_rows` PREFIX existed
only to feed `rung[]`; I removed them from 3.0a too (D77) and named them in the plan row. The BODY column
stays (fused `search` reads it). If the manager wants them kept in 3.0a, restore one sentence in §4.1 and §2.7.

## Ids re-checked after the removal

Every other F-row naming `fs` or a rung was re-read; each still holds: F12 (`plan_test`; unrelated to the
sink), F14 (`fused`/`search` cross facts; B-fn and E-func fused rows now say their PREFIX rungs run too but are
unreported), F15 (comparisons; the SIMD-on cell is simply not compared before RUNG-LIST), F16 (round-trip
projection loses only the `fs` item; the same-class fixture is unchanged), F26 (arena; unaffected), F27 (cites;
the vrun trim-empty case is §2.7 text that stays), F29 (agreement uses the stored record; lost only "the
rendered rungs"), F30 (G2 cells; the top-level MASK 0 assertion now reads "MASK at no level"), F31 (exact
emptiness; `nrung == 0` dropped), F32 (whole-reply `memcmp`; unchanged), F33 (mf_wcall fixtures; unaffected,
ASK-2 NULL `def` only), F34 (six callbacks stay, sink counter gone). 3.0b's size stays L (about 14 readers,
two checks, harness growth, D27 author); no cite was re-derived.

## Stated gap and plan row

§2.3 "The stated gap" says in plain words: `search`, `stream`, the check and `fused` describe the OFF (scalar)
variant; under `-fmemfn-simd` the artifact may run vrun's (VECTOR, MASK, TRIM) while the reply names the OFF
triple. F13's doc text (§6's FIXED columns name layer and target) is kept. The note had no plan-rows section,
so §7 gained "Plan rows proposed" with RUNG-LIST, trigger "row 1 compares a SIMD-on cell, or the first MASK
producer lands". Q13 in §7 is ANSWERED in one line pointing at the ruling.

## Charter-vs-committed checklist

1. rung list and `fs` removed, grep shown (above): done. 2. F13 doc text kept, gap in §2.3: done.
3. PLAN row proposal: done (new subsection). 4. Q13 ANSWERED, R2 F13 and F34 rows, size: done.
5. other F-ids re-read: done (above). R2.1 table at top: done. Marker `[rev2.1 Q13]`: done. History line,
design/memfn CLAUDE.md line: done.
