# S26 — the run's apply order flipped: unset applied BEFORE set, so a
# letter named on both sides of the hyphen resolves set-wins. Measured
# truth (probe_mod05c.c): (?i-i)k and (?-ii)k are BOTH case-sensitive —
# unset WINS regardless of order — and the port encodes that only by its
# fixed set-then-unset block order, with no explicit branch. This is the
# one-reordering-refactor-away regression. R17 checks critic, finding 3.
SAB_ID="S26-unset-applied-first"
SAB_FILE="src/parse/mod_modifiers.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/letters.rxt"
SAB_DESC="pcrec_modport_optrun: apply un_* before set_*, so set wins a contested letter"
SAB_DOC_FIGURE="measured R17: 1 harness case (tests/modifiers/letters.rxt, the (?i-i)a block — (?-ii)a is NOT contested under this flip: both its i's are unset-side, so it pins the unset path itself, not the order)"
SAB_COUNT=1
# RE-ANCHORED 2026-08-21 (sabanchors lane): [M6.2] wave C added the 'm'
# (multiline) letter to this same set/unset block (set_m/un_m, ns.multiline),
# two lines this row's anchor predates. Anchor updated to include them, in
# their real position, so the flip still reorders the WHOLE block rather
# than only its pre-wave-C prefix. Intent (unset applied before set, so set
# wins a contested letter) unchanged.
SAB_BEFORE="    if (set_i) ns.caseless = true;
    if (set_s) ns.dotall = true;
    if (set_U) ns.ungreedy = true;
    if (set_n) ns.nocap = true;
    if (set_m) ns.multiline = true;
    if (set_J) ns.dupnames = true;
    if (xlvl >= 0) ns.xlevel = (uint8_t)xlvl;
    if (un_i) ns.caseless = false;
    if (un_s) ns.dotall = false;
    if (un_U) ns.ungreedy = false;
    if (un_n) ns.nocap = false;
    if (un_m) ns.multiline = false;
    if (un_J) ns.dupnames = false;
    if (un_x) ns.xlevel = 0;"
SAB_AFTER="    if (un_i) ns.caseless = false;
    if (un_s) ns.dotall = false;
    if (un_U) ns.ungreedy = false;
    if (un_n) ns.nocap = false;
    if (un_m) ns.multiline = false;
    if (un_J) ns.dupnames = false;
    if (un_x) ns.xlevel = 0;
    if (set_i) ns.caseless = true;
    if (set_s) ns.dotall = true;
    if (set_U) ns.ungreedy = true;
    if (set_n) ns.nocap = true;
    if (set_m) ns.multiline = true;
    if (set_J) ns.dupnames = true;
    if (xlvl >= 0) ns.xlevel = (uint8_t)xlvl;"
