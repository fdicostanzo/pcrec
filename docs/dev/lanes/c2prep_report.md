# lane `c2prep` — cycle-2 preparation: three compile-side deliverables

**2026-09-22, opus, branch `lane/c2prep` from `b3086b46`.** Docs and
throwaway census instruments only: **nothing under `src/`, `lib/` or `cli/`
changed**, no mechanism was built, and **no clock was read anywhere** (darwin;
D119's own mechanics). Every number below is a COUNT, or a timing quoted from
the I-85 Linux profile transcripts already committed under
`docs/dev/optloop/runs/`.

Deliverables: `docs/dev/optloop/firstset_design.md`,
`docs/dev/optloop/reqpos_census.md`, `docs/dev/optloop/onepass_census.md`,
with their instruments and data under `docs/dev/optloop/c2/`.

---

## Headlines

**1. `[OPT-FIRSTSET]`'s mechanism, as ratified, is unsound — and its own
proposed identity check passes it.** Narrowing `rx_can_begin_match` to the
AST-level first-byte set makes `\b(?:true|false|null)\b` report a SPURIOUS
match at offset 1 on `"atrue xnull "`, where the shipped artifact answers
`matches=0` (verified by compiling and running it, not by reading tables). The
DFA's start state is not "nothing has happened": for a `\b`-leading pattern it
encodes the preceding byte's word class, so the bytes leaving it live include
every word byte — not because a match can start on them, but because
consuming one moves the machine to a different CONTEXT state. M3 offers the
subset property as *"a free compile-time assertion and the natural identity
check"*, and `{t,f,n} ⊂ word-63`, so the proposed guard is satisfied by the
unsound narrowing. **The repair is one line reusing `rx_forward_seed_state`, a
table the artifact already emits; it restores the answer and changes no
count.** The error direction is spurious matches, which no subset argument can
catch.

**2. The cost model the note was chartered to supply declines nothing.**
`skipped + steps == n` exactly on every configuration measured, so cost per
byte is `(L·b + w·a + c)/(L+w)` with `L = (1−d)/d` — an identity, not a fit,
predicting the measured skipped fraction to within 0.03% across four
configurations — and its derivative in `L` is negative for every admissible
parameter. The single measurement that contradicts it is `json-constant`'s
×1.10, which **no linear accounting over that artifact's own counts
reproduces** (predicted 1.4408 ns/byte, measured 3.4064). So the D77 gate
became "re-run M3.c on `json-constant` first", not "build the decline rule".

**3. `[OPT-REQPOS]` tier 2 does not clear D77.** The bounded-`dmax` skip loop
the row is really about has a population of **two** among cycle 1's 34 losing
cells and 6.0% of the corpus — the smallest live tier on every population.
**Tier 2b, the pair / word compare, is the tier with a population**: 27.3% of
the bench and 18.6% of the corpus carry a necessary literal run of 2+ bytes,
and five `capability` patterns have the single byte PRESENT in the throughput
subject and the RUN ABSENT, four of them losing rows carrying 1.4617 of the
matrix's 10.284 weighted score.

**4. The one-pass DFA survives its kill gate by a factor of three.**
Capture-bearing reach is **31.46%** on the corpus (369 of 1,173) and **29.41%**
on the 17 capture-forced hybrid rows, against `captures_via_dfa_survey.md`
§3.6's ~10% threshold. The RE2/Go caps cost 0.26 points.

---

## Findings the briefs did not anticipate

**F1 — PCRE2's rightmost-byte rule is leaving three whole-call answers on the
table.** `[OPT-REQBYTE]` picks the rightmost necessary byte, deliberately,
copying `LASTCODEUNIT`. Reporting the whole necessary SET and joining it
against the subject census shows 14 of the 36 `capability` patterns with a
necessary byte have a RARER one, and on three the rarer byte is ABSENT while
the picked byte is PRESENT:

| pattern | picked | hits | rarest necessary | hits |
|---|---|---|---|---|
| `nested-comment-rec` (losing row, rank 9) | `/` | 30,000 | `*` | 0 |
| `wild-validator-email-owasp` | `.` | 14,826 | `@` | 0 |
| `wild-waf-crs-942500-comment-obfuscation` | `/` | 30,000 | `*` | 0 |

On those three batch 1's shipped pre-check cannot fire and a
frequency-informed pick answers the entire find-all call in one pass. It is
the cheapest item in the delivery: no new emitted mechanism, no new stamp —
`reqbyte.c` already carries the whole set internally and chooses one member
at the end — and the fact that decides it is the `freq` value the other
deliverable specifies.

**F2 — the findings-file work is further along than either brief assumed.**
The brief scoped me to "the VALUE and the consumer interface, not the
format". The format **already shipped**: `freq` is
`src/parse/rxt_schema.def:146` with a whole `DATA` scope
(`question`/`reader`/`analyzer`/`row`/`provenance`), a `--list-schema` row and
a spec section. Its body requires a **`reader`** line naming *"the selection
point that consumes it"* — a field that has never had a value to hold, and
`[OPT-FIRSTSET]` is the first mechanism that can fill it. The genuinely
unfinished half is `config`'s `analysis <list>` name resolution, which
`docs/spec/rxt_format.md` already records as *"not resolved in this build"* —
and that is exactly where D83 addendum item (4)'s `-I`-library-path
consideration lands.

**F3 — the survey's expected UTF-8 narrowing does not reach the population it
is about.** `[RAonepass]`'s overlapping-encoding caveat is real and visible:
whole-corpus one-pass reach falls 54.39% → 48.88%, 211 patterns. But
capture-bearing reach moves **0.06 points**. The reason is measured rather
than argued: **46.3% of the capture-bearing population is excluded by a node
KIND** (lookaround, backreference, subroutine call) before any first-set
question is asked, and a node kind does not change with the encoding.

**F4 — pcrec's own factoring pass changes what "one-pass" means.** `(xy|xz)`,
which the survey names from RE2's front end as NOT one-pass, is factored to
`x(?:y|z)` by `pcrec_altcls` before any analysis sees it and IS one-pass on
pcrec's tree. Worth **+3.16 points** of capture-bearing reach (28.30% →
31.46%), measured by giving the probe a `-no-factor` switch so both numbers
come off one instrument. Both clear the threshold, so the ranking does not
turn on it — but pcrec's reach is not comparable byte for byte with a
published figure derived from raw pattern text.

**F5 — two build-time findings about census instruments, both recorded in the
probe sources rather than only here.**

* *The first draft recursed down the `A_CAT` spine and died on the shipped
  corpus* — which is `src/opt/reqbyte.c`'s own stated reason for walking it
  iteratively, and this project's recorded segfault-on-a-20,000-byte-literal
  lesson met from the outside. Rewritten; the eleven smoke cases are identical
  before and after, which is what makes the rewrite checkable.
* *The first draft's pipeline prefix was parse + lower, and the cross-check
  against the shipped stamp caught it.* On `/user|/users` batch 1 stamps `r`
  and the probe read `s`, because `pcrec_altcls` factors that alternation
  first. **An analysis's answer is a property of the tree at its own call
  site, so a census that reconstructs the pipeline must reconstruct every
  REWRITING pass above that site** — and the only reason this was found is
  that the census was built with a cross-check against a shipped fact rather
  than against its own reasoning. Cross-check now 63/63.

---

## Validation

**COMPLETE for what this lane delivers, which is counts and documents.**
Nothing here needs a suite: no `src/`, `lib/`, `cli/` or `tests/` file moved,
so no gate, pin, manifest or sabotage anchor is touched.

| check | result |
|---|---|
| `git diff --stat b3086b46..lane/c2prep` (the branch point; `main` has since advanced) | **22 files, 19,617 insertions, 0 deletions, every one under `docs/`** |
| the same restricted to `src lib cli tests` | **empty** |
| both probes compiled `-Wall -Wextra -std=gnu11` with `gcc-16` | clean, no warnings |
| `reqpos_probe` vs batch 1's `RX_REQ_BYTE` on the capability set | **63 checked, 63 agree, 0 disagree, 1 skipped** |
| `reqpos_probe` smoke cases (11, hand-derived answers) | all correct, and identical across the iterative rewrite |
| `onepass_probe` smoke cases (13, incl. the survey's three named non-one-pass patterns) | all correct |
| throughput subjects regenerated from `captext.py` | all three SHA-256 values match `cycle1_analysis.md` 0.3's pins |
| scan-loop simulator vs the I-85 timings | the three baselines' identical counts predict their measured times to +0.01% |
| `make -j4 CC=gcc-16` in the worktree | clean (the probes link its `libpcrec.a`) |

**Not run, and not owed by this lane**: `make test`, `make strict`, `make
mech`, `make test-axes`. The box was carrying `worktrees/optimpl1`'s
answer-identity sweep throughout, and the brief's box rule held compile
sweeps to `PROCS=4` and forbade a suite; nothing in this delivery could move
one.

**Owed to Linux, named in the documents rather than here**:
`firstset_design.md` §7's four blocks (F1 the `json-constant` re-run that
gates the decline rule, F2 the soundness arm as a CORRECTNESS run, F3 what
the repair costs, F4 consumer (ii) on `nested-comment-rec`), and
`captures_via_dfa_survey.md` §3.6's M-B, untouched here and the measurement
that actually decides the one-pass row.

---

## Recommendations, for the manager to weigh at cycle 2's ranking

1. **`[OPT-FIRSTSET]` should not be implemented as ratified.** Either it
   carries §4.4's re-seed (an `abi` event, because the emitted scan loop gains
   a line) or consumer (i) is dropped and only the VM-route consumer (ii)
   ships, which §4.5 shows is unaffected by the soundness finding and is the
   cleaner half of the row anyway.
2. **The decline rule the profile asked for should not be built before
   `json-constant`'s ×1.10 is re-run.** It is the only calibration point that
   would justify a threshold and it is the only one that does not reconcile
   with its own artifact's counts.
3. **`[OPT-REQPOS]` should be re-scoped to tier 2b.** Tier 2's population is
   two losing cells; tier 2b's is five `capability` patterns that a word-grain
   pre-check would answer in one pass plus 734 corpus rows. If tier 2 is to be
   reconsidered, `bounded` is the subbench for it (six of its 43 patterns are
   tier 2, the densest anywhere) — which is D119's addendum letting the
   subbench follow the question.
4. **F1's pick rule is the cheapest thing in this delivery** and belongs ahead
   of both: it is a change to which member of a set `reqbyte.c` already
   computes, with a measured population of three whole-call answers on the
   bench's own subject.
5. **The one-pass row's next step is M-B, not a design note.** M-A is
   comfortably passed; nothing here says the second pass is worth removing.
