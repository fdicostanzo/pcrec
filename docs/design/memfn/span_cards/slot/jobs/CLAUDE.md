# docs/design/memfn/span_cards/slot/jobs/ — the S2d WINDOW's boxqueue jobs (span_cards.md §3.3, §9 S2d)

COMMITTED canonical copies (review r9 W1); never queued from here. Main copies this directory to a scratch job
dir, writes `window.env` there (from `window.env.example`: RUN_ID, FROZEN, TREE, optional HOLD) when Frank
clears the window, and queues the copies. Every `--dry-run` refuses a copy that differs from this directory.

## Files

- `common.sh` — sourced by every job: window.env (FROZEN resolved to its full sha, CODE_COMMIT), `check_inputs`,
  `ready_prep`, `ready_after` (an upstream ENDED, not green; 77 once the prep or the screen ended non-green; r9 W2), `timing_dry` (inputs only; `expect groups=N` from `plan.py groups`),
  `timing_job`.
- `480-kit-s2d-prep` — every job's slot dry run (frozen plan, links, gates, manifests); no clock.
- `480-kit-s2d-screen` — the placement screen (`run.py screen`, quiet-gated, idle-ok) after the prep; its
  non-green end (over the half gate) makes every timing job answer 77 (`ready_after`): the window is HELD.
- `481-kit-s2d-J1` .. `486-kit-s2d-J5` — the timing jobs (quiet-gated, idle-ok), each after the screen GREEN: J1; J2 after J1; J2p after J2
  (then J1 green -> `record.py ready-j2p`, J1 non-green -> 77); J3 after J2 and J2p; J4 after J3; J5 after J4.
- `489-kit-s2d-J9` — `record.py finalize` once the prep, the screen and every timing job ended.
- `window.env.example` — the window's variables.

Maintenance: update this file when files are added/removed or change roles.
