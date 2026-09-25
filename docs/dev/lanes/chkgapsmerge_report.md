# chkgapsmerge — landing lane/chkgaps onto main (2026-09-25)

Branch `lane/chkgaps` (tip before this work: `6629a658`), rebased onto main
`5a2094e7` (which now carries K64 FIXED via lane `k64fix`, merge `ce658cb7`,
abi 33). Task: rebase, resolve conflicts, reconcile the two lanes' shared
territory, validate, report — never merge (the manager merges).

## What conflicted, and why

Both lanes touched the same three files for related-but-distinct reasons,
because both were answering "how do we get standing coverage of K64" at the
same time from opposite sides (chkgaps: close the check-design gap that hid
it; k64fix: fix it).

1. **`tests/mech/run_sabotage_matrix.sh`** (the arm-registration comment
   block) — both lanes appended a new arm entry at the same point: main's
   `recidentity` (lane `varland`, unrelated — the [VAR] M6 seam-rename
   bucket) and chkgaps' `clsfold`. Resolved by keeping both, chkgaps'
   appended after main's; updated chkgaps' own "registered before S273"
   line to "before S275" since S273 was taken on main.

2. **`tests/rxtsource/run_rxtsource_tests.sh`** (the `CENSUS_*`/`RUNSH_*`
   pins) — both lanes added corpus content and re-pinned the same four
   variables. Resolved by layering chkgaps' delta on top of main's
   already-advanced pins (main had moved to 217/4001/29129 via k64fix +
   varfollow since chkgaps branched at 216/3999/29120). See "Retirement"
   below for why this delta was reverted in a follow-up commit.

3. **`tests/codegen/run_prechecks.sh`** — both lanes added a new numbered
   section at the same point after §5.5, both calling it "§5.6": main's
   K64-fix-A control (the ANCHORED witness, sabotage S274) and chkgaps'
   forced-VM positive control (the UNANCHORED witness, then-sabotage
   S273/renumbered S274/renumbered again S276 — see numbering below).
   Resolved by keeping main's as §5.6 (it landed first, chronologically,
   and is cited by known_issues.md K64's own text) and renumbering
   chkgaps' section to §5.7, including its internal variable names
   (`S56_*` → `S57_*`) and check labels (`[5.6]` → `[5.7]`). Both sections'
   `if`/`fi` nesting had to be manually reconstructed after the textual
   merge dropped one `fi` — caught by `bash -n` before committing.

4. **`tests/mech/CLAUDE.md`** (two more conflicts, same shape as #1: both
   lanes appended prose about their own new sabotage row at the same
   point). Resolved by keeping both blocks and correcting chkgaps' cross-
   references (S274→S276, §5.6→§5.7) in the kept copy.

5. **`docs/dev/known_issues.md`, `docs/dev/lanes/CLAUDE.md`, `tests/codegen/
   CLAUDE.md`** auto-merged cleanly (non-overlapping hunks); read after the
   fact for correctness, see "Prose reconciliation" below.

## Sabotage numbering

chkgaps had already renumbered its two new rows S273→S275 (cls-fold) and
S274→S276 (precheck-admit-unanchored) per an earlier team-lead ruling,
avoiding a collision with S273 (lane `varland`, unrelated: a `vm_bref`
off-by-one) and S274 (lane `k64fix`: the K64 fix's own answer-detectable
row) that had landed on main in the interim. The rebase replayed that
renumber commit cleanly on the file-identity level (git tracked it as a
rename); the two conflicts above were both in the COMMENT PROSE describing
the renumbered rows, not in the numbering itself.

**S275 required no changes** — its target (`src/gen/emit_vm.c`'s
`vm_cls_test`) was untouched by any main commit since chkgaps branched.
Verified DETECTED unchanged: `clsfold:78fail/85pass`.

**S276 needed re-anchoring**, and this was the one real mechanical
casualty of the two lanes touching the same function. Its target,
`req_route_one_attempt` (`src/gen/emit_dfa.c`), is the exact function
k64fix's fix A rewrote — from a one-line `return start_anchor != NONE;`
to a two-conjunct expression adding the linearity test. chkgaps' S276
anchored on the pre-fix one-line body, which no longer exists in the
tree; a solo mech run immediately after the rebase read
`ANOMALY (anchor drifted from HEAD)` rather than a false DETECTED or
UNDETECTED — the check-design discipline this house's own
`tests/mech/sabotages/CLAUDE.md` asks for (a stale anchor must be loud,
never a silent pass) worked exactly as documented.

Re-derived from `git show HEAD:src/gen/emit_dfa.c`: the plant now drops
BOTH the `start_anchor` conjunct and K64 fix A's own linearity conjunct
(collapsing the VM arm's `return` to an unconditional `true`), preserving
S276's original intent — every VM route admitted as one-attempt,
anchored or not — against the current two-conjunct source. This shares
its anchor text with S274 (both target the same function's `return`
statement) but plants a disjoint `AFTER`, which is fine and precedented
in this tree (S102/S165 share an anchor the same way) since each
sabotage builds its own independent scratch tree from `git archive HEAD`.

**Re-verified after the fix, tree `4106b318`:**

    S275  DETECTED  clsfold:78fail/85pass
    S276  DETECTED  prechecks:10fail/250pass
    S274  DETECTED  prechecks:2fail/260pass, corpus:4fail/5pass   (main's
                     own row, re-run in the same tree to confirm the two
                     rows sharing an anchor don't interfere with each
                     other's scratch builds)

`scripts/m6read_check_sab_anchors.py`: 284 sabotages / 300 anchor sites,
all resolve.

## Retirement: chkgaps' `tests/known_fail/k64_precheck_forced_vm.rxt`

chkgaps landed this file as standing known-fail-ratchet coverage of K64
BEFORE the bug was fixed (its own header says so: "closes when K64's fix
... lands"). k64fix landed its OWN regression at the same basename,
`tests/base/k64_precheck_forced_vm.rxt` (a normal, PASSING corpus file,
since the fix makes it pass), covering the identical witness pattern
(`^([a-zA-Z0-9._%+-]+)+@`, `--engine=vm`, `budget steps=10000`) plus MORE:
a second frameless-arm block, and a `gu` control proving the budget really
reaches the VM. Diffed both files directly (not just compared sizes) —
k64fix's is a strict superset of chkgaps' population.

Keeping both would assert the identical claim twice from two directories
with different meanings (one says "this fails, expected"; the other says
"this passes, and here's why it's allowed to"). Retired chkgaps' copy
(`git rm`), re-pinned `tests/rxtsource/run_rxtsource_tests.sh`'s census
back down to 217/4001/29129 (the value it already carried on main before
chkgaps' addition — the two lanes' net contribution here is +0/+0/+0),
and rewrote `tests/known_fail/CLAUDE.md`'s entry as GONE, following the
`k34_leftrec_giveup.rxt` precedent already in that file (state what it
was, why it's gone, where the surviving coverage lives).

**chkgaps' other three closures are UNAFFECTED and stand on their own** —
none of them depended on K64 being open:

- Gap 2 (`tests/axes/dump_diff.awk`'s `GIVEUP1` bucket, `run_axes.sh`'s
  promotion of it to a failure) closes a REACH gap in the axes battery
  itself, independent of any one bug.
- Gap 3 (mech's `encoding` arm scoring against a clean-tree baseline)
  closes a scoring defect in the mech driver, unrelated to K64 in cause.
- Gap 1's SECOND half, `run_prechecks.sh` §5.7 (renumbered from chkgaps'
  own §5.6) and sabotage S276, is a positive control for the UNANCHORED
  population G2's admission rule was never checked on — deliberately NOT
  K64's own (anchored) population, so it needed no dependency on the fix
  landing and needs none now that it has.

## Prose reconciliation

`docs/dev/known_issues.md` K64's closing paragraph read "**Both check gaps
CLOSED 2026-09-25 (lane chkgaps), the bug itself still open**" — true when
chkgaps wrote it, stale the moment k64fix's fix A merged (K64 is now
marked FIXED at the top of the same entry, from main). Rewrote the
paragraph to name its two K64-relevant closures (gap 1's prechecks
differential, now §5.7/S276 after renumbering, and gap 2's axes GIVEUP1
bucket) and record the known_fail retirement with a pointer to this
report. **A first pass at this rewrite over-corrected**: it folded
chkgaps' gap 3 (mech's `encoding` arm clean-tree baseline, S229/S-U8) —
unrelated to K64, a separate scoring defect found the same session — into
K64's own entry, miscounting "two" as "three". Caught on review and fixed
in a follow-up commit; K64's entry now names exactly the two closures that
are actually about K64's own shape. Gaps 3 and 4 (the encoding baseline
and the class-fold agreement check) are recorded only in
`tests/mech/CLAUDE.md` and `tests/codegen/CLAUDE.md`, where they belong.
`tests/known_fail/CLAUDE.md` got the retirement treatment (see
"Retirement" above).

## Validation

- `make -j4 CC=gcc-16`: clean (no `src/` changes in this merge beyond what
  each lane already built and validated separately).
- `make strict CC=gcc-16`: clean.
- `bash tests/known_fail/run_known_fail.sh`: "tests/known_fail/ is empty
  ... nothing to ratchet" — matches main's pre-chkgaps state exactly.
- `bash tests/rxtsource/run_rxtsource_tests.sh`: 214 passed / 0 failed / 1
  recorded (darwin's own pre-existing non-native-pin note), census
  reconciles at 217/4001/29129 — matches main's pre-chkgaps pin exactly,
  confirming the retirement is byte-for-byte net zero.
- `bash tests/codegen/run_prechecks.sh`: 262/0 — both §5.6 (main) and
  §5.7 (chkgaps) pass; §5.6r's control rows and §5.7's own four checks
  all green.
- `bash tests/codegen/run_cls_fold_agreement.sh`: 163/0, unchanged.
- Sabotage rows: S275, S276, S274 all re-verified DETECTED (figures
  above); `scripts/m6read_check_sab_anchors.py` green (284/300).
- `python3 scripts/m6read_check_sab_anchors.py` and the four targeted
  scripts above are the FILES this claim covers (BOILERPLATE's own rule:
  name the exact file a "re-ran standalone, clean" claim covers).
- Full `make test CC=gcc-16`: launched detached
  (`nohup ... > build/chkgaps_test.log 2>&1 & disown`) as this lane's
  last act per BOILERPLATE's DO-THEN-FINISH — this box's one-heavy-suite
  slot for the session; `make test-axes` deliberately NOT run (team-lead
  brief item 3). Verdict OWED at hand-off; poll
  `worktrees/chkgaps/build/chkgaps_test.log` for `*** [test-X] Error`
  lines (the real verdict) or the `sections ran: N/M` completion
  trailer. The one KNOWN pre-existing darwin red across every prior
  lane's report on this box is `tests/codegen/run_inline_capability.sh`'s
  `nm arm_a.o` probe — unrelated to anything in this merge.

## Not merged

Per the brief, this branch is NOT merged to main. Tip: see `git -C
worktrees/chkgaps log --oneline -1`. The manager merges after reviewing
this report and the `make test` verdict.
