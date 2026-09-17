# LENS 2 — DOMAIN / TOOL SEPARATION

Lane `lens2sep` (opus, read-only review), 2026-09-17, against `main` at
`7d444f9e`. Charter: `docs/dev/reviews/code_review_criteria_draft.md`
lens 2 — *"teach the computer the skills": where does policy code inline
mechanics that belong in a taught primitive?*

Primary deliverable: **the text-emission mechanism map** (§1) and **the
one kit** (§2). Secondary: other policy-inlines-mechanics instances,
ranked (§3). Annexes: A3 check-coupling (§4), A1 ruled-record checks
(§5), where the sweep stopped (§6).

**Nothing was built, measured by running, or changed.** Every count in
this report was obtained by grep or by reading the committed metric
artifacts, both cited per A5.

---

## 0. The headline, and the charter's seed corrected

The charter's seed reads: *"the emitters use neither core/sb.c nor
stdio — the tree appears to carry MULTIPLE text-emission mechanisms."*

**The first half is false and the correction is what makes the lens
interesting.** The emitters are `core/sb.c`'s two largest customers:
`src/gen/emit_dfa.c` makes 441 `sb_*` calls and `src/gen/emit_vm.c`
makes 330, against 18 stdio calls between them (grep census, §1.0).
`StrBuf` is not a mechanism the emitters bypass; it is the one
mechanism nearly everything in the tree shares.

**The second half is true, and the mechanisms are not the ones the seed
names.** What the tree carries is not four competing *streams*. It
carries one sound stream primitive and **four unbuilt primitives above
it**, each of which the policy code re-implements at every site:

| the mechanic | is it taught? | how many open-coded copies |
|---|---|---|
| append to a growing buffer | **YES** — `StrBuf`/`sb_*` | 0 |
| a library diagnostic | **YES** — `ctx_fail` | 0 |
| interpolate a prefix into fixed C text | **YES, but sealed into one seam** — `pcrec_enc_emit_text` | **652** `%s_` substitutions in `src/gen` |
| build a bounded text FRAGMENT to interpolate later | **NO** | 105 `snprintf`-into-`char[N]` sites in `src/gen` |
| escape and frame a TSV field/row | **HALF** — two incompatible escapers, neither shared | 5 row emitters, 3 with no escaping at all |
| join names with a separator | **NO** | 5 implementations |
| a CLI diagnostic | **NO** | 76 open-coded `fprintf(stderr, "pcrec: …")` |

The sharpest single observation in the report is **finding L2-3**: the
tree already contains the taught primitive for the biggest instance
(`pcrec_enc_emit_text`, a 7-line `$`-template interpolator), it works,
its own header explains exactly why it is better than the alternative —
and it is reachable from two call sites inside `src/gen/enc/` and
nowhere else, while the two emitters perform the identical operation by
hand six hundred and fifty-two times.

**Three numbers in this report were measured twice**, because the first
instrument was wrong each time, and the corrections are recorded where
they belong rather than quietly fixed: the source-text check count (§4.2 —
a literal-path grep counted 14 scripts, all of them matching in COMMENTS;
the real answer is 8), the prefix-interpolation count (§M3 — counting
`sb_printf` CALLS understates it, since one call can carry several `%s_`
substitutions; the real answer is 652), and `usage`'s span (§3 rank 1).
Two of the three moved in the direction that WEAKENS a finding, which is
the direction worth stating out loud.

---

## 1. THE TEXT-EMISSION MECHANISM MAP

### 1.0 The census (A5 — by grep, at `7d444f9e`, whole primary tier)

Per-file counts of each text-producing primitive. Files with zero of all
three are omitted; the list is exhaustive over `src/`, `cli/`, `lib/`.

| file | `sb_*` | stdio | `snprintf` |
|---|---|---|---|
| `src/gen/emit_dfa.c` | 441 | 8 | 24 |
| `src/gen/emit_vm.c` | 330 | 10 | 81 |
| `src/parse/syntax_dump.c` | 153 | 0 | 1 |
| `src/parse/rxt_source.c` | 126 | 0 | 16 |
| `src/parse/schema_dump.c` | 7 | 0 | 0 |
| `src/core/sb.c` | 3 | 0 | 0 |
| `src/core/internal.h` | 3 (decls) | 0 | 1 |
| `src/parse/limits_dump.c` | 2 | 0 | 0 |
| `src/parse/axes_dump.c` | 2 | 0 | 6 |
| `src/gen/enc/enc.c` | 2 | 0 | 0 |
| `src/core/compile.c` | 0 | 3 | 4 |
| `cli/main.c` | 0 | **93** | 3 |
| eleven other `src/` files | 0 | 0 | 1–9 each |

Two facts fall straight out. **Stdio is confined to `cli/main.c` plus
three sites in `compile.c` and eighteen in the emitters** — the library
genuinely does not print, which is a separation that is already right
and that any kit must preserve. And **`cli/main.c` uses zero `sb_*`**,
which is also right: it consumes finished `char *` blobs and writes
them.

### M1 — `StrBuf` and `sb_putc`/`sb_puts`/`sb_printf`/`sb_take`/`sb_free`

- **Where.** `src/core/sb.c` (81 lines); type and declarations at
  `src/core/internal.h:60-67`.
- **API shape.** `typedef struct { char *p; size_t len, cap; Ctx *cx;
  size_t abort_over; } StrBuf;` — append a char, a C string, or a
  `printf`-attributed format; `sb_take` transfers ownership and resets;
  `sb_free` releases.
- **Users.** 1,069 `sb_*` lines across 10 files (the column above), of
  which 6 are the declarations (`internal.h:62-67`) and definitions
  (`sb.c`) themselves — so ~1,063 call sites.
- **What it does that nothing else can.** Three things, each earned by a
  recorded incident. (i) It cannot truncate — `sb_grow` (`sb.c:8-31`) is
  the one place a buffer's length grows. (ii) `cx` upgrades a buffer from
  `abort()` to a diagnosed `ctx_nomem` ([M4.7b]/K7), and the NULL case is
  a real one that `syntax_dump.c`'s detached buffers use
  (`internal.h:46-50`). (iii) `abort_over` is `[ART-SIZE]`'s size-term
  early abort, placed at `sb_grow` precisely *"because this is the ONE
  place a buffer's length grows, so no append path can miss it"*
  (`sb.c:10-14`).
- **Cost of folding into one kit.** None. It **is** the kit's base. No
  finding is filed against it.

### M2 — the emitters' FRAGMENT buffers (`char buf[N]` + `snprintf`)

- **Where.** `src/gen/emit_vm.c` (81 `snprintf`, 41 buffers sized with a
  numeric literal + 20 sized `PCREC_MAX_EMIT_NAME_LEN`) and
  `src/gen/emit_dfa.c` (24 `snprintf`, 14 constant-sized). Roughly 105
  sites.
- **API shape.** **There is none.** It is an idiom, not an interface:
  declare a stack array, `snprintf` into it, pass the array as a `%s`
  argument to a later `sb_printf`.
- **Users.** Every large emitter function. The dense clusters are
  `vm_slot_expr`/`vm_slot_name` (`emit_vm.c:855-953`), the four
  call-site save/restore blocks (`:6818`, `:6942`, `:7009`, `:7023`,
  each `char val[160]; char nm[48];`), the cursor and revdet rungs
  (`:4078-4382`, `:4857-5138`), and the trace-line block
  (`:10770-10880`).
- **What it does that M1 cannot.** It produces a **value** — a C
  sub-expression or identifier to be interpolated into a later
  `sb_printf` — rather than appending to a stream. A `StrBuf` is a poor
  substitute for that today, and the reason is recorded: a stack-local
  `StrBuf` leaks its heap buffer when a `ctx_fail` longjmps out of
  emission, which LeakSanitizer caught on the size-term ladder and which
  is why `Ctx` carries two Job-owned scratch buffers
  (`internal.h:2013-2021`, `Job.scr_test`/`scr_desc`).
- **What it costs.** `snprintf` truncates silently, and the tree has the
  receipts:
  - **K38** (`src/core/limits.h:50-70`) is the recorded **miscompile**: a
    real 60-character `-p` prefix met a family of buffers sized for
    `"rx"` and produced uncompilable C, *"invisible to every corpus
    artifact because they all use the 2-char 'rx' prefix."* The cure was
    a shared constant, `PCREC_MAX_EMIT_NAME_LEN` (`limits.def:134`).
  - The cure is **partially adopted**: 34 sites use it (20 in
    `emit_vm.c`, 14 in `emit_dfa.c`); **41 buffers in `emit_vm.c` and 8
    in `emit_dfa.c` still hand-pick a number.**
  - Two separate comments argue their own buffer's size in prose, each
    citing the same incident — `emit_vm.c:944-948` (*"this file has
    already been bitten once by a too-small snprintf buffer"*) and
    `:6813-6817` (the same sentence again, 5,870 lines later). A third,
    `:10765-10769`, records `-Wformat-truncation` catching two of three
    trace strings after the `[M6-READ]` rename lengthened them.
  - `limits.h:65-68` states the general form outright: the constant
    exists *"so ONE size answers 'how big' at every such site instead of
    a fresh per-site guess that reopens K38 the next time a suffix
    grows."* Forty-nine sites still make the fresh per-site guess.
- **Cost of folding.** Measured against the alternative in §2: **nothing
  is given up.** An arena-backed formatted fragment cannot truncate, is
  freed wholesale with the compile, and is byte-identical in output to a
  fragment that *did not* truncate. The tree is 90% of the way there
  already — see M4.

### M3 — `pcrec_enc_emit_text`, the `$`-template interpolator

- **Where.** `src/gen/enc/enc.c:88-94` (7 lines).
- **API shape.** `void pcrec_enc_emit_text(StrBuf *sb, const char *text,
  const char *prefix)` — copy `text` to `sb`, replacing every `$` with
  `prefix`.
- **Users.** **Two**, both inside the same file: `enc.c:69`
  (`pcrec_enc_emit_decls`) and `enc.c:77` (`pcrec_enc_emit_defs`). The
  template bodies live in `src/gen/enc/enc_byte.c` and `enc_utf8.c` as
  ordinary C string literals.
- **What it does that nothing else can.** It lets the author of emitted
  text **write C**. `enc.h:18-23` states it: *"The residual is emitted
  verbatim except for the artifact's `--prefix`, so a backend is a string
  and a backend author writes C, not emitter code."* A 40-line residual
  function is 40 readable lines of C, not 40 `sb_printf` calls whose
  shape a reader must mentally reassemble.
- **Cost of folding.** None — **and that is the finding.** The operation
  it generalizes is the single commonest thing the two emitters do:
  a `%s_` substitution — one prefix-composed emitted identifier — occurs
  **347 times in `emit_vm.c` and 305 times in `emit_dfa.c`, 652 in all,
  across 450 source lines** (grep). Every one of those is
  `pcrec_enc_emit_text`'s `$` performed by hand, through `printf`
  positional arguments instead of a placeholder in readable C.
- **Why it is confined, and why that reason does not bind the
  mechanism.** D58/DD-12(7) scoped the *seam*, not the *primitive*, and
  the one constraint the seam imposes on template text (*"residual text
  must contain no other `$`"*, `enc.h:22-23`) is a property of the
  format, reusable anywhere the same rule is honoured.

### M4 — `derived_name`, `prefix_upper`, `vm_rolef`: three near-primitives

- **Where.** `derived_name` and `prefix_upper` in `src/gen/emit_dfa.c`
  (arena-owned prefix+suffix identifier builder; 8 users across
  `src/gen` and `src/core`). `vm_rolef` at `src/gen/emit_vm.c:754-770`
  (arena-owned **formatted** text for a listing role string).
- **What each does that M2 cannot.** `derived_name` allocates from the
  arena, so it can neither truncate nor leak. `vm_rolef` formats.
- **The gap, and it is one line wide.** `derived_name` cannot format;
  `vm_rolef` can, **and truncates anyway** — `emit_vm.c:764-765` reads
  `size_t sz = (size_t)n + 1; if (sz > sizeof buf) sz = sizeof buf;`
  over a `char buf[160]`. So the one arena-backed formatter in the tree
  reproduces the exact hazard it was in a position to retire. The two
  functions are the same function with different sizing policies, and
  neither is general.
- **Cost of folding.** None; both become one-liners over the kit's
  fragment call (§2, item 2).

### M5 — the dumps' local row/field helpers: four independent implementations

`src/parse/syntax_dump.c`, `rxt_source.c`, `axes_dump.c`,
`limits_dump.c`, `schema_dump.c` each produce TAB-delimited rows for a
`--list-*` surface. All five sit on `StrBuf`. Above `StrBuf` they share
**nothing**.

| file | field helper | row shape | escaping |
|---|---|---|---|
| `rxt_source.c` | `put_escaped` (`:3743`, 12 sites) | 20 explicit `sb_putc('\t')` (`:3857-3906`) | `\\ \t \n \r` then `<0x20\|0x7f → \xNN` |
| `syntax_dump.c` | `put_str` (`:141`, 14 sites, **NULL-guard only**); `put_text` (`:1195`, 5 sites, escaper) | 17 explicit `sb_putc('\t')` (`:208-264`) | **the escaper exists and the TSV path does not call it** |
| `axes_dump.c` | none | `axis_row` (`:253`), 13 params, one 12-`%s`-and-tab format string; `emit_pred_row` (`:359`) is a second | **none** |
| `limits_dump.c` | none | `limit_row` (`:46`), rows generated by X-macro off `limits.def` | **none** |
| `schema_dump.c` | none (zero `static` functions in 183 lines) | inline `sb_printf`, 9 tabs | **none** |

- **What each does that the others cannot.** Structurally, nothing. The
  capability sets are strictly ordered: `rxt_source.c`'s escaper ⊃
  `syntax_dump.c`'s escaper ⊃ nothing. The one genuine difference is
  that the two escapers serve **different formats**, and honestly so:
  `put_text` deliberately passes `\` through because its format grammar
  is human-readable `--explain` output (`syntax_dump.c:1193-1194`),
  while `put_escaped` must protect TSV framing. They are not redundant —
  but their `\xNN` tail is byte-identical logic
  (`syntax_dump.c:1200` vs `rxt_source.c:3758`) written twice, and there
  is no shared control-byte escaper for either to call.
- **The latent corruption, and where it was already diagnosed.**
  `rxt_source.c:3735-3742` records the exact failure and why the escaper
  exists: three corpus blocks carry a literal TAB in the pattern text,
  *"emitted raw the field splits and every later column shifts on
  exactly those rows — a three-row-in-3,265 corruption, which is the
  size of finding a summary swallows."* **The diagnosis stayed in that
  one file.** `axes_dump.c`, `limits_dump.c` and `schema_dump.c` splat
  free-form prose into tab-delimited cells with no escaping at all
  (`axes_dump.c:313-317` and `:337-343` carry multi-hundred-character
  hand-written `applies` prose), and `syntax_dump.c`'s TSV row writer
  puts `r->note`, `r->syntax`, `r->class_expect` and `r->family` through
  `put_str`, which does not escape.
- **Live or latent?** **Latent today.** Every string those three files
  render is a compile-time C literal in `registry.c` / `limits.def` /
  the axis candidate arrays, and a C literal is unlikely to contain a
  raw tab. The invariant is real and unenforced: nothing stops the next
  `applies` string or `limits.def` `desc` from containing one, and
  nothing would report it.
- **Cost of folding.** The `--explain`/`--probe-ask` block emitters in
  `syntax_dump.c` (`put_answer` `:1255`, `put_names` `:1277`,
  `put_agreement` `:1298`, `put_verb_block` `:1459`) are not row-shaped
  and stay. Everything row-shaped folds; `rxt_source.c`'s
  `rxt_columns[]` table (`:3806`, with `RXT_NCOLS` `:3802` and the
  header emitted by looping the table so header and `ncols` cannot
  disagree) is the shape the other four should adopt, and it already
  exists.

### M6 — `cli/main.c`'s raw stdio

- **Where.** `cli/main.c` (1,736 lines): 76 `fprintf(stderr, …)`
  (**zero** `fprintf` to any other stream), 14 `fputs` (12 → `stdout`, 1
  → the output `FILE *`, 1 → `usage`'s parameter), 2 `fputc`, 1 bare
  `printf` (`:1481`, the `--count-groups` answer), 9 `perror`.
- **API shape.** None. Two narrow wrappers exist and neither is a
  diagnostic channel: `static void usage(FILE *f)` (`:99`, 3 call sites)
  and `static int write_file(const char *path, const char *text)`
  (`:292-299`, 4 call sites).
- **What it does that nothing else can.** It is the only code in the
  primary tier that owns a `FILE *`. That separation is correct.
- **What it costs.**
  - **72 of the 76 stderr sites hand-write the literal `"pcrec: "`
    prefix.** There is no `die()`, `err()`, `warn()` or macro anywhere in
    the file; every site is `fprintf(stderr, "pcrec: …"); return 1;`.
  - `"missing value for %s"` appears **8 times verbatim** (`:726`,
    `:733`, `:740`, `:748`, `:757`, `:771`, `:778`, `:788`).
  - `"--flavour applies to … only"` appears at **6 sites in three
    different wordings** (`:1351`, `:1393`, `:1467`, `:1537`, `:1632`),
    each hand-enumerating which modes accept the flag.
  - `write_file` checks `fclose`'s return but not `ferror()` on the
    `fputs` that wrote the artifact (`:296-297`) — a short write on a
    full disk is reported only if it happens to surface at close.
- **Cost of folding.** Preserving diagnostic wording byte-for-byte is a
  hard constraint (D26, §5), so the fold is mechanical or it is nothing.

### M7 — `ctx_fail`: the contrast that makes the lens's case

- **Where.** `src/core/compile.c:16-31`.
- **API shape.** `void ctx_fail(Ctx *cx, size_t pos, const char *fmt,
  ...)` — `vsnprintf` into `cx->err->msg`, record `pos` and `input`,
  `longjmp`.
- **Users.** The whole library. `ctx_nomem` (`compile.c:24-29`) is its
  one specialization, and `internal.h` notes *"there is exactly one of
  these."*
- **Why it belongs on this map.** It is the **same mechanic** as M6 —
  format a message into a bounded buffer and deliver it through the
  program's error channel — taught once on the library side and
  open-coded seventy-six times on the CLI side, in the same repository,
  under the same review standard. `ctx_fail` also truncates, and that is
  fine *because it truncates in one place under one policy that a reader
  can find*. That contrast, not the truncation, is the finding.

### M8 — "join names with a separator": five implementations

Not a stream, but it is text production and it is the clearest
small-scale instance of the lens's question.

| implementation | where | separator | over-long behaviour |
|---|---|---|---|
| `put_mask` | `syntax_dump.c:61` (7 sites) | `\|` | n/a (StrBuf) |
| `render_modules` | `src/parse/enabled.c:164` | `,` | `continue` (`:180`) — skips the long name and keeps appending shorter later ones, so the result is an **out-of-order partial list**, not a prefix |
| `pcrec_enc_names` | `src/gen/enc/enc.c:52` | `,` | `if (k + ln + 1 < cap)` — silently drops |
| target-name join | `cli/main.c:1104-1113` | `, ` + `fputc(')')` | n/a (stdio) |
| target-name join | `cli/main.c:1147-1155` | `, ` | n/a (stdio) |

Three of the five are bounded-buffer copies of one loop, with three
different and undocumented over-long policies.

---

## 2. THE ONE KIT

### 2.1 What the kit is, and what it deliberately is not

Per **D82 bound 3** (*"Only axes with ≥ 2 real forms get a
representation object; a one-site boolean stays a boolean"*) and the
D75 addendum's *"no framework for its own sake"*, this proposal adds
**four functions and one CLI-local function**, every one of which has
two or more existing open-coded implementations in the tree today. It
adds no types, no registries, no dispatch and no policy objects.

It is deliberately **not** a general "emitter DSL". Three things a
reader might expect are excluded and the reason is given for each:

- **No indentation manager.** The emitters pass indent as a `const char
  *indent` parameter today (e.g. `pcrec_emit_startpos_guard`,
  `internal.h:5105`). Two forms, both trivial; D82 bound 3 says it stays.
- **No emitted-line abstraction** (`emit_line(c, fmt, ...)` wrapping
  `sb_printf` + `"\n"`). It buys nothing `sb_printf` does not, and it
  would move 771 call sites in the two most sabotage-anchored files in
  the tree (§4) for zero capability.
- **No merge of `put_text` and `put_escaped`.** They serve two formats
  with two correct and different policies (M5). What is shared is only
  the `\xNN` tail.

### 2.2 The API sketch

Home: a new `src/core/text.h` + `src/core/text.c` beside `sb.c`, or
`sb.c` itself grown — a manager's call, and the smaller change is
probably to grow `sb.c` and its `internal.h` block rather than mint a
file.

```c
/* (1) THE STREAM — unchanged. StrBuf + sb_putc/sb_puts/sb_printf/
 *     sb_take/sb_free stay exactly as they are (M1). */

/* (2) THE FRAGMENT — arena-owned formatted text. Cannot truncate.
 *     Never freed by its caller; dies with the compile's arena. */
const char *txt_f(Arena *a, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
/*     Implementation is sb_printf's own body (sb.c:49-62): a va_copy,
 *     a measuring vsnprintf(NULL, 0, ...), ONE arena_alloc of exactly
 *     n+1, a second vsnprintf. ~12 lines. Truncation is impossible BY
 *     CONSTRUCTION rather than by a per-site size argument. */

/* (3) THE TEMPLATE — pcrec_enc_emit_text (M3), moved and renamed,
 *     otherwise character for character what it is today. */
void txt_tmpl(StrBuf *sb, const char *text, const char *prefix);

/* (4) THE FIELD AND THE ROW — rxt_source.c's put_escaped (M5),
 *     promoted, plus the two shapes its four siblings hand-roll. */
void txt_field(StrBuf *sb, const char *s);   /* TSV-safe: \\ \t \n \r, then \xNN */
void txt_row(StrBuf *sb, const char *const *cells, int ncell);  /* escaped, tab-joined, \n */
void txt_join(StrBuf *sb, const char *sep, const char *const *names, int n);

/* (5) THE CLI CHANNEL — cli-local (cli/main.c or a new cli/diag.c),
 *     NOT in src/. ctx_fail's shape on the caller's side of the
 *     library boundary. */
int cli_err(const char *where, const char *fmt, ...)
    __attribute__((format(printf, 3, 4)));
/*     Writes "pcrec: " (+ " (<where>)" when non-NULL), the message,
 *     a newline, to stderr; returns 1 so every site stays
 *     `return cli_err(...);`. Wording is UNCHANGED at every site. */
```

### 2.3 What folds in

| mechanism | folds into | sites moved |
|---|---|---|
| M2 fragment buffers | (2) `txt_f` | ~105 in `src/gen` |
| M4 `vm_rolef`, `derived_name`, `prefix_upper` | (2) `txt_f` | 3 definitions, 8+ callers unchanged |
| M3 `pcrec_enc_emit_text` | (3) `txt_tmpl` | 2 call sites, rename only |
| M5 `put_escaped`, `put_str`-on-the-TSV-path, `axis_row`, `emit_pred_row`, `limit_row`, `schema_dump.c`'s inline rows | (4) `txt_field`/`txt_row` | 5 row emitters → 1 |
| M8 `put_mask`, `render_modules`, `pcrec_enc_names`, `main.c:1104`, `:1147` | (4) `txt_join` | 5 → 1 |
| M6's 76 `fprintf(stderr, "pcrec: …")` | (5) `cli_err` | 76 in `cli/main.c` |
| M1 `StrBuf`, M7 `ctx_fail` | — | **nothing. They are already right.** |

### 2.4 Migration order

Ordered by check-coupling cost ascending (§4), which is also roughly
risk-ascending. Per **D77** each step names the measurement that should
precede it.

**Step 1 — (4) the field/row layer.** Four dump files, **one** sabotage
anchor between them (`syntax_dump.c`, 1; `schema_dump.c`, 1; the other
three, 0 — §4). No abi event: `--list-*` output is not emitted artifact
text, so D76/D94 do not fire. *Measurement first:* does any string
reachable by `axes_dump.c`, `limits_dump.c` or `schema_dump.c` contain a
tab, newline or control byte today? If the population is zero — which is
likely — the wave is byte-neutral and the escaping is added as
insurance, which is exactly how it should be framed. If it is non-zero,
the wave is a **bug fix** and should be filed as one before it is
refactored.

**Step 2 — (5) the CLI channel.** 76 sites, **zero** sabotage anchors in
`cli/main.c`. `tests/cli/` pins diagnostic text, so D26 makes this a
purely mechanical substitution: `fprintf(stderr, "pcrec: X\n", …);
return 1;` → `return cli_err(NULL, "X", …);`, wording byte-identical. A
diff that changes one word of one message is out of scope for this
wave. *Measurement first:* none needed; the existing `tests/cli` suite
IS the control.

**Step 3 — (2) the fragment layer.** This is where the cost is, and also
where the correctness payoff is. It touches ~105 sites in the two files
that carry **113 of the tree's 261 sabotage anchors** (§4), 24 of which
quote an `sb_*`/`snprintf` call verbatim in `SAB_BEFORE`. The property
that makes it tractable: **it must be byte-neutral in the emitted
artifact**, because a fragment that *cannot* truncate produces exactly
the text a fragment that *did not* truncate produced. So it is **not**
an abi event, and the four standing byte-identity gates
(`tests/codegen/run_vm_identity.sh`,
`run_recursion_identity.sh` comparison (A), `run_backref_identity.sh`,
`run_atomic_identity.sh`) are the wave's own control at zero extra cost.
The 24 anchor re-aims travel in the wave (A3). *Measurement first:*
compile the corpus at a 60-character `-p` prefix before and after. Today
that is K38's own reproduction (`tests/cli/run_cli_tests.sh` case 3);
after the wave it should be provably clean at every one of the 49
hand-sized sites, which is the wave's acceptance number.

**Step 4 — (3) the template layer. Recommend AGAINST a wholesale
conversion, and this is the anti-perversion half.** Converting a run of
`sb_printf` calls into one `$`-template moves whitespace unless done
character-perfectly, and **any moved emitted byte is an abi bump plus a
grep-found re-pin of every reader of the number** (D76/D94 — the ritual
that missed a fifth reader in `match_api.md` once). The win is real
(readability of the emitted C's *source*) but it is a readability win
paid for in the most expensive currency this tree has. *Measurement
first:* count the runs of ≥ 5 consecutive `sb_puts`/`sb_printf` calls
emitting a contiguous literal block with only the prefix varying. If
that population is small, the change is not worth an abi event and the
honest answer is **do not do it**; if it is large, the number is the
argument. **Nobody has counted it, and this lane deliberately did not
build the counter** — that is D77's trigger, not a gap in this report.

---

## 3. BEYOND EMISSION — other policy-inlines-mechanics instances, ranked

Ranked by (payoff × confidence) ÷ blast radius. Each carries its A4
vocabulary in §7.

**Rank 1 — option plumbing is a 64-arm `if`/`else if` chain, and the
file says so itself.** `cli_parse` (`cli/main.c:379-809`, 431 span /
247 code lines — census row 6, the sixth-longest function in the tree)
is one `for` loop over `argv` whose body is a single chain of 64 arms
against 62 distinct option spellings, terminating in an unknown-option
error (`:794`) and a positional fallthrough (`:802`). There is no
`switch` in the file and no option-descriptor array for the general
case. **The taught primitive already exists, at one-tenth scale and
with its own justification**: `static const RaiseOnlyLimit
raise_only_limits[]` (`:67-80`, 6 rows of `{flag, floor, offsetof}`),
dispatched by `raise_only_match` (`:89-98`), whose header comment
(`:48-65`) explicitly frames the table as the alternative to *"one more
`else if` block in `cli_parse`'s chain below."* The file has therefore
already made the lens's argument about itself, once, for six flags, and
left the other fifty-six in the chain.

The compounding cost is `usage` (`cli/main.c:99-263`): **162 literal continuation
lines** inside a single `fputs`, with no machine-readable relationship to
the chain that parses those flags. A flag can be added to one and not the
other with nothing failing.

**Rank 2 — valid-value menus: 8 sites, 1 table-driven.** Seven of the
eight hard-code the menu as prose: `--unroll` (`:570-571`),
`--vm-entry-shape` (`:587-590`, hand-mirroring the four rung names that
`emit_vm.c` also spells), `--tune` (`:614-616`, hand-mirroring the five
aliases `src/core/tune.c` owns as a table), `--engine` (`:640-641`),
`--probe-ask` (`:1413-1417`), `--flavour` (`:1579-1580`), and a *second,
separately worded* engine menu for the `.rxt` surface (`:964-966`). The
eighth, `--encoding` (`:277-279`), renders its menu from the encoding
registry via `pcrec_enc_names` — and that call exists because D58's
`[M5-SEAM]` ruling specifically noted *"this diagnostic and cli/main.c's
name mapping drifting apart"* as the motivating instance
(`src/core/CLAUDE.md`, compile.c entry). **The lesson was learned once
and applied to one flag.** `--tune`'s menu is the most exposed: D103
makes `tune.c` the dial's one home, and `cli/main.c:614-616` is a second
spelling of that namespace.

**Rank 3 — growable-array append has no primitive.** Clone group 10
(`tools/review/out/clone_candidates.tsv`): `rxt_source.c`'s `prov_push`
(`:1370`), `variant_push` (`:1384`), `case_push` (`:1398`) and
`aux_push` (`:1412`) at `group_frac` **1.000** each, with `row_push`
(`:615`) at 0.485 — five copies of grow-if-full-then-append, in one
file, 13 lines each. Clone group 3 puts the same shape in two more
files: `cli/main.c`'s `libdir_push` (`:362`), `emit_vm.c`'s `vm_ev`
(`:737`) and `vm_isl_insert` (`:3567`). The missing primitive is an
arena-backed `vec` (capacity-doubling append over `arena_alloc` +
`memcpy`, which is what all seven already are). This is genuinely
shared with **lens 1** and should be deduped in synthesis.

**Rank 4 — DFA table WRITING is unfactored, though table *selection* is
the tree's model instance.** Clone group 11: `emit_dfa.c`'s
`emit_tr_table` (`:2610`, 0.750), `emit_eol_table` (`:2727`, 0.727),
`emit_end_table` (`:2742`, 0.727), `emit_acc_cls_table` (`:2906`,
0.600), `emit_seed_table` (`:2946`, 0.478). Clone group 7: the six
prefilter emitters `pf_emit_memchr` / `_bounded` / `pf_emit_bcls` /
`_bounded` / `pf_emit_ofs` / `_bounded` (`:4511-4854`) at **0.885–1.000**
— six functions where the `_bounded` variant of each pair is its
sibling plus a bound. **This one is ranked low on purpose**, because the
file it sits in is the tree's *best* answer to lens 2 already: `[ENG-FORM]`
/ D82's layer 1 makes every representation decision a
`static const` candidate list with `dfa_select` picking the first
applicable entry, and layer 2 makes emitted state an opaque token behind
a per-form accessor block. The *selection* half is a taught primitive and
an exemplary one. What was never factored is the *writing* half — the
`for` loop that prints `n × ncls` integers with a wrap and a comment
header. A shared `emit_int_table(c, name, cells, n, stride, cell_of)`
is a plausible three-argument primitive, and every one of those
functions sits inside the 113-anchor blast radius, so it should ride
step 3 or not happen.

**Rank 5 — enum→string mappers. RECOMMEND NO CHANGE, and say so.**
Clone group 2 flags `syntax_dump.c`'s `kind_name` (`:72`),
`doorway_name` (`:92`), `diag_name` (`:123`) and `doorway_word`
(`:965`) at `group_frac` **1.000** — four 10-to-12-line
`switch`-returning-a-literal functions, structurally identical and
semantically unrelated (they map four different enums). D82 bound 3 and
the D75 addendum both say a small mapper stays a small mapper. Folding
them into a shared table-driven lookup would add a table, a length, and
a lookup for four functions a reader understands in three seconds each.
**This is the clone detector being right about the text and wrong about
the design, and the finding is that it should be left alone** — filed so
a later wave does not rediscover it and "fix" it.

---

## 4. A3 — THE CHECK-COUPLING ANNEX

What binds to the code a kit migration would move, measured at
`7d444f9e`.

### 4.1 Sabotage anchors

`tests/mech/sabotages/` holds **261 rows**. An anchor is a **verbatim
source-text block**: `SAB_BEFORE` must match the file byte for byte
(sample: `S-U10_cwmin_fixpoint_one_round.sh`, `SAB_BEFORE` quoting six
lines of `src/opt/callgraph.c`). Any reformatting of a line inside an
anchor breaks the row.

| `SAB_FILE` | rows |
|---|---|
| `src/gen/emit_vm.c` | **85** |
| `src/gen/emit_dfa.c` | **28** |
| `src/parse/parse.c` | 11 |
| `src/core/compile.c` | 10 |
| `src/opt/select_engine.c` | 9 |
| … (18 further files) | ≤ 8 each |
| `src/parse/rxt_source.c` | 3 |
| `src/parse/syntax_dump.c` | 1 |
| `src/parse/schema_dump.c` | 1 |
| `src/core/sb.c`, `src/gen/enc/enc.c`, `cli/main.c`, `axes_dump.c`, `limits_dump.c` | **0** |

**113 of 261 anchors (43.3%) live in the two emitter files**, and of
those **24 quote an `sb_*` or `snprintf` call verbatim inside
`SAB_BEFORE`** — those are the rows a fragment-layer migration breaks
directly and must re-aim. The remaining 89 emitter anchors quote
non-text code and survive a text-only migration, but any of them whose
block *abuts* a changed line must be re-verified, not assumed.

Per `BOILERPLATE.md`, a re-anchor needs its **intent re-verified**, and
anchors are copied from `git show HEAD:<path>` — so the re-aim cost is
per-row human work, not a script.

**The distribution is the migration order's justification**: steps 1 and
2 of §2.4 touch 2 anchors between them; step 3 touches 24 directly and
puts 89 more in its blast radius.

### 4.2 Checks that grep pcrec's own SOURCE text

**This number was measured twice, and the first measurement was wrong —
recorded because the correction is the useful part.** Grepping the test
tree for the literal string `src/gen/emit` returns 14 `tests/codegen`
scripts, and **every one of those hits is inside a COMMENT.** The real
checks reach source through a variable (`SRC="$ROOT_DIR/src"`,
`run_cpset_structure.sh:49`), so the literal-path grep cannot see them
and over-counts by finding prose instead. The honest instrument is "a
non-comment line whose command is `grep`/`sed`/`awk`/`nl`/`wc` and whose
argument resolves under `src/`, `cli/` or `lib/`."

Measured that way, **8 scripts in the whole test tree read pcrec source
text**, and **5 of them read `src/gen/`**:

| script | reads |
|---|---|
| `tests/codegen/run_atomic_identity.sh` | `src/gen/` |
| `tests/codegen/run_backref_identity.sh` | `src/gen/` |
| `tests/codegen/run_cpset_structure.sh` | `src/gen/` + `src/core/`, `src/parse/`, `src/opt/` |
| `tests/codegen/run_lookaround_identity.sh` | `src/gen/` |
| `tests/codegen/run_search_pinned.sh` | `src/gen/` |
| `tests/axes/run_axes.sh` | `src/` |
| `tests/registry/axes_registry_check.sh` | `src/` |
| `tests/rxtsource/run_rxtsource_tests.sh` | `src/parse/` |

**That is a materially smaller and more tractable coupling than the
first count suggested**, and it is good news for §2.4 step 3: the
overwhelming majority of `tests/codegen`'s 33 scripts grep **emitted
artifacts**, which a byte-neutral migration does not move.

The class has still bitten the tree before, and the incident is on
record: `bat4triage_report.md` found `run_cpset_structure.sh`'s
`[1c]`/`[2d]` needles going red because `[M5.0]` stage 4 *legitimately
moved the source text they grepped for* — *"a check-staleness class, not
a correctness regression."* So **all 8 must be read before step 3, not
after they go red** — and the five `src/gen/` readers are the ones a
fragment-layer migration can actually disturb.

### 4.3 abi-pinned scaffolding

`rx_info.abi` is **26** (`src/gen/emit_dfa.c:1965`). D76/D94 make any
change to emitted scaffolding an abi bump **plus** a re-pin of every
reader of the number, found **by grep** (D94 ruled exactly this after a
hand-enumerated four-site list missed a fifth reader in
`match_api.md`).

**Per finding, stated per the brief's instruction:**

- **L2-1 / L2-2 (the fragment layer, step 3): NOT an abi event.** A
  fragment that cannot truncate emits what a fragment that did not
  truncate emitted. The byte-identity gates prove it rather than the
  author asserting it. *This is the property that makes the biggest wave
  affordable, and if it is ever violated the wave has a bug, not an abi
  bump.*
- **L2-3 (the template layer, step 4): IS an abi event if attempted.**
  Every whitespace byte that moves is scaffolding. Full D76/D94 ritual —
  bump, grep every reader of `26`, re-pin the `(B)` whole-file pin, run
  `make test-codegen` before delivering. This is the single largest
  reason §2.4 recommends against a wholesale conversion.
- **L2-4 (dump rows, step 1): NOT an abi event.** `--list-*` output is
  not artifact text. It does have its own pins — `tests/rxtsource/
  run_rxtsource_tests.sh` asserts field counts per row and has already
  gone stale once on exactly this kind of change (`w23impl_report.md`'s
  `NF != 15` finding, whose failure message *"names a TAB in a field as
  the only possible cause"*). If step 1 changes any dump byte, that
  script is the first reader to check.
- **L2-5 (the CLI channel, step 2): NOT an abi event.** `tests/cli/`
  pins wording; D26 says the wording does not move.
- **L2-6 through L2-10 (§3):** rank 4 (table writing) is inside the
  emitted-text blast radius and **is** an abi event unless byte-neutral;
  ranks 1, 2, 3 and 5 are not.

### 4.4 One more binding the brief did not name

`battriage_report.md` recorded a **second reader class** the abi ritual's
grep does not cover: `tests/codegen/run_cpset_structure.sh`'s CHECK 3
manifest holds `EMITTED_BYTES` counts that **never cite an abi digit**
but whose values move whenever scaffolding does. A grep for the old abi
number cannot find it. Any wave that moves an emitted byte must check
that manifest explicitly; it will not be found by the ritual's own
search.

---

## 5. A1 — THE RULED-RECORD CHECK

Every finding was checked against `docs/dev/decisions.md` before filing.
The rows that bear on this lens, and how each finding stands with them:

- **D90** (*every numeric limit lives in `limits.def`; a new number is a
  table row, never a bare `#define`*). The 49 hand-sized buffers
  (finding L2-1) are bare numbers. `limits.h`'s own inclusion rule
  carves out *"structural constants … and local algorithmic bounds with
  proofs beside them,"* and a reader could file the buffer sizes under
  that carve-out. **The argument against it is in `limits.h` itself**: a
  buffer size is not a structural constant but a **re-derivation of one
  fact that is already a `limits.def` row** (`PCREC_MAX_EMIT_NAME_LEN`,
  `:134`), and `limits.h:65-68` says so — *"ONE size answers 'how big'
  at every such site instead of a fresh per-site guess that reopens K38."*
  The finding is consistent with D90 and strengthened by it.
- **D82** (*the layered emitted form; gcc compile time is an acceptable
  tradeoff*), especially **bound 3** (*only axes with ≥ 2 real forms get
  a representation object; no framework for its own sake*). This bounds
  §2's kit — every proposed function has ≥ 2 existing implementations —
  and it is the ground for **rank 5's recommendation of NO CHANGE**.
  D82 is also the model the kit imitates: *"decisions expressed as
  selection over candidates, not an if/then hierarchy."*
- **D76 / D94** (the abi ritual and its grep-found site list). Governs
  §4.3 and is the decisive argument against step 4.
- **D26** (PCRE2 diagnostic **wording** is the wrong tier to spend
  effort on). **My M6/L2-5 finding does not contradict D26 and must not
  be read as doing so**: it is about the *mechanism* (76 open-coded
  `fprintf` sites hand-writing one prefix), explicitly **not** about what
  any message says. The proposed `cli_err` migration keeps every word.
- **D58 / DD-12 (7)** (encodings are sealed backends; no encoding
  conditional in compiler, emitter or artifact). Finding L2-3 proposes
  **reusing** `pcrec_enc_emit_text`'s mechanism outside the seam. This
  does not touch D58: the ruling seals *which backend's text an artifact
  embedded*, and the interpolator is a text utility with no encoding
  knowledge in it. `enc.h`'s third-encoding recipe (*"Nothing in
  src/core, src/gen, cli/ or lib/ is touched"*) constrains what a
  **backend** may require, not where a **utility** may live — though
  moving the function to `src/core` and leaving a wrapper in `enc.c`
  would be the conservative spelling.
- **D2** (plain GNU make, on purpose). The kit adds at most one
  `.c`/`.h` pair; no build-system change is proposed or needed.
- **D77** (build under measurement). Honoured: §2.4 names the
  measurement that should precede each step, and step 4's measurement
  has **not** been taken by this lane, which is why step 4 is a
  recommendation against rather than a plan.
- **k49fix §2.3's deliberate twice-spelled boundary rule** (the charter
  names it as a live A1 example). Checked and **not** in conflict: that
  is a rule spelled twice *across the encoding seam* on purpose, with an
  agreement check tying the two spellings. Nothing in §1–§3 proposes
  collapsing it, and no finding here names `next_pos` or the emitted
  advance text.

---

## 6. ADDENDUM 2 — WHERE THE SWEEP STOPPED

Per the ratification addendum, no silent caps: this is what was reviewed
and what was not.

**Reviewed exhaustively.** The *mechanism* population, found by grep
rather than by census rank: every file in `src/`, `cli/`, `lib/`
containing an `sb_*`, stdio, or `snprintf` call — the 22-file census at
§1.0 is complete, not a sample. Within it, every `static` function
taking a `StrBuf *` in the two emitters (60+ in `emit_dfa.c`, 7 in
`emit_vm.c`) was enumerated, and every `char buf[N]` declaration in both
emitters was listed and sized.

**Reviewed top-down by length.** `tools/review/out/function_census.tsv`
(860 rows, length-ranked) was worked from row 1 down to **row 38,
`parse_case_body` at 88 code lines**, against lens 2's question. That
covers every function in the tree at or above 88 code lines, including
all nine census rows in the two emitters, both `cli/main.c` giants
(`main` 331, `cli_parse` 247), all four `rxt_source.c` rows, and both
`syntax_dump.c`/`axes_dump.c` rows.

**Not reviewed individually.** The remaining ~822 census rows below 88
code lines were **not** read function by function. They were screened by
the §1.0 grep census, which is exhaustive over the mechanism this lens
is about — a function with no `sb_*`, stdio or `snprintf` call produces
no text and cannot carry a text-emission finding. Findings below the
length cut were admitted only where a clone-detector row or a grep hit
pointed at them (ranks 3, 4 and 5 in §3 all arrived that way).

**The residual risk in that screen, stated honestly.** It is blind to a
policy-inlines-mechanics instance that is *not* about text — a manual
loop where a shared walker belongs, an ad-hoc sort, an open-coded
bisection. Rank 3 (growable append) was caught only because the clone
detector found it, which suggests there are more of that shape. **A
second pass over the census's 88-and-below tail, aimed at non-text
mechanics, is the trigger ADDENDUM 2 asks me to name**, and lens 1's
sweep may already cover it — that is a synthesis question, not a gap
this lane should fill by guessing.

**Not in scope by charter.** `tests/lib/`, `tests/harness/` (secondary
tier, dispositioned to next round); emitted C; `studies/`; `docs/`.

---

## 7. FINDINGS (A4 vocabulary)

| id | finding | severity | effort | blast radius |
|---|---|---|---|---|
| **L2-1** | 49 emitter fragment buffers hand-pick a size where `PCREC_MAX_EMIT_NAME_LEN` exists; `snprintf` truncates silently and K38 is the recorded miscompile of exactly this. (`emit_vm.c` 41, `emit_dfa.c` 8; comments at `emit_vm.c:944`, `:6813`, `:10765`) | **CORRECTNESS-RISK** | LOCAL (as a size sweep) / CROSS-CUTTING (as the `txt_f` fold) | 2 files; 24 sabotage anchors directly, 89 in radius; 5 of the 8 source-grepping checks; **no abi event** |
| **L2-2** | No fragment primitive exists. ~105 `snprintf`-into-`char[N]` sites re-derive "how big" and "did it fit"; `vm_rolef` (`emit_vm.c:754`) is 90% of the primitive and truncates at 160 anyway (`:764-765`) | MAINTAINABILITY | CROSS-CUTTING | as L2-1 (same wave) |
| **L2-3** | The taught primitive for prefix interpolation **already exists** (`pcrec_enc_emit_text`, `enc.c:88-94`, 2 call sites) while the two emitters perform the identical operation across **652 `%s_` substitutions** on 450 lines (`emit_vm.c` 347, `emit_dfa.c` 305) | MAINTAINABILITY | **DESIGN-EVENT** | emitted bytes move ⇒ **abi bump + full D76/D94 re-pin**. §2.4 recommends AGAINST until the run-length population is measured (D77) |
| **L2-4** | Five independent TSV row emitters; two incompatible escapers; **three dump files escape nothing**, and the corruption they are exposed to is already diagnosed in a fourth (`rxt_source.c:3735-3742`). `syntax_dump.c` has an escaper its TSV path does not call | MAINTAINABILITY (+ latent CORRECTNESS-RISK) | LOCAL | 5 files; **2 sabotage anchors**; `tests/rxtsource` field-count pins; no abi event |
| **L2-5** | `cli/main.c` has no diagnostic channel: 76 open-coded `fprintf(stderr, …)`, 72 hand-writing `"pcrec: "`, `"missing value for %s"` × 8 — while the library side has exactly one `ctx_fail` | MAINTAINABILITY | **MECHANICAL** | 1 file; **0 sabotage anchors**; `tests/cli` wording pins (D26: wording unchanged); no abi event |
| **L2-6** | `cli_parse` is a 64-arm `if`/`else if` chain over 62 option spellings; the file's own `raise_only_limits[]` comment (`:48-65`) argues for the table it did not generalize; `usage`'s 162 literal lines (`:101-262`) have no machine relation to the chain | MAINTAINABILITY | CROSS-CUTTING | 1 file; 0 anchors; `tests/cli`; no abi event |
| **L2-7** | 8 valid-value menus, 1 table-driven. `--tune`'s (`:614-616`) is a second spelling of `tune.c`'s alias table, which D103 makes the dial's one home | MAINTAINABILITY | LOCAL | 1 file + 2 registries; no abi event |
| **L2-8** | Growable-array append has 7 open-coded copies (clone groups 10 and 3; four at `group_frac` 1.000 in one file) | POLISH | LOCAL | 3 files; **shared with lens 1 — dedupe in synthesis** |
| **L2-9** | DFA table *writing* is unfactored (clone groups 11 and 7, `group_frac` to 1.000) though table *selection* is the tree's exemplary taught primitive (D82 layer 1) | POLISH | LOCAL | `emit_dfa.c`; inside the 113-anchor radius ⇒ ride step 3 or skip |
| **L2-10** | Four `group_frac` 1.000 enum→string mappers in `syntax_dump.c`. **RECOMMEND NO CHANGE** — D82 bound 3 / D75 addendum. Filed so a later wave does not "fix" it | — (anti-finding) | NONE | none |

**Synthesis ranking per A4** (MECHANICAL+safe first, DESIGN-EVENT last):
L2-5 → L2-4 → L2-7 → L2-8 → L2-1 → L2-2 → L2-6 → L2-9 → L2-3.
L2-10 is a standing do-not.

---

## 8. NOTE TO LENS 10

Lens 10 (emission-kit unification, chartered as likely refactor wave 1)
charters **from** this map. Three things it should take as given and one
it should not:

- **Take**: the mechanism census (§1.0) is exhaustive over the primary
  tier and was built by grep; the anchor distribution (§4.1) is the cost
  model; the byte-neutrality property of the fragment layer (§4.3) is
  what makes wave 1 affordable.
- **Do not take**: §2.4 step 4 (the template layer). It is the largest
  readability win in the map and it is an abi event, and **the
  measurement that would justify it has not been taken.** A wave plan
  that schedules it on the strength of this report would be building
  ahead of a measured need (D77). Name the measurement; do not name a
  date.
