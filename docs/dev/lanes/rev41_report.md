# rev41 — R17-b′ design note REVISION 4.1 (lane rev41, 2026-10-21, docs only)

Branch `lane/memfn-rev41`, cut from `lane/memfn-b4`. Nothing under `src/`, `memfn/src/`,
`tests/` or `lib/` changed; no make, no compile, no timing. Sections are cited by number
(no line cites).

The task: apply three settled answers to rev 4's §7.3 questions. The rulings' text is in
`memfn/docs/journal.md` (2026-10-21) and the two 2026-10-21 notices at the end of
`memfn/docs/responses.md`.

## 1. Each edit, by section

Everything below is in `docs/design/memfn/r17b_prime.md` unless a file is named. Changed
text is marked `[rev4.1]`; superseded rev 4 text is struck through or noted, never deleted.

### Q-R17P-26 (Frank): a set site's form by its cover's TERM COUNT

| edit | section |
|---|---|
| Header paragraph for rev 4.1; "read §R4.1 first" line | the top of the file |
| §R4.1, the change list (change, rev 4, rev 4.1, where) | new section before §R4 |
| §0 item 2: the "R7 only where the shape has a measured key" bullet struck and replaced; the `[rev4]` R0 bullet re-pointed at the term-count rule; the §0 step table's B4 row | §0 |
| §R4's rows for the default, R0 and R7 gain strikes and notes | §R4 |
| Rev 3's rows 16 and 17 (R7, R7w) and the "R7 is gated on a measured key" note are marked superseded | §1.3 |
| R7 (row 12): fact is the cover's term count ≤ 2; the nine shape keys are in the evidence column and no row reads them; `basis` is UNMEASURED-DEFAULT by the self-check's rule (R7 reads no key, as D1), the constant 2 labelled in place (D149) | §1.3a row 12 |
| R7w (row 13): reached for ONE reason (≥ 3 terms); the "measured-loss / unmeasured" bullets struck; the no-cover case (no V1 form to route to) stated; how the rule is held honest | §1.3a row 13 and notes |
| The R0 note's "R7's per-shape comparator" sentence re-pointed at the count | §1.3a notes |
| The §1.8 row-edit log sentence names rev 4.1's edits | §1.8 |
| §1.9 default table: the row naming Q-R17P-26 replaced (an untimed combination routes by its count); the "winning shape" / "measured V1 LOSS" rows restated by term count; the "what the default costs" paragraph | §1.9 |
| B4's row in the step plan and the B4 gates column | §3.1 |
| The 54 no-key sites: now route by term count, split OWED to the regenerated manifest (NOT computed); the 586 is a floor, not an upper bound; the R0 population's losers are all ≥ 3 terms | §3.5 |
| The manifest item says where the 54's split is owed | §3.1a item 4 |
| B4's acceptance CONFIRMS the rule on the shapes it moves; a contradicting shape is a FINDING | §9.2 item 2, §9.4 |
| Expected-loss rule's population (1) restated by term count | §9.2a |
| Prediction covers every ≤ 2-term cover; ≥ 3-term covers carry none (zero-mover) | §9.3 |
| Sabotage: SN-8 re-aimed at the term-count comparator (witness: a (0,3,0) cover, 3 terms); S917's witness note | §8.3 |
| Standing question 1 and 3 bullets (a regenerated default set no longer moves R7's verdicts) | §10 |
| F25 re-ruled; new F32 ("not timed" is not "unknown" when the deciding fact is static and the trend monotone) | §11 |
| §5.2a evidence rows say "evidence for the term-count rule; no row reads these keys" | §5.2a |
| §7.3 Q-R17P-26 marked ANSWERED (answer quoted, source named, question text left) | §7.3 |

### Q-R17P-27 (Frank): YES, F2 defaults to V1 at B5

| edit | section |
|---|---|
| "a density condition, still open" replaced by the ruling in F2's row; E drops out of `needs`; g = 2 cells named an expected loss in the evidence column | §1.3a row 1 |
| Rev 3's F2 row marked superseded | §1.3 row 3 |
| §0 item 2's "F2 gains a density condition" bullet struck and replaced | §0 |
| The gap-grid item no longer gates F2 (it still locates libc's crossover) | §3.1a item 6 |
| B5 row: F2 built with NO density condition; B5 item (c) | §3.1 (B5) |
| Routing list: "F2 at B5" | §1.6 |
| §1.9 table: VM hat row | §1.9 |
| The g = 2 cells named EXPECTED losses up front, scored at B5 (B4 does not move the VM hat) | §9.2a |
| F30 note, the "F2's cells" row | §11, §5.2a |
| §7.3 Q-R17P-27 marked ANSWERED | §7.3 |

### Q-R17P-28 (kit manager): P1 recorded as fired on the letter, NOT built

| edit | section |
|---|---|
| P1's row: "NOT BUILT"; the "whether to build at B5" sentence struck and replaced by the ruling | §1.4 |
| §R4's P1 row | §R4 |
| B5 item (d): P1 is NOT built | §3.1 (B5) |
| The B5 deny row: `fd-pres-priced` is not added; B5 floor is +1 (`fd-vm-hat-1b`) | §3.4 |
| M23's "read by" cell; S978 declared UNREACHED | §5.2a, §8.3 |
| §7.3 Q-R17P-28 marked ANSWERED | §7.3 |

### Housekeeping

| edit | file |
|---|---|
| Charter checklist for rev 4.1 | `r17b_prime.md` §12 |
| rev 4.1 bullet in the r17b_prime entry; the rev 4 "F2 needs a density condition" line annotated | `docs/design/memfn/CLAUDE.md` |
| a paragraph on the stale predicted-mover manifest | `docs/design/memfn/r17b_prime/CLAUDE.md` |
| this report's index entry | `docs/dev/lanes/CLAUDE.md` |
| four rows (R7, R7w, F2, P1) in the row-edit log | `memfn/docs/finder_history.md` |

## 2. What I could not apply as stated, and the choices I made

Nothing was impossible. These are judgment points inside the instructions:

1. **The threshold's home.** The ruling says "term count, a compile-time fact". The table's
   convention is that thresholds are set keys. I kept the constant `2` as a literal in R7's
   row, labelled in place (D149) as a trend over nine timed shapes, and set R7's `basis` to
   UNMEASURED-DEFAULT by the same self-check rule D1 uses (a row that reads no key). I did
   not invent a derived key. If the kit manager prefers a derived `kit.terms.V1.WALK.max`
   read from the nine keys, it is a one-row edit.
2. **Term counts of the losers.** The ruling says "-13/-41/-46% at 3". By the shape
   notation (RANGE, EQ, CUBE), (2,0,1) is 3 terms but (3,1,0) and (3,0,1) are 4 each. The
   rule ("3 or more") is unaffected; the note records 3, 4 and 4.
3. **W64 (B6).** The rule is V1's (grid2 timed V1 against the walk). I did not extend it to
   the W16/W32 form; §1.3a row 12 says B6 decides that form's own condition.
4. **The 54 sites.** Not computed, per instruction: the split is stated as OWED to the
   regenerated manifest in §3.5, §3.1a item 4 and §9.2a.
5. **`memfn/docs/finder_history.md`.** Not in the brief's file list, but §1.8 says a row
   edit is logged in the commit that makes it, and rev 4 did so. I appended four rows.
6. **F2's `needs`.** Dropping the density condition removes E from F2's `needs` (rev 3 had
   P,A); stated in row 1.

## 3. Charter vs delivered

| brief item | status |
|---|---|
| Read BOILERPLATE, memfn/CLAUDE.md, the rulings (journal + two notices) | done |
| Worktree `worktrees/rev41` on `lane/memfn-rev41` from `lane/memfn-b4`; first command printed the toplevel | done |
| Q-R17P-26: R7 on term count; per-shape keys kept as evidence | done (§1.3a row 12, §5.2a) |
| R7w loses its "shape with no key" reason | done (§1.3a row 13) |
| §1.9 default-table row naming Q-R17P-26 | done |
| §1.3a rows | done |
| The decision table around "a set site whose shape has NO measured key" | done (§1.9) |
| §9.2a and the movers/population text; 54 sites route by term count, split OWED | done (§3.5, §9.2a) |
| B4's acceptance confirms the rule; a contradicting shape is a finding | done (§9.2, §9.4) |
| The row table stays a declared first-match table | done |
| Q-R17P-27: F2 defaults to V1 at B5, g = 2 cells named expected losses; replace "density condition, still open" everywhere | done (F2 row, B5 row, §1.3a, §7.3, §9.2a, the gap-grid item) |
| Q-R17P-28: P1 recorded as fired, not built; update P1 rows and B5 item (d) | done |
| Each §7.3 question marked ANSWERED, text left | done |
| Rev 4.1 header line and §R4.1 change list near the top; changed rows marked `[rev4.1]` | done |
| Superseded rev 4 text struck or replaced with a note | done |
| No line-number cites | done (diff scanned) |
| CLAUDE.md entries: docs/design/memfn/CLAUDE.md, r17b_prime/CLAUDE.md, lanes index | done |
| This report | done |
| DOCS ONLY: no make, compile, timing | done |
| NEVER cd; absolute paths and `git -C` | done |
