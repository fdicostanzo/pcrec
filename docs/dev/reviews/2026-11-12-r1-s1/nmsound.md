# nmsound findings

## Findings

### NMSOUND-1 CONFIRMED: `never_matches` says `empty-machine` on a char-step artifact that is not the empty scan
- Repro: `pcrec --features all -e utf8 --ucp --emit-facts --pattern '\b\B'` prints `never_matches ... empty-machine` (used=no) with `RX_ENGINE "dfa"`, `RX_DFA_SCAN "char-step"`.
- Expected per facts_listing.md §4.1.2¶12: `empty-machine` is "the test `<PREFIX>_DFA_SCAN "empty"` reads". On the island route that test does NOT pick the artifact: the `island` LOCATE row wins, so the char-step walk ships for a pattern the compile has proven matches nothing. kset.c `pcrec_never_matches` runs the pair test on the island machines (`j->engine == ENG_UNANCH`), and the emitter's row choice does not.
- Answers: correct (\b\B matches nothing in both). The cost is the doc parenthetical (the fact and the stamp disagree) plus a small speed loss: a proven-empty island pattern still walks the subject.
- Severity: doc (+ minor speed). Effort: small (either drop the parenthetical, or put the empty row ahead of the island row; the pair test holds on island machines, since 4 non-empty island patterns `\x{e9}\b`, `\b\x{e9}`, `\x{100}\B\x{101}`, `[^\x00-\x7f]\b` all read `no`). Blast radius: -e utf8 + UCP \b/\B patterns that never match (rare).
- Where: src/facts/kset.c:941-951; docs/spec/facts_listing.md §4.1.2¶12; src/gen/emit_dfa.c LOCATE table (island before empty).

### NMSOUND-2 CONFIRMED (design): `never_matches` is filed as an E2 CORE pattern fact, but it reads route state and machines, behind a second seal (`machines_final`) that runs beside the epoch mechanism
- facts.def:65 files it as `epoch 2, PF_CORE`. facts.h:345 defines CORE as "a walk of the sealed IR reading no prior and no other fact's choice", and facts.h:337 says "a fact may be asked only after its epoch's seal". `pcrec_never_matches` (kset.c:941) reads `Job.fit.chosen`, `Job.fit.prefilter`, `Job.engine` and the minimized (possibly collapsed, possibly `tagged`-swapped) machines. None of those is E2's sealed tree, and all of them are route CHOICES. So the epoch label is not what guards it: a separate bool, `Job.machines_final` (internal.h:3608), plus an internal-error `ctx_fail` does. That is a parallel seal beside `PfEpoch`, which already has `PF_E3_MACHINE`. That epoch is sealed only on ENG_UNANCH, which is why the fact could not be E3: the attempt route needs it too.
- Observable consequence (spec admits it, but it contradicts §1¶2's "what pcrec concluded about the PATTERN"): one pattern gets different values by route. `(a)\b(b)` reads `no` under `--engine=vm` and `empty-machine` under auto or `-fprefilter`. A future collapse-dependent case would vary with `-fprefilter-collapse` too.
- Hazard: a future reader that asks the fact between the E2 seal and the machine build gets an internal error (the guard works, which is good), not a decline. A future rung or reroute that rebuilds or swaps machines AFTER line 3285 (as `revend_choose_form` does before it) would silently read the wrong machines. The bool says "final" once, and nothing re-checks it.
- Suggest: a real machine-final seal in `PfEpoch` (E4, or E3 sealed on both branches with E3's own derivability rule), set by the driver at compile.c:3285; the fact's grain becomes route/artifact, not pattern; delete `machines_final`. Severity: design/maintenance. Effort: small to medium. Blast radius: the facts epoch vocabulary (facts_listing §4.1.1 `epoch` column, a promised vocabulary).
- Where: src/facts/facts.def:65, src/facts/kset.c:932-951, src/core/internal.h:3604-3608, src/core/compile.c:3285, docs/spec/facts_listing.md §4.1.2¶12 / §1¶2.

### NMSOUND-3 CONFIRMED (maintenance, trivial): the new dfa.c comment points to the wrong owner file
- src/ir/dfa.c, the header of `pcrec_dfa_pair_matches_nothing`, reads "the `never_matches` fact (src/facts/widths.c)". The fact's owner is src/facts/kset.c (`pcrec_never_matches`; facts.def:65 and src/facts/CLAUDE.md both say kset.c). Severity: maintenance. Effort: one word. Blast radius: none.

## SIBLING OF A FAMILY
Where "matches nothing" is concluded today:
1. The DFA LOCATE row `empty` (emit_dfa.c:10371, `locate_empty_applies`) on a DFA artifact.
2. The NEVER-MATCH switch: a hybrid becomes (1). It is the same predicate and the same emitter row, reached by a SECOND ROUTE. That is honest reuse, not a parallel mechanism.
3. A `-fprefilter` hybrid whose prefilter body is `empty` (RX_DFA_SCAN "empty" on a VM artifact). This is the old form, kept on purpose under do-or-die. It is the same predicate again.
4. The VM's root-minimum-width CEILING (`RX_VM_ROOT_MINW`, emit_vm.c:11784, "matches nothing"). That is the call-graph fixpoint, a different proof. FIND-MINW already folded its CHECK into the WIDTH slot (`CandWidth.ceiling`), so only the stamp, comment and listing row remain special. facts.h rightly refuses it as a `never_matches` value: INF and a saturated finite minimum share the ceiling. Note that the emitted comment's "matches nothing" claim has the same ambiguity.
5. derive.c's never arms (`is_never_leaf`/`never_node`, `PcrecDeriveReport.never`): an AST-level empty-class propagation on the compound's derived operand Q, with a different subject.
6. The island (char-step) machines: the fact proves them empty, but no row consumes the proof (NMSOUND-1).

Unify? (1) to (3) already are one. (4) should join the fact only once the width analysis carries an "infinite" bit separate from saturation. Then a value such as `unbounded-width` would be a true proof. (5) stays separate: its subject is a part, not the pattern. The fact's value set (an enum) is already the right shape for more proofs. The consumer table (the switch) should become a first-match table keyed on the proof, not on `PF_NEVER_MACHINE` alone.

## GENERAL FORM + UNLOCKS
General form: `never_matches` is a SET OF PROOFS (machine-empty, unbounded-width, root-derives-never), each a row with its own soundness argument. It has ONE consumer, the empty artifact, and the switch fires on any proof, not only on a hybrid's machines. Unlocks, each with its trigger:
- U1 `(?!)`, PCRE2's spelled-out FAIL idiom, is not proven: `(a)(?!)` stays a scanning hybrid (`never_matches no`). An empty-body negative lookaround lowered to the empty class is EXACT, and the existing machinery then proves it. Trigger: a nonzero count of `(?!)` in the harvested or bench corpora (counts only). Otherwise it is a BOONIES row.
- U2 VM artifacts with no prefilter (backreference, var, linked call) never get a proof: `(a)\b(b)\1` reads `no`, and the VM runs on every subject. A proof-only machine is a SUPERSET by construction: the construct is erased to "any bytes", which `frag_row`'s KTEXT_ANY already builds for a `consume` callout, so no prefilter ships. Trigger: a measured population of never-matching backref or recursion patterns. None is known, so BOONIES.
- U3 `unbounded-width` as a second proof (item 4 above), letting `(a(?1))` be the empty artifact instead of a VM with a stamped check. Trigger: the width analysis distinguishing INF from saturation for some other reason (e.g. FIND-MINW wanting exact W near the ceiling).
- U4 Context contradictions the pair test misses: `(?m)(a)$(?=b)` and `(a)$(?=b)` stay `no` (one-sided, so correct), while `(x)(?=a)(?!a)` is proven. Trigger: none in sight. Record only.
- U5 the island route consumes its proof (NMSOUND-1): empty before char-step. Trigger: already met if the doc sentence is to stay as written.

## PROBED-AND-HELD
About 75 pcrec compiles, all single and niced. Soundness of the switch (any pattern PCRE2 can match turned into the empty artifact): NONE FOUND.
- Premise "prefilter language ⊇ pattern language", by construction: read every `compile_ast` arm. Lookaround is erased (superset) or becomes an exact A_CTX. \K is exact. Atomic is erased (superset, positive context only). Backref, var and linked call get no prefilter, enforced by an internal error. Spliced calls are exact. Callouts get no prefilter: 3 patterns probed, all VM with no switch.
- Constructs the brief named but which pcrec does not implement (refused by name, so no hole): (*ACCEPT) x3, conditionals x2, newline verbs (*CR)/(*CRLF)/(*ANYCRLF) x3, \C \X \R x3. That is 11.
- One-char lookaround at the subject edges (absent side): 4 patterns correctly not empty (`(x)(?![\x00-\xff])` etc.). 3 true contradictions correctly empty.
- Caseless fold inside the ctx set: 2 patterns, 4 subjects, matching PCRE2.
- \G with left context at nonzero startpos (`(?<=a)\G(b)`, `\B\G(b)`, `(?<=a)\Gb`): 8 cases matching PCRE2. No \G-means-^ conflation.
- PCRE2 differential on switched or contradictory patterns: 7 patterns, 17 subject/startpos cases, all agree (`(a)\b(b)`, `(?=a)\Kb`, `(a)b\Gc` at startpos 0/1/2, `(a)$(?=b)`, `(?m)(a)$(?=b)`, `(a)\Z(?<=\n)`, utf8 `(\x{e9})(?<=a)`).
- \p{Greek} under byte (Script_Extensions puts \xb7 in it): 4 cases agree. No false empty set.
- Subroutines to {0}/DEFINE groups: 4 patterns, none falsely empty.
- End-anchor quirks (`(a)$\n`, `(a)\Z\n\Z`, ...): 4 patterns, none falsely empty.
- Stale state (part 2), by reading: the Job is calloc'd per attempt, so the fact cache and `machines_final` are fresh. Main machines are mandatory (an overflow is a ctx_fail and never interns as dead). Only `nedfa` is notempty. The tagged swap needs a clean optional build (`revend_fit`). The dfa memo key covers every Ctx field the builder reads. The build gate (`pcrec_artifact_has_dfa_scan`) equals the fact's own gate, so "prefilter true but no machine" (a calloc'd dfa with s0 == 0, which would read EMPTY) cannot occur.
- Forced routes: `--engine=vm` gives `no` with no switch; `-fprefilter` keeps the VM with an empty prefilter; `--engine=dfa` is refused as before; `-fprefilter-collapse` and a collapse population (`((a)|b){0,400}c\b\B`, 2 compiles) give a clean switch. `--emit-ir` on a switched pattern is a clean refusal. The `--emit-facts` force loop never hit "asked before final" in about 40 listings.
- Artifact parity: the switched artifact's stamps equal the native `--no-captures` empty artifact's, except NCAPS. The name table is kept, and the public entries are identical. `-futf-check` (-9) and startpos-guard (-7) refusals are identical to the `--engine=vm` artifact on 6 cases.
- Compound walk after the switch: 3 attempt-route switched hybrids, none became a compound (A1 holds).
- Island machines: 4 live patterns read `no` (the pair test holds there); 1 empty one is NMSOUND-1.
