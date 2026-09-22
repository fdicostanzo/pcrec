# Captures via a DFA — who does it, how, and what fits pcrec

**Lane `capsurvey`, 2026-09-22. Survey and design analysis only: nothing
under `src/`, `tests/` or `docs/spec/`; no timing measurement; no code
proposal beyond a design shape.** Chartered by Frank, 2026-09-22: *"I'd be
interested in if anyone is capturing using dfa."*

Read §0 for the one-paragraph answer, §1 for what pcrec has today (the
part that turned out to matter most), §2 for the survey proper, §3 for the
ranking and the measurement that decides it.

Every external claim is cited by URL or by a `REFERENCES.md` key. §2.12
separates what is a first-hand source (the implementation's own code,
documentation or paper) from what is this lane's reading of it.

---

## 0. The answer in one paragraph

Yes — several production engines assign capture groups from a DFA-class
automaton, and they split into exactly **two families that do different
things**. The first family, **the two-pass hybrid**, does *not* capture in
the DFA at all: a DFA finds the match bounds fast, and a second,
capture-capable engine (an NFA simulation, a bounded backtracker, or a
one-pass DFA) runs *only on the bounded span* to assign the groups. RE2,
Rust's `regex`, and .NET's `NonBacktracking` engine all do this, and the
second pass is where the captures actually come from. The second family,
**tagged automata (TDFA)**, genuinely records submatch positions *inside* a
deterministic machine: the DFA's transitions carry register operations that
copy input positions into tag variables, so one pass yields the parse.
Laurikari invented it, Kuklewicz corrected its POSIX disambiguation,
Trofimovich added one-symbol lookahead and shipped it in re2c; TRE and
Haskell's `regex-tdfa` are the other real implementations. A third, narrower
thing sits between them: the **one-pass DFA** (RE2's `OnePass`, Go's
`onepass`, `regex-automata`'s `dfa::onepass`), a true DFA that reports
capture spans for the subset of patterns with no ambiguity at any
alternation — and it is the only construction in the survey that delivers
**Perl/PCRE leftmost-first** capture semantics from a DFA. The published
TDFA constructions deliver leftmost-**greedy** or POSIX leftmost-longest,
not PCRE's full preference order with lazy operators. Hyperscan and PCRE2's
own `pcre2_dfa_match` report no captures at all, each for a stated reason.

**And the finding that reframes the question for pcrec: pcrec already
implements the two-pass hybrid, in production, and has since [M4.6].** Its
`RX_VM_PREFILTER "hybrid"` / `RX_VM_PREFILTER_LANG "exact"` artifacts are
the RE2/Rust shape — a forward+reverse DFA pair hands the VM an exact
anchored window and the VM assigns the captures on it. Measured here over
pcrec-bench's `capability` set at the shipped default: **26 of 64 patterns
are on the VM because of a capture group, and 17 of those 26 already run
that exact two-pass hybrid.** Of the 9 that do not, **7 are patterns no DFA
can express** (6 backreference, 1 subroutine call) and 2 are the
nullable-language decline [OPT-4.2] already owns. So "adopt the RE2 shape"
is not an available mechanism — it is shipped, and its unserved population
on this subbench is two patterns, for a reason that has nothing to do with
captures. The live question is the narrower one: should the DFA assign the
captures *itself*, removing the second pass.

---

## 1. What pcrec has today

### 1.1 The DFA route already computes a leftmost-first END and a START

`src/gen/emit_dfa.c:1-11` states the shape, and it is the same two-pass
structure RE2 and Rust use:

> `ENG_UNANCH` (patterns without `^` …): one O(n) forward pass over the
> subject with the unanchored priority DFA (finds the leftmost-first match
> END), then a backward pass with the non-pruning reverse DFA (earliest
> accepting position = match START).

The priority construction is `docs/dev/decisions.md` **D3** (2026-08-09):
DFA states are priority-ordered NFA state lists, a closure that reaches
ACCEPT prunes lower-priority states and marks the DFA state accepting, and
the runtime records the last accept position seen. D3's own closing
sentence names the limit this survey is about: *"Revisit-when: captures
(M4) need tagged automata or VM anyway."*

The emitted text confirms it. For `[a-z]+@[a-z]+` at default axes
(`RX_ENGINE "dfa"`, `RX_DFA_SCAN "unanchored"`), the forward loop keeps
`last_accept_position`, the reverse loop walks back from it keeping
`match_start_position`, and then:

```c
if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)match_start_position;
                     capture_spans[0][1] = (ptrdiff_t)match_end_position; }
```

**Slot 0 and nothing else.** That is the whole of what pcrec's DFA writes.

For `^`-anchored patterns the shape is `ENG_ATTEMPT` and the forward pass
runs per start position under a three-valued bound
(`src/gen/emit_dfa.c:6806-6812`): `0` when fully `^`-anchored,
`search_from` when fully `\G`-anchored, `subject_length` otherwise.

### 1.2 The DFA can PROMISE capture pairs but can never SET one

`dfa_artifact_ncaps` (`src/gen/emit_dfa.c:510`) returns `ngroups + 1`, so a
DFA artifact may carry `RX_NCAPS > 1`. That is [DD-14] wave G's
dead-capture elision: a group whose only occurrence sits under a `{0}` or
is reached only through a capture-transparent subroutine call can never be
written, PCRE2 still counts it and still reports it unset, so the artifact
must promise it. The DFA discharges that promise by filling the pairs with
`PCREC_UNSET` once at entry (`src/gen/emit_dfa.c:670-687`), gated on
`fit.chosen == ENGM_DFA` so the same emitter's second customer — the VM
hybrid's internal prefilter — does not inherit the loop.

So the DFA's relationship to captures today is exactly: **it can answer
"unset", and it can answer group 0. It has no mechanism that assigns a
position to a group.**

### 1.3 The VM assigns captures from trailed slots, published at close

Engine selection routes any pattern with a live capture to the VM:
`forces_captures` (`src/opt/select_engine.c:107`) sets
`*why = "capture group"` at `:141` and returns `ENGM_VM`. That is the
`RX_ENGINE_WHY "capture group"` population `cycle1_analysis.md` §2.3(a)
buckets.

The VM keeps one slot pair `(2g, 2g+1)` per group and reports at the end
(`src/gen/emit_vm.c:12009-12023`):

```c
capture_spans[0][1] = (ptrdiff_t)match_start + match_length;
for (group = 1; group < RX_NCAPS; group++) {
    capture_spans[group][0] = run->slot_values[2 * group];
    capture_spans[group][1] = run->slot_values[2 * group + 1];
}
```

The discipline that makes those slots correct under repetition is
[M6.5.2]'s **publish-at-close** (`src/gen/emit_vm.c:1052-1085`): the
opening position goes to a PENDING slot and the `(start, end)` pair is
published together at the closing position, because a write-on-traverse
model leaves iteration *n*'s start beside iteration *n−1*'s end and an "is
it set" test passes on a pair that is not a capture. That was measured
arm-versus-arm over 5,808 cells: publish-at-open gives 138 divergences and
40 reversed spans, publish-at-close gives 0 and 0.

**This matters to the survey.** Every TDFA construction faces the same
problem under repetition, and it is the reason a tagged machine needs
register *copy* operations and a disambiguation rule rather than a single
"last write wins" store. The .NET engine's documented limitation —
*"Multiple captures of a single group are not supported, only the last
one is"* — is the same territory, answered by declining the feature.

### 1.4 The hybrid IS the two-pass design, already in production

When the VM is chosen for a capture-only reason and the pattern carries no
backreference and no subroutine call, `fit->prefilter`
(`src/opt/select_engine.c:819-826`) turns on, and
`src/gen/emit_vm.c:11665-11679` emits the DFA under a private name with
this comment in the artifact:

> The capture-erased forward+reverse DFA pair, emitted by the SAME emitter
> the DFA-only artifact uses (`src/gen/emit_dfa.c`), under a private name.
> It is not an over-approximation: D31 erases the group at parse time and
> `A_CAP` is invisible to the NFA builder, so this IS the machine the
> capture-erased pattern compiles to … It hands the VM an anchored window
> so the VM never scans the subject.

The `--emit-ir` listing says the same thing in one line
(`src/gen/emit_vm.c:8936-8940`): *"the capture-erased forward+reverse DFA
pair hands the VM an exact window (§6.1); the VM never scans."*

And the emitted search entry is, verbatim from a compile of
`([a-z]+)@([a-z]+)` at `--features all`:

```c
{
    ptrdiff_t window[1][2];
    if (rx_prefilter(subject, subject_length, search_from, window) != 1) return 0;
    attempt_position = (size_t)window[0][0];
    window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;
}
rx_run_state_init(run);
…
for (;;) {
    ctx.pos = attempt_position;
    result = rx_match_anchored(&ctx, run, window_end);
    …
}
if (capture_spans) rx_report_captures(run, capture_spans, attempt_position, result);
```

That is the RE2 / `regex-automata` meta-engine shape, line for line: a DFA
pass produces `[start, end)`, a capture-capable engine runs anchored inside
it, the DFA never touches a group and the VM never scans the subject.

**Two qualifications the tree states about itself, and both are load-bearing
for §3.**

**(i) The END is used as a pruning ceiling, not as a hard bound.**
`v->mrl_win` (`src/gen/emit_vm.c:9899-9902`) is
`job->fit.prefilter && !pcrec_has_atomic(root) && !pcrec_has_lookaround(root)
&& !job->fit.prefilter_collapsed`. Only on that predicate does `window_end`
become `min(window[0][1], n)`; otherwise it is the subject end, because an
atomic group or a lookaround makes the erased machine a superset whose span
END is not a bound. `window_end` then feeds the MRL length-prune macro
(`src/gen/emit_vm.c:97-99`) — it kills a path whose remaining *minimum
width* cannot fit, and nothing else. **The VM still searches for an end the
DFA has already computed exactly.**

**(ii) Span-equality between the priority DFA and the VM is BELIEVED, not
proven, and the tree deliberately does not rest a correctness property on
it.** `src/gen/emit_vm.c:12199-12213` writes the structural argument out —
the prefilter is the capture-erased machine, it accepts exactly the
pattern's language, it reported `s[win[0][0], win[0][1])` is in that
language, so the VM finds a match anchored at `win[0][0]` and the retry is
dead code — and then refuses to use it:

> That argument rests on span-equality between the two machines, which R21
> SPLIT into "erasure STRUCTURAL, span-equality BELIEVED-WITH-GATE" after
> finding two live priority miscompiles (K17, K18) in exactly this
> territory. Resting an unsound-direction correctness property on a believed
> claim is what the ruling forbids, and 0-firings-in-99-trials is explicitly
> not a discharge.

RE2 and Rust rest on precisely this claim and pay for it with differential
testing. pcrec has a written ruling against doing so, and has the gates that
would discharge it instead. §3.1 is where that bill comes due.

### 1.5 The census: where the 64 `capability` patterns actually sit

Measured for this survey. Every `.rx` export in
`/Users/fdicostanzo/pcrec-bench/bench/capability/patterns` (read-only)
compiled by this worktree's own `build/pcrec` at the **shipped default**
(`--features all`, captures on, engine auto), stamps read off the emitted
`.c`. Reproduction: `docs/dev/optloop/capsurvey_census.py`, output
`docs/dev/optloop/capsurvey_census.tsv`.

| `RX_ENGINE` | `RX_VM_PREFILTER` | `RX_VM_PREFILTER_LANG` | count |
|---|---|---|---|
| `dfa` | — | — | 24 |
| `vm` | `hybrid` | `exact` | **26** |
| `vm` | `hybrid` | `count-collapsed` | 1 |
| `vm` | `none` | — | 11 |
| (refused) | | | 2 |

The 11 with no prefilter, each with the reason its own `--emit-ir`
`prefilter` line gives:

| reason | patterns |
|---|---|
| `no-backreference` (6) | `doubled-word`, `dup-param-detect`, `phone-palindrome-6`, `quoted-delim-match`, `tag-depth3-bound`, `tag-pair-match` |
| `no-linked-call` (3) | `balanced-parens-rec`, `bracket-array-define`, `nested-comment-rec` |
| `no-nullable-exact` (2) | `evil-alt-nested` (`^(([a-z]+)*)+$`), `trim-nested-star` (`^(\s+)*$`) |

The two refusals are `negation-scope-lookbehind-var` (variable-length
lookbehind, a module gap) and `wild-datetime-datefinder-alternation` (the
500,000-byte emitted-code cap); `cycle1_analysis.md` §1.2 already
dispositions both.

`wild-logparse-syslogbase-expanded` is the single `count-collapsed` row:
its prefilter is built from [OPT-4]'s count-collapsed superset, so its span
START is a lower bound the VM verifies from and its span END is not a bound
at all — `prune-ceiling` reads `subject-end` on it.

**The table above is the wrong cut for this survey's question, and the right
one is sharper.** "VM with a hybrid prefilter" is not the same population as
"VM *because of a capture group*": the same 38 VM rows split by
`RX_ENGINE_WHY` as well, and the cross-tab is what answers the brief.

| `RX_ENGINE_WHY` | `hybrid` | `none` | total |
|---|---|---|---|
| `capture group` | **17** | **9** | **26** |
| `(?>...)` atomic | 3 | 0 | 3 |
| `(?=...)` / `(?!...)` / `(?<=...)` / `(?<!...)` lookaround | 7 | 0 | 7 |
| `(?R)` / `(?&name)` recursion | 0 | 2 | 2 |
| | 27 | 11 | 38 |

So **26 of 64 patterns are on the VM because of a capture group**, and
**17 of those 26 already run the exact two-pass hybrid.** The other 9 are:

| reason the prefilter was declined | count | patterns |
|---|---|---|
| `no-backreference` | 6 | `doubled-word`, `dup-param-detect`, `phone-palindrome-6`, `quoted-delim-match`, `tag-depth3-bound`, `tag-pair-match` |
| `no-nullable-exact` | 2 | `evil-alt-nested` (`^(([a-z]+)*)+$`), `trim-nested-star` (`^(\s+)*$`) |
| `no-linked-call` | 1 | `nested-comment-rec` |

(The two remaining `none` rows — `balanced-parens-rec` and
`bracket-array-define` — are the recursion `RX_ENGINE_WHY` rows; they carry
no capture reason at all.)

**Read that against the brief's question and it answers it directly.** Of
the 9 capture-forced patterns where the two-pass hybrid does not run,
**7 are patterns no DFA-class automaton can express** — a backreference
erasure is not even a superset once the referenced group's transitive
closure holds an assertion or an atomic operator
(`src/opt/select_engine.c:571-603`, with 12 of 18 positive-control cells
measured as false negatives), and erasing a subroutine call yields a
*different language*, not a superset. Those stay VM, permanently, under
every mechanism in this survey. The remaining 2 are [OPT-4.2]'s
nullable-language decline, which `docs/dev/f2_rescue_split.md` has already
measured and ruled cannot narrow by capture location.

**Two population facts worth recording, because a later reader will
otherwise assume them.**

- **The other 10 hybrid rows carry NO captures** (`RX_NCAPS == 1`): they
  are on the VM for an atomic group or a lookaround, and their prefilter is
  pure scan avoidance. They are also the rows where `mrl_win` is FALSE by
  construction (`src/gen/emit_vm.c:9899-9902` excludes both constructs), so
  their window END is not a bound either — which means **every hybrid row in
  this set that has captures has an exact end, and every hybrid row that has
  an exact end has captures.** The two properties coincide on this
  population, and nothing makes them coincide in general.
- **[DD-14] wave G's dead-capture elision has ZERO population here.** All
  24 `dfa` rows read `RX_NCAPS 1`, so not one of them is the
  "DFA artifact that promises permanently-unset groups" case §1.2
  describes. The mechanism is real and shipped; this subbench does not
  reach it, and a claim about it must not be read off this census.

---

## 2. The survey

One section per engine or technique. Each states the mechanism, the
disambiguation semantics it delivers, worst-case complexity and automaton
size, whether it handles backreferences / lookaround / recursion or bails,
and its sources.

### 2.1 RE2 — DFA for bounds, then OnePass / BitState / NFA on the span

**Mechanism.** RE2 does not capture in its DFA. Its DFA answers "does it
match" and "where does it end", and — by compiling a reversed program and
running the DFA backward from the end — "where does it start"
([Cox10], §"DFA"). Capture groups come from one of three other engines,
chosen by pattern and input size: `OnePass` for unambiguous patterns,
`BitState` (a backtracker with a visited-state bitmap) when the regexp and
the string are both small, and the Pike-VM `NFA` otherwise. [Cox10] states
the selection rationale directly: *"on tiny texts, OnePass outruns even the
DFA"*, and BitState is used *"when the bitmap is at most 32 kilobytes"*.

**`OnePass` is the exception — a true DFA that reports capture spans.**
[RE2onepass] defines the criterion in the source's own words:

> One-pass regular expressions have the property that at each input byte
> during an anchored match, there may be multiple alternatives but only one
> can proceed for any given input byte.

Its examples: one-pass `x*yx*`, `([^ ]*) (.*)`, `(\d+)-(\d+)`, `x(y|z)`;
not one-pass `x*x`, `(.*) (.*)`, `(\d+).(\d+)`, `(xy|xz)`. The performance
claim is in the same comment: *"On a one-pass regular expression, the NFA
code runs at about 1/20 of backtracking PCRE speed. In contrast, this code
runs at about the same speed as PCRE"*, because the capture registers are
never copied — and *"repeated copying of the capture registers is the main
performance bottleneck in the NFA implementation."*

**Disambiguation.** Leftmost-first (Perl mode) or leftmost-longest (POSIX
mode), selected at compile time; the DFA's priority-pruning is what yields
leftmost-first, exactly as pcrec's D3 does.

**Complexity and size.** The DFA is built lazily with a bounded cache and
falls back when the budget is exhausted. `OnePass` is bounded at **65,000
states** (a 16-bit node index), a `kMaxOnePassCapture` limit on capture
pairs (5 capturing parens, `$0`–`$4` in the shipped constant), and memory
capped at one quarter of the overall DFA budget.

**Backreferences / lookaround / recursion.** None supported at all — RE2
does not implement them, so there is no bail-out path; the pattern is
rejected at compile time.

Sources: [Cox10]; [RE2onepass] (`re2/onepass.cc`, first-hand).

### 2.2 rust-regex / `regex-automata` — the same split, with more engines

**Mechanism.** `regex-automata`'s meta engine composes a lazy (hybrid) DFA,
a fully compiled DFA, a `PikeVM`, a `BoundedBacktracker` and a one-pass
DFA. [Gal23] states the strategy in one sentence:

> it is usually faster to run the lazy DFA first to find the bounds of a
> match, and then only run the `PikeVM` or `BoundedBacktracker` to find the
> capture group offsets.

The start of the match comes from a **reverse DFA** run backward from the
discovered end — the same trick RE2 uses and the same one
`src/gen/emit_dfa.c` already emits.

**`dfa::onepass` is the capturing DFA.** [RAonepass] is explicit that it is
*"the only DFA capable of reporting the spans of matching capturing
groups"*. Its definition of one-pass is "there is never any ambiguity about
how to continue a search": `a*b` qualifies, `a*a` does not; `(?-u)\w*\s`
qualifies in ASCII mode and `\w*\s` does **not** in Unicode mode, because
the UTF-8 automata for `\w` and `\s` overlap — a detail worth noting for
pcrec, whose `utf8` backend is byte-wise for the same reason RE2's is.

**Unanchored searches are structurally impossible for a one-pass DFA.**
[RAonepass] explains: an unanchored search prepends `(?s-u:.)*?`, which
matches any byte, so *"adding anything after"* it makes the overall pattern
not one-pass. The high-level APIs force anchored mode; the low-level
`try_search` returns an error for an unanchored request.

**Disambiguation.** Leftmost-first (Perl) throughout; the crate also offers
a leftmost-longest (`all`) match kind for the non-capturing engines.

**Complexity and size.** One-pass construction is O(n) in NFA states
against a general DFA's O(2^n) — [RAonepass] states the contrast directly.
Limits are documented as unconfigurable and "somewhat small" for the number
of explicit capturing groups, large for patterns and total states. The
`BoundedBacktracker` gives worst-case O(m·n) time at O(m·n) space and is
therefore restricted to small haystacks; the `PikeVM` is the unrestricted
fallback at O(m·n).

**Backreferences / lookaround / recursion.** None supported; rejected at
compile time.

Sources: [Gal23]; [RAonepass]; [RAhyb].

### 2.3 Laurikari's TNFA/TDFA and TRE — the original tagged automaton

**Mechanism.** [Lau00] introduced *tagged transitions*: an NFA whose
transitions carry **tags**, numbered markers whose positions in the input
are what a submatch is. Determinizing a TNFA yields a TDFA whose states
carry a mapping from tags to **registers** and whose transitions carry
**register operations** — copies and "set to current position" — so a
single deterministic pass leaves the submatch positions in the registers.
Laurikari proved the determinization terminates. [Lau01] is the thesis
treatment.

TRE is Laurikari's own implementation. Its `lib/README` names the pipeline:
`tre-compile.c` converts the AST to a *tagged AST* with *"appropriate
minimized or maximized tags added to keep track of submatches"*, then to a
TNFA without epsilon transitions; `tre-match-parallel.c` *"takes a string
and a TNFA and finds the leftmost longest match and submatches in one
pass"* in O(l); and `tre-match-backtrack.c` is *"a traditional backtracking
matcher"* at O(k^l) that *"can handle back references"*, dispatched by
`regexec.c` according to the features the pattern uses.

**Disambiguation.** TRE's parallel matcher claims **POSIX leftmost-longest**.
Its *syntax* nevertheless accepts minimal repetition (`*?`, `+?`, `??`,
`{m,n}?`) — *"Adding a `?` to a repeat operator makes the subexpression
minimal, or non-greedy"* [TREsyntax] — and the *minimize/maximize* tag
distinction in the tagged AST is the machinery that would express it. **This
lane could not confirm from TRE's own documentation whether the parallel
matcher honours minimal repetition or whether such patterns are routed to
the backtracker**, and the README's "leftmost longest" sentence is written
without qualification. Treated as uncertain; see §2.12.

**Complexity and size.** Linear in the input for the parallel matcher;
determinization is subset construction and carries its exponential
worst case, plus register allocation on top.

**Backreferences / lookaround / recursion.** Backreferences: supported, by
falling back to the backtracking matcher (exponential). Lookaround:
not supported. Recursion: not supported.

Sources: [Lau00]; [Lau01]; [TREreadme]; [TREsyntax].

### 2.4 re2c's TDFA(1) — captures inside a real DFA, shipped

**Mechanism.** [Tro19] extends Laurikari's algorithm with **one-symbol
lookahead**, giving TDFA(1) against baseline TDFA(0) *"by analogy with LR
parsers LR(1) and LR(0)"*. The lookahead lets the determinizer defer a tag
write until the next symbol disambiguates it, which *"results in significant
reduction of tag variables and operations on them"*. [Tro20] is the
engineering write-up; [BT22] gives the full pseudocode, the optimizations,
and both ahead-of-time and just-in-time determinization variants.

This is the closest thing in the survey to "capturing with a DFA" in the
plain sense: the machine is deterministic, it makes one pass, and the
submatch positions fall out of register operations attached to its
transitions.

**Disambiguation — the brief asked to check this, and the check passes with
a caveat.** re2c's own manual [re2cman] offers both policies as separate
options: `--captures` / `--leftmost-captures` for *"submatch extraction with
leftmost greedy capturing groups"*, and `--posix-captures` / `-P` for POSIX.
[Tro19] formalizes Kuklewicz's POSIX algorithm and shows the resulting TDFA
are *"as efficient as Laurikari TDFA or TDFA that use leftmost greedy
disambiguation"*. [BT21] and [BT22] carry the correctness work, adapting
Okui and Suzuki's POSIX formulation [OS10].

**The caveat is the one that matters to pcrec: leftmost-greedy is not
PCRE leftmost-first.** re2c's regular-expression syntax has **no lazy
operator** — the manual documents `*`, `+`, `?` and `{n,m}` and nothing
non-greedy [re2cman], and the request for `a+?` was raised as an issue
against the project ([re2cIssue208]) rather than answered by existing syntax.
Leftmost-greedy coincides with PCRE preference exactly on patterns whose
every quantifier is greedy and which contain no atomic group, possessive
quantifier, backreference or lookaround. PCRE's preference order is a
strict superset, and no published TDFA construction this lane found proves
its disambiguation correct for it.

**Complexity and size.** [BT22]'s own claim about the run-time cost is the
useful one: *"The number of registers and operations depends only on the RE
structure and tag density, but not on the input string, therefore it adds
only a constant overhead to the DFA execution."* So matching is linear in
the input with a constant factor above ordinary DFA recognition; [Tro19]'s
experiments report lookahead TDFA *"considerably faster and usually smaller
than baseline TDFA; and … reasonably close in speed and size to ordinary
DFA used for recognition"*. Determinization carries subset construction's
exponential worst case. [BT22] also notes that **bounded repetition is not
desugared**: *"Bounded repetition is usually desugared via concatenation,
but we avoid desugaring as it may duplicate tags and change submatch
semantics in a RE."*

**Backreferences / lookaround / recursion.** None. re2c is a lexer
generator over regular languages; these constructs are outside its input
language, not bailed out of.

Sources: [Tro19]; [Tro20]; [BT21]; [BT22]; [re2cman]; [re2cIssue208]; [TDFAwiki].

### 2.5 Kuklewicz's `regex-tdfa` — POSIX submatch in Haskell

**Mechanism.** A pure-Haskell TDFA engine for `regex-base`, *"inspired by
the algorithm (and Master's thesis) behind the regular expression library
known as TRE or libtre"* [RegexTDFA]. Its historical significance is larger
than its usage: Kuklewicz's implementation is what answered, affirmatively,
the question of whether a TDFA can do **POSIX** disambiguation correctly —
[Tro19] formalizes what Kuklewicz had described informally, and [TDFAwiki]
records the sequence.

**Disambiguation.** POSIX leftmost-longest, with correct submatch capture;
the package's own documentation makes the correctness claim its selling
point against the C libraries.

**Complexity and size.** [RegexTDFA]: *"Matching input text of length N
should have O(N) runtime, and should have a maximum memory bounded by the
pattern size that does not scale with N."* Its own caveat: *"Regexes with
large character classes combined with {m,n} are very slow and
memory-hungry"* — the same bounded-repetition-times-class blow-up pcrec
knows as K25 and [ART-SIZE].

**Backreferences / lookaround / recursion.** None supported.

Sources: [RegexTDFA]; [TDFAwiki].

### 2.6 .NET `RegexOptions.NonBacktracking` — three passes, captures in the third

**Mechanism.** [Mos23+] is the derivative-based, symbolic algorithm .NET 7
shipped; it is not a classical DFA but a derivative automaton built lazily
over a symbolic alphabet, and it behaves as a DFA for recognition. The match
is produced in **three passes** [DotNetDeepDive]: a forward pass over
`.*?` + pattern that records the last nullable position (the match end); a
**reverse pass** over the reversed pattern, walked backward from that end,
to find the match start; and a third pass, over the matched span only, that
generates the match.

**Captures replaced that third pass.** [DotNetPR65129], the PR that added
them, states it directly: it substitutes *"the third phase of the match
generation algorithm with an NFA simulation that includes additional effects
to record capture group starts and ends on transitions"*, resting on *"a new
variant of the symbolic version of the Antimirov derivative that only
includes the parts of the pattern that the backtracking engine would visit
before hitting a nullable path"*, and *"maintaining a prioritized set of
states in the NFA simulation"* so that backtracking match-generation
semantics are faithfully reproduced.

So .NET is squarely in the two-pass-hybrid family: **the deterministic
machine finds the bounds, an NFA simulation with effects assigns the
groups.** The PR is explicit about the cost — *"NFA simulation with
application of effects is significantly more heavy weight than DFA
simulation"* — and about the overhead vanishing when no groups are present
or `ExplicitCapture` is used.

**Disambiguation.** PCRE/Perl-style leftmost-first with greedy and lazy
priorities, deliberately: the whole point of the paper's title is that the
non-backtracking engine *"preserves backtracking semantics"*, and [Mos23+]
carries a formal correctness proof — as far as this lane found, the only
one in the survey for an industrial matcher.

**Complexity and size.** Linear in the input for the DFA phases with a
bounded lazy-derivative cache and an NFA fallback when the cache is
exhausted; the capture phase runs only over the matched span.

**Backreferences / lookaround / recursion.** Backreferences: not supported;
the .NET pattern falls back to the backtracking engine. Lookaround:
supported, and [Mos23+] states the theory is *"extensible with
lookarounds"*. Recursion: .NET has no recursion construct.

**Limitation to note.** *"Multiple captures of a single group are not
supported, only the last one is"* [DotNetPR65129] — the `Captures`
collection a backtracking .NET match exposes is not reproduced. PCRE and
pcrec have no equivalent of that collection, so it is not a constraint
pcrec would inherit.

Sources: [Mos23+]; [DotNetPR65129]; [DotNetDeepDive] (secondary, see §2.12).

### 2.7 Go's `regexp` `onepass` — the same one-pass idea, third implementation

**Mechanism.** Go's standard library carries a one-pass machine in
`src/regexp/onepass.go`, whose own comment says: *"Some regexps can be
analyzed to determine that they never need backtracking: they are guaranteed
to run in one pass over the string without bothering to save all the usual
NFA state"*, and states the condition as *"at any `InstAlt`, there must be
no ambiguity about what branch to take"* [GoOnepass]. It records captures
through the program's `InstCapture` instructions, counted as `NumCap`.

**Practical limit.** The conversion is abandoned for programs of 1,000 or
more instructions, because checking feasibility becomes too expensive.

**Disambiguation.** Leftmost-first (Go's `regexp` is RE2's semantics, Perl
mode by default, with `POSIX` variants available for the leftmost-longest
match kind).

**Backreferences / lookaround / recursion.** None supported.

Sources: [GoOnepass] (first-hand source comments).

### 2.8 Hyperscan / Vectorscan — offsets only, no captures, and why

**Mechanism.** Hyperscan [Wan19+] decomposes a pattern into literal
factors and automaton fragments and matches them with SIMD string matching
plus NFA/DFA engines, in **streaming, multi-pattern, all-matches** mode.

**It reports no captures, by design.** Its own documentation lists
*"Backreferences and capturing sub-expressions"* among unsupported
constructs, and says of parentheses: *"Parenthesization, including the named
and unnamed capturing and non-capturing forms. However, capturing is
ignored."* [HSdoc]

**The reason is the matching model, not the automaton.** Hyperscan's
*"default behaviour is only to report the end offset of a match"* [HSdoc].
Even obtaining the *start* offset is an opt-in feature with a stated price:
`HS_FLAG_SOM_LEFTMOST` gives *"the leftmost possible start offset"* at the
cost of *"reduced pattern support … tracking SOM is complex and can result
in Hyperscan failing to compile a pattern with a 'Pattern too large'
error"*, plus increased stream state and a performance overhead. And the
semantics are not PCRE's at all: scanning `/foo.*bar/` against
`fooxyzbarbar` returns **two** matches, at the ends of `fooxyzbar` and
`fooxyzbarbar`, where libpcre reports one greedy match. A capture is a
statement about *which single parse won*; an engine that reports the set of
all match ends has not chosen a parse, so there is nothing to report
captures for. Vectorscan is a fork of Hyperscan and inherits the model.

Sources: [HSdoc]; [Wan19+].

### 2.9 PCRE2's `pcre2_dfa_match` — no captures, and it says why

**Mechanism.** PCRE2's alternative matching function runs a parallel
simultaneous-paths simulation (a lockstep NFA simulation, not a
determinized machine), finds **all** matches at one start position, and
returns them in the output vector in decreasing order of length — POSIX-ish
leftmost-longest at the top, rather than leftmost-first.

**No captures.** [PCRE2matching] gives the reason in one sentence:

> when dealing with multiple paths through the tree simultaneously, it is
> not straightforward to keep track of captured substrings for the different
> matching possibilities … PCRE2's implementation of this algorithm does not
> attempt to do this. This means that no captured substrings are available.

Everything that depends on captures falls with them: backreferences,
conditionals testing a backreference or a specific group recursion, script
runs, scan-substring assertions. The function also does not support `\K`,
`\C` in UTF modes, the backtracking control verbs other than `(*FAIL)`,
`PCRE2_MATCH_INVALID_UTF`, or the JIT.

**This is the most direct statement in the survey of the difficulty pcrec's
own D3 works around.** PCRE2 declines the bookkeeping; pcrec's D3 solves the
*span* half of it by pruning lower-priority threads at ACCEPT, which is
enough for group 0 and not enough for groups 1..n — which is what a tagged
construction adds.

Sources: [PCRE2matching] (first-hand, the PCRE2 documentation).

### 2.10 Others with real implementations

- **Sulzmann & Lu, POSIX parsing with derivatives** [SL14], implemented in
  Haskell as `regex-pderiv`. Partial derivatives carry a parse-tree value
  alongside the state, so submatches are a by-product of the derivative
  walk; the implementation scans right-to-left to implement POSIX. Later
  work (Ausaf, Dyckhoff & Urban, formalized in Isabelle/HOL) found the
  original correctness argument had gaps that *"cannot be filled easily"*
  and supplied simpler definitions and proofs. POSIX only; no
  backreferences, lookaround or recursion.
- **Okui & Suzuki** [OS10] — a deterministic position automaton with
  augmented transitions that translates input into a compact DAG of syntax
  trees in linear time, following the POSIX leftmost-longest rule. Not a
  shipped engine itself, but the disambiguation formulation [BT21]/[BT22]
  adapt for TDFA, so it is upstream of re2c's POSIX mode.
- **Borsotti & Trofimovich, POSIX submatch on NFA** [BT21] — the same
  family applied to a non-determinized machine, which is the honest
  alternative when determinization blows up.
- **Kleenex / optimally streaming greedy parsing** [GHR14], [Gra16+] — a
  *greedy* (leftmost-greedy) streaming parser compiled to deterministic
  streaming string transducers, decomposed into an "oracle machine" that
  performs streaming greedy disambiguation and an "action machine" that
  emits the parse. Real implementation, sustained high throughput,
  worst-case linear time. Its disambiguation is greedy, not PCRE
  leftmost-first, and it is a *parser* (it emits a full syntax tree), which
  is strictly more than captures.
- **V8 / linear JavaScript matching** [BP24] — identifies a larger subset of
  JavaScript regex matchable in linear time, corrects prior algorithms, and
  adds lookaround handling; some of it *"merged in the V8 JavaScript
  implementation used in Chrome and Node.js"*. It is a prioritized NFA
  simulation (Pike-VM family) with JavaScript's backtracking semantics, not
  a DFA — listed because it is the most recent production work on
  captures-with-backtracking-semantics-without-backtracking, and because
  JavaScript's semantics are much closer to PCRE's than POSIX is.
- **Register Set Automata** (Turoňová et al., arXiv:2205.12114) — a
  register-automaton approach to *backreferences*, not to captures; noted
  only so a later reader does not mistake it for this territory.

### 2.11 The summary table

| # | Engine / technique | Where captures come from | Disambiguation | Worst case | Backrefs / lookaround / recursion |
|---|---|---|---|---|---|
| 1 | RE2 | second engine on the DFA-found span (OnePass / BitState / NFA) | leftmost-first **or** POSIX | O(n) per pass; DFA cache bounded; OnePass ≤65k states, ≤5 capture parens | none — rejected at compile time |
| 2 | rust `regex-automata` | second engine on the lazy-DFA-found span (onepass / bounded backtracker / PikeVM); reverse DFA for the start | leftmost-first (leftmost-longest available) | O(n) DFA; PikeVM O(m·n); onepass build O(n) states | none — rejected at compile time |
| 3 | Laurikari TNFA/TDFA, TRE | **inside the DFA**, tag registers on transitions | POSIX leftmost-longest (minimal-repeat syntax exists; matcher's treatment unconfirmed) | linear match; determinization exponential worst case | backrefs → backtracking matcher, O(k^l); no lookaround/recursion |
| 4 | re2c TDFA(1) | **inside the DFA**, tag registers, one-symbol lookahead | leftmost-**greedy** (default) or POSIX; **no lazy operator in the syntax** | linear match, constant register overhead; determinization exponential | outside the input language |
| 5 | `regex-tdfa` (Haskell) | **inside the DFA**, Kuklewicz's POSIX TDFA | POSIX leftmost-longest | O(N) match, memory bounded by pattern size | none |
| 6 | .NET `NonBacktracking` | third pass: NFA simulation with effects, on the span the first two passes bounded | **leftmost-first with backtracking semantics**, formally proved | linear phases, bounded derivative cache | backrefs → backtracking engine; lookaround supported; no recursion |
| 7 | Go `regexp` onepass | **inside the one-pass DFA**, `InstCapture` | leftmost-first | linear; conversion abandoned ≥1,000 instructions | none |
| 8 | Hyperscan / Vectorscan | **none** — end offsets only; SOM opt-in for the start | all-matches, not a chosen parse | — | none; capturing parentheses parsed and ignored |
| 9 | PCRE2 `pcre2_dfa_match` | **none** — simultaneous paths, no per-path bookkeeping | leftmost-longest, all lengths returned | O(n·m) | none; backrefs and backref-conditionals fall with captures |
| 10 | Kleenex / streaming greedy | full parse tree from a deterministic streaming transducer | leftmost-**greedy** | linear in input | none |

### 2.12 Provenance — first-hand versus this lane's reading

**First-hand sources** (the implementation's own code, its own
documentation, or its authors' paper), quoted above: RE2's `onepass.cc`
comment; Go's `onepass.go` comments; the `regex-automata` crate
documentation; BurntSushi's design write-up (the crate author's); the re2c
manual; Trofimovich's and Borsotti & Trofimovich's papers; Laurikari's
papers; TRE's `lib/README` and syntax document; the `regex-tdfa` package
description; Hyperscan's developer reference; the PCRE2 `pcre2matching`
documentation; the `dotnet/runtime` PR description for captures support;
Moseley et al.'s PLDI paper record.

**Secondary, and flagged as such.** The three-phase description of .NET's
algorithm in §2.6 is taken from [DotNetDeepDive], a public gist by a .NET
maintainer rather than from the paper or the source; the PR quote that
*"the third phase"* was replaced is first-hand and corroborates that three
phases exist, but the per-phase detail (`.*?` prefix, last-nullable
recording, reversed-pattern backward walk) rests on the gist. [Cox10] is
the author's article series, not the RE2 source, for everything in §2.1
except the `OnePass` quotes.

**Explicitly uncertain, and left uncertain.**
- Whether TRE's *parallel* (TDFA) matcher honours minimal repetition, or
  routes such patterns to the backtracker. TRE's syntax documents `*?`
  and friends; its README describes the parallel matcher as finding *"the
  leftmost longest match"* with no qualification. Both cannot be
  unconditionally true. **Not resolved here** — it would need reading
  `tre-compile.c`'s tag assignment, which is beyond this survey's scope.
- Whether any published TDFA construction has been proved correct for a
  disambiguation policy that includes **lazy** operators. This lane found
  none. The absence of a proof is not a proof of impossibility: Laurikari's
  *minimize/maximize* tag distinction is exactly the degree of freedom a
  lazy operator needs, and it is present in the original construction. The
  honest statement is that **the published, proved constructions cover
  leftmost-greedy and POSIX, and PCRE preference is neither.**
- [BT22]'s complexity claims. The abstract makes none; the register-overhead
  sentence quoted in §2.4 is from the body as rendered by an HTML mirror,
  not from the typeset PDF (this box has no PDF text extractor). Treated as
  accurate but single-sourced.

---

## 3. What fits pcrec

D119's constraints apply: algorithmic only, no SIMD, **constrained to our
engine architecture** — *"if it turns out it would require something wholly
different that's a deferral at best"*. The four standing evaluation lenses
(memory `pcrec-design-evaluation-lenses`, wired in the root `CLAUDE.md`
situation index) are applied in §3.4.

### 3.1 (a) DFA finds the bounds, VM assigns captures on the span

**Verdict: already built. There is no mechanism here to propose, and that is
the survey's most useful single result.**

§1.4 shows the shipped artifact doing exactly what RE2 and
`regex-automata` do, and §1.5 measures its reach: **17 of the 26
capture-forced `capability` patterns at the shipped default**, plus 10 more
capture-free rows that use the same prefilter purely to avoid scanning. `src/gen/emit_vm.c:11665-11679` and the
`--emit-ir` `prefilter` line both call the window **exact**, and it is
exact for a structural reason pcrec owns — D31 erases the group at parse
time and `A_CAP` is invisible to the NFA builder, so the prefilter's DFA is
not an approximation of the pattern, it *is* the pattern's DFA.

**What pcrec's DFA already provides for it:**

- a **leftmost-first END**, from the priority forward machine (D3,
  `src/gen/emit_dfa.c:1-11`) — not a leftmost-longest end, which is the
  property that makes it usable at all under PCRE semantics;
- a **START**, from the non-pruning reverse machine walked back from that
  end — the RE2/Rust reverse-DFA trick, emitted;
- a per-attempt **re-seed**: on a failed attempt the retry recomputes the
  window from the prefilter rather than stepping one byte
  (`src/gen/emit_vm.c:12216-12222`);
- an **anchored VM entry** that never scans (`rx_match_anchored`), and
  `rx_report_captures` to publish the slots.

**What it does not do, and this is the only live item in (a).** The END is
consumed as a *pruning ceiling*, not as a *hard bound*. `window_end` feeds
the MRL macro, which kills a path whose remaining minimum width cannot
reach the ceiling; it does not tell the VM that the winning path's end is
*exactly* `window_end`. Under span-equality, a VM path that accepts at any
position other than `window_end` is not the winner and a path that would
pass `window_end` is dead — so the VM could run **anchored at both ends**,
which is a strictly stronger prune than the width test, and could fail the
whole attempt the moment no live thread can reach the known end.

**And that is exactly the claim `src/gen/emit_vm.c:12199-12213` refuses to
rest on.** R21 split "erasure STRUCTURAL, span-equality BELIEVED-WITH-GATE"
after K17 and K18 — two live priority miscompiles found in this territory.
A hard end bound would put an unsound-direction correctness property on the
believed half: if the two machines ever disagree on the span, a
both-ends-anchored VM does not merely prune less, it **deletes a real
match**. RE2 and Rust accept that exposure. pcrec has a written ruling
against accepting it on belief, and the gate that would discharge it
(`tests/codegen`'s identity gates plus the corpus differential) is the
route, not an argument.

**Which cycle-1 rows would move.** None of the ones the brief names, and
the census is why:

- The `capture group` `RX_ENGINE_WHY` population is **already on this
  path** wherever a prefilter is possible: 17 of its 26 members at the
  default, with 7 of the remaining 9 structurally out of reach of any DFA.
- The three 39,000–49,000× default-config cells
  (`cycle1_analysis.md` §1.1) are **not blocked on (a)**. `evil-alt-nested`
  (`^(([a-z]+)*)+$`) and `trim-nested-star` (`^(\s+)*$`) are the two
  `no-nullable-exact` rows: their own exact language matches the empty
  string, so the forward+reverse pair would admit a zero-length match at
  every position and could never dismiss one. That is [OPT-4.2]'s decline,
  and `docs/dev/f2_rescue_split.md` already measured that it cannot narrow
  by capture location — it is correctly keyed on global emptiness
  admission. The lever those two rows need is a **partial-admission
  prefilter** or a VM step budget, both of which that memo already names,
  and neither of which is a captures-via-DFA question.
- The third cell (`trim-nested-star`/search) is backtracking cost, which
  §4 of the cycle-1 analysis already dispositions.

**Where it cannot apply, plainly.** Backreferences, subroutine calls and
recursion: a DFA cannot express them. Not "expensively" — at all.
`src/opt/select_engine.c:571-603` measures the backreference case (the
erasure is not even a superset once the referenced group's transitive
closure holds an assertion or an atomic operator: 12 of 18 positive-control
cells are false negatives; where it *is* a superset the span is wrong on up
to 389 of 12,786 subject-family pairs) and the call case is a *different
language*, not a superset (`a(?1)b` with group 1 = `x` matches `axb`;
erase the call and `ab` does not). Those 9 rows — 7 of them capture-forced —
stay VM-only under every mechanism in this survey, permanently. Lookaround is a third case with a
different shape: the erasure *is* a sound superset, so a prefilter is built,
but its span END is not a bound — which is exactly why `mrl_win` excludes
it (`src/gen/emit_vm.c:9899-9902`).

### 3.2 (b) TDFA in pcrec — captures inside the DFA itself

**Verdict: DEFER under D119's engine constraint, and say so with the
reason rather than filing it as unranked.**

**What it would take.** A tagged construction replaces, not extends,
`src/ir/dfa.c`'s priority subset construction: states become
(NFA-state-list, tag→register map) pairs, transitions gain register
operation lists, and the interner
(`src/ir/dfa.c:809`/`:871`, which today interns on the priority-ordered
per-view list plus `eolvar`/`endvar`) must intern on the register mapping
too or the machine stops being finite. `src/opt/minimize.c`'s Hopcroft
refinement must become tag-aware — two states with identical transition
behaviour but different register operations are not equivalent — and
`docs/dev/dfa_online_minimization_study.md`'s whole analysis of the
minimization seam is written against the untagged machine. The emitter
gains a register file and a per-transition operation list, which is a new
emitted form, an `abi` event and a new size term. `tests/codegen`'s four
byte-identity gates, the sabotage matrix's DFA anchors and the
`EMITTED_BYTES` manifests all move.

**Size growth.** Three multiplicative terms on top of today's table:
determinization on tagged states produces more states than on untagged ones
(the tag map is part of the state identity), each transition carries an
operation list, and the register file is per-artifact storage. [Tro19]'s
own experimental claim is the optimistic bound — lookahead TDFA are
*"reasonably close in speed and size to ordinary DFA used for
recognition"* — and pcrec's own size posture ([ART-SIZE], the
1,000,000-byte cap, [CLS-TREE]) is the axis that would price it.

**Whether leftmost-first is supported: no, not as published.** §2.4 is the
check the brief asked for. re2c does claim both leftmost-greedy and POSIX,
and the claim holds — `--leftmost-captures` and `--posix-captures` are both
shipped options with correctness work behind them ([Tro19], [BT21],
[BT22]). But re2c's syntax has no lazy operator, and **leftmost-greedy is
not PCRE leftmost-first**: it coincides only on patterns whose every
quantifier is greedy and which carry no atomic group, possessive
quantifier, backreference or lookaround. pcrec's compatibility standard
(D26) makes *what a pattern matches* exact, so adopting a construction
proved for a different preference order would require either restricting
the TDFA route to the coinciding subset — which is a selection predicate
nobody has characterized — or extending the disambiguation proof to PCRE
preference, which is a research contribution, not an implementation.

**Against D119's constraint this is "something wholly different"**: a
different determinization, a different minimization, a different emitted
form, and a disambiguation policy whose correctness for pcrec's semantics
is unproved. Deferral is the honest disposition.

**One qualification that keeps it from being a permanent no.** `APPROACH.md`
§2's island ladder already names it: tier 3, *"VM fallback — fragments
containing capture groups (islands split at capture boundaries; **tagged
automata are a later upgrade**)"*. A tagged machine for a *fragment* is a
much smaller object than one for a whole pattern, and the island protocol
([ENG-ISL], §3.5) is where it would land. That is the shape a future
[CLS-TREE]-style study would examine, not this cycle's.

### 3.3 (c) The ONE-PASS special case

**Verdict: the one candidate in this survey that fits pcrec's architecture
as it stands, and the only one that can deliver PCRE leftmost-first
captures from a deterministic machine. Measurement-gated.**

**What it is.** A pattern is one-pass when at each input byte during an
**anchored** match at most one alternative can proceed ([RE2onepass];
[RAonepass]; [GoOnepass] all state the same criterion in their own words).
For such a pattern the NFA determinizes to a machine where each DFA state
corresponds to at most one NFA state, so a capture instruction attaches to
a transition unconditionally — no register copying, no priority set, no
second pass. Three independent production implementations exist, all under
Perl/leftmost-first semantics, which is the fit that matters.

**Why it fits pcrec specifically, and the fit is unusually close:**

1. **The criterion is a predicate over the existing IR.** pcrec's IR is
   already a Pike/PCRE2-style program with `split`, `save`, `char`, `class`
   (APPROACH.md §2). The one-pass test is "at every `split`, the two
   branches' first-byte sets are disjoint" plus "it is immediately obvious
   when a repetition ends" — a walk over that IR, in `src/opt/`, next to
   `possessify.c` and `prefix_k.c`, which already do first-set reasoning.
   No new IR, no new construction.
2. **pcrec already has an anchored entry and an anchored machine.**
   One-pass is anchored-only in all three implementations, and structurally
   so ([RAonepass]: prepending `(?s-u:.)*?` destroys the property).
   pcrec has `<prefix>_match`/`<prefix>_match_caps` (the anchored match-here
   entries), `ENG_ATTEMPT` for `^`-anchored patterns with `start_max = 0`
   (`src/gen/emit_dfa.c:6806-6812`), and — decisively — the hybrid's own
   `rx_match_anchored` is *already* the anchored capture-assigning call. A
   one-pass DFA would be a **drop-in replacement for that call**, inside the
   existing prefilter protocol, with the window unchanged.
3. **It is an engine-selection rung, not an engine.** pcrec already has a
   selection ladder with `ESEL_*` values, a drop ladder ([K53-SELRETRY]),
   and a stamp discipline. "One-pass DFA" is one more rung whose predicate
   is checkable and whose failure falls back to today's VM with no
   behavioural difference.
4. **Every implementation caps it, and pcrec has `limits.def`.** RE2 caps at
   65,000 states and 5 capture pairs; Go abandons at 1,000 instructions;
   Rust documents a "somewhat small" group limit. Those are exactly
   `src/core/limits.def` rows.

**What it would buy, and where.** Today a hybrid-exact artifact pays a DFA
pass over the subject *and* a VM pass over the match span. A one-pass DFA
pays one pass and assigns the captures on the way. That is worth nothing
where matches are rare and the subject is long (the DFA prefilter dominates
and the VM span is tiny — which is precisely why cycle 1's winners are
already at the §2.2 floor on those rows), and worth the whole second pass
where **the subject *is* the match**: the `match` regime, `^`-anchored
patterns, and find-all sweeps over match-dense subjects. RE2's own comment
says the same thing from the other side — *"on tiny texts, OnePass outruns
even the DFA"*.

**What it cannot do.** Ambiguous patterns — which is most interesting ones.
`(.*) (.*)`, `x*x`, `(xy|xz)` are all out, and so is any pattern under
`utf8` whose classes have overlapping UTF-8 encodings ([RAonepass]'s
`\w*\s` example), which is a real narrowing for pcrec's byte-wise UTF-8
automata. **The reach is unknown and that is the blocking unknown**, not a
detail — see §3.6.

### 3.4 Ranking, against the four lenses and D119

| lens | (a) DFA bounds + VM on the span | (b) TDFA | (c) one-pass DFA |
|---|---|---|---|
| **specific vs general** | general — and already the general mechanism; nothing to add | general, and *too* general: it changes every DFA pattern's construction to serve the capture-bearing ones | specific by construction (a pattern subset), but the PREDICATE is general and the emitted form reuses the existing anchored entry |
| **core vs derived** | core, shipped | core — replaces determinization and minimization, the two most load-bearing passes | derived: an analysis over the existing IR plus a selection rung; neither construction moves |
| **applicable vs assumption-changing** | applicable; the one open item (a hard end bound) *is* assumption-changing, because it converts R21's believed span-equality into a correctness dependency | assumption-changing at the root: adopts a disambiguation policy (leftmost-greedy or POSIX) that is not PCRE's, with no published proof for PCRE's | applicable: leftmost-first is what all three implementations deliver, and a failed predicate falls back to today's artifact unchanged |
| **fits-arch vs refactor** | fits — it *is* the architecture | refactor, and the largest one available: new state identity, tag-aware minimization, new emitted form, `abi` event, every DFA gate and anchor moves | fits: one `src/opt/` pass, one selection rung, one emitter variant behind the existing anchored call |

**Ranking: (c) > (a)'s residual > (b).**

1. **(c) one-pass** is the only proposable mechanism. It is architecturally
   additive, delivers the right semantics, has three independent production
   precedents, and its failure mode is "fall back to today". It is gated on
   a reach measurement (§3.6) and on nothing else.
2. **(a)'s residual** — making the DFA's known END a hard bound on the VM
   run — is small, cheap and *already sitting in the tree behind a written
   ruling*. It is a legitimate candidate only if the span-equality claim is
   discharged by a gate rather than argued, which is a testing task with a
   clear shape (the corpus differential already compares spans; what is
   missing is a control that would *fail* if the two machines disagreed).
   Its payoff is unmeasured and plausibly small, since the MRL ceiling
   already covers the width case.
3. **(b) TDFA** is a deferral with a recorded reason, which under D119
   item 3 is a result rather than a failure. Its re-open condition is
   named: a fragment-level tagged machine under the island protocol, if and
   when §3.5's ladder makes fragment-level engines cheap.

**None of the three moves the three catastrophic default-config cells.**
That is worth stating plainly, because the brief's framing invites the
opposite conclusion. `evil-alt-nested` and `trim-nested-star` lose their
prefilter to [OPT-4.2]'s nullable decline, not to a captures-vs-DFA gap;
both are hopelessly ambiguous and so are not one-pass; and both are
`^`-anchored patterns whose `auto-nocaps` variant already runs at the
floor. Their lever is elsewhere.

### 3.5 [ENG-ISL]: is (a) the island?

**Yes, and the row already says so.** `docs/dev/plan.md`'s [ENG-ISL] row
names *"the hybrid PREFILTER (a DFA island inside the VM's entry, in
production)"* as one of three things already built that are instances of
one mechanism, alongside the [OPT-5] scan edge and [ENG-DIRECT]'s
direct-coded automaton. Frank's framing — *"islands of vm in dfa as well as
islands of dfa in vm … We're blurring the lines"* — is exactly the reading
under which (a) is not a new idea but the shipped instance.

The precise correspondence: **a DFA region whose end triggers a bounded VM
run** is the hybrid's entry protocol, where the region is the whole subject
and the VM run is bounded by the window. What the row's general form adds —
a region *inside* a machine, spliced at the region's head with the edge's
head/fall-through protocol — is the thing (c) would eventually want: a
**one-pass capturing DFA for a capture-bearing REGION**, spliced into an
otherwise-VM program, is an island of capturing DFA in the VM. And that is
`APPROACH.md` §2's own tier 3, whose text already reads *"fragments
containing capture groups (islands split at capture boundaries; tagged
automata are a later upgrade)"*.

So the island ladder's three tiers map onto this survey cleanly: tier 1 and
2 (exact and accept-list islands) are the capture-free cases already
chartered; tier 3's "split at capture boundaries" is what a one-pass or
tagged fragment engine would *stop* having to do. **(c) at whole-pattern
scope is the cheap first step of that, and it needs none of the island
protocol** — which is an argument for doing it first, not an argument that
it is the island.

### 3.6 The measurement that decides it (D77)

Two measurements, in order. Neither is run here; both are stated so an
executor can run them without re-deriving anything. Both are **compile-side
plus a bench-shaped timing run**, and the timing half belongs on
ubuntubudu via the executor channel, not on this Mac (D119's mechanics,
[OPT-5] STEP 0's precedent).

**M-A — the ONE-PASS REACH CENSUS. Compile-side, no timing, and it comes
first because a small answer kills (c) outright.**

A one-pass predicate does not exist in the tree, so the census needs a
throwaway analyzer, which is the cheapest possible form of the question:
walk the lowered IR and report, per pattern, whether **(i)** every `split`'s
two branches have disjoint first-byte sets under the pattern's encoding,
**(ii)** every repetition's exit is decided by the next byte alone (the
body's first-byte set is disjoint from the follow's), and **(iii)** the
pattern is anchored or is being compiled for the anchored entry. Run it
over three populations:

| population | why |
|---|---|
| the 17 capture-forced `hybrid`/`exact` `capability` patterns (§1.5) | the only rows where (c) would replace a VM pass that is doing capture work |
| the shipped corpus's 3,938 `pattern`/`pattern-esc` lines at `--features all` | the general reach figure, comparable to every other axis census in the tree |
| the same corpus under `-e utf8` | [RAonepass]'s overlapping-UTF-8 narrowing, measured rather than assumed |

Report the reach as a fraction and — critically — **the reach among
capture-bearing patterns only**, since a one-pass DFA for a capture-free
pattern buys nothing pcrec's DFA route does not already have. **Decision
rule:** if fewer than ~10% of capture-bearing corpus patterns are one-pass,
(c) is a special case for a handful of patterns and fails
`pcrec-general-mechanisms-not-special-cases`; the row closes with the
number. Expect the RE2/Go caps to matter: apply a ≤5-capture-pair and
≤1,000-instruction filter as a second column so the figure is comparable to
the three precedents.

**M-B — WHAT THE SECOND PASS ACTUALLY COSTS. Timing, on ubuntubudu, and
only if M-A survives.**

The question (c) turns on is not "is one pass faster than two" — it is
"what share of a hybrid-exact artifact's time is the VM pass". Measure it
without building anything, by differencing two artifacts pcrec already
emits:

```
# Population: the 17 capture-forced hybrid/exact capability patterns
#            (capsurvey_census.tsv: RX_VM_PREFILTER "hybrid" and
#             RX_ENGINE_WHY containing "capture group").
# Subjects:  the bench's own throughput subjects t-64k / t-256k / t-1m
#            (hashes pinned in cycle1_analysis.md 0.3 -- verify them or STOP),
#            plus each pattern's own `match`-regime subject, which is the
#            regime where the second pass is the whole cost.
#
# ARM 1 (both passes):   pcrec --features all              -> DFA prefilter + VM captures
# ARM 2 (first pass only): pcrec --features all --no-captures
#                          -> the SAME forward+reverse DFA, no VM at all
#
# Both arms compiled with the bench's own flags; timed with the bench's own
# find-all driver loop shape (cycle1_analysis.md 0.5).
#
# The VM pass's share is (arm1 - arm2) / arm1, per pattern per regime.
```

`--no-captures` on a hybrid-exact pattern emits the capture-erased machine
alone — which is precisely arm 1's first pass with the second removed — so
the difference is the second pass and nothing else. This is the same
variant pair `cycle1_analysis.md` §1.1 already ranks, read for a different
quantity.

**Decision rule.** (c) is worth building only where arm 1 − arm 2 is a
material share. If the VM pass is under ~10% of total time on the
throughput regime and under ~25% on the match regime, the second pass is
not the cost and (c) buys little even at full reach; if it is over half on
the match regime, (c) has a target and the reach figure from M-A says how
big. State both numbers before any design note is written.

**A third, optional measurement, for (a)'s residual only.** Before the hard
end bound could be considered, the span-equality claim needs a *control*,
not an argument: a check that compares the prefilter's `window[0][1]`
against the VM's own reported `capture_spans[0][1]` on every hybrid artifact
over the whole corpus subject sweep, and **fails** on any disagreement. It
is a differential the harness can already express, it costs one extra
comparison per case, and until it exists and has a measured non-zero
population reaching it, R21's ruling stands and the bound stays a ceiling.

---

## 4. What this survey does not settle

- **Whether any TDFA construction can be made correct for PCRE preference
  order.** §2.12 records that no published proof covers it and that
  Laurikari's minimize/maximize tags are the plausible mechanism. That is an
  open research question, not a measurement, and it is the load-bearing
  unknown under (b).
- **The one-pass reach.** M-A is the whole of (c)'s viability and it is not
  run here. Nothing in §3.3 licenses a claim about how many pcrec patterns
  are one-pass.
- **Any throughput claim.** No timing was taken for this survey, on either
  box. Every ns figure quoted comes from `cycle1_analysis.md`, which took
  them from the bench's pinned ledger.
- **TRE's treatment of minimal repetition** (§2.12), which would need a read
  of `tre-compile.c`.
- **Whether a size term should price a tagged machine's register file.** It
  is a new storage class and `src/core/limits.def` has no row shaped like
  it; the question is downstream of (b) being un-deferred and is not worth
  answering before that.
