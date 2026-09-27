# Findings — the contract (`[FINDINGS]`)

**Status: B1 (2026-09-27).** This page is the contract for what pcrec reads
from *findings* — measured facts about the subjects a build will see — and
what it promises about them. It grows by step
(`docs/design/findings/design.md` §13–§14): B1 wrote §1–§6 below (the data
the compiler reads, the normalization, the per-kind NONE answers, the stamp);
resolution, `--analysis`, `-I` and the listings are B2's, the analyzer's
command line B3/B6's, `run-rarity` B4's, `cpfreq` B5's. Where a section is
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
| **block** | one data block inside a bundle, headed by its kind (`freq`), holding COUNTS plus declarations plus provenance |
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
| `cpfreq` | occurrences of each decoded code point | `U+HHHH`… | `byte-rate via encode-utf8` \| `encode-latin1` | B5 |
| `bigram` | occurrences of each adjacent byte pair | `HH HH` | `run-rarity via markov1` | B4 |

A block's **`serves <query> when <enc>[,<enc>…] via <derivation>`** line is
its applicability, and the compiler's whole selection rule is "use what the
data declares": nothing in the compiler tests the encoding next to a rate.
`encoding <e>` describes the counted data and is never consulted for
selection. Within one bundle at most one block may serve a given
(query, encoding). A count above **`PCREC_MAX_FIND_COUNT`** (2^40,
`limits.md` §3.7) is refused at parse, by that name.

**The chain at B1 is the built-in `default` alone**, the shipped analysis
compiled into `libpcrec` (§6). It declares `serves byte-rate when byte via
unigram`, so under `-e byte` every reader reads its rates and under `-e utf8`
the `byte-rate` answer is NONE.

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

## 4. The readers: one NONE answer per question KIND

A rate is asked through ONE accessor, and each question KIND spells its NONE
answer once; a reader states its kind and the ORDER in which it offers its
candidates, which is its tie rule, and never tests the rate itself (D126 Q4).

| kind | question | NONE answer |
|---|---|---|
| PICK | which of `n` candidates is rarest (argmin, ties to the EARLIEST candidate) | the reader's positional rightmost candidate (PCRE2's LASTCODEUNIT rule) |
| COMPARE | is `p` no commoner than `q` | false: no density claim |
| MASS | the rate summed over a set or a sequence | the uniform rate's mass, `⌊k·10^6/256⌋` for `k` members or bytes — CARDINALITY |

| reader | kind | what the rate chooses | why no answer or give-up can move |
|---|---|---|---|
| the necessary byte's pick (`<PREFIX>_REQ_BYTE`) | PICK: the threaded rightmost member, then the rest 255→0 | which member of the necessary set the pre-check scans | every member is necessary, so its absence proves NOMATCH; on a VM route with no DFA in front every member is pre-checked (K65) |
| the necessary run's scan member (`<PREFIX>_REQ_RUN`'s `@idx`) | PICK: the run in order | which member of the run the `memchr` scans | the run is compared whole at each hit |
| the necessary run's window | MASS over each 8-byte window (ties leftmost) | which window of a longer run is emitted | any window is necessary; on a VM route with no DFA in front the whole run is also compared (K66) |
| G1, the pre-check's domination rule (`<PREFIX>_REQ_WHY`) | COMPARE | whether a pre-check dominated by the candidate scan is elided | only in front of a linear DFA scan whose language already requires the byte |
| the offset-k selection (`<PREFIX>_DFA_PREFILTER_OFFSETS`) | MASS over each offset's byte set | which necessary offset sets the skip scans and verifies | every tested (offset, set) is necessary for every match |

`tuning.md` §2.27–§2.30 carry each mechanism; `docs/design/findings/design.md`
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

## 6. The shipped default and the store

`src/findings/default.rxt` is the one authored analysis: a `freq` block
whose counts are the static byte-frequency prior pcrec shipped before B1
(its header carries where the numbers come from), declaring `byte` only. The
store is every `src/findings/<name>.rxt`, compiled into `libpcrec` at build
time, parsed by the same `.rxt` reader as any user file in a no-filesystem
mode (an `include "…"` or `lib` line is refused there). A compile does not
parse it: the build pre-parses the same text into a table, and
`tests/findings/` checks the two agree.

Not built at B1 (B2): naming an analysis (`analysis <name>` in a config,
`--analysis`), the `-I` search path, a user's bundle, `--list-analyses` /
`--list-analysis`.
