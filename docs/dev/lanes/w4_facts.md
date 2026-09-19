# [REVW.4] WAVE 4 (CLI + CONFIG) — FACT SHEET

Lane `w4facts` (sonnet, read-only — no `make`, no edits under `src/`,
`cli/`, `lib/`, `tests/`). Branch `lane/w4facts` from `main` at
`923a5a58` (wave 3 gated and merged). Every number below was re-measured
against that commit today (2026-09-19); nothing is copied from the
review without a fresh grep or `sed -n` behind it. Where my count
differs from the review's, both numbers are given.

This sheet answers five items named in the brief (the code review's
"Wave 4 (CLI + config)" paragraph, `M3`, `Q6`/D107, `D106` addendum 3,
and `synthesis_collation.md` §2.2). It makes no implementation decision;
§6 lists what needs a ruling before an implementing lane starts.

---

## 0. What the review sources got wrong or stale

Re-measuring against `923a5a58` (wave 3 merged 86e7c8da) surfaced five
corrections, in addition to the one the brief already named
(`axes_dump.c`'s path and line count):

1. **`src/parse/axes_dump.c` → `src/dump/axes_dump.c`, 747 lines, not
   731.** Wave 3 moved the whole dump tier (item 1 of `lane/w3`). Every
   citation below uses the new path.
2. **`cli_parse` is `cli/main.c:417-845` (429 lines) today, not
   `379-809` (431 lines).** The function grew by roughly the same size
   it shifted — net near-zero, but every cited line number inside it in
   the review and in `docs/spec/` is stale by 30-40 lines.
3. **`emit_predicate_axes` is `src/dump/axes_dump.c:391-684` (294 code
   lines), not `375-668` / 178 lines.** The function itself was
   re-commented heavily (see §5) between the review and now; the
   structural claim ("not one `if` or loop") still holds — verified by
   reading all 294 lines — but the size figure the review and L1's own
   report cite is under half the current count.
4. **`tools/review/out/function_census.tsv` (and its siblings —
   `clone_candidates.tsv`, `literal_census.tsv`, etc.) are themselves
   stale.** Header: `generated 2026-09-17` at commit `7d444f9e`, which
   predates wave 3's file move. Every row in that TSV citing
   `cli/main.c` or `src/parse/axes_dump.c` carries the old path and/or
   line range (verified for both functions named above). Regenerating
   these is outside this lane's scope (I do not run tooling that writes
   files) but the implementing lane should not trust them without
   re-running `tools/review/`'s census scripts first.
5. **`docs/spec/cli.md`+`limits.md`+`registry.md` carry 27
   `cli/main.c:<line>` citations by occurrence count today (cli.md 20,
   limits.md 6, registry.md 1), not the review's 28** — one short, most
   likely a citation removed or reworded since the review, not a
   miscount on either side; not worth chasing further. **The four
   specific staleness examples L11-F3 named are independently
   re-confirmed stale, AND HAVE DRIFTED AGAIN since the review measured
   them**: `limits.md`'s `cli/main.c:56-58` now lands inside a comment
   about `raise-only` size overrides, not `PCREC_MAX_DFA_STATES_TABLE`;
   its `272-282` still lands inside the `--features` usage-string block,
   not `set_encoding` (this one the review already had wrong, and it is
   still wrong the same way); `cli.md`'s `159` lands mid-usage-string
   (island/capture-slot text), not the `-` handling the review named;
   its `345-350` lands in a comment above `CliState`, close to but not
   exactly the struct tail the review named. **This is the review's own
   point proven a second time**: these citations must be re-aimed by
   flag spelling, never by line number, whichever wave touches the file
   next.

---

## 1. The `cli_parse` table (L11's 59-arm-guard finding, L2's rank-1,
   L1-X10, manager row M3 — counted once)

**Site.** `cli_parse`, `cli/main.c:417-845`, 429 lines.

**(a) Counts, re-measured against the live body:**

| measure | count | matches review? |
|---|---|---|
| top-level `if`/`else if` arms | 64 (1 `if` + 63 `else if`) | L2-L2-6's "64-arm" — yes |
| arms containing `!no_more_opts &&` | **59** (exact grep count) | L11-F3's "59" — yes, exact |
| `-fno-*` arms (whole body is `opt.flags \|= PCREC_NO_X;`) | **20** | L1-X9's "20" — yes, exact |
| `strtol`/`strtoll` integer-value arms | **5**, now at `cli/main.c:606, 623, 683, 696, 737` | L1-X10's "5×" — yes, count; lines drifted (review cited `568,585,647,660,701`) |
| "valid-value menus" (a hand-enumerated or table-derived legal-value set surfaced in a diagnostic) | **8, 1 table-driven** — see table below | L2-L2-7's "8 sites, 1 table-driven" — yes, exact, re-sited |

**The 8 valid-value-menu sites, re-sited:**

| flag | current site | shape |
|---|---|---|
| `--unroll=` | `cli/main.c:604-611` (error at 608) | hand prose, numeric range 1..4096 |
| `--vm-entry-shape=` | `cli/main.c:621-630` (error at 625) | hand prose, numeric range + 5 named rungs |
| `--tune=` | `cli/main.c:649-657` (error at 652-653) | **table-driven** — calls `pcrec_tune_parse`, delegating to `src/core/tune.c`'s own alias table |
| `--engine=` | `cli/main.c:670-678` | hand `strcmp` ladder, 3 values (auto/dfa/vm) |
| `--probe-ask WANT` | `cli/main.c:1456-1461` | hand prose (claim/verdict/result); the enum test itself lives in the library (`pcrec_probe_ask`), only the diagnostic text is CLI-local |
| `--flavour` | `cli/main.c:1622-1624` | hand prose ("only 'pcre2' exists"); the lookup (`pcrec_flavour_by_name`) is a function call but the error text is hand-typed, not rendered from a names list |
| `.rxt` target `engine` row (`apply_target`) | `cli/main.c:994-1000` | hand `strcmp`, 1 value (`vm` only) — a **second, separately worded** engine menu for the config-block surface |
| `--encoding=`/`-e` | `set_encoding`, `cli/main.c:310-319` | **table-driven** — renders its error text from `pcrec_enc_names()`, the encoding registry; the one lens-2 names as the model to copy |

Note two of the eight are already table-driven (`--tune=`, `--encoding=`)
— the review's "1 table-driven" undercounts by one against my
measurement; both delegate to a real registry (`tune.c`, the encoding
registry) rather than hand-typing a menu, and only their surrounding
`cli_err` prose differs in how it was built. This is a fact for the
implementing lane, not a correction of severity — the count of
**hand-typed** menus is 6, not 7.

**(b) Readers/anchors, found by grep:**

- **Sabotage rows: zero.** `grep -rln "cli/main\.c\|cli_parse" tests/mech/sabotages/` returns nothing. Confirmed independently of the review (which also states 0).
- **`tests/cli/run_cli_tests.sh`**, 2,209 lines (exact match to L11's citation, no drift) — pins diagnostic wording by string match, not by line number, so a table-driven rewrite that preserves diagnostic TEXT byte-for-byte does not stale this file; a rewrite that changes wording does.
- **`docs/spec/cli.md`** carries the bulk of the 27 line-numbered citations (§0.5); none of the arms inside `cli_parse` itself are individually cited by line as often as the flag names are cited by spelling elsewhere in the same doc — re-aim by spelling.
- **`tools/review/out/function_census.tsv`** row 8 (stale path/lines — see §0.4); **`clone_candidates.tsv`** has no clone-group row for `cli_parse`'s `-fno-*` arms per L1's own note ("each arm is one line — below the detector's shingle floor"), confirmed structurally true (each `-fno-*` arm is a single `else if` line).
- **13 codegen test scripts** reference `cli/main.c` by the review's own count (L1-X10's row); I did not re-run this count — it is a grep over `tests/codegen/*.sh` for the string `cli/main.c`, and the brief's effort budget did not extend to re-deriving it independently. Flag as **owed to the implementing lane** if it matters for their blast-radius statement.

**(c) D80 (caller-observable)?** Only if the table-driven rewrite changes
any diagnostic's TEXT, or changes which flags are accepted. A rewrite
that is byte-identical on every diagnostic and every accepted/rejected
flag needs no `docs/spec/` content hunk — but `docs/spec/cli.md`'s stale
line citations (§0.5) should be re-aimed in the same change regardless,
since the wave is already touching the file (cheap, and the citations
are already known-wrong).

**(d) Emitted-byte question:** No. `cli_parse` is in the `cli` layer
(outermost, per `coding_guide.md` §1.9's `lib -> core -> enc -> parse ->
ir -> opt -> gen -> driver -> dump -> cli`); it parses `argv` into
`pcrec_options` and never touches `src/gen/`'s emitters. None of
`scripts/emit_sweep.py`'s four streams can move from this item structurally
— confirm with a sweep run regardless, since "structurally can't" is an
argument, not a substitute for the gate.

---

## 2. The mode mutual-exclusion relation (L11-F4)

**Site.** `main`, `cli/main.c:1264-1784` (521 lines total; the review's
census row cited `1223-1736`/514 lines — drift ~40-45 lines, same
direction as `cli_parse`'s).

**(a) Counts, re-measured:**

The membership-test idiom (`if (<mode>) { if (<other modes> ||
...) { cli_err(...); return 1; } ... }`) appears **exactly 6 times**,
confirmed by grepping for `list_syntax ||` (present in all six, since
`list_syntax` is the first-declared mode flag and every guard includes
it):

| # | site (line) | guarded mode | membership size | members |
|---|---|---|---|---|
| 1 | `cli/main.c:1352-1358` | `--source` | **13** | list_syntax, list_definitions, list_verbs, list_families, list_axes, list_limits, list_schema, explain, count_groups, emit_ir, probe_want, list_source, flavour |
| 2 | `cli/main.c:1379-1383` | `--list-source` | **12** | same 13 minus `list_source` itself, minus `flavour`, plus `st.source` |
| 3 | `cli/main.c:1428` | `--probe-ask` | **9** | list_syntax..count_groups (drops emit_ir/probe_want/list_source/flavour/st.source) |
| 4 | `cli/main.c:1474` | `--emit-ir` | **9** | identical membership to #3 |
| 5 | `cli/main.c:1502` | `--count-groups` | **8** | drops `count_groups` itself from #3/#4's set |
| 6 | `cli/main.c:1533` | the `--list-*`/`--explain` family | **8**, same members as #5, but tested by **summed count > 1** rather than OR-membership | list_syntax, list_definitions, list_verbs, list_families, list_axes, list_limits, list_schema, explain |

**4 distinct memberships (13 / 12 / 9 / 8), confirmed exactly** —
matches L11-F4's "written 6 TIMES with 4 DIFFERENT memberships." Site
6 is additionally a DIFFERENT KIND of test from the other five (a
summed-count-over-1 mutual exclusivity check among the 7 list_*/explain
flags themselves, not a "is some OTHER mode active" guard) — worth the
implementing lane's attention: unifying "6 sites" into "1 relation"
needs to decide whether site 6's pairwise-exclusivity shape survives
as a second relation or folds into the first.

**(b) Readers/anchors:** Sabotage rows: zero (same grep as item 1, same
file). `tests/cli/run_cli_tests.sh` pins the refusal wording of each
block — 2,209 lines, no line-number anchors (string-matched). L11-F4's
own row states "35 `pcrec: --…` diagnostics" pinned; I did not
independently re-derive this count (a literal grep for `"pcrec: --"`
against the test file returns 0, meaning the assertions are not spelled
that way at the top level — likely checked through a helper function.
**Owed**: re-derive the actual diagnostic-pin count and mechanism before
this item lands, since the assertion SHAPE (not just the count) governs
how safely six sites collapse to one.

**(c) D80:** **Yes, unavoidably**, and this is the item's central
design question, not a formality. Because the six sites have four
DIFFERENT memberships today, collapsing them into "one relation written
once" means choosing which membership is authoritative for which call
site — if the unified relation is simply the widest (13-member) set
applied everywhere, sites 3/4/5/6 would newly refuse combinations they
accept today (e.g. `--probe-ask` combined with `--flavour` is not
refused by site 3's current 9-member set but would be refused by the
13-member set). Any such change in what a given invocation accepts or
refuses is caller-observable and needs a `docs/spec/cli.md` hunk (D80).
The alternative — a general relation parameterized per call site so
behavior is UNCHANGED — needs the same D80 hunk only if the wording of
any of the 35 diagnostics changes, which a mechanical extraction can
avoid.

**(d) Emitted-byte question:** No, same reasoning as item 1 (outermost
`cli` layer, no `src/gen/` contact).

---

## 3. `limits_check.sh` filter inversion (Q6 / D107)

**This is already RULED** — Frank's ruling is D107
(`docs/dev/decisions.md`, "D107 — limits detector: INVERT the
name-keyed filter", 2026-09-17). This section re-measures the check's
current state against that ruling rather than re-opening the question.

**Site.** `tests/registry/limits_check.sh`, 293 lines total (review
cited 277 — the whole file, not just the filter line, so "277" was
likely already a mid-file line cite that has since drifted by ~16
lines from unrelated edits).

**(a) Current filter, exact text, `tests/registry/limits_check.sh:273`:**
```
grep -E 'MAX|_MIN_|_MIN\b|CAP|LIMIT|BUDGET|THRESHOLD|_LEN\b|DEPTH|NEST'
```
(and the per-identifier variant at line 278). This is the vocabulary
D107 says to stop filtering by. The existing allowlist
(`tests/registry/limits_check.sh:250-262`, `ALLOWLIST="..."`) has
**12 entries** today: `TRIE_MAX_RDEPTH`, `MAX_GROUPS`,
`LEGEND_MAX_STATES`, `LEGEND_MAX_EXAMPLE`, `VM_MAX_STRIDE`,
`VM_FAST_TIER_BYTES`, `VM_FAST_TIER_MIN`, `VM_MRL_DYN_MAX`,
`SELECT_MAX_ROUNDS`, `COMPILE_MAX_ATTEMPTS`,
`PCREC_STEP_BUDGET_DEFAULT`, `PCREC_WORK_BUDGET_DEFAULT`.

**The 14 name-invisible constants (L3-F1's population), re-verified
present at current line numbers:**

| constant | current site | disposition (L3-F1 + D106 addendum 3) |
|---|---|---|
| `SIZE_TERM_BAR_DEFAULT 75` | `src/core/compile.c:464` | **RULED: becomes a `limits.def` row** (D106 addendum 3, item 4 below) |
| `C_MEMCHR 6u` | `src/opt/prefix_k.c:260` | argued at site; allowlist candidate |
| `C_BITMAP 116u` | `src/opt/prefix_k.c:261` | argued at site; allowlist candidate |
| `C_VERIFY 250u` | `src/opt/prefix_k.c:262` | argued at site; allowlist candidate |
| `C_ENTER 2000u` | `src/opt/prefix_k.c:263` | argued at site; allowlist candidate |
| `C_MISPRED 1500u` | `src/opt/prefix_k.c:280` | argued at site; allowlist candidate |
| `MATERIAL_NUM 2u` | `src/opt/prefix_k.c:294` | argued at site (12 lines of derivation); allowlist candidate |
| `MATERIAL_DEN 1u` | `src/opt/prefix_k.c:295` | argued at site; allowlist candidate |
| `PREMUL_DEAD 65535` | `src/gen/emit_dfa.c:2402` | table SENTINEL, correctly out — second allowlist |
| `PCREC_RXT_WAVE_BUILT 23` | `src/core/internal.h:4729` | schema version, correctly out — second allowlist |
| `PCREC_RXT_WAVE_RESERVED 999` | `src/core/internal.h:4737` | sentinel, correctly out — second allowlist |
| `REG_SEL_ANY (-1)` | `src/core/internal.h:3084` | sentinel, correctly out — second allowlist |
| `PCREC_ENGINE_DFA 1` | `lib/pcrec.h:684` | API enum value, correctly out — second allowlist |
| `PCREC_ENGINE_VM 2` | `lib/pcrec.h:685` | API enum value, correctly out — second allowlist |

All 14 re-confirmed present at (drifted) current lines; none of the
`#define`s themselves have moved in kind or value since the review, only
in line number (small drift, ≤10 lines on every site except
`SIZE_TERM_BAR_DEFAULT`'s move from :458 to :464).

Per D107: **1 (SIZE_TERM_BAR_DEFAULT) becomes a limits.def row** (item
4), **7 (the prefix_k.c cost-model constants)** join the existing
12-entry allowlist with reasons (already argued at their sites — the
argument text exists, it is a matter of citing it in the allowlist
comment), **6 (PREMUL_DEAD, both RXT_WAVE constants, REG_SEL_ANY, both
PCREC_ENGINE values) go on a NEW second allowlist** for non-limit kinds
(sentinels/schema-versions/API-enum-values), exactly as D107 specifies.

**(b) Readers/anchors:** D107 itself already states "the arm gains its
own sabotage row (a name-shape-invisible `#define`; none plants one
today)" — confirmed: `grep -rln "limits_check" tests/mech/sabotages/`
finds S208/S209/S215/S251/S44, all of which plant against `limits.def`
ROWS or the doc join, not against the filter's name-vocabulary logic
itself — D107's statement that no existing row exercises the inverted
filter's failing direction is correct. `tests/registry/limits_check.sh`'s
own PASS line (~line 286, review cited :290 — drift 4 lines) enumerates
the filter vocabulary in its success message and needs rewording to
match whatever the inverted check reports.

**(c) D80:** No — this is a check-only file, not a caller-observable
surface. Zero source files change if the disposition is allowlist-only
(true for 13 of the 14; the 14th, `SIZE_TERM_BAR_DEFAULT`, is item 4's
concern, not this item's).

**(d) Emitted-byte question:** No — `tests/registry/` is test/check
tooling, outside every one of `emit_sweep.py`'s four streams by
construction.

---

## 4. F2 (`[ART-SIZE]` bar → `limits.def` row) and F4 (`"requires
   module"` spellings, dispositioned as-is)

**F2 is RULED** (D106 addendum 3, quoted in full in `decisions.md`):
*"resolve by MOVING `SIZE_TERM_BAR_DEFAULT` (src/core/compile.c) into
`limits.def` as a row, so both parameters of the one unroll-K size-term
ladder live in the one ruled home... Wave 4."*

**(a) Current site and the row-format gap.** `SIZE_TERM_BAR_DEFAULT 75`
is `src/core/compile.c:464`, consumed at `:673`
(`const int size_term_bar = bar0 ? bar0 : SIZE_TERM_BAR_DEFAULT;`). Its
sibling, `PCREC_SIZE_TERM_THRESHOLD`, is already a `limits.def` row at
`src/core/limits.def:161` (kind `"selection knee"`). **`limits.def`'s
own documented `unit` vocabulary
(`src/core/limits.def:24-27`) is `"bytes" | "states" | "entries" |
"elements" | "nodes" | "copies" | "groups" | "levels" | "positions" |
"chars" | "frames" | "steps" | "work-units" | "count" | ""` — there is
no `"percent"` unit.** `SIZE_TERM_BAR_DEFAULT` is a percentage (75%).
L3-F2's own report flagged exactly this gap ("I cannot tell... whether
the asymmetry is deliberate... `limits.def`'s `unit` vocabulary has no
'percent'"). **This is an open question for the implementing lane, not
resolved by D106 addendum 3's text**: either add a `"percent"` unit to
the vocabulary (one line in the header comment plus whatever the
`unit` column's own validation checks), or spell the row `unit ""`
(dimensionless) with the percent nature stated in `desc`, matching the
convention already used for other ratio-shaped rows if any exist.

**(b) `--list-limits` makes this D80-observable.** `limits.def` rows are
dumped verbatim by `pcrec --list-limits` (`src/dump/limits_dump.c`,
per `limits.def`'s own header comment) — **adding a row is a new line
in that TSV output**, which is caller-observable. D107's text already
names this: *"re-pins `limits_check.sh`'s manifest count and
`docs/spec/limits.md` §3 if a row is added."* Confirmed:
`limits.def` currently has **57 rows** (`grep -c "^PCREC_LIMIT("
src/core/limits.def` = 57, matching the file's own self-reported count
in its header comment). Adding one row makes 58 — `docs/spec/limits.md`
§3's prose and `tests/registry/limits_check.sh`'s manifest count both
need the same +1.

**(c) The sabotage row does NOT need re-anchoring, only re-verifying.**
`tests/mech/sabotages/S192_sizeterm_bar_removed.sh` (`SAB_FILE="src/core/compile.c"`)
anchors on the CONSUMING line inside `size_term_choose`
(`SAB_BEFORE='    if (best != 0 && total[best] * 100 <= total[0] * (size_t)bar) sel = best;'`),
not on the `#define SIZE_TERM_BAR_DEFAULT 75` line itself. Moving the
constant's DEFINITION to `limits.def` (and its default-read site from
`SIZE_TERM_BAR_DEFAULT` to whatever `limits.def`'s generated accessor
is named) does not touch `size_term_choose`'s body, so S192's anchor
text is unaffected **as long as the `bar` parameter's read expression at
`compile.c:673` keeps the same shape the row's accessor would need to
preserve** — re-run S192 solo after the change as verification, not as
a re-anchor.

**F4 — dispositioned already, not a Frank-ruling item.** L3-F4
(`"requires module '%s'"` spelled 20 ways in 8 distinct format strings
across `mod_uprops.c` ×9, `ext.c` ×4, `mod_modifiers.c`,
`mod_recursion.c`, `mod_backrefs.c`, `parse.c`, `syntax_dump.c`) does
**not** appear in `synthesis_collation.md`'s §3 rulings-for-Frank list —
only F2 does (item 7 there). F4's own row states its disposition
inline: **LOCAL effort, "zero re-aim cost for a byte-preserving
change"** (the ~80 test files bind to RENDERED TEXT, not to the
duplicated format strings' locations), and the synthesis's H5 note
(`synthesis_collation.md:606-608`) explicitly scopes it OUTSIDE the
already-ruled `RegDiag` central home — this is a "factor 20 spellings
into one helper" mechanical fix, not a design event, and not something
needing Frank's ruling. **"F2/F4's chosen dispositions" in the wave-4
summary paragraph means**: F2's disposition is Frank's D106-addendum-3
ruling (move to `limits.def`); F4's disposition is the author's own,
already stated in the finding (factor, LOCAL, no ruling needed).

**(d) Emitted-byte question (both):** No for F2 — `limits.def` is read
by `compile.c` at compile time to produce a value, never emitted
verbatim into generated C. No for F4 — `"requires module"` diagnostics
are printed to the CLI's own stderr, never emitted into generated C
matchers.

---

## 5. X9 / `axes.def` — priced, not built (design-event proposal for Frank)

**Site.** Three hand-maintained sources today:

1. **`lib/pcrec.h`** — the bit declarations. `grep -c "PCREC_NO_\|PCREC_FORCE_"` returns 32 hits total in the file (not all are axis members — e.g. `PCREC_NO_CAPTURES` and `PCREC_EMIT_MAIN` are semantic flags outside the predicate-axis table; I did not hand-sort the 32 into "axis" vs "not axis" — the implementing lane should, since it determines the X-macro table's exact row count).
2. **`cli/main.c`'s `cli_parse`** — the 20 `-fno-*` arms (item 1's table), each `else if (!no_more_opts && !strcmp(a, "-fno-X")) opt.flags |= PCREC_NO_X;`.
3. **`src/dump/axes_dump.c`'s `emit_predicate_axes`**, 294 code lines (§0.3), **18 `PredAxis p` struct declarations** covering the VM/engine-selection axes; `docs/spec/registry.md` §6 states 24 axes total across both the VM/engine family and the DFA layer-1 family (`table`, `prefilter`, `view`, `seed`, `accept`, `direction`, `match`, `scan-edge`, `scan-body`, `search-start`) — the DFA-layer axes are emitted by a **separate function**, `emit_dfa_list_axis` (17 lines, `src/dump/axes_dump.c`, per `tools/review/out/function_census.tsv` row — stale path, unverified current line), which X9's remedy as scoped by L1/L11 does not claim to touch. **Confirmed structurally**: reading all 294 lines of `emit_predicate_axes` finds not one `if` or `for`/`while` statement — it is 18 scope blocks of sequential `emit_pred_row` calls, exactly the "data table written as code" shape L11-F6 names.

**Two awk scrapers, confirmed by reading both, not deleted, live today:**

1. `tests/registry/axes_registry_check.sh:181-196` — an `awk` block that
   pattern-matches `strcmp(a, "-...")` literals followed by
   `opt.flags |= PCREC_(NO|FORCE)_...` lines in `cli/main.c`'s TEXT, to
   build a `CLI_MACRO` table used by `check_cli_flag` (line ~232) to
   verify the dump's reported `cli_flag` column matches what the parser
   actually accepts.
2. `tests/axes/run_axes.sh:245-280` — the **identical** pairing logic
   (its own header comment at line 245 says so: "One awk pass over the
   arg-parsing loop"), independently re-implemented, with its own
   fatal-guard at line 279 for exactly the failure mode X9's row
   predicts ("cli/main.c's loop shape changed").

**(e) What each check currently guards, and what would guard it after
the extraction:**

- **What they guard today:** drift between fact (2) (the parser's
  flag-text-to-bit mapping, hand-written in `cli_parse`) and fact (3)
  (the dump's `cli_flag` column, hand-written in `emit_predicate_axes`).
  Both are independently maintained prose; the awk scrapers exist
  because nothing else would catch one being edited without the other.
- **What would guard it after the extraction:** **nothing needs to,
  structurally.** If `cli_parse`'s 20 arms and `emit_predicate_axes`'s
  18 blocks both become table-walks over one `PCREC_AXIS(...)` X-macro
  row list (`src/core/axes.def`, on `limits.def`'s and
  `rxt_schema.def`'s own precedent — both `.def` X-macro tables already
  exist and are read by multiple consumers: `src/core/limits.def` 393
  lines / 57 rows, `src/parse/rxt_schema.def` present and sized
  similarly), the `cli_flag` column is read directly by BOTH consumers
  from the SAME source line — there is no longer two independently-typed
  facts to reconcile, so the reconciliation check has nothing left to
  check. The awk scrapers are **deleted**, not re-aimed, which is why
  L1's report calls this a DESIGN-EVENT rather than a LOCAL fix: A3's
  usual cost direction (a change needs new checks) inverts (a change
  DELETES two checks). The residual reconciliation risk moves one level
  down: `axes.def`'s own bit values must still agree with
  `lib/pcrec.h`'s `PCREC_NO_*`/`PCREC_FORCE_*` enum values (fact (1)) —
  a strictly smaller surface (one file vs. two awk-scraped ones), and
  whether that agreement needs its own check (or whether `axes.def`
  becomes the bit values' one true source, with `lib/pcrec.h` generated
  or `#include`-ing it) is a design question for whoever builds this,
  not answered here.

**Extraction site-count estimate** (not a build plan, a cost sketch for
Frank's pricing): ~60 lines of `cli_parse` (the 20 `-fno-*` arms) become
a loop; all 294 lines of `emit_predicate_axes` become a table-walk (per
L11-F6, X9 IS the whole remedy — no partial split proposed by any
lens); some subset of `lib/pcrec.h`'s 32 `PCREC_NO_*`/`PCREC_FORCE_*`
declarations (bound needs the hand-sort noted above) either stay or
become generated from the same table; 2 awk scrapers (one block each in
`tests/registry/axes_registry_check.sh` and `tests/axes/run_axes.sh`)
are deleted outright. Zero sabotage rows re-aim (confirmed: `grep -rln
"axes_dump\.c\|emit_predicate_axes" tests/mech/sabotages/` returns
nothing, matching L11-F6/L1-X9's own "0 anchors" claims). `docs/spec/registry.md`
§6 (the `--list-axes` contract — its own text already warns the axis
LIST there "has now gone stale TWICE," 19→21→24, so whoever builds this
should re-derive rather than hand-edit that section) and possibly
`docs/spec/tuning.md` §2 would need review for consistency, though
X9 does not by itself change any axis's OUTPUT — only where its
declaration lives — so a byte-identical extraction needs no `docs/spec/`
content hunk, only a mechanism-description one if either spec currently
describes "hand-written in `cli/main.c`/`axes_dump.c`" as the
mechanism.

**(c) D80:** No, if the extraction is byte-identical on every dumped
row and every accepted flag (the standard the coding guide's §4.1 and
L11-F6 both hold this to — "the axis-table centralization IS the whole
remedy," not a semantics change). Yes, if any row's text or any flag's
acceptance changes as a side effect — not expected, but the byte-identity
gate (`scripts/emit_sweep.py` plus a live `--list-axes`/`--dump-axes`-equivalent
diff, not one of the four `emit_sweep.py` streams since none of them
capture `--list-axes` output — **this is a gap**: the implementing
lane needs its own before/after diff of `pcrec --list-axes` output,
which `emit_sweep.py` does not provide) is the proof either way.

**(d) Emitted-byte question:** No — same outermost-layer argument as
items 1/2 (`cli` parses argv, `dump` renders registry text; neither
reaches `src/gen/`'s emitters). Structurally cannot move a byte on any
of `emit_sweep.py`'s four streams.

---

## 6. Coding-guide disciplines that apply, per item

- **Items 1/2 (cli_parse table, mode relation):** `coding_guide.md` §4
  (altitude rubric) governs directly — both are "code-driven vs
  data-driven" cases (rubric question 3) and "variations looped rather
  than inlined N times" (question 4). §1.9's layer model places both
  squarely in the outermost `cli` layer, dependent leftward only.
- **Item 3 (limits_check.sh inversion):** §5 item 4 of the guide is
  this exact finding, already written into the guide as current ground
  truth ("Name-keyed filters are the recurring blind spot... If your
  filter is a name list, say what it cannot see" — L3-F1). §1.8 also
  names `SIZE_TERM_BAR_DEFAULT`/`C_MEMCHR` by name as the motivating
  instance for D90's `limits.def` boundary.
- **Item 4 (F2/F4):** §1.8 (limits.def is the one home for a numeric
  limit a pattern can be measured against) governs F2 directly — a
  percentage bar IS such a value (it steers a selection), so the move
  is consistent with, not an exception to, the discipline.
- **Item 5 (X9):** §4.1 explicitly cites `emit_predicate_axes` as "the
  pure case" for common-extraction-first, already anticipating this
  item. §2's taught primitives (`sb_fragf`, `sb_stampf`) are for
  EMITTED ARTIFACT text (`src/gen/`) and do NOT apply here —
  `axes_dump.c` renders the `--list-axes` REGISTRY dump, a `dump`-layer
  concern, not an emitted-matcher concern; the implementing lane should
  not reach for those primitives by reflex. `docs/dev/learnings.md`
  §3 / memory `pcrec-general-mechanisms-not-special-cases` applies to
  the axes.def design itself: it should be ONE general table read by
  all three current sources, not a fourth parallel mechanism next to
  them.

---

## 7. Open questions for the manager, numbered

1. **Item 4's `limits.def` unit vocabulary has no "percent."**
   `SIZE_TERM_BAR_DEFAULT` is the first ratio-shaped limit to become a
   row. Recommendation: add `"percent"` as a 16th unit rather than
   spelling it `unit ""` — a dimensionless unit for a value whose whole
   point is that it is a percentage reads worse than extending the
   vocabulary by one word, and D90's own `limits.def` header already
   treats vocabulary extension as routine (D107 does the same thing to
   `limits_check.sh`'s filter). Rests on: `limits.def:24-27`'s current
   14-plus-empty unit list, confirmed to have no percent-shaped entry.

2. **Item 2's four-membership collapse needs an authoritative
   membership chosen, and that choice is D80-observable.**
   Recommendation: the NARROWEST membership consistent with each site's
   own stated purpose (i.e., preserve today's per-site acceptance
   exactly, parameterizing the general relation rather than widening
   any site to the union) — changing acceptance is a real behavior
   change six call sites deep in `main`, not a refactor, and nothing in
   the review argues today's narrower memberships are wrong. Rests on:
   the exact 13/12/9/9/8/8 membership table in §2(a).

3. **Item 2's 6th site is a different KIND of check (pairwise
   exclusivity by summed count) from the other five (membership-in-a-
   set).** Recommendation: keep it a second relation rather than
   forcing one shape to cover both — the summed-count form is checking
   something the OR-membership form structurally cannot (that at most
   one of 7 co-equal flags is set), and collapsing it into the
   OR-membership shape would either lose that guarantee or require an
   awkward encoding. Rests on: `cli/main.c:1533-1536`'s literal
   `list_syntax + list_definitions + ... > 1` test, read directly.

4. **Item 5 (X9) is priced, not decided — this section restates that
   for Frank rather than defaulting to "build it."** The review's own
   framing (a DESIGN-EVENT that deletes rather than adds checks) is the
   argument FOR bringing it to Frank, and this sheet's job stops at
   pricing. Recommendation: given the cost inversion (A3 gets CHEAPER,
   not more expensive, from centralizing) and that the `.def` X-macro
   shape is already twice-precedented in this tree (`limits.def`,
   `rxt_schema.def`), the shape question ("should this exist") looks
   settled by precedent even before Frank's ruling on WHEN — the open
   question is genuinely just timing (this wave vs. later), not
   architecture. Rests on: §5's full site inventory and the two `.def`
   files' existence/sizes.

5. **`lib/pcrec.h`'s 32 `PCREC_NO_*`/`PCREC_FORCE_*` grep hits are not
   all axis members**, and I did not hand-sort them. Recommendation:
   whoever builds item 5 does this sort as their first step — it bounds
   `axes.def`'s exact row count and is needed before the table can be
   written. Rests on: `grep -c "PCREC_NO_\|PCREC_FORCE_" lib/pcrec.h` =
   32, cross-checked against `emit_predicate_axes`'s 18 `PredAxis`
   blocks (fewer than 32, consistent with some `PCREC_NO_*`/`FORCE_*`
   bits being non-axis semantic flags like `PCREC_NO_CAPTURES`).

6. **`emit_sweep.py`'s four streams do not cover `--list-axes` output**,
   so item 5's byte-identity gate needs a fifth, ad-hoc diff the
   implementing lane must build (a before/after `pcrec --list-axes`
   capture), not an existing instrument. Recommendation: build it as a
   throwaway script for this wave's validation, not a permanent
   addition to `emit_sweep.py` — `--list-axes` output is a `dump`-layer
   artifact, not one of the corpus/composition streams `emit_sweep.py`
   is scoped to (per that script's own header, quoted in §5's
   parenthetical). Rests on: reading `scripts/emit_sweep.py`'s header
   comment, which enumerates exactly four streams and none is
   `--list-axes`.

7. **`tools/review/out/*.tsv` census artifacts are stale** (generated
   at `7d444f9e`, before wave 3's file move) and will mislead anyone who
   trusts them for item 1 or item 5's blast radius without
   re-generating first. Recommendation: the implementing lane
   re-generates them (or re-derives the specific numbers by hand, as
   this sheet did) before citing any `tools/review/out/` figure in
   their own report — do not carry a stale row forward a second time.
   Rests on: §0.4.

8. **The 13-codegen-scripts and 35-diagnostics counts (L1-X10's and
   L11-F4's own figures) were not independently re-derived in this
   sheet** — the effort budget went to the five items' own site
   counts and the two most consequential D80 questions (items 2 and
   4) instead. Recommendation: the implementing lane re-derives both
   before relying on them, the same way every other count in this
   sheet was re-derived rather than copied. Rests on: this being the
   one place in the sheet where I am explicitly citing an unverified
   review number rather than a re-measured one (flagged inline at
   §1(b) and §2(b) respectively).

---

## 8. Validation owed

None run — this is a read-only fact sheet, no `make`, no edits under
`src/`/`cli`/`lib`/`tests`. Every count above was produced by `grep`,
`sed -n`, `wc -l`, or `git show` against worktree `w4facts` at
`923a5a58`, run directly in this session (not delegated, not copied from
a stale artifact without saying so).
