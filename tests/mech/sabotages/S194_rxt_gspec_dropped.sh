# S194 (S-C1) — [DD-13b.W1.1] run.sh's parser DROPS every `g`/`gp` capture
# expectation, so 4,182 corpus expectations stop being checked and nothing
# about the patterns themselves changes.
#
# THE ROW IS INTERESTING BECAUSE THE LOSS IS SILENT IN THE OBVIOUS PLACE.
# A dropped expectation cannot FAIL — it is simply never asked — so the
# corpus's pass/fail split does not go red, it goes SMALLER, and a suite
# that reports "0 failures" reports exactly that either way. What sees it
# is a COUNT and a DIFFERENTIAL: `harness` because 4,182 fewer cases are
# scored, and `rxtsource` because leg C (verify_rxt.py, a different parser
# in a different language) still reads the lines and leg B no longer does.
#
# TWO ARMS ON PURPOSE. Either alone would be a weaker claim: the count
# arm cannot say WHICH cases went missing, and the differential cannot say
# that anything was being checked in the first place.
SAB_ID="S194-rxt-gspec-dropped"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource harness"
SAB_DESC="run.sh's g/gp arm parses the line and then discards it, so every per-group capture expectation in the corpus is silently never checked"
SAB_REACH_POP="tests/captures/basic.rxt|^gp? |10"
SAB_COUNT=1
SAB_BEFORE='                case_gspec[$last_idx]="${case_gspec[$last_idx]}${gslot},${gstart},${gend},${gpend};"'
SAB_AFTER='                : "SABOTAGE S194: the g/gp expectation is parsed and thrown away"'
