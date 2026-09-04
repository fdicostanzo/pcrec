# Compacting DFA states as they are generated — a design study

Lane `dfamin`, worktree `worktrees/dfamin`, branch `lane/dfamin`, on `main`
at `03e632c0` (plan row [LIM-2] STUDY-1). **READ-ONLY study**: nothing under
`src/` or `tests/` is written by this lane, no `make` was run, no compile
and no benchmark. Every claim about pcrec's code is cited as `path:line`
and comes from reading that code in this worktree; every claim about the
literature carries a citation, and the ones I could not verify past an
abstract or a search snippet are marked **unverified**.

**Revised 2026-09-04, same day, after Frank clarified the charter.** The
first version ranked §3 under the assumption that the two-pass shape was the
target; Frank's clarification made clear it is an opportunity, not a
constraint. §3 is rewritten (a merge taxonomy, full online compaction as a
first-class candidate, and a new candidate A′), §4 gains brittleness tables
for the two candidates that were not first-class before, and §5's
recommendation changes. §1 and §2 are unchanged. The revision's own trigger
and what it moved are recorded at the head of §3.

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

## 3. Candidate mechanisms, ranked on the merits

**Revised 2026-09-04 after Frank's clarification** (14:3x, relayed by the
manager): he does not dictate the method — *"if it turns out the full
compaction is the way to go then i'm all for it"* — and the two-pass shape is
an **opportunity, not a constraint**: an incremental pass that takes the easy
wins as states are generated, then another pass for the complicated
equivalences, and that second pass *"might even be optional if expensive and
the final state of the incremental was usable"*. So this section now ranks on
simplicity, soundness and brittleness **together**, full online compaction is
a first-class candidate rather than a long-shot last row, and §3.1-§3.2 answer
the two questions the clarification opens: which equivalences are the cheap
and safe incremental wins, and whether the thorough pass is a correctness
requirement or an optimization.

Line-count estimates are my judgement from reading the code, not measured.
"Exact" means language- and span-preserving by construction.

### 3.1 Is the thorough pass a correctness requirement or an optimization?

**It is an optimization, and the evidence is inside the pass itself.**

`pcrec_minimize_dfa` returns immediately when `n <= 1` (`src/opt/minimize.c:69`)
and rebuilds only when it actually merged something — `if (nparts < n)`
(`:160`). So **"minimization merged nothing" is already an ordinary, shipped
outcome**, and every stage downstream of it handles an unmerged machine on
every compile where the partition happens to be discrete. The pass's own
header states its role plainly: priority semantics *"are fully baked into the
transition structure by the time this runs, so behavior-preserving merging
cannot change any match result"*, and what it buys is that it *"shrinks
emitted tables / label counts, which is both a code-size and a cache win"*.

Three things do depend on it. None of them is correctness:

1. **Ordering, against [OPT-5]'s scan edge.** `src/core/internal.h:4387`:
   the scan-edge pass *"Runs on EVERY machine, immediately after
   `pcrec_minimize_dfa` on that machine: it needs the canonical state set,
   and nothing after it rebuilds a `DState`."* The hard half of that is the
   ordering — minimize's rebuild `calloc`s fresh `DState`s
   (`src/opt/minimize.c:164`) and copies the accept bits, `tr`, `eolvar` and
   `endvar` but **not** `scan_span`, so running minimize *after* scanedge
   would silently drop every scan edge. Whether **minimality** as opposed to
   **finality** is a precondition of the chain-finding walk is *not* settled
   by that sentence: the pass's five preconditions
   (`src/opt/scanedge.c:43` onward) are local shape tests on `tr[]` and the
   accept bits, which an unminimized machine can satisfy. **Marked as a
   question a prototype must answer, not as a fact.**
2. **Representation.** `dfa_premul` (`src/gen/emit_dfa.c:2518`) reads the
   finished machine's `n * ncls` against `PREMUL_MAX_ENTRIES`, so skipping
   the pass changes which table form is emitted. A size and speed effect.
3. **Size.** The artifact grows by exactly the shrink the pass would have
   made: 0.75-3.5% forward and 29.5-65.4% reverse on lim2's two altwide
   witnesses, and **97% on the k18 census witness** (lim2 §2, §10).

So Frank's "might even be optional" is **architecturally available** — an
unminimized DFA is a correct artifact today. Whether it is *desirable* is
decided by (3), and (3) decides it firmly: skipping a pass that removes 96%
of the states would enlarge the artifact 27-fold on precisely the pattern
this study exists for. **The second pass becomes genuinely optional only in
proportion to how close the incremental pass gets to minimal** — which,
§3.2 shows, is a property of exactly one of the candidates.

**And this reframes the size bail, which is the finding I would most want
Frank to see.** For [LIM-2]'s early refusal you must prove *"the final table
will be at least X"*, and a lower bound on the final state count comes only
from a set of states you have proved **pairwise inequivalent** —
distinguishability is monotone, so states proved distinct stay distinct as
the machine grows. Compaction proves the **opposite** thing: it proves
states equivalent. A partially compacted count is an *upper* bound on the
explored part's final blocks, and upper bounds license nothing. **So
compaction does not, by itself, make the bail exact — unless the incremental
result IS the artifact, at which point raw equals emitted, the projection is
exact by identity, and no bound reasoning is needed at all.** That is the
one configuration in which Frank's optional-second-pass idea and lim2's
margin problem solve each other, and it is why §3.8's candidate matters more
than its position in the original draft suggested.

### 3.2 A taxonomy of the merges: what does each one need to know?

This answers "which equivalences are the cheap-and-safe incremental wins".
The tiers are ordered by what a merge must know before it can be made.

**Tier 0 — needs nothing. Already built, and worth naming so the baseline is
honest.** pcrec already performs the cheapest online compaction there is:
two pre-sets whose closures are identical intern to one state
(`src/ir/dfa.c:871`), an empty non-accepting closure is not a state at all
(`:1115`), views that coincide share one list (`:915`), and `eolvar`/`endvar`
canonicalize to `-1` when they match (`:1126`, `:1132`). The baseline is not
"no online compaction" — it is "online compaction limited to *syntactic
identity* of the closure". Everything below extends that reach.

**Tier 1 — needs only facts about the NFA, computable once before the
worklist runs.** Dropping *dominated positions* from a subset (candidate B,
§3.7). Reduces the lists themselves, so it reduces `sum(nlist)` and therefore
the K7 charge, and it reduces how many *distinct* lists exist at all.

**Tier 2 — needs one state's own finished row, and nothing else.** Two states
whose accept-bit vectors, transition rows (target for target), `eolvar` and
`endvar` are identical **are equivalent, full stop**: `δ(i,c) = δ(j,c)` for
every class and equal accepts means equal residuals, with no fixpoint, no
lookahead and no partition. This is the first round of Moore refinement
isolated, and it is the cheapest *real* online merge available (candidate A′,
§3.6).

**Tier 3 — needs the futures of a bounded region.** Moore refinement over the
subgraph whose reachable set is fully explored (candidate A, §3.5). Exact,
and its merges are a subset of the final pass's.

**Tier 4 — needs an equivalence *hypothesis* maintained against an unfinished
machine.** Assume states equivalent, propagate the assumption, and split when
a counterexample arrives. This is the union-find-plus-refutation shape
Watson/Daciuk and Almeida–Moreira–Reis use for on-demand pair equivalence
(§2.1), and it is what Nicol & Frohme's "equivalence registry" appears to be
(§2.3, **unverified**). Candidate C, §3.8.

**The ranking criterion this taxonomy exposes, which the original draft
missed:**

> **Only Tiers 1 and 4 can make construction itself cheaper.** Tier 1 shrinks
> the lists, so fewer distinct subsets are ever formed. Tier 4 can merge two
> states *before either has been expanded*, which is the only way an
> *equivalence* saves work. Tiers 2 and 3 merge states that have already been
> paid for: they shrink the count and the artifact, not the compile.

So the answer to "which are the cheap-and-safe incremental wins" is **Tiers 1
and 2** — Tier 2 unconditionally (it needs no new theory at all), Tier 1
subject to §3.7's three conditions. The answer to "which need the thorough
pass" is **Tier 3 and above**, and specifically the K18 case: two subsets are
equivalent there because the *union* of their residual languages coincides,
which no bounded-depth local check can see. If the incremental pass is
Tiers 1+2, the entire 97% shrink is left to the thorough pass.

### 3.3 The candidates, ranked

| # | mechanism | tier | new code (est.) | exact? | makes construction cheaper? | K18 ratio after | second pass optional? |
|---|---|---|---|---|---|---|---|
| **A′** | merge states with identical finished rows | 2 | 40-70 lines | yes, trivially | no | small effect | no |
| **N1** | no compaction; refuse on a deterministic WORK budget | — | 10-25 lines | n/a — makes no size claim | n/a | unchanged (27×) | n/a |
| **N2** | no compaction; project from the CLOSED subgraph | 3 (read-only) | 80-120 lines | exact as a LOWER bound | no | unchanged (27×) | n/a |
| **B** | drop dominated positions from each subset | 1 | 170-270 lines | exact **if** §3.7's three conditions hold | **yes** | plausibly 2-5× | no |
| **A** | periodic partial minimization, "an unfilled row is unique" | 3 | 200-300 lines | yes | no | probably still ≈27× (§3.5) | no |
| **C** | full online compaction / equivalence registry | 4 | 500+ lines, new subsystem | yes | **yes** | ≈1× by construction | **yes — uniquely** |

### 3.4 N — the null candidates: do not compact; change what is projected

Both leave `src/ir/dfa.c`'s construction alone, emit not one different byte on
any artifact that fits today, and are therefore **not** `abi` events.

**N1 — refuse on a deterministic work budget.** The harm [LIM-2] set out to
cut is a user waiting 10-20 s for a refusal the VM route delivers in
0.01-0.07 s (`tests/resource/run_lim2_sizecap_projection.sh:15`). That harm is
a function of *work done*, not of *bytes projected*, and pcrec already
maintains a deterministic work counter on this path: `cx->subset_elems`
(`src/ir/dfa.c:933`). A second, much lower threshold on it — routed the way
`intern`'s two existing refusals are, including `cx->dfa_overflowed` so
`--engine=auto`'s [SEL-1] ladder still sees it (the field lim2 §11 had to add)
— refuses early and deterministically with no size claim at all. Honest about
being a *complexity* refusal rather than a *size* one. It does not answer the
charter's question; it is here because D77 says to name the cheap thing first.

**N2 — project from the closed subgraph.** Call a built state *closed* when no
state reachable from it has an unfilled row. On the closed subgraph the
existing minimization computes exactly the final Nerode partition restricted
to those states, so its blocks are **provably pairwise inequivalent** — which
§3.1 shows is the property a bail actually needs. The block count is a sound
**lower bound** on the final minimized state count: no `BAIL_KEEP_PCT`, no
percentage, no calibration, and lim2 §10's unrepresentable "194.124 points"
disappears.

Its weakness is that the closed set may be nearly empty for most of the
construction on exactly the counted-repetition shapes at issue, leaving the
bound sound and useless. That is measurement M1 (§5.2), and it is cheap.

### 3.5 A — periodic partial minimization (Tier 3)

Periodically run the existing `pcrec_minimize_dfa` on the machine built so
far, then continue; the end-of-construction call stays where it is
(`src/core/compile.c:1134`).

**The soundness rule is one branch.** A partial machine has unfilled rows
(`tr[cl] == -2`, `src/ir/dfa.c:992`). Moore refinement on it is unsound if two
unfilled cells compare equal — two states could merge on the strength of two
futures neither of which has been computed. Make every unfilled cell **unique
to its own (state, class)** in `state_sig` (`src/opt/minimize.c:39`), and no
state carrying an unfilled row merges with anything, no state transitioning
into one merges with a state transitioning elsewhere, and the fixpoint
propagates the exclusion backwards. What remains merging is precisely the
closed subgraph. **Every merge is therefore one the final pass would also
have made** — the premise §1.3(c)'s byte-identity argument needs.

**Then the rest of it.** Merging mid-construction means renumbering live
states, and the numbering is load-bearing in five places the existing pass
never has to think about, because it runs when nothing is live:

1. **The worklist cursor.** `for (int si = 0; si < d->n; si++)`
   (`src/ir/dfa.c:1284`) indexes by number; a renumber invalidates `si`.
2. **The intern hash table** (`src/ir/dfa.c:827`, `:835`) must be rebuilt —
   which is only possible if the NFA lists still exist, i.e. (3).
3. **The pass destroys what construction still needs.**
   `src/opt/minimize.c:183`-`:186` sets every survivor's
   `up[u].nlist = 0; up[u].list = NULL`, on the stated ground that the lists
   are dead afterwards. During construction they are not: the worklist reads
   `d->st[si].up[cu].list` (`src/ir/dfa.c:1310`) and `view_same` (`:849`)
   memcmps them on every intern.
4. **The start-state family.** `s0`, `s1u[]`, `s1g[]` remap at
   `src/opt/minimize.c:202`-`:215`; the file's own comment records that
   forgetting one leaves *"a wrong start state rather than a missing one"*.
5. **The caps.** `d->n` shrinks, so the state cap (`src/ir/dfa.c:886`) now
   measures something different and the refusal set moves (§1.4).

**Cost, and K25.** `known_issues.md` K25 records minimization at **15.3 s of a
15.4 s compile** on `a{0,25000}` — Moore needs O(n) rounds on a chain. Running
it k times multiplies that, and the threshold predicate that controls it is
another `BAIL_KEEP_PCT`-shaped calibration hazard.

**The finding that decides A.** Under the sound rule the merges available are
exactly the closed subgraph's — and on the K18 shapes I expect that set to
stay small until construction is nearly finished, because the counter's states
keep the frontier reachable. **If that is right, A is simple and does almost
nothing on the population that motivated the study.** Reasoned, not measured;
M1 tests it.

A weaker rule that would merge more — treat an unfilled cell as a wildcard —
**is unsound and unsound silently**: wildcard-compatibility is not transitive,
so it is not an equivalence relation and the fixpoint is not well defined.

### 3.6 A′ — merge states with identical finished rows (Tier 2)

**New in this revision**, and it is the smallest genuinely-online merge in the
document. When a state's row is completed in the worklist, hash it on
(accept bits across `UPC_N`, the whole `tr[]` row, `eolvar`, `endvar`) into a
second table beside the existing `d->tab`, in the idiom `dhash`/`tab_insert`
already establish (`src/ir/dfa.c:809`, `:827`). A hit is an equivalence, with
no fixpoint and no theory: identical targets and identical accepts mean
identical residuals. Merging can make *another* pair's rows identical, so a
small worklist propagates it.

- **Exact**, unconditionally. This is the one candidate whose soundness needs
  no argument a panel could attack.
- **40-70 lines**, no new file, no preorder, no partition, no O(n) rounds, no
  K25 multiplier.
- **It can record an alias instead of renumbering**, deferring the compaction
  to the final pass's existing renumber — which sidesteps all five of §3.5's
  hazards at the price of not shrinking `d->n` for the caps.
- **It saves no construction work** (Tier 2: the row is already expanded), and
  it does not shrink the artifact beyond what the thorough pass already
  achieves. Its value is that the count is available *during* construction.
- **But the count it makes available is the wrong kind.** Per §3.1, a
  partially-merged count is an upper bound on the explored part's final
  blocks, not a lower bound on the final total — so **A′ does not license a
  bail**, and it does not solve lim2's problem. That is worth stating flatly
  because A′ looks like it should.

A′ is the honest answer to "what is cheap and safe to take as states are
generated". It is also, by itself, not worth building: it costs little and
buys little. Its real role is as a **component of C** (§3.8), where the same
row-hash is the registry's confirmation step.

### 3.7 B — drop dominated positions from each subset (Tier 1)

The brief's "reduce the NFA/positions by simulation before determinizing", in
the form that fits this construction.

**The mechanism.** Compute once per machine, before the worklist, a preorder
`⊑` on the NFA's `N_CLASS` positions such that `p ⊑ q` implies every
continuation `p` accepts, `q` accepts too, at the same position. Then in
`closure` (`src/ir/dfa.c:771`) drop a position when one already in the list
dominates it. §2.2's literature calls this the right-invariant preorder /
simulation reduction; §2.2's symbolic-automata work is the version that fits
pcrec's byte-equivalence-class alphabet.

**Why this shape could crush K18.** The counter tail is `(X(X(X)?)?)?`
(`src/ir/nfa.c:744`): a position in copy *j* has strictly more iterations
remaining than the same position in copy *i > j*, so `copy_i ⊑ copy_j` for
`j < i` — the inclusion §1.2 established, now used as a reason to *delete*.
A subset that reached copies 4 through 30 reduces to `{copy 4}`, and the
number of reachable subsets falls from the number of *ranges* to the number of
*minima*: roughly quadratic to roughly linear in the count. That is the right
order of magnitude for 27,575 → 1,010.

It is also, with C, one of only two candidates that **reduces the K7 charge**
(§1.4), because it acts before `intern` sees the list.

**It does not reach the minimal machine.** `{copy 4}` and `{copy 5}` remain
distinct states. The thorough pass is still needed and still does real work,
so **B's second pass is not optional**. Expect the ratio to fall from ~27× to
something small but not 1×.

**Three pcrec-specific soundness conditions, each a way to be quietly wrong.**

1. **Domination must hold in every view.** A position's future is an accept
   answer in each of `UPC_PLAIN`/`UPC_WORD`/`UPC_NL` and in each of
   base/EOL/END (§1.3(a)). A preorder computed without the assertion states
   (`N_WORDB`, `N_NWORDB`, `N_EOL_M`, `N_BOT_M`, `N_END`, `N_GSTART` —
   `src/ir/dfa.c:1153`-`:1171`) would dominate across a context boundary and
   answer a `\b` or a `(?m)$` with the wrong bit.
2. **The K18 open-loop context breaks context-freeness of "the future".**
   `src/ir/dfa.c:207`: a position's behaviour inside a closure depends on
   which loops are open on the path that reached it. So "the language of
   position *p*" is not well defined independently of context, and a preorder
   computed on the bare NFA may fail under some contexts. Either condition the
   preorder on the open-loop context (much more expensive; contexts are
   discovered during closure, not before), or restrict it to pairs no loop
   entry separates — easy to state, easy to get subtly wrong.
3. **Priority.** I believe order is safe and record the argument so it can be
   attacked. The DFA route answers spans, not captures (§1.3(a)); a state's
   output is a set of accept bits. If `p ⊑ q` and both are in the list, every
   accept `p` contributes `q` contributes at the same position, so no accept
   bit changes whichever comes first in preference order; and priority pruning
   truncates at the first ACCEPT, so dropping `p` can only lengthen the
   surviving list, never move where it truncates. **This is the claim I would
   most want a D6 panel to attack** — the leftmost-first machinery in this
   file has already produced K1, K17 and K18 against arguments that looked
   this clean.

**Cost.** The simulation preorder is classically `O(|Q|·|δ|)`, on NFAs that
reach tens of thousands of states precisely when it is needed. A *bisimulation*
quotient (Paige–Tarjan, near-linear) is cheaper and **is not the same thing**:
bisimilarity merges copies only if their futures coincide exactly, which for an
unrolled counter they do not, so I expect it to buy approximately nothing here.
Worth stating because it is the intuitive first reach and it is the wrong one.

**One tempting shortcut, named so it is not silently taken.** The dominance
that matters on K18 shapes is "copy *i* is dominated by copy *j < i* of the
same repeat", which the NFA builder knows by construction and could stamp for
free. That is a special case of a general fact, and the standing rule
(memory `pcrec-general-mechanisms-not-special-cases`, D75's addendum) is that
the general form gets built. It is legitimate as an implement-then-replace
prototype for M2, where the only question is *how much is there to win*; it is
not legitimate as a landing.

### 3.8 C — full online compaction (Tier 4)

Nicol & Frohme's construction (§2.3): an equivalence registry that tracks and
unifies language-equivalent states as they are discovered, with convexity
closures and simulation as additional reducers and a threshold predicate that
interrupts exploration to minimize. Exact, published, in a 2026 venue, and it
reports its gains *"especially [in] worst-case scenarios"* — the population
pcrec cares about.

**Promoted to first-class by Frank's clarification, and on the merits it earns
the place**, for three reasons the original draft under-weighted:

1. **It is the only candidate for which the second pass is genuinely
   optional.** A registry that unifies equivalent states as they are
   discovered *is* the canonization; the machine it leaves is minimal or near
   it, so skipping the thorough pass costs little size (§3.1's objection
   evaporates) — and at that point **raw equals emitted and lim2's projection
   is exact by identity**, no margin and no bound reasoning. Frank's
   optional-second-pass idea and lim2's margin problem solve each other in
   exactly this configuration and in no other.
2. **It is one of only two candidates that makes construction cheaper**
   (§3.2's criterion): a Tier-4 merge can be made before either state's row is
   expanded, so 96% of the k18 witness's rows would never be walked.
3. **It subsumes A′ and composes with B.** A′'s row-hash is the registry's
   confirmation step; B's preorder is exactly the "simulation" the abstract
   names as an additional reducer. So the cheap candidates are not wasted work
   if C is where this ends up — they are C's components, which makes an
   incremental route to C real rather than rhetorical.

**Against it:** it is a new subsystem, it replaces rather than extends
`src/opt/minimize.c`, and it lands every one of §3.5's five renumbering
hazards plus the registry's own invariants (a hypothesis that must be split
on refutation is a data structure where being wrong is silent by
construction). **I have not read the paper past its abstract**
(§2.3, `unverified`), so "500+ lines and a new file" is a guess, and I cannot
say what its overhead is on the ordinary patterns that are 99% of the corpus.
Its authors publish an open-source implementation. Reading both is cheap, needs
no box time, and is now the **first** item in §5's plan rather than the last.

### 3.9 The two-pass verdict

Frank's three questions, answered directly.

**Which equivalences are the cheap-and-safe incremental wins?** Tier 2 (A′,
identical finished rows) unconditionally — it needs no new theory and its
soundness is one line of algebra. Tier 1 (B, dominated positions) subject to
§3.7's three conditions, and it is the cheaper-construction one of the two.
Together they are perhaps 250-350 lines and they are the honest content of
"take the easy wins as states are generated".

**Which need the thorough pass?** Everything at Tier 3 and above, and that
includes the whole of the K18 case: two subsets are equivalent there because
the *union* of their residual languages coincides, and no local, bounded-depth
check can see that. Tiers 1+2 alone would leave most of the 97% shrink on the
table.

**Is the incremental result alone a usable artifact?**

| property | Tiers 1+2 only | Tier 4 (C) |
|---|---|---|
| correct? | **yes** — §3.1: an unminimized DFA is already a shipped, ordinary outcome | yes |
| smaller? | somewhat; on the k18 witness it would leave most of a 27× on the table | ≈minimal by construction |
| size bound honest? | **no** — a partially-merged count is an upper bound on the explored part, and a bail needs a lower bound (§3.4) | **yes, and exactly** — raw *is* emitted, so the projection is an identity |
| second pass optional? | no — skipping it enlarges the k18 artifact ~27× | **yes** |

So the shape Frank described — easy wins during, thorough pass after, second
pass optional if expensive — **is coherent, and it is a description of
candidate C.** With the cheap tiers alone the second pass is not optional; it
is where nearly all the shrink lives. That is not an argument against starting
with the cheap tiers: A′ and B are C's own components, so building them first
is a real incremental route rather than throwaway work. It is an argument
against expecting the cheap tiers to deliver the property that makes the whole
manoeuvre worth doing.

## 4. Brittleness (Frank's directive 3, and his stated concern)

Four candidates actually compact: **A′** (identical finished rows), **A**
(periodic partial minimization), **B** (dominance pruning) and **C** (the full
online registry). This section takes each apart by failure mode and asks the
project's own question of each one: *what would have to be true for a check to
fail, and who chose that input* (`docs/dev/learnings.md` §3).

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
patterns".** A's real problem is not brittleness. It is that §3.5 expects it
to merge almost nothing on the population that motivated the study, and that
prediction is untested. **Measure before building** (§5, M1).

### 4.3 Candidate B — dominance pruning inside the closure

| # | failure mode | caught by | new check needed |
|---|---|---|---|
| B1 | the preorder dominates across an assertion boundary, so a `\b` / `(?m)$` / `\z` accept bit is wrong in one view only | `tests/assertions/` and PC-3 — **only if a corpus pattern combines an unrolled counted repeat with an assertion.** That is a cross-product cell, and learnings §3 records this exact failure ("a corpus needs the axes of the MECHANISM under test, not of the exemplar that motivated it; the cross-product cell neither of two large honest sweeps generates") | **yes, and it is the load-bearing one:** a generated corpus of {counted-repeat shapes} × {`\b`, `\B`, `(?m)^`, `(?m)$`, `\z`, `\Z`, `\G`}, oracle-verified against libpcre2. It does not exist today |
| B2 | the K18 open-loop context makes "the language of a position" context-dependent, so a preorder computed on the bare NFA is wrong under some contexts | the four `k18_*.rxt` files' 1,459 guard cases — the strongest existing check for this hazard, and `DFA_INVARIANT` (`dfa.c:250`) aborts in shipped builds if loop nesting stops being proper | **yes:** sabotage rows planting an over-relating preorder, asserting the k18 suites go red. If they stay green that is a finding about the population, not a pass (learnings §3) |
| B3 | priority: §3.7's condition 3 is an argument, and the leftmost-first machinery in this file has already produced K1, K17 and K18 against arguments that looked this clean | the corpus's spans, `counterk`, the lazy-preference witnesses `src/ir/nfa.c:741` names (`(?:ab\|a){0,2}?b`) | a preference differential over dominated-position shapes specifically — lazy and greedy spellings of the same counted repeat |
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

### 4.4 Candidate A′ — identical finished rows

The short table, because there is genuinely little here.

| # | failure mode | caught by | new check needed |
|---|---|---|---|
| A′1 | the row hash collides and two unequal rows are treated as equal | nothing would notice a bad *comparison* — but the fix is the existing idiom: `intern` (`src/ir/dfa.c:871`) already confirms every hash hit by full comparison, and A′ must do the same. A hash-only merge would be a defect, not a design choice | no, provided the confirm-on-hit rule is followed |
| A′2 | a row is hashed before it is complete (`tr[cl] == -2` still present) | nothing — it would merge on an unfinished row, which is §3.5's unsound-wildcard failure wearing a different hat | **yes:** an assertion that every cell is filled at the hash site, in `dfa.c`'s existing `DFA_INVARIANT` idiom (`:250`), which survives a caller's `-DNDEBUG` |
| A′3 | aliasing without renumbering leaves a stale id somewhere (`s0`/`s1u[]`/`s1g[]`, `eolvar`, `endvar`, a cached `tr` target) | the corpus's spans would go wrong loudly, and `run_*_identity.sh` would show bytes moving | no |
| A′4 | it changes nothing at all — the merges it finds are ones the final pass finds anyway | **nothing.** A mechanism that is a no-op passes every check in the tree | **yes, and this is the real risk:** a census counting how many merges A′ makes that the final pass does not make *earlier*, over the corpus. A′'s whole claimed value is timing, so timing is what must be measured |

**Verdict on A′: not brittle, and not, on its own, worth building.** Its
failure modes are either trivially avoided by following an existing idiom or
loud. Its real risk is A′4 — being a no-op dressed as a mechanism — which is
the D77 question, not a brittleness question. Build it as a component of C
(§3.8), or not at all.

### 4.5 Candidate C — the full online registry

| # | failure mode | caught by | new check needed |
|---|---|---|---|
| C1 | a hypothesis is never refuted because the refuting input is never explored, so two inequivalent states stay merged | the corpus's spans — **only where the mechanism fires**, and a registry fires everywhere, which is actually the *good* case for coverage compared with A's threshold | **yes:** the same forced-mode-plus-whole-corpus sweep A1 needs, plus a **differential against the existing pipeline** — compile every corpus pattern both ways and assert the two minimized machines are isomorphic. That differential is C's single strongest available check and it has no analogue for A or B |
| C2 | the split-on-refutation propagation misses a transitive consequence (a merge that depended on a merge that was just undone) | nothing, and this is the failure mode I would expect a registry to have | **yes:** an invariant re-check at the end of construction — every surviving merge re-verified against the finished machine, in the `DFA_INVARIANT`/`abort()` idiom, on by default. Expensive, and it is exactly the "prove the mechanism did what it claimed" check the cheaper candidates cannot afford but this one can, because it replaces the thorough pass and inherits its budget |
| C3 | inherits every one of §3.5's five renumbering hazards, since it renumbers continuously rather than periodically | items 1-4 fail loudly (wrong start state, wrong spans, corrupt worklist); item 5 (the caps) fails silently and permissively | the refusal-set manifest, as for A2/B7 |
| C4 | the second pass is skipped (§3.9) and the artifact is *larger* than today on some population nobody looked at | `tests/size/`'s artifact-size log and tripwire — this axis is already built and already loud | no. This is the one place where deciding to skip the thorough pass is well covered before the fact |
| C5 | overhead on the 99% of patterns that gain nothing — a registry pays per state on every compile | `tests/bench/run_bench.sh`'s COMPILE-SPEED budget, calibrated for cliffs | **yes:** the same corpus-wide compile-time delta B6 needs. One check for both |
| C6 | emitted bytes move nearly everywhere, since the state set changes wherever anything merges early | identity gates, loudly | no — but the landing is an `abi` bump and a re-pin at every reader found by grep (D76/D94), and it will be a large one |

**Verdict on C: the most dangerous mechanism here and the best-checkable
one, and those are not in tension.** C2 is a genuinely nasty failure class —
a hypothesis structure where being wrong is silent by construction. But C is
also the only candidate that can be checked by **isomorphism against the
existing pipeline over the whole corpus**, because it computes a quantity the
current code already computes independently. A and B have no such reference;
their correctness has to be argued and then sampled. C's can be *diffed*.
Combined with C4's already-built size axis, C's brittleness is lower than B's
despite its size — provided C2's end-of-construction invariant re-check is
built in from the start rather than added after the first defect.

### 4.6 The null candidates' brittleness, briefly

N1 (a work budget) has one failure mode: it refuses a pattern that would have
compiled. That is loud, deterministic, and caught by the refusal-set manifest
of A2/B7 — which N1 needs built anyway. N2 (project from the closed subgraph)
cannot be unsound as a lower bound (§3.4), so its only failure is being
*vacuous*, which is a silent failure of a different kind: the bail simply
never fires and lim2's 10-20 s refusals come back. That is caught by lim2's
existing cost check (`run_lim2_sizecap_projection.sh`'s check 2, the wall-time
ceiling that fails when the bail stops firing) — a check that already exists
and was already designed for exactly this.

---

## 5. Recommendation, and the measurement that would trigger building it

### 5.1 Recommendation

**Separate the two problems first — they are not the same problem — then
read the paper, then measure.** In order:

1. **Fix lim2's margin problem on its own, now, with N2 or N1.** §3.1's
   finding is that the size bail needs *provable inequivalence* while
   compaction proves *equivalence*: they are opposite proofs, and only the
   configuration in §3.9's right-hand column collapses the distinction.
   So the bail should not wait on the compaction question at all. N2's
   closed-subgraph block count is a sound lower bound with no percentage in
   it, retiring lim2 §10's unrepresentable "194.124 points"; it changes no
   emitted byte and is 80-120 lines. **Conditional on M1** showing the closed
   set is not empty — if it is, fall back to N1 (a deterministic work budget),
   smaller still, no size claim at all.
2. **Read Nicol & Frohme (M5) before deciding anything else.** Frank's
   clarification makes full online compaction a live option, and C is the
   only candidate with the property that makes the whole manoeuvre worth
   doing — an optional second pass, and with it an *exact* size projection.
   Its assessment here rests on an abstract. **This is now the first item,
   not the last**: it costs no box time, and it is unreasonable to rank a
   first-class candidate on material nobody has read.
3. **Take M1 and M2.** M1 decides A outright and tells N2 whether it is
   vacuous. M2 sizes the prize for B and, because B's dominance preorder is
   the "simulation" C's own abstract names as a reducer, it also puts a floor
   under what C could achieve. If M2's ratio stays above 10×, the honest
   answer to the charter's question is "no, not affordably" — a legitimate
   outcome to record rather than route around.
4. **Then choose between B and C on the numbers**, with §4.5's verdict in
   hand: C is the more dangerous mechanism and the better-*checkable* one,
   because it can be diffed for isomorphism against the existing pipeline
   over the whole corpus and B cannot.

**Do not build A.** It is the one candidate this study can rank down on
merits rather than on missing measurements: it is Tier 3, so it saves no
construction work (§3.2), its available merges are the same closed subgraph
N2 only *reads*, and it lands all five renumbering hazards to get them. If
M1 says the closed set is large, N2 gets the benefit at a third of the cost
and none of the risk; if M1 says it is small, A does nothing. There is no M1
outcome that favours A.

**Do not build A′ alone.** It is exact, tiny and safe (§4.4), and it is also
Tier 2, so its merges arrive after the work is already paid for and its count
is the wrong kind for a bail (§3.6). Build it as C's confirmation step, or
not at all.

Frank's three questions, answered where he asked them: §3.1 (correctness or
optimization), §3.2 (which wins are cheap and safe), §3.9 (is the incremental
result usable alone). The short version is that **his shape is coherent and
it describes candidate C** — with the cheap tiers alone the second pass is
not optional, because that is where nearly all the shrink lives.

Frank's original directive 3 asked whether this can be done without getting
brittle. **For B: yes, but only after the cross-product corpus of §4.3
exists. For C: yes, and more cheaply than for B**, provided §4.5's C2
end-of-construction invariant re-check is built in from the start rather
than added after the first defect.

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
is the special case §3.7 names and forbids as a landing; it is legitimate
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

**M5 — read the literature properly. TAKE THIS ONE FIRST.** Nicol & Frohme,
arXiv:2505.10319 / TACAS 2026, in full, plus their open-source library: the
operational definitions of "equivalence registry", "convexity closure" and the
threshold predicate; the experimental numbers; the overhead on easy inputs;
and specifically **whether their result is minimal or merely reduced**, since
§3.9's whole right-hand column depends on it. No box time and no acceptance
bar, but it is the gate on ranking C honestly — it retires four `unverified`
marks in this document, including the ones under the candidate Frank's
clarification promoted.

**M6 — is the second pass worth skipping? (decides §3.9's open cell, and only
after M5/M2 pick a mechanism).** For whichever compaction is prototyped,
compile the corpus twice — thorough pass on, thorough pass off — and read
artifact size and compile time both ways, in the shape `tests/size/`'s log
already has.

- Rows: the whole `.rxt` corpus plus the altwide set plus the k18 witnesses.
- **Bar:** the second pass may be made optional only if, with it skipped,
  **no** artifact grows by more than a few percent and the k18 witness in
  particular does not regress toward its 27×. Anything else and the pass
  stays mandatory, the projection stays a bound rather than an identity, and
  §3.1's reframing stands: the bail is a separate row solved by N1/N2.
- This is also where §3.1's one unsettled code question gets answered — does
  [OPT-5]'s scan edge require *minimality* or only *finality*
  (`src/opt/scanedge.c:43`'s five preconditions against
  `src/core/internal.h:4387`'s "it needs the canonical state set")? A
  prototype answers it in an afternoon; this study could not.

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

- That candidate C reaches a *minimal* machine rather than a merely reduced
  one. §3.9's "second pass optional" column depends on that, and it rests on
  the word "canonization" in an abstract. M5 settles it.
- That [OPT-5]'s scan edge tolerates an unminimized machine. §3.1 shows the
  documented dependency is an *ordering* one and that the pass's five
  preconditions are local shape tests, but "it needs the canonical state set"
  is not disproved by that, only unexplained. M6 settles it.
- That A′ is worth building. It is exact and cheap; §3.6 argues it buys
  little alone, which is a judgement, not a measurement.
- That B is sound. §3.7's three conditions are stated as obligations, and
  condition 3 (priority) is an argument I want attacked.
- That the byte-identity sketch in §1.3(c) holds. It is a plausibility
  argument with three named holes and it must be measured.
- Anything about Nicol & Frohme's algorithm beyond its abstract.
- Any number about pcrec that was not read from the code or from lim2's
  report. **No compile, no `make`, and no benchmark was run by this lane**;
  every quantitative claim here is either cited from `lim2_report.md`, from
  `known_issues.md`, from `limits.def`, or marked as an expectation to be
  measured.

---

## 6. M5 — the paper, read

Lane `m5paper`, worktree `worktrees/m5paper`, branch `lane/m5paper`,
**2026-09-04**. READ-ONLY: no `make`, no compile, no benchmark, nothing
under `src/` or `tests/` written. This section discharges §5.2's M5 and
retires the `unverified` marks in §2.3 and §3.8.

**What was read.** Nicol & Frohme, *Deconstructing Subset Construction:
Reducing While Determinizing*, arXiv:2505.10319v2 [cs.FL], 10 Apr 2026,
CC BY 4.0, in full via the arXiv HTML (`https://arxiv.org/html/2505.10319v2`)
— all of §1-§6, Algorithm 1, Definitions 1-4, Tables 1-3 and the
Data-Availability Statement. To appear in TACAS 2026, LNCS,
doi:10.1007/978-3-032-22749-2_20. Figures 1 and 2 are survival (cactus)
plots and were **not** readable as data: the HTML carries them as images,
so every claim below about their content comes from the paper's own prose
about them and is marked where it does. Also read, from the reference
implementation `github.com/jn1z/OTF` (default branch `main`, last push
2026-05-29): `README.md`, `CHANGELOG.md`, `LICENSE.txt`, `pom.xml`, and the
sources `OTFDeterminization.java`, `OTFCommandLine.java` (the driver) and
`PTInitializers.java` (the partition initializer). The Zenodo artifact
(doi:10.5281/zenodo.18163403) was **not** downloaded or run.

### 6.1 The headline, first, because it inverts §3.9

**Candidate C's defining property is false.** The paper's construction does
*not* leave a minimal machine; a final, full minimization is mandatory, and
the paper says so in its own words at the end of §3.1:

> "While $A'$ may be minimized during exploration, the threshold predicate
> might not trigger in the last iteration. **Thus, a final minimization is
> necessary for correctly canonizing $A$.** This step is omitted from
> Algorithm 1 to allow for utilizing the presented technique directly in
> [9]'s approach as well (cf. Section 5) which does not require an explicit
> minimization."

The reference implementation agrees without qualification. `doOTF`'s own
javadoc calls its return value *"(Partially) minimized DFA; output of
Algorithm 1"* (`OTFDeterminization.java`), and the driver runs a full
Hopcroft pass on it unconditionally, on every configuration:

```java
final DFA<?, Integer> otfDFA = OTFDeterminization.doOTF(nfa.powersetView(), alphabet, threshold, registry);
final CompactDFA<Integer> minimizedDFA = HopcroftMinimizer.minimizeDFA(otfDFA, alphabet);
```

(`OTFCommandLine.java`, method `CCL`.) The paper's §5.1 "Parameters" says
the same from the other side: *"All configurations use Hopcroft's algorithm
[22] to minimize either the intermediate automata (OTF) or the final
automaton (OTF, SC)."* — OTF appears in both lists.

So §3.8's reason 1 and the whole right-hand column of §3.9's table are
withdrawn. **The second pass is not optional under this construction, raw
does not equal emitted, and lim2's size projection does not become an
identity.** The one configuration in which "Frank's optional-second-pass
idea and lim2's margin problem solve each other" does not exist in the
published work. §6.6 re-ranks C on what is left.

### 6.2 What the algorithm actually is (answer 1)

**In two sentences.** OTF is classic subset construction with two changes:
the metastate → DFA-state map is mediated by an *equivalence registry*
whose lookup may answer with an already-built state that is merely
*language-equivalent* to a metastate never seen before, so that metastate is
never created or explored; and exploration is periodically interrupted by a
*threshold predicate*, at which point the partial DFA is minimized by
Hopcroft with every unexplored state pinned in its own block, and each
equivalence the minimizer finds is handed back to the registry to widen
future lookups. The paper states both in §3: *"First, the NFA state space
exploration may be repeatedly interrupted by a threshold predicate... Second,
the mapping between NFA metastates and DFA states... is handled by an
equivalence registry."*

**What is tracked per state.** Nothing is tracked *on* the DFA state. The
state is an integer counter (Algorithm 1 lines 21-23) and the DFA is an
ordinary `CompactDFA`. Everything is in the registry, whose interface is
Definition 4 — three operations only:

> GET$(Q)$ returns a state $q\in S'$ such that $L(Q)=L(q)$. The method may
> also return undefined if it is not aware of such state yet.
> PUT$(Q,q)$ links the behavior of metastate $Q$ to state $q$ with the
> precondition that $L(Q)=L(q)$.
> UNIFY$(q_1,q_2)$ informs the registry about the language equivalence of
> states $q_1$ and $q_2$, which may affect future results of the GET method.

The paper is explicit that a hash-based one-to-one registry with `UNIFY` as
a no-op reproduces classic subset construction exactly (§3, after Def. 4;
repeated in §3.2). The registry *is* the mechanism.

**What is merged, and on what relation.** **Language equivalence** — not
bisimulation, not simulation. Def. 4's contract is stated as $L(Q)=L(q)$
throughout, and the CCL registry's inference rests on the set identity
$L(A\cup B)=L(A)\cup L(B)$ (§4.1, attributed to [6]), which follows from
$L(Q)=\bigcup_{q\in Q}L(q)$ in §2.1. Simulation appears in exactly one
place and in a *subordinate* role: the CCLS registry (§4.2) precomputes the
similarity preorder on the input NFA and uses it to *prune* and *saturate*
metastates before lookup, so that a lookup key is normalized. That is a
device for finding more equivalences faster, not the equivalence being
tested.

**When a merge is decided — two distinct events, and only one of them saves
work.**

1. **At lookup, before the metastate exists** (Algorithm 1 line 19,
   `n' ← getR(N)`). If the registry can prove $L(N)=L(n')$ for an existing
   state $n'$, no state is created, nothing is pushed on the stack
   (lines 20-29 are skipped), and $N$'s successors are never computed. **This
   is the only part of OTF that reduces exploration**, and it is a Tier-4
   merge in §3.2's vocabulary: decided before *either* row is filled.
2. **At the interrupt, strictly after a row is filled** (Algorithm 1 lines
   32-33: `E' ← E' ∪ {c'}` then `if threshold(A')`). The intermediate
   minimization runs on completed rows only, and unexplored states are
   pinned apart by construction (lines 34-42: `sig[i] = i` for a state not in
   $E'$, a Boolean accept value for one in it). The paper's §3.2 states the
   consequence: *"unexplored states are assigned unique blocks in the initial
   partition, ensuring they remain distinct until their behavior is fully
   determined. Consequently, minimization never merges states with incomplete
   information."* The reference implementation adds a condition the paper's
   Algorithm 1 does not show: `if (complete && threshold.test(out))`, where
   `complete` is false if *any* successor of the state just popped was newly
   created (`OTFDeterminization.java`) — so a minimization is attempted only
   at a moment when the frontier did not grow.

**This is exactly the study's candidate A, with the study's own soundness
rule.** §3.5 derived "make every unfilled cell unique in `state_sig`" from
first principles; Algorithm 1 lines 34-42 are that rule, published. The
study's §3.5 is therefore *correct as a rule* and is confirmed by an
independent source. One consequence of it, though, is stated too
pessimistically in §3.5 and that misstatement is what killed A there — see
§6.6.

**What it guarantees about the result.** Language equivalence to the input
NFA, and nothing stronger about the loop's own output. The paper gives **no
theorem and no lemma** anywhere; §3.2 "Termination and Correctness" is four
paragraphs of prose whose argument is that both modifications preserve what
classic subset construction already guarantees, and §3.3 explicitly declines
a real analysis. Minimality of the *final* result comes from the final
Hopcroft pass, exactly as it does in pcrec today (`src/opt/minimize.c:69`
onward, called at `src/core/compile.c:1134`-`:1135`).

### 6.3 The property the study bet on (answer 2)

**It does not hold**, per §6.1. What remains, stated precisely:

- **The result of the exploration loop is reduced, not minimal.** The gap
  has two named sources in the paper's own text. (i) The threshold may not
  fire near the end, so states created after the last interrupt were never
  offered for merging (§3.1's closing paragraph, quoted in §6.1). (ii) Even
  immediately after an interrupt, states kept apart *only* because they
  reach distinct unexplored states are not proved distinct; when those
  successors are later explored and merged, their predecessors become
  mergeable and stay unmerged until the next interrupt or the final pass.
- **The paper measures this gap as a headline metric rather than
  eliminating it.** §5.1 "Measurements": *"The overhead describes the
  difference between the number of states of intermediate automata and the
  final DFA... For OTF and BRZ-OTF, we use the maximum size of the
  intermittently minimized automata as reference point."* That quantity is
  lim2's quantity — raw-carried minus emitted — and OTF is presented as
  *shrinking* it, never as driving it to zero. The strongest claim in the
  evaluation is conditional and partial: *"For SC and OTF, simulation boosts
  performance both by improving runtime and reducing overhead, **sometimes to
  the point of not introducing any redundant states at all**"* (§5.2,
  Walnut). "Sometimes", on some systems, and in the *simulation-bearing*
  configurations — which are candidate B, not candidate C.

**Can a size bail use the reduced count as an exact or a lower bound? No,
on both counts, and the reason is the one §3.1 already gave.**

- Not exact: §6.1.
- Not an upper bound on the final total: exploration continues after any
  interrupt, so more states are still coming.
- **Not a lower bound**: two blocks of an intermediate partition may be
  separated only by witnesses that run into distinct unexplored states.
  Those separations are not proofs of distinguishability, so the block count
  is not a count of provably-distinct states. §3.1's finding stands
  unchanged: compaction proves *equivalence*, a bail needs proved
  *inequivalence*, and OTF supplies no monotone quantity of the second kind.

The paper offers nothing in this direction and says so structurally: §1
contrasts the canonization problem with universality and inclusion, where
antichains let you stop early, and concludes *"For the canonization problem,
however, the construction of the full DFA is necessary."* §2.4's
Baburin–Cotterell hardness result is not disturbed.

**One observation for lim2, marked as a sketch and not a result.** The
monotone quantity is distinguishability, and the sharpest sound lower bound
is not necessarily N2's closed subgraph: a pair separated by a witness path
whose every transition is *filled* is genuinely distinguishable even if
unexplored states exist elsewhere in the machine. Turning that into a
*count* needs pairwise-distinguishability across blocks rather than a
partition (wildcard-compatibility is not transitive — §3.5's own warning),
so it is not obviously a refinement step. Named so it is not lost; **not
settled here, and nothing in the paper bears on it.**

### 6.4 Cost (answer 3)

**Complexity, as the paper states it: it does not.** §3.3 declines the
analysis outright — *"Providing a detailed analysis of OTF's complexity is a
challenge as it highly depends on user-provided parameters... As a result,
we only want to briefly sketch the worst-case performance"* — and the sketch
is that the main loop may still iterate exponentially often, *"On top of
that come the costs of registry management, threshold evaluation, and
minimization, which – in the worst case – results in additional overhead
compared to classic subset construction."* There is no amortized result, no
bound relating work to the compression ratio, and no theorem.

**Per-operation costs, as stated per registry:**

| operation | CCL (§4.1) | CCLS (§4.2) |
|---|---|---|
| PUT | amortized constant (hash) | + prune and saturate, linear in $\|Q\|$ with cached simulation |
| UNIFY | merge two lattices; dominated by $\mathcal{O}(\|M_1\|\|M_2\|)$ subset comparisons on the minimal-element antichains | identical to CCL |
| GET | hash hit if singleton; otherwise scan lattices for one covering $Q$ from above and below. Worst case *"quadratic (in the number of lattices and the number of their minimal elements) number of subset comparisons"* (§4.1 Remarks) | prune first, then as CCL; *"the runtime is still dominated by the quadratic lookup process"* |

Preprocessing for CCLS is the similarity relation, $\mathcal{O}(|\delta|\cdot|S|)$
(§2.2, citing [32]); bisimilarity is $\mathcal{O}(|\delta|\cdot\log|S|)$ (§2.2,
citing [49]). §4.2's Remarks carry the warning the study's §3.7 arrived at
independently: *"Computing the simulation preorder can be prohibitively
expensive for large or dense NFAs, so the benefit of precomputing simulation
relations must outweigh the cost."* §5.1 records that they tried the LIGHT-
and HEAVY- reduction methods of [12] and *"found [them] to be impractical in
our benchmarks due to their worst-case performance on NFAs"*.

The threshold is adaptive (§5.1 "Parameters"): $t$ starts at 5000 and is
rescaled after each minimization by the ratio of the new to the previous
minimized size, so poor compression *lengthens* the interval between
minimizations and good compression shortens it. That is a self-calibrating
answer to §4.2's A7 hazard and is worth borrowing whatever else is.

**Measured results.** Two benchmark families, both on a server with two AMD
EPYC 7763 CPUs and 2 TB of RAM, single-threaded runs capped at 256 GB
(§5.1).

- **Use case 1, Walnut (§5.2):** 52 systems from Büchi-based arithmetic on
  automatic sequences, one-hour timeout. State counts min/median/max/mean =
  64 / 9,824 / 60,317 / 10,113; alphabet sizes 2 / 8 / 1,323 / 89. OTF
  *"canonizes notably more systems within the set timeout than SC"*, and
  OTF-S and BRZ-OTF canonize 44 and 45 systems respectively — not the same
  44 and 45, with only two canonized by neither. Minimization triggers
  (Table 2): OTF min 2, median 48, max 145, mean 50.29; OTF-S 0 / 9 / 105 /
  14.93; BRZ-OTF 0 / 2 / 27 / 4.61; BRZ-OTF-S 0 / 1 / 17 / 3.49.
- **Use case 2, random systems with modular structure (§5.3):** a
  Tabakov–Vardi variant with a modular partition of the state space,
  $n\in\{20,30,\dots,300\}$, ten seeds each, transition density 2, alphabet
  $k=\max(1,\lfloor\sqrt n\rfloor)$, 1000 s timeout. Triggers (Table 3):
  OTF 0 / 6 / 129 / 25.48, and the other three configurations within noise
  of it. The paper's own reading: OTF reduces overhead and improves runtime,
  *"though less dramatically, because the equivalence classes in this model
  are dominated by one class with a complex antichain, leading to slower
  searches"* — i.e. the registry lookup can eat the win.

**Overhead on easy inputs — asked for by §5.2's M5, and the answer is a
qualitative one.** The paper gives no percentage anywhere. The nearest
statement is §5.2's *"While the additional work of intermediate
minimizations results in somewhat similar runtimes for the best cases, its
positive impact on the more complex systems is evident"*, plus the abstract's
*"we are able to improve especially worst-case scenarios"* and the
conclusion's *"while being competitive for the remaining ones"*. So:
roughly neutral on easy inputs, by the authors' account, unquantified, and
on a population whose median system has 9,824 states. **It says nothing
about the cost of a registry on pcrec's median pattern, which builds a DFA
of tens of states.** §4.5's C5 and §5.2's M4 stand entirely unretired.

**Counted repetitions and bounded repeats: absent from the evaluation, and
so are regular expressions.** Neither benchmark family is regex-derived —
one is automatic-sequence arithmetic from Walnut, the other synthetic
modular NFAs. String matching appears in the paper exactly once, as a
motivating citation in §1 ([2], Aho–Corasick). **No K18 shape, no unrolled
counter, no `((?:[^a]{1,2}|.{0,2}?)+){0,8}`, nothing of the kind is
represented.** Worse for transfer: §5.3 states that the OTF idea is
targeted at *structure* — *"Random models like the ones by Tabakov-Vardi
[46] typically lack any structure which is what OTF is designed to
exploit"* — and whether an unrolled counted repeat's copy lattice is
"structure" in the sense CCL's convexity closure can exploit is exactly the
question the paper's evaluation does not answer. It is a plausible yes
(§3.7's inclusion chain over copies is a lattice), and it is **unverified**.

### 6.5 Fit to pcrec (answer 4)

The mapping first, then what breaks.

| paper | pcrec |
|---|---|
| NFA $A=(S,\Sigma,\delta,S_0,F)$, Def. 1, **no epsilon transitions** | `Nfa`, with epsilon structure; positions are `N_CLASS` byte-consuming states (`src/ir/dfa.c:1315`) |
| metastate $Q\subseteq S$ | `DView.list`, a **priority-ordered** id list (`src/core/internal.h:1158`), one per class-axis view |
| $\delta(C,i)$, Algorithm 1 line 18 | filter the source view's list by the class representative byte, then `closure` — `src/ir/dfa.c:1313`-`:1316` then `:771` |
| DFA state $q$, an integer from a counter (Algorithm 1 lines 21-23) | `d->n++`, creation order (`src/ir/dfa.c:994`) |
| registry PUT/GET, hash-based one-to-one baseline | `dhash`/`tab_insert`/`intern` (`src/ir/dfa.c:809`, `:827`, `:871`) — pcrec **is** the baseline registry the paper describes |
| $E'$, explored states | states with index below the worklist cursor `si` (`src/ir/dfa.c:1284`); every popped state's row is complete by `:1326` |
| intermediate minimize with `sig` (lines 34-42) | `pcrec_minimize_dfa` with `state_sig` (`src/opt/minimize.c:39`) and unexplored states pinned |
| final minimize | `src/core/compile.c:1134`-`:1135` |

**What pcrec would have to supply that it does not have. Five items, in
descending order of how fundamental they are.**

1. **A metastate that is a SET. This is the deepest obstacle and it is not a
   porting detail.** CCL's entire inferential power is the convexity closure
   of a join-semilattice whose join is $\cup$ and whose order is $\subseteq$
   (§2.3, §4.1 Eqs. 1-2). pcrec's state is a priority-ordered list compared
   by `memcmp` (`src/ir/dfa.c:849`), and the order is produced by the closure
   walk, not by the membership (`src/ir/dfa.c:533`, `:571`, `:771`). There is
   no $A\cup B$: the union of two ordered lists is not a state the
   construction can produce and its order is undefined. To build CCL on
   pcrec you would first have to prove that the order, the accept bits and
   the pruning are all functions of the underlying position set — which is
   §3.7's condition 3 (priority) restated over the whole lattice rather than
   over one dominated pair, and §3.7 already flags that argument as the one
   it most wants attacked.
2. **Pruning, which makes even the set-level identity fail on forward
   machines.** Forward machines run with `prune` on and the closure *"stops
   the instant ACCEPT is reached — lower-priority threads are pruned"*
   (`src/ir/dfa.c:1`-`:6`; the cut is `src/ir/dfa.c:655` and `:794`). The
   interned list is therefore a **truncated** closure, so it is not the
   closure of the pre-set and $L(Q)=\bigcup_{q\in Q}L(q)$ (§2.1) is not the
   semantics of the object pcrec interns. The reverse machine runs with
   `prune` off (D7, `src/ir/dfa.c:1`) and is closer to the paper's object,
   which is an interesting asymmetry: **the machine where lim2 measured the
   worst raw-vs-minimized shrink is also the one where the paper's algebra
   comes nearest to applying.**
3. **One key per state, not a tuple of five.** Def. 4's $Q$ is one metastate
   and $q$ one state. pcrec's identity is three ordered lists with three
   accept bits (`src/core/internal.h:1192`) plus two interned *variant state
   ids* (`:1193`, `:1207`), and the variants are interned **before** the base
   state (`src/ir/dfa.c:1126`, `:1132`, then `:1136`). A registry GET on the
   base tuple would therefore depend on registry decisions already taken for
   its own variants, and the convexity closure would have to hold
   componentwise *and* jointly. The paper has no analogue and the study's
   §1.3(a) obligation applies in full.
4. **A simulation preorder, for CCLS.** pcrec has none, and building one
   lands §3.7's three conditions unchanged — every view (`\b`, `(?m)$`,
   `\z`), the K18 open-loop context that makes "the language of a position"
   context-dependent (`src/ir/dfa.c:207`, `:329`, `:392`), and priority.
   Note this is candidate B: **the paper's SC-S configuration IS candidate B,
   and its OTF-S is candidate A plus B plus the generalization layer.**
5. **Epsilon transitions are NOT an obstacle**, and it is worth saying so to
   keep the list honest. `closure` is a deterministic function of the ordered
   pre-set and the machine's flags (`src/ir/dfa.c:771`, called at `:1104`),
   so Algorithm 1's $\delta(C,i)$ maps cleanly onto pcrec's filter-then-close
   and the key the registry would hold is the closed list pcrec already
   interns. The obstacle is item 1's ordering, not the epsilons.

**And the renumbering hazards, which the reference implementation dodges in
a way pcrec specifically cannot.** §3.5 listed five. OTF avoids most of them
by **never renumbering**: `updateDFA` redirects each merged state's
predecessors to the block representative, then pushes the dead id onto a
`stateBuffer` free list and reuses it for the next state created
(`OTFDeterminization.java`, `updateDFA` and the `stateBuffer.pop()` in
`doOTF`). That is elegant and it is **worse than useless for pcrec**: id
recycling destroys the property that a state's index is its creation order
(`src/ir/dfa.c:994`, `:806`), and creation order is what §1.3(c)'s entire
byte-identity argument rests on, via `minimize.c:161`'s renumber-by-first-
occurrence. So pcrec would face §3.5's hazards 1-5 in full, *continuously*
rather than periodically, and would additionally have to solve the one the
paper's implementation solved by a means pcrec cannot use. Hazard 3 is
unchanged and is the concrete blocker: `src/opt/minimize.c:185`-`:186` nulls
every view's list, and the worklist reads exactly those lists at
`src/ir/dfa.c:1310`. Hazard 5 is unchanged too: `d->n` feeds the caps at
`src/ir/dfa.c:886` and `:934`, so the refusal set moves.

One favourable note: **the alphabet fits.** The paper's systems have a median
of 8 input symbols and a maximum of 1,323 (§5.2), and its conclusion names
large alphabets as a known weak spot for the registries ([16], BDDs as
future work). pcrec's byte equivalence classes (`eqclasses`,
`src/ir/dfa.c:152`) are in the same range, so this is one axis where pcrec
is on the good side of the paper's envelope rather than the bad one.

### 6.6 Revised verdict on C (answer 5)

**C keeps its Tier-4 classification and loses its rank.** §3.2's taxonomy is
unchanged and is confirmed by the paper: OTF's GET-on-an-unseen-metastate
(Algorithm 1 line 19) is a genuine Tier-4 merge and is the only part of the
construction that reduces exploration. What changes is everything §3.8 built
on top of that.

**§3.8's three reasons, re-scored:**

1. *"It is the only candidate for which the second pass is genuinely
   optional"* — **false** (§6.1). Withdrawn in full, and with it the claim
   that raw equals emitted and lim2's projection becomes an identity.
2. *"It is one of only two candidates that makes construction cheaper"* —
   **confirmed** (Algorithm 1 lines 19-29), and it is the reason C is not
   dead.
3. *"It subsumes A′ and composes with B"* — **half right, and the wrong
   half is load-bearing.** C does not subsume A′; C *requires* **A**. UNIFY
   is called from exactly one place, the intermediate minimization
   (Algorithm 1 lines 43-45; in the implementation, `registry.unify` is
   reachable only from `otfMinimization`). Without periodic partial
   minimization the CCL registry learns nothing and degenerates to the
   hash map pcrec already has — the paper says so itself in §3.2: a
   constantly-false threshold plus a one-to-one registry *"coincides with
   classic subset construction"*. So **§5.1's "Do not build A" and any
   future "build C" are inconsistent**: A is C's evidence source. The only
   escape is CCLS's PUT-time prune-and-saturate, which needs no UNIFY at
   all — and that is candidate B wearing a registry's clothes, which is
   precisely the paper's SC-S configuration.

**The paper's Table 1 is a 2×2 of this study's own candidates**, which is
the single most useful thing M5 brought back:

| paper's name | this study |
|---|---|
| SC | today's pcrec — Tier 0, syntactic interning only (§3.2) |
| SC-S | **candidate B** (simulation prune/saturate on metastates) |
| OTF | **candidate A** + the CCL generalization layer |
| OTF-S | **A + B** + the generalization layer |
| BRZ / BRZ-* | Brzozowski, set aside for pcrec-specific reasons in §2.3 |

And the paper's own strongest size result lands on the **B** column, not the
C column: *"For SC and OTF, simulation boosts performance both by improving
runtime and reducing overhead, sometimes to the point of not introducing any
redundant states at all"* (§5.2). The configurations that occasionally reach
zero overhead — raw equals emitted, the property §3.9 wanted — are the
simulation-bearing ones.

**Revised ranking.** C moves from first-class to *"the most expensive route
to a benefit B may deliver more cheaply"*, on four grounds: its unique
property is false; it requires A underneath, whose five renumbering hazards
pcrec would take continuously and one of which the paper's implementation
solves by id recycling that pcrec cannot use (§6.5); its generalization
layer needs a set lattice pcrec's ordered, pruned, five-component states do
not form (§6.5 item 1); and its evaluation contains no regex, no counted
repeat and no pattern of pcrec's shape (§6.4).

**Should §5.1's recommendation change? Yes, in four specific ways.**

1. **Step 1 (fix lim2's margin with N2 or N1, conditional on M1) is
   unchanged and is now *more* clearly right.** §3.1's finding that the bail
   needs proved inequivalence while compaction proves equivalence is
   confirmed by §6.3: OTF supplies no bound of either kind, and the paper's
   §1 says the full DFA must be built.
2. **Step 2 (read the paper) is discharged by this section.**
3. **Step 4's "then choose between B and C on the numbers" becomes
   B-first.** B is the paper's SC-S: published, evaluated, the only
   configuration observed to reach zero overhead, Tier 1 so it cuts both
   construction work and the K7 charge, and it needs no intermediate
   minimization and therefore none of §3.5's five hazards. C is reconsidered
   only if M2 shows a large residual gap after B *and* someone is willing to
   build A underneath it. §4.3's cross-product corpus is still the
   precondition for B and is now the critical path.
4. **"Do not build A" survives, on a corrected reason.** §3.5's rule is
   confirmed by the paper — but §3.5's claim that under it *"what remains
   merging is precisely the closed subgraph"* is **too pessimistic, and it
   was the sole basis for predicting A does nothing.** Two states each
   carrying an unexplored successor still merge when it is the *same*
   unexplored successor, which is not the closed subgraph; §3.5's own
   parenthetical says as much ("a state transitioning into one merges with a
   state transitioning elsewhere" — the exclusion propagates only for
   *elsewhere*) and then over-concludes. The paper's median of 48 productive
   minimization triggers per Walnut system (Table 2) is evidence the yield is
   not vacuous on *some* population. A still is not recommended alone — it is
   Tier 3, it saves no construction work, and it lands all five hazards —
   but it should be declined on those grounds and not on a yield prediction
   this section shows was wrongly derived.

**Does M6 as written still decide the second-pass question? No — it is
answered in advance for C, and should be rewritten.** M6's bar was *"the
second pass may be made optional only if, with it skipped, no artifact grows
by more than a few percent"*. §6.1 settles that no OTF-shaped mechanism
licenses skipping it: the published construction requires a final
minimization and its reference implementation runs one unconditionally. M6's
**second half survives intact and is independent of the paper**: does
[OPT-5]'s scan edge require *minimality* or only *finality*
(`src/opt/scanedge.c:43`'s five local preconditions against
`src/core/internal.h:4387`'s "it needs the canonical state set")? That is a
pcrec code question a prototype answers in an afternoon, and it should be
what M6 is. **M1 also needs restating**: it should measure the yield of the
paper's partition rule — explored states blocked by accept vector,
unexplored states pinned singleton — not the closed fraction, because §6.6
item 4 shows those are not the same set. **M2 gains one row**: report the
paper's *overhead* metric (maximum intermediate size minus final size), since
that is lim2's own quantity and it makes pcrec's numbers directly comparable
to §5's.

### 6.7 Their library (answer 6)

**Name** OTF. **URL** `https://github.com/jn1z/OTF` (given in the paper's
Data-Availability Statement, alongside the Zenodo artifact
doi:10.5281/zenodo.18163403 holding the benchmark systems, full results and
a Docker image — **not downloaded**). **Licence** MIT, *"Copyright © 2025
John Nicol and Markus Frohme"* (`LICENSE.txt`, read). **Language** Java,
built on AutomataLib 0.12.1 (`net.automatalib`, `pom.xml`); the paper (§1,
§6) states it is included in the theorem prover Walnut since version 7.
**Size**: the GitHub API reports the repository at 375 KB over 70 files; the
32 files under `src/main/java` total ≈183 KB of source, plus ≈57 KB of
tests. The core loop, Algorithm 1 itself, is 182 lines
(`OTFDeterminization.java`). Byte sizes from the tree API — **the repository
was not cloned and no line count was taken**.

Two things the repository says that the paper does not.

- **The shipped registry is already past §4.1.** The driver instantiates
  `AntichainForestRegistry`, and the tree carries `AntichainForest`,
  `AntichainForest2`, `AntichainForest5`, `AntichainForest5Idx`,
  `InvertedIndex`, `ACElts`/`ACGlobals`/`ACPlus` and `SmartBitSet` — roughly
  130 KB of the 183 KB. §4.1's Remarks and §6 name *"more involved
  structures for antichains [10] or inverse indices [25]"* as future work;
  the implementation has already gone there. **§3.8's estimate of "500+
  lines, a new subsystem" is if anything low**: on this evidence the
  registry, not the loop, is the system.
- **`CHANGELOG.md` records two correctness-adjacent fixes in 1.1.0**
  (2025-10-29), one of them *"Fixed AC Union performance bug (conservative
  AC unioning sometimes lost equivalence information)"* — i.e. the antichain
  union silently dropped equivalences it had earned. That is §4.5's C2
  failure class, in the authors' own tree, found by them, five months after
  the first release. It is not a soundness bug (losing equivalences costs
  size and time, it does not corrupt the language), but it is direct evidence
  for §4.5's verdict that a registry is a structure where being wrong is
  quiet.

**As an isomorphism oracle for pcrec: no, and §4.5's claim never needed it.**
The tool reads finite automata in BA format and can write its result out
(`--writeBA`, added in 1.1.0 explicitly as a replacement for the removed
`--sanity-check` option), so it *can* be diffed against — but only for plain
NFAs with no epsilon transitions, no priority order, no class-axis or
position views and no `eolvar`/`endvar`. pcrec's machines are not expressible
in its input format, so it cannot check pcrec's DFAs. **This costs §4.5
nothing**: that section's checkability claim was a differential against
**pcrec's own existing two-pass pipeline** (compile every corpus pattern both
ways, assert the minimized machines isomorphic), which needs no external
reference and stands unchanged. The library's realistic use to this project
is as a cross-check for a pcrec-side *re-implementation of the algorithm* on
plain NFAs, which is a much narrower thing than an oracle. **Verified**: the
format, the flags and the licence, from the README, CHANGELOG and LICENSE.
**Unverified**: everything about running it — it was not cloned, built or
executed, and no claim here rests on its behaviour.

### 6.8 What M5 did not settle

- **Whether an unrolled counted repeat is "structure" in CCL's sense.** The
  copies form an inclusion chain (§3.7), which looks like exactly the lattice
  convexity closure exploits, and there is not one regex in the paper's
  evaluation to check it against. Plausible; **unverified**; it is the single
  most valuable thing a prototype could measure, and M2's stand-in is the
  cheap way to approach it.
- **Figures 1 and 2.** They are images in the HTML and were not read as data,
  so every quantitative claim in §6.4 about relative runtime and overhead is
  the paper's prose about its own plots, not a reading of them.
- **Any overhead number on easy inputs.** §6.4: the paper gives none, and
  pcrec's median pattern is three orders of magnitude smaller than its median
  benchmark system. §5.2's M4 is not retired by anything here.
- **The Zenodo artifact**, and therefore any independent check of the
  reported numbers.
- **Whether the priority order and the pruning are functions of the position
  set** (§6.5 item 1). This is the premise CCL would need in pcrec and it is
  the same claim §3.7's condition 3 wants attacked. Nothing in the paper
  bears on it, because the paper's automata have neither.
