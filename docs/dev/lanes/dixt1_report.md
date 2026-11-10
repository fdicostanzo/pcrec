# dixt1 — [DOC-INDEX] T1: the levelled accessor, the profile table, the gestalt `docs` row

Lane dixt1 (sonnet), branch lane/dixt1 off main ee25e11b3. BUILD GO: Frank, 2026-11-10 ("Go on build").
Design: docs/design/doc_index_format.md rev 3 §2.3, §2.4, §5 T1, §10 T1; appendix J.

## STATE AT HANDOFF

STATE: delivered. Validation: see "Acceptance" (the codegen/testscripts run is marked below).

### What was built, per section

- §2.3 the accessor: `scripts/entry` (python3 stdlib, `-I`, shebang `env -S python3 -I`). Levels 0/1/2; `KEY`
  routing rows 1-7 (real tags incl. the archive rule: plan wins, 2+ archive rows print all and exit 2); `-g` item
  grep (`-in`, `-l`, `-p`, `-s`, `--state`); `--work` (not-started + blocked at level 1, by section, `-s`, `-k`);
  `--rev SHA` (working-tree table, form by the files at SHA); `--levels`; `--over-cap`; `--selftest`. The plan
  grammar is plan_lint's (`HEAD`, `HEAD_OK`, `ATTR`, `SECTIONS` imported). Exit 0/1/2; trailer
  `entry: <n> items (profile <p>, level <l>)`.
- §2.4 the ONE profile table: `scripts/doc_profiles.py` (PROFILES: decisions/known/upstream DORMANT, plan
  `single`, completed `archive`; FIXTURE_PROFILES for the selftest; KEY_SHAPES shared with PL18).
- Gestalt row: `docs` kind, `L_docs`, `timeout 2 python3 -I "${GESTALT_ENTRY:-$here/entry}" --over-cap`; the
  `docidx` placeholder deleted; the general "an empty line prints nothing under --all" rule replaces the
  idle-held special case; header names `docs`. Silent under cap; `docs: unavailable` on non-zero exit, timeout,
  or missing trailer.
- PL18 in scripts/plan_lint.py (+ plants for `[K50]`, `[D26.a1]`, `[pcre2-compat-tiers]`, `[D26]`, `[U3b]`,
  `[D26.4]`; tests/plan_lint/CLAUDE.md row). 0 real tags match.
- R2-1: scripts/CLAUDE.md 4084 -> 3876 B after moving the `fullsuite_job.sh` parenthesis to scripts/NOTES.md and
  adding `entry`/`doc_profiles.py`. `check_claudemd_size.sh --all` green.
- R2-2/R2-3: scripts/tests/gestalt.test (stubs under `$T/ent/*.py`, J1-J3, a `docs` row case set).
- R2-7: `make test-doc-lint` (tests/doc_lint/run_doc_lint.sh + CLAUDE.md), TEST_SECTIONS + `.PHONY`, recipe's
  first line touches the trailer, tests/ci/shards.tsv row (`test-doc-lint 2 2 ESTIMATED`), tests/lib/
  san_excluded.txt `NO-C-RUN`, tests/CLAUDE.md, docs/testing.md.
- R2-8: monitoring.md step 0 (the main prompt; the kit prompt is "the same with OWNER=kit", so it inherits).
  The manager should read the diff of that prompt. Root CLAUDE.md situation row; docs/dev/CLAUDE.md;
  docs/dev/doc_format.md (§2.6: the format as built).
- History index line for this report (docs/dev/history/claude_md/docs__dev__lanes.md).

### J1-J10: red before, green after (one line each)

| id | red before (how shown) | green after |
|---|---|---|
| J1 | gestalt.test with the old `idle-held`-only skip: `--all` printed 13 lines and an empty line (3 FAILs) | `--all` 12 lines incl. DONE, no empty line |
| J2 | the old gestalt (no `docs` row): the over-cap stub case printed nothing (`FAIL: docs over: []`, row case red) | silent with the under-cap stub; exactly the `docs:` line with the over-cap stub |
| J3 | the old gestalt: exit-3, hang, no-trailer and blank stubs printed nothing (`FAIL: docs ...`) | `docs: unavailable` each; the 5 s hang returns in 2 s |
| J4 | entry copy rounding KB instead of truncating: `51.4 KB (+3.4 KB)` FAIL; pct rounded: `107%` at 52592 B FAIL | 106% / 107% / `51.3 KB` / silent at 49152 B |
| J5 | entry copy where a dormant profile is "not found" rc 0: `FAIL: J5 dormant D26 rc 0, want 1` (and K139) | exit 1 + `entry: profile decisions dormant (unit 1)` (known: unit 3) for D26, K139, D47.a2, `D26 addendum 2` |
| J6 | entry copy where any `- [TAG]` line is an archive row: FIX-2 `rc 2` and `as planned` printed | one row, exit 0 |
| J7 | shards.tsv without the row: `section 'test-doc-lint' has 0 shard rows`; san_excluded without the row: `UNLISTED tests/doc_lint/run_doc_lint.sh`; trailer with no marker: `MISSING - test-doc-lint` | all three structural lists carry the section (check_shards green, test-codegen see below) |
| J8 | entry copy ignoring `--rev`: the working-tree row `CHANGED` served, bogus SHA rc 0 | the plan row AT that commit; bogus SHA exit 1 |
| J9 | entry copy that parses Policy as an item section: `-g '\[ID\]'` rc 0 | the Policy templates are not items (fixture and real plan) |
| J10 | plan_lint with PL18's check disabled: `PLANT NOT DETECTED PL18` x6 | all six id-shaped tags refused; real plan: 0 violations |
| R2-1 | scripts/CLAUDE.md original + the two scripts named: 4242 B > 4096, `check_claudemd_size.sh --all` red | 3876 B green |

Red-before for the entry-side plants is by SABOTAGED COPIES in scratch (the scratch tree is not committed); for
the gestalt plants it is the pre-T1 gestalt run against the new test.

### Acceptance (run in this worktree)

- `make test-doc-lint test-ci-shards test-claudemd-size test-plan-lint`: green (doc-lint 2/2, check_shards 9+13,
  claudemd 359 files within limits, plan_lint 341 rows 0 violations, selftest 38+6 plants, 18 rules covered).
- `scripts/tests/gestalt.test`: 54 pass, 0 fail.
- `scripts/entry --selftest`: 48 checks, 0 failures (via `make test-doc-lint`).
- `make test-codegen`: green (TT-9: 165 run_*.sh found incl. tests/doc_lint/run_doc_lint.sh, planted-defect control flagged all five; 336+41+23+40+7 checks passed, 0 failed).
- `make testscripts`: OWED. Running in the background (it ends with the 600 s boxqueue.test); log /var/tmp/pcrec-pcrec/scratch/dixt1/accept.log, completion line `^rc=` at its end; verdict = make's `*** [...testscripts] Error` lines. gestalt.test (the only testscripts member this change touches) is green standalone, 54 pass 0 fail.
- `make strict`: not run (no C touched).

### Deviations

1. DEVIATION (archive head): the design says an archive row matches plan_lint's HEAD_OK form. HEAD_OK only
   admits the four live states, but plan_completed.md rows carry `STATE:completed`, `completed-in-place`,
   `done`, `delivered`, ... So `entry` uses `^( *)- [TAG] STATE:<any word>` for the archive and still imports
   HEAD_OK/HEAD/ATTR/SECTIONS for the live plan. The J6 shape (a tag on a non-STATE line is body text) holds.
2. DEVIATION (aliases at T1): the design resolves alias spellings through the owner table's `old_label`/
   `old_number`/`date`; that table is unit 1.0. T1 resolves them from the details file's `### Dn.aN` headings
   and `(was: "...")` lines (fixture-tested); the real decisions profile is dormant, so only the dormant
   behaviour is live.
3. `later:` (level 1, decisions) is computed from mentions in the other details entries with the supersede/amend
   verb list; it will be re-based on the owner-table attribution in unit 1. Fixture-tested only.
4. `-g` defaults to `-l 0` (design silent); `entry` KEY defaults to level 2.
5. `docs/dev/doc_format.md` is the rules as built (the design §2.6 says "without census or migration"); it is a
   short rewrite, not a copy of §2.
6. The `kit` profile (§8.1) is NOT added to the table (not in T1's list; it waits for the kit's conversion).

### Help text of scripts/entry (`scripts/entry -h`)

```
scripts/entry -- the levelled accessor for tracker files ([DOC-INDEX], D192; docs/dev/doc_format.md).

    scripts/entry KEY [-l N] [--rev SHA]     one item; default level 2
    scripts/entry -g REGEX [-in N] [-l N] [-p PROFILE] [-s SECTION] [--state S] [--rev SHA]
                                             item grep: match each item at level -in (default 0), print it whole
                                             at level -l (default 0). The archive is read only with -p completed.
    scripts/entry --work [-p PROFILE] [-s SECTION] [-k WORD]
                                             plan: every not-started and blocked row at level 1, by section
    scripts/entry --levels [-p PROFILE]      the level and work-view rows of the profile table
    scripts/entry --over-cap                 soft-cap line for scripts/gestalt (docs/dev/doc_format.md)
    scripts/entry --selftest                 planted fixtures: one per routing row, dormant, over-cap, --rev
    Levels: 0 the index line(s); 1 + the working fields; 2 + the full entry.
    Output ends `entry: <n> items (profile <p>, level <l>)`; exit 0 found, 1 none, 2 ambiguous.

The profile table is scripts/doc_profiles.py; the plan grammar is scripts/plan_lint.py's (imported, never a
second parser). Read-only; the root is the repository this script lives in, so the cwd does not matter.
```

### Owed / for the manager

- Read the monitoring.md diff (both prompts); the kit prompt inherits by "the same with OWNER=kit".
- The `docs` row prints nothing on today's tree (0 pair indexes); `entry --over-cap` says so in its trailer.
- No hook, no `make hooks` re-install in T1 (the hook rules arrive with unit 1).
