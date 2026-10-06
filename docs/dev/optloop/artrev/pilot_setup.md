# [ARTREV] pilot setup (lane artprep, 2026-10-06)

What a blind reviewer needs, prepared at the pin. Charter: `charter.md`; harness recipe: `studies/artrev/README.md`;
selection: `selection.tsv` / `selection.md`. Everything below is Mac, scratch tier.

## 1. The pin

- pcrec main **57db5152** (abi 62, START-SET stage 2 landed), `make CC=gcc-16` in worktree `artprep`;
  `build/pcrec` sha256 `67cca146a784b5479b6293eb4859b3d989c0cc251d46b48b9ccdf4ad12741764`.
- gcc-16 (Homebrew GCC 16.2.0) 16.2.0 for every compile (`ARTREV_CC=gcc-16`; the harness refuses clang). The one compile
  line is the harness's: `gcc-16 -O2 -fPIC -I<armdir> -DARTREV_PFX=rx -DARTREV_PFXU=RX -DARTREV_HAVE_IN=1 shim.c <driver>.c`.
- Generated with `ARTREV_CC=gcc-16 python3 studies/artrev/gen_selection.py --pilot --force --pcrec <build/pcrec> --pin 57db5152`,
  then re-generated inside each cell by the cell's own harness copy (`artrev.py gen ... --pattern-file <bench>/patterns/X.rx
  --flags=`, `--features all` is the harness default); each cell's `artifact.c` is byte-identical (`cmp`) to the
  artprep one.
- Main moved to c4420d62 (a journal commit) while this lane ran; `git diff 57db5152 c4420d62` over `studies/artrev`,
  `docs/spec`, `scripts`, `docs/dev/optloop/artrev` is empty, so the cells' copies of those paths ARE the pin's.

## 2. The artifacts and their stamps

| id | name | pattern (bench `.rx`, verbatim) | route at the pin | artifact.c sha256 | lines |
|---|---|---|---|---|---|
| A01 | `loglines_stack_frame` | `\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+\|Native Method\|Unknown Source)\)` | `RX_ENGINE dfa`, `RX_DFA_SCAN unanchored`, `RX_VM_START_SCAN none`, ncaps 1 | `1588f520bc47...a677a24` | 920 |
| A07 | `capability_doubled_word` | `\b(\w+)\b\s+\1\b` | `RX_ENGINE vm`, `RX_VM_PREFILTER none`, `RX_VM_START_SCAN first-class`, ncaps 2 | `42a70983f18b...fe9fec1` | 461 |
| A09 | `loglines_level_context` | `\b(?:ERROR\|FATAL\|CRIT)\b.{0,200}?\b(?:timeout\|timed out\|refused\|denied\|unreachable)\b` | `RX_ENGINE vm` (`collapsed-prefilter`, dfa overflowed >32000 states), `RX_VM_PREFILTER hybrid`, `RX_VM_START_SCAN none`, ncaps 1 | `bc5bb11bdb83...ad7d8a` | 1186 |

(`|` in the pattern column is escaped for the table only.)

**Moved versus the ca7bdb11 (abi 61) dry run** (`diff` of the dry-run `artifact.c` in the artharness scratch against the pin's):
- A01: no real move. 5 changed lines, all abi-62 bookkeeping (header comment `abi 61 -> 62`, `.abi = 62`, one new stamp line
  `RX_VM_START_SCAN "none"`). The DFA hat of START-SET is stage 3, not built.
- A09: no real move. The same 5 bookkeeping lines.
- A07: MOVED, and visibly the stage-2 VM hat: +23 lines net, a 256-entry `rx_start_set[]` table (digits, letters, `_`) and a
  skip loop `while (attempt_position < subject_length && !rx_start_set[subject[attempt_position]]) attempt_position++;`
  with its `>= subject_length` early return, at the search entry and again at the retry. A07's reviewers therefore meet a
  hat the generalizer will classify as known (START-SET stage 2).
Recorded in `selection.tsv` (`pinned_at`, `pin_stamps_abi62`) and `selection.md`.

## 3. Subjects, provenance, hashes

Read-only use of `/Users/fdicostanzo/pcrec-bench` (checkout head eb634d9d; `git status` clean before and after; scripts run with
`python3 -B`, output to scratch). Subjects live in `build-artrev/subjects/` of the artprep worktree (scratch) and are copied into
each cell. **The pilot cells are the `large-subject-throughput` regime; the short-call (`search_short`) regime is not part of the
pilot.** A correction to the draft selection: the loglines cell is TWELVE subjects (the bench report's `n` is 12 for stack-frame),
not `t-64k/t-256k/t-1m`.

- **capability (A07), three subjects**, copied unmodified from `bench/capability/throughput/`: sha256 equal to the bench's
  `manifest_throughput.tsv`: `t-64k.bin` 65536 B `d2e4f134...c8524`, `t-256k.bin` 262144 B `3cf7b248...b49b5a7`,
  `t-1m.bin` 1048576 B `ccbdf7eb...f9754ee`. (The committed `.bin` files exist in the Mac checkout.)
- **loglines (A01, A09), twelve throughput subjects + 112 search-band subjects**: the `.bin` files are NOT committed in the
  checkout, so they were REGENERATED EXACTLY with the bench's own generators at their committed default seeds
  (`bench/loglines/gen_throughput_subjects.py --out <scratch>` seed 20260829; `gen_subjects.py --out <scratch>` seed 20260828).
  Verification: the regenerated `manifest_throughput.tsv` and `manifest.tsv` are BYTE-IDENTICAL (`diff`) to the bench's committed
  ones, and all 124 files re-hashed from disk equal the manifest sha256 and length (0 bad). Nothing is a variant; no subject
  was unreproducible. Manifest files: `manifest_throughput.tsv` sha256 `b9449178...f4717`, `manifest.tsv` `a87a2744...38fc`
  (the in-scratch copies; identical to the bench's).

  | subject | bytes | sha256 |
  |---|---|---|
  | t-016k-fail | 16403 | 31c1616f2ad7bab3f632d18f4d4e6d411ac75186490f871cc5f5e73c19eb1d47 |
  | t-016k-syslog | 16434 | 006287dd17a4b00ed4edaf93a917bde036b1e830bc87c500c7cbe1603bb51030 |
  | t-016k-hit | 16398 | 26c60143735cec3b64b78784fae973fd7df2b137f0d476a9c24554337e0bfe8c |
  | t-064k-fail | 65593 | 245361c15fa6928f84cc9a05d68b14777c9fb1052ffe0cb67f28942d7ed67790 |
  | t-064k-syslog | 65605 | 8589bfc41d946e45091ac8351392fcb01fe1c696c9dc58c53dbb6c1147ef7424 |
  | t-064k-hit | 65551 | 744850ae823574e12565c40c7a03ff5ee4c94913ef19861ea16c27feac017831 |
  | t-256k-fail | 262169 | 4dfd5a731015ff46c5ff7a0a894d86fa2a976020ff28fec7d3618a9e3e8e85cf |
  | t-256k-syslog | 262173 | 770500847cbccc0deba098e8eef37bfe1d207f3da42805a6e67180a4a6443ed3 |
  | t-256k-hit | 262234 | 55d6fa934099d1a2826ffdc6b2f5e7e7ddcca330e9b08d34e8dded3897eb509a |
  | t-1024k-fail | 1048621 | 6c56d92fadb214df52c09aaa9fae33484b16e57d1b7930c88df8dda63c3ba104 |
  | t-1024k-syslog | 1048651 | 5530c7a17b17b60a8c40c4cbae98e88fa5a931ef9403e2fab2b67fa67d43ef07 |
  | t-1024k-hit | 1048621 | 72c6adf280bf63006e4773eb4b429307ba4e7c8bcfbdf7e0fb2d95fb31972417 |

  The 112 search-band hashes are in the bench's `bench/loglines/manifest.tsv`.
- Dense/sparse variants (charter S4) are the confirmer's to construct; none were made here.

**Null-twin identity with the real subjects** (artprep scratch, `identity <name> null --subject <all subjects> --corpus --battery 3000
--block 16 --san`, ASan+UBSan, libpcre2 10.48 Homebrew sample):

| artifact | subjects | cases / transcript lines | search cases matching in the original | libpcre2 sample | result |
|---|---|---|---|---|---|
| A07 | 3 | 14,915 / 79,700 | 1,372 of 14,912 | 1500 checked, 0 disagreements | PASS |
| A01 | 124 (12 throughput + 112 search) | 15,246 / 77,571 | 1,352 of 15,122 | 1500, 0 | PASS |
| A09 | 124 | 15,254 / 76,303 | 1,411 of 15,130 | 1500, 0 | PASS |

`--corpus` finds 0 corpus cases for all three patterns (also in the full tree), so identity rests on the supplied subjects, the
generated battery and the libpcre2 sample; the corpus arm of the charter is empty for the pilot, not skipped. The oracle is 10.48
Homebrew, not the 10.46 reference (noted by the harness).

## 4. The cells

Four cells, created with `scripts/mk_d27_cell.sh` RUN FROM THE MAIN TREE (not from a worktree), one per reviewer:

| cell (work here) | delivery worktree / branch (author never touches) | artifact |
|---|---|---|
| `/Users/fdicostanzo/pcrec/worktrees/rvA01-cell` | `worktrees/rvA01` / `rvA01` | A01 `loglines_stack_frame` |
| `/Users/fdicostanzo/pcrec/worktrees/rvA07a-cell` | `worktrees/rvA07a` / `rvA07a` | A07 `capability_doubled_word` |
| `/Users/fdicostanzo/pcrec/worktrees/rvA07b-cell` | `worktrees/rvA07b` / `rvA07b` | A07 `capability_doubled_word` (separate identical copy) |
| `/Users/fdicostanzo/pcrec/worktrees/rvA09-cell` | `worktrees/rvA09` / `rvA09` | A09 `loglines_level_context` |

Created from main HEAD c4420d62 (see section 1). **Allowlist passed to the script**: `docs/spec`, `studies/artrev`,
`docs/dev/optloop/artrev/notebook`, `docs/dev/optloop/artrev/charter.md`, plus `scripts/watchdog` (one addition to the brief, see below).
Then, per cell, by hand: that reviewer's artifact directory (generated by the cell's own harness into `build-artrev/<name>/`:
`artifact.c/.h/.s`, `GENERATION.txt`, `meta.json`, `arms/orig`, `arms/orig2`, a ledger holding only the `gen` row), the subjects
(`build-artrev/subjects/`, section 3), and `docs/dev/optloop/artrev/<ID>/` with `CELL.md` (the reviewer's own copy of the
commands below, paths relative to the cell) and a `leads.tsv` holding only the charter header (plus the `origin` column).
The notebook is the repo's `notebook/README.md` alone, so the two A07 reviewers start from the same (empty) notebook; the A07
cells are identical except for absolute paths in `GENERATION.txt`/`meta.json` and one timestamp (checked by `diff -r`).

Deviations from the script's output and why (each one found by testing, not by reading):
1. **`build/` was deleted from every cell.** The script copies the whole `build/` (a `pcrec` binary, `libpcrec.a`, objects). A
   reviewer has no use for it (artifacts are pre-generated) and a compiler binary carries the emitter's text templates, which is
   exactly the knowledge the charter blinds the reviewer to.
2. **`git init` was run in every cell.** `mk_d27_cell.sh`'s comment says the cell has "no .git to query"; that is false for a cell
   under `worktrees/`, which sits inside the main working tree: `git -C <cell> show HEAD:src/gen/emit_vm.c` printed the emitter
   source. An empty repo in the cell is a git boundary (`git show HEAD:...` now fails with "invalid object name 'HEAD'"). This is
   a defect of the script for ANY blinded cell, not just ARTREV; flagged for the manager. A reviewer could still `cd ..`, so the
   brief must keep the instruction "work only in the cell; do not open any path that appears outside it" (note `GENERATION.txt`
   records the generating binary's path, which is outside the cell).
3. **`scripts/watchdog` is in the allowlist.** `time` runs under `scripts/watchdog` (tree_root()/scripts/watchdog); without it no
   timing run can start. It is a generic supervisor with no pcrec knowledge.
4. **A symlink `worktrees/.mac-suite.lock` in each cell** pointing at the real `/Users/fdicostanzo/pcrec/worktrees/.mac-suite.lock`.
   Because of (2) the harness's `repo_root()` is now the cell, so its suite-lock check would otherwise look under the cell and never
   fire. Tested in a COPY of a cell: with the link retargeted at an existing file `time` refused (rc 5, "a Mac suite is running");
   with the lock absent and load1 at 29-34 it refused on the load gate (rc 7) and logged nothing; with the selftest override
   (`ARTREV_SELFTEST=1 ... --gate-override`) a 5-round run of `orig,orig2,null` completed in the cell (null deviation 0.04 ns/B).
   No real lock was touched.

Checks run on the delivered cells: `find`/`ls -R` finds no path named `src`, `design`, `tests`, `cli`, `lib`, `plan*.md`,
`decisions*` or `known_issues*` in any cell (only `docs/spec`, `studies/artrev`, `scripts/watchdog`, the artifact directory,
the subjects, the notebook README and the charter). `CLAUDE.md` files present: `studies/artrev/CLAUDE.md`, `docs/spec/CLAUDE.md`
only. Prose in 14 allowlisted files (`docs/spec/*`, `studies/artrev/*`) still names `src/...` or `docs/design/...` paths as text
(for example `docs/spec/cli.md` line 102); that is names, not contents. `studies/artrev/selftest.sh` needs a `pcrec` binary and so
CANNOT run in a cell (decision 1); the substitute is the smoke above (twin null, identity with real subjects, time) run in a copy
of each of A01, A07a and A09 cells: all three twin/identity PASS (800-battery, libpcre2 sample clean); time as above for A07a.
A07b is a byte-for-byte copy of A07a's procedure.

## 5. Commands a reviewer runs (from the cell root)

    export ARTREV_CC=gcc-16                 # bare `gcc` on this Mac is clang and is refused
    A="python3 -B studies/artrev/artrev.py"
    N=<artifact name: loglines_stack_frame | capability_doubled_word | loglines_level_context>

    # gen is already done (pin in GENERATION.txt).  Read: build-artrev/$N/{artifact.c,artifact.s,GENERATION.txt}
    $A twin $N null --null                              # twin: the noise control, always first
    $A twin $N L1 --new                                 # a copy of the original at arms/L1/artifact.c; edit it
    $A twin $N L1 --seal                                # diff -> twins/L1.rN.patch (rejects SIMD/flags/artifact.h edits, exit 4)
    $A identity $N L1 --subject <file> [--subject <file> ...] --corpus --battery 3000 --block 16 [--san]
    $A time $N --arms orig,null,L1 --subject cell=<file> [--subject dense=<file> ...] --rounds 11
    $A ledger $N                                        # leads/revisions/timing runs used against the bounds

Subject arguments: A07: `build-artrev/subjects/capability/t-64k.bin`, `t-256k.bin`, `t-1m.bin` (the whole cell). A01/A09:
`build-artrev/subjects/loglines/throughput/t-<016k|064k|256k|1024k>-<fail|syslog|hit>.bin` (the cell is all twelve; a
representative handful is enough for scratch iteration) and `loglines/search/s-NNN.bin` for short-call sanity. Each cell's
`docs/dev/optloop/artrev/<ID>/CELL.md` carries these lines already expanded.

Bounds, enforced by `iterations.tsv` (exit 3 = refused): 6 leads per artifact, 4 revisions per lead, 3 timing runs per revision,
6 hours per reviewer. `time` refuses (exit 5) while the suite lock exists or another run holds the cell's timing lock, exit 7 and
nothing logged when load1 stays over the gate (2.0 on the Mac).

## 6. The timing caveat

- Mac = SCRATCH. Numbers steer iteration and are never reported (charter 3.1); reportable timing is the confirmer's, on ubuntubudu,
  by day (08:00-19:00 local, outside a bench window).
- The Mac suite lock refuses timing while held (`worktrees/.mac-suite.lock`; there was none at the time of writing). ssbuild3 will
  hold it for a full `make test` later tonight, so reviewers can iterate (twin, identity) all night but cannot time until it clears.
- The Mac was at load1 28-34 (another lane) throughout this lane's work; the harness's default load gate (2.0) refuses real timing
  at that load. Nothing here measured a noise floor.
- Open harness gap, found here, not fixed (this lane is docs and selection only): the "two reviewers never time at once" lock is
  `<ARTREV_ROOT>/.timing.lock`, i.e. per cell, so cells do not see each other. The manager should sequence timing between the four
  cells (or a harness change should move that lock to the main checkout; the symlink trick used for the suite lock does not work,
  because the lock is taken with `mkdir`). The two A07 cells are the case to watch: concurrent timing runs would perturb each
  other's numbers.

## 7. Cleanup when a reviewer finishes

For each cell the script printed the exact `rsync` lines; the useful ones are `docs/dev/optloop/artrev/<ID>/` (review.md,
leads.tsv, twin patches) and `docs/dev/optloop/artrev/notebook/` (the reviewer's entry), which live under the cell and are not
in the script's allowlist printout, so copy them explicitly. Then `git -C /Users/fdicostanzo/pcrec worktree remove worktrees/rvXXX`,
`git branch -d rvXXX`, `rm -rf worktrees/rvXXX-cell`. (Artifacts, cells and subjects are gitignored scratch; nothing in this lane's
commit depends on them.)
