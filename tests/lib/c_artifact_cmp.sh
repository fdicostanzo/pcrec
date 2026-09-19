# tests/lib/c_artifact_cmp.sh -- compare two pcrec-emitted .c files for
# identity while ignoring the `#include "<basename>.h"` line.
#
# THE TRAP (dd8_report.md section 3.1, the recorded fourth instance --
# scripts/emit_sweep.py:396-398 avoids it with `-o -`; run_cli_tests.sh
# case9/case13/case14 and run_trie_identity.sh's gen_a/gen_b avoid it the
# same way, each independently): a pcrec artifact's `#include` line names
# its OWN `-o` basename, so two artifacts written to different -o names
# always differ there, however identical the rest of the file is. `cmp`/
# `diff` on the raw files reports a difference for a reason that has
# nothing to do with what the comparison was meant to test.
#
# Two independent header-stripping idioms already exist in this tree
# (run_offset_skip.sh's `drop_own_header`, run_island_tests.sh's
# `grep -v '^#include "'`) -- this is the shared form, for a NEW site to
# reach for instead of writing a third.
#
# cmp_c_artifacts FILE1 FILE2
#   Returns 0 (true, bash-comparison sense) iff FILE1 and FILE2 are
#   byte-identical apart from any line matching '^#include "'.
cmp_c_artifacts() {
    local a="$1" b="$2"
    cmp -s <(grep -v '^#include "' "$a") <(grep -v '^#include "' "$b")
}
