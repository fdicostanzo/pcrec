# Lane `cmprev4` report: `compound_entries.md` revision 4 (D163 addendum 8)

Lane `cmprev4`, 2026-10-16, branch `lane/cmprev4` from main `8eec6f874` (abi 78). DESIGN
TEXT plus scratch-grade compile-only size probes. Nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/`.

## What was asked

Revise `docs/design/compound_entries.md` from revision 3 to revision 4 per D163 addendum 8.
The part layout becomes caller-settable controls finer than the five positions. The positions
become presets (declared rows of switch settings, first-match). An explicit control overrides
the preset. The lane was to:
- propose the grain;
- tie it to revision 3's P/T rows;
- give each control's size and speed direction;
- reframe Q7-Q9 (Q6 is ruled);
- name the spec home, with D80 hunks owed at E1;
- apply the NEW-DATASET lens;
- add §R4 with a change map.

## What revision 4 says (read the note's §R4 first)

- **Three VALUED controls** (§3.2.2). None is a flag bit.
  - `--part-layout=CLASS:V` takes one value per class: `auto` (the owner's `0` layout), `shared` or `inline`. The classes are `prefilter`, `compound`, `find` and `wrap`.
  - `--part-inline-rank=R` takes `none`, `R3`..`R0` or `measured`; only `measured` reads `θ_hot` from the set. This is θ_hot's direct manual setting.
  - `--part-residual=V` gives the layout of every part that neither a class value nor the threshold decided.
  - The owned VM entry chain keeps its existing control, `--vm-entry-shape=N`. It is not respelled; unlock U-B would join the spellings.
- **The grain argument** (§3.2.3) keeps the manager's leaning (class plus threshold) and adds the residual mode. Without the residual, `−1` and `+2` would need presets that set class values. A class value set by a preset would then have to LOSE to the threshold, while a caller's class value would have to WIN, so the order would depend on where a value came from. With the residual, no preset sets a class value, and one fixed row order serves every source.
  - Rejected: one switch (that is the positions); per function (names are pattern-dependent); rank only (it cannot separate prefilter from `find`); class only (it cannot cut across classes by hotness).
  - A size cutover is FILED as U-S. The inlined copy's object bytes are 0.55× to 1.75× the source body's, so a cutover would need a measured conversion.
- **The presets** (§3.2.4) are new columns of `tune.c`'s `TUNE_TABLE` (contract: tuning.md §5.4). Every cell is `†` or em-dash today.

  | position | preset row |
  |---|---|
  | `−2` | residual `shared` |
  | `−1` | residual `shared` + rank `R3` |
  | `0` | nothing |
  | `+1` | rank `measured` |
  | `+2` | residual `inline` |

  Each control resolves to the caller's value if set, else the preset's, else unset.
- **The tables** (§3.4).
  - The artifact table: K resolves the controls. T1/T2 are Q6's ruled declines, now keyed on the threshold VALUE `measured`. T0 is the all-trivial short cut. T3 runs per part.
  - The part table: P1-P3 are the unchanged constraints, then P4-P6 (class value), P7 (rank ≥ threshold), P8-P10 (residual). A column translates revision 3's rows.
  - P1/P2 are HARD and P3 is a MEASURED POLICY row. No control overrides any of the three.
- **A held request** is a selection outcome, never a refusal (§3.4.2, tuning.md §2.21¶3's rule).
  - It is stamped `CLASS=V/held` (or `/none` when the class has no subject).
  - It is listed per part in a new `--emit-facts` section and counted in E1's census.
- **Stamps** (§3.4.1).
  - `<PREFIX>_PART_LAYOUT` RETURNS. Revision 3 dropped it because the position determined the layout; it no longer does. It is written only when T3 fires, so no default artifact moves.
  - `_THETA` is folded into its `rank=R@set` token. `_WHY` stays.
  - Both are caller-observable from E1, so their D80/D94 work is E1's, not E1′'s.
- **Checks** (§3.6) are keyed on the RESOLVED controls.
  - Every row is reachable at E1 by flags on corpus artifacts. Revision 3's UNREACHED stamp arm is now reached, against the no-control build.
  - New checks: preset resolution, against tuning.md §5.4's text; a precedence fixture; held reporting; answer identity of the controls in `test-axes`, tiered like `--vm-entry-shape`.
- **NEW-DATASET** (§3.9): every new item names its home and its owed spec section.
  - tuning.md new §2.51-§2.53, §4 mirror rows, §5.3 stamps and §5.4 preset rows.
  - cli.md: a new §1.x, plus §1.1.4 (per-class file-wins), §2.4 and §2.11.
  - match_api.md §6.3 and §8.2.
  - registry.md §6.
- **Q7-Q9 reframed** (§5.5).
  - Q7: keep the static rank, now caller vocabulary. U9 is re-shaped as a new threshold VALUE so a typed `R1` keeps its meaning.
  - Q8: it is now one preset cell. Leaning `auto`, because "hot inline, cold shared" is one flag away.
  - Q9: check per ROW through flags on corpus artifacts. Use synthetic witnesses only where the corpus has no subject. Explicit controls are live at E1 while preset cells stay `†`, on `--vm-entry-shape=N`'s precedent.

## Measured (scratch-grade: one run, compile-only, gcc 15.2 `-O2`, x86-64, this box; no clock)

`docs/design/compound_entries/rev4_osize.py`, `rev4_osize_cls.py`, `rev4_vmshape_o.sh` →
`results/rev4_*.tsv`:

| control | `.text` | `.o` |
|---|---|---|
| `prefilter:inline`, `(a)b` | +64 B (+4.4%) | +160 B |
| `prefilter:inline`, `(foo\|bar\|baz\|qux\|quux)\d+` | +320 B (+8.9%) | +352 B |
| `prefilter:inline`, `([a-z]+)@([a-z]+)\.com` | +704 B (+17.9%) | +1,112 B (+12.4%) |
| `prefilter:shared` | 0 where gcc already keeps it out of line; held by P3 elsewhere (it would cost +128 B) | |
| `compound:` any | 0 (every member held: F by P2, Q by P3) | |
| owned `--vm-entry-shape` `plain` → `inline` | +40% / +70% / +86% on three VM witnesses | +7.7% / +22.6% / +23.7% |
| `-fPIC` | prefilter deltas identical | |

Every time effect is UNMEASURED (instruction counts from revision 1 only).

## Findings for the manager

- **F-7**: `findall_iter.md` rev 2 §2.2 cites revision 3's position rows (P4/P6/P7/P8/P9). Translation: §3.4's last column. Not edited here.
- **F-8**: the value parameters have no single-source table. Eight with this note. Unlock U-V proposes one (`axes.def`'s sibling), filed, not scheduled.
- **F-9**: the largest `.o` lever is the owned VM entry chain, which already has a control (`--vm-entry-shape`).
- **E1's abi** (§5.1): ONE abi event, because the stamp vocabulary moves (D94 readers), although no default byte moves (the manager's reading, 2026-10-16).
- **Sabotage**: S999-S1008 are re-aimed. THREE NEW plants (precedence ×2, held marker; §3.6) take S1035-S1037, in the doc's table order.

## Validation

Design text only. The probes ran (outputs committed); `make` built the worktree's
`build/pcrec` for them. `make test-spec-history` 145/0 (its first run caught two citations of the unborn tuning.md section for `--part-inline-rank=`; reworded). No other suite was run or is owed: nothing under `src/` changed.

## Resume point for a follow-up

The note is ready for a panel or a ruling. Open items:
- Q7-Q9 (discussion form, with leanings);
- three sabotage ids;
- the E1 abi reading;
- U-V and U-S, filed with triggers.
