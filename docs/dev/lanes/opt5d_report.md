# opt5d2 — REVISION 2 of the [OPT-5] STEP 2 design note: delivery report

Lane `opt5d`, branch `lane/opt5d`, 2026-09-02. Deliverable: revision 2 of
`docs/design/opt5_step2_twopass.md`, working every finding of the D6 panel
review `docs/dev/reviews/2026-09-01-r49-opt5-step2.md`.

**Nothing under `src/` or `tests/` is touched.** The lane's whole diff against
`main` (`05c984b`) is six documentation files.

## 1. Commits

Range: `main`..`lane/opt5d`, starting from the merge of `05c984b` into
`8d36141`.

| commit subject | what |
|---|---|
| `opt5m2 premeasure memo lands with rev 2 (24ba0c4)` | `docs/dev/opt5_step2_premeasure.md` + `docs/dev/opt5m2_m2_changed_patterns.txt` checked out from `lane/opt5m2`, two entries added to `docs/dev/CLAUDE.md`. The `[OPT5M2-PROBE]` `emit_dfa.c` hunk was deliberately NOT taken |
| `wip(opt5d2): rev 2 header + changed-from-rev-1 summary` | header bumped, nine-point change summary |
| `wip(opt5d2): sections 0-1.2 …` | two-instrument frame, quantified rescue claim, P0/P2/P3/P5 |
| `wip(opt5d2): section 3.2/3.3 rewritten …` | the proof re-derived from the emitter |
| `wip(opt5d2): section 3.4 … + new 3.5 …` | failure directions reworked, failing-call bound closed |
| `wip(opt5d2): section 4 …` | axis J, the approved mirror hunk, the fold prediction table, D94's grep |
| `wip(opt5d2): sections 5.2/5.4/5.5 …` | named manifest, force-axis owed measurement, checks 5–9, narrowed size prediction |
| `wip(opt5d2): section 5.6 rebuilt …` | ids S218–S222, S219 declared UNREACHED, SAB_REACH_POP from birth |
| `wip(opt5d2): sections 5.7/6/7 …` | spec-delta table with the struct hunk, six new owed measurements |
| `wip(opt5d2): section 10 …` | the r49 disposition table |
| `wip(opt5d2): sections 2/5.1/5.3 …` | M3's confirmation lands, verdict-not-offset exception, (B) pin value |
| `docs: design/CLAUDE.md entry revised in place for rev 2` | the rev-1 entry REVISED, not duplicated |
| `wip(opt5d2): lane log …` | the restart record |

The note went from 812 to ~1,915 lines.

## 2. The disposition table (note §10) — summary

All 18 numbered r49 §2 items and all five MINOR items are dispositioned with
the section(s) changed and, for CONFIRMED-class items, the sentence added.
Headline dispositions:

- **BLOCKER-class (1–6):** all six WORKED. Item 3 is CLOSED (the failing-call
  bound is unsound; no `_match` change in STEP 2) rather than fixed, as ruled.
- **MAJOR (7–18):** all twelve WORKED. Item 8 is worked as the "cannot
  construct a witness" branch the brief allows; item 17 is worked with one
  flagged deviation (below).
- **MINOR:** all five WORKED. `tuning.md` is NOT edited — its §3.2 bullet's
  wording is written out in note §6.1 for the implementation lane, per D80.

## 3. What I could NOT fully discharge

**r49 item 8 — a synthetic witness reaching P3.** I could not construct one,
and the brief's stated fallback applies: the row ships as the phantom-check
shape, named as such.

The note's §5.6b gives the derivation rather than just the failure. On
`ENG_UNANCH`, `(?m)^` and `\G` route away via `nfa_has_bot`; `(?m)$`'s
dependence is on the upcoming byte and creates no `s1u` split; and
`s1u[UPC_PLAIN] == fs` always. So only `s1u[WORD]` can differ. Then the
squeeze: for `fs` to pass P2 its accept must be invariant in the upcoming
byte, which rules out an accept reached through `\b`/`\B`; so a passing `fs`
accepts through a boundary-free branch, and a boundary-free branch sits in
every seed closure — making every seed state accept AND be live. **P1 passing
at `fs` appears to imply P1 and liveness at every seed.** Six candidate shapes
are named and rejected in the note so the next author does not repeat them.

Consequences recorded in the note:

1. S219 ships `SAB_EXPECT=UNREACHED` with a reason, so `[MECH-REACH]`'s reverse
   check reads NOW REACHED the day somebody builds the witness. That reverse
   direction is the row's whole value.
2. The liveness conjunct's real guard is a **compiler assertion**, not a
   sabotage row — an assertion needs no witness, its firing is the finding.
3. §7 item 10 is the measurement that settles it: **count P3 EVALUATIONS, not
   declines**, on the default AND force axes. M1 counted declines (0), so
   "P3 is unreachable" and "P3 is reachable but never declines" are still not
   distinguished. Trigger: before the implementation ships S219 as anything
   other than UNREACHED.

Everything else in the r49 list is fully discharged in the note.

## 4. O-14

**O-14 had NOT landed.** `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md`
was last written 2026-09-01 18:47:34 and its newest message is `## O-13`;
checked at the start of the session and again at 11:28 EDT 2026-09-02.

Every scratch-tier number in note §0 therefore carries an explicit
**`[O-14 PENDING — manager fills at merge]`** marker, and §0's provenance rule
states which readings are scratch tier (O-13's two `pcrecbench quick` cells,
`--trials 3`, both stamped `inconclusive-load`, ratio-only) and which are not
(ledger readings and stamp facts, unmarked).

## 5. Findings against the review, the note's premises, or the code

1. **The [DD-13c] append discipline and the review's wording disagree, and the
   discipline wins.** The review says append the `rx_info` mirror "after
   `match_form`". That was the append point when `match_form` was the last
   member; `name` and `nentries` now follow it (`src/gen/emit_dfa.c:735ff`,
   added at abi 15). Taking it literally would move their offsets — the exact
   thing the discipline exists to prevent. **The note's hunk appends at the
   END, after `nentries`**, and records the reading (note §4.2, §9 F8).
2. **The mirror's guard is NOT `match_form`'s.** `match_form` is guarded on
   `fit.chosen == ENGM_DFA` because a hybrid's `_match` is the VM's. Axis J
   describes `<prefix>_search`'s post-loop block, which a hybrid DOES contain.
   So `search_form` uses `pcrec_artifact_has_dfa_scan` — the predicate
   `emit_info_def`'s own note at `:1690-1697` explicitly contrasts against.
   The review did not state this and an implementer copying `match_form`'s
   guard would stamp NULL on every hybrid.
3. **r49cons's reconciled frame table is not in the review verbatim.** The
   review's §6 carries r49cons's Q3 only as a summary sentence. Note §0's
   two-instrument table is a **reconstruction** from that summary plus O-13
   §2/§2(c) and this build's own stamp probes. The manager should check it
   against r49cons's delivery message before merge.
4. **A minor line-number correction to the review.** `dfa_table_name`'s
   reverse read is at `emit_dfa.c:2665`; `:2664` is the forward read. The note
   cites the pair.
5. **The two P3 arms share one sabotage id.** Revision 2 has a sixth failure
   direction (the liveness conjunct) but the brief specified five ids
   (S218–S222). Rather than mint a sixth id this worktree cannot safely claim,
   S219 carries both arms; flagged for the manager's arbitration at merge.
6. **The `.rxt` `startpos > 0` population is genuinely unquantified.** Note
   §5.6d gives the structural reason (plain `m`/`n` cells are startpos-0; only
   `ms`/`ns` carry nonzero) and two acceptable discharges. This is a real gap
   in the corpus, not just in the check plan, and §3.4(e) is invisible without
   it.
7. **Sabotage ids are provisional by construction.** S218–S222 are free at
   `05c984b`, but per `tests/mech/sabotages/CLAUDE.md` a worktree's id space is
   as of its branch point. The range is the manager's to arbitrate at merge,
   with a SIMULTANEOUS substitution if it moves.

## 6. Open questions for Frank

None blocking. Two worth a ruling when convenient:

1. **Should the P3 liveness conjunct ship as an assertion or a decline?** The
   note says both — the predicate declines, and the implementation asserts the
   conjunct so a machine reaching the elision with a dead seed is a loud
   internal error. If Frank prefers only one, the decline is the load-bearing
   half and the assertion is the belt.
2. **Q3 (the stamp's spelling) is still the manager's call**, and revision 2
   adds one consideration: Frank's Q2 ruling fixed the mirror field's name
   (`search_form`), so a stamp spelling that does not read as that field's
   macro would weaken the pairing check 5.4(8) relies on.

## 7. What the implementation lane inherits

- Note §6 is the D80 spec-delta list, eleven rows, including the `rx_info`
  struct hunk and the exact wording for `tuning.md` §3.2's third mirror bullet.
- Note §4.4 gives D94's grep, not a site list. abi 15 → 16.
- Note §5.4 has nine structural checks; §5.6 has five sabotage rows with their
  reach obligations; §7 has fourteen owed measurements, three TAKEN and six new
  in this revision.
- Note §8 marks all seven of Frank's rulings as STANDING, with Q2 flagged as
  the one ruled AGAINST the note's own rev-1 recommendation — the item an
  implementer reading rev 1 is most likely to get wrong.
