#!/usr/bin/env python3
"""studies/locate_finish/mk_l0_rows.py -- lane lfl0: writes the ten sabotage
rows docs/design/locate_finish.md §5 L0 plans ("New sabotage ids: 10"), each
plant-validated DETECTED at landing (docs/dev/lanes/lfl0_report.md §2.3), once
the manager assigns their ids. The anchors are the L0 tip's text.

    python3 studies/locate_finish/mk_l0_rows.py tests/mech/sabotages S1 S2 ... S10

in the order of the report's §2.3 table (ID1..ID10). Writes
<OUTDIR>/<ID>_<slug>.sh and prints each path; then run
`python3 scripts/m6read_check_sab_anchors.py .` and the rows' mech."""
import os, sys
out, ids = sys.argv[1], sys.argv[2:]
assert len(ids) == 10
def q(s): return "'" + s.replace("'", "'\\''") + "'"
SRC = "src/gen/emit_dfa.c"
EMPTY_ROW = '''    { .c = { "empty", 0, locate_empty_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "empty", .map = CM_NONE, .hands = CT_VERDICT,
      .needs = { [CAND_ROUTE_ATTEMPT] = { .front = CAND_FRONT_DFA } },
      .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_empty_unanchored,
                              [CAND_ROUTE_ATTEMPT] = emit_empty_attempt },
                    .scan = { [CAND_ROUTE_DFA] = "empty", [CAND_ROUTE_ATTEMPT] = "empty" },
                    .nomatch = true } },
'''
COMPOSITE_TAIL = '''                    .scan = { [CAND_ROUTE_DFA] = "unanchored",
                              [CAND_ROUTE_ATTEMPT] = "attempt" } } },
'''
FIN3 = '''    { .c = { "verify-at", 0, finish_verify_at_applies }, .slot = CAND_SLOT_FINISH,
      .routes = CR_DFA, .tok = "unwrapped", .map = CM_NONE,
      .hands = CT_START | CT_VERDICT,
      .list = { [CAND_ROUTE_DFA] = { "match", 1, "unwrapped", PCREC_NO_ANCHORED_DFA } },
      .desc = "the artifact's own ENG_UNANCH _match, and its anchored machine built inside the DFA caps ([ENG-ABS])",
      .needs = { [CAND_ROUTE_DFA] = { CAND_MA } },
      .u.finish = { CAND_FIN_VERIFY, .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT } } } },
'''
FIN4_TAIL = '''                              [CAND_ROUTE_ATTEMPT] = { CAND_HAND_AT, CAND_HAND_NOMATCH } } } },
'''
L0 = "docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md"
rows = [
 dict(slug="locate_order_swapped", suites="candoracle",
  hdr="LOCATE's two rows swapped: `composite` (an undeniable `cand_always` row) is walked before `empty`, so the empty engine's body is the composite's walk and `empty` is never selected.",
  det="tests/codegen/run_cand_oracle.sh: the trace build's self-check aborts `table-not-total LOCATE` (the last row routed on the DFA routes is no longer the undeniable fallback) on every witness. MEASURED by plant at landing: 59 of the oracle's checks fail.",
  desc="LOCATE order swapped: composite before empty, so the empty engine emits a scan; the self-check fails the table as not total",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\B\\\\b" && grep -qF "#define RX_DFA_SCAN \\"empty\\"" "$REACH_TMP/o.c" && echo REACH-EMPTY',
  rexp="REACH-EMPTY",
  file=SRC, before=EMPTY_ROW + "    { .c = { \"composite\", 0, cand_always }, .slot = CAND_SLOT_LOCATE,\n",
  after="    /* SABOTAGE {ID}: empty moved after composite */\n    { .c = { \"composite\", 0, cand_always }, .slot = CAND_SLOT_LOCATE,\n",
  file2=SRC, before2=COMPOSITE_TAIL, after2=COMPOSITE_TAIL + EMPTY_ROW),
 dict(slug="finish_route_misderived", suites="harness", target="tests/lookaround/prefilter.rxt",
  hdr="the path's finisher route misderives every hybrid as a DFA finisher (`cand_finish_of` reads the body bit instead of `fit.chosen`), so the hybrid's INLINED prefilter writes the caller-facing front (the end-window clamp, the pre-check and its handoff, the startpos guard, the dead-group fill) a second time inside the VM's search.",
  det='the corpus harness on tests/lookaround/prefilter.rxt. MEASURED by plant at landing: 34 of 53 cases fail.',
  desc="cand_finish_of misderives a hybrid as a DFA finisher: the inlined prefilter body emits the entry front (W/P/F) twice",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b" && grep -qF "#define RX_VM_PREFILTER \\"hybrid\\"" "$REACH_TMP/o.c" && echo REACH-HYBRID',
  rexp="REACH-HYBRID", file=SRC,
  before="    return cx->job->fit.chosen == ENGM_DFA ? cand_route_of(cx) : CAND_ROUTE_VM;",
  after="    return pcrec_artifact_has_dfa_scan(cx) ? cand_route_of(cx) : CAND_ROUTE_VM;   /* SABOTAGE {ID} */"),
 dict(slug="finish_hand_dropped", suites="candoracle codegen",
  hdr="the match-here entry's FINISH ask drops its hand (asks with 0). A hand is MANDATORY on a FINISH ask (locate_finish.md §2.2): no take cell matches 0.",
  det='tests/codegen/run_cand_oracle.sh: the trace build aborts `finish-no-hand FINISH` at the first FINISH ask, on every DFA witness (MEASURED by plant at landing: 29 checks fail). In the default build the walk selects no row and every DFA compile crashes.',
  desc="the match-here FINISH ask passes hand 0: the hand-mandatory check aborts (trace build), the walk selects no row (default build)",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "#define RX_DFA_MATCH \\"unwrapped\\"" "$REACH_TMP/o.c" && echo REACH-FINISH',
  rexp="REACH-FINISH", file=SRC,
  before="                  .hand = dfa_engine_is_empty(cx) ? CAND_HAND_NOMATCH : CAND_HAND_AT };",
  after="                  .hand = 0 };   /* SABOTAGE {ID}: the hand dropped */"),
 dict(slug="finish_order_swapped", suites="candoracle",
  hdr="FINISH's two rows swapped: `search-from` (undeniable) is walked before `verify-at`, so every DFA artifact's `_match` is the search-filter wrapper and the anchored machine is built for nothing.",
  det='tests/codegen/run_cand_oracle.sh: the self-check aborts (`table-listing-order`: the `match` listing is out of table order; `table-finish-not-total` behind it) on every witness. MEASURED by plant at landing: 59 checks fail.',
  desc="FINISH order swapped: search-from before verify-at, so every _match is search-filter; the self-check fails FINISH's totality",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "#define RX_DFA_MATCH \\"unwrapped\\"" "$REACH_TMP/o.c" && echo REACH-UNWRAPPED',
  rexp="REACH-UNWRAPPED",
  file=SRC, before=FIN3 + "    { .c = { \"search-from\", 0, cand_always }, .slot = CAND_SLOT_FINISH,\n",
  after="    /* SABOTAGE {ID}: verify-at moved after search-from */\n    { .c = { \"search-from\", 0, cand_always }, .slot = CAND_SLOT_FINISH,\n",
  file2=SRC, before2=FIN4_TAIL, after2=FIN4_TAIL + FIN3),
 dict(slug="boundary_projection_dropped", suites="candoracle harness", target="tests/lookaround/prefilter.rxt",
  hdr="the LOCATE -> FINISH boundary projection dropped: `pcrec_cand_lang_exact` ignores the body's recorded erasures, so a SUPERSET hybrid's prefilter span is handed on as the match's SPAN and `Vm.mrl_win` arms the window ceiling over it (the atomic-groups/lookaround match-loss class).",
  det='tests/codegen/run_cand_oracle.sh [cand-oracle-boundary]: the two superset witnesses record `BOUNDARY vm SPAN`, and the RETRY witnesses stop reaching their rows (MEASURED by plant at landing: 7 checks fail); the corpus harness on tests/lookaround/prefilter.rxt loses matches (6 of 53 cases fail).',
  desc="the boundary projection dropped: every hybrid body reads exact, a superset hybrid's trace records BOUNDARY vm SPAN and mrl_win arms the window ceiling",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?>a|ab)c(d)" && grep -qF "#define RX_VM_PREFILTER \\"hybrid\\"" "$REACH_TMP/o.c" && echo REACH-SUPERSET',
  rexp="REACH-SUPERSET", file=SRC,
  before="    return cand_finish_of(cx) != CAND_ROUTE_VM || pcrec_vm_prefilter_window(cx);",
  after="    return cand_finish_of(cx) != CAND_ROUTE_VM || cx->job->fit.prefilter;   /* SABOTAGE {ID} */"),
 dict(slug="retry_raise_removed", suites="candoracle",
  hdr="the RAISE progress class removed from RETRY's re-locate into the prefilter (E7, RETRY -> NEXT): the handoff graph then holds the cycle NEXT -> VERIFIER -> RETRY -> NEXT with no edge that strictly raises the lower bound (O9).",
  det="tests/codegen/run_cand_oracle.sh: the trace build's self-check aborts `table-progress-cycle` on every witness (MEASURED by plant at landing: 59 checks fail). No artifact byte moves: progress classes are data for the check.",
  desc="RETRY's re-locate (E7) loses its RAISE class: the self-check must report a cycle with no RAISE edge",
  reach="", rexp="", file=SRC,
  before="                             .raise = CN(CAND_SLOT_NEXT) | CN(CAND_NODE_VERIFIER) },",
  after="                             .raise = CN(CAND_NODE_VERIFIER) },   /* SABOTAGE {ID} */"),
 dict(slug="membership_rekeyed_to_finish", suites="candoracle codegen",
  hdr="a membership reader re-keyed to the FINISH selection (LR-S1, the shape revision 2 would have built): `dfa_table_name` takes the anchored machine from `dfa_match_is_unwrapped` instead of the path's members. It runs on VM hybrids (`pcrec_emit_dfa_scan_stamps`), where the finisher is the VM and FINISH has no row.",
  det='tests/codegen/run_cand_oracle.sh: every hybrid witness aborts `no-row FINISH` (MEASURED by plant at landing: 27 checks fail); in the default build every forward+reverse hybrid compile crashes (`(a+)b` exits 139).',
  desc="dfa_table_name reads the anchored member off the FINISH selection: every forward+reverse hybrid hits a no-row FINISH selection",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b" && grep -qF "#define RX_VM_PREFILTER \\"hybrid\\"" "$REACH_TMP/o.c" && echo REACH-HYBRID',
  rexp="REACH-HYBRID", file=SRC,
  before="""static const char *dfa_table_name(Ctx *cx)
{
    unsigned m = cand_path_members(cx);""",
  after="""static const char *dfa_table_name(Ctx *cx)
{
    unsigned m = cand_path_members(cx) | (dfa_match_is_unwrapped(cx) ? CAND_MA : 0);   /* SABOTAGE {ID} */"""),
 dict(slug="needs_cell_dropped", suites="codegen",
  hdr="a `.needs` declaration dropped: RECOVER's `reverse-pass` no longer declares the reverse machine, so the path's members lose R and the membership folds skip a machine the artifact carries.",
  det="test-codegen. MEASURED by plant at landing: run_dfa_uniform_fold.sh (250 corpus disagreements), run_premul_table.sh (2), run_search_pinned.sh (480 sweep failures) and run_form_census.sh (the `mixed` witness) all fail. The census's C5-L0 (studies/locate_finish/analyze.py) reads 3,656 disagreements.",
  desc="reverse-pass loses its needs (R): the member folds skip the reverse machine, RX_DFA_TABLE/RX_DFA_UNIFORM_FOLDS read without it",
  reach="", rexp="", file=SRC,
  before="""      .needs = { [CAND_ROUTE_DFA] = { CAND_MR } },
      .u.recover = { .pinned = false } },""",
  after="""      /* SABOTAGE {ID}: the reverse machine's needs dropped */
      .u.recover = { .pinned = false } },"""),
 dict(slug="look_erasure_unrecorded", suites="harness", target="tests/lookaround/prefilter.rxt",
  hdr="the lowering's `A_LOOK` arm stops recording its erasure (LR-G3): a lookaround-bearing hybrid's prefilter reads EXACT, `Vm.mrl_win` arms the window ceiling over a superset's span end, and the 16 qualifying shapes of lookaround_design.md §5.5 lose matches. S140 is the same hazard at the READER (`pcrec_vm_prefilter_window` ignores the record's look member); this row is the WRITER.",
  det="the corpus harness on tests/lookaround/prefilter.rxt (S140's detector). MEASURED by plant at landing: 6 of 53 cases fail. The census's C7 reads 478 disagreements.",
  desc="the A_LOOK arm stops recording its erasure: lookaround hybrids read exact and mrl_win prunes to a superset's window end",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\w{1,2}(?:(?=)|)$" && grep -qF "#define RX_VM_PREFILTER \\"hybrid\\"" "$REACH_TMP/o.c" && echo REACH-LOOK-HYBRID',
  rexp="REACH-LOOK-HYBRID", file="src/ir/nfa.c",
  before="    case A_LOOK:   b->nfa->erased |= NFA_ERASED_LOOK;   /* [OPT-REVEND] L0, LR-G3 */",
  after="    case A_LOOK:   /* SABOTAGE {ID}: the erasure is not recorded */"),
 dict(slug="match_meet_dropped", suites="anchoredmatch",
  hdr="the meet `caller ⊓ body` dropped (LR-G8): the match-here entry asks FINISH for `AT` even on an `empty` body, so `verify-at` is selected wherever the anchored machine was built and the empty engine's `_match` stops being the search-filter wrapper.",
  det="tests/codegen/run_anchored_match.sh: `\\\\B\\\\b` stamps `unwrapped` where the empty engine's documented form is `search-filter`. MEASURED by plant at landing: 4 checks fail.",
  desc="the match-here meet dropped: FINISH is asked AT on an empty body and DFA_MATCH reads unwrapped on empty artifacts",
  reach='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\B\\\\b" && grep -qF "#define RX_DFA_SCAN \\"empty\\"" "$REACH_TMP/o.c" && echo REACH-EMPTY',
  rexp="REACH-EMPTY", file=SRC,
  before="                  .hand = dfa_engine_is_empty(cx) ? CAND_HAND_NOMATCH : CAND_HAND_AT };",
  after="                  .hand = CAND_HAND_AT };   /* SABOTAGE {ID}: the meet dropped */"),
]
for i, r in enumerate(rows):
    ID = ids[i]
    L = ["#!/usr/bin/env bash",
         f"# {ID} ([OPT-REVEND] L0, lane lfl0; {L0}) -- {r['hdr']}",
         "# Detector: " + r['det'].replace('\\\\', '\\')]
    f = {"SAB_ID": f"{ID}-{r['slug'].replace('_', '-')}", "SAB_FILE": r["file"], "SAB_SUITES": r["suites"],
         "SAB_DESC": r["desc"],
         "SAB_DOC_FIGURE": f"Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh {ID}."}
    if r.get("target"): f["SAB_HARNESS_TARGET"] = r["target"]
    if r["reach"]:
        f["SAB_REACH"] = r["reach"]; f["SAB_REACH_EXPECT"] = r["rexp"]
    f["SAB_EXPECT"] = "DETECTED"
    f["SAB_COUNT"] = "1"
    f["SAB_BEFORE"] = r["before"]; f["SAB_AFTER"] = r["after"].replace("{ID}", ID)
    if r.get("file2"):
        f["SAB_FILE2"] = r["file2"]; f["SAB_COUNT2"] = "1"
        f["SAB_BEFORE2"] = r["before2"]; f["SAB_AFTER2"] = r["after2"].replace("{ID}", ID)
    for k, v in f.items():
        L.append(f"{k}={v}" if k in ("SAB_EXPECT", "SAB_COUNT", "SAB_COUNT2") else f"{k}={q(v)}")
    path = os.path.join(out, f"{ID}_{r['slug']}.sh")
    open(path, "w").write("\n".join(L) + "\n")
    print(path)
