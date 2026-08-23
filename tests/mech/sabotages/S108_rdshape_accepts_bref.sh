# S108 (design row S-BR4) — `rd_shape` GAINS AN ARM ACCEPTING `A_BREF`.
#
# THE ALARM SAYS AN ARM IS MISSING, NEVER WHICH ARM IS RIGHT, and that is the
# whole reason this is a row. Adding an `AKind` makes `rd_shape`'s switch raise
# `-Wswitch` under `make strict`; the author then has to choose, and ACCEPT is
# the plausible wrong choice.
#
# WHY IT MUST DECLINE. The reverse-deterministic rung recovers an iteration
# boundary by matching the REVERSED body from the right. A backreference's
# operand is not in its text — it is subject bytes a capture published — and
# there is no reversed spelling of "compare against what group k captured".
# `rd_reverse` runs only on a body this scan approved and its fallthrough
# COPIES, so an accepting arm here produces a reversed body that compares the
# same span while the walk runs the other way.
#
# Declining is always available and always safe (this file's own invariant),
# so the sabotage costs nothing to revert and everything to keep.
#
# ============================================================================
# TWO SITES, AND THE SECOND ONE IS WHY THIS ROW EXISTS AT ALL.
# Reworked 2026-08-22 after the SINGLE-SITE form scored UNDETECTED in the
# 118-row matrix on 5edba64. The single-site measurement is kept below because
# it is the finding, not a footnote: it is what a one-hunk mutation can and
# cannot say about a pair of independent gates.
#
# THE SINGLE-SITE FORM WAS UNOBSERVABLE, MEASURED. `rd_rep` consults two gates
# in sequence and the rd_shape edit removes only the first:
#
#     rd_shape(&S, a->l);                        <-- site 1
#     if (S.ok && pcrec_uniq_iteration(...))     <-- site 2
#         rev = rd_reverse(...);                 <-- the wall
#
# `pcrec_uniq_iteration` builds a Glushkov position automaton, and
# src/opt/possessify.c's own `case A_BREF:` sets `g->ok = false` -- a
# backreference consumes a variable amount of text, so it has NO POSITION and
# the (U1)/(U2) argument is not expressible over it. With ONLY site 1 applied,
# and a probe printf in rd_rep, on four bodies built to be revdet-eligible
# except for the reference:
#
#     (x)(?:ab|\1){2,}y   rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (x)(?:\1){2,}y      rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (x)(?:a\1){2,}y     rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (ab)(?:\1cd){2,}y   rd_shape S.ok=1   uniq_iteration=0 why=model-error
#
# The arm's verdict DID flip (S.ok 0 -> 1); the second gate declined every one,
# and the emitted artifact was BYTE-IDENTICAL to clean on all four. That is not
# a corpus gap -- the two gates are COEXTENSIVE, since every body whose
# rd_shape verdict site 1 changes is a body containing an `A_BREF`, which is
# exactly what the Glushkov arm refuses. No cell can exist.
#
# THE MIRRORED SINGLE EDIT IS NOT A SUBSTITUTE EITHER (measured): removing only
# possessify.c's `g->ok = false` and leaving rd_shape intact never reaches
# revdet at all -- rd_shape still declines first -- and its byte difference
# comes from POSSESSIFICATION instead ((x)(?:a\1){2,}y acquires "possessified
# unbounded repeat" and an RX_CUT). That is a different claim about a different
# pass, and it belongs to a row nobody has written yet.
#
# SO THE ROW REMOVES BOTH GATES, which is what its claim always described, and
# the reverse rung is genuinely OFFERED a body whose reversal has no meaning.
# rd_reverse then raises the wall its own comment promises. MEASURED with both
# sites applied, against the corpus AS IT ALREADY STANDS -- no new cell was
# needed, which is the difference between this row and S107:
#
#     tests/harness/run.sh tests/backrefs/*.rxt
#         clean:    455 pass / 0 fail
#         both:     390 pass / 65 fail, 13 distinct pattern-compile failures,
#                   33 "internal error: a backreference reached the reverse-
#                   deterministic body reversal" lines
#         caught by nested.rxt (22), selfref.rxt (30), dupnames.rxt (16)
#
# WHY TWO AND NOT THREE. A row needing three coordinated edits is describing a
# refactor rather than a plausible mistake. These two are one decision -- "a
# backreference is fine in a reversed body" -- spelled in the two files that
# each independently disagree, which is exactly the shape a reader following
# the `-Wswitch` alarm could talk themselves into.
# ============================================================================
SAB_ID="S108-rdshape-accepts-bref"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/nested.rxt"
SAB_DESC="rd_shape ACCEPTS a backreference in a quantifier body AND pcrec_uniq_iteration's independent Glushkov decline for A_BREF is removed, so the reverse-deterministic rung is genuinely OFFERED a body whose reversal has no meaning. rd_reverse raises its internal-error wall. TWO SITES because one is not falsifiable: with only the rd_shape edit the second gate declines every such body (why=model-error) and the artifact is byte-identical -- measured, see header"
SAB_DOC_FIGURE="MEASURED 2026-08-22 with both sites: harness tests/backrefs 390 pass / 65 fail, 13 distinct pattern-compile failures, 33 internal-error lines from rd_reverse's wall (nested.rxt 22, selfref.rxt 30, dupnames.rxt 16); clean 455/0. Canonical figure from run_sabotage_matrix.sh S108 below. The SINGLE-site form measured UNDETECTED -- zero checks failed, artifact byte-identical -- see header."
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
            S->ok = false;
            return;'
SAB_AFTER='        case A_BREF:
            return;   /* SABOTAGE S108 site 1: ACCEPT it */'

# SITE 2 -- the independent decline that made the one-hunk form unfalsifiable.
SAB_FILE2="src/opt/possessify.c"
SAB_COUNT2=1
SAB_BEFORE2='    case A_BREF:
        g->ok = false;
        return gk_parts_empty(true);'
SAB_AFTER2='    case A_BREF:
        return gk_parts_empty(true);   /* SABOTAGE S108 site 2: no independent decline */'
