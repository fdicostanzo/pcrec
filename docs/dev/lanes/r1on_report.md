# r1on report: [RUN-POS-SET] stage 2a rule (1) `alt_union` default ON, abi 106 -> 107

STATE: delivered-with-owed (built, local sections green after re-pins, sweep movers = census; cloud test/axes/mechrows dispatched, verdicts OWED)

## STATE AT HANDOFF
Branch lane/r1on, every change committed (tip after this report's commit). The rulings file
`docs/dev/lanes/r1on_rulings.md` is empty: no entry applied. No STOP condition hit: the sweep's movers
equal the census's set exactly, no answer moved (the harness section and the spanarms witness pass), and
no kit (memfn/) byte moved (sweep composition stream 0 movers, memfn/ untouched). Last acts: cloud
`test` (name r1on), `axes` (name r1on-axes) and `mechrows` (S3129-S3132, S3128, S693, S268, S1927)
dispatched with owner main; verdicts arrive as CLOUD-DONE.

## FLIP
- `src/facts/req.c`: `rr_alt_rows` is now a `{row, arm}` table like `rn_choice_rows`/`rb_rep_rows`/
  `rb_zero_rows`: row 1 `rr_alt_union` carries `PCREC_WALK_ARM(ALT)`, row 2 `rr_alt_affix` is never
  restored. `rr_alt_union` lost its `w->alt_union` clause; `RbWalk.alt_union` is gone.
- `src/facts/walk_arms.def`: new row `WALK_ARM(ALT, "alt", req_whole_run | req_pieces)`. The
  restore is the general walk-arm lever (`--harness=restore=alt`), not a second mechanism; a fact
  derived under it lists `harness:alt` (facts_listing.md §4.1.3¶4a, updated).
- Retired: `ReqWalkParams.alt_union` (facts_derive.h), its fill in `pf_derive_req_walk`
  (facts.c), `PcrecHarnessOptions.alt_union_run` (internal.h, bit not reused, comment kept), the
  `--harness=alt-union-run` CLI branch (cli/main.c), cli/CLAUDE.md option (10) marked RETIRED,
  src/facts/CLAUDE.md's lever sentence.
- `tests/axes/run_axes.sh`: `--harness=restore=alt` joins `INTERNAL_ARMS` (answer identity of the
  restored form vs default over the whole corpus). `tests/ci/cloud_axes_shards.tsv` regenerated
  (`cloud_units_plan.py axes --measured tests/ci/measured_axes.tsv --setup 70 --shards 20 --write`;
  the new unit takes the median estimate 387 s, shard 16); `cloud_axes_check.sh` PASS: 20 shards run
  the unsplit sweep's 116 jobs and 28 passes exactly once.
- Ruling recorded as an addendum to `docs/design/plan_row_bodies/RUN-POS-SET.md` ("2026-11-14
  manager ruling (rule (1) default ON)"), citing the s2r1b census (lane/s2r1 508bec313,
  docs/dev/lanes/s2r1b_report.md; not on main at this lane's base).
- Spec (D80): `docs/spec/tuning.md` §2.28¶3 (how the run is derived) gains the equal-width union
  sentence with examples (`AKIA|AGPA|AIDA|AROA`, `((a)|b){3}c`, `-+(?:(?=a)|)A`, and the S-c
  control `xy(?:ab|abc)zw` that still reports `xyab`); `docs/spec/facts_listing.md` §4.1.3¶4a
  names the arm `alt`.
- Premise test (on this branch's build): `xy(?:ab|ac)zw`, altcls denied: default
  `787961627a77@4/fffffffeffff`, `--harness=restore=alt` `61627a77@2/fffeffff` (the brief's two
  values, now with the default and the lever swapped).

## ABI READERS
Found by grep for the number at the last bump's sites (686237858's file list) plus `106` across
the tree: `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` 107; `docs/spec/match_api.md` §1 guard
(three spellings: the `!= 107` test, the `#error` text, `#define PCREC_RX_ABI_H 107`), §6 table
row 1 (`abi` ... `107`) and §6¶17's prose; `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=107` and
its transition message (`106->107: ...` appended); `tests/mech/sabotages/S693_abi_not_bumped.sh`
re-aimed (BEFORE 107, AFTER 106, RE-AIMED line); `docs/dev/history/abi_changelog.md` new entry
(the 106 entry becomes "was"); the identity gate (B) `tests/codegen/run_recursion_identity.sh`
`FILEPIN` SELF-PINNED to 196dad1e6 (this lane's last src commit; main re-pins to the landing
merge, OWED). Other `106` hits are unrelated numbers (registry row counts, error numbers, data).

## WITNESSES
- `tests/codegen/run_facts_checks.sh` [facts-ahead] turned around: rule (1)'s cells are now DEFAULT cells, each
  with a `--harness=restore=alt` twin that holds the old value (52 cells, was 24). Added one cell pair per
  census mover class (s2r1b "MOVERS BY CLASS"): literal-set branches `AKIA|AGPA|AIDA|AROA`; head- vs
  tail-aligned union `frank|zred|brad`; a repeat of a capturing alternation `((a)|b){3}c`; nested groups
  `(a(b|c)(d|e))`; zero-width branches `-+(?:(?=a)|)A`; the empty branch `abcd(?:|)efgh`; a utf8 range
  lowered to equal-width byte branches `x[\x{800}-\x{ffff}]y`; the handoff-shrinking repeat
  `(?:ab|ba|aa|bb){24}c` (4 -> 31 positions); `ab|a\Gb`; and `(?i)Ελληνικά`, whose outer alternation has a
  3-byte fold branch (U+1FBE), so the run correctly ENDS at the fold set's head. Three existing default cells
  also moved, as rule (1) predicts (a utf8 class range or caseless letter is an equal-width byte
  alternation): `abc[α-ω]defg` gains `616263`, `(?i)αβγ` gains `ce[93b3]`, `(?i)xyzβw` gains `[5777]`; each
  now has its restore twin with the old value. `q(?:cat|dog)q` gains the trailing `71`.
- S-c (alt_normal_form §5 stage 2a): `xy(?:ab|abc)zw` against `xyabczw` (0,7), `xyabzw` (0,6), `xyacbzw`
  NOMATCH (libpcre2-8 answers via tests/lib/p2probe.c), two blocks (default, engine vm) at the END of
  `tests/litscan/spanarms.rxt` (added at the end so no start-set manifest line moves). Its facts cell
  stays `78796162` in both arms.
- S-g was ALREADY landed (span_arms E2): row S1927 with its `(ab)x\1y` blocks in spanarms.rxt; reach
  re-checked REACHED on this branch. No new row.
- Sabotage rows (ids reserved S3129-S3133; S3133 unused): S3129 rule (1) off in the default (detector
  [facts-ahead], suite facts); S3130 S-c, the equal-width test dropped (harness on spanarms.rxt + facts);
  S3131 the `alt` arm not honoured (facts, the restore twins); S3132 the union replaced by the left branch's
  run (harness on tests/rungselect/rungselect.rxt, whose `((a)|b){3}c` block has `b` subjects).
  VALIDATE_ONLY: all fields OK. REACH_ONLY (S3129-S3132, S693, S268, S1927): 6 REACHED, S693 no probe.
  Detection itself is MEASURED by the mechrows cloud run (OWED).
- S268's probe `(?:x.abcy|wabc.v)q` still reads `none` (REACHED): its row-2 arm stays reachable.

## VALIDATION
- `make strict`: clean (scratch/r1on/strict.log).
- `bash tests/codegen/run_facts_checks.sh` standalone: 15 passed, 0 failed; [facts-ahead] 52 cells.
- `bash tests/harness/run.sh tests/litscan/spanarms.rxt`: 288 passed, 0 failed.
- `make -k test-codegen test-registry test-rxtsource test-memfn-deleg test-startset test-compound
  test-cand-oracle` via `boxlock run --label r1on-sections` (scratch/r1on/sections.log): red only in
  test-rxtsource (census +2 blocks / +6 lines from the S-c blocks), test-startset (vm manifests: the S-c
  rows, plus line shifts from the first placement mid-file) and test-compound (G7 lever fence: the new
  rows named `--harness=restore=alt`). All three fixed and re-run: `bash tests/rxtsource/run_rxtsource_tests.sh`
  300 passed / 0 failed; `make -k test-startset` rc=0 (scratch/r1on/startset2.log);
  `bash tests/compound/run_lever_fence.sh` PASS (3 checks, 4 controls). test-codegen, test-registry,
  test-memfn-deleg and test-cand-oracle were green on the first run. The other test-compound scripts
  were green.
- `tests/ci/cloud_axes_check.sh tests/ci/cloud_axes_shards.tsv`: PASS (116 jobs, 28 passes, each once).
- emit_sweep: `--ref main` (scratch/r1on/movers.tsv): every artifact moves, because of the abi digit, and
  the facts stream's 19 movers are the census's 19 exactly. To read movers without the stamp, a second run
  against main rebuilt with `PCREC_ARTIFACT_ABI 107` (`--ref-bin scratch/r1on/ref107/build/pcrec`,
  scratch/r1on/movers107.tsv, sweep107.log): c-default 19, c-vm 19, facts 19 movers, the SAME 19
  patterns as the census's default-config list (s2r1b an.out "(i)"); emit-ir (4 streams), stderr,
  composition (kit) and dumps 0 movers; every tag floor held. The run's rc=1 is those expected movers on
  identity-required streams.

## OWED
- Cloud verdicts (owner main, CLOUD-DONE via queuewatch): `test` r1on, `axes` r1on-axes (includes the new
  `--harness=restore=alt` answer-identity arm), `mechrows` S3129,S3130,S3131,S3132,S3128,S693,S268,S1927.
  If S3129 or S3131 reads UNDETECTED, check that the mechrows `facts` suite runs run_facts_checks.sh.
- Identity gate (B): `FILEPIN` self-pinned to 196dad1e6 (this lane's last code commit); main re-pins it
  to the landing merge.
- `measured_axes.tsv` has no timing for the new arm yet (the shard table gives it the 387 s median
  estimate); the next reweigh picks it up.
- Not done: no per-regime bench run for the moved picks (D186). The census showed +0.005% size and no
  answer change; any timing run is the manager's to schedule.
