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

- **`possessify.rxt`** — 1,028 oracle-verified cases over the §2.2 rule's own
  families: both arms (exact-count and disjointness) in both preferences, one
  block per DECLINING condition (ambiguous body, not prefix-free, nullable
  body, overlapping follow, subsumed follow, `^` in the follow), the lazy
  conjunct's guard cells that D47.6 ruled into the corpus, the `$`-follow
  exemption with newline subjects, and the nested-quantifier family the
  transitive-FOLLOW line is about.
- **`patterns.txt`** — the differential's population, built as §2.4's family
  (prefix × body × count × follow) with every count spelled BOTH ways. The
  both-ways part is not optional: R24 found the lazy defect precisely because
  the design lane's own probe could not express a lazy row, so half the
  question left its differential without a word in the output.
- **`possdiff_driver.c`** — links the possessified and denied artifacts under
  two prefixes into one TU. That is itself a real property being exercised:
  the fixed ABI types are emitted under a prefix-INDEPENDENT include guard so
  differently-prefixed headers can share a TU (D44/A-2).
- **`run_possdiff.sh`**, **`run_possessify_tests.sh`** — the two suites,
  wired into `make test` as `make test-possessify`.

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

## Failing-direction controls

Five `tests/mech/sabotages/` rows, one per refuted rule the design records —
S45 (the lazy conjunct), S46 ((U1) one-unambiguity), S47 ((U2) prefix-freeness),
S48 (the enclosing-loop FOLLOW term), S49 (the assertion exemption leaking to
`^`). All five are DETECTED by `run_possdiff.sh`; `make mech` prints the
matrix rather than this file quoting counts that would go stale.

Maintenance: update this file when files are added/removed or their roles
change.
