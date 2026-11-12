# Captures without the VM: tagged DFAs and their relatives, for pcrec

**Status: RESEARCH (lane `dfacap`, 2026-11-12, opus). No build, no build go.**
Frank 2026-11-12: *"I'd like to start a research lane into dfa capture. See
what the literature says and form some opinions on application to our
situation ... I want to know more about it: limits, level of effort, costs."*
Rulings in force: research only ("It's not the right time to act on");
[ENG-TDFA] is a filed, unscheduled BIG FISH; [CAPS-KNOWN]'s census is
scheduled "not a priority"; D26 makes capture offsets exact (tier 1); D194
sets: this memo feeds a future set and starts nothing.

Census instruments and outputs: `docs/design/dfa_captures/` (its own
CLAUDE.md). Plan-row and decision proposals are in §7; the manager files them.

## Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | say what is already settled, so nobody re-surveys it | the owner, the next lane | §1 lists every prior finding this memo relies on, with its source, and marks each claim here NEW or SETTLED |
| G2 | answer the semantics question that decides applicability | whoever designs a tagged DFA | §2.2 states which construction gives PCRE leftmost-first captures, at what cost, and what stays unproven, each claim marked SOURCED or INFERRED |
| G3 | size each class a step would free, split by cause | the owner, ordering this against [COND-FAMILY] | §3 counts, from the compiler's own stamps over corpus + bench, the VM rows freed by captures alone, by captures + lookaround, and those kept by other causes |
| G4 | a staged path with effort, cost and a D77 trigger per stage | the owner, at a future set | §5 gives each stage its size, what it frees (from §3) and the measurement that would open it |

Priority on conflict: G2 > G3 > G1 > G4 (a wrong semantics answer makes the
rest moot; a staged path without the census is guesswork). Non-goals: no
design of the construction, no code, no timing run, no syntax.

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Relevant in one place. §3 is compile-time COUNTS
   (which engine the shipped compiler picks), not timings. The only timing this
   memo uses is [CAPTURES-DFA-MB]'s M-B reduction (`onepass_census.md` M-B:
   bench find-all loops, Linux, best-of-N), quoted, not re-run. A match-dense
   regime would flip the value judgment in §6, which is why §6's trigger is
   that regime.
2. **Independent control.** Relevant. The engine and cause columns are the
   compiler's own `RX_ENGINE`/`RX_ENGINE_WHY` stamps, and the second pass's
   "would it be DFA without captures" is the compiler's own `--no-captures`
   answer, so they say what pcrec does, not what is possible. The
   lookaround-only and capture-inside-lookaround splits and the shape counts
   (§3.2) are a TEXT heuristic over the pattern (`census.py textscan`,
   `shape.py`), marked as such; spot-checked on 37 sampled rows, not
   validated against a parser. Any future build's control is §5.3: the VM,
   which is an independent capture engine already checked against libpcre2
   (PC-3).
3. **What moves when data is regenerated.** Not relevant: the census is a
   scratch measurement; nothing emitted, pinned or stamped reads it.

---

## 0. The answer in one page

**Most of the literature question was already answered** by
`docs/dev/optloop/captures_via_dfa_survey.md` (2026-09-22) and its two
measurements (`onepass_census.md`: M-A reach, M-B cost). This memo does not
redo that survey. It adds four things.

1. **The semantics blocker is smaller than the survey said (INFERRED, §2.2).**
   The survey closed TDFA as "proved for leftmost-greedy and POSIX, and PCRE
   is neither". But "leftmost-greedy" in the TDFA literature is the order of
   an ordered list of NFA configurations, the same thing D3's priority subset
   construction already is in `src/ir/dfa.c`. A lazy quantifier is only a
   different edge order inside that list, and pcrec's closure already
   implements PCRE's empty-iteration rule (K17/K18). So a leftmost-first
   tagged DFA is D3's construction plus a tag-to-register map per thread. It
   is not a different disambiguation theory. What stays unproven is narrower
   and testable: how PCRE2 *updates* captures under repetition (last
   iteration, empty iterations, restore versus clear). That is a property of
   where tags sit in the NFA, and the VM already defines it (publish-at-close,
   [M6.5.2]). Against it: re2c's maintainer doubts that lazy operators fit a
   DFA at all ("a DFA may fuse non-greedy and greedy paths", §2.2). The memo
   argues that doubt belongs to re2c's longest-match setting, but it makes
   `(a*)|(a*?)` Stage 0's first test.
2. **The census by cause (§3), corpus + bench, 5,769 unique patterns:**
   2,353 are on the VM; **815 (corpus 793, bench 22) are there ONLY because of
   captures**, which is 35% of the VM population on both the corpus and the
   bench. Captures plus a lookaround as the only other cause: **37 + 6
   spellings (bench 1)**, plus **88 more whose capture sits INSIDE the
   lookaround**, which no intersection product can serve. Kept on the VM by
   other causes regardless: backreferences 369, calls/recursion 60,
   atomic/possessive 51, callouts/variables 24, `\K` 14, lookaround + another
   cause 98. For comparison, [COND-FAMILY]'s own class (capture-FREE rows whose
   only cause is a lookaround) is **394 (bench 12)**.
3. **Of the 815, 709 already run the two-pass hybrid** (a DFA window, then the
   VM on the span), so on sparse search the VM pass costs nothing measurable
   (M-B: median 0.00% of time). The prize is (a) match-dense and whole-subject
   match (M-B: median 33% on 5-93 byte subjects, confounded), (b) the
   **106 captures-only rows with NO prefilter** (nullable languages, where
   the VM does the whole scan), and (c) structure: linear-time captures,
   captures under `--engine=dfa`, and `\K` as a start tag (88 more VM rows).
4. **One construction, not three mechanisms.** The one-pass DFA ranked first by
   the survey, [CAPS-KNOWN]'s tag-determinism and partial evaluation, and full
   TDFA are the SAME object at three admission levels: a determinized,
   tag-carrying priority machine whose register program needs no copies
   (one-pass and fixed-offset), or needs copies (general). Build the tagged
   construction once and admit by "copy-free" first. Do not build a separate
   one-pass engine.

**Recommendation (§6):** keep [ENG-TDFA] unscheduled. Let [COND-FAMILY]'s
checker product go first (ruled, speed-first, and its rows make the VM do
real work), but design the product's state identity so a per-thread tag map
can be added later (a seam, not a build). Open Stage 0 (a compile-only
tagged-construction counting probe, no `src/` edit) only on
[CAPTURES-DFA-MB]'s trigger: a match-dense bench cell where the hybrid's VM
share is at least 10% of time on Linux. Effort when opened: Stage 0 is one lane, Stage 1
(copy-free, anchored, inside the hybrid window) is one large opus lane plus a
panel, and Stage 2 (registers with copies) is a second large lane with the
real risk.

---

## 1. What we already have (read first)

| claim | source | status here |
|---|---|---|
| Two families exist: two-pass (DFA bounds, then a capture engine on the span: RE2, rust `regex-automata`, .NET) and tagged automata (Laurikari, TRE, re2c, `regex-tdfa`); the one-pass DFA sits between them | `captures_via_dfa_survey.md` §0, §2 | SETTLED |
| pcrec already ships the two-pass design: `RX_VM_PREFILTER "hybrid"` with an exact capture-erased forward+reverse DFA pair hands the VM an anchored window | survey §1.4; `src/gen/emit_vm.c` prefilter block; `src/opt/select_engine.c` `forces_captures` | SETTLED, re-measured in §3: 709 of 815 captures-only rows are hybrid |
| The window END is a pruning ceiling, not a hard bound; span-equality is BELIEVED-WITH-GATE (R21, K17/K18) | survey §1.4(i)(ii); D142 item 2 | SETTLED; it matters for Stage 1's placement (§5.2) |
| One-pass reach: 31.46% of capture-bearing corpus patterns (29.41% of the 17 capture-forced capability hybrids); UTF-8 barely moves it; `pcrec_altcls` adds 3.16 points | `onepass_census.md` M-A | SETTLED. NEW reading: 543 of the 1,173 capture-bearing patterns were excluded by node KIND (lookaround, backref, call), so among patterns a capture DFA could serve at all, reach is 369 / 630 = **59%** (INFERRED arithmetic from that table) |
| The VM pass's share of time: throughput median 0.00%, match regime median 32.75% on tiny subjects (confounded by per-call overhead); verdict SPLIT | `onepass_census.md` M-B; [CAPTURES-DFA-MB] | SETTLED; that row's trigger is reused in §6 |
| A successful exact hybrid makes the VM's leading fixed-width, choice-free segment redundant; the WHOLE program for `det_all` (164 of 569 exact hybrids, 29%); measured x1.13 match-dense, x1.00 sparse | `docs/design/pf_know.md` §0; D142 item 1 | SETTLED; `det_all` is Stage 1's trivial member |
| [CAPS-KNOWN]: tag-determinism per accepting state; partial finish plus VM resume; GENERAL FORM = partial evaluation of the VM over proven bytes | plan row [CAPS-KNOWN]; `start_landing.md` U1 | SETTLED as a row; NEW reading in §4.4: it is a restriction of the tagged construction |
| [ENG-TDFA]: two uses, START tags (the general form of start-landing) and CAPTURE tags; first step when opened = a study by measurement against leftmost-first semantics | plan row [ENG-TDFA] | SETTLED; this memo is that study's literature and census half |
| Compound tool: "DFA LOCATE + VM FINISH" is client 2; one captures array across parts (D163 add. 3); a DFA part produces no group spans except where derivable | D163 add. 1-3 | SETTLED; a tagged DFA is exactly a DFA part that DOES produce spans |
| Lookarounds become DFA-able through ONE checker product with (start, read) rows; captures inside a lookaround body keep the VM unless the finishing pass honours them | `cond_family.md` §2.1 (P8, P11, P12), §3 (M4, M7), §5 | SETTLED; §3.1 counts the overlap |
| D3: forward DFA states are priority-ordered NFA state lists; leftmost-first spans (greedy and lazy) from a pure DFA; "Revisit-when: captures (M4) need tagged automata or VM anyway" | decisions.md D3; `src/ir/dfa.c` header | SETTLED, and §2.2's main lever |

**Stop rule applied:** the survey answers "who does it and how" in full, so §2
is short. The effort goes to the semantics question (§2.2), the census by
cause (§3), and the staged cost (§5).

---

## 2. The literature

### 2.1 What each line of work contributes (summary; detail in the survey §2)

| work | what it gives pcrec | semantics |
|---|---|---|
| Laurikari TNFA/TDFA [Lau00] [Lau01] | the construction: tags on NFA transitions; DFA states map tags to registers; transitions carry register ops (set-to-position, copy) | POSIX (TRE) |
| Trofimovich TDFA(1) [Tro19], re2c [Tro20] | one-symbol lookahead defers tag writes, so fewer registers and ops; re2c ships both policies (`--leftmost-captures`, `--posix-captures`) | leftmost-greedy or POSIX |
| Borsotti-Trofimovich [BT21] [BT22] | full pseudocode, register optimizations (liveness, interference, allocation), AOT and lazy determinization; the claim that runtime overhead is constant per transition and independent of input | both |
| Okui-Suzuki [OS10]; Sulzmann-Lu [SL14] | POSIX disambiguation (positions, derivatives) | POSIX only, so not pcrec's |
| Frisch-Cardelli [FC04] (NOT READ: search summaries only) | defines GREEDY matching as first-match alternation over the star's expansion, and names the "problematic" case: a star whose body accepts the empty word | greedy (= Perl/PCRE order for regular constructs) |
| Berglund-van der Merwe [BM17] (NOT READ: search summaries only) | prioritized NFA (pNFA) and prioritized transducers as the formal model of backtracking matchers' capture semantics; a pNFA has at most one accepting run per input | backtracking (PCRE/Java) |
| RE2 OnePass / BitState / NFA [RE2onepass] [Cox10]; rust `regex-automata` onepass + PikeVM [RAonepass]; Go onepass [GoOnepass] | the two-pass shape pcrec already ships; one-pass as the cheap deterministic capture engine (caps: RE2 65k states and 5 groups, Go 1,000 instructions) | leftmost-first |
| .NET NonBacktracking [Mos23+] | captures from a third phase (an NFA simulation with effects) on a span the first two bound; backtracking semantics formally proved | leftmost-first |
| Hyperscan [HSdoc], PCRE2 `dfa_match` [PCRE2matching] | no captures: their automata keep no per-path bookkeeping, and all-matches semantics has no single chosen path | none |

### 2.2 The semantics question: which constructions give PCRE leftmost-first

PCRE's preference is the backtracking order: alternatives left to right,
greedy repeats prefer another iteration, lazy repeats prefer to stop, and the
first path to succeed wins. For a REGULAR pattern (no backreference, atomic
group, lookaround or recursion) that is exactly "the first accepting path in
the prioritized NFA's order" ([BM17]'s pNFA, [FC04]'s greedy semantics).

**What the published TDFAs deliver.** re2c's `--leftmost-captures` [re2cman]
(*"submatch extraction with leftmost greedy capturing groups"*) is
leftmost-greedy in the priority-order sense. [BT22] (read through the ar5iv
HTML, sections 1-3.3; relayed by the manager 2026-11-12): TNFA epsilon
transitions carry priorities, the closure is a left-to-right depth-first walk,
a TDFA state carries a PRECEDENCE vector, and two states merge only when the
configuration set AND the precedence coincide. Negative tags mark bypass
paths (an alternative not taken, a zero lower bound). Bounded repetition is
built directly rather than desugared, because desugaring duplicates tags.
Final register operations run once at match end, and a match ending
mid-input falls back to the last final state. [Tro19]: for leftmost-greedy,
"ordinals coincide with row indices". The paper says NOTHING about lazy
quantifiers, PCRE/RE2 equivalence or empty-iteration semantics. re2c's
"longest match takes precedence" is LEXER RULE selection, not submatch
choice [re2cman].

**The counter-statement, recorded first.** re2c's maintainer, on lazy
operators ([re2cIssue208], 2022-12-12): *"I'm not sure if non-greedy
operators can be implemented in DFA-based engines like re2c. The fundamental
problem is, a DFA may fuse non-greedy and greedy paths into one"*, with
`(a*)|(a*?)` as the example. Earlier (2018): non-greedy SUBMATCHES are
possible via tags, but the whole match cannot be non-greedy. This is the
strongest evidence against §2.2's claim, and it comes from the person who
built the construction.

**Why this memo still reads it as answered for pcrec (INFERRED).** The
"whole match cannot be non-greedy" part belongs to re2c's lexer setting,
where the overall end is longest-match. In pcrec, the overall end is the
first accepting thread in priority order, and D3's prune-at-ACCEPT already
computes it, lazy included. The shipped DFA answers lazy patterns' group-0
spans exactly today, checked against libpcre2 and python `re`. On "fusing":
in a precedence-ordered state, two paths are merged only when they reach the
same NFA state with the same future. The lower-priority path is then dropped,
which is exactly what a backtracker's priority does. For `(a*)|(a*?)`, the
two arms enter different NFA states, so they stay separate configurations
with separate tag versions. **`(a*)|(a*?)` and its relatives are Stage 0's
first differential cases**, because a respected practitioner believes they
can fail.

**Why that is close to pcrec's case (INFERRED, the main new claim):**

- pcrec's forward DFA is already the ordered-configuration construction.
  `src/ir/dfa.c` (header): *"A DFA state is a priority-ordered list of
  N_CLASS NFA states ... epsilon closure walks split edges in preference
  order and stops the instant ACCEPT is reached — lower-priority threads are
  pruned."* That is a leftmost-greedy TDFA's state with the tags removed.
- A lazy quantifier is not a different policy in this construction. It is the
  same split with its two edges in the other order. The closure walks "split
  edges in preference order", so laziness is already represented, and the
  shipped DFA answers lazy patterns' group-0 spans exactly today.
- The overall match is not longest-match as in re2c. It is the first accepting
  thread in priority order, which D3's prune-at-ACCEPT already computes. A
  tagged version keeps, per surviving thread, which register holds each tag,
  and at ACCEPT the highest-priority accepting thread's registers ARE the
  captures. That is the Pike VM's priority-thread rule, determinized, and the
  Pike VM rule is what RE2 and rust use for leftmost-first submatches.
- PCRE's empty-iteration rule ("a group iteration that matched nothing ends
  the loop") is already in the closure: `src/ir/dfa.c`'s K18 open-loop
  context (*"arriving by epsilon at a loop entry the path is already inside
  means the iteration in progress consumed nothing, which ENDS the loop"*).
  [FC04]'s "problematic" case is the same rule, and Go got it wrong
  ([GoIssue46123], `(|a)*` must match empty, as Perl and PCRE do).

**What stays unproven, stated narrowly.** Disambiguation is not the open
question. Capture UPDATE semantics under repetition is, and it is a different
question:

- the last-iteration rule and what an iteration that skips a group does to it
  (`(?:(a)|b)+` keeps group 1 from an earlier iteration);
- empty iterations: PCRE2 *restores* a group's previous value where Perl
  *clears* it (`(?:(a)?)+`-shaped patterns, [PCREdev2020]). D26 says follow
  PCRE2;
- publish-at-close: pcrec's VM writes a group's start to a PENDING slot and
  publishes the pair at close ([M6.5.2], 5,808 cells, 0 divergences against 138
  with publish-at-open). In a tagged machine that is an open tag written to a
  scratch register and copied at the close transition, so it costs a register
  copy, not a new theory.

All three are tag-placement questions inside the tagged NFA, and pcrec has a
complete oracle for them: the VM (§5.3). So the blocker the survey recorded,
"a research contribution, not an implementation", reduces to "an
implementation with an exact differential gate". **This claim is INFERRED.**
No paper read here proves a TDFA correct for lazy operators or for PCRE2's
capture-update rules, re2c's maintainer doubts the lazy half (above),
and K17/K18 show that this territory has produced real priority bugs in
pcrec before. Stage 0 (§5.4) exists to test the claim before anything is
built.

**Costs of the policy.** Leftmost-greedy is the cheaper TDFA policy. POSIX
needs ordinals and comparison work at determinization ([Tro19]; [BT22] treats
both). Runtime cost for either is register operations on transitions, constant
per transition and independent of the input ([BT22], single-sourced via the
survey).

---

## 3. Our situation: the census

### 3.1 Who is on the VM, and why (`census.py`, `classify.py`)

Population: every `pattern`/`pattern-esc` block in `tests/**/*.rxt` (through
`pcrec --list-source`) plus pcrec-bench's patterns (read-only: capability,
unusual and utf8 through their `patterns.rxt`, the other sub-benches' `.rx`
exports), deduplicated on pattern bytes, giving 5,769 unique patterns (5,487
corpus, 282 bench). Pass 1 is `--features all` (shipped default). Pass 2 runs
`--no-captures` on each row whose `RX_ENGINE_WHY` names a capture group. That
is 7,326 compiles in one niced process, over the brief's ~6,000 by the pass-2
rows; each compile is about 10 ms. Commit: this worktree's `build/pcrec` at
61dffa16a.

| | all | corpus | bench |
|---|---|---|---|
| patterns | 5,769 | 5,487 | 282 |
| DFA | 2,999 | 2,802 | 197 |
| VM | **2,353** | 2,291 | **62** |
| refused (module gaps, syntax errors in negative tests) | 417 | 394 | 23 |

The VM population split by what keeps it there (pass 2 answers "without
captures"):

| class | all | corpus | bench | what frees it |
|---|---|---|---|---|
| **captures ONLY** (`--no-captures` gives the DFA) | **815** | 793 | **22** | a capture-assigning DFA (this memo) |
| captures + lookaround only, capture outside the lookaround (TEXT) | 37 (+6 `(*positive_lookahead:` etc. spellings) | 36 | 1 | capture DFA AND [COND-FAMILY]'s checker product, both |
| captures + lookaround only, a capture INSIDE the lookaround (TEXT) | 88 | 88 | 0 | neither: a lookahead's captures come from an atomic sub-match, VM (`cond_family.md` M7) |
| captures + lookaround + another cause (TEXT) | 98 | 97 | 1 | not by these two steps |
| captures + backreference | 369 | 359 | 10 | never (a DFA cannot express it) |
| captures + call/recursion (not spliceable) | 60 | 57 | 3 | never |
| captures + atomic/possessive | 51 | 50 | 1 | a separate question (outside this memo) |
| captures + callout / pattern variable | 24 | 24 | 0 | VM by design |
| captures + `\K` | 14 | 14 | 0 | the tagged DFA (`\K` is a start tag, §4.6) |
| captures + DFA size cap | 1 | 1 | 0 | no (a tagged DFA is larger) |
| **capture-FREE**, lookaround only | 394 | 382 | 12 | [COND-FAMILY]'s checker product alone |
| capture-free, atomic/possessive | 207 | 204 | 3 | outside this memo |
| capture-free, `\K` | 74 | 73 | 1 | the tagged DFA (start tag) |
| capture-free, callouts/vars, calls, lookaround + other, size cap | 121 | 106 | 15 | no |

Read it as a ladder:

- **Captures alone hold 35% of the VM population**, on the corpus
  (793/2,291) and on the bench (22/62) alike. That is the class a tagged DFA
  frees. 709 of the 815 already run the hybrid. 106 run with NO prefilter
  (nullable languages like `(a|)`, `(a*)*`, `(a|){2,4}`), and there the VM
  scans the subject itself.
- **Adding lookaround-as-intersection frees only 43 more** with captures,
  against 394 capture-free rows the checker product frees alone. The two
  steps are nearly ADDITIVE populations, not a compounding one.
- **Captures inside lookarounds (88) are the main residue of the two steps
  together.** They are the corpus's test shapes (`(?=(a+)b)a+b`,
  `(?<=(a))b`). The bench has none.
- **Backreferences dominate the permanent VM class** (369), as the survey
  found on the capability bench (6 of 9).
- The `\K` rows (14 + 74) are a bonus a tagged DFA brings for free (§4.6).

The bench is the better proxy for real use (the corpus is written to exercise
the compiler). Its 22 captures-only rows are: capability's ipv4, us-zip,
logparse-atomic-removed, aws-key, github-pat, slack-webhook, userpass,
datefinder-alternation (36 groups, no prefilter), moment-iso8601,
codegrammar-flat/-xflag, the three nested-plus rows and semdiv `(a|)*\d`;
and syntax's seven group/recursion-spelling rows (calls that splice).

### 3.2 Which sub-classes are cheap (`shape.py`, TEXT heuristics over the 815)

| sub-class | count | source | cost class |
|---|---|---|---|
| one capture group (`RX_NCAPS` 2) | 568 (70%) | stamp | two tags; fewest registers |
| two or more groups | 247 | stamp | more tags; still constant per transition |
| a capture repeated (quantified, or inside a quantified group) | 296 (36%) | TEXT | last-iteration semantics: register COPIES (Stage 2) unless one-pass |
| a counted repeat `{n,m}` anywhere | 251 (31%) | TEXT | pcrec's NFA expands counts, so tags are duplicated per copy ([BT22] avoids desugaring for this reason) |
| one-pass (no ambiguity at any choice, anchored) | about 59% of KIND-eligible capture-bearing patterns | `onepass_census.md`, INFERRED arithmetic §1 | copy-free: each transition writes a position into a fixed slot |
| fully fixed-offset (`det_all`): every capture at a constant offset from start or end | 164 of 569 exact hybrids (29%); [CAPS-KNOWN]: 85 corpus + 3 bench | `pf_know.md` §4; [CAPS-KNOWN] | no registers at all: constants added to the window bounds |
| captures that need only the match bounds (a single group around the whole match, e.g. syntax `(cat)`) | inside the fixed-offset class | — | zero cost: group 1 = group 0 |

So, roughly: about a fifth to a third of the 815 need nothing but constant
offsets. About 60% are one-pass (copy-free, which includes the fixed-offset
cases). The rest, about 40%, are ambiguous and need the general register
machine. The one-pass and fixed-offset counts come from earlier censuses on a
slightly different population, so treat the split as approximate.

---

## 4. Limits

### 4.1 State and register blow-up

- **States.** A tagged DFA is at least as large as the untagged DFA (same
  subset construction) and usually larger, because two configuration lists
  that differ only in which register holds a tag are different states until
  register normalization maps them together. The worst case stays
  exponential in NFA size, as for any subset construction. Laurikari proved
  termination; Trofimovich's lookahead reduces registers and ops "and usually
  [gives] smaller" automata, "reasonably close in speed and size to ordinary
  DFA" ([Tro19], measured on re2c's lexer workloads, not on PCRE-shaped
  patterns).
- **Registers.** Bounded by (live threads) x (tags) per state: at most NFA
  states x 2 per group. With one-symbol lookahead and liveness, typical
  patterns need few.
- **What blows up in practice:** a capture inside a counted repeat over a wide
  class ([RegexTDFA]'s own warning; pcrec's K25/[ART-SIZE] for the untagged
  case), and unanchored search with captures (every restart is a new thread
  with its own tag versions). §5.2 sidesteps the second by running the tagged
  machine ANCHORED inside the existing hybrid window.
- **pcrec's guards apply unchanged:** `src/core/limits.def`'s state caps, and
  [SEL-1]'s overflow-as-selection-outcome (`forces_dfa_overflow`), so an
  overflow falls back to today's hybrid with no behavioural difference.

### 4.2 Lazy and greedy priority

Represented by edge order in the ordered state (§2.2). Not a limit, given the
INFERRED claim.

### 4.3 Nested quantified groups (last-iteration semantics)

The general case needs register copies: a group's value is the last iteration
that set it, and a group inside an outer repeat keeps an older iteration's
value when a later iteration skips it. PCRE2's restore-on-empty differs from
Perl's clear (§2.2). 296 of the 815 have a repeated capture. Inside the
one-pass subset no copies are needed (the next byte decides). Outside it,
this is Stage 2's work and its main correctness risk.

### 4.4 [CAPS-KNOWN] and partial evaluation, placed

[CAPS-KNOWN]'s general form runs the VM at compile time over static data
until the first choice that needs unknown data. A tagged determinization runs
the VM's thread SET over all inputs at once, so it does not stop at an
undecidable choice: it keeps both threads with their own tag versions. So
partial evaluation is the tagged construction restricted to the proven
prefix, tag-determinism per accepting state is the tagged construction
whose registers all reduce to constants, and one-pass is the case with one
thread per state. One construction, three admission levels (§0 point 4). The partial
resume (write the determined groups, then enter the VM mid-pattern) is a
different seam: a DFA-to-VM handoff inside a pattern, [ENG-ISL]'s island.

### 4.5 Captures inside lookarounds, and lookaround-as-intersection

The checker product of [COND-FAMILY] runs the lookaround body as a separate,
untagged deterministic component. Tags can live in the MAIN component of that
product unchanged, so "captures outside a capture-free lookaround" composes
(43 rows). Captures INSIDE a lookaround body (88 rows) do not compose:
PCRE2 sets them from the body's first successful (atomic) sub-match at that
position, which may extend past the main match, and only if the assertion
succeeds. A tagged checker would need its own priority order and a commit
point. That stays VM (`cond_family.md` M7, honour-on-close), as does a
non-atomic lookaround with captures (P11).

### 4.6 `\K`, alternation-reset, named groups, partial matches

- **`\K`**: a start mark is a tag on group 0's start (the last `\K` executed on
  the winning path wins, ordinary tag semantics). This is [ENG-TDFA]'s
  START-tag use and `cond_family.md` M8. It would move 14 + 74 VM rows. A
  `\K` inside a lookaround is refused today and stays so.
- **Alternation-reset `(?|...)`** (refused, [BRANCH-RESET]): numbering only.
  Two arms writing the same slot is natural for registers.
- **Named groups and duplicate names (`(?J)`)**: numbering and reporting only;
  no effect on the machine.
- **Partial matches**: pcrec has none (match_api.md §5.2¶6). If added, a tagged
  DFA reports tags at the last position as easily as the VM.

### 4.7 VM-only regardless

Backreferences (369 with captures), non-spliceable calls and recursion (60),
callouts and pattern variables (24), captures inside lookarounds (88),
atomic/possessive (51, a separate question), plus anything over the state or
register caps. Together that is about 600 of the 1,557 capture-forced rows,
and roughly 940 of the 2,353 VM rows once the capture-free remainder is
added. That is the VM's permanent floor under both the capture and the
lookaround steps.

---

## 5. Costs and effort

### 5.1 Speed and size

- **Per transition:** zero to a few register writes. One-pass: at most one
  `slot[k] = pos` per tag-bearing transition. Fixed-offset: none in the loop,
  constants added to the bounds at the end. General: copies on some
  transitions, plus final ops at accept. Against the VM, the comparison is
  frames, backtracking and per-instruction dispatch, so on match-dense input
  the tagged pass should win and on sparse input it changes nothing (the VM
  span is already tiny; M-B throughput median 0.00%).
- **It does not remove the locate passes.** Run anchored inside the hybrid
  window (§5.2), it replaces only the second pass. Removing the reverse pass
  too needs START tags in the unanchored forward machine (Stage 4).
- **Emitted size:** a tagged anchored machine plus the existing prefilter pair,
  against the VM program plus the pair. It could go either way. It is a new
  term for the size posture ([ART-SIZE], the emitted-size caps) and needs
  measuring in Stage 0.
- **Compile time:** subset construction with larger state identities, plus
  register allocation. Bounded by the existing caps.

### 5.2 What pcrec's DFA emitter and facts would need (files)

| piece | where | change |
|---|---|---|
| tags on the NFA | `src/ir/nfa.c` (today `A_CAP` is deliberately INVISIBLE to the NFA builder, D31; the comment near the top of the file explains why) | emit tag-set epsilon edges for open, close and `\K`, with publish-at-close as a pending tag; the capture-erased build stays for the prefilter |
| tagged state identity | `src/ir/dfa.c` (`intern`/`dhash` key on the ordered list + `eolvar`/`endvar`; the K18 open-loop context) | add a per-thread tag-to-register map, register normalization, and per-transition op lists |
| tag-aware minimization | `src/opt/minimize.c` (Moore refinement; the signature is accept bit + transitions + EOL/END edges) | the op lists join the signature; states with equal transitions but different ops do not merge |
| emitter | `src/gen/emit_dfa.c` (the forward, reverse and attempt loops; the hybrid's private prefilter) | an anchored tagged entry with a register file, writing `capture_spans`; a new emitted form, so an abi event (D76/D94) |
| selection | `src/opt/select_engine.c` (`forces_captures` returns `ENGM_VM`) | a row in the engine table: "tagged DFA, admitted when the construction is copy-free (Stage 1) / within caps (Stage 2)", falling back to today's hybrid. A deny/force axis per D144 item 4 |
| caps | `src/core/limits.def` | tagged-state and register caps (RE2's 5 groups / Go's 1,000 instructions are the precedents; pcrec measures its own) |
| facts | `src/facts/` | `tag_shape` per pattern (copy-free / fixed-offset / general) as a listed fact, so [ENGINE-WHY] can say why a capture pattern stays VM |
| spec | `docs/spec/` (engine stamps, `RX_ENGINE` values, the axes table) | D80 hunk in the same change |

**Where Stage 1 plugs in:** in place of `rx_match_anchored` inside the
hybrid's window protocol. That is the survey's §3.3 point 2, and compound's
"DFA locate + finish" client (D163 add. 1). It does NOT rest on the
believed span-equality claim: the tagged machine computes its own end from
the window start and treats the window end as a ceiling, as the VM does
today.

### 5.3 Test and oracle burden (D26 tier 1)

Captures must match PCRE2 exactly. The burden is smaller than for most
engine work because **pcrec already has an independent capture engine**: the
VM, which is checked against libpcre2 (PC-3) and python `re`. A tagged route
behind a deny/force axis is then covered by `make test-axes`' answer-identity
sweep (every axis against the default, over the whole corpus) with no new
expectations. The corpus's capture expectations are oracle-verified already.
Needed in addition: a TAG-FOCUSED corpus (repeated groups, empty iterations,
restore-versus-clear, lazy, nested counted repeats, `\K` in alternations) with
libpcre2-verified expectations, written D27-blind from the goal, because this
is K17/K18 territory; and sabotage rows for the tag ops.

### 5.4 The staged path

| stage | what | size (rough, by analogy with prefilter-class features; not estimated line by line) | frees (from §3) | D77 trigger |
|---|---|---|---|---|
| **0** | compile-only COUNTING probe in `studies/` or `docs/design/dfa_captures/` (links libpcrec, no `src/` edit): build the tagged priority construction for the 815 + 43 rows, report tagged/untagged states, registers, copies per transition, the copy-free share, and differential spans against the VM on the corpus subjects | one opus lane | nothing; it tests §2.2's INFERRED claim and prices Stages 1-2 | [CAPTURES-DFA-MB]'s trigger (match-dense bench cell, hybrid VM share at least 10% of time on Linux) OR Frank's word |
| **1** | copy-free tagged construction, anchored, in the hybrid window; admission = no register copies (one-pass and fixed-offset, `det_all` and the [CAPTURES-DFA-MB] whole-program skip folded in) | one large opus lane + D6 panel + D27 tag corpus; abi event | about 60% of the 815 (INFERRED), including the 5 one-pass capability hybrids | Stage 0 shows copy-free reach of at least ~30% of the 815 and no differential mismatch |
| **2** | registers with copies (general leftmost-first TDFA with lookahead and register allocation) | a second large lane; the correctness risk lives here (§4.3) | the remaining ambiguous captures-only rows within caps (up to about 330) | Stage 1 shipped AND a bench cell among the ambiguous rows (moment-iso8601, ipv4: M-B's "has a target" rows) |
| **3** | with [COND-FAMILY]'s checker product: tags in the main component | small once both exist | 43 rows (bench 1) | both pieces built |
| **4** | START tags in the unanchored forward machine (removes the reverse pass; [ENG-TDFA] use 1, [START-LANDING] general form); `\K` | medium | the reverse pass on every hybrid; 88 `\K` rows | a bench cell where the reverse pass is a measured share |

---

## 6. Opinions, ranked

1. **Do not build now, and do not build a separate one-pass engine ever.**
   The one-pass DFA, tag-determinism and partial evaluation are admission
   levels of one tagged priority construction (§4.4), and D3's construction
   is already most of it (§2.2). Building one-pass as its own mechanism is
   the special case `pcrec-general-mechanisms-not-special-cases` warns
   against. Building the tagged construction with a "copy-free" admission row
   is the general form, and it grows by widening its admission.
2. **[COND-FAMILY]'s checker product goes first.** The owner ruled it
   (speed-first, D193), and its capture-free rows (394, bench 12) are rows
   where the VM does real work: the prefilter's end is not a bound under a
   lookaround, so the window is weak. The captures-only rows (815, bench 22)
   are more numerous but mostly already behind an exact hybrid window whose
   VM pass costs about 0% on sparse input. The two steps free nearly
   disjoint populations (§3.1), so the order loses nothing.
   **One ask for that build:** keep the product's state identity open to a
   per-thread annotation, so tags can later join the key without
   re-architecting (a seam the [STREAM] A-REV remodel also touches, D153).
3. **Stage 0 is the next step for captures, on a trigger.** It is cheap
   (compile-only, no `src/` edit), it is the D77 measurement, and it is
   the only way to discharge §2.2's INFERRED claim before any build. Its
   trigger is [CAPTURES-DFA-MB]'s existing one. No new trigger is invented.
4. **Stage 1 then Stage 2, each on its own trigger (§5.4).** Expected payoff:
   match-dense find-all and whole-subject match on capture patterns (M-B
   median 33% of time is the VM, before the subject-size confound is
   resolved), the 106 no-prefilter nullable rows (VM does the scan today),
   linear-time captures as a robustness property, and captures under
   `--engine=dfa`.
5. **Handoff architecture (`pcrec-handoff-architecture`).** Two seams, each
   serializable and each with its own test: (a) the TAGGED NFA (states,
   priority-ordered edges, tag ops), checked against the VM program it is
   derived from; (b) the TAGGED DFA (states, transitions, register ops, final
   ops), checked by span and capture identity against the VM. The emitter
   reads (b) only. Other back ends (other languages) read the same (b).

**What this memo does not settle:** whether §2.2's claim survives contact with
PCRE2's capture-update corner cases (Stage 0's differential decides it); the
emitted-size and compile-time price (Stage 0); whether the M-B match-regime
share holds at larger subjects ([CAPTURES-DFA-MB]); and atomic groups and
possessives on the DFA, a separate question.

---

## 7. Proposed plan-row and decision changes (the manager files)

- **[ENG-TDFA]**: add `refs: docs/design/dfa_captures_research.md`, and a
  `next:` line: "Stage 0 counting probe (§5.4) on [CAPTURES-DFA-MB]'s
  trigger; one construction with copy-free admission first; no separate
  one-pass engine." Keep it unscheduled.
- **[CAPTURES-DFA-MB]**: note that its one-pass rung member is Stage 1's
  admission level of [ENG-TDFA], not a separate engine.
- **[CAPS-KNOWN]**: note §4.4. The partial-evaluation census stays as
  scheduled. Its tag-determinism half is [ENG-TDFA] Stage 1's fixed-offset
  level.
- **[COND-FAMILY]**: a note on the checker product's design. The state
  identity should admit a later per-thread tag map. §3.1 also gives a rough
  re-count for its trigger (394 capture-free lookaround-only VM rows, bench
  12; boundedness and width NOT separated, so it does not replace the
  re-count the row names).
- **D3 addendum (proposed):** "Revisit-when captures" is answered: the
  tagged extension of this construction is [ENG-TDFA]'s route. Lazy and
  empty-iteration semantics are already in the closure; capture-update rules
  are the open part (dfa_captures_research.md §2.2).

## Evidence and reproduction

- `docs/design/dfa_captures/census.py`: population and the two passes;
  `classify.py` and `classify_out.txt`: §3.1; `shape.py` and `shape_out.txt`:
  §3.2; `capture_forced.tsv`: the 1,557 capture-forced rows with their pass-2
  answers.
- Run: `PCREC=build/pcrec TESTS=tests BENCH=<pcrec-bench>/bench nice -n 10
  python3 docs/design/dfa_captures/census.py > census.tsv`, then
  `python3 classify.py census.tsv` and `python3 shape.py census.tsv`.
- Premise check (brief): `build/pcrec --emit-facts -p rx --pattern '(a+)(b+)'`
  prints `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture group at pattern offset 0"`.
  `'(?=a)(b)'` needs `--features all` (the lookaround module) and then reads
  vm / "capture group at pattern offset 5" / hybrid. Its width-1 lookahead is
  an `A_CTX` node, so `--no-captures` takes it to the DFA.
