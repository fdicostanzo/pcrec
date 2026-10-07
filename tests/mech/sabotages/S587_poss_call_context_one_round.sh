# S587 — K93: THE CALL-CONTEXT FIXPOINT STOPPED AFTER ONE ROUND
# (src/opt/possessify.c, `pss_run`): one context-only walk, then the marking
# walk, whether or not the first walk widened anything.
#
# A context a call site sees can depend on the context of the group it sits
# in, which may only be joined later in the same walk. The context walk runs
# right to left along each spine, so a pattern whose calls all PRECEDE their
# definitions needs a second round: `(?1)a((?2))c(a+)b` reaches group 2 before
# group 1's site inside it carries group 1's context `{a}`, leaves group 2's
# context at `{c}`, and possessifies `a+` — NOMATCH on "aaacab" where
# libpcre2 10.46 answers (0,6). Every other k93.rxt witness converges in one
# round, so this row's detector is that one block.
SAB_ID="S587-poss-call-context-one-round"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/k93.rxt"
SAB_DESC="the call-site context fixpoint runs one context-only walk instead of iterating to convergence, so a context that reaches a group only through a later-joined context is lost (K93)"
SAB_DOC_FIGURE="PREDICTED: harness on tests/recursion/k93.rxt — the (?1)a((?2))c(a+)b block fails (nomatch where libpcre2 answers a match); every other block stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S587."
# [MECH-REACH] the site answers at HEAD: the second-round witness's `a+` is
# not possessified.
SAB_REACH='"$PCREC" --features recursion --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "(?1)a((?2))c(a+)b" && grep -q "^#define RX_VM_STRATS 0x2u" "$REACH_TMP/o.c" && echo REACH-CALL-ROUND2'
SAB_REACH_EXPECT="REACH-CALL-ROUND2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        } while (P->cc_grew);'
SAB_AFTER='        } while (false);   /* SABOTAGE S587: one round */'
