# mscomp2 — [COMPOUND] design note revision 2 (2026-10-12, opus)

Lane `mscomp2`, branch `lane/mscomp2` from main `21641979` (abi 76). Design only: nothing
under `src/`, `cli/`, `lib/`, `tests/` or `docs/spec/` changed. Deliverable:
`docs/design/compound.md` revision 2 (renamed from `composite.md` by D163 addendum 2), with its
evidence in `docs/design/compound/twin/` (revision-2 instruments `twin2.py`, `ctrl2.c.in`,
`cost2.py`, `probes2.py` beside revision 1's, own CLAUDE.md). Inputs: the panel
`docs/dev/reviews/2026-10-12-r2-composite.md`, D163 with addenda 1 and 2, D88 addendum 1, plan
row [COMPOUND].

## Commits

- `fd81c292` rename: `git mv` the note and its evidence dir; cross-references
  (`match_split_pinonly.md`, plan.md's [ENG-TACTICS] row, the twin CLAUDE.md files). The
  historical review files and the merged `mscomp_report.md` keep the old word.
- `bf43bbfe` WIP: `twin2.py`, `ctrl2.c.in`, `cost2.py`.
- `4f9b5efd` revision 2 of the note, the twin2 results, the plants, the size and one-TU
  generators.
- (this commit) `docs/design/CLAUDE.md` entries, flag-name fixes, this report.

## Measurements (light, no clock, Linux dev box, gcc 15.2, libpcre2 10.46, ≤ 4 workers)

- **Differential on the shipped config** (chk M3/M4, sem S2, arch N4):
  `results/split_differential2.tsv`. Q derived the build's way (never node + prune, not
  `(?!)`), F = P under the bound, one prologue, every option arm (byte; utf8 × {refuse, none,
  align} × {`-futf-check` off, on}), witness bytes asserted, panel witnesses verbatim. 177
  case-arms, 2,170,123 cells, 574,769 matches: **0 differences** compound vs today, 0 today vs
  libpcre2, 0 find-all. 6 cases declined with their reason. Q routes: `dfa/rev-end` 79,
  `dfa/unanchored` 53, never 20, `dfa/attempt` 2, VM 23.
- **Plants** (`results/plants.tsv`): Q from `from`, the utf check with Q's reach, no prologue:
  each goes red (9 / 6 / 22 case-arms); plant 2 on a DFA witness (`\A\s+|\s+\z`).
- **Counted loads, pin-only** (`results/split_loads2.tsv`): K106 128,040,002 → 3; floor / end /
  both matches today + 1-2 loads; wrapper with both matches 16,003 → 6; floor-only `a{0,4}\A`
  63,994 → 4; the final-newline two-seed walk 3.00× on `\s+$` and `\s*?$` (B3's).
- **Sizes and one-TU** (`results/sizes2.tsv`, `one_tu_probe2.txt`, generator `probes2.py`):
  trim 3.03×, wrapper 2.35×, floor-only 1.07×, concat-sqli 1.15× linked; static-without-omission
  fails `-Werror` with 27 errors.
- **`VALID_LB`**: P's reach is a parse-time fact (1 on `\A\s+|\s+\z` under any guard flags),
  Q's is 0.

## Disposition table (finding → where addressed)

| id | disposition | where |
|---|---|---|
| chk B1 | DONE: first build PIN-ONLY (A5: Q `rev-end` or never); S+F waits for a bench reading of concat-sqli on its own subjects; the match-density cost conjunct's shape sketched, designed at the trigger; matching pin-only cells counted | §B.4, §B.5, §B.7, §F B4/B5 |
| chk B2 | DONE: B3 = lane `revb3`, `revend_onepass.md`, not designed here; the post-B3 factor dependency stated; G3's bound for the shape is B3's | §B.5, §E.3, §F B3 |
| sem MF1 | DONE: one prologue, `-futf-check` with P's reach; plant 2 detects | §A.6, §E.2 |
| sem MF2 | DONE: floor-only compound keeps P's `-7`/`-9` (prologue); plant 3 detects | §A.6, §E.4 CMP-12 |
| sem MF3 | DONE: F = a BOUND on P's attempt (`PB_ONE_ATTEMPT`), no tree wrap; twin `^x\|a(?R)?b` 0 diffs | §B.1, §J-3 |
| sem MF4 | DONE: f = aligned `from`, `qf = next_pos(f)`; `(?>\Ga\|ab)c` 0 diffs on all six arms | §A.6 |
| sem S1 | DONE: called/referenced/condition groups never deleted; first build declines; DEFINE-style keep for B6 | §B.1, §E.4 CMP-14 |
| sem S2 | DONE: twin runs the derived Q, every option arm, the floor-only controller, a `(?R)` row | §E.2 |
| sem S3 | DONE: `\K` declines the cache or keys on the attempt start | §C |
| sem notes | DONE: verbs/callouts decline via a registry attempt-scope column; D158 "answer for answer" dropped, give-up returned at once; caller contract for the cache | §B.8, §A.9, §C |
| arch M1 | DONE: renamed "compound" everywhere; `cand_rows[]`'s LOCATE row "composite" keeps its name (stated once) | header |
| arch M2 | DONE: combinators `first-nonzero`, `min-start-then-finish`, `locate-then-finish`, `select-by-arg`, `dispatch` over the typed results; in-Job row vs part rule; D.2 reclassified as in-Job | §A.2, §D.2 |
| arch M3 | DONE: `CompPart` flags_set/clear, engine, bound, need; table-build self-check, no defaulted field | §A.1 |
| arch M4 | DONE: `drop-compound` row in `fit_rungs[]`, first among size rungs; choice is attempt-level state | §A.3, §A.8 |
| arch M5 | DONE (same as sem MF1/MF4) | §A.6 |
| arch M6 | DONE: keep = controller edges into the closure; the hybrid's `"static "` subsumed at B0 | §A.4 |
| arch S1 | DONE: pattern- vs machine-level classification; defined compound values via the generated-stamp rule | §A.7 |
| arch S2 | SUPERSEDED by D163 add. 2 item 2 (always on, no bit) | §A.11 |
| arch S3 | DONE: trace site key, `TABLE_ROOTS`, row-reach witnesses, declared reads; no `--list-axes` (no axis) | §A.10 |
| arch S4 | DONE: parts inherit `noclone`; `noinline` decided by the short-call cell | §A.5, §E.3 |
| arch S5 | DONE: admission reads through declared `CandRead` projections, trace-checked | §A.3 |
| arch S6 | DONE: deferred, trigger named (U6) | §H |
| arch S7 | DONE: `CompRow.state_words` reserved | §A.1, §C |
| arch N1 | DONE: `__` reserved; user prefix with `__` refused (population 0) — §G Q2 | §A.5, §G |
| arch N2 | DONE: F hits `dfamemo`; D45-margin row at B4 | §A.12 |
| arch N3 | DONE: hybrid trigger = a client needs a wider part interface | §A.13, §H U1 |
| arch N4 | DONE: align and `-futf-check` arms in the twin | §E.2 |
| arch §H | DONE: G4's expected set from the plain artifact's `nm -g` | §E.3 |
| chk M3 | DONE: shipped-config differential; per-ID Q `dfa` and matches > 0 required in G2 | §E.2, §E.3 |
| chk M4 | DONE: witness bytes from the pattern, asserted present | §E.2 |
| chk M5 | DONE: decline reasons recorded/asserted; CMP-1 etc. declared UNREACHED with their step; A2 via an independent walk | §E.4 |
| chk M6 | DONE: D94 recipe by macro/field NAME | §E.5 |
| chk M7 | DONE: G3's attempt clause dropped (loads only) | §E.3 |
| chk S8 | DONE: G3 bounds derived (excess ≤ calls; the 4k/k ratio test) | §E.3 |
| chk S9 | DONE: B0-B2 each get a positive control | §F |
| chk S10 | DONE: landing bar = every bench artifact (reach 0), 16 single-class floor rows + 2 concat-sqli named; "byte-identical" defined | §E.3 G6 |
| chk S11 | DONE: generators (`probes2.py`) and reproduction commands | twin CLAUDE.md |
| chk S12 | DONE: Q compiles under P's caps; a degraded Q declines (A4) | §B.4 |
| D163 add. 2 (1) | DONE: rename | header, everywhere |
| D163 add. 2 (2) | DONE: always on; the harness-only lever, its home, its fence, test-axes and bisect use | §A.11 |
| D163 add. 2 (3) | DONE: pin-only first, B3 first, DFA-only first, Q from `next_pos(aligned floor)`, captures on demand as a client | §B, §D.1 |

## Findings

1. **J-2: F must be a BOUND, not `_match`.** A DFA attempt route's `_match` is search-filter;
   as F it left K106 at 128,040,004 loads and cost 2.00× on an end match. The bounded F reads 3
   and 1.0001×. This also fixes how the compound's own `_match` must be built (§B.3).
2. **`(?R)` in Q is sound past the floor** (J-3).
3. **The first build's bench reach is 0**, so G6 is a whole-bench byte check (J-5).
4. **The lever design** (separate harness binary + hidden internal entry + self-marking
   `"forced-off"`) was chosen over an env var or a hidden flag as an answer-free choice; it is
   recorded in §A.11 for the manager.
5. **`sqli_p.txt`/`sqli_np.txt` are empty files in the tree** (revision 1's `cost.py` reads
   them); revision 2 takes concat-sqli from `results/cases2.tsv` instead.

## Open questions for Frank (§G, discussion form)

Q1 `--fast-or-fail` when a compound overflows a cap (leaning: degrading, `fof = IN`); Q2
reserve `__` in user prefixes (leaning: refuse, population 0); Q3 VM parts may answer where
today gives up (leaning: accept, derive the lever arm's GIVEUP1 rows from the stamp; needed
only at B6).

## What is owed

Nothing. No long run was launched; every number above is complete and committed.
