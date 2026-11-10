# scan-substring-anchoring: how (*scan_substring:(GROUPS)PATTERN) matches PATTERN

Tag pcre2-10.46. Paths under src/ and doc/ of the reference tree.

## Where decided
- Documentation: doc/pcre2pattern.3:2886-2935 (DOCUMENTED).
- Run-time: the match-loop case for the scan-substring assertion, pcre2_match.c:5735-5862 (READ).
- Its end-of-group handling (the "assertion body finished" path): pcre2_match.c:6333-6348 (READ).
- Compile: the parser turns the group list into a sequence of group-reference tests placed at the front of the assertion; pcre2_compile.c:6457-6460, 6473-6623 (READ). Quantifier handling pcre2_compile.c:7325-7345 (READ). Lookbehind-length pre-pass pcre2_compile.c:9945-9960 (READ).

## Answers
1. Start anchored: YES. READ: the matcher moves the current position to the start of the chosen group's capture and runs the body from there, with no search loop, so there is no bump-along (pcre2_match.c:5810-5819). DOCUMENTED: "always anchored" (pcre2pattern.3:2917-2920).
2. End: NOT anchored at the end. The body may match a prefix; it need not consume the whole substring. READ: the code only temporarily lowers the end-of-subject limit to the end of the capture (5811-5813); nothing demands reaching it. So `(a+)(*scs:(1)a)` on `aaa` succeeds. Effects of the lowered end: `$`, `\Z`, `\z` match at the substring end (DOCUMENTED 2920-2922); the not-end-of-line option is cleared inside (5813). The subject START is not reset, so `^` matches only if the substring is at subject start, and lookbehind can look at text before the substring (DOCUMENTED 2922-2926). To require whole-substring, write `\z` or `$` at the end of PATTERN. Example: `(\w+)(*scs:(1).+rh)` pattern from the man page finds words containing "rh" not at the start.
3. Several groups: checked in the order listed; the FIRST one that is set is scanned, only that one (READ 5755-5800: loop stops at first set; later entries are only skipped over). A name shared by several groups (dupnames) expands to all of them in numerical (name-table) order, same rule (READ 5767-5781; DOCUMENTED 2908-2910). "Set" means the capture slot is within the current used-offset range and not unset (5762, 5777). Relative numbers are resolved at compile time.
4. None set: the assertion FAILS (no match at that point) (READ 5767 falls to no-match when the list ends with nothing found; DOCUMENTED 2910). It is not a negative assertion; no negated form exists (INFERRED, none seen in compile).
5. Atomic / captures: it behaves like an ordinary positive assertion (an atomic one): once the body matches once, the first success is accepted, the code skips past the alternatives and continues; the matcher does not backtrack into the body (READ 5816-5855). Note it first tries each alternative of the body in order, like any assertion. Captures set inside the body are copied out and remain visible afterwards and in later back references (READ 5820-5826; DOCUMENTED 2933-2935). Mark data is also propagated. On failure captures revert. When later failure unwinds across it, the saved end-of-subject is restored first (6333-6348), so outer matching sees the true subject end.
6. Quantified: yes. The compile step lists it with the other assertions that Perl-style repetition replicates (pcre2_compile.c:7342); `{1,1}` is a no-op, `?`, `*` etc. work as for lookahead assertions (INFERRED from sharing that branch; I did not trace each count form; a zero minimum makes it optional). Lookbehind: it may appear inside a lookbehind: the length pre-pass treats it like a lookahead, contributing nothing to the fixed length (READ 9945-9960; INFERRED for the exact inner behaviour). Its body may contain its own lookbehind into text before the substring (DOCUMENTED). Not supported by the DFA matcher (DOCUMENTED 2889-2890).

## Not checked
JIT behaviour; callout/mark details; exact error cases for out-of-range group numbers (compile reports a bad reference, pcre2_compile.c:6610-6615 READ for numbers); quantifier expansion for counts above 1.

## Cited by
(none yet; the manager fills this in when code leans on the note)
