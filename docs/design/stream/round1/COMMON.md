# COMMON brief: end-state architecture, "one instruction stream" (round 1, approach lanes)

## The owner's framing (Frank, 2026-11-01, verbatim)
"Right now we consider an rx to be either a dfa or a vm. It is recognized that this is less true all as we progress because many rx have some of both. Vm has dfa match and dfa has what is really a vm scan edge. Both have kit sections. You did the vm emit refactor recently. The idea is this: all regex artifacts are a continuous set of instructions. Some of those are vm. Some are dfa components. Rather than think of the artifact rigidly as this section is dfa and this is vm, it's instead simply what was produced at that point in the rx. Then the 'vm' emitted instructions include codes for vm as now, dfa code, and kit codes."
And on the method: "I'd like to go high level first in our thinking and have an end state then we can prove it out with smaller changes ... Once we have a high level approach that has benefit (tricky) then we do some proofs ... Trickiest is overcoming the 'bird in the hand' perspective."

## Scope mandate (binding)
- You touch ONLY /home/pcrec/projects/pcrec, READ-ONLY. pcrec-bench is read-only too, and only if you need it.
- You write ONLY under /var/tmp/pcrec-pcrec/scratch/stream/<your dir>/. Never /tmp, never either repo, nowhere else on the machine.
- No make, no builds, no suites, no box queue. You may run the existing build/pcrec on single patterns (`build/pcrec -p rx -o OUT --pattern 'X'`, outputs under your dir), and `--emit-ir` / `--emit-facts` likewise. Use `timeout 60` on each run.
- Never read PCRE2 source (D181; ask the manager for a pcre2-reader note instead).
- Do not read other approach lanes' directories (blinding).

## What pcrec is
Read only what you need:
- An ahead-of-time PCRE-to-C compiler: APPROACH.md (the approved architecture: two engines, modules, optimization pass), docs/spec/pattern_language.md (the semantics: PCRE2 is the source of truth, backtracking, leftmost-first preference), docs/spec/match_api.md (what a caller sees).
- The VM refactor: decisions D182, "the record is the source"; VM emission builds a record of instructions and renders C from it; docs/dev/guide/coding.md §2.7.
- The landmark walk: D161 and its addendum 17 ("the reverse DFA seeded at the landmark is the SCAFFOLDING; SCAN EDGES are the optimization inside it").
- The kit: memfn/CLAUDE.md, D146/D147/D157 (pcrec hands the kit FACTS, never methods).
- Pricing placement is under study (docs/design/pricing_rulepilot.md on lane/rulepilot, via `git show`).

## The worked patterns: apply your end state to EVERY one
Show the instruction stream it produces (pseudo-instructions, not C), where each segment kind sits, and what each seam hands across.
1. `abc`  (pure literal)
2. `[a-z]+@x`  (landmark walk: kit find, reverse DFA with a kit scan edge, forward verify)
3. `(\w+)@(\w+)\.com`  (captures with backtracking)
4. `(a|ab)(c|bcd)(d*)`  (leftmost-first preference that a DFA's longest-match would get wrong)
5. `(\w+)\s+\1`  (backreference)
6. `foo(?=bar)|(?<!x)baz`  (lookaround)
7. `(?:cat|dog|bird|fish|...30 words...)s?`  (heavy alternation)
8. `(a+)+b`  (nested quantifier, catastrophic for naive backtracking)
9. `x(?C1)y\d+`  (a callout mid-pattern)
10. `\p{Greek}+\s\d{3}` under UTF-8

## What to deliver: <your dir>/approach.md (create it; write it INCREMENTALLY)
1. **The end state, high level.** The instruction kinds, the segment model, who decides segmentation and how, and the seam contract (position, captures, proof, backtracking re-entry).
2. **The soundness rule:** when may a stretch be committed to a deterministic (DFA) segment without changing a backtracking answer? And what happens where it may not (re-entry, alternatives, state sets)?
3. **The worked patterns,** all 10.
4. **BENEFIT CASE.** For each claimed benefit:
   - what it is: speed, reach, simplicity (special cases DELETED: name them), new capability;
   - how it would be measured or demonstrated;
   - which patterns it reaches.
   Be honest: "tidier" alone is not a benefit; say which claims are weak.
5. **BIRD-IN-THE-HAND DISCIPLINE.** Compare the two FULLY BUILT end states, yours against today's two-engine design grown as far as it can go, head to head. Migration cost goes in a SEPARATE section and is never subtracted from end-state merit. "Today's code works" is not an argument. Name what today's design can NEVER do that yours can, and the reverse.
6. **Holes you already see** in your own design, ranked.
7. **Smallest proofs:** 2-3 small changes that would demonstrate the approach. Prefer byte-identical re-expressions first, then one that shows a benefit.
Length: aim for 6-10 pages. Prose and tables; pseudo-code only where it clarifies.
Final reply: at most 150 words, with the file path and your top 3 claims.

## OWNER'S BENEFIT CRITERIA (Frank, 2026-11-01, after round 1). These SUPERSEDE speed as the headline.
"I don't anticipate large speed wins (indeed there might be some trouble there because cutting the front and back apart lead to some blindness) or similar benefits. I see the advantage in simplicity but not only for its own sake. 1. pcrec main can be more focused. In general we should create this as handoff architecture. ... The truth is that projects get lost when the unit of focus is too large. The unit of focus for pcrec approaches the whole project. Making a change means scanning too much. New code is generated instead of updating existing. It's hard to see the bigger picture. Test errors can come from anywhere. Splitting off memfn was work but I think worth it. 2. flexibility: new backend? New frontend? 3. division of labor. That said, even if we determine that this approach is correct, I don't think we could have gotten here any other way. We needed to know what the seam was and you can only do that by building it first and then dividing."
So the end state is judged on:
(F1) FOCUS: does it shrink the unit of focus (a contract per seam, tests per part, a change touching one part)?
(F2) FLEXIBILITY: a new backend, or a new front end?
(F3) DIVISION OF LABOUR: can parts be owned and validated separately?
(F4) NO BLINDNESS: a handoff must carry facts both ways. P1's [LANDWALK-PRES] is the worked example: a local decision blind to a cheaper check across the seam.
Speed must not REGRESS; it is not the case for the design.
