# tt6fix report: the plant pass reads its protocol from stdout; a runner's stderr is shown, never parsed

Lane tt6fix (opus), 2026-11-24. Branch lane/memfn-tt6fix, cut from origin/main @ 01f342d9f (PR #1 as landed).
D203 bug fix, test side only. Nothing under src/, cli/, lib/ or memfn/src was edited.

## Summary

- **The bug.** `scripts/m6read_check_sab_anchors.py`'s runner plant pass treated ANY stderr from a
  runner's `--plant-check` as UNREADABLE. The runners source `tests/lib/timeout_bin.sh`. On a box whose
  bare `timeout` is not GNU (the Linux dev box: uutils), that helper prints its deliberate `[TT-6]` notice
  to stderr. So 3 of the 4 runners read UNREADABLE there, and 22 of the 68 `--selftest` cases failed.
- **The class.** A checker treats a helper's ADVISORY stderr as its parsed protocol. This checker was the
  class's second instance. The first was `[MACPORT]` (cc_resolve.sh) on the Mac. It was patched as an
  instance, with a `CC_RESOLVE_ANNOUNCED="1"` pre-set in the runners' environment ("any OTHER stderr is a
  finding"). The third helper notice, `[ORACLE-LINK]` (resolve_pcre2.sh), would have hit the same patch.
- **The fix.** The `--plant-check` protocol is now STDOUT plus the exit code only: the row grammar, the
  one summary line, and their consistency. Each runner's stderr is SHOWN, in one deduplicated block that
  names the run behind every line, and it is never parsed. A red runner's message quotes its stderr's
  last line as context. The instance patch (the gate pre-set) is removed. No notice is suppressed.
- **Siblings.** I found no other defective site. Every other consumer in the tree reads stdout or the
  exit code, and shows stderr or greps a log for a protocol line. Counts and commands are under
  "Class and siblings".
- **Standing control.** `--selftest` goes from 68 to 74 cases:
  - the two "writes stderr" cases flip to green-and-shown;
  - 6 new cases force the `[TT-6]` and `[MACPORT]` notices on (green, and the notice must be shown);
  - red drills run with the notice on: a runner that dies, a stale FROM, a dump that dies, and a
    runner that dies saying why on stderr.
- **Mutants.** The harness gains E1-E9 on the new clauses. P4/P4b are retired (ignoring stderr is now
  the rule) and P5 is re-spelled onto its new site. All 12 run are killed (P5-P7, E1-E9).
- **Validation on the Mac.** I ran the live pass with and without a forced notice. Both are green:
  81 plants, 39 twins. `--selftest` is green in all four runs (pooled and serial, each forced and
  normal) and the four outputs are byte-identical. The make results are under Validation.

## Reproduction

The notice path keys on `timeout --version` not naming GNU coreutils (`tests/lib/timeout_bin.sh`'s
detection order). I forced that path with a fake non-GNU `timeout` first on PATH, in scratch: it prints
`timeout (uutils coreutils) 0.8.0` for `--version` and execs gtimeout otherwise. A copy is in
`docs/dev/lanes/tt6fix_evidence/fake_nongnu_timeout.sh`. The helper then resolves `gtimeout` and prints
`[TT-6] TIMEOUT_BIN=gtimeout (...)`, which is the Linux box's case one binary over.

At 01f342d9f, with `PATH=<fakebin>:$PATH`, `TIMEOUT_BIN` and `TT6_TIMEOUT_BIN_ANNOUNCED` unset:

- Premise, with no fake: `runner plants checked: 81 (89 edits, 4 runners, each at its pin)`, rc 0.
- Live pass, forced: `runner plants checked: 6 (6 edits, 1 runners)` and `UNREADABLE RUNNERS: 3`.
  Each of the three reads `memfn/tests/run_g2_pres.sh / run_g2_win.sh / tests/memfn/run_wreply.sh
  --plant-check UNREADABLE: [TT-6] TIMEOUT_BIN=gtimeout (default 'timeout' is not GNU coreutils; d`,
  followed by 3 pin lines (`pinned at 34/39/2, NOT READ`). rc 1.
  run_proof.sh sources only cc_resolve.sh, whose notice the old gate pre-set silenced.
- `--selftest`, forced: `plant pass selftest: 68 cases, 11 unit rows, 22 failed`, the brief's count.
  The failures include the clean copy, every STALE/AMBIGUOUS/MISSING FILE case on win, pres and wreply,
  the twin cases, and the TWINS NOT EXPLICIT cases. Each lacks its words because its runner went
  UNREADABLE first.

## Class and siblings

The CLASS: a consumer of a process that sources an advisory-notice helper scores that process's stderr
(or the merged `2>&1` stream) as protocol. The helpers that print such notices number exactly three, each
once per process tree under an exported `*_ANNOUNCED` gate:
`tests/lib/timeout_bin.sh` `[TT-6]`, `tests/lib/cc_resolve.sh` `[MACPORT]` and `tests/lib/resolve_pcre2.sh`
`[ORACLE-LINK]`. I found them with `git grep -n ANNOUNCED`.

**Python consumers.**
- `git grep -nE "(err|stderr)\.strip\(\)( or|\)|:| and)|if (r|p|out|res|proc)?\.?stderr\b|not (r|p|out|res|proc)\.stderr|stderr *(==|!=)|stderr=subprocess\.STDOUT" -- '*.py' ':!docs/dev/lanes' ':!third_party'`
  gives 29 lines in 20 files. Of those files, only m6read runs a shell script. The rest run pcrec, gcc,
  a built oracle or themselves (verify_rxt.py merges its own child's output).
- `git grep -lE "[\[(] *[\"']bash[\"']|[\"'](/bin/)?sh[\"'] *,|\.sh[\"'] *[,\]]" -- '*.py' ':!third_party'`
  gives 26 files that run a shell script. I read every one that runs a helper sourcer:
  - fuzz.py, vm_oracle.py, check_entries.py and capdiff.py run `bash gen_timeout.sh secs|cpusecs|runsecs`.
  - local_adapter.py runs `. resolve_pcre2.sh` and `. cc_resolve.sh`.
  - g2_vspan.py runs `mk_mftrace_lib.sh`.
  - cloud_units_plan.py runs `run_axes.sh`.

  All of them read **stdout** (`int(r.stdout.strip())`, `dict(... stdout ...)`) and show stderr only
  when the run has already failed. That is the fixed shape.
- Within m6read itself there were 3 stderr verdict sites: `read_row`, check and dump. Check and dump
  were fixed. `read_row` is kept: it sources a sabotage ROW (data, which sources no helper) under our
  own `bash -c`, and bash's diagnostic is the only signal of a half-sourced row, because the `-c`
  script still exits 0.

**Shell consumers.**
- `python3 -I docs/dev/lanes/tt6fix_evidence/stderr_consumer_census.py TREE` (output beside it)
  resolves 192 helper sourcers, direct plus transitive through `. X.sh`. It then lists 94 call sites,
  in tests/, scripts/, memfn/ and docs/, that run a sourcer with stderr captured or merged.
- Every site is one of three kinds:
  - a `> log 2>&1` that the consumer then greps for its own protocol line (`score_arm`, `PASS:`, the
    TSV markers in rebaseline.sh, `HARNESS FAILURE:` in run_callouts_tests.sh);
  - a stderr file that is only `cat`-ed on a failure already decided by the exit code (run_axes.sh,
    run_ksweep.sh, gate.sh, nocompile_selftest.sh, reach_only_selftest.sh);
  - a quiet sourcer (scripts/boxqueue, chainrun, cloudrun and queuewatch source `timeout_bin.sh
    2>/dev/null`).
- No site tests stderr for emptiness, compares merged output exactly, or takes its `head -1`. Also
  `git grep -nE '\-s "\$[a-z_]*err'` finds 0 shell checks that score a non-empty stderr file.
- Corroboration, an inference I did not measure: `make test` runs on the Linux dev box with the `[TT-6]`
  notice on in every section, and it is green there, so a stderr-scoring make-test section would
  already be red. The plant pass is not a make-test section run in that environment. [SABANCHOR] runs
  it, and the lanes run it by hand.

**Sibling count: 1 defective consumer (this file, 2 sites: check and dump), plus its earlier instance
patch (the `CC_RESOLVE_ANNOUNCED` pre-set). 0 other defective sites among 20 + 26 Python files and 94
shell capture sites.**

## Fix

I chose **stdout plus exit code as the protocol, stderr shown and never parsed**.

The alternative was a notice-grammar allowlist, in which `[TAG] ...` lines are tolerated and any other
stderr stays red. I rejected it for three reasons:

- **It re-breaks for every new helper.** It is the instance patch in another form: each new notice
  wording needs an entry, and a miss is red on the boxes where the notice fires.
- **The tree already has a rule, and this is the one outlier.** Every other consumer counted above
  reads stdout and shows stderr.
- **What stderr-as-verdict caught is still caught by the protocol.** A runner that dies goes red on its
  exit code. A runner that exits early has no summary line. Garbage on stdout fails the row grammar,
  and a well-formed lie fails the consistency rule. What is given up is stderr from a run whose exit
  code is 0 or 1 and whose protocol is complete and consistent. Such a run answered the plant question.
  Its stderr is printed for the reader, and the runner's own suite owns its health.

Mutant E4, the allowlist design, is killed by the "writes stderr (shown, green)" case. That kill
records the choice.

Changes:

- `scripts/m6read_check_sab_anchors.py`:
  - `run_all` no longer pre-sets `CC_RESOLVE_ANNOUNCED`.
  - Check and dump decide on `rc` and stdout only. The UNREADABLE text names the protocol fault
    (`exit N, K summary line(s), M malformed row(s)`) and appends `; its stderr ends: <last line>`.
  - The new block `runner stderr (shown, not parsed: the verdict reads stdout and the exit code): N
    line(s)` lists each distinct line with the runs that printed it.
  - The pass's header comment gains a `channels` paragraph that says why the gate is never pre-set.
- **Self-test.**
  - `Case.env` holds a case's environment changes, and `notice(c, "tt6"|"cc")` forces a notice on: its
    gate unset, its variable set to an absolute path rather than the default name.
  - Each forced case REQUIRES its notice text in the output. A fixture that stops reaching the notice
    is therefore red, not vacuously green.
  - The two stderr cases are now green-and-shown. Six cases are new: `[TT-6]` forced green, `[MACPORT]`
    forced green, both forced with a runner dying, `[TT-6]` forced with a stale FROM, `[TT-6]` forced
    with a dump dying, and a runner dying with a message on stderr.
- `docs/dev/lanes/plantfix2_evidence/harness.py` (the brief names it): P4/P4b retired with a comment,
  P5 re-spelled, E1-E9 added (87 mutants, every site present exactly once).
- `docs/testing.md` ("The timeout binary itself") states the consumer rule. `tests/lib/timeout_bin.sh`'s
  header points at that rule. The notice itself is unchanged.

## Validation

All runs were on the Mac with `TMPDIR=$PCREC_TMPDIR/scratch/tt6fix`, under `worktrees/.mac-suite.lock`.
"Forced" means `PATH=<fake non-GNU timeout>:$PATH` with `TIMEOUT_BIN`/`TT6_TIMEOUT_BIN_ANNOUNCED` unset.

| run | result |
|---|---|
| `python3 -I scripts/m6read_check_sab_anchors.py`, normal | rc 0: `runner plants checked: 81 (89 edits, 4 runners, each at its pin)`, `runner plant twins checked: 39`, one shown line, `[MACPORT] CC=gcc-16`, from 3 runners x 2 modes |
| the same, forced | rc 0: 81 / 39, two shown lines, `[MACPORT]` and `[TT-6] TIMEOUT_BIN=gtimeout`, the latter from pres, win and wreply x 2 modes |
| `--selftest`, pooled, normal | rc 0: `74 cases, 11 unit rows, 0 failed` (24 s) |
| `--selftest --serial`, normal | rc 0: the same (75 s); its stdout is byte-identical to the pooled run's |
| `--selftest`, pooled, forced | rc 0: the same (26 s) |
| `--selftest --serial`, forced | rc 0: the same (75 s); identical to the pooled forced run's, and to the normal runs' |
| mutant harness, `P5,P6,P7,E1..E9` | CONTROL GREEN; `mutants: 12, killed 12, survived 0`. Rows are in `docs/dev/lanes/tt6fix_evidence/mutants.out` |
| `make CC=gcc-16 strict` | rc 2. This is the PRE-EXISTING Mac failure: the kit's targets-check prints `MISMATCH the host family MF_FAM_AARCH64 compared no target against gcc -march` (plus the features and level-admission lines). There are no compile warnings. |
| `make CC=gcc-16 test-codegen` | rc 2, 19/22 scripts passed. The 3 reds are exactly the PRE-EXISTING Mac-only `run_size_term.sh` (K100), `run_case_spelling_identity.sh` (empty `.text`, Mach-O) and `run_residual_twins.sh`, the same three plantfix2 and s3012fix recorded. `PASS: [SABANCHOR] scripts/m6read_check_sab_anchors.py: all 1412 sabotage rows' anchors resolve and all 81 runner plants apply at their pins` |

On the mutants: only the 12 mutants on clauses this lane touched were re-run. The other 75 have
unchanged sites. Their kills in plantfix2's and s3012fix's runs did not depend on the two cases this
lane changed: only P4/P4b's kills did, per both `.out` files, and P4/P4b are retired. No mutant is
argued equivalent.

## STATE AT HANDOFF

STATE: delivered. Branch lane/memfn-tt6fix, committed. The rulings file
(`docs/dev/lanes/tt6fix_rulings.md`) was empty at every re-read: before each commit, before each run
over 2 minutes, and before this report. No ruling was applied. No queued jobs, and nothing is owed. The
lock `worktrees/.mac-suite.lock` was released after each run. Evidence is in
`docs/dev/lanes/tt6fix_evidence/`: the census script and its output, the fake timeout, and the mutant
rows.
