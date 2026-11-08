# S1890 ([RUN-POS-SET] stage 2b, lane altbuild; design §3.2 r4 SND-1, §5 2b
# S-w) -- THE ADJACENCY TEST'S ROW 2 IGNORES WRITES.
#
# Row 2 passes an `m` of `j`'s exact width only if `m` writes nothing. The
# plant drops the condition, so `(?:ab|a\Kd|ad)` merges `ad` up past `a\Kd`
# and answers (0,2) on `ad`, where libpcre2 answers (1,2); its capture twin
# `(?:ab|(a)d|ad)\1?` answers (0,2) on `ada` against (0,3).
# tests/altcls/altnf_rules.rxt's S-w blocks.
SAB_ID="S1890-altnf-row2-ignores-writes"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/altcls/altnf_rules.rxt"
SAB_DESC="the adjacency test's row 2 passes a same-width branch that writes, so (?:ab|a\\Kd|ad) merges ad past a\\Kd and loses the reset start libpcre2 reports"
SAB_DOC_FIGURE="PREDICTED: tests/altcls/altnf_rules.rxt red on the S-w blocks (\\K and capture twins)."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:ab|a\\Kd|ad)" | grep -o "ALTCLS_FACTORED [0-9]*"'
SAB_REACH_EXPECT='ALTCLS_FACTORED 2'
SAB_REACH_POP='tests/altcls/altnf_rules.rxt|^pattern \(\?:ab\|a\\Kd\|ad\)$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return m->hd.minw == j->w && m->hd.bounded && m->hd.maxw == j->w &&
           !m->hd.writes;                                   /* row 2 / 3 */'
SAB_AFTER='    return m->hd.minw == j->w && m->hd.bounded && m->hd.maxw == j->w;   /* SABOTAGE S1890 */'
