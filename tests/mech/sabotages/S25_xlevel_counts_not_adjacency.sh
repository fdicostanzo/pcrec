# S25 — the x LEVEL counts occurrences instead of checking ADJACENCY: the
# naive reading of "xx means EXTENDED_MORE" an author recalling the docs
# would write. Measured truth (probe_mod05c.c): (?xsx) is level 1 — only
# an IMMEDIATELY preceding 'x' upgrades — and this sabotage makes any
# second x in the run upgrade, so (?xsx)[a b] silently deletes the class
# space it should keep. R17 checks critic, finding 2.
SAB_ID="S25-xlevel-counts-not-adjacency"
SAB_FILE="src/parse/mod_modifiers.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/xxmode.rxt"
SAB_DESC="pcrec_modport_optrun: x level upgrades on ANY second x in the run, not adjacency"
SAB_DOC_FIGURE="measured R17: 1 harness case (tests/modifiers/xxmode.rxt, the (?xsx)[a b] block)"
SAB_COUNT=1
SAB_BEFORE="        case 'x':
            if (hyphen) un_x = true;
            else xlvl = (i > from && p[i - 1] == 'x') ? 2 : 1;
            break;"
SAB_AFTER="        case 'x':
            if (hyphen) un_x = true;
            else xlvl = (xlvl >= 1) ? 2 : 1;
            break;"
