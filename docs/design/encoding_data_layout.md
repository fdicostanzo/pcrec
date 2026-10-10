# Encoding data layout — the encoding as the organizing unit (inventory, diagnosis, proposal)

> **STATUS (2026-10-09, D159): [ENC-DATA] CANCELLED. Nothing here is scheduled.** Non-UTF byte encodings are out of scope for pcrec (translation layers outside it). Other UTFs wait for a concrete consumer. This note stays as the reference map such an effort starts from: §1's inventory, §2.3's three sites reading code-point bitmaps as bytes. §7's questions are dissolved by D159, except Q5, which moved to [U8-PICK].

**Lane `encinv`, 2026-10-09, opus, from main `57fe04ef` (abi 71). INVENTORY + PROPOSAL
ONLY: nothing under `src/`, `cli/`, `lib/`, `tests/`, `third_party/` or `docs/spec/`
moved.** Frank, 2026-10-09: *"please organize encoding data (it should be to some
degree) around the (currently untrue) idea there may be more encodings. each encoding
data set colocated with its other data sets and organized consistently."*

Every path and line below was found by grep and reading on `57fe04ef`. Two facts were
measured live in this lane's own worktree build (`build/scratch/`, gitignored): the
include-graph back-edge list (§2.5) and the unconstrained `when`/`via` pair (§2.6).

## 0. Findings first

1. **Most of what looks like encoding data is CODE-POINT data, and only a small core
   is keyed to an encoding.** The UCD tables, the fold relation, the C-locale class
   bitmaps and the code-point analyses are facts about characters. An encoding consumes
   them through its own ENCODER and LOWERING. Only the data whose content is BYTES is
   encoding-specific: the backend row and its residual text, the start-byte set, the
   encoder, the byte-level priors (`freq` blocks) and the byte-level oracle captures.
   One file is misnamed by that test: `src/enc/utf8_fold_pairs.inc` holds Unicode fold
   pairs that any Unicode-repertoire backend would include verbatim (§2.1).
2. **There are TWO per-encoding registries, not one.** `src/enc/enc.c`'s `enc_table[]`
   is the declared one. `src/opt/lower_enc.c:439-442`'s `lower_ops[]` is a second table
   keyed by encoding id. Its `identity_max` column restates `PcrecEnc.onebyte_max`
   value for value (0xFF / 0x7F). So the documented third-encoding recipe ("nothing in
   `src/opt` … is touched", `src/enc/CLAUDE.md`) is false today (§2.2).
3. **Five sites infer an encoding CAPABILITY from scalar thresholds or table presence
   instead of reading a declared field** (§2.3). They are `max_cp <= 0xFF` meaning
   "UCP reads Latin-1" (`parse.c:637`), `has_entry(SPAN_CASELESS_UCP)` meaning the
   same thing (`enc.c:213`), `max_cp >= 0x10FFFF` meaning "Unicode universe" (twice),
   `max_cp > 0xFF || start_cls` meaning "multi-byte", and two places that read a
   CODE-POINT bitmap as a BYTE set. The last two are correct only because every
   encoding so far is ASCII-compatible. That assumption is nowhere declared. A
   one-byte codepage (EBCDIC) would be silently misread by three of them.
4. **The two match-time fold tables are produced by two different mechanisms.** utf8's
   is a python-generated, committed `.inc` that is `#include`d into its backend text.
   byte's (K94) is generated in C at EMIT time by the SHARED `enc.c`, behind
   `if (t->id == PCREC_ENCE_SPAN_CASELESS_UCP)` (`enc.c:152-153`). That is an
   entry-id special case in the seam's own emitter. Their `to` columns also mean
   different things: the CaseFolding target versus the least class member (§2.4).
5. **The encoder lives outside its encoding, and the findings layer reaches up to
   get it.** `pcrec_utf8_encode` is defined in the shared `enc.c:375`.
   `encode-latin1` is arithmetic inline in `src/core/findings.c:214-224`. The
   include-graph tool reports `core/findings.c:48 -> enc/enc.h` as one of the tree's
   two layer back-edges, measured on this tree (§2.5).
6. **There are four encoding VOCABULARIES**, and `latin1` means three different things
   in them (§2.6): the compile encodings `{byte, utf8}`; the data-description
   vocabulary `{ascii, utf8, latin1, bytes}` (`rxt_schema.def:323`); the derivations
   `{encode-utf8, encode-latin1}`; and the analyzer's `{ascii, utf8, bytes}` with
   hard-coded `serves` lists (`analyze/count.c:387-401`). A `cpfreq` block's
   `when`/`via` pair is unconstrained, which is legitimate (a `byte` matcher over UTF-8
   text). MEASURED: `serves byte-rate when byte via encode-utf8` parses and stamps a
   digest.
7. **A third encoding touches 15 places today, and 9 of them are avoidable** (§2.7,
   the table).
8. **The byte-frequency prior is no longer "keyed by its contents".**
   `reqbyte_freq_pick.md` §3.2's complaint was answered by D123-4: the table moved to
   `src/findings/default.rxt` with `serves byte-rate when byte via unigram`, a
   DECLARED key. One residue is left: that block says `encoding ascii` while
   carrying 128 rows ≥ 0x80 at the floor (§2.6). [U8-PICK]'s utf8 prior belongs in
   the same bundle as a `cpfreq` block (§5).

**The proposal in one paragraph.** A data set is keyed by the most general axis its
CONTENT depends on. Code points go to the repertoire, organized by SOURCE
(`third_party/<src>-<ver>/` → named tables). Bytes go to the ENCODING (`src/enc/`,
one file per encoding, holding everything that encoding contributes). A corpus goes to
the ANALYSIS, with the encoding as the declared `serves when` key on each block. The
`PcrecEnc` row is the encoding manifest. Every encoding-keyed fact the compiler reads
hangs off that row as a declared field, never as a threshold inference, and the
second table (`lower_ops[]`) is keyed through it. The migration (§4) is eight
no-mover steps proven by `scripts/emit_sweep.py`, plus one spec-moving rename. The two
abi-moving moves (fold-table unification, the [U8-PICK] prior) are separate,
discussed in §7.

## 1. Inventory

Legend for the last column. **E** = reaches emitted bytes (an abi reader when it
changes). **S** = stated in `docs/spec/`. **—** = compile-time only, not in the spec.
"Consumers" lists file:line read sites, not every mention.

### 1.1 The encoding seam itself (`src/enc/`)

| # | path | what | enc | made how | consumers | E/S |
|---|---|---|---|---|---|---|
| A1 | `src/enc/enc.c:22-25` `enc_table[]` | THE registry: one `PcrecEnc*` per encoding, by-id/by-name lookup, name menu | all | hand | ~30 `pcrec_enc_by_id` sites (parse, ir, facts, opt, gen, dump, core); `cli/main.c:354` by name; `rxt_source.c:618` validates `serves when` names | S (`match_api.md` §9.1, cli.md) |
| A2 | `lib/pcrec.h:35-36` `PCREC_ENC_BYTE=0`, `PCREC_ENC_UTF8=1` | public enum, the ids the rows carry | all | hand | `rx_info.encoding` (`emit_dfa.c:3069` emits the integer) | E S |
| A3 | `src/enc/enc_byte.c:322-403` | byte backend: `PcrecEnc` row (`max_cp` 0xFF, `fold` ascii, `onebyte_max` 0xFF, `restrict_ok` true, `start_cls`/`guard` NULL), `entries_byte[]` residual text, `sites_byte[]`, `advance_byte` | byte | hand | emitters via `pcrec_enc_emit_*`; parse/ir/facts via fields | E S (`match_api.md` §3.1.x) |
| A4 | `src/enc/enc_utf8.c:478-626` | utf8 backend: same row shape; entries `next_pos`, span compares, `decode`, `back_step`, `var_valid`, `valid_upto`; `start_cls_utf8[32]` (`:562`), `start_guard_utf8` (`:597`), `advance_utf8` | utf8 | hand (+A5 included) | as A3 | E S |
| A5 | `src/enc/utf8_fold_pairs.inc` | 1,484 `{from,to}` simple-fold pairs AS C STRING LITERALS, `#include`d mid-initialiser at `enc_utf8.c:170` | **content: Unicode; consumer: utf8** | GENERATED by `third_party/ucd-16.0.0/generate.py:148,860` ← `CaseFolding.txt` | utf8 caseless span compare text | E (only artifacts with a utf8 caseless backref/var) |
| A6 | `src/enc/enc.c:120-136` `enc_emit_latin1_fold_table` | byte+UCP caseless compare's `{byte, least-member}` table, generated at EMIT time from `pcrec_fold_latin1_rep` (`core/fold.c:175`) | byte | generated in C at emit time ← B2 | called from shared `enc_emit_defs` `:152-153` on entry id | E |
| A7 | `src/enc/enc.c:375` `pcrec_utf8_encode` | the ONE compile-time UTF-8 encoder | utf8 | hand | `opt/lower_enc.c:239-240`, `core/findings.c:219` | — |
| A8 | `src/enc/enc.c:211-215` `pcrec_enc_span_fold` | "which fold does a caseless span use under UCP": latin1 if the table carries `SPAN_CASELESS_UCP`, else `e->fold` | all (inferred) | hand | `opt/possessify.c:435` | — |

### 1.2 Code-point (repertoire) data: encoding-independent by content

| # | path | what | made how | consumers | E/S |
|---|---|---|---|---|---|
| B1 | `src/parse/uprops_tables.inc` | `\p` property interval lists (gc + 171 scripts × namespaces) | GENERATED ← `third_party/ucd-16.0.0/` (`generate.py:146`) | `mod_uprops.c`, `mod_ucp.c` | E (via lowered automata of `\p` patterns) |
| B2 | `src/core/fold_tables.inc` `pcrec_ucd_fold_links` | simple case-fold as cyclic next-member links (1,454 classes) | GENERATED ← `CaseFolding.txt` (`generate.py:147`) | `core/fold.c:93`: `pcrec_fold_ucd_simple`, `pcrec_fold_latin1`, `pcrec_fold_latin1_rep` | E (folded classes; A6) |
| B3 | `src/core/fold.c:68` `pcrec_ascii_fold[256]` | the 52-letter ASCII partner map (C-locale fold) | hand, deliberately ("a table someone can READ") | `pcrec_fold_ascii`; the `ascii-named` fold row at EVERY encoding (`parse.c:650`); byte's residual compare is tied to it by `tests/backrefs/fold_agreement_check.c` | E |
| B4 | `src/core/fold.c:185-187` `pcrec_fold_{ascii,ucd_simple,latin1}` | the three fold RELATIONS as objects | hand over B2/B3 | `PcrecEnc.fold`, `parse.c` `fold_rows[]` `:646-653` | E |
| B5 | `src/parse/cls_bits.inc` | 20 named byte-range sets (`\d \s \w \h \v`, newline, 14 POSIX), the C-locale chartables at cp ≤ 0xFF | GENERATED by `tests/probes/probe_cls_bits.c --emit` against libpcre2 10.46 (8-bit, non-UTF, non-UCP); PC-4 re-measures | `registry.c:512-550` ports; `mod_classes.c:70-92`; **read as BYTE sets at** `ir/dfa.c:174`, `enc/enc.c:367-368`, `mod_assertions.c:121` | E |
| B6 | `src/parse/registry.c:418-421` `h_def`/`H_def`/`v_def`/`V_def` | the Unicode `\h \v` sets, chosen by tag `DEF_ENCODING_UTF8` (predicate `max_cp >= 0x10FFFF`, `definitions.c:77-79`) | hand | the definitions table | E S (`--list-definitions` prints the tag name, `definitions.c:184`) |

### 1.3 Encoding-keyed compiler data OUTSIDE `src/enc/`

| # | path | what | enc | consumers | E/S |
|---|---|---|---|---|---|
| C1 | `src/opt/lower_enc.c:439-442` `lower_ops[]` | SECOND per-encoding registry: `{id, identity_max, lower_class, pat_char}`; also the UTF-8 length table `:290-295` | byte, utf8 | `ops_for` `:446` (internal error when a ready encoding has no row); `pcrec_pat_char` (the parser's literal reader) | E |
| C2 | `src/parse/parse.c:636-637` `fr_latin1` | "UCP under a one-byte encoding folds by Latin-1", asked as `max_cp <= 0xFF` | inferred | `fold_rows[]` T2 | E |
| C3 | `src/parse/definitions.c:77-79`, `mod_ucp.c:51`, `mod_ucp.c:157-158` | "the universe is Unicode's", asked as `max_cp >= 0x10FFFF` | inferred | `\h \v` row choice, `(*UTF)` port, UCP set clamp | E S |
| C4 | `src/facts/endwin.c:175` | "multi-byte, so decline END_WINDOW", asked as `start_cls != NULL \|\| max_cp > 0xFF` | inferred | `RX_END_WINDOW` (`decline:enc-multibyte`) | E S (`tuning.md`) |
| C5 | `src/core/findings.c:187-189` `find_derivs[]`, `:202-232` | derivations `encode-utf8` (calls A7) and `encode-latin1` (inline arithmetic, drops cp > 0xFF) | utf8, "latin1" | `pcrec_find_block_byte_rate`; `rxt_source.c:589` menu literal | E (FINDINGS digest) S (`findings.md` §3a) |
| C6 | `src/core/findings.c:288` | the compile's encoding NAME, matched against `serves when` lists | all (registry) | `pcrec_find_chain_answer` | E |
| C7 | `src/ir/dfa.c:173-174` `cr_nl_set` | the newline context set = `pcrec_cls_newline` as a BYTE set, `e` ignored | assumes ASCII-compatible | DFA context atoms | E |
| C8 | `src/enc/enc.c:362-370` `pcrec_enc_start_cls_ok` | K50 partition check against `pcrec_cls_word_esc`/`newline` read as BYTE sets | assumes ASCII-compatible | compile-time refusal | — |

### 1.4 Findings (the priors)

| # | path | what | enc | made how | consumers | E/S |
|---|---|---|---|---|---|---|
| D1 | `src/findings/default.rxt` | the shipped default `freq` block: 256 hand-assigned ppm, high half floored at 2; `serves byte-rate when byte via unigram`; `encoding ascii` | **byte only (declared)** | hand ("the one bundle with no generator") | embedded as D4; every `-e byte` byte-rate reader; `-e utf8` reads NONE | E (`<P>_FINDINGS` digest, picks) S (`findings.md` §2, §6) |
| D2 | `src/findings/log.rxt`, `weblog.rxt` | `freq` (`when byte`) + `cpfreq` (`when utf8 via encode-utf8`) per corpus | byte, utf8 | GENERATED by `third_party/{synth-log-lines-v1,elastic-examples-apache-logs-bc53b584}/generate.py` via `build/pcrec-analyze` | only when a compile names them | E S |
| D3 | `tests/findings/default_ppm.tsv` | the pre-B1 table D1 must normalize to | byte | pinned | `tests/findings/` | — |
| D4 | `src/core/findings_store.inc`, `findings_table.inc` | the store's text and pre-parse | per block | GENERATED by `make gen-findings` (`scripts/embed_text.sh`, `scripts/findgen.c`) | `core/findings.c:59,70` | E |
| D5 | `tests/codegen/run_prechecks.sh` [3.7c], [4.5c], [4.9], [4.9b] | witnesses that the byte prior is NOT read under `-e utf8` | utf8 | hand | `make test-codegen` | — (these move when [U8-PICK] lands) |

### 1.5 Vocabularies and enumerations that name encodings

| # | path | what it lists | registry-driven? |
|---|---|---|---|
| F1 | `src/parse/rxt_schema.def:323` | DATA `encoding` closed set `ascii utf8 latin1 bytes` (describes the COUNTED data; never consulted for selection) | no: its own vocabulary |
| F2 | `src/parse/rxt_source.c:612-622` | `serves … when <enc>` validated by `pcrec_enc_by_name` | **yes** |
| F3 | `analyze/count.c:340-352` `classify_encoding`/`enc_rank`; `:387-401` `derive_serves` | analyzer: observed `ascii/utf8/bytes`; writes `when byte,utf8` / `when byte` / `when utf8 via encode-utf8` | no: hard-coded (a zero-dependency binary, `analyze/CLAUDE.md`) |
| F4 | `cli/main.c:161-162` | `--help`: "byte (default) or utf8, both compile" | no |
| F5 | `docs/spec/match_api.md §9.1` ("want byte, utf8"), `docs/spec/rxt_format.md:943` (`byte`, `utf8`), `docs/design/findings/design.md` §2.4 | spec/design sentences enumerating encodings | no |
| F6 | `src/dump/findings_dump.c:133-134` | `--list-analysis` resolution: one row per query × encoding | **yes** (iterates `pcrec_enc_by_id`) |
| F7 | `src/dump/facts_dump.c`, `--emit-facts[=ENC,…]` | facts per listed encoding | yes (by name) |

### 1.6 Oracle captures keyed by encoding

| # | path | what | enc | made how |
|---|---|---|---|---|
| G1 | `oracle_store/libpcre2-10.46/membership.tsv`, `…-10.46-ucp/membership.tsv` | property membership; the question key is `(property, encoding)` (`tests/oracle/oracle_store.py:72`) | rows `utf8` (and `byte` under ucp) | `tests/oracle/build_uprops_store.py`, `tests/ucp/build_ucp_store.py` |
| G2 | `tests/utfcheck/cases_10.46.tsv` | `PCRE2_UTF` validity/startpos answers | utf8 | `tests/utfcheck/gen_cases.py` + `probe_pcre2.c` |
| G3 | `tests/ucp/latin1_fold_10.46.tsv` | `PCRE2_UCP\|CASELESS` (no UTF) partners of each byte | byte | captured against 10.46 |
| G4 | `src/parse/cls_bits.inc` (B5) | the chartables, measured | (cp ≤ 0xFF) | `tests/probes/probe_cls_bits.c` |

### 1.7 Tests, gates, stamps, limits, the bench

| # | path | what | enumerates encodings how |
|---|---|---|---|
| H1 | `.rxt` corpora: 668 `encoding utf8` lines in 38 files (17 in `tests/utf8/`, 5 in `tests/ucp/`), 224 `encoding byte` | each BLOCK declares its encoding, checked against the registry | per block (data-keyed) |
| H2 | `tests/utf8/*_byte.rxt` (6 twins), `tests/ucp/byte.rxt` / `sets_utf8.rxt` | byte controls for utf8 axes; per-encoding UCP sets | file-name suffix, inconsistent (`_byte` suffix, `byte.rxt`, `sets_utf8`) |
| H3 | `tests/codegen/run_encoding_checks.sh` (DD12a(i)/(ii), §8.5 byte/utf8 differential, K49 advance agreement), `tests/utf8/run_startbnd_diff.sh`, `tests/encseam/`, `tests/backrefs/fold_agreement{,_ucp,_utf8}_check.c` | per-backend structural ties and differentials | hard-coded pairs |
| H4 | `tests/harness/verify_rxt.py:378-396` | the python oracle's own next-boundary rule `if encoding == 'utf8'` | hard-coded (an INDEPENDENT second spelling, correct for an oracle) |
| H5 | `scripts/emit_sweep.py:385` `ARM_BASES = {"byte": (), "utf8": ("-e","utf8")}`, `:949` `--emit-facts=byte,utf8`, `:2355` `--bases` default `byte,utf8` | the byte-neutrality sweep's per-encoding bases and floors | hard-coded |
| H6 | stamps: `rx_info.encoding` (A2); `<P>_UTF_CHECK` (`emit_dfa.c:10996`), `<P>_STARTPOS_GUARD` (`:10984`), `<P>_END_WINDOW` decline reason, `<P>_FINDINGS` `byte-rate=none` under utf8 | encoding-derived stamps; none carries the encoding NAME | — |
| H7 | `src/core/limits.def:391` `PCREC_STARTPOS_GUARD_TEXT_MAX` | sized by the BACKEND's guard text (utf8's is 46 bytes) | no other limit is per-encoding (`PCREC_MAX_FIND_CPFREQ_ROWS`, `PCREC_UCP_NARROW_MAX_INTERVALS` are encoding-blind) |
| H8 | `pcrec-bench/testees/pcrec/configs.toml:850-864`, `adapter.py` `effective_encoding` | the bench passes `-e utf8` in `flags` and suffixes the config id `_utf8` | **the encoding NAME is a cross-repo contract** |
| H9 | mech sabotage anchors: 3 rows `SAB_FILE="src/enc/enc_byte.c"`, 10 `enc_utf8.c`, 1 `enc.c`, 4 `src/opt/lower_enc.c`, 4 `src/core/fold.c`, 11 `src/core/findings.c` | path-anchored witnesses | path readers: a move re-anchors them |

### 1.8 Named "encoding" but NOT encoding data (stays where it is)

- `<P>_DFA_TABLE`'s "encoding" is the TRANSITION TABLE's representation (cell width,
  premultiplied or not), not the subject encoding. It is a term collision only.
- The memfn kit (`memfn/src/mismatch.c`) is encoding-blind by construction: the
  backend's `PcrecEncSite` rows describe the fold KIND, and the kit renders a loop.
- `oracle_store/`'s per-`OracleId` layout. The encoding is a question FIELD, which is
  the right key for a store organized by oracle.
- B1-B5. Code-point data is encoding-independent by content (§2.1). Each source keeps
  its home under the `third_party/` rule.
- Test corpora by MODULE (`tests/<module>/`, the house convention). Each block
  carries its encoding as data (H1), and that is already the right shape.

## 2. Diagnosis

### 2.1 Two axes are conflated, and a third is missing from the vocabulary

The repo has a SOURCE axis (`third_party/<src>-<ver>/`, ruled 2026-09-04: "a data
source compiles to generated tables") and an ENCODING axis (`src/enc/`, D58/DD-12:
"everything an artifact carries that depends on which ENCODING … lives in this
directory, in exactly one file per encoding"). What sits between them has no name: the
CODE-POINT data a source produces. That data is independent of every encoding, and an
encoding consumes it through its encoder or lowering.

`utf8_fold_pairs.inc` is the one place the conflation lands in a file name. Its content
(`{from, to}` simple-fold code points) is pure Unicode. Its only utf8-specific property
is its FORMAT (C string literals for the emitted residual), and that format is equally
right for any backend whose repertoire is Unicode: a UTF-16 or UTF-32 backend would
`#include` the same file into its own decode walk. The name says "utf8 data". The
content says "UCD data, emitted-text form". The `third_party/README.md` index has to
spell this out as "the EMITTED form" of the same relation that `fold_tables.inc` holds
in compiler form, which is the symptom.

### 2.2 The second registry, and the recipe that is not true

`lower_ops[]` (C1) is a per-encoding table outside `src/enc/`, selected by id with an
internal-error fallback. It is a sound DD-12 (7) instance ("no `if (enc == UTF8)`"),
but it is a SECOND place a backend must be added. The stage-2 record
(`src/enc/CLAUDE.md`, "nothing in `src/core`, anything above this directory in the
layer order, `cli/` or `lib/` was touched") does not mention that `src/opt/lower_enc.c`
gained the utf8 instance in the same stage, or that `lib/pcrec.h`'s enum value already
existed. The recipe text in `enc.h:49-58` repeats the claim.

**It cannot simply move into `src/enc/`.** `lower_class_utf8` builds AST nodes through
`pcrec_ast_node`, defined in `src/parse/parse.c:60`, so the move would create an
`enc -> parse` back-edge. Lowering is CODE with a little data, and its layer is `opt`.

**Its one data column duplicates the registry.** `identity_max` ("the greatest code
point whose encoded form is its own single byte", `lower_enc.c:24`) is
`PcrecEnc.onebyte_max` ("every code point <= this is written as exactly ONE byte equal
to it", `enc.h:492-501`): 0xFF and 0x7F in both tables. That is two spellings of one
fact with no tie between them.

### 2.3 Capabilities inferred instead of declared

The house rule is no presumed values (memory `pcrec-no-silent-defaults`). These sites
each derive an encoding FACT from a number that happens to separate today's two
encodings:

| site | asks | inferred from | right for a codepage (EBCDIC)? | right for UTF-16/32? |
|---|---|---|---|---|
| `parse.c:637` `fr_latin1` | UCP folds by Latin-1 | `max_cp <= 0xFF` | **no**: UCP over cp037 is not Latin-1's bytes | yes |
| `enc.c:213` `pcrec_enc_span_fold` | the same fact, a second predicate | table carries `SPAN_CASELESS_UCP` | depends on the row | yes |
| `definitions.c:79`, `mod_ucp.c:51,157` | universe is Unicode's | `max_cp >= 0x10FFFF` | yes | yes |
| `endwin.c:175` | multi-byte, decline | `start_cls \|\| max_cp > 0xFF` | yes | yes |
| `ir/dfa.c:174`, `enc.c:367-368`, `mod_assertions.c:121` | newline / word set AS BYTES | `pcrec_cls_*` code-point bitmaps copied as byte sets | **no**: `\n` is 0x25 in cp037 | n/a (multi-byte) |

The first two rows are ONE fact ("which relation folds a caseless contribution under
UCP") spelled by two different predicates in two layers. They agree today because
`byte` is the only encoding that satisfies either. The last row is the undeclared
ASCII-compatibility assumption: code points U+0000..U+007F encode as themselves.
`onebyte_max >= 0x7F` holds for both rows, but nothing checks it.

`src/enc/CLAUDE.md` already records the codepage case under D77 ("A CODEPAGE BACKEND
WILL NOT FIT IT", about `max_cp`). This table extends that record to the four sites
that would MISCOMPILE silently rather than refuse.

### 2.4 One kind of data, two production mechanisms

Both backends have a caseless span compare that folds SUBJECT bytes at match time, so
both need a fold table in the artifact:

| | utf8 (A5) | byte under UCP (A6, K94) |
|---|---|---|
| produced | python, `make gen-tables`, COMMITTED `.inc` | C, at EMIT time, from `core/fold.c`'s links |
| placed into the artifact by | the backend's own text (`#include` inside the string) | the SHARED `enc_emit_defs`, on `t->id == PCREC_ENCE_SPAN_CASELESS_UCP` |
| `to` column means | CaseFolding's target | the least member of the class within Latin-1 |
| control | `fold_agreement_utf8_check.c` (two sources) | "one definition" by construction, plus `fold_agreement_ucp_check.c` |

Each mechanism is sound and each is checked. They are still inconsistent. The byte
side breaks the seam's own rule that the emitter knows nothing about a backend beyond
"copy the text of every entry the MASK names", because `enc.c` names one entry by id.
A third encoding with a match-time fold (any Unicode backend) would have to pick one
of the two shapes or add a third.

### 2.5 The encoder sits in the shared file, and findings reaches up for it

`pcrec_utf8_encode` is utf8's encoder, but it is defined in the shared `enc.c` and
named for one encoding. `encode-latin1`'s encoder (cp ≤ 0xFF → that byte, else drop)
is inline in `src/core/findings.c`. So a third encoding's ENCODER has no designated
home. MEASURED (`python3 tools/review/include_graph.py --out-backedges`, this tree):
the tree has exactly two layer back-edges, and one of them is
`src/core/findings.c:48 -> src/enc/enc.h` (`core -> enc`). It exists to read the
encoding name (C6) and the encoder (C5).

### 2.6 Four vocabularies, and `latin1` means three things

| vocabulary | members | where | means |
|---|---|---|---|
| compile encoding | `byte`, `utf8` | registry (A1), CLI, spec, bench (H8) | how the matcher reads bytes |
| data description | `ascii`, `utf8`, `latin1`, `bytes` | `rxt_schema.def:323`, analyzer (F3) | what the counted exemplar WAS |
| derivation | `encode-utf8`, `encode-latin1` | `findings.c:187-189` | which encoder turns code points into bytes |
| fold relation | `ascii`, `ucd-simple`, `latin1` | `core/fold.c:185-187` | a case relation |

The data-description vocabulary is legitimately separate: `ascii` is a property of data
and not an encoding anyone compiles for. `bytes` against `byte` is a near-collision a
reader trips on. `latin1` is a data description, a derivation and a fold, and the brief
names it as a candidate third ENCODING ("Latin-1-as-code-points"). If that encoding
lands, the word means four things.

**The `when`/`via` pair is unconstrained, and that is correct.** MEASURED in this
lane's scratch: a `cpfreq` block saying `serves byte-rate when byte via encode-utf8`
parses, and `-e byte --analysis mis 'xé'` stamps
`RX_FINDINGS "byte-rate=mis:ae2a5428b495114c"`. This is not a defect. A `byte` matcher
scanning UTF-8 text sees exactly the UTF-8 byte histogram, so the derivation names the
SUBJECT TEXT's encoding, which the compile encoding does not determine. Two things
follow. The derivation vocabulary is a vocabulary of ENCODERS, and it should be
resolvable through whatever owns encoders (§3.3). And `encode-latin1` is, in effect,
`byte`'s own encoder under its UCP reading, which is why its name collides.

**A residue in D1.** `default.rxt`'s block declares `encoding ascii` yet carries rows
for all 128 bytes ≥ 0x80 (the authored floor). `encoding` describes counted data, and
this block is an AUTHORED prior. Neither `ascii` nor `bytes` is true of it.

### 2.7 What a third encoding touches today

Take a hypothetical `X` that compiles. "Inherent" means the place is the encoding's
own data, or a public name that must exist.

| # | place | why | inherent? |
|---|---|---|---|
| 1 | `src/enc/enc_X.c` + `enc.h` extern + `enc.c` row | the backend | **inherent** (the recipe) |
| 2 | `lib/pcrec.h` enum value | the public id | **inherent** (public API) |
| 3 | `src/opt/lower_enc.c` `lower_ops[]` row + `lower_class_X` + `pat_char_X` | lowering is code | inherent for the code; the `identity_max` column is not (§2.2) |
| 4 | `src/core/findings.c` `find_derivs[]` + arithmetic | a cpfreq derivation for X | **avoidable**: resolve `encode-<name>` through the registry's encoder |
| 5 | `src/parse/rxt_source.c:589` derivation menu literal | a hand list | avoidable: render from `find_derivs[]` |
| 6 | `src/parse/parse.c:637`, `enc.c:213` | the UCP-fold fact (§2.3) | avoidable: one declared field |
| 7 | `ir/dfa.c:174`, `enc.c:367-368` | ASCII-compatible assumption | avoidable for any ASCII-compatible X (declare and check); a codepage needs real work |
| 8 | `src/parse/rxt_schema.def:323` | data-description set | only if X is a description of data too |
| 9 | `analyze/count.c:340-401` | analyzer classification + `derive_serves` | partly avoidable: a shared `.def` the zero-dependency binary may `#include` (data, no linkage) |
| 10 | `cli/main.c:161-162` help | hand list | avoidable: print the rendered menu (`pcrec_enc_names`) |
| 11 | spec sentences (F5) | hand lists | avoidable: cite the registry (the rendered menu an unknown `-e` prints, `pcrec_enc_names`) once |
| 12 | `scripts/emit_sweep.py` `ARM_BASES`, `--emit-facts`, `--bases` | sweep bases + floors | the floors are inherent per base; the LIST should be checked against the registry |
| 13 | `tests/harness/verify_rxt.py:378-396` | the oracle's boundary rule | **inherent**: an oracle must spell it independently |
| 14 | tests: corpora, differentials, fold agreement, startbnd | per-encoding evidence | **inherent** |
| 15 | pcrec-bench adapter | `effective_encoding` | the bench's own call (one writer each way, D78) |

Six of the fifteen are inherent and nine are avoidable. Of the nine, four are
zero-mover refactors (§4).

### 2.8 Oracle captures in three homes

Per-encoding answers from libpcre2 live in `oracle_store/` (G1, keyed by
`OracleId` with an `encoding` question field, the designed home), in `tests/<module>/`
(G2, G3, plain TSVs with a comment header) and in `src/parse/` (G4, a generated C table
whose generator sits in `tests/probes/`). Each predates the next. Only G1 has the
store's self-checking header and hash discipline.

### 2.9 What is already right (do not churn it)

- `src/enc/` is one file per encoding, and the backend is a row of data plus text.
- `.rxt` blocks and findings blocks carry the encoding as DECLARED data, validated
  against the registry (F2, H1). D123-4 removed the "keyed by contents" problem that
  `reqbyte_freq_pick.md` §3.2 named.
- `--list-analysis` (F6) already enumerates the registry, so per-encoding findings
  coverage is listable today.
- `third_party/` is organized by source, with the generator beside its data and
  PROVENANCE naming derived files. It needs no change.

## 3. Proposal

### 3.1 The rule

**Key a data set by the most general axis its CONTENT depends on.**

| content depends on | axis | home | named for |
|---|---|---|---|
| characters (code points) | repertoire | the generated table its SOURCE produces (`third_party/<src>-<ver>/generate.py` → `src/<layer>/<src>_*.inc`) | the source (`ucd_`), never an encoding |
| bytes under one encoding | encoding | `src/enc/enc_<name>.c` (or `src/enc/<name>/` once it needs a second file, §3.2) | the encoding |
| a corpus | analysis | `src/findings/<analysis>.rxt`, one block per kind | the analysis; the encoding is the block's `serves when` key |
| what libpcre2 answered | oracle | `oracle_store/<OracleId>/<kind>.tsv` | the OracleId; the encoding is a question field |

**How the two organizing axes compose.** SOURCE → repertoire tables → (an encoding's
ENCODER/LOWERING) → bytes. A source never produces encoding-named data. An encoding
never owns repertoire data, only the function that maps it to bytes. One UCD bump
therefore moves every encoding's derived bytes through one regeneration, and one new
encoding needs no new UCD output. That is the property `reqbyte_freq_pick.md` §3.5
wanted for priors ("one generator … serving every encoding, instead of an N×M grid"),
applied to all repertoire data.

### 3.2 Layout

Recommended: keep ONE FILE PER ENCODING as the unit, which is the shape `src/enc/`
already has, and move into it the per-encoding data that lives elsewhere in
`src/enc/` today:

```
src/enc/
  enc.h, enc.c          the registry and the seam's shared machinery ONLY
                        (no encoding-named function, no entry-id special case)
  enc_byte.c            byte: row, residual text, sites, advance, its encoder,
                        its UCP match-time fold table producer (moved from enc.c)
  enc_utf8.c            utf8: row, residual text, sites, advance, start set/guard,
                        its encoder (pcrec_utf8_encode, moved from enc.c)
  ucd_fold_pairs.inc    (renamed from utf8_fold_pairs.inc) Unicode simple-fold pairs
                        in emitted-text form, for ANY Unicode-repertoire backend
```

**Why not `src/enc/<name>/` directories now.** After the two moves, each encoding has
exactly one file, so a directory would hold one file. The cost is real: the Makefile's
`LIBSRCS` glob (`Makefile:108-112`, one level deep), 14 mech sabotage `SAB_FILE`
anchors (H9) and `run_cpset_structure.sh:518-535` read the paths, plus about 130 files that mention the two
backend paths. D77 trigger: **the first encoding that needs a second file of its own** (a
generated BYTE table, e.g. a codepage's cp↔byte map), and then all encodings move
together so the layout stays uniform. When that happens the file names are fixed now
so the move is mechanical: `src/enc/<name>/backend.c`, `src/enc/<name>/<datum>.inc`.

### 3.3 The registry row is the manifest

`PcrecEnc` is already a declared table, and it becomes the ONE place an encoding-keyed
fact is read from. Each item below is a D58 seam event, recorded as `max_cp`, `fold`
and `restrict_ok` were:

1. **`encode`**: `int (*encode)(unsigned cp, unsigned char b[4])`, returning a length,
   or 0 for "not in this encoding's repertoire". byte: cp ≤ 0xFF → one byte, else 0.
   utf8: today's `pcrec_utf8_encode`. Readers: `lower_enc.c`'s utf8 instance (or the
   row's own, through `e->encode`) and the findings derivation. The derivation
   vocabulary then resolves through the registry. Note the derivation names the
   SUBJECT TEXT's encoding, not the compile's (§2.6), so `via encode-<name>` looks up
   `pcrec_enc_by_name(<name>)->encode`, and `encode-latin1` needs a ruling (Q2).
2. **`ucp_fold`**: `const PcrecFold *`, the relation a caseless contribution folds by
   under UCP. byte: `&pcrec_fold_latin1`. utf8: `&pcrec_fold_ucd_simple`. It replaces
   `fr_latin1`'s `max_cp <= 0xFF` and `pcrec_enc_span_fold`'s table-presence test,
   which are one fact in two predicates (§2.3).
3. **ASCII compatibility is declared and checked, not a field.** `enc.h`'s recipe gains
   the obligation (U+0000..U+007F encode as themselves), and
   `pcrec_enc_start_cls_ok`'s sibling check asserts `onebyte_max >= 0x7F` at the same
   point. No consumer reads a field, so no field is added (D77). A codepage backend
   fails that check by name rather than miscompiling at three sites.
4. **`lower_ops[]` keyed THROUGH the row**: `identity_max` is deleted and readers use
   `e->onebyte_max`. The table stays in `opt` (layering, §2.2), and the recipe text
   names it as the one code site outside `src/enc/` a backend adds (step E8).

What is NOT added: a `--list-encodings` surface, a separate manifest file, or a
`PcrecEnc` field for each data kind. Until a third encoding is requested, the manifest
is the row plus §3.4's table (D77).

### 3.4 The encoding data manifest, documentation tier

`src/enc/CLAUDE.md` gains one table, with data KINDS as rows and encodings as columns.
Each cell is a path or `none: <reason>`. The kinds are: backend row; residual entries;
advance; start set/guard; encoder; lowering instance; case fold; UCP fold; match-time
fold table; default byte-rate prior (which block of `default` serves it, or NONE);
oracle captures; test corpora; sweep base. A row that is `none` for one encoding
states why (byte's start set: "every position is a start"; utf8's default prior:
"none until [U8-PICK]"). It is the list a reviewer checks a third encoding's change
against, and the list of KINDS is the control for any later machine check (§6, Q2).

### 3.5 Priors stay analysis-keyed

The findings shape is already right. A bundle is a fact about a corpus, a block's
`serves when` line is its encoding key, and a `cpfreq` block serves any encoding
through that encoding's encoder. Splitting priors per encoding
(`src/enc/utf8/prior.rxt`) would rebuild the N×M grid that `reqbyte_freq_pick.md`
§3.5 rejected. The encoding-specific part of a prior is the DERIVATION, which belongs
to the encoder (§3.3 item 1). The one fix in this area is D1's `encoding` line, which
should state what the authored block is (Q4).

### 3.6 Repertoire data keeps its homes, with one rename

`uprops_tables.inc`, `fold_tables.inc`, `pcrec_ascii_fold`, `cls_bits.inc` and the
`pcrec_fold_*` relations do not move. `utf8_fold_pairs.inc` becomes
`ucd_fold_pairs.inc` (§4 E5). Unifying the two match-time fold tables (§2.4) is
discussed in Q3. It is an abi event and is not part of the no-mover migration.

### 3.7 Vocabularies

- The compile-encoding name is the registry's, and every hand list of it (F4, F5,
  `rxt_source.c:589`) is rendered from the registry or rewritten to cite it.
- The data-description vocabulary stays separate and gets one sentence in
  `findings.md` §2 saying why it differs from `-e`. Renaming `bytes` is Q4.
- The analyzer's `derive_serves` hand table moves into a data-only `.def`
  (`analyze/serves.def`, an X-macro of (observed encoding, kind) → `when`/`via`) when a
  third encoding first needs an edit there. D77, and the binary stays zero-dependency.

### 3.8 Tests, oracles and the sweep

- No corpus moves. New encoding-specific `.rxt` files use the suffix
  `<topic>_<encoding>.rxt` (H2 shows three spellings today).
- New oracle captures keyed by encoding go to `oracle_store/<OracleId>/<kind>.tsv`
  with the `encoding` question field. G2/G3 migrate when their reader is next
  regenerated. G4 stays a C table (its consumer is the compiler) but its PROVENANCE
  line names the OracleId.
- `emit_sweep.py`'s `ARM_BASES` stays a PINNED list (it carries per-base floors), and
  it gains a coverage assertion: the pinned base names must equal the registry's
  names, read from the compiler's rendered menu. That way a new encoding cannot be
  silently absent from the sweep. The list and the registry are two sources, so the
  check is a real control. It is built WITH the third encoding, not before (D77).

## 4. Migration: no-mover steps

Each step is proven the same way. Run `scripts/emit_sweep.py` against a `git archive`
of the step's parent: streams 1-4 and 6 byte-identical at both bases, stream 5
identical except where noted, and all variants at `--variant all`. Run
`make test-codegen` (DD12a(i)/(ii), K49 advance agreement), the `make test` sections
`test-backrefs` (all three fold agreement checks), `test-uprops` (the `generate.py
--check`), `test-findings` (§2/§3/§12) and `test-encseam`, and `include_graph.py`
(back-edges ≤ 2). The sweep's reference is built from an archived revision and never
from the working tree, which is what makes it an independent control.

| step | change | movers | abi? | spec? |
|---|---|---|---|---|
| E0 | §3.4 manifest table in `src/enc/CLAUDE.md`; `enc.h`/CLAUDE recipe text corrected to name `lower_ops[]` and `lib/pcrec.h` (§2.2) | none (docs) | no | no |
| E1 | move `pcrec_utf8_encode` from `enc.c` into `enc_utf8.c`; add `PcrecEnc.encode` (byte + utf8); `lower_enc.c` and `findings.c` call `e->encode` / the by-name row | none | no | no |
| E2 | delete `LowerOps.identity_max`; read `PcrecEnc.onebyte_max` | none (same values) | no | no |
| E3 | add `PcrecEnc.ucp_fold`. `fold_rows[]`'s `latin1` row becomes a `ucp` row: predicate `cx->mods->ucp`, action `e->ucp_fold`. Under utf8 that is `ucd-simple`, which is what the `encoding` row answers today. `pcrec_enc_span_fold` returns `ucp ? e->ucp_fold : e->fold`. The table is not listed by any dump, so renaming the row is internal | none: both old predicates select the same relation per encoding today, and the sweep's `--ucp` and `-i` arms are the witnesses | no | no |
| E4 | the latin1 match-time table producer moves into `enc_byte.c`, attached to its entry row as a data hook (`PcrecEncEntry.emit_data`, NULL elsewhere); `enc_emit_defs` loses the entry-id test | none (same text, same position) | no | no |
| E5 | rename `src/enc/utf8_fold_pairs.inc` → `ucd_fold_pairs.inc` (`generate.py:148`, `Makefile:190`, `enc_utf8.c:170`, `third_party` README/CLAUDE/PROVENANCE); regenerate (the header comment changes, and it is outside the emitted string literals) | none emitted; the `.inc` header text moves | no | no |
| E6 | findings derivations resolve the encoder through the registry: `encode-utf8` → `pcrec_enc_by_name("utf8")->encode`. `encode-latin1` stays bound to byte's encoder pending Q2. The menu literal `rxt_source.c:589` is rendered from `find_derivs[]` | none (the digest is over the ppm table, `findings.c:332`) | no | no |
| E7 | assert ASCII compatibility (`onebyte_max >= 0x7F`) at registry check time; `enc.h` recipe states it | none | no | no |
| E8 | rename the definitions tag `DEF_ENCODING_UTF8` → `DEF_ENCODING_UNICODE` (its predicate is already the capability) | **`--list-definitions` output** (`definitions.c:184` prints the tag; 4 rows today) → emit_sweep stream 5 shows the expected mover; no test pins the name (grep) | no | **yes**: `docs/spec/registry.md` §9 (the closed tag list) and `cli.md (old line 228)`, in the same change (D80) |

E1-E7 touch `src/` but add no emitted byte. E1/E2/E3/E4 each add or remove a
`PcrecEnc`/`LowerOps`/`PcrecEncEntry` field, and each is recorded as a D58 seam event
in `src/enc/CLAUDE.md`. That is the house's established ritual. Path-anchored mech
rows: E1/E4 move code within files that rows anchor to (14 rows on `enc_*.c`/`enc.c`,
11 on `findings.c`), so the steps' lane re-verifies each touched anchor from
`git show HEAD:<path>` (BOILERPLATE's re-anchor rule). The recommended §3.2 layout
moves no file.

**What is deliberately NOT a no-mover step**, with the reason:

- Fold-table unification (Q3): the utf8 table's representatives change, so every
  utf8 caseless-reference artifact moves. abi bump plus identity re-pin (D76/D94).
- The [U8-PICK] utf8 prior (§5): every `-e utf8` artifact whose readers ask byte-rate
  moves its `<P>_FINDINGS` stamp and possibly its picks. abi event, `findings.md`
  hunk, and the D5 witnesses re-pinned.
- Per-encoding directories (§3.2): its trigger has not fired.

## 5. Where the [U8-PICK] utf8 byte-rate prior lives

**In the default analysis, `src/findings/default.rxt`, as a second block:** `cpfreq`,
`serves byte-rate when utf8 via encode-utf8`. That is u8pick0's sketch, and it is the
layout §3.1 prescribes. The data is code points about a text class (repertoire content
about a corpus). The encoding-specific part is the `serves` line plus utf8's encoder.
`default` stays the chain terminal by identity, and the bundle's two blocks can never
collide because they serve different encodings ([r2 M-B1]). In the §3.4 manifest,
utf8's "default byte-rate prior" cell changes from `none until [U8-PICK]` to
`default.rxt cpfreq (via encode-utf8)`.

**If the rows are GENERATED** (from an independent, licensable multilingual exemplar,
per u8pick0's own caveat and D83), the exemplar goes in `third_party/<source>-<ver>/`
with `PROVENANCE.md` naming `src/findings/default.rxt`'s `cpfreq` block as what derives
from it, and with a `generate.py`. That makes `default.rxt` partly generated, which
contradicts its header ("the one bundle with no generator") and gives one file two
writers. The obvious way around that is a generated sibling bundle that `default`
`include`s, and it **does not work today**. The terminal is appended as ONE link by
identity, and its own `include` is never followed (`src/parse/rxt_find.c:309-317`;
`findings.md` §7). Making it work would be a resolution-semantics change with a
`findings.md` §7 hunk. Q5 is the ruling.

My leaning is to AUTHOR the utf8 block, the way the byte half is authored. The shares
should be documented, citable script and text-class priors in the bundle header,
following `default.rxt`'s own independence discipline. That keeps one writer and
needs no chain change. An exemplar-measured multilingual prior then ships as a NAMED
analysis (`weblog`'s shape) that a deployment opts into with `--analysis`.

## 5a. Other placements checked

None of the alternatives fits better. A per-encoding `src/enc/utf8/prior.rxt` would
re-split the data by encoding (§3.5). A `freq` block would be keyed `when utf8`, but
its content is a byte histogram of one corpus under one encoding. That is legal, but
it cannot also serve a future UTF-16, while the `cpfreq` block can.

## 6. The three standing questions

1. **The measurement regime.** *Relevant only to §5.* This design reads and produces
   no measured number. Its migration is byte identity, which is regime-free. The
   [U8-PICK] prior is a corpus statistic, and its regime is (exemplar, the encoding
   it serves, derivation). Its timing evidence (u8pick0: 7700X, gcc 15.2, scratch
   tier, load1 ~9-60) belongs to [U8-PICK]'s landing, not to this layout.
2. **The independent control.** *Relevant.* (a) Every step's control is
   `emit_sweep.py` against an archived reference build, a different source from the
   working tree. (b) The fold agreement checks stay two-source; E4 must not turn
   `fold_agreement_ucp_check.c` into a self-comparison (it reads the EMITTED table,
   so the move keeps it honest). (c) Any later manifest check (§3.4, the
   `ARM_BASES` assertion) must take its expected list of KINDS or encodings from a
   fixture, never by enumerating the registry it checks (learnings §3, K35). (d) No
   new sabotage row is designed here; E3/E7 would want one each (a backend whose
   `ucp_fold` disagrees with `fold_rows`, a backend with `onebyte_max < 0x7F`), with
   ids from a range the manager assigns.
3. **What moves when data is regenerated.** *Relevant.* A UCD bump moves B1/B2 → the
   lowered automata of `\p`/caseless patterns under every encoding, and A5 → utf8
   caseless-reference artifact text. That is a re-measurement event (D26) and a
   corpus re-pin, not a scaffolding abi event, as today. Editing D1 moves the
   FINDINGS digest and possibly the picks of every `-e byte` artifact with a byte-rate
   reader (`findings.md` §6 says so). G1-G4 recaptures move test expectations only.
   E5's regeneration moves only the `.inc` header comment. This proposal changes none
   of these consequences. It makes the per-encoding ones listable (§3.4).

## 7. Open questions for Frank (discussion)

**Q1. Directories per encoding now, or at the trigger?** The problem is that Frank's
phrase "each encoding data set colocated" reads most naturally as `src/enc/<name>/`.
On one side is a uniform shape that a third encoding drops into. On the other is a
one-file directory per encoding today, 14 sabotage anchors, a Makefile glob and about
130 files that mention the backend paths. My leaning is one file per encoding now (it is already colocated once
E1/E4 land) and directories at the first encoding needing a second file, all
encodings moving together. I would bat this around if you read "colocated" as
directory-shaped regardless.

**Q2. What does `encode-latin1` become?** The problem is that the derivation is
byte's encoder under its UCP (Latin-1) reading, it is spelled `latin1`, and "latin1"
is a candidate third encoding. The forces: no shipped bundle or analyzer output uses
it (only the spec and tests), D44.2 permits no aliases, and a rename is a format/spec
change (D80) but not an abi event (the digest is over rates). My leaning is to bind
derivations to registry names (`encode-<registry-name>`, so `encode-byte`) and retire
`encode-latin1` in the same change. If a real `latin1` encoding ever lands, it owns
`encode-latin1`. The alternative is to keep `encode-latin1` as a named codepage
encoder independent of the registry, which keeps two encoder namespaces.

**Q3. Unify the two match-time fold tables?** The problem is two production
mechanisms (§2.4). The forces: K94's emit-time generation from the one relation is
the stronger discipline (one definition), and it would delete the only generated file
in `src/enc/`. But utf8's `to` column is CaseFolding's target and the links cannot
reproduce it, so unifying means switching utf8 to least-member representatives. That
is equally correct for an equality compare, and it moves every utf8 caseless-reference
artifact (an abi event). My leaning is not now (D77, nothing is broken). E4 removes
the seam violation at zero movers. Unify when a third Unicode backend wants the table.

**Q4. The data-description vocabulary (`ascii utf8 latin1 bytes`).** The problem is
that `bytes` sits beside `byte`, and D1 claims `ascii` for an authored table with 128
high-byte rows. My leaning is to keep the vocabulary (it describes data, not
compiles), give D1 an honest value (`bytes` is the closest member; an `authored`
member would be more accurate but grows a closed set for one row), and add one
sentence to `findings.md` §2. I have no strong view between `bytes` and a new member.

**Q5. Is the shipped utf8 prior authored or generated?** See §5. The problem is that
the default analysis has one hand-authored file, and a generated block would give
that file two writers. The sibling-bundle escape needs the chain terminal to follow
its own `include`, which it does not today (`rxt_find.c:309-317`). The forces: an
authored structural prior is cheap and keeps one writer, but its shares are
assumptions (u8pick0's caveat, and the K35 trap if they were ever fitted to bench
subjects). A generated prior is evidence-based, but it needs either a terminal-
include change (a `findings.md` §7 spec hunk) or region-generation inside
`default.rxt`. My leaning is authored, with documented citable shares, plus an
exemplar-generated NAMED analysis for deployments. Either way, the layout question
is settled: the block lives in the default analysis as `cpfreq ... when utf8 via
encode-utf8`.

**Q6. Should the ASCII-compatibility obligation be a ruling?** The problem is that
three sites (§2.3, last row) read code-point bitmaps as bytes. Declaring the
obligation (E7) means "pcrec encodings are ASCII-compatible" is a design limit, and an
EBCDIC request would then be a design stop, not a backend. My leaning is yes: say it,
check it, and record EBCDIC under D77 beside the codepage `max_cp` note.

## 8. Not built (D77), with triggers

- `src/enc/<name>/` directories. Trigger: an encoding needs a second file of its own.
- A `--list-encodings` surface or a machine-checked manifest. Trigger: a third
  encoding is requested, or the bench asks for an encoding listing.
- `analyze/serves.def`. Trigger: the first analyzer edit a new encoding would force.
- The `ARM_BASES` coverage assertion. Trigger: built with the third encoding.
- Migrating G2/G3 into `oracle_store/`. Trigger: their next regeneration.
- Fold-table unification (Q3). Trigger: a third Unicode-repertoire backend.
