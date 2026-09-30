# S402 ([OPT-CLSPACK], lane clspack) -- THE SITE THRESHOLD IS OFF BY ONE.
#
# ANSWER-NEUTRAL: D131 item 6 rules the atom table the default "from N ~ 11
# live class sites up"; the plant makes the row need 12, so an artifact with
# exactly 11 table-read classes keeps its bitmaps. Every answer is right
# either way; run_clspack.sh's atom-11 witness sits exactly on the threshold
# so a strict/non-strict slip moves its stamp.
SAB_ID="S402-clspack-threshold-off-by-one"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clspack"
SAB_DESC="the table selection's atom predicate compares nset > atom_min_sites, so exactly 11 table-read classes no longer share an atom table"
SAB_DOC_FIGURE="(measured below at landing)"
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            holds = nset >= PLACE.atom_min_sites'
SAB_AFTER='            holds = nset > PLACE.atom_min_sites'
