# s2rev14 report: span_cards rev 1.4, the kit manager's R14-1..R14-4 on the first S2d window (design + code)

Lane s2rev14 (opus), worktree `worktrees/s2c`, branch `lane/memfn-s2c`, from ce88f1766. Scratch:
`/var/tmp/pcrec-pcrec/scratch/memfn/s2rev14/`. Nothing queued. No timing run, no `make test`, no mech.
STATE: delivered.

## Summary

- **R14-1 (null base = the arm's own loop).** `link.py` renders `base.null.<cls>` from the class instance's
  compare wrapper text, the same text the arms use. Only the site body differs: it becomes
  `slot_null(<the body's first load>)`, so the load is kept at the arm's width (a memcmp's run becomes one
  `slot_ld` of its length). In place of the compare there is a 1 that gcc cannot fold. The candidate loop in
  the wrapper is now an explicit pointer bump, for arms and bases alike.
  - In objdump the base and its arm now share their addressing (a pointer bump plus `(%rdi,%rcx)`), their
    32-byte loop alignment and their load width. The compare instruction is the difference.
  - The new `null_check` refuses a base whose text differs from its class arm's outside the body. It also
    refuses a base that keeps a load the arm's body never makes.
  - In `gen.c`, a null base's gate now counts every candidate.
- **R14-2 (sub-resolution).** A delta row that fails the NULL rule is still MEASURED when `|med(x_l)| <= r`.
  - r is 3 x isqrt_rn(K_MED x sp2): three standard errors of the row's median. sp2 is the spread from §3.4 step
    6 and K_MED is the constant from §3.5¶6.
  - Such a row gets value `max(0, med)` and noise `max(r, noise)`.
  - NULL still applies when `|med| > r`.
  - The spec text is `measures.md` §3.5¶3a (new), with §3.5¶3 and ¶11 amended. There is no change to the format,
    the noise state or the seam.
- **R14-3.** Every quiet check now logs load1 and the top 5 co-runners from ps (`pid:comm:%cpu`). They go into
  the transcript, and finalize copies them into the record's new `quiet` section. The dry run takes one
  ungated sample and refuses a line that has no co-runners (QUIET-LOG). est's `notes()` names any job whose
  control shows a launch-level fast/slow split. That note goes into the rows output, into the record
  (`note_box_state`) and into the draft as a `# note` line.
- **R14-4.** Delta rows now print `ungated`. A second note, `note_bimodal`, names the priced delta rows whose
  launches fall into two clusters, in the record and in the draft.
- **Replay** (R14-2 and R14-4 only; R14-1 cannot be replayed because the cells were taken with the old base):
  - Four floors now pass: `verify.rc-memcmp.l1`, `verify.rc-words.w1`, `verify.settest.c1` and
    `verify.settest.c2`.
  - `floor:byte.libc` still fails its gate (3.3 % over 3 %), as expected, so the outcome is still REFUSED on
    that one floor.
  - The closest call is c1.p50: |med| 0.093 wb against r 0.097 wb.
- **Sabotage.** Six new slot-local rows, S2940-S2945, all DETECTED. All 17 slot rows are DETECTED, and the
  control is green (numbers in Validation).

## Rev 1.4 text

`docs/design/memfn/span_cards.md` is now rev 1.4. Changes:

- A new **§R1.4** with the ruling table (R14-1..R14-4, where each is answered), r's derivation and branch, and
  the replay.
- §2.3: the `verify_cmp` estimator's base.
- §3.2: "The `null` verify base", rewritten.
- §3.3: the co-runner log at each quiet check.
- §3.5:
  - the delta-rows paragraph (the sub-resolution branch and `ungated`);
  - the run record table (the `quiet` section, and the `note_box_state` / `note_bimodal` keys with their
    thresholds);
  - three new constructed-outcome rows.
- Goal 2: a sub-resolution row counts as priced.
- STATE AT HANDOFF.

**Spec hunks**, cited by section only: `measures.md` §3.5¶3 (failing rows defer to ¶3a; "beyond the row's
resolution"), §3.5¶3a (new: r, the branch, value, noise, priced) and §3.5¶11 (a sub-resolution row is priced).

**No format change was needed.** A sub-resolution row is a format-2 `measured` row with a legal value (0 is
allowed) and a numeric noise. r is defined from the row's own cells, so it needs no table, no field and no
producer rule. The draft's notes are `#` comment lines, which `tests/knowledge/ks_ref.py decode` reads cleanly
(see the format exercise below).

**r and when a row takes the branch.**
- **Derivation:** r is three standard errors of the row's own 7-launch lower median. This is the same scale
  and factor that drift uses in §3.5¶6. So r is the size the row's own launches cannot tell from zero.
- **Comparison with the analysis's "about 0.1 wb":** that figure is the trimmed launch spread itself. On the
  first window, r for the eight failing verify rows came out at 0.097-0.165 wb, and their |med| was
  0.019-0.099 wb.
- **Branch:**
  - A row that fails the NULL rule with |med| <= r is a measured sub-resolution row.
  - With |med| > r it stays NULL. That covers a consistent negative beyond r (a fixture defect) and mixed signs
    or a below-A/A result at a size above r.
  - A row that passes the NULL rule is priced exactly as before.

**Note thresholds** (they gate nothing):
- The split note fires on a gap over 0.5 % between two clusters of at least 2 launches in a job's control.
- The bimodal note fires on a gap over 10 % of the row's value.
- Both are labelled UNMEASURED DEFAULT (D149) in `est.py`.

## Code

All files are under `docs/design/memfn/span_cards/slot/` unless a full path is given.

- `link.py`:
  - `SLOT_HELPERS` (`slot_ld`, `slot_null`, with an opaque 1);
  - `NULL_LOADS` (a first-match table of the three load spellings), `null_body`, `null_check`;
  - the null branch of `render` (renders the class instance, then swaps the body);
  - the WRAP_CMP loop is a pointer bump;
  - the NULL-BASE check in `build_objs`, which prints `null-base: N bases ...`.
- `gen.c`: a null base's gate expectation is count E, with the position sum and FNV over every candidate. Its
  header comment is updated.
- `est.py`:
  - `resolution`, `split_gap`, the sub-resolution branch in `compute`, `notes`;
  - the `ungated` print and `note` lines in the rows output;
  - the draft's `# note` lines and the source text `slot J<j> sub-resolution r N`;
  - six new self-test cases (row predicates).
- `run.py`: `corunners` (ps, top 5, excluding its own process and ps), `QUIET_TOP`, the co-runner field in
  `quiet_now`, and the dry run's one ungated quiet sample (QUIET-LOG).
- `record.py`: the `quiet` section (`quiet_rows`), and finalize writes est's two note keys. A note that cannot
  be computed is written as `unavailable: ...`.
- `sabotage.sh`: rows n1, n2, s1, s2, q1, b1.
- `docs/spec/measures.md`: the hunks above.
- CLAUDE.md files: `slot/`, `span_cards/`, `s2d1/`.
- `s2d1/rev14_replay_rows.txt`: the replay's est output.

Commits (`git log ce88f1766..HEAD`):
- f4cc04c2a: s2cfix2's deliver file, as written;
- 076936d83: R14-1;
- aa07be2b2: R14-2..R14-4 and the spec hunk;
- 63d1b117f: the design text, the sabotage rows and the replay file;
- the commit carrying this report.

## Replay over the first window

How it was run:
- `cp -r` of `/var/tmp/pcrec-pcrec/scratch/memfn/s2d/s2d-20261106` to `scratch/s2rev14/replay` (the original is
  untouched).
- `record.py finalize` was re-run there with the run's own states and commit (508178bd2…). This adds the
  `quiet` section and the note keys. Everything else in the record stays byte-equal (checked by diff).
- Then `est.py rows`. Output: `s2d1/rev14_replay_rows.txt`, exit 3.

| floor | rev 1.3 | rev 1.4 replay |
|---|---|---|
| byte.libc | FAIL (gate, noise 3.3 %) | FAIL (unchanged, expected) |
| verify.rc-memcmp.l1 | null (negative) | PASS: p0 value 0 noise 0.152 wb; p50 value 0 noise 0.118 wb |
| verify.rc-words.w1 | null (mixed) | PASS: p0 0.024 ± 0.130; p50 0.026 ± 0.134 wb |
| verify.settest.c1 | null (negative) | PASS: p0 0 ± 0.165; p50 0 ± 0.097 wb (|med| 0.093, the closest call) |
| verify.settest.c2 | null (mixed) | PASS: p0 0.035 ± 0.112; p50 0.019 ± 0.114 wb |

The outcome is `REFUSED exit 3 floor:byte.libc (text)`.

Notes on the replay:
- **Box state:** the split note fires in every job's control: J2 0.94 %, J2p 0.83 %, J3 1.48 %, J4 0.75 %,
  J5 1.72 %.
- **Bimodal rows:** the note names `find_hit.walk.random.one.1024`, `walk.random.one.256` and also
  `walk.periodic.one.1024`. The last one has two high launches (41.2 and 44.7 against about 30.4); the rule
  found it, not the ruling's list.
- **Draft notes cannot be shown by the replay:** est writes no draft on a REFUSED outcome.
- **Format exercise:** a separate copy (`scratch/s2rev14/fmt`) with the byte.libc floor line removed gives a
  PARTIAL draft. Its notes are its 2nd and 3rd lines, its digest is 89915b6a051c508d, and `ks_ref.py decode`
  exits 0.
  - In that draft, the sub-resolution rows keep their raw negative `abs_ns_e6` (provenance, -19349 on l1.p0)
    while `value_e6` is clamped. The decoder accepts it. It is flagged here in case S2e's strip or the loader
    reads `abs_ns_e6` as a cost.

## Sabotage

Ids S2940-S2945 are the slot-local rows in `slot/sabotage.sh`. They are not mech rows: no make suite runs their
detectors.

| row | id | plant | detector |
|---|---|---|---|
| n1 | S2940 | the null base rendered with an indexed loop | `NULL-BASE MISMATCH base.null.c1: its text differs from its class arm's outside the compare` |
| n2 | S2941 | the null base always keeps a byte load | `NULL-BASE MISMATCH base.null.l1: its body 'slot_null(subject[pos])' keeps no load its class arm's body makes` |
| s1 | S2942 | sub-resolution value not clamped | self-test case "consistently negative within r ... clamped to 0" WRONG |
| s2 | S2943 | the `|med| <= r` condition dropped | self-test case "consistently negative above r: null" WRONG |
| q1 | S2944 | the quiet check logs no co-runners | the dry run's `QUIET-LOG` |
| b1 | S2945 | the bimodal note names nothing | self-test case "a delta row in two clusters is named by the bimodal note" WRONG |

## Validation

Every step ran alone; the box carried other sessions' non-timing queue jobs (no timing window).

- `make` rc 0; `make strict` rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- `make test-memfn-finder`: 3272 passed, 0 failed.
- `tests/registry/limits_check.sh`: 39 passed, 0 failed.
- `tests/memfn/run_arch_blind.sh`: 17 passed, 0 failed.
- `make test-plan-lint`: 0 failed.
- `make test-spec-history`: 11 passed, 0 failed.
- `est.py selftest`: 15 cases, 0 wrong (six of them new for R14-2/R14-4).
- `slot/sabotage.sh`: control green (J2 dry run, est self-test); **17 DETECTED, 0 MISSED of 17 rows** (the 11 earlier rows plus n1 n2 s1 s2 q1 b1). Log: `scratch/s2rev14/sab_all.log`.
- Job scripts: every S2d job script (prep, screen, J1-J5, J2p, J9) `--dry-run` from a COPY in another directory
  (`scratch/s2rev14/jobcopies/`). This used a sandbox `PCREC_TMPDIR` whose `s2d/window.vars` names
  RUN_ID=s2c-dry and FROZEN=HEAD; main's window.vars was not touched. All of them print their declarations.
  The expected groups are J1 9, J2 3, J2p 7, J3 6, J4 5 and J5 3.
- Slot dry runs (J1, J2, J2p, J3, J4, J5) under run id s2c-dry: run as job 480-kit-s2d-prep's WORK from its copy, in the sandbox. `s2d-prep J rc=0` for all six, `PREP EXIT 0`. J4 printed `null-base: 7 bases, each its class arm's text outside the compare, keeping a load the arm makes`. Every job printed one ungated quiet sample with its co-runners. Log: `scratch/s2rev14/prep_work.log`.
- emit_sweep spot: `--ref ce88f1766 --bin build/pcrec --no-corpus --patterns-file` with the first 20 of s2cfix2's pattern list. Every stream gave **movers=0, asymmetric=0**, ending `emit_sweep: DONE rc=0` (`scratch/s2rev14/emit/sweep.log`). This rev touches no `src/`, `cli/`, `lib/` or `memfn/` file, so zero movers is what was expected.

## Gate jobs

- `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/jobs/474-kit-s2c-slotsab`:
  - its rows are now j j2 k l1 l2 l3 g2 g3 f1 f2 f6 n1 n2 s1 s2 q1 b1;
  - `expect rows=17` with the matching regex;
  - its header names S2940-S2945;
  - its `--dry-run` from a copy is green.
- 470-473: no count moves.
  - `tests/mech/rows_for.sh` over the changed files selects no mech row, so 473 keeps 14.
  - 471's sections list is unchanged (12).
- S2d copies in `s2c/jobs/s2d/`: the nine job scripts and `common.sh` are byte-identical to the tree's
  `slot/jobs/` (cmp). None of them changed in rev 1.4, so there was nothing to sync.
  - Their own `window.vars` (main's, FROZEN 508178bd2) now refuses at `--dry-run` with "HEAD is not FROZEN".
    That is the intended stale-window guard: the next window needs main to set a new FROZEN and RUN_ID.
- Nothing queued.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| R14-1 the base is the arm's loop minus the compare, from one source text | yes: link.py (one render, the body swapped), pointer-bump loop, objdump confirmed |
| R14-1 check that they differ only in the compare | yes: `null_check` (text diff outside the body, plus the kept load is the arm's) |
| R14-1 sabotage planting a different base loop | yes: S2940 (plus S2941 for the load) |
| R14-2 measured "consistent with zero within r" (clamped value, noise r or the spread) | yes: est.py, measures.md §3.5¶3a |
| R14-2 no set-format/noise-state/seam change | yes: none |
| R14-2 r's derivation and the branch vs NULL stated | yes: §R1.4, §3.5, §3.5¶3a |
| R14-3 co-runners + load1 in the transcript and the record; draft box-state note | yes: run.py, record.py `quiet`, est.py notes |
| R14-3 no gate or z change | yes: none |
| R14-4 `ungated`; a note line naming the bimodal rows in the record and the draft | yes (the rule also names walk.periodic.one.1024) |
| Replay R14-2/R14-4 and report the floors | yes: four verify floors pass, byte.libc fails |
| span_cards §R1.4 table, `[rev1.4 <id>]` marks; spec hunks by section cite | yes |
| validation list | yes: see Validation |
| jobs 470-474 counts; S2d copies synced and dry-run from copies | yes: 474 moved to 17, others unchanged; S2d copies identical |
| s2cfix2_deliver.txt committed as-is | yes: f4cc04c2a |
| sabotage ids S2940-S2949 | S2940-S2945 used |
| no timing run; nothing queued; artifact_size_log.tsv untouched | yes |

## STATE AT HANDOFF

OWED: none. Tip: the commit that carries this section, on `lane/memfn-s2c`.

Next step (main's and the kit manager's): a fresh S2d window. It times byte.libc again and prices the verify rows
under the new null base. main writes a new `window.vars` (RUN_ID, and FROZEN at this tip or its merge). The
S2d job copies need no edit.

A conflict between the deliver file and the brief: `docs/dev/artifact_size_log.tsv` was already modified in the
worktree when this lane started (a gate side effect). The brief says not to touch it, and the deliver file names
no `dirty-ok`. So `scripts/lanecheck s2rev14` reports "the tree is not clean" for that one path, and nothing
else. This lane did not commit it, revert it, or hide it from git.
