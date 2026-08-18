# R30 — D6 panel on the [M6.1] assertions module design

- **Target**: `docs/design/assertions_design.md` at commit **4f0dafe**
  (lane/asrtdesign; blob d295a6e39e678dd7c6a8ecae464e7277b11cbdac,
  measurements tree c420acb584ccf764edc5a44ae220f3a3bb34066f; 1,437 lines).
  The lane touched no code (`git diff main...HEAD -- src/ lib/ cli/ tests/
  Makefile` empty).
- **Panel**: three read-only critics, 2026-08-18 — r30-engine (opus; engine
  semantics vs the oracle), r30-checks (sonnet; checks/gates/test design),
  r30-measure (sonnet; measurements/provenance/staleness). No critic ran
  `make`; all numbers independently re-derived (own ctypes/libpcre2 10.46
  probes, own emitted-artifact drivers, own harvests), not re-runs of the
  lane's scripts except where re-running WAS the check.
- **Process defect at launch (manager's own)**: the panel launched while a
  manager-relayed Frank question was still being folded into the doc, so the
  target moved mid-review (bcc2069 → 41540bb → 4f0dafe) until a freeze was
  imposed. All findings below were re-verified against 4f0dafe. Lesson
  recorded at the end.

## Verdict in one paragraph

The design's FOUNDATIONS survive adversarial re-derivation unusually well:
the D47.5 scope-blind miscompile is real and is the best-supported claim in
the document (both cell tables reproduced independently by two critics); the
\A/\Z alias claim survived a 1,008-cell differential with zero
disagreements; the \G mechanism claims are structurally verified; all six
committed probes reproduce exactly. But the ENGINE-SPLIT half of the design
has two HIGH holes the implementation waves cannot proceed past — the spine
has no mechanism for assertion context at `startpos > 0` (E1), and the
`(?m)^` routing puts every such pattern permanently in D8's known-slow class,
measured O(n²) (E2) — plus a cluster of mediums (E3–E8) in the same
sections. The doc goes back to the lane for a revision round; the affected
sections get a focused re-check before [M6.2] expands.

## HIGH findings (both REFUTED, both engine-split)

### E1 — the spine is not exhaustive: no mechanism seeds assertion context at `startpos > 0`

§0.2's "exactly three things" omits a fourth requirement: **runtime
start-state selection from a byte outside the search window**. PCRE2 reads
`s[startpos-1]` to seed \b/\B/(?m)^ context (eight measured cells, e.g.
`\bfoo` on "xfoo" at startpos 1 → no match, while the sliced subject
matches). ENG_UNANCH emits both its forward and reverse start states as
compile-time constants (emit_dfa.c:946, :1029), so neither engine half has a
mechanism; the doc's own VM row (§9.3) implements exactly the semantics the
DFA side omits. The reverse machine has the mirror hole: a trailing `\b`
depends on `s[end]`, a byte the reverse walk never consumes — the same
problem class §3.7 uses to exile `(?m)^` to ENG_ATTEMPT, unacknowledged for
`\b` on ENG_UNANCH. Not impossible — a once-per-search dispatch off
`startpos ? fcls[s[startpos-1]] : BOT` mirrors what §3.7 already proposes —
but the exhaustiveness claim is refuted and the design must add the
mechanism, forward and reverse.
**Disposition: FIX-IN-LANE (major)** — §2 gains the fourth row; Wave B
landing conditions gain the eight startpos>0 cells (strongest:
`\bfoo`/"xfoo"/startpos 1 → NO match, where a slice-blind implementation
matches) plus the same cells driven through the §3.1 find-all loop.

### E2 — `(?m)^` routing is a permanent class change into D8's slow shape, measured O(n²)

"Inherits D8's known-slow shape and nothing else changes" is false twice:
plain `^` takes the `start_max=0` fast path (D8's own text), and `(?m)^` can
NEVER take it — its interior start state is live by definition, so
`start_max = n` always (emit_dfa.c:1105-1108). ENG_ATTEMPT has no prefilter
and no skip loops at all, so the cost is n+1 attempts with zero scan
avoidance: measured on the exact engine shape (`^[^b]*b|\n[^b]*b`),
4.0x per doubling — 20,396x slower than the anchored twin at n=32,000 —
and 33x slower than ENG_UNANCH's memchr on the trivial linear case.
A cheap mitigation exists that the doc does not mention: `(?m)^` attempts
can only begin at 0 or after '\n', so a memchr('\n') candidate-start
prefilter in emit_attempt recovers most of the linear-case loss.
**Disposition: FIX-IN-LANE (major)** — strike the sentence; state the O(n²)
plainly; add the memchr('\n') prefilter as a design element or a stated
landing condition; reframe Q3 before any ruling. Whether this unparks
[DD-7] (reverse BOT variant) is a **RULING (Frank)** once the revised
framing exists.

## MEDIUM findings

### E3 — `\z` byte-identity "by construction" rests on the wrong canonicalization reference (REFUTED)

§3.3 canonicalizes `endvar` against the BASE closure but establishes
identity against the EOL view — one sentence apart. For any `$`-bearing
pattern the eol-differing states intern a live `endvar` and the artifact is
NOT byte-identical. Repair is small (canonicalize endvar against the EOL
view / three-way canonicalization). The panel notes in the design's favor:
Wave A's proposed byte-identity check WOULD have caught this — the check is
good, the claim was wrong.
**Disposition: FIX-IN-LANE.**

### E4 — §3.4 × §3.5 never composed; composed at the doc's own worst values the state cap is EXCEEDED (REFUTED)

8,002 states × 4.75 = 38,009 > `PCREC_MAX_DFA_STATES_TABLE` 32,000, on a
pattern (`((a)|ab){4000}c`) inside the doc's own named worst-ratio class;
table budget 2.4% → 11.4%. Second defect: §3.4's corpus silently excludes
every ENG_ATTEMPT pattern (22 `^`-bearing rows have no state count — the
probe reads `facc[]`, which that engine doesn't emit), i.e. the budget was
measured only on the engine `(?m)^`/`\G` do NOT use.
**Disposition: FIX-IN-LANE** — state the composed worst case, disclose the
exclusion, make compose-both-caps a Wave B landing condition.

### E5 — the skip-hazard is misattributed and Wave B's sabotage row cannot fire (REFUTED)

The \b/\B accept is CONSTANT across any skipped run (state identity pins
prev-wordness; §3.4's refinement pins next-wordness) — the hazard is real
only for `(?m)$`/`\Z`-family accepts. Consequence: Wave B's
sabotage-disabling-the-intersection row is a NO-OP on every pattern Wave B
lands — a check with no failing direction, the project's recorded
check-design failure mode, in the wave the doc calls most dangerous. Also:
the cure names 1 of 5 scan-avoidance mechanisms; the post-skip compensating
accept (emit_dfa.c:1003-1004) reads a scalar that must become class-indexed;
and memchr CANNOT be intersected — `\bx*`'s start state accepts at word
boundaries, so the `start_acc` prefilter gate must widen to "accepts on any
class" or go unsound (concrete cell: `\bx*` on "a x").
**Disposition: FIX-IN-LANE** — move the cure + sabotage to Wave C or give
Wave B a `(?m)$`-shaped stand-in; enumerate all five mechanisms with their
individual fates.

### E6 — the zero-cost accept-table measurement is scoped to ENG_UNANCH and has no end-of-subject column (REFUTED as scoped)

ENG_ATTEMPT bakes accept into the goto body (`last = pos;`) — no `facc[]`
exists there, so the A/B measurement doesn't cover the engine `(?m)^`/`\G`
use, and that engine's EOL-variant branch carries no `__builtin_expect`
guard either. At `pos == n` there is no byte to index by: the lane's own
probe papers over it with class 0 (probe_acc_by_class.sh:33). The clean
answer (at pos==n use the view's SCALAR accept, never index) exists but no
section states the composition rule between the {base,eolvar,endvar} view
axis and the class axis.
**Disposition: FIX-IN-LANE** — state both exclusions; write the composition
rule.

### E7 — \K "structurally impossible" is overstated; the conclusion (VM-only) stands (WEAKENED)

Leftmost-first is a total order, so PCRE2's \K answer is unique (six
measured cells, including the doc's own ambiguous-boundary shape). The real
obstruction: the \K position is not a function of the subset state — but
tagged DFAs recover exactly such positions, so the honest wording is
"pcrec's DFA is not a tagged DFA and this design does not propose making it
one", not "structurally cannot". As written it is the kind of sentence a
later lane cites to close a door that is not closed.
**Disposition: FIX-IN-LANE (wording + record the tagged-DFA door).**

### E8 — §9.3's match-here paragraph is factually wrong; the Wave D test targets a nonexistent difference; \K breaks the match-here filter (premise REFUTED)

The DFA artifact's `rx_match` IS `rx_search` with `startpos = ctx->pos` plus
a start-equality filter (quoted from an emitted artifact) — "there is no
startpos" is false, and the two engines' match-here entries have different
shapes (VM calls `rx_match_impl` directly). For fully-\G patterns the two
entries agree exactly, so Wave D's owed differential has nothing to find —
rewrite or drop. The live hazard: under \K, `caps[0][0]` is the post-\K
start, so the filter rejects genuine anchored matches (`a\Kb` at pos 0 →
-1 where PCRE2 matches (1,2)) and the return value is the post-\K length —
which a D38 callout uses as its advance. §6.3 needs a third rule for the
match-here entry; Wave E's tests must cover it.
**Disposition: FIX-IN-LANE.**

### M2 — the prototype has a second, unidentified fidelity defect under bounded-repeat-over-wide-alphabet shapes (WEAKENED)

`\w{3,16}`'s prototype baseline undercounts 4.25x vs real pcrec — a
direction the stated "no pruning" gap cannot produce — and that same pattern
supplies one of the two ">2.00x" ratio outliers (18/4 = 4.50x; against
pcrec's real baseline it would be ≈1.06x). The 4.75x headline max is on an
uncontested pattern and stands.
**Disposition: FIX-IN-LANE** — re-derive `\w{3,16}`'s baseline (pcrec CAN
compile `\w{3,16}` today), fix or footnote the ">2x: 2 patterns" line, and
caveat §3.5's "one known fidelity gap" framing.

### M6 — the .rxt-corpus harvest recurred a NAMED project defect (locale-collation `sort -u`); population 609 is wrong, 1030 is right (provenance MEDIUM-HIGH; conclusion LOW)

The "574 of 609" population came from an uncommitted harvest whose
`sort -u` under en_US.UTF-8 merges punctuation-differing patterns — the
exact defect eng_brep's R24 M-F1 entry already named and fixed with
`LC_ALL=C`. True population 1030; the critic re-ran the probe on the
corrected corpus and got IDENTICAL headline numbers (48,012 max
states×ncls, same pattern) — conclusion strengthened, provenance defect
real.
**Disposition: FIX-IN-LANE** — commit the harvest script with `LC_ALL=C`;
report the corrected 962/1030 row.

### M7 — one provenance header was hand-written to imitate archive.sh output (provenance MEDIUM-HIGH; data correct)

`out/dollar_multiline_rerun.txt` was never produced by archive.sh: git
history shows its original two-line hand header rewritten by hand into the
archiver's format (stale RUN commit/date kept, no working-tree line, prose
the script cannot emit), making §0.3's "every file in out/" claim false for
1 of 6 files. The NUMBERS are correct (independently reproduced from
scratch). A hand-typed block imitating a mechanical archiver is a sharper
instance of "a control sharing a source with what it controls" than
anything the archiver guards against — a reader cannot tell it from the
real five without git archaeology.
**Disposition: FIX-IN-LANE** — genuinely re-run the probe through
archive.sh (numbers are stable; costs nothing). **Process lesson recorded
below.**

### M5 — Q1's D18 exemption argument is unsound (argument REFUTED; question stays open)

"Semantic namespace, not an optimisation axis" is contradicted by D18's own
worked example: D23 ran the earn-its-axis test on case-folding — a semantic
dimension — and it FAILED into the parser. D58's encoding axis was justified
by a committed second customer (M5 is the next milestone), which newline
lacks. The honest test is the one D23 ran: try to fold newline (hardwire
LF) and see which way it fails. Accepting the exemption as stated would
exempt every future semantically-flavored customerless axis.
**Disposition: FIX-IN-LANE (reframe Q1's argument); then RULING (Frank).**

### M3 — the stale eng_brep 0/720 + 180/720 figures are cited as current fact in four fixable places

plan.md [M6.2], docs/design/CLAUDE.md:414, src/opt/CLAUDE.md:154,
src/core/CLAUDE.md:131 (eng_brep_design.md itself is Q6/manager territory;
the R24 review record is historical, untouched). Today's numbers: 21/384,
33/384 full; 0/168, 12/168 on the greedy population — qualitative claim
survives on both oracles.
**Disposition: MANAGER-AT-MERGE** — all four cites fixed in the same pass;
eng_brep annotation + any D47.5 addendum (lane's Q7) decided then.

## LOW / minor findings

- **C3**: Wave A's byte-identity check and Wave E's \K structural check are
  the only proposed checks with no sabotage row. **FIX-IN-LANE** (stated
  landing conditions).
- **C2 (process)**: the original "node-kind fails safe / flag fails unsafe"
  prose oversold a property the codebase already had (the `first_of`
  catch-all declines unknown kinds either way); superseded mid-review by the
  measured -Wswitch version. Lesson: measure the differentiator, don't
  assert it.
- **C7**: the `--encoding=utf8` gating precedent transfers by analogy, not
  verbatim (whole-pattern single gate vs per-construct registry dispatch);
  the doc's actual mechanism ("registry row gains a built predicate") is
  fine — say the granularity difference. **FIX-IN-LANE (one sentence).**
- **M8**: §8.3's -Wswitch experiment promises "command and output", delivers
  output only, and is unverifiable by any read-only critic. **FIX-IN-LANE**
  — commit it as a real instrument (probe adds the enumerator, runs
  `gcc -fsyntax-only`, counts, reverts) or soften §0.3's promise.
- **E8-adjacent m1/m2**: §0.2's "exactly three things" vs §3.1's own
  "\b is both" row; §9.3's \b VM spelling reads out of bounds at both edges
  as written (K27 class — carry the guards in the design spelling).
  **FIX-IN-LANE.**
- **S4 correction**: §12 item 5's refutation experiment must sweep
  `startpos > 0` or it cannot fire. **FIX-IN-LANE.**

## What survived attack (evidence, not absence of attack)

- **D47.5 scope-blind gate** (C1, M-1f, both cell tables): confirmed by two
  critics on independent instruments; "the single best-supported claim in
  the document". The 5-cell table: 2 of 5 shapes miscompile, both
  lost-match direction; the one shape D47.5's obligation names is the one
  the shipped code gets right.
- **\A/\Z exact-alias claim** (S1): 1,008-cell differential (16 pattern
  pairs × 20 subjects × every startpos), zero disagreements, including
  every adversarial trailing-newline shape tried.
- **\G semantics + mechanism** (S2, S3, S4): `pos == startpos` measured;
  `start_max = startpos` is a one-token third string at the verified site;
  three start states confirmed minimal.
- **\Z python-oracle divergence** (C4, 1e): the 7-row table reproduces
  verbatim; \Z expectations must ride the libpcre2 differential.
- **mods blast radius** (C8, and the lane's own grep): possessify.c is the
  sole post-parse reader; compile.c's two sites are seeds into the parse.
- **All six committed probes** (M-1a..1f) reproduce exactly; the
  throughput probe reproduced on a checked-quiet box.
- **mrl.c:18-24 house rule** (the lane's own late find, verified by
  r30-checks static grep 15/6-files и by direct read): the exhaustive-
  switch-no-default convention exists, is named, and altcls.c cites it
  (verified by r30-checks' static 15-warnings/6-files grep and by direct
  read of both files).
- **eng_brep staleness** (M3): the doc's today-numbers reproduce exactly;
  the 720-population numbers are not reproducible under any interpretation.

## Open questions to Frank (after the revision round)

- **Q1** (newline axis) — with M5's reframe: the fold-first test, not the
  semantic-namespace exemption.
- **Q8** (flag vs node-kind for parse-resolved multiline `$`) — with the
  mrl.c house-rule footing and the lane's either-way controls ask; Frank's
  stated lean is the flag.
- **Q3-revised** ((?m)^ performance) — only on E2's corrected framing,
  including the memchr('\n') prefilter option and the DD-7 unpark question.
- Lane's Q6/Q7 (eng_brep annotation; D47.5 addendum) — manager-at-merge.

## Process lessons (for the journal and learnings at close)

1. **Panel targets are frozen commits.** The manager relayed a design input
   to the author after launching the panel; the doc moved under two
   critics. Freeze before launch; batch inputs until after compile.
2. **Provenance imitation is worse than absent provenance** (M7): a
   hand-written header in a mechanical archiver's format defeats the
   reader's ability to distinguish stamped from asserted — the
   sharpest-yet instance of the named "control sharing a source with what
   it controls" class. Archivers must be the only writers of their output
   directory; a hand edit there is a red line, not a formatting choice.
3. **The locale `sort -u` defect recurred after being named and fixed
   once** (M6) — a named defect is not a fixed defect; the fix must travel
   as committed tooling (the harvest script), not as knowledge.
4. **A sabotage row that cannot fire on the wave's own population is not a
   landing condition** (E5) — check the sabotage against the wave's
   pattern class, not just against the mechanism.
