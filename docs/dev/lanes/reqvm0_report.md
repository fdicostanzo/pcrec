# reqvm0 — [REQRUN-VM] step 0: why VM routes skip the required-run handoff and re-entry, and the VM-side soundness rule

Lane reqvm0 (opus), 2026-10-27, read-only facts plus one report. Main at
33ee30a85. No build, no make, no timing. Probes are single-pattern compiles
with the main-tree `build/pcrec` and a 20-line driver (scratch
`/tmp/claude-1001/reqvm0/drv.c`, `probe.sh`). The driver includes the
artifact and calls `rx_search(s, n, startpos, caps)` once per startpos.

## Summary

- **The exclusion was a SCOPE call, not a soundness call, and Frank ruled
  it as "file, don't build" with a trigger.** litscan_k82h.md §1.4 (a)
  says skipping VM-only attempts is "sound by Claim 1". It names two
  reasons it was left out: "no measured customer: 0 movers in the
  forced-VM census", and K49's encoding-advance discipline would be needed.
  Frank's ruling (2026-10-05) was: "**Q7 FILE, DON'T BUILD:** the
  no-DFA-scan VM handoff is [OPT-VMSEED]'s territory (cross-noted there);
  its trigger is a VM-route cell that measurably pays the rescan."
  - subtri's case 7 (url-tld-fix, x3.89) is that trigger cell.
  - Frank's 2026-10-27 filing of [REQRUN-VM] ("Yes", folding [OPT-VMSEED])
    is his own later ruling.
  - So the STOP RULE does not fire. He ruled a deferral with a trigger, not
    a permanent exclusion. **The manager should confirm this reading.**
- The hybrid re-entry exclusion (rlhbuild, 2026-10-11) is also scope. The
  hybrid gets "the ENTRY generalization only ... their retries are RETRY's;
  no re-entry inside the prefilter function". That is slot ownership. No
  failing case was named.
- **The two halves are different problems.**
  - **VM hybrid (case 2).** The re-entry inside the hybrid's prefilter
    function is the DFA argument word for word, applied to the prefilter's
    own language. It is answer-identical AND give-up-preserving, because
    the prefilter's answers (and so the VM's attempts) do not change. The
    declines it needs (count-collapsed, `\G` + prefilter-window) are
    already in FIRST's predicate, which the NEXT row reads.
  - **VM-only (case 7).** Answer-identical by Claim 1 and Claim 2′. It is
    **NOT give-up-preserving**: the skipped attempts would have spent step,
    work and frame budget. Probe P1 shows this. Today
    `(a?){25}a{25}xyz` gives up from startpos 0 (`-2` at a 1M step budget,
    `-4` at the default budget), and answers `(86,114)` from `c − K = 61`.
  - The movement is one way only (give-up → the unbounded answer), the
    same class as the start-set VM half (tuning.md §2.42¶3). But
    match_api.md §3.1¶14, tuning.md §2.41¶9 and Frank's Q10 ("no
    give-up→match allowance anywhere") say the handoff never moves a
    give-up. **The VM-only half needs a Frank ruling. It is not blocked on
    soundness.**
- **Facts.** `req_landmark_maxoff` is already derived on VM-only artifacts
  (`--emit-facts` shows it, used `no`; case 7 has K = 4). The whole run
  (`req_whole_run`) is published. Its own maxoff (`RbRun.whole_maxoff`) is
  internal and not a listed fact.
- **Recommendation.** One row, two admitted consumers, written as a
  first-match table (see Recommendation):
  - the hybrid prefilter re-entry, buildable now;
  - VM-only entry + retry re-entry, gated on the give-up ruling, and
    landmarked on the WHOLE run (K65's pick-independence).

## History of the exclusion

1. **The VM-only exclusion: conjunct (a), [K82] (B), commit 6e519889a**
   (k82hbuild, abi 60 → 61). The code comment at
   `src/gen/emit_dfa.c` `req_handoff_applies` reads: "(a) A SCAN TO MOVE:
   `pcrec_artifact_has_dfa_scan` ... A VM with no DFA scan is
   [OPT-VMSEED]'s." The design, docs/design/litscan_k82h.md §1.4 (a),
   says:
   > The VM with NO DFA scan is excluded. Its pre-check is K65/K66's linear
   > no-match proof, and skipping its attempts (sound by Claim 1) has no
   > measured customer: 0 movers in the forced-VM census. A VM
   > `attempt_position` advance would also need K49's encoding-advance
   > discipline. It is filed, not built (§Q Q7).

   §3's census row is "Forced-VM configs: 0 movers. That route has no scan
   to move, and K65/K66 own it." Q7 recommended "file it, don't build it
   ... 0 forced-VM movers with a measured loss". **Frank's ruling, the same
   note's "Rulings (Frank, 2026-10-05)"**: "**Q7 FILE, DON'T BUILD:** the
   no-DFA-scan VM handoff is [OPT-VMSEED]'s territory (cross-noted there);
   its trigger is a VM-route cell that measurably pays the rescan."
   - Verdict: SCOPE (population and D77). Soundness was asserted, not
     feared ("sound by Claim 1").
   - The one engineering obligation it named is K49: `attempt_position`
     must stay a character start, which the existing
     `PCREC_START0_ROUNDUP` provides.
   - The emitted guard in `src/gen/emit_vm.c` ("internal error: the [K82]
     handoff reached a VM route with no prefilter to start") only makes
     the scope decline loud.
2. **The VM-only route keeps ON_MISS**
   (`emit_dfa.c` `req_site_define`:
   `s->handoff = handoff ? MF_H_ASSIGN : MF_H_ON_MISS`).
   - This is a consequence, not its own decision. `handoff` is
     `req_use(cx) == REQ_USE_HANDOFF`, and FIRST's row declines VM-only
     by (a), so the site keeps no position.
   - The K65/K66 text that VM-only pre-checks carry (whole set, whole run)
     is a no-match proof by design (tuning.md §2.29¶3-4).
3. **The VM hybrid is excluded from re-entry: [REQ-HANDOFF-L1], commit
   91a31ba5f** (rlhbuild, abi 74 → 75).
   - `pf_handoff_applies` returns false where
     `cand_finish_of(cx) == CAND_ROUTE_VM`. Its comment: "the forward
     search machine of the caller-facing body (never the VM hybrid's
     inlined prefilter, whose retries are RETRY's)".
   - rlhbuild_report.md §1.3 repeats it ("`cand_finish_of != VM`: never
     inside a VM hybrid's prefilter, whose retries are RETRY's"), and its
     §7 item 7 says: "VM hybrids get the ENTRY generalization only
     (grp-atomic-alt, K 2): their retries are RETRY's; no re-entry inside
     the prefilter function."
   - Verdict: SCOPE (slot ownership). No failing case is named in the
     report, the code or tuning.md §2.41¶8a ("never inside a VM hybrid's
     prefilter").
   - `req_reentered` likewise answers false off `CAND_ROUTE_DFA`, so the
     hybrid declares no `landmark_position`.
4. **Lineage.** Frank's 2026-09-22 question on [OPT-REQBYTE] ("use the
   position of the REQBYTE to set the search start") led to [OPT-REQPOS]
   tier 2. Tier 2 was declined on population (reqpos_2b.md). Its VM half
   was re-opened 2026-09-25 as [OPT-VMSEED] (Frank: "vm is important when
   caps, etc are on so it matters"). It was folded into [REQRUN-VM] on
   2026-10-27 (Frank "Yes").

Frank's give-up ruling, which bears on the VM-only half, is from the same
2026-10-05 rulings: "**Q10 DECLINE** the handoff on count-collapsed
prefilters (no give-up→match allowance anywhere); population 0 on corpus
and bench."

## The DFA soundness argument

docs/design/litscan_k82h.md §1.2 sets it up.

- **Invariant F.** Every successful attempt at `p` holds the landmark at
  some `q ∈ [p, p + K]`. K is the landmark's maximum byte offset on the
  lowered tree. The run never lies inside a lookaround body: req.c does
  not descend into `A_LOOK`, so `q ≥ p`.
- **Claim 1.** Take `c` = the least landmark occurrence `≥ f`. No attempt
  in `[f, c − K)` succeeds, because a success at `p` has `q ≥ c`, so
  `p ≥ c − K`.
- **Claim 2 / 2′.** The answer at `f` equals the answer at any `lo ≤ p*`,
  because attempts read `f` only as a lower bound. `\G` reads `f` by name,
  so every consumer keeps `search_from` as the `\G` reference and moves
  only its scan start.
- **Claim 3.** The body is correct at any legal startpos. Under utf8,
  `lo` is rounded up to a character start.

**The re-entry** (`emit_req_reentry_use`) applies the same argument again
inside the scan, at one point. The comment says: "The miss is sound where
the block runs, at the start state with no accept pending: nothing begun
earlier is pending, and every later match holds the landmark at or after
`posvar`." Spelled out:

- At `forward_state == S0 && last_accept_position == -1`, the unanchored
  machine's future is exactly a fresh search from `scan_position`. No
  thread that began earlier is alive (S0 is the start state), and no
  earlier accept is waiting to be reported.
- So the remaining answer is `answer(scan_position)`. Claims 1-3 apply
  with `f := scan_position`:
  - if `landmark_position < scan_position`, re-find from `scan_position`;
    a miss answers NOMATCH;
  - otherwise jump to `round_up(c − K)` where that is ahead, and re-seed
    a context-seeded machine from the byte before.
- The kept `landmark_position` is still the least occurrence `≥
  scan_position` while it is `≥ scan_position`, because every earlier
  re-find was from a smaller position.

It is give-up-preserving on the DFA because the DFA meters no steps.

## The VM soundness rule

**The form being judged**, for a backtracking VM attempt loop (VM-only,
`<PREFIX>_VM_PREFILTER "none"`):

- **Entry.** `c` = the least landmark occurrence `≥ f`; a miss is
  NOMATCH, which is today's pre-check. Set
  `attempt_position = (c − f > K) ? round_up(c − K) : f`.
- **Retry.** After a failed attempt at `p`, take the encoding's advance
  `p′ = adv(p)` (K49). If `landmark_position < p′`, re-find from `p′`; a
  miss returns 0. Then `p′ = max(p′, round_up(landmark − K))`. The VM
  start-set seek ([START-SET], `first-class`) follows as today.

**Claim (answer identity).** The answer equals today's when all of these
hold:

- **(V1) F holds for the program's own language, in bytes.** K is finite.
  It is computed on the lowered tree, where backreferences, variables,
  linked calls and (future) consumer callouts are ANY/unbounded, so a
  landmark to their right gets no finite K. `A_LOOK` bodies are not
  descended, so a run inside a lookbehind is never the landmark.
- **(V2) `\G` keeps reading `search_from`.** The VM already passes
  `search_from` (not `attempt_position`) to `<prefix>_match_anchored`
  where `v->ngst > 0` (M6.2 wave D).
- **(V3) Every position the loop starts at is a legal startpos.** Under a
  multibyte encoding the moved position is rounded up to a character
  start (`PCREC_START0_ROUNDUP`), and the K73 offset-0 seek still runs on
  `attempt_position`.
- **(V4) The skipped attempts would all have failed.** This is Claim 1
  applied at each re-find point: with `L` = the least landmark occurrence
  `≥ p′`, no attempt in `[p′, L − K)` succeeds.
- **(V5) Each attempt starts from a reset run state.** No attempt's
  answer depends on an earlier failed attempt
  (`<prefix>_reset_for_next_attempt` rewinds the trail and `resume_depth`;
  `call_top` is reset). So the first successful attempt and its captures
  are the same attempt as today's. The [START-SET] VM seek already relies
  on this (tuning.md §2.42¶2).

**Proof sketch.** The VM answer is the least `p ≥ f` whose attempt
succeeds, together with that attempt's priority-order path. The proof
needs three things:

- every skipped `p` fails, by V4 at each segment;
- the attempts actually run are the same `p` values, in the same order,
  each from a reset state (V5), with the same `\G` reference (V2), at
  legal starts (V3);
- `search_from` keeps its other readers: the end-window clamp, the root
  minimum-width check, and `[OPT-ANCHOR-VM]`'s bound.

**Budgets, the one observable difference.** Budgets are per CALL.
`run_state_init` sets `steps_left` once, and the per-start reset
"rewinds the trail and zeroes `resume_depth` WITHOUT resetting the
budgets, deliberately (a bump-along must not buy itself a fresh
allowance)" (`src/gen/emit_vm.c`).

- A skipped attempt spends nothing, so the budget left at every attempt
  that runs is at least today's.
- Hence: today answers → the new form gives the same answer; today gives
  up → the new form gives up OR returns the unbounded answer. Never the
  reverse.
- This is give-up-NON-preserving in one direction: match_api.md §3.1¶13
  and ¶15's class, and tuning.md §2.42¶3's and match_api.md §6.3.5¶8's
  precedent. It is not give-up-preserving.

**The VM hybrid (prefilter re-entry).** The hybrid's `<prefix>_prefilter`
is a DFA unanchored body: forward scan, S0 `memchr`, reverse pass (case 2's
artifact). Put the re-entry inside that function's forward scan at S0 with
nothing accepted. Then the DFA argument applies to the PREFILTER's
language `L′` with `f := its third argument`, and the function's answer
(window start and end) is unchanged. Three things follow:

- the VM's `attempt_position` and `window_end` are unchanged at the entry
  call and at every retry call;
- no VM attempt moves, so the change is **give-up-preserving**;
- the clamped `window_end` (`prefilter-window`) reads the same answer.

The condition is that K bounds `L′`: the exact language or a zero-width
erasure (litscan_k82h.md §4.2 item 1, "the run is still necessary in it,
at the same offsets").

- That excludes the count-collapsed prefilter (Q10).
- `\G` + the prefilter-window ceiling is FIRST's (d′).
- `pf_handoff_applies` already requires `req_use_read == HANDOFF`, which
  carries both declines.
- Adaptive re-seed step mode never calls the prefilter, so its attempts
  are unchanged too.

## Cases that break it

Each risky case with its verdict and probe. "today" is the current
compiler's answer. Search from `lo` stands in for what a run-driven loop
would compute (hand simulation; no implementation).

| case | verdict on VM-only | probe (pattern, subject, flags) | today: search(0) | search(lo) | what the form must preserve |
|---|---|---|---|---|---|
| step/work/frame budget | **one-way give-up movement (the ruling)** | P1 `(a?){25}a{25}xyz`, `a`×25 `b` `q`×60 `a`×25 `xyz`, `--engine=vm --step-budget=1000000`; K = 50, c = 111, lo = 61 | `rc=-2` (STEPS); `rc=-4` at the default budget | `(86,114)` | the unbounded answer `(86,114)`; give-up → answer only |
| `\G` before the run | sound iff `\G` keeps `search_from` (V2) | P4 `(?:\Gab\|x)(cat)dog`, `zzabcatdog`, `--engine=vm`; K = 2, c = 4, lo = 2 | NOMATCH | `(2,10)` (`\G` anchored at 2) | NOMATCH: move `attempt_position` only, never the `\G` argument (S469's VM twin) |
| `\G` matching at f | sound | P3 `(?:\Gab\|x)abc`, `xxabcab`; K = 2 | `(1,5)` | lo = 0 = f | unchanged |
| lookbehind before the run | sound: success reads the whole subject, never `f` (Claim 2); the look body is never the landmark | P2 `(?<=q.)ab`, `qzab`; K = 0 | `(2,4)` | `(2,4)` from 2 | lookbehind reads below `lo` |
| run inside a lookbehind | no landmark there: `(?<=abc)xyz` has run `xyz`, K = 0 | facts only | — | — | — |
| UTF-8, `c − K` mid-character | sound with round-up (V3); without it the startpos is illegal | P5 `.cd` `-e utf8`, `€€cd`; K = 4, c = 6, c − K = 2 | `(3,8)` | from 2: `rc=-7` (startpos error); from 3: `(3,8)` | round up to 3; never attempt at a continuation byte (K49/K73) |
| caseless under utf8 | sound: K is BYTES on the lowered tree (H2) | P6 `(?i)stra` `-e utf8`, `xſtra`; K = 2 (ſ is 2 bytes) | `(1,6)` | from 1: `(1,6)` | K = 2 not 0; under `-e byte`, K = 0 and NOMATCH (correct) |
| branches at different offsets | sound: K is the max over branches (a masked cube run) | P7 `(?:xx\|y)abc`, `zxxabc`; run `[xy]abc`@1, K = 1 | `(1,6)` | `(1,6)` from 1 | — |
| backreference before the run | declined: K unbounded (`A_BREF` is ANY) | `(a)\1xyz` → `unbounded` | — | — | no move |
| variable-width prefix | declined: K unbounded | `a+xyz` → `unbounded`; `a{1,3}xyz` → 3 | — | — | no move / bounded |
| linked call before the run | declined: `A_CALL` is an unbounded gap | `(?1)xyz(a)` → `unbounded` | — | — | no move |
| `\K` | sound: K is from the ATTEMPT start (H3) | `ab\Kcd` → K = 2 | — | — | the reported start may exceed `lo` |
| `(?\|...)` branch reset | out of population: "not implemented yet" (refused) | — | — | — | n/a today; captures do not touch F |
| `^` / `\G`-anchored (one attempt) | sound, no gain | `[OPT-ANCHOR-VM]` `attempt_max` already ends after one attempt; the pre-check admission's `one-attempt` row | — | — | decline (nothing to skip) |
| callouts | answer-identical for pure callees | `x(?C1)abc` → K = 1 (a callout is a CHECK, text ZERO, kindrow.def) | — | — | see below |
| partial matching / NOTEMPTY | n/a | match_api.md §5.2¶6: no partial or streaming state; a pattern with a landmark is not nullable, so find-all never takes the empty-match advance | — | — | — |
| verbs | n/a | `(*COMMIT)`/`(*SKIP)`/`(*PRUNE)`: "outside pcrec's scope and no module will implement it" | — | — | k82h's (g) stays structural |
| case 7 itself | sound | `url-tld-fix` on a small subject, K = 4, c = 19 | `(15,44)` | `(15,44)` from 15 | the exact start (whole run at offset 0) |

**Callouts.** match_api.md §11.6¶1 makes "fire count and order
unspecified". A pure callee's defined answer is the backtracking-order
answer over attempts "start positions in order". litscan_k82h.md (g),
as retired by [INLINE-C] 1b, adds: "an attempt below the scan start is
one the erased SUPERSET language cannot match ... and fires on attempts
the engine skips are unspecified (the fire contract)". So the skip is
allowed. Two effects remain:

- "Each fire is one step" (§11.6¶3), which is the budget row above;
- a callee error code (`result < -1`) from a skipped attempt no longer
  ends the search, the same as under the [START-SET] seek.

A future CONSUMER callout must carry text ANY in its kind row, or F
breaks.

**K65's pick lesson (design point, not a soundness break).** With the
run WINDOW as the landmark, `c_w − K_w ≤ c_W − whole_maxoff`, where `W` is
the whole run. Which skipped attempts (and so which give-ups) move then
depends on the byte-rate prior's window pick, and `--analysis` bundles
move it. That is K65's NOMATCH ↔ give-up-by-pick shape. With the WHOLE
run as the landmark, the bound is a fact of the pattern, and it is always
at least as tight. VM-only artifacts already ship the whole-run compare
(`<prefix>_reqrun_whole`, K66), and subtri's 7a prototype used it. Case
7: whole run `https://www.` at offset 0, so K = 0 and the candidate is
exact.

**Census note (D77, first measurement for the design).** litscan_k82h.md
§3 found all 35 corpus blocks carrying a step budget or a `gu` case "on
the VM with no DFA scan". So the VM-only half lands exactly on the
give-up corpus. How many have a finite K and a give-up that moves is
unmeasured. It is a sweep over 50 compiles, so it goes through the queue.
The repros named so far stay put:

- K64's `^([a-zA-Z0-9._%+-]+)+@` is anchored and declined;
- K65's `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` has an unbounded K.

## Recommendation

**Widen as ONE row ([REQRUN-VM]): one fact (the landmark + K), one site
(the PRE site, ASSIGN), one deny (`-fno-req-handoff`).** The admissions,
declared first-match (D122 addendum 4: rows on `cand_rows[]`, never a
VM-local table):

| # | route / consumer | condition | verdict | give-up | slot |
|---|---|---|---|---|---|
| 1 | any | `-fno-req-handoff` | none (today's discard gate) | — | — |
| 2 | any | no pre-check emitted, or the landmark's K unbounded | none | — | FIRST (exists) |
| 3 | any | one-attempt route (`^`/`\G`-anchored, VM `attempt_max`) | none: nothing to skip | — | FIRST (new conjunct on VM; DFA already structural) |
| 4 | VM hybrid | count-collapsed prefilter (Q10), or `\G` + `prefilter-window` (d′) | entry `scan-from-startpos`, no re-entry | preserving | FIRST (exists) |
| 5 | VM hybrid | otherwise, and the K admission (`req_landmark_admits`) passes against the prefilter's start row | entry handoff (exists) + **re-entry inside `<prefix>_prefilter`'s forward scan** | **preserving** (prefilter answers unchanged) | NEXT `handoff`: drop `cand_finish_of == VM`; `req_reentered` widened |
| 6 | VM-only (`VM_PREFILTER "none"`) | the give-up ruling is NOT given | none (today) | — | — |
| 7 | VM-only | ruling given; the landmark is the WHOLE run (pick-independent), K = its whole maxoff, finite | entry `attempt_position = max(f, round_up(c − K))` + **retry re-entry** after K49's advance, before the start-set seek; `\G` keeps `search_from` | **one-way** (give-up → unbounded answer) | FIRST on the VM route + a RETRY/NEXT row on the VM route (the engine-neutral table) |
| 8 | DFA routes | as today | unchanged | preserving | — |

- **Rows 4-5 (case 2)** are buildable on today's contracts. Every decline
  is inherited from FIRST, and nothing observable moves except speed and
  the `<PREFIX>_DFA_PREFILTER`/handoff stamps. Engineering items for the
  design note:
  - the PRE site is defined after `<prefix>_prefilter` today (case 2:
    `rx_reqrun` at line 470, the prefilter at 207), so the define moves
    up or the landmark is passed in. Either is an emitted-layout abi
    event;
  - a `landmark_position` local inside the prefilter function;
  - whether the entry's hit is passed to the prefilter (one search per
    call instead of two).
- **Row 7 (case 7) needs Frank's ruling first.** Question for relay, in
  plain words: on a VM artifact with no DFA in front, skipping attempts
  the required run proves cannot match makes some calls that give up
  today return the right answer instead. It never goes the other way.
  The start-set skip already has this property (§2.42¶3). Q10 said the
  handoff should never move a give-up. Do you accept the one-way
  movement for the VM-only handoff? If yes, these change: match_api.md
  §3.1¶14, tuning.md §2.41¶4/¶9 and the axes GIVEUP1 manifest for
  `-fno-req-handoff`, measured. **Leaning: yes, same class as the
  start-set skip.**
- **Facts.**
  - Rows 4-5 read `pcrec_fact_req_landmark_maxoff` as today.
  - Row 7 needs the whole run's maxoff published as a fact. It is
    computed in req.c (`run->whole_maxoff`) but not listed;
    `req_landmark_maxoff` = window maxoff.
- **Consumers that change.**
  - `req_handoff_applies` (a): a VM-only path member.
  - `req_site_define`: ASSIGN on VM-only; `ret_pred` = the whole-run part.
  - `emit_vm.c`'s search entry: `attempt_position = first`, and drop the
    "no prefilter" `ctx_fail`.
  - The retry tail.
  - `pcrec_emit_vm_start_seek`'s premise comment.
  - `pf_handoff_applies` and `req_reentered`.
  - `<PREFIX>_REQ_HANDOFF` values on VM-only artifacts.
  - The mech rows S469/S476 analogues on the VM.
- **One mechanism.** subtri named startset.md Q-R5's VM `first-memchr`
  (7c) as a sibling: "one of the two, not both". Row 7 subsumes it on
  the landmark population.

No blocker on soundness. The VM-only half is blocked on the give-up ruling.

## STATE AT HANDOFF

- STATE: complete (read-only; report only, NO BUILD GO honoured).
- Branch `lane/reqvm0`. The report is committed. A history index entry is
  added to `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Rulings file `reqvm0_rulings.md`: last entry applied: none (the file
  holds "(none yet)").
- OWED: none.
- Probe scratch (not committed): `/tmp/claude-1001/reqvm0/` (`drv.c`,
  `probe.sh`, `p1`-`p9` artifacts and subjects).
- Questions for the manager:
  - confirm the STOP RULE reading (Q7 was a deferral with a trigger,
    superseded by Frank's 2026-10-27 filing);
  - relay the row 7 give-up question to Frank.
