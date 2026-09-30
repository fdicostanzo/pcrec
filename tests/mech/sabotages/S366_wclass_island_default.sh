# S366 ([CLS-TREE] S3, lane s3build) -- THE ISLAND'S WORD SCAN FALLS INTO A
# RESTORED `default:` ON A WIDE CLASS.
#
# `vm_isl_words` carried a real `default: return false` until S3 (D-6), and
# the inventory's row 10 names it the one `default:` site that MOVES
# ARTIFACTS: a wide literal (`café|naïve|résumé`) is an island source, and a
# kind that falls into the default drops the island SILENTLY -- every answer
# unchanged, `RX_VM_ALT_ISLANDS` gone. S3 enumerated the switch fully and
# gave `A_WCLASS` its own arm (walk the child at the same depth). The plant
# puts the default back in place of that arm, the edit a later reader
# "tidying" the switch would make.
#
# Detected two ways that do not share a source: the census reads the SOURCE
# (a switch with a default: and no A_WCLASS label), W3 reads the ARTIFACT
# (the island stamp is gone). Answer checks see nothing.
SAB_ID="S366-wclass-island-default"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="vm_isl_words' A_WCLASS arm is replaced by a default: return false, so a wide-literal alternation silently loses its island"
SAB_DOC_FIGURE="MEASURED solo-plant 2026-09-29 at the S3 tip: wclass:3fail/7pass DETECTED -- [5a] (no A_WCLASS label), [5c] (a default:) and [W3] (RX_VM_ALT_ISLANDS gone on café|naïve|résumé)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case A_WCLASS:
        return vm_isl_words(v, a->l, out, depth, budget);'
SAB_AFTER='    default:
        return false;'
