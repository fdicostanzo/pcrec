# z2build — [KIT-VERIFY] U1 step Z2 (docs/design/kit_proof.md §7, rev 2.2)

Lane z2build (opus), 2026-10-21. Branch `lane/z2build`, worktree
`worktrees/z2build`, base main `ec10382cf` (abi 82) with lane/x0fix merged
(`fc926a603`, kit_proof rev 2.2). Build go: Frank 2026-10-21 ("both you and kit
please proceed", then "Proceed through all items").

## STATE AT HANDOFF

- **Built and committed** (7 commits, `bc665f16d..dc74f4f98`, plus this report's
  commit). No abi event, no deny or force bit, no D/K id taken.
- **Light checks green** on the lane tip (below). **Heavy checks QUEUED, verdicts
  OWED**: boxqueue jobs `540-z2build-sweep`, `541-z2build-maketest`,
  `542-z2build-mech`, `543-z2build-x1` (job files in
  `worktrees/z2build/build/z2s/jobs/`). The sweep started 15:12 EDT. Each
  ends with an `== z2build <name> COMPLETE` line in its job.log and writes
  its logs under `worktrees/z2build/build/z2land/` (sweep, make test, mech)
  or `build/z2x1/` (census, X1, stated).
- **Rulings file**: read at every checkpoint; last entry read is **ruling 1**
  (X0 passed on rev 2.2; decide `(?:[a-z]{0,3}\z|x)[0-9]{3}` exhaustively on the
  built artifact). Done: decided, 0 differences (below).
- Do not prune `worktrees/z2build` before the four jobs end; the jobs build and
  read it.

## What was built

| piece | where | note |
|---|---|---|
| harness lever `--harness=kit-proof` | `cli/main.c`, `src/core/internal.h` (`PcrecHarnessOptions.kit_proof`, `pcrec_kit_proof_routed`) | set only through `pcrec_harness_compile`; default and trace builds decline `cover` |
| `mf_preview(art, "R-26.6")` | `src/gen/memfn_sites.c` `pcrec_memfn_art` | after `mf_reach`, routed compiles only |
| span_facts first slice (UL-0) | `src/facts/kset.c` (`pcrec_span_walk`), `facts.def`/`facts.h`/`facts.c` | the k-set walk extended to an exact per-thread subset walk: in-span `A_CTX` narrows per thread, the true set (view-gated eol bytes, x0fix's R2 ruling); declines named (`erased-nfa`, `end-mark`, nullable, dead); budget `PCREC_SPAN_WALK_SUBSETS` (limits.def, UNMEASURED label) |
| `--emit-facts` row `span_facts` | `src/dump/facts_dump.c`, `docs/spec/facts_listing.md` §4.1.2¶7c | the spec hunk |
| MkLang / MkEnd / MkKnown | `src/facts/facts.h`, `src/gen/known.h`, `known.c` | MkEnd reads A from the EMITTED entry on both arms, with scan edges |
| `cover_conj[]` C1-C14 | `src/gen/known.c` | first failing row = the `why`; C8's disagreement is an internal error in the trace build |
| `cover` LOCATE row, `emit_cover` | `src/gen/emit_dfa.c` | after `rev-end`; REPORT site `DELEG_COVER`; the DEFAULT build holds the kit's defined class to the stated sets (`pcrec_cover_proof_diff`, any difference an internal error) |
| true `exact_len` over the SENT sets | `src/gen/memfn_sites.c` `pcrec_memfn_span0_stated` | every start-origin FIND site; was `_today` (exact_len 0) |
| compound.c field reads (§2.6) | `src/core/compound.c`, `compile.c` | A1 reads the row's NEXT ask, A5 `end_seeded` |
| trace records | `KITPROOF`, `SPANSET`, `SITESTATED` under `PCREC_KIT_PROOF_TRACE` | the census and stated-check inputs |
| `make test-kitproof` | `tests/kitproof/` (new; CI shard 1, weight ESTIMATED) | 24 verdicts, 6 facts, 55 answers (393 cells) against libpcre2 10.46's committed answers |
| C17 | `tests/memfn/site_manifest.tsv` row COVER (`delegated`), `site_census.py` `PASS_CONFIGS` | see deviation 2 |
| sabotage rows | S1130-S1141, S1144, S1148, S1149; S512 and S894 re-pinned/re-aimed | mech arm `kitproof` |
| instruments | `docs/design/kit_proof/z2/` | X1 driver, exhaustive cell, census/stated/hist |

## Measured on the lane (light)

- `make strict` clean; `test-spec-history`, `test-plan-lint`, `test-memfn-deleg`
  (14/0, after moving `emit_cover`'s `mf_result` to the arena: C10 rule 4),
  `test-memfn-manifest` (13/0), `test-kitproof` (88/0), `test-registry`,
  `test-memfn-finder`: all rc 0. Lever fence 3 checks + 4 controls green.
  Sabotage anchors: 894 rows, all resolve. VALIDATE_ONLY on the 71 queued rows:
  all valid. Every new row's REACH probe reads its expected value on the clean
  tree.
- **Ruling 1 decided**: `(?:[a-z]{0,3}\z|x)[0-9]{3}` reads `cover` k=4 (S_d =
  `x`,`[0-9]`x3) on both encodings. Every subject of length 0..8 over
  {a, z, x, 0, 9, \n, #} (6,725,601 subjects), every startoffset and the
  find-all loop against libpcre2 10.46: **0 differences in 66,243,390 cells,
  native and utf8 alike** (`docs/design/kit_proof/z2/out/exh_ruling1_*.txt`).
  The control (the PCRE2 side handed `(?:[a-z]{0,3}|x)[0-9]{3}`) reads 2,984
  differences at length 5. No conjunct declines it.
- The built slice's statements on the five in-span witnesses are green against
  libpcre2 10.46 by `x0.py stated` (`out/stated_built.txt`), including
  `[ab](?<=a)c|bc` at exact_len 2, where `x0/stated.tsv`'s slice row stated 0
  (both sound; the product {a,b}x{c} is exact).
- Default-build identity was spot-checked earlier in the lane (800 base-corpus
  compiles plus 42 samples, byte-identical with main's build/pcrec); the full
  proof is the queued sweep.
- X1 smoke (7 items): 0 differences beyond X0's U1 class; X1's own plant
  (`X1_PLANT=1`, ends one byte late) reads red.

## Owed (queued)

1. `540-z2build-sweep`: emit_sweep vs `fc926a603`, streams c-default/c-vm/
   emit-ir/composition, `--arms start`, `--variant all`: **0 movers expected**.
   MEASURED for the first part before handoff (`build/z2land/sweep/main.log`):
   c-default, c-vm, emit-ir 0 movers over 5,811 argv patterns (5,357-5,358
   compiled), composition 0 movers over 387 files, self-check passed.
   Then facts and dumps as a MEASUREMENT: declared deltas are the new
   `span_facts` row on every `--emit-facts` listing and the
   `PCREC_SPAN_WALK_SUBSETS` row of `--list-limits`; nothing else should move.
2. `541-z2build-maketest`: perfrun make test (shape 4,2).
3. `542-z2build-mech`: 71 rows (the 15 new, S512, S894, and 54 re-runs the
   diff derives: rows anchored in a definition `fc926a603..HEAD` changes, on a
   changed `.def`/`.h`, or on the C17 manifest/census and the lever fence).
   Every new row is expected DETECTED; S1139 and S1141 are the two I am least
   sure of (S1139 is C9 dropped alone, not the design's two edits; S1141's
   hybrid may decline at C4 before the plant matters). An UNDETECTED there is
   a finding about the plant, not the code.
4. `543-z2build-x1`: the census (13,956 items: K35's why histogram, the C8
   control, agreement with conj.py), X1 over X0's 1,433-item population, and
   the stated check on 1-in-4 of the census's SENT statements. Expected: C8
   internal errors 0, agreement with conj.py on cover-vs-not (any disagreement
   is a design/code disagreement and a stop-rule item), X1 0 red beyond U1.

## Deviations from the design and the brief

1. **`cover` declares no kit ask (`kask`)**: its predicate reads `pcrec_cover`,
   whose C13 asks the kit; declared as a LOCATE→LOCATE read it would be a
   self-edge the read graph's cycle check refuses.
2. **C17: the row is `delegated`, not `pending`.** A `pending` row whose
   emitter spells no search form fails rule 4 (stale), and `emit_cover` spells
   none (the kit writes the FIND). A `delegated` row must be reached by the
   corpus pass, which never compiled through the harness. Fix, general: the
   traced binary is now linked as the harness (`-DPCREC_HARNESS`; with no
   lever it compiles as build/pcrec) and every corpus pattern runs under each
   row of `site_census.PASS_CONFIGS` (default, kit-proof). C17_ROW_FLOOR
   13 -> 14, S512 re-pinned. **This widens the lever fence's allowlist** by
   `tests/memfn/site_census.py` and `tests/kitproof/` (precedent:
   `tests/memfn/run_arm_reach.sh`): main's call.
3. The slice states the TRUE set and exact products the design text called
   0 (deviation in the sound direction, libpcre2-checked).
4. Two new decline reasons in the facts listing (`decline:erased-nfa`,
   `decline:end-mark`), in the spec hunk.
5. Not built at Z2: the out-of-span context records (the D168 producer half),
   CK-1/CK-7/CK-10, and the C13 refusal-detail split (C13 reports `refused`).
   Rows S1142/S1143 (design: ship UNREACHED) and S1150 (PROPOSED, not
   allocated) have no row file: S1150's plant (union instead of per-thread
   narrowing) is not one anchored edit in the walk; its detectors (the facts
   rows, X0's stated check) are in place. S1145 is B1's (the deny); S1146 and
   S1147 are kit-side.
6. X1 grows its subject families from conj.py's plan (as X0 did); the oracle
   is still libpcre2. Patterns of X0's U1 class (a `{0}`-quantified anchor
   group, upstream_issues.md U1) are reported apart.
7. One slip: I copied the site manifest into `/tmp` for a scratch comparison
   and removed it a few seconds later.

## Not mine, seen in passing

`boxqueue status` shows main's `120-main-postmerge` FAILED with
`POPULATION-SHORT: done ran=none declared=1` (its job.log lacked the
`== postmerge COMPLETE` line), verdict GREEN.

## TRIAGE (z2tri)

Job 541-z2build-maketest: 74/74 sections, one red, `test-cand-oracle`.
Rulings file read through entry 3; entry 2 applied below.

**Class (b): the check legitimately sees the new `cover` row; no defect in Z2,
no environment cause, nothing under `src/`.** Premise test: `bash
tests/codegen/run_cand_oracle.sh` reproduces the red in about 60 s, one FAIL
line: `[cand-oracle-coverage] rows with no witness: cover` (165 passed / 1
failed). The check's K35 rule is that every identity in `cand_rows[]` has a
witness line that REACHES it, and the only way to reach `cover` is the harness
lever (`build/pcrec-harness`), which the oracle never used.

Fix, in the check, no name exemption:

- `cand_oracle_witnesses.tsv` gains two `cover` witnesses (`foobar`, `\bcat\b`,
  the tests/kitproof verdict patterns) whose FLAGS carry the harness option.
  `run_cand_oracle.sh` compiles a witness with that option by the trace build's
  own `pcrec-harness` (same sources, same `-DPCREC_CAND_TRACE`) and keeps the
  existing reach rule: the line must print a `CANDROW` hit for `cover`.
- New `[cand-oracle-shipped]` check: every harness witness is compiled again
  by the shipped trace compiler WITHOUT the option and must print NO `CANDROW`
  hit for its row; its population is counted (at least one, equal to the
  number of harness witnesses). Failing direction: with the second compile
  routed through the lever (scratch copy), both witnesses FAIL with "the
  SHIPPED compiler reaches harness-only row 'cover'" (169 passed / 2 failed).
  Result after the fix: 171 passed / 0 failed.

Ruling 2 (a manifest state `preview`):

- `tests/memfn/site_manifest.tsv`: COVER `delegated` -> `preview`; the header
  states the three-word vocabulary.
- `site_manifest_check.py`: `preview` accepted; its emitters must spell no form
  (rule 3), it is a listed site for rule 2, and rule 4's preview clause holds
  it to "rendered over the harness configs, and over NO shipped config".
- `site_census.py`: `run_corpus` also returns each compile's config class,
  DERIVED from the row's lever (`config_class`: a `--harness=` lever is
  `harness`, anything else `shipped`), so a row cannot be declared shipped
  while routing the lever; `verdict` takes `preview` and the tags; a selftest
  line covers the four directions (harness-only passes; a shipped render fails;
  no harness render fails; a function shared with a delegated row fails).
- Result: `bash tests/memfn/run_site_manifest.sh` 15 passed / 0 failed, "COVER
  was rendered by 48 harness-config compile(s) and by no shipped-config one",
  manifest 14 rows (delegated 12 / preview 1 / pending 1), floor unchanged.
- The compound lever fence (`tests/compound/run_lever_fence.sh`) was re-run
  and is green (3 checks, 4 controls) after one more allowlist widening:
  `tests/codegen/run_cand_oracle.sh` and `tests/codegen/cand_oracle_witnesses.tsv`
  (test drivers of the lever, no new global; the same kind as ruling 2's two).
  This is a THIRD widening beyond the two the ruling named: main's call.

Docs: tests/memfn/CLAUDE.md (rule 4, three-state status),
tests/codegen/CLAUDE.md, the header of run_site_manifest.sh.

OWED, and why: the commit, and the solo mech rows that anchor on the oracle
(S594, S597, S844, S1019 and the C17 rows S510, S511, S512, S1091). Boxqueue job
542-z2build-mech was RUNNING when the work finished (the mech matrix archives
`HEAD`, so a commit mid-run would change what its later rows test) and 543 is
pending, so nothing was committed. The edits sit in the worktree; a copy of the
diff is `build/z2tri/z2tri.patch`.

## FIX (z2fix)

Lane z2fix (opus), 2026-10-21, on `lane/z2build`. Rulings read through entry 5
(the HOLD during the kit's timing window 560: from it on, edits and reads only).

**Headline: none of Z2's reds is a defect in the built code.** All three are
defects in Z2's own instruments, and each is now fixed and has a
failing-direction control. Nothing was declined from `cover`: there was nothing
to decline, so no conjunct was added and the population is unchanged. The
default build is unmoved. The `src/` change is trace-build-only (every edited
line sits inside `#ifdef PCREC_CAND_TRACE`). Measured: `known.o`, `facts.o` and
`memfn_sites.o` built without the trace flag are byte-identical (debug info
stripped) before and after the change. No abi event, no kit-side change, no new
S-id.

### Premise test

`(*positive_lookbehind:a)b` on `ab`, through `build/pcrec-harness
--harness=kit-proof`, answers `match 1 2`, the same as PCRE2. It does NOT
reproduce. `(?<=a)b` gives the same answer. Both negative spellings answer
correctly on `b`. The red came from the instrument, not the artifact.

### (1) X1: an item-directory collision in z2.py

`x1_item` built each artifact in `items/FLAGS_<first 40 hex of the pattern>`.
Two patterns that share their first 20 bytes therefore shared one directory, and
the `-j8` workers overwrote each other's `a.c`/`drv`. An item then read another
pattern's artifact.

- The evidence: 11 directories were shared by 26 items. They hold all 11 reds
  and the `PermissionError` (an exec of a `drv` being rewritten). Both shapes
  are this one cause:
  - (a) `(*negative_lookbehind:a)b` shared a directory with
    `(*negative_lookbehind:a)c` and `(?:a|b)`.
  - (b) `(*UCP)(?i)[[:lower:]]` shared one with `(*UCP)(?i)[[:lower:]x]`, whose
    `x` folds to `X`. That is the "second match at 1" on `aX`.
  The fold-inert rule and the C_{-1}/read_floor code were never involved.
- The fix: the key is the whole pattern's sha1 (`item_key`). The subject seed
  was also `hash()` of a string, which Python randomizes per process. It is now
  `zlib.crc32`, so X1's subjects are reproducible.
- The re-run of the 30 formerly colliding items: 28 cover artifacts, 64,100
  subjects, 473,046 cells, **0 bad**. That includes all 11 reds and the
  PermissionError item.

### (2) Stated check: 40 reds in 2 classes, both on the checker's side

- **26 (19 slice, 7 site): statements made by a compound PART.**
  `pcrec_compound_walk` compiles [MATCH-SPLIT]'s parts inside the parent's
  compile, even where the final artifact is `RX_COMPOUND "none"`. Each part's
  compile prints its own SPANSET/SITESTATED/KITPROOF into the same stderr. The
  census attributed all of them to the whole pattern P.
  - The part is Q, which is P with its floor anchors (`^`, `\A`, `\G`) killed
    and searched only past the floor (src/opt/derive.c).
  - Every one of the 26 is a floor-anchor pattern stating Q's set, for example
    `^a|b` -> Q = `b`, S_0 = {b}, and that set is correct for Q.
  - gdb confirmed the stack: `part_compile` -> `pcrec_cover` -> `cc_exact` ->
    `pcrec_fact_span`.
  - The fix: the three trace records end in the part's role (`-` for the compile
    itself). The census keeps the role. A Q statement is checked against P with
    `\G` -> `(?!)` and with absent-before left out of the contexts, which is
    exactly Q's domain ("P anchored at any later start").
  - `decision()` reads the compile's own last KITPROOF, never a part's, in
    hist, x1 and exh.
- **14 (12 slice, 2 site): `\K` patterns.** x0pcre counts an anchored match
  that does not START at the origin as no match. `\K` moves PCRE2's reported
  start, so the oracle measured the reported-start language. The statement is
  about the attempt origin, which is a FIND site's candidate, so the stated
  `{a,b}` for `(?:a\K)?b` is right.
  - The fix: `oracle_pattern` drops `\K`, lexically (escapes, classes,
    `\Q..\E` and `(?#..)` are copied verbatim). This is exact because `\K`
    never changes what matches.
  - `\K` never reaches `cover`: in the census, 116 `\K` items decline at C1 and
    104 have no DFA decision.
- **Re-check of every statement of the 66 census items behind the 40 reds,
  re-censused with roles: 54 statements (17 own, 37 Q), red 0**, 4
  inconclusive bytes.
- **The control:** `Z2_STATED_CONTROL=raw` is the pre-fix check (the pattern as
  written, every context). It reads **red 54 of 54**.

### (3) Mech: S1141 equivalent, S685 not Z2's

- **S1141 is an equivalent mutant at Z2. It is declared, not fixed.**
  - The structural argument: the anchored machine A is built only where a
    FINISH row on the compile's finisher route declares it
    (`build_anchored_dfa`, src/core/compile.c: `verify-at`, the DFA route
    alone). On a VM-finisher hybrid `anchored_ok` is false, so C4
    (`anchored-A`) declines whatever C1 lets through.
  - Measured on a scratch build of the plant: the witness `(?'w'cat)` moves its
    first failing row from `finisher-dfa` to `anchored-A`, and its artifact
    still reads `RX_ENGINE "vm"` / `RX_DFA_SCAN "unanchored"`.
  - No `make test` check can see the difference, because the decline's identity
    exists only in the trace build.
  - The row now reads `SAB_EXPECT=UNDETECTED` with `SAB_EXPECT_REASON`. Its
    header says what would make it DETECTED: a VM-route FINISH row that
    declares A.
  - The population figure is OWED. `s1141pop.py` re-decides every census item C1
    declines (2,207 in the 543 census) with the planted trace harness. I
    stopped my own run of it, which was waiting on the box lock behind 560; it
    is part of job 545 and must read `planted cover admissions = 0`.
- **S685 UNREACHED is pre-existing and not Z2's.** The row is byte-identical to
  main's (last touched by main's `08bda4927`, R-12 VMLAZY REPLACE), and its own
  text declares the UNREACHED as EXPECTED (VMLAZY deleted at R-12). Left alone.
- All 18 rows anchored in the three edited files still resolve (each
  `SAB_BEFORE` count equals its `SAB_COUNT`). `VALIDATE_ONLY` over all 894
  rows: valid.

### (4) Why X0 passed and X1 failed: X0's verdict stands

- **X1's reds:** they come from z2.py's directory key alone. X0 builds no
  per-item artifacts: it simulates conj.py's plan.
- **The stated reds:** they come from a population X0 never had, plus the
  oracle's `\K` rule.
  - The Z2 census's SENT statements include part-compile statements, and X0
    reads the whole pattern's emitted machine.
  - X0's population (`pop.jsonl`, 1,433 items) holds no `\K` pattern, so the
    one shared oracle trait (x0pcre's reported-start rule) never met X0's
    population.
- **The reading (conj.py/kvdfa) has neither defect.** It reads the whole
  pattern's emitted machine. **X0 does not need a re-run.**
- `x0.part1_site` gained `absent=True`, a default-preserving argument, so X0's
  own calls are unchanged.

Side record, not a stop item: the 543 census reads 44 harness/conj.py
disagreements, all harness-decline / conj-cover, all `exact/producer-short`.
That is the sound direction, and C8's producers-disagree internal errors are 0.

### STATE AT HANDOFF

- **Commits** on `lane/z2build`: this section's commit (`z2fix:` prefix).
  `docs/dev/artifact_size_log.tsv` is left modified and uncommitted (job 541
  rewrote it; it is not this lane's).
- **Queued, verdicts OWED**:
  - **`545-z2build-x1fix`** (job file `build/z2s/jobs/545-z2build-x1fix`, output
    `build/z2x1fix/`): the builds, `make strict`, `test-kitproof`, S1141's
    planted trace build (from `git archive HEAD`), census, hist, X1 over the
    1,433-item population, stated 1-in-4, and s1141pop.
    - Green iff the job.log carries `z2fix verdict: build_rc=0 census_rc=0
      x1_rc=0 stated_rc=0 s1141_rc=0` (`expect done=1 lines=`). Each tool
      echoes its own `DONE rc=` line.
    - Expected: X1 red-beyond-U1 0 with no ERR, stated red 0 with no unchecked
      part role, s1141pop admissions 0.
  - **`546-z2build-s1141`**: S1141 solo. Expected `UNDETECTED (expected)`,
    `unexpected: 0`.
- **Light checks done before the HOLD:** the premise test, the 30-item X1
  re-run, the 66-item stated re-check and its control, the S1141 witness under
  the plant, and the default-object identity.
- **What I ran during 560's window, before I read ruling 5:** six single-file
  gcc compiles (the object comparison) and the start of a boxlock-waiting job,
  which never got the lock and was stopped.
- Last ruling applied: **5**.
