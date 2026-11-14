# vocfix report

## STATE
Done, committed on lane/vocfix.

## CAUSE
C4 class 3 (intrinsic) regex `v[a-z][a-z0-9]*q?(?:_[a-z]+)?_[sufp](?:8|16|32|64)` (tests/memfn/arch_blind_check.py) is case-insensitive and matched the Python name `VRUN_U8` (looks like a NEON `vXXX_u8`): 8 hits in tests/axes/memfn_arm.py.

## FIX
Renamed VRUN_U8 -> RUNW_U8 (and VRUN_U8_PAD) in tests/axes/memfn_arm.py. Check and allowlist untouched. Older reports keep the old name (not scanned).

## VALIDATION
`bash tests/memfn/run_arch_blind.sh <worktree>`: checks passed 17, failed 0.
