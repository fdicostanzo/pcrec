# src/parse — PCRE pattern parser

Base-tier PCRE parser (literals, `.`, classes, quantifiers, alternation, anchors, groups, metachar escapes) producing the AST, plus the construct registry and the module producers (`mod_*.c`) it reaches through four doorways, plus the `.rxt` source-file readers. Anything outside the base tier is routed through registry rows that yield a precise "requires module 'X'" diagnostic instead of a miscompile. Also hosts the knowledge-module rows (`ks_*.c`).

## Standing rules

Maintenance: update this file when files are added/removed or their roles change.

Registry (registry.c, D24) and doorways:
- Non-base syntax is described ONCE, as a row in registry.c, and reached through exactly four doorways (after `\`, after `(?`, after `(*`, after `[` in a class). Adding a construct = adding a row, never editing parse.c. A construct with two homes will drift (`\v` once decoded as VT because two tables disagreed).
- parse.c is the base grammar AND NOTHING ELSE (SR-2); it stops gaining CONSTRUCTS (not correctness fixes: FIX-1's `case '{'` / two-phase `try_quant` overflow rule were base-tier syntax bugs). A new construct needs a registry row.
- Add a row in registry.c and nowhere else. `syntax` must be a pattern that really reaches that doorway: tests/registry/ uses it as the probe, so a new row covers itself.
- `RS_MODULE` with no handler is a complete outcome (named, cleanly rejected, queryable), not a stub.
- `RS_BASE` rows in `RK_ESC` are a narrow named exception (7 rows: `\a \e \f \n \r \t` and bare `\x`, `ESC_BASE_D`) existing only to give `RegRow.definitions` (D85) a home; never consulted by live dispatch (`esc_char_value` still decodes them). Do not add an eighth base-tier construct casually (read definitions_table.md's architectural note). Braced `\x{...}` stays out (unicode-props' unbuilt form; no new doorway).
- Two "requires module" diagnostics deliberately stay in parse.c, no doorway: `\x{...}` and the possessive `+` suffix (a doorway would cost the base tier a lookup). `\b` in a class is the row's BASE class port (ExtPort.base; gate never touches it).
- `(?:` is base grammar, answered before the registry; its row exists only so the table is complete for the dump.
- Registry: tail selection and engines column: moved verbatim to NOTES.md, section "Registry: tail selection and engines column".
- An inline option setting is a RUN, not a byte (Q2): the `(?` doorway reads the whole run; grammar is measured (`(?aP)` ok, `(?aPP)` err 111, misplaced hyphen err 194, PCRE2 stops at first error). Module names in diagnostics are pinned by hand in tests/reject/, not verified by libpcre2.
- `RF_CLASS_DELIM` carries a construct's own recognition rule (opens only when its matching `X]` appears later); all THREE class-bracket rows carry it. `RF_CLASS_NAMED` is meaningful only ON an `RF_CLASS_DELIM` row (registry_check.c requires the pairing). `open_msg` is the one POSITION-varying field. `<`/`>` POSIX names are whole-class-only (`pcrec_registry_posix_whole_class_only()`, `at_content_start`; `check_posix_positions`).
- `RF_CLASS_INVALID` stays (permanent class-position invalidity); port data guarded by `check_class_ports` (populations pinned, values oracle-tied); set bitmaps are GENERATED from libpcre2 censuses (PC-4 re-measures), never hand-typed.
- A verb NAME goes in the VerbName tables (mod_verbs.c), not a RegRow (Q1/D25). Its form bits (VF_BARE/ARG/EMPTYARG/EQNUM/GROUPARG/ATSTART) are MEASUREMENTS: add the name, run `bash tests/registry/run_registry_tests.sh`, let libpcre2 tell you the bits; never reason from the docs. Table chosen by CASE of first name byte only; terminator set is per-name.
- `(?` doorway cannot decline (catch-all is REJECTED); `pcrec_ext_class_bracket` can (DECLINE, cursor unchanged). Do NOT give them one contract. Non-matching `(?X` bytes get PCRE2's wording with no module (the run/byte is the construct).
- RF_INDEX rows never dispatch by name/byte-only identity: in `pcrec_registry_arbitrate` the RF_INDEX skip goes BEFORE the `REG_SEL_ANY` case (load-bearing). Byte-keyed index rows record the true selector byte, never `REG_SEL_ANY`; `check_index_rows` (registry_check.c) asserts against the engine's own dispatch.
- Port chosen by construct FAMILY where families differ (`GROUP_RC`/`GROUP_RC_T` macros); a row differing in a macro-fixed field is written LONGHAND. `(?0` is a prefix of two targets: every numeric recursion port re-reads the WHOLE digit run from the selector byte (`(?01)` is group 1, not the root).

Doorway seam (ext.c):
- Doorways RETURN a tagged `ExtResult` (EXT_NOT_MINE / EXT_REFUSAL formatted at claim time); `pcrec_ext_finish` is the one epilogue; call sites in parse.c end in internal-error walls for unhandled outcomes. Every doorway takes an `ExtWant` level; `pcrec_ext_gate` demotes RESULT to VERDICT when the row's module is off (consults enabled.c AFTER row choice); `answered_at` records the post-gate level; the CURSOR RULE (cx->pos moves only under WANT_RESULT; the CALLER moves the cursor, never the doorway) is measured through `--probe-ask` (check06).
- `group_answer`: a general `want == WANT_RESULT && aport.kind == PORT_FN` producer-invocation path (passes the position after `sel`+`tail`; the option-run branch passes the SELECTOR byte). Every new `(?` producer not shaped like an option run uses it; no second special-cased block.
- UNBUILT epilogue: a gate-open construct with no producer refuses by the CONSTRUCT's name (not "requires module"), read off ONE source (post-gate WANT_RESULT reached = "gate open, port missing"); sits AFTER the `ROADMAP_NEVER` case. `PCREC_UNBUILT_MARKER` (internal.h) is the one shared wording. The `built` column (`pcrec_construct_built_status`, syntax_dump.c, D65) is DERIVED live, never hand-set, and must not text-match.
- `pcrec_ext_verb` lives in mod_verbs.c as a direct call (not a port); ext.c still owns `DECLINE` (class-bracket only); `REFUSE`/`BAD_ROW` macros are shared via internal.h.
- Keep lexer extent scans (scans.c) out of module TUs; scans.c must NEVER link the enabled-set symbols (`nm` is the oracle, check01).

Parser structure (PARSE-1):
- The group case is three functions: `p_group` owns entry/exit bookkeeping (`cx->depth`), `p_group_body` owns everything between `(` and `)` and neither end. Keep it so a `return` in the body stays balanced. `pcrec_ctx_fail`'s longjmp bypassing the exit is structural: `src/core/compile.c` holds the ONLY `setjmp`.
- `p_alt_info` fills `AltInfo {nbr, last_bar}` (count computed by the loop that drives the parse; `Ast` has no position field, so modules needing an offset need it reported). Never re-derive branch counts by scanning text.
- Modifier state lives in `cx->mods` (ModState), seeded once from options in compile.c; saved/restored around every BODY-CARRYING group; a bare option run escapes its paren's restore (measured leak rule). The restore belongs at the group boundary in the base grammar, not in a module.
- A parsed concatenation holds no empty that carries nothing (no `reg` stamp): `p_cat` drops it after `p_rep`'s quantifier check ([FLAG-SPELL]), so `(?i)abc` and `(?i:abc)` build one tree. Readers may rely on it (ctxnode.c's CAT arm does); the anchor seal (`pcrec_wrap_bare_anchor`) and lower_enc's seal build CAT-with-empty outside `p_cat` and keep it.
- Nested bodies use `pcrec_parse_body` (stops AT its terminator; the CALLER consumes its own `)` and raises its own unterminated diagnostic with `PCREC_MISSING_CLOSE_PAREN_MSG`). Do not use `pcrec_parse_info` for a nested body.
- Parser structure details (PARSE-1): moved verbatim to NOTES.md, section "Parser structure details (PARSE-1)".
- Module-specific invariants and .rxt readers, composer, definitions: moved verbatim to NOTES.md, section "Module-specific invariants and .rxt readers, composer, definitions".

## Files

- scans.c — always-live extent scans (K4 three-rule delimiter-pair scan, `pcrec_ext_class_pair_opens`, verb-name extent); pure over (pat, patlen); never links enabled-set symbols
- enabled.c — the enabled feature set (`--features`, `std1` named set, `pcrec_default_features`, `pcrec_enabled_set_label/_modules`)
- parse.c — base grammar, AST, case fold T2 (`fold_rows`), `\Q\E` lexing, bare-anchor helpers, `pcrec_ast_pin`, `pcrec_parse_body`, `pcrec_parse_mods_init`
- parse_mods.h — ModState/ParseMods definition; included by nothing outside this directory
- registry.c — construct registry (D24/SR-1): all non-base rows, `bare_rows[]`, index rows, arbitration, `pcrec_registry_verb_name_row`
- ext.c — three of the four doorways (`pcrec_ext_escape`, `pcrec_ext_group`, `pcrec_ext_class_bracket`), `pcrec_ext_gate`, `pcrec_ext_finish`
- ctxnode.c — lookaround to context-node lowering table (`ctx-node` row, `-fno-ctx-node`/`PCREC_NO_CTX_NODE`; `pcrec_look_rows`)
- definitions.c — `RegRow.definitions` evaluator/resolver/tag-namer/core-set predicates (D85)
- mod_verbs.c — `(*` doorway (`pcrec_ext_verb`), VerbName tables; resolves a name to its own row
- mod_classes.c — module `classes`: POSIX port, includes generated cls_bits.inc
- cls_bits.inc — GENERATED positive byte-set tables (do not edit)
- mod_modifiers.c — module `modifiers`: option-run grammar and semantic port (`pcrec_modport_optrun`)
- mod_uprops.c — module `unicode-props` scanner + producer; uprops_tables.inc GENERATED from third_party/ucd-16.0.0
- uprops_tables.inc — GENERATED category/script tables (do not edit)
- mod_ucp.c — module `ucp`: `(*UTF)`/`(*UCP)`, option run, UCP sets
- mod_named_groups.c — module `named-groups` declaring port
- mod_assertions.c — module `assertions` (`\A \Z \z \b \B \G \K`)
- mod_lookaround.c — module `lookaround` (one port, width rule, `\K` check)
- mod_atomic_groups.c — module `atomic-groups`, `pcrec_atomic_suffix_row`
- mod_vars.c — module `vars` (`${name}`)
- mod_backrefs.c — module `backrefs`, `pcrec_bref_resolve`
- mod_recursion.c — module `recursion` (calls, DEFINE)
- rxt_schema.def / rxt_schema.c — `.rxt` format schema as data and its reader (one exhaustive switch over the constraint kinds)
- rxt_source.c — `.rxt` head parser, `--list-source`, resolution (`pcrec_rxt_source_resolve`), `lib` closure
- rxt_find.c — analysis-bundle resolution chain ([FINDINGS] B2)
- ks_analysis.c / ks_lib.c — knowledge-module kind rows for analysis and `lib` ([KNOW-SRC])
- rxt_compose.c — the composer binding `.rxt` definitions into the target tree (W1.3)

## Pointers

APPROACH.md; docs/design/{lookaround_design,assertions_design,atomic_groups_design,backrefs_design,subroutines_design,ucp_design,utf_valid_design,variables_common,variables_pattern,definitions_table,registry_built_status_memo,design_notes_mod06}.md; docs/design/dd13_format/{format_design,w1_impl}.md; docs/design/findings/design.md; docs/design/measure_sets.md; docs/spec/{registry,rxt_format,table_contract,vars,findings,match_api,limits}.md; docs/dev/decisions.md (D20, D24-D33, D37, D62, D65, D67, D71, D85, D87, D89, D100, D130, D133); tests/registry/CLAUDE.md, tests/rxtsource/CLAUDE.md, tests/parse/CLAUDE.md; memfn/CLAUDE.md.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__parse.md

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
