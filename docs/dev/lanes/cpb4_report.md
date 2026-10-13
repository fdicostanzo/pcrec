# cpb4 — [COMPOUND] build step B4, the driver (lane report)

Lane cpb4 (opus), 2026-10-12, `lane/cpb4` from main `690dc4e03`. Design `docs/design/compound.md` rev 2.2
(§R2.2, §A.14, §F.1); rulings D163 + add. 1-6, D88 add. 1, callout alignment §14. **abi 76 -> 77.**

## What landed
- **Row table** (`src/core/compound.c`): `compound_rows[]` = `split`, pin-only, admission as listed
  conjuncts (A1-A3 PRE, A4/A5 POST); `compound_place[]` first-match; `pcrec_compound_rows_check` (trace
  build + unit drive with planted faults); `CompPart.groups` identity; the walk checks slot coverage and
  builds the shell. Every engine walks: A1 is the one engine gate.
- **Shell** (`src/gen/emit_compound.c`, `pcrec_emit_dfa`'s shell branch): P's prologue, stamps,
  residuals, rx_info, main; the parts spliced unrendered (K79); the controller `first-nonzero(F @ x,
  Q @ next_pos(x))` for `_search`, F at `ctx->pos` for the match pair.
- **ONE call-site code table** (`callsite_rows[]`, 8 rows, emitted only where the callee can return the
  code): a DFA guards-off part gets rows 1, 2 and the dead trap 8; INTERNAL propagates. Spec §4¶10/¶10a.
- **`drop-compound`** = `fit_rungs[]` row 5 (size, degrading, fof IN); every row states `FitSets.comp`.
  `PB_ONE_ATTEMPT` is an emission request (`PcrecEmitIn.bound`).
- **`<PREFIX>_COMPOUND`** on every artifact; stamp catalogue `src/gen/stamp_kinds.c`: pattern-level keeps
  P's value, machine string `"compound"`, count `-1`, `MEMFN_FORMS` the parts' union (new kind), an
  unclassified stamp an internal error in a shell.
- **Harness lever** (`--harness=no-compound`, `build/pcrec-harness`, hidden `pcrec_harness_compile`):
  full admission and caps, then the plain artifact stamped `"forced-off"`. Fence G7: one global under
  `pcrec_harness_`, no `lib/` declaration, widened grep. Namespace table (cli.md §1.6¶2): rows
  `parts` and `harness-lever`.
- **Spec:** match_api §1¶2, §3.7, §4¶10/¶10a, §6¶6a, §6.3.12; limits §8.4 row 0 + ¶1a; cli §1.6¶2/¶2a;
  abi_changelog 77; TOCs regenerated. **abi readers by grep:** codegen `ABI_EXPECT`, S693, match_api ×2,
  recursion-identity (B) self-pinned to `cd1d2d8f9` (the lane's last src commit).

## Gates (lane tip; box_hold present, so single sections only)
- **G1** `split.rxt` 105 blocks / 13,839 lines from libpcre2 10.46, rides test-corpus (70,235 cases, 0
  failed); `verify_split.py` 9,784 spans, 549 groups, 3,504 `mc`, 0 disagreements.
- **G2+G4** `check_split_diff.py`: 189 case-arms, 2,296,796 cells vs the lever and libpcre2, `.h` and
  `nm -g` identity; a call-site trap reports as SIGILL. **G3** `check_linear.py`: counted loads at k and
  4k, 26 rows, 0 violations (final-newline cells at today's rev-end cost). **G5** is B2's check.
- **G6** `landing_census.py` (ref = main): corpus 4,606 × 2, 97 admitted by ID (`admitted.tsv`), 2
  stamp-sized `_WHY` movers, 0 findings; bench 367: 0 admitted, 1 stamp-sized. Re-run on the final src.
- **G7** PASS; the lever property (`check_lever.py`, also test-axes' declared internal arm): 8,365 plain
  pairs byte-identical, 97 forced-off.
- **Decline controls** RE-DERIVED (`check_declines.py`, `compound_drive walk`, `declines.tsv`): 12 named
  controls, 114 candidates, A1=37 A2=2 A5=40 admit=44 refused=3.
- **Shell checks** (`run_shell_checks.sh`): call-site rows, both namespace rows, `drop-compound` at a cap
  between the compiler's own plain/compound sizes (15,706 / 30,911).
- **Green singly:** make, strict, compound, codegen, rxtsource, startset, registry, size, corpus, cli,
  reject, findings, spec-history, every memfn section, cand-oracle, fallback-table, prechecks,
  search-pinned, start-landing, tune-dial, anchored-match, premul-table, vm-frameless, dfa-uniform-fold,
  prefilter-collapse, entry-shape-identity, cpset-structure, definitions, examples, core,
  encoding-checks, possessify, rungselect, counterk, mrl, prefilter, altcls, island, vm.

## Findings
1. **§E.4 re-derived:** `(?<=^a)b|c$` and `(?<=\G)a|b$` decline at A1 (not A2); `^x|\n(?m)^b$` at A5;
   the A2 witnesses are `(?m)^a|b$`, `x(?m:^)a|b$` (no floor anchor killed); concat-sqli A5 as designed.
2. **CMP-11 has no DFA population:** every admitted P and Q stamp the same `_VALID_LB` (the twin's
   plant 2 gave Q no reach). S901 declared UNREACHED.
3. **Nine machine-stamp corpus sweeps needed a compound bucket:** one helper `tests/lib/compound_art.{sh,py}`;
   each sweep skips and counts, `run_dfa_stamps.sh`'s bucket holds the stamps. Four memfn stamp regexes
   now read the artifact's own prefix (no `__`, by the namespace table).
4. `mc` graduates from the keyword census (its arm had landed); the census awk now counts it (K35).
5. Caps are raise-only, so the drop-compound witness builds its own low-cap compiler.

## Sabotage S891-S910 (allocated by main), new mech arm `compound`
Hand-measured on the lane tip (fresh archive, plant, build, the row's arm): **16 DETECTED** (S892-S894,
S896-S900, S902, S903, S905-S910; S902's trap fires, 18 SIGILL case-arms); **4 UNREACHED** declared with
REACH probes (S891, S895, S901, S904). S627-S636 re-anchored for `FitSets.comp`.

## Owed / deferred
- **After box_hold lifts:** full make test, test-axes, recursion-identity, mech on S891-S910, S627-S636,
  S693: `build/sc/posthold.sh` (detached), log `build/sc/posthold.log`.
- Deferred: an `--emit-facts` compound listing; a D45 compile-CPU row for the walk; call_graph
  TABLE_ROOTS for `compound_rows[]`. Unreached arm: `MEMFN_FORMS`'s non-`"none"` union (no part emits a
  kit form today, even under `-fmemfn-simd`). plan.md's [COMPOUND] row is the manager's to update.
