# r17bp3 — R17-b′ design note REVISION 2 (the kit's first candidate-finder delivery)

Lane `r17bp3`, 2026-10-14, opus, DESIGN ONLY. Branch `lane/memfn-r17bp3`, cut from the
kit branch `lane/memfn-r17` (`aea223614`). Delivers `docs/design/memfn/r17b_prime.md`
revision 2 (revision 1 is `830bbce39`), with `[rev2]` markers and a change log (§R2).
Nothing under `src/`, `memfn/`, `tests/` or `lib/` changed; no build, no timing, no
measured constant in any source. Inputs read from MAIN (`git show main:...`): requests
R-17..R-21, decisions D161 (+ add. 1-15), D162 (+ add. 1-4), D165 (+ add. 1), D166
(+ add. 1/1.1/2), regime_tables rev 0.5, measure_sets rev 2.1, findall_iter.md, main's
`emit_dfa.c`/`emit_vm.c`/`memfn_sites.def`/`memfn.h`/`options.def`/`lib/pcrec.h`/spec
for the current state (abi 78, MF_SITE_ABI 10, `memfn` floor 6, bit 55 free); from this
worktree: winreq, sbscope, pcscope, regime_eval rev 2.2, finder_history.md,
window_contract.md (identical to main's).

## What revision 2 is

The ONE design for the kit's first candidate-finder delivery, against MAIN's code. Main
has neither R17-a nor R17-b (the kit branch's merge was aborted), so both are PORTED
steps (B0, B4), and every census in the plan is re-taken against main.

1. **Scope and table (§1).** Set FIND, the one-byte stops (PF, DFA hat, hybrid, MLINE),
   and the presence pre-checks + handoffs merged into ONE window request per search
   entry (one `mf_site`, several uses). `fd_rows[]` gains a SLOT column: 21 rows
   designed, 15 FIND + 6 PRES. 18 are built by B1/B3b and LOCKED at B4; F0 (NONE), F1
   (a measured libc row) and P1 (the priced pre-scan) are formal post-lockdown
   additions at B5. The Q-WR-1 defaults are D1 (one member and not the VM hat's seek →
   the libc row, UNMEASURED-DEFAULT) and R7 (LINER); PRES's default is KEEP (Q-WR-9).
   A temporary declared list `fd_route[]` keeps each site group SHADOW until its step.
2. **Step plan (§3).** B0 port R17-a (zero, MF_SITE_ABI 10→11); B1 = ST1 + R-19 +
   R-20's kit half + E3 (zero; →12); B2 = ST2 one-byte routed (zero; →13); E-1 (main,
   window_contract S1, its own abi event); B3a presence shadow, five-pick comparator at
   100% (zero; →14); B3b presence + handoff routed (zero for artifacts; a registry event:
   bit 45 → `--memfn=no-pres-set-lead`). FIRST DELIVERY COMPLETE, no pcrec abi event of
   its own. Then grid2, E4-E8 judge, and B4 the routing commit = LOCKDOWN (the one
   censused mover; ONE abi event 78 → next carrying M0's stamp, bit 55's size rung,
   PR-10's comment; →15). B5 measured rows (one census each), B6 SIMD (SIMD-off zero),
   B7 libc deny (future), B8 dispatch if not paid at B4, B9 R17-b″.
3. **Contract (§4).** A PRESENCE span class (`omin` from the MATCH START, `member_order`,
   no `omax`), `head_max` on the site; range-level binding once per activation over
   `[start + omin, n)`, EMPTY = NOMATCH, decided first; the unconstrained reply
   `[lo, n)` legal iff span 0 is OPTIONAL or absent; the per-candidate cut a permission
   (iterator only); proven facts `proven0`/`scan_exists`/`includes`/`pres_kept` as the
   read-back for pcrec's six readers (G1, R4, the K admission, `landing` L4,
   `<string.h>`, the stamps) with no form name; the K65 obligation per consumer; all
   sixteen winreq C-items mapped; `mf_measures`/`consulted`/`mf_form_hash`/reader
   declarations/cards per R-MS1..5.
4. **Measurements (§5).** 23 quantity families (M1-M23), 15 in grid1, 8 ABSENT (the three
   dispatch charges, the one-byte libc and libc-free costs and crossover, NONE's gap
   threshold, the pre-scan gate); a card per quantity under `kit-grid@2`; the `libc:`
   dependency as provenance plus a set-level `libc-mismatch` flag.
5. **zen4-grid2 (§5.4): ONE slot, ≈ 88 min required, ≈ 96 min with the optional items**:
   the 149 fit groups streamed (56.1 min), dispatch twins (5.2), one-byte arms (13.5),
   NONE arms (2.4), build + answer gate (~10); optional F2 perf passes (~6) and a
   pre-scan trigger probe (~2). The paranoid suggestion moves from E4 into grid2's prep.
6. **R17-b″'s seam (§6).** H rows, A3, the presence carry (`valid_until`), the cut-off as
   a permission; the kit's row 40 B with the form byte recomputed; S = 48 B if pcrec's
   K5 pair-hit row retires, 64 B if not.

## Findings (the note's §11; new in revision 2)

- **F10** the first delivery needs no measurement set; **F11** presence `omin` from the
  match start makes the zero-mover window exact; **F12** proven facts are decided once
  per site at layer OFF; **F13** R1 must read the crossover against the TERMINAL pick
  (rev 1's would have dispatched one-byte LIBC sites once grid2 paid); **F14** KW-8's
  fifth pick (the landmark admission) is an ORIGIN choice; **F15** Q-WR-11's "no
  `-fcomments` move" cannot hold if the text changes; **F16** findall_iter's K5 pair-hit
  row loses its owner under the merge; **F17** `libc:` cannot be row staleness (the
  run-time library is the caller's); **F18** regime_eval's suggestion sits in E4 but
  grid2 runs first; **F19** R-19's three storage points omit the PRE composite's entry;
  **F20** one-byte sites are zero-mover against both branches, set sites only against
  main; **F21** rows whose quantities grid2 measures must be built after lockdown, or
  they fold their movers into B4.

## Questions (§7)

Rev 1's Q-R17P-1..8 CLOSED with their rulings (§7.1). New, each with a recommendation:
Q-R17P-9 grid2's fit condition (streamed re-fit, ~96 min, vs grid1's condition + a
streamed pass, ~176 min); Q-R17P-10 S (48 B, retiring pcrec's K5 row); Q-R17P-11 the
landmark admission stays pcrec's under framing (a); Q-R17P-12 the PF comment rides B4;
Q-R17P-13 zero-mover routing may precede the judge (the gate is the first MOVING commit);
Q-R17P-14 the `libc:` dependency owner as provenance + a set-level flag.

## Sabotage

S911-S922 (R17-b′'s 12, R-19's inside) and S964-S980 (R-21's SW-1..17), each with its
step, detector and reach witness (§8.3). Rows unreachable before their step are declared
UNREACHED with the step that reaches them (S911-S913 until a dispatch pays, S969 until a
true `omin`, S974/S976/S978 until B5, S979 until R17-b″). B6 needs its own ids.

## Validation

Docs only: no build or suite applies. Every file:line and population was re-read from
main or from the scoping reports it cites; no instrument was re-run (revision 1's
transcripts in `r17b_prime/out/` were taken on the kit branch, and the plan re-counts
against main at each build step). Nothing owed.

## Commits

On `lane/memfn-r17bp3`: WIP commits per section (`fae877d9d` §0-§1, `5fddb6b3c` §2-§3,
`554634707` §4, `23ba79f1c` §5, `70c7befd8` §6-§9, `e608bca34` §10-§12, `43074f406`
and `4e8033c60` consistency passes), then the final commit with this report.
