# CRITIC modularity: dpcompact (r97)

## Findings


### MOD-1 — clsets.k53() (study + frozen ref copy) still depends on the writer's ROW ORDER, which ucd_dump.c and ucd_tables.h now both declare "not a contract"
CONFIRMED (pre-existing dependence, carried across the new seam). severity: maintenance/answer-latent. effort: S (filter on `ns & 1`). blast: tests/clskit population + studies/cls_tree_study.
- `tests/clskit/ref/clsets.py` and `studies/cls_tree_study/clsets.py` `k53()`: `if name in want and want[name] not in got` ignores the row's `ns`. The name `L` has two rows in the dump: row 641 `L ns=1` (General_Category Letter, 7030-char set) and row 642 `L ns=8` (`bc=L`, Bidi Left-to-Right, a DIFFERENT set). k53 picks gc=L only because the writer emits ns=1 first. ZZZZ likewise (ns=2 before ns=5; same set today).
- repro: `awk -F'\t' '$1=="L"' kit/sets_subject.tsv` -> two rows, differing sets; read k53's loop.
- Expected: a reader of an interface whose order is "not a contract" must select by (name, ns). Swap generate.py's sort of those two rows and K53's "L" population silently becomes Bidi_Class=L.
- Why in scope: the subject rewrote `_parse_inc` (both copies) to read the interface's TSV and wrote "Rows come in the interface's row order, which is not a contract" into ucd_dump.c:17-18 — the one caller that DOES depend on order was left as is.

### MOD-2 — `pcrec_ucd_find`'s contract is "the FIRST row whose mask intersects", i.e. writer order IS observable through the interface; the uniqueness invariant that makes it harmless is neither stated nor asserted
CONFIRMED (contract/doc gap; no wrong answer today). severity: design/doc. effort: S. blast: ucd_tables.h:40, generate.py.
- ucd_tables.h:19-20 says "Row ORDER is the writer's and is not a contract"; ucd_tables.h:40 defines find as "The first row named ... whose mask intersects `ns`". With a multi-bit `ns` (the parameter is a mask) two rows can qualify and order picks the answer.
- Measured over the dump (1384 rows, 881 names, 342 multi-row names, 260 of them with differing sets): 0 pairs of same-name rows have intersecting masks. So today "first" == "the only", and every in-tree caller passes a single bit.
- Fix: state the invariant in the header ("at most one row per (name, namespace bit); `ns` is one bit") and have generate.py assert it (or ucd_tables.c take a single bit). Then the order disclaimer is true rather than aspirational.

### MOD-3 — the wall's private-symbol needle is a HAND-COPIED list of the writer's current array names; a new array the writer adds is invisible to it
CONFIRMED (by construction). severity: maintenance (check adequacy). effort: S. blast: tests/core/ucd_wall_check.sh:89-90.
- `b='\bucd_(iv_blob|set_off|set_n|name_blob|row_name|row_ns|row_set|row_ci_set)\b'` restates generate.py's emit() symbol list (the .inc today defines exactly these 8 statics + `UCD_GEN_*`, listed by `grep -nE '^(static|#define)' src/parse/ucd_tables.inc`). The next format change (e.g. a `ucd_row_flags[]` or a two-stage index) adds a symbol the wall does not know, and a caller that `extern`s it passes — the control (a planted #include) still passes, so nothing reports the drift. This is a check whose population is a second copy of what it controls (learnings §3 / K35 shape).
- General form: derive the needle from the product itself (every identifier the .inc defines at file scope), or have the writer give every private symbol one prefix (`ucd_`/`UCD_GEN_`) and assert it, then match the prefix minus the interface's own `pcrec_ucd_` names. See MOD-4 for the prefix collision that makes the second route need care.

### MOD-4 — `pcrec_ucd_` is now the new interface's prefix AND the private symbol of a sibling generated table (`pcrec_ucd_fold_links`, fold_tables.inc, read by fold.c)
CONFIRMED. severity: maintenance/naming (D174 names-describe-behaviour adjacent). effort: S (rename either side; fold_tables.inc rename is generator + fold.c + data_plan prose). blast: src/core/fold.c:93-141, src/core/fold_tables.inc, generate.py.
- `grep -n pcrec_ucd_fold_links src/core/fold.c` -> 6 sites; ucd_tables.h claims `pcrec_ucd_*` as "THE ONE INTERFACE" (`pcrec_ucd_find/_contains/_row_*/_unicode_version`). A reader (or a future prefix-based wall, MOD-3) cannot tell an interface call from another table's raw array by name; a prefix-based needle would flag fold.c, a prefix-based allow would let a caller of the raw fold array through.

### MOD-5 — the wall exempts ALL of `docs/` and every `*.md`, so ~2,000 code files are outside its population, including a live second reader of the format the charter's sizes were measured with
CONFIRMED. severity: maintenance/check-population. effort: S (scope the exemption to prose suffixes, or retarget/retire the instrument). blast: ucd_wall_check.sh:100; docs/design/data_plan/formats.py.
- `git ls-tree -r --name-only SUBJECT -- docs | grep -vE '\.(md|txt|tsv)$'` -> 1,161 .py, 364 .sh, 196 .c (and more) under docs/, none scanned (`case ... docs/*) continue`).
- `docs/design/data_plan/formats.py` (the §1.2 storage-format instrument, listed in docs/design/data_plan/CLAUDE.md:9 as live) regex-parses `pcrec_uprop_iv[] = {` / `pcrec_uprop_names[] = {` out of a `uprops_tables.inc` — the retired format; it is now dead against SUBJECT and would be an offender (needle `d` matches it) were docs/ scanned. A re-measure of A1-compact's sizes (the charter quotes them) has no instrument that reads through the interface.
- The control plants into mod_uprops.c only, so the exemption's reach is never exercised.

### MOD-6 — tests/registry/pcre2_check.c now includes the interface yet still spells the namespace numbering as literals (`{1u,""},{2u,"sc="}..{32u,"age="}` and `bit & (16u | 32u)`), a second, unasserted copy of the numbering
CONFIRMED. severity: maintenance. effort: S (use PCREC_UCD_NS_*). blast: tests/registry/pcre2_check.c ~3475-3485.
- Pre-existing literals, but the reason they were literals (the numbers lived only in the generated .inc) is gone: the subject added `#include "parse/ucd_tables.h"` to this file. Renumbering PCREC_UCD_NS_* (the module's own `_Static_assert` keeps writer and header in step) would leave this sweep testing `\p{sc=..}` with the wrong prefix per row, and the extension branch keyed on the wrong bits. `uprops_names.py` keeps its own numbers deliberately AND checks them against the dump's `#ns` lines; this file does neither.
- Same in the study copy studies/linktest_probe/pcre2_check_linked.c (see MOD-8).

### MOD-7 — `pcrec_ucd_contains` re-implements both halves of the module: the row scan of `pcrec_ucd_find` and the varint walk of `ucd_decode` (two copies of the format's decode loop inside the one module)
CONFIRMED (code reading). severity: maintenance (house rule: one home). effort: S. blast: src/parse/ucd_tables.c:144-176.
- ucd_tables.c:147-150 vs 159-162 (same name/ns/len/memcmp scan); 126-131 vs 166-171 (same `lo = prev + varint; hi = lo + varint; prev = hi`). The format comment is the module's contract with its writer; a change to the interval encoding (say `lo - prev_hi - 1`, which the non-adjacent invariant allows and saves bits) must be made twice in the file, and only `find` is exercised by the byte-identity corpus at scale (`contains` serves mod_code / mod_named_groups only).
- Fix: one private `ucd_row_of(name, len, ns)` -> row index or -1, and one private cursor `ucd_next(&p, &prev, &lo, &hi)`; find/row_set/contains become three short callers.
- Side note (SUSPECTED speed, not this lens; for the speed critic): the old callers binary-searched a decoded span; `contains` is a linear early-exit walk, so a per-character test of a high code point against `L` (677 intervals) decodes ~1,350 varints, plus the 1,384-row strlen scan per call, per character of a code segment / group name. Confirm with a long non-ASCII `(?<name>)` or code segment timing.

### MOD-8 — stale prose and dead pointers after the move (grep of retired names over SUBJECT, denylist excluded; history records such as lane reports, call graphs, census TSVs, sabotage-anchor TSVs left aside as records)
CONFIRMED. severity: doc. effort: S (one sweep). Sites:
1. src/parse/mod_uprops.c:166-167 "one of the three `PCREC_UCD_NS_*` bits the generated table defines" — the HEADER defines them now (the generated table defines `UCD_GEN_NS_*`), and there are six.
2. tests/registry/pcre2_check.c:3452 "the same independence argument `pcrec_ucd_find`'s own comment makes" — ucd_tables.h's find comment makes no such argument; it lives in mod_uprops.c's THE NAME LOOKUP comment.
3. tests/uprops/run_uprops_tests.sh:353 "THE CASELESS RULE, measured (ucd_tables.c's `pcrec_ucd_find`)" — find only selects the `-i` set; the rule and its measurement are generate.py's CASELESS_AS and mod_uprops.c's lookup comment.
4. src/parse/parse.c:926-927 "module `unicode-props` picks the right span ... (mod_uprops.c's `pcrec_ucd_find`)" — the function is ucd_tables.c's.
5. third_party/ucd-16.0.0/generate.py header "WHAT IT WRITES": `src/parse/ucd_tables.inc` "the general-category interval tables module `unicode-props` consults" — read by ucd_tables.c only, and carries scripts/bc/blk/age too. Its `encode_set` docstring restates the encoding while saying it is "DOCUMENTED IN ucd_tables.c ... and nowhere else".
6. `UCD_GEN_NSETS` is emitted (generate.py:1057) and read by nothing.
7. studies/linktest_probe/pcre2_check_linked.c: the subject edited its comment at :2977 but left the CODE calling the retired `pcrec_uprops_row_count/_row_name/_unicode_version` (:3095-3100) — the probe can no longer link against libpcrec. The wall's retired-name needle `d` covers `pcrec_uprop_(iv|names)` and `PCREC_UPROP_NS_` but not the retired FUNCTIONS `pcrec_uprops_*`, so it does not see this. Either keep the study frozen (revert the comment hunk) or port it.
8. studies/cls_tree_study/README.md:8,67 and CLAUDE.md:10,27 still say the study parses `uprops_tables.inc` (*.md is outside the wall).
9. clsets.py (both copies): the default path runs `build/ucd_dump`, which nothing builds (no Makefile target; absent in the built review tree), so the study's documented invocation fails unless UCD_DUMP is set; `_parse_inc` keeps its name and rebuilds the RETIRED pool layout `(name, ns, off, n, ci_off, ci_n)` from the TSV.
10. docs/design/encoding_data_layout.md:101 (row B1, the data-layout inventory) still names `uprops_tables.inc` read by `mod_uprops.c, mod_ucp.c`; data_plan/CLAUDE.md:9 still lists formats.py as a `uprops_tables.inc` reader (MOD-5).

### MOD-9 — SIBLING OF A FAMILY: the same generator's sibling product `src/core/case_tables.inc` has exactly the two-reader shape this subject retired (C includer emit_subst.c + a Python regex parser), and the wall is a one-table special case, not the general form
CONFIRMED (the second reader); design judgment (the general form). severity: design. effort: general wall M (row table + derived needles), case-map retarget S-M. blast: tests/core/ucd_wall_check.sh, tests/oracle/case_map_check.py, generate.py --list-products.
- Evidence: tests/oracle/case_map_check.py:37 `INC = .../src/core/case_tables.inc` and `parse_inc()` regex-parses `pcrec_case_%s_map[] = {`, `{0x..,0x..}` pairs and `#define PCREC_CASE_*_COUNT/_MAX_GROWTH` — the same pattern clsets.py/uprops_names.py used on uprops_tables.inc before this subject. fold_tables.inc (fold.c, plus its row type `PcrecFoldLink` in internal.h:5363) and utf8_fold_pairs.inc (enc_utf8.c) each have one C includer today; cls_bits.inc (mod_classes.c) too, but its symbols are non-static `const` (extern-visible) and named by cpset.c/registry.c prose.
- Per table or per data source? The owner's words ("the format is only understood to the module which provides an interface") are about a FORMAT, and every generated product has one; the data-plan row scopes the build to uprops only ("Fold tables did not carry over"). My reading: the RULE is per product (each product: one owning module = sole includer, one interface), the WRITER is per data source (generate.py writes four). The wall as built hard-codes one product name, one owner, one 8-symbol list (MOD-3), one allow-list and one plant; a second member would be a copy of the script — the parallel-mechanism shape the house rules warn about.
- General form: a declared first-match row table `product | owning module | interface header`, its product column FROM `generate.py --list-products` (already added by this subject) plus cls_bits.inc's generator; per row the needle is derived from the product's own file-scope identifiers; one scan, one population floor, one planted-include control per row. A product with no row is itself a red (every generated file names its owner).
- Unlocks: (a) case_map_check.py's second reader is caught and retargeted to a dump through emit_subst's (or a case module's) interface; (b) data_plan's B3-shared first client, the fold-pairs table, and any later fold/case compaction become one-module format changes with the wall already standing; (c) one Python dump-reader shape for all Unicode-derived tables.
- Trigger (D77): build the row-table form when a SECOND product changes layout or gains a second reader that is not an accepted oracle — B3-shared's fold-pairs work is the named one. Until then, file a plan row and record in the wall header that it covers one product by design. (Not a build-now ask.)

### MOD-10 — nits: the TSV is a new text format with three hand-written parsers; the build graph still says every object reads the table
CONFIRMED. severity: maintenance (nit). effort: S.
- ucd_dump.c:13-18 defines the TSV (`-` = empty, `lo-hi` hex joined by `,`, `#version`/`#ns` headers); it is parsed separately in tests/uprops/uprops_names.py:145-155 and both clsets.py copies (the ref copy is frozen by design, so two independent parsers plus the frozen one). One small `tests/uprops/ucd_dump.py` reader would give the dump one reader the way the .inc now has one; acceptable as is if the frozen-copy rule forbids it.
- Makefile:233-236 keeps `src/parse/ucd_tables.inc` in GEN_TABLES, a prerequisite of EVERY `$(BUILD_DIR)/obj/%.o`; after the wall only ucd_tables.o reads it. Harmless (over-rebuild; the comment at :189 explains why the blanket exists) but the build graph now contradicts the module boundary; a per-object prerequisite would state it.

## Witness sizes
- Row-order / uniqueness probe: the full dump, 1,384 rows, 881 names, 342 multi-row names (min witness 2 rows, max the whole table); BASE vs SUBJECT dumps compared whole (kit/sets_base.tsv vs kit/sets_subject.tsv).
- Retired-name grep: the whole SUBJECT tree (git grep, denylist excluded), 5 patterns, 52 files hit.
- Sibling scan: 4 sibling generated products, every file-scope symbol, grepped over src/ tests/ tools/ studies/ cli/ lib/ memfn/.
- Compiles used: 0 of 2,000 (the lens is structural; answer identity is other lenses').

## PROBED-AND-HELD
- ucd_tables.h leaks no layout: no offset, blob, count array or encoding type crosses it; the only numbers are PCREC_UCD_NS_* (interface vocabulary), `_Static_assert`ed against the writer's UCD_GEN_NS_* (6/6). No pointer into the blob escapes (all results arena-decoded).
- Exactly one includer of ucd_tables.inc in C (ucd_tables.c); no C file outside the module names any of the 8 private arrays or UCD_GEN_* (git grep over SUBJECT; only the allow-listed generator, wall script, S357x/S-U12 rows).
- pcrec-bench: no .py/.sh/.c/.h/Makefile names uprops_tables / pcrec_uprop_ / pcrec_uprops_ (outside its worktrees).
- Callers no longer re-derive: the two binary searches (mod_code.c code_span_has, mod_named_groups.c ng_in_prop) are deleted in favour of pcrec_ucd_contains; mod_ucp.c and mod_uprops.c call pcrec_ucd_find; the caseless choice is the module's (callers pass a bool, never pick a set).
- Writer order: BASE and SUBJECT dumps are identical row-for-row (1,384 rows, names, masks, both sets) — order and content unchanged; 0 same-name pairs with intersecting masks, so find's "first" is unique today (MOD-2 is about the contract, not an answer).
- uprops_names.py keeps its own NS numbers on purpose (promise side) AND checks them against the dump's #ns lines — legitimate.
- Pre-normalised-name rule: an interface fact, documented in the header; written in mod_uprops.c (producer), generate.py (writer) and uprops_names.py (deliberate independent third) — held as legitimately shared.
- S-U12's comment states the writer's sort; it is a sabotage of the module, allow-listed, and the dependence is what makes the plant silent — legitimate.
- generate.py --list-products removes the repeated product names from run_uprops_tests.sh §7 — held.
CRITIC COMPLETE
