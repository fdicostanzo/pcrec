# S1981 ([VLOOKBEHIND] review r4 F1) -- THE REFUSAL TIER OF A MATCH-TIME LENGTH.
# A lookbehind holding a backreference or a variable is pcrec's capability
# limit (shape 5, "not implemented"); libpcre2 accepts `(a)(?<=\1)x`. Planted,
# the rule never asks `pcrec_cwmax_static`, so every such lookbehind reads
# "unbounded" again: true refusal, false fact about PCRE2.
SAB_ID="S1981-lb-backref-reads-unbounded"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="reject"
SAB_DESC='a lookbehind holding a backreference or a variable is refused as unbounded (shape 7) instead of not implemented (shape 5)'
SAB_DOC_FIGURE='PREDICTED (lane vlbfix): the two shape-5 reject_gated rows red ((a)(?<=\1)x, (?<=${x})a: "unbounded" printed); the two err-125 controls stay green.'
SAB_COUNT=1
SAB_BEFORE='            if (pcrec_cwmax_static(br[i]) >= PCREC_W_UNBOUNDED)'
SAB_AFTER='            if (1)   /* SABOTAGE S1981 */'
