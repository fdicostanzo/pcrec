# landing — the two [OPT-5] STEP 2 union-battery LANDING-BAR fixes

Lane `landing` (2026-09-02/03), branch `lane/landing`. Two test-script-only
fixes found by the union battery's test stage on the [OPT-5] STEP 2 merge
(main `de32a4b`). Nothing under `src/`.

## Commits

- `04e2279` — tests/rxtsource: re-pin the corpus census for [OPT-5] STEP 2's
  two files
- `87c2d6c` — tests/codegen: fix K24 control's grep -c/|| interaction
  dropping its count

## FIX 1 — the corpus census pins

**Cause**, verified by reading the two new corpus files directly (not
just trusting the battery log's truncated numbers): lane opt5i added
`tests/base/start_pinned_startpos.rxt` (4 blocks / 79 lines) and
`tests/assertions/start_pinned_startpos.rxt` (1 block / 16 lines) — 5
blocks / 95 lines across 2 files — without moving
`tests/rxtsource/run_rxtsource_tests.sh`'s pins.

**Pins moved:**

| pin | before | after |
|---|---|---|
| CENSUS_FILES / BLOCKS / LINES | 189 / 3320 / 26799 | 191 / 3325 / 26894 |
| RUNSH_FILES / BLOCKS / LINES | 188 / 3317 / 26788 | 190 / 3322 / 26883 |
| C3_PASS | 13201 | 13280 |
| C3_SKIP | 13509 | 13525 |
| C3_SKIP_OWNORACLE | 10274 | 10290 |
| every other C3_SKIP_* reason | unchanged | unchanged |

The PASS/own-oracle split (+79 / +16) is uneven and traced to its cause
rather than assumed: `tests/base/start_pinned_startpos.rxt`'s 79 lines are
ordinary python-expressible patterns and land in PASS; `tests/assertions/
start_pinned_startpos.rxt`'s 16 lines (a `\bx*` pattern) land in
own-oracle — not because `\b` is python-inexpressible (`tests/assertions/
CLAUDE.md` states `\b` is python-verified cell for cell) but because
`declares_own_oracle()` in `tests/harness/verify_rxt.py` exempts every
file under a directory that carries its own `verify_*.py`, and
`tests/assertions/` has `verify_pcre2.py` — so the whole file is skipped
regardless of the individual construct.

**Flagged, not fixed (out of scope for this brief):** the header's "run.sh's
own population 178 files / 3,262 blocks / 26,680 lines" line was already
wrong before this move — it does not equal census minus known_fail (which
is 190/3,322/26,883, matching RUNSH_*, the values the code actually checks
against). Left a dated note pointing at it in the script; someone should
re-pin that prose line in a separate change.

**MEASURED (post-`.lift`, `bash tests/rxtsource/run_rxtsource_tests.sh`):**
94 checks passed / 0 failed (95th `PASS:` line is the closing summary
echo, not a counted check). Every C1/C2/C3 line PASS, including:

```
PASS: census: 191 files / 3325 blocks / 26894 expectation lines (matches the pin)
PASS: file list: 191 files (the population every leg below reads)
PASS: denominators reconcile: census 191/3325/26894 minus known_fail's 1/3/11 = run.sh's 190/3322/26883
PASS: rxtsource: INV-COMPAT holds over 191 files / 3325 blocks / 26894 expectation lines
```

No FAIL lines anywhere in the run.

## FIX 2 — the K24 control's grep -c / || bug

**Cause**, sharper than "harmless today": `grep -c` exits 1 (not 0) when it
counts zero matches, and **zero accessor calls is the SUCCESS value this
check wants** — a fully de-sugared control has none left. So the old
`|| echo 999` fired on every PASSING run, not only failing ones, making
`k24_left` the two-line string `"0\n999"`. The later
`[ "${k24_left:-999}" -ne 0 ]` then errored ("integer expression
expected") on that multi-line value and evaluated false either way,
silently skipping the K24 control's accessor-count assertion — on every
green run, not just some.

**Fix:** split extraction failure from the count. Only a failed `body`
extraction now sets `k24_left=999`; the grep's own exit status is
discarded (`|| true`), so `k24_left` is always exactly one integer.

**MEASURED (post-`.lift`, `make test-codegen`):** `run_group: 5/5 scripts
passed`, 109+31+22+32+7 = 201 checks passed / 0 failed across
`run_codegen_tests.sh`, `run_dfa_stamps.sh`, `run_offset_skip.sh`,
`run_size_term.sh`, `run_trie_identity.sh`. The K24 check itself:

```
PASS: [K24]: rx_search stays monolithic at -O2 under noclone, and the
de-sugared, attribute-stripped control DOES split (1 clone(s)) — the
partial-inlining pass is live, so this is not a vacuous green.
```

`1 clone(s)` in the control confirms the accessor-count assertion actually
ran (the pre-fix bug would have skipped straight past it silently). No
"integer expression expected" anywhere in the log's stdout or stderr.

## Process note: a main-tree scope violation, caught and closed

Both files were first edited in the MAIN tree by mistake (`/home/duxevents/
pcrec/tests/...`) instead of the `worktrees/landing/` worktree, violating
the scope mandate. Caught before any commit (via `git status --short` in
both locations), corrected by copying the edits into the worktree and
`git checkout --`-reverting the main tree. Exact timestamps (from this
session's own transcript): first write to `tests/rxtsource/
run_rxtsource_tests.sh` 20:00:57 EDT, first write to `tests/codegen/
run_codegen_tests.sh` 20:02:33 EDT, revert completed 20:02:53-54 EDT — full
account given to the manager on request. The manager's journal (`aa89550`)
records the incident closed: san's codegen run on the battery was
unaffected (109/0). Skill guidance updated (§3: verify the worktree path
before the first edit) as the generalizable lesson.

## Delivery status

Both scripts green, both fixes committed, worktree clean apart from this
report. Ready to merge.
