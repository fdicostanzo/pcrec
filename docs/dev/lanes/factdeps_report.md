# factdeps: fact-consumer inventory and three-layer check sketch ([FACT-READS], proposed tag)

Lane factdeps, opus, 2026-11-12. Read-only inventory plus design sketch. No code, no build, no runs.
Deliverable: `docs/design/fact_consumers_inventory.md` (PROPOSED rev 0), indexed in
`docs/design/CLAUDE.md`.

## STATE AT HANDOFF

- Branch `lane/factdeps` from main `8184f6fb6`. The memo, this report, the `docs/design/CLAUDE.md`
  line and the lanes history index entry are committed.
- Rulings file `docs/dev/lanes/factdeps_rulings.md`: empty at every read. No entry was applied.
- Validation: none owed. No suite or build was needed (docs only). `scripts/check_claudemd_size.sh
  --all` is clean (`docs/design/CLAUDE.md` is 12,282 of 12,288 bytes; the cond_family line was
  shortened to fit the new entry).
- Scratch: `/var/tmp/pcrec-pcrec/scratch/factdeps/` holds `sites.txt` (the accessor call-site scan)
  and `emit_vm_rpfix.c` (`lane/rpfix`'s `emit_vm.c`, read for O12-O14). Neither is committed.
- Fan-out note: four Explore subagents were launched for the fact gathering. All four ended without
  delivering a report. Everything in the memo was gathered directly in this lane.

## FINDINGS

1. **Consumers (memo §1.1).** 60 functions in 8 files (95 call sites) ask facts outside `src/facts/`.
   Almost all of them are in `src/gen/emit_dfa.c`. `req_run` has 20 call sites. Three facts
   (`req_pieces`, `req_set_maxoff`, `req_run_maxoff`) have no consumer call at all. Stages are
   named from `compile_driver`'s real order (memo §0): S0 resolve through S9 listing, with E1 at
   compile.c:2929, E2 at :3043, and E3 at :3200 (ENG_UNANCH only).
2. **The consumer side already has a checked declaration mechanism at SLOT grain.** `cand_nodes[]`
   (`emit_dfa.c:10072`) declares slot→slot `reads`, `under`/`by`, `kask`/`kfields` and the runtime
   `succ`/progress classes. The trace build traps undeclared reads and asks (`cand_read_hit`,
   `cand_ask_check`). The missing piece is one column, the FACTS a slot reads. The design extends
   that table and `facts.def` and adds no parallel mechanism (memo §1.4, §6.4).
3. **Undeclared proof uses (memo §1.2).** The sharpest one: the VM route's minimum width is
   `pcrec_minw(root)` (`emit_vm.c:10602` → `CandVmFacts.root_minw` → `cand_min_width`,
   `emit_dfa.c:10234`). The DFA route reads the declared `width` fact. That is one question with two
   definitions, and the VM one's soundness ordering (after the callgraph fixpoint) exists only as a
   comment. Also undeclared: the emitter's direct `pcrec_dfa_accepts_nowhere` calls beside the
   `never_matches` fact, and the fallback ladder's reads (rows declare `.sets`, never what they read).
4. **"Asked" is control flow, kept still by BALLAST (memo §3).** Four asks exist only to keep
   `--emit-facts`' `used` column still: `select_engine.c:1210`, `emit_dfa.c:1602-1603`,
   `emit_dfa.c:8704`, and s1fix's re-added `attempt_entry` ask. Incident 2 counted an E3 fact as
   "consumed" on a route where it is `absent`. Proposed definition: `used(f)` = a declared reader
   that ran lists `f`. Migration is shadow-then-switch, with the `facts_listing.md` §4.1¶2 hunk.
5. **Orderings (memo §2).** 17 are listed. O1-O3, O9, O10 and O17 are declared and checked. O4
   (machine-final), O5 (`root_minw` after the fixpoint) and O8 (ladder writes → readers) are comments
   or half-declared. The EMITTED orderings O12-O15 (clamp → min-width → pre-check → handoff → offset-0
   seek → start-set seek → attempt loop) are prose only. **Incident 1 (O14) is an emitted-order
   defect, not a compile-time read-order one**, so a fact-read check alone cannot catch it. The memo
   adds a second axis: a position-MOVE / re-check-after-move column on `cand_rows[]`, checked over
   the trace stream.
6. **Seam domains (memo §4).** `mf_site.head_max` has no reserved value. 0 means "no handoff", and
   pcrec's `PCREC_W_UNBOUNDED` (2^40) reaches it on the unbounded handoff row (incident 3).
   `span_lo/hi` is translated to `MF_SPAN_UNBOUNDED` by hand at four builders. The window fields'
   `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` appear in memfn.h's changelog prose with no `#define` at
   this commit (flagged for the kit, not traced further). `facts.def` has no value-domain column.
7. **Composition coverage (memo §5).** `make test-axes` sweeps one flag at a time. One pair is
   declared disjoint (end window × `\G`) and one is declared composed (G1 × handoff). Seven sharing
   pairs are declared nowhere, incident 1's pair among them.
8. **Check design (memo §6).** WRITE: a lint of predicate text against the row's declared mask
   (blind past one helper level). COMPILE: (a) a generated epoch-vs-stage table check (recommended;
   it refuses a declared read of an unsealed-route fact) and (b) typed seal tokens (deferred, with a
   trigger); for domains, a one-member `PfW` type at the seam builders plus one generated converter
   (catches incident 3 at compile time). TRACE: `pf_enter` checks the innermost open reader in the
   existing `PCREC_CAND_TRACE` build; the move/re-check stream checker catches incident 1. Coverage
   per incident is in memo §6.5.
9. **Size (memo §7.1): 9 units, R0-R8,** one commit each under the zero-movers gate. R0-R4 are the
   core (declarations, trace trap, `used` re-sourced). R7 is the seam domain plus a kit request. R8 is
   the emitted-order axis. The VM `root_minw` double definition is a separate fact change and is
   kept out of these units (`[FIND-MINW]`'s trigger already names it).
10. **The [COND-FAMILY]/[ENG-TDFA] plan (memo §7.2)** adds an `A_COND` arm to every no-`default:`
    derivation, new facts (`tag_shape`, a condition kind bit, M12 guards), new consumers (the
    tagged-DFA engine row and entry, PRESENCE guard rows, M10 ladder rows, [ENGINE-WHY]), a new E3
    route, and new emitted orderings (M7 honour-on-close, the tagged entry inside the window
    protocol). The last is why R8 belongs in the foundation.

Proposed plan tag: `[FACT-READS]` (free per `scripts/entry`). The row is the manager's to file.
