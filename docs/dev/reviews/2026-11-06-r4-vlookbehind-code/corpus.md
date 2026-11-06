# corpus findings

Method: own ctypes driver ($D/chk.py, libpcre2-8 10.46, byte options 0, `encoding utf8` -> UTF|MATCH_INVALID_UTF)
checked EVERY m/n/ms/ns/g/perr cell of 9 files (not a sample): d27/refusals 138 cells, d27/spellings 178,
alpha_spellings 64, gated 14, lookbehind_group_alt 49, lookbehind_variable 54, lookbehind_variable_witness 54,
recursion/d27/sr_interactions 124, recursion/inlookaround 52 (727 cells). Mutation control: 3 planted edits all caught.

## Findings

corpus-1 (doc, CONFIRMED, low): the D27 generators are not runnable in-tree, so d27/README.md's "`gen_refusals.py` emits them"
is only true in a mirrored layout. tests/lookaround/d27/common.py:19-21 resolves la_oracle at tests/lookaround/docs/design/...
(one `..`, path does not exist); tests/recursion/d27/sr_gen.py writes under CELL. Pre-existing (author's cell layout), not
introduced by the subject. In a mirror with the probes at tests/lookaround/docs/design/, gen_refusals.py and gen_spellings.py
reproduce the flipped rows' expectations (same m/n/g lines as the tree; only comment/`features`/`# pcre2-only` line ORDER differs,
triage class 1). sr_gen.py not runnable; its flipped block verified by my driver instead.

corpus-2 (test strength, CONFIRMED, low): tests/lookaround/d27/spellings.rxt:140-143, 151-154, 162-165 -- three flipped blocks
(`(?<*(a|ba))c`, `(*naplb:...)`, `(*non_atomic_positive_lookbehind:...)`) now only `n "ba"`, `n "xa"`: subjects lack `c`, so they are
vacuous (nomatch from any engine, answered or refused-as-nomatch cannot be told apart except via the compile). libpcre2 agrees
(nomatch); the discriminating twins are at :233+ (bac/xac/aac). Author's own subjects, not a wrong expectation.

No wrong expectation, no pcrec-derived expectation, no cell encoding pcrec where libpcre2 differs.

## PROBED-AND-HELD

- All 727 cells above: 0 mismatches vs libpcre2 10.46 (all 15 flipped D27 rows incl. 7 refusals.rxt, 7 spellings, 1 sr_interactions).
- perr cells where libpcre2 ACCEPTS: only backref-in-lookbehind rows (refusals.rxt:188,193; gated.rxt:129) and old gate rows
  (gated.rxt:53,68,86,96) -- the stage-2/gate refusals, unchanged in kind, each with comment; zero-width-repeat divergence rows
  do not appear in any rxt (no pattern libpcre2 refuses carries an answer expectation: checker flags none).
  Witness file's 4 perr (W8,W9,W9b x2) are refused by libpcre2 too.
- Generators: tests/lookaround/gen_corpus.py run into my dir reproduces lookbehind_variable, gated, alpha_spellings, refused (and all 13
  files) byte for byte; p2gen over lookbehind_variable_witness.gen.py and lookbehind_group_alt.gen.py (own probe build of p2probe.c in
  my dir) reproduce both .rxt byte for byte. gen_corpus uses pcre2_ctypes (changed: latin-1 for non-UTF str) but its new cells are all ASCII.
  No generator answer path reads pcrec (gen_refusals/gen_spellings: common.la -> libpcre2; p2gen: p2probe.c; recursion gen_corpus B(): spans via libpcre2 oracle, sr_gen asserts INTENT vs libpcre2 at lines ~1405-1486).
- sr_check.py PCREC_ONLY_PERR emptied: no perr block in recursion/d27/*.rxt is accepted by libpcre2 (none flagged).
- bref_oracle.py: byte mode now hands libpcre2 the pattern's UTF-8 bytes (same bytes pcrec reads); utf8 modes add UTF(+MATCH_INVALID_UTF) with
  boundary-only startpos; utf8-clip = options 0 + ASCII-only guard. Correct for each mode. Subjects now bytes (same lengths as latin-1 str).
  Non-ASCII patterns fed to it elsewhere: none -- every `pattern` line with non-ASCII in tests/ is in utf8/, startset, litscan, assertions/rev_end,
  landwalk, named_groups, modifiers (not bref_oracle callers: callers are run_{backref,dupnames,expansion,lookaround,recursion}_diff.sh over
  backrefs/recursion/lookaround corpora) apart from the NEW witness file's 6 e-acute blocks (byte-mode sweep in run_lookaround_diff.sh §1 is
  then consistent with pcrec's byte reading). No existing oracle answer moved (pre-change a latin-1 str of a non-ASCII pattern could not occur in those corpora).
- D27 discipline: README.md:40-50 and the superseded-in-part notes in la_d27_extract.md:155, sr_d27_extract.md:360 say who (lane vlbbuild,
  manager ruling R1, 2026-11-06), why (stage 1 built the loop), that expectations are libpcre2 10.46's, and which rows stay refused.
