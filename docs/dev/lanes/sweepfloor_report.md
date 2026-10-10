# sweepfloor report: start-sweep DIFFER_PINS re-pin after [OPT-REVEND] L2

Lane `sweepfloor`, branch `lane/sweepfloor`, off main a2f66450. Cause of
the five red floor lines in `docs/design/memfn/probes/r13/slot18_sweep_triage.md`
Q2, which found them identical on main and R-13's tree.

## Method
A driver (not committed; scratch under the worktree's `build/sf/`) imported
`scripts/emit_sweep.py`'s own `enumerate_corpus` / `compile_stream_c` /
`start_keys_moved` and, over the same 4527 distinct corpus patterns, compiled
BASE and BASE+FLAG with three binaries: a15fb77b (pre-REVEND), 7388f1c0
(REVEND L1+L2 merge, abi 73) and main a2f66450. It counted differ/stamp per
arm and, for every pattern that left a count between a15fb77b and 7388f1c0,
checked whether the plain compile carries `rev-end` (`RX_DFA_SCAN "rev-end"`).
a15fb77b -> 7388f1c0 is the only step where any count moved; 7388f1c0 ->
main moved none.

## Per-pin table (c-default stream)
| pin | old | a15fb77b | 7388f1c0 = main | new | patterns that left | cause |
|---|---|---|---|---|---|---|
| byte -fno-run-prefilter differ+stamp | 132/132 | 138/138 | 127/127 | 127/127 | 11 | all end-pinned, rev-end at 7388f1c0 (0 at a15fb77b) |
| byte -fno-end-window differ+stamp | 288/288 | 362/362 | 272/272 | 272/272 | 90 | same |
| byte -fno-req-run stamp (differ 553 unchanged) | 301 | 311 | 296 | 296 | 15 (stamp only) | same |
| utf8 -fno-req-handoff differ+stamp | 280/280 | 290/290 | 275/275 | 275/275 | 15 | same |
| utf8 -fno-req-run stamp (differ 608 unchanged) | 299 | 309 | 294 | 294 | 15 (stamp only) | same |

The leavers are nested: the 95 distinct patterns that left any of the above
(plus byte -fno-req-handoff's 4, 167 -> 163, still at its pin 163, untouched)
are all `$` / `\z` / `\Z`-terminated (`$`, `a$`, `a{0,4}\z`, `\bfoo$`,
`(foo|foobar)$`, `.{1,3}?(?:\B|)$`, ...). For all 95: `rev-end` absent at
a15fb77b, present at 7388f1c0. Every drop is explained by rev-end; nothing
was left unexplained.

Observation: at a15fb77b the counts were ABOVE the 2026-10-06 pins (138 > 132,
362 > 288, 311 > 301, 290 > 280, 309 > 299), so the pins were slack floors
before REVEND, not tight; re-pinned to the measured value anyway (the house
shape, "floors sit AT the measured value").

## Manifest
`-fno-end-window` c-default manifest `$` no longer differs (rev-end, END_WINDOW
"none" either way). Replaced by `^$`, the shortest remaining c-default mover
at main (then `()$`, `^.$`, `^a$`). The c-vm cell keeps `$` (VM route
unchanged, 288/288, no flag raised).

## Not touched
R-13's memfn floors; the other 27 arms; utf8 -fno-end-window ASSERT_ZERO.

## Validation
See the handback; `make test-spec-history` after this report.
