# S273 — [recidfix->varland] THE BUCKET'S OWN NEGATIVE CONTROL: a
# `vm_bref`/`vm_var` emission bug that is NOT the ruled seam rename must NOT
# be admitted by `run_recursion_identity.sh`'s fourth named exception
# (`bref_rename_rewrite`), because a bucket whose admission is loose enough
# to swallow an unrelated defect is worse than no bucket — a green run would
# read as "the rename, nothing else" while hiding a real miscompile.
#
# THE PLANT is one token in the LENGTH operand of the renamed call:
# `(size_t)(ref_end - ref_start)` becomes `(size_t)(ref_end - ref_start + 1)`
# — a backreference compare that reads one byte PAST the referenced group on
# every call. The call still says `span_match`, the reference side is still
# `subject + (size_t)ref_start`, so on casual inspection this differs from
# the ruled rename only in one `+ 1`. That similarity is the whole point of
# the row: `bref_rename_rewrite`'s admission is EXACT TEXT EQUALITY after its
# one substitution, not "looks like the rename", so the extra token must
# leave the rewritten pre-module region byte-UNEQUAL to the subject's and the
# pattern must land in `rdiff`, not in the new bucket.
#
# THIS IS ALSO AN ORDINARY WRONG-ANSWER ROW, unlike S269/S270's
# admission-only siblings: reading one byte too many changes a real ANSWER
# (a backreference now accepts a byte the pattern never asked to match), so
# `brefdiff`/`harness` catch it independently of anything this row's own arm
# does. `recidentity`'s job is narrower — it is the only arm that can say
# WHERE inside the identity gate's bucket machinery the difference was
# supposed to land, and that it did not silently fall into the rename's own
# exception instead.
SAB_ID="S273-span-match-length-off-by-one"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="recidentity brefdiff harness"
SAB_DESC="vm_bref's renamed span_match call reads one byte past the referenced group's end ((size_t)(ref_end - ref_start + 1) instead of (size_t)(ref_end - ref_start)) -- an ordinary backreference-length miscompile that happens to share vm_bref's emission site with the ruled [VAR] M6 seam rename, so the row also proves run_recursion_identity.sh's new bref-rename bucket does not admit it by resemblance"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (varland lane, tree df867383): recidentity:SKIPPED-no-git-history -- this arm can NEVER run inside tests/mech/run_sabotage_matrix.sh's scratch trees (git archive HEAD | tar -x has no .git, and the gate needs full git history to git-archive its pinned reference commits; MECH-2), so the mech matrix cannot score this row's own claim directly. brefdiff:23fail/7pass and harness (corpus:467fail/28646pass) both DETECTED independently on the length-changing answer, exactly as predicted -- the failing cells show the predicted signature ('(a)\\1' answering 'match 0 3' where the oracle says 'match 0 2', one byte too long). Row verdict: DETECTED (SKIPPED -- no oracle), unexpected: 0. The row's own claim -- that comparison (A) lands the plant in rdiff rather than the bref-rename bucket -- was validated MANUALLY instead (docs/dev/lanes/varland_report.md Sec3a): a hand-sabotaged compiler's program region for '(a)\\1' was compared by hand against bref_rename_rewrite()'s output on the real pre-module reference binary, and the two differ by exactly the +1 token -- confirming the bucket does NOT admit it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S273."
# [MECH-REACH] the clean tree really does emit the two-line pointer+length
# form on an ordinary backreference, both directions asserted: the OLD
# two-offset form must be ABSENT (the rename has landed) and the NEW form
# must be PRESENT (there is something for the plant to touch).
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a)\1" && grep -q "(size_t)(ref_end - ref_start)," "$REACH_TMP/o.c" && ! grep -q "(size_t)ref_start, (size_t)ref_end," "$REACH_TMP/o.c" && echo REACH-SPAN-MATCH-LENGTH-FORM-PRESENT'
SAB_REACH_EXPECT="REACH-SPAN-MATCH-LENGTH-FORM-PRESENT"
SAB_COUNT=1
SAB_BEFORE='        "                  (size_t)(ref_end - ref_start),\n"'
SAB_AFTER='        "                  (size_t)(ref_end - ref_start + 1),\n"   /* SABOTAGE S273: off by one */'
