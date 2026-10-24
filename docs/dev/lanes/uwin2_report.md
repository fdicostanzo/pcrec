# uwin2: window_site.md rev 2 (DESIGN ONLY)

Lane uwin2 (kit manager's lane), 2026-10-21, branch `lane/memfn-uwin2` (rev 1 + `lane/memfn-b4scope`).
No build go: no `memfn/src`, `src/`, `cli/`, `lib/` or `tests/` edit; no make; no timing.

Delivered: `docs/design/memfn/window_site.md` rev 2 (551 lines, rev 1's length), the
`docs/design/memfn/CLAUDE.md` row. Every finding of `docs/dev/reviews/2026-10-21-r2-memfn-window-site.md`
and the kit manager's five rulings are placed by id in the note's Appendix B.

Decisions a resuming agent needs:
- S1 and S2 land as ONE landing (no adapter; §5.1).
- Adoption between the baseline scan and the offset-k skip needs a new minimal fact, ALTERNATIVES (§1.1): the
  two are different sound conjunctions (`\b\.[0-9]{4}Z`: `.` is outside k0), so a pick cannot be avoided
  otherwise. Flagged for the next panel to try to fold away.
- The reseed's "unconditional" half of M5′ (§R4.3.5) moves bytes, so it is NOT in S2 (§3.5).
- Tie rule: one stated rule (lower offset); run-pinned sites use "higher" today; S1 owes the count of
  model ties inside runs (§2.1).

OWED: job 581 (`581-kit-r27-follow`) was PENDING when written; D-hors's threshold is OWED to its table
(`worktrees/r27b/build/r27b/job/r27b_table.md`). All "zero movers" claims are OWED to S2's emit_sweep.
