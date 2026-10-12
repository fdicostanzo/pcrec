# tests/lib/compound_art.sh -- [COMPOUND] ONE answer to "is this artifact a
# compound", for every corpus sweep that holds a MACHINE stamp to the text
# (docs/spec/match_api.md §3.7, §6.3.12). A compound's machine-level stamps
# read "compound" (counts -1): its text is parts and a controller, so no
# single scan, table, start recovery or handoff exists for such a sweep to
# compare. Those sweeps SKIP a compound and COUNT the skip; the compound's
# own stamps are held in ONE place, tests/codegen/run_dfa_stamps.sh's
# compound bucket. Source this file; it defines:
#   compound_row FILE   the artifact's <PREFIX>_COMPOUND value: "none", a
#                       row name, "forced-off" (the harness lever), or ""
#                       (no stamp: not an artifact of this abi)
#   is_compound FILE    true iff FILE is a compound (a row name)
# A part's own macros sit under `<prefix>__<role>` and a part carries no
# COMPOUND stamp, so the one line read is the artifact's.
compound_row() {
    sed -n 's/^#define [A-Za-z0-9_]*_COMPOUND "\(.*\)"$/\1/p' "$1" | head -1
}
is_compound() {
    case "$(compound_row "$1")" in
        ""|none|forced-off) return 1 ;;
        *) return 0 ;;
    esac
}
