# C3's three-way verdict — python as a transcription-error tripwire

**BUILT, lane `pyrole`, 2026-09-10/11.** Ruled by Frank (2026-09-10):
python `re` is the historical base-tier oracle (D4), but PCRE2 is the
compatibility target (D26) — a python-vs-PCRE2 divergence is "interesting,
not actionable." Python's ONE remaining actionable value is
**INDEPENDENCE**: most `.rxt` expectations were themselves written FROM
libpcre2 answers, so a straight pcre2-differential check is partially
CIRCULAR (`docs/dev/learnings.md` §3's standing lesson — a control must not
share a source with what it controls). Python never authored these
expectations, so a python disagreement is a real transcription-error
tripwire — **but only where python agrees with PCRE2 too**; where PCRE2
disagrees with python, python was simply wrong (or version-sensitive, or
genuinely PCRE2-inexpressive), and the corpus expectation is not in doubt.
Frank approved narrowing `tests/harness/verify_rxt.py`'s C3 tier to exactly
that role.

## 1. The verdict table

C3 already had a two-way split for every `m`/`n`/`ms`/`ns`/`g`/`gp` cell:
python AGREES with the expectation (PASS), or python has NO OPINION at all
(a `.rxt` construct python cannot compile — SKIP, `no-python-expression`,
never scored, because "no opinion is not disagreement" — the file's own
long-standing comment, present since W1.1). What was missing was the THIRD
case: python compiles the pattern and gives a **different** answer.
Before this lane that was unconditionally a FAILURE. Now:

| python's answer vs. expectation | store's answer | verdict |
|---|---|---|
| agrees | (not consulted) | **PASS** |
| no opinion (compile fails) | (not consulted) | **SKIP** (`no-python-expression`, unchanged) |
| **disagrees** | store confirms the expectation | **INFO** — never a failure |
| **disagrees** | store covers the question, disagrees too | **FAIL** — a real transcription tripwire |
| **disagrees** | store has no committed answer for this exact question | **FAIL** — `STORE-UNCOVERED`, today's python-only verdict, counted separately |

Only the bottom three rows are new; the top two are the pre-existing C3
behaviour, unchanged. **The store is consulted ONLY when python already
disagrees** — an agreement needs no second opinion, and a `.rxt` cell that
already skips (own-oracle, pcre2-only, giveup, composed, perr-accept) never
reaches this logic at all, exactly as before.

## 2. The store-consultation flow

`tests/harness/verify_rxt.py`'s `_verdict_match_at`/`_verdict_captures`
(one per `.rxt` cell shape — `m`/`n`/`ms`/`ns` map onto the oracle
interface's `match-at` kind, `g`/`gp` onto `captures`, `docs/design/
oracle_interface.md` §2) build the exact `Question` the cell is asking and
call `oracle_store.lookup()` (`tests/oracle/oracle_store.py`) against a
COMMITTED store — **never a live library at check time** (the design's own
rule, and an economy argument too: a ctypes call per corpus case is
precisely the per-question cost the store exists to amortize away). A
`captures` question's `nslots` is derived from the `.rxt` cell's own `slot`
number (`slot + 1` — slot 0 is always the whole match, matching the `.rxt`
`g`/`gp` numbering exactly), never hand-supplied, so a `.rxt` slot maps
onto exactly one store question shape and two callers checking different
slots on the same match correctly land on two different (and independently
cacheable) store rows, per the design's own §4 rule.

A `StoreCorruption` (a tampered `rows=` header count, a stored `question`
column that does not match its own hash) is **not caught here** — it
propagates as a hard script failure, per `oracle_store.py`'s own rule
("never silently absorbed"). A clean miss (no committed row for this exact
question) is the ONLY thing that becomes `'uncovered'`.

## 3. The bucket definitions

Two NEW buckets, alongside the pre-existing PASS/FAIL/SKIP:

- **INFO** — `python-divergent, pcre2-confirmed`. Modelled on
  `tests/thread/run_stackdepth_tests.sh`'s `record()` bucket (the K33
  darwin addendum): a fourth verdict that is neither a pass, a fail, nor a
  skip, **separately counted, always printed** (per file, in the same
  `=== file: N ... ===` shape the FAILURES block already uses — an
  informational cell that stays silent by default is exactly the quiet-
  bucket shape `docs/dev/learnings.md` §3's K35 lesson warns against), and
  with **no gate on its count** — a growing INFO count is not itself an
  alarm; it is coverage the mechanism is now catching that used to be
  either a silent FAILURE or (before any oracle wiring at all) never
  checked.
- **STOREUNCOVERED** — a sub-count of FAIL, not a fourth verdict of its
  own: how many of today's failures are a **clean miss** against the store
  (the mechanism could not confirm-or-refute, so it fell back to the
  pre-existing python-only verdict) rather than a real, store-confirmed
  disagreement. Counted for the same reason every other C3 skip reason is
  broken out by name (`docs/dev/learnings.md` §3, and this section's own
  history of re-pins): a population nobody counts is not a population. A
  nonzero STOREUNCOVERED count is not an alarm either — it is exactly
  today's pre-lane behaviour, preserved as the safe default — but a
  GROWING one names exactly which cells `tests/rxtsource/
  build_c3_store.py` should capture next.

Both buckets are wired through `run_supervised` (the multi-file subprocess-
per-file aggregation path C3's own 900-second wall bound uses) as well as
the in-process single-file path, and through `tests/rxtsource/
run_rxtsource_tests.sh`'s C3 section as two new pins, `C3_INFO`/
`C3_STOREUNCOVERED`, checked alongside the pre-existing nine (now eleven).
The census reconciliation formula gained INFO as a third term:
`PASS + INFO + SKIP + (the one pinned timed-out file's own lines) ==
CENSUS_LINES` — informational cells are no longer inside PASS (python did
not verify them) or inside SKIP (a real answer was obtained and compared,
just not from python), so the accounting needs the third bucket explicitly
or it would silently under-count.

## 4. The store instance, and why it deviates from `oracle_store/CLAUDE.md`

`tests/rxtsource/build_c3_store.py` captures via the LOCAL DIRECT-LINK
adapter (`tests/oracle/local_adapter.py`), against this box's resolved
Homebrew libpcre2 10.48, and commits the result to `oracle_store/
libpcre2-10.48/{match-at,captures}.tsv`. **This is a deliberate deviation**
from `oracle_store/CLAUDE.md`'s stated convention ("only the REFERENCE
version [10.46] is committed... a local box's own resolved library is a
separate, gitignored cache"), directed explicitly in this lane's brief. The
reason it is safe rather than merely expedient: `docs/design/
oracle_interface.md` §8 Claim 2's staleness-impossibility argument — same
`OracleId` (which includes `version`) ⇒ same answer, always; a version
BUMP is a clean miss, never a stale hit — applies identically across a
version MISMATCH between two boxes. A box whose resolved libpcre2 is not
literally `10.48` gets a clean miss on every row in this store (falls back
to `STOREUNCOVERED`, never a false confirmation), exactly as a future
Homebrew bump on THIS box would. No general (non-`membership`) REMOTE
adapter exists yet (`remote_adapter.py`'s own scope note), so a true 10.46
capture of these same seven questions would need one built first — named
as a future migration step, not built here (D77).

**The store's population is deliberately small and hand-enumerated, not a
corpus sweep.** `build_c3_store.py`'s `QUESTIONS` dict carries exactly the
seven questions this lane's own full-corpus `verify_rxt.py` run found
python disagreeing on, each cited to its exact `.rxt` file:line. A FUTURE
divergence this store does not cover is not silently accepted — it lands
in STOREUNCOVERED and fails exactly as it would have before this mechanism
existed (§1's bottom row) — so under-covering the store is SAFE by
construction, and growing it is the ordinary maintenance path (re-run the
script with a new question appended) rather than a silent hole.

## 5. What a future python-version bump does — SHOULD BE: nothing fails

This is not hypothetical; it is what actually happened while measuring
this lane's own population. Two of the three divergence mechanisms behind
the seven known cells are **python-version artifacts, not permanent
semantic gaps**, confirmed by bisecting three interpreters installed on
this box (system `python3` = 3.9.6, homebrew `python3.10`, miniconda
`python3.11`):

- A non-leading global `(?i)` (`tests/backrefs/d27/caseless.rxt:39`)
  compiles under python <=3.10 (with a `DeprecationWarning`) and applies
  the flag globally — wrong, against PCRE2's enclosing-group scoping —
  but is a hard `re.error` under 3.11+ (python REFUSES the pattern
  outright), which routes the cell to `no-python-expression` instead of a
  comparison at all.
- Lazy-counted-alternation capture timing and negative-lookahead capture
  retention (`tests/counterk/counterk.rxt:568/626/644/702`,
  `tests/lookaround/captures.rxt:59/67`) changed between python's 3.9/3.10
  and 3.11 lines — MEASURED clean (no divergence at all) under both 3.10
  and 3.11 on this box.

So under python 3.11+ — which `run_rxtsource_tests.sh`'s own pre-existing
"BOX SENSITIVITY" note already establishes the reference/Linux box runs
(python 3.14) — **none of these seven cells reach the store-consultation
path at all**: they are ordinary PASSes (or, for caseless.rxt:39, an
ordinary SKIP). `C3_INFO`/`C3_STOREUNCOVERED` are pinned at **0** for
exactly that reason (§7 below), not because this lane observed 0 locally —
this box's own default `python3` (3.9.6) measures INFO=7. **This is the
intended shape of the mechanism**: a python upgrade (or downgrade, or a
different box's older interpreter) changes ONLY which bucket a cell lands
in (PASS/SKIP directly, or INFO via the store) — it never turns a
store-confirmed cell into a failure, and it never needs a code change. See
`docs/dev/upstream_issues.md` U17 for the full measured record of both
divergence classes.

## 6. The `# pcre2-only` marking question — RETIRE reliance on the colon
form, keep the bare form exactly as it is

Frank's brief asked this lane to settle and record: what happens to
existing `# pcre2-only` markings now that the store mechanism exists to
absorb a genuine divergence — honor them as belt-and-suspenders, or retire
them?

**Measured first, because the two spellings already in this corpus behave
completely differently and the difference was not previously documented
anywhere.** `verify_rxt.py`'s marker recognition (`parse_rxt`, unchanged by
this lane) is an EXACT match: `line.strip() == '# pcre2-only'`. The corpus
carries this marker in two shapes:

- **The BARE form**, `# pcre2-only` with nothing after it — **1,039 lines
  across 60 files**, and the ONLY form the parser actually recognizes. A
  block marked this way is skipped ENTIRELY (`skipped_pcre2_only`), before
  python ever attempts a comparison — this is the original, W1.1-era
  convention (`docs/testing.md`'s own citation) and it is UNCHANGED by this
  lane.
- **The COLON form**, `# pcre2-only: <reason>` — **64 lines across 7
  files** (`tests/backrefs/d27/{caseless,octal,numeric,dupnames,
  spellings,interactions}.rxt`, `tests/atomic_groups/d27/interactions.rxt`
  — all corpora built by `gen_corpus.py`-style generators, which
  independently invented this richer, self-documenting spelling without
  ever touching the parser that reads it). **This form does NOT match the
  exact-string test and has NEVER skipped anything** — every one of these
  64 lines has always been parsed and python-compared like any ordinary
  cell. The comment text beside each one ("python refuses a non-leading
  global (?i)", "python has no \\8/\\9 backreference concept") reads as a
  functioning directive but has only ever been PROSE.

**Why this was invisible until now.** For most of these 64 lines, the
comment's own claim ("python cannot express this") is independently true
via the ORDINARY compile-failure path — `re.compile` raises, `compiled is
None`, and the cell lands in `no-python-expression` regardless of whether
the marker matched. The marker's non-recognition was silent because its
effect and the compile-failure path's effect usually coincide. The seven
cells this lane's redesign resolves are exactly the population where they
DON'T coincide: python compiles the pattern successfully and returns a
confidently WRONG answer, which the (non-functioning) colon marker was
apparently meant to pre-empt and could not.

**Recommendation: RETIRE the colon form's aspiration to ever gate
anything, and do not fix the parser to recognize it.** "Honor as belt-and-
suspenders" would mean widening the exact-match test to also recognize
`# pcre2-only:` — and that is the WRONG fix, not merely an unnecessary one:
of the 64 colon-marked lines, only 7 are actual divergences (this lane's
own population); the other 57 are either already-inexpressible (unaffected
either way) or — the case that matters — python ALREADY AGREES with the
expectation despite the author's caution, and are counted PASS today. A
parser fix that started honoring the colon form would silently move those
PASSING cells into SKIP, shrinking real, currently-exercised coverage for
no offsetting gain — the store mechanism (§1-§4 above) already covers the
one case the colon form was trying to guard (a genuine, silent divergence)
more precisely, per-cell, oracle-verified, rather than per-block,
hand-asserted. **Implemented as: no parser change.** The bare form
continues to be the one functioning marker, unchanged; the colon form
continues to be prose. A low-priority, OUT-OF-SCOPE-for-this-lane follow-up
worth naming for whoever next touches those seven files: reword the colon
comments so they read as plain prose rather than as a directive that looks
functional but is not (e.g. drop the `# pcre2-only:` prefix and keep the
explanation) — not fixed here, since editing those corpus files' pinned
census/`# pcre2-only` counts is outside this lane's brief (verify_rxt.py +
its callers + this note, explicitly not `src/`, not W1.2/W1.3 territory,
not `uprops_compare.py`) and belongs to whichever lane next has cause to
touch those specific files.

## 7. Pinning, and the gap this redesign newly exposes rather than causes

`tests/rxtsource/run_rxtsource_tests.sh`'s C3 section pins are LINUX-
REFERENCE numbers by long-standing convention (the section's own "BOX
SENSITIVITY" note, present since before this lane). This lane's own delta,
measured in isolation against the pre-existing pins: **PASS unchanged,
SKIP unchanged (every `SKIP_*` reason unchanged), FAIL -7, INFO +7,
STOREUNCOVERED +0** — the seven cells move from FAIL to INFO and nothing
else moves. `C3_INFO`/`C3_STOREUNCOVERED` are pinned at **0** (§5's
argument: the reference box's newer python never reaches the store-
consultation path for this population at all).

**One consequence is a NEWLY VISIBLE, PRE-EXISTING gap, not a new one.**
The population-pin comparison (`PASS`/`SKIP`/`SKIP_*` against their
Linux-reference pins) only runs when `verify_rxt.py` exits 0 (zero
FAILURES). Before this lane, the seven-cell FAIL kept this box's `c3rc`
nonzero, so that comparison was never reached, and this box's own
ALREADY-DOCUMENTED python-3.9.6-vs-3.14 skip-count skew (measured here:
PASS 12729/SKIP 16118 locally against the pinned 13708/15074) was
invisible — masked by the harder failure, not fixed by it. Fixing the
seven cells makes `c3rc` 0 on this box for the first time, which surfaces
that pre-existing mismatch as a NEW population-pin FAIL in this section —
this is not a regression this lane introduces (the numbers were always
wrong on this box; only the code path that compares them was unreachable)
and it is not a gap this lane's brief scoped it to fix (box-sensitivity pin
management is `docs/dev/wake.md`'s darwin admin territory, per this
section's own established precedent of "VERIFIED LOCALLY... Linux
re-validation OWED"). Named here so the next reader does not mistake a
newly-VISIBLE old gap for a new one introduced by this change.

## 8. Validation

- `python3 tests/harness/verify_rxt.py` over the full corpus (209 files,
  excluding `known_fail`): before this lane, PASS=12729 FAIL=7 (the seven
  cells listed in `docs/dev/upstream_issues.md` U17); after, PASS=12729
  FAIL=0 INFO=7 STOREUNCOVERED=0 — PASS and every SKIP reason byte-for-byte
  unchanged, confirming the redesign moves ONLY the seven known cells and
  touches nothing else.
- Isolated per-file re-runs of the three touched files
  (`tests/backrefs/d27/caseless.rxt`, `tests/counterk/counterk.rxt`,
  `tests/lookaround/captures.rxt`) reproduce the same seven-cell INFO
  population exactly, both via the in-process path and via
  `run_supervised`'s subprocess-per-file aggregation (the code path
  `tests/rxtsource/run_rxtsource_tests.sh`'s actual C3 invocation takes).
- **Sabotage check** (never committed — a scratch copy under the session
  scratchpad, deleted after the check): `tests/counterk/counterk.rxt:568`'s
  `g 1 0 2` line was planted to `g 1 5 9` — a fabricated expectation
  matching NEITHER python's own answer `(1,2)` NOR the store's confirmed
  PCRE2 answer `(0,2)`. Result: `verify_rxt.py` exits 1, reporting
  `line 568: ... group slot 1 expected (5,9) but python got (1, 2) AND
  the C3 oracle store disagrees too ((0, 2))` — a real FAILURE, exactly
  the bottom-but-one row of §1's table, confirming the mechanism cannot be
  fooled by a transcription error that happens to also be a python
  divergence.
- A direct unit check of the `'uncovered'` path (a question never captured
  in the store) confirms the clean-miss fallback returns `'uncovered'`
  rather than raising or silently passing.

## 9. What is NOT built here (D77)

- A true 10.46 REFERENCE capture of these seven questions — needs a
  general (non-`membership`) remote adapter `remote_adapter.py` does not
  have yet. The local-10.48 instance is safe per §4's argument and is
  what this lane's brief directed.
- Wiring the store as ANY other check's oracle (PC-3/PC-4/uprops — the
  design's own migration ladder, §9 Step 2/3, names C3 as this very step).
- Fixing the colon-form `# pcre2-only` marker recognition, or rewording
  the 7 files that use it (§6's explicit recommendation NOT to fix it).
- Resolving the box-sensitivity population-pin mismatch this redesign
  newly exposes on darwin (§7) — a separate, pre-existing, out-of-scope
  gap.
