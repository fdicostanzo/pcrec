# tests/recursion — module `recursion` ([DD-14])

Subroutine calls: `(?1)`..`(?9)` and beyond, `(?-N)`/`(?+N)` relative forms
(with their leading-zero and relative-zero variants), `(?&name)`,
`(?P>name)`, `\g<N>`/`\g<name>`/`\g<±N>`, `\g'N'`/`\g'name'`, `(?R)`, `(?0)`,
and the two spellings the charter's list did not have, `\g<0>`/`\g'0'`.
Design: `docs/design/subroutines_design.md` (PROPOSED, not yet paneled at the
time this corpus was written). Decisions: `docs/dev/decisions.md` D71 (the
give-up-code diagnostic axis, D71.1 in particular) and D72
(`PCREC_ERR_INTERNAL`).

**WAVE D HAS ALSO LANDED, AND THIS SECTION IS AGAIN THE PRESENT TENSE.**
Wave B+C shipped the three `(?` ports, the resolver's call rule,
`src/opt/callgraph.c` and the emitter's call linkage, leaving the `\g<`/`\g'`
family `unbuilt` (below). Wave D wired `pcrec_brport_g`'s `<`/`'` arms
(`src/parse/mod_backrefs.c`, design §4.2's "NOT A NEW PORT" ruling), so
`\g<N>`/`\g<name>`/`\g<±N>`/`\g<0>` and `\g'N'`/`\g'name'`/`\g'0'` all compile
and match now too. **This directory runs 371 cases / 0 failures** — the 22
`\g` blocks (below) went from `perr` to real `m`/`n`/`g` lines by ONE edit to
`gen_corpus.py` (deleting each block's `wave='D'` keyword argument) and a
re-run, exactly as the paragraph below always said they would; nothing about
the CELLS changed, only what pcrec answers them with.

**WHAT USED TO BE EXPECTED-UNSUPPORTED WAS THE `\g` FAMILY, AND IT WAS MARKED
RATHER THAN RED — THIS PARAGRAPH IS KEPT AS THE RECORD OF WHY, PAST TENSE.**
Design §8.1 required the two `\g` registry rows to stay `unbuilt` until wave D
wired their port — D65 flips `built` from the PORT's answer, and a wave that
flipped them while the emitter could not compile the spelling would have
shipped a compliance index that lies — so the 22 blocks whose pattern carries
`\g<` or `\g'` rendered as `perr` blocks under
`gen_corpus.py`'s `wave='D'` marker, with **the oracle's answer carried in a
`# WAVE D ORACLE:` comment beside each cell**. That was `APPROACH.md` §7's
expected-unsupported policy as `docs/testing.md` states it (step 2: pin the
compile error via `perr`; step 3: once the component is implemented, replace
those blocks with real cases), and wave D's edit is to delete one keyword
argument and re-run the generator — the `m`/`n`/`g` lines that come back are
the ones libpcre2 gives THEN, never a transcription of what it gave now.

## THE CORPUS IS GENERATED, and there is no python arm

`gen_corpus.py` wrote every expectation in every `.rxt` here — **including
every `g` line** — by driving the cell through libpcre2 10.46 (via
`docs/design/subroutines_measurements/probes/sr_oracle.py`, which borrows
`la_oracle.py` → `br_oracle.py` → `pcre2_ctypes.py`, three levels of
borrowing rather than a fourth copy of the ctypes binding) BEFORE it was
written. The generator never asks pcrec anything.

**Unlike every earlier generated corpus in this tree, there is no python
arm and no `# pcre2-only` marking.** Design §10.1 MEASURED it: python3's
`re` has NO subroutine-call construct at all — not different semantics, an
ABSENCE. Every one of the nine call spellings plus both zero spellings
raises `re.error` at compile time. `\1` and `(?P=n)` DO compile in python,
but they are `backrefs`'s reference construct, not this module's call
construct (design §2.1's one-cell discriminator is why `spellings.rxt`
opens with it) — treating python's agreement on those two spellings as
coverage of this module would be the exact trap §10.1 names.

Re-run after changing a cell list:

    python3 tests/recursion/gen_corpus.py

It rewrites the `.rxt` files in place and prints a per-file census. A
second run with no source change is a no-op (`git diff` empty — checked,
see below).

**`(?(DEFINE)...)` DOES NOT APPEAR ANYWHERE IN THIS CORPUS.** It is module
`conditionals`'s construct at the `(?(` doorway until D71 decision 4's
registry row lands (`[DD-14]` wave F — not started when this corpus was
written; see `refused.rxt`'s own note that design §2.5's "RULED: no
DEFINE" is SUPERSEDED by that later ruling). Every callee-only body in this
corpus uses the oracle-verified **`{0}`-callee idiom** instead —
`(?:(?<g>BODY)){0}` — a REPEAT of a GROUP, base syntax, needing only
`recursion` (plus `named-groups` for a named callee). Design §2.5/§4.4c
measured it an exact substitute for plain, recursive, atomic and
rung-bearing callees; this generator re-verifies every such cell against
libpcre2 itself rather than trusting that claim.

## Files

- **`refused.rxt`** — the `conditionals` refusals this module does NOT
  unlock: `(?(DEFINE)`, `(?(R)`, `(?(1)`, each pinned by running today's
  built `build/pcrec` (this worktree, off `main`, no subroutine-call
  producer). Includes the cell showing `--features recursion` changes
  nothing — the doorway is still `conditionals`'s until wave F lands.
- **`gated.rxt`** — the two D65 diagnostics (`requires module 'recursion'`
  under std1 vs `... is enabled but ... is not implemented yet` under a
  partial set), P2's masking cell, and the positive control. **P2's cell is
  flagged NOT OBSERVABLE IN ITS TRUE FORM TODAY** — see "What could not be
  oracled" below.
- **`spellings.rxt`** — design §2.1's one-cell call-vs-reference
  discriminator (`(a|b)\1` nomatch vs `(a|b)(?1)` match on `"ab"`), then
  every shipped call spelling carrying the same discriminator.
- **`relative.rxt`** — `(?±N)`/`\g<±N>` at four distances each direction,
  the leading-zero relative forms, and the four relative-zero error cells
  (all real PCRE2 compile errors, `kind='pcre2'`).
- **`whole.rxt`** — `(?R)`/`(?0)`/`\g<0>`/`\g'0'` and the anchor cells:
  `^(a(?1)?b)$` on `"aabb"` is `(0,4)`, `^(a(?R)?b)$` is nomatch, because
  `(?R)` re-runs the anchors and `(?1)` does not.
- **`captures.rxt`** — after return, at depth 3, after a failed call, and
  the inheritance cell `^(a)(b\1)(?2)$` on `"ababa"` with its `"abab"`
  control (needs `backrefs`).
- **`atomicity.rxt`** — the isolated discriminator (a callee reachable only
  by the call) over three quantifier shapes, the depth-retry cell, and all
  four atomic controls (nomatch).
- **`leftrec.rxt`** — three give-up cells (direct, indirect, nullable-
  prefix), each `gu frames` per D71.1 (see "The `gu frames`-vs-`recurse`
  note" below); the `^(a|(?1)a)$` on `"a"×200` cell that MUST match; and
  the right-recursion contrast that is NOT a give-up.
- **`dupnames.rxt`** — design §3.4(c)'s call/reference split (a call
  resolves a duplicated name STATICALLY to the first declaration; a
  reference resolves it dynamically to the first SET member — see
  `tests/backrefs/dupnames.rxt` for that half), the no-retry-into-later-
  members cell, the unset-first-declaration discriminator, and the
  uniformity check over all four by-name spellings.
- **`kreset.rxt`** — design §3.4(b)'s three `\K` cells: `\K` inside a
  called body moves the reported start and SURVIVES the return, because
  pcrec spells `\K` as a write to the same slot as group 0's start and `W`
  (the callee's restored slot set) must exclude it.
- **`zerodef.rxt`** — the `X{0}` callee family (plain, recursive, atomic,
  rung-bearing), each against its `{1}` NON-`{0}` twin (the same callee
  emitted lexically once as well as called) — design §4.4c's own control
  shape (`^((?>a)){1}b$` allocates cut marks, `{0}` allocates none). The
  atomic and rung-bearing rows are the LOAD-BEARING ones; the plain row is
  the control that a naive fix would pass vacuously.
- **`leadingzero.rxt`** — design §2.4a's pair on the ANCHORED
  discriminator: `^(a(?01)?b)$` on `"aabb"` is `(0,4)` (group 1),
  `^(a(?00)?b)$` is nomatch (the root) — the whole digit run after `(?` or
  inside `\g<>`/`\g''` is read as decimal, never the first character.
- **`mrl.rxt`** — design §4.4b's fixpoint PAIR: the mutual-recursion
  witness that refuted the withdrawn "least fixpoint over non-recursive
  branches" gloss (must MATCH at every length swept), and the control where
  infinity IS the right answer (must match NOTHING). Neither cell alone is
  the specification.
- **`slotfamilies.rxt`** — design §5.3b's two MEASURED slot families: AXIS
  P (`SLOT_GROUP<n>_PENDING`, a LOST MATCH without it — `^(a(?1)?b)\1$` on
  `"aabbaabb"`/`"aaabbbaaabbb"`) and AXIS C (`SLOT_CUT_MARK<n>`, a FALSE
  MATCH without it — `^((?>a(?1)?))a$`, with `^((?:a(?1)?))a$` as the
  control whose language the false matches would reproduce).
- **`quantified.rxt`** — design §2.6's twelve quantified spellings, the
  empty-body guard (a nullable or empty callee under `*` terminates), and
  `^(?R)*$`'s unconditional give-up (`gu frames`) — no non-recursive branch
  exists, so the empty-iteration guard alone cannot save it.
- **`inlookaround.rxt`** — design §3.4(d)/(e) (a call INSIDE a lookbehind
  needing a width, refusing on a recursive callee; ordinary inside a
  lookahead/atomic group) and §3.5's mirror image (a call TO a group whose
  LEXICAL HOME is a lookbehind/negative-lookahead/atomic-group/lookahead,
  W1/W2/W3/W5, each with its wrapper-isolating control and, where the
  language permits, the inline control). **NO W4 cell** — design §3.5
  withdrew it (the optional group IS emitted, merely not executed); the
  shape it stood in for is `X{0}`, which lives in `zerodef.rxt`.
- **`nocaptures.rxt`** — design §4.3's marked-set cells (one-hop, two-hop),
  written on the ORDINARY (captures-on) axis. **Does not and cannot today
  assert the `--no-captures` axis itself** — see "What could not be
  oracled" below.
- **`d27/`** — NOT this lane's; the blinded corpus is a separate,
  D27-cell-isolated lane (`[DD-14.D27]` in `docs/dev/plan.md`, not started).

## The `gu frames`-vs-`recurse` note (D71.1)

Design §5.6 originally proposed TWO give-up codes: `PCREC_ERR_FRAMES`
(unchanged, the frame-capacity counter) and a new `PCREC_ERR_RECURSE` keyed
on a separate `call_depth` counter. **D71.1 (`docs/dev/decisions.md`)
overrode this**: `PCREC_ERR_RECURSE` is reserved and `ERR_FLOOR` moves
−4→−5 as an ABI fact, but the `call_depth` COUNTER itself is NOT in the
default artifact — it is a diagnostic-generation-axis-only build (`--trace`'s
shape), emitted only when asked for. **The DEFAULT artifact's give-up for a
deep or runaway call is `PCREC_ERR_FRAMES`.** Every `gu` cell in
`leftrec.rxt`/`quantified.rxt` is therefore written `gu frames "<subject>"`,
with a comment recording that the diagnostic-axis variant (once it exists)
would instead read `gu recurse "<subject>"` on the same cell. If Frank
revisits D71.1 (it is explicitly marked revisitable — "a second diagnostic
axis wants the [V-H] namespace"), only that comment needs to flip, not the
cell's pattern or subject.

**THE DIRECTIVE TAKES A SUBJECT, AND AN EARLIER DRAFT OF THIS CORPUS DID
NOT GIVE IT ONE.** The landed wave A grammar (measured directly against
`worktrees/srA`'s `tests/harness/run.sh`, since this worktree's own harness
predates wave A's merge): `^gu[[:space:]]+(steps|frames|work|recurse)
[[:space:]]+"(.*)"[[:space:]]*$` — no bare `gu <code>` form, no `gus`
startpos variant. The manager's review caught this before merge (a bare
`gu frames` line is a hard parse error under the real grammar, same
`unparseable .rxt line` failure this file's own `GU` class docstring now
warns against); fixed in `gen_corpus.py` (the `GU.subj` field, already
carried for the oracle cross-check comment, is now ALSO what gets written
into the directive line) rather than by hand-editing the four `.rxt` lines.
Each subject is chosen for REACHABILITY, stated in the cell's own comment,
and cross-checked against the design's own archived measurement where one
exists (`docs/design/subroutines_measurements/out/leftrec.txt` L2/L3/L6 use
the identical subjects for the identical shapes).

## What could not be oracled

**TWO OF THE THREE ENTRIES BELOW ARE DISCHARGED** by [DD-14] wave B+C and are
kept with their discharge recorded rather than deleted, because each names a
real limit of the `.rxt` format that the next module will meet again. See
"P2's cell is DISCHARGED" and "The `--no-captures` axis is no longer a gap"
above.

- **Every `gu frames` cell's give-up itself.** `gu` asserts pcrec's OWN
  give-up behaviour, which libpcre2 has no equivalent code for — there is
  no oracle to check it against. Each `GU` block instead records what
  libpcre2 itself does on the *same* cell as a comment (almost always its
  own guard, `rc -52`), purely as a shape cross-check, never as the
  assertion. (What COULD be checked, and was: the directive's own GRAMMAR —
  see "The `gu frames`-vs-`recurse` note" above.)
- **`gated.rxt`'s P2 cell** (`(?&n)(?<n>a)` under `--features recursion`
  alone). Design §9.3 predicts this should refuse naming `named-groups`
  once the call itself parses (the declaration `(?<n>a)` is what needs that
  module, reached lexically before the resolver runs). Today, with
  `recursion` having no producer at all, the doorway never gets that far —
  it refuses naming `recursion` itself (`... is enabled but (?&...) is not
  implemented yet`). The `.rxt` `perr` directive only checks a nonzero
  exit code, so this cell PASSES VACUOUSLY today — exactly the S108 masking
  shape the design itself names. **The code lane must re-check this cell's
  message once wave B+C lands the `(?&` parse**, not just its exit code.
- **The `--no-captures` axis for `nocaptures.rxt`.** MEASURED: no `.rxt`
  directive for it exists anywhere in the tree today (`grep -rn
  "no-captures\|nocaps" tests/harness/run.sh docs/testing.md
  tests/*/CLAUDE.md` — `tests/backrefs/CLAUDE.md` says so explicitly).
  Every module that needs this axis carries a SEPARATE shell/C instrument
  compiled with `--no-captures` that inspects the artifact directly
  (`tests/backrefs/run_backref_diff.sh` §4 is the precedent to copy). This
  file therefore pins the ORDINARY-axis behaviour of the marked-set cells
  only; a future `run_recursion_diff.sh`-shaped instrument is what the code
  lane owes to actually compile these under `--no-captures` and assert
  `RX_NCAPS`/slot survival. Reported as a gap, not invented as harness
  syntax, per the lane brief.

## Current harness-run state

**MEASURED ON THIS TREE at [DD-14] wave D's landing**, with
`bash tests/harness/run.sh tests/recursion`:

    cases passed: 371
    cases failed: 0

Fully reconciled, in the four stages the code lane passed through:

| stage | passed | failed |
|---|---|---|
| the corpus as merged, on the pre-B+C compiler | 20 | 273 |
| the ports + the linkage, before any corpus edit | 223 | 70 |
| after the four corrections below (wave B+C close) | 306 | 0 |
| after `gen_corpus.py` sheds `wave='D'` (wave D close) | **371** | **0** |

**THE WAVE D DELTA IS +65, AND IT IS EXACTLY THE 22 `\g` BLOCKS' CELL COUNT.**
The 22 blocks that used to render one `perr` case each now render their real
`m`/`n`/`g` lines — several cells per block for the `g` (group-span)
directives — so the count moved by cells, not by blocks; no block was added
or removed, no expectation outside the `\g` family changed, and `git diff`
over `tests/recursion/*.rxt` at this wave touches only the six files whose
patterns carry `\g<` or `\g'`
(`spellings.rxt`, `relative.rxt`, `whole.rxt`, `leadingzero.rxt`,
`quantified.rxt`, `dupnames.rxt`).

The **20 / 273** row is the corpus's own landing figure and its composition is
unchanged from what this file recorded then: 15 `perr` blocks that genuinely
refused, 3 cases from `spellings.rxt`'s backreference REFERENCE control
(`(a|b)\1`, which needs only the already-shipped `backrefs` module) and 2 from
`inlookaround.rxt`'s W3 INLINE control (which carries no call construct at
all). **The four `gu` lines parse** — this worktree now carries wave A, so the
`unparseable .rxt line` result this file used to record against the LOCAL
harness is gone, and the reconciliation against `worktrees/srA` it needed is
retired with it.

### The four corrections, all made at `gen_corpus.py` and none to an expectation

1. **`dupnames.rxt`'s `features` line gains `backrefs`.** `(?J)` is dispatched
   by module `modifiers`' option-run port and its LETTER is module `backrefs`'
   — the [M6.5] split the compliance page records — so every DUPNAMES cell was
   refusing with *"inline option 'J' (dupnames) requires module 'backrefs'"*
   and the whole file was red for a reason that is not about subroutine calls.
   Design §9.3 names the cell's features and did not follow the letter to its
   own module.
2. **`gated.rxt`'s ENABLED-BUT-UNBUILT section is REPLACED BY ITS POSITIVE
   HALF**, and that replacement is this wave's own deliverable rather than a
   corpus defect: D65 flips `built` from the PORT, so the wave that wires the
   port is the wave that must stop pinning *"module 'recursion' is enabled but
   `(?1...)` is not implemented yet"*. **The generator's own guard said so,
   unprompted, on its first run against the new binary** — *"'(a)(?1)' marked
   kind=pcrec but build/pcrec COMPILES it — the refusal this cell pins does not
   exist"*. The replacement asserts the flip from the OTHER side: the same two
   spellings must now COMPILE and answer §2.1's discriminator, so a compiler
   that merely stopped REFUSING fails.
3. **The 22 `\g` blocks render as `perr` under `wave='D'`** — see the header.
4. **THREE CELLS ARE PARKED** in `tests/known_fail/dd14_bc_open.rxt`, because
   each is a RULING nobody has made rather than a bug. See below.

### P2's cell is DISCHARGED

This file used to record `gated.rxt`'s P2 cell as **NOT OBSERVABLE IN ITS TRUE
FORM** and demand that the code lane re-check its MESSAGE rather than its exit
code. Done, and it answers as design §9.3 predicted: `--features recursion --
'(?&n)(?<n>a)'` now refuses with *"`(?&n)` names a capture group, which
requires module 'named-groups'"*, from the port's own gate check, which sits
BEFORE the name grammar for `br_name_ref`'s reason (without that module there
is no such thing as a group NAME). The row is no longer vacuous.

### The `--no-captures` axis is no longer a gap

This file recorded that no `.rxt` directive for `--no-captures` exists anywhere
in the tree and that the code lane owed a `run_recursion_diff.sh`-shaped
instrument. **It exists**: `tests/recursion/run_recursion_diff.sh` §1 compiles
the one-hop and two-hop cells under the flag and asserts BOTH halves — the
called group's slots survive in the emitted C (the slot legend) AND the matcher
still answers correctly while reporting `RX_NCAPS 1`. Both halves are needed:
the answer alone can be right by accident on a subject the callee's own text
happens to match. `nocaptures.rxt` keeps its ordinary-axis pins beside it.

## The three parked cells (`tests/known_fail/dd14_bc_open.rxt`)

`known_fail` is excluded from `make test` and RUN by the ratchet, which fails
if a cell there starts PASSING — `u9_atomic.rxt`'s shape, and its own header's
principle: *"the cells stay, they stay loud, and if pcrec is ever changed to
reproduce it this file FIRES"*. Each cell's former position in the live corpus
carries a comment stanza pointing here, written by `gen_corpus.py`'s `parked=`
argument so the two cannot drift.

- **`^(a?(?1)b)$` answers NOMATCH, not `gu frames`.** Design §4.4b's `minw`
  Kleene fixpoint gives this callee `minw = infinity` — its language IS empty,
  since `X = a? X b` has no base case — and §12 P-12 RULES that the MRL prune
  reads that as *"no position can match"*. So pcrec refuses the subject in
  constant time where 10.46 spends its own `rc -52` finding out, and §5.9
  scores exactly that pair "agreed in kind". **The class answers two ways**,
  which is what needs a ruling: the two SIBLING cells in `leftrec.rxt` still
  give up, because neither carries a quantifier for an MRL bound to hang on —
  so which answer a left recursion gets depends on whether the pattern happens
  to contain a quantifier, and that is not a fact about recursion.
- **Two calls inside a LOOKBEHIND are OVER-REJECTED** (a tier-2 refusal, never
  a miscompile), and **no `A_CALL` arm of `pcrec_maxw` can fix it**:
  `la_widths` runs in the PARSE HOOK, where it must, because that is the only
  place with a pattern OFFSET to refuse at — and the call graph does not exist
  until every call is resolved at end of parse and every rewriting pass has
  run. Design §3.4(d) says the width analysis descends into the callee and does
  not say WHEN it runs. The fix a ruling would order is a DEFERRED WIDTH
  RE-CHECK, which is a change to a landed module's core plus a new `u.look`
  field for the diagnostic's offset.

## Checks run

- **Idempotency**: `python3 tests/recursion/gen_corpus.py` twice in a row
  leaves `git diff` empty.
- **Independent features check**: a from-scratch regex-over-pattern-text
  deriving required features (never importing `gen_corpus.py`), diffed
  against each block's `features` line. Caught a REAL bug on the first
  pass — the generator's `PERR` blocks had a `gate_features` field used
  only to verify against `build/pcrec` and never written to the `.rxt`
  file's own `features` line, so `gated.rxt`'s "enabled" cells were
  verified under `--features recursion` but WRITTEN with no `features` line
  at all (would have silently tested the closed-gate wording forever).
  Fixed by collapsing to one field; see the `PERR` class's own docstring.
  Of 18 initial findings, 2 were the real bug (now 0) and the remaining 7
  are confirmed-intentional (gate-closed / partial-enablement cells whose
  whole point IS the missing feature — each cross-checked directly against
  `build/pcrec`, not just asserted).
- **Second-path spot verification**: 25 randomly sampled `m`/`n`/`g` cells
  re-derived through a FRESH standalone ctypes binding to
  `libpcre2-8.so.0` (own `CDLL` load, own struct/argtypes, own `.rxt`
  parser and escape decoder) — zero code shared with `gen_corpus.py` or
  `sr_oracle.py`. 25/25 agreed.
- **Harness parse run**: see "Current harness-run state" above — run both
  against this worktree's own harness (pre-wave-A) and, read-only, against
  `worktrees/srA`'s (wave A's real `gu` grammar), because only the second
  can actually validate the `gu` cells.
- **`gu` grammar conformance**: caught by the manager's review before
  merge, not by this lane's own checks — the initial `gu frames` cells
  (design §10.3's directive, described only in prose at the time this
  corpus was first written) omitted the REQUIRED subject the landed wave A
  grammar takes. Fixed in `gen_corpus.py` (see the `GU` class's own
  docstring) and re-verified against `worktrees/srA`'s real parser above.
