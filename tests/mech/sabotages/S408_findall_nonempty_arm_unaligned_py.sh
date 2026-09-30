# S408 — [K75] THE SAME PLANT IN THE PYTHON LEG (verify_rxt.py's `_findall_protocol`).
#
# `verify_rxt.py` carries its own transcription of §3.1's loop for `mc` lines
# (leg C); K75 gave its non-empty arm the same continuation-byte skip
# `<prefix>_next_pos(end - 1)` spells. This row disables the skip, so the python
# count on `a` over `a\x80a` reads 1 (it searches from the stray, and python's
# `re` happily matches nothing before the next `a`... and, for `.`, would match
# the stray itself and count 3) where the fixture says 2.
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
