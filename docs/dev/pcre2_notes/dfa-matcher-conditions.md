# The alternative (DFA) matcher: conditional groups, lookaround, unsupported items

Tag pcre2-10.46. Main file: src/pcre2_dfa_match.c. Man page: doc/pcre2matching.3.

## 1. Conditional groups

The matcher handles a conditional group at the moment a path reaches it (READ, pcre2_dfa_match.c:2831-2932). The condition kind was settled at compile time, so the DFA matcher only looks at the compiled kind.

Accepted:
- Recursion test with no number, `(?(R)yes|no)` (and `(?(R0)...)`, which the compiler treats the same, pcre2_compile.c:6528-6532). It is true when the matcher is currently inside any recursion or subroutine call, false otherwise (READ, pcre2_dfa_match.c:2876-2883). It cannot tell which group is being recursed into.
- DEFINE, `(?(DEFINE)...)`: always false, so the "no" side (nothing, since DEFINE allows only one branch) is taken and the body is skipped (READ, :2864-2866; the compiler marks it always-false, pcre2_internal.h:1734, pcre2_compile.c:6592-6595 plus the later conversion mentioned at pcre2_internal.h:1767).
- VERSION, `(?(VERSION>=10.4)...)`: the compiler decides true or false at compile time (pcre2_compile.c:6640-6643), so the DFA matcher just takes the matching side (READ, :2869-2870 for the always-true kind).
- Assertion conditions, `(?(?=...)yes|no)`, `(?(?!...)...)`, `(?(?<=...)...)`, `(?(?<!...)...)`; and the degenerate negative assertion that always fails, which the compiler turns into a bare fail item and is treated as an always-false condition (READ, :2864, :2882-2926).
- If auto-callout is on, a callout sits between the group opener and an assertion condition; the matcher runs it and skips it first (READ, :2841-2851).

Rejected, at match time (not at compile time), when a path actually reaches the conditional:
- Group-set tests by number `(?(1)...)`, by name `(?(name)...)`, `(?(<name>)...)`, `(?('name')...)`, including the relative forms; the duplicate-name variants too. The code calls these "back reference conditions".
- Recursion tests for a specific group, `(?(R1)...)`, `(?(R&name)...)`, i.e. any recursion test whose number is not "any"; and recursion tests on a duplicated name.
All of these return the error PCRE2_ERROR_DFA_UCOND (-40), whose message reads "backreference condition or recursion test is not supported for DFA matching" (READ, :2857-2860, :2879; message at pcre2_error.c:264; public name in pcre2.h and pcre2api.3:4426). DOCUMENTED: pcre2matching.3 lines ~149 list "conditional expressions that use a backreference as the condition or test for a specific group recursion" as unavailable.
INFERRED: because the check is at match time, a pattern with such a condition compiles fine and only fails if some path reaches that group; a match that never gets there (for example the group is in an alternative never tried, or the subject is rejected earlier) does not report the error. Not tested by me.

Examples (derive tests): pattern `(a)?(?(1)b|c)` on "ab": error -40, even though the standard matcher answers "ab". Pattern `(?(R)a|b)` on "b": matches "b". Pattern `(?(?=a)ab|c)` on "ab" matches "ab"; on "c" matches "c". Pattern `(?(DEFINE)(?<x>a))b` on "b": matches "b" (the DEFINE body is never entered directly).

## 2. Lookaround and assertion conditions

READ (:2786-2827, :2899-2926). For a lookahead or lookbehind (positive or negative) reached at the current subject position, the matcher makes a separate, nested call of itself on just the assertion body, starting at the current position, with its own small offset vector and its own slice of the workspace (taken from a spare recursion workspace that can be grown; running out gives the workspace-size error). It also passes the same recursion depth counter and the shared match counters (so the match limit and depth limit still apply).
- Only the success/failure of that nested call is used. Any non-negative result means "the body matched somewhere"; the match lengths and any captured text are discarded. Captures inside an assertion are therefore ignored (in fact this matcher captures nothing at all; INFERRED from the documented absence of captured substrings, pcre2matching.3 ~140).
- A negative result other than plain no-match (an error such as the workspace or limit errors, or the unsupported-item error from inside the body) is returned immediately as the whole match's error (READ, :2824 and :2923).
- For a positive assertion, success continues the main path after the assertion at the same subject position (consuming nothing); for a negative assertion, the path continues only if the nested call found no match. A failed condition for an assertion condition takes the "no" branch (or ends the path if there is none); a satisfied one takes the "yes" branch (READ, :2924-2926).
- Lookbehinds: the nested call is made from the current position and the compiled lookbehind body steps backwards by its fixed length itself; I did not trace that code (top of the main routine, near :594, is where the backward step is handled). NOT CHECKED in detail.
- DOCUMENTED: pcre2matching.3 ~87 says the scan is single-pass except that at a lookaround the characters ahead or behind are inspected independently.
- Consequence: the assertion body is run in full, to find any match, not just the first; the answer needs only existence.

## 3. Unsupported features

Any compiled item the main loop has no case for lands in a catch-all that returns PCRE2_ERROR_DFA_UITEM (-42), message "pattern contains an item that is not supported for DFA matching" (READ, :3256-3258; message at pcre2_error.c:266). Again this happens at match time when a path reaches the item. READ that the per-item length tables list no handling for backreferences (plain, caseless, by name), script runs, accept, assert-accept, the keep-out reset item for `\K`, mark, prune, commit, skip, then and their argument forms (pcre2_dfa_match.c:175-276, tables marked zero) and that the main loop has no cases for them (checked by grep: none of those items appears in the loop).
- Backreferences `\1`, `\k<n>`, `(?P=n)`: refused (-42). DOCUMENTED, pcre2matching.3 ~147.
- `(*ACCEPT)`: refused (-42). `(*COMMIT)`, `(*PRUNE)`, `(*SKIP)`, `(*THEN)`, `(*MARK:x)` and their argument forms: refused (-42). The one verb supported is `(*FAIL)`/`(*F)`, which behaves as a failing negative assertion (READ, :2780-2784; DOCUMENTED, pcre2matching.3 ~169).
- `\K`: refused (-42); documented as unsupported because paths disagree about the start (pcre2matching.3 ~157).
- Script runs `(*script_run:...)`, `(*sr:...)`, atomic script runs: refused (-42). DOCUMENTED, ~151. Scan-substring assertions also unsupported (documented ~153; code not examined).
- Supported by contrast: atomic groups and possessive repeats (via nested calls), recursion/subroutine calls (via nested call; a loop guard gives PCRE2_ERROR_RECURSELOOP, and running out of internal offsets in a call gives PCRE2_ERROR_DFA_RECURSE, -39; READ :2934-3030), callouts (with fixed capture_top and capture_last values, documented).
- Also noted by the man page: `\C` unsupported in UTF mode; PCRE2_MATCH_INVALID_UTF refused with its own error (pcre2matching.3 ~162-170, pcre2_error.c:295).

Examples: `(a)\1` on "aa": -42. `a(*ACCEPT)b` on "ab": -42. `a\Kb` on "ab": -42. `a(*COMMIT)b`: -42. `a(?!b)` on "ac": matches "a". `a(*FAIL)|ab` on "ab": matches "ab".

## Not checked
Exact behaviour of lookbehind stepping inside the DFA loop, partial-match interaction with assertions, whether the compiler rejects any of these earlier in special options, scan-substring code.

## Cited by
(none yet; the manager fills this in when code leans on the note)
