# memfn wake — kit session hand-off (rewritten 2026-10-11 ~13:30)

This is the kit session's orientation file. Run it as `/pcrec-memfn-manager`;
its §1 is the wake order. It is rewritten at every pause and holds the
current state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager, session `pcrecdev3`. The
  pcrec manager is "main" (`pcrecdev1`; it may be a fresh session, so run
  ListAgents and send to the current pcrec manager). Main files requests
  in `requests.md`. You answer in `responses.md` and are its only writer.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use
  `gnutimeout` (bare `timeout` is uutils). There is no git identity, so
  commit with `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- Work one branch per unit, each in its own worktree. Never merge to main,
  never push, never `cd` (use `git -C` and absolute paths).
- **Scratch:** `worktrees/memfn-slot/` (one dir per slot, plus kept survey
  and triage reports).

## 2. Read, in this order

`memfn/CLAUDE.md`; `requests.md` / `responses.md` (newest); the tail of
`journal.md`; `memfn/docs/ideas.md` (the 2026-10-11 entries); BOILERPLATE
before briefing.

## 3. Box, slot and cron rules

- One heavy suite at a time across BOTH sessions. ASK main for the GO
  before each slot, and ping main at the end with the verdict.
- Light work (make -j4, strict, single sections pinned `taskset -c 12-15`)
  needs no slot.
- A red stage gets a triage lane BEFORE you read the log.
- **Running lanes miss mid-run messages.** Twice this session a scope or
  design addition sent to a running lane was ignored (r14b, spansurv).
  Put changes in a FRESH lane and verify additions in the deliverable.
- Heartbeat cron `17,47 * * * *`. Recreate it at wake, delete it at close.
- Restore `docs/dev/artifact_size_log.tsv` after make test / test-axes.

## 4. Current state (2026-10-11 ~13:30)

- **On main (merged):** R-12 (VMLAZY abi 72), R-13 (vrun-w32/w16 + vrun-kb),
  RQ-4's harness and reading, R-14 (padded word + trimmed verify, denies
  vrun-pad / vrun-trim), and the ideas branches up to lane/memfn-ideas2.
- **R-15: DONE, awaiting main's merge.** lane/memfn-r15 @ 310fad70.
  - The row `precheck_assign_byte` + the scalar deny; zero movers on main.
  - slot22 is green after triage (G2 quick floors re-pinned ee365ab1; the
    two test-axes axes were load-window losses, and a quiet re-run is
    green).
  - Main merges R-15 FIRST, then merges main into lane/rlhbuild, runs L1's
    chain, and L1's merge is the abi event (it flips the three stale items,
    r15b_report §7).
  - Told main: the variants sweep's 26 tag floors are stale on main.
- **R-16 (filed, NOT started):** KB at w32 only (Frank's Q-R14-1 ruling,
  D147 addendum 16), sabotage S815-S819. It runs after R-15. Its
  re-timing needs a heavy slot on main's GO. Kit-local, SIMD-off identical.
- **lane/memfn-ideas3 @ f4513e3a+ (NOT merged):** ideas.md entries
  2026-10-11, the r14p_report correction (slot21's control was not
  like-for-like on 20 cells) and a [responses] notice asking main to file
  the span thread UNSCHEDULED under [SPAN-ISEL]. Ask main to merge it with
  R-15.
- **Frank's rulings this session** (recorded): KB stays (Q-RQ4-1, D147
  add. 15); KB at w32 only (Q-R14-1, add. 16); the loss survey is ONE pass,
  accepted (memory pcrec-one-pass-loss-chasing); the span ideas are
  UNSCHEDULED, info-gathering only, no kit build time (memory
  pcrec-memfn-span-unscheduled).
- **Unscheduled / filed:** the span thread (surveys done; a designed spike,
  opportunistic only); the KB rare-KA hypothesis; pc16 nested length checks;
  pcrec workload facts (density, length class, byte profile, from
  pcrec-analyze bundles); memcasecmp for caseless backrefs; the cached
  class truth vectors for the VM; Q-G2M6-1..9; [MEMFN-CI-ASCII]; a D27 G2
  pass for the SIMD contract and the R-15 landmark sites.

**Worktrees:** r15 (R-15, keep until merged), ideas3 (keep until merged),
r14/r14b/r14p/s21prep/rq4/rq4h/r15b/vmlazy-era ones (merged; main prunes
via wtprune), memfn-slot (scratch), g2u + g2u-cell (keep).

## 5. Next actions on wake

1. Recreate the heartbeat cron, run ListAgents, and read requests.md for
   new items.
2. Check whether main merged R-15 and lane/memfn-ideas3. If not, send one
   line naming both tips.
3. Start R-16: a build lane (kit-local distance rule: KB only in the w32
   arm), light checks, then ask main for the heavy slot (identity +
   re-timing).
