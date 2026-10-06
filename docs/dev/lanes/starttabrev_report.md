# Lane `starttabrev` — report

**Lane:** `starttabrev`, 2026-10-06, branch `lane/starttabrev` off main
`4743ebb5`. DESIGN ONLY: nothing under `src/`, `cli/`, `lib/` or `tests/`
changed; no `make` was run. Probes used the main tree's `build/pcrec` (abi 64,
built from `74379fe0`; `git log 74379fe0..4743ebb5 -- src cli lib` is empty).

**Charter:** revise `docs/design/start_table.md` to revision 2 per the light D6
panel (`docs/dev/reviews/2026-10-06-r-starttable-panel.md`, every finding
ACCEPTED), with seven must-haves: a DERIVED inventory; routes by the
prefilter's engine; typed handoffs + Frank's re-entry question + M5; D-4; the
proof per checks M1-M4; every minor; Q1-Q9 restated.

## What was delivered

- `docs/design/start_table.md` revision 2, with a §R disposition table mapping
  every panel finding (sound M1-M6, m1-m6, n1-n6; checks M1-M4, m1-m8, notes;
  Frank's re-entry question) to its resolution and section. Changes are marked
  `[r2 <id>]` inline.
- `docs/design/start_table/` instruments (own CLAUDE.md, updated):
  - `call_graph.py` → `call_graph.txt`: the derived start family (99 members +
    15 seeds, 148 decision sites), from the emitters to every landmark read;
  - `inventory.tsv` + `inventory_check.py`: one disposition per member; the
    check passes 114/114 and fails on any undispositioned or stale member;
  - `deny_census.py` → `deny_census.tsv`, `deny_transitions.tsv`,
    `deny_hidden.tsv`, `deny_movers.tsv`, `row_census.tsv`, `slowest.tsv`: the
    deny-delta census (13 start-family flags × 4 arms × 3,595 patterns), with
    hidden-mover fingerprints and the row census's deny arms;
  - `row_census.py` revised: route-keyed joint stamps (seven disjoint route
    classes; the double count fixed), bound literals read off the text, H1 read
    two ways, `--deny` arms;
  - `refactor_edit_set.tsv` + `sabotage_anchors.py` (rewritten) →
    `sabotage_anchors.tsv`: the re-aim list derived from the plan's edit set and
    the call graph (14 re-aim / 81 re-run / 95 family rows; 0 count mismatches
    over 463 rows / 480 sites); the hand-written `sabotage_anchors.family` is
    deleted;
  - `note_tables.py`: prints the note's census tables from the committed TSVs.
- `docs/design/CLAUDE.md`: the `start_table.md` entry gains a revision-2 block.

## Findings the revision produced (beyond the panel's)

1. **The per-commit anchor gate the checks critic asked for already exists.**
   `scripts/m6read_check_sab_anchors.py` enforces "every `SAB_BEFORE`/
   `SAB_BEFORE2` occurs exactly `SAB_COUNT`/`SAB_COUNT2` times", and
   `make test-codegen` runs it as [SABANCHOR]. The note now names it as the
   per-commit gate; what was missing was the DERIVED re-aim list, now from the
   edit set.
2. **The derived re-aim count is 14, not 9-10.** Beyond the critics' S169,
   S222, S263, S371, the M5 fix (C5b) re-aims S269, S274, S276 (P2's arms) and
   S492 (N7's anchoring conjunct): fixing M5 moves anchors the panel's count
   could not have seen.
3. **`-fno-req-byte` moves `RX_FINDINGS` on artifacts it cannot act on**
   (probed: `[ab]*c?`, auto and `--engine=vm`: `RX_FINDINGS
   "byte-rate=default:…"` → `""`). The deny removes the byte-rate prior's ASK,
   and the ask is what the stamp records. This is the side-effect channel §1.3
   names ("no eager plan"), observed on the corpus: 1,179 of the 3,222 vm/byte movers
   of `-fno-req-byte` move ONLY that stamp. It is correct behaviour today (the stamp reports
   whether the prior was consulted), and it is why the refactor's ask-SET
   invariant is a real obligation, not a formality.
4. **The call graph found the route dispatch** (`pcrec_emit_dfa_engine` on
   `job->engine`) and the `fit.chosen == ENGM_DFA` entry gate as decision
   sites — together the mechanism by which an ATTEMPT hybrid's inlined body is
   an ATTEMPT customer (sound M1).
5. **Revision 1's 184 `HYBRID: "none"` were all ATTEMPT (170) or empty (14)
   hybrids**; an ENG_UNANCH hybrid prefilter never stamps `none`.
6. **D-4 also fires on `\d\dzq` under utf8** (run-pinned in byte, offset-set in
   utf8), beyond the panel's `abc$` pair.

## Validation

- `python3 -I docs/design/start_table/inventory_check.py
  docs/design/start_table/call_graph.txt docs/design/start_table/inventory.tsv`
  → `family+seeds 114; dispositions 114`, exit 0.
- `python3 -I docs/design/start_table/sabotage_anchors.py . call_graph.txt
  refactor_edit_set.tsv` → `SITES 480 ROWS 462 FAMILY_ROWS 95 RE_AIM_ROWS 14
  RE_RUN_ROWS 81 COUNT_MISMATCH 0` (462 distinct row ids: one row file has no
  site in a readable form for this parser — it is counted by
  `scripts/m6read_check_sab_anchors.py`, which reads 463 / 480 and reports
  "all anchors resolve").
- `deny_census.py` over 3,595 patterns, 201,320 compiles, ~23 min at 9 jobs:
  52 (flag, arm) cells, 0 refusal moves, every hidden mover fingerprinted
  into four named classes (P4's body, fact stamps, the prior's ask, the
  collapse rung's ENGINE_SEL); table in start_table.md §3.4. The auto/byte column
  reproduces the checks critic's measured table exactly (513, 136, 14, 163,
  183, 403, 337, 288, 48).
- Probes re-run on this build: sound M1's five patterns, D-4's six cells,
  D-2b's capturing twin.

## Owed / not done

- Nothing is built; the refactor's C0 floors are re-measured at C0 (the note
  says so; the census numbers here seed them).
- The short re-check (§6 Q9) by the two critics.
- Q1 is pending Frank (manager recommends "fold first, gated on the revised
  note clearing a short re-check"; the note agrees).

## Resume notes

A follow-up round starts from §R of the note and from `start_table/CLAUDE.md`.
Every number in the note re-derives from a committed TSV via
`start_table/note_tables.py` or the scripts' own summaries; the re-aim list is
`sabotage_anchors.tsv`'s RE-AIM rows.
