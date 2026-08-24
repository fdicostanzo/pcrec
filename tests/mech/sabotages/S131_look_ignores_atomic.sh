# S131 ([M6.6.2] wave B+C, design §9.3 S-LA16) — `.atomic` IS READ.
#
# THE THIRD OF D62 CONTROL 3's THREE FLAG ROWS (see S129's header for the
# argument). Ignoring `.atomic` and always emitting the cut makes the
# NON-ATOMIC forms behave atomically — `(?*X)` becomes `(?=X)`.
#
# **OBSERVABLE ONLY THROUGH `nonatomic_ahead.rxt`'s `# pcre2-only` CELLS**, and
# the design says so because it decides the suite assignment. python3 `re` has
# no `(?*` AT ALL (design §7, G5), so every cell that can see this row is one
# `tests/harness/verify_rxt.py` skips — the corpus harness DOES run them (a
# `# pcre2-only` line is an ordinary comment to `run.sh`; it is the python
# oracle that steps aside), which is why the `harness` arm scores this row.
# The `lookaround` arm scores it a second way and a sharper one: its §2
# asserts the EXACT number of cells on which `(?=` and `(?*` DISAGREE, so a
# compiler that cut both spellings reports agreement where 13 disagreements
# are required. R33 C2-7 is why that arm was wired at this wave rather than at
# wave F as the design first placed it — without it this row would score
# UNDETECTED while looking like coverage.
SAB_ID="S131-look-ignores-atomic"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround/nonatomic_ahead.rxt"
SAB_DESC="vm_look ignores Ast.u.look.atomic and always emits the cut, so the NON-ATOMIC (?* commits to its body's first success exactly as (?= does — the two spellings become one construct"
SAB_DOC_FIGURE="PREDICTED: nonatomic_ahead.rxt goes red on the cells where a retry is possible — (?*(a|ab))\\1\$ on \"abab\" answers NOMATCH where libpcre2 says (2,4) — and the lookaround arm's §2 reports 0 disagreements where 13 are required. Canonical figure owed from run_sabotage_matrix.sh S131."
SAB_COUNT=1
SAB_BEFORE='    const bool atomic = a->u.look.atomic;'
SAB_AFTER='    const bool atomic = true;   /* SABOTAGE S131: .atomic ignored */'
