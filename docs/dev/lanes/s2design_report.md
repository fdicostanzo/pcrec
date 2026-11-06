# s2design — span_pick stage 2, the design (lane report)

Lane `s2design`, branch `lane/memfn-s2design` (cut from the kit branch `lane/memfn-k1102` at c03c2d711),
2026-11-06. DESIGN ONLY: no C, no make, no timing, no box job. Deliverable:
`docs/design/memfn/span_cards.md` rev 0 (the stage-2 design of record) and its line in
`docs/design/memfn/CLAUDE.md`. Request: R-35 item 1 (`memfn/docs/requests.md:805`); Frank's GO 2026-11-06.

## Summary (what a fresh agent resumes from)

1. **Cards**: a new method version `kit-grid@3` (`kit-grid@2` is grid2's slot method, `r17b_prime.md:2040`,
   never written; not reused). Four quantities: `find_byte` (method; the UNIT row is `kit.find_byte.walk`,
   so byte(walk) is the unit), `find_hit` (method;landing;split), `verify_cmp` (form;cls;pass), `enter`
   (kind;entry). Grid1's ten quantities are not re-measured (no reader). SIMD forms (vrun-w16/w32,
   vany2/3-w16/w32) are METHOD TOKENS of find_byte/find_hit, reader Frank's C9 row; row 1's SIMD-on arm
   is checked to need none (MEMFN_FORMS `none` on its sites). memchr-back DEFERRED (no reader, D77).
2. **Producer**: `memfn/measure/` (kit-owned, never built by make), cell texts through G2's window-site
   builder (one builder), one driver, quiet-gated `idle-ok` boxqueue jobs in 650's shape, CPU 7 / sibling
   15, >= 50 ms calibrated loops, 7 rounds, 5 launches + 2 by the cross-launch rule, A/A by separate
   compiles; FULL/PARTIAL/REFUSED per measure_sets §7.3; per-launch medians KEPT as
   `measure_store/zen4-grid3/1/raw.tsv` (committed, not embedded); one window, J1-J6, ~32 min timed,
   ~45 with quiet waits. [PAIR-LOOKAHEAD-TIME] is J1, first: 128 MEASURED, or a later D186 unit change
   with the PAIR cards waiting for it.
3. **Noise channel**: `mf_measure` gains `noise_state` (UNSTATED refused) + `noise_e6`, appended last,
   MF_SITE_ABI 23 -> 24; the three positional constructors must state it; noise is handed ONLY from a set
   whose digest covers it. Derived noise: a STORED, RECOMPUTED field with a per-derivation quadrature rule
   (a new column in `measures.md` §3.2), interp-log2's UNMEASURED.
4. **Digest**: set FORMAT 2 with domain `pcrec-meas-2` covering noise; format 1 unchanged, so zen4-grid1@1
   (digest 13a6536315af1520, sha, DEFAULTS.log row 1) stays byte for byte.
5. **Coverage factor**: z = 2 (`COVER_Z_E3 2000`), UNMEASURED DEFAULT, in plan_cost.def's MARGIN family,
   written with its reader at row 1.
6. **Step-0 gate**: manager's reading CONFIRMED (D176 Q3 = SRS §7 step 0); the trigger is already met by
   smp20, so it cannot stop stage 2; it runs first because it scopes the card grid, and re-runs after the
   cards as row 1's forecast.
7. **Moves**: no emitted byte, no pcrec abi (95), no stamp; MF_SITE_ABI 24, format 2, a new built-in set,
   card rows, form-hash ids. DEFAULTS: recommend the literal D166 add. 2 reading (flip at S2e, an empty
   census), main's call.
8. **Build plan**: S2a noise+format 2, S2b census, S2c producer, S2d the window (main clears it with
   Frank), S2e the set, S2f the forecast; 14 sabotage rows listed, ids the manager's.

## Findings (facts the design rests on, cited)

- F1 `kit-grid@2` names grid2's run (`r17b_prime.md:2040`, :2059); the card file says ver 2 is "NOT written
  here" (`memfn/data/cards/kit-grid.tsv` header).
- F2 Committing a set changes the default under D166 add. 2 ("a bare compile reads the LATEST set" until
  M2) and `measures.md` §5¶6, against R-35's "leaves DEFAULTS unchanged" (span_cards §8.3).
- F3 `mf_measure` has three positional constructors: `cli/main.c:160`, `src/gen/memfn_sites.c:89`,
  `tests/memfn/arm_fixtures.c:1562`; kit readers `compose.c:895`, `finder.c:442-446`.
- F4 The loader refuses any `format` but 1 (`src/core/ks_measures.c:305`); `noise_e6` is a text column
  today, `value_e6` the only parsed number (`ks_measures.h:55,72`); the digest role is
  `ks_measures.c:244-246`.
- F5 Only `measure_store/*/*/set.tsv` is embedded (Makefile `MEAS_STORE_SRCS`), so a sibling `raw.tsv` is not.
- F6 Form-hash ids today: `walk`, `libc` only (`memfn/src/formhash.c:240`).
- F7 `PAIR_LOOKAHEAD` = 128 is instruction-chosen, its time UNMEASURED (`memfn/src/ofsskip.c:267-278`); R-30
  is landed (abi 95, `src/gen/emit_dfa.c:55`).
- F8 R-33's sweep (job 240) ran 5,492 compiles in 14 s (`worktrees/.boxqueue/queue.log`), so the census is
  cheap.
- F9 The SRS is `docs/design/memfn/stop_ranking_study.md` on unmerged `lane/memfn-stopstudy` fc6735cdf
  (`pricesurvey_report.md:5-7`); its §7 step 0 and §8 item 2 are quoted in span_cards §7.
- F10 match_api's measures sentences (§6¶14a, §6.3.10¶12-¶13) do not move in stage 2.

## For main

1. memchr-back deferred (span_cards §2.5, §10.1).
2. DEFAULTS reading (B) recommended (§8.3).
3. The bundle sampling-noise seam field deferred to its producer; amends span_pick.md:237-238 (§4.6).
4. No match_api hunk (§4.4).
5. S2a and S2e carry pcrec-side hunks (`src/core/ks_measures.{c,h}`, `src/gen/memfn_sites.c`, `cli/main.c`,
   `src/dump/measures_dump.c`, `docs/spec/measures.md`, `tests/knowledge/`, `measure_store/`) for main's
   review in the kit's same-commit package, as R-35 (a) rules for unit 3.0.
6. S2d needs one timing window (~45 min) cleared with Frank; S2b and S2f are compile-only boxqueue jobs.
7. Stage 2 landing fires [BENCH-WITHDATA]'s trigger (plan.md:1720).

## Charter vs committed

| brief item | committed where | state |
|---|---|---|
| read BOILERPLATE, memfn/CLAUDE.md, the listed docs | — | done |
| 1 the cards: every column, the four quantities, SIMD forms per layer, method version and §5.4 relation, a reader per card | span_cards §2.1-§2.6 | done |
| 2 the producer: fixtures, driver, home, job shape (quiet gate, pin, >= 50 ms, rounds, A/A), raw cells kept, assembly to measure_store, gates, box time, the PAIR sweep and what it decides | §3.1-§3.8 | done |
| 3 the noise channel: fields, MF_SITE_ABI 23->24, pcrec fill, compose.c check, spec hunks, readers by grep, derived noise by quadrature | §4.1-§4.5 (bundle noise §4.6 deferred, For main) | done |
| 4 noise in values_digest: the version event, grid1's digest, DEFAULTS and stamps, readers by grep, proof nothing emitted moves | §5 | done |
| 5 the coverage factor: home, value, derivation | §6 | done |
| 6 the step-0 gate: confirm/refute with cites, who runs it, what it shows, whether landing waits | §7 | done (CONFIRMED, refined) |
| 7 what stage 2 moves, every number and its package | §8 | done |
| 8 build plan as units with witnesses, heavy runs, windows, sabotage rows | §9 | done (ids for the manager) |
| 9 open questions for Frank with recommendations | §10 | done (none for Frank; four for main) |
| CLAUDE.md line | docs/design/memfn/CLAUDE.md | done |
| lane report with this checklist | this file | done |
| no C, no make, no timing, no box jobs | — | held |

## STATE AT HANDOFF

STATE: delivered. OWED: none of the design. No make, no timing, no box job run. Not a build go.
