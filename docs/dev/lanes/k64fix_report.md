# k64fix — K64 fix A (lane k64fix, opus, 2026-09-25)

Branch `lane/k64fix` from `b8aa188e`. Brief: build fix A for K64 as Frank
ruled it (docs/dev/known_issues.md K64; cycle2_admitfix_reading.md §1.8 A).

## FINDINGS FIRST

1. **The fix is one conjunct in the one predicate.** `req_route_one_attempt`
   (src/gen/emit_dfa.c) still answers "one attempt" on the VM route from
   `Job.start_anchor`, but now also needs the attempt to be linear:
   `(fit.prefilter && !fit.prefilter_collapsed) || Job.vm_frameless`. The new
   `Job.vm_frameless` field (src/core/internal.h) holds `!Vm.has_push`, the same
   bool `<PREFIX>_VM_FRAMELESS` stamps. `vm_plan_entry` publishes it right
   after deriving that bool, which is before `pcrec_emit_prologue` asks
   `req_admit`. Nothing else is re-derived and there is no parallel mechanism.
2. **The repro is fixed, and so are the bench subjects.** I re-ran
   `giveup_repro.sh` against the pair `b8aa188e` (6ef76820 behaviour) and
   k64fix, with its pin names swapped by sed. The script is unchanged.
   The 75 short subjects matched 75/75 by sha and the throughput subjects 3/3.

   | pin | cfg | rc over 75 |
   |---|---|---|
   | b8aa188e | vm | **5 × -2** (500,000,001 steps, ~3.1 s each), 66 nomatch, 4 match |
   | k64fix | vm | 71 nomatch, 4 match (b1885a83's state, PCRE2's answers) |
   | both | auto | 71 / 4, and the auto artifact is byte-identical |

   The five are `sd-empty-alt-hit`, `sd-empty-alt-miss`, `sec-github-pat`,
   `v-uuid-badnibble` and `v-uuid-valid`. On the fix each one returns before
   the VM runs, after one `memchr`, so 0 VM steps. The driver's step
   print is meaningless in that case, as the script's own header warns.
3. **The census found a mover the brief did not predict: 41 AUTO-route
   artifacts.** The brief predicted that the forced-VM throughput artifacts
   regain the pre-check and that the DFA/auto route stays byte-identical. On
   the bench population that holds exactly: 12 movers, which are the 6 named
   patterns × vm-caps/vm-nocaps, and 0 auto movers. The corpus population
   also holds auto-route VM artifacts with **no hybrid at all**. Those are
   backreference and linked-call patterns such as `^(a(?1)?b)$`, `^(a)\1*$`
   and `(?J)…\k<a>$`, and the hybrid prefilter is declined outright for them.
   They are framed, unguarded and anchored, so they have exactly the K64
   hazard, and the rule correctly gives them back their pre-check. The
   brief's "auto route is untouched" argument is true only where auto
   selects a DFA or an exact hybrid (reading §1.4's population), not for
   every auto artifact.
4. **Every mover has one shape.** There are 176 of 6,634 artifact-configs:
   256 bench configs and 6,378 corpus configs over 3,189 distinct corpus
   patterns × {`--features all`, `+ --engine=vm`}. Every one changes exactly
   1 line, `RX_REQ_WHY "one-attempt"` → `"emitted"`. It gains either 5 lines
   (the stamp, `<string.h>` and the 3-line byte check; 141 artifacts) or 16
   lines (the stamp, `<string.h>` and the run check; 35 artifacts). Every
   mover is `VM_FRAMELESS 0`, `VM_PREFILTER "none"`, `VM_START`
   anchored/gstart. None is a hybrid: no collapsed hybrid is one-attempt in
   either population. That arm is reachable only under `-fprefilter-collapse`,
   and §5.6 pins it there. There are 0 refusal mismatches and 0 timeouts.
5. **abi: OPEN, escalated to the manager.** The fix adds no stamp, no
   declaration and no layout change. It does change a stamp's VALUE and the
   emitted text on 176 artifacts. D76 says the output is byte-exact within an
   abi number, and `run_recursion_identity.sh`'s (B) sweep of call-free
   `--engine=vm` artifacts contains movers such as `^(a|ab)$` and `(^a){1,3}`,
   so (B) is expected red without a 32→33 bump and re-pin. I have not run it;
   the gate is opt-in. Per brief item 5 I stopped and asked rather than
   bumping. **See §Owed.**

## What was built

- `src/core/internal.h`: adds `bool vm_frameless` to `Job`, with a header
  comment covering who publishes it, when, and why early.
- `src/gen/emit_vm.c` (`vm_plan_entry`): one assignment, published next to
  the derivation of `has_push`.
- `src/gen/emit_dfa.c` (`req_route_one_attempt`): the conjunct, plus a header
  paragraph saying why a VM one attempt must also be linear.
- `docs/spec/tuning.md` §2.29 (D80):
  - a new paragraph, "G2 needs the one attempt to be LINEAR", with the
    mechanism and the two admitting facts;
  - the **Answer-identity** paragraph rewritten to cover give-ups. The old
    sentence "the check could only ever return the answer the engine below it
    then returns anyway" was false. It is now true within the same step
    budget, and the paragraph says why the linearity condition is part of the
    claim;
  - the stamp table's `"one-attempt"` row now reads "linearly (a DFA, an
    exact hybrid, or a frameless VM program)".

  `limits.md` §1 needed no change: a give-up stays honest, and this fix
  simply stops producing one here.

## Checks (both directions verified)

- **`tests/base/k64_precheck_forced_vm.rxt`**: 2 blocks, 9 cells.
  - Block 1 is `^([a-zA-Z0-9._%+-]+)+@` with `engine vm` and
    `budget steps=10000`. It has 4 `n` cells with class runs of L = 16..20,
    1 `m` cell, and 1 `gu steps` control ("…!@": with the byte present the
    budget still bites, which proves the witness reaches the VM).
  - Block 2 is the frameless control `^[a-zA-Z0-9._%+-]+@`.
  - `tests/harness/run.sh` on the file gives **9/0 on the fix** and **4 failed
    / 5 passed with `PCREC=<b8aa188e build>`**. The four failures are the
    block-1 `n` cells, as steps give-ups.
  - Python oracle: `verify_rxt.py` reports PASS=8, SKIP=1 (giveup). I kept the
    runs short so python's own exponential backtracking stays fast.
- **`tests/codegen/run_prechecks.sh` §5.6** (+8 checks, 250 → 258):
  - five REQ_WHY rows in route pairs: forced-VM framed → emitted; the same
    pattern on auto with an exact hybrid → one-attempt; the same pattern
    under `-fprefilter-collapse` → emitted; exact → one-attempt; frameless
    forced VM → one-attempt;
  - three `[5.6r]` reach rows proving each witness still takes the route its
    reason names.

  It passes **258/0** on the fix. On b8aa188e it goes **256/2**: the two
  "emitted" rows fail.
- **Sabotage S273** (`tests/mech/sabotages/S273_precheck_g2_vm_linearity_removed.sh`)
  plants the pre-K64 VM arm. `SAB_HARNESS_TARGET` aims the corpus arm at the
  new `.rxt`, and `SAB_REACH` probes the clean tree (framed, unguarded, keeps
  its pre-check). The `run_sabotage_matrix.sh S273` run scored it
  **DETECTED: `corpus:4fail/5pass`, `prechecks:2fail/256pass`**, with
  0 unexpected, 0 undetected, 0 unreached and 0 anomalies. The highest S-id
  on main was S272.
- **S269 re-anchored.** Its `SAB_BEFORE` quoted the predicate body I changed.
  The plant and its intent ("the predicate always says no") are unchanged.
  - I measured its prechecks arm by hand on the new anchor: `git archive`,
    then `replace.py` (1 occurrence), build, run → **13 fail / 245 pass**.
    That is §5.1/5.2/5.4/5.5 as before, plus §5.6's three one-attempt rows.
  - Its harness arm (full corpus, expected green) was NOT run. It is owed at
    `make mech`.
  - S269 and S270's "measured on the clean tree at 250" figures now read 258.
- `tests/mech/CLAUDE.md` gains the S273 table row and a paragraph saying
  S273 is the one plant in the admission family a corpus can see.

## Re-pins (readers found by grep)

- `tests/rxtsource/run_rxtsource_tests.sh`:
  - CENSUS_* and RUNSH_* move 216/3995/29113 → 217/3997/29122.
  - C3_PASS 13721 → 13729, C3_SKIP 15227 → 15228, C3_SKIP_GIVEUP 23 → 24,
    from the file checked alone (the prior re-pins' method).
- S269 and S270 SAB_DOC_FIGURE counts.
- No other pin names run_prechecks' count.
- **NOT re-pinned, pending the abi ruling:** `run_recursion_identity.sh` (B).
  Any manifest that pins emitted bytes of a mover (cpset EMITTED_BYTES,
  resource) will show up in make test; none is expected, because their
  witnesses are default-route.

## Check gaps (brief item 6): listed, not closed

- `docs/dev/lanes/admitimpl_answerdiff.py` ran auto-route arms only. It is a
  one-shot lane instrument that nothing re-runs, so editing it closes
  nothing. Its standing replacement is the new corpus file plus S273, which
  put a forced-VM witness where every `make test` sees it.
- `tests/axes/run_axes.sh:780` counts a one-sided give-up as "budget-bound"
  and never as a failure. Changing that is a policy change to a multi-hour
  battery, and I could not validate it cheaply, so it is not done here. The
  learnings §3 candidate stands as filed: count answer→give-up TRANSITIONS as
  their own population.
  The census above is a second instance of the general lesson. The brief's
  population ("the 6 forced-VM cells") came from the bench, and the corpus
  held 41 more artifacts of the same shape on a route the brief called
  untouched.

## Validation

- `make strict`: clean.
- The targeted runs above, with the files they ran named.
- `make test-codegen`, `make test-rxtsource` and `make test-prechecks`:
  running at the time of writing. The results are in the handback message.
- **Owed:**
  - the abi ruling, and the bump ritual if it is ruled;
  - the full `make test`, after the manager's slot go (log path in the
    handback);
  - the S269 harness arm, at the next `make mech`.
