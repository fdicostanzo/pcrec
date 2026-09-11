# pyrole — C3's three-way verdict

Lane `pyrole`, 2026-09-10/11. Branch `lane/pyrole`, parked (worktree at
`worktrees/pyrole`). Redesigns `tests/harness/verify_rxt.py`'s C3 tier to
Frank's ruling (2026-09-10): python `re` is the historical base-tier oracle
(D4) but PCRE2 is the compatibility target (D26), so a python-vs-expectation
disagreement is "interesting, not actionable" by itself — python's one
remaining actionable value is INDEPENDENCE from the `.rxt` expectations
(most of which were themselves written FROM libpcre2 answers), which makes
a disagreement a transcription-error tripwire only where python ALSO
disagrees with a real PCRE2 answer.

## Deliverables

1. **`docs/design/c3_three_way.md`** — the design note: the verdict table,
   the store-consultation flow, the INFO/STOREUNCOVERED bucket definitions,
   the `# pcre2-only` marking recommendation, and what a future
   python-version bump does.
2. **Implementation** — `tests/harness/verify_rxt.py` (the three-way
   verdict logic, `_verdict_match_at`/`_verdict_captures`, `run_supervised`
   aggregation) and `tests/rxtsource/run_rxtsource_tests.sh` (the two new
   `C3_INFO`/`C3_STOREUNCOVERED` pins, the reconciliation formula).
3. **The store capture** — `tests/rxtsource/build_c3_store.py`, committed
   to `oracle_store/libpcre2-10.48/{match-at,captures}.tsv` (7 questions).
4. **Validation**: before/after `verify_rxt.py`/`run_rxtsource_tests.sh`
   runs, a sabotage check, a unit check of the store-uncovered fallback.
5. **`docs/dev/upstream_issues.md` U17** — the citable record of the two
   python `re` divergence classes.
6. Updated CLAUDE.md files: `tests/rxtsource/`, `tests/harness/`,
   `tests/oracle/`, `oracle_store/`, `docs/design/`.

## What the mechanism does

A `m`/`n`/`ms`/`ns`/`g`/`gp` cell whose python answer disagrees with the
`.rxt` expectation now consults the committed C3 oracle store
(`oracle_store/libpcre2-10.48/`, `tests/oracle/oracle_store.py`'s
`lookup()`, never a live library at check time) before being scored:

- store CONFIRMS the expectation → **INFO** (a new, separately-counted,
  always-printed, never-gated bucket — modelled on `tests/thread/
  run_stackdepth_tests.sh`'s `record()` bucket).
- store covers the question AND disagrees too → **FAIL** (a real
  transcription tripwire).
- store has no committed answer for this exact question → **FAIL**,
  `STORE-UNCOVERED` (falls back to today's pre-lane python-only verdict,
  counted separately so the population is visible).

## The 7 red cells

All seven resolved via the mechanism, no hand-marking: `tests/backrefs/
d27/caseless.rxt:39`, `tests/counterk/counterk.rxt:568/626/644/702`,
`tests/lookaround/captures.rxt:59/67`. All seven are PCRE2-confirmed —
python alone was wrong, on two genuinely distinct, both version-sensitive,
divergence classes (`docs/dev/upstream_issues.md` U17):

1. A non-leading global `(?i)` compiles under python <=3.10 (a
   `DeprecationWarning`) and applies globally, wrong against PCRE2's
   enclosing-group scoping — a hard `re.error` under 3.11+.
2. Lazy-counted-alternation capture timing and negative-lookahead capture
   retention — both closed between python 3.9/3.10 and 3.11.

Bisected with three interpreters actually present on this box (system
`python3` 3.9.6, homebrew `python3.10`, miniconda `python3.11`) — under
3.11, all seven cells are ALREADY clean (PASS or, for the caseless.rxt
cell, an ordinary `no-python-expression` SKIP), confirming the reference/
Linux box (documented python 3.14) never reaches the store-consultation
path for this population, which is why `C3_INFO`/`C3_STOREUNCOVERED` are
pinned at **0**, not this box's own local 7/0.

## The `# pcre2-only` marking question — settled

Frank's brief asked what to do with existing markings. **Measured, not
assumed**: `verify_rxt.py`'s marker recognition is an exact string match,
`line.strip() == '# pcre2-only'`. The corpus carries this marker in two
shapes that behave completely differently and nothing in the tree
previously said so:

- the **bare** form — 1,039 lines / 60 files — the only one the parser
  ever recognizes; a block marked this way skips entirely, unchanged.
- the **colon** form, `# pcre2-only: <reason>` — 64 lines / 7 files (every
  one from a `gen_corpus.py`-style generator: `tests/backrefs/d27/*`,
  `tests/atomic_groups/d27/interactions.rxt`) — **does not match the exact
  string and has never actually skipped anything.** It reads as a
  directive and has only ever been prose.

**Recommendation, implemented: retire reliance on the colon form; do not
fix the parser to recognize it.** Of the 64 colon-marked lines, only 7 are
real divergences (this lane's own population) — the other 57 are either
already-inexpressible via the ordinary compile-failure path, or python
already agrees despite the author's caution and the cell is a live PASS
today. Widening the exact-match test would silently move those passing
cells out of verified coverage for no offsetting gain; the store mechanism
already covers the one case the colon form was trying to guard, more
precisely and per-cell. No parser change made. Full argument: `docs/
design/c3_three_way.md` §6.

## Validation

**`verify_rxt.py` over the whole corpus** (209 files, `find tests -name
'*.rxt' | grep -v known_fail`, matching what `run_rxtsource_tests.sh`'s C3
section itself invokes minus the one it separately excludes):

| | before | after |
|---|---|---|
| PASS | 12729 | 12729 |
| FAIL | 7 | 0 |
| INFO | (bucket did not exist) | 7 |
| STOREUNCOVERED | (bucket did not exist) | 0 |
| SKIP (all reasons) | 16107 | 16107 |

PASS and every SKIP reason byte-for-byte unchanged — confirms the redesign
moves exactly the seven known cells and nothing else. (`run_rxtsource_
tests.sh`'s own C3 invocation additionally includes the one `known_fail`
file its own denominator counts separately — SKIP there reads 16118, not
16107 — an existing, unrelated difference in which file list is passed,
not something this lane's change causes; see the script's own comments on
the two denominators.)

**`tests/rxtsource/run_rxtsource_tests.sh`, whole-section run:**

- Before this lane: 115 passed / 3 failed. C3 itself hard-FAILed
  (`verify_rxt.py reported failures`); two OTHER, unrelated, pre-existing
  failures present in both runs and untouched by this lane — a message
  truncation in `[DD-13b.W1.2]`'s resolution-refusal check and a
  `[DD-13b.W1.3]` dup-definition-detection gap (msgtrim/other lanes'
  territory, per this lane's own scope mandate).
- After this lane: 117 passed / 3 failed. C3 now passes its "0 failures"
  gate (3 new PASS lines: discovery, the verified/info/skip line, census
  reconciliation) but its population-pin comparison now correctly RUNS for
  the first time on this box (previously unreachable — see below) and
  reports a real, but PRE-EXISTING and OUT-OF-SCOPE, mismatch.

**A finding worth flagging explicitly, not hidden**: the population-pin
comparison (`PASS`/`SKIP`/`SKIP_*` against their Linux-reference pins) only
runs when `verify_rxt.py` exits 0. Before this lane, the seven-cell FAIL
kept this box's exit code nonzero, so that comparison was never reached —
this box's own already-documented python-3.9.6-vs-3.14 skip-count skew
(`run_rxtsource_tests.sh`'s own pre-existing "BOX SENSITIVITY" note) was
invisible, masked rather than fixed. Fixing the seven cells makes the exit
code 0 on this box for the first time, which surfaces that mismatch as a
NEW-LOOKING (but not actually new) population-pin FAIL. This is documented
in the re-pin comment and in `c3_three_way.md` §7; it is box-sensitivity
pin-management territory (`wake.md`'s darwin admin slice), not this lane's
scope, and not fixed here. **Net over the whole section: my own change is
one hard C3 failure replaced by 3 new PASSes plus one honestly-explained,
pre-existing, unrelated FAIL** — a strict improvement, correctly reported
rather than claimed as fully green.

**Sabotage check** (scratch copy under the session scratchpad, never
committed): `tests/counterk/counterk.rxt:568`'s `g 1 0 2` planted to
`g 1 5 9` — matches NEITHER python's own answer `(1,2)` NOR the store's
confirmed PCRE2 answer `(0,2)`. `verify_rxt.py` exit code 1, reporting
`line 568: ... group slot 1 expected (5,9) but python got (1, 2) AND the
C3 oracle store disagrees too ((0, 2))` — a real FAILURE, exactly the
"neither oracle matches" row of the verdict table. Transcript kept in
`docs/design/c3_three_way.md` §8; the sabotaged file itself was deleted
immediately after the check, never committed.

**Store-uncovered unit check**: `_verdict_match_at` called directly with a
question never captured in the store returns `('uncovered', None)` rather
than raising or silently passing.

## What is OWED / not built here (D77, per `c3_three_way.md` §9)

- A true 10.46 reference capture of these seven questions (needs a general
  non-`membership` remote adapter that does not exist yet).
- Wiring the store as any OTHER check's oracle (PC-3/PC-4/uprops).
- Rewording the 7 colon-marked corpus files (recommended NOT to touch the
  parser; the files themselves are named as a low-priority follow-up for
  whoever next has cause to edit them — out of this lane's scope, which
  was explicitly `verify_rxt.py` + its callers + a design note, not `src/`,
  not W1.2/W1.3 territory, not `uprops_compare.py`).
- Resolving the box-sensitivity population-pin mismatch this redesign
  newly surfaces on darwin (above) — flagged for the manager, not fixed.
- `make test`/`make strict` — not run (box concurrency rule; this lane's
  validation is `verify_rxt.py` directly and the targeted
  `run_rxtsource_tests.sh` section, per the brief's own instruction to ask
  before a full suite run rather than run one unilaterally).

## Handback

Branch `lane/pyrole`, four commits, all committed and pushed to nothing
(local worktree branch — parked for the manager to merge). Validation
COMPLETE for everything in scope; the box-sensitivity pin gap and the
Linux-reference re-capture are explicitly OWED, not silently left for the
manager to discover. `git log --oneline lane/pyrole` for the four commits;
`git diff main lane/pyrole --stat` for the full file list.
