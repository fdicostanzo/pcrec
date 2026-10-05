# r1gclose: round-1 gate close + r1mtriage follow-ups (2026-10-05)

Lane `r1gclose` (sonnet), branch `lane/r1gclose` off main 2de14a0e, Mac only
(suite lock held and released at the end). Input: `r1mtriage_report.md`.

## 1. Round 1 closed in the docs

- `docs/dev/plan.md` [OPTLOOP]: the bold status gains a 2026-10-05 "ROUND 1
  CLOSED" paragraph (gate complete at c4c70f2c, mech's 29 flags dispositioned
  by r1mtriage with no compiler regression, pointers to the report, §3.ab and
  this report). Grep of plan.md for other rows naming round 1's gate or mech
  as a trigger found none (the only hit is [OPTLOOP]'s own text, whose earlier
  "gate is OWED" sentences are dated history now followed by the closure).
- `docs/dev/learnings.md` §3.ab: a check never run to completion rots
  silently. Evidence is the report's: six of the ten flagged rows were stale
  from 09-20..09-29 and S297's detector was vacuous on ELF from birth, because
  no full mech had completed since 08-30; corollaries are a driver wall cap
  that fits the matrix, a flip accepted only with its clean-tree control, and a
  detector shown to fire on the platform that gates.

## 2. S220's answer cells

- Source of truth is the generator: `tests/lookaround/gen_corpus.py` gained
  `(?!a)` on {a, b, ab, ""} and `x*(?!a)` on {a, xa, xxb, ""}; only
  `lookahead.rxt` was regenerated in the repo (+2 blocks, +8 `m` lines; the
  other generated files are untouched, see the caveat below).
- Expected answers (from the generator, which never asks pcrec): `(?!a)` on
  "a" is (1,1), on "b" (0,0), on "ab" (1,1), on "" (0,0); `x*(?!a)` on "a"
  (1,1), "xa" (0,0), "xxb" (0,2), "" (0,0). Oracle method: the generator drove
  every cell through libpcre2 (ctypes binding; locally 10.42, the dev Mac's
  resolved library, NOT the 10.46 reference — the Linux box was off limits)
  AND python3 `re` in the same pass; both blocks came out python-verified (no
  `# pcre2-only`), and `tests/harness/verify_rxt.py` independently reads the
  file at PASS 60 -> 68, 0 FAIL, skips unchanged.
  Caveat for a later regeneration: on this Mac the generator's other six
  outputs differ from the committed ones (committed from the 10.46 box, local
  libpcre2 is 10.42), so only `lookahead.rxt` — byte-identical before my
  addition — was taken from the run; regenerate on the reference box before
  touching the others.
- Re-pins in the same change (readers found by grep): `run_rxtsource_tests.sh`
  CENSUS 4510/38748 -> 4512/38756, RUNSH the same, C3_PASS 16619 -> 16627
  (3.14 number inferred from the measured python-3.9 +8), C3_VERIFIABLE
  18616 -> 18624, each with a dated note. `test-rxtsource` 278 passed / 0
  failed after. `run_expansion_diff.sh`'s population pin and the lookaround
  diff did not move (`make test-lookaround`: 5/0 and 11/0). The corpus cells
  on the clean compiler: `tests/harness/run.sh tests/lookaround/lookahead.rxt`
  73 passed / 0 failed.
- DETECTION. Plant applied to a scratch tree (S220's own SAB_BEFORE/AFTER
  pair, built at build/plant_tree) and the harness run over the file:
  **70 passed / 3 FAILED** — `(?!a)` on "a" and on "ab" and `x*(?!a)` on "a",
  each `expected 'match 1 1' got 'match 0 1'`. That is answer-level (the
  reported start is the search origin where the true match begins later),
  where before only the structural run_search_pinned §1 witnesses saw it
  (corpus 0 fail). S220's SAB_DOC_FIGURE records this. The official solo
  matrix run (`run_sabotage_matrix.sh S220`, tree edf3982a) was launched
  detached: log `worktrees/r1gclose/build/logs/s220_solo.log`, completion
  file `build/logs/s220.done`; its verdict line is OWED (see below).
- Side observation: the corpus's pre-existing `(?![^a])` (axis13) is also a
  P2-sole-guard machine but no cell distinguishes it under the plant
  (axis13 + wordb_empty_compose pass 1400/0 with the plant). Not added.

## 3. The "exactly three" re-sweep (s220_view_decliners.txt)

Method (measurement-only wrapper around `start_pinned_applies` in a scratch
`git archive` tree under build/, never committed): for every distinct corpus
`pattern` line (3,612, including the two new cells) print P1, P2,
`dfa_needs_seed` and the verdict, compiled as run_search_pinned.sh compiles
(`--features all -fcomments -p rx --no-captures`), on the default axis,
`-fprefilter` and `-e utf8`.

Result at current main (+ the two new cells): **SEVEN patterns pass P1 and are
refused by P2**, not three:

| pattern | needs a seed (P3 would also decline) | source |
|---|---|---|
| `\B`, `\B\B`, `\Bx*` | yes | the 2026-09-02 three |
| `\Bx?` | yes | tests/utf8/axis11_startpos_boundary.rxt (newer than the sweep) |
| `(?![^a])` | no: P2 is the sole guard | tests/utf8/axis13_ctx_illformed.rxt |
| `(?!a)`, `x*(?!a)` | no: P2 is the sole guard | the new cells |

At the branch point without the new cells it is five. `-fprefilter` has none;
`-e utf8` yields six (all but `(?![^a])`). Corrections made: the manifest
holds all seven with the method and split in its header, S220's
`SAB_REACH_POP` is `^[^#]|7` (selector no longer `^\B`, which would have read 4
and ignored the lookahead members), S220's header paragraph and
`tests/mech/CLAUDE.md` carry the correction. Not edited: the dated historical
reports (tri220, r51fix) and S219's header.

Extra finding for S219's owner: `(?<!.)` passes P1 and P2 and needs a seed, so
P3 now DECLINES one corpus pattern; S219's header claim "P3's decline is never
asked" is a 2026-09 statement the tree no longer supports. S219 remains
declared UNDETECTED (expected); whether the plant now has a detector via
`(?<!.)` is unmeasured here.

## 4. Validation

| item | result |
|---|---|
| `make test-lookaround` (lookaround diff + expansion diff) | 5/0 and 11/0, logs build/logs/lookaround.log |
| `make test-rxtsource` after the re-pin | 278 passed / 0 failed (build/logs/rxtsource2.log); first run before the re-pin: 7 failures, all the census/C3 pins |
| lookahead.rxt through the harness, clean | 73 passed / 0 failed |
| same, S220 plant | 70 passed / 3 failed |
| `make strict CC=gcc-16` | clean |
| codegen `search_pinned` | not run: no `src/` change and the S220 solo run exercises it (the sabotage matrix runs `searchpinned`); OWED inside the matrix log |
| S220 solo matrix row | OWED, log `build/logs/s220_solo.log`, completion `build/logs/s220.done` |

Expected S220 solo verdict: DETECTED with `pop ... =7(want>=7)`, `reach:ok`,
`searchpinned` red on the §1 witnesses and the corpus arm now red (the three
cells). A verdict of UNDETECTED would be a finding.
