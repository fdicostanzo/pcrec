# S174 — [DD-14 wave G] THE DEAD-CAPTURE ELISION CALLS A LIVE GROUP DEAD.
#
# `pcrec_has_live_capture` (src/opt/atomic.c) answers "can any emitted code
# WRITE a capture slot", and `src/opt/select_engine.c`'s `forces_captures`
# reads it: a pattern with no live capture does not need the capture-recording
# engine and may compile to the DFA. The whole rule rests on ONE structural
# fact — `A_REP{0,0}` EMITS NOTHING, so a group under it has no instruction
# anywhere that assigns its slot pair — plus §3.1's measured capture
# transparency for the call half.
#
# THE POLARITY IS WHY THIS ROW EXISTS. Over-reporting liveness costs an engine
# and never a wrong answer, so the failure that matters is the OTHER
# direction, and it is silent in the worst way: a group that a match CAN set is
# declared dead, the pattern is handed to an engine that cannot record it, and
# every span the user asked for comes back UNSET on a match that is otherwise
# correct. The sabotage widens the prune from `rmax == 0` to "or `rmin == 0`",
# which is the near-miss a reader would actually write — `(a)?` is optional,
# not absent.
#
# ITS DETECTOR IS A `g` LINE AGAIN, for S173's reason, and this time the whole
# `captures/` corpus is the population rather than one module's: `^(a)?b$` on
# "ab" must report g1 = (0,1), and under this row it reports UNSET.
SAB_ID="S174-elision-marks-live-group-dead"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/captures/basic.rxt"
SAB_DESC="pcrec_has_live_capture prunes at rmin == 0 as well as rmax == 0, so every group under an OPTIONAL repeat is declared dead. '(a)?b' then has no live capture, engine selection hands it to the DFA, and group 1 comes back permanently UNSET on a match that is otherwise correct -- the elision's unsound direction, where over-reporting liveness would only have cost an engine."
SAB_DOC_FIGURE="PREDICTED: tests/captures/basic.rxt RED on the group-span lines of every optional-group case, with its m/n spans unchanged; the codegen suite's engine-selection rules RED where a capture-bearing pattern is expected on the VM. The four NAMED elision patterns in run_recursion_identity.sh stay as they are -- this row widens the rule, it does not narrow it -- so that check is NOT the detector and its silence here is the evidence the two are asking different questions. Canonical figure owed from run_sabotage_matrix.sh S174."
SAB_COUNT=1
SAB_BEFORE='            if (a->u.rep.rmax == 0) return false;'
SAB_AFTER='            if (a->u.rep.rmax == 0 || a->u.rep.rmin == 0) return false;   /* SABOTAGE S174 */'
