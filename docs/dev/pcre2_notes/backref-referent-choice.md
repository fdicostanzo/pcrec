# Backreference referent choice: duplicate names, branch reset, unset groups, caseless scope

Question: for a backreference to a duplicated group name (PCRE2_DUPNAMES or
(?J)), or to a group number inside a (?| branch reset, which capture does the
interpreter (pcre2_match) compare against when several of those groups are set
or some are unset? Under PCRE2_MATCH_UNSET_BACKREF, does an unset referent match
empty in every case, including a duplicate name with a mix of set and unset
groups? And does caseless matching follow the backreference's own (?i) scope or
the referent's?

Source: tag pcre2-10.46, files pcre2_match.c, pcre2_compile.c, and the man pages
doc/pcre2pattern.3 and doc/pcre2api.3.

## 1. Branch reset: a number names one slot, so there is nothing to choose

- READ: a numbered reference (and a named reference whose name is not
  duplicated) compiles to the plain single-group reference item carrying just
  the group number (pcre2_compile.c:7940-7963). At match time it looks up that
  one capture slot (pcre2_match.c:5154-5159). Inside (?| every alternative
  writes the same numbered slot. So \1 compares against whatever group 1 holds
  on the current match path: the value left by whichever alternative last
  closed it. A failed alternative's capture is not kept, because the capture
  vector belongs to the backtracking frame (INFERRED from the frame-local
  capture vector used throughout pcre2_match.c; I did not trace the restore
  path itself).
- READ: a name repeated inside a branch reset at the SAME number, such as
  (?|(?<a>x)|(?<a>y)), is not a duplicate. During parsing, a second occurrence
  of a name that has the same number is dropped silently, before the
  PCRE2_DUPNAMES check, so this needs neither PCRE2_DUPNAMES nor (?J)
  (pcre2_compile.c:5556-5580). A reference to it is the plain numbered
  reference, as above.
- READ: two different names for the same number are a compile error, so a
  branch reset cannot give one number two names (pcre2_compile.c:5577-5581).

Examples (INFERRED from the above; a test would confirm):
- (?|(a)|(b))\1 matches "aa" and "bb", and does not match "ab" or "ba".
- (?|(?<n>a)|(?<n>b))\k<n> behaves the same, with or without (?J).

## 2. Duplicate names: the first SET group in pattern order

- DOCUMENTED (pcre2pattern.3:2105-2112): the groups that share the name are
  checked in the order in which they appear in the pattern, and the first one
  that is set is used. The example given is (?J)(?:(?<n>foo)|(?<n>bar))\k<n>,
  which matches "foofoo" and "barbar" but not "foobar" or "barfoo".
- READ, compile side: whether a name is "duplicated" is decided from the list of
  all names gathered in the parse pass over the whole pattern, so a reference
  written BEFORE the duplicate groups still gets the duplicate-name form
  (pcre2_compile.c:6936-6959). That form records where the name's run of entries
  starts in the name table, and how many entries share it
  (pcre2_compile.c:6987-7008; the run is found by the helper at
  pcre2_compile.c:5862-5907).
- READ, table order: the name table is kept in alphabetical order. A
  duplicate is inserted AFTER the entries that already carry its name, so
  same-named entries keep pattern order. In the ordinary case (no branch reset)
  that is also ascending group number (pcre2_compile.c:9128-9167; it is filled
  in the order the names were found, pcre2_compile.c:10737-10738).
- READ, match side (pcre2_match.c:5136-5152): the interpreter walks the
  same-named entries in table order and stops at the first group whose capture
  is set. The test for "set" is that the group number is below the current
  highest-used capture boundary AND its start offset is not the unset marker.
  That group's slot becomes the referent. The choice is made once, when the
  reference item is entered, before any repetition. Every repetition of a
  quantified duplicate-name reference, such as \k<n>{2,}, uses that same group
  (pcre2_match.c:5161 onward).
- READ: if NO same-named group is set, the walk runs off the end. The referent
  slot is then the LAST same-named entry, which is unset, and handling continues
  as for an unset group (section 3).
- Subroutine calls by duplicate name are a different rule (the first
  occurrence, set or not). DOCUMENTED pcre2pattern.3:2114-2116 and READ
  pcre2_compile.c:6950-6957. They are not a backreference and are mentioned only
  so the two are not confused.

Examples (the first is DOCUMENTED; the rest are INFERRED):
- (?J)(?<n>a)?(?<n>b)\k<n> on "bb": the first n is unset and the second holds
  "b", so the reference uses "b". The pattern matches "bb".
- (?J)(?<n>a)(?<n>b)\k<n> on "aba": both are set. The first in pattern order
  wins, so the reference is "a". It matches "aba" and does not match "abb".
- (?J)(?:(?<n>x)|(?<n>y))\k<n> on "yy" matches; on "xy" there is no match.

## 3. Unset referents and PCRE2_MATCH_UNSET_BACKREF

- DOCUMENTED (pcre2api.3:1826-1833, pcre2pattern.3:2519-2524): by default a
  reference to an unset group fails. With the option, it matches an empty string.
- READ: the single comparison routine treats a referent as unset if its number
  is at or past the highest-used capture boundary, or its start offset is the
  unset marker. Then it succeeds with length zero if the option is set, and fails
  otherwise (pcre2_match.c:362-383). The option is read from the compiled
  pattern's options.
- READ, quantified references (pcre2_match.c:5201-5218): for an unset referent,
  the quantified reference matches nothing and carries on if the minimum is zero
  OR the option is set. Otherwise the minimum loop fails on the first try. A SET
  referent of zero length likewise matches any number of times at no cost.
- The duplicate-name answer: the option does NOT make a mixed set produce empty.
  Unset same-named groups are skipped by the walk in section 2, so as long as at
  least one same-named group is set, the reference compares against the first
  set one's text, whatever the option. Only when ALL same-named groups are unset
  does the option matter: the reference then matches empty with the option, and
  fails without it (READ, pcre2_match.c:5145-5150 together with :375-382).

Examples (INFERRED; with PCRE2_MATCH_UNSET_BACKREF unless stated):
- (a|(bc))\2 on "a": with the option it matches "a" (\2 is empty); without it,
  no match. The pattern is DOCUMENTED, the outcome INFERRED.
- (\1)(a) on "a" matches with the option (DOCUMENTED pcre2api.3:1830-1832).
- (?J)(?:(?<n>a)|(?<n>b))?c\k<n> on "c": no n is set, so with the option it
  matches "c", and without it there is no match.
- (?J)(?<n>x)?(?<n>y)\k<n> on "y" followed by end of subject: the second n holds
  "y", so the reference needs another "y". With the option it is still no match
  on "y" (empty is NOT tried), and it matches "yy".

## 4. Caseless: the backreference's own scope decides

- DOCUMENTED (pcre2pattern.3:2493-2499): case sensitivity is whatever is in
  force at the backreference. ((?i)rah)\s+\1 matches "rah rah" and "RAH RAH" but
  not "RAH rah", even though the group itself matched caselessly.
- READ: at compile time, the reference chooses its caseless or caseful form from
  the options in effect at the reference's own position. This holds for both the
  numbered and the duplicate-name forms (pcre2_compile.c:7001, :7957). In the
  caseless form, the reference also stores two extra flags taken from the extra
  options in effect at that point: PCRE2_EXTRA_CASELESS_RESTRICT and
  PCRE2_EXTRA_TURKISH_CASING (pcre2_compile.c:7002-7008, :7958-7963). The
  referent group's options play no part.
- READ: at match time, the comparison uses those stored flags. In UTF or UCP
  mode it walks the reference text character by character with Unicode case
  folding (pcre2_match.c:385-420 and following). Note that the subject may use a
  different number of code units than the captured text.

Examples: (?i:(a))\1 on "aA" gives no match; (a)(?i)\1 on "aA" matches; in
both, the group's own case rules do not matter (INFERRED from the DOCUMENTED
rule).

## Not checked

The JIT and pcre2_dfa_match (the DFA matcher does not support backreferences
anyway). How the capture vector is restored on backtracking inside a branch
reset (assumed from the per-frame design). Partial-match return paths of the
comparison. Behaviour of conditions that test a duplicate name, such as (?(<n>)...).

## Cited by

(none yet; the manager fills this in when code leans on the note)

## Confirmed against libpcre2 10.46 (manager, 2026-11-01)

Run through libpcre2-8 with default options: `(a)(?i:\1)` matches "aA" (the backreference follows its own caseless scope); `(?J)(?:(?<n>a)|(?<n>b))\k<n>` on "bb" matches with the first group unset and the second (0,1).
