# Lens `check` -- memfn-sp1f (SUBJECT 98145b3d5)

## Findings

### CHECK-1  CONFIRMED  maintenance/design  effort S  blast: tests only
No regression test for the new `gone` logic or the selfcheck change.
scripts/tests/emit_sweep.py.test (the sibling control for `--dumps-declared-rows`, line ~216, "both directions")
is NOT in the diff. `dumps_declared_delta(..., gone)` and the `real = label != "selfcheck"` gate are
untested; the only evidence is the lane's one real run. Behaviour I measured by importing the module from
SUBJECT with crafted bytes (11 cases) and sweep_dumps on base vs subject binaries (7 runs, dumps only):
 - gone row still present: caught (2 problems). Gone row missing from REF: caught. Extra removal: caught
   (line count). Extra addition: caught. Remove-b/add-c: caught (undeclared row moved). Reorder: caught.
   Gone + declared-moved together: passes correctly. Flag typo (`--list-axis`): the real diff stays
   undeclared, so it is a mover (caught, by accident of the fallback, not by validation).
   Correct invocation (`--list-axes:fd-r8`, `:fd-ndisp`) base->subject: 0 movers, declared_moves 2.
   Only fd-r8 declared: caught (line count 274 -> 273). Third bogus key: caught (not in REF).
   Reversed binaries: caught.
 - Fix: add the cases above to emit_sweep.py.test (a 12-line python heredoc next to the declared-rows one).

### CHECK-2  CONFIRMED  maintenance  effort XS  blast: emit_sweep --variant + --dumps-declared-gone/rows
The selfcheck exemption is an exact-string compare, `label != "selfcheck"` (emit_sweep.py:3381), but the
variant path calls run_full_sweep with label `f"selfcheck-{vname}"` (line 2065; `dumps` is in
VARIANT_STREAMS, line 641). Under `--variant X --dumps-declared-gone ...` the variant self-check
(ref vs an independent rebuild of ref) still receives the declared rows, so identical dumps produce
"declared gone row ... is still listed (surface identical)" (reproduced with sweep_dumps(W,W,...gone)) and the
self-check FAILS. Latent false RED, not a masking. The fix mask is also a magic string coupled across two
call sites; pass `declared=False` (or a kw) from the two selfcheck call sites instead of comparing a label.
Does the selfcheck change MASK anything? No: it compares one revision with itself, so no declared delta can
legitimately exist there; the identity_required report still demands all-identical.

### CHECK-3  CONFIRMED  minor/maintenance  effort XS
A declared-gone key matching SEVERAL REF lines is accepted: `la` drops every line whose first field equals
the key, and HEAD must hold none (case "a/x/x/b -> a/b": []). `gone` is documented as "the row", singular.
A surface with repeated first fields (the --list-syntax family may have them) would let one declaration
swallow N removals. Not exploitable on --list-axes (keys unique). Fix: require exactly one REF line per
gone key (or document "all rows with this key").

### CHECK-4  CONFIRMED  design/test-coverage  effort S
S919's UNREACHED claim is true at SUBJECT but its REACH_POP is a dead literal and can no longer flip.
tests/mech/sabotages/S919_...sh: `SAB_REACH_POP='tests/memfn/finder_check.py|"body:R1:UNSTATED" in ln|1'`.
 - The literal matches 0 lines at SUBJECT and ALSO at BASE (BASE had `"body:R1" in ln`), so the probe was already
   vacuous before 1f; the lane did not touch S919 at all (diff shows only S917).
 - Now it names R1, an id that is reserved, never reused, and deleted: even the day a row reading `body` returns,
   it will not be R1, so the probe stays at 0 and the "reads NOW REACHED if ..." sentence in SAB_EXPECT_REASON is
   false by construction. Every FD_CT in memfn/src/finder.c:194-221 passes MF_ANY for `body` (no row reads M;
   KN_M and FLD_body are vestigial), so UNREACHED is true, but only by a probe that cannot flip.
 - Also stale: the S919 header ("must DECLINE every finder row that reads M (R1, R2, R8)"), and "R1's gate record
   must name body" in its WHERE-IT-IS-SEEN.
 - Fix: re-aim REACH_POP at the true trigger, e.g. `memfn/src/finder.c|^FD_CT(_T)?\(.*(MF_ONESHOT|MF_PARAM|MF_BODY_)|1`
   (a FD_CT whose body argument is not MF_ANY), and reword the header to "any row that reads M".

### CHECK-5  CONFIRMED  maintenance  effort XS
S917's UNREACHED holds and its probe is sound but fragile. `memfn/src/finder.c|\{ FL_KEY,|1`: 0 matches at SUBJECT
(and 0 at BASE: the old R8/R1/R2 used FL_N/FL_E_G, so the wording "R8, R1/R2 ... no decision reads fd_lookup" is
true both before and after). fd_lookup's only caller is fd_value <- cmp_eval's FL_KEY case (finder.c:421,458);
no row has FL_KEY, so no decision reads it. It flips when a row is written `{ FL_KEY,` (the table's own
initializer shape, matches the typedef line? no: the enum is `{ FL_NONE = 0, FL_KEY }`, not matched; comments
"FL_KEY:" not matched). Held. Residual: the whole FL_KEY machinery (cmp_eval FL_KEY, key_expand, fd_lookup,
the mf_finder_key listing at :851) is now code with zero rows and zero live detector (D77 "build ahead of a
measured need" lens, not a check defect); S917 correctly says it must be re-aimed when a row appears.

### CHECK-6  CONFIRMED  maintenance/doc  effort XS
Dead `unpaid` column and a check that guards a field nothing can set. finder.c:141 keeps `fd_form unpaid` "FF_UNSTATED
on every row", the listing still emits it (:858) and finder_check.py A:208 asserts it is "-". It cannot fail
except by someone re-adding the field's use; the lane chose a ratchet over deleting the column. If kept, fine
(it does fail on a row with an unpaid pick); if the column is a leftover, delete field + column + assert together.
Same family: LATER_FORMS still lists W64 "B6"/NONE "B5"/dispatch-twin "B4/B8" (finder_check.py ~line 140), pushing
three "R-MS3: form X hashes from Bn" strings into the UNREACHED list although R8 (W64's row) and the dispatch
rows are gone; the steps they name are no longer the plan (span_pick supersedes). Stale narrative, not a gap.

### CHECK-7  SUSPECTED  maintenance  effort S
IDENT_MEMFN (emit_sweep.py:3002) and finder_check B1_DENIES are hand-lists with no cross-check against the
`--list-axes` memfn section. 1f edited both by hand and they match the binary today (12 = 12:
vrun-w32/w16/kb/trim/pad, precheck-assign-byte, fd-d1, fd-pres-g1, fd-pres-pick, pres-set-lead,
window-search, window-skip), but a deny ADDED to options.def and never to IDENT_MEMFN silently drops out of the
answer-identity sweep (memfn_arm.py's population check covers the axes arm, not IDENT_MEMFN). Pre-existing;
confirm by adding a row. The 1f edit itself is right (stray re-added fd-r8 is caught three ways: J refuses the
option, RETIRED_DENIES absent from options.def, memfn_arm population vs --list-axes).

### Standing: siblings, general form, unlocks
- Siblings: `facts_declared_delta` / `--facts-declared-moves` and `dumps_declared_delta` / `--dumps-declared-rows`
  (declared-delta, judged both ways). `--dumps-declared-gone` is the third member: three near-identical
  "declared delta" judges now (rows moved, facts moved, rows gone) -> [forest-for-trees] trigger at 3 members.
  Also the [MECH-REACH] family (REACH_POP probes: S917, S919, S596...).
- General form: ONE declared-delta judge taking {key: (before, after)} where after=GONE/ADDED/value, over
  any keyed TSV surface (dumps, facts, tuning rows), with the unit control in scripts/tests. Unlocks (triggers):
  an ADDED-row declaration the first time a unit adds a registry row (span_pick stage 2 adds rows at the
  --list-axes / --list-limits surfaces) -- today that would need yet another flag; the dumps stream for
  --list-facts without a second judge.
- REACH_POP discipline: a probe naming a deleted/reserved row id (S919) cannot flip. General rule: a REACH_POP for an
  "unreached because nothing uses X" row should probe X's USE SITE shape (a declaration pattern), never an id.

## PROBED-AND-HELD
- run_finder.sh at SUBJECT (single run, ~20 compiles): checks passed 1924, failed 0 (A-L, presence 44, proof 882).
- rows.tsv: 30 data lines = 12 arms + 4 runcmp + 4 fn + 10 fd; row_floors.tsv same split (12/4/4/10, fd 10);
  ROWS_FLOOR=30 matches. rows_check.py A is a floor on len(kit) PLUS an exact two-way kit/manifest comparison
  (kit-only rows and manifest-only rows both FAIL), so a stray re-added or missing row is caught; the floor alone
  would not (it is `<`, a row added to both kit and manifest passes with floor 30 -- by design, "raise in same commit").
- tests/axes/memfn_arm.py: removed 4 cells; --list-axes memfn section at SUBJECT has 12 rows; population check at
  memfn_arm.py:255 is a two-way equality with MEMFN_CLASS; DIFFER_PINS/ASSERT_ZERO removed in step with it.
- registry.md 6p8b "memfn section floor: 12" = binary's 12 memfn rows; 6p8a table lost exactly fd-r8/fd-ndisp.
- All 22 sabotage SAB_BEFORE anchors in memfn/src/finder.c, options.def, memfn.h, finder_check.py (script: every
  sabotages/*.sh whose SAB_FILE exists, count of SAB_BEFORE in the file at SUBJECT) still match exactly once
  (only S717, a SAB_COUNT 2 row in vrun.c untouched by 1f, differs). So no OTHER sabotage lost its anchor to 1f
  (S596 cand_row_deny_dropped, S1018-S1020, S1079, S1105 anchors intact).
- S1025 retirement: its three artifacts (fd_pay, pay_fill, n_interval; mf_finder_pay + --pay-grid; finder_check H)
  are all gone together; no other sabotage's SAB_SUITES-detector lived in H (H's only plant was S1025). Remaining
  references are history (run_sabotage_matrix.sh comment, tests/mech history, ctx_span/measure_sets anchor TSV
  snapshots, which are dated design records). run_sabotage_matrix.sh has no per-id count table to update; the
  +4 comment lines are the only bookkeeping and say the right thing (it still lists S1025 in "Registered before ..."
  line 497, historical).
- S1089 still detects its plant: finder_check I's refusal assertion is untouched (`ref and want in ref and not dec`).
- B1_DENIES ["fd-d1"], RETIRED_DENIES (4 names, each must be absent from options.def AND refused as "unknown option"
  by J) fail if a name is re-added.
- ONESHOT re-aim (I): requires a non-empty set of `table=fd ... verdict=` records AND no `body:` token in any of
  them, so it is not vacuous (g_b non-empty) and fails if any row's gate starts naming body; weaker than the R1
  specific check only in that no row can now name body, which CHECK-4 states.
