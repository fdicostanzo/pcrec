# spansurv: callout span-helper survey for [SPAN-HELPERS]
Facts only. Read-only survey of pcrec and pcrec-bench; no code run. Date 2026-10-29.

## 1. Evidence: what callout/embedded code in the repo does by hand

Helper usage today (grep of tests/code/*.rxt, tests/code/*/*.rxt, docs/guide): rx_in x5 (guide IPv4 example), rx_eqi x1, rx_u64 x1, rx_u8next x1 (all tests/code/macros.rxt). rx_eq, rx_hex, rx_find: ZERO uses outside tests/code/span_check.c (their unit check) and the spec table. The set was specified from design (inline_c_requirements.md), not from demand; demand so far is numeric-range + one case-fold + one UTF-8 loop.

| site | what the code does | helper that serves it |
|---|---|---|
| tests/code/octet.h `octet_le255`, `all_le255` (UC-1a/1b) | decimal digit run to unsigned, `<= 255`; accumulates `v*10+d` with NO overflow guard (safe only because the pattern is `\d{1,3}`) | rx_in (the guide already shows it); a hand version is exactly the overflow trap |
| tests/code/geoip.c (UC-3) | prefix test `10.` / `192.168.` with memcmp on `(p,n)` | none needed (user's own function); a prefix test is `rx_find(s,z)==0` |
| macros.rxt "PORT=80" | `rx_eqi(RX_CAP(1),"PORT") && rx_u64(RX_CAP(2),&v) && v<65536` | existing |
| macros.rxt UTF-8 count | `rx_u8next` loop counting characters | existing |
| inline_c_requirements UC-2a (template) | hand loop over a name table with `RX_EQ` (Mon -> Monday) | none; case-insensitive membership/index (cand. D) |
| UC-2b template | `rx_atou(RX_G(1)) + 1` (illustrative) | rx_u64 |
| UC-2c template | URL-decode with user `hexval()` of two digits | rx_hex on a 2-byte span, but template side; see ambiguity A5 |
| pcrec-bench bench/unusual/callees/callees.c `ub_luhn` | Luhn mod 10 over group 1, from the right, double every second | none: cand. F |
| same `ub_isbn13` | length 13, `97[89]` prefix, weights 1/3 sum mod 10 | none (weighted check sum; not generalised) |
| same `g1_len`, `ub_netstr` | parse a decimal length from group 1 (1-9 digits), consume that many bytes | rx_u64 (the bench compiles callees independently of any artifact, so it cannot show use) |
| same `ub_member` | FNV-1a hash set loaded from a file | none: user data, out of scope |
| bench `callout_calib.py`, `check_callouts.py` | drive the above; no further callee bodies | -- |

Other callout tests (tests/code/frag, d27, t2, registry) use constant-return or trivial segments; no further by-hand logic. Bench has no callout body beyond luhn, isbn13, member, netstr, stub.

## 2. Well-known callout / "regex cannot do this" cases

| use case | covered today by | gap |
|---|---|---|
| IPv4 octet 0-255, port 0-65535, hour/minute ranges | rx_in (decimal, constant bounds) | leading zeros accepted (`007`); a pattern concern, flag A1 |
| IPv6 hex group `<= ffff`, hex range | rx_hex then compare | no hex rx_in (`rx_hex(s,&v) && v<=hi`, two lines) |
| `$1 <= $2` (range 10-20, version parts, port pairs) | NOTHING: both spans need rx_u64 to two locals; fails past 64 bits | cand. A |
| numbers wider than 64 bits against a bound or each other | NOTHING (rx_u64 rejects) | cand. A, with cand. B for a constant bound |
| ISO date/time ordering (`2026-01-02` vs `2026-03-04`, fixed width) | NOTHING (no span-vs-span compare; rx_eq takes a NUL-terminated C string) | cand. A (digits only) or cand. E (bytes) |
| dates: month length, leap year | rx_in for ranges; month/day dependence is by hand | cand. G (flag A4: domain, not span) |
| Luhn, ISBN, IBAN mod 97 | NOTHING | cand. F (Luhn); IBAN is cand. H |
| balanced parentheses | NOT a helper case: pcrec has recursion `(?R)`; only "equal counts" of two markers needs counting | cand. J, low |
| length limit in characters | rx_u8next loop by hand (8 lines, easy to get the -1 case wrong) | cand. I |
| case-insensitive membership in a word set (days, months, keywords) | rx_eqi in a hand loop | cand. D |
| Unicode property of a code point | rx_u8next gives cp; property needs tables | `\p{..}` in the pattern already does it; NO helper (tables, size, UCD data-source rule). Recommend decline |
| UTF-8 decode | rx_u8next | covered |
| base64/hex validity | character class + length in pattern; hex value by rx_hex | covered; no helper |
| timestamps (epoch, signed) | rx_u64 unsigned only; sign by hand | cand. K, low |

## 3. Candidates (name says what the caller sees; rx_span style)

Ranked by uses served x error-proneness of the hand version.

**A. `int rx_numcmp(rx_span a, rx_span b, int base, int *cmp)`** (Frank's first). Returns 1 and `*cmp` = -1/0/1 when BOTH spans are set, non-empty, every byte a digit of `base` (2..36, ASCII 0-9, a-z, A-Z either case, no sign, no prefix); returns 0 and leaves `*cmp` untouched otherwise (also for `base` outside 2..36). Skip leading zeros (`000` equals `0`), compare significant digit counts, then digit by digit BY VALUE (`(c|32)-'a'+10` for letters; ASCII order is not value order across `9`/`A`/`a`, so decimal could memcmp but base>10 must map per digit). No tables, no locale, no overflow, no allocation, any length. Serves: `$1<=$2`, versions, ranges, >64-bit numbers, hex/binary/octal compares. Overlaps rx_u64/rx_hex/rx_in only for operands under 2^64; this is the only one for span-vs-span. Hand version: error-prone (leading zeros, equal-length-only compare, case). RANK 1.
  Name choice flagged A2: `rx_numcmp` vs `rx_cmp_digits`.

**B. `rx_span rx_lit(const char *z)`**: the set span over the bytes of `z` (len = strlen, loop, no include). Lets cand. A and E take a constant as a span (`rx_numcmp(RX_CAP(1), rx_lit("18446744073709551616"), 10, &c)`). Without it the caller writes the `(rx_span){(const unsigned char*)z, n}` cast. Trivial, no semantics risk. RANK 2 (enables A with constants). Name: `rx_lit` says "literal as span". Does the artifact already include string.h? Not checked; the loop avoids it.

**C. `int rx_uint(rx_span s, int base, uint64_t *out)`**: generalises rx_u64/rx_hex to base 2..36 (binary flags, octal modes, base36 ids). Same invalid contract as rx_u64. Overlap: rx_u64 = rx_uint base 10, rx_hex = base 16; adding it alone would make two spellings of one fact (memory general-mechanisms): either replace the two (spec change, abi) or define them as wrappers. Flag A3. RANK 4 (few uses: bases other than 10/16 are rare).

**D. `ptrdiff_t rx_eqi_index(rx_span s, const char *const *words, size_t n)`**: index of the first `words[i]` equal to `s` ignoring ASCII case (rx_eqi semantics), else -1 (also for unset s). Serves day/month names to number (`Mar` -> 2), keyword membership, command words; replaces a hand loop of rx_eqi (the loop is simple, so error-proneness is low; the value is the index). No tables, no locale (ASCII fold only, as rx_eqi). Overlap: rx_eqi in a loop. RANK 3 (many uses, low error rate).

**E. `int rx_cmp(rx_span a, rx_span b)`**: bytewise (unsigned byte) lexicographic -1/0/1, shorter prefix first; an unset side orders before every set span and two unset spans compare 0 (unset must be flagged by the caller via RX_CAP_SET; ambiguity A6: or return a separate valid flag like cand. A for consistency). Serves fixed-width ISO dates/times, string ordering, span equality (`rx_cmp==0`) including embedded NULs, which rx_eq (NUL-terminated z) cannot express. Overlap: A for digit strings. RANK 5.

**F. `int rx_luhn(rx_span s)`**: 1 when `s` is non-empty, all ASCII decimal digits, and the Luhn sum (every second digit from the right doubled, minus 9 if over 9) is 0 mod 10; else 0. No separators (the pattern strips them or the caller passes digits only). Serves card numbers, IMEI. One fixed algorithm, one standard; hand version is the classic off-by-one (parity from the right, not the left). Seen by hand in pcrec-bench (`ub_luhn`). Overlap none. RANK 3 tie by evidence (the only check digit with in-repo hand code). Flag A7: it is a named domain algorithm, not a span primitive.

**G. `unsigned rx_days_in_month(uint64_t year, unsigned month)`**: 28-31 by the proleptic Gregorian rule (div 4, not 100 unless 400), 0 when month is outside 1-12. Serves date validation (`(\d{4})-(\d\d)-(\d\d)`: rx_u64, then compare day). Hand version: the leap rule is the famous bug. Not a span helper (integers). Flag A4: ruling needed whether the set stays span-only. RANK 6 unless domain helpers are admitted.

**H. `int rx_mod(rx_span s, int base, uint32_t m, uint32_t *rem)`**: remainder of the number spelled by `s` in `base` divided by `m` (1..2^32-1), same validity contract as A, digit by digit, any length. Serves IBAN (mod 97 over base-36 digits, after the caller rotates; because the rotation joins two spans the IBAN case needs two calls with a carried remainder or a pre-built buffer, so the fit is partial), big-number divisibility (`n % 3`), mod 11 checks. Overlap none. RANK 7 (one use case, partial fit).

**I. `ptrdiff_t rx_u8count(rx_span s)`**: number of UTF-8 characters, or -1 for an ill-formed span (rx_u8next's -1 definition), unset -> -1? or 0 (ambiguity A6: rx_u8next treats unset as the end). Serves "at most N characters" limits across a group. Overlap: rx_u8next loop. RANK 5.

**J. `ptrdiff_t rx_count(rx_span s, const char *z)`**: non-overlapping occurrences of non-empty `z`; 0 for empty `z`? (ambiguous, A6). Serves "equal count of x and y". RANK 8, low evidence.

**K. `int rx_i64(rx_span s, int64_t *out)`**: optional `-`/`+` then rx_u64 digits, range check both ends. Serves signed values, offsets, timestamps. Sign handling is where hand code breaks (INT64_MIN). RANK 8.

Declined: Unicode property of a code point (tables; use `\p`), base64 decode (needs an output buffer; template side), anything locale-aware (isdigit/toupper are locale-dependent; every candidate above uses ASCII arithmetic only).

## 4. Cost note
All candidates are `static inline`, no tables, no includes beyond what the family has (stdint/stddef), no locale. A-K together are roughly 120-180 lines of artifact text in every callout artifact (rx_u8next alone is about 15 lines today); unused ones emit no object code but add source size and one abi bump, one spec paragraph each (§11.10 table), and a span_check.c row (the existing checker compares each helper to a reference model).

## 5. Ambiguities for a ruling
- A1 Leading zeros: rx_u64/rx_in accept `007`; A skips them (equal to `7`). Keep, or add a no-leading-zero flag? (IPv4 strictness is a pattern concern.)
- A2 Names: rx_numcmp vs rx_cmp_digits; rx_lit vs rx_z; rx_eqi_index vs rx_index_eqi.
- A3 Cand. C: replace rx_u64/rx_hex (breaking, pre-1.0 abi event) or keep them as fixed-base spellings beside it?
- A4 Is the set span-only, or do domain checks (leap year, Luhn, mod 97) belong? Recommendation: admit only A, B, D now; hold F/G/H as a "domain" row with a trigger of demand (build under measurement).
- A5 Template side (rx_atou, RX_G(1), hexval in inline_c_requirements UC-2): does §11.10 apply there? Spec says every callout artifact carries the helpers; templates were not checked.
- A6 Unset/empty conventions for cand. E, I, J (rx_u8next says unset = end; rx_find says unset = -1). Follow A's separate-valid shape for any candidate that returns an ordering, count or index.
- A7 Sign, `0x` prefix, underscores, and separators (`1,000`) stay out of every helper (pattern strips them); confirm.
