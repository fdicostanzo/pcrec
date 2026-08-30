# S197 (S-C4) — [DD-13b.W1.1] `# pcre2-only` becomes an ordinary comment,
# so the python oracle stops skipping the blocks it cannot answer and
# starts verifying them against an engine that disagrees with PCRE2.
#
# THE DETECTOR IS A SKIP COUNT, NOT A PASS COUNT, and that is the point of
# the row. Some of the un-skipped blocks will fail loudly (python cannot
# compile them at all); others will PASS while asking the wrong question.
# A check that watched only pass/fail would score this partly detected and
# would go fully green the day the remaining divergences happened to agree.
# W1.1 added the aggregate SKIP line for exactly this: before it, the
# script printed a per-file skip line only when a file had skips and no
# total anywhere, so "the same number of cases were skipped" had nothing
# to read.
#
# ITS POPULATION IS THE MECHANISM'S, NOT THE CENSUS'S. There are 636 lines
# in the corpus BEGINNING `# pcre2-only`; the parser matches the stripped
# line EXACTLY, so its population is 571. A row written against 636 would
# be asserting a number no code produces.
SAB_ID="S197-rxt-pcre2only-ignored"
SAB_FILE="tests/harness/verify_rxt.py"
SAB_SUITES="rxtsource"
SAB_DESC="verify_rxt.py stops recognising the `# pcre2-only` marker, so blocks that are correct for PCRE2 and not python-verifiable are checked against python anyway"
SAB_REACH_POP="tests/lookaround/nonatomic_ahead.rxt|^# pcre2-only$|1"
SAB_COUNT=1
SAB_BEFORE="        if line.strip() == '# pcre2-only':"
SAB_AFTER="        if False and line.strip() == '# pcre2-only':   # SABOTAGE S197"
