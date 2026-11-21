# CRITIC CHECKS — r72 memfn-bsu1

## Findings

### CHECKS-1 — the new `skip` column's speed direction has no detector (stop_skip / hors_skip returning -1)
SUSPECTED. Severity: speed (a proved position re-tested; answers unchanged) / check gap. Effort: S (two mech rows) or a ruled "no row" note. Blast radius: every E-find site. window.c `stop_skip` (~4121), `hors_skip` (~4100); ren_search rows' `skip` column.
U1 lifted `skip` from the head renderers' out-parameter into a declared table column. No mech row anchors on it (grep of every SAB_BEFORE for `skip`/`stop_alone`/`plan_ix`: none in window.c; base had none on `*skip =` either, so this is pre-existing, not a regression). The answer-wrong direction (skip an unproved entry) would be caught by the corpus' answers. The speed direction is not obviously caught: G2's exact loop pin (g2_win_gen.c loops_check, ~1280/1890) knows the E-find stop skip only where the stop is a WIDE entry inside a stretch, and explicitly does NOT read D-hors's probe ("D-hors's probe and B-fn's function are not read").
Plants to settle (each SAB_COUNT 1):
 (a) BEFORE `    return ih >= 0 && w->grp[ih] < 0 ? ih : -1;` AFTER `    (void)ih; return -1;   /* SABOTAGE */` — witness `[0-9a-f]{17}` (D-hors per §10.2 cells 17-18), default flags; expect SILENT-MOVE vs subject, then name the suite that reds (I expect none).
 (b) BEFORE `    return w->stop_alone ? w->stop_ix : -1;` AFTER `    (void)w; return -1;   /* SABOTAGE */` — witness `ab[0-9]{26}` (D1, narrow stop: G2's pin cannot see a lone re-test); expect SILENT-MOVE, detector unknown.
If both survive every suite, either a row is owed or the gap is ruled (speed-only mutants are bench-visible only).

### CHECKS-2 — the span form table's order T-deny/T-force ahead of T-lever has no witness
SUSPECTED. Severity: maintenance (test-only lever; no caller combines them). Effort: S, or a "no row: no population" note. window.c wf_spanrows / §3's rule "T-deny, T-force and T-lever stay ahead of every later row".
Every detector exercises one state at a time: G2's default pass sets opts (deny/force) with no lever, its head passes set the lever with opts NULL (g2_win_gen.c ~1400, "in a head pass, the pass's head"); cards.py arm I is the deny alone, H(n) the lever alone (cards.py:233/237); §10.2's T-table cells 17-20 put lever/force ahead of V, not deny ahead of lever. So a first-match ORDER defect among the escape rows is invisible. CONFIRMED that the combination moves bytes: plant:S3281 vs subject on `[0-9a-f]{32}` with `PCREC_BIN=harness --harness=span-head=5 --memfn=no-span-loop` = SILENT-MOVE (2 lines) — exactly what an order plant would emit.
Plant to settle: BEFORE `static int s_deny_holds(const wf_sx *x)  { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) < 0; }` AFTER `static int s_deny_holds(const wf_sx *x)  { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) < 0 && !(x->d->art && (x->d->art->levers & KIT_LEVER_SPAN_HEAD)); }   /* SABOTAGE */`; witness above; expect SILENT-MOVE vs subject and no suite red. Pre-existing (base's if-chain order was equally unwitnessed), but U1 made it a declared first-match property, and U2 adds rows below it.

## PROBED-AND-HELD
Compiles: 50 (cap 400). Witnesses: `[0-9a-f]{32}` (32 positions), `[0-9a-f]{4}[g-z]{4}` (8), `[0-9a-f]{100}` (100), `x[0-9a-f]{80}y` (82). MIN witness length 8, MAX 100 positions (the CLI states offsets to width 32 only).
Sub-part 1, plant compares (PCREC_BIN=harness where a lever is used; every emitted header `Pattern:` checked on the S3278 pair):
- S3278 `--memfn=span-loop` on {32}: plant vs subject SILENT-MOVE (2 lines); plant vs base-S3278 SAME; plant(force) == subject(default) SAME in byte AND utf8, so memfn_arm.py's `span-loop=force` DIFFER cell (witness `[0-9a-f]{32}` c-default) loses its witness: detector reaches.
- S3279 lever 5: vs subject SILENT-MOVE (2); vs base-S3279 SAME.
- S3280 lever 5: vs subject SILENT-MOVE (2); vs base SAME. Also at force (head 0, where the plant now ALSO moves wf_stretches' head-0 enumeration: the offset-0 entry is no stretch start): vs subject SILENT-MOVE (2), vs base-S3280 SAME — the enumerator side-effect is byte-neutral (the stretch re-starts at entry 1, exactly the base plant's loop).
- S3281 lever 5 + `--memfn=no-span-loop`: vs subject SILENT-MOVE (2); vs base SAME. Its G2 detector (long rows under the deny, default pass, no lever) reaches by code reading: deny not holding -> T-head H(64) -> loops on k 500/1024.
- S3282 lever 5: vs subject SILENT-MOVE (2); vs base SAME.
- S3276, S3283 (force and lever 5 on {32}): SILENT-MOVE (2) each. S3277 (force and lever 1 on the mixed 4+4): SILENT-MOVE (2) each; its plant also widens the enumerator's k across the set boundary, consistent with wf_loop_len's own (planted) reading: one effect, not two.
- S3284, S3285: SAME vs subject on {100}, x{80}y (default, force, lever 64) — EXPECTED: the CLI states no offset past 32, and both rows declare G2's window family (library-level, k 500/1024) as detector. S3285's anchor `enum { WF_SPAN_HEAD = 64 };` is still read by T-head's `s_head_h`; S3284's by wf_loop (unchanged). Reach not provable from the CLI here; it is the g2win arm's.
- No LOUD compare anywhere.
Sub-part 2, U1's new decision points:
- enumerator guards `(int)i == w->skip || w->grp[i] >= 0` in wf_stretches: EQUIVALENT mutants (wf_loop_len(w,i,0) breaks at j == i on the same two conditions and returns 0), so no row is possible or owed.
- wf_test_to's `i < end` guard: EQUIVALENT (an entry outside every stored stretch has wf_loop_len(head 0) == 0, hence 0 at every head >= 0). The live reads are `.i == i` and `.h`; dropping `.h` (head stays INT32_MAX) kills every loop -> G2's exact pin and head-pass loop floors red (S3279's behaviour). Per-STRETCH h is unobservable at U1 (every row reads plan/site facts, so all stretches of a plan share h); first observable at U2 (§10.2 cell 16). Held.
- enumerator `i += k - 1` (no row): dropping it loses every later stretch's match (mixed family's second stretch goes lone) and overruns the n/2+1 list; G2's mixed-stretch exact pin should red. Covered behaviourally (SUSPECTED-covered; a REACH row is optional). The n/2+1 capacity itself is exactly sufficient (disjoint stretches of k >= 2).
- order `w->skip` set before wf_stretches in wf_find_prepare: only a stretch STARTING at the skipped entry would move; covered by G2's E-find stop pin where reachable. No row owed.
- wf_tables_check's new span-row line: same shape as Table E's hole line, which has no row either (a static-initializer self-check; deleting it is equivalent on today's table). Held by precedent.
- T-head / WF_SPAN_HEAD: covered by S3285 (anchor still read). s_head_holds -> 0 is self-LOUD (kit_walk returns WF_NSROWS -> -1).
- skip column: CHECKS-1. Row order: CHECKS-2.
Decider census: decider_census.py writes only tempdirs under $TMPDIR (read before running; TMPDIR=my lens dir). Subject: 102 passed, 0 failed, backstop hits 68; base (--no-plants): hits 67, 0 failed. Re-derived independently (my own grep with the script's BACKSTOP list over memfn/src): the ONLY new hit line is `size_t r = kit_walk(&wf_spantable, ...)` in wf_stretches (67 -> 68); map rows 70 -> 72 (wf_stretches fn, wf_spanrows data). Both numbers HOLD. `wf_spanrows[` is not a backstop shape, consistent with `wf_erows[` (Table E) — a direct row read outside a member would be invisible, as it already is for Table E.
`python3 -I -B scripts/m6read_check_sab_anchors.py` in the review tree: "sabotages checked: 1368 (1426 anchor sites) / all anchors resolve". S2982's anchor (RB_PAIR first line) unchanged.

CRITIC COMPLETE
