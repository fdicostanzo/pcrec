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

### Files, with the checksum each was retrieved at

| file | SHA-256 | bytes |
|---|---|---|
| `UnicodeData.txt` | `ff58e5823bd095166564a006e47d111130813dcf8bf234ef79fa51a870edb48f` | 2,175,362 |

Verify with `shasum -a 256 third_party/ucd-16.0.0/*.txt`.

## What derives from it

This is the direction `third_party/README.md` says a maintainer and a licence
audit both actually need — from the source outward.

| derived artifact | produced by | consumed by |
|---|---|---|
| `src/parse/uprops_tables.inc` | `third_party/ucd-16.0.0/generate.py` | `src/parse/mod_uprops.c` — module `unicode-props`' `\p{...}` / `\P{...}` name lookup |

`generate.py`'s own docstring says which of the emitted properties come from
the UCD and which are PCRE2 inventions read off `man pcre2pattern`; that split
is the file to read before trusting any single row.

Regenerate with `make gen-tables` (or `python3
third_party/ucd-16.0.0/generate.py`). `make test` runs the generator's
`--check` mode, so a `.inc` edited by hand fails the suite by name.

## Why this file set and no other

**Only what stage 3 uses is vendored** (D77: no data ahead of a measured
need). General categories and every derived family this stage ships —
`L&`, `Any`, `Xan`, `Xps`, `Xsp`, `Xuc`, `Xwd` — come out of
`UnicodeData.txt` alone, and `Cn` is derivable as the complement of what that
file lists, since it lists only ASSIGNED code points.

The later stages bring their own files INTO THIS DIRECTORY, at this same
version, and add their rows to the table above:

- **[M5.0] stage 4** (the DD-1 fold closure) needs `CaseFolding.txt`.
- **[M5.0] stage 5** (scripts and `Script_Extensions`) needs `Scripts.txt`
  and `ScriptExtensions.txt`.

`utf8_design.md` §3.3's table lists all six files as the vendored set; that is
the milestone's total, not stage 3's.

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
