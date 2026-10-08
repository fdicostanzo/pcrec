# decfbB0 — [DEC-FALLBACK] refactor B, step B0: the instruments

Lane decfbB0 (opus), 2026-10-08, branch `lane/decfbB0` off main `ab583f6b`.
There is NO compiler change: `git diff ab583f6b HEAD -- src cli lib memfn` is
empty. The charter is `docs/design/dec_fallback.md` rev 2: §4.2's B0 list,
§11's rulings and §R's dispositions. The model is [START-TABLE] C0
(`stc0_report.md`).

Three sonnet sub-lanes worked in their own worktrees and were merged into
this branch:
- decfbB0a: item 10;
- decfbB0b: items 6 and 11;
- decfbB0c: items 7 and 9.

Their reports carry the detail and are committed beside this one
(`decfbB0a_report.md`, `decfbB0b_report.md`, `decfbB0c_report.md`). This lane
did items 1-5, the merge, the gate runs and the docs.

## Summary (a fresh agent resumes from here)

**Status.** B0 is delivered and validated, except the heavy chain. The chain
is ARMED, detached, on `worktrees/decfbB0/.lift` (see "Owed"). Every instrument
was shown both ways: zero diffs on main against itself, and red on a planted
change. Every new floor is measured.

**The B0 gate run** (main `ab583f6b` against this branch, which has the same
src): CLEAN, 379 s.
- Command: `emit_sweep.py --ref ab583f6b --tree-rev HEAD --variant all --trace
  --trace-order fallback=ordered --jobs 6`.
- Scope: 5 variants × 2 bases × (c-default, c-vm, emit-ir, emit-ir-auto ×4
  arms, stderr, plus facts and dumps at the first base) over 5,423 corpus
  rows, and a trace pair per variant.
- Result: 0 movers, 0 asymmetric, every plumbing check held, all 50 tally
  reports held their floors, every trace floor held, and the trace build moved
  0 stdout bytes in every variant.

**Next:** B1, the fallback trace. `row_reach` (item 8) and the fbt SEQUENCES
half (item 11(a)) read that trace, so they land there.

## Deliverables

| # | deliverable | where | both directions |
|---|---|---|---|
| 1 | `--variant NAME\|all\|NAME=CFLAGS`, `--bases` (byte, utf8) | `scripts/emit_sweep.py` (`VARIANTS`, `run_variants`) | clean: the gate run. Red: an unapplied `-D` fails the plumbing check. This was observed live; it is how the `--list-limits` defect below was found. The self-test asserts that `lowdfa`/`lowthr`/`lowsize`/`lowboth` are red on the shipped binary and that `plain` is clean |
| 2 | stream `emit-ir-auto` (stdout+rc+stderr at the default engine, refusals included; base + `-fno-prefilter`/`-fprefilter`/`-fno-prefilter-collapse`), per-token floors, thin-tag manifests | `emit_sweep.py` | clean: the gate run. Red (a): a planted listing token (`no-nullable-exact` → `…exacT` in a scratch build) gives 143/138/143 movers on the three arms that print it. Red (b): S-I3 (the arm dropped from the stream's argv). The self-test goes 3 red, and the full-corpus run goes red on `TAG FLOOR … no-fno-prefilter 0 < 1430` and on the `(?:ab){0,16000}` manifest |
| 3 | stream `stderr` (full stderr + rc of the stream-1/2 compiles, refusals compared), refusal floors per engine | `emit_sweep.py` | clean: the gate run. Red: a planted warning text (`large artifact` → `artifacT`) gives 5 movers in `stderr`, and the same 5 in `emit-ir-auto[-fprefilter]`, whose stderr carries the warning |
| 4 | every floor measured in emit_sweep's OWN population, per variant and per base | `VARIANT_PINS` (10 cells), `TRACE_VARIANT_RECORDS_FLOOR` (5) | measured by one run of main against itself (`--emit-pins`). Held by the gate run, red under S-I3 (above) |
| 5 | the attempt histogram's own driver, parent vs child | `docs/design/dec_fallback/attempt_hist.py` (imports decfb0's `build_ref.PATCHES`; `census.py` unchanged) | clean: HEAD vs HEAD, all 5 variants, 4,794 blocks, BYTES_DIFF 0. Red: a dangling plant commit (`attempt < 8` for `COMPILE_MAX_ATTEMPTS`) makes 11 lowsize compiles differ (the 9-attempt ladders) |
| 6 | hand-written `check_ir_value` rows for every T2 row and reached scope | `tests/prefilter/run_prefilter_tests.sh` §7b | 50/0 (was 34). Each value was oracle-read from today's compiler. The lowsize row builds its reference compiler once |
| 7 | `trace_diff.py --order SLOT=ordered\|set`; `--variant` composes with `--trace` | `scripts/trace_diff.py`; `emit_sweep.py --trace-order` | 30/30 tests (13 new). S-I2 plant (`--order` ignored): 4 red. The variant traces ran in the gate run |
| 9 | `state_readers.sh` re-run; `call_graph.py --family fallback`; `sabotage_anchors.py --edit-names/--final` | `docs/design/{start_table,dec_fallback}/` | see the "Item 9" section below |
| 10 | `alloc_check` W5: `pcrec_emit_facts` with the injection in the force loop | `tests/core/alloc_check.c` | green: `make alloc` 9/0. Red: the forcing arm disabled; the arm moved below `nomem` (S-F0); a pattern that stops reaching the loop (K35 floor) |
| 11(b) | the OBSERVED-STAMP LEG: 8 `ENGINE_SEL` + 7 `UNROLL_K_WHY` values against match_api.md §6.3, K35 floors | `tests/codegen/run_fallback_table.sh`, `TEST_SECTIONS` `test-fallback-table`, mech arm `fallbacktable` | 66/0 in ~7 s. Red: a witness dropped (S-I4); a value removed from the spec; `ESEL_FORCED` spelled "selected"; a PFLW text changed |
| 11(c) | `VM_PREFILTER_LANG_WHY` (6 forms) and `VM_PREFILTER_WHY`, with hand-written texts | the same script | inside the 66 |

The registry's extractors moved to `tests/lib/spec_extract.sh`, so the
observed-stamp leg reuses the docs leg's extraction rather than copying it.
`axes_registry_check.sh` was byte-identical before and after the move: 214/0.

### Item 9 (decfbB0c)

- **state_readers.** The derived census on this base has the same 408 lines
  as at `42ab7c25`; only the line numbers moved.
- **The family.** `--family start` output is byte-identical to before. The
  fallback family has 12 roots and 14 derived seeds. It is the seeds' one-hop
  readers plus the roots: 53 members.
  - The transitive reach was useless: `compile_driver` reaches 761
    definitions.
- **Re-aims.** 11 RE-AIM rows, the same as the design §4.4, at the same
  commits.
- **RE-RUN against rev 1's hand list.**
  - Reproduced: S237/S252/S420 at B2, S193, S64/S176 at B4, S40, and
    S224-S226.
  - S189/S191/S192 are seen only by `--step` at B3. They need the commit's
    diff, so they cannot be computed before B3 exists.
  - Added: eight `compile_driver` rows at B3+B5 (S166, S169, S178, S257, S261,
    S306, S437, S440).
- **Owner resolution** stays a hard error. S571 is the one pre-existing
  unresolved site.

## Floors (measured, main `ab583f6b` against itself, two builds per variant)

**Where the values are.** The full table is in `scripts/emit_sweep.py`
(`VARIANT_PINS`) and in the per-run TSV `variant_tallies.tsv`.

**How they were set.**
- Each floor sits at the smaller side's measured value (DIFFER_PINS' stance).
- Every tag under 100 has a manifest: the shortest pattern carrying it on both
  sides.

**Reach (both_ok per stream):**

| cell | c-default | c-vm | emit-ir | facts |
|---|---:|---:|---:|---:|
| plain/byte | 5,075 | 5,069 | 5,069 | 4,955 |
| lowsize/byte | 4,941 | 4,937 | 4,937 | 4,817 |
| lowboth/byte | 4,941 | 4,937 | 4,937 | 4,817 |

The other seven cells are in `VARIANT_PINS`.

**The `emit-ir-auto` base token counts, plain/byte:**
- `refused` 3,234;
- `yes` 1,412;
- `no-backreference` 492;
- `no-nullable-exact` 138;
- `no-linked-call` 127;
- `no-engine-vm` 17;
- `no-dfa-overflow` 1;
- `no-nullable-collapsed` 1;
- `yes-collapsed` 1.

The last three are thin and have manifests.

**What the variants add.**
- lowdfa raises `no-dfa-overflow` and `yes-collapsed`.
- lowsize and lowboth raise `yes-collapsed` to 34 and `no-fno-prefilter`
  (SIZECAP) to 67.

**Trace records per arm (c-default / c-vm):**

| variant | c-default | c-vm |
|---|---:|---:|
| plain | 315,269 | 105,080 |
| lowsize | 344,001 | 111,874 |
| lowdfa | 314,815 | 105,080 |
| lowboth | 342,053 | 111,874 |
| lowthr | 334,637 | 111,944 |

**The attempt histogram** (decfb0's population, 4,794 blocks):
- the population floor is 4,746 (1% margin);
- each variant must have at least one multi-attempt compile (measured 21 /
  231 / 90 / 238 / 61);
- the plain probed build must be byte-identical to the unprobed one.

**Self-test** `scripts/tests/emit_sweep.py.test`: 14/0 (was 7).

## Choices where the note was ambiguous

1. **The variant plumbing control is a table of witness stamps
   (`VARIANT_WITNESSES`), not `--list-limits`.** MEASURED: `--list-limits`
   prints limits.def's literal (`30000000`) on a
   `-DPCREC_MAX_AUTO_DFA_ELEMS=3000` build, so it cannot see the `-D`. The
   witnesses:
   - lowsize: `(?:a\K){0,10}ab` gives `cap-rescue`;
   - lowdfa: `(?:a|b)*a(?:a|b){11}` gives `collapsed-prefilter`;
   - lowboth: both of the above;
   - lowthr: `--engine=vm (((?:a{0,2}b)+c){0,20}d){0,20}e` gives
     `capacity-declined`;
   - plain must stamp none of these values.
2. **The CFLAGS composition.** A variant appends its `-D` set to the
   Makefile's own `-O2 -g`. The plain variant reuses the two default builds.
3. **Streams per variant.** Composition is not run per variant: the default
   run covers it, and its files carry their own options. facts and dumps take
   no base, so they run once per variant.
4. **`emit-ir-auto`'s arms run at every variant × base.** The note says
   "every variant × base encoding, plus the arms", which allowed either
   reading; this takes the wider one. Thin tags get manifests below a count
   of 100. Listing tokens are read by section and row name.
5. **The `stderr` stream recompiles the stream 1-2 argv** rather than
   threading stderr out of streams 1-2, so those streams are untouched. It is
   deterministic: the same argv gives the same stderr.
6. **Trace per variant.** It runs at the first base. The per-variant records
   floor is new and measured. The trace stdout check reads that base's
   hashes.
7. **attempt_hist's anchors.** It reuses decfb0's PATCHES (one copy; a
   `__main__` guard was added to `build_ref.py`) and fails closed on a
   drifted anchor. B3 rewrites the catch branch and must hand the child's
   re-anchored probes with `--child-patches`, re-verifying their intent.
8. **The byte-figure `_WHY` texts** (decfbB0b). They are held to the shape
   `^size cap retry, (exact|hybrid) [0-9]+ > 1000000$` plus figure > cap. The
   figures move on every emitted-text abi event. The `nfa N` form is held to
   its full text.
9. **W5's post-loop trials** (decfbB0a) are reported as a NOTE, not
   asserted: see the finding below.
10. **No new S-ids** were taken; the mech arm `fallbacktable` is registered
    with no rows, as stc0 did for `emitsweep`. Drafts for S-I2/S-I3/S-I4 are
    the plants recorded above.
    - S-I3's detector is `scripts/tests/emit_sweep.py.test` (arm
      `emitsweep`).
    - S-I4's detector is fbt (b).
    - S-I2's detector is `trace_diff.py.test`.

    Numbering is left to the manager, because several lanes are taking S-ids
    concurrently.

## Findings

- **`pcrec_emit_facts` aborts on OOM in its listing renderer** (decfbB0a).
  - What happens: 9 of 11 post-force-loop allocation failures die by SIGABRT.
    The FactsRows/StrBuf row buffers in `src/dump/facts_dump.c` have no error
    channel; `sb_grow` aborts when `sb->cx == NULL`.
  - Class: the same as K7 / lens-5 F1, on the `--emit-facts` path.
  - Recommendation: a K-entry. Once it is fixed, W5's NOTE population can be
    promoted to an asserted class.
- **`--list-limits` reports limits.def's literal, not the compiled value.**
  Under a `-D` override the listing is therefore wrong about the binary it
  runs in.
  - Probably intended: the registry describes the def.
  - Still worth a sentence in `limits.md` if a caller reads it as "the
    limits this binary enforces".
- **The corpus has grown past emit_sweep's PINS.** That is 5,423 argv rows
  against the measured 4,606. The floors still hold; they were not re-pinned
  here because that is outside B0.
- `dec_fallback.md`'s `-fprefilter` forced-on SIZECAP witness stamps
  PFLW "size cap retry, exact", not "forced" (decfbB0b). This is today's
  behaviour, pinned only through the listing row.

## Owed (the heavy chain, ARMED)

- **Chain script:** `worktrees/decfbB0/build/land/chain.sh`. It runs `make`,
  `make -k -j6 -Otarget test` (which includes the new `test-fallback-table`
  and the §7b rows), `make strict`, `make alloc`, `make testscripts`, mech
  `VALIDATE_ONLY=1`, and 39 mech rows. The rows are every row whose detector
  suite this lane changed (emitsweep, prefilter, registry, resource/alloc).
  No mech row anchors a file this lane changed.
- **Verdicts:** `build/land/trailer.log`, one `rc=` line per stage, ending
  `== CHAIN DONE`. For make test, read `build/land/test.log` with
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (empty = green). For mech,
  read its own `== mech run COMPLETE` trailer in `build/land/mech.log`.
- **The waiter** polls `worktrees/decfbB0/.lift`. It was started with
  `nohup setsid`; its PID/SID are in the handback message.

Already run in this lane, outside the chain:
- the B0 gate run (above);
- the attempt histogram, clean and planted;
- the emit_sweep self-test;
- per sub-lane: `make test-codegen`, `make test-registry`, the prefilter
  suite, `make alloc` and `make strict` (in their reports).

## Commits

These are `lane/decfbB0`'s commits, with the three sub-lane merges:
- `decfbB0a` (alloc W5);
- `decfbB0b` (spec_extract move, §7b rows, fbt + section + mech arm, docs);
- `decfbB0c` (trace_diff `--order`, call graph family, regenerated anchors);
- then this lane's commits: emit_sweep variants/streams, plumbing
  witnesses, attempt_hist, self-test, pins, docs, plan.md and this report.
