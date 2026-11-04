# STAGE1 — span_pick rev 5, stage-1 readiness (premise + slot tracing)

Subject: docs/design/memfn/span_pick.md rev 5 (9c9aadb60). Code read in the review tree
(main 7f55a62f9, worktrees/crit-memfn-spanpick5). Rulings read on main 7f55a62f9 (D186 add. 1/2,
roadmap §0a/A-PLAN/§5). Read-only; one `pcrec --list-axes` run, no make, no sweep.

## Findings

### STAGE1-1  D186 add. 2 (main) gives stage 1 a job that no unit carries: the provenance source leaves the seam
- status: CONFIRMED (decisions.md at 7f55a62f9, D186 add. 2 "Blind compiles use the default": "The provenance fields (`mf_prov.source`, the bundle "default" label, memfn.h) leave the seam in span_pick stage 1: the kit never sees the source." Commit 7f55a62f9's subject also says "provenance source leaves the seam at stage 1".)
- severity: design ; effort: one unit row plus its reader list ; blast radius: memfn.h seam, pcrec memfn_sites.c, two tests ; where: §Staging table; §pcrec-side findings ("whether the field stays is main's call"); §Owner rulings "For main: ... `mf_prov.source`'s future"
- body: rev 5 treats the field's future as an open item for main, but main has already ruled: it goes in stage 1. None of 1a-1f removes it. The readers are: memfn.h :1213-1214 (the `mf_prov_source` enum) and :1224-1225 (`source`, `bundle`); src/gen/memfn_sites.c :187-190 (the PCREC_FIND_SRC -> MF_PROV map) and `pcrec_memfn_prov_stanza` (memfn_sites.h :176, .c :573ff); tests/memfn/arm_fixtures.c :1580-1581; tests/memfn/finder_check.py :658 (the L reader regex) and :682ff (R-24). It is an MF_SITE_ABI event. It is byte-identical, because MF_SITE_ABI reaches no emitted text (src/ only assigns `s->abi`, memfn_sites.c :413). Fix: add a unit (1g, or fold it into 1f's seam event) with this reader list, and strike the "main's call" sentences.

### STAGE1-2  The decider census's grep shapes miss the very deciders 1b/1c unify, so the census cannot go red on them
- status: CONFIRMED (`grep -nE 'kit_walk\(|< best|< bm|tie_takes|TIE_|< inc' memfn/src/*.c` has hits only in compose.c, finder.c, ofsskip.c, runcmp.c and window.c. None of the following deciders matches.)
- severity: maintenance ; effort: small (shapes or a function list) ; where: §The tables "The decider census"
- body: these live argmin and first-match deciders leave no hit. (1) presence.c :165 `m < lo || (m == lo && tie_over(...))`: P3's set pick and the second tie spelling (U5). (2) presence.c :182 `c < sm`: P3's run_scan (U2). (3) presence.c :192 `wm < wl`: the run window (T_WINDOW, U5). (4) window.c :1335 `rank_ppm[j - 1] > c`: translate's run rank (U2, 1c). (5) window.c :1754-1755: the B-row renderer first-match `for` loop (T-FRAME's renderer row). (6) finder.c :1065-1085: fd_pres's chain order. (7) precheck.c :158 `implied_by`. Items (1)-(4) are exactly the spellings 1b/1c delete, so the census is blind at its own base to the members it ratchets. The sabotage row (a byte-identical copy of `run_member`'s loop) is caught only because that loop is spelled `< bm` + `tie_takes`; a copy of presence.c's spelling would pass. Fix: make the census a declared FUNCTION list (decider -> table, one line each, with plain loops mapped by hand), with the grep as a backstop that also matches `< lo`, `< sm`, `< wl`, `> c)` and the generic strict-compare-then-assign shape. Add a second sabotage that copies presence.c :182's loop.

### STAGE1-3  1f's reader list is incomplete: a build break, a stale mech sabotage, and its own MF_CLASS_V event
- status: CONFIRMED (grep for `fd-r8|fd-ndisp|mf_finder_pay|fd_pay|pay_fill|n_interval`; finder.c `fd_rows[]` order)
- severity: maintenance ; effort: small ; where: §Staging row 1f
- body: the 1f row lists registry.md, `--list-axes`, emit_sweep.py, memfn_arm.py, finder_check.py and rows. It misses these readers:
  - tests/memfn/arm_fixtures.c :1685 calls `mf_finder_pay`. Deleting the entry breaks the fixture build.
  - tests/mech/sabotages/S1025_sn9-pay-tie-pays.sh plants into `fd_pay` and is registered at tests/mech/run_sabotage_matrix.sh :497. It must be retired, or it reads as not applied.
  - finder_check.py's `--pay-grid` H section (:641).
  - memfn.h :1550-1557.
  - tests/memfn/rows.tsv :119/:123-124 and row_floors.tsv :103/:107-108.
  The rows are ordered `R8 R3a R3b R4 R1 R2 D1 D1c D1w PAIR R7w P0 P2 P3 P4 P9` (finder.c :249ff), so R8, R1 and R2 sit AHEAD of the PRES rows. By the design's own rule ("a finder row added or removed ahead of the PRES rows is an MF_CLASS_V event"), 1f is also an MF_CLASS_V event; its row names only MF_SITE_ABI. The registry hunk itself holds: `memfn` section floor 14 (registry.md :177), 14 denies in `--list-axes` = IDENT_MEMFN (emit_sweep.py :2996), and 14 -> 12 is correct.

### STAGE1-4  1c's U6 is not "kit-only", and its retire condition is already false
- status: CONFIRMED
- severity: design ; effort: one sentence (decide), or a small unit ; where: §Staging row 1c; §What stage 1 deletes U6
- body: the "landmark shadow" (presence.c :222-245) writes the PUBLIC `mf_pres_picks.landmark` (memfn.h :1630). Two places read it today. (a) pcrec itself: emit_dfa.c :11256 `pick_rec("landmark", pl, kl, ...)`, the KW-8 agreement record, under PCREC_CAND_TRACE. (b) tests/memfn/run_pres_picks.sh :61, whose PICKS list includes "landmark". So "retired if no census reads it" is false at the base, and as written U6 does not retire. If it is meant to retire, it touches a public struct (an MF_SITE_ABI event), emit_dfa.c and run_pres_picks.sh, which does not fit a "kit-only spellings" unit. Fix: state the decision (keep the shadow as a named member until pcrec states the landmark as a candidate, or retire it as its own seam event with these readers) and drop "kit-only" for U6.

### STAGE1-5  Purity-breaker cites: (d) has no setter, (b)'s list is short, (c) is already fenced
- status: CONFIRMED (grep of memfn/src and kit.h)
- severity: doc ; effort: text ; where: §The designer/emitter split, "Purity breakers today"
- body:
  - (d) `art->consulted` is never SET anywhere in memfn/src. Its only uses are the declaration (kit.h :292) and the reader in `mf_art_end` (compose.c :1303). "Set by T-PICK rows" describes the future. The plan call takes `const mf_art *` (window.c :1058), so a T-PICK row on the plan face cannot set it. At stage 3, `consulted` must be set on the define path. Say so.
  - (b) the label list misses compose.c :982, :988 and :1005 (`fd_pres(art, art->nsites + 1, ...)`) and fd_route's `handle` parameter (finder.c :863/:871/:888). No row reads `q.handle` (no `->handle` read in finder.c), and the label is read only by `head()` (gate.c :936), which holds.
  - (c) for the window face, the reach is ALREADY counted on the taken call only. `mf_wdecide` calls `decide(art, site, 1, d)` (quiet, window.c :1070); `gate_tctx.quiet` "counts no reach" (kit.h :906-908); phase 2 re-decides once counted (window.c :1812/:1840, the :1815 setup quiet). So 1d's fence for (c) is a KEEP. The real risk is a 1d that serves phase 2 from a stored phase-1 plan ("No cache" forbids it), which would drop the counted define. Name that mechanism.
  - The breaker list is otherwise complete. The only mutable statics are gate.c :850-856 (MF_TRACE only); there are no function-local statics, `_Thread_local` or `getenv` in memfn/src. Of the mutable `art->` fields (`words`, `wused`/`wemitted`, `simd_inc`, `includes`, `forms`, `libc`, `reach_*`, `nreach`), none is read by window.c's decision; they are text-time state (C3's scope holds).

### STAGE1-6  The stage-1 witness cannot fail for a reach-count change, and only weakly for a mass-rounding change
- status: CONFIRMED (row_floors.tsv header: floors are `floor(0.9 x measured)`; emit_sweep.py compares emitted artifacts, dumps, facts and stderr, never MFTRACE reach)
- severity: maintenance ; effort: small ; where: §Staging "Witness, per unit"; 1b; 1d
- body:
  - Reach: "reach floors" are lower bounds. A fence that double-counts, or that drops 10% or less, passes. Stage 1 claims zero movers, so the right check for 1d and 1e is EQUALITY of the N2 census REACH totals (chosen and asked per row) at base vs HEAD. 1e also renames table `wfD` rows into `fd`, so the comparison needs a declared row map.
  - Ties: held. The `-e utf8` arm hands no rates (uniform mass by count), so equal masses are everywhere, and a mis-ordered tie moves bytes in the corpus sweep.
  - Rounding: 62,500 vs 62,496 matters only against absolute constants and ratios: HORS_MIN 145,822 (window.c :1596); MARGIN's x2, where floor(6*1e6/256)=23,437 vs 2*floor(3*1e6/256)=23,436; and the 1e6 cap vs 999,936 at 256 members. A sweep catches a rounding drift only where a corpus site straddles one of these. The design's own counterexample for a set-shaped primitive, `zzzzzzz~J`, is in no corpus or kit test file (grep of tests/ and memfn/tests: 0 hits).
  - Fix: 1b adds a golden-value test of the one primitive (NONE at k = 1, 3, 6, 16 and 256; a repeated byte per position; capped vs uncapped), adds `zzzzzzz~J` to the corpus or a `--patterns-file`, and names the 588 sample's generator (docs/dev/lanes/s3_evidence/gen_sample_588.py) and the bench pattern list as `--patterns-file` inputs.

### STAGE1-7  The purity witness has no harness and no named builder
- status: CONFIRMED (no repeat/reorder plan-call check under tests/memfn or memfn/tests; the nearest precedent is finder_check.py :604, "the query is not pure", via `arm_fixtures --query`)
- severity: maintenance ; effort: small-medium ; where: §Staging 1d "witness: plan calls repeated and reordered give equal plans"
- body: the harness is owed and no lane is named to build it. On today's code it passes trivially (`mf_wdecide` is const-art and quiet), so it needs a plant to prove it can fail: e.g. a row reading `art->nsites`, which must go red under reordering, and a sticky `art->err` case for (a). Fix: 1d's lane builds it in arm_fixtures: N window sites, plan calls in order, reversed and repeated, `mf_wreply` compared field by field, plus that plant as its sabotage row.

### STAGE1-8  "run_group_ok read by BOTH renderers' grouping" would change translate's behaviour, not just its spelling
- status: SUSPECTED (confirm: over the corpus, every B-fn site whose translate group differs from find_groups'; a gcc-free census of `pterm` groups vs `run_group_ok`)
- severity: answer-risk (byte identity) / doc ; effort: text, or a population check ; where: §The tables T-VERIFY "C-run"; 1d
- body: today only `find_groups` reads `run_group_ok` (window.c :1494). `translate` groups by equal `pterm` (window.c :1280-1295). It has no `core` clause, no MF_MAX_TERM cap and no explicit adjacency check (pterm's join, window.c :910-929, gives adjacency and shape, but a PINNED join (`in_pinned`) does not require core). Making translate read `run_group_ok` is a behaviour change unless equivalence is argued. The byte witness only sees it where a B-fn site has a pinned non-core position. Fix: either argue the equivalence in the text, or keep translate's grouping as a named member until a census shows the two agree.

### STAGE1-9  T-FIND's row order in the design is not today's order
- status: CONFIRMED (finder.c :249ff: D1, D1c, D1w, PAIR, R7w; design: "D1c, PAIR, D1, D1w, R7w")
- severity: doc ; effort: text ; where: §The tables T-FIND
- body: the rows are answer-disjoint (finder.c's PAIR comment: two members vs one; D1c is a context stop with no span 0), so the answers hold. But the walk order moves the MFTRACE records and the `mf_finder_rows` listing indices (`pres_row`). Fix: write today's order with "order kept", or declare the reorder with its disjointness argument and its MF_CLASS_V/trace consequence.

### STAGE1-10  The ratchet cannot be counted at stage 1's base yet, and roadmap §0a still contradicts one plan
- status: CONFIRMED (roadmap.md at 7f55a62f9 §5: rows R01-R19 only, each with a grep-able re-count recipe; §0a first bullet)
- severity: doc/process ; effort: a main-side edit before the go ; where: §Staging "Ratchet (proposed for main)"; §The designer/emitter split "(no roadmap edit is left to stage 1)"
- body:
  - Ratchet: the kit rows (find-method deciders, position enumerators, mass variants, tie and run-member spellings, the landmark shadow, inert finder rows) are not in §5. They have no recipes, and "position enumerators" names no members. §5 requires the lane to run each row's recipe at base and HEAD, so main must add the rows WITH recipes before stage 1's first lane can take its base count. That is a pre-build step missing from the unit list.
  - Roadmap: A-PLAN open point 1 is amended on main (5e8bcf455/b405ff811, both ancestors of 7f55a62f9), so that half holds. But §0a's first bullet still reads "it states its candidates and their prices" and "pcrec sees its candidates only as opaque entries with prices", which contradicts one plan with prices in the trace only (D186 add. 2). A §0a edit is still owed, by main, not by stage 1.

### STAGE1-11  D186 add. 2's "rank by MEMBER COUNT, declared as the rules' tie-break" has no stage-1 step, and its readers use it as a rate model
- status: CONFIRMED (decisions.md at 7f55a62f9, D186 add. 2: "With NO rates handed, the kit's rules rank sets by MEMBER COUNT (a uniform mass), declared as the rules' own tie-break, not a rate model (manager, 2026-11-03)")
- severity: design/doc ; effort: text in 1b ; where: §Staging 1b; §The pick "No rates ... rules only"
- body: 1b keeps the NONE-mode total (`uniform_mass`, presence.c :59-62) but declares nothing. Under NONE, the uniform mass is also compared against ppm constants: D-hors's admission (window.c :1596, HORS_MIN 145,822, about 37.3 members) and MARGIN's ratio. Those uses act as a rate model, not as a count tie-break. Stage 1 must keep those answers, so the declaration has to name these readers (or main's sentence needs narrowing). Fix: 1b adds the declared NONE row (member count -> uniform ppm, its readers listed), so the declaration exists before stage 3 reads it.

### STAGE1-12  Minor cite and test-edit gaps
- status: CONFIRMED
- severity: doc ; effort: text ; where: as listed
- body:
  - src/core/findings.h :300 is a comment; `pcrec_find_byte_rate` is declared at :303 (with the macro form at :437).
  - memfn.h :1212 is MF_ANALYSIS_LIST_V; the source enum is at :1213-1214.
  - compose.c :1303 is `consulted`'s reader, not a setter (see STAGE1-5).
  - 1a needs edits in tests/memfn/finder_check.py :109 (FIND_ROWS), rows.tsv :120-122 and row_floors.tsv :104-106. The measure keys `kit.h3a`/`kit.gstar.*` stay in zen4-grid1 with no reader, which is harmless.
  - 1e moves D-hors from table `wfD` into the T-FIND walk, so rows.tsv/row_floors.tsv/rows_check's derived row set and the MFTRACE table names change. Not listed.
  - Every other cite checked holds (PROBED-AND-HELD).

### STAGE1-13  Separability: hidden dependencies, and a cheaper order for 1f
- status: CONFIRMED (code reading)
- severity: maintenance ; effort: text ; where: §Staging
- body:
  - 1c needs 1b. Presence's run window reading T_WINDOW and the presence-member tie row are 1b's. `run_scan` asking `run_member` must take presence's `mf_term` cubes (presence.c :181), which needs 1b's position-multiset primitive.
  - 1e needs 1d. D-hors's admission reads T-VERIFY's tested sets (window.c :1596, `dx->w->set[stop_ix]`) and D-shift resume reads its offsets, so the T-VERIFY step list must exist.
  - 1f after 1e makes 1e's merged walk carry R8/R1/R2, their denies and the pay rule, only to delete them one unit later. Landing 1f right after 1a avoids that work. If the caller-visible change is to stay last, say why.
  - The stated order 1a..1f respects every dependency, but no unit after 1a can land out of order. Say so in the table.
  - No unit is non-byte-identical without being marked. The MF_* events in 1a, 1c-U6, 1e, 1f and the new STAGE1-1 unit move no emitted byte.

## PROBED-AND-HELD

- Purity-breaker cites:
  - window.c :1062 (sticky `art->err`) and compose.c :960; window.c :997/:1007/:1734/:1818, finder.c :930, ofsskip.c :486 and compose.c :268/:281 (the `art->nsites + 1` label).
  - gate.c :936 (trace-only reader), gate.c :850-856 (statics under MF_TRACE) and :884-900 (`reach_print`).
  - runcmp.c :515 (`wused & ~wemitted`) and ofsskip.c :565-567 (`simd_inc`).
  - All 15 say what the design says (with STAGE1-5's caveats).
- Other cites:
  - compose.c :255-258; emit_dfa.c :7598-7604; finder.c :934 (layer hard-coded) and :938 (SF_WINDOW_STOP set only in `fd_find`; its other uses are the PAIR row's facts and comments); window.c :1061, :251-254 and :877-878 (`rd_set`, `reseed`).
  - compose.c :869-882 (`mf_art_begin` takes the set and analysis per art); window.c :1592-1597; ofsskip.c :414-416 (`fn_rows` BODY).
  - presence.c :48-56 (`kit_byte_rate` returns the handed table or NULL) and :58-113 (NONE = uniform by count); presence.c :222-245.
  - emit_dfa.c :1045-1077/:1058 (`req_run_member`) and :9064 (`req_landmark_admits`); findings.c :745/:780; kset.c :294.
  - `rc_row_of` (runcmp.c :214), `kit_set_test` (generic.c :106), `member_test` (generic.c :133), `wf_erows`, `b_fn_holds` (window.c :1673), `run_member` (window.c :763, `< bm` + T_MASS_STRETCH), `wf_ties` T_* rows (window.c :77-110; `tie_takes` returns 0 for EXCHANGE/LEFTMOST, matching "strict <").
  - About 30 cites in all.
- Counts against population/span_pick/counts.out: 371 of 371 RTE OFS sites with no kind; A-floor 1,397/1,800 RTE and 1,420/1,835 incl. DEF; 1,742/1,767 PF sites; 1,429 PARKED+RESEED / 291 NONE / 22 PARKED; 740/714 RESEED core positions. All match.
- `mf_set_terms` (1a, N3): no caller outside terms.c; internal (kit.h :498-503), not public; deleting it is no seam event.
- 1f's caller-visible hunk: registry.md §6¶8a rows `fd-r8`/`fd-ndisp` (:168-169) and §6¶8b floor 14 (:177); `--list-axes` shows 14 memfn denies, equal to emit_sweep's IDENT_MEMFN, and ASSERT_ZERO/DIFFER_PINS carry `fd-r8`/`fd-ndisp` (emit_sweep.py :556-560, :605-608). 14 -> 12 is right. No docs/spec/cli.md hit.
- emit_sweep.py as the witness: it covers default, `--engine=vm`, every `--memfn=no-X` (IDENT_MEMFN), every accepted axis flag incl. `-fmemfn-simd`/`-fno-memfn-simd`, `-e utf8`, `--list-*` dumps (stream 5, so 1f's `--list-axes` change is seen), `--emit-facts`, stderr, and `--patterns-file` for extra populations. A mis-ordered tie IS detectable (the utf8 arm hands no rates: ties everywhere). The limits are in STAGE1-6.
- Plan-face purity beyond the listed breakers: `mf_wdecide` takes `const mf_art *`, calls `decide` quietly, reads only site facts and per-art inputs (`an` via `kit_byte_rate`, `ms`, `denies`, `levers`), and frees its heap state. No reader of earlier sites (`art->sites`) in the decision path; no cache.
- MF_SITE_ABI / MF_CLASS_V do not reach emitted text. `pres_row` is resolved by pcrec through the `mf_finder_rows` listing, trace-only (memfn_sites.c :779-797), so row deletions are seam events, not byte movers.
- Roadmap A-PLAN open point 1: amended on main (5e8bcf455, b405ff811 are ancestors of 7f55a62f9). Holds; §0a does not (STAGE1-10).
- D186 add. 2 on main against the stage-1 list: the "O3 = WAIT", `zen4-grid3`, "one plan, with the trace", "pure function" and "D186 over D144" lines are all reflected. The two that are not are STAGE1-1 (provenance) and STAGE1-11 (member count).

## Readiness verdict

- 1a: ready with listed text fixes (STAGE1-12 test edits; STAGE1-2 and STAGE1-10: the census and ratchet base this lane writes need the fixed census shapes and main's ratchet rows with recipes first).
- 1b: ready with listed text fixes (STAGE1-6 golden primitive test and `zzzzzzz~J`; STAGE1-11 the declared NONE/member-count row).
- 1c: ready with listed text fixes (STAGE1-4: decide U6, keep or retire, as a seam event with its pcrec readers; STAGE1-13 state its dependency on 1b).
- 1d: ready with listed text fixes (STAGE1-5 breaker list and the existing `quiet` fence; STAGE1-7 purity harness owner, shape and plant; STAGE1-8 argue or drop "run_group_ok read by both"; STAGE1-6 reach-equality check).
- 1e: ready with listed text fixes (STAGE1-9 row order; STAGE1-12 wfD -> fd test and trace edits; STAGE1-13 its dependency on 1d; consider landing 1f before it).
- 1f: ready with listed text fixes (STAGE1-3: arm_fixtures.c :1685, S1025 retirement, the pay-grid section, rows/floors, and its MF_CLASS_V event).
- Missing unit: the provenance-source removal ruled on main (STAGE1-1) must be added.

**Overall: ready for a build go: YES WITH LISTED TEXT FIXES:** STAGE1-1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13. The ones that need a decision rather than a sentence are STAGE1-1 (add the unit), STAGE1-4 (U6 keep or retire), STAGE1-8 (equivalence or keep) and STAGE1-10 (main adds the ratchet rows with recipes before the base count).
