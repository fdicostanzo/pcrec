# spanarms7 report: span_arms.md rev 3, the lookaround units L1-L3 re-based on the accepted architecture note

Lane spanarms7, opus, 2026-11-18. Design only (no build go for this lane); no file under src/, cli/, lib/,
memfn/, tests/ or scripts/ was touched.

## STATE AT HANDOFF

OWED: none

- STATE: done. Branch `lane/spanarms7`, cut from main `8993b8f82` (= T for every code statement).
- Rulings file `docs/dev/lanes/spanarms7_rulings.md`: empty at every read (before the WIP commit, before
  this report). Last R-n applied: none.
- Deliverable: `docs/design/span_arms.md` rev 3. The design of record for L1, L2, L3 is its new §14; §12
  carries the rev 3 D-next amendment and the rev 3 D168 addendum text (for the manager to file); every
  rev 2.2 passage §14 replaces carries an inline `[REV 3: ...]` marker (23 markers); the status line is the
  history entry.
- Validation: `make -s test-plan-lint` PASS (plan lints clean; selftest 45 plants, 0 failures); a grep of the
  added lines for `.md:NNN`/`plan.md:` line cites finds none. No suite run (none owed).

## WHAT MOVED

- `docs/design/span_arms.md`: status → PROPOSED rev 3; new §14 (base and built state, the stale list, the
  re-measured "today" table, D-1..D-16 answered, the units L1 → L3 → L2 each with census, remodel commits,
  feature, contract, abi, tests, card and deletes, the owner's 2026-11-18 words mapped to the units,
  standing questions, commands C-R0..C-R9); §12 gains the rev 3 D-next amendment and D168 addendum (the old
  addendum marked SUPERSEDED); inline markers in §2, §3.7, §5.1-§5.8, §6, §8, §8.2, §9, §10, §13.
- Main design results, each with its reason in §14.3:
  - The item is form (a) SHARED (A17): a lookahead reads desc.h's head column (`PdHead`, FIRST positions),
    a lookbehind its body's description (LAST positions), united by the module's one per-offset union
    (`pcrec_ph_alt`) reading each group as a reversed head. No third family, so register row 29 (ND-2) is
    not taken and row 26 (P5) is discharged by L1.
  - The never fact (A8, D-9 answer (a)): derive.c's prune rules are extracted as one declared row table in
    the AST area, read by derive.c and by the run walk. The root's never is rendered as `req_whole_run`'s why
    `dead`. It does NOT reach `never_matches` or the empty artifact at L1, so P6 is not needed. [NEVER-MATCH]'s
    trigger fires at L1's landing.
  - K gets three states (none / bounded / unbounded) plus a signed value. `omin` is `min(0, K)` for every
    run TOP builds, so there is no `RbRun.omin`, no `ReqRun.omin` and no `req_run_omin` row.
  - The consumed extent lives on `ReqRun` (not on `RbRun`) with one accessor. `rn_better` is split into a
    comparator so TOP's candidates keep their extent beside them.
  - `reach` is not a walk parameter: TOP is a combining row table (BACK at L3, AHEAD at L2) whose rows the
    `look` arm passes over. `lb_bytes` is a walk parameter read through RM-5's accessor.
  - CAT-SET is re-spelled as one step at the walk's exit over the chosen run's consumed exact positions. The
    reason: `rr_pow`/`rr_rep_split` join copies through `rr_cat` with no set, so rev 2.2's step missed them.
  - RM-3's one emitter replaces a mode with the "target is the hit" rule, and S470/S809 keep per-caller
    plants. L3's signed form is a 3-row table on K's state. At K >= 0 it is today's text, byte for byte.
  - Units in the order L1, L3, L2: L3 has its go, so it lands the shared pieces first (RM-4, the consumed
    extent).
- Findings for the manager (not owner questions):
  - F-1. D-16 has THREE emitted K comments, not one: emit_dfa.c:1118, :7900, :7967 (C-R7). L3 is an abi
    event for them and for the signed move.
  - F-2. Site 16's ":1469 start stating the fact" moves nothing. memfn.h's run span is "start 0, verify NO,
    core all"; only `omin` (:1479, the run's entry) changes.
  - F-3. A remodel commit outside the note's RM-1..RM-5 is needed: the extraction of the never rows from
    derive.c. It rides L1 under the remodel-go call (site 21 maps derive.c). It is byte-identical, gated on
    the .c streams plus `tests/compound/compound_drive.c`, and its anchors come from the map with a derive.c
    range group added.
  - F-4. With the window retired, W-T2 and W-T3 become ANSWER witnesses. W-L11's K is −10. W-L12 is RETIRED:
    its K > 0 case is unreachable because a BACK run has `omin = maxoff`.
  - F-5. `(?<=fo{1,3})bar` stays `bar` at L3, against rev 2.2's predicted `obar`: a split repeat walls the
    description.
  - F-6. The plan row [CTX-FACTS-NEG]'s status and trigger still read as filed. The re-scope is recorded only
    in the plan row body.
  - F-7. D-8 RE-TESTS K's state through one predicate rather than acting through a start row. This is
    "Act through the row" not applied: the move text serves three callers chosen by three tables. The
    reason is stated in §14.3 D-8; it is for the manager to accept or file.

## NOTE ITEMS DISCHARGED

| note item | answered where (span_arms.md) | how |
|---|---|---|
| D-1 ITEM row walks the body | §14.3 D-1 | new T3 row E-5i before E-5, arm `look`; `rb_row_into`/`rb_zero_into` take the mutable walk and the level's slots; only item, body guards and never leave the body |
| D-2 where guards/never live | §14.3 D-2 | `RbRuns` (`lg`, `rg`, `never`); RM-1's `RbRuns` half applies |
| D-3 T4's spelling | §14.3 D-3 | fixed steps of `rr_cat` sharing one meet; ALT one post-step on the existing common head/tail; CAT-SET at the walk exit; `look` restore semantics |
| D-4 TOP, reach, lb_bytes, rn_scan_mass | §14.3 D-4 | combining row table with an arm column; no `reach` parameter; `lb_bytes` a parameter; `rn_scan_mass` ranks over every position (D191.2), its comment rewritten |
| D-5 omin/consumed extent home | §14.3 D-5, D-7 | not on `RbRun`; extent on the walk output and `ReqRun` (facts.h interface); `omin = min(0, K)`, not stored |
| D-6 scan primitive, extent accessor, trace shadow | §14.3 D-6 | RM-4 = `pcrec_run_scan_index(rate, run, lo, hi)`; extent accessor lands with L3; shadow keeps the whole run (not the retired agreement check) |
| D-7 K's representation | §14.3 D-7 | three states + signed value; K alone; `MF_HEAD_MAX_UNBOUNDED` at :1644 |
| D-8 RM-3 parameters, act-through-row | §14.3 D-8 | `(hit, pos, target, K)` with the target-is-the-hit rule; differences stay in callers; re-test through one predicate (F-7); L3's signed table |
| D-9 DEAD propagation | §14.3 D-9 | (a) shared never rows extracted from derive.c; rendering `dead`; no reach into `never_matches` at L1 |
| D-10 the item's form | §14.3 D-10 | (a) SHARED: head column AHEAD, description BEHIND via `ph_alt`; no ND-2; P5 discharged |
| D-11 lb_bytes factor/unit, VLOOKBEHIND stage 2 | §14.3 D-11 | characters at the accessor, ×1/×4 at the filler; no interaction (a backref body has no description) |
| D-12 PCRE2 questions | §14.3 D-12 | NOT answered here by rule (D181): two questions listed below for a pcre2-reader; no design choice depends on them |
| D-13 spec hunk list | §14.3 D-13 | per-unit table by section/paragraph |
| D-14 L2 refreshed | §14.3 D-14, §14.4 L2 | kit scans any position; consumed extent pcrec-internal; precondition met |
| D-15 today column | §14.2 | re-measured at T (C-R2, 29 patterns) |
| D-16 K comments | §14.3 D-16 | three sites (F-1), wording at K < 0, abi event at L3 |

Questions for a pcre2-reader (D181), from D-12: (a) In UTF mode, may a lookbehind read before the start
offset, and what bounds how far (the declared `max_lookbehind`, nested lookbehinds)? (b) Does PCRE2's "last
code unit" start optimisation ever take a unit from inside a positive lookahead?

## MANAGER READINGS TESTED

- **(m1) ruling 2 is answer (a) and what D168, D172, D191.2-3 already said: SUPPORTED.**
  - D168: "come from ONE producer"; "a FIXED-WIDTH POSITIVE lookbehind enters directly".
  - D172: "spans, each with a start offset (negative allowed)"; "Fixed lookbehinds and post-span lookaheads
    longer than 1 come with it, sourced from main's D168 producer".
  - D191.2: "the run crosses as ONE uncut span with byte sets at signed offsets from the attempt start".
  - D191.3: "a run outside the match is ONE run value ... never a second wider fact".
  - The owner's `foobar` at −3 is that one uncut span.
- **(m2) "the match is proved and search is over" describes the existing cover route and adds no new
  requirement to L1-L3: NOT SUPPORTED as worded.** Its second half holds; its first does not.
  - At T the cover route takes `(?<=f)bar` (one-character context) and `foobar`, but NOT `(?<=foo)bar`
    (`RX_DFA_SCAN "unanchored"`, C-R6).
  - So for the owner's own example the proved-and-over ending is not an existing route. It is a later READER
    of L1's item ([CTX-SIDES-PRODUCER], D172's window site, [LOOK-LOCATE]) under §12c's SUFFICIENT and
    OUTPUTS-DETERMINED.
  - It adds no requirement to L1-L3 (§14.5), and it does not change what the feature does, so the stop rule
    does not fire.
- **(m3) §8.2's kit request is delivered by R-38 K38-2 at the current MF_SITE_ABI, so L2's precondition is
  met and only its readiness critic remains: SUPPORTED.**
  - memfn.h (MF_SITE_ABI 29, C-R4) says: "`omin` is measured from the ATTEMPT start and may be negative on
    the run span; head_max is int64_t, the run's position-0 offset; the twin admits by max(K, 0)". Its
    `head_max` text says "SIGNED: with a negative run `omin` it may be negative or 0".
    `MF_HEAD_MAX_UNBOUNDED` is "the stated value "K unbounded"".
  - The loud agreement check is gone (C-R5: 0 hits).
  - It was delivered in §12a's end-state form, not §8.2's text: §8.2 part A's consumed extent was withdrawn
    by D191.2 ("nothing about consumption crosses the seam").

## UNITS AND THEIR ORDER

1. **L1** (go'd). The census comes first (`census_l1.py`; expected movers `xy(?=bc)[bc]c`, `a(?=b)[bc]`,
   `ab[xy][xy](?=(?<=xx)y)[xy]`, `[ac][ac]cc(?<=acc)(?<=cc)d`, `x(?=qr)[pq]r`, the dead rows; it stops if
   empty). Then remodel commits RM-1 and the never rows, then the feature: E-5i, the `look` arm, guards,
   T4 steps, the item (head column plus description), TOP with no rows, the TOP set step, `dead`.
   - Contract: facts_listing §4.1.3. No abi event.
2. **L3** (go'd). The census comes first. Then remodel commits RM-2, RM-3, RM-5, RM-4 (with the `rn_cmp`
   split), then the feature: the BACK row, `lb_bytes`, the consumed extent and its accessor, `omin =
   min(0, K)` on the run span, the signed move and re-ask, the A8 conjunct deleted, three K comments.
   - Contract: match_api §6.3.7¶10, ¶11; tuning §2.41¶1, ¶8b, §2.28¶1; facts_listing §4.1.2¶8b.
   - abi +1 at landing.
3. **L2**, after its one readiness critic (its kit precondition is met). The census comes first. It has no
   remodel of its own (RM-4 and the extent are L3's). The feature is the AHEAD row.
   - Contract: match_api §6.3.7¶6 and tuning §2.28¶1 (the past-the-consumed-end clause). No abi event.

## OPEN QUESTIONS FOR THE OWNER

none. Checked against the record:
- Whether the item has one producer: the owner, 2026-11-18, "The search span the pcrec delivers to kit
  should have "foobar" with starting index -3", with D168's "ONE producer".
- Whether L2 waits on the kit: D191.1, "L2 after the kit's delivery of R-38 plus one readiness critic".
  The delivery is in memfn.h at MF_SITE_ABI 29.
- The lookbehind cap: §12b Q4, "(lookbehind cap = declared lookbehind length): AGREED".
- One run value: D191.3, "a run outside the match is ONE run value, every reader raised together".
- The remodels: the manager's remodel-go call, which already rules them.
- The dead fact's home: the manager's r50 A8 ruling.
- When the cover takes `(?<=foo)bar`: [CTX-SIDES-PRODUCER] and [LOOK-LOCATE] are filed with triggers
  (span_arms §10).

## COMMANDS

All from the worktree root against `8993b8f82` unless named; outputs in
`/var/tmp/pcrec-pcrec/scratch/spanarms7/` (not committed). The design's own list is span_arms.md §14.7
(C-R0..C-R9).
- `git -C /home/pcrec/projects/pcrec/worktrees/spanarms7 rev-parse --show-toplevel` (the worktree path)
- `grep -c "ACCEPTED rev 2.1" docs/design/req_lookaround_arch.md` (1); `grep -n "PROPOSED rev 2.2" docs/design/span_arms.md` (line 3 before the edit); `timeout 60 /home/pcrec/projects/pcrec/build/pcrec --help` (runs)
- C-R0 `git diff --stat 57fcb5737 8993b8f82 -- src memfn/src memfn/include lib cli docs/spec tests/mech/sabotages docs/dev/decisions.md docs/design/span_arms.md` (memfn/docs/requests.md only)
- C-R1 `git grep -n "span_arms E1\|span_arms R1\|span_arms E2" 8993b8f82 -- src/facts/req.c` (7)
- C-R2 `python3 -I probe.py pats.txt > probe_T.out` (29 patterns through the main tree's `build/pcrec -p rx --features all --emit-facts --pattern P`)
- C-R3 `git grep -n -i -E "span_facts|MkCtx|pcrec_span_walk" 8993b8f82 -- src` (0)
- C-R4 `git show 8993b8f82:memfn/include/memfn.h | grep -n -E "^#define MF_SITE_ABI|may be NEGATIVE|negative on the run span|SIGNED: with a negative|MF_HEAD_MAX_UNBOUNDED"`
- C-R5 `git grep -c "req_run_member\|pcrec_req_window" 8993b8f82 -- src` (0)
- C-R6 `python3 -I probe.py pats2.txt > probe_cover.out` (`foobar`, `bar`, `(?<=f)bar`: cover; `(?<=foo)bar`: unanchored)
- C-R7 `git show 8993b8f82:src/gen/emit_dfa.c | grep -n "%lld bytes before"` (3)
- C-R8 `git show 8993b8f82:src/facts/req.c | sed -n '905,914p'`
- C-R9 `git show 8993b8f82:src/gen/emit_dfa.c | grep -n "define PCREC_ARTIFACT_ABI"` (:55, 108)
- `git grep -l pcrec_derive_split_q 8993b8f82 -- tests` (tests/compound/compound_drive.c)
- `scripts/entry VLOOKBEHIND -l 1`, `scripts/entry NEVER-MATCH -l 1`, `scripts/entry DESC-DEAD -l 1`, `scripts/entry CTX-FACTS-NEG -l 1`
- `make -s test-plan-lint` (PASS)
