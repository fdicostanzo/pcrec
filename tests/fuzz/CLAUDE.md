# tests/fuzz — PCRE2-oracle differential fuzzer

Random pattern/subject generator that differentially fuzzes `pcrec` against
a real PCRE2 8-bit oracle (dlopen'd at runtime — no `-dev` package on this
box). Plan step M2.5; promotes the R1 semantics critic's ad-hoc session
tooling into a committed, repeatable tool. Manual/checkpoint tool (`make
fuzz`), not part of `make test` — see README.md for why.

## Files

- **pcre2_oracle.c** — hand-declared PCRE2 8-bit ABI CLI oracle (see its
  header comment for the dlopen rationale). `pcre2_oracle 'PATTERN'
  <subject-file> [startpos]` → `match S E` / `nomatch` / `cerr <code>` /
  `mlimit <code>` (PCRE2 match-limit safeguard tripped — not a verdict).
- **fuzz_driver.c** — subject-from-file driver template for pcrec-generated
  matchers, owned by this fuzzer (not a reuse of tests/harness/driver.c).
- **fuzz.py** — generator + comparator + runner:
  `python3 tests/fuzz/fuzz.py [--seed N] [--patterns 300] [--subjects 15]
  [--keep] [--jobs N]`. Deterministic per `--seed`. See its module
  docstring and `EXCLUDED FROM GENERATION` block for what's not generated
  and why.
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
