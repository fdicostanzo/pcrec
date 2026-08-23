# tests/backrefs — module `backrefs` ([M6.5.2])

Every backreference spelling (`\1`..`\N`, `\g` in its brace/bare forms, `\k` in
its three, `(?P=name)`), PCRE2's octal disambiguation at the atom position, and
`(?J)`/DUPNAMES with the resolution rule that makes it mean anything. Design:
`docs/design/backrefs_design.md`, panel-approved at R32
(`docs/dev/reviews/2026-08-22-r32-backrefs-design.md`).

**A backreference is not a class-membership test, and every file here follows
from that.** Everything else pcrec compiles is a 256-bit bitmap or a position
predicate — which is why caselessness folds away at parse time (D23) and why
the DFA can carry every other construct. A backreference compares SUBJECT TEXT
against SUBJECT TEXT at a pair of positions the backtracking state holds at
that instant. So it is VM-only, it cannot have a prefilter, its caseless form
is the encoding seam's second residual entry, and the thing most likely to be
wrong about an implementation is WHICH pair of positions it reads.

## THE CORPUS IS GENERATED, and that is a property rather than a convenience

`gen_corpus.py` wrote every expectation in every `.rxt` here by driving the
cell through libpcre2 10.46 BEFORE it was written, and drove python3 `re` over
the same cells in the same pass. A block carries `# pcre2-only` exactly where
python diverged or could not compile the pattern — **computed, never
declared** — with the first divergence and the cell count recorded above the
marking.

That matters more here than anywhere else in the tree, because this module has
the largest oracle divergence pcrec has met. python `re` refuses EVERY
self-reference and EVERY forward reference at compile time, has no `\g`, no
`\k` and no `(?J)` at all, rejects the `(?<n>...)` declaring spelling, and
refuses `(?i)` anywhere but the pattern start — which is exactly where the two
cells that decide WHERE the caseless flag is read live. R32 C3 found the first
test plan marking two of these files python-verifiable IN THE DIRECTION THAT
LOSES THE ORACLE; computing the marking removes the species.

Re-run it after changing a cell list:

    python3 tests/backrefs/gen_corpus.py     # rewrites the .rxt files in place

Current census, from that run: **244 cells, 53 blocks python-verified, 65
`# pcre2-only`, 31 `perr`.** `python3 tests/harness/verify_rxt.py
tests/backrefs/` passes 234/234 on the python-verifiable half; `bash
tests/harness/run.sh tests/backrefs/*.rxt` passes 455/455 over this
directory's own cells.

**The two harness figures differ, and the command is why.** `run.sh
tests/backrefs/` (the DIRECTORY, no glob) also walks `d27/` — the [M6.5.3]
blinded corpus — and reports 662. Both numbers are correct for what they
were asked; quote the command with the figure. (The 442 this paragraph
carried until 2026-08-22 was the pre-d27 value of the 455 figure, correct
when written and made confusing only by d27 landing beside it.)

The 2026-08-22 additions are the "EMPTY CAPTURE UNDER AN UNBOUNDED
QUANTIFIER" block in `numeric.rxt` (+7 cells, +13 harness cases): the live
population of the empty-iteration guard, without which sabotage row S107
scored UNDETECTED against a module that was correct. See that block's own
comment and the row's header.

## Files

- **numeric.rxt** — `\1`..`\9` and above: the UNSET rule (PCRE2 FAILS an unset
  reference, it does not match empty — `^(a)?\1$` on `""` is no match), the
  EMPTY rule (a group that captured the empty string is SET, and the two are
  ONE `if` apart), quantified references, and the startpos sweep. Fully
  python-verifiable, which is unusual in this directory and is why the file
  exists as its own: it is the half of the semantics a base-tier oracle can
  still arbitrate.
- **octal.rxt** — §5's four ordered questions, each with a DISCRIMINATOR
  subject so "it compiled" is never mistaken for "it is a backreference". The
  ASYMMETRY is the finding: `\1`..`\9` see the WHOLE pattern (`\1(a)` compiles)
  while `\10`+ see only what PRECEDES them (`\10(a)..(j)` is the octal byte
  0x08). **No test that only uses groups-before will notice** an
  implementation that gets it backwards, which is why sabotage rows S112 and
  S113 are separate.
- **octal_class.rxt** — the CLASS position, run with the module ENABLED. Every
  cell is a MUST-NOT-CHANGE pin: inside a class a backreference is impossible,
  so `\0`..`\7` are octal and `\8` `\9` `\g` `\k` are the literal characters,
  and that is BASE syntax the gate never touches. Sabotage S110 makes the atom
  port claim the class position and these twelve cells are the only thing that
  sees it.
- **selfref.rxt** — self-references, forward references, **and the RE-ENTRY
  class, which is this file's reason for existing.** `(a|b\1)+` on "ab" is
  libpcre2 (0,1) with group 1 = (0,1); the write-on-traverse model the first
  design was built on answers (0,2) with group 1 = (1,2), and
  `^(?:(a|b\1)y)+` on "aybay" makes that model's emitted compare UNDERFLOW a
  `size_t`. The first design's `selfref.rxt` took only the S/F cells that
  AGREED — and cells that agree under both publication disciplines cannot
  detect the difference between them.
- **nested.rxt** — the trail as behaviour. `^(?:(a|b)\1)+$` on "aabb" is (0,4)
  with group 1 = **(2,3)**, not (0,1): the reference must compare against THIS
  iteration's capture, and on backtracking the PREVIOUS iteration's value must
  come back. Also the reverse-deterministic shape (a group in the loop body,
  the reference OUTSIDE it), which was traced correct and UNTESTED in the first
  design, and nested backreferences.
- **spellings.rxt** — every spelling, and the `\g` doorway's OTHER construct.
  `^(a|b)\g<1>$` matches "ab" (a SUBROUTINE call re-runs the group's pattern)
  where `^(a|b)\g{1}$` does not (a backreference compares the captured text),
  so the two halves belong to two different modules and this one may claim only
  one of them.
- **caseless.rxt** — WHERE the `(?i)` is read and WHAT the compare folds. The
  load-bearing pair is `^(a)(?i:\1)$` (matches "aA") beside `^(?i:(a))\1$`
  (does NOT): the caselessness is the option in force AT THE REFERENCE, not at
  the group, and an implementation reading it at the group passes one and fails
  the other.
- **dupnames.rxt** — `(?J)`'s scoping rule (checked AT EACH DECLARATION against
  the scoped state, which four separating cells establish) and §8.3's
  resolution rule, plus the RE-ENTRY cells over a name run that the first
  design's file had none of.
- **gated.rxt** — what each partial enable buys, and the class column that does
  not move.

## The instruments

- **run_backref_diff.sh** — nine sections, four EXACT population guards. Three
  of the sections exist because nothing else in the tree asks their question:
  §3 (the RE-ENTRY arm, where publish-at-close is observable AND NOWHERE ELSE —
  a 5,808-cell arm-vs-arm sweep found the backref-FREE control at 0/0 in BOTH
  publication disciplines), §4 (the `--no-captures` arm, the only place §6.3's
  "keeps internal slots, reports none" ruling is exercised) and §8 (the
  SPAN-DIVERGENCE section, the only possible detector for a prefilter planted
  on a backref pattern). §9 is the 65,536-pair fold agreement.
- **run_dupnames_diff.sh** — §8.3 swept rather than sampled, and checked THREE
  ways: pcrec against libpcre2, an INDEPENDENTLY WRITTEN model of the rule
  against libpcre2, and both populations asserted exact. The `.rxt` cells
  separate four candidate readings; only a sweep shows no FIFTH fits.
- **bref_batch.c / bref_entries.c** — the batch drivers, one process per
  (pattern, arm) rather than per cell. **They report the GROUP SPANS**, unlike
  their `atomic_groups` siblings, because for this module the group spans are
  the sharper detector: the re-entry family contains subjects on which the
  outer span agrees and the group does not.
- **bref_oracle.py** — the libpcre2 side in one process, with the group list
  PADDED to the requested count (libpcre2 truncates trailing unset pairs, so
  without padding the two oracles disagree about a SHAPE rather than an
  answer — and every such block would be marked `# pcre2-only` for no reason).
- **fold_agreement_check.c** — the mechanism that discharges R32 E8. pcrec's
  ASCII fold exists TWICE and cannot be made to exist once (a parse-time class
  widener; match-time arithmetic in the encoding residual), so this walks all
  65,536 ordered byte pairs comparing the SHIPPED
  `rx_bref_match_caseless` — compiled out of an artifact pcrec actually
  emitted — against `pcrec_ascii_fold`, which `cls_casefold` derives from.
  Neither side can be edited into agreement with the other.

`tests/codegen/run_backref_identity.sh` is the module's byte-identity gate and
lives there with its four siblings; it is OPT-IN (`make test-backrefs-identity`)
because it is a claim about a MOMENT, not a standing invariant.

## What is deliberately NOT here

- **`nocaps.rxt`.** The `.rxt` format has no `--no-captures` directive, and the
  facts that axis needs are pcrec-only reflection assertions (`RX_NCAPS`
  is 1) rather than match spans. `run_backref_diff.sh` §4 carries it, and
  says so.
- **`\g<...>` / `\g'...'` as accept cells.** They are SUBROUTINE CALLS, module
  `recursion`, and they appear here only as `perr` blocks recording what
  libpcre2 answers and why pcrec refuses.
- **A `PCREC_MATCH_UNSET_BACKREF` arm.** Measured and declined (§3.3): 2 of the
  8 unset cells flip under the bit, and implementing it means a second emitted
  shape for one construct selected by an option pcrec does not have.
