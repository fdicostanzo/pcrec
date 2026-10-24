# iterdoc report — find-all iterator spec fixes from the D27 adversary (2026-10-22, sonnet)

Input: iterd27_report.md (F1-F6, D1-D5). Spec-only: docs/spec/match_api.md. No code, no abi.
Premise test: repro F1 against this branch's build gives pcrec `(0,1) (2,3)`, libpcre2 `(0,1)`.

Added/changed (match_api.md): §3.1.3¶4a (F1, restart rule), ¶6 qualified (F5), ¶11a (F1, `\G`);
§3.8¶2a (exceptions to "PCRE2's global iteration"; D5 CRLF, plan row DD-11, no promise), ¶5a (D2: bit
0x80 reserved and ignored; code mask is 0xF0 on purpose), ¶6a (D4: vars check, after guard and UTF
check, first search), ¶9 (D1); §3.8.2¶5 and §4¶9a (D3: ncaps == 0, now four causes); §9.3¶4 (F2);
§9.5¶2 (F5), ¶3 (F6, K74).

Measured: after a refused setter on a BOUND iterator, `lo` is unchanged (next search start; 2 after one
match of `a` over `aaaa` from 1), rc == PCREC_ERR_ITER.
F6: `$ \z \Z (?m)$` over `e3 81` and `c3 a9 80 c3` reproduce (pcrec reports (n,n), libpcre2 nothing).
`\B` and `(?<!.)` agreed with libpcre2 on the three subjects I tried (e3 81, 61 80 61, c3 a9 80 c3);
the adversary's witnesses for them were `61 e3 81` and `61 f0 9f 98`, not re-run. K74's own entry names
only `$` and `\B`: the manager may want it widened (not done: dev doc, out of scope).
Code-defect notes: none new. D4's wording assumes F3 (corefix) lands: unset var refused at the first
search whatever the subject holds.

Validation: `make test-spec-history` 159 + 11 checks, 0 failed; scripts/spec_toc.py run (no heading change).
