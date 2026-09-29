# S336 ([UCP] U1) -- `(?aW)` DOES NOT REACH `\b`.
#
# THE CLAIM (ucp_design.md §1.4, [O]): `(?aW)` restricts `\w \W` AND `\b \B` —
# `(?aW:x\b)` on `xé` matches (an ASCII boundary inside the scope) where
# `x\b` does not. One tag, DEF_UCP_W, covers the whole family; the scope is
# resolved at parse time onto the node (assertions_design.md §8).
#
# THE SABOTAGE drops the `aW` conjunct from DEF_UCP_W, so a restricted `\b`
# resolves to its UCP definition — which U1 REFUSES by name — and a
# restricted `\w` to the UCP word set, which is wide and refused too. A
# pattern that compiled now refuses: tests/ucp/knobs.rxt's `(?aW)` blocks
# (`(*UCP)(?aW:a\b)`, `(*UCP)(?aW)a\b`, `(*UCP)(?aW)\w+`) fail to compile.
SAB_ID="S336-ucp-aw-not-reaching-wordb"
SAB_FILE="src/parse/definitions.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/ucp/knobs.rxt"
SAB_DESC="DEF_UCP_W ignores the (?aW) restriction, so \\b inside (?aW:...) under UCP resolves to UCP \\b and is refused"
SAB_DOC_FIGURE="harness over tests/ucp/knobs.rxt: the (?aW) \\b/\\B/\\w blocks stop compiling (red). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S336."
SAB_REACH='"$PCREC" --features classes,modifiers,assertions -e utf8 -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)(?aW:a\\b)" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        return cx->mods->ucp && !(cx->mods->arestrict & PARSE_ARESTRICT_W);'
SAB_AFTER='        return cx->mods->ucp; /* SABOTAGE S336 */'
