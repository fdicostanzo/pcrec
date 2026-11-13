TITLE: With PCRE2_MATCH_INVALID_UTF, a subject ending in an ill-formed unit loses the final empty match: pcre2_match() cannot find an end-of-subject match from an earlier offset (`\z`, `$`, `x*` after NOTEMPTY_ATSTART)

Hello, and thank you for PCRE2.

With PCRE2 10.49 (release tarball, default configure, interpreter, no JIT), under `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF` a match that is only possible at the very end of the subject is not found when the subject ends in an ill-formed unit, unless the start offset is already the end:

```
/\z/utf,match_invalid_utf
    a\xff               No match      (expected 0: at offset 2)
    a\xff\=offset=1     No match      (expected 0: at offset 2)
    a\xc3\xa9           0: at offset 3   (valid trailing character: found)
```
pcre2unicode says an offset on an invalid sequence "is skipped, and the match starts at the next valid UTF character, or the end of the subject". `$` and `(?=)` after `NOTEMPTY_ATSTART` behave the same way.

It is visible in global matching since 10.47 added `pcre2_next_match()`: after the empty match at offset 1 of `a\xff` it asks for offset 1 with `NOTEMPTY_ATSTART`, `pcre2_match()` returns NOMATCH, and the final empty match at offset 2 is lost. `pcre2test` `/x*/utf,match_invalid_utf,g` on `a\xff` gives 2 matches (offsets 0, 1); 10.46's loop gave 3 (0, 1, 2). `pcre2_substitute()` with `SUBSTITUTE_GLOBAL` and `[$0]` gives `[]a[]\xff` on 10.49, `[]a[]\xff[]` on 10.46. `ab`, `a\xc3\xa9` and `\xffb` keep their trailing/following empty match.

I think `pcre2_match()` itself is unchanged between 10.46 and 10.49 (same results with both libraries); only the callers' retry differs. I found no ChangeLog entry or open/closed issue for this (#343 is a different `\z` case). Thanks for taking a look.
