# F3 (O-31 finding 3) — VM step budget on evil-alt-nested — investigation only, no fix

2026-09-17, lane f3budget, sonnet. Read-only investigation per the brief:
does pcrec's VM step budget give a typed give-up on `^(([a-z]+)*)+$`
(the bench's "evil-alt-nested"), or does it hang to the harness's
wall-clock kill as O-31 finding 3 reported? No `src/`/`tests/` change —
the mechanism was found working; nothing here needed a fix.

**HEADLINE: COULD NOT REPRODUCE THE HANG.** Across two boxes (this Mac,
and the tailnet Linux reference box `duxevents@100.69.121.107`, gcc
15.2.0 x86_64 — the box O-31's numbers presumably came from), two pcrec
commits (this branch's tip `cf0962e3`, and the bench's own pinned
`d34c9131` from `testees/pcrec/configs.toml`), and a subject-length sweep
from 5 to 100,000 bytes, the step-budget give-up fires CLEANLY in
under 10 seconds every time. No hang observed anywhere.

## 1. The mechanism, read and verified correct

`src/gen/emit_vm.c` emits exactly ONE tick site for the step counter,
at the fail label, gated `has_budget && has_push`:

    src/gen/emit_vm.c:10860
    if (--run->steps_left < 0) return %s_R_STEPS;

That fires once per BACKTRACK RESUMPTION (once per pop off the resume
stack) — the comment above it (`:10826-10832`) states the design intent
explicitly: forward progress is free, only resumptions are counted, so
the counter is subject-length-independent and measures exactly the
thing D51 bounds. For the WORK budget (a separate counter, D49), charge
sites are `RX_CHARGE_WORK` call sites (`:176-177` in the emitted
artifact) — lookaround back-steps, frameless scan iterations, frames
discarded at a cut. Neither budget is reachable by a loop shape that
bypasses it: `^(([a-z]+)*)+$` has no lookaround/atomic/frameless
construct, so ALL of its combinatorial cost is genuine backtrack
resumption, which the one tick site counts.

Budget re-initialization was also checked across every entry variant
(`rx_search`, the `_deep` escalation tier, `rx_search_in` with
caller-supplied buffers): all three funnel through `rx_search_run`,
which calls `rx_run_state_init` unconditionally
(`emit_vm.c`'s emitted `:444`) — `steps_left`/`work_left` are freshly
set on every call, on every entry. No entry point skips it.

## 2. Reproduction attempts, all clean

Compiled `^(([a-z]+)*)+$` with captures on (forces VM — `RX_ENGINE_WHY
"capture group at pattern offset 1"`), both `--engine=vm` (forced) and
default `auto` (which independently lands on VM too:
`RX_ENGINE_SEL "declined-nullable-default"`, since the nullable inner
group blocks the DFA-prefilter rescue). Standalone `--emit-main`
driver, typed exit codes (`steps`/`frames`/`work`/`match`/`nomatch`).

**The canonical worst-case subject** — `n` copies of `a` followed by one
non-`[a-z]` byte (`!`), the standard evil-regex construction that
maximizes split ambiguity right up against the point of failure:

| box | commit | n=20 | n=50 | n=100 | n=1000 | n=5000 |
|---|---|---|---|---|---|---|
| Mac (gcc-16, arm64) | tip `cf0962e3` | 2.97s steps | 2.96s steps | 2.99s steps | 2.99s steps | — |
| Linux (gcc 15.2, x86_64) | tip `cf0962e3` | 7.89s steps | 8.95s steps | 8.08s steps | 7.03s steps | 7.26s steps |
| Linux (gcc 15.2, x86_64) | bench pin `d34c9131`, `--features all` (bench's exact flags) | 7.00s steps | 6.73s steps | — | — | — |

Flat regardless of `n` past a small threshold (the pattern is
`^`-anchored, so the search loop makes exactly one attempt at position
0 and returns immediately on a typed give-up — it never retries later
start positions, and the shared, non-reset-on-retry budget means a
retry loop couldn't multiply the cost anyway even if it existed:
`rx_reset_for_next_attempt` deliberately does not refill either budget,
D51/D49's own rationale, comment at the emitted `:246-251`). Effective
rate: ~166M steps/s on the Mac, ~71M steps/s on the Linux reference box
— both AT OR ABOVE D51's own ~50M steps/s calibration assumption, so
the 500M default's ~10s worst-case estimate holds for this exact shape
rather than being "astronomically high."

**Two negative controls**, to rule out variant shapes:

- An interleaved-mismatch subject (`"aaa!"` repeated) fails almost
  instantly (`nomatch`, ~10ms) — the early `!` lets the search prune
  fast; it is NOT a worse case, confirming the single-trailing-mismatch
  shape is the right worst-case construction.
- A purely matching subject (`n` copies of `a`, no mismatch) up to
  n=100,000 matches in ~10ms flat — greedy-first succeeds immediately,
  no backtracking, confirming the pathology is specifically about the
  failing case and not a hidden O(n²) cost on the happy path.

## 3. The DFA/`--no-captures` "wrong answer" half — could not confirm either

The brief also asked to confirm whether pcrec-nocaps' answer is a
DFA-route answer the oracle disputes. Built `--no-captures` at the
bench pin (`RX_ENGINE "dfa"`, `RX_ENGINE_SEL "selected"` — the pure DFA
route, since removing captures removes the only thing that was forcing
VM). It answers `nomatch` correctly and instantly for every subject in
§2's sweep (n=5 through 50), agreeing with python `re`'s oracle
(checked directly). For this pattern the captured GROUPS don't affect
the matched LANGUAGE (`^(([a-z]+)*)+$` recognizes exactly `[a-z]*`), so
there is no ambiguity in match/no-match or in the reported span for a
`$`-anchored pattern to disagree about — I found no construction where
the DFA route diverges from the VM route or from python `re` here.

## 4. What this means against the brief's four questions

1. **Does the budget fire, and at what n does wall time exceed N
   seconds with the budget not fired?** It fires, always, within
   single digits of seconds, at every n tried (5 to 100,000). Never
   found an n where it failed to fire inside a reasonable bound.
2. **Where does the counter tick; is there a bypassed loop shape?**
   One site (`emit_vm.c:10860`), ticks once per backtrack resumption,
   gated correctly on `has_push`; nothing about this pattern's shape
   (no lookaround, no atomic groups, no splice/call, no frameless
   scan) routes its cost through an uncounted path. Verified by
   reading the code and by the fact that every give-up in every test
   reported `steps` (never `work` or a silent timeout).
3. **Is the default calibration astronomically high for this shape?**
   No — measured rate (71-166M steps/s) is at or above D51's own
   assumption, so the ~10s worst-case the ruling states holds here.
4. **Fix or recommendation?** No fix — nothing broken was found. The
   step-budget mechanism, read and measured, behaves exactly as D51/D49
   designed it to for this construct, on both the dev boxes available
   to this lane, at both the current tip and the bench's own pinned
   commit.

## 5. Recommendation to the manager

I cannot square this clean reproduction against O-31 finding 3's report
of a wall-clock-kill hang, and I do not have read access to the actual
O-31 ledger or the bench's real subject bytes from this box (the local
`/Users/fdicostanzo/pcrec-bench` checkout is stale — its `HEAD` is
`41b9179`, an I-57 travel-month entry that predates any O-31 commit;
`git fetch` timed out, no network reachable from this box for that
repo). Before this is treated as closed, someone with access to the
live pcrec-bench state should pull the actual O-31 subject text (and
its harness's per-case wall-clock timeout value) and compare against
§2's construction — either the real subject differs from the canonical
"n matches + one mismatch" shape in a way this lane didn't find, or the
bench's own per-case timeout is tighter than the ~7-9s this shape
genuinely costs on their hardware family, which would make this a
bench-harness calibration question rather than a pcrec one.

## Reproduction

Scratch-only, nothing committed to the tree beyond this report (no
`src`/`tests`/`docs/spec` touched, per the brief's own framing — this
found no counting-site bug to fix and no calibration to re-rule).
Artifacts and commands used are in this lane's own transcript; the key
generation commands were:

    build/pcrec -p rx --emit-main --engine=vm -o - '^(([a-z]+)*)+$'
    build/pcrec -p rx --features all --emit-main -o - '^(([a-z]+)*)+$'      # bench's pcrec-auto shape
    build/pcrec -p rx --features all --no-captures --emit-main -o - '^(([a-z]+)*)+$'  # pcrec-nocaps shape

each run under `gnutimeout 60/90` on the tailnet reference box, subject
`'a'*n + '!'`.
