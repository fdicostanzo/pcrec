# 2026-11-15-r8-memfn-mcfixc — code round on the mcfixb fix diff (DRAFT, dispositions PROPOSED)

## Subject
- SUBJECT 38869c33320c8f65df6fa67811a82e187bfbf1bd (lane/memfn-mcfixb tip); BASE 6ab3f485b9942606ebd5765fd68fd9a586804138
  (by design: rounds r5-r7 reviewed everything up to it). Fix diff only: slot/{d197_rule.py,d197_rule.tsv,est.py,link.py,
  sabotage.sh,CLAUDE.md}, memfn/src/window.c.
- Rulings frozen at main 782502e99 (decisions.md/plan.md); no FREEZE DRIFT at hand-back (same commit).
- FREEZE NOTE: D197's rule conditions, Kit R1 and r6 FIDELITY-1 were briefed as quoted by the launcher; their records
  were not re-located by the coordinator this round.
- Round kit: review tree built (nice make -j2, rc 0); dry J4 (35 arms, 0 misses) and dry JMH (172 arms, 0 misses) at
  SUBJECT in kit/.

## Lenses as run
| lens | model | question | why |
|---|---|---|---|
| check adequacy + rule soundness | opus | (1) re-anchored/changed sabotage rows fail for their stated reason; (2) timed_form cannot let a real timed arm key `null` or skip; (3) CLI parses 609/610's shapes, refuses malformed; (4) absent-pin NOTE cannot price tonight's record unpinned; + sibling-of-family, general form + unlocks | launcher sized the round SMALL: one critic + one verifier |
| verifier | sonnet | ADQ-1..3 | standard |

The critic caught all four findings; the verifier ran ADQ-2 and ADQ-3 end to end (HOLDS x3).

## Findings (PROPOSED dispositions)
- **ADQ-3** (design, answer-adjacent; S) — est.py read_cells' absent-pin tolerance is keyed on "pin absent", not "record
  predates r6". Verified: an est._synth(window="mfcard") record with one `cells_sha256_J2` line deleted prices with
  rc 0 and only a stderr NOTE (609 tees stdout only). The real pre-r6 records (s2d1, s2d2) carry NO `window` key, so
  `"window" not in rec["run"]` identifies exactly the legacy records. The fix's own `mf_nopin` case asserts the loose
  rule on an mfcard-window synth. Part 4's specific worry HELD (a non-ran job's cells are refused first; every ran job
  is pinned at finalize). **Proposed FIX-NOW** (before tonight's 609): legacy predicate; refuse "CELLS PIN absent"
  otherwise; retarget `mf_nopin` to a window-less synth and add the pinless-mfcard case as REFUSED; apply the same
  predicate to manifest_check's identical absent-pin tolerance (est.py ~365); sabotage row for the new refusal.
- **ADQ-2** (answer on a SECOND window, design; S) — no staged job reaches second-ness. 609/610/common.sh contain no
  `--second`; re-queueing them with a new RUN_ID scores the re-run as a first run. Verified: the same INCONCLUSIVE pair
  reads `INCONCLUSIVE ... the ONE re-run` without `--second` and `NOT-WIN (second-run-without-a-verdict)` with it. 610
  also hard-codes the first-run arguments though d197_rule.tsv:105 says CONFIRM re-runs "with the SAME arguments (a
  second run's --second included)". Not tonight's answer. **Proposed FIX-NOW (job files only, S)**: window.vars
  FIRST_RUNDIR (empty on the first window); 609 and 610 append `${FIRST_RUNDIR:+--second "$FIRST_RUNDIR" "$FIRST_RUNDIR.avx2libc"}`;
  each --dry-run echoes which. Alternative ruling: PLAN with trigger "before any re-run of the mfcard window is staged".
- **ADQ-1** (maintenance/design; S) — J4's null bases are now keyed strict (`null`: no callee) while the 28 J4 verify
  arms they are subtracted from (settest, rc-words, rc-memcmp) resolve to callees None = any external (pre-existing at
  BASE). A verify arm calling an out-of-line memcmp would be timed with the call; the base cannot carry it; the delta
  absorbs it unrefused. J4 is not in tonight's window (JMB/JMH/J2/J2p all keyed). **Proposed PLAN**, trigger: J4
  scheduled in any timed window — give settest/rc-* their dry-run callee rows, or document the deliberate exemption.
- **ADQ-4** (design/maintenance, family) — the arm-class fact `kind == "verify" and form == "null"` is re-derived at five
  link.py sites (render 524, arm_entry 569, 623, 725, timed_form 230); TIMED_CALLEES keys on the cell's form while
  timed_form keys on (kind, form); enter/j1's "no shape check" and J4 verify's "any external" are implicit fall-throughs.
  General form: one declared first-match ARM-CLASS table (renderer, slot kind, cell-bearing, timed key, callees incl.
  explicit ANY with reason, shape-checked). Unlocks: J4 callee rows (closes ADQ-1; trigger J4 scheduled); a new arm kind
  is one row (trigger J5B / next kind); a population self-test walking every plan.build() arm and refusing an unclaimed
  one (trigger: now, cheap — the critic's py/arm_keys.py is its skeleton; it would have caught j4fix's original gap at
  plan time). **Proposed PLAN** (table); the population self-test **FIX-NOW optional** if the manager wants it cheap.
- **NOTED**: `d197_rule.py` with no arguments raises IndexError (sys.argv[1] read before the try), rc 1 — trivial.
- **NOTED**: row k now depends on libc's callee set being a superset of walk's; if libc's TIMED_CALLEES row narrows, k
  moves to TIMED-SHAPE again (the m-history this lane just repaired). Worth one line in k's comment.

## PROBED-AND-HELD (critic, verified where marked)
- Sabotage rows run singly at SUBJECT: t2 (ISA MISMATCH, -march plant at compile_tu), k1 (KEY-ARM MISMATCH via render),
  k (CELL-TEXT MISMATCH; TIMED-SHAPE and FRAME pass first, as the changed comment states), m1 (pin compare disabled; the
  r6 FIDELITY-3 case goes WRONG), m6 (S3220 goes WRONG): all DETECTED for their stated reason, all SAME, none LOUD for
  another reason; every anchor unique.
- timed_form over every plan.build() arm: JMB 9, JMH 173, J2 5, J2p 20 all cell-bearing and keyed; only J4's 7 null bases
  take the cell-less path; 10 direct probes (cell-less find/ctl/settest/form-None verify) all refuse; no plan form starts
  with `null`; a null base never needs a callee (dry J4 linked all 7 under `()`).
- CLI: 13 argument shapes: 609's and 610's reach rule(); flag order free; one-rundir flag, duplicate flag, extra
  positional, `--second=X`, three rundirs, wrong verb, bare `rule`: usage rc 2.
- window.c `_Static_assert(FF__COUNT <= 31 ...)`: strictly stronger than `FF_MFIND < 31`.

## By-id completeness
ADQ-1 HOLDS (verified) · ADQ-2 HOLDS (verified, run) · ADQ-3 HOLDS (verified, run) · ADQ-4 not verified (design/count
claim; the five sites are line-cited). No answer-level finding against tonight's first-run verdict; ADQ-3 is the one
that can affect tonight's record if a pin line is lost.

## Lessons for the guide
- A tolerance added for LEGACY inputs must be keyed on a legacy marker, not on the absence of the thing it tolerates;
  the check-adequacy lens should plant "delete the new pin from a NEW-shape record" whenever a fix adds an
  absent-field tolerance.
- A rule's CLI flag that only a human can supply (here `--second`) is a population nobody counts: the lens should grep
  every staged job for each flag the rule's spec requires and list the unreached ones.

Texts: review/adequacy.md, review/verify.md, review/COMMON.md.

## RULED (kit manager, 2026-11-15 ~15:30)
- ADQ-3 FIX-NOW: a missing cells pin is tolerated ONLY on a legacy record (no `window` key: s2d1/s2d2); any record with a `window` key and no pin is REFUSED, in est.py and manifest_check alike; retarget the mf_nopin selftest case + add the new-shape plant (pin line deleted from an mfcard-shaped record -> refused).
- ADQ-2 FIX-NOW (job files, kit scratch): FIRST_RUNDIR (+ its AVX2 arm) in window.vars; 609 and 610 pass `--second` with it when set; 610 reads the first run's arguments from window.vars, not hard-coded; dry-run both ways.
- ADQ-1 PLAN (trigger: J4 is ever timed). ADQ-4 PLAN (one arm-class table; trigger: the next arm class or RULE-9's rules.py). Process lesson accepted (plant the deleted field on a new-shape record).
- One XS lane (sonnet); its diff gets a single-critic check before landing.
