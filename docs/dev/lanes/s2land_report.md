# s2land — the S2 joint landing ([RUN-POS-SET] stage 3 + memfn Part D + R-41)

Lane s2land (opus, 2026-11-13). Branch `lane/s2land` from main `0b7a2ece5`, prepared for
the manager to fast-forward into main. Inputs: lane/memfn-partd @ `5c90af24e`,
lane/memfn-k1108 @ `0557e3097`, lane/rps3 @ `811e44862` (reports rps3, rps3b, rps3c).

## STATE AT HANDOFF

- STATE: delivered-with-owed. Merges, the flip, the abi event and every rps3 OWED item
  that needs no corpus measurement are committed. No rulings file was named in the brief.
- Last src commit `686237858` (the identity self-pin's subject). The branch tip carries
  tests/docs only after it.
- Validated here (before the owner's 20:00 hold): `make` and `make strict` clean after the
  merges and again after the flip; `make test-codegen` run 1 at `656ebebe1`: 19/21 scripts,
  two reds, both stage-3 movers in checks (fixed in `cc731ff44`, CHANGES below); run 2 at
  `cc731ff44`: 21/21 scripts, GREEN. `reqcube_check.py` standalone (the file `run_codegen_tests.sh`
  runs): 100 passed, 0 failed.
- Queued (not-before 2026-11-14T01:00) and cloud-dispatched: OWED below.

## MERGES

Each `git merge` run alone, rc read:

| order | branch | rc | result |
|---|---|---|---|
| 1 | lane/memfn-partd `5c90af24e` | 0 | clean (`f2e66d6fa`) |
| 2 | lane/memfn-k1108 `0557e3097` | 0 | clean (`e441ffc3f`; journal/responses only) |
| 3 | lane/rps3 `811e44862` | 1 | ONE conflict, `docs/dev/history/claude_md/docs__dev__lanes.md`: the kit's five lane entries (pdesign..partdfix) against rps3/rps3b/rps3c's three; union-resolved, both sides kept (`7f93e4519`). `src/gen/emit_dfa.c` auto-merged. |

`make -j16` and `make strict` clean on the merged tip (strict: "whole tree compiles clean
with -Werror -Wshadow; the kit's target table check passes").

## FLIP

One commit, `27bf6f146`, per rps3b's "AT THE JOINT LANDING" list:

- `src/core/limits.def` `PCREC_MAX_REQ_RUN_POS_SET` 2 -> 128; the INTERIM sentence replaced by
  the landed statement (128 since the S2 joint landing; the interim 2 and its cube clause retired).
- The cube clause RETIRED whole, not set false: `PF_WALK_POS_CUBE` (facts.c),
  `ReqWalkParams.pos_cube` (facts_derive.h), `RbWalk.pos_cube` and the cube test in
  `rn_admits` (req.c). `pcrec_req_cube` stays (other readers: facts.c, req.c's union).
- Lever (9) `run-pos-sets` retired at every site: `PF_WALK_POS_SET_AHEAD` and its
  `tests/registry/limits_check.sh` allowlist entry + comment, `internal.h`
  (`run_pos_sets`; the tenth's comment rewritten), `cli/main.c`, `cli/CLAUDE.md` option (9)
  (recorded as retired), `src/facts/CLAUDE.md`.
- `[facts-ahead]` (`tests/codegen/run_facts_checks.sh`): the `sets` lever cells became
  default cells (values unchanged: the landing build lists exactly what the lever listed),
  the interim default twins dropped, `sets+alt` became `alt`, and eight rows the pre-Part-D
  kit REFUSED (rps3b "go green only after the flip") added as default cells (`[α-ω]foo`,
  `abc[α-ω]defg`, `(?i)αβγ`, `(?i)xyzβw`, `(?i)москва`, `cat|dog`, `(?:ab|cd)xy`,
  `q(?:cat|dog)q`, and `xy(?:ab|cd|ef)zw` under the altcls denies): 24 cells. All compile
  (none REFUSED) and each value was checked by hand against req.c's rules
  (`cat|dog` -> `[6364][616f][6774]` is readiness memo U-d's `{c,d}{a,o}{t,g}`).
- rps3c's swap: `untestable`'s ROW line deleted from `tests/codegen/cand_oracle_unreached.tsv`
  (the ROW-line mechanism and header stay, now empty); witness `untestable - cat|dog` added
  to `cand_oracle_witnesses.tsv` (measured: the shipped build stamps `_REQ_WHY "untestable"`
  on `cat|dog`, the kit declining a run with no findable position). `tests/codegen/CLAUDE.md`
  updated.

**Rule (1) is NOT turned on.** No written owner ruling for `.alt_union` default ON exists:
decisions.md has none; plan.md's [RUN-POS-SET] says "2a census-first and 3m follow"; the
row body's 2026-11-12 note accepts readiness memo §6 q1's leaning, which keeps rule (1)
"behind the harness-only lever". `alt-union-run` stays; listed under OWED.

## ABI

`105 -> 106` (`686237858`), readers found by grep for `105` near `abi`/`ABI`:
`src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`; `docs/spec/match_api.md` §6 (the translation-unit
guard's `#if`/`#error`/`#define`, the `rx_info` table row, the "It is `106`" prose);
`tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its failure-message transition copy
(105->106 appended FROM the changelog); `tests/mech/sabotages/S693_abi_not_bumped.sh`
re-aimed (BEFORE 106, AFTER 105); `docs/dev/history/abi_changelog.md` (the new "is `106`"
entry, the old one demoted to "was `105`"); `tests/codegen/run_recursion_identity.sh`
FILEPIN and ABASEPIN self-pinned to `686237858` (`656ebebe1`; the manager re-pins to the
landing merge). The kit's own events ride the merge: MF_SITE_ABI 29, MF_CLASS_V 10, and
`docs/spec/registry.md` §6¶8b's `memfn` section floor already 13 (the kit raised it for
its `run-verify-wide` row; 13 rows measured on the landing build).

rps3's own OWED items:

- `MF_HEAD_MAX_UNBOUNDED` guard: the kit declares the name (memfn.h, `(int64_t)1 << 40`,
  MF_SITE_ABI 29), so the `#ifdef` is REMOVED and `req_site_define` states it
  unconditionally: a kit without the name now fails to build instead of silently stating
  the number.
- `tests/memfn/c10_presence.tsv` `(a+)+zq`: R-41's named value IS 2^40, so the pinned
  `1099511627776` is what it yields; the interim comment rewritten.
- part_d §9 item 9 pins: emit_sweep's four `--memfn=no-run-verify-wide` cells and
  `tests/axes/memfn_arm.py`'s (both layers) leave ASSERT_ZERO for DIFFER, manifest the corpus
  pattern `(?i:select)\d+x` (measured: it differs in byte/utf8 x c-default/c-vm, default and
  `-fmemfn-simd` layers). Floors are PROVISIONAL 1, labelled in both files: the corpus
  counts need a sweep the box hold forbids before 01:00 (OWED: re-pin at the measured value).
- The decline witnesses: cand-oracle `untestable` (above) and S3128's plant on
  `req_run_tested` (below). The R-by-role witness `xy/users\d+`: `run_offset_skip.sh`
  `users-digit`, `run-pinned`, offsets `0*,1,2,3,4,5,6,7`, scan byte 120 at 0, maxk 7,
  run compare `!memcmp(subject + cand, "xy/users", 8)` (measured on the landing build; the
  wide `[0-9]` stays outside the pin).

## CHANGES

Commits after the merges: `27bf6f146` (flip), `686237858` (abi), `656ebebe1` (self-pin),
`cc731ff44` (check movers, S3128), `e07b021c0` (deny pins), plus this report.

- **test-codegen run 1's two reds, both stage-3 movers in checks** (not product bugs):
  - `reqcube_check.py` crashed parsing a set-form `_REQ_RUN` (`[30-39]`...). It now reads
    both spellings of tuning.md §2.28¶7 (stamps compared by member set; a set-form run is
    counted, `REACH: ... set form`, outside the masked-word checks 1-2, which read cube
    runs); check 8's canonical form: a cube carries information (popcount(K) >= 1; was 7 or
    8, the interim domain), and a set-spelled run must hold a non-cube position with no
    bracket over 128 members (111 masked + 201 set-form rows over 5802 corpus patterns,
    floor 46 kept). Witnesses s2b/s2c (`S\d(?i:...)` -> `S.(?i:...)`) and control ctl1
    (`[0-9]+abcdef` -> `.+abcdef`) re-shaped: `\d`/`[0-9]` became run positions, which put
    `S` inside the run and made the "exact run" control a set run; `.` (no information)
    keeps each witness's intent.
  - `[facts-rep]`: `(?:ab[0-9]cd){3}` was the "body not `all`" witness; its body is `all`
    now and the repeat lists all three copies (kept as its own cell). The non-all witness is
    `(?:ab.cd){3}` (`cdab`), and S1923's REACH re-aimed to it.
- **S3128** (new mech row, `tests/mech/sabotages/S3128_run_tested_reads_stated.sh`):
  `req_run_tested` answers "stated" (`return run >= 0;`), so a declined run reads as
  tested; suite candoracle, detector the `untestable` witness. DESIGNED, not yet measured
  (REACH stage queued). Id: above the kit's S3127, no reserved range covers it.
  `tests/ci/cloud_mech_shards.tsv` regenerated (`cloud_units_plan.py mech --measured
  tests/ci/measured_mech.tsv --slots 30 --waves 3 --write`; the shard assignment reshuffles,
  56 unmeasured rows).
- Docs: `cli/CLAUDE.md`, `src/facts/CLAUDE.md`, `tests/codegen/CLAUDE.md`; this report and
  its history-index entry.

**Expected movers vs main `0b7a2ece5`** (the queued sweep's movers file; every class has a
named cause):

| class | cause |
|---|---|
| EVERY artifact (abi digits only) | abi 105 -> 106: provenance line, `rx_info.abi`, the TU guard |
| artifacts with a run through a class or an alternation union: new runs (none -> run), longer runs, `_REQ_RUN` set-form spelling, `_REQ_WHY`/`_DFA_PREFILTER`/offset changes | the domain flip (rps3b census: 354 movers of 7423 under the stage-3 domain, 37 bench "new") |
| runs the pre-Part-D kit refused (K-1) now compile with a set-test verified part | Part D (wide positions verify-only, R by role) |
| `_REQ_WHY "untestable"` (e.g. `cat|dog`) | Part D's decline row; pcrec's `untestable` req-admit row |
| VM artifacts on `handoff-attempts-unbounded` (`(a+)+zq` shape) | R-41: `MF_HEAD_MAX_UNBOUNDED` stated, the kit declines the landmark |
| facts stream: `req_whole_run` values and `used` asks | the domain flip |
| dumps: `--list-axes` (req-admit `untestable`, set-leads/emitted renumbered 5/6; memfn `run-verify-wide`), `--list-limits` (`PCREC_MAX_REQ_RUN_POS_SET` 128, two rows' text) | rps3 (untestable, texts), the kit (deny row), the flip (value) |

No mover is expected from rps3c's minimize fix (byte-identical, measured by rps3c) or from
the kit's merge alone (zero pcrec movers, partdfix gate 598).

## VALIDATION

- `make`, `make strict`: clean (merged tip; after the flip).
- `make test-codegen` run 1 at `656ebebe1`: `run_group: 19/21 scripts passed`, reds
  `reqcube_check.py` and `[facts-rep]` (both fixed above).
- `make test-codegen` run 2 at `cc731ff44` (src identical to `686237858`): `run_group: 21/21 scripts
  passed`, make rc 0, no `*** [test-` line (log `/var/tmp/pcrec-pcrec/scratch/s2land/codegen2.log`).
  It includes `[facts-ahead]` (24 cells), `[facts-rep]`, `run_offset_skip.sh`'s new witness,
  the identity gate at the self-pin, and the abi checks.

## OWED

- QUEUED (owner s2land, every stage held until 2026-11-14T01:00 by the time-gated job
  GATE_KEY, which creates `worktrees/s2land/.lift`; batch BATCH_ID, each stage waits for the
  one before it to go green; verdicts by `scripts/monread s2land`; stages file
  `worktrees/s2land/build/STAGES.s2land`):
  1. `make strict`;
  2. `make -k test-codegen test-registry test-rxtsource test-memfn-deleg test-startset
     test-compound test-cand-oracle` (cand-oracle added: its witness/allowance files moved);
     verdict by `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`;
  3. `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S1923 S3128 S693 S448 S451 S452
     S453 S454 S3107 S3119`;
  4. `make test` (perfrun);
  5. `emit_sweep.py --ref 0b7a2ece5` (all streams), a MEASUREMENT stage: green when the
     movers file `/var/tmp/pcrec-pcrec/scratch/s2land/sweep_main_movers.tsv` is written;
     movers EXPECTED (table above);
  6. `emit_sweep.py --ref <tip> --arms start --emit-pins
     /var/tmp/pcrec-pcrec/scratch/s2land/arms_pins.tsv`: the deny/plain arms over the
     stage-3 build; a floor that stage 3 lowered reds here.
  ORDER CHANGED from the brief (sweep after `make test`, not before): the sweep against main
  is red by design (every artifact moves in the abi digits), and a red stage cancels the
  rest of a batch.
- CLOUD: `scripts/cloudrun --kind test --name s2land` and `--kind axes --name s2land-axes`
  on lane/s2land (dispatched as this lane's last act; run ids in the handback).
  test-axes reads `memfn_arm.py`'s provisional floors.
- RE-PIN from the measurements: `DIFFER_PINS` / `memfn_arm.py` run-verify-wide floors AT the
  measured value (stage 6's pins file; the axes run), and any other arm floor stage 6 reds.
- D3's pcrec-artifact floor (part_d §9 item 9, §5.1 D3): census over `collect.py --sources
  corpus` >= the run-verify-wide DIFFER cell, a literal raised from 0. No such literal exists
  on either branch today (grep: only `memfn/tests/run_g2_pres.sh` `FLOOR_D3`, the G2-fed
  one); it needs the kit's production collector run, a kit task after the measurement.
- The D27 author's decline and R-by-role witnesses (part_d §5.1.1 "The D27 author", ruled
  YES): not written by either branch (no lane record found); a D27 cell lane, OWED.
- Rule (1) default ON (`alt_union`, `rr_alt` row 1): needs an owner ruling; with it, the
  `alt-union-run` lever turns into a restore arm, `[facts-ahead]`'s `alt` cells become
  default cells, and stage 2a's S-c/S-g witnesses land (rps3b OWED).
- rps3's STOP note (item 2, the head-vs-`req_byte` check on a decline) still asks main to
  confirm (rps3_report.md).
- The kit's own OWED (responses.md done line): the every_pos card's timing (owner-cleared
  window); `run-verify-wide`'s reach re-measure, which stage 6 provides.
- `make test-axes`, mech on the full matrix: the manager's (cloud).
