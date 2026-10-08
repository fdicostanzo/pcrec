# posstri: triage of lane/possbuild's four red `make test` sections

Lane `posstri`, sonnet, 2026-10-07, branch `lane/posstri` from `070f29e4`
(lane/possbuild's tip, [ART-POSS-ARMS] build, abi 65 -> 66, merged with main
8cada7b9). Input: possbuild's `build/slot/maketest.log` (rc=2, four reds:
test-cpset-structure, test-rxtsource, test-codegen, test-startset). Every
section's red is a CHECK-side item; no `src/` change, no real regression found.
worktrees/possbuild was not touched. Scratch (a `git archive` of main 8cada7b9
built to compare against) lived in this worktree's gitignored `build/` and is
deleted.

## Verdicts

| section | verdict | fix commit |
|---|---|---|
| test-cpset-structure | 2 fails, both check-side: [2b] allowlist, [3] manifest | fdaba81b |
| test-rxtsource | census/C3 pins stale for 71 new blocks | a611b9fc |
| test-codegen | one fail, `run_size_term.sh` §9 pool lost a side | 6a0084a9 |
| test-startset | `[vm-movers]` manifests missing the new blocks' rows | dff05ab7 |

### test-cpset-structure (the unexpected one; fdaba81b)

Two independent fails in the log.

**[2b]** "a file outside the allowlist reads the A_CLASS payload directly":
`src/opt/possessify.c:1416-1417`, the new `cls_polarity`, reads
`x->u.cls.iv[i].lo/.hi`. Diagnosis: the check's intent (r54 E1) is that nothing
renders a class to a bitmap by reading the payload; the allowlist already
carries the same kind of reader (`opt/altcls.c`, `parse/ctxnode.c`: interval
algebra over code points, never a bitmap). `cls_polarity` is a sorted
interval-vs-interval sweep of a class against the gate's code-point set C,
above the lowering (possessify runs before `pcrec_lower_enc`; its `A_WCLASS`
arms are loud, `gk_build` at `possessify.c:898`). It makes no bitmap, and
rendering via `pcrec_cls_bits_widen` would answer wrongly for a class reaching
past the byte range. Fix: `src/opt/possessify.c` added to `ALLOW`, with a
header paragraph in the file's own style naming the reader and why. The allowlist
is whole-file, so this also stops policing the rest of `possessify.c`; the
other `possessify.c` class reads already go through `pcrec_cls_bits_widen`
(`:486`, `:908`).

**[3]** the recorded stamp manifest drifted. Six values over five rows,
evidence by diffing `-o -` artifacts of a scratch build of main 8cada7b9
against this tree:
- `a(b|c)+d`, `(a)(b)(c)`, `(?<=foo)bar`, `(a(?1)?b)`: EMITTED_BYTES +29
  exactly. The delta is the abi digits (same width) and one new line,
  `#define RX_VM_POSS_ARMS 0x0u` (29 bytes). The DFA sample rows carry no VM
  stamp block and do not move.
- `(\w+)\s+\1`: a real mover, the manifest's only reference-bearing pattern.
  Stamp `RX_VM_POSS_ARMS 0x4u` (arm B). `\w+` (followed by the disjoint `\s+`)
  now possessifies: `RX_RESUME_FRAMES` 2 -> 1, `RX_TRAIL_FRAMES` 5 -> 4,
  `RX_NSLOTS` 6 -> 5, the program turns FRAMELESS (`RX_VM_FRAMELESS` 0 -> 1,
  entry shape `plain` -> `inline`), `RX_VM_STRATS` 0x3u -> 0x1u, EMITTED_BYTES
  29085 -> 28640 (-445 at `-o -`; the manifest's `printf '%s'` form reads one
  less). Answer evidence: `tests/possessify/run_possdiff.sh` on this pattern
  alone (it is in `arms_core.txt`; header `# features: all`) reads 1 agreed / 0
  diverged / 311 pattern-subject-startpos cells with a possessified quantifier.
Fix: the 7 manifest cells re-recorded to the values this check's own sample
loop printed (the log's `>` lines), and a dated RE-RECORDED paragraph added in
the file's established style. Re-ran standalone: `bash
tests/codegen/run_cpset_structure.sh`, 28 passed / 0 failed.

### test-rxtsource (a611b9fc)

Log: `found 275/5392/51505, pinned 275/5321/50915`, plus the C3 pcre2-only /
SKIP pins. Cause: possbuild's added `.rxt` cells. Counted per file with the
check's own awk at 8cada7b9 versus the tip (not by recomputing the corpus):
`tests/possessify/possessify.rxt` 76/2514 -> 145/3082 (+69 blocks, +568 lines),
`tests/recursion/k93.rxt` 23/133 -> 25/155 (+2/+22). Total +71 blocks / +590
lines / +0 files, which is the found - pinned difference to the digit, and
equals the C3 `pcre2-only` and `SKIP` movement (+590): all the new blocks are
`# pcre2-only` (libpcre2 10.46 verified), so `C3_PASS` and the other skip
buckets do not move. Re-pinned: `CENSUS_BLOCKS` 5392, `CENSUS_LINES` 51505,
`RUNSH_BLOCKS`/`RUNSH_LINES` the same delta (nothing under known_fail),
`C3_SKIP` 34184, `C3_SKIP_PCRE2ONLY` 17108. Re-ran standalone, file
`tests/rxtsource/run_rxtsource_tests.sh`: 279 passed / 0 recorded / 0 failed
(python 3.14, the pinned reference).

### test-codegen (6a0084a9)

14 of 15 scripts green; the sole red was `tests/codegen/run_size_term.sh` §9:
"the band-eligible pool has 1 distinct shape(s) below 0.75 and 7 above (want at
least 2 each)". Diagnosis by running the script's own measurement (threshold-1000
reference compiler, `--engine=vm`, K=1..8, `--warn-emit-bytes`) on abi 65 (main
8cada7b9) and abi 66, all eleven members: every ratio rises by 0.0001-0.0003,
and `(?:ab|ba|aa|bb){24}c` goes 0.7498 -> 0.7500, i.e. it crosses the bar and
now stamps `size-model-declined` (prediction and stamp still agree). Every
member stamps `RX_VM_POSS_ARMS 0x0u` at the default, so the cause is the +29-byte
K-INVARIANT stamp line alone, not the arms. That is the same event this
file's header already records twice (abi 54, abi 62): the pool's in-band
below-bar side shrinks and a member must be added. Added `((a)|ab){0,17}c`
(`tests/counterk/counterk.rxt:475`, a corpus pattern) as shape
`capture-alt-bounded`: ratio 0.7199 (0.7196 at abi 65), `size-model` taken,
in band. It has the same body as the `capture-alt` member but a bounded count,
so it sits below the bar where its sibling sits above. Judgement call: the
shape tag is a label the file's author assigns; I judged a bounded count over a
captured alternation a distinct emitter axis from `prefix-chain`, and said so
in the file. The constant (0.75) is not touched, per the file's own instruction.
Note `(?:ab|ba|aa|bb){24}c` now sits at 0.75004, declined, a knife-edge member
that agrees with its stamp; flagging it, not changing it. Re-ran standalone, file
`tests/codegen/run_size_term.sh`: 32 passed / 0 failed ("12-member pool ... 2
below / 7 above").

### test-startset (dff05ab7)

`[vm-movers]` red on both arms: "70 not in the manifest, 0 manifest rows not
movers" (auto) and 71 (forced). The 19 other checks in the section passed
(including `[vm-iff]`, `[vm-route]`, `[vm-deny]`, `[vm-table]`, the every-startpos
differential, 4,355,646 cells). Cause: the same added blocks. Evidence: ran the
manifests' own generator, `docs/design/startset/s1/census_s1.py`, on this tree
(its `-fno-start-set` arm, so any build works). It reproduces the check's
counts exactly (V at auto 362 movers, forced 3144, DFA 82). Diffed against the
committed manifests, corpus rows only: auto +70 (69 `possessify.rxt` lines
3032-4007, 1 `k93.rxt:279`), forced +71 (69 + `k93.rxt:260,279`), s3_dfa +0; 0
rows gone and 0 hex changes, so no existing row moved. Fix: the new rows appended
to `manifest_s2_vm_auto.tsv` and `manifest_s2_vm_forced.tsv` with a dated
comment line (the k93tri/k94tri precedent). I did not re-run the section
itself in this triage (heavy; box shared with possbuild's detached chain): that
is in the chain below.

## Not changed / worth a look
- `[2b]`'s allowlist is per file; see above.
- Nothing here changes `src/`, `lib/`, `cli/`, or any spec: all four are
  check-side, no D80 hunk owed.
- The conflict with possbuild's own report claims: none. Its "light validation"
  (test-possessify/recursion/reject/registry/corpus/backrefs/atomic) did not
  include these four sections.

## STATE AT HANDOFF
Commits on `lane/posstri` (tip is the last): fdaba81b (cpset), a611b9fc
(rxtsource), 6a0084a9 (size-term pool), dff05ab7 (startset manifests), and
this report. Standalone re-runs done: cpset 28/0, rxtsource 279/0, size_term
32/0. NOT re-run: test-startset, whole test-codegen, full make test.

**Validation OWED, detached chain armed.** `build/tri/chain.sh` (in this
worktree, gitignored) runs
`make -k -j16 -Otarget test-startset test-rxtsource test-codegen test-cpset-structure`
then the full `make -k -j16 -Otarget test`, restoring
`docs/dev/artifact_size_log.tsv` after each. It waits (a detached `setsid`
waiter, 60 s poll) for BOTH `worktrees/possbuild/build/SLOT_DONE` AND
`worktrees/posstri/.lift`; the manager creates `.lift` to release it. Logs:
- `build/tri/STAGES` (lines `four rc=.. wall=..s`, `maketest rc=.. wall=..s`,
  then `DONE`),
- `build/tri/four.log`, `build/tri/maketest.log`,
- `build/tri/DONE` is touched last.
Completion line: `grep DONE build/tri/STAGES`. Verdict: the make `*** [Makefile:N:
test-X] Error` lines, via `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
build/tri/four.log build/tri/maketest.log` (empty = green). If test-codegen or
test-startset is still red there, the first suspect is a second mover of the
same kind (a count that cites the added blocks or abi 66).
