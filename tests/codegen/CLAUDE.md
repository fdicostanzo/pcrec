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

- **run_wordctx_identity.sh** — [M6.2] wave B's BYTE-IDENTITY GATE, the same
  shape one axis over. `\b`/`\B` are the largest change any wave of [M6.2]
  makes to the engine — the class map is refined by the word set, every state
  gains a second closure, the accept becomes class-indexed where it varies,
  and the machine gains a third start state — and the claim is that a pattern
  WITHOUT them pays for none of it. Reference build is this tree's sources
  with `-DPCREC_NO_WORDCTX` (`has_word` pinned false); sabotage S71 is the
  measured failing direction. Landing figures: 1039 of 1039 `\b`-free corpus
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
  tree's sources with `-DPCREC_NO_MLINECTX` (`has_nl` pinned false); sabotage
  S76 is the measured failing direction.

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
  every `RX_PUSH` with its resume target, the set of `stv` slots actually
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
  (SAN-1: rides this GENCFLAGS compile with `gcc -fanalyzer`, opt-in).
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
`rx_fs[0-9]+\[256\]` would be satisfied by ANY engine present, so a check
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
2. **§3.8.3.1 — no `sfound` at the reverse boundary except through the
   context-indexed accept, from ANY writer.** The design states an invariant
   rather than a patch because there is more than one writer: the reverse
   SKIP's `sfound = pp;` is emitted under a COMPILE-TIME condition, so what
   lands in the artifact is a bare unconditional assignment with no runtime
   test to fail. The check enumerates every `sfound` assignment in the body
   and requires each to be conditioned on an accept read. A companion rule
   (2b) pins R30 N9: the boundary accept must be ATTACHED to the `pp <=
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

Two design points worth keeping:

- **The population is DERIVED, not typed.** The residual entry NAMES are
  read out of the artifact (each residual declaration is preceded by the
  backend's own `ENCODING RESIDUAL entry` comment), so a backend adding a
  second entry is covered the day it lands rather than the day someone
  remembers to extend a list here. Finding NO residual entry at all is a
  FAILURE — the empty-population shape this file's charter is about.
- **The check reads FUNCTION BODIES, not the whole file.** A residual name
  legitimately appears in comments, in its own declaration, and inside its
  own definition; anywhere else inside a file-scope function body is the
  violation. Six emission shapes (DFA memchr-prefilter, DFA bitmap-
  prefilter, anchored, VM, `--engine=vm`, `--emit-main`) in both artifact
  forms.

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
  write goes through `RX_SET` rather than straight to `stv[0]` — the macro is
  what records the old value on the trail, and without it a `\K` crossed on a
  LOSING path stays crossed.
- **rule 1b** — a `\K`-FREE VM artifact emits the PRE-WAVE `caps_out` body
  **character for character**, with the two lines pinned here as LITERALS. The
  literal is deliberate rather than lazy: "does not contain the `\K` form"
  would pass on an emitter that had rewritten the line into some third shape.
  This is also **the whole of wave E's byte-identity claim**, and why this
  directory gained no fifth `run_*_identity.sh`: the emitter reads `v.nkreset`
  at exactly ONE site, so the claim is about one predicate rather than about a
  construction spanning several. Its corpus-wide half was MEASURED ONCE
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
