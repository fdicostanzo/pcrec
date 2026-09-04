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
`(X(X(X)?)?)?` built copy by copy (`:732`-`:745`). Nesting a counted
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
