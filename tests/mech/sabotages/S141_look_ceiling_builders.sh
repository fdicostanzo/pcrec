# S141 ([M6.6.2] wave E, design §9.3 S-LA13) — THE PREDICATE IS READ AT ALL THE
# CEILING SITES, NOT ONLY AT THE STAMP.
#
# THE CLAIM (design §5.6(3)). `v.mrl_win` has FOUR readers: `--emit-ir`'s
# PRUNING description, the `RX_VM_PRUNE_CEILING` stamp, and the TWO lines that
# BUILD the ceiling — the search ENTRY's `window_end = min(window[0][1], n)` and
# the RETRY recompute. R31 E3 measured what happens when only the first two read
# it: the artifact stamps "subject-end" while its ceiling is still LIVE, and a
# check asserting on the stamp is GREEN on a matcher silently losing matches.
#
# THIS ROW IS THE OTHER HALF OF S88, AND THE DIRECTION IS REVERSED FROM THE
# DESIGN'S FIRST SKETCH (R33 C2-10). That sketch had the row sabotage the stamp
# and needing a second site to do it; the stamp is a ONE-SITE expression, so
# flipping its source needs no second site at all. The two BUILDERS are the pair
# that is two sites by construction, and this row sabotages BOTH of them while
# LEAVING THE STAMP READING THE FLAG. S88 does the entry site alone for the
# atomic module; this one does entry AND retry, so a compiler on which only the
# retry recompute had been missed is caught too.
#
# WHAT MAKES IT DETECTABLE IS A STRUCTURAL CHECK AND NOTHING ELSE. Every
# behavioural suite in the tree is GREEN on this sabotage for the atomic and
# lookaround corpora alike -- no, it is worse than that: the sabotage RESTORES
# the pre-[M6.4.2] bug, so the answers that go wrong are exactly the ones S88's
# and S140's own corpora already own. What THIS row defends is that the
# artifact's four descriptions of its own ceiling cannot DISAGREE, which no
# corpus can see. `[M6.6-LOOKAROUND rule 1]` and `[M6.4-ATOMIC rule 1]` are one
# shared function for that reason, and 1(a) is the arm that fires here.
#
# IRLISTING IS PREDICTED GREEN, AND THE DISJOINTNESS IS THE POINT. The
# `--emit-ir` description reads `v.mrl_win`, which this row does not touch, so
# the listing keeps saying "the subject end" while the emitted code clamps. A
# row that turned every assigned suite red would not prove the sources are
# separately needed -- S88's own doc figure makes the same argument for 1(a)
# versus 1(b).
SAB_ID="S141-look-ceiling-builders"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen irlisting"
SAB_DESC="Both lines that BUILD the MRL ceiling -- the search entry and the retry recompute -- are gated on job->fit.prefilter instead of on v.mrl_win, while the stamp and the --emit-ir description keep reading the flag. Every artifact whose ceiling was suppressed (atomic or lookaround) now stamps \"subject-end\" and clamps to the prefilter window anyway: R31 E3's defect, restored at both builders at once"
SAB_DOC_FIGURE="PREDICTED: [M6.4-ATOMIC rule 1(a)] and [M6.6-LOOKAROUND rule 1(a)] RED (2 window[0][1] assignments survive on each fixture) with 1(b) and 1(d) GREEN on both, and [rule 1c] GREEN on both twins; irlisting GREEN, because the fourth reader is untouched and the disjointness is the row's point. Canonical figure owed from run_sabotage_matrix.sh S141."
SAB_COUNT=1
SAB_BEFORE='            v.nclamp == 0 ? ""
              /* H3 site 1 of 3 (the search ENTRY). */
              : v.mrl_win
'
SAB_AFTER='            v.nclamp == 0 ? ""
              /* SABOTAGE S141 site 1/2: the ENTRY builder re-derives from the
               * raw prefilter flag instead of reading the predicate */
              : job->fit.prefilter
'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='                 prefn,
                 v.mrl_win
                   ? "            window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;\n"'
SAB_AFTER2='                 prefn,
                 /* SABOTAGE S141 site 2/2: the RETRY builder, likewise */
                 job->fit.prefilter
                   ? "            window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;\n"'
