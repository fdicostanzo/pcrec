# Inline code in patterns — design ([INLINE-C], pattern side)

**Status: PROPOSED, rev 0 (lane inlinecdes, 2026-10-26).** Design only: no
build go, nothing under `src/`, `tests/` or `docs/spec/` touched. Inputs:
`docs/design/inline_c_requirements.md` (the requirements, whose section 8
"Frank's answers" Q1-Q8 are BINDING here), `docs/design/design_callout_abi.md`
(D38), plan rows [INLINE-C] and [M4-CALLOUTS] (D36), `docs/spec/match_api.md`,
`docs/spec/rxt_format.md`, the parser registry, the engine selector and the VM
emitter as they stand at `570b601d6`. Spelling choices below are the manager's
to change (memory "dd13b syntax is manager's"); section 10 holds the few that
are Frank's. Ids in this note (`S-IC*`, `D-IC*`) are PLACEHOLDERS.

Facts re-measured for this note (libpcre2 10.46 probe, `build/probe/`,
uncommitted; and `build/pcrec` at main): PCRE2 refuses `(?{x})` and `(??{x})`
(error 111, "unrecognized character after (? or (?-") and `(*{x})` (error
160); it accepts ``(?C`c: return 0;`)``, ``(?C`c,verify: x`)`` and
`(?C"name")`; `(?Cx)` is error 182 and `(?C256)` error 138. pcrec today
answers `(?C...) requires module 'callouts'` for every `(?C` form and
"unrecognized character after (? or (?-" for `(?{`.

## Goals

Ranked; an earlier goal wins a conflict.

1. **Trust: a pattern source never becomes code without the invoker's say-so,
   and code from a file the invoker did not name runs only at a pinned
   version.** Who benefits: whoever compiles pattern files they did not write.
   Measurable form: with `--allow-code` absent, every entry point (CLI FILE,
   CLI `--pattern`, library `pcrec_compile`, the `.rxt` harness, every
   `--list-*` that compiles) refuses every embedded segment by name and emits
   zero bytes (one refusal test per entry point, each with a way to fail);
   with it present, a segment reached through an `include`/`lib` line with no
   `sha256=` pin, or a pin that does not match the file's bytes, is refused
   (one test per row of section 5's table).
2. **Same answer as PCRE2 for a pure callout.** Who benefits: a user moving a
   pattern between PCRE2 and pcrec. Measurable form: over the callouts corpus,
   pcrec's answer equals libpcre2 10.46's with `PCRE2_NO_AUTO_POSSESS |
   PCRE2_NO_START_OPTIMIZE` (section 1.7; Frank's question 1 in section 10) —
   zero disagreements — when the same predicate text drives both; and every
   optimization axis is answer-identical to default over that corpus
   (`make test-axes`).
3. **The cost is paid only by patterns that use it, and a `verify` segment
   that rarely vetoes keeps the DFA's speed.** Who benefits: every user
   (first half), the user with a hot validation pattern (second). Measurable
   form: (a) the identity gate over the existing corpus shows zero byte movers
   other than the abi number line; (b) on a veto-free subject, a
   `verify`-eligible artifact's search time is within the A/A floor of the
   same pattern's callout-free artifact plus one direct call per match
   (dev box, section 9 stage 4's measurement card).
4. **Calling the user's own C is one declaration away.** Who benefits: the
   casual C user (Frank, 2026-10-26). Measurable form: UC-3 builds with one
   `code-header` head line and the user's ordinary `gcc main.c gen.c own.c`
   line, and a compile error in a segment is reported at the pattern file's
   own line (DT-3.3).

**Priority order:** 1 over 2 over 3 over 4. A feature that turns data into
code must not trade the gate for convenience; a speedup that changes an
answer is a miscompile.

**Design constraint, ruled not ranked (Q2):** ONE call site. Numbered and
named bindings, inline code in either spelling, and a pcrec artifact used as a
callout all reach one call-site emitter, one fire contract, one return table
and one test population.

**Non-goals.** The template side (`${{ }}`, `${( )}`) — pattern side first
(Q1); it is a later phase (section 9, stage 6) that reuses the generated-
function and trust machinery built here. `post` mode (Q4: only on a measured
need). Parsing, type-checking or rewriting the user's code (the text is
opaque except for finding its end; Q7: no `$1`). A sandbox (D22). A
`pcre2_callout_block`-shaped ABI (V-A's compat layer). Native abort (Q6, D38).
Languages other than C (room only: section 2.2's tag). Running a C compiler
from pcrec (`--check-c`: not in this plan). README or survey work (Q8).

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT at two stages. Stage 2 (inline segments):
   the per-fire cost of a call site against the same predicate hand-written in
   the caller after a plain search — throughput, warm, hit-dense subjects, dev
   box (7700X), gcc 15.2, glibc; it confirms Frank's "the only cost is the
   drop into vm" and nothing else is decided by it. Stage 4 (`verify`):
   throughput on veto-free versus veto-heavy subjects. The REGIME FLIPS THE
   DECISION: a vetoed candidate pays the scan, one call and then the VM from
   the candidate's start, so a predicate that mostly vetoes is slower under
   `verify` than inline. That is why the mode is the user's declaration per
   segment (Q4) and not a selector row the compiler picks on its own.
2. **Independent control.** RELEVANT. (a) Answers: libpcre2 10.46 runs the
   SAME predicate source through `pcre2_set_callout`, behind an adapter the
   test author writes against PCRE2's documented block (section 9.2); it
   shares no code with pcrec's emitter or its segment macros. (b) Optimizer
   barriers and `verify`'s equivalence: `make test-axes`, whose deny flags
   (the new `-fno-callout-verify` included) compare each optimization against
   its own absence. (c) Pins: `sha256sum(1)` and the NIST SHA-256 vectors, not
   pcrec's implementation. (d) `#line`: gcc's own diagnostic text.
   Populations are counted, not assumed: each stage's corpus declares its case
   count and its reach witnesses ([MECH-REACH]).
3. **What moves on regeneration.** RELEVANT, narrowly. No table or
   calibration is added. A `sha256=` pin IS data that moves by design: when a
   pinned file changes, the pin stops matching and the target is refused
   until a person re-pins it (Q5). Emitted bytes move only for patterns that
   contain a callout site (section 8.1); the abi events are section 8's.

## 1. The call-site primitive ([M4-CALLOUTS] step 2)

### 1.1 One node

Every callout spelling parses to ONE AST node, `A_CALLOUT`, carrying:

| field | meaning |
|---|---|
| `bind` | first-match: `CO_CODE` (embedded code), `CO_NAME` (a named binding), `CO_NUM` (a numbered binding) |
| `name` / `num` | the binding's identifier (`CO_NAME`) or 0-255 (`CO_NUM`) |
| `lang`, `text`, `textlen` | `CO_CODE` only: the language tag and the DECODED code bytes (arena) |
| `width` | `W_PRED` (returns 0 or -1 only) or `W_ANY` (any native length); section 1.5 |
| `mode` | `M_INLINE` or `M_VERIFY` (section 4) |
| `seg` | the segment index: 1-based textual order among `CO_CODE` nodes of the pattern |
| `src` | provenance: source file id, line, column (section 3.4, section 5) |
| `reg`, `reg_at` | the registry row and offset, as every module-owned node carries (D67) |

The registry already holds the `(?C` row (`GROUP_XA_CALLOUT`, module
`callouts`, `VM_ONLY`, `RF_CROSSES_ATTEMPTS`); it gains a port function, and
`(?{` gets a sibling row (section 2). Both rows' ports produce `A_CALLOUT`,
the way the three named-group rows share `pcrec_ngport_declare`. The VM_ONLY
column keeps doing what it does for every module node: `forces_registry` in
the engine selector reaches the node and answers "VM", with the row's own
`syntax` as `engine_why` — no callout clause in the selector.

### 1.2 Emission: `VE_CALLOUT` gets its producer

`VE_CALLOUT` is reserved in the VM emitter with no producer. Its producer
emits, at the site, in this order:

1. Build a fresh `rx_ctx` on the stack: `subject`, `len` from the entry;
   `pos` = the current position; `ncap` = the site's compile-time constant
   (1.3); `caps` = the VM's working slot array viewed as `ptrdiff_t (*)[2]`
   (engine_m4.md §3.4: the capture region is first); `user` from the binding
   (1.4); `vars`, `nvars` = what the entry received (NULL/0 when it took
   none).
2. Write slot 0's start: `stv[0] = attempt start` (1.3).
3. Call the callee (1.4) and route its return through the call-site return
   table (1.6).

One emitter function, parameterised by a BINDING ROW (1.4); no other site
calls a callout.

### 1.3 What the code sees

The view is `match_api.md` §5's representation, with three site rules:

- **`ncap`** is `1 + the highest group number whose opening parenthesis
  precedes the site` (engine_m4.md §3.4, D38.6): a compile-time constant per
  site, so the view does not depend on which path reached it.
- **Groups that ENCLOSE the site read as their last CLOSED value or unset**,
  never a half-written pair. Today an unmarked group writes its start at the
  open and its end at the close, so a site inside `(a(?C1)b)` would see a
  fresh start beside a stale or unset end. The fix is not a callout clause:
  [M6.5.2]'s PUBLISH-AT-CLOSE already exists for exactly this fact (a
  backreference must not see a half-open group), keyed by a marked set that is
  "the union of every `A_BREF`'s `refs`". The marked set becomes the union of
  every reader's refs: each `A_BREF`'s, plus, for each `A_CALLOUT`, the groups
  enclosing it. A pattern with no callout marks exactly what it marks today
  (byte-identical). This gives PCRE2's view: a group is visible after it
  closes, and a repeated group keeps its previous iteration's value until it
  closes again (`match_api.md` §5.1¶2's retention rule).
- **Slot 0** at a site is `{attempt start, PCREC_UNSET}`: the start is known,
  the end is not. The attempt start is where the current anchored attempt
  began (PCRE2's `start_match`), NOT a `\K`-moved start. Writing it costs one
  store per fire, only in callout-bearing artifacts, and adds no `rx_ctx`
  field (no change to the frozen struct; requirement R-P3 asked for one of the
  two). On a completed match the entry overwrites slot 0 as today.

`F9`/`match_api.md` §5¶7 stands: the view is valid for the call only.

### 1.4 Binding rows: who the callee is

The emitter reads the callee from a declared first-match table:

| # | row | callee expression | `user` | width default |
|---|---|---|---|---|
| 1 | `code` (`CO_CODE`) | a direct call of the generated `static` function `<prefix>__code<seg>` (section 3) | `NULL` | `W_PRED` |
| 2 | `named` (`CO_NAME`) | `rx_callout_<name>.fn` — `extern const rx_callout_ref rx_callout_<name>;` declared by the artifact, defined by the user (D38 §1.1) | `rx_callout_<name>.user` | `W_ANY` |
| 3 | `numbered` (`CO_NUM`) | `rx_callout_<n>.fn`, same shape, `<n>` the decimal number | `rx_callout_<n>.user` | `W_ANY` |

Row 1 is a direct call so gcc can inline the user's code into the VM; rows 2
and 3 are the D38 binding unit verbatim. `rx_callout_<name>` is the
fixed-literal, unprefixed family D38/D41.1 ruled: two artifacts naming one
binding share it, which is the point (one definition serves both). The
compile-time namespace table in `src/core/compile.c` already reserves its row
2 (`callout-bindings`) "with its first producer"; this is that producer. Row
1's name is `<prefix>__<role>`-shaped, inside the namespace row 1 already
reserves (a user prefix may not contain `__`).

A named or numbered binding is any `rx_matchfn`: a hand-written function, a
PCRE2-convention function behind the macro of section 7, or a pcrec artifact's
`<prefix>_match` (section 6).

### 1.5 The native return convention (Q6) and what "length consumed" means

The callee returns what `rx_matchfn` returns (`match_api.md` §2, D38): a
length `>= 0` anchored at `ctx->pos`, `-1` for "fail this path", or a code
from `match_api.md` §4. Mid-pattern:

- **`0`** is a pass that consumes nothing: the engine continues at `pos`.
- **`k > 0`** consumes `[pos, pos+k)`: the engine continues at `pos+k`. The
  consumed bytes belong to every group that encloses the site, so the R-c
  "GROUP form" (D38 §3) needs no syntax: `((?C"octet"))` captures what the
  callee consumed.
- **The callee is ATOMIC** (D38 §2): on backtracking past the site the engine
  never asks it for a shorter length; it reaches earlier choice points. If the
  engine reaches the site again (a different path, or a later attempt), the
  callee is called again — the tentative-path firing of R-P4.
- **`-1`** fails the path: the engine backtracks exactly as on a failed atom.

**Width classes.** `W_PRED` declares the callee returns only `0` or `-1`; a
positive return is a contract break and traps (row 9 of 1.6). `W_ANY` admits
any length. Two reasons for the class, both general: it turns the most likely
user mistake into a loud stop at the first test run (writing `return 1;` to
mean "pass" would otherwise silently consume a byte: requirement W4), and it
is a FACT the optimizer needs (section 1.8: a `W_PRED` site is the empty
string in a prefilter's language, a `W_ANY` site is "any bytes"). Embedded
code is `W_PRED` unless its tag says `consume` (section 2.2); bindings are
`W_ANY` (they are the composition path). The class narrows the range of the
native convention; it is not a second convention. Frank's question 2 in
section 10 asks whether the default is right.

Named macros for the user's returns: `RX_PASS` (0), `RX_FAIL` (-1), and a
length is just the number.

### 1.6 The return table (extends `match_api.md` §4¶10)

`match_api.md` §4¶10 already rules that a composed call site handles a
callee's code through ONE first-match table, emitting rows only for codes the
callee can return. A callout site is the table's second producer (the
compound's controller is the first). A user callee "can return" anything, so
every row is emitted; the table gains rows 9 and 10:

| # | the callee's code | action |
|---|---|---|
| 1 | a length `>= 0` within the subject | success edge: continue at `pos + ret` |
| 2 | `-1` | failure edge: backtrack |
| 3 | a give-up, `[PCREC_ERR_FLOOR, -2]` | propagate unchanged (D49) |
| 4 | `PCREC_ERR_INTERNAL` | propagate unchanged |
| 5 | `PCREC_ERR_UTF` | propagate unchanged |
| 6 | `PCREC_ERR_STARTPOS` | `__builtin_trap()` |
| 7 | `PCREC_ERR_UNSET_VAR` | propagate unchanged |
| 8 | any other code below 0 | `__builtin_trap()` (D38 item 4) |
| 9 | NEW: `ret > 0` at a `W_PRED` site | `__builtin_trap()`: the predicate broke its declared width |
| 10 | NEW: `ret > len - pos`, or (under a multi-byte encoding) `pos + ret` not a character boundary | `__builtin_trap()`: the callee broke `rx_matchfn`'s contract; every position the engine continues from must be inside the subject and on a boundary (K50) |

Rows 9 and 10 are checked before row 1 (first match). Their cost is one
compare on the success path and is emitted only at callout sites. A trap,
rather than a fail, for the same reasons D38 gave: it is freestanding, free on
the warm path, and a contract break the engine cannot continue soundly from.

### 1.7 The fire contract, and which PCRE2 answer is the reference

Stated in the spec (requirement R-P4), unchanged in substance from D36 and
D163 addendum 6 Q2: a callout may fire on paths the engine later abandons,
zero or several times per final match, at engine-chosen positions; a callee
whose return depends only on what `rx_ctx` carries for that call (PURE) gets
a defined ANSWER; side effects see an unspecified sequence.

The answer needs a reference, because PCRE2's own answer moves with its
optimizations (requirements probe P7: `(\d+)(?C{p})` on `1234` gives `[1,4)`
by default and `[0,3)` under `PCRE2_NO_AUTO_POSSESS|PCRE2_NO_START_OPTIMIZE`).
**Proposed reference: the unoptimized backtracking order** — start positions
in order, at each start the paths in priority order, every veto applied —
which is libpcre2 with `PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE`, and
which is what pcrec's VM computes when no optimization prunes a path that can
reach a site. It is the answer a reader can predict from the pattern alone.
Under D26's addendum (compatible unless PCRE2 bug; say "compatible", never
"the same") the spec says pcrec is compatible with PCRE2 run without its
auto-possessification and start optimizations, and names P7 as the reason.
This is a semantics choice: section 10, question 1.

### 1.8 What a callout site means to the optimizer (one rule, every pass)

A callout reads `pos` and the captures so far, so any pass whose proof says
"backtracking here cannot change the outcome" is unsound across a site that
would see a different `(pos, caps)` (possessification of `\d+` before
`(?C...)` changes the D1 answer, requirements §4.4). The general statement,
not a list of special cases: **to every pass, an `A_CALLOUT` is a consumer
whose acceptance depends on `pos` and on every group in `1..ncap-1`, of width
`[0,0]` (`W_PRED`) or `[0,∞)` (`W_ANY`)** — the same class as an `A_BREF`
whose `refs` are all of those groups, plus position. Each pass already answers
for `A_BREF` (a capture-reading consumer); the build lane makes each pass's
fact table read the callout through that same predicate rather than adding a
callout clause per pass, and the control is `make test-axes` over a corpus
whose vetoes steer backtracking (D1, D2 and P8-P10 shapes): an optimization
that prunes a path a site could see differs from its own deny flag.

The prefilter (the hybrid's capture-erased scan) needs the same fact in
language form: a `W_PRED` site erases to the empty string and a `W_ANY` site
to "any bytes, any length". This corrects engine_m4.md's recommendation (c)
("apply the prefilter to callout patterns uniformly"), written when callouts
were zero-width predicates only; D38 later made a callout a CONSUMER, and
erasing a consuming site to the empty string would make the scan reject
matches (section 10a, conflict 3). Stage 1 declines the prefilter for callout
patterns outright (one `pf_admits` row); stage 4 admits it under the language
rule above.

### 1.9 Where a site may appear in v1

The registry's VM_ONLY row sends the pattern to the VM; the parser refuses by
name the positions v1 does not support (never a miscompile). First-match:

| # | position | v1 |
|---|---|---|
| 1 | inside a lookbehind | refused: "a callout inside a lookbehind is not supported" |
| 2 | inside a conditional's CONDITION (`(?(?C1)...)`, PCRE2's callout-before-assertion form) | refused |
| 3 | inside a group reachable by a subroutine call or recursion (`(?1)`, `(?R)`, `(?&n)`, `(?(DEFINE)`) | refused: a call multiplies fire points and the site's `ncap` constant stops being one number |
| 4 | inside a group a delivering call imports from a library (`rxt_format.md` §1.2) | refused for the same reason |
| 5 | anywhere else: the main sequence, alternations, capture and non-capture groups, quantified groups, atomic groups, lookaheads | supported |

Rows 1-4 are lifted one at a time, each on a need, by a stage with its own
tests.

## 2. Two spellings, one node

### 2.1 The spellings

| spelling | example | owner module | PCRE2 reads it as |
|---|---|---|---|
| `(?C)`, `(?Cn)`, n in 0..255 | `(?C7)` | `callouts` | a numbered callout |
| `(?C` + delimited string, NOT starting with a language tag | `(?C"octet")` | `callouts` | a string callout |
| `(?C` + delimited string starting with a language tag | ``(?C`c: return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;`)`` | `code-<lang>` | a string callout (valid PCRE2) |
| `(?{` [tag] code `})` | `(?{ return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL; })` | `code-<lang>` | error 111 (PCRE2 refuses it) |

`(?{` is a pcrec extension in a spelling PCRE2 refuses (D38 Q5's namespace
rule; measured above). Perl reads the same text as embedded Perl; pcrec reads
it as embedded C (or the tagged language).

### 2.2 The language tag

```
tag    := lang ( "," attr )* ":"
lang   := [a-z][a-z0-9_]*          one registered language; "c" in v1
attr   := "verify" | "consume"     (v1 set; unknown -> refused by name)
```

- In the **PCRE2 spelling** the tag is MANDATORY and begins at the first
  byte of the DECODED string: a string with no tag is a binding name (row
  2/3 of 1.4), and must be a C identifier — any other untagged string (PCRE2
  lets a program read arbitrary callout text) is refused: "a (?C"...")
  string is a binding name (a C identifier) or tagged code (`c: ...`)".
- In **`(?{`** the tag is OPTIONAL and begins immediately after `{` with no
  whitespace; `(?{ ... })` with no tag is C, by grammar (fixed forever, never
  configurable, so a file's meaning never depends on a setting). A text that
  begins with `ident:` where `ident` is not a registered language is refused
  with a hint ("unknown language tag 'x'; if this is a C label, put a space
  before it") — a C label as the very first token is the only collision.
- `verify` sets the segment's mode (section 4); `consume` sets `W_ANY`.
  Repeating an attribute is refused. Mode is per segment (Q4).

A later language registers a row in a declared language table (`lang`, the
module `code-<lang>`, its end scanner for `(?{`, its glue emitter); nothing
else changes.

### 2.3 End rules

**PCRE2 spelling: PCRE2's rule exactly, no lexer.** The string ends at the
first lone closing delimiter; a doubled delimiter is one literal delimiter
(requirements P2/P3/P5: `{` closes with `}`, and `}}` is one `}`). The tag is
then read from the DECODED string. This keeps the same bytes meaning the same
pattern to both programs (the requirements' "worst kind of miscompile"
argument) and needs no knowledge of the language. The relief valve for code
full of braces is a delimiter the code does not use (`` ` `` or `$`), or the
`(?{` spelling.

**`(?{` spelling: balanced braces, with the LANGUAGE's lexical skips.** The
tag (if any) selects the language's scanner; for C:

1. Phase-2 splices first: a backslash immediately followed by a newline is
   removed before anything else is recognised (so `// x \`+newline continues
   the comment, as in C).
2. Skipped as opaque: `"..."` and `'...'` literals with backslash escapes
   (an encoding prefix `L`, `u`, `U`, `u8` is ordinary identifier text before
   the quote), `/* ... */` comments, `// ...` to the end of the line.
3. A `'` inside a pp-number (a token that starts with a digit, or `.` then a
   digit) is a C23 digit separator, not a character literal.
4. Depth starts at 1 after `(?{`; `{` and the digraph `<%` add one; `}` and
   `%>` subtract one (C always reads the digraphs as braces). Braces on
   preprocessor lines count like any other. Trigraphs are NOT recognised (gcc's
   gnu modes ignore them; C23 removed them).
5. The segment ends at the brace that brings depth to 0, which MUST be
   followed immediately by `)`; otherwise refused: "(?{ ... }) must end with
   '})'". An unterminated literal or comment, or end of pattern at depth > 0,
   is refused naming the segment's START offset.

The pattern's own modes do not apply inside a segment: `(?x)` does not make
`#` a comment there (P6 is PCRE2's behaviour for the string form; `(?{` copies
it). Inside a character class `[(?{]` is three literal bytes, as today.

The per-row test table (requirement R-S4) is section 9's stage 2 scanner
table: one row per rule above plus `"}"`, `'}'`, `/* } */`, `// }` then
newline, `<% %>`, `1'000`, `u8"}"`, a `}` at depth 2 followed by `})`, and the
refusals.

### 2.4 Errors (D26 tiers)

The construct's REALITY and OWNER are exact; wording is not:

| situation | diagnostic (shape, not wording) |
|---|---|
| `(?C` numbered/named, module `callouts` off | today's "(?C...) requires module 'callouts'" (unchanged) |
| embedded code, `--allow-code` does not name its language | "(?{...}) requires module 'code-c', which only the command-line option --allow-code=c enables" |
| `features code-c` in a file, or `--allow-code` on a config's `pcrec` line | refused at parse: a file cannot grant code (section 5) |
| unknown tag / attribute, untagged non-identifier string | refused by name, offset of the segment |
| end-rule failures | 2.3 item 5 |
| position not supported | 1.9's table |

Module `code-c` implies the call-site machinery of `callouts`; a pattern with
embedded code alone needs no `features callouts`.
