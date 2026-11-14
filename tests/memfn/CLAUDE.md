# tests/memfn — pcrec's side of the memfn kit's checks ([MEMFN])

pcrec's checks on the search-code kit (`memfn/`, D146/D147;
`docs/design/memfn/integration.md`). The kit's OWN tests (G2) live under
`memfn/tests/`, not here. Born at R4a (2026-10-05) with C17.

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
- **run_link_checks.sh** — [MEMFN] R4a: `make test-memfn-link`, a `make test` section; C15, C16 and R-28's frame check (no kit function over a 4 KB stack frame, `-O2 -fstack-usage`, with a planted-fat-frame witness); the census probe's compile (3.0b).
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
- **rows_check.py**, **run_rows.sh** — `make test-memfn-rows` (in TEST_SECTIONS; ~3 s; §P plants rows B, C, M).
- **row_map.tsv**, **row_map.py** — the DECLARED row map (1e): rows moved across tables, and its ONE parser; rows_check M (pinned in run_rows.sh) and `reach_equal.py --map` (held to BASE's trace both ways).
- **renderer_rows.tsv** — the declared (frame, method row, renderer row) triples of `MFTRACE FDROUTE` (3.0a); rows_check R holds every traced triple to it.
- **stream_support.tsv** — the support pin (3.0a §2.5.2); rows_check S, vs `arm_fixtures --streams`.
- **decider_census.tsv**, **decider_census.py** — THE DECIDER CENSUS (span_pick.md rev 5.2 §The tables; unit 1a, lane sp1a): the declared map of every kit decider to its question table or named exception, its backstop grep and plants, and (K38-1, section D) the exact callers of `kit_run_member`/`kit_run_decide`; run by `make test-memfn-rows`. A stage-1 unit that moves a decider edits its row.
- **reach_equal.py** — REACH EQUALITY between two MF_TRACE builds, per pattern and arm; gone rows DERIVED, equal to `--gone`; failing sets compared; `--map` compares through row_map.tsv; `--limit`/`--no-corpus` are smoke runs (trailer LIMITED, exit 3) (span_pick stage 1's witness; opt-in, no make target, heavy).
- **mk_mftrace_lib.sh** — builds `build/libpcrec_mftrace.a` (make rule of the same name): build/libpcrec.a with its kit members swapped for `-DMF_TRACE` builds, the ...
- `occurrence_oracle.py` (+ `_selftest.py`) — K38-2a occurrence oracle (D27-blind, sheet §3.3; k382o_report.md).
- `arm_fixtures.c --only FIXTURE` (N4) renders one fixture alone, so a traced run's rows are that fixture's.
- `arm_fixtures.c --site-text ID [CLS]` / `--site-parts ID [CLS]` / `--hash-text FILE|-` / `--facts ID [CLS]` (span_cards S2c, includes kit.h): an instance's hashed text (whole or FILE/BODY), any text's hash, the slot's facts; `--hash`: `FORMCLS` lines, per-instance R-MS3 fixtures (r9).
- `arm_fixtures.c --purity` / `--purity-control` (span_pick 1d): THE PURITY HARNESS (11 sites; NONE and framed replies, fresh art vs interleaved defines, whole-reply memcmp; the sticky-err fence; 3.0b's fixtures: NOTES.md "Purity harness"). run_finder.sh floors it EXACTLY, runs it plain and on the MF_TRACE driver `fxt` (E-func/E-generic define counts EXACT), plants `nsites`-keyed A-mass and M-parked rows (RED, control moved), and runs **run_purity_reach.sh** over **purity_rows.tsv**: each window.c table row dropped must move a reply or be declared unreached.
- **run_n2_sample.sh**, **n2_sample_patterns.txt** — [MEMFN-ROWCON] N2's zero rules on a SAMPLE (lane m7fix, 2026-10-08; opt-in, no make target; mech arm `n2sample`).
### The finder table's B1 checks (lane fdb1, [MEMFN] R17-b′ B1)
- **run_finder.sh**, **finder_check.py** — `make test-memfn-finder` (in TEST_SECTIONS, CI shard 3; mech arm `memfnfinder`; seconds). Check C reads every `memfn/data/cards/*.tsv` by listing (floor 3), holds each card row's shape and the `kit:form.`-dep guard (named deps resolve; count EXACT 17); check B: an id's hash = its instances' fold (S2933).
- **proven_check.c** — R-25 (lane memfn-r25): the form class's proven sets honour the row's declared `tests`.
- **mass_check.c** (1b/1c goldens: `kit_mass`, `kit_run_set`, `kit_run_member`, the normal-form refusal; floor 41), **run_decide_check.c** (K38-1: the run decision's readers, the verify-YES stretch included; floor 13): parts of test-memfn-finder.
### The per-offset proof and the context spans (lane r26z1, [MEMFN] R-26 Z1)
- **run_proof.sh**, **proof_check.c**, **proof_run.c**, **proof_meta.h** — R-26.1-R-26.5's checks (MF_SITE_ABI 18), part `proof` of `make test-memfn-finder` ... Since D172 S2 commit 1 (lane wsc1) proof_run repeats every call with the subject at a guard page after n, one before 0, and between SENTINEL pads (review S2's read-limit layouts); plant `S1408` (an over-read past n; wsc1's `WSC1-R1`, renamed by wsc2) is their witness. Later history of this check (D172 S2 commit 6, S3): tests/memfn/NOTES.md.
### D172 S2 commit 4's lever check (lane wsc4)
- **run_wreply.sh** — the window family's REPLY check (D172 S2; wsc4-wsc6). Opt-in, no make target; ~10 s plus a tree build; takes the box lock. Full description: NOTES.md "run_wreply.sh".
### The guarded-bytes check (RQ-3, D155 add. 2)
- **run_simd_guarded.sh**, **simd_guarded_check.py**, **simd_bounds.tsv** — `make test-memfn-guarded` (in TEST_SECTIONS; mech arm `simdguarded`).
### The SIMD floor rule, C9-x86 (R-13)
- **run_simd_floor.sh**, **simd_floor_check.py**, **simd_levels.c**, **target_text.py** (C11 too; NOTES.md) — `make test-memfn-simdfloor` (in TEST_SECTIONS; mech arm `simdfloor`).
- **simd_bounds.tsv** gains each SIMD row's measured bound (`vrun-w16`, `vrun-w32`); a MEMFN_FORMS token `FORM@L1+L2` is bounded by the sum of its rows `FORM-Lk` ...
- **libc_census.py** (C11): its SIMD-on half is the MOVERS half since R-13: an ON compile equals the default exactly where its `MEMFN_FORMS` reads `none` (`MOVERS_FLOOR`, ...
- **simd_accept.tsv** — THE SIMD ACCEPTANCE RECORD (integration.md §R4.9.6): one line per SIMD row x level x official CPU class (zen1, zen4), every line CANDIDATE at ...
- **run_targets.sh**, **targets_check.c** — `make test-memfn-targets`; NOTES.md "targets" (+U3 part 4).
- **run_d27_region.sh**, **d27_region/** — `make test-memfn-d27region`: the D27 spec-first suite of the CPU-target text, plus its control. Own CLAUDE.md.
- **run_d27_frame.sh**, **d27_frame/** — `make test-memfn-d27frame` (`-full` opt-in): D27 suite of 3.0b's framed ask, its control and empty run. Own CLAUDE.md.
- **run_pres_picks.sh**, **pres_pick_witnesses.tsv** — KW-8's named witnesses (R17-b′ B3a, lane b3a): a `-DPCREC_CAND_TRACE` pcrec compiles each line (pick, nontrivial, ...
- **run_pr11.sh**, **pr11_front.py**, **pr11_witnesses.tsv** — the PR-11 control (R17-b′ B3a): over count-collapsed VM hybrids (`RX_VM_PREFILTER_LANG "count-collapsed"`), ...
### The position ranking (lane rq2, [MEMFN] RQ-2, D157)
- **run_rank.sh**, **rank_check.py** — the ranking claim, INVERTED since D172 S2 commit 6: pcrec hands the kit no ranking (every PRE/OFS predicate has rank_n 0); S1420 is the failing direction; N4's door (`find_door`) stays. History: NOTES.md.

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

- **prov_check.c** — BUILD-ONLY (run_finder.sh compiles it `-fsyntax-only -Werror`, never links or runs it): a static assertion of `mf_akind.digest`'s offset. Reduced at span_pick 1g (MF_SITE_ABI 22) when `mf_prov` and pcrec's stanza mapping left the seam; finder_check L (the seam allowlist, rate-site digest loop with reach control, no-`digest` scan) is the digest check.
- Also (one-line entries for these are in the history file): `c10_onebyte.tsv`, `run_arm_reach.sh`, `run_libc_census.sh`, `run_presence.sh`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__memfn.md`.
