# docs/design/k23_impl/probes/ — the K23 lane's instruments

Everything here is a MEASUREMENT instrument or a THROWAWAY PROTOTYPE, never
a candidate implementation. The prototypes work by patching already-emitted
C, so they measure the real lowering while leaving `src/` untouched.

Nothing here is built or run by pcrec's `make`.

Two standing conventions, both learned the hard way and both stated in the
files themselves:

- **`LC_ALL=C` in every shell probe**, against R24 M-F1's collation defect
  (a UTF-8 locale's `sort`/`uniq` merges strings differing only in
  punctuation — close to a worst case for a corpus of regexes). No probe here
  sorts today; the setting is kept so a later edit inherits it.
- **Every injected-source patch asserts that it landed**, exactly once, and
  fails loudly otherwise. A silent no-op patch would report 0 steps for every
  pattern, i.e. a free speedup — the check-design failure mode this project
  keeps rediscovering, a control sharing a source with what it controls.

## Files

- `steps.sh` — EXACT backtrack-resumption count for one pattern over many
  subject lengths. Emits with an effectively infinite step budget and adds a
  counter increment beside the budget decrement, i.e. at `engine_m4.md`
  §4.2's single charge point, so the number it prints IS the number the
  shipped budget would be compared against. One compile per pattern, one run
  per length.
- `work.sh` — FORWARD SCAN WORK beside the step count. Its header opens by
  saying what it is NOT: this is a LANE PROXY (one unit = one span-loop
  scan-body iteration), not D49's `RX_ERR_WORK` meter, whose charge sites do
  not exist in any matcher this lane can emit. It was written because R26
  M2/E6 found the note quoting work numbers that had no probe behind them at
  all.
- `model.py` — the step count in CLOSED FORM, with its own validation.
  `--check` reproduces nine independently measured instances (all exact; the
  check is written so a nonzero difference is a refutation, not a residual);
  `--grid` reports where the law crosses the 10^6 default budget as a
  function of inner-range width, which is D27's black-box characterization
  turned into a function; `--ratios` compares python's measured TIMES against
  the law's predicted NODE COUNTS across four size steps (R26 E8's argument,
  adopted — it is stronger evidence that python walks the same tree than the
  single wall-clock pair the note used to carry).
- `prune_proto.py` — the RECOMMENDED mechanism as a patch: clamp each
  cursor's greedy end to the last position from which the rest of the pattern
  can still fit, **rounded down onto the cursor's iteration lattice**
  (R26 E1 — an off-lattice clamp deletes the correct position from the choice
  set and is unsound, not merely loose; it answered `nomatch` on 5 of 8
  subjects of a stride-2 shape). Its flags are mostly findings rather than
  options:
  - `--replicas` — an ASSUMPTION GUARD that makes it DECLINE shapes outside
    the two-level replicated form instead of silently mis-patching them,
    added after the randomized differential caught 44 wrong answers (note
    §11.1).
  - `--no-lattice` — the SABOTAGE control that re-emits the pre-R26 unrounded
    clamp, so the stride/residue corpus can be validated in the failing
    direction. A corpus that does not go red under it is not testing the
    lattice rule.
  - `--placebo` — the throughput control: same sites, same instruction shape,
    minrest forced to 0, so "the clamp costs" and "inserted code moves the
    layout" are separable.
  - `--clamp-scan` — fold the clamp into the scan's own bound so forward work
    drops too; measured to land on exactly one forward pass.
  - `--prefilter-ceiling` — the R26 E4 prototype: use the DFA prefilter's
    match-END window (which `rx_search` computes and discards) as the clamp
    ceiling instead of the subject end. Closes the trailing-suffix residual
    entirely. Plumbs the window through a file-scope variable, which a real
    implementation may not do (TS-1) — it belongs in `rx_work`.
  - `--frames-sites` / `--minrest-py` — the TEST form at frames-rung
    iteration entries, and a per-site minrest for nesting deeper than two
    levels, where no single formula covers the site index.
- `memo_proto.py` — the competing mechanism as a patch: mark
  (program point, position) on arrival, fail on a second arrival. Its header
  carries the soundness argument (a pure DFS backtracker cannot revisit a
  state whose subtree succeeded) and its two conditions, one of which
  backreferences break. Reports its own table size, which is the point.
- `diff3.py` — the THREE-WAY differential: baseline pcrec vs pruned pcrec vs
  python `re`, comparing the FULL capture vector rather than the span.
- `cases_prune.tsv` — hand-chosen cases around the known boundaries, with the
  adversarial axes named inline (unanchored search that must skip bytes, a
  non-empty follow, trailing bytes the match need not consume, nullable and
  unit-minimum inners).
- `cases_random.tsv` / `gen_cases.py` — the seeded randomized sweep over the
  shape family. It exists because the hand-chosen corpus inherits the
  defect's own alphabet, and it is what caught this lane's prototype defect.
  **Its second version carries STRIDE and RESIDUE axes** (bodies of width 1,
  2 and 3; subject lengths that are not multiples of the stride; prefixes
  that shift the lattice origin), because the first version drew every body
  from a single-byte alphabet and so could not distinguish a correct clamp
  from a broken one — 855 cells blind to a real unsoundness. That is the
  note's own §11.1 lesson recurring against the generator that taught it, and
  §11.4 states the sharper form: randomising protects only the axes the
  generator can express.
- `head2head.sh` — baseline vs prune vs memo on one shape: steps, answers,
  emitted code size, gcc time, memo table size.
- `throughput.sh` — what the clamp costs on the common path, best-of-N, with
  the placebo arm.
- `archive.sh` — regenerate `../out/` with D35-style provenance headers.
  `--all` adds the two differentials (~45 min; run it in the background and
  poll the files).

Maintenance: update this file when probes are added or removed or their roles
change.
