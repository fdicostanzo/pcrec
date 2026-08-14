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
- **fuzz.py** — generator + comparator + runner:
  `python3 tests/fuzz/fuzz.py [--seed N] [--patterns 300] [--subjects 15]
  [--keep] [--jobs N]`. Deterministic per `--seed`. See its module
  docstring and `EXCLUDED FROM GENERATION` block for what's not generated
  and why. Beside the general grammar it carries `TRAP_TEMPLATES` (~8% of
  generated patterns), shape-focused rows for preference bugs the unbiased
  generator CAN produce but essentially never rolls. Two classes today: R2's
  overlapping-prefix alternation under a lazy quantifier (R2-M1/R2-S1), and
  R21/K17's outer star over a lazy nullable prefix plus a nested nullable
  quantified group — the latter measured to move its class from ~1e-4 of
  patterns to 4%. **Add a row whenever a preference bug is found by something
  other than this fuzzer**; that is what the block is for. Check each
  addition in the FAILING direction (the K17 rows expand to 111 distinct
  patterns giving 28 divergences against the pre-fix compiler and 0 against
  the fixed one) — a trap that never fired against the bug it names is
  decoration. Do not add a row for a bug that is still OPEN: traps run inside
  `make fuzz`, which must stay green, so deferred bugs belong in
  `tests/known_fail/` instead.
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
status). A divergence always gets a bundle under `failures/`; triage by
reproducing independently of the fuzzer and minimizing before concluding
it's a real engine bug (see README.md's "Triaging a divergence").

Maintenance: update this file and README.md when the generator's covered
feature set, the exclusion list, or the output-bucket classification changes.
