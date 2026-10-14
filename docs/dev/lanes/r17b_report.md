# r17b — R17-b, R-17's one SIMD-off byte move (BUILD)

Lane r17b (opus), 2026-10-12, for the memfn kit manager. Branch `lane/r17b`,
cut from the kit branch `lane/memfn-r17` at `010b612c9`. Design followed:
`docs/design/memfn/setfind.md` rev 2.3 §11.2 with its `[rev 2.2]`/`[rev 2.3]`
blocks, §3.3-§3.5, §4.1-§4.3, §5-§8, §10, §12.2, §12.4a, §12.5 (S850-S854),
§12.6, §12.7, §14 (N5, N6), §R5-§R6; `docs/dev/lanes/r17a_report.md`;
`docs/design/memfn/probes/r17/slot24_triage.md`. Box: the Linux dev box, every
command `taskset -c 12-15`, `-j4`.

**Verdict: built in one abi event (76 -> 77, `MF_SITE_ABI` 11 -> 12). The
mover census reads BAD 0 over 4,542 distinct corpus patterns x 5 arms: every
mover is at a predicted site, and the deny artifact equals the reference on
every pattern. Every light suite listed in §5 is green after four reader re-aims (§6.5), and S850-S854 are
DETECTED solo.** The full `make test`, test-axes, the full mech, the identity
sweeps, G2 full, N2 and the G1 timing are OWED to slot25 (§8), staged, not
launched.

## 1. Census headline (§11.2: walk -> kit form, a pcrec-side reader over emitted C)

`docs/dev/lanes/r17b_movers.py` (committed; output `r17b_movers.out`) compiles
every distinct corpus pattern (`emit_sweep`'s enumeration, `--features all`)
three times per arm: by the reference compiler (the kit tip `010b612c9`, abi
76), by the tree's, and by the tree's with `--memfn=no-pf-terms-mask`. The abi
digit is normalized on the lines that name the abi. Then:

- The PREDICTION is read off the reference artifact alone. The artifact holds
  a table walk `while (X[ + 1] < subject_length && !rx_T[subject[X]]) X++;`,
  and that table, read from the same artifact, has a cover of at most 4 terms
  by the script's OWN search. The search is written from §3.1-§3.2's
  definitions in Python and shares no code with `memfn/src/terms.c`.
- A predicted artifact must move, carry `__next_candidate(&` and the W8
  sub-block, and hold no walk or table. Alternatively it may equal the
  reference, listed as `coverable-declined` (the kit's node budget, §6.2).
- Every other artifact must equal the reference.
- The deny artifact must equal the reference on EVERY pattern.

| arm | movers | coverable-declined | identical | both refuse | BAD |
|---|---|---|---|---|---|
| byte (default) | **996** (can_begin_match 527, -bounded 205, start_bytes-bounded 39, start_set 450 walks) | 0 | 3,168 | 378 | 0 |
| byte `--engine=vm` | **2,910** (5,820 start_set walks: entry + retry) | 0 | 1,255 | 377 | 0 |
| `-e utf8` | **964** | 0 | 3,211 | 367 | 0 |
| `-e utf8 --engine=vm` | **2,907** | 0 | 1,270 | 365 | 0 |
| `-fmemfn-simd` | **996** (identical to byte: no SIMD arm exists) | 0 | 3,168 | 378 | 0 |

(Re-run by lane r17b2 at the derived budget, §6.2's resolution. Lane r17b's
own run read 957 / 2,866 / 964 / 2,907 / 957, with 39 / 44 / 0 / 0 / 39
`coverable-declined`; those 39 byte and 44 VM artifacts, all `\W`-shaped, are
the new movers.)

Distinct walk sets judged: 505, of which 432 are coverable within 4 terms.

**Headline: SIMD-off movers 996 (byte) / 2,910 (VM) / 964 / 2,907 (utf8),
0 coverable-declined,
BAD 0, the deny arm byte-identical to abi 76 everywhere. The SIMD-on movers
equal the SIMD-off movers at every site.**

## 2. What changed, per file

**Kit (`MF_SITE_ABI` 11 -> 12, no `MF_VOCAB` move):**
- `memfn/src/terms.c` (new). `mf_set_terms` implements §3.2-§3.3: prime
  cubes from a containment table over all 3^8 cubes, maximal arcs from the
  target's runs, and bounded IDDFS branching on the lowest uncovered member.
  The objectives are lexicographic (§3.3).
  - **One result-preserving change**: per depth, the set's search runs first.
    A direct cover is ranked ahead of every complement cover, so the
    complement's search runs only where the set has no cover at that depth
    (§6.2).
  - `mf_cover_check` is §10's round trip, a loud refusal.
  - It also holds the two renderers: the W8 mask expression and the per-byte
    member test.
- `memfn/src/mfk.c` (new): the W8 sub-block (`PCREC_MFK_W8_H`, `pcrec_mfk_w8_*`)
  as one string; `mfk_block` writes it once per art; `mf_shared_block`.
- `memfn/src/pffind.c` gains the row `pf_terms_mask` (define, `locals`, use,
  contract, arm), and its header is rewritten (F-2). `PF_SERVES` splits into
  `PF_SERVES_SHAPE` plus the stem/window cells, and the old rows' contracts
  are unchanged.
- `memfn/src/kit.h`: the arm's `locals` column (appended; every other arm states
  NULL), `mf_art.mfk`, the cover types, `MF_SET_K` (4, MEASURED-UNOFFICIAL
  slot2) and `MF_SET_BUDGET` (4096, UNMEASURED DEFAULT).
- `memfn/src/compose.c`: `arms[]` gains the row between `pf_memchr_bounded` and
  `pf_walk`; `mf_locals` runs the row's `locals`; `mf_defined` reports
  `keeps_storage`.
- `memfn/include/memfn.h`: `MF_SITE_ABI` 12 and its log line,
  `mf_result.keeps_storage` (appended), `MF_P_TRACE`, `mf_shared_block`.
- `memfn/src/options.def`: `pf-terms-mask` (MF_OPT_DENY, MF_B_SCAN,
  MF_L_SCALAR).
- `memfn/PROVENANCE.md`: rows for terms.c and mfk.c; pffind.c's row.

**pcrec (abi 76 -> 77):**
- `src/gen/emit_dfa.c`:
  - `PCREC_ARTIFACT_ABI` 77.
  - `MemfnFind.keeps_storage`.
  - `emit_search_head(..., bool cin)`: the DFA search body and the hybrid's
    prefilter const-qualify their subject parameters where the defined FIND
    keeps storage.
  - `pcrec_subject_params`, one spelling shared with the VM's `_run`.
  - `pcrec_emit_vm_start_define` returns `keeps_storage`.
  - N4's door is called before the `reads_table` return (§6.3).
  - The Q-R5 comment above `vm_hat_find_of` is rewritten (F-2). The
    `PF_SCAN_SET` assertion in `pcrec_emit_vm_start_seek` is KEPT.
- `src/gen/emit_vm.c`: `_run`'s head reads `pcrec_subject_params(cin)`.
- `src/gen/memfn_sites.c`: the probe build (`-DPCREC_RANK_PROBE`) sets
  `MF_P_TRACE` on the art.
- `src/core/compile.c`: N6. `valid_prefix(p, &why)` extends the existing check
  and refuses, case-folded, `pcrec_mfk` or `pcrec_mfk_*` with its own message;
  one check serves every route.
- `src/core/internal.h`: the two declarations.

**Spec (D80, method-blind):**
- `match_api.md` §6.3's `RX_DFA_PREFILTER` values `byte-class`,
  `byte-class-bounded` and `first-class-bounded`, and `RX_VM_START_SCAN`'s
  `first-class`. Each now reads "the search kit's FIND over the set, its form
  the kit's, the table emitted where that form reads it". The VALUES are
  unchanged.
- §1¶7a (new): the sub-block guards `PCREC_MFK_<W>_H`, one per width, the
  reserved stem, and the mixed-abi refusal by ¶7's own guard.
- §8.0¶4: N6.
- §1¶7's code block and §6's `abi` cells read 77.
- `tuning.md`: §2.42¶2 ("the search kit's FIND over `S`"), §2.42¶4 (the
  `start_bytes` table where the form reads one) and §2.14¶1 (the set's form).
- `registry.md`: §6¶8a's new row `pf-terms-mask`, and §6¶8b's floor 6 -> 7.
- `cli.md` §1.6¶1 and `rxt_format.md` §1.3¶3: N6.
- `docs/dev/history/abi_changelog.md`: the 77 entry.

**Checks and tests:**
- `tests/memfn/setfind_check.py` and `run_setfind.sh`: `make
  test-memfn-setfind` (in TEST_SECTIONS) and the new mech arm `setfind`. They
  check §12.7's rows, the -Wjump-misses-init check over movers, the s/n write
  check, the const head, the table check (S840's), N6 on three routes, the
  trace reach and the trap fixture.
- `memfn/tests/g2/g2_setfind_gen.c`, `g2_setfind.h`, `g2_setfind_driver.c` and
  `memfn/tests/run_g2_setfind.py`: G2's setfind family, section 4c of
  `run_g2.sh`.
- `tests/mech/sabotages/S850-S854` and the `setfind` arm in
  `run_sabotage_matrix.sh`.
- The test readers, re-aimed (§4).
- `tests/memfn/arm_fixtures.c` gains two seq cases (`locals-walk-uncoverable`,
  `locals-walk-denied`), and `run_arm_pins.sh` sets `locals-protocol` RENDER
  `pf_terms_mask` with `GATE_CASE_FLOOR` 100.
- `tests/memfn/rows.tsv`: the new row, with the walk witnesses re-picked.
  `row_floors.tsv` gains the new row, and the two walks' pcrec floors return
  to PLACEHOLDER. `run_rows.sh` sets `ROWS_FLOOR` 21.
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT` 77, its message, and the
  OS-1 head regex. `tests/mech/sabotages/S693`: re-aimed 77/76.
- `docs/dev/optloop/alpha_r17b.sh`: the G1 harness, staged.
- CLAUDE.md: `memfn/`, `memfn/src/`, `memfn/include/`, `memfn/tests/`,
  `tests/memfn/`, `tests/startset/`, `tests/mech/`, `src/gen/`, `src/core/`,
  `docs/dev/lanes/`, `docs/dev/optloop/`.

## 3. The abi readers found by grep (D76/D94)

`git grep` was run for `76` beside `abi`, `ABI_H`, `ABI_EXPECT` and
`PCREC_ARTIFACT_ABI`, and for the emitted head spelling. Every hit:

| reader | change |
|---|---|
| `src/gen/emit_dfa.c` `#define PCREC_ARTIFACT_ABI` | 76 -> 77 (the `.abi` stamp, K80's guard value and `#error` text derive from it) |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=76` | 77, plus the transition message's 76->77 clause |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | BEFORE 77, AFTER 76, re-aim note |
| `docs/spec/match_api.md` §1¶7 code block (3 sites) | 77 |
| `docs/spec/match_api.md` §6's `abi` table cell and §6¶17's "It is `77`" | 77 |
| `docs/dev/history/abi_changelog.md` | the 77 entry |
| the identity gate's (B) pin, `tests/codegen/run_recursion_identity.sh` FILEPIN | NOT moved: it self-pins to the branch's last `src/` commit, and the brief makes this change ONE commit, so the pin is OWED at the merge (opt5i's precedent; the gate is opt-in and not in this lane's light list) |
| readers of the emitted HEAD spelling, which never cite the number (D94 addendum) | `run_anchored_match.sh` §2's positive half, `run_codegen_tests.sh` OS-1's signature check, `run_dfa_stamps.sh` and `run_premul_table.sh`'s `rx_prefilter(` head match (all: `*\(const \)?subject`) |

Not readers: `registry_check.c`'s `qualifying != 76` (a row count); the
`[LOSS-REVIEW] (abi 76)` history comments in `tests/backrefs/*`,
`run_encoding_checks.sh` and `S825` (dated narrative).

## 4. The test readers of the walk text (§12.6, K2-8), re-aimed

| reader | what it reads | fate |
|---|---|---|
| `tests/codegen/run_dfa_stamps.sh` | the bitmap / start_bytes walk markers | gains the kit use line as the SET arms' second spelling (no hat: byte-class; with the hat's re-seed: first-class-bounded; the guard's `- scan_position > 1` is the D11 bound) |
| `tests/codegen/run_anchored_match.sh` §2 | no PF inside `rx_match`; the search entry HAS one | the kit marker joins both; the head regex tolerates the const |
| `tests/assertions/run_mline_diff.sh` | the `bitmap` mechanism | the kit marker joins it |
| `tests/codegen/run_premul_table.sh`, `run_dfa_stamps.sh` | the hybrid prefilter's head | const-tolerant |
| `tests/startset/{startset_checks,vmhat_checks,dfahat_checks}.py` | the emitted tables, seeks and stamps against the facts | compile with `startset_lib.KIT_WALK` (`--memfn=no-pf-terms-mask`): pcrec's start-set text is held on the deny arm, where the census proves it is today's byte for byte; `vmhat_diff.py`'s answer differential keeps the default arm |
| `tests/memfn/rank_check.py` (N4 door counts) | `FINDDOOR` records where a table is emitted | the door now fires at every defined set site (§6.3), so its floors read the full population again |
| `tests/memfn/rows.tsv` | row witnesses and signatures | the new row, walk witnesses re-picked (`(*UCP)(?aD)\w`, `(*UCP)\b\w+\b`: corpus patterns whose Latin-1 word sets have no 4-term cover) |
| `tests/codegen/run_offset_skip.sh` §2c | ofsskip reads no `can_begin_match` | unchanged (the offset-skip sites do not move) |
| `tests/codegen/run_cpset_structure.sh` CHECK 3 `EMITTED_BYTES` | sample byte counts | re-recorded with the diff read if moved (§5) |

The populations and floors are as follows:

- The deny-arm readers keep their existing literal floors. Their population
  is today's, by the census's deny == reference.
- The default arm's population is the census count (§1).
- The new structural check's own sample floors are floor(0.9 x measured) from
  its first run: 185 movers, 306 uses and 317 non-movers at `--every 25`, so
  floors 166 / 275 / 285.

## 5. Light verdicts (this box, pinned 12-15, logs under `build/r17b/logs/`)

| suite | verdict | log |
|---|---|---|
| `make -j4`, `make strict` | clean (rc 0) | `sec2_strict.log` |
| `test-memfn-setfind` | 32 passed / 0 failed (witnesses 10/10, corpus 502 artifacts, N6 12/12, trace 4/4, trap) | `setfind1.log` |
| `test-memfn-arms` | 385 passed / 0 failed | `sec2_test-memfn-arms.log` |
| `test-memfn-link` (C16) | 8/0 | `memfn-link.log` |
| `test-memfn-manifest`, `-arch`, `-forms`, `-reach`, `-stamps`, `-guarded`, `-simdfloor`, `-deleg` | 11/0, 15/0, 5/0, 4/0, 25/0, 10/0, 51/0, 5/0 | `memfn-*.log` |
| `test-memfn-rows` | 162 / 0 | `sec2_test-memfn-rows.log` |
| `test-memfn-rank` (+ N4 door) | 15 / 0 | `sec2_test-memfn-rank.log` |
| `test-startset` | 35 / 0 | `sec2_test-startset.log` |
| `test-registry` | 79 / 0 | `sec2_test-registry.log` |
| `test-rxtsource` | 298 / 0 | `sec2_test-rxtsource.log` |
| `test-codegen` | 16 / 16 scripts passed (SABANCHOR included) after the reader re-aims of §6.5; the first run was red on three readers | `sec3_codegen.log` (first run `sec2_test-codegen.log`) |
| `test-cpset-structure` | 29 / 0 after CHECK 3's deliberate re-record (§6.5); first run 28 / 1 | `cpset2.log` (first run `sec2_test-cpset-structure.log`) |
| `test-assertions` | 9 / 0 | `sec2_test-assertions.log` |
| `test-spec-history` | 144/1. The one red is PRE-EXISTING on the kit branch: line-number citations in `docs/design/memfn/probes/r17/slot24_triage.md` (:168/:170/:185) and `memfn/docs/responses.md:2303`. Main's copy of the review file is fixed; the kit's two files are the kit session's | (ran directly) |
| G2 quick (`make test-memfn-g2`) | 52,987,688 passed / 0 failed. The setfind family is inside it, and `pf_terms_mask` is chosen 2,720 times (its g2 floor is pinned at 2,448 = floor(0.9 x 2,720)) | `sec_test-memfn-g2.log` |
| G2 setfind quick alone | 21/0. 1,616 sets (974 MUSTRENDER all stateful, both edges declined). O2: 52,387,628 checks, 0 failed. O0 dirty: 10.5M. ASan+UBSan: 12.8M. Byte-swapped LE: 17.5M, with its control failing 8.06M as it must. Trace build: 17.5M, 16,296 trap sites. Trap fixture: trapped (SIGILL) | `g2s_quick.log` |
| mover census, full | BAD 0 (§1) | `docs/dev/lanes/r17b_movers.out` |

## 6. Findings and deviations (setfind.md text vs the code; smallest sound reading taken)

**6.1 The design never says how pcrec learns a site is stateful.**
§7.4 requires the const qualifiers "only in bodies that hold a stateful site",
and a const head on a non-mover would move an artifact the census does not
predict. pcrec cannot name the kit's form (D157), and `mf_defined` reported
only `reads_table` and `includes`. I added `mf_result.keeps_storage`, a report
of the define appended last. It is set iff the chosen row has a `locals`
column. That is a layout change, so `MF_SITE_ABI` moves 11 -> 12 in the same
commit. No test pins that number.

**6.2 The node budget binds on the corpus's own word classes (T3's tripwire
is crossed).** At BUDGET 4096 as written:
- `\w` needed 5,583 nodes and DECLINED. The design (§12.6) treats `\w` as a
  4-term mover.
- After the one result-preserving change (per depth, search the set before
  its complement; objective 2 makes a complement result at that depth
  irrelevant once a direct one exists), `\w` takes 1,486 nodes and renders
  its cover. 1,486 is still above BUDGET/4 = 1,024, T3's limit.
- `\W` needs 25,763 nodes (75 ms), because proving `\W` has no direct cover
  within 4 terms is the expensive half. So it DECLINES to the walk, which is
  sound.

The census lists these as `coverable-declined`: 39 byte and 44 VM artifacts,
all `\W`-shaped sets. §3.3 says that if any corpus set exceeds BUDGET/4, "the
budget has become a visible selection constant and must be derived instead".
That condition now holds, and a ruling is owed. Two options: derive the
budget, or make the search cheaper without changing its result (for example,
a sound lower bound on the terms a residue needs). The search order the
design specifies is kept, so `\W` stays a walk until then.

**6.2 RESOLUTION (lane r17b2, 2026-10-12, branch `lane/r17b2`): the search
is pruned without changing its answer, and the budget is derived.**

*The change* (`memfn/src/terms.c`, `dfs` carries each prune's argument in its
comment). It rests on one fact. Iterative deepening returned at the first
depth with a cover, so at depth k every recordable cover has exactly k terms,
and a node d terms short of k completes only with exactly d more.
- **A lower bound.** Members x and y are JOINT iff some candidate holds both.
  By §3.2's dominance that is iff the cube they span is inside the target, or
  they sit in one run within 128 of each other. A greedy set of uncovered
  members, pairwise not joint, needs one term each. A node whose bound
  exceeds its depth has no completion, so it is cut.
- **A cost bound.** Once a cover is recorded, a branch whose cost so far plus
  6 (the cheapest term) per remaining term exceeds the best cost is cut.
  Equal cost is kept, because objective 4 decides it.
- **The branch member** is the uncovered member with the fewest joint
  partners, not the lowest. Every k-term cover still holds it in some term,
  so every cover is reached. The best cover is ranked on the sorted cover,
  whatever order it was reached in.
- The per-depth set-first order (lane r17b) is kept.

*Node counts* (nodes per derivation, both targets, all depths):

| set / population | before (unbounded) | after |
|---|---|---|
| `\w` | 1,486 | **21** |
| `\W` | 25,763 (DECLINED at 4096) | **22** (covered: the complement of `\w`'s cover) |
| corpus + bench FIND sets (558; 49 bench-only) | max 228,276; 32 over 4096 (7 with a cover, 25 with none) | **max 29** |
| every 256-entry table in those artifacts (1,201) | max 238,642; 91 over 4096 | max 29 |
| G2's full setfind set space (15,590) | max 428,662; 84 over 4096 | max 143 |
| the generated space (1,354,644) | 52,069 over 4096 (26,351 with a cover) | **max 787** (a 4-term union) |

*Compile-time cost.* On the corpus FIND sets, the new search takes a mean of
0.186 ms per set (max 0.25 ms). The old search took 0.498 ms on the sets it
completed within 4096 nodes, and 13.4 ms mean / 1.26 s max with the budget
lifted. Over the generated space the new mean is 0.229 ms, against 8.50 ms
for the old unbounded search. The new fixed cost is the pair table, about
0.07 ms, and it is paid once per target.

*The independent control.* `docs/dev/lanes/r17b2/harness.c` links the tree's
search beside the OLD search: `terms.c` at 174f3e320, with its cap turned into
a variable and set to 50M (corpus), 5M (G2) or 2M (generated). Neither search
reads the other. Results:
- corpus FIND sets: 558/558 SAME;
- all 256-entry tables: 1,201/1,201 SAME;
- G2 full: 15,590/15,590 SAME;
- generated: 1,354,644/1,354,644 SAME.

There were 0 DIFF and 0 REF-INCOMPLETE: the old search completed on every set
under its cap. So the two searches agree everywhere, the old one with no
budget. That includes 155,523 generated sets above BUDGET/4 = 1,024 for the
old search, and 52,069 above the old 4096. Per family (n / new max / old over
4096):
- single 512 / 2 / 0
- pair 65,280 / 47 / 0
- cube 10,544 / 2 / 0
- range+arc 64,006 / 2 / 0
- near-cube 360,854 / 143 / 833
- union 178,938 / 787 / 10,490
- G2-shaped union 198,920 / 91 / 1,079
- scattered 59,874 / 227 / 3,787
- one-member corpus neighbours 197,206 / 337 / 17,036
- two-member 218,510 / 659 / 18,844

*The budget* (`memfn/src/kit.h`, labelled DERIVED/MEASURED):
`MF_SET_BUDGET = 4 x 787 = 3148`. 787 is the most nodes over the whole stated
population above, and 4 is T3's margin. It is not 4096 raised: it is LOWER,
and no set of the population comes near it. A structural worst case was not
usable: up to 384 candidates per node at depth 4 is about 2e10 nodes.

*T3* (`tests/memfn/setfind_t3.c`, leg 5 of `make test-memfn-setfind`). It
runs over the pinned 558 sets plus singletons, every cube and 2,000 seeded
unions, with complements: 18,102 sets.
`T3 max nodes 187 (at union 895), budget 3148, budget/4 787` -> `T3 OK`. It
reads the kit through the new test-only `mf_set_terms_probe` (memfn.h,
listed under MF_SITE_ABI 12, the same unmerged event).

*New movers* (§1, census re-run at full population on the five arms, BAD 0):
byte 957 -> 996 (+39), VM 2,866 -> 2,910 (+44), `-fmemfn-simd` 957 -> 996,
and utf8 / utf8-vm unchanged (964 / 2,907). `coverable-declined` 39 / 44 -> 0.
These moves are part of abi 77; nothing was bumped again. The slot25 script
now defaults W to this worktree, and its census judge expects 0
coverable-declined.

**6.3 N4's door fired only where the table is emitted.** The stateful form
emits no table, so the probe build's `FINDDOOR` population collapsed: 150 /
1 / 141 against floors of 1,400 / 70 / 3,100. N4's claim is that the set
handed to the kit equals the table pcrec NAMES, and that holds whether or not
the table is emitted. The door now runs before the `reads_table` return on
all three tables. This is probe-build code only: the default build's stub is
a no-op, and no artifact byte moves.

**6.4 The design's §12.6 K2-8 table names five readers; grep found more.**
These were not in the table:
- all of `tests/startset/`'s structural checks, re-aimed at the deny arm (§4);
- four readers of the emitted HEAD spelling, which the const qualifiers moved
  (§3);
- the rank probe's door counts (§6.3).

**6.5 Three more test readers of the walk, found by running test-codegen
and test-cpset-structure.** They were missing from §12.6's table and from
§6.4's grep; the suites that count are what found them (D94 addendum):
- `run_codegen_tests.sh` [K24]: the witness `(alpha|beta|gamma|delta|epsilon)`
  is a mover. Its de-sugared, attribute-stripped CONTROL no longer gets gcc
  to split `rx_search`, so the control stopped firing. The check now
  compiles the deny arm, which is the shape the regression was measured on.
  The attribute is emitted on both arms.
- `run_offset_skip.sh` §2c reads `can_begin_match` from a
  `-fno-offset-skip` build of `uuid`. That build's byte-class body is now
  the kit's form and has no table, so the check now passes
  `--memfn=no-pf-terms-mask` too. This is the same shape as the
  `-fno-start-set` and `-fno-req-handoff` additions before it.
- `run_cpset_structure.sh` CHECK 3: four `EMITTED_BYTES` rows moved, and all
  four are census movers. They were re-recorded deliberately, each deny
  artifact verified byte-identical to the reference. The manifest's own
  history comment records it.
- `run_dfa_stamps.sh` did not parse after my reader edit: an apostrophe in a
  comment inside its single-quoted awk block. Fixed, 39 / 0.

**6.6 Not deviations, as specified:**
- one row; no adapt, ring, stateless or memchr_set row;
- no density fact;
- `MEMFN_FORMS` stays `none`, and `MEMFN_LIBC` is unchanged (the form calls no
  libc);
- `RUN_WORDS` and the stamp VALUES are untouched;
- the `PF_SCAN_SET` assertion is kept;
- W8 is the only sub-block;
- the guard carries no value.

A design-conformant detail worth knowing: `\w`'s cover spells `_` through
the prime cube {G, O, W, _} (cost 7), because the non-prime EQ(`_`) is not a
candidate (§3.3's stated restriction).

## 7. Sabotage figures (solo, `tests/mech/run_sabotage_matrix.sh <id>`, at `db41314e5`; logs `build/r17b/logs/mech_S85*.log`)

| id | plant | detector | figure |
|---|---|---|---|
| S850 | the storage point moved below the seedhead `goto` (two edits in emit_dfa.c) | `[witness dfa-scan-edge]` jumps (`[0-9]{3,}x`, -Wjump-misses-init on `__c`) | `setfind:7fail/29pass` DETECTED |
| S851 | the use's guard pastes the live `n` hook | the use-text check, every mover | `setfind:16fail/26pass` DETECTED |
| S852 | the head drops `size_t const`'s const | the head check, every mover | `setfind:18fail/24pass` DETECTED |
| S853 | the trace's bound-vs-live trap removed | the trap fixture and the trace reach (traps != uses) | `setfind:6fail/27pass` DETECTED |
| S854 | N6's refusal removed | the N6 cases on `-p`, an .rxt target and the library | `setfind:7fail/25pass` DETECTED |

All five rows: `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0, anomalies: 0, oracle-skipped: 0)`.

## 8. OWED to slot25 (staged at `worktrees/memfn-slot/slot25/run.sh`, NOT launched)

The judges are stated in the script's header. In brief:

- **The census at full population over thirteen arms:** the default five plus
  `-fno-start-set`, `-fno-offset-skip`, `-fno-req-handoff`, `-fno-req-run`,
  `--tune=min-size`, `--tune=max-speed`, `-e utf8 --engine=vm -fmemfn-simd`
  and `-fcomments`. Its judge is `BAD 0`.
- **`emit_sweep` over the streams with no abi digit**, plain and utf8: 0
  movers, except the `--list-axes` memfn row. Also the variants over the
  listing streams, and the `--trace` sweep, whose judge is selection-trace
  identity.
- **G2 quick and full.** The full tier's setfind floors print UNREACHED; pin
  them from that run.
- **N2 with `--propose`.** Pin `pf_terms_mask`, `pf_walk` and
  `pf_walk_bounded`'s pcrec floors and the new row's g2 floor in
  `row_floors.tsv`.
- **`run_setfind.sh` at `SETFIND_EVERY=1`**, `make test` through perfrun, and
  the full mech.
- **The G1 alpha at both layers** (`alpha_r17b.sh all`: base `010b612c9` vs
  the tip, deny `--memfn=no-pf-terms-mask`, `first` and find-all, OFF and
  `-fmemfn-simd`). The ON column times the same artifacts until arms exist,
  and its `check` prints `ON==OFF` saying so. This is pcrec's own regime; the
  official verdict is the bench relay (§11.2a), which is main's.

Also owed (not in this lane's brief; each has an owner and a trigger):

| item | owner | trigger |
|---|---|---|
| ~~the budget ruling (§6.2)~~ RESOLVED by lane r17b2 (§6.2's resolution); T3 built as leg 5 of test-memfn-setfind | - | - |
| sabotage rows S820-S843 (the kit's renderer/cover/cache plants allocated to R-17; only S850-S854 were briefed) | the kit manager | a follow-up lane before or with slot25's mech |
| T2 golden pin `tests/memfn/pins/setfind_terms.tsv`, T3 budget tripwire, T4 `pcrec_cube_of` cross-check (§12.1) | the kit (T4 pcrec-side) | the D27-blinded G2 author's lane, or the follow-up |
| §12.2's Q8 (two sites in one function, the S835 fixture) and Q10 beyond SWAR; the dynamic cache-path reach for S830-S834 (gcov, §12.5) | the kit | with the S820-S843 rows |
| §13.4's disassembly check (the struct stays local; syn8) | the kit | slot25's alpha reading |
| the bench relay (§11.2a, gates the merge) | main | after slot25 |
| the D155 addendum 4 annotation (the renderer lands in R17-b) | main | already asked (K3-10) |

## 9. Charter vs committed

| brief item | committed |
|---|---|
| `pf_terms_mask`, SWAR `mask8_swar` behind `<stem>__next_candidate`, cover from `mf_set_terms` K = 4, no density | yes (pffind.c, terms.c) |
| options.def `no-pf-terms-mask` MF_L_SCALAR MF_B_SCAN MF_OPT_DENY; registry §6¶8b 6 -> 7 | yes |
| no adapt / ring / stateless / memchr_set row | none built |
| per-width sub-block renderer, demand-emitted, W8 only SIMD-off, `PCREC_MFK_<W>_H`, stem `pcrec_mfk_` | yes (mfk.c; W8 once per art; presence/identity checked) |
| const-qualified subject inputs on the holding bodies (K3-3) | yes (DFA body, hybrid prefilter, VM `_run`, exactly where the form keeps storage: §6.1's report field) |
| the body guard reads `<stem>__c.n` (K3-2); trace `c.n == n && c.s == s` trap (§12.4a) | yes |
| N6 in `valid_prefix` (every route), spec hunks cli.md §1.6¶1, match_api §8.0¶4 + every reader by grep | yes (+ rxt_format §1.3¶3) |
| ONE abi event 76 -> 77, readers by grep | yes (§3) |
| stamps per §11.2 (MEMFN_FORMS none) | yes |
| method-blind spec hunks (RX_DFA_PREFILTER, RX_VM_START_SCAN, tuning §2.42, the sub-block sentence) | yes (+ tuning §2.14¶1) |
| Q-R5 comment rewritten; PF_SCAN_SET assertion kept | yes |
| re-aimed test readers with before/after populations and floors | yes (§4), plus the readers grep found beyond §12.6 |
| -Wjump-misses-init over the movers; s/n and const-head checks; trace reach | yes (setfind_check.py, run_setfind.sh) |
| S850-S854 each DETECTED by a single-row mech run | yes (§7) |
| G2 against the scalar byte loop over a generated predicate space, incl. §12.2's candidate sequences | yes for Q1-Q7, Q9, the guard pages, ASan+UBSan, the BE test and the trace. OWED: Q8 and Q10 beyond SWAR |
| mover census over emitted C, never the kit's `moved` | yes (§1) |
| slot25 script (identity sweeps, G2 quick + full, N2, make test, mech all rows, G1 alpha both layers) | yes, staged, not launched |
| light validation only | yes |
| CLAUDE.md updates | yes |
