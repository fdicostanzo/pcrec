#!/usr/bin/env python3
"""studies/locate_finish/mk_l2_rows.py -- [lane revbuild] writes [OPT-REVEND]
L2's sabotage rows (locate_finish.md §5 L2: revend.md §9.2's sixteen recast,
L2.1's stamp fork, the deference, the size-ladder clause; §5 L3: stage 2's
four), S758-S780, into tests/mech/sabotages/. Each anchor is read off the
CURRENT source and must occur exactly once (else this script stops), so the
rows are written against the text they plant into.

  python3 -I studies/locate_finish/mk_l2_rows.py tests/mech/sabotages
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SRC = {}


def src(path):
    if path not in SRC:
        SRC[path] = open(os.path.join(ROOT, path)).read()
    return SRC[path]


def q(s):
    return "'" + s.replace("'", "'\\''") + "'"


NET = "tests/assertions/rev_end.rxt"
DESIGN = "docs/design/locate_finish.md §5 L2 (revend.md §9.2)"
ROWS = []


def row(sid, slug, file, before, after, suites, desc, detector, reach=None,
        target=None, require=None, site2=None, design=DESIGN):
    ROWS.append(dict(sid=sid, slug=slug, file=file, before=before, after=after,
                     suites=suites, desc=desc, detector=detector, reach=reach,
                     target=target, require=require, site2=site2, design=design))


E = "src/gen/emit_dfa.c"
W = "src/facts/endwin.c"
REACH_WALK = ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\s+$" && '
              'grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK', "REACH-WALK")

row("S758", "revend_seed_nl_dropped", E,
    '               tie ? "    int revend_tie = 0;\\n" : "", eol ? 2 : 1);',
    '               tie ? "    int revend_tie = 0;\\n" : "", eol ? 1 : 1);   /* SABOTAGE S758 */',
    "harness", "the walk's n-1 seed dropped: a `$`/`\\Z` match ending before a final newline is lost",
    "the answer net: `\\d+$` on \"abc123\\n\" and `a*$` on \"aa\\n\" answer NOMATCH or the empty end match", REACH_WALK, NET)
row("S759", "revend_first_seed_not_min", E,
    '               "        if (match_start_position < revend_start) {\\n"',
    '               "        if (revend_start == (size_t)-1) {   /* SABOTAGE S759 */\\n"',
    "harness", "the first accepting seed is kept instead of the smallest start over the seeds",
    "the answer net: `\\s*$|x\\z`, `[^\\n]*\\n?$` and the tie families, where seed n-1 reaches further left", REACH_WALK, NET)
row("S760", "revend_seed_guard_deleted", E,
    '    pcrec_sb_puts(c, "        if (match_end_position < search_from) break;\\n"',
    '    pcrec_sb_puts(c, "        (void)0;   /* SABOTAGE S760 */\\n"',
    "harness", "the `match_end_position < search_from` seed guard deleted: a seed below the startpos walks",
    "the answer net's startpos cells (`\\s*$` from 3 on \"ab\\n\", `b\\z` from 2): a start below the startpos is reported", REACH_WALK, NET)
row("S761", "end_pin_optional_repeat", W,
    '            if (a->u.rep.rmin >= 1) { a = a->l; continue; }\n            return EW_NONE;',
    '            a = a->l; continue;   /* SABOTAGE S761: rmin == 0 keeps the pin */',
    "harness", "`ew_walk` pins an optional repeat (rmin == 0) by its body's view: `(?:a$)?` reads end-pinned",
    "the answer net's D family: `(?:a$)?` on \"b\" must match empty at 0, the walk finds nothing there",
    None, NET)
row("S762", "end_pin_multiline_dollar", W,
    '            return a->u.anch.multiline ? EW_NONE : EW_EOL;',
    '            return EW_EOL;   /* SABOTAGE S762: (?m)$ pins */',
    "harness", "`ew_walk` reads a multiline `$` as end-pinned (decline (4) dropped)",
    "the answer net's D family: `(?m)a$` on \"a\\nb\" matches (0,1), which a walk from n never reaches",
    None, NET)
row("S763", "end_pin_gstart_kept", W,
    '    if (gstart) return PCREC_EPIN_NONE;                   /* (3) */',
    '    (void)gstart;   /* SABOTAGE S763: \\G no longer declines the pin */',
    "harness", "`end_pin` drops the `\\G` decline (3), so `end_window` (its reader) clamps a `\\G` pattern",
    "the answer net's D family (`\\Ga$|b$` at startpos 1) and tests/assertions' `\\G` rows: the window clamp moves the startpos `\\G` reads",
    None, "tests/assertions")
row("S764", "revend_dead_seed_unskipped", E,
    '    emit_reverse_block(c, &rev, "revend", "continue;");',
    '    emit_reverse_block(c, &rev, "revend", NULL);   /* SABOTAGE S764 */',
    "asan harness", "the walk's dead-seed skip deleted (X1): a speculative seed whose state is dead reads `view[row(dead)]`",
    "the answer net's X family under ASan (`\\d+$(?=\\n)` on \"12\": the seed at n is the dead state)",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\d+$(?=\\\\n)" && '
     'grep -q "if (rx_reverse_is_dead(reverse_state)) continue;" "$REACH_TMP/o.c" && echo REACH-DEADSKIP', "REACH-DEADSKIP"),
    NET, "asan")
row("S765", "revend_tie_takes_n", E,
    '                   "        revend_end = revend_start + (size_t)revend_len;\\n"',
    '                   "        revend_end = subject_length; (void)revend_len;   /* SABOTAGE S765 */\\n"',
    "harness", "a tie takes end n without the anchored run",
    "the answer net's lazy ties: `\\s*?$` on \" \\n\" is (0,1), `\\s+?$` on \"a  \\n\"",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\s*?$" && '
     'grep -q "revend_len = rx_match(&revend_ctx)" "$REACH_TMP/o.c" && echo REACH-T2', "REACH-T2"), NET)
row("S766", "revend_tie_takes_n1", E,
    '                   "        revend_end = revend_start + (size_t)revend_len;\\n"',
    '                   "        revend_end = subject_length - 1; (void)revend_len;   /* SABOTAGE S766 */\\n"',
    "harness", "a tie takes end n-1 without the anchored run",
    "the answer net's greedy ties: `\\s*$` on \" \\n\" is (0,2), `\\s+$` on \"a \\n\"",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\s+$" && '
     'grep -q "revend_len = rx_match(&revend_ctx)" "$REACH_TMP/o.c" && echo REACH-T2', "REACH-T2"), NET)
row("S767", "nl_last_overclaims", E,
    '    if (d->s0 < 0 || d->s0 >= d->n) return false;\n    stack[n++] = d->s0;',
    '    return false;   /* SABOTAGE S767: nl_last always false */\n    stack[n++] = d->s0;',
    "harness revend", "`nl_last` answers \"no tie\" for every machine, so a tie-capable walk emits no tie arm",
    "the answer net's tie families (the seed that reached first wins the end) and run_rev_end.sh's tie-arm witnesses",
    REACH_WALK, NET)
row("S768", "revend_route_widened", E,
    '    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,\n      .routes = CR_DFA, .tok = "rev-end", .map = CM_NONE,',
    '    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,\n      .routes = CR_DFA | CR_ATTEMPT, .tok = "rev-end", .map = CM_NONE,   /* SABOTAGE S768 */',
    "harness candoracle", "R2: the row is routed on CAND_ROUTE_ATTEMPT, which has no reverse machine and no walk emitter",
    "an ENG_ATTEMPT end-pinned pattern (`^\\w+$`, `(?m:^)\\w+$`) selects `rev-end`: no emitter on that route (a crash) and the self-check's needs-unrouted",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^\\\\w+$" && '
     'grep -qF "#define RX_DFA_SCAN \\"attempt\\"" "$REACH_TMP/o.c" && echo REACH-ATTEMPT', "REACH-ATTEMPT"), "tests/assertions")
row("S769", "revend_stage1_conjunct_back", E,
    '    return pcrec_fact_end_pin(s->cx) != PCREC_EPIN_NONE;               /* R1 */',
    '    return pcrec_fact_end_pin(s->cx) != PCREC_EPIN_NONE &&\n           cand_finish_of(s->cx) != CAND_ROUTE_VM;   /* SABOTAGE S769: stage 1 again */',
    "revend", "stage 1's conjunct restored: a VM hybrid's inlined body keeps the composite",
    "run_rev_end.sh: the hybrid witnesses `(\\s+){2}$`, `(\\d+)$` read `unanchored`",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\\\d+)$" && '
     'grep -qF "#define RX_VM_PREFILTER \\"hybrid\\"" "$REACH_TMP/o.c" && grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-HYB-WALK', "REACH-HYB-WALK"),
    design="docs/design/locate_finish.md §4.3 (stage 2, D156 addendum 1 Q2)")
EMPTY_ROW_START = '    { .c = { "empty", 0, locate_empty_applies }'
REV_ROW_COMMENT = '    /* [OPT-REVEND] L2 `rev-end` (A2'
_e = src(E)
_i, _j = _e.index(EMPTY_ROW_START), _e.index(REV_ROW_COMMENT)
EMPTY_ROW = _e[_i:_j]
REV_ROW_END = '                    .fin = CT_START | CT_VERDICT | CT_ENDSET } },\n'
row("S770", "empty_after_revend", E, EMPTY_ROW, "    /* SABOTAGE S770: empty moved after rev-end */\n",
    "revend", "R4: `empty` after `rev-end`, so an end-pinned pattern that matches nothing selects the walk",
    "run_rev_end.sh: `[^\\x00-\\xff]$` reads `rev-end` where its body is `empty`",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[^\\\\x00-\\\\xff]$" && '
     'grep -qF "#define RX_DFA_SCAN \\"empty\\"" "$REACH_TMP/o.c" && echo REACH-EMPTY-PIN', "REACH-EMPTY-PIN"),
    site2=(REV_ROW_END, REV_ROW_END + EMPTY_ROW))
row("S771", "revend_deny_unplumbed", E,
    '    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,',
    '    { .c = { "rev-end", 0, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,   /* SABOTAGE S771 */',
    "revend", "the row's deny unplumbed: `-fno-rev-end` is inert (the listing still shows the bit)",
    "run_rev_end.sh: the walk survives `-fno-rev-end` on every walking artifact, and the deny witness reads `rev-end`",
    REACH_WALK)
row("S772", "verify_at_loses_endset", E,
    '      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT, CAND_HAND_ENDSET },\n                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },',
    '      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT },   /* SABOTAGE S772 */\n                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },',
    "revend", "`search-from` takes ENDSET ahead of `verify-at` on CAND_ROUTE_DFA: a tie relocates where the anchored machine exists",
    "run_rev_end.sh: `\\s+$`/`\\s*?$` read the relocate arm where the anchored one is expected",
    REACH_WALK)
row("S773", "dfa_scan_stamp_forked", E,
    '    return cand_locate_of(cx)->u.locate.scan[cand_route_of(cx)];',
    '    if (pcrec_fact_end_pin(cx) != PCREC_EPIN_NONE && cand_route_of(cx) == CAND_ROUTE_DFA)\n        return "rev-end";   /* SABOTAGE S773: the stamp forked from the selection */\n    return cand_locate_of(cx)->u.locate.scan[cand_route_of(cx)];',
    "revend dfastamps", "`<PREFIX>_DFA_SCAN` is a second predicate (the pin and the route), not LOCATE's selection",
    "run_rev_end.sh (the denied build still stamps `rev-end`) and run_dfa_stamps.sh (the stamp against the text)",
    REACH_WALK)
row("S774", "start_absence_forked", E,
    '    [CAND_SLOT_RECOVER] = "attempt-start",',
    '    [CAND_SLOT_RECOVER] = "reverse-pass",   /* SABOTAGE S774 */',
    "dfastamps", "L2.1: RECOVER's absence reads `reverse-pass`, so a path that asks no RECOVER stamps a start recovery it does not run",
    "run_dfa_stamps.sh [start]: `RX_DFA_START` against the text on every attempt/empty artifact",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^ab" && '
     'grep -qF "#define RX_DFA_START \\"attempt-start\\"" "$REACH_TMP/o.c" && echo REACH-ABSENT', "REACH-ABSENT"),
    design="docs/design/locate_finish.md §5 L2.1")
row("S775", "deference_dropped", E,
    '        if (CAND_READ(CAND_SLOT_PRESENCE, CAND_SLOT_LOCATE, &ls, "req-whole")->u.locate.whole)\n            return true;',
    '        (void)ls;   /* SABOTAGE S775: the LOCATE.whole deference dropped */',
    "harness", "PRESENCE no longer defers to a walk that answers presence itself: a pre-check is admitted ahead of the walk",
    "the walk's own assertion refuses the compile (`internal error: a whole-window pre-check was admitted ahead of the rev-end walk`) on every walking pattern with a necessary byte",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "abc$" && '
     'grep -qF "#define RX_REQ_WHY \\"dominated\\"" "$REACH_TMP/o.c" && echo REACH-DOMINATED', "REACH-DOMINATED"),
    NET, design="docs/design/locate_finish.md §4.3 (LR-G6)")
row("S776", "size_ladder_clause_dropped", "src/core/compile.c",
    '           s->cx->job && s->cx->job->anchored_ok &&\n           pcrec_cand_drop_anchored_shrinks(s->cx);',
    '           s->cx->job && s->cx->job->anchored_ok;   /* SABOTAGE S776: LR-S12 dropped */',
    "revend", "the size ladder drops the anchored machine of a tie-capable walk, which then relocates through the composite and GROWS",
    "run_rev_end.sh §3: under a lowered emitted-size cap the tie witness must keep `RX_DFA_MATCH \"unwrapped\"` and no forward machine",
    None, design="docs/design/locate_finish.md §5 L2 (LR-S12)")
D3 = "docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4)"
row("S777", "vm_verify_takes_endset", E,
    '                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },\n      .u.finish = { CAND_FIN_VERIFY } },',
    '                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT, CAND_HAND_ENDSET } },   /* SABOTAGE S777 */\n      .u.finish = { CAND_FIN_VERIFY } },',
    "revtwin revend", "LR-S3: a clamped tie reaches the VM's verify-at, its window end max(D) = n instead of the priority end",
    "the window twin: the lazy tie `(\\s+?){2}$`'s window end differs; run_rev_end.sh's hybrid tie witness loses its relocate arm",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\\\s+?){2}$" && '
     'grep -q "search_from = revend_start;" "$REACH_TMP/o.c" && echo REACH-HYB-TIE', "REACH-HYB-TIE"),
    design=D3)
row("S778", "superset_projected_span", E,
    '    if (cand_finish_of(cx) != CAND_ROUTE_VM || pcrec_cand_lang_exact(cx)) return hand;',
    '    return hand;   /* SABOTAGE S778: no boundary projection */',
    "harness", "a superset body's hand reaches the VM unprojected (SPAN where it is a LOWER bound)",
    "the VM entry's FINISH asks disagree with the window it arms: `\\w{1,2}(?:(?=)|)$` (the answer net's S family) refuses to compile",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\\\w{1,2}(?:(?=)|)$" && '
     'grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-SUPERSET', "REACH-SUPERSET"),
    NET, design=D3)
row("S779", "inlined_locate_on_vm", E,
    '    return pcrec_artifact_has_dfa_scan(cx) ? cand_route_of(cx) : CAND_ROUTE_VM;',
    '    return pcrec_artifact_has_dfa_scan(cx) && cx->job->fit.chosen == ENGM_DFA\n           ? cand_route_of(cx) : CAND_ROUTE_VM;   /* SABOTAGE S779 */',
    "revend", "the inlined body asks LOCATE on CAND_ROUTE_VM, so a hybrid never selects the walk",
    "run_rev_end.sh: the hybrid witnesses read `unanchored`",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\\\d+)$" && '
     'grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-HYB-WALK', "REACH-HYB-WALK"), design=D3)
row("S780", "hybrid_dead_seed_unskipped", E,
    '    emit_reverse_block(c, &rev, "revend", "continue;");',
    '    emit_reverse_block(c, &rev, "revend", entry ? "continue;" : NULL);   /* SABOTAGE S780 */',
    "revtwin", "X1 on a HYBRID: the inlined walk's dead-seed skip deleted",
    "the window twin's trailing-lookaround hybrids (`(\\d+)$(?=\\n)`, `(\\d)$(?!\\n)`, `(a)\\Z(?=\\n)`)",
    ('"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\\\d+)$(?=\\\\n)" && '
     'grep -q "if (rx_reverse_is_dead(reverse_state)) continue;" "$REACH_TMP/o.c" && echo REACH-HYB-DEADSKIP', "REACH-HYB-DEADSKIP"),
    design=D3)


def main():
    out = sys.argv[1]
    for r in ROWS:
        text = src(r["file"])
        n = text.count(r["before"])
        if n != 1:
            sys.exit("%s: anchor occurs %d times in %s" % (r["sid"], n, r["file"]))
        if r["site2"] and src(r["file"]).count(r["site2"][0]) != 1:
            sys.exit("%s: second anchor not unique" % r["sid"])
        lines = [
            "#!/usr/bin/env bash",
            "# %s ([OPT-REVEND] L2, lane revbuild; %s; docs/dev/lanes/revbuild_report.md) -- %s." % (r["sid"], r["design"], r["desc"]),
            "# Detector: %s." % r["detector"],
            "SAB_ID=%s" % q("%s-%s" % (r["sid"], r["slug"].replace("_", "-"))),
            "SAB_FILE=%s" % q(r["file"]),
            "SAB_SUITES=%s" % q(r["suites"]),
            "SAB_DESC=%s" % q(r["desc"]),
            "SAB_DOC_FIGURE=%s" % q("Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh %s." % r["sid"]),
        ]
        if r["target"]:
            lines.append("SAB_HARNESS_TARGET=%s" % q(r["target"]))
        if r["require"]:
            lines.append("SAB_REQUIRE=%s" % q(r["require"]))
        if r["reach"]:
            lines.append("SAB_REACH=%s" % q(r["reach"][0]))
            lines.append("SAB_REACH_EXPECT=%s" % q(r["reach"][1]))
        lines += ["SAB_EXPECT=DETECTED", "SAB_COUNT=1",
                  "SAB_BEFORE=%s" % q(r["before"]), "SAB_AFTER=%s" % q(r["after"])]
        if r["site2"]:
            lines += ["SAB_FILE2=%s" % q(r["file"]), "SAB_COUNT2=1",
                      "SAB_BEFORE2=%s" % q(r["site2"][0]), "SAB_AFTER2=%s" % q(r["site2"][1])]
        path = os.path.join(out, "%s_%s.sh" % (r["sid"], r["slug"]))
        open(path, "w").write("\n".join(lines) + "\n")
        print(path)


if __name__ == "__main__":
    main()
