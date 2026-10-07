# k94tri report -- triage + landing of lane/k94fix (2026-10-07)

Source log: k94's Mac `make test` (maketest.log), red on four sections. Main merged into lane/k94fix first
(clean, no conflicts; main already carried rxspin's rxtsource re-pin). All fixes are pcrec-side
declarations; nothing under memfn/ was edited.

| section | failing check | cause | class | fix | rc after |
|---|---|---|---|---|---|
| test-rxtsource | census/file list/C1/case-row/C3/W23-S7 (10 fails) | new tests/backrefs/caseless_ucp.rxt: +1 file, +10 blocks, +175 case lines, all libpcre2-only answers (C3 pass count unchanged at 16253) | STALE PIN (lane's) | CENSUS 275/5321/50915, RUNSH 251/5321/50915, C3_SKIP +175 (33594), C3_SKIP_PCRE2ONLY +175 (16518) in tests/rxtsource/run_rxtsource_tests.sh | 0 (278 pass) |
| test-startset | [vm-movers] auto + vm: 8 movers not in manifest | caseless_ucp.rxt: 8 VM-hybrid mover blocks. After the merge also composition_d27.rxt (main's rxspin landed without startset manifests): +104 auto / +416 forced / +11 dfa rows | STALE PIN (lane's 8) + PRE-EXISTING ON MAIN (composition_d27 rows) | regenerated with docs/design/startset/s1/census_s1.py on the merged build into scratch; diff was pure additions (auto +112, forced +424, dfa +11, no row moved, bench rows identical); adopted rows, header notes appended | 0 (both vm-movers and dfa-movers 0 off-diagonal) |
| test-memfn-manifest | rule 1 (static half): enc_byte.c:304 defs_bref_ci_ucp spells a span-index form, no pending row names it | new emitter defs_bref_ci_ucp is a copy of defs_bref_ci's span compare, the same N7 pending form | pcrec-side declaration the lane missed (not a new kit site, not kit-owned; D147 addendum 10 row N7 already covers byte seam bref compares) | added defs_bref_ci_ucp to the N7 row of tests/memfn/site_manifest.tsv | 0 |
| test-memfn-forms | C12: enc_byte.c span-index 3 forms, ceiling 2 | same form, third spelling | same | tests/memfn/c12_ceilings.tsv enc_byte.c span-index ceiling 2 -> 3 (first attempt dropped the `-` column; fixed in a follow-up commit) | 0 |

Note: the N7 pending row and the ceiling are RATCHETS for the forms N7 will replace; the new emitter will move
with defs_bref_ci when N7 lands (it is a third copy, not a new mechanism).

Validation (each alone, on the merged tree, gcc-16, Mac): make strict rc=0; test-rxtsource 0; test-memfn-manifest 0;
test-memfn-forms 0; test-startset 0; test-backrefs 0. The mac suite lock was held by stc2; sections run one at a time.
Not run: full make test, mech (S590/S591 were k94fix's own).
