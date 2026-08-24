# tests/recursion — module `recursion` ([DD-14])

Subroutine calls: `(?1)`..`(?9)` and beyond, `(?-N)`/`(?+N)` relative forms
(with their leading-zero and relative-zero variants), `(?&name)`,
`(?P>name)`, `\g<N>`/`\g<name>`/`\g<±N>`, `\g'N'`/`\g'name'`, `(?R)`, `(?0)`,
and the two spellings the charter's list did not have, `\g<0>`/`\g'0'`.
Design: `docs/design/subroutines_design.md` (PROPOSED, not yet paneled at the
time this corpus was written). Decisions: `docs/dev/decisions.md` D71 (the
give-up-code diagnostic axis, D71.1 in particular) and D72
(`PCREC_ERR_INTERNAL`).

**NOTHING IN `src/` IMPLEMENTS A SUBROUTINE CALL YET.** This corpus was
written by the wave B+C CORPUS lane running *ahead of* the wave B+C CODE
lane (both concurrent, per `docs/dev/plan.md`'s `[DD-14.BC]` row) — every
`m`/`n` block here is oracle-correct against libpcre2 today and is EXPECTED
to report a pattern-compile failure (`... is enabled but ... is not
implemented yet`) until wave B+C lands. That is `docs/testing.md`'s own
"expected-unsupported" policy working as designed, not a corpus defect —
see "Current harness-run state" below for the exact, reconciled count.

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
`leftrec.rxt`/`quantified.rxt` is therefore written `gu frames`, with a
comment recording that the diagnostic-axis variant (once it exists) would
instead read `gu recurse` on the same cell. If Frank revisits D71.1 (it is
explicitly marked revisitable — "a second diagnostic axis wants the [V-H]
namespace"), only that comment needs to flip, not the cell's pattern or
subject.

## What could not be oracled

- **Every `gu frames` cell's give-up itself.** `gu` asserts pcrec's OWN
  give-up behaviour, which libpcre2 has no equivalent code for — there is
  no oracle to check it against. Each `GU` block instead records what
  libpcre2 itself does on the *same* cell as a comment (almost always its
  own guard, `rc -52`), purely as a shape cross-check, never as the
  assertion.
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

## Current harness-run state (as of this corpus's landing)

`bash tests/harness/run.sh tests/recursion`: **20 cases pass, 273 fail**
(289 ordinary cases + 4 `gu`-directive hard errors = 293 total). Fully
reconciled, not just tallied:

- **20 passes** = 15 `perr` blocks (all genuinely refuse under today's
  built `build/pcrec`, verified live by the generator itself) + 3 cases
  from `spellings.rxt`'s backreference REFERENCE control (`(a|b)\1`, which
  needs only the already-shipped `backrefs` module) + 2 cases from
  `inlookaround.rxt`'s W3 INLINE control (`^(?>(a|ab))z(?:a|ab)c$`, which
  needs only the already-shipped `atomic-groups` module and deliberately
  carries no call construct at all).
- **4 FORMAT failures**, all `gu frames` lines reported `unparseable .rxt
  line (hard error)` — the wave A `gu` directive (design §10.3) has not
  merged into this worktree (this worktree branched off `main` at
  `05d75a9`; wave A landed in a separate lane, `lane/srA`). **A known,
  reported gap, not a corpus defect** — once wave A merges, these 4 blocks
  are expected to parse and then (correctly) still fail to compile, same as
  every other block, until wave B+C lands.
- **269 ordinary case failures** = every remaining `m`/`n`/`g` case,
  reporting `module 'recursion' is enabled but ... is not implemented yet`
  (113 distinct pattern-compile failures) — the correct, expected state per
  `docs/testing.md`'s "expected-unsupported" policy. Zero `requires module
  'recursion'` (std1-closed) refusals appear among the failures, because
  every real corpus block deliberately declares `features recursion` (or
  more) — the closed-gate wording is exercised only by `refused.rxt`'s and
  `gated.rxt`'s own `perr` cells, which pass.

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
- **Harness parse run**: see "Current harness-run state" above.
