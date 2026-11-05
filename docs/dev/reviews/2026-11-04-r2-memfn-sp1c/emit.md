# EMIT lens findings — critic round memfn-sp1c (code), 2026-11-04

Subject 3ecb647c7 vs BASE 7b671bc2c. Method: (1) BASE vs SUBJECT emitted C +
MFTRACE records (trace pair, whose C equals the plain binaries' on a checked
sample); (2) a DUAL-SPELLING plant in a private export of the SUBJECT kit
(emit/plant/, built to emit/dualbuild/pcrec-dual): every replaced computation
recomputed in its BASE spelling beside the new one, a `DUALBAD` line on any
disagreement and per-site reach counters at exit; (3) code reading.

## Findings

No mover found. Every replaced computation agreed with its BASE spelling at
every reach (0 disagreements), and BASE vs SUBJECT emitted C and MFTRACE
records were byte-identical on every case that compiled. One maintenance
note below.

### EMIT-1 (CONFIRMED as a fact of the code; no mover today) — one TIE row, two key spaces
- Severity: maintenance. Effort: trivial (pass `r->start + j`-style
  offsets, or say in kit.h that T_MASS_STRETCH's keys may be run-relative).
  Blast radius: none today. Any future TIE row kind that is not
  translation-invariant would move run_member's pick.
- Where: memfn/src/window.c:777 and :780 (`kit_run_member`) key
  T_MASS_STRETCH on RUN-RELATIVE indices `j`/`b.pos`. a_mass_choose
  (window.c ~572) keys the SAME row on absolute offsets (`k + WF_LO`).
  memfn/src/kit.h:365 says "Keys are offsets, except T_PRES_MEMBER's".
  BASE's run_member passed `r->start + j`. The answers agree only because
  the row's `to` is TIE_HIGHER, a pure `c > b`, which a shift does not change.
  If the row is ever retuned to a kind that reads the key's absolute value
  (a nearest-to-candidate or sign-sensitive rule), run_member, P3's scan and
  translate's ranking all move, and neither kit_tie_takes nor the TIE table
  says this row is fed two kinds of key.
- What would confirm a mover: none is reachable under today's three `to`
  kinds (HIGHER/LOWER/LEFTMOST, all comparisons). Recorded so that a later TIE
  edit does not turn it into one.


## PROBED-AND-HELD

Compile budget used: 1,409 of 1,500 (counted per invocation in emit/compiles.log).

1. **Dual-spelling plant** (emit/plant/, the SUBJECT kit export with BASE's
   spelling recomputed beside each new one: `DUALBAD` on disagreement, reach
   counters at exit). Its own control: a sabotage copy (emit/sab/) that
   drops kit_run_member's tie fired `DUALBAD` on P3 scan, window run_member
   and translate rank (3 of 4 probe compiles). pcrec's own cross-check also
   refused the sabotaged run member: "internal error: the window family's run
   member 0 is not the run window's own index 7".
   Totals over 666 dual compiles (30 crafted witnesses x 11 configs; 250
   corpus patterns sampled from the 666 corpus lines that hold a literal
   run, (?i) or adjacent classes, rotating 10 arm x regime configs; the 31
   pres_pick_witnesses/c10_presence rows with their own flags plus 12
   n2_sample patterns, each under default and a uniform bundle). 0 BAD in
   every counter:
   - P3 run scan (kit_run_member vs BASE's rightmost-first strict `<` over the
     cube mass): 12,785 reaches, 0 bad;
   - P3 run window mass (set multiset vs cubes): 9,997, 0 bad;
   - P4 set_leads: 10,635, 0 bad;
   - landmark admission `h`: 350, 0 bad;
   - window run_member (exact and whole): 13,756, 0 bad;
   - translate rank_pos/rank_ppm (walk vs insertion sort over the term's
     cube): 734 reaches over 267 cases, 0 bad;
   - translate plan sets `w->set[hint_at+k]` vs the term's derived cube: 734,
     0 differ;
   - tie present among a scan's run positions: 7,245 sites; masked run
     positions: 4,430; runs longer than MF_PRES_WINDOW: 5,146. So ties, masks
     and long runs were exercised, not merely possible;
   - translate n > MF_RANK_MAX: never.
2. **Normal-form refusal** (kit_presence_check, the question "can a site
   pcrec emits now be refused?"): the plant counted every RUN presence span
   reaching the check. 12,554 checks, 0 non-normal. The BASE trace binary's
   KITMASS `nonnormal` read 0 on all 168 BASE/SUBJECT cases that compiled.
   Held by construction as well. pcrec's only pspans constructor
   (req_pres_spans, src/gen/emit_dfa.c ~1475) copies `whole`/`whole_mask`
   from the necessary-run walk. Every run position there comes from
   `rn_put` (src/facts/req.c:277), which fails the compile (internal error)
   on `t & ~k`. rn_app/rn_pre only copy already-normal positions.
3. **Byte identity BASE vs SUBJECT** (emitted C + MFTRACE REACH/SEL/ROW/END
   records + non-trace stderr), 330 cases:
   - 30 crafted witnesses x 8 configs (the four arms; `--analysis log`;
     vm/simd x log). 30 of these were also compiled with the plain build/pcrec
     pair. 168 compiled and were identical. 72 failed identically on both
     sides: `--analysis uniform` is not a built-in bundle ("unknown analysis
     'uniform'"), and `\b` needs module 'assertions'.
   - Then the 30 witnesses x 3 configs under REAL -I bundles written for
     this probe (emit/bundles/uniform.rxt, every byte equal; ties.rxt, case
     pairs, letters and digits tied): 90 of 90 identical.
   - Trace-binary C = plain-binary C, checked on 2 patterns.
   - Witness shapes: case-folded runs; [aA]-style and one-bit-pair masked
     runs; runs of 12-40 bytes (longer than the window); `zzzz~J`
     repeated-byte ties; mask-0 (`.`) run positions; multi-member set terms
     ((cat|dog), x[abc]y); Latin-1/high-byte classes; handoff shapes
     (\w+@example\.com); the NONE row (-e utf8).
4. **By reading** (each held, with no plant needed):
   - compose term_prove: the old run branch is exactly kit_run_set's
     formula, and mask NULL still reads 0xFF.
   - a_parked_choose, a_model_choose, a_mass_choose and d_hors_holds: a
     signature change only. The set path of kit_mass is unchanged; the
     removed cube path was fed only by presence's run_pos.
   - Landmark with no run and no pick: the empty set's mass, which is 0 under
     both rate and NONE, is now the literal 0.
   - P4: kit_presence_check requires a SET presence span to have exactly one
     member, so the span's set is `{q}`.
   - The rank walk equals the insertion sort: ascending mass, ties to the
     higher position, every position exactly once.
   - run_bytes leaves `a` unset only on an EMPTY plan set. That is
     pre-existing and the same in both spellings' input. Counter 7 shows it
     was never reached.
   - asm (gcc -S) was not needed: no C differed.

CRITIC COMPLETE
