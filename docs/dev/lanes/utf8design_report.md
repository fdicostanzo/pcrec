# [M5.0] DESIGN-GATE lane — delivery report

**Lane:** `utf8design` (opus), worktree
`/Users/fdicostanzo/pcrec/worktrees/utf8design`, branch `lane/utf8design`.
**Delivered:** 2026-09-04. **Not merged, not pushed.**
`docs/dev/plan.md` untouched, as briefed.

## Deliverables

| path | state |
|---|---|
| `docs/design/utf8_design.md` | 1,496 lines. PROPOSED; unpaneled. |
| `docs/design/utf8_measurements/probes/` | 7 probes + oracle helper + remote bundler + archiver |
| `docs/design/utf8_measurements/out/` | 8 archived transcripts, all written by `archive.sh` |
| `docs/design/utf8_measurements/CLAUDE.md`, `out/CLAUDE.md` | written |
| `REFERENCES.md` | `[Cox07]`, `[Ragel]`, `[UCD]` added, cited from §2.3/§3.3/§4.4 |
| `docs/design/CLAUDE.md` | two entries added |

Nothing under `src/`, `tests/`, or `docs/spec/`. One WIP commit plus this
report's own.

## Section-by-section status against the charter

| charter item | section | status |
|---|---|---|
| (i) the lowering | §2 | **complete.** Construction cited, pipeline position fixed, all four byte-tier consumers answered, invalid-UTF ruled with a measurement, parser boundary drawn. |
| (ii) `\p{...}` | §3 | **complete.** 114 spellings measured; families staged; table sizing swept from the oracle. **The data-source question is an ASK, not an answer.** |
| (iii) DD-1 | §4 | **complete, and smaller than the charter expected** — simple folding only. |
| (iv) the seam's second instance | §5 | **complete.** All four residual entries instantiated; `\b` answered with a deliberate no-new-entry; the cross-note resolved. |
| (v) engine/selection | §6 | **complete.** Sizing measured, DFA-eligibility argued, prefilter answered with a new opportunity recorded-not-built. |
| (vi) the oracle plan | §7 | **complete.** 23 measured divergence rows against a charter minimum of 10; `.rxt` needs flagged, not written. |
| (vii) validation | §8 | **complete.** Identity gate, 8 sabotage rows, ~420-cell population, the `maxw` compatibility question answered as "the gate is the check". |
| (viii) module/staging | §9 | **complete.** Five stages, each with its own acceptance. |

## The five results that matter most

1. **The `[M5.0]` row's own CROSS-NOTE prescribes a cure that would break
   every lookbehind under UTF-8.** MEASURED: PCRE2 measures lookbehind length
   in **characters** (`(?<=[a\x{3b1}])x`, one branch, one character, one-or-two
   bytes, compiles with `MAXLOOKBEHIND` = 1). Setting `pcrec_maxw`'s `A_CLASS`
   arm to the maximum code-unit length makes `la_widths`' `minw == maxw` test
   read `1 != 4` for every class and refuses `(?<=a)x`. Resolution in §5.6:
   two quantities, two consumers.
2. **`\p{...}` does not require `PCRE2_UTF`**, so `unicode-props` is not
   encoding-gated and can land before the utf8 backend. Corollary returned to
   `[DD-11]`: its chartered second predicate is keyed on **UCP**, not UTF.
3. **10.46 does simple (1:1) folding only** — 0 of 11 one-to-many cells. This
   deletes `[FORM-CHAR]`'s object (5) `utf8-full-fold`. But the fold is a
   **closure** that **reaches outside the written range**, so it must run on
   code points before lowering.
4. **There is no state blowup.** `\p{L}` is a 283-state minimised DFA,
   `\p{L}*` is 282, UTF-8 `.*` is 9 — against 10,000/32,000 caps.
5. **`enc_byte.c`'s predicted witness for the length-returning backref
   residual is refuted; the decision is vindicated by a different cell.**
   `(?i)^(ss)\1$` on `"ss\xdf"` is no match under UTF; `^(k)\1$` on
   `k`+U+212A matches `(0,4)` — a 1:1 fold that is not length-preserving.

## The ASKs (§14) — six, none a ruling contradiction

1. **Invalid-UTF semantics.** Proposal: an ill-formed sequence matches
   nothing; no validation pass, no error return. Diverges from `PCRE2_UTF`'s
   default, which errors for the whole subject. Accept?
2. **Vendor UCD data files** at a pinned version (16.0.0) into
   `third_party/`. Both alternatives are disqualified and the disqualification
   is measured. This would be the first non-PCRE2 third-party data here.
3. **Make "simple folding only" a standing check**, or accept it as a
   re-measurement event on version bump?
4. **Is a UCP axis owed?** 8 of 28 divergence rows. Design recommends no.
5. **`ENG_ATTEMPT`'s start loop** tries mid-character starts under UTF-8 —
   harmless, wasted. Fixing it means routing a shared emitter loop through a
   residual entry, which S68 forbids. Leave (recommended) or charter?
6. **The `.rxt` third oracle value** (python-verifiable through `str` only).
   Route to `[DD-13b]` or charter a small amendment?

## Escalations and corrections owed at merge

- **`[DD-12]` is stale in two places.** It assigns the CharSet widening to
  MOD-0.6; D33 §7's own 2026-08-12 amendment reassigns it to "the first wide
  producer", which is this milestone. And its item (3) mischaracterises
  `PCRE2_MATCH_INVALID_UTF`. Both should be corrected on the row.
- **`src/gen/enc/enc_byte.c`'s backref comment** names a witness that is
  measured NOT to behave as it says. Its design conclusion is right; the
  example should be replaced with `^(k)\1$` (§12 P-6 makes this a check).
- **A note, not an escalation:** `--features unicode-props` on `\p{L}` still
  reports `\p requires module 'unicode-props'` rather than an
  enabled-but-unbuilt refusal naming the construct (`out/premises.txt` §3).
  Whether that matches the D38-consistent wording the `assertions` module
  established is a question this lane did not chase — it is D26 tier 3
  (wording) and it changes nothing in this design. Flagged so the
  implementation wave decides deliberately.

## Instrument defects (full detail in `out/CLAUDE.md`)

Four found by running this lane's own probes, plus one non-defect recorded at
the same length because the alarm was rung and did not sound (the
python-version axis does not move any of the 28 divergence rows — verified by
re-running the whole table under both pythons and diffing).

The one worth the manager's attention: **`-o /dev/null` was reproduced
verbatim** after `subroutines_measurements/CLAUDE.md` had already recorded it.
That is the second time this house has recorded that shape (R30 M6 was the
first). The durable fix is a shared probe fixture, not another entry.

## Method note: the remote oracle

This is the first lane here whose reference oracle lives on another machine.
Every libpcre2 claim was measured against **10.46 on the old box**, via a
stdin-delivered bundle that embeds the borrowed binding chain verbatim —
nothing was written on that box. `probes/bundle.py`'s docstring and
`utf8_measurements/CLAUDE.md` carry the mechanism and the argument for it.
**A local run measures a third library**: `find_library("pcre2-8")` on this
Mac resolves to miniconda's 10.37, not Homebrew's 10.48.

## DISCLOSURE — files injected at spawn

Beyond the brief itself, the following were injected into this lane's context
by the harness rather than read by choice:

1. **`/Users/fdicostanzo/pcrec/CLAUDE.md`** (session-root project
   instructions) — and separately the worktree's own richer `CLAUDE.md`,
   which carries the "Situation index" table the session-root copy lacks.
2. **`/Users/fdicostanzo/pcrec/worktrees/utf8design/docs/CLAUDE.md`** and
   **`docs/design/CLAUDE.md`** — auto-injected as a system reminder partway
   through the lane, not opened by the lane.
3. **A memory-index reminder** naming user/project memories.
4. The environment block (box facts, scratchpad path) and the available-skills
   listing.

No denied file was read. The lane read `src/`, `docs/dev/plan.md`,
`docs/dev/plan_completed.md`, `docs/dev/decisions.md`, `docs/spec/
match_api.md`, `APPROACH.md`, `REFERENCES.md` and the sibling design lanes'
probes deliberately, all within the mandated repository.

## Sub-lane

One measurement sub-lane (sonnet) built `probes/probe_sizing.py` — the
byte-automaton construction and its state counts — scoped to that one file
plus scratch, briefed with the scope mandate, and forbidden `make`/git writes.
It found and fixed a real construction bug via its own self-check (5,460
mismatches → 0) before any number left the probe. Its Unicode-version caveat
(python 3.11 = 14.0.0, PCRE2 10.46 = 16.0.0) is carried into the design as
§2.4 caveat 2 and quantified against §3.3's oracle-swept census.

## What was NOT done

- No `make test` (light testing only, per the brief): the tree was built
  (`make -j4 CC=gcc-16`, green) and probes compiled/ran; the suite was not.
- No `docs/spec/` edit. §7.4 and ASK 6 flag what `rxt_format.md` will need.
- No product code, no `tests/` corpus. The population is sized (§8.3), not
  written.
- **§12 P-5 is the measurement this design does not make**: §2.4 sizes
  classes in isolation, not the products a real pattern builds. That is the
  most likely place its comfort is misplaced, and it says so.
