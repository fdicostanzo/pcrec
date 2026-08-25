# tests/possessify — the [ENG-BREP] possessification rung's validation

`docs/design/eng_brep_design.md` §2 is the design; `src/opt/possessify.c` is
the analysis; `src/gen/emit_vm.c` is what acts on it. This directory is the
evidence that it changes no answer.

**Not a module directory.** Possessification is an OPTIMISATION over the base
tier, not a regex feature, so no block here carries a `features` directive and
there is no module gate to open. It gets its own directory for the reason
`tests/vm/` has one: what it needs to assert is not expressible as `.rxt`
expectations.

## The three checks see three different things, and none replaces another

This is the part worth reading before adding to any of them, because the
natural instinct — "the corpus is green, so the rule is right" — is wrong here
in a specific way.

- **`possessify.rxt`** pins what each pattern MATCHES. It is structurally
  BLIND to the rule itself: a possessified quantifier and a backtracking one
  match identically, which is the entire claim. Every expectation was produced
  by BOTH oracles (python3 `re` and libpcre2 10.46) and agreed; two cells of
  the `(|a){m,n}` family agree on the span and differ on group 1, and are kept
  SPAN-ONLY with the divergence recorded inline rather than pinned to
  whichever oracle was asked first (§3.6's investigate-don't-filter rule; R24
  S-F5 measured pcrec agreeing with libpcre2 on all 15,600 cells of that
  family).
- **`run_possdiff.sh` + `possdiff_driver.c`** — the row's PRIMARY instrument
  (§5.1). Same pattern compiled twice, once with the rewrite and once with
  `-fno-possessify`, both artifacts linked into ONE translation unit, and
  every subject compared on the span, EVERY capture slot and the FAILURE
  SURFACE at every start position. The denied build is not an approximation of
  the semantics — it is the shipped semantics — so a disagreement is a bug by
  construction rather than a question about which engine is right. It is blind
  to a rule that fires on nothing, which is why it carries its own NON-VACUITY
  control: a sweep in which no pattern possessified compared identical
  artifacts and measured nothing, and says so as a failure.
- **`run_possessify_tests.sh`** — that the rewrite HAPPENED where the stamp
  says it did, NOWHERE when denied (D47.3's do-or-die, asserted against the
  artifact and never against the flag having been passed), that verdict-free
  patterns emit BYTE-IDENTICAL C with the pass on and off, and that
  `rx_info`'s declared capacities moved with the machinery. Nothing else in
  the tree asserts any of these.

## Files

- **`possessify.rxt`** — oracle-verified cases over the §2.2 rule's own
  families: both arms (exact-count and disjointness) in both preferences, one
  block per DECLINING condition (ambiguous body, not prefix-free, nullable
  body, overlapping follow, subsumed follow, `^` in the follow), the lazy
  conjunct's guard cells that D47.6 ruled into the corpus, the `$`-follow
  exemption with newline subjects, and the nested-quantifier family the
  transitive-FOLLOW line is about.

  **Every family appears TWICE, and the second half is the one that tests the
  emitter.** Under the default engine choice a capture-free pattern routes to
  the DFA and never reaches `src/gen/emit_vm.c`, so possessification is
  structurally invisible to it — measured on this file's first version, 33 of
  38 patterns were DFA-routed and only THREE carried a possessified
  quantifier, which is an oracle-verified corpus for a VM rewrite that almost
  never ran the VM. Wrapping each pattern in one capture forces the VM
  artifact while changing nothing the analysis sees (A_CAP is transparent to
  FIRST, to FOLLOW and to the Glushkov construction) and group 1 is then the
  whole match, so the capture slot is checked too. With both halves: 43
  VM-routed patterns, 28 of them possessified.
- **`patterns.txt`** — the differential's population, built as §2.4's family
  (prefix × body × count × follow) with every count spelled BOTH ways. The
  both-ways part is not optional: R24 found the lazy defect precisely because
  the design lane's own probe could not express a lazy row, so half the
  question left its differential without a word in the output.
- **`possdiff_driver.c`** — links the possessified and denied artifacts under
  two prefixes into one TU. That is itself a real property being exercised:
  the fixed ABI types are emitted under a prefix-INDEPENDENT include guard so
  differently-prefixed headers can share a TU (D44/A-2).

  **It is now SHARED with `tests/rungselect/`** ([ENG-BREP]'s next rung), which
  links it with its own pair of artifacts. The comparison this file makes — two
  artifacts of one pattern must agree on span, every slot and the failure
  surface — is the same claim for every member of D47.3's deny family, and only
  the words in the divergence report differ. Those come in through
  `-DDIFF_A_LABEL`/`-DDIFF_B_LABEL`, which default to this suite's own wording,
  so nothing here changed behaviour. Keep it that way: a second copy of this
  comparison would be a second thing to keep in step with the first.
- **`run_possdiff.sh`**, **`run_possessify_tests.sh`** — the two suites,
  wired into `make test` as `make test-possessify` and into the `make
  ubsan`/`make asan` both-axes batteries. EXECUTION of every generated
  binary in both scripts is bounded via `gen_run` (`tests/lib/gen_timeout.sh`,
  `WATCHDOG_SECTION=possdiff`/`possessify`) — the run budget, a 512m RSS
  ceiling, and a log line per run in `build/watchdog.log`. `run_possdiff.sh`'s
  driver reads its subject sweep on STDIN, and `gen_run`/`scripts/watchdog`
  backgrounds its child (`setsid ... &`); with job control off (a script's
  default) bash gives a backgrounded job's stdin from `/dev/null` regardless
  of a redirection written on the `gen_run` call itself, so that site opens
  the subject file INSIDE a `bash -c` `gen_run` runs, where the redirection
  is resolved by that process rather than inherited — silently swept 0
  subjects on the first wiring attempt (this file's own D47.6 "measured
  nothing" shape), caught by comparing the cell count against a run before
  the change. `run_possdiff.sh --corpus`
  additionally derives, at run time, every `.rxt` corpus pattern the analysis
  gives a positive verdict on and sweeps those too — a DIFFERENT population
  from `patterns.txt`, which is built to exercise the rule's own arms and
  refutations while the corpus is what pcrec is actually asked to compile.
  Derived from the pass's own census line rather than kept as a second file
  that could go stale against the analysis.

## The two differential populations, and why both

Read from a run, not from here — but for orientation, the last full sweep was
365 patterns and 158,827 pattern-subject-startpos cells at zero divergences:
155 patterns from `patterns.txt` (the designed family, built to exercise the
rule's own arms and each of its refutations) and 210 derived by `--corpus`
(every `.rxt` pattern the analysis gives a positive verdict on). Neither
subsumes the other. The designed family contains shapes the corpus does not —
nobody writes `(?:ab?){0,4}b` on purpose — and the corpus contains shapes
nobody designed for, which is the whole reason it is adversarial.

## Two lessons this directory paid for, recorded so they are not re-paid

**The subject generator can silently measure nothing.** D47.6: the design
lane's archived sweep reported 20 "false declines" that were 20 GENUINE
divergences, because its random-subject alphabet was `"abcd "` and every
`z`-prefixed pattern in its family was therefore swept essentially without its
prefix. `run_possdiff.sh` derives each pattern's subject alphabet from the
PATTERN'S OWN TEXT for this reason, and the discriminating family is prefix +
repeated body. *A generator whose alphabet omits a pattern character measures
the generator.*

**A green sabotage row is a finding about the POPULATION, not a clean bill.**
Sabotage S48 (the enclosing-loop FOLLOW term dropped) came back UNDETECTED
against the first version of `patterns.txt`, and the reason was that every
nested cell in it put a NON-NULLABLE item after the inner quantifier — a shape
where the term is merely conservative. A generated search over an
18,480-pattern nested family found 7,553 patterns whose verdict changes
without the term and 44 wrong spans in a 1,259 sample; the shape that
discriminates puts the inner quantifier at the END of the enclosing body.
Twelve witnesses were added and S48 is now DETECTED. The term is load-bearing;
the first population simply could not see it.

## What "the failure surfaces agree" means, and why it is not the obvious thing

§5.1 asks the two builds to agree on the FAILURE SURFACE, not merely on
matches. Read literally that is in tension with the feature: possessification
CHANGES the frame requirement — §7 predicts exactly that — so an artifact that
answers a 200,000-byte subject and one that honestly returns `RX_ERR_FRAMES`
at 512 do not have the same failure surface, and neither is wrong.

The requirement is a claim about the INTERSECTION of the two artifacts'
DECLARED limits, and the measurement turned out sharper than the claim: on
`(x)(?:a|bc)+d` the two agree on every length the denied build says it can
handle and part at EXACTLY its stamped `subject_ceiling`, 511 against 512. The
stamp is exact at its boundary rather than conservative, which is what makes
the intersection computable instead of guessed, and the divergence above it
runs only in the direction of the possessified build being MORE capable. Both
halves are pinned in `run_possessify_tests.sh`; the archived cell is
`docs/design/possessify_impl/throughput.txt`.

It was found by a throughput cell run OUTSIDE the denied build's limit, which
returned two different answers and looked for a moment like a divergence.

## The finding this lane owes the manager: the step budget cannot see a
## possessified loop

Not a defect in this directory's checks — a design consequence, recorded here
because it was found here and because the next ladder rung will meet it again.

§4.2 charges a step per backtrack RESUMPTION, deliberately, so that forward
progress is free and the budget is subject-length-independent. A possessified
loop performs no resumptions, so it charges NO STEPS. With the prefilter off
(`--engine=vm`), the search then rescans from every start position with nothing
to stop it: on `(a*)b` over a subject of all `a`, MEASURED 0.033 s at 10 KB,
0.581 s at 50 KB, 2.297 s at 100 KB — quadratic — where the `-fno-possessify`
build gives up in constant time after 1M steps.

It is not a regression in what SHIPS: under the default engine choice §4.7's
ordering rule applies, the prefilter answers `(a*)b` outright and the VM never
scans. The exposure is `--engine=vm`, which turns the prefilter off on purpose
(R21 E-6) and is a diagnostic mode.

**RULED (manager, 2026-08-16): land as-is.** The fix-of-record is an
E-5-SHAPED CHARGE — one step per possessified-loop ENTRY, the island-entry
precedent §4.2 already carries — OWED WITH THE COUNTER-K STEP, which touches
the same accounting. Not gold-plated into this landing.

**SLOW, NOT LOOPING**, and the difference was established rather than assumed,
because a wrongly-admitted nullable body would spin forward charging zero
steps and look identical from outside. The emitted loop's cursor strictly
increases under a hard bound (§6's termination argument holding exactly
because §2.2 refuses a nullable body), the growth is cleanly quadratic, and
the full 1 MB cell terminates in 228.5 s with the correct answer. See
tests/vm/CLAUDE.md for the numbers.

## A note for whoever runs this suite alongside something else

`tests/base/k18_cost_gates.rxt` gates on COMPILE TIME — it rides D45's
generated-code budget (5 s plain), and one of its patterns emits a 205 KB
artifact that gcc legitimately takes ~2.4 s on. Running `make test` while
`make mech` is building whole trees pushed it over and produced three
"failures" that were pure CPU contention. The check that settles it takes ten
seconds: that pattern's emitted C is BYTE-IDENTICAL with the pass on and off
(it possessifies nothing) and gcc times 2.39 s against 2.40 s, so
possessification cannot be the cause. Serialize the batteries.

## [ENG-BREP] Three checks here PIN THE NEXT RUNG OUT

`run_possessify_tests.sh`'s frames-rung shape block, §7's ceiling prediction and
its capture-bearing counterpart all pass `-fno-revdet` as of the
reverse-deterministic rung's landing. Not a workaround — each names the FRAMES
RUNG in what it asserts, and `(?:a|bc)` is reverse-deterministic, so at the
default those quantifiers stopped taking that rung. The failures read as "the
cut is missing from the possessified build" and "subject_ceiling did not move as
§7 predicts", neither of which was true: the rung the assertion names was no
longer the rung that ran. D46's pin-the-selection rule.

The third one is worth reading for a reason of its own. It asserts that a
possessified loop with CAPTURES in its body still declares a ceiling, because
the cut discards frames and deliberately does not rewind the trail. On the
reverse-deterministic rung that stamp is 0 and it is TRUE — that rung SUPPRESSES
the body's capture writes and recovers the same values by a backward walk at
commit, so nothing grows per iteration. Two different facts about two different
emissions, and the denial is what keeps this file asserting its own.

## Failing-direction controls

Five `tests/mech/sabotages/` rows, one per refuted rule the design records —
S45 (the lazy conjunct), S46 ((U1) one-unambiguity), S47 ((U2) prefix-freeness),
S48 (the enclosing-loop FOLLOW term), S49 (the assertion exemption leaking to
`^`). All five are DETECTED by `run_possdiff.sh`; `make mech` prints the
matrix rather than this file quoting counts that would go stale.

Maintenance: update this file when files are added/removed or their roles
change.

## [DD-14.FB] the frames-rung check reads the capacity macro from the `.h` (2026-08-25)

`RX_RESUME_FRAMES` moved out of the generated `.c` and into the paired header
with the caller-buffer sizing surface (spec §10.4), because a caller has to
read it before it can size a buffer for `<prefix>_search_in`. This suite's
`gen` helper compiles with `-o <name>.c`, i.e. SPLIT output, so the frames-rung
check now reads the macro from `<name>.c` and `<name>.h` together — the same
correction this file's `strats` helper already carries for
`PCREC_VM_STRAT_POSSESSIVE`, and for the same reason.

**It would have gone RED, not vacuous**, and the distinction is worth keeping
straight because the first version of the fix's comment claimed otherwise: the
comparison is arithmetic and `[ "" -lt "" ]` is an error, which is false. What
the wrong read cost was the MESSAGE — a failure reading `( -> )` sends a reader
to the possessify pass instead of to a macro that changed file.
