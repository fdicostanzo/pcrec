# [M5.0] CLOSE-OUT RITUAL — lane m5close report

2026-09-12, sonnet tier, worktree `worktrees/m5close`, branch `lane/m5close`.
On Frank's word 2026-09-12 ("sidecar the m5 closing") + the standing GO
(2026-09-06, "continue through to M5.0 completion"). Docs-only delivery:
nothing under `src/`/`tests/` touched, per the brief.

## 1. Compliance-refresh (task 1)

Ran the `compliance-refresh` skill's procedure. Built this worktree's own
`build/pcrec` first (`make -j4 CC=gcc-16`, clean).

**Component 1 (generated construct index) and component 3 (keyed
annotations) needed NO edit.** Before touching anything, ran the checks
cold and all four passed against the tree as-is:

- `--check`: PASS, 138 rows, matches the dump
- `--names`: PASS (12 distinct modules; OUT-OF-SCOPE/ROADMAP_NEVER agree,
  17 verb names; 0 ROADMAP_NEVER rows)
- `--check-annotations`: PASS, 91 annotation keys (40 registry, 51 base),
  21 blocks match the store
- `--tension`: informational, ran clean (no crash; the usual placeholder
  gaps like `(?n)` standing in for `(?0)`..`(?9)`)

This surprised me going in — the brief expected the \p/\P and
encoding-related rows to move. They didn't, because the last compliance
touch (`9bbdc0f9`, itself part of the utf8s5 lane's own WIP work) already
covered stage 5's script-row content, and neither K53-SELRETRY's fix nor
[ORACLE-LINK]'s dlopen retirement changed anything `--list-syntax` reports
(`\p{...}` was already a registered, `built` construct since MOD-0.6's
recogniser; K53 is an engine/resource issue, not a grammar-recognition
one, so the dump never moved).

**Component 2 (the hand-written survey prose) WAS stale.** The
"Unicode properties" section's narrative (added at stage 3, `9a1583ba`/
`d69ef05f`/`11929d96`/`9bbdc0f9`) described K53 as an unresolved,
permanent blocker — "SIZE turned out to be a real blocker for five of
the 45 names under `--encoding=utf8` at default axes" — with no mention
that K53-SELRETRY (`6effd93a`, 2026-09-10) fixed it. Corrected in place
(`docs/pcre2_compliance.md`, ~15 lines added after the existing K53
paragraph): states the fix, the mechanism (the optional-contributor
drop ladder, `RX_ENGINE_SEL "size-cap-retry"`, no abi bump), the measured
number (`\p{L}` 772,418 bytes where it refused at 1,076,638), and the
report's own finding that the corpus population the fix actually reaches
is pcrec-bench's `altwide` witnesses, not the `\p` family (the codegen
census compiles corpus `pattern` lines with no encoding, so the `\p`
rows are Latin-1-clamped there).

Re-ran all four checks after the edit — still clean (`--check` 138 rows,
`--check-annotations` 91/21, `--names` clean, `--tension` clean). The
edit is prose outside the generated annotation blocks, so it could not
and did not perturb the render-drift checks.

**Validation**: `make test-registry` (`tests/registry/run_registry_tests.sh`
— registry_check, compliance_section.py, PC-3, PC-4, definitions-oracle)
run to completion in the background (the box was under contention from
lane rxtnul's concurrent `make test`, which is why a first foreground
attempt hit a 120s timeout; re-launched via `nohup timeout 900` and
polled with Monitor rather than blocking). **Fully green**: PC-3
209/0 failed (libpcre2 10.48 via pkg-config), PC-4 273 patterns / 62,872
match cells / 0 disagreements, the 1:n fold arm 22/0, registry_check's
five sub-phases each `checks failed: 0` (248/763/872/898/989 in the log),
definitions-oracle 354 cells / 101,244 A==B / 101,244 A==C / 0
disagreements. Log: `build/m5close_test_registry.log` (not committed —
build artifact).

## 2. Plan row completion (task 2)

Moved `[M5.0]` from `docs/dev/plan.md` (was `STATE:started`, line 217, a
single ~15.5 KB line) to `docs/dev/plan_completed.md` under a new
`## Completed 2026-09-12` heading, verbatim — every character of the
original row preserved, including its internal per-stage progress
markers — with exactly two changes: `STATE:started` → `STATE:completed`,
and one bolded completion stamp appended at the very end (matching the
row's own established convention of appending each new development in
bold as it landed), citing: stage-5 validation discharged 2026-09-11 via
I-65 (all six S5-ARM stages green at pin `616c2e49` on ubuntubudu; san
35/35; `uprops_utf8` `[STORE]` 387/387 exact; PC-4 62,872 cells 0
disagreements), the compliance-refresh finding (components 1/3 unmoved,
component 2 corrected), the plan move itself, and the journal entry.
Confirmed `grep -n "^\- \[M5.0\]" docs/dev/plan.md` now returns nothing —
the row is fully gone from the active plan, no partial/duplicate copy.
`grep -c "STATE:completed" docs/dev/plan_completed.md` reads 180
(179 before this change).

## 3. Milestone journal entry (task 3)

Appended `## 2026-09-12 — [M5.0] MILESTONE CLOSED (lane m5close,
close-out ritual)` to the end of `docs/dev/dev_journal.md`: what shipped
(all five stages with their merge commits, the two boundary-correctness
engine fixes K49/K50-BNDSTART and K53-SELRETRY sequenced around them, and
[ORACLE-LINK]/[S5-ARM]'s load-bearing infrastructure fixes), the
validation record (the I-65 discharge with its numbers), this session's
own work, and what the milestone leaves open (pointers only —
[CLS-TREE]'s design note/panel, [UTF-PAT], [UTF-RW], [K50-NULLGATE],
[XARCH], U16/S-U12). Every commit hash and number cited was read from
`git log`/the existing plan row/lane reports, not invented — cross-checked
against `docs/dev/lanes/CLAUDE.md`'s existing per-lane summaries and
`git log --oneline` for the exact merge SHAs (f22b65c4, 05b2fe8a,
819ec889, 83f7175b, 0b21c32f, 9d37356d, 8e0fe77f, 6effd93a).

## Validation summary

| check | result |
|---|---|
| `--check` (component 1) | PASS, 138 rows, before and after |
| `--names` (component 2 module references) | PASS |
| `--check-annotations` (component 3) | PASS, 91 records / 21 blocks, before and after |
| `--tension` | clean, informational |
| `make test-registry` | **GREEN** — PC-3 209/0, PC-4 62,872 cells/0 disagreements, registry_check 5 sub-phases all `checks failed: 0`, definitions-oracle 354 cells/0 disagreements |

**Nothing OWED.** The brief's validation bar (`tests/registry/
compliance_section.py --check-annotations` and `make test-registry` at
minimum) is fully discharged, not partially — the box contention only
cost wall-clock time (background + Monitor rather than a blocking
foreground call), not scope. No full `make test` was run, per the
brief's explicit instruction (lane rxtnul's suite was occupying the box);
that full battery is the manager's at merge, as for any docs+annotations
change.

## Rulings received

None — no mid-flight questions arose. The brief's own instructions
(skip the full suite, run test-registry at minimum, background+Monitor
for anything over ~2 minutes) covered every decision point this lane hit.
