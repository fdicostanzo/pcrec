# docs/dev/reviews/2026-10-05-r4-startset/ — review r4's critic files

The verbatim panel record behind `../2026-10-05-r4-startset.md`, the
consolidation and dispositions. These are the three critics' own reports,
committed by lane `ssrev` as delivered. Do not edit them; corrections go in
the consolidation.

- `ssc-sound.md` — soundness lens (opus). F1 is the BLOCKER (the DFA hat's
  `T = S ∩ E`). F5 (c)-F10 were appended by the manager from the critic's
  first message.
- `ssc-sound-harness/` — that critic's reproduction harness: `dfa_onex.sh`,
  `vm_onex.sh`, the `\x`-decoding drivers `drv2e.c`/`drv3e.c`, and the
  libpcre2 differential `odrv.c` + `run1.sh`. See its README.md. It
  reproduces F1's `narrowed_reseed_diffs=11040`, and lane ssrev re-ran that
  number on its own build.
- `ssc-checks.md` — checks, controls and contract lens (sonnet).
- `ssc-cost.md` — cost and measurement-regime lens (sonnet).
