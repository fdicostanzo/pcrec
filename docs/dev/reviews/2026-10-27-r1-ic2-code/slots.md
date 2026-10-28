# ic2 critic: slots (slot tracing, ruling check, house rules)

Subject: lane/ic2 at 864902a48, against BASE 614d45eb3. Review tree:
worktrees/crit-ic2. Read-only. No make was run.

Disclosure: one `git diff 614d45eb3 864902a48 | grep` for abi-number
readers (run with no path filter) printed about 15 matching lines from
denied files: docs/dev/lanes/ic2_report.md, ic2_test_job and ic2_mech_job
(lines that name "abi 89 -> 90", "queue job 621", "emit_sweep", the S693
re-aim). I did not open those files and used nothing from those lines. Every
later diff named its paths.

## Findings

### SLOT-1: the per-option SCOPE row was never filed, and its trigger has already fired in this stage
- CONFIRMED (by grep). Design §5.1 and §9.4 (D20 PLAN) say stage 2 lands on
  today's three mechanisms (the by-name chain in rxt_source.c, the CLI's
  tail-span containment, `saw_prefix`) and that a per-option SCOPE row
  (`any` | `not-config` | `invoker-only`) is FILED, with GRANT as its first
  use and "the next option that needs a scope" as its trigger. That row is
  not in the subject tree: `grep -n 'not-config\|per-option SCOPE\|OPT-SCOPE'
  docs/dev/plan.md docs/dev/decisions.md docs/design/plan_row_bodies/*.md`
  finds nothing, and neither does the same grep on main's plan.md.
  Meanwhile the stage added TWO options that need a scope, not one:
  `--allow-code` and `--code-header`. Both went into the by-name chain
  (src/parse/rxt_source.c:872-887; the chain now has four members:
  --analysis, --measures, --allow-code, --code-header), and both are also
  caught by the tail span (cli/main.c:608-615, the comment says so). So the
  trigger fired inside the stage that was supposed to file the row.
- No fifth OPTION-scope mechanism appeared. `--code-header` with a FILE
  operand ("--code-header applies to --pattern", cli/main.c:3146) sits in the
  existing applies-to family beside `--callout`'s identical refusal, and is
  not a new mechanism. But see SLOT-4: the describe modes' grant is a new
  "which entry may" mechanism, hand-placed.
- Consequence: stage 3 adds pin lines and stage 6 adds template code. If
  either needs a scoped option, the chain grows to a fifth by-name member
  with nothing tracking it.
- Severity: design / maintenance. Effort: file the row (one plan line). Then
  build it now or at the next option; the trigger has fired. Blast radius:
  none (a docs filing).
- GENERAL FORM + UNLOCK: a SCOPE column on the CLI option table, with values
  `any` | `not-config` | `invoker-only`. It replaces the by-name chain's four
  strncmp pairs, and the tail span would then check one column instead of a
  struct layout. `saw_prefix` disappears: `-p` would be `not-config` by row.
  UNLOCK: the `pcrec` line's refusal text is generated per row ("a config
  names X with its own Y line"), so each new head-line/option pair costs one
  row. TRIGGER: already met (two options in this stage).

### SLOT-2: the GRANT column is presented as a general `any | invoker-only` column, but every reader treats "invoker-only" as "code-<lang>"
- CONFIRMED (by reading). RF_INVOKER_ONLY (src/core/internal.h:4612-4624)
  is documented as a general column: "the row's module is INVOKER-ONLY ...
  only the invoker's own grant enables it". Its readers hard-code that the
  module is code, and that its door is `--allow-code`:
  - src/parse/enabled.c:193-195 `INVOKER_ONLY_MSG`: "module '%s' is code;
    code is enabled by --allow-code ...";
  - src/parse/ext.c:589-595: looks the language up by feature, and falls
    back to `r->module` used as a language tag ("--allow-code=<module>");
  - tests/registry/registry_check.c:1260-1265 and :2486:
    `r->module + strlen("code-")`, which reads past the start of any
    invoker-only module whose name does not begin with `code-`;
  - the grant itself (`pcrec_code_grant_resolve`, enabled.c:384) never reads
    the column. It reads the language table, so the column decides only who
    may NOT set the bit. Who MAY set it is a second source, codelang.def.
- Today these are the same set, so nothing answers wrong. The column is not
  the general form it claims to be. It is a code flag under a general name,
  and the door it implies is spelled in three diagnostics and two test
  sites instead of in a column.
- Severity: design / maintenance (names describe behaviour, D174). Effort:
  small, either way. Blast radius: diagnostics only.
- GENERAL FORM + UNLOCK: either rename it honestly (RF_CODE, derived from the
  language table, since every code row is generated there anyway), or give
  the grant its DOOR as data: a per-module grant row (module -> the option
  that grants it, the library member) read by the three diagnostics, the
  resolver and registry_check. UNLOCK: stage 6's template code (`${{...}}`)
  and any later invoker-only module reuse the refusal and the resolver with
  no `strlen("code-")`. TRIGGER: the first invoker-only row not spelled
  `code-<lang>`, or stage 6 if templates get a module of their own.

### SLOT-3: "a later language adds ONE row here; nothing else changes" is not true: the FEAT_* bit is a second hand-written site
- CONFIRMED (by reading). The header of src/parse/codelang.def says a new
  language is one row. Its `feature` column names `FEAT_CODE_C`, which is a
  hand-written enum member in src/core/internal.h:4361-4367 ("One bit per
  registered language"). A second language needs a row plus a new FEAT_ bit
  in a different file, from a mask with a fixed width (bit 19 of an
  `unsigned` today). The pairing is checked: registry_check's bijection
  check (registry_check.c:651ff.) would catch a row sharing a bit. So this is
  a two-site edit, not a silent drift. It still contradicts the table's own
  promise and design §2.2's last paragraph.
- Severity: doc / maintenance. Effort: either generate the FEAT_ bits from
  the def file (an X-macro enum after FEAT_UCP), or correct the comment to
  "one row plus its FEAT_ bit". Blast radius: none today.
- Consequence for [SCANNER-DOGFOOD]: that row adds a per-language scanner
  COLUMN (the def file says so), so the table changes shape there anyway.
  That is the natural point to generate the bit too.

### SLOT-4: the GRANT column is a per-ROW bit where the design names a MODULE column, and the uniformity check its readers rely on does not exist
- CONFIRMED (by reading and grep). Design §5.1: "The module table gains a
  GRANT column". There is no module table. GRANT is `RF_INVOKER_ONLY`, a
  flag bit on each registry row (internal.h:4612-4624). Two comments say
  "Every row of one module carries the same value (registry_check asserts
  it)": internal.h:4621 and enabled.c:177. `module_invoker_only`
  (enabled.c:178-189) depends on that claim, because "the first row
  answers". The assertion is not in the tree:
  `grep -rn 'RF_INVOKER_ONLY\|invoker.only' tests/` finds only the
  diagnostic-wording site (registry_check.c:1260), the engine-witness site
  (:2486), a comment (:2053) and S1683. None of them checks that the flag is
  uniform across a module.
- Why it matters (a trust risk that has not fired yet): `all`
  (enabled.c:290-296) leaves out only the rows that carry the flag, and ORs
  in `rows[i].feature` for every other row. If a module has one row WITH the
  flag and one WITHOUT, `features all` grants that module's bit, and with it
  code. An explicit list (`features code-c`) is refused only if the first row
  found carries the flag. Today `code-c` has exactly one row, so nothing
  leaks.
- Consequence for [SCANNER-DOGFOOD]: that row adds the `(?{` row, a second
  row of `code-c`. If it is generated by the same X-macro as the tagged row,
  it carries the flag. If it is written longhand, or by a second macro that
  forgets `RF_INVOKER_ONLY`, then `features all` silently grants embedded C,
  and the claimed check does not exist to catch it. (S1683 sabotages the
  `all` line itself, not a row that lacks the flag.)
- Severity: trust (it has not fired). Effort: small. Either add the claimed
  registry_check assertion (every row of a module has the same
  RF_INVOKER_ONLY), or compute `all` as the union of features minus the
  invoker-only MASK (the OR of the feature bits of every flagged row), so a
  mixed module fails closed. Blast radius: the gate.
- GENERAL FORM: the grant is a MODULE fact, so its home is a module-level
  row (module -> grant door), not a bit copied onto every row. The language
  table already is that row for `code-<lang>`. SLOT-2's door column and this
  are one fix.

### SLOT-5: the §5.9 entry classes are hand-placed in four product sites, with two spellings of the same describe grant; the TEST derives completeness, the PRODUCT does not
- CONFIRMED (by reading). The design says the entry-point table is "DERIVED
  from the CLI's own mode list". In the TEST that holds:
  tests/code/run_code_tests.sh:175-184 reads CLI_MODE_TABLE and fails on any
  mode that has no row. But the class of each entry (writes / describe /
  takes) is a hand list in the test (`EP_ROWS`, :137-159). In the PRODUCT,
  the describe class is four separate edits, using two different spellings:
  - `pcrec_emit_ir` (compile.c:3607) and `pcrec_emit_facts`
    (facts_dump.c:199) set `defo.allow_code = pcrec_code_all_langs()` (a
    string);
  - `pcrec_count_groups` (compile.c:3649) and the registry's
    `built_status_probe` (syntax_dump.c:845) OR in
    `pcrec_code_describe_mask()` (a mask).
  No CLI_MODE_TABLE column says "describe", so a new describe-or-review mode
  opens the grant only if its author remembers a fifth site. The test then
  fails, which is good, but the product stays a hand list.
- One behaviour falls out of the string spelling: the describe sites replace
  the grant only when it is NULL. `--allow-code=` (empty) with `--emit-ir`
  passes "" through, which grants nothing, so the describe mode refuses the
  code. CONFIRMED BY TRACE, not by a run (no binary):
  1. `--allow-code=` sets `st.allow_code = a + 13`, which is ""
     (cli/main.c:1567).
  2. `cli_dispatch` resolves "" with no error, because
     `pcrec_code_grant_resolve` skips an empty spec (enabled.c:387).
  3. `opt.allow_code = ""` (cli/main.c:2633).
  4. `pcrec_emit_ir` keeps "" because it is not NULL (compile.c:3607), so the
     grant is 0 and the segment is refused.
  `--count-groups` ORs in the mask unconditionally (compile.c:3649) and
  accepts the same pattern, so under `--allow-code=` two members of one
  describe class disagree.
  Repro once a binary exists: `pcrec --allow-code= --emit-ir --pattern
  'a(?C`c: return RX_PASS;`)b'` should refuse, while the same command with
  `--count-groups` should print 0. An empty grant and no grant should not differ
  on a describe entry.
- Consequence for stage 3: `--list-callouts` (§5.6, the reviews class)
  must parse code without the grant. It will be a fifth hand site, and a
  third spelling unless one is chosen now.
- Severity: maintenance / design. Effort: small. One helper ("open the
  describe grant on this Ctx/options") used at all four sites, or better a
  `class` column on CLI_MODE_TABLE read by the dispatcher and by the test's
  EP_ROWS (the test's classes would then come from the product, so the test
  would need its own oracle for what each class does, which it already has
  in its three behaviour arms). Blast radius: describe modes only.
- GENERAL FORM + UNLOCK: an `entry class` column on the mode table (writes
  | describe | reviews | takes). UNLOCK: §5.9's table becomes a projection
  of `--help`, and stage 3's `--list-callouts` is one row. TRIGGER: stage 3
  (`--list-callouts`).

### SLOT-6: named feature sets are not checked against GRANT (§5.1 (i) "excluded from every named set" holds by list content, not by mechanism)
- CONFIRMED (by reading). `pcrec_enabled_resolve_spec` expands a named set
  through `find_module_bits` (enabled.c:308-314) with no
  `module_invoker_only` test. The explicit-list arm has that test
  (enabled.c:328-331) and `all` has its own. Only `std1 = {classes,
  modifiers}` exists, and it is frozen, so nothing leaks today. A future
  `std2` that listed `code-c` would grant code from any `features` text,
  which is exactly what T1 forbids, and no check would object.
- Severity: trust (it has not fired). Effort: one line (apply the same test
  in the named-set arm, or refuse at table build). Blast radius: the gate.
  TRIGGER: the next named set (D37 version boundary).
### SLOT-7: the macro set's names are hand-written twice in emit_code.c (the define text and the `#undef` list), and a third and fourth time in the test and the spec
- CONFIRMED (by reading). `code_macros` (src/gen/emit_code.c:262-297) has
  `fixed[]`, the eleven names to `#undef`, and separately a literal block
  that `#define`s those eleven names. Two hand lists of one fact, in one
  function. tests/code/run_code_tests.sh:281 (`MSET`) is a third copy, and
  its "ends with the file" regex (:307) is a fourth spelling, as a pattern
  family. The spec table (§11.9¶5) is the contract, so that copy is
  expected. The A8 `#undef` block of artifact-internal macros IS derived
  (`code_undef_live` reads the emitted text, :187-234). That is good, and it
  is the form the macro set's own `#undef` could share.
- Today the lists agree (eleven names each). A macro added to the define
  text and not to `fixed[]` leaks past its segment. Because every segment
  redefines the same text identically, that leak is invisible between
  segments. It shows only if the end-of-file check's regex happens to cover
  the new name (`RX_(SUBJ|LEN|POS|START|CAP|USER|G_)`). An `RX_SPAN_OF` or
  `RX_VARS` would not match it.
- Severity: maintenance. Effort: small: one row table `{name, params,
  body}` that emits both the define and the undef (the RX_CAP_* family
  already shares its guard text six times and would shrink with it). Blast
  radius: emitted text only, but that is an abi event, so do it at the next
  event that already moves callout artifacts (stage 4).

### SLOT-8: the "language by tag" lookup is written three times, beside an existing by-feature accessor; the grant sentence is written four times
- CONFIRMED (by reading). The house guide's shared-abstraction rule:
  - the same loop `while (k < nl && strcmp(L[k].tag, lang)) k++` (or its
    `strlen && strncmp` twin) is in mod_code.c:86-88
    (`pcrec_code_header_check`), enabled.c:400-404
    (`pcrec_code_grant_resolve`) and compile.c:2067-2070 (the
    `code-header` grant check). `pcrec_code_lang_by_feature` exists
    (mod_code.c:101). The missing sibling is `pcrec_code_lang_by_tag(s,
    len)`.
  - compile.c:2071-2076 rebuilds the module name as `'code-%s'` from the
    tag, though the row has a `module` column.
  - the sentence "only the command-line option --allow-code=X (or the
    library's allow_code member) enables" is written in ext.c:592-594,
    compile.c:2072-2076 and registry_check.c:1263 (as an expectation), with
    two more variants: enabled.c:193 `INVOKER_ONLY_MSG` and
    rxt_source.c:879. D26 makes the wording a low tier, so this is not a
    wording complaint. It is one fact (the door) spelled five ways, which is
    SLOT-2's missing column showing up in the diagnostics.
- Severity: maintenance. Effort: small. Blast radius: diagnostics (each
  wording change re-pins tests/code and registry_check expectations).
### SLOT-9: the binding table has no column for "who writes the definition"; the emitter tells the rows apart by kind, and re-derives the function name from a second format string
- CONFIRMED (by reading); severity design, small. The ONE CALL FORM ruling
  (INLINE-C.md, Frank 2026-10-27) says the rows "differ only in WHO WRITES
  THE DEFINITION and its name and linkage". `PcrecCalloutBinding` carries
  `symbol`, `callee`, `user` and `is_extern` (linkage). "Who writes" is
  implied by `!is_extern`, and the definition's NAME is not in the row at
  all:
  - `code_fn` (emit_code.c:133-137) formats `"%s__code%d"` itself, and its
    comment says it is "the binding row's symbol without its `_ref`".
    mod_callouts.c:173 is a second format string, `"%s__code%d_ref"`, for
    the same name;
  - `pcrec_emit_code_protos` (emit_code.c:143), `pcrec_emit_code_block`
    (:421) and the `_CODE_LANGS` stamp (emit_dfa.c:2676) select rows by
    `bind == CO_CODE`, not by a row column.
- The CALL SITE is uniform, which is what the ruling is about. vm_callout
  (emit_vm.c:9005ff.) and the listing read only `bind.callee`/`.symbol`, and
  `src/opt/` has no `CO_CODE` at all. So this is a definition-site
  narrowing, not a second call path.
- Consequence: §6 (artifact-as-callout) stays a user-written binding, so it
  adds no pcrec-written row and does not fire this. The trigger is the first
  OTHER binding whose definition pcrec writes: a stage-6 template segment, or
  the PCRE2 wrapper's helper of §7 if it is emitted. That needs a second
  `bind ==` test at three sites.
- GENERAL FORM: add `writer` (artifact | user) and `defn` (the function
  name, NULL for user rows) to `PcrecCalloutBinding`. Protos, the block and
  `--emit-main` all read the row. TRIGGER: the next pcrec-written binding.

### SLOT-10: the span helpers have ONE source (good), but "published as a header" is met only through each artifact's own `.h`
- SUSPECTED narrowing, a question for the manager. The ruling (INLINE-C.md
  2026-10-26: "emitted into callout-bearing artifacts and published as a
  header from ONE source") has two halves:
  - The one source holds. `span_helpers[]` in src/gen/emit_code.c:35-124 is
    the only implementation. tests/code/span_check.c holds REFERENCE
    implementations written from §11.10's table. That is a test oracle by
    design (its header says so), not a second copy of the product, and it
    is compiled against the artifact's own text (`-include`). The spec
    table is the contract. The guide points at the spec and has no copy.
  - "Published as a header": no standalone header exists. There is no file
    under lib/ and no `--emit-*` mode that writes it. The helpers reach a
    hand-written binding only when the user includes some callout
    artifact's `.h` (match_api §6.3.1¶1 puts them there). A user who writes
    a binding library meant for several patterns gets the helpers from
    whichever artifact header the library happens to include. That works,
    because of the `PCREC_RX_SPAN_H` guard, but it ties the library to an
    artifact.
- If the ruling meant a standalone header, it is narrowed. If it meant
  "the artifact's header", it holds. Ask, do not fix. A standalone form
  would be `pcrec --emit-span-header` printing the same `span_helpers[]`
  (still one source). Its trigger is the first user binding library, or
  stage 6 templates, whose generated code may want the helpers without a
  matcher.

### SLOT-11: the doubled-delimiter decode is copied between the two `(?C` ports
- CONFIRMED (by reading); maintenance, small. mod_callouts.c:250-256 and
  mod_code.c:192-199 hold the same loop (copy a byte; if it is the close
  delimiter, skip the next). Only the code port also records `exact`. The
  shared home is next to `pcrec_callout_extent_scan` in scans.c, which
  already owns the end rule ("one home for the tag shape, read by the
  recogniser and the port" is that file's own stated pattern):
  `pcrec_callout_string_decode(arena, raw, rawlen, close, &exact)`.
  [SCANNER-DOGFOOD]'s `(?{` port will not need it (no delimiters there), so
  two is the final count. Still, the end rule is PCRE2-exact by design
  (§2.3), and two copies of it are two places for it to drift.
### SLOT-12: a FILE target silently drops `code-header` lines past the 256th
- CONFIRMED (by reading); answer-adjacent, low. cli/main.c:2196-2203:
  `PcrecCodeHeader hdrs[256]; ... for (ri = 0; osrc && ri < osrc->nrows &&
  nh < 256; ri++)`. Header line 257 and later are not emitted, and nothing
  says so. The schema row is `REPEAT` with no bound (rxt_schema.def:165),
  and `--code-header` on the CLI grows without limit (realloc), so the two
  sources of the same list have different limits. Effect: a `.rxt` with 257
  `code-header` lines, whose segment calls a function declared only in the
  257th header, compiles under pcrec and fails in the user's gcc with an
  implicit-declaration error that names the segment, not pcrec. Coding
  guide §1.8: a value a file can be measured against is a `limits.def` row
  or has no limit. Here it is a bare array size, invisible to
  limits_check (which scans `#define`s and enum members, not array bounds).
  Fix: allocate per target, as `--code-header` does, or refuse past a
  limits.def row by name. Effort: a few lines. Blast radius: none in the
  corpus.

### SLOT-13: house rules on the cli/main.c hunks (option parsing)
- CONFIRMED (by reading); maintenance, small.
  - The push of one `--code-header` value is written twice
    (cli/main.c:1558-1565 for `--code-header V` and :1569-1575 for
    `--code-header=V`): the same realloc, assign and increment. `libdir_push`
    (:826) is this file's existing shape for exactly this. A
    `code_header_push(st, v)` removes the copy.
  - `if (a[2] == 'a') st->allow_code = ...; else <code-header>`
    (:1556) tells two options apart by their third byte, inside a branch
    entered by two strcmps. The branch is a two-row if-chain that throws
    away its own test result. Split it into two `else if` arms, as the
    `=`-spelling arms just below already are.
  - Each grant is resolved twice: once in `cli_dispatch`, for an early error
    (:2626), and again in `compile_driver` (compile.c:2058). That is
    harmless, since the resolver is pure; listed only so nobody "fixes" one
    of them into a divergent copy.
### SLOT-14: house-rules pass, length-ordered over the four named files (the stopping point is stated)
Functions over about one screen, scored against coding.md §4's five
questions (length is a trigger, not a verdict):
- `pcrec_codeport` (mod_code.c:158, 84 lines). Q1 fails a little. It mixes
  four levels: the scan guard, the decode loop (SLOT-11: extract it), two
  refusal scans written at DIFFERENT altitudes (the bidi rule is a table plus
  a function, `code_invisible`/`code_find_invisible`; the C0-control rule is
  an inline loop at :212-218), and the reached-code test. The two byte rules
  answer one question ("bytes a segment may not carry"). Making them one
  `code_forbidden_byte(text, n, &what, &off)` with the control range as a
  row keeps the port at one level. After those two extracts it is about 50
  lines and passes. Side effects: `code_tag` reads as a scanner but applies
  attributes to the node (through `pcrec_callout_attrs`). Its header says
  so, and the same design is in mod_callouts, so this is held.
- `code_macros` (emit_code.c:262, 66 lines). Q3/Q4: SLOT-7. The `bool set`
  parameter selects two behaviours (define or undef), which the row table
  of SLOT-7 also removes. The `RX_G_` run walk is at the right level.
- `code_segment` (emit_code.c:340, 54 lines). Q1: the first 18 lines compute
  the source position (line, column, whether to pad), and the rest emits.
  Extract `code_src_pos(cx, a, &line, &col, &pad)`. The rule it encodes is
  §3.1's, and it deserves its own name and header. Then the function passes.
- `code_undef_live` (emit_code.c:191, 44 lines). Passes. One purpose (a
  `#define`/`#undef` line reader over the emitted text, deriving A8's list
  rather than keeping one), and data-driven through `code_keep`. Probed: a
  `#undef` at the start of a line inside an emitted comment would mark a
  live macro dead. No emitter writes one today. Held.
- `pcrec_emit_code_block` (30 lines), `pcrec_code_grant_resolve` (enabled.c,
  33 lines), `pcrec_code_header_check`, `module_invoker_only`: under a
  screen, one purpose each. The lookup duplication is SLOT-8.
- compile.c's grant-and-header block inside `compile_driver` (+33 lines,
  compile.c:2052-2084): inline detail in a function that is already the
  pipeline's longest. Extract `code_grant_apply(&defo, emit_in, &feat_mask,
  err)` beside the existing `[UCP]` implied-modules step it sits next to.
- cli/main.c hunks: SLOT-12 and SLOT-13.
- Tables used as if-chains: `pcrec_callout_binding` is a switch with no
  `default` (§1.3 holds). `code_keep` and `code_invisible` are real
  first-match tables. The `a[2] == 'a'` dispatch (SLOT-13) is the one
  if-chain hiding a table.
- Function-local statics (§1.5): `all[]` in `pcrec_code_all_langs` and
  `fixed[]` in `code_macros` are `static const`, immutable. Held.
- Raw allocation (§1.1): none added under src/. The CLI's realloc/strdup are
  the CLI's own, as everywhere in cli/main.c.
- WHERE I STOPPED: every new function in mod_code.c, emit_code.c and
  enabled.c, plus the cli/main.c hunks of the diff (CliState fields, the
  option parse, apply_target, compile_sources, cli_dispatch, main's frees).
  I did NOT house-review the unchanged context of cli/main.c, or
  src/parse/scans.c and rxt_source.c beyond the hunks quoted in SLOT-1,
  SLOT-11 and SLOT-12.

## SIBLING OF A FAMILY

1. **"Which sources may set or grant this" (the authority family).** Before
   this stage it had three members, all named in design §5.1: the
   rxt_source.c by-name chain, the CLI's tail-span containment, and
   `saw_prefix`. This stage adds:
   - (4) the GRANT bit on registry rows: features texts;
   - (5) two more by-name chain entries: `--allow-code`, `--code-header`;
   - (6) the CLI applies-to refusal for `--code-header` with a FILE operand,
     a twin of `--callout`'s;
   - (7) the describe-entry auto-grant, four hand sites (SLOT-5);
   - (8) the harness manifest's entry-only `allow-code` (test-owned, §5.2).
   The question in every case is "may source S enable fact F". (4), (7) and
   (8) are new MECHANISMS. (5) and (6) are new members of old ones. So: no
   fifth OPTION-scope mechanism, but three new grant mechanisms beside it,
   and the filed-row instruction that was meant to collect them (D20) was
   not carried out (SLOT-1).
2. **Declared projection tables** (codelang.def, beside rxt_schema.def,
   kindrow.def and CLI_MODE_TABLE). codelang.def is a good member: it
   generates the registry row, the recogniser, the grant vocabulary, the
   describe grant and the stamp vocabulary. Its two gaps are the FEAT_ bit
   (SLOT-3) and the grant door (SLOT-2).
3. **Derived emitted-name lists** (A8's `code_undef_live`, which reads its
   emitted text, beside stamp_kinds' classified list). The macro set's own
   `#undef` is the member that is still hand-kept (SLOT-7).

## GENERAL FORM + UNLOCKS

- **One AUTHORITY table: (fact) x (source class) -> allowed | refused,
  plus its door.** Facts: each option, each invoker-only module. Source
  classes: invoker CLI, library member, config `pcrec` line, features text,
  local file, reached file, describe entry, harness entry. The by-name
  chain, the tail span, `saw_prefix`, the GRANT bit, the four describe
  sites and the refusal sentences (SLOT-8) all become reads of it.
  UNLOCKS:
  - stage 3's pins are one new source class, "reached and fully pinned ->
    allowed", which replaces the port's pointer test
    (`cx->code_def->file != cx->defs->file->path`, mod_code.c:222). That
    test cannot express T7's every-chain rule anyway: the port sees one
    definition, not the closure's chains;
  - `--list-callouts` is a describe/reviews row;
  - stage 6's template code is a new fact row that reuses every source
    class.
  TRIGGER: stage 3 is the natural point, because it must rewrite the reached
  rule regardless. Cost if deferred past it: stage 3 adds a ninth mechanism
  (the pin verdict) to the family.
- **Module-level grant row** (SLOT-2 and SLOT-4 as one fix). It closes the
  mixed-module leak by construction. TRIGGER: [SCANNER-DOGFOOD]'s second
  `code-c` row.
- **Entry class column on CLI_MODE_TABLE** (SLOT-5). TRIGGER: stage 3.
- **Binding row `writer` and `defn` columns** (SLOT-9). TRIGGER: the next
  binding pcrec writes itself.
- **Macro-set row table** (SLOT-7). TRIGGER: the next abi event that moves
  callout artifacts (stage 4).

## Ruling check (does the code agree), and consequences

- **ONE CALL FORM (2026-10-27): AGREES at every call site.**
  `vm_callout` and the listing read `bind.callee`/`.symbol`. `src/opt/`
  has no CO_CODE test. `--emit-main` now loops on `is_extern`, so a
  code-only pattern gets a driver. Definition-site narrowing: SLOT-9. The
  required single check exists (run_code_tests.sh arm 10: unity, embedded,
  artifact-as-callout, plus a separate-file control that must show an
  indirect call). Two small observations on that check, offered but not
  verified by a run: it counts only `call *` (an indirect TAIL call, `jmp
  *`, would not count, though a binding call is never a tail call in the VM
  today), and it writes `sep_bind.c` without ever compiling it (dead text).
- **R1 (2026-10-27, `(?{` deferred): AGREES.** No `(?{` row, no scanner.
  codelang.def, mod_code.c, registry.c and the design's stage-2 text all
  cite R1. Consequences for [SCANNER-DOGFOOD]: a scanner column in
  codelang.def, a second generated row per language (SLOT-4's uniformity
  risk), and the FEAT_ bit (SLOT-3).
- **Span helpers (2026-10-26): AGREE in part.** One source, `static
  inline`, guarded, in every callout artifact, each helper tested. The
  "published as a header" half is open: SLOT-10.
- **D7 (ownership is rows, generated from the language table): AGREES.**
  One generated row per language, owned by `code-<lang>`, VM_ONLY through
  the row, the recogniser one function per language because a recogniser
  sees only its tail (registry.c:394-407), the port producing the same
  A_CALLOUT. `--list-syntax` reads the row (`invoker-only` added to the
  flag names, syntax_dump.c:57).
- **§5.1 GRANT: NARROWED** to a per-row bit with an absent uniformity
  check (SLOT-4), named generally but read as code (SLOT-2), and not
  applied to named sets (SLOT-6). `all` and explicit lists hold.
  `PCREC_FEATURE_SET`/`_MODULES` do not move (the grant joins the mask
  only, compile.c:2052-2058). That matches §5.1's disclosure rule.
- **D20 (SCOPE row filed): NOT DONE** (SLOT-1).
- **§5.9 entry table "derived from the mode list": derived in the test's
  completeness check, hand-kept in the product** (SLOT-5).
- **§3.2/A8 macro set and undef list:** the A8 block is DERIVED from the
  emitted text (good); the macro set's own undef is hand-kept (SLOT-7).
- **`_CODE_LANGS` vs the stamp-kinds table: AGREES.** It has a row
  (stamp_kinds.c:62, SK_PATTERN), it is in the spec's kind table
  (match_api.md, the "pattern" row) and its §6.3 inventory row, it is in
  the `.h` per §6.3.1¶1, its vocabulary comes from the language table in
  table order, and it is absent on artifacts with no code.
- **D26: AGREES.** The malformed-`(?C` row is untouched. The refusal for an
  ungranted tagged string names the module and the door. Wording variants
  (SLOT-8) are D26's low tier; the duplication is the house-rule point.
- **D38: AGREES.** Rows 2/3 are the binding unit verbatim
  (`extern const rx_callout_ref rx_callout_<name>`). Row 1 is file-local,
  `{ fn, NULL }`, `user` NULL, and its name `<prefix>__code<seg>_ref` is
  inside namespace row 1.
- **D76/D94 abi 89 -> 90: AGREES by grep.** Readers that cite the number
  were found and moved: `PCREC_ARTIFACT_ABI`, the shared block's
  `PCREC_RX_ABI_H` guard and #error text, match_api §6 (two sentences),
  run_codegen_tests' `ABI_EXPECT`, the recursion-identity FILEPIN (lane
  self-pin, with the manager re-pin noted) and S693's BEFORE/AFTER. The
  remaining 89s are history (abi_changelog), the plan status line, S693's
  deliberate AFTER and an unrelated optloop normaliser. The D94 addendum's
  readers that never cite the number (registry, codegen, rxtsource) moved
  their own counts in the diff: registry_check's 143->144 rows and the
  ports, VM_ONLY and family counts; the rxtsource hunks. That they PASS is
  a run I could not do (no make, no binary).

### Consequences by later stage (collected)
- **Stage 3 (pins, `--list-callouts`):** the reached-code rule lives in the
  port as a pointer comparison against the one definition being bound
  (mod_code.c:222-226). T7's order-independent "every chain pinned" needs
  the closure's chains, so stage 3 moves this rule, it cannot extend it.
  `--list-callouts` is the fifth describe-grant site (SLOT-5). The authority
  table is the natural build point (General form).
- **Stage 4 (`verify`):** the macro set reads `RX_START` as
  `ctx->caps[0][0]`. The FINISH-hand view source of §1.2 supplies `{s,
  UNSET}`, so the macros need no change. Stage 4's abi event is the place to
  table the macro set (SLOT-7).
- **Stage 6 (templates):** the language table has no column for where code
  may appear (pattern or template). The door (SLOT-2), the writer column
  (SLOT-9) and the span header (SLOT-10) all come up there.
- **[SCANNER-DOGFOOD]:** a second row per language (SLOT-4), the scanner
  column and the FEAT_ bit (SLOT-3). The tag scan
  (`pcrec_code_tag_extent_scan`) is shared and ready for it. `(?{`'s
  optional tag needs a recogniser that accepts the NO-tag form for `c` only,
  which is a per-language "default" column (§2.2: "no tag is C, by
  grammar").

## PROBED-AND-HELD

- ONE CALL FORM at the call site: grepped CO_CODE / is_extern over src/ and
  cli/ (12 hits). None is in vm_callout, the listing or src/opt/. Held.
- Language-table projection: all 5 consumers of codelang.def (mod_code.c
  twice, registry.c twice, and the grant vocabulary through
  `pcrec_code_langs`) read the same X-macro. The registry row's module,
  feature and syntax come from the row. Held (except SLOT-3).
- `_CODE_LANGS` against stamp_kinds.c, the match_api kind table, the §6.3
  inventory and §6.3.1¶1 placement: 4 of 4 sites agree. Held.
- The A8 `#undef` block: derived from the emitted text. Its keep list
  (`code_keep`, 6 rows) was checked against every `#define PCREC_` that
  src/gen emits (about 40 names: all are public contract or guards). Held.
- abi readers: grep for 89 next to abi/ABI/ABI_H/ABI_EXPECT over the tree
  (excluding lanes, reviews, history). 9 hits, all deliberate. Held.
- Reached-code test (mod_code.c:222): `d->file = s->path` (rxt_source.c:4394)
  and `defs->file = src` (:4503), so a root-file definition compares
  pointer-equal and a lib definition does not. `include` fragments are
  never compiled by the FILE path (targets name only the file's own
  blocks, rxt_source.c:4569-4575), so code cannot enter through a fragment
  there. Held for stage 2.
- Per-attempt reset: `Ctx` is memset per compile attempt (compile.c:2231),
  so `ncodesegs` restarts at 1. Held.
- The span-helper oracle: span_check.c builds against the artifact's own
  text through `-include`, with references from the §11.10 table. One
  product source. Held.
- The `pcrec` line: `--allow-code`/`--code-header` are refused by the
  by-name chain at parse AND by the tail span at apply. The chain is the
  spot D20 named, and the double cover is harmless. Held (SLOT-1 is about
  the missing row, not a hole).
- `module_invoker_only` scans the whole registry once per listed name: a
  cost on `features` parsing only, not per compile byte. Held.
- NOT RUN: the built compiler was absent for the whole review
  (worktrees/crit-ic2/build/ and base-src/build/ missing; build.log shows
  the build yielding to queue jobs 621/622). Every finding is by reading.
  The one item that needs a run is the empty-grant describe behaviour in
  SLOT-5 (traced, not run).
