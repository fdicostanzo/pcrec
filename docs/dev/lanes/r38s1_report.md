# r38s1 — R-38 interface sheet rev 1 (review 2026-11-09 r2 r38s, as ruled)

STATE: delivered. Lane r38s1 (kit design lane), 2026-11-09, branch lane/memfn-r38s, worktree
`worktrees/r38s`, from tip 713da9faf. Design only: no code, no `make`, no boxqueue job, no compile.

## Summary

Wrote rev 1 of `docs/design/memfn/span_runs_sheet.md` (commit e0c9bf109), applying review
2026-11-09 r2 r38s's rulings: F1-F11, the PLAN unit K38-2a, and §6 Q1-Q6 recorded as RULED. A
"Revision log" table at the top maps each id to its sections; changed text is marked `[r1 F<n>]`.

The main design move (F2): the run's reply is a SITE decision, so pcrec asks at pre-check site
construction in `src/gen/` (`req_pres_ask`), not at fact derivation. That ask already runs
`mf_ask`, the pure define-time query that answers each span's link. So rev 1 adds NO new entry:
the reply (`has_scan`, `scan`, `ver_lo`, `ver_len`) becomes one record of `mf_class`
(`mf_class.run`, an `MF_CLASS_V` move), read only where the run span's link is tested. This one
change also settles F3's none state (read off the link: P2 or no run span means unread), SEAM-6's
two slots (the tested bit and the extent come from one decision in one call), SEAM-1's dominated
case, SEAM-8's art lifecycle, and the review's SEAM-7 question. Rev 0's `mf_run_decide` is gone.

F1: the earned skip is now pcrec's decision when three things hold: SUFFICIENT, OUTPUTS-DETERMINED
(both pcrec facts, neither crosses) and the kit's whole-run extent. The start is `c − omin`. The
kit only reports how far it verified, and no sheet sentence lets it infer exactness. No unit of the
sheet builds the skip (P1 for main).

## Item by item

| id | applied in | how |
|---|---|---|
| F1 | §3.4, §2.3, §3.3 item 3, §6 Q3, §6 P1 | three preconditions (SUFFICIENT, OUTPUTS-DETERMINED incl. MARK, the whole verified extent); start `c − omin`; D187 add. 1's NOTED GAP cited; call-mode clause (unverified, pcrec's at the skip unit); witnesses `(?:ac|ca)xyz`/`aaxyz`, `(bar)(?=baz)`/`barbaz`; "exact where verified" renamed "held where verified" |
| F2 | §2.2, §4.1, §6 Q6 | ask in src/gen at `req_pres_ask`; reply on the Job's pre-check record (the defined site's ask); `req_whole_run` stays the pattern fact; no reply value in a fact (D124); the listing shows pcrec's run |
| F3 | §2.2, §2.3 | `has_scan` (vrun w32's ANDed position allowed; 0 = floor shape); none state off the link; invariants; `ver_len` 0 means `ver_lo` 0 and unread; closed input list incl. `levers`, `pres_proof`, `policy`; "every level in the site's policy the art admits" |
| F4 | §1 Goal 2, §2.5, §4.1, §2.4 C4 | Goal scoped to the pre-check; the prefilter window site's run member named as a second, kept decider, listed in the census; REQ_BYTE = `pcrec_req_pick` over consumed positions (value unchanged at K38-2); C4 restricted to `RX_REQ_WHY "emitted"`, counted |
| F5 | §4.4, §5 K38-2 | tuning §2.28¶5/¶7, §2.29¶4, §2.41; match_api §6.3.7¶5/¶7/¶11, §6.3.1¶5a; facts_listing §4.1.2¶8/¶8b; findings.md §4 rows and ¶2; least-candidate narrowing in ¶11/§2.41; P4 for main (L2's CHECKED-UNCHANGED) |
| F6 | §4.2, §4.3, §5 "existing sabotages" column | the run pin reads the WHOLE run (a counted population; main may reverse); every unnamed reader with a fate (`req_landmark_hit_ppm` moves with the twin; `len >= 2` sites; K derivation; MF_T_RUN readers find the run by position; MFPRES/c10_presence.tsv; KNOWN_READERS; `PCREC_MAX_REQ_RUN_EMIT` retires; `pres-window` lever retires; listing rows); sabotage fates S1095, S1096, S1107 (K38-1), S278, S1543, S1544, S449, S329, S453, S285 (K38-2) |
| F7 | §2.4, §3.5, §5 K38-1 and K38-2a | C1 split (oracle half in G2; skip half at the skip unit, VM route, renderer plant, `barbaz` on `barbaq barbaz` (7,13)); C2 containment and both plants; C4 compares the OFFSET, under `--analysis=uniform` and the new probe lever `run-tie-left`; W-L1 candidate-floor plant plus a rates case; W-K2 `abababcc` (4,8); W-K3 G2 admission-bit observable; W-K4 split into a (guard page, unaligned) and b (ASan, aligned-down at misaligned subjects); K38-1's census plant replaced by a caller check plus a per-reader tie plant; NEW K38-2a (G2 presence family, occurrence oracle (D27 author recommended), C2 classifier, the lever) ahead of K38-2 |
| F8 | §5.1 | K38-2 IS a pcrec abi event; ritual listed; four populations named (Q1 K, Q2 stamp, Q5 names, §4.2 pin) |
| F9 | §2.1, §2.4, §5.1, §6 P3 | run-span constants are true facts or refused; derived part's span fields unread (0, refused if nonzero); "verify fact" vs "tested" named apart; `member` unread on the run; `nterm` 0 and `nalt/alts/wfloor` refusals listed as moving; chain-order clause named as a duplicated slot kept by a check; set-member unification as P3 |
| F10 | §2.1, §3.3, §6 Q3, §6 P2 | `maxoff` departure with its trigger (D176 Q4); verify field vs value; least occurrence -> least candidate, with the pcrec texts that need the same narrowing |
| F11 | §1, §2.1, §6 Q1, header | `verify` cites §6 Q3; Q1 movers corrected (`(?:ab|cd)xabcdefghijkq` 7->2, `\s?xabcdefghijkq` 6->1); landmark cite `emit_dfa.c:1557-1565`; compose.c −23 after 3.0a stated; constraints split from ranked goals |
| K38-2a | §5, §5.1 Order | G2 presence family as a PLAN unit ahead of K38-2, with witness and plants A-C |
| SEAM-7 | §6 Q6 | answered: K38-2 adds no entry; the general form kept as a noted unlock with three triggers |
| §2.1's sentence | §2.1 | kept verbatim ("The seam stays D172's LIST ...") |

Nothing ruled was left unapplied.

## Rulings applied

The review's "Manager rulings (2026-11-09)" in full, and the brief's restatement:
- Verdict and every PROPOSED disposition: applied as above.
- F1 owned: SUFFICIENT and OUTPUTS-DETERMINED defined in §12c's words; "fires only when all three
  hold" (§3.4).
- F2: src/gen at site construction; Q6 reversed (§6 Q6).
- Q1 YES, Q2 (b), Q3 NO confirmed, Q4 YES with K38-2a first, Q5 accept, Q6 src/gen: §6 items 1-6.
- D157: the sheet states facts only. pcrec-side names (`req_run_reply`) are marked as pcrec's.
  The probe lever is a kit test-only lever, not a method field.

## Open questions

1. (§6 Q7, new) Ruled (b) has no spelling where no run part renders (P2 `dominated`, `cover`, or no
   pre-check site asked). Recommend: the whole run with no `@`, and retire the `req_run` listing
   row into `req_whole_run` in the same spec hunk.
2. A design departure for main to confirm: the review's F2 text said "keep the reply on the Job's
   pre-check record with the link" and kept an entry. Rev 1 goes one step further and puts the
   reply INSIDE `mf_ask`'s class, with no new entry, so the tested bit and the extent cannot
   disagree (SEAM-6). The cost is an `mf_class` member, which K38-2 already moves.
3. The probe lever `run-tie-left` is a NEW lever class. Today's contract says a lever "restores an
   OLD form" (`memfn.h` `mf_lever`). K38-2a adds a contract sentence for a test-only lever that
   perturbs one decision to a different SOUND choice. Main may prefer to drop the lever and use only
   the all-tie regime for C4.
4. §4.2's run-pin choice (the WHOLE run) is a pcrec-side choice made here at the review's
   request (F6 "must choose"). Main may reverse it at K38-2's brief.
5. Q2's original round text put "the extent in the listing only", which F2's ruling (no decision
   in the listing, D124) contradicts. Rev 1 shows the extent in the site's trace records instead.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| read BOILERPLATE, memfn/CLAUDE.md, docs/design/CLAUDE.md | done before writing |
| rev 1 answering review r2, rulings first | sheet, commit e0c9bf109 |
| ALL of F1-F11 as ruled | Item by item above |
| F1: cover not language; SUFFICIENT + OUTPUTS-DETERMINED; kit reports extent only; no sentence implying otherwise | sheet §2.3, §3.3 item 3, §3.4 |
| F2: ask at pre-check site construction (src/gen); entry and call point re-homed; Q6 reversed | sheet §2.2, §6 Q6 |
| §6 Q1-Q6 recorded RULED | sheet §6 items 1-6 |
| K38-2a as a PLAN unit ahead of K38-2 with witness and plant | sheet §5 |
| §2.1's D172-list sentence kept | sheet §2.1 |
| facts, not methods (D157) | sheet §2-§4 |
| Revision log at the top, id -> section | sheet "Revision log" |
| CLAUDE.md line | docs/design/memfn/CLAUDE.md (rev 1 line) |
| report with the deliver file's sections | this file |
| history-index line | docs/dev/history/claude_md/docs__dev__lanes.md |
| lanecheck DONE | run before the handback |

## STATE AT HANDOFF

OWED: none (design lane; no runs queued). No rulings file was named in the brief. Next: main
reviews rev 1 (the review's short re-check round: fix-induced + readiness) before K38-2's build go.
K38-1 may proceed after 3.0a.
