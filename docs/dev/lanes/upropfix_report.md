# upropfix report

## STATE AT HANDOFF
Red run 43112766175 (sha 10a1a64b3) had ONE distinct red, shard 5: test-codegen
`[agreement] the empty-engine bucket differs from its named manifest` (130 new patterns).
- Cause: the D27 \p corpus patterns compile under the byte encoding, where their property set has no member < 256.
- Class: correct never-match; manifest drift (a diff reviewed per row).
- Verified: 70 Age/Block patterns against UCD 16.0.0 (DerivedAge.txt: Age=1.1 holds all 256 bytes so every other Age,
  Age=Unassigned and [^\p{Age=1.1}] are empty; Blocks.txt: only Basic Latin/Latin-1 have members < 256); the other 60 against
  libpcre2 10.46 non-UTF over all 256 bytes (zero hits). Installed libpcre2 10.46 rejects Age=/Block= (error 147), so UCD is their oracle.
- Fix: the 130 patterns appended to EMPTY_MANIFEST in tests/codegen/run_dfa_stamps.sh with a [UPROP-D27] comment.
- Local verdict: `bash tests/codegen/run_dfa_stamps.sh` in the worktree: 41 passed, 0 failed (bucket 235, non-vacuous).
- pcrec bugs found: none.
- Axes run 43112859523 (cloud/main/axes/upropprom) was still in progress at start; not included.
- OWED: cloud test + axes runs queued via scripts/cloudrun (names upropfix).
