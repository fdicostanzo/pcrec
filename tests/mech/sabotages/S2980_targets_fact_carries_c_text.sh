#!/usr/bin/env bash
# S2980 -- [XARCH-DEV] unit K0 (request R-36; lane k0). A FACTS ROW CARRIES AN EMITTER'S SPELLING.
#
# Plant: memfn/src/targets.def's last target row (a facts row) has its feature token replaced by the C
# preprocessor macro a C emitter would test for it: C text in a fact, which the owner's ruling of
# 2026-11-07 keeps apart (facts are read alike by a C or a Rust emitter; spellings live in targets_c.def
# and targets.c's C section). The row's family is not the host's, so the compiler control skips it.
# Detector: memfn/tests/check_targets.sh (part 1 of tests/memfn/run_targets.sh, arm memfntargets): every
# facts field must be a token list, and a macro name is not one; part 2's literal row agrees.
SAB_ID="S2980-targets-fact-carries-c-text"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='a facts row carries C text (a preprocessor macro name) in place of a feature token'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2980.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='MF_NO_NEEDS, "neon",'
SAB_AFTER='MF_NO_NEEDS, "__ARM_NEON",'
