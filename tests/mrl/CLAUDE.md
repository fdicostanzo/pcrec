# tests/mrl — [M4.6d] MINIMUM-REMAINING-LENGTH pruning

MRL pruning is K23's fix of record (D51 ruling 1; design:
`../../docs/design/k23_impl/k23_design.md`, build outcome in that note's
§14). At every point where the emitted VM commits to a subject position it
knows a compile-time lower bound on the bytes any accepting continuation must
still consume; a position with fewer bytes left is provably doomed and is cut
before a choice point is pushed for it.

Three instruments, seeing three different things, none substituting for
another — the shape `tests/possessify/` established and `tests/rungselect/`
and `tests/counterk/` inherited:

- the `.rxt` corpus — what each pattern MATCHES, oracle-verified;
- `run_mrldiff.sh` — that the pruned build and the `-fno-length-prune` build
  AGREE, over a subject sweep, on span + every capture slot + the failure
  surface;
- `run_mrl_tests.sh` — that the bound is EMITTED where the stamp says and
  nowhere when denied, that D51 ruling 2's three obligations have code behind
  them, and that K23 actually COLLAPSED.

## The `.rxt` corpus is D27-BLINDED, and that is the thing to know first

Every `.rxt` file here was written by an author DENIED `src/`, the rest of
`tests/`, the design notes and the git history — working in a
`scripts/mk_d27_cell.sh` cell against a prebuilt binary, from a one-page
statement of what MRL PROMISES and nothing else. That is D27's rule, applied
to the fix for a defect D27 itself found.

**It paid, immediately and in the way D27 predicts.** The author's family 10 —
`(a{1,3}){65}`, a shape the plan row specifically owed them — FAILED against
the build lane's first implementation: 32 cases returning `RX_ERR_STEPS` where
the promise says the matcher must answer. The cause was real and the build
lane had reasoned itself past it: on the counter rung the emitter writes ONE
body copy per K iterations, so the compile-time view of "how many mandatory
iterations still follow" tops out at `K + residue` (9 here) where the truth is
`count - stv[ctr] - j` (65 here). The design note had designed exactly that
runtime expression (§4.5) and the build lane had deferred it as a residual on
the reasoning that once-per-trip pruning was "enough". It was not, and no
instrument derived from the implementation was going to say so — the
differential agreed (both arms explored the same space), the corpus had no
such shape, and the structural checks saw a bound emitted at every site.

The remaining ten families came back CLEAN, which is also information: the
author swept trailing constructs, alternation minima, zero-width and
zero-minimum shapes, nesting, multi-byte bodies, laziness, partial and
non-zero-start matches, required-no-match subjects and capture spans through
all of the above, and found nothing. A clean family is a measured statement
about where the bound is not wrong.

## Files

- `01_trailing.rxt` — what FOLLOWS a quantifier, which is the quantity the
  bound is about: trailing literals, `$`, alternations of unequal length,
  trailing quantifiers, and nothing at all.
- `02_alternation.rxt` — the minimum of an alternation is the SMALLER branch.
  A bound that took the left branch, or the longer one, over-estimates.
- `03_zerowidth.rxt` — `a*`, `{0,n}`, `(a|)`, `()`, `^`, `$` and stacked
  zero-minimum quantifiers, where the bound must be exactly 0.
- `04_nesting.rxt` — quantifiers inside quantifiers, where minimums MULTIPLY
  and a bound that adds is wrong in the dangerous direction.
- `05_multibyte_body.rxt` — 2- and 3-byte bodies at subject lengths that are
  NOT multiples of the body width. This is R26 E1's territory reached from
  outside: a bound applied at the wrong granularity lands the cursor between
  two legal iteration boundaries.
- `06_lazy.rxt` — lazy quantifiers alone and mixed greedy/lazy when they nest.
- `07_partial_and_startpos.rxt` — matches that do not reach the subject end
  and do not start at offset 0.
- `08_nomatch.rxt` — near-miss subjects where the right answer is "no match",
  the direction in which a too-SMALL bound is invisible.
- `09_captures.rxt` — group spans through the shapes above, including the
  `RX_UNSET` branches. Half the promise is where the groups land.
- `10_owed_a1_3_65.rxt` — the owed `(a{1,3}){65}` region, 65..100 'a's. Python
  `re` does not terminate here, so the expectations are derived in CLOSED FORM
  from PCRE's leftmost-greedy semantics, with the reasoning in the file's own
  comments; the author cross-validated that closed form against literal DFS
  backtracking AND against python at counts 1..20 before applying it at 65.
  **This is the file that found the counter-rung gap.** It also discharges the
  counter-K lane's checkpoint-2 hand-off: `tests/base/d27_large_counts.rxt:58`
  deliberately left the region unpinned, and it is pinned here.
- `11_motivating_shape_small.rxt` — a small-scale echo of the promise's own
  motivating shape, as a positive control that the "faster" half is real.
- `patterns.txt` — the differential's designed family, organised by WHERE a
  minimum-bytes number can be wrong rather than by pattern shape.
- `run_mrldiff.sh` — the differential. Reuses
  `../possessify/possdiff_driver.c` (as the rung-select and counter-K suites
  do) because the claim is identical for every member of D47.3's deny family.
- `run_mrl_tests.sh` — the structural checks and acceptance cells.

## What the two scripts carry that the corpus cannot

**`run_mrldiff.sh` sweeps BOTH ENGINES, and that is this suite's own axis.**
The two get different CEILINGS: `--engine=vm` turns the DFA prefilter off, so
the bound measures to the SUBJECT END; the default path threads the
prefilter's match-end window (D51 ruling 2), which is tighter and is the form
that ships. A sweep on either alone leaves the other's arithmetic untested,
and the window form is the riskier of the two — it is the only conservative
choice in this design that errs UNSOUND if it is ever stale, because a stale
window is too SMALL.

It also carries STRIDE, for the reason R26 E1 made unavoidable: bodies of
width 1, 2 and 3, at subject lengths on and off the stride lattice. An 855-cell
differential once blessed an unsound clamp because every body in its corpus
came from a single-byte alphabet, and at stride 1 the broken clamp and the
correct one emit arithmetically equal code — zero of its 506 stride-1 cells
could ever have gone red.

**`run_mrl_tests.sh` asserts the things both arms of a differential agree
about.** The differential cannot see that K23 collapsed, because both its arms
answer; the acceptance cell pins the exemplar at a step budget of EIGHT and
requires the denied build to fail there, so the check measures the pruning and
not the box. Same shape for the suffix residual (§9.1): the default build
answers a 16-byte trailing suffix within 64 steps and the `--engine=vm` build
does not, which is what makes the ceiling stamp worth having.

## The denial leaves NO TRACE, deliberately

`-fno-length-prune` on a pattern that carries no bound emits BYTE-IDENTICAL C,
and `run_mrl_tests.sh` asserts that over every pattern in the tree (701 of
them today). That property is what makes the denied build a ground truth
rather than merely a second build, and it is why `<PREFIX>_VM_PRUNE_CEILING`
stamps `"none"` under the denial rather than naming it — the same rule
`emit_dfa.c`'s strategy-denial mask states for `rx_info.flags`, one stamp
over. The denial is checked by the ABSENCE of bounds, never by a stamp saying
it was passed.

Maintenance: update this file when files are added/removed or their roles
change.
