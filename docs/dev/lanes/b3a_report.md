# Lane b3a — R17-b′ step B3a, the ST3 shadow (2026-10-17, opus)

Charter: `docs/design/memfn/r17b_prime.md` rev 3 §3.1 row B3a. Branch `lane/b3a`, cut from main @ 184fc9110
(E-1 + R-23 + R-24 landed). PRESENCE is STATED on the merged site and PRES stays UNROUTED. KW-8's kit PORTS of
pcrec's five priced picks run in the TRACE build beside pcrec's own picks. **Zero artifact movers vs 184fc9110.**
`MF_SITE_ABI` 15 -> 16, with no `MF_VOCAB` move and no pcrec abi event.

## 1. What changed

### Kit (memfn/)

- **`memfn/include/memfn.h`** — `MF_SITE_ABI` 16. Each item below is appended last.
  - New enum `mf_span_class`: `MF_SPAN_UNSTATED = 0`, `BOUNDED`, `CONTEXT`, `PRESENCE`.
  - New constant `MF_ORDER_UNKNOWN` (0xFFFF).
  - `mf_pred` gains `span_class`, `omin` and `member_order`.
  - `mf_site` gains:
    - `head_max`, the handoff's K;
    - `npspan`;
    - `pspans`, the stated presence spans.
  - `mf_class` gains `npres` (`MF_CLASS_V` 3). `MF_MAX_PRES` is 257: 256 members plus 1 run, derived rather than tuned.
  - KW-8's port entry `mf_pres_ports(art, site, proof, displaced, out)` over the types `mf_pres_proof` and
    `mf_pres_picks`. `MF_PRES_WINDOW` is 8, pinned to pcrec's `PCREC_MAX_REQ_RUN_EMIT` by a `_Static_assert` on
    pcrec's side.
- **`memfn/src/compose.c`** — `kit_presence_check` is called from `site_check`. `mf_define` and `mf_ask` refuse a
  malformed presence statement:
  - the rendered `preds`/`pred` must carry no class, omin or order;
  - `pspans` and `head_max` are allowed on ALL_PRESENT sites only, and `head_max` only with ASSIGN;
  - every span must have class PRESENCE, one term at offset 0, no window, omin ≥ 0, and no plan hint, plan_pos,
    fn_ref or rank;
  - a RUN span must have `member_order` 0 and `run_len` ≥ 2, and a site may carry at most one;
  - a SET span must have exactly one member and a nonzero `member_order` (≤ 256 or UNKNOWN).
- **`memfn/src/presence.c`** (new, 0BSD, PROVENANCE row) — `mf_pres_ports`. It re-derives the five picks from the
  STATED spans, from `head_max`, and from the analysis object's `byte-rate` payload. Under PRIOR_NONE it uses
  cardinality masses.
  - **Set pick:** the lowest mass wins. A tie goes to the higher `member_order`, then the larger byte.
  - **Run scan index:** the lowest mass wins. A tie goes to the rightmost.
  - **Window start:** over windows of `MF_PRES_WINDOW`. A tie goes to the leftmost.
  - **Set-leads:** strictly rarer only.
  - **G1 (byte dominated):** identity, run-verified, and density "no commoner", the last on one-byte only.
  - **Landmark admission:** `h==0 || (K*h<1e6 && (1e6-K*h)*m > 1e6*h)`, under ASSIGN only.
- No finder row reads `pspans`. The PRES slot rows (P0/P2/P3/P4/P9) are unchanged and unrouted.

### pcrec builder lines — FLAGGED FOR MAIN'S REVIEW (they are in this lane's own commits)

- **`src/gen/emit_dfa.c` `req_pres_spans`**, called from `req_site_define`, states:
  - one one-byte span per necessary-set member, in descending byte order (PR-5, unpicked);
  - then the whole run as one span with its mask;
  - `span_class` PRESENCE and `omin` 0 (PR-6);
  - `member_order`, the member's rightmost order when the fact states it, else `MF_ORDER_UNKNOWN` (PR-7);
  - `need` REQUIRED only when no DFA scan is in front (VM_ATTEMPT), else OPTIONAL.

  It also sets `s->head_max = pcrec_fact_req_landmark_maxoff(cx)` when the site hands its landmark on, else 0.
- **`req_pick_shadow`** (under `PCREC_CAND_TRACE` only, placed after `cand_select_quiet`) runs quiet:
  - it builds the proof (`dfa_cand_scan` PRESENCE) and the displaced set (`cand_select(NEXT, …|PCREC_NO_REQ_HANDOFF)`);
  - it calls `mf_pres_ports`;
  - it prints `MFPICKSITE` and one `MFPICK pick agree nontrivial differs pcrec kit kind` record per pick, beside
    pcrec's own `req_set_pick`, `pcrec_fact_req_run`, `req_set_leads_applies`, `req_byte_dominated_by` and
    `req_landmark_admits`;
  - withheld presence (Q-WR-4) records `withheld-one-attempt` / `withheld-whole` and states no spans;
  - `PCREC_PICK_PLANT=<pick>` flips one comparison (SN-6).
- **`src/gen/memfn_sites.c` `pres_record`** (trace build, `PCREC_MF_ROUTE_TRACE`) prints `MFPRES`: the stated
  spans per defined site. The proposed C10 fixtures read it.
- **`src/facts/facts.{c,h}`** — `pcrec_fact_req_set_stated` and `pcrec_fact_req_whole_run_stated` are NON-PASS
  reads (`pf_ask(…, false)`). Stating presence never sets `used`, so the `--emit-facts` stream does not move
  (Q-WR-12).
- **`tests/codegen/run_cand_oracle.sh`** (main's file) also runs `tests/memfn/run_pres_picks.sh` and folds its
  counts in.
- **`tests/memfn/run_finder.sh`** gains `part pr11`.

### Deviations from the note's letter (judgement calls, for review)

1. **`pspans` is a separate array on the site, not new entries in `preds[]`.** `preds[]` is what the PRES slot and
   the precheck arm render today. Putting the spans there would move bytes, or would need every reader of
   `preds[]` to skip them. The separate array keeps the zero-mover bar by construction.
2. **The PRES slot shadow still runs over `preds`, not `pspans`.** B3a states presence. Moving the slot's input is
   the routing step, which belongs to B3b.
3. **`member_order` follows the fact's rightmost order** (the set pick's tie order) because that is the order
   pcrec's pick reads. A member the fact does not order is UNKNOWN, never a presumed value.
4. **The comparator lives pcrec-side** (`req_pick_shadow`). pcrec owns the expectations, and the kit sees only
   facts (D157).

## 2. Validation (light; `taskset -c 12-15`, `-j4`)

VALIDATION_TABLE

## 3. KW-8 census (`docs/design/memfn/r17b_prime/b3a/pick_census.py`)

Populations:

- **corpus:** emit_sweep's own enumeration;
- **bench:** pcrec-bench `bench/*/patterns/*.rx`, read-only;
- **rwquest:** `questions.tsv` with its flags.

Each population runs over three arms: `-`, `-e utf8` and `--engine=vm`. A record is NON-TRIVIAL when the pick
had a real choice: more than one candidate, a tie broken, or a strict comparison decided. The floors
(`pick_floors.tsv`, [rev3 D10]) are floor(0.9 × the measured non-trivial agreeing records).

| pop | pick | records agreed | non-trivial agreed | floor |
|---|---|---|---|---|
| corpus | set | 6477 / 6477 | 2465 | 2218 |
| corpus | scan | 1394 / 1394 | 1394 | 1254 |
| corpus | window | 1394 / 1394 | 67 | 60 |
| corpus | leads | 1342 / 1342 | 1342 | 1207 |
| corpus | dominated | 6477 / 6477 | 3260 | 2934 |
| corpus | landmark | 508 / 508 | 508 | 457 |
| bench | set | 539 / 539 | 377 | 339 |
| bench | scan | 316 / 316 | 316 | 284 |
| bench | window | 316 / 316 | 18 | 16 |
| bench | leads | 304 / 304 | 304 | 273 |
| bench | dominated | 539 / 539 | 271 | 243 |
| bench | landmark | 118 / 118 | 118 | 106 |
| rwquest | set | 408 / 408 | 309 | 278 |
| rwquest | scan | 282 / 282 | 282 | 253 |
| rwquest | window | 282 / 282 | 36 | 32 |
| rwquest | leads | 270 / 270 | 270 | 243 |
| rwquest | dominated | 408 / 408 | 220 | 198 |
| rwquest | landmark | 89 / 89 | 89 | 80 |

There were 0 disagreements and 0 `port-refused` records.

Withheld shadows, which state no spans (Q-WR-4):

- corpus: one-attempt 783, whole 132;
- bench: one-attempt 45.

The window pick's non-trivial population is small because a real window tie needs a run longer than 8. The
named witnesses carry a real tie (`-e utf8 (?i:x)abcdefg(?i:y)`).

The census was re-run at the tip in the chain: PICK_CENSUS_TIP. Transcript: `b3a/out/pick_census_full.txt`.
Named witnesses: `tests/memfn/pres_pick_witnesses.tsv` (17 lines, 40 checks, one plant per non-trivial line).

## 4. PR-11 control (`tests/memfn/run_pr11.sh`, `b3a/pr11_census.py`)

The control asks one thing of a COUNT-COLLAPSED VM hybrid (`RX_VM_PREFILTER_LANG "count-collapsed"`, nfa.c
`rmin = rmin ? 1 : 0`). Its static `_prefilter` must refuse every subject derived from a matching subject by:

- deleting a stated necessary-set byte (all occurrences), or
- breaking every occurrence of the stated run.

It must also still pass the matching subject.

- **Light check** (in `run_finder.sh`): 4 witnesses plus a control, 5/0 in 2 s.
- **Census** over the three populations × {`-`, `-e utf8`}, which found 20 collapsed artifacts:

| pop | arm | ok | derived subjects | no-claims | unchecked (no subject) |
|---|---|---|---|---|---|
| corpus | - | 2 | 208 | 1 | 0 |
| corpus | -e utf8 | 0 | 0 | 2 | 0 |
| bench | - | 5 | 48 | 0 | 1 |
| bench | -e utf8 | 5 | 48 | 0 | 1 |
| rwquest | - | 1 | 112 | 0 | 0 |
| rwquest | -e utf8 | 1 | 40 | 0 | 1 |

That makes 14 artifacts checked with 0 enforcement failures. Matching subjects for the bench and rwquest patterns
are harvested by running the artifact's own `_search` over the population's texts (64 bytes of context).

- A **no-claims** artifact states no req_set and no req_whole_run, so it has nothing to enforce.
- An **unchecked** artifact found no matching subject in its texts.

The tip re-run is PR11_TIP (`b3a/out/pr11_census.txt`).

**The planted collapse drops rmin (S1100, nfa.c): DETECTED.** finder reported 3 failures.

## 5. Proposed main-side diffs (`docs/design/memfn/r17b_prime/b3a/proposed/`)

Apply them in this order. Each is `git apply --check` clean, in sequence, on this lane's tip.

1. **`deleg_entry.diff`** (charter item a, Q-R17P-18) — `src/gen/memfn_sites.def` gains an `entry` column, a
   closed `DelegEntry` with an UNSTATED zero:
   - PF and MLINE get `DELEG_ENTRY_PRE`: their sites take the PRE composite's verdict as their ENTRY use;
   - PRE gets `DELEG_ENTRY_SELF`: it stays the row of the PRESENCE-ONLY site (the no-DFA VM entry, the hybrid's
     `_search_run`, and `attempt_entry` without MLINE);
   - every other row gets `NONE`.

   Its consumers change with it:
   - `memfn_sites.h` (the enum and `DelegRow.entry`);
   - `memfn_sites.c` (the X-macro);
   - `tests/memfn/site_census.py` (the stub macro);
   - `tests/memfn/run_deleg_sites.sh`: its probe macro, a re-aimed budget plant, and **check 6** (every row
     states its entry; PRE only on FIND rows, and on at least one of them; SELF exactly on the ALL_PRESENT row),
     with a planted control.

   The ENTRY use's own vocabulary (`MF_USE_ENTRY`) is an `MF_VOCAB` event left to B3b. Until then the column is a
   table fact that only C10 reads, and every instance renders as it does today.
2. **`c17_use_points.diff`** (item b) — `tests/memfn/site_manifest.tsv`: PRE's use points
   (`pcrec_emit_req_byte_check`, `emit_req_reentry_use`) move under PF's emitters, and
   `pcrec_emit_req_byte_check` also moves under MLINE's. PRE keeps `req_site_define`. The rationale is recorded in
   each row's note. C17 passed 13/0 on the edited manifest.
3. **`c10_presence.diff`** (item c) — the new `tests/memfn/c10_presence.tsv` holds 5 fixtures: one per PRE kind
   (DFA_SCAN, HYB_PF, VM_ATTEMPT, DFA_ATTEMPT) plus a handoff with `head_max` 4. Expected values are written from
   the pattern, not from a record. **Check 7** reads the MFPRES records and adds a kind floor and a planted
   need-swap control.

Applied together in the working tree, C10 gave 14/0 and C17 gave 13/0. The chain's apply-build-test-sweep result
is in §2. The pcrec side of the C10 fixtures (`pres_record`) is already in this lane's commits.

## 6. Sabotage (ids S1093-S1101, allocated by the kit manager)

Each plant was run SOLO in a `git archive HEAD` copy by `b3a/sabotage/run_skb3a.sh`:

| id | plant | suite | result |
|---|---|---|---|
| S1093 | the comparator always agrees (`pc == kit` -> 1) | candoracle | DETECTED (16 fail) |
| S1094 | port: set tie order swapped | candoracle | DETECTED (5) |
| S1095 | port: scan tie goes leftmost | candoracle | DETECTED (6) |
| S1096 | port: window tie goes rightmost | candoracle | DETECTED (1) |
| S1097 | port: set-leads not strict | candoracle | DETECTED (11) |
| S1098 | port: G1 identity dropped | candoracle | DETECTED (3) |
| S1099 | port: landmark ignores K | candoracle | DETECTED (1) |
| S1100 | nfa.c collapse drops rmin (PR-11) | memfnfinder | DETECTED (3) |
| S1101 | pcrec states its pspans with class UNSTATED | candoracle | DETECTED (46) |

SN-6's per-pick planted disagreement is also built into the witness runner: `PCREC_PICK_PLANT` runs on every
non-trivial witness line.

## 7. OWED heavy runs (manager's slot; none run here)

Each run below is launched from the worktree root:

```
# full make test
scripts/perfrun -- make test > build/land/make_test.log 2>&1
#   verdict: grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'

# G2 full
make test-memfn-g2-full > build/land/g2_full.log 2>&1

# mech
#   - the derived memfn rows: anchors in compose.c, emit_dfa.c and memfn_sites.c moved
#     (SABANCHOR in test-codegen passed);
#   - the S1093..9 rows, once main allocates their ids:
make test-mech > build/land/mech.log 2>&1

# N2 census, per its runner
```

## 8. Charter vs committed

CHECKLIST

Tip: TIPSHA
