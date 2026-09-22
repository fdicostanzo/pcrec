# capsurvey — "is anyone capturing using dfa" (2026-09-22)

Lane `capsurvey`, branch `lane/capsurvey` from main `69172a00`, opus.
**Docs-only writer**: nothing under `src/`, `cli/`, `lib/`, `tests/` or
`docs/spec/`; no timing measurement on either box; `/Users/fdicostanzo/pcrec-bench`
read-only (its `.rx` pattern exports were read, nothing there was written).
The compiler WAS built (`make -j4 CC=gcc-16`, rc=0) so that emitted C and
compile-side stamps could be read rather than inferred. Nothing owed.

## Commits

| commit | what |
|---|---|
| `615cc7a1` | WIP bring-up (empty) |
| `99d7cff3` | the survey, the census script + TSV, 27 new `REFERENCES.md` entries, two cited-by extensions, the `docs/dev/optloop/CLAUDE.md` entries |
| `1e2d0073` | citation-verification pass: two wrong `file:line` cites corrected, census numbers refined to the `RX_ENGINE_WHY` cross-tab |
| (this) | this report + its `docs/dev/lanes/CLAUDE.md` line |

## Deliverables

- `docs/dev/optloop/captures_via_dfa_survey.md` — the survey and the fit
  analysis. §1 pcrec today (every claim `file:line`), §2 ten engines with
  provenance separated in §2.12, §3 the three candidates ranked against
  D119 and the four standing lenses plus the two D77 measurements.
- `docs/dev/optloop/capsurvey_census.py` / `capsurvey_census.tsv` — the
  §1.5 census. Runnable as it stands (`PCREC`/`BENCH`/`OUT` from the
  environment), unlike the cycle-1 scripts that carry a hardcoded
  scratchpad path.
- `REFERENCES.md` — 27 entries, alphabetically inserted without moving any
  existing one; `[RAhyb]` and `[Wan19+]` cited-by lists extended.
- `docs/dev/optloop/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` — file entries.

## The answer, short

**Yes, and in two different senses.** *(1)* The two-pass hybrid — a DFA
finds the bounds, a second capture-capable engine runs on the span — is
what RE2, Rust's `regex` and .NET's `NonBacktracking` all do; the DFA never
touches a group. *(2)* Tagged DFAs (TDFA) genuinely record submatch
positions inside a deterministic machine, via register operations on
transitions: Laurikari's construction, Kuklewicz's POSIX correction,
Trofimovich's lookahead TDFA(1) in re2c, plus TRE and Haskell's
`regex-tdfa`. A third, narrower thing — the **one-pass DFA** (RE2's
`OnePass`, Go's `onepass`, `regex-automata`'s `dfa::onepass`) — is a true
DFA that reports capture spans for patterns with no ambiguity at any
alternation, and it is **the only construction in the survey that delivers
Perl/PCRE leftmost-first captures from a deterministic machine**. The
published TDFA constructions deliver leftmost-**greedy** or POSIX.
Hyperscan and `pcre2_dfa_match` report no captures at all, each for a
stated reason (§2.8, §2.9).

## Five findings, in the order they are worth reading

### F1 — pcrec already implements design (a), and the brief's framing assumed otherwise

The brief asks what pcrec's DFA would provide for a "DFA finds the bounds,
VM assigns captures on the span" mechanism. The answer is that pcrec
**ships that mechanism**. `src/gen/emit_vm.c:11665-11679` emits the
capture-erased forward+reverse DFA pair under a private name and the
artifact's own comment says it *"hands the VM an anchored window so the VM
never scans the subject"*; the `--emit-ir` listing calls the window
**exact**; the emitted search entry reads `window[0][0]`/`window[0][1]` from
the prefilter, runs `rx_match_anchored` at that start, and calls
`rx_report_captures`. That is RE2's and `regex-automata`'s meta-engine
shape line for line.

So the mechanism is not available to propose. What *is* available is the
residual: the END the DFA computes exactly is consumed only as an MRL
*pruning ceiling* (`window_end`, gated on `v->mrl_win`,
`src/gen/emit_vm.c:9899-9902`), never as a hard bound — the VM still
searches for an end the DFA already knows.

### F2 — and the tree has already reasoned about that residual, and ruled against it

`src/gen/emit_vm.c:12199-12213` writes out the structural argument that the
prefilter's span is the VM's span, and then declines to rest on it: R21
split it into *"erasure STRUCTURAL, span-equality BELIEVED-WITH-GATE"* after
K17 and K18, two live priority miscompiles in exactly this territory.
A hard end bound converts that believed claim into an unsound-direction
correctness dependency — a disagreement would **delete a real match**, not
merely prune less. RE2 and Rust take that exposure and pay for it with
differential testing. So the residual is not a design question, it is a
**gate** question, and §3.6 names the control it needs (a check comparing
the prefilter's `window[0][1]` against the VM's own reported match end on
every hybrid artifact, failing on any disagreement).

### F3 — the census's first cut was the wrong cut, and the right one changes the conclusion's shape

The first census cross-tabbed `RX_ENGINE` × `RX_VM_PREFILTER` and read
"26 of 64 already on the hybrid path, 11 with no prefilter". Splitting by
`RX_ENGINE_WHY` as well gives a different and much more useful population:

| `RX_ENGINE_WHY` | `hybrid` | `none` | total |
|---|---|---|---|
| `capture group` | **17** | **9** | **26** |
| atomic `(?>...)` | 3 | 0 | 3 |
| lookaround (four spellings) | 7 | 0 | 7 |
| recursion `(?R)` / `(?&name)` | 0 | 2 | 2 |

**"VM with a hybrid prefilter" and "VM because of a capture group" are
different sets**, and 10 of the 27 hybrid rows carry `RX_NCAPS 1` — they
are on the VM for an atomic group or a lookaround and their VM pass assigns
no groups at all. Those same 10 are exactly the rows where `mrl_win` is
false by construction, so on this population **having captures and having
an exact end coincide**, and nothing makes them coincide in general. A
later reader taking any "N of 64" figure off this subbench needs to know
which cut produced it.

Of the 9 capture-forced patterns with no prefilter: 6 backreference,
1 subroutine call, 2 the [OPT-4.2] nullable-language decline. **Seven of
the nine are patterns no DFA-class automaton can express** — not
expensively, at all — so the two-pass hybrid's genuinely unserved
population here is **two patterns**, and their cause has nothing to do with
captures. `docs/dev/f2_rescue_split.md` already owns that cause and has
already ruled it cannot narrow by capture location.

### F4 — [DD-14] wave G's dead-capture elision has zero population on this subbench

All 24 `dfa` rows read `RX_NCAPS 1`, so not one is the "DFA artifact that
promises permanently-unset groups" case. The mechanism is real and shipped
(`src/gen/emit_dfa.c:510`, `:670-687`); this population does not reach it.
Recorded in the survey rather than left for a later reader to assume the
opposite from the presence of a `dfa`-with-captures code path. (K35's
shape: a population nobody counted.)

### F5 — two of sixteen `file:line` citations were wrong, and neither was wrong by drift alone

Every `src/` citation was opened on this worktree before delivery
(`codeguide_report.md`'s own discipline). Two failed:

- **`src/ir/dfa.c:809`/`:871`** for the state interner — inherited verbatim
  from `docs/dev/dfa_online_minimization_study.md` §1 (2026-09-04) and stale
  since. Line 809 is now a comment fragment about something else. The
  interner is `intern()`/`dhash()` at `src/ir/dfa.c:896-985`. *A citation
  copied from another document in this repository is exactly as fresh as
  that document, and nothing marks it.*
- **`src/gen/emit_vm.c:97-99`** for the MRL prune macro — those are the
  macro's lines **in an emitted artifact**, not in the emitter. The emitter
  site is `:11363-11368`, and reading it revealed there are **two** macros
  (`_PRUNE_TOO_SHORT` and `_PRUNE_CLAMP_SPAN`), not one. *Citing a line
  number read off generated output produces a citation that is precise,
  checkable, and points at the wrong file — and it survives a "does this
  line exist" check.*

## The ranking delivered

Against D119's engine constraint and the four standing lenses
(specific-vs-general, core-vs-derived, applicable-vs-assumption-changing,
fits-arch-vs-refactor):

1. **(c) the ONE-PASS DFA** — the only proposable mechanism. Its criterion
   is a predicate over the IR pcrec already has, it is anchored-only and
   pcrec already has anchored entries (`rx_match_anchored` is *already* the
   anchored capture-assigning call a one-pass DFA would replace), it is a
   selection rung rather than an engine, every implementation caps it and
   pcrec has `limits.def`, and it delivers **leftmost-first** — which the
   TDFA line does not. Gated on the reach census (M-A) and nothing else.
2. **(a)'s residual** — the hard end bound. Small, cheap, and blocked on a
   gate rather than on a design, per F2. Payoff unmeasured and plausibly
   small, since the MRL ceiling already covers the width case.
3. **(b) TDFA** — a recorded **deferral** with its reason, which under D119
   item 3 is a result. It replaces determinization *and* minimization
   (`intern` must key on the register map; Hopcroft must become tag-aware),
   is a new emitted form and an `abi` event, and its published
   disambiguation policies are leftmost-greedy or POSIX, neither of which
   is PCRE preference. Re-open condition named: a *fragment*-level tagged
   machine under the island protocol, which `APPROACH.md` §2 tier 3 already
   calls *"a later upgrade"*.

**[ENG-ISL]:** (a) is exactly the island the row already names — its own
text lists *"the hybrid PREFILTER (a DFA island inside the VM's entry, in
production)"* as one of three shipped instances of one mechanism. The
island framing's live contribution here is for (c) at *fragment* scope: a
one-pass capturing DFA for a capture-bearing region, spliced with the
head/fall-through protocol, is an island of capturing DFA in the VM — and
that is `APPROACH.md` §2's tier 3, whose text already anticipates it.
**(c) at whole-pattern scope needs none of the island protocol**, which is
an argument for doing it first.

**None of the three moves the three 39,000–49,000× default-config cells**
(`cycle1_analysis.md` §1.1), and the survey says so plainly, because the
brief's framing invites the opposite conclusion. Two of them lose their
prefilter to the nullable decline, not to a captures gap, and both are
hopelessly ambiguous so neither is one-pass.

## The two measurements owed before any of this is built (D77)

Stated in full in the survey §3.6 with commands; summarized here.

- **M-A, the ONE-PASS REACH CENSUS** — compile-side, no timing, **first**,
  because a small answer kills (c) outright. Needs a throwaway predicate
  over the lowered IR (disjoint first-byte sets at every `split`;
  repetition exit decided by the next byte; anchored), run over three
  populations (the 17 capture-forced hybrid rows, the shipped corpus's
  3,938 pattern lines, the same corpus under `-e utf8` for the
  overlapping-UTF-8 narrowing), reported as reach **among capture-bearing
  patterns**. Decision rule: under ~10% and (c) is a special case and fails
  `pcrec-general-mechanisms-not-special-cases`.
- **M-B, WHAT THE SECOND PASS COSTS** — timing, ubuntubudu via the
  executor, only if M-A survives. Differences two artifacts pcrec already
  emits: `--features all` (DFA prefilter + VM captures) against
  `--features all --no-captures` (the identical forward+reverse DFA, no VM),
  on the bench's own throughput subjects plus each pattern's `match`-regime
  subject. `(arm1 − arm2)/arm1` is the VM pass's share. Nothing is built to
  take this measurement.

## What this lane did NOT settle

Listed in the survey §4 and repeated here so a follow-up brief inherits it:
whether any TDFA construction can be made correct for PCRE preference order
(no published proof found; Laurikari's minimize/maximize tags are the
plausible mechanism); the one-pass reach; any throughput claim; whether
TRE's *parallel* matcher honours minimal repetition or routes such patterns
to its backtracker (its syntax document and its README cannot both be
unconditionally true, §2.12); and whether a size term should price a tagged
machine's register file.

## Sources and provenance

35 external sources, 27 given new `REFERENCES.md` entries. §2.12 of the
survey separates first-hand (an implementation's own code, documentation
or its authors' paper) from secondary, and flags three items as explicitly
uncertain rather than resolving them by guess. Three entries carry
`(unverified: ...)` fields per the file's own rule: `[Lau01]` (URL not
fetched), `[BT22]` (body quotations read from an HTML mirror because this
box has no PDF text extractor — `pdftotext`, `mutool`, `pypdf` and the Read
tool's PDF path are all absent), and `[re2cIssue208]` (the maintainer's
resolution was not in the rendered page; the "no lazy operator" claim rests
on the manual instead, with the issue as corroboration only).

## Validation

**COMPLETE for a docs-only lane.** `make -j4 CC=gcc-16` rc=0 (needed to read
emitted C). The census reproduces: two independent runs of
`capsurvey_census.py` against the same binary give identical stamp
distributions, and the second run — after the script was fixed to read the
`.h` as well as the `.c`, since `RX_NCAPS` lives in the header and the first
version reported every artifact's capture count as absent — is what is
committed. No suite was run and none is owed: nothing under `src/`,
`tests/`, `cli/`, `lib/` or `docs/spec/` was touched, so no gate, manifest,
count or pin moves.
