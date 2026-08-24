# S158 ([DD-14] wave B+C, design SS9.3 S-SR10 AND S-SR11a) -- A CALL TARGET
# JOINS THE MARKED SET.
#
# ONE ROW FOR TWO DESIGN IDS, because the arm is ONE LINE and both ids
# sabotage it. SS9.3 splits them because it expected a transitivity FIXPOINT to
# be a separate mechanism from the one-hop mark; SS4.3 WITHDREW that clause on
# measurement, and the two-hop shape is now the same line's population rather
# than a second line's. The row keeps both cells for exactly that reason.
#
# THE CLAIM (P10, MEASURED): `--no-captures` deletes the `A_CAP` wrapper of
# every group NOTHING references -- `(a)\1` under the flag mentions
# `RX_SLOT_GROUP1` NINE times and `(a)b` mentions it ZERO. A call names a group
# exactly as a reference does, so without this arm `(a)(?1)` under
# `--no-captures` loses group 1 and the call has no body at all.
#
# THE MARK IS NOT TRANSITIVE AND NEEDS NO FIXPOINT, and that is SS4.3's own
# correction to its first version: a call from INSIDE group 1 to group 3 is an
# `A_CALL` NODE IN THE TREE, so `pcrec_bref_mark`'s whole-tree walk reaches it
# WHEREVER IT SITS and marks 3 directly. The arm is `mark[target] = true` and
# no descent -- which is also design SS4.4's rule (a whole-tree predicate must
# not follow `.body`) paying for itself.
#
# ITS DETECTOR IS NOT A `.rxt` CELL AND CANNOT BE. There is no `.rxt` directive
# for `--no-captures` anywhere in this tree, which the corpus's own CLAUDE.md
# records as a gap and names the shape of the fix: a separate instrument that
# compiles under the flag and inspects the ARTIFACT.
# `tests/recursion/run_recursion_diff.sh` SS1 is that instrument, and it asserts
# BOTH halves -- the group's slots survive in the emitted C, AND the matcher
# still answers correctly while reporting `RX_NCAPS 1` -- because the answer
# alone can be right by accident on a subject the callee's own text happens to
# match.
SAB_ID="S158-call-target-unmarked"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="recursion"
SAB_DESC="pcrec_bref_mark's A_CALL arm stops marking u.call.target, so under --no-captures the called group's A_CAP is stripped out from under the call and the callee has no body"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR10/S-SR11a): the --no-captures AXIS ONLY, which is why this row's suite is \`recursion\` (run_recursion_diff.sh 1) and not \`harness\`: no .rxt directive for that flag exists anywhere in the tree, so the corpus is structurally blind to it. 1 asserts BOTH hops -- (a|b)(?1) for S-SR10 and ^(a(?3))(b)((c))\$ for S-SR11a -- and asserts them in the artifact (the slot legend) as well as in the answer, because the answer can be right by accident on a subject the callee's own text happens to match."
SAB_COUNT=1
SAB_BEFORE='        case A_CALL:
            if (a->u.call.target > 0 && a->u.call.target < nmark)
                mark[a->u.call.target] = true;
            return;
        case A_CAT:'
SAB_AFTER='        case A_CALL:   /* SABOTAGE S158: the target is not marked */
            return;
        case A_CAT:'
