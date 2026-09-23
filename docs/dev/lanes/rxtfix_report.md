# rxtfix — triage of `test-rxtsource` red on merged main (2026-09-23)

**Cause**: lane b2fix's K34 closure (`[OPTLOOP.1.impl]` batch 2, gate log
`gate_b1885a83.log:4148-4392`, `checks failed: 9`) deleted
`tests/known_fail/k34_leftrec_giveup.rxt` (1 file/3 blocks/11 lines) and
placed its 11 now-passing cells by hand into the already-counted
`tests/recursion/d27/sr_depth.rxt` (`docs/dev/known_issues.md` K34's closure
note). Neither of b2fix's own validation checks (the known-fail ratchet;
the recursion diff) could see the population move — both are answer-level
and every cell answers correctly either way — so the corpus-wide CENSUS
pins in `tests/rxtsource/run_rxtsource_tests.sh` went stale first, exactly
the leading hypothesis, confirmed by `git log --stat` on the K34 closure
commit and by independently recomputing the real census with the script's
own awk logic against the live corpus.

**Pins moved, with derivation** (never subtracted — each literal follows
its own mechanism, `CENSUS - kf = RUNSH`):

| pin | before | after | why |
|---|---|---|---|
| `CENSUS_FILES` | 214 | 213 | the deleted file's own file left the census |
| `CENSUS_BLOCKS` | 3957 | 3954 | the deleted file's 3 blocks left the census |
| `CENSUS_LINES` | 29037 | 29037 (unchanged) | the 11 lines reappeared inside a file the census already counted |
| `RUNSH_FILES` | 213 | 213 (unchanged) | census and the known_fail exclusion each dropped by 1 and cancelled |
| `RUNSH_BLOCKS` | 3954 | 3954 (unchanged) | census and the exclusion each dropped by 3 and cancelled |
| `RUNSH_LINES` | 29026 | 29037 | the exclusion itself went to zero (`tests/known_fail/` is empty), so RUNSH gains back the 11 lines it used to subtract |

Verified independently of the script: `find tests -name '*.rxt' \| wc -l`
→ 213; the script's own awk census run standalone → `files=213
blocks=3954 lines=29037`, matching the new pins exactly.

**Targets, verdict**:

- `bash tests/rxtsource/run_rxtsource_tests.sh` / `make test-rxtsource
  CC=gcc-16`: **212 passed / 0 failed / 1 recorded** (was 202/9/0). The one
  `RECORD:` line is the pre-existing darwin python-version-skew C3 note
  (this box's python3 is 3.9, the C3 pins are python 3.14's numbers —
  documented, unrelated, matches `btriage_20260917_report.md`'s prior
  instance of the same box behavior).
- `make test-known-fail CC=gcc-16`: **green** — `tests/known_fail/ is
  empty`, `nothing to ratchet`, as K34's closure note expects.
- `make test-recursion CC=gcc-16`: launched detached per BOILERPLATE
  DO-THEN-FINISH; log `/tmp/rxtfix_make_recursion.log` in the worktree's
  own session scratchpad path — **OWED at report-write time, result to
  follow in the handback message** (verdict filled in before sending).

**learnings.md**: added §3.z (K34/rxtfix instance) — a lane can move
content between two files, watch both of its own answer-level checks read
green, and still leave a corpus-wide census red for the next lane, because
a relocation moves three census literals in three DIFFERENT shapes (not
one delta copied three times). Checked first: §3.y (2026-09-22, the
ff63ebf3 misread) covers a coverage guard living in a different FILE from
what it counts — adjacent but distinct (that instance is about a stale
COUNT pin nobody re-ran; this one is about corpus CONTENT relocating
between two files whose own checks are both answer-level and both stay
green regardless). New instance, not a duplicate.

**Commits**: `885cac75` (worktree `lane/rxtfix`, branch off main
`1bc0db30`) — the pin fix plus the learnings.md addendum, one commit.

**lanes/CLAUDE.md**: one-line entry added pointing here.
