# tests/memfn — pcrec's side of the memfn kit's checks ([MEMFN])

pcrec's checks on the search-code kit (`memfn/`, D146/D147;
`docs/design/memfn/integration.md`). The kit's OWN tests (G2) live under
`memfn/tests/`, not here. Born at R4a (lane memfnmanifest, 2026-10-05) with
C17. R4c's lane r4cchecks (2026-10-06) added C4, C12, C13, C14, C17's
re-keyed dynamic half and the VM hybrid handoff reach floor (below). Later
pcrec-side kit checks and pins (`pins/`, C5/C10, §17.4) land here too.

## Files

- **site_manifest.tsv** — THE CHECKED SITE MANIFEST (integration.md §R4.3.4, D147 addendum 5): one row per search or span-compare site pcrec emits (13 at R4a: PF, PRE, ...
- **search_vocab.tsv** — THE SEARCH-FORM VOCABULARY: the text shapes that count as a search form when an emitter spells them.
- **c17_lex.py** — the emitter reader.
- **site_manifest_check.py** — C17 itself.
- **site_census.py** — C17 rule 2's mechanism: `find_callers` (calls to `mf_define`/`mf_emit` under `src/`, attributed to the enclosing function, comments and strings ...
- **run_site_manifest.sh** — the entry point (`make test-memfn-manifest`, in TEST_SECTIONS; mech arm `memfnmanifest`).
### C4, C12, C13, C14 and the reach floor (lane r4cchecks, R4c)
- **arch_blind_check.py**, **run_arch_blind.sh**, **c4_allowlist.tsv** — C4, the arch-blindness detector (`make test-memfn-arch`; mech arm `memfnarch`).
- **form_checks.py**, **run_form_checks.sh**, **c12_ceilings.tsv** — C12, C13, C14 (`make test-memfn-forms`; arm `memfnforms`).
- **run_handoff_reach.sh** — the VM routes' handoff reach floors (`make test-memfn-reach`; arm `memfnreach`): four VM hybrid witnesses (two with the prefilter's re-entry, [REQRUN-VM]) and the VM attempt loop's rows: four admitted witnesses (re-entered or entry-only, one with its utf8 round-up line) and the declines pinned to `none` ...
### C11's routing leg (lane r4e0b, R4e'.0b)
- **routing_shape.py** — C18's ROUTING leg (D155 item 6 and addendum 1): every offset-skip/pre-check function in an artifact (a `static inline size_t` named by pcrec's ...
### C15 and C16 (lane memfnskel)
- **run_link_checks.sh** — [MEMFN] R4a: `make test-memfn-link`, a `make test` section; C15, C16 and R-28's frame check (no kit function over a 4 KB stack frame, `-O2 -fstack-usage`, with a planted-fat-frame witness).
- **c15_allowlist.txt** — C15's exceptions, one undecorated symbol per line, each with its reason.
### C5 and C10 (lane r4ccore, R4c)
- **arm_fixtures.c** — (R17-a, MF_SITE_ABI 11, lane r17a: every kit call states a forward FIND's window as pcrec's builders do, `fx_win`/`FXW`, applied after the fixture's ... Since D172 S2 commit 6 (lane wsc6) `fx_win` states span 0's class only (the renderer interface): W0-W2 and the R-26 prefix/context facts left with their fields, and the nine window gate cases with them (`GATE_CASE_FLOOR` 98 -> 89).
- **pins/arms.tsv** — C5's pins: arm (the kit's form id), fixture, part (`def`/`use`), bytes, sha256. Recorded at R4c's IMPLEMENT commit, whose I1 shadow comparator proved ...
- **run_arm_pins.sh** — C5 (`make test-memfn-arms`, in TEST_SECTIONS).
- **pins/r4h_target/** — R4h's FROZEN TARGET (lane advtarget, 2026-10-08; its own CLAUDE.md): one `<fixture>.c` per in-loop ADVANCE shape, a 3-line header, the kit's text ...
- **pins/n7_target/** — M7's FROZEN TARGET (lane m7, 2026-10-08; its own CLAUDE.md): one `<fixture>.c` per byte-wise span-compare shape (exact, the UCP expression fold, ...
- **pins/m6_target/** — M6's FROZEN TARGET (lane m6, 2026-10-08; its own CLAUDE.md): one `<fixture>.c` per strided span-loop shape (possessive with/without `it_`, greedy ...
- **run_deleg_sites.sh** — C10's static half (`make test-memfn-deleg`, in TEST_SECTIONS): DELEG_SITES (`src/gen/memfn_sites.def`) against D91's budgets (this file's ...
### The row manifest, signatures and floors (lane n4, [MEMFN-ROWCON] N4)
- **rows.tsv** — THE KIT'S ROW MANIFEST (row_contracts.md rev 4.1 §4), HAND-maintained: one line per row of the kit's selection tables (13 at N4: the composer's 9 arms, ...
- **row_floors.tsv** — per-row CHOSEN floors: `pcrec_floor` over the full N2 census (`-` for a non-`pcrec` row), `g2_floor` over G2's quick tier.
- **rows_check.py**, **run_rows.sh** — `make test-memfn-rows` (in TEST_SECTIONS; about 1.5 s).
- **mk_mftrace_lib.sh** — builds `build/libpcrec_mftrace.a` (make rule of the same name): build/libpcrec.a with its kit members swapped for `-DMF_TRACE` builds, the ...
- `arm_fixtures.c --only FIXTURE` (N4) renders one fixture alone, so a traced run's rows are that fixture's.
- **run_n2_sample.sh**, **n2_sample_patterns.txt** — [MEMFN-ROWCON] N2's zero rules on a SAMPLE (lane m7fix, 2026-10-08; opt-in, no make target; mech arm `n2sample`).
### The finder table's B1 checks (lane fdb1, [MEMFN] R17-b′ B1)
- **run_finder.sh**, **finder_check.py** — `make test-memfn-finder` (in TEST_SECTIONS, CI shard 3; mech arm `memfnfinder`; seconds).
- **proven_check.c** — R-25 (lane memfn-r25): the form class's proven sets honour the row's declared `tests`.
### The per-offset proof and the context spans (lane r26z1, [MEMFN] R-26 Z1)
- **run_proof.sh**, **proof_check.c**, **proof_run.c**, **proof_meta.h** — R-26.1-R-26.5's checks (MF_SITE_ABI 18), part `proof` of `make test-memfn-finder` ... Since D172 S2 commit 1 (lane wsc1) proof_run repeats every call with the subject at a guard page after n, one before 0, and between SENTINEL pads (review S2's read-limit layouts); plant `S1408` (an over-read past n; wsc1's `WSC1-R1`, renamed by wsc2) is their witness. Since D172 S2 commit 6 (lane wsc6) the prefix facts, context spans, `absent`/`consumable`, `read_floor` and `consumer` are gone from the site, and their refusals, generated context items and SATISFIES cells with them; family A gains the window site's renderer-interface refusals (plant `S1419`); the oracle's floor is the FAILS cell below the subject; plants S1222/S1223/S1226 retired with their code, and S1255/S1256 were declared EQUIVALENT until D172 S3 retired RPT, kit_report_exact and mf_preview (lane s3): their plants, ZK6/ZK7, S1251-S1254, family D's preview checks and family C's preview renders went with them, and a REPORT site stated in terms is now REFUSED on every art (family A, C, D).
### D172 S2 commit 4's lever check (lane wsc4)
- **run_wreply.sh** — the window family's REPLY check (D172 S2; wsc4, inverted at commit 5, reduced at commit 6 when the planner's pick and the inverse harness lever were deleted): every witness stamps its NEXT row at the default flags and compiles at five flag sets (K35 floors on cases and keys); REACH through a perturbed tree copy (RESEED unstated: no offset-set row, at least five witnesses moved; R stated under `-fno-run-prefilter`: the RE-SEED refusal fires); `--plants` S1413-S1414 each red (S1412 retired with the pick). Opt-in, no make target; ~10 s plus a tree build; takes the box lock.
### The guarded-bytes check (lane rq3, [MEMFN] RQ-3, D155 addendum 2)
- **run_simd_guarded.sh**, **simd_guarded_check.py**, **simd_bounds.tsv** — `make test-memfn-guarded` (in TEST_SECTIONS; mech arm `simdguarded`).
### The SIMD floor rule, C9-x86 (lane r13, [MEMFN] R-13, R4e' batch 1)
- **run_simd_floor.sh**, **simd_floor_check.py**, **simd_levels.c** — `make test-memfn-simdfloor` (in TEST_SECTIONS; mech arm `simdfloor`).
- **simd_bounds.tsv** gains each SIMD row's measured bound (`vrun-w16`, `vrun-w32`); a MEMFN_FORMS token `FORM@L1+L2` is bounded by the sum of its rows `FORM-Lk` ...
- **libc_census.py** (C11): its SIMD-on half is the MOVERS half since R-13: an ON compile equals the default exactly where its `MEMFN_FORMS` reads `none` (`MOVERS_FLOOR`, ...
- **simd_accept.tsv** — THE SIMD ACCEPTANCE RECORD (integration.md §R4.9.6): one line per SIMD row x level x official CPU class (zen1, zen4), every line CANDIDATE at ...
- **run_pres_picks.sh**, **pres_pick_witnesses.tsv** — KW-8's named witnesses (R17-b′ B3a, lane b3a): a `-DPCREC_CAND_TRACE` pcrec compiles each line (pick, nontrivial, ...
- **run_pr11.sh**, **pr11_front.py**, **pr11_witnesses.tsv** — the PR-11 control (R17-b′ B3a): over count-collapsed VM hybrids (`RX_VM_PREFILTER_LANG "count-collapsed"`), ...
### The position ranking (lane rq2, [MEMFN] RQ-2, D157)
- **run_rank.sh**, **rank_check.py** — (R17-a, lane r17a: the same probe build also carries N4's door assertion, `find_door` in src/gen/emit_dfa.c: where a defined FIND's ... SINCE D172 S2 COMMIT 6 (lane wsc6, the kit manager's R1) THE CLAIM IS INVERTED: pcrec hands the kit NO ranking (the ranking and `plan_hint` are the kit's renderer interface, written by the window family's translation), so every predicate of every PRE/OFS site carries rank_n 0 and names no RUN term; pcrec's ranking (`ofs_pred_rank`, `pcrec_find_run_rank`) and its rows S731-S737 retired, and S1420 (a ranking stated on a pre-check part) is the claim's failing direction. N4's door stays.

## Maintaining it

- **A new search form in an emitter:** add a row, or name the function on
  its site's existing row, and raise the floor if you added a row.
- **A respelled form the vocabulary no longer sees:** rule 4 says so. Teach
  `search_vocab.tsv` the new shape; never delete the row to get green.
  Worked example (lane advtri, 2026-10-08, abi 67): [MEMFN] R4h's layout
  normalization respelled the five ADVANCE loops in the kit's layout
  (parenthesised `more` and member, braced body, step on its own line), and
  `walk-stmt`/`walk-open` stopped seeing them (4 rule-4 FAILs, 3 C12 STALE
  ceilings). Both regexes were widened to the new shape, not the rows or
  ceilings touched: C12 reads the same 12 forms in the same ceilings.
- **A migration step's REPLACE commit:** flip its rows to `delegated`.
  From then on, rule 3 holds pcrec to spelling none of them.
- `c4_populations/` — C4's COMMITTED compiler populations (`gcc -dM -E` dumps
  per ISA flag set, one directory per compiler/target/box). arch_blind_check.py's
  `population_controls()` plants classes 1-2 from every one, on every run, so
  the Mac checks ubuntubudu's gcc x86 vocabulary (R4c, 2026-10-07). An empty
  dump fails its population, with a scratch control on every run (R4c′).
  Own CLAUDE.md.

- Also (one-line entries for these are in the history file): `c10_onebyte.tsv`, `prov_check.c`, `run_arm_reach.sh`, `run_libc_census.sh`, `run_presence.sh`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__memfn.md`.
