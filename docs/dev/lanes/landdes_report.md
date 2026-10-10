# Lane `landdes` — the design of `[START-LANDING]`

**2026-10-09, opus. DESIGN + HAND-TWIN only: nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changes.** Branch `lane/landdes`, cut from main `e1e387b9`
(abi 71). Deliverables:
- `docs/design/start_landing.md` (the note, with "where to attack" per section);
- `studies/start_landing/` (own CLAUDE.md: the fact-probe patch, census, twin
  transformer, identity driver, controls, timing, results);
- index entries in `docs/design/CLAUDE.md` and `studies/CLAUDE.md`.

## Summary (what a resuming agent needs)

**The rows.** RECOVER becomes `pinned`, `end-minus-width`, `landing`, `reverse-pass`.
Both new rows hand `SPAN` exactly as `reverse-pass` does. Each is proved to return
EXACTLY today's reverse-pass start on every call, so:
- PCRE2 agreement is inherited;
- the deny build is a genuine control (an independently built machine);
- hybrids are NEUTRAL by window identity, verified per prefilter call.

**(a) The fact (§2).** The survey's statement, "every start-set byte takes the anchored
machine to accepting", is too narrow under utf8: a lead byte alone accepts nothing, and
the largest K4 cells are utf8 `.`/`\p{L}+`. The built fact is **Λ, the ONE-CHARACTER
fact**:
- every one-character path from `Nfa.anch_start` ends dead or unconditionally
  accepting, with an exact closure where an assertion is a decline;
- the pattern is not nullable;
- multibyte encodings: no continuation byte is in the start set.

Proof: §2.4 (Lemma 1, fresh at every landing; Lemma 2, the first accept is the
landing thread's; the Theorem).

Under the invalid-tolerant utf8 contract one guard is owed. An ill-formed FIRST
character at the landing re-enters the forward scan at `landing + 1`: a RAISE edge,
E5's shape, measured free.

Owner: `src/facts/kset.c`, a new E3 fact. The EXACT condition (the "excursion"
condition, a product walk over the emitted F) is FILED: its measured upper bound
over Λ on the bench is 0.58 ms of 54.6 ms (§2.8).

**(b) `end-minus-width` (§3).** A fixed BYTE width from the same NFA walk, with
assertions passed (sound superset). It is exact for any VERIFIED end, ill-formed
input included; `$`/`\Z` do not touch it.

The interaction is REVEND. `rev-end`'s walk asks RECOVER with a SPECULATIVE end, so
RECOVER asks gain FINISH's `hand` filter: `END` vs `SEED`. Only `reverse-pass` takes
`SEED`. A sibling LOCATE row, `rev-end-width` (an AT at `n − W` to `verify-at`), is
filed on REVEND's side.

**(c) Rows and readers (§4).**
- Order: `end-minus-width` before `landing`. Measured indistinguishable where both
  apply; generality decides.
- `u.recover.pinned` becomes a four-valued `act`.
- `.needs` omit R, so L0's member fold drops the reverse machine with no stamp edit.
- `RX_DFA_START` already reads RECOVER's selection, so this does not need L2.1.
- Two deny-only bits, masked from `rx_info.flags`. The listing is `search-start`
  1..4.
- One abi event. The readers by grep are in §4.5: the abi number, the stamp-value
  sentences (including the registry anchor phrase "which of two forms", which names
  a count), the deny-chain expectations, byte-count readers, S218-S222/S693
  re-anchors, and the pcrec-bench adapter's CLOSED `dfa_start` enum
  (`testees/pcrec/adapter.py:804`) plus its report legend and trend META key.

**(d) Identity (§5).** Twins in ASSERT mode keep the reverse pass and count
row ≠ reverse-pass PER CALL of the DFA body (the search, or a hybrid's inlined
prefilter).

| population | rows | cells | twin ≠ artifact | per-call compares / diffs | NEW libpcre2 disagreements | find-all calls / diffs |
|---|---|---|---|---|---|---|
| bench, every selected row, default + nocaps | 310 | 91,519,182 | 0 | 50,130,712 / 0 | 0 (14,504 pre-existing K74, identical both sides) | 30,317,336 / 0 |
| of which hybrids | 33 | 9,296,618 | 0 | 2,742,756 / 0 | 0 | 1,270,273 / 0 |
| corpus, every selected row, default config | 1,750 (+1 NOT-TWINNABLE, F-L4) | 169,952,746 | 0 | 143,323,191 / 0 | 0 (43,440 pre-existing: the PCRE2 `(()|^){0}` quirk, K74, capacity give-ups; identical both sides) | 56,164,734 / 0 |
| of which hybrids | 637 | 70,893,458 | 0 | 65,703,299 / 0 | 0 | 17,892,005 / 0 |

Controls FAIL as they must (`results/controls.txt`):
- `x*y`, `xa|a` and `ab|x*y` forced through `landing`: up to 55,152 wrong answers,
  each a new libpcre2 disagreement;
- utf8 `.{3,8}` (multi-character excursion, tolerant utf8);
- the guard removed on utf8 `.`, `\p{L}+`, hybrid `(.)`;
- `W + 1` on `abcd`, utf8 `é`, hybrid `(\d{4})`.

**Timing (§5.4), directional.** Loaded box (load1 11-12), 7700X, two runs, n = 21 per
variant. Median Δ: utf8 `.` −42%, `\p{L}+` −35%, `abcd` −37/−38%, `\w+` −29/−30%.
All clear 2(σa+σb) except `\w+`, whose σ is one cold 5.5 ms outlier, reported as
measured. The guard costs nothing measurable.

**(e) Predictions (§6).** The rows take 46.5 of 54.6 ms K3+K4 weight (default config;
`landing` 42.6, `end-minus-width` 3.9). Utf8 `\p{L}+` 11.8 → ~7.6 ms, utf8 `.` 13.1 →
~7.6, `\w+` 7.1 → ~5.0 (twin ratios over older-pin Ryzen 1600 medians).

**(f) Build (§7).** After L0:
- B1: the two facts, a no-mover;
- B2: the rows, record, guard and readers, the abi event;
- B3: the RECOVER hand, unless REVEND's L2.2 carried it;
- B4: the bench relay.
9 sabotage rows.

## Questions for Frank (in the note's §9, as discussion with a leaning)

1. Λ now, the excursion condition filed (leaning: yes; ≤ 0.58 ms extra).
2. The tolerant-utf8 guard against `-futf-check`-only (leaning: the guard).
3. RECOVER asks carry a hand (leaning: yes, built by whichever of this and L2.2
   lands second).
4. `end-minus-width` before `landing` (leaning: yes; LR-G10's order is the other
   defensible reading).
5. File `rev-end-width` on REVEND's side (leaning: file).

## Where the panel should attack first

- §2.4 Lemma 1 against every emitted scan shape: the edge path's `goto` to the view
  label, and a pre-accept head whose `scan_next` is `s0`.
- Λ.2 under `-i` + utf8 folding.
- The guard's "only the final landing" argument.
- L3 asserted rather than tested.
- §3.3's hand filter as the only thing between `end-minus-width` and a wrong answer on
  `rev-end` paths after L2.2.
- §4.5's reader list: re-run the grep.

## Findings for the record

- **F-L1 (survey correction).** The survey's K4 fact as worded excludes every
  multibyte utf8 pattern. Its twin (`landtwin.py`) recorded the LAST landing, which
  is right, but the stated fact was the byte form. Without the §2.5 guard the twin is
  wrong on ill-formed utf8 (`C3 61`: `(0,2)` vs `(1,2)`); the survey's twin was
  answer-checked only on well-formed bench subjects.
- **F-L2 (REVEND interaction, owed by whichever lands second).** `locate_finish.md`
  §4.1 has `rev-end` asking RECOVER. Without a hand on the ask, `end-minus-width`
  would be selected there and answer an unverified `n − W`.
- **F-L3 (pre-existing).** K74 (`$`/`\B` at an ill-formed subject END) shows up as
  14,504 cells of `utf8/asr-b-midchar` (`\B`) against libpcre2 on the exhaustive
  ill-formed pool. It is identical in the artifact and the twin. Witness: `\B` on
  `61 C3`, pcrec `(2,2)`, libpcre2 no match. Known, deferred.
- **F-L4 (census limit, fixed in the script).** A compile whose LAST probe line came
  from an abandoned fit-ladder attempt (a size-cap prefilter drop) was counted as a
  mover. One corpus row (`tests/uprops/size_ladder_prefilter_drop.rxt:15`, default)
  surfaced as NOT-TWINNABLE. `census.py` now reads the emitted artifact for a DFA
  body. The committed census TSVs predate the fix, so the corpus mover counts may be
  over by such rows; B2's `emit_sweep` re-derives the movers anyway.
- **F-L5 (observation).** The survey's "first byte the forward machine stepped"
  measure and the twin's "last landing" are different quantities. The 85.7% figure is
  the first; the row needs the second. On Λ patterns they coincide.

## Validation status

- **COMPLETE**:
  - the bench twin sweep (310 rows);
  - the residual forced-landing sweep (117 patterns);
  - the controls;
  - two timing runs;
  - the bench and corpus censuses;
  - the corpus twin sweep (1,750 rows, 143.3 M per-call checks, 0 differences,
    `MAXSUBJ=12000`).
- Nothing is owed. No `make test`, no mech (per the brief), compiles at -j2.
- Box load: other lanes' heavy chains (load1 9-14) throughout.
