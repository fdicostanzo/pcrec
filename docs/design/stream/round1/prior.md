# One instruction stream: an end state from prior art (lane stream-prior, round 1)

Status: COMPLETE (round 1). Sources are cited by key; the
reference list is at the end (S9) with URLs. Keys already in pcrec's
REFERENCES.md are marked (R).

## S0. The answer in brief

Every production engine that mixes automata kinds splits a match on the SAME
three seams: a **finder** (literal or landmark search), a **bounder** (a
deterministic machine that finds or checks where a match can be), and a
**finisher** (an engine that is complete for the semantics: captures,
preference, the non-regular features). They differ in WHERE they draw the
split. RE2, Rust's meta engine and .NET draw it per PATTERN, as a fixed pipeline
of whole-pattern phases. Hyperscan and Spencer's Tcl/PostgreSQL engine draw it
per COMPONENT inside the pattern, and each pays for that with semantics:
Hyperscan reports match ends without leftmost-first preference or captures;
Spencer's engine adopts DFA-friendly "longest" preference rules for
alternation. Nobody in the survey splits per component AND keeps Perl/PCRE
backtracking semantics.

That gap is the end state proposed here. The artifact is ONE program of typed
instructions (the D182 record discipline, widened from the VM body to the
whole artifact). Its instruction set has five families: kit search, automaton
segments, deterministic consumers, backtracking control, and barriers with
declared effects. "DFA engine" and "VM engine" become DERIVED descriptions of a
program (it has no reachable choice point, or it has), not a choice that is
made first and then constrains everything after it.

The soundness rule that makes per-component splitting safe under backtracking
semantics is not new. It is the auto-possessification / auto-atomicity
analysis (PCRE2 [PCRE2api], .NET [Toub22], pcrec's own possessify), stated as
a general admission test: **a stretch may run as a deterministic segment iff
backtracking into it cannot change the answer**. Where that test fails, the
stretch keeps a choice point. A **gate** is a deterministic machine that only
rejects positions and never commits. It is always sound, for every feature,
backreferences and callouts included (Spencer's per-node DFA check, RE2/Rust
prefilters, pcrec's hybrid prefilter).

Top claims, argued below:
1. **Captures at seams cost nothing.** A capture boundary becomes a SAVE
   between two segments. It is no longer a reason to leave the deterministic
   world. With possessification, many capture, backreference and callout
   patterns become CHOICE-FREE programs. Such a program runs once from a
   recovered start, instead of today's forward+reverse DFA pair followed by a
   VM pass over the window (S4, S5 B1). A cheap compile-only census decides
   how many patterns this reaches (`--emit-ir` already prints `resume-points`).
2. **Captureless lookaround becomes a context condition on a deterministic
   segment.** Precedents: re2c trailing context, RE#'s edge lookarounds
   [VVE25], and Barrière & Pit-Claudel's per-position oracle [BP24]. Today any
   lookaround forces the whole pattern onto the VM.
3. **One seam contract replaces the pairwise handoffs** (prefilter→VM window,
   DFA→kit scan edge, VM→island, locate→finish, composite controller→part).
   It carries position, capture state, proof (the subject-knowledge record
   plan.md already wants) and re-entry. This is the simplicity claim. It is
   real only if the named special cases are deleted (S5 B4), and it is the
   weakest of the three to MEASURE.

## S1. What the prior art decomposes into, and what it costs

| System | Decomposes into | Decides how | Gives up | TAKE | AVOID |
|---|---|---|---|---|---|
| Hyperscan [Wan19+] | string components + small FA components (`/FAn strn ... str1 FA0/`), chosen on the Glushkov graph by dominator path, dominator region and min-cut | compile-time graph analysis. At run time the string matcher DRIVES: each FA has a "switch" that turns on only when its left neighbours have matched | captures, start-of-match by default, leftmost-first preference (reports all ends). Its decomposition-correctness proof is "left as future work" (§3.1) | **cut points from graph dominators** (a seam where every match must pass); the finder schedules the automata; small components determinize | an unproven decomposition; "every end" semantics |
| RE2 [Cox10] | whole-pattern phases: forward DFA (end), reverse DFA (start), then OnePass / BitState / NFA on the span | per call, by capability and size (BitState when the bitmap is ≤32 KB) | backrefs and lookaround, by policy ("cannot be implemented efficiently using automata") | **bound, then finish on the span**; **BitState = memoized backtracking**: a (state, position) visited bitmap keeps a backtracker linear | whole-pattern-only phases (one engine per phase per pattern) |
| Rust regex-automata meta [Gal23][RArevinner] | the same phases plus literal strategies: prefilter, reverse-anchored, reverse-suffix, reverse-inner. Capture engines preferred in the order one-pass DFA > bounded backtracker > PikeVM | by strategy table at build time. A DFA may QUIT (e.g. Unicode `\b` on non-ASCII), and the engine falls back. Run-time quadratic guards on reverse-suffix/inner | backrefs and lookaround. Reverse-inner was WRONG on leftmost semantics until 2026 (issue #1354, commit 64ad0b6) | **fallible segments with a defined give-up**; quadratic guards as part of the contract; the inner-literal split | special strategies as separate code paths, each with its own exactness bug |
| Spencer engine (Tcl, PostgreSQL) [PGregex][TclRE] | a tree of subexpressions ("subre"), each node with its own DFA. A backtracking walk over the tree tries split points, and the node DFA is checked before it recurses | structural: the parse tree | Perl preference. Alternation "prefers longest match", and a branch takes the preference of its first quantified atom. "If there are many tree levels it can get very slow" | **per-node DFA as a necessary-condition gate**; a **backreference's DFA = a copy of its referent's** (an over-approximation that cannot false-negative) | letting the DFA define the preference; a seam at every tree level (seam cost) |
| .NET backtracking compiler + source generator [Toub22] | one backtracker, emitted as code ("the structure of the backtracking gets baked into the structure of the code") | auto-atomicity over the whole expression; a `switch` on the first char for disjoint alternations; find optimizations (fixed-distance sets, a literal after a set loop, searched and then matched backwards) | nothing (full semantics) | **auto-atomicity as the soundness rule**; deterministic alternation by first-byte switch; the landmark-then-walk-back find | — (this is pcrec's VM's closest relative) |
| .NET NonBacktracking [Mos23+][DotNetPR65129] | derivative DFA (built lazily, falling back to an NFA when large), three passes: end, start, captures | the engine is chosen by an option; within it, DFA→NFA by size | backrefs, lookaround, atomic groups, conditionals, `\G`; keeps only the last capture of a group | backtracking (leftmost-first) semantics CAN live in a deterministic machine. [Mos23+] proves it for its fragment | an engine chosen by the user per pattern |
| V8 Irregexp + linear engine [V8lin] | a backtracker, plus a linear engine for a subset | at run time: after 50,000 backtracks (default), the call falls back to the linear engine, if the pattern is in its subset | the linear subset excludes backrefs and lookaround | **a budget-triggered change of method** | switching engines whose semantics differ |
| Selective memoization [DSL21][FH24] | a backtracker plus a (node, position) memo of failures | memo only at selected nodes (loop and alternation entries), run-length encoded | [DSL21]'s lookaround extension was later shown flawed [FH24]; backrefs break the memo's premise | **memo as a property of a VM segment**, giving linear time for its regular part, lookaround and atomic included [FH24] | memoizing where the continuation reads capture state |
| Tagged DFA [Lau00][Tro19][BT22] / one-pass DFA [RAonepass][RE2onepass] | captures inside a DFA (tag registers on transitions) / a DFA where each state is one NFA state | construction-time | TDFA: POSIX or leftmost-greedy, never PCRE's lazy preference. One-pass: only unambiguous (anchored) fragments | **one-pass is the only DFA that gives PCRE captures**; tag operations on transitions are the model for a SAVE at a seam | TDFA as a general PCRE capture engine |
| Lookaround without backtracking: RE# [VVE25], [BP24] | RE#: derivatives with intersection and complement, lookarounds only at the regex's EDGES. BP24: one oracle pass per lookaround, a per-position boolean table read by a `CheckOracle` instruction; captureless lookbehinds run in lockstep | construction-time | RE# is POSIX leftmost-longest. BP24's capture reconstruction relies on JavaScript's "capture reset", which PCRE does not have. Both exclude backrefs ("uniform futures" fails) | **a lookaround with a regular body and no captures is a per-position predicate**: fold it into the segment at its edge, or read it as an oracle | JS capture-reset reasoning; POSIX end selection |
| PCRE2 itself [PCRE2api][PCRE2jit][PCRE2matching] | one backtracker (interpreted or JIT, same semantics), start-of-match optimizations, auto-possessification. A separate `pcre2_dfa_match` with DIFFERENT semantics (all matches at a start, longest first, no captures) | compile-time flags | — | **optimizations may skip callouts** ("these 'start-up' optimizations can cause them to be skipped"), which pcrec's fire contract (match_api §11.6) already mirrors | a DFA path that changes the answer (`pcre2_dfa_match`) |

### What the table says, in four lessons

**L1. The seams are universal; only their granularity varies.** Finder →
bounder → finisher appears in every row. Per-pattern pipelines are simple, and
they waste work: RE2 and pcrec's hybrid scan a matched span two or three times.
Per-component splitting saves that work, and both systems that do it lost
semantics, because they let the automaton DEFINE the answer. The way out is to
make automata only ever ACCEPT or REJECT what the backtracking semantics would
pick, never choose between answers. That is the soundness rule in S3.

**L2. Gates are free and universal.** A machine for a necessary condition can
only remove positions that cannot match. Spencer's per-node checks, RE2's and
Rust's prefilters, Hyperscan's switches and pcrec's hybrid prefilter are all
gates. Gates never need a semantics argument beyond "over-approximates". That
is why they reach backrefs (via the referent copy) and callouts (as epsilon).

**L3. Every split inside the pattern needs an exactness condition and a
run-time guard.** Rust's reverse-inner had a leftmost bug for years, and
"syntactic analysis doesn't predict it perfectly" [Gal23], so it carries
quadratic guards. pcrec's D161 add. 17 reached the same place: an admission
table for the landmark walk. The end state must make the exactness condition
a DECLARED part of every seam, not a property argued per strategy.

**L4. Seams cost something.** Spencer's engine slows with tree depth.
Hyperscan keeps components few and large ("Avoid having too many strings").
.NET's NonBacktracking falls back to an NFA when the DFA grows. Splitting must
therefore be priced. A planner that cuts at every possible seam is Spencer's
engine again.

## S2. The end state

### S2.1 The artifact is one program

The artifact is one program: a sequence of typed instruction records
(D182's "the record is the source", widened from the VM body to the whole
matcher, search loop included). Each record renders its own C. No section is
"the DFA" or "the VM". Each instruction is simply what the planner produced at
that point of the pattern. The search loop is part of the program too: the
implicit unanchored prefix `.*?` is a CHOICE over start positions, and finders
and gates implement it.

### S2.2 The instruction families

| Family | Instructions | Moves the cursor | Leaves a resume point | Writes captures | Code owner |
|---|---|---|---|---|---|
| **K: kit search** | `FIND(site)` forward to the next candidate; `WALK(site, dir)` back or forward over a class run (bounded or not, D161 add. 17) | yes | `FIND` is resumable (the next candidate); `WALK` is not | no | the kit (D146; pcrec hands FACTS, D157) |
| **A: automaton segments** | `DFA(M, mode)` with mode ∈ {`exact`, `ends`, `gate`, `locate`}; `RDFA(M)` reverse (start recovery, the D161 scaffolding); `ONEPASS(M)` (captures on transitions) | `exact`, `locate` and `RDFA` do; `gate` does not | `ends` only (an end-position iterator in preference order) | `ONEPASS` only | pcrec; a scan edge inside M is a kit site |
| **D: deterministic consumers** | `LIT(s)`, `CLASS(c)`, `SPAN(c, min, max, possessive)`, `SWITCH(first-byte → arm)` | yes | no | no | pcrec (SPAN may delegate to the kit, as today's VMSPAN) |
| **V: backtracking control** | `CHOICE(arms, order)`, `JUMP`, `FAIL`, `COMMIT`/atomic, `SAVE(slot)`, the trail, `REPORT` | — | `CHOICE` | `SAVE` | pcrec (today's 29 VM record kinds) |
| **B: barriers with declared effects** | `BACKREF(g)`, `ORACLE(look-id)`, `LOOK(sub-program)` (a lookaround with captures or backrefs inside), `CALLOUT(n, attrs)`, `MEMO(point)` | `BACKREF` and consume callouts do | callouts can fail (backtrack); `LOOK` is atomic | `LOOK` may | pcrec; the callee is the user's |

Two notes on the table. First, the kinds are not new. Families V and D are
today's VM records; family A is today's DFA engine, prefilter pair and
islands; family K is today's kit sites; family B is today's VM modules. What
is new is that they share ONE record type and ONE seam contract, and that a
family may appear anywhere in a program, not only inside the "host" engine
that was picked for the pattern. Second, `MEMO` is the one kind with no
counterpart in pcrec today. It is the RE2 BitState / [DSL21] / [FH24]
mechanism, and the source of benefit B3.

### S2.3 Segments

A **segment** is a maximal run of instructions that share one control
discipline: deterministic (families A, D and K: one answer, no resume),
backtracking (V, with resume points), or barrier (B). Segments are a VIEW of
the program, computed from the kinds, and are never stored as a separate
structure. Today's `RX_ENGINE` survives as a derived stamp: `dfa` means "no
CHOICE is reachable except the start loop's", and `vm` means otherwise.

### S2.4 Who decides segmentation, and how

The **planner** walks the IR (pcrec's single NFA-with-instructions graph,
APPROACH §2) in program order. For each node it reads a DECLARED first-match
table (memory `pcrec-decisions-as-first-match-tables`). This is the S3
soundness rule as rows:

| # | the stretch is... | it becomes |
|---|---|---|
| 1 | a necessary condition of the rest of the match (over-approximated: backrefs → their referent, lookarounds and non-consuming callouts → ε) | a `DFA(gate)` or `FIND` in FRONT of the stretch it protects (always sound, L2). Whether to emit it is a PRICE question, not a soundness question |
| 2 | a capture boundary | `SAVE` at a seam. Never by itself a reason to change family |
| 3 | exact in context (S3, E1-E4) | family D if it is one class or literal, else `DFA(exact)`; `ONEPASS` if it contains SAVEs and is one-pass |
| 4 | a monotone end set (APPROACH §2 A-1) | `DFA(ends)`, with its iterator as the resume point |
| 5 | a captureless lookaround with a regular body at a segment edge | absorbed into the adjacent `DFA` as left or right context (S3 E5), else `ORACLE` |
| 6 | a backref, a lookaround with captures, or a callout | a family B barrier |
| 7 | anything else | family V (`CHOICE`), with `MEMO` at the loop/alternation entries when S3 E6 holds |

A second pass **fuses** adjacent deterministic instructions into one `DFA`
when the price says one machine beats N small ones. This is L4, and it is how
a capture-free pattern still compiles to today's single whole-pattern DFA.
Placing the FINDER uses Hyperscan's idea: the cut is a dominator of every
accept path. pcrec's facts already compute it (`req_*`, `kset_walk`,
landmark), and the kit receives it as a site (D161). The PRICE half of the
planner is the pricing work under study (pricing_rulepilot); this design
needs only that pricing chooses among SOUND options, never decides soundness.

### S2.5 The seam contract

Every boundary between two instructions of different families carries one
record:

| Field | Content | Today's scattered equivalents |
|---|---|---|
| `pos` | the cursor, and the direction of travel | the hybrid window start, the landmark position, the scan-edge exit |
| `caps` | which capture slots are written, and the trail mark since the last resume point | the VM trail; the hybrid's "VM assigns captures on the window" |
| `proof` | what is KNOWN about the subject here: bytes proven at offsets, length bounds, window end, context bytes | PF-KNOW (D142), kit proven sets (D161 add. 16), K23 MRL, the match-end mark (D164); the plan.md row "ONE general record of what is ALREADY KNOWN about the subject" |
| `reentry` | NONE / `FIND-next` / `ENDS-next` / a `CHOICE` resume frame / `START-next` | the hybrid's retry after a failed window; `RX_ITER_RETRY`; the VM's resume frames |
| `effects` | for kit and callout instructions: what they read and write (slots, cursor, groups), and whether they can transfer control | D182's ruling (c)(1), "kit windows are OPAQUE WITH DECLARED EFFECTS" |
| `exact` | which admission row made this seam sound (S3), so a check can verify it | D161 add. 17's admission table, possessify's verdict |

The `exact` field is lesson L3 made structural. A reverse walk, an inner cut,
or a deterministic stretch inside a VM program names the row that admits it,
and a test sweep can deny each row independently (the existing
`make test-axes` deny/force discipline).

## S3. The soundness rule

**Setting.** Write the pattern at some point as P · S · K: what came before,
the stretch to be placed, and its continuation. Under backtracking semantics,
the paths through S from position i yield a sequence of outcomes (e₁, c₁),
(e₂, c₂), … in PREFERENCE order (end position, capture state). The answer
from that point is the first outcome from which K succeeds. A deterministic
segment returns one outcome and keeps no resume point. Committing S to such a
segment is sound exactly when the outcome it returns is the one backtracking
would settle on, for every subject. The admission rows below are sufficient
conditions for that, each with a precedent.

| Row | Admission condition (sufficient) | Segment | Precedent |
|---|---|---|---|
| **E1a atomic-by-disjointness** | S = a greedy or lazy repeat of a class C, and no continuation of K can begin with a byte of C (a giveback can never help) | `SPAN` possessive, or `DFA(exact)` | PCRE2 auto-possess, .NET auto-atomicity, pcrec possessify |
| **E1b unique end** | for every subject, S has at most one end from i: fixed width, or a prefix-free literal set (a first-byte-disjoint alternation) | `LIT`, `SWITCH`, `DFA(exact)` | .NET's first-char `switch`; one-pass [RAonepass] |
| **E1c infallible continuation** | K succeeds from every end S can reach (e.g. K is nullable and assertion-free at an unanchored pattern end) | `DFA(exact)` computing e₁, the D3 leftmost-first answer of S alone | pcrec's D3 machine computes exactly e₁ for K = ε |
| **E2 captures** | S contains SAVEs. Sound in a deterministic segment only if S is one-pass, or if the SAVEs sit at S's edges (then they are seam SAVEs, not inside) | `ONEPASS(M)`, or a `DFA` bracketed by `SAVE`s | one-pass DFA [RE2onepass][RAonepass][GoOnepass] |
| **E3 locate** | the capture-erased stretch (here the whole pattern, or a suffix of it) has the same leftmost-first [start, end] as the full pattern: no backref, captured lookaround or callout inside, or one with a proven-exact over-approximation | `DFA(locate)` + `RDFA`, then a finisher with the end PINNED (paths that cannot reach e are pruned) | RE2, Rust, .NET 3-phase; pcrec's hybrid "exact" |
| **E4 monotone ends** | S's preference enumerates ends in position order (a single quantified class) | `DFA(ends)`, with the iterator as the resume point | APPROACH §2 A-1 accept-list islands |
| **E5 captureless lookaround** | `(?=X)`/`(?!X)`/`(?<=X)`/`(?<!X)` with X regular and free of captures, backrefs and callouts: a pure function of (subject, pos) | `DFA(gate)` anchored at pos without moving it (lookahead); a bounded `RDFA(gate)` or a lockstep context bit in the enclosing forward DFA (lookbehind); fused into the adjacent `DFA` at a segment EDGE | re2c trailing context; RE# edge lookarounds [VVE25]; [BP24] `CheckOracle` and lockstep lookbehind |
| **E6 memo** | from point p, K's success depends only on pos: no reachable `BACKREF` to a group that can differ between two arrivals at (p, pos), and no reachable callout whose return reads capture state | `MEMO(p)` on a V segment: a failure memo with (p, pos) bits | RE2 BitState; [DSL21]; [FH24] (lookaround and atomic included) |
| **G gate** | always: any machine for a NECESSARY condition | `DFA(gate)`, `FIND` | L2 |

**Where no row applies.** The stretch stays family V. It is a `CHOICE` with
a resume frame, the trail restores captures, and the re-entry is the frame.
This is today's VM, unchanged. Three things do NOT happen in this design,
deliberately:
- **No state sets or Pike simulation.** [Mos23+] and [DotNetPR65129] show
  that a priority-ordered thread set can reproduce leftmost-first captures
  linearly for regular fragments. A `PIKE(M)` kind is a legitimate future row
  between E2 and V, and is held under D77 until a measurement names a
  population that MEMO does not already serve.
- **No automaton ever CHOOSES between two backtracking outcomes** unless E1
  or E4 has proved that the choice coincides with preference. This is the
  line Hyperscan and Spencer crossed (L1).
- **No TDFA.** It is POSIX or leftmost-greedy, not PCRE.

**The start loop is not special.** The unanchored search is `CHOICE` over
start positions, earliest first. A `FIND` prunes it (rule G). An `RDFA`
start recovery replaces it by ONE start only under D161 add. 17's admission
(the class excludes every landmark byte, so no earlier start pairs with a
later landmark). Otherwise the program iterates `START-next` from the
recovered earliest candidate. Rust's quadratic guards (`min_match_start`)
become a field of that seam's re-entry: never walk back past the previous
attempt's floor.

**Exactness is per seam, so it is checkable per seam.** The seam record's
`exact` field names the row that admitted it. A deny-flag per row, applied to
the whole corpus, must leave every answer identical: the existing
`make test-axes` discipline, with one axis per admission row instead of one
per optimization.

## S4. The worked patterns

Notation: one instruction per line; `‖` marks a seam, with what crosses it.
"Today" is read off the shipped `build/pcrec` (`--features all`, the
`RX_*` stamps and `--emit-ir` summary rows), run 2026-11-01 on single
patterns.

### 1. `abc`
```
L:  FIND(lit "abc")                 ‖ pos=i, proof={bytes[i..i+3]="abc"}, reentry=FIND-next
    REPORT [i, i+3)
```
One kit instruction. The proof field makes any verify redundant, so nothing
re-reads the bytes. Today: DFA engine with the same kit find. **No
difference, and none should exist.** The test of this case is that the stream
DEGENERATES: no seam overhead and no record that renders as dead C.

### 2. `[a-z]+@x`
```
L:  FIND(site: landmark "@x", class-before [a-z])  ‖ pos=@, proof={"@x" at pos}, reentry=FIND-next
    RDFA([a-z]+)  -- scaffolding; its looping state is a kit WALK scan edge
                    ‖ start s, exact=D161a17-T(exclusion: '@' ∉ [a-z])
    SPAN?/verify: nothing left to verify (proof covers "@x")
    REPORT [s, pos+2)
```
Three families in one program: K (find), A (reverse machine) with K inside
it (scan edge), and REPORT. This is exactly today's landmark walk
(`RX_DFA_START "reverse-pass"`, `RX_DFA_SCAN_EDGE "range"`). The stream adds
nothing here beyond NAMING the seams, which is what a byte-identical first
proof should show (S8 P1).

### 3. `(\w+)@(\w+)\.com`
```
L:  FIND(site: landmark "@", class-before \w)        ‖ pos=@, reentry=FIND-next
    WALK(\w, back, unbounded) -> s                   ‖ exact=D161a17 (exclusion: '@' ∉ \w)
    SAVE 2 ← s
    -- the run [s, @) is already proven \w+ by the walk: proof covers it
    SAVE 3 ← pos;  LIT "@"
    SAVE 4
    SPAN(\w, 1, ∞, possessive)                       ‖ exact=E1a ('.' ∉ \w)
    SAVE 5
    LIT ".com"   -- fail → reentry FIND-next (no CHOICE anywhere)
    REPORT [s, end)
```
**Today:** VM engine "forced by capture group". A capture-erased forward DFA
finds the end, a reverse DFA finds the start, and the VM then runs over the
window (`RX_VM_PREFILTER "hybrid"`) with `resume-points 0`. So the matched
bytes are traversed three times, and the VM program it finally runs has no
choice point at all. **Stream:** one find, one walk back, one forward
deterministic run that is the verify and the capture assignment at once.
Every capture is a seam SAVE (E2). This is benefit B1's archetype.

### 4. `(a|ab)(c|bcd)(d*)` (preference that longest-match gets wrong)
On `abcd`, PCRE gives $1=`a`, $2=`bcd`, $3=``. POSIX/longest gives `ab`,`c`,`d`.
```
L:  FIND(gate: first byte 'a')  ‖ reentry=START-next
    SAVE 2
    CHOICE [ LIT "a" | LIT "ab" ]       -- E1 fails: "a" is a prefix of "ab", and K can fail after either
    SAVE 3; SAVE 4
    SWITCH(first byte){ 'c' → LIT "c" ; 'b' → LIT "bcd" }   ‖ exact=E1b (disjoint first bytes)
    SAVE 5; SAVE 6
    SPAN(d, 0, ∞, possessive)            ‖ exact=E1c (end of pattern, unanchored)
    SAVE 7;  REPORT
```
One V segment, around `a|ab` only. Everything after it is deterministic, and
a failure there resumes the one CHOICE. **Today:** VM behind the exact DFA
pair, `resume-points 1`. That count is already the stream's minimum, so
today's VM has found the same structure. The stream's gain is the first two
passes, not the VM. A `locate` DFA here is sound (E3, no non-regular
feature), and it is worth keeping when matches are rare. The planner keeps it
in FRONT as a gate rather than as a locate: the finisher's own run is cheap,
and the gate's job is only to skip non-matching text. **The preference trap
is closed by construction:** no automaton chooses between `a` and `ab`.

### 5. `(\w+)\s+\1` (backreference)
```
L:  FIND(gate: \w\s+\w — referent-copy over-approximation of \w+\s+\1, Spencer's rule)
                                    ‖ pos=landmark run of \s, reentry=FIND-next
    WALK(\w, back) -> s0            ‖ exact=NONE: the walk gives the EARLIEST candidate, not THE start
S:  SAVE 2
    SPAN(\w, 1, ∞, possessive)      ‖ E1a (\s ∩ \w = ∅)
    SAVE 3
    SPAN(\s, 1, ∞, possessive)      ‖ E1a (\1 starts with \w)
    BACKREF 1                       -- barrier; fail → reentry START-next (s0+1 ... up to the \s run)
    REPORT
```
`xthe the` shows why the walk is not exact here: the start is 1, not 0. The
start loop is a `CHOICE` over starts in [s0, landmark), bounded by Rust's
guard (never re-walk below the previous floor). **Today:** VM,
`RX_VM_PREFILTER "none"`, because the listing reads "the erased approximation
is neither a sound superset nor the true span". The VM scans by its first
class (`RX_VM_START_SCAN "first-class"`), with `resume-points 0`. **Stream:**
a gate exists (Spencer's referent copy makes the backref's DFA a sound
superset when the group is set before the backref and holds no
backref/recursion), and so does a landmark find. **Caveat:** whether today's
"not a sound superset" verdict reflects a case the referent copy misses
(caseless backrefs? an unset group?) needs checking before this is claimed.
It is an S7 hole (H5).

### 6. `foo(?=bar)|(?<!x)baz` (lookaround)
```
L:  DFA(locate, M) where M = foo·[right-context bar] | [left-context ¬x]·baz
      -- E5: both lookarounds are captureless with literal bodies at the EDGE of their arm
      -- the lookbehind is a context bit in M's state (the previous byte was 'x'), lockstep [BP24]
      -- the lookahead is trailing context: M reports end = (end of "foobar") − 3
                                    ‖ [s, e), exact=E5+E3
    REPORT [s, e)
```
No V segment at all: no captures and no ambiguity (`f` and `b` are disjoint).
**Today:** VM ("forced by `(?=...)`"), behind an exact forward+reverse DFA
pair, with `resume-points 1`. **Stream:** a pure DFA. Benefit B2 (reach).
Lookarounds in the MIDDLE of a segment (`a(?=b)\w`) are not folded in this
end state. They are an `ORACLE`/`DFA(gate)` at a seam: sound, but a seam
(S7 hole H4).

### 7. `(?:cat|dog|bird|fish|...30 words...)s?` (heavy alternation)
```
L:  FIND(site: multi-literal set of the 30 words)   ‖ pos=i, proof={word w at i}, reentry=FIND-next
    -- leftmost-first among the words that matched at i: D3 machine of the alternation (E1c: K=s? is infallible)
    DFA(exact, trie of 30 words) -> j                ‖ the kit may hand over w and make this a no-op
    SPAN(s, 0, 1)
    REPORT [i, j(+1))
```
**Today:** DFA engine (no captures). Same shape. **With a capture**
`(cat|dog|...)s?`, today goes to VM-hybrid (checked on a 6-word form: an
exact DFA pair, then a VM with an alternation trie ISLAND and
`resume-points 0`). The VM has already rebuilt the DFA's trie as an island,
which is a second host for the same kind. The stream keeps ONE trie DFA and
brackets it with `SAVE 2`/`SAVE 3` at its seams (E2). The capturing form
then costs the same as the capture-free form. B1 again.

### 8. `(a+)+b` (nested quantifier)
```
L:  FIND(lit 'b') / DFA(gate) ; RDFA(a+ back from b)   ‖ [s, e) exact=E3 (capture-erased a+b)
F:  -- finisher, end PINNED at e:
    SAVE 2
    MEMO(p1); CHOICE-loop [ SPAN(a,1,∞) greedy, with giveback ... ]   ‖ E6 holds (no backref, no callout)
    SAVE 3
    LIT 'b'
    REPORT
```
On a matching window, the first greedy path succeeds, so neither the memo nor
backtracking ever runs. On a window that cannot match, E3 has already
excluded it. **Today:** the same (`prefilter-window` prune ceiling,
`resume-points 3`). The catastrophe is already defused by the exact locate.
**Where the stream adds something** is the case today's design cannot gate:
the same nested quantifier next to a backref or a callout (no exact locate),
for example `(a+)+b\1`. `MEMO` gives the V segment linear worst case under
E6 if the backref reads a group that is not rewritten between arrivals.
Here it reads group 1, which IS rewritten, so E6 fails, and that pattern
stays exponential-with-budget as in PCRE2. B3 is narrower than it first
looks; S5 says so.

### 9. `x(?C1)y\d+` (callout mid-pattern)
```
L:  FIND(lit "xy")  -- a non-consuming callout is ε for a gate (rule G); its "effects" record says zero-width
                                    ‖ pos=i, reentry=FIND-next
    LIT x
    CALLOUT 1 (ctx: pos=i+1, caps)  ‖ barrier: may fail → reentry FIND-next; fires only at gated positions
    LIT y
    SPAN(\d, 1, ∞, possessive)      ‖ E1c (end of pattern)
    REPORT
```
Firing only at positions the gate admits is allowed by the fire contract
(match_api §11.6: count and order unspecified, the pure callee's answer is
the backtracking-order answer). PCRE2 does the same with its start
optimizations ("can cause them to be skipped" [PCRE2api]). A `consume`
callout breaks the ε over-approximation: its effects record says "moves the
cursor by an unknown amount", so the gate either stops at the callout (`FIND x`
only) or is not emitted. **Today:** VM, `prefilter "no-callout"` ("a callout
pattern has no prefilter yet"), `RX_VM_START_SCAN "first-class"`,
`resume-points 0`. **Stream:** a literal find across the callout. B2 (reach),
via the `effects` field rather than via a callout special case.

### 10. `\p{Greek}+\s\d{3}` under UTF-8
```
L:  FIND(site: \s\d landmark, or Greek's lead-byte set {CE, CF, E1(+next)}; the kit chooses)
    RDFA(\p{Greek}+ as UTF-8)   -- scaffolding; scan edge over the Greek byte classes
                                ‖ exact=D161a17 (Greek ∩ \s = ∅ as code points AND as encodings)
    DFA(exact, \s\d{3} as UTF-8)  ‖ E1b (fixed width in characters; the encodings are prefix-free)
    REPORT
```
**Today:** the DFA engine, with the same shape available. **No difference.**
This case exists to check that UTF-8 does not break the rows: E1a's
disjointness must hold on CODE POINTS (the classes) and is then automatic on
encodings, because UTF-8 is prefix-free. The one-pass narrowing [RAonepass]
reports (`\w*\s` under Unicode) bites only ONEPASS, which this pattern does
not need.

### Summary of the ten

| # | today | stream | difference |
|---|---|---|---|
| 1 `abc` | DFA + kit find | FIND, REPORT | none (degeneracy test) |
| 2 `[a-z]+@x` | DFA landmark walk | FIND, RDFA⊃WALK | none: it names today's seams |
| 3 captures | VM-hybrid: 2 DFA passes + VM, 0 resume points | FIND, WALK, SAVEs + deterministic run | 3 traversals → 1 (B1) |
| 4 preference | VM-hybrid, 1 resume point | gate + 1 CHOICE + deterministic tail | the pass count; same VM |
| 5 backref | VM, no prefilter, first-class scan | gate (referent copy) + landmark + start loop | a gate (B2), if the superset holds |
| 6 lookaround | VM-hybrid, 1 resume point | a pure DFA | no VM (B2) |
| 7 alternation | DFA | same; with a capture: same + 2 SAVEs | the capturing form at DFA cost (B1) |
| 8 nested | VM-hybrid, safe via exact window | same; MEMO for un-gateable relatives | narrow (B3) |
| 9 callout | VM, no prefilter | FIND across the callout | a finder (B2) |
| 10 UTF-8 | DFA | same | none (row check) |

## S5. Benefit case

Each claim below gives what it is, how to measure it, the patterns it
reaches, and an honest strength rating.

### B1 (speed): one traversal instead of three for choice-free capture programs. STRONG where it applies; the population size is unknown

- **What.** A capture pattern that possessification leaves with no choice
  point (`resume-points 0` in today's listing) is a deterministic program
  with SAVEs. Today it costs a forward DFA pass (end), a reverse pass
  (start), and a VM pass over the window. Under locate×finish
  (locate_finish.md) that becomes a landmark walk, a forward verify and a VM
  pass. In the stream, the forward deterministic run IS the verify and the
  capture assignment, so it costs FIND, WALK back, and one forward run.
- **Why it is not already planned.** Locate×finish keeps FINISH as a
  separate engine run over a located window, because the VM is the finisher
  of record whenever a capture exists. The stream drops that premise: a
  capture is a seam SAVE (E2).
- **Measure.** (1) Compile-only census over pcrec-bench's capability set and
  the .rxt corpus: how many VM artifacts have `resume-points 0`, and how many
  have ≤1. The listing already prints the field. Queue it as a >50-compile
  sweep. The survey's own count is a lead: 17 of 26 capture-forced
  capability patterns are on the exact hybrid
  (captures_via_dfa_survey.md §0). (2) Timing in the match regime and
  find-all over match-dense subjects, both layers (D147). On long subjects
  with rare matches, the finder dominates and B1 is near zero. The survey
  reached the same conclusion for the one-pass DFA (§3.3).
- **Reaches:** #3, #7 with a capture, #5 (the per-start run), #4 partly
  (its tail).

### B2 (reach): non-regular or opaque features stop poisoning the rest of the pattern. MEDIUM

- **What.** Today one lookaround, callout or backref sends the whole pattern
  to the VM host, sometimes with no prefilter at all (`no-callout`,
  `no-backreference`). In the stream, the feature is one barrier
  instruction. Everything around it keeps the deterministic and kit kinds:
  captureless lookaround folds into a DFA (E5); a non-consuming callout is ε
  to a finder through its declared effects; a backref is gated by a
  referent-copy superset (Spencer's rule).
- **Measure.** The same census restricted to patterns with these features,
  route by route (today against the stream's planned route). Then bench
  rows for the populations the census finds.
- **Reaches:** #5, #6, #9.
- **Weakness.** The callout and backref finders are things today's design
  could add as one-off prefilter rows. The stream's advantage there is that
  they come from ONE rule (G + effects) and are not built per feature (B4).

### B3 (worst case): MEMO bounds backtracking where no exact locate exists. WEAK

- **What.** A failure memo at loop and alternation entries (RE2 BitState,
  [DSL21], [FH24]) gives the V segment linear time where E6 holds.
- **Honest reach.** Where an exact locate exists, today's hybrid already
  defuses the catastrophe (#8). Where it does not, the reason is usually a
  backref or a callout, and those are the very things E6 excludes when they
  read groups the loop rewrites (`(a+)+b\1`). The reachable population is
  nested quantifiers with no exact locate and only harmless barriers: real,
  but small.
- **Compatibility question.** PCRE2 hits its match limit on these subjects.
  pcrec with MEMO returns an answer. That is a limit difference, not a match
  difference (D26 tier), but it needs a ruling.
- **Measure.** Adversarial subjects on the census population: step counts
  with and without MEMO.

### B4 (simplicity): special cases that are DELETED, not tidied. MEDIUM, conditional on actually deleting them

Each of these becomes a row or a field of the one model. Every item needs
verification against the code before it is claimed; this lane read the
documents, not `src/`.

| Today's special case | Becomes |
|---|---|
| engine selection as a first, global decision (the `ESEL_*` ladder, the K53 drop ladder, `RX_ENGINE_WHY "forced by capture group"`) | a DERIVED stamp (S2.3) |
| the VM's alternation trie ISLAND, a second implementation of the DFA's trie | the one `DFA(exact)` kind with seam SAVEs |
| APPROACH §2's three island strengths (exact / accept-list / fallback) | rows E1, E4 and V of the admission table |
| `RX_VM_START_SCAN` (the VM's own first-class scan) beside the DFA's finder | one `FIND` |
| prefilter declines by feature (`no-callout`, `no-backreference`) | rule G plus `effects` |
| pairwise proof handoffs: PF-KNOW (D142), `RX_REQ_HANDOFF`, the D164 end mark, kit proven sets | the seam's `proof` field (the plan.md subject-knowledge row's natural home) |
| per-strategy exactness arguments (the walk admission table, possessify's verdict, the hybrid's `LANG exact` reason) | the seam's `exact` field, one deny axis per row |

The measurable form is the count of (kind × host) cells. Today a new kind
(one-pass, PIKE, a new kit site) is built once per host that needs it. In
the stream it is built once. "Tidier" by itself is not claimed.

### B5 (capability): ONEPASS segments and E5 lookaround folding. WEAK as a stream benefit

Both could be added to today's design as an island kind or a DFA feature.
The stream makes them ordinary rows. They are listed for completeness and
not counted toward the case.

### Where the case is weak, plainly

On capture-free regular patterns (#1, #2, #7, #10) the stream equals today,
by construction. The planner's default must REPRODUCE today's whole-pattern
DFA, or it is a regression (L4). The case therefore rests on B1's population
and B2's reach. Both are measurable with a compile-only census before any
build.

## S6. Bird-in-the-hand discipline: the two FULLY BUILT end states

**Today's design, grown as far as it goes:** a DFA host (D3 leftmost-first
machine, kit scan edges, the landmark-seeded reverse DFA as scaffolding,
table/goto forms) and a VM host (D182 records, possessify, exact /
accept-list / trie islands, prune and MRL, the VM's own start scan). The
hybrid joins them, locate×finish chooses any locate with any finish, D163
composites coordinate sub-artifacts, and the subject-knowledge record is
built. **The stream, fully built:** S2-S3.

The striking prior-art observation is that today's design, grown fully,
CONVERGES on the stream: a VM host that contains DFA islands and kit sites,
and a DFA host that contains kit sites. Spencer's engine and .NET's
generator each grew the same way. What separates the two end states is not
reach but HOSTS: in today's design every kind is built per host, and the
host is chosen first.

| Question | Today, fully grown | Stream, fully built |
|---|---|---|
| A capture-free regular pattern | one whole-pattern DFA (default) | the same, but only if the planner fuses. Fusion is a priced decision (risk: L4) |
| A capture pattern with no choice point | locate passes, then a VM pass over the window | a find and a walk, then one deterministic pass (B1) |
| One lookaround or callout in a long regular pattern | the whole finish goes to the VM; the prefilter is per-feature (absent today for callouts and backrefs) | one barrier; the rest stays deterministic (B2) |
| A new kind (one-pass, PIKE, a kit form) | built once per host that needs it | built once |
| Where exactness lives | per strategy: the walk table, possessify, the hybrid's LANG reason, island strengths | per seam, one `exact` field, one deny axis per row |
| Catastrophic backtracking with no exact locate | step budget (as PCRE2's match limit) | MEMO where E6 holds, else the step budget |
| Global whole-pattern optimization (Hopcroft over the whole language, one tight loop) | native | needs fusion. Never worse than today ONLY if fusion is correct |
| Analysis of the VM program (possessify, prune, MRL) | sees the whole VM program | sees the whole stream, since it is the same records |

**What today's design can NEVER do without becoming the stream:** let the
finish of a capture pattern be anything other than a separate engine run
over a located window. The finisher is chosen per pattern, and a capture
anywhere makes it the VM. Any fix (a "deterministic VM finish fused with the
walk" locate×finish row) is the stream's B1 rebuilt as one special row.
Likewise, it cannot keep a DFA's finder and scan kinds for the part of a
pattern after a barrier, except by building those kinds a second time inside
the VM host.

**What the stream can NEVER do that today's design can:** get the
whole-pattern DFA for free. Today the engine choice yields that DFA by
default. The stream gets it only through a fusion decision that can be WRONG,
and a wrong decision is a slowdown, never a wrong answer. This is a real
asymmetry, not a migration cost. The stream answers it with a planner default
of "no V instruction reachable → fuse everything" (today's DFA route,
exactly), and by pricing every departure from that default.

"Today's code works" plays no part above. Neither does the proof burden of
the stream's admission rows, which is real but is an end-state property: S7
H2.

### S6.1 Migration cost (separate; never subtracted from the above)

- **The VM body is already records (D182 step (a), landed).** That is the
  hardest piece of the widening, and it is done. Steps (b)/(c), analysis on
  the records, are the planner's natural substrate.
- **The DFA emitter's top level** (`emit_dfa.c`: the candidate rows,
  `cand_select`, `dfa_matches`, the scan-edge and reverse-pass routes) must
  render from records. The locate×finish L0 closure (`cand_path_of`) already
  derives "which machines and slots this artifact uses" as one function,
  which is the planner's half.
- **The hybrid entry and composites** become stream prologues.
- **Every scaffolding change is an abi event** (D76/D94). The byte-identical
  steps (S8 P1, P2) avoid it, and B1 is the first abi event.
- **Listing:** `--emit-ir` is VM-only today and must list the stream for
  every artifact.
- **Tests:** one answer-identity deny axis per admission row, a D27
  spec-first author per new row (E5, E6), and the S8 censuses.
- **Rough order:** P1, P2 (weeks, byte-identical), then B1 (one abi event),
  then B2's rows one at a time, each with a measured trigger (D77).

## S7. Holes I already see, ranked

1. **H1 Fusion pricing (L4).** The stream is only as fast as its cut/fuse
   decisions. Spencer's engine shows what cutting at every seam costs (seam
   entry and exit inside a hot loop: `(?:\w+\s)*` with a capture on the inner
   word pays two SAVEs and a segment change per iteration, where a DFA pays
   nothing). The default must reproduce today's route wherever today's
   route exists, and every departure needs a measured price. Pricing is
   still under study (rulepilot), so the stream's speed claims inherit that
   open question.
2. **H2 Proof burden of the in-context rows.** E1c (infallible continuation),
   E3 (locate exactness under captures) and E5 (lookaround folding) are
   "obviously sound" in exactly the way Rust's reverse-inner was before
   #1354. Each row needs a written argument, a D27 spec-first test author,
   and a deny axis. E1a is today's possessify and inherits its maturity.
   The others do not.
3. **H3 The start loop under non-exact walks** (#5). When the walk gives
   only the earliest candidate, the per-start runs can go quadratic on runs
   of the walk class. Rust needed run-time guards for the same shape. The
   `reentry` floor field is the mechanism, and its bound needs a proof.
4. **H4 Lookaround folding is only easy at segment edges with fixed-width
   bodies.** `a*(?=a)` puts the lookahead's body inside S's own follow set.
   The DFA must then report the PREFERRED S-end at which the context holds,
   which is tag-like end adjustment. That is the TDFA territory this design
   otherwise avoids. Mid-segment lookarounds stay seams (`ORACLE`/gate),
   which is sound but costs a seam.
5. **H5 The backref gate.** Today's listing says the erased approximation of
   `(\w+)\s+\1` is "neither a sound superset nor the true span". Spencer's
   referent copy is a superset in the simple case. Which PCRE2 cases break it
   (caseless backrefs, an unset group under PCRE2_MATCH_UNSET_BACKREF,
   duplicate group names, `(?|`), and whether the gate survives them, is
   unverified.
6. **H6 MEMO semantics.** Its soundness with trailed captures, atomic
   groups and lookaround [FH24]; its memory (points × subject length, capped
   or run-length encoded as in [DSL21]); its interaction with the step
   budget; and the D26 ruling on answering where PCRE2 errors.
7. **H7 Callout fire sets move with the planner.** This is allowed (§11.6),
   but a callee that is not pure sees a different firing set when a
   release changes a cut. That is release-to-release behaviour drift, and
   it should be documented.
8. **H8 Many small machines and gcc.** Each DFA segment is its own
   table/goto region. gcc's superlinear compile time (APPROACH §2) penalizes
   big functions, not many small ones, so this is probably benign. Code size
   is not benign, and needs the artifact-size log.
9. **H9 The listing and the stamps.** Callers and tests read `RX_ENGINE`,
   `RX_VM_PREFILTER` and friends. They must survive as derived stamps (S2.3),
   or each removal is a caller-visible change with its spec hunk (D80).

## S8. Smallest proofs

**P1 (byte-identical): the DFA artifact's top level as stream records.** Take
the DFA engine's route (finder, reverse-pass start, scan edge, forward match,
report: today's `RX_DFA_SCAN`, `RX_DFA_START`, `RX_DFA_SCAN_EDGE` decisions)
and have it RENDER from a short list of typed records: `FIND`, `RDFA`,
`DFA(exact)`, `REPORT`, under the D182 tiling discipline. The stamps are
derived from the records. Gate: an identity sweep over the corpus with
movers = 0, and `--emit-ir` lists the records for DFA artifacts too. **It
shows** that one record type carries the DFA route as well as the VM body,
and **it falsifies** the approach if the DFA top level cannot be expressed
without kind-specific escape hatches.

**P2 (byte-identical): the VM-hybrid's prologue on the same records, with a
seam record.** Render the hybrid's forward and reverse DFA pair and its
window handoff as `DFA(locate)`, `RDFA`, and a SEAM record carrying `pos`,
`proof` (PF-KNOW's facts) and `reentry` (the retry after a failed window),
then the V program. Gate: identity, movers = 0. **It shows** that the two
hosts' handoffs are one seam type, and that the subject-knowledge record has
its home.

**P3 (benefit): the deterministic finish (B1).** First the census (a
compile-only queued sweep): VM artifacts with `resume-points 0` and a
landmark that D161 add. 17 admits for the capture-erased prefix. If the
population is real, build the stream route for exactly that population:
`FIND` landmark → `WALK` back → the V program run ONCE from the walked start,
with no forward DFA pass. The program has no CHOICE, so a failure means
`FIND-next`. Gate: answer identity over the corpus with a test-only deny
lever (memory `pcrec-flag-follows-caller-effect`: a public deny only if the
route can be slower, which it can on short subjects, so this decision is
open). Measure: the match regime and dense find-all, both layers, on #3-like
rows. **It is the smallest change that demonstrates a benefit the two-engine
design does not reach without a special row.**

(A fourth candidate, if P3's population is thin: E5 for a single
fixed-width lookahead at a pattern's end, `foo(?=bar)`, as DFA trailing
context. This is B2's cheapest instance. It moves a pattern from VM to DFA
and is easy to measure.)

## S9. References

(R) = already in pcrec's REFERENCES.md under that key. NEW entries need to
be added by the manager. All were accessed 2026-11-01, read through a
summarizing fetch except [Wan19+], whose pages 3-8 were read as rendered PDF
pages. No code was downloaded or run.

| Key | Source | URL |
|---|---|---|
| [Wan19+] (R) | Wang et al., "Hyperscan: A Fast Multi-pattern Regex Matcher for Modern CPUs", NSDI 2019. §3.1 decomposition `/FAn strn … str1 FA0/`, switches; §3.1's "we leave its formal proof as our future work"; §3.2-3.3 dominator path/region and min-cut string extraction | https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf |
| [Cox10] (R) | Russ Cox, "Regular Expression Matching in the Wild" (RE2: DFA, reverse DFA, OnePass / BitState / NFA; omitted features) | https://swtch.com/~rsc/regexp/regexp3.html |
| [Gal23] (R) | Andrew Gallant, "Regex engine internals as a library" (meta engine; reverse suffix/inner and their quadratic guard; capture engine order) | https://burntsushi.net/regex-internals/ |
| [RArevinner] (R) | regex-automata reverse-inner and its leftmost fix, issue #1354, commit 64ad0b6 | https://github.com/rust-lang/regex/commit/64ad0b6 |
| [RAonepass] (R) | regex-automata one-pass DFA docs | https://docs.rs/regex-automata/latest/regex_automata/dfa/onepass/struct.DFA.html |
| [RE2onepass] (R), [GoOnepass] (R) | RE2 and Go one-pass implementations | see REFERENCES.md |
| [PGregex] NEW | PostgreSQL `src/backend/regex/README` (Spencer's engine: subre tree, per-node DFA as a pre-check, backref DFA = a copy of the referent's, "If there are many tree levels it can get very slow") | https://github.com/postgres/postgres/blob/master/src/backend/regex/README |
| [TclRE] NEW | Tcl `re_syntax` manual, "Matching" (alternation "prefers longest match"; a branch takes the preference of its first quantified atom that has one) | https://www.tcl-lang.org/man/tcl8.6/TclCmd/re_syntax.htm |
| [Toub22] NEW | Stephen Toub, "Regular Expression Improvements in .NET 7", .NET Blog, 2022 (backtracking baked into code structure; auto-atomicity; first-char switch; find optimizations; NonBacktracking's unsupported constructs) | https://devblogs.microsoft.com/dotnet/regular-expression-improvements-in-dotnet-7/ |
| [Mos23+] (R) | Moseley et al., "Derivative Based Nonbacktracking Real-World Regex Matching with Backtracking Semantics", PLDI 2023 | https://doi.org/10.1145/3591262 |
| [DotNetPR65129] (R) | dotnet/runtime PR #65129, captures for NonBacktracking | https://github.com/dotnet/runtime/pull/65129 |
| [V8lin] NEW | V8 blog, "An additional non-backtracking RegExp engine" (linear engine; fallback after 50,000 backtracks; unsupported backrefs and lookaround) | https://v8.dev/blog/non-backtracking-regexp |
| [DSL21] NEW | J. C. Davis, F. Servant, D. Lee, "Using Selective Memoization to Defeat Regular Expression Denial of Service (ReDoS)", IEEE S&P 2021, DOI 10.1109/SP40001.2021.00032 | https://www3.cs.stonybrook.edu/~dongyoon/papers/SP-21-Memoization.pdf |
| [FH24] NEW | H. Fujinami, I. Hasuo, "Efficient Matching with Memoization for Regexes with Look-around and Atomic Grouping", ESOP 2024 (arXiv:2401.12639); reports [DSL21]'s lookaround extension flawed | https://arxiv.org/abs/2401.12639 |
| [Lau00] (R), [Tro19] (R), [BT22] (R) | tagged NFA/DFA; lookahead TDFA; "A closer look at TDFA" | see REFERENCES.md |
| [VVE25] NEW | I. E. Varatalu, M. Veanes, J. Ernits, "RE#: High Performance Derivative-Based Regex Matching with Intersection, Complement, and Restricted Lookarounds", POPL 2025, DOI 10.1145/3704837 (POSIX semantics; lookarounds only at edges, bodies lookaround-free; reverse then forward pass) | https://arxiv.org/abs/2407.20479 |
| [BP24] (R) | Barrière & Pit-Claudel, "Linear Matching of JavaScript Regular Expressions" (§4.3 oracle table and `CheckOracle`; §4.4 lockstep captureless lookbehind; backrefs excluded) | https://arxiv.org/abs/2311.17620 |
| [PCRE2api] NEW | PCRE2 `pcre2api` documentation (PCRE2_NO_AUTO_POSSESS, NO_DOTSTAR_ANCHOR, NO_START_OPTIMIZE; optimizations "can cause [callouts] to be skipped") | https://www.pcre.org/current/doc/html/pcre2api.html |
| [PCRE2jit] (R), [PCRE2matching] (R) | PCRE2 JIT; `pcre2_dfa_match` semantics | see REFERENCES.md |

Repository sources read (read-only): APPROACH.md §2; decisions D146, D147,
D161 add. 17, D163, D182; docs/dev/optloop/captures_via_dfa_survey.md §0 and
§3.3; docs/design/locate_finish.md (header); docs/spec/pattern_language.md
§7.11 and §9¶9; match_api.md §11.6; plan.md's subject-knowledge row; and
`build/pcrec --features all` outputs (stamps and `--emit-ir` summaries) for the
worked patterns.
