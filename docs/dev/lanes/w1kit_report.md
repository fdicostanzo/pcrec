# [REVW.1] WAVE 1 STAGES 1-2 — THE EMISSION KIT

Lane `w1kit` (opus, 2026-09-18), branched off `lane/w1stage0` at `74736fb4`.
Charter: `docs/dev/reviews/lens_reports/lens10_emission_kit_charter.md`
stages 1 and 2. Manager synthesis `docs/dev/reviews/2026-09-17-code-review.md`
§3 wins on any disagreement with the charter; D108 is the binding design
constraint. Stage 3 (fragment retirement) is WAVE 2's and is untouched here.

**PARKED, NOT MERGED.** `make test` was launched as this lane's last act per
BOILERPLATE's DO-THEN-FINISH; §7 names the log and what is owed.

---

## 0. THE HEADLINE — the charter's central stage-1 proposal is REFUTED BY THE TREE

The charter's §2.2 item (4) promotes `rxt_source.c`'s `put_escaped` verbatim as
`sb_field`, "one TSV field, framing-safe", and lists as its customers
`syntax_dump.c`'s TSV path, `axes_dump.c`'s `axis_row`, `limits_dump.c`'s
`limit_row` and `schema_dump.c`'s inline rows. **Adopting it there is a
contract break, not insurance**, and the number is not marginal:

| dump | data rows | rows carrying a RAW BACKSLASH |
|---|---:|---:|
| `--list-syntax` | 138 | **56** |
| `--list-families` | 100 | **50** |
| `--list-definitions` | 50 | **33** |
| `--list-axes` | 78 | **9** |
| `--list-limits` | 57 | **2** |
| `--list-schema` / `--list-verbs` | 71 / 50 | 0 / 0 |
| | | **150 rows** |

`put_escaped`'s vocabulary DOUBLES the backslash, because the `.rxt` subject
escape is round-trippable and `tests/harness/driver.c`'s `decode()` reads it
back. The registry dumps' `syntax` column is literally `\d`, `\p{`, `\N{U+`,
and `tests/reject/` iterates those rows to build probe patterns. `sb_field`
there turns `\d` into `\\d` on 150 rows across five dumps.

**The charter half-saw this and drew the line one file too far left.** Its own
§2.2(4) keeps `put_text` (`syntax_dump.c`'s `--explain` escaper) separate on
exactly this ground — *"it deliberately passes `\` through … two correct
policies for two formats"* — and says what is shared is only the `\xNN` tail.
That is right, and it is true of the registry DUMPS as well as of `--explain`:
`docs/spec/table_contract.md` rule 5 asks only that *a field never contains a
TAB*, and says nothing about escaping. The charter's error is treating
"`--list-source` is a TSV dump" and "`--list-syntax` is a TSV dump" as one
population when their WIRE FORMATS differ.

**Taking the tree's side, the kit ships TWO vocabularies over ONE
implementation** (§1). That is the shape the charter's own `\xNN`-tail
observation points at; it just does not follow it through to a second entry
point.

### 0.1 The charter's stage-1 precondition, answered

> *"does any string reachable by `axes_dump.c`, `limits_dump.c` or
> `schema_dump.c` contain a tab, newline or control byte today? If the
> population is zero the wave is byte-neutral and the escaping is insurance.
> If it is non-zero the wave is a BUG FIX and must be filed as one."*

**ZERO**, and measured wider than asked — every `--list-*` surface, not the
three named: 0 rows carrying a non-TAB control byte, and 0 rows whose field
count differs from their own header's, across all eight dumps. So the escaping
IS insurance, it is byte-neutral, and there is no bug to file — **in the
vocabulary that is correct for those dumps**. In the charter's proposed
vocabulary the population is 150 and the wave is a regression.

---

## 1. THE KIT, AS BUILT (stage 1)

Home: `src/core/sb.c` and its `internal.h` block, per the charter — every
function is under 20 lines, they all sit on `StrBuf`, and D2 makes a new
`.c`/`.h` pair a Makefile edit for no capability.

```c
void sb_text (StrBuf *sb, const char *s);              /* NUL-terminated */
void sb_textn(StrBuf *sb, const char *s, size_t n);    /* n bytes, may not be */
void sb_field(StrBuf *sb, const char *s);
void sb_join (StrBuf *sb, const char *sep, const char *const *names, size_t n);
void sb_row  (StrBuf *sb, const char *const *cells, size_t ncell);
```

**`sb_text`/`sb_textn` — the FRAME escape.** A byte below 0x20, and 0x7f, goes
out as `\xNN`; every printable byte, backslash included, passes through. This
is `--explain`'s vocabulary and every registry TSV dump's.

**`sb_field` — the `.rxt` SUBJECT escape**, `put_escaped` moved verbatim:
`\\ \t \n \r` then the same tail. Round-trippable. Its customers are
`--list-source`'s 11 escaped-column sites and nothing else in the tree.

Both share `sb_frame_byte`, one static, which is the `\xNN` tail the charter
identified as written twice. `sb_textn` exists because `put_text` was
LENGTH-based with two call sites passing a non-NUL-terminated slice
(`query + nstart, namelen` and `&selb, 1`) — a detail the charter's one-entry
sketch had no room for.

**`sb_join` — no truncation, no reordering, no dropping.** That is the whole
point; `enabled.c` and `enc.c` are the bounded joins that could do all three
(§3).

**`sb_row` is `sb_join` with `"\t"`, `sb_text` per cell, and a newline** — one
loop, not two implementations. Its value is the CELL COUNT: a row whose field
count differs from its header's is exactly the `NF != 15` class of defect
`w23impl_report.md` recorded, and a named cell array is what makes the count
readable at the call site.

### 1.1 What was adopted, and what was not

| site | before | after |
|---|---|---|
| `rxt_source.c`'s `put_escaped` (11 calls) | its own switch | **`sb_field`**, function retired |
| `syntax_dump.c`'s `put_str` (13 calls) | `if (s) sb_puts(sb, s)` — **escaped nothing** | **`sb_text`**, function retired |
| `syntax_dump.c`'s `put_text` (4 calls) | its own `\xNN` loop | **`sb_textn`**, function retired |
| `syntax_dump.c`'s `put_mask` (6 calls) | a `first` flag + `sb_putc('|')` | select into a small array, **`sb_join`** |
| `axes_dump.c`'s `axis_row` | one `sb_printf`, 12 conversions | **`sb_row`** over a named 12-cell array |
| `limits_dump.c`'s `limit_row` | one `sb_printf`, 7 conversions | **`sb_row`** over a named 7-cell array |
| `schema_dump.c`'s two row sites | one `sb_printf` each | **`sb_row`**, 10 and 4 cells |
| `--list-syntax`'s own 17-column row | per-column `sb_text` + `sb_putc('\t')` | **UNCHANGED** — §1.2 |
| `rxt_source.c`'s 20-column row + 4 sections | per-column, conditional, mixed | **UNCHANGED** — §1.2 |

**The three dumps that "escape nothing" now escape something**, in the right
vocabulary: `axes_dump.c`, `limits_dump.c` and `schema_dump.c` route every
cell through `sb_text`, and so does `--list-syntax`/`--list-definitions`/
`--list-families`, whose own TSV path never called the escaper sitting in its
own file. That is L10-3's actionable core, closed.

### 1.2 `sb_row` is NOT adopted at the two big rows, and the reason is structural

The charter names five row emitters. Four took `sb_row` and the two largest did
not, because **their cells are not in hand as strings — they are produced INTO
the buffer.**

`--list-syntax`'s row is 17 columns, of which three are MASKS rendered inline
(`put_mask` writes straight to `sb`), one is a `0x%04x`, and five are
per-column enum renderings — each column carrying its own dated comment
explaining when and why it was appended. Converting it to a `const char *[17]`
means three scratch `StrBuf`s per row × 138 rows, and it destroys the
per-column comment placement on the tree's most contract-load-bearing dump
(`tests/reject/` iterates it). `rxt_source.c`'s main table is 20 columns of
conditional and numeric writes plus four `#section` blocks in the same shape.

Against §4's altitude rubric this is question 3 answering *correctly
code-driven*: the current form is readable, per-column annotated and correct,
and a cells-array rewrite would be violence for no capability. **The four sites
that DID take `sb_row` are exactly the ones that already received their cells
as a parameter list or a struct** — the conversion there is a named array a
reader can count against the header, which is the improvement.

The one thing each of the four needed is a small local for its single numeric
cell (`char ord[16]`, `char val[24]`, `char wave[16]`). These are **not** the
`PCREC_MAX_EMIT_NAME_LEN` class the coding guide §2.2 forbids adding to: no
`-p` prefix reaches them and the bound is the TYPE's, not a pattern's. Each
says so at the site.

---

## 2. D108 — THE SEAM AS BUILT

> *(1) the kit's primitives take DATA and produce TEXT; they do not reach back
> into compiler state. (2) Keep the walk -> event -> render boundary clean.*

**(1) holds by construction and is checkable by grep.** Every one of the five
functions takes `(StrBuf *, values…)`. None takes a `Ctx`, a `Job`, an `Ast`,
a `Dfa` or a `Vm`; none reads a global. A back-end fed from a deserialized IR
calls them unchanged, because there is nothing for it to be missing. The
declarations in `internal.h` state the rule where a future author meets it.

**(2) was not at risk in these stages and the report says so rather than
claiming credit.** The walk→event→render seam is `emit_vm.c`'s `VEvent`
stream and `vm_render_listing`; stages 1-2 touch neither. What stages 1-2 owed
D108 is NON-FORECLOSURE, and the measurable form of that is: when wave 2's
renderer arrives, does it have a text layer to call? It does, and the layer it
gets is data-in/text-out with two vocabularies already separated — which is
strictly more useful to an IR back-end than one vocabulary would have been,
since an IR back-end serializing `.rxt` fixtures and one rendering a registry
dump need different escapes for the same reason these two do today.

One thing worth naming for wave 2: **`sb_row`'s cell array is the natural shape
for an event-consuming renderer** and the natural shape for nothing else here,
which is why four sites took it and two did not. A renderer built from an event
stream has its cells in hand by construction.

---

## 3. L10-2 — THE BOUNDED JOINS, AND A THIRD FAILURE MODE NOBODY PREDICTED

The charter files L10-2 **CORRECTNESS-RISK (live, small)**: five join
implementations, three with different undocumented over-long policies, one of
which (`render_modules`) produces an out-of-order partial list.

### 3.1 The severity is wrong: it is LATENT, not live

| join | rendered bytes today | buffer | headroom |
|---|---:|---:|---|
| `render_modules` (`--features all`) | 179 | 512 | **35% used** |
| `pcrec_enc_names` (`byte, utf8`) | 10 | 128 | **8% used** |

Neither truncation branch has ever been taken. This is the same correction
lens 10 itself made to lens 2's L2-1 (CORRECTNESS-RISK → MAINTAINABILITY with
a latent risk, once the margins were measured) arriving one finding later.

### 3.2 The demonstration, both loop bodies verbatim, at caps the tree cannot reach

```
modules cap=30  OLD: classes,unicode-props,quoting
modules cap=30  NEW: classes,unicode-props
modules cap=38  OLD: classes,unicode-props,assertions,misc
modules cap=38  NEW: classes,unicode-props,assertions
encs    cap= 7  OLD: 'byte, '
encs    cap= 7  NEW: 'byte'
encs    cap=11  OLD: 'byte, '
encs    cap=11  NEW: 'byte, utf8'
```

The modules rows are L10-2's own claim reproduced: at cap 30 `assertions`,
`backrefs` and `recursion` are skipped and the SHORTER `quoting` is appended —
a gap-toothed, out-of-order list that reads exactly like a complete one. **And
that list is EMITTED** (`PCREC_FEATURE_MODULES`), so the failure mode is an
artifact claiming a feature set the build does not have.

**The `encs` rows are a THIRD failure mode neither L10-2 nor this lane
predicted.** The charter says `pcrec_enc_names` "silently drops". It does
worse: the separator is written under a DIFFERENT bound from the name
(`k + 2 < cap` vs `k + ln + 1 < cap`), so at caps 7-10 it emits `"byte, "` —
a **dangling separator**, a menu that reads as though a name went missing
rather than as a truncated list. At cap 11 it drops `utf8` entirely where the
repaired form fits it.

### 3.3 The fix is one keyword at each, and `sb_join` is DECLINED there with a reason

Both are now an **ordered PREFIX**: what does not fit is the tail.

`sb_join` cannot truncate at all and is the better answer — but it needs a
`StrBuf`, i.e. a heap allocation, and **`pcrec_enc_names` sits on
`pcrec_compile`'s own refusal path** (`src/core/compile.c:1141`, immediately
before a `ctx_fail`), where a failed `realloc` has no error channel and
`sb_grow` would `abort()` the CALLER. That is coding-guide §1.1 exactly: *an
`abort()` on OOM kills the caller's process*. Introducing that hazard to repair
an unreachable defect is the wrong trade, and having ONE of the two bounded
joins reach the primitive while the other cannot is worse than having neither —
two policies again, which is what L10-2 is about.

So `sb_join` ships with `put_mask` as its adopting customer (6 call sites, one
implementation) and as `sb_row`'s implementation, and the two bounded sites get
the policy stated identically at both. The reasoning is written at both
functions, so the next reader does not re-derive it.

**A note on D82 bound 3** (≥2 existing implementations before an extraction).
Counted honestly there are **six** separator loops in the tree — `put_mask`,
`syntax_dump.c`'s family-members loop, these two bounded ones, and
`cli/main.c`'s two stderr target lists — but they write to **three different
destinations** (`StrBuf`, a fixed buffer, `FILE *`), and the extractable part
(*"if not first, write the separator, then the name"*) is one line. What
actually differs between them, and what is actually defective, is the over-long
POLICY, which only the two bounded ones have at all. The bound is satisfied by
the escape pair (`put_text` + `put_escaped`, two implementations of one tail)
rather than by the join.

### 3.4 `cli/main.c`'s two stderr joins are DECLINED

`fprintf(stderr, "%s%s", i ? ", " : "", ts[i].prefix)` streams to a `FILE *`
and can neither truncate nor reorder — it is already the correct shape.
Routing it through `sb_join` means materializing a `const char *` array from a
strided struct field, at an unbounded `nt`, plus a heap `StrBuf`: more code, a
new allocation, no behaviour change. Not done.

---

## 4. STAGE 2 — THE CLI CHANNEL

```c
static int cli_err(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
```

`"pcrec: "` + the message + a newline, on stderr, returning 1. **71 of
`cli/main.c`'s 79 `fprintf(stderr, …)` sites** route through it.

**NO `where` PARAMETER.** The charter's item (7) and lens 2's sketch both give
it a leading `const char *where` rendered `" (<where>)"`, with a
`format(printf, 3, 4)` attribute that does not match its own signature.
MEASURED: not one of the 79 sites has that shape — the parentheticals in these
messages are prose inside the sentence, at a dozen different positions, and
none is a location this channel could compose. A parameter with no caller is
machinery ahead of a measured need (D77). The reason is at the function so it
is not re-proposed.

**EIGHT SITES DECLINED**, each with its reason:

- `write_file`'s `"%s: write error\n"` is deliberately path-prefixed like
  `perror()` and is not a `"pcrec: "` message at all.
- Seven belong to the two PIECEWISE builders — `--target`'s *"no target named
  'x' (it declares: a, b)"* and the multi-target *"… has 2 targets (a, b) and
  `-o x` names a single file …"* — which assemble ONE logical message across
  five statements with a loop in the middle. Routing them through a single call
  needs a buffer, which is a change of SHAPE rather than of channel and is out
  of scope for a mechanical wave (the charter's own §3 stage-2 discipline: *"a
  diff that changes one word of one message is out of scope"*).

### 4.1 D26, proven two ways, by instruments that deliberately do not share a rule

**(1) THE MESSAGE SET.** Derived from the source's own call statements
(balanced-paren, string-aware), normalized by deleting every `"pcrec: "` and
every `"\n"` ANYWHERE in a statement's joined literal set — **not** by
stripping a prefix and a trailing newline the way the conversion does. That
distinction is load-bearing and was earned: the conversion's first pass used
"the last string literal in the statement", which is a TERNARY OPERAND at four
sites (`st.target ? "--target" : "--lib-path"`), so it missed them; an
instrument sharing that rule would have read green on exactly the four sites
the rule got wrong. **79 messages, IDENTICAL.**

**(2) THE LIVE SWEEP.** Every option bare / `=` / `=bad` / separate-arg-bad,
every query mode, every `tests/rxtsource/fixtures/*.rxtin` through `--source`
and `--target`, plus the pattern/prefix/output-path refusals: 1.68 MB of
stdout+stderr+rc over **379 diagnostic lines**. **BYTE-IDENTICAL**, which is
what covers newline PLACEMENT, the thing instrument (1) deliberately does not
check.

`tests/cli/run_cli_tests.sh`: **284 passed / 0 failed**.

---

## 5. BYTE-NEUTRALITY — THE STAGE-1 EVIDENCE

The charter asks for `--list-*` output diffed byte for byte "for every dump and
every flag combination the CLI accepts". Built as a 3.6 MB corpus and re-run
after EVERY commit:

- 7 registry dumps × **12 `--features` axes** (none/all/std1/classes/
  modifiers,assertions/unicode-props/recursion/lookaround/backrefs/
  named-groups/atomic-groups/quoting), stdout and stderr and rc;
- `--list-syntax`/`--list-definitions` × the `--flavour` axis, plus the
  bad-flavour refusal, at all 12 feature axes;
- `--explain` over **all 138 registry rows' own `syntax`**, at both gate states;
- `--probe-ask` × 3 levels × 138 rows × 2 gate states;
- `--list-source` over **all 249** `tests/**/*.rxt` + `*.rxtin` files;
- the CLI menus (`-e nosuch`, `--features nosuch`, `--encoding=utf8
  --engine=dfa`, `--target nosuch`).

**0 differing files at every one of the four checkpoints** (the syntax_dump
adoption, the `sb_field` adoption, the row layer, the L10-2 fix).

And because `PCREC_FEATURE_MODULES` is EMITTED TEXT, the L10-2 fix additionally
got an **emit-diff**: 300 corpus patterns × 5 `--features` axes = 1,500 cells,
compiled by a `git stash`-built branch-point binary and the new one —
**0 movers**, 1,133 identical, 367 both-refuse.

**abi verdict: NOT an abi event**, as the charter predicts for both stages. No
emitted scaffolding moved: `--list-*` output is not artifact text, `cli_err`
writes to stderr, and the emit-diff above is the direct measurement for the one
change that reaches an artifact at all.

---

## 6. ANCHOR RE-AIMS — TWO, BOTH RE-VERIFIED DETECTED

Population found BY GREP on this tree (method rule (i)): **266** `S*.sh` row
files; `grep -rl` for every identifier this wave moves
(`put_escaped`/`put_str`/`put_text`/`put_mask`/`render_modules`/
`pcrec_enc_names`/`axis_row`/`limit_row`/`emit_pred_row`/`cli_err`/`fprintf`)
returns **zero** rows for all of them. Only two rows anchor text this wave
moves, both found by `SAB_FILE`:

**S200 (`--list-source` emits a raw tab in the pattern column).** Its anchor is
one line of `put_escaped`'s switch, at 8-space indentation. The function moved
to `src/core/sb.c` **VERBATIM — same bytes, same column** — so the anchor text
is UNCHANGED and only `SAB_FILE` moves. That is method rule (ii) working as
stated: `replace.py` matches whole-file and line-agnostic, so a relocation that
keeps its column costs a re-aim of one field. Verified the literal occurs
exactly once in `sb.c` and zero times in `rxt_source.c` before committing.
*Intent re-verified* (the house rule, and it needed asking because the function
now serves a wider name): `sb_field` has exactly the 11 `--list-source` call
sites `put_escaped` had and no others — the registry dumps use `sb_text`, the
other vocabulary, which does not carry this case at all.

    S200  pop:tests/modifiers/xxmode.rxt:/^pattern .*<TAB>/=1(want>=1),
          reach:ok(1/1), rxtsource:2fail/210pass                  DETECTED

**S241 (`--list-schema` hand-writes one row instead of walking the table).**
Its anchor quoted the schema row's `sb_printf` through the cardinality
argument; that call is now `sb_row` over a cell array, so the text no longer
exists. RE-DERIVED from the live source, not weakened: the plant is the same
one column on the same one row, spelled against the cell array instead of the
vararg list, carrying the rest of the array through verbatim exactly as the old
form carried the rest of the format. Occurrence count verified at 1. Reach
probe unchanged and still reads the shipped `at-most-one`.

    S241  reach:ok(1/1), rxtsource:1fail/211pass                  DETECTED

Both run solo through the driver (`run_sabotage_matrix.sh S200` / `S241`,
`CC=gcc-16 PROCS=2`), both `unexpected: 0, undetected: 0, unreached: 0,
anomalies: 0, oracle-skipped: 0`. Field validation (`VALIDATE_ONLY=1`) passes
on both. Logs: `build/w1kit_mech_S200.log`, `build/w1kit_mech_S241.log`.

**`make mech` was NOT run in full**, per the brief; the checkpoint battery
covers it.

---

## 7. VALIDATION

| | |
|---|---|
| `make -j4 CC=gcc-16` | clean after every commit |
| `make strict CC=gcc-16` | clean after every commit |
| `tests/cli/run_cli_tests.sh` | **284 passed / 0 failed** |
| the 3.6 MB dump corpus | **0 differing files**, ×4 checkpoints |
| the 1.68 MB CLI sweep | **byte-identical**, 379 diagnostic lines |
| the CLI message set (79) | **identical** |
| L10-2 emit-diff, 1,500 cells | **0 movers** |
| sabotage S200 / S241 | **DETECTED** / **DETECTED** |
| `tests/rxtsource/run_rxtsource_tests.sh` | **0 failed**, 211 files / 3,938 blocks / 28,949 lines |
| `make test-registry` | **0 failed** after §7.3's fix (102/0, 22/0, 54/0; definitions-oracle 354 cells / 101,244 A==B / 101,244 A==C / 0 disagreements) |
| `make test-codegen` | **1 failure, the known pre-existing darwin one** — §7.1 |
| full `make test` | §7.2 — OWED |

### 7.1 Targeted suites

Logs in the worktree: `build/w1kit_rxtsource.log` (`RXTSOURCE_RC=0`),
`build/w1kit_registry.log`, `build/w1kit_codegen.log` (`CODEGEN_RC=2`).

`make test-codegen`'s single failure is
`tests/codegen/run_inline_capability.sh`:

    FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is
          evidence here

which is the darwin nm-probe red this lane's brief names as pre-existing and
carrying `TEST_RC=2`. Every other script in that group is green (31/0, 14/0,
13/0, 9/0 …), and the check is a `[CC-DIFF]` STEP 2 compiler CAPABILITY probe
that compiles its own witness and reads symbols with `nm` — it touches nothing
stages 1-2 moved.

### 7.3 THE ONE RED THIS LANE CAUSED, AND THE TREE'S OWN CHECK CAUGHT IT

`make test-registry` went red on the FIRST run, in
`tests/registry/limits_check.sh`:

    FAIL: [code] src/parse/syntax_dump.c:66:#define MASK_MAX 8
          -- 'MASK_MAX' is neither a limits.def row nor on the cited allowlist

`put_mask`'s select-then-join needs a compile-time array bound, and the first
spelling was a bare numeric define. The check is RIGHT, on both halves of
D90's boundary as the coding guide §1.8 states it: a bare numeric define is
exactly what that detector is for, AND a scratch-array bound is not a
`limits.def` row either (L3-F6 declines to propose 94 of them). Neither arm of
"add a row" or "add an allowlist entry" is the correct answer.

**The bound is DERIVED instead**: `NELEMS(flavour_names) + NELEMS(engine_names)
+ NELEMS(flag_names)`, the SUM of this file's three mask tables, which is
trivially an upper bound on any one of them, is a compile-time expression
rather than a literal, and needs no number updated anywhere when a table grows.
There is no constant left for the detector to have an opinion about.

### 7.2 OWED — the full `make test`

Launched backgrounded as this lane's LAST act, to
`build/w1kit_test.log`, ending in a literal `TEST_RC=<n>` sentinel line. Poll
the log tail for it.

**Known pre-existing red on this box, NOT this lane's**: the darwin
`inline_capability` nm-probe FAIL, which carries `TEST_RC=2`. A second
pre-existing red this tree may show is `test-anchored-match`'s
`run_anchored_diff.sh` (`tt4m_time.md`'s own finding: 26 patterns whose emitted
C does not compile under the harness's `-Werror` flags, identical in both of
that memo's runs). Neither is attributable here — stages 1-2 move no emitted
byte, proven by §5.

---

## 8. WHAT THE CHARTER GOT WRONG, COLLECTED

Stated as a list because a wave-2 lane will read the charter and not this
report unless the list is short enough to carry.

1. **§2.2(4): `sb_field` at the registry dumps is a contract break.** 150 data
   rows carry a raw backslash. Two vocabularies, one tail. §0.
2. **§2.2(4)'s signature is incomplete**: `put_text` is LENGTH-based with two
   non-NUL-terminated call sites, so the escape needs an `n` form.
3. **§2.2(7)'s `cli_err` has a `where` parameter with zero callers**, and its
   `format(printf, 3, 4)` attribute does not match its own signature (the
   format is argument 2). §4.
4. **§3 stage 1's "wrap `put_escaped`, which takes rxt_source.c's anchors to
   0" is not available.** S200's anchor quotes the BODY, which moves under any
   spelling — wrapper or not. The relocation is still nearly free, but for
   method rule (ii)'s reason (verbatim, same column) rather than for the
   charter's. §6.
5. **L10-2's severity is LATENT, not live** (35% and 8% headroom), and
   `pcrec_enc_names`' defect is a DANGLING SEPARATOR rather than the
   "silently drops" the charter records. §3.
6. **The anchor population is a floor, as the synthesis says**: 266 rows here
   against the charter's 261, and every identifier this wave moves has ZERO
   rows against it.
7. **A FRESH INSTANCE FOR Q6 / L3-F1, found by accident.** After deriving the
   bound (§7.3) the check fired a SECOND time — on the COMMENT explaining why
   the constant had been removed, because that comment quoted the rejected
   define in its declaration's own spelling and `limits_check.sh` reads the
   file's raw lines without skipping comment text. L3-F1 characterises this
   detector by what it MISSES (a name-keyed filter blind to `C_MEMCHR`,
   `SIZE_TERM_BAR_DEFAULT`); this is the other direction — what it FALSELY
   CATCHES. A wave-4 lane inverting the filter per Q6 should fix both, and a
   comment-skipping pass is the cheaper half. Worked around here by rewording
   (the comment now says what happened without spelling the directive) and
   flagged at the site so the next editor of that comment does not reintroduce
   it; the check itself is untouched, since changing a check needs its own
   failing-direction story and that is not this lane's row.

**Held:** the charter's stage ORDER, its abi verdicts (both NOT abi events,
confirmed by measurement rather than assumed), its byte-neutrality methodology,
its `put_text`-stays-separate ruling, its identification of the `\xNN` tail as
the shared thing, and its stage-2 mechanical-only discipline.

---

## 9. WHAT IS NOT SETTLED

1. **The two big rows keep their per-column shape** (§1.2). If wave 2's
   event-stream renderer wants a uniform row layer, that is the change that
   makes a cells array natural for them, and it should ride that wave rather
   than this one.
2. **`syntax_dump.c`'s family-members loop** (`:521-535`) is a sixth separator
   loop that `sb_join` cannot take: it counts and classifies as it goes, so it
   has no array to hand over. Left alone; named so it is not mistaken for an
   oversight.
3. **The two piecewise CLI message builders** (§4) are the residue of stage 2.
   Routing them through `cli_err` needs a buffer; whether that is worth it is a
   wave-4 question (the `cli_parse` table is that wave's item anyway).
4. **`sb_row`'s numeric cells use small stack locals.** They are provably safe
   and are not the K38 class, but they ARE three more fixed buffers in a tree
   whose wave-2 acceptance criterion counts them. They are in `src/parse/`, not
   in the two emitters, so they do not touch stage 3's population — stated here
   so a wave-2 census does not find them and wonder.
5. **This lane did not run `make mech` in full**, so the only rows re-verified
   are the two it disturbed.
