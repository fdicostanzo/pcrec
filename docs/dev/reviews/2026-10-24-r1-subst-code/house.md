# HOUSE lens (house rules: coding.md, style.md, architecture.md declared-table rule)
Subject 1222b31be, read at /home/pcrec/projects/pcrec/worktrees/crit-subst. Static reading plus a few
single-pattern compiler probes. tools/review/out/*.tsv (function_census, clone_candidates) are dated
2026-09-21, commit ed15116d5, and hold zero rows for emit_subst.c / subst_template.c, so they cannot
be cited for the new code; line counts below are mine (span, from the file).

Function population read length-ordered (span lines): st_seq 128, st_escape 97, emit_region_items 68,
cli_subst ~66, emit_subst_slot 46 (almost all emitted text), emit_case_kit 45, st_cond 43,
emit_subst_render_region 41, emit_subst_item 40, emit_subst_items 40, emit_subst_render_head 35,
pcrec_emit_subst 34, pcrec_subst_parse 32, pat_char_utf8 (hunk), support_unit 26, case_state_tables 22.
STOPPED at about 20 lines; everything under that was skimmed in passing, not rubric-scored.

### HOUSE-1  Group-name grammar re-implemented a fifth time (st_name_char / st_in_prop)
- status: CONFIRMED (read both sides)
- severity: maintenance
- effort: S ; blast radius: template names vs pattern names drifting (accepted spellings)
- where: src/parse/subst_template.c:82-110 vs src/parse/mod_named_groups.c:93-127 (ng_in_prop, ng_name_char), pcrec_group_name_scan at :145
- body: mod_named_groups.c:123-131 says "THE NAME GRAMMAR AS ONE FUNCTION ... Two hand copies of one grammar
  is the drift [it] was made a single function to avoid". The subst parser's header (lines 20-27) admits it is a
  private copy that "UNIFIES WITH IT AT MERGE"; pcrec_group_name_scan is already in this tree, so the merge
  is now. st_in_prop is ng_in_prop line for line (minus the ctx_fail on a missing table). Differences are
  only the Ctx plumbing: ng uses isalpha (locale) and pcrec_pat_char, st uses ASCII st_alpha and
  pcrec_utf8_decode. Shared abstraction: Ctx-free `size_t pcrec_name_char_len(const char *s, size_t n, size_t i,
  bool utf, bool first)` (+ `bool pcrec_cp_in_prop(const char *norm, unsigned cp)`), called by ng_name_char
  (utf = encoding wider than a byte) and by st_name_char; replaces 2 call-site bodies. architecture.md "One
  table per slot: no private copy of a declared mechanism".

### HOUSE-2  Output-writing tail of the CLI now copied 3x (two new copies)
- status: CONFIRMED
- severity: maintenance
- effort: S ; blast radius: cli/main.c only
- where: new: cli/main.c cli_subst (~2124-2155) and cli_emit_support (~2181-2186); old: compile_sources (~2000-2045) and main (~2955-2990)
- body: three distinct fragments are each spelled at 3-4 sites. (a) `fputs(c_src, stdout); if (fflush(stdout) != 0 ||
  ferror(stdout)) { cli_err("write error on stdout"); rc = 1; }` : 4 sites (2037, 2147, 2183, 2983). (b) header path
  `malloc(len+3); strcpy; if ".c" suffix swap to ".h" else strcat ".h"`; cli_subst's copy is verbatim main's
  (2955-2963). (c) `write_file(c) || write_file(h)`. Shared abstractions: `static int put_stdout(const char *text)`;
  `static char *header_path(const char *outpath)` (NULL after perror); `static int put_outputs(const char *outpath,
  const char *hpath, const pcrec_output *out)` covering the to_stdout/file split. Replaces the 4+3+3 sites; what
  varies is only whether h_src is present. Also cli_subst at ~66 lines mixes option-refusal, file read, path
  derivation, compile and output (altitude Q1/Q2); the extractions above plus a `subst_refuse_rx_options(st)` leave
  it at one level. Minor: `a[7] == '-'` (line ~1106) tells --subst from --subst-file by character index; compare
  names or keep a flag.

### HOUSE-3  pcrec_prefix_acceptable duplicates the inline prefix check it claims to share
- status: CONFIRMED
- severity: maintenance
- effort: S ; blast radius: prefix diagnostics for rx vs subst
- where: src/core/compile.c:208-221 (new) vs :2539-2543 (compile_driver)
- body: the comment says "a template and a regex share one prefix rule (valid_prefix + the reservation table)"; the
  rule is two helpers called from two places with the two diagnostic strings ("invalid symbol prefix (must be a C
  identifier, <= %d chars)", "invalid symbol prefix: it %s") spelled twice. compile_driver should call
  `pcrec_prefix_acceptable(user_prefix, why, sizeof why)` then `pcrec_ctx_fail(&cx, 0, "%s", why)`; replaces 1 site.
  Without it a new reservation row's message or a new check lands in one place only. Related: ns_subst_families[]
  and the row's `why` string list the same four families twice (compile.c:172-195) and a third time as emit_subst.c
  `support_names[]` + the types block; drift between the three is silent. (Table shape itself is fine: it IS a row
  appended to ns_reserved[], no selector edit.)

### HOUSE-4  The template item walk is spelled twice in the emitter and the COND layout five times
- status: CONFIRMED
- severity: maintenance
- effort: M ; blast radius: emit_subst.c, subst_template.c; sabotage anchors S13xx-S15xx quoting these lines (grep -rl before moving)
- where: emit_subst.c:717-756 (emit_subst_item), :910-977 (emit_region_items); layout at emit_subst.c:772, :954, subst_template.c:389, :582, :438-441
- body: emit_subst_item and emit_region_items switch over the same SubstItemKind and spell the same (pointer,
  length) pair per kind: GROUP0 `s + c[0][0]` / `(size_t)(c[0][1] - c[0][0])`, VAR `ctx->vars[%d].p ? ... :
  rx_subst_empty` / `.len : 0`, SUBJECT `s`/`ctx->len`, BEFORE, AFTER; the first stores `q->p=..; q->len=..; q++`, the
  second hands both to `<p>_put(dst, w, P, L, &st)` (and builds P,L with snprintf into `char b[96], n[96]`). Shared
  abstraction: a row table `span_exprs[kind] = { ptr, len }` (VAR needs a %d, so format strings) read by both emitters;
  the two callers then differ only in the store verb. GROUP/NAME (via _subst_group) and LIT (string literal) stay code.
  Second clone: the COND arm (num==0 shortcut, `slot == -3` MISMATCH test, set/else split) in both; and the offsets
  `set = i+1, unset = set+nset, next = unset+nunset` are recomputed in emit_subst_items, emit_region_items,
  st_pieces (`1 + nset + nunset`), st_span, st_cond. One `static inline size_t subst_cond_end(const SubstItem *it,
  size_t i)` / a `SubstCondSpan {set, unset, next}` accessor in internal.h next to SubstItem removes all five.
  emit_region_items (68 lines) altitude: its length is the inlined clone, not a verdict on the switch; after the table
  it sits near 40 and passes.

### HOUSE-5  Fixed scratch buffers in the emitter (coding.md 2.2) and a closed list now wrong
- status: CONFIRMED (letter of the rule; no truncation reachable)
- severity: maintenance
- effort: S ; blast radius: emit_subst.c:913, subst_template.c:193/410/553
- where: emit_subst.c:913 `char b[96], n[96]`
- body: coding.md 2.2: "a new fixed scratch buffer in either emitter is a finding against you" and the closed list of six
  declarators is the count `tools/review/fragment_census.py` reports. The two buffers hold `ctx->vars[%d]` expressions
  (bounded by int digits, ~75 bytes, so no K38 hit) but should be `pcrec_sb_fragf` or vanish with the HOUSE-4 table
  (emit the format straight into the store). In the parser `char msg[96]` appears three times (st_too_big, st_cond,
  st_seq) as the same snprintf-then-st_fail pair: a `static int st_failf(pcrec_error *, size_t at, const char *fmt, ...)`
  replaces the three and the literal 96.

### HOUSE-6  Arena strndup copied again (fifth private copy)
- status: CONFIRMED
- severity: maintenance
- effort: S
- where: subst_template.c:134 st_strndup; siblings rxt_source.c:394, mod_named_groups.c:84, mod_backrefs.c, mod_recursion.c
- body: coding.md 2.5 names the three `Ctx`-taking arena strndup helpers as the correct shape; this is a 4th/5th, the
  only one with no way to diagnose. A core `pcrec_arena_strndup(Arena *, const char *, size_t)` in arena.c (base tier)
  is the abstraction; the Ctx variants wrap it. Notice-siblings rule (architecture.md) at about three, here past three.

### HOUSE-7  Emitted subst artifacts carry non-ASCII bytes; rx artifacts and the support unit do not
- status: CONFIRMED. Repro: `build/pcrec -p t --features subst-extended --subst '\U$1x${2:-y}' -o - | grep -nP '[^\x00-\x7F]'` -> 3 lines (comments with "§2¶13", "§2¶14", "§4¶8"). Two rx artifacts probed: 0 such bytes. `--emit-support`: 0 (it writes "section 10").
- severity: maintenance
- effort: S ; blast radius: any consumer compiling artifacts with clang -Winvalid-source-encoding, strict -finput-charset, or a Latin-1 tooling chain
- where: emit_subst.c:859-860 (`§2¶13`), :872 (`§2¶14`), :985 (`§4¶8`)
- body: no written rule, but the emitted-text convention in practice (emit_dfa/emit_vm: 400+ non-ASCII bytes in SOURCE comments, 0 in output) is ASCII. The support unit text already writes "section 10". Spell the three as "section 2 para 13" etc. Not an abi event for rx; bumps nothing in rx artifacts (subst artifacts carry their own stamps) but is an emitted-byte change for subst, so make it before the subst abi is pinned.

### HOUSE-8  case_state_tables: an if-chain inside a while condition, magic 9/3, unbounded scan
- status: CONFIRMED (reading); no wrong answer found
- severity: maintenance
- effort: S
- where: emit_subst.c:835-839, :828, :856, :864
- body: case_rules[] IS a declared first-match table, good (architecture.md). But the row-applies test is a 3-clause
  `||` chain inside `while (...)` with no name, and the loop has no bound: it relies on every event having a final CW_ALWAYS
  row ("the last row of each event is unconditional"), so a future event or an edited row runs r past the array. A named
  `static bool case_row_applies(const row *, int ev, int region, int one)` and a `r < n` guard that fails loudly (no silent
  default, architecture.md) fix it. The state count 9 and the base 3 appear as literals in state_tables, emit_case_kit and the
  emitted `[%d][9]`; one `CASE_STATES`/`CASE_CASES` constant. CC_NONE and CC_ITSELF are indistinguishable in the mode
  computation (both -> 0); either drop one enumerator or make the mode column a direct "case source" so the table says what the
  code does. `ecase` (line 833) is computed for END/CHAR events where it is meaningless.

### HOUSE-9  st_seq: stop test duplicated; `$`-form ladder and SubstItem initializers
- status: CONFIRMED (duplication) / altitude judged below
- severity: maintenance
- effort: S-M
- where: subst_template.c:461 and :473 (the stop predicate), 7 positional SubstItem initializers (160, 246, 357, 416, 421, 492, 560, 564, 569)
- body: (1) `stop != ST_TOP && (s[i]=='}' || (stop==ST_SET_TEXT && s[i]==':'))` is written twice, at the loop head and in the
  literal-run scan; if one is edited the run scan and the head disagree and a literal swallows the terminator. A
  `static bool st_at_stop(StStop, char)` replaces both. (2) Nine-field positional compound literals
  `(SubstItem){ KIND, at, len, ref, num, 0, 0, 0, 0 }` at 9 sites; shared `static void st_push(SubstTmpl *, SubstItemKind, size_t off,
  size_t len, int ref, int num)` (only COND sets nset/pset) removes the trailing-zero noise and the chance of a transposed
  ref/num. (3) altitude of st_seq (128 lines) vs the five questions: Q1 fails (literal scan, escape dispatch, nine `$`
  forms, then item construction at one level); Q3 mostly passes: the `$` forms are an ordered recognizer ladder whose arms
  differ in what they consume and in the diagnostic, sharing out-variables (num/name/nlen/var), so a row table would need to
  carry the code (compare coding.md 6, "do not table-drive the rung emitters"). Remedy is extract `st_dollar(ps, depth)`
  (the forms) and `st_run(ps, stop)` (the literal run); NOT a table. st_escape (97) passes Q1-Q4: a flat switch on the escape
  letter with the control letters already a table; it stays long. (4) st_cond encodes the group/name/match distinction as
  `num` = -1 / 0 / k across st_cond's caller (lines 514, 532) and the nested ternary at 421-423; a named `enum` or the
  item kind passed in replaces the sentinel.

### HOUSE-10  emit_subst_info builds the whole support unit to read its hash
- status: CONFIRMED (reading)
- severity: size (compile time only) / maintenance
- effort: S
- where: emit_subst.c:1145 `if (unit) free(support_unit(&id));`
- body: the full text (two StrBufs, the case tables, FNV over ~20 KB) is built and discarded to obtain `id`; pcrec_emit_support
  then rebuilds it. Split `support_unit_text(StrBuf *)` / `support_unit_id()` or have support_unit return the id via a cheap
  helper; also reads as a side-effecting call used as a value getter. Tiny cost, but the pattern (build, free, ignore) is what the
  reader of emit_subst_info sees first.

### HOUSE-11  Smaller, grouped (each S, none changes an answer)
- emit_subst.c:780 `pcrec_sb_printf(c, "        {\n")` with no arguments next to the identical puts at :776: use pcrec_sb_puts; the two arms of the num==0 split share the open/close lines.
- emit_subst_render_head (35) if/else repeats two of five declaration lines under `region`; a shared declaration with a `[[maybe_unused]]` form or an `(void)` list (as emit_region already does) would drop the branch. The `(map && (map->run ? map->nrun : map->nslot) < N)` expression is spelled in the types block (check) and in the render head; one emitted macro/inline in the types block names it.
- emit_subst.c:526-527 and 520-524: `#define PCREC_SUBST_H <abi>` and the `#define %s %s_v%d` name macros are hand-written defines. coding.md 2.6 forbids hand-written `#define %s_...` VALUE stamps; these are not `<UPPER>_<NAME>` stamps so they are outside the helper's shape, noted only because 2.6's list of exceptions does not name them.
- definitions.c: pcrec_def_text_hex and pcrec_def_text_unicode are now byte-identical one-liners over pcrec_esc_digits_value (and _octal differs only in base); one `def_text_digits(operand, len, base, cx)` would carry all three. Also the long \cX comment now sits above pcrec_esc_ctrl_value (its subject) and pcrec_def_text_cx gets a one-line header; fine, but the bare \x / \o comment block above the new helper at :306-311 now documents a function that follows it, not the helper placed there. 
- cli/main.c read_whole_file: a third whole-file reader (beside ks_measures.c:685 and rxt_source.c:1019); the CLI one is the only grow-as-you-read loop. Not an extraction candidate on its own (three different error contracts) but note the family.

## PROBED-AND-HELD
- Allocation discipline (coding 1.1/1.2): subst path uses an `Arena`/`StrBuf` with no `.cx`, so OOM aborts. Documented as an explicit exception at subst_template.c:54-58 and internal.h pcrec_subst_compile ("only caller is the CLI until [IFACE-PUSH]"); declared in internal.h not lib/pcrec.h so not public. Held; the trigger should be written on the IFACE-PUSH row.
- pcrec_options memcmp in cli_subst: pcrec_default_options memsets first (compile.c:62), so padding is deterministic. cli_emit_support's CliState compare is memcpy'd from a zeroed st. Held (2 sites).
- pat_char_utf8 (lower_enc.c): switch over PcrecUtf8Status has no default (coding 1.3), messages and order (lead, truncated, overlong, surrogate, too-big) preserved; decoder returns the same first failure. Held.
- pcrec_esc_digits_value refactor of three def_text_* functions: behaviour-equal (the old early `> 0xFF` return vs new saturate then caller range check). Held on reading.
- limits.def rows (PCREC_MAX_TEMPLATE_GROUP/NESTING): proper rows with measurement text; `96`, `9`, `4096`, `64`, `256`(emitted) are scratch/emitted constants, not rows (coding 1.8). `256` RX_SUBST_BATCH_PAIRS is overridable in emitted text. Held.
- case_rules[] and ns_reserved[]/ns_subst_block: declared first-match tables, row added without selector edit (architecture.md). Held apart from HOUSE-8.
- Emitted comment safety: template text goes through pcrec_emit_comment_bytes (emit_comment_safe_byte); prefix/name via c-string-literal escaper. Held.
- Function-local `static const` tables (ctl[], maps[], min_of) are const, not mutable state (coding 1.5). Held.
- emitted run-validation duplicated between pcrec_subst_check and `<p>_subst_slot`: deliberate per-call re-assert (§4¶10, hand-filled ctx), not a house violation. Held.

## NOT COVERED
- tools/review censuses not regenerated for this tree (would write into out/ in the repo); no clone numbers cited.
- Emitted-C quality / answers (other lenses). The 0xE0/0xF0 decoder at emit_subst.c:441 (`rx_subst_utf8_char_` in the support unit) vs emit_iter.c's emitted decoder (not read) may be a runtime-side duplicate; unchecked.
- Whether abi bump / identity re-pin was owed for the emit_dfa.c exports (no rx byte moved per the diff: three new functions only).
- tests/mech sabotage-anchor impact of the proposed moves (HOUSE-4, 8, 9) not enumerated; grep -rl before any move (coding 3.5).

## DONE
