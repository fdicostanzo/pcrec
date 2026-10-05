# memfn wake — TEMPLATE (no kit session has run yet)

This is the orientation file for the dedicated, long-lived kit session
(Q36, D147). It is born as a template. **At every session end or pause,
the kit session rewrites it from scratch** in the shape below: the
current state, never a history (the history is `journal.md`).

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions session: the kit's owner, working
  `memfn/` inside the pcrec repository. The pcrec manager ("main")
  directs you; your durable channel to it is `responses.md`, its channel
  to you is `requests.md` (read it; never edit it).
- **You work in your OWN worktree** under `worktrees/` (e.g.
  `worktrees/memfn`, branch `lane/memfn-<topic>`), cut from a main that
  contains the request you are serving. FIRST command in it:
  `git rev-parse --show-toplevel`. You NEVER merge to main; the manager
  reviews and merges. You never `cd` into another worktree or the main
  tree; use `git -C` and absolute paths.
- Scope mandate: write only inside your worktree and the session
  scratchpad (`docs/dev/lanes/BOILERPLATE.md`'s top line). Read-only
  everywhere else in the repo; never write to pcrec-bench.

## 2. Read, in this order

1. `memfn/CLAUDE.md` — the layers (D147), the boundary, the
   same-commit abi rule, symbols/licence.
2. `docs/dev/decisions.md` D146, D147 (and D144 for acceptance, D145
   for licences, D76/D94 for the abi ritual, D80 for the spec).
3. `memfn/docs/requests.md` (open items without a `done:` in
   `responses.md`), then the tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/integration.md` — §R4.3 first (the rulings), then §L
   (the layers), then the sections
   your request names (§14 the contract, §15 the site shapes, §22 the
   build order).
5. `docs/dev/lanes/BOILERPLATE.md` — box facts, process rules,
   DO-THEN-FINISH, the handback rule. They bind you as any lane.
6. Before C: `docs/dev/coding_guide.md`. Before a check:
   `docs/dev/learnings.md` §3.

## 3. Box and suite rules (summary; BOILERPLATE wins on conflict)

- One heavy suite at a time on a box; coordinate through the manager.
- Mac: directional timings only. Verdicts are Linux (ubuntubudu over the
  tailnet), `taskset`-pinned, calibrated loops ≥ ~50 ms, absolute deltas
  against a floor (D144 addendum 1). Heavy Linux runs go through the
  manager's executor channel, never your own ssh.
- Long runs: background, logged, detached (`nohup … & disown`, plus
  `caffeinate` on the Mac); a run longer than ~4 min is the last thing
  you launch before handing back.
- Every acceptance reading reports SIMD-off AND SIMD-on (D147).
- A change that moves a pcrec byte carries pcrec's abi bump, re-pins
  (readers by grep), stamp values, spec hunk and G1 alpha in the SAME
  commit.

## 4. Current state (rewrite each session)

- Kit code: none yet. Next code step: R4a (integration.md §22).
- Open requests: R-1 (R4b measurement).
- Open defects: none.
- Last journal entry: 2026-10-05 (subtree set up).
- In flight / owed runs (log paths, completion lines): none.

## 5. Next actions (rewrite each session)

- (template) Serve the oldest open request the manager has briefed you
  on; ack it in `responses.md` first.
