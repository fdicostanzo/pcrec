# Compacting DFA states as they are generated — a design study

Lane `dfamin`, worktree `worktrees/dfamin`, branch `lane/dfamin`, on `main`
at `03e632c0` (plan row [LIM-2] STUDY-1). **READ-ONLY study**: nothing under
`src/` or `tests/` is written by this lane, no `make` was run, no compile
and no benchmark. Every claim about pcrec's code is cited as `path:line`
and comes from reading that code in this worktree; every claim about the
literature carries a citation, and the ones I could not verify past an
abstract or a search snippet are marked **unverified**.

Chartered by Frank, 2026-09-04: *"1. as its cutting edge, a websearch on
the latest would be a good first step. 2. consider if an incremental
partial followed by a thorough pass at the end would be simpler (simplicity
is the key there — as this sounds like a crazy complex manoeuvre as-is).
3. a study would be a good first move to see if it can be done without
getting brittle — which would be my concern."*

The trigger is lane lim2's census finding
(`docs/dev/lanes/lim2_report.md` §10, read in `worktrees/lim2`): the
mechanism [LIM-2] built projects the emitted table's size from **raw**
subset construction, but the emitted artifact is the **minimized** table,
and the corpus holds a pattern where raw is 27× the minimized machine
(27,575 raw states → 1,010 minimized, a 97.06% shrink). A percentage
margin on raw bytes cannot bound emitted bytes across that population. The
question this study answers is whether the two quantities can be made to
track each other at the source — by compacting states as they are
generated.

**Disclosure (scope mandate).** My context was injected at spawn with the
session-root `CLAUDE.md` and the memory index. The parts that shaped
decisions here are the situation-index rows on D77 ("build under
measurement"), on general mechanisms rather than special cases, and on
scaffolding changes being an `abi` event; and the memory summaries for
`pcrec-check-design-lessons` and `pcrec-build-under-measurement`. Nothing
else outside this worktree's own files influenced the analysis.

---

## 1. The problem in pcrec's terms

### 1.1 What a state is

Not a set. `src/ir/dfa.c:1` states it: *"A DFA state is a priority-ordered
list of N_CLASS NFA states."* The list is `DView.list`, declared
`/* priority-ordered N_CLASS state ids (arena) */` at
`src/core/internal.h:1158`, and its order is leftmost-first preference
order, produced by an epsilon closure that walks split edges in preference
order (`src/ir/dfa.c:533` `clo_open`, `:571` `clo_walk`, `:771` `closure`).

A full state (`DState`, `src/core/internal.h:1163`) is more than one list:

| component | what it is | where |
|---|---|---|
| `up[UPC_N]` | the same pre-set closed once per class-axis context — plain / word / newline — each with its own `list`, `nlist` and `accept` bit | `internal.h:1157`, `:1192` |
| `eolvar` | an interned variant state, the `eol_ok` closure of the same pre-set; `-1` means "identical to this state" | `internal.h:1193` |
| `endvar` | an interned variant state, the `(eol_ok, end_ok)` closure; `-1` means "**identical to the EOL view**", not to this state | `internal.h:1207` |
| `tr[ncls]` | the transition row, one target per byte equivalence class | `internal.h:1208` |
| `scan_span` etc. | [OPT-5]'s scan edge, written after minimization | `internal.h:1234` |

Identity, and therefore interning, is over **all** of that:
`dhash` (`src/ir/dfa.c:809`) hashes every view's list, every view's accept
bit, `eolvar` and `endvar`; `intern` (`:871`) confirms a hit by comparing
`eolvar`, `endvar` and every view with `view_same` (`:849`), which is
`nlist` equality plus `memcmp` of the lists — an **ordered** comparison.
Two subsets holding the same NFA states in a different order are different
states here, by construction.

A new state's index is `d->n++` (`src/ir/dfa.c:994`), i.e. **creation
order**. That single fact is what makes section 1.4's byte-identity
question answerable at all.

### 1.2 Why distinct subsets are language-equivalent in the K18 shapes

`tests/base/k18_cost_gates.rxt`'s census witness is
`(1{0,30}?[^]abc][^abc]){28,30}0+|a` (lim2 report §10). Counted repetition
is lowered by **copying the body**: `src/ir/nfa.c:701` `A_REP` emits `rmin`
copies in sequence and then, for a finite `rmax`, a nested-optional tail
`(X(X(X)?)?)?` built copy by copy (`:744`-`:745`). Nesting a counted
repeat inside another multiplies the copies. So the NFA for the witness
carries many structurally identical copies of one body, distinguished only
by how many iterations remain.

Two things follow, and they are different things:

1. **The copies are not equivalent as NFA states.** A position in copy *i*
   has residual language `X^{≤ n-i}·tail`; copy *i+1*'s has
   `X^{≤ n-i-1}·tail`. They are ordered by inclusion, not equal.
2. **The subsets containing them very often are equivalent as DFA states.**
   A subset that has reached copies 4 through 30 and a subset that has
   reached copies 5 through 30 accept exactly the same continuations,
   because the union of the residuals is the same. This is the shape that
   collapses 27,575 raw states to 1,010: the *distinctions* raw construction
   draws are between counter configurations whose *unions* coincide.

That distinction is the whole difficulty. The equivalence is a property of
the **residual language of the subset**, which is a fact about the future.
Raw construction discovers it only after the future has been built — which
is exactly what `src/opt/minimize.c` then does, and exactly why the
mechanism the charter asks about is hard.

The second family in the same file — `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` and its
relatives, cited in the brief — is the same mechanism with nullable bodies
and the K18 open-loop context (`src/ir/dfa.c:207`) multiplying the
distinctions further: the memo is keyed on `(state, open-loop context)`
(`:329` `lctx_find`, `:392` `pmemo_add`), so paths that differ only in
which loops are open on them produce different closures, hence different
subsets, hence different raw states — many of which minimize back together.

### 1.3 What "compacted as generated" must preserve

Three obligations, in decreasing order of how obviously they must hold and
increasing order of how easy they are to violate silently.

**(a) The language, and the span.** The DFA route answers spans only —
a pattern with live captures is routed to the VM by `select_engine.c`'s
`forces_captures` (recorded in `tests/base/k18_cost_gates.rxt`'s own
header). The forward machine finds the match end and the reverse machine
(`prune` off, D7) finds the earliest accepting position, i.e. the start
(`src/ir/dfa.c:1`, `src/core/compile.c:1127`-`:1133`). So what must be
preserved is each machine's accept behaviour at every position under every
view — not just "the same set of strings", but the same accept bit in each
of the three class-axis views and in each of the base / EOL / END position
views. Merging two states that agree on `up[UPC_PLAIN].accept` and differ on
`up[UPC_NL].accept` would answer a `(?m)$` with the wrong bit, silently;
`minimize.c:113`-`:120` splits the initial partition on **every** accept
bit for exactly that reason, and any online mechanism inherits that
obligation whole.

**(b) Answer identity across the corpus.** This is the checkable form of
(a). The existing sweeps are the `.rxt` corpus under the harness, the
`make test-axes` answer-identity sweep over every optimization-axis flag,
the `counterk` differential, and PC-3 against libpcre2 (`CLAUDE.md`, "Build
& test"). A compaction that is unsound will show up here if and only if the
corpus contains a pattern where the unsound merge is *reachable and
observable* — which section 4 argues is the weak point, not the strong one.

**(c) Byte identity of emitted artifacts — a separate question, and the
answer is "probably yes, and it must be measured, not argued".**

Here is the chain. The emitted table is written by `emit_tr_table`
(`src/gen/emit_dfa.c:2264`): `d->n * d->ncls` cells, iterated
`for i in 0..d->n` × `for cl in 0..d->ncls`, each cell
`tr_cell(d, r, i, cl)` = `r->cell_of(t, d)` (`:2216`), which for the
indexed form is the state number itself. **State numbers are emitted
verbatim.** So the emitted bytes are a function of the final state
*numbering*, not merely of the final automaton up to isomorphism.

The final numbering comes from `minimize.c:161`-`:172`: *"renumber classes
by first occurrence"* — walk raw states in index order, and the first raw
state of each block gives that block its final number. Raw index order is
creation order (§1.1). Therefore:

> If an online compaction merges a state **into the earlier-created member
> of its block**, and merges only pairs the final minimization would also
> have merged, then each surviving block's representative is still its
> minimum creation index, the survivors are still visited in the same
> relative order, and the final numbering is unchanged.

The argument that no *new* first-occurrence order arises: the worklist is
`for (int si = 0; si < d->n; si++)` (`src/ir/dfa.c:1284`), so a state's row
is expanded strictly after every lower-numbered state's row. If state *k*
is merged into an earlier state *j*, every successor *k*'s row would have
created was already created when *j*'s row was expanded, at a lower index,
in the same per-class order. Nothing is created later than it was before,
and nothing is created that was not created before.

**This is a plausibility argument, not a proof, and it has at least three
known holes:** it assumes the online merges are a subset of the final
minimization's merges (a *partial* compaction that merges on weaker
evidence could merge two states the final pass would keep apart only if it
were unsound, so this is really the soundness assumption again); it assumes
merging never *creates* a distinction (the `eolvar`/`endvar` variant states
are interned out of band inside `make_state`, `src/ir/dfa.c:1126`/`:1132`,
before the base view — so a merge of a variant changes which id a base state
records, and the ordering argument has to be redone for that path); and
[OPT-5]'s scan edge runs *after* minimization on the final numbering
(`src/core/compile.c:1143`), so it inherits whatever the numbering is
rather than constraining it.

**The rule that applies either way:** if a prototype changes one emitted
byte on one artifact that fits today, that is an `abi` bump plus an
identity-gate re-pin, in the same change, with every reader of the number
found by grep — `CLAUDE.md`'s situation-index row, D76/D94. It is a normal,
budgeted event before 1.0 (memory `pcrec-abi-changes-pre-release`), not a
blocker; but it is a *ritual*, and a prototype that quietly moves bytes
without performing it will be caught by the identity gates and rejected.

### 1.4 What the current caps do, and what compaction would do to them

This is the part that makes the mechanism a **contract change**, not an
optimization, and it is easy to miss.

| cap | value | read where | what compaction does to it |
|---|---|---|---|
| `PCREC_MAX_DFA_STATES_TABLE` | 32,000 | `limits.def:137`, checked at `dfa.c:886` against `d->n` | `d->n` becomes smaller, so **patterns that refuse today would compile** |
| `PCREC_MAX_DFA_STATES_GOTO` | 10,000 | `limits.def:136` | same, on ENG_ATTEMPT |
| `PCREC_MAX_TABLE_ENTRIES` | 2,000,000 | `limits.def:138`, folded into `maxstates` at `dfa.c:1195` | same |
| `PCREC_MAX_SUBSET_ELEMS` (K7) | 48,000,000 | `limits.def:139`, checked at `dfa.c:934` against `cx->subset_elems` | **unchanged unless the charge moves** — `subset_elems` is charged at intern time (`dfa.c:933`) and is a per-compile budget that nothing rolls back |
| `PCREC_MAX_EMIT_BYTES` | 1,000,000 | `limits.def`, the late post-emission check | the projected figure becomes tight; this is [LIM-2]'s whole objective |

Two consequences worth stating plainly:

- **The refusal set moves.** [LIM-2]'s own acceptance bar was "the refusal
  set moves NOT AT ALL", and lim2 §11 records a real regression found by
  `make test` when it moved by accident. Compaction moves it *deliberately*
  and in the permissive direction, which is a spec event under D80
  (`docs/spec/limits.md`) and needs `--engine=auto`'s [SEL-1] retry ladder
  re-examined, since that ladder reads `cx->dfa_overflowed`.
- **Compaction does not, by itself, fix K7.** The memory cost K7 bounds is
  `sum(nlist)` over interned states, charged before the lists are copied.
  A state that is merged away was still closed and still charged. Only a
  mechanism that avoids *computing* the closure — i.e. one that reduces the
  NFA before determinizing, or that recognizes the merge before `intern` is
  reached — reduces the K7 charge.

---

## 2. Survey (Frank's directive 1: the state of the art)

Searches run 2026-09-04. Where I could only reach an abstract or a search
snippet, the row says so; I did not read any of these papers in full.

### 2.1 Incremental / anytime / partial DFA minimization

**Watson, B. W. — "An incremental DFA minimization algorithm" (FSMNLP
2001); Watson & Daciuk, "An efficient incremental DFA minimization
algorithm", *Natural Language Engineering* (2003).**
<https://dl.acm.org/doi/10.1017/S1351324903003127>
The distinguishing property, in the authors' own framing: the algorithm
*may be halted at any time, yielding a partially-minimized automaton*, and
all other known minimization algorithms have intermediate results that are
not usable for partial minimization. It works by testing **equivalence of
state pairs** on demand (a recursive equivalence test with a depth bound,
memoized), rather than by global partition refinement. Quadratic time in
practice. **Exact** — the halted result is a correct automaton for the same
language, merely not fully minimized. *Verified from the search result
summary and the ACM/Springer abstracts; I did not read the paper.*

**Almeida, M., Moreira, N., Reis, R. — "Incremental DFA minimisation",
*RAIRO — Theoretical Informatics and Applications* 48(2):173-186 (2014).**
<http://www.numdam.org/item/ITA_2014__48_2_173_0/>
A newer incremental algorithm in the same family: quadratic for any
practical application, halted at any point returning a partially minimised
automaton, and — the property that matters most here — *"may be applied to
a given automaton at the same time as it is processing a string for
acceptance"*, i.e. it is explicitly designed to interleave with another
traversal of the machine. Core operations are pair equivalence testing and
union-find (Tarjan). **Exact.** *Verified from the journal abstract via
WebFetch; I did not read the paper.*

The important limitation of this whole family for our purpose: they
minimize an automaton that **already exists in full**. "Anytime" means you
may stop early and get a partially minimized *complete* automaton. It does
not mean you may minimize an automaton whose transitions have not been
computed yet. That gap is §3's central problem, and none of these papers
close it.

### 2.2 NFA reduction before determinization

**Ilie, Navarro, Yu / Ilie & Yu — NFA reduction by right- and left-invariant
preorders; "follow automata".**
Champarnaud & Coulon, "NFA reduction algorithms by means of regular
inequalities", *Theoretical Computer Science* (2004),
<https://www.sciencedirect.com/science/article/pii/S0304397504004803>,
surveys the family: reduction is driven by **preorders over states related
to inclusion of left and right languages**; Ilie, Navarro and Yu compute the
simulation relation for classical finite automata and use the natural
equivalences of right- and left-invariant quasi-orders to reduce NFAs.
Bisimilarity — the coarsest bisimulation — is computable in almost linear
time by Paige–Tarjan; the *simulation* preorder is more expensive but
strictly stronger as a reducer. **Exact** with respect to the language.
*Verified from the search summary and the ScienceDirect abstract.*

**Partial-derivative and position (Glushkov) automata as bisimulation
quotients.** Broda, Machiavelo, Moreira, Reis, "Partial Derivative and
Position Bisimilarity Automata" (CIAA 2014),
<https://link.springer.com/chapter/10.1007/978-3-319-08846-4_20>: partial
derivative automata and follow automata are quotients of the **position
automaton** by particular bisimulations. This is directly relevant because
pcrec's NFA is position-flavoured — its subset elements are `N_CLASS`
states, i.e. byte-consuming positions (`src/ir/dfa.c:1315`), and
its counted repeats are unrolled copies of one body (`src/ir/nfa.c:729`).
Copies of one body are precisely the shape a bisimulation quotient
collapses when their futures coincide. **Exact.** *Verified from the
chapter abstract.*

**D'Antoni & Veanes, "Simulation Algorithms for Symbolic Automata" (ATVA
2018),** <https://link.springer.com/chapter/10.1007/978-3-030-01090-4_7>
and the technical report <https://arxiv.org/pdf/1807.08487>. Simulation
computation lifted to automata whose transitions carry **predicates over a
large alphabet** rather than single symbols. pcrec's alphabet is exactly
this shape — byte equivalence classes computed per machine by `eqclasses`
(`src/ir/dfa.c:152`), typically far fewer than 256 — so a symbolic
formulation is the right one to borrow if this route is taken. **Exact.**
*Verified from the abstracts; algorithm details unverified.*

**Hyperscan (Wang et al., NSDI 2019),**
<https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf>.
Hyperscan's answer to determinization blow-up is not a better
determinization: it is **graph decomposition** — find literal (fixed
string) factors, cut the pattern into smaller "engines" at those factors,
and match each with whichever engine suits it (DFA, bit-parallel Glushkov
NFA, or a special-case engine). *"Decomposed regular expression components
increase the chance of fast DFA matching as they tend to be smaller than
the original pattern."* Version 2.0 moved to a Glushkov NFA internal
representation over which all transformations operate. So Hyperscan's
lesson for this study is a negative one about scope: the production system
with the strongest incentive to solve this problem sidesteps it structurally
rather than compacting subsets. **Heuristic at the decomposition level,
exact per engine.** *Verified from the NSDI paper's abstract and Intel's
own description; the reduction passes' details are unverified.*

### 2.3 Minimization interleaved with subset construction

**Nicol, J. & Frohme, M. — "Deconstructing Subset Construction: Reducing
While Determinizing" (arXiv:2505.10319, 2025; TACAS 2026),**
<https://arxiv.org/abs/2505.10319>, also
<https://link.springer.com/chapter/10.1007/978-3-032-22749-2_20>.
**This is the closest published work to the charter's question.** The
abstract, verbatim: *"We present a novel perspective on the NFA canonization
problem, which introduces intermediate minimization steps to reduce the
exploration space on-the-fly. Central to our approach are equivalence
registries which track and unify language-equivalent states, and allow for
additional optimizations such as convexity closures and simulation. Due to
the generality of our approach, these concepts can be embedded in classic
subset construction or Brzozowski's approach. We evaluate our approach on a
set of synthetic and real-world examples from automatic sequences and
observe that we are able to improve especially worst-case scenarios. We
provide an open-source library implementing our approach."*
The mechanism, as far as the abstract and the secondary summaries go:
exploration is **interrupted by a threshold predicate**, the
partially-constructed DFA is minimized, and exploration resumes on the
smaller machine. **Exact** (language-preserving canonization). Headline
result: improvement concentrated in **worst cases**, which is precisely the
population pcrec cares about. *Verified: abstract and venue. **Unverified:**
the operational definitions of "equivalence registry", "convexity closure"
and the threshold predicate; the experimental numbers; the overhead on easy
inputs. The PDF's text layer did not extract through WebFetch, and a full
read is a named item in §5's plan.*

**Brzozowski double-reversal** (reverse, determinize, reverse, determinize)
is the classical way to get a minimal DFA without a separate minimization
pass; García et al., "DFA minimization: from Brzozowski to Hopcroft",
<https://files01.core.ac.uk/download/pdf/14028276.pdf>, connects it to
partition refinement. It is worth naming for one pcrec-specific reason and
then setting aside: **pcrec already builds a reverse machine** for the D7
fast path (`src/core/compile.c:1131`), so half of Brzozowski's input exists.
It is set aside because the reverse machine is a *different* machine with
different pruning (`prune` false, `src/ir/dfa.c:1`) built from a separately
constructed reverse NFA, not the reversal of the forward DFA — and because
Brzozowski's complexity is exponential in the worst case, which is the case
at issue.

**Lazy / hybrid DFAs — Rust `regex-automata::hybrid`, RE2.**
<https://docs.rs/regex-automata/latest/regex_automata/hybrid/index.html>.
The lazy DFA builds itself during the *search*, bounded by a fixed cache
capacity, constructing at most one new state per input byte and so achieving
`O(mn)` search without ever paying worst-case construction. This is
**exact** but it is a fundamentally different product: pcrec is an
ahead-of-time compiler that emits self-contained C with no runtime
interpreter (`CLAUDE.md`, first paragraph). A lazy DFA moves determinization
into the generated code, which is out of scope by the project's own
definition. It appears here because it is the answer the two most-used
modern engines actually chose, and because it explains why neither of them
has an "online minimization" to borrow. *Verified from the crate
documentation.*

### 2.4 Bounded-size determinization, 2020s

**Baburin, I. & Cotterell, R. — "A Close Analysis of the Subset
Construction" (arXiv:2407.09891, 2024; DCFS 2025),**
<https://arxiv.org/abs/2407.09891>. Two results that bear directly on §3's
null candidate. First, a hardness result: computing NFA state complexity
within polynomial precision is **PSPACE-hard**, and *"it is PSPACE-hard to
decide whether the classical subset construction will yield an equivalent
DFA with an exponential increase in the number of states"* — so any a priori
estimate of the construction's size or running time is inherently hard.
Second, a usable positive result: they define **subset complexity**, an
upper bound on the size of the DFA produced by subset construction, and
show it can be bounded efficiently from the **cyclicity and rank of the
NFA's transition matrices**. *Verified from the arXiv abstract. The paper
does not, per its abstract, relate subset-construction size to minimal DFA
size — which is the relation lim2's census actually needs, so this bounds
the wrong end.*

**Dusi, N. et al. — "Quick Subset Construction", *Software: Practice and
Experience* (2023),** <https://onlinelibrary.wiley.com/doi/full/10.1002/spe.3246>.
Listed for completeness; I read only the title and venue. **Unverified.**

### 2.5 What the survey settles

- The "minimize while determinizing" idea is real, current, published in
  2025-26, exact, and reports its gains **exactly where pcrec's problem is**
  (worst cases). It is not folklore and it is not a fringe idea.
- Everything in the incremental-minimization family (§2.1) minimizes a
  *complete* automaton. "Anytime" is about stopping early, not about
  starting before the machine exists. Frank's proposed shape — partial
  during, thorough at the end — is therefore **not** a straight application
  of Watson or Almeida–Moreira–Reis; it needs its own soundness rule for
  states whose rows are not yet filled. §3.1 gives one.
- NFA-side reduction (§2.2) is the mature, cheap, one-shot half of the
  space, is exact, and is the only candidate that can reduce pcrec's K7
  charge as well as its state count, because it acts before any closure is
  computed.
- Nobody publishes an a priori bound on the *minimal* DFA's size that is
  cheap enough to compute during construction. The 2024 hardness result
  says not to look for one.

---

## 3. Candidate mechanisms, ranked by simplicity

Simplicity first, per Frank's directive 2. "Simplest" here means: fewest new
concepts in `src/ir/dfa.c`, fewest existing invariants disturbed, and — the
one that matters most in this file — fewest places where being wrong is
silent.

Line-count estimates are my judgement from reading the code, not measured.
"Exact" means language- and span-preserving by construction; "heuristic"
means it can be wrong and needs a checker.

### 3.0 Summary table

| # | mechanism | new code (est.) | cost per state | exact? | K18 raw/min ratio after | end pass unchanged? |
|---|---|---|---|---|---|---|
| **N1** | no compaction; refuse on a deterministic WORK budget instead of a projected size | 10-25 lines | zero | n/a — makes no size claim | unchanged (27×) | yes |
| **N2** | no compaction; minimize the CLOSED subgraph periodically and project from its block count | 80-120 lines | amortized O(n·ncls) per run | exact as a LOWER bound | unchanged (27×) | yes |
| **A** | Frank's shape: periodic partial minimization by the existing pass, "an unfilled row is unique" | 200-300 lines | O(rounds · n · ncls) per run | exact | **probably still ≈27× — see 3.2** | mode parameter added |
| **B** | reduce the subset as it is closed, by a dominance (simulation) preorder computed once on the NFA | 170-270 lines | O(nlist · log) per state, plus one O(\|Q\|·\|δ\|) precompute | exact **if** three pcrec-specific conditions hold (3.3) | plausibly ≈2-5× | yes |
| **C** | full online equivalence registry (Nicol & Frohme, §2.3) | 500+ lines, a new subsystem | high | exact | ≈1× by construction | replaced |

### 3.1 N — the null candidate: do not compact; change what is projected

Two forms. Both leave `src/ir/dfa.c`'s construction alone, emit not one
different byte on any artifact that fits today, and are therefore **not**
`abi` events.

**N1 — refuse on a deterministic work budget.** The harm [LIM-2] set out to
cut is a user waiting 10-20 s for a refusal that the VM route delivers in
0.01-0.07 s (lim2's own framing, `tests/resource/run_lim2_sizecap_projection.sh:15`).
That harm is a function of *work done*, not of *bytes projected*. pcrec
already maintains a deterministic work counter on exactly this path:
`cx->subset_elems`, incremented at `src/ir/dfa.c:933`, capped at 48,000,000
by K7. A second, much lower threshold on the same counter — routed the way
`intern`'s two existing refusals are routed, including `cx->dfa_overflowed`
so `--engine=auto`'s [SEL-1] ladder still sees it (the exact field lim2 §11
had to add) — refuses early, deterministically, with no claim about size at
all.

It is honest about what it is: a *complexity* refusal, not a *size* refusal.
It would say "pattern too complex for the DFA engine", which is a message
this compiler already has. It does not answer the charter's question. It is
in this list because it is a five-times-smaller change than anything else
here and it delivers most of the measured benefit, and because D77 says to
name the cheaper thing before building the expensive one.

**N2 — project from the closed subgraph.** Call a built state *closed* when
no state reachable from it has an unfilled row. On the closed subgraph, the
existing minimization computes exactly the final Nerode partition restricted
to those states (their futures are fully known and cannot be refined by
anything built later). The block count is therefore a **sound lower bound**
on the final minimized state count, and lower bounds are exactly what a
"refuse once the cap is provably exceeded" check needs — no `BAIL_KEEP_PCT`
margin, no percentage, no calibration, and lim2 §10's unrepresentable
"194.124 points" problem disappears.

**Its weakness is severe and is the reason it is not my recommendation.** In
a counted-repetition machine the built states form a large region from which
the frontier stays reachable, so the closed set may be nearly empty for most
of the construction. The bound would then be sound and useless. Whether that
is what actually happens on `k18_cost_gates`'s witness is a measurement
nobody has taken — it is item 1 in §5's plan, and it is cheap.

### 3.2 A — Frank's shape: incremental partial during, thorough at the end

**The idea, made precise.** Periodically, during the worklist loop, run the
existing `pcrec_minimize_dfa` on the machine built so far, then continue.
The end-of-construction call stays exactly where it is
(`src/core/compile.c:1134`).

**The soundness rule, and it is one line.** A partial machine has unfilled
transition rows (`tr[cl] == -2`, set at `src/ir/dfa.c:992`). Moore refinement
on a partial machine is unsound if two unfilled cells compare equal: two
states could then merge on the strength of two futures neither of which has
been computed. The fix is to make every unfilled cell **unique to its own
(state, class)** in `state_sig` (`src/opt/minimize.c:39`) — one extra branch
in the existing signature loop. With that, no state carrying an unfilled row
merges with anything, and no state transitioning into one merges with a state
transitioning elsewhere; the fixpoint propagates the exclusion backwards, and
what remains merging is precisely the closed subgraph of §3.1's N2. **Every
merge the online pass makes is therefore a merge the final pass would also
have made** — which is the premise §1.3(c)'s byte-identity argument needs.

That is the good news, and it is genuinely simple: one branch in
`state_sig`, plus a call site.

**Then the rest of it.** Merging mid-construction means renumbering live
states, and the machine's numbering is load-bearing in five places the
existing pass does not have to think about, because it runs when nothing is
live:

1. **The worklist cursor.** `for (int si = 0; si < d->n; si++)`
   (`src/ir/dfa.c:1284`) indexes states by number. A renumber invalidates
   `si` and must remap it.
2. **The intern hash table.** `d->tab` maps a state's hash to its index
   (`src/ir/dfa.c:827` `tab_insert`, `:835` `tab_grow`). After a renumber it
   must be rebuilt from scratch — and it can only be rebuilt if the states'
   NFA lists still exist, which brings us to (3).
3. **The pass destroys what construction needs.** `minimize.c:183`-`:186`
   sets every surviving state's `up[u].nlist = 0; up[u].list = NULL`,
   on the stated ground that *"the NFA-state lists are dead after
   minimization (nothing downstream reads them)"*. During construction they
   are not dead: the worklist reads
   `d->st[si].up[cu].list` at `src/ir/dfa.c:1310` to build the next pre-set,
   and `view_same` (`:849`) memcmps them on every intern. So the online pass
   must keep them — which means keeping the representative's lists and
   discarding the merged-away states' arena storage (arena memory is not
   individually freeable, so it simply leaks until the compile ends; that is
   consistent with how the arena is already used, but it means the K7 charge
   is unchanged, §1.4).
4. **The start-state family.** `s0`, `s1u[UPC_N]`, `s1g[UPC_N]` are remapped
   at `minimize.c:202`-`:215`, with a comment recording that forgetting one
   leaves *"a wrong start state rather than a missing one, and only on
   patterns that minimize, which is most of them"*. Online, the same remap is
   needed, plus the `eolvar`/`endvar` re-canonicalization at
   `minimize.c:193`-`:196` has to be correct against states whose rows are
   still unfilled.
5. **The caps.** `d->n` shrinks, so the state cap at `src/ir/dfa.c:886` now
   measures something different (§1.4). The refusal set moves.

**The cost, and K25.** `known_issues.md` K25 records that Moore refinement
needs O(n) rounds on a chain, and that `a{0,25000}` already spends **15.3 s
of its 15.4 s compile inside minimization**. Running the pass *k* times
multiplies that. A threshold predicate (Nicol & Frohme's own device, §2.3)
controls it, but the predicate is then a tuning knob whose calibration is
another `BAIL_KEEP_PCT`-shaped hazard: a number chosen against a small
witness set that a wider population invalidates.

**The finding that decides this candidate.** Under the sound rule, the merges
available online are exactly the closed subgraph's — and on the K18 shapes I
expect that set to be small until construction is nearly finished, for the
same reason N2's bound is at risk of being vacuous: the counter's states keep
the frontier reachable. **If that is right, Frank's shape is simpler than
full online minimization *and does almost nothing on the population that
motivated the study*.** I want to be very clear that this is *reasoned, not
measured* — §1.2's argument about why the states are equivalent says nothing
directly about when they become *provably* equivalent. It is the single
cheapest measurement in §5 and it should be taken before any of this is
built.

**A weaker rule that would merge more is available and I do not recommend
it**: treat an unfilled cell as a wildcard that matches anything. That gives
a coarser partition, so more merges — but wildcard-compatibility is not
transitive, so it is not an equivalence relation, the fixpoint is not
well-defined, and merges made on it are not merges the final pass would make.
It is unsound, and it would be unsound in the silent direction.

### 3.3 B — reduce the subset as it is closed, by an NFA-level dominance preorder

This is the brief's "reduce the NFA/positions by simulation before
determinizing", in the form that actually fits this construction.

**The mechanism.** Compute, once per machine before the worklist runs, a
preorder `⊑` on the NFA's `N_CLASS` positions such that `p ⊑ q` implies
every continuation `p` accepts, `q` also accepts, at the same position. Then,
in `closure` (`src/ir/dfa.c:771`), drop a position from the emitted list when
a position already in the list dominates it. §2.2's literature calls this
the right-invariant preorder / simulation reduction (Champarnaud & Coulon;
Ilie–Navarro–Yu), and §2.2's symbolic-automata work (D'Antoni & Veanes) is
the version that fits pcrec's byte-equivalence-class alphabet.

**Why this shape, specifically, is the one that could crush K18.** The
counter tail is `(X(X(X)?)?)?` (`src/ir/nfa.c:744`-`:745`): a position in
copy *j* has strictly more iterations remaining than the same position in
copy *i > j*, so `copy_i ⊑ copy_j` for `j < i` — the inclusion §1.2 already
established, now used as a *reason to delete* rather than as an obstacle. A
subset that has reached copies 4 through 30 reduces to `{copy 4}`. The number
of reachable subsets falls from the number of *ranges* of copies to the
number of *minima*, i.e. from roughly quadratic in the count to roughly
linear. That is the right order of magnitude for lim2's measured
27,575 → 1,010.

It is also the only candidate here that reduces `sum(nlist)` and therefore
**actually reduces the K7 charge** (§1.4), because it acts before `intern`
sees the list.

**It does not reach the minimal machine.** `{copy 4}` and `{copy 5}` are
still distinct states, and the final minimization is still needed and still
does real work. Expect the raw/minimized ratio to fall from ~27× to
something small but not 1×; the end pass stays exactly as it is, unchanged.

**Three pcrec-specific soundness conditions, and every one of them is a way
this could be quietly wrong.**

1. **Domination must hold in every view.** A position's future is not one
   language: it is an accept answer in each of `UPC_PLAIN` / `UPC_WORD` /
   `UPC_NL` and in each of base / EOL / END (§1.3(a)). A preorder computed
   without the assertion states (`N_WORDB`, `N_EOL_M`, `N_BOT_M`, `N_END`,
   `N_GSTART` — the kinds scanned at `src/ir/dfa.c:1153`-`:1171`) would
   dominate across a context boundary and answer a `\b` or a `(?m)$` with the
   wrong bit. The preorder has to be computed on the assertion-bearing NFA,
   with assertions as guards, or it is wrong.
2. **The K18 open-loop context breaks context-freeness of "the future".** The
   whole point of `src/ir/dfa.c:207`'s memo is that a position's behaviour
   inside a closure depends on **which loops are open on the path that
   reached it** — that is PCRE's empty-iteration rule. So "the language of
   position *p*" is not well-defined independent of context, and a dominance
   relation computed on the bare NFA may fail under some contexts. Either the
   preorder must be conditioned on the open-loop context (much more
   expensive, and the contexts are discovered during closure, not before), or
   it must be restricted to pairs where no loop entry separates them — a
   restriction that is easy to state and easy to get subtly wrong.
3. **Priority.** I believe order is safe here and I want to record the
   argument so a reviewer can attack it. The DFA route answers spans, not
   captures (§1.3(a)); its per-state output is a set of accept bits. If
   `p ⊑ q` and both are in the list, then every accept `p` contributes, `q`
   contributes at the same position, so no accept bit changes, whichever of
   the two comes first in preference order. Priority pruning (`prune` on,
   `src/ir/dfa.c:1`) truncates the list at the first ACCEPT, so dropping `p`
   can only *lengthen* the surviving list, never change where it truncates.
   **This is reasoning, not proof, and it is the claim I would most want a
   D6 panel to attack** — the leftmost-first machinery in this file has
   already produced three separate corrections (K1, K17, K18) for arguments
   that looked this clean.

**Cost.** The simulation preorder is the expensive part: classically
`O(|Q|·|δ|)`, and the NFAs here reach tens of thousands of states on exactly
the patterns that need it. A cheaper *bisimulation* quotient (Paige–Tarjan,
near-linear) is available and **is not the same thing** — bisimilarity would
merge copies only if their futures coincide exactly, which for an unrolled
counter they do not, so I expect bisimulation alone to buy approximately
nothing on K18 shapes. That is worth stating because it is the intuitive
first thing to reach for and it is the wrong one.

**One tempting shortcut, named so it is not silently taken.** The dominance
that matters on the K18 shapes is "copy *i* of an unrolled repeat is
dominated by copy *j < i* of the same repeat", which the NFA builder knows
by construction and could stamp on each state for free, with no preorder
computation at all. That is a special case of a general fact, and this
project's standing rule (memory `pcrec-general-mechanisms-not-special-cases`,
D75's addendum as the worked example) is that the general form is what gets
built. It is legitimate as an *implement-then-replace* first prototype for
the measurement in §5 — where the question is only "how much is there to
win" — and it is not legitimate as a landing.

### 3.4 C — the full online equivalence registry

Nicol & Frohme's construction (§2.3): an equivalence registry that tracks and
unifies language-equivalent states as they are discovered, with convexity
closures and simulation as additional reducers, and a threshold predicate
that interrupts exploration to minimize. Exact, published, and by
construction it makes raw size track minimized size — which is precisely what
the charter asks for.

It is last because it is a new subsystem, it replaces `src/opt/minimize.c`
rather than extending it, and it lands every one of §3.2's five
renumbering hazards *plus* whatever the registry's own invariants are. I
have not read the paper past its abstract (§2.3, **unverified**), so I
cannot estimate its code size honestly beyond "500+ lines and a new file",
and I cannot say what its overhead is on the ordinary patterns that make up
99% of the corpus. Its authors publish an open-source implementation; reading
that implementation and the paper is a named, cheap item in §5.

I would not charter this without B having been measured first. If B gets the
ratio from 27× to 3×, the remaining 3× is not worth a new subsystem.

---

## 4. Brittleness (Frank's directive 3, and his stated concern)

The two candidates that actually compact are **A** (Frank's shape) and **B**
(dominance pruning). This section takes each apart by failure mode and asks
the project's own question of each one: *what would have to be true for a
check to fail, and who chose that input* (`docs/dev/learnings.md` §3).

The working definition, from the brief: **a mechanism whose failures nothing
would catch is brittle.** By that definition the verdicts below are not
symmetric, and the asymmetry is the useful part of this section.

### 4.1 The existing checks, and what each one can see

| check | sees | blind to |
|---|---|---|
| `.rxt` corpus under `tests/harness/run.sh` | wrong spans, wrong verdicts, on ~2,845 patterns | anything the mechanism does not reach on those patterns |
| `make test-axes` | an axis flag changing an answer | a change that is answer-identical and wrong about size or cost |
| PC-3 registry vs libpcre2 | construct reality and module attribution | spans (it is a registry differential) |
| `counterk` differential, `tests/base/k18_*.rxt` (1,459 guard cases) | counted-repeat and empty-iteration preference errors | assertion × counted-repeat cross products |
| `tests/codegen/run_*_identity.sh` | one emitted byte moving, against a reference build | nothing — this axis is well covered and loud |
| `tests/size/` artifact-size log + tripwire | artifact size moving per pattern | compile TIME |
| `tests/resource/` CPU budgets, `k18_cost_gates.rxt`'s harness budget | a compile-time cliff on the shapes it names | a uniform few-percent regression spread over the corpus |
| `tests/mech/run_sabotage_matrix.sh` | a check that cannot go red | a check nobody wrote |
| lim2's `tests/resource/lim2_census.c` | raw-vs-minimized shrink, forward machine, 12 patterns | the reverse and anchored machines |

### 4.2 Candidate A — periodic partial minimization

| # | failure mode | caught by | new check needed |
|---|---|---|---|
| A1 | a merge made on a partial machine that the final machine would not make (unsound in the silent direction) | the corpus sweep — **only if the online pass fires on corpus patterns.** It fires above a threshold; ordinary patterns never reach it. This is the `[MECH-REACH]` shape exactly: a witness that never reaches its site | **yes, and it is the load-bearing one:** a forced mode (`threshold = 1`, run after every interned state) plus the whole corpus, answer-identical. Without it the mechanism's soundness is checked on a population of about a dozen patterns |
| A2 | `d->n` shrinks, so the state cap (`dfa.c:886`) and `PCREC_MAX_TABLE_ENTRIES` fire later: patterns that refuse today compile | **nothing asserts the refusal set.** lim2 §11's identical failure was caught by `tests/vm/run_vm_tests.sh`'s [SEL-1] section by luck, not by design | **yes:** a refusal-set manifest — verdict plus stamped category per pattern over corpus + `tests/resource` shapes, diffed. lim2 needs it too; it is one check for two rows |
| A3 | scoped to the forward machine (lim2's precedent), leaving the reverse machine — where the measured shrink is worst, 29-65% (lim2 §2) — untouched | nothing per-machine | extend `lim2_census.c` to the reverse and anchored machines. Small |
| A4 | the DFA is also the VM's capture-erased **prefilter** (S6.1); a prefilter that became a subset rather than a superset would drop matches | the corpus's hybrid patterns, `counterk`, `backrefs` | no — covered, provided A1's forced mode runs over the whole corpus |
| A5 | state numbering moves, so emitted bytes move | the identity gates and the size ratchet, loudly | no. This axis is the project's strongest |
| A6 | performance cliff: K25 records minimization at 15.3 s of a 15.4 s compile on `a{0,25000}`; k runs multiply it | `tests/resource/` budgets and `k18_cost_gates.rxt`'s own harness budget — this is precisely what that file exists for | no |
| A7 | the threshold predicate's calibration — a number chosen against a small witness set | nothing | **yes:** a census across the population, and per learnings §3 it must not be derived from the mechanism's own decision. lim2 §10 is the template, including its failure |

**Verdict on A: checkable, but only with A1's forced mode, and A1's forced
mode is the whole difference between "tested" and "tested on twelve
patterns".** A's real problem is not brittleness. It is that §3.2 expects it
to merge almost nothing on the population that motivated the study, and that
prediction is untested. **Measure before building** (§5, M1).

### 4.3 Candidate B — dominance pruning inside the closure

| # | failure mode | caught by | new check needed |
|---|---|---|---|
| B1 | the preorder dominates across an assertion boundary, so a `\b` / `(?m)$` / `\z` accept bit is wrong in one view only | `tests/assertions/` and PC-3 — **only if a corpus pattern combines an unrolled counted repeat with an assertion.** That is a cross-product cell, and learnings §3 records this exact failure ("a corpus needs the axes of the MECHANISM under test, not of the exemplar that motivated it; the cross-product cell neither of two large honest sweeps generates") | **yes, and it is the load-bearing one:** a generated corpus of {counted-repeat shapes} × {`\b`, `\B`, `(?m)^`, `(?m)$`, `\z`, `\Z`, `\G`}, oracle-verified against libpcre2. It does not exist today |
| B2 | the K18 open-loop context makes "the language of a position" context-dependent, so a preorder computed on the bare NFA is wrong under some contexts | the four `k18_*.rxt` files' 1,459 guard cases — the strongest existing check for this hazard, and `DFA_INVARIANT` (`dfa.c:250`) aborts in shipped builds if loop nesting stops being proper | **yes:** sabotage rows planting an over-relating preorder, asserting the k18 suites go red. If they stay green that is a finding about the population, not a pass (learnings §3) |
| B3 | priority: §3.3's condition 3 is an argument, and the leftmost-first machinery in this file has already produced K1, K17 and K18 against arguments that looked this clean | the corpus's spans, `counterk`, the lazy-preference witnesses `src/ir/nfa.c:741` names (`(?:ab\|a){0,2}?b`) | a preference differential over dominated-position shapes specifically — lazy and greedy spellings of the same counted repeat |
| B4 | the reverse machine runs with `prune` off and must keep every thread to find the **earliest** accept; the soundness argument there is not the forward one | full-span corpus answers, if such a pattern exists in the corpus | same cross-product corpus as B1, with the reverse machine as an explicit axis |
| B5 | emitted bytes move wherever domination exists | identity gates, size ratchet | no — but the landing is an `abi` bump plus a re-pin at every reader found by grep (D76/D94) |
| B6 | the preorder is computed on **every** pattern, including the 99% that gain nothing; classically `O(\|Q\|·\|δ\|)` | `tests/bench/run_bench.sh`'s COMPILE-SPEED budget and `tests/resource/` — both calibrated for cliffs, not for a uniform 3% | **yes:** a corpus-wide compile-time delta, the shape the artifact-size log already has for size |
| B7 | fewer states and smaller subsets mean K7 and the state caps fire later: the refusal set moves permissively | nothing | the same refusal-set manifest as A2 |

**Verdict on B: brittle as the tree stands today, and specifically fixable.**
Three of its seven failure modes (B1, B2, B4) live in a cross-product cell
that no existing sweep generates, and B2's is the cell where this project has
already been wrong three times. That corpus is a bounded, buildable thing —
a few hundred generated patterns, oracle-verified — and learnings §3's rule
applies with full force: **it must be written before the mechanism, not
after**, because "guards written to answer a finding are reliably wrong in
the way the finding was wrong."

With that corpus and the sabotage rows, B stops being brittle. Without it, B
is a mechanism whose sharpest failure mode nothing in the tree can see, which
is the definition the brief gave.

### 4.4 The null candidates' brittleness, briefly

N1 (a work budget) has one failure mode: it refuses a pattern that would have
compiled. That is loud, deterministic, and caught by the refusal-set manifest
of A2/B7 — which N1 needs built anyway. N2 (project from the closed subgraph)
cannot be unsound as a lower bound (§3.1), so its only failure is being
*vacuous*, which is a silent failure of a different kind: the bail simply
never fires and lim2's 10-20 s refusals come back. That is caught by lim2's
existing cost check (`run_lim2_sizecap_projection.sh`'s check 2, the wall-time
ceiling that fails when the bail stops firing) — a check that already exists
and was already designed for exactly this.

---

## 5. Recommendation, and the measurement that would trigger building it

### 5.1 Recommendation

**Do not build A. Do not build C yet. Take two measurements, and let them
decide B.** In order:

1. **Fix lim2's margin problem with N2, as its own small row, now.** The
   closed-subgraph block count is a sound lower bound with no percentage in
   it, which retires lim2 §10's finding that no `BAIL_KEEP_PCT` value can
   express the required margin. It changes no emitted byte, is not an `abi`
   event, and is 80-120 lines. **Conditional on M1** below showing the closed
   set is not empty; if it is empty, fall back to N1 (a deterministic work
   budget), which is smaller still and delivers most of the measured benefit
   while making no size claim at all.
2. **Measure the prize for B (M2). If it is there, charter B; if it is not,
   the honest answer to the charter's question is "no, not affordably", and
   that is a legitimate outcome to record rather than a failure to route
   around.**
3. **Read the Nicol & Frohme paper and its library (M5).** No box time, and
   it is the only thing that can retire §2.3's and §3.4's `unverified`
   marks. Do it regardless of what M1 and M2 say.

Frank's directive 2 asked whether "incremental partial during, thorough at
the end" is simpler than full online minimization. **It is simpler — the
soundness rule is one branch in `state_sig` — and I believe it is
ineffective on the population that motivated the study**, because the merges
it can soundly make are exactly the closed subgraph's, and on a counted
repetition the frontier stays reachable from nearly everything until the
end. That belief is the thing M1 tests, and M1 is cheap enough that no
design work should happen before it.

Frank's directive 3 asked whether this can be done without getting brittle.
**For B: yes, but only after the cross-product corpus of §4.3 exists.** For
A: yes, but only with the forced-threshold mode of §4.2, and the question is
moot if M1 says A does nothing.

### 5.2 The measurements

All five are read-only instrumentation of a debug build, none of them land
under `src/`. Each names its own acceptance bar in advance, per D77.

**M1 — the closed fraction (decides A and N2; the cheapest thing here).**
Instrument `pcrec_build_dfa`'s worklist to report, at each 5% of raw states
built, how many built states have no unfilled row reachable from them.

- Rows: `tests/base/k18_cost_gates.rxt`'s two witnesses (the census witness
  `(1{0,30}?[^]abc][^abc]){28,30}0+|a` and the nested-counted family the
  brief cites); pcrec-bench's altwide `w-2048`, `w-512`, `s-4096`, `s-2048`,
  `sh1-512`; the `tests/counterk/` tower; and 20 ordinary corpus patterns as
  a control.
- Read: closed fraction against construction progress, per machine (forward,
  reverse, anchored).
- **Bar:** if the closed fraction passes 50% before half the raw states are
  built on the k18 witness, A and N2 are both live. If it stays under 10%
  until the last 5% of construction, **A is dead for this population and N2
  is vacuous** — go to N1 and stop.

**M2 — the dominance prize (decides B).** Instrument the same build with a
deliberately illegitimate stand-in for the general preorder: drop a position
when an earlier copy of the same unrolled repeat is present in the list. This
is the special case §3.3 names and forbids as a landing; it is legitimate
here because the only question it answers is *how much is there to win*.

- Rows: the same set as M1.
- Read: raw states, minimized states, `sum(nlist)` (the K7 charge),
  construction wall time — each with and without the stand-in.
- **Bar:** charter B's general form if, on the k18 witness, the raw/minimized
  ratio falls from 27× to under 3×, **and** `sum(nlist)` falls by more than
  2× on the altwide `w-N` series. If the ratio stays above 10×, B is not the
  mechanism either; record that and close the study's question.

**M3 — the refusal-time prize (the thing [LIM-2] actually wanted).** Refusal
wall time on `w-2048` and on `run_lim2_sizecap_projection.sh`'s own
1,600-literal synthetic witness, under whichever of N1/N2/B survives.

- **Bar:** lim2's own target was "the VM route's cost class", ~0.1 s. lim2
  measured 1.55 s on `w-2048` and 12.51 s on `s-4096` and did not reach it.
  Beating 1.55 s on `w-2048` is the honest bar; reaching 0.1 s is the goal.

**M4 — the cost on the 99% (a veto, not a prize).** Compile-time delta over
the whole `.rxt` corpus for whichever prototype survives M1/M2, in the shape
the artifact-size log already has for size.

- **Bar:** median regression under 2%, p99 under 10%. Worse than that and the
  mechanism needs a threshold predicate, which reopens §4.2's A7 calibration
  hazard and should be counted against the candidate's simplicity, not waved
  through.

**M5 — read the literature properly.** Nicol & Frohme, arXiv:2505.10319 /
TACAS 2026, in full, plus their open-source library: the operational
definitions of "equivalence registry", "convexity closure" and the threshold
predicate; the experimental numbers; the overhead on easy inputs. No box
time, no acceptance bar — it retires four `unverified` marks in this
document.

### 5.3 The acceptance bar for the step itself, whenever it is chartered

Not a measurement, a delivery standard, stated here so it is not negotiated
later:

- Answer-identical over the whole corpus on every axis (`make test-axes`),
  and PC-3 green.
- **The cross-product corpus of §4.3 (counted repeats × assertions × machine
  direction) written, oracle-verified and RED under a planted over-relating
  preorder, before the mechanism lands** — not after.
- A refusal-set manifest, with every movement in it explained and carried in
  `docs/spec/limits.md` in the same change (D80).
- The identity gates green after a deliberate `abi` bump and a re-pin at
  every reader of the number found by grep (D76/D94), or byte identity
  demonstrated and the bump shown to be unnecessary — measured, not argued
  from §1.3(c)'s plausibility sketch.
- `make strict`, `make test`, `make test-codegen`.

### 5.4 What this study does not claim

- That B is sound. §3.3's three conditions are stated as obligations, and
  condition 3 (priority) is an argument I want attacked.
- That the byte-identity sketch in §1.3(c) holds. It is a plausibility
  argument with three named holes and it must be measured.
- Anything about Nicol & Frohme's algorithm beyond its abstract.
- Any number about pcrec that was not read from the code or from lim2's
  report. **No compile, no `make`, and no benchmark was run by this lane**;
  every quantitative claim here is either cited from `lim2_report.md`, from
  `known_issues.md`, from `limits.def`, or marked as an expectation to be
  measured.
