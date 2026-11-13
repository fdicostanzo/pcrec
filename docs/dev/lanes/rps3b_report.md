# rps3b — [RUN-POS-SET] stage 3 follow-ups on lane/rps3 (lane report)

Lane rps3b (opus), branch `lane/rps3` from its tip `31ce56741` (lane rps3 ended;
its report `rps3_report.md` is the starting point). Rulings applied: the manager's
three of 2026-11-13 (1: no `#if MF_SITE_ABI`, a TEST-ONLY lever for the stage-3
domain; 2: `rr_alt` rule (1) in scope behind its lever, byte-identical by default,
step 0's census a counted listing, not a gate; 3: the kit's joint rulings, R-41's
name `MF_HEAD_MAX_UNBOUNDED`, K from the head member on a decline).

## STATE AT HANDOFF

- STATE: delivered-with-owed. Tasks (a), (b), (c) are built and committed; every
  default artifact is meant to be byte-identical to rps3's (no default path
  changed: both levers are off on every shipped compile).
- No rulings file was named in the brief; the last ruling applied is the brief's
  ruling 3 (2026-11-13).
- rps3's queue batch `b202611130720443634579` (owner rps3), verdicts read from
  `worktrees/.boxqueue/`: 220 strict GREEN (`done/...-220-...strict`, rc 0, 37 s);
  221 codegen RED (`failed/...-221-...codegen`, rc 2, 247 s), its only red
  `test-codegen`'s [SABANCHOR] (3 stale anchors: S266, S294, S463; 20 of 21
  run_group scripts passed); 222-228 (registry, rxtsource, memfndeleg, startset,
  compound, reach, sweep) NEVER RAN: each waits on 221, which failed, so they sit
  `pending` (not-ready) and will not run unless 221 is retried. My `boxqueue
  cancel` of them was refused by the permission system, so they are still pending
  (the manager may cancel them; they are superseded by this lane's batch below).
  I edited the tree with them pending because none of them can start.
- Validated here (standalone, on this branch): `make strict` clean;
  `python3 -I scripts/m6read_check_sab_anchors.py` "all anchors resolve" (1262
  rows); `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S266 S294 S463`
  rc 0, 3 reached, and `... S268 S466` rc 0, 2 reached;
  `bash tests/codegen/run_facts_checks.sh` 15 passed, 0 failed (the new
  [facts-ahead], 20 cells, among them); `bash tests/registry/limits_check.sh` 42
  passed, 0 failed; `bash tests/compound/run_lever_fence.sh` PASS.
- The suites, the emit_sweep and the REACH run are QUEUED as one batch (OWED).

## CHANGES

**(a) [SABANCHOR], three rows re-derived from the live source (same fault, same
site).** `S266_freqpick_argmax.sh`: rps3 added `pcrec_find_pos_pick` (the run scan
index's per-position-set pick) with the same loop line as `pcrec_find_pick`, so the
anchor is ANCHOR COUNT 2; it now carries `pcrec_find_pick`'s `cube_mass` line (the
set pick, the one §3.7 reads). `S294_reqrun_enc_decline_leftmost.sh`: the run's
tie now lives in `pcrec_find_pos_pick`; the row plants the same tie fault there
(site 1, what §3.6/§4.9 read) AND in `pcrec_find_pick` (`SAB_FILE2`, same file),
so it still reaches both PICK readers as its description says (description
updated). `S463_handoff_k_minus_one.sh`: the context line moved under rps3's new
"tested" comment; the anchor is the `k` line plus that comment's first line.
Probes re-read on the branch (`RX_REQ_BYTE "120"`/`RX_REQ_RUN "none"`;
`"64"`/`"c3a940@2"`; `RX_REQ_HANDOFF "3"`), each row's re-anchor comment says so.

**(b) Ruling 1: the stage-3 domain behind a test-only lever.** No `#if`. The test
build's `--harness=run-pos-sets` (`PcrecHarnessOptions.run_pos_sets`,
`src/core/internal.h`; CLI arm in `cli/main.c` beside the other levers) makes
`pf_derive_req_walk` (`src/facts/facts.c`) walk in the landing's domain:
`pos_set` = `PF_WALK_POS_SET_AHEAD` (128, the most members a position may have
and still carry information) and the cube clause off. `-fno-req-run-fold` still
wins (1). `PF_WALK_POS_SET_AHEAD` is on `tests/registry/limits_check.sh`'s LIMIT
allowlist with its reason (test-build only, deleted with the lever). `--emit-facts`
already carries the harness record (`pin.harness`), so the lever reaches the
listing and every `.rxt`/`--pattern` compile alike.

**(c) Ruling 2: `rr_alt` rule (1).** `rr_alt` (`src/facts/req.c`) is now a
declared first-match table, `rr_alt_rows`: row 1 `rr_alt_union` (both branches
`all`, same untruncated width, `maxw` equal to it, and the per-position union
inside the walk's domain at every position: the alternation is `all`, its run the
union), row 2 `rr_alt_affix` (today's common head/tail, unchanged). Row 1 is on
only under the test build's `--harness=alt-union-run`
(`ReqWalkParams.alt_union`), so the default is byte-identical. Measured
(`--emit-facts`, altcls denied so the alternation reaches the walk): the stage 2a
predicted movers hold, `abcd(?:ab|ab)efgh` 6 -> 10 positions,
`(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` 4 -> 6, `xy(?:ab|ac)zw` `abzw` -> `xyabzw` (cube
domain); with both levers `xy(?:abc|abd)zw` -> `xyab[63 64]zw`; S-c's control
`xy(?:ab|abc)zw` stays `xyab` (unequal width never `all`). Answer smoke under the
lever (compiled `--emit-main`, run): `xy(?:ab|abc)zw` on `xyabczw` (0,7) and on
`xyabzw` (0,6); `abcd(?:ab|ab)efgh` on `zzabcdabefgh` (2,12); `xy(?:ab|ac)zw`
on `qxyaczw` (1,7), on `qxyadzw` NOMATCH.
Sabotage rows anchored in `rr_alt` re-anchored on row 2, same fault, same line:
`S268_req_run_alt_overclaim.sh`, `S466_alt_width_left.sh` (REACH rc 0).

**The pre-kit check `[facts-ahead]`** (`tests/codegen/run_facts_checks.sh`, in
the lever fence's allowlist already): 20 `--emit-facts` cells, each lever cell
beside its default twin, every one a pattern today's kit ACCEPTS (the
`--emit-facts` compile is a real compile, so a run today's kit refuses refuses
the listing too; there is no kit-free facts path).

**Docs:** `cli/CLAUDE.md` (harness options 8-10), `src/facts/CLAUDE.md` (the
domain line, `rr_alt_rows`), `src/facts/facts_derive.h` (a stale
`pf_walk_domain` cite fixed). No `docs/spec/` hunk: the levers are test-only
(the G7 fence forbids their spelling there), and no caller-observable byte moves.

### Step 0's census (counted listing, NOT a gate)

Script `docs/dev/lanes/rps3b_evidence/census.py` (p2_census.py's population:
every corpus pattern block and every pcrec-bench pattern, read-only), output
`rps3b_evidence/census.out`. 7423 patterns (7031 corpus, 392 bench), 29,692
`--emit-facts` compiles through `build/pcrec-harness` at `abdb715f2`. Default:
1589 state a run, 5346 none, 488 refused (the corpus's own reject rows).
NOT independent: the run is pcrec's own walk under its levers (the memo's
independent model is OWED).

| lever set | movers vs default | new (none -> run) | moved | kit-refused (K-1) |
|---|---|---|---|---|
| `run-pos-sets` (stage-3 domain) | 354 | byte 24 corpus + 13 bench, utf8 11 + 2 | byte 44 + 8, utf8 28 + 0 | byte 109 + 46, utf8 62 + 7 |
| `alt-union-run` (rule (1), interim domain) | 10 | byte 8 corpus | byte 2 corpus | 0 |
| both | 371 | byte 33 + 13, utf8 11 + 2 | byte 46 + 8, utf8 28 + 0 | byte 114 + 46, utf8 62 + 8 |

No compile lost its run and none timed out under any lever. Rule (1)'s movers
(17 rows, listed in census.out) are alternations of zero-width branches
(`a{2}(?:(?<!\w)|)b` `aa` -> `aab`, `ab|a\Gb` none -> `ab`), cube-domain
captures (`((H)|I){3}J` none -> `HHHJ/fefefeff`), and five that the kit refuses
only together with the domain lever (`((a)|b){3}c`, bench `alt-cyr-64`).
Bench movers under the domain lever: 23 cells that name a run (`\d{4}`,
`\d{8}`, `\d{16}`, `hex8-bounded`, `uuid-near-miss` x2, `us-zip` x2,
`cls-i-class`, `cls-mixed-case`, `va-tenant`, `cls-s-nbsp`, `float-literal`,
`wild-datetime`: new; `logparse-atomic` x2, `tail-ext-lower-txt`,
`winpath-near-miss` x2, `github-pat` x2, `http-5xx`: longer), and 53-54 bench
cells the kit refuses today. These are the timing cells the landing owes D186
evidence for.

### Rows that go green only after the flip (today's kit refuses them, K-1)

Measured single compiles, `--emit-facts` under `--harness=run-pos-sets` (and
with `alt-union-run`): every one is refused today with `mf_define: the derived
run part's find is not at the run reply's scan position`. utf8: `[α-ω]foo`,
`abc[α-ω]defg`, `(?i)αβγ`, `(?i)xyzk`, `(?i)xyzβw`, `(?i)москва`, `(?i)straße`,
`[\x{400}-\x{4FF}]{4,16}`; byte: `cat|dog`, `(?:ab|cd)xy`, `q(?:cat|dog)q`,
`xy(?:ab|cd|ef)zw` (altcls denied). Accepted today, so already in
[facts-ahead]: `\d{3}-\d{4}`, `[a-z]{8}`, `xy/users\d+`, `\w+@example\.com`,
`GET /[a-z]+ HTTP`, `(?i)xyzłw`, `xy(?:abc|abd)zw`. The census's
`kit-refused` counts are the full population.

## OWED

- QUEUED batch (owner `rps3b`, stages file `worktrees/rps3/build/STAGES.rps3b`,
  each stage waits for the one before it to go green; verdicts by
  `scripts/monread rps3b`): `make strict`; `make test-codegen test-registry
  test-rxtsource test-memfn-deleg test-startset test-compound`, verdict by
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`; `REACH_ONLY=1 bash
  tests/mech/run_sabotage_matrix.sh S266 S294 S463 S268 S466 S280 S3048 S329
  S448 S451 S453 S456`; `python3 scripts/emit_sweep.py --ref f066e84ee` over
  rps3's streams (all but `dumps`), expected movers NONE (movers file
  `$PCREC_TMPDIR/scratch/rps3b/sweep_movers.tsv`).
- rps3's stuck pending jobs 222-228 (batch `b202611130720443634579`): cancel.
- Cloud runs: the manager's.
- AT THE JOINT LANDING (with lane/memfn-partd), by hand, in one commit:
  `src/core/limits.def:411` `PCREC_MAX_REQ_RUN_POS_SET` 2 -> 128 (and its text's
  INTERIM clause); `src/facts/facts.c:228` `PF_WALK_POS_CUBE` true -> false (or
  delete the clause); then retire lever (9): `facts.c:229-244`
  (`PF_WALK_POS_SET_AHEAD`, `ahead`), `src/core/internal.h:209`, `cli/main.c:1542`,
  the LIMIT allowlist entry in `tests/registry/limits_check.sh`, `cli/CLAUDE.md`
  option (9). Rule (1) default ON: `facts.c:245` `.alt_union` becomes true unless
  a new restore arm `alt` (a `src/facts/walk_arms.def` row, alt_normal_form §11's
  harness lever, an internal arm of `tests/axes/run_axes.sh`) is restored, and
  `internal.h:210` / `cli/main.c:1543` retire; `[facts-ahead]`'s lever cells
  become default cells and its default twins move (a facts/artifact mover census
  then, with D186's per-regime evidence). Every row in "go green only after the
  flip" above becomes a [facts-ahead] cell.
- Stage 2a's sabotage witnesses S-c and S-g (alt_normal_form §5 stage 2a) as mech
  rows, once rule (1) is on by default (no id taken here).
- The memo's INDEPENDENT census model (no pcrec code); this lane's census is
  pcrec's own walk under its levers.
- rps3's own OWED list stands (abi 105 -> 106, `MF_HEAD_MAX_UNBOUNDED` confirmed by
  the kit's ruling 3 so the guard stays, c10's `(a+)+zq` row, §9 item 9 pins, the
  decline witnesses, `make test`, `make test-axes`, mech).
