# ENG-BREP — the bounded-repeat emission strategy

**STATUS: PROPOSED, AMENDED PER R24 (2026-08-15/16)** —
`../dev/reviews/2026-08-15-r24-eng-brep.md`. Three read-only critics
(soundness, measurements-vs-prose, consistency). **The central result HELD and
was strengthened; one design claim was REFUTED and five were narrowed.**

What held, and by more than this note could show. The repaired
possessification rule of §2.2 — unique-iteration + non-nullable +
disjoint-or-exact — is sound for GREEDY quantifiers against **libpcre2** as
well as python, at 0 counterexamples over the full 5,016 × 260 family with an
identical possessifiable population; that closes §8 item 6's own disclosed gap
from the outside. §2.2's transitive-FOLLOW line — which §8 item 8 nominated as
"the single most likely place for a soundness bug to be hiding" — survived a
42,336-pair targeted attack at 0 divergences, with failing-direction controls
confirming it is load-bearing rather than inert. Both censuses in §2.6 recount
exactly from raw data and are robust to leave-one-out. All four plan-row
requirements were confirmed accurately discharged.

**What did NOT survive: §2.3's lazy paragraph.** The note claimed greedy, lazy
and possessive agree on the span whenever the disjointness arm applies. They
do not: on a NULLABLE remainder the follow's first-byte test is vacuous, and a
lazy quantifier stops at the bottom of the exit chain where a greedy one tops
out. 316 diverging cells, both oracles agreeing; `a{1,3}?` on `"aaaa"` is
`(0,1)` lazy and `(0,3)` possessive. §2.2's rule now carries a lazy-only
conjunct, §2.3 states the corrected argument, and §2.4 runs the lazy family
that this lane's probe structurally could not — its helper returned `None` for
every lazy row, because a lazy quantifier has no possessive spelling, and
nothing in the output said half the question was unasked. **No live
miscompile: nothing is implemented.** This is the design-first process
catching a defect before an emitter exists, which is what it is for.

Five narrowings, applied: `$` in the follow is promoted from BELIEVED to
MEASURED-WITH-GATE (safe at 0/720, unsafe at 180/720 under `(?m)`, so the gate
must be a live check — §2.5); §3.4's capture derivation regains the
ZERO-ITERATION clause the archived probe had and the prose dropped, 42% of its
own validated population (§3.4); §2.7's "the probe is wrong in the right
direction" is qualified to CATEGORIES, with the structural reason pcrec itself
is exact for caseless (§2.7); §6's instrument is disclosed as span-only and
python-only, and the panel's captures-aware three-way rebuild confirms the
claim at 15,600 cells (§6); and U9 is cited where the oracle choice matters
(§2.4, §5.3). §5.3's greedy-AND-lazy sweep is now mandatory rather than
advisory.

Four measurement discrepancies, all in the rung census, all fixed by
re-derivation with a COMMITTED script (`probes/census_rungs.py`,
`probes/probe_cell33.sh`) — and the shared cause is recorded in §10.1: an
uncommitted `sort -u` pipeline running under a UTF-8 locale, whose collation
merges strings differing only in punctuation, which is close to a worst case
for a corpus of regexes. §3.2 and §7 carry the corrected figures.

Sections carry **[R24]** markers where the panel's finding is what changed
them.

Design note for the `[ENG-BREP]` plan row, written
DESIGN-FIRST and panel-eyed before any implementation lane opens, on the
scheduling precedent K18 set at the R21/R23 close. **This note is not the
fix.** It carries the analysis, the strategy ladder, the measurements that
picked between the candidates, a termination argument, and the validation plan
an implementation lane should execute.

Written against `engine_m4.md` §2.5 (the rung ladder), §5.2 (the
verdict-discharging rewrite socket) and §6.3/§6.4 (disjoint-follow
possessification, "built M4.6"), and against the plan row's own rulings and
three amendments.

Measurement scripts, generated pattern families and archived probe output:
`eng_brep_measurements/`. Every scratch compiler this lane built was built
into a COPY of the tree by `probes/mkscratch.sh`, so no measurement here ever
entered `src/`, `build/`, or the known-fail ratchet's line of sight.

---

## 0. How to read this

### 0.1 Claim marking (house style, inherited from `k18_memo_design.md`)

Every claim below is marked **STRUCTURAL** (follows from the code's own
construction, and the note says which construction), **MEASURED** (a number
this lane produced, with the probe that produced it), or **BELIEVED** (an
argument I find convincing but did not reduce to either of the other two).
R21's and R23's shared lesson is that panels break what is BELIEVED, so the
marks point at the soft places rather than making the note look strong.

### 0.2 Six things refuted here, five of them this note's own

Put first, because a note whose refutations are buried reads as an advocacy
document. Items 1–4 are this lane's; items 5–6 were found by R24 and are
listed with the rest rather than quarantined in the panel block, because a
reader deciding how much to trust this note should see them together.

1. **The possessification analysis as the plan row states it is UNSOUND.**
   "Body's consumable set disjoint from the follow's first set → giveback is
   dead" is false on its own. MEASURED: 117 counterexamples in the first
   differential run, every one a body like `(a|ab)` whose iterations can end
   in two places. §2.4. The repair — the body must also admit a UNIQUE
   iteration — is the analysis this note actually proposes, and it survives
   the same differential at 0 counterexamples over 5,016 patterns × 260
   subjects, and (R24) at 0 against libpcre2 as well.

2. **A zero-width assertion in the follow breaks the first-set model.**
   MEASURED: `[ab]{0,4}\b` on `"abc"` matches `(0,0)` greedy and `(3,3)`
   possessive, so an assertion is not "absent from the follow" merely because
   it consumes nothing. §2.5.

3. **The plan row's last-iteration capture derivation for the motivating cell
   is wrong.** "group2 = [end−2, end−1) iff `subject[end−2] == 'a'`" fails on
   1,799 of 15,036 matches, because a group inside a loop keeps the value from
   the last iteration that ENTERED it and a later `b` iteration does not clear
   it. The corrected derivation — a backward scan to the last `a` in the
   loop's span — is 0 of 15,036. §3.4. This does not damage the rung; it
   sharpens why the rung has to be a reversed-automaton WALK and not a
   constant-offset formula.

4. **Third-amendment consequence (b) is NOT established, and this note
   reports that rather than repeating it.** "ENG-BREP's replication reduction
   also shrinks pcrec's own DFA-construction work" does not follow, because
   `src/ir/nfa.c`'s `A_REP` arm replicates the body independently of anything
   `emit_vm.c` does (STRUCTURAL, src/ir/nfa.c:561). An emitter-side counter
   changes the emitted C and nothing upstream of it. What IS established, and
   is new, is that the compiler's own cost on the erased path is
   **quadratic** in the unrolled count — 0.012 s at N=64 to 2.689 s at
   N=4000 — and that it lives in a different module than this row. §1.4.

5. **This note's own LAZY extension was unsound** [R24 S-F1, the panel's one
   design-level hit]. §2.3 claimed greedy, lazy and possessive agree on the
   span under the disjointness arm; on a nullable remainder they do not, at
   316 measured cells. The rule now carries a lazy-only conjunct. The probe
   could not have caught it: it compared each pattern against a possessive
   respelling, and a lazy quantifier has no possessive spelling, so the helper
   that noticed returned `None` and the family vanished from the differential
   without a word in the output. §2.3, §2.4, §10.1.

6. **Every "distinct" figure in the rung census was an undercount** [R24
   M-F1/M-F2], because an uncommitted `sort -u` pipeline ran under a UTF-8
   locale whose collation treats `\d+` and `[\d]+` as the same string. 11
   distinct patterns was 15; 311/111/96 was 398/191/148. The stamp tallies,
   which never passed through `sort -u`, were right all along. §3.2, §10.1.

### 0.3 The design, in brief

Bounded repeats are answered by a LADDER, cheapest first, and the ladder's
order is Frank's ruled question order:

| # | Rung | What it costs at run time | Owner |
|---|---|---|---|
| 1 | **Possessify** — prove no retreat into the loop can ever succeed (the rule is preference-sensitive: §2.2) | zero frames, zero trail | a `discharge` hook on §5.2's socket |
| 2 | **Rung-select** — the §2.5 ladder: cursor / fixed stride / reverse-deterministic / boundary record | one frame per LOOP, not per iteration | `emit_vm.c`'s per-`A_REP` rung choice (partly built) |
| 3 | **Counter-K** — one body copy per K iterations plus a counter | one frame per iteration, K amortised | new, `emit_vm.c` |
| — | Replication (today) | one frame per iteration, O(N·body) emitted C | the status quo, retained as ground truth |

The dial nobody has to guess is K: choice points are identical across K
(STRUCTURAL, §4.1), so K is purely a speed/size trade, and both of its curves
are MEASURED in §4.3. They agree on the answer.

### 0.4 What this note is not

It does not re-open D26 (diagnostic wording is tier 3; the existing cap
diagnostic is fine and §7 only asks it to point here). It does not re-argue
D45's compile budgets. It does not design DFA islands or accept-list islands.
It does not touch backrefs or atomic groups beyond noting that §5.2's socket
is the seam all three share.

---

## 1. What the emitter does today, and what it costs

### 1.1 The RULED replication reading

`X{m,n}` compiles as `m` mandatory copies followed by `n − m` NESTED optional
copies — `(X(X(X)?)?)?`, not chained optionals — with no counter and no
empty-iteration suppression test at all. That reading is RULED (D44 / R21 E-2)
and MEASURED into place: with the empty-iteration guard applied to bounded
repeats too, 60 of 225,240 generated pairs diverge from libpcre2; restricted
to `rmax == -1`, 0 of 225,240. The nesting (rather than chaining) is likewise
a measured choice, from `(?:ab|a){0,2}?b` on `"abab"`.

Both `src/gen/emit_vm.c` (`vm_opt_chain`) and `src/ir/nfa.c` (the `A_REP`
arm) implement this, INDEPENDENTLY. That independence is invisible in the
plan row and it is load-bearing for §0.2 item 4.

### 1.2 The three victims

STRUCTURAL: emitted C is O(N · body). MEASURED, on
`((a)|b){0,N}c` with captures, compiled by a scratch compiler whose
`PCREC_MAX_VM_REPEAT_COPIES` was raised so the sweep could see past the cap
(`probes/mkscratch.sh bigcap`, `outputs/replication_sweep.tsv`):

| N | emitted lines | emitted bytes | gcc −O1 | gcc −O2 |
|---|---|---|---|---|
| 1 | 350 | 13 KB | 0.11 s | 0.22 s |
| 16 | 775 | 26 KB | 0.22 s | 0.42 s |
| 64 | 2,134 | 66 KB | 0.52 s | **1.52 s** |
| 128 | 3,946 | 121 KB | 1.01 s | 4.72 s |
| 256 | 7,570 | 231 KB | 2.02 s | 19.14 s |
| 400 | 11,647 | 356 KB | 3.22 s | 51.96 s |
| 1000 | 28,634 | 874 KB | 10.03 s | **TIMEOUT > 240 s** |
| 4000 | **113,572** | **3.5 MB** | 152.64 s | **TIMEOUT > 240 s** |

Two things to read off this table.

**The N=4000 row is the D45 incident, reproduced.** The plan row records
113,545 lines / 3.5 MB; this lane measures 113,572 lines / 3,536,883 bytes at
commit 0a082ea — a delta of 27 lines, 0.02%, on a compiler that has taken
several landings since the row was written. The cause of the 27 lines was not
chased; the point of the row is that the order of magnitude and the shape both
reproduce.

**gcc's cost is linear at −O1 and quadratic at −O2.** −O1 tracks N closely
(0.52 → 1.01 → 2.02 → 3.22 across 64/128/256/400 — the first two intervals
double, the third is ×1.56 against a ×1.56 step in N, so "doubles" was the
wrong word for a claim that is really "exponent 1"; a regression over the
whole sweep gives **0.99**). −O2 goes ×3.1, ×4.1, ×2.7 over the same steps,
i.e. an exponent of about 2. `limits.h`'s
recorded curve (0.50 / 1.40 at N=64, 3.50 / 51.54 at N=400) is reproduced to
within the noise of a different machine. This is the whole justification for
`PCREC_MAX_VM_REPEAT_COPIES = 64` and it survives re-measurement.

### 1.3 The interim backstop, and what it refuses

`PCREC_MAX_VM_REPEAT_COPIES = 64` is checked in the pre-pass, BEFORE emission,
against `v.maxcopies` — the largest replication factor any one bounded repeat
over a choice-bearing body demands. Its diagnostic already names the fix
("remove the alternation so the body compiles to a span loop instead"). This
note does not propose removing it; §7 proposes what it should say once there
is somewhere better to point.

The cap is on REPLICATION and not on total size, and that is right: MEASURED,
a 200-branch capture-bearing keyword alternation has 199 resume points and
compiles in 0.50 s, while `((a)|b){0,4000}c` is sixteen characters and 3.5 MB.
The defect is DISPROPORTION.

### 1.4 The compiler's OWN cost — the third amendment, checked

The third amendment as corrected carries consequence (b): the replication
reduction "also shrinks pcrec's own DFA-construction work, an additional
measured motivation for this row." This lane measured that and **it does not
hold as stated**, for a structural reason.

MEASURED (`outputs/nfa_growth.txt`), NFA states for `((a)|b){0,N}c`, from a
scratch compiler with one `fprintf` at the end of `pcrec_build_nfa`:

| N | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 1000 | 4000 |
|---|---|---|---|---|---|---|---|---|---|---|
| NFA states (each direction) | 15 | 27 | 51 | 99 | 195 | 387 | 771 | 1,539 | 6,003 | 24,003 |

Exactly `6N + 3`, linear, and it is produced by `src/ir/nfa.c`'s own
replication loop. **Nothing `emit_vm.c` does changes this number** — the VM
emitter and the NFA lowering replicate independently from the same AST. An
emitter-side counter-K therefore shrinks the emitted C and leaves pcrec's own
machine construction exactly where it was. So does possessification, which
rewrites the quantifier's STRATEGY and not the AST's repeat count.

What the measurement did turn up is worth more than the claim it refutes.
MEASURED (`outputs/erased_path_cost.txt`), the capture-ERASED path — the one
the plan row holds up as cheap:

| N | pcrec's own time | gcc −O2 | emitted lines |
|---|---|---|---|
| 64 | 0.012 s | 0.060 s | 148 |
| 256 | 0.025 s | 0.073 s | 208 |
| 1000 | 0.181 s | 0.082 s | 440 |
| 2000 | 0.656 s | 0.088 s | 753 |
| 4000 | **2.689 s** | 0.098 s | 1,378 |

The 1,378 lines reproduce the plan row's figure EXACTLY. The 0.078 s does
not: at N=4000 the artifact takes **2.7 seconds of pcrec's own time** and
0.098 s of gcc's. (0.078 s is very close to this lane's gcc-only figure at
N=1000, so the plan row's number is most likely a gcc time recorded as a
total. Reported, not adjudicated.)

STRUCTURAL, and the mechanism is visible in the emitted artifact: at every N,
the FORWARD DFA is **2 states** (`rx_ftr[8]`), and the whole count lives in
the REVERSE machine — `rx_racc[66]` / `rx_rtr[264]` at N=64, `rx_racc[4002]` /
`rx_rtr[16008]` at N=4000. Subset construction builds Θ(N) reverse states,
each closing over a Θ(N) NFA, which is where the quadratic comes from.

**The consequence that survives, restated so a budget can be posed on it:** any
depth- or size-shaped budget in the compiler must be posed on the UNROLLED
quantity. The surviving evidence is this table plus the NFA row above — a
pattern whose reader-visible nesting never moves produces 24,003 NFA states
and 4,002 reverse DFA states — not the refuted depth-multiplication claim. And
the erased path has its own ceiling that nobody wrote down:
`PCREC_MAX_DFA_STATES_TABLE = 32000` caps this shape at roughly N = 32,000.

---

## 2. Question 1 — POSSESSIFY: which bounded repeats need no backtracking at all

### 2.1 The claim

For a large and precisely-characterisable class of quantifiers, NO retreat
into the loop can ever produce a match the PREFERRED path does not. For those,
the emitter owes zero resume frames, zero trail entries and no counter — the
loop is a forward scan. This is the cheapest rung and it must be tried first,
which is why Frank ruled it question 1.

"Preferred path" rather than "maximal path" is deliberate [R24 S-F1]: for a
greedy quantifier the preferred path IS the maximal one, but a lazy
quantifier prefers the minimum, and the class of quantifiers that owe zero
frames is correspondingly narrower for lazy than for greedy. §2.2's rule
carries the difference as an explicit conjunct and §2.3 shows the witness
that forced it. A reader who takes "zero resume frames" from this section
alone and applies it to a lazy quantifier on the disjointness arm will emit a
wrong span on a measured family.

### 2.2 The analysis, stated precisely

Let `Q = X{m,n}` be a quantifier occurrence in a pattern. Define, over bytes:

- **FIRST(X)** — the set of bytes that can begin one iteration of `X`.
- **FOLLOW(Q)** — the set of bytes that can begin whatever runs after `Q`,
  computed transitively: the first set of `Q`'s remaining siblings, extended
  outward past nullable siblings to the enclosing constructs, and INCLUDING
  FIRST(B) for the body `B` of every enclosing loop (an enclosing loop can
  start another iteration once `Q`'s parent finishes).

Say `X` **admits a unique iteration** when both hold on `X`'s position
(Glushkov) automaton:

- **(U1) one-unambiguous** — the initial position set is pairwise byte-disjoint
  and every position's follow set is pairwise byte-disjoint. Equivalently: at
  most one position is live after any prefix. This is Brüggemann-Klein &
  Wood's 1-unambiguity, and it is exactly what "per-byte-disjoint branches"
  means once it is stated for the whole body rather than for a top-level
  alternation.
- **(U2) prefix-free** — no ACCEPTING position has an outgoing edge. No proper
  prefix of an iteration is itself a complete iteration.

**THE RULE** (the lazy conjunct added at [R24 S-F1]). `Q` is
possessive-equivalent when

> `X` admits a unique iteration, `X` is not nullable, and **either**
>
> - `m == n` — the EXACT-COUNT arm, which holds for either preference; **or**
> - FIRST(X) ∩ FOLLOW(Q) = ∅ — the DISJOINTNESS arm, which holds
>   unconditionally for a GREEDY `Q`, and for a LAZY `Q` only when the match
>   cannot also END at the quantifier (everything after `Q`, out to the end of
>   the pattern, is non-nullable).

Four notes on the shape of that rule.

- **The lazy conjunct is not decoration; without it the arm is unsound.**
  MEASURED: 316 counterexamples, e.g. `a{1,3}?` on `"aaaa"` is `(0,1)` lazy
  and `(0,3)` possessive. §2.3 and §2.4.

- **The exact-count arm is free and it is not in the plan row.** With a
  unique-iteration body there is exactly one way to run `k` iterations from a
  given start, so the loop's ONLY freedom is `k`; `m == n` removes it without
  any reference to what follows. MEASURED, it is not a curiosity: it is 52 of
  the 76 possessifiable verdicts on the realistic pattern set (§2.6), because
  real bounded repeats are `\d{4}`, `[0-9a-f]{8}`, `\d{2}` — exact counts over
  classes.
- **Every set is computed in the SOUND direction.** A construct the analysis
  cannot model widens to "all bytes", which makes the disjointness test fail
  and the quantifier keep its machinery. Declining is always available.
- **The condition is on the QUANTIFIER, not the pattern.** D46 already
  established the rung as a per-`A_REP` property with a per-quantifier stamp;
  this joins that family.

### 2.3 Why it is sound

STRUCTURAL, given (U1)+(U2)+non-nullable:

1. From any start position `p`, at most one iteration of `X` can run, and it
   has exactly one end. (U1) makes the position path deterministic; (U2) stops
   it at the first accepting position, which is therefore the only one.
2. So the loop's reachable exit positions from `p` form a strictly increasing
   chain `p = q₀ < q₁ < q₂ < …`, with `q_{i+1}` determined by `q_i`. Strict
   because non-nullable.
3. The greedy path takes the largest `k` in `[m, n]` for which `q_k` exists —
   it reaches the top of the chain. (A lazy quantifier walks the same chain
   from the bottom; see below.)
4. For any non-maximal exit `q_i`, another iteration ran from `q_i`, so
   `subject[q_i] ∈ FIRST(X)`.
5. FIRST(X) ∩ FOLLOW(Q) = ∅ therefore says the follow's first byte test fails
   at every non-maximal exit. No retreat can succeed. ∎ (In the `m == n` arm,
   step 3 leaves one exit and steps 4–5 are unnecessary.)

**Where each premise is load-bearing, with its witness.** Step 2 is where the
plan row's version breaks: without (U1), a "retreat" can move the exit
position RIGHT rather than left, because re-choosing inside the body changes
the iteration's LENGTH. Without (U2), the same happens without any alternation
at all. Both are measured witnesses, not hypotheticals — §2.4.

**Lazy quantifiers — the argument above is GREEDY-ONLY, and the first version
of this note got that wrong [R24 S-F1, REFUTED].** Step 3 is where preference
enters, and the original paragraph waved it away: steps 1–2 do not mention
preference, so the chain is the same, and it concluded that greedy, lazy and
possessive therefore agree on the span. They do not.

The hole is in step 5. "The follow's first-byte test fails at every
non-maximal exit" is VACUOUSLY TRUE when the follow can match empty and the
match can end at the quantifier — there is no first byte to test. A greedy
loop is unharmed by that: it tops out at the chain's top (step 3), and the
vacuous follow succeeds there just as it would anywhere, so greedy and
possessive still agree. **A lazy loop stops at the BOTTOM of the chain**, where
the same vacuous follow also succeeds — and reports a shorter span than the
possessive form. MEASURED, `a{1,3}?` on `"aaaa"`:

| form | span |
|---|---|
| `a{1,3}?` (lazy) | `(0,1)` |
| `a{1,3}+` (possessive) | `(0,3)` |

so the loop's exits are not interchangeable and the emitter cannot drop the
machinery. This is why the rule in §2.2 carries a lazy-only conjunct: on the
disjointness arm a lazy `Q` additionally requires that the match cannot end at
the quantifier — everything after `Q`, propagated outward to the end of the
pattern, must be non-nullable. With that conjunct the differential is clean in
both preference families (§2.4).

**The EXACT-COUNT arm is preference-independent and needs no conjunct.** There
is one exit, so top and bottom of the chain are the same position and step 3
is vacuous rather than the follow test being vacuous. MEASURED at 0
counterexamples for lazy as well as greedy, which is also why this arm carried
the largest share of the realistic census (§2.6) through the refutation
unchanged.

**Why this lane could not see it.** `probe_possess.py` built a possessive
respelling of each generated pattern to compare against, and a lazy quantifier
has no possessive spelling — `X{m,n}?+` is not a thing. So the probe's helper
returned `None` for every lazy row and the whole preference family was
silently absent from a differential the note described as covering the design.
The repair is to compare a LAZY pattern against the POSSESSIVE form of the
same base count (`X{m,n}?` vs `X{m,n}+`), which is a valid pair and is what
§2.4's second family now does. §10 records this as the lane's own
instrumentation defect, because it is one.

### 2.4 The differentials that refuted the first two versions

`probes/probe_possess.py` states the analysis as code and checks it against an
oracle in both directions over a generated family (3 prefixes × 12 bodies ×
8 base counts × 19 follows, each base count spelled BOTH ways — `X{m,n}`
against `X{m,n}+` and `X{m,n}?` against `X{m,n}+` — for **8,032 compiling
pairs**, 260 subjects each, about 2.1 M pattern-subject comparisons). The
oracle is python3 `re`, whose possessive quantifiers are the mechanised
statement of "no retreat into this loop"; this is a BASE-TIER oracle, not the
three-way sweep §5.3 specifies. **The lazy half of that family did not exist
before [R24]** — see §2.3's closing paragraph and §10.

One caveat on the oracle, measured by the R24 panel and recorded in
`docs/dev/upstream_issues.md` U9: python-possessive and PCRE2-possessive are
**not interchangeable**. PCRE2 10.46 does not backtrack into a PRECEDING item
after a possessive bounded repeat of a GROUP (`a?(?:b){0,4}+a` on `"a"`:
PCRE2 reports no match, python and the correct answer are `(0,1)`), and that
shape sits inside exactly the family swept here. It does not touch any verdict
below — the divergence is on the possessive SIDE of the comparison, not on the
analysis — but it is the measured reason §5.1's pcrec-vs-pcrec differential is
the primary instrument and an oracle is the ride-along.

Two directions, because they are different questions:

- **SOUNDNESS** — every quantifier called possessive-equivalent must behave
  identically greedy and possessive on every subject. One counterexample
  refutes the design.
- **NON-VACUITY** — the analysis must also say no to things, and those noes
  must be where the divergences are. An analysis that says yes to nothing is
  sound and worthless.

**v1, disjointness alone** (`outputs/possess_differential_v1_REFUTED.summary`):

| verdict | differential same | differential DIVERGES |
|---|---|---|
| possessifiable | 1,395 | **117** |
| no | 619 | 773 |

All 117 counterexamples are one body, `(a|ab)`. The witness:
`(a|ab){0,4}c` on `"abc"` is `(0,3)` greedy with group 1 = `"ab"`, and `(2,3)`
possessive with group 1 unset. FIRST is `{a}`, FOLLOW is `{c}`, disjoint — and
the analysis was still wrong, because the greedy path takes `a`, stalls at
offset 1, and the retreat re-decides the SAME iteration as `ab`, moving the
exit from 1 to 2. Step 2 of §2.3 is exactly the premise that fails.

A second witness, found by direct probe rather than by the sweep, needs no
alternation at all: `(?:ab?){0,4}b` on `"ab"` is `(0,2)` greedy and no match
possessive. The body is one-unambiguous; its accepting position `a` (with `b?`
empty) simply has an outgoing edge. That is (U2).

**v2, the rule of §2.2 without the lazy conjunct — GREEDY ONLY**, with the
assertion follows of §2.5 and three follows added that the v1 family lacked:

| verdict | differential same | differential DIVERGES |
|---|---|---|
| possessifiable | 2,031 | **0** |
| no | 1,522 | 1,463 |

0 counterexamples to soundness, and 1,463 divergences among the noes, so the
analysis is not vacuous. Note the population GREW (1,395 → 2,031) while
getting sound, which is the exact-count arm paying for itself.

**And v2 is where the note stopped, which is why R24 found a third defect.**
Running the same rule over the LAZY spelling of the same family
(`outputs/possess_differential_lazy_control.summary`, the probe's
`BREP_NO_LAZY_CONJUNCT=1` mode):

| lazy, no conjunct | differential same | differential DIVERGES |
|---|---|---|
| possessifiable | 1,715 | **316** |
| no | 1,318 | 1,667 |

316 counterexamples — and this lane's 316 is the same number the panel reached
independently on its own instrument, which is the strongest form of agreement
two measurements of one defect can have.

**v3, with the lazy conjunct** (`outputs/possess_differential.summary`), both
preference families in one run:

| preference | verdict | differential same | differential DIVERGES |
|---|---|---|---|
| greedy | possessifiable | 2,031 | **0** |
| greedy | no | 1,522 | 1,463 |
| lazy | possessifiable | 1,695 | **0** |
| lazy | no | 1,338 | 1,983 |

**The `no` row's same/DIVERGES split above is the PRE-D47.6 figure, kept for
history** (see the corrected bullet below for why); the possessifiable rows
are exact and unaffected. Re-run with the fixed subject generator, the split
moves to greedy `no` 1,320/1,665 and lazy `no` 1,154/2,167 — the possessifiable
rows are byte-identical (2,031/0 and 1,695/0) because that population never
depended on the missing subjects; only how many of the ALREADY-DECLINED `no`
cells the differential could see diverging changed. Current archive:
`outputs/possess_differential.summary`.

Three things to read off this, none of them automatic:

- **The greedy rows are byte-identical to v2's** (2,031 / 1,522 / 1,463). The
  conjunct is scoped to lazy and provably did not disturb the family that was
  already clean — which a restructuring this size could easily have done
  silently.
- **The conjunct is what removes the 316**, not something else that changed
  underneath: the control above is the same binary with one flag flipped, and
  it is committed so the control can be re-run rather than believed.
- **It costs ZERO false declines — corrected 2026-08-16 (D47.6).** This
  bullet originally read "It costs 20 false declines (1,715 → 1,695
  possessifiable-and-same)". Pulling those 20 for Frank's inspection refuted
  the claim: all 20 GENUINELY diverge lazy-vs-possessive (e.g. `za{1,3}?` on
  "zaa": lazy `(0,2)`, possessified `(0,3)`) on subjects
  `probe_possess.py`'s `subjects()` could not produce — its random alphabet
  was `"abcd "`, which never contained the prefix byte `z` that every
  non-empty `PREFIXES` member is built from, so every z-prefixed pattern in
  exactly this cost bucket was swept without the depth to even enter its own
  loop. Fixed in the same ruling (`z` joins the alphabet, plus deterministic
  repetition-heavy subjects — see the probe's own docstring). Re-swept over
  the full 3,726-row possessifiable population (both preferences): 0
  counterexamples, and the 336 lazy+nullable-rest `no` cells that used to
  include those 20 "same" rows now show 0 same / 336 DIVERGES. The lazy
  possessifiable population is still 1,695 against greedy's 2,031: laziness
  still costs about 17% of the class, all of it the nullable-rest tail — but
  the conjunct itself, which is what this bullet is about, costs nothing
  measurable. See D47 ruling 6 and §10.1's new entry.

**One thing v1 got right by accident, disclosed.** v1's follow set contained
no follow beginning with a body's SECOND byte, so the `(?:ab|a)` family — just
as ambiguous as `(a|ab)` — passed v1's differential clean. v2 adds `b`, `ab`
and `bc` as follows. A family that passes because the harness never asked the
question is the failure mode `pcrec-check-design-lessons` is about, and it
happened here.

### 2.5 The third refutation: assertions in the follow

MEASURED. Modelling a zero-width assertion as "not in the follow, because it
consumes nothing" is unsound:

| pattern | greedy | possessive |
|---|---|---|
| `[ab]{0,4}\b` on `"abc"` | `(0,0)` | `(3,3)` |
| `(?:a\|bc){0,4}\b` on `"ab"` | `(0,0)` | `(2,2)` |
| `a{0,4}\B` on `"ba"` | `(1,1)` | no match |

`\b` at a retreat position can succeed where it fails at the maximal exit,
which is precisely the thing a first-BYTE set cannot express. **The rule:** an
assertion reachable at the follow's first position widens FOLLOW to all bytes,
i.e. the analysis declines. Sound, one line.

**`$` is the exception, and it is now MEASURED-WITH-GATE rather than a
conservatism [R24 S-F2].** This note originally declined `$` with the rest and
filed "is `$` separately safe?" as its highest-value follow-up; the panel
answered it. `$` in the follow IS safe — **0 of 720 diverging cells** — and
the argument is an upward-closure one: `$` is true only at the subject end
(and before a final newline), which no retreat can reach from a position
further left, so a retreat position that satisfies `$` cannot exist below the
maximal exit.

**But only while MULTILINE is off.** Under `(?m)`, `$` is true before EVERY
newline, the upward-closure argument collapses per-line, and the same sweep
gives **180 of 720 diverging**. So the exemption is conditional and the
condition must be a LIVE CHECK in the implementation — a test on the pattern's
actual multiline state at analysis time, not a comment saying pcrec does not
support `(?m)` yet. pcrec refuses `(?m)` today (module `assertions`), which is
what makes the exemption safe NOW and is exactly the kind of fact that stops
being true without anyone revisiting this note.

The 0 is not inert: on the same instrument `\b`/`\B` follows give 332 of 720
diverging and `^` gives 80 of 240, so the sweep can and does find divergence
where divergence exists.

### 2.6 What it covers — two censuses, and they disagree by more than four times

`probes/probe_possess_corpus.py` runs the same analysis (imported, not copied,
so a refutation moves both numbers at once) over two populations.

**The .rxt corpus** — 756 harvested patterns, 1,725 quantifiers, 112 patterns
python3 `re` cannot parse and which are reported rather than dropped:

| | possessifiable | no | rate |
|---|---|---|---|
| bounded | 51 | 250 | **17%** |
| unbounded | 123 | 1,301 | 9% |

**A realistic set** — `probes/realistic_patterns.txt`, 40 patterns of the kind
bounded repeats actually appear in (dates, UUIDs, IPs, MACs, fixed-width
fields, versions, log lines):

| | possessifiable | no | rate |
|---|---|---|---|
| bounded | 69 | 15 | **82%** |
| unbounded | 7 | 15 | 32% |

**These figures moved at [R24 S-F1]**, because the lazy conjunct declines
quantifiers the old rule admitted. Nine corpus quantifiers changed verdict —
4 bounded (55 → 51) and 5 unbounded (128 → 123) — every one of them
lazy + disjointness-arm + nullable-remainder, which is exactly the class §2.3's
refutation identifies. The realistic set did NOT move at all: it contains no
lazy quantifier, so 69/84 stands unchanged. (The panel's own blast-radius
estimate was 10 quantifiers where the committed script measures 9; the
one-cell difference is not explained here, and the script's number is the one
quoted because it can be re-run.)

**The gap is the finding.** The .rxt corpus is a COMPILER test corpus,
adversarial by construction — its bounded repeats were chosen to break things,
so a possessification rate measured on it says nothing about the population the
feature is for. On patterns people write, four bounded repeats in five need no
backtracking machinery at all, against roughly one in six on the corpus. Both denominators are reported because either
one alone would mislead: the first understates the win, the second is a
hand-written list and says so in its own header.

Reasons, realistic set: 52 exact-count + unique-iteration, 24
disjoint + unique-iteration, 27 overlap, 3 not-prefix-free. The exact-count
arm carries 52 of the 76 — which is also why the realistic figure survived a
refutation that moved the corpus figure: the arm the refutation did not touch
is the arm real patterns use.

### 2.7 Conservatism, named rather than smoothed over

1,522 "no" verdicts never diverged in the differential — the analysis is
sound, not tight. (This is the greedy `no`/same count from §2.4's v3 table,
pre-D47.6; the fixed subject generator moves it to 1,320 — same table, same
caveat.) The identified sources, in order of how much they cost:

- **`$` follows** (`a{0,4}$`, `\d{2,4}$`): declined by §2.5's blanket
  assertion rule, and — as of [R24 S-F2] — **recoverable**, because `$` is
  measured safe with a live `!multiline` gate. This was the largest single
  source of conservatism in the greedy family and the implementation lane
  should take it; §2.5 states the gate.
- **Subsumed follows** (`[ab]{0,4}b?c`): FOLLOW contains `b` because of the
  `b?`, but a `b` at any retreat position was already consumable by the loop,
  so the retreat cannot help. PCRE2's `pcre2_auto_possess.c` does exactly this
  kind of subsumption reasoning; pcrec's first version should not.
- **The lazy conjunct's own cost** [R24 S-F1] — **corrected 2026-08-16
  (D47.6): ZERO, not 20.** This bullet originally read "20 quantifiers the
  greedy rule admits are declined in the lazy spelling without the
  differential showing a divergence" and attributed that as the price of
  stating the conjunct on "the rest is nullable" rather than the sharper
  "some non-maximal exit actually succeeds". The 20 were pulled for
  inspection and all genuinely diverge — see the §2.4 correction and D47
  ruling 6 for the full account (the instrument's subject alphabet, not the
  conjunct, was at fault). The conjunct is stated on the coarser condition
  because it is one predicate and provably sound, which remains the right
  trade for a first version, but it is not buying that soundness with any
  measured cost.
- **`\d`, `\w` and every other CATEGORY** widen to all bytes in the probe's
  model. In pcrec they would not — the real implementation has exact 256-bit
  class bitmaps and can intersect them precisely, so the shipped analysis
  should be STRICTLY less conservative here for CATEGORIES than the probe that
  validated it.

  **This is a claim about categories only, and the original wording
  over-generalised it** [R24 S-F4]. "The probe is wrong in the right
  direction" is NOT a blanket property: the probe's IGNORECASE handling is
  unsound in the OTHER direction, because python folds case at compile time,
  so the probe computes FIRST(`(?i)a`) = `{a}` and misses `A`. A porting lane
  that inherited the probe's model along with its conclusions would inherit
  that hole.

  **pcrec itself is safe here STRUCTURALLY, for a reason worth writing down:**
  `src/parse/parse.c`'s `cls_casefold` folds case into every `A_CLASS` bitmap
  at PARSE time, and every literal in pcrec is an `A_CLASS` — so by the time
  any analysis sees the AST, a caseless `a` already has both `a` and `A` in
  its bitmap and the byte-set model is exact rather than approximate. The
  probe's defect is a property of python's parse tree, not of the design.
  Census impact was one harmless row; the census figures survive it.

### 2.8 Delivery seam: §5.2's socket, and why the socket and not the emitter

§5.2 rules that the future customers of engine selection "are not analyses
that return a verdict, they are REWRITES that discharge a verdict", and gives
them a `discharge` hook in a fixpoint pass. Possessification is exactly that
shape: it does not observe that the loop needs no frames, it MAKES the
quantifier one that needs none.

The registration is an `EngineAnalysis` row owned by the core (unlike
`backrefs` or `atomic_groups`, possessification is not a module's construct —
it is an optimisation over the base tier), whose `discharge` rewrites the
`A_REP` node's strategy in place. Two properties this inherits for free:

- **The fixpoint bound already exists.** §5.2 requires the pass to be bounded
  from day one so a later rewrite pair cannot loop. Possessification is
  monotone (a possessified quantifier is never re-examined) so it terminates
  in one pass, but it does not have to argue that separately.
- **The size-estimate obligation does not bind.** §5.2's rewrite author owes a
  size estimate before committing, because the archetypal rewrite (finite
  backref expansion) makes the AST BIGGER. This one only ever removes
  machinery.

**What the socket does NOT buy, stated because §0.2 item 4 is about it.** The
rewrite lands on the AST, but `src/ir/nfa.c` lowers `A_REP` by replication
regardless of any strategy annotation, so the prefilter's NFA is unchanged.
Possessification is a run-time and emitted-size win, not a compiler-time one.
Making it a compiler-time win would mean teaching the NFA lowering an atomic
construction, which is a different row and is not proposed here.

### 2.9 Prior art: `pcre2_auto_possess.c`

PCRE2 performs auto-possessification at compile time in
`pcre2_auto_possess.c`, comparing the repeated item's character set against
what can follow it and rewriting the opcode to its possessive form when they
cannot overlap. It is cited here as **prior art that the transformation is
real and safe in a production engine**, not as a specification: D26 makes
PCRE2 the source of truth for what a pattern MATCHES, and possessification by
construction changes no match. pcrec's own analysis must therefore be
justified on its own terms — which §2.3 does and §2.4 checks — and any place
the two engines possessify different sets is not a compatibility defect,
because both compute the same answers.

**Where this note's rule and pcrec's own prior design disagree** [R24 C-F1].
`engine_m4.md` §6.3 names disjoint-follow possessification as "the one real
piece of new analysis M4.6 owes" and states it in exactly the form §2.4
measured unsound; §6.4's status table calls it "designed, built M4.6". Both
are now annotated in place to point here, and §2.5's `z(ab)*y` example is
annotated as surviving (its body is non-nullable and admits a unique
iteration, so the repaired rule admits it too). The DELIVERY seam that
document specifies — §5.2's `discharge` hook, §2.8 above — is unaffected; what
changed is only that the analysis behind the hook is bigger than a first-set
comparison.

Two differences worth recording so a later reader does not assume parity.
PCRE2's analysis works on compiled opcodes and handles a fixed repertoire of
item shapes; the one proposed here works on the AST before lowering and keys
on a whole-body automaton property, so it reaches multi-byte bodies like
`(?:a|bc)` that an item-wise comparison does not. In the other direction,
PCRE2 does subsumption reasoning this note explicitly defers (§2.7).

---

## 3. Question 2 — RUNG SELECTION: which residual bodies each rung catches

### 3.1 The ladder, as designed and as built

§2.5's ladder, cheapest first: disjoint follow → fixed stride → reverse
deterministic → boundary record → frames + stamped ceiling. [M4.5b] landed 2
of the 5 rungs. What exists in `emit_vm.c` today is a two-way choice made per
`A_REP` by `vm_cursor_fits` — a deterministic FIXED-LENGTH body (via
`vm_det_seq`, plus D44.1's capture-offset extension) takes the span-loop
cursor; everything else falls through to frames, bounded or unbounded. D46
stamps the choice per quantifier and `--emit-ir` reports it.

**A naming note, because this note and `engine_m4.md` count rungs
differently** [R24 C-F3]. `--emit-ir` stamps the three values `cursor`,
`frames-bounded` and `frames-unbounded`, and the census below is keyed on
those stamps — so "cursor" here is an EMITTED-STRATEGY name, not a ladder
position. In §2.5's own hierarchy the cursor is the fixed-stride rung (the
single-byte body is just its stride-1 case), and `cursor` as emitted today
covers fixed-stride and nothing below it. Where this note says "the cursor
rung" it means the stamp; where it discusses the ladder it uses §2.5's names.

### 3.2 The census: what the rungs catch today

`probes/probe_rungs.py` reads the rung out of the emitter's OWN listing
(`--emit-ir`'s RUNGS section, written by the same walk that writes the C, so
it cannot drift from what is emitted). Over the 756 harvested patterns, with
`--engine=vm` forced so every pattern reaches the VM
(`outputs/rung_census_forcedvm.tsv`):

**Every figure in this section is now produced by `probes/census_rungs.py`,
which is committed and reads the archived census files.** The first version
computed them in an uncommitted shell pipeline; two of the three columns were
wrong and none could be re-derived. See the end of this section for what went
wrong, and §10.

| rung | emitted stamps | distinct (pattern, rung, detail) | distinct patterns |
|---|---|---|---|
| cursor | 1,402 | 398 | 349 |
| frames-unbounded | 1,234 | 191 | 188 |
| frames-bounded | 236 | 148 | 140 |

The middle column is a LOWER BOUND on distinct source quantifiers, and the
script says so where it computes it: `detail` is the emitter's role text
(`"frames rung, bounded {0,4}, greedy"`), so two copies of one source
quantifier collapse — which is the point — but so do two genuinely different
quantifiers with the same bounds and preference. The emitted `label` cannot be
used instead: replication assigns a fresh label per copy, which is the very
inflation the column exists to see past.

**Read the columns together, not one.** The stamp count is what the EMITTER
sees and the distinct counts are closer to what the AUTHOR wrote. Across the
table stamps exceed distinct triples by **3.9×** (2,872 against 737), and on
the cursor row by 3.5× — replication multiplying the quantifiers the emitter
handles. The sharpest single cell: one 60-character corpus pattern,
`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}`, contributes
**352 rung stamps**. Its source has **7** distinct quantifier shapes in all,
of which **3** are on the frames-bounded rung; the original text said "three
source quantifiers" without that narrowing and so understated the pattern's
own complexity while overstating the inflation ratio. Either way the point
stands and is the third amendment's surviving consequence (a) — budgets go on
the unrolled quantity — observed on a second, independent quantity.

Under DEFAULT engine selection (`outputs/rung_census_default.tsv`) the picture
is smaller: 613 of 756 patterns request no captures and never reach the VM at
all, and **15** distinct patterns put a quantifier on the frames-bounded rung
(822 / 164 / 75 stamps across cursor / frames-unbounded / frames-bounded).
**The population this row is about is small and the compiler already knows how
to identify it** — which is the argument for solving it well rather than
cheaply.

**What went wrong the first time, because the cause is reusable** [R24
M-F1/M-F2]. The original numbers came from a pipeline ending in
`sort -u`, run under `LANG=en_US.UTF-8`. That locale's collation treats
strings differing only in punctuation as EQUAL, so `sort -u` silently merged
distinct patterns:

```
$ printf '%s\n' '\d+' '[\d]+' | sort -u | wc -l
1
$ printf '%s\n' '\d+' '[\d]+' | LC_ALL=C sort -u | wc -l
2
```

Every "distinct" figure from that pipeline was therefore an UNDERCOUNT — 11
instead of 15, 311/111/96 instead of 398/191/148 — while the stamp tallies,
which never passed through `sort -u`, were right. The panel found the wrong
number and found the column unreproducible; this is why. A regex test corpus
is close to a worst case for locale collation, since its patterns differ
mostly in punctuation. The replacement script counts in python with exact
string equality and never shells out.

(The stamp total also moves by 2, from 1,404 to 1,402 cursor: two corpus
patterns contain a literal tab, which shifts the fields of a TSV row. The
census script drops rows without exactly five fields rather than
misattributing them, and reports the count so the loss is visible.)

### 3.3 The motivating cell, reproduced

N = 4000, three ways. **Every cell below comes from ONE serial run of
`probes/probe_cell33.sh`** (`outputs/cell33_motivating_cell.txt`), with the
`engine` column read out of `--emit-ir`'s own header per row so that no row
can claim a rung the compiler did not take:

| | pattern | engine | emitted lines | pcrec | gcc −O2 |
|---|---|---|---|---|---|
| replicated | `((a)\|b){0,4000}c` | vm | 113,549 | 2.72 s | **> 300 s (timeout)** |
| capture-ERASED (`--no-captures`) | `((a)\|b){0,4000}c` | dfa | 1,378 | 2.62 s | 0.118 s |
| span-loop cursor | `(ab){0,4000}y` | vm | 2,822 | 1.62 s | 0.219 s |

The erasure cell is real and it is an **82× reduction in emitted lines**. §1.4
corrects what it costs — the cost moves from gcc to pcrec rather than
vanishing. Row 3 is the point of §2's whole argument in miniature: a body with
no choice point never replicates in the emitter, which is why `a{0,65535}` and
`(?:ab){0,9999}` have never been a problem and why the cap's diagnostic
already names "remove the alternation" as the fix.

**Two things about this table were wrong before [R24 M-F4]**, and both are
worth stating because they are ordinary rather than exotic.

Its three rows came from three different places — a line count from one
archived file, a pcrec time from an unarchived transcript, a gcc time from a
sweep run under load. Mixing sources inside one table is how a table stops
being a measurement and starts being an assembly.

And row 3 used `(?:ab){0,4000}y`, which is NON-CAPTURING. A pattern with no
capturing group requests no captures, so it never reaches the VM at all — the
row labelled "cursor rung" was measuring the DFA, the same engine as row 2.
The body is `(ab)` here, and `--emit-ir` confirms `engine vm` / `rungs cursor`
before the row is timed. (This one the panel did not catch; it surfaced on
re-measurement, which is the argument for re-measuring rather than
re-sourcing.)

Line counts differ slightly from §1.2's table (113,549 here against 113,572
there) because that sweep passed `--emit-main` and this one does not. Same
compiler, same pattern, different artifact shape — stated so the two tables do
not read as a contradiction.

### 3.4 The reverse-deterministic rung, and what it can and cannot derive

PCRE2 reports only the LAST iteration's captures, so the 3,999 other capture
writes a replicated `((a)|b){0,4000}c` performs are unobservable by
definition. The rung's promise is that the DFA pair delivers the exact span
and the last-iteration captures are recovered by walking the REVERSED body
automaton backward from the end — O(1) memory, no trail.

**The plan row's worked derivation for this cell is wrong, and the way it is
wrong is instructive.** As stated: group 1 = `[end−2, end−1)`, group 2 = the
same iff `subject[end−2] == 'a'`. MEASURED over 15,036 matches
(`outputs/lastiter_capture_derivation.txt`): **1,799 mismatches.** Group 1 is
right. Group 2 is not, because a group INSIDE a loop keeps the value from the
last iteration that entered it — a later `b` iteration does not clear it —
so on `"abc"` group 2 is `(0,1)`, not unset.

The corrected derivation, **0 mismatches over the same 15,036**, in two
clauses:

- **Zero iterations** (the span is just the `c`, i.e. `end − start == 1`):
  BOTH groups are unset. There is no iteration to have written them.
- **One or more iterations:** group 1 = `[end−2, end−1)`; group 2 =
  `[p, p+1)` where `p` is the last `a` in `[start, end−1)`, unset if there is
  none.

**The zero-iteration clause is not a footnote and the first version of this
note dropped it** [R24 S-F3]. The archived probe always had it — its own
output records 6,259 zero-iteration matches out of 15,036, **42% of the
validated population**, at 0 mismatches — but the write-up stated only the
second clause, whose `[end−2, end−1)` is meaningless when the loop never ran.
An implementation lane building the reverse-deterministic rung from the prose
alone would emit a wrong group on 42% of the motivating cell's own matches.
Recorded here rather than quietly patched because the failure mode — a
validated derivation losing a clause on the way into prose — is one a reader
should expect to look for elsewhere in this note.

Bonus, from the same re-check: with the zero-iteration clause stated, the
derivation is also 0-mismatch on `m > 0` shapes, where the clause is
unreachable by construction.

That repair is the rung's own argument, sharpened. A constant-offset formula
was never the right shape; what recovers group 2 is a BACKWARD SCAN that
continues until it finds the last iteration which took the branch the group
lives in. That is a reversed-automaton walk — exactly what §2.5's
reverse-deterministic rung is — and its cost is bounded by the loop's span,
not by O(1), which the rung's "O(1) per retreat" phrasing should be read
against.

**What the rung cannot do**, stated so the ladder's residual is honest:

- **Reverse-ambiguous bodies stay on the frames rung.** §2.5's own
  counterexample, `(aa?)*` on `"aaa"`, is undiminished: the rightmost byte
  cannot say which iteration ended there.
- **A group whose branch is never taken has no backward witness to find**, and
  the scan must still be bounded by the loop's start. The derivation above
  terminates because the loop's span is known; a rung that did not have the
  span first could not do this at all — which is why this rung sits behind the
  DFA pair and not in front of it.
- **Nested loops multiply the walk.** The derivation above is single-level. A
  capture inside a nested bounded repeat needs the enclosing iteration's
  boundary first. Not designed here; §8.

### 3.5 The residual

After questions 1 and 2, what is left for question 3 is: a bounded repeat over
a body that is NOT possessive-equivalent (its follow overlaps its first set,
or its iteration is ambiguous), and NOT deterministic enough for any cursor
rung, and whose per-iteration backtracking is therefore real. `((a)|b){0,N}c`
with `c` replaced by something starting with `a` or `b` is the archetype. On
the realistic census, that residual is 15 of 84 bounded quantifiers; on the
adversarial corpus it is 250 of 301.

---

## 4. Question 3 — COUNTER-K for the genuinely nondeterministic remainder

### 4.1 K changes no choice point — STRUCTURAL

Replication of `X{0,N}` produces N nested optional copies, each with one
choice point ("take this copy" vs "skip the rest"), and `vm_opt_chain` pushes
exactly one resume frame per copy. A counter loop with unroll factor K
produces `ceil(N/K)` trips through a block containing K copies, and each copy
keeps its own choice point in the same preference order. The number of choice
points, their order, and the frame pushed at each are therefore identical for
every K from 1 to N; only the emitted CODE that hosts them differs.

That is what makes K a dial and not a semantics — and it is also what makes
the §5.1 differential a total check rather than a sampling one: if choice
points are identical, then any disagreement between two K values is a bug by
construction, with no "but they are allowed to differ here" case to argue.

### 4.2 The emitted shape

One counter per bounded repeat, living in the `stv` array beside the capture
pairs and the empty-iteration guards, trailed on the same write-on-traverse
discipline as everything else in `stv`.

**No layout change is required, and this is not a coincidence.** §2.4's ruled
`stv` layout table already has the row — "next `R` — bounded-repeat counters
(`{m,n}`)" — sitting between the capture pairs and the empty-iteration
guards. It has no producer today (`vm_count_slots` computes
`nstate = 2*ncaps + nguard_total + nlow_total`, with no `R` term), so this row
is filling in a slot class the engine design reserved and the replication
reading then made unnecessary. An implementation lane should read that as
confirmation of the shape rather than as licence to skip §5's validation.

> **[COUNTER-K LANE, R25, 2026-08-16] §4.2 is CORRECTED IN FOUR PLACES by
> `counterk_impl/counterk_design.md`.** Annotated here rather than rewritten,
> per this directory's house style, because the corrections are what the next
> reader needs and the original claim is what they will otherwise carry
> forward.
>
> 1. **"No layout change is required, and this is not a coincidence" is right
>    about the slot and gives no REASON.** The reason (that note's §2.2): the
>    counter must be restored on resumes into the BODY, not only at the loop
>    label, and the trail is the only mechanism in this VM that does that. A
>    per-frame field is correct at one nesting level and dies on cost.
> 2. **The sketch's tail is not "(n − stv[ctr]) copies".** The tail is reached
>    only from the trip guard with `ctr` a multiple of K, so the residue is the
>    COMPILE-TIME constant `NOPT mod K` and the tail is the existing
>    `vm_opt_chain` at a smaller count. Related: the guard skips the loop at
>    `K > NOPT` STRICTLY, so byte-identity with today's output holds at
>    `K > NOPT` and not at `K == NOPT`.
> 3. **"The counter starts at 0 and counts the OPTIONAL copies" leaves the
>    MANDATORY prefix replicating**, so `X{4000}` and `X{4000,}` stay refused
>    over a choice-bearing body. That note's §3.1 gives the mandatory phase its
>    own counted loop.
> 4. **K = 8 does NOTHING for K22**, whose tower is all `{0,2}` counts and so
>    sits below K entirely. A downward safety CLAMP on K, computed bottom-up
>    over the nesting subtree, is what makes counter-K the fix the plan row and
>    the K22 entry both credit it with — and whether K may vary per quantifier
>    at all is F-1, open with Frank against §4.5 below.

```
  ; X{m,n}, unroll K
  L_entry:   stv[ctr] = 0
  L_trip:    if (stv[ctr] + K > n) goto L_tail   ; the partial last trip
             <K copies of X's code, each with its own choice point>
             RX_SET(ctr, stv[ctr] + K)
             goto L_trip
  L_tail:    <(n - stv[ctr]) copies, i.e. the residue, emitted as today>
             goto L_next
```

The tail is the existing `vm_opt_chain` at a smaller count, which is why this
is an extension rather than a rewrite: at K = N the loop never runs and the
emitter reduces to exactly today's output, which §5.2 turns into a
zero-regression gate.

The mandatory `m` copies are emitted ahead of the loop as today. The counter
starts at 0 and counts the OPTIONAL copies, so the comparison in `L_trip` is
against `n − m`.

### 4.3 The two curves, MEASURED

**Compile time.** §1.2's table IS the K curve, because a counter loop with
factor K emits K body copies regardless of N. Reading gcc −O2 as a function of
copies: 1.52 s at 64, 4.72 s at 128, 19.14 s at 256 — quadratic. At K ≤ 16 the
compile cost of the unrolled block is under 0.5 s and is not the binding
constraint on anything.

**Throughput.** The counter loop is not built, so its speed cannot be
measured. What CAN be measured is the two ENDS of the axis, because both ship
today: K = N is full replication (`((a)|b){0,N}c`) and K = 1 is the same code
shape as the frames-rung star (`((a)|b)*c` — one body copy, one resume frame
per iteration, a backward jump). The star is NOT the counter loop (no counter,
and it carries the empty-iteration guard a bounded repeat does not), so this is
an ESTIMATE of the axis and is labelled as one. `probes/probe_throughput.sh`,
−O2, min of 3 trials, both artifacts checked to agree on span and group 1
before any time is compared (`outputs/throughput_sweep.tsv`):

| N | replication (ns/search) | one-copy loop (ns/search) | loop ÷ replication |
|---|---|---|---|
| 1 | 42.4 | 110.0 | 2.59 |
| 2 | 59.8 | 129.8 | 2.17 |
| 4 | 82.8 | 138.8 | 1.68 |
| 8 | 131.9 | 173.6 | 1.32 |
| 16 | 229.7 | 258.0 | **1.12** |
| 32 | 653.7 | 521.6 | 0.80 |
| 64 | 913.3 | 856.7 | 0.94 |
| 128 | 1,700.7 | 1,761.7 | 1.04 |
| 256 | 4,285.1 | 3,065.9 | 0.72 |

**The knee is at K ≈ 16, and both curves agree on it.** Unrolling buys 2.6× at
one copy, 1.3× at eight, 1.1× at sixteen — and by 32 the advantage is gone
(0.72–1.04, i.e. at or below parity; the straight-line code stops paying once
it stops fitting in cache). Meanwhile the compile-time cost of the unrolled
block is quadratic in exactly that variable. There is no region above ~32
where unrolling is worth anything.

**RECOMMENDATION (MEASURED, on the estimate above): K = 8, with 16 as the
alternative if the implementation lane's real counter loop measures a larger
per-trip overhead than the star's.** K = 8 keeps ~1.3× of the ~2.6× available
and costs 0.22 s of gcc −O2. This is Frank's own suggested range, arrived at
from the curves rather than from the suggestion.

### 4.4 The sweep that should decide it for real

The estimate above is two ends of an axis. The real sweep, whose home is
[BENCH-1]'s bounded-repeats family:

- **Axes.** N ∈ {1, 2, 4, 8, 16, 32, 64, 128, 256, 1000, 4000} × K ∈ {1, 2, 4,
  8, 16, 32, N} × body ∈ {`(a|b)`, `((a)|b)`, `(a|bc)`, a 5-branch keyword
  alternation, a nested `(a(b|c))`} — body SIZE is a third axis and the §1.2
  table only walks one body.
- **Both metrics per cell.** Compile time (pcrec and gcc, −O1 and −O2
  separately, since they differ by an exponent) and match throughput.
- **Three subject regimes**, because a bounded repeat's cost is dominated by
  which one it is in: the loop SATISFIED at its maximum, the loop satisfied
  well below its maximum, and the loop FAILING after maximal consumption
  (where backtracking actually runs and where K should matter most — the
  throughput table above measures only the first).
- **The cost-gate families ride along**, per third-amendment consequence (c):
  the bounded-repeat × nullable-loop family (S14's witnesses, ~0.1% of random
  patterns) joins the sweep, since its interaction with the counter is the one
  place termination could go wrong (§6).
- **Every cell under `timeout`**, generously sized; a timeout is a recorded
  finding, as the `> 240 s` cells in §1.2 are.

### 4.5 What the sweep must NOT be allowed to decide

K is per-artifact tuning; it must not become a per-pattern heuristic in v1.
D18's "an axis must earn itself" applies: one measured constant, forceable per
§5.2, and a later row may make it adaptive if a measurement ever asks for it.

---

## 5. Validation — the four ruled requirements, discharged

### 5.1 Requirement 1 — replication is the ground truth, so the primary instrument is a pcrec-vs-pcrec differential

**Why this is the strongest instrument available anywhere in the project.**
Replication is not an approximation of `{0,N}` semantics; it is literally
`{0,N}` unrolled, it is what ships today, and §1.2 measures it as tractable
below the knee (N ≤ 256 compiles in 19 s at −O2, N ≤ 64 in 1.5 s). So the
check does not need an external oracle to have an opinion: two pcrec artifacts
for the same pattern, one forced to replication and one forced to
counter-K/possessive/rung-X, must agree, and **any disagreement is a bug by
construction** because §4.1 makes the choice points identical.

The comparison is on four things, and the last two are the ones a weaker check
would drop:

1. the match span;
2. **EVERY capture slot** — all `RX_NCAPS` pairs, including the ones the test
   subject leaves unset, compared as `ptrdiff_t` pairs against `RX_UNSET`;
3. the FAILURE SURFACE — a subject that exhausts the frame array must produce
   `RX_ERR_FRAMES` from BOTH artifacts **at the same iteration count**, not
   merely both fail. This is what stops a strategy from passing by being
   quietly more forgiving than the ground truth;
4. `rx_info`'s stamped `frame_capacity` / `subject_ceiling`, which D44.5 makes
   the artifact's honest declaration of its own limit. A strategy that changes
   the real limit and not the stamp has broken the stamp's contract, and the
   differential is where that shows.

> **[COUNTER-K LANE, R25, 2026-08-16] items 3 and 4 are NARROWED by
> `counterk_impl/counterk_design.md` §8.1.** Annotated in place per house
> style; the requirement is right and two of its four comparisons cannot be
> made as written.
>
> - **Item 4 asks the two builds' stamps to AGREE, and they must not.** A
>   counter build writes `1 + ⌈NOPT/K⌉` trail entries per phase that a
>   replication build does not, so its honest `cost.trail` is larger and its
>   stamped ceiling correspondingly tighter. The checkable property is not
>   equality between builds but HONESTY per artifact — run at the stamped
>   ceiling and confirm no give-up, the shape `tests/vm/run_vm_tests.sh`
>   already uses. Frames DO agree exactly, because one choice point per
>   iteration is semantics-dictated and no strategy moves it.
> - **Item 3's "at the same iteration count" is not observable as the emitter
>   stands.** Trail overflow and frame overflow return the SAME sentinel and
>   `--backtrack-frames=` sets both capacities from one number, so a
>   differential cannot tell which array gave up or provision one without the
>   other. Either a distinct trail sentinel is added, or the differential
>   over-provisions and checks frames only.

**Subjects**, swept rather than chosen: for each pattern, the loop satisfied at
0, 1, m−1, m, m+1, n−1, n and n+1 iterations; each of those with the follow
present and absent; plus a random sweep over the body's own alphabet. The
harness precedent is `tests/vm/`'s existing identity checks and
`tests/codegen/run_trie_identity.sh`, which already builds a reference compiler
behind a flag and diffs emitted C — the same technique, one axis over.

**Where the differential is blind, disclosed:** above the replication knee
there is no ground truth to compare against, so `N = 4000` is checked by §5.3's
oracle sweep and by extrapolation of the strategy's own N-independence, not by
this instrument. That is the honest limit of "replication is the true version".

### 5.2 Requirement 2 — every strategy forceable end to end, do or die

The R21 E-6 testability pattern, and D46's controllability half, which
currently has no producer. Concretely:

- `--repeat-strategy=replicate|counter|auto` and `--unroll=K`, per invocation,
  refusing rather than silently downgrading when the pattern cannot honour the
  request (the `--engine=` precedent exactly: "a request the pattern cannot
  honour is REFUSED, never silently downgraded").
- `--no-possessify` — the negative axis, so the possessification rewrite can be
  turned OFF and the differential can compare with against without.
- `--rung=cursor|frames|auto`, completing D46: today the rung is observable
  (the `<PREFIX>_VM_RUNGS` bitmask, `--emit-ir`'s RUNGS section) and not
  forceable.
- Each choice reported in `rx_info` and in `--emit-ir`'s header, so a check can
  assert that the artifact did what it was told rather than trusting the flag.
  `--emit-ir` already prints `rungs` and `max replicas`; this adds the
  strategy and K beside them.

"Do or die" is the point: a strategy that cannot be forced cannot be
differentially tested, and this row's entire validation story is a
differential.

### 5.3 Requirement 3 — the three-way oracle sweep on top

Per D44's three-way rule (pcrec / python3 `re` / libpcre2), riding on top of
the pcrec-vs-pcrec differential rather than replacing it, and DENSE where the
design has edges:

- at and around the K threshold — K−1, K, K+1 iterations, and N ≡ 0, 1, K−1
  (mod K), which is where an off-by-one in the residue tail lives;
- N = 0 and N = 1, and `m > 0` (`X{2,5}`), and `m == n`;
- empty-capable bodies (`(a?){0,4}`, `(a*){0,3}`, `((?:a|)){2,4}`) — §6's
  territory;
- captures inside the loop, including a group inside an alternation inside the
  loop, which §3.4 shows is where the last-iteration rule is least intuitive;
- **`(|a){m,n}` specifically** — a nullable-FIRST-branch group in a bounded
  repeat. Named as its own cell because R24 measured it as the family where
  the oracles themselves disagree: over 15,600 cells, pcrec agreed with
  libpcre2 on every one, while **python disagreed with libpcre2 on 106 cells,
  all of them `(|a){m,n}` captures**. A two-way python-only check on this
  family would have raised a false alarm against pcrec. That is a measured
  argument that D44's three-way rule earns itself on this row rather than
  being ceremony;
- **greedy AND lazy at every shape — MANDATORY, not a nice-to-have** [R24
  S-F1]. §2.3's lazy argument was BELIEVED and was REFUTED; the repaired rule
  has a lazy-only conjunct, so a sweep that spells every shape greedy is
  structurally incapable of exercising the conjunct. Any implementation lane
  that omits the lazy half is re-running the exact experiment that missed the
  defect the first time.

§3.6's no-pre-built-exclusion rule stands: a three-way disagreement is
investigated, not filtered. Note U9 (`docs/dev/upstream_issues.md`) before
investigating one in a possessive-spelled family: PCRE2 10.46 and python
disagree there for a reason that is neither engine's fault and none of
pcrec's.

### 5.4 A gate the lane gets for free

At K = N the counter loop never runs and the emitter reduces to today's
`vm_opt_chain` output (§4.2). So **`--repeat-strategy=counter --unroll=N` must
emit BYTE-IDENTICAL C to `--repeat-strategy=replicate`** for every corpus
pattern. That is the §5.4 zero-regression technique applied to this row, it is
cheap, and it fails loudly if the residue-tail arithmetic is wrong.

---

## 6. Termination, stated explicitly

R21 E-2's ruling is load-bearing here and the plan row is right to demand this
section: **bounded repeats take NO empty-iteration guard.**

**Why the guard exists at all.** For `X*` with a nullable `X`, an iteration
that consumes nothing can be repeated forever; §3.3's guard records the
position at which the loop last iterated and suppresses a repeat at the same
position. It is a slot in `stv` and a test per iteration.

**Why a bounded repeat does not need it, today.** STRUCTURAL: under
replication there is no loop. `X{0,4}` is four nested optional copies, and
"four" is a property of the emitted code, not of anything checked at run time.
Each copy is either taken or skipped, so at most four iterations run, and an
empty iteration simply produces a shorter path, not a longer computation.
Termination is by construction, and there is nothing to guard.

**Why a counter loop keeps that true, which is the claim this row owes.**
STRUCTURAL: `L_trip` in §4.2 increments `stv[ctr]` by K on every trip and the
loop's guard is `stv[ctr] + K > n − m`. The counter is monotonically strictly
increasing and bounded above by `n − m`, so at most `ceil((n−m)/K)` trips
happen — **whatever the body consumes, including nothing**. The bound is on
the COUNTER, not on progress through the subject. That is the exact difference
from the unbounded star, where no counter exists and the only available bound
IS subject progress, which is why the star needs the guard and the bounded
repeat does not.

The backtracking direction terminates for the same reason from the other side:
each resume frame belongs to one copy at one counter value, `rx_fail` pops
monotonically, and the counter is restored from the trail on unwind, so no
frame can be re-entered at the same (copy, counter) pair twice.

**And this is not merely intentional, it is correct.** MEASURED
(`outputs/termination.txt`, `probes/probe_termination.sh`), read out of the
emitter's own `--emit-ir` SLOTS section:

| pattern | bound | guard slot emitted |
|---|---|---|
| `(a?){0,4}b`, `(a*){0,3}b`, `((?:a\|)){2,4}b`, `(b*){1,3}c`, `(\|a){0,3}b`, `((a)\|){0,2}b` | bounded | **none** |
| `(a?)*b`, `(a*)*b`, `((?:a\|))*b`, `(\|a)*b` | unbounded | present |

and the same ten patterns against python3 `re` over 14 subjects each: **0
divergences**. The omission is deliberate, visible in the listing, and matches
the oracle.

**Scope of that instrument, and the stronger result that replaced it** [R24
S-F5]. This lane's check compared SPANS ONLY and against python ONLY — it
could not have seen a capture-slot divergence, and it had no second oracle. The
R24 panel rebuilt it captures-aware and three-way: **15,600 cells, pcrec equal
to libpcre2 on every one, span and every capture slot.** So §6's claim is now
confirmed at a strength this lane did not reach, and the confirmation is the
panel's, not this note's.

The rebuild also produced the S-F5 finding that §5.3 now carries as a named
cell: python disagreed with libpcre2 on 106 of those cells, all `(|a){m,n}`
captures. Had the panel checked two ways instead of three, §6's own family
would have produced a false alarm against pcrec.

**The one thing an implementation lane must not do:** add the guard "for
safety" when the counter arrives. It would be a semantic change, it is exactly
what E-2 measured as wrong on 60 of 225,240 pairs, and the counter makes it
unnecessary.

---

## 7. Blast radius, predicted

- **Capture-free patterns: zero change.** They never reach `emit_vm.c`; §5.4's
  byte-identity gate covers them and 613 of 756 corpus patterns are in this
  class.
- **The corpus: small and predictable.** 15 distinct patterns put a quantifier
  on the frames-bounded rung under default selection (§3.2; the figure was 11
  before [R24 M-F1] and the undercount's cause is recorded there). Possessification touches
  more (174 of 1,725 quantifiers across both bounds), and every one of those
  changes emitted C while changing no answer — which is precisely what
  `emitdiff`-style checking is for and what the §5.1 differential asserts.
- **The cap's diagnostic gets to stop being the endgame.** Today
  `PCREC_MAX_VM_REPEAT_COPIES` refuses `((a)|b){0,4000}c` with advice to
  rewrite the pattern. Once the counter exists, the same pattern compiles; the
  cap stays as the backstop for the replication STRATEGY and its diagnostic
  can honestly point at `--repeat-strategy=counter`. That is D26 tier 3 work
  and should not be gold-plated.
- **`rx_info`'s stamped ceiling moves, for the better.** A counter-K artifact's
  frame requirement is `ceil((n−m)/K)`-independent — still one frame per
  iteration — so `subject_ceiling` is unchanged in kind. Possessification
  removes frames entirely for its class, so those artifacts newly stamp
  "no limit" truthfully where today they stamp a real one.
- **Two known-risk interactions**, both to be swept rather than argued:
  bounded repeat × nullable loop (§4.4, third-amendment consequence (c)), and
  bounded repeat nested inside a bounded repeat, where the replication factors
  MULTIPLY and `v.maxcopies` currently records only the max.

---

## 8. What I did NOT measure, and where the risk sits

Ordered by how likely it is to matter.

1. **The counter loop itself, at all.** It does not exist. §4.3's throughput
   estimate substitutes the frames-rung star for K = 1, which differs from a
   counter loop by a counter increment, a compare and the ABSENCE of the
   empty-iteration guard. The direction of that error is unknown: the star
   carries a guard the counter would not (so the counter should be faster) and
   lacks a counter the loop would have (so slower). The knee's LOCATION is
   the claim most exposed to this, though the compile-time curve alone would
   put it in the same place.
2. **ANSWERED at [R24], kept for the record: `$` as a follow.** This entry
   read "BELIEVED-yes and unmeasured; the single highest-value follow-up". It
   is now MEASURED-WITH-GATE — safe at 0 of 720, unsafe at 180 of 720 under
   `(?m)` — and §2.5 carries the result and the live-gate requirement. Left in
   place rather than deleted because the note's own prediction about which
   unmeasured item mattered most turned out to be right, and that is worth
   being able to check next time.
3. **Lazy quantifiers under possessification — PARTLY ANSWERED, and the answer
   was a REFUTATION** [R24 S-F1]. This entry recorded that the differential
   could not check lazy "because there is no possessive spelling of a lazy
   quantifier", and proposed deferring the check to §5.1's pcrec-vs-pcrec
   differential once forcing exists. Both halves were wrong in a way worth
   keeping visible: the comparison `X{m,n}?` against `X{m,n}+` is perfectly
   well-formed and needed no forcing, no implementation and no new
   instrument — only the realisation that the possessive form is the right
   right-hand side for BOTH preferences. Deferring a cheap check to a lane
   that does not exist yet is how the defect survived the note. §2.4's lazy
   family now runs; what remains unmeasured is lazy under NESTING (item 8) and
   lazy against libpcre2 (item 6).
4. **Nested bounded repeats.** Every measurement here uses a single level. The
   replication factors multiply, `vm_count_slots` records only the maximum,
   and §3.4's capture derivation is single-level. This is the largest
   unexplored corner and §7 names it as a sweep axis.
5. **UTF-8.** The whole analysis is stated over BYTES. In pcrec's UTF-8 mode a
   "byte set" is still the right object (the automaton is over bytes), so the
   analysis should carry over unchanged — BELIEVED, unmeasured, and the
   multi-byte-class shapes are the place to check it.
6. **libpcre2 anywhere in THIS LANE.** Every oracle check this lane ran is
   python3 `re`. **[R24] closed the most important part of this gap from the
   outside:** the panel re-ran the full 5,016 × 260 greedy family against
   libpcre2 and reports 0 counterexamples with an identical possessifiable
   population, and re-ran §6's own family three ways at 15,600 cells with
   pcrec matching libpcre2 on every span and every slot. So the headline
   soundness result IS PCRE2-verified — by the panel, not by this note. What
   is still python-only here: the LAZY family added at [R24] (§2.4), the two
   censuses of §2.6, and the `$`/assertion sweeps. §5.3's three-way sweep
   remains specified and not run by anyone.

   **[NESTED-LAZY LANE, 2026-08-16] the python-only residual is CLOSED**
   (`outputs/nestedlazy_findings.txt`, probes committed): the lazy family
   0/5,016 vs libpcre2 (10.46); the censuses' possessifiable rows
   differentially checked for the first time (306 rows, 0 counterexamples,
   both oracles; one `(?i:...)` body disclosed as out of the unparser's
   scope); the `$`-follow sweep split by arm — exact-count
   follow-independent (0/48), greedy disjoint safe non-multiline / unsafe
   under `(?m)` (0/168 and 12/168, reproducing §2.5's gate numbers against
   BOTH oracles), and the lazy disjoint arm's 21/168 divergences are the
   ALREADY-DECLINED lazy+nullable-rest shape (`$` makes the remainder
   nullable regardless of `(?m)`), verified against the SHIPPED pass by the
   manager at merge: `([^c]{0,4}?)$` stamps 0-of-1 possessified while the
   greedy control stamps 1-of-1. MAINTAINER NOTE with teeth: any future
   `$`-exemption rework must feed `$`'s presence through the SAME
   lazy-conjunct machinery, never bypass it as an independent rule — a
   bypass ships exactly those 21 cells as miscompiles.
7. **The realistic pattern set is hand-written from memory of the shapes**, by
   the same author who wrote the analysis. That is the exact control-shares-a-
   source failure this project has hit before. A set harvested from real
   sources would be a strictly better denominator and this one should be
   treated as indicative, not measured.
8. **NESTED quantifiers' verdicts are censused but not differentially
   validated.** `probe_possess.py` compares the outermost quantifier's
   preference spelling against its possessive spelling, and only the
   OUTERMOST one. The FOLLOW computation for a
   quantifier inside another quantifier's body — where the enclosing loop's
   own FIRST set joins the follow, which is the subtlest line in §2.2 — is
   therefore exercised by §2.6's censuses and checked by nothing. It is the
   single most likely place for a soundness bug to be hiding, and §5.1's
   pcrec-vs-pcrec differential is what should close it.

   **[R24] partly retired this, and the residual is narrower than it was.**
   The panel attacked exactly this line — 42,336 pairs × 200 subjects, 0
   diverging, with failing-direction controls that confirm the line is
   load-bearing (dropping the enclosing-loop-FIRST term yields 172
   divergences; dropping U1+U2 yields 551). So the transitive FOLLOW rule is
   now measured, not merely censused. What is still unchecked is the same
   nesting question for the LAZY conjunct, which postdates that sweep: the
   probe's `info[0]` selection means a lazy quantifier nested inside another
   quantifier's body has never been differentially tested. The panel's own
   note that `info[0]` is "correct only by accident" applies with more force
   now that there are two rules to get right instead of one.

   **[NESTED-LAZY LANE, 2026-08-16] the residual is CLOSED**
   (`probes/probe_possess_nested.py`, `outputs/nestedlazy_findings.txt`):
   a 9,216-pattern two-quantifier family across all four preference
   combinations, testing BOTH the outer's and the inner's verdict with the
   target's identity asserted against its own (lo,hi) rather than assumed
   — 18,432 comparisons, 0 soundness counterexamples on the real analysis.
   Failing-direction controls both catch: dropping the lazy conjunct
   yields 68/2,560 divergences, dropping the enclosing-loop-FIRST term
   212/3,952. The `info[0]`-by-accident concern is retired by
   construction, not by luck.
9. **Assertions INSIDE the body are ignored by the unique-iteration check**
   (`Glushkov.build` skips `AT`), while assertions in the FOLLOW widen to all
   bytes (§2.5). The asymmetry is deliberate and BELIEVED sound in the
   direction it matters: dropping an assertion from the body can only ADD
   paths, and both (U1) and (U2) are preserved downward — a deterministic,
   prefix-free superset has a deterministic, prefix-free subset. Argued, not
   measured; no body in the differential family contains an assertion.
10. **Compile-time cost of the possessification analysis itself.** Glushkov
   first/last/follow over a body is linear-ish in body size, and the bodies are
   small, so this is believed negligible — unmeasured, and the pathological
   case (a body that is one enormous alternation) was not tried.
11. **Interaction with `--trace` and the step budget.** A counter loop's step
   accounting (§4.2 charges nothing per trip) was not checked against §4.2's
   "a step IS a backtrack resumption" rule. Probably free; unverified.

---

### 8.1 Follow-up, ratified for benching (Frank, 2026-08-16): CAPTURE-WALK SINKING

Recorded during the rung-select lane's flight, from conversation on the
as-built revdet listing. The revdet rung derives last-iteration captures
by a backward walk AT EACH COMMIT, then tries the follow — so a retreat
that dies in the follow's first byte has paid a walk (bounded by the
committed span) for captures nothing ever observed. Since no construct in
the current tier can read a capture slot before ACCEPT, the walk is free
to move later, and the design space is ONE knob — how far the walk SINKS:

- **eager** (as built): walk at every commit; O(span) per retreat,
  O(span²) worst case on a long failing follow (disclosed at §3.4).
- **n-step / sink-to-first-branch** (Frank's proposal): in an AOT
  emitter this is pure CODE MOTION, no runtime counter — emit the walk
  block after the follow's first n consume events, stopping at the first
  choice point so nothing duplicates. n is pattern-determined and
  maximal for free (`abba` gives n=4). Retreats that die before the sink
  point never pay the walk; the retreat frame is pushed at commit as
  today, so frames/trail accounting is unchanged.
- **accept-time** (n=∞): retreat pays only the one reverse step that
  locates the previous boundary; ONE walk per loop at the accept label
  derives everything. O(span) total. Needs the loop's entry/boundary
  slots trailed (per pass, not per iteration) so a path that abandons
  the loop entirely cannot leak stale spans.

The unifying rule: the walk sinks to the LATEST POINT DOMINATING EVERY
OBSERVER of its slots. Base tier: that is accept. A future `backrefs` or
callout module is an observer that pulls the sink point earlier
AUTOMATICALLY, per pattern — no eager/lazy mode switch. Both sunk
variants stay forceable against eager for §5.1's differential.

Why gcc cannot do this for us (and what it may do anyway): capture
writes are TRAILED — each store pushes an undo record the backtrack path
reads — so the walk is live on the fail path as far as gcc can prove,
and neither the walk loop nor its trail traffic can be compiler-
eliminated. Plain untrailed stores gcc may sink or kill on its own. So
the bench question is the DELTA the manual sink adds over gcc's share:
BENCH-1's bounded-repeats family, non-disjoint follows, eager vs sunk
forced both ways, compile time and throughput. Per D18 the optimization
is built only if that delta earns it; "negligible" is a good, cheap
outcome.

## 9. Rulings requested

**ALL SIX RULED (Frank, 2026-08-16 — docs/dev/decisions.md D47; outcomes
here, reasoning there):** (1) possessify-first CONFIRMED for BOTH
application and build order, eyes open that the D45 refuse-cap endgame
arrives with a later ladder step. (2) K = 8, as a NAMED CONSTANT in
src/core/limits.h (PCREC_DEFAULT_UNROLL_K), sweep may move it. (3) The
four force flags are RESHAPED: gcc-style ALLOW/DENY flags (deny
composes per-quantifier — each quantifier walks its own ladder skipping
denied steps), one K value parameter, per-quantifier strategy STAMPS
with denied-strategy-appears = hard failure, denying both universal
fallbacks = compile error; documented as testing/tuning axes, one
spelling family, not top-level user features. In-pattern `(*...)` hints
DEFERRED (oracle string-identity + module-gating costs; see D47.3).
(4) Third-amendment consequence (b) STRUCK-AND-REPLACED in the plan row.
(5) The `$` exemption SHIPS in v1 with the LIVE !multiline gate; module
`assertions` row inherits the gate-test obligation. (6) The lazy
conjunct ACCEPTED — and ruling on it CORRECTED ITS OWN PREMISE: the "20
false declines" below are refuted, all 20 GENUINELY diverge on subjects
probe_possess.py's generator could not produce (its ALPHA omits the
prefix `z`), the full 3,726-row possessifiable population re-swept
targeted is 0 counterexamples both preferences, and the conjunct's
measured cost is ZERO. The 20 cells join the .rxt corpus as guards.
The original asks are retained below unedited; ask 6's premise is
corrected where §2.4/§10 discuss the sweep.

1. **The ladder order and the recommendation to build possessification
   FIRST.** §2 is the largest win on the realistic population (82% of bounded
   quantifiers) and it is the only one of the three that removes machinery
   rather than reshaping it. It is also the only one that needs a new analysis
   pass. Confirm it leads.
2. **K = 8 as the shipped default**, subject to §4.4's sweep moving it. The
   alternative reading of §4.3 is K = 16 (which keeps a little more of the
   speed and still compiles in 0.42 s); the case for 8 is that the curve is
   already flat there and smaller is cheaper to compile and to reason about.
3. **The forcing-flag surface of §5.2.** Four new generation axes
   (`--repeat-strategy`, `--unroll`, `--no-possessify`, `--rung`) is a lot of
   surface for one row, and D18 says an axis must earn itself. My reading is
   that all four earn themselves as TESTABILITY axes (each one is what makes a
   differential possible) rather than as user features, and that they should be
   documented as such. Confirm, or cut `--rung` — it is the one whose
   differential D46's observability half already partly covers.
4. **Whether third-amendment consequence (b) should be struck from the plan
   row.** §0.2 item 4 and §1.4 report it as not established. The row's other
   consequences are unaffected. I have not edited the row; that is the
   manager's call.
5. **[R24] Whether the `$`-follow exemption ships in v1 or waits.** §2.5 now
   has it measured safe under a live `!multiline` gate, and §2.7 records it as
   the largest single source of conservatism in the greedy family. The case
   for taking it is that end-anchored bounded repeats are common; the case for
   waiting is that it is the only rule in §2 whose correctness depends on a
   pattern option rather than on pattern structure, so it is the first place
   an `(?m)` implementation would silently break the analysis. My
   recommendation is to TAKE it, with the gate written as an assertion against
   the pattern's live multiline state rather than a comment — but a manager
   who would rather have one fewer option-coupled rule before module
   `assertions` lands has a real argument.
6. **[R24] Whether the lazy conjunct's 20 false declines are worth a v2.**
   §2.4 measures the conjunct as costing 20 quantifiers that the differential
   shows no divergence for; the conjunct is stated on "the remainder is
   nullable" where the sharp condition is "some non-maximal exit actually
   succeeds". I recommend NOT sharpening it in v1 — 20 out of 2,031 is a 1%
   cost for a rule that is one predicate and provably sound, and §2.3's
   history is that the elaborate version of this argument is the one that was
   wrong.

---

## 10. A note on this lane's own instrumentation

Recorded because each of these produced numbers that would otherwise have
entered the note as findings.

- **The analysis was wrong and the probe caught it — twice.** §2.4's 117
  counterexamples and §2.5's `\b` witness both came from running the analysis
  against an oracle rather than from reading it. The version of this note
  written without the differential would have proposed an unsound
  transformation with a confident soundness argument attached, because the
  argument's broken step (exits form an increasing chain) is the step that
  looks least like an assumption.
- **v1's differential passed a family it should have failed** (§2.4, the
  `(?:ab|a)` disclosure), because the harness's follow set never asked a
  question that family could get wrong. The fix was to add three follows. The
  lesson is the recorded one: a check whose inputs come from the same head as
  the design inherits that head's blind spots.
- **`probe_throughput.sh` reported every row under the wrong N** on its first
  run, because `sh` has no locals and a helper's `n=$1` ate the caller's loop
  variable. Caught by the smoke run producing rows labelled `starrep4`. The
  script now prefixes helper variables and says why in a comment.
- **Two cells of the replication sweep were measured under load** from a
  parallel probe and reported pcrec times ~30% high; they were re-measured
  serially before being quoted, and §1.4's table is the serial one. The
  archived sweep still contains the loaded cells, which is why the note quotes
  §1.4's table and not the sweep's `pcrec_s` column for those rows.
  **[R24 M-F4] found the sequel to this and it is worse than the original
  defect:** the serial re-measurement was never ARCHIVED, so §3.3 ended up
  quoting a number that existed only in a transcript. A number that cannot be
  re-run is not a measurement, whether or not it is correct. §3.3's table is
  now produced whole by `probes/probe_cell33.sh`, serially, into one file.
- **Every scratch compiler was built by `probes/mkscratch.sh`**, which asserts
  that each patch actually changed its file — so a `sed` whose anchor moved
  fails loudly instead of silently building the stock compiler and reporting
  its numbers under a prototype's name.

### 10.1 The three defects [R24] added

- **The lazy preference family was never in the differential** (§2.3, §2.4).
  `probe_possess.py` built a possessive respelling of each generated pattern,
  a lazy quantifier has no possessive spelling, and the helper that noticed
  that returned `None` — silently dropping half the design's claim from a
  check the note described as covering it. The defect is not the `None`; it is
  that the skip was invisible in the output, so nothing in 5,016 rows of TSV
  said "and half the question was not asked". The replacement derives BOTH
  spellings from one base count, so omitting a family now requires deleting a
  loop rather than falling through a helper. §8 item 3 records the reasoning
  error that kept it there: the note KNEW lazy was unchecked, wrote it down as
  a limitation, and proposed deferring it to an implementation lane that does
  not exist — when the check cost one afternoon and needed nothing new.
- **`sort -u` under a UTF-8 locale silently merged distinct patterns** (§3.2),
  making every "distinct" figure in the rung census an undercount. Two of the
  panel's findings (M-F1's wrong count, M-F2's unreproducible column) are the
  same defect seen from two angles. Two aggravating factors, both mine: the
  pipeline was never committed, so nobody could re-derive it; and a regex test
  corpus is close to a worst case for locale collation, since its patterns
  differ mostly in punctuation. `probes/census_rungs.py` now produces every
  figure §3.2, §3.3 and §7 quote, in python, with exact string equality.
- **§3.3's table mixed three sources and mislabelled a row.** Its line count
  came from one archived file, its pcrec time from an unarchived transcript,
  and the row it called "cursor rung" used `(?:ab){0,N}y` — non-capturing,
  therefore requesting no captures, therefore compiled by the DFA and never
  reaching the VM's cursor rung at all. The panel caught the mixed sources
  (M-F4); the mislabelled row is this lane's own finding on re-measurement.
  `probe_cell33.sh` now reads the engine out of `--emit-ir`'s header per row,
  so a row cannot claim a rung the compiler did not take.

### 10.2 The defect [D47.6] added

- **`probe_possess.py`'s subject alphabet excluded the discriminating
  character.** This is the fifth-or-so instance in this lane alone of the
  corpus-cannot-reach-the-failure lesson (§2.4's `(?:ab|a)` follow gap and
  §10.1's lazy-family omission are its siblings above) — this time the thing
  that could not be reached was not a construct or a preference family but a
  single BYTE. `subjects()`'s random tail was drawn from `ALPHA = "abcd "`,
  which never contained `z`, the byte every non-empty `PREFIXES` member
  (`"z"`, `"(?:z|)"`) is built from; the handful of fixed literal `z`-subjects
  carried too little post-`z` repetition to enter a `{3,}`-bodied loop at
  all. §2.4's "20 false declines" was this defect's visible symptom: the
  differential reported "same" for 20 z-prefixed lazy+nullable-rest
  quantifiers not because they were safe, but because no subject in the swept
  set could exercise the divergence. Pulling those 20 for Frank's inspection
  (D47 ruling 6) found this rather than a real cost. Fixed by adding `z` to
  `ALPHA` and, more durably, by generating deterministic repetition-heavy
  subjects (long single-byte runs and two-byte cycles, each also emitted
  prefixed by every pattern byte) instead of relying on a random walk to find
  depth by luck — so the next byte a `PREFIXES`/`BODIES`/`FOLLOWS` edit
  introduces is swept with real depth from the start rather than needing its
  own inspection to notice the alphabet never grew to match it.
