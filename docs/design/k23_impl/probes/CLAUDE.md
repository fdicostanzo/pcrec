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
- `model.py` — the step count in CLOSED FORM, with its own validation.
  `--check` reproduces nine independently measured instances (all exact; the
  check is written so a nonzero difference is a refutation, not a residual);
  `--grid` reports where the law crosses the 10^6 default budget as a
  function of inner-range width, which is D27's black-box characterization
  turned into a function.
- `prune_proto.py` — the RECOMMENDED mechanism as a patch: clamp each
  cursor's greedy end to the last position from which the rest of the pattern
  can still fit. Carries three things that are findings rather than options:
  `--replicas` (an ASSUMPTION GUARD that makes it DECLINE shapes outside the
  two-level replicated form instead of silently mis-patching them — it was
  added after the randomized differential caught 44 wrong answers, see the
  note §11.1), `--placebo` (the throughput control: same sites, same
  instruction shape, minrest forced to 0, so "the clamp costs" and "inserted
  code moves the layout" are separable), and `--clamp-scan` (fold the clamp
  into the scan's own bound so forward work drops too — D49's metric).
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
- `head2head.sh` — baseline vs prune vs memo on one shape: steps, answers,
  emitted code size, gcc time, memo table size.
- `throughput.sh` — what the clamp costs on the common path, best-of-N, with
  the placebo arm.
- `archive.sh` — regenerate `../out/` with D35-style provenance headers.
  `--all` adds the two differentials (~45 min; run it in the background and
  poll the files).

Maintenance: update this file when probes are added or removed or their roles
change.
