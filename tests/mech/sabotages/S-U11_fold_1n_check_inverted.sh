# S-U11 ([M5.0] stage 1 by design, LANDED at stage 4; utf8_design.md §4.1.1,
# §8.2, ASK 3 RULED) -- THE STANDING 1:n FOLD CHECK IS LIVE.
#
# THE ODD ROW IN THIS TABLE, AND DELIBERATELY SO. Every other row sabotages
# the COMPILER and asks whether a check notices. This one sabotages A CHECK'S
# OWN EXPECTATION and asks whether the MATRIX notices -- because the fact it
# defends is a fact about libpcre2, which no amount of pcrec-side testing can
# reach. Its subject being the oracle is also why the design placed it at
# stage 1, four stages before the fold it defends; it landed here because
# stages 1-3 did not build it.
#
# THE CLAIM: libpcre2 10.46 implements SIMPLE case folding and no one-to-many
# folding at all -- 0 of 11 measured cells, under both `PCRE2_UTF|CASELESS`
# and `...|UCP`. The whole caseless lowering rests on it: a 1:n fold is a
# SEQUENCE, so its existence would force a caseless literal into an
# alternation and a caseless class to hold something a set cannot hold. The
# failure would be SILENT -- a future libpcre2 that gained full folding would
# simply start matching cells pcrec answers `no` to.
#
# THE SABOTAGE inverts the verdict test, so all 22 assertions demand a MATCH.
# Against a healthy oracle every one fails, which is the row scoring DETECTED.
# The floor below is 22 and not 11 on purpose: 11 would pass a check that had
# silently dropped the `PCRE2_UCP` arm, which is the arm a full-folding
# implementation is likeliest to reach first.
SAB_ID="S-U11-fold-1n-check-inverted"
SAB_FILE="tests/registry/pc4_check.c"
# [mechreach fix, 2026-09-09] SAB_SUITES was "registry", which never ran
# pc4_check.c at all -- run_sabotage_matrix.sh's `registry` arm builds
# registry_check.c (the SR-1 table vs the parser); PC-4 was documented as
# deliberately NOT wired into this matrix's suite dispatch at all ("add it
# the day one is, with the sabotage that needs it" -- this file's own
# CLAUDE.md). This row's detector had no suite to run in, full stop, which
# is a SEPARATE defect from the [MECH-REACH] one below: fixing the reach
# probe alone still left this row UNDETECTED (measured: reach:ok(1/1),
# registry:0fail/225pass). The new `pc4` arm (registered in
# run_sabotage_matrix.sh's suite vocabulary in the same change) builds and
# runs pc4_check.c's own `check_1n_fold()` directly.
SAB_SUITES="pc4"
SAB_DESC="the standing 1:n fold check asserts that ss-ligature cells DO match caseless, inverting the result the whole DD-1 lowering rests on"
SAB_DOC_FIGURE='MEASURED solo 2026-09-08: a clean run prints the fold block reading 22 assertions (11 cells x 2 option words), 0 matching, and PASSES; inverted, run_pc4.sh exits 1 with exactly 22 FAIL lines naming the design event. MEASURED solo 2026-09-09 (mechreach, post-fix, via the new `pc4` arm): pc4:22fail/1n-fold-only -- DETECTED, matching the 22-FAIL prediction exactly.'
# THE REACH QUESTION FOR A ROW WHOSE SUBJECT IS A CHECK is whether the check
# is still WIRED, not whether the compiler can do something -- so the probe
# greps its call site. The POPULATION floor is 11 (the cells) rather than
# §8.2's 22, because the 22 is ASSERTED EXACTLY inside `check_1n_fold` itself,
# which sees a lost UCP arm that a grep for a string in this file cannot.
# [mechreach fix, 2026-09-09] TWO bugs, both from authoring (a3ba7de7), not
# from anything the tree outgrew. (1) the path was relative
# ("tests/registry/pc4_check.c") but the probe's cwd is $REACH_TMP, a fresh
# scratch dir under $MECH_SCRATCH -- the file was never THERE, so grep
# exited 2 ("No such file or directory"), exactly the exit code the battery's
# mech.log recorded. Needed "$TREE/tests/registry/pc4_check.c". (2)
# SAB_REACH_EXPECT is matched as a LITERAL SUBSTRING (grep -qF in the
# driver), never as a regex -- '^1$' can only ever match the three literal
# characters '^1$', which `grep -c` never prints (it prints a bare "1"). Both
# confirmed by running the exact probe by hand before and after the fix.
SAB_REACH='[ "$(grep -c "check_1n_fold()" "$TREE/tests/registry/pc4_check.c")" = "1" ] && echo REACH-1N-CHECK-WIRED-ONCE'
SAB_REACH_EXPECT='REACH-1N-CHECK-WIRED-ONCE'
SAB_REACH_POP='tests/registry/pc4_check.c|^    \{ "|11'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            asserted++;
            if (rc >= 0)'
SAB_AFTER='            asserted++;
            if (rc < 0)   /* SABOTAGE S-U11: the assertion inverted */'
