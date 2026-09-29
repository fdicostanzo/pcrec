# S24 — the semantic port's `a`+sub-letter lookahead dropped: the consumed
# sub-letter falls into the run walk's default case, which is the port's
# "grammar rejects" internal-error wall — a crash-shaped answer on a
# syntactically valid, PCRE2-real construct ((?aP) compiles there). The
# port's `case 'a':` is a SECOND implementation of the grammar's a<sub>
# rule (recognition in option_run_ok, semantics here) — the R8/C2-9
# two-homes drift shape, which is why it gets its own row. R17 checks
# critic, finding 1.
SAB_ID="S24-asub-lookahead-drop"
SAB_FILE="src/parse/mod_modifiers.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/letters.rxt"
SAB_DESC="pcrec_modport_optrun: drop the a<sub> lookahead so the sub-letter hits the default wall"
SAB_DOC_FIGURE="measured R17: 1 harness case (tests/modifiers/letters.rxt, the (?aP)x block)"
# [UCP] U1 re-aim (lane ucpu1): the lookahead now records WHICH restriction
# and consumes the sub-letter in one line; dropping the consume keeps the
# edit's intent (the sub-letter reaches the default wall).
SAB_COUNT=1
SAB_BEFORE="            if (bit != PARSE_ARESTRICT_ALL) i++;"
SAB_AFTER="            ;   /* SABOTAGE S24: the sub-letter is never consumed */"
