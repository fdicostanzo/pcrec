# CHECK findings

## Findings

### CHECK-1 — the raise retires the only sabotage witness of emit_dfa.c's K38-2 run-span assert (held raise 2794f4696, S526)
CONFIRMED (static + one plant run on a copy of the combined approximation). Severity: maintenance (a check's
witness lost; no answer moves). Effort: small (one new mech row). Blast radius: emit_dfa.c:1446 only.
- At SUBJECT, S526 (`MF_MAX_TERM 32 -> 31`) is BUILD-REFUSED by `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <=
  MF_WSPAN_POS, ...)` (src/gen/emit_dfa.c:1446), through MF_WSPAN_POS = MF_MAX_SPAN_POS = MF_MAX_TERM; its REACH
  greps exactly that chain. It is the only row in tests/mech/sabotages/ whose plant reaches that assert (grep for
  PCREC_MAX_REQ_RUN_SCAN / MF_WSPAN_POS over the rows at SUBJECT and in R/combined/tree: S526, S1918 (req.c copy
  count, not the assert), S3223 (C15 in known.c)).
- The raise (R/subject/raise_2794f4696.diff, S526 hunk) makes MF_WSPAN_POS the literal 4095 and RE-AIMS S526 at
  C14's stride clause, rewriting SAB_DESC (the old intent "the stored run no longer fits one window span" is
  dropped, not kept). The assert at emit_dfa.c:1446 survives (present in R/combined/tree) with NO row planting
  it; the new comment says only "emit_dfa.c's K38-2 assert stays satisfied".
- Re-aim itself verified on a copy (checks/s526/tree = combined tree's src, lib, memfn, tests/memfn + the S526
  plant and its SAB_FILE2 removal): `run_form_checks.sh` -> `FAIL: C14: a shape bound fails: C14 stride:
  MF_MAX_TERM must hold VM_MAX_STRIDE positions`, checks 4 passed / 1 failed; every src/ and memfn/src .c
  compiles -fsyntax-only (100 + 18 files, 0 bad), so the planted tree would build: DETECTED as the raise claims
  (a syntax-level stand-in for the build, not a mech run; the row says NOT YET RE-MEASURED).
- Fix shape: keep a row for the K38-2 intent (e.g. plant `PCREC_MAX_REQ_RUN_SCAN` above MF_WSPAN_POS in
  limits.def, or MF_WSPAN_POS below 32, expecting BUILD-REFUSED), or record in S526 that the assert's witness
  is retired and why (learnings §3: a witness that stopped reaching its site, [MECH-REACH]).

### CHECK-2 — purity's "NONE's frame part is zero" no longer sees plan_test (S3086's own detector narrowed)
CONFIRMED by plant. Severity: maintenance (a check narrowed; a sibling suite still catches it). Effort: one line.
Blast radius: tests/memfn/arm_fixtures.c:2640 (pur_call_fixtures), S3086's named detector.
- The respelled check compares `pur_vals(&r)` (all three list pointers set to NULL) from offsetof(framed) to the
  end against zero. plan_test lies in the frame part; BASE's memcmp covered its inline entries, so a NONE ask that
  answered plan_test was red. Now a NONE reply carrying a plan_test list is invisible to it: the comment
  "plan_test NULL on NONE: zero too" is what the check should ASSERT, but pur_vals makes it true by construction.
- Repro: copy SUBJECT memfn/src, in mf_wdecide's NONE branch after `if (rc) memset(out, 0, sizeof *out);` add
  `if (!rc && rows && rows->plan_test && out->nplan) { memset(rows->plan_test, 1, out->nplan); out->plan_test =
  rows->plan_test; }` (checks/kp/P1); link tests/memfn/arm_fixtures.c against the kit objects; `fx --purity`:
  7874 passed / 0 failed (clean: 7874 / 0). d27_frame (seed 1, 3000 cases) on the same objects: 2519 failed,
  `none_frame_part_zero` (its frame_part_zero reads the raw pointer bytes), so the defect is still caught, but
  by d27 alone, not by the row S3086 names (SAB_REACH_POP pins `fx --purity`).
- Fix shape: assert `r.plan_test == NULL` on NONE beside the zero compare (the design's own sentence, r45_reply
  §5 (a) "`plan_test` NULL on NONE keeps it zero").

### CHECK-3 — "the asks write the caller's rows" has no witness; the deep compares short-circuit on pointer equality
CONFIRMED by plant. Severity: maintenance/design (a new contract clause untested; a regression to kit-owned
list storage would alias held replies). Effort: small (one assert per test's ask wrapper). Blast radius:
memfn.h:1593 (mf_rows: "the kit writes into it and never allocates"), r45_reply §5 "The asks write only `*out`
and the caller's `rows`"; tests arm_fixtures.c:2448, d27_frame.c:596, kit window.c:2881.
- Plant P2 (checks/kp/P2): reply_of writes plan/plan_term into function-static arrays and points the reply at
  them instead of `rows`. Results: `fx --purity` 7874/0 (clean 7874/0); d27_frame seed 1, 3000 cases 268750/0
  (identical to clean); G2 window generator (seed 20261022, 1500 sites) + driver: gen 0 FAIL, run 5600/0
  (identical to clean). GREEN everywhere.
- Why: no test asserts `r.plan == rows->plan` (or that the lists lie in the storage handed in), and every repeated
  -ask compare (`purity_repeat`, `none_ignores_*`, `purity_after_*`, pur_diff_n) treats two equal pointers as
  equal lists (`la != lb &&`, `if (a == b) return 1;`). With aliased storage both held replies point at the same
  buffer, so the compare is vacuous; the design's rule says "A pointer value is NEVER compared", and these
  shortcuts are pointer compares that can only ever turn a check green.
- Fix shape: in each test's ask wrapper, check the reply's non-NULL lists equal the rows passed; drop the
  pointer-equality shortcut (compare contents always).

### CHECK-4 — "on -1 the asks write nothing to `rows`" has no witness
CONFIRMED by plant (low). Severity: maintenance (contract clause untested). Effort: small. Blast radius:
r45_reply §5 "The asks" ("on -1 they write nothing to `rows`"); not stated in memfn.h's mf_rows comment.
- Plant P3b (checks/kp/P3b): on mf_wdecide's two NONE refusal paths (wf_check, decide) write `rows->plan[0] =
  0x5a5a` (plus a stderr marker to prove reach). Reached 127 times in d27 (seed 1, 3000 cases) and 150 times in
  G2's generator; G2 run 5600/0 green; d27's only reds (255, `ask_writes_no_trace`) are the MARKER's stderr
  bytes, none about the rows. Purity never reaches these paths (0).
- Structural reason: d27's ring returns a refused ask's slot (`g_ring_at--`, d27_frame.c:620) and no other test
  holds rows across a refused ask, so nothing can observe the write. Fix shape: one fixture that pre-fills a
  rows block with a sentinel, makes a refused ask, and compares the block; and the clause in memfn.h.

## PROBED-AND-HELD

Plant classification below: every compare is plant tree vs its witness (clean SUBJECT green by the same command
where run). DETECTED rows: the witness FAILS on the plant; "SAME" = same intent as SAB_DESC, witness reaches it.
- `python3 -I scripts/m6read_check_sab_anchors.py` (SUBJECT tree's copy, root from __file__): "sabotages checked:
  1307 (1361 anchor sites) / all anchors resolve", rc 0.
- S1018 (memfnfinder, R/plants/S1018): SAME, DETECTED: run_finder.sh 15540 passed / 2468 failed (clean 18112/0);
  red through the define-time re-ask ("the define-time query's class differs from the define's", the DESC's
  traced-driver half) on 13 C-sites, every set*/run*/pre-* fixture and the purity traced pass.
- S1083 (memfnfinder): SAME, DETECTED: 18106/6, including the named `F-B1-3: (?m)^\n's pre-check is not
  dominated` and run_proof's copy check (`B context stop: proven_prev its set`, A11/A12). The `if (0) memcpy`
  plant leaves the existing `else memset(..0xFF..)` attached: all ones, as DESC says.
- S1224 (memfnfinder): SAME, DETECTED: 18110/202, `C site N C-PROOF: proven[] differs across the layers`. Twin
  `run_proof.sh --plant S1224`: RED 101 failed at SUBJECT and 101 at BASE (same detector, same count).
- S3086 (memfnfinder): SAME, DETECTED: 18089/23, `call: site N: NONE's frame part is not zero (framed 1)` (the
  pinned `fx --purity` population). See CHECK-2 for the plan_test sibling the respelled check no longer sees.
- S1148 (kitproof, R/plants/S1148): SAME, DETECTED: reach.sh `\d{4}` -> REACH-DECLINE on the plant, REACH-COVER
  on SUBJECT; run_cover.sh on the plant tree 95 passed / 80 failed incl. `verdict - \d{4}: RX_DFA_SCAN
  "unanchored", expected cover (S1148 reach)`.
- S3097 (codegen, R/plants/S3097): SAME, LOUD on the cover patterns: zqxzqx, `hello world`, `abc[de]fghij` rc 1
  with "internal error: the memfn kit refused the `@` table's cover-row phase-1 ask (src/gen/emit_dfa.c,
  req_run_at)"; `a.*zqxzqx` (no cover) compiles rc 0. SUBJECT: all four rc 0; SAB_REACH conditions hold
  (zqxzqx: RX_DFA_SCAN "cover", RX_REQ_RUN "7a71787a7178@3"; Pattern: headers checked).
- S1407 (`run_g2_win.sh --plant S1407`, SUBJECT): SAME, RED 4787 passed / 813 failed, `PROOF: proven[1] does not
  hold`; BASE's plant: identical (4787/813, same first line). The `d + 1 - MF_PROOF_LO < proof_n` guard skips
  only the last tested position's +1 when the range ends there; interior positions still plant.
- S3092 (`--plant S3092`, SUBJECT): SAME, RED `site 138: reply id: method's emptiness ...`; BASE: identical line
  and counts (driver 5600/0).
- S3242 (`run_proof.sh --plant S3242`, new): SAME as its DESC, RED BY ITS MESSAGE ("the proof range ends before
  the statement's following offset") through mf_define (`A accept span 0 BOUNDED: refused: mf_define: ...`),
  308 failed; clean run_proof.sh 888/0 including the two new "R-short control" accepts. As the design says, it
  witnesses only that R-short exists (self-check sharing `end`'s source, r45 §1 F1); row (b) is the control.
- S526 (raise, read-only + copy): re-aimed (DESC rewritten), DETECTED by C14 stride on a copy of the combined
  approximation; see CHECK-1 for the K38-2 assert's lost witness.
- Deep compares, neighbouring fields: G2 window generator with a kit plant flipping `libc_free` on the ask path
  (checks/kp/P4): 1912 x "mf_ask: the query's class differs from the define's"; clearing a bit of the LAST proof
  row (proof_n - 1, past every tested offset) on the ask (P5): the same 1912 reds. class_same / kit_class_same /
  proof_same compare proof_n and every row below it, by-value members via memcmp with the pointer nulled: every
  field BASE's whole-struct memcmp covered except bytes past the count, which no longer exist as reply content
  (a row past proof_n is "all ones" by the B5 rule and proof_run reads exactly nproof rows; proof_run.c's
  site_static now FAILs a REQUIRED position past the range). Reply compares (rsame_n, wreply_same_n,
  pur_diff_n, wr_first_diff) cover plan/plan_term over nplan below `framed` and plan_test over nplan in the
  whole-reply form; the retired "plan_test past nplan" checks (d27_frame hold_reply, g2 frame_classes) retire
  per r45 §5 (b) and d27's replacement keeps the range check over the count. Gaps found: CHECK-2..4 only.
- Clean controls run by me: checks/kp/CLEAN (SUBJECT kit sources): purity 7874/0, d27 seed 1 x3000 268750/0
  (floors BROKEN at 3000 cases, expected: measured at 20000), G2 gen 0 FAIL / run 5600/0.

CRITIC COMPLETE
