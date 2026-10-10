# `[START-LANDING]` — RECOVER rows that know the start without walking

**DESIGN NOTE + HAND-TWIN, PROPOSED, revision 1, nothing built.** Lane `landdes`,
2026-10-09, from main `e1e387b9` (abi 71). Nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changes. Charter: plan row `[START-LANDING]`
(`../dev/plan.md`), placed by `locate_finish.md` rev 2.1 §7.3 (LR-G10) and ordered by
D156 addendum 1 (Frank: REVEND builds first, this is designed in parallel). Evidence:
`../../studies/start_landing/` (own CLAUDE.md): a fact PROBE (a scratch patch that
prints the facts and selects nothing), the census over walk_survey's two populations,
an emitter-independent twin transformer, the three-answerer identity driver
(artifact, twin, libpcre2 10.46), its controls, and directional timing.

Read before writing: `../dev/walk_survey.md` §4 K4 and K3 (the survey's class labels,
not known_issues ids); `locate_finish.md` §1.2 (the product and the `CT_*` hand
masks), §2.7 (`.needs` and the path derivation), §5.1 (the stamp rule), §7.3, §7.6,
§7.9; `start_table.md` §1.1-§1.6 (the row contract and the typed handoffs) and the
shipped `pinned` row (`src/gen/emit_dfa.c` `start_pinned_applies` `:7889`,
`cand_rows[]` RECOVER rows `:8427-8437`); `opt5_step2_twopass.md` (`pinned`'s proof,
whose shape §2 follows); the review `../dev/reviews/2026-10-09-r-locfin-panel.md`
LR-G10/LR-G11/LR-G14.

---

## 0. Answers first

1. **(a) The fact (§2).** The survey's statement, "every start-set byte takes the
   anchored machine to accepting", is sound in byte encodings and too narrow under
   utf8: a lead byte alone accepts nothing, and the two largest K4 cells are utf8. The
   fact this design reads is **Λ, the ONE-CHARACTER fact**: *from the pattern's own
   anchored start, every one-character path ends DEAD or UNCONDITIONALLY ACCEPTING,
   no assertion is reached before that, the pattern is not nullable, and (multibyte
   encodings) no continuation byte can begin a match.* Under Λ the forward scan's LAST
   landing (the position the NEXT block handed when it last ran) is exactly the start
   today's reverse pass returns, on every call; §2.4 proves it. That is answer
   identity with TODAY'S ARTIFACT, not only with PCRE2, and it is what makes the row
   NEUTRAL on hybrids. Under the invalid-tolerant utf8 contract one runtime guard is
   owed: an ILL-FORMED first character at the landing re-enters the forward scan at
   `landing + 1` (a RAISE edge, §2.5). The owner is `src/facts/kset.c`, the walk
   from `Nfa.anch_start` ("the thread from the candidate start alone"), as a new E3
   fact. The EXACT condition (§2.3, the "excursion" condition) admits more, but its
   measured upper bound on the bench is 0.58 ms of 54.6 ms: FILED (§2.8).
2. **(b) `end-minus-width` (§3).** A fixed BYTE width `W` of the machine's own
   language, read from the same NFA walk (assertions passed: zero-width, so a superset
   of paths, the sound direction). It is exact whenever RECOVER is handed a VERIFIED
   end, utf8 and ill-formed input included. `$`/`\Z`/`\z` do not touch it. The one
   interaction is REVEND: `rev-end`'s walk asks RECOVER with a SPECULATIVE end, which
   neither new row may take (§3.3).
3. **(c) The rows (§4).** RECOVER becomes `pinned`, `end-minus-width`, `landing`,
   `reverse-pass` (`end-minus-width` ahead of `landing`: equal cost where both apply,
   measured, and it needs neither the NEXT record nor the guard). Both new rows
   are routed `CR_DFA` only (no reverse pass exists on the other routes) and take only
   the hand `END`. Each has one deny-only bit masked out of `rx_info.flags`. Their
   `.needs` omit R, so §2.7's member fold drops the reverse machine with no stamp edit.
   `RX_DFA_START` and `rx_info.search_form` gain two values. One abi event. On
   hybrids the rows are NEUTRAL BY WINDOW IDENTITY, verified per prefilter call
   (68.4 M calls over 670 hybrid rows, bench and corpus, 0 differences, §5).
4. **(d) Identity (§5).** Every bench row the design selects (310 (pattern, config)
   rows) was twinned in ASSERT mode, which keeps the reverse pass and compares its
   start with the row's on every call. Coverage: 91.5 M (call, startpos) cells, every
   startpos on short subjects, the bench's own throughput subjects with find-all, and
   a machine-derived exhaustive pool (ill-formed utf8 tokens included). Results:
   **0** twin/artifact differences, **0** per-call differences in 50.1 M calls, and
   **0** new libpcre2 disagreements (the 14,504 pre-existing ones are K74's, identical
   on both sides). The corpus adds 1,750 rows and 143.3 M per-call checks, also with
   0 differences (§5.2). Seven controls FAIL as they must (§5.3).
   Directional timing, two runs, 7700X, loaded box: `abcd` −37/−38%, utf8 `.` −42%,
   utf8 `\p{L}+` −35%, `\w+` −29/−30%. Every gap except `\w+` exceeds 2(σa+σb); the
   `\w+` gap does not, because one cold outlier of 5.5 ms inflates σ (§5.4).
5. **(e) Predicted bench (§6).** Of the 54.6 ms K3+K4 weight (default config), the
   rows take 46.5 ms (85%): `landing` 42.6, `end-minus-width` 3.9. The top cells:
   utf8 `\p{L}+` 11.8 → ~7.6 ms, utf8 `.` 13.1 → ~7.6, `\w+` 7.1 → ~5.0 ms.
6. **(f) Build (§7).** After L0, as 4 commits: B1 the two facts (a no-mover), B2
   the rows, the record and the guard (the abi event), B3 the `hand` filter on
   RECOVER (if REVEND's L2.2 has not landed it already), and B4 spec/listing/bench
   relay. 9 sabotage rows.

---

## 1. The question, and why the answer is an identity

RECOVER asks: *given a match END from the forward machine, where does the match
start?* (`start_table.md` §1.2). Today two rows answer it. `pinned` uses zero bytes
of evidence: the start state accepts unconditionally, so the start is `search_from`.
`reverse-pass` is the fallback: a backwards walk over the reverse machine from the
end to the furthest-back accepting position at or after `search_from`.

walk_survey found two classes where the start was known before the walk:
- K4: the match begins at the byte where the start-byte skip LANDED;
- K3: every match has the same width.

Both are new RECOVER rows that hand `SPAN` (`CT_START`) exactly as `reverse-pass`
does, so the locator's output type is unchanged and FINISH is untouched
(`locate_finish.md` §1.2, §7.3).

**The proof obligation is stronger than "PCRE2-correct", and that is deliberate.**
Each new row is proved to return EXACTLY THE START TODAY'S REVERSE PASS RETURNS, on
every call, for every subject and `search_from`. Three things follow:
- PCRE2 agreement is inherited, not re-derived;
- the deny flag yields a genuine control: the denied build recovers the start from an
  independently built reverse machine (`tuning.md` §2.19's argument for `pinned`);
- on a VM hybrid the inlined prefilter's window is byte-for-byte today's, so no VM
  attempt moves and the give-up surface cannot move (NEUTRAL by window identity;
  `locate_finish.md` §1.5 classifies by attempts removed, and these remove none).

The twins test exactly this identity (ASSERT mode keeps the reverse pass and counts
disagreements per call, §5).

**Where to attack §1.** A RECOVER asker whose END is not the forward machine's
verified end. §3.3 names one, `rev-end`. Is there another (the trace build's
RECOVER asks are the population)?

---

## 2. (a) The `landing` fact

### 2.1 What "the landing" is in the emitted loop

The forward scan (`emit_scan_loop`, `src/gen/emit_dfa.c:9528`) runs the NEXT row's
block exactly when the machine holds the start state with nothing accepted:
- `pf_open` (`:5958`) writes the guard `if (<state> == <s0 cell> && last == (size_t)-1) {`;
- every NEXT emitter ends inside that block with `scan_position` at its candidate,
  having re-seeded the state where it re-seeds (`pf_emit_ofs_reseed`, `:6523`).

The block is emitted exactly once, on the generic path or, where `s0` is a scan-edge
head, on the edge path (`emit_scan_loop`'s own comment: "It fires at `s0` and nowhere
else"). Every arrival at state 0 on the generic path re-enters the loop top through
`continue` (state 0 is never a stop state), so every iteration that holds `s0` with
nothing accepted runs the block.

**The record.** The landing row's emitter adds one statement, the block's LAST:
`landing_position = scan_position;`, with `size_t landing_position = search_from;`
declared beside the forward state. So `landing_position` is the position the machine
last stepped from `s0` after a NEXT hand-off: the start of the current EXCURSION from
the start state.

- **One shared site.** All eight NEXT emitters on `CR_DFA` close their block with the
  same `}` line (`pf_emit_memchr` `:6103`, `_bounded` `:6127`, `pf_emit_bcls` `:6145`,
  `_bounded` `:6159`, `pf_emit_ofs` `:6552`, `_bounded` `:6571`,
  `pf_emit_first_memchr_bounded` `:6758`, `pf_emit_first_class_bounded` `:6773`).
  B2 replaces those eight lines with one `pf_close(c, f)` that writes the record
  (when `f`'s RECOVER selection is `landing`) and the brace. That is one site, not
  eight, and a ninth NEXT form cannot be added without it.
- **`next-none` has no block**, so no record: `landing` declines there (§2.6 L4).
  Population: 0 bench and 0 corpus patterns where Λ holds and `end-minus-width` does
  not already take the artifact; witness `(?s).+` (Λ holds, NEXT `none`, not fixed
  width).

### 2.2 The obligation

`landing` is exact iff, on every call that reports a match, today's reverse pass
returns `landing_position`. The reverse pass returns the smallest `s ≥ search_from`
with `[s, e)` a match of the machine's language, where `e` is the forward machine's
reported end. The forward machine reports the priority end of the LEFTMOST start
(its existing correctness; nothing here changes it). So the obligation is:

> **(E)** whenever the forward scan accepts, the leftmost match start at or after
> `search_from` equals the last landing.

### 2.3 The exact condition, and why it is not the built fact

(E) is a property of the pair (the emitted forward machine F with its state ids, the
thread started at the landing). It can be decided at compile time by a product walk:
- explore triples (F's state, the full thread content, the landing thread's NFA set)
  from (`s0`, fresh, `closure(anch_start)`) over all 256 bytes;
- FAIL if F accepts while the landing thread does not;
- FAIL if F reaches state 0 with anything but fresh threads alive.

F's state ids matter, not only NFA content: minimization can map a state that still
carries the landing thread onto state 0. `xa|a` is the witness. After `x`, the state
`{xa·1} ∪ fresh` is language-equivalent to `fresh` (every future accept of `xa`
coincides with one of `a`), so the guard re-runs and the record moves past a live
thread (control in §5.3: 55,152 wrong answers).

That product is the general form, and it is NOT what this design builds:
- **Measured reach (§2.8):** on the bench it adds at most 0.58 ms of weight over the
  one-character fact (1% of the class).
- **Cost:** it needs F's minimized state ids, so it would be a DFA-layer analysis
  rather than an NFA fact, with its own state budget.
- **Utf8:** under the invalid-tolerant contract, an excursion longer than one
  character needs every byte of `[landing, e)` well-formed, not only the first, which
  is a walk again.

### 2.4 The fact Λ, and its proof

**Λ (the one-character fact).** Walk the pattern's NFA (`Job.nfa`, the machine's own
language) from `Nfa.anch_start`, closing over ε EXACTLY (an assertion node is not
passed; reaching one is a decline), and require:
1. `closure(anch_start)` holds no accept (not nullable) and reaches no assertion
   (nothing reads the start edge: no `^`, `\b`, `\G`, lookbehind, `(?m)^`, `\K`
   before the first byte);
2. under an encoding with multibyte characters (the seam's `PCREC_ENCE_DECODE` row
   exists; never `if (utf8)`, DD-12 (7)), no consuming state of that closure accepts
   a continuation byte `0x80-0xBF`;
3. for every byte path that consumes ONE CHARACTER from there, the frontier is
   - empty (dead), or
   - reaches accept on an assertion-free ε-path (UNCONDITIONALLY accepting), or
   - (multibyte only, at most 3 bytes in) still mid-character: every live consuming
     state reads only continuation bytes, and the walk continues.
   Anything else declines: alive-but-not-accepting after a whole character, or an
   assertion before the accept.

Λ holds for `\w+`, `[a-z]+\d*`, `C`, `C+D*`, `C{1,n}`, `.+`, utf8 `.`, utf8
`\p{L}+`, `[a-zé]+`. It fails for `ab` (alive after one character), `x*y`, `\w+@`,
`\b\w+` (assertion at the start), `\w+\b` (accept only behind an assertion), and
`.{3,8}`.

**Lemma 1 (fresh at every landing).** Let `L` be a value of the record. Every thread
alive in F at `L` started at `L`, i.e. F holds only the start closure. *Proof:* by
induction over landings. At the first, the call's forward state is the start state
with no prior thread: Λ.1 implies F is unseeded (the seeds `s1u[u]` and `s1g[u]`
differ only through a left-context assertion in the start closure), so the
initializer writes `s0`. At a later landing `L'`, the previous landing `L`'s thread
consumed one character after `L` and, by Λ.3, then died or accepted. Had it accepted,
F would be accepting, the guard would be false, and no landing would follow. So it
died. Every other thread alive between `L` and `L'` started at a byte after `L` that
the machine STEPPED. By Λ.2 a continuation byte starts nothing. A character-start
byte inside the excursion is impossible under Λ, since the excursion is one
character. So at the character boundary F holds only fresh threads, which is the
start closure, which is state 0, and the guard runs at `L'`. Minimization cannot hide
a live thread here, because there is none: a thread that dies on every completion is
effectively dead and is irrelevant to the answer. Skipped bytes start no match (the
NEXT row's own soundness, `LOWER`), and a re-seeding skip writes `s0` on an unseeded
machine. ∎

**Lemma 2 (the first accept is the landing thread's).** After the last landing `L`,
the first position at which F accepts is one character after `L`, and the accepting
thread started at `L`. *Proof:* by Lemma 1 every thread alive at `L` started there.
Threads started inside the character are at continuation bytes and start nothing
(Λ.2). The landing thread accepts unconditionally at the end of its character (Λ.3),
and it is the only thread that can. ∎

**Theorem.** Under Λ, every call that reports a match reports
`start = landing_position` from today's reverse pass. *Proof:*
- No match starts in `[search_from, L)`: earlier landings' threads died (Lemma 1), and
  skipped bytes start no match.
- A match starts at `L` (Lemma 2), so `L` is the leftmost start.
- The forward machine's `e` is that start's priority end (unchanged code).
- The reverse pass returns the smallest start of a match ending at `e` at or after
  `search_from`, which is `L`. ∎

### 2.5 The utf8 guard (the invalid-tolerant contract)

The proof's step "the landing thread consumes one CHARACTER" assumes the bytes at `L`
form one. Under the default invalid-tolerant contract (`match_api.md`, "an ill-formed
sequence matches nothing") they need not. Witness: utf8 `.` on `C3 61`. The landing
is 0 (`C3` is a lead byte). The landing thread dies at `61`. The fresh thread started
at `61` accepts. F accepts at 2 without returning to state 0. The landing says
`(0,2)`; today's artifact and libpcre2 say `(1,2)`.

**The guard.** Where the encoding has a `PCREC_ENCE_DECODE` row AND the start set
holds a byte ≥ `0x80`, the post-loop block first tests the character at the landing:
```c
if (!<p>_decode(subject, subject_length, landing_position)) {  /* ill-formed */
    scan_position = landing_position + 1; last_accept_position = (size_t)-1;
    forward_state = <s0 cell>; landing_position = scan_position;
    goto <p>_forward_restart;
}
```
Only the FINAL landing's character can be ill-formed with F accepting. An ill-formed
character at an earlier landing either:
- kills every thread (F returns to state 0 and re-lands, Lemma 1's argument), or
- leaves a later thread that becomes the accepting one, which makes it the final
  case.

With the final landing's character well-formed, Λ.3 applies and the Theorem holds.
With it ill-formed, no match starts at `L` (an ill-formed sequence matches nothing),
so the leftmost start is ≥ `L + 1`. Restarting the forward scan there, in the start
state, is exact: the machine is unseeded, so the left context is irrelevant.

The restart is a RAISE re-entry (`locate_finish.md` §2.5: `lo` strictly increases). It
is E5's shape ("a hit the verifier rejects re-enters the scan", `start_table.md`
§1.6). It costs a re-scan of `[L + 1, e)` once per ill-formed landing and nothing on
well-formed text (§5.4: `dot` vs `dot-ng`, no measurable cost). Under `-futf-check`
the guard is dead code (the subject was refused if ill-formed); it is emitted anyway
(D77: no measured need for a second form).

### 2.6 The predicate (`landing`)

```
L1  route CR_DFA                                  (.routes; RECOVER on CR_ATTEMPT is
                                                   stamp-only and leaves at L2.1)
L2  Λ holds  (pcrec_fact_land_char(cx))           (the fact, §2.7)
L3  F unseeded: !dfa_needs_seed(F), s1u[0] == s0,  ASSERTED, not a conjunct: Λ.1
    s1g == s1u                                      implies it (the census: 0 / 3,100
                                                   Λ rows seeded); start_pinned_
                                                   assert_routing's shape
L4  NEXT selected on CR_DFA has a block           read through cand_read (a DAG
    (map EXACT0 / EXACTK; not `next-none`)         edge RECOVER → NEXT; NEXT reads
                                                   only BOUND, so still acyclic)
L5  the ask's hand is END (§4.3)                  rev-end asks with SEED
```
Not a conjunct: empty bodies (`empty` precedes the composite on LOCATE). Not nullable
(Λ.1), so no clash with `pinned`, which needs an accepting start state.

### 2.7 Who computes it

**`src/facts/kset.c`, a new E3 fact `land_char`**, sibling of `kset_walk`. Its
header already states why this is the right place: the thread from the candidate
start ALONE exists only in the pattern's own NFA, walked from `Nfa.anch_start`. It is
sealed on the `ENG_UNANCH` branch after the wrap, where `Job.nfa` is the machine the
forward and reverse DFAs are built from (collapsed or not). The prototype (`proto.patch`,
`lp_land_fact`) is ~100 lines over the same `NState` walk.

It differs from `kset_walk` in one way, and the difference is the soundness
direction. `kset_walk` PASSES assertions: a wider frontier skips less, the safe
direction for a filter. `land_char` makes an EXACT claim, so an assertion is a
decline, never a pass. This is the patfacts design's "one owner per QUESTION" (D120):
the two walks answer different questions on the same NFA. A shared closure helper
with a mode is the build lane's call; a second copy of `wclose` is not acceptable.

Not the DFA: F cannot isolate the landing thread (§2.3's `x*y`/`xa|a`), and the
anchored machine `adfa` is optional (`Dfa.optional`, dropped by the size ladder: utf8
`.` drops it today).

### 2.8 What Λ leaves, measured (the excursion condition is FILED)

On the bench (default config, the auto-caps testee), the rows leave 117 patterns on
`reverse-pass` that carry K3/K4 weight (8.11 ms). Every one was forced through the
LANDING twin in assert mode (`results/twins_residual_forced.txt`):

| outcome | patterns | est. weight | examples |
|---|---|---|---|
| WRONG: the landing is not the start on some tested subject | 34 | 7.42 ms | utf8 `.{3,8}` (2.87 ms: a newline ends the run, the next run starts later), `(a\|)*\d`, `email/orig`, json numbers |
| landing-exact on every tested subject (an UPPER bound for the excursion condition) | 77 | 0.58 ms | utf8 `[\x{400}-\x{4FF}]{4,16}`, `\w+\z`, `\s+$`, `.{80,}`, `in\|instanceof` |
| not twinnable (`next-none`) | 6 | 0.10 ms | `.{8,64}` |

So K4 is, to within 1% of its weight, exactly the Λ class. The excursion condition is
FILED as `[START-LANDING-EXC]` (BOONIES-class, memory `pcrec-high-impact-focus`).
Trigger: a bench cell whose excursion-exact weight exceeds 1 ms. No measurement is
chartered.

**Where to attack §2.**
- (a) Lemma 1's "the guard runs at every return to state 0": a scan form where state
  0 is reached on a path that jumps past the block. The edge path's `goto` to the view
  label is the one to read: under Λ, can a pre-accept head's `scan_next` be `s0`
  with the block on the generic path?
- (b) Λ.2 under `-i` with utf8 caseless folding: a fold that lands a continuation byte
  in the start set.
- (c) The guard's "only the final landing can be ill-formed": a subject where an
  ill-formed lead byte's thread survives into a well-formed character.
- (d) L3 asserted rather than tested: a pattern with an assertion-free start closure
  whose machine is nevertheless seeded (the K50 `N_CSTART` gate sits on the wrap's
  split, not in `anch_start`'s closure; is that always so?).
- (e) A NEXT form whose candidate re-seeds to a state other than `s0` on an unseeded
  machine.

---

## 3. (b) `end-minus-width`

### 3.1 The fact

**`fixed_width`, a second E3 fact in `src/facts/kset.c`:** the frontier walk from
`Nfa.anch_start` with assertions PASSED (they consume nothing, so passing them yields
a superset of paths, and "every path has length W" proved on a superset holds on the
set). `W ≥ 0` iff accept appears in exactly one frontier, at depth `W`, and that
frontier has no consuming state. Otherwise the answer is "not fixed": accept at two
depths, a thread continuing past an accept, or a cycle (the walk exceeds the NFA's
state count). Prototype `lp_fixed_width`, ~30 lines.

**Why bytes, from the NFA, and not `pcrec_cwmin == pcrec_cwmax`.**
- The width the row needs is in BYTES (`start = e − W` is byte arithmetic).
- `pcrec_cwmax` counts CHARACTERS by definition: `A_CLASS` and `A_WCLASS` are 1 in
  every encoding (`src/opt/mrl.c`'s header).
- On the lowered tree it mixes units: a literal `é` is two 1-byte classes (2), but
  `.` is one `A_WCLASS` (1). Utf8 `.` is fixed in characters and variable in bytes
  (1-4), and only a byte walk sees it.
- The NFA is also the language the machines recognise. A count-collapsed prefilter's
  NFA is the collapsed one (`X{m,n}` becomes `X{min(m,1),}`, unbounded, so not
  fixed). An erased lookaround is zero-width either way.

So one walk serves every route, with no separate `Nfa.erased` read.

### 3.2 The row's predicate, and what is exact

```
W1  route CR_DFA
W2  W = pcrec_fact_fixed_width(cx) >= 0
W3  the ask's hand is END (§4.3)
```

**Exact everywhere it applies.** The forward machine hands a VERIFIED end `e`: some
match `[s, e)` exists with `s ≥ search_from`. Every match has exactly `W` bytes, so
`s = e − W`, and today's reverse pass returns that same `s`. This holds:
- under views, seeds and `\G`: no left-context condition is involved, the end already
  satisfied them all;
- under ill-formed utf8: an ill-formed sequence is never part of a match, and the
  match is a path of the byte NFA;
- under `\K` on a hybrid's prefilter (the window start is the ATTEMPT start; `\K`
  moves only the reported one, and the DFA route excludes `\K`).

`W = 0` (`\b`, `(?=x)`, the empty pattern) gives `start = e`. `pinned` precedes it
where the start state accepts invariantly, and the two agree where both apply.

### 3.3 `$`, `\Z`, `\z`, and REVEND

**`$`/`\Z` do not change a width.** They consume nothing. `abc\Z` on `"abc\n"` ends
at 3 (the forward machine's `e`), and `e − 3 = 0`. No interaction on correctness.

**The interaction is REVEND's walk.** In `locate_finish.md` §4.1, `rev-end` "asks
RECOVER" (its walk is RECOVER's reverse block seeded at `n`, `n − 1`, so
`RX_DFA_START` reads `"reverse-pass"` truthfully). That end is SPECULATIVE: the walk
itself is what decides whether a match ends there. If RECOVER's first-match walk
were asked there unchanged:
- `end-minus-width` would answer `n − W` for an end that may not be a match end (a
  WRONG ANSWER on any subject whose tail does not match);
- `landing` has no landing at all.

So RECOVER asks carry a HAND, the mechanism FINISH already has: `CandSel.hand`, one
filter in `cand_select` (`locate_finish.md` §2.2). The composite's ask hands `END`, a
verified match end (the VERIFIER's output). `rev-end`'s ask hands `SEED`.
`end-minus-width`, `landing` and `pinned` take `END` only. `reverse-pass` takes both.
`pinned` already never co-occurs with `end_pin` (revend X3's assertion); its `take`
makes that a declaration, and the assertion stays. This is a general mechanism (the
FINISH filter applied to one more slot), not a REVEND clause. It needs a sabotage
row whose witness is an end-pinned fixed-width pattern on a non-matching tail.

**Population.** 6 bench / 41 corpus `end-minus-width` patterns are end-pinned
(`view` 1/2 in walk_survey's cells). After L2.2 they go to `rev-end`, and these rows
do not apply to them. `landing` has none (`$` is an assertion).

**A sibling, FILED.** An end-pinned fixed-width pattern does not need a reverse walk
either. A match ending at `n` (or `n − 1` under the `nl_last` tie) starts at
`n − W`, and one anchored run of `W` bytes verifies it. As a LOCATE row that is
`AT(n − W)` handed to `FIN3 verify-at`, plus the tie's second point. That is REVEND's
territory: filed there as `rev-end-width`, trigger "a bench end-pinned fixed-width
cell where the walk exceeds 10% of the cell", 6 bench patterns today.

**Where to attack §3.**
- (a) The width walk's cycle test on a machine whose cycle consumes nothing (an
  ε-cycle is closed, not stepped; check).
- (b) A body whose RECOVER end is not a match end of the SAME machine's language:
  hybrid superset prefilters. The reverse machine is built from `rnfa` with the same
  collapse flag; is `Job.nfa` always that language?
- (c) `W` larger than the subject: impossible, given a match exists; the twin's
  find-all covers `e − W ≥ search_from`.

---

## 4. (c) The rows, their predicates, routes, stamps and readers

### 4.1 Order and rows

`cand_rows[]` RECOVER block, first match (spelling of the new fields as
`locate_finish.md` §4.1's; the build lane's):

```c
{ .c = { "pinned", PCREC_NO_START_PINNED, start_pinned_applies },        /* S1, shipped */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "pinned", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = CT_END },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0 } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 1, "pinned" } },
  .u.recover = { .act = CRA_SEARCH_FROM } },
{ .c = { "end-minus-width", PCREC_NO_START_WIDTH, start_width_applies },  /* S2, new */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "end-minus-width", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = CT_END },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0 } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 2, "end-minus-width" } },
  .u.recover = { .act = CRA_END_MINUS_W } },
{ .c = { "landing", PCREC_NO_START_LANDING, start_landing_applies },      /* S3, new */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "landing", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = CT_END },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0, .asks = ASK(CAND_SLOT_NEXT) } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 3, "landing" } },
  .u.recover = { .act = CRA_LANDING } },
{ .c = { "reverse-pass", 0, cand_always }, ...                            /* S4, shipped */
  .take = { [CAND_ROUTE_DFA] = CT_END | CT_SEED },
  .needs = { [CAND_ROUTE_DFA] = { .mach = M_R } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 4, "reverse-pass" } },
  .u.recover = { .act = CRA_REVERSE } },
```

- **`u.recover.pinned` (bool) becomes `u.recover.act`, a four-valued action.** The
  emission dispatch at `:9743` switches on it: the end and start assignments, plus
  the guard for `CRA_LANDING` under a decode row. `dfa_search_is_pinned`'s readers
  split by what they ask:
  - "is R absent?" is §2.7's member fold at L0 (`.needs`);
  - "is the start `search_from`?" is `act == CRA_SEARCH_FROM` (the hybrid's
    bound-not-answer shape, `tests/codegen/run_search_pinned.sh`).
  Today's seven readers are re-classified by grep at B2, never by a comparison of the
  row's name (`start_table.md` [r2 sound-m2]).
- **`end-minus-width` before `landing`.** Where both apply (`\w`, `[a-z]`, `(?s).`),
  they are measured indistinguishable:
  - `\w` on `syntax/t-1m`: 4756/4643 µs (`end-minus-width`) against 4796/4699 µs
    (`landing`), two runs, inside each other's σ (§5.4);
  - `end-minus-width` needs no record, no NEXT block, no guard and no unseeded
    machine, so it is the cheaper row to reason about and to emit.
  `pinned` stays first. Its population must not move (no mover on already-pinned
  artifacts), and it agrees with `end-minus-width` where both apply (`W = 0`).
- **`.needs`** omit R on S1-S3, so §2.7's member fold drops the reverse machine
  (tables, accessor block, stay/scan-edge tables) with no special case, exactly as it
  does for `pinned`. R is still BUILT (`opt5_step2_twopass.md` §8 Q5's compile-CPU
  note applies unchanged; filed with it, BOONIES).

### 4.2 Route coverage

| route | RECOVER asked? | the new rows |
|---|---|---|
| `CR_DFA`, DFA artifact | yes, by the composite | apply |
| `CR_DFA`, a VM hybrid's inlined `<p>_prefilter` | yes, the same emitter (`pcrec_emit_dfa_engine`) | apply; NEUTRAL by window identity (below) |
| `CR_ATTEMPT` | stamp-only until L2.1 drops the route bit; the attempt loop's candidate IS the start | not routed |
| `CR_VM` | no RECOVER slot | — |

**Hybrids: NEUTRAL by window identity, verified, not argued.** The survey argued it
from language identity. §1's identity is stronger: per call, the prefilter's
`window[0][0]` is today's. ASSERT-mode twins of 670 hybrid rows (33 bench, 637
corpus) compared it on 68.4 M prefilter calls (every startpos, the VM's RETRY
recomputes included, since they call the same prefilter): 0 differences (§5.1, §5.2). The superset and collapsed
hybrids are covered by the same argument: Λ and `W` are read from the NFA the
prefilter's machines are built from, and the identity is with that machine's reverse
pass. `locate_finish.md` §1.5's classification: NEUTRAL (no attempt removed).
`locate_finish.md` §7.9 (LR-G14) is subsumed where Λ holds (a `SPAN`, not merely a
`LOWER`) and stays BOONIES elsewhere.

### 4.3 The hand, the deny bits, the listing

- **Hands.** RECOVER's ask carries `CandSel.hand` = `CT_END` (the composite) or
  `CT_SEED` (`rev-end`'s walk, L2.2). This is the FINISH filter on one more slot. It
  is MANDATORY on a RECOVER ask: an ask with `hand == 0` aborts, the FINISH rule (no
  silent default). `CT_END` and `CT_SEED` are new `CT_*` bits, inside the composite
  only; neither crosses the LOCATE → FINISH boundary.
- **Deny bits.** Two deny-only bits, `-fno-start-width` / `PCREC_NO_START_WIDTH` and
  `-fno-start-landing` / `PCREC_NO_START_LANDING` (spellings and bit numbers are the
  manager's). Both are added to `strategy_denials` (masked out of `rx_info.flags`, as
  `-fno-start-pinned` is: no answer moves, so a declined artifact is byte-identical
  under the flag). Under either deny the walk falls to the next row. The bottom of the
  chain is `reverse-pass`, an independently built machine, which is what makes
  `make test-axes`' sweep a control.
- **Listing.** Axis `search-start`: `pinned` 1, `end-minus-width` 2, `landing` 3,
  `reverse-pass` 4, each with its `desc` beside the row.

### 4.4 Stamps, by the rule

- `RX_DFA_START` and `rx_info.search_form` read RECOVER's selected `tok` already
  (`dfa_search_start_name`). RECOVER is asked on every path where these rows can be
  selected, so the two new values fall out with no stamp edit, whether this lands
  before or after L2.1's generated rule.
- `RX_DFA_TABLE`, `RX_DFA_UNIFORM_FOLDS` and `RX_DFA_SCAN_EDGE` fold over L0's
  members. R leaves, so a mover's values can change (e.g. `"mixed"` → `"range"` when
  only R carried the other edge form). These are SELECTION-FACT movers, inside the abi
  event.
- The orientation comment block reads RECOVER's row at L0. Its text moves on movers
  (non-essential comment, inside the event).
- No new stamp. `RX_DFA_PREFILTER` is unchanged: NEXT is unchanged, the record is one
  statement inside its block.

### 4.5 The abi event, and the readers by grep

ONE event, at B2: `PCREC_ARTIFACT_ABI` N → N+1, where N is main's number when B2
lands. It is 71 at this pin, or 72 if REVEND's L2 lands first. Readers, by grep at
this pin (`grep -rn 'PCREC_ARTIFACT_ABI\|ABI_EXPECT\|abi 71'`, then the stamp
values), and the build lane re-runs that grep at its own pin:

| class | readers |
|---|---|
| the abi number | `src/gen/emit_dfa.c:54` (`#define`); `tests/codegen/run_codegen_tests.sh:3042` (`ABI_EXPECT`); `docs/spec/match_api.md:302` (the `#error` example); `tests/mech/sabotages/S693_abi_not_bumped.sh` (anchor `#define PCREC_ARTIFACT_ABI 71`: re-anchor, intent unchanged); `src/gen/CLAUDE.md` (narrative); the identity gate's (B) pin; `match_api.md` §6's abi history (`:205-206`, `:3451`, `:3838` style entries gain one) |
| `RX_DFA_START` / `search_form` values | `docs/spec/match_api.md:786-796`, `:1931-1940`, `:4829-4853` (the value table; the registry anchor phrase "which of two forms the scan entry takes" names a COUNT, so it must change: `tests/registry/axes_registry_check.sh:620` reads it); `docs/spec/tuning.md` §2.19 (`:1760-1840`), `:3872`, `:3915-3930`, `:4005`, `:4073`, `:4288`; `docs/spec/cli.md:623` (the deny list); `lib/pcrec.h:542` (the `search_form` comment) |
| deny-chain expectations (a `-fno-start-pinned` build now falls to `end-minus-width`/`landing`, not `reverse-pass`, on a fixed-width or Λ pattern) | `tests/codegen/run_search_pinned.sh` (`a*` witness: not fixed, nullable, unchanged; re-check its §9 identity sweep), `tests/codegen/cand_oracle_witnesses.tsv:56` (`a?+`: unchanged), `tests/resource/run_resource_tests.sh` (`a{5,25000}`, `(a\|b){5,30000}`: unchanged, neither Λ nor fixed); each re-derived at B2, not assumed |
| byte-count readers (movers shrink: no reverse machine) | the size ladder's measured rungs and `--max-emit-bytes` expectations in `tests/resource/`; `tools/review/out/literal_*.tsv` (generated) |
| the trace and sabotage anchors on the RECOVER rows | `tests/mech/sabotages/S218`-`S222` (anchored on `u.recover.pinned` / `start_pinned_applies` text: re-anchor, intents unchanged), `tests/codegen/run_cand_rows.sh` (`u.recover` member checks) |
| **pcrec-bench (read only; relay through `inbox_from_pcrec.md`)** | `testees/pcrec/adapter.py:801-830` (`dfa_start` CLOSED enum `["pinned", "reverse-pass"]`, checked against `--list-axes` axis `search-start`); `pcrecbench/report.py:763`, `:2542`, `:5641` (the `start=<pinned\|reverse-pass>` legend); `pcrecbench/tests/test_report.py:3533-3600`; `tools/selfcheck.py` fixtures; `tools/trend.py:80` / `trend_snapshot.py:69` (`dfa_start` is a trend META key, so the movers show as stamp changes in the trend) |

**Where to attack §4.**
- (a) A `dfa_search_is_pinned` reader that means "R absent" but is re-keyed to
  `act == CRA_SEARCH_FROM` (or the converse).
- (b) The `hand` filter's totality: for every (RECOVER ask, hand), the last row
  taking it is undeniable. `reverse-pass` takes both; any future RECOVER row that
  takes neither is a self-check failure.
- (c) The mandatory hand on asks that are stamp-only today (RECOVER on `CR_ATTEMPT`,
  on `empty`).
- (d) A machine stamp that folds over R by a path that does not read the members.

---

## 5. (d) Answer identity: hand-twins, controls, timing

### 5.1 Method and the bench population

**The twin is emitter-independent.** `mktwin.py` edits TODAY'S artifact text,
anchored on emitted lines (every anchor asserted):
- it adds the record as the NEXT block's last statement;
- under utf8 it adds the §2.5 guard, with a Table 3-7 well-formedness test written
  in the twin;
- `replace` mode deletes the reverse block;
- `assert` mode keeps the reverse block and counts, per call of the DFA body (a
  DFA artifact's `_search`, or a hybrid's `<p>_prefilter`), the calls whose row
  start differs from the reverse pass's.

**The selection is the PROBE's**, not the twin's. `census.py` runs pcrec built with
`proto.patch` (which prints the facts and selects nothing) and applies §2.6/§3.2's
predicates to the printed facts.

**The driver** (`check.c`, adapted from `studies/revend_twin/check.c`) links the
artifact, the twin and libpcre2 10.46 (utf8: `PCRE2_UTF | PCRE2_MATCH_INVALID_UTF`;
`-i`: `PCRE2_CASELESS`). For every subject it compares every `search_from` in
`[0, n+1]` (subjects over 512 bytes: 64 sampled plus the last 8) and a find-all.
Three pools per row:
- `ex`, machine-derived and exhaustive: one byte per class of the artifact's forward
  machine, plus utf8 tokens for a 2-, 3- and 4-byte character, a lone continuation,
  a truncated lead and `0xFF`; every string up to the length that keeps it under
  40,000 subjects;
- the corpus and edge pool of `studies/revend_twin/mksubj.py`;
- the bench's OWN subjects for the row (throughput first, find-all over the whole
  subject).

**Bench, every design-selected row, both configs** (`results/twins_bench.txt`; 310
(pattern, config) rows; `end-minus-width` 191 DFA + 31 hybrid, `landing` 32 byte +
54 utf8 + 2 hybrid):

| | rows | cells | twin ≠ artifact | DFA-body calls compared | call differences | libpcre2 disagreements (artifact / twin / twin-only) | find-all calls / differences |
|---|---|---|---|---|---|---|---|
| `landing`, byte | 32 | 16,391,036 | 0 | 19,203,458 | 0 | 0 / 0 / 0 | 7,490,332 / 0 |
| `landing`, utf8 (guarded) | 54 | 12,748,380 | 0 | 10,219,260 | 0 | 0 / 0 / 0 | 9,312,862 / 0 |
| `end-minus-width`, DFA | 191 | 53,083,148 | 0 | 17,965,238 | 0 | 14,504 / 14,504 / 0 | 12,243,869 / 0 |
| hybrids (`landing` 2, `end-minus-width` 31) | 33 | 9,296,618 | 0 | 2,742,756 | 0 | 0 / 0 / 0 | 1,270,273 / 0 |
| **total** | **310** | **91,519,182** | **0** | **50,130,712** | **0** | 14,504 / 14,504 / **0** | 30,317,336 / **0** |

The 14,504 libpcre2 disagreements are all utf8 `\B` (`utf8/asr-b-midchar`, `W = 0`)
at an ill-formed subject END: pcrec answers `(2,2)` on `61 C3`, libpcre2 none. That
is K74 (`../dev/known_issues.md`, OPEN, deferred), pre-existing and identical in the
artifact and the twin. The driver's find-all advances to the match end (the
pre-[K75] protocol); it is the same loop on both sides, so the identity holds under
either.

### 5.2 The corpus

`results/twins_corpus.txt` covers every corpus pattern block the design selects, in the
default config: 1,751 rows, of which 1,334 are `end-minus-width` and 417 `landing`. It
uses the same three pools, with two changes: the `ex` pool is capped at 12,000 subjects,
and the third pool is the block's own subjects (walk_survey's synthesized 16 KiB
subjects around each block's match).

| | rows | cells | twin ≠ artifact | DFA-body calls / diffs | libpcre2 (artifact / twin / twin-only) | find-all calls / diffs |
|---|---|---|---|---|---|---|
| all | 1,750 | 169,952,746 | 0 | 143,323,191 / 0 | 43,440 / 43,440 / **0** | 56,164,734 / 0 |
| of which hybrids | 637 | 70,893,458 | 0 | 65,703,299 / 0 | — | 17,892,005 / 0 |

The 1,751st row is NOT-TWINNABLE, because the census read its facts from an abandoned
fit-ladder attempt. `tests/uprops/size_ladder_prefilter_drop.rxt:15`'s final artifact
has its prefilter size-dropped, so it has no DFA body and RECOVER is not asked.
`census.py` now judges by the emitted artifact (report F-L4).

The 43,440 libpcre2 disagreements are all pre-existing and identical on both sides:
- `(()|^){0}[b]` is the documented PCRE2 10.46 optimizer quirk
  (`../dev/upstream_issues.md`; `tests/base/fuzz_regressions.rxt:29`).
- utf8 `$`, `\b` and `\B` at an ill-formed END are K74.
- `(a(b)?)+` and `((?=(a+))a)+` give up on capacity (rc −3) on a 2,000-byte run, where
  libpcre2 answers. A give-up is in-contract.

Bench and corpus together:
- 2,060 twinned rows and 261.5 M cells;
- **193.5 M per-call identity checks, 0 differences**, of which 68.4 M are hybrid
  prefilter calls;
- 86.5 M find-all calls, 0 differences.

### 5.3 Controls that fail (`results/controls.txt`)

Each control plants a fault the harness must see.

| control | what is planted | the failure seen |
|---|---|---|
| `x*y`, `xa\|a`, `ab\|x*y` forced through `landing` (Λ declines them) | a landing on a pattern where a live thread survives a return to state 0 (minimization merges `{xa·1} ∪ fresh` into `s0`) | replace mode: 55,152 / 55,152 / 17,491 twin ≠ artifact on `ex`, each also a NEW libpcre2 disagreement; assert mode: 79,756 / 79,756 / 25,499 call differences |
| utf8 `.{3,8}` forced through `landing` (guarded) | a multi-character excursion under the tolerant contract | 4 call differences (assert), 2 NEW libpcre2 disagreements (replace), e.g. `61 CE 7A 7A 61`: twin `(0,5)`, libpcre2 `(2,5)` |
| utf8 `.`, `\p{L}+`, hybrid `(.)` with the §2.5 guard REMOVED | the ill-formed first character | 3,047 / 2,027 / 3,047 call differences on `ex`, 32 each on the utf8 pool |
| `abcd`, utf8 `é` (W = 2 bytes), hybrid `(\d{4})` with `W + 1` | a width off by one, and in particular characters for bytes (`é`: 1 character, 2 bytes) | every call differs (252 / 44,319 / 77,517) |

Four controls do NOT fail: `ab`, `\w+@`, `\w+\b`, `\b\w+`, `[a-z]{2,}` forced through
`landing`. They are recorded because they are informative.
- `ab`'s run-pinned NEXT row only lands on full occurrences.
- The others satisfy the EXCURSION condition (§2.3): every thread dies together.

They are what §2.8's residual sweep measures at scale.

### 5.4 Directional timing (`results/timing_run{1,2}.txt`, `timing_summary.txt`)

Scratch tier, per the brief's rule:
- Ryzen 7700X, gcc 15.2 `-O2`, `taskset` to one CPU (5, then 9);
- load1 11-12 from other lanes (the box was NOT quiet);
- 3 interleaved repeats × 7 find-all runs per variant (n = 21);
- the bench's own 1 MiB subject;
- span checksum equal on every line.

Median ± σ, µs; "sig" = |Δ| > 2(σ_today + σ_twin):

| cell (form) | run 1 today → twin | Δ | sig | run 2 today → twin | Δ | sig |
|---|---|---|---|---|---|---|
| `\w+` syntax/t-1m (`landing`) | 2517 ± 381 → 1752 ± 106 | −30.4% | no | 2417 ± 689 → 1722 ± 170 | −28.8% | no |
| utf8 `.` utf8/t-1m (`landing`, guarded) | 7854 ± 135 → 4546 ± 142 | −42.1% | YES | 7724 ± 85 → 4469 ± 193 | −42.1% | YES |
| utf8 `\p{L}+` utf8/t-1m (`landing`, guarded) | 5107 ± 102 → 3321 ± 68 | −35.0% | YES | 5072 ± 135 → 3284 ± 82 | −35.3% | YES |
| `abcd` litrun/mat-l4 (`end-minus-width`) | 335 ± 6 → 208 ± 5 | −38.0% | YES | 332 ± 12 → 210 ± 6 | −36.7% | YES |
| `\w` syntax/t-1m (`end-minus-width`) | 7874 ± 124 → 4756 ± 113 | −39.6% | YES | 7860 ± 62 → 4643 ± 84 | −40.9% | YES |
| `\w` syntax/t-1m (`landing`) | 7873 ± 86 → 4796 ± 141 | −39.1% | YES | 7838 ± 93 → 4699 ± 124 | −40.0% | YES |
| utf8 `.` (`landing`, NO guard: the guard's cost) | 7825 ± 91 → 4773 ± 228 | −39.0% | YES | 7773 ± 84 → 4520 ± 195 | −41.9% | YES |

- `\w+`'s σ is one cold outlier (5,497 µs, the first run of run 2; the other 20
  samples are 2,165-2,775 µs). Without it the gap clears the bar. As measured, it
  does not, and is reported so.
- The guard costs nothing measurable (guarded 4546/4469 against unguarded 4773/4520).
- `end-minus-width` against `landing` on `\w`: Δ within σ in both runs.

These agree with walk_survey's twins (−20..−42% on the same cells).

---

## 6. (e) Predicted bench values

`results/predict.txt` (`predict.py`). Inputs:
- the bench's own set-grain pcrec median per cell (walk_survey's `bench_times.py`:
  newest report per set, older pins, Ryzen 1600);
- two predictions:
  - `G/T`, the uniform-per-byte model: an UPPER weight, a reverse byte priced as a
    forward one;
  - `twin`, the measured median ratio (§5.4, both runs averaged), applied only to
    cells whose shape was timed.

Directional only: another box, older pins, a loaded run.

| cell (default config) | row | today | `G/T` | pred. (`G/T`) | pred. (twin) |
|---|---|---|---|---|---|
| utf8/prp-l `\p{L}+` throughput | landing | 11.77 ms | 0.35 | 7.62 | 7.63 |
| utf8/cls-dot `.` throughput | landing | 13.12 | 0.24 | 9.94 | 7.60 |
| utf8/cls-neg-single throughput | landing | 13.04 | 0.24 | 9.93 | — |
| utf8/ci-neg-fold throughput | landing | 13.03 | 0.24 | 9.92 | — |
| syntax/mod-a, syntax/cls-w `\w+` throughput | landing | 7.12 / 7.09 | 0.42 | 4.12 / 4.11 | 5.01 / 4.99 |
| utf8/cls-mixed throughput | landing | 7.98 | 0.34 | 5.26 | — |
| syntax/unp-p-lc, cls-posix throughput | landing | 6.59 / 6.56 | 0.41 | 3.91 / 3.90 | — |
| syntax/unp-p-uc throughput | landing | 5.82 | 0.30 | 4.07 | — |

The two models disagree in both directions:
- on utf8 `.` the twin saves more than `G/T` predicts (the reverse walk over utf8
  costs more per byte than the forward);
- on `\w+` it saves less (the forward scan-edge loop is the cheaper per byte).

Class totals, default config:
- `landing` takes 42.58 ms of the 54.62 ms K3+K4 weight;
- `end-minus-width` takes 3.94 ms;
- 8.11 ms stays on `reverse-pass` (§2.8: 7.42 of it genuinely not a landing).

nocaps: 42.42 + 0.73 of 51.03 ms. The bench's own run on the targeted hardware is the
verdict (D144 addendum 4); this table ranks, it does not predict a report.

---

## 7. (f) The build plan, after L0

`[START-LANDING]` needs L0:
- §2.7's `.needs` and member fold, so R leaves with no stamp edit;
- the `CandSel.hand` field FINISH introduces.

It does NOT need L2.1's generated stamp rule (§4.4). It is ordered after L0 and
otherwise independent of REVEND. If it lands after L2.2, B3 is already done by
REVEND (or REVEND must have done it, §3.3), and the abi number is 72 → 73.

| commit | content | movers | spec | checks |
|---|---|---|---|---|
| **B1** the facts | `land_char` and `fixed_width` in `src/facts/kset.c` (one closure helper shared with `kset_walk`, exact vs passing mode), registered in `facts.def` (E3, `PF_DERIVED` off `kset_walk`'s walk or `PF_CORE`, the facts owner's call), listed by `--emit-facts` | none (no reader) | `docs/spec/facts_listing.md` gains two rows | the census's five-row agreement: the fact against the prototype's printed value over bench + corpus, 0 disagreements |
| **B2** the rows | the two rows; `u.recover.act`; the `pf_close` record; the §2.5 guard (adds `PCREC_ENCE_DECODE` to the mask where emitted); the emission dispatch; `dfa_search_is_pinned`'s readers re-classified; `strategy_denials`; two deny bits; the listing; L3's assertion | **abi event**: every artifact whose RECOVER selection moves (bench 155 + 155 of 734 compiles; corpus 1,751 default / 1,751 nocaps of 9,124) | `match_api.md` (`DFA_START`/`search_form` value tables, the two-forms paragraph `:786-796` becomes four, the abi history), `tuning.md` (§2.19 generalised to the axis with two new deny headings), `cli.md:623` | `emit_sweep` default vs parent: the movers equal the census's selected set exactly; `make test-axes` with both new denies; the identity twins re-run on the BUILT rows (`MODE=assert` against `-fno-start-width -fno-start-landing`); the registry checks |
| **B3** the hand on RECOVER | `CandSel.hand` mandatory on RECOVER asks; `take` per row; `rev-end`'s ask `CT_SEED` (only if L2.2 has landed; else L2.2 carries it) | none | `start_table.md`-level, no caller-visible change | the self-check's totality over (RECOVER, hand); its sabotage row |
| **B4** relay | `inbox_from_pcrec.md`: `dfa_start` gains `end-minus-width` and `landing` (closed-vocabulary event), the abi number, the expected mover cells | — | — | — |

**Sabotage: 9 rows.**
1. Λ widened (alive-not-accept read as accept).
2. Λ's assertion test passed rather than declined.
3. Λ.2 dropped.
4. The record omitted from one NEXT form.
5. The guard dropped.
6. `fixed_width` in characters.
7. `fixed_width` off by one.
8. The RECOVER hand filter dropped (witness: an end-pinned fixed-width pattern on a
   non-matching tail, post-L2.2).
9. `RX_DFA_START` forked from the selection (S222's intent, re-aimed).

S218-S222 are re-anchored, not counted. Each needs a constructed witness that reaches
its site ([MECH-REACH]); §5.3's controls are the starting set.

**Where to attack §7.**
- (a) B2's movers are "the census's selected set": the census reads the PROTOTYPE's
  facts, so B1's agreement check is what makes that a control and not an echo.
- (b) The twins re-run on the built rows. Against what? The deny build's
  independently built reverse machine, not the twin transformer.
- (c) Mover byte counts against `--max-emit-bytes` rungs: a mover that drops R may
  now FIT a rung it did not, which is a fit mover (a different machine set chosen),
  not only a byte mover.

---

## 8. Standing questions (`docs/design/CLAUDE.md`)

### 8.1 The measurement regime — RELEVANT

- **Compile-side, regime-free:** the census and coverage numbers (the prototype's
  facts over walk_survey's populations).
- **Correctness, regime-free:** the identity sweeps.
- **Timing (§5.4), scratch tier:**
  - throughput regime (a dense find-all over the bench's own 1 MiB subjects);
  - independent calls (stateless re-entry);
  - Linux 7700X, gcc 15.2, glibc;
  - a LOADED box (load1 11-12), stated per run with σ and the 2(σa+σb) test.
- **Weights (§6):** walk_survey's older-pin Ryzen 1600 medians, so a ranking, not a
  prediction.

Could another regime flip a decision?
- A short-subject `search` regime shrinks the walk (the reverse pass is bounded by
  the match).
- The rows never add work: the record is one store per landing, the guard one decode
  per reported match.
- So no regime makes them slower. The 2(σa+σb) bar fails only on `\w+` (σ from one
  cold outlier). The ordering decision (`end-minus-width` before `landing`) rests on
  generality, not on a timing.

### 8.2 The independent control — RELEVANT

- **The fact's selection** (the probe) is checked against ANSWERS: the twin is built
  from today's artifact text, not from the emitter, and is compared with the
  artifact's own reverse pass per call and with libpcre2 per cell. Neither the
  probe's predicate nor the twin's form shares a source with the reverse machine.
- **The controls (§5.3)** show the harness sees a wrong landing, a missing guard and
  a wrong width.
- **The population is counted by walk_survey's** `pop_bench.py` / `pop_corpus.py`
  (K35: who counts is named) and joined on `(pid, config)` with its committed cells.
- **After the build:** the deny chain ends at an independently built machine, and
  `make test-axes` with the two denies is the shipped control.
- **[MECH-REACH]:** each sabotage witness in §7 names its site. `next-none`'s
  conjunct has a population of 0 and its witness is `(?s).+`.

### 8.3 What moves when data is regenerated — RELEVANT, little

- No calibration, prior or data file is read. Λ and `W` are per-compile NFA facts.
- What moves on regeneration of the PATTERN (B2's abi event): `RX_DFA_START` and
  `search_form` values, the member-folded machine stamps, the reverse tables and
  accessor block (removed), the orientation comment, the NEXT block's one statement,
  and artifact byte counts (down).
- The study's results move with the tree; nothing reads them.
- A spec change (§7 B2).

---

## 9. Questions for Frank (discussion, each with a leaning)

**Q1. The fact: one character now, the excursion condition filed?**
- *Problem:* the exact condition (§2.3) is a product walk over the emitted machine,
  while the one-character fact is an NFA walk.
- *Forces:*
  - the general form is the house preference (memory
    `pcrec-general-mechanisms-not-special-cases`);
  - its measured extra reach is ≤ 0.58 ms of 54.6 (§2.8), it is a different layer's
    analysis (minimized state ids), and under tolerant utf8 it needs a whole-span
    validity walk.
- *Leaning:* build Λ; file `[START-LANDING-EXC]` with its trigger. Implement-then-
  replace stays open if a cell appears.

**Q2. The tolerant-utf8 guard against an `-futf-check`-only `landing`.**
- *Forces:* without the guard, `landing` on utf8 is limited to `-futf-check`
  artifacts, and the bench does not compile with `-futf-check`, so the two largest
  cells (utf8 `.`, `\p{L}+`, ~10 ms of weight) would be lost. The guard measured
  free (§5.4) and its relocate is an existing edge shape (E5).
- *Leaning:* the guard.

**Q3. RECOVER asks carry a hand.**
- *Problem:* `rev-end`'s walk asking RECOVER is a SPECULATIVE end; taking the
  composite's rows there is a wrong answer (§3.3).
- *Forces:* the hand is FINISH's existing filter on one more slot. The alternatives
  are a `rev-end` clause in two predicates (a special case) or `rev-end` not asking
  RECOVER (its `RX_DFA_START` would then need its own spelling, LR-G4's problem).
- *Leaning:* the hand, built by whichever of `[START-LANDING]` and L2.2 lands second.

**Q4. `end-minus-width` before `landing`.**
- *Forces:* information order says "how much evidence", which puts `landing` (one
  byte) before an end subtraction. Cost is equal (measured). Generality favours
  `end-minus-width` (no record, no NEXT dependency, no guard, works on seeded and
  `next-none` machines).
- *Leaning:* `end-minus-width` second. The survey's and LR-G10's order is the other
  defensible reading.

**Q5. Filing `rev-end-width` (§3.3)** on REVEND's side: an end-pinned fixed-width
pattern needs one anchored run of W bytes, not a walk.
- *Leaning:* file with its trigger; 6 bench patterns.

---

## 10. The lenses

| lens | reading |
|---|---|
| specific vs general | two rows of the existing RECOVER slot, and one general mechanism (the hand) applied to one more slot. The excursion condition is the general fact; Λ is its closed-form case, chosen by measurement (§2.8) |
| core vs derived | both facts are derived from the NFA the machines are built from; nothing new is stored |
| applicable vs assumption-changing | applicable: identity with today's reverse pass, so no answer, attempt or give-up moves |
| fits the architecture vs refactor | fits L0's `.needs`/member fold and FINISH's hand filter; the one refactor is `u.recover.pinned` → `act`, which the third and fourth rows force |
| D124 shared question / engine hat | RECOVER is asked only by the DFA hat (`CR_DFA`), on DFA artifacts and on the hybrid's inlined body alike; the ATTEMPT hat's candidate is its start, and the VM hat has no RECOVER |
| forest for the trees | the RECOVER family is now four rows by evidence (none, the end, the landing, a walk) plus filed siblings: `candidate-verify` (§7.6), `rev-end-width` (§3.3), the excursion condition (§2.8) and LR-G14 (§4.2). A fifth member is a row, not a mechanism |
