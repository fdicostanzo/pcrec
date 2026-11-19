# spanarms8 report — review r51 filed; span_arms.md rev 3.1

Lane spanarms8 (opus, 2026-11-18), branch `lane/spanarms8` cut from lane/spanarms7 @ 4bf63fb9d. Design only: no
code, no make beyond `make -s test-plan-lint`, no suite, no queue job.

## STATE AT HANDOFF

OWED: none

- STATE: complete. Rulings file `docs/dev/lanes/spanarms8_rulings.md`: empty at every check (before each commit
  and before this report); last R-n applied: none.
- Premise test held: `git log -1 --format=%h -- docs/design/span_arms.md` printed 3b7d1508e at start; the scratch
  review's by-id completeness line counts 47 findings.
- PART 1 committed (1696f04e7): `docs/dev/reviews/2026-11-18-r51-spanarms7.md` (the draft with a "RULED (manager,
  2026-11-18):" line after every PROPOSED disposition, verbatim from the dispositions file; the verdict, READYL2's
  conditional discharge, the D27 recommendation, the process-change hold, the lane's F-7 and the filing ruling also
  RULED), and its directory: COMMON, CONFORM, READYL1, READYL2, READYL3, RULING, verify, process (= .coord/process.md),
  dispositions, CLAUDE.md. Scrubbed cites: verify.md (tuning.md l.933 → §2.41¶1; match_api.md l.2437 and
  facts_listing.md l.95 dropped beside their section tags), RULING.md (plan.md l.871-877, l.877 ×2, l.950-954,
  l.555-558 → the rows [CTX-FACTS-NEG], [CTX-SIDES-PRODUCER], [NEVER-MATCH]). The remaining `l.NNN` cites in the
  copies are span_arms.md / the note / ARCH-STEP.md body lines (not plan.md, not spec). Reviews index line added;
  the oldest line (r12-memfn-d3fix2) moved to reviews/NOTES.md (CLAUDE.md 12,125 bytes, size check green).
- PART 2 committed: `docs/design/span_arms.md` rev 3.1 (status line history entry; 123 `[REV 3.1 ...]` markers).
- Lanes history index line added (docs/dev/history/claude_md/docs__dev__lanes.md). Not edited: the note, the
  register, the guide, decisions.md, docs/design/CLAUDE.md, anything under src/ cli/ lib/ memfn/ tests/ scripts/.
- No STOP-rule finding: no ruled disposition was contradicted by the tree or the record.

## FINDINGS APPLIED

| finding | applied? | where in span_arms.md rev 3.1 |
|---|---|---|
| READYL1-1 | applied (option a) | D-1 table: E-5i arm `look \| zero`; D-1 paragraph lists the five readers kept true; §5.8 marker |
| READYL1-2 | applied | §14.4 L1 Feature: `walk_arm_facts` = PF_REQ_WHOLE_RUN, PF_REQ_SET, PF_REQ_SET_MAXOFF (not PIECES); D-13 L1 row gains facts_listing §4.1.3¶4a |
| READYL1-3 | applied | §14.4 L1 Tests: S1925 re-aimed onto E-5i's action; L1 Feature lists the 11 feature anchors |
| READYL1-4 | applied | D-9 paragraph + L1 remodel 2 (RM-6): run_cpset_structure.sh in the gate; `is_never_leaf` stays in derive.c (a NODE answer); binding S899, others checked |
| READYL1-5 | applied | §14.2 five rows' L1 cells (req_set / req_byte / RX_REQ_BYTE); L1 census model gains the set step, expected movers listed |
| READYL1-6 | applied | D-10 "WHERE THE HEAD'S PER-KIND RULES LIVE": one rule in desc.c with a position callback (register row 27's move), `RbVal.head` and its writers listed; src/facts/CLAUDE.md line named; L1 remodel 3 |
| READYL1-7 | applied | D-3 CAT-SET: `run.off + i`, saturating, before the floor; `RbSet.pick` not updated, stated |
| READYL1-8 | applied (a, b, c) | D-3 (`rb_rep_best_val` copies `never`); D-5 + L1 remodel 1 (why the ReqRun half rides early; 0 anchors); §14.1 item 4 + §5.7 W-T1 marker |
| READYL2-1 | applied | §14.1 item 6; §5.7 W-T2/W-T3 markers; L3 and L2 Tests: answer witnesses under `--memfn=no-fd-pres-pick` only |
| READYL2-2 | applied (retire) | §14.1 item 7; §5.7 W-L11 marker; L3 Tests: W-L11 struck and RETIRED |
| READYL2-3 | applied | §14.2 row `[a-z]abc` K 1; L2 census; L2 Tests W-L9 numbers; §5.7 W-L9 marker |
| READYL2-4 | applied (placement note) | D-13 L3 and L2 rows. The pick-stretch sentences (§6.3.7¶5, tuning §2.27¶4, §2.28¶7) are placed in the L3 row, not L2's as the finding wrote: D-6 gives the consumed extent its first value at L3, where `(?<=qz)ab` already makes them false; the row says they move with L2 if L2 lands first. facts_listing §4.1.2¶8 and tuning §2.41¶8c split by side (BEFORE at L3, AFTER at L2) |
| READYL2-5 | applied (as ruled) | D-4 BACK row: `++ rg` clause is L2's; D-4 paragraph; §5.2 TOP marker; §14.2 new row `(?<=foo)bar(?=baz)`; L3 census (no mover), L2 census/Feature/Tests (mover, witness, plant) |
| READYL2-6 | applied (1-4) | L2 Remodel (L2-first list); §5.7 W-S4b, W-T2a, W-T3a, W-L13 markers |
| READYL3-1 | applied (as ruled) | D-8: guard per row (new column), `k != 0 \|\| round.len > 0`; the witness `(?<=a)a(\w)\1` from 3 on `-aaaaaq-b`, oracle (3,6), with its run (kept guard (2,5); 22/1857 vs 0); L3 Tests W-L15 + guard plant |
| READYL3-2 | applied | L3 Tests: run_prechecks.sh [5.12b] K<0 arm, [5.12a] lookbehind rows (byte ×2, utf8 ×1) |
| READYL3-3 | applied | D-13 L3 row (with READYL2-4 / CONFORM-4): §6.3.7¶6, tuning §2.28¶1 definition, facts_listing §4.1.2¶8, BEFORE side |
| READYL3-4 | applied (clamp form) | D-8 K<0 cells: `if (n - hit < B)` / `if (n - landmark_position < B)` the miss path; the false claim withdrawn with its reason; L3 Feature; L3 Tests W-L16 (asan) |
| READYL3-5 | applied | L3 Tests: vmhat_checks.py admits a signed decimal |
| READYL3-6 | applied (rule, row kept) | D-6 empty-extent rule (accessor none at lo == hi, set's pick, pin none); D-4 extent cell; §14.2 three rows; L3 census and Tests W-L17..W-L19 |
| READYL3-7 | applied (with CONFORM-3) | D-4 + L3 remodel 5 (`rn_cmp` its own commit), S474 re-aimed, S1930 checked; RM-4's text struck |
| READYL3-8 | applied | L3 RM-2 (S3075 first line checked), RM-3 (the tool's first-line limitation), Feature (S3075 re-aimed with the re-ask edit; S3074/S3076/S1702 K >= 0 note) |
| READYL3-9 | applied (1-5) | L3 Feature "Also RESTATED" (1)-(3); D-6 (4); D-13 L3 checked-unchanged cell (5) |
| CONFORM-1 | applied | D-10 and L1 Deletes: row 27 |
| CONFORM-2 | applied | D-3 marker; D-4 `RB_ROW_EACH` and register row 19's event + proposed status; L1 Feature |
| CONFORM-3 | applied (with READYL3-7) | as READYL3-7 |
| CONFORM-4 | applied (with READYL3-3) | as READYL3-3 |
| CONFORM-5 | applied | §14.4 L1 "REMODEL OVERLAP" paragraph |
| CONFORM-6 | applied | §14.0 RM-6 bullet; D-9; L1 remodel 2 (the corpus gate near-vacuous, the compound tests the real gate) |
| CONFORM-7 | applied | D-9 paragraph: mrl.c stays a width saturation; PfNever/`empty` machine-level |
| CONFORM-8 | applied | §14.1 item 5; D-7; §12 D-next |
| CONFORM-9 | applied | D-10 "WHY THE REP WALL STAYS UNTIL R2"; §8 R2 row's census |
| CONFORM-10 | applied (as ruled) | §14.0 RM-6 bullet with the proposed register row 5 status; D-9 NEVER column |
| CONFORM-11 | applied (PLAN) | §10 U-bestof with trigger; nothing built |
| CONFORM-12 | applied (DOC) | D-7 names `PfBound`; §10 U-bound |
| CONFORM-13 | applied (DOC, our side) | D-10 cross-reference; §10 U-edge. The matching sentence in docs/design/vlookbehind.md is NOT written (outside this lane's files): owed by the manager |
| CONFORM-14 | applied | D-8 paragraph: K-sign rows are A-POSDOM's input |
| RULING-1 | applied | D-9: the owner's words "can be built in the AST area" quoted; the restatement named as such |
| RULING-2 | applied | §14.1 item 1 (the check, three cites); §12 addendum text + header marker |
| RULING-3 | applied | §12 D168 addendum: what it amends and why it is not "two mechanisms"; the plan NOTE mismatch named for the manager |
| RULING-4 | applied (as ruled) | §14.4 common (1): D191.1 quoted, one-sentence why, THE MANAGER'S READING marked; each census bullet |
| RULING-5 | applied (PLAN + facts) | §14.5: L1-L3 do not deliver it; the owing row named ([CTX-SIDES-PRODUCER]); facts below |
| RULING-6 | applied (DOC) | §14.5 the two "0"s mapped |
| RULING-7 | applied | L3 Feature and Deletes: §5.4 A8 (r4 READY3-4) |
| RULING-8 | applied | D-11 cites D191.3's words |
| RULING-9 | applied | §14.1 item 2; D-14 |
| RULING-10 | applied (DOC) | D-12: the pcre2 note cited, the question narrowed; dispatch is the manager's |

47 of 47 applied; none not applied.

## WHAT MOVED

- The three answer/safety fixes that gate L3: (1) READYL3-1, the entry guard is per row: the K < 0 row always
  emits its move (`k != 0 || round.len > 0`), witness `(?<=a)a(\w)\1` from 3 → (3,6); (2) READYL3-4, an end clamp
  on every K < 0 row (`n - hit < B` → the miss path), replacing a false "cannot pass the end" claim; (3)
  READYL3-6, an empty consumed extent has no run pick (no `n = 0` call into `pcrec_find_run_scan_index`).
- Unit shape: L3 is BACK-only (`++ rg` moves to L2); L3 gains remodel commit 5 (`rn_cmp`); L1 gains RM-6 (the
  NEVER column, after RM-1) and remodel 3 (the head's per-kind rule into desc.c, register row 27's own move).
- Every census STOPs on its MODEL's predicted population (the manager's reading of D191.1, to be told to the owner).
- Witnesses: W-L11 retired (with W-L12); W-T2/W-T3 answer witnesses under the flag only; new W-L15 (answer), W-L16
  (asan), W-L17..W-L19 (empty extent); W-L9's numbers; D27 witnesses listed as owed by the build lanes.
- Spec list (D-13) completed per unit and side.
- Proposals for the manager to file (the design does not edit the register): register row 5 status (RM-6), row 19
  status (`RB_ROW_EACH`), and a NOTED DEVIATION row for F-7 (D-8, in the register's columns).

Judgement calls a confirm critic should look at: READYL2-4's pick-stretch hunks placed at L3 (reason in the
table); READYL1-6's fix chooses the SHARED extraction (one per-kind head rule with a position callback) and puts
it as an L1 remodel commit under register row 27's own event, which is a remodel commit outside RM-1..RM-6 (the
manager may want to confirm the remodel-go call reaches it, as for RM-6); READYL3-6 keeps the BACK row for an
empty extent rather than adding `head.n > 0` (the clipped `(?<=a{32})b` case needs the extent rule anyway).

## FACTS FOR THE MANAGER

RULING-5's fact task (facts only):
- The kit-proof note is `docs/design/kit_proof.md` (not under docs/design/memfn/). Its §7 row **B1**: "THE ONE
  BYTE-MOVING EVENT, after B4: the REPORT row routed in the default build together with pcrec's row; ... the
  `"cover"` stamp; ...". Its §R2.3 is headed "What the build (D172 S3, B1's event) superseded" (rev 2.3, lane
  s3fix, 2026-10-24). On main, bc675b020 (2026-10-23) "D172 S3: REPORT routed by the window family's E-find row,
  D-hors; cover by default; abi 83 -> 84" is B1's event; it is an ancestor of main.
- [CTX-SIDES-PRODUCER] (`scripts/entry CTX-SIDES-PRODUCER -l 2`): STATE:not-started, filed 2026-11-08 (lane
  spanarms2), status (2026-11-08) "not started; today the cover's one-position context sides are a machine
  reading of the anchored DFA". Trigger, quoted: "a second machine-side consumer of a context side, or cover B1
  (kit_proof.md §7)". The event "cover B1" occurred 2026-10-23 (bc675b020), BEFORE the row was filed: its
  trigger HAS FIRED (it was already met at filing), and the row still reads not-started with no fired note.
- [LOOK-LOCATE]: not-started; trigger "span_arms unit L3 has landed, and a bench cell whose rarest bytes sit in a
  lookbehind" (not fired: L3 not built). It LOCATES on a lookbehind's bytes; it does not prove a match.
- [COVER-CAP]: started; status (2026-11-18) "stage 1 landed (abi 108); stage 2 + the kit's forms MERGED on
  lane/covs2land (c774d15c0, abi 109) ..."; it lifts the cover's 24-position cap; it says nothing of lookbehind
  context.
- Which row owes "the match is proved and search is over" for `(?<=foo)bar`: of the plan rows, only
  [CTX-SIDES-PRODUCER] has the cover's context sides as its subject (its body: "One producer of subject sets at
  signed offsets (D168)"); the design names it (§14.5). Note: its row text scopes `MkEnd` `ctx_before`/
  `ctx_after` (known.h: `ctx_before[32]` is "C_{-1}", one position), and does not itself say "wider than one
  position". D172's decision text says "Fixed lookbehinds and post-span lookaheads longer than 1 come with it [the
  unified window site], sourced from main's D168 producer" — a second record naming the same outcome, with no
  plan row of its own that I found.
- Route stamps, the main tree's build/pcrec (built 2026-11-15 19:53). The brief's exact command (`-p rx
  --emit-main` WITHOUT `--features all`) fails on both lookbehind patterns: `pcrec: (?<...) requires module
  'lookaround' (pattern offset 0)`; `foobar` compiles. With `--features all`:
  - `(?<=foo)bar`: `RX_DFA_SCAN "unanchored"`, `RX_DFA_SCAN_EDGE "none"`, `RX_REQ_RUN "626172@0"`, `RX_REQ_BYTE
    "98"`, `RX_REQ_HANDOFF "none"`, `RX_REQ_WHY "dominated"`, `RX_VM_PREFILTER "hybrid"`; 0 lines matching COVER.
  - `(?<=f)bar`: `RX_DFA_SCAN "cover"`, `RX_DFA_SCAN_EDGE "none"`, `RX_REQ_RUN "626172@0"`, `RX_REQ_BYTE "98"`,
    `RX_REQ_HANDOFF "none"`, `RX_REQ_WHY "dominated"`; 0 lines matching COVER.
  - `foobar` (same with or without `--features all`): `RX_DFA_SCAN "cover"`, `RX_DFA_SCAN_EDGE "range"`,
    `RX_REQ_RUN "666f6f626172@3"`, `RX_REQ_BYTE "98"`, `RX_REQ_HANDOFF "none"`, `RX_REQ_WHY "dominated"`; 0 lines
    matching COVER (the uppercase token does not occur; the route is the lowercase stamp value).

Other items owed to the manager by the rulings (not actions of this lane): the register edits proposed (rows 5,
19, the F-7 deviation row); the D168 addendum's filing and the [CTX-FACTS-NEG] NOTE alignment (RULING-3); the
vlookbehind.md half of CONFORM-13's cross-reference; RULING-4's reading told to the owner; RULING-10's narrowed
pcre2-reader question (dispatch optional); the confirm critic before any build.

## COMMANDS

- `git -C /home/pcrec/projects/pcrec/worktrees/spanarms8 rev-parse --show-toplevel`; `git -C ... log -1 --format=%h -- docs/design/span_arms.md` (3b7d1508e)
- `python3 -I $PCREC_TMPDIR/scratch/spanarms8/scrub.py <worktree>/docs/dev/reviews/2026-11-18-r51-spanarms7` (copies + cite scrub, asserting each replacement found)
- `python3 -I $PCREC_TMPDIR/scratch/spanarms8/file_review.py <worktree>/docs/dev/reviews/2026-11-18-r51-spanarms7.md` (RULED lines; printed 47 ids, 47 distinct)
- `bash scripts/check_claudemd_size.sh --all` (402 within limits); `make -s test-plan-lint` (checks passed: 2, failed: 0), run after each part; the pre-commit hook's staged checks passed (52) on each commit
- `grep -rn "B1" docs/design/kit_proof.md`; `sed -n 54,70p docs/design/kit_proof.md`
- `scripts/entry CTX-SIDES-PRODUCER -l 2`; `scripts/entry LOOK-LOCATE -l 2`; `scripts/entry COVER-CAP -l 1`
- `git -C /home/pcrec/projects/pcrec log -S'"cover"' --oneline --reverse main -- src/gen/emit_dfa.c` (bc675b020 first with the cover default); `git log -1 --date=short bc675b020`
- `grep -n ctx_before src/gen/known.h`; `sed -n 9906p docs/dev/decisions.md` (D172's "longer than 1" sentence)
- `timeout 60 /home/pcrec/projects/pcrec/build/pcrec -p rx --emit-main -o $PCREC_TMPDIR/scratch/spanarms8/lbN.c --pattern P` for the three patterns (the lookbehind two refused: module), then the same with `--features all` to `lbfN.c`; `grep -hoE '(RX_DFA_SCAN|RX_REQ_[A-Z_]+|RX_VM_PREFILTER)( |_[A-Z_]+ )"[^"]*"'` and `grep -c COVER` on each
