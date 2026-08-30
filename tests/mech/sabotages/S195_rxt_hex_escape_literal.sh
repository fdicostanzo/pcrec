# S195 (S-C2) — [DD-13b.W1.1] the python oracle decodes `\xHH` as the three
# characters `xHH` instead of the byte, so every subject carrying a hex
# escape is verified against text nobody wrote.
#
# THE DETECTOR IS THE ORACLE ITSELF, and this row is only measurable at all
# because W1.1 wired that oracle into `make test`. Before this step
# `verify_rxt.py`'s `main()` was invoked by nothing in the tree, so this
# plant would have scored UNDETECTED — not because the corpus was
# insensitive to it, but because the check that reads the corpus never ran.
#
# ITS POPULATION IS NAMED, AND THE DESIGN'S NUMBER IS THE WRONG ONE — the
# same census-vs-mechanism split S197 records one row over, arrived at
# independently here. w1_impl §3.1.1 gives S-C2 a population of 171 corpus
# lines, 90 of them in tests/base/. Both figures are right for "a line
# containing `\x` anywhere", and both are WRONG for this plant: the
# sabotage is in `decode_subject`, which only ever sees the text between a
# case line's quotes, so `\x` in PATTERN text is not in its population at
# all. MEASURED: 115 corpus lines carry a `\xHH` inside a quoted subject,
# 53 of them in tests/base/. A row written against 171 would be asserting
# a number this code cannot produce.
SAB_ID="S195-rxt-hex-escape-literal"
SAB_FILE="tests/harness/verify_rxt.py"
SAB_SUITES="rxtsource"
SAB_DESC="verify_rxt.py's subject decoder turns \\x41 into the literal characters x41 rather than the byte 'A', so every expectation on an escaped subject is checked against the wrong text"
SAB_REACH_POP="tests/backrefs/octal_class.rxt|\\\\x[0-9a-fA-F][0-9a-fA-F]|5"
SAB_COUNT=1
SAB_BEFORE='                out.append(chr(int(hexpart, 16)))'
SAB_AFTER='                out.append("x" + hexpart)   # SABOTAGE S195'
