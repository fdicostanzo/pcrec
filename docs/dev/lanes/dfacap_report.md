# dfacap — captures without the VM: research report

Lane `dfacap`, opus, 2026-11-12. Research only, no build. Branch
`lane/dfacap`. Deliverable: `docs/design/dfa_captures_research.md` (the memo),
with census instruments in `docs/design/dfa_captures/`.

## STATE AT HANDOFF

- DONE: the memo (Goals, standing questions, §0-§7), the census (5,769
  unique corpus + bench patterns, 7,326 compiles, about 1,300 over the
  brief's ~6,000 because of the second `--no-captures` pass; one niced
  process, about 1 minute), the instruments and outputs committed, 4 new
  REFERENCES.md entries ([BM17], [FC04], [GoIssue46123], [PCREdev2020]),
  cited-by lines updated on 18 existing keys, and `docs/design/CLAUDE.md`
  indexed.
- Rulings file `docs/dev/lanes/dfacap_rulings.md`: empty at every read, so
  no ruling was applied.
- No `src/` or `memfn/` edit. No owed runs. No pcre2-reader was used (no
  PCRE2-source fact was needed; PCRE2 capture-update behaviour is cited from
  the pcre-dev list and left to a future differential).
- Limits of the sourcing: the web-fetch subagents ended without delivering
  their reports, so the new literature facts come from WebSearch summaries
  and are marked `(unverified: ...)` in REFERENCES.md. The survey's earlier
  first-hand readings ([BT22], [Tro19], re2c) are reused as they stand.

## FINDINGS

**Settled before this lane** (memo §1): the survey
`docs/dev/optloop/captures_via_dfa_survey.md` already covers who captures
with a DFA and how. pcrec already ships the RE2/rust two-pass hybrid. The
one-pass reach is 31% of capture-bearing patterns (M-A). The VM pass costs
about 0% of time on sparse search and a median 33% in the match regime on
tiny, confounded subjects (M-B).

**New 1, semantics (INFERRED, memo §2.2):** the survey's blocker ("TDFA is
proved for leftmost-greedy and POSIX, PCRE is neither") is smaller than it
read. Leftmost-greedy TDFA keeps configurations in priority order, and that
is D3's construction in `src/ir/dfa.c`. A lazy quantifier is only edge order
inside it, and PCRE's empty-iteration rule is already in the closure (K18).
The open part is capture UPDATE under repetition (last iteration, PCRE2's
restore-on-empty versus Perl's clear, publish-at-close). Those are
tag-placement rules, testable exactly against the VM.

**New 2, census by cause (memo §3.1, compiler stamps):**

- VM population: 2,353 of 5,769 patterns.
- **Captures only: 815 (bench 22)**, 35% of the VM population on both
  corpus and bench. 709 of them already run the hybrid; 106 have no
  prefilter at all (nullable).
- Captures + a capture-free lookaround as the only other cause: 43
  (bench 1).
- Captures INSIDE a lookaround: 88, which stay on the VM.
- Kept by other causes: backreferences 369, calls 60, atomic 51, callouts 24,
  `\K` 14.
- [COND-FAMILY]'s own class (capture-free, lookaround only): 394 (bench 12).
- **The two steps free nearly disjoint populations**: they add up rather than
  compound.

**New 3, one construction (memo §4.4):** one-pass, [CAPS-KNOWN]
tag-determinism and partial evaluation, and full TDFA are admission levels of
one tagged priority construction: copy-free versus registers with copies. Do
not build a separate one-pass engine.

**Limits (memo §4):**

- States are at least those of the DFA, with an exponential worst case; caps
  and [SEL-1] fallback apply.
- Registers are bounded by threads x tags.
- Repeated captures (296 of 815) and counted repeats (251) are the expensive
  shapes.
- Captures inside lookarounds, backreferences, calls, callouts and
  atomic/possessive stay on the VM. That is about 940 of the 2,353 VM rows,
  the VM's floor under both steps.
- `\K` becomes a start tag, which is a bonus: 88 more rows.

**Effort and costs (memo §5.4):**

- Stage 0: a compile-only counting probe. One lane, no `src/` edit.
- Stage 1: copy-free, anchored, inside the hybrid window, replacing
  `rx_match_anchored`. One large opus lane, plus a panel, plus a D27 tag
  corpus; an abi event. Frees about 60% of the 815 (INFERRED).
- Stage 2: registers with copies. A second large lane, where the correctness
  risk is.
- Stage 3: with the checker product, 43 rows.
- Stage 4: START tags, which drop the reverse pass.
- The oracle burden is light: the VM is already an independent, PC-3-checked
  capture engine, and test-axes' answer-identity sweep covers a deny/force
  axis.

**Recommendation (memo §6):**

- Keep [ENG-TDFA] unscheduled.
- The checker product goes first. It is ruled, and its rows make the VM do
  real work.
- Ask that the product's state identity leave room for a per-thread tag map.
- Open Stage 0 only on [CAPTURES-DFA-MB]'s trigger (a match-dense bench cell
  where a hybrid's VM share is at least 10% of time on Linux) or Frank's word.

The proposed plan-row and D3-addendum edits for the manager to file are in
memo §7.
