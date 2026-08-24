# S126 ([M6.6.2] wave B+C, design §9.3 S-LA5) — SR-8's `VM_ONLY` STAMP IS WHAT
# STOPS THE DFA COMPILING AN ERASED LOOKAROUND.
#
# THE COUPLING THIS DEFENDS, named in design §5.2 rather than buried.
# `src/ir/nfa.c` lowers an `A_LOOK` to an EPSILON, so ONE lowering serves TWO
# consumers with different soundness requirements: as a PREFILTER the erasure
# is sound (L(P) is a subset of L(erase(P)) at every position, measured at 0
# violations over 45 shapes), and as THE DFA ENGINE'S OWN MACHINE it is a
# miscompile. Only SR-8's per-row `engines` stamp stands between the two
# readings. `atomic-groups` has the identical coupling and the identical
# guard, so this is precedent rather than novelty — with one difference in
# this module's favour: an erased lookaround is LOUDLY detectable, because
# `(?=a)b` erased is `b`, which matches "b" where the truth is NOMATCH.
#
# THE ROW MUST BE NAMED (R33 C2-12). SR-8 ANDs the per-row stamps over the
# post-discharge tree, so flipping ONE row frees only patterns written with
# THAT spelling. This flips the `(?=...)` row and nothing else, which is why
# the AFTER text is a longhand row rather than an edit to the shared
# `GROUP_LA` macro — flipping the macro would flip all four rows that use it
# and prove something weaker.
#
# THE DETECTOR MUST BE CAPTURE-FREE (R33 C2-12 again, measured). `(a)(?=b)c`
# keeps the VM whatever this row says, because delivering a capture slot is
# already VM-forcing — so a capture-bearing detector would MASK the row.
# `(?=a)b` satisfies both requirements and is in `lookahead.rxt` by name, with
# its own comment saying so.
#
# [M6.6.2 wave E2] `laexpand` ADDED TO THIS ROW, and it was MEASURED before it
# was assigned (2026-08-24, one laexpand-only mech run per row: 8 of the
# module's 15 rows DETECTED, 7 UNDETECTED — the table is in
# tests/mech/CLAUDE.md). What the substitution driver sees here that the
# module's own corpus does not is DEPTH: 8,260 libpcre2-verified cells
# belonging to a module that already ships, re-expressed as lookarounds. For
# this row, the driver compiles every expanded pattern through the DEFAULT
# engine selection, so the erased-lookaround prefilter answers for the
# wrong language on the whole expanded population.
SAB_ID="S126-look-row-not-vmonly"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="harness lookaround registry laexpand"
SAB_HARNESS_TARGET="tests/lookaround/lookahead.rxt"
SAB_DESC="the (?=...) registry row's engines mask is widened from VM_ONLY to ANY_ENGINE, so SR-8 stops forcing the VM for a positive lookahead and the pattern is compiled from nfa.c's epsilon lowering — the lookaround-ERASED language"
SAB_DOC_FIGURE="PREDICTED: (?=a)b answers (0,1) on \"b\" where the truth is NOMATCH; the registry arm's engine-capability tripwire also fires (a VM_ONLY row with a producer must refuse --engine=dfa by name). Canonical figure owed from run_sabotage_matrix.sh S126."
SAB_COUNT=1
# [M6.6.2 wave F] THE `AFTER` ROW GAINED ITS `family` SLOT. `RegRow` grew a
# `family` field (D71 item 3) and every longhand row initialises it
# explicitly; NULL is the CORRECT value here -- `(?=...)` IS its family's
# canonical spelling, and its two alpha aliases point AT it -- so this is the
# same row it always was, spelled against the current struct rather than
# relying on a zero default nobody wrote.
SAB_BEFORE='GROUP_LA('"'"'='"'"',  "(?=...)",       "positive lookahead"),'
SAB_AFTER='/* SABOTAGE S126: this ROW alone widened to ANY_ENGINE */
{RK_GROUP, '"'"'='"'"', NULL, "(?=...)", M_lookaround, FLAV_PCRE2, ANY_ENGINE, RS_MODULE, RD_MODULE, NULL, NULL, 0, "positive lookahead", ROADMAP_PLANNED, QF_YES, NULL, 0, NULL, {PORT_FN, false, 0, NULL, pcrec_laport_group}, NO_PORT, NULL},'
