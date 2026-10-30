# Lane p1tri — triage of the 710-p1build-test reds on lane/p1build

Lane p1tri, opus, 2026-10-30, worktree `worktrees/p1build`, branch `lane/p1build` (the P1
landmark-walk stage 1 build, docs/dev/lanes/p1build_report.md). Input: job
`710-p1build-test` (failed/20261030T184940...; `job.log.make` RED-REAL, 11 sections; `job.log.ident`
red). Brief: merge main first, classify every red (a) inherited / (b) a pin the walk legitimately
moved / (c) a real P1 regression, fix, re-run the sections, queue one full re-validation.

## Summary

Main (5796317e9, abi 93) is merged into the lane (d5c031454); the landing stays abi 95
provisional (94 reserved for p4entry). Every red is classified below: two inherited (fixed by the
merge), one real P1 defect (a non-ASCII `--list-axes` literal, a one-character fix), and the rest
stale checks, pins and witnesses that the walk moved for a legitimate reason. **No red is an answer
problem.** The one stamp/body disagreement ([agreement], 76 artifacts) was proved on the body side:
the stamp `landmark-walk` is true, and the check had no marker for the walk body. Each fix is a
re-pin, a check that now reads the walk, or a witness moved back onto the domain it tests, with the
reason written beside it. The section re-runs and the startset census are QUEUED (the box was held
by queue work all evening; see STATE AT HANDOFF), and the startset manifests are OWED from that
census. Re-run in the lane and green: `run_facts_checks.sh`, `run_arch_blind.sh`,
`run_cpset_structure.sh`, `run_landmark_walk.sh`, `gen_adversarial.py witness`,
`axes_registry_check.sh` (245), `m6read_check_sab_anchors.py`, `make strict`.

## The merge

`git merge main` (85 commits, from main ae1d53859 to 5796317e9) conflicted in 8 files, all abi
readers or append-only lists:
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`, match_api.md (three abi readers), run_codegen_tests.sh
  `ABI_EXPECT`: kept 95.
- `docs/dev/history/abi_changelog.md`: the walk's entry stays on top, now "93 -> 95 PROVISIONAL";
  main's trailgc entry follows it as "was 93".
- S693: `SAB_BEFORE` 95, `SAB_AFTER` 93 (the parent's number, main's).
- run_rxtsource_tests.sh census pins: the walk's delta (+1 file, +35 blocks, +181 lines, all
  pcre2-only) summed onto main's (+10 cscan lines): `CENSUS_LINES`/`RUNSH_LINES` 75704, `C3_SKIP`
  52961; files, blocks and `C3_SKIP_PCRE2ONLY` unchanged from the lane.
- the lanes history index: both sides kept.
- run_recursion_identity.sh: main's FILEPIN text, then re-pinned (below).
`make -j16` and `make strict` are clean on the merge.

## Reds, one row each

| section | FAIL line (first) | class | change | green evidence |
|---|---|---|---|---|
| recursion-identity (job.log.ident) | `could not build the file-pin reference compiler from 8936a8156: ../shared/sha256.h` | a | main's fix (the file-pin build carries `shared/`) arrives with the merge; FILEPIN self-pinned to `379b84fac`, the lane's last `src/` commit, over the merge (manager re-pins to the landing merge) | OWED: queued `709-p1tri-sec-recursion-identity-locked` |
| memfn-guarded | `population simd-form: 5 below its floor 6` | a | main's fix, by the merge; no lane change | OWED: queued `709-p1tri-sec-memfn-guarded` |
| registry | `axes_registry_check COVERAGE CHANGED — 245 passing checks, expected 242` | b | the `locate` axis gains `landmark-walk` with its deny bit 57: 3 checks (macro/bit, cli flag, tuning.md heading); pin 242 -> 245 with its reason (run_registry_tests.sh) | `axes_registry_check.sh` standalone: 245 PASS, 0 failed, the three `[locate/landmark-walk]` lines; section OWED (queued) |
| codegen / run_dfa_stamps.sh | `[agreement] 76 artifact(s) stamp a scan shape their emitted body does not have`; `[values] 76 ...` | b | **proved on the body side**: e.g. `(?:a+)+b` stamps `landmark-walk` and its body holds the walk loop (`size_t lmwalk_reach = search_from;`, the `memchr` for `b` at `landmark_position`, the reverse walk) followed by the relocate's unanchored scan; the check's derivation had no walk marker, so the trailing forward step read as `unanchored`. The check gains the marker (`lmwalk_reach`, outranking the forward step) and `landmark-walk` in `SCAN_VALUES` (the value is match_api.md §6.3.4's, added by p1build) | OWED: queued `709-p1tri-sec-codegen` |
| codegen / run_ctext_ascii.sh | `[litscan] non-ASCII string literal(s) in an emitter: src/gen/emit_dfa.c:10351` | **c** | a real P1 defect, local: the walk row's `.desc` (printed by `--list-axes`) held `P·L`; now `P then L` (no artifact byte moves; no reader of the text in tests) | OWED: queued (codegen) |
| codegen / run_facts_checks.sh | `[facts-e3] the witnesses reach 4 of the 3 routes` | b | the widened-domain witness `\zabc -fno-req-handoff` now takes the walk; it also carries `-fno-landmark-walk` to stay on the unanchored route (comment beside it) | `run_facts_checks.sh` standalone: 9 PASS, 0 failed |
| codegen / run_codegen_tests.sh | `[TT-9] ... UNLISTED tests/codegen/run_landmark_walk.sh` | b | `tests/lib/san_excluded.txt` gains it as `DEFER-PLAIN` (it compiles with plain `$CC`, no `$GENCFLAGS`) | OWED: queued (codegen) |
| memfn-arch | `NEW architecture vocabulary: tests tests/codegen/NOTES.md class 6`; `STALE allowlist row ('tests', 'tests/codegen/CLAUDE.md', 6)` | b | p1build moved the `run_prechecks.sh` §5 line (it says "x86_64 measurement") from CLAUDE.md to NOTES.md for size; the C4 row follows the line (same count 1, same reason) | `run_arch_blind.sh` standalone: 17 PASS, 0 failed |
| memfn-manifest | `rule 2 (reach): delegated row LMHIT was never rendered` | b | the kit is reached through the door from `find_define` (the census attributes a render to the door's caller), which the row did not name; LMHIT now names `find_define` too, as MLINE names PF's `find_site`/`pcrec_emit_find`. Note: the reach is therefore SHARED with PF's row (rows already share callers: PRE/SETREST, VMSPAN/VMSTRIDE); the walk's own render is held by run_landmark_walk.sh's witnesses | OWED: queued `709-p1tri-sec-memfn-manifest` |
| search-pinned | `stamps "end-minus-width" but emits a rewind_position: (?:ab\|ba\|aa\|bb){24}c`; `RX_DFA_SCAN_EDGE 'range' but the artifact's own edges fold to 'none' ... [a-z]+@(?:[a-z]+@)*[a-z]+` | b | (1) the walk's own reverse walk writes `rewind_position` inside the walk loop; `RX_DFA_START` names the RELOCATE's recovery (p1build FIX-1, its acceptance cell `[a-z]{40}@x` reads `end-minus-width`), so the check reads `rewind` outside the loop (`lmwalk_reach` .. `search_from = lmwalk_start;`); (2) the edge is the landmark machine's (`landmark_state == 6 && ...`), which `dfa_member_machines` folds (ML, and MA as the inline verify); the check's folds now read `rx_landmark_*` and `rx_lmverify_*` on a walk | OWED: queued `709-p1tri-sec-search-pinned` |
| start-landing | `"end-minus-width" sub=1 rewind=1 rec=0 guard=0: (?:ab\|ba\|aa\|bb){24}c` | b | same as search-pinned (1): `has_rewind` reads past the walk loop, in the file and in the sweep worker | the awk read on that artifact: no rewind outside the loop (rc 1), the subtraction at line 494; section OWED (queued) |
| prechecks | `[5.1] x[0-9]+Q: RX_REQ_WHY is "dominated"`, `[5.12l] ... the text keeps landmark_position` (32 lines) | b | the witnesses `x[0-9]+Q`, `\w+@\w+`, `[0-9]+ABC...`, `[a-y]\d{0,150}:` now take the walk (stamped `landmark-walk`), whose PRESENCE decline is `dominated` by design and whose loop keeps a `landmark_position` of its own. Every compile in run_prechecks.sh carries `-fno-landmark-walk` beside `COVER_DENY` (the D172 S3 precedent: a decliner is byte-identical under the deny). The walk's own `dominated` is now held in run_landmark_walk.sh (a `[presence]` line per walk witness, 10) | `run_landmark_walk.sh`: 68 PASS, 0 failed; section OWED (queued) |
| cpset-structure | `[3] the recorded manifest has drifted`: `[a-z]+@[a-z]+ EMITTED_BYTES 35231 -> 43368` | b | diff read: the sample's only walk pattern; under `-fno-landmark-walk` it reads 35,231 again (measured), its stamps unchanged; re-recorded with the reason | `run_cpset_structure.sh` standalone: 29 PASS, 0 failed |
| findings | `§8 w-c3 c3 RX_REQ_WHY default='dominated' (pinned 'emitted')` | b | the c3 witness `a+c` takes the walk at default; `(?:a+c)+` keeps the same G1 identity flip (emitted -> dominated under the bundle) on the unanchored scan, which the walk declines (the landmark recurs in the prefix) | `gen_adversarial.py witness`: 5/5 PASS |
| startset | `[vm-movers] 27 not in the manifest` (all tests/landwalk/landwalk.rxt); `[dfa-route] 7 violation(s): DFA_SCAN landmark-walk`; `[dfa-deny] 2 violation(s)` (reseed.rxt:15, :117); `[dfa-movers] 2 not in the manifest` (landwalk.rxt:224, :246) | b | `dfa-route`: the hat of a walk artifact sits in the relocate's unanchored scan (checked on `\b[a-z]+@x\b`: the skip and conditional re-seed follow `search_from = lmwalk_start;`), so the rule admits `landmark-walk`. `dfa-deny`: under the class deny the deny arm (no hat) ADMITS the walk where the hat arm does not (`(?:\b\|xy)a`: `landmark-walk` vs `unanchored`, measured), because the walk reads NEXT; `-fno-landmark-walk` joins `CLASS_DENY`. The two manifests: the movers are new corpus blocks (landwalk.rxt); **OWED**, from the census (queued `708-p1tri-census`) | OWED: census then a startset run |

## STATE AT HANDOFF

- **Branch** `lane/p1build`: the merge d5c031454 and six p1tri commits over it (last: the report).
  Rulings file `p1tri_rulings.md`: "(none yet)" at every read (last: before the report commit).
- **Queued, OWED** (all in the queue, prio 708/709, owner p1tri):
  `708-p1tri-census` (the startset mover census, manifests to
  `$PCREC_TMPDIR/scratch/p1tri/census2/man/`); the eleven section jobs
  `709-p1tri-sec-{registry,codegen,search-pinned,start-landing,prechecks,cpset-structure,findings,memfn-manifest,memfn-arch,memfn-guarded,recursion-identity-locked}`
  (each `make test-X` on this tree, verdict = make's `*** [test-X] Error` line in its job.log);
  `709-p1tri-test` (make, strict, the identity gate at FILEPIN 379b84fac, the full `make test` via
  perfrun; `not-before 2026-10-31T08:00`, cap 3600; checked by `add`'s dry run: 81 sections).
- **OWED before 709-p1tri-test runs green:** re-pin `tests/startset/manifests/manifest_s2_vm_forced.tsv`
  (+27, landwalk.rxt) and `manifest_s3_dfa.tsv` (+2, landwalk.rxt:224, :246) from the census output:
  diff the corpus rows of `census2/man/` against the committed files, expect ONLY landwalk.rxt rows
  added (any other moved row is a finding), keep the bench rows as committed, add a dated header
  line, then `make test-startset`. Without it the full job reads startset red.
- **A stray waiter:** my first census attempt, `scripts/boxlock run --label p1tri-census` (pid
  2978203, output `$PCREC_TMPDIR/scratch/p1tri/census/`), is still yielding to the queue; my
  `safekill` of it was refused by the permission classifier. It is harmless (scratch output only) but
  will take the box once the queue drains: the manager may `scripts/safekill 2978203`.
- **Not touched:** 711-p1build-mech, 712-p1build-timing, [LANDWALK-PRES].
- **Landing notes (unchanged from p1build):** abi 95 provisional (re-number if 94/95 are taken);
  re-pin FILEPIN to the landing merge; the S693 AFTER follows main's number at landing.
