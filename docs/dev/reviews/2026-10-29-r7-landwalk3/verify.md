# crit-landwalk3 VERIFY (opus), 2026-10-29

Subject: docs/dev/lanes/p1dsg3_report.md @ cdb5717d9 (copy: verify/subject.md). Code read in
worktrees/crit-landwalk3 (main ffb9254cb), src/gen/emit_dfa.c unless named. Probe dir
verify/. Compiles: counted per section (total at the end). Nothing run after 19:00.

## FIX-1/SOUND-1

**Verdict: HOLDS (both), and they are two layers of ONE defect. FIX-1 happens first; SOUND-1
is what is left after FIX-1's cheaper fix. §Size's member claim fails as written.**

What the subject says (checked): §A2's LOWER row: "composite's cells (NEXT, RECOVER) and
`CAND_MF` join the path"; Build plan step 4 lists the walk row's fields as `.c.deny`, `.needs {
CAND_ML | CAND_MA, 0, PRESENCE }`, `.whole`, `u.locate.gives[]`. `gives[]` replaces `fin` only;
no `.recover` is named anywhere for the walk, so it is 0 (unstated).

The chain, traced myself:
- `cand_path_of` (:11928) visits LOCATE = the walk; its `.needs` cells are 0, so nothing is
  visited from it. Then `cand_locate_hands` gives LOWER and `cand_path_finish(..., reloc =
  p.finish)` (:11943). With search-from's new DFA LOWER cell, `act == CAND_FIN_SEARCH`, `hand !=
  AT`, so it visits the FALLBACK's cells (:11902-11904): composite DFA cells = NEXT | RECOVER
  (:10225).
- `cand_path_visit(RECOVER)` marks RECOVER asked (:11882) BEFORE selecting, then `cand_path_row`
  (:11847) -> `dfa_search_start_of` (:9708) -> `dfa_search_start_at(cx,
  cand_locate_of(cx)->u.locate.recover)` = hand 0 -> `cand_select`: every RECOVER row is a
  handed slot and `cand_takes` (:10647, "A 0 hand matches no cell") refuses hand 0 BEFORE any
  predicate runs (:10729). Result NULL. In the quiet derivation `cand_hit_as` returns early and
  `PCREC_CAND_TRACE_REC` does not evaluate `row` (internal.h:9316), so the derivation survives
  with `p->recover = NULL` and `CAND_MR` never enters `p.needs`.
- First non-quiet reader: the stamp rule. `dfa_search_start_name` (:9715): `cand_stamp_absent`
  returns NULL because the path ASKS RECOVER, then `dfa_search_start_of(cx)->tok` on NULL. Same
  for `rx_info.search_form` (:3426) and, if the relocated block reuses composite's emitter,
  `emit_unanchored`'s `rr->u.recover.act` (:13328-13329). Release: NULL dereference. Trace
  build: `cand_hit_as` traps `recover-no-hand` (:11512) before the deref. The one reader that
  does NOT crash is `emit_orientation_block` (:14983): it gates on `cand_recover_asked` first
  and takes CRA_REVERSE.

SOUND-1 is real but LATENT behind FIX-1: the `cand_recover_asked` gates (:9613 P4, :9648 W0,
:9667 L0', :9741, :14983) are never reached while the hand is 0, because `cand_takes` filters
first. It becomes the behaviour as soon as FIX-1 is fixed, by EITHER of FIX-1's options:
- FIX-1 option (b) (`.recover = CAND_HAND_EXISTS` on the walk): the predicates still read the
  SELECTED row's cells (`cand_recover_asked`, :11817), which name no RECOVER, so pinned /
  end-minus-width / landing decline and RECOVER is `reverse-pass`.
- FIX-1 option (a) (the closure keyed by the fallback row): fixes only `cand_path_of`. The
  stamp, `rx_info` and emitter readers call `dfa_search_start_of` directly, not through the
  path, so they still ask hand 0 and still crash. **Correction to FIX-1: option (a) alone is
  insufficient**; it must re-key `dfa_search_start_of` (the reader every RECOVER consumer
  shares), not only the closure.
So the one defect is "a RECOVER cell reached by relocation reads two fields off the SELECTED
LOCATE row (`u.locate.recover`, `.needs[].cells`) instead of the row whose cells were visited".
The complete fix touches both reads: `dfa_search_start_of` and `cand_recover_asked` read the
relocate target's (composite's) `recover` hand and RECOVER cell on a relocating LOCATE row, or
the walk row declares both (`.recover = EXISTS`, and RECOVER in a cell set that does not put
RECOVER on the walk's own front) — the first is the general form.

Reachability of SOUND-1's speed loss (9 compiles; stamps quoted here):
the three stage-1 bench rows are `reverse-pass` today (`a+b`, `(*UCP)a\sb -e utf8`:
`RX_DFA_START "reverse-pass"`), so no bench row moves. A user-reachable witness exists:
`[a-z]{40}@x -fno-req-handoff` stamps `RX_DFA_SCAN "unanchored"`, `RX_DFA_PREFILTER
"byte-class"`, `RX_DFA_START "end-minus-width"` today; it passes rows 1-8 by hand (DFA, `@`
top-level, one branch, `@` not in [a-z], NEXT_cf byte-class), so if admitted its LOWER relocate
would run `reverse-pass` instead of `end-minus-width`. Severity: FIX-1 is design (a crash on
every admitted compile, since every admitted compile has the LOWER hand in `gives[]`, so it is
on the path whether or not it fires at run time); SOUND-1 speed, small blast radius (fixed-width
P only, behind default-off flags or cover declines).

§Size's member claim `{ML, MA, MF, MR} -> {MA, MF, MR}` FAILS as written. Under today's
derivation with rev 2's row, the walk path's members are `{ML, MA, MF}` (MR is lost with the
NULL RECOVER); the drop's composite path is `{MA, MF, MR}`; after ⊄ before (MR is new), so
"dropping it always shrinks the members ... without a shrink test" is unproven. After FIX-1
option (b) without SOUND-1's fix it holds (reverse-pass on both sides). After the full fix it
also holds, but as `{ML, MA, MF, X} -> {MA, MF, X}` with X = the same RECOVER row's needs on both
sides (MR only for reverse-pass). The claim should be stated as "the walk's members minus ML",
conditional on the RECOVER read being the relocate target's.

## SOUND-2

**Verdict: HOLDS (speed, quadratic, only under `-e utf8 -futf-check`).** The subject says what
the finding says: Disposition SLOT-10 and Build plan step 4 recommend "a call to
`<prefix>_match`", justified only by "the seed ask and the `_match` entry's caller ask select the
same row (`verify-at`) under the same availability". Nothing in rev 2 mentions the caller
prologue.

Structural check (2 compiles: verify/u.c = `[a-z]+@x -e utf8 -futf-check`, verify/n.c = same
without the check): emitted `rx_match` (u.c:274) runs the K50 startpos guard and then
`rx__valid_upto(subject, subject_length, search_from)` (u.c:287), which walks from `pos` to `n`.
n.c's `rx_match` has no such call (only the definition and the public `rx_valid_upto`).

Twin (mine): verify/seedtwin.c includes the emitted source and calls `rx_match` at s* = j-2 for
every `@` of "ab@" x N (every verify fails, as on a dense no-match subject). `perf stat -e
instructions:u`, `taskset -c 7`, under watchdog (verify/seedtwin.txt):

| N (hits) | -futf-check | without |
|---|---|---|
| 10,000 | 152.2M | 1.58M |
| 20,000 | 604.4M | 3.04M |
| 40,000 | 2,408.6M | 5.96M |

Doubling the hits quadruples the instructions with the check (x3.97, x3.99) and doubles them
without: O(hits·n). The SOUND critic's wall-time table agrees in shape.

Corrections: (1) the K50 guard per hit is O(1) and harmless; only the validation matters.
(2) There is no prologue-free anchored entry today (`rx_match` inlines A after the prologue;
`rx__find` is the SEARCH internal), so SOUND-2's second fix is a new internal entry, which is
itself an emitted-scaffolding change in the same abi event; the inline form avoids it. Either is
small. The acceptance net needs a utf8 `-futf-check` row (T6's shape) as SOUND-2 says.
Severity: speed (quadratic) as stated; blast radius narrower than "every admitted pattern" —
only artifacts built with `-futf-check` (opt-in; the K50 guard alone is constant).

## FIX-2/SOUND-4

**Verdict: HOLDS (maintenance, trace build; one finding, two names). FIX-2's CONFIRMED is
right; SOUND-4's SUSPECTED can be upgraded.** The subject says it: §The NEXT read cycle "The
memo also holds the start set NEXT_cf's row proves (`cand_row_scan`, as `req_start_set` reads
it), which is L8's `m`", and §Checks row `table-read-unasked`/`table-ask-unread`: "no new kit ask
(the asks inside the fill are NEXT's and PRESENCE's own, already declared)".

Traced (no compile needed):
- `cand_row_scan` (:8367): on a PF_SCAN_BYTE/SET row (memchr, byte-class: all three stage-1
  admitted rows) it calls `cand_ask(cx, reader, ...)` (:8382), whose trace half is
  `cand_ask_check(reader, CAND_SLOT_NEXT, route, flags)` (:8307), plus
  `CAND_ASK_FIELD(reader, EXISTS)` and `(reader, PROVEN0)`.
- `cand_ask_check` (:11609) traps `undeclared-ask` unless `cand_nodes[reader].kask[NEXT]` has
  the route; `cand_ask_field` (:11623) traps unless `kfields` has the field.
- Declared kask today: PRESENCE (:9960), NEXT (:10003-ish block, `kask[NEXT]=DFA`), RETRY,
  RECOVER. LOCATE declares none, and rev 2 adds only `reads`/`under`/`by` ("3 fields").
- `req_start_set` (:8979) passes `CAND_SLOT_NEXT` legitimately: its one predicate caller is
  NEXT's own `pf_handoff_applies` -> `req_landmark_admits` (:9048, :9022). NEXT_cf's SELECTION
  makes no start-set ask (the selection never calls `cand_row_scan`), so the memo's start set is
  an ask made for L8, i.e. by LOCATE. "The asks inside the fill are NEXT's own" is false for it.
So the build either passes LOCATE and traps (`undeclared-ask`, then `undeclared-ask-field`), or
copies `req_start_set`'s literal NEXT and passes under a wrong label — the check then holds a
reader the checked code names, which learnings §3 forbids.

Fix as FIX-2 states it is correct: `cand_nodes[LOCATE].kask[NEXT] = CAND_ON(DFA)`, `kfields =
EXISTS | PROVEN0` (5 fields, not 3); `table-ask-unread` (:11280, kask ⊆ reads) then passes
because rev 2's `reads[NEXT] = DFA`, and the kask edge lies inside the read graph, so
`table-read-cycle` is unchanged. FIX-2's `ask-while-open` caution is right but mild: want =
flags | LOCATE.under[NEXT] = F|NO_LW; any ask after the fill's `cand_select(NEXT)` has returned
has no open NEXT(F|NO_LW) frame. Severity: maintenance (trace build only; no answer, no byte).

## FIX-3

**Verdict: HOLDS (maintenance; trace-build invariant on a reachable sequence).** The subject's
§Size reader list is, verbatim: `COMPILE_MAX_ATTEMPTS`' formula and comment;
`fit_tables_selfcheck`; `axes_dump.c`, `run_fallback_table.sh`, `limits_check.sh`; limits.md
§8.4. It names no FitAct, no sequence table, no act text; the rung's SHAPE names `.deny`,
`.sets`, `.applies`, `.on`, `.degrading`, `.note` only.

Traced in compile.c:
- `fit_seq_legal[]` (:1794-1815) holds `{DROP_ANCHORED, DROP_PREMUL}` and the END_MARK /
  COLLAPSE / HANDOFF pairs; `fit_record` (:1853-1872) asserts `fit-sequence` in the trace build
  for every ATTRIBUTING row (esel cells not both PASS). Every PF-DROP rung today attributes
  `{ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY}` (drop-anchored :1362, drop-premul :1373,
  drop-handoff), and S238 (`size_drop_unstamped`) exists to hold that a size drop stamps, so the
  new rung must attribute too.
- Reachability of `{DROP_LW, DROP_ANCHORED}`: the LW rung keeps SDR (`FIT_SDR_KEEP`, rev 2), so
  `fit_anchored_applies` (`size_drop_rung == SDR_NONE && anchored_ok && drop_anchored_shrinks`)
  can fire on the walk-dropped retry when the composite artifact is still over the cap. Not
  listed -> `fit-sequence` fails. `{DROP_LW, DROP_PREMUL}` likewise (`fit_premul_applies`:
  `size_drop_rung < SDR_NO_PREMUL`, DFA). Both pairs are needed.
- Checked and NOT needed (a refinement of FIX-3): `{COLLAPSE, DROP_LW}` — `fit_collapse_applies`
  requires `fit.chosen != ENGM_DFA`, and row 1 `finisher-dfa` needs a DFA finisher, so the two
  never meet; `{DROP_END_MARK, DROP_LW}` — `fit_end_mark_applies` requires `revend_form ==
  RF_TAGGED` (rev-end selected), and the end-mark-dropped retry still selects rev-end, which
  outranks the walk. Neither is reachable as far as I can trace.
- Other readers FIX-3 names, confirmed present: the `FitAct` enum (:866-869, a new value), the
  recovery switch's retrying case list (:2552-2555, a `-Wswitch` hit anyway), `fit_act_text`
  (:1658), `docs/design/dec_fallback.md` §1.7 row table (:269) and `dec_fallback/row_reach.py`
  `SIZE` tuple (:67), and the `engine-route` order-7 desc on `prefilter-collapse` (:1349, which
  lists "dropped the optional anchored machine, the premultiplied table or the prefilter").
  Also present and unnamed by either: mech sabotages S636/S637 (drop-anchored SDR / note) and
  S238 — not broken by an insertion, but they are the rung row's existing controls and the new
  rung needs its own S238-shaped row.
Fix as stated (two pairs, the act, the readers). Severity unchanged: maintenance.

## FIX-4

**Verdict: HOLDS (compile cost + listing under the deny; no answer, no emitted byte).** What
rev 2 actually says about the gate:
- §Admission "Shape": "The deny is the row's `.c.deny = PCREC_NO_LANDMARK_WALK` ... read by
  `cand_select`. Rev 1's L0 `denied` row is DELETED."
- §Mechanism "Where and when it is built": "Only where every PRE row passes. The gate evaluates
  the PRE phase with LOCATE on the eval stack ... A pattern where `rev-end` or `cover` outranks
  the walk can still pay for an ML build, because the gate does not read LOCATE."
- §The NEXT read cycle: "The compile-time PRE gate runs the walk row's PRE phase through
  `cand_applies`"; "the bit has exactly one selection reader, the walk row's `.c.deny`
  (`cand_select`)".
Nothing says the gate tests the deny. In code, the deny is tested only in `cand_select`
(:10727, `pcrec_flags_has(flags, r->c.deny)`); `cand_applies` is the predicate alone (release
macro: `(r)->c.applies(s)`; trace: the stack wrapper). So the PRE rows 1-9 (memo fill
included) run, and ML is built, under `-fno-landmark-walk` and on every `drop-landmark-walk`
retry (whose `sets` ORs exactly that bit). ML is not on the path there (the walk is not
selected), so the artifact still sheds it: the rung's SIZE purpose survives, but its compile
cost does not, and a deny flag that leaves a C1 `lmwalk-cf` record and facts `used` moves behind
is not inert.

Precedents confirmed: `pcrec_revend_form_asked` (emit_dfa.c:13525) gates `revend_choose_form`
(compile.c:3104) on `cand_locate_of` (deny honoured through `cand_select`), and
`build_anchored_dfa` reads `PCREC_NO_ANCHORED_DFA` itself (compile.c:387). Fix as FIX-4 states:
the gate tests `.c.deny` first, named as the bit's BUILD reader beside its one SELECTION reader;
the counterfactual argument ("exactly one selection reader") is untouched, because the fill
sets the bit and the gate must not run inside a fill anyway. Severity: size/compile-cost +
listing, as stated; effort trivial.

## FIX-5/SOUND-3

**Verdict: HOLDS (listing/doc; one finding, two names). FIX-5's SUSPECTED upgrades to
CONFIRMED for `run_pin` by code + proxy; FIX-5's six-fact list overstates it.** The subject
says, §Checks row "`--emit-facts` used record": "the fill marks NEXT's facts used | the same
facts as the walk-off compile (the lemma: same NEXT row); no mover expected". The lemma covers
ADMITTED patterns only; §Mechanism itself says the gate runs where `rev-end`/`cover` outrank the
walk, and there today's compile makes no NEXT selection at all.

Evidence (5 compiles, `--emit-facts`, verify/facts1-5.txt):
- `[a-z][a-z]@x` (`cover`): `run_pin used no`; with `-fno-anchored-dfa` (composite, NEXT
  `run-pinned`): `run_pin used yes`.
- `c[ac]t` (`cover`): `run_pin used no`; `--memfn=no-window-search`: `yes`.
- `[a-z]+@x$` (`rev-end`): `run_pin used no`.
Mechanism: the fill is a `cand_select(NEXT)` for the forward machine. NEXT's first two rows are
`run-pinned-bounded` / `run-pinned` (:10327, :10335); `pf_run_applies_common` (:7335) reads
`req_run` and, where `us.kind != DFA_PF_NONE` and `req_run.len >= 2` (both witnesses: `@x`,
`c[ac]t`'s 3-byte run), `us_run_pin` -> `pcrec_fact_run_pin` (facts.c:598), whose accessor sets
`pf->used` (facts.c:128). Rows 1-7 pass by hand on `[a-z][a-z]@x` (DFA; A built — cover's C4
needs it; `@` top-level, P non-empty; one branch; `@` not in [a-z]), so row 8 fills there.
So walk-on flips `run_pin` to `used yes` on cover/rev-end artifacts.

Correction to FIX-5: the other five facts in its diff (`end_window`, `width`, `req_set`,
`req_whole_run`, `req_landmark_maxoff`) also move in my `c[ac]t` diff, but that diff is the
whole composite path (emitters, pre-check builder), not the fill's one NEXT selection. Only
`run_pin` is shown to be read by the selection itself; the rest need the trace build, as FIX-5
says.

Precedent confirmed: `req_pres_proof_quiet` (:10828) saves and restores `cx->job->pf.used`
around a re-read "so the trace stream and `--emit-facts` stay the admission's own", and
facts_listing.md §4.1¶2 exempts `cover`'s admission read from `used`. §4.1's `used` column is
PROMISED ("yes — a compiler pass asked for the fact while the artifact was built"), so the fill
either restores `pf.used` (the precedent; recommended, since the fill is a counterfactual read
whose world was not built) or the build carries a §4.1¶2 hunk and declares the mover. Severity:
listing/doc (spec-visible column), effort trivial. Note FIX-4 interacts: while the gate ignores
the deny, `-fno-landmark-walk` compiles move too.

## FIX-6

**Verdict: HOLDS (maintenance; the trap as worded would fire on every RECOVER selection).** The
subject says (§A2 "The asker"): "0 is UNSTATED, and `cand_takes` traps it in the trace build",
and "`cand_takes`: FINISH takes AT iff `s->asker ∈ r->u.finish.at_askers`". The trap is not
scoped to FINISH; the AT rule is.
- `cand_takes` (:10647) runs for every handed slot: `cand_select` calls it when `CN(slot) &
  CAND_HANDED_SLOTS` (:10729), `CAND_HANDED_SLOTS = FINISH | RECOVER` (:10642).
- RECOVER's selections build `CandSel` without `.point`: `dfa_search_start_at` (:9694). Under
  `point -> asker` that is asker 0, so an unscoped 0-trap fires on every RECOVER ask in the
  trace build (every DFA compile with a composite body).
- RECOVER's totality check sets `.point = true` (:11450) for a LOCATE row's walk ask: under the
  rename that reads as CALLER, which is the wrong asker by rev 2's own taxonomy.
- `CAND_HAND_WINDOW` is `CAND_HAND_AT` numerically: `cand_hand_alias` (:11202) spells `AT` as
  `WINDOW` on RECOVER. So the asker test must stay gated on `r->slot == CAND_SLOT_FINISH`
  exactly as today's `point` test is, or a RECOVER `WINDOW` ask would be held to `at_askers`.
- Site count: 7 explicit `.point` sites (:10769, :10780, :10802, :11417, :11450, :13601,
  :13631) plus `cand_path_finish`'s parameter and its call sites (:11933-11944); "about 17"
  holds only counting implicit initializers. Mechanical either way.
Fix as stated: scope the 0-trap and `at_askers` to FINISH and say so (simplest), or give
RECOVER's sites BODY explicitly. Severity: maintenance, trivial.

Aside, relevant to FIX-1: RECOVER's totality check skips LOCATE rows with `!lr->u.locate.recover`
(:11447). So the walk row's unstated 0 hand is INVISIBLE to `table-recover-not-total`; no
existing self-check catches FIX-1, which is why it needs the explicit field or the re-keyed
read (and a sabotage/control row).

## FIX-7

**Verdict: HOLDS (maintenance, trivial), with one detail REFUTED.** The subject says (§A2): "`fin`'s
one reader is `cand_locate_hands` (grep: 3 lines)". In `src/` that is true (emit_dfa.c
:10793-10795 are the only `u.locate.fin` reads). But two mech sabotages carry the field's
SPELLING as plant anchors:
- `tests/mech/sabotages/S770_empty_after_revend.sh` :20/:36 (`.fin = CT_VERDICT`), :26/:28
  (`.fin = CT_START | CT_VERDICT | CT_ENDSET`);
- `tests/mech/sabotages/S738_locate_order_swapped.sh` :22/:38 (`.fin = CT_VERDICT`), :28/:30
  (`.recover = CAND_HAND_EXISTS, .fin = CT_START`).
Their `SAB_BEFORE`/`SAB_BEFORE2` text must match the source exactly; once `gives[]` replaces
`.fin` on all four LOCATE rows, neither plant applies, so both need re-aiming in the build
commit (mech would report them as not applying, not as silently passing, so the risk is a red
matrix, not a lost control). Not readers of the value, but readers of the text — the "found by
grep" rule should grep `tests/` too.
REFUTED detail: `tools/review/out/literal_census.tsv` has no `.fin`/`CT_*` row (grep: only an
unrelated `PCREC_ARTIFACT_ABI` line matches "fin"); it is not a reader.

## FIX-8

**Verdict: HOLDS (doc, low).** The rank check (`cand_path_selfcheck`, the loop ending at the
`table-progress-rank` fail) today reads `if (!fb || rt == CAND_ROUTE_VM) continue;` and then
fails a FIN_SEARCH take hand `h != AT` with `!(h & ~fb->hands)`. Rev 2 (§Checks
`table-progress-rank`, §A2 "`u.locate.gives[]` is a 0-terminated list of `{ hand, asker }`")
gives `gives[]` no route dimension, and its rank row says nothing about the VM skip (the
totality row does say "CAND_ROUTE_VM keeps its hand list").
- Today on VM: `search-from` VM takes {ENDSET, LOWER} (rev 2's own §A2 list), composite
  `.hands = CT_LOWER`; without the skip the LOWER cell would fire (`CT_LOWER & ~CT_LOWER ==
  0`), so the skip is what keeps the check green on VM today.
- Amended operand without the skip: LOWER, ENDSET ∉ composite's `gives[] = {SPAN}`, so VM
  would PASS — vacuously, since composite's DFA-body SPAN hand does not describe the VM search
  entry (on VM `search-from` IS the search entry, E-FC/the projected hand, not a relocate to
  composite).
So the skip stays load-bearing semantically, and a build that "simplifies" it away under the
new operand would turn a false-positive guard into a silent pass. Rev 2 does not propose
removing it, so this is a one-sentence doc fix to the §Checks row ("the VM route stays skipped:
its FIN_SEARCH row is the entry, not a relocate"), not a design defect. Severity: doc, as stated.

## Cross-cutting notes

- Ranking of what survives: FIX-1 (design: a NULL selection on every admitted compile, and
  invisible to `table-recover-not-total`) > SOUND-1 (speed, latent behind FIX-1, survives
  either FIX-1 option) ≈ SOUND-2 (quadratic speed, `-futf-check` only) > FIX-4, FIX-5/SOUND-3
  (compile cost / listing) > FIX-2/SOUND-4, FIX-3, FIX-6, FIX-7 (maintenance, trace build or
  mech) > FIX-8 (doc).
- None is ANSWER-level: no libpcre2 twin was owed. No finding contradicts a MANAGER RULING of
  r1/r5; each is a fix-induced gap in rev 2's application of an accepted disposition (SLOT-2,
  SLOT-3, SLOT-6, SLOT-8, SLOT-10, SLOT-1/SLOT-5).
- Budget: 16 pcrec compiles (2 seed-twin; 6 RECOVER-stamp probes, 3 patterns x 2 encodings; 3 fixed-width;
  5 facts listings), 2 gcc builds, 6 twin runs; all before 19:00, one process at a time.

VERIFY COMPLETE
