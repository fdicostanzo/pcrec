# K82 cause (B): the HANDOFF — the run pre-check's candidate becomes the scan start

**Status: PROPOSED (design only, lane `k82hand`, 2026-10-04, from
`lane/k82fix` `f0d0b206`, abi 60).** Nothing under `src/`, `tests/` or
`docs/spec/` moves here. Frank's ruling (`known_issues.md` K82, "REVISED
2026-10-04", on `litscan_k82b.md`): the T3 handoff is built FIRST, as its own
row after k82fix, light D6 panel first. It fixes cause (B) with no rates and
no threshold. The expected-cost model and its [FINDINGS.B4] reader are parked
behind a census of unbounded-offset runs that still lose after this lands
(§3.3 gives that population).

**LINEAGE — THIS IS FRANK'S 2026-09-22 RECOMMENDATION, RETURNING (added by the manager 2026-10-05 at Frank's request).** On [OPT-REQBYTE]'s landing Frank asked: *"Could it use the position of the REQBYTE to set the search start if it was at a potentially known offset or start back then forward?"* (`docs/dev/plan_completed.md:4715`, the [OPT-REQPOS] FILED clause; journal `docs/dev/dev_journal.md:25059`). It was filed as [OPT-REQPOS] **tier 2** ("BOUNDED offset range ... jump to q − dmax", the same mechanism as this note's lo = c − K). Lane c2prep's census then **DECLINED** tier 2 on population: it covered 6-8% of patterns with TWO losing cells, so it did not clear D77 (`docs/design/reqpos_2b.md:14-31` and its population table at `:77`; ratified with the 2b BUILD at `:791-794`, "BUILD 2b / DECLINE tier 2"; row closed 2026-09-26 with tier 2 still declined). The VM-route half was re-opened 2026-09-25 as [OPT-VMSEED] (`docs/dev/plan.md`, "[OPT-REQPOS] tier 2's re-opening"; Frank: "vm is important when caps, etc are on so it matters") and as [ENG-TACTICS] tactic (c), "REVERSE-THEN-SKIP (Frank's shape)". Both are unscheduled. **What is different now:** C3 (abi 59) made the discarded candidate a measured LOSS rather than a missed gain. The K82 cause-(B) cells lose up to +0.70 ns/B to the rescan (mod-i 1.39 vs 0.76 ns/B with the gate off; T3 twin 0.81), and the population is 47 bench / 160 corpus movers (§3.3), not 6-8% with two losing cells. This note is the DFA-route (and hybrid first-call) instance of tier 2. [OPT-VMSEED] remains the VM-route instance; Q7 here files it rather than building it.

**SECOND LINEAGE — D122 item 3, "CARRY VERIFIED FACTS FORWARD" (Frank, 2026-09-25, `docs/dev/decisions.md:8314-8319`):** *"a prefilter or pre-pass that verified a literal at a candidate knows things the matcher then re-checks — e.g. the DFA can enter at δ*(s0, run) instead of s0 and skip re-reading the run; the VM can resume after the literal; bounds checks covered by the verified span are dead."* Built so far for ONE fact only, the dominated pre-check's elision (R10, `docs/design/patfacts/inventory.md:592`). The VM-resume and dead-bounds-check halves sit in [OPT-VMLIT], STATE:not-started. The reverse-DFA forms are [ENG-TACTICS] tactics (b)/(c), unscheduled. The handoff is the narrowest carried fact, "no match starts before c − K", consumed as a start bound. D122(3)'s richer facts (enter at δ*(s0, run), skip re-verifying the run) remain open and compose with it.

**REVISION 2 (lane `k82hrev`, 2026-10-04): the light D6 panel r1
(`../dev/reviews/2026-10-04-r1-k82-handoff.md`, two critics, 17 findings,
all ACCEPTED by the manager) is applied in place.** Each change is marked
`[r1 <id>]` where it lands; §R maps every finding to the section that now
answers it. The mechanism survived measurement (~60 shapes, 0 diffs at
every startpos against today's artifact and libpcre2). What moved is the
contract the mechanism leans on and the checks: the gate's RETURN VALUE is
now load-bearing (§1.1a), the give-up allowance narrows to count-collapsed
prefilters (§4.2), the hybrid's prefilter is a third `\G` reader (Claim 2′),
verbs and callouts decline (§1.4 (g)), the utf8 round-up is an uncapped
loop taken only when `lo > f` (§1.4 (e)), the abi and byte-count readers are
enumerated by grep (§2.3a), and every sabotage row has an in-suite detector
and a constructed reaching witness (§4.4). The Frank questions are revised
(§Q); Q3's recommendation is reversed.

Instruments: `../dev/optloop/s4/k82hand/` (its own `CLAUDE.md`):
- `proto_maxoff.diff`: a prototype of the §1.3 offset derivation, used only
  to count;
- `k82h_census.py` / `k82h_census.out`: the predicted-mover census.
- `k82h_census_r2.py` / `k82h_census_r2.out` ([r1 C-C8], [r1 C-C9]): the
  same classifier over two more corpus configs and over the corpus's
  budget/give-up blocks.

Timings quoted are k82cost's twin T3 on the Mac (`../dev/optloop/s4/
k82cost/t3_mac.out`). They are DIRECTIONAL (D144 addendum 1). Linux figures
are r1alpha's (`../dev/lanes/r1read_report.md` §3).

## 0. Findings first

1. **The handoff is a startpos advance, and its soundness reduces to two
   facts the tree already relies on.**
   - The first is the artifact's own every-startpos contract, which the
     identity gates sweep.
   - The second is one new core fact: a BYTE bound K on where the run's
     window sits after the attempt start.
   - With c the gate's first window hit at or after `search_from`, no match
     attempt in `[search_from, c − K)` can succeed (§1.2). So the body may
     begin its scan at `lo = max(search_from, c − K)` and answer exactly
     what it answers at `search_from`.
   - `\G` is the one construct that reads the startpos as more than a lower
     bound. It keeps reading `search_from` (§1.2, Claim 2′).
2. **All five cause-(B) cells are in the population, four of them at K = 0.**
   The prototype derivation over the bench exports gives:
   - `mod-i`, `mod-r`, `cls-fold-pair` and `cls-pair-ctl`: K = 0.
   - `ci-strasse`: K = 2, not 1. Under `-e utf8`, `(?i)s` folds with
     U+017F `ſ`, which is two bytes, so the run `TRA` can sit two bytes after
     the start. **The bound must be BYTES on the lowered tree.**
     `pcrec_cwmax`, which counts characters (`A_WCLASS` = 1), would
     under-count it, and that error deletes matches. This is hazard H2 and
     sabotage S464.
3. **The predicate is structural:** a run pre-check is emitted, a DFA scan
   is in front (the DFA unanchored or attempt body, or the VM hybrid's first
   prefilter call), and K is finite.
   - Bench (345 exports, auto): **47 distinct program movers** (49 rows).
   - Corpus (auto): **160** (209 rows).
   - Forced-VM configs: 0 movers. That route has no scan to move, and
     K65/K66 own it.
   - Unbounded and therefore unreachable: 8 bench and 37 corpus artifacts
     on a DFA-scan route. `union-select` is the only C3 customer among
     them, and it keeps its discard gate unchanged (§3).
4. **The handoff program does a SUFFIX of the discard program's work.**
   - The gate is unchanged.
   - The engine's scan starts at `lo ≥ search_from` and not at
     `search_from`.
   - The only added work is one subtraction and compare per PASSING call,
     plus, under `-e utf8` and only when `lo > f`, a boundary round-up. It
     is ≤ 3 byte tests on well-formed text and unbounded only by `n` on
     ill-formed text ([r1 S-F5], §1.4 (e)).

   So against abi 60 no measured cell can regress past the floor except
   through code placement. Against DENY (abi 58, no run gate) the residual is
   the gate's own scan of `[search_from, c]` against the engine prefilter's
   scan of the same bytes. That is `mod-i`'s +0.05..+0.18 ns/B pair-arm
   overshoot on the Mac, a separate emission item (§5 H11).
5. **It is a NEW two-row first-match table, not a row of `req_admits[]` and
   not a row of `dfa_pfs[]`.**
   - `req_admits[]` answers WHETHER and WHAT to pre-check.
   - `dfa_pfs[]` answers how the forward machine finds its next candidate
     INSIDE the loop.
   - This table answers what the body does with the pre-check's answer:
     discard it, or begin there.
   - It composes with every row of both, and three bodies read it.
   - Deny `-fno-req-handoff` (bit 46, the next free bit after k82fix's 45).
   - It is an abi event, 60 → 61, with a new `<PREFIX>_REQ_HANDOFF` stamp
     (§2). [r1 C-C1] The stamp is proposed ONLY on artifacts where the
     handoff applies, which confines byte movement to the program movers
     (§2.2, §2.3a, Q3).
6. **[r1 S-F1] The handoff makes the gate's RETURN VALUE load-bearing.**
   Today only "found / not found" matters, so a gate that returns a LATER
   occurrence is invisible. Under the handoff it deletes matches: critic 1
   sabotaged it and got 6,549 of 18,052 cells wrong. The gate's contract
   (leftmost masked occurrence ≥ `search_from`) is now written down (§1.1a)
   and has its own sabotage row (S464).

## 1. The mechanism

### 1.1 What is handed off

Today (abi 60) the run pre-check is emitted by `emit_req_run_check`
(`src/gen/emit_dfa.c:1145`) as

```c
    if (rx_reqrun(subject, subject_length, search_from) >= subject_length) return 0;
```

`rx_reqrun` (`ofs_test_emit_fn`, the one search block) returns `c`. That is
the first position at or after `search_from` where the run's WINDOW begins:
every position passes the masked compare, and on the pair arm a candidate is
returned only after its verify. If there is no such position it returns `n`.
The candidate is thrown away. The handoff keeps it:

```c
    size_t handoff_position = rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return 0;
    /* [K82] every match begins at most K bytes before its run window ... */
    if (handoff_position - search_from > K) {
        handoff_position -= K;
        /* utf8 only: round UP to a character start (§1.4 (e)) */
        while (handoff_position < subject_length && !(START(handoff_position))) handoff_position++;
    } else
        handoff_position = search_from;
```

The subtraction is written so it cannot underflow: `c ≥ search_from` always
holds, and `search_from + K` would overflow near `SIZE_MAX`. At K = 0 the
`-= K` line is not emitted, and the test reads `> 0`. The local's name
carries no prefix (K79: the emitters never see the caller's prefix).

[r1 S-F6] The round-up sits INSIDE the `lo > f` branch. When the handoff
leaves `lo == f`, `lo` is the caller's own startpos and is used unrounded,
exactly as today. Rounding there would change behaviour under
`-fno-startpos-guard`, where a mid-character startpos is the caller's
declared choice and today's artifact scans from it as given.

[r1 S-F5] The loop is UNCAPPED, bounded only by `< subject_length`. That is
the SEEK primitive's own shape (§1.4 (e)). Revision 1 said "≤ 3 tests",
which holds only on well-formed text: a subject with four or more stray
continuation bytes in a row needs more, and a capped loop would hand the
body a non-start. `START(p)` here stands for the encoding backend's start
predicate (§1.4 (e)), never a spelled test.

### 1.1a [r1 S-F1] The gate's contract: the LEFTMOST occurrence at or after `search_from`

Claim 1 (§1.2) reads `c` as the LEAST `q ≥ search_from` with a masked
occurrence of `W`. Today nothing checks that, because the discard program
uses only `c < n`. A gate that returns a LATER occurrence, or an occurrence
before `search_from`, answers today's question correctly and silently
deletes matches under the handoff. Critic 1 planted "the gate returns the
second occurrence" and measured 6,549 wrong cells of 18,052.

So the build writes the contract into `ofs_test_emit_fn`'s header comment,
and the one search block it renders owns it:

> `rx_reqrun(s, n, from)` returns the least `q ≥ from` at which every
> position of the window passes its masked compare, or `n` when there is
> none. A caller may use the returned position, not only its comparison
> with `n`.

What this binds:
- **The pair arm.** It leapfrogs two `memchr` streams and verifies each
  hit. It must return the LESSER verified candidate, never the one from
  the stream it advanced last. The `fresh = 1` re-search per call (H11)
  is what makes the lesser one the least `≥ from`: no stale stream
  position from a previous call can sit below `from`.
- **Future arms.** Any later run-compare arm that renders through
  `ofs_test_emit_fn` is bound by it: [MEMFN]'s fused scan+verify twins
  (R1d), and S4's `pcrec_emit_run_compare` rows when they render a search
  rather than a compare. A twin that returns "some occurrence" is a
  correct discard gate and an incorrect handoff gate. The [MEMFN] build
  lane's brief must name this contract.
- **The check.** Sabotage S464 (§4.4) plants the later-occurrence gate.
  `handoff.rxt`'s dense find-all rows and a new two-occurrence row detect
  it: there the first occurrence is the match's own window and a second
  occurrence follows it, so a later-occurrence gate starts the scan past
  the match. (The decoy rows cannot detect it. Their first occurrence is
  the decoy, and the later one is the match's.)

The three consumers each read `handoff_position` in place of
`search_from` at exactly ONE site:

| body | today | with the handoff |
|---|---|---|
| DFA unanchored (`emit_unanchored`, caller-facing entry; `emit_dfa.c:8144` + the forward seed) | `size_t scan_position = search_from;` and the seeded initializer `search_from ? seed[class[subject[search_from - 1]]] : s0` | `scan_position = handoff_position;` and the initializer reads `handoff_position` (§1.4 (c)) |
| DFA attempt (`emit_attempt`, `emit_dfa.c:8638`) | `for (start = search_from; start <= start_max; start++)` | `for (start = handoff_position; …)`. The `\G` dispatch `start == search_from` is UNCHANGED |
| VM hybrid (`emit_vm.c:13398`, the FIRST prefilter call) | `if (prefn(subject, subject_length, search_from, window) != 1) return 0;` | `prefn(subject, subject_length, handoff_position, window)`. The VM's `search_from`, which `\G` reads, is unchanged. [r1 S-F3] The prefilter's own `\G` reads its THIRD argument, so inside this one call it reads `lo` (Claim 2′) |

Everything else in each body still reads `search_from`:
- the K73/K50 start guards (they already ran, above the gate);
- the end-window clamp (also above the gate);
- the reverse pass's lower bound `rewind_position > search_from`, which is
  sound either way (§1.2, note);
- the VM's retries, which call the prefilter at `attempt_position`.

**Find-all.** There is no cross-call state, because the matcher API is
stateless (`match_api.md` §3.1). Each call's own gate searches from its own
`search_from`: the previous end, or `next_pos(end − 1)` under utf8 after K75.
So each call hands off its own candidate, and its work is the gap to the
next run occurrence plus the engine's scan from about that occurrence to the
match end. Nothing is re-used, and nothing needs to be. The pair arm's
`fresh = 1` re-search of BOTH streams per call is untouched. That is
`mod-i`'s residual (k82diag §1.B, 4.8x the subject) and its own item (H11).

### 1.2 Soundness: the invariant and its proof sketch

Notation:
- **Subject and startpos.** The subject is `s[0..n)`, and `f` is the
  startpos as the body sees it at the gate (after the K73 seek and the
  end-window clamp).
- **Attempt start.** An ATTEMPT START is a position `p ≥ f` at which a
  match attempt begins. That is the thread start, NOT the reported start:
  under `\K` the two differ, and every offset below is measured from the
  attempt start.
- **The window.** `W` is the run's emitted window, `req_run`'s
  `bytes`/`mask`/`len`. A masked OCCURRENCE of `W` at `q` means
  `(s[q+i] & mask[i]) == bytes[i]` for every `i < len`.

**The fact (§1.3), INVARIANT F.** For every pattern P whose
`req_run_maxoff` is a finite K: every successful attempt at any `p`
contains a masked occurrence of `W` at some `q` with `p ≤ q ≤ p + K`.

**Claim 1 (no early success).** Let `c` be the gate's answer: the least
`q ≥ f` with a masked occurrence of `W`, or `n`. Then no attempt at
`p ∈ [f, c − K)` succeeds. If `c = n`, no attempt succeeds at all (today's
NOMATCH).

*Proof.* Suppose an attempt at `p ≥ f` succeeds. By F it has an occurrence
at `q ∈ [p, p + K]`. Because `q ≥ p ≥ f`, `q` is a candidate for the gate's
minimum, so `q ≥ c`. Then `p ≥ q − K ≥ c − K`. ∎

The `q ≥ p` half is what makes the window's FIRST hit at or after `f` the
right anchor. It needs every byte of the run to lie inside the match's
consumed text. `req.c` already guarantees that, because a lookaround's body
is never descended into (its header says why), and a lookbehind's bytes are
the one way a run could sit before `p`.

**Claim 2 (startpos advance).** Suppose P reads the startpos only as the
lower bound on attempt starts, which holds for every `\G`-free pattern.
Then the PCRE2 answer at startpos `f` equals the answer at any
`f′ ∈ [f, p*]`. Here `p*` is the least successful attempt start `≥ f`; when
there is none, `f′` may be anything.

*Proof.* The answer is the attempt at `p*` with that attempt's preferred
end. An attempt's success and its end depend on `p` and on the whole subject
(lookbehind and `\b` read before `p`, and PCRE2 lets them read before the
startpos), never on `f`. Attempts starting `≥ f′` have the same least
success `p*`. ∎

**Claim 2′ (`\G`).** Where P contains `\G`, an attempt's success also reads
`f`, but only through the `\G` test. Run the attempts `p ≥ lo` with the `\G`
anchor still at `f`, and the set of successful attempts `≥ lo` is unchanged,
so the least one is too. That is why every consumer keeps `search_from` as
the `\G` reference and moves only its scan start. ENG_ATTEMPT spells the
two variables separately already (`start` and `search_from`). The VM hybrid
does too (`attempt_position` and `search_from`). The DFA unanchored body has
no `\G` start family: ENG_UNANCH implies no `N_GSTART`, which is the
premise `start_pinned_assert_routing` (`emit_dfa.c:7119`) asserts for the
pinned form. The build asserts the same premise for every handoff body
(§1.4 (d)).

**[r1 S-F3] The THIRD `\G` reader: the hybrid's static prefilter.** It is
an ENG_ATTEMPT-shaped DFA function, and its `\G` dispatch is `start ==`
its third argument. The hybrid's first call passes `lo` there, so for that
call the prefilter's `\G` tests `start == lo`, not `start == f`. That is
sound, and the argument is short:
- When `lo == f` nothing changed.
- When `lo > f`, a `\G` branch can succeed only at `p = f`, and Claim 1
  rules out every success below `lo`. So no true match is lost.
- The prefilter may now ADMIT a start at `lo` through a `\G` branch that
  the VM, still anchored at `f`, rejects. That widens a superset filter,
  which the VM's verify absorbs (D51 ruling 2's direction).
- This is not a new exposure. The VM's RETRIES already call the prefilter
  at `attempt_position` (§1.1's list), so the prefilter's `\G` has read
  `search_from` on the first call only, ever. The handoff makes the first
  call read the way every retry already reads.
- The one read that is not a filter is `window_end` on the clamped arm
  (H8): it is set from the prefilter's first ANSWER. A spurious `\G` answer
  at `lo` could end earlier than the true match. The build therefore
  DECLINES the handoff on a hybrid that has both a `\G` start family and
  the clamped window arm (`mrl_win`), by conjunct (d′) in §1.4. Its
  measured population is zero: no census hybrid mover carries `\G` (§3.1a).
  Q9 asks whether the decline can drop once the build reads whether
  `window_end` is re-derived per prefilter answer.

Critic 1 measured the unguarded form at 0 diffs over 7 `\G` hybrid shapes
(~280k cells). `handoff.rxt` gains a `\G`-hybrid prefilter-window row on a
constructed witness, `(?:\Gab|x)(cat)dog` (VM hybrid, `exact` prefilter,
K = 2 on the prototype; on `zzabcatdog` from 0, `lo` = 2 and the true
answer is NOMATCH, while a `\G` anchored at `lo` would match `(2,10)`),
and S469's plant and §5.12's "no `\G` reader" check
extend to the prefilter's third argument (§4.4).

**Claim 3 (the body is correct at `lo`).** The emitted body's answer at a
legal startpos is the PCRE2 answer. That is the artifact contract,
`match_api.md` §3.1. `tests/utf8/run_startbnd_diff.sh` and the identity
gates sweep it at every startpos.
- Under `-e byte`, every position is legal.
- Under a multibyte encoding, only character starts are legal (K50 refuses
  the others). So `lo` is ROUNDED UP to the next character start before it
  is used (§1.4 (e)). That keeps Claim 1's conclusion, because a
  continuation byte is never a match start (`match_api.md` §3.1, K73/K75),
  and it makes `lo` a startpos the contract covers.

[r1 S-F9] **Claim 3 turns every-startpos correctness from a contract into a
load-bearing path.** Today a body bug that shows only at startpos `x > 0`
is reached only by a caller who passes `x`. Under the handoff it is reached
whenever `c − K = x`, on an ordinary call from 0. So every route the
predicate admits (DFA unanchored, DFA attempt, VM hybrid) must pass the
every-startpos sweep over its movers, not only the identity gates' corpus:
§4.2 item 1's differential runs every mover at EVERY start position, per
route, and reports the per-route counts (a route with zero swept movers is a
failure, K35). Cross-note for [UCP] U3/U4: their seeded context reads the
previous CHARACTER, which is multibyte under utf8. Because `lo` is always a
character start (or `f` itself, S-F6), the context at `lo` is the one a
caller's startpos `lo` gets. So U3/U4 inherit the handoff for free if they
are correct at caller startposes, and their own every-startpos sweep must
include the handoff movers.

**Theorem.** With `lo = f` when `c − f ≤ K` and `lo = round_up(c − K)`
otherwise ([r1 S-F6]), the handoff body's answer equals today's. By Claim
1, `p* ≥ c − K`. Also `p* ≥ f`, and `p*` is a character start, so
`p* ≥ lo` in both cases. Claims 2/2′ then give answer(f) =
answer(lo), and Claim 3 says the body computes answer(lo).

**One emitted detail the theorem does not cover by itself.** The DFA
reverse pass keeps `rewind_position > search_from`, so it could in
principle walk below `lo`. It cannot stop there. A start it finds is a `p′`
with `[p′, e)` a match, which makes `p′` a successful attempt, so
`p′ ≥ c − K` by Claim 1. Keeping `search_from` there moves no emitted byte
on that line.

**What the proof does NOT need.** No anchoring or view assumption, no `\b`
or lookbehind exclusion, and no prefilter shape. The context at `lo` is the
same context a caller's startpos `lo` would have. The seeded initializer
already computes it from `subject[lo − 1]` (§1.4 (c)). The offset-set
prefilter's landing (`pf_emit_ofs_reseed`) is exactly this computation one
row over.

### 1.3 The fact: the run window's maximum byte offset from the attempt start

**Where.** It is a new accumulator on `src/facts/req.c`'s one walk (`rb_walk`),
the walk that already produces the run. It is not a second walk and not a
re-spelling, because only the walk knows WHICH occurrence its run came from:
- `best` (`rn_better`) can come from a left factor, a right factor or a
  join;
- head and tail runs come from opposite ends of the subtree.

`reqpos_probe.c` (cycle 2's census instrument, `run_pmax`) computed the same
quantity for exact runs by re-spelling the walk, and its header records
what that cost.

**The arithmetic.** It is in BYTES on the LOWERED tree, with
`pcrec_sat_add`/`pcrec_sat_mul` and `PCREC_W_UNBOUNDED` as the one
"unbounded". It does NOT use `pcrec_cwmax`, which counts characters. On the
lowered tree an `A_WCLASS` is one character over a byte child of up to four
bytes, so `cwmax` would under-count (finding 2). The walk takes each node's
byte width from its own arms:

| node | `maxw` (bytes) | run offsets |
|---|---|---|
| `A_CLASS` (lowered: one byte) | 1 | `rr_pos`: head = tail = best at 0 |
| `A_CAT` (`l` then `r`) | `maxw(l) + maxw(r)` | head 0; tail `maxw − tail.n`; `l.best` as is; `r.best` + `maxw(l)`; the join `l.tail ++ r.head` at `l.tail`'s offset |
| `A_ALT` | max of the branches | common head at 0; common tail at `maxw − tail.n` |
| `A_REP {m,M}`, `m ≥ 1` | `M × maxw(body)` (`M = −1` → unbounded) | `best` = the body's, at its offset: the FIRST iteration begins at the repeat's start |
| `A_REP`, `m == 0` | `M × maxw(body)` (the body is walked for its width alone) | none |
| `A_CAP`, `A_ATOMIC`, `A_WCLASS` | the child's | transparent |
| zero-width kinds (`A_EMPTY`, `A_BOL`, `A_EOL`, `A_END`, `A_CTX`, `A_GSTART`, `A_KRESET`, `A_LOOK`) | 0 | none |
| `A_BREF`, `A_VAR`, `A_CALL` | unbounded | none |

**Why these offsets hold.**
- **Head.** A head is a guaranteed PREFIX, so its offset is 0 in every
  match.
- **Tail.** A tail is a guaranteed SUFFIX, so it starts at
  `len(match) − n ≤ maxw − n`. That holds after truncation too: `rn_pre`
  keeps the last bytes, so the stored tail still ends at the subtree's end.
- **A truncated head.** `rn_app` keeps the first bytes, so the offset is
  unchanged.

**The run CHOICE does not move.** The offset is an annotation: `rn_better`
still ranks by information alone. A run at a bounded offset is not
preferred over a more informative unbounded one. That would be a selection
change with no measured need (D77), and it would move every C3 artifact.

**Window.** `pcrec_req_window` cuts `bytes = whole + at`, so the window's
bound is `K = whole_maxoff + at` (saturating).

**The record ([PATFACTS], D126).**
- `ReqRun` gains `whole_maxoff`, the core half, set beside
  `whole`/`whole_len` in `pf_derive_req_walk` (`facts.c:172`).
- It also gains `maxoff`, the derived half, set beside `at` in
  `pcrec_req_window`.
- `--emit-facts` gains one derived row, `req_run_maxoff` (E2,
  `depends req_run`, owner `src/facts/req.c`, no deny of its own). Its
  value is `<K>`, or `unbounded`, or `none` where no run shipped.
- `req_whole_run` and `req_run` keep their value text. They render the
  `<PREFIX>_REQ_RUN` stamp (`litscan_s4.md` §2.3.5), so adding to them
  would make every run-bearing artifact a stamp mover for nothing.

**Prototype.** `proto_maxoff.diff`, about 60 lines of `req.c`, is the
table above, minus the record plumbing.

| pattern | `-e` | K |
|---|---|---|
| `(?i)cat` | utf8 | 0 |
| `(?i)straße` | utf8 | 2 (`ſ`) |
| `x{2,5}(?i)cat` | utf8 | 5 |
| `.{3}cat` | utf8 | 12 |
| `é{2}cat` | utf8 | 4 |
| `ab(?:cdef\|xyzdef)g` | utf8 | 5 |
| `(?:a\|bb)?catdog` | utf8 | 2 |
| `(?:éx\|ʩx)` | utf8 | 1 (a run that begins on a continuation byte) |
| `(?:ab\|c)(?i)select` | utf8 | 4 |
| `\w+cat`, `a.*?(?i)select` | utf8 | unbounded |

The prototype's run equals the shipped `req_whole_run` on every row it was
read against, because the choice is untouched. The build lane's check is
the same comparison over the whole census.

### 1.4 The exact predicate

The table is asked only where the admission emitted a run pre-check:
`req_admit` is `EMITTED` or `SET_LEADS`, and `req_run.len ≥ 2`. Its
`handoff` row applies iff all of the following hold:

- **(a) A scan to move: `pcrec_artifact_has_dfa_scan(cx)`.** This is G1's
  own premise, read from the same predicate, never restated.
  - It covers the DFA unanchored body, the DFA attempt body, and the VM
    hybrid.
  - The VM with NO DFA scan is excluded. Its pre-check is K65/K66's
    linear no-match proof, and skipping its attempts (sound by Claim 1)
    has no measured customer: 0 movers in the forced-VM census.
  - A VM `attempt_position` advance would also need K49's
    encoding-advance discipline. It is filed, not built (§Q Q7).
  - The build asserts the correspondence at the hybrid site: on a hybrid
    with no `prefn`, the predicate is a `pcrec_ctx_fail`.
- **(b) A bound: `req_run.maxoff < PCREC_W_UNBOUNDED`.** A saturated finite
  value reads as unbounded, which is the safe direction.
- **(c) The body's start is a variable the table can move.** It must not
  be the pinned form (`emit_unanchored`'s `pinned`, OPT-5 step 2). There
  the answer is "the match began at `search_from`" by construction.
  - A pinned machine's start state accepts unconditionally, so the pattern
    is nullable and has no necessary run. So (c) is UNREACHABLE.
  - The build makes it a `pcrec_ctx_fail` beside the existing
    `start_pinned_assert_routing`, not a silent conjunct.
  - On the seeded forward machine the initializer reads the moved start,
    through the same `seed_emit_seeded` text (`emit_dfa.c:5459`). It is
    one writer, so `pcrec_dfa_scan_state_written` (scanedge precondition
    (8)) answers as it does today. It is NOT a second reseed after the
    initializer, which would be a second writer of the state variable.
- **(d) `\G`.** No conjunct: Claim 2′. Beside
  `start_pinned_assert_routing`'s own `s1g` loop (`emit_dfa.c:7119`), the
  build asserts that an unanchored machine carrying a handoff has no `\G`
  start family. That is the same premise asked of a second body shape, and
  it is a loud internal error if it ever moves.
- **(d′) [r1 S-F3] Hybrid, `\G` and the clamped window.** On the VM hybrid,
  decline when the program has a `\G` start family AND the prefilter's
  window arm is clamped (`mrl_win`). Claim 2′ gives the reason. Measured
  population: 0 movers.
- **(e) Encoding.**
  - Under `byte`: nothing.
  - Under a multibyte encoding: `lo` is advanced to the next character
    start through the encoding BACKEND's start predicate. That is the
    predicate `pcrec_emit_start_zero`'s SEEK arm already renders
    (`if (pos == 0 && !(P)) do pos++; while (!(P));`, `emit_dfa.c:876`),
    applied here without its `== 0` clause. The build either generalizes
    that one primitive over its position variable or adds a sibling mode
    to it. It never spells a second predicate. DD-12 (7) applies: no
    encoding test in shared emitter code.
  - The advance never passes `p*`: `p* ≥ c − K` is a character start, so
    the first start at or after `c − K` is at most `p*`. (Revision 1 said
    "never passes `c`'s own character start", which is false when the run
    begins on a continuation byte, `(?:éx|ʩx)`; `p*` is the bound that
    holds.)
  - [r1 S-F5] It is NOT bounded by the encoding's maximum sequence length.
    On well-formed text it takes at most 3 steps; on ill-formed text (a run
    of four or more stray continuation bytes, the K75 "stray" kind) it
    takes as many as there are. The loop is uncapped, `< subject_length`
    being its only bound, which is the SEEK primitive's shape.
  - [r1 S-F6] It runs only when `lo > f`.

  This conjunct is not a refusal. It is the one encoding-dependent line of
  the emission (§Q Q2 asks whether it can be dropped).
- **(g) [r1 S-F4] No verb and no callout.** A backtracking verb in a FAILED
  attempt below `lo` can end the whole search under PCRE2 (`(*COMMIT)`:
  the attempt fails and no later start is tried). Skipping that attempt
  would then turn a NOMATCH into a match. So the predicate declines on any
  verb or callout node in the pattern. It reads the same fact
  [OPT-HYB-RESEED]'s callouts/verbs decline reads (`hyb_reseed.md` §6,
  lane reseedfix), never a second spelling of it. Today the conjunct is
  structurally unreachable: `(*COMMIT)` is refused ("outside pcrec's
  scope") and `(?C1)` is refused by module `callouts` ("not implemented
  yet"), both measured on the prototype. So its sabotage row ships
  declared UNREACHED (S475, §4.4), and the build adds a compile-time
  assertion beside it, on S219's precedent.
- **(f) Not denied:** `-fno-req-handoff`.

**Not conjuncts, and why.**
- **Anchors, `$`/`\z` views, `\b` and lookbehind.** These are context. The
  initializer at `lo` computes the same context a caller's startpos `lo`
  would get (Claim 3).
- **`\K`.** The offsets are from the attempt start (§1.2).
- **The end-window clamp.** It runs above the gate, so the gate's
  `search_from` is the clamped one.
- **G2's one-attempt routes.** They emit no pre-check, so the table is not
  asked.
- **`set-leads`.** Its byte check is a discard check that runs first. The
  run search after it is the one handed off.

## 2. Where it slots

### 2.1 A new first-match table, `req_uses[]` (axis `req-use`)

| # | row | deny | predicate | emitted |
|---|---|---|---|---|
| 1 | `handoff` | `PCREC_NO_REQ_HANDOFF` (`-fno-req-handoff`, bit 46) | `req_admit()` returns `EMITTED` or `SET_LEADS` with a run, AND §1.4 (a)-(g) | the gate's candidate kept, `handoff_position` declared, the body's one start site reads it |
| 2 | `scan-from-startpos` | — | always (fallback) | the body's start site reads `search_from`, as today. Where a run pre-check is emitted, that is today's `if (rx_reqrun(...) >= n) return 0;`; where none is, nothing is emitted for this table at all |

[r1 C-C10] Three corrections to revision 1's table:
- **Row 1 CALLS `req_admit()`.** Revision 1 restated the admission's
  verdict ("asked only where the admission emitted a run pre-check") in
  prose beside the table. A separate table is defensible only if it reads
  the admission's answer and never re-derives it, so the predicate's first
  conjunct is the call itself. A change to `req_admits[]` then reaches
  `req_uses[]` with no edit.
- **Row 2 is not "discard".** Where no pre-check is emitted there is
  nothing to discard. The row's name says what it does on every artifact
  it serves: the scan starts at the startpos. (The `--list-axes` row label
  is `scan-from-startpos`.)
- **The cross-table check.** §5.12 (§4.2 item 4) asserts, over the
  corpus, that `REQ_HANDOFF` is present only where `REQ_WHY` reads
  `"emitted"` (the `set-leads` row stamps `"emitted"` too) and
  `REQ_RUN` is not `"none"`. A handoff on any other admission verdict is
  a failure, which is the one way the two tables could disagree.

`DFA_SELECT(ReqUseRow, req_uses, …)`, the `dfa_pfs[]`/`req_admits[]`
idiom (D122 addendum 4's table discipline; memory: decisions as first-match
tables). `--list-axes` reads its rows through a
`pcrec_req_use_row`/`pcrec_req_use_nrows` pair, the same shape as k82fix's
`pcrec_req_admit_row`.

**Why not a `req_admits[]` row.**
- `req_admits[]`'s verdict is a closed set about WHETHER a pre-check is
  emitted and in which SHAPE (`none`, `one-attempt`, `dominated`,
  `set-leads`, `emitted`).
- The handoff is orthogonal to the shape. It applies to `set-leads` and
  `emitted` alike. As rows it would be a product (`set-leads-handoff`,
  `emitted-handoff`), which is the parallel-row smell.
- `REQ_WHY` answers "is a pre-check emitted". With a handoff the answer is
  still yes, so its closed token set does not move.

**Why not a `dfa_pfs[]` row.**
- `dfa_pfs[]` selects the forward machine's IN-LOOP candidate step, which
  runs every time the machine returns to `s0` with nothing accepted.
- The handoff is a ONE-SHOT ENTRY landing, read by three bodies. Two of
  them are not `dfa_pfs[]` customers' loops: ENG_ATTEMPT's start loop and
  the VM's first prefilter call.
- It composes with every `dfa_pfs[]` row (§3.1: movers sit on all eight
  forms), and it reads the pre-check, not the machine.
- Making it a `dfa_pfs[]` row would make every form a pair (with and
  without the landing).
- The "masked run TERM in the prefilter" that litscan_s4.md §2.3.5 named
  is the in-loop sibling. It needs a FIXED offset (a pin): a term is
  tested at an offset from the candidate start. The handoff needs only a
  BOUNDED one. They are different mechanisms for different populations,
  and the term stays named and unbuilt.

**One derivation for the variable (coding guide: one source).**
- `pcrec_emit_req_byte_check` RETURNS the expression the body's start site
  must read: `"search_from"`, or `"handoff_position"` when row 1 was
  selected.
- Each of the three callers passes that string to its one start site. The
  DFA's is a new `DfaForm.from` field, which the forward direction's
  `seed_cond`/`seed_byte` and the `scan_position` initializer render from.
  On a non-mover it is byte-identical text.
- The hybrid's static internal prefilter is the DFA emitter's other
  customer. It emits no gate (`fit.chosen == ENGM_DFA`), so its `from` is
  `search_from` by construction.

### 2.2 Stamps, `REQ_WHY`, `--emit-facts`

- **`<PREFIX>_REQ_HANDOFF`** (NEW). Its value is the decimal K that the
  emitted subtraction carries (`"0"`, `"26"`).
  - **[r1 C-C1] It is emitted ONLY on artifacts where the handoff applies**
    (row 1 selected). Revision 1 put `"none"` on every artifact, on the
    `REQ_WHY` presence rule. The panel's grep (§2.3a) showed what that
    costs: every byte-count reader of every artifact moves, though none of
    those artifacts changes its program. Movers-only confines the byte
    movement to the program movers. This is Q3's revised recommendation;
    the facts-only alternative and the every-artifact option are priced
    there.
  - Presence is the biconditional: an artifact carries the stamp iff its
    body declares `handoff_position`. §4.1's manifest and §5.12's
    structural check both test it, from different sources (§4.1 from
    Python's recomputation over `--emit-facts`, §5.12 from the emitted
    text).
  - Absence is not ambiguous, because `--emit-facts` always lists the
    decision: the `req-use` row in the decisions section reads `handoff`
    or `scan-from-startpos` on every artifact, and `req_run_maxoff` reads
    `<K>`, `unbounded` or `none`. A reader who wants the "no handoff"
    answer stated has it there, where the other non-program facts already
    live.
- **`<PREFIX>_REQ_WHY`**: unchanged, closed set unchanged.
- **`--emit-facts`**: the `req_run_maxoff` row (§1.3), and the `req-use`
  decision on every artifact.

### 2.3 abi event (D76/D94) and spec hunks (D80)

**abi.** abi 60 → 61, or k82fix's number + 1 at landing.
- The emitted text moves on every program mover: the gate line becomes the
  `if` block of §1.1, the start site reads `handoff_position`, and the
  stamp line is added.
- Every other artifact moves only in the abi digit (`60` → `61`, the same
  byte count) under the movers-only stamp. Under the every-artifact
  option it would also gain a line; §2.3a counts what that moves.
- Re-pin the identity gates (`test-recursion-identity`'s FILEPIN and its
  `ABI_SUBJ` read, the entry-shape and cpset gates, and every pin a digest
  of emitted text reaches), run `make test-codegen` before delivery, and
  THEN run the suites that count (registry, codegen, rxtsource), per D94's
  addendum.

**[r1 C-C3] Bit 46 joins `strategy_denials`.** `emit_info_def`'s
`strategy_denials` mask (`src/gen/emit_dfa.c:2728` on `lane/k82fix`) is
what makes `-fno-req-handoff`'s artifact byte-identical to BASE: without
it, passing the flag moves `rx_info.flags` on EVERY artifact, including
the ones the flag cannot act on (the [OPT-4] comment in the mask records
exactly this defect, measured, for `-fno-prefilter-collapse`). Bit 45
(`PCREC_NO_REQ_SET_LEAD`) is a member; bit 46 joins on the same ground:
the mask holds knobs with no observable effect, and the handoff changes no
answer (Theorem; the narrowed give-up allowance of §4.2 is on a population
measured empty) and records what the emitter did in its own stamp. It is
NOT the [DD-14 wave G] exception (`lib/CLAUDE.md:218`): that flag selects
an engine, this one does not. So DENY == BASE holds modulo the abi digit
alone, and §4.1's deny arm checks it on every artifact. A forgotten mask
entry is caught there by construction (every artifact differs by 5 bytes),
and by S473's plant if the deny bit is dropped from the row.

### 2.3a [r1 C-C1] The readers, found by grep

Revision 1 listed the abi readers from k82fix's own event and missed the
second reader class: pins of BYTE COUNTS and digests that never cite the
digit (D94's addendum). Both classes are enumerated here by grep, on main
(`b1869be1`, abi 59) and on `lane/k82fix` (`f0d0b206`, abi 60). The build
lane re-runs these commands at its own commit and diffs the output against
this list; the list is a floor, not the inventory.

**The abi digit.**

    git grep -nE 'PCREC_ARTIFACT_ABI [0-9]|ABI_EXPECT=|\(abi 60\)|abi 60\b|PCREC_RX_ABI_H[^0-9]*60\b|\.abi = 60|ABI_SUBJ|FILEPIN' \
        lane/k82fix -- src cli lib tests docs/spec Makefile

| reader (lane/k82fix) | what it pins |
|---|---|
| `src/gen/emit_dfa.c:52` | `#define PCREC_ARTIFACT_ABI 60` |
| `docs/spec/match_api.md:302` | the K80 `#error` text, `(abi 60)` |
| `docs/spec/match_api.md:2299` | "`rx_info.abi` is `60` on every artifact today", plus §6's change log |
| `tests/codegen/run_codegen_tests.sh:3021` | `ABI_EXPECT=60` and its bump-ledger message |
| `tests/codegen/run_recursion_identity.sh:1160` | `FILEPIN` (`bdb6d556`), the (B) whole-file reference |
| `tests/codegen/run_recursion_identity.sh:1252-1261` | `ABI_SUBJ` vs `ABI_PIN`: the "bump abi and re-pin (B)" tripwire |

Main's set is the same at abi 59, plus six comment-only citations that
do not move (`src/facts/CLAUDE.md:233`, `run_encoding_checks.sh:616,1216,
1255`, `run_facts_checks.sh:395`, `run_prechecks.sh:397`, all "(abi 59)"
provenance notes). The four instrument normalizers that rewrite the digit
(`docs/dev/optloop/alpha_vedge.sh:104`, `s4/alpha_c1.sh:185`,
`s4/alpha_c3.sh:188`, and k82fix's `s4/alpha_k82.sh:169`) match `5[5-9]`,
`5[89]` or `(59|60)`,
so a reuse of any of them against abi 61 must widen its pattern; the build's
own alpha script inherits `alpha_k82.sh`'s `norm()` and must read
`(60|61)`.

**The byte counts and digests.**

    git grep -nE 'EMITTED_BYTES|762574' lane/k82fix -- tests docs/spec lib src Makefile
    git grep -nw -e 186 lane/k82fix -- tests/registry
    git grep -nlE 'reqcube|emit_sweep' lane/k82fix -- tests src
    git ls-tree -r --name-only lane/k82fix -- tests | grep -iE 'manifest|\.tsv$'
    git grep -nE '124 rows|42 axes' lane/k82fix -- docs/spec/registry.md

| reader | moves under every-artifact | moves under movers-only |
|---|---|---|
| `tests/codegen/manifests/m5_stage1_stamps.tsv` (12 `EMITTED_BYTES` rows, read by `run_cpset_structure.sh:518-547`) | all 12 | 2: `\bword\b`, `(?i)HeLLo` (the prototype's predicate on each pinned pattern; the other 10 are `dominated`, `one-attempt`, `none` or no run) |
| `tests/resource/run_resource_tests.sh:682-698` (`a{5,25000}` rescued at 762,574 bytes) | yes | no (`dominated`, no run) |
| `tests/size/check_size_tripwire.sh` + `docs/dev/artifact_size_log.tsv` (`run_size_log.sh`) | every row, by the line's bytes; the tripwire's 1,400,000-byte max is not near | the program movers' rows only |
| `tests/codegen/reqcube_check.py`, `runcmp_check.py`, `tests/litscan/reqcube.rxt` (`gen_reqcube.py`) | the text they excise or pin around the run pre-check: re-read | the movers among their witnesses: re-read |
| `tests/lib/c_artifact_cmp.sh`'s `emit_sweep` (the recursion identity gate's whole-file sweep) | every artifact: a FILEPIN re-pin | the digit only: the same re-pin, fewer differing lines |
| `tests/findings/manifests/*.txt` (b1/ship mover lists) | re-derive: a stamp line on both arms must not create a mover | re-derive: the handoff is findings-independent (K is a walk fact), so the lists should not move; the build confirms |
| `tests/registry/run_registry_tests.sh:629-643` (`axesn == 186`) | +k | +k |
| `docs/spec/registry.md:192` ("124 rows / 42 axes") | +2 rows, +1 axis | same |
| `tests/axes/run_axes.sh` groups (F3 is bit 45's) | a new GROUP F4 for bit 46 | same |

`k` is measured at the build: k82fix's analogous event (one axis, one
flagged row) was 183 → 186, +3; the panel estimated +2.

**The contract readers (D80), which move under either option.**
- `docs/spec/match_api.md`: §6.3 the stamp, its presence rule and
  value; §6 the abi 61 change-log entry; :2299's "abi is 60" sentence;
  :3813's `REQ_WHY` table, whose `"emitted"` row gains "since `abi` 61
  possibly handed off (`REQ_HANDOFF`)"; and §3.1's sentence, revised by
  [r1 C-C8] because revision 1's "unobservable by the contract" is false
  for the give-up surface (a deny flag that moves `PCREC_ERR_STEPS` versus
  a result is exactly K65/K66's invariant):

  > A search may begin its internal scan after `startpos` where a
  > necessary literal proves that no match begins earlier; its answer is
  > the one a scan from `startpos` gives. The step budget meters only the
  > work the matcher performs, so positions it proves cannot begin a match
  > consume none. Where an artifact's VM prefilter is count-collapsed
  > (`RX_VM_PREFILTER_LANG "count-collapsed"`), a search that returns
  > `PCREC_ERR_STEPS` when built with `-fno-req-handoff` may therefore
  > return a match without it, and that match is the one an unbounded
  > budget returns.

  The last sentence ships only if Q10 keeps the allowance; under Q10's
  recommended decline it is dropped and the first three stand alone.
- `docs/spec/tuning.md`: a new §2.41 for `-fno-req-handoff`; the
  flags→flag table at :3738 gains the bit-46 row beside bit 45's; §2.29's
  `REQ_WHY` paragraph gains a cross-reference.
- `docs/spec/registry.md` / `cli.md:582`: the `req-use` axis and the flag
  in the deny-flag list.
- `docs/spec/facts_listing.md`: the `req_run_maxoff` row and the `req-use`
  decision.
- `docs/spec/findings.md:128`: the run's scan-member PICK row. The handoff
  reads the window the PICK chose, never re-picks, so the row gains one
  sentence that the window's K is a walk fact independent of the PICK, or
  is left unchanged if the build finds no reader there.
- `lib/CLAUDE.md:218`: the `strategy_denials` discussion gains bit 46 as
  an ordinary member (C-C3 above), so a reader does not take it for the
  wave-G exception.
- `lib/pcrec.h`: the flag, beside `PCREC_NO_REQ_SET_LEAD`;
  `src/core/axes.def`: the row; the owning directories' `CLAUDE.md` where
  a file's role changes.

## 3. Predicted movers and their timing

### 3.1 The census (compile-only, `k82h_census.out`)

The populations are `c3_movers.py`'s, imported: every bench export ×
{auto, vm} × {caps, nocaps}, and every corpus `pattern` row × {auto, vm}.
The binary is the prototype over `lane/k82fix`.

| population | run pre-check emitted | DFA-scan route | **bounded: program mover** | unbounded (unreachable) | no DFA scan (VM, excluded) |
|---|---|---|---|---|---|
| bench auto | 59 | 55 | **47** (49 rows) | 8 | 4 |
| bench auto-nocaps | 59 | 55 | **47** (49 rows) | 8 | 4 |
| bench vm / vm-nocaps | 99 / 99 | 0 / 0 | 0 / 0 | 0 / 0 | 99 / 99 |
| corpus auto | 219 | 197 | **160** (209 rows) | 37 | 22 |
| corpus vm | 447 | 0 | 0 | 0 | 447 |

**K distribution (bench auto movers).**
- K = 0 on 33 of the 47.
- 1-5 on 7.
- 9 on 3 (`altwide/sfx-*`).
- 23-32 on 4 (`litrun/lit-l31` 23, `lit-l40` 31, `slack` 26,
  `kv-quoted` 32).

**Mover routes (bench auto).**
- DFA unanchored: 39.
- DFA attempt: 2 (`anc-m-caret`, `asr-caret-ml`).
- VM hybrid: 6 (`userpass`, `slack`, `github-pat`, `lkb-neg`, `lkb-pos`,
  `asr-lb-neg`).

The corpus auto movers are 121 / 6 / 33.

**The in-loop forms the movers sit on.** `byte-class`, `memchr`,
`offset-set[-bounded]` and `byte-class-bounded` all occur. The handoff
composes with each, which is §2.1's argument made concrete.

**Stamp-only movers:** none under the movers-only stamp ([r1 C-C1]): a
non-mover moves only in its abi digit. (Revision 1's every-artifact
`"none"` line made every artifact a stamp mover; §2.3a counts the cost.)

### 3.1a [r1 C-C9, C-C8] The populations revision 1 did not count (`k82h_census_r2.out`)

Same prototype, same classifier (`k82h_census.py`'s `one()`, imported).

| corpus config (3,663 distinct pattern/args) | compiled | run pre-check | DFA-scan route | **mover** | unbounded | routes of the movers | hybrid movers' `RX_VM_PREFILTER_LANG` |
|---|---|---|---|---|---|---|---|
| `auto` (cross-check of §3.1) | 3,291 | 219 | 197 | **160** | 37 | 121 DFA unanchored / 6 attempt / 33 hybrid | 33 `exact` |
| `--no-captures` | 3,291 | 219 | 197 | **160** | 37 | 144 / 7 / 9 | 9 `exact` |
| `--engine=vm -fprefilter` | 3,021 (642 refused: `-fprefilter` is do-or-die) | 197 | 197 | **160** | 37 | 160 hybrid | 160 `exact` |

What it says:
- **[r1 C-C9] No new mover kinds.** The no-captures corpus moves the same
  number of artifacts with the same K histogram; 24 of auto's hybrid
  movers become DFA movers there, because without captures the selector
  takes the DFA. The forced hybrid reaches all 160 as hybrids. So the
  hybrid route's population for the differential is 160, not 33, if the
  differential runs the forced arm, and §4.2 item 1 does run it.
- **Every hybrid mover's prefilter is `exact`**, in every config, and the
  six bench hybrid movers read `exact` too (checked one by one:
  `wild-secrets-username-password-pair`, `-slack-webhook-url`,
  `-github-pat`, `syntax/lkb-neg`, `lkb-pos`, `utf8/asr-lb-neg`). That
  empties §4.2's narrowed give-up allowance on every measured
  population ([r1 S-F2]).
- **[r1 C-C8] The budget and give-up cells are disjoint from the movers.**
  The corpus has 35 pattern blocks carrying a step/frame budget or a `gu`
  case (`tests/base/k64_*`, `k65_*`, `k66_*`, `tests/harness/giveup.rxt`,
  `tests/litscan/reqcube.rxt:434-492`, `tests/recursion/*`,
  `tests/vars/*`). Compiled as the harness compiles them (their own
  `engine` column honoured, which `c3_movers.py`'s population ignores),
  all 35 are on the VM with no DFA scan: 0 movers. So no shipped give-up
  expectation can move under the handoff.
- **The K > 0 population is THIN.** 27 corpus movers (133 of 160 are
  K = 0) and 14 bench movers (33 of 47). K = 0 is the population where
  K−1 and the clamp are untestable (there is no K−1, and `c − 0` cannot
  underflow), so S463 and S470's witnesses must come from these 27 + 14
  or be constructed (§4.4 constructs them).
- **`\G` hybrids: none.** No mover on any route carries a `\G` start
  family, which is why S469's witness is constructed:
  `(?:\Gab|x)(cat)dog` is a VM hybrid, `exact` prefilter, K = 2 on the
  prototype. (`(?:\G|x)(cat)dog`, K = 1, is a hybrid too but cannot
  discriminate: its `\G` branch consumes nothing before the window, so a
  `\G` moved to `lo = c − 1` would need a second, earlier occurrence.)

### 3.2 The K82 cells and C3's customers

These are the auto configs. The forced-VM arms are not movers.

| cell | route | K | today (abi 60) | predicted with the handoff |
|---|---|---|---|---|
| `mod-i`, `mod-r` | DFA, `byte-class` | 0 | Linux +0.59..+0.70 ns/B over BASE | T3 Mac: 1.39 → 0.81 (DENY 0.76) at 64 KiB, 1.70 → 1.00 (0.86) at 1 MiB. Predicted Linux: BASE + about 0.05-0.15 (the pair-arm overshoot, H11) |
| `cls-fold-pair`, `cls-pair-ctl` | DFA, `memchr` | 0 | +0.32..+0.41 | T3 Mac 0.99 → 0.55 = DENY. Predicted Linux ≈ BASE, inside the floor |
| `ci-strasse` | DFA, `byte-class`, utf8 | **2** | +0.08..+0.10 | T3 Mac 0.65 → 0.49, which BEATS DENY's 0.53. Predicted Linux: BASE or a small win |
| `userpass` (A) | hybrid | 0 | k82fix's `set-leads` restored BASE (the `=` lead rejects) | null. The run search never runs on its subject, so the handoff is never consulted |
| `alt-shared-char` (C) | DFA, `offset-set` | 0 | k82fix's argmin restored the one-stream scan | null to small win: the engine's scan starts at the window instead of re-finding it |
| `ci-ascii-control` (customer) | DFA, `byte-class` | 0 | −0.45..−0.50 (the win) | null: the run is absent, the gate rejects, and T3 measured 0.208 against 0.209 |
| `union-select` (customer) | DFA | **unbounded** (`.*?`) | −0.40..−0.52 (the win) | NOT a mover. Discard gate unchanged, byte-identical apart from the abi digit (no stamp under movers-only, [r1 C-C1]) |
| `slack` | hybrid | 26 | null stakes | null: the run is absent |
| `stack-frame` (control) | DFA, `offset-set-bounded` | 0 | k82diag: deleting the gate WINS, 0.347 → 0.252 | predicted toward 0.252. This is the one cell where the gate PASSES densely on real text with an exact run, and an alpha cell |
| `http-5xx` | DFA | unbounded | null | not a mover |
| union-srch short calls (~35 cells, +2.4..+4.4 ns) | — | — | the per-call entry term | null within the floor: the handoff adds one compare per PASSING call and removes none of the gate's entry cost. Q7 stands where k82cost left it ([MEMFN]'s binding-form criterion) |

**The movers outside K82.** About 30 of the 47 are pre-C3 exact-run
pre-checks (tier 2b), for example `syntax/anc-*`, `asr-wb`, `qnt-quest`,
`esc-quote`, `mod-s` and `utf8/lit-*`. They had the same discard-then-rescan
shape on match-dense subjects: reqpos_2b.md §4.3's "~1% of a pass wasted on
the 1.00× rows". The handoff should show as small wins or nulls there,
never as losses (finding 4). Six of them are the alpha's "outside" cells
(§4.5).

### 3.3 The parked cost model's trigger population

The ruling parks the cost model behind "a census of C3 runs at UNBOUNDED
offset still losing after the handoff lands". The reachable side of that is
known now.

**On the bench (auto), 8 artifacts:**
- `union-select`;
- `comment-obfuscation` (`/\*…\*/`'s `*/`);
- `http-5xx`;
- `cls-h`, `cls-s-lc`, `cls-v`;
- `qnt-plus-ctl`;
- `qnt-poss-plus`.

**On the corpus,** 37.

**What the trigger needs.** k82cost's model flagged `cls-v` as a builtin-
prior decline at 64 KiB (litscan_k82b.md §2.4). It is the one member with a
predicted loss. The trigger's measurement is these 8 cells' Linux deltas,
discard gate vs `-fno-req-run`, after the handoff lands. It is OWED to the
round's batch gate, not to this row.

## 4. Validation plan

### 4.1 The mover manifest and the deny arm (compile-only, `k82_movers.py`'s shape)

- **Arms.** BASE = abi 60 (k82fix's tip), NEW, and DENY = NEW +
  `-fno-req-handoff`. The abi digit is normalized at its sites (§2.3a).
- **NEW vs BASE: the PROGRAM moved iff predicted.** The prediction is
  recomputed in Python from NEW's `--emit-facts`: `REQ_WHY` "emitted", a
  run, a DFA-scan route from the stamps, `req_run_maxoff` finite, and no
  §1.4 (d′)/(g) decline.
  - On a predicted mover, `REQ_HANDOFF` is present and equals that K.
  - [r1 C-C1] On every other artifact there is NO difference beyond the
    abi digit: no stamp line, under the movers-only rule.
  - Off-diagonal cells are failures.
- **DENY vs BASE:** identical on every artifact modulo the abi digit
  ALONE ([r1 C-C3]: bit 46 is in `strategy_denials`, and DENY emits no
  stamp).
- **The fact's own check.** NEW's `req_whole_run` equals BASE's on every
  artifact: the offset is an annotation and must not move the choice.
- **Populations:** §3.1's and §3.1a's tables, reconciled count for count
  (K35: an empty or shrunken population is a failure), including the
  `--no-captures` and forced-hybrid corpus arms ([r1 C-C9]).
- **[r1 C-C4] What this manifest is NOT.** It predicts movers and K from
  `--emit-facts`, which reads the same `rb_walk` the build emits from. So
  it checks the plumbing (fact → selection → text), never the fact. A
  wrong K is invisible to it by construction. The fact's checks are §4.2a.

### 4.2 Answer identity

1. **The differential.** `c3_answers.py`'s shape, run over every program
   mover with BASE := DENY. The driver is `possdiff_driver.c`: span, every
   capture slot and the failure surface, at EVERY start position. The
   subjects are `b1_mover_answers.py`'s sweep plus `PREFIXES=1`.
   - **[r1 S-F9] Per route.** The movers are run and COUNTED per admitted
     route (DFA unanchored, DFA attempt, VM hybrid), with the forced-hybrid
     corpus arm included so the hybrid route has 160 movers rather than 33
     (§3.1a). A route with zero swept movers is a failure.
   - **[r1 S-F5, C-C7] Ill-formed utf8.** The utf8 movers' subject sweep
     includes ill-formed and truncated subjects: runs of 1-6 stray
     continuation bytes placed before, inside and after `[c − K, c)`, a
     truncated lead at the subject's end, and an overlong lead. The K73/K75
     rules decide the expected answer; DENY is the reference arm, so the
     differential needs no oracle for them.
   - **[r1 S-F2] The allowance is EMPTY except on count-collapsed
     prefilters.** Revision 1 allowed `give-up → NOMATCH` and
     `give-up → match` on every hybrid. That was too wide. A hybrid's VM
     attempts start only where its prefilter answers, or after a failed
     attempt that began there. K bounds the prefilter's own language
     whenever that language is the exact one or an erasure of zero-width
     nodes (lookarounds, `\b`): the run is still necessary in it, at the
     same offsets. So no attempt is ever made below `c − K`, with or
     without the handoff, and the VM's work is identical. The one
     prefilter language K does not bound is [OPT-4]'s COUNT-COLLAPSED one
     (`X{m,n}` widened to `X{min(m,1),}`, `RX_VM_PREFILTER_LANG
     "count-collapsed"`): its answers can sit below `c − K`. There, and
     only there, `give-up → NOMATCH` and `give-up → match` (the match
     DENY returns at an unbounded budget) are allowed. **Every other
     change, on every route, is a DEFECT.**
   - **The measured allowance population is zero**: every hybrid mover
     in every config, corpus and bench, reads `exact` (§3.1a). The
     count-collapsed prefilter is a fallback-only ladder rung (ruling B,
     `prefilter_count_independence.md` §10a). So the build constructs one
     count-collapsed hybrid mover (a pattern whose exact prefilter
     overflows the state cap, with a run after the counted repeat) and
     runs it as the allowance's witness; if none can be constructed, the
     allowance is deleted rather than kept untested. §Q Q10 recommends
     the simpler finish: decline the handoff on count-collapsed
     prefilters, which empties the allowance by construction.
2. **The handoff witnesses**, a new `tests/litscan/handoff.rxt`. It is
   generated by a `gen_handoff.py` with python3 `re` expectations; utf8
   rows are `re` over `str`, and the K73 continuation-byte rule is checked
   against the 10.46 transcript where `re` cannot speak. Each pattern runs
   under every engine row the harness runs (auto, vm, the `-fno-*` axes),
   at every startpos.
   - **The maximum-offset case.** The match begins exactly K bytes before
     its window: `x{2,5}(?i)cat` on `xxxxxCaT` (K = 5), and
     `(?:a|bb)?catdog` on `bbcatdog` (K = 2).
   - **[r1 S-F1] Two occurrences.** The first occurrence is the match's
     own window and a second follows it: `(?i)cat` on `CAT CAT`, and
     `x{2,5}(?i)cat` on `xxxxxcat xcat`. S464's witness.
   - **Decoys.** A false run occurrence within K bytes BEFORE a real match:
     `a{3}(?i)cat` on `cat aaacat`, where lo lands inside the decoy's
     span.
   - **Near the startpos.** The run within K of a non-zero startpos: the
     underflow clamp, `x{2,5}(?i)cat` on `xxxxxCaT` at startpos = 1..5.
     S470's witness: at startpos 3 the answer is `(3,8)`, and a missing
     clamp reports `(0,8)`, below the startpos.
   - **Multibyte width.** `(?i)straße` on `ſtraße`, `éſtraße` and
     `xſTRASSE`. Here lo = c − 2 lands on a continuation byte, which tests
     the rounding. Also `.{3}cat` and `é{2}cat` under utf8 with 2/3/4-byte
     characters in the prefix.
   - **[r1 C-C7] Ill-formed text.** The same patterns with 4, 5 and 6 stray
     continuation bytes immediately before the window, so the round-up
     takes more than 3 steps ([r1 S-F5]'s counterexample to "≤ 3").
   - **Seeded starts.** `\bcat\b` and `(?<![a-z])cat` with a word
     character at lo − 1 and lo − 2 (on the DFA route, and on the hybrid
     for the lookbehind). S468's witness is `\bcat\b` on `zcat cat` from
     0: the true first match is `(5,8)`, and a seed read from
     `search_from` instead of `lo` reports `(1,4)`.
   - **The attempt route.** `(?m)^item` (ENG_ATTEMPT), and `(?:\G|x)cat`
     and `\Gx|yx`-shaped `\G` rows on whichever route the selector gives
     them (Claim 2′).
   - **[r1 S-F3] The `\G` hybrid.** `(?:\Gab|x)(cat)dog` (VM hybrid,
     `exact`, K = 2) on `zzabcatdog`, `abcatdog`, `zxcatdog` and
     `zzabcatdogxcatdog` from every startpos. S469's witness: from 0 on
     `zzabcatdog` the answer is NOMATCH, and a `\G` anchored at `lo`
     reports `(2,10)`.
   - **`\K`.** A row on the route that carries it: offsets are from the
     attempt start.
   - **Find-all.** Dense matches (`(?i)cat` over `cAtCaTcat…`) and
     overlapping run occurrences (`aa(?i)a` style).
   - **A run that begins on a continuation byte:** `(?:éx|ʩx)`.
   - **Controls.** `a.*?(?i)select` and `ab.*xyzw` (unbounded, must not
     move) and the forced-VM rows (must not move).
3. **The corpus and identity gates.**
   - `make test`: the `.rxt` corpus on every engine row, every identity
     gate after its re-pin, and the codegen structural checks.
   - [r1 C-C9] `make test-axes AXES="-fno-req-handoff -fno-req-set-lead
     -fno-req-run-fold -fno-offset-skip -fno-run-prefilter -fno-scan-edge
     -fno-hyb-reseed -fprefilter"`. That is the new flag, its two admission
     neighbours, and the scan-form flags that change which of the three
     bodies (and which in-loop form) the handoff lands in, because the deny
     of each must compose with the handoff on. `tests/axes/run_axes.sh`
     gains GROUP F4 for bit 46: its budget-bound population is §4.2 item
     1's count-collapsed movers (measured empty), stated so on the F3
     precedent. The full `test-axes` is the batch gate's (D144 item 2).
4. **Structural checks** (`tests/codegen/run_prechecks.sh`, a new
   §5.12; k82fix's file ends at §5.6, so the build takes the next free
   number and keeps this name in its header), read off the TEXT. [r1 C-C5]
   Every detector the sabotage table names is HERE, in the suite. Revision
   1 placed S464/S465/S466/S472's detectors (old numbering) in the
   manifest under `docs/dev/optloop/`, which mech never runs, so they
   read UNDETECTED; and S466 (an unbounded run handed off) is
   answer-equivalent, so no `.rxt` row can see it.
   - **The hand K pin table** ([r1 C-C4] (a), [r1 C-C11]): §4.2a's table,
     each pattern compiled and its `REQ_HANDOFF` compared to the hand
     value. Detects S465 and S466.
   - **Presence:** `handoff_position` is declared iff `REQ_HANDOFF` is
     present, and the subtraction constant equals the stamp.
   - **Bounded:** no artifact whose `--emit-facts` `req_run_maxoff` reads
     `unbounded` carries a handoff; named witnesses `a.*?(?i)select` and
     `ab.*xyzw`, plus the corpus population (floor: the 37 unbounded
     DFA-scan artifacts of §3.1, set at 80% of the measured count). Detects
     S467.
   - **The run choice:** a `req_whole_run` pin table on patterns where a
     bounded and a more informative unbounded run compete (`ab.*xyzw` →
     `78797a77`, the unbounded `xyzw`). Detects S474.
   - **[r1 C-C10] The cross-table check:** a handoff only where `REQ_WHY`
     reads `"emitted"` and `REQ_RUN` is not `"none"`.
   - **One start site per body:** the DFA initializer and `scan_position`,
     the attempt loop, or the hybrid's first `prefn` call.
   - **`\G` readers** ([r1 S-F3]): ENG_ATTEMPT's `start == search_from`
     and the VM's own `search_from` never read `handoff_position`; the
     hybrid prefilter's third argument reads it at the FIRST call only.
     Detects S469.
   - **The round-up** ([r1 S-F5], [r1 S-F6]): present iff the encoding is
     multibyte, INSIDE the `> K` branch only, with `< subject_length` in
     its condition and no step cap. Detects S471 and S472.
   - **The (d′) decline:** no handoff on a hybrid whose text carries both
     a `\G` start family and the prefilter-window ceiling. Detects S476.
   - **The deny row:** `-fno-req-handoff` emits no stamp, no
     `handoff_position`, and abi 60's gate line. Detects S473.
   - Each check carries its population floor and a named witness (K35).

### 4.2a [r1 C-C4] The fact's own checks, which share no source with the walk

The manifest (§4.1) and the stamp (§2.2) both come from `rb_walk`. A K the
walk gets wrong is a K both agree on. Three checks that do not:

**(a) The hand K pin table** (in-suite, §5.12). Each K is derived by hand
from §1.3's width rules on the pattern TEXT, not by running the walk:

| pattern | `-e` | hand K | derivation |
|---|---|---|---|
| `(?i)cat` | byte | 0 | the run is the whole match's head |
| `(?i)straße` | utf8 | 2 | the run `TRA` follows `(?i)s`, which matches `s`, `S` or `ſ` (U+017F, 2 bytes) [r1 C-C11] |
| `x{2,5}(?i)cat` | utf8 | 5 | five `x` bytes at most before the run |
| `.{3}cat` | utf8 | 12 | three characters of up to 4 bytes |
| `é{2}cat` | utf8 | 4 | two 2-byte characters |
| `ab(?:cdef\|xyzdef)g` | utf8 | 5 | the run `defg` after `ab` + `xyz` (5 bytes) |
| `(?:a\|bb)?catdog` | byte | 2 | the wider branch `bb` |
| `(?:ab\|c)(?i)select` | utf8 | 4 | `ab` (2), then `(?i)s`, which is not a cube under utf8 (`ſ` is 2 bytes), so the run `ELECT` sits up to 2 + 2 bytes in |
| `(?:\Gab\|x)(cat)dog` | byte | 2 | `\G` is zero-width, `ab` is 2 |
| `a.*?(?i)select`, `ab.*xyzw` | byte | none (unbounded) | `.*` |

The prototype agrees on every row it was run on (§1.3's table; the last
three were run for this revision). If the walk and the hand derivation
ever disagree, the build stops and the panel's question is which is wrong.

**(b) An independent invariant-F oracle.** Invariant F (§1.2) is a claim
about the PATTERN's language, so it can be checked against a reference
matcher with no pcrec code in the loop. For every mover (corpus and bench,
every config of §3.1a) and every subject of §4.2 item 1's sweep:
- for every position `p`, ask libpcre2 (the local 10.48 adapter,
  `tests/oracle/`; python `re` as the cross-check where it compiles the
  pattern) for an ANCHORED match at `p` (`PCRE2_ANCHORED`, startoffset
  `p`);
- where one exists, assert a masked occurrence of the window (`REQ_RUN`'s
  bytes and mask, read off the stamp) in `[p, p + K]`.

The anchored match at `p` makes `\G` true at `p`, so it tests a SUPERSET
of the real successes; F must hold on it too, because the walk counts
`\G` as zero-width. The check shares the window with the walk (it reads
the stamp) and nothing else: K is the one input under test, and the
oracle decides where matches begin. It reports cells checked and
violations, per population (K35); 0 violations is the bar, and a
violation is a K that deletes matches.

**(c) The K−1 plant over the whole mover population.** S463 (K − 1) is
planted once, and the §4.2 item 1 differential is run over EVERY K > 0
mover, not only `handoff.rxt`. The report states detections over
population: a K > 0 mover where K − 1 changes no answer on the sweep is a
mover whose sweep never places a match at exactly `c − K`, which is a
coverage gap in the sweep, and is listed. (Critic 1's plant over its own
shapes detected on 98.) The K > 0 population is THIN: 27 corpus movers and
14 bench movers (§3.1a). This revision says so rather than letting the 160
stand in for it, and the constructed rows of §4.2 item 2 exist because of
it.

### 4.2b [r1 C-C2] DD12a(i): the encoding pair check

`tests/codegen/run_encoding_checks.sh`'s DD12a(i) compiles each pattern
under `byte` and `utf8` and requires the hot loop's control flow to be
identical after normalizing the stamps that legitimately differ
(`REQWHY_STAMP_RE` at `:590`; the `[silentred]` excision of `rx_reqrun`
when `REQ_WHY` differs, `:886-905`). The handoff differs by encoding by
design: K can differ (`(?i)straße` is 2 under utf8 and smaller under
byte, where `ſ` is not a member), and the round-up exists only under
utf8. Unhandled, DD12a(i) goes red on the movers. The build adds:
- **A named region.** The handoff block (the `if (handoff_position -
  search_from > K) { … } else …` of §1.1) is excised from BOTH sides as
  `/* [K82-handoff] handoff block excised for comparison */`, anchored on
  its opening and closing lines, the `[silentred]` shape.
- **A `REQ_HANDOFF` normalizer** beside `REQWHY_STAMP_RE`, rewriting the
  value to `N`. Presence must match on both sides unless `REQ_WHY` or
  `REQ_RUN` differs by encoding (the handoff then legitimately applies
  under one encoding only); an unexplained presence asymmetry is a failure.
- **A floor.** The number of pairs excised on both sides is reported and
  floored at 80% of its landing count (K35), and each side's excised
  region is at most 8 lines, so an over-broad excision cannot silently
  hide the rest of the function.
- **A sabotage row.** S477 (§4.4) widens the excision's end anchor to the
  function's closing brace; the 8-line ceiling detects it.

### 4.3 ASan/UBSan

- **The sweep.** The §4.2 item 1 differential under
  `CFLAGS="-fsanitize=address,undefined -fno-builtin-memcmp
  -DDIFF_EXACT_SUBJECT"`, over every program mover (every subject in a
  block of exactly its length). This is `c3_answers_san.log`'s run.
- **Edge subjects.** `n = 0` with a NULL subject; a startpos at `n` and at
  `n − 1`; a match at offset 0 with K > 0 (the clamp); utf8 subjects that
  END in a truncated sequence after the run; [r1 S-F5] utf8 subjects that
  END in four or more stray continuation bytes, with `c − K` among them.
- **The control.** S472 (the round-up's `< subject_length` dropped) is
  planted once under the san axis, on `S455`'s precedent: a sanitizer
  control that is itself sabotaged. Its reaching witness needs a subject
  with no character start in `[c − K, n)`, which a window that contains an
  ASCII byte never allows; if the build cannot construct one, the row's
  in-suite detector is the structural one (§5.12, "the round-up"), and the
  ASan arm is recorded as unreached rather than claimed.

### 4.4 Sabotage rows: S463-S477, fifteen rows (check main's highest at landing)

Highest S-id on main `b1869be1`: S456; on `lane/k82fix`: S462 (S457-S462
are k82fix's). So the handoff's rows start at S463 if k82fix lands first.
[r1 C-C6] Every row names its constructed reaching witness (`SAB_REACH`)
and the population that witness stands for (`SAB_REACH_POP`), and every
detector is in the suite ([r1 C-C5]).

| row | plant | `SAB_REACH` (witness) | `SAB_REACH_POP` | in-suite detector |
|---|---|---|---|---|
| S463 | the subtraction uses K − 1 (lo one byte too late) | `x{2,5}(?i)cat` on `xxxxxCaT`: `(0,8)` becomes `(1,8)` | the K > 0 movers (27 corpus, 14 bench) | `handoff.rxt` maximum-offset rows; §4.2a (c) reports the whole-population count |
| S464 | [r1 S-F1] the gate returns a LATER occurrence (the pair arm returns the stream it advanced last, not the lesser) | `(?i)cat` on `CAT CAT`: the first match is lost | every mover on the pair arm, and every mover for the single-stream spelling | `handoff.rxt` two-occurrence and dense find-all rows |
| S465 | the walk's width counts an `A_WCLASS` / multi-byte class as 1 byte (the `cwmax` mistake) | `(?i)straße` `-e utf8` on `ſtraße`: K 2 → 1 | utf8 movers whose K counts a multibyte member | §5.12 hand K pin (`ci-strasse`'s pattern, K = 2); `handoff.rxt` `ſtraße` rows |
| S466 | `A_ALT`'s width takes the LEFT branch, not the max | `(?:a\|bb)?catdog` on `bbcatdog`: K 2 → 1, the span moves | movers with unequal-width alternation before the window | §5.12 hand K pin; `handoff.rxt` |
| S467 | the `bounded` conjunct dropped (an unbounded run handed off at the saturated K: answer-equivalent) | `a.*?(?i)select`, `ab.*xyzw` | the 37 corpus / 8 bench unbounded DFA-scan artifacts | §5.12 "bounded" check (structural; no answer can see it) |
| S468 | the seeded initializer keeps reading `search_from` while `scan_position = handoff_position` | `\bcat\b` on `zcat cat`: `(5,8)` becomes `(1,4)` | seeded DFA movers (`\b`, lookbehind) | `handoff.rxt` seeded rows |
| S469 | the hybrid passes `handoff_position` into the VM's `search_from` (the `\G` anchor moved) | `(?:\Gab\|x)(cat)dog` on `zzabcatdog`: NOMATCH becomes `(2,10)` | `\G` hybrid movers: 0 measured, 1 constructed | `handoff.rxt` `\G`-hybrid row; §5.12 "`\G` readers" |
| S470 | the underflow-safe form replaced by `c − K` with no clamp | `x{2,5}(?i)cat` on `xxxxxCaT` at startpos 3: `(3,8)` becomes `(0,8)` | the K > 0 movers | `handoff.rxt` startpos 1..K rows |
| S471 | the utf8 round-up dropped | `(?i)straße` `-e utf8`, text only (answers unreached: 0 diffs over 13 shapes, [r1 S-F5]) | utf8 movers | §5.12 "the round-up" (structural) |
| S472 | the round-up's `< subject_length` dropped | the ASan edge row if constructible (§4.3) | utf8 movers | §5.12 "the round-up"; the san axis where reached |
| S473 | `-fno-req-handoff`'s deny bit dropped from the row | `(?i)cat` `-fno-req-handoff` | every mover | §5.12 deny row. NOT the registry suite: `--list-axes` walks the same row, a control sharing its source (k82fix's S462 lesson) |
| S474 | the run choice moved: `rn_better` prefers a bounded run | `ab.*xyzw`: `req_whole_run` `78797a77` → `6162` | patterns with a bounded and a more informative unbounded run | §5.12 `req_whole_run` pin table |
| S475 | [r1 S-F4] the verb/callout conjunct dropped | none: verbs and callouts are refused before the predicate is asked | 0 | declared UNREACHED with that reason, plus the compile-time assertion (§1.4 (g)) |
| S476 | [r1 S-F3] the (d′) decline dropped | a constructed `\G` hybrid with the prefilter-window ceiling, or UNREACHED if the build cannot construct one | 0 measured | §5.12 "the (d′) decline" |
| S477 | [r1 C-C2] DD12a(i)'s handoff excision widened to the function's closing brace | any utf8/byte pair with a handoff on both sides | the both-sides-excised pairs | DD12a(i)'s 8-line ceiling (§4.2b) |

Revision 1's rows map as: S463 → S463, S464 → S465, S465 → S466, S466 →
S467, S467 → S468, S468 → S469, S469 → S470, S470 → S471, S471 → S473,
S472 → S474. New: S464, S472 (was §4.3's unnumbered control), S475, S476,
S477.

Every row is checked single-row for [MECH-REACH]: the witness must reach
its site on the plant's tree. Anchors are copied from
`git show HEAD:<path>` at landing.

### 4.5 The Linux alpha cells (D144)

`alpha_k82.sh`'s protocol: `taskset -c 2`, loops of at least 50 ms, base
and deny as the floor, absolute deltas for per-call cells (D144
addendum 1). The arms are:
- BASE = abi 60;
- NEW;
- DENY = NEW + `-fno-req-handoff`, where DENY == BASE modulo the abi digit
  ([r1 C-C3]).

The cells:
- **The five cause-(B) cells** at 64 KiB and 1 MiB: `mod-i`, `mod-r`,
  `cls-fold-pair`, `cls-pair-ctl`, `ci-strasse`.
- **C3's customers:** `ci-ascii-control`, `union-select` (the control:
  DENY == NEW in program text), and `slack`.
- **(A)/(C) re-reads:** `userpass` and `alt-shared-char`.
- **`stack-frame`:** the dense real-text exact run.
- **Six movers outside K82:**
  - `altwide/sfx-64` (K 9);
  - `litrun/lit-l31` (K 23);
  - `loglines/kv-quoted` (K 32);
  - `syntax/asr-wb` (seeded);
  - `syntax/anc-m-caret` (attempt route);
  - `syntax/lkb-pos` (hybrid).
- **The union-srch short-call set** over its movers, as absolute ns
  against the floor.

The expected reading:
- cause (B) back to BASE ± the pair-arm residual on `mod-*`;
- customers null;
- outside movers null or better;
- short calls inside the floor.

Any loss past the floor is an issue row (D144 item 3). Any wrong answer is a
disaster.

## 5. Hazards and open questions — what the light D6 panel must refute

**Hazards** (each is a claim this note makes that a critic should try to
break, with the witness that would break it):

- **H1 — Claim 2's premise.** Is the startpos read ONLY as the attempt
  lower bound by every construct pcrec compiles, `\G` aside?
  - Candidates to refute: the K73/K75 offset-0 rules (they run above the
    gate, on `search_from`); the end-window clamp; any VM verb (out of
    scope, refused by `mod_verbs.c`); the VM's step budget (§4.2: a budget
    is the one place a skipped attempt is observable, and only toward an
    answer).
  - [r1 S-F4] Verbs and callouts are refused today, and §1.4 (g) declines
    them structurally for the day they are not. [r1 S-F2] The step budget
    is observable only on a count-collapsed prefilter (§4.2). [r1 S-F3]
    The hybrid's prefilter reads its third argument as `\G` (Claim 2′).
- **H2 — Bytes, not characters.** Is every width arm of §1.3 a byte count
  on the LOWERED tree? `A_WCLASS` must descend, and `A_CALL` stays
  unbounded. The prototype's `ci-strasse` K = 2 says yes on one cell. A
  critic should find a lowered node whose byte width the arms
  under-state.
- **H3 — The attempt start vs the reported start.**
  - `\K`'s offsets are from the attempt start.
  - Does any DFA-route artifact report a start other than its thread
    start?
  - Does the reverse pass's `rewind_position > search_from` stay correct
    (§1.2's note)?
- **H4 — Window vs whole run.** `K = whole_maxoff + at`. Is the window the
  thing the gate finds, at `at`, in every arm, including the [K66] whole
  run, which is never on a DFA-scan route?
- **H5 — Truncation.** After `PCREC_MAX_REQ_RUN_SCAN` truncation (`rn_pre`
  drops a tail's front, `rn_app` a head's end), is "head at 0, tail at
  `maxw − n`" still true of the STORED bytes?
- **H6 — A non-boundary `lo` under utf8.** The note rounds up to make `lo`
  a legal startpos (Claim 3). The DFA's own landing (the offset-set
  reseed) already lands on arbitrary bytes, and a run-bearing pattern's
  first consumed byte is matched by a lowered class, which never admits a
  lone continuation byte. Is the rounding then unnecessary, and is that
  provable rather than merely likely? Q2 asks Frank.
  - [r1 S-F5] Measured by critic 1: removing the round-up entirely gave 0
    diffs over 13 shapes. Not a proof; S471 keeps a STRUCTURAL detector
    because it reads unreached on answers. The round-up that stays is
    uncapped and taken only when `lo > f` ([r1 S-F6]).
- **H7 — One writer of the state.** The initializer reads the moved start,
  and nothing else writes the state at entry. Does any `seedhead`
  (`goto … seeded straight onto a scan-edge head`) or view-selection
  initializer read `search_from` separately?
- **H8 — The hybrid's superset prefilter.** Is calling it first at `lo` as
  sound as its retries at `attempt_position` (D51 ruling 2)? And is
  `window_end`, set from its first answer on the clamped arm, still a
  bound on the match's end?
  - [r1 S-F3] Answered for the filter, held for `window_end`: the
    retries already read `attempt_position` as `\G`, so the first call at
    `lo` is a retry's shape; but `window_end` on a clamped `\G` hybrid is
    declined by (d′) until the build reads its writer (Q9).
- **H9 — Pinned and empty forms.** Is the pinned form unreachable? The
  argument is that a nullable pattern has no run. The empty engine emits
  no gate.
- **H10 — "A suffix of the discard program's work."** Can starting at `lo`
  cost MORE than starting at `search_from`?
  - A seeded `lo` is not `s0`, so `pf_open`'s prefilter does not fire
    until the machine returns to `s0`. The machine is at the candidate
    anyway.
  - On the hybrid, the first prefilter answer at `lo` may come later than
    at `search_from` but never earlier, and the VM attempts fewer.
  - **[r1 S-F2] Corrected.** "The VM attempts fewer" was wrong. Wherever
    K bounds the prefilter's language (the exact language, or an erasure
    of zero-width nodes), the prefilter never answers below `c − K` (§4.2
    item 1), so the VM attempts EXACTLY the same positions with or
    without the handoff. The saving on the hybrid is the prefilter's scan
    of `[f, lo)` and nothing else. Only a count-collapsed prefilter can
    answer below `c − K`, and there the VM does attempt fewer; that is the
    one population where the give-up surface can move, and it is measured
    empty.
- **H11 — The pair arm's per-call overshoot** (`mod-i`'s residual). It is
  not addressed, and it is not this row: no cross-call state exists to
  carry a stream's lookahead. Its general answer is the pair arm's
  emission, or [MEMFN]'s binding-form criterion (k82cost's Q7).
- **H12 — Stamp population.** Every artifact gains a line. Is that the
  right trade against "only movers carry it"? (Q3.)
  - [r1 C-C1] Answered no: §2.3a enumerates what every-artifact moves, and
    the revised Q3 recommends movers-only.
- **H13 — [r1 S-F1] The gate's return value.** The gate must return the
  LEFTMOST occurrence at or after `search_from` (§1.1a). Today nothing
  checks it. S464 does.
- **H14 — [r1 S-F9] Latent body bugs.** A body bug at a non-zero startpos
  is now reached on calls from 0 (Claim 3's note); the per-route
  every-startpos sweep is the check.

**Open questions for Frank** moved to §Q below, revised by the r1 panel.

## §Q. Questions for Frank (revision 2)

Revision 1 asked Q1-Q8 here. The revised set follows; each carries a
recommendation. Q3 is reversed by [r1 C-C1]; Q9 and Q10 are new.

- **Q1. A new axis (`req-use`, a two-row table) rather than a property of
  `req_admits[]` or `dfa_pfs[]`?**
  **Recommendation: yes** (§2.1). The handoff answers its own question
  and composes with both tables. [r1 C-C10] Row 1 CALLS `req_admit()`
  rather than restating it, and §5.12 checks the two tables agree.
- **Q2. The utf8 round-up: keep it, or drop it on a proof (H6)?**
  **Recommendation: keep it in the first build**, in its revised form:
  uncapped (`< subject_length` its only bound, [r1 S-F5]) and taken only
  when `lo > f` ([r1 S-F6]). It keeps the soundness argument a pure
  reduction to the startpos contract. Critic 1's 0 diffs over 13 shapes
  with it removed is evidence, not a proof; if a proof arrives, it comes
  out in a later abi event with S471's structural detector inverted.
- **Q3. `REQ_HANDOFF` on every artifact, only where the handoff applies,
  or in `--emit-facts` only?** [r1 C-C1] REVERSED.
  **Recommendation: stamp only on artifacts where the handoff applies
  (option b); facts-only (option c) is acceptable.** The blast radius of
  each, from §2.3a's grep:
  - **(a) every artifact (`"none"` elsewhere).** Every byte-count reader
    moves though no program does: all 12 `EMITTED_BYTES` rows of
    `m5_stage1_stamps.tsv`, the resource suite's 762,574-byte pin, every
    row of `artifact_size_log.tsv`, every artifact of the recursion
    identity gate's whole-file sweep, and the findings mover manifests
    must be re-derived to show no false mover. The deny arm weakens to
    "DENY == BASE modulo one line". Revision 1 chose this for the
    `REQ_WHY` presence rule; the grep says it is the expensive spelling.
  - **(b) movers only.** Byte movement is confined to the program movers:
    2 of the 12 `EMITTED_BYTES` rows (`\bword\b`, `(?i)HeLLo`), the
    resource pin unmoved, the size log's mover rows only. DENY == BASE
    modulo the abi digit alone. D46's observability holds: the stamp is
    present exactly where the program differs, and `--emit-facts` states
    the `req-use` decision on every artifact.
  - **(c) facts-only.** The same byte movement as (b) minus one line per
    mover. Observability rests on `--emit-facts` and on the
    `handoff_position` text; §5.12's presence check compares the facts row
    with the text (still two sources). It departs from the house idiom
    that a selection which changes the program is stamped in the
    artifact, which is why it is the second choice.
- **Q4. The L = 1 case** (a one-byte pre-check's `memchr` hit handed off,
  needing per-byte offsets for the SET).
  **Recommendation: file it, don't build it (D77).** Unchanged: cause (B)
  is runs only, and the trigger is a measured byte-only pre-check mover on
  match-dense text.
- **Q5. A cap on K?**
  **Recommendation: none.** Unchanged: any finite K is sound, and a large K
  degrades to `lo = search_from`.
- **Q6. Tighten the DFA reverse pass's lower bound to `lo`?**
  **Recommendation: no.** Unchanged: it moves text on every DFA mover for
  no measured gain.
- **Q7. The VM with no DFA scan** (attempts from `lo`, sound by Claim 1).
  **Recommendation: file it, don't build it.** Unchanged: 0 forced-VM
  movers with a measured loss; K49's encoding-advance discipline needed.
- **Q8. Sequencing.**
  **Recommendation:** build on `lane/k82fix` after it lands, as its own
  commit and abi event; the light panel (r1) is done and this revision
  applies it. The build lane's brief names §1.1a's gate contract, and so
  does the next [MEMFN] build brief ([r1 S-F1]). The cost model stays
  parked behind §3.3's 8-cell measurement.
- **Q9. [r1 S-F3] Drop the (d′) decline (`\G` + clamped window on the
  hybrid) later?**
  **Recommendation: keep it in the first build.** Its measured population
  is zero, so it costs nothing, and it removes the one read (`window_end`)
  the soundness argument does not cover. The build lane reports whether
  `window_end` is re-derived from every prefilter answer or only the
  first; if every, (d′) comes out in a later abi event with S476 inverted.
- **Q10. [r1 S-F2, C-C8] The count-collapsed give-up allowance: keep it,
  or decline the handoff on count-collapsed prefilters?** §4.2 narrows the
  allowance to count-collapsed hybrids, the one place the VM's attempts
  change. Two ways to finish it:
  - keep it: the handoff skips provably failing attempts there too, a
    budget-limited search can then answer where `-fno-req-handoff`'s gives
    up, and the spec says so (§2.3a's last sentence); the build must
    construct a witness, because the measured population is empty;
  - decline: add a conjunct (no handoff when `RX_VM_PREFILTER_LANG` is
    `count-collapsed`), and then `-fno-req-handoff` never moves the
    give-up surface, with no exception and no spec sentence.
  **Recommendation: decline.** The population is measured empty on corpus
  and bench, the count-collapsed rung is a fallback-only ladder attempt
  (ruling B), and the decline keeps K65/K66's invariant (a deny flag does
  not move `PCREC_ERR_STEPS` against a result) exceptionless. If a
  count-collapsed mover with a measured give-up ever appears, the
  allowance is the D77 follow-on.

## 6. The lenses (memory: design evaluation lenses)

- **Specific vs general.** The general form is "a necessary literal
  found at a position bounds the earliest match start". The run is its
  L ≥ 2 instance, and Q4 names L = 1. No cell-specific clause.
- **Core vs derived.** The bound is a core walk fact (`whole_maxoff`). The
  window's K is derived (`+ at`, a rate choice). The use is an emission
  row.
- **Applicable vs assumption-changing.** It changes no contract
  assumption. It relies on the startpos contract, which already holds.
- **Fits the architecture vs refactor.** One fact field, one table, and
  three start sites that already exist. No new body shape.
- **Shared question / engine hat (D124).** "Where may this call's scan
  begin?" is one question. Three bodies wear the hat through one returned
  expression (§2.1).

## §R. Revision 2: the r1 panel's findings and where each is answered

Panel record: `../dev/reviews/2026-10-04-r1-k82-handoff.md` (critics
k82hcrit1, opus, measuring; k82hcrit2, sonnet, reading). All 17 findings
ACCEPTED by the manager; this table maps each to the text that now answers
it. Every change is marked `[r1 <id>]` in place.

| id | sev | finding (short) | answered in |
|---|---|---|---|
| S-F1 | MAJOR | the gate's return value is load-bearing (leftmost, ≥ `search_from`) | §0 item 6; §1.1a (the contract in `ofs_test_emit_fn`, the pair arm, [MEMFN]/S4 bound by it); §4.2 item 2 two-occurrence rows; S464; H13; Q8 |
| S-F2 | MINOR | the give-up→match allowance is too wide; H10 wrong | §4.2 item 1 (allowance only on count-collapsed prefilters, measured population 0); §3.1a (every hybrid mover `exact`); H10 corrected; Q10 |
| S-F3 | MINOR | the hybrid's prefilter is a third `\G` reader | §1.1's table; Claim 2′ (the third reader, the retry precedent, `window_end`); §1.4 (d′); §4.2 item 2 `\G`-hybrid row on `(?:\Gab\|x)(cat)dog`; §5.12 "`\G` readers"; S469, S476; H1, H8; Q9 |
| S-F4 | MINOR | nothing excludes verbs/callouts | §1.4 (g) (reads [OPT-HYB-RESEED]'s fact; unreachable today, measured); S475; H1 |
| S-F5 | MINOR | "≤ 3 tests" round-up is false on ill-formed input | §0 item 4; §1.1 (uncapped loop); §1.4 (e); §4.2 item 1 ill-formed sweep and item 2 rows; §4.3 edge rows; S471 structural, S472; H6; Q2 |
| S-F6 | NOTE | rounding when `lo == f` changes `-fno-startpos-guard` behaviour | §1.1 (round-up inside the `> K` branch); Theorem; §1.4 (e); §5.12 "the round-up" |
| S-F9 | NOTE | every-startpos correctness becomes load-bearing | Claim 3's note (incl. the [UCP] U3/U4 cross-note); §4.2 item 1 per-route sweep; H14 |
| C-C1 | MAJOR | §2.3's reader list misses the byte-count readers | §2.3a (grep commands on main and `lane/k82fix`, both reader classes, per-option movement); §2.2 movers-only stamp; §3.1; Q3 reversed with the blast radius of (a)/(b)/(c) |
| C-C2 | MAJOR | DD12a(i) goes red on the movers | §4.2b (named region, `REQ_HANDOFF` normalizer, floor, 8-line ceiling); S477 |
| C-C3 | MAJOR | bit 46's membership in `strategy_denials` | §2.3 (joins the mask, why, and why it is not the wave-G exception); §4.1 deny arm |
| C-C4 | MAJOR | the manifest's controls share `rb_walk` with the build | §4.1 "what this manifest is NOT"; §4.2a (a) hand K pin table, (b) independent invariant-F oracle against libpcre2/python `re`, (c) K−1 over the whole mover population with the count; the thin K > 0 population stated (27 corpus, 14 bench) in §3.1a and §4.2a |
| C-C5 | MAJOR | S464/S465/S466/S472 (old numbering) had detectors outside the suite | §4.2 item 4 (§5.12 carries every detector); §4.4's detector column |
| C-C6 | MAJOR | [MECH-REACH]: witnesses that do not reach | §4.4's `SAB_REACH`/`SAB_REACH_POP` columns with constructed witnesses; §3.1a (no `\G` hybrid mover, so S469's is constructed) |
| C-C7 | MAJOR | the utf8 population lacks ill-formed/truncated subjects | §4.2 item 1 and item 2 ill-formed rows; §4.3 |
| C-C8 | MAJOR | "unobservable by the contract" is false for give-up | §3.1a (35 budget/`gu` blocks, 0 movers); §2.3a's revised spec sentence; §4.2 item 1; Q10 |
| C-C9 | MINOR | census misses `--no-captures` corpus and forced hybrids; test-axes subset too narrow | §3.1a (`k82h_census_r2.out`); §4.1 populations; §4.2 item 3 (eight flags, GROUP F4) |
| C-C10 | MINOR | `req_uses[]` should call `req_admit()`; row 2's "discard" text | §2.1 (row 1 calls it, row 2 renamed `scan-from-startpos`, the cross-table check); §4.2 item 4; Q1 |
| C-C11 | NOTE | "declared iff numeric" is self-agreement; pin `ci-strasse` K = 2 | §4.2a (a)'s hand table, first utf8 row |

**Sabotage rows**: S463-S477, fifteen, contiguous (§4.4, with revision
1's mapping). **Frank questions**: Q1-Q10 (§Q).

## Rulings (Frank, 2026-10-05)

- **Q1 YES:** the separate two-row `req_uses[]` table (axis `req-use`, `-fno-req-handoff`, bit 46). Frank notes the behaviour itself was his earlier recommendation; see the two LINEAGE paragraphs at the top.
- **Q2 KEEP:** the utf8 round-up, in its revised form (uncapped `< n` loop, only when lo > f).
- **Q3 (a), REVERSING the note's own recommendation:** `<PREFIX>_REQ_HANDOFF` goes on EVERY artifact of the family, `none` where the handoff does not apply. House convention: stamps vary only by engine family, never by presence within a family, and "does not apply" is a value. The byte-count readers §2.3a lists are re-pinned in the build's own change (the abi ritual).
- **Q4 FILE, DON'T BUILD:** the one-byte pre-check handoff (L = 1) is filed as a row; D77 trigger = a bench cell where a one-byte `memchr` pre-check pays the rescan.
- **Q5 NO CAP on K:** the handoff limits itself (a large K degenerates to today's start). K is guarded by the independent pin table, oracle and K−1 plant, not by a threshold.
- **Q6 NO:** the reverse pass keeps its `search_from` lower bound (sound, tested incl. `\K`). Revisit only on a measured cell where it walks below lo.
- **Q6 NOTE (Frank, 2026-10-05):** tightening the reverse pass's bound to lo should give the SAME answer by construction, which makes it a candidate TEST CASE: a variant with the bound at lo, diffed against the shipped one, is a free equivalence check on K and the proof. Noted; no action yet.
- **Q7 FILE, DON'T BUILD:** the no-DFA-scan VM handoff is [OPT-VMSEED]'s territory (cross-noted there); its trigger is a VM-route cell that measurably pays the rescan.
- **Q8 BUILD NOW** on main as its own abi event (60 -> 61): lane k82hbuild, Mac validation first, Linux alpha (alpha_k82h.sh) in the next daytime slot.
- **Q9 KEEP** the (d′) decline (`\G` with the clamped prefilter window); population 0, closes the one unproven case.
- **Q10 DECLINE** the handoff on count-collapsed prefilters (no give-up→match allowance anywhere); population 0 on corpus and bench.
