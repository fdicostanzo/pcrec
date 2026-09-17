# byteid — the dial+K59 train's byte-identity sweep (2026-09-17)

Branch `lane/byteid`, worktree `worktrees/byteid`. Measurement only —
nothing under `src/`/`tests/` touched. Confirms `k59rung_report.md`'s
structural claim (§4) with a corpus-wide measurement: does the dial+K59
train (merge `cf0962e3`) change any emitted byte for an artifact that
already compiled at the branch point?

Full method, results and reconciliation against `dialimpl_report.md`'s
§5.3a figures: `docs/dev/dialtrain_byteid.md`. Reproduction pieces:
`docs/dev/dialtrain_byteid_evidence/` (own CLAUDE.md).

## Verdict

**Zero movers beyond the known, constant RX_TUNE stamp.** Over 3,938
corpus pattern lines (211 files) compiled by both the branch-point
baseline and the merged tip at default flags:

| bucket | count |
|---|---:|
| identical | 0 (expected — RX_TUNE stamps unconditionally) |
| both refuse (module-gated, unrelated) | 2,438 |
| newly fixed / newly broken | 0 / 0 |
| movers | 1,500 |

**Every one of the 1,500 movers moves by exactly +27 bytes** — verified
both by a delta histogram (one bucket) and by full-diff inspection of
samples spanning the corpus's whole size range (35 KB to 665 KB baseline).
Every diff shows exactly two hunks: the inserted
`#define RX_TUNE "balanced"` line (27 bytes, matching `emit_dfa.c:7186`'s
own comment) and the `.abi: 25 -> 26` digit substitution (same character
count, 0 net bytes). No mover carries any other hunk. This sweep's
population is exclusively `--prefix rx` at the unset (`balanced`) `--tune`
default; it does not reach dialimpl's own `+31`-byte witness (a longer
prefix), which that lane's report already reconciles by hand.

K59's own premul drop-ladder rung requires a prior size-cap-refused
attempt (`src/core/compile.c:1074`); nothing in this corpus reaches that
state at default flags, so this sweep corroborates
`k59rung_report.md`'s structural no-move argument without independently
exercising the rung — consistent with, not a substitute for, that report's
own OWED item.

## What is OWED

Nothing from this lane's own brief. Named, not built, per the memo's "What
this does not cover": a non-default-`--prefix` sweep (would exercise the
`+23..+28`-byte range's other end), a non-`balanced`-`--tune` sweep (a
different but still per-token-constant delta), and independently
exercising K59's own rung over a corpus population that reaches the
size-cap retry path (none exists in `tests/` today at default flags).

## Rulings received

None — no mid-flight questions arose.
