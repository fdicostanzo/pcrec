# upbug28: PCRE2 callout start_match after \K

## STATE AT HANDOFF
Done. Verdict: ALREADY REPORTED AND FIXED UPSTREAM (stop rule). Nothing drafted,
no upstream_issues.md row, nothing for the manager to file. Only this report and
the lanes history index line were added. No rulings file was present. Driver and
scratch are under `$PCREC_TMPDIR/scratch/upbug28/` (d.c, binaries d10.46, d10.49).

## FINDINGS
1. Doc sentence (pcre2callout, "The callout function" section; same text in the
   `pcre2.txt` bundle, 10.49 install share/doc): "The start_match field
   normally contains the offset within the subject at which the current match
   attempt started. However, if the escape sequence \K has been encountered,
   this value is changed to reflect the modified starting point." pcre2test
   documents no start display: "Output from pcre2test does not indicate the
   [callout_flags] bits unless callout_extra is set", and its callout lines
   show only the `^` current position, so pcre2test cannot show start_match.
2. Reproduction (C driver, interpreter, no JIT, via pcre2_set_callout; start_match / current_position):
   - `a\K(?C1)b` on `ab`: 10.46 and 10.49 both start_match=0, pos=1; ovector[0]=1 (\K itself works).
   - `ab\K(?C1)`: start_match=0, pos=2; ovector 2..2.
   - `(a\K(?C1)b)(?C2)`: C1 and C2 both start_match=0; ovector 1..2.
   - `x*a(?:b\K(?C1)c)` on `xxabc`: start_match=0; ovector 4..5.
   Identical on 10.46 and 10.49; the doc promise (start_match = 1 after \K) is not met.
3. Verdict: library BUG (interpreter only; JIT already updated it), not a doc
   error and not a misread. Existing report: PCRE2Project/pcre2 issue #1040
   ("\K produces inconsistent behaviour with pcre2_callout_block->start_match
   when not using JIT", opened 2026-10-13, closed 2026-10-23), fixed by merged
   PR #1043 "Fix interpreter callout start_match after \K" (touches
   src/pcre2_match.c, testinput2/testoutput2, ChangeLog). The fix postdates the
   10.49 release (2026-09-28), so it should ship in the next release; it is not
   in 10.49 (reproduced above).
4. Consequence for pcrec/andspike: oracle spans via callout start_match are
   wrong after \K on interpreter builds up to at least 10.49; derive the match
   start from ovector[0] (or JIT) until a release containing #1043 is pinned.
   Searches for other start_match/\K issues found none beyond #1040.
