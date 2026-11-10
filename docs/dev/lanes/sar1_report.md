# Lane sar1: span arms unit R1 (a repeat counts as its copies)

Lane sar1 (opus), 2026-11-09. Branch lane/sar1 in worktrees/sar1, based on lane/sae1 2d6ed9b9b (unit E1,
under code review; E1 sits on lane/u3mech, abi 98). Main is NOT merged in. Design:
docs/design/span_arms.md rev 2.2 §3, §6 (T2 rows 2-3), §8 row R1, §12, §12b Q1; D191 (Frank 2026-11-09,
"Go on build"; repeats count as their copies).

## Summary

- **Premise held.** `build/pcrec --emit-facts` on `xy(?:ab){2}zw` gave `req_whole_run 6162` at the branch
  point. It gives `7879616261627a77` (`xyababzw`) now.
- **T2 rows 2-3 are built as rows of E1's first-match table** (`rb_rep_rows`, `src/facts/req.c`). There is
  no second mechanism. The rows, first match:
  1. Width-0 body: E1's row.
  2. `rb_rep_exact` (`m = n`, `X{0}` included) -> `RB_REP_EXACT`.
  3. `rb_rep_any` -> `RB_REP_SPLIT`.
  4. Then today's best-only copy and the gap, reached only when an arm is restored.
- **Row 2's value** (`rr_rep_exact`): `X^c`, built by `rr_pow` as c copies through `rr_cat`. The width is
  always `rr_rep_w(m, w)`, never c·w, and the tail is placed from that width. `all` holds only when c = m.
- **Row 3's value** (`rr_rep_split`): the head and the best come from `X^c · gap`, the tail from
  `gap · X^c`. The width is exact. At c = 0 the row is today's gap.
- **The copy count** (`rr_pow_count`) is `c = min(m, sat)`. `sat` is 2 for a body that is not `all`, and
  `ceil(PCREC_MAX_REQ_RUN_SCAN / w)` for an `all` body of width w. It derives from the storage bound, with
  no constant of its own (§3.1 point 3).
- **The set is unchanged** (§3.3). A repeat keeps the body's members at `m >= 1` and none at `m = 0`, as
  before.
- **The pieces: a power combinator**, `pcrec_pd_pow` in `src/facts/desc.c`, applies cat k times. Its
  loop is bounded by the two description bounds, never by k:
  - A single-group description that already stores only its last `max_pos` positions gains width alone
    from each further copy. The shortcut adds that width in one step.
  - A description of two or more widths reaches `max_groups` (`PD_OVER`) within that many copies.
  - Only `X{m}` gets pieces; a variable repeat stays `pd_none` (§3.2).
- **The restore arm `rep`** is a new row in `src/facts/walk_arms.def`. It has its own comment block after
  E1's `EMPTY` row, so E2's `zero` row merges beside it. It restores today's forms: the best-only copy at
  `m >= 1`, and the gap.
- **No abi number, no scaffolding change expected.** Only the VALUES of facts and stamps move: the run,
  `RX_REQ_RUN`/`RX_REQ_BYTE`/`RX_REQ_HANDOFF`, and the pre-check choices that read them. The identity job
  is the check. If it shows scaffolding moving, that is a STOP per the brief.
- **Two existing pins moved with the run; both are re-aimed in this branch:**
  - `x{2,5}(?i:cat)`'s run is now `xxCAT` (K 3, was `CAT` at K 5).
  - Sabotage S463's reach probe now reads K 3. A plant re-check showed that it still detects
    (handoff.rxt, 185 red cells, (1,8) where (0,8) is expected).
  - In `tests/memfn/run_handoff_reach.sh`, the VM attempt-loop witness `x{2,5}(?i:cat)` is now a
    re-entered row (its run holds the set's `x`). `(ab)c?userpass`, a corpus pattern of
    handoff_vm.rxt, is the entry-only witness. 16/0 there.
- **Gates.** The census, the identity diff, make test, mech, and a full REACH_ONLY sweep are queued
  (STATE AT HANDOFF). The axes job is HELD by ruling R-AXES (the manager queues it).

## Census and movers

The census is a measurement record, not a build gate (D191).

**The instrument** is `docs/dev/lanes/sar1_evidence/census_r1.py`. It is census_e1.py's population and
observation code with a new MODEL of T2 rows 2-3. The model reads no compiler code:

- It SPELLS every quantified item whose body consumes as copies, using E1's scanner width-0 test (width-0
  bodies are E1's and already in the reference):
  - `X{m}` -> m copies of `(?:X)`; `X{0}` is deleted.
  - `X{m,n}`/`X{m,}`/`X+`, m >= 1 -> `X^m (?:X){0,n-m} X^m`.
- It asks TODAY's compiler for the spelling's run and pieces.
- Why the double `X^m` is faithful for run BYTES: the run never crosses the gap. So the spelling gives
  exactly row 3's head (`X^m` then the gap) and tail (the gap then `X^m`). Offsets are not compared.
- It abstains, and lists the pattern, on:
  - `(?x)`;
  - a named group in a copied body;
  - a capture in a copied body when the pattern refers to groups;
  - a quantified non-ASCII literal byte;
  - a quantifier after `\E`;
  - a spelling over 20000 bytes.

**The two-sided compare** is census_e1.py's, plus:

- the PIECES (`req_pieces` value) beside the run, per encoding;
- a TIE class: two runs of equal information (`popcount` of the masks) but different bytes. The walk
  breaks such ties by its own order (F22). Ties are listed apart from value mismatches.
- a PIECES-WHY class: both sides list `none`, for another drop reason. The power is described before its
  right neighbour's wall is met; the spelling meets the wall first. For example, `(a.){10}xyz` under utf8
  now reads `decline:over-bound` where it read `decline:not-fixed-width`. This is the listing's why only.
  These patterns stay identity movers.
- a list of the facts whose VALUE or WHY moved, apart from those whose `used` column alone moved.
  - Example: `ab{2,}c`'s `req_set` is unchanged in value. A pass now asks for it, so its `used` column
    moved.

**Smoke run** (13 patterns: the R1 witnesses, `ab{2,}c`, `(?:\b)+xy`, and one bench-shaped
`x{2,5}(?i:cat)`):

- 9 movers, 9 predicted, 0 value mismatches, 0 ties, 0 two-sided differences.
- 2 PIECES-WHY patterns: `(a.){10}xyz` and `(?:a.){10}.?xyz` under utf8.
- 4 pieces value movers, every one an exact repeat.
- The facts whose value moved: `req_whole_run`, `req_run`, `req_run_maxoff`, `req_byte`,
  `req_landmark_maxoff`, `run_pin`, `req_pieces`.

**Measured by hand against the design's §3.4 table** (`--emit-facts`, byte):

| pattern | value |
|---|---|
| `A{4}` | `AAAA` |
| `ab{3}c` | `abbbc` |
| `xy(?:ab){2}zw` | `xyababzw` |
| `(?i)xy(?:ab){2}zw` | 8 cube positions |
| `abcd(?:ab\|Ab){2}efgh` | 12 positions |
| `xy(?:abc\|abd){2}zw` | `xyab` |
| `x(?:a[bc]){2}y` | 6 positions |
| `(?:abc){20}` | 32 positions (11 copies) |
| `xy(?:ab){0}zw` | `xyzw` |

- Unchanged, as the table says: `xy(?:ab){0,2}zw`, `xy(?:ab)*zw`, `[0-9]{4}`.
- `(a.){10}xyz` and `(?:a.){10}.?xyz` keep K 20 and 21.
- Two of the table's cells are TIES that the walk breaks the other way:
  - `xy(?:ab){2,3}zw` lists `ababzw` (the table says `xyabab`, 6 either way);
  - `xy(?:ab)+zw` lists `abzw` (the table says `xyab`, 4 either way).
  - §3.6 names this tie class (F22).

**The full census is OWED** (job `main-sar1-census`):

- Population: the corpus (`--list-source` over tests/**/*.rxt) plus every pcrec-bench pattern file
  (bench/*/patterns/*.rx, read-only).
- Output: `$PCREC_TMPDIR/scratch/sar1/census/summary.txt`, which ends `== census COMPLETE: N movers,
  M two-sided differences`, and `census.tsv`.
- The stop rule (no mover anywhere) cannot fire: the corpus witnesses alone move. Whether a BENCH cell
  moves is the census's own finding; its summary line counts bench movers.

## Identity

- **The B0 identity diff is OWED** (job `main-sar1-ident`). It runs `scripts/emit_sweep.py` with every
  stream over the corpus and E1's bench pattern list, the reference being the branch point (E1's build,
  `$PCREC_TMPDIR/scratch/sar1/ref`). The verdict is E1's `docs/dev/lanes/sae1_evidence/ident_check.py`,
  reused unchanged on R1's census.tsv:
  - every argv-stream mover is a census mover;
  - every composition mover's source holds one;
  - no dumps mover and no asymmetric row;
  - the facts-stream movers equal the census's.
- The completion line is `== ident_check COMPLETE: 0 unexplained`.
- A census mover classed PIECES-WHY is still a census mover in census.tsv. ident_check therefore counts it,
  and the facts stream must list it.

## Witnesses and sabotage

**Witnesses** are in `tests/litscan/spanarms.rxt`, inserted after E1's W-R4 so that E2's appended blocks
merge cleanly:

- Each block runs on the default route and again under `engine vm`.
- Every cell is libpcre2-8 10.46's (`tests/lib/p2probe.c`; 80 cells probed, 0 differ).
- The file is 142/0 under the harness.

| witness | pattern | role |
|---|---|---|
| W-R1 | `xy(?:ab){1,2}zw` | answers |
| W-R2 | `xy(?:ab){1,3}zw` | answers |
| W-R3 | `ab(?:cd){0,2}ef` | answers |
| W-R5 | `(?:abc){20}` | answers; its detector is the listing |
| W-R6 | `(a.){10}xyz` (VM, K 20) | answers |
| W-R6 DFA twin | `(?:a.){10}.?xyz` (K 21), with `ns 2` | answers |
| mover | `xy(?:ab){2}zw` | answers |
| mover | `xy(?:ab){0}zw` | answers |
| mover | `x(?:a[bc]){2}y` | answers |
| mover | `(?:ab){1,2}cd(?:ef){1,2}` | the run `abcdef` joins two repeats |

**Listing check `[facts-rep]`** (new section of `tests/codegen/run_facts_checks.sh`, 9 cells, 12/0 for the
whole file):

- `xy(?:ab){2}zw` lists `xyababzw`. Under `--harness=restore=rep` it lists `6162` with `harness:rep` on
  `req_whole_run` and `req_pieces`, and none on `req_set`.
- W-R5's 32 positions.
- `(?:a|bc){2}`'s three pieces, and `none` under `rep`.
- `(?:ab){20}(?:c|de)`'s pieces at widths 41 and 42.
- A variable repeat's `decline:not-fixed-width`.
- All expectations are by hand from T2 and the description's cat; the derivations are in the section's
  comment.

**Sabotage rows** S1915-S1921 are used; S1922-S1924 are unused. Every row was detected by a MANUAL plant
on this branch (plant, build, its detector, revert; script `$PCREC_TMPDIR/scratch/sar1/plant.sh`), and
every REACH probe prints its token on the unplanted build:

| row | planted error | detected by |
|---|---|---|
| S1915 (W-R1) | row 3 sets `all` | harness spanarms.rxt, 20 red |
| S1916 (W-R2) | unrolls `n` copies | harness, 14 red |
| S1917 (W-R3) | c from max(m, 1) | harness, 4 red: W-R3 on both engines; W-R4 also fails |
| S1918 (W-R5) | copy count one short | [facts-rep] (30 positions) |
| S1919 (W-R6) | width of the c unrolled copies | harness, 8 red, VM and DFA witnesses |
| S1920 | `pcrec_pd_pow`'s shortcut adds no width | [facts-rep] (widths 33/34) |
| S1921 | the exact row carries no `rep` arm | [facts-rep] (restore=rep keeps the new run) |

- The lever fence (`tests/compound/run_lever_fence.sh`) allows S1921, whose reach probe names the lever.
  The fence PASSES.
- `VALIDATE_ONLY` passes for all 7 rows.
- **Reach sweep by hand:** I ran the REACH probes of the 83 rows that mention the run, the byte, the
  handoff, the landmark or the pin, on the lane build. One row was UNREACHED, S463, and it is re-aimed
  (above). On the branch point, only this lane's own new rows fail, as they should.
- **The official mech verdict** (job `main-sar1-mech`, S1915-S1921 plus the re-aimed S463) and the full
  REACH_ONLY sweep (`main-sar1-reach`, 1209 rows) are OWED. If the sweep reads red, compare it against a
  REACH_ONLY run of the base before blaming this branch: I have not measured whether the base itself
  reaches every row.

## Spec and listing hunks

- `docs/spec/tuning.md` §2.28¶3 (how the run is derived): "nothing is joined across a repeat's iterations
  (`(?:ab){2,}` reports `ab`)" is replaced. The new text:
  - a repeat counts as the copies every match takes, joined to each other and to their neighbours
    (`xy(?:ab){2}zw` reports `xyababzw`, `(?:ab){2,}` reports `abab`);
  - the copies a match may add beyond them break contiguity;
  - a zero-iteration quantifier of a CONSUMING body breaks it. The qualifier "of a body that consumes"
    also states E1's row-1 exception, which E1 left unspoken in that sentence.
- `docs/spec/facts_listing.md`:
  - §4.1.2¶8c (`req_pieces`): "a repeat" becomes "a repeat whose count varies". An exact repeat is its m
    copies (`(?:a|bc){2}` lists three pieces).
  - §4.1.3¶4a: the `harness:` token sits on `req_whole_run`/`req_pieces` for the arms `empty` and `rep`,
    and `rep`'s meaning is added. The lever's spelling is not named (the fence greps docs/spec).
- spec_history check: 11/0.
- **Listing movers (advisory, facts_listing §1):**
  - `req_whole_run` and the facts derived from it move as above;
  - `req_pieces` moves for exact repeats only, plus the PIECES-WHY drop-reason class above;
  - `req_set`'s value does not move, but its `used` column can.
- CLAUDE.md updated in src/facts (rows, `pow`, anchors) and tests/litscan (spanarms entry). Both pass the
  size check at commit.

## Checks run

By hand, on the lane build:

| check | result |
|---|---|
| `nice make -j4` | clean |
| `make strict` | clean |
| `tests/litscan/spanarms.rxt` under the harness | 142/0 |
| `tests/codegen/run_facts_checks.sh` | 12/0 (incl. [facts-rep] 9 cells, [facts-arm], [facts-pieces]) |
| `tests/memfn/run_handoff_reach.sh` | 16/0 |
| `tests/compound/run_lever_fence.sh` | PASS |
| `tests/spec_history/run_spec_history.sh` | 11/0 |
| mech `VALIDATE_ONLY` | 7/7 |
| manual plants | 7/7 detected, plus S463's re-check |
| reach probes | 83-row subset, all reached after the S463 re-aim |
| census smoke run | 13 patterns, 0 two-sided differences |

Every expected answer was checked against libpcre2 10.46 (80 cells).

NOT run by hand: make test, the full census, the identity diff, test-axes, the mech matrix, the full REACH
sweep. These are the owed jobs below.

## STATE AT HANDOFF

- **Commits on lane/sar1:**
  - 6ab200b3c: code, witnesses, [facts-rep].
  - e92a4bf93: sabotage rows, spec, axes arm, fence, CLAUDE.md.
  - 4bcb40533: S463 and handoff-reach re-aims.
  - The census tool commit.
  - This report's commit.
- **Base:** lane/sae1 2d6ed9b9b.
- **Rulings file** `docs/dev/lanes/sar1_rulings.md`: the last entry applied is **R-AXES** (manager,
  2026-11-09).
  - I had queued `main-sar1-axes` before reading R-AXES. It was CANCELLED by hand, and `mech` was
    re-queued to follow `maketest` instead of `axes`.
  - The axes job script is ready for the manager at `$PCREC_TMPDIR/scratch/sar1/jobs/axes.sh`, key
    `main-sar1-axes` (`AXES=--harness=restore=rep make test-axes`). It needs E1's compound-lever fix
    (lane sae1fix) merged into lane/sar1 first.
- **OWED queue jobs** (job scripts in `$PCREC_TMPDIR/scratch/sar1/jobs/`). Each is hold-aware: no start
  from 19:00 to 01:00, and none starts before the kit's `kit-u2-mech4` ends and E1's `main-sae1-mech` is
  green.

| job | what | completion line | log |
|---|---|---|---|
| `main-sar1-census` (210) | census_r1.py over the corpus and the bench | `== census COMPLETE:` | `scratch/sar1/census/summary.txt` |
| `main-sar1-ident` (211) | emit_sweep plus ident_check | `== ident_check COMPLETE: 0 unexplained` | `scratch/sar1/ident/` |
| `main-sar1-maketest` (212) | make strict, then make test via perfrun (PC-3 included) | make's `*** [test-` lines | `scratch/sar1/maketest.log` |
| `main-sar1-mech` (214) | S1915-S1921, S463 | `== mech run COMPLETE: 8 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0` | `scratch/sar1/mech.log` |
| `main-sar1-reach` (215) | REACH_ONLY over all 1209 rows | `== mech run COMPLETE` with unreached 0 | `scratch/sar1/reach.log` |

- **Open for the manager (reply either way):**
  - Are the two TIE cells of the §3.4 table (`ababzw` for `xyabab`, `abzw` for `xyab`) acceptable as
    listed? They are the walk's own tie order. The design's table names the other member, and §3.6 says
    the build's tie-break picks one.
  - Are the PIECES-WHY movers (a drop reason changes from `not-fixed-width` to `over-bound` under utf8)
    acceptable as advisory listing movers, rather than ordered so that the wall's reason wins?
- **Known limits:**
  - The restore lever does not reach compound parts (E1's, being fixed by sae1fix).
  - `RbRun.trunc` is not set on a head that stores exactly 32 bytes of a longer exact repeat (c < m with w
    dividing 32). `all` is forced false there. `trunc` has no reader outside the walk, and `all` false
    stops every join it would guard.
- No kit facts to relay: the seam is unchanged and only carries longer runs. No memfn/ edits. No D, K or R
  numbers taken.
