# compatfacts: look-alike fold facts
Script: /tmp/claude-1001/compatfacts/facts.py  Raw output: /tmp/claude-1001/compatfacts/out.txt
Method: vendored UnicodeData.txt (16.0.0) parsed for <tag> decompositions (3832 compat-mapped code points);
python3 unicodedata is 16.0.0 (matches; 0 tag mismatches, same 3832 count). Full NFKC via unicodedata.normalize.
"Maps to X" = NFKC(cp)==X and cp!=X. Counts exclude the letter itself.

## 1. Code points whose NFKC is exactly one ASCII char
Totals: 1033 (+ self). Uppercase 474 (17-20 each, mean 18.2), lowercase 449 (16-20 each), digits 110 (11 each).
By tag: font 779, circle 64, wide 62, super 60, sub 27, square 26, compat 15.
Per-letter (see out.txt for all 62): f=16 (font13,circle,wide,super), F=18, a=18, i=20, y=16, Z=17, each digit=11 (font7,super,sub,circle,wide).
Note: 1126 single->single ASCII sources overall (Q3) vs 1033 for letters+digits; the other 93 are punctuation/space/symbols.
Note: Kelvin U+212A and U+017F are canonical/case, not <compat>; they enter via Q4, not Q1.

## 2. One-to-many ASCII (NFKC result is a multi-char all-ASCII string): 308
compat 156 (Ĳ->IJ, ǉ->lj, ﬁ->fi, ㎏... ), square 102 (㋎->eV, ㍱->hPa, ℡ squares like TEL), circle 43 (⑩->10..⑳->20),
super 5 (℠->SM, ™->TM, 🅪->MC), vertical 2 (︙->...). Parenthesized/period forms (⒜->(a), ⒈->1.) are <compat> and counted in the 156.
Plus 833 multi-char results involving non-ASCII (¼->1⁄4, ¨-> U+0020 U+0308 ...).

## 3. Beyond ASCII
Compat-mapped code points total: 3832 (tags: font 1230, compat 720, square 286, super 249, circle 240, final 240, isolated 238,
initial 171, narrow 122, wide 104, medial 82, sub 64, vertical 35, small 26, fraction 20, noBreak 5).
Single non-ASCII targets: 1565 sources -> 811 distinct targets (Arabic 382 sources [presentation forms], CJK 331, Greek 309
[math alphabets, symbols], Hangul 175, Latin 121, Katakana 105 [halfwidth], Cyrillic 65, Hebrew 13, arrows/nabla ~25).
Every compat-mapped cp has NFKC != itself (0 identity).

## 4. With case folding (?i)
NFKC_Casefold is NOT in the vendored files (only CaseFolding.txt, Scripts.txt, etc; no DerivedNormalizationProps.txt, which carries NFKC_CF mappings
and Default_Ignorable removals). Not needed to count: computed as NFKC(cf(NFKC(cf(NFD(x))))) with Python casefold (C+F), omitting the
default-ignorable removal step (affects only ignorables, which never map to a letter).
Set size per letter (cps whose NFKC_CF form is that single letter, INCLUDING the ASCII upper and lower themselves):
a38 b36 c39 d40 e38 f36 g36 h37 i41 j38 k38 l40 m39 n37 o38 p37 q36 r38 s37 t37 u37 v39 w36 x38 y35 z35 (total 976); digits 12 each.
f: 34 non-ASCII: U+1DA0 U+2131 U+24BB U+24D5 U+A7F3 U+FF26 U+FF46 U+1CCDB U+1D405... (math alphabets) U+1F135.
Case-only entries already in plain (?i): k also gets Kelvin U+212A, s gets U+017F (long s). Those are existing simple-case-fold facts.
Alternative cheaper route: compat set of upper+lower letter (Q1 sets union) gives nearly the same set.

## 5. Symmetry / chains
NFKC is idempotent over all 3832 (0 unstable); 0 NFKC targets are non-stable.
One-step <compat> mappings that contain a character itself compat-mapped: 112 sources (e.g. U+3378 ㎸ -> d m U+00B2; U+3395 -> U+03BC U+2113),
114 by the other measure; the *recursive* mapping resolves them. Thus the UnicodeData.txt single-step table is not enough: need the recursive closure
(or NFKC itself). Mappings are many-to-one; a char's set is NOT symmetric (f matches ｆ but ｆ does not need to match "f" in pattern direction unless the pattern is normalized too).

## 6. UTF-8 cost of the class for one letter
Columns: code points, ranges, UTF-8 byte-range sequences (standard utf8-ranges split), distinct lead bytes.
compat set + self: f 17/17/17/5; a 19/19/19/6; k 18/18/18/5; e 19/19/19/5; A 19/19/19/5; digit 0 12/12/12/4.
With (?i) NFKC_CF set (both cases + compat): f 36/36/36/7; k 38/38/38/6; s 37/37/37/7.
All 52 letters union (compat only): 923 cps -> 74 ranges, 83 sequences, 9 lead bytes (math alphabets are runs, so union compresses).
Interpretation: a per-letter class is ~17-40 disjoint 1-4 byte sequences, mostly 4-byte (U+1Dxxx math) and 3-byte (U+FFxx, U+24xx, U+2xxx), 2-byte few (ª U+00AA is o?-type, U+02E2); lead bytes 0xC2/0xC3/0xCA.., 0xE1, 0xE2, 0xEA, 0xEF, 0xF0.
Multi-char sources (Q2: ﬁ->fi etc.) are not in these counts; they would be alternatives of whole sequences.

## 7. Survey (verified by fetch unless marked)
- UTS #18: only canonical equivalence is a conformance item (RL2.1, NFD-based; "difficult"); suggests normalizing text/pattern to NFD/NFC; no compatibility-equivalence requirement; RL1.5 simple case-insensitive required, RL2.4 full case folding. https://www.unicode.org/reports/tr18/ (last 32K chars unread)
- ICU regex: no normalization; UREGEX_CANON_EQ not supported. https://unicode-org.github.io/icu/userguide/strings/regexp.html
- Perl: no normalization; "nothing in Perl 5 that ignores the differences"; normalize both with Unicode::Normalize (NFD). https://perldoc.perl.org/perlunicode
- Python `regex`: only case folding (FULLCASE); nothing on normalization. https://pypi.org/project/regex/ (first 100K chars of page read)
- Java: CANON_EQ (canonical only, perf/memory warning); UNICODE_CASE; nothing on compatibility. https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/Pattern.html
- Rust regex crate (ripgrep's engine): simple case folding only; no normalization mentioned. https://docs.rs/regex/latest/regex/ ; ripgrep specific: nothing verified (my search found nothing).
- .NET: page fetched but too large and not read; UNVERIFIED (from memory: culture/invariant case-insensitivity, no normalization).
- RE2: UNVERIFIED (from memory: no normalization, simple case folding).
- Elasticsearch analysis-icu icu_folding filter: UTR#30-based folding that also normalizes, via analyzer not regex. https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu-folding.html
Overall: no regex engine surveyed matches compatibility characters; the standard route is normalizing both sides outside the engine (or ICU/Lucene folding at analysis time).
