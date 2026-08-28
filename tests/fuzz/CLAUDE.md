# tests/fuzz — PCRE2-oracle differential fuzzer

Random pattern/subject generator that differentially fuzzes `pcrec` against
a real PCRE2 8-bit oracle (dlopen'd at runtime — no `-dev` package on this
box). Plan step M2.5; promotes the R1 semantics critic's ad-hoc session
tooling into a committed, repeatable tool. The many-seed, many-pattern
CAMPAIGN stays manual/checkpoint-only (`make fuzz`, `campaigns/`) — see
README.md for why. **[M4.7e]** added a FIXED-seed slice that IS wired into
`make test` (`make test-capturediff`, `run_capturediff_gate.sh`) — a
pinned seed is exactly as reproducible as any other differential in this
tree, which is what the manual-only reasoning below does not cover.

## Files

- **pcre2_abi.h** — the hand-declared slice of the PCRE2 8-bit ABI and its
  dlopen loader, shared. Extracted from pcre2_oracle.c by PC-3, when
  tests/registry/pcre2_check.c became a second consumer and would otherwise
  have copied it — two descriptions of somebody else's ABI is the shape of the
  `\v` bug this project already paid for. The loader returns a status instead
  of exiting, because the two consumers need opposite policies: the fuzz oracle
  must fail hard, and pcre2_check.c (inside `make test`) must skip loudly.
  **[M4.7d]** added `pcre2_pattern_info_8` and `pcre2_get_ovector_count_8` to
  the resolved symbol set, plus `PCRE2_ABI_INFO_CAPTURECOUNT` (opcode `4`,
  MEASURED — dlopen'd libpcre2 has no header here to read the constant off
  of, so this project's standing discipline is to probe it: three patterns
  with distinct group counts, one candidate opcode consistent with all
  three; see the macro's own comment for the transcript). Both new symbols
  are REQUIRED by `pcre2_abi_load()` now, same as every existing one — a box
  whose libpcre2-8 lacks them fails the fuzz oracle hard (unchanged policy)
  and makes `pcre2_check.c` skip louder (unchanged policy, wider trigger);
  not expected on any box with a stock `libpcre2-8-0` package, confirmed
  present on this one.
- **pcre2_oracle.c** — the PCRE2 8-bit CLI oracle, now built on pcre2_abi.h. `pcre2_oracle 'PATTERN'
  <subject-file> [startpos]` → `match S0 E0 [S1 E1 ...]` / `nomatch` /
  `cerr <code>` / `mlimit <code>` (PCRE2 match-limit safeguard tripped — not
  a verdict) / `ovtoosmall <code>` (defensive-only, not expected to fire —
  see below). **[M4.7d]**: the `match` line now carries EVERY capture-group
  span (index 0 the whole match, index `k` group `k`), not just the whole
  match — the ovector is sized to `capturecount + 1` pairs, queried fresh
  per pattern via `pcre2_pattern_info_8` right after compile, which is also
  what makes a never-participated group read back `(-1, -1)` in both
  offsets rather than undefined memory (PCRE2_UNSET, all bits set — cast to
  a signed type of the same width this IS the literal `-1`, bit-for-bit
  pcrec's own `PCREC_UNSET`, so no numeric remapping exists anywhere in this
  file — see tests/fuzz/README.md's "Capture-group span comparison" for the
  measurement transcript this rests on).
- **fuzz_driver.c** — subject-from-file driver template for pcrec-generated
  matchers, owned by this fuzzer (not a reuse of tests/harness/driver.c).
  Compiled ONCE against a throwaway pattern and reused for every subsequent
  pattern's gen.o (fuzz.py's dominant per-pattern cost saver — see
  README.md "Performance"), which is only safe because this file reads
  `rx_info.ncaps` at RUNTIME rather than the compile-time `RX_NCAPS` macro
  (that macro is baked in from the THROWAWAY pattern, wrong for any other
  pattern's own group count — see this file's own header comment and
  README.md's "RX_NCAPS is NOT part of what's shared" section for the
  274/317-divergence stack-smash this caused before the fix, this session).
  Prints `match S0 E0 [S1 E1 ...]` (**[M4.7d]**: every `caps[k]` pair, `k` in
  `[0, rx_info.ncaps)` — was whole-match-only before) / `nomatch` / `steps`
  (PCREC_ERR_STEPS) / `frames` (PCREC_ERR_FRAMES) — never `TIMEOUT`, that's
  fuzz.py's own subprocess-level sentinel for a hung child, distinct from a
  bounded-budget verdict. `tests/registry/pc4_driver.c` shares the identical
  shared-driver trick and had the identical latent bug, fixed the same
  session (README.md) — its own output stays whole-match-only, since PC-3's
  pattern space carries no capturing constructs (see its own file comment).
- **fuzz.py** — generator + comparator + runner:
  `python3 tests/fuzz/fuzz.py [--seed N] [--patterns 300] [--subjects 15]
  [--keep] [--jobs N]`. Deterministic per `--seed`. See its module
  docstring and `EXCLUDED FROM GENERATION` block for what's not generated
  and why. Beside the general grammar it carries `TRAP_TEMPLATES` (~8% of
  generated patterns), shape-focused rows for preference bugs the unbiased
  generator CAN produce but essentially never rolls. Three classes today:
  R2's overlapping-prefix alternation under a lazy quantifier (R2-M1/R2-S1),
  R21/K17's outer star over a lazy nullable prefix plus a nested nullable
  quantified group — the latter measured to move its class from ~1e-4 of
  patterns to 4% — and K18's sibling family (fixed 2026-08-15), where the
  redirect is lost one hop SHORT of a loop entry rather than at one. The K18
  rows pin BOTH alternation orders on purpose: the ingredient is that the arm
  whose exit edge lands on the already-seen state is the PREFERRED one, not
  that it is lazy, and a greedy nullable arm gets that by being written first
  — two of the K18 entry's own "does not diverge" controls were live
  miscompiles with their arms swapped. Two rows carry a `{0,2}` body, which is
  a separately-reachable sub-case a corpus built from the original witness
  cannot produce at all. **Add a row whenever a preference bug is found by
  something other than this fuzzer**; that is what the block is for. Check
  each addition in the FAILING direction (the K17 rows expand to 111 distinct
  patterns giving 28 divergences against the pre-fix compiler and 0 against
  the fixed one; the nine K18 rows expand to 64 distinct patterns giving 56
  divergences over 543 cells against the pre-K18 compiler and 0 against the
  fixed one) — a trap that never fired against the bug it names is
  decoration. A template is `.format`ted with `{a}/{b}/{q}`, so a literal
  brace in a row must be DOUBLED (`{{0,2}}`); an unescaped one raises
  `KeyError` inside `gen_trap` on the draw that picks it, which is a broken
  fuzzer rather than a broken trap. **[M4.7d]** added the sibling
  `CAPTURE_TEMPLATES`/`gen_capture()` (same `.format()` mechanism, same
  brace-doubling rule), drawn at ~20% density in `main()`'s pattern loop
  (mutually exclusive with the ~8% trap lane) specifically to make the
  quantified-group / group-around-alternation / nested-group combinations
  routine rather than incidental — the unbiased grammar produces SOME
  capturing group often (`gen_atom`'s own ~14%-per-draw rate) but rarely
  lands a quantifier directly around one or a group directly inside another
  quantified group in the same draw. This lane's subjects run up to 8 bytes
  (the trap lane's run up to 4) because capture-span bugs (cross-iteration
  retention, empty-final-iteration overwrite) need multiple loop iterations
  to surface at all. Do not add a row for a bug that is still OPEN: traps run inside
  `make fuzz`, which must stay green, so deferred bugs belong in
  `tests/known_fail/` instead. Compiles every pattern with an explicit
  `--step-budget=STEP_BUDGET` (env-overridable, README.md "Step/frame budget
  policy") rather than the VM's bring-up 1,000,000 default, so a
  pathological pattern resolves to a fast, correctly bucketed
  `PCREC_ERR_STEPS`/`PCREC_ERR_FRAMES` verdict instead of a harness-clock
  collision. Every subprocess call this file makes (pcrec compile, gcc
  compile/link, the generated matcher, the PCRE2 oracle) now catches its own
  `TimeoutExpired` and reports a classified cell rather than raising — the
  oracle side (`oracle_run()`) and the pcrec-compile side
  (`compile_with_pcrec()`) were the two found missing this discipline this
  session (both crashed a multi-thousand-pattern run outright before the
  fix; `compile_and_link()`'s GCC-TIMEOUT handling was always correct and is
  the pattern the fix generalizes). `RUN_TIMEOUT` (the generated-matcher and
  oracle execution bound, `pcrec_run()`/`oracle_run()`) now reads
  `tests/lib/gen_timeout.sh runsecs` the same way `tests/vm/vm_oracle.py`'s
  `RUN_TIMEOUT` does — one shared number rather than this file's own
  literal — via `subprocess.run(..., timeout=RUN_TIMEOUT)` rather than a
  per-run `scripts/watchdog` wrapper, since this is a thousands-of-cells
  inner loop where watchdog's fixed per-run startup cost would multiply the
  campaign's runtime. GENERATED-code compiles (the gen.c compile and its
  link) additionally carry the D45-third-addendum CPU-primary budget via
  the `_cpu_limited` ulimit shim reading `gen_timeout.sh cpusecs`; the
  oracle-shim and driver-template compiles are hand-written C, outside
  D45's scope, and deliberately stay on the wall bound alone.
  **[M4.7e] second addendum** added `MODULE_CLASS_ATOMS` next to
  `CLASS_ATOMS` — the classes-module escapes (`\d \D \w \W \s \S`) and two
  POSIX `[:name:]` forms (`[[:alpha:]] [[:digit:]]`), drawn at a modest,
  NAMED weight (`MODULE_CLASS_WEIGHT = 0.15` of the existing class-atom
  branch in `gen_atom`, not merged into `CLASS_ATOMS` itself) — closing the
  README.md-documented finding that the differential gate was open
  (`PCREC_DEFAULT_FEATURES="std1"`) but the generator never actually
  emitted anything std1's two modules own. `modifiers` generation stays
  out of scope, owed to [M7.0] (docs/dev/plan.md) rather than added here.
- **README.md** — full usage, exception-list rationale, output-bucket
  reference, triage process, and documented findings from this tool's
  build session (a real PCRE2 match-limit oracle bug now fixed, and a
  tracked PCRE2 optimizer quirk on `{0}`-quantified anchor alternations).
- **run_capturediff_gate.sh** — **[M4.7e]** the GATE-ON wiring: runs
  `fuzz.py` at ONE FIXED seed/patterns/subjects (its own argparse
  defaults, spelled out in the script so a future default change there
  doesn't silently resize this gate), asserts fuzz.py's own zero-divergence
  exit code, and additionally asserts every exclusion-bucket LABEL fuzz.py's
  summary prints is still present in the output (no-silent-caps: a bucket
  vanishing from the summary text, not just its count going to zero, is
  itself a regression this gate catches). Probes libpcre2 presence itself
  BEFORE calling fuzz.py (build `pcre2_oracle.c`, call its own `--version`,
  which does the real dlopen attempt) and SKIPS loudly (PC-3's own pattern,
  tests/registry/run_registry_tests.sh) rather than calling into fuzz.py's
  oracle plumbing, which is deliberately fail-hard (see pcre2_abi.h's entry
  above) — right for a manual dev tool, wrong for a `make test` section on a
  libpcre2-less box. `make test-capturediff` is its Makefile target, part of
  `make test` proper (unlike `test-spec`).
- **campaigns/** — **[M4.7e]** committed logs from the AT-SCALE, many-seed
  capture differential campaign (D35-style provenance: date, HEAD commit,
  libpcre2 version, seed list). Evidence, like docs/measurements/ reports —
  no check reads these; `make test-capturediff` above is the live,
  re-measured regression gate. Re-run manually (`python3 tests/fuzz/fuzz.py
  --seed N ...` per seed, or the driver loop recorded in the campaign log
  itself) rather than from a make target, same manual-only posture as
  `make fuzz`.
- **failures/\<timestamp\>/NNNN_\<kind\>/** — repro bundles (pattern.txt,
  subject.hex/.bin, outputs.txt) written by runs that found divergences.
  Regenerated output, not committed fixtures — safe to delete.

## Conventions

Exit code 0 iff zero accept/reject and zero content divergences (the DFA
state-cap bucket — review finding A-3, a known unimplemented-VM-fallback
limitation — and oracle-inconclusive `mlimit` count never affect exit
status; nor do the harness-level buckets added this session: pcrec compile
timeout, oracle probe timeout, and pcrec step/frame-budget exhaustion —
see README.md's "Step/frame budget policy"). A divergence always gets a
bundle under `failures/`; triage by reproducing independently of the
fuzzer and minimizing before concluding it's a real engine bug (see
README.md's "Triaging a divergence").

**[SEL-1] (2026-08-28, K40) NARROWED WHAT THE "DFA state-cap" BUCKET CAN
STILL CATCH.** It counts a pcrec compile stderr containing "too complex for
the DFA engine" (the two DFA-side caps in `src/core/limits.h`, state count
and K7's subset-element budget) OR "NFA exceeds" (`PCREC_MAX_NFA_STATES`,
which has no fallback engine and is UNCHANGED by [SEL-1]). Under
`--engine=auto` — `compile_with_pcrec()`'s only mode — the first half is now
a SELECTION OUTCOME rather than a refusal (`docs/spec/tuning.md` §2.11): a
pattern that used to land in this bucket for that reason now compiles as a
VM fallback and lands in the ordinary accept/compare pipeline instead. The
bucket did not stop being meaningful; its population just moved, and moved
ENTIRELY on this fixed seed's own draw (8 -> 0 at seed 1/patterns 300,
`run_capturediff_gate.sh`'s own re-pin). **A NEW, related bucket exists only
in `run_capturediff_gate.sh`, not in fuzz.py's own summary**: some of those
newly-VM-compiled patterns are large enough that `gcc` itself (compiling the
emitted C at fuzz.py's own `-O0` default, under D45's fixed CPU-second
budget) can hit ITS OWN resource limit — `docs/dev/known_issues.md` K41,
"CPU time limit exceeded" / "internal compiler error" — which is neither a
pcrec correctness defect nor the pre-existing "gcc compile fails" class this
Convention paragraph already excludes from exit status; see the gate
script's own header comment for the classification and why it lives there
rather than in fuzz.py.

Maintenance: update this file and README.md when the generator's covered
feature set, the exclusion list, or the output-bucket classification changes.
