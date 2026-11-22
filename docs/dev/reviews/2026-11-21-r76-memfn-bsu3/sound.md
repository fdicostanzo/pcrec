# CRITIC SOUND: r76 memfn-bsu3

## Findings

NONE. No subject finding: every probe in PROBED-AND-HELD below held (0 differ, 0 fault, SUBJECT = BASE).

KIT NOTE (not a subject finding, relayed to crit-memfn-bsu3 by SendMessage): kit/oracle.py `--utf`
passes 0x00080000|0x20000000. 0x20000000 is PCRE2_ENDANCHORED (/usr/include/pcre2.h:107), not
PCRE2_MATCH_INVALID_UTF (0x04000000). With ORACLE_OPTS=--utf both trees showed 598-760 false
differences per artifact, plus -4/-9 errors on invalid UTF. This lens re-diffed against a corrected copy,
sound/bin/oracle_n.py (UTF|MATCH_INVALID_UTF, no UCP, which is pcrec's -e utf8 without --ucp; a UCP oracle
copy oracle_u.py differs on `\w` for both trees, which is expected because pcrec does not imply UCP).

### Matrix product (stated before the runs, then run)
About 54 patterns x {SUBJECT, BASE} plus 40 random sets (SUBJECT only) plus 8 artifacts x 7 consumer
flag columns, about 350 compiles in total including ~150 emit-only discovery calls. The cap is 600.

## PROBED-AND-HELD

Method: kit check.sh (guard-page runner, layouts R and L, against libpcre2-8) on SUBJECT and BASE, with
the got.txt files cmp'ed between the trees. Generator sound/bin/gen.py puts a near-miss byte at EVERY
template position: (a) nibble-crossing non-members, (b) member^0x80 (which tests the b0/b1 split),
(c) member+-1, (d) 00/0a/7f/80/ff. It also builds: a later match after the miss, overlapping matches,
lengths L-3..L+1, prefixes and suffixes of 1/2/3/31/33 random bytes, periodic misses at periods
15/16/17/31/32/33/L-1/L/L+1 over runs of 3L+40 bytes, and 200 random mostly-member subjects. In each R
layout the match ends flush against the high guard page; in each L layout the subject starts flush
after the low guard page. Every probed artifact's reach was checked with `grep -c __w32_b art.c` and
MEMFN_FORMS: 77 of 90 artifacts render the block (span-vector@w32). The other 13 are the intended
controls (none), counted apart.
Totals: 57,058 subjects x 2 layouts; 45,005 subjects on block-rendering artifacts. 0 differ, 0 faults
on SUBJECT, on BASE, and SUBJECT-vs-BASE.
Witness size: K min 16 (`[0-9a-f]{17}`), K max 1000 (`[0-9a-f]{1001}`, width 4095). Subject length 0 to
4008 bytes.

- (a) boundary, window row D-hors (LO 0). At width 4095, K = 16,17,31,32,33,63,64,65 and 1000 all hold
  (B=16 for K<32, B=32 for K>=32, checked in the emitted `i + B < K`). The n=1002 control (K 1001) is
  none. At default width 32: K 16,17,31.
- (a) scan row R7w (`[0-9]{n}`, LO 1). K 24,25,31,32,33,63,64 at width 4095, and K 24,31 at width 32.
  The n=66 control (K 65) is none.
- (a) LO != 0 and the V stretch not the site's first: `[g-z]{3}[0-9a-f]{20}` (LO 3),
  `[a-c]{5}[0-9]{25}` (LO 6), `[a-z][0-9]{25}` (LO 2), `.[0-9a-f]{20}` (LO 1), `[g-z]{2}[0-9a-f]{40}`
  (LO 2, B 32), `[a-c]{5}[0-9]{60}` (LO 6, K 59), `[g-z]{7}[0-9a-f]{65}` (LO 7, K 64), and
  `[0-9a-f]{20}[g-z]{20}` (a second eligible stretch, which falls to T-head: one block). All hold. I read
  the bound against the read range in the emitted text: C7 bound `c + 64 < n`, reads [c+6, c+65); B65w
  bound `c + 64 < n`, reads [c+1, c+65).
- (b) sets. `[^\n]` (255 bytes, K 19 and 39). `[\x70-\x7f\xf0-\xff]` (lo_t/hi_t entries -128: high
  nibble 7 and 15; K 19, 39). `[\x80-\xbf]` (it reaches V as a scan site, LO 1, K 24 and 39; it does not
  reach V at {20}). `[^0-9]`, `[\x00-\x7f]`, `[a-z\x80-\xff]`, `[\x00-\xfe]`, `[\x01-\xff]`, `[^\x80]`,
  `[^\x7f]` were found to reach V by discovery. `(?i)[a-f0-9]`, `(?i)[k-s]` (K 39), `\w`, and 40 seeded
  random sets (dense, both halves with nibble 7/15 members, range unions, sparse; 34 of 40 reach V, at K 19
  and K 39). All hold. A one-byte set (`[a]{20}`, `a{20}`-shaped) and `[\x7f\xff]` take a run or vrun
  form, not V, so the brief's "one-byte set" cell is unreachable for V.
- (b) -e utf8 (the corrected oracle, valid-UTF and random-byte subjects, multibyte é/€/ſ/K/ß/emoji at
  every position): `\w{20}`, `\w{40}`, `[\x00-\x7f]{20}`, `[0-9]{33}` (V, K 32, B 32). Also the controls
  `[0-9a-f]{17}` and `[a-z]{3}[0-9a-f]{40}` (none under utf8). 0 differ on both trees. Caseless and
  `[^\n]` under utf8 do not reach V.
- Consumer flags: 8 block artifacts (A17w, A34w, A65w, B65w, C7, C9, D2, D4) rebuilt at gcc -O0/-O2/-O3/
  -Os, gcc -O2 -march=native, clang -O0/-O2. All 56 builds give answers identical to the check run, with
  0 faults. The artifact's own pragma region supplies AVX2 without -mavx2.
- Controls: -fmemfn-simd=x86-64 (w16 only), -fno-memfn-simd (the default) and --memfn=no-span-vector all
  render no block, and their answers hold. Under the first two the selector calls `__body`; under the
  deny there is no V at all. --engine=vm and alternation sites do not reach V.
- Hand-check, by reading. vs_table writes t[15]..t[0] per copy (`_mm*_set_epi8` takes the highest lane
  first), and writes a value over 127 as value-256. I checked the emitted `[0-9a-f]` table by hand:
  `0,0,0,0,0,0,8,8,8,72,72,72,72,72,72,8`, which is t15..t0 for lo_t[0]=8, lo_t[1..6]=72, lo_t[7..9]=8.
  The bit table puts 1<<n in lanes 0..7 and 1<<(n-8) in lanes 8..15 of each 128-bit half, which is
  correct for per-lane vpshufb. The hn computation, srli_epi16 by 4 then &15, takes no bits from the
  neighbouring byte. wf_at(base "S + C", LO) gives `S + C`, `S + C + LO` or `S + C - x`. The last form
  is unreachable because wf_loop_len requires off >= 0. The loop reads [i, i+B) with i+B < K and the
  tail reads [K-B, K), and K >= B by the choice of B. The K >= 16 kit_fail precedes every text.

CRITIC COMPLETE
