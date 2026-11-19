# Lane l1build: span_arms L1, the census, then the three remodel commits

Lane l1build (opus), 2026-11-19. Branch `lane/l1build`, cut from main `e121371b2` (the unit's BASE). Design of
record: `docs/design/span_arms.md` rev 3.2, §14.4 "Common to every unit" and "L1", steps (1) and (2) only. The
feature (sites 1-9, 21, 23) is NOT built here; a fresh lane builds it from "Notes for the feature lane".

## Summary

- **Census first** (`l1build_evidence/census_l1.py`). It took about 15 minutes to write and run
  (08:37-08:52; the reference-compile phase runs in about 1 s). It does NOT stop L1 under D191.1's literal rule.
  - The model predicts 54 movers. All 54 are in the corpus and none in the bench.
  - 51 are `dead`: synthetic fixtures such as `y(?=a)z`, 42 of them in `tests/lookaround/d27/matrix.rxt`.
  - 3 move `req_set`/`req_byte`/`req_set_maxoff`, all in `tests/possessify/composition_d27.rxt`.
  - Every expected mover and non-mover named in §14.4/§14.2 (26 rows) agrees with the model. One FINDING:
    `req_set_maxoff` moves with every `req_set` mover, and §14.4's list omits it.
- **The three remodel commits are landed on the branch**, each in its own commit, answer- and byte-identical
  by construction:
  - RM-1 `a4230e01e`;
  - RM-6 `e7bb64748`;
  - remodel 3 `7581123e4`.
- **Re-aimed sabotages:** S1638-S1641 (the kindrow.def rows gain a column) and S1891 (`anf_head`'s REP arm
  moved into desc.c).
- **Identity verdicts and the binding sabotages are OWED** as box-queue jobs (STATE AT HANDOFF).
- **Already measured on the box:**
  - `make strict` is clean at the tip.
  - `tests/core/kindrow_check.sh` passes 6/6.
  - `tests/litscan/spanarms.rxt` passes 288/0 at the tip.
  - A 56-compile byte comparison of the `\w`-class-head witnesses shows base = RM-6 = remodel 3.

## Census

**The instrument.** `docs/dev/lanes/l1build_evidence/census_l1.py` follows §14.4 L1 "Census (first)":
- census_e1.py's scanner and census_e2.py's item classes, loaded from their files;
- an exact-set model over the BYTE spelling. It reads no compiler code:
  - consumed one-position items become byte sets;
  - a set over 128 members (`PCREC_MAX_REQ_RUN_POS_SET`) is a gap;
  - each positive lookaround's item is its body's per-offset sets: a lookahead's left-aligned, a
    lookbehind's right-aligned, an alternation body united per offset where every branch reaches, nested
    items kept at their own offsets;
  - the guard is the item's terms out to the first absent or out-of-domain term;
  - the guard meets consumed positions only across exact-width neighbours, and stops at a gap or a wall;
  - edge leftovers meet each other;
  - an empty meet is NEVER, propagated by D-9's rows;
  - reach 0: guards are dropped at the root.

Where the model narrows a consumed position:
- **The spelling.** The narrowed pattern is spelled (the item text is replaced by `\xHH` or `[\xHH...]`). The
  run, `req_set`, `req_byte` and `req_set_maxoff` predicted for it are the BASE compiler's facts of that
  spelling, encoding byte (E1/E2's method: the model's own part is the spelling).
- **The TOP SET STEP.** It is applied on top: every exact one-byte position of the predicted run, plus every
  narrowed one-byte position the spelling's set keeps, joins today's `req_set`. The second term exists
  because the walk applies the step BEFORE the run floor (READYL1-7), so a below-floor run still joins.

The STOP reads this predicted population (RULING-4). The two-sided observed-vs-model compare belongs to the
feature's gate.

**Population** (`l1build_evidence/census_summary.txt`, the base build `e121371b2`):

| quantity | count |
|---|---|
| rows (corpus + bench) | 7460 (7071 + 389), 5815 distinct texts |
| texts with a positive lookaround | 675 |
| abstained | 97 (55 subroutine calls, 16 conditionals, 13 `(?x)`/`(?i)`, 4 recursion, 9 other); bench 1 (a `(?x)` scanner pattern) |
| read by the model | 578 (bench 7) |
| model narrows or proves never | 60 (corpus 60, bench 0) |
| of them refused by the base compiler (`refused.rxt`, `gated.rxt`) | 5 |
| narrowed, no fact moves (`(?=a\|bc)\w`: the narrowed position is `[ab]`, no single byte) | 1 |
| **PREDICTED MOVERS** | **54 (corpus 54, bench 0)** |
| `dead` (why on `req_whole_run`) | 51 |
| `req_whole_run` | 0 |
| `req_set` / `req_byte` / `req_set_maxoff` | 3 / 3 / 3 |
| lowerings among the movers | look-ahead-pos:ctx 16, :look 22; look-behind-pos:ctx 5, :look 12 |

The 3 fact movers are `\w*(?=a)\w`, `(?=a(b)?)\w\1?` and `A*(?=a)\w`: `req_set` gains `a` (97), `req_byte`
none→97. The 51 dead movers are listed one per line in `census_summary.txt`.

**Model limits, counted rather than predicted** (an under-approximation, in texts):

| limit | texts |
|---|---|
| a guard stopped at an alternation group's edge | 122 |
| a guard stopped at a repeat's edge | 53 |
| a quantified lookaround | 42 |

**§14.4's expected movers and non-movers, each by name: 26 rows, 0 disagreements.** The predicted values
match §14.2's L1 column:

| pattern | predicted run | `req_set` | `req_byte` |
|---|---|---|---|
| `xy(?=bc)[bc]c` | `xybc` | gains 98 | — |
| `a(?=b)[bc]` | `ab` | gains 98 | 97→98 |
| `ab[xy][xy](?=(?<=xx)y)[xy]` | `abxxy` | gains 120, 121 | 98→120 |
| `[ac][ac]cc(?<=acc)(?<=cc)d` | `[ac]accd` | gains 97 | — |
| `x(?=qr)[pq]r` | `xqr` | gains 113 | 120→113 |

- **Dead:** `foo(?=bar)baz`, `(?<=ab)(?<=cb)c` and W-D8 `x[^\x00-\xff]y`.
- **Not moved:** `xyz(?<=yz)abc`, `xy[ac]b(?:(?<=ab)b|c)` and `x(?=ab|ac)a.`, plus every L3/L2 row of §14.2.
- **Live** (not dead): §5.2 (g)'s `x(?:foo(?=bar)baz)?y`, `(?:foo(?=bar)baz|q)` and `(?:foo(?=bar)baz){0}x`.

None of the five expected value movers is itself a corpus pattern: they are §14.2's own probes, which the
feature's tests add.

**Finding 1 (census).** On every `req_set` mover, `req_set_maxoff` moves too: a byte joining the set joins
its offset table. §14.4's expected-mover list names `req_set` and `req_byte` but not `req_set_maxoff`. The
census's EXPECT table adds it on those rows, with a comment pointing here.

**Finding 2 (census, scope).** No bench pattern moves at L1. L1's own movers are fixtures. Its value is
structural: the item, the guards and the never bit, which L3 and L2 read.

## Census verdict

**NOT a stop** under D191.1 / RULING-4: the model predicts movers (54, all in the corpus). As the manager's
R1 asked, stated plainly: **L1's own movers are 51 dead/never fixtures and 3 narrowings, all in the corpus,
none in the bench.** At the model-only stage this was 56 never and 4 narrowing; at the compiled stage 5 never
patterns are base-refused and 1 narrowing moves nothing. The bench's lookaround patterns are L3/L2 shapes.
The judgement for each, one line each:

| bench line | pattern | unit | why |
|---|---|---|---|
| 90 | `(?<=\$)\d+(?:\.\d{2})?\b` | L3 | BACK: the lookbehind `$` before the consumed head `\d` gives `$[0-9]` at K −1, where today's run is below the floor |
| 94 | `^(?!.*\.\.)[A-Za-z0-9.]+(?=@)` | L2 | AHEAD: the consumed tail `[A-Za-z0-9.]` (R1's copies) `++ @` |
| 113 | `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$` | none | every lookahead body starts with `.*`: no item at any offset, so no unit moves it |
| 255 | `item(?= done)` | L2 | AHEAD: `item done` at 0, consumed `[0,4)` |
| 258 | `(?<=item )done` | L3 | BACK: `item done` at K −5 |
| 309, 310 | the `(?x)` inline-C scanner patterns | (abstained) | `(?x)`: the model does not read them; no claim |
| 332 | `(?<=[\x{400}-\x{4FF}])\s` | L3 (utf8) | BACK: the lookbehind's two UTF-8 byte positions `[d0-d3][80-bf]` before `\s` |
| 333 | `(?<=\xc3\xa9)x` | L3 | BACK: `\xc3\xa9x` at K −2 |
| 335 | `(?<=a\|\xc3\xa9)x` | L3 | BACK: the branches' common last offset `[a\xa9]` before `x`, at K −1 |

The manager carries the question "is L1's feature worth building before L3/L2's value is shown" to the owner
(R1). The remodels landed anyway, as R1 ruled: they are refactors under D191 addendum 2, and L3 and L2 need
them too.

## Remodel commits

1. **RM-1, `a4230e01e`**, `src/facts/req.c`, `src/facts/facts.c`:
   - **`RbRuns` half (D-2):** `rr_unit` is now the stated empty value, a designated initialiser. `rr_pos`,
     `rr_cat` and `rr_alt` start from it, and each `rr_alt_rows` row (`rr_alt_union`, `rr_alt_affix`) writes
     a complete value from it.
   - **`ReqRun` half (D-5):** both writers start from `pf_req_run_none()`: the deny's empty value in
     `pf_store_empty`, and the derivation in `pf_derive_req_walk`.
   - **Anchors:** the base anchor map's RM1 group is the note's 15 (S268 S446 S466 S807 S1910 S1915-S1919
     S1923 S3129-S3132). Each still matches once after the edit, so none moved and none was re-aimed.
2. **RM-6, `e7bb64748`**:
   - **The column:** `src/core/kindrow.def` gains a NEVER column, with values NO / ANY / EVERY / BODY /
     NODE. `src/core/internal.h` gains `KindNever`, `KindRow.never` and `pcrec_never_by_row` (the one
     propagation, a no-default switch). `pcrec_ast_row` picks NO for a NEGATIVE `A_LOOK`, the same way it
     already picks the `consume` TEXT of `A_CALLOUT`.
   - **The readers:** `src/opt/derive.c`'s `q_cat`, `q_alt`, `A_CAP`, `A_ATOMIC` and `A_LOOK` read the
     column; a new helper `q_never_body` serves the one-body kinds. The NODE answers (`is_never_leaf`, REP's
     `m`), the rewrites and the group-keep rule stay in derive.c.
   - **S899:** its line, the prune `if (it[i].never && !it[i].keeps)`, is kept verbatim at its column, so
     S899 did not move.
   - **Re-aimed:** S1638-S1641. Their whole-row anchors gain `, BODY)`/`, NO)`; the intent is unchanged.
   - **Doc:** `src/core/CLAUDE.md`'s kindrow line names the column.
3. **Remodel 3, `7581123e4`**:
   - **The rule:** the head's per-kind rule moves from `src/opt/altnf.c`'s `anf_head` into `src/facts/desc.c`
     as `pcrec_ph_node(cx, a, body, pos, env)`, with the position callback `PhLeafPos` declared in desc.h.
     `A_WCLASS` is the callback's answer, and a CAT/ALT spine reaching the rule is a loud internal error:
     its walker folds the spine.
   - **The caller:** `anf_head` keeps only the walk and passes `anf_head_pos` (a class is its node,
     `A_WCLASS` none). It is the rule's first caller.
   - **Re-aimed:** S1891, from `anf_head`'s REP arm to `pcrec_ph_node`'s.
   - **Register row 27's status is updated** (`docs/dev/guide/architecture.md`). The rule landed, and the row
     closes when L1's feature makes the run walk's item the second caller.
   - **Doc:** `src/facts/CLAUDE.md`'s desc line names `pcrec_ph_node`.

The anchor map tool is extended at `l1build_evidence/firstunit_anchors_l1.py`, the r50 tool with the RM-6
(derive.c, kindrow.def, internal.h) and remodel 3 (altnf.c, desc.c) range groups. Its output at the base is
`l1build_evidence/anchor_map_base.txt`:

| group | anchors at the base |
|---|---|
| RM6 | S1189, S893, S899, S904 |
| RM6k | S1638-S1641 |
| REM3 | S1891 |
| RM6h, REM3d | none |

S1190 lies outside the q_* range (the G5 walk) and is checked with the RM-6 rows. Tree-wide, no sabotage
anchor matches 0 times at the tip: the same 12 pre-existing double-match rows remain, all in unrelated
files.

## Identity verdicts

OWED, one box-queue job per commit, each its own gate.

- **The command:** `scripts/emit_sweep.py --ref-bin <base e121371b2 build> --bin <commit build>`, run from an
  export of the base. It covers every stream (the .c streams 1-2 and 4, emit-ir, dumps and the facts stream
  6) over the corpus plus `bench_patterns.txt`. The verdict is `sae1_evidence/ident_check.py` against an
  EMPTY census, because a remodel has no mover.
- **The builds:** `$PCREC_TMPDIR/scratch/l1build/trees/{base,rm1,rm6,rm3}/build/pcrec`, each built from
  `git archive` of its commit.
- **The pass line:** `== ident_check COMPLETE: 0 unexplained`.

Measured before queueing:
- **Smoke:** emit_sweep over 20 corpus patterns (c-default, facts), base vs remodel 3: 0 movers.
- **The `\w`-class witnesses** (`l1build_evidence/wclass_heads.txt`, 14 patterns): each compared under byte
  and utf8 and on both engines, 56 comparisons. Base, RM-6 and remodel 3 give identical .c bytes.
- **FINDING 3: the `A_WCLASS` arm is UNREACHABLE at `anf_head` today.** A tracing plant on the arm in a
  scratch copy of remodel 3 printed nothing over all 28 compiles. altcls runs BEFORE the encoding lowering,
  so no `A_WCLASS` exists yet. The lowering's own altnf call hands byte-box branches, not `A_WCLASS` nodes
  (`src/opt/lower_enc.c` `lower_class_utf8`). So conf-spanarms8 (b)'s "a wall in altnf" is a wall no input
  reaches. Remodel 3's identity there holds by construction, and the sweep's `\w` witnesses cannot exercise
  it. The arm first matters to the feature's run walk, which runs on the lowered tree, where `A_WCLASS`
  is real.

## Deviations from the design

- **`req_set_maxoff`** is added to the census's expected movers (Finding 1).
- **RM-6 reads the column in derive.c's five combinator arms only.** The leaf kinds still return a literal
  `false`; their row value is NO, the same answer. The NEVER column is also asked of `A_LOOK` per node
  through `pcrec_ast_row`, which keeps "a row states the kind-level answer only" true. The alternative,
  making `A_LOOK` a NODE row, would leave the positive/negative split as hand code in every reader.
- **The NEVER propagation's design table (D-9) names "the run walk" as its second reader.** That reader
  arrives with the feature, not here, so only derive.c reads the column.
- **The anchor tool's new range groups** are in a lane copy (`firstunit_anchors_l1.py`). The r50 file under
  `docs/dev/reviews/` is unedited, as reviews are records.
- **One light probe exceeded the sweep cap** (RUNS.md: over 50 compiles is heavy). The 56-way `\w`-witness
  comparison (168 compiles across three builds) and its 56-compile plant runs were run outside `boxlock`,
  on a free box, for a few seconds each.
- **RM-1's identity is by construction AND owed by the gate:** no facts-writer anchor exists (D-5's READYL1-8
  (b): the map finds 0 there); the facts stream is the gate.

## Notes for the feature lane

- **The base for the feature** is this branch's tip. The census instrument is `census_l1.py`. Run it with the
  FEATURE build as well, to get the two-sided observed-vs-model compare §14.4 puts at the feature's gate. The
  script predicts only; add an `--observed WORK_PCREC` arm comparing `--emit-facts` rows, as census_e1.py
  does. Its EXPECT table already holds §14.4's rows, with `req_set_maxoff` added.
- **The head's per-kind rule is `pcrec_ph_node` (desc.h).** The run walk's AHEAD item calls it with a byte
  callback. A class is its rendered 256-bit byte set, and `A_WCLASS` IS a position at byte level, where the
  walk sees it after lowering. The CAT/ALT spines are folded by the walker with `pcrec_ph_cat`/`pcrec_ph_alt`.
  The REP arm is a wall until [REPEAT-RUN] R2 (CONFORM-9). The design's BEHIND reader (a group read as a
  reversed head through `pcrec_ph_alt`) is not built: it is the feature's one new desc.c function (D-10).
- **The never propagation is `pcrec_never_by_row(pcrec_ast_row(a).never, any, every)`.** The walk's
  `rr_cat`/`rr_alt`/T2/E-5i read it for `RbRuns.never` (D-9). The NODE kinds (REP by `m`, the empty-class
  leaf) need the walk's own code: `rn_count(ps) == 0` in `rb_class_into`'s out-of-domain branch, and the
  empty meet.
- **RM-1 gives `RbRuns` and `ReqRun` one stated empty value each.** The feature's new fields default there:
  `lg`/`rg`/`never` in `rr_unit`, `cons_lo`/`cons_hi` (L3) in `pf_req_run_none`. The two one-field copies
  stay the feature's own writes: `rr_rep_split`'s `o.tail` line, and `rb_rep_best_val`'s `never`
  (READYL1-8 (a)).
- **Exact sets vs cube hulls.** The model meets EXACT byte sets. §5.1 still says the guard is "the cube hull
  of the term's set". If the feature meets hulls, a guard term whose set is not a cube can predict a wider
  narrowing than the census assumed. The corpus movers above are all exact single bytes or `{a,b}`, so they
  are unaffected. Settle which (§5.2's notation says cubes, D187; positions are sets since [RUN-POS-SET])
  before writing `rn_meet`.
- **Sabotage ids: S3340-S3354 are untouched** (this lane added no row), so the feature has the whole range.
- **The A_WCLASS arm of the head rule** is reached first by the feature (Finding 3). Give it a witness and a
  plant there.
- **The register, for the manager:**
  - Row 5's derive.c pass is done by RM-6 (its status still reads "rides L1").
  - Row 27's status was updated in remodel 3's commit.
  - Row 19's event fires at the feature (`RB_ROW_EACH`).

## STATE AT HANDOFF

- **Commits on `lane/l1build`:**
  - `29149186e` census_l1.py (WIP);
  - `a4230e01e` RM-1;
  - `e7bb64748` RM-6;
  - `7581123e4` remodel 3;
  - this report's commit, with the evidence: census_l1.py final, census_summary.txt, census.tsv,
    firstunit_anchors_l1.py, anchor_map_base.txt and wclass_heads.txt.
- **Rulings file:** last applied **R1** (manager, 2026-11-19: proceed with the three remodels; the census
  verdict stated as above).
OWED: none (as the deliver file declares); the queued box-queue jobs below are this lane's gate runs,
listed for the manager to adjust per the brief.

- **Queued box-queue jobs** (owner `l1build`; scripts in `$PCREC_TMPDIR/scratch/l1build/jobs/`, outputs under
  `$PCREC_TMPDIR/scratch/l1build/`):

  | key | what | pass line or verdict |
  |---|---|---|
  | `l1build-ident-rm1` | RM-1's identity gate (`ident-rm1/`) | `== ident_check COMPLETE: 0 unexplained` |
  | `l1build-ident-rm6` | RM-6's identity gate | the same |
  | `l1build-ident-rm3` | remodel 3's identity gate | the same |
  | `l1build-mech-reaimed` | S1638 S1639 S1640 S1641 S1891, the re-aimed rows | each must read DETECTED: RED under its plant ([MECH-REACH]) |
  | `l1build-mech-bound` | the 15 RM-1 rows plus S899 S893 S1189 S1190 S904 | each at its declared expectation (S904 is declared UNREACHED) |
  | `l1build-test-compound` | the derivation's tests, `compound_drive.c` (RM-6's exercising gate) | make's verdict |
  | `l1build-test-cpset-structure` | the `[2b]` allowlist on `is_never_leaf` (RM-6) | make's verdict |
  | `l1build-test-core` | kindrow_check (also run by hand: 6/6) | make's verdict |
  | `l1build-test-altcls` | the altnf rules, S1891's witness file (remodel 3) | make's verdict |

  The two mech jobs and the sections run IN the worktree. Nothing in the worktree may be edited while they
  run.
- **Not owed by this lane:** `make test` (the full suite) and `make test-axes`; the brief's owed is none.
  The manager runs the full battery at merge.
