# COMMON brief: critic round r76 memfn-bsu3 (CODE mode)

Read this whole file first. Your own lens brief (`brief_<lens>.md`) holds
your ONE question.

## Scope mandate (binding)

- You may touch ONLY the pcrec repo (/home/pcrec/projects/pcrec), the
  pcrec-bench repo (/home/pcrec/projects/pcrec-bench), and the temp root
  `$PCREC_TMPDIR` = /var/tmp/pcrec-pcrec. Do not create, modify, or delete
  any other file on this machine.
- READ-ONLY on both repos. Never edit them, never commit, never run `make`
  or a suite (`make test*`, `tests/mech/run_sabotage_matrix.sh`, a battery).
  You MAY run single-pattern compiles (`build/pcrec`, the kit below), `gcc`,
  `clang`, `objdump`, `nm`, and the check SCRIPTS named in your brief
  directly, on single artifacts, inside your compile cap.
- Your scratch goes ONLY under
  `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/<lens>/` (create it).
  `/tmp` is not used: run `export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/<lens>/tmp`
  (mkdir it) before anything else, in every shell command (each Bash call
  is a fresh shell).
- Never `cd` in a compound command; use absolute paths and `git -C`.
  Run Python as `python3 -I -B`. Wrap any command that could hang in
  `timeout 300`.
- Never kill anything with pkill/pgrep. If you must stop a process you
  started, use `/home/pcrec/projects/pcrec/scripts/safekill PID`.
- No `gh`, no network.
- Load: the box is shared and may be running other suites. Use `nice` on
  every gcc loop and run at most 2 compiles at once. Hold your compile cap
  (in your brief). ALL probing must END by 00:30 tonight (2026-11-22):
  the box has a timing window 01:00-07:00. If you are not done by 00:30,
  stop probing and write up what you have.

## Subject (frozen)

- SUBJECT = branch `lane/bsu3` at `ec578d053599b58e6d96997245cf356746f21086`.
- BASE = `2cdff179475c0e962018de4610ea637db1f6d729` (the parent of the
  lane's first commit `be192b04a`; it is also `git merge-base main
  lane/bsu3` today).
- The subject commits (subjects only): be192b04a "R-47 U3: the vector
  span's w32 level block (abi 111 -> 112)"; 33953d7c2 "R-47 U3 pins: S3515
  (C18 -O0 rule control (1)), S730 V witness, C4 rows, recursion-identity
  self-pin"; 3f5d93969 "recursion-identity FILEPIN comment worded
  arch-free"; then two report-only commits (denied).
- Review tree (built, read-only): `/home/pcrec/projects/pcrec/worktrees/crit-memfn-bsu3`
  (= SUBJECT, `build/pcrec` and `build/pcrec-harness` built).
- BASE tree (built, read-only): `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/base`
  (a `git archive` of BASE, built clean).
- The diff to review:
  `git -C /home/pcrec/projects/pcrec diff 2cdff179475c ec578d053 -- . <EXCLUDES>`
  (EXCLUDES below). Files: memfn/src/window.c (the code), src/gen/emit_dfa.c
  (abi 112), docs/spec/{limits,match_api,registry,tuning}.md,
  docs/dev/history/abi_changelog.md, tests/memfn/{simd_bounds.tsv,
  simd_floor_check.py, simd_guarded_check.py, span_vector_identity.py,
  c4_allowlist.tsv}, tests/mech/sabotages/{S3515 (new), S693, S730},
  tests/codegen/{run_codegen_tests.sh, run_recursion_identity.sh}.

## Design of record and what is IN scope

`docs/design/memfn/block_span.md` rev 4.2 as at SUBJECT (read it with
`git -C /home/pcrec/projects/pcrec show ec578d053:docs/design/memfn/block_span.md`).
The subject is **§14 unit U3 only**, quoted from §14:

> **U3** | The `w32` level block: §4.1's text bracketed by V's own writer
> (lane order, the K ≥ 16 assert), the selector's replaced call, the include
> bit on the art, the form token, the guarded bound and `simd_bounds.tsv`, the
> `limits.md`/`tuning.md`/`registry.md` hunks. [rev4.1, R71-4] **C18's head
> family (`SELECTOR`, `HELPER`), the `_b` name form and the -O0 rule with
> control (1)** (§10.2), so `test-memfn-simdfloor` reads U3's text green.
> [rev4.1, R71-5] A V witness (`[0-9a-f]{17}`) added to
> `simd_guarded_check.py`'s NAMED, `simd-form-named` re-pinned 8 → 9, so the
> new `simd_bounds.tsv` row has a reader that is not the every-10th sample.
> F2 recorded before anything else | yes (SIMD-on)

plus the previous round's items it names (see "Earlier-round items" below).
Sections you will need: §4.1 (the text), §4.2 (over-read and boundary),
§4.3 (answer identity), §4.4 (the cascade), §5 (seam shape, guarded bound),
§6 (F2), §10.2 "The C18 amendment", §11 (expected movers), §12 (constants).

**NOT in the subject (do not report their absence):** everything §14 assigns
to U4 and later: G2-V (unit/whole sections), the 20 T-table pin cells,
SPAN-SEED's per-check wiring and floors, sabotage rows (a)-(f), C18's NAMED
three span witnesses, its floors and controls (2)-(4), the routing leg
(`routing_shape.py`), `DIFFER_PINS` floors, C18 `FLOORS` re-pin, the C6
card, the abi package at the landing base. F2 is a delivery step recorded in
the lane's report (denied to you): you may re-run it, but "F2 is not a
committed test" is not a finding.

**Not a finding:** the abi is 111 -> 112 on the kit branch while main has
re-pinned the previous unit to 110; whichever unit lands later re-pins by
grep.

## Rulings in force (read from main at the freeze, `git -C /home/pcrec/projects/pcrec show fb258a000:docs/dev/decisions.md`)

- D201 (block-build) and its addenda 1-5: decisions.md lines 10299-10313 at
  fb258a000. Verbatim owner words: D201 "build with simd layer"; add. 2
  "the function goes inline so it's just code organization? If that's true
  I don't have a problem with that." (read as option A); add. 4
  "scalar-check-cut: yes"; add. 5 "wrap-clang: a. Policy is inline wrappers
  where possible so this is a move towards that. The wrapper is a separate
  fix to an out of policy coding not related to the simd change / That
  said, do track the clang issue with an item for follow-up to make sure no
  surprises".
- D157 (line 9389): pcrec -> kit carries FACTS only, never presumes the
  kit's method.
- D76 (line 5600) / D94 (line 6572, and its addenda at 6686 and 7747): a
  scaffolding change is an abi bump; every reader of the number is found by
  GREP; then run the suites that count.
- D144 (line 8968) and add. 4 (8981): SIMD verdicts come from pcrec-bench on
  the targeted hardware; D155 item 2 (quoted in block_span.md's FREEZE
  NOTE): V lands CANDIDATE behind the OFF switch.
- Read every ruling file (decisions.md, plan.md) ONLY via `git show
  fb258a000:path`, never the live tree.
- ONE lens (the CONTRACT lens) checks quoted owner words against the record;
  the others cite them without re-checking.

## Earlier-round items in scope

(Filled from the launcher's reply; see "R75 ITEMS" at the end of this file.
If that section says PENDING when you read it, review U3 against §14 alone.)

## The box and the consumer flags

The box is AMD Zen 4 (AVX2 + AVX-512), gcc 15.2.0 (`gcc`), clang (`clang`).
Any claim about "identical machine code" or speed SHAPE carries
consumer-flag columns: gcc -O2, gcc -O3, gcc -Os, clang -O2, and gcc -O2
-march=native. Note the artifact supplies its own ISA region (`#pragma GCC
target(...)` / `#pragma clang attribute push`) at `-fmemfn-simd=x86-64-v3`,
so it compiles without `-mavx2`.

## The run kit (use it; do not build your own tools for these jobs)

`K=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/kit`

- `$K/emit.sh TREE OUT.c [pcrec args...]`: writes the artifact (prefix
  `rx`) with TREE's compiler. TREE = `base` | `subject` | `plant:S3515` |
  `plant:S730` (planted compilers, see below). Pass the pattern as
  `--pattern '...'` in SINGLE quotes or via a file; check the
  `/* ... Pattern: ... */` first line of every emitted file you cite before
  reporting a byte-identity or route claim (shell quoting has eaten `\b`
  before).
- `$K/check.sh TREE 'PATTERN' SUBJ.hex WORKDIR [pcrec args...]`: emits,
  builds the GUARD-PAGE runner (`$K/gp.c`) with `gcc ${GPCFLAGS:--O2
  -march=native}`, runs every subject in two layouts (R: the subject ends
  flush against a PROT_NONE page; L: it starts flush after one), diffs
  first-match answers against libpcre2-8 (`$K/oracle.py`; set
  `ORACLE_OPTS=--utf` for a utf8 artifact). Prints `N subjects, D differ, F
  fault`; files in WORKDIR (art.c, got.txt, want.txt, diff.txt). SUBJ.hex is
  one subject per line in hex. A smoke run: `[0-9a-f]{17}` at
  `--features all -fmemfn-simd=x86-64-v3`, 202 subjects, 0 differ on both
  trees.
- Compare BASE/SUBJECT emitted C under the SAME basename in two dirs (the C
  names its file in places). A BASE/SUBJECT compare pair counts as 2
  compiles in your cap.
- Useful flags (check `build/pcrec --help`): `--features all`,
  `-fmemfn-simd=x86-64-v3` (the 32-byte level), `-fmemfn-simd=x86-64` (SSE2
  baseline, admits no w32), `-fno-memfn-simd` (default), `-e utf8`,
  `--window-search-width=4095` (the wide cover width), `--memfn=no-span-vector`
  (the deny), `--engine=vm`.
- Planted compilers (prebuilt, `$K/../plants/<ROW>/tree/build/pcrec`): S3515
  and S730 as the subject's rows declare them (applied with exact
  SAB_COUNT). ONE lens (CHECKS) owns all plants; the others do not plant.
- The 710 timed sources (read-only copy): `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/R/710/`
  (`work/src/<class><k>.avx2-loop.c`, `confirm.py` with `CLASSES`,
  `SITE_EXPECT`, `KS_OLD`, `KS_NEW`; `spike708.py`). Its compile is
  `gcc -std=gnu11 -O2 -w` (confirm.py line 409).

## DENYLIST (D27 applied to review): never open, and EXCLUDE from every git diff and grep

- `docs/dev/lanes/bsu*` and `docs/dev/lanes/bspan*` (the lanes' reports,
  briefs and rulings files);
- every file or directory under `docs/dev/reviews/` whose name contains
  `bspan`, `bsu1`, `bsu2` or `bsu3`;
- `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md`,
  `memfn/docs/ideas.md`;
- `worktrees/.mgr/`, every other worktree under `worktrees/` except
  `worktrees/crit-memfn-bsu3`, the box queue and its logs, job logs;
- `$PCREC_TMPDIR/scratch/` dirs `bsu1*`, `bsu2*`, `bsu3`,
  `crit-memfn-bsu2`, `memfn`, and every other `crit-*` round dir;
- this round's `.coord/` directory and other critics' lens directories;
- `git log` bodies beyond subject lines (use `--format=%h %s`).

EXCLUDES for git (append to every `git diff` / `git grep` / `git log --
path`): `':!*bspan*' ':!*bsu*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!memfn/docs/ideas.md'`

EXCLUDES for plain grep -r: `--exclude='*bspan*' --exclude='*bsu*' --exclude-dir='*bspan*' --exclude-dir='*bsu*' --exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=ideas.md --exclude-dir=.mgr --exclude-dir=build`
(note: run plain grep on a path INSIDE the review tree, e.g.
`.../worktrees/crit-memfn-bsu3/memfn`, so the root's own name does not
matter).

## Output format

- Your findings file `<lens>.md` in the round dir has been PRE-CREATED with
  its headings. APPEND to it (Edit, or a shell `cat >> FILE <<'EOF'`); never
  overwrite it with Write (the harness refuses a subagent's whole-file
  Write and the file stays empty).
- Append each finding THE MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact
  command, observed vs expected) or SUSPECTED (what would confirm it);
  severity (answer / speed / size / maintenance / doc / design); effort;
  blast radius; file:line or §. A finding against a ruled D-row cites it
  and argues, or drops.
- State the MINIMUM and MAXIMUM witness size your probe pool reached (k,
  subject length): a 0-difference result below the witness's length is not
  evidence.
- End with `## PROBED-AND-HELD` (with case counts) and, as the very last
  line, `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/<lens>_deliver.txt <lens>`
  and fix what it says until it prints DONE. Then END.
- Your final reply: at most 150 words. A failed final reply is EXPECTED for
  a nested agent and needs no escalation: the CRITIC COMPLETE line in your
  file is the delivery. If your findings-file append is REFUSED, SendMessage
  the findings to `crit-memfn-bsu3` at once, marked relayed.
- The two standing questions (sibling of a family; general form + unlocks,
  with triggers) belong to the SLOT lens only.

## R75 ITEMS

PENDING (the launcher has not supplied the texts at launch time). Review U3 against block_span.md §14
alone. If the texts arrive, a separate fresh critic covers them; you need not look for them.
