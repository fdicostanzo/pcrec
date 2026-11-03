# sp1a — span_pick stage 1, unit 1a (dead code, the census map, the ratchet base)

Lane sp1a (opus), branch `lane/memfn-sp1a`, cut from main 564db08c5 (span_pick.md rev 5.2, the design
of record). Build go: the owner's conditional approval, confirmed by main's GO (2026-11-03). Scope:
unit 1a exactly as span_pick.md rev 5.2 §Staging specifies, plus (once for all of stage 1) the frozen
bench pattern list. Nothing from any other unit.

## What changed

Commits on `lane/memfn-sp1a` (oldest first): f5ce4c49e (census at base), a00f2437c (the unit's code),
43f42766a (bench list), 4d63bbd54 + 8f0d8c0cf (reach-equality instrument), then this report.

- **N3, `mf_set_terms`** (internal, no seam event): `memfn/src/terms.c` deleted, with kit.h's cover
  section (`MF_SET_K`, `MF_SET_BUDGET`, `mf_sterm`, `mf_cover`, the prototype). No caller anywhere
  (`memfn/`, `src/`, `cli/`, `lib/`, `tests/`). Readers edited: `memfn/PROVENANCE.md` (its row; C16
  goes red on a row naming a missing file), `memfn/src/CLAUDE.md`, `memfn/CLAUDE.md` (R-28's stack
  paragraph: `pair_facts` and the `dfs` note), two kit comments (window.c, vany.c). Left as history:
  `docs/dev/lanes/r17b2/` (lane evidence), run_link_checks.sh's header comment.
- **The inert finder rows R3a, R3b, R4** (B9 iterator rows; no deny; their predicate needed KN_H, a
  fact no site states, so they never held): the three rows and their contracts (`ct_r3a`, `ct_r3b`,
  `ct_r4`) deleted from `memfn/src/finder.c`, with the H comparator kinds only they read
  (`FL_H_SPAN`, `FL_H_POP`, their `cmp_eval` arm, `fd_holds`' two KN_H lines). KN_H stays in the
  knowledge-key vocabulary (the listing's `needs` letters) and FF_A3 in `fd_form` (B9's reserved
  form; `ff_name` is asserted against the enum). Ids reserved; logged in `memfn/docs/finder_history.md`.
  Readers (span_pick 1a's list, re-grepped): `tests/memfn/finder_check.py` `FIND_ROWS`;
  `tests/memfn/rows.tsv` (and its header count); `tests/memfn/row_floors.tsv`; plus one the design
  did not list, `tests/memfn/run_rows.sh`'s `ROWS_FLOOR` 36 -> 33 (a floor on the kit's listed rows:
  33 now, so 36 would read red). The keys `kit.h3a`, `kit.h3b`, `kit.gstar.*` stay in the sets, unread.
- **MF_CLASS_V 5 -> 6** (`memfn/include/memfn.h`, with its history line): `mf_class.pres_row` /
  `pres_led` carry finder-row indices and three rows left ahead of the PRES rows. No layout move, no
  MF_SITE_ABI move. pcrec's one reader (`pcrec_memfn_pres_routed`, memfn_sites.c) maps the index
  through `mf_finder_rows`, so its records keep their row names; `arm_fixtures.c`/`proof_check.c`
  compare `v` against the symbol. Recorded in `memfn/docs/journal.md`. The responses-ledger line is
  the kit session's to write (single writer): **for the kit manager**.
- **The census map** (span_pick rev 5.2 §The tables, "The decider census"; written at the base, kept
  by each unit): `tests/memfn/decider_census.tsv` (50 members: 39 `fn`, 7 `part` and 2 `data` rows mapped to
  T-FIND, T-VERIFY, T-SETTEST, T-CMP, T-PRES, T-FRAME, KEY, M, TIE or a named exception, each with
  its retiring unit or trigger; 2 `excluded`, `kit_walk`'s definition and prototype) and its check
  `tests/memfn/decider_census.py`, run by `make test-memfn-rows` (one more recipe line; no new make
  test section). Members are the design's list by name; the lane ADDED, as members, the helpers the
  design's ranges imply (`f0_of`, `walked`, `scan_ok`, `in_stretch`, `m_pair` in KEY/M), `tie_over`
  (R23's other member), `member_test` (T-SETTEST, the Q11 site) and the RUN chain as
  `pred_test:run-chain` (the per-byte RUN compare lives in `pred_test`). Parts are checked by an
  anchor substring inside their function.
- **The ratchet base**: roadmap §5 R20-R27's recipes run at 564db08c5 and at HEAD (Census and
  ratchet below). No roadmap edit (stage 1 does not edit the roadmap).
- **The frozen bench pattern list** `docs/dev/lanes/spanpick_bench_patterns.txt`: pcrec-bench
  e351528a, every `[[patterns]]` file of `bench/*/subbench.toml`, read by `r33_sim/collect.py`'s own
  `src_bench` (imported, not re-derived): 392 patterns (356 distinct), `--list-source` escapes; a
  leading `#` is written `\x23` (three bench patterns are `#`, which `read_patterns_file` would skip
  as a comment). Round trip through emit_sweep's `read_patterns_file` checked equal to the bytes.
- **`tests/memfn/reach_equal.py`** (new, opt-in, no make target): REACH EQUALITY between two MF_TRACE
  builds, per arm, every `MFTRACE REACH` key (row chosen/asked and field/class cells) summed over the
  population, with `--gone` rows that must have lines at the base and none at HEAD; K35 floors on the
  population and on chosen totals; `reach_equal: DONE rc=N` trailer. Stage 1's later units (1f's gone
  rows, 1e's row map) can reuse it.
- `tests/memfn/CLAUDE.md` gains the two files' lines.

## Witness

Unit 1a's witness (span_pick rev 5.2 §Staging, "Witness, per unit" and 1a's row): byte identity on
EVERY arm, stamps included, over the corpus plus three `--patterns-file` inputs; G2; the census;
REACH EQUALITY on every surviving row with the declared difference R3a, R3b, R4.

Run in the lane (light, under 50 compiles each, before the box queue's window):

| check | file/command run | result |
|---|---|---|
| census + plants | `make test-memfn-rows` (runs tests/memfn/decider_census.py) | rows 222 passed 0 failed; census 55 passed 0 failed; backstop 36 hits, 0 outside a member; plant window.c (run_member's loop) 2 stray hits RED; plant presence.c (`c < sm`) 1 stray hit RED |
| finder | `make test-memfn-finder` | 1985 passed, 0 failed |
| link (C15/C16/R-28) | `make test-memfn-link` | 11 passed, 0 failed (after the PROVENANCE row; red before it, C16) |
| warnings | `gcc -Wall -Wextra -Werror` on finder.c, compose.c, window.c | clean (the full `make strict` is job 300) |
| byte identity smoke | base 564db08c5 vs HEAD, default engine, job 588's 24 + `zzzzzzz~J` | 25 of 25 identical |
| reach smoke | `tests/memfn/reach_equal.py --limit 6`, 4 arms | 0 differing keys; R3a/R3b/R4 lines at base, none at HEAD |

**OWED (queued, see Queue jobs): the full witness** — byte identity over all 69 declared arms
(emit_sweep's `--list-ident-arms`) with the three patterns files; reach equality over the corpus at 18
arms; `make strict`; the kit's structural sections incl. G2 quick and test-findings (the
`*_movers.txt` manifests). Expected: every job green; the reach job's declared difference exactly the
three fd rows. The full `make test` and mech gates are later landing jobs (not queued here).

## Census and ratchet

Roadmap §5 recipes, run at the base and at HEAD (a scratch transcription of the recipes,
`$PCREC_TMPDIR/scratch/memfn/sp1a/ratchet.sh`):

| row | base 564db08c5 | HEAD | delta | 1a's declared delta |
|---|---|---|---|---|
| R20 kit find-method deciders | 3 | 3 | 0 | — |
| R21 position enumerators | 1 | 1 | 0 | — |
| R22 mass variants | 3 | 3 | 0 | — |
| R23 tie-rule tables | 1 | 1 | 0 | — |
| R24 run-member spellings | 2 | 2 | 0 | — |
| R25 landmark shadow | 1 | 1 | 0 | — |
| R26 inert finder rows R3a/R3b/R4 | 3 | 0 | **-3** | -3 |
| R27 `mf_set_terms` | 1 | 0 | **-1** | -1 |
| **total** | **15** | **11** | **-4** | -4 |

No row rose; 1a introduces no counted member. The census map's base: 50 members, the backstop's 36
hit lines at the base all inside members (span_pick rev 5.2 cites 36 at 2636dee99; the same 36 at
564db08c5), unchanged at HEAD (1a removes no backstop line: the finder rows carried none).

## Kept counted names

**None.** 1a deletes both of its counted members WHOLE (R26's three rows, R27's function and file);
it keeps no counted name as a thin caller, so main has no recipe to re-state before landing. The other
counted names (R20-R25's members) are untouched by 1a.

## Queue jobs

Scripts in `$PCREC_TMPDIR/scratch/memfn/sp1a/jobs/` (each with `--dry-run`, dry-run tested; shared
settings `common.sh`), queued with `scripts/boxqueue add`, every one `not-before 2026-11-03T01:05`,
chained with `after` in this order, each ≤ 1 h with its `est`:

| job | what | est / cap | result |
|---|---|---|---|
| 300-kit-sp1a-strict | `make -j16; make strict` | 240 / 1200 s | job log; trailer `sp1a-strict: DONE rc=N` |
| 301-kit-sp1a-memfn | `make test-memfn-rows` (census + plants), `-finder`, `-link`, `-g2`, `-arms`, `-stamps`, `-deleg`, `-manifest`, `test-findings`; after 300 | 600 / 2700 s | job log, 9 `sp1a-section NAME rc=N` lines |
| 302-kit-sp1a-reach | HEAD MF_TRACE build into `scratch/.../head-mftrace`; `reach_equal.py` vs the base's MF_TRACE build, corpus + the 3 patterns files, 18 arms (default, `--engine=vm`, `-fmemfn-simd`, `-e utf8`, the 14 kit denies), `--gone fd:R3a,fd:R3b,fd:R4`; after 301 | 1200 / 3600 s | job log, trailer `reach_equal: DONE rc=N keys=K differ=D` |
| 303/304/305-kit-sp1a-ident1..3 | emit_sweep's 69 declared identity arms, split by index into 3 shards of 23 (`--ref-bin` the frozen base build `scratch/.../ref/build/pcrec`, `--bin` the tree's build, the 3 patterns files); run-total 5700 s; 303 after 302, 304 after 303, 305 after 304 | 1900 / 3600 s each | `<run dir>/job.log.ident` (`ident: arms run 23`, `ident: arms failed 0`); per arm `scratch/.../ident.<ARM>.log` and `scratch/.../ident/<ARM>/` |

Each job's result is under `worktrees/.boxqueue/{done,failed}/<timestamp>-<job>/` (read with
`scripts/verdict`). Patterns inputs: the committed bench list, `scratch/.../p588.txt` (column 3 of
`docs/dev/lanes/s3_evidence/sample_588.tsv` less its `#` lines, 24 patterns) and `scratch/.../pzzz.txt`
(`zzzzzzz~J`); every job's dry run counts the three files at 417 patterns. A red job STOPS the chain
(each `--ready` is `after` its predecessor).

## STATE AT HANDOFF

STATE: delivered, validation OWED (jobs 300-305). Code complete for unit 1a at the branch head; no
rulings file named in the brief. For the kit manager: the responses-ledger line for MF_CLASS_V 6. For
main: the ratchet log line (15 -> 11 at 1a's landing) and the landing jobs (full `make test`, mech).
A fresh agent resumes from the job results above: all green = 1a's witness complete; any byte moved
in an ident arm or any surviving-row reach difference is a STOP per the brief.
