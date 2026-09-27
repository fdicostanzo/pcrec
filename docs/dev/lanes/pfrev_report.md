# pfrev: [PATFACTS] step-2 design, revision 2 (2026-09-26)

Branch `lane/pfdesign` (worktree `worktrees/pfdesign`). Docs only. No make,
test, mech or battery runs. Five `build/pcrec` single-pattern probes were run
(main's build) for the §11.6 witness measurement.

Input: `docs/dev/reviews/2026-09-26-r1-patfacts-design.md` (on main). Output:
`docs/design/patfacts/design.md` revision 2, plus the patfacts/ and design/
CLAUDE.md entries. Citations were re-verified against main `3204160a`, whose
`src/` is identical to the design's base `e060f2e0` (the diff is empty).

## Findings applied (every FIX row)

A1, A2, A3, A4+C2+C3, A5, A6, C1, C4, C5, A10, F4+F5, A7, A8+F2, A9, A11,
A12, A13, C6, C7, F1, F3. Each is marked `[r1 ID]` in the text.

Where the revision departs from, or adds to, the disposition text:
- **F3.** The review's correction was itself wrong. `emit_dfa.c:~7398-7423`
  is the OPT-5 pinned tail. The DFA start-anchor assertion is at
  `emit_dfa.c:7860-7867`, and that is what the design now cites.
- **A10.** Check 1 is born with B1, as ruled. The witness population
  ("a rate-asking fact left unasked by the ordinary compile") is MEASURED
  EMPTY. `REQ_BYTE` is stamped on every route probed (DFA, `--engine=vm`,
  `-e utf8`), so the pick is always asked, and forcing it early moves
  nothing. The sabotage row therefore ships declared UNREACHED with a REACH
  line. The alternative, holding the check until a witness exists, is left
  to the manager and recorded in §11.6.
- **A11.** A second `setjmp` would break the house rule of exactly one. So
  the guard reuses K60's shape instead: a `Ctx.pf_forcing` flag is read in
  the existing handler, and the handler resumes the force loop.
- **A12.** The 15 raw sites in `emit_vm.c` are `#define <P>_…` MACHINERY
  (`:11390-11628`), not stamps. They are named and excluded by name. There
  are also raw stamp sites at `emit_dfa.c:8966` and `emit_vm.c:226/228`.

## §9 changes

- New 3.0a: the `internal.h` split. The E2 derivation declarations move to
  `src/facts/facts_derive.h`. `pcrec_prefix_ksets` waits for 3.4.
- 3.0: the include/link check is born there, and the relocations happen one
  per commit (startanch, endwin, `rb_walk` into `req.c`).
- 3.1 (B1): the rate readers and `set_ppm` move beside the primitives, and
  `reqbyte.c` is deleted.
- 3.2: `kinds.c`/`widths.c`, the eager E1 seal, and the `fit` copies
  deleted.
- 3.4: `kset.c`, FLAGGED as a possible mover, with a pre-lane grep of every
  pin reader.
- New §9.1: the SEMANTIC/SCAFFOLDING mover classification.

## Final question list

Q1-Q10 are kept. Q1 is updated (eager E1, per-branch E3), Q6 is rewritten
(S2a now vs wait for S2b; recommend S2a now), and Q10 is updated. Q11 is new:
adopt `src/facts/` (recommend yes, with the critic's and the manager's
reasons).

## Could not apply

None.
