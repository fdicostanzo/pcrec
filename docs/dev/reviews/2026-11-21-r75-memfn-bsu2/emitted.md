# CRITIC emitted: memfn-bsu2 (r75)

## Findings

No finding survived. Every probe below held; nothing is SUSPECTED.


## PROBED-AND-HELD

Compiles used: about 767 pcrec compiles (cap 800), plus 540 invocations that pcrec rejected while parsing options (a
quoting bug in my own driver, --pattern-esc needs a double-quoted value; they did no compile work and finished in about 1 s)
and about 30 gcc/clang builds of emitted matchers. Mask = ONLY `(abi 109)`->`(abi 111)` in line 1 and `.abi = 109,`->`.abi = 111,`;
these are the only two abi readers in an artifact (grep -w 109 on a BASE artifact). Driver: emitted/bin/sweep.py (BASE,
SUBJECT default, SUBJECT `--memfn=...,no-span-vector`, with the deny MERGED into any existing --memfn string).

(a) OUTSIDE the V sites, nothing moves; the deny restores BASE everywhere.
- Corpus sample: 5998 distinct (pattern, flags, encoding) rows from the 343 .rxt files under W/tests. 150 sampled (half drawn from
  rows with a class, quantifier, \w or \d), each x3 compiles, across 6 regimes: off/w32 (30), x86-64-v3 (30), x86-64 w16 (15),
  width 4095 (30), v3 + 4095 (30), --engine=vm (15). Byte and utf8 rows come from the corpus's own encoding column. 79 rows are
  refused identically by both binaries (modules not enabled: assertions, unicode-props, backrefs) with the same rc; 1 rc 125 on
  both. Of the rows that compiled: default == BASE at every non-V site; deny == BASE at all 150; V sites hit: `[a-f]{32}` off and
  `[0-9a-f]{17}` v3 (default moves only at the V call plus __body/selector).
- Targeted (30 + 20 + 20 rows, x3): ofsskip/vrun FUNC sites `(?i)cat` and `abc[0-9]+xyz` at off, x86-64-v3 and x86-64, and
  `(?i)cat` -e utf8 v3: byte-identical to BASE after the mask, default AND deny (the v3 file carries
  rxa_mf1_ofsskip__body/__w16/__w32/selector and MEMFN_FORMS "vrun@w32+w16"; the selector comes through kit_selector and moves no byte).
  T-deny `--memfn=no-span-loop` ([0-9a-f]{32}, [0-9a-f]{40}, [0-9a-f]{100}@4095), T-force `--memfn=span-loop` (same, plus v3 +
  4095): default == BASE (T-deny/T-force ahead of V hold). T-lever `--harness=span-head=8` (pcrec-harness only; plain pcrec rejects
  it), [0-9a-f]{100}@4095, [0-9a-f]{32} off and v3: default and deny == BASE except the #include basename. Floor (E-generic via
  `--memfn=no-window-search`): [0-9a-f]{32}, \w{20}, [0-9a-f]{100}@4095 plain, with span-loop, and with span-head=4 (harness):
  all == BASE. Boundaries that must NOT move hold: [0-9a-f]{16} (off, v3), [0-9]{24}, [0-9a-f]{33}, [0-9a-f]{1002}@4095,
  [0-9]{66}@4095, x[0-9]{26}, ab[0-9]{26} (and under no-fd-d1: D1w), [xy][0-9]{26}, a.{20}b, (a|b)[0-9]{20}, foo\w+bar v3,
  [a-z]+ing v3, \d{3}-\d{4}; --engine=vm [0-9a-f]{17}, \w{20}, [0-9a-f]{32} v3: no move. utf8 per the §11 census: [^\n]{17},
  [^\n]{32}, [0-9a-f]{17}, [aeiou]{17}, [0-9a-f]{20} do not move; [0-9]{25}, [0-9a-f]{25}, [aeiou]{25}, [a-f]{32},
  [A-Za-z0-9_-]{17}, \w{17}, \w{25}, \w{32}, [A-Z]{25}, \d{32}, [+.0-9]{25} move only at the V site; deny == BASE for all.
  w16 layer (x86-64): [A-Z]{25}, [aeiou]{32} move only as at off; [+.0-9]{17} does not move.
- Harness pitfall noted (pre-existing CLI, NOT the subject): a second `--memfn=` flag REPLACES the first (last wins), so
  `--memfn=span-loop --memfn=no-span-vector` drops span-loop. tests/memfn/span_vector_identity.py appends DENY to flags that never
  carry --memfn (LAYERS/ENCS/width only), so the gate is not exposed; any future checker composing the deny with a memfn row must
  merge into one comma string.

(b) AT the V sites, the text is §5's and the answers are identical.
- Reconstruction check (emitted/bin/vchk.py): for each V site, delete the `__body`+selector pair and replace every
  `rxa_mf1_vs0(rxa_mf1_s, rxa_mf1_c)` call by the body's returned expression; the result must equal BASE byte for byte (after the
  abi mask). RECON_EQ on all 26 V sites: [0-9a-f]{32}, \d{32}, [0-9a-f]{17}, [0-9]{25}, \w{20}, [0-9a-f]{31}[0-9] (stretch+stop),
  [0-9a-f]{3}[g-z][0-9a-f]{20} and [a-z][0-9]{25} (lone-test head before the stretch: the walk reads `head && rxa_mf1_vs0(...)`),
  \w{20} / [0-9a-f]{28} / [0-9]{25} / [A-Za-z0-9_-]{17} -e utf8, [0-9a-f]{32} v3, \w{20} x86-64, [\x80-\xbf]{25} v3 (non-ASCII set),
  (?i)[a-f]{20}, [^\n]{20}, and at 4095: [0-9a-f]{100}, {200} v3, {1000}, {1001} (k 1000, last D-hors V cell), [0-9]{64},
  [0-9]{65} (k 64, last R7w V cell), [0-9a-f]{20}[g-z]{20} (two eligible stretches: exactly ONE body, vs0, SMALLEST FORM).
  So the call replaces exactly the stretch chain, nothing else moves, and __body is today's H64 text (k > 64 bodies carry the loop).
- Shape vs §5: `__body` head `static inline __attribute__((always_inline, unused)) int <p>_mf1_vs0__body(const unsigned char
  *rxa_mf1_s, size_t rxa_mf1_c)`, `return <chain>;`; selector `static inline __attribute__((always_inline)) int <p>_mf1_vs0(...)`
  returning `__body(rxa_mf1_s, rxa_mf1_c)` at off, x86-64 AND x86-64-v3 (no rung at U2, as the subject states); placed at file
  scope right after the `_sh` table, before the search function. MEMFN_FORMS / SIMD_GUARDED_BYTES / includes do not move at U2.
  Non-V boundaries [0-9a-f]{16}, [0-9]{24}, {1002}, {66}, \b[0-9a-f]{32}\b (refused by both: module), [A-Z]{25}x, a[0-9a-f]{20},
  xy[0-9a-f]{20}z, \w{5}-\w{20}: no body.
- Builds: 22 V artifacts build with gcc -O2 -Wall -Wextra -Werror, 5 with clang -O2 -Wall -Wextra -Werror (-c); `unused` keeps
  both quiet.
- Answers vs R/kit/oracle (libpcre2-8): 21 V artifacts x 130 subjects each (exact-length match, one byte short, match at subject
  end after 50 bytes of junk, single-byte and empty subjects, a hole mid-run, 120 random mixes with noise bytes \xff \x80 \xc3 /
  utf8 multibyte é and €): 0 mismatches (2730 runs), plus hand cases for the two-stretch site (match 2 42 / nomatch one short / 0 40).

LARGEST witness reached: [0-9a-f]{1001} at --window-search-width=4095 (k 1000, a 1000-position __body), answer-checked on subjects
up to about 3000 bytes; longest R7w: [0-9]{65}@4095 (k 64).

CRITIC COMPLETE
