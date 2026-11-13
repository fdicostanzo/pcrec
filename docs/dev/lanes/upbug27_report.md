# upbug27 — is the lost final empty match after a trailing ill-formed unit a PCRE2 bug? (2026-11-12, sonnet)

## STATE AT HANDOFF
Done; verdict BUG, not previously reported. Draft at `docs/dev/lanes/upbug27_issue.md` (17 lines), U27 row appended to
`docs/dev/upstream_issues.md`. Nothing filed or commented on GitHub. Rulings file empty (no entries applied). No src/memfn edits.
Scratch: `/var/tmp/pcrec-pcrec/scratch/upbug27/` (nm.c, e.c, f.c, old.c, binaries).
Manager to do: file the issue, then add to `docs/dev/upstream_tracked.tsv` the line
`https://github.com/PCRE2Project/pcre2/issues/<N>	U27	<filed date>` (tab-separated: URL, row id, date) and flip the U27 status.

## FINDINGS
1. **Premise holds.** 10.49 pcre2test `/x*/utf,match_invalid_utf,g` on `a\xff`: 2 matches (0, 1); `\xff`: 1; `ab`: 3; `a\xc3\xa9`: 3;
   `\xffb`: 3. 10.46 (classic documented loop, my C driver against the system 10.46 lib): `a\xff` 3, `\xff` 2. `pcre2_substitute` global
   via the or49disp probe: 10.46 `[]a[]\xff[]`, 10.49 `[]a[]\xff`. This build has only 8-bit support (no 16/32 pcre2test); without
   MATCH_INVALID_UTF the subject is rejected up front (-23), so the question does not arise. 10.46 pcre2test is not on the box (10.49's
   uses `pcre2_next_match`, absent in 10.46).
2. **Root cause is not #945 and not the 10.47 advance change.** #945 is a JIT-only fix (ChangeLog 10.48 item 27); this build has no JIT.
   The library's `pcre2_match` is IDENTICAL on 10.46 and 10.49 for the relevant calls. The difference is the caller: 10.47 added
   `pcre2_next_match()` (ChangeLog 10.47 item 11), used by pcre2test /g and `pcre2_substitute`. After the empty match `[1,1]` on `a\xff` it
   returns offset 1 + NOTEMPTY_ATSTART; `pcre2_match` then returns NOMATCH on BOTH versions, where the old loops retried one character on
   and found `[2,2]`. Documented contract of `pcre2_next_match` (pcre2api): "Returning 1 does not imply that there is another match", but
   the empty match at 2 exists.
3. **Core inconsistency (the bug), same on 10.46 and 10.49** (C driver, UTF|MATCH_INVALID_UTF, 8-bit):
   - `\z` on `a\xff`: offset 0 NOMATCH, offset 1 NOMATCH, offset 2 `[2,2]`. Same for `$`, `(?=)` and `x*` with NOTEMPTY_ATSTART at 1.
   - `\z` on `a\xc3` (truncated sequence): NOMATCH from 0; on `a\xc3\xa9` (valid): `[3,3]`; `ab` from 1 with NOTEMPTY_ATSTART: `[2,2]`.
   - Mid-subject ill-formed (`\xffb`, off 0 NOTEMPTY_ATSTART) finds `[1,1]`; only a TRAILING ill-formed unit blocks the end position.
   So the bump-along never reaches end-of-subject past a trailing ill-formed unit.
4. **Documentation says it should match.** pcre2unicode "MATCHING IN INVALID UTF STRINGS": a start offset on an invalid sequence is
   "skipped, and the match starts at the next valid UTF character, or the end of the subject"; invalid sequences are "a barrier", but the
   subject end is not a barrier for `\z`/`$` (the same page: internal boundaries are not line ends; #343, closed, fixed `A\z` matching
   BEFORE an invalid unit, the opposite error). Nothing documents the end position as unreachable after a trailing invalid unit.
5. **Existing reports**: searched issues/PRs (open and closed) for next_match, MATCH_INVALID_UTF, `\z`, NOTEMPTY_ATSTART, trailing/end of
   subject, substitute: none. Nearest: #343 (`A\z` over a MIDDLE invalid unit, fixed 2023), #1054/#944/#945 (JIT), #588 (always validate UTF).
6. **Verdict: BUG** (inconsistent: valid trailing char, mid-subject invalid unit and offset-at-end all find the end match; documented
   "or the end of the subject"; present before 10.47 but exposed to global loops by `pcre2_next_match`). The issue draft reports the
   `pcre2_match` behaviour and the `pcre2_next_match`/substitute symptom, and asks (not asserts) which side should change.
7. **pcrec**: no change; pcrec keeps the 10.46/Perl-shaped answer, the subst/d27 cells remain a recorded oracle difference
   (or49disp finding 6). Proposed id: U27; tracked.tsv line shape above.
