# [MATCH-SPLIT] 4a — the pin-only split (DESIGN NOTE)

Lane `msdesign` (2026-10-12, opus), from main `33c2eb7a` (abi 76). **Design only.** Nothing
under `src/` is changed or built. The one kind of evidence taken is reading stamps and
emitted code from single `build/pcrec` compiles on this branch (`build/ms/`, not committed).
Inputs: `match_split_requirements.md` (§2 requirements, §2.2 classes, §3 costing, §5.1
rulings including Q5 and the 4a scope of 2026-10-12), `../dev/lanes/mssurvey_report.md` with
`../dev/optloop/matchsplit/{summary,qwork}.txt` (the counts), D156 and its addenda, D158,
D151 addendum 6, `cand_rows[]`/`cand_nodes[]` (`src/gen/emit_dfa.c:8654`, `:8850`), and the
[OPT-REVEND] walk (`emit_rev_end`, `src/gen/emit_dfa.c:11645`). Plan row `[MATCH-SPLIT]`
(chunk 4a of `../dev/chunks_2026-10-11.md`); it owns K106.

Read §0 first. §1 is the scope, §2 soundness, §3 the locators, §4 the tables, §5 cost,
§6 the interface, §7 the checks, §8 the build steps, §9 the questions and unlocks, §10 the
standing questions, §11 the findings.

## 0. Answers first

1. **The split's classes fall into two kinds, and that is what makes pin-only cheap.** A
   FLOOR class (`^`/`\A`, `\G`) has exactly one candidate, and it is the smallest position a
   match can start at: 0 when `search_from == 0`, else `search_from`. A RACING class (`$`,
   `(?m)^`, `(?m)$`, and later FREE) has candidates spread over the subject. Try the floor
   first. If FINISH succeeds there, nothing else can start earlier, so the call is over. If it
   fails, the racing class's leftmost candidate IS the answer. So with **at most one racing
   class** the split does no work that it throws away, and needs no state across calls. That
   holds for S+E and G+E, and for 4b's S+F and G+F. With **two racing classes**, the loser's
   work is thrown away and may be repeated on the next call. That is the 4c problem; it
   covers LS+LE, LS+E, E+F and LS+F (§1.2).
2. **4a admits FLOOR + E: S+E, G+E, S+G+E.** These are 22 of mssurvey's 35 pin-only patterns:
   all 21 S+E (9 of K106's 11 counted trim shapes, the utf8 2016-outage form, the wrapper strip
   and its captured hybrid form, `^|end$`, `^|$`) plus G+E. S+LS and G+LS are already served by
   today's MLINE candidate skip. E+LE is already served by today's unanchored composite. Both
   are degenerate members that 4a leaves byte-identical. Declined with a named home: S+LE →
   4b (its LE class is served by the composite over the floor-free machine, 4b's mechanism),
   and LS+LE → 4b.2 (two racing classes; K106's two `(?m)` trim shapes stay quadratic until
   then, Q2).
3. **The locator reuses two existing rows.** The floor is one iteration of today's ATTEMPT
   loop, bounded by two new BOUND rows whose texts are `bot`'s and `gstart`'s. The END class is
   today's `rev-end` walk run over **Q**: the reverse machine of the pattern with its
   BOT-family NFA nodes killed (`N_BOT`, `N_BOT_M`, `N_GSTART`, the exact kind set of
   `pcrec_nfa_has_bot`, `src/ir/nfa.c:1225`). Q is therefore exactly the ENG_UNANCH-routable
   remainder of the pattern. A tie between the two `$` seeds is resolved inside the locator by
   one attempt of the ATTEMPT machine at the walk's start, so the locator hands FINISH only
   SPAN or NOMATCH, and FINISH gains no take cell. This is one new LOCATE row, `split`, on
   CAND_ROUTE_ATTEMPT (§4).
4. **Soundness is arithmetic plus rev-end's own proof (§2).** Floor paths can start only at
   the floor. Every non-floor path is end-pinned, so it is a path of Q. Q's walk finds the
   leftmost Q start. FINISH at the floor and at a tie runs the FULL machine, which gives
   priority. A single seed at `s*` has exactly one possible end.
5. **Linear by count (§5).** K106's subject `Q·\t^k·Q` at k = 16,000 costs 128,040,002
   subject loads today and 2 under the split. The wrapper strip makes n+3 attempt entries per
   call today and at most 1 under the split. A dominance argument gives the admission with no
   constant: on every subject, split loads ≤ today's loads + 2 per call. Find-all runs at most
   three walks, so it needs no cross-call cache, which confirms the §5.1 Q2 answer for this
   member.
6. **Interface (§6).** `RX_DFA_SCAN "split"` (`rx_info.scan` is a `const char *`, so the
   layout does not change). `RX_DFA_START` becomes `"reverse-pass"` on split artifacts by the
   generated stamp rule (D156 add. 2). There is one new fact, `pin_split`. One deny, the
   combinator's: a new bit `-fno-match-split` (bit 55, leaving 8 free against the ≤ 4 trigger;
   Q1). `-fno-rev-end` also removes the row. It is an abi event. There is no kit request: the
   walk reaches the delegated EDGE/STAY sites rev-end already reaches. One size-ladder rung,
   `drop-split`, is shaped like `drop-anchored`.

## 1. Scope

### 1.1 Floor and racing classes

The classes are those of `match_split_requirements.md` §2.2. They are defined on PATHS: an
absolute anchor anywhere on a path pins it, and a line anchor pins only at the path's edge.

| class | kind | candidates per call | evaluated |
|---|---|---|---|
| S (`^`, `\A`) | FLOOR | {0} if `search_from == 0`, else none | first, one attempt |
| G (`\G`) | FLOOR | {`search_from`} | first, one attempt |
| E (`$`, `\Z`, `\z`) | RACING | starts of matches ending at `n` or `n−1` | after the floor fails |
| LS (`(?m)^` leading) | RACING | line starts ≥ `search_from` | forward enumeration |
| LE (`(?m)$` trailing) | RACING | starts of matches ending at a line end | forward scan (no pin locator) |
| F (free) | RACING | anywhere | forward scan (4b/4c) |

**The rule.** A floor candidate is ≤ every other candidate, because 0 ≤ `search_from` ≤
any racing candidate. So the floor is tried first. If the full machine matches there, that
match is the leftmost and the call ends. If it fails, the floor is dead for this call. With
one racing class left, its leftmost candidate is the answer, and none of its work is
discarded. With two racing classes, a class that loses to the other has scanned for nothing.
Under the stateless API the next call redoes that scan, which is §3.1 item 3's repetition.
That is the dividing line between 4a/4b and 4c.

### 1.2 The census mixes, member by member

mssurvey's pin-only population (`summary.txt` §3) is 35 patterns:

| mix | count (corpus / idioms) | today's route | 4a | why |
|---|---|---|---|---|
| S+E | 21 (1 / 20) | `dfa-attempt[n]` ×20, `hybrid-attempt[n]` ×1 | **ADMITTED** | floor + one racing (E) |
| G+E | 1 (1 / 0) | `dfa-attempt[n]` | **ADMITTED** | floor + one racing (E) |
| S+LS | 1 (1 / 0) | attempt + MLINE `memchr('\n')` | unchanged | 0 is a line start, so today's skip already enumerates {floor} ∪ line starts (stamp `RX_DFA_PREFILTER "memchr"`, read on this branch) |
| G+LS | 2 (2 / 0) | attempt + MLINE | unchanged | the skip's bound is `search_from` under a `\G` family (`emit_dfa.c`, the [M6.2 wave D] note above `pcrec_emit_find(... DELEG_MLINE ...)`) |
| E+LE | 3 (3 / 0) | `dfa-unanchored` | unchanged | no floor; today's forward composite serves both racing classes in one pass, so it IS their union locator |
| S+LE | 1 (1 / 0) | `hybrid-attempt[n]` | declined → 4b | LE has no pin locator; its locator is the composite over the floor-free machine, which is 4b's mechanism (S+F) |
| LS+LE | 6 (2 / 4) | `dfa-attempt[n]` | declined → 4b.2 | two racing classes; includes K106's `(?m)^\s+\|\s+$` and its comment variant (Q2) |

So 4a admits 22 patterns and changes nothing for the other 13. There are 0 bench patterns
(Q5 ruled zero bench reach). LS+E is UNREACHED (0 patterns). It would need the 4c admission
unless its E arm is bounded: an E start at or after `n − W − 1` cannot precede a line-start
candidate `c < n − W − 1`, so the walk is skipped there. That is the §5.1 cheap test.

## 2. Soundness (brief item 1)

Notation: P is the pattern (on ENG_ATTEMPT, since it has a BOT-family node). Its live paths
are FLOOR paths (carrying S or G) and E paths (no floor pin, an absolute end pin). Under 4a's
admission there are no others. Q is P's NFA with every BOT-family node killed, so Q's paths
are exactly P's non-floor paths. `f` is the floor: 0 when S is the only floor kind and
`search_from == 0`; `search_from` when G ∈ floor. When S is the only floor kind and
`search_from > 0`, `f` does not exist. `s*` is the walk's result: the smallest position ≥
`search_from` at which Q's reverse machine, seeded at an allowed end, accepts.

- **Leftmost across classes (R1).** Take any P-match starting at `p ≥ search_from`. On an S
  path, `p = 0`, which forces `search_from = 0 = f`. On a G path, `p = search_from = f`. On
  an E path, it is a Q-match, so `p ≥ s*`. So the leftmost start lies in {f} ∪ [s*, ∞), and
  `f ≤ s*`. If P matches at `f`, the leftmost start is `f`. Otherwise it is `s*`, because Q's
  paths are P's paths, so P matches at `s*`. Otherwise there is no match. The walk finds `s*`
  exactly by rev-end's proof (`revend.md` §3.1): every E path ends at a seed (`n`; and `n−1`
  when `s[n−1] = '\n'` under `$`/`\Z`), and the seeded reverse machine accepts exactly at the
  starts of the Q-matches ending there.
- **Priority at a start (R2).** At `f`, the attempt runs P's full machine, which is today's
  attempt at `f`, byte for byte. At `s*`, every P-match is a Q-match. Floor paths cannot
  start there: if `s* = f`, the attempt at `f` would have matched, a contradiction. So the
  possible ends at `s*` are exactly the seeds that reached it. If one seed did, there is one
  end, and SPAN is the priority match. If two did, the tie is resolved by one attempt of P's
  full machine at `s*`, which is guaranteed to match because `s*` is a real start (§3.2).
  This matches today's priority, which is PCRE2's.
- **Zero-width START arm (§5.1, `^|end$`).** On `"end"`, call 1 tries the floor at 0. The
  full machine's priority returns `(0,0)`, and the END class is never consulted. Call 2
  arrives with `search_from = 1`. S is dead, and the walk over Q = `end$` is floored at 1, so
  it cannot reach 0, and the call returns 0. That is `(0,0)` only, which is today's answer
  and the documented loss of `match_api.md` §3.1.3. On `"xend"` the walk gives `(1,4)`. On
  `"x"` it gives no second match. On `"end\n"`, the walk seeded at `n−1` reaches 0, but it is
  floored at 1, so `(0,0)` only, as today. NOTEMPTY (the emitted substitution loop of
  `replace_design.md` §3.8, and [FINDALL-NEXT]): the restriction is FINISH's. The floor
  attempt runs the full machine, so under "empty not permitted" it finds `(0,3)` itself. A
  future NOTEMPTY mode carries one obligation: if FINISH rejects an E candidate at `s*` (an
  empty E match), the walk must be retaken from `s* + 1`. No such mode exists today.
- **`^|$` and the two `$` seeds.** On `"a\n"`: call 1 gives `(0,0)` from the floor. Call 2
  (`search_from = 1`): seed `n−1 = 1` accepts the empty Q-match at 1, and seed 2 accepts at
  2. The minimum is 1, so the result is SPAN `(1,1)`. Call 3 (from 2) gives `(2,2)`. Call 4:
  `search_from > n`, so it returns 0. That is `(0,0),(1,1),(2,2)`, as today and PCRE2. On
  `""` and `"a"`: `(0,0)` from the floor, then `(n,n)` from the walk where `n > 0`.
- **`\G` and `search_from` (R4/R5).** G's one candidate is `search_from`, tried every call.
  The walk is floored at `search_from`. Q contains no `\G`, because the kill removes it, so
  `end_pin`'s decline (3) (`src/facts/endwin.c:180`, which protects the WINDOW clamp from
  moving `search_from`) is not inherited. This is why the walk's pin comes from the new fact
  (§3.3), not from `end_pin`.
- **`(?m)` line rules (R6).** 4a admits no LS or LE class. `N_BOT_M` is in the kill set only
  so that the reverse builder never meets a kind it cannot evaluate (`nfa.c:1195-1224`). Under
  the admission, every path through it is a floor path, so killing it removes no Q path.
- **`$`/`\Z` before a final newline (R7).** These are rev-end's two seeds and its `nl_last`
  test (`revend_nl_last`, `emit_dfa.c` above `emit_rev_end`), reused unchanged and
  parameterized by Q's pin (§3.3). `\z`-only Q gets one seed. Seeding `n−1` for a `\z` path is
  sound anyway: the walk accepts nothing there (the `pcrec_end_pin` comment, `endwin.c:159`).
- **Empty matches and the find-all advance (R3).** The split reports the same span as today
  on every call (above). So the caller's loop (empty advance `next_pos(start)`, non-empty
  advance `next_pos(end − 1)`) reads identically. A nullable Q (`\s*$`) accepts at the seeds
  themselves. `^\s*|\s*$` on `"  a  "` gives `(0,2)`, `(3,5)`, `(5,5)`, as today.
- **Context at a candidate (R8).** For the floor attempt, this is today's start dispatch (the
  `s0` / `gstart_seed_state` / `seed_state` arms of `emit_attempt`). For the walk, it is
  rev-end's floor obligation: the reverse walk's termination reads `s[search_from − 1]`.
- **utf8 (R10).** The floor is 0 or `search_from`, a boundary by contract (K73's offset-0
  rule is the attempt head's `PCREC_START0_SKIP`). The walk's accepting positions are lead
  positions (rev-end, K49/K50 by construction). The walk's head applies `PCREC_START0_SEEK`
  to `search_from`, as `emit_rev_end` does. That is safe after the floor attempt, because Q
  has no `\G`. The tie attempt at `s*` is at a lead position.
- **Captures (R9).** On the hybrid (`^(\s*)\{|\}(\s*)$`, `RX_VM_PREFILTER_LANG "exact"`,
  `RX_VM_RESEED "exact"`, read on this branch), the split body is the VM's inlined DFA. It
  hands the VM the same exact SPAN today's inlined attempt body hands, because ties are
  resolved inside the body. The VM runs `verify-at` over an identical window.
- **Give-ups (R11, D158).** The DFA routes carry no budget. On the hybrid the VM receives the
  identical window on every call, so its STEPS/FRAMES/WORK surface is identical, not merely
  one-way. Resolving ties in the body is what buys that. Handing ENDSET to the VM would send
  it to `search-from` with no window ceiling, which is a different give-up surface. So R11 is
  satisfied in its strongest form.
- **Dead paths.** `x^a|b$` is classified with a dead S path. Q is the live E part, and the
  floor attempt at 0 is wasted but sound (§4.2). Paths killed in Q that were dead already lose
  nothing.

## 3. The locators, all existing machinery (brief item 2)

### 3.1 The floor: one iteration of today's attempt loop

`emit_attempt` (`emit_dfa.c:12035`) already writes `for (start = first; start <= start_max;
start++)` (`:12251`) with `start_max` from BOUND's row (`:12215`). The split asks BOUND on
CAND_ROUTE_ATTEMPT exactly as today, and BOUND gains two rows (§4.1). Their texts are those of
`bot` (`"0"`) and `attempt-gstart` (`"search_from"`). They have `.one = CAND_ONE_NONE`,
because other starts CAN match: it is the racing class's. That way no `CAND_BOUND_ONE` reader
(P2, N12, N7, R3) concludes "one attempt". NEXT stays on the path unchanged. MLINE's skip
never skips the floor (its guard is `start > 0` / `start > search_from`), and it cannot skip
a real start such as the tie's `s*`. Soundness of that is by construction: a skipped start's
state is dead (the [D63] note).

**The loop's fall-through** is today's `return 0` (`emit_dfa.c:12594`). Under the split it
becomes the walk. Nothing else in the loop text changes, except one thing: `start_max` becomes
a variable, because the tie re-enters the loop at `s*` (§3.2).

### 3.2 The END class: rev-end's walk over Q

The walk is `emit_rev_end`'s seed loop (`emit_dfa.c:11645`): two seeds, the dead-seed skip,
`emit_reverse_block` (`:11233`), the smallest-accepting-start merge and the tie flag. It is
**factored, not copied**. A shared `emit_end_walk(cx, c, pin, &rev)` carries the seed loop
and the merge, and its two callers differ only in their head and their tie arm:

| | `rev-end` (CR_DFA, today) | `split` (CR_ATTEMPT, new) |
|---|---|---|
| machine | `job->rdfa` = reverse of P | `job->rdfa` = reverse of Q |
| pin (seeds) | `pcrec_fact_end_pin(cx)` | `pcrec_fact_pin_split(cx)->epin` |
| head | `emit_search_head` + `PCREC_START0_SEEK` | `attempt_entry`; the SEEK placed after the floor loop |
| start analysis for the reverse form | `unanch_start` (the forward machine exists) | built from the reverse machine alone, `anch_start`'s precedent (`emit_dfa.c:11787`): `kind = DFA_PF_NONE`, view flags from Q's reverse machine |
| tie (ENDSET) | FINISH: `verify-at` (anchored run) or a relocate | inside the locator: `start = start_max = s*; goto` the attempt loop; one attempt of P's full machine, which matches because `s*` is exact |
| SPAN | FINISH `report` | FINISH `report` (`emit_search_success`), unchanged |

Q is built in `compile.c`'s ENG_ATTEMPT arm (`:2573`), after P's attempt DFA, following
`build_anchored_dfa`'s pattern (`:238`) for an OPTIONAL machine:

- **When it is built.** Only when a LOCATE row on this compile's route declares `CAND_MR`.
  This is the path derivation's NEEDS half, the `pcrec_cand_finish_needs` precedent
  (`emit_dfa.c:9897`); a `pcrec_cand_locate_needs` sibling asks the same question of LOCATE.
  It is not built when the split is denied, so a denied build is byte-identical.
- **How.** `pcrec_build_nfa(cx, root, &job->rnfa, true, false)` builds the uncollapsed
  reverse NFA. Then a new `pcrec_nfa_kill_bot(&job->rnfa)` (`src/ir/nfa.c`, beside
  `pcrec_nfa_has_bot`, the one owner of NFA surgery) turns every BOT-family node into an
  `N_CLASS` with an empty set, which is dead by an existing kind. Then
  `pcrec_build_min_dfa(..., false, true, PCREC_MAX_DFA_STATES_TABLE, ...)` and
  `pcrec_scanedge_dfa(..., false)` run, exactly as the ENG_UNANCH arm builds `rdfa`
  (`:2544-2570`).
- **If it overflows.** The state cap's overflow is saved and restored as in
  `build_anchored_dfa`. The machine stays empty, the split does not apply (membership is
  needs ∩ built), and today's route results. "Optional" covers every resource, which is the
  K53 lesson; the emitted-bytes side is §6.6.

### 3.3 The fact the row reads: `pin_split`

There is one fact, `PF_FACT(PIN_SPLIT, "pin_split", 2, PF_CORE, 0, "src/facts/pins.c", "")`.
It is a path-summary walk over the lowered tree, the same tree the E2 seal records. It ports
the analysis `msclass.py` ran over 5,703 patterns. That analysis has C2 libpcre2 0
violations and C4's two plants red. Its value:

- `floor`: {S, G} present on some live path.
- `racing`: {E, LS, LE, F} present on live paths that carry no floor pin. A path's class is E
  if it carries an absolute end pin anywhere, LS if `(?m)^` is at its leading edge, LE if
  `(?m)$` is at its trailing edge, else F.
- `bot_m`: some non-floor live path carries `(?m)^` anywhere.
- `epin`: over E paths, `Z` if every one ends in `\z`, else `EOL` (two seeds).
- `decline`: the walk met something it does not classify: a backreference, a call, a
  variable, `\K`, or an anchor inside a lookaround. All of these decline the fact, like the
  shipped walks (`endwin.c` `A_BREF`/`A_VAR`/`A_CALL`).

The summary at a node is a set of (start-kind × end-kind × consumed) triples. That is a
40-bit lattice, so a repeat's closure is a small fixpoint. `A_CAT` folds its spine
iteratively, per `src/opt/mrl.c`'s rule.

**The machine agreement assertion** follows `emit_attempt`'s own [OPT-ANCHOR-VM] assertion
(the `PCREC_SANCH_BOT && !anchored` failure, `emit_dfa.c` just below `:12215`). It runs one
way by design. After Q's reverse NFA is built, check two things:

- (a) Q has no live `N_BOT_M`;
- (b) Q with `N_EOL`/`N_END` also killed is EMPTY (no live path to `N_ACCEPT`). That is,
  every Q path is end-pinned, and it is checked by reachability.

If the fact admitted but either test fails, the compile stops with `pcrec_ctx_fail`
(internal error). This is the miscompile direction: a free path the walk would never see is
a deleted match. The other direction, the machine proving dead a path the fact counted as
free, only declines, which is conservative. The assertion must be silent over the whole
corpus and every `make test-axes` axis at landing.

### 3.4 Per call and per find-all (Q2 verified)

- **Per call.** Floor: at most one attempt of P. Today's first attempt is the same attempt,
  with the same loads. Walk: at most two seeds, each reading back until Q's reverse machine
  dies or reaches `search_from`. That is the trailing run plus one byte for context, never
  `n` unless the trailing run is `n`. Tie: one forward attempt over the match. SPAN: no
  forward re-read (walk-only, form C).
- **Per find-all, S+E.** The floor attempt runs only in call 1 (`search_from = 0`). Each
  later call runs one walk, and every reported E match ends at `n−1` or `n`. So after the
  first E report `search_from ≥ n−1`, and at most two more calls follow, each floored at
  `n−1` or later. Total: at most 1 attempt + 3 walks + 1 tie attempt.
- **Per find-all, G+E.** The G attempt runs every call. Today's first attempt of each call is
  the same attempt. A walk runs only on a call whose G attempt failed. Its result (or 0) ends
  the find-all within two more calls. Total: today's G attempts + at most 3 walks.

**No cross-call cache and no admission predicate are needed for 4a.** This is §5.1 Q2's
answer, verified per member. The repeated-walk cost of `match_split_requirements.md` §3.1
item 3 needs a second racing class, which 4a does not admit (§1.1).

## 4. Where it sits in the tables (brief item 3)

### 4.1 Rows and edges

| table / node | change | order and reason |
|---|---|---|
| LOCATE (`cand_rows[]` head) | **new row `split`**, `.routes = CR_ATTEMPT`, `deny = PCREC_NO_MATCH_SPLIT \| PCREC_NO_REV_END`, `.hands = CT_START \| CT_VERDICT` (SPAN, NOMATCH; never ENDSET), `.u.locate.whole = true`, `.scan[ATTEMPT] = "split"`, `.recover = CAND_HAND_WINDOW`, `.needs[ATTEMPT] = { CAND_MATT \| CAND_MR, CN(NEXT) \| CN(BOUND) \| CN(RECOVER), CAND_FRONT_DFA }` | after `rev-end`, before `composite`. `rev-end` is CR_DFA only, so the two never compete and their order is answer-free. `composite` stays the total fallback |
| LOCATE predicate | `locate_split_applies`: route is ATTEMPT; `pin_split` admits (`floor ≠ ∅` or dead-only floor, `racing == {E}`, `!bot_m`, `!decline`); the body is exact (`pcrec_cand_lang_exact`, so no count-collapsed hybrid body); `job->rdfa` built | the "built" conjunct is membership = needs ∩ built, as `finish_available` does for `verify-at` |
| BOUND | **two rows** `floor-gstart` (`"search_from"`, applies when G ∈ floor) and `floor-bot` (`"0"`, otherwise), both `.one = CAND_ONE_NONE`, `.routes = CR_ATTEMPT` | after `attempt-gstart`, before `all`. Each reads LOCATE's selection on CR_ATTEMPT: a **new declared read** `cand_nodes[BOUND].reads[LOCATE] = CR_ATTEMPT`, made through `cand_read` ([CAND-PATH-READS]'s mechanism). It must read the SELECTION, not the fact: if Q overflowed, the row must not bound the loop, or matches are deleted. Acyclic: `split`'s predicate reads only the fact and `built` |
| RECOVER | `reverse-pass` gains CR_ATTEMPT with `take[ATTEMPT] = { WINDOW }`; `cand_nodes[RECOVER].asks` gains CR_ATTEMPT | the walk IS a reverse block asked with the speculative WINDOW hand, as `emit_rev_end`'s assertion requires. `pinned`/`end-minus-width`/`landing` stay CR_DFA, take only EXISTS, and so cannot meet a walk. Totality per (route, hand) holds (SL3's self-check) |
| FINISH | **none** | SPAN → `report` (already takes SPAN on CR_ATTEMPT); NOMATCH → `nomatch`; VM hat SPAN → `verify-at` (exact hybrid). Resolving the tie in the locator is what keeps FINISH, and with it every ATTEMPT artifact's `_match` (`RX_DFA_MATCH "search-filter"`), unmoved |
| WINDOW / PRESENCE / FIRST (front) | unchanged rows | WINDOW: `end_window(P)` is −1 on every admitted S+E, because an S arm is not end-pinned. Where every arm is end-pinned (`^a$\|b$`), the clamp is sound for floor paths too (an S match starting at 0 implies `n ≤ W`). PRESENCE: `dominated` through the LOCATE `whole` disjunct, so no whole-window pre-check. A pre-check would cost O(n) per call and undo the split. FIRST: no DFA scan, so `scan-from-startpos` |
| `fit_rungs[]` (`compile.c:938`) | **new rung `drop-split`**, shaped like `drop-anchored` (`.degrading = true`, `.fof = FIT_FOF_IN`, `.on = FIT_L_SIZE`, `.sets` = the split's deny) | among the D135 size rungs, before `drop-anchored`. Their populations are disjoint by engine (Q exists only on ENG_ATTEMPT, A only on ENG_UNANCH), so the order is answer-free |

### 4.2 Emitted shape (for the build lane; text not normative)

```
    size_t start; size_t start_max = <BOUND floor text>;   /* was `const` */
    int split_walked = 0;
    start = <first>;
split_attempt:
    for (; start <= start_max; start++) { ...today's attempt body; success -> report... }
    if (split_walked) return 0;       /* the tie's attempt matched: unreachable by §2 */
    split_walked = 1;
    <K73 SEEK on search_from>         /* utf8 only, as emit_rev_end */
    <emit_end_walk over job->rdfa (Q), pin = pin_split.epin>
    if (revend_start == (size_t)-1) return 0;
    if (revend_tie) { start = start_max = revend_start; goto split_attempt; }
    <emit_search_success(revend_start, revend_end)>
```

A non-admitted artifact never runs this text: `emit_attempt` keeps `const size_t start_max`
and its `return 0` unless the LOCATE row is `split`. So every other artifact is byte-identical
apart from the abi digits. The reverse machine's tables and accessor block use the reverse
form's own names. Their disjointness from the attempt machine's `<p>_byte_class` /
`<p>_targets_N` is a build obligation, proved by `make strict`.

### 4.3 Sibling-of-a-family

- **The position-pin FACT family is dispersed, with four members.** `start_anchor`
  (`startanch.c`, whole-pattern must-S/G), `end_pin` and `end_window` (`endwin.c`,
  whole-pattern must-E), `empty_admits` (`widths.c`, the empty paths' S/E masks), and now
  `pin_split` (per-path has/must). That is ≥ 3, so **propose the unification: `pin_split`'s
  per-kind {has, must} columns become the one table, with the other four as its projections.**
  It is staged, not built in 4a. Projection would MOVE the 22 corpus patterns on which the
  shipped facts are conservative (mssurvey finding 6), so it is its own mover step with its
  own manifest (§9 U3). In 4a the trace build checks agreement in one direction: each
  projection of `pin_split` equals the shipped fact or is strictly stronger.
- **The floor-bound SELECTION family is not dispersed.** `bot`, `attempt-gstart`,
  `vm-anchored`, `vm-gstart`, `floor-bot`, `floor-gstart` and `all` are rows of ONE BOUND
  slot already. Their predicates, however, read three sources: the attempt machine's
  `s1u`/`s1g`, `start_anchor`, and `pin_split`. The fact unification above is their
  unification too.
- **The from-the-end LOCATE family.** `rev-end` and `split` share one walk emitter
  (`emit_end_walk`) and differ in machine and head. `rev-end` is the split's degenerate case
  with floor = ∅. Folding them into one row with route hats is possible later, but it buys
  nothing now: the CR_DFA predicate must stay `end_pin`'s to keep today's 9 conservative
  E-only patterns unmoved (mssurvey C1).
- **The combinator.** 4b adds a second racing sub-locator to the same `split` row: the
  composite of Q (forward+reverse over the floor-free machine). That is a second hat chosen by
  `pin_split.racing`, not a second row. So the family stays one row.

**Remodel overlap:** none. [START-TABLE], [DEC-FALLBACK], L0's path derivation and
[CAND-PATH-READS] are shipped, and this design uses their mechanisms. [PRIOR-COST-UNIFY]
(chunk 2) is not read: 4a reads no prior.

## 5. Cost by counted loads (brief item 4)

### 5.1 The two named cells, on paper, in qwork.py's unit

The unit is subject-byte loads of a whole find-all, as in `qdrv.c` (`../dev/optloop/
matchsplit/qwork.txt`). Today's column is measured; the split's column is derived from §3.4.

| cell | subject | today T (16k) | today attempts | split T | split attempts | derivation |
|---|---|---|---|---|---|---|
| trim `^\s+\|\s+$` (and 8 more S+E shapes, utf8 form included) | `Q·\t^k·Q` | **128,040,002** (growth 15.99) | 16,003 | **2** | 1 | floor at 0 reads `Q`: both arms die (1). Seed `n` reads `Q`: Q's reverse machine dies (1). `s[n−1] ≠ '\n'`, so no second seed. One call |
| trim | `Q·\t^k` | 16,002 | 3 | k + 2 | 1 | floor (1); walk reads k tabs + `Q` → SPAN `(1, n)`; call 2 floored at `n` reads 0 |
| trim | `\t^k` | 16,000 | 2 | k | 1 | floor matches `(0,k)`; call 2 floored at `n` |
| wrapper `^\s*\{\|\}\s*$` | `Q·}^k·Q` | 32,003 | **16,003** | **2** | 1 | floor reads `Q` (1); seed `n` reads `Q`, dead (1) |
| wrapper | `Q·}^k` | 32,001 | 16,002 | 3 | 1 | floor (1); walk reads `}` → accept at `n−1`, then `}` kills it (2); call 2 reads 0 |
| wrapper, captured (hybrid) | same | 32,003 / 32,002 | 16,003 / 16,002 | same as above + one VM `verify-at` over the reported span | 1 | identical window to today's |

K106 goes from 15.99 growth per 4× k to a constant on the internal-run subject, and the
wrapper strip from n+3 attempt entries per call to at most 1. No hand twin was needed: every
split number is a sum of terms §3.4 bounds, and each bound is a property of a walk or attempt
already counted in `qwork.txt`.

### 5.2 Why no constant is needed: dominance on every subject

Take any subject and any call. Today's loop attempts `f` (or `search_from`), then every
position up to the first success `m` or to `n`. The split attempts `f` (the same attempt, the
same loads), then walks. In the match case the walk reads `[m−1, n)` (plus one seed's extra
byte for the tie). Today's successful attempt at `m` reads at least `[m, e)` with
`e ≥ n−1`, and today also paid for every failed attempt in `(f, m)`. In the no-match case
the walk reads until Q dies, at most `n − search_from + 1` loads, while today attempts every
position, at least `n − search_from` loads.

So **split loads ≤ today's loads + 2 per call, on every subject**. That is the derivation of
the admission: it is unconditional for the 4a members, with no prior read and no hand-set
constant (memory `pcrec-suspect-tuning-constants`).

### 5.3 When the split does NOT pay (§3.2)

- **N1** (already the free class's route, rare anchored first bytes): not a 4a member (no
  floor class, or today unanchored: E+LE).
- **N2** (find-all density × long walk): impossible in 4a, which has one racing class (§3.4).
- **N3** (END class whose start is a landmark, `^#|//.*$`): admitted. The walk runs the last
  line backwards, at most one line per call, and dominance (§5.2) still holds against
  today's attempt-every-position. A FREE locator on `//` would be cheaper still, and that is
  4b's sub-locator choice.
- **N4** (short calls): the loads term cannot lose by more than 2 per call. The instruction
  term can: the two-seed loop setup and the tie bookkeeping, which is K103's rev-end entry
  floor (9 ns vs 3.8 ns at bench O-96 (c)1 on Zen 1, not reproduced on the dev box). Leaning:
  admit anyway, with a scratch-tier short-call cell in the landing bar (§7.3). A loss past
  the noise floor becomes a K row, not a predicate (D144's disposition precedent, Q3).
- **N5** (size): Q's reverse machine is the extra bytes. `drop-split` drops it before any
  refusal (§4.1), so the split never refuses a pattern that compiles today. That is the K53
  lesson applied to emitted bytes.

## 6. Interface (brief item 5)

### 6.1 Stamps

- **`<PREFIX>_DFA_SCAN "split"`** is a new value, generated from the LOCATE row (D156 add. 2:
  the locator is named once, from the path). It is mirrored by `rx_info.scan` (`const char *`,
  row 20 of `match_api.md` §6¶1's `rx_info` table), so the layout does not change. 4b and 4c add NO
  value: the class mix is the fact, listed by `--emit-facts`.
- **`<PREFIX>_DFA_START`** becomes `"reverse-pass"` on a split artifact (RECOVER is on its path,
  so it stamps its selection). It is `"attempt-start"` today.
- **`<PREFIX>_DFA_TABLE` / `_DFA_SCAN_EDGE` / `_DFA_UNIFORM_FOLDS`** are folds over the path's
  members, which now include Q's reverse machine. So they become that machine's form (they
  read `"none"` on an attempt body today). These are generated moves, declared in the
  manifest.
- `RX_DFA_MATCH`, `RX_DFA_PREFILTER` and `RX_REQ_*` do not move.

### 6.2 The deny (flag bits: 55 of 64 used, so 9 free; the [IFACE-PUSH] hard trigger is ≤ 4)

Recommended: **one new bit, `-fno-match-split` / `PCREC_NO_MATCH_SPLIT` (bit 55)**. It is the
combinator's deny for 4a, 4b and 4c alike. It goes in the row's `deny` together with
`PCREC_NO_REV_END`, so either bit removes the row. That follows the run-pinned pair's
precedent (`PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER`). It is answer-identical, masked in
`strategy_denials`, and not engine-selecting, because the route stays ENG_ATTEMPT. It leaves
8 free bits. Reuse alone is the alternative (Q1).

### 6.3 Spec hunks (D80, in the build's change)

- `docs/spec/match_api.md` §6.3.4¶2: the `RX_DFA_SCAN` value set (the `<!-- value-set:
  RX_DFA_SCAN -->` marker) gains `"split"`, and so does §6¶1's row-20 enumeration of `rx_info.scan`. §6.3.4¶11:
  the `"reverse-pass"` row adds "every `"split"` artifact".
- `docs/spec/tuning.md`: a new §2.49 `-fno-match-split` (bit 55; answer-identical; it restores
  the attempt route byte for byte; no budget is involved on the DFA route, and the hybrid's VM
  window is identical, so it is neither ONE_WAY nor a D158 marker case). §2.46 `-fno-rev-end`
  gains one sentence: "also removes `split`, whose END walk is this one".
- `docs/spec/facts_listing.md` §4.1: the `pin_split` row (grain pattern, epoch E2, the value
  format `floor=S|G racing=E|LS|LE|F epin=Z|EOL`, and its `why` tokens).
- `docs/spec/registry.md` §6: the `locate` axis lists `split` (orders renumber: rev-end 1,
  split 2, unanchored 3). The deny axis row. The axis count +1.
- `docs/spec/limits.md`: Q's reverse machine is charged to `PCREC_MAX_DFA_STATES_TABLE` as an
  optional machine (an overflow is a selection outcome), and the `drop-split` rung (§2.17's
  ladder).

### 6.4 abi event

The text and stamp values change, so this is an abi event (76 → the manager's number at land,
D76/D94). The readers are found by grep: `PCREC_ARTIFACT_ABI` (`emit_dfa.c:51`), `.abi`
expectations, the (B) FILEPIN in `run_recursion_identity.sh`, `docs/dev/history/
abi_changelog.md`, and spec sentences citing the number. Also the byte-count reader class
(cpset `EMITTED_BYTES`, resource rescue pins), re-derived by measurement, not by the digit
grep (D94 addendum).

### 6.5 Emitted-text impact

On admitted artifacts: the walk, Q's reverse tables and accessor block, a variable
`start_max`, and one `goto`. Nothing else moves, except the abi digits on every artifact
(§4.2).

### 6.6 Kit (memfn)

**No new site and no request.** The walk's loop is `emit_scan_loop` over Q's reverse machine.
Its EDGE/STAY renders are the delegated rows rev-end already reaches, through the same door
(`pcrec_memfn_define`, D146), with facts only (D157). The floor's MLINE site is not reached
by any 4a member. The C17 site manifest is unchanged. Its reach census may count more renders
(re-pinned, §7.2).

## 7. Checks (brief item 6)

### 7.1 Sabotage rows (ids allocated by the manager: check `memfn/docs/requests.md`'s reserved ranges and main's highest)

| row | plant | direction | detector, and why it reaches |
|---|---|---|---|
| MS-1 | `floor-bot`'s text `"0"` → `"-1"` (the floor attempt never runs) | answer | corpus: `^\s+\|\s+$` on `"  a"` loses `(0,2)` |
| MS-2 | the kill omits `N_GSTART` | answer / assertion | G+E witness `\Ga$\|b$` at startpos > 0: the reverse builder meets a `\G` it cannot evaluate, or the agreement assertion fires |
| MS-3 | the walk floor ignores `search_from` | answer | `mc` find-all cells on `^\|$`, `^\|end$` (duplicate or early matches) |
| MS-4 | the admission accepts `racing ⊇ {LE}` | answer | `(?m)^a\|b$` loses line-end matches; the agreement assertion (b) fires on the witness, so the compile refuses |
| MS-5 | the admission accepts `racing ⊇ {F}` | answer | `^a\|b\|c$` loses `b` matches (assertion (b) fires) |
| MS-6 | `epin = EOL` read as `Z` (one seed) | answer | `^x\|a$` on `"a\n"` loses `(0,1)` |
| MS-7 | tie arm replaced by SPAN of seed `n` | answer | `^q\|a$\|a\n$` on `"a\n"`: priority gives `(0,1)`, the plant gives `(0,2)` |
| MS-8 | `locate_split_applies` returns false (the split never selected) | **efficiency, answers unchanged** | the counted-work gate (§7.2 G3) and the `RX_DFA_SCAN "split"` population floor. This is the direction no answer check can see |
| MS-9 | BOUND floor rows read the FACT instead of the LOCATE selection, with Q forced to overflow | answer | lowered-cap variant (`--max-dfa-states` reference build, the `PCREC_ANCHORED_MAX_STATES` precedent): matches deleted on the trim witness |
| MS-10 | the agreement assertion removed and MS-5's plant applied | answer | MS-5's detector. It shows the assertion is the one guard on the fact's soundness |
| MS-11 | `drop-split` row deleted | refusal set | lowered-size variant: a split artifact refuses where today compiles (emit_sweep `stderr` stream, `lowsize`) |

Each row is reach-proved: the witness's `RX_DFA_SCAN` reads `"split"` on the clean build
(`SAB_REACH`), and the population floor is in `SAB_REACH_POP`.

### 7.2 Gates and witnesses

- **G1 corpus** `tests/matchsplit/match_split.rxt` (new directory; own CLAUDE.md), oracle-first
  against libpcre2 10.46. Contents:
  - all 35 pin-only shapes of mssurvey §3 (the 13 non-admitted as controls);
  - the §5.1 witnesses (`^|end$` on `end`, `xend`, `x`, `end\n`; `^|$` on `""`, `a`, `a\n`);
  - K106's three subject shapes at small k;
  - the tie witness (`^q|a$|a\n$`);
  - G+E with startpos cells;
  - nullable E (`^\s*|\s*$`);
  - context-led E (`^x|\bfoo$`);
  - the captured wrapper;
  - an `encoding utf8` block for the outage form, with ill-formed subjects;
  - `mc` find-all cells throughout.
- **G2 the every-startpos and find-all differential**: the split against `-fno-match-split`
  and libpcre2 over generated subjects, on every admitted pattern of the corpus plus the
  idioms list. This is revbuild's window-twin shape (`../dev/lanes/revbuild_report.md`).
  0 differences is the bar, and ASan/UBSan arms are included.
- **G3 the counted-work gate**, `tests/matchsplit/run_linear.sh`. It promotes `qdrv.c` from
  the survey: the 9 S+E trim shapes plus the wrapper strip at k ∈ {1000, 4000}, asserting
  growth ≤ 4.5 per 4× k and T ≤ 4n + 8 (§3.4's bound: 1 attempt + 3 walks + 1 tie, each ≤ n).
  It is the start-landing precedent of a standing hostile cell, as a count instead of a clock.
- **G4 the machine agreement assertion** (§3.3): silent over the corpus and every `make
  test-axes` axis.
- **G5 the libpcre2 differential** (PC-3/registry) is unchanged. G1's cells are oracle-first.

**Expected to move (re-pinned in the build's own change):**

- emit_sweep: movers = exactly the admitted set, by ID. The manifest is the `pin_split` census
  over the corpus. Residue is byte-identical after the abi digits on every stream and variant.
- emit_sweep's `--emit-facts` stream: +1 row on every artifact (`pin_split`), declared.
- The dumps stream: `--list-axes` (locate row, deny axis).
- Start-arm `DIFFER_PINS`: `-fno-rev-end` now differs on split patterns.
- The FILEPIN.
- The registry axis pins.
- `run_form_census.sh`: a floor for `"split"` and a re-derived `"attempt"` floor.
- `run_dfa_stamps.sh`'s `[start]` (`"reverse-pass"` on an ATTEMPT body).
- `run_encoding_checks.sh` DD12a(i): the walk's region on an ATTEMPT body (revtri's
  precedent).
- `run_cand_rows.sh` and cand-oracle: the new row, the BOUND→LOCATE read, RECOVER's ATTEMPT
  cell.
- The trace SET gate's site keys.
- The rxtsource census, startset manifests and size log: the new corpus file.
- C17's reach count.
- The cpset manifest, only if one of its rows is admitted (re-derive).

### 7.3 Landing bar

- **Improve, counted:** K106 trim (G3, linear, was 15.99) and the wrapper strip (attempt
  entries ≤ 1 per call, was n+3).
- **Byte-identical apart from the abi digits:** the five fully-anchored attempt-scan artifacts
  of [OPT-ATTEMPT-SPLIT]'s bar (`ipv4-near-miss`, `uuid-near-miss`, `base10num-near-miss`,
  `winpath-near-miss`, `wild-validator-email-owasp`). Their racing set is empty, so `split`
  does not apply. Also concat-sqli (S+F, 4b) and every E-only `rev-end` artifact.
- **Answers:** G1 and G2 at 0 differences.
- **Short call, scratch tier:** trim and wrapper at n ∈ {0, 1, 2, 8, 64}, interleaved,
  split vs `-fno-match-split`. A loss beyond the noise floor is a K row (§5.3 N4).
- **Bench:** zero reach, accepted (Q5). The `anc-wrap` wishlist family is a landing-bar cell
  when the bench takes it, not a trigger. The bench relay is one line: the closed
  `RX_DFA_SCAN` enum gains `"split"`.

## 8. Build steps (one lane, implement-then-replace inside it)

1. **S0, no movers.** `pin_split` (`src/facts/pins.c`, the facts.def row, the listing row,
   the trace-build projection agreement check against `start_anchor`/`end_pin`). Then
   `pcrec_nfa_kill_bot` with its reachability helpers. Then `emit_end_walk` factored out of
   `emit_rev_end`: rev-end's text must stay byte-identical (emit_sweep 0 movers apart from the
   facts stream).
2. **S1, the abi event.** The ATTEMPT-arm build of Q; the LOCATE row, BOUND rows, RECOVER cell
   and read edge; the `emit_attempt` hook; the deny bit; `drop-split`; the spec hunks; G1-G4;
   the MS rows; every pin in §7.2.

## 9. Questions for Frank, and unlocks

**Q1. The deny: spend a bit now, or reuse `-fno-rev-end`?** The problem: R12 asks for a deny
that restores today's route, and bits are scarce (9 free, trigger at 4). The forces:

- Reusing `-fno-rev-end` costs nothing today, and it is honest in one sense: the split's END
  walk IS rev-end's.
- But it confounds a bisect. Denying it also moves every E-only artifact off rev-end, so a 4a
  regression cannot be isolated without moving rev-end too.
- 4b's sub-locator (the composite of Q) has no deny of its own, so 4b will need a combinator
  bit anyway.

Leaning: spend bit 55 now, one bit for the whole combinator (4a-4c), with the row also
honouring `-fno-rev-end`.

**Q2. K106's two `(?m)` trim shapes (LS+LE).** The problem: they have two racing classes, so
4a's no-waste argument does not cover them. They stay quadratic after 4a. The forces:

- A sound linear design exists. LS is evaluated first, then the LE composite scan over the
  floor-free machine, stopped at the first idle point at or after the LS candidate. The forward
  machine accepts a `CT_UPPER` it does not accept today. That design never costs more per call
  than today, because one DFA pass over all threads started before the candidate is a max
  where today's attempts are a sum.
- But it needs 4b's composite-of-Q machinery plus a new UPPER acceptance on the forward scan.
  That is not 4a's walk.
- Their population is 6 (2 hand-built corpus witnesses, 4 of my idioms).

Leaning: 4b.2, right after S+F lands. K106's entry is re-worded "S+E fixed by 4a; the two
LS+LE shapes by 4b.2". I would like your read on whether the `(?m)` trim is common enough to
pull it into 4a's lane anyway.

**Q3. The short-call fixed term.** The problem: by loads, the split never loses by more than
2 per call. By instructions, the walk's setup may lose a few ns on tiny subjects, which is
K103's floor and was not reproduced on the dev box. The forces: an unconditional admission is
what D77 and SEL-COST §3 ask ("the sign must hold in every regime"), and it holds for loads.
A per-call predicate would need a measured constant, which we would rather not invent.
Leaning: unconditional admission, with the scratch short-call cell in the landing bar and a K
row if it shows (D144).

**Choices I made (answer-free or following rulings):**

- the floor/racing decomposition and the one-racing-class admission;
- the fact on the AST with the one-way machine assertion. The alternative, deriving the
  decision on the NFA, is exact but would move the fact out of `src/facts/` and away from its
  future readers;
- tie resolution inside the locator, so FINISH and `_match` stay unmoved;
- the stamp spelling `"split"`;
- `drop-split`'s place among the size rungs;
- the corpus directory name;
- the G3 bound.

**Unlocks, each with its trigger:**

- **U1 (4b) S+F / G+F, plus S+LE / G+LE.** The same row with a second racing sub-locator: the
  composite (forward+reverse ENG_UNANCH machines) of Q inside the ATTEMPT artifact, after the
  floor. No waste (§1.1). Trigger: MET (concat-sqli ×3.51, I-85 M5.b; 21 S+F on attempt/n by
  mssurvey count (c)).
- **U2 (4b.2) LS+LE / LS+F.** The UPPER-bounded forward scan (Q2). Trigger: 4b landed, plus
  K106's two counted `(?m)` shapes.
- **U3 the position-pin fact unification (§4.3).** `start_anchor` / `end_pin` /
  `end_window` / `empty_admits` become projections of `pin_split`. It is its own mover step
  (22 corpus patterns, mssurvey finding 6). Trigger: 4a landed, plus a reader that gains from
  the stronger facts (the VM's `attempt_max` on the 13 optional-prefix-before-`^` patterns).
- **U4 (4c) E+F / LS+E with an unbounded E arm.** The `stay_len` admission of §5.1. Trigger:
  chunk 2's consumer price plus a bench cell (none today).
- **U5 dead and redundant anchors** (requirements F2; mssurvey findings 3-4). `pin_split`'s
  dead/redundant information moves `x(?:^|y)z`, `(?:^)?ab` and `ab|a\Gb` to the free route
  with no split at all. Trigger: a population outside test witnesses (0 today).
- **U6 `rev-end-width` on Q.** When K103 fix (b) (WINDOW → AT on `end-minus-width`) lands,
  it applies to Q's fixed-width E arms (quote and bracket strip) through the same row family.
  Trigger: that row.
- **U7 the VM-only route.** S+E on VM-only (0 pin-only today), and mssurvey finding 2's
  VM-only E-only quadratic (`(\s*)$`, 10 of 16 measured). That is a capture-erased
  reverse-from-end locator in front of a VM with no DFA body. It is filing material for the
  manager (a K row candidate), not 4a.
- **U8 an ATTEMPT `verify-at` hat** (one attempt at the caller's position) for every ATTEMPT
  artifact's `_match`. Finding F-2. Trigger: a match-regime cell on an unanchored ATTEMPT
  artifact.

## 10. Standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT, and answered by counts.** Every number here is a subject-load
   count from `qwork.txt` (Linux dev box, `-O0` instrumented artifact, whole find-all), or
   derived from §3.4's bounds in that unit. The admission is derived by dominance in loads
   (§5.2), so no regime flips it. The one regime-dependent term, per-call instructions on
   short subjects, is a landing-bar cell (scratch tier), not a decision input.
2. **Independent control: RELEVANT.**
   - G1 and G2 are checked against libpcre2 10.46 and against today's artifact, and neither
     shares a source with the split.
   - G3's bound comes from §3.4's argument, not from the build's output.
   - The agreement assertion G4 shares the pattern with the fact but not the derivation (AST
     walk vs NFA reachability). It guards only the miscompile direction, so it is plumbing,
     labelled so.
   - The population is counted by the `pin_split` census and cross-read against mssurvey's
     independently written `msclass.py` labels (same design, separate code). K35: the
     denominators are printed per population.
   - Every MS row's witness is reach-proved (§7.1).
3. **What moves when data is regenerated: NOT RELEVANT for 4a.** The split reads no prior, no
   findings bundle and no calibration. Regenerating `default.rxt` moves nothing here. The
   design's own data is the corpus file, and its pins are listed in §7.2.

## 11. Findings (for the manager)

- **F-1** The census's E+LE (3) and S+LS/G+LS (3) are already linear today, served by the
  unanchored composite and the MLINE skip respectively (stamps read on this branch). So 4a's
  real population is the 22 floor+E patterns, and K106 is fixed for 9 of its 11 counted
  shapes plus the utf8 outage form.
- **F-2** `<prefix>_match` on an ATTEMPT artifact is `_search(pos)` filtered to `start ==
  pos` (`rx_match` in the emitted `.c`). A failing match-here therefore runs the attempt loop
  to `n`. The split makes that cheap for its own artifacts as a by-product. For every other
  unanchored ATTEMPT artifact it stays O(n): U8.
- **F-3** `end_pin`'s `\G` decline (3) is the WINDOW clamp's obligation, inherited by
  rev-end's R1. A walk that never moves `search_from` would not need it. That is why the
  split's pin comes from `pin_split` over the non-floor paths. Re-examining R1 on CR_DFA is
  out of scope: it would move G+E-on-DFA patterns, of which there are none, since `\G` routes
  to ATTEMPT.
- **F-4** On an attempt body, `RX_DFA_SCAN_EDGE "none"` is described in the spec as "no loop-carried
  table load to shorten". A split artifact carries Q's table-driven reverse machine, so that
  sentence gains an exception in the §6.3 hunk.
