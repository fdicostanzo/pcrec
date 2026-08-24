# S104 (design row S-BR15b) — ONLY ONE MEMBER OF A DUP-NAME RUN IS MARKED.
#
# R32's re-check E13. §8.3's resolution is a MATCH-TIME choice: the emitted
# chain reads EVERY member's pair in ascending number until it finds a
# published one. So the marked set — the groups that get publish-at-close —
# must be the UNION of every `A_BREF`'s `refs`, not the member some analysis
# thinks the reference "resolves to". Mark only one and E1 returns through the
# others.
#
# THE MEASURED CELL SHOWS THERE IS NO SUCH MEMBER TO PICK:
# `(?J)^(?:(?<a>q))?(?:(?<a>a|b\k<a>))+$` on "aba" is (0,3) with group 1 UNSET
# and group 2 = (1,3) — the chain falls THROUGH the unset first member to the
# second, which is the one being RE-ENTERED. Marking "the first" is exactly
# wrong here, and marking "the last" is wrong on the sibling cell.
#
# INVISIBLE to every cell where the first member resolves, which is why
# `dupnames.rxt` had to GAIN re-entry cells (the first design's file had none,
# so this row would have had no detector at all).
SAB_ID="S104-mark-one-run-member"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="dupnamesdiff brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/dupnames.rxt"
SAB_DESC="pcrec_bref_mark marks only the FIRST member of each A_BREF's refs array, so a duplicated name's later members keep write-on-traverse. The resolution chain reads them at match time, and R32 E1 returns through an unmarked one: (?J)^(?:(?<a>q))?(?:(?<a>a|b\\k<a>))+$ on \"aba\" resolves to group 2, which is precisely the member this sabotage leaves unpublished"
SAB_DOC_FIGURE="PREDICTED: dupnamesdiff RED; the corpus RED on dupnames.rxt's re-entry block. Canonical figure owed from run_sabotage_matrix.sh S104."
SAB_COUNT=1
SAB_BEFORE='            for (int i = 0; i < a->u.bref.nrefs; i++)
                if (a->u.bref.refs[i] > 0 && a->u.bref.refs[i] < nmark) mark[a->u.bref.refs[i]] = true;'
SAB_AFTER='            /* SABOTAGE S104: only the first member of the run */
            for (int i = 0; i < 1 && i < a->u.bref.nrefs; i++)
                if (a->u.bref.refs[i] > 0 && a->u.bref.refs[i] < nmark) mark[a->u.bref.refs[i]] = true;'
