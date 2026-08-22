# S110 (design row S-BR6) — THE MODULE'S ATOM PORT ALSO CLAIMS THE CLASS
# POSITION.
#
# §5.2's INVARIANT, as a row. Inside a character class a backreference is
# IMPOSSIBLE — there is no cursor to compare against — so `[\0]`..`[\7]` are
# octal and `[\8]` `[\9]` `[\g]` `[\k]` are the literal characters. That is
# PCRE2 BASE SYNTAX (`ExtPort.base`, FIX-3/K13, 41 measured cells), and the
# module gate never touches it: those answers are identical with `backrefs`
# enabled, disabled, or absent.
#
# THE FAILURE IS INVISIBLE TO A MODULE-OFF RUN, which is the point of running
# `octal_class.rxt` with the module ENABLED. Twelve base cells are the only
# thing that sees it, and MOD-0.3d's migration held 127 corpus pins
# byte-identical precisely so that this could not drift unnoticed.
SAB_ID="S110-atom-port-claims-class"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="harness reject registry"
SAB_HARNESS_TARGET="tests/backrefs/octal_class.rxt"
SAB_DESC="The digit rows' CLASS port is replaced by the module's atom port, so [\\1] stops being the byte 0x01 and the class position acquires backreference semantics PCRE2 does not have there. Twelve measured base cells move; every atom-position cell is unaffected"
SAB_DOC_FIGURE="PREDICTED: the corpus RED on octal_class.rxt; registry RED on check_class_ports (the FN class-port population moves). Canonical figure owed from run_sabotage_matrix.sh S110."
SAB_COUNT=1
SAB_BEFORE='{PORT_FN, false, 0, NULL, pcrec_brport_digit}, {PORT_FN, true, 0, NULL, pcrec_clsport_octal}}'
SAB_AFTER='{PORT_FN, false, 0, NULL, pcrec_brport_digit}, {PORT_FN, true, 0, NULL, pcrec_brport_digit}}   /* SABOTAGE S110 */'
