# 2026-09-30 r1 — [OPT-HYB-RESEED] critic panel: triage

Panel (D6), two read-only critics on lane/reseed (cee5ad81/8f6007b8):
- `2026-09-30-r1-hyb-reseed-sem.md` (rscrit1: engine semantics, answer soundness)
- `2026-09-30-r1-hyb-reseed-checks.md` (rscrit2: checks, claimed numbers)

Headline: answer-identity NOT refuted (~185 pattern × encoding runs, every startpos + find-all, 0 result/capture differences). One HIGH check break, and several overclaims. Every item goes to fix lane `reseedfix`.

| id | sev | finding | disposition |
|---|---|---|---|
| chk F1 | HIGH | +~569 B emitted per adaptive hybrid pushes run_size_term.sh's cap-rescue pin over 31,500 (K=2 not 4); the report's "codegen 125/0" was one script, not `make test-codegen` | FIX. First, SHRINK the emitted adaptive code (a shared or smaller emission; ~1,100 hybrids × 569 B is a real size cost). Then re-measure the cap on a rebuilt reference. Re-pin only by mechanism. |
| chk F2 | MED | "a single byte never qualifies for row 2" is false in a default build: the built-in byte-rate prior is always stamped | FIX the spec/design/report wording; add a check pinning the NONE-prior arm |
| chk F3 | MED | timing overclaims (×28 not in the table, max ×21.56; "every cell" false; ~4% noise floor makes ×1.02 null; the I-114 fresh-launch caveat was ignored) | FIX the claims; report as directional with the noise floor stated; the bench x86 ask settles it |
| chk F4 | MED | calibration unpinned (swapping frameless/framed goes undetected) and not reproducible (twins/driver only in /tmp) | FIX: commit the calibration harness (studies/ or tests/); add a check that detects a row swap |
| chk F5/F6 | LOW | S370's wording overstates its plant; 15 vs 13 checks; unbounded awk; no RX_VM_RESEED value-set check; stale registry.md §6 | FIX all |
| sem F1 | LOW-MED | clamped over-approx hybrids: a match can become PCREC_ERR_WORK near the budget (~1.1-1.25× work; witness `(?<=a|bc)[a-c]{2,4}d`, --work-budget=100000) | FIX: add the give-up qualifier to match_api's abi paragraph. MEASURE whether clamped hybrids gain enough to justify the adaptive row (deviation 4); if not, exclude them by row |
| sem F10 | note | a future `callouts` module on hybrids must decline re-seed, as it declines the entry prefilter | one line in design §6 |
| sem table | note | the dense start state (steps_left=cap, short_gaps=2) lives in emitter code, not row columns | FIX: move it into the rows |
| sem gaps | note | two witnesses exercised only the no-match path; no subject >100 KB was run | cover in the fix lane's differential |
