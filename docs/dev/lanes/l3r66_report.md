# l3r66 report: review r66's rulings applied to span_arms L3

Lane l3r66 (opus), 2026-11-21. Branch `lane/l3r66`, cut from `lane/l3chk` dad027580. Review:
docs/dev/reviews/2026-11-21-r66-l3fix.md, its "Rulings (manager, 2026-11-21 01:40)". Scratch:
`/var/tmp/pcrec-pcrec/scratch/l3r66/` (not committed). BASE = `694d91dc4`, the `git archive` export
lane l3r65 built clean (`scratch/l3r65/base/`; `src/facts/req.c`, `src/facts/facts.c` and
`src/gen/emit_dfa.c` checked byte-identical to `git show 694d91dc4:<path>`). Every instruction count:
`perf stat -e instructions:u`, `taskset -c 7`, `-r 5`, a 1 MiB buffer of the named text searched 5 times
(`scratch/l3r66/perf/m.sh TAG PCREC PATTERN TEXT [flags]`, the critic's driver; fill floor ~9.0M).

## Summary

Both speed findings are fixed and back at BASE, and no answer moved.

- EMIT-2: `fwd_reentry` is now true under `--engine=vm -fprefilter`. `(?<=qz)x?a:` on English text is
  8,998,888 instructions, the same as BASE.
- EMIT-3: BACK's `displaces` now reads the root's necessary set. An empty consumed run whose set has a
  member at a static bound keeps BASE's byte-landmark handoff. `(?<=qz)(?:a.|.a)` is at BASE on qz-dense
  and on English text. The English x6 win is given up and filed as plan row [L3-BYTE-LANDMARK-WIN].
- The six r65 A patterns emit C identical to BASE apart from the abi digits, and every cell reads 1.000.
- Census BASE -> SUBJECT: the default streams and `--engine=vm` are unchanged from l3r65. The new
  `--engine=vm -fprefilter` stream moves only the default's 2 patterns.
- Checks: 8 new [facts-look] cells, multi-flag support in its reader, a DD12a(i) one-sided-run floor,
  1 default-route answer block, and sabotage rows S3480-S3485 (6). S3383 and S3455 are re-anchored.
- Records: facts_listing §4.1.2¶8, span_arms REV 3.5, D191 addendum 3, three plan-row edits and two new
  rows, the critic skill's line, and the cpset comment.

PREMISE TEST (reproduced before any edit, on the unmodified branch tip dad027580):

| pattern / flags / text | BASE | SUBJECT (dad027580) |
|---|---|---|
| `(?<=qz)x?a:` `--engine=vm -fprefilter`, English | 8,998,887; `handoff`, `613a@1`, K 1 | 14,170,843; `memchr`, `717a@1`, K -2 |
| `(?<=qz)(?:a.\|.a)` default, `qz bqz cqz ` | 8,998,891; `handoff`, no run, K 1 | 39,964,842 (x4.4); `byte-class`, `717a@1`, K -2 |
| `(?<=qz)(?:a.\|.a)` default, English | 85,622,145 | 14,170,871 (x6 win) |

Commands: `m.sh BASE scratch/l3r65/base/build/pcrec '(?<=qz)x?a:' "the quick brown fox jumps over the lazy dog " --engine=vm -fprefilter`, and the same for the SUBJECT binary and for the other pattern and text. English = `the quick brown fox jumps over the lazy dog `. These are the review's figures (9.0M -> 14.2M; x4.4).

## EMIT-2

The fix is in `src/facts/facts.c`:
`.fwd_reentry = !pcrec_opt_has(cx->opt, PCREC_NO_REQ_HANDOFF) && (cx->opt->engine != PCREC_ENGINE_VM || pcrec_opt_has(cx->opt, PCREC_FORCE_PREFILTER))`.
It still reads only the options. The three texts are restated: the field comment in
`src/facts/facts_derive.h`, span_arms §14.4 L3 REV 3.5, and facts_listing §4.1.2¶8 ("every compile but
`--engine=vm` without `-fprefilter`, or `-fno-req-handoff`").

AFTER (`scratch/l3r66/perf/emit23.tsv`): BASE 8,998,888 -> FIX 8,998,888. Both have stamps `handoff`,
`613a@1` and `REQ_HANDOFF "1"`. On `zz qza: qzxa: a: ` both trees return 5 matches (the driver's sum
over 5 searches).

[facts-look] cells: `--engine=vm -fprefilter (?<=qz)x?a:` lists `req_whole_run 613a` and
`req_landmark_maxoff 1`. To support these cells, the reader's flag column now splits on spaces
(`read -ra`). The plant is S3480 (the `-fprefilter` disjunct becomes `false`).

## EMIT-3

The fix is one declared row condition in TOP's BACK row (`src/facts/req.c`). The row type's
`displaces` column gains the root's necessary set (`const RbSet *set`), and `rb_top` passes `&v->set`.
`rb_top_back_displaces` is one boolean expression with three disjuncts:
`!w->fwd_reentry || (best->n == 0 && !rb_set_bounded_landmark(set)) || (lo < hi && best->off >= PCREC_W_UNBOUNDED)`.
`rb_set_bounded_landmark` asks whether any member has `RbSet.off < RB_OFF_UNBOUNDED`.

The condition is wider than "the picked member is bounded", on purpose. The `req_byte` pick is a
derived rate choice that the core walk does not read (the layering of src/facts/req.c's header). The
wider answer can only keep BASE more often, which is the direction that cannot lose against BASE.

AFTER (`emit23.tsv`):

| text | BASE | FIX |
|---|---|---|
| `qz bqz cqz ` | 8,998,892 | 8,998,891 |
| English | 85,622,144 | 85,622,144 |

Both trees stamp `handoff`, `REQ_RUN "none"`, `REQ_HANDOFF "1"`. On `qzab xqzba qa ` both return 5.

The English win (x6) is given up and filed as plan row [L3-BYTE-LANDMARK-WIN]: trigger L2's design, or
a bench pattern that reaches the shape. Its numbers are in the row. [facts-look] cells: by default
`(?<=qz)(?:a.|.a)` lists no run with landmark 1; under `--engine=vm` it lists `717a` at -2. The plant is
S3481 (`best->n == 0` without the landmark conjunct).

RE-CHECK: THE SIX r65 A PATTERNS. Command: `scratch/l3r66/perf/build.sh {base,fix} PCREC` then
`run.sh base fix results.tsv` (l3r65's scripts repointed; the subjects are l3r65's `perf/subj/`). The
medians of 5:

| pattern | absent | rare | common | decoy | emitted C |
|---|---|---|---|---|---|
| `-i (?<=foo)bar` | 2,588,089 -> 2,588,087 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |
| `-i (?<=item )done` | 2,438,162 -> 2,438,163 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |
| `(?<=a)\Kb` | 2,459,061 -> 2,459,061 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |
| `(?>(?<=a)b)` | 2,471,707 -> 2,471,706 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |
| `(?<=qz)x?a:` | 225,059 -> 225,059 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |
| `(?<=x)qzjv[a-z]*\d` | 1,518,587 -> 1,518,588 | 1.000 | 1.000 | 1.000 | same apart from the abi digits |

The answers are identical in every cell.

THE CENSUS, BASE -> SUBJECT. Command: `python3 -I scratch/l3r66/census.py
scratch/crit-l3feat/emitted/lb.txt scratch/l3r66/census_lb.tsv`. This is l3r65's script with SUBJ
repointed and one new stream, `vm-pf` = `--engine=vm -fprefilter`. The population is the 428 corpus
`(?<=` patterns.

| stream | SAME | ABI-ONLY | DIFF |
|---|---|---|---|
| byte | 41 | 385 | 2 |
| `-i` | 41 | 385 | 2 |
| utf8 | 37 | 389 | 2 |
| `--engine=vm` | 41 | 294 | 93 |
| `--engine=vm -fprefilter` (new) | 58 | 368 | 2 |

- The default movers are `(?<=foo)` and `(?<=xyz)a+xyz` on every default stream, as at l3r65. The
  `vm-pf` movers are the same 2 patterns.
- `RX_DFA_PREFILTER` moves on no cell.
- The program region is identical on all 2,140 cells.
- No corpus pattern reaches EMIT-3's shape, so the census does not move with that fix.

## Checks

- **[facts-look]** (tests/codegen/run_facts_checks.sh) gains 8 cells: the 2 EMIT-2 cells, the 4 EMIT-3
  cells (default and `--engine=vm`), and CHECK-2's optional byte-side pins for `(?<=a)(b)\1x` (`6162`,
  -1). It has 71 cells. RE-RAN STANDALONE: `bash tests/codegen/run_facts_checks.sh` (the file that
  `test-codegen` chains), 16 passed, 0 failed.
- **CHECK-1** (tests/codegen/run_encoding_checks.sh): `RUN_ONE_SIDED` is now read, with a floor of 2
  (`RUN_ONE_SIDED_LANDING=2`, the two reaching pairs). S3485 plants the arm's red branch: the run-scan
  term becomes `set()`.
- **CHECK-3**: tests/litscan/spanarms.rxt gains a default-route block for `(?<=xyz)a+xyz` (5 subjects at
  every start). Every cell is libpcre2-8's (tests/lib/p2probe.c built in scratch). RE-RAN STANDALONE:
  `bash tests/harness/run.sh tests/litscan/spanarms.rxt` gave 2169 passed, 0 failed.
- **CHECK-2** comments are restated at the 2 run_encoding_checks.sh sites and in S3450's RE-AIMED comment.
- **CHECK-4 plants as rows**:
  - S3482 (no empty-best arm) is red on `(?<=foo)`.
  - S3483 (no unbounded arm) is red on `(?<=xyz)a+xyz`.
  - S3484 (no engine clause) is red on the `--engine=vm` cells.
- **Sabotage**: S3480-S3485, 6 rows. Their REACH lines print their tokens on the tip, and
  `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S3480 S3481 S3482 S3483 S3484 S3485 S3455 S3383`
  reports 8 definitions valid. S3383 and S3455 are re-anchored (`rb_top`/`displaces` gained the set
  argument; their intent is unchanged). `scripts/m6read_check_sab_anchors.py` resolves all anchors. The
  plant verdicts are in "Validation dispatched".
- **Pins** re-pinned for this lane's +1 block, each with its reason line:
  - rxtsource CENSUS/RUNSH 7265 / 101830, C3_PASS 26330, C3_VERIFIABLE 28749. Re-ran
    `bash tests/rxtsource/run_rxtsource_tests.sh`: 0 failed.
  - manifest_s2_vm_forced.tsv +1 row (`spanarms.rxt:3058 --features all`). Re-ran
    `bash tests/startset/run_vmhat_checks.sh`: rc 0.
  - `run_startset_checks.sh` and `run_dfahat_checks.sh`: rc 0 with no re-pin.
  - Before touching each pin file I ran `git log --since=14.days`. Each earlier re-pin had a different
    cause, so none is a second re-pin for one cause.

## Docs and records

- **facts_listing §4.1.2¶8** (EMIT-1/2/3, written once): the landmark wording now covers the run or a
  bounded set member, and the `-fprefilter` route. It also says that the consumed run of any length,
  including one byte, is "not empty". Examples added: `(?<=qz)(?:a.|.a)`, `(?<=foo)b`, and
  `(?<=foo)bar` under `--engine=vm -fprefilter`.
- **span_arms §14.4 L3**:
  - TRADE-3: RECORD (b) quoted.
  - TRADE-2: the owner's words quoted verbatim, with their home on main
    (docs/design/plan_row_bodies/REQ-LOOKAROUND.md, the LEAN paragraph, landed after this branch's base).
  - New REV 3.5 addendum: both fixes, their counts, the plants, the six patterns and the census.
- **decisions.md D191 addendum 3** (TRADE-4): the pick rule's record, as an addendum to the L3 entry.
  It covers the narrowing, who made it under which record line, and the un-do triggers [L3-CONS-REENTRY]
  and [L3-BYTE-LANDMARK-WIN].
- **plan.md**:
  - [L3-CONS-REENTRY]'s ref names the LEAN's real home (TRADE-2).
  - [L3-BOUNDED-RUN-REFINE] notes EMIT-1's speed half.
  - New [L3-BYTE-LANDMARK-WIN] (EMIT-3's given-up win).
  - New [WTPRUNE-QUIET] (the PROCESS teardown leak).
  - `scripts/plan_lint.sh`: 0 violations.
- **.claude/skills/pcrec-critic/SKILL.md**: one line, a fix-up round also builds the REVIEWED tree with
  a `reviewed` tree-selector value.
- **TRADE-1**: run_cpset_structure.sh's RE-RECORDED hunk is replaced by a 5-line statement that no row
  moves against the abi 109 base (the manifest is at 38505).
- abi stays 110. No emitted scaffolding changed: the census shows only fact choices and the abi digits.

## Validation dispatched

LOCAL RUNS (complete, on this box, nice):
- `bash tests/mech/run_sabotage_matrix.sh S3480 S3481 S3482 S3483 S3484 S3485 S3455 S3383` at e8a191b99
  (`scratch/l3r66/mech.log`) printed `== mech run COMPLETE: 8 rows (unexpected: 0, undetected: 0,
  unreached: 0, anomalies: 0, oracle-skipped: 0)`. All 8 were DETECTED: the 7 facts rows each give
  facts 1fail/15pass, and S3485 gives encoding 1fail/14pass (baseline 0 fail).
- D3 floor: `PROCS=4 bash tests/memfn/run_d3floor.sh` (`scratch/l3r66/d3.log`). All 4 cells are green
  and 60 of 60 plants are ok, so no re-pin was needed.
- Other local runs: `make strict` clean; `bash tests/codegen/run_facts_checks.sh` 16/0;
  `bash tests/rxtsource/run_rxtsource_tests.sh` 0 failed; `bash tests/startset/run_startset_checks.sh`,
  `run_vmhat_checks.sh` and `run_dfahat_checks.sh` rc 0; `bash tests/harness/run.sh
  tests/litscan/spanarms.rxt` 2169/0; `scripts/plan_lint.sh` 0 violations;
  `scripts/m6read_check_sab_anchors.py` all anchors resolve.

CLOUD (dispatched as the last act; verdicts reach main through queuewatch): `scripts/cloudrun --owner main
--kind test --ref <tip> --name l3r66-test` and `--kind axes --name l3r66-axes`. The tip sha and the
ls-remote proof are in the handback message (the tip is this report's commit).

## STATE AT HANDOFF

STATE: delivered. Branch `lane/l3r66`, all work committed.
- Code: `src/facts/facts.c` (EMIT-2), `src/facts/req.c` and `src/facts/facts_derive.h` (EMIT-3, comments).
- The stop rule never fired: no answer moved, each fix is one declared row condition, and no loss
  against BASE is left on any measured cell.
- abi stays 110.
- Rulings file: `docs/dev/lanes/l3r66_rulings.md` is empty, so no R-n was applied beyond the brief. I
  re-read it before each commit and before this report.
OWED: none. The two cloud runs (l3r66-test, l3r66-axes) are dispatched, and their verdicts reach main through queuewatch.
- Not done, and not asked for:
  - An answer cell for `(?<=qz)(?:a.|.a)`. Adding one adds a new corpus pattern and moves more pins; the
    listing is pinned by [facts-look], and the critic's 43 answer cells held.
  - A `-fprefilter` answer block. The .rxt format has no optimization-flag line, and the [facts-look]
    cell pins the listing.
- Box use ended at 01:22 local.
