# pdrev3 — part_d.md rev 3 (the kit's design for R-38 Part D, re-check review r2 memfn-partd2 as ruled)

Lane pdrev3 (opus), 2026-11-12. Branch `lane/memfn-pdesign` (worktree `worktrees/pdesign`), base
`35bee4da9`. Deliverable: `docs/design/memfn/part_d.md` rev 3 (commit `f923a13fc`) plus its pointer
line in `docs/design/memfn/CLAUDE.md`. DESIGN ONLY: no code under `memfn/src` or `src/`. Cites
re-read at main `a8ae73be0` (later than `a9fc6dbd8`). `git diff --stat 35bee4da9 a8ae73be0` is empty
over `memfn/`, `src/gen/`, `tests/memfn/`, `memfn/tests/`, `tests/mech/`, `docs/spec/`,
`scripts/emit_sweep.py`, the census instruments and the readiness memo, so the code cites by
function name hold at main. `span_runs_sheet.md` moved only in §5's K38-3 row.

## STATE AT HANDOFF

- STATE: done. Rev 3 and the CLAUDE.md line are committed, and so is this report.
- OWED: none. I ran no suite and queued no job. What this lane measured (single compiles only, with
  the worktree's `build/pcrec` from one `nice make -j8`, rc 0):
  (1) today's `_REQ_WHY`/`_REQ_HANDOFF`/`_REQ_RUN` for the witnesses, by default and under
  `--memfn=no-window-search`: `[a-z]{8}.q`, `\d{3}-\d{4}` and `x.(?:cat|dog)` came back `dominated`
  on both routes; `(a|bc)[a-z]{8}.q` came back `emitted`/`11`; `(a|bc)\d{3}-\d{4}` came back
  `emitted`/`5`; `\d[aA]\d` and `(a|bc)\d[aA]\d` came back `none` (no necessary byte);
  `xy/users\d+` came back `78792f7573657273@0`; F4's pattern (`--features all`) came back `vm`,
  `emitted`;
  (2) I checked python3 `re` answers for each witness: (0,50), (3,53), (0,5), (4,14), (1,4), (1,6),
  (3,15).
- No rulings file was named. I applied the review's Rulings section through its last entry ("P8
  RULED ... kit + main jointly"), together with the [RUN-POS-SET] note on main (P14's re-scope, P1
  and P8 in the stage-3 brief).

## Summary

Rev 3 applies every FIX-NOW (P1-P19, P22, P23) and DOC (P20, P21) finding, and marks P24 as NOTED in
a §6 row. Each change is marked `[r2pd Pn]` (`P13a`-`P13e` for P13's parts). The five decisions:

- **P3**: a no-scan run (`SF_RUN_NOSCAN`) is run-less in P2. The set pick leads, `proof->run` is not
  required, and every span is `proven_by`. On REQUIRED routes P0 still comes first, so K66 is never
  dropped. Witness: `x.(?:cat|dog)` keeps `dominated` (today's value, MEASURED). Rev 2's rule would
  have emitted a doubled `memchr('x')` pre-check instead.
- **P9**: the scan-less body is now `fn-every-pos`, a name for what it does. It is the FIRST BODY
  row, and the three BODY rows' `holds` are disjoint facts (no scan / a cube scan / a one-byte scan),
  so where each row sits in the order cannot change the result. `ofs_fn_scan` writes -1s on
  `MF_NO_PRED`, and every caller is listed. The libc note becomes each body row's own. Its card is
  new: a formhash.c id `every-pos` plus a `kit-grid` card row at the next version, visibly
  UNMEASURED, and `CARD_FORMDEP_COUNT` +1. Witness: F4's pattern on a MATCHING subject, (0,50). A
  guard that only zeroed the scan would let `fn-pair` render a pair body on byte 0, which answers
  NOMATCH.
- **P15 + D3**: the record is `MFTRACE run_part_terms`, printed where the derived part's terms are
  handed to ofsskip; collect.py already keeps such lines. The census gains one parser for it. Before
  landing, the check is a per-site equality on the trace-build G2 presence family: the census's
  unspelled SET terms must equal G2's own count, which G2 takes from its generated sets and from C2's
  reading of the rendered text. Its `every-pos` count must also equal G2's count of scan-less runs.
  Both totals carry literal floors. The pcrec-artifact floor is armed at the joint landing. D3 is now
  READY.
- **P8**: `leads` and `rlead` are retired on runs with any non-cube position. That is a pcrec-side
  edit in S2's landing, and the successor controls are C2 and G2's decline equality (§9 item 5).
- **P14**: R by role now applies only to a window site's alternative. The run presence span is not R,
  and the span count in §2.2 is corrected (§2.2, §1, §4, §9 item 1).

## Per-finding changes

| id | disposition | change (part_d section) |
|---|---|---|
| P1 | FIX-NOW | §9 item 2: `req_site_define`'s head-part `gate_need` reads the TESTED run, like the head check; §5.1.1 D1: G2's layout head need by `trun` |
| P2 | FIX-NOW | §2.1: `fn-every-pos` comes FIRST, BODY `holds` are disjoint facts, `ofs_fn_scan` guard, every caller listed, the libc note per row, `ofs_fn_applies` under the scope; §2.4 witness row P2/P9; §5.1 plant p10; §5.2 floor "scan-less REQUIRED on a MATCHING subject" |
| P3 | FIX-NOW (decision) | §2.4 item 2 "P2 on a no-scan run", item 4's last bullet; F3 witness restated on pcrec's real proof; §9 item 5 |
| P4 | FIX-NOW | §9 item 5: the lead reader (`req_pres_head(lead=true)`, `req_set_leads_applies`) reads the tested run |
| P5 | FIX-NOW | §2.4 table: each witness's route is MEASURED; F2 and F7 move to prefixed shapes; the D27 author's caveat (§5.1) |
| P6 | FIX-NOW | §5.1.1 D1: G2's `!tested` branch is split (P2 vs decline), the decline is rendered and oracle-checked, `g_p2_untested` is P2-only; §5.1.1 D2 floors |
| P7 | FIX-NOW | §5.1.1 D1: `derive_run_part` relaxes to `!rr->ver_len`, so the scan-less reply refuses under the K-1 message |
| P8 | FIX-NOW (joint decision) | §9 item 5: `leads`/`rlead` retired on non-cube runs, pcrec-side in S2's landing; successors C2 and G2's decline equality; §2.4 item 4 |
| P9 | FIX-NOW (decision) | §2.1 name + reason; §5.3 its own UNMEASURED card; §0 G4; §5.1.1 D2; D3 counts `every-pos` |
| P10 | FIX-NOW | §5.1.1 D2: an `arm_fixtures` pair (all-wide REQUIRED run, `fn-every-pos`; control with one findable position, `fn-memchr`), `FIXTURE_FLOOR` +2 |
| P11 | FIX-NOW | §5.1 D2 cell + §5.1.1 D2 + §5.2: `run_of` moves with `g_run_shaped`; `two_runs` keeps the three-member fix for a second spelled verify-YES span; floor for wide-R alternatives with an exact member; §5.1.1 D0 base count split by verify |
| P12 | FIX-NOW | §5.1 D2 plant p9 → G2's two-sided pin (exactly 0); §5.1.1 D2; §6 C7 re-pins it |
| P13 | FIX-NOW | (a) §5.1.1 D1 `PRES_ROWS`, table-size check, `B3B_PRES`; (b) D2 `translate:run-rank`, `RUN_CALLERS`, `MEMBER_COUNT`, S3006; (c) D2 `ASSERT_ZERO` → `DIFFER_PINS` at landing; (d) D2 S1409's anchor, the uniqueness plant, the deny's carrier and S3009; (e) §4 reason 1: the order pin is finder_check |
| P14 | FIX-NOW | §2.2 ruling text scoped, count corrected (two multi-position verify-NO kinds), `mf_wspan.verify` text; §1 item 1; §4; §9 item 1 |
| P15 | FIX-NOW (decision) | §5.1 D3 row (record, population, floor, plants), §5.1.1 "D3, READY" (the witness), §8 item 2 |
| P16 | FIX-NOW | §4: `match_api.md` §6.3.7¶11, `tuning.md` §2.41¶1 and ¶7a, §2.28¶1, §2.29¶4 added to the hunk list; §9 item 7 |
| P17 | FIX-NOW | §9 item 4: `req_note_run` (a scan-less run has no scan) and `emit_req_handoff_rest` (a decline's landmark is the head) |
| P18 | FIX-NOW | §5.1.1 D0: the SET rate rule (members share the position's mass), the other `run[]`/`mask[]` readers, F24's count > 0 at the base, the floors armed at D0 |
| P19 | FIX-NOW | §5.1.1 D1: the memfn.h `mf_link` MEMBER/ORDER texts and `mf_pres_picks`' `dominated` text |
| P20 | DOC | §2.4 item 2 "Its facts": `facts` `SF_RUN_NOSCAN`, need through the contract's `CM(N_OPTIONAL)`, no `nofacts` |
| P21 | DOC | §2.1 "The scope, and who passes it": the three callers are precheck `run_part`, `ofsskip_applies` and `ofs_fn_serves`; the rev 2 claims are corrected |
| P22 | FIX-NOW | §5.1.1 D1 floors: declines with a verified member, declines on ASSIGN sites |
| P23 | FIX-NOW | §2.1 item 6: one kit spelling accessor (four readers, one plant); §9 preamble: one pcrec predicate "the pre-check tests the run" |
| P24 | NOTED | §6 C8: the general form (test kind = f(need, findability) per span), with its unlocks and trigger |

## Decisions applied

- P3: §2.4 item 2. The rule is scoped by `SF_RUN_NOSCAN`. On REQUIRED, P0 precedes P2 by contract
  (`N_REQUIRED` vs `N_OPTIONAL`, finder.c's `ct_p0`/`ct_p2`), so the rule never drops K66.
- P9: §2.1 and §5.3. On naming (D174): `fn-every-pos` / `every-pos` ("verify every candidate
  position"). The order is a fact because the `holds` are disjoint; a BODY with no row holding is
  the walk's existing error.
- P15: §5.1 D3 and §5.1.1. The record's fields: `art`, `site`, `part`, `hint`, `terms`.
- P8: §9 item 5. The ruling is quoted, with the edit's place (S2's landing) and its successors.
- P14: §2.2 and every sentence that restated the rule (§1, §4 twice, §9 item 1).

## D3

READY. Its pieces:
- **Record**: `MFTRACE run_part_terms art= site= part= hint= terms=OFF:KIND:VAL,...`, printed by
  `run_part_terms` in the trace build.
- **Census**: one parser of the record in `vcls.py` and in `census0.py forecast`'s `class_measure`.
- **Population (pre-landing)**: the trace-build G2 presence family's wide strata, every target.
- **Check**: two per-site equalities, census against G2's own counts. G2 counts from its generated
  sets plus C2's classifier over the rendered text, so the expectation shares no source with the
  record. The equalities cover unspelled SET terms and `every-pos` parts, and both totals sit on
  literal floors recorded at D2.
- **Joint landing**: the pcrec-artifact floor (stage-3 run parts with a wide verified position, from
  pcrec's artifact diff) is raised from 0.
- **Plants**: p11 (the parser skips SET terms) and p12 (no record for a scan-less part).
- **Witness reasoning** (§5.1.1): on `ab\dcd`, the record lists `SET {0-9}` at 2; C2 reads that
  position as admitting exactly `0-9`; G2 says that set is unspelled. Both sides count 1. Under p11
  the census counts 0 and the check goes red. With the check removed, nothing goes red: the forecast
  would price the site from its RUN term alone.

## Facts for pcrec's stage 3

part_d §9:
1. R by role, only in a window site's alternative; the presence run span is not R. The witness
   `xy/users\d+` keeps `run-pinned`.
2. On a decline, every reader of "a run shipped" reads one predicate, "the pre-check TESTS the run".
   That includes `req_site_define`'s head-part `gate_need` (P1), keyed on a TESTED run.
3. A declined run with no verified member declines the pre-check and gets its `_REQ_WHY`.
4. A scan-less REQUIRED run ships with no `@`. Two emitted comments must change: `req_note_run` and
   `emit_req_handoff_rest` (P17).
5. `set_leads` -1 and run-less dominance on a no-scan run. The lead reader reads the tested run
   (P4). `leads`/`rlead` are retired as independent expectations on non-cube runs (P8), with C2 and
   G2's decline equality as successors.
6. Version events: `MF_SITE_ABI` and `MF_CLASS_V`, each the next number at landing.
7. Spec hunks, now including §6.3.7¶11, `tuning.md` §2.28¶1, §2.29¶4, §2.41¶1 and ¶7a (P16).

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| BOILERPLATE.md and memfn/CLAUDE.md first; first command `rev-parse --show-toplevel` | done; it printed `/home/pcrec/projects/pcrec/worktrees/pdesign` |
| 1. every FIX-NOW (P1-P19, P22, P23) and DOC (P20, P21), each marked `[r2pd Pn]` | part_d rev 3; each id P1..P24 has at least one mark (grep; P13 as P13a-e); per-finding table above |
| 2. P3: a no-scan run is run-less in P2, with the `x.(?:cat\|dog)` witness keeping `dominated` | §2.4 item 2, witness row F3 |
| 2. P9: its own UNMEASURED card, a behavioural name, its choice-order place by fact, the witness | §2.1, §5.3, witness row P2/P9 |
| 2. P15: record `run_part_terms`, pre-landing floor from G2's rendered wide sites, pcrec floor raised at the joint landing | §5.1 D3, §5.1.1 |
| 2. P8: `leads`/`rlead` retired on non-cube runs, pcrec-side in S2's landing, successors C2 + G2's decline equality | §9 item 5 |
| 2. P14: R scoped to a window site's alternative; the run presence span is not R | §2.2, §1, §4, §9 item 1 |
| 3. D3 READY: check, population and floor, plant, a control that reds without the check (named witness) | §5.1 D3 row, §5.1.1 "D3, READY" (`ab\dcd`); "D3" above |
| 4. §9 facts, including P1 (`gate_need` on a TESTED run) and P8's retirement | §9 items 2 and 5 |
| cites verified at a9fc6dbd8 or later; spec/plan by section or [TAG]; a "rev 3" line at the top | cites re-read at main `a8ae73be0` (empty diff on cited code since the base); spec by § and ¶; rev 3 paragraph at the top |
| report with the deliver file's sections, a per-finding table and an `OWED:` line | this file |
| no code, no suites, no queue jobs, no monread; scope (worktree + scratch only) | held: one `nice make -j8` in the worktree and single compiles. The make log was first written to `/var/tmp/pcrec-pcrec/` (the temp root, not `scratch/memfn/pdrev3/`) and then moved there |

OWED: none
