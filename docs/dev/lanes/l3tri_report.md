# l3tri report (triage of the L3 feature's cloud make test reds and its local REACH red)

## Summary
Every red of both runs is classified. There is NO real regression and no wrong answer. All four reds were
stale expectations or check-model gaps, and each is fixed on lane/l3tri (cut from lane/l3feat 3f02ca8ab;
lane/l3feat is untouched).
- Cloud run 44837163439 (completed, conclusion failure): shards 6, 13 and 14 failed, plus `gather`, which
  only collects the shards. Every other shard passed.
  - Shard 14 (test-lookaround): two D27 L1 listing pins, A22 and C07. STALE EXPECTATION: L3's run now
    reaches into the lookbehind. Both were re-judged sound and equal to PCRE2, then re-pinned.
  - Shard 6 (test-cpset-structure CHECK 3): `(?<=foo)bar` EMITTED_BYTES 38505 -> 39608. STALE
    EXPECTATION: the diff, read against the abi 109 build, is exactly L3's run finder plus the K < 0 move.
    Re-recorded with its RE-RECORDED note.
  - Shard 13 (test-encoding-checks DD12a(i)): CHECK-MODEL GAP, two causes.
    - (a) The check did not know the K < 0 entry-move text, which L3 owns.
    - (b) The check did not model the byte-rate-keyed PRES order beside a run. That gap was already on main
      (main's own check flags `ab(c)\1x` at K 1); L3 moved the DD12a(ii) witness `(?<=a)(b)\1x` into it.
    Both are taught to the check. The new arm is guarded by a multiset comparison, and sabotage S3450 shows
    it detected.
- Local job 301-main-l3feat-reach: one row unreached, S3381. STALE WITNESS: W-D2 `(?<=ab)(?<=cb)c` now lists
  `6263` beside `dead`, and the probe had pinned the value `none`. Re-aimed to read only the `dead`
  annotation; the plant is still DETECTED.
- Cloud re-dispatch: see STATE AT HANDOFF.

PREMISE TEST: `make -C <wt> test-lookaround` at 3f02ca8ab reproduced the two shard-14 lines exactly (the A22
and C07 FAIL lines, `*** [Makefile:1254: test-lookaround] Error 1`). After the fix the same target gives
0 FAIL and 20 PASS, and no make error.

## Cloud test failures
Read with `gh run view 44837163439 --json ...` and `gh api repos/.../actions/jobs/<id>/logs`. While the run
was in progress, `--log-failed` refused, so the job logs were read through the API. Logs:
`$PCREC_TMPDIR/scratch/l3tri/j592.log` (shard 6), `j771.log` (13), `j736.log` (14).

| shard | section | red | class |
|---|---|---|---|
| 14/18 | test-lookaround | `A22 (?<=nop)st lists 6e6f707374, recorded 7374`; `C07 (?<=a)(?<=[ab])c lists 6163, recorded none` | stale expectation (L3 moved the listing as designed) |
| 6/18 | test-cpset-structure | `[3]` manifest drift: `(?<=foo)bar EMITTED_BYTES 38505 -> 39608` | stale expectation (the artifact gained L3's code) |
| 13/18 | test-encoding-checks | DD12a(i): 3 selection incoherences, the K50 undeclared-form list (3 new members), and 8 strict pairs outside named regions | check-model gap (below) |

Shard 13 in detail. The three new members were `(?<=(?:abc|abde|ab))z`, `(?<=a)(b)\1x` and
`(?i)(?<=ab)(b)\1x`. The last two are the check's own explicit DD12a(ii) witnesses. The other 4 + 1
diverging patterns (`ab|abc|ad`, `\b`, `\B`, ...) are the K50 manifest's existing members.
- (a) "REQ_HANDOFF -2 but 0 handoff gate(s)" and "REQ_WHY emitted but 0 pre-check(s)". The gate IS present.
  Its K < 0 spelling is `rx_reqrun(subject, subject_length, (search_from >= B ? search_from - B : 0))`,
  followed by the end clamp `if (subject_length - handoff_position < B) return 0;` and the move block
  `if (handoff_position >= search_from || search_from - handoff_position < B) { ... } else ...`. The utf8
  side carries its round-up inside that block (the "while ... search_from++" TEXT DIFFERS line). None of
  these matched HANDOFF_DECL_RE, HANDOFF_GATE_RE or HANDOFF_OPEN_RE. This is not R-1's decline: the decline
  removes the forward scan's re-entry row, and the entry gate stays.
- (b) "byte pre-check scans 98,120 but REQ_BYTE is 98" on `(?<=a)(b)\1x`. That is a VM route with run `ab`@1
  (K -1) and a presence test of `x`. The kit's PRES order reads the byte-keyed prior. Under byte, `x` comes
  first, as the one-byte gate before the run's gate. Under utf8, `x` comes after, as an `rq_set` loop.
  Main shows the same thing at K >= 0: running main's check on `ab(c)\1x` with main's build gives the same
  two findings (`$PCREC_TMPDIR/scratch/l3tri/dd_main.out`). No corpus pattern in the default slice reaches
  that shape, so main stayed green until L3 gave the always-appended witness a run.

## Reach run failures
Job 301 (`.boxqueue/failed/20261120T184309.126815398-301-main-l3feat-reach/job.log`) ended `rows=1376
reached=679 unreached=1`. The unreached row is `S3381-guard-empty-meet-not-dead reach:MISSING(1/1)`. Its
probe grepped `req_whole_run ... none\tdead`. Since L3 the listing reads `6263` (BACK's `bc` at K -1) with
`dead`, which facts_listing §4.1.3¶1a allows (the value is the walk's run; any run is sound for a pattern
that never matches). This is a re-aim, not a loss of coverage: the site (the EMPTY-MEET branch setting
`dead`) is still reached. The probe now reads `([^\t]*\t){5}dead\t`.

## Fixes
- c424cd262: `tests/lookaround/d27_l1/l1d27_listing.tsv` A22 and C07 re-pinned. Both are PASS rows, so
  there is no limit row to drop (`l1d27_limits.tsv` names neither).
- 6c6eba8b2: `tests/mech/sabotages/S3381_*.sh` reach re-aimed, with a header note.
- 65cbc4c97: `tests/codegen/run_encoding_checks.sh` DD12a(i):
  - (a) HANDOFF_DECL_RE and HANDOFF_GATE_RE accept the K < 0 start. The new HANDOFF_NEG_CLAMP_RE is excised
    with the gate (or alone after a one-byte gate). The new HANDOFF_NEG_OPEN_RE block is excised like K82's,
    under the same 8-line ceiling.
  - (b) THE PRESENCE ORDER (`presence_stmts`). It applies only where both sides state a run (`@`) and
    their presence statements differ in order or form. The members are compared as a multiset: if they are
    unequal, it is a selection finding. If they are equal, the statements are removed from both sides and
    counted (`PRESENCE_ORDER`, floored at 1 by the witness, K35).
  - A sanity mutation (utf8 `rq_set {120}` -> `{121}`) reads as a different multiset.
- e51c5aaaf: `tests/codegen/manifests/m5_stage1_stamps.tsv` row re-recorded, with a RE-RECORDED note in
  `run_cpset_structure.sh`.
- 686808f49: sabotage S3450 (DD12a(i) presence order lost; detector: the floor and strict identity).

No allowlist or exception row was added; the K50 manifest is untouched. Proposed filing (no new K number
taken): DD12a(i)'s PRES-order model gap predates L3 (`ab(c)\1x` on main). The presence-order arm closes it
for run-stating pairs. A critic round should judge whether the multiset bar is the right strength, because
it is a check change (pcrec-critics-on-all-work).

## Re-judged pins
- A22 `(?<=nop)st`, byte: 7374 -> `6e6f707374`, K -3 (`req_landmark_maxoff`). Spec expectation: "run
  contains 7374; sound in every match; not dead". It contains 7374, and the run is present at
  `[s-3, s+2)` in all 4 libpcre2 matches of the row (`sound.py`, scratch). Not dead.
- C07 `(?<=a)(?<=[ab])c`, byte: none -> `6163` [rate:builtin-prior], K -1. Spec expectation: "NOT dead;
  answers as PCRE2". It is not dead, and the run is present at `[s-1, s+1)` in all 3 libpcre2 matches.
- Answers: `PCREC=build/pcrec bash tests/harness/run.sh tests/lookaround/d27_l1/l1d27_witnesses.rxt` (the
  libpcre2 10.46 answers) gives cases passed 775, failed 0.
- `(?<=foo)bar` EMITTED_BYTES 39608: the diff against the abi 109 build is the abi digits, RX_REQ_RUN/WHY/
  HANDOFF, `rx_reqrun` (scan `b`, verify `foob`/`obar`), the K < 0 gate/clamp/move, the prefilter's start
  `handoff_position` and RX_RUN_WORDS 3 -> 4. RX_DFA_PREFILTER stays "run-pinned".

## Validation
All local runs used `nice` on the l3tri build.
- `make test-lookaround`: before the fix, the two FAIL lines plus `*** [Makefile:1254: test-lookaround] Error 1`.
  After: 20 PASS, 0 FAIL, no make error (`lookaround2.log`).
- `make test-encoding-checks`: before, `checks failed: 3` (`enc0.log`). After, every sub-check `failed: 0`.
  DD12a(i) PASS (248 strict pairs); handoff pairs on both sides 21 -> 24; presence-order pairs 1 (floor 1)
  (`enc1.log`).
- `make test-cpset-structure`: checks passed 29, failed 0 (`cpset.log`).
- `REACH_ONLY=1 run_sabotage_matrix.sh S3381`: REACHED. The plant `run_sabotage_matrix.sh S3381` reads
  `facts:1fail/15pass DETECTED`.
- S3450: VALIDATE_ONLY valid; REACH_ONLY REACHED; the plant reads `encoding:4fail/13pass DETECTED`,
  unexpected 0.
- `python3 scripts/m6read_check_sab_anchors.py`: 1377 sabotages, all anchors resolve.
- Not run locally: the full REACH_ONLY matrix, and `make test` beyond these sections. The cloud test
  re-dispatch covers `make test`.

## STATE AT HANDOFF
STATE: done. Branch lane/l3tri, tip = this report's commit (named in the handback). Last ruling applied: none
(l3tri_rulings.md is empty); R-1 and R-2 of l3feat stand and nothing here touches them. The cloud test is
re-dispatched with main's `scripts/cloudrun --owner main --kind test --ref <tip> --name l3tri-test`; its
DONE line and the `git ls-remote` proof are in the handback message. Its verdict is owed to the manager's
watcher, not to this lane. A full REACH_ONLY re-run (job-301 shape) at the tip is recommended to the manager.
Dispatched: `cloudrun: DONE rc=0 pushed 5cd2bc269 -> cloud/main/test/l3tri-test owner=main kind=test`;
`git ls-remote origin 'refs/heads/cloud/main/*/l3tri*'` prints
`5cd2bc269511b09a9f31624714572b6a54efa057 refs/heads/cloud/main/test/l3tri-test` (the dispatched sha is the
commit before this sentence, which adds only text to the report).
OWED: none (the cloud verdict is the manager's, via queuewatch CLOUD-DONE).
