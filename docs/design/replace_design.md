# Search/replace — the variable layer over a ruled substitution design

**Status: PROPOSED, over a RULED baseline.** Design only; nothing under
`src/`, `cli/`, `lib/` or `tests/` was touched.

## 0. Read this section before any other

**This note does not design substitution. `docs/design/subst_template_design.md`
already did, and D38 (2026-08-14) ruled all fourteen of its open questions.**
That note is 1,256 lines, its measurements were taken against libpcre2 10.46
with twelve predictions stated before the first run, and three of them were
refuted. It is the design of record for `[M4-SUBST]`.

Its scope, in its own words: *the `pcre2_substitute` capability as an AOT
artifact — pattern AND replacement template compiled together into one emitted
C function (match + splice), first/global modes, caller-buffer zero-allocation
mode plus an output-sizing mode.*

So this note's actual job is narrow and it is stated here so nobody re-opens
settled ground:

1. **§1 records what is already ruled**, in a table, so a reader can tell at a
   glance which parts of the charter are asking for something that exists.
2. **§2 adds the one genuinely new thing**: the caller's variable environment
   reaching the replacement side, which `subst_template_design.md` predates
   and does not contemplate.
3. **§3 answers the charter's brainstorm list** against that baseline, one
   verdict per item.
4. **§4 settles the call interface** with variables in it, against §5.2's
   ruled surface.

**Three findings decided the shape of this note**, and each corrects a premise
in the charter:

- **The shell style and PCRE2's `SUBSTITUTE_EXTENDED` style are the same
  style** (§1.2). `${n:-default}` and `${n:+alt}` are bash's operators,
  spelled identically, because PCRE2 borrowed them from shell. The charter
  asks me to "pick the pcrec syntax = the shell style... and state every
  departure from PCRE2." For those two forms there is no departure to state;
  they are already ruled in, verbatim.
- **"Callouts that return strings? I think we support that" — the callout ABI
  does not, and a different, already-ruled mechanism does** (§3.1). Callouts
  are match-or-fail only, ruled at D38 and enforced at every generated call
  site with `__builtin_trap()`. The string-returning sibling is `rx_renderfn`,
  ruled at D38 Q13, already carried in `docs/spec/match_api.md` §2, with its
  `out == NULL` sizing convention already specified. It is designed and
  reserved, not built — which is a different answer from "we support that."
- **The two-call overflow protocol the charter asks me to weigh is the one
  PCRE2 shape D38 deliberately declined** (§4.1), and the ruled replacement is
  strictly better: one function, `out == NULL` for sizing, the required
  capacity *always* reported. There is no argument left to have; there is a
  ruling to cite.

---

## 1. What is already ruled

### 1.1 The rulings, as a table

Every row is **[RATIFIED]**. Section numbers are into
`subst_template_design.md`; question numbers are its §9, all ruled by D38.

| topic | ruled | where |
|---|---|---|
| `$0` / `${0}` is the whole match | core tier | Q1 |
| `$n` / `${n}` is capture group *n* | core tier, resolved and **bounds-checked at compile time** | §3.1, §4 |
| `${name}` is the named group | core language tier, gated additionally on module `named-groups` | §3.1 |
| bare `$name` (no braces), greedy, PCRE2-exact | supported — the compile-time check defuses the footgun | Q2 |
| `$$` is a literal `$` | core tier | §3.1 |
| a backslash is an **ordinary literal byte** in the core tier | **[MEASURED]** PCRE2 behaviour, not a simplification: `x\ny` is five bytes without `EXTENDED` | §3.1 |
| `\n` `\x41` `\$` `\u` `\l` `\U` `\L` `\E` | module `subst-extended` | §3.3 |
| `${n:-word}` and `${n:+yes:no}` | module `subst-extended` | §3.3 |
| case forcing is a **pending operator on the output byte stream**, not on the next template item | **[MEASURED]**, three corners a naive design gets wrong | §3.3 |
| an UNSET but existing group renders as | **a generation axis, default empty** | Q3 |
| output buffer | **length-only, no NUL termination, no NUL budget**, 8-bit clean | Q4 |
| the pcrec-only extension namespace | **`${!...}` reserved**, on a **testable rule**: every pcrec-only template form must be a spelling PCRE2 rejects | Q5, §7.1 |
| callback template segments | `rx_renderfn(const rx_ctx *, unsigned char *out, size_t cap) -> ptrdiff_t`, `-1` fails, `out == NULL` returns the length it would produce | Q13, §7.2 |
| sizing mode | **exact by contract**; renderers must honour `out == NULL` and be deterministic across the two passes | Q11 |
| where the template comes from | **`--replace` now, repeatable**; `[V-E]`'s manifest gains a template field when that design lands | Q7 |
| first vs global | **a generation axis, not a flag** — two functions that differ in code, not in a branch | §5.3 |
| the global empty-match rule | **[MEASURED]**, and it refutes the intuitive reading | §6.1 |
| `pcrec_error` gains a which-input tag | landed: `pcrec_err_input` with `PCREC_ERR_INPUT_TEMPLATE` is **in `lib/pcrec.h` today** | Q8 |
| module tiering | `subst` / `subst-extended` / `subst-pcrec` | §3.0 |
| UTF | byte offsets throughout; global-mode step width is `[M5]`'s only change | Q9 |
| duplicate group names under `(?J)` | deferred, lands with module `named-groups` | Q10 |
| `--no-captures` × a `$n`-referencing template | a **compile-time** error | D44.7 |

### 1.2 The shell style is already the ruled style

The charter asks for bash/zsh-style syntax on the replacement side. Setting
the two vocabularies side by side:

| bash | PCRE2 `SUBSTITUTE_EXTENDED` | pcrec (ruled) |
|---|---|---|
| `${name}` | `${name}` | `${name}` — the named group |
| `${n:-word}` | `${n:-word}` | same, `subst-extended` |
| `${n:+word}` | `${n:+yes:no}` (and one-armed `${n:+yes}`) | same, `subst-extended` |
| `${name:?word}` | — | `subst-pcrec` (§3.4) |
| `${name#pat}` `%` `^^` `,,` `:off:len` `${#name}` | — | `subst-pcrec` (§3.4) |

The first three rows are identical across all three columns. So the charter's
instruction and D38's ruling agree, and the honest statement is not "pcrec
picks the shell style over PCRE2's" but **"PCRE2 already uses the shell style
for the forms it has, and pcrec extends it with the forms it does not."** Every
extension lands in `subst-pcrec` under Q5's already-ruled namespace rule.

### 1.3 The departures from PCRE2, collected

D26 requires each to be tiered. There are five and they are all tier 3 (API
shape and error timing), none tier 1 (what a pattern matches):

1. **The `EXTENDED` dialect is a module, not a run-time bit.** D18: the
   template is baked in, so the dialect is a singleton dimension by
   construction and can never become a generation axis. §3.4 there.
2. **`SUBSTITUTE_LITERAL` is not an option.** It is the degenerate template
   compiler — a template with no `$` — and needs no code. **[MEASURED]** in
   PCRE2, `LITERAL` *beats* `EXTENDED` when both are set.
3. **`SUBSTITUTE_UNKNOWN_UNSET` has no analogue.** References resolve at
   compile time, so there is no run time at which a name can be unknown. An
   unknown name is a build error. This is the AOT win the plan row names.
4. **Output is length-only, no NUL.** Q4. PCRE2 terminates, requires room for
   the terminator, and **[MEASURED]** reports the length *inclusive* of it on
   overflow but *exclusive* on success — the same variable meaning two things
   depending on the return value. pcrec's `*outlen` means bytes produced on
   success and capacity required on overflow, uniformly.
5. **Sizing is not an option you must remember to pass.** §4.1.

None of these changes what a replacement *produces* for a given match and
template, which is the tier that is exact.

---

## 2. The variable layer — the one new thing

`subst_template_design.md` predates the variable charter and contemplates one
source of values: the match. The addition is a second source: the caller.

### 2.1 The spelling

**[PROPOSED]**, and it costs no new ruling because D38 Q5 already reserved the
namespace it uses:

> In a replacement template, `${!name}` is the caller's variable `name`.
> A bare `${name}` remains the capture group, exactly as ruled.

`variables_common.md` §1.4 carries the argument; the short form is that the
brace namespace on this side is fully occupied by the match's own groups, so a
caller variable cannot spell itself `${name}` here without colliding with a
ruled production. `${!...}` is reserved, is **[MEASURED]** rejected by libpcre2
10.46 in both dialects, and satisfies §7.1's testable namespace rule.

By that rule's own terms, `${!name}` is module `subst-pcrec`.

### 2.2 The operator suite reaches both selectors

**[PROPOSED]** every operator applies to either selector, with no per-selector
table:

```
    ${1:-none}        group 1, or "none" if it is unset or empty
    ${!prefix:-dev}   the caller's variable, or "dev"
    ${!user^^}        the caller's variable, uppercased   (subst-pcrec)
    ${1:0:3}          the first three bytes of group 1     (subst-pcrec)
```

This is what makes the charter's "the syntax should be the same" true in the
place it matters: one grammar, one evaluator, one value model
(`variables_common.md` §2), reaching two selector namespaces. The UNSET/EMPTY
distinction is the same distinction on both sides — `{-1,-1}` for a group that
did not participate, `p == NULL` for a variable the caller left unset — which
is why `:-` and `-` mean the same thing regardless of which selector precedes
them.

### 2.3 What a variable does *not* change

Three things, stated because each is a plausible assumption:

- **It does not change the unset default.** D38 Q3's generation axis
  (default empty) governs groups *and* variables on this side. The pattern
  side's refusal default (`variables_pattern.md` §5) is the deliberate
  asymmetry, and it does not leak here: in a template, rendering empty
  produces visible wrong output, not a silently wider language.
- **It does not force any engine.** A template variable never touches the
  matcher; it is spliced into the output. Only a *pattern* variable forces the
  VM.
- **It does not interact with `--no-captures`.** D44.7's compile-time error is
  about `$n` references; `${!name}` references nothing the matcher produces, so
  a `--no-captures` artifact can carry a variable-bearing template and that is
  a useful combination (a template that reads only the caller's environment
  and the whole match).

---

## 3. The brainstorm, item by item

One verdict each: **MVP**, **ROADMAP** (with what would open it), or
**DECLINE** (with the reason).

### 3.1 Callouts that return strings

**Verdict: already ruled as `rx_renderfn`; ROADMAP (phase 3).**

The charter says "I think we support that." The precise state of the tree:

- **The callout ABI does not carry a string return, and deliberately.**
  `design_callout_abi.md` §2 ruled native callouts **match-or-fail only**:
  `rx_matchfn` returns a length or `-1`, and values below `RX_ERR_FLOOR` are
  reserved and **enforced today** at every generated call site with
  `if (ret < RX_ERR_FLOOR) __builtin_trap();`. `abort()` and `longjmp` were
  both considered and rejected with reasons. F4 in that note's freeze list is
  the same rule from the match-API side.
- **`rx_renderfn` is the string-returning sibling and it is ruled.** D38 Q13:
  `rx_renderfn(const rx_ctx *, unsigned char *out, size_t cap) -> ptrdiff_t`,
  `-1` to fail, `out == NULL` returning the length it would produce while
  writing nothing. `docs/spec/match_api.md` §2 carries it today as an ABI
  type: *"Emitted ONLY when a substitution template names it."*
- **So a "replacement callout" is exactly `(match, group spans, user) → bytes`,
  and that is what `rx_renderfn` is.** It takes `const rx_ctx *`, which carries
  the subject, the position, the capture array and `void *user` — so the
  callback chooses its own group rather than being handed a pre-selected one,
  which the first draft's bespoke signature could not do. D38 Q6 subsumed the
  user-data question into the `rx_callout_ref` binding unit.

What the variable layer adds is one line: a renderer should also see the
caller's environment. **[PROPOSED]** it does, by the same route the captures
take — the `rx_ctx` the renderer already receives gains nothing, and the
renderer reads variables through `ctx->user` if it needs them, because a
renderer that wants the environment is a renderer the *embedder* wired to it.
Adding a `vars` member to `rx_ctx` would change a fixed-literal ABI type
shared by every artifact to serve the minority that needs it — the exact
change D38 §1.1 recorded Frank rejecting ("ouch").

**[OPEN]** §5 Q2 records the alternative.

### 3.2 Case transforms

**Verdict: `\U \L \E \u \l` are MVP-adjacent (ruled `subst-extended`);
`${!n^^}`-style operators are ROADMAP.**

D38 already ruled the PCRE2 forms, with **[MEASURED]** semantics including the
three corners (a pending force skips an empty group and lands on the next
literal; a one-shot force *cancels* an active run rather than nesting; a run
spans `$n` boundaries and literal text alike).

`subst_template_design.md` §7.3 already argues against the operator form and
this note agrees: a pcrec `${!upper:1}` would be **redundant with** `\U$1\E`
and "should be justified on ergonomics or not built." The bash operators
`^`/`^^`/`,`/`,,` are worth having only because the *pattern* side has no
`\U` equivalent (`variables_pattern.md` §6.3), so the operator earns its place
there and rides along here for one grammar. ASCII-only, refusing by name under
`-e utf8` until a 1:n case-mapping table exists — the same restriction the
pattern side takes and for the same reason.

### 3.3 Substring `${n:off:len}`

**Verdict: ROADMAP.** Cheap on this side (a group's span is already a pair of
offsets, so a substring is arithmetic on them, no copy). What it needs before
building is a stated want, not a measurement: nothing in the corpus or the
bench asks for it. D77.

One correctness note for whoever builds it: under `-e utf8` an offset is a
*byte* offset by D38 Q9's ruling that the template compiler is encoding-blind,
so `${1:0:3}` can split a character. **[PROPOSED]** it refuses rather than
splitting — a truncated character is a malformed output, and producing one
silently is the shape §2.3's UTF-8 validation rule exists to prevent.

### 3.4 Default and alternate on unset groups

**Verdict: MVP on the variable selector, already-ruled `subst-extended` on the
group selector.**

`${n:-}` / `${n:+}` are D38-ruled. `${!name:-}` / `${!name:+}` are the same
operators over the other selector and come free with §2.2's one grammar.
`${name:?word}` is new on both selectors and is the loud one — **[PROPOSED]**
it fails the substitution (returning the template's own error, not a match
failure), which is the template-side analogue of the pattern side's refused
call and lands in `subst-pcrec`.

### 3.5 A per-match counter

**Verdict: ROADMAP, and the spelling matters more than the feature.**

Numbering replacements (`${#}` as the 1-based match index in a global
substitution) is genuinely useful and genuinely cheap — the emitted global
loop already carries the count as its return value (`subst_template_design.md`
§5.2: "Count as the return value... it is what a caller actually wants to
branch on"), so the number exists and is not currently readable from a
template.

But `${#name}` is bash's **length** operator (§1.2's table), so `${#}` and
`${#name}` would be two unrelated operators distinguished only by whether a
name follows — which is exactly the greedy-name ambiguity D38 Q2's measurement
found in `$name`. **[PROPOSED]** spell the counter `${!n}`-free and distinct —
e.g. `${!index}` as a *reserved variable name* rather than a new operator, so
it rides §2.1's namespace with no grammar change at all. That is the general
mechanism: a counter is a variable the engine sets, not a new syntactic form.

### 3.6 Conditional replacement (if-then-else)

**Verdict: MVP for the two-armed form, because PCRE2 already has it.**

**[MEASURED]** at `subst_template_design.md` §3.3: `${n:+yes:no}` is PCRE2's
own two-armed selector and the one-armed `${n:+yes}` is also valid. So the
if-then-else the charter asks about is a ruled `subst-extended` form, not an
extension. Nothing to design.

The richer form — a predicate over the value rather than over its
set/unset-ness — is `design_callout_abi.md` §3's **embedded code** direction
(Frank's `\{ strlen($1) == 5 }` sketch), which that note records as *distant
future* with its restriction set explicitly TBD, and which §6 Q6 there leaves
open by Frank's own ruling. **DECLINE** for this design; it is a different
feature with a different open question, and `rx_renderfn` (§3.1) is the escape
hatch that covers its use cases today without a new language.

### 3.7 Recursion and nesting limits

**Verdict: MVP, as a `limits.def` row.**

`variables_common.md` §1.7: nesting is permitted in the `word` position only,
bounded at **compile time**, because the template is parsed when the artifact
is built. So there is no run-time recursion in the emitted code and the bound
is an ordinary `src/core/limits.def` row — visible to `--list-limits`,
raisable by the documented mechanism, and read by the D107 limits detector for
free.

The thing to *not* build: a run-time recursion depth counter. There is nothing
recursive at run time to count.

### 3.8 The global loop and empty-match advancement

**Verdict: MVP, ruled, and do not re-derive it.**

`subst_template_design.md` §6.1 is **[MEASURED]** against libpcre2 and it
**refutes the intuitive rule**, which is why this note cites it rather than
restating it in its own words:

> An empty match is suppressed **only at the position where an empty match was
> just produced** — not at the end of a non-empty match.

The discriminating cell is `a*` on `"aab"` with replacement `[$0]`, which
gives `[aa][]b[]` and not `[aa]b[]`. A design that suppresses at the previous
match's end is wrong by one substitution, and that was the note's own
prediction P10 before it was measured.

**One thing worth flagging for whoever implements it**, because it is a
genuine seam and neither note owns both sides: `docs/spec/match_api.md` §3.1's
*caller-driven* find-all loop is explicitly **lossy** relative to PCRE2 and
python for empty-preferring patterns — it has no way to express PCRE2's
"NOTEMPTY_ATSTART retry," so its result is always a strict subset. §6.1's
emitted loop *does* express the retry ("that search is retried not-empty-at-
start and anchored"). So the emitted substitution loop is **not** the §3.1
loop with a splice in it, and building it that way would produce a different
substitution count on exactly the empty-preferring patterns §6.1 measured.
`[PC-5]` already classifies `NOTEMPTY`/`NOTEMPTY_ATSTART` as `EMITTED-LOOP`
for this reason. **[PROPOSED]** the implementation note for `[M4-SUBST]` states
this seam explicitly; it is the kind of thing that reads as a defect when
found later.

**The variable layer inherits four empty-match-advancement gaps from the
ruled baseline, stated here explicitly rather than left implicit.**
`subst_template_design.md` §6.1's rule is oracle-verified for two axes —
empty match after a non-empty match (the rule's whole point) and empty match
at end (the `"aab"` example's trailing `[]`) — with empty match at start
implicit in the same trace (`"bab"`'s empty match at offset 0). Four more are
**explicitly** marked open in that ruled baseline, and this note does not
reopen them, only names them so the variable layer's own inheritance is on
the record rather than silent:

- **`\G`** — cited, not solved, deferred to `[DD-4]` (`subst_template_design.md`
  §6.2, "whichever lands second must not introduce a second copy of it").
- **UTF-8 mid-codepoint advancement** — deferred entirely (`subst_template_design.md`
  §6.2, "a step-width question in the emitted loop... Deferred entirely"), in
  contrast to `docs/spec/rxt_format.md`'s own `mc` find-all count, which
  states the identical-shaped rule NORMATIVELY — the eventual
  `[M4-SUBST]` implementation should reuse that rule rather than re-derive
  it.
- **Newline/CRLF conventions inside the loop** — deferred to `[DD-11]`
  (`subst_template_design.md` §6.2, "the probe does not exercise it,
  deliberately... `[DD-11]` owns `NEWLINE`/`BSR`").
- **Lookbehind-anchored interaction with the global loop** — not discussed in
  either the ruled baseline or this note before now; recorded here as a
  fifth open item with no owner yet named.

None of these four are variable-specific, and `[DD-4]`/`[DD-11]` are
pre-existing dependencies of the ruled baseline this design correctly
declines to re-litigate. But the variable layer makes the UTF-8 question
MORE material than it was: a caller-supplied variable's bytes are spliced
into the output stream at exactly the position the deferred step-width
question governs, so caller-controlled multi-byte content is a new way to
exercise a rule nobody has built yet — worth a note for whoever opens
`[M4-SUBST]`, not a design change here.

### 3.9 A `--replace` `.rxt` block kind

**Verdict: MVP, and this note PROPOSES rather than rules.**

`subst_template_design.md` §8.1 already proposes the shape, in the existing
directive grammar: a block-scoped `repl <template>` beside `flags`/`features`,
with `s "<subject>" "<expected>"`, `sg` for global, and `serr` for a template
that fails to compile. The `<expected>` field reuses the existing quoted-subject
escape set unchanged, which matters because substitution output is exactly
where an embedded NUL or newline needs writing down.

**The variable-binding directive itself lives in `variables_common.md` §3.5,
not here** — the underlying `rx_var` array is shared between the pattern and
replacement consumers (§4.2 below), and a test author reading this note
needs one pointer to the shared binding mechanism rather than a
substitution-scoped proposal that a pattern-side reader (`variables_pattern.md`
proposes no `.rxt` syntax of its own) would have no reason to find. In brief:
`var <name> "<value>"` (block-scoped, repeatable) and `var-unset <name>`
(declares the slot UNSET, a state distinct from `var name ""`'s EMPTY,
`variables_common.md` §2.2) bind a variable identically whether the block is
a bare `m`/`n` match case or a `repl`-bearing substitution case.

**This does not rule the spelling.** Memory `pcrec-dd13b-syntax-is-managers`:
`.rxt` format spelling and syntax are the manager's call, and the machinery a
new production must satisfy is real — a `rxt_schema.def` row with its ten
columns, and agreement across all three parser legs (`pcrec` itself,
`tests/harness/run.sh`, `tests/harness/verify_rxt.py`), checked by W23-S3.
`docs/spec/rxt_format.md`'s graduation rule also offers the staging path: an
`ext` block can carry this before it is a production, and must graduate "the
day something in an `ext` block needs pcrec to ACT on it."

---

## 4. The call interface

### 4.1 The output protocol — ruled, and the charter's three options collapse to it

The charter asks me to argue two-call overflow versus a caller-supplied
allocator versus a callback sink. D38 already ruled, and the ruling is none of
the three as stated — it is the two-call protocol's two calls **merged into
one function**:

```c
/* On entry *outlen is the capacity of out; on return it is the number of
 * bytes produced. Returns the number of substitutions (0 = no match, subject
 * copied through), or RX_SUBST_NOSPACE with *outlen set to the capacity that
 * would suffice. out may be NULL: nothing is written, *outlen receives the
 * required capacity. Allocates nothing, ever. */
int rx_subst(const unsigned char *s, size_t n,
             unsigned char *out, size_t *outlen);
```

Why this beats the plain two-call protocol, in the ruled note's own terms:
**[MEASURED]** PCRE2 without `OVERFLOW_LENGTH` returns `-48` on an undersized
buffer and sets the length to `PCRE2_UNSET` — *the caller learns nothing*, and
must have remembered to pass an option to learn anything. Always reporting the
required capacity costs one `size_t` store on a path that is already failing,
and removes an option. `out == NULL` is the same idea reached from the other
end, and it is the pre-flight call.

- **A caller-supplied allocator: DECLINE.** "Allocates nothing, ever" is the
  embedded-niche property and the reason this is an AOT compiler. An allocator
  hook re-introduces allocation and a failure mode, to save a caller one call
  they can already skip by sizing generously.
- **A callback sink: ROADMAP**, and it is already offered rather than invented
  — §7.2 option (c), `rx_subst_to(s, n, sink, ctx)`. Its trigger is stated
  there: it *"composes with `[M3]` later and removes the buffer-sizing question
  entirely,"* and writing straight to a socket or a `FILE *` is the embedded
  story. D77-shaped: build it when `[M3]` (streaming) arrives, not before.

### 4.2 Variables on the entry

**[PROPOSED]**, by the same rule the pattern side takes, so that there is one
rule and not two:

```c
int rx_subst(const unsigned char *s, size_t n,
             unsigned char *out, size_t *outlen,
             const rx_var *vars);
```

The parameter appears **only on artifacts whose template names a variable**,
which is D18's rule unchanged (a fixed choice is compiled away) and which
means a variable-free substituter is byte-identical to the ruled surface. The
index macros are shared with the pattern side: one `<PREFIX>_NVARS`, one
`<PREFIX>_VAR_<NAME>` per name, over the union of the names the pattern and
the template mention — which is the right union, because a single artifact can
carry both a pattern variable and a template variable and they should share a
namespace and an array.

`vars` goes last, after `outlen`, so the ruled parameter positions do not move.

### 4.3 First and global

**[RATIFIED]** §5.3: a **generation axis**, not a flag. `{first}` emits
`rx_subst`; `{global}` emits `rx_subst`; `{first, global}` emits
`rx_subst_first` and `rx_subst_all`. The two genuinely differ in code — the
first-match form has no loop, no carried position and none of §6's empty-match
machinery — so a run-time flag would put the whole global state machine into
the first-match path and pay for it on every call. D18 forbids exactly that
trade.

### 4.4 The generated shape

**[RATIFIED]** §5.5: nothing ties one pattern to one template. The splice code
is per-template, the matcher is per-pattern and shared, so `rx_subst_redact`
and `rx_subst_expand` over one matcher is the same named-entry-point
mechanism and needs no new machinery. Q7 ruled `--replace` repeatable on that
basis.

**[PROPOSED]** the template compiles to a small program at build time, exactly
as the pattern does — a sequence of segments, each a literal run, a group
reference, a variable reference, or a renderer call — and the expansion half
of `variables_common.md` §5 is what evaluates a segment's operators. One
program form, two sources of value. This is the charter's "the replacement
TEMPLATE compiled to a small program at compile time, like the pattern," and
it is what makes the operator suite shareable rather than duplicated.

Note the constraint that shapes packaging: **D88, one artifact per emitted
file, always.** Composition is linking, never a multi-pattern translation
unit. So several templates over one matcher is several entry points in one
file (one artifact), and several *patterns* is several files.

---

## 5. Open questions

Numbered; recommendations are this note's, not rulings. Questions already
ruled by D38 are not re-opened here.

1. **Is `${!name}` the right spelling on this side?** §2.1 spends D38 Q5's
   reserved prefix. The alternative is a distinct sigil for caller variables
   (`@{name}`, say), keeping `${!...}` free for later extensions.
   *Recommend `${!name}`*: Q5 reserved the prefix for pcrec extensions
   generally and this is the extension with the widest reach; the remaining
   namespace after it is still large.

2. **Does a renderer see the variable environment directly?** §3.1 routes it
   through `ctx->user`, refusing to add a member to a fixed-literal ABI type
   shared by every artifact. The alternative is a `vars` member on `rx_ctx`,
   which is a D38 §1.1-shaped decision ("it changes the signature for every
   caller to serve the minority that needs it") and belongs on the ABI side,
   ruled once, not twice. *Recommend: rule it in `design_callout_abi.md`, and
   `ctx->user` in the meantime.*

3. **The counter's spelling.** §3.5 proposes a reserved *variable name* rather
   than a new operator, to avoid colliding with bash's `${#name}` length
   operator. *Recommend as proposed*, but the reserved-name mechanism is new
   and needs its own rule (which names are reserved, and what happens when a
   caller supplies one).

4. **Does `${1:0:3}` refuse or split under `-e utf8`?** §3.3 proposes refuse.
   The counter-argument is that D38 Q9 ruled the template compiler
   encoding-blind, and a refusal is an encoding-aware behaviour appearing in a
   component ruled not to have one. *Recommend: refuse, and note that the
   refusal is a compile-time property of the artifact's declared encoding
   rather than a run-time branch* — which keeps Q9's "no encoding conditional
   in the emitted artifact" intact.

5. **The `.rxt` production's spelling and staging.** §3.9 proposes `var` /
   `var-unset` beside §8.1's `repl` / `s` / `sg` / `serr`, and explicitly does
   not rule. The manager's call, per memory `pcrec-dd13b-syntax-is-managers`;
   the `ext`-then-graduate path is available if the format work is not ready.

6. **Does `[M4-SUBST]`'s streaming holdback survive a variable?** That row's
   2026-09-06 sharpening sizes the holdback buffer from `cwmax`/`maxw`, and
   `variables_pattern.md` §2 makes a *pattern* variable's `maxw` unbounded.
   So a var-bearing pattern would refuse streaming by that row's own honest-
   refusal rule. That is probably correct and it is certainly a consequence
   nobody has written down. *Recommend: confirm it is the intended reading
   when `[M4-SUBST]` opens*, rather than discovering it at build time.

---

## 6. The four lenses

| lens | verdict |
|---|---|
| **specific vs general** | **GENERAL**, and mostly by *not adding*. The substitution design was already ruled; this note adds one selector to an existing grammar and one parameter to an existing entry, and routes every brainstorm item either to a ruled mechanism (`rx_renderfn`, `${n:+yes:no}`, the generation axis) or to an existing module tier. The one place it resists a specific mechanism is §3.5, where a counter becomes a reserved variable name rather than a new operator. |
| **core vs derived** | **DERIVED.** Nothing in the matcher moves. The template compiler is, in `subst_template_design.md` §1's **[MEASURED]** argument, a pure function of the template text and the *shape* of the capture data — it never needs a matcher, and the variable layer does not change that: a variable is a second source of bytes for a splice that already exists. |
| **applicable vs assumption-changing** | **APPLICABLE.** A variable-free template is byte-identical to the ruled surface (§4.2's parameter appears only when named). The one assumption this note *tests* rather than changes is §3.8's: that the emitted global loop is the §3.1 caller loop with a splice — it is not, and saying so now is cheaper than finding it in a substitution count later. |
| **fits-arch vs refactor** | **FITS**, and more cleanly than the pattern side, because the hooks are already cut: `pcrec_err_input.PCREC_ERR_INPUT_TEMPLATE` is **in `lib/pcrec.h` today** with no producer, `rx_renderfn` is in `docs/spec/match_api.md` §2 today with no producer, `${!...}` is reserved today with no spender, and the module names `subst`/`subst-extended`/`subst-pcrec` are ruled. This note spends three of those four reservations on what they were reserved for. The packaging constraint (D88, one artifact per file) is satisfied by §4.4 without a change. |
