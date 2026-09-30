# [ENG-LOOK] step 0 — fixed-length (k=2-4) lookaround state-growth census

Lane `lacens2` (sonnet), branch `lane/lacens2`, worktree `worktrees/lacens2`,
on `lane/ucpu2` at `61cbc894`. MEASUREMENT lane: nothing under `src/`. Answers
plan.md's [ENG-LOOK] STEP 0 (filed `eee1d36a`): over the lookaround census
population, the FIXED-LENGTH lookarounds of 2-4 characters, counted by
length and direction, with the state growth a product construction (the
plan row's own mechanism) would cost, "estimate before committing" per D77.

Script `docs/dev/lookaround_census/eng_look_growth.py`, engine
`docs/dev/lookaround_census/lac_engine.py` (own CLAUDE.md).

---

## 0. Headline

**The population is small and thin on real-world diversity: 98 candidate
occurrences (56 k=2, 40 k=3, 2 k=4 — `lookaround_census.md` S3's own
count), 97 of which compile (1 skip: a 1.08 MB bench pattern that exceeds
pcrec's own emit-size limit before any lookaround product is even added),
almost all drawn from `tests/lookaround/*.rxt` fixtures and one
systematically-enumerated boundary matrix (72 of 98). Where the
construction is well-defined (LOOKBEHIND — see S2), state growth is real
but small in absolute terms: baseline DFAs of 2-3 states grow to 3-10
states, i.e. +1 to +8 states per fold, nowhere near the 32,000/10,000-state
caps this row's own charter worries about.**

**For LOOKAHEAD the census surfaced a genuine mechanism problem, not just a
number (S3): the brief's literal construction (a product against pcrec's
own REVERSE machine) measures ZERO state growth in ALL 43 cases, because
pcrec's reverse machine only walks the MATCHED span end-to-start and a
lookahead's body sits PAST the match end — a region that machine never
scans today.** plan.md's own ENG-LOOK mechanism text says bounded
lookahead folds into the FORWARD pass as a "k-byte delayed acceptance"
instead; built and measured here too (S3), but composing it correctly
(only at the pattern's actual assertion point, not from the whole
machine's start state) is real design work this script does not attempt —
its own number is a model, not a clean bound. The one REAL fact from that
half: the delayed-accept body automaton itself is small, 3-5 states for
k=2-4.

**Verdict against D77 (S5): the STATE-COUNT budget is not what would
justify building this — every number measured or modeled here is small.
What is unresolved is the MECHANISM for lookahead, and the population
that would exercise it in earnest is not there yet (this census's own
98 candidates are 72 from one boundary-matrix file and ~20 near-trivial
test fixtures). Recommend: no build from this step 0 alone; a real
design pass (the D6 panel plan.md already schedules) is needed to settle
lookahead's fold point before any state-growth number is decision-grade,
and a NEW measurement over a less test-fixture-dominated population — the
[CTX-PREFILTER]/[OPT-VMLIT]-style corpora, or fresh bench patterns — would
be the trigger to revisit.**

---

## 1. Method

**Population.** `docs/dev/lookaround_census/shapes_9399d927.tsv` (the same
493-pattern census [CTX-PREFILTER] and `lookaround_census.md` use), filtered
to the `ks` column (shape-(b), fixed width) equal to 2, 3, or 4 — 98 rows
(56/40/2), matching S3's own per-occurrence k-distribution exactly (no
pattern in this population carries more than one shape-(b) occurrence — no
comma-joined `ks` values found). All 98 are byte encoding, 0 caseless
(checked before writing any byte-alphabet code).

**Erasure.** For each candidate pattern, EVERY lookaround occurrence
(not only the k=2-4 target) is cut from the pattern text
(`lac_engine.erase_occurrences`, a balanced-paren walk mirroring
`shape_classify.py`'s own `_group()`, PLUS a fix this run found live:
the walk must also consume a trailing quantifier on the construct itself
— `(?<=abc)*z` erases to `*z`, a dangling quantifier pcrec correctly
refuses as "does not follow a repeatable item"; 12 of the original 98
candidates hit this before the fix, 0 after). The erased pattern is
compiled `--engine=dfa --no-captures --features all` — a REAL pcrec
compile, giving a clean DFA baseline. **Model, stated plainly**: erasing
EVERY occurrence (not just the target) and re-adding only the target's
product measures the MARGINAL cost of folding in ONE bounded lookaround
while holding any others erased — not the real shipped cost of a
multi-occurrence pattern with every occurrence folded.

**State extraction.** pcrec's own generated C is parsed directly
(`lac_engine.parse_pcrec_tables`): the `rx_forward_*`/`rx_reverse_*`
`byte_class[256]`/`next_state[]`/`is_accepting[]` arrays, confirming
`RX_DFA_TABLE "premultiplied"` empirically (state IDs are
`0, n_classes, 2*n_classes, ...`; `65535` is dead). `n_before` is the count
of LIVE (non-dead) states reachable by BFS from state 0 — real, not
modeled.

**Body automaton.** `lac_engine`'s own atom parser (independent of
`shape_classify.py`'s width-only reading, by the same discipline
`lookaround_census.md` S1 uses) resolves each body to a byteset per atom
(literal, `.`, bracket class, `\d`/`\w`/`\s`/... shorthand, and one
`(?:...)` group case — the sole one in this population,
`(?<=(?:ab){2})x`), REFUSING (not guessing) anything it cannot resolve. All
98 resolved cleanly. Three constructions, all real subset-construction/
trie builds, no guessed sizes:

- `build_ends_with_dfa` — the Aho-Corasick-style Sigma*.L "ends-with"
  automaton (a KMP failure-function automaton built directly from the trie,
  not via NFA epsilon-closure), for LOOKBEHIND against the FORWARD machine
  (plan.md's own pairing: a lookbehind is a property of the
  already-consumed prefix, which the forward scan walks through).
- `build_starts_with_dfa_reversed` — the SAME construction over each
  branch's atoms REVERSED, for LOOKAHEAD against the REVERSE machine (this
  census's brief, LITERALLY: "reverse(L)*Sigma* in the reverse machine").
- `build_delayed_accept_dfa` — plan.md's OWN stated mechanism instead:
  "bounded lookahead in the forward pass as a k-byte delayed acceptance" —
  the body's own verify-next-k-bytes automaton (no Sigma* search prefix,
  no failure-function fallback: a byte that does not continue any branch
  is DEAD, not redirected).

**Product.** `lac_engine.product_reachable` — an exact BFS over LIVE
reachable (base_state, body_state) pairs, byte by byte (0-255) against
pcrec's own real transition table and the body automaton above, dropping
a pair the instant either side dies. `n_after` is the pair count; never the
`n_before * n_body` upper bound (also reported, as `upper_bound`).

---

## 2. S2: lookbehind — the reliable measurement

54 occurrences, `build_ends_with_dfa` composed with the FORWARD
erased-pattern machine — a correctly-scoped product (the forward machine
DOES scan the whole matched region, including the lookbehind's own
asserted text, since it is part of the ALREADY-CONSUMED prefix):

| k | n | n_before (min/mean/max) | n_after (min/mean/max) | max growth |
|---|---:|---|---|---:|
| 2 | 33 | 2 / 2.1 / 3 | 3 / 5.9 / 10 | +8 |
| 3 | 20 | 2 / 2.1 / 3 | 5 / 5.2 / 6 | +3 |
| 4 | 1 | 2 / 2.0 / 2 | 6 / 6.0 / 6 | +4 |

Overall: `n_before` min 2 / mean 2.1 / max 3; `n_after` min 3 / mean 5.7 /
max 10; growth min +1 / mean +3.5 / max +8 states; ratio (n_after/n_before)
up to 5.0x but on tiny absolute bases — **every measured lookbehind product
in this population fits in 10 states or fewer.** The 18 non-matrix.rxt
rows (real `tests/lookaround/*.rxt` fixtures, not the boundary matrix) read
the same shape: `n_before` is 2 in every one of them (these are minimal
test patterns — `(?<=ab|cd|ef|gh)x|q` and similar — with almost no
surrounding structure), `n_after` 3-10. **The population itself is thin on
non-synthetic diversity** — no bench-derived lookbehind pattern survived
past the one oversized bench witness that was skipped.

---

## 3. S3: lookahead — a mechanism problem, not a clean number

86 occurrences, two constructions each (43 x 2 = 86):

| method | n | n_before (mean) | n_body (mean) | n_after (mean) | growth (min/mean/max) |
|---|---:|---:|---:|---:|---|
| `reverse_sigma_star_brief` (this census's own literal spec) | 43 | 2.65 | 4.35 | 2.65 | **0 / 0.00 / 0 — every single row** |
| `forward_delayed_accept` (plan.md's own stated mechanism) | 43 | 2.63 | 4.35 | 4.33 | -8 / +1.70 / +3 |

**`reverse_sigma_star_brief` reads flat because it is measuring the wrong
machine, not because lookahead is free.** pcrec's reverse machine
(`RX_DFA_START "reverse-pass"`) walks ONLY the matched span, backward from
`last_accept_position` to `search_from`, to find the match START — a
lookahead's body is entirely PAST `last_accept_position` (zero-width,
consumes nothing), so the reverse machine as it exists today never
traverses it at all. Composing a body recognizer against it is composing
against a machine with no reason to grow. This census's own literal
instruction (matching the brief this lane received) produced a clean,
reproducible, WRONG-SHAPED answer — recorded here as the finding, not
silently corrected away.

**`forward_delayed_accept` is the RIGHT automaton (plan.md's own words) but
composed the WRONG WAY here.** This script folds it against the erased
machine from STATE 0 (the pattern's own start), not at the specific state
where the assertion actually occurs mid-pattern — `build_delayed_accept_dfa`
has NO restart-on-mismatch edge (a byte that does not continue the body
kills that path permanently, by design: it is a verifier, not a search),
so composing it from state 0 cuts off large parts of the base machine a
correctly-scoped fold (engaging the sub-automaton ONLY at the assertion's
own position) would never touch. This is why growth can read NEGATIVE
(`n_after < n_before`, min -8) — an artifact of this script's simplified
whole-machine composition, not a real state SHRINKAGE; no product
construction produces fewer live states than either input alone once
correctly scoped. **The one number from this half that IS trustworthy:
`n_body` — the delayed-accept sub-automaton's own size, 3-5 states for
k=2-4 — telling us the marginal machinery a correctly-scoped fold would
need to thread in in is small, regardless of exactly where in the pattern
it attaches.**

---

## 4. S4: unresolved / skipped

One pattern-level skip: `capability/wild-logparse-syslogbase-expanded`
(the bench's ~2 KB timestamp/hostname/IP regex) — its erased form alone
emits 1,075,611 bytes of C, over pcrec's own 1,000,000-byte limit, before
any lookaround product is added. Not a finding about lookaround folding;
this pattern is already at the edge of what pcrec's DFA path can emit at
all (`docs/dev/artifact_size_census.md`'s own territory). Zero body-atom
resolution failures — every k=2-4 body in this population is a literal/
class/shorthand concatenation or alternation, well within
`lac_engine`'s deliberately narrow atom parser (see its own CLAUDE.md
entry / module docstring for exactly what it does and does not resolve).

---

## 5. Verdict (D77)

State growth for the population actually measured is small in every
dimension tried — lookbehind products top out at 10 states, lookahead's
own body automaton tops out at 5. Nothing here approaches the
32,000/10,000-state caps, so a STATE-COUNT budget argument does not block
this row. What DOES block it: (1) the population is 72/98 from one
boundary-enumeration test file and the rest near-trivial fixtures — no
real customer pattern in this census exercises k=2-4 lookaround at any
meaningful scale; (2) the LOOKAHEAD mechanism itself is not yet a settled
design — this step 0 found that the naive product-with-today's-existing-
machine approach is wrong-shaped in BOTH directions tried (the reverse
machine literally cannot see the asserted text; the forward-delayed-accept
construction needs to attach at the assertion's own position, not the
pattern's start, which is a real design task). **Recommend: do not build
from this measurement alone. The design gate plan.md's ENG-LOOK row
already names (a D6 panel, after [M6.6] ships VM semantics) is where the
lookahead attachment-point question gets resolved; a fresh state-growth
measurement against a real population (once one exists — [CTX-PREFILTER]'s
own census or fresh bench patterns) is the trigger to re-run this script.**

---

## 6. Reproducing

```
python3 docs/dev/lookaround_census/eng_look_growth.py build/pcrec /tmp/OUTDIR
```
from the repo root (needs a built `build/pcrec`; no boxlock, no network,
~1-2s). Writes `eng_look_growth.tsv` (one row per occurrence x method) and
`eng_look_skipped.tsv` to OUTDIR. This memo's own run is committed at
`docs/dev/lookaround_census/eng_look_growth_61cbc894.tsv` /
`eng_look_skipped_61cbc894.tsv` (commit `61cbc894`, the branch point).
