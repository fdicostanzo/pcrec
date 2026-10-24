# [UPROP-MORE] — `\p{}` covers the binary properties, Bidi_Class, and (as an extension) Block and Age

Lane `upropd` (sonnet), 2026-10-24. **Design only**: nothing under `src/`,
`tests/`, `docs/spec/`. **Status: PROPOSED.** No build before Frank reads it.
Inputs: `docs/dev/utf_wants_2026-10-24.md` (want 3), `docs/pcre2_compliance.md`
(Unicode properties), `docs/design/utf8_design.md` §3, `third_party/ucd-16.0.0/`.

## STOP-RULE FINDING, FIRST

**PCRE2 10.46 already has nearly everything pcrec lacks, and one missing
mechanism covers all of it.** Probed live against libpcre2 10.46 (Unicode
16.0.0; a ctypes probe over ~130 spellings, scratch only): it accepts **53
binary properties** (106 spellings with their short aliases), `Any`, and
`Bidi_Class` (`bc`) with the 23 SHORT class names only. It rejects Age, Block
(`In...`, `Block=`, `blk=`), `Assigned`, `Hyphen`, `Other_*`,
`Full_Composition_Exclusion`, and every other UCD property axis (`gc=`, `ea=`,
`lb=`, `gcb=`, `nt=`, `jt=`, `ccc=`). So the survey's "Emoji,
Default_Ignorable, Bidi_Class" are all **catch-up (a)**, not extensions. Only
Block and Age are beyond PCRE2.

The one missing mechanism: **a reader for UCD's ranged-property files**
(`cp[..cp] ; Name # comment`, the same format in PropList,
DerivedCoreProperties, emoji-data and DerivedBidiClass) feeding the existing
generator's row table. Today `generate.py` reads only UnicodeData, Scripts,
ScriptExtensions, CaseFolding and PropertyValueAliases. Everything below is
shaped around adding that reader once. No parser, engine, emitter or abi
change is needed: a property is an interval list, exactly like `\p{Sc}`.

Premise test: `build/pcrec -p rx -e utf8 --features unicode-props --emit-main
-o X --pattern '\p{Emoji}'` refuses: `pcrec: module 'unicode-props' is enabled
but \p{...}: this Unicode property is not implemented yet (pattern offset 9)`.
Without the feature the text is `\p requires module 'unicode-props'`. Same for
`\p{Alphabetic}`, `\p{Bidi_Class:AL}`, `\p{bc=AL}`, `\p{Hex_Digit}`,
`\p{Age=6.0}`, `\p{InBasicLatin}`, `\p{Assigned}`.

## GOALS

1. **Every `\p{...}` spelling libpcre2 10.46 accepts compiles in pcrec with the
   same set.** Who: users porting PCRE2 patterns (the `\p{Emoji}` digit
   gotcha, Go #14509-style requests). Measure: the PC-3 name sweep finds no name
   PCRE2 accepts and pcrec refuses (today 106 spellings plus the Bidi_Class
   forms refused); an all-code-points comparison against libpcre2 is exact at
   the pinned version.
2. **Data from official Unicode files only, at 16.0.0**, and no claim of a
   Unicode conformance level that an official test file does not prove (Frank
   2026-10-24). Measure: every property row names the vendored file it came
   from; the generator fails if a promised name has no source.
3. **No cost to existing users.** Measure: every existing pattern's emitted
   bytes unchanged (no abi event); `libpcrec.a` grows by a table, estimated
   ~120-200 KB.
4. **Extensions beyond PCRE2 (Block, Age) are opt-in and labelled** (SR-10).

Priority on conflict: 2 > 1 > 3 > 4. Non-goals: properties of strings
(`RGI_Emoji`, `\q{}`; utfwant want 4), `\X` and Grapheme_Cluster_Break
([GRAPHEME]), UTS #18 conformance claims, any property PCRE2 rejects other than
Block/Age.

## 1. Which properties, ranked

Demand (utfwant): the best-evidenced are Emoji (and the digit gotcha),
Alphabetic/Lowercase/Uppercase/White_Space/ID_Start (TR18 RL1.2),
Default_Ignorable and Bidi_Control (Trojan-Source detection, want 13), then
Bidi_Class. Block/Age: **no demand evidence in the survey at all.**

| rank | set | class | PCRE2 | pcrec |
|---|---|---|---|---|
| 1 | Emoji family: `Emoji`, `Emoji_Presentation`, `Emoji_Modifier`, `Emoji_Modifier_Base`, `Emoji_Component`, `Extended_Pictographic` (+ `EPres EMod EBase EComp ExtPict`) | (a) catch-up | accepted | refused |
| 2 | Case/letter: `Alphabetic Lowercase Uppercase Cased Case_Ignorable Changes_When_{Casefolded,Casemapped,Lowercased,Titlecased,Uppercased}` (+ `Alpha Lower Upper CI CWCF CWCM CWL CWT CWU`) | (a) | accepted | refused |
| 3 | Invisible/bidi: `Default_Ignorable_Code_Point` (`DI`), `Bidi_Control` (`Bidi_C`), `Bidi_Mirrored` (`Bidi_M`), `Join_Control`, `Variation_Selector`, `Noncharacter_Code_Point`, `Pattern_White_Space`, `White_Space` (`space`) | (a) | accepted | refused |
| 4 | `Bidi_Class` / `bc`, `=` or `:`, the 23 short names `AL AN B BN CS EN ES ET FSI L LRE LRI LRO NSM ON PDF PDI R RLE RLI RLO S WS` | (a) | accepted, short names only | refused |
| 5 | Identifier/ASCII/CJK/misc: `ID_Start ID_Continue XID_Start XID_Continue`, `ASCII ASCII_Hex_Digit Hex_Digit`, `Ideographic Unified_Ideograph Radical IDS_Binary_Operator IDS_Trinary_Operator IDS_Unary_Operator`, `Dash Quotation_Mark Terminal_Punctuation Sentence_Terminal Soft_Dotted Diacritic Extender Math Deprecated Logical_Order_Exception Regional_Indicator Prepended_Concatenation_Mark Pattern_Syntax Grapheme_Base Grapheme_Extend Grapheme_Link` (+ their short aliases) | (a) | accepted | refused |
| 6 | `Block` (`Block=Greek`, `blk=`) and `Age` (`Age=6.0`) | **(b) beyond PCRE2** | rejected (error 147) | refused; extension behind `--features` |

Ranks 1-5 are one mechanism (§3): the ranking orders review and tests, not
build effort. Do not split them into lanes by rank.

**(b) the extension.** Block and Age exist in ICU, Java, .NET and Python
`regex` but not in PCRE2, so under D26 they are a pcrec extension behind a
feature name (SR-10), and the docs must say it is not portable to PCRE2. Rank 6
because the survey found no demand; the build sizing makes them a separable
last stage Frank can decline (Q2). Spelling proposal: `\p{Block=Greek_And_Coptic}`,
`\p{blk=...}`, `\p{Age=6.0}`, prefix forms only. PCRE2 rejects these, so no valid
PCRE2 pattern changes meaning. The Java-style `\p{InGreek}` is NOT proposed (it
collides with the bare-name namespace and gains nothing). Open sub-point for
the build: whether `Age=V` means "assigned in exactly V" (UCD's DerivedAge) or
"assigned by V" (ICU's reading); the answer must be taken from the file's own
definition and stated in the spec.

Not proposed (PCRE2 refuses them, no demand): `Assigned` (it is `\P{Cn}`;
compliance already records this), `Hyphen`, `Other_*`, `Full_Composition_Exclusion`,
`gc=`, `ea=`, `lb=`, `gcb=`, `nt=`, `jt=`, `ccc=`, long `Bidi_Class` value names
(PCRE2 takes short names only). `East_Asian_Width` (want 15) would be one more
(b) extension by the same mechanism if ever asked; recorded as an unlock, not a
row.

Caseless behaviour, **measured** on 10.46: under `-i` only `Lu`, `Ll`, `Lt`
become `L&`; `\p{Lowercase}`, `\p{Uppercase}`, `\p{Cased}`, `\p{Emoji}` and
`\p{Bidi_Class:L}` are unchanged. So every new row's caseless set is its own
set (the generator's `CASELESS_AS` already says "everything else is itself").

## 2. DATA RULE: official files, at 16.0.0

Home: **extend `third_party/ucd-16.0.0/`** (same source, same version, same
`generate.py`, same `make gen-tables`; its PROVENANCE already says later stages
bring their files in at this version). A new directory would split one source
across two generators for nothing. NEW-DATASET lens answered: home =
`ucd-16.0.0`; the files become rows of the existing `src/parse/uprops_tables.inc`,
generated by the existing generator; no new generated file.

Sizes are from the unicode.org directory listing for 16.0.0 (read, nothing
downloaded); the build lane records exact bytes and SHA-256 at retrieval.

| file | status | size | provides |
|---|---|---|---|
| `UnicodeData.txt` | vendored | 2.2 MB | `Bidi_Mirrored` (field 9) |
| `PropertyValueAliases.txt` | vendored | 79 KB | `bc` value names |
| `PropList.txt` | **add** | 141 KB | White_Space, Bidi_Control, Join_Control, Dash, Quotation_Mark, Terminal_Punctuation, Hex_Digit, ASCII_Hex_Digit, Ideographic, Diacritic, Extender, Noncharacter_Code_Point, Radical, Unified_Ideograph, Pattern_*, Soft_Dotted, Sentence_Terminal, Variation_Selector, Deprecated, Logical_Order_Exception, Regional_Indicator, IDS_*, Prepended_Concatenation_Mark |
| `DerivedCoreProperties.txt` | **add** | 1.1 MB | Math, Alphabetic, Lowercase, Uppercase, Cased, Case_Ignorable, Changes_When_*, Default_Ignorable_Code_Point, Grapheme_Base/Extend, ID_*, XID_* (Grapheme_Link: I could not confirm which file carries it from the pages read; the generator's coverage check below settles it) |
| `emoji/emoji-data.txt` | **add** | 110 KB | the six Emoji properties |
| `extracted/DerivedBidiClass.txt` | **add** | 167 KB | Bidi_Class for ALL code points, including the unassigned defaults that `UnicodeData.txt` field 4 lacks |
| `PropertyAliases.txt` | **add** | 9 KB | official short names of the binary properties and `bc` (replaces a hand-written alias list) |
| `Blocks.txt` | only for (b) | 11 KB | Block |
| `DerivedAge.txt` | only for (b) | 132 KB | Age |

Added for (a): ~1.5 MB of text (DCP dominates); for (b) another ~143 KB.
`ASCII` and `Any` are computed (U+0..7F; the universe), as `Any` is today.

**The generator fails loudly** if any promised name has no source line (a
counted population, K35), and PROVENANCE.md gets one row per file with its
SHA-256.

**No conformance overclaim.** Unicode publishes no official test file for these
properties (its test files cover break rules, normalization, the bidi
algorithm). So pcrec states only: "properties as defined by the Unicode 16.0.0
data files named in PROVENANCE.md". It does NOT claim UTS #18 RL1.2 / RL2.7
conformance, and docs and spec say that sentence verbatim.

Version pin: when libpcre2 moves to Unicode 17, D26's re-measurement rule fires
and every file here moves together (one directory bump). Block/Age are the only
rows with no libpcre2 cross-check across that bump.

## 3. Mechanism

Today's path (read from the tree): `generate.py` parses the vendored files into
`{name: interval list}` rows with a namespace mask (`BARE`, `SC`, `SCX`),
interns identical lists, and writes `src/parse/uprops_tables.inc` (717 rows,
312 distinct sets, 10,961 intervals, 104,896 bytes of table). `mod_uprops.c`
normalises the body (case, space, `-`, `_` dropped), looks it up by namespace
(`uprops_lookup`), and `uprops_produce` hands the interval list to the same
`cpset` machinery as `\p{L}`; the byte automaton is built per encoding
downstream. No property data reaches an artifact (utf8_design §3.3.1).

Changes:
1. **Generator**: one ranged-file reader, a source table `(file, property) ->
   row names (full name + alias from PropertyAliases)`, and the coverage check.
   Binary rows are `NS_BARE` only (PCRE2 rejects `\p{Alphabetic=Y}`, measured).
2. **`bc`/`Bidi_Class`**: a fourth namespace bit `NS_BC` (the mask is an
   `unsigned char`, 3 bits used) and a prefix entry in `uprops_namespace`
   (`mod_uprops.c`, which today answers `bc=` with the unbuilt message). Values
   are the 23 short names; long names stay refused as in PCRE2.
3. **Interval pool**: offsets are `unsigned short` (limit 65,535; the generator
   already errors if exceeded). Pool today 10,961; the added sets are estimated
   at 15-20k intervals (ESTIMATE), so it fits; widen only if the generator trips.
4. **Registry/docs**: compliance rows `\p{<binary property>}` and
   `\p{Bidi_Class:..}` move `REJECTED` -> `OK-GATED`; a `docs/spec/` hunk in the
   same change (D80).
5. **Name collisions** with the 171 scripts are caught by the generator's
   duplicate check and PC-3's whole-table sweep (`check_gated_uprops_space`).

**[UCD-RECORD] verdict: this row rides the existing per-property tables and is
NOT the trigger.** That row's trigger is "the first LARGE GENERAL table ships in
emitted artifacts". Nothing here ships data in an artifact. The trigger fires
with [GRAPHEME]: `\X` decides boundaries at MATCH time, so a
Grapheme_Cluster_Break + Extended_Pictographic table does reach an artifact. The
named interval lists this row generates are exactly the input a record-table
builder would need, so nothing here is wasted by that later row.

**Cost, emitted size (measured, today's build, `-e utf8`, bare `\p{X}`,
emitted C bytes):** Zs 22 KB; Cf 45 KB; Sc 43 KB; Nd 51 KB; Greek 48 KB; Sm
76 KB; Han 76 KB; Lu 138 KB; So 200 KB; L 587 KB (the K53 near-cap case;
`-e byte` `\p{L}` is 15 KB). The cost is the byte automaton, not the table.
By analogy (ESTIMATE; the build lane measures): Emoji family, Dash,
Quotation_Mark, Join_Control, White_Space, Bidi_Control, Default_Ignorable are
small-to-mid (20-120 KB); `Alphabetic`, `ID_Continue`, `XID_Continue`,
`Case_Ignorable`, `Grapheme_Base`, `Lowercase`, `Changes_When_Casemapped` are
`L`-sized or larger (0.5-1.0 MB) and may meet the size caps as `Xan` did.
[CLS-TREE] is the designed answer (class as data, not automaton structure);
this row does not depend on it, but until it lands `\p{Alphabetic}` has `\p{L}`'s
compile-size profile. Bidi_Class: `L`, `R`, `AL` large; the other 20 small.

## 4. Oracle and tests

Standing questions (docs/design/CLAUDE.md):

1. *Measurement regime*: byte counts only (box-independent); no timings. Only
   the size estimates above are affected; a different regime does not flip a
   decision.
2. *Independent control*:
   - **(a)** libpcre2 10.46 builds its tables from the UCD with its own script,
     so it shares only upstream data with us, not our parser. Run the existing
     all-code-points sweep (`tests/uprops`, `make test-uprops-utf8` shape) over
     every new row, exact at the pinned version; PC-3 gains the converse
     direction: pcrec **refuses no name PCRE2 accepts**, over a committed,
     counted list (the 106 spellings plus bc forms probed here).
   - **Second control for what python covers**: python on this box is
     Unicode **16.0.0** (checked): `Bidi_Mirrored` (554 code points) via
     `unicodedata.mirrored`, and `Bidi_Class` for ASSIGNED code points via
     `unicodedata.bidirectional`. Not usable for unassigned defaults or other
     properties; the other box has a different python (utf8_design §3.3), so
     this is a local cross-check only.
   - **(b)** the official file is both source and only oracle, so the control is
     weak by construction. Mitigation: structural checks (blocks tile the whole
     code space without gaps; Age sets nest by version and their union is the
     `Cn` complement), and the spec says plainly that Block/Age have no
     independent differential.
   - Sabotage witnesses: a line deleted from a copy of a vendored file must trip
     the coverage check; a planted wrong alias must trip PC-3.
3. *What moves on regeneration*: `uprops_tables.inc` grows; no existing emitted
   bytes move (new names only), so **no abi bump**. Pins that count rows or
   bytes (the table banner, the PC-3 population, the compliance generated
   index) are re-pinned in the same change. A Unicode version bump moves every
   row's set and is a D26 re-measurement.

Tests: a `.rxt` corpus per family under `tests/utf8/`, authored blind (D27)
from this note's table by an author denied `src/`; witnesses such as
`\p{Emoji}` matches `5` and `\p{Extended_Pictographic}` does not; negation
(`\P{}`, `\p{^}`), inside classes, both encodings, `-i` unchanged.

## 5. Siblings, general form, unlocks

General form: **a property is a named interval list from an official ranged
file.** Sibling family: Script / Script_Extensions / general category (done),
Bidi_Class, binary properties, then Block / Age / East_Asian_Width / Line_Break /
Joining_Type (same reader, other files, extension tier).

Unlocks, each with its trigger:
- **[GRAPHEME]**: needs `Extended_Pictographic` (delivered here, from
  emoji-data) and `Grapheme_Cluster_Break` (`auxiliary/GraphemeBreakProperty.txt`,
  not in this row; same reader), with `GraphemeBreakTest.txt` as its official
  oracle. Trigger: Frank starts [GRAPHEME].
- **[CLASS-SETOPS]**: `[\p{Alphabetic}--\p{Lu}]` and similar become useful; the
  interval algebra exists in `cpset`. Trigger: [CLASS-SETOPS] starts; no
  dependency either way.
- **Emoji digit gotcha** (`\p{Emoji}` matches `0-9 # *`): documentation only;
  the guide should show `\p{Emoji_Presentation}` and `\p{Extended_Pictographic}`.
- **Trojan-Source detection** (want 13): `\p{Bidi_Control}` plus
  `\p{Default_Ignorable_Code_Point}` fall out; a `docs/guide/` example.
- **[UCD-RECORD]**: see §3. **[COMPAT-FOLD]/NFKC**: not unlocked (needs
  UnicodeData decomposition fields, already vendored).

## 6. Build sizing and questions

If Frank agrees: **one sonnet lane for (a)** (generator reader + coverage check
+ `NS_BC` + data vendoring + PROVENANCE + compliance/spec hunks), one **sonnet
D27 blind test-author lane** (cell) for the corpus, one review. Block/Age: a
separable second sonnet lane after (a), only if wanted. `make test` (~11 min)
runs as each lane's last act, queued. No engine, parser or emitter change, so no
opus lane.

Questions for Frank, in plain words:
1. **Add 5 more Unicode data files (about 1.5 MB of text) beside the ones already
   in the Unicode data directory?** My view: yes, same source and version.
2. **Block and Age are not in PCRE2 and nothing in the survey asks for them.**
   Build them as a labelled opt-in extension, or leave them until someone asks?
   My view: leave them out for now.
3. **Big properties such as `\p{Alphabetic}` will compile to hundreds of KB under
   utf8, like `\p{L}`, until the class-matcher work lands.** Ship anyway, or wait?
   My view: ship; users already see this for `\p{L}`.
4. **Wording of the claim**: say only "properties as defined by the Unicode
   16.0.0 data files" and explicitly NOT claim Unicode regex conformance level
   1.2? My view: yes.
