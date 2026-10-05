# K82 cause (B): the HANDOFF — the run pre-check's candidate becomes the scan start

**Status: PROPOSED (design only, lane `k82hand`, 2026-10-04, from
`lane/k82fix` `f0d0b206`, abi 60).** Nothing under `src/`, `tests/` or
`docs/spec/` moves here. Frank's ruling (`known_issues.md` K82, "REVISED
2026-10-04", on `litscan_k82b.md`): the T3 handoff is built FIRST, as its own
row after k82fix, light D6 panel first. It fixes cause (B) with no rates and
no threshold. The expected-cost model and its [FINDINGS.B4] reader are parked
behind a census of unbounded-offset runs that still lose after this lands
(§3.3 gives that population).

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
constructed witness, `(?:\G|x)(cat)dog` (VM hybrid, exact prefilter, K =
1 on the prototype), and S469's plant and §5.12's "no `\G` reader" check
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
    encoding-advance discipline. It is filed, not built (§5 Q7).
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
  possibly handed off (`REQ_HANDOFF`)"; §3.1's sentence (§4.2a gives its
  revised text).
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
  `(?:\G|x)(cat)dog` is a VM hybrid, `exact` prefilter, K = 1 on the
  prototype.

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
  `-fno-req-handoff`. The abi digit is normalized at its sites.
- **NEW vs BASE: the PROGRAM moved iff predicted.** The prediction is
  recomputed in Python from NEW's `--emit-facts`: `REQ_WHY` "emitted", a
  run, a DFA-scan route from the stamps, and `req_run_maxoff` finite.
  - On a predicted mover, `REQ_HANDOFF` equals that K.
  - On every other artifact, the only difference is the stamp line
    `"none"`.
  - Off-diagonal cells are failures.
- **DENY vs BASE:** identical on every artifact, modulo the one stamp line.
- **The fact's own check.** NEW's `req_whole_run` equals BASE's on every
  artifact: the offset is an annotation and must not move the choice.
- **Populations:** the §3.1 table's, reconciled count for count (K35: an
  empty or shrunken population is a failure).

### 4.2 Answer identity

1. **The differential.** `c3_answers.py`'s shape, run over every program
   mover with BASE := DENY. The driver is `possdiff_driver.c`: span, every
   capture slot and the failure surface, at EVERY start position. The
   subjects are `b1_mover_answers.py`'s sweep plus `PREFIXES=1`.
   - **Allowed changes:** `give-up → NOMATCH`, and `give-up → match` where
     the match equals DENY's at an unbounded step budget. The hybrid
     skips failing attempts before `lo`, so it can no longer exhaust a
     budget there.
   - **Every other change is a DEFECT.**
2. **The handoff witnesses**, a new `tests/litscan/handoff.rxt`. It is
   generated by a `gen_handoff.py` with python3 `re` expectations; utf8
   rows are `re` over `str`, and the K73 continuation-byte rule is checked
   against the 10.46 transcript where `re` cannot speak. Each pattern runs
   under every engine row the harness runs (auto, vm, the `-fno-*` axes),
   at every startpos.
   - **The maximum-offset case.** The match begins exactly K bytes before
     its window: `x{2,5}(?i)cat` on `xxxxxCaT`, and `(?:a|bb)?catdog` on
     `bbcatdog`.
   - **Decoys.** A false run occurrence within K bytes BEFORE a real match:
     `a{3}(?i)cat` on `cat aaacat`, where lo lands inside the decoy's
     span.
   - **Near the startpos.** The run within K of a non-zero startpos: the
     underflow clamp, startpos = 1..K.
   - **Multibyte width.** `(?i)straße` on `ſtraße`, `éſtraße` and
     `xſTRASSE`. Here lo = c − 2 lands on a continuation byte, which tests
     the rounding. Also `.{3}cat` and `é{2}cat` under utf8 with 2/3/4-byte
     characters in the prefix.
   - **Seeded starts.** `\bcat\b` and `(?<![a-z])cat` with a word
     character at lo − 1 and lo − 2 (on the DFA route, and on the hybrid
     for the lookbehind).
   - **The attempt route.** `(?m)^item` (ENG_ATTEMPT), and `(?:\G|x)cat`
     and `\Gx|yx`-shaped `\G` rows on whichever route the selector gives
     them (Claim 2′).
   - **`\K`.** A row on the route that carries it: offsets are from the
     attempt start.
   - **Find-all.** Dense matches (`(?i)cat` over `cAtCaTcat…`) and
     overlapping run occurrences (`aa(?i)a` style).
   - **A run that begins on a continuation byte:** `(?:éx|ʩx)`.
   - **Controls.** `a.*?(?i)select` (unbounded, must not move) and the
     forced-VM rows (must not move).
3. **The corpus and identity gates.**
   - `make test`: the `.rxt` corpus on every engine row, every identity
     gate after its re-pin, and the codegen structural checks.
   - `make test-axes AXES="-fno-req-handoff -fno-req-set-lead
     -fno-req-run-fold"`. That is the new flag plus its two neighbours,
     because the deny of each must compose. The full `test-axes` is the
     batch gate's (D144 item 2).
4. **Structural checks** (`tests/codegen/run_prechecks.sh`, a new §5.12),
   read off the TEXT:
   - `handoff_position` is declared iff `REQ_HANDOFF` is a number;
   - its subtraction constant equals the stamp;
   - exactly one start site reads it per body (the DFA initializer and
     `scan_position`, the attempt loop, or the hybrid's first call);
   - no `\G` reference reads it;
   - the utf8 rounding is present iff the encoding is multibyte;
   - the deny row reads `"none"` and the abi-60 gate line.

### 4.3 ASan/UBSan

- **The sweep.** The §4.2 item 1 differential under
  `CFLAGS="-fsanitize=address,undefined -fno-builtin-memcmp
  -DDIFF_EXACT_SUBJECT"`, over every program mover (every subject in a
  block of exactly its length). This is `c3_answers_san.log`'s run.
- **Edge subjects.** `n = 0` with a NULL subject; a startpos at `n` and at
  `n − 1`; a match at offset 0 with K > 0 (the clamp); utf8 subjects that
  END in a truncated sequence after the run (the rounding's bound).
- **The control.** A planted out-of-bounds read in the rounding loop
  (`< n` dropped) must be caught: `S455`'s precedent, a sanitizer control
  that is itself sabotaged once.

### 4.4 Sabotage rows (numbered from S463; check main's highest at landing)

| row | plant | detector |
|---|---|---|
| S463 | the subtraction uses K − 1 (lo one byte too late) | `handoff.rxt` maximum-offset rows (the match at exactly c − K is lost) |
| S464 | the walk's width counts a `A_WCLASS` / multi-byte class as 1 byte (the `cwmax` mistake) | `handoff.rxt` `ſtraße` / `.{3}cat` utf8 rows; the manifest (`ci-strasse` K 2 → 1) |
| S465 | `A_ALT`'s width takes the LEFT branch, not the max | `(?:a\|bb)?catdog` on `bbcatdog`; the manifest's K column |
| S466 | the `bounded` conjunct dropped (an unbounded run handed off at K = 0) | `a.*?(?i)select` and `union-select` rows; the manifest (unbounded artifacts move) |
| S467 | the seeded initializer keeps reading `search_from` while `scan_position = handoff_position` | `\bcat\b` with a word character at lo − 1 (a match reported or lost on the wrong context) |
| S468 | the hybrid passes `handoff_position` into `search_from` (the `\G` anchor moved) | the `\G` hybrid row; `run_prechecks.sh` §5.12's "no `\G` reader" check |
| S469 | the underflow-safe form replaced by `c - K` with no clamp | the startpos 1..K rows (size_t wrap → NOMATCH where a match exists) |
| S470 | the utf8 rounding dropped | the `éſtraße` / `(?:éx\|ʩx)` rows IF a wrong answer results, else the structural "rounding present" check alone. The panel's answer to Q2 decides which (H6) |
| S471 | `-fno-req-handoff`'s deny bit dropped from the row | `run_prechecks.sh` §5.12 deny row. NOT the registry suite: `--list-axes` walks the same row, a control sharing its source (k82fix's S462 lesson) |
| S472 | the run choice moved: `rn_better` prefers a bounded run | the manifest's `req_whole_run` equality check (§4.1) |

Every row is checked single-row for [MECH-REACH]: the witness must reach
its site on the plant's tree. Anchors are copied from
`git show HEAD:<path>` at landing.

### 4.5 The Linux alpha cells (D144)

`alpha_k82.sh`'s protocol: `taskset -c 2`, loops of at least 50 ms, base
and deny as the floor, absolute deltas for per-call cells (D144
addendum 1). The arms are:
- BASE = abi 60;
- NEW;
- DENY = NEW + `-fno-req-handoff`, where DENY == BASE in program text.

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
- **H7 — One writer of the state.** The initializer reads the moved start,
  and nothing else writes the state at entry. Does any `seedhead`
  (`goto … seeded straight onto a scan-edge head`) or view-selection
  initializer read `search_from` separately?
- **H8 — The hybrid's superset prefilter.** Is calling it first at `lo` as
  sound as its retries at `attempt_position` (D51 ruling 2)? And is
  `window_end`, set from its first answer on the clamped arm, still a
  bound on the match's end?
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
- **H11 — The pair arm's per-call overshoot** (`mod-i`'s residual). It is
  not addressed, and it is not this row: no cross-call state exists to
  carry a stream's lookahead. Its general answer is the pair arm's
  emission, or [MEMFN]'s binding-form criterion (k82cost's Q7).
- **H12 — Stamp population.** Every artifact gains a line. Is that the
  right trade against "only movers carry it"? (Q3.)

**Open questions for Frank**, each with a recommendation:

- **Q1. A new axis (`req-use`, a two-row table) rather than a property of
  `req_admits[]` or `dfa_pfs[]`?**
  **Recommendation: yes** (§2.1). The handoff answers its own question,
  and it composes with both tables.
- **Q2. The utf8 rounding: keep it, or drop it on a proof (H6)?**
  **Recommendation: keep it in the first build.**
  - It makes the soundness argument a pure reduction to the startpos
    contract.
  - It costs at most 3 byte tests per passing call, on utf8 movers only.
  - If the panel proves the DFA and hybrid never begin a match on a
    continuation byte for a run-bearing pattern, it can come out in a
    later abi event with S470 as its detector.
- **Q3. `REQ_HANDOFF` on every artifact ("none") or only on movers?**
  **Recommendation: every artifact**, the `REQ_WHY` presence rule. Every
  artifact moves at the abi digit anyway, and a stamp whose absence means
  something is a reader's trap.
- **Q4. The L = 1 case.** A one-byte pre-check's `memchr` hit could be
  handed off by the same rule if the walk tracked per-member offsets for
  the SET. The set is intersected at `A_ALT`, so that needs offsets per
  byte, `reqpos_probe.c`'s `pmax[256]`.
  **Recommendation: file it, don't build it (D77).** Cause (B) is runs
  only. The trigger is a measured byte-only pre-check mover on
  match-dense text. The table already has the row. Only the fact would
  widen.
- **Q5. A cap on K?**
  **Recommendation: none.** Any finite K is sound, and a large K degrades
  to `lo = search_from`, which is today's work plus one compare. The
  census's largest bench K is 32.
- **Q6. Tighten the DFA reverse pass's lower bound to `lo`?**
  **Recommendation: no.** It moves emitted text on every DFA mover for no
  measured gain (§1.2's note), and it would make the reverse pass a
  fourth consumer.
- **Q7. The VM with no DFA scan.** Its attempts could start at `lo` too,
  which is sound by Claim 1.
  **Recommendation: file it, don't build it.** There are 0 forced-VM
  movers with a measured loss, the pre-check there is K65/K66's no-match
  proof, and an advance there must take K49's encoding-advance discipline.
- **Q8. Sequencing.**
  **Recommendation:** build this on `lane/k82fix` after it lands, as its
  own commit and abi event, with the light panel on THIS note first (the
  ruling). The cost model stays parked behind §3.3's 8-cell measurement.

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
