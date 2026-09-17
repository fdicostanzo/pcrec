# LENS 11 — FUNCTION COMPOSITION & ALTITUDE

Lane `lens11alt` (opus, read-only review; nothing under `src/`, `cli/`,
`lib/`, `tests/` was written, and no build or suite was run). Charter:
`docs/dev/reviews/code_review_criteria_draft.md`, lens 11 (Frank's verbatim
rubric), under the two ratification addenda.

Scope: **PRIMARY tier only** — `src/`, `cli/`, `lib/`. Emitted C, the `.rxt`
corpus, `tests/`, `studies/` and `docs/` are out by the charter's own
exclusion; `tests/lib/` + `tests/harness/` are the secondary tier, next round.

Metric artifacts cited per A5 (post-merge paths):
`tools/review/out/function_census.tsv` (860 functions, length-ranked) and
`tools/review/out/clone_candidates.tsv`. Lens 1's report is cited at its
post-merge path `docs/dev/reviews/lens_reports/lens1_semantic_duplication.md`
(read on lane `lens1dup`'s parked branch).

**The rubric, restated so the reader can check my work.** Length is a
TRIGGER, never a verdict. Every function below was scored against Frank's
five questions — (1) is the body at ONE semantic level; (2) is it one simple
purpose, clear from the NAME; (3) is it appropriately code-driven vs
data-driven; (4) are variations LOOPED rather than inlined N times; (5) are
optimizations weighed, and where the code cannot explain itself do the
comments — and a function that passes all five **stays long and the finding
says so**. §5 is that half of the deliverable and it is not short.

---

## 0. THE HEADLINE

**This tree does not have a function-length problem. It has eight functions
with one.** The census's own distribution says so: 860 functions, 18,913
code lines, **median 10 code lines**, 644 of 860 at or under 20. The 31
functions at 100+ code lines are 3.6% of the population and hold **31.4%**
of the primary tier's code (5,933 lines). The tail is not a symptom of a
loose house style; it is eight or nine specific places where one function
kept accreting, surrounded by a population composed about as well as C
allows.

That matters for the anti-perversion clause, because it means a blanket
"split everything over N" would do violence to ~23 of the 31 and buy
nothing: **13 of the 31 pass all five questions and should stay exactly as
long as they are** (§5), and most of the rest need one or two named
extractions, not a decomposition.

**The three sharpest specific results:**

1. **`pcrec_emit_vm` (778 code lines) is three functions in one, and the
   split is along a seam the file itself already respects everywhere else**
   — roughly 30% of its body is *dataflow analysis over the call graph*
   (two fixpoints, a transitive closure, a per-region save-set build) that
   emits no text at all, sitting inside a function whose job is to write C.
   It is also **the single most anchor-dense function in the tree: 26
   sabotage rows plant inside its body**, so it is simultaneously the most
   valuable and the most expensive thing on this list. That tension is the
   finding, not a footnote.

2. **The two CLI functions fail question 3 the same way and one of them has
   a correctness edge.** `cli_parse` is a 60-arm `else if` chain in which
   `!no_more_opts &&` is re-typed **59 times** — forget it once and `--`
   silently stops working for that option. `main` dispatches seven mutually
   exclusive modes with the "which other modes conflict with me" relation
   spelled **six different times with four different memberships**, correct
   today only because of the ORDER of the blocks above each one.

3. **Repetition correlates with silence, and it is measurable.** The
   functions that fail questions 3/4 are systematically the LOWEST
   comment-to-code ratio in the population (`pcrec_brport_g` 1.20,
   `pcrec_rxt_source_tsv` 1.33, `main` 1.55, `emit_predicate_axes` 1.65,
   `cli_parse` 1.74) while the functions that pass all five are the highest
   (`emit_info_def` **7.82**, `pcrec_select_engine` 4.78, `compile_ast`
   3.26). Question 5 asks whether the comments explain what the code cannot;
   the pattern says the repeated arms are the ones nobody explained, because
   per-arm there was nothing to say — the explanation belonged to the
   missing abstraction.

**One correction to lens 1's join table, measured.** Its ADDENDUM-1 row
"`vm_render_listing` → **X8**" does not hold: X8 is stamp emission
(`sb_printf(… "#define %s_…")`), and `grep -c '#define %s'` over
`src/gen/emit_vm.c` finds **52 sites, every one of them inside
`pcrec_emit_vm`** (lines 8539-11575) and **zero** inside `vm_render_listing`
(7777-8277). X8's real reach is one function, not two; `vm_render_listing`'s
own repetition is a different shape entirely (§3, F8). The rest of the join
table reproduced exactly.

---

## 1. METHOD, AND WHAT IT CANNOT SEE

**Population and order (ADDENDUM 2).** I worked the length-ranked census
top-down. The over-100-code-lines population is **31 functions, not 30** —
the brief's 30 and a first `awk NR>1 && $5>=100` count of 32 are both
artifacts of the census file's two header lines and of awk comparing the
literal header token `code_lines` against `100` as a *string*. Counted with
`($5+0)>=100` over `NR>2` it is exactly 31. All 31 are scored in §2. §7
names where I stopped.

**How a function was read.** Each was reduced to a comment-stripped
skeleton at one and two nesting levels (a throwaway script in the session
scratchpad, not committed), then the interesting regions were read in full.
The skeleton also gave a per-phase code-line count for the largest
functions; those counts include string-literal continuation lines that the
census's `code_lines` does not, so I use them as **proportions only** and
cite the census for every absolute number.

**ADDENDUM 1, the loop, as actually executed.** For every function I asked
lens 1's question first: *is there a common semantic extract that makes this
shorter without a function-specific split?* Where there is, the finding
names it and proposes **no** ad-hoc split (F6 is the pure case: the remedy
is X9 and nothing else). Where lens 1 found none — `compile_driver` and
`emit_attempt`, its two explicitly stated rows — my five questions stand
alone and I say so at the finding. §6 runs the loop in the other direction:
five extract candidates this lens found that lens 1's detector could not
see, because they live *inside* a long function rather than between two
functions.

**A3 instrument, and its limit.** Sabotage rows bind by `SAB_BEFORE` exact
source text, so the population that binds to a function is found
mechanically, never by judgement: I parsed `SAB_FILE` + the first non-blank
line of `SAB_BEFORE` out of all 262 rows in `tests/mech/sabotages/`, located
that text in the named file, and attributed it to the census row whose line
span contains it. **The limit is real and stated rather than hidden**: ~24
rows' `SAB_BEFORE` first line does not match today's source byte for byte
(some carry a second anchor in `SAB_BEFORE2`, some may have drifted), so
every anchor count below is a **floor**. A refactor wave must re-run this
attribution against its own tree rather than trusting these numbers.

**What this lens cannot see.** It reads structure, not behaviour. Every
"this could be one loop" claim below is a claim about *source shape*; where
the code writes emitted text, only the identity gate can prove the bytes did
not move, and each finding says so rather than asserting byte-identity from
a reading.

---

## 2. THE SCOREBOARD — all 31 functions at 100+ code lines

`ratio` is span-lines / code-lines (the comment-and-blank density).
`anc` is the sabotage-row floor from §1's attribution. Q1-Q5 are Frank's
five questions: `+` pass, `~` weak, `!` fail.

| # | function | file | code | ratio | anc | Q1 | Q2 | Q3 | Q4 | Q5 | verdict |
|---|---|---|---:|---:|---:|:-:|:-:|:-:|:-:|:-:|---|
| 1 | `pcrec_emit_vm` | gen/emit_vm.c:8539 | 778 | 3.90 | 26 | ! | ! | + | ~ | + | **F1** |
| 2 | `pcrec_rxt_source_parse` | parse/rxt_source.c:2095 | 548 | 1.78 | 1 | ! | ! | ! | ! | ~ | **F2** |
| 3 | `compile_driver` | core/compile.c:556 | 402 | 3.07 | 7 | ! | ~ | + | ! | + | **F5** |
| 4 | `main` | cli/main.c:1223 | 331 | 1.55 | 0 | ~ | ~ | ! | ! | ! | **F4** |
| 5 | `vm_render_listing` | gen/emit_vm.c:7777 | 288 | 1.74 | 0 | + | + | ~ | ! | + | **F8** |
| 6 | `cli_parse` | cli/main.c:379 | 247 | 1.74 | 0 | + | + | ! | ! | ~ | **F3** |
| 7 | `vm_emit` | gen/emit_vm.c:7129 | 211 | 2.44 | 9 | ! | + | + | ~ | + | **F7** |
| 8 | `emit_attempt` | gen/emit_dfa.c:6373 | 201 | 2.53 | 2 | + | + | + | + | + | PASSES (§5) |
| 9 | `vm_revdet_rep` | gen/emit_vm.c:4827 | 184 | 1.76 | 1 | + | + | + | + | + | PASSES (§5) |
| 10 | `emit_predicate_axes` | parse/axes_dump.c:375 | 178 | 1.65 | 0 | + | + | ! | ! | ~ | **F6** |
| 11 | `vm_cursor_rep` | gen/emit_vm.c:4037 | 177 | 2.12 | 5 | + | + | + | ! | + | **F12** |
| 12 | `pcrec_rxt_source_tsv` | parse/rxt_source.c:3816 | 167 | 1.33 | 0 | + | + | ! | ! | ! | **F9** |
| 13 | `pcrec_syntax_explain` | parse/syntax_dump.c:1508 | 146 | 1.80 | 0 | ~ | + | + | + | + | **F14** |
| 14 | `pcrec_rxt_compose` | parse/rxt_compose.c:718 | 146 | 1.93 | 0 | ~ | + | + | + | + | PASSES (§5) |
| 15 | `pcrec_rxt_source_resolve` | parse/rxt_source.c:3491 | 140 | 1.69 | 0 | + | + | + | ~ | + | PASSES (§5) |
| 16 | `pcrec_modport_optrun` | parse/mod_modifiers.c:242 | 125 | 1.98 | 4 | + | + | ~ | ! | + | **F11** |
| 17 | `pcrec_brport_g` | parse/mod_backrefs.c:318 | 125 | 1.20 | 0 | + | + | + | ! | ! | **F10** |
| 18 | `compile_ast` | ir/nfa.c:551 | 121 | 3.26 | 1 | ~ | + | + | + | + | **F7** (mild) |
| 19 | `vm_count_slots` | gen/emit_vm.c:2566 | 119 | 2.93 | 1 | ! | + | + | + | + | **F7** |
| 20 | `pcrec_select_engine` | opt/select_engine.c:480 | 117 | 4.78 | 9 | + | + | + | + | + | PASSES (§5) |
| 21 | `pcrec_minimize_dfa` | opt/minimize.c:66 | 114 | 1.40 | 0 | + | + | + | + | + | PASSES (§5) |
| 22 | `vm_counter_phase` | gen/emit_vm.c:5210 | 113 | 1.60 | 4 | + | + | + | + | + | PASSES (§5) |
| 23 | `vm_cost_rep` | gen/emit_vm.c:1938 | 112 | 2.32 | 0 | + | + | + | + | ~ | PASSES (§5) |
| 24 | `p_class` | parse/parse.c:943 | 111 | 2.58 | 2 | + | + | + | ! | + | **F13** |
| 25 | `pcrec_scanedge_dfa` | opt/scanedge.c:467 | 108 | 2.07 | 1 | ~ | + | + | + | + | **F15** (mild) |
| 26 | `pcrec_prefix_ksets` | opt/prefix_k.c:371 | 107 | 1.85 | 2 | + | + | + | + | + | PASSES (§5) |
| 27 | `vm_look_behind` | gen/emit_vm.c:6249 | 107 | 1.85 | 3 | ~ | + | + | + | + | **F14** |
| 28 | `emit_info_def` | gen/emit_dfa.c:1470 | 104 | 7.82 | 2 | + | + | + | + | + | PASSES (§5) |
| 29 | `compile_source` | cli/main.c:1082 | 104 | 1.35 | 0 | + | + | + | + | + | PASSES (§5) |
| 30 | `pcrec_callgraph_build` | opt/callgraph.c:648 | 102 | 2.01 | 2 | + | + | + | + | + | PASSES (§5) |
| 31 | `first_of` | opt/possessify.c:163 | 100 | 2.81 | 4 | + | + | + | + | + | PASSES (§5) |

Tally: **13 PASS all five and stay long** (§5); 15 carry a filed finding;
3 carry a mild one. Not one of the 31 is a candidate for the mechanical
"split at N lines" the rubric warns about.

---

## 3. FINDINGS, ranked

Ranked MECHANICAL-and-safe first per A4, with the DESIGN-EVENT-adjacent
ones last. Every row states its lens 1 join per ADDENDUM 1 *before* any
function-specific proposal.

---

### F8 — `vm_render_listing`: three identical section loops and six identical slot loops

**Severity: MAINTAINABILITY. Effort: MECHANICAL. Blast radius: 1 file,
0 sabotage rows, `tests/vm/run_vm_tests.sh:803` names this function in a
check that compares the listing against the emitted artifact; no emitted
`.c` bytes (this writes the `--emit-ir` listing).**

**Lens 1 join: NONE APPLIES, and the join table's X8 row is wrong here**
(§0). X8's 52 stamp sites are all in `pcrec_emit_vm`; this function has
zero. Its repetition is its own.

**Evidence (A5):** census row `src/gen/emit_vm.c:vm_render_listing`
7777-8277, 288 code lines, 41 `sb_printf(o,` sites.

Q4 fails twice, in two families.

*Family one — the per-quantifier event sections.* `emit_vm.c:8067-8079`
(RUNGS), `8089-8100` (STRATEGIES) and `8118-8131` (PRUNING) are the same
twelve-line program three times, differing in exactly four values: the event
kind, the name table, one column width, and the empty-population sentence.

```c
/* One home for "list every event of kind K, or say why there are none". */
static void vm_listing_events(StrBuf *o, const Vm *v, int kind,
                              const char *const *kindname, int namew,
                              const char *none_msg);
```

*Family two — the slot families.* `8019-8054` walks `nguard_total`,
`nlow`, `nmark`, `nrev` (three lines per entry), `nlookmark` and `nlookpos`
with six copies of one `for` + `sb_printf("  %-12d %-22s %s\n", …)` shape.
The variation is (count, slot accessor, description) — a three-column table
over the six families, walked once.

**Why this one is first.** It is the largest pure Q4 failure in the tree
with **zero** sabotage anchors, one file, and an output that no artifact
consumes — the cheapest possible first move for a refactor wave that wants
to prove its method before touching anything anchored.

---

### F12 — `vm_cursor_rep`: the emitted span-scan loop is written twice

**Severity: MAINTAINABILITY (emitted-text divergence risk). Effort:
MECHANICAL. Blast radius: 1 file, **5 sabotage rows** attribute inside this
function, `tests/codegen/run_codegen_tests.sh` and `tests/vm/run_vm_tests.sh`
name it; the emitted bytes must not move and the identity gate is the proof.**

**Lens 1 join: none applies** — lens 1 did not reach the VM's rung emitters
(its ADDENDUM-2 remainder item 1 names exactly this surface as unreviewed
and asks for a second pass).

**Evidence (A5):** census row 4037-4412 (177 code lines).
`emit_vm.c:4151-4158` (the possessive arm) and `4292-4303` (the greedy arm)
emit the identical eight-line C fragment — `{ unsigned long it_ = 0; …
while (CURSOR + stride <= BOUND TEST) { CURSOR += stride; it_++; } }` —
differing in exactly one token: the bound is the literal
`subject_length` in the first and a variable (the MRL-folded window end or
`subject_length`) in the second.

```c
/* Emit the artifact's bounded span scan. BOUND is the C expression the
 * cursor may not pass; everything else is identical at both call sites. */
static void vm_emit_span_scan(StrBuf *b, const Vm *v, const Ast *a,
                              int stride, const char *test, const char *bound);
```

**Why it is worth more than eight lines.** Two writers of one emitted
fragment is exactly the hazard this tree has recorded elsewhere (k49fix
§2.3's twice-spelled boundary rule was allowed to ship *only because it also
shipped an agreement check that extracts one from the artifact and compares
it against the other*). Here there is no agreement check, and the two copies
are 140 lines apart in one function.

---

### F10 — `pcrec_brport_g`: three delimiter branches that are one parse

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 1 file, 0
sabotage rows attribute inside this function (the file carries 5 that name
other functions — a wave must re-check), `docs/spec/` carries no wording pin
on these refusals beyond the module's own diagnostics.**

**Lens 1 join: X6 (the group-reference kit) applies to the file and NOT to
this repetition.** X6 is about `mod_backrefs.c` ↔ `mod_recursion.c` sharing
(`br_relative`, `br_name_ref`); the duplication here is *intra-function* and
survives X6 untouched. It is a §6 feedback item.

**Evidence (A5):** census row 318-467, 125 code lines, **ratio 1.20 — the
lowest in the 31-function population**. Three branches: `\g{…}`
(328-376), `\g<…>` / `\g'…'` (383-436), and the bare form (442-466). All
three run the same four-step program: find the delimiter's end, trim, read
an optional `+`/`-` sign, scan digits, then either resolve a relative
reference or take a name. The sign-scan alone —

```c
int sign = 0; size_t d = b;
if (p[d] == '-') { sign = -1; d++; }
else if (p[d] == '+') { sign = 1; d++; }
```

— is typed at `:339-342`, `:394-397` and `:443-446`.

```c
/* The one \g-family reference parse: a [b,e) span, already delimiter-
 * stripped, yields either a (signed) number or a name. */
static int br_ref_in_span(Ctx *cx, const char *p, size_t b, size_t e,
                          int *sign, long *value, const char **name);
```

What genuinely varies per branch and must stay at the call site: the
delimiter search, whether interior whitespace is trimmed (the brace form
trims, the angle form does not), and the `what[]` text built for the
diagnostic. **The lowest comment ratio in the population and the clearest
triplication are the same function**, which is §0's third headline in its
purest single-function form.

---

### F13 — `p_class`: the class-endpoint read is spelled twice, and a ruling says it should be once

**Severity: MAINTAINABILITY, with a ruled-record argument in its favour.
Effort: LOCAL. Blast radius: 1 file, 2 sabotage rows attribute inside
`p_class` (including `S-U1`, whose `SAB_BEFORE` quotes the three-line
fold/union/negate tail at `:1223-1225` — *outside* the region this finding
moves).**

**Lens 1 join: none applies.** Lens 1 did not file `parse.c`.

**A1 — the ruled record.** K12's fix is recorded as *"the five-step §16
order in `p_class`"* (docs/dev/CLAUDE.md's known-issues entry), i.e. the
ORDER in which a class endpoint is resolved is a ruled property with a
recorded bug behind it. That ruling is an argument **for** this extraction,
not against it: today the order is spelled twice and correctness depends on
the two spellings agreeing.

**Evidence (A5):** census row 943-1228 (111 code lines). The low endpoint
is read at `parse.c:1069-1073` and the high endpoint at `:1165-1170` with
the same three-way program (`\` → `esc_class_value`, `>= 0x80` →
`lit_next_cp` after un-consuming, else the literal byte), followed by the
same `EXT_REFUSAL && !ep_set_certain` test at `:1114` and `:1170`.

```c
/* One class endpoint: consumes it, returns the code point, and fills the
 * extension claim. §16's order lives here and nowhere else. */
static int cls_endpoint(Ctx *cx, int c, bool quoted, ExtResult *claim);
```

Everything else in this 215-line loop is genuinely sequential class-item
parsing at one altitude, and I am **not** proposing to split it.

---

### F6 — `emit_predicate_axes`: a data table written as 178 lines of code

**Severity: MAINTAINABILITY. Effort: DESIGN-EVENT (it is X9, not a local
edit). Blast radius: per lens 1's X9 — `cli/main.c`, `src/parse/axes_dump.c`,
`lib/pcrec.h`, and it DELETES rather than re-aims two awk scrapers. 0
sabotage rows attribute inside this function.**

**Lens 1 join: X9 IS THE WHOLE REMEDY, and lens 11 proposes no split at
all.** This is ADDENDUM 1's pure case: scored on its own, the function
fails question 3 outright, and the correct response is not to cut it into
pieces but to delete it into a table that already has a proposed home
(`src/core/axes.def`).

**Evidence (A5):** census row 375-668 (178 code lines). Twenty blocks of
the identical shape — declare a `PredAxis` initializer with eight of its
ten fields identical (`NULL, "", 0, NULL, 0, NULL, NULL, NULL`), then call
`emit_pred_row` two to eight times with an ordinal and two strings. There
is no control flow in the function at all: not one `if`, not one loop. It is
a table with parentheses.

**The honest note on question 5:** the per-row prose *is* the documentation
of each axis, and it must survive into the table's rows. An X9 that keeps
the strings and loses the explanations would trade one problem for a worse
one.

---

### F9 — `pcrec_rxt_source_tsv`: the header reads the column table, the row writer does not

**Severity: MAINTAINABILITY trending CORRECTNESS-RISK. Effort: LOCAL.
Blast radius: 1 file; `--list-source` is a published contract
(`docs/spec/table_contract.md`, `docs/spec/rxt_format.md`) so any change is
a D80 spec event even if no byte moves; the format-reader survey
(`tests/rxtsource/run_rxtsource_tests.sh`) asserts field counts.**

**Lens 1 join: X12 applies to this FILE (11 `strcmp` ladders) but not to
this function.** No extract shortens it.

**Evidence (A5):** census row 3816-4037 (167 code lines, ratio 1.33).
`rxt_source.c:3787-3801` declares `rxt_columns[]`, twenty entries, and
`:3852-3856` writes the header by walking it. The row writer at
`:3863-3906` then writes twenty fields **by hand, in an order maintained by
eye**, as twenty repetitions of `sb_putc(&sb, '\t'); if (r->FIELD)
sb_puts(&sb, r->FIELD);`.

**The comment on the table claims a safety the structure does not
provide.** `:3789-3792` says the list is *"kept as a table rather than as
fifteen `sb_puts` calls in the header string so the HEADER and the ROW
WRITER cannot disagree about how many there are"* — but the row writer never
reads the table; the agreement rests entirely on a check in
`tests/rxtsource/`. That is question 5's truthfulness half: the comment
describes a structural guarantee where the guarantee is procedural. (The
same comment's opening words, *"THE 15 COLUMNS"*, stand over a twenty-entry
array; `w23implfix_report.md` already recorded this at sixteen entries, so
this is its second observation, not a new finding.)

```c
/* A row descriptor per column: the accessor and the escaping rule.
   The header AND the row writer walk the same array. */
static const struct { const char *name; RxtFieldKind kind; size_t off; }
    rxt_columns[] = { … };
```

The four `#section` blocks at `:3916-4034` are a second, milder Q4 instance
(four copies of `if (count) { section_open(...); for (...) { emit row } }`);
`section_open` already exists, so half the extraction is done and the loop
body is what varies.

---

### F11 — `pcrec_modport_optrun`: fourteen parallel booleans applied by fourteen parallel lines

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 1 file, **4
sabotage rows attribute inside this function** (`S22` caret-reset, `S24`
a-sub lookahead drop, `S25` x-level counts-not-adjacency, `S26`
unset-applied-first) — every one of them plants in exactly the region this
finding would move, so the re-aim burden is the finding's main cost and its
intent re-verification is not a formality.**

**Lens 1 join: none applies.**

**Evidence (A5):** census row 242-488 (125 code lines).
`mod_modifiers.c:250-253` declares `set_i/set_s/set_U/set_n/set_m/set_J`
and `un_i/un_s/un_U/un_n/un_x/un_m/un_J`; `:276-399` sets them in a switch;
`:419-432` applies them in fourteen consecutive one-line `if`s. Three of the
fourteen letters are genuinely special (`x` carries a LEVEL, `m` and `J`
carry their own rulings, `r`/`a` refuse), and those must stay as code.

```c
/* letter, ParseMods field, and whether the letter takes a level */
static const struct { char c; size_t off; bool levelled; } optrun_letters[];
```

**A1 caution.** R17 (`2026-08-12-r17-mod05.md`) reviewed this grammar and
`S24`/`S25`/`S26` exist because three *"correct-today-unguarded port
corners"* were found here — the a-sub two-homes rule, x-level
adjacency-vs-count, and unset-wins. A table must preserve all three, and the
unset-wins ordering in particular is a property of the APPLY ORDER
(`set_*` before `un_*`), which a naive per-letter table would erase. **File
this one behind F1-F13 and require its sabotage rows to be re-run in the
failing direction, not merely re-anchored.**

---

### F7 — the per-kind dispatchers with one fat arm: finish the pattern the file already set

**Severity: MAINTAINABILITY. Effort: LOCAL (per function). Blast radius:
`vm_emit` **9 sabotage rows**, `vm_count_slots` 1, `compile_ast` 1; no
emitted bytes if faithful, and the identity gate proves it.**

**Lens 1 join: X1 covers the WHOLE-TREE walks and explicitly does not cover
these** — X1's shape is "classify / descend / spine-loop" over an `Ast` for
a verdict; these are per-kind *producers* (they emit, count or build), which
X1's proposed signature does not serve. Lens 1's §5 warning applies with
equal force here: do not merge the arms, only relocate them.

**Evidence (A5) and the argument, which is the file's own precedent.**
`src/gen/emit_vm.c` already ratified this shape once: `vm_cost` (98 code
lines) dispatches per kind and its `A_REP` arm is a **one-line delegation**
to `vm_cost_rep` (`:2349-2350` → `:1938`, 112 code lines). Three functions
away, the same file does the opposite:

| dispatcher | code | the fat arms, inline | already delegated |
|---|---:|---|---|
| `vm_emit` 7129-7643 | 211 | `A_BREF` 7416-7555 (~80 lines), `A_CAP` 7349-7415, `A_CAT` 7557-7592, `A_WORDB/A_NWORDB` 7312-7348 | `A_ALT`→`vm_alt`, `A_REP`→`vm_rep`, `A_ATOMIC`→`vm_atomic`, `A_LOOK`→`vm_look`, `A_CALL`→`vm_call`/`vm_splice` |
| `vm_count_slots` 2566-2914 | 119 | `A_REP` 2777-2912 (135 span lines), `A_LOOK` 2609-2709 | — |
| `compile_ast` (ir/nfa.c) 551-945 | 121 | `A_REP` 723-810, `A_ALT` 683-722 | `A_ATOMIC`→ recursion, leaf kinds → `frag_single` |

Question 1 is what fails: in `vm_emit`, six arms are one line and four are
whole programs, so reading the function tells you six of ten things it does
and hides the other four. The remedy is `vm_bref`, `vm_cap`, `vm_cat`,
`vm_wordb` / `vm_count_slots_rep` / `compile_rep`, each named the way
`vm_cost_rep` already is, and the dispatcher becomes what its name says.

`compile_ast` is marked *mild*: its `A_REP` arm is the bounded-repeat
expansion that K7's fix rewrote, its comment density is 3.26, and it is the
one place in `nfa.c` where the expansion's shape can be read in one screen
alongside the fragment algebra it uses. A wave should take `vm_emit` and
`vm_count_slots` first and decide `compile_ast` on the evidence of those.

---

### F14 — three loop bodies that are functions: `vm_look_behind`, `pcrec_syntax_explain`, `emit_attempt`'s state loop

**Severity: POLISH. Effort: MECHANICAL. Blast radius: `vm_look_behind` 3
sabotage rows, `pcrec_syntax_explain` 0, `emit_attempt` 2.**

**Lens 1 join: none applies** (`emit_attempt` is one of lens 1's two
declared "no extract applies" rows; the other is `compile_driver`, F5).

Each of these is a short preamble plus one loop whose body is the whole
function:

- `vm_look_behind` (`emit_vm.c:6315-6444`, 130 of 198 span lines): the
  per-branch emission. Extract `vm_look_behind_branch(v, a, i, br, bl,
  bodl, endl, …)`.
- `pcrec_syntax_explain` (`syntax_dump.c:1565-1717`, 150 of 263 span
  lines): the per-registry-row match-and-render. Extract `explain_row(...)`.
- `emit_attempt` (`emit_dfa.c:6729-6870`): the per-state block. **I probed
  this one and HELD it** — see §5.1; it is listed here only so the
  synthesis does not re-find it and think it was missed.

The first two are the honest, small, no-argument wins; I rank them last
among the mechanical findings because the gain is readability only.

---

### F15 — `pcrec_scanedge_dfa`: nine parallel arrays hand-allocated and hand-freed

**Severity: POLISH (MAINTAINABILITY on the failure path). Effort: LOCAL.
Blast radius: 1 file, 1 sabotage row.**

**Lens 1 join: X5 (the growable arena array) does NOT cover this** — these
are fixed-size `malloc`/`calloc` blocks, not a growth idiom — but it is the
same missing library one shelf over, and §6 records it as such.

**Evidence (A5):** census row 467-690 (108 code lines).
`scanedge.c:478-516` allocates nine blocks, `:517-521` tests all nine in one
`if` and unwinds, and `:688-689` frees all nine in two lines. That is ~25 of
the function's 108 code lines spent on storage, at a different altitude from
the chain-finding algorithm they serve; one `struct ScanEdgeScratch` with an
allocate/free pair puts the algorithm on one screen. (`pcrec_minimize_dfa`
has the same shape at five blocks and I passed it in §5 — five is the line
I drew, and I state it rather than pretending the boundary is principled.)

---

### F3 — `cli_parse`: a 60-arm `else if` chain, with one guard re-typed 59 times

**Severity: MAINTAINABILITY, with a named correctness hazard. Effort:
CROSS-CUTTING (it is X9 + X10 plus the table). Blast radius: `cli/main.c`,
0 sabotage rows, `tests/cli/run_cli_tests.sh` (2,209 lines) pins diagnostic
wording, and `docs/spec/cli.md` + `docs/spec/limits.md` + `docs/spec/registry.md` carry
**28 `cli/main.c:<line>` references over 25 lines** — of which I verified at least five are
**already stale today** (`limits.md`'s `cli/main.c:56-58` lands in a
`PCREC_MAX_DFA_STATES_TABLE` comment; its `272-282` lands in
`set_encoding`; `cli.md`'s `159` lands in a usage string and its `345-350`
in the tail of `struct CliState`). Nothing checks them, which is exactly why
a wave must re-aim them by flag SPELLING rather than by line — the citation-
provenance class `w23implfix_report.md` named, recurring in the spec tier.**

**Lens 1 join, taken first per ADDENDUM 1: X9 (≈60 lines of this function
are the optimization-axis arms) and X10 (the five `strtol` arms at `:568,
585, 647, 660, 701`).** Together they remove roughly a third of the body
without any lens 11 proposal at all. **What they do not touch is the
chain itself**, and that is where the hazard lives.

**Evidence (A5):** census row 379-809 (247 code lines);
`tools/review/out` has no clone row for it because each arm is one line —
below the detector's shingle floor. Direct census: **61 string-compare
calls inside the function** (the tree-wide scan finds only seven functions
with five or more; this one has nearly as many as the other six combined),
and `!no_more_opts &&` appears in **59** of the top-level arms.

**The hazard, stated precisely.** `--` (end of options) works because every
one of the 59 arms remembers to test `no_more_opts`. There is no structural
reason a sixtieth arm would; the failure mode is silent (an option keeps
being recognised after `--`), it is invisible to any test that does not
specifically pair that flag with `--`, and the correct spelling is
unenforceable by the compiler.

```c
/* One row per option. The `--` rule, the "=value" split and the
   unknown-option refusal are the loop's, not each arm's. */
static const CliOpt cli_opts[] = {
  { "--emit-main",  OPT_FLAG,  offsetof(pcrec_options, flags), PCREC_EMIT_MAIN },
  { "--unroll=",    OPT_INT,   offsetof(pcrec_options, unroll_k), 1, 64, "1..64" },
  …
};
```

with X10's `cli_int_opt` as the `OPT_INT` handler and X9's `axes.def` rows
generating every `-fno-*` entry. The arms that cannot be table rows —
`--tune`'s two spellings, `--engine=`'s inner ladder, `--features`'s
lookahead, the bare-`-` and `--` cases — stay as code after the table walk,
which is question 3 answered honestly rather than universally.

---

### F4 — `main`: seven modes, and the mutual-exclusion relation written six times with four memberships

**Severity: MAINTAINABILITY trending CORRECTNESS-RISK. Effort: LOCAL
(after F3). Blast radius: `cli/main.c`, 0 sabotage rows,
`tests/cli/run_cli_tests.sh` pins the refusal wording of every one of these
blocks (35 `pcrec: --…` diagnostics in the file), D80 spec hunk required.**

**Lens 1 join: none applies.** X10 stops at `cli_parse`.

**Evidence (A5):** census row 1223-1736 (331 code lines, ratio 1.55).
Seven mode blocks — `--list-source` (1335), `--probe-ask` (1383),
`--emit-ir` (1429), `--count-groups` (1457), the list-family (1489),
`--source` (1644) and the default compile path (1668) — each of which is
the same three-part program: *reject every other mode; reject the
incompatible non-mode options; do the work and return.*

The first part is written **six times with four different memberships**
(`cli/main.c:1308, 1336, 1384, 1430, 1458, 1489`): thirteen members at
`:1308`, eleven at `:1336`, nine at `:1384` and `:1430`, eight at `:1458`
and `:1489`. The short ones are correct **only because of the order of the
blocks above them** — `:1489` may omit `count_groups` solely because
`:1457`'s block already returned. Nothing states that dependency; it is
carried by block order in a 331-line function.

Second Q4 instance in the same function: `:1251-1267` re-declares
seventeen `const` locals whose entire content is `st.<field>`, which is
below the function's altitude and adds a second name for every mode flag —
so `st.source` and `list_source` are read in the same conditional at
`:1336` while `st.list_source` is not used at all.

```c
static const CliMode cli_modes[] = {
  { "--list-source", offsetof(CliState, list_source), MODE_QUERY,
    .forbids = MODE_ANY_OTHER | OPT_PATTERN | OPT_OUTPATH | OPT_FLAVOUR,
    .run = run_list_source },
  …
};
```

One table makes the relation declarative, makes each mode's incompatible
options a field rather than a paragraph, and makes the order of the blocks
stop being load-bearing. `main` then reads: parse, resolve features, pick
the mode, run it.

---

### F5 — `compile_driver`: a 402-line pipeline with a 266-line failure policy inlined in the middle

**Severity: MAINTAINABILITY. Effort: LOCAL, with a stated technical
constraint. Blast radius: `src/core/compile.c`, **7 sabotage rows**
attribute inside the function, `COMPILE_MAX_ATTEMPTS` is derived from the
rung set, and `docs/spec/` describes the retry's observable stamps
(`RX_ENGINE_SEL`).**

**Lens 1 join: NONE — lens 1 says so explicitly** (its §3 names
`compile_driver` and `emit_attempt` as the two rows where no extract
applies and lens 11's questions must stand alone). They do, and they fail
question 1.

**Evidence (A5):** census row 556-1789 (402 code lines, 1,234 span).
Reading it at one nesting level, the body is:

| region | what it is |
|---|---|
| 556-690 | options/tune resolution, then ~30 locals — 10 of them the size-term ladder's parallel arrays (`st_k`, `st_ok`, `st_code`, `st_total`, `st_nodes`, `st_whylen`, `st_fc`, `st_sc`, …) |
| 691-820 | per-attempt `Ctx` construction (~40 field assignments) |
| **822-1088** | **`if (setjmp(cx.jb)) { … }` — the whole retry policy: five rungs** |
| 1092-1525 | the actual pipeline: parse → compose → altcls → discharge → callgraph → select → postresolve → lower → build → emit (one call per line, with rationale) |
| 1532-1677 | the size-term ladder's accounting, three phases |
| 1690-1771 | diagnostics, take the output, return |

The pipeline region — the part the function is NAMED for — is one call per
pass at a uniform altitude and is a pleasure to read. It is bracketed by two
regions at a completely different altitude, of which the setjmp handler is
the larger: **five retry rungs inlined one after another**, each shaped
`const bool X_eligible = …; if (X_eligible) { job_cleanup(&cx); <mutate the
carried state>; <reset err>; continue; }` — the size-term ladder (842-861),
the SEL-1 overflow pair (890-920), OPT-4's size rung (947-969),
`SDR_NO_ANCHORED` (1017-1027) and `SDR_NO_PREMUL` (1073-1085).

Two measurable consequences of that shape: `err->msg[0] = 0; err->pos = 0`
is re-typed **7 times** in the file, and `COMPILE_MAX_ATTEMPTS` is a
hand-derived expression over the rung structure —
`3 + 2 * (SIZE_TERM_LADDER_N + 1) + 1 + SDR_MAX` (`compile.c:403`) — which
every new rung must remember to move.

**A1 — the ruled record, cited and NOT contradicted.** `utf8k53_report.md`
§1.2 records the author deliberately declining to build *"a contributor
table, a registry, or a per-contributor callback"* because at N=1 those are
*"machinery designed around one customer, which D18/OS-0/D53 forbid"*, and
§1.1 names the repeated shape explicitly (*"a fourth of the same shape"*).
**I am not proposing that table.** Two notes for the synthesis, both
factual: the same report named the event that would reopen the question —
*"a future droppable contributor … is the event that makes rung ORDER a
real question"* — and that event has arrived (`SDR_NO_PREMUL`, ruled by
Frank 2026-09-17 at `internal.h:1904-1929`, so the ladder is N=2 today and
its order is RULED rather than measured); and what this finding proposes is
orthogonal to the table question anyway.

**The proposal** is one extraction at the altitude seam:

```c
/* Decide what a failed attempt licenses. Returns RETRY (state mutated for
   the next attempt) or GIVE_UP. All five rungs live here; the driver sees
   a verdict. */
static RetryVerdict compile_retry(Ctx *cx, CompileRetryState *rs,
                                  pcrec_options *defo, pcrec_error *err);
```

plus a `SizeTermState` struct for the ten parallel ladder arrays and a
`retry_reset(err)` for the seven copies.

**The technical constraint, stated because it is the real risk.** The
`volatile` qualifiers on the carried scalars are required by the standard
for automatic objects of the function containing `setjmp` that are modified
between the `setjmp` and the `longjmp`, and `compile.c:589-602` documents
that `make strict`'s `-Wclobbered` flags exactly these. Moving the *policy*
into a callee is safe (the callee's own automatics are not implicated), but
the carried state must stay in `compile_driver`'s frame and be passed by
pointer — a `CompileRetryState` of pointers-to-volatile, or the struct
itself declared `volatile` in the caller. Any wave that takes this finding
must build under `make strict` and read the `-Wclobbered` output as an
acceptance criterion, not as noise.

---

### F2 — `pcrec_rxt_source_parse`: 25 productions inlined in one loop, beside the table that was supposed to end that

**Severity: MAINTAINABILITY trending CORRECTNESS-RISK. Effort:
CROSS-CUTTING. Blast radius: `src/parse/rxt_source.c` (4,037 lines), 1
sabotage row attributes inside the function (the file carries more that name
other functions), `tests/rxtsource/run_rxtsource_tests.sh` is the
three-legged parity harness and every production has fixtures, D80 spec
event if any refusal moves.**

**Lens 1 join, taken first: X5 and X12 apply and are not enough, and lens 1
says so.** X5 (the growable arena array) reaches this function's own
`RXT_PUSH_FRAME` macro (`:2123-2142`); X12 (strcmp ladders that are lookups)
reaches its 27 string compares. Lens 1's ADDENDUM-2 remainder item 2 names
this file as the surface it took X5 and X12 from **and went no further** —
so for the body of the function, my five questions stand alone.

**Evidence (A5):** census row 2095-3069, **548 code lines — the second
longest function in the tree**, max nesting depth 5, 27 string compares
(second only to `cli_parse`). The body is one `for (size_t i = 0; i < L.n;
i++)` line loop containing, in order: line classification and blank/comment
handling; the indentation/attachment state machine with frame push and
close (2236-2374); schema-row resolution and the generic checks
(2376-2476); and then **three scope-keyed `tok_is` ladders** —
`RXT_SCOPE_FILE` with eleven arms (2479-2689), `RXT_SCOPE_CONFIG`
(2691-2720), the section scopes (2735-2744) — followed by the block-scope
ladder with ten more (2816-3008). Arms range from three lines (`tag`) to
**73** (`include`, 2527-2600).

**A1 — the direction is already ruled, and this is the half that did not
land.** `src/parse/rxt_schema.def`'s own header states the ruling: *"Until
W23.1 the format's structural rules lived in `src/parse/rxt_source.c`'s
control flow — three flat keyword tables and a chain of `tok_is()` arms,
each remembering its own cardinality, its own continuation rule and its own
idea of what may be indented under it. The ruling is that those rules are
DECLARED and VALIDATED instead."* W23.1 landed exactly that for STRUCTURE
(scope, cardinality, value shape, children, constraints — walked by
`frame_constraints` and `check_value_shape`). The per-production SEMANTICS
— what each keyword's value means and where it is stored — stayed inline,
and that is what this finding is about. **I am not arguing against the
boundary the tree drew**: `check_value_shape`'s own comment
(`rxt_source.c:960-972`) rules that *"the PRECISE grammar of a `token`, a
`list` or a `qualified-line` stays with the production that owns it, and
that is a boundary rather than a shortcut"*, with a worked reason
(`lib "a path"` is a `token` whose value carries a space). Agreed — a
production's grammar should stay with the production. **The proposal is that
a production should therefore BE something**: a named function, reachable
from its schema row, instead of an anonymous arm in a 548-line loop.

```c
/* Beside the existing schema row: the production's own reader. */
typedef int (*RxtProduction)(RxtP *p, RxtFrame *f, RxtRow *block,
                             const RxtSchemaRow *row, size_t line,
                             const char *tok, const char *value);
/* rxt_source.c keeps one table (scope, kind) -> production; the loop
   resolves the row (it already does) and calls it. */
```

with `rxt_line_include`, `rxt_line_vocabulary`, `rxt_line_under`,
`rxt_line_provenance` and the rest as file-static functions — which is what
the 73-line `include` arm already is in everything but name.

**Why the severity carries the "trending" half.** The parse loop keeps
fourteen pieces of carry-over state across iterations (`last_indent`,
`last_was_content`, `last_row`, `last_rxtrow`, `last_row_line`,
`last_row_value`, `cur_route`, `last_aux_line`, plus the frame stack), and
every inline arm can read and write all of them. The lane reports from W23.3
and W23.5 record three defects of exactly that family — `under`'s key tuple
sliding one component left, `prose_value` measuring zero on an indented
line, the attachment branch holding three distinct mistakes under one
sentence — which is the cost of a state machine whose productions have no
boundary. A production-per-function does not fix those; it makes the next
one local.

---

### F1 — `pcrec_emit_vm`: an analysis pass, a configuration pass and an emitter sharing one body

**Severity: MAINTAINABILITY (the code is correct; the cost is read-time and
edit-time). Effort: CROSS-CUTTING, STAGEABLE. Blast radius: 1 file, **26
sabotage rows attribute inside this function — the densest anchor site in
the tree, 10% of the whole failing-direction net**; `tests/codegen/`'s
identity gate and D76/D94's abi ritual bind every emitted byte;
`tests/vm/run_vm_tests.sh` and `tests/codegen/run_cpset_structure.sh` name
it directly.**

**Lens 1 join, taken first: X8 and X1.** X8 (stamp emission) is confirmed
exactly here — 52 `sb_printf(… "#define %s_…")` sites, **all 52 inside this
function**. X1's whole-tree walk reaches it through its `pcrec_has_atomic` /
`pcrec_has_lookaround` reads at `:8756-8758`. **Neither shortens it
materially**: X8 converts 52 format strings into 52 helper calls (its value
is the greppable stamp-name set that D94's ritual wants, which is real but
is not a length remedy), and X1 touches two call sites. So after lens 1 is
fully applied, this function is still ~700 code lines, and the five
questions have to answer it.

**Q1 and Q2 fail, and the seam is unusually clean.** Reading at one nesting
level, the body is nine regions. Measured as a proportion of the
comment-stripped body (§1's caveat on absolute counts):

| region | ~share | what it is | emits text? |
|---|---:|---|:-:|
| 8539-9000 | 13% | slot/backreference map, `unroll_k`, MRL flags, **the call-target nullability FIXPOINT** (8792-8865) | no |
| 9000-9189 | 9% | **the per-region W save-sets, the transitive closure over `callgraph_reaches`, and a second FIXPOINT for per-region cost** | no |
| 9189-9405 | 8% | frame/trail capacity, step and work budgets, tiered-entry decision, buffer surface | no |
| 9405-10075 | 12% | the prologue and ~60 stamps | yes |
| 10075-10400 | 10% | the `run_state` struct, the `R_*` macros | yes |
| 10400-10770 | 19% | the run function's preamble, the reset function, the dispatch prologue, the body splice | yes |
| 10770-10970 | 7% | accept / fail / exhaust trailers | yes |
| 10970-11310 | 10% | the search entry and its retry loop | yes |
| 11310-11575 | 11% | the three public entries, residual, info, `main`, the IR dump, the job write-back | yes |

**Roughly 30% of the longest function in the tree emits nothing.** The
9000-9189 region in particular is textbook dataflow analysis — allocate a
bitset per call target, union the transitively-reached targets' sets, sort
the members into a list, then run a readiness-ordered fixpoint calling
`vm_cost` per region — with an internal-error check at `:9138-9143` that
exists precisely because *two* computations of |W| have to agree. That is a
pass. It has a name in the design (§6.3's W-set), it has its own failure
mode, and it is sitting in the middle of a function whose job is to write C
text.

```c
/* Three extractions, in dependency order; each takes `Vm *` and returns
   void, because the state they compute already lives on `Vm`. */
static void vm_resolve_nonnull(Vm *v, Ast *root);        /* 8792-8865  */
static void vm_build_region_saves(Vm *v, Ast *root, int nstate); /* 9000-9186 */
static void vm_plan_capacities(Vm *v, ...);              /* 9189-9400 */
```

After those three and X8, `pcrec_emit_vm` is an emitter of ~450 lines whose
regions are the emitted file's own order — which is the shape `emit_attempt`
and `emit_info_def` already have and which §5 passes them for.

**Q4 is weak rather than failed**, and the reason is worth recording so a
wave does not over-cut: the emitted regions look repetitive (nine
`sb_printf` blocks writing entry points) but each writes a *different*
emitted function with a different signature and different guards, and
`vm_emit_default_entry` (`:8438`) is already the extracted common part,
called at `:11312`, `:11470` and `:11484` — the file's own comment at
`:11466` says the rule is stated once *"and not restated at each of the
three"*.

**Q5 passes, emphatically.** This is the most heavily explained function in
the tree by absolute comment volume (2,259 comment/blank lines), and the
comments are doing question 5's job rather than narrating: `:8570-8597`
records that a check was placed at the wrong site and why the conclusion
survived a pass reorder; `:8586-8592` deletes a *wrong reason* for a right
conclusion and says so (*"a wrong reason is worse than none"*). The
archaeology half of that volume is lens 4's charter and I do not duplicate
it here.

**The staging this finding requires (A3).** With 26 sabotage anchors in one
body, the order is: (1) X8's stamp helpers, which move no logic and whose
anchors are `#define` text; (2) `vm_resolve_nonnull`; (3)
`vm_build_region_saves`; (4) `vm_plan_capacities` — each its own commit with
the identity gate green, each re-running the sabotage rows whose
`SAB_BEFORE` text the commit moved, found by grep and not by memory. A
single "decompose `pcrec_emit_vm`" commit is the wrong unit of work and
would make a red sabotage row impossible to attribute.

---

## 4. THE CROSS-CUTTING OBSERVATION (question 5, measured)

The scoreboard's `ratio` column is not decoration. Sorting the 31 by it:

- **Bottom five**: `pcrec_brport_g` 1.20 (F10, triplicated parse),
  `pcrec_rxt_source_tsv` 1.33 (F9, hand-maintained column order),
  `compile_source` 1.35 (PASSES), `pcrec_minimize_dfa` 1.40 (PASSES),
  `main` 1.55 (F4, six copies of one relation).
- **Top five**: `emit_info_def` 7.82 (PASSES), `pcrec_select_engine` 4.78
  (PASSES), `pcrec_emit_vm` 3.90 (F1, but Q5 passes), `compile_ast` 3.26
  (PASSES/mild), `compile_driver` 3.07 (F5, Q5 passes).

Every function I scored `!` on question 3 or 4 sits at or below 1.98; every
function whose only problem is SIZE sits at or above 2.0. Two of the bottom
five pass all five questions, so this is a correlation and not a rule — but
the direction is one-way and worth stating as a review heuristic: **a long
function with a low comment ratio is nearly always long because something is
written N times, and a long function with a high comment ratio is nearly
always long because the problem is.** The ratio is a cheap pre-filter for
which of the two a reviewer is looking at.

---

## 5. PASSES AND STAYS LONG — the anti-perversion half

Thirteen of the 31 pass all five questions. For each: why it is long, and
what a mechanical splitter would have broken.

1. **`emit_info_def`** (`gen/emit_dfa.c:1470`, 104 code lines in **813
   span** — ratio 7.82, the highest in the tree). It writes the
   `struct rx_info` initializer, field by field, in struct order. One
   purpose, one altitude, and the length is 87% explanation of what each
   field means to a consumer. It also carries `.abi = 26` (`:1965`), so
   D76/D94 make any edit here an abi event with a whole-file identity
   re-pin. **Do not touch this function.** If a wave ever must, the change
   is a scaffolding change by definition and carries the ritual.

2. **`pcrec_select_engine`** (`opt/select_engine.c:480`, 117 lines in 559,
   ratio 4.78, 9 sabotage anchors). Four phases — mask narrowing, explicit
   selection, the prefilter decision, the possessify/revdet handoff — all at
   one altitude (selection policy), and the volume is the *rationale* for
   decisions that R47 and the O-31 investigations both had to re-derive from
   it. The prefilter block (`:643-919`) is the only plausible extraction and
   I hold it in §5.1.

3. **`emit_attempt`** (`gen/emit_dfa.c:6373`, 201 lines). Writes one
   emitted function, in the emitted function's own order: byte-class table,
   per-state target tables, locals, the start loop, the gates, the prefilter,
   the seed dispatch, the per-state blocks, the epilogue. The four per-state
   arms (`wsplit` / `endvar` / `eolvar` / plain) are four genuinely
   different emitted programs, each with a comment naming the wave and the
   shape that forced it. See §5.1 for the one extraction I probed.

4. **`vm_revdet_rep`** (`gen/emit_vm.c:4827`, 184 lines). Emits one rung's
   whole emitted program in label order — scan, body, short, full, commit,
   walk, extend — with the analysis marks (`vm_rung_mark`, `vm_prune_mark`)
   interleaved at the sites that decided them. Splitting at the labels would
   produce functions that each take the other's labels as parameters.

5. **`vm_counter_phase`** (`gen/emit_vm.c:5210`, 113 lines). Same argument,
   one rung down: the unrolled counter loop's trip/tail/skip labels are one
   program.

6. **`vm_cost_rep`** (`gen/emit_vm.c:1938`, 112 lines). The rung ladder as a
   cost question, in the same order the emitter takes the rungs — the
   correspondence IS the correctness argument and separating them would hide
   it. (One question-5 note, not a finding: `vm_cursor_fits(...)` is called
   three times with the same arguments at `:1980, 2063, 2116`, which reads
   as three independent tests of one predicate; a `const bool` computed once
   would say what is true.)

7. **`first_of`** (`opt/possessify.c:163`, 100 lines). A per-kind
   classification returning a `First` set. Every arm is short; the length is
   the kind count times the per-kind justification. **A table here would
   delete the `-Wswitch` alarm**, and that alarm is the ruled record:
   `src/opt/mrl.c:14-20` (*"an exhaustive switch per analysis is the alarm
   that fires when a node kind is added"*, with `:279`'s worked case) and
   `src/opt/atomic.c:28-35` (*"NONE OF THE SEVEN SWITCHES IN THIS FILE
   CARRIES A `default:`"*, which cites the mrl.c rule by line). Question 3's answer here is "code, deliberately".

8. **`pcrec_minimize_dfa`** (`opt/minimize.c:66`, 114 lines). One
   algorithm — Moore refinement — with its five scratch buffers freed on one
   path. Initial partition, refine to fixpoint, rebuild. Nothing crosses an
   altitude.

9. **`pcrec_prefix_ksets`** (`opt/prefix_k.c:371`, 107 lines). One cost-model
   search: walk the frontier, price each candidate, pick, materialise. The
   selection loop reads the model it just built; separating them would put
   the model's units in two places.

10. **`pcrec_callgraph_build`** (`opt/callgraph.c:648`, 102 lines). Already
    composed the way F7 asks `vm_emit` to be: seven named phases, five of
    them one `cg_walk` call with a callback struct. Its length is the phase
    count.

11. **`pcrec_rxt_compose`** (`parse/rxt_compose.c:718`, 146 lines). Bind
    rounds, unresolved diagnosis, export check, assignment, delivery-map
    build, injection. Marked `~` on Q1 only for the 87-line delivery-map
    block at `:894-981`, which is a real candidate if this file is ever
    opened for another reason — not worth a wave on its own.

12. **`pcrec_rxt_source_resolve`** (`parse/rxt_source.c:3491`, 140 lines).
    Three phases: verify every `lib` resolves, walk the closure, build the
    targets. The per-field `blk ? blk : set` cascade at `:3713-3721` is
    six lines of genuine three-way policy (the `features` case differs), and
    a table would hide the one that differs.

13. **`compile_source`** (`cli/main.c:1082`, 104 lines). Parse, resolve,
    select the target, decide the output shape, loop. The cleanest long
    function in `cli/main.c` and the model the other two should look like.

**One from the mid-band, because it answers a question the census raises.**
`frame_constraints` (`parse/rxt_source.c:1223`, 73 code lines) has **max
nesting depth 8 — the deepest in the tree** — and passes all five questions:
it is the schema-driven constraint walk (rows → constraints → kinds), the
depth is the table's own three levels plus a switch, and every arm is
short. Depth, like length, is a trigger and not a verdict.

---

### 5.1 PROBED AND HELD — extractions I considered and declined

1. **`emit_attempt`'s per-state block** (`emit_dfa.c:6729-6870`, 140 span
   lines in one loop). Declined: the body reads `d`, `st`, `acc2`, `unl`,
   `p`, `c`, `wsplit`'s `endview`, and the per-state target-table names the
   function itself emitted — an extraction's parameter list would be the
   function's own local state handed back to it, which is indirection
   without an altitude change. F14 lists it only so it is not re-found.

2. **`pcrec_select_engine`'s prefilter block** (`select_engine.c:643-919`).
   Declined: 276 span lines but ~25 code lines, all at the same altitude as
   the rest of the function (selection policy), and 9 sabotage rows bind
   inside the function. The volume is rationale, and moving the rationale
   away from the decision it explains is the opposite of question 5.

3. **The nine `atomic.c` predicate walks.** Held, and lens 1's §5 is the
   reason, restated here so that a reader of THIS report reaches the same
   conclusion: they must not become one function; only the traversal is
   extractable, and the wrong version of that refactor deletes two sabotage
   rows' plant sites and the `-Wswitch` alarm in one commit.

4. **`compile_driver`'s `volatile` declarations.** Held. They look like
   noise and are not: `compile.c:589-602` documents that
   `-Wclobbered` (promoted by `make strict`) flags exactly these
   automatics, because the loop calls `setjmp` fresh each iteration. Any
   F5 wave must keep them and prove it with `make strict`.

5. **`emit_vm.c`'s job-owned scratch buffers** (`v->cx->job->scr_test`,
   used at `:4091`). Looks like a premature optimization replacing a local
   `StrBuf`; it is not, and the comment says why — a size-term ladder trial
   can `longjmp` out mid-append, and the battery's LeakSanitizer axis found
   the orphaned local that a plain local produced. Question 5 answered
   correctly at the site.

6. **`pcrec_minimize_dfa`'s five `malloc`s** (vs F15's nine in
   `pcrec_scanedge_dfa`). Held at five. The line I drew between the two is
   the fraction of the function they occupy (~10% vs ~25%), and I state that
   it is a judgement rather than pretending it is a principle.

7. **Splitting any of the four per-rung VM emitters by emitted label.**
   Held: the labels are one control-flow graph and the emitted program's
   order is the function's order. This is the shape the rubric's warning is
   about.

---

## 6. FEEDBACK INTO LENS 1 (ADDENDUM 1's loop, other direction)

Five extract candidates this lens found that lens 1's instruments could not
see, because they live INSIDE a long function rather than between two named
ones. Each is offered in lens 1's own terms (A2: the shared abstraction
named) for the synthesis to merge into the X-list or drop.

1. **X5's real population is 28, not 10.** Lens 1's X5 lists ten named
   `*_push`-style functions. `grep -rn "cap \* 2 :" src/ cli/` finds **28
   sites**, of which **22 are `arena_alloc`-based** — the exact shape X5's
   `pcrec_arena_vec_push` serves. The eighteen X5 did not list are *inline*
   copies inside longer functions: `rxt_source.c:1348` (inside
   `line_constraints`), `:2126` (inside `pcrec_rxt_source_parse`'s
   `RXT_PUSH_FRAME` macro), `:3408`, `:3445`, `:3476`, `rxt_compose.c:823`
   (inside `pcrec_rxt_compose`), `emit_vm.c:740, 1438, 3548, 3584`,
   `altcls.c:235`, `lower_enc.c:205`, `atomic.c:380`, plus the four
   `realloc`/`malloc`-based ones X5 correctly excludes on ownership grounds
   (`ir/dfa.c:878, 1035`, `ir/nfa.c:138`, `cli/main.c:365`). **The inline
   copies are part of why the long functions are long**, which is precisely
   ADDENDUM 1's loop closing.

2. **The listing-section loop** (F8's `vm_listing_events`), 3 sites.

3. **The emitted span-scan writer** (F12's `vm_emit_span_scan`), 2 sites,
   emitted-text divergence risk.

4. **The `\g`-family reference parse** (F10's `br_ref_in_span`), 3 sites
   inside one function — the intra-function half of X6, which X6's
   cross-file framing does not reach.

5. **The class endpoint read** (F13's `cls_endpoint`), 2 sites, with K12's
   ruled ordering as the reason it should have one home.

And one **correction**: the join table's `vm_render_listing` → X8 row does
not hold (§0); X8's population is 52 sites in one function,
`pcrec_emit_vm`, confirmed by direct grep in both directions.

---

## 7. WHERE I STOPPED (ADDENDUM 2) — the unreviewed remainder, named

**Reviewed individually and scored against all five questions:** the 31
functions at 100+ code lines (§2), in full.

**Reviewed opportunistically, not individually scored:** nine functions in
the 50-99 band that a mechanical scan or a neighbouring read pulled in —
`frame_constraints` (73, scored and passed, §5), `parse_setting` (74),
`parse_case_body` (88, via the ladder scan), `seen_add` (12), `cond_holds`
(32), `cli_flag_of` (15), `stamp_macro_of` (9), `prov_push` /
`variant_push` / `case_push` (13 each, via X5).

**Two tree-wide mechanical scans were run over the WHOLE 860-function
population**, so the claims they support are not limited to the read set:

- the string-compare-ladder scan (question 3): only **seven** functions in
  the primary tier carry five or more `strcmp`/`strncmp`/`tok_is` calls —
  `cli_parse` (61), `pcrec_rxt_source_parse` (27), `parse_setting` (11),
  `parse_case_body` (11), `cond_holds` (6), `cli_flag_of` (6),
  `stamp_macro_of` (5). The last two are lens 1's X12. **Question 3's
  failure mode is therefore fully enumerated for the tree**, not sampled.
- the nesting-depth scan (question 1): six functions at depth 6+, all named
  in §2 or §5.

**Named remainder, NOT reviewed:**

1. **The 50-99 code-line band, 29 functions I did not open** — including
   `vm_cost` (98), `clo_walk` (96), `vm_rev_emit` (96), `emit_state_legend`
   (95), `apply_target` (94), `pcrec_modport_uprops` (88), `trie_build`
   (86), `pcrec_build_dfa` (86), `intern` (84), `vm_rep` (84), `gk_build`
   (82). This band holds 2,303 code lines (12% of the tier). On the two
   mechanical axes above it is clean, so what is unreviewed here is
   questions 1, 2 and 5 — altitude, naming and explanation — which need a
   reading and cannot be scanned for. **If a second lens 11 pass is
   chartered, this band is where it goes**, and `vm_cost` + `vm_rep` +
   `vm_rev_emit` first, since F7 and F12 both land next to them.

2. **The 800 functions at or under 49 code lines** (~9,800 code lines,
   52% of the tier). Not individually reviewed. The distributional evidence
   says the risk here is low — median 10 lines, 644 of 860 at or under 20 —
   and the two scans found nothing in this band except the two X12 members.
   The question the scans cannot answer is question 1's *other* direction
   (a function too GENERAL for its body, or a decomposition so fine the
   reader has to reassemble it), and I did not sample for it. I flag it as
   genuinely unmeasured rather than implying the population is clean.

3. **`lib/pcrec.h`** — no functions in the census sense; lens 9's charter.

4. **The secondary tier** (`tests/lib/`, `tests/harness/`) — out of this
   round by the charter.

**I am not naming a need for a second pass on the emitters**, unlike lens 1,
and the reason is that lens 11's questions on `src/gen/emit_vm.c` are
answered by F1, F7, F8 and F12 plus the §5 passes; what remains unread there
is duplication, which is lens 1's charter and which lens 1 has already
named.
