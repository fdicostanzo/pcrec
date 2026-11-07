# Lane altbuild — alternation normal form stages 1, 2p, 2b (BUILD)

STATE: stages 1, 2p, 2b built (lane altbuild stopped in 2b under its STOP RULE, ruled R4; lane altbuild2 finished it); review r5 altcode's ruled fixes applied by lane altfix, validation OWED ("Lane altfix", OWED). Design: `docs/design/alt_normal_form.md` rev 3.
Build go: Frank, 2026-11-06, stages 1, 2p, 2b only.

## Ids taken

- Sabotage ids: **S1880-S1899** (the highest on main and in every worktree at
  this lane's start was S1856; taken from well above it, since another lane
  and the kit are allocating).
- abi: current + 1 at landing (grep at the time; another lane may bump first).

## Premise test (base 80341284e, before any code edit)

Reproduced on `build/pcrec` at the base: utf8 `req_whole_run` lengths
`(?i)abcdÀefgh` 6, `(?i)αβγ` 0, `(?i)Ελληνικά` 0, `(?i)привет мир` 0,
`(?i)naïve café` 8; `--engine=vm -fno-cls-kit` islands `x(?:[éà]1|q2|r3)y` 1,
`x(?:1[éè]|q2|r3)y` 0, `x(?:1[éà]|q2|r3)y` 1, `x(?:[éà]|q2|r3)y` 1,
`a[éÉ]b` 1, `(?i)aéb` 1, `(?i)xé+y` 2 (rungs `0x4u`, 3319 B). All as §5 states.

## Stage 1 — the lowering's merge, the island's set reading

### What was built

- `src/opt/altnf.c` (new): the alternation owner `pcrec_altnf`, rule M only
  (§3.3): branches described as A_CAT spines of A_CLASS positions; grouped by
  the all-but-`p` key (`anf_in_key`, one statement read by the hash and the
  equality test); adjacency rows 1-3 of §3.2 (row 1 some position disjoint,
  row 2 same width and no writes, row 3 otherwise refuse), the reach test
  over the span between partners with a prefix-count fast path; declared
  order (widths ascending, positions last-first, sweeps to a fixpoint);
  duplicates of an earlier mergeable branch dropped without a reach test.
  `PcrecAnfRules {merge, prefix, suffix}` in `internal.h` (a struct, not
  `#define` bits: limits_check scans numeric defines).
- `src/opt/lower_enc.c`: `LowerOps.split` (`split_byte`, `split_utf8`) and the
  exported `pcrec_lower_boxes` (the canonical unmerged split, the island's
  admission source); `lower_class_utf8` hands its boxes to the owner unless
  bit 10 denies; the `A_CAT(A_EMPTY, alt)` seal is deleted (K123's peel makes
  it dead; the A_WCLASS wrapper stays load-bearing).
- `src/gen/emit_vm.c` `vm_isl_words`: the A_WCLASS arm reads the class's SET
  (`pcrec_wcls_set` -> `pcrec_lower_boxes`), admitted iff every box of the
  canonical split is a single string (today's admission, kept as a
  predicate); the A_ALT and A_CAT spine walks step `t->l` (island-local),
  so a head-position class reaches the set arm. `vm_isl_subtree_nodes`
  (the chain-size walk) unchanged.
- Bit 10 `-fno-altcls-merge` re-specified to deny the owner's merge at both
  callers; `RX_ALTCLS_MERGES` does not count the lowering's merges (spec
  hunks: `docs/spec/tuning.md` §2.6¶1-2, §2.20¶2; `docs/spec/match_api.md`
  §6.3.11¶3; `lib/pcrec.h` bit-10 comment; `--list-axes` row text, a declared
  dump-row delta for B0).
- abi 95 -> 96 (provisional, the next number at landing; renumber if
  vlookbehind bumps first). Readers found by `grep -rn '\b95\b'` over the
  tree's abi sites: `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
  `tests/codegen/run_codegen_tests.sh` ABI_EXPECT and its transition
  message; `tests/mech/sabotages/S693_abi_not_bumped.sh` SAB_BEFORE;
  `docs/spec/match_api.md` lines 212 (#error example), 1646 (table), 1804
  (§6¶17); `docs/dev/history/abi_changelog.md` new top entry. Identity gate
  (B) FILEPIN self-pinned to `e3df76804` (`run_recursion_identity.sh`, with
  its SELF-PIN line); the manager re-pins to the landing merge.
- `tests/codegen/run_cpset_structure.sh` [2b]: the owner's four interval
  readers (`anf_cls_hash/eq/disjoint/union`) added FUNCTION-scoped to
  `ALLOW_FN` with their rationale. This gate went red on the correct build
  (the owner is a new reader of `u.cls`); the design did not name it. Not a
  STOP in my reading: it is a population check whose documented process is
  "add the reader with its reason on first contact" (every ALLOW_FN entry
  arrived that way), not an answer or identity gate. Flagged for the code
  round.
- `tests/axes/run_axes.sh`: the `-fno-cls-kit` REFUSAL_PATTERN entry and its
  K35 floor (60) are RETIRED: the merge keeps every wide class of the corpus
  under the VM cap, so the floor became unreachable on a correct build (the
  K55 precedent). `docs/spec/tuning.md` §2.33¶7 gains the sentence saying
  why. A second gate the design did not name.
- `tests/utf8/altnf_lowering.rxt` (new): the stage's answer witnesses, every
  cell read from libpcre2 10.46 (`altbuild_evidence/altnf_lowering_oracle.out`,
  all OK): `(?i)β`, `(?i)k` (default and VM), `x(?:1[éà]|q2|r3)y` (VM), K123's
  `(?<=[a\x{3b1}])x`, `(?i)abcdÀefgh`, `(?i)Ελληνικά`, `\p{Nd}+` (VM).
- `tests/codegen/run_wclass_census.sh` PART 4: island counts N1-N3 (the S-i
  head witness `x(?:[éà]1|q2|r3)y` reads 1), the merge's own N4 (`a[éÉ]b`
  merged 0, bit 10 1), and box counts N5 (`\p{Lu}` 67, `\p{Nd}` 39,
  `\p{L}` 330, `.` 8).

### Gates the design did not name (both CONFIRMED by the manager)

1. `run_cpset_structure.sh` [2b]: function-scoped ALLOW_FN entries for the
   owner's interval readers.
2. `run_axes.sh`: the `-fno-cls-kit` refusal floor retired.

### R1/R2 — the unpredicted island mover (a STOP, then ruled)

The cell: `x(?:[éà]|q2|r3)y` under `--engine=vm`, `RX_VM_ALT_ISLANDS` 1 -> 0.
Cause: the island's word list is unchanged (the set reading keeps today's
admission), but `vm_isl_subtree_nodes` counts the child the CHAIN emits, the
merged child is smaller, and the size row `isl_bytes > chain_bytes *
VM_ISL_SIZE_FACTOR` (`emit_vm.c`) then prefers the chain. The design's
"U4 is an equality" was wrong inside an enclosing alternation: corrected by a
tagged ERRATUM after §5 stage 1's FIX-7 paragraph. Answers do not move (match
counts equal across merged/denied and equal python `re` on the subject;
libpcre2 agrees on the rxt cells).

R1 asked for the speed of each flip. `perf stat -e instructions:u`, taskset -c 7,
10 reps of a ~1 MB generated subject (seed 7), merged vs bit-10 deny
(`altbuild_evidence/r1_knee_perf.{sh,out}`, driver `r1_knee_perf_drv.c`):

| cell | merged | denied (bit 10) | ratio |
|---|---|---|---|
| knee `x(?:[éà]\|q2\|r3)y`, `-fno-cls-kit` | 299.9M (island 0) | 161.5M (island 1) | 1.86x slower |
| knee, kit on | 325.5M (island 0) | 161.5M (island 1) | 2.0x slower |
| `a[éÉ]b` (bare) | 50.2M | 64.3M | 0.78 (win) |
| `(?i)aéb` (bare) | 89.7M | 98.5M | 0.91 (win) |
| `(?i)xé+y` (bare, rungs 0x4u -> 0x1u) | 143.3M | 233.7M | 0.61 (win) |

R1's condition ("a clear loss: stop and report") was MET at the knee cell; the
lane stopped stage 1 and reported. R2 ruled (b): accept it as a listed D186
cell with no new decision row (no corpus or bench pattern is in the family,
the default route takes the DFA, bit 10 restores it); the loss is the size
row's pre-existing weakness (it prices by size, not work), filed by the
manager as a plan row with this cell as its witness and I-176 as its trigger.

### U4 — island and rung census

`altbuild_evidence/u4_census.py`: 936 utf8 patterns (860 corpus blocks, 76
bench/utf8) x 4 axes (`--engine=vm`/auto x kit on/off) = 3744 cells, base
`80341284e` vs stage. First run (`u4_stage1.log`, `u4_movers_stage1.tsv`): 211
cells refused on both; 91 movers, 60 island/rung movers all bare-class and all
restored by bit 10 (U1's predicted bare-class family: `(?i)é`, `(?i)αβγ`,
`(?i)москва`, `(?i)(\xe9+)\1`...), 31 REFUSAL-MOVED, every one a BASE refusal
the merge retires (`\p{L}+`, `\P{L}+` under `-fno-cls-kit`: refused at the
base, compiled at the stage, refused again under bit 10). The census now
classes those `refusal-retired-by-merge` (only FEWER refusals are expected,
FIX-3), and holds a refusal floor (over a fifth refused fails: its first
draft wrote `-o /dev/stdout`, which writes a `.h`, and "passed" with every
cell refused). No knee-family (`alt`) mover is in the corpus or the bench.
The rerun with the final classification is in the OWED list below.

### Sabotage (stage 1)

| row | plant | verdict |
|---|---|---|
| S1880 | `anf_in_key` keys position `p` too (`return i != p;` inverted) | DETECTED |
| S1881 | box width dropped (`b->w = w;`) | DETECTED |
| S1882 | the island's set arm reads one box only | DETECTED |
| S1883 | the set arm splits per member (unmerged per code point) | DETECTED |
| S1884 | the A_ALT spine walk reverted to `pcrec_ast_seethru(t->l)` | DETECTED |
| S1885 | the A_CAT spine walk reverted (count and fill loops both) | DETECTED |

`altbuild_evidence/mech_stage1.log` (11 rows incl. the re-anchored S366, S303,
S-U8: S1885 UNDETECTED there, its plant reverted one of two loops and left
them mismatched; rewritten as the exact two-loop revert),
`mech_stage1_s1884_s1885.log` (both DETECTED). S366, S303 and S-U8 re-anchored
on the new code.

## Stage 2p — the piece set (facts only, inert)

### What was built

- `src/facts/desc.c` / `desc.h` (new): the fixed-width PIECE DESCRIPTION
  (§3.4-§3.5), FIX-4's combinator interface: `pcrec_pd_unit/none/pos/cat/alt`
  over width groups of position sets, the alphabet a parameter (`PdAlpha`:
  join, same). CAT = product with same-total-width hull merge; ALT = union;
  each group stores its LAST <= 32 positions (`PCREC_MAX_REQ_RUN_SCAN`); over
  `PCREC_MAX_REQ_PIECES` groups the description drops (`PD_OVER`). The
  node-grain carve-out: it includes no `facts_derive.h`, reads no fact
  (`run_facts_checks.sh` CARVE list; `src/facts/CLAUDE.md` rule).
- `src/facts/req.c`: the req walk builds the description in the SAME walk
  as the set and the runs (`RbVal.desc`); class positions via
  `rb_pos_set` (singleton cache); walls (gap, repeat, assertion, A_EMPTY,
  lookaround, backref, call) set none.
- Fact `req_pieces` (`facts.def`, epoch 2, core, denied with
  `req_byte`/`req_run`), INERT: nothing reads it but `--emit-facts`. Declines
  `decline:one-group`, `decline:not-fixed-width`, `decline:over-bound`.
- Limit `PCREC_MAX_REQ_PIECES` = 10 (`limits.def`), MEASURED before the row
  landed (RDY-6a): `p2_census.py` over every corpus block and every bench
  pattern, census-only bound 4096: 6696 compiles, max 10 groups
  (bench altwide), ci-moskva 4 (`p2_census.out`; the census read each bench
  file's FIRST line, so the 8 multi-line bench patterns were counted by their
  first line only).
- Spec: `facts_listing.md` §4.1.2¶8c (spelling, the three declines, stored
  last 32, inert); `tuning.md` §2.27¶5 and §2.28¶8 Facts emptied gain
  `req_pieces`. `limits_check.sh` manifest 78 -> 79.
- `run_facts_checks.sh` [facts-pieces]: 7 witnesses at an independent model's
  value, the three declines among them.

### Gate (model)

`p2_model.py` (CaseFolding.txt + UTF-8, shares no code): 37 mixed-width fold
classes in `(?i)abcd<X>efgh` + bench/utf8: 95 agree, 0 differ, 16
UNPREDICTED (groups, properties, POSIX classes the model does not read), 2
pcrec refusals (`p2_model.out`).

### Sabotage (stage 2p)

| row | plant | verdict |
|---|---|---|
| S1886 (S-p) | CAT keeps only the shortest group | DETECTED (facts) |
| S1887 (S-L) | the run walk reads through a positive lookbehind | DETECTED (harness, `tests/lookaround/startpos.rxt` `ms 3 "abcx"`; the corpus's own `(?<=abc)x` is the design's `(?<=foo)bar` cell) |

`altbuild_evidence/mech_stage2p.log`. Every existing mech anchor in the files
2p edits still reaches (16 rows checked by SAB_BEFORE count).

### Instrument additions (scripts/emit_sweep.py)

The B0 judge could not take a NEW row: `--facts-declared-moves FACT:row:>new`
(a new fact, one row per encoding, none in REF), `--dumps-declared-new
FLAG:KEY` (`--dumps-declared-gone` mirrored), `--facts-encodings LIST` (B0
part 3's byte half; default unchanged). Each unit-checked both ways (judged
clean on the true delta, red on a missing row and on an undeclared move).


## Stage 2b — the owner (rule M on the adjacency test, P, S, the re-run)

### What was built

- `src/opt/altnf.c` rewritten as THE PROCEDURE (§3.3): per round M to its
  fixpoint, then P, then S; another round if P or S changed the list; P's
  rests and S's heads get the whole procedure again (`anf_sublist`, depth
  `PCREC_MAX_ALTCLS_FACTOR_DEPTH`). M's adjacency test is §3.2's three rows
  over the moved branch only (row 1 a disjoint head position; row 2 same
  width, bounded, no WRITES; row 3 refuse); A_EMPTY is a mergeable width-0
  branch (duplicates drop). P keys on the longest run of equal leading CLASS
  elements; S on the longest node-identical suffix (`anf_node_same`: CLASS,
  EMPTY, CTX, REP, CAT/ALT; every other kind is "not the same").
- The adjacency head (FIX-4 carve-out): `PdHead` plus `pcrec_ph_unit/pos/
  wall/cat/alt` in `src/facts/desc.{h,c}`; the walk is the caller's
  (`anf_head`), the module combines. A repeat contributes no head (FIX-1);
  a callout that consumes is a writing wall; lookarounds are units carrying
  their body's writes.
- Work bound `PCREC_MAX_ALTNF_WORK` = 1,000,000 units (adjacency calls plus
  interval comparisons), MEASURED (`altbuild_evidence/p2b_work.out`): owner
  peak 831,549 (bench altwide s-4096), corpus far below; lowering peak 750.
  Worst case on random 3-8 letter lists (§5 SIM-5): n=200 2,783; 400 8,479;
  800 31,805; 1600 185,279; 3200 935,681; 6400 4.56M units (0.22 s whole
  compile). Past the bound the rest of that alternation stays as written.
  limits_check manifest 79 -> 80.
  NOTE: s-4096's whole compile is 10.6 s at the stage against 6.7 s at the
  base; perf puts 77% in `make_state` (DFA construction over the rewritten
  tree), not in the owner. That compile is refused for size either way
  (1.6 MB of C).
- altcls is a caller: the walk plus `pcrec_altnf` with {merge: !bit 10,
  prefix/suffix: !bit 11}; its old stage-1/stage-2 code is deleted. Stamps
  redefined (match_api §6.3.11¶3): MERGES = lists M folded in, FACTORED = P
  plus S factorings. Callout counts may move (§11.6¶1 gains the give-up
  sentence, example `(?:ab|(?C1)x|ad)`).
- Spec: tuning §2.6¶1, §2.7¶1/¶2; match_api §6.3.11¶3, §11.6¶1; lib/pcrec.h
  bits 10/11 comment; `--list-axes` rows `altcls-merge@1`/`altcls-factor@1`
  (declared dump moves for the 2b sweep); `--list-limits` new row.
- abi: no second bump; 96 (stage 1) covers the landing.

### Witnesses (libpcre2 10.46)

- `tests/altcls/altnf_rules.rxt` (new, generated by
  `altbuild_evidence/altnf_rules_gen.py`): 24 blocks, 78 cases, all pass,
  including `(?:ab|a\Kd|ad)` on `ad` = (1,2), `(?:ab|a|ad)` = (0,1),
  `(?:ab|(a)d|ad)\1?`, `(?:ab|a(?:x)?|ad)`, `(?:a|ab)c|(?:a|ab)b`.
- Random differential (`p2b_fuzz_gen.py`, seed 2026): 400 patterns x 90
  subjects = 36,000 cases; 36,000 OK on the stage and 36,000 OK under
  `-fno-altcls-merge -fno-altcls-factor` (spans and every capture). Reach:
  285 of the 400 stamp FACTORED >= 1, 85 MERGES >= 1.
- Callout counts: `(?:ab|(?C1)x|ad)` 1 (pcre2) vs 0;
  `(?:(?:a|a)(?C1)b|(?:a|a)c)` 2 vs 1. Both inside §11.6¶1 (spans agree).
- Stamps (measured): `x(?:a|b|cd|e|f)y` M1/F0; `(?:ab\b|ad\b)` M1/F2 (the
  design's "2 by hand"); `(?:abx|aby|abz)q` M1/F0 (as predicted);
  `(?:xing|ying)` M1/F0; `(?:xyr|zr)` M0/F1; `frank|fred` F1;
  `(?:ab|a\Kd|ad)` F2.

### Movers (`altbuild_evidence/p2b_movers.out` / `.tsv`)

REF = stage 1+2p `24095dfc5` (B0 already accounts for 1+2p against the
base). Population 6,720 (every corpus block at its encoding, every bench
pattern), default and VM routes. 117 patterns move, all in observable classes
§5 2b predicts (stamps, VM program bytes, the island census, rungs, DFA
tables):

| route | observable | down | up |
|---|---|---|---|
| auto | FACTORED | 13 | 83 |
| auto | MERGES | 2 | 59 |
| auto | islands | 3 | 0 |
| auto | artifact size | 36 | 13 |
| vm | FACTORED | 13 | 82 |
| vm | MERGES | 2 | 58 |
| vm | islands | 13 | 23 |
| vm | artifact size | 81 | 20 |

VM program bytes changed on 22 (auto) / 100 (vm) and rungs on 2 / 3. Four
refusals RETIRED (the REF refused for emitted code size; the stage
compiles): VM `altwide/clsa-1024`, VM `altwide/clsd-1024`, both routes of
`capability/wild-datetime-datefinder-alternation`. The DENIED pair (both
bits) is identical to the REF on all 6,720. (Against the plain base
`80341284e` plus abi, the denied pair differs on 3 utf8 caseless cells: that
is stage 2p's req walk reading the stage-1 lowering's alternation under
bit 10, identical at `24095dfc5`; not a 2b mover.) Answer identity over the
corpus (`run_altdiff.sh --corpus`) is OWED.

### Readers re-read

- `run_altcls_tests.sh`: count3 `b|ab|c` now 1 (row 1: `b` vs `a` are
  disjoint), new count4 expects 0, barrier3 1, verdict-free pattern
  `frank|zrex|bray`; new re-run and suffix count checks (S1892/S1893's
  targets). 18 passed, 0 failed.
- `scripts/alt_census.py`: the merge paragraph points at the owner;
  `ab|cd|a|b` re-measured (0 islands by default, 1 under bit 10).
- DD-14 fixture `((?:a|b))(?1)`: MERGES 1, holds.
- S66 re-anchored to the owner's fold line (validates).
- `run_island_tests.sh`: see STATE AT HANDOFF. Two witnesses re-picked (the
  factoring precondition now `frank|fred|frost|brad|bobby|bill`, F2, one
  island; the budget witness compiled with both bits denied). One cell RED.
- Not yet re-read: run_axes, run_form_census, run_specimen_identity,
  run_registry_tests.sh:447-456, emit_vm.c:572, S67.

### Sabotage (stage 2b): VALIDATE_ONLY clean; the mech run is OWED

| row | plant | witness |
|---|---|---|
| S1888 (S-d) | row 2 passes a mergeable branch of any width | altnf_rules.rxt `(?:ab\|a\|ad)` |
| S1889 (S-k) | P keys on any identical leading node | `(?:a\|ab)c\|(?:a\|ab)b` on abc |
| S1890 (S-w) | row 2 ignores WRITES | `(?:ab\|a\Kd\|ad)` |
| S1891 (S-h) | an optional repeat gives its body head | `(?:ab\|a(?:x)?\|ad)` |
| S1892 (S-m) | created lists not re-run | count `(?:ab\b\|ad\b)` MERGES 1 |
| S1893 (S-s) | rule S never runs | count `(?:xyr\|zr)` FACTORED 1 |

## STATE AT HANDOFF

STOPPED in stage 2b under the STOP RULE. All 2b code, spec, tests and
evidence are committed (WIP commit); `make strict` is clean. Every quick
suite run passes EXCEPT one cell:

**`tests/island/run_island_tests.sh`, the cap-guard ladder's non-vacuity
cell.** The ladder (`(?:abc|abcq|abcqr|abcqrs|...)Z`, N=340) must emit a
chain within (425,000, 500,000) code bytes under `-fno-alt-island`. The
owner merges and factors it to 31,162 (the stage 1+2p build: 459,273). The
design names the island census as a mover, but not this witness.
Re-scaling is not a plain N change:

1. A distance-2 word set (no one-position merges) still shrinks 3x (N=340:
   176,906 against 484,072 at 1+2p), so N would grow about 3x.
2. Compiling the ladder with both bits denied exposes a PRE-EXISTING defect.
   At the base `80341284e` with `-fno-altcls-factor`, rungs N=300 and N=340
   are REFUSED with the island and ACCEPTED under `-fno-alt-island`. That is
   the acceptance regression the cap guard exists to prevent; it is latent
   today because altcls's old prefix factoring always ran under the default
   flags. Candidate known_issues row (not filed by this lane).

Ruling needed: re-scale the witness (to what), and what to do about (2).

Not started: the U4 rerun, U1 for bench/utf8, the `ofs_test_of` re-probe,
the remaining readers above, the vlookbehind merge (not announced in
`altbuild_rulings.md` at this handoff), and the code critic round.

OWED heavy runs (launched detached at the end, logs under
`$PCREC_TMPDIR/scratch/altbuild/logs/`): mech S1888-S1893
(`owed_mech2b.log`), `run_altdiff.sh --corpus` (`owed_altdiff.log`),
test-codegen + registry + rxtsource (`owed_suites.log`).

lanecheck: there is no `altbuild_deliver.txt`, so lanecheck does not apply.

## Lane altbuild2, 2026-11-06 — K139, the R4 items, item 3

The predecessor's text above is unchanged. Rulings read through R4; no
"LOOKBEHIND LANDED" line was in `altbuild_rulings.md` at any boundary, so the
vlookbehind merge (item 4) did NOT happen; lane/altbuild is still based on
its own base.

### Commits

| commit | what |
|---|---|
| `3b5a231c6` | K139 probe evidence (`altbuild_evidence/k139_*`); the ruled local guard fix regressed a dense family, reverted, STOP (led to R4) |
| `06db77410` | readers re-read (stale altcls comments name the owner); U4 post-2b and ofs re-probe instruments |
| `cfd28cf38` | **K139 FIXED**: the `drop-islands` row (R4) |
| `82ef1d9c3` | R4 (a): size-term pool member re-picked; island manifest re-pinned |
| `78caf76cb` | R4 (b): trie identity controls deny the owner on both sides |
| (this commit) | this section; `altbuild_evidence/u1_bench.py` |

### K139: one declared row in the size-cap retry table (R4)

- `fit_rungs[]` (`src/core/compile.c`) gains `drop-islands`, placed after
  `drop-landmark-walk` and before `drop-anchored`. In VM order it comes after
  `unroll-rescue`/`prefilter-collapse` and before `drop-handoff`/`drop-prefilter`.
  - Applies when the refused attempt's VM program emitted an island. The new
    `Job.vm_islands` field is written beside the `VM_ALT_ISLANDS` stamp.
  - Sets `flags_or = PCREC_NO_ALT_ISLAND`, `restart = true` (the size term
    re-runs, so `COMPILE_MAX_ATTEMPTS` gets a fifth ladder run and one more
    retry).
  - Degrading, FOF_IN, its own `size-cap-retry` cells, its own stderr note.
  - Sequence pairs added after `drop-end-mark`/`collapse`/`sel1-collapse`/`sel1-drop`
    and before `drop-handoff`/`drop-prefilter`. The trace build's
    self-check and the sequence check stay clean on every witness.
- The in-emitter guard is UNCHANGED. It is a speed shortcut and a deletion
  candidate under [ISL-PRICE].
- No emitted byte moves for a pattern that compiled before: the row is only
  reached from a refusal. So there is no abi event.
- Spec:
  - `limits.md` §8.4: table row 2b, ¶2 (VM rows), new ¶2c, ¶3 "all ten".
  - `limits.md` §8.5: new ¶1b (the stamp), ¶5 and ¶6 (2b listed).
  - `tuning.md` §2.20: ¶2's size row (the cap guard stated, plus the retry) and ¶6.
  - Also updated: `dec_fallback.md` sequence table, `row_reach.py` SIZE, and
    K139 in `known_issues.md`, marked FIXED. That entry exists only on main,
    so the merge will conflict there; keep the FIXED text.
- Witnesses, all ACCEPTED on the row build (each was refused before):

  | witness | flags | result |
  |---|---|---|
  | ladder N=300 | owner deny pair | DROPPED islands, ships the chain |
  | ladder N=340 | owner deny pair | DROPPED islands, ships the chain |
  | rand-1000 eight-letter words | default flags, `--engine=vm` | retried |
  | six concatenated 200-word alternations | default, `--engine=vm` | retried |
  | six concatenated 200-word alternations | default, auto route | VM, `RX_ENGINE_SEL "size-cap-retry"` |
  | dense 1,600 / 1,800 / 2,000 words | owner deny pair | KEEP their island (361,656 / 404,567 / 447,307 code bytes) |

  - `--size-cap=refuse` on rand-1000 refuses with the caller's own 518,578 B
    figure.
  - The retry artifact is byte-identical to the direct `-fno-alt-island`
    artifact on all four retry witnesses.
- Retry compile cost, median of 5 runs, against the direct `-fno-alt-island`
  compile:

  | witness | retry | direct `-fno-alt-island` |
  |---|---|---|
  | ladder 300 | 55.7 ms | 35.5 ms |
  | ladder 340 | 64.6 ms | 37.6 ms |
  | rand-1000 | 65.2 ms | 36.0 ms |
  | six alternations | 111.9 ms | 56.7 ms |

  So the retry costs about 1.6x to 2x one compile.
- Tests:
  - `run_fallback_table.sh`, witness `W_ISLSIZE` (24 random words,
    trlowsize, `--engine=vm`): `seq-isldrop` (`drop-islands@size`),
    `seq-islref` (refused under `--size-cap=refuse`), `seq-islnone`
    (`-fno-alt-island` arrives nowhere), and `note-isl` (the hand-written
    note). The existing trlowsize/trlowboth witnesses were re-run on a
    scratch trlowsize trace build: every sequence is unchanged.
  - `run_island_tests.sh` section 11: see item 1.
- Sabotage S1894 (row inert, `fallbacktable` arm): DETECTED on a scratch
  trlowsize plant. `seq-isldrop` reads `refuse@size` and the compile is
  refused. The mech run is in job 303.
- The row-deleted plant was also built at the shipped caps
  (`a2/pcrec_plant`). Section 11 goes RED on the ladder (N=340) and on the
  rand-1000 retry cell. The dense cell stays green, as it should: it guards
  the opposite direction.

### Item 1: the cap-guard witness (R4)

`run_island_tests.sh` section 11, rewritten:

1. The ladder N=260/300/340 runs under the owner deny pair (the default
   shrinks it to about 31 KB).
   - No rung may be refused with the island and accepted without it.
   - A rung that stamps no island must equal its `-fno-alt-island` artifact.
   - N=260's islands now fit, so they are kept.
2. The non-vacuity cell is now "the retry row FIRES" at the default flags,
   on rand-1000 under `--engine=vm`:
   - the compile succeeds;
   - the drop note is printed, one note per fired row, which is the count;
   - the artifact stamps `RX_VM_ALT_ISLANDS 0`;
   - the artifact is byte-identical to `-fno-alt-island`'s.
3. A new dense cell checks that the islands which fit are kept (1,600/1,800/2,000
   words, deny pair).

Results: green on the row build (3/3), red on the row-deleted plant (2 of 3).

### R4 (a): the size-term pool

- Cause: rule M merges `(?:ab|ba|aa|bb){24}c`. It stamped `UNROLL_K_WHY
  "default"` and no island, a prediction/stamp mismatch. This was the
  predecessor's `owed_suites.log` test-codegen red, `run_size_term.sh` FAIL 1.
- New member `(?:ab|cd|aqr|cst){8}z`, added to `counterk.rxt` with python3
  `re` expectations (harness 10/10). Measured:
  - MERGES 0 and FACTORED 0;
  - ratio 0.7158, `size-model`, 1 island.
- Whole pool re-measured on a scratch threshold-1000 reference:
  - 0 mismatches;
  - 9 members in band;
  - 3 below-bar shapes, 4 or more above-bar shapes;
  - 2 islanded members.
- Corpus pin moved: `run_recursion_identity.sh` `ISLAND_PATTERNS`. The old
  pattern stamps 0 islands under `--engine=vm`; the new one stamps 8.
- The old pattern stays in the corpus as an answer witness.

### R4 (b): the trie identity controls

- Before: the controls read factored/factored (4 and 8 branches) and
  compiled/compiled (256 branches). This was `owed_suites.log`'s other red.
  Rule P factors the `[aA]`-class prefix that the [OPT-ALTCLS] precedent
  relied on altcls declining.
- Fix: both sides of `check_control` pass the deny pair, with a comment
  citing the precedent.
- Measured against a scratch `-DPCREC_NO_TRIE` build: all three controls
  read factored/unfactored again.

### Item 3

- **U4 after 2b, corpus part** (`a2/u4b/u4.log`, `u4_movers.tsv`; instrument
  `altbuild_evidence/u4_census_2b.py`; the restore control is the deny pair):
  - 862 patterns x 4 axes = 3,448 cells; 196 refused on both sides.
  - 91 movers:
    - 55 bare-class island/rung losses, restored by the pair;
    - 7 alt-family island losses, restored by the pair:
      - `(?:éx|ʩx)` in `litscan/handoff.rxt`;
      - 2b's own `altnf_rules.rxt` cells;
    - 29 base refusals retired by the owner.
  - 0 findings. PASS.
  - Run against the pre-K139 build.
- **U4 bench part:** the first run pointed at `bench/utf8` instead of
  `bench/utf8/patterns`. It is OWED as job 300.
- **U1 for bench/utf8:** instrument `altbuild_evidence/u1_bench.py`
  (base96 vs s12p, a construct predicate with a bracket scanner). OWED as
  job 301.
- **ofs_test_of PREM-6 re-probe** (`a2/ofs_reprobe.log`, `ofs_reprobe.py`):
  - 7,338 patterns x 2 flag sets = 14,676 compiles; 1,304 refused, 0 timeouts.
  - The run-term was reached on 87 default compiles and 218 ofs compiles.
  - Masked positions inside the pinned run: **0**. It remains unreached, as
    §4.2 noted.
- **Readers re-read:**
  - `run_axes`: the `-fno-altcls-merge` refusal entry is still reached.
  - `run_form_census`: no ALTCLS floors. The `RX_VM_CLS_FOLDS` floors are
    unverified; they are in test-axes, OWED.
  - `run_registry_tests.sh:447-456`: the text is still true.
  - S67: VALIDATE_ONLY valid.
  - `emit_vm.c` Vm.isl_over_cap comment: updated.
  - `run_specimen_identity`: 9 FAIL / 6 pass. The failure is identical on
    base `80341284e`, s12p, the stage and main's build: pre-existing, opt-in,
    not this lane's.
  - `run_resource_tests.sh:1405`: says "all five" degrading rungs, which
    was already stale. It has no 2b witness; `seq-islref` covers the switch
    instead.
  - `row_reach.py`: no corpus pattern reaches `drop-islands@size`. The reach
    gate may want a declared zero; see the reach run.
- **Predecessor's OWED runs, read:**
  - mech S1888-S1893: 6/6 DETECTED, 0 unexpected (`logs/owed_mech2b.log`).
  - `run_altdiff.sh --corpus`: 153/153 agree, 110,729 cells.
  - `owed_suites.log`: test-codegen was red on exactly (a) and (b); both
    are now fixed. Registry and rxtsource did not run (no `-k`); that is
    job 302.

### Acceptance table (MEASURED vs predicted, every mover class)

| stage | mover class | predicted | measured |
|---|---|---|---|
| 1 | utf8 fold runs/tables, multi-box classes | §5 stage 1 list | corpus: stage 1 section; bench/utf8 U1: OWED (job 301) |
| 1 | bare-class island/rung losses, restored by bit 10 | yes (RDY-1/RDY-3) | 60 at stage 1; 55 after 2b (pair) |
| 1 | knee `x(?:[éà]\|q2\|r3)y` island loss | NO (R1/R2 STOP, ruled D186 cell) | no corpus or bench member at stage 1 |
| 1 | refusals retired | fewer only (FIX-3) | 31 at stage 1, 29 after 2b, 0 new refusals |
| 2b | ALTCLS stamps, VM program bytes, DFA tables, island census, rungs | yes (§5 2b) | 117 patterns, every one in these classes (`p2b_movers`); alt-family island losses 7 cells (U4), restored by the pair |
| 2b | refusals retired | not named | 4 (`altwide/clsa-1024`, `clsd-1024`, `wild-datetime` both routes) |
| 2b | cap-guard ladder witness | NO | STOP; ruled R4; K139 row + item 1 |
| 2b | size-term pool, trie controls | NO | ruled R4 (a)/(b) |
| K139 | refusals retired by `drop-islands` | (R4) | the four witnesses; no corpus pattern reaches it |
| all | answers | none | altdiff 153/153; witnesses vs libpcre2 10.46; harness green on touched blocks |

### Gates the design did not name (for the code round)

1. `run_cpset_structure.sh` ALLOW_FN (stage 1, confirmed).
2. `run_axes.sh` `-fno-cls-kit` refusal floor retired (stage 1, confirmed).
3. **K139 row** `drop-islands` (R4).
4. **Item 1 witness**: section 11 rewritten (deny-pair ladder, the retry
   fires, dense keeps its island).
5. **(a)** `run_size_term.sh` pool member + `ISLAND_PATTERNS`.
6. **(b)** `run_trie_identity.sh` controls under the deny pair.

### OWED (detached box-queue jobs; read with `scripts/boxqueue state KEY`)

All four jobs are queued behind lane vlbbuild's long chain. None had run
when this lane ended.

| job | runs | log |
|---|---|---|
| `300-altbuild2-u4bench` | U4 with the bench/utf8 population, on the CURRENT build (K139 row included; rescues by the row would show as refusal movers) | `a2/u4c/` |
| `301-altbuild2-u1bench` | U1 for bench/utf8 | `a2/u1b/u1_bench.tsv` |
| `302-altbuild2-regrx` | `make -k test-registry test-rxtsource` | (job log) |
| `303-altbuild2-k139` | `make -k test-fallback-table test-island test-codegen test-recursion-identity-locked`, then mech S1894 | `a2/logs303/` |

Still owed with no job: `make test`, test-axes (form census floors) and
the reach run for the new row. The vlookbehind merge waits for the
manager's "LOOKBEHIND LANDED" line.

(`a2/` = `$PCREC_TMPDIR/scratch/altbuild/a2/`; `logs/` =
`$PCREC_TMPDIR/scratch/altbuild/logs/`.)

## Lane altfix (2026-11-06, opus): the three red owed jobs, then review r5 altcode's ruled fixes

Brief: triage 301-303, apply every FIX-NOW and DOC id of
`docs/dev/reviews/2026-11-06-r5-altcode.md` (RULING block; rulings R5/R6),
validate through the queue. Commits on `lane/altbuild` over `4cc816446`:
`d8119f007` (EMIT-1/2/3, SLOT-2/3/4, CHK-5/8, spec), `ce68bcf5d` (the
triage fixes, the remaining ids, the island arm), `8cbf0db6c` (recursion
identity self-pin). Not merged with main (the brief: a later lane does).
Scratch: `$PCREC_TMPDIR/scratch/altfix/` (`t/` witnesses, `tip/` the
frozen tip binary, `jobs/`, `out/`).

### Triage of the three red jobs

| job | verdict | cause | fix |
|---|---|---|---|
| 301-altbuild2-u1bench (rc 1, 2 s) | NOT an invocation error: the gate ran (76 patterns) and reported 8 findings, every one the INSTRUMENT's | `u1_bench.py`'s predicate missed two multi-box constructs: caseless ASCII `k`/`s` (fold orbits leave ASCII: KELVIN SIGN, LONG S; `ci-kelvin`, `ci-long-s`, `ci-class-range` through `[a-z]`) and an alternation of single non-ASCII characters (`alt-mixed-width`, folded by altcls into a wide class); its direction rule allowed islands only `1 -> 0` (`ci-greek-run` 3 -> 0, `ci-moskva` 6 -> 1 are legitimate falls); a route whose refusal RETIRED (`prp-l`, `prp-notl` on the VM) read every other observable `- -> value` as a finding | predicate widened (both constructs), any fall allowed, a refusal-moved route's other observables skipped, and EMIT-1's island RISES listed in their own class (not findings); STAGE is now the branch tip. Re-run: job `altfix-u1bench` |
| 302-altbuild2-regrx (rc 2) | REAL red, a missing re-pin (registry green) | test-rxtsource's census: the branch added `tests/altcls/altnf_rules.rxt`, `tests/utf8/altnf_lowering.rxt` and edited `counterk.rxt` (+2 files, +35 blocks, +121 case lines; pcre2-only +111, PASS +10) and never re-pinned | CENSUS_* 314/6339/75851, RUNSH_* 290/6339/75851, C3_PASS 22660, C3_SKIP 53098, C3_SKIP_PCRE2ONLY 20245, C3_VERIFIABLE 25056 (the entry-file and W23-S7 counts derive from CENSUS_FILES). Re-run: batch C `r302` |
| 303-altbuild2-k139 (rc 1, 1539 s) | REAL red, four causes | (a) test-fallback-table: stage 1 shrank `(\p{Xwd})`'s tables to 933,498 B, so every hybrid-drop witness built on `(\p{Xwd})`/`(\p{Xwd})x` fits with NO rung (11 cells, the ENGINE_SEL floor, both PFWHY shapes, two notes); note-premul's `[^\p{C}\p{M}\p{P}]` now fits after the anchored drop. (b) test-codegen SABANCHOR: CHK-8 (S238). (c) recursion identity (A) and (B): the branch moves call-free regions on purpose. (d) mech S1894 was DETECTED (green) | (a) re-aimed to `(\p{Xwd}|\p{Nd}x|\p{Sc}y)` (hybrid 1,058,204 B, prefilter drop) and its `x` form (handoff then prefilter, 1,060,847 B), each ~6% over the cap; note-premul to `[^\p{C}\p{M}\p{P}]\p{L}` (anchored then premul). The same shrink had silently emptied OTHER suites' witnesses, re-aimed in the same commit: `tests/prefilter` T2 size-dropped pair, `tests/uprops` §5 (the new witness has the same member set over that sweep's subject; argued in the script), S420 (now detected through tests/resource's `(\p{Xwd})\b`, 1,087,026 B; its harness target dropped), S1708-S1714's REACH. (b) SAB_COUNT 6. (c) FILEPIN and ABASEPIN self-pinned to `ce68bcf5d`; the landing re-pins both to the merge (TRD-7). Re-run: batch C `r303` |

The u1 instrument fix is a check change: its predicate now covers the two
constructs, and nothing it reported as a finding was a pcrec defect (each
was checked against the construct it names).

### Review ids

| id | ruling | disposition (commit) |
|---|---|---|
| EMIT-1 | FIX-NOW (a) | `d8119f007`: the island's `A_CLASS` arm reads a byte class as its member words (ascending byte order), charged to the word budget; `vm_isl_single` and the multi-member decline gone; a wide class is read through `vm_isl_set_split` (its canonical split's boxes, each a byte class read member by member). Witnesses: island section 12 `[MEMB] m_w256` (bench altwide w-256 fixture `tests/island/altwide_w256.pattern`, 1 island where the fix's absence gives 20) and `m_twin` (`x(?:ea|fb|ga)y`); sabotage **S1990** (a one-member-only arm). |
| EMIT-2 | FIX-NOW | `d8119f007`: `drop-islands` is the last VM rung before `refuse` (`fit_rungs[]`, `fit_seq_legal[]` mirrored: handoff/prefilter may precede it, nothing but refuse follows). limits.md §8.4 row 6 (was 2b), ¶2c, ¶5/¶6 rung lists; K139; dec_fallback.md; tuning.md's rung references. Witness: fallback cells `seq-isl400` (400 words, `drop-prefilter@size` only, the island kept) and `seq-isl1000` (`drop-prefilter@size > drop-islands@size`, code 524,805 B over 500,000). |
| EMIT-3/TRD-1 | FIX-NOW | `d8119f007`, NOT impossible, no STOP. The size row's factor compares the island with the chain counted BEFORE rule M's folds: rule M records on the fold's union node the branches it stands for (`cls.branches`, `pcrec_cls_branches`, set in `anf_cls_fold` at both callers), and `vm_isl_subtree_nodes(.., unfold)` counts a folded class's concatenation as those branches. The cap guard and `est_chain` keep the emitted count. Witness: the verified family list, every member back at base96's island count and program bytes (table below); island section 12 `m_cat`, `m_utf8`, `m_utf8b`; sabotage **S1991** (the factor reading the folded chain). |
| CON-1 | FIX-NOW | `ce68bcf5d`: match_api.md §1¶7's guard block reads 96 in all three places. |
| TRD-2 | FIX-NOW (doc) | `ce68bcf5d`: the abi 96 changelog entry lists the 2b, K139 and fix movers. |
| CON-2, TRD-4 | DOC | `d8119f007`: limits.md ¶1b (the retry artifact is `-fno-alt-island` with the earlier rungs' drops applied, apart from ¶5's stamp and the figure ¶4's stamp quotes) and ¶2c + K139 (the refused-anyway compile cost, 3,000 words: 2.30x / 1.84x). |
| TRD-3 | FIX-NOW (spec) | `ce68bcf5d`: tuning.md §2.33¶7 says the refusal is the PAIR's limit, which single-axis test-axes does not see (re-verified: `\P{Unknown}` under `-fno-cls-kit` compiles, under the pair refuses at 556,358 B). |
| TRD-5 | DOC | `ce68bcf5d`: design §3.4 states the code's weaker reading (the description is DROPPED over `PCREC_MAX_REQ_PIECES`, not collapsed; inert today). |
| CHK-2 | FIX-NOW | `ce68bcf5d`: `dumps_declared_delta` reports a declared row the dump never listed (checked: an invented key beside a real one is now a problem). |
| CHK-5 | FIX-NOW (doc) | `d8119f007`: S66 header/DESC/FIGURE rewritten for rule M; S366 re-anchored with its figure dated; S693's DESC names no fixed number (and its AFTER is 95, the parent's). |
| CHK-8 | FIX-NOW | `d8119f007`: S238 SAB_COUNT 6. |
| SLOT-2 | FIX-NOW | `d8119f007`: `pcrec_spine_flatten`/`pcrec_spine_build` beside `pcrec_ast_node` (parse.c, internal.h); altcls's and altnf's private flatteners/builders deleted; lower_enc.c and the island's set split use the builder. |
| SLOT-3 | FIX-NOW | `d8119f007`: altcls.c's arm comments state today's invariant (altcls walks; the owner decides); cpset.c, emit_vm.c and `run_cpset_structure.sh` stop naming deleted callers. |
| SLOT-4 | FIX-NOW | `d8119f007`: `lower_class_utf8` calls the one `split_utf8`; `split_byte` deleted, the byte cell's split NULL and `pcrec_lower_boxes` fails on a NULL split. |
| SLOT-6 | FIX-NOW | `ce68bcf5d`: limits.def's `PCREC_MAX_REQ_RUN_SCAN` row names its second reader (altnf's head `max_pos`) and that reader's unit (character positions); a comment at the reader. |
| SLOT-7 | DOC | `ce68bcf5d`: design §2.3 and src/facts/CLAUDE.md say "co-location" (pd read by req.c, ph by altnf.c). |
| CHK-1, CHK-3, CHK-4, SLOT-5, CON-2 test entry, TRD-3 test entry, TRD-5 bound re-derivation | PLAN | for the landing to file; not built. |
| SLOT-8 | PLAN | member list onto [ISL-PRICE]; not built. |
| TRD-4 hopeless-case skip | PLAN, D77-held | not built. |
| CHK-6, CHK-7, TRD-6 | NOTED | none. |
| TRD-7 | NOTED (landing) | the landing re-pins FILEPIN and ABASEPIN (now self-pinned to `ce68bcf5d`) to its merge. |
| TRD-8 | REJECTED | none. |

Sabotage rows: new **S1990**, **S1991** (from the brief's S1990-S1999,
re-grepped on main, every worktree and every branch: free), detected by
a new mech arm `island` (`tests/island/run_island_tests.sh`; an island
moves no answer, so `harness` is green on it by construction). RETIRED:
S1883 (its admission predicate, single-string boxes, is gone: the widening
reads range boxes member by member; wclass census `[N1]` flipped to assert
the island), S1884 and S1885 (the island-local `t->l` step no longer
decides an island: the byte child enumerates the same words; SLOT-5 owns
unifying the step). RE-AIMED: S66, S238, S366, S693, S1882, S-U8, S303,
S420, S1708-S1714. `m6read_check_sab_anchors.py`: all anchors resolve.

### EMIT-3: the shape chosen, and the one judgment in it (for the manager)

"The chain at the island's set reading" was first built literally: every
class counted as its members. That restored the family, and also
OVER-ADMITTED classes the user WROTE, which no merge touched: base96 ->
literal reading, `(?i)` days of the week 0 -> 1 island (VM program 9,355 ->
80,373 B for 274K -> 273K instructions), `a.|bc` 0 -> 1 (~691 -> 78,549 B),
`(?i)x(?:cat|dog|cow)y` 0 -> 1 (2,257 -> 10,797 B, 720K -> 553K),
`x(?:[a-f]oo|[g-m]ar|zz)y` 0 -> 1 (2,033 -> 7,296 B, 597K -> 516K).
The ruling's purpose clause is "so a merge the island reads through cannot
flip the comparison", and EMIT-1's "(over budget: the size row decides as
today)"; so the built shape undoes ONLY rule M's folds (provenance on the
fold's node) and counts a written class as the one test the chain emits
for it. Under it every written-class decline of island section 4 stays a
decline (reasons restated as size-row declines), and the day/caseless
shapes keep the chain (`(?i)` days: 0 islands at both; its program is
smaller, 9,355 -> 5,897 B, from rule M itself). This sits
against R1, which REJECTED counting the unmerged split; R5 now orders the
set reading, and provenance is the narrowest form of it. If the manager
wants the literal reading instead, it is one line (`unfold` multiplies by
the member count) and the four over-admits above are its price.

### New mover class (EMIT-1 on a WRITTEN class), measured

A finite alternation holding a multi-member written class used to decline
the island outright; now the size row decides it like any other. Measured
(instructions:u, taskset -c 7, 3 runs each, identical):

| pattern | flags | base96 islands / program B / instructions | tip |
|---|---|---|---|
| `x(?:[éà]\|foo\|bar\|baz)y` | byte `--engine=vm` | 0 / 2,024 / 365,359 | 1 / 2,907 / 204,715 |
| `x(?:1[éè]\|q2\|r3)y` | `-e utf8 --engine=vm` | 0 / 1,826 / 364,364 | 1 / 2,468 / 213,355 |
| `x(?:[я]\|cat\|dog)y` | byte `--engine=vm` | 0 / 1,411 / 297,923 | 1 / 2,137 / 184,112 |

(1.6x-1.8x fewer instructions, ~45-55% more program bytes.) No answer
moves: the island is exact by construction and the denied-pair census
(job `altfix-movers`) re-reads the population.

### Acceptance table (re-measured)

instructions:u, `taskset -c 7`, 3 runs (all three equal to the digit
shown), single-process probes, not niced; base96 = the base with only its
abi digit bumped; "before" = the branch at `4cc816446`; "after" = this
lane's EMIT-1 build (the island stamps and program bytes of every row are
unchanged by the later EMIT-3 provenance step, checked per row: the stamp
and `RX_VM_PROGRAM_BYTES` equal base96's).

| cell | flags | base96 | before | after |
|---|---|---|---|---|
| bench altwide w-256 | `--engine=vm` | 205K, 143,470 B, 1 island | 12.19M, 20 islands | 205K, 143,470 B, 1 island |
| w-256 with captures (w256br) | `--features all` | 272.7K | 13.07M | 272.7K |
| months | `--features all` | 1.064M | 3.248M | 1.064M |
| `x(?:[éà]\|q2\|r3)y`, u1 subject | `-e utf8 --engine=vm` | 170K | 236.9K | 170K |
| same, u2 subject | `-e utf8 --engine=vm` | 237K | 456.6K | 237K |
| `(?:ab\|ba\|aa\|bb){24}c` (rule M wins) | `--engine=vm` | n/a | 1.737M | 1.737M (unchanged) |
| EMIT-3 family (`fam.txt` + both twins + `x(?:cat\|cot\|dog)y`, byte and utf8) | VM | islands / program bytes | the review's cells lost their islands | every cell with a base96 island has it, at base96's program bytes; three cells GAIN one (the written-class class above) |
| k400 (400 words + `\d+`) | default | one rung | `drop-islands` first | `drop-prefilter` only, 1 island, 239,386 B, 259K = base |

The full re-measure with the final tip binary is job `altfix-acc`
(OWED below): the EMIT-2/3 numbers above were taken during the lane, and
the kit's S2d timing window (rulings R6) began before the last build.

### OWED (detached box-queue jobs, owner altfix; read with `scripts/boxqueue state KEY`)

Every job waits on `altfix-gate` (ready once the kit's job 489 has ended,
R6), which touches `scratch/altfix/lift`. The batches run in `--snapshot`
worktrees of the commit named in the OWED list below.
Snapshot commit for every batch: `0a8d252f6`. Frozen tip binary for the
binary jobs: `scratch/altfix/tip/pcrec`, built from `8cbf0db6c` (src identical
to `0a8d252f6`). Each job's log is `job.log` in its run dir under
`/home/pcrec/projects/pcrec/worktrees/.boxqueue/{done,failed}/<ts>-<name>/` (perfrun's make log beside it as `job.log.make`).

| key (owner altfix) | runs | completion line to read |
|---|---|---|
| `altfix-gate` | the R6 lift (touches `scratch/altfix/lift`) | outcome=green |
| `altfix-acc` | the acceptance re-measure, base96 vs tip, 12 cells (`scratch/altfix/jobs/acc.sh`; artifacts `scratch/altfix/m/`) | `== acc DONE 12 cells` |
| `altfix-u1bench` | 301's re-run, fixed instrument, base96 vs tip (`scratch/altfix/out/u1_bench.tsv`) | `findings (unpredicted mover, growth, new refusal): 0` |
| `altfix-movers` | the 2b movers table re-measured, REF s12p vs tip (`scratch/altfix/out/p2b_movers_altfix.tsv`); rc 1 = denied-pair differences, PREDICTED from EMIT-1's written-class islands | `movers rc=0` or `movers rc=1` and its summary |
| `altfix-b202611062200122965726.strict`, `.test` | make strict; make test via perfrun | no `*** [(Makefile:N: )test-X] Error` line |
| `altfix-b202611062200122966738.mech1`, `.mech2`, `.reach` | mech S1880-S1882, S1886-S1894, S1990, S1991; S238, S66, S366, S693, S303, S-U8, S420, S1708-S1714; then REACH_ONLY over all 28 | `== mech run COMPLETE` trailer, every row DETECTED / reach ok |
| `altfix-b202611062200122968116.r302`, `.r303` | 302 re-run (test-registry, test-rxtsource); 303 re-run (test-fallback-table, test-island, test-codegen, test-recursion-identity-locked, plus test-prefilter, test-uprops-utf8 for the re-aimed witnesses) | no `*** [... test-X] Error` line |
| `altfix-b202611062200122969007.axes` | make test-axes, cap 28800 | no `*** [... test-X] Error` line |

The batches chain inside themselves (a stage waits for the one before to go
green), not across batches. Hand-checked green before queueing, on this
tree under the box lock: `run_island_tests.sh` (45 passed, section 12
included), `run_wclass_census.sh` (0 failed), `run_fallback_table.sh` (0
failed; the EMIT-2 cells and the re-aims included);
`m6read_check_sab_anchors.py` (all anchors resolve); mech VALIDATE_ONLY over
the 28 rows (all valid).
