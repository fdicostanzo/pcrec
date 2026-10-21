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

## Files

- `01_trailing.rxt` — what FOLLOWS a quantifier, which is the quantity the bound is about: trailing literals, `$`, alternations of unequal length, trailing quantifiers, ...
- `02_alternation.rxt` — the minimum of an alternation is the SMALLER branch.
- `03_zerowidth.rxt` — `a*`, `{0,n}`, `(a|)`, `()`, `^`, `$` and stacked zero-minimum quantifiers, where the bound must be exactly 0.
- `04_nesting.rxt` — quantifiers inside quantifiers, where minimums MULTIPLY and a bound that adds is wrong in the dangerous direction.
- `05_multibyte_body.rxt` — 2- and 3-byte bodies at subject lengths that are NOT multiples of the body width.
- `06_lazy.rxt` — lazy quantifiers alone and mixed greedy/lazy when they nest.
- `07_partial_and_startpos.rxt` — matches that do not reach the subject end and do not start at offset 0.
- `08_nomatch.rxt` — near-miss subjects where the right answer is "no match", the direction in which a too-SMALL bound is invisible.
- `09_captures.rxt` — group spans through the shapes above, including the `RX_UNSET` branches.
- (`10_owed_a1_3_65.rxt` was here and is DELIBERATELY ABSENT. The owed `(a{1,3}){65}` region belongs to the D27 corpus of record, ...
- `11_motivating_shape_small.rxt` — a small-scale echo of the promise's own motivating shape, as a positive control that the "faster" half is real.
- `patterns.txt` — the differential's designed family, organised by WHERE a minimum-bytes number can be wrong rather than by pattern shape.
- `run_mrldiff.sh` — the differential.
- `run_mrl_tests.sh` — the structural checks and acceptance cells.
- `cwmax_check.c` — [M6.6.2 wave A; RE-AIMED at [M5.0] stage 2] the CHARACTER width pair `pcrec_cwmin`/`pcrec_cwmax` against the whole `.rxt` corpus.

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

(Rest of this section: see the history file.)

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__mrl.md`.
