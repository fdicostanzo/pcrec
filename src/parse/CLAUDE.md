# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **scans.c** — the ALWAYS-LIVE extent scans (design §12; MOD-0.1 slice 9):
  the K4 three-rule delimiter-pair scan (with `pcrec_ext_class_pair_opens`,
  its predicate form) and the verb-name extent. Pure over (pat, patlen);
  named per spec check01's discovery convention (`*_extent_scan`); this TU
  must NEVER link the enabled-set symbols — `nm` is the oracle (check01),
  and the isolation is the mechanical form of "what a construct IS cannot
  depend on what is switched on"
- **enabled.c** — the enabled feature set (MOD-0.1 slice 9): one home,
  process-wide, written once by the CLI's `--features` (module names from
  the registry, or all/none; unknown names refused by name) before any
  compile; `pcrec_feature_enabled` is the gate's membership question.
  Deliberately NOT a pcrec_options field (D20). Since MOD-0.3c enabling a
  module with producers CHANGES VERDICTS — that is the point of a gate —
  and check07's transition rule owns the shape of that change (an eligible
  row must flip to a refusal naming its own module, nothing else may move).
  **[STD1] phase A (D37, 2026-08-13) adds frozen named sets on top, WITHOUT
  touching the mask machinery above.** `g_named_sets` holds one entry today
  — `std1` = {classes, modifiers}, FROZEN forever once shipped, expanded
  through the same `find_module_bits` registry lookup an explicit list
  already used (factored out so there is exactly one name->bits lookup).
  `PCREC_DEFAULT_FEATURES` is D37's bare-default MAPPING POINT — the one
  place "no --features flag" resolves to a named vocabulary value; it stays
  `"none"` through phase A on purpose (see its own comment before touching
  it — the flip to `"std1"` is a deliberately separate later commit that
  travels with the full suite re-baseline). Two new readers,
  `pcrec_enabled_set_label`/`pcrec_enabled_set_modules`, expose WHICH name
  resolved the current set and its rendered (mask-derived, so it cannot
  drift) module list — static, fixed-size buffers filled once by `install()`
  at spec-parse time, matching the file's existing write-once/read-many
  contract; src/gen's artifact stamping is their only consumer today
- **parse.c** — **[M4.5b]: the capturing-`(` hook now also builds the AST's
  capture node.** `p_group_body`'s existing hook is the one place that knows
  "is this `(` a capturing group", so `Ctx.ncap++`, the group NUMBER and the
  `A_CAP` wrapper all live there together; the number is taken BEFORE the body
  parse for the same reason the increment is, since PCRE2 assigns numbers by
  opening-paren order and an inner group must not steal an outer one's.
  `Ctx.want_caps` is the ONLY gate — with it false the tree produced is
  byte-identical to D31's, which is what makes engine_m4.md §5.4's gate
  structural rather than audited. The wrapper PROPAGATES `not_repeatable`
  rather than defaulting it: leaving it at the arena's zero would make
  `((?i))*` legal with captures on and error 109 with `--no-captures`, a
  divergence between the two modes, and whether pcrec should reject that
  spelling at all is a separate pre-existing question this node must not
  silently answer. The capture wrap goes OUTSIDE the bare-anchor `A_CAT` wrap,
  so `(^)`'s group spans the whole (empty) match rather than only the anchor.
  Otherwise: see also **PARSE-1 (2026-08-11)** below, which changed the
  group case's SHAPE without adding a construct — the base grammar AND NOTHING
  ELSE (SR-2): literals, `.`,
  classes, quantifiers, `|`, `(...)`, `(?:...)`, `^`, `$`, the plain character
  escapes. Produces the AST. Meant to stop growing: a new construct needs a
  registry row, not an edit here. "Stops growing" means stops gaining
  CONSTRUCTS — it does not freeze the base grammar's own correctness. FIX-1
  (2026-08-10) added a `case '{'` to `p_atom` and a two-phase overflow rule to
  `try_quant` for K5/K6, both of which are the base tier being wrong about
  syntax it already owned, with no registry row involved
- **registry.c** — the syntax construct registry (D24/SR-1): every non-base
  construct as one `static const` row, plus the lookup. Since Q1 (D25) it also
  holds the `(*` doorway's two verb-NAME tables — 31 upper + 19 lower, chosen by
  the CASE of the first name byte exactly as libpcre2 chooses between its own
  two. Every bit of those tables is measured against libpcre2 and re-measured on
  every run by tests/registry/pcre2_check.c.

  **[M6.6.2 wave F] IT ALSO HOLDS THE FIRST ROWS THAT NEVER DISPATCH.** The
  twelve `(*` alpha lookaround spellings (`VERB_LA`) carry `RF_INDEX`: they
  are real, distinct PCRE2 spellings the compliance index owes a line for,
  and none of them is selected by a byte, because the `(*` doorway decides by
  NAME. `pcrec_registry_arbitrate` skips them in ONE line — placed BEFORE the
  `REG_SEL_ANY` arm, which is load-bearing: that arm assigns the kind's
  catch-all unconditionally, so a skip placed after it would let the last
  alpha row steal the `(*` doorway and make every verb in the tree answer
  "requires module 'lookaround'". `pcrec_registry_verb_name_row` (also here,
  beside the rows, because it reads `tail` AS A NAME) is what mod_verbs.c
  resolves a scanned name through. D71 item 3; `check_index_rows` in
  tests/registry/registry_check.c asserts both halves against the ENGINE's
  own dispatch rather than by re-reading the flag.
- **ext.c** — three of the four doorways (SR-2) now: `pcrec_ext_escape`,
  `pcrec_ext_group`, `pcrec_ext_class_bracket` (`pcrec_ext_verb` moved to
  mod_verbs.c at MOD-0.4 — see its own entry below; declared in internal.h
  and called from parse.c exactly as before, so this remains "the edge that
  makes the registry the ONLY home rather than a sixth copy" for all four).
  parse.c calls these once its own switch has declined. Since MOD-0.1's
  returned-claims epilogue (D33 §5) a doorway RETURNS its terminal answer as
  a tagged `ExtResult` (EXT_NOT_MINE, or EXT_REFUSAL carrying the diagnostic
  formatted at claim time), and `pcrec_ext_finish` — the one epilogue —
  renders refusals; call sites in parse.c end in internal-error walls for
  outcomes they do not handle, which is what closed K11 (the noreturn-era
  UB) and the PARSE-1 fallthrough discard. SR-6's module handlers become
  their callees, extending ExtWhat with probes that are false the day
  before (D33 §9.3). Since MOD-0.1's slice 8 every doorway takes an
  `ExtWant` ask level (§18.2's three-level contract, no `may` axis — see
  internal.h): parse.c's six call sites ask WANT_RESULT, `pcrec_ext_gate`
  demotes RESULT→VERDICT while a row's module is not enabled (a real
  per-row membership test since slice 9, consulting enabled.c AFTER row
  choice; floors at VERDICT), the result's `answered_at` records the
  post-gate level ("gate open, port missing" vs "gate closed"), and the
  CURSOR RULE — cx->pos moves only under WANT_RESULT — is measured
  externally through `--probe-ask` (check06's channel) rather than
  asserted. Slice 9 moved the extent scans out to scans.c; ext.c keeps the
  seam: row choice, the gate, the terminal answer. Since MOD-0.2 the escape
  and group doorways call `pcrec_registry_arbitrate` directly and render
  its ambiguity defect (two answering rows at the winning rank) as an
  internal error — unreachable on the correct table, validated live by an
  equal-rank sabotage. **MOD-0.4** promoted `pcrec_ext_gate` from `static`
  (was `ext_gate`) and the `REFUSE`/`BAD_ROW` refusal-epilogue macros out to
  internal.h — mod_verbs.c needs both and gets one shared definition of
  each rather than a second copy; `pcrec_ext_gate` is still DEFINED here,
  `DECLINE` stays file-local (only the class-bracket doorway produces it).
  **[M6.3] `group_answer` gains the GENERAL producer-invocation path**: a
  second, unconditional `if (want == WANT_RESULT && r->aport.kind ==
  PORT_FN) return r->aport.fn(...)` sits below the option-run family's own
  special-cased block, for every RD_MODULE row whose port is not shaped
  like an option run — module `named-groups` is its first (and, until the
  next such module lands, only) caller. Its `from` convention DIFFERS from
  the option-run branch's on purpose: this one passes the position right
  after the row's own full selector prefix (`sel` plus `tail`, since a
  tailed row's construct-specific text starts past its tail), while the
  option-run branch passes the SELECTOR byte itself (the run includes it)
  — the two shapes disagree about where their own text begins, which is
  why they are dispatched by different tests (`r->recognise`'s pointer
  identity vs. this branch's `aport.kind`) rather than merged into one.
  **[M6.2 wave A] the ENABLED-BUT-UNBUILT epilogue (`UNBUILT`)**: a module
  that lands its constructs across several waves — `assertions` is the
  first — has an interval where its gate is OPEN and a given construct
  still has no producer, and "requires module 'X'" is then a lie of the
  most annoying kind, since it asks the user to do what they have already
  done. The refusal names the CONSTRUCT instead, on `--encoding=utf8`'s
  PRINCIPLE (a name pcrec knows but cannot compile is refused by its own
  name, never as unknown) though not its mechanism — that gate is one
  whole-pattern decision against a one-row table, this one is per-construct
  at the registry dispatch, because a half-landed module has some
  constructs built and others not WITHIN ONE PATTERN (R30 C7). The
  condition is read off ONE source and deliberately not off a second
  `built` column: reaching the epilogue at post-gate `WANT_RESULT` means
  the gate was open and the port block declined, which is exactly D33's
  "gate open, port missing" that `ExtResult.answered_at` has reported to
  `--probe-ask` since MOD-0.1 slice 9. It sits AFTER the `ROADMAP_NEVER`
  arm in the group doorway, because "no module will ever implement this"
  and "this module has not implemented it yet" are different facts and the
  permanent one wins. Pinned in tests/reject/'s `== assertions ==` section
  with the gate-closed rows adjacent; sabotage S70.

  **[D65] (2026-08-21) a `built` column DOES exist now** — `pcrec
  --list-syntax`'s new column, `pcrec_construct_built_status`
  (syntax_dump.c) — and it is NOT the second declared column the paragraph
  above warns against: it is DERIVED, live, per row, by driving the gate
  and reading `ExtResult.answered_at` exactly as this file's own comment
  already describes ("gate open, port missing"), never a hand-set field
  that could drift from the ports. `PCREC_UNBUILT_MARKER` (internal.h) is
  the one shared string both this macro's format and the `\p`/`\P`-adjacent
  in-class splice use, so the two ext.c refusal SITES stay one wording —
  but the classifier itself does NOT match that text (a text-match first
  draft was WRONG on three real rows: module `verbs` and module
  `unicode-props` both refuse with the CLOSED-gate wording even at a
  forced-open gate, since neither routes through this epilogue at all —
  see docs/design/registry_built_status_memo.md's implementation record
  and tests/registry/CLAUDE.md item 10 for the measurement).
- **mod_verbs.c** — the `(*` doorway. **[M6.6.2 wave F] IT IS NO LONGER
  PURE MIGRATION: it PRODUCES, and not for its own module.** The doorway now
  resolves a scanned NAME to that name's own registry row when it has one
  (`pcrec_registry_verb_name_row`, registry.c) and keeps its own row when it
  does not — which is every verb except the twelve alpha lookaround
  spellings. From that point on nothing in the function is
  lookaround-specific: `r` is "the row this name answers for", and the gate,
  the port call and both terminal refusals all read it, so the SECOND module
  to give a verb name a row of its own needs no edit here. This closes the
  defect design §8.2 measured at P3 — all twelve alpha spellings answered
  *"requires module 'verbs'"*, the wrong module, because ONE catch-all row
  answered for every name in both tables.

  **THE ROW LOOKUP SITS AFTER THE FORM AND POSITION CHECKS, DELIBERATELY**
  (R33 C2-6). `(*pla)` is a real name in a form PCRE2 does not accept, and a
  form mismatch is decided BEFORE module attribution in PCRE2 as in pcrec, so
  its "(*alpha_assertion) not recognized" survives this wave.

  **WHAT THE ORDERING PROTECTS IS THE ANSWER LEVEL, NOT THE MESSAGE**, and a
  CONTROL BUILD refuted the first version of this paragraph, which claimed
  the reject table's `(*pla)` row would go red if the lookup moved. It does
  not: the form refusal's text comes from the VerbName TABLE's `unknown_msg`,
  not from the elected row, so it is byte-identical on either side of the
  form check and a message-only pin cannot see the difference. What DOES move
  is `answered_at` — `--features lookaround --probe-ask result -- '(*pla)'`
  reads `verdict` on the shipped compiler and `result` on the control, which
  is D33's "the gate was OPEN and the port had nothing to say" signal. The
  control therefore has a FORM ERROR reporting itself as an answer given with
  module `lookaround`'s gate open: this wave's own misattribution one level
  down. `tests/cli/`'s case10 pins all four cells (both gate states x
  `(*pla)` and `(*pla:a)`), since `--probe-ask` is the channel that can see
  it and the reject table is not.

  The doorway also GATES TWICE now — once on its own row for every refusal
  decided before the name is known, and again on the name's row, recomputed
  from the ORIGINAL ask rather than the demoted one.

  Historically (MOD-0.4), the MIGRATION TEST: moves
  `pcrec_ext_verb` here from ext.c WITH the `(*` doorway's two VerbName
  tables and their four accessors (was registry.c) and their whole
  measured-grammar comments (the probes-and-code-together rule
  mod_modifiers.c's entry below states). PURE MIGRATION — no verb produces
  yet, the doorway-3 wall stays, gate ON/OFF stay byte-identical to the
  pre-move build (verified: 602 differential comparisons across every verb
  name × applicable form, unknown names, the 128/129-byte length boundary,
  the `LIMIT_*` accumulator boundary, empty-name shapes, at-start
  placement, both gate states — zero diffs). WIRING: a direct call, not a
  port — `pcrec_ext_verb` keeps its exact signature and parse.c's call
  site is unchanged, unlike mod_modifiers.c's `(?` doorway, which
  dispatches across a FAMILY of GROUP_OPT rows via a row's `recognise`
  field. Doorway 3 has exactly ONE RegRow (`verb_rows[0]`, still in
  registry.c) dispatching by NAME through the tables in this file, not by
  row, so there is no row family for a recognise pointer to mark; building
  one would wire a producer nothing exercises yet (internal.h §14.3's
  NULL-port discipline) and would invent the synthetic-buffer UB class
  mod_modifiers.c's `recognise` field exists to sidestep, a risk that does
  not arise here since verb dispatch reads scanned NAME TEXT
  (`pcrec_verb_name_extent_scan`, scans.c — stays there, unmoved: pure over
  (pat, patlen), needed regardless of gate state, and scans.c's
  never-links-the-enabled-set contract is exactly why lexer machinery does
  not belong in a module TU even when it has one caller). See the file's
  own header for the full mapping of the milestone's four measured facts
  (the returned-claims epilogue, the VF_* form computation, VF_ATSTART's
  `at == 0`, and the `star = at + 1` blame offset) to where each still
  lives
- **mod_classes.c** — module `classes` (MOD-0.3c), the first module with
  real PRODUCERS: includes the GENERATED cls_bits.inc (20 positive byte-set
  tables from libpcre2 censuses — regenerate with probe_cls_bits --emit,
  never hand-edit; the complement law makes negation table-free) and
  provides `pcrec_clsport_posix`, the `:` row's PORT_FN (one row, fourteen
  names, both polarities — a NAME is not a fixed set per row). Production
  wiring: the escape doorway answers a post-gate WANT_RESULT from the
  position's SET port (EXT_NODE at atom, EXT_MEMBERS in class, both built
  by parse.c's `pcrec_ast_class_from_bits`, the ONE constructor that owns
  fold-before-negate); parse.c's call sites consume — esc_atom splices
  EXT_NODE, p_class ORs EXT_MEMBERS and advances to res.end (the caller
  moves the cursor, never the doorway — check06's rule). The endpoint rule
  gained its produced twin: a SET at a range endpoint is err-150's analogue
  in BOTH gate states (step 4 now keys on any surviving claim), and
  `[[:alpha:]]-z`-shaped low-side dashes refuse after production exactly as
  they do after a certified refusal
- **mod_modifiers.c** — module `modifiers` (MOD-0.5), slice 1 (MOD-0.5b) so
  far: the `(?` doorway's OPTION RUN, moved out of registry.c WITH its whole
  measured grammar comment (the probes-and-code-together rule — see the
  file's own header, and R8/C2-9's drifted `LIMIT_*` rule as the
  counter-example it cites). `pcrec_registry_option_run_ok` is the grammar;
  `pcrec_registry_option_run_recognise` is what the twelve GROUP_OPT rows now
  carry in their `recognise` field instead of the retired `RF_OPTION_RUN`
  flag, and it is a MARKER rather than the check itself — always answering
  true, same as the tail-less default — because the real check needs the
  selector byte the standard recogniser `at` sits one position past, and
  reconstructing that from `at` would read out of bounds against
  registry_check.c's synthetic arbitration-sweep buffers. ext.c still runs
  the real check, gated on the pointer's identity rather than the flag.
  **MOD-0.5c added the SEMANTIC port** `pcrec_modport_optrun` — the twelve
  rows' atom-port FN, the shared handler for BOTH spellings (`(?run)` and
  `(?run:body)`, diverging only at the terminator inside the port): walks
  the validated run building set/unset masks (unset wins, measured), applies
  them to `cx->mods` for a bare run (whose caller splice deliberately
  escapes the group save/restore — the measured leak-to-enclosing-`)` rule),
  or does save/apply/`pcrec_parse_body`/restore for `:`; per-letter refusals; `m` is **REAL since [M6.2] wave C** — it sets the scoped
  multiline state, and `p_atom`'s `^`/`$` rows resolve that state onto the
  node at the assertion itself (D62, `Ast.u.anch.multiline`), which is what makes
  `(?m:...)` and `(?m)...(?-m)` right by construction rather than by a
  downstream pass re-deriving scope. Its wave-A pair of refusals (module-off,
  and enabled-but-unbuilt) retired with the letter, along with their two
  `tests/reject` pins; what remains is the module-OFF refusal by the letter's
  own name, which still needs its own copy of ext.c's rule because a letter's
  refusal is produced HERE, per letter, and a letter's module is not the
  dispatching row's. `-m` needs no gate at all — it asks for the semantics
  pcrec's anchors have with no module. Since [M6.3], `J` -> K14's
  permanent ROADMAP_NEVER wording rather than a module name — it used to
  say "requires module 'named-groups'", true only while that module did
  not exist; named-groups shipped WITHOUT (?J)/DUPNAMES (a ruled scope
  exclusion, docs/dev/plan.md's [M6.3] row), so the old wording would have
  turned into a live lie the moment the module landed, and this letter's
  refusal is unconditional regardless of whether named-groups is enabled
  (see mod_named_groups.c's own duplicate-name check, which never
  consults this letter); recognised-malformed runs diagnosed here (the
  err-194/114 shapes).
  **A BARE RUN'S NODE IS MARKED `not_repeatable` since R20/SPEC-1**, a tier-1
  MISCOMPILE the D27 blinded writer found: the bare run produces `A_EMPTY`,
  `A_EMPTY` is ORDINARILY quantifiable (`()*` and `(a|)*` both compile in
  libpcre2), so `a(?i)*` compiled and its matcher matched a/aa/aaa where
  libpcre2 gives err 109. pcrec's own registry had been right all along —
  these rows' `quantifiable` column reads `form` — so nothing was missing:
  the PRODUCER contradicted the table. The flag lives on `Ast` (internal.h,
  read by `p_rep`) because the node KIND cannot carry the fact, and the
  boundary is BARE-vs-SCOPING rather than "produces no atom": the genuinely
  lexical constructs produce no atom either and are TRANSPARENT — libpcre2
  compiles `a\Q\E*` and `a(?#c)*`, letting the quantifier reach back to the
  preceding atom. 560-cell differential (5 positions × 16 runs × 7
  quantifier forms): 455 cells where the oracle rejects and pcrec ACCEPTED,
  now 0, with the blame OFFSET byte-identical to libpcre2's on all 455; the
  105 cells the oracle accepts are unmoved, so there is no over-rejection.
  The x/xx LEVEL is adjacency-sensitive and a later bare `x` downgrades — every
  clause probe-cited in the port's comment. The x/xx CONSUMER (skip set,
  comments, class-interior deletion) lives in parse.c's lexer helpers
  (MOD-0.5d): `xskip`, `cls_skip`, `cls_peek_past_dash`
- **mod_uprops.c** — module `unicode-props` (MOD-0.6 phase 2): the `\p`/`\P`
  doorway's BODY SCANNER, NO PRODUCER (nothing that refuses today may start
  compiling — Frank's ruling). Measured against libpcre2 10.46
  (tests/probes/probe_uprops.c, a full 256-byte tail sweep): `\p`/`\P` have
  NO decline-shaped tail at all — every byte lands on {COMPILES, PCRE2 err
  146 malformed, err 147 unknown-name} — so the row's `recognise` field
  answering "always" (a MARKER, `pcrec_registry_uprops_recognise`,
  mirroring `pcrec_registry_option_run_recognise`'s pointer-identity shape)
  is the permanently correct answer, not a Q2-shaped over-promise. `\p`/`\P`
  stay longhand rows in registry.c for that one field; ext.c keys off the
  marker's pointer identity and calls `pcrec_modport_uprops` DIRECTLY
  (bypassing `aport`/`cport`, which stay `NO_PORT` — no producer this
  phase), REFINING the refusal into the measured malformed(146)-vs-
  unknown-name(147) split with a load-bearing OFFSET (the S27 lesson) —
  where the pre-existing generic fallback gave one text at the backslash's
  offset for every tail. The STREAMING NORMALISATION ALGORITHM (normalise
  while scanning, insignificant space/tab/hyphen/underscore, ASCII case
  folded, a leading `^` consumed once and excluded from the count) stops at
  `PCREC_UPROP_NAME_MAX` (48, `src/core/limits.h`'s PCRE2 INTERNALS
  section) SIGNIFICANT characters — confirmed, not merely assumed, by
  locating the blame offset TWICE (a bare run and one padded with
  insignificant filler between every character) and finding it tracks
  significant-character count, never total body length. The SHORT-NAME
  TABLE (`C L M N P S Z`, case-insensitive, 14 of the 52 possible letters)
  is HAND-WRITTEN rather than generated from a libpcre2 census — a manager
  ruling (2026-08-12 phase-2 authorization), overriding this module's own
  design note: a table generated from
  libpcre2 and checked by a PC-3 differential against the SAME libpcre2
  install is one source wearing two hats, this project's recurring
  check-design failure. Used ONLY where pcrec's table is EXHAUSTIVE for the
  axis (a single significant character, no `=`); a multi-character or
  `Script=`/`sc=`-shaped body promises the module WITHOUT any lookup, so
  pcrec's own "not recognised" wording is never a claim about PCRE2's
  opinion, only about pcrec's own (partial, stated) vocabulary. `\N{U+`'s
  own K10 fix (registry.c's flag removal) is a SEPARATE change and landed
  first — see registry.c's own comment on that row and
  tests/registry/CLAUDE.md's `check_class_syntax_reach` entry. **Slice 5
  (mech finding)**: the brace path's table lookup became FOLD-FREE
  (`uprops_short_lookup` expects an already-folded byte; only the
  bare-letter path folds at its call) after mech measured S34 UNDETECTED —
  the lookup's own re-fold was silently repairing a sabotaged accumulator,
  the control-sharing-a-source shape. S33 (caret consume) was also
  UNDETECTED at first landing for a different reason (its predicted flip
  misread ruling 3's generic-message design). Both histories + fixes:
  docs/design/design_notes_mod06.md §8.3 and the sabotage files' own headers.
  K16 (docs/dev/known_issues.md, found at R19 close, ruled deferred-to-producer)
  records the malformed-body-byte divergence — 164/256 body bytes are
  err-146 to libpcre2 at the byte; this scanner reads past them; the fix
  lands with the first producer
- **mod_named_groups.c** — module `named-groups` ([M6.3]): one shared
  producer, `pcrec_ngport_declare`, for all three declaring spellings
  `(?<name>...)` `(?'name'...)` `(?P<name>...)` — which spelling dispatched
  is read off the elected row's own `sel`/`tail`, and everything else
  (name grammar, numbering, duplicate check, body parse) is identical. The
  first construct wired through ext.c's GENERAL producer-invocation path
  (`group_answer`'s new `if (want == WANT_RESULT && r->aport.kind ==
  PORT_FN)` branch, below the option-run family's own special-cased one) —
  every future `(?` producer that is not shaped like an option run reaches
  its construct through that branch rather than adding a second
  special-cased block. Name grammar MEASURED against libpcre2 10.46
  (tests/probes/probe_named_groups.c): first byte letter/`_`, later bytes
  alnum/`_`, max 128 bytes (`PCREC_MAX_GROUP_NAME`, limits.h; PCRE2 error
  148 above — a measured wall, not PCRE1's older 32-byte folklore),
  duplicate name a compile error (no DUPNAMES; `(?J)`/DUPNAMES itself is
  RULED OUT OF SCOPE, mod_modifiers.c's own 'J' case refuses it
  unconditionally). NUMBERING is the base grammar's opening-paren-order
  rule with ONE measured divergence: `cx->ncap` increments UNCONDITIONALLY
  here, ignoring `cx->mods.nocap` — `(?n)` suppresses a PLAIN group's
  number but not a named one's (probe step 9). ENGINE: no new forcing rule
  — a named group's `A_CAP` node is indistinguishable from a plain
  group's, so `src/opt/select_engine.c`'s pre-existing generic
  capture-forcing rule already selects the VM whenever it delivers a real
  slot; see docs/dev/decisions.md D59 for why the three declaring rows'
  `engines` mask moved to `ANY_ENGINE` instead of SR-8 being built (D55's
  own tripwire fired exactly as its "Revisit when" predicted, and this is
  the answer). `Ctx.named_groups`/`n_named_groups` (internal.h) carry the
  declared (name, number) pairs — a lexical fact recorded regardless of
  `want_caps` — for `src/gen/emit_dfa.c`'s `emit_info_def` to sort
  (`strcmp` on name, matching PCRE2's own measured `PCRE2_INFO_NAMETABLE`
  order) and stamp into `rx_info.groups`/`nnames` at emission.
- **mod_assertions.c** — module `assertions` ([M6.2] WAVE A): one shared atom
  producer, `pcrec_asrtport_atom`, for `\A`, `\Z` and `\z`, dispatching on
  the elected row's own `sel` — mod_named_groups.c's shape and the same
  reason. **Two of the three are EXACT ALIASES of nodes pcrec has shipped
  since M1** and this is the cheapest finding in the module
  (docs/design/assertions_design.md §3.2, measured at 1,008 differential cells
  / 0 disagreements rather than read off the comments): `A_BOL`'s own comment
  is PCRE2's `\A` word for word and `A_EOL`'s is PCRE2's `\Z`, so both are
  parser rows with NO engine work. `\z` is not — "end of subject, full stop"
  is strictly stronger than `\Z`, and it gets its own `A_END` kind, its own
  `N_END` NFA kind, a third closure view (src/ir/dfa.c) and a third position
  view in both emitters, per D62's kinds-encode-structure principle.

  **`Ast.u.anch.multiline` is deliberately left at the arena's zero here**, and that
  is the alias claim's fine print rather than an omission: PCRE2's `\A`/`\Z`
  are UNAFFECTED by multiline, so `(?m)\Z` still means the subject end while
  `(?m)$` means before every newline. parse.c's `^`/`$` cases copy the scoped
  state; this port must not, and the zero is the correct value.

  The three registry rows are LONGHAND rather than `ESC_CLASS_INVALID` for
  exactly one field (`aport`) and keep `RF_CLASS_INVALID` and `NO_PORT` at
  class position: `[\A]` is PCRE2 error 107 permanently, so an ATOM producer
  must not quietly become a class one. NOT REPEATABLE is inherited rather than
  restated — `\A*` `\z*` `\Z*` are all error 109 while `(\z)*` compiles
  (measured), and A_BOL/A_EOL were already in parse.c's bare-quantified
  rejection, so A_END simply joined it and the two group-wrap sites.

  **[M6.2] WAVE B added `\b` and `\B` to the SAME producer**, dispatching on
  `sel` exactly as the three above do, and lowering to two kinds rather than
  one kind plus a negation flag on D62's principle — no option turns `\b` into
  `\B`, so the distinction is structure. They are the module's first CONTEXT
  assertions: `\A`/`\Z`/`\z` are questions about the POSITION, answerable by
  an integer compare, while these read the two BYTES around it, which is what
  buys the alphabet refinement, the state-identity bit and the class-indexed
  accept in src/ir/ and src/gen/.

  **THE TWO ROWS ARE ASYMMETRIC AT CLASS POSITION AND THAT IS PCRE2'S, NOT
  THIS MODULE'S TO TIDY.** `\b` KEEPS its scalar class port — inside a
  character class `\b` is not an assertion at all, it is base syntax for
  backspace (0x08) — so its atom port lands beside a LIVE `cport`, the only
  row in the module where that happens. `\B` keeps `RF_CLASS_INVALID` and
  `NO_PORT` for `\A`'s reason. `tests/registry/registry_check.c`'s port
  census pins both halves: the atom population moved 29 -> 31 and the SCALAR
  population stayed at 5, and an atom producer that had swallowed `\b`'s class
  position would move the second number. NOT REPEATABLE inherited the same
  way, re-measured against libpcre2 10.46: `\b*` `\b+` `\b?` `\b{2}` `\B*`
  are all error 109 and `(\b)*` `(\B)*` both compile to (0,0).

  **[M6.2] WAVE D added `\G` to the SAME producer**, dispatching on `sel` like
  the five above, keeping `RF_CLASS_INVALID` and `NO_PORT` at class position
  (`[\G]` is PCRE2 error 107, measured). It is a THIRD kind of question again:
  `\A`/`\Z`/`\z` compare the position against a COMPILE-TIME constant,
  `\b`/`\B` read the two bytes around it, and `\G` compares it against a
  RUNTIME value the match call supplies — `<prefix>_search`'s own `startpos`
  (docs/spec/match_api.md §3.1). That is what buys a closure bit and a second
  family of start states in src/ir/dfa.c and an extra parameter on the VM's
  `match_anchored`, and nothing at all in the alphabet: it reads no byte. Not
  repeatable, measured the same way: `\G*` `\G+` `\G?` `\G{2}` `a\G*` are all
  error 109 and `(\G)*` compiles to (0,0).

  **[M6.2] WAVE E added `\K` to the SAME producer AND CLOSED THE MODULE** —
  all eight constructs now dispatch through `pcrec_asrtport_atom` on `sel`.
  Same longhand row, same `RF_CLASS_INVALID`/`NO_PORT` at class position
  (`[\K]` is PCRE2 error 107, measured), same inherited not-repeatable rule
  (`\K*` `\K+` `\K?` `\K{2}` `a\K*` are error 109 and `(\K)*` compiles).
  The port census moved 32 -> 33 with the SCALAR population unmoved at 5 for
  the fourth wave running.

  **AND IT IS THE ONE ROW IN THIS PORT THAT IS NOT AN ASSERTION.** Every kind
  above asks a QUESTION about the position and can answer no; `\K` always
  succeeds, reads nothing, and WRITES — it moves the reported start of the
  match. Two consequences live here rather than downstream. First, this port
  records `cx->first_kreset_pos` (on `first_cap_pos`'s precedent, first-wins),
  because `src/opt/select_engine.c` decides the engine by WALKING the AST for
  an A_KRESET — the honest question, since the reported start is
  path-dependent exactly when such a node exists — and no AST node carries a
  source position for the `engine_why` stamp to name. Second, `\K` is the
  module's only VM_ONLY row, and wave E is the day
  `tests/registry/registry_check.c`'s engine-capability tripwire FIRED for the
  first time since [M4.7a] wrote it. The answer was not to build SR-8's
  generic registry-column consultation at sample size one, and not to
  allowlist the row either: the tripwire gains a NAMED exception that PAYS,
  asserting live that `--engine=dfa` on `a\Kb` refuses by the construct's own
  name. A second construct arriving there is when SR-8 has earned its axis.

  **[M6.6.2] `A_LOOK` ANSWERS `false` TO THAT PREDICATE, AND THE REFLEX ANSWER
  IS THE WRONG ONE** — which is the best available demonstration that the rule
  it encodes is PCRE2's GRAMMAR and not "is this zero-width". A lookaround IS
  zero-width, and `true` would refuse `(?=a)*`; `lookaround_design.md` §2.6
  measured all fourteen quantified forms compiling in BOTH oracles. It is
  `A_ATOMIC`'s answer for `A_ATOMIC`'s reason: a bracketing construct with a
  body of its own is not a BARE assertion standing alone.

  **THE BARE-ANCHOR RULE IS NOW ONE FUNCTION, AND WAVE D FOUND OUT WHY IT HAD
  TO BE.** `pcrec_is_bare_anchor` / `pcrec_wrap_bare_anchor` (parse.c, declared
  in core/internal.h) are the single home for the node-kind set that drives two
  rules — `try_quant` REFUSES a bare quantified one, every group form WRAPS it
  so the quantifier lands on an `A_CAT`. It used to be FOUR hand copies
  (`try_quant`, `p_group_body`, mod_modifiers.c's `(?i:...)` port,
  mod_named_groups.c's declaring port) and they had ALREADY DRIFTED: wave B
  added `\b`/`\B` to two of them and not to the other two. A tier-2
  over-rejection rather than a miscompile — invisible to a corpus of ACCEPTED
  patterns — and exactly the several-homes drift D24's registry exists to
  prevent one level up. Found and fixed by this wave while adding the sixth
  kind. **THE TWO STALE COPIES WERE NOT EQUALLY REACHABLE, measured on a
  pre-fix build**: mod_modifiers.c's is live on the DEFAULT path (`(?i:\b)*`,
  `(?i:\B)*`, `(?i:\G)*` all refused where libpcre2 gives (0,0)), while
  mod_named_groups.c's is reachable only under `--no-captures`, because a
  named group wraps its body in `A_CAP` and an `A_CAP` is not a bare anchor.
  The two halves are therefore pinned in different places — gpos.rxt section 8
  and run_assertions_tests.sh §2b — since no `.rxt` block can pass a flag.

  `not_repeatable` is deliberately NOT part of the predicate: it is a
  per-NODE flag a bare option run sets (R20/SPEC-1), and it must not be
  wrapped — `(?:(?i))*` is error 109 where `(^)*` is not.
- **mod_lookaround.c** — module `lookaround` ([M6.6.2] wave B+C): ONE group
  port, `pcrec_laport_group`, for ALL SIX registry rows — `(?=...)` `(?!...)`
  `(?*...)` and the three `(?<` tails `=` `!` `*`. Design:
  docs/design/lookaround_design.md, panel-approved R33.

  **ONE PORT AND NOT SIX**, because the six constructs differ ONLY in the
  three `Ast.u.look` flags the port sets, and a second port function would be
  a SECOND PLACE the `(?<`-tail split is decided. The dispatch is a single
  table keyed on the row's own `sel`/`tail` — the same two fields
  `pcrec_registry_arbitrate` matched to elect the row — so the port cannot
  elect a different construct than the registry did.

  **[M6.6.2 wave F] ONE PORT FOR EIGHTEEN ROWS, and `la_kind` is still the
  ONE PLACE the flags are decided.** The twelve `(*` alpha spellings carry
  the same port in their own `aport`, and an alias row is resolved through
  its `family` — the primary's own `syntax` (D71 item 3) — to the PRIMARY
  ROW, whose `sel`/`tail` then select the LaRow. So an alias gets no flags of
  its own to be wrong about, and twelve more LaRow entries would have been
  twelve more chances for `(*nla:` to come out positive. The resolution is
  ONE LEVEL by construction (a primary has no `family`); a dangling or
  chained reference falls out as NULL and reaches `BAD_ROW`, and
  `check_families` in tests/registry/registry_check.c fails it long before a
  user could.

  **THE WAVE B+C SPLIT WAS THAT TABLE'S `built` COLUMN, AND WAVE D SPENT IT.**
  D65 derives a row's `built` status from the PORT's `ExtResult` at
  `WANT_RESULT` (syntax_dump.c) and never runs the emitter, so the column
  flips for exactly the rows whose tail this port ACCEPTS. Wave B+C recognised
  the three LOOKAHEAD tails and DECLINED the three `<` tails with the
  enabled-but-unbuilt refusal — three rows `built`, three `unbuilt`, no row
  outside module `lookaround` moved. **Wave D landed the back-step seam entry
  (`PCREC_ENCE_BACK_STEP`), deleted the decline, and DELETED THE `built`
  COLUMN WITH IT**: it carried exactly one fact, that `vm_look` had no
  back-step, and there is nothing left for it to say. All six rows read
  `built`; the registry tally moved 55+45 -> 58+42 and the SR-8 witness gate
  demanded three new witnesses automatically, with no edit to the gate.

  The decline WAS an `EXT_REFUSAL` and not an `EXT_NOT_MINE` because the `(?`
  doorway CANNOT decline (its catch-all is REJECTED, so `EXT_NOT_MINE` from it
  is a registry defect the wall reports). A refusal answered AT `WANT_RESULT`
  is D33's "gate open, port missing" signal, which is the one D65 reads — and
  §2.5's VARIABLE-WIDTH refusal, which is what this port answers in its place,
  is deliberately NOT that signal: the module is enabled and the row is built,
  so it is the CAPABILITY tier and is worded as one.

  **AND IT OWNS §2.5's WIDTH RULE, added at wave D.** `la_widths` walks the
  body's TOP-LEVEL branches and stores each one's fixed width in
  `u.look.widths`/`nbranch` (arena `int *`, D70). Two things about it are not
  the first thing a reader expects. WRITTEN ORDER IS THE REVERSE OF THE WALK —
  `p_alt_info` left-nests a flat alternation, so descending the `->l` spine
  yields branches BACKWARDS and the table is filled from the END, which is
  what makes `widths[0]` the branch PCRE2 tries first (§2.4 level 1, measured:
  `(?<=(a)|(aa))c` on "aac" reports g1=(1,2)). And the BRANCH COUNT comes from
  `AltInfo.nbr`, computed by the loop that DROVE the parse, never re-derived
  from the text: a `|`-counting scanner would be a second implementation of
  the branch-splitting rule and would get `(?<=(a|bc))x` (refused, ONE branch
  of width 1..2) and `(?<=a|bc)x` (shipped, TWO fixed branches) exactly
  backwards — the two cells §2.5 exists to distinguish.

  **IT ALSO OWNS §2.7's `\K` CHECK, WHICH IS NEEDED RATHER THAN FREE.** `\K`
  is module `assertions` and already ships, so without a check `(?=a\K)b`
  would compile today's `\K` inside tomorrow's lookaround and quietly move
  the reported match start. libpcre2 10.46 refuses it in all four polarities
  (err 199) and Frank ruled the refusal PERMANENT on 2026-08-23 — the
  `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` bit that would restore the old semantics
  is not adopted and is not to be proposed. `la_has_kreset` is a RECURSIVE
  walk through nested groups AND nested lookarounds and stops AT the
  assertion's `)` (R33 C1-7): `(?=(a\K))x`, `(?=a(?:\K))x` and
  `(?=(?:(?=\K)))x` all refuse, while `(?=a)\Kb`, `a(?=b)\Kc` and `a\Kb`
  all compile. Both directions are `tests/lookaround/refused.rxt`'s, and the
  offset is the ASSERTION's rather than the `\K`'s because `Ast` carries no
  position of any kind.

  `not_repeatable` is PROPAGATED from the body, as A_CAP's and A_ATOMIC's is.
  Note what that does and does not decide: `(?=a)*` and the other thirteen
  quantified forms compile (`pcrec_is_bare_anchor` answers FALSE for A_LOOK,
  which is what lets them), while `(?=(?i))*` — which libpcre2 ACCEPTS,
  measured at this wave — is refused exactly as pcrec already refuses
  `((?i))*` and `(?>(?i))*`. That is ONE pre-existing question about a bare
  option run, not a new one this construct gets its own answer to.
- **mod_atomic_groups.c** — module `atomic-groups` ([M6.4.2]): the `(?>...)`
  group port (`pcrec_agport_atomic`, wired through ext.c's GENERAL
  producer-invocation path, mod_named_groups.c's precedent), and
  `pcrec_atomic_suffix_row`, the lookup parse.c's possessive-suffix desugaring
  stamps from. Design: docs/design/atomic_groups_design.md, panel-approved R31.

  **TWO SPELLINGS, ONE NODE KIND, TWO PRODUCERS.** `(?>X)` arrives at the port;
  `X*+ X++ X?+ X{n,m}+` do NOT — `p_rep` in parse.c recognises the `+` after a
  quantifier it has already accepted and desugars to `A_ATOMIC(A_REP(X))`,
  PCRE2's own definition. That equivalence is MEASURED over bodies whose
  iteration can end in two places (18 pairs / 47 cells / 28 non-unique-body /
  0 disagreeing); the first version of the measurement used only unique-
  iteration bodies, where per-iteration and group-exit cutting CANNOT differ,
  and was rebuilt after the R31 panel refuted it as evidence.

  **THE SUFFIXES HAVE REGISTRY ROWS AND NO DOORWAY**, which is a new shape for
  this directory: `RK_QUANTSUFFIX`, four rows, consulted by the DUMP and by
  `p_rep`'s stamp lookup and by nothing on the base path. registry.c's header
  has always listed the possessive `+` as a deliberate exemption because a
  doorway would cost the base tier a lookup on every quantifier; that reason is
  preserved exactly and the rows close the OTHER half of the problem — without
  them `--list-syntax` and the generated compliance index say `(?>...)` is
  built and say NOTHING about the four suffix spellings, so a reader cannot
  tell "not implemented" from "not in the table".

  **THE ENGINE STAMP (SR-8, D67), and there is no `forces_atomic`.** Both
  producers write `Ast.reg` — the ROW, not a copy of its `engines` mask, so the
  column keeps one home and select_engine.c can also name the construct. An
  unstamped node claims BOTH engines, which fails in the UNSOUND direction on
  purpose: what catches a forgotten stamp is the generic tripwire in
  tests/registry/registry_check.c, not a lucky default. `Ctx.first_atomic_pos`
  is `first_kreset_pos`'s twin, first-wins, and supplies the DIAGNOSTIC's
  offset only — the verdict walks the post-discharge tree.

- **mod_backrefs.c** — module `backrefs` ([M6.5.2]): four producing ports and
  the end-of-parse resolution pass they all feed. Design:
  docs/design/backrefs_design.md, panel-approved R32.

  **FOUR PORTS, ONE NODE KIND, AND ONE PORT THAT ALSO PRODUCES CHARACTERS.**
  `pcrec_brport_digit` owns the ten digit rows and PCRE2's octal
  disambiguation, which makes it the only producer in this directory that can
  return something that is not its module's construct: rules 1 and 3 make `\0`
  and a re-read multi-digit run ORDINARY CHARACTERS. `pcrec_brport_g`,
  `pcrec_brport_k` and `pcrec_brport_pname` are pure reference producers.

  **THE OCTAL RULE IS FOUR ORDERED QUESTIONS**, and stating it in that order is
  what makes rule 3' fall out instead of being a special case: does the run
  start with `0` (octal, at most three digits); is it a single digit 1-9
  (backreference, WHOLE-pattern count); does it have an octal reading at all,
  i.e. start 1-7 (backreference if that many groups exist SO FAR, else octal);
  otherwise it starts 8 or 9, which are not octal digits, so the re-read would
  consume ZERO digits and PCRE2 reads the whole DECIMAL number. The ASYMMETRY
  between questions 2 and 3 is the finding, and no test using only
  groups-before will see an implementation that gets it backwards.
  **The octal SCAN itself is not written here**: `pcrec_clsport_octal`
  (parse.c) is the base grammar's own measured rule and the CLASS position's
  producer, so calling it is what keeps the two positions from acquiring two
  implementations of one PCRE2 fact.

  **THE STAMP GOES ON THE `A_BREF` AND NOWHERE ELSE**, which is a per-NODE
  answer to a per-ROW question rather than a forgotten stamp. `\1`'s row is
  VM_ONLY, but `(a)\10` is the octal byte 0x08 — an ordinary character with no
  VM requirement — so stamping the character node the octal re-read produces
  would refuse `--engine=dfa '(a)\10'` for a construct that is not there.
  Asserted in both directions by `run_backref_diff.sh` §7.

  **NOTHING HERE RESOLVES A REFERENCE.** Every port RECORDS one (`PendingRef`,
  core/internal.h) and `pcrec_bref_resolve` settles all of them at end of
  parse — which is what makes forward references legal BY CONSTRUCTION rather
  than by an exception, and what gives the numeric, relative and by-name
  spellings ONE definition of "group k exists". That single definition is
  load-bearing rather than tidy: while the relative form refused at the port
  for a number out of range, the `\g` row's own `syntax` (`\g{-1}`, standalone)
  refused there too, and D65's built-status derivation called a construct this
  module BUILDS `unbuilt`. The ONE thing that cannot be deferred is rule 3's
  backref-vs-octal decision, because deferring it would let a later group
  retroactively turn an octal literal into a reference.

  **AND IT DELETES `A_CAP` WRAPPERS.** Under `--no-captures` a group a
  BACKREFERENCE names still needs its internal slots (§6.3), and "will any
  reference name this group" cannot be answered at the opening paren — a
  FORWARD reference makes it unanswerable there in principle, and the lexical
  pre-scan that could answer it is the one `Ctx.ncap`'s comment records as
  dead. So `p_group_body` and `mod_named_groups.c` now build the wrapper for
  every numbered group and this pass removes the ones nothing reads; for a
  pattern with no reference that is ALL of them, which is what makes the
  emitted C identical to what it always was. `tests/codegen/run_backref_identity.sh`
  is where that stops being an argument.

- **parse_mods.h** — the SCOPED INLINE-OPTION STATE's definition, and the
  header NOTHING outside this directory includes ([M6.2] wave A; D62;
  assertions_design.md §8.6). `Ctx.mods` is a pointer to an INCOMPLETE
  `ParseMods` in core/internal.h, so §8.2's invariant — *scoped modifier state
  is resolved at parse time, onto the node; no post-parse pass reads it* — is
  a COMPILE ERROR outside `src/parse/` rather than a discipline rule. It was a
  discipline rule until wave A and exactly one pass broke it
  (src/opt/possessify.c, reading the parser's END-OF-PATTERN multiline state
  at verdict time: a scope-blind miscompile waiting for `(?m)` to be
  accepted). If a pass elsewhere needs to know what a modifier decided, the
  answer is a FIELD ON THE NODE set by the parser — `Ast.u.rep.greedy` from `(?U)`,
  `Ast.u.anch.multiline` from `(?m)` — not a wider read. `pcrec_parse_mods_init`
  (parse.c) is the ONE seeding entry point; `src/core/compile.c`'s two
  `cx.mods = (ModState){...}` assignments are gone, and every Ctx that can
  reach a parser or a doorway port (including syntax_dump.c's two query
  surfaces, which can reach module `modifiers`' producing port) calls it.
- **syntax_dump.c** — rendering the registry as text (SR-3) AND, since
  MOD-0.7, querying the live parse front: `--list-syntax`
  (TSV — 12 columns at SR-4, 15 since MOD-0.1 appended `roadmap`,
  `quantifiable` and `class_expect`, all on 2026-08-11, 16 at D65's `built`
  and 17 at [M6.6.2] wave F's `family`; columns are APPENDED,
  never reordered, so consumers' positional reads survive),
  `--list-families` (TSV, 7 columns — D71 item 3's INDEX LAYER: one line per
  family, where a family is the rows sharing a key and a row's key is its
  `family` column if set and its own `syntax` otherwise, with `built` ANDed
  over the members. A SECOND dump for `--list-verbs`' reason: `--list-syntax`
  is per-ROW and its consumers depend on that — tests/reject/ probes every
  non-base row's own `syntax`, and a collapsed dump would have silently
  dropped twelve probes), `--list-verbs`
  (TSV, 6 columns — the Q1 name tables, which are not RegRows and so cannot
  appear in the row dump whose format SR-4 froze), `--explain`, and since
  MOD-0.1's slice 8 `pcrec_probe_ask` (`--probe-ask` — ONE doorway call at a
  chosen want level with the real cursor reported before/after, routed by a
  bytewise scan to the first doorway opener in full-text coordinates, `(?:`
  excluded exactly as parse.c excludes it; the check06 cursor-rule channel,
  10 TSV fields appended-never-reordered).
  **MOD-0.7 made this file a CALLER of the doorways, not only a renderer.**
  The bytewise scan is now `doorway_route`/`doorway_call`, file-statics with
  TWO callers — `--probe-ask` and the rewritten `--explain` — because a second
  router would drift and the drift would be invisible, each surface staying
  self-consistent with itself (extraction evidence: 1089 `--probe-ask` cells
  byte-identical, check06's floors unmoved). `--explain` was a mutual-prefix
  match on the `syntax` column with no `ext_`/`arbitrate` reference at all,
  which R10/C4-2 refuted as a control and which made D29's own worked example
  (`--explain '(?i-m:'`) fail; it now prints the ROW's declared attribution
  beside the LIVE doorway's answer and compares them per row (election,
  promise, attribution — `docs/design/design_notes_mod07.md` §5.2), selecting rows by
  prefix UNION bucket-candidates with each row tagged which rule found it, and
  exiting 3 when a row DISSENTS.
  **THE CLAUSES ARE SCOPED TO THE CLOSED GATE since R20/MOD07-2+3**, and the
  scope is the correction: §5.2's census was taken at the closed gate while
  the implementation asked its clauses at whatever `--features` said, so the
  enabled set was an axis the predicate had never been established over. Two
  defects lived there — `--features modifiers --explain '(?J)'` DISSENTED on
  attribution about a tree tests/reject:664 pins as CORRECT (an enabled
  option-run port refuses per LETTER, and a letter's module is not the
  dispatching row's), and a producing answer short-circuited promise and
  attribution away, so opening a gate SHRANK the coverage of the rows it
  turned on. Now TWO calls per displayed row: the `own *` fields show the
  REQUESTED-gate answer as DATA, and a second `WANT_VERDICT` call is what the
  clauses judge. `WANT_VERDICT` is how "the default enabled set" is reached
  without a process-global being rewritten — `pcrec_ext_gate` only demotes and
  floors at VERDICT, so no enabled set can promote it, and a BASE port answers
  at the level asked (measured equivalent to a default-set RESULT ask on all
  100 rows, every `--probe-ask` field compared). A FOURTH clause, `gate`, is
  the one thing an open gate is good for here: a row that PRODUCES must have
  its declared module in the enabled set — the cross-check the short-circuit
  walked past. Total over the table at every gate state, measured as a
  100-row × 5-gate-state census: 0 dissents everywhere, against 2 at
  `modifiers` and 2 at `all` before.
  **The honest limit, measured and repeated
  here because it is the thing a reader will assume wrongly: the attribution
  clause CANNOT dissent on a module-name swap** — ext.c renders "requires
  module '%s'" from the same `r->module` this file prints, so the two agree by
  construction (100 rows, zero census difference under C4-1's sabotage).
  Module-name truth is `tests/reject`'s hand pins; what the live call adds is
  ELECTION, which no existing check has, because 13 rows share their rendered
  diagnostic with a bucket sibling. MOD-0.7 also fixed K14 HERE: the `status`
  line promised module `callouts` for the ROADMAP_NEVER row while ext.c and
  `put_expect` in this same file had both been roadmap-aware since MOD-0.1.
  **BOTH QUERY SURFACES `setjmp` THEIR OWN Ctx since R20/MOD07-1**, and
  `doorway_call`'s comment — which had named "the first enabled,
  result-producing module port" as the event that must revisit the zeroed Ctx,
  two milestones after that port landed — is rewritten as a discharged
  obligation. A raising port used to SIGSEGV both surfaces; it now abandons
  the answer and returns NULL with a `pcrec_error` filled, which the CLI
  renders in the compile path's own shape. Both surfaces `arena_free` too
  (`--probe-ask` never did). **`--explain`'s value renderings escape control
  bytes** (R20/MOD07-8, `put_text`: bytes below 0x20 and 0x7f as `\xHH`, `\`
  deliberately not doubled) — the format grammar had no escaping, so a query
  containing a newline injected a synthetic header line that the test
  suite's own `explain_field` parser read as real. Internal, not public API — the CLI and the
  test suite are the only consumers, and promoting a function into lib/pcrec.h
  later is easier than un-promoting it. SR-4 makes this dump load-bearing, so
  its FORMAT is an interface: no field may contain a tab or a newline, which
  tests/cli case 10 asserts by counting fields

  **[D65] (2026-08-21, docs/design/registry_built_status_memo.md, ratified
  wholesale) — `--list-syntax` gains a 16th column, `built`.** A THIRD
  question beside `status`/`roadmap`'s two ("is this base grammar" /
  "will a module ever implement it"): has the owning module's producer
  actually LANDED, per construct. `pcrec_construct_built_status` (the
  exported entry both this dump and `tests/registry/registry_check.c`'s
  defect assertion call — one derivation, two callers) reuses
  `doorway_route`/`doorway_call` exactly as `--probe-ask`/`--explain` do,
  with EVERY module forced open (`src/parse/enabled.c`'s process-global
  set, saved via `pcrec_enabled_set_modules()` and restored exactly after —
  the same shape `pcre2_check.c`'s "gated pass" already uses), and
  classifies on `res.what` + `res.answered_at` rather than on refusal TEXT
  — see its own comment in this file for the three real rows (module
  `verbs`, module `unicode-props`, and the cross-module `(?m)` case) a
  narrower text-matching first draft measured wrong on before landing on
  this shape. `PCREC_BUILT_NA` ("—") for `RS_BASE`/`RS_REJECTED` rows,
  where the question does not arise; `PCREC_BUILT_DEFECT` for a row whose
  own well-formed `syntax` answers neither way — never rendered as a
  status, always a `registry_check` hard failure. Measured on the shipped
  registry: 33 of the 34 rows belonging to SHIPPED modules read `built`;
  `(?J)` reads `unbuilt` (module `modifiers`' own permanent, unconditional
  DUPNAMES decline) — the precise distinction a per-module summary always
  blurred, and the reason D65 ruled per-CONSTRUCT granularity.

## PARSE-1 — `p_alt` as a module callback (2026-08-11)

Three defects made `p_alt` unusable as the callback D28/D29/D30 promise. All
three are fixed or recorded here; none adds a construct, so parse.c's "stops
growing" rule is intact.

**The group case is now three functions, and the split is load-bearing.**
`p_group` owns a group's ENTRY and EXIT bookkeeping; `p_group_body` owns
everything between `(` and `)` and owns neither end. `cx->depth--` used to sit
AFTER the doorway call, so it was already on a path a module could never reach;
now a `return` added anywhere inside the body function stays balanced by
construction. `ctx_fail`'s longjmp still bypasses the exit, and that is correct
and structural rather than lucky: `src/core/compile.c` holds the ONLY `setjmp`
in the tree, its failure branch runs `job_cleanup` and returns, and `Ctx` is a
stack-local zeroed per `pcrec_compile` call — no caller can observe a
half-unwound depth, and no API reuses a `Ctx`.

**`p_alt` reports what it always computed.** `p_alt_info` fills an `AltInfo`
`{nbr, last_bar}`. It is a struct and not an `int` because `ctx_fail` takes a
POSITION as a required argument, so a module cannot RAISE "more than two
branches" from a count alone; D26 puts pcrec's own offsets against pcrec's own
convention in tier 2, and `Ast` has no position field, so a design that leaves
the AST alone forecloses recovering one afterwards unless `p_alt` reports it.
**The count is computed by the loop that drives the parse**, which is why it
cannot disagree with what was parsed: a `|` inside `[a|b]`, an escaped `a\|b`,
or one inside a group never reaches that loop. `\Q...\E` and `(?#...)` are
siblings of `p_alt`, not children, so `quoting`/`comments` cannot perturb it
either.

**`caseless` moved from the options to the Ctx.** `opt` is `const` and
caller-owned, so D29's "set parse state, parse body, restore" had nothing to
set and `(?i:a)b` was inexpressible. The field is `cx->mods.caseless` since
MOD-0.5c widened the PARSE-1 bool into the ModState struct; it is seeded
from `opt->u.bref.caseless` in compile.c — one home, seeded once — and
saved/restored around every BODY-CARRYING group (the save/restore placement
moved to p_group_body's body tail at MOD-0.5c; a bare option run escapes
its own paren pair's restore by construction — see parse.c's comment at the
splice). That boundary is MEASURED, 17/17
against libpcre2 10.46: `(?i)` set inside a group stays in force to the end of
THAT group, **leaks across that group's sibling alternation branches**
(`(a(?i)b|c)d` matches `Cd`), and is restored at the immediately-enclosing `)`.
A top-level `(?i)` is never restored. So the restore belongs at the group
boundary in the base grammar, not inside a module — the parser must not need to
know whether a module fired.

**The callback itself is `pcrec_parse_body`.** `p_alt` and `p_alt_info` are
static, so ext.c cannot call them, and `pcrec_parse_info` is the WRONG entry
point for a nested body — it requires end-of-pattern and ctx_fails on `)`.
`pcrec_parse_body` parses a body and stops AT its terminator without consuming
it; the CALLER consumes its own `)` and owns its own unterminated diagnostic,
which is what keeps "missing closing ) for group" single-homed (the base grammar
owns it for `(` and `(?:`; a module owns a different message for a different
construct, so this is not the D24 two-homes shape).

**What PARSE-1 did NOT fix, recorded with its repro.** If `pcrec_ext_group` ever
returns a node, control still falls through into the body parse and **the node
is silently discarded**. Reproduced, and it is an exit-0 miscompile: give the
doorway one selector byte that returns a node, and `(?%x)b)` compiles to
byte-identical C to the bare pattern `b` — the module's node AND the pattern's
own unmatched trailing `)` both vanish with no diagnostic. MOD-0.1 owns it; the
shape is to capture the return and BRANCH around the body parse.

**Do NOT copy `pcrec_ext_class_bracket`'s contract for it.** The two doorways'
non-fail outcomes are DISJOINT. class_bracket's three `return;` sites never
write `cx->pos`, so its only normal-return outcome is DECLINE, cursor unchanged.
The `(?` doorway can never decline — `registry.c:505`'s catch-all is `REJECTED`
— so its only future normal-return outcome is CLAIM, cursor past its own `)`.
One signature over both would make "returns normally" mean opposite things
depending which doorway was called.

Checks: `tests/parse/`, and read its CLAUDE.md before trusting the
AST-identity check — it passed on the tree BEFORE PARSE-1 existed and is a
forward-pointing regression net, not evidence the feature is present.

## The construct registry (registry.c, D24)

One declarative home per non-base construct, replacing knowledge that lived in
up to five places at once. `\v` shipped decoding as vertical tab because
`esc_modules[]` and `esc_char_value`'s switch disagreed ten lines apart with
nothing enforcing agreement; a construct with two homes will drift.

Everything non-base enters through exactly **four doorways** — after `\`, after
`(?`, after `(*`, after `[` inside a class — and since SR-2 those doorways are
four real function calls in ext.c. Since SR-9 a doorway is keyed by a byte AND
an optional TAIL, which is what lets `(?P<` `(?P=` and `(?P>` name three
different modules instead of one. parse.c's own switch answers first and
returns in every one of them. A base-tier pattern still reaches the
class-bracket doorway once per non-negated `[` — measured 2026-08-10, `[abc]`
costs 1 lookup and `[a-z]+@[a-z]+\.[a-z]{2,4}` costs 3 — so "no lookup at all"
was wrong; the cost is small, not absent.
`(?:` is the single construct sharing a doorway with non-base syntax, and the
base grammar answers it before the registry is consulted. Its row exists so the
table is COMPLETE for SR-3's dump, not because anything looks it up. SR-5 turns
that from a claim into an instrumented measurement.

Four axes stay apart on purpose: **flavour** (which construct a byte MEANS) /
**option** (what it DENOTES) / **enablement** (is it available) / **engine**
(can it LOWER). A flavour change rebinds a row; it cannot reach inside another
construct's handler. One flavour exists today, by design.

Rules when touching it:

- **Add a row here and nowhere else.** `syntax` must be a pattern that really
  reaches that doorway — tests/registry/ uses it as the probe, so a new row
  covers itself with no test edit.
- **`RS_MODULE` with no handler is a complete outcome**, not a stub: the
  construct is named, cleanly rejected and queryable.
- **The `engines` column is design intent, not measurement.** Nothing consumes
  it — [M4.7a] deliberately did not build SR-8's lowering-time consultation
  ahead of a producer (zero producers, zero customers); a TRIPWIRE
  (tests/registry/registry_check.c's check_engine_capability_tripwire)
  guards the gap instead, asserting every VM_ONLY-masked RS_MODULE row has
  no wired producer. Wiring the first one is what earns the consultation;
  do not build on this column's values without checking them.
- **Two "requires module" diagnostics deliberately stay in parse.c**: `\x{...}`
  (a sub-case of the base `\x` handler) and the possessive `+` suffix (a
  quantifier suffix, not an atom). Neither is a doorway, and giving them one
  would cost the base tier a lookup. `\b` inside a class is base
  SEMANTICS but no longer parse.c's special case: since MOD-0.3d it is the
  row's own BASE class port (ExtPort.base — the gate never touches it), as
  are the octal digits and the literal fallbacks. RF_CLASS_BASE retired
  with the migration; check_class_ports ties the port values to the
  measured class_expect column.
- **A row may carry a `tail`** (SR-9), and since MOD-0.2 (2026-08-11) the
  lookup engine never interprets it: selection is RECOGNISER + RANK (design
  §2.2/D32, kept per-port-ready by Part II §14.4). Each sel-matching row's
  recogniser runs — positive and local, knowing nothing of its siblings; NULL
  means `pcrec_recognise_tail_default` with the row's `tail` as its parameter,
  which is the field's only remaining reader on the lookup path — and the
  highest-ranked ANSWERING row wins. Multiple answers are NORMAL (the bare
  fallback answering "always" is correct, D32 §2); **two answers at the
  WINNING rank is the defect**, rendered by the escape/group doorways as an
  internal error, never resolved by declaration order. Rank tiers are 0
  (fallback / never clashes), 25 (tailed), 70 (`\N{U+`, the longer half of the
  table's one prefix pair) — values are meaningless except between clashing
  rows, documented on RegRow.rank. A tail is still a literal prefix, not a
  pattern — `(?-` keeps ten rows, "0".."9", rather than one "\d" (the `-\d+)`
  collapse is DEFERRED: as written it declines on `(a)(?-1`/`(a)(?-1x)`/
  `(a)(?-1:x)`, PCRE2 error 114, a tier-2 regression; it waits for a passing
  reachability differential). Three bytes use tails: `P` (`<` named group, `=`
  backreference, `>` subroutine call), `<` (`=` `!` `*` are lookaround,
  everything else is a named group) and `\N` (`{U+` is a Unicode code point,
  `{` alone is a construct PCRE2 refuses). **Row ORDER must not be able to
  stand in for the rule** — the `\N` pair stays written SHORTEST first so
  order disagrees with the required outcome; `check_tail_precedence` retired
  WITH committed successors: `check_row_ranks` (tailed row must outrank the
  fallback tier) and `check_arbitration_liveness` (floored multi-answer
  counts per bucket plus the esc-'N' triple-answer assertion, R11/M3's
  counter). The retired SR-9 engine was proven equivalent before deletion:
  a 261,193-probe scaffold plus a 5,247-comparison behavioural differential,
  zero differences.
- **The compound module name is gone.** `M_lookaround_named`
  ("lookaround/named-groups") existed for `(?<`, one byte meaning two
  constructs. A compound name is a true sentence and an inexact answer, and D26
  puts module attribution in tier 2. Reach for `tail` first; fall back to a
  compound name only when the deciding text is not a literal prefix.
- **An inline option setting is a RUN, not a byte** (Q2). Splitting the `(?`
  catch-all into eleven option-letter rows fixed `(?q)` and left `(?iZ)` still
  promising module 'modifiers' for syntax PCRE2 refuses, because the row is
  chosen by the first byte and nothing read the rest. The doorway reads the
  whole run, as Q1 made `(*` read the whole name. The grammar is MEASURED and
  its edges are not guessable from single letters: `a` takes one ASCII-restrict
  sub-option (`(?aP)` compiles, `(?aPP)` is error 111), and a misplaced hyphen
  is error 194 — a MALFORMED option setting, so a module is still owed.
  `RF_OPTION_RUN` said this at MOD-0.5's start; it RETIRED at MOD-0.5b, moving
  to mod_modifiers.c as a `recognise` pointer instead of a flag, and the
  SEMANTICS landed at MOD-0.5c/d — see the mod_modifiers.c entry above for
  the port, the scoped state, and the lexer (one home; this line is a
  pointer, not a second description). See D28 and [MOD-0.5] in docs/dev/plan_completed.md.
- **`RF_CLASS_DELIM` carries a construct's own recognition rule**, not just its
  diagnostic: a delimiter-pair construct opens only when its matching `X]`
  appears later, and the class's own bracket can serve as its `[`. SR-2 moved
  that out of parse.c because it is the construct's rule, not base grammar. All
  THREE class-bracket rows carry it since FIX-2 — the `:` row was missing it,
  which was K3 in both directions at once.
- **`open_msg` is the one field that varies by POSITION**, and only one row uses
  it: inside a class `[[:alpha:]]` is a construct PCRE2 SUPPORTS (name the
  module), at a class's own bracket `[:alpha:]` is one PCRE2 will never accept
  (name none). That is a tier-2 distinction under D26, which is why it is a
  field and not a fifth doorway kind.
- **`RF_CLASS_NAMED` means the text between the delimiters is a NAME from a
  known set**, and an unknown one is not the construct at all. `[[:foo:]]` is
  "unknown POSIX class name", not a promise about module `classes`. It is only
  meaningful ON a `RF_CLASS_DELIM` row — the name is the text the delimiter scan
  measures — and since R9 `registry_check.c` requires that pairing rather than
  leaving it to whoever writes the next row. The 16-name table was regenerated
  independently from libpcre2 at R9, ~2.4 billion probes, and is exactly right.
- **`<` and `>` are POSITION-RESTRICTED**, which R9/C3-4 found pcrec not
  modelling. libpcre2 takes them only as a class's ENTIRE content: `[[:<:]]`
  compiles, while `[x[:<:]]`, `[[:<:]a]` and even `[^[:<:]]` are all "unknown
  POSIX class name" — and every ordinary name works in every position. pcrec
  promised module `classes` for all of them: the same over-promise FIX-2
  removed for bogus names, surviving for the two real names FIX-2 itself
  discovered. `pcrec_registry_posix_whole_class_only()` plus the doorway's
  `at_content_start` parameter is the fix, and `check_posix_positions` in
  pcre2_check.c is what notices it coming back. Neither existing differential
  could: one varies the name with position fixed, the other varies position with
  the name fixed, and the defect was in the cell neither generates.
- **Two things about `pcrec_ext_class_bracket`'s scan that the code cannot say
  about itself** (R9). Its three rules are correct — a critic ran 1,239,480
  generated patterns against libpcre2 with zero verdict divergences — but the
  ORDER of the close check against rule 1 is arbitrary, not load-bearing as the
  comment used to claim: the predicates are disjoint for every delimiter the
  registry can hold, and no delimiter can be `]` because `registry_check.c` now
  forbids it. And `close_at` starts at `from` rather than 0 so that a row
  reaching the name check without having run the scan asks about a zero-length
  name instead of a wrapped `size_t`.
- **A row carries two PRODUCING PORTS since MOD-0.3b** (`aport`/`cport`,
  design Part II §4/§14; full doc on ExtPort in internal.h): tagged
  data-or-function, one per position, NONE at class = permanently invalid
  (§14.3's NULL meaning; slice 3 retired RF_CLASS_BASE into base ports —
  RF_CLASS_INVALID STAYS, because D33 §3's precondition is measurably
  false while lexical and unicode-props rows carry honest NULLs that are
  not permanently invalid; journal 2026-08-12). WIRED since slice 2 (the
  classes producers) and slice 3 (the BASE ports — gate-immune PCRE2 base
  facts); the port DATA is guarded by registry_check's check_class_ports
  (populations pinned, values oracle-tied). Set bitmaps are GENERATED from
  libpcre2 censuses and re-measured by PC-4 — never hand-typed.
- **A verb NAME goes in the VerbName tables, not in a RegRow** (Q1/D25), and
  its form bits are a MEASUREMENT: add the name, then run
  `bash tests/registry/run_registry_tests.sh` and let libpcre2 tell you which
  of VF_BARE / VF_ARG / VF_EMPTYARG / VF_EQNUM / VF_GROUPARG / VF_ATSTART are
  right. Do not reason them out from the PCRE2 documentation; the check will
  disagree with you and it will be correct.

## The `(?` doorway, after Q2

The catch-all row used to answer "requires module 'modifiers'" for every byte.
MEASURED with a generated sweep of all 256 bytes and 45 completions each,
against libpcre2 10.46: **38 bytes begin a construct and 217 do not** (of the
255 probeable ones; NUL is K9's territory). All 217 were promised a module for
syntax PCRE2 rejects outright with error 111 — the same defect Q1 removed at
`(*` and FIX-2 at the class bracket, at the doorway that is 217x wider.

Six over-promises were fixed, and only four of them were on the plan. The other
two came from the sweep, which is the argument for generating an input space
rather than listing it, one more time:

| written | was | is |
|---|---|---|
| `(?q)` and 216 other bytes | module 'modifiers' | PCRE2's error-111 wording, no module |
| `(?+N)` `(?-N)` | 'modifiers' | 'recursion' — relative subroutine calls |
| `(?[...])` | 'modifiers' | 'classes' — an extended character class |
| `(?P=` `(?P>` | 'named-groups' | 'backrefs' / 'recursion' |
| `(?PX)` and 251 other tails | 'named-groups' | PCRE2's error-141 wording *(not on the plan)* |
| `(?iZ)` `(?-Z)` `(?aPP)` | 'modifiers' | no module — the RUN is the construct *(not on the plan)* |

(The `(?[...])` row's "is" column above is Q2-era history: MOD-0.3a
(2026-08-12) moved it again, 'classes' → 'extended-classes', the day module
`classes` gained producers. Same session, `[[:<:]]`/`[[:>:]]` moved to
per-NAME attribution — module 'assertions' — in the PosixName table.)

**The run grammar was wrong twice before the differential accepted it**, and
both errors are worth not repeating. First too strict — "at most one hyphen,
never after `^`" — which UNDER-promised for 24 shapes that PCRE2 calls option
settings (error 194, "invalid hyphen"): a malformed option setting is still an
option setting, and module 'modifiers' is exactly what would diagnose it. Then
wrong about ORDERING: PCRE2 stops at the first error, so `(?--D)` is 194 at the
second hyphen and never examines the `D` that would have been 111. Three
candidate rules, each refuted by measurement — the same shape as K4, where four
measured patterns separated three candidates and no weaker rule got all four.

Do not read a module name here as externally verified. libpcre2 says whether a
construct EXISTS; it cannot say pcrec should call it 'recursion'. The module
names are pinned by hand in tests/reject/, as they have always been.

## The `(*` doorway's NAME tables (Q1 / D25)

Doorway 3 is the only one decided by a NAME rather than a byte, and until Q1
pcrec did not read it: one catch-all row answered "requires module 'verbs'" for
everything, which promised a module for `(*NOTAVERB)`, called `(*)` a verb when
PCRE2 reads it as a quantifier with nothing to quantify, and accepted `a(*CR)`
when a start-of-pattern option away from the start is an error.

Four answers now, and which one is chosen is entirely table-driven:

| written | answer |
|---|---|
| a known name in a form libpcre2 accepts | `(*...) requires module 'verbs'` |
| a name the selected table does not have | `(*VERB) not recognized or malformed` (upper) / `(*alpha_assertion) not recognized` (lower) |
| `MARK` bare or with an empty argument | `(*MARK) must have an argument` |
| an empty name (`(*)`, a truncated `(*`) | `quantifier does not follow a repeatable item` |

Three things that are easy to get wrong here, all measured rather than reasoned:

- **The table is chosen by the CASE of the first name byte**, and by nothing
  else. `(*accept)` is not `(*ACCEPT)` misspelt — it is a lookup in a table that
  contains no `ACCEPT`, and PCRE2 gives it a different error.
- **The terminator set is PER-NAME.** `(*ACCEPT:x)` compiles and `(*CR:x)` does
  not; `(*MARK:)` is an error and `(*ACCEPT:)` is not; only `LIMIT_*` takes
  `=digits`. That is what the VF_* bits record.
- **`VF_GROUPARG` is the difference between two truncations.** `(*pla:x` is
  PCRE2 "missing closing parenthesis" — the name WAS recognised — while
  `(*ACCEPT:x` is "not recognized". A subpattern argument does not need its `)`
  at the doorway; a name-run argument does.

None of these names is implemented. Every one still ends the compile — the
tables record what libpcre2 ACCEPTS, not what pcrec does.

## Case folding (OS-1 / D23)

`options.caseless` (CLI `-i`) is handled entirely here: `cls_casefold` adds
each ASCII letter's other case to a class bitmap, so the automaton is built
case-blind and nothing downstream — NFA, DFA, minimizer, emitter — knows the
option exists. Measured result: `-i 'aBc'` emits byte-identical C to
`'[aA][bB][cC]'`, so caselessness is not an engine axis (D18's case 1).

Two rules that are easy to break and hard to detect:

- **Fold the POSITIVE set, then negate.** `[^a]` caseless means "neither a nor
  A". Folding the complement instead yields every byte. Both results are
  case-closed, so no downstream stage, invariant or equivalence check can tell
  them apart — only behaviour can. Pinned by tests/base/caseless.rxt and by a
  shape check requiring `-i '[^a]'` == `'[^aA]'` and != `'[^A]'`.
- **Every site that builds an A_CLASS must fold.** There are three: char_node,
  p_class, and `.` (which needs nothing — "every byte but \n" is already
  case-closed). A post-parse AST walk would catch future sites automatically
  and is deliberately not used: AST depth is unbounded in pattern length, so it
  would add exactly the recursion DD-10/TS-4 exists to remove. A new
  class-producing construct calls `cls_casefold` itself.

ASCII only — bytes >= 0x80 have no case in the C locale, and Unicode folding
stays with DD-1/M5.

## Conventions

The parser builds an expression AST using recursive descent. Split edges in the AST preserve choice order for greedy/lazy and alternation preference. Non-base syntax is described once, in registry.c's row tables, and reached through the four doorways — three defined in ext.c, the verb doorway in mod_verbs.c since MOD-0.4 (its two name tables moved with it): adding a construct means adding a row, not editing parse.c. Unsupported syntax produces an actionable "requires module 'X'" error rather than a miscompile.

Maintenance: update this file when files are added/removed or their roles change.
