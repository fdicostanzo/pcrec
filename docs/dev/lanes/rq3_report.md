# rq3 — [MEMFN] RQ-3: SIMD bytes size-neutral, reported, checked (2026-10-09)

Lane rq3 (opus), branch `lane/rq3` off main `9c181041` (D155 addendum 2).
The brief is RQ-3 of `docs/design/memfn/integration.md` §R4.9.11, as ruled
by D155 item 9 (Q-R9-9) and D155 addendum 2. It has three parts: NEUTRAL,
REPORTED, and CHECK with no cap.

## 0. Summary

1. **Neutral.** pcrec now has a SIMD BRACKET and a DECISION VIEW in
   `src/core/sb.c`:
   - `pcrec_sb_simd_open` and `pcrec_sb_simd_close` count the bracketed
     bytes into `StrBuf.simd_guarded`, in the uncut unit, and count the
     text's caps breakdown into `simd_size`.
   - `pcrec_sb_len_decide` is uncut minus guarded. `pcrec_sb_size_decide`
     is the caps' measure minus the guarded text's.
   - `pcrec_sb_splice` carries the record across the two scratch-buffer
     splices.

   Every length DECISION reads the decision view (census in §1). Commit 1
   (`fd98c937`) moves zero bytes: a sampled `emit_sweep.py --variant all`
   against `9c181041` reads CLEAN at every variant, base and stream.
2. **Reported.** The stamp `<PREFIX>_SIMD_GUARDED_BYTES` is on every
   artifact, directly after `MEMFN_LIBC`. Its value is FIXED-WIDTH HEX,
   `0x0000000000000000ULL` today. This is abi **71**, next at landing: 70
   is the kit's R4e′.0b.

   The width is a finding (§2). The line renders before the size
   measurement, so a decimal value leaked the guarded count into every
   measured length. The witness caught it: `--warn-emit-bytes`' quoted
   sizes moved by 6 bytes.
3. **Check, no cap.** The check is `make test-memfn-guarded`, run by
   `tests/memfn/run_simd_guarded.sh` and `simd_guarded_check.py` against
   `simd_bounds.tsv`.
   - **The stamp claim.** Stamped ≤ Σ declared row bounds over
     `MEMFN_FORMS`' sites. This is 0 ≤ 0 on the plain build.
   - **The witness.** A test-only `-DPCREC_SIMD_WITNESS` build writes a
     1,620,166-byte guarded block through the sink's ops, at file scope and
     at the VM program's start.
   - **Its arithmetic.** The stamp is blocks × size in every arm.
   - **Its neutrality.** Its artifacts, rc and stderr equal the plain
     build's with the blocks and stamp removed. This holds at six arms over
     a corpus sample plus four named witnesses.

   Sabotage rows S699-S703 sit on the new mech arm `simdguarded`, and all five are DETECTED.

No aggregate guarded-bytes budget was added (addendum 2).

## 1. Reader census (by grep, not by hand list)

**Method.** I grepped `pcrec_sb_len_uncut` and every `.len` or `->len`
read of an artifact buffer under `src/gen`, `src/core`, `src/opt`,
`src/enc` and `src/facts` (§5 lists the commands). Every hit was then
classified as a decision or not.

**Decision readers.** They are now on the decision view.

| reader | site (post-change) | feeds |
|---|---|---|
| VM entry-shape knee | `src/gen/emit_vm.c:10786` (`program_bytes = pcrec_sb_len_decide(&job->vmsb)`) | the AUTO rung compare at `:10921`; the size-quoting stamp `<PREFIX>_VM_PROGRAM_BYTES` at `:11531` |
| caps / size term / ladder measurement | `src/core/compile.c:2658`, `:2660` (`pcrec_sb_size_decide` on csb, hsb) | `emit_code`/`emit_tot`: the size-term threshold (`:2717`), the ladder's records (`:2675`, `:2727`) and the `size_term_choose` argmin, the D84 caps (`:2794`, so the `fit_rungs[]` size-cap arrivals), the refusal's quoted figures (`size_cap_bytes`), and the `--warn-emit-bytes` note (`:2839`) |
| ladder trial scratch abort | `src/core/sb.c:24` (`sb_grow`: `pcrec_sb_len_decide`, and no abort inside an open bracket) | the size-term ladder's per-trial bound (3 × cap) |

**Carriers.** These are not decisions, but without them the guarded
record would be lost:
- `src/gen/emit_vm.c:12828`: the VM program's splice into csb, now
  `pcrec_sb_splice`.
- `src/gen/emit_dfa.c:1247`: the K82 handoff `round` splice.

**Examined and not a decision:**
- `memfn_stamps.c`'s libc scan and its mark splice. They read text and
  write no size. The splice keeps counts; they are offset-free.
- `vm_cls_respell` (`emit_vm.c:1741`, `b->len = 0` and re-put). Counts
  are unchanged. A respell inside a guarded region would stale
  `simd_size`; that is a hazard for the kit (§4).
- `facts_hook`'s `csb.len` (`compile.c`). This is a listing.
- `tests/size`' SIZELOG. This is an external log.
- The `cmt_dropped` of spliced scratch buffers. It was never carried
  before, and carrying it would move the trial abort, so it is still not
  carried.

**Why the caps reader is a second helper.** "One helper" holds for the
length readers: `pcrec_sb_len_decide` is the only function that subtracts
`simd_guarded`. The caps classify text into prose and tables, so they
cannot read a length. They read `pcrec_sb_size_decide`, which subtracts
the same record's text breakdown. The breakdown is measured at
`simd_close` by the caps' own measure. That measure,
`pcrec_emit_size_measure`, moved verbatim from compile.c to sb.c so the
base tier can call it.

Exactness rests on two conditions, both checked:
- **Line alignment.** A bracket opens and closes at a line boundary, and
  `pcrec_sb_simd_open` and `pcrec_sb_simd_close` refuse otherwise.
- **Closure.** A bracket does not end inside a comment or a table, which
  the `open_out` flag checks.

## 2. Findings

- **F1: the stamp's own width was a leak.** The stamp renders in
  `pcrec_memfn_stamps_render`, before the size measurement, which is the
  kit stamps' rule. So its bytes are measured code. A decimal value is one
  byte longer per digit. The witness check's `warn` arm showed every
  quoted size moving by 6 (`1620166` vs `0`). That is the guarded count
  reaching a length decision through the line that reports it.

  The fix is fixed-width hex (`0x%016llx`): the line is 52 bytes whatever
  the count. I considered and rejected two alternatives:
  - rendering the line after the measurement (the K79 shape), which needs
    a second mark and an extra pass;
  - right-aligned decimal.
- **F2: one named size-quote mover**, the same one R4a′ had. In
  `tests/uprops/size_ladder_prefilter_drop.rxt` (composition),
  `RX_VM_PREFILTER_WHY` quotes the DISCARDED hybrid attempt's measured
  size. That attempt now carries the 52-byte line. The mover is named in
  `stamp_mover_census.py`'s `RQ3_SIZE_MOVERS`.
- **F3: kit gap.**
  - `mf_sink` has no `simd_open`/`simd_close` members, and
    `mf_formdecl.guarded_max` does not exist. Both are born in SIMD batch
    1's `MF_SITE_ABI` bump.
  - pcrec's half is in place at the declared signatures:
    `pcrec_memfn_sink_simd_open(void *u, int level)` and
    `pcrec_memfn_sink_simd_close(void *u)`, declared in
    `src/gen/memfn_sites.h`. `level` is typed `int` here; the design names
    it a levels.def token, so the kit fixes the type. They are UNWIRED
    because `pcrec_memfn_sink` cannot assign members that do not exist.
    Batch 1 adds two lines there: `ps->s.simd_open = ...`.
  - The bound for a real form comes from `simd_bounds.tsv` today. It
    should come from the kit's `guarded_max` once declared. The check's
    UNDECLARED arm fails on any `MEMFN_FORMS` token without a row, so the
    first SIMD row cannot land silently.

## 3. Validation (light, CPUs 0-7, this box)

**Commits.**

| commit | content |
|---|---|
| `fd98c937` | part 1, the mechanism (no emitted byte moves) |
| `78bf3808` | parts 2 and 3: the stamp, abi 71, the spec hunks, the witness build, the check |
| `5698bc05` | the FILEPIN self-pin, the abi ledger, the K37 one-line bound |
| `47f42ca0` | the re-pins, the limits_check entry, S699-S703, the CLAUDE.md entries |

**Results.**

- **Part 1 zero movers.** I ran `emit_sweep.py --ref 9c181041 --tree-rev fd98c937 --variant all --every 10` (plain, lowsize, lowdfa, lowboth, lowthr × byte and utf8, all streams). Result: **VARIANTS: CLEAN**, 0 movers and 0 asymmetric in every cell, and every self-check passed (501 s). The full population is OWED to the chain.
- **Part 2 mover census.** `stamp_mover_census.py --ref 9c181041 --abi 69:71 --event rq3`, over the full corpus (5,431 rows) and all 373 composition files:

  | stream | result |
  |---|---|
  | c-default | 4,980 stamps+abi |
  | c-vm | 4,981 stamps+abi |
  | comp-c | 53 stamps+abi + 1 (see below) |
  | comp-h | 54 abi |
  | emit-ir-vm | 4,981 identical |

  The one remaining comp-c artifact is the named size-quote mover (F2). After naming it, the census is CLEAN; that re-run is in the chain.
- **Byte-count re-pins.** I diffed `a` against main's compiler at `-o -`: the only differences are the four abi digits and the one stamp line.
  - `tests/codegen/manifests/m5_stage1_stamps.tsv`: all 12 EMITTED_BYTES rows +52.
  - `tests/resource` K59-PREMUL rung: 762691 -> 762743.
- **Sections after the re-pins**, run with `make -k -j8 test-X`:
  - test-registry rc 0 (limits_check 37/0);
  - test-cpset-structure rc 0;
  - test-resource rc 0;
  - test-codegen rc 0. Before the K37 fix its one red was K37 reading my wrapper's two-line call.
  - test-rxtsource rc 0 (279/0);
  - test-memfn-stamps rc 0;
  - test-memfn-guarded rc 0.
- **`make test-memfn-guarded`** at its default `--every 10`: 59 s including the witness build.
  - 544 corpus rows were sampled, plus 4 named witnesses, × 6 arms = 3,288 cells.
  - Populations: compiled 3,042, VM 1,632, DFA 1,410, two-block 1,632, ladder-moved 6, refused 246.
  - Arithmetic: blocks × 1,620,166 in every arm.
  - Neutrality: holds on every cell.
- **The failing direction.** `run_sabotage_matrix.sh S699..S703`, all solo rows at `47f42ca0`:

  | row | plant | result |
  |---|---|---|
  | S699 | knee | `simdguarded:481fail/8pass` DETECTED |
  | S700 | caps view | `768fail/1pass` DETECTED |
  | S701 | trial abort | `12fail/8pass` DETECTED |
  | S702 | splice | `426fail/4pass` DETECTED |
  | S703 | double count | `1249fail/7pass` DETECTED |

  `== mech run COMPLETE: 5 rows (unexpected: 0, ...)`.
- `make strict`: clean, at commit 1.

**OWED, as a heavy chain armed on `worktrees/rq3/.lift`.** The chain is `build/land/chain.sh` and its verdicts go to `build/land/trailer.log`. It runs, in order:
1. `scripts/perfrun` make test;
2. make strict;
3. the FULL-population `emit_sweep` for part 1 (`fd98c937` vs `9c181041`, `--variant all`);
4. the mover census re-run;
5. `run_recursion_identity.sh`;
6. mech VALIDATE_ONLY;
7. 40 mech rows: S699-S703 plus the 35 that `sabotage_anchors.py ... --step rq3=9c181041..HEAD` derives, all `hunk`.

**Completion lines:**
- `trailer.log`: `== CHAIN DONE`;
- `test.log`: grep `\*\*\* \[(Makefile:[0-9]+: )?test-` (empty means green);
- `mech.log`: `== mech run COMPLETE`.

## 4. Hazards for the kit (not built)

- The bracket must contain whole lines that close their own comments and
  tables. pcrec refuses otherwise, with an internal error naming the
  rule.
- pcrec rewrites text after emission in three places:
  - `vm_cls_respell` re-spells `_class_bitmapN[` reads in the VM program;
  - the K79 prefix render;
  - the mark splice.

  Only the first could alter text inside a bracket, if a guarded helper
  read a class bitmap. `simd_size` would then be stale. C-SEL or this
  check would read a moved artifact.
- The witness writes csb (at the mark) and vmsb (at `vm_init`). A future
  length reader of hsb, or of a scratch buffer that is not spliced, is
  outside its reach. The script header says so.

## 5. Proposed plan-row text

- [RQ-3] STATE:done — SIMD bytes neutral to pcrec's length decisions and
  reported (D155 item 9 + addendum 2).
  - **Mechanism and readers.** The bracket and decision view are in
    `core/sb.c`. The knee and VM_PROGRAM_BYTES, the caps, the size term,
    the ladder and its trial abort, and every quoted figure read the
    SIMD-off length.
  - **Stamp.** `<PREFIX>_SIMD_GUARDED_BYTES` is fixed-width hex, abi 71.
  - **Check.** `make test-memfn-guarded` runs the stamp ≤ Σ row bounds
    check plus the witness build's arithmetic and neutrality.
  - **Sabotage.** Rows S699-S703.
  - **Kit gap.** The `mf_sink` members and `guarded_max` are owed by SIMD
    batch 1, which wires `pcrec_memfn_sink_simd_open/_close` and moves the
    bounds to `guarded_max`.

## Landing merge (rq3land)

Lane rq3land (opus, 2026-10-09) re-landed RQ-3 on main's R4e′.0b (abi 70,
merge 82ff9432; `git merge main` took main at 47842ee3, whose src is
identical to 82ff9432's: the two commits after it are kit docs). RQ-3 now
reads **abi 70 -> 71**.

**Commits.**

| commit | content |
|---|---|
| `3b7d7b69` | the merge, conflicts resolved, every pin re-measured |
| `07a600ec` | FILEPIN self-pinned to `3b7d7b69` (the lane's last src commit) |
| `c59bf075` | S693 re-anchored to abi 71 |

**Conflicts (8 files), resolved by mechanism.**
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`, `run_codegen_tests.sh`
  `ABI_EXPECT`, `match_api.md` §6's guard example: 71. The codegen
  ledger message keeps R4e′.0b's `69 -> 70` clause and appends RQ-3's as
  `70 -> 71`.
- `match_api.md` §6's ledger: R4e′.0b's entry becomes "was `70`"; RQ-3's
  "is `71`" entry now says it was built on 69 and re-landed on 70.
- `m5_stage1_stamps.tsv`, `run_resource_tests.sh`, `run_cpset_structure.sh`,
  `run_recursion_identity.sh`: main's side taken, then re-measured (below).
- `docs/dev/lanes/CLAUDE.md`: both entries kept (r4e0b, then rq3).
- Not a conflict but a reader: `tests/codegen/CLAUDE.md`'s RQ-3 entry
  re-worded to 70 -> 71. The kit's own docs (`memfn/docs/journal.md`,
  `wake.md`) already say "abi 71", correctly; single-writer, untouched.

**Re-pins, each measured on the merged build against a reference compiler
built from `git archive 82ff9432`, at the same `-o` basename.**

| pin | main (abi 70) | now | delta | how verified |
|---|---|---|---|---|
| cpset manifest, all 12 `EMITTED_BYTES` rows | e.g. `a` 23528 | 23580 | +52 each | `run_cpset_structure.sh` [3]'s own diff; `abc`, `\bword\b`, `(?i)HeLLo`, `(a(?1)?b)` diffed: abi digits + the one stamp line |
| resource K59-PREMUL rung (`a{5,25000}`) | 762832 | **762884** | +52 | diffed: abi digits + `#define RX_SIMD_GUARDED_BYTES 0x0000000000000000ULL` |
| recursion identity (B) FILEPIN | `b3e26cfa` | `3b7d7b69` | | self-pin convention |
| S693 (`PCREC_ARTIFACT_ABI` plant) | BEFORE 70 / AFTER 69 | BEFORE 71 / AFTER 70 | | `m6read_check_sab_anchors.py`: 589 rows, all resolve |

- **`RQ3_SIZE_MOVERS`** (stamp_mover_census.py) is unchanged: the one named
  size-quote mover is still `tests/uprops/size_ladder_prefilter_drop.rxt`
  (comp-c). The census re-run (`--ref 82ff9432 --abi 70:71 --event rq3`)
  is in the light tier; its verdict is below.
- **The stamp census.** The resource witness's `--warn-emit-bytes` quote moves
  771040 -> 771092 (code 14985 -> 15037), +52. This is the stamp line being
  measured code (as R4a′'s stamps are), not the guarded count leaking (F1).
- **S693 needed a re-anchor** because the first light-tier `test-codegen`
  went red on [SABANCHOR]: R4e′.0b's row anchors on `PCREC_ARTIFACT_ABI 70`.
  It now plants 71 -> 70, which keeps the same intent (the newest event's bump
  is missing). Its `SAB_DESC` also read "stays 68", stale since r4e0b's
  renumber; it now reads 70.

**The `<fn>__body` readers and the stamp.**
- The stamp sits after `MEMFN_LIBC`, outside every FUNC. `routing_shape.py`
  (C11's routing leg) reads the same FUNC count on the plain and the
  `-DPCREC_SIMD_WITNESS` artifacts for `abc` (1), `\bword\b` (2) and
  `(?i)HeLLo` (1), and the witness stamps are blocks × 1,620,166 (DFA
  `0x18b8c6`, VM `0x31718c`).
- The FUNC-by-name readers (`run_prechecks.sh`, `run_offset_skip.sh`,
  `reqcube_check.py`, `run_dfa_stamps.sh`, `run_encoding_checks.sh`,
  `libc_census.py`) run in the light tier's `test-codegen` and
  `test-memfn-stamps`.
- **FINDING F4 (not fixed).** On a VM artifact the witness build's second
  block sits at the VM program's start, inside `rx_match_anchored`. So
  `routing_shape.py` reads it as `rx_match_anchored holds a directive: #if
  defined(PCREC_RQ3_WITNESS_GUARD)`. That violates D155 addendum 1's floor rule
  ("a function that does work never contains #if").
  - It is test-only: the witness is never in a product build, and the routing
    leg runs only on the plain build.
  - But the VM-program block models a placement the floor rule forbids.
  - It exists to reach the knee reader (`vmsb`'s length). Once real SIMD forms
    obey the floor rule, guarded text in `vmsb` can only come through a
    helper or selector.
  - The manager should decide whether the witness's VM block should be a
    selector-shaped `#if` chain (or a guarded helper spliced into `vmsb`) so
    the witness honours the rule it will one day be checked under.

**Mech list (45 rows).**
- S699-S703, plus the union of
  `docs/design/start_table/sabotage_anchors.py ROOT(82ff9432) {start_table,dec_fallback}/call_graph.txt
  …/refactor_edit_set.tsv --repo . --step rq3land=82ff9432..HEAD`. That is
  40 rows (39 `hunk`, S164 `reach(vm_init)`). It is 5 more than the
  pre-merge 35: S41, S164, S184 (dec_fallback's graph), plus S437, S516,
  S623, S693.
- The output is in `build/land/sa_{start_table,dec_fallback}.tsv`. rc 2 is
  the pre-existing unresolved rows (S571 and others).

**Light tier, pinned to CPUs 0-7** (`build/land/light.sh`; verdicts in
`build/land/light/trailer.log`, codegen re-run in `build/land/light/rerun.log`):
- `make strict` on the merge: clean.
- Every section (codegen, resource, cpset-structure, registry, rxtsource,
  memfn-stamps, memfn-guarded), the recursion identity gate, the census, and
  the part-1 zero-mover `emit_sweep`.
- **The part-1 probe.** Part 1's commit `fd98c937` predates the merge, so
  the probe is the unreferenced commit object `85ab0974a4b15aa430df8488ef8e59da69273cd3`: HEAD `07a600ec` with
  the stamp line suppressed (`if (0)`) and the abi at 70. It runs
  `emit_sweep --ref 82ff9432 --tree-rev 85ab0974a4b15aa430df8488ef8e59da69273cd3 --variant all --every 10`; the
  decision-neutral helpers must read **0 movers** against main.
- Verdicts: see "Light-tier verdicts" below.

**Heavy chain.** `build/land/chain.sh` was rewritten for refs main 82ff9432:
the probe `85ab0974a4b15aa430df8488ef8e59da69273cd3` for part 1 at full population, census `--abi 70:71`, and
the 45 rows above. The aborted 15:11 run's `build.log`/`test.log` were moved
into `build/land/aborted_1511/`.

The chain is started by **the one waiter**, `build/land/gate2.sh` (pid
1349594). Once `== LIGHT DONE` and the codegen re-run are logged, it starts
the chain only if every light verdict is green. The first gate, `gate.sh`,
was stopped with `scripts/safekill` before it read anything, because it
would have counted codegen's stale-anchor red.
- Gate verdict: `build/land/gate.log`.
- Chain verdicts: `build/land/trailer.log` (`== CHAIN DONE`), `test.log`
  (grep `\*\*\* \[(Makefile:[0-9]+: )?test-`, empty means green, read with
  `test.log.perfrun`), `emit_sweep.log` (`VARIANTS: CLEAN`), `census.log`
  (`census: CLEAN`), `recid.log`, `mech.log` (`== mech run COMPLETE`).
