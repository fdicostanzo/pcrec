# F3 round 2 (O-31 finding 3) — one SEARCH call under captures on b"a"*17+b"!"

2026-09-17, lane f3search, sonnet. Round 2 of the O-31 finding-3
investigation, against the bench's refutation of round 1
(`f3budget_report.md`): their failing subject is exactly
`b"a"*17 + b"!"` (18 bytes), all three captures arms hit a 60-second
per-subject alarm 5/5 under the short-subject-search regime, and they
report "the first iteration never returning" — six times round 1's
measured worst case.

**VERDICT: (a), measured and read — one budget, one typed give-up,
bounded call.** A single `<prefix>_search` call on the exact subject
costs ONE step budget and returns `PCREC_ERR_STEPS` in 2.5-2.8 s on
this Mac (round 1 measured the identical single-call shape at 7-9 s on
the bench's own box family). The budget is initialized once per entry
call, shared across every per-startpos attempt inside the call, and a
STEPS give-up propagates out immediately. **The bench's >60 s is their
own harness's measurement regime**: the `search_short` regime's
calibration PROBE batches every subject at a fixed 200 iterations
(`pcrec-bench/pcrecbench/harness.py:77`, `PROBE_ITERS`), each iteration
is a fresh search call that legally re-pays the full per-call budget,
and their 60 s alarm fires around iteration 7-8 of 200 — with nothing
printed per iteration, so from outside it reads as "the first iteration
never returned." That inference is refuted directly: driving the bench
driver's own loop shape at their own pin, the first iteration RETURNS
at 2.73 s with the typed give-up (`first_iter_wall=2.728s`,
`first_giveup=-2`), and total batch wall is linear in iters
(10 iterations = 27.4 s).

## 1. The code, read with file:line

All facts verified on BOTH the tip (`67053297`) and the bench's pin
`a770139e` — the emitted artifacts for `^(([a-z]+)*)+$` at the two
commits are byte-identical apart from the known `RX_TUNE`/abi-digit
stamp delta (`dialtrain_byteid.md`'s +27 bytes; diffed directly).
Emitted-artifact line numbers below are from the tip's artifact
(default flags, `-p rx`; `RX_ENGINE "vm"`, `RX_ENGINE_SEL
"declined-nullable-default"`); emitter sites in `src/gen/emit_vm.c`
beside them.

- **One budget init per entry call.** `rx_search_run` (emitted :432,
  emitter `src/gen/emit_vm.c:11227`) calls `rx_run_state_init` exactly
  once, before the startpos loop; that sets `steps_left =
  RX_STEP_BUDGET` (500,000,000, D51) and `work_left` (emitted :237-238,
  emitter :10570).
- **STEPS propagates out immediately** — the first check inside the
  startpos loop (emitted :448, emitter :11233): `if (result ==
  RX_R_STEPS) return PCREC_ERR_STEPS;`. A give-up never advances the
  startpos loop.
- **The per-attempt reset does not refill.** `rx_reset_for_next_attempt`
  (emitted :247-251, emitter :10607) unwinds the trail and zeroes
  `resume_depth`; its comment states the D51/D49 rationale ("retrying at
  the next starting position cannot buy itself a fresh allowance").
- **The only budget re-arm is the deep tier, and it is FRAMES-gated.**
  `rx_search` (emitted :477-497, emitter :8510) escalates to
  `rx_search_deep` on `PCREC_ERR_FRAMES` AND NOTHING ELSE (emitted
  :494); the deep re-run does refill budgets (its comment says so,
  by design), so the worst case per call is fast-tier-work-until-FRAMES
  plus one full deep budget — bounded at ~one budget plus epsilon, and
  measured below as exactly that shape (`RX_TEST_TIER_HOOK` counted one
  escalation per call at n≥15).
- **The `^` anchor is compiled into the program, and non-zero attempts
  are free.** `rx_L0` (emitted :266): `if (scan_position == 0) goto
  rx_L2; goto rx_fail;` — and at `rx_fail` the `resume_depth == 0`
  check (emitted :397) precedes the step decrement (:398), so an
  attempt that pushed no frames costs ZERO steps. The search form does
  iterate all 19 start positions, but 18 of them are O(1). (Confirmed:
  n≤14's full exhaustive nomatch returns in 32-94 ms.)
- **`rx_search_in` with caller buffers** (emitted :504-511) funnels to
  the same `rx_search_run`: same single init, same propagation. No
  deep tier (the caller's buffers are the storage) — measured below,
  same cost, zero escalations.
- **The §3.1 find-all loop ends on a give-up.** `docs/spec/match_api.md`
  §3.1's loop breaks on `r != 1`, so a correct protocol driver makes
  exactly ONE call on this subject. Verified with the loop transcribed
  from `tests/encseam/findall_driver.c`.

So (b) — per-attempt re-arm — is false at both commits, and (c)'s
anchor variant is false too. Within one call the budget is (a).

## 2. The measurements

Driver: `docs/dev/lanes/f3search_driver.c` (the encseam §3.1 shape
plus a single-call mode, the anchored match form, `search_in`, and the
bench driver's own batch loop transcribed from
`pcrec-bench/testees/pcrec/driver.c:699-733`). Compiled `gcc-16 -O2
-DRX_TEST_TIER_HOOK` against the artifact emitted at each commit (the
pin built via `git archive a770139e`, its own `build/pcrec`, its own
`--features all` flags). Every run under `scripts/watchdog -s 120 -m
2000000 -c 110`. Subject is always `b"a"*n + b"!"`.

**One `rx_search(s, n+1, 0, caps)` call, tip build, n sweep:**

| n | wall | outcome | deep escalations |
|---|---|---|---|
| 13 | 0.032 s | 0 (nomatch) | 0 |
| 14 | 0.094 s | 0 (nomatch) | 0 |
| 15 | 0.558 s | 0 (nomatch) | 1 |
| 16 | 1.119 s | 0 (nomatch) | 1 |
| **17** | **2.725 s** | **PCREC_ERR_STEPS** | 1 |
| 18 | 2.723 s | PCREC_ERR_STEPS | 1 |
| 19 | 2.733 s | PCREC_ERR_STEPS | 1 |
| 20 | 2.751 s | PCREC_ERR_STEPS | 1 |

**n=17 is the boundary case exactly**: the first n whose exhaustive
nomatch search exceeds 500M resumptions (the cost roughly ×2.4 per
+1 a; n=16 completes under budget at 1.12 s). The bench's subject sits
precisely on the first budget-firing input. Rate ≈ 185M steps/s here,
consistent with round 1's 166M/s Mac figure (and its 71M/s on the
bench's box family → ~7 s/call there, matching round 1's 7-9 s).

**All modes at n=17:**

| mode | build | wall | outcome |
|---|---|---|---|
| search1 (one call) | tip | 2.776 s | STEPS give-up, 1 escalation |
| search1 (one call) | pin a770139e | 2.756 s | STEPS give-up, 1 escalation |
| findall (§3.1 loop, spec shape) | tip | 2.748 s | loop ends on the give-up, 0 matches |
| match (`rx_match_caps`, round-1 contrast) | tip | 2.728 s | STEPS give-up |
| search_in (64K-frame caller buffers — the vm-in-caps arm) | pin | 2.489 s | STEPS give-up, 0 escalations |
| batch ×10 (the bench driver's own loop) | tip | first iter 2.728 s; total 27.418 s | first give-up typed; 10 escalations |

Match form and search form cost the same (one attempt at pos 0 is the
whole cost either way). The three bench arms (auto-caps, vm-caps,
vm-in-caps) are indistinguishable at this level — same VM program, same
one budget; `search_in` is marginally cheaper (no fast-tier
false start).

## 3. Where the bench's 60 s comes from

Read from their harness (read-only, the local checkout; the driver and
calibration files predate O-31 and carry the relevant machinery):

- `testees/pcrec/driver.c:699` — per subject, an OUTER `iters` batch
  loop; `:715-733` — the find-all body; a give-up breaks the INNER loop
  only (`:721`), and the batch continues. Each next iteration's
  `do_search` is a fresh call → a fresh per-call budget, by contract.
- `pcrecbench/harness.py:77` — `PROBE_ITERS = {"search_short": 200}`:
  the calibration probe runs every subject at a fixed 200 iterations
  before `calibrate()` (`:240-265`) picks the real `iters` off the
  MEDIAN subject.
- Arithmetic: at their measured ~71M steps/s, one call ≈ 7 s; the 60 s
  per-subject alarm fires during iteration ~8 of the 200-iteration
  probe batch, 5/5 deterministically. The driver prints nothing per
  iteration, so the alarm's `timedout` row is indistinguishable from
  "first iteration hung" unless a single-iteration trial is run — which
  is exactly the trial that would have shown the 7 s typed give-up.
- The auto-nocaps control fits the same frame: the DFA route answers
  nomatch in ~12 ns/call, the probe is instant, `calibrate()` hands it
  5.6M iterations, 69 ms — their own number.

## 4. Disposition

**No pcrec change recommended; nothing here is a counting-site bug or
an open contract question.**

- The budget's contract IS per-call, deliberately: D51 ruling 3 sets
  500M with "worst-case honest-refusal delay on a pathological input
  ~10 s at the measured ~50M steps/s" accepted with eyes open ("DD-2 is
  robustness, not a latency guarantee"). The measured 2.5-2.8 s (Mac) /
  ~7-9 s (their box) sits inside that stated envelope.
- pcre2's shape is the same: `match_limit` bounds ONE `pcre2_match()`
  call; a harness batching N calls on a limit-exhausting input pays
  N × the limit there too. (pcre2's DEFAULT limit is 10M vs pcrec's
  500M, so its give-up arrives ~50× sooner — that is a calibration
  difference D51 already records, with the 20M conservative option
  named as the road not taken. The bench episode adds no new evidence
  against D51: what their harness batched was a typed refusal that
  arrived within D51's stated envelope.)
- **The actionable fix is bench-side**, to relay via the manager's
  outbox: (i) in `driver.c`, break the OUTER iters loop when an
  iteration's first search returns a give-up — iterating a
  deterministic typed refusal 200× measures nothing and turns an ~7 s
  answer into a 1,400 s batch; and/or (ii) wall-cap the calibration
  probe per subject rather than fixing its iteration count. Their own
  `giveup` variable already detects the case at `count == 0`; it just
  doesn't leave the batch.
- Their "first iteration never returning" sentence should be corrected
  in the O-31 record: measured false at their own pin with their own
  loop shape.

## Rulings received

None; none requested.

## Reproduction

    build/pcrec -p rx -o evil.c '^(([a-z]+)*)+$'          # tip; VM via captures
    build/pcrec -p rx --features all -o evil.c '^(([a-z]+)*)+$'   # pin, bench flags
    gcc-16 -O2 -DRX_TEST_TIER_HOOK -o f3 docs/dev/lanes/f3search_driver.c evil.c
    scripts/watchdog -s 120 -m 2000000 -c 110 -S f3 -- ./f3 17 search1
    ./f3 17 findall | match | search_in | batch 10

The pin build comes from `git archive a770139e` into scratch; nothing
in either repo's tree was modified for it. Validation: no `src/`/
`tests/` change to validate — measurement plus one committed driver
file; the driver compiles `-O2` clean under gcc-16 (its own build is
its check).
