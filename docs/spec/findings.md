# Findings — the contract (`[FINDINGS]`)

**Status: B5 (2026-09-28).** This page is the contract for what pcrec reads
from *findings* — measured facts about the subjects a build will see — and
what it promises about them. It grows by step
(`docs/design/findings/design.md` §13–§14): B1 wrote §1–§6 below (the data
the compiler reads, the normalization, the per-kind NONE answers, the stamp);
B2 wrote §7–§9 (resolution, naming an analysis, the listings, the library
fields) and widened §2 and §6; B5 wrote §3a (`cpfreq` and its two
derivations) and the shipped `log` and `weblog` analyses (§6); the
analyzer's command line is B3/B6's, `run-rarity` B4's. Where a section is
not yet built it says so. Design record: `docs/design/findings/design.md`;
decisions D122, D123, D126.

**The one promise that frames the rest: findings may change SPEED, never an
ANSWER, never a GIVE-UP.** Every reader of a rate chooses among options each
of which is sound (§4), so any rate table — the shipped one, a user's, an
adversarial one — gives the same answers and the same give-ups; it moves
only which sound option the artifact takes.

## 1. Terms

| term | meaning |
|---|---|
| **analysis** (bundle) | one `analysis <name>` block of an `.rxt` file (`rxt_format.md`): at most one data block per kind, and an optional `include <other>` |
| **block** | one data block inside a bundle, headed by its kind (`freq`, `cpfreq`), holding COUNTS plus declarations plus provenance |
| **query** | what a compiler reader asks. Closed set: `byte-rate`, `run-rarity` |
| **derivation** | the named arithmetic turning a block's counts into a query's answer (§3). Closed set; each is legal on its kinds only |
| **answer** | for (query, compile encoding): the first block along the chain whose `serves` line names that query and lists that encoding, derived by its `via`; otherwise **NONE** |

## 2. The data

A block stores **counts**, never rates: `row <key> <count>`, keys ascending,
a zero count written by omitting the row. The kinds, their keys and
derivations:

| kind | counts | key | derivations | built |
|---|---|---|---|---|
| `freq` | occurrences of each byte | `HH` (lowercase hex) | `byte-rate via unigram` | B1 |
| `cpfreq` | occurrences of each decoded code point | `U+HHHH`…`U+HHHHHH` (uppercase; a Unicode scalar value) | `byte-rate via encode-utf8` \| `encode-latin1` (§3a) | B5 |
| `bigram` | occurrences of each adjacent byte pair | `HH HH` | `run-rarity via markov1` | B4 |

A block's **`serves <query> when <enc>[,<enc>…] via <derivation>`** line is
its applicability, and the compiler's whole selection rule is "use what the
data declares": nothing in the compiler tests the encoding next to a rate.
`encoding <e>` describes the counted data and is never consulted for
selection. Within one bundle at most one block may serve a given
(query, encoding). A count above **`PCREC_MAX_FIND_COUNT`** (2^40,
`limits.md` §3.7) is refused at parse, by that name.

**The chain** is the named analysis, then its `include`, then that one's
`include`, …, and always ends in the built-in `default` (§7). With no analysis
named it is `default` alone, the shipped analysis compiled into `libpcrec`
(§6). `default` declares `serves byte-rate when byte via unigram`, so with no
analysis named, under `-e byte` every reader reads its rates and under
`-e utf8` the `byte-rate` answer is NONE.

## 3. `unigram`: counts → byte-rate (the normalization)

Given 256 counts `c(b)`, `N = Σ c(b)`, `z` = the number of zero counts and
`FLOOR` = **`PCREC_FIND_FLOOR_PPM`** (2):

1. `N == 0` is an error: the block has no byte-rate.
2. `M = 1,000,000 − FLOOR·z`.
3. `ppm(b) = FLOOR` if `c(b) == 0`, else `max(FLOOR, ⌊c(b)·M / N⌋)`.
4. `R = 1,000,000 − Σ ppm(b)` (may be negative) is added to the LARGEST
   entry, ties to the lowest byte.
5. Hence `Σ ppm = 1,000,000` and every `ppm(b) ≥ FLOOR`.

Integer arithmetic only (a count ≤ 2^40 times `M` fits 64 bits), so the rates
are bit-identical on every box.

**Test vectors** (checked against an independent implementation,
`tests/findings/findings_ref.py`):

| counts | ppm |
|---|---|
| the shipped default (256 counts summing to 1,000,000, none zero) | each `ppm(b) = c(b)` exactly (`N = M = 10^6`, `R = 0`) |
| all equal (every count 1) | byte 0x00: 3,970; every other byte: 3,906 (`R = 64`) |
| one nonzero (0x61 → 5) | 0x61: 999,490; every other byte: 2 |
| negative residue (0x00 → 10^12, every other byte → 1) | 0x00: 999,490; every other byte: 2 (`R = −509`) |

## 3a. `encode-utf8` and `encode-latin1`: code points → byte counts

A `cpfreq` block's rows count CODE POINTS; a byte-rate reader wants BYTES.
Its derivation turns the one into the other, then §3 normalizes the result
exactly as it does a `freq` block's counts:

- **`encode-utf8`**: `count(b) = Σ_cp count(cp) × occ(b, utf8(cp))` — each
  code point's count added once for every byte of its UTF-8 encoding. The
  encoder is the one pcrec lowers a `-e utf8` pattern with, so the bytes a
  rate is derived for are the bytes the matcher scans. On an ASCII-only
  sample every encoding is one byte and this is exactly the `freq` view:
  the same rates and the same digest.
- **`encode-latin1`**: a code point at or below `U+00FF` puts its count on
  that byte; a larger one is **dropped**, and `--list-analysis`'s
  `resolution` row says how many occurrences were (its `dropped` column).
  A block all of whose code points drop counts nothing and is refused at
  compile (§3 step 1).

A derived count above **`PCREC_MAX_FIND_COUNT`** is refused when the block
is parsed, by that name (two code points sharing a lead byte can sum past it
though no row does); a `cpfreq` block holds at most
**`PCREC_MAX_FIND_CPFREQ_ROWS`** (65,536) rows (`limits.md` §3.7).

**Why a code-point kind at all.** A `freq` block describes one byte
sequence; under `-e utf8` a byte's rate depends on which characters the
subjects hold, and the analyzer's default declarations (design §10.2) give
the `byte` compile the block counting bytes and the `utf8` compile the block
whose applicability the data declares per code point. The two can never
both claim one (query, encoding) in a bundle (§2).

## 4. The readers: one NONE answer per question KIND

A rate is asked through ONE accessor, and each question KIND spells its NONE
answer once; a reader states its kind and the ORDER in which it offers its
candidates, which is its tie rule, and never tests the rate itself (D126 Q4).

| kind | question | NONE answer |
|---|---|---|
| PICK | which of `n` candidates is rarest (argmin, ties to the reader's positional rightmost candidate when it is among the minima, else to the EARLIEST); a candidate is a byte or, since `abi` 59, a CUBE `(T, K)` whose cost is the rate summed over its members (a byte is the cube with `K = ff`) | the same argmin over MASS's NONE answer, the uniform mass (cardinality): the candidate with the fewest members, ties to the rightmost — so PCRE2's LASTCODEUNIT rule wherever every candidate is one byte, and an exact position before a pair (since `abi` 60, [K82]; before it the rightmost whatever the candidates' sizes) |
| COMPARE | is `p` no commoner than `q` | false: no density claim |
| MASS | the rate summed over a set or a sequence | the uniform rate's mass, `⌊k·10^6/256⌋` for `k` members or bytes — CARDINALITY |

| reader | kind | what the rate chooses | why no answer or give-up can move |
|---|---|---|---|
| the necessary byte's pick (`<PREFIX>_REQ_BYTE`) | PICK: the threaded rightmost member, then the rest 255→0 | which member of the necessary set the pre-check scans | every member is necessary, so its absence proves NOMATCH; on a VM route with no DFA in front every member is pre-checked (K65) |
| the necessary run's scan member (`<PREFIX>_REQ_RUN`'s `@idx`) | PICK over the run's POSITIONS as cubes in REVERSE order (rightmost first) [FIND-TIE]: a pair position costs its two members' summed rate | which position of the run the scan tests (one `memchr` for a byte, two streams for a pair, `tuning.md` §2.39) | every position is necessary: the run is compared whole, masked where it is masked, at each hit of either member |
| the necessary run's window | MASS over the MEMBERS of each 8-position window (a pair position contributes both members; ties leftmost) | which window of a longer run is emitted | any window is necessary; on a VM route with no DFA in front the whole run is also compared (K66) |
| the run pin's scan (`run_pin`'s stretch) | PICK over the window's EXACT positions in reverse order | which exact byte of a masked run the run-pinned prefilter scans | the pin claims only exact positions, each necessary at its offset |
| G1, the pre-check's domination rule (`<PREFIX>_REQ_WHY`) | COMPARE | whether a pre-check dominated by the candidate scan is elided | only in front of a linear DFA scan whose language already requires the byte |
| the pre-check's lead (`set-leads`, `tuning.md` §2.40) | PICK over `[the run's scan cube, the necessary set's pick]`, the run first | whether the set pick's one-byte `memchr` is tested before the run search | both are necessary, so either's absence proves NOMATCH; on a VM route with no DFA in front every set member is tested anyway (K65) |
| the offset-k selection (`<PREFIX>_DFA_PREFILTER_OFFSETS`) | MASS over each offset's byte set | which necessary offset sets the skip scans and verifies | every tested (offset, set) is necessary for every match |

`tuning.md` §2.27–§2.30 and §2.40 carry each mechanism; `docs/design/findings/design.md`
§6.2a carries the arguments.

## 5. The stamp: `<PREFIX>_FINDINGS` and `rx_info.findings`

Every artifact records which findings it was built from
(`match_api.md` §6, §6.3):

```c
#define RX_FINDINGS "byte-rate=default:1822fb973b95a4da"
```

- One `query=bundle:digest` item per query the compile **asked**, in the
  fixed query order (`byte-rate`, then `run-rarity`), `;`-joined.
- `query=none` when asked and nothing answered (`-e utf8` under the default).
- The empty string when nothing was asked (a pattern no reader looked at).
- `bundle` is the analysis whose block ANSWERED.
- **The digest** is FNV-1a-64, 16 lowercase hex digits, over the bytes
  `pcrec-find-1\0byte-rate\0` followed by the 256 derived ppm values as
  `uint32` little-endian in byte order — exactly what the readers consumed:
  no kind, no `via`, no provenance, so the same rates from any block give the
  same digest.
- `rx_info.findings` equals the macro byte for byte.
- **Disclosure.** The analysis NAME is plain text in every artifact built
  under it, macro and `rx_info` both, so a shipped binary discloses it. Name
  analyses neutrally.

A shipped-data change (editing `default.rxt`) moves the digest of every
artifact that consumed it, which is how such a change becomes visible.

## 6. The shipped analyses and the store

`src/findings/default.rxt` is the one authored analysis: a `freq` block
whose counts are the static byte-frequency prior pcrec shipped before B1
(its header carries where the numbers come from), declaring `byte` only. The
store is every `src/findings/<name>.rxt`, compiled into `libpcrec` as its
text, and parsed by the same `.rxt` reader as any user file in a
no-filesystem mode (an `include "…"` or `lib` line is refused there). A
compile does not parse it: `make gen-findings` pre-parses the same text into
a committed table, and `tests/findings/` checks the table, the embedded text
and the source file all agree.

**The shipped `log` and `weblog` analyses** ([FINDINGS] B5) are GENERATED,
never hand-edited: each is what the analyzer (`build/pcrec-analyze`,
`analyze/`, [FINDINGS] B6) prints for a corpus vendored under
`third_party/`, whose `generate.py`
writes `src/findings/<name>.rxt` (`make gen-tables` regenerates them and the
store; `make test-findings` fails when one is stale).

| analysis | corpus | blocks | serves |
|---|---|---|---|
| `weblog` | 1,000,000 bytes of Apache combined-format web-server request lines (`elastic/examples`, Apache-2.0, pinned commit) | `freq`, `cpfreq` | `byte-rate` under `byte` (freq) and `utf8` (cpfreq, `encode-utf8`) |
| `log` | 999,960 bytes of SYNTHESIZED Hadoop-DataNode-shaped log lines (no licensable real corpus was found; its provenance says `fidelity synthesized`) | `freq`, `cpfreq` | the same split |

Neither is consulted unless named (`--analysis weblog`, a config's `analysis
log`): the chain of a compile that names nothing is still `default` alone,
so under `-e utf8` its `byte-rate` answer is still NONE. Naming one gives a
`-e utf8` compile a measured byte-rate. Neither includes another bundle.

`--list-analyses` lists the store (§8).

## 7. Resolution: from a name to the chain

An analysis is named in exactly two places: a `config`'s `analysis <name>`
line (`rxt_format.md`; one name, composed later-wins across `from`/`with`
like `engine`), and `--analysis NAME` on the command line (or
`pcrec_options.analysis`, §9). Names are lowercase: `[a-z][a-z0-9_-]*`.

**`--analysis` only FILLS.** It names the analysis of a `--pattern` compile,
and of each target of a file operand whose configs name none. It never
overrides a config's own `analysis`; a target whose config names a different
one gets the file's, with a non-fatal note on stderr (`cli.md` §1.1's
file-wins rule — `--engine` stays its single exception). An experiment is a
config VARIANT in the file (`config exp from base` + `analysis x`, and a
target built `with exp`).

**Three stops, searched in order, and nothing else** — no environment
variable, no default directory, no working-directory lookup:

| stop | searched | a name maps to |
|---|---|---|
| S1 | the bundles defined in the compiling `.rxt` file itself (never its `include "…"` fragments or its `lib` files), or a library caller's `analysis_source` | the bundle whose `analysis` line carries the name (a name defined twice in one file is a parse error) |
| S2 | for each `-I DIR` in order (a library caller's `analysis_dirs`), the file `DIR/<name>.rxt` whose directory entry is EXACTLY `<name>.rxt` | that file's ONE bundle, when it is named `<name>`. A file that defines no bundle, or one of another name, FALLS THROUGH to the next stop with a note on stderr; a file defining two or more bundles is refused |
| S3 | the store built into the library (§6) | by name |

**The chain** starts at the first stop defining the selected name, then
follows each bundle's `include <other>`: an `include` of the bundle's OWN name
resolves starting at the stop AFTER the one it was found at (gcc's
`#include_next` — the way to extend a shipped analysis under its own name),
any other include from S1. Any other repeated (bundle, stop) is an include
cycle and refused, naming the cycle. The chain holds at most
**`PCREC_MAX_FIND_CHAIN`** (8, `limits.md` §3.7) links before its terminal.

**The terminal is the built-in `default`, by identity, never by name**: a
`default.rxt` in an `-I` directory does not move a compile that did not name
it. An explicit `include <default>` IS a name lookup (and the way to extend
the default); when it reaches the store's `default`, the terminal is not
added a second time.

**Answering a query** (§1's *answer*): the first block along the chain whose
`serves` line names the query and lists the compile's encoding. Each query is
answered from exactly one block, and every block is self-contained for the
queries it serves.

Resolution is EAGER: it runs before the pattern is parsed, so a bad name
refuses even a pattern no reader would look at.

| failure | behaviour |
|---|---|
| a name no stop defines | refused, naming the stops searched |
| a name with an uppercase letter or another illegal byte | refused, naming the rule |
| an include cycle, or a chain over `PCREC_MAX_FIND_CHAIN` | refused, naming the chain / the limit |
| an `-I` file defining two or more bundles | refused, naming the file |
| an `-I` file that fails to parse, or is over **`PCREC_MAX_FIND_BUNDLE_BYTES`** (1 MiB) | refused, with the parse's own diagnostic / by the limit's name |
| an `-I` file that defines no bundle, or one of another name | a note, and the search continues |
| the selected chain declares no query at all under this compile's `-e` | a note (every reader takes its NONE answer) |
| the same name at two stops | not an error: the earlier stop shadows the later |

## 8. The listings: `--list-analyses` and `--list-analysis`

Both are `table_contract.md` producers, every table a named `#section`,
every free-text cell escaped by the contract's own rule.

**`--list-analyses`** — one row per analysis built into the library (the
store). `-I` directories are never enumerated. Columns: `name`, `kinds`
(canonical order `freq,cpfreq,bigram`), `serves` (`query@enc` pairs its own
blocks answer), `include`, `source`/`license`/`retrieved` (its first block's
provenance), `rows_digest`, `bytes` (the embedded text's size).
`rows_digest` is a DIFFERENT hash from the stamp's: FNV-1a-64 over
`pcrec-find-rows-1\0`, then per block its kind and a NUL followed by each
nonzero `(key u8, count u64le)` in key order (a `cpfreq` block's key as
`u32le`) — it identifies a bundle's rows, where the stamp identifies what a
compile consumed.

**`--list-analysis NAME [-I DIR…]`** — the chain THIS invocation would resolve
for `NAME`, then the named bundle's own data:

| section | rows | columns |
|---|---|---|
| `chain` | one per link, in order | `link`, `bundle`, `stop` (`source` / `-I` / `store` / `store-default`), `location` (the file, for `-I`), `include` |
| `resolution` | one per query × compile encoding | `query`, `encoding`, `link`, `bundle`, `kind`, `via`, `digest` — the exact digest a `<PREFIX>_FINDINGS` stamp would carry, or `none` — and `dropped`, the code-point occurrences the derivation dropped (`encode-latin1`, §3a; `0` for the others, empty with no answer) |
| `freq`, `cpfreq` (and later `bigram`) | the named bundle's own rows | `key`, `count`, and for `freq` the normalized `ppm`; a `cpfreq` key is spelled `U+HHHH` |
| `declarations` | one per block | `kind`, `encoding`, `serves` (as written), `question`, `reader`, `analyzer` |
| `provenance` | one per block × field written | `kind`, `field`, `value` |

**`--list-analysis FILE [-I DIR…] [--analysis X]`** — the per-TARGET view,
chosen when the value is not an analysis name (a path has a `.` or a `/`):
what each target of the `.rxt` FILE resolves to after config joins and the
fill-only `--analysis`.

| section | rows | columns |
|---|---|---|
| `targets` | one per target | `target`, `configs` (its `with` list as written), `analysis`, `named_by` (`config` / `cli-fill` / `none`), `config_line` (the config that named it) |
| `chain` | one per target × link | `target` + the name view's `chain` columns |
| `resolution` | one per target × query × compile encoding | `target` + the name view's `resolution` columns |

## 9. The library: `pcrec_options`

`pcrec_options` carries the same surface (`lib/pcrec.h`):

| field | meaning |
|---|---|
| `analysis` | the bundle name; NULL for none (the chain is `default` alone, byte-identical to a compile that predates these fields) |
| `analysis_dirs` | a NULL-terminated list of S2 directories; NULL for none |
| `analysis_source`, `analysis_source_len` | `.rxt` TEXT defining bundles, stop S1, parsed in the no-filesystem mode (a `lib` or `include "…"` line is refused — a buffer opens no file); NULL for none |

The library PARSES: a caller hands text or directories, never pre-parsed
values. A caller with no filesystem passes `analysis_source` and/or relies on
the built-in analyses. Resolution failures refuse the compile through
`pcrec_error` (§7's table); the two notes are written to stderr.
