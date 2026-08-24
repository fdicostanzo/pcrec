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

- the `.rxt` files — what each pattern MATCHES, oracle-verified against
  python `re`;
- `run_mrldiff.sh` — that the pruned build and the `-fno-length-prune` build
  AGREE, over a subject sweep, on span + every capture slot + the failure
  surface;
- `run_mrl_tests.sh` — that the bound is EMITTED where the stamp says and
  nowhere when denied, that D51 ruling 2's three obligations have code behind
  them, and that K23 actually COLLAPSED.

**A FOURTH ARRIVED WITH [M6.6.2] wave A** and it does not fit the shape above,
which is why it is called out rather than folded into the list:
`maxw_check.c` (run as `run_mrl_tests.sh` §8) reads a number the compiler
NEVER EMITS. `src/opt/mrl.c` gained `pcrec_maxw` — `pcrec_minw`'s twin with the
opposite sound direction — whose only consumer is the lookaround module's
fixed-width rule, which does not exist yet. So none of the three instruments
above can be red because of it: there is no bound to emit, no differential arm
to disagree, and no `.rxt` cell whose answer depends on it. The check links
`libpcrec.a`, parses every `pattern` line in `tests/` to an AST and calls the
two analyses directly.

## What this directory is, and what it is NOT

**It is the IMPLEMENTATION lane's test directory.** The `.rxt` files here are
ordinary implementation tests: they pin what MRL's own machinery does, shape by
shape, and they were written knowing the mechanism exists.

**The D27 CORPUS OF RECORD for K23 is elsewhere** —
`../base/d27_k23_ambiguous_decomposition.rxt`, authored in a separate cell by
an author denied `src/`, the rest of `tests/`, the design notes and the
history, and merged from the `d27k23` lane. That file owns the
`(a{1,3}){64,65,66}` ambiguous-decomposition region the plan row owed. Nothing
here duplicates it, and nothing here should: a corpus written by the lane that
wrote the implementation is not a D27 corpus whatever its authoring
arrangements, and two corpora over one region collide at merge.

### The provenance of these files, stated because it is a fact and not a claim

Before the manager's D27 author was known to this lane, this lane spawned its
own cell-isolated author against the same one-page statement of what MRL
promises. Ten of these eleven files came back from that cell; the eleventh —
the owed `(a{1,3}){65}` region — was DROPPED from delivery on the manager's
instruction, because it duplicated the corpus of record. That is the right
call on collision grounds regardless of how either file was authored.

**The exercise paid before it was dropped, and the finding is why this
paragraph exists.** The owed-region file FAILED against this lane's first
implementation: 32 cases returning `RX_ERR_STEPS` where the promise says the
matcher must answer. The cause was real. On the counter rung the emitter
writes ONE body copy per K iterations, so the compile-time view of "how many
mandatory iterations still follow" tops out at `K + residue` (9 there) where
the truth is `count - slot_values[ctr] - j` (65). `k23_design.md` §4.5 had designed
exactly that runtime expression; this lane had deferred it as a residual on
§9.3's "once-per-trip is believed enough", which splits into a FREQUENCY that
holds and a VALUE that does not.

No instrument derived from the implementation was going to say so — the
differential agreed (both arms explored the same space), the corpus had no
such shape, and the structural checks saw a bound emitted at every site with
the right arithmetic for the model the emitter had. That is D27's claim
measured again, and it is the reason the mechanism now has its own acceptance
cell in `run_mrl_tests.sh` (§1b) rather than resting on a corpus this
directory does not own.

The remaining ten families came back clean, which is also information: they
sweep trailing constructs, alternation minima, zero-width and zero-minimum
shapes, nesting, multi-byte bodies, laziness, partial and non-zero-start
matches, required-no-match subjects and capture spans through all of the
above, and found nothing.

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
- (`10_owed_a1_3_65.rxt` was here and is DELIBERATELY ABSENT. The owed
  `(a{1,3}){65}` region belongs to the D27 corpus of record,
  `../base/d27_k23_ambiguous_decomposition.rxt`, which also discharges the
  counter-K lane's checkpoint-2 hand-off — `../base/d27_large_counts.rxt:58`
  deliberately left the region unpinned. What this directory keeps of that
  episode is the MECHANISM guard in `run_mrl_tests.sh` §1b and the account
  above.)
- `11_motivating_shape_small.rxt` — a small-scale echo of the promise's own
  motivating shape, as a positive control that the "faster" half is real.
- `patterns.txt` — the differential's designed family, organised by WHERE a
  minimum-bytes number can be wrong rather than by pattern shape.
- `run_mrldiff.sh` — the differential. Reuses
  `../possessify/possdiff_driver.c` (as the rung-select and counter-K suites
  do) because the claim is identical for every member of D47.3's deny family.
- `run_mrl_tests.sh` — the structural checks and acceptance cells.
- `maxw_check.c` — [M6.6.2 wave A] `pcrec_maxw` against the whole `.rxt`
  corpus, from BOTH SIDES, because either inequality alone is passed by a
  degenerate implementation: `maxw >= minw` at every NODE (passed by
  `return PCREC_W_UNBOUNDED;`) AND every oracle-verified span in the corpus
  within the root's `maxw` (passed by `return 0;`). The second is the only
  constraint on maxw in this tree that does not come from pcrec — the spans
  are python-`re`- and libpcre2-verified — and it is the direction that
  miscompiles, since an under-estimated maxw makes a variable-width
  lookbehind branch look fixed. Three sabotages (`zero`, `unbounded`, `swap`)
  are required to make it fail. Measured at wave A: 122 files, 2168 blocks,
  1914 patterns parsed, 254 refused, 12,637 nodes swept (9,583 with a bounded
  maxw), 8,901 oracle spans, 0 violations.

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
