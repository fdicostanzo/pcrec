# S142 ([M6.6.2] wave F, D71 item 3) — AN ALIAS ROW'S MODULE IS THE ONE FACT
# THE INDEX LAYER CAN GET WRONG WITH NOTHING ELSE NOTICING.
#
# WHY THIS ROW EXISTS, and the honest answer is that the family check needed a
# claim of its OWN. `check_families` (tests/registry/registry_check.c) asserts
# four things; three of them are also caught somewhere else the moment they
# break — a dangling `family` reaches `la_kind`'s BAD_ROW and reddens the
# corpus, a widened `engines` mask drops the row out of SR-8's qualifying
# population and fires that check's exact 66/36/36 count, and a `built` that
# moved fires the built-status tally. The FOURTH — members of one family
# disagreeing about their MODULE — is caught by this check and by nothing
# else, and that is exactly the shape this project's own record says goes
# unnoticed:
#
#   - the parser RENDERS the diagnostic from the row, and tests/reject/'s
#     dump-driven loop READS the same row for its expectation, so the two
#     agree in unison about the wrong module. That is this repository's
#     signature check-design failure (docs/dev/learnings.md §3), and it is
#     why tests/reject/ keeps a hand-written second source at all;
#   - the hand-written rows cover THREE of the twelve alpha spellings by
#     design (one short name, one non-atomic, one long spelling). This row
#     sabotages a FOURTH, `(*napla:`, so the hand-written layer genuinely
#     cannot see it;
#   - `check_feature_module_bijection` cannot see it either: the sabotage
#     swaps in `M_verbs`, a VALID feature/module PAIR, so the bijection the
#     `M_*` macros exist to protect still holds.
#
# WHAT GOES WRONG WITHOUT THE CHECK. `--list-families` and the compliance
# page's generated index print ONE line per family, reading module (and
# engines, and status) from the family's canonical member. So a member that
# disagrees is silently overruled in the index while `(*napla:a)` itself
# answers "requires module 'verbs'" to a caller — the precise defect design
# §8.2 measured at P3 and this wave was built to fix, restored for one
# spelling and invisible in the page that is supposed to report it.
#
# NOT A `built` SABOTAGE, and the brief that asked for this row asked the
# right question about that. Flipping a member `unbuilt` DOES break the
# family's AND rule, but it also moves `check_built_status_defects`' exact
# 118 = 70 + 42 + 6 tally, so the family check would not be the detector and
# the row would be measuring something already measured. The module axis is
# where this check is alone.
SAB_ID="S142-alias-family-wrong-module"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="registry"
SAB_DESC="one alpha-spelling INDEX row (the (*napla: alias of (?*a)) is given module 'verbs' instead of 'lookaround' — a valid feature/module pair, so the bijection check still passes, and the family it belongs to now has members that disagree about which module owns the construct"
SAB_DOC_FIGURE="PREDICTED: the registry arm fails naming the family — 'family (?*a): member (?*a) is module lookaround but member (*napla:a) is module verbs — the index prints ONE module for the family'. Canonical figure owed from run_sabotage_matrix.sh S142."
SAB_COUNT=1
SAB_BEFORE='VERB_LA("napla", "(*napla:a)", "(?*a)",
        "non-atomic positive lookahead, alpha spelling of (?*...)"),'
SAB_AFTER='/* SABOTAGE S142: this ALIAS alone re-attributed to module `verbs` */
{RK_VERB, REG_SEL_ANY, "napla", "(*napla:a)", M_verbs, FLAV_PCRE2, VM_ONLY,
 RS_MODULE, RD_MODULE, NULL, NULL, RF_INDEX,
 "non-atomic positive lookahead, alpha spelling of (?*...)", ROADMAP_PLANNED,
 QF_YES, NULL, 0, NULL, {PORT_FN, false, 0, NULL, pcrec_laport_group},
 NO_PORT, "(?*a)"},'
