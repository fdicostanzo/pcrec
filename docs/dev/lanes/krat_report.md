# krat: kit ratchet rows and span_pick plan rows (docs only, 2026-11-03)

Base: main 27cfc44f7, branch lane/krat. Edited: docs/design/stream/roadmap.md (section 5), docs/dev/plan.md, docs/design/plan_row_bodies/IFACE-PUSH.md. No code, no make, no suite.

## Ratchet rows

Rows R20-R27 follow R19 in the roadmap section 5 table (area A-PLAN, p1build column "n/a (kit row)"). Counts were taken by running each recipe's grep at 27cfc44f7 over memfn/src; the counting rule is the header's (a family of n spellings counts n - 1; a unit the end state keeps none of counts whole). One dated line was added to the "Ratchet log": total 44 = 29 (p1build merge as it stands) + 15. No existing row changed.

| id | family | members found (recipe hit counts) | count |
|---|---|---|---|
| R20 | find-method deciders | fd_route 1 (finder.c), fd_find 1 (finder.c), select_arm 1 (compose.c), fn_rows BODY 2 rows = 1 member (ofsskip.c): 4 | 3 |
| R21 | position (stop) enumerators | a_model_choose 1, a_mass_choose 1 (window.c): 2 | 1 |
| R22 | mass variants | cube_mass 1, kit_set_mass 1, kit_set_sum 1, window_mass 1 (presence.c): 4 | 3 |
| R23 | tie-rule tables | wf_ties 1 (window.c), tie_over 1 (presence.c): 2 | 1 |
| R24 | run-member spellings | run_member 1 and translate's rank_pos line 1 (window.c), P3 run_scan line 1 (presence.c): 3 | 2 |
| R25 | landmark-admission shadow | marker "the FIFTH: the landmark admission" 1 (presence.c) | 1 |
| R26 | inert finder rows | R3a, R3b, R4 rows in finder.c fd_rows: 3 (end state keeps none) | 3 |
| R27 | mf_set_terms, no caller | defined terms.c; zero other `mf_set_terms(` lines in memfn/ src/ cli/ lib/ tests/ outside terms.c and kit.h | 1 |

Total 15. Sources: span_pick rev 5 section Staging (units 1a-1d, the Ratchet sentence), units_inventory section 4 (U2-U6) and section 3 (N3), kitunits_report section 2a items 1, 3, 4, 7.

Judgment calls for the manager to confirm:
- R27 (mf_set_terms) and R26 (inert rows) are rev 5 unit 1a's "4 members", reading "inert finder rows" as R3a/R3b/R4 and adding N3 as its own row; rev 5's ratchet sentence names only "inert finder rows". R8/R1/R2 (unit 1f, retired with denies) are NOT counted, since the sentence does not list them.
- R21: rev 5 unit 1d deletes "a_model_choose's private enumeration" and "mass_domain's copy"; I counted the two enumerating functions (1), not the copy as a third member. If the copy should count, R21 is 2.
- R23: counts kit-side tables only (rev 5 1b says "2 tie spellings"; the third is pcrec's PICK, D157). A_parked_choose (a k0 price, no enumeration) is not counted.
- R22: kit_set_mass is counted as a variant though it calls kit_set_sum (it is the capped form); rev 5 says 1b deletes "2-3" of them, consistent with 4 - 1.
- "UNCOUNTED": none. `b_fn_holds` is FRAME family per rev 5 and is not a row.

## Plan rows

Filed in the Backlog section, not Active: `scripts/plan_lint.sh` rule PL13 flags a top-level `STATE:not-started` row in Active ("expects started/blocked"), so the brief's "Active" and "STATE:not-started" cannot both hold; lint won. Move them if you want them in Active as started.

| row | source sentence in rev 5 |
|---|---|
| [SPAN-PICK-UTF8] | "For main" line (rows [SPAN-PICK-UTF8], ...); section The pick 6 / Uncovered: "Under `-e utf8` blind is NONE today (`findings.md` section 2 para 7); the gap is byte-encoded compiles over UTF-8 text: priced rows over two-member stops are gated on a fix (an encoding fact, or a per-encoding default prior)." Trigger wording from review 2026-11-03 r2 ("[SPAN-PICK-UTF8]'s per-encoding prior, or a priced row on NONE"). |
| [SPAN-PICK-PERCALL] | section With data: "(i) the cards' regime is the cell's (long subjects; per-call cells need [SPAN-PICK-PERCALL]'s term)". Rev 5 says no more; the per-byte-cards-versus-per-call-bar reason is review r1 MEAS-5 (cited in refs). The trigger is mine, built from that: an open question for the manager. |
| [PICK-IDIOM] | Rev 5 only names it in "For main". The description and trigger (the first T-PICK row's landing) are from review 2026-11-02 r2 (F, SLOT-14), cited in refs. |

IFACE-PUSH: the row's refs line gained "2026-11-03 class option (span_pick rev 5)"; the one dated line recording the option is in docs/design/plan_row_bodies/IFACE-PUSH.md, because the row's charter already sat at the 6-line maximum (PL11 fired when I put the line in the row). Rev 5 itself says only "an [IFACE-PUSH] class option"; the content (a class-declaring compile input; no compile can declare a class today, only `idk`) is review 2026-11-02 r1, D2 / MEAS-4.

Validation: `(cd WT && scripts/plan_lint.sh)` prints "276 rows parsed, 0 violations". No `plan.md:<number>` text written.

## STATE AT HANDOFF

STATE: done; OWED none. Edits committed on lane/krat (named paths only). Rulings file docs/dev/lanes/krat_rulings.md did not exist at start or end (no rulings applied). Open for the manager: the four judgment calls above, and where the three plan rows should live (Backlog now).
