# spanarms6 report: docs/design/span_arms.md rev 2.2 (review 2026-11-08 r4, L2/L3, as ruled)

Lane spanarms6, opus, 2026-11-08. Design and single-pattern measurement only (NO BUILD GO: nothing
under `src/`, `cli/`, `lib/`, `memfn/`, `tests/` touched). Base: main `1ffcce0c1`. One
`nice make -j2 build/pcrec` in the worktree; `tests/lib/p2probe.c` compiled into the lane scratch
against libpcre2-8 10.46; no suites. Evidence: `docs/dev/lanes/spanarms6_evidence/`
(`facts_r4.out`, `facts_tw.out`, `oracle_r4.out`, drivers `facts.sh`, `or.sh`).

## Summary

Rev 2.2 applies READY2-1..7 and READY3-1..9 of `docs/dev/reviews/2026-11-08-r4-spanarms5.md` as
RULED, touching L2/L3 text only: §5.2's TOP row, §5.4 rows A1, A3, A5, A7-A10, A13 and the
closing paragraph, §5.6's L2/L3 rows, §5.7's L2/L3 witnesses plus two new mechanism conditions,
§8's L2/L3 rows and order line, the new §8.1 (L3's sites in A-POSDOM's table shape) and §8.2 (the
kit request), §9, §12's D-next, §13 (Q3 and Q4 extended, Q7-Q9 new). The new §R4 holds every
re-check. L1, E1, R1 and E2 text is unchanged.

No verifier ran in r4, so each finding was re-checked first: 15 HOLD, 1 PARTLY (READY2-1), 0
REFUTED. STOP RULE not met: the L2 blocker READY2-2 HOLDS (read: `req_run_member` compares the
kit's `run_member` with pcrec's `r->idx` and fails loudly; every member reader goes through it),
and no L3 rule was found unsound.

What changed in substance:

- **L2 blocker (READY2-2):** the scan member is ONE decision and it is the KIT's. pcrec states the
  run's consumed extent `[cons_lo, cons_hi)` as a fact on the run window and on the presence run
  span, reads the kit's member at every reader, and cuts its 8-position window around that
  member. `pcrec_find_run_scan_index` leaves the member's path. The request text is §8.2 part A.
- **READY2-1 / rulings R1:** the corrected keep-last value is `a^12 b^20`. W-T2 cannot fail at
  default flags OR under `--memfn=no-fd-pres-pick`: the flag adds only a whole-run presence test
  from `search_from` (`rx_reqrun_whole`, read in the emitted C), K stays the window's, and the
  sabotaged run is a substring of the subject. W-T2 and W-T3 are now `req_whole_run` listing rows.
  The new answer witnesses W-T2a `a^20(?=b^5 z b^14)` and W-T3a `(?<=a^20)b^8 z b^11` are spelled
  literally, so they need no R1, and the lone `z` moves the window's K (hand-derived). With `y`
  the prior picks a uniform `b^8` window (measured), so the rare byte has to be `z`.
- **READY2-6:** `pcrec_run_pin` reads `cons`. The `run-pinned` prefilter stays, and the pre-check
  becomes not-dominated (a listed mover, `dominated` to `emitted`).
- **READY3-3:** K = `omin + at`, which can have either sign. New witnesses: W-L11
  `(?<=e{10})eeeeeqzx` (K 0, `omin` −10; oracle N from 11 and 12) and W-L12
  `(?<=e{8})eeeeeeeeeeqzx` (K 5: today's unsigned distance wraps once the floor is below the
  start; oracle N from 14).
- **READY3-4 ADMIT:** A8's `whole_maxoff < 0` decline is deleted, and the VM attempt-loop rows use
  A3's signed move. Mover: `RX_REQ_HANDOFF` `"0"` becomes the signed K (`(?<=foo)bar(\w)\1`: `"-3"`).
  Spec hunks: tuning §2.41¶8b and match_api §6.3.7¶11. W-L13 `(?<=ab)ab[a-z]*q(\w*)\1` checks
  the entry row (oracle (4,7) from 3, sabotage (2,7)). W-L14 `(?<=ab)ab(\w)\1` on `xababab-` is
  the re-entry move's reaching witness that READY3-2 asked for: the oracle answers N, and the
  sabotage re-runs attempt 3 forever, which the gate's timeout catches.
- **READY3-2:** the margin's unsigned cast is named, and its admission reads `max(K, 0)`. The kit
  is told the same fact (§8.2 part B).
- **READY3-7 BUILD NOW:** §8.1 lists L3's two `PCREC_START0_ROUNDUP` sites (`emit_dfa.c:1175`,
  `:7799`) as rows of (site, mode, the hand it guards). L3 adds no mode and no call site, so R08
  does not grow. The kit's floor is named as a site outside pcrec.
- **Dependencies:** L2 and L3 can go in either order. Both wait for the kit's §8.2 delivery, and
  whichever lands first builds `cons` and the kit-member read.

## Disposition table

| finding | ruling | re-check | applied | where |
|---|---|---|---|---|
| READY2-1 | FIX-NOW | PARTLY: cannot fail at default (HOLDS); under the flag it cannot fail either (REFUTED part; presence-only flag, `a^12 b^20` a substring) | W-T2 a listing row; W-T2a; §5.7 condition (5) | §5.7, §8 |
| READY2-2 | FIX-NOW (facts request) | HOLDS (read `emit_dfa.c:1058-1076`, `window.c:855-890`; `barbaz` member @5 measured) | kit owns the member; §8.2 part A; A1, A13, §9 | §5.4, §8.2, §9, §12, §13 |
| READY2-3 | FIX-NOW | HOLDS (`WIT` has no lookaround pattern) | `bar(?=baz)` ADDED to `WIT` in L2's gate | §5.7, §8 |
| READY2-4 | FIX-NOW | HOLDS (`req.c:841-852`, `findings.c:780`) | trigger on the compare's false-candidate rate; Q4's cost | §8, §13 |
| READY2-5 | FIX-NOW | HOLDS (spec paragraphs read) | hunks ¶6, tuning §2.28¶1, findings.md §4 member row; ¶4/¶5/¶7/¶11/§2.27¶4 checked-unchanged | §5.4 A7, §8 |
| READY2-6 | FIX-NOW | HOLDS (`kset.c:294-318`; `bar(?=baz)` pin 0, run-pinned, measured) | pin reads `cons`; WHY mover listed | §5.4 A5, §5.6, §9 |
| READY2-7 | FIX-NOW | HOLDS (`a{20}` run none, measured) | depends-on rows; order line | §8 |
| READY3-1 | FIX-NOW | HOLDS (same window/K measured) | W-T3 a listing row; W-T3a; `a^8` slip corrected | §5.7, §8 |
| READY3-2 | FIX-NOW | HOLDS (`emit_dfa.c:9057-9063`, `presence.c:199-222`, `lmwalk.c:248` read) | margin in A3, `max(K, 0)`, kit fact, W-L14 | §5.4, §8, §8.2, §9 |
| READY3-3 | FIX-NOW | HOLDS (`e^15 qzx` window @10; oracle) | K = `omin + at`; `req_run_omin` the whole run's; W-L11, W-L12 | §5.2, §5.4, §5.6, §5.7, §9 |
| READY3-4 | ADMIT | HOLDS (`"0"` measured on three patterns; oracle) | decline deleted; mover; §2.41¶8b, §6.3.7¶11; W-L13, W-L14 | §5.4 A8, §5.6, §5.7, §8, §9, §12 |
| READY3-5 | FIX-NOW | HOLDS (`facts.h:88-89`, `req.c:853`) | A10 "already signed", out of L3's changed list | §5.4, §8 |
| READY3-6 | FIX-NOW | HOLDS (`qzab` req_byte 122 measured) | L3 depends on `cons`; W-S4c | §5.4, §5.7, §8 |
| READY3-7 | BUILD NOW | HOLDS (plan `[DEC-POSDOM]` not-started; roadmap A-POSDOM) | §8.1 site table | §8, §8.1, §13 Q8 |
| READY3-8 | FIX-NOW | HOLDS (`facts.c:104`, `:840`; no outside caller of `pcrec_fact_req_run_maxoff`) | §9 sentinel row; none bit for K only | §5.4 A9, §8, §8.2, §9 |
| READY3-9 | FIX-NOW | HOLDS (WHY measured on six witnesses) | today's WHY recorded; gate precondition (6) | §5.7, §8 |

## Kit request text

The full text is in span_arms.md §8.2, for the manager to file as R-n once rev 2.2 is ruled. In
short: it is ONE request in two parts.

- **Part A (gates L2 and L3).** FACT: every successful attempt holds every stated position of the
  run, but only `[cons_lo, cons_hi)` lies inside the match. pcrec states that extent on the run
  window statement and on the presence run span. Why pcrec needs it: `<PREFIX>_REQ_BYTE` promises
  "a byte every match must contain", so the reply's member must lie inside the extent. Ranking is
  the kit's. Ownership: the member is the kit's single decision. pcrec states the whole run once,
  reads the member (at fact-derivation time, before any site exists; the entry is the kit's
  choice), cuts its window around it, and no longer picks a member itself.
- **Part B (gates L3).** FACT: the presence `omin` may be negative, with origin = the attempt start.
  The occurrence is the least one at or after `max(0, origin + omin)`, at entry and at re-entry.
  `head_max` (K) may be negative or zero, meaning the landmark begins up to −K bytes before the
  match start; `omin` is the whole run's, and K = `omin + at`. pcrec's margin reads `max(K, 0)`.
  `head_max`'s none state stays the kit's `handoff` field. If the kit bounds the negative `omin`,
  pcrec's TOP row takes the smaller of that bound and `lb_bytes`.
- The kit chooses the method and the number of `MF_SITE_ABI` events (D157).

## STATE AT HANDOFF

STATE: done. Branch `lane/spanarms6`, commits `31724fb5a` (evidence), `9d2b11453` (WIP),
`c8b77caa4` (rev 2.2), plus this report and its history-index line. Rulings file: last entry
applied R1 (the W-T2/W-T3 arithmetic re-run with `a^12 b^20` before READY2-1's fix; done, see
READY2-1). OWED: nothing run-wise; no suites were in scope. Open for the manager:

- File §8.2 as R-n once rev 2.2 is ruled.
- L3 goes to Frank (§13 Q8, Q9).
- L2 goes after the kit's answer plus one readiness critic.

The answer witnesses added here (W-T2a, W-T3a, W-L12, W-L13's sabotage, W-L14) are HAND-DERIVED
over the stated move, with oracle answers measured. A build lane re-measures them under its plants,
behind §5.7 condition (6), the WHY/HANDOFF precondition.
