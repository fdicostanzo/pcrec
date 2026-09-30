# S408 — [K75] THE SAME PLANT IN THE PYTHON LEG (verify_rxt.py's `_findall_protocol`).
#
# `verify_rxt.py` carries its own transcription of §3.1's loop for `mc` lines
# (leg C); K75 gave its non-empty arm the same continuation-byte skip
# `<prefix>_next_pos(end - 1)` spells. This row disables the skip, so python
# resumes ON the stray: the `a` cells are unmoved (python's `re` steps over a
# byte that is not an `a` for free) but `.` over `a\x80a` reads 3 (it matches
# the stray itself) and `a|` over it reads 4, against the fixture's 2 and 3.
#
# THE DETECTOR is the same rxtsource check as S407's, its `verify_rxt.py` half.
SAB_ID="S408-findall-nonempty-arm-unaligned-py"
SAB_FILE="tests/harness/verify_rxt.py"
SAB_SUITES="rxtsource"
SAB_DESC="verify_rxt.py's find-all transcription resumes after a NON-EMPTY match at its raw end without the continuation-byte skip next_pos(end - 1) spells, so python and C disagree on a match ending before a stray continuation byte (K75)"
SAB_REACH_POP="tests/rxtsource/fixtures/mc_illformed_utf8.rxtin|^mc .a.*\\\\x80|6"
SAB_COUNT=1
SAB_BEFORE='            pos = en
            if encoding == '"'"'utf8'"'"':
                while pos < n and 0x80 <= ord(subj[pos]) <= 0xBF:
                    pos += 1
        else:'
SAB_AFTER='            pos = en   # SABOTAGE S408
        else:'
