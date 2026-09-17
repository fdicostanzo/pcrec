# f2rescue — [O-31 F2] the captures/nullable-decline split (2026-09-17)

MEASUREMENT/ANALYSIS ONLY. Nothing under `src/`. Deliverable:
`docs/dev/f2_rescue_split.md`. `make strict` clean (no src changes; docs +
this report only).

## What was asked

Bench O-31 finding 2: why does the captures axis strip pcrec's
"nullable-collapse rescue" on `trim-nested-star` (×214,356) and
`winpath-near-miss` (×242,483), while `phone-list-nested-plus`'s hybrid
prefilter survives captures (×135,700) — and can the decline boundary
narrow to "declines only when a capture intersects the collapsed
region"?

## What was found — summary (full detail + citations in the memo)

The ask's own premise needed correcting on two points before the
boundary question was answerable:

1. **`trim-nested-star` never reaches the count-collapse rung at all.**
   `(\s+)*` has no counted `{m,n}` to collapse. What fires is a SECOND,
   collapse-agnostic decline ([OPT-4.2]'s `ESEL_DECLINED_NULLABLE_
   DEFAULT`), not the rung-scoped `ESEL_DECLINED_NULLABLE` [OPT-4.1]'s
   comments call "the nullable-collapse rescue." A second corpus
   instance of the same DEFAULT-form decline turned up in the bench's
   own capability set: `evil-alt-nested`.
2. **`winpath-near-miss` is not in either population.** It has zero
   capturing groups; `auto` selects the DFA identically on both capture
   arms. Its ledger row is `auto-caps` vs forced `vm-caps` — the
   unrelated "auto picks correctly, a forced engine doesn't" comparison
   — which the O-31 outbox's "mirrors" phrasing folds together with the
   real captures-axis finding, but the ledger's own §1.2 Finding D prose
   already keeps them separate.

Both decline fields (`prefilter_declined_nullable`,
`prefilter_declined_nullable_default`, `select_engine.c:905-910`) derive
from ONE local, `lang_nullable_declinable` (`:888-889`), which has **no
capture conjunct at all** — `fit.lang_nullable && !has_bref && !has_call
&& !force_on`. Captures matter only as one of several routes that force
`fit.chosen == ENGM_VM` (`forces_captures`, `:99-135`, computed earlier
in the pipeline and entirely independent of nullability); once VM is
chosen by ANY route, the same global test (`pcrec_minw(root)==0`,
`:653`) governs the decline uniformly.

A constructed witness family (`[a-z]{0,60000}` bare / wrapped in a
capture / capture disjoint but pattern still whole-nullable / capture
disjoint and pattern non-nullable) shows something sharper: the
RUNG-scoped decline the ask names is **structurally unreachable whenever
captures are present**. Captures force VM selection before the exact
DFA build the SEL-1 retry mechanism exists to catch the overflow of ever
runs, so the retry — and the rung it creates — never fires. Confirmed
corpus-wide: a full census of the shipped corpus's 3,938 `pattern` lines
(1,500 compile under bare `-p rx`, no extra `--features`) plus the
bench's own 58-pattern `bench/capability/patterns.rxt` (32 compile) finds
56+2 hits on the DEFAULT decline and **zero** on the rung form in
either population, at default flags.

**Verdict on the ask: the boundary cannot narrow by capture location —
not as a small predicate change, not at all.** Two of the three real
witnesses have no "collapsed region" to intersect; the rung form is
already unreachable under captures on any witness; and a constructed
disjoint-capture case (`(x)?[a-z]{0,60000}`, capture outside the
quantifier, whole pattern still nullable via the capture's own
optionality) demonstrates the decline is correctly testing GLOBAL
emptiness-admission — exactly the property that makes a position-skip
prefilter valueless regardless of which subexpression contributes the
nullability. Narrowing to a syntactic "intersects" test would let that
witness's prefilter build and pay the measured 1.2-9.9x loss for zero
rejection power, reintroducing the defect [OPT-4]/[OPT-4.2] exist to
close. `phone-list-nested-plus` was never "escaping" a captures
constraint; `pcrec_minw(root)==1` for it (`\d+` inside the `+`-repeated
group forces at least one byte), full stop, independent of where its one
capture sits — verified live (`RX_VM_PREFILTER_LANG_WHY "no counted
repeat"`, `RX_VM_PRUNE_CEILING "prefilter-window"`, confirming the VM
reruns for captures inside the DFA-prefilter's candidate window, as the
brief asked to verify).

Recommends two design-event candidates instead of a predicate change —
a partial-admission prefilter (can still dismiss some positions under
whole-pattern nullability), and the VM step-budget / give-up O-31
finding 3 already asks about for `evil-alt-nested` (the more general
fix — it helps this whole population without touching engine
selection). Neither built or further measured here (D77): no charter,
no measured need beyond this one finding.

## Validation

- `make -j4 CC=gcc-16`: clean build.
- `make strict`: clean (whole tree, `-Werror -Wshadow`) — no `src/`
  changes in this lane, so this is a smoke check that the tree state is
  sound, not evidence about this lane's own work.
- Every stamp cited in the memo is read live off a freshly compiled
  `--emit-main` artifact from this lane's own build, not copied from the
  bench ledger — the ledger is cited only for the ranking numbers
  (`×214,356` etc.) that this lane did not re-time (per the brief:
  "measure nothing — the bench owns timing; your evidence is SELECTION
  outcomes").
- Corpus census: `find tests -name "*.rxt" | xargs grep -h "^pattern "`
  (3,938 lines, 211 files) each compiled individually with
  `--emit-main` at default flags, `ENGINE_SEL` stamp read off the
  output; bench capability set fetched read-only over the tailnet
  (`ssh duxevents@100.69.121.107 cat .../bench/capability/patterns.rxt`,
  58 lines) and censused the same way. Scripts/raw results kept under
  the session scratchpad (not committed) — reproduction commands are
  inline in the memo (§5) rather than requiring the scratchpad to
  persist.
- No `make test`/`mech`/`san`/`axes` run — out of scope for a
  measurement-only lane with no `src`/`tests` changes, and the box was
  shared with byteid/f3budget/mechfix for this lane's whole working
  period (small builds only, per BOILERPLATE).

## Rulings received

None — no mid-flight questions; the brief was fully actionable as
written once the two premise corrections (§ above) were established
from the code and confirmed against the ledger.

## Scope note

Zero files touched under `src/`, `tests/`, or `docs/spec/`. Deliverable
is `docs/dev/f2_rescue_split.md` + this report + a `docs/dev/CLAUDE.md`
entry (per repo convention: every directory's CLAUDE.md is updated when
a file is added). Read-only ssh probes to the pcrec-bench reference
oracle box for the ledger/outbox/patterns.rxt text, per BOILERPLATE's
light-probe allowance; nothing written to pcrec-bench.
