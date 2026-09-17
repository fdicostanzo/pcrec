# LENS 10 — EMISSION-KIT UNIFICATION: THE WAVE 1 CHARTER

Lane `lens10kit` (opus, review + measurement), 2026-09-17, against `main` at
`7d444f9e`. Charter: `docs/dev/reviews/code_review_criteria_draft.md` lens 10,
broken out as likely REFACTOR WAVE 1. Predecessor map: lens 2's
`lens2_domain_tool_separation.md` (§8 addresses this lane directly); lens 3's
`lens3_config_centralization.md` §F6; lens 1's
`lens1_semantic_duplication.md` §X8 and §4.

**Nothing under `src/`, `cli/`, `lib/` or `tests/` was written or run. No
`make`.** Every number below is a grep or a read-only script over the
committed source; the scripts are in `lens10_evidence/` beside this file and
each states its own blind spots.

---

## 0. THE HEADLINE

**The D77 measurement lens 2 named comes back 1** — one run of ≥5 consecutive
`sb_*` calls emitting a contiguous prefix-only literal block, in both emitters
combined, and that one run performs **zero** prefix substitutions. **The
template layer stays OUT of wave 1**, which is what lens 2 leaned toward, but
**not for lens 2's reason, and its supporting number is wrong by roughly half.**

Three findings shape the charter, in descending order of how much they change it:

- **F1 — the metric measured a shape the code has already eliminated.** The
  emitters do not write contiguous literal blocks as runs of calls; they write
  them as ONE `sb_printf` with a multi-line concatenated format literal. There
  are **28 such single-call blocks spanning ≥5 source lines** that a
  `$`-template could replace as-is, the largest being 369 source lines / 8,884
  emitted bytes (`emit_dfa.c:681`). Counting *calls in a row* finds 1 of them,
  because they are all one call each. §1.3.

- **F2 — L2-3's "652 `%s_` substitutions, every one of those is
  `pcrec_enc_emit_text`'s `$` performed by hand" is not what 652 counts.** The
  652 reproduces exactly (`grep -o '%s_' | wc -l`), but positional pairing of
  conversions to varargs shows **306 of 584 pairable occurrences (52.4%) bind
  the prefix**; the other 278 bind the *uppercased* prefix, a machine name, a
  table tag or a function name — none of which a `$`-only interpolator can
  produce. And of the 771 `sb_*` call statements in the two emitters, **460 are
  MIXED** (they carry at least one non-prefix substitution) and hold **49,749 of
  the 77,258 literal bytes**. A `$`-template cannot replace 64% of the emitted
  literal text without a second placeholder and a formatter, which is a
  different primitive from the one lens 2 proposed reusing. §1.5.

- **F3 — the fragment layer's correctness payoff is LATENT, not live, and lens
  2's proposed acceptance number would pass before the wave ran.** Over the 43
  `snprintf` writes into a literal-sized buffer in the two emitters, **zero can
  provably truncate at a legal maximum-length (60-byte) `-p` prefix** under a
  deliberately weak lower bound; the tightest margin in the tree is **9 bytes**
  (`emit_vm.c:10384`, `gst_param[96]`). Lens 2's step-3 acceptance — *"provably
  clean at every one of the 49 hand-sized sites"* — is already true at
  `7d444f9e`. A wave acceptance criterion satisfied by the branch point is the
  K35 shape. §4.1 supplies the criterion that is not. **And the one existing
  long-prefix control compiles the pattern `a`** (`tests/cli/run_cli_tests.sh`
  case 3), a trivial DFA artifact that reaches essentially none of
  `emit_vm.c`'s 40 literal-sized buffers — so the population L2-1 is about has
  never been exercised at a long prefix at all. §4.2.

The charter that follows therefore **keeps lens 2's migration ORDER** (it is
right, and the anchor distribution still justifies it) and **changes three
things**: the template stage is closed rather than deferred, the fragment
stage's severity and acceptance are restated on measured ground, and a new
stage 0 is inserted because the fragment stage cannot be validated without it.

---

## 1. THE MEASUREMENT (deliverable 1; D77)

### 1.1 What lens 2 asked for

> *"Count the runs of ≥ 5 consecutive `sb_puts`/`sb_printf` calls emitting a
> contiguous literal block with only the prefix varying. If that population is
> small, the change is not worth an abi event and the honest answer is do not
> do it; if it is large, the number is the argument."*
> — `lens2_domain_tool_separation.md` §2.4 step 4

Operationalised (`lens10_evidence/count_runs.py`), with every choice stated
because each one can be argued with:

- **A CALL** is `sb_puts` / `sb_printf` / `sb_putc` in **statement position**
  (the preceding non-space/comment code character is `;` `{` `}` `:` `)`, or
  the keyword `else`/`do`). This rejects expression uses.
- **GUARDED**: a call reached through `if (…)` / `for (…)` / `while (…)` /
  `else` / `do` is counted but may neither join nor head a run — a `$`-template
  block is one unconditional text blob.
- **CONTIGUOUS**: two calls are adjacent iff the text between the `;` of one
  and the start of the next is whitespace and/or comments only. Any other token
  breaks the run. They must also target the same `StrBuf`.
- **ONLY THE PREFIX VARYING**: a call qualifies if it is `LIT` (a string or
  char literal, no conversions) or `PFX` (every conversion is `%s` and every
  vararg is a prefix expression — `p`, `v->p`, `v.p`, `f->p`, `prefix`,
  `cx->opt->prefix`, `pfx`, `e->p`; `emit_dfa.c:4262-4263`'s `VROW`/`VTBL`
  arg-pair macros are expanded before pairing).

**Instrument cross-check (A5).** The script finds **330 calls in
`emit_vm.c` and 441 in `emit_dfa.c`** — byte-for-byte lens 2's own independent
grep census (§1.0). Two instruments, two methods, same numbers.

### 1.2 The answer

| | `emit_vm.c` | `emit_dfa.c` | both |
|---|---|---|---|
| call statements | 330 | 441 | 771 |
| classified `LIT` | 93 | 171 | 264 |
| classified `PFX` | 17 | 13 | 30 |
| classified `OTHER` | 220 | 257 | 477 |
| maximal runs | 70 | 129 | 199 |
| **runs of length ≥ 5** | **1** | **0** | **1** |
| calls inside those runs | 9 | 0 | 9 |

Run-length distribution — `emit_vm.c`: 65×1, 4×2, 1×9. `emit_dfa.c`: 122×1,
6×2, 1×3. **The longest run in `emit_dfa.c` is three calls.**

*(The `LIT` total here is 264 and in §1.3's table it is 255. Not an
inconsistency: this classifier admits `sb_putc` with a char literal as `LIT`,
and §1.3's — which is about the size of a literal BLOCK — routes every
`sb_putc` to its `non-literal format` row instead. Both tables sum to 771.)*

The one qualifying run is `emit_vm.c:7807-7815`, nine `sb_puts` calls writing
the VM listing's header comment. Every one is a pure literal; the run performs
**zero** prefix substitutions, so it is not a template candidate at all — it is
a *concatenation* candidate (nine `sb_puts` that could be one).

**So the population lens 2's metric asks about is 1, and that 1 is not of the
kind the metric was looking for. On lens 2's own stated decision rule, the
answer is: do not do it.**

### 1.3 Why the answer is 1 — F1, the metric and the code disagree

The emitters already merged their literal runs. A contiguous block of emitted
text is written as ONE call with a multi-line concatenated C string:

```c
    sb_printf(c,
        "/* ---- THE OFFSET-k CANDIDATE-START SKIP -------------------------\n"
        " * Every match of this pattern carries a byte from a known set at each\n"
        …
        " *\n");                              /* emit_dfa.c:4710, 7 lines */
```

Counting *calls in a row* cannot see this. Counting the **literal block one
call carries** can. Per-call (`lens10_evidence/count_tmpl.py`), over the same
771 calls:

| bucket | calls | literal bytes | prefix varargs |
|---|---|---|---|
| `LIT` (no conversions at all) | 255 | 26,035 | 0 |
| `PFX-ONLY` (all conversions `%s`, all varargs the prefix) | 30 | 1,474 | 35 |
| `MIXED` (≥1 non-prefix substitution) | 460 | 49,749 | 276 |
| non-literal format (a `char`, or a variable format) | 26 | — | — |
| **total** | **771** | **77,258** | **311** |

And the population lens 2's step 4 was actually trying to find —
**single-call literal blocks spanning ≥5 source lines that a `$`-template
replaces as-is** — is **28**, of which 27 are `LIT` and one is `PFX-ONLY`:

| file | line | source lines | emitted bytes | prefix subs |
|---|---|---|---|---|
| `emit_dfa.c` | 681 | **369** | 8,884 | 0 |
| `emit_dfa.c` | 6166 | 22 | 1,215 | 0 |
| `emit_vm.c` | 10648 | 14 | 819 | 0 |
| `emit_dfa.c` | 546, 4726 | 12 | 465, 525 | 0 |
| `emit_dfa.c` | 7021 | 10 | 564 | 0 |
| … 21 more at spans 5–9 … | | | | |
| `emit_vm.c` | 11305 | 5 | 253 | **2** |

`emit_dfa.c:681` (`emit_rx_abi_types`) is a 369-line, 8,884-byte `sb_puts` of
the `rx_abi.h` contract with **no substitutions whatsoever**. It is already
exactly what `enc.h:18-23` argues for (*"a backend is a string and a backend
author writes C, not emitter code"*) — a verbatim C blob in a string literal —
and it needs no interpolator to be that.

**The finding, stated generally, because it outlives this charter: a proxy
metric that counts the SYMPTOM of a shape (many small calls) goes stale the
moment somebody fixes the symptom by hand, and then reports the underlying
population as absent.** The 28 blocks were there the whole time; lens 2's
counter would have returned 1 in every era since the emitters were written.

### 1.4 What the template would actually have to be

Of the 28 blocks, **27 carry no substitution at all** — for those,
`pcrec_enc_emit_text` and `sb_puts` are the same function, and converting them
buys a `$` that is never used. The entire population where the *interpolation*
is the point is **30 `PFX-ONLY` calls carrying 35 prefix substitutions and
1,474 emitted bytes**, and 28 of those 30 are a single source line long.

The readability win lens 2 correctly identified is real and it lives in the
**MIXED** bucket — 460 calls, 49,749 bytes, the long `sb_printf` calls whose
format a reader must mentally reassemble against a positional argument list.
**But `pcrec_enc_emit_text` cannot reach that bucket.** It substitutes one
placeholder with one string and formats nothing. Reaching MIXED needs a
*different, larger* primitive (named placeholders and conversions — a template
engine), which is a design event several orders of magnitude above the
seven-line function lens 2 proposed promoting.

### 1.5 F2 — L2-3's 652, decomposed

`grep -o '%s_' | wc -l` gives **347 + 305 = 652**, reproduced exactly. Pairing
conversions to varargs positionally (`lens10_evidence/decompose_652.py`, with
`VROW`/`VTBL` expanded — without the expansion five calls do not pair and 60
occurrences are lost):

```
grep -o '%s_' total:                   652
accounted by positional pairing:       584   (0 unpairable calls)
  --> bound to a PREFIX expression:    306   (52.4%)
  --> bound to something else:         278
residual (652 - 584):                   68
  --> inside an `snprintf` format:      45   (the M2 fragment-buffer sites)
  --> inside a comment:                 11
  --> in an sb_* arg, not a paired conversion: 12
```

The non-prefix 278, by binding: `v.up`/`v->up`/`upper`/`g->upper` (the
**uppercased** prefix) 139 · `f->dir->c.name` 49 · `m` (machine name) 45 ·
`rv` 16 · `name`/`fn`/`guard`/`searchfn`/`matchfn`/`matchcapsfn`/… 29.

Two consequences for the charter. **(a)** The argument's magnitude halves:
306, not 652. **(b)** More importantly, the *uppercased* prefix is the single
largest non-prefix binding (139), and it is a **second derived name from the
same source** — which is a real finding about the kit (§2.2 item 3) and is
invisible if the 652 is read as one number.

### 1.6 VERDICT on the template layer

**CLOSED, not deferred.** Lens 2 left step 4 as "recommend against pending the
measurement"; the measurement has been taken and it does not turn. Stating the
verdict three ways so a later wave does not reopen it by accident:

1. On lens 2's own decision rule and metric: the population is **1**, and that
   one performs no substitution. Do not do it.
2. On the corrected metric (single-call blocks): the population is **28**, but
   **27 of them substitute nothing**, so a template adds a placeholder
   character to text that has no placeholder. The interpolation population is
   **30 calls / 1,474 bytes**, 1.9% of the emitted literal text.
3. On the population where the readability win actually is (MIXED, 460 calls,
   64% of emitted literal bytes): `pcrec_enc_emit_text` **structurally cannot
   reach it**. Reaching it is a new template engine, which is a DESIGN-EVENT
   with no measured need behind it (D77).

And the price is unchanged and is the highest this tree charges: any moved
whitespace byte is emitted scaffolding, so it is a D76/D94 abi bump plus a
grep-found re-pin of every reader of `26` — the ritual that missed a fifth
reader in `match_api.md` once (D94), and that `battriage_report.md` records
**cannot** find `run_cpset_structure.sh`'s `EMITTED_BYTES` manifest at all
because those rows never cite an abi digit.

**What would reopen it (name the measurement, not a date — D77):** a *different*
proposal, for a template primitive with named placeholders and conversions,
carrying a measured statement about the MIXED bucket. The number that would
justify it is not a run length; it is a defect or comprehension cost
attributable to positional-argument reassembly in those 460 calls, and nobody
has one.

### 1.7 The instrument's blind spots, stated

- **Prefix-expression set is a closed list.** A prefix reached by a spelling
  not in the eight listed scores as non-prefix, biasing `PFX`/`PFX-ONLY`
  **down** and `MIXED`/`OTHER` **up**. It was built by dumping every
  `sb_printf` vararg expression by frequency and reading the top 40; a spelling
  below that cut could be missed. Direction of the error is against my verdict
  being wrong in the risky direction only if a missed spelling is common, and
  the top-40 dump's tail is at n=4.
- **Arg-pair macros are handled by a two-entry table** (`VROW`, `VTBL`). A
  future arg-pair macro would silently unpair its call; `decompose_652.py`
  prints the unpairable count (currently 0) so this fails loudly rather than
  silently.
- **`OTHER-NONLITERAL` (26 calls) is not decomposed.** These are `sb_putc` with
  a non-literal argument and `sb_puts`/`sb_printf` with a variable format —
  they carry runtime text and are template-hostile by construction, so they are
  excluded rather than analysed.
- **Emitted-byte counts treat `\xNN`/`\n` as one byte and `%s` as zero.** They
  are lower bounds on emitted size and are used only for relative weighting.
- **The census is the two emitters only.** `syntax_dump.c` (153 `sb_*`) and
  `rxt_source.c` (126) were not run through the run-length counter, because the
  template question lens 2 raised is about `--prefix` interpolation and neither
  file interpolates a prefix.

---

## 2. THE KIT API (deliverable 2)

### 2.1 What survives from lens 2's sketch, and what does not

Lens 2 proposed five functions. After the measurement:

| lens 2's item | verdict here |
|---|---|
| (1) `StrBuf` unchanged | **KEEP.** It is the base and no finding is filed against it. |
| (2) `txt_f` — arena-owned formatted fragment | **KEEP, renamed and re-scoped.** §2.2 item 1. |
| (3) `txt_tmpl` — promote `pcrec_enc_emit_text` | **DROP.** §1.6. The function stays where it is, serving its two call sites, and `enc.h`'s own rationale for it stays true of it. |
| (4) `txt_field` / `txt_row` / `txt_join` | **KEEP** `txt_field`/`txt_row`; **KEEP** `txt_join`. §2.2 items 4–6. |
| (5) `cli_err` — CLI diagnostic channel | **KEEP** unchanged. §2.2 item 7. |
| — | **ADD** item 2, `txt_name` / `txt_upper` — forced by §1.5(b). |
| — | **ADD** item 3, the stamp pair, shared with lens 1's X8. |

### 2.2 The functions

Home: grow `src/core/sb.c` and its `internal.h:60-67` block rather than mint a
file. Rationale: every function below is ≤ 20 lines, they all sit on `StrBuf`
or `Arena`, and D2 (plain GNU make, on purpose) makes a new `.c`/`.h` pair a
Makefile edit for no capability. `cli_err` is the exception and is CLI-local by
design (the library does not print — §1.2's stdio confinement is a separation
that is already right and the kit must preserve it).

---

**(1) THE FRAGMENT — arena-owned formatted text that cannot truncate.**

```c
/* Format into arena-owned storage sized exactly to the result. Truncation is
 * impossible BY CONSTRUCTION rather than by a per-site size argument.
 * Never freed by the caller; dies with the compile's arena.
 * On allocation failure: routes through ctx_nomem via the arena, i.e. the
 * caller's setjmp, exactly as arena_alloc does today (K7's discipline). */
const char *sb_fragf(Arena *a, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
```

*Semantics.* `sb_printf`'s own body (`sb.c:49-62`) with the destination
changed: `va_copy`, a measuring `vsnprintf(NULL, 0, …)`, ONE `arena_alloc` of
exactly `n+1`, a second `vsnprintf`. ~12 lines. `n < 0` aborts as `sb_printf`
already does.

*What it replaces.* The M2 idiom — `char NAME[N]; snprintf(NAME, sizeof NAME,
…); … sb_printf(c, "%s", NAME)` — at the **43** sites where an `snprintf`
writes an in-scope literal-sized buffer in the two emitters, plus
`vm_rolef` (`emit_vm.c:754-770`), which is the same function already, built on
a `char buf[160]` and **truncating anyway** at `:764-765`.

*D82 bound 3 (≥2 existing implementations) — verified.* `vm_rolef`
(`emit_vm.c:754`) and `derived_name` (`emit_dfa.c`) are two existing
arena-owned name/fragment builders; the 43 stack-buffer sites are a third
implementation written 43 times. **Bound satisfied.**

*Per-site migration shape.* **MECHANICAL where the buffer is written once and
read once** (the majority): delete the declaration, replace
`snprintf(buf, sizeof buf, F, …)` + later `%s`-of-`buf` with an inline
`sb_fragf(arena, F, …)`. **JUDGED where the buffer is written conditionally and
read unconditionally** — e.g. `emit_vm.c:10770-10790`'s
`accept_tr`/`fail_tr`/`exhaust_tr`, each initialised to `""` and then
conditionally filled, whose *empty* value is load-bearing (the comment at
`:10792-10795` says so: the untraced artifact's bytes stay identical "because
the insert is simply empty"). Those become `const char *accept_tr = "";` and a
conditional assignment — still mechanical in shape, but each one must be read,
because the empty default is a byte-identity contract.

---

**(2) THE DERIVED NAME — one prefix, two spellings.**

```c
/* The artifact's prefix-derived identifier: `<prefix>_<suffix>`. */
const char *sb_name(Arena *a, const char *prefix, const char *suffix);
/* The same, uppercased: `<PREFIX>_<SUFFIX>` — the stamp/macro namespace. */
const char *sb_upper(Arena *a, const char *prefix, const char *suffix);
```

*Why this exists and lens 2's sketch did not have it.* §1.5(b): the
**uppercased prefix is the largest single non-prefix binding in the whole
`%s_` census (139 of 584)**, and it is not an independent fact — it is the
prefix, transformed. Today that transformation lives in `prefix_upper`
(`emit_dfa.c:659`) writing into `char up[80]` on `Vm` (`emit_vm.c:376`) and
into local buffers elsewhere, and the two spellings then travel as two
independent strings through every emitter function. `sb_upper` makes them one
derived fact with one derivation, which is `learnings.md` §3's one-derivation
rule applied to a name.

*D82 bound 3 — verified.* `derived_name` + `prefix_upper` (`emit_dfa.c:659`)
are two existing implementations, and `Vm.up` is a third cached one. **Bound
satisfied.**

*Migration shape.* **JUDGED, and this is the one item I recommend NOT
attempting in wave 1** — see §3, stage 3's scope note. `Vm.up` is a struct
field read at 110 sites; retiring it is a data-flow change, not a text change.
`sb_name`/`sb_upper` should LAND in wave 1 as the substrate for item 3, with
`Vm.up` left in place and migrated later or never.

---

**(3) THE STAMP — shared with lens 1's X8.**

```c
void sb_stamp_str (StrBuf *c, const char *upper, const char *name, const char *value);
void sb_stamp_int (StrBuf *c, const char *upper, const char *name, long long value);
void sb_stamp_bool(StrBuf *c, const char *upper, const char *name, bool value);
```

*What it replaces.* Lens 1 X8's census: **52 sites in `emit_vm.c`, 21 in
`emit_dfa.c`** matching `sb_printf(.*"#define %s`, each a bespoke one-liner.

*D82 bound 3 — verified* at 73 existing implementations.

**This item is lens 1's finding, not mine, and it is listed here only because
it is a text-emission primitive in the same two files and a wave that moves
those lines twice pays the anchor re-verification twice.** Disposition is a
synthesis question: either X8 rides wave 1's stage 3 or wave 1 does not touch
stamp lines at all. **My recommendation: it rides**, because the two stages'
blast radii are the same 123 anchors and the same 7 source-grepping checks, and
paying that once is strictly cheaper than paying it twice. Flagged for the
manager rather than assumed.

---

**(4)/(5) THE FIELD AND THE ROW.**

```c
/* One TSV field, framing-safe: \\ \t \n \r escaped, then <0x20|0x7f -> \xNN. */
void sb_field(StrBuf *sb, const char *s);
/* `ncell` escaped fields, tab-joined, newline-terminated. */
void sb_row(StrBuf *sb, const char *const *cells, int ncell);
```

*What they replace.* `rxt_source.c`'s `put_escaped` (`:3743`, 12 sites) is the
implementation, promoted verbatim; `syntax_dump.c`'s TSV path (17 explicit
`sb_putc('\t')`, `:208-264`, fields written through `put_str` which escapes
nothing); `axes_dump.c`'s `axis_row` (`:253`, 13 params) and `emit_pred_row`
(`:359`); `limits_dump.c`'s `limit_row` (`:46`); `schema_dump.c`'s inline rows.

*D82 bound 3 — verified* at 5 existing row emitters and 2 existing escapers.

*NOT merged:* `put_text` (`syntax_dump.c:1195`) stays separate. It
deliberately passes `\` through because its grammar is human-readable
`--explain` output (`:1193-1194`), and lens 2 is right that these are two
correct policies for two formats. What is shared is only the `\xNN` tail
(`syntax_dump.c:1200` vs `rxt_source.c:3758`), written twice.

---

**(6) THE JOIN.**

```c
void sb_join(StrBuf *sb, const char *sep, const char *const *names, int n);
```

*What it replaces.* `put_mask` (`syntax_dump.c:61`, 7 sites), `render_modules`
(`enabled.c:164`), `pcrec_enc_names` (`enc.c:52`), and `cli/main.c:1104-1113`
and `:1147-1155`. **D82 bound 3 — verified at 5.**

*This one is a bug fix, not a cleanup, and should be filed as one.* Three of
the five are bounded-buffer copies of one loop with three different and
undocumented over-long policies, and one of them is wrong in a way nothing
reports: `render_modules` (`enabled.c:180`) `continue`s past a name that does
not fit and keeps appending shorter later ones, so the result is an
**out-of-order partial list**, not a truncated prefix. `pcrec_enc_names`
silently drops. `sb_join` on `StrBuf` cannot do either.

---

**(7) THE CLI CHANNEL** — unchanged from lens 2's sketch.

```c
int cli_err(const char *where, const char *fmt, ...)    /* cli/ only */
    __attribute__((format(printf, 3, 4)));
```

Writes `"pcrec: "` (+ `" (<where>)"` when non-NULL), the message, a newline, to
stderr; returns 1 so every site stays `return cli_err(…);`. **D26: every word
of every message is unchanged, at every site.** D82 bound 3 — 76 existing
implementations.

### 2.3 What the kit deliberately is NOT

Carried forward from lens 2 §2.1, unchanged, and re-affirmed by my
measurement: no indentation manager (two forms, both trivial); **no
`emit_line()` wrapper** (it buys nothing `sb_printf` does not and would move
771 call sites in the two most anchored files in the tree for zero
capability); no merge of `put_text` and `put_escaped`; **and now, no template
layer** (§1.6). Lens 2's own rank-5 anti-finding stands: the four
`group_frac` 1.000 enum→string mappers in `syntax_dump.c` are **left alone**,
per D82 bound 3 and the D75 addendum.

### 2.4 Lens 3's F6 and D90 — judging the brief's claim

The brief asks whether this claim is true: *"your kit should retire the
buffers instead, e.g. arena- or sb-backed formatting with no fixed size, which
answers lens 3's F6 and lens 2's L2-1 in one move."*

**Verdict: true for L2-1, and for F6 it DISSOLVES the question rather than
answering it — which is better, and the difference matters for how the stage
is briefed.**

- **D90 compliance is not at issue, and lens 3 is right about that.** F6
  explicitly declines to propose 94 `limits.def` rows, because a scratch-buffer
  size is not "a value a pattern can be measured against" — the phrase
  `limits_check.sh`'s own allowlist uses. `sb_fragf` needs **no** size
  constant at all, so it neither adds a `limits.def` row nor adds a bare
  `#define`. It is the one disposition that is clean under D90 in both
  directions.
- **F6's actual finding is a QUESTION**: *"which of these 94 buffers hold text
  whose length is bounded by a `limits.def` row, and of those, which fail to
  derive from it?"* Retiring the buffer does not answer that question for any
  site; it makes the question unaskable, because there is no size to derive.
  **Those are different outcomes and a brief that conflates them will produce
  a lane that thinks it has audited something it has only deleted.**
- **The practical consequence:** the audit F6 proposes (name the longest
  string each writer can produce; (a) derive from the governing limit, or (b)
  state why the bound is local) is **not a prerequisite** for the fragment
  stage and should not be scheduled as one. It is, however, exactly the
  instrument that produces the stage's *rollback evidence* — see §3 stage 3.
- **One caveat on scope.** F6 counts **94** buffers across `src/` + `cli/`;
  my own count in the two emitters is **48** literal-sized declarations at code
  positions (40 `emit_vm.c`, 8 `emit_dfa.c`) against **29** sized by
  `PCREC_MAX_EMIT_NAME_LEN` (16 and 13). Lens 2's figures are 49 and 34. The three instruments differ on
  declaration-matching detail; **all three agree on the shape and none of them
  should be cited as an exact site list without being re-run**. Wave 1 touches
  only the emitters' 48, and the remainder elsewhere in `src/`+`cli/` are
  out of wave 1's scope.

---

## 3. THE STAGE PLAN (deliverable 3)

Ordered by A3 check-coupling cost ascending, which is lens 2's order and is
right. Every anchor number below was **re-grepped by this lane**
(`lens10_evidence/anchor_census.py`), and it does not match lens 2's, for a
reason that matters:

**A3 CORRECTION — 261 rows carry 277 ANCHORS.** Sixteen rows carry a second
anchor (`SAB_FILE2`/`SAB_BEFORE2`), and each anchor is an independent verbatim
source-text block that must match its file byte for byte, so each is
independently re-aimable and must be counted independently. Counting rows
undercounts the re-aim burden by 16.

| `SAB_FILE` | **anchors** | what they quote |
|---|---|---|
| `src/gen/emit_vm.c` | **94** | TEXTCALL 10, SNPRINTF 2, BUFDECL 2, other 81 |
| `src/gen/emit_dfa.c` | **29** | TEXTCALL 8, BUFDECL 1, other 21 |
| `src/parse/rxt_source.c` | 3 | TEXTCALL 1, other 2 |
| `src/parse/syntax_dump.c` | 1 | other 1 |
| `src/parse/schema_dump.c` | 1 | TEXTCALL 1 |
| `src/core/sb.c`, `enc.c`, `cli/main.c`, `axes_dump.c`, `limits_dump.c`, `enabled.c` | **0** | — |
| everything else | 149 | — |

**123 of 277 anchors (44.4%) live in the two emitters.** Lens 2's "24 anchors
quote an `sb_*` or `snprintf` call verbatim" does not reproduce: **18 quote a
text call** (`sb_puts`/`sb_printf`/`sb_putc`), **2 quote an `snprintf`**
(`S106_caseless_field_ignored.sh`, `S143_call_return_no_restore.sh`), and **3
quote a `char NAME[…]` declaration** (`S114_resolution_first_by_number.sh`,
`S143_…`, `S74_reverse_termination_blind.sh`). The distinction is
load-bearing: **the fragment stage's DIRECTLY-broken anchor set is the
`snprintf`+`BUFDECL` group — 4 sabotage rows — not 24.**

**Source-text-reading checks (re-grepped).** Seven scripts read `src/gen/`
source text: `run_atomic_identity.sh`, `run_backref_identity.sh`,
`run_codegen_tests.sh`, `run_cpset_structure.sh` (**24 reads — by far the most
coupled single file in the tree**), `run_lookaround_identity.sh`,
`run_recursion_identity.sh`, `run_search_pinned.sh`. Lens 2 named five of these
and missed `run_codegen_tests.sh` and `run_recursion_identity.sh`.
`axes_registry_check.sh` references `src/gen/` paths by a non-text mechanism.
**All seven must be read BEFORE any stage that moves emitter source text, not
after they go red** — `bat4triage_report.md` records `run_cpset_structure.sh`'s
`[1c]`/`[2d]` needles going red on exactly this, *"a check-staleness class, not
a correctness regression."*

---

### STAGE 0 — the long-prefix corpus control. **NEW; a precondition, not a cleanup.**

**Why it exists.** §4.2: the only long-prefix check in the tree compiles the
pattern `a`. Stage 3 cannot be validated without a control that reaches the
sites it moves, and building that control after the migration means it has
nothing to compare against.

**What it is.** A read-only sweep, in the shape `cmtfix_report.md` and
`dialtrain_byteid.md` already established: compile every corpus
`pattern`/`pattern-esc` line at `-p rx` **and** at a legal 60-byte prefix, and
record, per pattern, whether each compiled and whether the 60-byte artifact
compiles under the harness's own `-Werror` flags. The BASELINE is the branch
point; the artifact is a committed TSV.

- **A3 anchors moved: 0.** Nothing under `src/`, `cli/`, `lib/` is touched.
- **abi verdict: NOT an abi event** (D76/D94 do not fire; no emitted
  scaffolding moves — indeed nothing is emitted that is kept).
- **Validation bar:** the sweep runs to completion and its row count equals the
  corpus's own `pattern`-line count, checked against the same number
  `run_rxtsource_tests.sh`'s census pins. A truncated sweep must be detectable
  by comparing the two, which is `tests/size/check_size_tripwire.sh`'s own
  guard shape.
- **Rollback:** delete a TSV.
- **This stage's OUTPUT is stage 3's acceptance criterion** and its result is
  independently interesting: if any pattern compiles at `-p rx` and fails at 60
  bytes, **that is a live K38 recurrence and a bug filed today**, before any
  refactor.

---

### STAGE 1 — the field/row layer (`sb_field`/`sb_row`) + `sb_join`.

Four dump files plus `enabled.c`, `enc.c`, `cli/main.c`.

- **A3 anchors: 2** — `syntax_dump.c` 1 (quotes non-text code),
  `schema_dump.c` 1 (`S241_schema_dump_handwritten.sh`, quotes a text call and
  **breaks directly**). `axes_dump.c`, `limits_dump.c`, `enabled.c`, `enc.c`,
  `cli/main.c` carry **zero**. Plus `rxt_source.c`'s 3 (1 TEXTCALL,
  `S200_rxt_pattern_unescaped.sh`) if `put_escaped` is moved rather than
  wrapped — **it should be wrapped, leaving `put_escaped` as a one-line
  forwarder, which takes that to 0.**
- **abi verdict: NOT an abi event.** `--list-*` output is not emitted artifact
  text; D76/D94 do not fire.
- **Byte-neutrality proof.** Not asserted — *measured*, by
  `--list-syntax`/`--list-limits`/`--list-axes`/`--list-schema`/`--list-source`
  output diffed byte for byte against the branch point's, for every dump and
  every flag combination the CLI accepts. The dumps are deterministic and take
  no input, so this is a complete control, not a sample.
- **The escaping is a BEHAVIOUR change and must be measured first, not
  assumed byte-neutral.** Stage 1's own precondition: does any string
  reachable by `axes_dump.c`, `limits_dump.c` or `schema_dump.c` contain a tab,
  newline or control byte today? If the population is zero the wave is
  byte-neutral and the escaping is insurance. **If it is non-zero the wave is a
  BUG FIX and must be filed as one before it is refactored** — the corruption
  is already diagnosed in a fourth file (`rxt_source.c:3735-3742`: *"emitted
  raw the field splits and every later column shifts on exactly those rows — a
  three-row-in-3,265 corruption, which is the size of finding a summary
  swallows"*).
- **Validation bar:** `make test-rxtsource` + `make test-registry` + `make
  test-cli` green; the dump byte-diff above; `make strict`.
- **Additional reader to check:** `run_rxtsource_tests.sh` asserts field counts
  per row and **has already gone stale once on exactly this kind of change** —
  `w23impl_report.md`'s `NF != 15` finding, whose failure message *"names a TAB
  in a field as the only possible cause"*, so a lane meeting that red will be
  sent to read the escape function. Read it first.
- **Rollback:** one revert; the primitives have no other callers yet.

---

### STAGE 2 — the CLI channel (`cli_err`).

- **A3 anchors: 0.** `cli/main.c` carries none.
- **abi verdict: NOT an abi event.**
- **Byte-neutrality proof:** `tests/cli/` pins the wording and D26 says the
  wording does not move. The existing suite IS the control; **no new
  measurement is needed and none should be invented.**
- **Validation bar:** `make test-cli` green with an unchanged check count;
  `make strict`.
- **Scope discipline:** a diff that changes one word of one message is out of
  scope for this stage. 76 sites, `"missing value for %s"` × 8 verbatim, 72
  hand-writing `"pcrec: "`. Purely mechanical substitution.
- **Rollback:** one revert.
- **Out of scope and filed separately:** `write_file` (`cli/main.c:292-299`)
  checks `fclose`'s return but not `ferror()` on the `fputs` that wrote the
  artifact — a short write on a full disk is reported only if it happens to
  surface at close. That is a bug, not a channel question, and it should not
  ride a mechanical wave.

---

### STAGE 3 — the fragment layer (`sb_fragf`, `sb_name`/`sb_upper`), and lens 1's X8 if it rides.

This is the wave's cost and, per §4.1, **not its correctness payoff**.

- **A3 anchors.** **Directly broken: 4 anchors in 4 rows** — the ones quoting
  an `snprintf` or a `char NAME[…]` declaration: `S106_caseless_field_ignored`,
  `S114_resolution_first_by_number`, `S143_call_return_no_restore` (one anchor
  quoting both) and `S74_reverse_termination_blind` (one anchor quoting a
  buffer declaration AND a text call). **In the blast radius and requiring re-verification: 123** (all
  emitter anchors), of which **18 quote a text call** and any whose block
  *abuts* a changed line must be re-verified rather than assumed. If X8 rides,
  add the anchors abutting the 73 stamp lines.
- Per `BOILERPLATE.md`: a re-anchor needs its **intent re-verified**, and
  anchors are copied from `git show HEAD:<path>` — **per-row human work, not a
  script.** Budget it that way.
- **abi verdict: NOT an abi event — and this is the property that makes the
  stage affordable.** A fragment that *cannot* truncate emits exactly what a
  fragment that *did not* truncate emitted, and §4.1 measures that no fragment
  truncates today. If a byte moves, the stage has a bug, not an abi bump.
- **HOW BYTE-NEUTRALITY IS PROVED — two independent instruments, because one
  of them is known to be blind here.**
  1. **The four standing byte-identity gates**
     (`tests/codegen/run_vm_identity.sh`, `run_recursion_identity.sh`
     comparison (A), `run_backref_identity.sh`, `run_atomic_identity.sh`) —
     free, already in `make test`, and they run at `-p rx`.
  2. **A full-corpus emit-diff at BOTH prefixes**, `cmtfix_report.md` /
     `dialtrain_byteid.md` methodology: baseline via `git archive` of the
     branch point, every corpus `pattern`/`pattern-esc` line compiled by both
     trees, byte-diffed — **at `-p rx` AND at the 60-byte prefix from stage 0.**
     The `-p rx` arm proves neutrality for the shipped configuration; **the
     60-byte arm is the only instrument that reaches the sites the stage
     moves** (§4.2), and it is the arm the standing gates cannot supply.
  * **Expected result: 0 movers on both arms.** `dialtrain_byteid.md`'s
    "1,500 movers, every one exactly +27 bytes" is the shape of a *reported and
    explained* mover set; this stage should have an empty one, and any mover is
    §4.1's finding rather than a delta to explain away.
- **Validation bar:** the two instruments above; `make test` green; `make
  mech` with the 5 re-aimed anchors DETECTED and the row count unchanged at
  261; `make strict`. Per `mechfix_report.md`, a MISSING suite log now scores
  ANOMALY rather than DETECTED — read the mech output for anomalies, not only
  for the verdict line.
- **The acceptance NUMBER** (replacing lens 2's, which §4.1 shows is already
  satisfied at the branch point): **zero literal-sized `char NAME[…]` scratch
  buffers remain in `src/gen/emit_vm.c` and `src/gen/emit_dfa.c`** — a grep,
  checkable in both directions, with a floor of 48 declarations at the branch
  point. It is a
  *completeness* criterion, which is what the stage actually delivers, rather
  than a *safety* criterion that was already true.
- **SCOPE NOTE — `Vm.up` stays.** `sb_name`/`sb_upper` land as the substrate
  for the stamp pair, and `Vm.up` (`emit_vm.c:376`, a `char up[80]` field read
  at ~110 sites) is **not** retired in wave 1. Retiring it is a data-flow
  change through the emitter's central struct, not a text change, and it does
  not share this stage's byte-neutrality argument. Naming it here so a lane
  does not scope-creep into it and so a later wave does not think it was
  forgotten.
- **Rollback shape.** The stage is decomposable **per call site**, which is its
  best property: every site is an independent `snprintf`→`sb_fragf`
  substitution, so a red bisects to one site and reverts to one site. It should
  be delivered as a sequence of commits grouped by emitter function, never as
  one squashed diff, precisely so that the full-corpus emit-diff can be run at
  a midpoint and the rollback granularity is one function.

---

### STAGE 4 — `emit_vm.c:7807-7815` and the 27 no-substitution blocks. **OPTIONAL, POLISH.**

The nine-`sb_puts` run §1.2 found, collapsed into one call. Byte-neutral by
inspection (nine adjacent literals concatenate to one literal), 0 anchors, 0
abi. Listed for completeness and because leaving it unlisted invites a later
lane to rediscover it and propose the template layer again. **The 27
no-substitution blocks are left exactly as they are** — they are already one
call each and already readable C-in-a-string.

---

## 4. RISKS (deliverable 4)

### 4.1 Truncation may be a PRESERVED BUG — the candidate list, and it is empty

The brief is right that this is the stage's sharpest hazard: *"K38's class
means truncation today can be a BUG being preserved; a site whose output
changes because the old code truncated is a FINDING."* Retiring a buffer
changes behaviour at exactly the sites where the buffer was too small, and such
a site's emitted bytes will move — so the byte-identity instruments will go red
for the RIGHT reason, and a lane that reads that red as "my refactor is wrong"
will paper over a live defect.

**I measured the candidate list** (`lens10_evidence/buf_risk.py`). The bound:

```
src/core/limits.def:133   PCREC_MAX_PREFIX_LEN    = 60
src/core/limits.def:134   PCREC_MAX_EMIT_NAME_LEN = 60 + 96 = 156
worst_case >= len(fixed format text) + 60 * (number of %s bound to the prefix)
```

Every other conversion scores **zero**, so this is a strict UNDER-estimate: a
site it flags can definitely truncate; a site it does not flag may still be
able to. **That asymmetry is deliberate — the output is a candidate list, not a
clean bill of health.**

| | |
|---|---|
| `char NAME[<literal>]` declarations at code positions, two emitters | **48** (40 + 8) |
| declarations sized `PCREC_MAX_EMIT_NAME_LEN` | **29** (16 + 13) |
| literal sizes at or above 156 (structurally safe) | **15 of 48** |
| `snprintf` writes into an in-scope literal-sized buffer | **43** |
| **provably truncating at a legal 60-byte prefix** | **0** |
| tightest margin measured | **9 bytes** — `gst_param[96]`, `emit_vm.c:10384`, worst case 87 |
| *(count caveat)* | the 48 counts FIRST declarators at code positions. A grep of `char NAME[<digit>` per LINE gives 53 in these two files, of which **6 are mentions inside comments**; conversely ~14 same-line continuation declarators (`char accept_tr[288], fail_tr[288], exhaust_tr[192];`) are buffer objects the declaration count does not separate. **48 declaration statements is the number to brief from; the buffer-object count is higher and no instrument here pins it exactly.** |
| second tightest | 10 bytes — `mrl_param[96]`, `emit_vm.c:10378`, worst case 86 |
| others with a prefix substitution | `fn[96]`/71, `cnt[192]`/93, `accept_tr[288]`/248 and /133, `pop_tr[352]`/307 |

**Consequences for the charter, in order of importance.**

1. **L2-1's severity should be restated.** Lens 2 files it CORRECTNESS-RISK on
   the strength of K38 being a recorded miscompile. K38 *was* a live
   miscompile; the cure was applied to 29 sites and the remaining 48 are, as
   measured, **all safe today at every legal prefix**. The honest severity is
   **MAINTAINABILITY with a latent CORRECTNESS-RISK** — the same disposition
   lens 2 itself gave L2-4, and for the same reason: a real invariant, unenforced.
2. **Lens 2's acceptance number cannot be used.** *"Provably clean at every one
   of the 49 hand-sized sites"* is true at `7d444f9e`, before the wave. A
   criterion the branch point satisfies measures nothing about the change —
   `learnings.md` §3's shape, and the reason §3 stage 3 proposes a completeness
   criterion instead.
3. **The stage's expected mover set is EMPTY, and that is now a prediction with
   a measurement behind it rather than a hope.** Any mover the stage 3
   emit-diff produces contradicts this table and is a FINDING to be filed
   before the stage lands — most likely as a site where a non-prefix `%s` (my
   bound scores it zero) carries more bytes than I could bound. **Named
   candidates, being the sites where a non-prefix substitution is doing the
   most work relative to headroom:** `accept_tr`/`fail_tr`/`exhaust_tr`
   (`emit_vm.c:10770`, 40 bytes of measured headroom on a 288-byte buffer),
   `pop_tr` (`:10870`, 45 on 352), and the `val[64]` family in the cursor and
   revdet rungs (`emit_vm.c:4216-4382`, `:5102-5106`), whose slot expressions
   are built by `vm_slot_expr`/`vm_slot_name` (`:855-953`) — the one site whose
   own comment (`:944-948`) says *"this file has already been bitten once by a
   too-small snprintf buffer."*
4. **`emit_vm.c:8165-8167` is the one recorded LIVE truncation and it is not in
   this table.** Its comment describes truncating a listing column
   (*"TRUNCATED it to `slot_values[2] <- scan_`"*) above a `char slot[48]`.
   That truncation is a function of SLOT NAME length, not prefix length, so my
   prefix-bound instrument is structurally blind to it. **A `--emit-listing`
   artifact's columns are emitted text**, so retiring `slot[48]` will move
   listing bytes on any pattern with a long enough slot name. This is the one
   site I can name in advance as an expected, legitimate mover, and the lane
   must decide deliberately whether the listing's column width is a contract
   (the same comment warns *"A rename that moves emitted names has to check the
   listing's column widths too"*) — **escalate rather than fix in-flight.**

### 4.2 F3b — the K38 control's reach is ~zero, and nothing measures that

`tests/cli/run_cli_tests.sh` case 3 (`:195-216`) is the tree's only long-prefix
check. It compiles a 60-character prefix and asserts the generated code
compiles — **on the pattern `a`**. A single literal compiles to a trivial DFA
artifact and reaches none of `emit_vm.c`'s 45 literal-sized buffers, which live
in the cursor, revdet, counter, trace and listing rungs.

So: the cure for K38 was applied to 29 sites, 48 still guess, and **the check
that exists to stop K38 recurring cannot see any of the 48.** This is the
[MECH-REACH] shape — a witness that does not reach its site — and it is worth
more than the refactor it blocks. **It is a finding to file independent of
whether wave 1 ever runs**, and stage 0 is its remedy.

### 4.3 The `emit_vm.c` second-pass collision — sequencing

Lens 1 §4 names the need for a second pass and is explicit about what it did
not review: *"`src/gen/emit_vm.c` below the stamp and slot layers … I examined
its stamp emission (X8), its saturating arithmetic (X3) and its walk instances
(X1) and **did not review its rung/slot/frame emission at all.** This is the
single largest unreviewed surface in the primary tier … **I am naming the
need.**"*

**That unreviewed surface is exactly where stage 3 works.** 40 of the 48
literal-sized buffers are in `emit_vm.c`, and the dense clusters lens 2
located — `vm_slot_expr`/`vm_slot_name` (`:855-953`), the four call-site
save/restore blocks (`:6818`, `:6942`, `:7009`, `:7023`), the cursor and revdet
rungs (`:4078-4382`, `:4857-5138`), the trace block (`:10770-10880`) — are all
rung/slot/frame emission.

**Proposed sequencing, and the reason for each ordering:**

1. **Lens 1's second pass runs BEFORE stage 3, and stages 0/1/2 do not wait for
   it.** Stages 0, 1 and 2 touch no `emit_vm.c` line (stage 0 touches no source
   at all), so they are independent and can start immediately.
2. **The second pass is read-only and its inputs are the current lines.** If
   stage 3 lands first, the second pass reviews migrated code, and its clone
   detector's shingles over those functions are invalidated — the review would
   be of my refactor rather than of the original design, which is the wrong
   thing to review.
3. **The second pass may change what stage 3 should do.** If it proposes an
   extraction over the cursor/revdet rungs, migrating those sites to `sb_fragf`
   first means migrating them twice and re-verifying the same anchors twice.
4. **X8 (the stamp pair) is the one item that should ride stage 3 rather than
   wait**, because lens 1 has already reviewed the stamp layer and named its
   extraction, and it shares stage 3's 123 anchors and 7 checks exactly. See
   §2.2 item 3; flagged for the manager, not assumed.

### 4.4 Smaller risks, named

- **`run_cpset_structure.sh` does 24 source-text reads** — more than the other
  six `src/gen/` readers combined. It is the single check most likely to go red
  on any emitter text move, and it has done so before for a legitimate reason
  (`bat4triage_report.md`). **Read it before stage 3, not after.**
- **`battriage_report.md`'s second reader class.** The same script's CHECK 3
  manifest holds `EMITTED_BYTES` counts that **never cite an abi digit** but
  whose values move whenever scaffolding does, so the abi ritual's grep
  structurally cannot find it. Stage 3 claims byte-neutrality, so this manifest
  should not move — **but it is the manifest that proves the claim, so it must
  be checked explicitly rather than assumed untouched.**
- **`sb_fragf` and the arena's lifetime.** `Ctx` carries two Job-owned scratch
  buffers (`internal.h:2013-2021`, `Job.scr_test`/`scr_desc`) precisely because
  a stack-local `StrBuf` leaks its heap buffer when `ctx_fail` longjmps out of
  emission — LeakSanitizer caught that on the size-term ladder. `sb_fragf`
  allocates from the **arena**, which is freed wholesale with the compile, so
  it does not reintroduce that hazard — **but this must be verified under `make
  san`, not argued**, and K54's `SAN_DETECT_LEAKS` derivation is what makes
  that runnable on darwin.
- **`sb_fragf` raises arena pressure.** Every fragment that was stack storage
  becomes an arena allocation that lives until the compile ends. K7's accounting
  bounds arena traffic and `PCREC_MAX_SUBSET_ELEMS` and friends are calibrated
  against it. The volume is ~43 sites × a handful of calls per artifact, which
  is negligible against the NFA/DFA traffic those caps exist for — **stated as
  a belief with its reason, not as a measurement**, and the stage 0 sweep's own
  peak RSS is the cheapest instrument that would falsify it.
- **The `""` default is a byte-identity contract at three sites**
  (`accept_tr`/`fail_tr`/`exhaust_tr`, §2.2 item 1). A migration that makes
  these `NULL` instead of `""` moves emitted bytes on every untraced artifact —
  which is every shipped artifact.

---

## 5. A4 — SEVERITY / EFFORT / BLAST RADIUS

| id | element | severity | effort | blast radius |
|---|---|---|---|---|
| **L10-0** | The long-prefix control (`run_cli_tests.sh` case 3) compiles the pattern `a` and reaches ~none of the 48 literal-sized emitter buffers; the check that exists to stop K38 recurring cannot see the population it is about | **CORRECTNESS-RISK** (instrument) | LOCAL | 1 check + 1 new sweep; 0 src files; 0 anchors; no abi |
| **L10-1** | Fragment layer: 43 `snprintf`-into-`char[N]` sites re-derive "how big"; `vm_rolef` (`emit_vm.c:754`) is 90% of the primitive and truncates at 160 anyway (`:764-765`); tightest margin in the tree is 9 bytes | MAINTAINABILITY (+ latent CORRECTNESS-RISK) | **CROSS-CUTTING** | 2 files; **4 anchors directly, 123 in radius**; 7 source-reading checks; **no abi event** |
| **L10-2** | `sb_join`: 5 implementations, 3 with different undocumented over-long policies; `render_modules` (`enabled.c:180`) produces an **out-of-order partial list**, not a truncated prefix | **CORRECTNESS-RISK** (live, small) | LOCAL | 4 files; 0 anchors; no abi |
| **L10-3** | Field/row layer: 5 independent TSV row emitters, 2 incompatible escapers, 3 dump files escape nothing; `syntax_dump.c` has an escaper its TSV path does not call | MAINTAINABILITY (+ latent CORRECTNESS-RISK) | LOCAL | 5 files; **1–2 anchors**; `tests/rxtsource` field-count pins; no abi |
| **L10-4** | CLI channel: 76 open-coded `fprintf(stderr, …)`, 72 hand-writing `"pcrec: "`, `"missing value for %s"` × 8 | MAINTAINABILITY | **MECHANICAL** | 1 file; **0 anchors**; `tests/cli` wording pins (D26: wording unchanged); no abi |
| **L10-5** | `sb_name`/`sb_upper`: the uppercased prefix is a second derived name from one source, derived independently at ≥3 sites, and is the largest single non-prefix binding in the `%s_` census (139 of 584) | MAINTAINABILITY | LOCAL (as the primitive) / **DESIGN-EVENT** (as a `Vm.up` retirement) | 2 files for the primitive; `Vm.up` is ~110 read sites and is **out of wave 1** |
| **L10-6** | `emit_vm.c:8165`'s recorded LIVE truncation (`char slot[48]`, a listing column) is bounded by slot-name length, not prefix length, and is invisible to every prefix-based instrument; its emitted bytes WILL move when the buffer is retired | **CORRECTNESS-RISK** | LOCAL, **escalate** | 1 site; `--emit-listing` bytes; column-width-as-contract is a manager question |
| **L10-7** | The template layer. **RECOMMEND NO CHANGE — CLOSED, not deferred.** Population 1 by lens 2's metric, 30 calls / 1.9% of emitted literal bytes by the corrected one, and structurally unable to reach the 64% where the win is | — (anti-finding) | NONE | none. Filed with its measurement so a later wave does not reopen it by guess |
| **L10-8** | `write_file` (`cli/main.c:292-299`) checks `fclose` but not `ferror()` on the `fputs` that wrote the artifact | POLISH (correctness, remote) | MECHANICAL | 1 site; **do not ride stage 2** |

**Wave-1 running order** (MECHANICAL + safe first, per A4; DESIGN-EVENT never):
**stage 0 (L10-0)** → **stage 2 (L10-4)** ∥ **stage 1 (L10-3, L10-2)** →
*[lens 1 second pass]* → **stage 3 (L10-1, L10-5 primitive, lens 1 X8)** →
stage 4. L10-6 and L10-8 are filed separately and ride nothing. L10-7 is a
standing do-not.

Stages 0, 1 and 2 are independent of each other and of the lens 1 second pass,
so the wave's critical path is stage 0 → lens 1's second pass → stage 3.

---

## 6. WHERE THE SWEEP STOPPED (ADDENDUM 2), and what is NOT settled

**Measured exhaustively.** Every `sb_puts`/`sb_printf`/`sb_putc` call statement
in `src/gen/emit_vm.c` and `src/gen/emit_dfa.c` (771, cross-validated against
lens 2's independent grep); every `char NAME[<literal>]` declaration and every
`snprintf` into one in those two files; all 277 sabotage anchors in all 261
rows; every `%s_` occurrence in the two emitters.

**Read and taken as given** (lens 2 §8's instruction): the §1.0 mechanism
census across the primary tier, and the byte-neutrality property of the
fragment layer. **Re-measured and found different**: the anchor counts (rows vs
anchors), the anchors-quoting-text classification, the source-grepping check
list, and L2-3's 652.

**Not reviewed.** The run-length and template analysis covers the two emitters
only; `syntax_dump.c` (153 `sb_*`) and `rxt_source.c` (126) were examined for
the field/row/join findings but not run through the template counter, on the
ground that neither interpolates a `--prefix`. `cli/main.c`'s 76 stderr sites
were counted, not read individually — stage 2's mechanical claim rests on lens
2's reading of them plus `tests/cli` being the control, not on my own site-by-
site pass. The ~41 literal-sized buffers elsewhere in `src/`+`cli/` (lens 3's
94 minus my 48) are out of wave 1's scope and unexamined here.

**What is NOT settled, headed by the sharpest:**

1. **Whether stage 1's escaping is byte-neutral or a bug fix is genuinely
   open** and is the one measurement a stage-1 lane must take before writing
   code. I did not take it: it requires enumerating every string reachable by
   three dump files' data tables, which is a different sweep from this lane's.
2. **Whether lens 1's X8 rides stage 3** is a synthesis decision, not mine. I
   recommend it rides, on shared-blast-radius grounds.
3. **Whether the `--emit-listing` column widths are a contract** (L10-6) is a
   manager/Frank question and blocks retiring one buffer, not the stage.
4. **The arena-pressure belief in §4.4 is a belief.** It has a named
   falsifying instrument (stage 0's peak RSS) and no measurement.
5. **`Vm.up`'s retirement** is named, scoped out, and has no plan. It is the
   largest residue of L10-5 and should not be picked up opportunistically.
6. **My prefix-expression list is a closed set of eight spellings** (§1.7). It
   was validated against a frequency dump, not proved complete, and every
   number in §1.2/§1.3/§1.5 depends on it.
