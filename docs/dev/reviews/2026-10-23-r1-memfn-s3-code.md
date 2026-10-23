# 2026-10-23 r1 — memfn S3 CODE critic round (D172 S3, commit 7e1caad08 + 34ee758a1)

The project's first blinded CODE critic round, run at Frank's request (2026-10-23): "we've been doing design critics but not code critics … Major pieces like this need a code critics round." Read-only critics, no fixes, reports only. Its learnings feed a future code-critic skill and main's coding / architecture / style guide.

## 1. Setup

- **Subject:** D172 S3 on `lane/memfn-s3w`: code commit 7e1caad08 (E-find, D-hors, cover by default, abi 83→84 provisional, the retirements) plus the test/pin follow-up 34ee758a1. Base is main c3ea619c3.
- **Known finding the critics were BLINDED to:** job 605's 24-pattern mover sample showed caseless literals up to 29x slower. The cause: E-find's find step renders only `memchr` (one byte) or a byte walk, so a two-member stop such as `{B,b}` lost the two-stream `memchr` find the default build used.
  - Denied files: s3_report.md Parts 4-6, s3_evidence/*605*, dev_journal.md, owner.md, the memfn journal and responses, and this review.
- **Blinding leaks, as disclosed:**
  - cc-tests read s3_report.md lines 1-47 (status headlines naming the foobar bar FAIL, not the caseless finding) and says it did not use them.
  - cc-design saw only `git log` subjects.
  - cc-perf and cc-quality report none.

| critic | model | lens |
|---|---|---|
| cc-design | opus | design compliance against window_site rev 3.2, D146/D147/D172 and the house rules (general mechanisms, first-match tables, row contracts, facts-not-methods) |
| cc-perf | opus | emitted code against what it REPLACES: both arms (default vs `--memfn=no-wf-find`) compiled over about 50 varied patterns, loops and asm read, no timing |
| cc-quality | sonnet | code quality against coding_guide.md: duplication, parallel mechanisms, tables vs if-chains, comments, constants, refusals, frames |
| cc-tests | sonnet | test and gate adequacy against learnings §3 and check-design lessons: populations counted, controls sharing a source, representativeness |

## 2. Did they catch it?

| critic | caught the find-form gap? | how |
|---|---|---|
| cc-perf (opus) | **YES, CONFIRMED with loops and asm** | Compared emitted search loops class by class. `(?i)hello`: the old arm leapfrogs two `memchr` calls; the new arm runs `while (!(s[c+3]==76 \|\| s[c+3]==108)) c++`, which gcc compiles to one byte per iteration. It ALSO found the SIMD kernels lost under `-fmemfn-simd`, and that this loss had been booked as a re-pinned floor (simd_floor_check 39→33) that nobody judged as a speed trade. |
| cc-design (opus) | **YES, CONFIRMED with the design quote** | Traced each phase-2 slot to its table. §2.2's PAIR row ("two-member cube … two memchr streams") is unreachable because `fd_find_form` maps only LIBC/WALK. Also found that Table B is asked a made-up question (offset 0, a `table_ref` nobody stated, contracts widened against "KEPT UNCHANGED"). |
| cc-tests (sonnet) | **PARTLY** | Its top gap was "caseless masked compare on the default path: no bar cell, findings-only sample", framed as a CORRECTNESS risk (a mask too strict) rather than speed. It also found the SIMD-on loss went silent for every previously SIMD-routed mover. |
| cc-quality (sonnet) | **NO** | Came closest at finding 7 (the LIBC branch trusts a one-member invariant held in another file) and finding 1 (E-find duplicates the floor's frame). It never asked what Table B would have chosen. |

## 3. Findings, consolidated by id (severity order)

| id | sev | finding | critics | disposition |
|---|---|---|---|---|
| C1 | HIGH | E-find renders only LIBC/WALK. Table B's PAIR row (two-stream `memchr`) and its SIMD row are unreachable, so caseless and two-value-cube stops get a byte walk, up to 29x slower (605). | design, perf, tests | FIX: Table B returns the deciding row's PICK, and E-find renders it (the design's own §2.2/§2.7). Frank: "We absolutely will." |
| C2 | HIGH | The SIMD loss was booked as a floor re-pin (simd_floor_check 39→33; rows.tsv fn-pair/vrun witnesses re-aimed to the deny arm), never judged as a trade. | perf, tests | PROCESS: a re-pin that LOWERS a performance-form count is a trade to judge, not a pin to move. Restore the floor after C1. |
| C3 | MED | Table B is asked a made-up question: offset 0, `table_ref=1` unstated, `MF_SPAN_BOUNDED`, layer fixed `CL_L_OFF`. FIND/PRES contracts widened (`KD_ALL`) to admit it. D1c can never fire. | design | FIX with C1: ask with (set, d*, stretch facts, layer) and keep the contracts unchanged. |
| C4 | MED | E-find is a Table E row the design does not have. window_site.md was never revised to record it (docs/design/CLAUDE.md requires a deliberate revision). | design | DOC: window_site rev 3.3 records E-find (OWED since the S3 rulings). |
| C5 | MED | Rules keyed on the REPORT label: `e_generic_holds` (`site_kind != REPORT`) and `select_arm`'s early return, against §0 "keyed on a stated fact, never on a label". | design | FILE: a frame fact ("the candidate is the answer"). Trigger: a second such consumer or the next MF_SITE_ABI event. |
| C6 | MED | D-hors is reachable only inside E-find, so it never serves native sites. §5.2's G1 over non-REPORT D-hors movers is vacuous. | design | FILE with C7. Trigger: S1's native D-hors count > 0. |
| C7 | MED | Table D is not a kit_table (a hand `if` in `wf_find_prepare`): no contract, trace or reach counter. Its row/basis fields are read by nothing. | design, quality | FIX: Table D becomes a declared kit_table, small and in S3's own code. |
| C8 | MED | The stop choice prices rarity only, not the scan method (`[Qq]uery` scans `{Q,q}` byte by byte where the old arm memchr'd 'y'). | perf | FOLD into C1's general form: one priced choice over (stop position × find method). Frank's E[sh] ruling is the same idea for D. |
| C9 | MED | E-find duplicates the floor's ASSIGN/NOP frame, the `({…})` skeleton and the position loop (`wf_find_use`/`wf_find_expr`/`wf_find_test` vs `wf_stmt`/`wf_expr`/`wf_test`). | quality | FIX: shared frame and prologue helpers. |
| C10 | MED | Population gaps: tiny/lookaround strata (≈70% of movers) have no bar cell; the sample is 24 rows; high bytes, NUL and utf8 are absent from G2 and the timing; G2 windows are ≤5 wide against an admission cap of ≈13. | tests | GATE: the sample is now part of the bar (main agreed). Widen G2's alphabet and width. Add high-byte and caseless cells. |
| C11 | MED | The census controls share a source: its expected set is "what NEW stamps cover", and it ignores .rxt options. | tests | FIX: pass .rxt options; count option-driven cover patterns. |
| C12 | MED | Horspool on dense uniform runs degenerates to shift 1 (`[a-z]{16}`) and discards the verify-fail position. | perf | MEASURE: E[sh] (Frank's ruling) covers admission. The run-skip resume goes to ideas.md. |
| C13 | LOW-MED | No plants on the shift VALUES, the C-run mask word, the WALK table or `fd_find_form`. | tests | FIX: 3-4 G2 plants. |
| C14 | LOW-MED | `e_find_holds` casts away const and writes `e->form` inside a predicate, re-run on every quiet ask. | quality | FIX: compute once in setup. |
| C15 | LOW | The `--list-axes` descs for cover, wf-find and wf-hors name architecture ("memfn kit", "E-find", "HORS_MIN"). | design | D174: reword. The listing is caller-visible. |
| C16 | LOW | The `--harness=kit-proof` lever is inert but still live code. | quality | FILE: removal with a trigger. |
| C17 | LOW | Smaller items: stale or missing headers, a 320-byte buffer literal, "wf-find" spelled in 3 places, find_groups on the query path, libc=1 declared even on Horspool text, the fd_find_form + define_sel stack chain (~7 KB). | quality, design | FIX in the C1 build where touched; otherwise file. |

**Compliant, as the critics confirmed:**
- Table A (A-mass, TIE rows) and Table C rows are declared.
- C-run groups go through runcmp.
- The shared hoisted bound and guards are reused.
- D-hors matches §2.5 exactly.
- The two denies are in place, and the OFF arm is DEF exactly.
- The retirements are clean, with symbol hygiene (MF_NS, statics).
- The _Static_asserts are present.
- HORS_MIN is a labelled provisional row.

## 4. Learnings for the code-critic skill

1. **The lens that compares emitted code against what it replaces, on both arms, caught the regression from code alone.** Generated-code projects need an emitted-artifact lens, not only a source lens.
2. **A design-compliance lens that traces every slot to its named table catches parallel mechanisms.** It needs the design doc and the house rules as inputs.
3. **The code-quality lens (sonnet) found real maintenance issues but missed the behavioural gap.** Source-level reading alone does not see emitted behaviour.
4. **The test-adequacy lens finds populations nobody counts.** Pair it with a rule: a lowered performance-form floor is a TRADE to judge.
5. **Blinding is worth doing, and it leaks through report headers and `git log`.** A skill should give critics a denylist AND a clean worktree at the subject sha, not the branch tip.
6. **Two opus critics with different lenses converged independently on C1.** At least one opus lens should be on emitted behaviour, one on design.
7. **The manager's own rulings are review subjects.** C1 entered through a lane recommendation the manager ruled through (the "FORM only" reading of the FIND slot). The skill should have critics check the rulings against the design too.

## 5. By-id completeness

C1-C17 each have a disposition. FIX items go to the C1 build brief: C1, C3, C7, C9, C11, C13, C14, C15, plus C17 where touched. GATE items are on the bar: C10. FILE items go to ideas.md / plan rows via main: C5, C6, C12 (run-skip), C16. The PROCESS rule C2 goes to main's guide. The DOC item C4 is window_site rev 3.3.
