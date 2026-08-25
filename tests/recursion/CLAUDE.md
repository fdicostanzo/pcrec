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

**`(?(DEFINE)...)` IS THIS MODULE'S SINCE `[DD-14]` WAVE F** (D71 item 4,
overruling design §2.5's "RULED: no DEFINE"). It is a TAILED row on the
`(?(` doorway — tail `DEFINE)` — and everything else at that doorway is
still `conditionals`'. It lowers to the SAME NODE the `{0}`-callee idiom
produces (an `A_REP` with `rmin == rmax == 0` over the body), which is why
`define.rxt` and `zerodef.rxt` carry the two spellings SIDE BY SIDE: they
are two spellings of one construct, and the corpus asserts they agree
rather than assuming it. `tests/codegen/run_codegen_tests.sh`'s rule 4
asserts the stronger form — the two artifacts are identical byte for byte
once the pattern text and offsets are normalised away.

The OTHER files keep the **`{0}`-callee idiom** — `(?:(?<g>BODY)){0}`,
a REPEAT of a GROUP, base syntax — wherever a callee-only body is wanted.
That is deliberate and not an oversight: those cells were oracle-verified
in that spelling, and re-spelling a cell moves a measurement without
re-measuring it.

## Files

- **`refused.rxt`** — the `conditionals` refusals this module does NOT
  unlock: `(?(R)`, `(?(1)`, each pinned by running today's built
  `build/pcrec`. **Wave F rewrote this file's point.** Its two `(?(DEFINE)`
  cells moved to `define.rxt` (the construct is `recursion`'s now), and what
  remains is the SPLIT: the last cell runs `(a)(?(1)b|c)` WITH `recursion`
  enabled and pins that it is still refused — one doorway, two modules,
  and enabling this one must not unlock the other's conditions.
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
- **`leftrec.rxt`** — three EMPTY-LANGUAGE cells (direct, indirect,
  nullable-prefix), the `^(a|(?1)a)$` on `"a"×200` cell that MUST match, and
  the right-recursion contrast. **[DD-14 wave E] ALL THREE EMPTY-LANGUAGE
  CELLS ARE NOW RULED `n`, NOT `gu frames`.** At wave B+C the first two gave
  up and the third answered NOMATCH, decided by whether the pattern happened
  to carry a quantifier for an MRL bound to ride on — a shape with nothing to
  do with recursion. `[DD-14.EMPTY]` removed the non-uniformity at its root:
  `<prefix>_search` compares the remaining subject against the ROOT's minimum
  width and answers NOMATCH before pushing a frame. MEASURED: all three roots
  report `pcrec_minw` = `PCREC_MINW_MAX` (2^40) once `pcrec_callgraph_build`
  has run, and exactly four of the corpus's distinct patterns reach that
  ceiling — these three plus `mrl.rxt`'s infinity control. Sabotage row
  **S169** cuts the site, and its signature is TWO of the three going red:
  the nullable-prefix cell keeps its own `a?` clamp and must stay green.
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
  rung-bearing), each with its `(?(DEFINE)` TWIN (`[DD-14]` wave F: the two
  spellings lower to one node, so the pair is the assertion) and each
  against its `{1}` NON-`{0}` twin (the same callee
  emitted lexically once as well as called) — design §4.4c's own control
  shape (`^((?>a)){1}b$` allocates cut marks, `{0}` allocates none). The
  atomic and rung-bearing rows are the LOAD-BEARING ones; the plain row is
  the control that a naive fix would pass vacuously.
- **`define.rxt`** (`[DD-14]` wave F) — D71 item 4's construct: the library
  idiom itself, a numbered callee inside a DEFINE, the
  body-does-not-run-lexically pair, two definitions in one DEFINE, a
  RECURSIVE callee, a DEFINE placed AFTER its call, an alternation inside
  the defined group, an empty body, a body defining no group, a quantified
  DEFINE, scoped `(?i)` reaching the body, and two DEFINEs in one pattern.
  Plus four refusals: PCRE2's own single-branch rule twice (same wording,
  same offset — `at + 3`), and the pair that shows the tail INCLUDES the
  `)` (`(?(define)` and `(?(DEF)` are name conditions on 10.46, so without
  it this module would have claimed `(?(DEFINED)`). The empty-body and
  group-less-body cells are there because "legal" is the surprising answer:
  the wave's brief expected a refusal and libpcre2 has no such rule.
- **`realworld.rxt`** (`[DD-14]` wave F, `[LIB]` entry #1) — the RFC 5322
  email specimen in all THREE spellings (hand-inlined `orig.rx`,
  `{0}`-factored `factored.rx`, and a `(?(DEFINE)`-factored one) over
  fourteen subjects from the specimen's own manifest. The patterns are READ
  from `docs/design/subroutines_measurements/email_specimen/` and the DEFINE
  spelling is DERIVED from `factored.rx` by the generator — a hand-typed
  third copy of 400 bytes could disagree about one character class and this
  corpus would pin the disagreement. **The 1 MB throughput subjects and the
  deep-repetition set 057-064 are EXCLUDED, with the reason in the file
  header**: five of those measured `PCREC_ERR_FRAMES` on the factored
  spelling at wave B+C, and that number is wave G's and `[FB]`'s to move.
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
  exists, so the empty-iteration guard alone cannot save it. **THE ONE `gu`
  CELL LEFT IN THE CORPUS** after wave E moved `leftrec.rxt`'s two, and the
  contrast is the point: `^(?R)*$` is a genuine RUNAWAY with a base case, so
  its language is not empty and no width bound can rule a subject out.
  **[DD-14 wave E] also carries S157's answer-level witness**: three cells
  with ORDINARY greedy quantifiers over a call, whose backtrack is
  load-bearing (`^(a?)(?1)+a$` and `^(a?)(?1){2}a$` on `"a"` need `(a?)` to
  give its `a` back for the trailing literal). Under sabotage S157 those two
  answer NOMATCH; the third, `^(a?)(?1)*$`, moves `RX_VM_STRATS` 0x2 → 0x3
  with EVERY ANSWER UNCHANGED and is kept as the statement of what a corpus
  CANNOT see — a row resting on it alone stays UNDETECTED for ever, which is
  where wave B+C's search stopped.
- **`inlookaround.rxt`** — design §3.4(d)/(e) (a call INSIDE a lookbehind
  needing a width, refusing on a recursive callee; ordinary inside a
  lookahead/atomic group) and §3.5's mirror image (a call TO a group whose
  LEXICAL HOME is a lookbehind/negative-lookahead/atomic-group/lookahead,
  W1/W2/W3/W5, each with its wrapper-isolating control and, where the
  language permits, the inline control). **NO W4 cell** — design §3.5
  withdrew it (the optional group IS emitted, merely not executed); the
  shape it stood in for is `X{0}`, which lives in `zerodef.rxt`.
  **[DD-14.LB] grew it from 3 blocks to 21**, when the deferred width
  re-check landed: the seven-cell call-bearing family (a bare call, a call
  with literals around it, a two-hop acyclic chain, an alternation OF calls at
  the body's own top level entered through both branches, the NEGATIVE
  polarity, a call inside a nested lookahead), the three mixed
  call-free/call-branch cells, §2.4's BRANCH-ORDER pair, and four `perr`
  blocks (the ruled 1..2 capability limit, self-recursion, mutual recursion,
  and an acyclic callee that REACHES a cycle).
- **`run_lookbehind_call_sweep.py`** — [DD-14.LB], ON-DEMAND, not part of
  `make test`. The NET beside `inlookaround.rxt`'s aimed questions: 908
  generated patterns (11 callee width-classes x 14 lookbehind body templates x
  both polarities) x 22 subjects, every cell asked of libpcre2 and of a real
  compiled artifact. It exists because the corpus above inherits its author's
  alphabet — D27's own finding — and a product space does not.

  **ITS VERDICT IS A CLASSIFICATION, NOT A PASS COUNT**, and that is the part
  worth reading before running it. A pattern libpcre2 compiles and pcrec
  REFUSES is not a failure: PCRE2 10.43+ ships variable-length lookbehinds and
  `lookaround_design.md` §2.5 charters that loop rather than shipping it. What
  the sweep checks is that every such refusal is the §2.5 WIDTH refusal — never
  a crash, an internal error, a give-up, or a diagnostic naming the wrong
  module (`bad_refusal`, which must be 0). The opposite direction,
  `pcrec_only` — pcrec compiling what libpcre2 refuses — must be 0 too, and it
  is the one that would mean the width rule had gone soft.

  MEASURED at [DD-14.LB]: 9,240 cells compiled by both, **9,240 agree, 0
  disagree**; 220 pcrec-refuses with **bad_refusal 0** (all 220 carry the one
  §2.5 sentence, and every refused callee is variable-width — `a?`, `a|bc`,
  `a*`, or a body built from one); 268 both-refuse; 0 pcrec-only; 0 build
  failures; 0 give-ups.
- **`prefilter.rxt`** — **[DD-14 wave E]** design §8.2's own counterexample:
  `a(?1)b` with group 1 = `x` matches `"axb"`, and the call-ERASED pattern
  `ab` does not — so the erasure is a DIFFERENT language, not a superset, and
  `select_engine.c` forces `fit.prefilter` OFF whenever `pcrec_has_call`.
  The counterexample runs through all three doorways (`(?1)`, `\g<1>`,
  `(?&w)`), because `pcrec_has_call` is an AST predicate and a wiring that
  reached only one port would pass one block and fail the others. **THE CELLS
  ARE UNANCHORED ON PURPOSE**: the prefilter exists to find a candidate
  START, so an anchored pattern never asks it anything and would go green
  under the very sabotage (S165) these cells exist to catch. §8.3's R09 pair —
  the inlined `(cat)xcat` (call-free, prefilterABLE today) beside its call
  form `(cat)x(?1)` — is the control that says the two differ by the CALL and
  by nothing else, and is where a wave-G splice regression lands first.
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
deep or runaway call is `PCREC_ERR_FRAMES`.** Every `gu` cell is
therefore written `gu frames "<subject>"`, with a comment recording that the
diagnostic-axis variant (once it exists) would instead read
`gu recurse "<subject>"` on the same cell. **[DD-14 wave E] THERE IS EXACTLY
ONE SUCH CELL LEFT** — `quantified.rxt`'s `^(?R)*$`. `leftrec.rxt`'s two moved
to ruled `n` when `[DD-14.EMPTY]` landed, and the difference between the two
kinds is worth keeping straight: a `gu` cell is right for a genuine RUNAWAY,
which has a base case and a non-empty language and which no width bound can
rule a subject out of; a ruled `n` cell is right for an EMPTY language, where
`minw` reaching the ceiling is a compile-time fact about every subject. If Frank
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
4. **NO CELL IS PARKED ANY MORE.** Wave B+C parked three in
   `tests/known_fail/dd14_bc_open.rxt`; [DD-14.LB] closed the file and all
   three cells are live here. See below.

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

## The three formerly-parked cells — CLOSED by [DD-14.LB]

`known_fail` is excluded from `make test` and RUN by the ratchet, which fails
if a cell there starts PASSING — `u9_atomic.rxt`'s shape, and its own header's
principle: *"the cells stay, they stay loud, and if pcrec is ever changed to
reproduce it this file FIRES"*. **All three cells wave B+C parked have now
left, by three different doors, and the three doors are the point.**

- **`^(a?(?1)b)$` answers NOMATCH, not `gu frames`** — and it was A CORPUS BUG
  rather than an owed ruling (removed 2026-08-24 on manager review, before the
  other two). Design §4.4b's `minw` Kleene fixpoint gives this callee
  `minw = infinity` — its language IS empty, since `X = a? X b` has no base
  case — and §12 P-12 RULES that the MRL prune reads that as *"no position can
  match"*. So pcrec refuses the subject in constant time where 10.46 spends its
  own `rc -52` finding out, and §5.9 scores exactly that pair "agreed in kind".
  The parked expectation could not have come from libpcre2 at all: **a give-up
  is pcrec's own artifact behaviour, never an oracle fact.** The cell is live
  in `leftrec.rxt` as a RULED nomatch, rendered by `gen_corpus.py`'s `GU` block
  with `code=None` plus a required `ruling=` citation.

  **[DD-14 WAVE E] AND THE CLASS IT BELONGED TO IS CLOSED TOO** — the cell was
  a corpus bug, but the reason its two SIBLINGS disagreed with it was a real
  gap. `^((?1)a)$` and the indirect p/q cycle have the same empty language and
  the same infinite root `minw`, and they gave up where this one answered in
  constant time, because an MRL bound has to be EMITTED somewhere and only this
  cell's `a?` carried a quantifier for one to ride on. `[DD-14.EMPTY]` removed
  that at the root: `<prefix>_search` compares the remaining subject against
  the ROOT's minimum width before pushing a frame, so all three answer alike
  and both siblings are ruled `n` cells now. It is the general MRL bound
  applied at the root and not an empty-language special case, which is why it
  is a WIDTH COMPARISON and not an unconditional `return 0` — `PCREC_MINW_MAX`
  is reached by SATURATION as well as by the fixpoint's infinity, and the value
  cannot tell the two apart. **The measurement that moved the SITE**: asked at
  `pcrec_select_engine`, where the plan row put it, `pcrec_minw(root)` is 1, 1
  and 0 on the three siblings — the arena's zero, because
  `pcrec_callgraph_build` has not run yet — so a root check there could never
  fire. Asked in the emitter it is `PCREC_MINW_MAX` on all three. Sabotage row
  **S169** cuts the site, and its signature is TWO of the three going red: this
  cell keeps its own `a?` clamp and must stay green.
- **Cell 1, `^(?:(?<g>ab)){0}ab(?<=(?&g))$`, was parked correctly and its
  charter was right.** A tier-2 over-rejection caused by TIMING: `la_widths`
  runs in the PARSE HOOK, where it must, because that is the only place with a
  pattern OFFSET to refuse at, and the call graph does not exist until every
  call is resolved and every rewriting pass has run — so no `A_CALL` arm of
  `pcrec_maxw` could have fixed it. [DD-14.LB] built the DEFERRED WIDTH
  RE-CHECK the note asked for (`u.look.at` records the offset,
  `widths == NULL` on a lookbehind means pending, and `pcrec_postresolve` —
  src/opt/postresolve.c — re-asks module `lookaround`'s own rule after
  `pcrec_callgraph_build`). The cell is a live match cell in
  `inlookaround.rxt`.
- **Cell 2, `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$`, WAS PARKED WITH THE WRONG
  CAUSE**, and this is the entry worth reading twice. It was parked alongside
  cell 1 as the same timing over-rejection, with a note calling it *"the
  fixed-PER-BRANCH form pcrec ships"*. It is not. Its lookbehind body is ONE
  top-level branch — an `A_CALL` — of width 1..2, because the alternation lives
  inside the CALLEE; that is `(?<=(a|bc))x` reached through a call, which
  `lookaround_design.md` §2.5 CHARTERS the longest-first step-back loop for and
  does not ship, and which `tests/lookaround/refused.rxt` has pinned as a D26
  tier-2 CAPABILITY limit all along. Fixing the timing left the refusal
  standing and changed the SENTENCE — from *"this one is unbounded"*, a claim
  about the call graph and false, to *"this one can match 1..2 characters"*, a
  claim about the shipped subset and true — at the same offset. That diagnostic
  is the entire evidence that separated the two cells. It is now a live ruled
  `perr` in `inlookaround.rxt`, and the fixed-per-branch form its note MEANT to
  describe is a live match cell beside it (`(?<=(?&g)|(?&h))`, widths 1 and 2,
  alternation at the body's own top level).

**THE LESSON, stated so it outlives these three cells: a parked cell's stated
CAUSE is a claim, and it can be wrong even when the disagreement is real.
Discharging the named cause is not the same as closing the cell — re-measure
before assuming the two coincide.**

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

## [DD-14 wave G] What this directory gained, and what moved

**`run_recursion_diff.sh` HAS A §5**, and it is design §9.2's SECOND CONTROL —
the one this module has and `lookaround` did not. Every `pattern` line under
this directory, deduplicated, built on BOTH LINKAGES (default, and
`-fno-splice-calls`) and swept over §3's own 24-subject x every-startpos grid,
comparing the span AND every `RX_NCAPS` group pair. It sweeps the CORPUS rather
than a list, which is the OPPOSITE choice from §3's and is deliberate: §3's 16
rows each defend a MEASURED claim, so writing them down IS the point, while
§5's claim is about a POPULATION and a hand-written list is exactly how such a
claim goes green while covering less than it says. A pattern that refuses must
refuse on BOTH arms — a one-sided refusal is a wave-G bug wearing a skip's
clothes, so it is a FAILURE and not a `continue`. **MEASURED: 156 of 170
patterns built on both linkages (14 refused on both), 15,912 cells, 0
disagreements.**

**TWO OF ITS SECTIONS MOVED, AND BOTH MOVES ARE THE CLAIM CHANGING RATHER THAN
THE CHECK WEAKENING.**

- **§1's SLOT-SURVIVAL half is pinned on `-fno-splice-calls`**, which is the
  only axis it was ever about. It greps the emitted C for
  `RX_SLOT_GROUP<n>_START` — a fact about the VM's SLOT LAYOUT — and after wave
  G `--no-captures '(a)(?1)'` has no live capture and no linked call, so it
  compiles to the DFA ENGINE, which has no layout at all and where the grep
  would report a deleted group where there is simply no VM. The flag forces the
  LINKAGE, which forces the VM, which is where the marked set is observable.
  The DEFAULT build is run beside it as a one-cell `A == B`, so the ANSWER half
  is asserted on both engines.
- **§4 is THREE cells now.** §8.1's `aⁿbⁿ` argument is structural for a
  RECURSIVE callee and merely conservative for an acyclic one, so: recursion
  still refuses `--engine=dfa` BY NAME; a SPLICEABLE call COMPILES; and
  `-fno-splice-calls` puts the second back to a refusal that names the
  construct. The third is what makes the second evidence about the LINKAGE
  rather than about the construct having quietly stopped being VM-only.

**THE WHOLE CORPUS RUNS ON BOTH ARMS** through `tests/harness/run.sh`'s new
`RXTFLAGS` env var: `RXTFLAGS=-fno-splice-calls bash tests/harness/run.sh
tests/recursion` is 593/0, the same as the default arm. That is `A == oracle`
and `B == oracle` against this corpus's own libpcre2-generated expectations,
which is strictly more than `A == B`.

**AND `realworld.rxt`'s EXCLUSION NOTE IS DISCHARGED WITHOUT AN EDIT TO IT.**
That file's header excludes the deep-repetition subjects 057-064 because five of
them measured `PCREC_ERR_FRAMES` on the factored spelling at wave B+C, and says
that number is wave G's and `[FB]`'s to move. `run_specimen_identity.sh` runs
**all 85 subjects, those eight included**, on all four spellings and asserts NO
GIVE-UP anywhere — so the claim is discharged by the instrument that owns the
whole specimen rather than by re-generating a corpus file, which would have
moved a measurement without re-measuring it (this directory's own rule about
re-spelling a cell).
