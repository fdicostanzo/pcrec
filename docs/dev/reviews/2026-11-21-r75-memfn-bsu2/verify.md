# verify.md (r75 memfn-bsu2): inline verification by the coordinator (each item a one-call repro or a quote), 2026-11-21 ~14:05-14:08

## CONTRACT-1: HOLDS
`R/kit/pc base|subj DIR -p rxa --window-search-width=4095 --pattern "$(cat R/contract/cap_witness.txt)"`: BASE rc=0 (499743 bytes of code);
SUBJECT default rc=1 "pattern too large: 500060 bytes of emitted code (limit 500000)"; SUBJECT --memfn=no-span-vector rc=0 (499743).

## SLOT-1: HOLDS
trace-subj `[0-9a-f]{32}`: `MFTRACE END table=wfS art=1 site=1 phase=define at=0 k=31 chosen=T-vwin would_decline=0 fields=-`;
tests/memfn/reach_equal.py:73's END regex: NO MATCH.

## SLOT-2: PARTLY (the silent-typo half HOLDS; "which check reds" not run: suites are out of scope)
Plant R/plants/V1 (finder.c fd_named_id `"R7w"` -> `"R7W"`, built from SUBJECT): compiles, no mf_art_begin refusal; `[0-9]{25}` and
`\d{32}` emit no `_vs0` (T-vscan dead, silently); `[0-9a-f]{32}` keeps V (T-vwin). Only DIFFER-floor pins (opt-in make test-axes) could see it.

## CENSUS-1: HOLDS (gcc -O2, GNU diff, §2.1 normalizer): `[aeiou]{20}` 38 lines; `\w{20}` 20; bench `[0-9a-f]{32}` 0, `\d{32}` 0.
## CENSUS-3: HOLDS (clang -O2): `\d{32}` default vs deny, normalized, GNU diff: 264 lines.

## CHECKS-1: HOLDS
`span_vector_identity.py --ref-bin R/base/build/pcrec --bin R/checks/plants/deadv --root W --jobs 2 --cells seed4095` (deadv = the
SUBJECT with --memfn=no-span-vector forced): both cells `default_movers=0`, `compiled=82 failures=0 PASS` rc 0.
## CHECKS-2: HOLDS
Same with `--bin R/checks/plants/vsite_extra` (respaces `#include <string.h>` and doubles the V call, V artifacts only): movers 31, PASS rc 0.
## CHECKS-3: HOLDS by reading: span_vector_identity.py:163-166 fails only on `total == 0`; no per-cell population test.
## CHECKS-6: HOLDS by grep: span_vector_identity is read by no Makefile/target (tests/memfn/CLAUDE.md:74 "opt-in, heavy").

Not separately re-run (critic repro accepted, same mechanism as a verified item): CHECKS-4 (mask copy plant), CHECKS-5 (held on sample),
CENSUS-2/-4/-5 (measurements in R/census/res_*.tsv), CONTRACT-2/-3 (quotes of options.def / registry.md / tuning.md).
VERIFY COMPLETE
