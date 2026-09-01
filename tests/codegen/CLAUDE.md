# tests/codegen — structural assertions on generated code

Asserts that behavior-preserving optimizations are actually PRESENT in the
emitted C. These are not correctness tests (the .rxt corpus owns correctness);
they exist because checkpoint review R2 (finding R2-PR3) showed that three M2
optimizations — self-loop skip states, the anchored fast path, and DFA
minimization — could each be COMPLETELY disabled with zero signal from
`make test` or `make bench`. Behavior-preserving work needs structural tests
or it has no regression net at all.

## Files

- **run_trie_identity.sh** — DIFFERENTIAL codegen check for the M2.8
  alternation trie (R3.3). Builds a reference compiler from the same sources
  with `-DPCREC_NO_TRIE` (which forces `elig[j] = false` in nfa.c's A_ALT path)
  and diffs the emitted C over 500 generated alternation patterns. The trie is
  required to be OUTPUT-PRESERVING — subset construction plus minimization must
  erase it — so any difference is a rule-1/rule-2 soundness bug. No subjects, no
  gcc, ~4 s. Env: PCREC, CC, TRIE_N, TRIE_SEED, KEEP=1, SANFLAGS (SAN-1:
  extra flags appended to the from-source `$REF` reference build only —
  `$PCREC` is already overridable and carries the PRIMARY compiler-axis
  sanitizer coverage for free; see docs/testing.md "Sanitizer + lint
  battery" for a real finding (F1) this SANFLAGS wiring surfaced).
- **run_vm_identity.sh** — [M4.5b] THE ZERO-REGRESSION GATE (engine_m4.md
  §5.4, §13 P-7: "this one should be a GATE, not a prediction"). Its claim is
  that a capture-free pattern does not touch any new code — same AST, same
  NFA, same DFA, same emitter, same bytes — now that a second emitter and a
  capture AST node exist.

  It does NOT pin a historical commit, which is what §5.4's literal wording
  ("byte-identical to the pre-M4 emitter's output") would require: a check
  written that way fails the first time anyone legitimately changes the DFA
  emitter, which is a built-in expiry date and worse than no check because it
  teaches people to edit the pin. The permanent formulation compares the
  DEFAULT compile against `--no-captures` over every `pattern` line in every
  .rxt under tests/ (so the population grows with the corpus, not with the
  script), plus: `--no-captures` yields a DFA artifact for EVERY pattern, and
  `RX_NCAPS > 1 ⇒ VM` now holds NON-VACUOUSLY — that check had no population
  at all before [M4.5b] and this file's own [M4.4] note said so.

  ONE normalization, and it is ARITHMETIC rather than a filter: `rx_info.flags`
  legitimately differs by exactly the `PCREC_NO_CAPTURES` bit, so that bit is
  subtracted from the `--no-captures` side and every other byte must still
  match. Deliberately not a `grep -v` of "the stamp lines" — this project's
  recorded check-design failure is controls sharing a source with what they
  control, and its close cousin is a comparison loosened until it stops
  discriminating. Both compiles also use the SAME BASENAME in different
  directories, or the `#include "<name>.h"` line alone would differ (the exact
  trap run_trie_identity.sh documents at its own gen_a/gen_b — the first
  version of this script reported all 260 capture-free patterns divergent for
  precisely that reason).

  Also asserts the §5.6 override's refusals: `--engine=dfa` on a
  captures-default group-bearing pattern refuses AND names `--no-captures`,
  that named escape actually works, `--engine=vm` emits NO prefilter (D44/R21
  E-6 — without which tests/vm's differential is near-tautological), and the
  default hybrid DOES emit one (§4.7's cliff guard). 9 checks; sabotage S40.

  **The refusal-agreement arm carries ONE scoped, PINNED exception**
  (2026-08-17): a refusal from the VM's replication cap
  (`PCREC_MAX_VM_REPEAT_COPIES`) is a VM-only resource limit the
  `--no-captures` DFA path structurally lacks, so at exactly the cap the two
  sides legitimately diverge on acceptance — exposed when the D27 blinded
  corpus (df63549) landed `(a{1,3}){65}` precisely on the 64-copy boundary,
  which is D27 doing its job. The exception is keyed on the cap's own
  diagnostic text ("would replicate its body"), nothing wider, and the
  divergent population is PINNED at exactly 1 as its own check line:
  movement in either direction fails loudly (a new boundary pattern →
  re-pin upward deliberately; counter-K un-refusing the shape → re-pin to
  0 and consider retiring the arm — the counter rung makes emitted size
  count-independent, so this population is EXPECTED to go to 0 when it
  lands). Validated sabotages: pin expectation changed 1→2 fails the pin
  line alone; exclusion key changed to never-match fails TWICE (the
  original REFUSAL MISMATCH resurfaces AND the pin reads 0) — so the
  exclusion cannot silently swallow non-cap mismatches and its own removal
  is loud. Validation note recorded because the first attempt measured
  nothing: the sabotaged copies were first run from the scratchpad, where
  the script's own-path corpus discovery finds no population and the
  no-population guard's failure READ AS the sabotage firing — a control
  failing for an unrelated reason is this project's oldest check-design
  trap, and the fix was re-running from the script's real location.

- **run_endvar_identity.sh** — [M6.2] wave A's BYTE-IDENTITY GATE, the
  `run_trie_identity.sh` shape one closure view over. `\z` adds a THIRD view
  to the subset construction, and assertions_design.md §3.3 claims that costs a
  `\z`-free pattern NOTHING — same states, same tables, same bytes, BY
  CONSTRUCTION rather than by a `has_z` flag. The reference build is this
  tree's own sources with `-DPCREC_NO_ENDVAR` (the third view's INTERNING
  compiled out), not a pinned historical commit, for the reason
  `run_vm_identity.sh` states about its own formulation.

  **It exists BECAUSE the prose said the opposite thing first.** The design's
  first draft canonicalized `endvar` against the BASE view and argued zero
  regression from it; R30 finding E3 showed that makes every eol-differing
  state of every `$`-bearing pattern intern a live redundant `endvar`, so the
  artifact is NOT byte-identical — the exact opposite of the claim. "X is
  impossible by construction" is precisely the claim a construction check is
  for, and sabotage S69 restores the refuted form as the measured failing
  direction.

  **The positive control is SCOPED TO THE DFA, and the scoping is a finding.**
  The first draft required every compilable `\z` pattern to differ between the
  two builds and failed on `(\z)*` — a capture-bearing pattern, so a VM
  artifact, and the VM spells `\z` as a literal `if (pos == n)` and consults no
  view table at all. A `\z` pattern that AGREES must therefore be one the DFA
  never compiled, which the artifact's own `RX_ENGINE` stamp says (VM artifacts
  only). That is a different fact from the one being measured, which is why
  reading it to explain a non-difference is legitimate and reading
  `dfa_has_endvar` would not be. Landing figures at wave A: 1011 of 1011
  `\z`-free corpus patterns byte-identical, 18 DFA-compiled `\z` patterns
  differing, 0 DFA-compiled ones agreeing — read the current numbers from a
  run.

  **[M6.2 wave C] ITS SPLIT IS NO LONGER `grep -F '\z'`, AND THIS GATE IS WHAT
  SAID SO.** Wave A wrote the third closure view for `\z` and split on `\z`,
  which was exact at the time. BOTH `(?m)` anchors read that same view, for
  OPPOSITE purposes: `(?m)$` is "end of subject OR the next byte is a
  newline", so it reads `end_ok` to be TRUE there; `(?m)^` does NOT match
  after a newline that ENDS the string, so it reads `end_ok` to be FALSE
  there. So the day the `m` letter was accepted this gate went RED on 51
  patterns, every one a `(?m)` anchor sitting in the identity population where
  it does not belong. That is the check working: it caught a wave-C construct
  silently joining a wave-A mechanism, which no behaviour test could see
  (`-DPCREC_NO_ENDVAR` is never defined in a shipped build). The split now
  asks "does this pattern create a `pos == n` view" through
  `tests/lib/mlscan.py`'s `multiline_anchor`, and those patterns join the
  POSITIVE CONTROL, where they belong and where they strengthen it.

  Their arrival also gave that control a SECOND legitimate non-difference
  class, with its own anti-vacuity argument. `a(?m)^b` and `a(?m)^b|c` carry a
  `(?m)^` that can never hold (a `^` after a MANDATORY consumed byte), so no
  state's END view differs, nothing is interned, and the knob has nothing to
  disable. That is detected by reading the **UNSABOTAGED** artifact for an
  end-view table — and reading it there rather than in the reference build is
  the whole of what makes it admissible: `-DPCREC_NO_ENDVAR` is a
  reference-build-only flag, so a DEAD knob cannot make the subject build stop
  emitting those tables, and a broken knob therefore cannot grow this class.
  In the reference build the same read WOULD be `dfa_has_endvar`, which this
  script's own rule forbids.

**[M6.2 REPAIR SLICE, 2026-08-19] ALL FOUR GATES' REFERENCE KNOBS ARE NOW AT
THE ACTION, AND THIS PARAGRAPH IS THE ONE TO READ BEFORE ADDING A FIFTH.**
Wave D found that a knob-based reference is blind to any sabotage OUTSIDE the
region the knob suppresses, because both builds are compiled from the same
sabotaged sources — so the knob's PLACEMENT decides what the gate can see.
Waves A/B/C pinned a FLAG (`has_word`/`has_nl` in `src/ir/dfa.c`'s NFA scan);
S71 and S76 delete that flag's CONSUMER, so the refinement ran in both builds
and cancelled, and S71 was scored DETECTED only through an incidental
`-Wunused-parameter` in the reference build. Two things were then MEASURED by
the repair slice, and the second is the non-obvious one:

  - moving each knob to the EMITTER, wave D's own model, is NOT sufficient
    for waves A/B/C. `\G` refines no alphabet and interns no state the
    emitter cannot neutralize; `\b`/`(?m)` refine the ALPHABET and `\z`
    interns a STATE, and no emitter branch can undo either. With an
    emitter-only knob S71 leaves **1186/1186 `\b`-free artifacts
    byte-identical** — as blind as before.
  - what works is a `#ifndef` around the ANALYSIS'S ACTION (the refinement in
    `eqclasses`, the interning in `make_state`), which an edit to that
    action's own gate cannot cancel, PLUS an emitter half for the sites where
    the emitted text is what the construct decides. After both, all three red
    on their own gates through BYTES: **S71 1178 of 1186 differing, S76 1117
    of 1201**, and S69 failing `endvaridentity` — each with its corpus arm
    green, which is the semantics-preserving signature.

`-DPCREC_NO_ENDVAR` was ALREADY at its action (its `#ifndef` wraps the
interning block S69 edits) and did not move. The rule for a fifth gate: put
the knob around the ACTION the construct performs, never around the flag that
decides whether to perform it — and then run the row through
`tests/mech/run_sabotage_matrix.sh` rather than trusting the shape.

- **run_wordctx_identity.sh** — [M6.2] wave B's BYTE-IDENTITY GATE, the same
  shape one axis over. `\b`/`\B` are the largest change any wave of [M6.2]
  makes to the engine — the class map is refined by the word set, every state
  gains a second closure, the accept becomes class-indexed where it varies,
  and the machine gains a third start state — and the claim is that a pattern
  WITHOUT them pays for none of it. Reference build is this tree's sources
  with `-DPCREC_NO_WORDCTX`; sabotage S71 is the measured failing direction. Landing figures: 1039 of 1039 `\b`-free corpus
  patterns byte-identical, 47 controls differing, 0 unexplained agreements.

  **Its SPLIT is subtler than wave A's, and the difference is the file's own
  lesson.** `run_endvar_identity.sh` can split the corpus on `grep -F '\z'`
  because `\z` means one thing everywhere. `\b` does not: inside a character
  class it is BASE syntax for backspace (0x08), and `[\b]` is in this corpus
  today. A text split ignoring that would put `[\b]` in the CONTROL
  population, where it would correctly fail to differ and report a false
  alarm about a working knob. So the split scans for `\b`/`\B` OUTSIDE a
  bracket expression — on the pattern TEXT, deliberately not on anything pcrec
  computes — and prints both counts every run so the exclusion is visible
  rather than latent.

  **It also has a SECOND legitimate non-difference, found by running it.**
  `\b\B` and `\B\b` are contradictions (a position is a word boundary or it
  is not), so the emitter's "matches nothing" early-out produces an artifact
  with no automaton in it and the two builds agree for a reason unrelated to
  the knob. Classified rather than excluded, and read off the ARTIFACT (the
  `(void)s; ... return 0;` body) rather than off a maintained list of pattern
  texts — the same rule the VM arm follows.

- **run_mlinectx_identity.sh** — [M6.2] wave C's BYTE-IDENTITY GATE, the third
  in the family. `(?m)` adds a NEWLINE half to the class axis wave B built —
  the alphabet is refined by `pcrec_cls_newline` (D64's one definition), every
  state gains a third closure, the `pos == n` view goes live, and ENG_ATTEMPT
  gains D63's candidate-start prefilter — and the claim is that a pattern
  WITHOUT a multiline `^`/`$` pays for none of it. Reference build is this
  tree's sources with `-DPCREC_NO_MLINECTX`; sabotage S76 is the measured
  failing direction.

  **THIS ONE HAS A REASON THE OTHER TWO DID NOT.** Waves A and B each ADDED a
  view beside existing ones. Wave C turned a BOOL into a three-valued enum,
  rewriting every site that read `waccept`, `wlist` or `s1w`. A mechanical
  refactor of that size is exactly where a `UPC_PLAIN` becomes a `UPC_WORD` in
  one arm and nothing notices, and the corpus cannot see it unless the arm is
  reachable. This gate can, on every pattern in the tree.

  **Its SPLIT is subtler again, and for a third reason.** `\z` means one thing
  everywhere (a substring split); `\b` means two things (a bracket-depth
  split); `(?m)` means one thing but is SCOPED and spelled several ways —
  `(?m)`, `(?im)`, `(?m:...)` and `(?^m)` all set it while `(?-m)`, `(?im-m)`
  and a bare `(?i)` do not. So the scanner walks the option-run grammar
  `src/parse/mod_modifiers.c` walks (optional leading `^`, then letters, with
  everything after a `-` on the unset side) rather than looking for a
  substring. Deliberately not decided by anything pcrec computes: a split from
  `Dfa.clsctx` would be the check reading its own subject's verdict.

- **run_gstart_identity.sh** — [M6.2] wave D's BYTE-IDENTITY GATE, the fourth
  in the family and **the one whose REFERENCE KNOB IS PLACED DIFFERENTLY, for
  a measured reason the other three should be re-read against.** `\G` adds a
  third position bit to the closure and a SECOND FAMILY of interior start
  states (`Dfa.s1g[]`), which the ENG_ATTEMPT emitter turns into a three-way
  start dispatch, a `gseed[]` label table and a third `start_max` string; the
  claim is that a pattern without a `\G` pays for none of it. Its SPLIT is the
  simplest in the family — `\G` has one spelling and no in-class meaning
  (`[\G]` is PCRE2 error 107 permanently), so "contains the two bytes `\G`" is
  the whole classification, `run_endvar_identity.sh`'s shape.

  **THE KNOB IS AT THE EMITTER (`src/gen/emit_dfa.c`'s three decision points),
  NOT IN THE ANALYSIS.** The other three pin a `has_*` flag in
  `src/ir/dfa.c` — inside the code their own sabotages edit — and the
  reference compiler is built from THE SAME (sabotaged) SOURCES, so such a
  sabotage runs in BOTH builds and CANCELS. Measured by the wave-D lane:
  `run_wordctx_identity.sh`'s identity sweep stays **1135/1135 identical**
  under its own S71, and that script fails only because the deleted gate
  orphans a parameter and the reference build then warns. Forcing
  `gseed`/`gtbl` false and `a_gst = a_bot` at the emitter makes the reference
  build structurally the PRE-WAVE EMITTER, which no edit to the analysis can
  undo — after which sabotage S83 goes red in the sweep (93 of 1,175 patterns)
  as a byte-identity sabotage should.

  **It also earned its keep on the first run**: moving the knob immediately
  exposed a live defect in the wave's own emitter that the mis-placed knob had
  hidden — a `gseed[]` table emitted on every `\b` and `(?m)` artifact that no
  dispatch ever read. Nothing else in the tree could have seen it.

  **Its positive control is stated differently from wave C's, and the
  difference is deliberate rather than a weakening.** Wave C can demand that
  EVERY DFA-compiled `(?m)` pattern differ between the builds, because a
  multiline anchor always changes the alphabet. The reference build reads `\G`
  as `\A`, so a pattern for which those two really ARE the same machine —
  `\A\Gx`, or a `\G` on a branch that is dead either way — cannot be moved by
  the knob, and demanding it differ would be a check that is RED ON CORRECT
  BEHAVIOUR. Those land in an INERT bucket, read off the artifact (no
  `(start == startpos)` arm emitted) and printed one per line. That bucket is
  the weakest of the four and says so: it accepts the compiler's own verdict
  that a pattern needs no `\G` machinery, and what CHECKS that verdict is
  `tests/assertions/gpos.rxt`, where every pattern landing there has
  libpcre2-produced cells across the whole startpos sweep.

- **run_ir_listing.sh** — [M4.5c] DD-8's VM program listing (`--emit-ir`) held
  to the ARTIFACT it describes. engine_m4.md §10's constraint is that the dump
  derive from the same structure the emitter walks; the emitter satisfies that
  structurally (one event stream, appended by the primitives that write the C),
  and this checks it anyway, because the structural argument holds only while
  there is genuinely one call. Each listing SECTION is pinned to a fact
  derivable from the `.c`: the label SET both directions and duplicate-free,
  every `RX_PUSH` with its resume target, the set of `slot_values` slots actually
  written, the header's RX_NCAPS/frames/trail against the artifact's own
  macros, and the island/callout counts against the artifact rather than
  against the listing's own claim (so those sections begin working the day a
  producer exists rather than needing a rewrite). Also pins `--emit-ir`'s
  refusal on a pure-DFA artifact — an as-built decision, §10 and DD-8's row
  are silent — and holds `--trace` to the property its own source comment
  claims: the instrumented artifact must agree with the plain one on every
  answer, trace on stderr, and the plain one must trace nothing.

  It found a real drift on its FIRST run: the accept label was emitted by a
  direct `sb_printf`, so the artifact carried a label the listing did not.
  That is the entire failure mode §10 names, and it existed for the length of
  one commit.

  The trace check's plain/traced binary runs (a handful per pattern, not an
  inner loop) go through `gen_run` (`tests/lib/gen_timeout.sh`,
  `WATCHDOG_SECTION=codegen`), the shared run budget plus a 512m RSS
  ceiling and a `build/watchdog.log` line per run.

  It carries a NON-DEFAULT `--prefix` case for a second reason found the same
  way: every other check here uses the default `rx`, which cannot see a
  hardcoded `RX_` in the listing's own text — and there was one, so a
  `-p myrx` listing named a `RX_NCAPS` macro the artifact does not contain.
  When a check's fixture is the default of the thing it checks, it is blind to
  exactly the class of bug that only shows up off the default. 78 checks
  ([M4.5e]'s figure — read the current count from a run rather than this
  line, per this file's own standing note below on hand-copied counts);
  sabotages S41 and S42.

  Runs under `make test-vm`, not `make test-codegen`, for a measured reason —
  see the note below.

- **run_lookaround_identity.sh** / **lookaround_classify.py** — [M6.6.2]
  module `lookaround`'s BYTE-IDENTITY GATE and the grammar-aware classifier
  that splits its population. Two modes since wave B+C (bucket by default,
  pure-refactor on demand) and a THREE-part positive control; the classifier
  is a scan and not a grep because `(?=` in a class is three literal bytes and
  `(?<name>` is a named group. Full entry: the `[M6.6.2]` section below. Opt-in
  as `make test-lookaround-identity`, never part of `make test`.
  **RETIRED 2026-08-24 ([DD-14] wave A, main 0c75c96):** the ABI event
  (PCREC_ERR_RECURSE / ERR_FLOOR −5 / PCREC_ERR_INTERNAL) changed every
  artifact's `#define` block, and this gate's reference is pre-`A_LOOK` by
  construction (its positive control (a) refuses anything newer), so no
  valid pin exists past that commit. The script now REFUSES with the
  explanation when the subject tree carries `PCREC_ERR_INTERNAL`; its last
  valid run is recorded at [M6.6]'s close (1a8541e). Successor: the
  [DD-14] four-axis identity gate (subroutines_design.md §9, wave E),
  pinned at post-wave-A main.
- **run_dfa_stamps.sh** — [DD-13] (2026-08-25), widened by [DD-13c]: the D46
  SELECTION STAMPS (`RX_ENGINE`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`;
  `docs/spec/match_api.md` §6.3), each held to the LOOP IT NAMES. Runs under
  `make test-codegen` as a third script beside `run_codegen_tests.sh` and
  `run_trie_identity.sh`. Compile-only (no `gcc`), one `awk` per artifact,
  ~70 s over the whole corpus. Two halves:
  - **NAMED WITNESSES** whose expected value is spelled out in the
    file — one per documented value, including `(?:...)\z` for the
    `-bounded` pair and `\B\b` / `^\B\b` for `"empty"` on both engines
    ([DD-13c]; the anchored one is NOT in the corpus, so nothing but that
    row tests it) — plus three VM rows for the hybrid iff. They pin the
    MECHANISM; the sweep below pins AGREEMENT, and agreement is a property
    two wrong answers can also have (an emitter that stamped `"none"`
    everywhere AND emitted no prefilter anywhere would sail through a pure
    agreement check).
  - **A CORPUS SWEEP** over every `pattern` line in every `.rxt`
    (2,772 on this tree, floored at 2,620, `LC_ALL=C`, K35), asserting:
    exactly one of each stamp per DFA artifact, `RX_ENGINE "vm"` on every VM
    artifact, [DD-13c]'s hybrid IFF in both directions, every value inside
    the documented set, and stamp-equals-loop on both axes for every
    artifact that CONTAINS a DFA scan (DFA artifacts and VM hybrids alike).
  - **THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS.** Every
    verdict is derived from the EMITTED MATCHER TEXT — the `memchr` call,
    the `can_begin_match` walk, `start_max`, the skip's bound — which
    `emit_unanchored`/`emit_attempt` write, while the macros come from
    `emit_dfa_stamps`/`pcrec_emit_dfa_scan_stamps`. Different code paths, so
    a drifting stamp is a red. The engine discriminator is `goto rx_L0;`
    (the VM's program entry), NOT `RX_ENGINE`: reading the macro to decide
    which artifact kind to check the macro on is the circularity the file
    refuses in a comment. The HYBRID discriminator is the same kind of
    thing — the emitted DEFINITION `static int rx_prefilter(const unsigned
    char *subject, ...`, the line `emit_search_head` writes when emit_vm.c
    asks emit_dfa.c for a scan under a private name.
  - **[DD-13c] THE RUNTIME MIRRORS ARE HELD TO THE MACROS HERE**, because
    this is the script that already compiles the whole corpus:
    `rx_info.scan`/`.prefilter` must equal `RX_DFA_SCAN`/`RX_DFA_PREFILTER`
    on every compiled artifact of BOTH engines (2,483), reading
    `NULL`/`"none"` where the macros are absent. A THIRD source in the same
    one-pass `awk` — struct-literal initializer lines, neither `#define`s nor
    matcher text. The LINE COUNT is asserted too (exactly one of each): the
    validation showed that without it, fields that stopped being emitted made
    the value comparison vacuously true and the check green.
  - **[DD-13c] THE VM HALF IS AN IFF, NOT A PROHIBITION.** The old rule was
    "no `RX_DFA_*` macro on a VM artifact", and it was wrong about the §6.1
    hybrid, which inlines a full DFA scan and (since [DD-13c]) stamps the
    two lines for it. Asserted both ways with both populations printed: a
    VM artifact carries them IFF its emitted text contains that inlined
    body IFF `RX_VM_PREFILTER` is `"hybrid"`. The middle term is matcher
    TEXT, so neither `#define` is ever checked against the other alone, and
    the check refuses to pass if either side of the iff has no members
    (an iff with an empty side asserts only one implication).
  - **THE EMPTY-ENGINE BUCKET IS NAMED AND COUNTED, NEVER FILTERED.** Four
    corpus patterns (`\B\b`, `\b\B`, `\d\b\w`, `a\bb`) are proven to
    match nothing, so their search function is one `return 0` with no loop.
    The bucket is an EXACT NAMED MANIFEST of those four (r37 #2: a floor of
    one answers "did it vanish", never "is it the right set"), and since
    [DD-13c] its members are ASSERTED on the scan axis — `RX_DFA_SCAN
    "empty"` — rather than exempted from it, plus the prefilter assertion
    it always had (no loop => the stamp must read `"none"`).
  - **Validation (made to fail on purpose, four ways):** scan value
    inverted → 386 red; the `-bounded` arms dropped → 92 red; the whole
    stamp call removed → the presence checks red on 2,022 artifacts; the
    witness table pointed at a VM artifact → red, because each witness
    asserts its artifact IS a DFA one before reading its value.

- **run_premul_table.sh** — [OPT-3] (2026-08-26) the PRE-MULTIPLIED DFA
  TRANSITION TABLE (`docs/design/premultiplied_dfa_table.md`,
  `docs/spec/tuning.md` §2.13), held to the artifact rather than to its stamp.
  Its OWN section, `make test-premul-table`, part of `make test` and
  deliberately NOT of `make smoke` — it sweeps the whole corpus AND compiles
  and runs sixteen matchers (~6 min), which is the same argument
  `run_endvar_identity.sh` and `run_ir_listing.sh` already carry for running
  under other sections.
  - **WHY IT EXISTS.** The transform is ANSWER-PRESERVING BY CONSTRUCTION —
    it changes the ENCODING of a state, not the machine — so the whole `.rxt`
    corpus, both oracles and every differential agree whether or not the
    emitter got it right in the ways that matter. Three failure modes, none
    of which an answer comparison can reach: the state variable left `int`
    (gcc reinstates the `movslq` the transform exists to remove; the artifact
    is CORRECT and the optimization buys nothing); the generation-time bound
    not switching; and a cell that is not premultiplied, or a sentinel that
    collides with a real value.
  - **THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS.** Every
    verdict comes from the EMITTED MATCHER TEXT — table declarations, table
    cells, the state variable's declaration, the transition line — with the
    stamp compared against it. The two come out of different write sites
    (`dfa_table_name` writes the macro; `emit_tr_table`/`emit_acc_table`/
    `emit_unanchored` write the tables and the loop). **The CLASS COUNT is
    read from `rx_*_byte_class`, a different table written by a different
    emitter function**, because §5's whole invariant is "every cell is a
    multiple of the stride" and taking the stride from the transition table
    would make it a tautology.
  - **Six sections**: named witnesses one per documented value; the bound on
    both sides WITH a non-vacuity assertion that the swept family straddles
    it; the corpus sweep (the [DD-13c] iff both ways, stamp vs declarations,
    the bound per machine, the ACCEPT TABLE'S LENGTH as an independent second
    witness of the form, and the SHAPE); the cell invariant; and the deny
    flag's answer identity, which EXCLUDES a pattern whose scan carries no
    numeric table rather than counting it as an equal pair.
  - **Validated in three failing directions** (each planted, rebuilt, run,
    reverted; clean baseline 15/0): the table not premultiplied → **13/19**
    with §5 red on 14,387 of 39,787 cells and §1/§2/§3 correctly GREEN (they
    read declarations, the plant changed cells); the sentinel colliding →
    **12/5**, and it took breaking BOTH bound conjuncts, since the range one
    still refuses on its own — with §5 GREEN, because the corpus's largest
    machine is 40,010 entries and cannot carry a collided cell, so the BOUND
    arm is what makes a collision unreachable and the CELL arm cannot see
    this defect; the state variable left `int` → **14/1**, §3's shape arm
    ALONE on 1,824 machines, with every answer unchanged.
  - **The first run of this file found five defects in ITSELF**, and they are
    worth reading before writing the next check here: a witness table split
    on `|`, which is a pattern byte; a DFA-scan discriminator keyed on "has a
    table", which called the four empty-engine artifacts stamp-without-a-scan
    (r37 finding #5 read backwards — the [DD-13c] iff is about CONTAINING a
    scan, and a body that is one `return 0` contains one); an `awk` field
    index reading a variable's NAME where its TYPE was wanted, which reported
    3,744 shape violations on a correct tree; a drift count with no names
    beside it; and a flag row comparing one form with itself.

- **run_offset_skip.sh** — [OPT-K] (2026-08-28) the OFFSET-k CANDIDATE-START
  SKIP (`docs/design/offset_k_skip.md`, `docs/spec/tuning.md` §2.14), held to
  the artifact rather than to its stamp. Runs under `make test-codegen` as a
  fourth script in that group; compile-only apart from §1, ~10 s.
  - **WHY IT EXISTS.** The mechanism is ANSWER-IDENTITY-PRESERVING BY
    CONSTRUCTION — every test it adds to a candidate start is a NECESSARY
    condition of a match beginning there — so the whole `.rxt` corpus, both
    oracles, every differential AND `make test-axes` agree whether or not the
    emitter ever selects it. Sabotage S187 is that made real: the selection
    never fires, the tree stays green, and the row's MEASURED 4.5×-17.1×
    is gone. Five failure modes are enumerated in the file's header; the
    other four are the form selected where it was measured NOT to pay, the
    stamp and the arithmetic drifting apart, the byte-frequency prior no
    longer summing to one (which no artifact shows), and the deny flag
    leaving a trace.
  - **THREE SOURCES, NEVER TWO.** The expected k-set for each of the four
    witnesses is a LITERAL in the file, read from the design note's §4.7, and
    BOTH the `RX_DFA_PREFILTER_OFFSETS` stamp AND the emitted `rx_ofsskip`
    helper are compared against it. `dfa_prefilter_offsets` writes the macro,
    `pf_block_ofs` writes the helper, a human wrote the table — so any two of
    them drifting is red. §1 asks the SHIPPED ARRAY through the shipped
    library (`pcrec_byte_freq_total_ppm`) rather than re-summing the source
    literals, which would be a second transcription agreeing with any typo it
    shared.
  - **IT IS PAIRED WITH `tests/offsetskip/offset_skip.rxt` AND BOTH FILES SAY
    SO.** That corpus owns the emitted skip's ARITHMETIC and would pass on a
    compiler that had stopped emitting the skip; this file owns the
    POPULATION. Neither substitutes for the other, and the patterns are the
    same on purpose.
  - **Validated in four failing directions** (planted, rebuilt, both
    instruments run, reverted; clean baseline 19/0 here and 80/0 in the
    corpus): the resume off by one → **19/4** here and **79/1** there; the
    reseed deleted → **18/1** and **79/1**, the corpus case a FALSE MATCH; the
    selection never firing → **14/5** and **80/0 GREEN**, which is the point of
    the file; the prior no longer summing to 1e6 → **18/1** and **80/0**.
  - **THE FIRST PLANT MEASURED ZERO IN THE CORPUS AND THAT IS THE LESSON TO
    CARRY.** The resume off-by-one left `offset_skip.rxt` 75/75 green: its
    overlapping-candidate rows EXERCISE the resume line and cannot DETECT a
    change to it, because losing a match needs the pattern to allow its own
    scan byte BEFORE the offset it is scanned at, and none of the four
    witnesses can. The corpus gained `[-a]{3}-b` for exactly that.

- **run_anchored_match.sh** — [ENG-ABS] (2026-08-29) the ANCHORED MATCH-HERE
  FORM (`docs/design/anchored_match_unwrapped.md`, `docs/spec/tuning.md`
  §2.15), held to the artifact rather than to its stamp. Its own section,
  `make test-anchored-match`, part of `make test` and NOT of `make smoke` —
  `run_premul_table.sh`'s measured argument, plus a second compiler build for
  its §4.
  - **WHY IT EXISTS.** The form is ANSWER-IDENTITY-PRESERVING (§3's argument),
    so the whole `.rxt` corpus, both oracles and `make test-axes` agree whether
    or not the emitter ever selects it. The ANSWER half is
    `tests/anchored/run_anchored_diff.sh`; this file owns the POPULATION and
    the SHAPE, and the two name the same mechanism on purpose.
  - **§2 IS r39's MISCOMPILE-1 ONE ROW OVER.** A candidate-start prefilter is a
    set derived for the SCAN role; reusing it in a MATCH-HERE body would skip
    past `ctx->pos` and report no match where one begins. The section reads the
    `<prefix>_match` BODY for all three prefilter mechanisms and asserts the
    artifact's own `<prefix>_search` carries one — so the negative cannot be
    satisfied by a compiler that emits no prefilters at all.
  - **§4 EXISTS BECAUSE THE OVERFLOW ARM'S POPULATION IS ZERO**, measured, not
    assumed: the DFA caps are shared and the mandatory machines reach them
    first. A fallback nobody can reach is a fallback nobody has tested, so §4
    builds a reference compiler with `-DPCREC_ANCHORED_MAX_STATES=6` (that
    knob's ONE consumer, `src/core/limits.h`) and drives real patterns through
    the arm: no diagnostic, the stamp flips, and the artifact is the
    `-fno-anchored-dfa` build's to the byte.
  - **§5's FLOORS ARE THE POINT.** The form silently ceasing to be selected
    leaves every answer right, `make test-axes` green (with nothing to deny the
    two builds are one build) and the row's measured gain gone. Census at
    landing: 2,786 corpus patterns — 1,489 vm, 288 refused, 825 unwrapped, 180
    search-filter(attempt), 4 search-filter(empty), 0 search-filter(overflow).
  - **Its own first run found two defects IN ITSELF**, both worth reading: a
    witness reading `RX_NCAPS` off a SPLIT output, where that macro lives in
    the `.h` and every grep returned the empty string (the row passed its own
    guard for the wrong reason); and a byte comparison that differed only in
    the `#include "<basename>.h"` line — the trap `run_trie_identity.sh`
    documents at its own `gen_a`/`gen_b`, met a third time.

- **run_form_census.sh** — [CHK-2] piece 3 (2026-08-26) THE FORM CENSUS:
  compiles every `.rxt` corpus pattern twice (default engine, and
  `--engine=vm` forced where accepted — the wider population for the
  VM-only stamps) and counts artifacts per STAMP VALUE for every stamp
  `docs/spec/match_api.md` §6.3 documents plus its two joint
  distributions, printed beside the verdict (the K39/[OPT-4] style). A
  DIFFERENT KIND of check from `run_dfa_stamps.sh` and
  `run_premul_table.sh`, which also count populations as a BY-PRODUCT of a
  structural stamp-matches-loop check: this script's own claim is "has
  every value in the spec's own vocabulary been produced by SOMETHING in
  this tree" — a FLOOR for every value the corpus reaches (K35: rounded
  down generously) and a REQUIRED, BUILT, ASSERTED synthetic witness for
  every value with ZERO corpus population, checked by a completeness loop
  rather than a hand-picked exclusion list. **Measured 2026-08-26: 2,772
  corpus patterns, 135s at `PROCS=4` uncontended.** Two values — `"mixed"`
  (tuning.md §2.13's own documented likely gap) AND `"indexed"` (found
  live by the completeness loop, undocumented anywhere as a gap) — have
  ZERO corpus population; both covered by synthetic witnesses
  (`[01]*1[01]{13}` for "mixed", `(?:[a-z]+)@(?:[a-z]+)` with
  `-fno-premul-table` for "indexed" — the deny flag as a direct
  controllability lever, not a second pattern search). The census also
  found a THIRD `RX_VM_PRUNE_CEILING` value live (`"none"`, 1,047 of 1,488
  VM artifacts), not enumerated as a value-set table in §6.3 the way
  `RX_DFA_PREFILTER`'s is, floored as an observed fact rather than
  asserted complete against a documented set. Runs as part of
  `make test-axes` (opt-in, alongside `tests/axes/run_axes.sh`) rather
  than `make test-codegen`, despite fitting under its 2-minute budget in
  isolation — the two share the opt-in/heavy-battery placement.
  **Detect demonstration** (docs/dev/learnings.md §3): `dfa_table_name`
  (src/gen/emit_dfa.c:2288) sabotaged in a scratch copy to never return
  `"mixed"`; the census FAILS TWICE — the witness's own local check and
  the completeness loop independently — naming the exact value and the
  exact witness pattern. Full transcript in the script's own header.

- **run_tiered_entry.sh** + **tier_driver.c** — [OPT-1] (2026-08-25) the
  TWO-TIER DEFAULT ENTRY (`docs/design/two_tier_entry.md`,
  `docs/spec/match_api.md` §10.9). OPT-IN, `make test-tiered-entry`, NOT in
  `make test`: its §2 compiles the whole corpus and its §3 builds and runs
  four matchers. The behavioural half rides `make test` already — every
  existing differential compares answers through the un-suffixed entries, so
  a tier that changed an answer is red across the suite, not only here.
  - **THE FAILURE IT IS BUILT AGAINST, named before the code was written:
    an answers-only check for this change passes on a build where the
    optimization is ABSENT.** An artifact whose fast tier is secretly bound
    at the stamped default answers every subject correctly and escalates
    never. So the boundary is derived THREE ways per subject and the three
    are compared: the escalation counted at the escalation SITE (under
    `-DRX_TEST_TIER_HOOK`, which the artifact declares as an `extern`
    FUNCTION — a mutable static in an artifact is a TS-1 failure and a
    §5.3 breach, so the counter lives in the driver); the give-up predicted
    by `<prefix>_search_in` at the FAST capacities, which is the same
    capacity guard reached through an entry [OPT-1] does not touch; and
    `gcc -fstack-usage`'s real frame, which is the only one of the three
    that can tell a working optimization from an absent one.
  - **THE DEPTHS ARE FOUND, NOT ASSUMED.** The five boundary subjects (1,
    FAST-1, FAST, FAST+1, DEFAULT) are located by bisecting through
    `_search_in`, so a change to the frame layout, `VM_FAST_TIER_BYTES` or
    `vm_cost`'s ratios moves what this file tests. A hardcoded `9` would be
    green forever and mean nothing after the first re-sizing.
  - **§2 IS A BICONDITIONAL, checked in both directions**: tiered code
    present ⇔ `FAST_FRAMES < RESUME_FRAMES`. Population 2,758 corpus
    patterns (986 dfa, 1,215 vm single-tier, 272 vm tiered, 285 refused),
    counted and printed, with a separate assertion that the TIERED side is
    non-empty — a biconditional only ever checked on its trivial side is a
    vacuous pass. The engine discriminator is `goto rx_L0;`, not a stamp,
    for run_dfa_stamps.sh's circularity reason.
  - **THE FLOOR (r38 finding 3a), and it is the arm to read first.**
    Everything else in this check bounds the fast tier from ABOVE only —
    `FAST <= RESUME`, the biconditional, §4's frame — so a derivation that
    SHRINKS leaves all of them green while the tier degrades to
    escalate-on-everything. The stamp and the bind move together and this
    file reads both, so it could not see it. Three arms: (A) the tiered
    corpus population floored at 250 (measured 272) and printed; (B) every
    tiered artifact must FILL its page budget to within one frame + one
    trail entry of the integer rounding, read off the artifact — this one
    is DERIVATION-INDEPENDENT, asserting the property the scaling exists to
    produce rather than re-implementing the scaling; (C) nothing tiers below
    `VM_FAST_TIER_MIN`. **Validated by halving the derivation: floor B alone
    went red on 271 of 271 tiered artifacts at 16 passed / 1 failed, with
    every answer and span still correct.**
  - **§6, THE MULTI-GROUP WITNESS (r38 3b).** `((a)|(aa))+b`, `RX_NCAPS=4`,
    60 consecutive depths, 37 escalating, first at n=24 (a 25-byte subject).
    `tier_driver.c` `memcmp`s the WHOLE capture array against `_in` at the
    default descriptor, because §10.9 promises returns AND spans and the
    specimen's single whole-match group is too weak to carry that — on it
    "the spans agree" is nearly implied by "the returns agree".
  - **Validation (made to fail on purpose, MEASURED 2026-08-25, planted in
    a scratch emitter and removed):**
    (i) the fast tier bound at the STAMPED DEFAULT ("it never escalates") →
    §3(b) red on 2 of 6 depths (n=9 and n=342: predicted 1, counted 0) and
    §4 red on both arms (entry frame 131,248 B) — **while §3(a)'s answers
    stayed GREEN on all 6 depths and §2 stayed green**, which is the
    measured proof that neither an answers-only check nor the structural
    sweep would have caught it.
    (ii) `FAST_FRAMES`/`FAST_TRAIL` stamped at the default while the tiered
    code is still emitted → §2 red on **272 artifacts** (every tiered one in
    the corpus), `mismatch-code-tiers-stamp-says-one`, AND the non-empty
    -population arm fires too, which is the guard against §2 passing vacuously.

- **run_codegen_tests.sh** — greps ONE ENGINE'S BODY (extracted by entry name;
  see below) for each optimization's
  signature (skip tables + skip loop, `start_max = 0` for fully-anchored
  patterns and its ABSENCE for partially-anchored ones, memchr prefilter,
  a table-size ceiling that only holds if minimization ran, engine selection
  for `$` vs `^`, and the M2.12 EOL-path checks: skips present and bounded at
  n-1, reverse skip entry guard, memchr bounded at n-1, and an ORDER check
  that accept/EOL evaluation follows the skips), plus the OS-0b multi-engine
  block. **Since [STD1] phase A (D37, 2026-08-13)** also a WHOLE-FILE check
  (the stamp sits above any engine function, so `body()` does not apply):
  `--features std1` stamps `/* Feature set: std1 (modules: classes,modifiers) */`
  plus the `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` macros in the .c, the
  paired `.h` carries the comment but never the macros, and a bare
  invocation still stamps something rather than nothing. **[STD1b]
  (2026-08-13) re-baseline:** phase A's bare invocation stamped `"none"`
  (the pre-flip default constant); the bare default is `std1` now, so the
  bare-invocation check flipped to expect
  `/* Feature set: std1 (modules: classes,modifiers) */`, and a second
  check was added for `--features none` stamping `"none"` explicitly (the
  escape hatch, unaffected by the flip) — 33 checks before, 34 at [STD1b].
  **[M4.4] (D44.2/D44.5, 2026-08-14) re-baseline: 37 checks.** The
  `<prefix>_span` out-struct retires (D44.2) for a caps-array
  `<prefix>_search` parameter, so the OS-1 entry-point-signature grep and
  the multi-engine fixture's hand-written second-engine declaration both
  update to the new signature; the multi-engine block's "exactly once per
  file" assertion now targets the fixed ABI-types block's
  `#define PCREC_RX_ABI_H` line instead of the retired span typedef, and
  its duplicate-emission assertion INVERTS (see below); a new check builds
  two DIFFERENTLY-PREFIXED generated headers together in one TU (D44/A-2's
  own positive control); and two new structural checks assert
  `rx_info.ncaps == RX_NCAPS` and `RX_NCAPS > 1 => VM` (D42.2/D44.5, §11
  item 9 of docs/design/match_api_m4.md), both live from this commit and
  trivially green pre-[M4.5] since `RX_NCAPS` is 1 on every artifact this
  DFA-only emitter produces. Part
  of `make test`;
  env: PCREC, CC, GENCFLAGS, KEEP=1, LINTGEN=1
  (SAN-1: rides this GENCFLAGS compile with `gcc -fanalyzer`, opt-in),
  CLANGGEN=1 ([CC-CLANG]: the same shape one compiler over — defaults CC
  to clang unless already set, opt-in; the K24 noclone check is
  gcc-specific by design and reads differently, not wrongly, under it).
  **[M4.7c] (2026-08-17)** added two more `rx_info` cells beside the
  ncaps/engine pair above: `pattern_len` is the pattern's ordinary byte
  count for `'abc'` (3), and — the cell that would catch a field silently
  reporting the MATCHED-byte count instead of the SOURCE-byte count —
  `'a\nb'` (4 source bytes: `a`, `\`, `n`, `b`) stamps `pattern_len = 4`,
  not 3 (the bytes the matcher itself walks). The K9 repro proper (an
  embedded NUL, the field's whole reason for existing — docs/dev/known_issues.md
  K9) cannot be expressed here at all, since argv has no way to carry a NUL
  through to `pcrec`; it lives as a direct library-API C probe in
  tests/cli/run_cli_tests.sh case16.

  **[K35], 2026-08-25 ([DD-14] close): it also carries the LOCALE GUARD,
  and that check is not about codegen at all** — it lives here because this
  is where the tree's structural checks live. It sweeps every
  `tests/**/run_*.sh` for a `sort` used as a COMMAND WORD and fails naming
  any site guarded by neither an `LC_ALL=C` prefix nor an `export LC_ALL=C`
  ABOVE it — the export's POSITION is load-bearing and the check tests it,
  because an export below a sort guards nothing. It counts SITES and
  GUARDED sites per LINE, so a line carrying two sorts with one guard is
  caught rather than passed. Measured 2026-08-25: 62 sites across 53
  scripts, all guarded; floors of 50 sites / 40 scripts make a COLLAPSED
  sweep a failure rather than a pass (the population that vanishes is the
  check that cannot fail). Validated in three failing directions before
  landing: an unguarded site, a script whose export was moved BELOW its
  sorts, and an empty population. WHY IT IS A CHECK AND NOT A CONVENTION:
  the hazard was written down once, at `tests/cli/run_cli_tests.sh:786`,
  and recurred five times anyway.

  **[K37]/[TT-9], 2026-08-25 (srRun2, [CHK-1]): two more structural checks
  live beside K35, same reasoning — neither is about codegen, both are
  where the tree's structural checks live.**

  **[K37] THE BARE-COMPILER-CALL GUARD.** Sweeps `tests/**/*.sh` for the
  compiler token (`build/pcrec`, `$PCREC`, `"$PCREC"`) and fails naming any
  site that is neither structurally excluded (a comment, a `PCREC=`
  assignment, an `[ -x/-f "$PCREC" ]` existence test), guarded
  (`pcrec_run`/`"$TIMEOUT_BIN"`/`gen_run`/`gen_cc` on the line), nor a
  match for one of six reasoned, per-entry-validated ALLOWLIST regexes
  (a diagnostic message, an env-var prefix onto a self-recursive or
  python-worker invocation, an argument two positions past the command
  word, a grep pattern string, a python heredoc argument, a bash -c
  positional argument). Measured 2026-08-25: 55 scripts / 427 sites (372
  guarded, 31 allowlisted across the 6 categories, all non-vacuous);
  floors 40/380. Fixes docs/dev/known_issues.md K37 — see
  `tests/lib/CLAUDE.md`'s `gen_timeout.sh`/`pcrec_run` entry for the
  mechanism this check guards.

  **A SELF-REFERENCE TRAP FOUND DURING VALIDATION, worth reading before
  writing a sixth structural check in this file.** The FIRST version of
  this check's own source — its regex literals, its allowlist reason
  prose — contained the literal text `$PCREC` and `build/pcrec`, so the
  check's own definition lines matched its own site regex and it failed
  against ITSELF (9 sites, all inside its own block). Not the standing
  "control shares a source with what it controls" trap (this check reads
  no verdict pcrec computes) but its textual cousin: a check whose PATTERN
  TEXT contains its own SEARCH TARGET is scanning itself. Fixed by writing
  the dollar sign as a bracket expression (`[$]PCREC`, not `\$PCREC`) and
  one letter of "pcrec" the same way (`pc[r]ec`) — identical regex
  semantics, no contiguous byte match — and rewording prose to say "the
  PCREC variable" rather than spell `$PCREC`. Demonstrated: reverting any
  `[$]` back to `\$` makes the check fail against itself again.

  **[TT-9] THE SANITIZER SUITE LIST.** Every `tests/*/run_*_diff.sh` must
  be in `tests/lib/san_scripts.txt` (see its own header) or a stated
  exclusion; today's exclusion set is empty — the enumeration found all 9
  belong in the manifest, including 5 that were silently absent from
  `ubsan`/`asan`/`san`'s old hand-copied lists (`tests/lookaround/`'s two
  and three `tests/assertions/` diff scripts the same search surfaced).
  Floor 5 (measured 9).

  **BOTH VALIDATED red then green** (a scratch
  `tests/altcls/zz_k37_validate_tmp.sh` carrying one bare `"$PCREC" --help`
  call; a scratch `tests/altcls/run_zz_validate_diff.sh` not in the
  manifest — both created, observed as the sole named failure, deleted).

  **[SABANCHOR], 2026-08-26 (srAnchor): tests/mech/CLAUDE.md's own standing
  tripwire, `scripts/m6read_check_sab_anchors.py`, now runs HERE as a FAILING
  check** rather than living as an ad-hoc script someone has to remember to
  run by hand. srTier's two-tier default entry ([OPT-1]) and the DFA scan
  stamps ([DD-13c]) moved the emitted text three sabotage rows anchor
  against — S67 (`src/gen/emit_dfa.c`'s `strategy_denials` mask gained a
  member after the ALTCLS pair), S179 and S183 (`src/gen/emit_vm.c`'s
  `_search_in` bind/delegation, whose surrounding format-string arg list
  shrank) — and a battery script outside this tree caught all three
  ANOMALY at a run's start; nothing IN this tree would have. The check
  reads the tripwire's own `sabotages checked: N` line as its population
  (floor 150, measured 180) and fails on either a stale/unreadable anchor
  or a collapsed population, so a future refactor that moves an anchor is
  caught by `make test-codegen` the moment it lands rather than by the next
  full `make mech` sweep (up to ~50 min) or a battery author's memory.
  **VALIDATED red then green** in a scratch copy of the tree (`git archive
  HEAD` extracted outside the repo, never the live `tests/mech/sabotages/`):
  planting a stale `SAB_BEFORE` on S01 reproduced the check's exact bad
  branch (`STALE ANCHORS: 1`, exit 1), reverting reproduced the ok branch
  (`all 180 anchors resolve`, exit 0).

## [M4.5b] re-baseline: 38 checks, and three narrowings worth reading

Three checks in `run_codegen_tests.sh` had to move when the VM engine landed,
and in each case the fix is a NARROWING that adds coverage rather than a
loosening that removes it. Read them together, because they are the same
lesson three times: a check written when only one shape existed can encode
that shape by accident.

1. **The minimization check's group is now `(?:...)`.** It was
   `(get|post|put|delete|patch)`, and the group was incidental to what the
   check measures (a DFA table's size) — until D42.1 made captures the
   default, at which point the capturing spelling routes to a VM artifact
   where the table lives in `rx_prefilter`, not in the `rx_search` body
   `body()` extracts. A NEW companion check then asserts the same alternation
   in its CAPTURING spelling gets a minimized table inside the prefilter,
   which is coverage that did not exist before: the hybrid runs the same
   forward+reverse pair through the same passes, so a minimization bug scoped
   to that path was previously invisible.

2. **`body()`'s anchor accepts an optional `static`.** The VM's prefilter is
   the same emitter's output under a private name and a different storage
   class, and it must be per-engine extractable for exactly the reason every
   other body is.

3. **TS-1 now distinguishes a static FUNCTION from a static OBJECT.** D19's
   property is "no mutable file/function-scope STATE", and a function has no
   storage to race on — but while every emitted `static` was a table, "static
   and not const" and "mutable state" were the same set and the check could
   not tell them apart. A VM artifact emits five static functions and keeps its
   whole mutable working set in a LOCAL of the search entry, which is what D19
   asks for. The discriminator is C's declarator syntax (a `(` with no `=`,
   `;` or `[` before it), not a list of known function names, so
   `static unsigned char rx_tbl[256] = {` — S06's sabotage, a table with its
   `const` dropped — still has no `(` at all and is still caught, and so is
   anything of the shape `static int rx_counter = f(0);`.

   S02 and S06 were RE-RUN through `tests/mech` after these edits, because a
   narrowed check whose sabotage was validated against the wide version has
   not been validated at all.

## THREE scripts here run under a DIFFERENT section, and the reason is measured

`run_endvar_identity.sh` ([M6.2] wave A) runs under `make test-assertions`,
on exactly the argument the two below run under `make test-vm`: it builds a
reference compiler and sweeps the whole corpus through BOTH builds, which is
minutes rather than seconds, and `make smoke` includes `test-codegen` and is
already at its 60s target. It lives HERE because it is an identity
differential, kin to `run_trie_identity.sh` by technique; it runs THERE
because that is the module whose claim it gates. `make test` runs it either
way.

## Two scripts here RUN under `make test-vm`, and the reason is measured

`run_vm_identity.sh` and `run_ir_listing.sh` live in this directory because
they are identity and structural differentials — kin to `run_trie_identity.sh`
by technique — but `make test-codegen` does not run them. `make smoke`
includes `test-codegen`, and the two cost 8.0s and 2.9s against this section's
own 0.7s + 7.4s (measured 2026-08-15). Leaving them here took `test-codegen`
from 9.33s to 16.28s and `make smoke` to 62.98s, against a documented 60s
target; moving them to `test-vm` puts smoke back at 54.76s.

docs/testing.md asks for exactly this re-check whenever a section grows, and
records the second finding the measurement turned up: smoke was ALREADY over
its target on the main this lane merged, dominated by `test-known-fail`'s
23.26s — a section that used to be nearly free, and is not this directory's to
fix.

`make test` runs all four scripts either way; only the section wrapper moved.

## Engine-scoped greps, and why a whole-file grep stopped being enough (OS-0b)

Every symbol these checks look for is a function-local static or a statement
inside the engine function — that is the measured finding OS-0b rests on, and
it is what lets several engines share one file under D18/D20. It is also what
makes a whole-file grep wrong as soon as there IS more than one engine:
`rx_forward_stay[0-9]+\[256\]` would be satisfied by ANY engine present, so a check
reading "this pattern emits a skip table" degrades to "some engine in here
does" while still passing. All 19 grep sites across 11 generated files now run
against a body extracted by entry name (`body()`).

An extractor is itself a thing that can silently break, so it is not trusted on
inspection. The multi-engine block builds a two-engine file by hand — the
fixed ABI-types block once for the file, a distinct entry name per engine,
every other identifier
untouched, i.e. exactly the transformation an engine finder (OS-0) will apply —
and requires a scoped grep to find the skip table in the engine that HAS one
('.*=.*') and NOT in the engine that does not ('^a|b'). A `body()` returning
the whole file fails the second; one returning nothing fails the first. The
block also compiles the fixture under GENCFLAGS.

**[M4.4] (D44.2/D44/A-2) INVERTS the duplicate-emission assertion, on
purpose.** Before the API break, duplicating `emit_span_typedef`'s call
broke the build (gcc: `error: conflicting types for 'rx_span'`, since each
occurrence declared a fresh anonymous struct; confirmed under -std=gnu11
and -std=c99) — the emit-once rule was load-bearing because nothing guarded
re-inclusion. The fixed ABI types (`rx_ctx`, `rx_matchfn`, `rx_group_entry`,
`rx_info`, ...) are wrapped in a PREFIX-INDEPENDENT `#ifndef PCREC_RX_ABI_H`
guard instead (the R21 panel MEASURED that a per-prefix guard fails the
exact case it exists for: two differently-prefixed generated headers in one
TU, each deriving a DIFFERENT guard name, both bodies re-defining the fixed
types), so the property worth asserting flipped: duplicating the WHOLE
guarded block (guard included) must NOT break the build anymore, and the
codegen suite's own positive control for the guard's necessity is instead
the two-differently-prefixed-headers check below.

Validated sabotages for run_codegen_tests.sh (37 checks pass clean, as of
[M4.4] — read the current count from a run rather than this line, which has
already drifted at least once). Each was
applied to a FRESH tree, with the edit asserted to have landed before the tree
was built:

| sabotage (exact edit) | result |
|---|---|
| `int nout = 0;` -> `int nout = 0; return 0;` in `pick_skip_states` (skip states off) | 7 fail — the 6 pre-OS-0b skip checks, unchanged by the scoping, plus the multi-engine control reporting its fixture can no longer discriminate |
| in `body()`, `$0 ~ "^int " fn "\\(" { inside = 1 }` -> `{ inside = 1 }` (extractor returns the whole file) | 3 fail, incl. "scoped grep attributed engine A's skip table to engine B" |
| replace only the attribution-step extraction: `&& body "$WORKDIR/multi.c" rx_search_b ...` -> `&& cp "$WORKDIR/multi.c" ...` (isolates scoping from fixture construction) | 1 fail — the attribution check alone |
| [M4.4] `tests/mech/sabotages/S04_duplicate_typedef.sh`, RETARGETED: neuter the `PCREC_RX_ABI_H` guard (`#ifndef PCREC_RX_ABI_H` -> an unconditional `#if 1`) | 2 fail — the D44/A-2 cross-prefix compile check and the OS-0b duplicated-block compile check; a single-prefix artifact still compiles, so nothing else regresses |
| in the fixture's rename, `s/\brx_search\b/rx_search_b/g` -> `.../rx_search/g` (engines keep one name) | 1 fail — compile, `error: redefinition of 'rx_search'` |

## The OS-1 checks assert an ABSENCE, which the corpus cannot

Case folding (D23) is behaviour-preserving in the direction that matters here:
a corpus can prove `-i abc` matches `ABC`, but nothing in it can prove the
match cost nothing. The OS-1 checks assert the emitted shape instead — that
`-i 'aBc'` is byte-identical to `'[aA][bB][cC]'`, that a letter-free pattern is
untouched by `-i`, that no `tolower`/`0x20`-style conversion appears anywhere,
and that the entry-point signature is unchanged (a compiled-away option must
not surface at run time, D18). Implement caselessness as a runtime check and
every one of them fails while the corpus stays green.

These comparisons use `-o -` and, since [M4.4], compare the `rx_search`
ENGINE BODY (`body()`-extracted) rather than the whole file. That is not
tidiness: writing two files emits two different `#include "<name>.h"`
lines, so a whole-file comparison would differ for a reason unrelated to
folding — the same trap `run_trie_identity.sh` documents at its
`gen_a`/`gen_b`, and the reason the first version of these checks used
`gen` and failed. **[M4.4] added a second, structurally similar reason to
scope down to the engine body specifically**: `rx_info` (D43.1) embeds the
source pattern text and the compiled `flags` word unconditionally, and
both legitimately differ between two different pattern spellings (or
between `-i` and no `-i`, even on a pattern `-i` has no folding effect on —
the flag is still set as compiled) — the same "the stamp differs by
design" shape D37's [STD1] case9/case10 already established in
`tests/cli/`. D18's zero-cost claim was always about the AUTOMATON
specifically, which is exactly what `body()` extracts; comparing the whole
file would now fail these checks for a reason that has nothing to do with
whether folding leaked into the runtime.

`run_trie_identity.sh` also sweeps its 500-pattern corpus TWICE, once
case-sensitive and once with `-i`. Folding rewrites the bitmaps the trie keys
on — `Cat|CAT|cat` goes from three unrelated branches to three identical ones —
so the folded sweep drives rule 1's accept split and rule 2's disjoint-run
logic down paths the unfolded corpus never reaches.

| sabotage (exact edit) | result |
|---|---|
| move the `cls_casefold` call in `p_class` from before the negation to after it | 1 codegen check (`-i '[^a]'` is not `'[^aA]'`) + 6 caseless.rxt cases |
| delete the `cls_casefold` call in `char_node` (classes still fold, literals do not) | 1 codegen check + 14 caseless.rxt cases |
| `if (cls_has(b, c) \|\| cls_has(b, c + 32))` -> `if (cls_has(b, c + 32))` (fold one direction only) | 1 codegen check + 8 caseless.rxt cases |
| in run.sh, drop the `-i` mapping so `flags i` becomes a no-op | 21 of 56 caseless.rxt cases |

## TS-1 guards a property NOTHING else in the repo can see

D19's rule is "usable FROM threads, never threaded". For generated code that
reduces to two mechanical facts — every emitted `static` is `const` (so it is
.rodata with a constant initialiser: no lazy init, nothing to race on) and the
output references no non-reentrant or allocating libc. Both hold today by
construction, and both are invisible to correctness testing.

The sabotage numbers make the point better than the prose. Making every emitted
table a NON-CONST static fails 8 TS-1 checks and **zero** corpus cases: the code
compiles, matches identically, and passes the entire suite while being
thread-hostile. That is the memoisation-cache / hoisted-scratch-buffer /
diagnostics-counter failure mode, and under D18 also a selector that caches its
choice in a global.

The sweep covers 18 emitted files across 9 emission shapes (both engines, EOL
and non-EOL, both prefilter kinds, skip states, the never-matches path,
case-folded, and `--emit-main`), plus the paired `.h`. The file count is itself
asserted, so a sweep that quietly stops generating stops passing.

| sabotage (exact edit) | result |
|---|---|
| `static const unsigned char %s_%s[%d]` -> `static unsigned char %s_%s[%d]` in `emit_u8_table` | 8 TS-1 checks, **0 corpus cases** |
| `size_t pos = startpos;` -> `size_t pos = startpos; (void)errno;` in `emit_unanchored` | 6 TS-1 checks (+ the OS-0b compile check, incidentally, because `errno` also needs a header it does not get) |

Line 1 of each file is stripped before scanning — it echoes the user's pattern
verbatim, so a pattern named `malloc` would otherwise fail its own denylist.
The scan does not strip C comments, so an emitted comment that merely mentions
a denylisted symbol will trip it; that is deliberate, and the fix is to reword
the comment rather than to weaken the list.

The M2.12 additions are the sharpest illustration of why this directory
exists: reverting the EOL path to its M2.7 state (no prefilter, no skips —
~76x slower on `$` patterns) fails 6 checks here while the .rxt corpus still
passes 53/53, because the change is behavior-preserving by construction.

## Two kinds of check live here

`run_codegen_tests.sh` asserts a SIGNATURE is present in the output — cheap,
but it only ever proves the optimization ran, never that it was right.
`run_trie_identity.sh` asserts EQUIVALENCE against a reference build with the
optimization off, which proves soundness across hundreds of patterns at once.
Prefer the second shape whenever an optimization is supposed to be
output-preserving; the M2 journal wrongly concluded M2.8 was not structurally
testable, and the equivalence check turned out to be both possible and far
stronger than the corpus (a broken disjointness guard shows up on a handful of
.rxt cases and on 64 of 500 patterns here — the measured figures and the exact
edits behind them are in the sabotage table below). The ".rxt cases" half of
that figure was measured at 2 when this was written and is 6 today
(alternation_trie.rxt grew) — which is MECH-1's founding example of a
hand-copied count going stale silently. Current figures for EVERY sabotage in
this file come from `bash tests/mech/run_sabotage_matrix.sh` (S01..S14 cover
this directory); the tables below keep the exact edits and the lessons, and
the generator owns the numbers.

An equivalence check has its own trap, and the fix for it is not optional: if
BOTH builds had the optimization off, every comparison would agree and the
script would certify a deleted optimization. `run_trie_identity.sh` therefore
carries POSITIVE CONTROLS — patterns whose NFA fits the cap only when factored,
so the two builds fail at different stages — and they are sabotage-validated.

**There are three of them, at 4, 8 and 256 branches, and the small ones are the
important ones.** The first version had only the 256-branch control while every
generated pattern had 3..8 branches, and a critic broke it in one clause:
`elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` left all three checks
green, `make bench`'s KEYWORD-SCALE green, and the whole `make test` suite green
with the trie deleted for every hand-written pattern. A control that only proves
the optimization fires OUTSIDE the corpus's own range proves nothing about the
corpus. When adding an equivalence check, put a control inside the range of the
inputs it actually compares.

## [M6.2 wave B] the three `\b` rules, and why none is a correctness test

`run_codegen_tests.sh` gained an `[M6.2-WORDB]` block of three rules from
`assertions_design.md`, each of which is invisible to every oracle in the
tree — this file's whole charter, three more times:

1. **§3.6.2 — never index an accept table at `pos == n`.** Two axes select an
   accept bit (the VIEW axis by position, the CLASS axis by the next byte),
   and at end of subject there IS no next byte, so the accept is the view's
   SCALAR one. Getting it wrong reads `s[pos]` at `pos == n` — an
   out-of-bounds read in EMITTED code, K27's class — and usually changes NO
   answer, because the byte one past the subject is often readable and often
   lands in a class with the same bit. Checked two ways, because either alone
   is weak: every class-indexed read must go through the guarded `cl` local,
   AND the `pos >= n` guard (with the scalar accept inside it) must precede
   the first such read. Sabotage S73.
2. **§3.8.3.1 — no `match_start_position` at the reverse boundary except through the
   context-indexed accept, from ANY writer.** The design states an invariant
   rather than a patch because there is more than one writer: the reverse
   SKIP's `match_start_position = pp;` is emitted under a COMPILE-TIME condition, so what
   lands in the artifact is a bare unconditional assignment with no runtime
   test to fail. The check enumerates every `match_start_position` assignment in the body
   and requires each to be conditioned on an accept read. A companion rule
   (2b) pins R30 N9: the boundary accept must be ATTACHED to the `rewind_position <=
   startpos` break, because the loop has a SECOND exit (dead state) and an
   epilogue below it would record a position the walk never reached and index
   the accept table with a negative state. Sabotage S72.
3. **§7.2 item 3 — one word-set spelling per artifact.** Whatever `\w` means,
   `\b` must agree with, and the only way to guarantee that is one definition
   with two readers. A second copy changes nothing the day it lands and drifts
   the day one is regenerated.

**The FIXTURE is `\bx.*y\b`**, and the choice is load-bearing: it is the only
shape carrying every emitted site at once — class-indexed accepts in BOTH
machines, mechanism 4's seed in both, AND live forward and reverse SKIP
states. Rule 2 is about the skip, so a fixture without one would satisfy it
vacuously, and the check asserts the skip's presence rather than assuming it.

## [M6-READ] `run_object_neutrality.sh` — the two-compiler gate

Added 2026-08-21 as conversion step 2, BEFORE any emitter change. It sweeps
every `pattern` line in every `.rxt` under `tests/` (the population grows with
the corpus, `run_vm_identity.sh`'s formulation) through TWO pcrec builds,
compiles both artifacts at `-O2 -g0`, and compares:

  **(a)** raw `.text` + `.rodata` bytes — executed code, which contains no
  names at all. This is the property that matters.
  **(c)** exported symbols — [M6-READ] promises zero ABI change, and this is
  the line that enforces it.
  **(b)** all symbols, reported as INFO only. Renaming a static function or a
  function-local static table renames its internal-linkage symbol; that is not
  executed code and does not survive `strip`, but a check diffing disassembly
  TEXT fails on it. The sample stage's first version did exactly that and
  produced 200 lines of diff in which every line was a symbol name.

**It is NOT in `make test`**, and cannot be: it needs a second compiler. It is
a tool pointed at two builds. That also makes its reference STRONGER than the
`*_identity.sh` family's — those build a reference from the same sources with
a `-D` knob, which wave D measured can CANCEL a sabotage; this one takes a
genuinely independent binary, sharing no sources with its subject.

**Its own non-vacuity has two arms.** A sweep that compared nothing fails
loudly (`same == 0`), and a pattern one build refuses while the other compiles
is a REFUSAL MISMATCH rather than a skipped row. But the sharper control is
self-arming and arrives with the conversion: after the rename, **(b) must be
NON-ZERO** while (a) and (c) stay clean. If (b) came back 0 from a converted
emitter, the gate would be reading artifacts the rename never touched.

Baseline recorded at step 2, current build against itself: 33 of 40 patterns
compared (7 refused by both), (a) and (c) clean, **(b) = 0** — which is
correct for a self-comparison and is the number the conversion must move.

## [M6-READ] the SLOTS block's non-vacuity guard, and the sabotage that earned it

Added 2026-08-21, **before** any emitted identifier was renamed, because the
rename is what makes the hazard live. `run_ir_listing.sh`'s SLOTS block
compares two extractions that are both pattern-matched SPELLINGS the emitter
writes: `RX_SET(<slot>` in the `.c`, `set slot_values[n]` in the listing. Renaming
them together is the only CORRECT way to rename them — and doing so makes
both greps match nothing, after which `diff -q` on two empty files passes.
The check would go on reporting green while reading neither side.

This is the failure this project already has in its own memory (a control
sharing a source with the thing it controls), and [M6-READ] is a live
occasion for it in two independent ways: the listing's prose moves with the
emitter's variable names, and the artifact stops writing `RX_SET(2,` at all
once the slot legend lands (`RX_SET(RX_SLOT_GROUP1_START,`).

Three things now hold the block open:

1. **Per-pattern non-emptiness, asserted on BOTH sides.** Every pattern in
   `PATTERNS` has at least one capturing group, so every one must write at
   least one slot; an empty extraction is a failure with its own message
   naming which side went blind.
2. **Symbolic operands are RESOLVED against the artifact's own `#define`s**,
   so the block keeps working across the slot-legend change instead of
   needing a flag day — and an operand that resolves to nothing is a hard
   failure, not a silently dropped row.
3. **A sweep-wide guard for CHOICE POINTS**, which cannot assert
   non-emptiness per pattern (a fully-possessified pattern legitimately
   pushes no frame) but across this sweep must find some.

**Measured, both directions** (run from this directory — see the scratchpad
warning below, which this lane walked into before getting it right):

| state | old check | new check |
|---|---|---|
| unsabotaged | 79 pass / 0 fail | 80 pass / 0 fail |
| listing side moved only (`set slot_values[n]`) | 68 / 11 — already caught | 69 / 11, message names the listing |
| **BOTH sides moved** (the real post-conversion state) | **79 / 0 — all 11 SLOTS checks comparing empty against empty** | **69 / 11, message names the `.c` side** |

The middle row is why the guard is not redundant: the one-sided sabotage was
always caught, so a validation that only tried that one would have concluded
the block was already safe. Only the both-sides case is vacuous, and it is
the case the conversion actually produces.

The guard also found a live defect in the extraction on its first run: the
old numeric-only grep was matching `RX_SET`'s own `#define` line and silently
dropping the operand because the macro PARAMETER name (`slot_`) is not
`[0-9]+`. Resolving symbolic operands made it visible. `#define` lines are
now excluded explicitly.

## **[M6.4.2] `run_atomic_identity.sh`, and the ONE gate here whose reference is a PINNED COMMIT**

> **[M6.4.4]: THIS ONE IS OPT-IN.** It is not in `make test`, not in
> `make test-atomic`, and not on the `ubsan`/`asan` lists — `make
> test-atomic-identity` runs it. The design ruled it a ONE-SHOT LANDING gate
> (§11.2, §14 item 8) and the pinned reference below is exactly why that
> reading is right: every run re-answers the same question about a moment that
> has passed, and the answer cannot move unless someone edits PRE-MODULE code.
> Its archived result lives in docs/testing.md, "The atomic landing gate". The
> four `-D`-knob gates above are NOT affected: their references track the
> current tree, so they are standing invariants and stay in `make test`.
> It also has no sanitizer axis to offer — it never runs a generated matcher,
> it compares emitted C as TEXT.

The fifth `run_*_identity.sh`, and the paragraph above ("ALL FOUR GATES'
REFERENCE KNOBS ARE NOW AT THE ACTION") asks to be read before adding one. Its
answer for this module is that **no knob placement works, because there is no
action to place one around.** The four predecessors each gate an ANALYSIS
ACTION — a refinement in `eqclasses`, an interning in `make_state`, an emitter
dispatch — and the knob works because the action runs on the population under
test. Module `atomic-groups` refines no alphabet, interns no state and reads no
byte it did not already read as part of a body: its whole surface is "is there
an `A_ATOMIC` in the tree", which is FALSE for every pre-module pattern. A knob
would gate code that never runs on the identity population, so the sweep would
report 100% identical no matter what was sabotaged — the blindness that
paragraph warns about, in its purest form.

So the reference is built by `git archive` from a PINNED PRE-MODULE COMMIT,
`probe_kreset_identity.sh`'s precedent ([M6.2] wave E). It shares NO SOURCES
with the subject, so no sabotage of this tree can reach it — which also makes
it strictly stronger than a knob build, and is the direct answer to wave D's
own finding that a knob build's sabotage CANCELS.

**Three guards keep it from going vacuous**, and the third is this module's
own. The pin must RESOLVE (a gate that cannot build its reference SAYS so
rather than skipping); the reference tree must not contain `A_ATOMIC` (a
mistyped commit resolving to something recent would build a reference that
agrees everywhere); and the POSITIVE CONTROL is the refusal-mismatch column —
the pre-module compiler cannot compile an atomic pattern at all, so a run
reporting zero differing AND zero refusal mismatches has lost its atomic
population or is comparing two builds of the same tree.

Landing figures: **1311 default and 1312 `--engine=vm` atomic-free corpus
patterns byte-IDENTICAL, 0 differing, 0 refusal mismatches, 96 atomic patterns
all refused by the reference.** K29's fix genuinely does move emitted bytes for
`X{n,}` on the counter rung with a positive §2.2 verdict, and the gate was
written expecting an exception bucket for it — but NO corpus pattern is in that
family (0 of 1448), so it asserts a flat zero and the bucket was DELETED rather
than kept "just in case". A differing-but-expected bucket is exactly the thing
that quietly absorbs the next real difference.

## **[M6.4.2] the `[M6.4-ATOMIC]` block: five rules plus 5b and 5c**

Every rule matches **BOTH SPELLINGS OF A CUT** and **CALL SITES**, and both are
corrections the R31 panel forced rather than caution. `vm_revdet_rep` cuts by
assigning `run->resume_depth = <prefix>_rvN_frame_mark` and never touches the
`RX_CUT` macro — `vm_cut`'s own header records a step-charge probe that
"reported a confident zero for the revdet rung" for exactly that reason. And
`#define RX_CUT(slot_)` is emitted UNCONDITIONALLY on every VM artifact, so
`grep -c RX_CUT` is at least 1 on every artifact pcrec has ever produced.
MEASURED on live artifacts before the rules were written:

| pattern | `grep -c RX_CUT` | `'^ *RX_CUT('` | second spelling |
|---|---|---|---|
| `a*+b` | 1 | 0 | 0 |
| `(?>a*)b` | 1 | 0 | 0 |
| `(?:a|bc)*+d` | 1 | 0 | **1** |

The first two are the CURSOR rung, frameless and correctly cutless; the third
is REVDET. A rule spelled "the artifact contains `RX_CUT`" is green on all
three and would be green on a compiler emitting no cut at all.

**Rule 1 asserts on TWO SOURCES because R31 E3 showed one is satisfiable by a
half-done edit.** The design's first form of RULE H3 edited `v.mrl_win` and
called the artifact's `RX_VM_PRUNE_CEILING` stamp the check — but that flag was
read only by the stamp and the `--emit-ir` text, while the lines that BUILD the
ceiling were gated on `prefn` and `nclamp` and never on it. Measured by making
exactly that edit: **the stamp reads "subject-end" (1(b) GREEN) with both
`window_end = window[0][1]` assignments still live (1(a) RED)**. It is also
SCOPED to `nclamp > 0` (R31 C5): the stamp is three-valued, and an unscoped
rule is RED on the four correct `"none"` artifacts in every 46-pattern R3a
sample. Rule 1c is the other direction — an atomic-FREE artifact must KEEP its
ceiling, or rule 1 would pass on an emitter that switched it off for
everything.

**Rule 5 drives BOTH PREFERENCES on all six dispatch paths**, which is R31's
re-check N1: the cursor rung SATISFIES cut-equivalence (it is frameless) and
still answers the wrong language on a lazy body, so a greedy-only per-path
check would have been green on the lift that miscompiles 7 of 8 lazy cells.

**Rule 5c is E4/S98's detector, and it found a live bug during the lane.** Every
`RX_CUT(n)` must name a slot the artifact's own legend declares a CUT MARK.
With RULE 3's condition-(d) decline written into `vm_rep` alone, `vm_count_slots`
took the revdet arm while the emitter took the frames arm, and
`-fno-possessify '(?>(?:a|bc){2})d'` emitted `RX_SET(RX_SLOT_REVDET0_ENTRY, …)`
and `RX_CUT(2)` onto the revdet loop's OWN entry slot — two live loops sharing
one slot, which is the failure `vm_count_slots`' header names. Its failing
direction was then demonstrated by reverting the fix (2 CUT-NOT-A-MARK).

## [M6.5.2] the `[M6.5-DUPNAMES]` block, and `run_backref_identity.sh`

**`[M6.5-DUPNAMES]` — the reflection table's ORDER, read off the ARTIFACT.**
With `(?J)` the `rx_info.groups` table can hold ADJACENT ROWS WITH EQUAL NAMES,
and `docs/spec/match_api.md` §6's caller algorithm (bsearch, walk BACK to the
run's first row, then FORWARD to the first participating one) selects the
LOWEST-numbered participating member ONLY IF the within-name order is
ascending. Get it backwards and the table encodes the "last set" rule
`backrefs_design.md` §8.3's `"xyy"` cell rules out — while the emitted matcher
still implements "first set", so the two disagree and NO match-semantics test
can see it.

**WHY IT IS STRUCTURAL RATHER THAN A BEHAVIOURAL `.rxt` CELL**, and this is
R32's re-check finding: without the number tiebreak, whether the emitted order
is wrong depends on TWO unspecified properties agreeing — `qsort`'s stability
and the direction `Ctx.named_groups` is walked in. `mod_named_groups.c`
PREPENDS and `emit_dfa.c` walks from the head, so on glibc (a stable merge
sort) a name-only comparator yields DESCENDING numbers within a run. A check
that depends on that coincidence is not a control. Reading the order off the
ARTIFACT depends on neither.

**STRICTLY increasing, not merely non-decreasing**, and that is the COMPARATOR
TOTALITY half: a comparator returning 0 for rows that differ in NUMBER would
leave them in whatever order the sort produced, and two rows equal in BOTH
fields would be a duplicate the table must never contain. The ORDER half is
live exactly when a dup-name pattern is compiled; the TOTALITY half is
exercisable on every fixture with two or more names, which is why the fixture
set has both kinds and asserts EXACTLY 5 tables of which EXACTLY 3 carry a
duplicated name. Failing direction demonstrated: with the tiebreak removed,
three fixtures go red naming the offending row pair. Sabotage S120.

**`run_backref_identity.sh` — the module's byte-identity gate, and the SECOND
one here whose reference is a PINNED COMMIT.** Same ruling and same reasoning
as `run_atomic_identity.sh` (ASK-4, ruled with R32): a knob-built reference is
sabotaged too, and here a knob would be worse than weak — NO STAGE OF THIS
MODULE RUNS ON THE CONTROL POPULATION, so it would gate dead code and the
sweep would report 100% identical whatever was sabotaged.

**THREE AXES, and the third is this module's own.** Under `--no-captures` the
parser now builds an `A_CAP` for EVERY numbered group and deletes the
unreferenced ones at end of parse (§6.3, because a FORWARD reference makes
"will this group be referenced" unanswerable at the opening paren), so "the
tree is what it always was" is a claim about a DELETION rather than about code
that never ran. **That axis found a real defect on its first run**: the
resolution pass's early return skipped the strip for a backref-FREE pattern, so
every `--no-captures` artifact with a group emitted different bytes while
answering identically — which is exactly the class of defect only an identity
sweep sees.

**IT COMPARES PAST D37's THREE FEATURE-STAMP LINES**, with the filter asserted
to remove EXACTLY three from each side, and that is the precedent `tests/cli`
case10 set rather than a loosening. `render_modules` (src/parse/enabled.c)
renders the enabled module list by walking the registry in TABLE ORDER and
taking each module name at its FIRST row; this module adds two rows naming
module `recursion` at `RK_ESC 'g'`, well before the `RK_GROUP` rows where that
name previously first appeared, so under `--features all` the stamp's list
moves `recursion` earlier. The mask, the gate state and D37's own promise (the
stamp's value can be passed back to `--features`) are order-independent, and
case14 is where the stamp's CONTENT is pinned.

Result at landing: default 1501/0, vm 1502/0, nocaptures 1501/0 identical, with
the positive control at 124/124 backref-bearing patterns REFUSED by the
pre-module compiler.

## [M6.6.2] `run_lookaround_identity.sh` — module `lookaround`'s gate: BUCKET mode by default since wave B+C, pure-refactor mode on demand

**The THIRD gate here whose reference is a PINNED COMMIT**, and the one where
the pin is not merely preferable but the only possibility. `LOOKAROUND_
IDENTITY_REF` defaults to `eacac76`, [M6.6.2]'s branch point — the last tree
whose `struct Ast` carries the per-kind fields at top level, before D70's
tagged union. A `-D` knob could not build this reference even in principle: a
refactor has no gated region, and no knob can make one build use `n->rmin` and
the other `n->u.rep.rmin` without BEING the refactor.

**IT HAS TWO MODES, AND WAVE B+C FLIPPED WHICH ONE IS THE DEFAULT.**

`STRICT_ALL=1` was wave 0's claim and is STRONGER than the one a module gate
normally makes: D70's refactor was ~250 mechanical access-site renames with
zero behaviour change, so the assertion was not "a lookaround-FREE pattern is
unmoved" but that EVERY pattern in the population is unmoved, on the FULL RAW
STDOUT with no stamp strip. **That mode goes red BY CONSTRUCTION the moment a
lookaround compiles** — `(?=`, `(?!` and `(?*` patterns now build and the
pinned reference refuses every one — which is a correct answer to the wrong
question. It is KEPT RUNNABLE and kept documented, because it is the right
mode for the next change of that kind (a rebase of wave 0 onto a moved base,
any later pure refactor), and a red under it should be read as "the mode does
not fit this tree" before it is read as a defect.

`STRICT_ALL=0` is the default since wave B+C and is the ordinary module-gate
claim: **a lookaround-FREE pattern's emitted bytes did not move.** The
population is split by `lookaround_classify.py` and only the FREE bucket is
compared, on all four axes.

**THE STAMP STRIP IS ALLOWED IN BUCKET MODE AND ASSERTED, NOT TRUSTED.**
`run_backref_identity.sh` is entitled to filter D37's three feature-stamp lines
because a MODULE legitimately moves them, and this wave is such a module. So
the three lines are stripped — and the strip REPORTS HOW MANY LINES IT REMOVED
and requires exactly three on each side of every compiled comparison. A filter
that quietly removed four would be absorbing precisely the difference the gate
exists to report; a wrong count is its own failure class, `STAMP FILTER`.
Under `STRICT_ALL=1` nothing is stripped and a stamp-only difference is a
FINDING for the manager.

**FOUR AXES** (ASK-4): `default`, `--engine=vm`, `-fno-prefilter`,
`--no-captures`. The default alone is blind to most of `src/gen/emit_vm.c`,
where 174 of the wave's 249 renamed sites live — under it most corpus patterns
route to the DFA and never reach the VM emitter at all.

**THE POPULATION INCLUDES THE REJECT TABLE.** Every `pattern` line from every
`.rxt` under `tests/` (known_fail included), PLUS every pattern
`tests/reject/run_reject_tests.sh` exercises, parsed out with `shlex` so shell
quoting is read rather than guessed at (an unparseable row is skipped and
COUNTED, never mangled into a different pattern). The reject half is not
padding: those patterns are the only population that exercises the stderr
comparison at all, so without them a refactor that moved a diagnostic would go
unseen. Floor 1400, asserted.

**THE SWEEP IS PYTHON, AND THAT IS A CORRECTNESS CHOICE.** Its two predecessors
compare with `a="$(gen_a ...)"`, and command substitution STRIPS TRAILING
NEWLINES — so a difference confined to trailing bytes is invisible to them. At
a pure refactor that blind spot is not acceptable, so this sweep captures
stdout, stderr and exit status as bytes and compares them exactly.

**THE POSITIVE CONTROL IS NOW IN THREE PARTS**, because "0 differences"
between a tree and itself is worth nothing. (a) The reference is ASSERTED
pre-refactor: it must contain neither `A_LOOK` nor `u.rep.`, so a mistyped pin
that resolved to something recent fails loudly instead of reporting a clean
bill of health. (b) The gate is DEMONSTRATED RED — the recipe is in the script
header (swap `a->u.rep.rmin` for `a->u.rep.rmax` at one `vm_rep` site in
`src/gen/emit_vm.c`, rebuild, run, revert). A gate nobody has seen red is a
gate nobody has checked. **(c), added at wave B+C and the one design §9.2 calls
the half that can actually fail: the BEARING bucket must be REFUSED IN FULL by
the reference** (`ctl_bad == 0 && ctl_ok == nb`). (a) and (b) are claims about
the PIN and about the SCRIPT; (c) is a claim about the two COMPILERS, and it is
re-answered on every run.

**THE BUCKET SPLIT ([M6.6.2] wave B+C; it was the `WAVE E HOOK`), and it is a
GRAMMAR-AWARE SCAN because it cannot be a grep.** `(?=` inside a character
class is three literal bytes, `\(?=` is an escaped paren, and `(?<name>` is a
NAMED GROUP belonging to a different module — SR-9 split that selector by TAIL
after a 256-byte sweep found exactly three lookaround tails (`=`, `!`, `*`) and
the named-group path for every other byte. A substring test gets all three
wrong in the direction that ADMITS a pattern to the identity population,
which is a silent pass. `lookaround_classify.py` tracks backslash escapes and
class depth and FAILS SAFE toward BEARING: a truncated `(?` or `(?<`, and any
`(*name:` whose name merely contains "look", go there though no rule names
them. **Control (c) is what makes failing safe safe**: over-classifying costs a
pattern from the identity population and is caught LOUDLY, because a
lookaround-free pattern filed as bearing is one the reference COMPILES.
Measured at the wave B+C landing: 85 bearing / 2048 free, floors 60 and 700,
control 85/85, and 0 differences on all four axes.

**AND THE CLASSIFIER'S OTHER DIRECTION WAS MEASURED TOO, WHICH THE CONTROL
CANNOT DO.** Control (c) catches OVER-classification (a free pattern filed as
bearing is one the reference compiles). UNDER-classification — a
lookaround-bearing pattern quietly admitted to the identity population — has no
such backstop, so it was measured directly: `STRICT_ALL=1` on the wave B+C tree
reports **332 differing comparisons over the four axes, 83 distinct patterns,
and ZERO of them in the FREE bucket**. Every pattern whose emitted bytes moved
is one the classifier calls bearing. Re-run that pair (`STRICT_ALL=1 KEEP=1`,
then classify the `DIFFERS` lines) after any change to the classifier or to the
population; it is the only evidence that the split is not hiding a difference.

**On demand, via `make test-lookaround-identity`** — not in `make test`, on the
ruling `test-atomic-identity` and `test-backrefs-identity` have and for the
same reason: the reference is a second full build of the compiler, and the
answer cannot change unless someone edits code at or before the pin.

## Conventions

Every check must be validated against a deliberate sabotage: disable the
optimization in a scratchpad build and confirm the check FAILS. A structural
test that passes under sabotage is worse than no test — it certifies nothing
while looking like coverage. Sabotage the SPECIFIC branch under test, not the
feature containing it. When adding an optimization to src/gen or src/opt, add
its check here in the same change.

Validated sabotages for run_trie_identity.sh. **Record the exact edit, not just
the count** — the first version of this table carried a number produced by a
contaminated tree (two sabotages stacked, because a `git checkout` revert
silently failed inside a non-git tarball copy) and another that was never
measured at all:

| sabotage (exact edit) | .rxt | @200 | @500 |
|---|---|---|---|
| `return n;` as the first statement of `disjoint_run_len` | 2 | 21 | 64 |
| in rule 1, hoist every accept to the front instead of partitioning the list around each (keep removing them from the list) | 16 | 38 | 94 |
| `TRIE_ENABLED = 0` in the shipped build | 0 | 0 | 0 — only the CONTROLS fire |
| `elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` | 0 | 0 | 0 — only the 4- and 8-branch controls fire |

Do NOT use the naive rule-1 sabotage (skip the accept split, change nothing
else): it leaves items with `len == depth` in the list for rule 2, which then
reads `seq + depth*32` past the allocated key — a 32-byte arena over-read, so
the count is unstable between builds (171 and 176 observed for the same edit).
The hoist form above is memory-safe by construction.

## The [K24] partial-inlining check, and the two things that make it non-vacuous

Added 2026-08-17 (k24fix lane) to `run_codegen_tests.sh`. It asserts that
`<prefix>_search` is NOT split into a `.part` clone by gcc's partial-inlining
pass — the property `__attribute__((noclone))` in `emit_search_head` buys, and
the one this file's founding charter describes exactly: behaviour-preserving,
invisible to the corpus, and worth a measured 1.33x on
tests/bench/compare case (c). See docs/dev/known_issues.md K24 and
docs/design/k24bisect_impl/k24_fix_note.md.

Two design points, both of which this directory has learned the hard way and
which a future editor must not "simplify" away:

1. **It compiles at `-O2` EXPLICITLY, not under `$GENCFLAGS`** (which defaults
   to `-O1`). Partial inlining is an `-O2` pass. Run at `-O1` the check would
   pass forever, attribute present or not — a green cell with no population,
   which is the exact failure the 256-branch-control lesson above is about.
2. **It carries its own CONTROL, and the control's source is INDEPENDENT of
   what it controls.** The positive asks `nm` — gcc's own output — whether a
   clone exists. The control strips the attribute back out of the SAME
   generated file and asserts gcc DOES clone it. Without that, a future gcc
   that stopped splitting would make the positive vacuously green and the
   guard would quietly stop guarding, with nobody the wiser until a bench
   floor went red again. If the control stops firing the check FAILS and says
   the population is gone, rather than reporting success.

Validated sabotage: delete the `sb_printf(c, "__attribute__((noclone))\n");`
line from `emit_search_head` in src/gen/emit_dfa.c, rebuild, re-run — the check
FAILS with "emitted artifact carries no `__attribute__((noclone))` at all"
(measured 2026-08-17; codegen checks went 39/39 pass to 1 failure). Note the
sabotage-then-restore rebuilds `build/pcrec`, so do it when nothing else is
running against that binary — doing it during a `make test` contaminates that
run and it has to be discarded and redone.

## [OPT-ALTCLS] broke the trie's positive controls, and the fix generalizes

2026-08-17: landing `src/opt/altcls.c`'s stage 2 (prefix factoring) turned
`run_trie_identity.sh`'s three positive controls (4/8/256 branches) from
factored/unfactored to factored/FACTORED — the reference build, compiled
with `-DPCREC_NO_TRIE`, was passing anyway. Root cause: `src/opt/altcls.c`
is a NEW pass that runs BEFORE `nfa.c`'s trie entirely, is NOT gated by
`-DPCREC_NO_TRIE` (that macro reaches only `nfa.c`'s own trie code), and
targets the SAME shape the controls were built from — a run of branches
sharing a literal first byte, exactly `ctl_small`'s bare-letter prefix and
the 256-branch control's bare binary digits. With a bare-letter prefix,
`altcls` pre-factors the shared run on BOTH sides before `-DPCREC_NO_TRIE`
ever gets a chance to matter, so the reference build stops being "trie
disabled" and becomes "trie disabled AND nothing left for it to disable" —
the exact vacuous-control failure mode this file's own header already
warns about, from a cause its author had no way to anticipate.

**The fix is narrower than the failure looks: widen every prefix BYTE from
a bare literal to a two-member CLASS** (`a` → `[aA]`, binary digit `0` →
`[02]`). `nfa.c`'s `trie_key` accepts ANY class-only leaf sequence (no
single-bit restriction — see its own comment, "whose every leaf is
A_CLASS"), while `src/opt/altcls.c`'s eligibility test requires a branch's
FIRST atom to hold EXACTLY one byte (`altcls_single_bit`). A two-member
class is therefore trie-eligible and altcls-ineligible in one move: altcls
declines at the very first `altcls_branch_peel` call for every branch in
the pattern (verified: `RX_ALTCLS_MERGES`/`RX_ALTCLS_FACTORED` both stamp
0 on the widened controls), restoring the control's original property —
shipped=factored, reference=unfactored, driven by `-DPCREC_NO_TRIE` alone.
No subjects are ever run against these patterns (this file's own header:
"no subjects, no gcc"), so widening what each position matches costs
nothing the check verifies. Re-measured clean: all three controls green,
the 500-pattern equivalence sweep still 500/500 identical both axes
(case-sensitive and `-i`), zero regressions.

**The generalizable lesson, for whoever adds the next AST-level pass that
runs before `nfa.c`:** ANY pass that runs upstream of the trie and is not
itself gated by `-DPCREC_NO_TRIE` can pre-empt a positive control built
from bare literals the same way. This project's `-DPCREC_NO_TRIE` /
`-fno-X` deny-flag family (D46/D47.3) is scoped PER PASS by design — no
single flag disables "everything upstream of the trie" — so a future
pass with equivalent reach needs the same widened-class treatment applied
here, not a new reference-build flag.

## [M5-SEAM] two additions: the residual/hot-path barrier, and K27's probe

**`[M5-SEAM/DD-12(7)]` — no engine body calls an encoding residual entry.**
D58 built the DD-12 residual seam: an artifact embeds exactly one
encoding's residual block, and `<prefix>_next_pos` is its first entry.
DD-12 (7) rules that the per-encoding header is the RIGHT seam for the
runtime-identity residue and the WRONG seam for the hot path, "ENFORCED BY
CHECK, NOT CONVENTION" — and this file is where such a check belongs for
the reason its own header states: **no correctness test can see it.** Under
the byte backend `<prefix>_next_pos` IS `pos + 1`, so an engine that
advanced through it would match identically, the whole corpus and both
oracles would stay green, and the artifact would have acquired exactly the
cross-seam call that makes the hot path's shape and speed depend on the
encoding the moment a second backend lands.

**[M6.5.2] THE CHECK CHANGED SHAPE, because the seam gained its SECOND and
THIRD entries and they are not like the first.** `<prefix>_next_pos` has no
business anywhere inside the matcher — unanchoredness is the automaton's own
self-loop, so there is no external advance to route through. A BACKREFERENCE
COMPARE has no automaton representation whatsoever, so forbidding the call
forbids the construct. "Never called from an engine body" is therefore no
longer the rule; it is the DECLARED-COUNT-ZERO case of one:

> the number of CALL SITES of `<prefix>_<entry>` inside file-scope function
> bodies other than the entry's own definition and `main()` must EXACTLY equal
> the count the FIXTURE TABLE declares.

Three design points, and the first two are R32 E7/C2's whole finding about the
first draft of this change:

- **THE EXPECTATION COMES FROM THE TEST, NOT FROM THE ARTIFACT.** A check whose
  population is read out of the artifact's own residual declarations goes GREEN
  exactly when the thing it guards is broken: an emitter that inlines the
  compare AND drops the entry from the mask leaves nothing to assert, and the
  global empty-population guard does not notice because `next_pos` is
  unconditional and keeps it satisfied. So each fixture row DECLARES which
  entries its artifact must carry, and the artifact's declared set is asserted
  to EQUAL it.
- **THE COUNT IS A DECLARED INTEGER, NOT A COUNT OF ANYTHING.** Deriving it by
  scanning the fixture's PATTERN for `\<digit>` would be a SECOND
  IMPLEMENTATION of PCRE2's octal disambiguation, and it would get the same
  cells wrong that rule exists to get right — `(a)\10` is octal and contains
  ZERO backreferences, `(a)\18` is `\01` then a literal `'8'`. Worse, a
  scanner and the emitter would drift in the SAME direction, i.e. green on an
  incorrect compiler. A human wrote the integer beside the pattern, and every
  octal-ambiguous spelling is kept out of the fixture set.
- **THE SCOPED GUARD IS EXACT, NOT A FLOOR.** The global guard cannot serve:
  `next_pos` is unconditional, so it stays satisfied even if every
  backref-bearing fixture were deleted. Four fixtures declare a bref entry, and
  a floor of "at least 3" would pass while one silently lost its declaration —
  which is the population-shrinking failure the guard exists to catch, arriving
  through the guard itself.

**COMMENT STRIPPING IS TOKEN-LEVEL AND RUNS FIRST**, and it changes
`next_pos`'s own check in EXACTLY ONE DIRECTION — the direction that hides
things, which is why it is named rather than absorbed. Before it, a COMMENT
naming `<prefix>_next_pos` inside an engine body was reported as a violation,
which is STRICTER than this check's own stated allowlist ("a residual name may
appear (a) in a comment"). **Demonstrated before the rewrite** on a synthetic
body whose only mention was a comment: flagged. Token stripping brings the
implementation INTO LINE with its documented contract rather than loosening it
past one. S68 still fires either way — its sabotage plants a real CALL, and
stripping comments cannot hide a call.

The stripper carries in-comment state ACROSS records (a `/* */` region spans
lines), skips string and character literals so a `/*` inside one cannot open a
comment and a residual NAME inside one is not counted as a call, and runs
BEFORE head-detection and the column-0 brace rules — because a comment can
otherwise contain something that looks like a definition head or a `}` at
column 0 and desynchronise the `inbody` tracking. Matching is at TOKEN
boundaries, not substring: `rx_bref_match` is a proper prefix of
`rx_bref_match_caseless`, and a substring rule would count every caseless call
as a case-sensitive one and pass with the emitter wired backwards.

**Every failing direction was demonstrated before the check was trusted**: a
declared count moved 1 -> 2 goes red; deleting a bref fixture row reddens the
scoped guard; a body whose only mentions are comments and a string literal
counts 0; a body with one real call plus its intent comment counts 1 for each
of the two entry names.

- **The population is DERIVED, not typed.** The residual entry NAMES are
  read out of the artifact (each residual declaration is preceded by the
  backend's own `ENCODING RESIDUAL entry` comment) — used now to CHECK the
  fixture's declaration rather than to BE it. Finding NO residual entry at
  all is still a FAILURE.
- **The check reads FUNCTION BODIES, not the whole file.** A residual name
  legitimately appears in comments, in its own declaration, and inside its
  own definition. Ten emission shapes now (DFA memchr-prefilter, DFA bitmap-
  prefilter, anchored, VM, `--engine=vm`, `--emit-main`, and four
  backreference fixtures) in both artifact forms.

Sabotage: `tests/mech/sabotages/S68_residual_in_hot_loop.sh` routes the
emitted bitmap prefilter's skip loop through `<prefix>_next_pos` — the edit
a developer holding a fresh "advance one character" helper would actually
make. DETECTED at `codegen 3fail/41pass` with `corpus 0fail/56pass`; the
corpus staying green is the finding, not a footnote to it.

**`[K27]` — the contract's legal `(s == NULL, n == 0)` subject, RUN.**
docs/spec/match_api.md §3.1 admits a NULL subject when `n == 0`, and the
emitted `memchr` prefilter used to receive it: technical UB in EMITTED code
(docs/dev/known_issues.md K27, closed by this lane). This check compiles a
memchr-prefilter artifact, links a driver calling
`<prefix>_search(NULL, 0, 0, NULL)` and `<prefix>_next_pos(NULL, 0, 0)`,
and RUNS it, requiring `0 1`.

Placement is the whole point and is worth understanding before moving it:
this script is already on the `make ubsan` and `make asan` suite lists, so
the run is instrumented there (with `-fno-sanitize-recover`, a first-hit
abort) and pins the answers on the plain axis. K27 was invisible to the
battery for a structural reason — the sanitizers' generated-code axis runs
the CORPUS, and no corpus case passes `s == NULL`, so the instrumented axis
had nothing to see. A check that only compiled the artifact would reproduce
that hole exactly. It also fails loudly if its fixture stops carrying a
memchr prefilter, rather than passing vacuously.

**Two measured facts about the `[M5-SEAM/DD-12(7)]` extractor**, both worth
keeping because a body extractor that silently matched nothing would make
this check vacuous exactly like the OS-0b scoping hazard this file already
documents:

- It reaches the VM's own body, not only the DFA's. Verified by planting
  `(void)<prefix>_next_pos(ctx->subject, ctx->len, ctx->pos);` immediately
  inside `<prefix>_match_impl` in an emitted VM artifact: reported.
- `main` is ALLOWLISTED. The `--emit-main` `main()` is a CALLER, not an
  engine — a demo `main()` doing find-all through `<prefix>_next_pos` is
  the documented caller protocol (docs/spec/match_api.md §3.1), not a
  derailment. It does not call it today; the entry exists so a later
  `--emit-main` that does is not misreported.

**The `[M4.4/D44/A-2]` sibling** added in the same lane asserts the ABI
block's PROPERTY (byte-identical across four prefixes of different lengths
and shapes) rather than only its consequence (the cross-prefix one-TU
compile above, which a block merely free of prefix-dependent content would
also satisfy). Its control is the whole file, which must DIFFER across
prefixes — otherwise the extractor is comparing two empty strings, or
`--prefix` is not reaching the emitted text at all. Since [M5-SEAM] the
block also carries a pointer to the residual entries, and that paragraph
has to stay independent of the ENCODING axis as well as the prefix one: the
block is emitted once per file under a prefix-independent guard, so two
artifacts compiled for different encodings into one TU share it and only
the first copy survives.

## **[M6.2 wave E] the `[M6.2-KRESET]` block, and the identity gate that is NOT here**

`\K` is module `assertions`' last construct and the first whose whole
structural surface is provenance rather than presence. Four checks:

- **rule 1** — a `\K` artifact's `<prefix>_caps_out` derives `caps[0][0]` from
  the TRAILED slot 0, and the unconditional `caps[0][0] = (ptrdiff_t)start` is
  GONE from it. That `start` is the prefilter's span start under the hybrid,
  i.e. the REVERSE PASS's answer and the PRE-`\K` start, which
  assertions_design.md §6.3 rule 1 says may bound the search and must never be
  written out. Both directions are asserted in one artifact, plus that the
  write goes through `RX_SET` rather than straight to `slot_values[0]` — the macro is
  what records the old value on the trail, and without it a `\K` crossed on a
  LOSING path stays crossed.
- **rule 1b** — a `\K`-FREE VM artifact emits the PRE-WAVE `caps_out` body
  **character for character**, with the two lines pinned here as LITERALS. The
  literal is deliberate rather than lazy: "does not contain the `\K` form"
  would pass on an emitter that had rewritten the line into some third shape.
  This is also **the whole of wave E's byte-identity claim**, and why this
  directory gained no fifth `run_*_identity.sh`: the emitter reads `v.nkreset`
  into a DEFAULT ARTIFACT at exactly ONE site (`--emit-ir`'s listing and
  `--trace`'s ACCEPT line read it too; neither writes a default artifact), so
  the claim is about one predicate rather than about a construction spanning
  several. Its corpus-wide half was MEASURED ONCE
  against the genuine PRE-WAVE COMPILER (1,208/1,208 identical at the default
  engine, 1,209/1,209 under `--engine=vm`, 0 refusal mismatches) — a reference
  sharing NO SOURCES with the subject, which is strictly stronger than a `-D`
  knob build and is the direct answer to wave D's own finding that a knob
  build's sabotage CANCELS.
- **rule 3** — the VM's match-here entry calls `<prefix>_match_impl` at
  `ctx->pos` directly: no `caps[0][0] != ctx->pos` filter (which under `\K`
  compares against the POST-`\K` start and rejects a genuine anchored match)
  and no `caps[0][1] - caps[0][0]` return (which is the POST-`\K` length, and
  a D38 callout advancing by it on `ab\K` would advance by 0 forever).
- **rule 3b** — the DFA artifact's `rx_match` still carries its start filter
  and its caps-derived return VERBATIM. It has to be checked on a `\K`-FREE
  pattern, because a `\K` pattern is VM-forced and has no DFA entry at all —
  which is also why those two lines are correct there and wave E touched
  neither.

Sabotages **S85** (R30 C3's own request: take `caps[0][0]` from the
prefilter's span) and **S86** (the write untrailed). Their symptoms in rule 1
are DISJOINT, which is why they are two rows rather than one edit with two
halves; measured, S85 fails 198 corpus cases and S86 exactly 6 — the two undo
families and nothing else.

## [DD-14] wave B+C — the SUBROUTINE CALL's three structural rules

Module `recursion`'s corpus is 306 oracle-verified cases and its behavioural
instrument is `tests/recursion/run_recursion_diff.sh`. **Three of the module's
claims are invisible to both**, and each is here for its own reason.

**RULE 1 — `goto *` count == 1 + the number of emitted SHARED CALLEE BODIES**
(design §5.8). `src/gen/emit_vm.c`'s opening comment states, as a design
decision, that there is "exactly ONE indirect jump in the whole function". A
call's return is a SECOND, and §5.8 amends the invariant to a RELATION rather
than a constant — a CONSTANT is wrong in both directions, which R34's LENS2-5
measured: a call-free artifact is 1, one callee is 2, THREE DISTINCT callees
are 4 however many call SITES there are (the sites share the body), and a
wave-G fully-spliced artifact is back to 1. The five fixtures cover exactly
that spread, and the shipped emitter answers 1 / 2 / 2 / 4 / 2.

**AND THE RULE IS ONLY STATEABLE BECAUSE THE `goto *` IS WRITTEN INLINE.** The
design sketches the return as an `RX_RETURN` MACRO, which puts one `goto *` in
the definition and NONE at the uses — making the artifact's count `1 +
(has_calls ? 1 : 0)` and the relation unexpressible. Emitting per region is a
deliberate deviation recorded at `vm_region`, and sabotage S168 is the row: it
routes the return through a macro, changes NO ANSWER, and fires on exactly
ONE of this rule's four call-bearing fixtures — the three-distinct-callee one.
A rule written as a constant would have passed that sabotage three times out
of four.

**RULE 2 — a call-FREE artifact carries none of this module's machinery**
(design §9.1). The resume frame gains two fields, `RX_PUSH` a line, the fail
label a line, both resets a line each, and `RX_CALL` appears — all gated on
ONE flag, so the byte-identity claim is STRUCTURAL rather than something a
sweep discovers. Checked in BOTH directions in one run: the four names must be
ABSENT from a call-free VM artifact and PRESENT in a call-bearing one, so a
check that had stopped looking at anything cannot pass. (The corpus-wide
measurement was taken separately against a `git archive` of the pre-module
compiler: 2,198 of 2,198 identical, with the positive control at
`ctl_bad = 0`.)

**RULE 3 — the callee region and the lexical occurrence come from the SAME
NODE** (wave A2's pass-ordering finding, commit 513de65; sabotage S166).
`u.call.body` is a CACHE of "which subtree is that group's, in the tree the
emitter will walk", and `src/opt/altcls.c` REBUILDS nodes rather than mutating
them. **MEASURED** by moving `pcrec_callgraph_build` above that pass and
diffing artifacts: `((?:a|b))(?1)` then emits a merged class test lexically and
the un-merged two-branch alternation WITH ITS OWN `RX_PUSH` in the region —
two different programs for one group — and `RX_RESUME_FRAMES` moves 2 → 3.
**The ANSWERS do not change**, because altcls is answer-preserving in both
directions, which is exactly why this is a structural rule and not a corpus
cell. The fixture asserts both halves — that the merge HAPPENED
(`RX_ALTCLS_MERGES >= 1`, so the shape can still express the hazard) and that
NEITHER program needs a resume push.

**AND THE DISCHARGE WITNESS IS MEASURED NOT TO BE A HAZARD**, which is why
rule 3 has one fixture rather than two: `((?>a)b)(?1)` compiles
BYTE-IDENTICALLY under the same sabotage, because `pcrec_discharge_atomic`
splices by rewriting the PARENT's `->l` IN PLACE and the `A_CAP` a callee is
rooted at keeps its identity. Wave A2 named both passes; only the one that
REBUILDS the node matters.

## [DD-14] waves D+E — `run_recursion_identity.sh`, opt-in as `make test-recursion-identity`

Module `recursion`'s byte-identity gate, in `run_atomic_identity.sh`'s exact
shape (a pinned pre-producer commit via `git archive`, since this module has
no stage a `-D` knob could sit on — the whole surface is "is there an
`A_CALL` in the tree", false for every pre-module pattern). **WAVE D LANDED
THE DEFAULT-AXIS SEED AND WAVE E GREW IT TO ITS FOUR AXES** — `default`,
`--engine=vm`, `-fno-prefilter`, `--no-captures` (design
`subroutines_design.md` §9.1) — which is what the seed's own header said
would happen, and nothing about the reference, the pin or the classification
rule changed in kind. §9.2's SPLICE-vs-LINKAGE SECOND control is still
absent and is wave G's: it needs the `-fno-splice-calls` axis §6.3's linkage
rule introduces. Pinned at `ac4917d` (wave A2's merge —
the last commit with `A_CALL` the KIND but no producer for either doorway,
verified by the reference tree's `src/parse/mod_recursion.c` not existing
rather than by grepping for port names, since wave A2's own `internal.h`
already MENTIONS `pcrec_rcport_num` in a forward-looking comment and a
substring search over the whole tree is a false positive on prose). **No
retirement guard, unlike its three siblings**: their pins predate [DD-14]
wave A's ABI event (`PCREC_ERR_RECURSE`/`ERR_FLOOR`/`PCREC_ERR_INTERNAL`,
main `0c75c96`) and cannot be moved past it; `ac4917d` already contains that
event (`0c75c96` is its own ancestor), so it is baked into both sides of
every comparison here and cannot be what retires this gate. The classifier
covers both doorways — `\g<`/`\g'` outside a class, and a `(?` construct
whose tail is not one of the twelve named non-call shapes (`:` `=` `!` `*`
lookbehind `<name>` `'name'` `P<` `P=` `>` atomic-group `#` `(` conditional,
inline-option run) — and FAILS SAFE toward the call bucket on anything else,
`lookaround_classify.py`'s rule. Landing figures: read them from a run
(`bash tests/codegen/run_recursion_identity.sh`); the corpus splits roughly
90% call-free to 10% call-bearing, comfortably above the 700/60 floors, and
the positive control's own first draft caught its own bug — an early
classifier version had no `(?>` exclusion and misclassified every atomic
group as a call, which the reference-refuses-all-calls control refused to
pass vacuously (153 of 287 "call-bearing" patterns were accepted by a
pre-recursion compiler, because most of them were plain atomic groups).

**WHAT WAVE E ADDED, and each piece is there because a green run alone does
not say it.**

- **THE OTHER THREE AXES.** `-fno-prefilter` is not ceremonial here: §8.2
  forces the prefilter OFF for a call-bearing pattern, which is a touch on
  `select_engine.c` — a file EVERY pattern goes through — and the axis that
  pins the prefilter constant is the one that localises a predicate that
  over-fires. `--no-captures` is the backrefs-precedent axis: §4.3 edits
  `pcrec_bref_mark`'s union, which is `--no-captures`' own machinery, and a
  mark-set edit that over-marks makes the flag keep slots it used to delete.
- **A PER-AXIS POSITIVE CONTROL.** §9.2's control (the reference REFUSES
  every call-bearing pattern) now runs on each axis rather than once,
  because "refuses" is an answer the axis flags can in principle change —
  both `--no-captures` and `-fno-prefilter` reach `select_engine.c`, where a
  refusal lives.
- **THE D37 STRIP, ASSERTED, PLUS A RAW COMPARISON BESIDE IT.** The ruled
  claim (§9.1) is byte-identity past D37's three feature-stamp lines, with
  the filter asserted to remove exactly three per side. This gate makes BOTH
  comparisons and counts `stamp-moved` — pairs that differ RAW and agree
  STRIPPED. It is 0 on all four axes and is *expected* to be, unlike
  `backrefs`: module `recursion`'s registry rows PREDATE the module (P4
  measured all 26 VM_ONLY before any producer existed), so `render_modules`'
  first-row walk never moved the name. A nonzero value is a FAILURE, not a
  note; wave F adds rows and must say so.
- **A 23-ROW CLASSIFIER SELF-TEST, run before anything is classified.**
  §0.3 item 9 is the census's own MEASURED instrument defect — a naive
  `\g<` scan counts `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` as a
  call — and "the classifier masks classes" is a claim about code, not a
  comment. The rows pin `^[\g<1>]$` and `^[(?&x)]$` call-free (BOTH
  doorways' version of the defect), `a[b]\g<1>` call-bearing (masking must
  not swallow the rest of the pattern), `(?>` as an atomic group (the row
  the first draft got wrong), and `(?~x)` failing safe into the call bucket.
  **Four of the rows are WAVE F's arm**: D71 item 4 made `(?(DEFINE)` this
  module's, so the conditional exclusion grew a `(?!DEFINE)` negative
  lookahead, and the rows pin `(?(DEFINE)abc)^x$` CALL-BEARING (a
  DEFINE-bearing pattern with no call in it is still one this module changed,
  which is F's own honesty argument), the DEFINE-plus-call form the same,
  `(?(DEFINE)(?<g>a))b` the same — the SHARP one, because it scans TWO `(?`
  occurrences, a DEFINE tail that goes to the call bucket and a `(?<g>` that
  the named-group arm recognises, so it is what pins the ANY-occurrence rule
  against a classifier that reads the last verdict or lets a recognised inner
  construct rescue the pattern — and `^[(?(DEFINE)a)]$` call-FREE, because the
  class mask has to reach the newest doorway or it reintroduces the census's
  oldest defect.

**EXERCISED IN THE FAILING DIRECTION at wave E**, which is the half a green
run cannot supply: one byte of an emitted comment (`emit_dfa.c`'s
`"/* Generated by pcrec. Pattern: "` → `", Pattern: "`), on a path every
call-FREE artifact takes. MEASURED: `checks passed: 4  checks failed: 8`,
rc 1, with every axis at `same=0`:

| axis | same | differing | refused by both |
|---|---|---|---|
| `default` | 0 | 2199 | 240 |
| `--engine=vm` | 0 | 2200 | 239 |
| `-fno-prefilter` | 0 | 2200 | 239 |
| `--no-captures` | 0 | 2199 | 240 |

The four PASSes are the four positive controls, and they staying green is the
RIGHT shape rather than a hole: the control is a claim about the REFERENCE
(does it refuse every call-bearing pattern) and the planted byte was in the
SUBJECT, so a control that had gone red would mean the two halves of the gate
were reading each other. Each axis also fired its floor check, which is the
second, independent reason the run is red. Reverted; `make` and the green
run above are on the reverted tree.

## [DD-14.FB] the caller-provided frame buffer's structural block (2026-08-25)

Six checks in `run_codegen_tests.sh`, all of them things a `.rxt` cell is
structurally incapable of seeing.

**The first one is the compatibility promise itself.** Spec §10.8 says the
three existing entries keep their exact signatures and adds, in its own words,
that "the implementation lane owes a check that asserts each line". The corpus
cannot defend that: it recompiles its driver against whatever the header says,
every run, so a wrapper that quietly changed `<prefix>_search`'s declaration
would pass every cell and break every vendored consumer. So all six
declarations are pinned CHARACTER FOR CHARACTER with `grep -qxF`, on a VM
artifact and a DFA one.

**And one check on the `--trace` axis**, because that axis moves the struct the
macros measure: a traced artifact must stamp `RX_RESUME_FRAME_SIZE` **48**
(call-bearing) and **32** (call-free), not the untraced 40 and 24, and both
traced artifacts must COMPILE — which is where their `_Static_assert`s live. A
stamp stuck at 40 would hand a caller a capacity 20% larger than its
reservation holds. Drift through the member list is unrepresentable (the list
that emits the struct is the list that computes the size, so a trace-blind list
emits a struct with no `id` member and fails on that); this covers the
remaining route, a second computation blind to an axis the struct sees, and it
was validated in the failing direction against a scratch emitter doing exactly
that.

The other six: the five sizing macros emitted exactly once on both engines
(real on the VM artifact, INERT on the DFA one — and the alignment specifically
NOT 0, since a caller rounding an arena cursor up to it would divide by zero);
the three `_Static_assert`s that reconcile the stamped sizes with the real
`sizeof`/`_Alignof`, which are sabotage row S184's build-time detector; that NO
capacity guard compares against a stamped constant and at least four read the
capacity fields (too FEW is also a failure — that would mean a guard was
deleted rather than converted, and this check must not read a deletion as
success); the delegation direction on the emitted TEXT; and `rx_info`'s four
fields at `abi` 3.

**Why the delegation direction is checked on the text.** Reversing it
(`<prefix>_search` implemented as `<prefix>_search_in(..., NULL)`) changes NO
ANSWER — what it costs is the `_in` entry's small stack frame, because it would
then own the default arrays and C cannot declare a local conditionally. Every
behavioural cell passes under either direction, so text is the only instrument
that sees it.

**One existing check moved with this wave.** `[M6.2-KRESET rule 3]` asserted
that `<prefix>_match` calls `<prefix>_match_anchored` directly; the entry is
now a wrapper and the call moved one level deeper. The rule's PROPERTY —
"reaches the anchored implementation, never through `<prefix>_search`" — is
unchanged, so the check now spans `rx_match` AND `rx_match_run` and GAINED two
assertions rather than losing one: neither may mention `rx_search`, and
`rx_match_in` must reach the same `rx_match_run`. An entry that filtered on
only one of its two spellings would be wrong for exactly the callers who used
that one.

## [DD-14.FB] the recursion identity gate is now TWO comparisons (2026-08-25)

`run_recursion_identity.sh` used to ask one question — "is a call-free
pattern's whole artifact byte-identical to the pre-module pin `ac4917d`,
past D37's three stamp lines?" — and [DD-14.FB] made that question
unanswerable: the caller-buffer surface is UNCONDITIONAL, so every artifact
gains ~180 lines and changes ~30, across an announced `abi` 2 → 3 boundary
that D40 regime 1 governs. The gate now asks two questions instead, and prints
two numbers so they never blur:

- **(A) the PROGRAM REGION against the UNCHANGED `ac4917d`** — `goto
  <prefix>_L0;` … `<prefix>_accept:`, with no filtering beyond the three
  stamps, so a COMMENT change inside the region is still a difference. This is
  the claim the gate was built for, still measured against the reference it
  was built against.
- **(B) the WHOLE FILE against a pin moved forward to `8fc1e51`** — the last
  commit of the FB wave touching `src`/`lib`/`cli`. Everything after that pin
  is byte-exact whole-file again, comment changes included.

**WHY NOT A WIDER `stamp_strip`, MEASURED so nobody re-derives it.** Extending
the filter with named exact lines for the FB surface needs **200 distinct
lines** (30 old-side, 180 new-side, 69 of them comments). It fails twice: it
**over-strips** — the filter necessarily contains `ptrdiff_t rx_match(const
rx_ctx *ctx)` and its `_caps` sibling, whose signature lines moved when the
bodies became statics, so the gate would stop seeing a change to the two
declarations spec §10.8 promises are unchanged — and it **still under-covers**,
leaving 5 (DFA) to 12 (VM) blank-line differences no whole-line pattern removes
safely. Filtering to green is the failure this project has recorded twice.

**THE TWO FB LINES INSIDE THE REGION ARE A MEASURED ZERO, NOT A FIRING
EXCEPTION.** The region-exit guard's type and capacity operand are the only FB
lines that can move inside a program region, and `vm_region` is emitted only
for a call-BEARING artifact — this sweep's population is the call-FREE bucket.
So the assertion is that NO artifact in the population carries `RX_VM_CALL_`,
which is a leak detector for the classifier rather than a licence.

**THE ELISION LIST SPLIT IN TWO, and both halves are checked.** Wave G's four
dead-capture patterns differ from the PRE-MODULE reference (VM-selected then,
DFA-selected now, so the region exists on one side only) and must NOT differ
from the post-wave-G FILE PIN, where the elision is on both sides. One list,
two expectations, each asserted against the comparison it belongs to.

## [TT-11]/D76 (2026-08-25): the two pins have two OWNERS, and the FILE pin's guard is now STRUCTURAL

(A)'s pin is the MODULE's promise (pre-module, never moves; its exception list
is D75's four dead-capture patterns, above). (B)'s pin is owned by the emitted
`abi` NUMBER (`rx_info.abi`, stamped by `src/gen/emit_dfa.c`): it IS, by
definition, the commit that introduced the CURRENT `abi`; within an abi number
the emitted output is byte-exact whole-file, comments included; ANY change to
the emitted scaffolding — comments, declarations, layout — is an `abi` bump
AND a re-pin of (B) to that change's last `src`-touching commit, in the SAME
change (free pre-v1 under D40; the binding event it should be once pcrec ships
v1).

The gate used to guard the FILE pin with an ad-hoc
`grep -q RESUME_FRAME_SIZE "$FILEREFSRC/src/gen/emit_dfa.c"` — a probe that
encoded [DD-14.FB]'s own boundary by name and would say nothing about the
NEXT scaffolding change. It now builds an artifact from EACH compiler
(subject and file-pin) on a call-free pattern (`'a'`), reads each side's
`.abi = N` stamp with `grep -o '\.abi = [0-9]*'`, and refuses when they
differ, naming the fix directly: "the emitted scaffolding changed: bump `abi`
in src/gen/emit_dfa.c and re-pin comparison (B) to this change's last src
commit, in the same change (D76)". Validated: pointing
`RECURSION_IDENTITY_FILEPIN` at a pre-FB commit (`ac4917d`, `.abi = 2`
against the subject's `.abi = 3`) makes the refusal fire with that exact
message; the default pin (`8fc1e51`, same `.abi = 3` as the subject) passes
straight through to the sweep. Comparison (A) is untouched by this — it never
read the probe at all.

**[OPT-1], 2026-08-25 — THE SECOND SUCH EXERCISE, and the pin is `469a432`
now.** The TWO-TIER DEFAULT ENTRY: `abi` 4 -> 5, comparison (A) byte-identical
against the unchanged `ac4917d`, (B) re-pinned in the same change. What is new
about it is that **no DFA artifact's bytes move at all** — a first for an `abi`
bump — because the tier is emitted entirely by `src/gen/emit_vm.c` and a DFA
artifact has no resume stack to tier. The `abi` number versions the artifact
FORMAT rather than the VM, so it moves on both kinds regardless, and (B) is
therefore re-pinned for DFA artifacts too.

**[DD-13], 2026-08-25 — THE RULE'S FIRST EXERCISE BY A NON-LAYOUT CHANGE, and
the pin was `5991d4c`.** [DD-13] gave every DFA artifact three D46
selection stamps. It moves NO struct offset and NO emitted program byte —
comparison (A) is byte-identical against the unchanged `ac4917d` pin on all
five axes, which is the PROOF that the change is scaffolding only — and it
still bumps `abi` 3 -> 4 and re-pins (B), because (B) compares WHOLE FILES and
three new `#define` lines are a whole-file difference on ~2,000 artifacts.
That is D76 working as ruled rather than an exception to it, and it is the
reading a future change should copy: (A) says whether BEHAVIOUR moved, (B)
says whether BYTES moved, and only the second is what `abi` versions.
Demonstrated both directions on this change: with the new pin the gate is
15/0; with `RECURSION_IDENTITY_FILEPIN=8fc1e51` (the old pin, `.abi = 3`
against the subject's `4`) it REFUSES with the message above before the sweep
runs.

**[DD-13c], 2026-08-25 — THE SECOND EXERCISE, and the pin is
`c940551` now.** r37's two scope findings move emitted `#define`
bytes (the four proven-empty DFA artifacts' scan value; two new lines on every
VM hybrid) and move nothing inside the program region, so the reading above is
copied verbatim: `abi` 5 -> 6 (lane srTier's two-tier entry took 4 -> 5 immediately before), (B) re-pinned, (A) byte-identical
against the unchanged `ac4917d`. Demonstrated both directions again — see the
[DD-13c] entry in `docs/dev/dev_journal.md` for the measured numbers.

- **run_size_term.sh** — [ART-SIZE]/D84's structural check (2026-08-29). Reads
  the ARTIFACT, never the stamp alone: the four size-term stamps unconditional
  on every VM artifact (D81), four of the six `_UNROLL_K_WHY` values driven
  through the path each one names, the stamped `K` checked against
  `--unroll=1/2/4/8` and against the term's own choice, and the two effective
  caps against the flags (including that a below-default `--max-emit-*` value
  is REFUSED — raise-only is what stops those being used to manufacture a
  refusal on someone else's build).
  **It builds a second compiler, and that is [ENG-ABS]'s precedent rather than
  a new surface.** `cap-rescue` has a natural population of ZERO and the CLI
  overrides are raise-only, so the branch cannot be reached from outside at
  all; the check builds a REFERENCE COMPILER with the limits lowered at
  pcrec's own compile time (`-DPCREC_SIZE_TERM_THRESHOLD=20000
  -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000`) and drives it there. BOTH constants
  move, not one: the threshold gates on CODE bytes, so lowering only the cap
  gives a compiler in which the ladder never runs on the witness and the
  pattern simply refuses. An anti-vacuity cell asserts the rescue chose a
  DIFFERENT K from the default build, and the NATURAL cap-rescue population is
  pinned at 0 as a CEILING that fires if a real pattern ever lands in the band
  `docs/design/artifact_size_term.md` §4.2b calls empty.

- **run_prefilter_collapse.sh** — [OPT-4]/K39's structural check (2026-08-29).
  The count-collapsed hybrid prefilter, held to the ARTIFACT rather than to its
  stamp. THE AXIS IS ANSWER-IDENTITY-PRESERVING (D46), which is exactly why it
  needs this: the whole `.rxt` corpus, both oracles, `make test-axes` and every
  differential agree whether or not the emitter got any of it right. Six
  failure modes none of them can reach — the collapse silently stopping (§1
  asserts count-independence on the DEFAULT artifact, with a failing-direction
  control proving the equality is the collapse and not an artefact); the stamp
  drifting from the machine (§2 compares `RX_VM_PREFILTER_LANG` against BYTES —
  `"exact"` iff byte-identical to the `-fno-prefilter-collapse` build — over
  seven witnesses chosen to land on named sides of the knee); the MRL ceiling
  surviving a superset prefilter, which is a silent MATCH LOSS rather than a
  size regression (§3, on every collapsed corpus artifact); the collapse
  reaching the DFA ENGINE, where a superset IS a miscompile (§4's iff, both
  directions, over 2,772 patterns); the population moving in EITHER direction
  (§5); and the `_WHY` reason drifting from the outcome it explains (§2, §5,
  and §1's ratio cell).
  **THE CONTROLS DO NOT SHARE A SOURCE WITH WHAT THEY CONTROL** (learnings §3),
  and §5 is where that costs real work. The claim it defends is that the knee
  fires only where a COUNT made the machine big, so the obvious term — "does
  the compiler think this pattern has a collapsible repeat" — is
  `pcrec_has_collapsible_rep`, a CONJUNCT OF THE GATE UNDER TEST: a bug in it
  would make the assertion agree with the defect. The replication factor is
  therefore re-derived from the PATTERN TEXT by an awk scanner in this file,
  which is itself pinned on 9 hand-checked patterns (an escaped brace, a brace
  inside a class) before it is trusted, and carries a non-vacuity control
  because a scanner answering ">= 2" for everything would make the assertion a
  tautology.
  **§5 IS RETIRED AND DELETED (Frank's ruling B, 2026-08-29).** It was a form
  census over the knee's population — how many corpus artifacts sat above
  `PCREC_PREFILTER_EXACT_NFA_STATES`, banded on both sides, with zero of them
  of replication factor < 2. Ruling B deleted the knee, so that population no
  longer exists and every one of those assertions would now be measuring
  nothing. DELETED rather than left with a band of `0..0`: a check whose
  subject has gone is worse than no check, because it reads like coverage. Its
  replication-factor scanner went with it.
  **WHAT REPLACED IT IS STRONGER.** The same corpus sweep now asserts RULING B
  ITSELF — every artifact that collapses at the default must name a LADDER RUNG
  as its reason (`n_coll - n_rung == 0`). A returning knee, by design or by
  accident, fails there. It is not vacuous: one corpus pattern reaches the
  [SEL-1] rung, so the assertion has a live subject.
  **§6 IS A DIFFERENT QUESTION FROM THE REST OF THE FILE** ([OPT-4]'s second
  commit, the [SEL-1] rung). Every other cell compares two languages for ONE
  artifact; §6 is about an artifact that did not previously EXIST. A pattern
  whose DFA overflows a cap AS THE ENGINE used to fall to a VM artifact with
  `RX_VM_PREFILTER "none"`, because rebuilding the prefilter would have been
  the identical machine that just overflowed — true of the exact language,
  false of the collapsed one. So the question is not "which language" but "a
  prefilter at all", and the evidence is a different stamp plus the deny flag
  returning the old outcome, which is the section's non-vacuity control: without
  it the cells would pass on a compiler whose caps had simply been raised.
  **§1 SPLIT IN TWO UNDER RULING B, and the split IS the ruling.** K39 can be
  answered two ways and only one is the default: COUNT-INDEPENDENT (reachable
  under `-fprefilter-collapse`, asserted on K39's own pair with its
  failing-direction control) and COUNT-BOUNDED (what a user gets — the caps
  bound the size, and a pattern whose exact artifact they refuse compiles via
  the size rung). Asserting only the first would be a claim about a flag nobody
  passes; asserting only the second would let the force flag rot.

## [OPT-4.1] `run_prefilter_collapse.sh` gains §6b, and §6 becomes half of a pair

The count-collapsed rescue is now GATED ON NON-NULLABILITY (`docs/spec/
tuning.md` §2.17): pcrec does not build a collapsed prefilter whose language
matches the empty string, because such a filter admits a zero-length match at
every position and can therefore dismiss none of them. pcrec-bench measured
that shape at 1.2-9.9x SLOWER than no prefilter at all (its O-10 item 3, pin
96e44c2) against the 2.2-4.6x the same rung WINS where structure survives the
collapse — and the rung could not tell the two populations apart.

**§6 AND §6b ARE THE SAME MACHINE FOUR CHARACTERS APART**, which is the only
form of control that carries information here. §6's witness is [SEL-1]/K40's
own overflow pattern; §6b's is that pattern wrapped in `(?:...)?` — one
epsilon in the NFA, the same DFA overflow, opposite sides of the predicate. §6
fails if the gate OVER-fires (a compiler that declined everything takes its
prefilter away); §6b fails if it UNDER-fires. Neither direction is safe alone,
and a predicate wired to a constant fails exactly one of them.

**THE EVIDENCE IS A DIFFERENT STAMP FROM §6's, NECESSARILY.** A declined
artifact carries NO `RX_VM_PREFILTER_LANG` at all — `match_api.md` §6.3's iff
makes the language macro conditional on there being a machine to name — so the
decline is read off `RX_ENGINE_SEL "declined-nullable"`, whose value is
written by `pcrec_engine_sel_name` in a different file from the `fit.prefilter`
clause that took the decision, with the ABSENCE of the LANG macro checked
beside it as the second, independent term.

**§2 GAINED A THIRD EXPECTATION RATHER THAN A SECOND FUNCTION.**
`lang_witness exact-nullable` shares `exact`'s LANGUAGE and its byte-identity
leg (a flag that changed nothing moved no byte) and differs only in the `_WHY`
line it requires — `"nullable collapsed language"`, which is what separates a
flag that reached a POLICY from one that reached a vacuity. Its two witnesses
are the `count-collapsed` rows above them minus one character.

**AND `-fprefilter` OVERRIDES THE DECLINE, asserted in §6b(3).** It is
do-or-die (D46/D47.3): the decline's alternative is NO prefilter, which is
exactly what an explicit `-fprefilter` forbids, so a request this pass cannot
honour must REFUSE rather than be silently answered with its opposite. The row
accepts either a hybrid or a named refusal and reports which — what it fails
on is a silent override. `-fprefilter-collapse` does NOT override it: that flag
chooses a LANGUAGE for a prefilter, not whether one exists.

Sabotage rows: S206 (predicate removed) and S207 (predicate inverted), on the
new `pfcollapse` mech arm. Both are answer-identical, so their corpus arm is
EXPECTED green — see `tests/mech/CLAUDE.md`'s own section for why that is the
arm working rather than a half-detection.
