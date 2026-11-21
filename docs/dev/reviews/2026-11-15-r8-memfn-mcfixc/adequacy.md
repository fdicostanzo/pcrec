# adequacy (crit-memfn-mcfixc)

## Findings

### ADQ-1 (CONFIRMED, maintenance/design, low; effort S; blast radius J4 only, not tonight's mfcard window) — the null base is keyed, its paired verify arms are not
link.py:211-233. `timed_form` keys J4's cell-less null bases `null` (no callee) and its docstring says "never an unkeyed,
silently looser check", but the 28 cell-carrying J4 verify arms they are subtracted from (settest x12, rc-words x12,
rc-memcmp x4) still key to forms no TIMED_CALLEES row names, so `timed_callees` returns None = ANY external (the r5 rule
the table's header comment keeps for "the s2d jobs' verify/enter forms"). Repro: py/arm_keys.py (plan.build() over every job,
each arm through render's fc rule + timed_form/timed_callees): `J4 12 verify settest fc settest callees None`, same for
rc-words / rc-memcmp; `J4 7 verify null -> timed_form null`. So in J4 the SUBTRAHEND is held strict and the MINUEND loose:
a verify arm whose compare went to an out-of-line external (rc-memcmp -> memcmp, the case pcrec may inline) is timed
with a call per candidate, and the null base (compare removed) cannot carry the same call, so the delta absorbs the call
cost unrefused. Not a regression (pre-existing r5 exemption); the fix diff makes the asymmetry newly visible. Fix: give
settest/rc-words/rc-memcmp rows (their dry-run callees, as r6 did for libc/pair/walk), or state in the table comment that
J4's verify forms are deliberately unkeyed and why the null base differs. Tonight's jobs (JMB, JMH, J2, J2p) are all
keyed (see PROBED-AND-HELD).

### ADQ-2 (CONFIRMED, answer on the SECOND window, design; effort S; blast radius D197's verdict when a re-run happens) — no staged job can reach second-ness
Jobs: 609 calls `d197_rule.py rule "$RUNDIR" "$RUNDIR.avx2libc"` (no flag); 610 calls `rule "$RUNDIR" "$RUNDIR.avx2libc"
--confirm "$CRD" "$CRD.avx2libc"` (hard-coded); common.sh/609/610 contain NO `--second` anywhere (grep). The CLI parses
--second correctly (drill + my probe), but D197's "a second INCONCLUSIVE is NOT-WIN" (d197_rule.tsv:108-109) is reached
ONLY if a person hand-adds `--second FIRST FIRSTAVX2` when the window is re-run. The natural way to stage the one re-run
("the mfcard window again ... same plan and commit, a new run id", tsv:109) is to re-queue these same job files with a new
RUN_ID — which scores the second run as a FIRST run: a second INCONCLUSIVE prints INCONCLUSIVE "ONE re-run allowed"
again, never NOT-WIN (provenance cannot notice: nothing tells it a first run exists). Worse, d197_rule.tsv:105 says the
CONFIRM path re-runs "this rule again with the SAME arguments (a second run's --second included) plus --confirm", but
610 hard-codes the first-run argument list, so a CONFIRM reached on the second window and passed through 610 drops
--second too (a refused/absent confirmation then reads INCONCLUSIVE, tsv:104, instead of NOT-WIN, the r6 RULE-5 drill row
"the same absent confirmation on the second run: v3 NOT-WIN"). Not tonight's answer (tonight is the first run). Fix
(general form): window.vars carries FIRST_RUNDIR (empty on the first window); 609 and 610 both append
`${FIRST_RUNDIR:+--second "$FIRST_RUNDIR" "$FIRST_RUNDIR.avx2libc"}`; plus a dry-run line echoing which. Trigger: before
any re-run of the mfcard window is staged.

### ADQ-3 (CONFIRMED by the fix's own self-test case, design/maintenance, low-medium; effort S; blast radius every est read of a post-r6 record) — the NOTE path is keyed on "pin absent", not on "record predates r6"
est.py read_cells (diff hunk @540) and the r7 case `mf_nopin` (est.py ~1760). Direct answer to part 4: a job finalized
in a state other than `ran` CANNOT reach the unpinned read — read_cells refuses any cells.J*.tsv of a non-ran job
first ("holds cells of job X, which the record says failed/wait-timeout"), and record.py finalize pins every ran job
whose cells file exists (record.py:302-304), so a ran job of tonight's window always carries a pin. HOLDS for the
failed/wait-timeout question. BUT the tolerance itself is unconditioned: any record lacking the pin line reads with a
NOTE, and `mf_nopin` proves it on a record whose `window` is `mfcard` (est._synth(..., window="mfcard")) — a record
shape that cannot exist pre-r6 (mfcard has never run; s2d1/s2d2 records, checked in the tree, carry NO `window` key at
all, and no manifest pins either). So one line deleted from tonight's run_record.tsv (or a record written by an older
record.py if TREE is flipped, common.sh:22) degrades FIDELITY-3 to a stderr NOTE that 609 does not grep (est rows rc 0;
609 tees stdout only). The self-test case documents the loose rule as intended. Fix: tolerate a missing pin only for a
LEGACY record — predicate `"window" not in rec["run"]` (true of exactly s2d1/s2d2 and rmax_drill's re-derivation of
them) — and refuse "CELLS PIN absent" otherwise; retarget `mf_nopin` to a window-less synth and add the mfcard
pinless case as a REFUSED case. Sibling: manifest_check (est.py:365-367) has the same unconditioned absent-pin
tolerance for `manifest_sha256_<job>`; one `legacy(rec)` predicate should serve both (see the family section).

### ADQ-4 (design/maintenance, family; SUSPECTED as a cost, CONFIRMED as a count; effort M; no answer impact today) — sibling of a family: "what IS this arm" is re-derived per consumer
Yes, timed_form is a member of a family. The predicate `a.kind == "verify" and a.form == "null"` now appears at FIVE
link.py sites (render 524, arm_entry 569, 623, 725, and timed_form 230), each mapping the same arm class to one
consumer's value (renderer branch, slot.h kind K_NULL, the members/run source, the null-base check, and now the
TIMED_CALLEES key). TIMED_CALLEES itself is a prefix table over the CELL's form, while timed_form is an if-chain over
the ARM's (kind, form): two keying spaces for one fact, glued by "fc or else". The enter/j1 artifact arms are a third
implicit row ("no shape check": decided by the absence of SLOT_GATE_TU in the rendered text, link.py:690-694), and
J4's settest/rc-* forms a fourth ("no row: any external", ADQ-1). Two siblings outside link.py share the shape:
est.py's absent-pin tolerance in read_cells and manifest_check (ADQ-3: "legacy record" re-decided per pin).
GENERAL FORM: one declared first-match ARM-CLASS table in link.py, rows keyed on (kind, form-pattern):
`null base | find:<form> | ctl | verify:<form> | enter/j1` -> {renderer, slot kind, cell-bearing?, timed key,
callees (a tuple, or an explicit ANY with its reason), shape-checked?}. timed_form, TIMED_CALLEES, arm_entry's kind
map and render's dispatch become lookups; "any external" and "no shape check" become visible declared cells instead
of fall-throughs. Likewise est.py gets one `legacy(rec)` predicate for every absent pin.
UNLOCKS (with triggers): (a) J4 joining a timed window gets its verify forms' callees as table rows, closing ADQ-1
(trigger: J4 scheduled in any window); (b) J5B's enter_back / a new arm kind is one row, not five edits (trigger: J5B
scheduled, or the next arm kind); (c) a self-test that walks EVERY plan.build() arm through the table and refuses an
arm no row claims — a population check (K35) that would have caught j4fix's original null-key gap at plan time
rather than in a dry run (trigger: now, cheap: py/arm_keys.py is ~20 lines and is that check's skeleton);
(d) the legacy predicate lets est refuse pinless post-r6 records (ADQ-3; trigger: before tonight's 609 if cheap).

## PROBED-AND-HELD

- Part 1, sabotage rows run singly at SUBJECT (`SLOT_TREE=$T sabotage.sh adequacy/sab_ROW ROW`, fresh dirs; logs adequacy/row_ROW.log):
  - m1 S3207: DETECTED, est rc 1, the matched line is `[r6 FIDELITY-3] two keys' cells swapped after finalize ... WRONG`
    (the new `[r7 RULE-2] ... present and different: refused` also goes WRONG, consistent). The re-anchor (`elif got != pin`)
    disables exactly the pin compare. SAME.
  - m6 S3221: DETECTED, shape rc 1, `[S3220] a J4 null base with an out-of-line callee WRONG ok` (timed_form None ->
    timed_callees("" prefix) None -> any external). The null-base control row stays ok. SAME. (A sibling plant, deleting
    the `("null", ())` row, reaches the same None and would also be detected by S3220: reasoned, not run.)
  - k: DETECTED, J2 rc 3, `CELL-TEXT MISMATCH kit.find_byte.libc: site text bc7b2e02..., the hash of the instance its key
    names (libc -) d7672e87...`. The plant now renders libc from walk's facts+parts; walk's text calls no external, so
    TIMED-SHAPE (libc row allows memchr) passes and FRAME (both generic) passes; the cell-text check is the one that
    fires, as the comment states. SAME. (Fragility note, not a finding: the row now depends on the libc row's callee set
    being a SUPERSET of walk's; if libc's row ever narrows, k moves to TIMED-SHAPE again.)
  - t2 S3161: DETECTED, JMB rc 1, `ISA MISMATCH kit.find_byte.mfind-swar: keyed target generic, its code needs bmi,bmi2
    (andn ...)`: the -march=x86-64-v3 plant at compile_tu's re-anchored line (both _time and _g objects) is the cause. SAME.
  - k1 S3167: DETECTED, JMH rc 1, `KEY-ARM MISMATCH kit.find_hit.mfind-swar.periodic.one.4.50: dim reject: the key names 50,
    the Arm 0`: render's key_arm_mismatch on the planted reject=0, the mechanism the comment names (plan freeze/groups
    did not refuse first). SAME. All five rows: SAME, none SILENT-MOVE, none LOUD-for-another-reason.
  - Anchors: sabotage.sh's patch() refuses an anchor not found exactly once (loud); k's two anchors, k1's re-indented
    plan.py anchor, m1's, t2's and m6's are each unique in the subject (grep).
- Part 2, timed_form: plan.build() over EVERY job, each arm through render's fc rule (py/arm_keys.py): JMB 9 arms, JMH 173,
  J2 5, J2p 20 — every timed arm carries a cell and keys to a TIMED_CALLEES row (mfind-* (), fn-memchr/libc/pair memchr,
  walk/ctl ()); none reaches `null` or an unkeyed None. Only J4's 7 null bases take timed_form's cell-less path. Direct
  timed_form probes (py/tf_probe.py, 10 cases): a JMH find arm, a ctl arm, a J4 settest arm and a form-None verify arm
  with fc None or () all REFUSE; a null base outside J4 (group JMH.base) keys `null` (render then holds its name/of).
  Prefix: no plan form starts with `null` (forms: walk libc pair fn-memchr mfind-swar/w16/w32 settest rc-words rc-memcmp
  null artifact); `nullx` would key () — strict, not loose, so harmless; mfind-w64 (OWED) keys () via `mfind-`.
  A null base can never legitimately need a callee: its body is the class arm's text with the compare removed and the
  dry J4 run (kit/dryJ4.log) linked all 7 under the () row.
- Part 3, d197_rule.py CLI, 13 argument shapes (subprocess): 609's shape `rule A B` and 610's `rule A B --confirm C D`
  reach rule() (REFUSED input on absent dirs = past the parser); both flag orders parse; one-rundir flags, duplicate
  flag, extra positional, `--second=C D`, three rundirs after a flag, `rules A B`, bare `rule`: usage rc 2. Only gap: no
  arguments at all -> IndexError traceback rc 1 (sys.argv[1] read before the try; trivial, not filed). Second-ness: ADQ-2.
- Part 4: a failed / wait-timeout job's cells file cannot be read unpinned (read_cells refuses non-ran jobs' cells
  first); every ran job is pinned at finalize. Held; the residual is ADQ-3.
- window.c `_Static_assert(FF__COUNT <= 31 ...)`: stronger than the old `FF_MFIND < 31` (covers every pick, REN_PICK(f)
  for f < FF__COUNT stays below bit 31 = REN_FRAME). Read, held.
