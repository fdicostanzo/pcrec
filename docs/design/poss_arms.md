# [ART-POSS-ARMS] — two possessify arms, widened soundly

**REVISION 2.1** (lane `possarms21`, 2026-10-07, from main `abb3db6c`). It
discharges the re-check of revision 2 (critic R, the "Re-check of rev 2"
section of `../dev/reviews/2026-10-07-r-poss-arms-panel.md`): rows N1, N2,
R-3(b), R-4, R-5, R-6, R-7 and R-8. Each edit is marked `[r2.1 <id>]`, and
§R2.1 tabulates them. **Read §R2.1 first.** R-3(a), the D27-blinded
composition pass, is a separate author's; this revision leaves its hook
(`poss_arms_measurements/rev21/run_composition.sh`, §8.8). Revision 2.1's
evidence is in `poss_arms_measurements/rev21/` (own CLAUDE.md).

**REVISION 2** (lane `possarms2`, 2026-10-07, from main `c2a0c6df`). It applies
every disposition of the D6 panel
(`../dev/reviews/2026-10-07-r-poss-arms-panel.md`). Each edit is marked
`[r2 <finding-id>]`, and §R2 tabulates them. Read §R2 first. Revision 1 was
lane `possarms`, 2026-10-07, from main `bcb7b128`.

DESIGN ONLY: nothing under `src/` changes on this branch. The plan row is
`docs/dev/plan.md` [ART-POSS-ARMS]. Its evidence is
`docs/dev/optloop/artrev/report_pilot.md` §5 item 1 and `generalize.md` I6,
and its rank is `docs/dev/optloop/round3_selection.md` 3a-2. The possessify
design of record is `eng_brep_design.md` §2, and the analysis is
`src/opt/possessify.c`. Revision 1's evidence is in `poss_arms_measurements/`;
revision 2's is in `poss_arms_measurements/rev2/`, and revision 2.1's in
`poss_arms_measurements/rev21/`. Each has its own CLAUDE.md.

**Headline.**

- `[r2.1]` **Rev 2's prototype MISCOMPILED with A0 and B together (N1),
  and that is fixed.** Arm B read a captured group's FIRST with
  `first_of`, which answers "the next character at a position". A0 makes
  that answer a NARROW, non-nullable set for a zero-width gate. A text never
  contains a gate, so arm B now uses `TEXT_FIRST`, in which a zero-width item
  is (∅, nullable) (§3.1). The three 10.46 witnesses answer (0,3).
- `[r2.1]` **Greedy-only is LOAD-BEARING (N2), not declared-conservative.**
  A lazy loop whose continuation can END through an empty bypass stops at its
  lowest exit, and A1 bypasses row 2's `may_end` (§2.3). The lazy plant is
  now a sabotage row.
- `[r2.1]` **Both arms' folds were QUADRATIC, and both are now linear
  (R-4).** Arm B's is one capture fact per group number, where in progress
  means widen. A1's is a continuation summary that does not depend on `Q`,
  found by this revision. The witnesses and the build-bar cells are in §8.7.
- `[r2.1]` **The predicate is FROZEN by sha1** (§8.3a). CLAIM-vs-MARK reads
  per-quantifier marks and pins the UCP refusals. A1's continuation must
  equal the walk's FOLLOW, as a build-time check (§8.7). The
  backreference-stays-VM tripwire is designed (§8.7). The blinded
  composition pass has its hook (§8.8).

- **Arm A** (a context gate in the follow) is **SOUND as restated, and with
  one more conjunct than revision 1 had.** A1 recomputes the loop's
  continuation, so it must cross a called group's end the way K93's join
  does: at zero consumption, the continuation unions the call sites' joined,
  A0-valued contexts (§2.3a). Without that union, A1 re-opens K93 on EVERY
  call-bearing pattern, not only on gate shapes. The unsound plant marks 16
  `tests/recursion/k93.rxt` patterns. `[r2 A-F1]`
- **Arm B** (a backreference's FIRST is the union of its groups' FIRSTs) is
  **SOUND as restated**. K94 is not a prerequisite. `[r2 C-K94]`
- **The arms move the default ENGINE as well as frames.** The atomic free
  discharge asks the same verdict. With the arms, `\w++\b` and `(?>\w+)\b`
  are discharged and go to the DFA. Measured over 4,132 patterns: **0**
  flips, with 186 patterns at risk.
  - Arm A's deny bit is therefore ENGINE-SELECTING.
  - **Arm B's is not, and cannot be.** A backreference needs a capture
    group, and a capture-bearing pattern is VM-routed. That half of the
    disposition is refuted (§9). `[r2 C-1]`
- **Every check the panel asked for now exists as a prototype, and each can
  fail.**
  - The exhaustive-subject possdiff detects all six planted defects, plus
    the A-F1 and termination plants.
  - CLAIM-vs-MARK agrees on every compared row and detects every plant
    without a subject.
  - Every ablated conjunct has a diverging control. ~~The exception is
    greedy-only, which the ablation shows is NOT load-bearing (§8.4).~~
    `[r2.1 N2]` Greedy-only included, once the family has a nullable
    follow (§8.4).
  - `[r2 B-B1, B-B2, B-B3]`
- **The give-up surface does NOT move one way.** Re-measured on ONE
  committed subject: the minimum work budget goes 394 denied → 1,199 with
  the arms, the same as the user-written possessive spelling. The two
  conflicting rev-1 pairs came from two uncommitted subjects. `[r2 B-M3]`
- **Census (K35), re-based on post-K93 `possessify.c`:**
  - **frames move on the DEFAULT route on 3 bench / 3 corpus patterns**, the
    same six as revision 1;
  - the denominator is 4,132 patterns, of which 393 are refused, with a
    committed list. `[r2 B-M4]`
- **abi event: yes.** The ids, bits and the abi number are taken at build,
  by grep. **Cost: M** (revision 1 said S). `[r2 C-S*, ranking]`

---

## §R2.1 — what revision 2.1 changed, finding by finding

| finding | where | what was done | evidence (`poss_arms_measurements/rev21/`) |
|---|---|---|---|
| N1 BLOCKER | §2.1, §3.1, §3.2, §7 | arm B reads `TEXT_FIRST` (a zero-width item is (∅, nullable)); the two `first_of` questions are named as [POSS-CTX-TABLE]'s READER field | `proto_rev21.patch`; `witnesses_r21_10.46.out`; plant S567 DETECTED |
| N2 MAJOR | §0, §2.3, §8.2, §8.4a, §11 | greedy-only KEPT and is now load-bearing (477/3,964 lazy rows diverge once a bypass follow exists); the lazy plant is a row | `results/keep1/eq_a21.out`; plant S568 DETECTED |
| R-3(b) | §8.3a | predicate FROZEN by sha1; the post-freeze edit rule; two edits applied under it, per category; hand vs computed reported apart | `gen_*21.py`, `results/out2/claimmark.out` |
| R-4 | §3.1, §7, §8.7 | capture fact once per group number (in progress = widen, state on the walk); NEW: A1's continuation summary; compile-time witnesses with a build-bar cell | `timing_r4.sh`, `results/out2/timing.out` |
| R-5 | §8.7 | A1 ≡ FOLLOW as an always-on check over the summary; atomic-end sentinel | census R5 5,437/5,437 eq |
| R-6 | §8.7 | backref-stays-VM tripwire in `tests/reject/` | verified refused today |
| R-7 | §8.3a | per-quantifier marks from `--emit-ir` strategies; `UCP_PIN` 4,502 and its trigger in [UCP]/[CLS-TREE] | `r21_claimmark.py` |
| R-8 | plan.md | [ART-POSS-ARMS] body corrected | — |
| R-3(a) hook | §8.8 | `run_composition.sh` (four harness passes, divergence + reach) | smoke: plant detected |

## §R2 — what revision 2 changed, finding by finding

| finding | sev | where | what was done | evidence (`poss_arms_measurements/rev2/`) |
|---|---|---|---|---|
| A-F1 | BLOCKER | §2.3a, §8.2 | fix (a): a cap-end / root-end marker in A1's continuation unions `cc[g].follow ∪ cc[g].encl` (A0-valued); `cc` never holds an A1 value. Both witnesses are now possdiff patterns and a sabotage row. They are also .rxt cells, owed by the build (§8.2) | `proto_rev2.patch`; `pdx/plant_A1_NOCC.log`; `claimmark.out.gz` rows C0001/C0002/C0005/C0006; `census_r2.tsv.gz` (`vm_ABnocc`) |
| C-2 | HIGH | §2.3a | option (b) is chosen: a joined context supplies only the P = {0,1} component. The triple is not well defined, and its measured gain is 0 | `census_r2.tsv.gz` |
| C-1 / B-M1 | HIGH | §5.4, §9 | route-flip census: 0 flips over 4,132, 186 at risk. A's deny bit goes in the `kept` set, with `--engine=dfa` refusal witnesses and spec sentences. **B's bit is REFUTED as engine-selecting**: it can never move `RX_ENGINE` | `census_r2.tsv.gz`, `routeflip_witness.{sh,out}`, `pdx/routeflip_default.log` |
| B-B1 | BLOCKER | §8.1, §8.2 | exhaustive subjects, split by code point; a REACH check per (pattern, witness); `# flags:`; all plants run | `subjects_exh.py`, `possdiff_exh.sh`, `possdiff_plants.sh`, `pd_*.txt`, `pd_reach.tsv`, `pdx_verdicts.txt` |
| B-B2 | BLOCKER | §8.3 | CLAIM-vs-MARK over every claimed row plus a 1-in-10 stratified sample; mixed-LAST body added. It found two places where the INDEPENDENT predicate was narrower than the rule, both oracle-confirmed sound | `gen_a2.py`, `gen_b2.py`, `r2_claimmark.py`, `claimmark.out.gz`, `claimmark_v1.out.gz` |
| B-B3 | BLOCKER | §8.4 | ablation table at ML ≥ 4; depth-1 termination witness and plant | `a2_abl_ml4.out.gz`, `a2_new_ml4.out`, `b2_ml5.out`, `pdx/plant_SAB_NORECGUARD.log` |
| B-M2 | MAJOR | §8.5 | `<PREFIX>_VM_POSS_ARMS` stamp, a `poss-arms-moved` bucket, the emit_sweep mover rule | design only (build-time) |
| B-M3 | MAJOR | §6, §8.6 | committed subject; one re-measurement; run_axes' classifier and allowance; `outcome_word.h`; a fourth class | `wb_subject.py`, `minwb2.sh`, `wb_runs.tsv` |
| B-M4 | MAJOR | §5.2, §5.3 | A0 family sweep; denominator and refused list; deny-delta re-count at build | `gen_a0.py`, `a0_ml4.out.gz`, `census_r2_refused.tsv` |
| A-F3 | LOW | §2.1 | the empty-S widening rule replaces "belt and braces" | `proto_rev2.patch` (`px_S`) |
| A-F4 | LOW | §2.1 | the prototype's rule is adopted (narrowed gates are non-nullable), with the reason | `census_r2.tsv.gz` (`vm_ABa0null` = `vm_AB` on all rows) |
| B-M5 | MAJOR | §8.1 | `# flags:` header, no TAB column, a named floor, per-arm firing from `--emit-ir` | `possdiff_exh.sh` |
| C-S1..S9 / B-M6 / A-F2 | MED | §1, §6, §9, §11, plan row | §1 rewritten as history; Q4 struck; spec drafts cut to the arms' sentence; citations by name; ids, bits and abi at build | — |
| C-K94 | — | §3.3 | not a prerequisite; Latin-1 cells held out; seam ⊆ T2 inclusion check | — |
| Q3 / Q6 / Q7 | — | §11 | applied as ruled | — |
| B-FAM | — | §7, plan, survey | [POSS-CTX-TABLE] filed | `../dev/plan.md`, `decision_families_survey.md` |

## 0. The verdict this extends, restated

`pss_verdict` in `src/opt/possessify.c` is a first-match ladder over one
`A_REP` `Q = X{m,n}`, with `base_ok = uniq(X) && !nullable(X)`. `[r2 C-S*]`
Code is cited by function name. Line numbers are taken at build.

| # | row | fires when |
|---|---|---|
| 1 | exact-count | `base_ok && m == n` |
| 2 | lazy decline | `base_ok && disjoint && lazy && may_end` (returns NO) |
| 3 | disjointness | `base_ok && disjoint` |
| 4 | default | NO |

Here `disjoint` means `FIRST(X) ∩ (FOLLOW(Q) ∪ ENCL) = ∅`. FOLLOW is built
from `first_of` and, since K93 (D154), is widened at every called `A_CAP` by
the join of that group's call-site contexts `cc[g]` (`cc_widen`). Both arms
change what `first_of` answers for one node kind each, so neither adds a row
to this table.

- **Arm B** changes `first_of`'s `A_BREF` arm. It is context-free.
- **Arm A** changes `first_of`'s `A_CTX` arm in two ways:
  - **A0**, a context-free refinement;
  - **A1**, a Q-relative refinement. It is an INPUT to row 3 and is
    computed for a greedy `Q` with `m ≥ 1` (§2.3). ~~§8.4 measures that the
    greedy restriction is conservative~~ `[r2.1 N2]` The greedy restriction
    is LOAD-BEARING: row 3 alone is sound only because a greedy loop takes
    its top exit first (§2.3, §8.4).

## 1. History: the call-target miscompile, and the join that fixed it `[r2 C-S1, C-S2, A-F2]`

Revision 1 found a pre-existing miscompile on main:

- possessify judged a quantifier inside a SUBROUTINE-CALL TARGET against
  the group's lexical follow;
- every call site re-runs the body under its own follow;
- `(a+)b(?1)a` on `abaa` gave NOMATCH, where 10.46 gives (0,4).

Revision 1 proposed widening a called group's follow to all bytes. **That is
not what landed.**

**What landed (K93, D154, merged 60366d74): the JOIN.** `pss_run` drives a
per-group table `cc[g]` (`CallCtx`: `follow`, `encl`, `may_end`, keyed by
group number; 0 = the root, for `(?R)`) to a fixpoint with context-only
walks (`P->collect`). The `A_CALL` arm joins its site's context (`cc_join`).
A call inside a lookaround joins the top context (`cc_top_visit`). The
`A_CAP` arm (and `pss_root`, for `(?R)`) then walks the body under the
lexical context ∪ the join (`cc_widen`). There is one verdict per node and
it holds at every site. The atomic free discharge (`pcrec_poss_survey`)
runs the same walk, so it is covered too. Frank's per-copy alternative is
filed as [POSS-CALL-COPY].

**`(?R)` follows the sound answer (D154 addendum 1).** `(?:b(?R)a|a+)` on
`baa` is (0,3), equal to PCRE2 under `NO_AUTO_POSSESS`. PCRE2 10.46's
default (1,3) is U18, reported upstream as PCRE2Project/pcre2#1034.
Revision 1's Q4, which recommended PCRE2's default, is **STRUCK**.
`[r2 C-S2]`

**The consequence for this note** is A-F1 (§2.3a). A1 is a second follow
computation, so it must see the join as well.

## 2. Arm A — a context assertion in the follow

### 2.1 The fact

`A_CTX(C, fn)` covers `\b`, `\B` and every single-character lookaround
(`internal.h`'s `A_CTX` note; built by `src/parse/ctxnode.c`). Its truth
function `fn` is a 4-bit table indexed by `(p << 1) | q`, where:

- `p` means the previous character is in `C`;
- `q` means the next character is in `C`;
- an absent character (subject start or end) reads as NOT in `C`.

Suppose the analysis knows a set `P ⊆ {0,1}` of possible `p` values at a
position. Then the gate can be passed only where the next character's
membership `q` is in

    Q(P) = { q : ∃ p ∈ P, fn(p, q) }

**Representation, for `first_of`.** `first_of` works in code-point space
capped at 0xFF. A set with a member above 0xFF is widened to all 256 bytes
(`pcrec_cls_bits_widen`). So:

- `S(P) = { c ≤ 0xFF : (c ∈ C) ∈ Q(P) }`;
- if `Q(P) = {0,1}`, keep today's answer (all bytes, non-nullable).

This keeps the change byte-identical for every gate it cannot narrow.

**The truncation rule** `[r2 A-F3]`. Truncation at 0xFF is exact against
every set `S` is ever compared with. Every such set either holds no member
above 0xFF, or holds one and has therefore been widened to all 256 bytes,
which meets any NON-EMPTY `S`. So truncation can be unsound in only one way:
`S` comes out EMPTY while the true set is not. The rule is therefore:

> **If `Q(P)` is non-empty and `S(P)` comes out empty, widen to all bytes.**

This replaces revision 1's "FIRST(X) contains no code point above 0xFF"
conjunct, which it subsumes. A widened `FIRST(X)` meets every non-empty `S`.
An empty `S` with an empty `Q(P)` is the true answer: the gate never passes,
as in `\w+(?<!\w)`. The hazard is real on 10.48 (`[a\x{100}]+(?=\x{100})`).
It is unreachable today: `ctxnode.c`'s `t3_ctx_applies` builds an `A_CTX`
only when its set is byte-expressible under the encoding, so under `-e utf8`
both `C` and its complement keep members ≤ 0xFF. The rule is in the
prototype (`px_S`). Its plant (`PROTO_SAB_NOWIDEN`) has no reachable
witness, and the build carries it as a stated invariant with a unit cell
(§8.2).

**Nullability** `[r2 A-F4]`. **A narrowed gate is NON-NULLABLE.** This is the
prototype's rule. Revision 1's prose said "nullable iff `fn(p,0)` for some
`p ∈ P`". The census measured the prototype's rule, so the prose is changed
to match it. The rule is tighter and justified:

- Every reader of possessify's FIRST/nullable asks about a RETREAT exit
  `e_k` (`k < K`). That is rows 2 and 3, the survey's same verdict, and an
  inner quantifier's follow judged against ITS retreat exits.
- At a retreat exit the right-hand character EXISTS: it is iteration
  `k+1`'s first character, which is in `FIRST(X)`.
- A gate there must read that character. "Non-nullable" states exactly that
  the continuation cannot succeed without a next character, which holds at
  every position any reader asks about.
- End of subject is reached only at the TOP exit `e_K`, and neither row
  reads the continuation there.
- It is also today's value: the shipped `A_CTX` arm already returns
  `nullable = false`. The nullability column is therefore byte-identical by
  construction.
- Measured: the census under revision 1's prose rule (`PROTO_A0_NULLABLE`)
  equals the census under the adopted rule on all 4,132 patterns
  (`vm_ABa0null` = `vm_AB`). The K35 re-count therefore shows no delta from
  this choice.

**The rule holds for ONE reader, and revision 2 had a second** `[r2.1 N1]`.
Every bullet above is about a reader of the NEXT CHARACTER AT A POSITION.
Arm B (§3.1) also called `first_of`, on a captured group's body, and asked
a different question: which character can the captured TEXT begin with. A
gate is not in any text. In `((?=a))` the group captures the empty string,
yet revision 2 answered FIRST(`\1`) = {`a`}, non-nullable. A0 + B together
then miscompiled on the default route with no plant (critic R; 10.46 (0,3),
prototype NOMATCH on `abb`):

- `(?:((?=a))a)?b+\1b`, `((?=a)c?)ab+\1b`, `(?:((?=a))a|)b+\1b`.

Before A0, `first_of` answered ALL BYTES for every gate, and all bytes
declines every disjointness test, so the wrong nullability was masked. A0 is
the first producer of a NARROW answer for a zero-width node, which is why the
two questions first disagree here. The fix is on the TEXT reader (§3.1's
`TEXT_FIRST`), not on this rule. [POSS-CTX-TABLE]'s context record carries
the two questions as a READER field (§7).

### 2.2 The two rows

| row | P | where it is sound | what it reaches |
|---|---|---|---|
| **A0** | `{0,1}` (nothing known about the left) | everywhere `first_of` is read: rows 1-3, the lazy conjunct, the free discharge's survey, the call-site joins | lookahead-born gates, whose `fn` ignores `p`: `(?=C)` gives `S = C`; `(?!C)` gives `S = ¬C`; both non-nullable (§2.1) |
| **A1** | `{ pol_C(c) : c ∈ LAST(X) }` | row 3's disjointness, for `Q` greedy with `m ≥ 1` and `base_ok`, over `Q`'s own continuation (§2.3) | `\b`/`\B` and the lookbehind forms after a loop whose LAST characters share one polarity |

A0 needs no argument beyond §2.1. `\b`, `\B` and the lookbehinds get nothing
from A0, because their `fn` depends on `p` and `Q({0,1}) = {0,1}`.

### 2.3 Why A1 is sound (the precise predicate)

**Premise** (from `base_ok`, eng_brep §2.3). With `X` admitting a unique
iteration and non-nullable, the loop's reachable exits from a given start
form a strictly increasing chain `e_m < … < e_K`. The greedy loop takes
`e_K` first. A possessive `Q` differs from a greedy one only if some retreat
exit `e_k` (`k < K`) leads to a match while `e_K` does not.

**At every retreat exit `e_k` with `k ≥ 1`:**

- the character before `e_k` is the last character of iteration `k`, so it
  is in `LAST(X)`;
- the character at `e_k` exists. It is the first character of iteration
  `k+1`, so it is in `FIRST(X)`.

`m ≥ 1` makes `k ≥ 1` hold for every exit. With `m = 0`, `e_0` is a retreat
exit whose left character is whatever precedes `Q`.

**The conclusion.** Every continuation from `e_k` that reaches a gate
before consuming a character tests that gate at `e_k`. It passes only if
`s[e_k]` has a membership in `Q(P_C)`. So the continuation's FIRST,
computed with `P_C` at those gates, over-approximates "the characters at
which the continuation can start at `e_k`". If `FIRST(X)` is disjoint from
it (and from `ENCL`), the continuation fails at every retreat exit.

**Gates reached at zero consumption, and why this is not a separate
conjunct.** `P_C` is valid only at `e_k` itself. A FIRST computation reads a
gate only on the continuation's EMPTY path:

- along `A_CAT` past a nullable item;
- into `A_ALT` branches, `A_CAP` and `A_ATOMIC`;
- into an `A_REP`'s first iteration.

A gate behind a consuming item contributes nothing to FIRST, because the
consuming item's own first set stands in front of it. So "zero consumption"
is a property of FIRST, not a condition the implementation tests. `P` is a
parameter of the fold, never a fact about a node. This is why §8.4 has no
ablation row for it.

**The enclosing-loop term.** `ENCL` is unioned UNGATED, as today. The
§2.2 / R24 H1 line stays load-bearing for the base rule, and **for A1 too**
`[r2 B-B3]`:

- A gate with an empty BYPASS lets the continuation reach the enclosing
  loop's end at zero consumption, and the loop's restart then rescues the
  match.
- Witness: `(?:a+(?:\b|)|ab)+c` on `aabc` gives (0,4) greedy and (1,4)
  possessive on 10.46. A1 without ENCL would claim it.
- Where the gate HEADS the in-body continuation, the restart can only
  happen behind it, and the ungated union is merely conservative:
  `(?:\w+)+\b` and `(?:x+\1|(a))+` decline and do not diverge (§8.4: 2,268
  such rows, 0 diverging).
- Gating `ENCL` to those shapes would be a refinement with its own
  refutation surface. It is not part of this build (RC-Q2).

**Why greedy-only — LOAD-BEARING** `[r2.1 N2]`. ~~Revision 2 kept the
conjunct as declared-conservative: dropping it claimed 1,134 lazy rows, 0
diverging at ML=4, and the argument was that a lazy loop stopping early stops
at a retreat exit, where the A1-valued continuation cannot succeed.~~ That
argument covers only continuations that READ a character at `e_k`. Critic
R's 10.46 witness: `(\w+?(?:\b|))` on `ab` is (0,1); with A1 admitted for
lazy loops it is (0,2).

- **Why it breaks.** A lazy loop stops at the LOWEST exit where the
  continuation succeeds. A continuation with a path to the match end that
  tests no gate and reads nothing (here the empty bypass `|)`) succeeds at
  every exit. So the lazy loop stops at `e_m` and the possessive spelling at
  `e_K`. That is row 2's case (`lazy && may_end` declines). A1 feeds only
  row 3's disjointness, so a lazy A1 skips row 2's may_end.
- **Why greedy is safe.** A greedy loop tries `e_K` first. A gate-free empty
  path succeeds there, and the loop never retreats. A path that fails at
  `e_K` but could succeed at a retreat exit `e_k` must read `s[e_k]`, which
  is the A1 argument above.
- **Why rev 2 measured 0.** `gen_a2.py`'s follows had no nullable follow
  (each consumes or gates), and its only lazy quantifier was `+?`. Rev 2.1's
  generators add the bypass follows `(?:\b|)`, `(?:\B|)` and
  `(?:(?=C)|)`, the bounded lazy `{1,3}?`, `{2,}?` and `{2,4}?`, and the
  witness rows. Lazy ablation re-measured: §8.4.
- **The sound lazy rule exists but is not built.** It would re-ask row 2 with
  the A1 continuation's own end-reachability: does the continuation reach the
  match end on a path that tests no narrowed gate. That is a second row with
  its own refutation surface. Its population is unmeasured, and D77 says
  wait.
- **The lazy plant is now a SABOTAGE ROW** (§8.2), with this witness. It is no
  longer a control.

A0 needs no such conjunct. It is valued inside `first_of`, so row 2 sees the
bypass's nullability directly: `[a-c]+?(?:(?=x)|)` declines through
`may_end`. The A0 family sweep re-runs with the bypass follows (§5.3).

#### 2.3a A1 across a call boundary `[r2 A-F1, C-2]`

**The defect revision 1 had (A-F1).** A1 recomputes `Q`'s continuation from
the lexical tree. Inside a called group, the lexical continuation reaches
the group's end and then continues with whatever follows the group at its
DEFINITION. Every call site continues differently. The shipped walk already
knows this (`cc_widen` at the `A_CAP`), but A1's recomputation did not. Two
10.46 witnesses:

| pattern | subject | greedy | possessive |
|---|---|---|---|
| `(a+(?:\b\|))\|b(?1)a` | `baa` | (0,3) | (1,3) |
| `(?:b(?R)a\|a+(?:\b\|))` | `baa` | (0,3) | (1,3), the U18 shape |

**It is broader than the panel's two witnesses.** For a continuation with
no gate, A1's lexical recomputation IS the lexical follow. Dropping the
join from A1 therefore re-opens K93 itself on every call-bearing pattern.

- Measured with the unsound plant `PROTO_A1_NOCC`, it newly marks **16**
  patterns in `tests/recursion/k93.rxt`, every one a K93 witness:
  `vm_ABnocc` against `vm_AB` in the census.
- The corpus therefore detects this plant by itself.

**Fix (a), the general form.** A1's continuation is a chain of items with a
marker at the END of every `A_CAP` it leaves (the walk pushes it in its
`A_CAP` arm). When the fold reaches a marker for group `g` at zero
consumption, it unions `cc[g].follow ∪ cc[g].encl`. At the root end it
unions `cc[0]`, for `(?R)`. These are the join's values, computed by the
context-only walks with `first_of`, so they are **A0-valued**. **`cc` never
stores an A1 value**: A1 depends on `Q`, and one table cannot hold a value
per `Q`. Both witnesses decline under the fix. The calls that stay sound
keep their mark: `(\w+\b)x(?1)` and `(\w+\b)x(?1)y` (0 diverging on
libpcre2, `b2_ml5.out` C0003/C0004).

**The representation (C-2), and the choice.** The joined contexts supply
only the **P = {0,1} component**. A P-indexed triple was the alternative.
Three reasons for the choice:

1. **It is sound.** For every P, `Q(P) ⊆ Q({0,1})`, so the A0 value is a
   superset of every A1 value. A join only widens, and a wider follow only
   declines more.
2. **The triple is not well defined.** `P` is a polarity relative to ONE
   gate set `C`. A call site's continuation can hold gates over different
   sets: `\w` for `\b`, any `C` for `(?<=C)`. A P-indexed value would have
   to be keyed by `(C, P)` for every gate set in the program, or by `Q`'s
   LAST class itself. That is a per-`Q` table again.
3. **Its measured gain is zero.** `PROTO_A1_NOCC` drops the join entirely.
   That is an unsound UPPER bound on anything a per-P join could recover. It
   differs from the built rule on 16 corpus patterns and 0 bench patterns.
   All 16 are K93 witnesses whose call-site follow is a plain byte the loop
   itself consumes, which no `P` removes. So the triple would recover
   **0** marks.

The cost moves from S to S-M, as the panel projected. With the other
dispositions, the row's total is M (§9).

**The full predicate, as one sentence.** For `Q = X{m,n}` greedy with
`m ≥ 1` and `base_ok`:

- let `P_C` be the polarities, with respect to `C`, of the code points in
  the classes at `X`'s Glushkov LAST positions;
- recompute `Q`'s continuation FIRST with every `A_CTX(C, fn)` reached at
  zero consumption valued `S(P_C)` (§2.1's empty-S widening applies);
- at every called-group end and the root end crossed at zero consumption,
  union that group's joined A0 context;
- union `ENCL`;
- grant row 3 if `FIRST(X)` is disjoint from the result.

### 2.4 What the row's wording got wrong — the counterexamples tried

Each line was a candidate rule, either the row's own wording or a simpler
one. Each was refuted by a libpcre2 equivalence check: the greedy spelling
under `no_auto_possess` against the possessive spelling, on the same
subjects. Rows were confirmed on 10.46 (`../poss_arms_measurements/
witnesses_10.46.out`). Revision 2's new witnesses were confirmed in one
light session (`rev2/witnesses_r2.pcre2test` → `rev2/witnesses_r2_10.46.out`):
A-F1's two, ENCL's control, the arm × call decline, the `\B` and
empty-reference claims, the depth-1 cycle, and a lazy `(?!C)` at the end.

| candidate | witness | greedy | possessive | the conjunct it buys |
|---|---|---|---|---|
| "a subset of `\w`" tested on the LITERAL | `k+\b`, `utf,i`, subject `k` U+212A | (0,1) | NOMATCH | wordness is read on the FOLDED code-point class. `(?i)k` under UTF folds to {k, K, U+212A}, and U+212A is not `\w` without UCP. pcrec is safe structurally: `cls_casefold` folds at parse time, so the class carries the code points |
| `m ≥ 0` | ` \w?\b`, subject ` aa` | (0,1) | NOMATCH | `m ≥ 1`: the `e_0` exit has an unknown left character |
| polarity read from FIRST(X) | `(?:a\.)+\b`, subject `a.a.` | (0,2) | NOMATCH | polarity is read from LAST(X) |
| a mixed LAST read as one polarity | `(?:a[a.])+\b`, subject `a.a.` | (0,2) | NOMATCH | `P_C` is the SET of polarities; a mixed set gives `Q(P) = {0,1}`, which declines |
| lexical continuation only (A-F1) | `(a+(?:\b\|))\|b(?1)a`, subject `baa` | (0,3) | (1,3) | the call-site join at a called group's end (§2.3a) |
| an impure class | `[a .]+\b`, subject `a ` | (0,1) | NOMATCH | none needed: `P = {0,1}`, so A1 declines |

What the restatement makes WIDER:

- **Multi-character bodies.** `(?:ak)+\b` and `\B(x|ab){1,2}\b` are sound.
  The latter is `tests/startset/hybrid.rxt:280`, and the rule fires on it.
- **`\B` after a multi-character body** `[r2 B-B2]`. `\B` admits the left
  character's OWN wordness. For a single-class body, `FIRST(X)` has that
  wordness, so A1 declines, as revision 1 said. A multi-character body
  whose FIRST and LAST polarities differ is claimed and sound:
  `(?:a\.)+\B`, LAST `.`, FIRST `a`. Revision 1's generator never modelled
  `\B` as a gate. CLAIM-vs-MARK found the prototype marking these rows, and
  the predicate was corrected (`gen_a2.py`): 108 `\B` rows claimed, 0
  diverging.
- **A gate behind an empty-able reference** `[r2 B-B2]`. In `(a?)x+\1\b`,
  when `\1` is empty the `\b` is reached at zero consumption from `x+`'s
  exit. A1 values it there. Revision 1's arm-B generator widened the gate
  instead ("arm A does not apply"). 16 rows are claimed and 0 diverge.
- **Lookaround-born gates through A0.** `[A-Za-z0-9.]+(?=@)` (bench
  `email-local-nodup`) and `\d+(?![\d.])` (bench `float-literal-bound`)
  both fire. A0 is sound for lazy loops and `m = 0` too (§5.3).

**Sweep, arm A** (`rev2/gen_a2.py` → `eqcheck.py`, libpcre2 10.48 local):

- **Population:** 24,300 pattern pairs = 15 bodies × 6 quantifiers × 9
  follows × 5 wrappers × 6 modes. The mixed-LAST body `(?:a[a.])` is new.
- **Claims:** 3,402 (revision 1's 3,294 plus 108 `\B`).
- **Claims re-swept at ML=4** (every string of length ≤ 4 plus 100 random,
  7,481-11,211 subjects per pattern): **3,294 claimed, 0 diverging**. The 108 `\B` claims
  are new and are swept at ML=4: 0 diverging.
- **Ablation controls** at ML=4: §8.4.
- **Independence:** the CLAIM column is computed in Python from class
  membership asked of libpcre2 itself (`^(?:C)$` per character per mode). It
  is never computed from pcrec.

### 2.5 Flags, one line each

- **caseless:** classes are folded at parse time, and `C` is not affected
  (`\w` under `(?i)` is `\w`). The polarity is read from the folded class.
- **utf:** FIRST and `S` are code points ≤ 0xFF, and anything above widens
  (§2.1's truncation rule). Under `-e utf8` without UCP, `\w` is ASCII, so
  `\w+\b` fires.
- **ucp:**
  - Under `-e utf8 --ucp`, pcrec today REFUSES UCP `\w`. It is a wide set,
    refused until [CLS-TREE] S4 / [UCP] U3. All 2,059 `utf,ucp` rows that
    CLAIM-vs-MARK selected are therefore refused, and it records them as
    REFUSED. When
    the route lands, `\w` reaches above 0xFF, `FIRST(X)` widens, and A1
    declines. That is a lost opportunity, not an error.
  - Under `byte --ucp`, `\w` includes Latin-1 letters. `C` comes from the
    same resolution, so `é+\b` fires correctly.
- **multiline:** irrelevant to the gate.
- **ungreedy `(?U)`:** read the node's parse-resolved `greedy` (D62).
- **recursion / calls:** §2.3a.
- **empty subject / startpos:** a retreat exit always has both neighbours
  inside the loop's own text.

## 3. Arm B — a backreference's FIRST

### 3.1 The fact

PCRE2 reads a backreference `\n` (`A_BREF`, `refs[]`) as follows. It takes
the text of the FIRST SET member of `refs[]`, in ascending group number, and
compares it caselessly if the REFERENCE is caseless (`u.bref.caseless`,
D62). An unset reference FAILS. `PCRE2_MATCH_UNSET_BACKREF` is out of scope.

Every value a published capture can hold is a string some `A_CAP` node with
that number matched. Captures written inside a subroutine call are restored
on return, and a negative assertion keeps no capture.

**The rule:**

    FIRST(\n)    = fold_ref( ∪_{g ∈ refs} CAP(g) )                   [r2.1 N1, R-4]
    CAP(g)       = ∪_{A_CAP c : c.no == g} TEXT_FIRST(c.body)   (once per g)
    nullable(\n) = ∃ such c with TEXT_nullable(c.body)

- `fold_ref` is applied only when `u.bref.caseless` is set.
- An unset member contributes nothing, because it fails.
- **`TEXT_FIRST` is not `first_of`** `[r2.1 N1]`. It answers "which
  character can a captured TEXT begin with". It is `first_of`'s fold with
  every ZERO-WIDTH kind answering (no bytes, nullable): `A_CTX`, `A_LOOK`,
  `^`, `$`, `\z`, `\G`, `\K`, the empty node. A zero-width item contributes
  no character to a text, so this is exact, not an approximation. It is NOT
  the A0/A1 valuation, which is a fact about the next character at a
  POSITION (§2.1's last paragraph). Every other kind defers to `first_of`
  (a nested reference re-enters `CAP`). Revision 2 called `first_of` here,
  which is N1's miscompile. Its plant is `PROTO_SAB_TEXTPOS` (§8.2).
- **`CAP(g)` is computed ONCE PER GROUP NUMBER** `[r2.1 R-4]`.
  - One walk indexes every `A_CAP` by number. Lookaround and DEFINE bodies
    are included. A call's body is a back edge and is not followed.
  - `CAP(g)` is memoized in the walk's state. A group whose value is IN
    PROGRESS when asked again (a reference cycle, `(a\2)(b\1)`) answers
    WIDEN.
  - This replaces revision 2's depth-1 counter, and it is strictly wider.
    A deeper reference now resolves: `(a)(\1b)x+\2` is claimed, and 10.46
    agrees on its witness (`rev21/witnesses_r21_10.46.out`).
  - **The cost was quadratic and now is not.** Revision 2 walked the whole
    tree for every reference. The measurements are in §8.7.
  - **The state lives on the walk, not in a file static.** The prototype
    hangs `CAP`'s table off `Ctx` for the duration of one `pss_run` and
    restores the previous value after. That is because `first_of` receives
    only `Ctx`. The build puts it on `Pss`, or on [POSS-CTX-TABLE]'s context
    record once `first_of` takes one.
- ~~**Depth-1.** Inside `FIRST(c.body)`, a nested `A_BREF`/`A_CALL`/`A_VAR`
  keeps today's widen. That also ends cycles such as `(a\2)(b\1)`.
  `[r2 B-B3]` This is a TERMINATION rule, not a soundness conjunct. A deeper
  resolution is sound: `(a)(\1b)x+\2` resolved to depth 2 does not diverge
  (`b2_ml5.out`). What depth-1 buys is that the fold terminates without a
  visited set. Its witness is `(a\2)(b\1)x+\1`, which is claimed, compiles,
  and does not diverge. Its plant (`PROTO_SAB_NORECGUARD`, the guard
  dropped) does not terminate. It is detected as a compile timeout or
  crash (§8.2).~~ `[r2.1 R-4]` Superseded by the in-progress-widens rule
  above. The plant keeps its name and now means "an in-progress group is
  recomputed", which recurses without bound on the same witness.

### 3.2 Why each clause is there — the counterexamples tried

Same instrument as §2.4: 6 characters (`a b x space A .`), every string of
length ≤ 5 plus 300 random, 9,631 subjects each.

| narrower spelling | witness | greedy | possessive | clause |
|---|---|---|---|---|
| no fold at a caseless reference | `(a)A+(?i:\1)`, subject `aAA` | (0,3) | NOMATCH | `fold_ref` keyed on the REFERENCE |
| the group's unfolded literal | `(?i:(a))A+\1`, subject `AAA` | (0,3) | NOMATCH | `FIRST(c.body)` is the folded class |
| the first member of a name run | `(?J)(?:(?<n>a)\|(?<n>x))x+\k<n>`, subject `xxx` | (0,3) | NOMATCH | union over ALL of `refs[]` |
| the first `A_CAP` with the number | `(?\|(a)\|(x))x+\1`, subject `xxx` | (0,3) | NOMATCH | union over every `A_CAP` with that number |
| "non-nullable group" assumed | `(a?)x+\1x`, subject `xx` | (0,2) | NOMATCH | nullability is read from the member bodies |
| a gate read as the text's first character `[r2.1 N1]` | `(?:((?=a))a)?b+\1b`, subject `abb` | (0,3) | NOMATCH | `TEXT_FIRST`: a zero-width item is (∅, nullable) |
| unset reads as empty | `(?:(a)\|b)x+\1x` under `match_unset_backref`, subject `bxx` | (0,3) | NOMATCH | correct only while the option is out of scope |
| body non-nullable ⇒ capture non-empty | `(?=((*ACCEPT)a))x+\1x`, subject `xx` | (0,2) | NOMATCH | `(*ACCEPT)` closes a group early, even EMPTY |

"Closed" is not needed, and "non-nullable" is the wrong condition
(revision 1's argument, unchanged).

**Sweep, arm B** (`rev2/gen_b2.py` → `eqcheck.py`, ML=5, NR=300):

- 669 rows: revision 1's 660, plus the two depth-1 rows and seven
  arm × call rows.
- **418 claimed, 0 diverging; 231 non-claimed rows diverge** (the controls).
- Every ablated clause diverges (§8.4).

### 3.3 Flags and the tripwires

- **caseless:** use the fold relation T2 selects for a LITERAL at the
  reference's scope. That is `pcrec_ast_class_from_cpset`'s own relation,
  so build a cpset from FIRST and publish it through that producer. Do not
  re-implement the fold.
- **K94 is NOT a prerequisite** `[r2 C-K94]`. K94 (lane `k94fix`) is the
  seam's Latin-1 fold gap: a byte-backend caseless backref under `--ucp`
  folds ASCII only. Arm B folds with T2's relation. T2's relation is a
  superset of the runtime compare both before and after K94's fix, so the
  arm is sound in both states. Two consequences for the build:
  - Latin-1 byte + `--ucp` caseless-backref cells stay OUT of arm B's .rxt
    cell set until K94 merges. Their expectation is K94's to settle.
  - `tests/backrefs/fold_agreement_check.c` gains a **seam ⊆ T2 inclusion
    check**: every pair the encoding seam's caseless compare equates, T2
    also relates. That is the property arm B's soundness rests on, and it
    holds on both sides of K94.
- **utf:** a fold that leaves ASCII (k → U+212A, s → U+017F), or any member
  above 0xFF, widens to all bytes.
- **duplicate names / `(?|`:** these are the union clauses above. `(?|` is
  unbuilt, so its clause is satisfied by construction today. Resolving
  `refs` → `A_CAP` by NUMBER over every `A_CAP` makes it correct on arrival.
  That is the same by-number keying K93's join uses (§7).
- **The tripwires** `[r2 Q6]`. These follow B's form; revision 1's
  `check_engine_capability_tripwire` was retired at [M6.4.2]. The count is
  corrected: there is **one** soundness tripwire.
  - **`(*ACCEPT)` (module `verbs`).** When `verbs` gains a producer,
    `nullable(\n)` must become true for any group that can contain
    `(*ACCEPT)`. `tests/registry/registry_check.c` asserts that the
    `(*ACCEPT)` row stays `unbuilt` in `--list-syntax`. Its failure message
    names arm B's clause and the 10.46 witness `(?=((*ACCEPT)a))x+\1x` on
    `xx`. A `features verbs` .rxt block holding that witness is `perr`
    today, and it starts compiling the day the module does.
  - **`(?|`.** The same registry assertion covers the `(?|` row, but as a
    RE-VERIFICATION prompt, not a soundness tripwire. By-number resolution
    is already correct for it. When the module lands, the
    `(?|(a)|(x))x+\1` cell joins the sweep.
  - **`MATCH_UNSET_BACKREF`** has no producer, so nothing is keyed on it.
    If it ever ships, an unset member contributes "nullable".
- **recursion / calls:** captures set in a call are restored.
  `(?(DEFINE)(?<w>(a)))(?&w)x+\2` is claimed and does not diverge. A `Q`
  INSIDE a call target is governed by the join (§1, §2.3a). Arm B needs no
  extra conjunct there, because `FIRST(\n)` is context-free.
  - Measured: `(a)(x+\1)b(?2)x` is claimed with 0 diverging.
  - `(a?)(x+\1)b(?2)x` declines. Its `\1` can be empty, so the follow
    crosses the called group's end, where the join adds the call site's
    `x`.
  - Its lexical-only reading is unsound: 13 diverging subjects on
    libpcre2, witness `xbxx` (`b2_ml5.out` C0006).
- **`A_VAR`:** keeps today's widen.

## 4. The combined witness: `doubled-word`

`\b(\w+)\b\s+\1\b` has:

- `\w+`, followed by `\b`: A1 marks it, with `P = {in}` and `S = ¬W`;
- `\s+`, followed by `\1`: arm B marks it, with `FIRST(\1) = W`.

With both marked, the program is frameless. Textual `RX_PUSH(` sites go
3 → 1 and the artifact stamps `RX_VM_FRAMELESS 1`. The armed program equals
the user-written `\b(\w++)\b\s++\1\b`'s: the work-budget minimum is the
same 1,199 on the committed subject (§6). Both spellings answer
`the the cat` → (0,7) on 10.46.

## 5. Population (K35) — counted, not inherited

### 5.1 The instrument and the denominator `[r2 B-M4, C-S*]`

`rev2/r2_census.py` drives the rev-2 prototype (`rev2/proto_rev2.patch`,
re-based on post-K93 `possessify.c`, env-switched). It is NOT the
implementation. The populations are [ARTREV]'s `census.py` loaders:

- every pcrec-bench `bench/*/patterns/*.rx` (read-only): 345;
- every distinct corpus `pattern`/`pattern-esc` block by (pattern,
  encoding, `-i`): 3,787.

**Denominator: 4,132 patterns.** 393 are refused by the base `--engine=vm`
compile: 23 bench and 370 corpus. They are listed with their reason in
`rev2/census_r2_refused.tsv`. The largest classes are deliberate refusal
cells (69 "quantifier does not follow a repeatable item", 40 variable-length
lookbehind, 42 `\p{...}` forms, 16 out-of-range `\x{...}`, 15 `\K` in a
lookaround, …) and the emitted-size caps (the `altwide/*-1024` bench
patterns). **Every count below is over the 3,739 that compile.**

### 5.2 Results

`rev2/census_r2.tsv.gz` records, per pattern: the marks under no arm, A, B,
A+B, A0 alone, the A1 path alone, A+B without the join (the A-F1 plant),
and A+B with revision 1's nullability. It also records the default-route
engine under BOTH the denied and the armed builds, push sites and
`RX_VM_FRAMELESS`.

| | bench | corpus |
|---|---|---|
| arm A fires (`--engine=vm`) | 6 | 12 |
| of which A0 alone | 3 | 0 |
| arm B fires (`--engine=vm`) | 1 | 1 |
| either | 6 | 13 |
| DEFAULT route, frames move | **3** | **3** |
| DEFAULT route DFA (frames moot) | 3 | 10 |
| DEFAULT route ENGINE moves | **0** | **0** |

The default-route movers are the same six as revision 1, re-measured on
post-K93 `possessify.c`:

- **bench `doubled-word`:** both arms; 3 push sites → 1; becomes FRAMELESS.
- **bench `email-local-nodup`:** A0, `(?=@)`; 4 → 3.
- **bench `wild-logparse-syslogbase-expanded`:** A1; 265 → 261.
- **corpus `wordb_vm.rxt:339`:** A1; 2 → 1; FRAMELESS.
- **corpus `startset/vmhat.rxt:381`:** B; 2 → 1; FRAMELESS.
- **corpus `startset/hybrid.rxt:280`:** A1 on `(x|ab){1,2}`; 4 → 3.

### 5.3 The A0 family sweep `[r2 B-M4]`

`rev2/gen_a0.py` puts lookahead-born and lookbehind-born gates in every
position the panel named:

- directly in the follow;
- in an ALTERNATION branch;
- inside a QUANTIFIED group in the follow;
- in the loop BODY itself;
- under an ENCLOSING loop;
- at the pattern END (the `(?!C)` nullability question);
- the lookbehind forms.

It covers greedy, lazy, `m = 0` and exact-count rows: 6 bodies × 7
quantifiers × 8 follows × 4 wrappers × 6 gate sets = 8,064 pairs.

- **3,000 claimed, 0 diverging** at ML=4. Each pattern gets 7,481 subjects:
  every string of length ≤ 4 over 9 characters, plus 100 random.
- **2,117 non-claimed rows diverge**, so the controls are not vacuous.
- Claimed rows exist in every position: direct, alternation branch,
  quantified group, gate in the body, lookbehind, and an enclosing loop
  (exact-count only).
- The claims include 552 lazy and 552 `m = 0` rows. A0 is sound for both,
  as §2.2 claims.
- That includes lazy loops followed by `(?!C)` at the pattern END. These
  are claimed under §2.1's non-nullable rule, so `may_end` is false, and
  none diverges. This is the measured half of A-F4.

The CLAIM is today's ladder with each gate valued as §2.1-§2.2 value it.
Membership is asked of libpcre2.

### 5.4 The route-flip census `[r2 C-1]`

The atomic free discharge (`src/opt/atomic.c`) asks `pcrec_poss_survey`,
which is the same walk and the same `pss_verdict`. The arms therefore widen
it. A discharged `(?>…)` or possessive suffix leaves the tree, and the
pattern can become DFA-eligible.

- **Measured: 0 of 4,132 patterns change default engine.** The population
  at risk was counted, not assumed: **186** patterns are VM-forced by an
  atomic group or a possessive suffix (180 corpus, 6 bench), and 117 of
  them are in `tests/atomic_groups`.
  - None of them puts an arm-reachable gate or reference after its
    possessive body.
  - The 189 `tests/atomic_groups` patterns were read separately: 133 vm→vm,
    43 dfa→dfa, 13 refused.
  - Both engines are recorded per pattern (`eng_base`, `eng_AB`). Revision
    1's census recorded only the last one it saw.
- **The constructed witnesses flip** (`rev2/routeflip_witness.out`).
  `\w++\b`, `(?>\w+)\b`, `x(?>\w+)\b`, `\d++(?![\d.])`, `[a-z]++(?=@)` and
  `(?>[a-z]+)(?=@)` each go vm → dfa by default. Denied, `--engine=dfa`
  REFUSES each with "possessive quantifier requires the VM engine" or
  "(?>...) requires the VM engine". Armed, it compiles.
  - Their DFA-route answers equal the VM-denied build's on the exhaustive
    sweep (`pdx/routeflip_default.log`).
- **A third give-up direction.** A pattern that moves to the DFA loses
  every match-time budget (the DFA has no STEPS, WORK or FRAMES), so its
  give-ups can only disappear. The DFA's own compile-time caps (state cap,
  emitted size) are the new refusal surface. On the measured population it
  is empty, since nothing flips. §9 states what the deny bits do about it.
- **The classification stands at zero flips** (C-1 (2)): ONE verdict.
  Arm A's bit is ENGINE-SELECTING. Arm B's is answer-identity-preserving,
  because no B-reachable pattern can change engine (§9).

### 5.5 Against ARTREV's count

ARTREV counted 1 bench / 2 corpus. All three of its patterns are in §5.2's
list. The three new ones are outside ARTREV's reader grammar or its arm
definition (A0's lookaround-born gates, a multi-character body). The two
counts share no code and agree on the overlap. At build the count is
re-taken a third way, independently (§8.6).

## 6. The give-up surface — NOT one-way `[r2 B-M3, C-S*]`

The STEPS and FRAMES give-ups can only disappear. A WORK give-up can
appear. This is a property of possessification in general.
`docs/spec/tuning.md` §2.1 and `limits.md` §7 already say so: lane
`possside` landed those paragraphs on main, with the user-written possessive
spelling as the shipped witness.

**The two rev-1 pairs conflicted, and why.**

- The note measured 1,070 → 2,565 (no arms → arms).
- The spec measured 581 → 1,586 (denied → user-written `\b(\w++)\b\s++\1\b`).
- Both said "200 distinct words + `last last`, 1.5 KB", and neither
  generator was committed. A minimum work budget is a per-subject number,
  so the two pairs are not comparable and neither is reproducible.

**Re-measured on ONE committed subject.** The subject is
`rev2/wb_subject.py 200`: 809 bytes, sha1 `bc1608f6…`. The tool is
`rev2/minwb2.sh`, which bisects, takes `--engine=vm`, and FAILS LOUDLY on a
compile error or an unrecognised outcome. The table is `rev2/wb_runs.tsv`.

| build | minimum `--work-budget` |
|---|---|
| main, default | 394 |
| main, `-fno-possessify` | 394 |
| prototype, no arm | 394 |
| prototype, arm B only | 595 |
| prototype, arm A only | 998 |
| **prototype, arms A+B** | **1,199** |
| **main, user-written `\b(\w++)\b\s++\1\b`** | **1,199** |

At each minimum the answer is `match 800 809`. One below it gives up on
`work`. The arms' artifact needs exactly the budget the hand-possessified
spelling needs, because it is the same program. The ratio here is 3.04,
against 2.40 and 2.73 on the two uncommitted subjects.

**Spec (D80), for the build commit:**

- **`tuning.md` §2.1's measurement is re-pointed** to the committed subject
  and its numbers (394 / 1,199), citing `wb_subject.py`.
- **One arms-specific sentence is appended** to §2.1's paragraph:

  > The `-fno-poss-ctx-follow` / `-fno-poss-bref-first` arms (§2.x) widen
  > which loops this applies to: on the committed subject the doubled-word
  > pattern's minimum work budget is 394 with both arms denied and 1,199
  > with both on, the hand-possessified spelling's own number.

- `limits.md` §7's bullet stands as landed. Its parenthetical citation moves
  with §2.1's numbers.

## 7. Lenses

**Sibling of a family? Yes, three times.**

1. **The FIRST-byte family** (`decision_families_survey.md` §3.7). D148 Q4's
   "do not merge `first_of` with `start_set`" stands.
2. **The two sub-facts** `[r2 Q7]`. Both are built as **file-local statics
   in `possessify.c`, separately testable**. They are extracted to
   `src/facts/` only when a second reader arrives; otherwise they overlap
   [PATFACTS].
   - **`ctx_admits`** (revision 1's `pcrec_ctx_admits`): which next
     characters a gate admits, given `P`.
     - It gets an EXHAUSTIVE model check: all 16 truth tables × the 3
       non-empty `P` subsets × a set of `C`s, compared with a direct
       evaluation.
     - It must report "members beyond the reader's tier" (above 0xFF) so
       that a reader widens rather than truncates (§2.1).
   - **The capture fact**: number → every `A_CAP` with that number. It
     covers lookarounds and DEFINE, reuses K93's by-number machinery
     (`cc[]` is keyed by group number, and so is this), and walks EVERY
     `A_CAP`, not the call graph's first binding.
     `[r2.1 R-4]` Its VALUE, `CAP(g)` (§3.1), is computed once per group
     number and memoized; in progress means widen. Its state is the walk's
     (`Pss`), never a file static.
   - **The continuation summary** `[r2.1 R-4, found by this revision]`. A1's
     fold had the same quadratic shape as arm B's: it re-walked `Q`'s
     continuation for every quantifier.
     - Witness: `(?:a+|a+|…)(?:\b|)(?:\b|)…`, n = 6,400. The denied build
       takes 0.90 s and revision 2's prototype 64.85 s (§8.7).
     - The fix rests on one fact: WHICH items the continuation reaches at
       zero consumption does not depend on `Q`, because every `A_CTX` is
       non-nullable whatever `P` is.
     - So each continuation node carries, once, a summary: the bytes of every
       reached item that is not a `P`-dependent gate (an A0-narrowable
       lookahead folds in here), the reached `P`-dependent gates grouped by
       their set `C` with `S` precomputed for the three `P`s, and the end
       flags.
     - Per `Q`, only the groups are evaluated, at O(distinct gate sets ×
       |LAST|).
     - The prototype checks the summary against the plain fold at every
       verdict (`R4SUM-MISMATCH`, §8.7: 0 on the census).
3. **possessify's own per-kind switches** `[r2 B-FAM]`.
   - Today the file holds three per-`AKind` switches (`first_of`,
     `gk_build`, `pss_walk`), the `pss_verdict` ladder, the `CallCtx`
     join, and the survey consumer.
   - The arms add a fourth fold (A1's continuation) and two more arms.
     [POSS-CALL-COPY] and the tripwires would add more. That passes the
     ~3-member threshold.
   - **FILED as [POSS-CTX-TABLE]** (`../dev/plan.md`, under [OPTLOOP]
     candidates per D137, UNSCHEDULED). It is one context record
     `{follow, may_end, encl, left}` and one per-kind rows table indexed by
     kind, with a static count assertion so `-Wswitch`'s exhaustiveness
     alarm survives. A1's `P` is the `left` component.
   - `[r2.1 N1]` **The record also carries a READER field.** `first_of`
     answers two different questions, and N1 is what happens when one reader
     gets the other's answer:
     - **"the next character at a POSITION"**: the retreat-exit readers
       (rows 1-3, the survey, an inner quantifier's follow, the call-site
       joins). A gate constrains that character: A0 gives `S`, A1 gives
       `S(P)`, non-nullable (§2.1).
     - **"the first character of a TEXT"**: arm B's `CAP(g)`. A gate
       constrains nothing, because it is not in the text, and it is
       nullable.

     Each per-kind row answers per reader. Today only the zero-width kinds
     differ, and `TEXT_FIRST` (§3.1) is the reader-2 column. The
     record makes "which question is this" a field, not a second function a
     future reader might not know to call.
   - It is NOT built ahead of the arms. The arms build on today's shape
     with table-shaped primitives (`ctx_admits`, the capture fact, the
     continuation fold).
   - The unification follows as a zero-mover refactor, gated on
     per-pattern `possessify marked/total` plus emit_sweep identity. Its
     trigger is the next per-kind possessify edit after the arms.
   - It has a row in `decision_families_survey.md`.

**General mechanism, not special case.**

- Neither arm adds a ladder row or a `\b` case.
- A0 and A1 are one function `S(P)` with one parameter.
- A1's call-boundary rule is the same join K93 built, read at one more
  place.
- B is the existing `first_of` asked of the group bodies.

**First-match table.** The ladder in §0 is unchanged.

**Engine hat / applicability.**

- Possessify is VM-only, and its verdict also feeds the atomic discharge,
  which is ENGINE-SELECTING (§5.4).
- Under START-SET stage 3 the DFA rows stay moot.
- The arms are algorithmic (D119).

**G1 interaction** (round3_selection.md (c) item 6). 3b-5's reverse-inner G1
must read the PRE-possessify tree. The arms enlarge the set of
`u.rep.possessive` marks, and the build's reviewer checks that G1 reads no
`possessive` field.

## 8. Checks, sabotage, harness

### 8.1 `run_possdiff.sh`'s extension `[r2 B-B1, B-M5]`

Prototyped as `rev2/possdiff_exh.sh` + `rev2/subjects_exh.py`. Every rule
below has run.

1. **Subjects: EXHAUSTIVE, replacing the bespoke families.**
   - Every string of length ≤ 4 over a case-flip-closed alphabet.
   - The alphabet is the pattern's own literal characters, with escapes
     decoded and syntax excluded (group names, flag letters, reference and
     call spellings, counts).
   - Then one WORD representative and one NON-WORD (`a` when the pattern
     has no word literal, and a second word letter when it uses `\w`; the
     space), plus `7` for a digit class.
   - Under `-e utf8`, U+00E9 and U+212A are added, and strings are built
     over CODE POINTS and then encoded.
   - This is eqcheck.py's generator shape, the one that found every
     refutation. The bespoke generator deleted `.` and never produced
     `aAA`.
2. **REACH per (pattern, witness subject).** `subjects_exh.py --reach S P
   [flags]` exits 0 iff `S` is in `P`'s sweep. It is wired as each sabotage
   row's `SAB_REACH_POP`, and the prototype runs `pd_reach.tsv`'s 11 pairs
   before compiling anything. **11/11 reached.**
3. **`# flags:` beside `# features:`.**
   - `-e utf8`, `--ucp` and `-i` apply to both sides. K93 already added
     the per-file `# features:` header, and this generalizes it.
   - **No TAB column**: ` \w?\b` begins with a space, so a column would be
     ambiguous.
   - `--corpus` compiles each derived pattern with its own encoding and
     flags, read from `--list-source` like the census does, never bare.
4. **The floor is a NAMED MANIFEST, not "population ≥ 1".**
   - The manifest is §8.2's witness set plus §5.2's six default-route
     movers, by pattern.
   - Per-arm firing is read from `--emit-ir`'s marked counts, armed against
     each deny bit, and from the per-arm stamp (§8.5).
   - CLAIM-vs-MARK's own counts (§8.3) are the population floor of record.
5. **Every sabotage row's `SAB_SUITES` includes `harness`**, with
   `SAB_HARNESS_TARGET=tests/possessify/possessify.rxt` (S586's precedent),
   so the oracle-side .rxt cells are a detector independent of possdiff.

The prototype's population is `rev2/pd_arms.txt`, `pd_utf8.txt`,
`pd_utf8i.txt`, `pd_ucp.txt` and `pd_i.txt`, 79 patterns in all:

- revision 1's designed family and sabotage witnesses;
- the rev-2 rows: mixed LAST, the A-F1 witnesses, arm × call, depth-1,
  lazy, A0 lookaheads;
- utf8, utf8 + `-i`, `--ucp` and `-i` files.

**Arms as designed: 79 agree, 0 diverge, 48 with a possessive mark, 403,943
cells, reach 11/11.**

### 8.2 Sabotage rows — every plant run `[r2 B-B1, A-F1, B-B3, C-S*]`

S-ids are taken AT BUILD, by grep. At this writing S560-S565 are free, S566
is taken (memfn), and the highest on main is S588 (k93fix). The rows are
named here by their plant. All were run on the exhaustive possdiff
(`rev2/possdiff_plants.sh`; verdicts in `rev2/pdx_verdicts.txt`, logs in
`rev2/pdx/`) and on CLAIM-vs-MARK (§8.3).

| row | plant (prototype switch) | witness (10.46-confirmed) | possdiff (exhaustive) | CLAIM-vs-MARK rows newly mismatched |
|---|---|---|---|---|
| A-m0 | A1 drops `m ≥ 1` (`PROTO_SAB_M0`) | ` \w?\b` on ` aa` | DETECTED, 2 patterns | 2,345 |
| A-firstpol | A1 reads polarity from FIRST (`PROTO_SAB_FIRSTPOL`) | `(?:a\.)+\b` on `a.a.` | DETECTED, 3 | 1,197 |
| A-mixed | A1 collapses a mixed LAST (`PROTO_SAB_MIXED`) | `(?:a[a.])+\b` on `a.a.` | DETECTED, 1 | 432 |
| B-nofold | B ignores `u.bref.caseless` (`PROTO_SAB_NOFOLD`) | `(a)A+(?i:\1)` on `aAA` | DETECTED, 1 (revision 1's harness MISSED it) | 1 |
| B-firstmem | B reads only `refs[0]` (`PROTO_SAB_FIRSTMEM`) | `(?J)(?:(?<n>a)\|(?<n>x))x+\k<n>` on `xxx` | DETECTED, 2 | 2 |
| B-nonnull | B forces `nullable(\n) = false` (`PROTO_SAB_NONNULL`) | `(a?)x+\1x` on `xx` | DETECTED, 2 | 33 |
| A-cc (A-F1) | A1 drops the call-site join (`PROTO_A1_NOCC`) | `(a+(?:\b\|))\|b(?1)a` on `baa` | DETECTED, 3 (both A-F1 witnesses and `(a?)(x+\1)b(?2)x`) | 3 (the C rows); and the corpus: 16 `k93.rxt` patterns newly marked |
| B-depth (termination) | B's depth guard dropped (`PROTO_SAB_NORECGUARD`) | `(a\2)(b\1)x+\1`: compiles | DETECTED: the compiler SEGVs (stack exhaustion) on all 3 cyclic-reference patterns | — |
| A-lazy (control, not a row) | A1 admits lazy loops (`PROTO_SAB_LAZY`) | — | NOT detected: 79 agree, 0 diverge, consistent with §8.4 | 892 newly marked, 0 diverging on the oracle (§8.4) |
| **A-lazy `[r2.1 N2]`, now a ROW (S568 at this writing, next free on main after S566)** | `PROTO_SAB_LAZY` | `(\w+?(?:\b\|))` on `ab` (10.46 (0,1)) | **DETECTED, 5 patterns** (rev 2.1 population, 104 patterns) | 3 hand rows |
| **B-textpos `[r2.1 N1]` (S567 at this writing)** | arm B reads `first_of`, the POSITION answer (`PROTO_SAB_TEXTPOS`) | `(?:((?=a))a)?b+\1b` on `abb` (10.46 (0,3)) | **DETECTED, 4 patterns** | 3 hand rows |

Rev 2.1 re-ran every plant on the extended population (Linux,
`rev21/results/out2/pdx_verdicts.txt`). The arms: 104 agree, 0 diverge,
517,382 cells, reach 15/15. Every plant is DETECTED. NORECGUARD is detected
as 3 compile refusals (crash), and the route-flip witnesses agree.

**[MECH-REACH] notes:**

- **Each witness is in the swept population.** The rows go into
  `tests/possessify/patterns.txt` / `calls.txt` under the new headers, and
  in as oracle-verified `.rxt` cells in `tests/possessify/possessify.rxt`.
  The A-F1 witnesses also go into `tests/recursion/k93.rxt` beside K93's own
  cells. The REACH check (§8.1 item 2) is each row's `SAB_REACH_POP`.
- **The A-F3 widening has no reachable witness** (§2.1). It is a stated
  invariant with a unit cell in the `ctx_admits` model check (§7), not a
  sabotage row.
- **The A-lazy switch is a control.** It shows the greedy-only conjunct is
  not load-bearing (§8.4). If the build keeps the conjunct, no sabotage row
  can be written for it; that is §8.4's point.

### 8.3 CLAIM-vs-MARK — a BUILD PRECONDITION `[r2 B-B2]`

`rev2/r2_claimmark.py`, over `gen_a2.py` + `gen_b2.py`, keeps:

- every claimed row;
- every ablation-tagged row (the near-misses, the most discriminating);
- a 1-in-10 hash-stratified sample of the rest.

Each greedy pattern is compiled with `--engine=vm --emit-ir` under no arm
and under the arms. MARK means "the arms raised `possessify marked`". Every
family row has exactly one quantifier an arm can reach. EXPECTATION is
`claim && !hi`, where `hi` means FIRST(X) has a code point above 0xFF, which
pcrec declines by representation (§2.1). The check is subject-free and
deterministic. It reads no pcrec code on the expectation side.

- **Result: 12,380 rows selected, 10,315 compared, **0 mismatches**. Mark equals expectation on every compared row: 3,079 expected marks and 7,236 expected declines. 126 of the claims fall in the `hi` class and pcrec declines them by representation, as expected.**
- **Refused: 2,065 rows. Every selected `utf,ucp` row is refused (2,059), because UCP `\w` under utf8 is refused today (§2.5). The two branch-reset rows and the two `(*ACCEPT)` rows belong to unbuilt modules. The two `match_unset_backref` rows have no pcrec spelling.**
- **It found two predicate gaps before it agreed**, both in the
  independent predicate (§2.4):
  - revision 1's generator did not model `\B` as a gate;
  - it widened a `\b` reached through an empty-able reference.

  It also found two hand claims, `(?:x+\1|(a))+` and `(?:(a)|x+\1)+`,
  WIDER than the rule: ENCL's ungated union (§2.3). That is sound either
  way, and they are now tagged `encl`. A check that agreed on the first run
  would have hidden all three.
- **Every plant is detected without subject luck** (§8.2's last column).

At build the check runs against the BUILT compiler, its deny bits replacing
the prototype's switches. It is a precondition: mark = expectation on every
compared row.

#### 8.3a Rev 2.1: per-quantifier marks, the UCP pin, and the FREEZE `[r2.1 R-7, R-3(b)]`

**(R-7) The mark is read per quantifier.** Revision 2 read MARK as "the
arms raised `possessify marked`", a count delta. A gained mark and a lost one
would cancel. `rev21/r21_claimmark.py` reads `--emit-ir`'s `strategies`
section instead: one row per emitted quantifier, in emission order.

- Rows are keyed by ORDINAL, because labels renumber when a program moves.
  A row count that differs between two compiles of one pattern is an
  ANOMALY, never a mark.
- The TARGET quantifier is found WITHOUT the arms. The generator's
  possessive spelling, compiled on the base build, differs from the greedy
  spelling at exactly one ordinal. A row where it does not (`unresolved`)
  falls back to "some quantifier flipped", and those rows are counted.
- MARK = the arms flipped the TARGET backtracking → possessive. A flip
  elsewhere is counted as `extra`. It is sound, but it is a claim the
  predicate did not make, so it is reported. Any other change is an
  `anomaly`.

**(R-7) The `utf,ucp` REFUSED population is pinned.** Every selected
`utf,ucp` row is refused today, because UCP `\w` under `-e utf8` is refused
until the kit-sized route lands (§2.5).

- The check takes `UCP_PIN` and exits 3 when the refused count moves. The
  count is 4,502 rows over the rev-2.1 population (`UCP_PIN=4502`); rev 2's 2,059 was
  over rev 2's.
- That is the trigger to re-sweep those rows. It is named in [UCP]'s and
  [CLS-TREE]'s plan rows.

**(R-3(b)) THE PREDICATE IS FROZEN.** Revision 2's predicate was edited
after the prototype's marks were seen (the `\B` and empty-reference gaps,
§8.3). So for the prototype, "the implementation equals the rule" was
partly circular. From this revision the predicate is pinned:

| file | sha1 at the freeze (commit `63be190c`) |
|---|---|
| `rev21/gen_a21.py` | `3bf0fdc0b1476d75492152fbb56ff542a46caa90` |
| `rev21/gen_a021.py` | `3c5fdf65d98ef0177da4eb3d4b2b844bb9473b68` |
| `rev21/gen_b21.py` | `9f9e7d92aa32f657c6f7a0ce3bf6b816a844eef8` |
| `rev21/r21_claimmark.py` (the comparison, not the rule) | `c5cf3dfc4fab40c11a9b57b91cbac49e223571fe` |

- **The post-freeze edit rule.** An edit to a predicate generator after the
  freeze is a RULE-LEVEL event, never a fix-up. It is made only in a
  revision of this note, and it carries:
  1. the trigger rows: the mismatching rows that prompted it, quoted;
  2. a libpcre2 oracle sweep of every row whose CLAIM the edit moves
     (`eqcheck.py`, ML ≥ 4), recorded before the edit is accepted;
  3. the new sha1s, entered in this table.

  The build's CLAIM-vs-MARK runs the generators at their pinned sha1s. A
  disagreement is a defect in the BUILD until a rule-level edit says
  otherwise.
- **Hand-literal rows are reported apart from computed ones.** Column 9 of
  every generator is `src`, either `computed` (the cross product's
  predicate) or `hand` (a literal claim written per row: the witnesses,
  `encl`, the `C`/`H`/`N` rows). Every summary line is split by it. A hand
  row's claim is the author's reading, not the rule's output. It counts as
  evidence of the rule only through its own oracle sweep.

**Result on the frozen-then-edited predicate** (Linux, rev-2.1 prototype,
`results/out2/claimmark.out`), split by source:

| config | src | compared | mark ≠ expect | unsound-direction | extra flips | anomalies |
|---|---|---|---|---|---|---|
| AB | computed | 33,037 | **5** | 5 | 657 | 0 |
| AB | hand | 44 | **0** | 0 | 2 | 0 |

- The 5 are the rows with unresolved targets (below).
- 3,459 computed targets are unresolved, and 2,160 are base-marked.
- utf,ucp REFUSED: 4,502.
- Every plant moves mismatches on the hand rows (`textpos` 3, `lazy` 3,
  `nonnull` 4, …).

**The first run against the freeze disagreed on 2,815 rows. Here is what
each category was.** These are POST-FREEZE EDITS 1 and 2. Both are
rule-level, and their trigger rows are in the generators' comments.

1. **2,047 exact-count rows (A0 family).** These are NOT an arm. The
   SHIPPED possessify already marks them (row 1, exact count) on the base
   build with the arms denied. So the possessive spelling moves nothing, and
   "flip" reads 0. The fix is to the COMPARISON (`r21_claimmark.py`): MARK is
   the target's state when the base build already marks it. That case is now
   counted as `base-marked` (2,160 after the extension), and those rows agree.
   The predicate is unchanged.
2. **745 R-block rows (arm A family), `hi` bookkeeping.**
   - 520 move FEWER: pcrec declines by representation (a caseless-utf `k`
     tail, or `\w` folded at parse time to U+212A/U+017F). The expectation
     is narrowed.
   - 225 move MORE: `hi` had been set on rows whose follow is EMPTY, where
     pcrec's widening cannot decline. These are backed by the libpcre2 10.46
     sweep over exactly those 225 trigger rows: **225/225 agree, 0 diverging,
     2,522,475 subjects**.
3. **18 A0 rows: LAST is read from the POSITION class.** This is a
   semantics statement, and it is the rule as §2.3 writes it: the polarities
   of the classes at X's Glushkov LAST positions. A gate inside the body is
   not a position, so the LAST of `(?:(?=[ab])\w)` is `\w`. The edit
   narrows claims (FEWER). The oracle sweep over the 18: 18/18 agree on
   10.46 (134,658 subjects). The wider claims were sound too. pcrec simply
   implements the stated, narrower rule.
4. **5 unresolved targets** (`(?:[a-z]+(?:(?=\W)[ab])+y)+` and four
   siblings). These are not model error.
   - The target body is emitted twice (two strategies rows), so the
     possessive spelling flips two ordinals and the target is unresolved.
   - The arms then mark a DIFFERENT quantifier, `(?:(?=C)[ab])+`. Its body
     can never match, so A0's `S` makes it trivially disjoint.
   - That is a claim the predicate never made. It and all 657 other extra
     flips are checked by the exhaustive possdiff over every extra-mark
     pattern (`mk_pd_extra.py`): **676 patterns, 0 diverging, 7.57 M cells**
     (`results/out2/pdxe/extra_tallies.txt`).
   - They stay listed as OPEN in the target-resolution sense. The instrument
     should key replicated copies as one target.

**Edit 2** (after the oracle sweep): the frozen arm-A R block omitted
`fold_ref` and CLAIMED 14 rows that 10.46 refutes. pcrec DECLINED all 14.
The edit narrows 48 claims (FEWER). Final sha1s: `gen_a21.py`
`2fec0c24…`, `gen_a021.py` `5bb09dfb…`, `gen_b21.py` unchanged,
`r21_claimmark.py` `d2288d1a…`.

### 8.4 The ablation table `[r2 B-B3]` (revision 2's; superseded by §8.4a)

Per conjunct dropped from the PYTHON predicate: the rows it newly claims,
and how many of those diverge on libpcre2 at ML ≥ 4 (arm A: every string of
length ≤ 4 plus 100 random; arm B: ≤ 5 plus 300).

| arm | conjunct dropped | newly claimed | of those, diverging | first witness |
|---|---|---|---|---|
| A1 | `m ≥ 1` | 2,268 | **996** | `\w*\b\w` on `a` |
| A1 | polarity from LAST (read FIRST) | 1,314 | **338** | `(?:a\.)+\b` on `a.a.` |
| A1 | a mixed LAST declines (collapse it) | 504 | **168** | `(?:a[a.])+\b` on `a.a.` |
| A1 | ENCL unioned (drop it) | 2,272 | **3** | `(?:a+(?:\b\|)\|ab)+c` on `aabc` |
| A1 | the call-site join (A-F1; lexical only) | 4 | **4** | `(a+(?:\b\|))\|b(?1)a` on `baa` |
| A1 | greedy only (admit lazy) | 1,134 | ~~**0**~~ REFUTED (§8.4a: 477 of 3,964 once the family has a nullable follow) | — |
| B | fold at a caseless reference | 2 | **2** | `(a)A+(?i:\1)` on `aAA` |
| B | union over every `refs[]` member | 2 | **2** | `(?:(?<n>a)\|(?<n>x))x+\k<n>` on `xxx` |
| B | union over every `A_CAP` with the number | 1 | **1** | `(?\|(a)\|(x))x+\1` on `xxx` |
| B | nullability from the member bodies | 12 | **12** | `(a?)x+\1x` on `xx` |
| B | `(*ACCEPT)` makes a group nullable (future `verbs`) | 1 | **1** | `(?=((*ACCEPT)a))x+\1x` on `xx` |
| B | unset reads as empty (future `MATCH_UNSET_BACKREF`) | 1 | **1** | `(?:(a)\|b)x+\1x` on `bxx` |

**Every conjunct but one diverges.**

- **ENCL**'s control needed new rows. The family's 2,268 wrapped rows put
  the gate at the HEAD of the in-body continuation, so a restart happens
  only behind it, and dropping ENCL loses nothing there (0 of 2,268). A
  gate with an empty BYPASS reaches the loop's end, and the restart then
  rescues the match. Three of the four `H` rows in `gen_a2.py` diverge.
- ~~**Greedy-only does not diverge, on 1,134 rows.** This is the measurement
  behind §2.3's "declared-conservative" and RC-Q1. It is also why no
  sabotage row can be written for that conjunct.~~ `[r2.1 N2]` REFUTED: the
  population had no nullable follow. See §8.4a: 477 of 3,964 diverge.
- **Not conjuncts, so not in the table:**
  - zero consumption, which is structural (§2.3);
  - B's depth-1, a termination rule (§3.1): resolving deeper is sound,
    `(a)(\1b)x+\2` 0 diverging; its plant hangs the compiler;
  - §2.1's empty-S widening, which has no reachable witness.

Arm A is swept at ML=4 (881-11,211 subjects per row), arm B at ML=5 (9,631).
The data is in `rev2/a2_abl_ml4.out.gz`, `rev2/a2_new_ml4.out` and
`rev2/b2_ml5.out`.

#### 8.4a The ablation table, re-measured on the rev-2.1 families `[r2.1 N2, N1]`

The same instrument (`eqcheck.py`), but run on **libpcre2 10.46** (ubuntubudu,
whose `pcre2test` is the reference). Arm A families use ML=4 with 100
random subjects; arm B uses ML=5 with 300. The populations are the extended
`rev21` generators (§8.3a). Every claimed, tagged or hand row is swept:
22,581 + 8,535 + 2,330 rows. The data is in `rev21/results/eq_*.out`.

| arm | conjunct dropped | newly claimed | of those, diverging | first witness |
|---|---|---|---|---|
| A1 | `m ≥ 1` | 2,640 | **996** | `\w*\b\w` on `a` |
| A1 | polarity from LAST (read FIRST) | 1,485 | **338** | `(?:a\.)+\b` on `a.a.` |
| A1 | a mixed LAST declines (collapse it) | 567 | **168** | `(?:a[a.])+\b` on `a.a.` |
| A1 | ENCL unioned (drop it) | 2,644 | **36** | `(?:\w+(?:\b\|)x)+` on `ax` |
| A1 | **greedy only (admit lazy, row 2's may_end bypassed)** | 3,964 (+80 in B's family) | **477** (+26) | `\w+?(?:\b\|)` on `aa`; critic R's `(\w+?(?:\b\|))` on `ab` |
| A1 | the call-site join (A-F1; lexical only) | 4 | **4** | `(a+(?:\b\|))\|b(?1)a` on `baa` |
| B | **TEXT_FIRST (read a captured text with `first_of`'s POSITION answer)** | 303 (B) + 903 (A0's R block) | **86** + **6** | `((?!x)) x+\1x` on ` xx`; `(?:((?=[ab]))a)?\d+?\1` on `a11`; N1's three |
| B | fold at a caseless reference | 2 | **2** | `(?i:(a))A+\1` on `AAA` |
| B | union over every `refs[]` member | 2 | **2** | `(?:(?<n>a)\|(?<n>x))x+\k<n>` on `xxx` |
| B | union over every `A_CAP` with the number | 1 | **1** | `(?\|(a)\|(x))x+\1` on `xxx` |
| B | nullability from the member bodies | 180 | **78** | `(a?) x{1,3}\1x` on ` xx` |
| B | `(*ACCEPT)` makes a group nullable (future `verbs`) | 1 | **1** | `(?=((*ACCEPT)a))x+\1x` on `xx` |
| B | unset reads as empty (future `MATCH_UNSET_BACKREF`) | 1 | **1** | `(?:(a)\|b)x+\1x` on `bxx` |

**Every conjunct diverges, greedy-only included.** Revision 2's "0 of
1,134" was a population with no nullable follow. The rows that diverge
are the bypass follows rev 2.1 added. The same lazy rows WITHOUT a bypass still
agree, which is §2.3's argument: a continuation that must read a character
cannot succeed at a retreat exit.

**The claims themselves** (the full predicate, after the two rule-level
edits of §8.3a):

- arm A: 11,800 claimed, **0 diverging**;
- A0: 7,614 claimed, **0 diverging**;
- arm B: 1,905 claimed, **0 diverging**.

Edit 2 is the record of the one place this did not hold at the freeze. The
frozen arm-A R block omitted `fold_ref` and claimed 14 rows that 10.46
refutes, for example `(\b\w)\W+\1` under `utf,i` on `k \x{212a}`. That was
a PREDICATE defect: pcrec declined all 14. Edit 2 narrows 48 claims, 14 of
them refuted and 34 sound.

### 8.5 Per-arm stamp and the identity gate `[r2 B-M2]`

- **`<PREFIX>_VM_POSS_ARMS`**, a bitmask stamp, is part of the abi event.
  - Bit 0 is set when A0 contributed to some positive verdict, bit 1 for
    A1, bit 2 for B.
  - It is emitted on every VM-route artifact, `0` when no arm fired.
  - D46/D47.3's do-or-die is asserted against it: a denied arm's bit is 0,
    on the ARTIFACT.
  - `RX_VM_STRATS`' POSSESSIVE bit cannot serve, since it does not flip per
    arm.
- **`run_recursion_identity.sh` (A) gains a `poss-arms-moved` bucket.** An
  artifact whose program region moved is excused iff it stamps a nonzero
  `VM_POSS_ARMS` AND compiling it with both arm bits denied restores the
  pinned program. The bucket has the stamp-or-deny shape `-fno-lit-run`'s
  bucket uses. Its non-vacuity arm is a named manifest (§5.2's corpus
  movers), not "≥ 1".
- **Mover validation:** `scripts/emit_sweep.py --ref <pre-change main>`. The
  movers must equal the manifest, by id, with 0 off-diagonal.

### 8.6 Give-up check and the independent re-count `[r2 B-M3, B-M4]`

- **The K65-style check REUSES `tests/axes/run_axes.sh`'s classifier**: its
  GIVEUP1 classification (`dump_diff.awk`) and the `GIVEUP1_ALLOWANCE`
  manifest, keyed for the two new axes. Revision 1's §8.3 duplicated it.
  - A GIVEUP(code1) → GIVEUP(code2) transition is classified as a FOURTH
    class, beside SAME / ANSWER→GIVEUP / GIVEUP→ANSWER.
  - `doubled-word`'s STEPS→WORK move is that class.
- **`possdiff_driver.c`'s `describe()` reads `tests/harness/outcome_word.h`**
  (the shared give-up word table, landed with axtri). It printed
  `PCREC_ERR_WORK` as "nomatch".
- **The K35 re-count at build is INDEPENDENT of the prototype.** It uses
  `start_table`'s three-method shape:
  - the built compiler's `--emit-ir` marked counts, armed against each deny
    bit (the deny-delta census);
  - the `VM_POSS_ARMS` stamp census;
  - the sabotage anchors' owners.

  It is diffed against `census_r2.tsv.gz`. Any difference is explained or
  is a defect.

### 8.7 Three more build-bar items `[r2.1 R-4, R-5, R-6]`

**(R-5) A1's continuation equals the walk's FOLLOW, as a build-time
assertion.** A1 recomputes `Q`'s continuation beside `pss_walk`'s FOLLOW: it
is a second computation of the same set, and the two can drift. With every
gate valued A0, they must agree:

    A1cont_A0(Q) ∪ ENCL  ==  FOLLOW(Q) ∪ ENCL      (bytes)
    A1cont_A0(Q).ends    ==  may_end(Q)            (the match can end)

- `ends` is "the continuation reaches the match end at zero consumption":
  lexically, or through a crossed call site's joined `may_end`.
- The build checks this ALWAYS, at every `pss_verdict`, in the house form:
  a disagreement is `pcrec_ctx_fail(..., "internal error: possessify: A1
  continuation disagrees with FOLLOW")`, like `cc_join`'s missing-slot
  check. Every compile `make test` runs is therefore a check. It must read
  the continuation SUMMARY (§7) valued A0, which costs O(gate groups) per
  quantifier. Re-running the plain fold per quantifier would bring R-4's
  quadratic back. The summary-equals-fold agreement (`R4SUM`) is the
  test-time half: a unit cell plus the census population. The deny bit does
  not vacate the check, because the summary is built whether or not A1 is
  consulted.
- It found one disagreement before it agreed. Inside an ATOMIC body,
  `pss_walk` analyses the body as a self-contained pattern (follow empty,
  may end), but A1's continuation ran on to the root and unioned `(?R)`'s
  join. That is conservative, so it was not a miscompile, but it was a second
  definition. The continuation now carries an explicit atomic-body END
  (`px_atomic_end`), the walk's own boundary.
- Measured over the census population (4,132 patterns, rev-2.1 prototype, Linux): **5,437 verdicts, all `bytes-eq/end-eq`; 0 R4SUM mismatches** (`rev21/results/out2/census_r21.tsv`). The census itself is unchanged from rev 2: arms fire 6 bench / 13 corpus, 0 default-engine flips, and the rev 2 → 2.1 mark delta is 0, because no corpus pattern has N1's shape. That is why N1 was missed.

**(R-6) The backreference-stays-VM tripwire.** Arm B's bit is classified
masked, answer-identity-preserving (§9), because every `A_BREF` is
`VM_ONLY` in `select_engine.c`, under `--no-captures` too. That premise has
a chartered threat: the finite-language expansion (`(abc)\1` → `abcabc`,
[M6.5]'s follow-up (d)/(f), whose only customer is `--no-captures`) would
make a backreference DFA-runnable.

- The build adds `reject_engine_dfa_bref_nocaptures` to
  `tests/reject/run_reject_tests.sh`, beside `reject_engine_dfa_vars`.
- It runs `--engine=dfa --no-captures --features all '(a)x+\1'` and requires
  exit 1 with "requires the VM engine, which --engine=dfa excludes".
- Its failure message names this note's §9 and says: "arm B's deny bit
  `-fno-poss-bref-first` is classified masked because a backreference is
  VM-only; if this pattern now compiles for the DFA, reclassify the bit as
  ENGINE-SELECTING (kept) and add a route-flip census for arm B".
- Today: refused, armed and denied (`rev21` prototype, verified).

**(R-4) A compile-time witness at the size boundary.** Both arms' folds were
quadratic in revision 2. Arm B walked the whole tree per reference, and A1
re-walked the continuation per quantifier. Both are now linear, as below.
The pass runs before the emitted-size caps refuse a pattern, so the caps do
not bound it; every row below is refused for size (rc 1) after the pass ran.
Wall seconds for `pcrec --engine=vm -o file`, the Mac under a concurrent
suite (load 9-16), so they are coarse:

| witness (n) | denied | rev 2 arms | rev 2.1, memos off | rev 2.1 |
|---|---|---|---|---|
| `Bsame` (`(a)` + n × `x+\1`), 12,800 | 7.40 | 40.94 | 7.35 | 7.19 |
| `Bdist` (n groups, `\g{N}`), 6,400 | 3.38 | 16.53 | 3.19 | 3.38 |
| `Bcycle` (n-group reference cycle), 6,400 | 0.62 | 4.29 | 41.17 | 0.60 |
| `A1alt` (n `a+` branches, n `(?:\b\|)`), 6,400 | 1.35 | 100.15 | 91.28 | 1.36 |
| `A1alt`, 12,800 | 11.37 | 410.20 | OWED | OWED |

These are Linux (ubuntubudu) wall seconds. `rev21/timing_r4.sh` writes the
table (`results/out2/timing.out`). It was stopped at the manager's wrap-up,
so the `A1alt` 12,800 rev 2.1 columns and the `A1lb` (distinct lookbehind
classes) family are OWED. Rows ≥ 128 KiB of pattern are skipped, because
that is Linux's argv cap. Reading the table:

- The INDEX alone fixes arm B's same-group and distinct-group shapes ("memos
  off" ≈ denied).
- The memo is what bounds the cycle shape.
- A1's continuation summary fixes the A1 shape.

The build bar carries two cells under `scripts/watchdog`: `Bsame` and
`A1alt` at n = 12,800. Each must compile (to the size refusal) within 2× the
denied build's own time on the same pattern. A regression to either
quadratic is 8-70× there, so the bar has headroom both ways.

### 8.8 The composition hook `[r2.1 R-3(a)]`

R-3(a) is a D27-blinded author's composition corpus (gate × capture × ref ×
lazy × bypass × call), oracle-verified on 10.46, written in a cell. This
lane did not read it. `rev21/run_composition.sh FILE.rxt` is its hook:

- It runs `tests/harness/run.sh` four times with the prototype: denied and
  armed, each on the default route and on `RXTFLAGS=--engine=vm`. The arms
  are VM-only, and a gate-only pattern routes to the DFA by default.
- It reports per route the cells that fail ARMED but pass DENIED (an arms
  divergence, exit 1), and lists the cells failing both sides, unattributed.
- It counts REACH: on how many distinct patterns the arms move `possessify
  marked`. Zero reach exits 3, because a corpus the arms never touch is not
  evidence.
- Smoke-tested on a scratch three-cell file: 0 divergences armed. With
  `PROTO_SAB_TEXTPOS=1`, it reports the N1 witness as a divergence on both
  routes.

Rev 2.1 closes when that run is green against the rev-2.1 prototype (the
re-check's ruling): no divergence, and nonzero reach.

## 9. abi, flags, spec, docs — what the build commit carries

**abi event: YES.** The number is taken at build, by grep (D94). It is 65 at
this writing. `[r2 C-S*]`

- **Precedent:** [OPT-VEDGE] and [OPT-REQRUN-ENC]. Each was an analysis
  relaxation that moved emitted program text on its movers.
- **What moves on a mover:**
  - the loop's emitted body;
  - `<PREFIX>_VM_STRATS`;
  - `rx_info`'s `frame_capacity` / trail VALUES;
  - `RX_VM_FRAMELESS` and the entry shape;
  - the new `<PREFIX>_VM_POSS_ARMS` stamp (§8.5), on every VM artifact;
  - on a route flip (§5.4, none measured), `RX_ENGINE` itself.
- **What does not move:** no struct offset and no `rx_info` member.
- **The site list is found BY GREP at build time** (D94; every reader of
  the number).

**Deny bits: two, one per arm. Arm A's is ENGINE-SELECTING and arm B's
is not** `[r2 C-1]`.

- **The bits:** `-fno-poss-ctx-follow` (A0 + A1) and `-fno-poss-bref-first`
  (B). Bit numbers are taken at build, from `lib/pcrec.h`.
- **ONE verdict** (D154's spirit). Each bit denies its arm in
  `pcrec_possessify` AND in `pcrec_poss_survey`.
- **`-fno-poss-ctx-follow` is ENGINE-SELECTING.**
  - Denying it can keep an atomic group or possessive suffix in the tree
    (`\w++\b`, `(?>\w+)\b`, `\d++(?![\d.])`, `[a-z]++(?=@)`). That moves
    `RX_ENGINE` to "vm", and makes `--engine=dfa` plus the denial REFUSE
    (`rev2/routeflip_witness.out`).
  - So it goes in `src/core/axes.def`'s ENGINE-SELECTING block, beside
    `-fno-atomic-discharge` / `-fno-splice-calls`. It is in the `kept` set
    of `emit_dfa.c`'s derived `rx_info.flags` mask, and tuning.md's "THE
    `rx_info.flags` RULE" names it among the kept engine-selecting denials.
  - [FLAGBITS] derives the mask from `axes.def`, so the only hand edit is
    `kept`.
  - The classification stands at zero measured flips (C-1 (2)).
- **`-fno-poss-bref-first` is NOT engine-selecting. This REFUTES the
  disposition's "the two deny bits are ENGINE-SELECTING" for arm B.**
  - Arm B only reaches a pattern that contains a backreference.
  - A backreference needs a capture group. A capture-bearing pattern is
    VM-routed by default (D44.6), and a backreference forces the VM even
    under `--no-captures`.
  - So B can change the program and the atomic discharge, but never
    `RX_ENGINE`, and `--engine=dfa` refuses both with and without it.
  - Measured on the prototype: `(a)x++\1` and `(a)(?>x+)\1` stay `vm`
    armed and denied, with and without `--no-captures`.
  - So it is ANSWER-IDENTITY-preserving, like `-fno-possessify`, masked by
    [FLAGBITS]'s default polarity, and listed in the rung-ladder block.
  - **If the re-check critic prefers symmetry** (both kept), the cost is one
    bit of reflection surface that can never differ in effect. The
    recommendation is the asymmetric, measured classification. It becomes
    engine-selecting only if a future engine can run backreferences.
- **The `--engine=dfa` refusal witness** for A's bit: `\w++\b` refuses
  denied and compiles armed. B has no such witness, which is the point.

**Spec (D80), the arms-specific sentences only** `[r2 C-S*]` (possside landed
the general paragraphs):

- `tuning.md` §2.1: §6's re-pointed measurement and its one sentence.
- **`tuning.md` §2.8 (`-fno-atomic-discharge`), appended:**

  > The discharge asks the possessify verdict, so the possessify arms
  > (§2.x, §2.y) widen what it discharges: `\w++\b` is discharged and
  > DFA-routed by default. Denying the context-gate arm
  > (`-fno-poss-ctx-follow`) keeps such a group on the VM.

- **The two new `tuning.md` §2.x entries.** Each names:
  - its arm;
  - its classification: `-fno-poss-ctx-follow` ENGINE-SELECTING and kept,
    with the `--engine=dfa` refusal sentence; `-fno-poss-bref-first`
    answer-identity-preserving and masked, with the one-line reason (a
    backreference is VM-routed);
  - the `VM_POSS_ARMS` bit it clears;
  - its witness.
- `match_api.md` §6's abi change-log paragraph, plus the `VM_POSS_ARMS`
  stamp's entry in the stamp table.
- `eng_brep_design.md` §2.5 (the assertion rule) gains a pointer here: "an
  assertion in the follow widens FOLLOW to all bytes" stops being true for
  `A_CTX`.

**Docs:** `src/opt/CLAUDE.md`'s possessify entry; the `possessify.c`
header's conjunct list (each new conjunct with its witness);
`tests/possessify/CLAUDE.md` (the `# flags:` header, the exhaustive
generator, REACH).

**Cost: M** (revision 1: S). The arm code is S-M. The rest is the checks the
panel required: the exhaustive possdiff, CLAIM-vs-MARK, the stamp and its
bucket, the engine-selecting classification with its witnesses, and the
tripwire.

## 10. The three standing questions

1. **Measurement regime. RELEVANT, narrowly.**
   - This lane measured no timing.
   - The −57.6% is ARTREV's: ubuntubudu x86, gcc, 7/7 pads, throughput
     regime.
   - The census, the sweeps, CLAIM-vs-MARK and the work-budget minimums are
     DETERMINISTIC COUNTS, independent of box and load.
   - They depend on the subject (the §6 minimums are per-subject, which is
     why the subject is now committed) and on the compiler revision (the
     census is at `c2a0c6df` plus the prototype).
   - A latency regime could not flip the decision. The WORK-budget
     direction is the one regime-like dependence, and §6 states it.
2. **Independent control. RELEVANT.**
   - **The soundness sweeps** check libpcre2 against libpcre2. The CLAIM
     comes from Python with membership asked of libpcre2.
   - **CLAIM-vs-MARK** checks pcrec against that Python claim. Its
     expectation side contains no pcrec code. It found three disagreements
     before it agreed (§8.3).
   - **possdiff** checks pcrec against pcrec-denied. It is the only check of
     the EMITTED code, and its subject population is now exhaustive and
     REACH-checked. The `.rxt` cells are the oracle-side complement.
   - **The census** is the prototype's. At build it is re-counted three
     independent ways (§8.6).
   - **Every plant was run and every one is detected.** Revision 1 ran two
     of six.
3. **What moves when data is regenerated. NOT RELEVANT as data.** No table,
   calibration or generated file is introduced. The emitted-byte movement
   is the abi event in §9. The census, the claim files and `wb_runs.tsv` are
   measurements, re-run rather than regenerated into anything.
   `wb_subject.py` is deterministic.

## 11. Questions — the panel's rulings, and what is left

Revision 1's questions as ruled (`../dev/reviews/2026-10-07-r-poss-arms-panel.md`):

- **Q1. §1 first?** Done: K93 landed as the join (§1).
- **Q2. Deny bits:** two, ENGINE-SELECTING (§9).
- **Q3. Ship A0?** YES, with A-F3's widening and B-M4's family sweep as
  preconditions. Both are discharged (§2.1, §5.3). A0's alpha cell is
  `email-local-nodup`; if no alpha is taken, the claim carries D149's
  "unmeasured" label.
- **~~Q4. `(?R)` against PCRE2's auto-possess.~~** STRUCK: D154 addendum 1,
  `(?R)` follows the sound answer; U18 = PCRE2Project/pcre2#1034.
- **Q5.** The seam's Latin-1 fold gap is K94 (lane `k94fix`). It is not a
  prerequisite (§3.3).
- **Q6. Tripwires:** B's form, one soundness tripwire (§3.3).
- **Q7. Shared primitives:** file-local statics, separately testable (§7).

**Open questions for the re-check critic:**

- `[r2.1 N2]` **RC-Q1 is ANSWERED: NO.** Critic R measured greedy-only as
  load-bearing, with witness `(\w+?(?:\b|))` on `ab`. A1 stays greedy-only.
  A sound lazy form would need a second row (§2.3), and it is not built.
  Revision 2's question follows, struck.
- ~~**RC-Q1. A1 for lazy loops?** The ablation measures greedy-only as not
  load-bearing: 1,134 newly claimed lazy rows, 0 diverging at ML=4; the lazy plant passes the exhaustive possdiff (79 agree). Revision 2 KEEPS the conjunct, declared
  conservative. Should it instead be dropped, so that A1 feeds row 3 for
  lazy loops under the existing row-2 conjunct? That would be a wider claim
  set with its own CLAIM-vs-MARK population.~~
- **RC-Q2. ENCL ungated** is load-bearing on bypass shapes (3 of 4 `H`
  rows diverge) and merely conservative where the gate heads the in-body
  continuation (2,268 rows, 0 diverging) (§2.3, §8.4). It stays ungated.
  Is a gated ENCL, unioned only where the continuation can reach the loop's
  end, worth a row?
- **RC-Q3. The P = {0,1} join** (§2.3a) gives up nothing measurable today.
  Does the critic accept "ill-defined plus zero measured gain" as the reason
  not to carry a per-P value?
- **RC-Q5. The deny-bit classification is asymmetric** (§9). A's bit is
  ENGINE-SELECTING and kept. B's is answer-identity-preserving and masked,
  because a backreference pattern is always VM-routed. This departs from
  the disposition's "both ENGINE-SELECTING". Does the critic accept the
  measured asymmetry?
- **RC-Q4. `-e utf8 --ucp`** is entirely refused today (§2.5). The arms'
  utf8+ucp behaviour is therefore unmeasurable until [CLS-TREE] S4 / [UCP]
  U3. Is "declines by representation, re-swept when the route lands" the
  right owed item?
