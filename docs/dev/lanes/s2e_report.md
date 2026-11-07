# s2e — span_pick stage 2 unit S2e "the set" (kit request R-35), lane report

Lane s2e, branch `lane/memfn-s2e` (cut from `lane/memfn-s2c` @ fd75d4119), 2026-11-07. Builds
`docs/design/memfn/span_cards.md` §9's S2e row (span_cards rev 1.5 + r11 fixes; Frank's stage-2 GO
2026-11-06 as recorded in the design), with §8.3 DEFAULTS (B) and the §10.2 amendments.

## Summary

- `measure_store/zen4-grid3/1/` committed: window 2 (run `s2d-20261107a`) scored by the FIXED est at
  fd75d4119: **outcome FULL, digest `2d2b3c0861443bec`, reproduced** (38 rows, 826 cells, `partial` 0).
- The embed is cell-less (Makefile strip step + ksgen writes an empty cells table and records `file_cells`);
  `--list-measurements` gains `file_cells`; DEFAULTS `idk` -> `zen4-grid3@1` (DEFAULTS.log row 2,
  `movers/0002.tsv` with 0 movers, to be re-derived by census job 485).
- The recompute check `tests/knowledge/meas_recompute.py` (written from the spec text alone by a sub-lane,
  imports nothing from slot/), wired into `tests/knowledge/run_measures_tests.sh`: every row, gate, J1's
  verdict, floor and outcome re-derived exactly.
- check C's measure_store pass in `tests/memfn/finder_check.py` (33 format-2 form rows, floor 33, 0 stale).
- Standing rule for fused-compare classes written (span_cards §3.5); vcls `[^x]` -> alu1; abs_ns_e6 note.
- Sabotage: 11 new rows S2964-S2974, all DETECTED by hand; S1229 re-aimed. Gate jobs 480-486 written and
  dry-run, NOT queued (owed: the gate jobs, queued by the kit manager).

## S2a tip merge

`git merge 252e0a1cb` ALONE: automatic, no conflicts, merge commit `5b6cf41aa` (12 files: ks_measures
KS_MEAS_MAX fix K138, memfn_sites.c `_Static_assert`, S2910 re-aim, S2912, known_issues, reports). Then
`make -j8` rc 0 and `make strict` rc 0 ("whole tree compiles clean"). `5b6cf41aa` is S2e's NAMED BASE for every
base-vs-head comparison below (size, census, mech).

## The set (window 2, fixed est)

- est's `draft_gate` refuses at this branch's HEAD (S2a's tip moved timed `src/`; the draft requires the est
  commit clean and the timed code unchanged since code_commit `1e4999d1c`), so est ran from a
  `git clone --shared` at **fd75d4119** under scratch (`/var/tmp/pcrec-pcrec/scratch/memfn/s2e/estclone`),
  over a copy of `s2d-20261107a` (`diff -rq` equal to the original).
- est rows (`scratch/memfn/s2e/rows.txt`): every row/drift/note/policy/outcome line identical to
  `span_cards/s2d2/r11_rows.txt`. Draft: 38 rows, 826 cells, digest **2d2b3c0861443bec**, outcome **FULL**,
  sha-256 `0c31e461...7071fa`.
- "its sha checked against S2d's report": S2d REFUSED window 2 and wrote no draft, so the comparison is against
  review r11's re-score draft (lane s2c15fix, sha `fe97a661...`): the two drafts differ ONLY in the
  `# note est_commit` line (8c193722d there vs fd75d4119 here). READING: r11's draft is S2d's scored record
  of this window; stated so.
- Canonical writer `pcrec --list-measurements=draft.tsv > set.tsv`: sha-256
  `c84766ade779fda6867923d58e13a6aa7223ae7d9a48be8df1ab9b1593cee4e1`, idempotent (R4), `ks_ref.py`'s digest
  2d2b3c0861443bec. PROVENANCE.md names the run, slot commit 1e4999d1c, run record sha `d2c9fb97...263b`,
  transcript sha, **est commit fd75d4119** with its note line, the bound rows' evidence, D188's facts, the
  embed and what derives. `index.tsv` row added.
- NOTE: S2e's vcls.py/vcls.out change (below) is in est's TIMED set, so an est at THIS tip would refuse to
  re-score window 2 (fails closed). The set is scored at fd75d4119 and PROVENANCE says so.

## DEFAULTS flip

`DEFAULTS`: `idk	zen4-grid3@1`. `DEFAULTS.log` row `2	idk	zen4-grid1@1:13a6536315af1520
zen4-grid3@1:2d2b3c0861443bec	movers/0002.tsv`. `movers/0002.tsv` in movers.py's own `--movers` shape:
seq 2, old/new, code_commit `6608a3104` (the last commit touching a built input), population "corpus rows 6304,
distinct patterns 5014, arms c-default;c-utf8;c-vm;ir;facts, passes base;self", movers 0. It is EXPECTED, not
yet measured: job 485 runs the census and fails unless its 0002.tsv equals the committed one but code_commit,
and unless the built inputs are unchanged between that code_commit and HEAD.
`--list-measurements` base vs head moves by exactly §1's rows and column: grid1's `default_for` idk -> empty,
the new grid3 row (`default_for` idk, file_cells 826), the `file_cells` column (grid1 0); the grid1 NAME view
is byte-identical base vs head. Amendments landed: measures.md §5¶6 (default), §6¶1 (file_cells), §6¶2
(FILE vs NAME view), §8¶2 (cell-less embed), §8¶3 (sets today), a new §3.3¶3 (cells in neither digest: the
stripped copy shares the identity, the file sha covers cells); measure_sets.md (`[s2]` lines: movers writer
§2.1, §3.6 default-change, sizing, §8.3); span_pick.md (`[s2]` Stage 2, Row 1, §Defaults);
measure_store/CLAUDE.md. `docs/spec/cli.md` §2.9a defers columns to measures.md §6 (no hunk needed).
`match_api.md` 6.3.10¶12's `zen4-grid1@1:...` is a syntax example, left as is.

## Standing rule (fused-compare classes)

`[S2e STANDING RULE]` bullet in span_cards §3.5 ("Fused-compare classes: a standing rule for EVERY future
window"): (1) a class is fused-compare ONLY by est's structural check of the pinned launch executables (two
agreeing readings), NEVER by a median's sign; (2) a bound row's value is max(0, med) and its noise
max(r_max, |med|), per REV15-5; (3) the rule changes only by a new revision plus a review before a window.
Cites S2950-S2963, review `docs/dev/reviews/2026-11-07-r11-memfn-s2rev15.md` and `s2d2/r11_rows.txt`. Sabotage
rows that FAIL on a non-fused class: **S2952 (x3)** and **S2951 (x2)**, both DETECTED in gate job 474's run
of 2026-11-07 (`.boxqueue/done/20261107T075022...-474-kit-s2c-slotsab/job.log`); confirmed, none added.
**This rule is main's condition for ACKing S2d.**

## vcls residual

FIX-5: `slot/vcls.py` `shape()` classes a two-range `[^x]` (0..x-1, x+1..255) as `alu1` (gcc lowers it to
one `cmpb`). Re-run over the same sweep (sha b88599f6, commit 71cad723e; the original reproduced exactly
first). Counts before -> after: RTE `c2.alu1` 216 -> **220**, `c2.cmp2` 74 -> **70** (the four sites);
DEF unchanged; verify lines unchanged. The majority stays alu1, so `plan.py`'s `shape_majority` and the plan
are unchanged (no plan change). slot/CLAUDE.md updated.

## abs_ns_e6 note

Five rows hold `value_e6` 0 beside a negative `abs_ns_e6`: the four bound rows (-22355, -20352, -22986,
-20694) and the sub-resolution `kit.verify_cmp.settest.c2.p50` (-1942). Stated in PROVENANCE.md and in
measures.md §3.5¶3a (with ¶3b): the column is the UNCLAMPED med(abs_l), provenance only, read by no reader.
"No reader" by grep (src, memfn, cli, lib, scripts, tests): only the column-name table in
`src/core/ks_measures.c:94`, the column macros in `ks_measures.h`, the views that print every column,
`tests/knowledge/ks_ref.py`'s decode and the recompute's provenance compare; no digest, stamp, kit row or
selection reads it.

## Recompute and checks

- `tests/knowledge/meas_recompute.py` (sub-lane, opus, spec-text-only: measures.md §3.4-§3.5 and kit-grid@3's
  rules from span_cards; imports only `ks_ref.py`, nothing from slot/). Over the worktree: rc 0, PASS on three
  copies, cards, 826 cell ids, base rule (35 delta rows), jobs, drift, row list 38, rows exact (W 999387;
  bound 4, gate pass 3, priced 28, sub-resolution 3), gates, J1 (verdict c re-derived), floor and outcome FULL,
  `partial` 0, every cell read. Population: "1 format-2 set(s) (floor 1), 1 format-1 skipped" (keyed on the
  header's `format`). Its report arrived late (via the kit manager and directly); I had already verified the
  files by reading the header and running both scripts (committed 6608a3104). It found no spec/producer
  disagreement. Its READINGS of open spec sentences: (1) §3.5¶3: a null row's abs_ns_e6 is compared only when
  the set states one (no null rows today); (2) §3.5¶11: `unless-j1-b` is decided by the RE-DERIVED J1 verdict,
  not the stated one; (3) §2.2¶5: a cell no row, control or verdict reads fails as UNREAD-CELL; (4) §3.5¶2: a
  card's `-` gate takes the policy's `gate_default_e6`; the set's cards must equal the record's (CARDS, from
  design §2.4, not the spec); (5) §3.4¶6: ids are checked against their columns BEFORE uniqueness, so (x2)
  reports ID-COLUMNS; (6) plant (x3) edits only the fifth id field, values untouched, BASE-RULE fires before
  any row is computed; (7) §3.4¶8: base-cell events must be an integer, 0 not required. NOT covered by the
  recompute: §3.5¶8a's est-commit and timed-code checks (they need git; est's draft_gate holds them) and the
  `source` column (display text).
- `tests/knowledge/run_measures_tests.sh`: STORE checks re-aimed (R4 on the FILE; R4/R5 of the NAME vs the
  runner's OWN stripped copy; `file_cells` vs the file's count; embedded text vs the stripped copy, 0 `cell:`
  scopes in the pre-parse); the Makefile's strip step re-run into scratch and compared with the runner's
  strip; a fresh ksgen over DEFAULTS + sets compared with the committed `measures_table.inc`, and
  `meas_store_check.c -DMSC_TABLE` over that fresh table (pre == fresh parse, 0 cells); the RECOMPUTE section.
  Last direct run: 110 checks, 0 failed.
- check C's measure_store pass (`finder_check.py check_store`): cards vs kit-grid.tsv's ver, every row on its
  card, non-form rows carry `-`, format-2 form tokens resolve through `arm_fixtures --hash` (red, never
  "later"), deps fullmatch `kit:form.<same id>=<16 hex>`, stale counted; floor 33. `run_finder`-equivalent
  run: 1108 passed, 0 failed, "2 kit-grid set(s), 33 format-2 form-bearing rows checked, 0 stale".
- Drift gate: `make gen-measures` after the last ksgen edit leaves `src/core/` clean.
- Light sections run directly (niced) at the code tip: `make test-codegen` rc 0, `test-spec-history` rc 0,
  `test-claudemd-size` rc 0; no `*** [test-` line in any log. `make strict` rc 0 at the merge; the full gate is job 480-482.
- READING (ksgen pre-parse): "the pre-parse has no cell" is implemented by writing an EMPTY cells table from
  the parsed file, not by parsing the stripped text; equal by meas_store_check's compare. A future derived row
  reading a cell would fail on the stripped NAME view, which that compare would show.

## Sabotage

S-ids S2964-S2974 (grep: free on main, in every worktree's tests/mech and in requests.md). All planted and
reverted by hand, each DETECTED:

| row | id | where | detector, observed |
|---|---|---|---|
| (p) | S2964 | recompute_plants.sh | ROW-MISMATCH kit.find_byte.libc noise_e6 610 vs 609 |
| (q) | S2965 | recompute_plants.sh | ROW-MISMATCH kit.enter.1.NONE value_e6 (W moved) |
| (w) | S2970 | recompute_plants.sh | REFUSED RECORD-SHA |
| (x) | S2971 | recompute_plants.sh | J1-VERDICT: stated b, re-derived c |
| (x2) | S2972 | recompute_plants.sh | REFUSED ID-COLUMNS |
| (x3) | S2973 | recompute_plants.sh | REFUSED BASE-RULE |
| (x4) | S2974 | recompute_plants.sh | REFUSED THREE-COPY |
| (u) | S2966 | mech, memfnfinder | "form libcx resolves to no form hash (red, never later)" + floor |
| (u2) | S2967 | mech, memfnfinder | "records deps kit:form.walk=..., not one kit:form.libc=..." + floor |
| (v1) | S2968 | mech, knowledge | "the Makefile's strip step disagrees with the runner's strip" |
| (v2) | S2969 | mech, knowledge | fresh ksgen != committed table; "cells: 826 rows pre-parsed, 0 fresh" |

`recompute_plants.sh` trailer: `== recompute plants COMPLETE: rows=7 detected=7 control=PASS`.
S1229 re-aimed to `{ "idk", "zen4-grid3", 1u }`. Mech fields: `VALIDATE_ONLY=1` over job 483's 20 rows valid.
READING (v1, v2): §9 names the embedded-text compare and meas_store_check's pre/fresh compare. Over the
COMMITTED .inc files those see a Makefile/ksgen edit only after a `make gen-measures`, which no suite runs; so
the runner re-runs the strip step and ksgen fresh, and the named compares (pre == fresh, 0 cells) are applied
to the fresh output. S2969 plants at the `put_tab(... "cells" ...)` line (ksgen holds the table in a local
`cells` pointer so the plant is one line).

## libpcrec size

Base `5b6cf41aa` (scratch clone build) vs head, `size -t build/libpcrec.a` TOTALS:
text 1639817 -> 1650470 (+10653), data 194576 -> 199952 (+5376), dec 1834909 -> 1850938 (**+16029 B**).
`size -A build/obj/core/measures.o`: Total 68207 -> 84722; `.rodata` 9595 -> 16379, `.data.rel.ro.local`
9464 -> 14832, `.rodata.str1.1` 3195 -> 4790, `.rodata.str1.8` 2078 -> 3902 (Berkeley: text 17339 -> 27894,
data 9464 -> 14832). Growth ~16.0 KB against tree_drill D's ~16 KB projection: on the projection. Every
other object is the same.

## Data-mover census

NOT run here (heavy: ~100k compiles, under the box lock). Job **485** runs `slot/movers.py` over every
distinct corpus pattern, five arms, two passes (base = 5b6cf41aa's pcrec vs head; self = head under
`--measures=zen4-grid1` vs `zen4-grid3`), writes its 0002.tsv to scratch and compares it with the committed
one but code_commit. Zero movers is the witness; its base pass also serves as the emit_sweep-style
byte-identity witness over those arms (§9's "emit_sweep byte-identical" is owed through this job; the
deny/SIMD arms of emit_sweep are not in movers.py's ARMS: stated, not run).

## Gate jobs

Under `/var/tmp/pcrec-pcrec/scratch/memfn/s2e/jobs/` (`common.sh` + 7 jobs, `JOB=`-free names in the
PRIO-OWNER-REST form, each sourcing common.sh by absolute path; `--ready` waits on s2a's hold.sh and the
previous stage):

- `480-kit-s2e-strict` — make strict.
- `481-kit-s2e-sections` — test-knowledge, test-memfn-finder, test-compound, test-codegen, test-registry,
  test-memfn-g2, test-spec-history, test-claudemd-size (after 480).
- `482-kit-s2e-test` — make test via scripts/perfrun (after 481).
- `483-kit-s2e-mech` — 20 mech rows (rows_for.sh over the changed files + the listing readers + S2966-S2969;
  after 482).
- `484-kit-s2e-slotsab` — slot/sabotage.sh, 35 rows (after 480).
- `485-kit-s2e-census` — the data-mover census (after 480).
- `486-kit-s2e-plants` — recompute_plants.sh, 7 rows (after 480).

Each dry-run through `scripts/boxqueue add --no-start` against a SCRATCH queue dir
(`PCREC_BOXQUEUE_DIR=.../s2e/bqtest`; boxqueue has no `add --dry-run`, `add` dry-runs before enqueueing):
all 7 accepted with their declarations; the real queue holds no s2e job. NOT queued. OWED: the gate jobs.

Light sections run directly (test-codegen, test-spec-history, test-claudemd-size): all rc 0 (Recompute
and checks).

## STATE AT HANDOFF

OWED: the gate jobs (queued by the kit manager): 480-kit-s2e-strict, 481-kit-s2e-sections, 482-kit-s2e-test,
483-kit-s2e-mech, 484-kit-s2e-slotsab, 485-kit-s2e-census, 486-kit-s2e-plants, under
`/var/tmp/pcrec-pcrec/scratch/memfn/s2e/jobs/`, each dry-run clean, none queued by the lane (brief). No
rulings file was written for this lane. Branch tip clean; to resume, read this report and span_cards §9's
S2e row. Two items stand on those jobs: the census's zero movers (485, which also re-derives
`movers/0002.tsv`) and make test (482).

## Charter-vs-committed checklist

| §9 S2e item | committed |
|---|---|
| draft, sha checked against S2d's report | yes (vs r11's draft; differs in est-commit note only) |
| canonical writer, store files, index.tsv | yes (set.tsv, PROVENANCE.md, index row) |
| gen-measures cell-less: strip step, ksgen file_cells | yes (Makefile `meas-strip`, ksgen.c, .inc regenerated) |
| listing `file_cells` column | yes (measures_dump.c, measures.c accessor, spec §6) |
| STORE compares re-aimed; S1241/S1232 re-verified | re-aimed yes; S1241/S1232 in mech job 483 (owed) |
| DEFAULTS (B) and amendments (§8.3, §10.2) | yes (DEFAULTS, log row 2, spec/design hunks) |
| recompute check, format-2 population floored, run record, J1 | yes (meas_recompute.py, floor 1) |
| check C measure_store pass, floored, deps, stale 0 | yes (floor 33, 0 stale) |
| movers.py and movers/0002.tsv | movers.py from S2c; 0002.tsv committed, census owed (job 485) |
| S1229 re-aim | yes |
| plants (p) (q) (u) (u2) (v1) (v2) (w) (x) (x2)-(x4) | yes, S2964-S2974, all DETECTED by hand |
| make test (normal), census | owed (jobs 482, 485) |
| emit_sweep byte-identical | owed via job 485's base pass (five arms) |
| libpcrec growth reported | yes (+16029 B) |
| brief: standing rule, vcls, abs_ns_e6, S-id grep, sizes | yes |
