# One instruction stream: a clean-sheet end state (lane stream-clean, round 1)

Author: lane stream-clean (opus), 2026-11-01. Read-only on the repo; written as if
pcrec's matcher code did not exist. Today's code was read only as EVIDENCE (what the
semantics demand, where speed comes from, what the kit offers) and to check that a
claim is achievable. Nothing here is a ruling.

Sources read: APPROACH.md §1-§6; pattern_language.md §4 (matching: §4.1 leftmost,
§4.2 preference order, §4.5 engines never change an answer, §4.6 give-ups);
match_api.md §3.5, §11 (callouts: §11.6 fire contract, §11.8 firing classes);
decisions D3, D146, D147, D157, D161 (addenda 7-17), D163 (compound, add. 1-7),
D182; coding.md §2.7; src/gen/CLAUDE.md; src/opt/CLAUDE.md; plan rows [ENG-TDFA]
and the bitstream row; and today's compiler output for the ten worked patterns
(`build/pcrec --features all`, stamps and `--emit-ir`, outputs in this directory).

---

## 0. The idea in one paragraph

A pcrec artifact is ONE program: a typed instruction stream, built as records and
rendered per kind (D182's discipline, widened from the VM body to the whole
artifact). There are no engines. There are INSTRUCTION FAMILIES — choice/control
(what the VM is today), automaton (what the DFA is today), search/scan (what the
kit does today), and assertion/call (lookaround, backreference, callout, part
call) — and every member obeys ONE seam contract. The single idea that makes the
mix exact is this: **every instruction is a generator of continuations in
preference order, and there is one choice stack for all of them.** A VM `split` is a
two-element generator. An accept-list automaton is an n-element generator. The
kit's candidate finder is the generator of start positions, and "advance to the
next start" is just a backtrack into it. A deterministic segment is a generator
that provably yields at most one continuation the rest of the pattern can use, so
it pushes nothing. Segmentation is a planner's choice of form for each stretch of
the one IR program, made by a declared first-match table whose admission
conjuncts ARE the soundness rule (§2).

---

## 1. The end state, high level

### 1.1 What exists

| layer | today | end state |
|---|---|---|
| IR | one NFA-with-instructions program (APPROACH §2) | unchanged: still the one program. It is the source every form is derived from |
| engine selection | `select_engine.c` routes the PATTERN to dfa or vm; VM may embed islands and a DFA prefilter; DFA may embed kit scan edges | gone as a decision. The planner assigns a FORM to each STRETCH of the program. "dfa"/"vm" survive only as derived stamps describing the result |
| artifact body | two emitters (`emit_dfa.c` ~16k lines, `emit_vm.c` ~14k lines), VM body via records (D182), DFA by direct text | one stream of typed records for the whole artifact, every byte from a kind's renderer (D182 widened) |
| seams | fixed shapes: kit find -> DFA; DFA prefilter -> VM window; VM -> island; compound controller -> part | one seam contract (§1.4), any number of seams, any order |
| kit | sites described by facts (D146/D157), rendered by the kit | unchanged in principle; kit sites become instructions in the stream with declared effects (D182 (c) ruling 1) |

### 1.2 The instruction families

Pseudo-instructions, not C. Each is ONE record kind with ONE renderer.

**Control and choice (the "VM" family).**
`LABEL`, `GOTO`, `FAIL` (pop the choice stack), `ACCEPT(start,end)`,
`CHOICE{a | b | ...}` (push the remaining arms, take the first),
`SET slot <- pos` (trailed), `CUT` (atomic/possessive commit: discard frames down to
a mark), `CALL/RETURN` (subroutines, recursion), `METER steps|work`.

**Consume (shared by every family).**
`LIT bytes`, `CLASS set`, `SWITCH first-byte -> labels`, each forward or backward.

**Automaton (the "DFA" family).**
`AUTO M dir exit` — run deterministic machine `M` from the cursor in direction
`dir`. `M` is a sub-stream of `STATE` records (transitions, accept marks, and
EDGE members: a state that loops on a class renders as a kit scan). The `exit`
mode says what the instruction yields:

| exit | yields | pushes a choice frame? |
|---|---|---|
| `FIRST` | the priority-first end of `M`'s language (D3's pruned subset machine) | no |
| `EXISTS` | whether any prefix is accepted (lookahead bodies, filters) | no |
| `LIST asc|desc` | every accepting position, consumed in one monotone order | yes: re-entry yields the next |
| `STATE` | the machine state itself, to be resumed later (streaming feed) | no |
| `TAGGED` | FIRST plus tag positions (captures inside the machine; [ENG-TDFA]) | no |

**Ordered thread set (new form, the third point on the spectrum).**
`THREADS P exit` — run the program fragment `P` as a priority-ordered thread list
(Pike-style, the undeterminized form of D3). Exact leftmost-first with captures
for any regular fragment, linear in the subject, never gives up. It is the form a
stretch takes when it is regular but neither determinizable cheaply (state cap,
D3's blow-up) nor safe to backtrack (catastrophic).

**Search and scan (the "kit" family; facts in, method the kit's, D146/D157).**
`FIND window` — the candidate generator (D161 add. 7: COMPLETE, ASCENDING, each
candidate is the origin pcrec chose). It is a generator: it sits at the bottom of
the choice stack and a `FAIL` that reaches it yields the next candidate; when
exhausted, the call answers NOMATCH (D161 add. 14's empty stream).
`SPAN class dir min max` — advance over a class run (today EDGE/STAY/VMSPAN/
VMSTRIDE/VMRUN, one instruction). `VERIFY prefix` — the kit proves offsets
(D161 add. 16's per-offset proven sets).

**Assertion and call.**
`ASSERT ±ahead|behind S` — run sub-stream `S` at the cursor; it is atomic, so `S`
is planned under an atomic context (§2.3). `BREF g` — compare against a group's
current span. `CALLOUT n` — call the bound `rx_matchfn` (§11). `PART p` — call a
sub-artifact (compound, D163), same convention as `CALLOUT` (D163 add. 5).

### 1.3 Segments

A SEGMENT is a maximal run of the stream whose instructions came from one form
choice for one stretch of the IR. Segments are a planning notion and a reading
aid (the listing shows them); the rendered artifact does not care where one ends.
Four FORMS: `backtrack` (control+consume instructions), `determinized`
(`AUTO`), `threads` (`THREADS`), `delegated` (`FIND`/`SPAN`/`VERIFY`). A form can
nest inside another only through an instruction: an `AUTO` inside a backtrack
segment is today's island; an EDGE inside `AUTO` is today's scan edge; an `ASSERT`
holds a whole sub-stream.

### 1.4 The seam contract

Every instruction is entered with the same MACHINE STATE and leaves it in one of
four ways. This is the whole contract; there is no per-pair protocol.

**State at a seam.**

| field | meaning |
|---|---|
| `pos` | the cursor (one per stream; `ASSERT` saves and restores it) |
| `slots` | ONE capture array in the parent's numbering (D163 add. 3), trailed |
| `proof` | what is already known about the subject near `pos`: per-offset proven byte sets (D161 add. 16), an END pin (the match end is known to be E), a START pin, and the context bits (what precedes `pos`) |
| `stack` | the one choice stack: frames are `(resume-label, pos, trail mark, generator state)` |
| `meters` | the step and work budgets (§4.6), charged by the instructions that can loop |

**Exits.** (1) fall through with an updated state; (2) branch to a label;
(3) `FAIL` = pop the top frame and resume its generator; (4) yield-and-push: an
instruction with more than one continuation pushes a frame holding ITS OWN resume
state, then falls through with the first continuation.

**Re-entry.** Backtracking into any instruction is the same act: pop a frame,
call that instruction's resume. For `CHOICE` the resume takes the next arm; for
`AUTO LIST` it takes the next accept position; for `FIND` the next candidate;
for `CALLOUT` with `consume` a different length if the callee offers one. A
deterministic instruction pushes nothing, so nothing can re-enter it.

**Proof flow.** Each instruction declares what proof it READS (a test it may skip
because the proof covers it) and what it WRITES or INVALIDATES. `FIND` writes the
proven sets the kit committed to; `SPAN` writes "every byte of [p, q) is in C";
the locate step writes END pins. An undeclared kit window or a consuming callout
is a barrier that invalidates the proof (D182 (c) ruling 1's "may-write-everything
barrier"). This is the general form of today's scattered "skip the test the
prefilter already made" cases ([MATCH-KNOWN], `cover`, the hybrid's "the VM never
scans").

### 1.5 Who decides segmentation, and how

A PLANNER pass, between optimization and rendering, turns the IR program into the
stream. It is one declared first-match table over STRETCHES (house rule: rows,
not an if-then web). A row is `(form, admission conjuncts, what it yields)`; the
conjuncts are the soundness rule of §2, stated as listable facts the listing can
show. Roughly, per stretch, first match:

| # | form | admitted when |
|---|---|---|
| 1 | delegated `SPAN` | a single class repeat that is DETERMINATE in context (§2.1 D-rule) |
| 2 | `AUTO FIRST` | the stretch is regular, capture-free (or captures only at its two ends), DETERMINATE in context, under the state cap |
| 3 | `AUTO FIRST` absorbing the tail | the stretch and everything after it to the pattern end (or to an atomic boundary) is regular and the caller asks for no captures inside it |
| 4 | `AUTO TAGGED` | as 2/3 but with captures inside, when [ENG-TDFA] exists |
| 5 | `AUTO LIST` | MONOTONE in context (§2.1 O-rule), captures a function of the end |
| 6 | `THREADS` | regular with captures, but catastrophic for backtracking or over the state cap |
| 7 | `backtrack` | always admissible (the floor, and the only form for backrefs into the stretch, recursion, non-atomic lookaround, consuming callouts) |

The start of the stream (where to begin attempts) is the same table applied to
the "prefix" stretch: `FIND` over the facts pcrec sends (spans bounded to the
origin it chose, D161 add. 9), plus, when the origin is a landmark, a reverse
segment (row 1 or 2 run backward: D161 add. 17's "reverse DFA as scaffolding,
scan edges inside").

Two properties make the planner safe to grow. **Row 7 always admits**, so any
stretch the table cannot prove gets the exact backtracking form (decline is always
safe, src/opt's soundness direction). **Every admissible tiling gives the same
answer** (§4.5 of the language spec, generalized from "engines" to "tilings"), so
forcing any row off is a deny axis and a differential test (§5).

Costs choose AMONG admissible rows, never between sound and unsound. Where the
table has more than one admissible row, the order of rows is the price; pricing
placement (lane rulepilot's question) plugs in here and nowhere else.

---

## 2. The soundness rule

### 2.1 The one statement

Fix a stretch `S` of the program (single entry, single exit) and its CONTINUATION
`K`: everything that can run after `S` exits, through enclosing loops and up to the
accept, as a language plus the slots it reads. From an entry state `σ`, backtracking
enumerates `S`'s ways `w1, w2, ...` in preference order (§4.2: alternatives left to
right, greedy more-first, lazy fewer-first, concatenation lexicographic), each
leaving `σi = (end_i, slots_i)`. The answer through `S·K` is the first `i` for which
`K` succeeds from `σi`, with `K`'s own first way.

**A form `F` may replace `S` iff, for every entry `σ`, `F` delivers the same first
successful `σi` and leaves the frames below it untouched.** Every row of the
planner's table is a sufficient, CHECKABLE condition for that statement:

**D (determinate in context).** `K` cannot succeed from any `σj, j > 1`, unless it
also succeeds from `σ1`. Then only `w1` matters: `S ≡ (?>S)` here, `F` computes
`w1` (D3's pruned machine computes exactly the priority-first end), and pushes no
frame. Checkable conjuncts, in increasing power:
- the single-class case: `S = C{m,n}` greedy and `first(K) ∩ C = ∅`, or `K` can
  accept at once (then `w1`, the longest, is preferred anyway). This is today's
  possessify unique-iteration test, the only one most real patterns need;
- the general disjointness case: for the ways of `S` that end earlier than a later
  way would, the byte that the later way consumes next is not in `first(K)`;
- an END pin in the proof (the match is known to end at `E`): `K` must end at `E`,
  so ways of `S` whose end leaves a remainder `K` cannot fill exactly are dead
  (MRL); with a fixed-width `K`, `S`'s end is forced to `E - width(K)`;
- an atomic context (`(?>...)`, a possessive quantifier, an atomic lookaround):
  only `w1` is ever used, by definition.

**O (monotone).** The ends `end_1, end_2, ...` are strictly monotone (greedy single
repeat: descending; lazy: ascending; `a|ab`: ascending) and each `slots_i` is a
function of `end_i` (no captures inside `S`, or captures only at `S`'s boundary,
or at a fixed margin from it). Then `AUTO LIST` yields the same sequence; equal
ends with equal slots are one continuation, so de-duplicating them is exact.
Non-monotone stretches such as `(?:aa|a)*` are NOT admitted (APPROACH §2 A-1
found this the hard way).

**T (tail).** `S·K` is regular up to the accept (or up to an atomic boundary) and
nothing after reads a slot set inside `S`. Then the end of the answer is the
priority-first end of `S·K` as one machine (D3). Slots inside are delivered by
`AUTO TAGGED`, by `THREADS`, or by a short backtrack pass with the END pin in the
proof (today's hybrid finish, which is this rule plus an end pin).

**P (thread set).** `S·K` is regular up to the accept or an atomic boundary,
captures allowed. A priority-ordered thread list gives exact leftmost-first with
captures (the argument RE2 and Rust regex rely on; D3 is its determinized form).
Admissible whatever the ambiguity; its cost is `O(n·m)`, never exponential, never a
give-up.

**B (backtrack).** Always admissible.

### 2.2 Where none of D/O/T/P applies

Exactly four things force a stretch into `B` (everything else is a cost question):

1. a BACKREFERENCE (or `(?(n)...)` condition) in `K` reading a group set inside an
   ambiguous `S`: two ways with the same end can differ in slots, so `K`'s answer
   depends on which way, and the order of ways is the program's;
2. RECURSION and subroutine calls whose body is ambiguous (the continuation is a
   stack, not a language);
3. a NON-ATOMIC lookaround (`(?*...)`) whose choice points stay live;
4. a CONSUMING callout (`consume`, §11.7): the next position is the callee's.

In `B`, re-entry is today's VM: a frame per live choice. But a `B` segment is not
monolithic: the planner DESCENDS into it and applies the rows to each sub-stretch,
so `(.+)=(\d+);\1` (`.` overlaps `=`, so `(.+)` is ambiguous, and `\1`
reads it) keeps `CHOICE` frames for `(.+)` but gets a `SPAN` for the determinate
`(\d+)` inside the same backtrack segment. A deterministic instruction inside a backtrack loop is
a pure function of its entry state and pushes nothing, so re-running it after a
frame below it resumes is exact; nothing ever re-enters it.

### 2.3 Rules that fall out

- **Captures are not a reason for the VM.** A capture boundary at a SEAM is a `SET`
  instruction. Only captures INSIDE an ambiguous stretch need a form that tracks
  them (`TAGGED`, `THREADS`, or `B`).
- **Lookaround bodies are planned in an atomic context.** A regular, capture-free
  lookahead body is `AUTO EXISTS` (any prefix accepted suffices); a fixed lookbehind
  is a context span before the origin when the kit can state it (D161 add. 16),
  otherwise `ASSERT behind` over a reverse `AUTO`.
- **Callouts are ε to the analysis when non-consuming, and a barrier when
  consuming.** §11.6 makes fire count and order unspecified and defines the answer
  only for pure callees; skipping a later way of `S` that rule D proves dead cannot
  change a pure callee's answer, because that path fails whatever the callee
  returns. A consuming site makes `first(K)` unknown, so D fails and `B` stays.
- **Start search is a generator like any other.** The leftmost rule (§4.1) is the
  ascending order of `FIND`'s candidates. A landmark origin with a reverse segment
  is exact under D161 add. 17's admission (the reverse class excludes every byte
  the landmark can match, so no start before one landmark pairs with a later one);
  otherwise the reverse form must yield every start in ascending order, or decline
  to a forward `FIND`.

---

## 3. The worked patterns

Notation: one instruction per line; `-> x` names what it yields; `; fail -> FIND`
means a failure pops back to the candidate generator (the bottom frame). `[D]`,
`[O]`, `[T]`, `[P]`, `[B]` name the §2.1 rule that admitted the form. "Today" is
the shape `build/pcrec --features all` emits on main (stamps in this directory's
`p1.c`..`p10.c`). Every stream is unanchored search from `startpos`.

### 3.1 `abc` (pure literal)

```
FIND { origin 0; spans a,b,c at 0..2, all exact; consumable 3 }   -> c
ACCEPT (c, c+3)            ; only if the kit's proof covers [0,3)
```
If the kit proves less (say only offset 0), the planner reads the proof and emits
`LIT "bc" at c+1` before the accept. Segments: one delegated segment. Seam
FIND -> ACCEPT hands `pos = c` and the proof "offsets 0..2 hold".
**Today:** DFA, `RX_DFA_SCAN "cover"`: the same thing. **No benefit**; the stream
just spells today's best route directly.

### 3.2 `[a-z]+@x` (landmark walk)

```
FIND { origin = the '@'; spans '@','x' at 0,1 exact; consumable 2;
       reverse span [a-z]+ before the origin (fact: [a-z] excludes '@') }  -> L
SPAN back [a-z] from L, min 1, floor startpos      -> s   [D]  ; fail -> FIND
ACCEPT (s, L+2)
```
Segments: delegated (FIND), delegated reverse (SPAN), done. Whether the kit does
the reverse walk inside FIND or as the separate SPAN is the kit's choice (D161
add. 17: "the memfn would be the one to implement perhaps both directions"); the
stream allows either. Leftmost: a run before one '@' cannot cross an earlier '@',
so FIND's ascending order is the order of starts. `floor startpos`: a run that
begins before `startpos` yields `s = startpos`, which is the correct match.
Seams hand `pos`, then `(s, proof "[s,L) in [a-z]; '@x' at L")`.
**Today:** DFA, unanchored forward pass to the end, then a reverse pass for the
start, range scan edge, req run `@x`. The general family (reverse DFA seeded at
the landmark, scan edges inside) is D161 add. 17; the stream is where it lives
as one instruction rather than as a route.

### 3.3 `(\w+)@(\w+)\.com` (captures)

```
FIND { origin = the '@'; span '@' at 0; span ".com" later, unbounded (presence);
       reverse span \w+ before the origin (\w excludes '@') }   -> L
SPAN back \w from L, min 1, floor startpos   -> s     [D] ; fail -> FIND
SET g1 = (s, L)
SPAN fwd \w from L+1, min 1                  -> e     [D: \w excludes '.']
SET g2 = (L+1, e)
LIT ".com" at e                                          ; fail -> FIND
ACCEPT (s, e+4)
```
No choice frame above FIND. Captures are SETs of seam positions. Check on
`a@b@c.com`: L=1 gives s=0, g2 "b", `.com` fails at '@'; L=3 gives s=2, g2 "c",
match [2,9) — PCRE's answer (start 0 fails, start 1 fails, start 2 matches).
**Today:** VM (`RX_ENGINE_WHY "capture group at pattern offset 0"`), hybrid
prefilter: a capture-erased forward DFA and reverse DFA locate the exact window,
then a frameless, possessified VM re-walks it to write the slots. The match is read
three times; the stream reads it once. **Benefit B1** (§4).

### 3.4 `(a|ab)(c|bcd)(d*)` (preference order a longest-match DFA gets wrong)

```
FIND { origin 0; span 'a' at 0; span {b,c} at 1 }        -> c0
SET g1.start = c0
CHOICE { e1 = c0+1  |  LIT 'b' at c0+1; e1 = c0+2 }     [O: ends ascending, g1 = f(end)]
SET g1.end = e1 ; SET g2.start = e1
SWITCH byte at e1: 'c' -> e2 = e1+1
                   'b' -> LIT "bcd" at e1 -> e2 = e1+3
                   else FAIL                              [D: arms' first bytes disjoint]
SET g2.end = e2
SPAN fwd 'd' from e2   -> e3                             [D: K accepts at once]
SET g3 = (e2, e3)
ACCEPT (c0, e3)
```
On `abcd`: arm 1 gives e1=1; byte 'b'; `bcd` matches [1,4); `d*` is empty; answer
[0,4), g1 [0,1), g2 [1,4), g3 [4,4) — the spec's own example (§4.2¶6). A
longest-preferring tagged automaton would take `ab` and report g1 [0,2). On `abc`
the `bcd` arm fails, FAIL pops the CHOICE frame, arm 2 gives e1=2, 'c' gives e2=3:
[0,3), g1 [0,2). One frame, and only where the program has a real choice whose
loser can be needed. Segments: delegated, backtrack (one CHOICE), consume,
delegated SPAN.
**Today:** VM, hybrid prefilter with handoff, alternation islands. Same answer;
the difference is that the stream's frame count is the pattern's real ambiguity,
not the engine's default.

### 3.5 `(\w+)\s+\1` (backreference)

```
FIND { origin 0; span \w at 0; span \s later, unbounded (presence) }   -> c
SPAN fwd \w from c, min 1    -> e1     [D: \w ∩ \s = ∅]
SET g1 = (c, e1)
SPAN fwd \s from e1, min 1   -> e2     [D: \1 starts with a \w byte]
BREF g1 at e2                -> e3     ; fail -> FIND
ACCEPT (c, e3)
```
The backreference is a compare instruction, not a reason for frames: `(\w+)` is
determinate in context, so `\1` reads the only slots that can exist (§2.2 case 1
does not fire). No skip after a failed start: `the he` fails at 0 and matches at 1.
**Today:** VM, frameless (so already deterministic), but `RX_VM_PREFILTER
"none"`: no kit start search. **Benefit B2** (reach): FIND and SPAN are available
to a backreference pattern because they are instructions, not a DFA route.

### 3.6 `foo(?=bar)|(?<!x)baz` (lookaround)

```
FIND { arm A: origin; spans f,o,o,b,a,r at 0..5 exact; consumable 3
              (the lookahead is a span after the consumed end);
       arm B: origin; context span [^x] at -1, "absent byte satisfies";
              spans b,a,z at 0..2 exact }                        -> c
SWITCH byte at c:                                          [D: 'f' vs 'b']
   'f' -> ASSERT ahead { LIT "bar" at c+3 }   (deleted when proved)
          ACCEPT (c, c+3)
   'b' -> ASSERT behind { c == 0 or byte[c-1] != 'x' }  (deleted when proved)
          ACCEPT (c, c+3)
```
The two arms cannot both start at one origin, so there is no frame. Were they to
share a first byte, a CHOICE would order them, arm A first (§4.2¶2). Each lookaround
body is planned in an atomic context: here a literal and a one-byte context test.
Leftmost across the arms is FIND's ascending order over the union window.
**Today:** VM (`(?=...)` forces it), hybrid prefilter `first-class-bounded`,
reseed `adaptive`. **Benefit B2:** with D161 add. 16's context spans, the whole
pattern runs with no backtracking machinery, and with the kit's proof, with no
engine at all.

### 3.7 `(?:cat|dog|bird|fish|...30 words...)s?` (heavy alternation)

```
FIND { origin 0; per-offset byte sets of the 30 words (the kit's multi-word form) }  -> c
AUTO FIRST M(trie·s?) fwd from c   -> e     [T: regular, capture-free to accept]
                                             ; fail -> FIND
ACCEPT (c, e)
```
D3's priority subset construction over the factored trie gives the leftmost-first
end (`cats` vs `cat`+`s?` is the machine's business). The planner could equally
choose today's unanchored-forward + reverse-start pair: both are AUTO instructions.
**Today:** DFA, unanchored, byte-class prefilter, reverse-pass start. **No
benefit**; same machine.

### 3.8 `(a+)+b` (nested quantifier)

```
FIND { origin = the 'b'; span 'b' at 0; reverse span a+ before it (a excludes 'b') }  -> L
SPAN back 'a' from L, min 1, floor startpos   -> s    [D: first(K) = {b}]
SET g1 = (s, L)       ; the first way: iteration 1 takes the whole run, iteration 2 cannot start
ACCEPT (s, L+1)
```
`(a+)+` followed by `b` is determinate, and its first way's group is derivable (the
whole run), so the catastrophic shape costs one reverse span. The interesting
variant is a NON-determinate one, e.g. `(a|aa)+ab`: neither D nor O holds (ends are
not monotone in preference order) and backtracking is exponential on a failing
run. It is regular with captures, so rule P admits `THREADS`: an ordered thread
list over the fragment, linear, exact captures, no give-up.
**Today:** VM, hybrid prefilter (memchr for 'b', reverse pass), `RX_VM_FRAMELESS
0` (the finish keeps frames). Today's answer is right and fast on this exact
pattern because the window is exact; **the variant is Benefit B4a**.

### 3.9 `x(?C1)y\d+` (a callout mid-pattern; site 1 non-consuming)

```
FIND { origin 0; spans 'x' at 0, 'y' at 1, \d at 2 }   -> c   ; the callout is ε to the analysis
CALLOUT 1 at c+1, slots so far                          ; fail -> FIND  (class: once-per-start)
LIT 'y' at c+1          (deleted when proved)
SPAN fwd \d from c+2, min 1      -> e                   [D: K accepts at once]
ACCEPT (c, e)
```
Skipping a start where `y` or `\d` is absent skips a fire on a path that fails
whatever the callee returns: allowed by §11.6 (fire count unspecified; a pure
callee's answer unchanged). With `consume` on site 1, FIND carries only the span
`x`; the CALLOUT writes `pos = c+1+k` and INVALIDATES the proof; `LIT 'y'` is
re-tested at the new cursor.
**Today:** VM (`(?C1)` forces it), `RX_VM_PREFILTER "none"`. **Benefit B2.**

### 3.10 `\p{Greek}+\s\d{3}` under `-e utf8`

```
FIND { origin 0; span 0 = Greek lead bytes, a SUPERSET (D161 add. 10): filter only }  -> c
AUTO FIRST M(Greek+ \s \d{3}) fwd from c   -> e     [T; D: Greek ∩ \s = ∅]
                                                     ; fail -> FIND
ACCEPT (c, e)
```
The Greek loop is a multi-state byte cycle, so it renders as states, not as a
one-state scan edge. The candidate is a character start; FIND's completeness covers
every Greek start, inexact bytes are re-checked by the machine.
**Today:** DFA, unanchored, byte-class prefilter, range scan edge, reverse-pass
start. **No benefit**; the open problem (a SPAN over a multi-byte class, the
"chain of sets" ADVANCE D161 add. 17 withdrew) is the same in both designs.

### 3.11 Summary

| # | pattern | today's route | stream segments | claim |
|---|---|---|---|---|
| 1 | `abc` | DFA cover | FIND, ACCEPT | none |
| 2 | `[a-z]+@x` | DFA fwd + reverse pass | FIND, SPAN back | small (one walk not two; also reachable today via D161 add. 17) |
| 3 | `(\w+)@(\w+)\.com` | VM + 2-DFA window | FIND, SPAN, SET, SPAN, SET, LIT | B1 one pass, not three |
| 4 | `(a\|ab)(c\|bcd)(d*)` | VM + islands | FIND, CHOICE, SWITCH, SPAN | frames = real ambiguity |
| 5 | `(\w+)\s+\1` | VM, no prefilter | FIND, SPAN, SPAN, BREF | B2 reach |
| 6 | lookaround | VM + prefilter | FIND, SWITCH, ASSERT | B2 reach |
| 7 | 30 words | DFA | FIND, AUTO | none |
| 8 | `(a+)+b` | VM + window | FIND, SPAN back, SET | variant: B4a |
| 9 | callout | VM, no prefilter | FIND, CALLOUT, LIT, SPAN | B2 reach |
| 10 | Greek utf8 | DFA | FIND, AUTO | none |

---

## 4. Benefit case

Ranked by how much I believe each one. "Measure" names the reading that would
confirm or kill it; none is measured yet.

### B1. Speed: one pass for capture patterns whose stretches are all determinate (MEDIUM)

- **What.** Today, a capture group sends the whole pattern to the VM. When the
  VM program is frameless (every quantifier possessified, `RX_VM_FRAMELESS 1`),
  the VM is already deterministic, but it still runs behind a capture-erased
  forward DFA and reverse DFA that locate the window first: the match is read
  three times (3.3). In the stream, captures at seams are SETs and the match is
  read once, from the landmark.
- **Reaches.** Patterns 3 and 8, and the common real shape: tokens separated by
  delimiters their classes exclude (emails, key=value, log fields, dates, IPs with
  captures).
- **Measure.** (a) Census: VM-routed corpus and bench patterns with
  `RX_VM_FRAMELESS 1` and every group boundary at a determinate seam (the
  population). (b) Timing: the email-shaped cell at high match density, stream vs
  today's hybrid, both kit layers (D147). The gain is per MATCH, so at low density
  the kit's FIND dominates both and the gain vanishes; the claim is only for
  match-dense subjects.
- **Weakness.** Today's design reaches much of this by growing [ENG-TDFA]
  (captures in a DFA) or the compound's concatenation split. So B1 is a "sooner and
  without a third engine" claim, not a "never otherwise" claim.

### B2. Reach: search, scan and proof for every pattern, whatever forces backtracking (MEDIUM-STRONG)

- **What.** Kit FIND, SPAN and proof are instructions with declared effects, not a
  DFA route. A backreference, a callout or a lookaround no longer decides how the
  pattern SEARCHES; it decides only the form of its own stretch.
- **Reaches.** Patterns 5 and 9 today get no kit start search
  (`RX_VM_PREFILTER "none"`); 6 gets a prefilter but keeps the VM for the whole
  pattern. In the stream all three run with no frames above FIND.
- **Measure.** Census: VM-routed patterns with `RX_VM_PREFILTER "none"` or with a
  prefilter-plus-VM route whose VM program is frameless; then timing on the bench
  cells among them.
- **Weakness.** Today's design can grow over-approximation prefilters per construct
  (it already did for lookaround). The stream's advantage is that it needs no
  per-construct rule: "a callout is ε when non-consuming" (§2.3) is one sentence,
  stated once.

### B3. Simplicity: parallel mechanisms deleted (STRONG over time, ZERO at first)

These become instructions or rows, and their parallel copies go away:

| deleted special case | becomes |
|---|---|
| engine selection as a routing decision (`select_engine.c`; `RX_ENGINE_WHY` as a router) | a derived stamp: "dfa" iff the stream has no frames |
| the hybrid prefilter protocol and its re-seed modes (`RX_VM_PREFILTER`, `_LANG`, `RX_VM_RESEED exact/adaptive`) | `FIND` + `AUTO` instructions in front of the stretch that needs frames |
| VM alternation islands and accept-list islands as a VM-only mechanism | `AUTO FIRST` / `AUTO LIST` instructions, admitted by rows D and O |
| two families of scan sites for one idea: DFA EDGE/STAY vs VM VMSPAN/VMSTRIDE/VMRUN | one `SPAN` instruction (the kit already shares one piece renderer for the VM three, D182 note) |
| two "next start" loops: the DFA start/search loop and the VM unanchored retry advance (K49) | the `FIND` generator at the bottom of the one choice stack |
| compound clients 2 (DFA locate + VM finish), 7 (concatenation split) and captures-on-demand as controllers over separate machines | tilings of one stream; backtracking ACROSS the cut, which D163 add. 3 records as "not addressed", is a generator frame |
| the DFA route table's LOCATE rows (`cover`, `reverse-pass`, `end-minus-width`, `attempt-start`) as engine routes | rows of the planner's prefix table, over instructions |
| "port this optimization to the other engine" plan rows (D161 add. 17: "the scan edge optimizations benefit forward dfa") | one instruction, one row; it lands once |

- **Measure.** Count, before and after: route stamps and deny axes, kit site kinds
  (`memfn_sites.def`), plan rows whose text is "the same for the VM/DFA", and
  emitter lines. The honest caveat: the DECISIONS do not vanish, they move into
  the planner's table. What vanishes is the second copy.

### B4. New capability (MIXED)

- **B4a, linear exact captures for ambiguous regular stretches (WEAK until counted).**
  `THREADS` (rule P) gives leftmost-first captures in `O(n·m)` with no step budget,
  for stretches such as `(a|aa)+ab`. Today these run on the backtracking VM behind
  an exact window, which makes the common case fast; the claim is for the residue
  where the finish itself explodes. Measure: a census of `RX_VM_FRAMELESS 0`
  patterns, then give-up counts on adversarial subjects. Weak because the exact
  window already hides most of it.
- **B4b, many seams with one choice stack (STRONG, structural).** A pattern can go
  determinate -> backtrack -> determinate -> backreference -> determinate with
  re-entry across every seam, e.g. `(\w+)=([^;]*);(?:\1|x)+`. Today a pattern has
  one engine plus islands; the compound gives fixed controller shapes with no
  backtracking across a cut.
- **B4c, every admissible tiling is a differential test (MEDIUM).** §4.5's "engines
  never change an answer" generalizes to "tilings never change an answer". Forcing
  each row off, or a random admissible tiling, is test-axes' answer-identity sweep
  over a much larger space than two engines.
- **B4d, proof across every seam (MEDIUM).** The kit's proven sets delete tests in
  backtracking stretches too (3.6, 3.9), under one declared-effects rule instead of
  [MATCH-KNOWN]'s per-route conjuncts.
- **B4e, a new engine is a new instruction (WEAK, speculative).** The bitstream
  locator row ([Cam14], "a THIRD ENGINE ... APPROACH needs an amendment") becomes
  a generator instruction beside FIND.

### What is NOT a benefit

Patterns 1, 7 and 10: same machine, same speed. "One renderer discipline for the
whole artifact": tidier, and worth nothing by itself. The derived `RX_ENGINE` stamp:
cosmetic.

---

## 5. Bird-in-the-hand discipline: the two end states, fully built

Today's design GROWN AS FAR AS IT CAN GO: a DFA engine (D3, Hopcroft, kit FIND, scan
edges, landmark reverse walks per D161 add. 17); a backtracking VM (D182 records,
possessify, MRL, exact and accept-list islands, hybrid locate + finish); [ENG-TDFA]
built (captures in the DFA); the bitstream locator as a third engine; the compound
with every filed client (split, locate/finish, concatenation split, per-branch
locators, captures on demand, arch variants). Against it, the stream end state of
§1-§2.

| question | today, grown | stream |
|---|---|---|
| captures on a determinate pattern, one pass | yes, via TDFA (a third engine) | yes, SETs at seams; TDFA becomes one AUTO exit mode |
| kit search for a backref / callout pattern | yes, with a per-construct over-approximation rule each | yes, one rule (constructs are instructions with declared effects) |
| backtracking ACROSS a determinate/backtrack seam | no: islands live inside the VM; the compound's cut needs a unique end (D163 add. 3) | yes: a generator frame |
| more than one seam of each kind, any order | only as nested islands inside one VM body | yes |
| an optimization lands once for all patterns | no: each engine's site (EDGE vs VMSPAN) and route | yes |
| a proof deletes a test anywhere | per route, with route-specific conjuncts | one declared-effects rule |
| linear exact captures on ambiguous regular stretches | only if a Pike engine is added as a fourth engine | a THREADS instruction |
| DFA-only streaming feed (`stream_feed`) | yes | yes: a stream with only AUTO + FIND is streamable; same limit for mixed |
| whole-pattern minimization | yes | yes, when the tile is the whole pattern |
| a pure-DFA artifact is meter-free and never gives up | yes, by engine | yes, derived: no frames, no meters |
| two independent emitters as each other's control | YES | NO: see below |

**What today's design can NEVER do that the stream can:** re-enter a determinate
segment from a later failure across a seam (generator frames), and carry a pattern
with several VM-forcing constructs in different places without routing the whole
pattern to one engine. Those are structural: the engine split is a per-pattern
partition, and the compound is a per-pattern controller over whole machines.

**What the stream can never do that today's design can:** have two independently
written engines check each other. Today `--engine=dfa` vs `--engine=vm` is an
answer-identity control that does not share a source with what it controls
(memory pcrec-check-design-lessons). In the stream, every tiling is rendered by the
same renderers: a bug in `SET` or `FIND`'s rendering is in every tiling, and B4c's
differential cannot see it. The libpcre2 differential (PC-3) stays the only
independent oracle. This is a real loss; it should be priced, not waved away.

---

## 6. Holes I already see, ranked

1. **Captures inside repeats are outside rules D/O.** `(\w+\.)+com` puts a group
   inside a loop; rule O requires slots to be a function of the end, rule D's
   first way still needs per-iteration slots. Without TAGGED or THREADS, these stay
   B, and the B1 population may be much smaller than "every possessified pattern".
   Only the census (§7 P2) can size it.
2. **The planner is new analysis with silent-miscompile risk.** Rule D beyond the
   single-class case (general disjointness, END-pin reasoning) is new code where
   an error is a wrong answer. Decline-by-default and the row-off differential
   help; they do not remove the risk.
3. **The shared-source control loss** (§5). Mitigation: keep PC-3; consider keeping
   ONE independently written reference tiling (pure backtrack) whose renderers are
   separate code, as the control.
4. **Generator state for `AUTO LIST` inside loops.** A LIST frame inside an
   iterated group needs per-frame storage for its accept positions, bounded by the
   window; the meters must charge it. Today's accept-list islands have the same
   problem in a narrower place.
5. **Proof invalidation must be complete.** A missing INVALIDATES on an instruction
   is a silent miscompile. D182 (c) ruling 1's "undeclared = may write everything"
   is the right default; every kit window must declare.
6. **THREADS and callouts do not mix.** A thread list fires sites in thread order,
   not backtracking order; firing class 1 ("a passing fire IS the match") breaks.
   Rule P must exclude callout-bearing stretches.
7. **Give-up behaviour moves with the tiling.** match_api §3.5¶2 already says
   which entry gives up is that entry's property, but every pinned give-up witness
   moves when a stretch changes form.
8. **Planner cost model.** Where several rows admit, the row order is the price.
   That is the pricing question (lane rulepilot) again, not answered here.
9. **Emitted size and gcc time.** Many small instructions with kit text each; the
   size caps and gcc's superlinear time on big functions (APPROACH A-3) bound how
   fine a tiling may be. AUTO can render as its own function when large.

---

## 7. Smallest proofs

**P1 (byte-identical): the VM artifact's outer scaffolding as instructions.** Put
the VM's entry ladder, the hybrid prefilter's locate call and the unanchored retry
advance into D182's record as three new kinds (`FIND`, `AUTO`, the generator
frame at the stack bottom) for ONE route (pattern 3's). Movers = 0 over the
identity gates. It shows Frank's sentence literally: one record stream holding VM
codes, DFA codes and kit codes, with no change in bytes.

**P2 (no emitted change): the planner as a dry-run census.** Run the §1.5 table
read-only over the corpus and the bench patterns, using facts the compiler already
computes (possessify's unique-iteration test is rule D's single-class case) and
print the tiling per pattern. Count: the B1 population (VM patterns whose every
stretch is D with captures at seams); the B2 population (VM patterns that gain
FIND); the stretches only P admits (B4a); the patterns with more than one
VM-forcing construct (B4b). This is D77's measurement before building, and it sizes
hole 1. It is a sweep: queue it.

**P3 (a benefit): the one-pass capture route for one shape.** For the population
P2 finds, emit `FIND landmark; SPAN back; SET; SPAN; SET; LIT; ACCEPT` behind a
test-only lever (memory pcrec-flag-follows-caller-effect); prove answer identity
over the corpus; time it against today's hybrid on an email-shaped bench cell at
high match density, both kit layers. If B1 does not show there, it does not exist.

---

## 8. Migration cost (separate; never subtracted from §5)

- The DFA emitter (~16k lines) into records: the largest single cost; byte-identical
  steps, each an identity-gate run.
- The planner replacing `select_engine.c` while producing today's routes exactly
  (byte-identical), then new rows one at a time, each with its own lever and
  measurement.
- The kit: EDGE/STAY and VMSPAN/VMSTRIDE/VMRUN merge into one SPAN site kind; a kit
  change and a pcrec abi event (D146).
- test-axes: the engine axis becomes tiling axes; the spec's §4.5 sentence and
  match_api's engine stamps are rewritten (D80: spec in the same change).
- The compound: clients 2 and 7 and captures-on-demand fold into tilings; split
  and arch variants stay controllers (they choose between whole artifacts).
- Order that keeps every step shippable: P1 (records for scaffolding) -> FIND
  generator unifies the two start loops -> SPAN unifies the scan sites -> the planner
  reproduces today's routes -> P3 and the B2 rows, each measured -> THREADS only when
  P2's census shows a population.
