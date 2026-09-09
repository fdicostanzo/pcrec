# PROVENANCE — the Unicode Character Database, 16.0.0

## Source

| | |
|---|---|
| **Origin** | https://www.unicode.org/Public/16.0.0/ucd/ |
| **Version** | Unicode 16.0.0 |
| **Retrieved** | 2026-09-06 |
| **Retrieved by** | lane `utf8s3`, [M5.0] stage 3 |
| **Licence** | Unicode License v3 (see LICENSE below) |
| **Modified?** | **No.** The files are byte-for-byte as retrieved. |
| **Stage-4 addition** | `CaseFolding.txt` retrieved 2026-09-08 by lane `utf8s4`, [M5.0] stage 4, from the same directory at the same version. |
| **Stage-5 addition** | `Scripts.txt`, `ScriptExtensions.txt` and `PropertyValueAliases.txt` retrieved 2026-09-09 by lane `utf8s5`, [M5.0] stage 5, from the same directory at the same version. |

### Files, with the checksum each was retrieved at

| file | SHA-256 | bytes |
|---|---|---|
| `UnicodeData.txt` | `ff58e5823bd095166564a006e47d111130813dcf8bf234ef79fa51a870edb48f` | 2,175,362 |
| `CaseFolding.txt` | `6f1f9c588eb4a5c718d9e8f93b782685e5c7fec872cf05e8e6878053599e09bb` | 86,092 |
| `Scripts.txt` | `9e88f0a677df47311106340be8ede2ecdacd9c1c931831218d2be6d5508e0039` | 189,588 |
| `ScriptExtensions.txt` | `049117ce26b9769fe2749b06eef51a50a89faef4a97764dd2d81daa715980700` | 20,576 |
| `PropertyValueAliases.txt` | `440fd3e5460b9bfe31da67b6f923992e1989d31fe2ed91e091c4b8f8e2620bf9` | 80,773 |

Verify with `shasum -a 256 third_party/ucd-16.0.0/*.txt`.

## What derives from it

This is the direction `third_party/README.md` says a maintainer and a licence
audit both actually need — from the source outward.

| derived artifact | produced by | consumed by |
|---|---|---|
| `src/parse/uprops_tables.inc` | `third_party/ucd-16.0.0/generate.py` | `src/parse/mod_uprops.c` — module `unicode-props`' `\p{...}` / `\P{...}` name lookup. From `UnicodeData.txt` (the general categories) and, since [M5.0] stage 5, from `Scripts.txt` + `ScriptExtensions.txt` + `PropertyValueAliases.txt` (the 171 script values, their spellings, and the two sets each answers to) |
| `src/core/fold_tables.inc` | the same generator, from `CaseFolding.txt` | `src/core/fold.c` — the `pcrec_fold_ucd_simple` relation the `utf8` encoding's caseless class constructor closes over ([M5.0] stage 4, DD-1) |
| `src/gen/enc/utf8_fold_pairs.inc` | the same generator, from `CaseFolding.txt` | `src/gen/enc/enc_utf8.c` — **the one derived artifact that IS emitted**, as C source text inside the caseless-backreference residual (see below) |

**THE THIRD ROW BREAKS THIS DIRECTORY'S OTHERWISE-UNIVERSAL RULE and the
break is deliberate, ruled by the design rather than taken here.**
`third_party/CLAUDE.md` says *"nothing here reaches a generated artifact"* —
the data compiles to tables inside `libpcrec.a` and a user's matcher is an
automaton over bytes. That holds for every property table and for the fold
CLASS closure, both of which are applied at parse time and never survive into
emitted C. It cannot hold for a caseless BACKREFERENCE: its operand is subject
text nobody has seen at compile time, so the fold has to exist a second time
as TEXT the artifact carries (`utf8_design.md` §4.6(b), which sizes it against
D84's caps and rules out the direct-indexed alternative at 4.4 MB). About
26 KB of table text, in an artifact that has such a backreference and in no
other. The licence obligation is unchanged and is discharged the same way —
the Unicode License v3 permits redistribution of the Data Files and of works
derived from them, and `LICENSE.txt` ships here unmodified.

**THE TWO FOLD ARTIFACTS ARE ONE RELATION IN TWO FORMS** — an orbit relation
for the compiler and a sorted `{from, to}` map for the artifact — generated in
one run from one file so they cannot drift, and tied by
`tests/backrefs/fold_agreement_utf8_check.c`, which compares the SHIPPED
residual against the compiler's own object over all 2,938 members of the
relation.

`generate.py`'s own docstring says which of the emitted properties come from
the UCD and which are PCRE2 inventions read off `man pcre2pattern`; that split
is the file to read before trusting any single row.

Regenerate with `make gen-tables` (or `python3
third_party/ucd-16.0.0/generate.py`). `make test` runs the generator's
`--check` mode, so a `.inc` edited by hand fails the suite by name.

## Why this file set and no other

**Only what a landed stage uses is vendored** (D77: no data ahead of a
measured need). General categories and every derived family this stage ships —
`L&`, `Any`, `Xan`, `Xps`, `Xsp`, `Xuc`, `Xwd` — come out of
`UnicodeData.txt` alone, and `Cn` is derivable as the complement of what that
file lists, since it lists only ASSIGNED code points.

The later stages bring their own files INTO THIS DIRECTORY, at this same
version, and add their rows to the table above:

- ~~**[M5.0] stage 4** (the DD-1 fold closure) needs `CaseFolding.txt`.~~
  **DONE 2026-09-08** — `CaseFolding.txt` is vendored above, at the same
  version, and its two derived artifacts are in the table.
- ~~**[M5.0] stage 5** (scripts and `Script_Extensions`) needs `Scripts.txt`
  and `ScriptExtensions.txt`.~~ **DONE 2026-09-09**, and it needed a THIRD
  file the design did not list: `PropertyValueAliases.txt`. Two reasons, both
  measured. Every script value answers to a four-letter code as well as a long
  name (`\p{Grek}` compiles on all three libpcre2 versions) and `Scripts.txt`
  carries only the long names; and `ScriptExtensions.txt` names its scripts BY
  CODE, so the code-to-name map is what makes it readable at all. It also
  supplies the one value `Scripts.txt` cannot — `Unknown`/`Zzzz`, which is the
  complement of everything that file lists — and the one this directory
  DECLINES, `Katakana_Or_Hiragana`/`Hrkt`, a UCD `sc` value no libpcre2 this
  project can reach accepts.

`utf8_design.md` §3.3's table lists five files as the vendored set (and does
not list `PropertyValueAliases.txt`); `PropList.txt` and
`DerivedCoreProperties.txt`, which it does list, are for the BOOLEAN
properties — declined by §3.4 — and are deliberately still absent.

## Why the version is 16.0.0, and why that is not what the local oracle says

The pin follows the REFERENCE oracle — libpcre2 10.46 on the Linux box — and
it is derived rather than assumed: the design's own §3.3 swept 10.46 and
measured `\p{L}` at 677 intervals, `\p{Lu}` at 651, `\p{Nd}` at 71 and
`\p{Xan}` at 770, and this directory's generator produces **exactly those four
numbers** from `UnicodeData.txt` at 16.0.0. Four independent confirmations
that the pin matches the reference.

Neither libpcre2 on the Mac dev box is at that version, MEASURED 2026-09-06:

| | libpcre2 | Unicode |
|---|---|---|
| Linux reference (`ubuntubudu`) | 10.46 | 16.0.0 — **the pin** |
| Mac, Homebrew (`pkg-config`, headers) | 10.48 | 17.0.0 |
| Mac, what the suite's dlopen shim RESOLVES (`/usr/lib`) | 10.42 | 14.0.0 |

The third row is the surprising one and it is a finding about the whole tree,
not about this directory: `tests/fuzz/pcre2_abi.h` lists bare SONAMEs before
the Homebrew absolute paths, and on macOS a bare name resolves through the
dyld shared cache to the system library. Every dlopen-based oracle in this
repository sees 10.42 on this box.

`tests/uprops/uprops_compare.py` is where that is dealt with: it reads the
oracle's Unicode version at run time and applies an exact-agreement rule when
it matches the pin and a stated drift budget when it does not. A libpcre2
version bump moves the pin DELIBERATELY, which is D26's re-measurement rule.

## LICENSE

The UCD is distributed under the Unicode License v3. The full text ships as
`LICENSE.txt` beside the data files, retrieved from
https://www.unicode.org/license.txt at the same time as the data.

In summary (the licence text governs, not this paragraph): permission is
granted free of charge to deal in the Data Files without restriction,
including the rights to use, copy, modify, merge, publish, distribute and
sell, provided the copyright notice and permission notice appear in all
copies, and the notice appears in associated documentation. That obligation is
discharged by shipping `LICENSE.txt` unmodified in this directory and by this
file.
