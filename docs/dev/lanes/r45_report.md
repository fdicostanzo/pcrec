# Lane r45 report — the kit's reply draft to R-45 (window spans of up to 4095 positions)

Lane r45 (opus, design only), branch `lane/memfn-r45` from main `ea83fbc01`, 2026-11-16.
The deliverable is `docs/design/memfn/r45_reply.md`; its §8 is a block ready for
`responses.md`, for the kit manager to post. No code was changed, nothing was timed, no
box job ran, and `make` was not run.

## Summary

- **Yes, the kit can carry spans of 4095.** It does so through ONE general span carrier on
  every window span, with no REPORT-only bound.
- **The carrier.** The per-position arrays leave the seam structs:
  - `mf_wspan`'s sets and table offers point at host-owned arrays;
  - `mf_class.proven[41][32]` becomes a counted proof, `proof_n` plus rows, in the
    caller's arena (`mf_arena`);
  - `mf_wreply`'s plan arrays are counted, also in the arena.
- **Every holder shrinks:**

  | struct | today | proposed |
  |---|---|---|
  | `mf_class` | 2,932 B | 1,640 B |
  | `mf_result` | 3,000 B | 1,712 B |
  | `mf_wspan` | 1,164 B | 32 B |
  | `mf_wreply` | 532 B | 136 B |

- **Bounds.** `MF_WSPAN_POS` 4095, `MF_WREACH` 4096, and the ceiling `MF_MAX_FWD` 4096.
  The proof range is a per-reply count under that ceiling.
- **Decoupling.** `MF_MAX_TERM` and `MF_WMAX_SPAN` stay 32 and are decoupled from span
  length. `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD` retire.
- **abi events.** One `MF_SITE_ABI` event (29 -> 30) carrying `MF_CLASS_V` 10 -> 11.
- **Forms.** The three forms' cards are specified as C1-C5. Their numbers are OWED to a kit
  timing window.
- **Interim head.** `h` = 32, labelled `UNMEASURED DEFAULT`, keeps the joint landing
  zero-mover at pcrec's default width.
- **Dense near miss** reads as O(n·k) against the engine's O(n). This is the one regime
  where a long cover can lose by orders of magnitude.

## The five answers

1. **ASK (1): yes, on every window span.**
   - `MF_WSPAN_POS` = 4095 (CHOSEN: pcrec's widest statement).
   - `MF_WREACH` = `MF_WSPAN_POS + 1` = 4096 (DERIVED).
   - `MF_MAX_FWD` = `MF_WREACH` (the build-time ceiling, for pcrec's `_Static_assert`).
   - The reply's proof range is a per-reply count, `mf_class.proof_n`, over the site's
     stated extent. Nothing is proven outside it by construction, and for a cover it always
     reaches offset `k`.
   - pcrec's 32/64 for non-cover sites become pcrec construction asserts, not kit bounds.
2. **ASK (2): no.** `MF_MAX_TERM` 32 and `MF_WMAX_SPAN` 32 (each under its own
   derivation) are decoupled from `MF_WSPAN_POS` 4095. S526 is re-aimed at `MF_WSPAN_POS`
   4095 -> 4094 (BUILD-REFUSED via pcrec's seam assert). `PM_NPROOF` and `G2W_NPROOF` go.
3. **ASK (3): three forms.** I (all inline, today's text), L (loops over maximal runs of
   one set) and H(h) (inline head, then L).
   - Cards C1 (k = 24, 32), C2 (36 uuid, 40 `lit-l40`, 49, 60), C3 (500, 1000), C4
     (compile and size, 32..4095) and C5 (the engine-route reference).
   - Subjects: hit-dense, dense near-miss, miss-heavy, random. Both layers.
   - `h` is the cards' output: the death-depth knee vs the code-size knee.
   - One PAIR option row, working name `span-loop`, for pcrec's dial.
4. **ASK (4): O(n·k) vs O(n).**
   - At k = 32 that is about 15.5 re-tests per byte, which fits the measured x6.65.
   - At 4095 it is about x850 (UNMEASURED extrapolation).
   - The statement already gives a bad-character skip past the failing offset, and an L/H
     loop yields that offset for free. This is logged as a reading, with OPEN Q3.
5. **ASK (5): arrays leave the seam structs.**
   - Statement arrays are host-owned. Proof and plan rows are kit-written into the
     caller's arena.
   - Arena proof rows: 1,312 B at k = 32 (as today), 16,288 B at 500, 131,328 B at 4095.
   - pcrec's 8 stack classes: 23,456 -> 13,120 B.
   - The kit's working arrays are sized per site extent. Raising the constants instead
     would make each window decision about 644 KB, and `find_groups`' stack array
     16,416 B.
   - abi: `MF_SITE_ABI` 30 with `MF_CLASS_V` 11 inside it; `MF_VOCAB` unchanged.

## Evidence

- **Size probe.** `/var/tmp/pcrec-pcrec/scratch/memfn/r45/sz.c` includes
  `memfn/src/window.c` and prints `sizeof`. It was compiled with `gcc -std=gnu11 -O0 -w -I
  memfn/include -Wl,--unresolved-symbols=ignore-all` and printed:
  - `mf_class 2932 proven 1312`, `mf_result 3000`;
  - `mf_wspan 1164 mf_walt 16 mf_wreply 532`;
  - `mf_site 2968 mf_pred 2808 mf_term 80`;
  - `wf_pos 76 wf_alt 6064 wf_dec 12568 wf_plan 3424 wf_legacy 5016`.
  These match R-45's figures (2,932 / 1,312 / 3,000).
- **Proposed layouts.** The same directory's `prop.c` printed `prop : class 1640 result
  1712 wspan 32 wreply 136`, and the per-k rows (proof rows `k + 9`, x 32 B).
- **Line cites** (main `ea83fbc01`):
  - the bounds: `memfn.h:277, 302, 309, 314-315, 650-667`;
  - `mf_wspan`: `:669-685`; `mf_run_reply`: `:1280-1285`; `proven[]`: `:1340`;
  - `MF_WPLAN_MAX`: `:1684`; `mf_wreply`: `:1695-1719`; the arena: `:1005-1012`;
  - window.c's working arrays: `window.c:155, 183, 219-220, 1323-1354`;
  - `wf_legacy`: `:1440-1441`; `legacy_ok`: `:1463`;
  - the C-run cap: `:1772-1786`; `find_groups`' stack array: `:1775`;
  - the D-hors `uint8_t` shift: `:1850`; the inline `&&` chain: `:3287-3313`;
  - the plan's proof: `:3853`; `term_prove`'s clip: `compose.c:406`;
  - pcrec's bound check: `src/gen/memfn_sites.c:590-600`; `cc_fits`:
    `src/gen/known.c:336`;
  - pcrec's `mf_wreply` locals: `src/gen/emit_dfa.c:4670, 7757, 16318`.
- **The kit's 2026-11-15 ideas entries** are read from `lane/memfn-k1108` (they are not on
  main): `git show lane/memfn-k1108:memfn/docs/ideas.md`, line 797 on.

## Open questions

Each carries a recommendation in r45_reply.md §7.
- **Q1 (main):** should pcrec keep 32/64 for non-cover sites as its own asserts?
  Recommend: yes, on `PCREC_MAX_REQ_RUN_SCAN` and `PCREC_PREFIX_K_MAX`, with no site kind
  in `window_bounds_check`.
- **Q2 (Frank):** should the interim `h` be 32 (UNMEASURED DEFAULT, zero movers at the
  default width)? Recommend: yes.
- **Q3 (Frank):** should a skip past the failing offset ride with the first build that
  admits k > 32? Recommend: yes, inside the L/H loop, on the same cards.
- **Q4 (main):** should `MF_MAX_SPAN_POS` retire now? Recommend: yes, if pcrec's A1 is on
  the combined branch first; otherwise keep it one release.
- **Q5 (main):** a kit timing window for C1-C3 and C5 beside cover_cap.md §11.4's night?
  Recommend: yes. C4 is a boxqueue job.
- **Q6 (main):** is 131 KB of arena per class answer of a 4095 cover acceptable until the
  stage-2 cost record? Recommend: yes. The run-length proof is designed and has its
  trigger.

## STATE AT HANDOFF

STATE: delivered (design only). Rulings file `docs/dev/lanes/r45_rulings.md`: empty; last
entry applied: none. The card numbers are not this lane's to owe: they need a kit timing
window, and the reply names them as OPEN.
OWED: none
