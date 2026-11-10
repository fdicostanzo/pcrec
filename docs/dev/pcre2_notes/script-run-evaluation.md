# Script runs: how the script-run group and its atomic form are evaluated (PCRE2 10.46)

Source tag pcre2-10.46, paths below under src/ and doc/. Claims are marked READ, DOCUMENTED, INFERRED.

## Summary

- The test is a post-match filter on the whole span the group matched; failure backtracks into the body. READ + DOCUMENTED.
- The test uses Script Extensions data, with special Han combinations and a same-digit-set rule. READ + DOCUMENTED.
- It runs in non-UTF mode too, treating each code unit as a code point. READ.
- The alternative DFA matcher does not support it: the match call fails with a "DFA unsupported item" error. READ + DOCUMENTED.
- Allowed inside lookbehinds and inside assertions used as conditions; nothing refuses it. READ (compile side), INFERRED (run side).

## 1. Match, then filter, backtrack on failure (READ)

- The pattern parser (pcre2_compile.c:4711-4742) treats the long and short spellings as the same group kind. The spellings are the long and short names of each form, as in the question (name table at pcre2_compile.c:569-572). The atomic spelling additionally wraps the body in an atomic group nested INSIDE the script-run group. This matches pcre2pattern.3:2986-2994: the atomic form means a script run whose body is an atomic group; an atomic group placed outside would not stop backtracking into the run.
- In the compiled form the script-run group is an ordinary non-capturing group kind. It is handled like an atomic or plain bracket in the length and first-code-unit analysis (pcre2_compile.c:7344, 7593-7596, 9053; pcre2_study.c:182, 1348; pcre2_auto_possess.c:648).
- At match time (pcre2_match.c:5538-5545) it is entered as a group that records a backtracking point and a frame, exactly as for a group that can match empty. The start position of the group is kept in the parent frame.
- When the matcher reaches the end of that group (pcre2_match.c:6354-6355) it asks the checking routine to judge the text from the saved group start to the current subject position. If the verdict is "not a run", that path returns plain no-match. Otherwise matching continues after the group.
- Consequence: it is a filter on each candidate span. For a non-atomic form, a failing span makes the matcher backtrack into the body and try a different (usually shorter) span, then test again. For the atomic form the body yields a single span, so failure kills the group attempt.
- The check covers only the text matched by the group, not lookarounds or text outside.
- DOCUMENTED warning (pcre2pattern.3:3004-3008, 3717-3718): an accept verb inside the group exits it immediately and bypasses the check. INFERRED: the check lives only at the group end.
- Examples a test could derive (UTF mode, Unicode build):
  - Pattern `(*sr:\w+)` on "paypal" with the second "a" replaced by Cyrillic U+0430: the greedy body takes all six letters, the check fails, the matcher backtracks to five, four, ... down to "p" alone, which is accepted (spans under two characters are always runs). Overall match is "p" at offset 0.
  - Pattern `(*asr:\w+)` on the same subject at offset 0: the body is atomic and gives only the whole span, the check fails, no match at offset 0. The search then tries later start positions.
  - Pattern `(*sr:\S+)\z` on a mixed-script token: the end anchor forces the full span, so backtracking exhausts and the match fails (except for a one-character span reaching the end).

## 2. What property is tested (READ, pcre2_script_run.c:40-340; DOCUMENTED pcre2unicode.3, section "Script runs")

The checking routine takes the start and end of the span.

- A span of fewer than two characters is always accepted, even if the character has unknown script. This is the only case where an Unknown-script character (unassigned, surrogates, or values above U+10FFFF in 32-bit non-UTF mode) is accepted. In longer spans any such character fails the check immediately.
- For longer spans it works character by character, using each character's Script and Script Extensions list from the library's Unicode data tables.
- A character whose Script is Common or Inherited AND which has no Script Extensions list is accepted with anything and does not constrain the run. Examples: ASCII punctuation, space, a plain combining acute accent.
- Every other character contributes a set of allowed scripts: its Script Extensions list plus, unless it is Common or Inherited, its own Script.
- The first constraining character sets the "required" set. Each later one must share at least one script with it, and the required set then shrinks to the intersection. So the intersection of all allowed-script sets must stay non-empty. Example: U+060C Arabic comma (extensions: Arabic, Hanifi Rohingya, Syriac, Thaana) can sit in Arabic or Syriac runs, but U+06D4 (Arabic and Hanifi Rohingya only) cannot join a Syriac run.
- Han special cases: Han combines with Hiragana plus Katakana (Japanese), with Bopomofo, or with Hangul, as virtual scripts. If the first constraining script is Hiragana or Katakana, the run is "Han or Hiragana or Katakana"; Bopomofo gives "Han or Bopomofo"; Hangul gives "Han or Hangul". If only Han has been seen so far, the choice stays pending until a non-Han constraining character arrives: one allowed only with Bopomofo fixes the Bopomofo combination; one allowed with Hiragana and Katakana only fixes the Japanese combination; one allowed with several stays pending; one allowed with none of the four fails. Hangul with Bopomofo with Han is not accepted. Once fixed, each later character must be allowed with Han or that script.
- Digit rule (on top of the script rule, for every character of category decimal digit, Common or not): the span may use digits from only one set of ten consecutive digits. The first digit fixes the set; a digit from a different set fails, even in the same script. The sets are found by binary search over a sorted table of each set's "9" code point, with an ASCII quick path. Examples: ASCII "12" then Arabic-Indic U+0663 fails; ASCII digits and fullwidth U+FF10-U+FF19 do not mix. A span of digits from a single set passes.
- Man page wording says only Script Extensions are used, not the plain Script; the code adds the plain Script for characters that are not Common or Inherited, which matters little because the extension list normally already contains it.
- The Han lists were analysed against Unicode 11.0.0 per a code comment; I did not re-derive them.

## 3. Non-UTF mode (READ)

- The routine takes a flag saying whether to decode multi-unit characters (pcre2_script_run.c:85); the matcher passes its UTF state (pcre2_match.c:6355). Without UTF each code unit is a code point looked up in the same tables. In the 8-bit library, bytes 0-255 are judged as the Unicode code points U+0000-U+00FF; in 16-bit, code units as BMP values; in 32-bit, the values themselves (above U+10FFFF is Unknown).
- Neither UTF nor UCP is needed. The compile condition is Unicode SUPPORT in the build, not an option (pcre2_compile.c:4714, 4743-4746; error text pcre2_error.c:186: script runs require Unicode support). So in a build without Unicode, pcre2_compile errors rather than ignoring the construct.
- INFERRED example (8-bit, no UTF): a span of byte 0xE0 (a Latin letter) and ASCII "a" is a script run; byte 0xE0 (Latin) with a byte that is a non-Latin letter cannot occur in Latin-1 beyond a few (e.g. 0xB5 micro sign is Common), so almost all Latin-1 spans pass. Not tested.

## 4. DFA matcher (READ + DOCUMENTED)

- The group has no handler in the DFA matcher; its entries in the length tables are zero (pcre2_dfa_match.c:181, 261), and the dispatcher's default arm returns the unsupported-item error (pcre2_dfa_match.c:3257-3258). pcre2pattern.3:2996-3000 says script runs are not supported by pcre2_dfa_match because they use the same mechanism as capturing parentheses.
- So pcre2_compile accepts the pattern, and pcre2_dfa_match gives PCRE2_ERROR_DFA_UITEM when it processes the group. INFERRED: the error is raised when the group is reached, not up front; I did not trace for an earlier pre-pass refusal. The atomic form fails too, since its outer wrapper is the script-run group.

## 5. Lookbehinds and conditions

- Lookbehind (READ): the fixed-length analysis walks into script-run groups like any non-capturing group (pcre2_compile.c:9263, 9708, 9956). Nothing rejects the construct, so a lookbehind containing a script run with a body of computable length compiles. The run check is applied to the span the body matches. INFERRED, not traced through the lookbehind matching frames.
- Conditions (READ, INFERRED): a script run is not itself a condition kind (conditions are group references, recursion tests, DEFINE, version tests, and assertions). It may appear inside an assertion used as a condition, or in the yes/no branches; compile sites treat it as an ordinary group.
- JIT (not asked): it has a JIT path calling the same routine (pcre2_jit_compile.c:9321-9350). Not checked in detail.

## Not checked

- Exact Unicode data table contents and per-character results.
- Test data for lookbehind script runs.
- ChangeLog: the feature was introduced as item 8 in ChangeLog:1316 (the 10.33-era notes).

## Cited by

(none yet; the manager fills this in when code leans on the note)
