# l1tri — triage of [REQ-HANDOFF-L1]'s validation-chain reds, and land prep

**Lane `l1tri`, 2026-10-11, opus.** Works directly on `lane/rlhbuild` (worktree
`worktrees/rlhbuild`; tip before this lane 43e1575b, abi 75). Input: the
rlhbuild chain, `build/land/chain.log` and its per-stage logs.

## 0. Answers first

| red (chain at 43e1575b) | class | fix |
|---|---|---|
| `make test` — `test-encoding-checks` | stale excise (lane rlhtri) | merged `lane/rlhtri` 52564f83 (fast-forward) |
| `make test-axes` — 7 axes, pcrec SIGSEGV on `axis01_encoded_length.rxt` | REAL regression (lane axtri §2) | merged `lane/axtri` 03ff92ea (fix 9dec5e6f) |
| `make test-recursion-identity` rc=2 | stale (B) FILEPIN | c9700391: FILEPIN a6dfa071 -> 9dec5e6f |
| `emit_sweep --arms start` rc=1 | stale floor, an intended L1 population move | cd72fa43: four DIFFER_PINS cells re-pinned |
| mech S806, S807 UNDETECTED | the sabotage rows' WITNESSES never reached their plants | 0601dce3: both re-aimed, two 5.12a rows; both DETECTED |

No design question is open. One process finding: rlhbuild_report.md §5's
"validated by plant at landing" was not true of S806/S807 (§2.3).

## 1. STEP 1 — merges

- `git merge lane/rlhtri`: fast-forward 43e1575b -> 52564f83.
- `git merge lane/axtri`: clean ort merge (`docs/dev/lanes/CLAUDE.md` auto-merged).
- `make -j16` rc 0; `make strict` rc 0 ("whole tree compiles clean").
- Spot check of the axtri repro: `build/pcrec -e utf8 -fno-offset-skip -p rx
  --emit-main --pattern '€+'` rc 0 (SIGSEGV at 43e1575b).

The chain's working tree carried a suite-rewritten `docs/dev/artifact_size_log.tsv`
(make test's [ART-SIZE] row log, header `commit=43e1575b`); restored with
`git checkout` before the merges, not committed. The STEP 3 make test rewrites it
again; the manager decides whether that copy is committed at merge.

## 2. STEP 2 — triage

All comparisons against main were made with a `git archive 677762be` build
(rlhbuild's merge-base with main) at `build/l1tri/base/`, and the scripts used
are in `build/l1tri/` (scratch, gitignored): `armdiff.py` (per-pattern start-stamp
movers for one arm on two binaries, through emit_sweep's own `stamps_of` /
`start_keys_moved`), `bindiff.py` (whole-artifact identity of two binaries over
the corpus).

### 2.1 `make test-recursion-identity` — stale (B) whole-file pin

recid.log: `[default]` (B) differing=174, `[noprefilter]` 98, `[nocaptures]` 175;
`[vm]` 0, linkage 0; every (A) program-region result clean. The (B) self-pin
`a6dfa071` is rlhbuild's last src commit BEFORE the branch merged main's kit
R-15 (2d8d4cfb) and axtri's fix. R-15's `precheck_assign_byte` row renders the
one-byte gate as a `memchr` ASSIGN, which is exactly what L1's handoff and
re-entry sites emit through.

Measured: a6dfa071 build vs the merged tip, default engine, all 4,542 distinct
corpus patterns: 176 differ, 0 acceptance mismatches, and EVERY changed line of
all 176 is one of `handoff_position = …` / `landmark_position = …` (the kit
gate's text), its `if (… == / >= subject_length)` test and the brace/return
lines it replaces, or `#define RX_MEMFN_LIBC` ("none" -> "memchr"); 0 lines
unexplained. (176 > 174 because this population includes the call-bearing
patterns the gate excludes.)

Fix c9700391: `FILEPIN` -> `9dec5e6f`, the branch's last src commit (axtri's
fix; `git diff 9dec5e6f HEAD -- src lib cli memfn Makefile` is empty). Other
readers of `a6dfa071` by grep: only rlhbuild_report.md (history).
Re-validation: STEP 3 `make test-recursion-identity`.

### 2.2 `emit_sweep --arms start` — two stale stamp floors

sweep.log: `byte -fno-req-run c-default stamp 208 < 296` and `utf8 … 79 < 294`;
every other arm ok. Per pattern against 677762be (`armdiff.py "" -fno-req-run`
and `"-e utf8"`): byte 296 -> 208, utf8 294 -> 79, **0 joiners**, and every
leaver (88 byte / 215 utf8) has the same shape: at main, denying the run turns
`REQ_HANDOFF` K -> "none"; at L1 the handoff stays at K. Witness
`(?:\G|x)cat`: main `-fno-req-run` -> `RX_REQ_HANDOFF "none"`, L1 -> `"1"` with
`RX_REQ_BYTE "99"`. This is L1's charter (the handoff rides the one-byte
REQ_BYTE landmark when no run ships), so the pin is stale, not the code.

L1's own axis grew too (`armdiff.py "" -fno-req-handoff`): byte 163 -> 339
stamp movers, main's set a strict subset (0 leavers); utf8 measured 519 differ
/ 517 stamp. Its floors stayed at 163/275 (still passing, but disarmed for
L1's population), so they are re-pinned at the measured value with the others.

Fix cd72fa43 (`scripts/emit_sweep.py` DIFFER_PINS + a header paragraph):
byte req-run stamp 296 -> 208, utf8 294 -> 79; byte req-handoff 163/163 ->
339/339, utf8 275/275 -> 519/517. Manifests unchanged (`SS`, `123` still move).
Every other cell's floor sits BELOW its measured value (corpus growth since the
pin's measurement, e.g. `-e utf8` 3188 vs 4130); not this lane's, untouched.
Re-validation: STEP 3 `emit_sweep --arms start`.

### 2.3 mech S806 / S807 UNDETECTED — the witnesses never reached the plants

Planted by hand in `git archive` copies (`build/l1tri/s806`, `s807`), the
5.12a witnesses read the SAME K as clean:

| plant | landing witness | clean K / stamp | planted K / stamp |
|---|---|---|---|
| S806 (`rb_intersect` keeps the nearer bound) | `(?:ab\|c):` | 2 / "2" | 2 / "2" |
| S807 (min-0 `A_REP` shifts nothing) | `a.?b` | 2 / "2" | 2 / "2" |

- **S806.** ':' is in neither branch of `(?:ab|c)`, so `rb_intersect` drops it
  and its offset comes from the alternation's WIDTH shift in the A_ALT arm, never
  from the planted max. A member must be carried by BOTH branches:
  `(?:ab:|c:)` reads K 2 clean, 1 planted, stamp "2" -> "1" (an artifact that
  would start the forward scan one byte late on `ab:`).
- **S807.** A BOUNDED min-0 repeat never reaches the A_REP `rmin == 0` arm:
  `.?`, `x{0,3}`, `(?:xy){0,10}`, `\d{0,150}`, possessive and atomic forms all
  read the same K under the plant (lowered to alternations before this walk).
  Only an UNBOUNDED min-0 repeat reaches it: `\w*:` reads K "unbounded" clean,
  0 planted (also `x*:`, `[a-z]*@`, `(?:xy)*+b`). The stamp is "none" both ways
  (the artifact does not hand off there at K 0), so the fact column is the
  detector, which is what 5.12a compares.

Fix 0601dce3: `run_prechecks.sh` §5.12a gains `(?:ab:|c:)` (2/"2") and
`\w*:` (unbounded/"none") rows (hand derivation: ab's colon at 2 vs c's at 1,
the farther holds; an unbounded repeat leaves no bound); the `(?:ab|c):` row's
reason text now says what it tests (the width shift); row floor 20 -> 22. S806's
`SAB_REACH` moves to `(?:ab:|c:)` (stamp "2"); S807's to `\w*:`'s
`req_landmark_maxoff` "unbounded" off `--emit-facts`; both files carry a
RE-AIMED paragraph. Both reach commands were evaluated on the clean and planted
binaries (S807's reach fails on its own plant, so it is plant-sensitive).

Re-validation (targeted, at 0601dce3): `make test-prechecks` 395/0 (was 393; the
two new rows); `bash tests/mech/run_sabotage_matrix.sh S806 S807`: `== mech run
COMPLETE: 2 rows (unexpected: 0, undetected: 0, unreached: 0, …) ==`, both
`prechecks:1fail/394pass DETECTED`. Log `build/l1tri/mech_806_807.log`.

Process note for the record: the rows' `SAB_DOC_FIGURE` says "validated by plant
at landing (rlhbuild_report.md §5)"; the 43e1575b chain read them UNDETECTED,
and the witnesses are unreachable for the plants on the tree as built, so that
validation either did not happen or measured something else. learnings §3's
"witnesses that stopped reaching their site" class, at birth.

## 3. STEP 3 — final validation on the merged tip (OWED at handback)

Chain `build/land2/chain.sh`, launched detached (`nohup setsid … & disown`,
no `.lift` wait: the brief rules the box quiet) at the tip carrying this report.
One line per stage in `build/land2/chain.log`; completion line
`== l1tri chain COMPLETE`. Order: make, strict, recursion-identity, emit_sweep
`--arms start`, mech S806 S807 S805 S808-S814, `make test` through
`scripts/perfrun --label l1tri`, `make test-axes` (longest, last: ~2.7 h on
the 43e1575b run).

| stage | command | log | verdict |
|---|---|---|---|
| strict | `make strict` | land2/strict.log | OWED |
| recursion identity | `make test-recursion-identity` | land2/recid.log | OWED |
| start arms | `python3 scripts/emit_sweep.py --ref HEAD --arms start --jobs 12 --out build/land2/sweep` | land2/sweep.log | OWED |
| mech | S806 S807 (re-aimed) + S805 S808-S814 | land2/mech_S*.log | OWED (S806/S807 already DETECTED at 0601dce3, §2.3) |
| full suite | `scripts/perfrun --label l1tri -- build/land2/test.log` | land2/test.log | OWED; verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` |
| axes | `make test-axes` | land2/axes.log | OWED; the axtri fix's landing+handoff co-selection population check |

A fresh reader fills this table from chain.log and the logs; a red make test
section is read with the perfrun class line (BOILERPLATE TRIAGE RULE).
