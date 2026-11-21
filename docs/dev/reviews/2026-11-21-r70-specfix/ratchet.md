# CRITIC RATCHET (sonnet): specfix r70

## Findings

### RATCHET-1  CONFIRMED  severity: maintenance
small / check10_quantifiable.c (`if (is_yes != row_q[i] && known_finding(S))`) and known_findings.inc
The ratchet keys on the syntax string only; it pins neither pcrec's value nor libpcre2's verdict. The .inc header says each row is "`quantifiable=no`" but nothing enforces it: any disagreement for a listed row (either direction) is swallowed and counts as a hit.
repro: plant p_flip (copy of the suite; registry dump edited so `\A` is `yes`, libpcre2 says `a\A*` does not compile; `\A` added to the .inc): check10 PASSES (rc 0). Same registry without the entry: RED. So a listed row cannot detect a wrong-way change of its cell. Fix: make entries (syntax, pcrec value, oracle verdict) triples, requiring val == listed && oracle == listed. Suppression covers only the one comparison (D1/D2 and unknown-value paths run before it and still fire: q_form/q_lexical/q_garbage plants all RED), so only the value flip is open.

### RATCHET-2  CONFIRMED  severity: doc
trivial / check10_quantifiable.c (last printf block)
"KNOWN FINDINGS ... N, all still disagreeing" prints unconditionally after the stale loop, so it appears even right after a stale entry was failed (plants stale/nosyn/dup: line says 14, "all still disagreeing", beside FAIL). The verdict is unaffected (rc 1, FAIL line present) but the sentence is false at that moment. Fix: print only if no entry was stale, or print "N listed, M still disagreeing".

### RATCHET-3  SUSPECTED  severity: maintenance
small / Makefile test-spec (`.ran` touched before the run) + run_spec_mod0.sh SKIP path
The SKIP exits 0 with only stderr `SKIP:` lines; the section's `.ran` marker was already touched by the recipe's first line, so test_trailer.sh reports `sections ran: N/N` and nothing marks that this section decided nothing. A box with neither pkg-config libpcre2-8 nor a linkable -lpcre2-8 gets a green `make test` with the D27 suite unrun, visible only in scrollback. It is PC-3's accepted pattern (parity, not regression); CI is not affected today (pinned 10.46 built in the runner, ci.yml:14) but nothing in CI asserts resolution, so image drift would turn the section into a silent no-op. Mitigation if wanted: CI-only require-pcre2 env making the SKIP exit 1, or the trailer listing skipped sections.

### RATCHET-4  CONFIRMED  severity: doc
trivial / Makefile comment above the section targets (~l.601-606); tests/ci/cloud_test_shards.tsv header
"Each target rebuilds `all` first (bar test-spec, which treats build/pcrec as a black box ...)" is now only half true: `test-spec: all` is unchanged and the new comment says "does not rebuild beyond `all`". Reword. The shard-table header `predicted_shard_s` / `sections_total` lines were not regenerated for the new row (only the unmeasured line was); shard 17 sums to 544.5s, under the 600s target, so no capacity effect.

## PROBED-AND-HELD

Plants on copies of tests/spec_mod0, check10 compiled and run against the subject registry (about 20 runs; baseline PASS: 13 known, 128 compared). RED naming the row: delete entry `\5`; invented agreeing row `(?:a)` (stale); syntax not in registry `NOSUCH` (stale); duplicate entry `\1` (second copy never hit, stale); empty .inc (13 disagreements; compiles clean with zero-size arrays); known row set to yes / form / lexical / garbage in the registry (stale, plus the D2/lexical/form/unknown message); known row removed from registry (stale); quantifiable column removed (AWAITING rc 3; run_spec_mod0.sh makes a plain run exit 1 on any awaiting check). SAME (silent): value flip on a listed row (RATCHET-1). A known entry is consumed only by the yes/no comparison path when is_yes != oracle verdict; form/lexical/D1/D2 paths never set known_hit, so a row moving to them goes red as stale. check_shards.sh run directly on the subject's TEST_SECTIONS: "87 sections in exactly one of 18 shards", rc 0; test-spec is in shard 17 (with test-alloc), so CI runs it. Docs: no remaining "not part of make test" claim about spec_mod0 outside lane/review/journal files. Minimum witness: single-row plants.

Standing questions. Sibling: known_findings.inc IS the sibling of endpoint_deviations.inc / class_expectations.inc in the same dir (same both-directions .inc pin, same stale-fails contract); it is not a candidate for tests/known_fail/ (that ratchet is for .rxt corpus patterns with a deferred-bug marker, a different object: registry cells vs corpus blocks). General form: one declared table of (syntax, pcrec value, oracle verdict, owner row tag) per spec check, consumed by one helper with stale/duplicate/unknown handling; it closes RATCHET-1 and gives check03/04/08/11-14 the same ratchet. Trigger: a third spec check wanting its own known-list, or the K153 data lane touching the file.
CRITIC COMPLETE
