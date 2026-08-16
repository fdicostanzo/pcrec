# tests/fuzz — PCRE2-oracle differential fuzzer

Random pattern/subject generator that differentially fuzzes `pcrec` against
a real PCRE2 8-bit oracle (dlopen'd at runtime — no `-dev` package on this
box). Plan step M2.5; promotes the R1 semantics critic's ad-hoc session
tooling into a committed, repeatable tool. Manual/checkpoint tool (`make
fuzz`), not part of `make test` — see README.md for why.

## Files

- **pcre2_abi.h** — the hand-declared slice of the PCRE2 8-bit ABI and its
  dlopen loader, shared. Extracted from pcre2_oracle.c by PC-3, when
  tests/registry/pcre2_check.c became a second consumer and would otherwise
  have copied it — two descriptions of somebody else's ABI is the shape of the
  `\v` bug this project already paid for. The loader returns a status instead
  of exiting, because the two consumers need opposite policies: the fuzz oracle
  must fail hard, and pcre2_check.c (inside `make test`) must skip loudly.
- **pcre2_oracle.c** — the PCRE2 8-bit CLI oracle, now built on pcre2_abi.h. `pcre2_oracle 'PATTERN'
  <subject-file> [startpos]` → `match S E` / `nomatch` / `cerr <code>` /
  `mlimit <code>` (PCRE2 match-limit safeguard tripped — not a verdict).
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
  Prints `match S E` / `nomatch` / `steps` (RX_ERR_STEPS) / `frames`
  (RX_ERR_FRAMES) — never `TIMEOUT`, that's fuzz.py's own subprocess-level
  sentinel for a hung child, distinct from a bounded-budget verdict.
  `tests/registry/pc4_driver.c` shares the identical shared-driver trick and
  had the identical latent bug, fixed the same session (README.md).
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
  fuzzer rather than a broken trap. Do not add a row for a bug that is still OPEN: traps run inside
  `make fuzz`, which must stay green, so deferred bugs belong in
  `tests/known_fail/` instead. Compiles every pattern with an explicit
  `--step-budget=STEP_BUDGET` (env-overridable, README.md "Step/frame budget
  policy") rather than the VM's bring-up 1,000,000 default, so a
  pathological pattern resolves to a fast, correctly bucketed
  `RX_ERR_STEPS`/`RX_ERR_FRAMES` verdict instead of a harness-clock
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
- **README.md** — full usage, exception-list rationale, output-bucket
  reference, triage process, and documented findings from this tool's
  build session (a real PCRE2 match-limit oracle bug now fixed, and a
  tracked PCRE2 optimizer quirk on `{0}`-quantified anchor alternations).
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

Maintenance: update this file and README.md when the generator's covered
feature set, the exclusion list, or the output-bucket classification changes.
