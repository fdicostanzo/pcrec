# cpb4 — [COMPOUND] build step B4, the driver (lane report)

Lane cpb4 (opus), 2026-10-12, branch `lane/cpb4` from main `690dc4e03`. Design: `docs/design/compound.md`
rev 2.2 (§R2.2, §A.14, §F.1); rulings D163 + add. 1-6, D88 add. 1, compound_callout_alignment.md §14.
**abi 76 -> 77.** B3 had not merged when this report was written, so the brief's re-pin to 78 did not apply.

## What landed
- **The row table** (`src/core/compound.c`). `compound_rows[]` has one row, `split`, pin-only. Its admission
  is a list of conjuncts `CompConj{id, phase, holds, reads}`: A1-A3 PRE, A4/A5 POST. `compound_place[]` is
  a first-match placement table. `pcrec_compound_rows_check` is the table self-check: it runs in the trace
  build and in the unit drive, which also feeds it planted faults. `CompPart.groups` is identity for
  split. The walk checks slot coverage and builds the shell.
- **The walk** runs in `compile_driver`'s attempt, after the machines are built. Every engine walks:
  A1 is the only engine gate, so the call site has no second DFA test.
- **The shell** (`src/gen/emit_compound.c`, `pcrec_emit_dfa`'s shell branch). It keeps P's prologue,
  stamps, residuals, rx_info and main, then adds the parts (spliced unrendered, K79) and the controller.
  The controller is `first-nonzero(F @ x, Q @ next_pos(x))` for `_search` and F at `ctx->pos` for the
  match pair.
- **ONE call-site code table** (`callsite_rows[]`, 8 rows). A row is emitted only if the callee can
  return its code. A DFA, guards-off part gets rows 1, 2 and the dead trap (row 8). `PCREC_ERR_INTERNAL`
  propagates. The match_api.md §4¶10 hunk is in this change.
- **`drop-compound`** is `fit_rungs[]` row 5 (FIT_L_SIZE, degrading, fof IN). Every row now states its
  `FitSets.comp` cell. `PB_ONE_ATTEMPT` is now an emission request (`PcrecEmitIn.bound`).
- **`<PREFIX>_COMPOUND`** is on every artifact. The stamp catalogue (`src/gen/stamp_kinds.c`) puts each
  stamp in one kind:
  - pattern-level stamps keep P's value;
  - machine strings read `"compound"`, machine counts `-1`;
  - **`MEMFN_FORMS` takes the parts' union** (new kind; spec §6.3.12);
  - a stamp with no kind is an internal error in a shell.
- **The harness lever** (`--harness=no-compound`, `build/pcrec-harness`, hidden
  `pcrec_harness_compile`). It runs the full admission and caps, then re-emits the plain artifact stamped
  `"forced-off"`. Its fence (G7) has three checks:
  - exactly one global under `pcrec_harness_`;
  - no `lib/` declaration of it;
  - the widened grep with its allowlist.
- **Namespace table** (cli.md §1.6¶2): row `parts` refuses `__`; row `harness-lever` refuses the
  reserved prefix.
- **Spec:** match_api.md §1¶2, §3.7, §4¶10/¶10a, §6¶6a, §6.3.12; limits.md §8.4 row 0 and ¶1a; cli.md
  §1.6¶2/¶2a; abi_changelog 77. The TOCs were regenerated.
- **abi readers, found by grep:**
  - codegen `ABI_EXPECT`;
  - S693 re-aimed;
  - match_api in 2 places;
  - the recursion-identity (B) pin, self-pinned to `cd1d2d8f9`.

## Gates (all green on the lane tip, box_hold present: single sections only)
- **G1** `tests/compound/split.rxt`: 105 blocks, 13,839 lines, written from libpcre2 10.46. It rides
  test-corpus (70,235 cases, 0 failed). `verify_split.py` re-asks 9,784 span cells, 549 groups and 3,504
  `mc` lines: 0 disagreements.
- **G2+G4** `check_split_diff.py`: 189 case-arms, 2,296,796 cells. It compares the compound against the
  lever and libpcre2, plus `.h` and `nm -g` identity. A call-site trap now reports as SIGILL.
- **G3** `check_linear.py`: counted loads, k and 4k, 26 rows, 0 violations. The final-newline cells are
  gated at today's rev-end cost.
- **G5** is B2's check (`check_derive.py`). **G6** `landing_census.py`:
  - corpus 4,606 × 2: 97 admitted by ID (`admitted.tsv`), 2 stamp-sized `_WHY` movers, 0 findings;
  - bench 367: 0 admitted, 1 stamp-sized.
- **G7** `run_lever_fence.sh` PASS. The lever property (`check_lever.py`, also a declared internal arm of
  test-axes): 8,365 pairs plain and byte-identical, 97 forced-off.
- **Decline controls** (`check_declines.py` + `declines.tsv`): RE-DERIVED with `compound_drive walk`,
  12 named controls and 114 candidates; A1=37 A2=2 A5=40 admit=44 refused=3.
- **Shell checks** (`run_shell_checks.sh`):
  - the call-site rows;
  - both namespace rows;
  - `drop-compound`, under a cap between the compiler's own plain/compound sizes (15,706 / 30,911).
- **Sections run singly and green:** make, strict, test-compound, test-codegen, rxtsource, startset,
  registry, size, corpus, cli, reject, findings, spec-history, every memfn section, cand-oracle,
  fallback-table, prechecks, search-pinned, start-landing, tune-dial, anchored-match, premul-table,
  vm-frameless, dfa-uniform-fold, prefilter-collapse, entry-shape-identity, cpset-structure,
  definitions, examples, core, encoding-checks, possessify, rungselect, counterk, mrl, prefilter,
  altcls, island and vm. The remaining sections are owed to the full run.

## Findings
1. **§E.4's decline list re-derived, as the brief asked.**
   - `(?<=^a)b|c$` and `(?<=\G)a|b$` decline at **A1**, not A2.
   - `^x|\n(?m)^b$` declines at A5.
   - The A2 witnesses are `(?m)^a|b$` and `x(?m:^)a|b$`: no floor anchor is killed.
   - concat-sqli is A5, as the design says.
2. **CMP-11 has no DFA population.** Every admitted P and Q stamp the same `_VALID_LB`: the twin's
   plant 2 gave Q no reach. S901 is declared UNREACHED.
3. **Nine machine-stamp corpus sweeps needed a compound bucket.** One helper now answers for all of
   them: `tests/lib/compound_art.{sh,py}`. Each sweep skips and counts compounds, and
   `run_dfa_stamps.sh`'s bucket holds their stamps. The memfn stamp regexes read the artifact's own
   prefix: no `__`, by the namespace table.
4. `mc` was in the keyword census, but its arm had landed. It graduates, and the census awk now counts
   it (K35: zero `mc` lines until split.rxt).
5. A cap below the built-in limit is refused (raise-only), so the drop-compound witness builds its own
   low-cap compiler.

## Sabotage rows S891-S910 (allocated by main), new mech arm `compound`
Hand-measured on the lane tip (fresh archive, plant, build, the row's arm):
- **16 DETECTED:** S892-S894, S896-S900, S902, S903, S905-S910.
- **4 UNREACHED**, declared with REACH probes: S891, S895, S901, S904.
- S627-S636 re-anchored for the new `FitSets` cell.

## Owed / deferred
- **After box_hold lifts:** the full make test, test-axes, recursion-identity, and mech on S891-S910,
  S627-S636 and S693. The chain is `build/sc/posthold.sh`, log `build/sc/posthold.log`.
- **Deferred:**
  - an `--emit-facts` compound listing;
  - a D45 compile-CPU row for the walk;
  - call_graph TABLE_ROOTS for `compound_rows[]`.
- **Unreached arm:** the `MEMFN_FORMS` union's non-`"none"` path. No compound part emits a kit form
  today, even under `-fmemfn-simd`.
