# r17bp4 — R17-b′ revision 3 and the panel record (2026-10-16)

Lane r17bp4 (opus, design only), branch `lane/memfn-r17bp4`, worktree
`worktrees/r17bp4`. Parent: the kit manager. Nothing under `src/`, `memfn/src/`, `tests/`
or `lib/` changed; no timing. Checks run: a markdown table-shape check over the documents
written, and `make test-spec-history` (light): 143/2 at the end, both reds
`docs/dev/lanes/fddocs_report.md:37` (`tuning §2.49`, `limits §8.4¶2b`), present on this
branch's base 39f13e397 and not this lane's; this lane's own two dangling `§2.49`
citations were found by it and removed (76070e8d7).

## Deliverables

1. **The panel record** `docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md`: the D6 panel on
   `r17b_prime.md` rev 2 (critics A contract, B zero-mover + checks, C measurement,
   D generality + unlocks), every id with a one-line summary, the kit manager's
   dispositions, and a BY-ID COMPLETENESS TABLE: **70 of 70 ids dispositioned**
   (A1-A23, B1-B17, C1-C13, D1-D11, U1-U6), each mapped to the revision-3 section that
   carries it. Header counts corrected: critic B is 1 BLOCKER / **9** MAJOR / **7** MINOR
   (its header said 8/8); critic C is 6 MAJOR / **7** MINOR (its header said 8 MINOR).
   Index entry in `docs/dev/reviews/CLAUDE.md`.
2. **Revision 3** of `docs/design/memfn/r17b_prime.md`: every accepted finding folded,
   marked `[rev3]`, with §R3 mapping each id to its section; §0 rewritten; §12 extended.
3. **`memfn/docs/finder_history.md`**: revision 2's row edits (logged late, B9) and
   revision 3's row edits, logged in this commit.
4. Index entries: `docs/design/memfn/CLAUDE.md` (rev 3), `docs/dev/lanes/CLAUDE.md`
   (this report).

## What revision 3 changed (the large items)

- **A4, the define-time query** (§4.5). The read-back moves from `mf_define` to
  `int mf_ask(const mf_art *art, const mf_site *site, const mf_hooks *def, mf_class *out);`:
  PURE (no text, handle, helper or art change; a rejected alternative leaves nothing),
  answering the class of what will actually be RENDERED (so a reader's switch is
  zero-mover by construction), for the OFF variant, and AGREEING with `mf_define` by a
  trace-build check and a G2 family. Facts in (the site, its define hooks, the art's
  denies/measures/analysis/layer); the form CLASS out: `exists`, `libc_free`, `proven0`,
  `includes`, and per presence span the chain-link attributes. Readers: G1 (`proven0`,
  B2; retires into kit row P2 at B3b), R4 (`exists`, `proven0`'s prior mass), `landing`
  L4 (`exists`); `<string.h>` and the stamps read `mf_defined` (written after define);
  the K admission reads NO kit fact (A11). Order: every site a selection reads is ASKED
  before it; edges in pcrec's `reads` DAG point back to FIRST only, so no cycle closes
  through the kit; a trace-build undeclared-read trap. It lands in **B1** (inside B1's
  MF_SITE_ABI bump, with a reader shadow) and **B2 depends on it** (and on main's review,
  Q-R17P-15).
- **A1-A3, sites per activation** (§2.1): one storage point above the first use, START =
  `search_from`, the handoff's `c − K` a use's argument; `attempt_entry` is the third caller
  (ATTEMPT_PRED widened and renamed DFA_ATTEMPT); a VM hybrid holds a presence-only site in
  `_search_run` and a find-only site in `_prefilter`.
- **The table** (§1.2-§1.5): a `kit_table` over `kit_walk` (ROWCON H1's trigger cited); one
  comparator `(lhs, op, key)` (a two-term conjunction for R8) plus boolean site facts;
  applicability in the gate (`site_kind`, `need`, `body`, `layer`); PRES picks as chain-link
  attributes; mandatory `basis` (with a self-check) and `refuted_by`; a per-row `routed` bit
  replacing `fd_route[]`. **23 rows designed, 19 locked at B4**; new: D1c (MLINE's context
  stop, A5), D1w (one member → WALK: the VM hat's |S| = 1 under D167 add. 1 A7, and
  `fd-d1`'s OFF arm, A17), F2 (the VM hat's measured move, B5), R7w (WALK behind a
  measured-key R7, C3); merged: R5 ∪ R6, R7 ∪ R7s (D8). R1/R2 apply only above a fast
  terminal (B14, C1).
- **The step plan** (§3): zero-mover means ARTIFACTS, at SIMD-on and `-fcomments` by lane
  sweeparm's arms (S981/S982); listing streams by DECLARED deltas (B1's five `--list-axes`
  rows, B3b's registry event); no `--emit-facts` section before B4 (A9); B0 "port, then
  gate"; E-1 main's event between B2 and B3a, B3a/B3b against main-after-E-1; MF_SITE_ABI
  numbered relatively; per-step main-side requests for DELEG_SITES / C10 / C17 / MF_VOCAB
  (A8); `cand_rows` readers and trace deltas per step (B4); `fd_rows[]` in rows.tsv; deny
  classes and floors 6 → 11 → 14 → 15; routing observable (pcrec-side routed-record count,
  disagreement witnesses, reverse plant SN-1); the shadow under interim and synthetic sets
  with B1's picks as B4's predicted-mover manifest (B6); per-pick floors (D10).
- **Measurement** (§2.5, §2.6, §5): per-regime floors and upper-bound pay tests (C4); PCU
  arithmetic, ties decline (D9); the crossover literal read off N = 33..46 or labelled
  INTERPOLATED (C5); M24, the shared-body mode branch (A6); card dims (C9); the converter's
  derived-key list (C1). **grid2 slot spec**: 1,501 group-arms, ≈ 91 min required at 3.4
  launches, ≈ 129 at 5 (rev 2's were 87-124 with the gate, C7's "88-113" mixing the two),
  with item 2a (N = 33..46), item 3a (three cover shapes), VM_ATTEMPT one-byte cells for
  F2, NONE as an arm inside item 3's groups, and a cross-launch rerun trigger.
- **The iterator seam** (§6): M as a parameter (`MF_BODY_PARAM`); one carried position per
  REQUIRED span or stream; K5's 16 B row retires only on a proven single-pass form; S
  derived, "48 B" withdrawn (D167 add. 1 A10); B9 after E0 → findall_iter revision → its
  panel → I1.
- **Acceptance** (§9): baseline main's walk; predictions as inequalities on named grid2
  groups (numbers from E4b before E5); the residual named as a stated loss under
  Q-REVAL-1; a Zen 1 bench regression at SIMD-off now refutes.

## Open questions (all for main; each with a recommendation; §7.2 of the note)

- **Q-R17P-15** the define-time query's contract (B2 waits on it). *Accept as specified;
  defining sites earlier instead would move every define point (R17-a measured 9 movers
  from one move) and still need a no-emit path.*
- **Q-R17P-16** R-21 PR-3: ATTEMPT_PRED → DFA_ATTEMPT incl. `attempt_entry`; R-19's
  builder list gains `req_site_define`, MLINE, `attempt_entry`. *Both, one ledger edit.*
- **Q-R17P-17** PR-6 / C-1: presence `omin` from the MATCH START. *Amend; window spans keep
  the origin-relative spelling.*
- **Q-R17P-18** DELEG_SITES / site manifest / MF_VOCAB at B3a: the PRE row merges into the
  FIND row as an ENTRY use (proposed `MF_USE_ENTRY`). *Accept the shape; spelling main's.*
- **Q-R17P-19** `PCREC_NO_REQ_SET_LEAD` at B3b. *Keep as a reserved, ignored name until
  [IFACE-PUSH].*
- **Q-R17P-20** D167 add. 1 A7's "at DFA_HAT": the VM hat is a VM_ATTEMPT consumer.
  *VM_ATTEMPT cells added to item 3; main confirms the addendum's wording.*
- **Q-R17P-21** the kit's `MF_SZ_ADDS` rows and the dial. *Outside the part-layout table
  (they are forms the size ladder reads); helpers follow the position passed as a fact.*
- **Q-R17P-22** `run_axes.sh`'s `--memfn=` arm. *Add it, reading `--list-axes`' `memfn`
  section, with DIFFER / ASSERT_ZERO / REFUSES classes, landing with B1.*
- **Q-R17P-23** a sabotage id block for SN-1..SN-9. *10 ids, before B1's lane.*
- **Q-R17P-24** the second official set vs M1. *No second official set before M1.*
- **Q-R17P-25** `exists` as its own bit. *Keep it, with the `exists = 0 ⇒ proven0` all-ones
  check; derive it only if main prefers fewer bits.*

**To main besides the questions:** requests.md R-21's "(pending)" line is stale (A23);
unlocks U1 (a form ladder) and U3 (one table library across kit and pcrec) proposed as plan
rows with their triggers, unscheduled.

## Charter checklist

| brief item | status |
|---|---|
| FIRST command printed the worktree; BOILERPLATE, memfn/CLAUDE.md, docs/design/CLAUDE.md read | done |
| Scope: writes only in `worktrees/r17bp4` and its gitignored `build/` scratch; no `cd`; no /tmp; no merge, no push | done |
| (1) panel record, by-id completeness table (incl. every MINOR), critic B's count error noted (and critic C's), index entry | done: 70/70 |
| (2) rev 3 with `[rev3]` markers and §R3 by finding id | done |
| D167 and addendum 1 (A7, A10, A11) bound | done (§1.3, §1.4, §4.5, §6, §7.1b) |
| E-1 agreement (B1 declares `mf_analysis`, NULL-tolerant, unread before B3a; main fills after B2) | done (§0, §3.1, §4.7, §4.9) |
| sweeparm's arms cited as THE SIMD-on / `-fcomments` instruments | done (§0, §3.1, §8.1) |
| §2.1, §6, B9 re-read against D163 add. 7 / compound_entries rev 2 and D165 / findall_iter | done |
| A4 designed concretely (signature, when called, readers, B1 vs B2) | done (§4.5) |
| grid2 additions as the slot spec (C3, C5, C7, C8) | done (§5.4) |
| §12 updated; first delivery stays B0-B3b zero-mover | done |
| WIP commits after each section; report; CLAUDE.md index entries | done |
| DESIGN ONLY; no code, timing or heavy `make` | done (table-shape check; `make test-spec-history` 143/2, both reds pre-existing in fddocs_report.md) |
