# D27 capture-semantics test authoring — NOTES

Author: blinded D27 spec-first test author, working only inside this cell.
Inputs read in full: `docs/design/match_api_m4.md` (the frozen match-API
contract) and `docs/testing.md` (the `.rxt` format, specifically its
"Capture-group expectations" section). `build/pcrec` was invoked only to
check ACCEPT/REJECT of candidate patterns (72 distinct patterns, all
accepted) — never to derive an expected span or slot value. Every expected
value in every `.rxt` file comes from python3 `re`.

## Disclosure

My spawn context automatically injected the session-root `CLAUDE.md` and a
memory index, as the brief said it would. Both are process/workflow
material (subagent tiering, journal conventions, worktree/cell mechanics),
not test corpora or implementation detail, so I did not treat them as
information about capture semantics and did not go looking further. I did
not read or list anything under `src/`, `tests/`, or any path outside this
cell; no `git` commands were run (the cell has no `.git`).

**Minor pre-existing-artifact note, not a blinding violation**: `cellwork/`
was described as an output directory, but it already contained one file,
`probe.h`, when I first listed it — a generated ABI header sample for the
pattern `a(b|c)+d` (`RX_NCAPS 2`, i.e. this artifact already delivers one
capture slot beyond the whole match). I read it before starting real work.
It does not expose anything beyond what `match_api_m4.md` §4/§5 already
document in full (the `rx_ctx`/`rx_info`/`rx_group_entry` shapes, `RX_NCAPS`,
`RX_UNSET`) — no test alphabet, no `src/` structure. I did not use it to
derive any expected value; it's flagged here purely because it was an
unexpected file where the brief described an empty directory. One
implication worth noting for the manager: `RX_NCAPS 2` for a one-group
pattern in this snapshot means the VM/M4.5 engine may already be live here,
ahead of what the "captures don't exist before [M4.5]" framing in the
contract's history might suggest — which is exactly why every group-slot
assertion below is written as `gp` (pending-VM, self-activating) rather than
`g` (claimed-live): see "g vs gp" below.

## Deliverables

- `cellwork/priority_and_iteration.rxt` — 33 `m`/`ms` cases, 42 `gp` lines.
- `cellwork/participation_and_zerowidth.rxt` — 26 `m`/`ms` cases, 47 `gp` lines.
- `cellwork/structure_anchors_misc.rxt` — 26 `m`/`ms` cases, 56 `gp` lines.
- **Total: 85 `m`/`ms` cases, 145 group-expectation lines**, all inside the
  brief's 80–150-case target.

All 72 distinct patterns used were confirmed ACCEPTED by this cell's
`build/pcrec` (`-p rx -o ... '<pattern>'`, `--features classes` where a
pattern uses `\d`). Nothing in the corpus needed a `perr` substitute.

## `g` vs `gp`: a deliberate, uniform choice

Every group slot 0 is covered implicitly by the `m`/`ms` line's own
`<start> <end>` fields (C3: `caps[0]` is always the whole match, always
live). For every slot 1 and above I used `gp` (pending-VM) uniformly, never
`g` (claimed-live), even though this cell's snapshot may already deliver
some of those slots (see the `probe.h` note above). Reasoning: determining
which slots are live for which of my 72 patterns on today's specific
artifact would require reading each pattern's own `RX_NCAPS` out of its
compiled `gen.h` — a form of "run the implementation to learn a fact used to
shape the test," which is exactly the derivation-from-implementation the
brief rules out (I'm allowed to check accept/reject only). `gp` is designed
for precisely this situation: per `docs/testing.md`, a `gp` line
"self-activates" and is checked exactly like `g` once the artifact's
`RX_NCAPS` covers that slot, with no corpus edit required, and produces a
real FAILURE (not a silent pass) if the value is wrong once it does. Using
`gp` throughout keeps the corpus correct and useful regardless of which
engine substep the artifact under test has reached — the population-
accounting discipline the brief asked for, applied conservatively.

One consequence: unlike the seed corpus example described in
`docs/testing.md` (which included 3 explicit `g 0 <start> <end>` lines "for
documentation clarity"), I did not add explicit slot-0 `g` lines anywhere —
the `m`/`ms` line already states that value and, per the same testing.md
section, doing so is optional and behaviorally identical either way ("costs
nothing," "harness behaves identically either way"). The `whole-match-c3`
case's comment says "explicit slot-0 check" — that's referring to the
`m`/`ms` line's own start/end value being exactly `caps[0]`, not to an
additional `g 0` line I chose to omit as redundant.

## Case-design taxonomy

**Territory A — alternation priority (leftmost-first, not longest-match).**
`priority_and_iteration.rxt`, cases `alt-priority-01` through `-10`,
`alt-backtrack-11`/`-12`. Which alternative's capture survives when several
could match; that a shorter first alternative wins even when a later one
would let the whole match consume more (`(a|ab)` on `"ab"` → group is `"a"`,
not `"ab"`); that alternation inside a repeated group doesn't maximize
overall length, only finds *a* match (`(a|a+)` on `"aaa"` → group is a
single `"a"`); backtracking through an anchor forcing a later alternative to
fire (`^(a|ab)$`); a group that transiently matches during the search and
is then discarded by backtracking, ending up **unset**, not holding its
transient value (`(a)?a` on `"a"` → group1 is `(-1,-1)`, not `(0,1)`) — this
last one is the sharpest test of "unset means the FINAL decision, not
anything tried along the way."

**Territory B — which quantifier ITERATION's value a group reports.**
`priority_and_iteration.rxt`, cases `iter-13` through `iter-31`. The general
rule (last iteration wins) across single-char bodies, multi-char bodies,
alternation bodies, nested repetition (`((a)+)+`), bounded `{n,m}` both
greedy and lazy, exact-count `{n}`, and a repeat count of exactly zero
(`(a){0}` — the group is structurally never entered, distinct from "entered
and produced an empty span"). Two cases (`iter-16`, `iter-17`) probe what
happens when a repeated group's LAST executed iteration is a *zero-width*
one following non-empty iterations — flagged specially below, this is the
one place I'd call the contract genuinely silent.

**Territory C — RX_UNSET / group participation.** `participation_and_
zerowidth.rxt`, cases `unset-01` through `unset-09`. Never-entered
alternation branches; an optional group not taken at all vs. taken;
`{0,n}`-shaped stars taken zero times (unset, explicitly NOT the same as an
empty span — `unset-03`); nested unset-inside-set (`unset-04`) and nested
set-and-unset-together (`unset-05`, both directions on one pattern); three-
way alternation with two simultaneous unset slots (`unset-06`); a group
nested inside an optional-and-quantified wrapper, exercised at all three
population levels — neither entered, entered-but-zero-iterations, entered-
with-iterations (`unset-07`, one pattern, three subjects); the winning
alternative simply having no group at all (`unset-08`); and the sharpest
case in the set, `unset-09`, on whether an EARLIER iteration's capture
survives when a LATER iteration of the same repeated wrapper takes the
*other* alternative branch — flagged below.

**Territory D — zero-width group matches.** `participation_and_
zerowidth.rxt`, cases `zw-01` through `zw-07`. A nullable group matching
empty at the very first search position; a zero-width group sandwiched
between two literal characters; forcing the search to walk to the end of
the subject before a zero-width match becomes possible (`$`-anchored);
the same anchored at the start; multiple adjacent optional groups
collapsing to the same empty position, or splitting non-empty/empty
between two adjacent groups depending on the subject.

**Territory E — anchors and startpos.** `structure_anchors_misc.rxt`, cases
`anchor-01` through `anchor-06`. Group offsets computed relative to a
`ms`-supplied `startpos` (mid-subject, exactly on the match boundary,
skipping an earlier candidate match entirely, across two groups spanning
the startpos-relative match), plus one `$`-anchored group and one explicit
`startpos=0` control case for `^`.

**Territory F — nesting depth and sibling order.** `structure_anchors_misc.
rxt`, cases `nest-01` through `nest-07`. Two siblings under one wrapper
(the exact pattern `docs/testing.md`'s own worked example uses, `((a)(b))c`
— I independently re-derived it rather than trusting the doc's prose);
three levels of pure nesting collapsing to one span; three siblings under
one wrapper; siblings with no wrapper at all and increasing lengths;
nesting combined with repetition (outer AND inner both must report only
their last iteration — `nest-05`); nested alternation at two different
depths in one pattern; and a three-level pattern with sibling literal text
on both sides at every level.

**Territory G — same subject, structurally different patterns.**
`structure_anchors_misc.rxt`, `struct-01a` through `-01e` (subject `"aaa"`
split 1+1+1, 1+2, 2+1, whole, and nested-1+1-then-sibling-1 across five
different patterns) and `struct-02a`/`-02b` (subject `"abcabc"` via a
repeated group vs. two sibling groups). Directly exercises that slot
values are a property of the PATTERN's structure, not something a reader
could infer from the subject text alone.

**Territory H — misc C1–C11 coverage.** `structure_anchors_misc.rxt`.
`c9-noncapturing`/`c2-o1-slot`: non-capturing groups `(?:...)` consume
neither a group number nor a `caps[]` slot (C9), so slot numbering for the
surrounding capturing groups stays contiguous — this is the "boring," fully
unambiguous case of C2's slot-vs-number distinction (see the ambiguity note
below for the corner the contract itself flags as non-trivial, which this
does NOT reach). `classes-bounded`: bounded `{n,m}` combined with a `\d`
class escape (`features classes`), both groups landing on real digit runs.
`caseless-01`/`-02`: `flags i` combined with a plain group and with an
alternation-under-quantifier group, confirming case-insensitive matching
doesn't change which span is reported, only which bytes match.

## Ambiguity / gap findings

1. **The contract is silent on cross-iteration capture retention within a
   repeated group.** `unset-09-star-of-alt-empty`, pattern `((a)|(b))*` on
   subject `"ab"`. Python `re` gives: group1 (outer, last iteration) =
   `(1,2)` = `"b"`; group2 (inner `a`-branch) = `(0,1)` = `"a"`, RETAINED
   from the FIRST iteration even though the SECOND (and last) iteration took
   the other branch and never touched group2 again; group3 (inner
   `b`-branch) = `(1,2)`, set by the second iteration. Neither
   `match_api_m4.md` nor `docs/testing.md` states this rule anywhere I could
   find — C6 says "every pair `0..ncaps-1` is written on a completed match,"
   which tells you THAT every slot has a value, not what that value is when
   a slot's owning subexpression didn't run in the match's final iteration.
   The only textual anchor for this behavior at all is `docs/testing.md`'s
   one-line gloss on its own seed corpus, "a repeated capturing group
   keeping only its LAST iteration's span" — which is exactly true for the
   group that WAS in the last iteration, but says nothing about a sibling
   group that wasn't. I derived the expected value from python `re`
   directly (leftmost-first backtracking semantics, the tier this task
   specifies) rather than from anything written in either document, and I
   flag it because a reader implementing this from the contract text alone,
   without independently knowing Perl/PCRE2 capture semantics, would have
   no way to derive `(0,1)` for group2 rather than `(-1,-1)` — "did this
   slot's subexpression run during the WINNING attempt at all, ever" reads
   just as plausibly as "did it run during the specific iteration that
   happened to be last," and only one of those two readings is correct.

2. **The same gap, one level simpler: an empty FINAL iteration overwrites a
   non-empty earlier one.** `iter-16-empty-final` (`(a?)*` on `"aaa"`) and
   `iter-17-empty-final` (`(a*)*` on `"aaa"`) both report group1 = `(3,3)`
   (empty, at the end) rather than `(2,3)` = the last non-empty `"a"`. This
   is the well-known "does a trailing empty match of a starred group count
   as an iteration for capture purposes" question, and it is not addressed
   by either document. It is the same underlying gap as finding 1 (both are
   instances of "the contract states THAT `ncaps` slots are populated, not
   the per-iteration RULE that produces a value"), listed separately because
   it is reachable with a single group and no alternation, so a much
   simpler repro if anyone wants one.

   Per the brief's own instruction, flagging the oracle itself: this
   specific pair of behaviors (empty-iteration handling in starred nullable
   groups) is the one shape in regex engines with a real history of
   cross-implementation and cross-version disagreement — older Perl/PCRE
   and pre-3.7 Python `re` did not agree with each other or with themselves
   across versions on exactly this case. I did not independently verify
   against a second oracle (no `libpcre2` is available in this cell), so
   while I'm using the python3 `re` this project has already measured at
   zero disagreements with PCRE2 across 225k pairs on this tier, THIS
   specific shape (trailing empty iteration of a starred nullable capturing
   group) is exactly the kind of case that measurement's aggregate number
   could be hiding a rare disagreement on. I'd flag `iter-16`/`iter-17` for
   an explicit libpcre2 cross-check once [M4.7]'s differential exists,
   ahead of trusting them as load-bearing regression cases indefinitely.

3. **Not a contradiction, but a real absence I had to design around**: the
   `.rxt` format documented in `docs/testing.md` has no line kind for
   asserting that a PATTERN gets a specific `RX_NCAPS`/`ngroups` value
   directly (only per-case `g`/`gp` group-span assertions, attached to a
   match). Territory G's "structurally different patterns" cases
   demonstrate different SLOT VALUES for the same subject, but nothing in
   the format lets a corpus assert "this pattern's artifact has exactly N
   capture slots" as its own fact independent of any one match — that
   would have been the more direct way to test C1 ("group count is a
   compile-time constant") and `rx_info.ncaps`/`ngroups` (§5) than inferring
   it indirectly from how many `gp` lines a case happens to carry. Recording
   this as a possible format gap for the manager, not fixing it myself
   (out of scope, and it isn't a blinding-relevant ambiguity — it's a
   harness-capability gap).

## Oracle verification evidence

Two independent scripts, in the scratchpad (never committed, never inside
the cell): `gen_cases.py` derived every value from python3 `re` while
writing the `.rxt` files, and `verify_rxt.py` is a SEPARATE, from-scratch
parser of the `.rxt` TEXT (not the generator's in-memory data) that
re-derives every `g`/`gp` line from python3 `re` a second time and diffs
against what's on disk. Final clean run of the independent verifier:

```
$ python3 verify_rxt.py
/home/duxevents/pcrec/worktrees/m45d-capauthor-cell/cellwork/participation_and_zerowidth.rxt: 26 m/ms cases re-derived, 47 g/gp lines re-derived, 0 mismatch(es)
/home/duxevents/pcrec/worktrees/m45d-capauthor-cell/cellwork/priority_and_iteration.rxt: 33 m/ms cases re-derived, 42 g/gp lines re-derived, 0 mismatch(es)
/home/duxevents/pcrec/worktrees/m45d-capauthor-cell/cellwork/structure_anchors_misc.rxt: 26 m/ms cases re-derived, 56 g/gp lines re-derived, 0 mismatch(es)

CLEAN: 85 m/ms cases and 145 g/gp lines, all independently re-derived from python3 `re` with zero mismatches, across 3 file(s).
```

Generator run (pattern-acceptance side, `build/pcrec` invoked for
ACCEPT/REJECT only):

```
$ python3 gen_cases.py
wrote .../cellwork/priority_and_iteration.rxt: 33 m/ms cases
wrote .../cellwork/participation_and_zerowidth.rxt: 26 m/ms cases
wrote .../cellwork/structure_anchors_misc.rxt: 26 m/ms cases

TOTAL m/ms cases: 85
TOTAL g/gp lines: 145

All 72 distinct patterns ACCEPTED by pcrec.
```
