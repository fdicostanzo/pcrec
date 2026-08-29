# tests/registry — the syntax construct registry, checked against the parser

Guards the SR-1 table in `src/parse/registry.c` (design: docs/dev/decisions.md
D24). The table describes every non-base PCRE construct declaratively; this
directory asserts that the description and the shipped parser actually agree.

## Files

- **definitions_check.c** / **run_definitions_tests.sh** — [DD-11.1]'s two
  required checks (docs/design/definitions_table.md §3 items 1-2): the
  STRUCTURAL check (every `RegRow.definitions` entry's output — a parsed
  DEFK_STR string or a DEFK_BUILDER's return value — is core-only
  vocabulary, via `pcrec_ast_all_core`/`pcrec_ast_is_core`,
  src/parse/definitions.c) and the CONTAINMENT check (the tag evaluator
  `pcrec_def_tag_applies` has exactly one caller in the tree, a shell grep
  in the `.sh` plus the same fact asserted from inside the built library in
  the `.c`). Two negative controls (`\Z`/A_EOL, `\B`/A_NWORDB — both real,
  shipped kinds the full reduction retires, §2) prove the structural
  predicate actually discriminates rather than passing everything for
  free; the containment grep's bite was verified live by a plant-rebuild-
  revert cycle (a synthetic second call site in src/gen/emit_dfa.c, proven
  to turn the check red, then reverted — not committed).
  **NOT YET WIRED into run_registry_tests.sh's guarded chain** — run
  standalone (`bash tests/registry/run_definitions_tests.sh`) until
  [DD-11.2]/[DD-11.3] land the standing `--list-definitions`/self-oracle
  surfaces this check is a precursor to; wiring lands with those, once the
  table's population (POSIX classes, `\c`/`\o`/`\N{U+`, the 9 base-tier
  literal escapes, `^`/`$`/`(?n)`) stops changing commit to commit.
- **registry_check.c** — links `build/libpcrec.a` and includes
  `src/core/internal.h`, so it compares the table with the parser inside one
  process rather than re-deriving either from CLI output
- **pcre2_check.c** — the same table against **libpcre2** (PC-3): the first
  check in this project that is not pcrec reading pcrec. Same link, plus a
  runtime `dlopen` through `../fuzz/pcre2_abi.h`. SKIPS LOUDLY and exits 0 when
  libpcre2-8-0 is absent, so a stranger's clone stays green. See its own
  section below
- **run_registry_tests.sh** — builds and runs both, plus compliance_section.py,
  PC-4 and (since [CHK-2] piece 1) axes_registry_check.sh; part of `make test`.
  Env: CC, KEEP=1, LIBPCREC (SAN-1: overrides
  the `build/libpcrec.a` these two link, default unchanged), SANFLAGS
  (SAN-1: extra flags appended to their builds, default empty) — both used by
  `make ubsan`/`make asan` to point this directory's own checks at the
  sanitizer-built library; see docs/testing.md "Sanitizer + lint battery"
- **run_pc4.sh / pc4_check.c / pc4_driver.c / pc4_subjects.h** — PC-4
  (MOD-0.3e), the SEMANTIC differential R8/C4-2 asked for and PC-3
  deliberately is not: what a PRODUCED construct MATCHES, cell by cell,
  against the live oracle. 273 deterministic patterns (11 esc + 28 posix
  spellings × 6 shapes, + 39 caseless bare forms — the first time `-i` has
  met an external oracle in this repository) × 271 shared subjects (every
  single byte + curated multis, ONE header embedded by both sides so the
  probed set cannot drift). Like `tests/fuzz/fuzz_driver.c`, pc4_driver.c is
  compiled ONCE against a throwaway pattern's gen.h and reused across every
  swept pattern's gen.o, so it sizes its caps array from `rx_info.ncaps`
  read at RUNTIME rather than the compile-time `RX_NCAPS` macro (which
  would be baked in from the throwaway pattern, not whichever pattern's
  gen.o driver.o ends up linked against). This was a live latent instance of
  the fuzz harness's own [M4.5]-era stack-smash bug — dormant only because
  today's PC-4 pattern space (escape classes, POSIX classes, quantifiers,
  anchors) has zero capturing constructs — found and fixed alongside the
  fuzzer's copy of the same bug (see tests/fuzz/README.md's "RX_NCAPS is NOT
  part of what's shared" section for the full mechanism). **[K21-class fix,
  2026-08-15]:** that stack-array fix ("the fuzz-driver stack smash",
  `89ccd89`) was a DIFFERENT bug from this one, in the same file — it did
  not touch pc4_driver.c's per-subject `if (rx_search(...))` truthiness
  check, which had the SAME shape as K21 (docs/dev/known_issues.md):
  `rx_search`'s return is three-valued, C-truthy on the negative
  RX_ERR_STEPS/RX_ERR_FRAMES give-up sentinels, so a give-up would have
  taken the match branch and printed `caps`. Fixed now: the driver
  discriminates `found == 1`/`== 0`/otherwise explicitly and prints
  `giveup steps`/`giveup frames` for that subject rather than fabricating
  a verdict. pc4_check.c treats a `giveup` line the same way it already
  treats libpcre2's OWN give-up (`mlimits`, below) — a non-comparable
  outcome, counted in its own `pcrec_giveups` bucket, excluded from
  `cells`, never entered into the match/nomatch agreement check, and
  asserted zero. Verified directly (not through the fixed 271-subject set,
  which has nothing long enough to burn a tiny step/frame budget): a
  scratch driver using the identical discrimination logic against a
  `--engine=vm --step-budget=50`/`--backtrack-frames=4` artifact prints
  `giveup steps`/`giveup frames` correctly; and pc4_check.c's new branch
  was verified in the FAILING direction by splicing one synthetic `giveup
  steps` line into a real `\d` sweep's results file — `cells` dropped by
  exactly 1, `pcrec_giveups` fired naming the count, and no spurious
  match/nomatch disagreement was reported for that cell. Dormant on the
  real sweep today (DFA-only pattern space, no `--engine=vm` anywhere in
  run_pc4.sh) — the real sweep's own 62,872-cell, 0-disagreement result is
  unchanged. Populations are EXACT predictions stated in
  pc4_check.c before the first run and confirmed on it: 232 both-accepted,
  41 refusal agreements (both directions checked — over-acceptance and
  over-rejection each fail naming the cell), 62,872 match cells, mlimit
  and (since the K21-class fix) `pcrec_giveups` both asserted zero on a
  backtrack-free, DFA-only pattern space. The pcrec side runs one process
  per PATTERN (all subjects in-process) through `gen_run`
  (`tests/lib/gen_timeout.sh`, `WATCHDOG_SECTION=registry`) — the shared
  run budget, a 512m RSS ceiling, and a `build/watchdog.log` line per run.
  whole sweep ~2.5 s bare; MEASURED (2026-08-16, isolated `run_pc4.sh`
  runs, this box): 9.2 s without the wrapper, 13.6 s with it (+~48%) across
  the 273 per-pattern runs, each individually well under a second (watchdog
  logged wall=0.10s per run). Skips loudly
  without libpcre2, probed BEFORE the gcc sweep is paid for; the runner
  carries a population-line needle so an unwired PC-4 fails rather than
  vanishes. LIVENESS proven in both axes before the zero was trusted: a
  one-bit bitmap sabotage fires per-pattern naming subject 0x35, and a
  dropped `-i` fold fires exactly the caseless posix cells — and the FIRST
  bitmap sabotage run returned zero failures because hand-maintained
  Makefile header deps did not include cls_bits.inc, so the sabotage never
  entered the binary (fixed in the same change; the lesson is the fuzz
  battery's one level down: prove the sabotage reached the binary before
  reading its zero)
- **axes_registry_check.sh** — [CHK-2] piece 1(a): the OPTIMIZATION-AXIS
  registry's own check, a DIFFERENT registry from the SR-1 syntax table
  above. Reads `pcrec --list-axes`'s TSV (`src/parse/axes_dump.c`) against
  `docs/spec/tuning.md` (every documented `(bit N)` heading),
  `cli/main.c` (the flag parser) and `docs/spec/match_api.md` §6.3 (the
  D46 stamp family's own home) — three files the dump never opens, so
  this is the INDEPENDENT side of the dump's own claim
  (`docs/spec/registry.md` §6/§7 states the boundary this dump does and
  does not prove). Three directions, every discrepancy named
  individually: (1) every dumped deny/force bit checked against
  `lib/pcrec.h`'s own definition and (where it has one) its CLI spelling
  in `cli/main.c`; (2) both `tuning.md`'s documented bits and
  `lib/pcrec.h`'s own `1u << N` bits (range 4-31, DERIVED with no upper
  bound since optk's 2e2914e — a hard-coded `4-15` here would have filtered
  bit 16 away before comparing, and bit 17 after it) swept to confirm every
  one appears SOMEWHERE in the dump — the reverse loss, an axis quietly
  dropped from `--list-axes`; (3) **[added on manager review, 2026-08-28]**
  every dumped `stamp_value` checked against `match_api.md` §6.3's own
  value-set table/string-literal pair for that macro, and every spec
  value swept back into the dump — the nine D46 bit constants
  (`PCREC_VM_RUNG_*`/`_STRAT_*`/`_PRUNE_*`) read from `src/gen/
  emit_dfa.c`'s own literal `#define` block instead of `lib/pcrec.h`,
  since they are emitted-artifact text the public header never declares;
  two named, cited exceptions in the script's own header (`RX_DFA_TABLE`'s
  composed `"mixed"`/`"none"`; the three ladder-fallback rung constants
  with no individual deny flag). 53 checks total. Run via
  `run_registry_tests.sh` below (its own coverage-count guard: == 53 PASS
  lines, exact). **Two bugs found and fixed while writing it**: bash's
  `IFS=$'\t' read` collapses runs of empty tab-delimited fields — tab is
  IFS *whitespace* regardless of what IFS is set to — exactly the gotcha
  `tests/lib/table.sh`'s own header comment already names from
  `tests/reject/`'s history; the row-reconstruction step separates
  fields with `\001` (not in bash's whitespace class) before the `read`
  loop that can see an empty field. And direction 3's markdown-table
  extraction first silently read the WRONG table — `match_api.md`'s
  tables are indented two spaces under their bullet, so a naive `^\|`
  row test skips past them to the next un-indented one — fixed by
  testing `^[ \t]*\|` instead; caught only by eyeballing the extracted
  values against the file, not by any test going red. Env: `PCREC`
  (default `build/pcrec`), `TUNING`/`CLIMAIN`/`MATCHAPI`/`EMITDFA`
  (override to point at a doctored scratch copy — the sabotage-validation
  lever; never point these at a file under this repo's own tracked tree)

## What it asserts

0. **Two invariants the class-bracket DOORWAY depends on and cannot assert
   itself** (R9). Both were true by accident before this, and each has a
   sabotage below. No `RK_CLASSBRACKET` row may use `]` as its selector — the
   doorway's scan treats "an unescaped `]` ends the class" and "delimiter + `]`
   closes the pair" as disjoint tests, which holds only while no delimiter is
   `]`; a critic proved the order of those two tests is otherwise arbitrary by
   swapping them for byte-identical results over 1.24M patterns. And every
   `RF_CLASS_NAMED` row must also carry `RF_CLASS_DELIM`, because the name is
   the text between the delimiters and the flag that says "this text is a name"
   has to be on the row whose extent the scan measures. Without the pairing the
   length computation underflows; it was memory-safe only because
   `pcrec_registry_posix_known` compares lengths before bytes, which is an
   implementation detail of a different function that nothing tied to this one.
   **The general rule R9 drew from both: when a dangerous operation is safe
   because of a fact that lives elsewhere, the assertion belongs where the fact
   is, not where the danger is.**
1. **Well-formedness** — no two rows claim one byte, catch-all rows come last,
   each row's `syntax` example really contains its selector byte, and the
   status/module/feature/engines/diagnostic fields are mutually consistent.
   Plus an EXACT row count (128 at [DD-14]'s close — the figure is pinned in registry_check.c and moves with every module that adds rows; it was 100 at Q2/SR-9; this file said 68 until
   2026-08-11, which is the drift an exact count is supposed to prevent
   happening to its own documentation) so rows cannot be deleted silently — the
   same "TABLE SHRANK" guard tests/reject/ carries. Note what R8/C4-10 measured
   about all three of these exact-count tripwires: each prints its own remedy,
   so following their instructions verbatim is how a row with a WRONG MODULE
   gets past the whole suite. They make a change VISIBLE in the diff; they do
   not make a wrong one fail. Only the hand-written rows in tests/reject/ do
   that, and only for rows someone wrote one for.
2. **table → parser** — every row's `syntax` is compiled for real, and the
   diagnostic must match the row EXACTLY. Substring matching would let a row
   name the wrong module and still pass.
3. **parser → table** — a 255-byte sweep of **all four** doorways. If the
   parser says "requires module" for a byte, a row must exist and name the same
   module; if a row claims a byte needs a module, the parser must really route
   it there; and a row whose diagnostic is fixed text (the collating rows) must
   match that text exactly. **This is the direction that catches a construct
   added to parse.c with no row** — the drift that produced the `\v` bug.
   Direction 2 alone is blind to it.
   *R4 correction:* the first version swept only two of the four doorways while
   this file already claimed all of them, and validated 1 of 3 class-bracket
   rows because fixed-text rejections carry no "requires module" marker.
   *Q1 correction (2026-08-10):* the `(*` doorway has its own `sweep_verb()`
   now, and the reason is a measured near-miss. The generic sweep asks "did the
   parser say *requires module*"; before Q1 all 255 bytes after `(*` said
   exactly that, so it exercised 255. Q1 made most of them say "not recognized"
   — correctly — and the generic sweep dropped from **255 bytes asserted to
   ONE** while still printing `PASS: sweep ... all 255 bytes agree`. A check
   that narrows to nothing without failing is this directory's own warning, one
   level down. `sweep_verb()` asserts instead that every byte REACHES the
   doorway, that its answer is one the registry can account for, and that
   PCRE2's two name tables are selected by CASE and nothing else — with
   liveness counters, because "one answer for everything" is exactly what the
   old sweep was reduced to.
4. **feature/module bijection** — a row carrying `FEAT_CLASSES` while printing
   "assertions" passed everything until a critic tried it. `registry.c`'s
   `M_<module>` macros now emit the pair together so a macro-built row cannot
   mismatch, but a LONGHAND row still can, and "correct by construction" is the
   kind of claim this project keeps losing when nothing tests it. Checked
   without an external module list (which would be a second home): across the
   table, mask and name must be a bijection, so one mismatched row necessarily
   collides with both the rows using its mask and those using its name.
5. **required rows** — a small hand-written manifest of constructs whose
   ABSENCE would silently regress a specific past incident (both collating
   rows, `\v`, `\b`, `(?:`, the two catch-alls). Everything above iterates the
   rows that exist and is therefore structurally blind to deletion: a critic
   removed both collating rows and all 116 checks stayed green. A coverage
   floor cannot fix this — it answers "did someone delete a lot", never "did
   someone delete the right ones".
6. **the MOD-0.2 arbitration** (2026-08-11) — row selection is recogniser +
   rank since MOD-0.2, and two checks own the migrated rules.
   `check_row_ranks`: every tailed row (18, a measured count with the
   R8/C4-10 caveat printed beside it) must sit above the fallback tier, or
   its construct is unreachable — the successor of the retired
   `check_tail_precedence`'s tailed-beats-fallback half. `check_arbitration_
   liveness`: per multi-row bucket, a FLOORED count of generated probes where
   more than one recogniser answers (10/15/15/50, predicted from the
   generator before the first run and confirmed exactly), plus the esc-`N`
   triple-answer assertion — the pair `\N{`/`\N{U+` is the only place the
   ordering between two TAILED ranks is observable, so its disappearance
   must fail loudly rather than leave rank untested (the retired check's
   liveness clause, re-homed; R11/M3's counter, D32 §9's retirement
   precondition). The D32 §9.5 migration scaffold (new engine vs the retired
   longest-tail-wins engine, 261,193 probes, 0 mismatches, 0 ambiguous) was
   deleted WITH the retired engine in one commit — an equivalence check
   cannot outlive its oracle honestly. The ambiguity defect path (two
   answers at the winning rank → "internal error: ambiguous registry
   arbitration...") was validated live: an equal-rank sabotage on the `\N`
   pair fires it with a clean exit 1 and 2 registry failures naming the row.
   R15 hardened all of this the same session: the liveness check now ends
   with the **no-ambiguity sweep** (every kind × sel × generated text,
   261,193 probes, zero winning-rank ties — the scaffold's deletion had
   left the `ambiguous` flag probed by nothing; equal-rank sabotage fails
   it directly), check_row_ranks also asserts **tails exist only at the
   escape and group doorways** (the other two ask the tail-less question
   and discard ambiguity — scans.c's prose assumption, now an assertion),
   the answer predicate is the engine's own exported
   `pcrec_registry_row_answers` (no duplicate to drift), and
   run_registry_tests.sh carries a **count (168 since MOD-0.6's K10 slice;
   167 since MOD-0.3b; 166 at R15) + manifest guard for registry_check
   itself**, mirroring PC-3's, with one
   NEGATIVE needle: the retired check's PASS line must not reappear. NOTE the division of
   labour R15's checks critic initially misread: these checks do NOT ask
   which row WINS — `check_table_to_parser` owns that (D32 §9.1's primary
   instrument), and a rank-value winner-swap sabotage fails it twice inside
   `make test`, measured.

7. **the MOD-0.3b port data** (2026-08-12) — `check_class_ports`, the
   unwired ports' only guard until the classes producers land. Populations
   PREDICTED before the first run and pinned (exactly 5 scalar class ports —
   `\b \g \k \8 \9` — 0 SET, 0 FN, 0 atom ports; slices 2-3 move them
   deliberately, in the same change as the producer). Values are
   oracle-tied, one rule per syntax shape: a bare-escape row's scalar must
   equal its libpcre2-fed `class_expect` byte (the port is never its own
   authority), a body-carrying row's must equal its selector letter (§14.3's
   literal-fallback law, FIX-3-measured). Sabotage-validated in three
   directions same-session: value drift on `\b` (0x08→0x09) fails the
   column tie, a zeroed `\k` scalar fails the fallback law, and deleting
   the call fires the count guard AND the manifest line.
8. **class-position reach** (MOD-0.6, K10's fourth net) — the generic
   `[\%c]` in-class sweep above supplies exactly one byte of tail, so it
   structurally cannot probe `[\N{U+41}]` (or any other tailed/body-
   carrying escape) at class position at all. `check_class_syntax_reach`
   closes that specific gap: for every RK_ESC row whose `syntax` carries a
   `tail` or body text past the bare `\X` form (today exactly 5: the `{U+`
   row, `\p`, `\P`, `\c`, `\o` — `\g`/`\k` are excused, base class ports,
   see below), it arbitrates on the REAL tail text a class doorway would
   see and confirms it resolves to THAT row, then confirms the compiled
   diagnostic promises that row's module. **Positive control, measured
   with a number at R19 close** (the panel's checks critic flagged the
   original record as count-less): re-applying `RF_CLASS_INVALID` to the
   `{U+` row fails EXACTLY ONE check — this one, naming the row and the
   unpromised module ("class-position reach: '\N{U+0041}' ... does not
   promise module 'unicode-props'"), measured on a scratch build
   2026-08-12. **What it cannot do, stated so
   it is not mistaken for more**: it predicts the expected text from the
   row's OWN current fields (same as `check_table_to_parser`), so it can
   never independently catch a WRONG FLAG the way K10 was wrong — only
   tests/reject/'s hand-written pins and PC-3's libpcre2 differential can
   do that, and always could. Positive-controlled by re-sabotaging K10
   (restoring `RF_CLASS_INVALID` on the `{U+` row): the check fails
   immediately, naming the row and the unpromised module.
9. **[M4.7a] the engine-capability TRIPWIRE** (docs/dev/plan.md's
   [SR-8]/[M4.7a] rows) — `check_engine_capability_tripwire` guards a
   deliberate NON-decision: SR-8's lowering-time engines-column
   consultation is NOT built in src/opt/select_engine.c today, because
   every VM_ONLY-masked `RS_MODULE` row lacks a producer (zero producers,
   zero customers — a manager redirect superseding an earlier reading that
   built the consultation ahead of need). The check asserts the fact that
   makes that omission safe: every such row's `aport.kind` is `PORT_NONE`.
   EXACT count, **48 rows since [M6.3]** (was 51 at M4.7a: 12 ESC + 38
   GROUP/GROUP_T + 1 VERB). [M6.3] is the FIRST time this population
   actually shrank rather than merely being asserted stable — module
   `named-groups` wired the first producer ever attached to a row this
   check had been watching, and the fix was NOT to build SR-8: a named
   group's AST is an ordinary A_CAP node, so the pre-existing generic
   capture-forcing rule in select_engine.c already sends it to the VM
   whenever it delivers a real capture slot, exactly as an unnamed group
   would be. The three declaring rows' `engines` mask moved from VM_ONLY to
   ANY_ENGINE instead (registry.c's own comment on those rows, and
   docs/dev/decisions.md's [M6.3] entry, carry the argument), which is what
   removes them from THIS check's population rather than tripping its
   `bad()` — 38 GROUP/GROUP_T rows became 35. Sabotage-validated (2026-08-17,
   scratch build, reverted before commit): wiring a dummy atom-position
   producer onto the `(?>...)` (atomic-groups) row fires this check by name
   AND `check_class_ports`' atom-port population guard (23→24, now
   26→27 post-[M6.3]) — two
   independent nets catching the same event, which is the point of a
   tripwire that also happens to sit next to a port-population check. The
   failure message is written to be read FIRST by whoever trips it: it
   names the exact next step (build SR-8 in select_engine.c) rather than
   only reporting a mismatch.

   **[M6.2] WAVE E IS THE FIRST REAL TRIP, and the exception it earned is
   the part to read before adding a second one.** `\K` genuinely IS VM-only
   — unlike [M6.3]'s named groups, whose AST is an ordinary `A_CAP` and
   which therefore LEFT the population by reclassification — so it stays in
   the population and the tripwire fires for exactly the reason it was
   written. The answer was still not to build SR-8: `\K`'s verdict is not
   "a registry column says VM", it is "this AST carries a node whose write
   is path-dependent", which is a fact about the TREE and not about the
   table, so a construct-specific `forces_*` row in select_engine.c is the
   honest shape and a generic column consultation designed around ONE
   customer is what [M4.7a] declined at sample size zero and D18/OS-0/D53
   forbid at sample size one.

   **The exception is not an allowlist entry — it PAYS.** The row is named
   (`RK_ESC`, `sel == 'K'`, module `assertions`) and, when present, the
   check goes on to ASSERT LIVE, through the same `pcrec_compile` every
   other check here drives, that `--engine=dfa` on `a\Kb` REFUSES naming
   the construct (D44.6/§9.2 item 2: the captures branch's
   `--no-captures` advice would be a lie here) AND that the same pattern
   COMPILES on the default engine — the second direction because a refusal
   test alone goes green on a compiler that stopped accepting `\K` at all.
   It borrows the feature gate to do so and ASSERTS the entry state was
   empty rather than saving-and-restoring blind, since every other check in
   this file believes it runs at the default set (pcre2_check.c's
   `mask_before != 0` rule, in miniature).

   Population accounting: `qualifying` stays 48 and `wired` becomes 1, so
   the pass condition is now `wired == kreset_exception` rather than
   `wired == 0`. **A SECOND construct arriving here is the trigger to build
   the generic consultation**, and the check's own comment says so — do not
   add a second exception.

   **THE TRIPWIRE IS GONE. Everything above item 9 describes is HISTORY, and
   this correction is dated 2026-08-22 ([M6.5.2]) because the paragraph above
   went stale at [M6.4.2] and stayed that way through a landing** — the
   hand-written-prose failure class this tree keeps cataloguing, met in the
   file that documents the checks. `(?>` was the second construct, D67 ruled
   SR-8 BUILT (`src/opt/select_engine.c`'s `forces_registry`), and
   `check_engine_capability_tripwire` was DELETED. What replaced it is
   `check_engine_capability`: the same demand turned the right way round —
   not "no VM_ONLY row has a producer" but **"EVERY VM_ONLY row that HAS one
   refuses `--engine=dfa` BY NAME"**, on a HAND-WRITTEN WITNESS per row whose
   construct genuinely bites, asserted in BOTH directions (the witness must
   also COMPILE on the default engine, or a compiler that had simply stopped
   accepting the construct would pass).

   Population accounting, re-derived from a run at [M6.5.2]: **`qualifying`
   54, `wired` 18.** 48 → 52 at [M6.4.2] (the four RK_QUANTSUFFIX rows) →
   54 now (the two `\g<` / `\g'` rows module `backrefs` added for module
   `recursion`); `wired` 1 → 6 → 18 (backrefs' twelve). **Those twelve are
   what made SR-8 the right build rather than a third exception**: the
   [M6.5.1] lane measured the tripwire's population against its own design
   and found backrefs would not be a third exception but TWELVE, which is
   the measurement D67 turns on.

10. **[D65] the BUILT-STATUS defect assertion** (docs/dev/plan.md's post-M6.2
    queue item 4; docs/design/registry_built_status_memo.md, ratified
    wholesale 2026-08-21) — `check_built_status_defects` iterates all 118
    rows (100 when this paragraph was written; 104 at [M6.4.2], 106 at
    [M6.5.2], 118 at [M6.6.2] wave F's twelve alpha-spelling INDEX rows) and calls `pcrec_construct_built_status` (src/parse/syntax_dump.c),
    the SAME function `pcrec --list-syntax`'s new `built` column calls, on
    every one. It is a defect check, not a status check: `--list-syntax` and
    the generated compliance index render `built`/`unbuilt`/`—`, and this
    check asserts the FOURTH bucket, `PCREC_BUILT_DEFECT` (a row whose own
    well-formed `syntax` — guaranteed reachable by rule 1's exact-row-count
    convention above — answered neither built nor unbuilt), never fires. It
    also asserts the process-global enabled set (src/parse/enabled.c) is
    restored to exactly what it was before the run, since the classifier
    mutates it once per row (forces "all" open, probes, restores) — the same
    `pcre2_check.c` "gated pass" shape, in miniature, over 106 calls instead
    of one.

    **[M6.4.2] ADDED AN EXACT TALLY BESIDE THE DEFECT ASSERTION, and it is a
    different check wearing the same function's name.** "0 defects" is
    satisfied by a table in which a construct SILENTLY STOPPED BEING BUILT:
    `built` drops, `unbuilt` rises, the sum is unchanged and nothing goes red
    — and the generated compliance index RENDERS that column, so it is a
    documentation regression nothing else in the tree can see. The three
    numbers are therefore pinned EXACT and each module's landing moves them
    in the same commit. **106 = 52 built + 48 unbuilt + 6 n/a** at [M6.5.2],
    from 104 = 38 + 60 + 6: fourteen rows flipped to `built` (`\0`, `\1`..`\9`,
    `\k`, `\g`, `(?J)`) and two were added born `unbuilt`. Four of the
    fourteen classify `built` only because module `backrefs` DEFERS reference
    validity to end of parse — `\1`, `\g{-1}`, `\k<name>` and `(?P=n)` are all
    error-115-class STANDALONE in PCRE2, and this derivation drives each row's
    `syntax` ALONE — which is a real dependency and is why that module's
    resolution has exactly one site. It stopped being theoretical during that
    landing: while the relative form refused AT THE PORT for an out-of-range
    number, the `\g` row's own `syntax` refused there too and this column
    called a construct the module BUILDS `unbuilt`.

    **Sabotage-validated in both directions** (measured on a scratch copy,
    reverted before commit): forcing the `\A` row's `aport` to `NO_PORT`
    flips its `--list-syntax` column from `built` to `unbuilt` and this
    check stays GREEN — a real refusal is not a defect, which is the whole
    point of having two buckets rather than one. Corrupting the same row's
    `syntax` from `"\\A"` to `"A"` (so it no longer reaches its own
    doorway, breaking SR-1's own precondition) flips the column to `defect`
    and this check FAILS, naming the row. Neither sabotage moved any other
    check in this file or in PC-3.

    **Why the classifier reads `res.answered_at` rather than the refusal
    TEXT**, recorded because a narrower first draft measured wrong on three
    real rows before landing on this shape: module `verbs` (a direct call,
    not a port — mod_verbs.c) and module `unicode-props` (bypasses
    `aport`/`cport` entirely — mod_uprops.c) both refuse with the
    CLOSED-gate wording ("requires module 'X'") even with their gate
    forced open, since neither routes through ext.c's shared
    ENABLED-BUT-UNBUILT epilogue; a refusal-text match would have wrongly
    scored both as registry defects. `res.answered_at == WANT_RESULT` is
    D33's own "gate open, port missing" signal instead, true for both —
    the gate genuinely was open, the PORT had nothing to say. **And why the
    gate forces "all" open rather than only each row's own module**: a
    first draft did the narrower thing and undercounted `(?m)` — the
    letter's own semantic gate (mod_modifiers.c's case 'm') checks
    `FEAT_ASSERTIONS`, not the dispatching `GROUP_OPT` row's own
    `FEAT_MODIFIERS` — a real cross-module dependency no per-row module
    lookup can see. Forcing every module open cannot turn a genuinely
    unbuilt construct built (MEASURED for `verbs`/`unicode-props` above:
    same refusal regardless of how many OTHER modules are on), so the
    wider force costs nothing and fixed the one real gap found while
    verifying this against the shipped compiler.

The probe patterns come from each row's own `syntax` field, so a new row covers
itself with no edit here. That is sound because this is a conformance check
between two descriptions, not a control: it asserts the two agree, never that
the rejection is CORRECT. Correctness is tests/reject/'s job, and its
accept-controls stay hand-written for precisely the reason this file does not
need to be (SR-4, and the trie-identity lesson about controls sharing a source
with the thing they control).

**Know what that boundary costs you.** This file cannot distinguish "both
descriptions right" from "both wrong the same way" — the likelier human error,
since one person maintaining two files from one misunderstanding gets both wrong
identically. A critic confirmed it: the same wrong module name written into BOTH
parse.c and registry.c passed 116/116 here (the check count at the time of that
measurement; it is 127 now — the RESULT is what matters, not the total). It was
caught by tests/reject/, whose hand-written expectations are literals — 144 of
them as of R7, when this sentence last said 93 — so tests/reject/ is not
decoration, it is the control this file deliberately is not. Two things narrow
the gap further: `registry.c`'s `M_<module>` macros make an invented module name
a compile error, and they pair each feature bit with its diagnostic name so a
macro-built row cannot mismatch (a longhand one still can — hence the bijection
check above). **Residual risk, open:** a NEW construct given the same
wrong module in both files, with no tests/reject/ row added, is caught by
nothing.

## Sabotage validation

The check was validated by eight edits to `src/parse/registry.c`, each reverted
after measuring; every one was caught. The last three exist because a critic
proved the first five could all pass while the table lost rows or mismatched a
module:

| sabotage edit | failures |
|---|---|
| `\v` row's module `"classes"` → `"assertions"` | 4 |
| delete the `\K` row entirely | 2 (both sweeps) |
| add a row for `\n`, a BASE escape the parser compiles | 4 |
| reword the collating message to "are unsupported" | 2 |
| drop `RF_CLASS_BASE` from the `\b` row | 2 |
| delete BOTH collating rows (R4 F2 — was **invisible** before the manifest) | 2 |
| delete the `(?:` base row | 1 |
| `\b` row longhand with `FEAT_CLASSES` but module `"assertions"` (R4 E1) | many |
| `RF_CLASS_DELIM \| RF_CLASS_NAMED` → `RF_CLASS_NAMED` (R9/C3-1) | 3 (+23 in PC-3) |
| add a `]`-selector `RK_CLASSBRACKET` row (R9/C2-1) | 2 (+1 in PC-3) |
| R20/OPTRUN-1: delete `group_answer`'s truncation branch (`(?P` at end of pattern) | 1 — the `(?%c` sweep's truncation exception, which is the ONLY generated instrument that reaches this cell: PC-3's tail-sweep template always inserts a byte after the prefix (+1 in tests/reject) |
| [M4.7a]: wire a dummy PORT_SCALAR atom-position producer onto the `(?>...)` (atomic-groups) row, a `VM_ONLY`/`RS_MODULE` row | 2 — `check_engine_capability_tripwire` (by name) AND `check_class_ports`' atom-port population guard (23→24), independently |
| [D65]: force the `\A` row's `aport` to `NO_PORT` (a real, honest un-wiring) | 0 — `check_built_status_defects` stays GREEN, correctly: the `--list-syntax` column flips `built` → `unbuilt`, which is not a defect |
| [D65]: corrupt the `\A` row's `syntax` from `"\\A"` to `"A"` (breaks SR-1's own reach-its-own-doorway precondition) | 1 — `check_built_status_defects`, naming the row; the `--list-syntax` column flips to `defect` |

## pcre2_check.c — the external check (PC-3)

Everything else in this directory, and in tests/reject/, is **pcrec checking
pcrec**. That is not a criticism of those checks; it is their measured limit,
recorded three separate times (R4, R5, R6): a row that is plausibly WRONG in the
single home is invisible, because the wrongness is what both sides read.

`pcre2_check.c` asks libpcre2 instead. Three parts:

1. **Every row's claim.** An `RS_MODULE` row says "PCRE2 HAS this and pcrec has
   not implemented it", so libpcre2 must COMPILE the probe — a row naming a
   construct PCRE2 does not have fails there. An `RS_REJECTED` row says
   "agreement IS compliance", so libpcre2 must REJECT it *and pcrec's message
   must be PCRE2's message*, not merely some rejection. **Mind the polarity:**
   docs/dev/plan.md had check (b) backwards until R6, and as written it would have
   passed every fabricated row it exists to catch.
2. **22 context wrappers.** A row's `syntax` reaches pcrec's DOORWAY, which is a
   weaker contract than "libpcre2 will compile this": `\3` needs three groups,
   `(?1)` needs one, `\k<name>` needs the name declared. Two guards keep the
   wrappers from becoming a way to paper over a bad row — a wrapper must CONTAIN
   the row's `syntax` verbatim, and a wrapper that is not NECESSARY is an error.
   A row with no wrapper whose syntax will not compile is a FAILURE, never a
   skip.
3. **Two more generated differentials at the CLASS-BRACKET doorway** (FIX-2):
   1680 patterns over delimiters x bodies x shapes x trailers, asserting no
   over-acceptance and no over-rejection; and ~150k POSIX class NAME probes from
   the same libpcre2-derived pool, asserting that a name libpcre2 has is
   deferred to a module and a name it lacks is not. The first found 126
   divergences on its first run where the plan had five hand-pinned cases; the
   second found two constructs a hand-written name list had missed (`[[:<:]]`
   and `[[:>:]]`) and refuted two successive wrong versions of K4's escape rule.

   **R9 found the first of those two probing less than it printed.** The shape
   written to exercise K4's nested-opener rule, `[[%ca[%cb%c]%c]]`, takes four
   `%c` and no `%s` while the call site passed the body string as its second
   argument — so a `const char *` was read as an `int`. Undefined behaviour;
   in practice the low byte of a literal's address, and at `-O0` sometimes NUL,
   truncating 21 probes to the stub `[[=a[`. Which patterns the sweep probed
   depended on `.rodata` layout while the header kept printing 1680, and
   `-Wall -Wextra` cannot see a non-literal format so `make strict` was clean.
   Net effect: 42 same-delimiter nested openers in the whole sweep, all at `:`,
   **zero at `.` and `=`** — the two rows for which rule 2 is the offset-only
   branch. Replaced with `cls_expand`, a positional expander with no argument
   list to fall out of step with; the sweep now generates 98/56/56 and still
   reports zero divergences, so the RULE was right and only the instrument was
   wrong.

   The guard is a **per-delimiter nested-opener floor**, and it is per-construct
   on purpose: "did the sweep reach a module" and "did both verdict buckets
   fill" were both green while one whole construct went ungenerated. Note what
   its own first version did — it counted ONE `[`+delimiter, which makes the
   ordinary inner bracket `[x[=a=]]` look like a nested opener, so it read
   511/504/504 and passed the sabotage. Two occurrences is the definition: the
   pair being scanned, plus the one that wins.

   **And it counts SIX buckets, delimiter x position, for a reason worth not
   re-learning.** Rule 2 has two positions, and when the 4a shapes were added
   (R9/C2-3, below) the per-delimiter floor stopped being able to detect the
   loss of the 4b shape: the 4a openers kept the counts non-zero, so the guard
   written for R9/C1-1 passed the very sabotage it was written for. Extending a
   check disarmed it. Each shape's removal now fires independently — verify that
   with a positive control if you ever add a seventh shape.

   R9/C2-3 is why the 4a shapes exist at all: turning rule 2 off at the class's
   own bracket for `.` and `=` only produces 1,416 over-rejections against
   libpcre2 — reduction `[.[.]`, five bytes, which libpcre2 compiles as a class
   of `.` and `[` — and the whole repository stayed green, including the
   nested-opener floor, because every nested opener generated was a 4b one.

   The differential also reads pcrec's MESSAGE in the both-refuse half now
   (R9/C1-8). It used to count `pc2 != 0 && rejected` as agreement without
   looking, which is 746 of the patterns and precisely where "is a module
   promised?" lives — so doorway 4a had no external check of its own
   over-promise. Distinguishing a real one from an honest one is mechanical
   rather than a hand-listed exemption: append the class's `]` and ask libpcre2
   again. `[[:alpha:]` then compiles, so pcrec deferring there is honest;
   `[:alpha:]]` still does not, so the 4a over-promise is caught.
4. **The verb NAME differential**, and this is the part that scales. Candidate
   names are generated from **libpcre2's own shared object** — its compiled-in
   name tables, read via `dlinfo`, expanded to every prefix and suffix — plus
   single-character mutations of the names pcrec claims, plus all 255 bytes,
   plus LENGTHS straddling the 126-130 boundary. ~75,000 candidates in 13
   forms, ~973,700 probes, about 3 seconds. libpcre2's verdict on each decides
   what pcrec owes.

   **`pool_from_lengths`'s alphabet is not just `A`/`a` any more** (K15,
   2026-08-12, docs/dev/known_issues.md): the same 126-130 lengths are also
   generated from three non-identifier filler bytes (space, `*`, 0x80), so
   the "long AND non-identifier" cell — invisible to identifier-only
   lengths — is finally reachable. It diverges from libpcre2: pcrec's extent
   scan hits the 128-code-unit cap before comparing the run to a table
   entry ("too long"), libpcre2's scan stops at the first non-alnum/`_`
   byte and answers "not recognized" about the short prefix. Ruled an
   acceptable tier-2 divergence under D26 (Frank, 2026-08-12) and given
   **this file's one exclusion**, `k15_excluded()`, scoped to exactly that
   cell — everything else in this differential, including the same
   non-identifier fillers UNDER the cap and identifier runs OVER it, is
   still compared with no exclusion and still agrees. See
   docs/dev/known_issues.md K15 and docs/pcre2_compliance.md's Backtracking
   control verbs section.

The prefix/suffix expansion is not decoration: `ANYCRLF`, `CRLF` and `LF` are
real PCRE2 option names that appear in the binary only INSIDE `BSR_ANYCRLF`, so
a pool of whole runs would have missed three names this check exists to notice.

5. **The DELIMITER byte sweep and the NAME x POSITION cross-product**, both
   added at R9 and both closing a hole the panel demonstrated with a live
   sabotage. `CLS_DELIMS` is `":.="`, hand-listed from pcrec's rows, so before
   R9 the only externally-oracled instrument at this doorway never left three
   bytes; a critic added a `!` construct with no registry row and every suite in
   the repo stayed green. The byte sweep runs 255 bytes x 5 shapes against
   libpcre2, and its liveness assertion is worth copying: it does not ask the
   table how many delimiters there are, it asks how many BYTES behave
   differently from an ordinary class member. That is a question only the parser
   can answer, so it can see a construct the registry does not know about.
   Expect `:` `.` `=` and `\` — the last is the class escape, kept in rather
   than special-cased out.
   The position sweep exists because two large honest differentials left a hole
   between them: the name sweep fixes position at `[[:NAME:]]`, the shape sweep
   never uses `<`/`>` as a body, and `<`/`>` are the two names libpcre2 accepts
   ONLY as a class's entire content. **Ask what your axes are and whether
   anything varies two of them together** — making either sweep bigger would
   never have found it.

6. **The `\p`/`\P` shape-space differential** (MOD-0.6 slice 4,
   `check_uprops_differential`), the module's first external check —
   `check_class_syntax_reach` (registry_check.c) only proves the row
   arbitrates to itself and promises a module; nothing before this compared
   pcrec's message and offset against libpcre2's own opinion of the name.
   1976 probes: `\p`/`\P` x prefix (`""`/`"^"`) x name (the 14 short names
   both cases, `Alpha`/`Alphabetic`/`Any`/`Foo`, and the empty name) x noise
   (none, leading/trailing space, internal hyphen/underscore/space,
   mixed-case — all measured insignificant, docs/design/design_notes_mod06.md §3)
   x shape (bare `\pX` for single letters, `{...}` for everything) x
   position (atom, class, class as low/high range endpoint, negated class),
   plus a 52-letter sweep (bare and `{X}`, both selectors, atom and class
   position) that is the INDEPENDENT check on `mod_uprops.c`'s hand-written
   14-of-52 short-name table (the manager's phase-2 ruling 2, §8): dropping a
   letter from that table is invisible to everything else in the suite and
   fails this check 20/20 (measured, reverted before commit — the twenty is
   the file's 20-report cap, and every failure names the dropped letter
   across all 5 positions and both cases).

   **What is oracle-derived and what is not, per cell.** The claim libpcre2
   CAN adjudicate — for the single-significant-character axis, is this
   letter a Unicode general-category short code — is answered by a live
   `pcre2_try` on the cell's own escape text, never by consulting
   `mod_uprops.c`'s table or a hardcoded pass/fail list here (that would be
   the check-design failure the memory `pcrec-check-design-lessons` names: a
   table generated from libpcre2 and checked by a differential against the
   same libpcre2 is one source wearing two hats). The AXIS BOUNDARY itself
   — a single significant character with no `=` is the only claim pcrec's
   table promises to be exhaustive for; every other well-formed body gets
   the GENERIC "requires module" text unconditionally regardless of what
   libpcre2 says about the name — is pcrec's OWN taxonomy decision (manager
   ruling 3), the same way a module NAME is pcrec's own taxonomy and no
   oracle query can arbitrate it.

   **The offset obligation is computed, not oracle-matched**, per D26: pcrec
   pins its OWN offset convention, not PCRE2's. `escape_start + 2 +
   strlen(body)` reproduces `mod_uprops.c`'s "one past the last byte
   consumed" rule exactly (docs/design/design_notes_mod06.md §3), and this is what
   proves the doorway's offset arithmetic is POSITION-INVARIANT — the same
   relative blame regardless of how many bytes of class-bracket/range/
   negation machinery precede the backslash — rather than merely re-deriving
   the eight offsets tests/reject/'s hand-written pins already cover at atom
   position.

   **What this check does NOT generate**, stated so its liveness buckets are
   not misread as wider than they are: every cell is WELL-FORMED by
   construction (a real name run, a real closing brace). The malformed-shape
   space — truncated, unterminated, a non-letter/non-brace tail byte, the
   48/49-character cap boundary, whether the caret counts toward it — stays
   pinned by hand, offset by offset, in tests/reject/run_reject_tests.sh; S32
   (the cap off-by-one) and S33 (the caret-consume drop) are the mech
   sabotages that validate THAT space, not this one.

7. **The GATED pass** (MOD-0.8c slice 2, `check_gated_option_space`), which
   closes R20's OPTRUN-B3. Everything above this line — every sweep, every
   differential, all 48.7M probes of the `(?` doorway — compiles pcrec at the
   DEFAULT enabled set, which is EMPTY. So every module-owned construct is
   refused at the gate before a producer runs, and what this file has always
   measured is RECOGNITION. R20 recorded the consequence as a boundary; SPEC-1
   had already paid for it. `a(?i)*` was accepted by pcrec with the gate open,
   is libpcre2 error 109, and the emitted matcher really matched `a`/`aa`/`aaa`
   — while at the closed gate the same pattern is correctly refused as
   "requires module 'modifiers'", so every differential here agreed with a
   compiler that was wrong.

   The pass re-walks three spaces — the option-run space (19,448 cells), the
   `(?` byte space (7,650) and both halves of the tail sweeps (20,400) — plus a
   fourth family that is the defect's own shape: **accepted spelling ×
   quantifier**, GENERATED from the spellings family 1 just measured both
   engines accepting, not hand-listed. 49,034 cells, +0.25s on PC-3's 3.33s.

   **The three closed-gate sweeps above are RECOGNITION TIER, and now say so
   in their own PASS lines** (`[RECOGNITION tier: default gate]`) as well as in
   a comment block above them. That is not decoration: comparing pcrec's
   gate-refusal against libpcre2 — which has everything on, always — answers
   "is this construct real, and whose is it", and is not behavioural coverage
   of a producing construct. SPEC-1 lived in exactly that mislabel.

   **The clause is check14's T1, and it is a different bar from every other
   sweep in this file.** Those ask recognition (did libpcre2 DISPATCH here),
   because at a closed gate acceptance is not on the table. Here it is, so the
   question becomes acceptance: *pcrec must not ACCEPT what libpcre2 REJECTS*.
   Error 109 is a construct libpcre2 dispatched to and then refused — a T1
   violation, but a recognition AGREEMENT, so reading OPTRUN-B3's cell with the
   old bar would have passed SPEC-1 too. T3 (a refusal emits no C) rides along
   free in-process, observed as `out.c_src == NULL` rather than inferred from
   the return code.

   **T2 is deliberately not asserted** (pcrec must not refuse as invalid what
   libpcre2 accepts). Three live, RULED tier-2 divergences are T2-shaped — K15,
   K16, and the deferred-validation ordering in docs/pcre2_compliance.md — so a
   T2 clause here would fire on decisions already made rather than on
   regressions.

   **THE ENABLED SET IS FOCUSED: `modifiers` alone, one pass per feature,
   never `all`** (docs/testing.md, "The differential gate principle", Frank
   2026-08-12). The pass is parameterised by its set, names it in every line it
   prints (`gated[modifiers] ...`), and REFUSES a set that is `all` or a comma
   list — "focused" is the property the whole pass rests on, so it is asserted
   rather than trusted. Two reasons: **attribution** (a failure implicates the
   module under test, not one of seventeen or an interaction between them) and
   **coverage honesty** (cross-module interaction is a real axis that earns its
   own deliberate, labelled sweeps, and must not be smuggled in as uncontrolled
   noise inside every differential). Same rule `--features` already pins:
   per-module, not blanket.

   `modifiers` is the set because it is the one module with PRODUCERS these
   three spaces exercise. Measured, and worth recording because it is what
   makes focusing free here: `modifiers` alone and `all` give **byte-identical
   populations** (49,034 cells, 3,769 accepted by libpcre2, 2,339 by pcrec) —
   every other module still refuses at the gate in this space, so `all` was
   buying nothing but ambiguity. When a second module gains producers at this
   doorway it gets its OWN call with its OWN name, not an extra bit in this one.

   The set is a process-global; the pass runs LAST, installs it, restores
   `none`, and asserts both transitions — the restore assertion now says why it
   matters, which is that the NEXT focused pass would otherwise not be focused.

   **One space, two walkers, held together by checksum.** The gated pass does
   not refactor the closed-gate checks (the R9 lesson — *extending a check
   disarmed it* — argues against reshaping three tuned checks to share a
   loop). It walks the same hoisted tables and asserts the SAME three pinned
   pattern-set checksums, so a generator that drifts from its closed-gate twin
   fails rather than quietly measuring a different space.

   **Failing-direction, measured 2026-08-12**: reverting SPEC-1's fix in a
   scratch build (drop `|| a->not_repeatable` from parse.c's `p_rep`) fires
   **672 T1 cells** here (12 reported, capped), naming `a(?)*`, `a(?x)+` and
   the rest of the shape — while `registry_check` and the CLI suite stay
   completely green. `tests/reject` also fires 11, from the hand pins that
   landed WITH the fix; the difference is that those pin the spellings someone
   wrote down and this covers the generated space, which is the whole
   check11-versus-check14 lesson one file over.

   **What it does not do**: it inherits its predecessors' residual, since it
   walks their tables. The zero-tail cell `(?P` is still ungenerated and the
   option runs still stop at length 3. No class-bracket or POSIX-name space is
   re-run gated — that is the `classes` module's production surface and under
   the focused rule it would be a SEPARATE pass, `check_gated_option_space`'s
   sibling with `classes` alone, not an extra bit on this one. Adding it is a
   one-line call plus its own floors; it is deliberately not built here.
   Cross-module interaction (`modifiers` + `classes` enabled together) is a
   real axis and is likewise deliberately absent: it belongs in a sweep that
   says that is what it is measuring.

## Coverage guard and manifest (R9/C1-7)

`run_registry_tests.sh` now asserts PC-3's exact passing-check count AND a
manifest of checks named by the finding each one closes. Until R9 this
directory had neither, while `tests/reject/` has carried both since R7 — and
this is the directory holding the expensive external checks. A critic deleted
both new differentials from `main()` plus the 4a sweep and everything stayed
green; the only trace was 129 → 128 and 81 → 76 in output nothing compared.
Two layers on purpose, for the reason tests/reject/ gives: the count makes a
deletion visible in the diff, the manifest makes it fail. Update the count
deliberately when you add a check, and add a manifest line whenever a check is
the ONLY thing standing between the repo and a specific past finding.

**This is the first mechanism in the project that can see a MISSING row.**
Everything else iterates what exists. Delete the `ACCEPT` name, misspell it
`ACCPET`, or invent a verb PCRE2 does not have, and none of that is detectable
by anything else in this repo at any effort. It works only because of Q1 (D25):
while one catch-all answered "requires module 'verbs'" for every name, pcrec's
answer did not depend on the name and the comparison was vacuous. Measured —
reverting the doorway to its pre-Q1 behaviour produces 21 failures here and,
before this file existed, produced none anywhere.

### What it does NOT establish

- **Module names are pcrec's own taxonomy** and no outside authority can check
  them. libpcre2 can say a construct exists; it cannot say `\d` belongs to a
  module called `classes`. tests/reject/'s hand-written rows remain the only
  check of that, exactly as before.
- **options = 0.** No `PCRE2_UTF`, no `PCRE2_UCP`, no `PCRE2_CASELESS`. Every
  claim is about default 8-bit mode; no UTF conformance is measured anywhere in
  this repo, and `-i` has never been run against `PCRE2_CASELESS`.
- **The `(?` doorway now gets three generated differentials of its own** (Q2),
  so the sentence that stood here — "only the `(*` doorway gets a name
  differential" — is retired. A 7650-probe BYTE sweep (libpcre2 recognises a
  byte after `(?` iff pcrec promises a module: 38 vs 217, both populations
  pinned), a 19448-probe OPTION-RUN sweep over runs of length 0-3, and 20400
  probes of TAIL sweeps for `(?P` `(?<` `(?+` `(?-`. `(?P=` versus `(?P<` and
  `\N{U+hhhh}` versus `\N` are no longer unswept.
  **Read what the tail sweeps can and cannot do.** `(?<` and `(?+` answer alike
  for every tail under libpcre2, so for those two prefixes agreement is free and
  proves nothing; only `(?P` and `(?-` have both buckets populated, which is why
  a live-prefix counter is asserted and why `(?<`'s module split is pinned by
  hand in tests/reject/ instead. (The floor sits at exactly 2 of 4 with no
  margin — measured, left as measured; the code comment beside it named only
  `(?<` as saturated until R20/OPTRUN-3 corrected it to name both, with the
  populations.)
  **The tail sweeps have TWO halves since R20/OPTRUN-1**, 10200 probes each
  (hence 20400 above, up from 10200), and the split is a defect fix rather
  than a widening. Every completion used to contain a `)`, so every generated
  pattern was a CLOSED construct and the whole TRUNCATED region was invisible
  to all 48.7M probes of this doorway — which is exactly where OPTRUN-1 lived.
  The truncated half is the same ten shapes with the `)` removed.
  **They are aggregated SEPARATELY, and the first version of the extension was
  not**: the per-byte verdict is an OR across completions, so appending
  truncated shapes to the same OR left them structurally unable to contribute
  a mismatch — measured VACUOUS, with a sabotage that drops every truncated
  module promise in a tailed bucket scoring ZERO failures repository-wide.
  Split into `HALF_CLOSED`/`HALF_TRUNC` with their own verdicts, populations
  and mismatch reports, the same sabotage fires 12 (capped). That is this
  directory's own recorded lesson — *extending a check disarmed it*, the R9
  nested-opener floor — recurring one doorway over, and it is why the PASS
  line prints both halves' populations.
  **Residual, stated because narrowing a blind spot is not closing it:** the
  template `"%s(?%s%c%s"` always inserts a byte after the prefix, so the
  ZERO-TAIL cell `(?P` itself is still a pattern this loop cannot generate.
  It is covered by a hand pin in tests/reject/ and by an expectation in
  registry_check's `(?%c` sweep, whose template does end at the selector.
- **RECOGNITION is the bar, not compilation, and the distinction is
  load-bearing.** PCRE2's "no construct here" errors are 111 and 141; every
  other error means it DISPATCHED and is complaining about the body. `(?+x)` is
  error 129, `(?i-m-s)` is 194, `(?0J)` is 114 — all constructs pcrec owes a
  module for. Bucketing any of those with 111 makes the check demand the
  over-promise Q2 removed, in reverse: the option-run sweep was first written
  against "does it compile" and reported 967 mismatches that were entirely the
  check's error.
- **A compiling probe is not a semantic check.** `\v` compiles in libpcre2 and
  in python `re`, and they mean different things by it. PC-3 proves the row
  names a construct PCRE2 has; the corpus and the fuzzer are what test meaning.

### Sabotage validation

**46 edits** (count the table's rows — this sentence said `27` from Q2/SR-9
until MOD-0.8c, which is a hand-maintained figure in the directory whose own
docs explain why those go stale; `tests/mech/` exists because of exactly this).
Each was reverted after measuring, and each was caught — but see the
tail-precedence row, which was NOT caught on its first run and is the reason two
more guards exist. **Record the EDIT, not just the count.** Six exist because
the R8 panel proved the first fourteen could all pass while the check was doing
much less than it claimed.

| sabotage (exact edit, in a scratch copy) | PC-3 failures |
|---|---|
| delete the `{"ACCEPT", ...}` row from `verb_upper` | 6 |
| `{"ACCEPT",` → `{"ACCPET",` | 21 (capped) |
| drop `VF_ATSTART` from the `CR` row | 10 |
| reword `"(*MARK) must have an argument"` | 20 (capped) |
| insert `{"NOTAVERB", VF_BARE, 0, NULL}` | 17 |
| verb row `syntax` `"(*ACCEPT)"` → `"(*...)"` (its pre-PC-3 value) | 1 |
| reword the collating rejection message (2 rows) | 2 |
| wrapper `"(a)\\1"` → `"(a)b"` (no longer contains its row's syntax) | 1 |
| drop `VF_GROUPARG` from `pla` | 3 |
| drop `VF_EMPTYARG` from `ACCEPT` | 4 |
| reword the lower table's "not recognized" | 20 (capped) |
| delete the `at != 0` start-of-pattern check (MOD-0.4: moved from ext.c to mod_verbs.c with the rest of `pcrec_ext_verb`; edit lands in mod_verbs.c now) | 20 (capped) — the same edit is independently mech-encoded as `tests/mech/sabotages/S29_verb_atstart_drop.sh` (MOD-0.4c), DETECTED via the `reject` suite alone (`a(*CR)`'s manifest pin), a cheaper channel than this libpcre2-backed one that still holds when PC-3 SKIPS |
| **restore pre-Q1 behaviour: the doorway ignores the name** | 21 (capped) |
| swap the two tables' "not recognized" messages | 21 (capped) |
| **`pool_from_library` succeeds and yields ZERO names** (R8/C1-F4) | **51** |
| wrapper hides its syntax inside `(?#...)` (R8/C1-F3) | 1 |
| fabricate an `ESC('y', "\\y", ...)` row (R8/C1-F3) | 1 |
| revert the `=digits` magnitude rule (R8/C2-3) | 4 |
| revert the 128-byte name-length rule (R8/C2-4) | 20 (capped) |
| `case 'K': return 0x4b;` in `esc_char_value` — a real miscompile (R8/C1-F5) | 1 |
| **shape 9 loses its nested opener** (`[[%ca[%cb%c]%c]]` → `[[%ca%cb%c]%c]]`) (R9/C1-F1) | **2** |
| `posix_whole_class_only` always returns false (R9/C3-4) | 8 |
| libpcre2 contributes ZERO POSIX class names (R9/C1-2) | 10 |
| `if (c2 == '!') ctx_fail(...)`, a construct with no registry row (R9/C1-3) | 6 |
| delete `check_class_brackets()` from `main()` (R9/C1-7) | count guard + 3 manifest lines |
| rule 2 off at doorway 4a for `.`/`=` only (R9/C2-3) | 12 |
| revert the `open_msg` branch — the 4a over-promise (R9/C1-8) | 3 |
| remove the 4b nested-opener shape, WITH the 4a shapes present (R9) | 2 |
| neutralise both 4a nested-opener shapes (R9) | 2 |
| drop the `]` from the close check, a bare delimiter closes (R9/C2-6) | 12 |
| **restore the pre-Q2 `(?` catch-all** (RS_REJECTED -> `GROUP(REG_SEL_ANY, ..., modifiers)`) | **25** (+8 reject) |
| the doorway stops reading the option run (pre-MOD-0.5b: `if (0 && (r->flags & RF_OPTION_RUN))`; MOD-0.5b retired the flag — the equivalent edit today is `if (0 && r->recognise == pcrec_registry_option_run_recognise)` in ext.c) | 23 (+4 reject) — carried forward at the move, not re-measured; `make mech` re-confirms |
| bare `(?P` promises 'named-groups' again (the 5th over-promise) | 24 (+1 reject) |
| `(?P=` back to 'named-groups' (R8/C4-7's misattribution) | 1 (+1 reject) |
| `(?+N` back to 'modifiers' | 1 (+1 reject) |
| one Q2 completion replaced by a duplicate of another (probe COUNT unchanged) | 1 (the set checksum) |
| **longest-tail-wins -> first-tail-wins in `pcrec_registry_find`** | **3** (+1 reject) — see below |
| `k15_excluded()` neutered (`return 0`) (K15, 2026-08-12) | **21** (20 capped verb-differential mismatches + the exclusion's own liveness check, which fires on the same zero) |
| R20/OPTRUN-1: delete the truncation branch from `group_answer` so `(?P` at end of pattern goes back to "unrecognized character after (?P" | **0 in PC-3** — the residual above, honestly: the tail-sweep template cannot generate the zero-tail cell. Caught by `registry_check` (1, its `(?%c` sweep) and `tests/reject` (1, the hand pin) |
| R20: every truncated pattern in a tailed bucket drops its module promise (`avail > 0 && bucket_has_tail && no ')' in the pattern` → refuse) | **0 with the halves merged, 12 (capped) with them split** — the measurement that turned the first version of the truncated extension from vacuous into live; every failure names `[truncated]` and its byte |
| MOD-0.6 slice 4: drop `'L'` from `mod_uprops.c`'s hand-written `UPROPS_SHORT_NAMES` table (`"CLMNPSZ"` → `"CMNPSZ"`) | **20** (capped) — every failure names `\pL`/`\pl`/`\p{L}`/`\p{^L}` across all 5 positions and both cases; this is the failing-direction proof for `check_uprops_differential`'s 52-letter axis, measured then reverted before commit |
| MOD-0.8c slice 2: revert SPEC-1's fix — drop `\|\| a->not_repeatable` from `p_rep`'s error-109 test in `src/parse/parse.c`, so a quantifier after a bare option run binds the preceding atom again | **672 T1 cells** in the GATED pass (12 reported, capped) and **0 anywhere else in this file** — the whole point of the gated pass, since the closed gate refuses `a(?i)*` correctly. `registry_check` 0, `tests/cli` 0, `tests/reject` 11 (the hand pins landed with the fix). Measured on a scratch copy 2026-08-12, never committed |

**The tail-precedence sabotage found a real hole and is the one to read**
(historical since MOD-0.2 — the engine it sabotaged is deleted and
`check_tail_precedence` retired with committed successors, item 6 above —
but the lesson is the reason those successors exist in the shape they do). On
its first run it produced **ZERO failures repository-wide**: every tail in the
table is one byte except `\N`'s pair, and those two were written longest-first,
so taking the FIRST matching tail gave the same answer as taking the LONGEST and
row ORDER was silently standing in for the rule. Two changes make it observable
— the `\N` rows are now written SHORTEST first, so order disagrees with the
rule, and `check_tail_precedence` asserts it for every prefix-related pair and
FAILS if no such pair is left. R9's general lesson, met again: when a dangerous
operation is safe because of a fact that lives elsewhere, the assertion belongs
where the fact is.

**And the measurement instrument lied before the check did.** Two of these
sabotages were first recorded as "0 failures" because the battery counted
`grep -c "^FAIL"`, and PC-3's stdout buffer can flush mid-line, splicing a FAIL
onto the end of a PASS line (`PASS: ...it reaches theFAIL: (? byte
differential...`). `bad()`'s `fflush(stdout)` does not prevent it — the partial
flush has already happened when the buffer fills. Count `FAIL:` unanchored, and
run a no-sabotage control first: the control is what showed the instrument was
wrong rather than the guards.

Three are load-bearing beyond the others. The pre-Q1 sabotage was detectable by
NOTHING in this repo before this change — and it also fails `sweep_verb()` now,
which is why that sweep was rewritten rather than left to narrow silently. The
empty-external-pool sabotage is the one that measures whether "external" is
still true. And the `\K` miscompile is the one proving `check_rows` looks at
pcrec at all, which it did not until R8.

**The battery lied once, and the lesson is one level down from the usual.** The
first `\K` sabotage reported 0 failures — it inserted `return;` into a function
declared `noreturn`, so nothing was sabotaged. *Prove your instrument is live
before trusting a negative result* applies to the sabotage as much as to the
check.

The SKIP path is validated the same way: pointing `PCRE2_ABI_LIBS` at a
nonexistent SONAME produces three `SKIP:` lines and exit 0, with zero failures.

### What R8 changed about this file, and why it is worth reading before editing

Four of `pcre2_check.c`'s guards exist because the panel defeated their first
versions, all in the same way — **a control sharing a source with the thing it
controls**:

- the candidate pool is tagged with the SOURCE that produced each name, and
  every name pcrec claims must come from libpcre2's binary INDEPENDENTLY.
  Without that, neutering the external source left 84% of the probes running
  (from mutations of pcrec's own table), every liveness check green, and a
  deleted verb row invisible.
- a wrapper's syntax must be LOAD-BEARING where it sits, tested by substituting
  it for `\Y` and requiring the wrapper to stop compiling. "Contains the
  syntax" was satisfied by hiding it in a PCRE2 comment.
- `check_rows` runs pcrec as well as libpcre2. It used to run only libpcre2, so
  a row that had started miscompiling passed.
- the accept and default buckets require the diagnostic's SHAPE, not pcrec's
  own catch-all STRING, which had quietly made this file the authority on which
  module owns `(*atomic:a)`.

## Known limitation: ONE BYTE of lookahead is all any sweep here has

This was previously written as "the verb doorway is weaker than its three
neighbours". R5 measured it and the statement was wrong in both directions.

**The `(*` sweep is STRONGER than was documented.** The template is `(*%c)`, so
it does vary the first name byte, and a branch keyed on it IS caught — a critic
added `if (pat[at+2] == 'N') ctx_fail(... 'misc')` and `registry` failed. The
old sentence "a name-conditional branch added to parse.c would not be caught"
is too strong.

**The real gap is any branch keyed PAST the first byte, and it is not the verb
doorway's alone.** Both of these were invisible to all seven suites:

| sabotage | what it shows |
|---|---|
| branch on `(*NO_S…` (four bytes in) | verb names past their first letter are unswept |
| branch on `(?P=` vs `(?P<` | the `(?` doorway has the same hole |

Selector byte `P` carries two PCRE2 constructs — `(?P<name>...)` and
`(?P=name)` — and the sweep varies only the byte after `(?`. The same is true of
`(?<=` vs `(?<!` vs `(?<name>`, of `(?C1` vs `(?C{...}`, and of every verb name.
registry.c's header already names one instance (`\N{U+hhhh}` sharing the `N`
selector with bare `\N`) and calls it a known outstanding second home — it is
not one instance, it is **the shape of every doorway that is keyed by one byte
while PCRE2 keys by a string.**

**BOTH rows above are now closed.** `(*NO_S…` — a branch four bytes into a verb
name — is caught by `pcre2_check.c`, because names are compared whole against
libpcre2 over ~75,000 candidates. `(?P=` versus `(?P<` was the open half, and
SR-9's `tail` plus Q2's tail sweeps closed it: `(?P` has three recognised tails
and 252 that are error 141, and the sweep asserts pcrec agrees on all 255.

The general statement still stands and is worth keeping: **a sweep that varies
one byte cannot see a branch keyed past it.** What changed is that this doorway
now has a differential rather than only a sweep. `(?C1` versus `(?C{...}` is a
live remaining instance — `(?Ca)` is error 182, "unrecognized string delimiter
follows (?C", so the callout body has a grammar nothing here reads. It belongs
to whoever builds module `callouts`, and MOD-0's syntax port is where it goes.

Per-verb MODULES still arrive with SR-6 (`(*pla:...)` is a lookahead and will
not belong to module `verbs`); Q1 gave the names an existence and a form, not a
module. Until then: do not read "all four doorways swept" as "every construct
behind them is guarded".

Maintenance: update this file when files are added/removed or their roles
change. Re-run the sabotage battery if the check's structure changes — a
conformance test that cannot fail is worse than none, because it reads as
coverage.

## compliance_section.py (SR-4)

Connects the registry to `docs/pcre2_compliance.md`. Run from
`run_registry_tests.sh` after `registry_check`, so its two results are printed
*outside* the C harness's "checks passed: N" summary — the count in that line is
registry_check.c's alone.

- `--check` — the generated construct INDEX in the compliance doc must match
  `pcrec --list-syntax`. Regenerate with `--write` after adding a row.
  **[D65] the generated table's 16-column `COLS` list and rendered markdown
  table both carry a `built` column** since 2026-08-21 (`built`/`unbuilt`
  per RS_MODULE row, `—` for RS_BASE/RS_REJECTED) — see
  docs/design/registry_built_status_memo.md and this directory's own item
  10 above for what it answers and why it is derived rather than declared.
- `--names` — every ``module `X` `` named in the doc's hand-written prose must
  be a module the registry knows. This is the check that catches the realistic
  failure: a module renamed in registry.c leaves the prose confidently
  describing something that no longer exists, and nothing else would notice.

**[SR-11] GENERATOR AGREEMENT (2026-08-21, docs/spec/table_contract.md):**
`dump()` now cross-checks its own `COLS` list against `--list-syntax`'s LIVE
header line before parsing a single row — a column appended, renamed or
reordered in the dump without a matching `COLS` update fails immediately,
naming both lists. `COLS` is this script's own transcription of the dump's
column order (python cannot source tests/lib/table.sh, which implements the
identical rule for shell/awk consumers — comment-skip, "the last `#` line
before the first data row is the header" — so this re-implements it rather
than diverging from it); a transcription that stops matching its source is
the D65 failure shape one level up (a hardcoded field COUNT drifted silently
until an appended column broke two consumers — see this directory's item 10
and docs/design/registry_built_status_memo.md's Correction section).
Sabotage-validated: renaming `class_expect` to `class_expect_RENAMED` in a
scratch copy of `COLS` fails `--check` naming the exact mismatch between
`COLS` and the live header, rather than silently misreading every row past
that point.

The document is NOT rendered wholesale, which the SR-4 plan text asked for.
Doing that would replace a survey — DFA-feasibility judgements, the
`PLANNED`/`PLANNED-HARD` reasoning, the divergence post-mortems, and every row
about BASE syntax, which the registry deliberately does not describe — with an
inventory the registry can already print. So the inventory is generated between
markers and the analysis is left to humans.

Both checks are positive-controlled: renaming a module in the prose
(`quoting` → `quotingx`) fails `--names`; editing one status cell in the
generated index fails `--check`.

**`--check` is a DRIFT detector, not a control, and the difference matters.**
Its own failure message names the remedy — `--write` — which regenerates the doc
from whatever the table now says and turns the suite green. It catches "someone
changed the table and forgot the doc". It cannot catch "someone changed the
table on purpose and regenerated". An R5 critic demonstrated exactly that:
mis-assigning `(?0)`'s module fails `--check`, and one `--write` makes it pass.
The control for a wrong module name is the hand-written table in tests/reject/,
never this.

## `--check-annotations` / `--write-annotations` / `--tension` ([DOC-DRV])

The compliance page's THREE-COMPONENT restructure (2026-08-21, plan row
[DOC-DRV], carried by `.claude/skills/compliance-refresh/SKILL.md`): the
~90 rows' worth of hand-written measurement and judgment that used to sit
inline in each prose row's notes column now lives construct-KEYED in
`docs/pcre2_compliance_annotations.txt` (format in that file's own header)
and renders back into the page as one `<!-- BEGIN GENERATED ANNOTATIONS:
<slug> -->` block per section, immediately after that section's own
hand-written `syntax | status | becomes` survey table (which this
restructure leaves untouched — only the notes column moved).

- `--check-annotations` — two things, same shape `--check` already has for
  the construct index: (1) every annotation KEY names a LIVE construct — a
  plain key must equal a current `pcrec --list-syntax` `syntax` value, a
  `base:`-prefixed key must be in this script's own `BASE_KEYS` allowlist
  (typed independently of the store, so a rename in one place and not the
  other fails); (2) the page's 21 generated annotation blocks must match
  what the store renders. Also asserts no duplicate keys and no annotation
  naming a section this script doesn't know.
- `--write-annotations` — regenerates all 21 blocks in place from the
  store, the `--write` equivalent.
- `--tension` — the CHECKED-TENSION guard between component 1 (registry)
  and component 2 (survey), both directions, **informational by design
  (always exits 0)**: a registry `RS_MODULE` row whose `syntax` never
  appears as a literal backtick token in the hand-written survey prose,
  and a syntax-shaped backtick token (opens `\`, `(` or `[`) in the survey
  that names no registry row at all. Both directions carry real, EXPECTED
  noise and are reported rather than gated for it — the registry side
  because the survey often writes a generic placeholder (`(?n)` for the
  whole `(?0)`..`(?9)` recursion family, `...` bodies instead of a
  registry row's literal probe text) where a literal-token match would
  never fire; the survey side because base-tier notation (`\d`-shaped)
  is, by SR-4's own design, never registry-tracked at all. Measured at
  landing: 94 `RS_MODULE` rows, 60 without a literal survey token; ~120
  syntax-shaped survey tokens, most of them base-tier or placeholder
  notation.

**Two bugs found and fixed while building this, both worth knowing before
touching `splice`/`splice_annotations` again:**

1. `render_annotations_block` originally ended its return value with an
   explicit trailing `"\n"` after the `END` marker. `splice_annotations`'s
   untouched TAIL slice (the text starting right after the ORIGINAL `END`
   marker, carried through unchanged) begins with the newline that already
   terminates `END`'s own line — so the explicit trailing newline doubled
   it, growing the page by one blank line per section on every
   `--write-annotations` run. Fixed by dropping the trailing newline and
   letting the tail supply it, the same way `splice()` already relies on
   its own tail slice for the newline after the SR-4 marker.
2. Three PRE-EXISTING call sites (`splice()`, the `--names` mode's
   SR-4-block-stripping, and `--check`) called `text.index(END)` with no
   start offset — safe while `END`'s literal (`<!-- END GENERATED -->`)
   appeared exactly once in the file, and silently wrong the moment this
   restructure introduced 21 more occurrences of it (one per annotation
   block), all of which sit EARLIER in the file than the SR-4 marker they
   were meant to find. An unqualified `text.index(END)` after
   `text.index(BEGIN)` would find the wrong, earlier `END` and slice
   backwards. All three now search `text.index(END, begin_at)`, anchored
   to their own `BEGIN`'s offset. Caught by running `--check`/`--names`
   against the restructured page, not by inspection — both failed with an
   empty or nonsensical `doc:` comparison line before the fix.

Both are exercised by the checks above on every `make test` run now (a
regression in either would either grow the page unboundedly on the next
`--write-annotations`, or make `--check`/`--check-annotations` compare
against the wrong span), but neither has a DEDICATED regression test of
its own beyond that — noted here since neither bug would announce itself
loudly if partially reintroduced (e.g. one call site left unqualified).

## Two hand-written assertions that must not be tidied away (R5 N-1)

`check_table_to_parser` ends with two hand-written `expect_msg` calls for the
class-open entry to the collating rows, added because the doorway model does not
describe that position so nothing derives them.

After SR-2 they are **the only non-circular assertion about message TEXT left in
this file.** Every other message check now reads the expected string from the
row that the parser also renders from. An R5 critic predicted SR-2 had made the
documented "reword the collating message → 2 failures" sabotage stale, measured
it, and found those two calls still catch it.

If they are ever folded into the derived loop as a tidy-up, `registry` loses the
ability to see any message change at all and tests/reject/ becomes the sole
guard. That would look like a simplification. It is not one.
