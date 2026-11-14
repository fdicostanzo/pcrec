# s2tri — triage of the S2 landing's cloud reds ([RUN-POS-SET] stage 3 flip)

Lane s2tri (opus, 2026-11-13), on `lane/s2land` (worktree `worktrees/s2land`), after lane
s2land ended. Inputs: s2land_report.md (expected-mover table), rps3b/rps3c reports, cloud
test run 43526131486 and axes run 43526187676 (both at `f80e45a92`). Work split over six
helper subagents in the same worktree (disjoint files, named-path commits), coordinated
here; every commit below is on the branch.

## STATE AT HANDOFF

- STATE: delivered-with-owed. Every red of both cloud runs is classified and fixed on the
  branch; no src/ or memfn/ file was edited. No rulings file was named in the brief.
- Root cause of every red: the flip `PCREC_MAX_REQ_RUN_POS_SET` 2 -> 128. A class of up to
  128 members (`\d`, `[a-z]`) and an alternation's union are now run POSITIONS (set-form
  `RX_REQ_RUN`, tuning.md §2.28¶7), so runs, K, landmarks, REQ_BYTE picks, prefilters and
  sizes move, and witnesses whose point was "this class is NOT in the run" stopped reaching
  their sites. No red was a wrong answer: the corpus `gu` reds were the stronger run PROVING
  nomatch where the control expected a give-up (PCRE2 and python agree: nomatch).
- Local validation before 20:00 (box free, single sections, one at a time), all at or after
  `013dd5fc1` unless named: `make -k test-prechecks test-memfn-finder` rc 0;
  `make -k test-memfn-reach test-memfn-rows test-memfn-deleg test-cand-oracle test-cli
  test-encoding-checks test-cpset-structure test-findings test-memfn-simdfloor
  test-startset test-fallback-table test-island` (at `5d5ceffb6`): every section green but
  test-island (fixed in `013dd5fc1`, then `make test-island` rc 0);
  `make -k test-rxtsource test-compound test-codegen test-registry` rc 0;
  `tests/harness/run.sh` on the two re-aimed corpus files: 303 passed, 0 failed, and
  `verify_rxt.py` on them: ALL CHECKS PASSED; `scripts/m6read_check_sab_anchors.py`: 1295
  rows, all anchors resolve.
- `REACH_ONLY=1` full matrix at `013dd5fc1`: 15 rows unreached that reach on main's
  pre-flip binary (all flip movers); re-aimed (below). Second full run at `f28a0aa50`
  (the last test-bearing commit): `mech-reach-only: DONE rc=0 rows=1295 reached=627
  unreached=0 declared-unreached=16` (log `/var/tmp/pcrec-pcrec/scratch/s2tri/reach_all2.log`).
- Commits after `f28a0aa50` are this report and its index entry only. Cloud runs and the sweep are OWED (below).

## REDS

Cloud test run 43526131486 (shards 2 3 6 7 8 10 11 12 13 15 17 red, 1 4 5 9 14 16 18
green) and axes run 43526187676 (all 20 shards: "the BASELINE run itself failed").
Logs: `/var/tmp/pcrec-pcrec/scratch/s2tri/test/shardN.log`, axes shard 4 artifact under
`.../s2tri/axes/a4/`.

| red (section) | class | cause |
|---|---|---|
| axes baseline, all 20 shards; test-corpus (shard 2, 6 cases); test-memfn-finder [deny-answers] x3 "failed 2"; test-findings sampled-slice check "bundles=0/11" | (a) witness | k66_precheck_whole_run.rxt:45/:58 and reqcube.rxt:442/454/489/502 `gu steps` controls answer NOMATCH: K66's run is now `[a-z]eeeeeeee~#~#~#~#` and S2b/S2c's `S[0-9]...`, which the subject lacks, so the pre-check proves nomatch (correct; the control can no longer exist with that pattern) |
| test-prechecks [5.9]/[5.9r], test-memfn-finder [k382-one-part] (4 of 8) | (a) witness | the same K66 run, no longer the 16-byte compare |
| test-prechecks [3.1r]/[3.1b], [3.7]/[3.7b], [4.5]/[4.5c], [4.7], [5.11], [5.12a], [5.12h], [5.12n] | (a)/(b) | runs through unions/classes; one reader (`run_scan_members`) could not read the set spelling |
| test-memfn-simdfloor (x86-64, x86-64-v3 named witnesses not movers) | (a) witness | `(?i)\w+cat`-shaped witnesses' class joined the run |
| test-memfn-reach php handoff K 6 | (a) pin | the union tails are run positions: K 3 |
| test-memfn-rows arms/precheck_assign_byte; renderer R7w/pf_walk `foo|bar\d` | (a) witness | `(?:\d{1,3}\.){3}\d{1,3}` has a set run (no byte landmark); `foo|bar` is a run (no FIND site) |
| test-memfn-deleg C10 `x\d{3}abcde` | (a) witness | the whole pattern is the run (K 0, no handoff) |
| test-memfn-finder pr11 traceback | (b) reader | `bytes.fromhex` on a bracketed position |
| test-memfn-finder [alias] population 2 < 4 | (a) witness | `(?:é|ü){2,3}` became run positions, the set-lead deny moved nothing (K35) |
| test-cand-oracle reach set-leads / handoff-attempts-entry | (a) witness | same `(?:é|ü){2,5}` cause |
| test-cli `--memfn=no-precheck-assign-byte` did not move dotted4 | (a) witness | as memfn-rows' arm |
| test-fallback-table seq-pfclow/pfcd2/isldrop/islnone/isl1000, att-scpfc, note-isl | (a) size mover | set runs add handoff/verify bytes; the ladder lands one rung later or refuses |
| test-island CAP GUARD N=300/340, RETRY | (b) check | the island attempt fires `drop-handoff` before `drop-islands` (cumulative `fit_rungs[]`); the shipped artifact is the chain's WITHOUT the handoff, the `-fno-alt-island` build keeps it. Diff = REQ_HANDOFF + the handoff block only |
| test-cpset-structure manifest drift | (a) pin | `cat|dog|cow|calf|camel` +26 emitted bytes (new run, `untestable`), diff read |
| test-findings §8 w-c2a/w-c2b | (a) pin / witness | `[0-9]` joined the run |
| test-encoding-checks DD12a(i) traceback | (b) reader | `int(hx..,16)` on `[` |
| 15 mech REACH probes unreached (local REACH_ONLY at `013dd5fc1`) | (a) witness | S1700 S1703 S266 S268 S456 S461 S465 S469 S477 S490 S515 S607 S805 S808 S809: each REACHES on main's pre-flip binary, not on the tip |

No (c) real pcrec regression was found. No (d) kit-side defect was found.

## FIXES

Commits on `lane/s2land` after `c48af8313` (helper tag in the subject):

- `5d5ceffb6` (coordinator) K66 and S2b/S2c witnesses re-aimed with `.` before the run:
  `(x?)([a-z]+)+.eeeeeeee~#~#~#~#\1` (16-byte run and `@14` restored; the `gu` subject
  `...Z!eeeeeeee~#~#~#~#` has no letter before the separator, oracle nomatch) and
  `(x?)([a-z]+)+S.(?i:select)\1` / `S.(?i:s)qz\1` (gen_reqcube.py, regenerated). Readers by
  grep: run_prechecks [5.9]/[5.9r], run_presence k382 LED, S278/S452 REACH (S452's
  `rq_set[] = { 83 }` read MISSING on the tip, restored), startset s2 manifests (pattern
  hex), findings ship_* movers, run_axes comments, two CLAUDE.md. Line numbers kept, so the
  axes allowance keys (k66 :38-43/:51-56, reqcube :438..499) hold.
- `013dd5fc1` (coordinator) test-island: the chain leg adds `-fno-req-handoff` exactly when
  the island build's stderr carries the drop-handoff note (the rung that fired, read from
  the note); byte-for-byte comparison otherwise unchanged; N=300/340 and RETRY equal.
- h1 `3d70b9997`: run_prechecks reader for the set spelling; re-pins with hand
  re-derivations ([3.1r], [5.11] 日本|日曜|日付, [5.12a] straße/ab(?:cdef|xyzdef)g/
  (?:ab|c)(?i)select/(?:\Gab|x) K, [5.12h] K 1, [5.12n] K 2); `.` re-aims ([3.7] fillers,
  [4.5] `github_pat_.{4}`, [4.7] `(?:x.abcy|wabc.v)q` and `a.b.=`, [5.11] `cat.+sate`,
  `(?i:xqz).+e`, `(?i:elect).+=`, [5.11c], [5.12a] dotted4/ipv6 with `.`), simdfloor
  witnesses `(?i).+cat`, `(?i)(.)+cat`.
- h2 `34597ce4f` php K 6 -> 3 (+S1707 reach); `703b30115` precheck_assign_byte arm
  `(?:.{1,3}\.){3}.{1,3}` (rows.tsv, test-cli) and R7w `f.o|b.r\d`; `f4a3c8a3d` C10
  `x.{3}abcde` (hand values unchanged); `04afae162` pr11_front.py reads set positions;
  `3d26aabb3` alias witnesses `(?:é.|ü.){2,3}...` (population 5); `893d59724` cand-oracle
  witnesses `(?:é.|ü.){2,5}...`.
- h3 `85c30efe4` DD12a(i) reads the set spelling (and admits `(?<=a{1,2})(?:foo|fob|fox)`'s
  run-pinned utf8 form, declared by the OFFSETS stamp); `730fc14b5` fallback-table
  witnesses (`(?:a\K){2,}.`, `\W` -> `.`, W_ISLSIZE 24 -> 19, seq-isl1000 gains
  drop-handoff); `e0d7d2e78` cpset manifest re-recorded (one row, diff read);
  `f06449682` findings w-c2a re-pinned, w-c2b re-aimed `.abcdefghijkl.+`.
- h4 `a1cf8cc5e` S805/S808/S809 probes read the byte-landmark witnesses (dotted4 with `.`,
  handoff.rxt ipv4), S266 reads §3.7's `.+x.+e.+`; `f28a0aa50` S461 probe on [5.11c]'s
  witness AND its plant re-anchored to `pcrec_find_pos_mass` (the old plant is an equivalent
  mutant on the tip: scratch builds clean 120, old plant 120, new plant 122).
- h5 `a2a0aab97` S1700/S1703/S469/S607/S490 probes re-pinned or moved to their detectors'
  own witnesses (no detector changed).
- h6 `a15144c2c` S268 on §4.7's `(?:x.abcy|wabc.v)q` (+ `27d09cb5e` its doc figure, planted
  build); `648fdff71` S456 `frank|fred` set run; `979c22cbb` S465 on §5.12a's `.{3}cat`
  utf8 (K 12, plant 3; straße no longer separates the plant); `5850a43ea` S477 K 1;
  `f42ef03dd` S515 libc record `memchr,memcmp`.

FINDING (not changed, for the manager): the size-cap ladder is cumulative and takes
`drop-handoff` before `drop-islands`, so an island-bearing alternation near the cap ships
without its handoff even where dropping the islands alone fits (N=300/340 and the
1,000-word set). Answer-identical; a speed loss only under the cap. Worth a plan row if
the order matters.

## KIT-SIDE

None found. Every memfn-seam red (rows, deleg, finder, reach, cli) was a pcrec-side
witness or reader; the kit rows (precheck_assign_byte, pf_walk, set-lead, presence) fire
on the re-aimed witnesses as before. The renderer witness change (`f.o|b.r\d`) names the
kit's plants S2983/S2984 as still SILENT-MOVE-detected (h2, measured by rows_check);
those are memfn's own mech rows, not in tests/mech, so the kit should re-run them.

## OWED

- CLOUD (dispatched at the final tip as this lane's last act, not waited for; verdicts by
  CLOUD-DONE to main): `--kind test --name s2tri`, `--kind axes --name s2tri-axes`,
  `--kind mechrows` over S3128 and the rows this lane touched or whose detector witness
  moved (30 ids): S3128 S278 S452 S3048 S1707 S1700 S1703 S266 S268 S456 S461 S465 S469
  S477 S490 S515 S607 S805 S808 S809 S471 S472 S813 S1923 S453 S800 S801 S802 S803 S804.
- QUEUED `200-s2tri-sweep` (owner s2tri, `boxqueue: not-before 2026-11-14T01:00`):
  `emit_sweep.py --ref 0b7a2ece5 --movers-out
  /var/tmp/pcrec-pcrec/scratch/s2tri/sweep_main_movers.tsv` on the tip; a MEASUREMENT
  (movers expected, s2land_report.md's table), green when the movers file is written.
- s2land's OWED items stand unchanged (provisional run-verify-wide DIFFER floors,
  stage-6 arms pins, D3 floor, the D27 witnesses, rule (1), rps3's STOP note); the arms
  sweep (`--arms start --emit-pins`) was not re-queued (the brief allows only the sweep).
- The full mech matrix on the final commit (the manager's), and the kit's S2983/S2984.
- Mid-lane helper handbacks did not reach the coordinator (unnamed subagents ended without
  a delivered report); every claim above is read from the commits and re-measured here.
