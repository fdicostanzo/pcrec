# Inline code in patterns — design ([INLINE-C], pattern side)

**Status: PROPOSED, rev 1 (lane inlinecrev1, 2026-10-26); rev 0 by lane
inlinecdes, paneled r1 (`docs/dev/reviews/2026-10-26-r1-inline-c-design.md`,
whose MANAGER RULINGS section binds this revision).** Design only: no build
go, nothing under `src/`, `tests/` or `docs/spec/` touched. Inputs:
`docs/design/inline_c_requirements.md` (its section 8 "Frank's answers" Q1-Q8
are BINDING), Frank's six further rulings of 2026-10-26 on the plan row
[INLINE-C] (cited here as FR1-FR6), `docs/design/design_callout_abi.md` (D38),
plan rows [INLINE-C] and [M4-CALLOUTS] (D36), `docs/spec/match_api.md`,
`docs/spec/rxt_format.md`, `docs/design/locate_finish.md` (D156),
`docs/design/compound.md` and `compound_callout_alignment.md` (D163), the
parser registry, the engine selector and the VM emitter as they stand at
`86a0fed00`. Spelling choices below are the manager's to change (memory "dd13b
syntax is manager's"); section 10 holds what is Frank's. Ids in this note
(`S-IC*`) are PLACEHOLDERS.

## REVISION 1 (read this first)

Rev 1 applies every finding the r1 round accepted and every ruling made on
it. Changed or new text carries `[r1 <id>]`, where `<id>` is the round's
finding id (A1-A9, T1-T7, D1-D21, and the doc-tier ids PREM-16a/c/f,
CON-15/18/19, SLOT-18a-e, SIM-6) or one of Frank's rulings FR1-FR6:

| id | Frank, 2026-10-26 (plan row [INLINE-C] notes) |
|---|---|
| FR1 | do NOT match PCRE2's callout behaviour under its optimizations: it is undocumented; fire count and order are unspecified; no PCRE2 flag set defines pcrec's answer |
| FR2 | every callout is a yes/no CHECK by default; `consume` opts in |
| FR3 | the context is read-only (`const rx_ctx *`); the return value is the only effect |
| FR4 | code cannot read or spend the budget; each fire counts as a step against the match budget |
| FR5 | named and numbered callouts also default to a check: `(?C"name,consume")`; a numbered callout declares it in the `.rxt` |
| FR6 | `--list-callouts` reports each site's FIRING CLASS, derived from structure; an optional `once` attribute is a compiler-checked promise |

What changed, by area (details at each mark):

- **Answer (section 1).** §1.7 rewritten to FR1: no reference flags; pcrec's
  answer is the pattern's backtracking-order answer; the PCRE2 comparison runs
  only on cases PCRE2's optimizations do not move (A1, D10 superseded). The
  site view: `ncap` is every group (A2); slot 0 is saved and restored around
  the call (A4); a site's groups join the one marked set, which is also
  `--no-captures`' keep set (A5). §1.8 is now a per-kind ATTRIBUTE ROW with a
  `text_width` and a `path` column, A_LOOK/A_VAR as analogs (D3), and every
  site erasure is recorded as inexact (A3). New §1.10 (firing classes and
  `once`, FR6) and §1.11 (budget, D9 + FR4). §1.6 names `callsite_rows[]` as the
  one return table (D5), fixes the row order (A9), and rules a callee's FRAMES
  (D8). One emitter, parameterised by binding row and view source (D2).
  Pre-registered obligations taken over (D4).
- **Spelling (section 2).** One attribute grammar for every callout (FR2, FR5):
  `consume`, `once`, `verify`; the numbered form declares in the `.rxt`.
  Ownership is rows, generated from the language table (D7). Malformed `(?C`
  gets its own refusal row (D17). Bidi controls in code are refused (T4).
- **Generated function (section 3).** `code-header` includes move after the
  matcher (A8); `#line` per decoded line (D18); accessors evaluate once and
  name groups correctly (A7, CON-15); `RX_PASS`/`RX_FAIL` live once (D16).
  `ext harness link` is withdrawn for a test-owned harness manifest (T3).
- **`verify` (section 4), rewritten.** Rev 0's `scan-end` is now `check-tail`, a FINISH row on `CR_VM`
  (D1 ruling); its scan is R with the tail REMOVED (A3, A6); its applicability
  reads site facts (A5); stage 4 waits for a census (D12); UC-1b' is its case.
- **Trust (section 5).** `code-*` modules are invoker-only, outside every
  feature vocabulary (T1); the harness keeps provenance (T2); an entry-point
  table (T5); test-axes reach with a counted floor (T6); pins reuse
  `sha256 <hex64>` and ONE SHA-256 home (D11); same file, two chains (T7).
- **Plan (sections 8-9).** Stage 1 split into 1a (the attribute row, zero
  movers) and 1b (the callout) (D3); stage 3 is scheduled and lifts §1.9 rows
  3/4 for pinned reached code (D11); stage 4 is designed, briefed after a
  census (D12); a remodel-overlap table and the flag-bit count (D14); spec
  hunks found by grep (D15); the INTERNAL comment as its own abi event (D6).
- **Questions (section 10).** Rev 0's two questions are ANSWERED (FR1, FR2).
  Two new semantics questions remain, in plain words.

Objections to a ruling: none. One reading the rulings leave open is flagged
where it is made (§1.7, the PCRE2 comparison as a filtered cross-check).

## Goals

Ranked; an earlier goal wins a conflict.

1. **Trust: a pattern source never becomes code without the invoker's say-so,
   and code from a file the invoker did not name runs only at a pinned
   version.** Who benefits: whoever compiles pattern files they did not write.
   Measurable form `[r1 T1, T5]`: every row of the entry-point table (§5.9),
   which is DERIVED from the CLI's own mode list plus the library and harness
   entries, has a test with a way to fail: a mode that writes C refuses every
   segment by name without `--allow-code` and emits zero bytes; a mode that
   only describes parses and writes no C; `--list-callouts` works without the
   opt-in and prints code escaped. Every door of the feature vocabulary
   (`features all` in a block, a config, a `pcrec` line, `--features all`, the
   library's `features = "all"`) is refused for code (one test each). With the
   opt-in present, code reached through an `include`/`lib` line is refused
   until stage 3, and from stage 3 is refused when any line on any chain to it
   carries no pin or a pin that does not match the parsed bytes (one test per
   row of §5.4).
2. **A defined answer for a pure callout, compatible with PCRE2 where PCRE2
   has one.** `[r1 FR1, A1, A2, D10, D13]` Who benefits: a user who must
   predict what a pattern with a check does, and a user moving a pattern
   between PCRE2 and pcrec. Measurable form: (a) over the callouts corpus,
   pcrec's answer equals the pattern's backtracking-order answer (§1.7)
   computed by a test-owned independent backtracker, zero disagreements, over
   a population of at least 1,000 generated callout patterns (the r1 round's
   generator shape ran 4,455) plus the named shapes (P7-P10, the `(?s).*`
   start veto, the looped-site view, `\K` before a site, `--no-captures`); the
   runner counts the population and is red below the floor. (b) On the
   subset whose libpcre2 10.46 answer does not move under its optimization
   options (§1.7), pcrec equals libpcre2's default-flag answer, zero
   disagreements; a case outside the subset is reported, never failed.
   (c) Every optimization axis is answer-identical to default over that
   corpus (`make test-axes`), with a counted floor of BUILT and LINKED
   callouts cases per axis (T6).
3. **The cost is paid only by patterns that use it, and a `verify` check that
   rarely vetoes keeps the DFA's speed.** Who benefits: every user (a), the
   user with a check in a hot pattern (b, c). Measurable form: (a) the identity
   gate over the existing corpus shows zero byte movers other than the abi
   number line at each stage (and none at all at stage 1a), and a sabotage row
   that marks every group publish-at-close unconditionally turns it red
   `[r1 D13, COST-9]`; (b) `[r1 D13]` INLINE mode: a pattern whose check is the
   empty predicate (`return RX_PASS;`) runs within the A/A spread of the same
   pattern's callout-free `--engine=vm` twin plus `n` direct calls, `n` the
   counted fires (the counting binding of DT-4.1), on paths that do not reach
   the site as well as on paths that do (gcc inlines the user's code into the
   VM; this catches a VM pessimised by it); (c) VERIFY mode (stage 4):
   on a veto-free subject, the empty-predicate `verify` artifact's search time
   is within the A/A spread of the callout-free pattern's DFA twin plus 5%,
   and is reported beside the inline (`-fno-callout-verify`) twin. The 5% is an
   UNMEASURED default, replaced by the card's first A/A run; the A/A source is
   the card's own repeat spread. A miss is a finding against stage 4: its
   FINISH row stays denied by default until the cause is named.
4. **Calling the user's own C is one declaration away.** Who benefits: the
   casual C user (Frank, 2026-10-26). Measurable form: UC-3 builds with one
   `code-header` head line and the user's ordinary `gcc main.c gen.c own.c`
   line, and a compile error in a segment is reported at the pattern file's
   own LINE (DT-3.3), and at its column where the text before the code on that
   line is plain ASCII with no escape `[r1 D18]`.

**Priority order:** 1 over 2 over 3 over 4. A feature that turns data into
code must not trade the gate for convenience; a speedup that changes an
answer is a miscompile.

**Design constraint, ruled not ranked (Q2):** ONE call site. Numbered and
named bindings, inline code in either spelling, a pcrec artifact used as a
callout, and `verify`'s check at a candidate end `[r1 D2]` all reach one
call-site emitter, one fire contract, one return table and one test
population.

**Non-goals.** The template side (`${{ }}`, `${( )}`) — pattern side first
(Q1); it is a later phase (section 9, stage 6) that reuses the generated-
function and trust machinery built here. `post` mode (Q4: only on a measured
need). Parsing, type-checking or rewriting the user's code (the text is
opaque except for finding its end; Q7: no `$1`). A sandbox (D22). A
`pcre2_callout_block`-shaped ABI (V-A's compat layer). Native abort (Q6, D38).
Languages other than C (room only: section 2.2's tag). Running a C compiler
from pcrec (`--check-c`: not in this plan). README or survey work (Q8).
Tracking PCRE2's optimization-dependent callout answers (FR1). Metering the
user's own C (FR4: the budget counts fires, not the work inside them).

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT at two stages `[r1 D13, COST-5, COST-6]`.
   Stage 1b/2 (inline mode): throughput, warm, hit-dense subjects, dev box
   (7700X), gcc 15.2, glibc; the control is the same pattern's callout-free
   `--engine=vm` twin with the fires COUNTED, so the card isolates the
   per-fire cost from the engine change; the one decision it can move is
   whether code segments stay direct, inlinable calls (§1.4 row 1) or become
   out-of-line calls (if inlining the user's code measurably slows the VM's
   non-site paths). Stage 4 (`verify`): veto-free AND veto-heavy subjects,
   against three twins (the DFA artifact of the callout-free pattern, the
   inline artifact under the deny flag, and the `verify` artifact), all with
   the empty predicate so the user's code does not swamp the overhead. The
   REGIME FLIPS THE DECISION: a vetoed candidate pays the scan, one call and
   then the VM from the candidate's start, so a check that mostly vetoes is
   slower under `verify` than inline. That is why the mode is the user's
   declaration per site (Q4) and not a selector row the compiler picks; the
   card reports the veto rate at which the two cross, for the guide.
2. **Independent control.** RELEVANT. (a) Answers `[r1 FR1]`: a test-owned
   independent backtracker written from §1.7's stated semantics (the r1
   round's `naive.py` is the precedent: 4,455 patterns, 0 differences against
   libpcre2 with its optimizations off), sharing no code with pcrec; and
   libpcre2 10.46 at DEFAULT flags on the optimization-insensitive subset,
   behind an adapter the test author writes from PCRE2's documented block
   (§9.2). (b) Optimizer barriers and `verify`'s equivalence: `make
   test-axes`, whose deny flags (the new `-fno-callout-verify` included)
   compare each optimization against its own absence, with a counted floor of
   built callouts cases per axis `[r1 T6]`. (c) Pins: `sha256sum(1)` and the
   NIST SHA-256 vectors, not pcrec's implementation. (d) `#line`: gcc's own
   diagnostic text. (e) Firing classes `[r1 FR6]`: a counting binding per site
   over the corpus, asserting fires-per-attempt never exceeds the class bound
   (§1.10). Populations are counted, not assumed: each stage's corpus declares
   its case count and its reach witnesses ([MECH-REACH]).
3. **What moves on regeneration.** RELEVANT, narrowly. No table or
   calibration is added. A pin IS data that moves by design: when a pinned
   file changes, the pin stops matching and the code is refused until a person
   re-pins it (Q5). Emitted bytes move only for patterns that contain a
   callout site (section 8.1), except the one every-artifact comment fix that
   is its own abi event `[r1 D6]`; the abi events are section 8's.

## 1. The call-site primitive ([M4-CALLOUTS] step 2)

### 1.1 One node

Every callout spelling parses to ONE AST node, `A_CALLOUT`, carrying:

| field | meaning |
|---|---|
| `bind` | first-match: `CO_CODE` (embedded code), `CO_NAME` (a named binding), `CO_NUM` (a numbered binding) |
| `name` / `num` | the binding's identifier (`CO_NAME`) or 0-255 (`CO_NUM`) |
| `lang`, `text`, `textlen` | `CO_CODE` only: the language tag and the DECODED code bytes (arena) |
| `width` | `W_PRED` (returns 0 or -1 only; the DEFAULT for every callout `[r1 FR2, FR5]`) or `W_ANY` (any native length; the `consume` attribute); section 1.5 |
| `mode` | `M_INLINE` or `M_VERIFY` (section 4) |
| `once` | `[r1 FR6]` the site carries the `once` promise (section 1.10) |
| `refs` | `[r1 A5]` the groups the site reads: every group of the pattern (section 1.3); unioned into the one marked set |
| `seg` | the segment index: 1-based textual order among `CO_CODE` nodes of the pattern |
| `src` | provenance: source file id, line, column, and the include/lib chain that reached it (section 3.4, section 5) |
| `reg`, `reg_at` | the registry row and offset, as every module-owned node carries (D67) |

`[r1 D7]` Ownership is ROWS, not port logic. Registry ports carry no module
fact (the rule in `src/core/internal.h` beside the port type: "Ports are DATA
about production; they carry no diagnostic and no module fact"), and D26 makes
a construct's owner exact. So:

- the numbered/named `(?C` row stays as it is (module `callouts`);
- a SECOND `(?C` row per registered language, owned by `code-<lang>`, whose
  per-row `recognise` hook (the existing MOD-0.2 arbitration hook) accepts
  only a decoded string that begins with that language's tag (2.2);
- one `(?{` row per registered language, owned by `code-<lang>`.

The language rows are GENERATED from section 2.2's language table, so the
language table is the single source and the registry rows are its
projection; `--list-syntax` and the compliance index read the owner from the
row as for every other construct. All these rows' ports produce `A_CALLOUT`,
the way the three named-group rows share `pcrec_ngport_declare`. The VM_ONLY
column keeps doing what it does for every module node: `forces_registry` in
the engine selector reaches the node and answers "VM", with the row's own
`syntax` as `engine_why` — no callout clause in the selector.

### 1.2 Emission: `VE_CALLOUT` gets its producer

`VE_CALLOUT` is reserved in the VM emitter with no producer. `[r1 D2]` Its
producer is ONE emitter function with two parameters, the BINDING ROW (1.4)
and the VIEW SOURCE, and with the success, failure and propagate edges
supplied by its caller:

| view source | who calls | `pos`, `caps` |
|---|---|---|
| `vm-slots` | the VM program at a site | the VM's current position; the VM's working slot array viewed as `ptrdiff_t (*)[2]` (engine_m4.md §3.4: the capture region is first) |
| `finish-hand` | `verify`'s FINISH row (section 4) at a candidate end | the hand's end `e`; a two-word local holding `{s, PCREC_UNSET}` (no other group exists there: 4.3) |

It emits, in this order:

1. Charge one step to the match budget (section 1.11) `[r1 D9, FR4]`.
2. Build a fresh `rx_ctx` on the stack: `subject`, `len` from the entry;
   `pos` and `caps` from the view source; `ncap` = the artifact's group count
   plus one (1.3) `[r1 A2]`; `user` from the binding (1.4); `vars`, `nvars` =
   what the entry received (NULL/0 when it took none).
3. `[r1 A4]` For `vm-slots`: save slot 0's start (it is `\K`'s live
   register), store the attempt start in it, call, restore it. For
   `finish-hand` the local already holds the start.
4. Call the callee (1.4) and route its return through the return table
   (1.6), whose edges are the caller's: the VM continues or backtracks; the
   FINISH row continues to the next tail check or takes its veto edge.

No other site calls a callout. The stage-1b sabotage rows are written against
this function, and at stage 4 each witness must reach both callers
([MECH-REACH]).

### 1.3 What the code sees

`[r1 FR3]` The context is READ-ONLY: the callee receives `const rx_ctx *`, and
its return value is its only effect on the match. The view is `match_api.md`
§5's representation, with three site rules:

- **`ncap` is the artifact's group count plus one, at every site** `[r1 A2]`.
  Rev 0's lexical constant (engine_m4.md §3.4: "1 + the highest group whose
  opening parenthesis precedes the site") hid groups PCRE2 shows: in
  `(?:(?C1)(a))+` on `aa` the second fire sees group 1 from the first
  iteration (`capture_top=2, g1=[0,1)`, libpcre2 10.46), and the lexical rule
  gave that site `ncap = 1`. engine_m4.md §3.4 is a design text, not a ruling;
  D38 item 6 rules a WATERMARK, and the widest constant is a sound one: a group
  not yet written reads `{-1,-1}` either way, which is what PCRE2's
  `capture_top` hides. The view still does not depend on the path. "The
  artifact's group count" is the PATTERN's group count, whatever
  `--no-captures` says (next bullet).
- **Every group a site can read is published at close** `[r1 A2, A5]`. A
  group reads as its last CLOSED value or unset, never a half-written pair.
  [M6.5.2]'s PUBLISH-AT-CLOSE already exists for exactly this fact, keyed by
  the ONE marked set that `pcrec_bref_mark` computes as the union of its
  readers' refs (`A_BREF`, `A_VAR`, `A_CALL` today). `A_CALLOUT` becomes a
  fourth reader: its `refs` (every group) are recorded on the node and unioned
  there. That set has TWO consumers, and both now follow: publish-at-close, and
  `--no-captures`' KEEP set (`br_strip_caps` keeps exactly the marked groups),
  so under `--no-captures` a callout pattern keeps every group the sites read
  and the artifact still delivers none (`<PREFIX>_NCAPS 1`). A pattern with no
  callout marks exactly what it marks today (byte-identical). Cost: in a
  callout artifact every group is published at close (two extra stores per
  close of a group that today writes in place). This gives PCRE2's view: a
  group is visible after it closes, and a repeated group keeps its previous
  iteration's value until it closes again (`match_api.md` §5.1¶2's retention
  rule).
- **Slot 0** at a site is `{attempt start, PCREC_UNSET}` `[r1 A4]`. The
  attempt start is where the current anchored attempt began, NOT a `\K`-moved
  start. Slot 0's start is `\K`'s live, trailed register in the VM
  (`RX_SET(RX_SLOT_WHOLE_START, ...)` at a `\K`; the report READS slot 0 as
  the `\K` start), so the site saves it, stores the attempt start, calls, and
  restores it (1.2 step 3): three moves per fire, only in callout artifacts,
  and no `rx_ctx` field (no change to the frozen struct; requirement R-P3
  asked for one of the two). Without the restore, `a\Kb(?C1)c` on `abc` would
  report `[0,3)` instead of `[1,3)`. `[r1 SIM-6]` Measured on libpcre2 10.46:
  PCRE2's `start_match` is NOT moved by `\K`, although pcre2callout(3) says
  it is; pcrec's rule is the attempt start either way, and the stage-1b corpus
  carries a `\K`-before-site case so a PCRE2 change on either side is seen (a
  D26-addendum case: the binary and its manual disagree; pcrec states its
  own rule).

`F9`/`match_api.md` §5¶7 stands: the view is valid for the call only.

### 1.4 Binding rows: who the callee is

The emitter reads the callee from a declared first-match table:

| # | row | callee expression | `user` | width default |
|---|---|---|---|---|
| 1 | `code` (`CO_CODE`) | a direct call of the generated `static` function `<prefix>__code<seg>` (section 3) | `NULL` | `W_PRED` |
| 2 | `named` (`CO_NAME`) | `rx_callout_<name>.fn` — `extern const rx_callout_ref rx_callout_<name>;` declared by the artifact, defined by the user (D38 §1.1) | `rx_callout_<name>.user` | `W_PRED` `[r1 FR5]` |
| 3 | `numbered` (`CO_NUM`) | `rx_callout_<n>.fn`, same shape, `<n>` the decimal number | `rx_callout_<n>.user` | `W_PRED` `[r1 FR5]` |

Every row's width is `W_PRED` unless the site says `consume` (2.2); rev 0's
"bindings are `W_ANY`" is replaced by FR5. Row 1 is a direct call so gcc can
inline the user's code into the VM; rows 2 and 3 are the D38 binding unit
verbatim. `rx_callout_<name>` is the fixed-literal, unprefixed family D38/D41.1
ruled: two artifacts naming one binding share it, which is the point (one
definition serves both). The compile-time namespace table in
`src/core/compile.c` already reserves its row 2 (`callout-bindings`) "with its
first producer"; this is that producer. `[r1 D16]` The table gains a row
refusing a binding NAME that contains `__` (as the prefix rule does, D41.1),
so `(?C"pcre2__octet")` cannot collide with the wrapper's helper
`rx_callout_pcre2__octet` (section 7). Row 1's name is `<prefix>__<role>`-
shaped, inside the namespace row 1 already reserves (a user prefix may not
contain `__`).

A named or numbered binding is any `rx_matchfn`: a hand-written function, a
PCRE2-convention function behind the macro of section 7, or a pcrec artifact's
`<prefix>_match` (section 6, declared `consume`).

`[r1 D19]` **An unbound binding is a link error, by design (D38):** an
artifact with a binding site requires the user to define `rx_callout_<name>`
(or `rx_callout_<n>`). PCRE2 runs a pattern whose callouts have no function by
ignoring them; pcrec does not, and the spec says so in one sentence.
`--emit-main` refuses a pattern with a binding site, by name ("--emit-main
cannot define the binding rx_callout_octet; link your own"), since its driver
could not link. The stamp `<PREFIX>_CALLOUT_BINDINGS` lists the binding
symbols the artifact needs `[r1 SLOT-18b]` (the compile-time mirror; an
`rx_info` member is [IFACE-PUSH]'s).

### 1.5 The native return convention (Q6) and what "length consumed" means

The callee returns what `rx_matchfn` returns (`match_api.md` §2, D38): a
length `>= 0` anchored at `ctx->pos`, `-1` for "fail this path", or a code
from `match_api.md` §4. Mid-pattern:

- **`0`** is a pass that consumes nothing: the engine continues at `pos`.
- **`k > 0`** (a `consume` site only) consumes `[pos, pos+k)`: the engine
  continues at `pos+k`. The consumed bytes belong to every group that encloses
  the site, so the R-c "GROUP form" (D38 §3) needs no syntax:
  `((?C"octet,consume"))` captures what the callee consumed.
- **The callee is ATOMIC** (D38 §2): on backtracking past the site the engine
  never asks it for a shorter length; it reaches earlier choice points. If the
  engine reaches the site again (a different path, or a later attempt), the
  callee is called again — the tentative-path firing of R-P4.
- **`-1`** fails the path: the engine backtracks exactly as on a failed atom.

**Width classes.** `W_PRED` declares the callee returns only `0` or `-1`; a
positive return is a contract break and traps (row 9 of 1.6). `W_ANY` admits
any length. `[r1 FR2, FR5]` Every callout is `W_PRED` unless it says `consume`
(Frank answered rev 0's question 2 "yes", and extended it to bindings). Two
reasons for the class, both general: it turns the most likely user mistake
into a loud stop at the first test run (writing `return 1;` to mean "pass"
would otherwise silently consume a byte: requirement W4), and it is a FACT the
optimizer needs (1.8). The class narrows the range of the native convention;
it is not a second convention.

`[r1 D16]` The return names `RX_PASS` (0) and `RX_FAIL` (-1) are defined ONCE,
in the callout-artifact fixed-literal family (section 8.1), so a hand-written
binding can use them too; a length is just the number.

### 1.6 The return table (extends `match_api.md` §4¶10)

`[r1 D5]` The table already exists: `callsite_rows[]` in
`src/gen/emit_compound.c` (compound.md §A.14, "shared by parts and (when they
build) callouts"), a table-kit root with a reach witness per row. A callout
site is its second producer; the table does not get a copy in the VM emitter.
Stage 1b LIFTS it to the shared emit layer (a file both emitters include; the
name is the build lane's) and reconciles the two callee conventions with ONE
column, `conv`, on the callee facts:

| `conv` | success | no match | below that |
|---|---|---|---|
| `part` (a compound part, today) | `r > 0` span | `r == 0` | codes |
| `matchfn` (every `rx_matchfn`: a callout, an artifact's `_match`) | `r >= 0` length | `r == -1` | codes below `-1` |

The compound's `reserved: r < 0` trap row stays the `part` convention's; under
`matchfn`, `-1` is the failure row and never reaches the trap. The lift is a
zero-mover change for the compound's artifacts, checked by the identity gate
over the compound's corpus before the callout rows are added. The callee facts
also gain the width class (row 9).

The rows for a `matchfn` callee, first match, in this order `[r1 A9]`:

| # | the callee's code | action |
|---|---|---|
| 2 | `-1` | failure edge (the caller's: backtrack, or the FINISH row's veto edge) |
| 3 | a give-up, `[PCREC_ERR_FLOOR, -2]` | propagate unchanged (D49); a callee's give-up does not escalate the outer tier (below) |
| 4 | `PCREC_ERR_INTERNAL` | propagate unchanged (D163 add. 6 Q3) |
| 5 | `PCREC_ERR_UTF` | propagate unchanged |
| 6 | `PCREC_ERR_STARTPOS` | `__builtin_trap()` |
| 7 | `PCREC_ERR_UNSET_VAR` | propagate unchanged |
| 8 | any other code below 0 | `__builtin_trap()` (D38 item 4) |
| 9 | `ret > 0` at a `W_PRED` site | `__builtin_trap()`: the check broke its declared width |
| 10 | `(size_t)ret > len - pos`, or (under a multi-byte encoding) `pos + ret` not a character boundary | `__builtin_trap()`: the callee broke `rx_matchfn`'s contract; every position the engine continues from must be inside the subject and on a boundary (K50) |
| 1 | `ret >= 0` | success edge: continue at `pos + ret` |

Rows 2-8 test negative values; rows 9, 10 and 1 apply to `ret >= 0` only, so
row 10's unsigned compare never sees `-1` (rev 0 said "checked before row 1",
which spelled literally with `ptrdiff_t` against `size_t` traps on every
`-1`). Row 1 no longer restates row 10's bound. The numbering keeps rev 0's
ids for cross-reference; the order above is the emitted order.

Cost `[r1 PREM-16a]`: a few compares on the success path, folded by gcc for an
inlined `W_PRED` code segment (rows 3-8 and 10 are then dead); at an extern
binding every row is live, and row 10 under UTF-8 adds a guarded load and
mask. A trap, rather than a fail, for the same reasons D38 gave: it is
freestanding, free on the warm path, and a contract break the engine cannot
continue soundly from.

`[r1 D8]` **A callee's give-up and the outer tier.** The callout site is the
first producer of this table whose callee CAN give up (a pcrec VM artifact
bound per section 6 above all). A callee's `PCREC_ERR_FRAMES` propagated out
of the outer VM's fast tier would trip the outer's §10.9 escalation and replay
the whole outer match, although the callee's own un-suffixed entry already
escalated and the replay cannot help. Ruled here: **a give-up that came from
a callee does not escalate the outer tier**; the site sets a local "callee gave
up" bit that the tier's escalation test reads, and the code propagates
unchanged. The spec wording moves with it: `match_api.md` §10.9¶6 and §4¶3's
last sentence ("from an un-suffixed entry it always means the stamped default
ran out") become "this call's stamped default, or a callee's". Stage 1b's test
binds a FRAMES-returning callee into a tiered outer artifact.

`[r1 D6]` The shared ABI block's `rx_matchfn` comment on every artifact says a
generated call site "traps on" `PCREC_ERR_INTERNAL`; row 4 and D163 add. 6 Q3
say it propagates. The comment is stale against a ruling. Correcting it moves
every artifact's bytes, so it is ITS OWN abi event, landed before stage 1b
(section 8.1), keeping stage 1b's mover expectation at the abi line only.

### 1.7 The fire contract and the answer `[r1 FR1, A1, D10]`

Stated in the spec (requirement R-P4), unchanged in substance from D36 and
D163 addendum 6 Q2: a callout may fire on paths the engine later abandons,
zero or several times per final match, at engine-chosen positions and in an
engine-chosen order; **fire count and order are unspecified** (FR1); a callee
whose return depends only on what `rx_ctx` carries for that call (PURE) gets a
defined ANSWER; side effects see an unspecified sequence. The firing CLASS of
section 1.10 is the one structural bound pcrec promises on top of that.

**pcrec's answer for a pure callout is the pattern's backtracking-order
answer:** start positions in order, at each start the paths in priority
order, every fire on every tried path honoured. It is the answer a reader can
predict from the pattern alone, and it is what pcrec's VM computes once the
optimizer treats a site as section 1.8 says (no pass may prune a path a site
could see).

**PCRE2 is not the reference here (FR1).** PCRE2's answer for a vetoing
callout moves with its optimizations: requirements probe P7, `(\d+)(?C{p})` on
`1234`, gives `[1,4)` by default and `[0,3)` with auto-possessification and
start optimization off; and with those two off, PCRE2 still auto-anchors a
leading `(?s).*`, so `(?s).*(?C)x` with a check that vetoes start 0 gives no
match on `axbx` until `PCRE2_NO_DOTSTAR_ANCHOR` is also set (then `[1,4)`, the
backtracking-order answer). Frank ruled (2026-10-26) that this behaviour is
PCRE2's UNDOCUMENTED optimization detail: pcrec does not chase it, and no
PCRE2 flag set defines pcrec's answer. The D26 addendum ("a PCRE2 choice the
standard leaves open is not a bug and pcrec follows PCRE2") does not decide
this case: PCRE2 has no single documented answer to follow (rev 0 cited the
addendum the wrong way; the round's D10).

**Compatibility, stated as the addendum requires ("compatible", never "the
same"):** the spec says pcrec is compatible with PCRE2 on a callout pattern
whose PCRE2 answer does not depend on PCRE2's optimizations, and names P7 and
the `(?s).*` case as patterns where it does. The test corpus finds that
subset mechanically (§9.2): a case is in it when libpcre2's answer is the same
at default flags and with EVERY answer-moving optimization off. The
optimization set is established by a survey of every `PCRE2_NO_*` compile
option against the corpus, not by two probes (the r1 round found a third,
`NO_DOTSTAR_ANCHOR`). *Reading flagged for the manager:* the flags are used
only as a FILTER that marks a case "PCRE2-sensitive" (reported, never failed);
they define nothing about pcrec's answer, which the independent backtracker
checks. If the manager reads FR1 as dropping the libpcre2 comparison
altogether, goal 2 (b) and the §9.2 libpcre2 leg are deleted and nothing else
changes.

### 1.8 What a callout site means to every pass: one attribute row `[r1 D3, A3]`

A callout reads `pos` and the captures so far, so any pass whose proof says
"backtracking here cannot change the outcome" is unsound across a site that
would see a different `(pos, caps)` (possessification of `\d+` before
`(?C...)` changes the P7 answer). Rev 0 said each pass "already answers for
`A_BREF` through one predicate" and that a callout could ride it. That
premise was false (the round's D3): there is no shared capture-reading-consumer
predicate; about 65 `case A_BREF` arms in 24 files each decide locally (the
verifier's count), several in exhaustive no-default switches whose `-Wswitch`
alarm is the house's enumeration of sites; and `A_BREF` is the wrong analog
(possessify's `bref_first` dereferences the referenced groups' TEXT, which a
callout has none of).

The general form is decision family 8's per-`AKind` attribute row
([DEC-KINDATTR], decision_families_survey.md §3.8) together with family 14's
per-kind rows table ([POSS-CTX-TABLE], §3.14). A_CALLOUT is the recorded
TRIGGER of both ("the next module that adds an AST kind"; "the next per-kind
possessify edit after [ART-POSS-ARMS]"). Per the manager's D3 ruling, the
trigger is met by building the general row, not by an exemption:

**Stage 1a builds ONE per-kind attribute row table** over today's kinds, with
these columns (a pass reads the column its question needs; a context-dependent
answer, such as possessify's follow threading or arm B's `bref_first`, keeps
its code and reads the row for the kind-level fact):

| column | readers (pass families) | values |
|---|---|---|
| `text_width` | TEXT/LANGUAGE readers: the prefilter's erased language (`nfa.c`), a capture's text first-set (possessify arm B), the required byte/run (`req.c`), min/max width (`widths.c`, `mrl.c`), start set (`startset.c`), end window (`endwin.c`), start anchoring (`startanch.c`) | `zero` (adds no text: `A_LOOK`, `A_KRESET`, anchors), `own` (the kind's own text: literals, classes, groups recurse), `any` (any bytes, any length: `A_VAR`) |
| `path` | PATH-PRUNING readers: possessify's position reader (`first_of`'s "next character at a position", `gk_build`, `pss_walk`), `revdet`, the atomic discharge, any proof that "backtracking here cannot change the outcome" | `transparent`, `gate` (zero-width, narrows: `A_LOOK`), `opaque` (every byte, nullable; decline: `A_VAR`) |
| `reads` | the ONE marked set (`pcrec_bref_mark`: publish-at-close and the `--no-captures` keep set) | `none`, `refs` (the node's own group list: `A_BREF`, `A_VAR`, `A_CALL`) |

The two width columns are the poss_arms rev 2.1 N1 lesson (one reader getting
the other's answer was a live miscompile) made into a schema: a text reader and
a path reader can no longer be handed one answer. `-Wswitch` exhaustiveness
stays: the row table is indexed by kind with a static count assertion, so a
new kind without a row is a compile error. Stage 1a moves ZERO bytes: every
existing kind's row reproduces today's per-arm answers, checked by
`--emit-facts` over the corpus, possessify `marked/total` per pattern over
corpus and bench, and `scripts/emit_sweep.py` identity. The census of arms
(which arms become row reads, which keep code) is stage 1a's first artifact.

**Stage 1b adds A_CALLOUT's row:**

| kind | `text_width` | `path` | `reads` | analog |
|---|---|---|---|---|
| `A_CALLOUT`, `W_PRED` | `zero` | `opaque` | `refs` = every group | `A_LOOK` for text readers; `A_VAR` for path readers |
| `A_CALLOUT`, `W_ANY` | `any` | `opaque` | `refs` = every group | `A_VAR` for both |

A `W_PRED` site's `path` is `opaque`, NOT `gate`: P7 is the witness (`(\d+)`
followed by a site at the end of the pattern possessifies if the follow reader
sees the site as empty, and the answer moves). The same row binds every
whole-window start fact a VM artifact uses: a `W_ANY` site between `a` and `b`
means `ab` is NOT a required run, because the callee may consume bytes between
them (`text_width any`).

**Erasure is recorded as inexact** `[r1 A3]`. The prefilter (the hybrid's
capture-erased scan) reads `text_width` in language form: a `W_PRED` site
erases to the empty string and a `W_ANY` site to "any bytes, any length".
Either erasure is a RELAXATION (a vetoing site removes paths the scan keeps),
the same class as a lookaround's erasure, so the lowering records it in
`Nfa.erased` (a new `NFA_ERASED_CALLOUT` bit beside `NFA_ERASED_LOOK`). The
existing machinery then stays sound with no edit, as `emit_vm.c`'s comment on
`pcrec_vm_prefilter_window` already promises ("a relaxation added to the
lowering later ... records itself and reads inexact here"): `mrl_win` is
false, so neither the `prefilter-window` prune ceiling nor `VM_RESEED "exact"`
arms on a callout pattern. A callout pattern's prefilter proves a START,
never an END. (Unrecorded, the ceiling would lose vetoed matches: `(?:a|ab)`
with a check vetoing position 1, on `ab`, would answer "no match" where the
answer is `[0,2)`.) `verify`'s end proof is a different fact, computed on a
different machine (section 4.3).

This corrects engine_m4.md's recommendation (c) ("apply the prefilter to
callout patterns uniformly"), written when callouts were zero-width predicates
only (section 10a, conflict 3). Stage 1b declines the prefilter for callout
patterns outright (one `pf_admits` construct row, stating how `-fprefilter`
behaves there as its siblings do); stage 4 admits it under the rule above.

`[r1 D4]` **Pre-registered obligations.** The tree already holds obligations
for "the kind that adds a callout": `emit_dfa.c`'s req-handoff conjunct (g)
and its start-set seek ("NO VERB AND NO CALLOUT ... the kind that adds one
must add a `PF_KIND_*` bit ... and decline here"), with sabotage rows S475 and
S496 shipped UNREACHED, and `tests/codegen/run_ir_listing.sh` asserting the
`--emit-ir` callouts count is 0. Stage 1b adds `PF_KIND_CALLOUT` (the
`src/facts/kinds.c` exhaustive switch is its alarm) and RETIRES the callout
half of both conjuncts with this argument, recorded at each conjunct: a
skipped attempt is one the erased superset language cannot match (`text_width`
makes a site's erasure a superset: empty for a check, any bytes for a
consumer); a pattern with vetoes matches a subset; and fires on attempts the
engine skips are unspecified (FR1). S475 and S496 are re-scoped to verbs
(still UNREACHED until a verb compiles); stage 1b's own sabotage row for the
skip facts is S-IC6b (a `W_ANY` site read as empty). The ir_listing
expectation flips in the same change. (The alternative, declining both, costs
the handoff and the seek on every callout pattern; the manager may choose it
instead, and nothing else in this note changes.)

### 1.9 Where a site may appear

The registry's VM_ONLY row sends the pattern to the VM; the parser refuses by
name the positions not supported (never a miscompile). First-match:

| # | position | stages 1b-2 | from stage 3 `[r1 D11]` |
|---|---|---|---|
| 1 | inside a lookbehind | refused: "a callout inside a lookbehind is not supported" | same |
| 2 | inside a conditional's CONDITION (`(?(?C1)...)`, PCRE2's callout-before-assertion form) | refused | same |
| 3a | inside a group of the SAME pattern reachable by a subroutine call or recursion (`(?1)`, `(?R)`, `(?&n)` to a local group, `(?(DEFINE)`), or inside a RECURSIVE `lib` definition | refused: a recursive call re-enters the site at a depth the view does not describe | same |
| 3b | inside a NON-recursive `lib` definition reached by a plain call `(?&name)` | refused: "embedded code reached through lib.rxt is not allowed before pins" | LIFTED: allowed under §5.4 (pins); the view is the definition's own (below) |
| 4 | inside a group a DELIVERING call imports from a library (`rxt_format.md` §1.2) | refused | LIFTED as 3b |
| 5 | anywhere else: the main sequence, alternations, capture and non-capture groups, quantified groups, atomic groups, lookaheads | supported | same |

`[r1 CON-3, D11]` Through the CLI, a `lib`'s content reaches a target ONLY
through a call, and an `include` fragment's blocks are never CLI targets
(probes in the round: `target rx = <lib def>` and `target rx = <fragment
block>` are refused "no definition"). So rows 3b and 4 are where every reached
code segment lives, and lifting them is what gives stage 3's pins an input.
A non-recursive definition is written out at each call site (spliced), so a
site in it is an ordinary site at each splice; two calls give two sites.

**The view inside a definition** (rows 3b, 4, from stage 3). The definition's
author wrote the code against the DEFINITION's text, not the caller's, so the
site's groups are the definition's own, numbered as the definition numbers
them: `ncap` is the definition's group count plus one, and `caps[k]` is the
definition's group `k` at this splice. A plain call is capture-transparent
(`rxt_format.md` §1.2), so the caller's groups are not visible to it either.
The emitter builds this view as a per-site slot map (a local array of
`ncap` pairs copied from the splice's slots before the call): a cost paid only
at sites inside definitions. This is a semantics choice (section 10,
question 2).

Rows 1, 2 and 3a are lifted one at a time, each on a need, by a stage with its
own tests.

### 1.10 Firing classes and the `once` promise `[r1 FR6]`

Fire count is unspecified (1.7), but a reader of a pattern can still be told
one structural fact per site: how many times it can fire within one ATTEMPT
(one anchored try at one start position, within one engine run). The compiler
DERIVES it from the pattern's structure (never from the subject), reports it
in `--list-callouts` (5.6) and in the IR `callouts` section, and checks the
`once` promise against it.

**The derivation.** On the parsed tree, before any optimization pass (the
class is a fact about the pattern as written, and 1.8 forbids a pass that
would add fires):

- A **repeat** of a site: the site is inside a quantified group whose maximum
  is 2 or more (`*`, `+`, `{n,}`, `{n,m}` with `m >= 2`, and `{n}` with
  `n >= 2`, which reaches the site `n` times deterministically).
- A **live choice point before** the site: walk from the site up to the root.
  At each enclosing CONCATENATION, look at the items BEFORE the one that
  contains the site. Any choice point inside them is live at the site (on a
  later failure, the engine can resume it and reach the site again), unless it
  is SEALED: inside an atomic group `(?>...)`, a possessive quantifier, or a
  lookaround, that is itself one of those earlier items (completed before the
  site, so its choices were discarded). A choice point is an alternation of
  two or more branches, a quantifier whose minimum and maximum differ (greedy
  or lazy), or a call to a group or definition (conservatively: its body may
  hold choices). A backreference, an anchor, a fixed-count repeat of
  choice-free items, a conditional's selection, and another callout site (its
  callee is atomic, D38 §2) are not choice points.
- Enclosing constructs do NOT add choices on the way up: an enclosing
  alternation resumes LATER branches, which do not contain the site; an
  enclosing optional group (`?`, `??`, `{0,1}`) resumes the skip, which does
  not reach the site; an enclosing atomic group or lookaround seals only once
  it completes, so the items before the site INSIDE it are examined by the
  same concatenation rule.
- **Tail**: the site is the last item of the pattern at every level from the
  site up to the root (nothing follows it on any path to accept), and it is
  not inside a lookaround. A passing fire at a tail site completes the match.

**The classes**, first match:

| # | class (listing token) | rule | what the code can rely on |
|---|---|---|---|
| 1 | `once-per-match` | no repeat, no live choice point before it, and tail | at most one fire per attempt, and a fire that passes IS the match (the view it saw is the match's end) |
| 2 | `once-per-start` | no repeat and no live choice point before it | at most one fire per attempt |
| 3 | `repeated` | otherwise | may fire more than once per attempt |

The listing also prints `tail` beside a `repeated` site that is in tail
position (a passing fire there still completes the match; vetoed fires can
repeat). Examples, each with its class and the reason the compiler prints:

| pattern (site is `(?C1)`) | class | reason |
|---|---|---|
| `abc(?C1)` | `once-per-match` | no choice before; tail |
| `a(?C1)b` | `once-per-start` | `b` follows |
| `(?:x(?C1)\|y)z` | `once-per-start` | the enclosing alternation resumes `y` only |
| `^(\d+)(?C1)$` | `repeated` | `\d+` at offset 1 is a live choice point before the site |
| `^(\d++)(?C1)$` | `once-per-start` | the possessive seals `\d++` |
| `(?>\w+@\w+)(?C1)` | `once-per-match` | the atomic group seals its choices |
| `\w+(?C1)` | `repeated`, `tail` | a veto backtracks into `\w+`, which reaches the site again |
| `(?:x\|y)(?C1)` | `repeated` | the alternation before the site can be resumed (structural: on `x` the second branch never matches, but the class is never data-dependent) |
| `(?:(?C1)(a))+` | `repeated` | inside a repeat whose maximum is unbounded |
| `(?:a(?C1)){2}` | `repeated` | inside a repeat of count 2 |
| `(?=\d+(?C1))` | `repeated` | inside the lookahead, `\d+` before the site is live until the lookahead completes |

The rule is SOUND (a site with no repeat and no live choice point before it
is reached at most once per attempt: reaching it twice needs a loop or a
resumed choice that precedes it) and deliberately conservative (the
`(?:x|y)` row): a class is a structural guarantee, never a prediction from
the data.

**The `once` attribute** (2.2) is the user's promise that a site is class 1
or 2. The compiler checks it and refuses a site of class 3, naming the
construct that breaks it and the fix: "callout at offset 9 is marked once but
can fire again: the quantifier \d+ at offset 1 can be backtracked into; make
it possessive (\d++) or wrap it in (?>...)", or "... is inside the repeat at
offset 0". The promise costs nothing at run time; it is a compile-time check
that keeps the class from silently degrading when the pattern is edited.
(The refusal's text as shipped, and its verdict on whether the fix changes
what the pattern matches: `match_api.md` §11.8¶3, §11.8¶3a.)

**What the class bounds, and what it does not.** It bounds fires per attempt
WITHIN ONE ENGINE RUN. Two things the contract already names are outside it,
and the spec says so: (1) different start positions are different attempts;
(2) the tiered default's escalation (`match_api.md` §10.9) re-runs the whole
call after the fast tier gives up, so every site fires again in the second
run. Any other engine mode that runs an attempt twice at one start is a
violation the build must not introduce for a class 1-2 site: `verify`'s veto
edge honours it (4.2: a class 1-2 site's veto skips the VM re-run at that
start), and a stage-1b sabotage row (S-IC19) re-runs an attempt at the same
start and must be caught by the counting-binding check (standing question 2e).

### 1.11 The budget `[r1 D9, FR4]`

Frank ruled that code cannot read or spend the budget and that each fire
counts as a step against the match budget; D163 add. 6 Q1 rules one budget
meter per EXPORTED call, which every pcrec-matcher callee charges. Two parts,
with different preconditions:

- **Each fire is one step on the outer call's meter.** This needs no new
  carrier: the outer VM charges its own step counter at the site (1.2 step 1),
  so a site that fires too often gives up `PCREC_ERR_STEPS` like any
  backtracking blow-up. The spec's `PCREC_ERR_STEPS` row reads "the step
  budget (backtrack resumptions and callout fires) ran out". Lands with stage
  1b. Nothing in `rx_ctx` exposes the meter, so the code cannot read or spend
  it (FR4).
- **A pcrec-matcher callee charges the caller's meter.** This needs the
  carrier the alignment note names (`rx_ctx` gains one `rx_session *`,
  compound_callout_alignment.md §7.3/§9, an [IFACE-PUSH] abi event), which
  this note does not build. **Interim row, explicitly TEMPORARY** (the
  manager's D9 ruling): until the session lands, a pcrec artifact bound as a
  callee runs each fire on its own fresh budget, as every un-suffixed entry
  does today. Because each fire already costs the outer one step, the number
  of fires is bounded by the outer step budget, so one outer call's work is
  bounded by the outer budget times one plus the callee's budget. The spec
  states that multiplier beside §4¶4's ×2, labelled temporary, and the row is
  deleted when the session member lands ([IFACE-PUSH], which carries this
  note's reference).
- **User C code is not metered.** Its own work is the user's (FR4: it cannot
  read or spend the budget); only its fires are counted.

`rx_ctx` therefore stays unchanged in this plan (8.1); the alignment note's
carrier is the one future change to it, and it is [IFACE-PUSH]'s.

## 2. Two spellings, one node

### 2.1 The spellings

| spelling | example | owner module | PCRE2 reads it as |
|---|---|---|---|
| `(?C)`, `(?Cn)`, n in 0..255 | `(?C7)` | `callouts` | a numbered callout |
| `(?C` + delimited string, NOT starting with a language tag | `(?C"octet")`, `(?C"octet,consume")` | `callouts` | a string callout |
| `(?C` + delimited string starting with a language tag | ``(?C`c: return RX_CAP_SET(1) && RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;`)`` | `code-<lang>` | a string callout (valid PCRE2) |
| `(?{` [tag] code `})` | `(?{ return RX_CAP_SET(1) && RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL; })` | `code-<lang>` | error 111 (PCRE2 refuses it) |

`(?{` is a pcrec extension in a spelling PCRE2 refuses (D38 Q5's namespace
rule; measured: error 111). Perl reads the same text as embedded Perl; pcrec
reads it as embedded C (or the tagged language). `[r1 SLOT-18e]` The tagged
`(?C` string is different: it is a PCRE2-ACCEPTED spelling to which pcrec gives
a meaning (PCRE2 hands the text to the program). Frank's Q3 ruled it, so it is
not a conflict, but the namespace rule "a pcrec-only form is a spelling PCRE2
rejects" does not cover it, and the compliance row says so: the same bytes are
a string callout to PCRE2 and code to pcrec under `--allow-code`.

### 2.2 The attribute grammar `[r1 FR2, FR5, FR6]`

One grammar for every callout's attributes:

```
attr     := "consume" | "once" | "verify"     (v1 set; unknown -> refused by name)
attrs    := ( "," attr )*
tag      := lang attrs ":"                     code, both spellings
lang     := [a-z][a-z0-9_]*                    one registered language; "c" in v1
binding  := ident attrs                        the whole decoded (?C"...") string
```

- `consume` sets `W_ANY` (1.5); `once` is the promise of 1.10; `verify` sets
  the site's mode (section 4). Repeating an attribute is refused. Mode is per
  site (Q4). The same three attributes apply to every binding row, so there is
  one grammar and no binding-kind exception.
- In the **PCRE2 string spelling**, the decoded string is read first-match:
  `lang attrs ":" ...` with `lang` a registered language is CODE (owner
  `code-<lang>`, 1.1); otherwise `ident attrs` with `ident` a C identifier
  containing no `__` is a NAMED binding (`(?C"octet,consume")`); anything else
  is refused: "a (?C"...") string is a binding name (a C identifier, with
  optional ,consume ,once ,verify) or tagged code (c: ...)". A binding called
  `c` is still `(?C"c")`, since it has no colon.
- In **`(?{`** the tag is OPTIONAL and begins immediately after `{` with no
  whitespace; `(?{ ... })` with no tag is C, by grammar (fixed forever, never
  configurable, so a file's meaning never depends on a setting). A text that
  begins with `ident:` or `ident,` where `ident` is not a registered language
  is refused with a hint ("unknown language tag 'x'; if this is a C label, put
  a space before it") — a C label as the very first token is the only
  collision.
- A **numbered** callout has no string, so it declares attributes in the
  `.rxt` head (FR5): a file-level line `callout <n> <attr>...`, e.g.
  `callout 7 consume once`, repeatable, one per number; its CLI equivalent for
  `--pattern` text is `--callout 7:consume,once`. A `callout` line naming a
  number the pattern does not use is refused (a stale declaration is a bug,
  not a default). The library has no equivalent in v1: a library caller who
  needs a consuming numbered callout writes the named form; the `pcrec_options`
  member it would need waits for [IFACE-PUSH] (memory "interface push later").
  These spellings are the manager's.

A later language registers a row in the declared language table (`lang`, the
module `code-<lang>`, its end scanner for `(?{`, its glue emitter); its
registry rows are generated from that row (1.1); nothing else changes.

### 2.3 End rules

**PCRE2 spelling: PCRE2's rule exactly, no lexer.** The string ends at the
first lone closing delimiter; a doubled delimiter is one literal delimiter
(requirements P2/P3/P5: `{` closes with `}`, and `}}` is one `}`). The tag is
then read from the DECODED string. This keeps the same bytes meaning the same
pattern to both programs (the requirements' "worst kind of miscompile"
argument) and needs no knowledge of the language. The relief valve for code
full of braces is a delimiter the code does not use (`` ` `` or `$`), or the
`(?{` spelling. (Held in the round: 12 of 12 delimiter cases.)

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
   gnu modes ignore them; C23 removed them; under `-std=c11` a trigraph
   mismatch is a loud compile error, never a silent miscompile).
5. The segment ends at the brace that brings depth to 0, which MUST be
   followed immediately by `)`; otherwise refused: "(?{ ... }) must end with
   '})'". An unterminated literal or comment, or end of pattern at depth > 0,
   is refused naming the segment's START offset.

The pattern's own modes do not apply inside a segment: `(?x)` does not make
`#` a comment there (P6 is PCRE2's behaviour for the string form; `(?{` copies
it). Inside a character class `[(?{]` is three literal bytes, as today.

The per-row test table (requirement R-S4) is stage 2's scanner table: one row
per rule above plus `"}"`, `'}'`, `/* } */`, `// }` then newline, `<% %>`,
`1'000`, `u8"}"`, a `}` at depth 2 followed by `})`, and the refusals.

### 2.4 Errors (D26 tiers)

The construct's REALITY and OWNER are exact; wording is not:

| situation | diagnostic (shape, not wording) |
|---|---|
| `[r1 D17]` malformed `(?C`: a bad delimiter, a number above 255, junk before `)` (`(?Cx)`, `(?C256)`, `(?C1x)`, `(?C!x!)`) | refused AS MALFORMED in every module state; never "requires module" (these are not callouts, and "requires module" tells the user a module would make them valid) |
| `(?C` numbered/named, module `callouts` off | "(?C...) requires module 'callouts'" |
| embedded code, `--allow-code` does not name its language | "(?{...}) requires module 'code-c', which only the command-line option --allow-code=c (or the library's allow_code member) enables" |
| `[r1 T1]` `features` text naming `code-c`, in any source; a config's `pcrec` line carrying `--allow-code` | refused at parse: "code is enabled by --allow-code, not by a features list or a file" (5.1) |
| unknown tag / attribute, untagged non-identifier string, a binding name containing `__` | refused by name, offset of the site |
| `[r1 T4]` a Unicode bidi control or invisible format character in a segment (U+202A-U+202E, U+2066-U+2069, U+200B-U+200F, U+2060-U+2064, U+FEFF) | refused, naming the code point and its offset in the segment |
| a `once` site that can fire more than once per attempt | refused with the construct and the fix (1.10) |
| a `callout <n>` line for a number the pattern does not use | refused by name |
| end-rule failures | 2.3 item 5 |
| position not supported | 1.9's table |

`[r1 D17]` The malformed-`(?C` misstatement exists TODAY (every `(?C` form
answers "requires module 'callouts'"), so its parser fix is filed to land on
its own, ahead of stage 1b (section 9.4).

`[r1 D7]` Module `code-c` owns its own rows (1.1), so a pattern with embedded
code alone needs no `features callouts`: the code rows' gate is `code-c`, and
`callouts` gates only the numbered/named row. Both rows produce the same node
and reach the same emitter.

## 3. The generated function

### 3.1 Name, signature, placement

Each `CO_CODE` node becomes

```c
static ptrdiff_t <prefix>__code<seg>(const rx_ctx *ctx);
```

an `rx_matchfn`, `static` in the artifact's `.c`, `<seg>` the segment index
(1.1). The prototype is emitted before the VM function; the DEFINITIONS are
emitted LAST in the `.c`, after the matcher. Putting them last means no
`#line` has to be restored afterwards, so the artifact's bytes do not depend on
the output file name; gcc inlines a later-defined `static` function at `-O2`
as readily as an earlier one (probed in the round: 0 calls left).
`[r1 PREM-16f]` The bytes DO depend on the input path as typed (`#line
"../x/ipv4.rxt"` vs `"ipv4.rxt"`), so the identity gate and any
reproducibility claim pin the invocation's spelling.

The layout at the end of the `.c` `[r1 A8]`:

```c
/* ... the whole matcher ... */
#undef RX_CUT                  /* every artifact-internal macro still live (A8) */
/* ... */
#include "octet.h"             /* code-header lines (3.3), after the matcher */
/* code segment 1: ipv4.rxt line 4, column 18 */
#define RX_SUBJ ...            /* the macro set of 3.2 */
static ptrdiff_t ipv4__code1(const rx_ctx *ctx)
{
#line 4 "ipv4.rxt"
                  return RX_CAP_SET(1) && RX_CAP_LEN(1) <= 3 && octet_le255(RX_CAP_P(1), RX_CAP_LEN(1)) ? RX_PASS : RX_FAIL;
__builtin_trap(); }
#undef RX_SUBJ ...
```

The text is the DECODED segment (PCRE2's doubled delimiters undone; under a
`pattern-esc` line the `.rxt` escapes already applied, `rxt_format.md`
§1.5¶3). It is a function BODY: statements ending in `return`. Falling off
its end traps (the line after the text): no silent default value. A
declaration the user needs and has no header for can be written inside the
body (a block-scope function declaration is standard C), so no `cdecl` line
is needed in v1. The example tests `RX_CAP_SET(1)` first `[r1 CON-15]`: an
unset group's `RX_CAP_P` is NULL and its length -1, and the user's function
should not receive them.

**`#line` and columns** `[r1 D18]`. One `#line N "file"` precedes the text,
and the first line is padded to its source column, ONLY when the segment's
text maps one-to-one onto source lines: a `pattern` line or `--pattern` text
with no undone delimiter doubling and no tab or non-ASCII byte before the code
on its first line. Otherwise:

- a `pattern-esc` value is ONE source line whose decoded text has many lines,
  so the emitter writes `#line N "file"` before EVERY decoded line (all map to
  the opener's line `N`) and pads nothing; gcc then names the right line for
  every error, and no column;
- a first line whose prefix holds a tab, a multi-byte character or an undone
  escape is not padded (gcc counts display columns with `-ftabstop`, and the
  byte count would be wrong), so gcc's column there is not the file's.

Goal 4's measurable form is the LINE everywhere, the column where the rule
above pads.

### 3.2 The macro set (Q7: generated names only)

Defined immediately before each definition, `#undef`ed immediately after, so
nothing leaks between segments or into the rest of the file:

| macro | value |
|---|---|
| `RX_SUBJ`, `RX_LEN`, `RX_POS` | `ctx->subject`, `ctx->len`, `ctx->pos` |
| `RX_START` | the attempt start, `ctx->caps[0][0]` (1.3) |
| `RX_CAP_SET(n)` | `n` in `1 .. ctx->ncap - 1` and the group's end is set |
| `RX_CAP_S(n)`, `RX_CAP_E(n)` | the group's start / end, or `-1` when not `RX_CAP_SET(n)` |
| `RX_CAP_LEN(n)` | end minus start, or `-1` |
| `RX_CAP_P(n)` | `RX_SUBJ + start`, or `NULL` |
| `RX_G_<name>` | `[r1 A7]` a named group's NUMBER: for a name used by ONE group and spelled in ASCII, the constant; for a name a `(?J)` pattern gives to several groups, the number of the run member that is set at this fire, walked by the same algorithm the emitted `\k<name>` resolution and `match_api.md` §5.4¶6 use (so caller, matcher and code cannot disagree), or the run's first number when none is set (so `RX_CAP_SET` reads false); no macro for a non-ASCII name (read it by number) or a name containing `.` (a delivered group) |
| `RX_USER` | `ctx->user` (NULL for a code segment in v1, 3.5) |

`[r1 CON-15]` Every accessor taking `n` evaluates it ONCE (a GNU statement
expression), so `RX_CAP_S(i++)` is safe; every accessor is the guarded form
(requirement W5): an unset or out-of-range group reads `-1`/`NULL`, never an
out-of-range pointer. Slot 0 is not a group: `RX_CAP_SET(0)` is false and
`RX_CAP_S(0)` reads -1; the attempt start is `RX_START`. `RX_PASS`/`RX_FAIL`
are not in this set any more: they live once in the callout-artifact family
(1.5, 8.1) `[r1 D16]`. The user can still read `ctx` directly; the macros are
convenience, not a wall.

**What is live at the segment block** `[r1 A8]`. The `code-header` includes
and the segments come AFTER the matcher, so a user header's macros and pragmas
cannot rewrite pcrec's own code. Before the include block the emitter
`#undef`s every artifact-internal macro (`RX_CUT`, `RX_PRUNE_*`, `RX_SLOT_*`,
`RX_R_*`, `<prefix>_VALID_LB`, the pattern-dependent `RX_VAR_<name>` and
`RX_SLOT_GROUP<n>_*`), so what stays live there is the public contract (the
stamps and the shared ABI block's fixed literals) plus the macro set. A codegen
check computes, over a CORPUS of callout artifacts (not one; the
pattern-dependent names differ per pattern), the identifiers `#define`d and
still live at the segment block, read from the emitted text, and fails when
that set intersects the macro set or holds any name outside the public
contract. The spec reserves the `RX_` family for user headers too.

### 3.3 The user's headers: `code-header`

```
code-header c "octet.h"          # head line (file-level), repeatable
code-header c <stdint.h>
```

CLI equivalent `--code-header c:octet.h` / `--code-header 'c:<stdint.h>'`.
The language word is there so a later language declares its own imports the
same way. Rules (requirements R-S2, UC-3):

- Emitted in the generated `.c` ONLY, immediately before the first segment
  definition, after the matcher and the `#undef` block (3.1) `[r1 A8]`, in the
  order written, duplicates (same exact text) emitted once; never in the `.h`,
  so a program that only calls the matcher never needs the user's headers
  (DT-3.4).
- Emitted AS WRITTEN; pcrec never opens, resolves or reads the named file
  (the C compiler resolves it with the user's `-I`). Generation stays
  hermetic and the trust surface does not grow.
- Which heads contribute: the entry file's, and (from stage 3) the head of
  every `lib` file that contributes a segment to the target. An `include`d
  fragment has no head of its own beyond `include` lines (`rxt_format.md`
  §1.1). A `code-header` line is code (a header can contain anything), so a
  lib's lines fall under the same pin rule as its segments (section 5).
  `[r1 D15]` This changes `rxt_format.md` §1.1's `lib` row ("named definitions
  — and nothing else"), a stage-3 spec hunk.
- A `code-header` line in a target with no code segment is emitted anyway
  only under `--allow-code`; without it, the line is refused like a segment.

The user's build adds their sources and `-I` as for any C program; pcrec
writes no build rule (R-S3). `-o -` still prints the `#include` lines: the
output is self-contained of pcrec, not of the user's headers.

### 3.4 Diagnostics land on the user's line

The `#line` directive names the source as the user wrote it: the FILE operand
as given on the command line; an `include`/`lib` target as written in its
line, joined to its parent's as-written directory (never `realpath`, never an
absolute path the user did not write, so the artifact is reproducible across
checkouts); `--pattern` text as `"<command line>"`. The file name is escaped by
the existing C-text escaper (`pcrec_sb_ctext`; the round probed gcc decoding
an escaped `café "q".rxt` correctly). The line is the source line of the
segment's first byte; for a `pattern-esc` value every decoded line maps to the
opener's line (3.1) `[r1 D18]`. gcc's error then reads `ipv4.rxt:4:31: error:
...` (DT-3.3). pcrec's own refusals name the pattern offset and the segment's
start (2.3).

### 3.5 User state (requirement R-P7)

`ctx->user` is NULL for a code segment in v1. State lives where C programs
keep it: the user's own globals or `_Thread_local` objects declared in their
header, or the caller's per-call variables (`ctx->vars`, which reach a callout
because the site passes them on, 1.2). The context itself is read-only (FR3).
A per-segment `user=SYM` attribute that makes the site's `user` the address
constant `(void *)&SYM` is the D38 per-binding shape without D38's rejected
per-call parameter; it is filed as a later row, on a need.

### 3.6 Tests that need the user's C linked `[r1 T3, T6]`

Rev 0 linked user stubs from an `ext harness` block in the `.rxt`. That broke
`rxt_format.md` §1.12's graduation rule (aux is never acted on: "a build reads
it" is acting) and was a path by which a pattern file made the harness compile,
link and RUN C with no opt-in, which goal 1 forbids. Withdrawn. Instead:

- The callouts test section carries a TEST-OWNED harness manifest in its own
  directory (`tests/callouts/`; the file name and syntax are the build lane's),
  not `.rxt` syntax: it declares the section's visible opt-in
  (`--allow-code=c`) and the stub sources to link, which live beside it. The
  harness (`tests/harness/run.sh`) reads a manifest only from the directory of
  the section it is running, so no `.rxt` text can name a C file, and every
  other section has no manifest (the T2 check of 5.7 stays meaningful).
- `make test-axes` runs the harness, so it reads the same manifest; the axes
  runner reports, per axis, the count of callouts cases that were BUILT and
  LINKED (neither refused nor a link failure) and is red when it is below the
  section's floor `[r1 T6]`. (The round verified that a compile REFUSAL on the
  axis side is already caught as an undocumented refusal; a LINK failure gave
  no dump line on either side and was silent, which the counted floor closes.)
- `rxt_format.md` §1.12 is unchanged.

`examples/` gains one buildable example under D118's Makefile shape, whose
rule carries `--allow-code=c` visibly and links the user's C itself.

## 4. `verify` mode (Q4) `[r1 D1, D2, D12, A3, A5, A6]`

### 4.1 What it is

A `verify` site asks: find the match with the DFA, run the check on it, and
only on a veto run the VM, with the check inline, from that match's start. The
user declares it per site (Q4) because it is a bet on the data: it wins when
vetoes are rare and loses when they are common (standing question 1).

### 4.2 Realization: one FINISH row on `CR_VM` (D156)

Rev 0 built `verify` as a new row in the hybrid's attempt loop. The round
found that it re-derives FINISH (D156, `locate_finish.md` §1.3/§2.3: "after
L0, 'verify a candidate' has ONE home") and is the third member of the
"locate with a DFA, check at the end, finish on the VM" family (compound
clients 7 and 8; compound_callout_alignment.md unlock U6,
`locate-then-finish(Q; external verifier)`). **Ruled (manager, D1):** `verify`
is a FINISH row on `CR_VM` in D156's vocabulary, so "verify a candidate" keeps
one home; the compound controller over U6 is the END STATE, filed (section
4.6). D36/F7 hold literally: the artifact is a VM hybrid, `rx_info.engine` is
`"vm"`.

The row, `check-tail` (a placeholder id beside `FIN1`-`FIN4`; the listing
token is its behaviour name, 4.3):

| field | value |
|---|---|
| route | `CR_VM` (the hybrid's finisher route) |
| `take` | `SPAN` from the TAIL-FREE scan (below), and only that hand |
| `needs` | VM, plus the tail-site list (the sites in the pattern's tail, in order) |
| pass edge | every tail check returns `k_i >= 0`: report `[s, e + k_1 + ... + k_n)`, FIN2-shaped (no group to write: applicability row `reads-groups`) |
| veto edge | a tail check returns `-1`: `FIN3 verify-at` with an `AT` hand at `s`, i.e. one anchored VM attempt at `s` with ceiling `n` (the subject end, NO window ceiling `[r1 A3]`), the checks inline; its answer at `s` is the answer; none at `s` goes to the next edge. EXCEPT for a class 1-2 tail site (1.10): its one fire per attempt is the one just made, so a veto means no match at `s` and the edge is FIN4 directly (no second fire at `s`, and no VM run) `[r1 FR6]` |
| none at `s` | `FIN4 search-from` the next character start after `s` (RETRY on `CR_VM`) |
| give-up / refusal code from a check | the return table (1.6), propagate edges |

**The tail-free scan** `[r1 A3, A6]`. The scan this row takes its hand from is
built from R, the pattern with its tail sites REMOVED (not erased): `R T`
where `T` is the tail run of sites. Width-class erasure stays the rule for the
ordinary prefilter of every callout pattern (1.8), but here no site is erased
at all, so a `consume` tail cannot stretch the scan's end to the subject end
(with `W_ANY` erased to "any bytes", the scan language is `R·Σ*` and its end is
not R's). The hand is `SPAN` when R's own lowering records no erasure: R's
exactness is computed on R's machine, never read from `<PREFIX>_VM_RESEED`
(which describes the WHOLE pattern's scan and is inexact on every callout
pattern by 1.8). This is the "own exactness fact" the round asked for, and
D156's boundary projection computes it: `SPAN` when exact, `LOWER` otherwise
(and `LOWER` is not this row's `take`).

**One call site** `[r1 D2]`. The checks at `e` are called by the 1.2 emitter
with view source `finish-hand`; the edges are this row's. The stage-1b sabotage
rows (S-IC1 `-1` as pass, S-IC4 a collapsed give-up, S-IC6 row 10 removed,
S-IC11 the `W_PRED` trap removed) must reach both callers at stage 4.

### 4.3 Applicability: a declared first-match table

The rows that decide whether the FINISH row applies are about the PATTERN.
Rev 0's rows about the hand (`no-scan`, `end-unproven`) are gone: they restated
D156's availability (`needs ⊆ built`) and the hand kind, which the FINISH
machinery already computes once.

| # | row (listing token, D174 behaviour name `[r1 CON-19, SLOT-18a]`) | predicate | outcome |
|---|---|---|---|
| 1 | `checked-inline:denied` | `-fno-callout-verify` (a deny-only axis, 4.5) | inline |
| 2 | `checked-inline:mixed` | some site in the pattern is not a `verify` site | inline: the `verify` sites run at their positions, which is the defined answer |
| 3 | `checked-inline:not-at-end` | a `verify` site is not in the pattern's TAIL (the trailing run of `A_CALLOUT` nodes in the top-level concatenation) | inline (non-tail needs a snapshot, 4.6) |
| 4 | `checked-inline:reads-groups` `[r1 A5]` | some tail site's `ncap > 1`, the SITE's fact; since every site reads every group (1.3), this is "the pattern has a capture group", whatever `--no-captures` says | inline: the VM walks the candidate for the groups the check reads |
| 5 | `checked-after-match` | otherwise | the FINISH row of 4.2 applies; the hand decides `SPAN` (the row) or `LOWER` (FIN4, i.e. the inline hybrid) per candidate route, as for every FINISH row |

Rows 1-4 are DOWNGRADES and never change an answer. They are observable: the
stamp `<PREFIX>_CALLOUT_VERIFY` carries the token of the row that fired,
`--list-callouts` prints it per site, and `pcrec --list-axes` lists the axis.
`[r1 A5]` Row 4 keys on the site's fact, not on `<PREFIX>_NCAPS > 1`: under
`--no-captures` `NCAPS` is 1 while the site still reads group 1, and rev 0's
row let `(\d+)(?{c,verify: ... RX_CAP_LEN(1) ...})` reach a view with no group.

### 4.4 Why the FINISH row gives the defined answer

Let the pattern be `R T`, `T` the tail run of `verify` sites and `R` with no
site (rows 2 and 3) and no capture group (row 4). Assume the checks are pure
(1.7). The scan is R's own machine, exact (the hand is `SPAN`).

1. **Earlier starts.** The scan's `s` is the leftmost start at which `R`
   matches. At any earlier start no path of `R` completes, so no path reaches
   `T`, nothing fires, and the backtracking order has no match there.
2. **The first fire at `s`.** The backtracking order explores `R`'s paths at
   `s` in priority order; the first to reach `T` is `R`'s first-priority
   match, which ends at `e` because the hand is R's exact leftmost-first span
   (premise: the scan is R with `T` REMOVED, so `e` is R's end whatever `T`'s
   width class; and `SPAN`, so the end is proven). With no group to read
   (row 4), the view at that fire is exactly the `finish-hand` view. Pure
   checks return the same values.
3. **All pass.** The backtracking order accepts on that path with
   `[s, e + Σk)`; so does the row.
4. **A veto.** The backtracking order continues with `R`'s next path at `s`.
   The row runs the VM anchored at `s` with no window ceiling, which IS the
   backtracking-order engine at `s`: it repeats the first fire (same veto, by
   purity) and continues identically. Same answer at `s`, including "none".
   For a class 1-2 site (1.10) no second path at `s` can reach the site, so the
   backtracking order has no match at `s` after the veto, and the row's FIN4
   edge says the same without the VM run.
5. **No match at `s`.** Both continue at later starts; by item 1 the scan's
   next answer is the next start at which `R` matches.
6. **Budgets.** The row skips the VM's walk on a pass, so it can ANSWER
   where the inline VM gives up on a budget, never the reverse — the latitude
   `match_api.md` §6.3.5¶8 already states for adaptive reseeding.

Held in the round: a simulator of exactly this algorithm against the
backtracking order found 0 counterexamples in 120,000 cases (`W_PRED` tails,
half UTF), and its sabotage twin (S-IC15's shape) 709 differences. Fire counts
differ (on a veto the first candidate fires twice, except at class 1-2 sites);
they are unspecified in every mode (1.7). The control is `make test-axes`: the
axis's deny flag runs the same corpus inline, so a row that changes an answer
is red.

### 4.5 Axis and bits `[r1 D14, SLOT-19]`

The axis `callout-verify` is DENY-ONLY (force key 0, as 23 of the 44 axes in
`src/core/axes.def` are): the user's per-site `verify` attribute is the
"force", and rows 2-4 are cases where the row is unsound or unbuildable, which
a force flag could only refuse. It spends ONE option-word bit. Count at
`86a0fed00`: `PCREC_BIT(n)` is used for n = 0..54 and 56, bit 55 is reserved by
the kit (`-fno-kit-size-drop`), so 7 bits are free (57..63), and bit 57 is
filed by D174 for [IFACE-PUSH]'s `PCREC_NO_WINDOW_REPORT` candidate. Stage 4
leaves 6 free (5 if bit 57 lands first); [IFACE-PUSH]'s hard trigger fires at 4
or fewer. `--allow-code` takes no bit (5.1).

### 4.6 What `verify` cannot do yet, and what would trigger it

- A NON-TAIL site needs the site's `(pos, caps)` on the winning path,
  recorded during the scan or recovered after it: [CAP-SPAN]'s or
  [MATCH-EVENTS]'s mechanism. Trigger: a measured pattern whose check cannot
  be moved to the tail.
- A group-reading check gains from the row only when [CAP-SPAN] places
  captures without the VM walk. Trigger: the same. `[r1 D12]` This is why the
  requirements' UC-1b (four groups, its check reads them) is a row-4 DOWNGRADE
  case, and a capture-free UC-1b' (the same validator with `(?:...)` groups and
  a check that parses `[RX_START, RX_POS)` itself) is the row's case.
- `[r1 D1]` **The end state: the compound controller.** `verify` is literally
  U6, `locate-then-finish(DFA part over R; external verifier = the tail
  checks; VM part as the veto finisher)`, compound.md §A.2's type check already
  admits the external callee, and client 8 (lookahead-as-check) is the same
  shape with an anchored DFA as the check. When the compound's controller
  reaches B-steps that host a VM part, the FINISH row moves to it with the
  same take/needs/edges; its applicability rows 2-4 are shared with clients
  7/8's admission. Trigger: U6's own (a client whose finisher is not
  pcrec-compiled) or stage 4 landing beside a compound B-step that hosts a VM
  part, whichever comes first.
- `post` (reject and resume, requirements M1) changes answers wherever the
  pattern has several candidates at a start; it is admissible only where the
  compound's unique-end admission (D163 addendum 7, clients 7/8) proves one
  candidate. Q4: only on a measured need.

## 5. The trust gate (Q5)

### 5.1 The opt-in `[r1 T1, D20, SLOT-18c]`

`--allow-code=LANGS` (a comma list; `c` in v1) on the COMMAND LINE, or the
library's `pcrec_options` member `allow_code` (a language list, default NULL =
none), enables module `code-<lang>` for that invocation. Nothing else enables
it. The mechanism is ONE column, not a list of refused spellings:

- **The module table gains a GRANT column** (`any` | `invoker-only`).
  `code-<lang>` rows are `invoker-only`, which (i) excludes them from `all` and
  from every named set (D37's `all` today is the union of EVERY registry row's
  feature, so `--features all --pattern '(?C)'` already reaches "enabled but
  not implemented": without the column, a file's `features all` would grant
  code), (ii) refuses their name in every `features` text however it arrives
  (a block, a config, a `pcrec` line, `--features`, `pcrec_options.features`),
  and (iii) leaves the CLI option and the options member as the only setters,
  writing a separate mask the feature resolver cannot set. The library thus
  has ONE gate for code, not two members that could disagree.
- **Disclosure** is the stamp `<PREFIX>_CODE_LANGS` `[r1 CON-19]` (the
  languages present), not `PCREC_FEATURE_MODULES`: `code-c` is not in the
  feature roster, so no `--features all` artifact's `PCREC_FEATURE_MODULES`
  moves at stage 2 (D178 add. (a)'s reason for not growing the roster), and
  §8.1's zero-mover expectation holds.
- **A config's `pcrec` line carrying `--allow-code` is refused at parse**,
  through today's by-name chain in `rxt_source.c` beside `--analysis` and
  `--measures` (`rxt_format.md` §1.1¶2). That chain, the CLI's span
  containment and the `saw_prefix` tail flag are three mechanisms answering
  one question ("which sources may set this option"); `--allow-code` is the
  family's fourth member. Per the round's D20 (PLAN), stage 2 lands on today's
  shape and a per-option SCOPE row (`any` | `not-config` | `invoker-only`) is
  FILED, with the GRANT column above as its first use; its trigger is the next
  option that needs a scope.
- **Stricter than Q5's endorsed text** (listed in 10a): Q5's recommendation,
  which Frank's answer opened with "yes", allowed a config's `pcrec` line to
  carry the opt-in "in the author's own repo"; this note refuses it on every
  config line, because a config can itself be reached through `include`/`lib`
  and a line cannot know whose repo it is in.
- No environment variable, no auto-detection.

The library takes the opt-in as a `pcrec_options` member, NOT a `flags` bit:
the option word's free bits are what [IFACE-PUSH]'s hard trigger watches
(4.5).

### 5.2 Local and reached `[r1 T2]`

- **LOCAL**: a FILE operand named on the command line, `--pattern` text, and
  the pattern string a library caller passes in. Local code needs only the
  opt-in ("perhaps local rxt is exempt", Q5).
- **REACHED**: every file read through an `include` or `lib` line, at any
  depth, including a `lib` found through `--lib-path`/`-I`.

**The harness keeps provenance.** Today `tests/harness/run.sh` compiles every
block, fragment blocks included, as `--pattern` text, which would make a
fragment's code LOCAL (laundered) under the callouts section's opt-in, and a
stage-3 "unpinned include refused" test run through the harness would agree
with itself. The rule: the harness passes the opt-in ONLY for blocks whose
source file is the section's entry file. Before stage 3, a code segment in a
fragment block is therefore compiled without the opt-in and refused, and the
harness expects that refusal. From stage 3, the harness compiles a fragment
block that carries code through pcrec's FILE path, naming the entry file and
the block, so pcrec itself walks the include chain and applies 5.4; the harness
never asserts provenance. (The FILE-path selector's spelling is the build
lane's; the rule is that provenance comes from pcrec reading the chain, never
from the harness.)

### 5.3 The pin `[r1 D11]`

```
include "frag/ipv4.rxt" sha256 <hex64>
lib "lib/net.rxt" sha256 <hex64>
```

The pin REUSES `rxt_format.md` §1.6¶7's spelling and case rule
(`@file:"path" [as <id>] [sha256 <hex64>]`: keyword then value, exactly 64 hex
digits, compared case-insensitively), so the format has one content-pin
spelling, not two. The value is SHA-256 of the file's bytes exactly as read,
no normalisation, so `sha256sum FILE` prints it. Any other value shape is
refused by value shape; `--list-schema` shows the key on both rows.
`[r1 D15]` §1.6¶8 ("`pcrec` checks neither the hash nor the 64-digit syntax")
becomes false for `include`/`lib` lines and is amended in stage 3's hunk: pcrec
checks these pins; the harness legs still own the `@file` case-line pins.

### 5.4 Rules, per segment and per `code-header` line (first match)

| # | the code's source | action |
|---|---|---|
| 1 | `--allow-code` does not name its language | refused (2.4) |
| 2 | local | allowed |
| 3 | reached, before stage 3 | refused: "embedded code at lib/net.rxt:12 is not allowed: code from included files needs pinned include lines (not in this build)" |
| 4 | reached, and SOME chain from a local file to it has a line with no pin | refused: "embedded code at lib/net.rxt:12 refused: the lib line at main.rxt:3 carries no sha256 pin" (the first unpinned line named) |
| 5 | reached, every line on every chain pinned (and verified, 5.5) | allowed |

Transitivity follows Q5's leaning (each line pins its own target) and is
also what makes the pins sufficient: a pinned file's bytes include its own
pin lines, so a pin at the top fixes the content of everything below it
exactly when every link below is pinned. An unpinned middle link could be
edited to point at different code, which is why row 4 names the first
unpinned line anywhere on the chain, not only the last.

`[r1 T7]` **The same file reached by two chains.** The closure parses a file
once per real path (`closure_walk` skips a lib already seen), so a file
reached by a pinned and an unpinned chain would otherwise carry whichever
chain came first. The rule is order-independent: code in a file is allowed only
when EVERY chain the closure finds to that file is fully pinned (row 4 names
the first unpinned line of the first failing chain).

A reached file with patterns and no code needs no pin (Q5: "an include
without a hash may still supply patterns").

### 5.5 Pin verification and the ONE SHA-256 `[r1 D11, T7]`

A pin, when present, is verified when the file is read for a build,
regardless of `--allow-code` and whether the file holds code: it is a
statement about the file, and a stale one is the signal Q5 asks for. A
mismatch refuses the target: "lib/net.rxt hashes to <h>, but the lib line at
main.rxt:3 pins <p>; re-inspect the file and update the pin". The hash is
computed over the SAME buffer the parser reads (one read: no second `open`, no
window between hashing and parsing). `[r1 PREM-16c]` `--list-source` stays as
pure as today (it already resolves `include` real paths): it reports the pin
as written and verifies nothing.

**The one SHA-256 home.** `analyze/sha256.{c,h}` is already a zero-dependency,
one-shot FIPS 180-4 SHA-256 (`pcrec_analyze_sha256_hex`, built into
`build/pcrec-analyze`), and pcrec computes no SHA-256 today (`src/` mentions
`sha256` only as field names). `analyze/` must not read anything under
`src/`/`cli/`/`lib/`, and `src/` should not reach into `analyze/`. So the one
implementation MOVES to a dependency-free leaf both builds compile: a new
top-level `shared/` directory holding `sha256.{c,h}` alone (its own CLAUDE.md
saying "leaf files only: no include of src/, lib/, cli/ or analyze/, no
dependency beyond the C library's `stddef.h`/`stdint.h`"), compiled separately
into `build/pcrec-analyze` and into `libpcrec`. Neither binary links the
other, analyze/CLAUDE.md's independence rule holds verbatim, and `analyze/`'s
"may not share code" clause concerns its deliberate TWIN of pcrec's analysis
READER (the counters and the document dump), not this digest: no check
compares the two binaries' digests, and the control for both is the NIST
vectors plus `sha256sum`. The directory name is the manager's; the
alternative, if a new top-level directory is unwanted, is libpcrec compiling
`analyze/sha256.c` directly (one Makefile line, an odd dependency direction,
same single source). A second copy is NOT proposed.

### 5.6 The reviewer's view `[r1 T4, T5, D15, FR6]`

`pcrec --list-callouts FILE` prints one row per site: target, source
`file:line:col`, spelling, binding row (1.4), language and attributes, width,
FIRING CLASS (1.10) with its reason, mode and the 4.3 row that fired, the
provenance chain with each line's pin, and the DECODED code. It works WITHOUT
`--allow-code` (its job is to let a reviewer read code BEFORE trusting it),
parses but compiles no C, and prints the code column through an ESCAPER:
printable ASCII as is, every other byte numbered (`\xNN`), and any Unicode
bidi control or invisible format character flagged by name on the row (the
CVE-2021-42574 shape: a reviewer must never see different code from what gcc
compiles). Such characters are also refused in segments (2.4), so the flag
fires on the refused input the reviewer is looking at.

`[r1 D15, SLOT-14]` **One row source.** The IR listing already reserves a
`callouts` section and a `callout-sites` summary row (`ir_listing.md` §3.7,
"no producer, so this section is empty"); the emitter already counts
`VE_CALLOUT` events for it. That section is the ONE per-site row source
(columns: label, binding row, width, firing class, mode, the 4.3 row);
`--list-callouts` is its trust-facing projection plus provenance, pins and
escaped code; `<PREFIX>_CALLOUTS` (the site count) reads the same count.

In the artifact, every segment carries its one-line source comment (3.1),
whose file name and code excerpt go through the existing C-text escaper.

### 5.7 Tool paths never pass the opt-in (requirement T2)

pcrec-bench's loaders, the oracle store, fuzzers, `--analysis` of exemplar
files, and every `make test` section except the callouts section compile
without `--allow-code`. The callouts section's opt-in is in its harness
manifest (3.6), where a reader sees it, and applies to its entry files only
(5.2). A check places a code segment in another section's corpus and asserts
the refusal. Its way to fail: with the opt-in check removed (sabotage S-IC9),
the segment compiles and the expected refusal is missing.

### 5.8 What a pin does not cover

Pins cover pattern-file bytes. They do not cover a header a `code-header`
line names or a source the user links: pcrec never opens those, and the
user's compiler finds them through the user's own build. The spec says so in
one sentence.

### 5.9 The entry-point table `[r1 T5]`

One row per pattern-taking entry, DERIVED from the CLI's own mode list (the
test enumerates the modes from `pcrec --help`'s mode table and fails on a mode
with no row, so a new mode cannot slip past the gate) plus the library and
harness entries:

| class | entries | without the opt-in | with it |
|---|---|---|---|
| writes C or an artifact | a FILE target, `--pattern` (with or without `--pattern-esc`), `-o -`, `--emit-main`, `--trace` (an instrumented matcher), `pcrec_compile` and the library's other compile entries, the harness | refuses every segment by name, emits zero bytes | 5.4's rules |
| describes a pattern | `--emit-ir`, `--emit-facts`, `--count-groups` (as listed by the mode table at build time) | parses code (a later group must still be counted), writes no C, prints no code text unescaped | same |
| reviews | `--list-callouts` | works; code printed escaped (5.6) | same |
| takes a construct or nothing, not a pattern | `--explain`, `--probe-ask`, `--list-axes`, `--list-definitions`, `--list-families`, `--list-limits`, `--list-schema`, `--list-source`, `--list-syntax`, `--list-verbs` | no change (none compiles a pattern; `--explain` describes the `(?{` construct like any other) | same |

Rev 0's goal 1 named "every `--list-*` that compiles", which is the empty set
today and, read literally, made `--list-callouts` refuse what it exists to
show.

## 6. A pcrec artifact as a callout

Q6's purpose: a compiled regex can BE a callout. The entry is
`<prefix>_match`, exported by every artifact unconditionally (D38 item 2): an
`rx_matchfn`, anchored at `ctx->pos`, returning the CONSUMED length
(`match_api.md` §3.1¶19, which keeps `\K` from breaking the advance) or `-1`
or a code; it ignores `ncap`/`caps` and reads `ctx->vars`, so the outer
call's variables reach the inner pattern. Binding it is one line in the
user's C:

```c
const rx_callout_ref rx_callout_octet = { octet_match, NULL };
```

and the outer pattern says `(?C"octet,consume")` `[r1 FR5]` (a binding is a
check unless it says `consume`; without it, the inner match's positive length
traps at row 9). The same thing from inline code:
`(?{c,consume: return octet_match(ctx); })` — the segment hands its own
read-only `ctx` through.

What it means, stated in the spec: the inner match is ATOMIC and OPAQUE (D38
§2, D38's F5: its captures do not reach the outer pattern; D38 item 5's v2 is
now "a group map on the binding unit", alignment §6.3); wrapping the site in a
group captures what it consumed; an inner give-up propagates through the
return table without escalating the outer tier (1.6); its budget is the
interim row of 1.11; two artifacts of different abi in one translation unit
fail to compile (the existing `PCREC_RX_ABI_H` guard). `[r1 CON-18]` The two
artifacts must share the ENCODING: a `-e utf8` inner called from a byte outer
can receive a mid-character `pos` and return `PCREC_ERR_STARTPOS` (row 6
traps), and a byte inner inside a UTF-8 outer can consume half a character
(row 10 traps); the spec says a mismatch traps at the first misaligned fire.
The source-level alternative inside one `.rxt` is a definition call
`(?&name)`, which is transparent to backtracking; the guide shows both and the
difference. A DFA artifact whose `_match` is the `"search-filter"` form
(`match_api.md` §3.2¶6) may skim the subject on a failing probe; the stamp says
which form it is.

## 7. The PCRE2-convention wrapper (Q6)

For a function written to PCRE2's contract (0 continue, positive fail this
path, negative abort), over pcrec's `rx_ctx`:

```c
#define RX_CALLOUT_PCRE2(name, fn, user_)                                     \
    static ptrdiff_t rx_callout_pcre2__##name(const rx_ctx *ctx_)            \
    {                                                                        \
        int r_ = (fn)(ctx_);                                                 \
        if (r_ == 0) return 0;                                               \
        if (r_ > 0)  return -1;                                              \
        __builtin_trap();     /* abort: reserved, no v1 meaning (Q6, D38) */ \
    }                                                                        \
    const rx_callout_ref rx_callout_##name = { rx_callout_pcre2__##name, (user_) }
```

`fn` has type `int fn(const rx_ctx *)`; the wrapped binding is a check (it
returns only 0 or -1), so the site needs no `consume`. `[r1 D16, SLOT-9]` The
macro belongs to the CALLOUT-ARTIFACT FIXED-LITERAL family (section 8.1),
emitted wherever the artifact's shared ABI block is emitted (the `.h`, or the
single stream under `-o -`) on every artifact with a callout site, under its
own `#ifndef` guard; its helper names sit inside the `rx_callout_` family, and
the namespace row that refuses `__` in a binding name (1.4) keeps a binding
from colliding with them (the round compiled the collision: a redeclaration
error). Porting a body written against `pcre2_callout_block`:

| PCRE2 block field | pcrec |
|---|---|
| `subject`, `subject_length`, `current_position` | `ctx->subject`, `ctx->len`, `ctx->pos` |
| `start_match` | `ctx->caps[0][0]` at a site (1.3): the attempt start, which is what libpcre2 10.46 reports (its manual says `\K` moves it; the binary does not) |
| `offset_vector[2k]`, `[2k+1]` | `ctx->caps[k][0]`, `[1]` |
| `capture_top` | none; `ctx->ncap` is the artifact's group count plus one at every site (1.3), and an unset pair reads `-1` |
| `callout_number`, `callout_string` | none: the binding IS the callout's identity (`match_api.md` §5.2¶7) |
| `mark`, `callout_flags`, `pattern_position`, `next_item_length` | none in v1 |

A function that takes a real `pcre2_callout_block *` is V-A's compat layer
(generation-time block assembly, D38 §4), not this macro; the artifact never
includes `pcre2.h`.

**Abort.** Per Q6 and D38 there is no abort in v1. `[r1 SLOT-18d]` The code
is RESERVED NOW, as Q6 asked: `PCREC_ERR_ABORT`, value −17 (the next free
value after the subst block's −11…−16 in `match_api.md` §4¶1's table), meaning
"the callee ends the whole search with no match", reserved in stage 1b's spec
hunk so no other producer takes it, and not emitted until a measured need.
Landing it splits the return table's row 8 (abort jumps to the search's
no-match epilogue) and makes the macro's negative branch return it.

## 8. abi and spec impact

### 8.1 What moves

Everything this design emits appears ONLY in an artifact with a callout site,
except one item: the call sites and their return-table rows, the segment
functions and their macros, the `code-header` includes and the `#undef`
block, the slot-0 save/store/restore, the step charge, the publish-at-close
marks for every group (the marked set is unchanged for a pattern with no
callout, 1.3), the definition-site view maps (stage 3), and the
**callout-artifact fixed-literal family** `[r1 D16, SLOT-9]`: a new
`match_api.md` §1 family, conditional (callout artifacts only) and
self-guarded, holding `RX_PASS`, `RX_FAIL` and `RX_CALLOUT_PCRE2`. Stamps on
callout artifacts only: `<PREFIX>_CALLOUTS` (the site count),
`<PREFIX>_CALLOUT_BINDINGS` (the binding symbols the artifact needs),
`<PREFIX>_CODE_LANGS` (stage 2) and `<PREFIX>_CALLOUT_VERIFY` (stage 4). No
pattern that compiles today contains a site (every `(?C` is refused and `(?{`
is a parse error), so the identity gate's expectation for stages 1b-5 is ZERO
movers in the existing corpus beyond the abi line, and for stage 1a zero movers
at all. That is checked, not assumed: each stage runs the gate before its abi
step, and a sabotage row (S-IC20: the marked set made unconditional) shows the
gate can fail.

The one exception `[r1 D6]`: the shared ABI block's `rx_matchfn` comment
("traps on" `PCREC_ERR_INTERNAL`) is corrected to "propagates" (D163 add. 6
Q3) as ITS OWN abi event before stage 1b, moving that one comment line in
every artifact (the whole corpus moves, on that line only; the gate's
expectation for that event is exactly that line). It is filed as a plan item
(section 9.4).

- `rx_ctx`: unchanged (slot 0 carries the attempt start, 1.3; the budget
  meter's carrier is [IFACE-PUSH]'s, 1.11).
- `rx_info`: no new member in v1. A member would move every artifact's
  initializer; the stamps carry the facts, and a run-time mirror, if wanted,
  belongs to [IFACE-PUSH].
- `pcrec_options`: one new member, `allow_code` (5.1), no `flags` bit.
- The option word: ONE bit, stage 4's deny-only axis (4.5).
- The return table: the shared `callsite_rows[]` gains the `conv` column and
  rows 9-10 (1.6), emitted only at callout sites; the compound's artifacts do
  not move (checked at the lift).

**abi events** `[r1 D14]`. In order: (0) the INTERNAL comment (its own event,
before 1b); (1) stage 1b, with stage 5 riding it if the two land together;
(2) stage 2; (3) stage 4. Stage 1a emits nothing and is not an event. Stage 3
is an event only if its build adds contract-valued emitted text (a stamp or a
fixed literal); the view map at definition sites is internal code for inputs
that did not compile before. Each event's number is "the next number at
landing" (never a literal in this note), its readers are found BY GREP for the
then-current number (the `.abi` stamp, test expectations, every spec sentence,
the identity gate's (B) pin, and the readers that never cite the number:
registry, codegen, rxtsource, per the D94 addendum), and the bump moves the
`PCREC_RX_ABI_H` line of every artifact (that line is the re-pin). Briefing
stages 1b and 5 together, and stage 2 directly after, keeps the re-pin windows
to the minimum.

### 8.2 Spec hunks (D80), by stage `[r1 D15]`

The list was derived by grep (`callout`, `(?C`, `ncap`, the module rosters,
the namespace table, the ASCII promise, `sha256`) at `86a0fed00`, D94-style;
the build lane re-runs the grep at its own base and adds what it finds.

| stage | spec files and sections |
|---|---|
| 0 (INTERNAL comment) | `match_api.md` §2 (the shared block's quoted `rx_matchfn` comment) |
| 1a | none (no caller-observable change); `decision_families_survey.md` §3.8/§3.14 and the plan rows [DEC-KINDATTR]/[POSS-CTX-TABLE] record the table |
| 1b | `match_api.md`: §1 (the callout-artifact fixed-literal family; §1¶5-¶6 amended for a conditional family), §2¶6 ("every emitted call site sets `ncap = 0`": a callout site sets the group count plus one), §4¶1 (`PCREC_ERR_ABORT` −17 reserved; the STEPS row counts fires), §4¶3 last sentence and §10.9¶6 (a callee's give-up, 1.6), §4¶4 (the temporary callee-budget multiplier, 1.11), §4¶10 (the callout site as the table's second producer, the `conv` column, rows 9-10, the row order), §5 (the site view: `ncap`, publish-at-close for every group, slot 0, the `--no-captures` keep set), a new callouts section (binding rows, fire contract, the defined answer and the PCRE2 compatibility sentence, width classes, attributes, firing classes and `once`, positions, unbound bindings), §6.3 stamp inventory (`_CALLOUTS`, `_CALLOUT_BINDINGS`); `cli.md` (module `callouts`; `--callout`; `--emit-main`'s refusal; the namespace table's row 2 "not yet enforced" becomes enforced, plus the `__` binding-name row); `rxt_format.md` §1.1 (the `callout` head line) and §1.13 (its schema row); `ir_listing.md` §3.7¶1 (the `callouts` section gains its producer and columns); `pattern_language.md` (the `(?C` forms and owner rows, the attribute grammar, the malformed row); `registry.md` (PC-3 for the `(?C` rows); `docs/pcre2_compliance.md` (the `(?C` row, via the compliance-refresh skill) |
| 2 | `match_api.md` (segment function, macro set, `_CODE_LANGS`; §6's ASCII paragraph scoped: "every byte is ASCII and compiles clean under `-Wbidi-chars`, except the bytes of a code segment and a `code-header` line, which are the user's as written"; bidi controls in segments are refused), the library options (§8.2's `pcrec_options` table: `allow_code`); `rxt_format.md` §1.1 (`code-header` row) and §1.13 (schema rows); `cli.md` (`--allow-code`, `--code-header`, the `pcrec`-line refusal, the module roster: `code-c` is invoker-only and outside `all`, §1.17¶3; the entry-point table's describe-only modes, §2.10/§2.13); `registry.md` (the module roster and GRANT column; PC-3's extension treatment of the `(?{` rows, which PCRE2 refuses with error 111); `pattern_language.md` (the `(?{` spelling and the tagged `(?C` owner, the bidi refusal); compliance (the `(?{` row: pcrec extension, Perl difference; the tagged `(?C`: PCRE2-accepted, pcrec meaning) |
| 3 | `rxt_format.md` §1.1 (`sha256 <hex64>` on `include` and `lib`; the `lib` row's "nothing else" gains `code-header` lines), §1.6¶8 (pcrec now checks `include`/`lib` pins), §1.13; `cli.md` (`--list-callouts`, the trust rules of section 5); `match_api.md`'s callouts section (§1.9 rows 3b/4 lifted, the definition-site view) |
| 4 | `tuning.md` (axis `callout-verify`, deny-only), `match_api.md` §6.3 (`_CALLOUT_VERIFY` and its tokens) and the callouts section (`verify`) |
| 5 | `match_api.md` (the wrapper macro and the porting table) |

`docs/guide/` gains a use-case page at stage 2 (pointing at the spec), with
the anchored-validator example first (requirements W1), the firing classes and
`once`, and one worked example of the three escaping layers (`.rxt`, PCRE2
delimiter, C; requirement R-S6).

### 8.3 Standing questions

Answered at the top of this note.

## 9. Staged build plan

Each stage is independently landable: its own module surface, tests,
sabotage rows, spec hunks and abi step. Sabotage ids are placeholders
(`S-IC*`); the build lane takes real ids from its brief's range and checks
each witness reaches its site (`REACH_ONLY=1`, [MECH-REACH]).

### 9.1 The stages `[r1 D3, D11, D12]`

**Stage 0 — the INTERNAL comment (its own abi event, D6).** One comment line
in the shared ABI block. Gate: the identity gate moves exactly that line on
every artifact. Can land any time before 1b.

**Stage 1a — the per-kind attribute row (zero movers; [DEC-KINDATTR] +
[POSS-CTX-TABLE]'s kind-level rows).** The census of per-`AKind` arms (which
become row reads, which keep code), then the row table of 1.8 over today's
kinds with its `text_width`, `path` and `reads` columns and a static count
assertion. No new kind, no emitted byte. Gates: `--emit-facts` over the corpus,
possessify `marked/total` per pattern over corpus and bench, and
`scripts/emit_sweep.py` identity, all 0 movers. Sabotage, one per pass family,
each flipping an EXISTING kind's row value so the gate goes red: S-IC21 the
first-set/possessify family reads `A_LOOK`'s `path` as `transparent`; S-IC22
the width/required-run family reads `A_VAR`'s `text_width` as `zero`; S-IC23
the NFA-lowering family reads `A_LOOK`'s erasure as exact; S-IC24 the marked
set drops `A_VAR`'s `reads`. (The context record {follow, may_end, encl, left}
of [POSS-CTX-TABLE] is NOT needed by the callout; it stays filed under that
row with its trigger restated as "the next context-dependent possessify edit".
The manager may fold it in; nothing else changes.)

**Stage 1b — the call site, extern-bound (module `callouts`; [M4-CALLOUTS]
step 2).** `(?C)`, `(?Cn)`, `(?C"name[,attrs]")` with every PCRE2 delimiter;
the `callout` head line and `--callout` for numbered attributes; the
malformed-`(?C` row (if the independent fix of 9.4 has not landed);
`A_CALLOUT` and its attribute row (1.8); `VE_CALLOUT`'s producer as the one
emitter with the `vm-slots` view source (1.2); binding rows 2-3 (1.4); the
site view with `ncap` = all groups, every group published at close and in the
`--no-captures` keep set, and the slot-0 save/restore (1.3); the lift of
`callsite_rows[]` to the shared emit layer with its `conv` column, rows 9-10
and the row order (1.6); the callee-give-up bit (1.6); the step charge per fire
(1.11); `NFA_ERASED_CALLOUT` and a `pf_admits` row declining the prefilter
(1.8); `PF_KIND_CALLOUT` and the retired conjunct halves, S475/S496 re-scoped
(1.8); the firing-class derivation, the IR `callouts` section and the `once`
check (1.10); the position table (1.9); the namespace rows (enforced row 2,
`__` refused); `--emit-main`'s refusal; the fixed-literal family; `_CALLOUTS`
and `_CALLOUT_BINDINGS`; `PCREC_ERR_ABORT` reserved in the spec. Tests
(`tests/callouts/`, stubs linked through the section's harness manifest, 3.6):
the backtracker and libpcre2 legs of §9.2 over the generated population (floor
1,000) plus D1/D2/P7-P10 shapes, the `(?s).*(?C"vetostart")x` start veto (A1),
`(?:(?C"g1set")(a))+` on `aa` and `(?:(?C"see")(a)|(b))+` on `ab` (A2),
`a\Kb(?C"see")c` checking both the reported start and the callee's `RX_START`
(A4), `(a)b(?C"g1set")` under `--no-captures` (A5); an enclosing-group case
(`(a(?C"see1")b)+`); a repeated-group retention case; give-up propagation (a
binding returning `PCREC_ERR_STEPS`) and a binding returning
`PCREC_ERR_FRAMES` inside a tiered outer artifact (D8); fires charged as steps
(a binding that always vetoes under a small `--step-budget` gives up STEPS);
an over-long return and a mid-character return (expect a trap); a `W_PRED`
binding returning 1 (expect a trap); an artifact bound as a callout with
`,consume` (section 6); a binding that consumes two bytes between two literals
(`a(?C"two,consume")b` on `axyb`, against the required-run and minimum-width
facts); the malformed forms `(?Cx)`, `(?C256)`, `(?C1x)`, `(?C!x!)` refused as
malformed with `callouts` on and off (D17); the firing-class table of 1.10 as
listing expectations and each class's bound checked by a counting binding over
the corpus; `once` accepted on every class 1-2 example and refused, with its
reason, on every class 3 example; DT-4.1 through a counting binding;
`make test-axes` over the corpus with the counted floor. Sabotage: S-IC1 the
site treats `-1` as a pass; S-IC2 an enclosing group is left unmarked; S-IC3
possessification ignores a site; S-IC3b possessify's position reader reads a
`W_PRED` site's `path` as empty (the P7 witness); S-IC4 a give-up is collapsed
to `-1`; S-IC5 the slot-0 restore is dropped (the `a\Kb` witness); S-IC6 row
10's check is removed; S-IC6b the required-run/skip facts read a `W_ANY` site
as empty; S-IC11 the `W_PRED` trap (row 9) is removed; S-IC19 an attempt is
re-run at one start (caught by the class-bound check); S-IC20 the marked set is
made unconditional (the identity gate goes red); S-IC25 callout refs omitted
from the marked set (the `--no-captures` witness); S-IC26 the step charge per
fire is dropped; S-IC27 the `once` check accepts a site inside a repeat.

**Stage 2 — embedded C (module `code-c`) with the local-only gate.** Both
code spellings; the generated language rows (1.1); the tag grammar; the `(?{`
C scanner; the generated function, macro set (statement expressions,
`RX_G_<name>` rules), the `#undef` block and `#line` per 3.1; `code-header`
(head and CLI) after the matcher; `--allow-code` and `allow_code`; the GRANT
column (5.1); the bidi refusal (2.4); ALL reached code refused (5.4 row 3;
pins arrive in stage 3, so stage 2 is safe alone); the harness rule of 5.2;
`_CODE_LANGS`. Tests: the scanner table (2.3; one row per rule, each refusal
included); UC-1a (DT-1.1-1.6); UC-3 (DT-3.1-3.4, a multi-line `pattern-esc`
segment's error on the right line); DT-4.1 inline; the entry-point table
(5.9), one test per row, generated from the mode list; `features all` refused
for code in a block, a config, a `pcrec` line, `--features` and the library;
`features code-c` and a `pcrec`-line `--allow-code` refused; a code segment in
a fragment block refused under the harness (5.2); the T2 check (5.7); a check
returning 1 and a segment falling off its end (expect a trap); the live-macro
check over a corpus (3.2); a bidi control refused and flagged. Measurement
card: the inline-mode card of standing question 1 and goal 3b. Sabotage:
S-IC7 the scanner does not skip string literals; S-IC8 an unknown attribute is
accepted; S-IC9 the opt-in check is removed; S-IC10 `#line` is dropped; S-IC28
`all` includes `code-c`; S-IC29 the harness passes the opt-in to fragment
blocks; S-IC30 a user header is emitted before the matcher.

**Stage 3 — pinned reached code and the reviewer's view (scheduled;
manager's D11 ruling).** `sha256 <hex64>` on `include` and `lib`; the ONE
SHA-256 moved to `shared/` (5.5); provenance chains; 5.4 rows 4-5 and the
every-chain rule; 5.5 (one read); §1.9 rows 3b and 4 lifted, with the
definition-site view (1.9); lib `code-header` lines under the same rule; the
harness's FILE-path compile of fragment blocks with code (5.2);
`--list-callouts` (5.6). Tests: NIST vectors and `sha256sum` agreement over
the corpus's pinned files; pinned/unpinned/mismatched for `include` and for
`lib`; upper-case hex accepted; a three-file chain with an unpinned middle
link (refused, naming it); a file reached by a pinned and an unpinned chain
(refused in either declaration order); a pinned file with no code still
verified; patterns from an unpinned file still compile; a site inside a lib
definition reading the definition's own group 1 while the caller has its own
group 1; a site inside a recursive definition still refused; `--list-callouts`
rows, without `--allow-code`, with escaped code and class columns. Sabotage:
S-IC12 the pin compare is skipped; S-IC13 only the last link is checked;
S-IC14 the local exemption reaches included files; S-IC31 the first chain's
verdict is used when a second is unpinned; S-IC32 the definition-site view
uses the caller's numbering.

**Stage 4 — `verify` (designed; briefed after a census).** Per the manager's
D12 ruling, its brief follows the D1 ruling (made: 4.2) and a CENSUS of
eligible shapes: how many of the requirements' and the bench's validation
shapes pass 4.3's rows 2-4 with an exact R (no lookaround, atomic group or
`\K` in R), counted, with the patterns listed. Scope: the `verify` attribute's
effect; the prefilter admitted for callout patterns under 1.8's language rule
(replacing 1b's blanket decline); the tail-free scan; the FINISH row
`check-tail` and its applicability table (4.2-4.3); the `finish-hand` view
source; the deny-only axis; `_CALLOUT_VERIFY`. Tests: UC-1b' (capture-free)
answers equal UC-1a's on DT-1.1-1.5 with the stamp `checked-after-match`;
UC-1b with the stamp `checked-inline:reads-groups`; a D2-shaped `verify`
pattern whose first candidate is vetoed (the VM fallback must find the
second); `(?:a|ab)` with a check vetoing position 1, on `ab`, answering
`[0,2)` both inline (the ceiling, A3) and under `verify` (the fallback runs
with no ceiling); a `verify,consume` tail (the scan must be R's, A6); a class
1-2 tail site vetoed (FIN4 edge, one fire); a downgrade per row 2-4 with its
stamp, row 4 under `--no-captures` included; under `-e utf8`, a veto followed
by a resume after a multi-byte character; `make test-axes` (the deny flag is
the control, 4.4). Measurement card (memory "new method needs measurement
card"): goal 3c's twins, veto-free and veto-heavy. Sabotage: S-IC15 a veto
answers "no match at s" without the VM (for a class 3 site); S-IC16 row 4 is
skipped; S-IC17 the resume steps one byte instead of one character; S-IC33 the
callout lowering does not set `Nfa.erased` (the `(?:a|ab)` witness under the
inline hybrid); S-IC34 the fallback keeps the window ceiling; S-IC35 the scan
erases a `consume` tail instead of removing it.

**Stage 5 — the PCRE2-convention wrapper.** `RX_CALLOUT_PCRE2` in the
fixed-literal family and the porting table. Tests: the same check native and
through the macro, equal answers; a negative return traps; under `-o -` the
macro is present. Sabotage: S-IC18 a positive return maps to `0`. Rides 1b's
abi bump if briefed with it (COST-9: as its own landing, D77 would ask for a
need).

**Stage 6 — later phases, not designed here.** The template side (`${{ }}`,
`${( )}`: requirements R-T1-R-T10, its two hard problems being the group
declaration R-T3 and once-per-match against the sizing pass R-T5; it reuses
section 3's function/macro/`#line` machinery and section 5's gate); `post`
mode (on a measured need); non-tail `verify` (with [CAP-SPAN]/
[MATCH-EVENTS]); the compound controller as `verify`'s end state (4.6); the
`user=SYM` attribute (3.5); lifting rows 1, 2 and 3a of 1.9; the library's
numbered-attribute member and the budget session ([IFACE-PUSH]); `--check-c`;
other languages.

Order: 0 and 1a before 1b; 1b, 2, 3 are a chain (each needs the previous);
4 needs 2 and its census; 5 needs only 1b and is best briefed with it.

### 9.2 The control, so it does not share pcrec's source `[r1 FR1]`

For each case the test author writes a pattern in pcrec's spelling and a
check BODY in the macro vocabulary of 3.2. The pcrec side compiles both as
usual. Two independent legs:

- **The backtracker (always).** A test-owned backtracking matcher written from
  §1.7's stated semantics (starts in order, paths in priority order, every
  fire honoured), with the check bodies compiled into it through an adapter
  header the test author writes. The r1 round's `naive.py` is its precedent
  (4,455 patterns, 0 answer differences against libpcre2 with optimizations
  off). It shares no code with pcrec's emitter or its segment macros. It
  carries `consume` sites, which libpcre2 cannot express. Its answer is the
  expectation; it never compares fire logs (fire counts are unspecified).
- **libpcre2 10.46 (on its subset).** A test-owned rewriter turns every
  `(?{c:...})` or `(?{...})` into ``(?C`c:...`)`` (backticks in the body
  doubled), and the driver registers one `pcre2_set_callout` function that
  dispatches on `callout_string_offset` to a per-site function whose body is
  the SAME text compiled under an ADAPTER header the test author writes from
  PCRE2's documented block (`RX_POS` is `cb->current_position`, `RX_CAP_S(n)`
  reads `offset_vector` under `capture_top`, `RX_START` is `start_match`, and
  the native returns map `0 -> 0`, `-1 -> 1`). The driver runs each case at
  DEFAULT flags and with every answer-moving `PCRE2_NO_*` option set (the
  survey's set, 1.7); a case whose two libpcre2 answers differ is
  "PCRE2-sensitive" and reported, never failed; on the rest pcrec must equal
  the default-flag answer (goal 2b). `consume` sites are excluded (no PCRE2
  equivalent).

The shared item is the check text, which is the test's INPUT; the engines, the
view construction and the macro definitions on each side are independent, so a
disagreement in, for example, which groups a site may read shows up as a red
case rather than agreeing with itself. Named bindings use the same scheme with
a stub function compiled into each driver.

### 9.3 The 20 draft usage tests, mapped

The drafts used PCRE2's return convention; under Q6 each check is rewritten
to `RX_PASS`/`RX_FAIL` and the requirements' illustrative `(?C{...})` becomes
`(?{...})` or a tagged string (untagged it is a binding name, 2.2). Each
expectation comes from the backtracker of 9.2 before it becomes a test
`[r1 FR1]` (rev 0's re-oracling of DT-1.6 under "reference flags" is dropped;
the round found its answer, `[1,9)`, the same under every flag set anyway).

| draft | stage | form |
|---|---|---|
| DT-1.1 - DT-1.5 | 2 (UC-1a) and 4 (UC-1b' answer-equal to UC-1a; UC-1b as the downgrade case) | `.rxt` blocks |
| DT-1.6 | 2 | `.rxt` block; expectation from the backtracker |
| DT-3.1, DT-3.2 | 2 | `.rxt` blocks with `code-header`, stubs from the harness manifest |
| DT-3.3 | 2 | build check: the missing header's gcc diagnostic names the `.rxt` and its line (and a multi-line `pattern-esc` case) |
| DT-3.4 | 2 | codegen check: the `.h` contains no user `#include` |
| DT-4.1 | 1b (named counting binding) and 2 (inline) | asserts the match and `n >= 1`, never a fire count |
| DT-2.1 - DT-2.7, DT-4.2, DT-4.3 | 6 (template side) | not in this plan |

Population: 11 of the 20 drafts land in stages 1b-4 (6 + 4 + 1); 9 belong to
the template phase (7 + 2). Each stage's own new cases are counted in its
report, and goal 2's generated population has its floor in the runner.

### 9.4 Remodel overlap, filed items and related rows `[r1 D14, D17, D19, D21]`

Overlap with in-flight rows (D153: a row touching a remodel site sequences
behind it), from the `STATE:started` rows at `86a0fed00`:

| stage | in-flight row | site shared | verdict |
|---|---|---|---|
| 1a | [DD-11.5] (a new `A_CTX` node class through the same passes) | the per-kind arms of the fact walks and possessify | WAIT for [DD-11.5]'s next landing, then 1a rows `A_CTX` too |
| 1a | [ART-POSS-ARMS] follow-ups / [POSS-CTX-TABLE] | `src/opt/possessify.c` | RIDE: 1a is that row's kind-level half |
| 1b | [COMPOUND] / [ENTRY-TABLE] (E1-prime; `emit_compound.c`, entries) | the lift of `callsite_rows[]` | WAIT for the in-flight E-step that edits `emit_compound.c`, then lift |
| 1b | [MEMFN] migration (VM per-byte literal chain, [OPT-VMLIT]), [OPT-LITSCAN] | `emit_vm.c`'s VM body | NONE in kind (the producer is a new event), but sequence the abi bump through the manager among the kit's events |
| 1b, 2 | [FINDALL-NEXT] (entries, `rx_info`) | the shared ABI block (stage 0's comment) | RIDE: schedule stage 0 in a window with no other shared-block edit |
| 1b | [VAR] (`rx_ctx.vars`) | the view's `vars` | NONE (read only) |
| 2 | [UCP] / [UPROP-MORE] (registry rows) | `src/parse/registry.c` | NONE in kind; rebase |
| 4 | [OPT-REVEND] (the boundary projection, match-end forms) | the hand kind `SPAN`/`LOWER`, `RX_VM_RESEED` | WAIT: stage 4 is briefed after its census anyway |
| 4 | [ENG-TACTICS], [REGIME] | the hybrid's search entry | WAIT for the entries remodel's FINISH-row landing |

Filed items (PLAN dispositions of the round, for the manager to file):

- **Stage 0**, the INTERNAL comment abi event (D6).
- **The malformed-`(?C` parser fix** (D17): today `(?C256)`, `(?Cx)` and
  `(?C1x)` answer "requires module 'callouts'", a reality-tier misstatement;
  a small parser fix lands independently of this plan.
- **A pcrec-bench `[inbox]` note at stage 1b's landing** (D19): the bench's
  `grp-callout` (`ca(?C1)t`) moves from did-not-compile to a link failure
  (undefined `rx_callout_1`).
- **The per-option SCOPE row** (D20, 5.1).

Related rows the note now cites `[r1 D21, COST-10]`:

- [POSTFACT]: tier 1 lowers REGULAR predicates (a numeric range over a digit
  span) into the automaton with no C and no VM; it answers UC-1's octet check
  without code. This note's value over it is the non-regular checks and the
  user's own C; stage 4's census counts only those.
- [BREF-SPAN]: a superset DFA plus a span-equality check, the same
  locate-then-check shape as `verify`; a fourth family member for the
  compound end state (4.6).
- [MATCH-EVENTS]: its trigger asks that the binding surface be designed with
  callouts. This note fixes the binding unit (`rx_callout_ref`, `user` NULL for
  code segments, the attribute grammar) and adds no event channel; the events
  row's design reads 1.4 and 2.2 as given.
- [M4-CALLOUTS]: its step-2 text predates D38 (10a, conflict 2).

## 10. Questions that are Frank's

Rev 0's two questions are ANSWERED (2026-10-26): question 1 by FR1 (do not
track PCRE2's optimization-dependent answers; §1.7), question 2 by FR2
(a check by default, `consume` opts in), extended by FR5 to every callout.

Two semantics questions remain, in plain words:

1. **When a check is written inside a library definition, which group numbers
   does it see?** (Stage 3.) Say `lib.rxt` defines `octet` as `(\d+)` followed
   by a check reading group 1, and your pattern calls it as
   `^(\w+)=(?&octet)$`. In your pattern, group 1 is the `\w+`; in the
   definition, group 1 is the `\d+`. Forces: the library author wrote the
   check against the definition's own text and cannot know who calls it; a
   plain call keeps none of the definition's groups for the caller anyway.
   Leaning: the check sees the DEFINITION's own groups (group 1 = the `\d+`),
   at a small cost only at sites inside definitions. The alternative is the
   caller's numbering, which would make a library check's meaning depend on
   every caller.
2. **What "once per match" means in the firing classes.** You listed three
   classes: once per match (tail), at most once per start, may fire
   repeatedly. This note reads "once per match" as: the check sits at the very
   end of the pattern AND nothing before it can be retried, so it runs at most
   once per starting position and, when it passes, that IS the match (for
   example `(?>\w+@\w+)` followed by the check). A check at the end after a
   retryable part (`\w+` then the check) can still run several times at one
   start (each veto makes `\w+` give back a character), so it is listed as
   "may fire repeatedly" with a note that it is at the end. Leaning: keep that
   reading, because a promise that holds only when the check passes is not
   much of a promise. The alternative is to call every end-of-pattern check
   "once per match", meaning "at most one PASSING run per match".

## 10a. Conflicts found (STOP RULE) and how this note reads them

1. **The return convention.** NO conflict between Q6 and D38: D38's native
   convention IS Q6's. The requirements' R-P5/W4 recommendation (PCRE2's
   convention inline) is superseded by Q6; its W4 danger is what FR2 answers.
2. **[M4-CALLOUTS]'s step-2 text vs D38.** The plan row still describes
   `extern int rx_callout_n(const rx_callout_block *)` with PCRE2's 0/positive/
   negative block contract as the native ABI. Ruled (manager, 2026-10-26): the
   text is stale; D38's `rx_callout_ref`/`rx_matchfn` governs and the PCRE2
   block lives in the compat layer (D38 §4); the row's body is amended.
3. **engine_m4.md's prefilter recommendation (c) vs D38's consuming
   callouts.** Ruled: erasure by width class (1.8), and `[r1 A3]` recorded as
   inexact, so a callout pattern's prefilter proves a start, never an end.
4. **Q4 ("the DFA finds the match") vs D36/F7 ("a pattern containing a
   callout compiles to the VM engine only").** Readings: (a) the artifact
   stays a VM artifact whose finisher runs the check at the DFA's end; (b) a DFA
   artifact carrying a VM fallback (a new artifact class, amending F7);
   `[r1 D1]` (c) a compound controller `locate-then-finish(DFA part; external
   verifier; VM part)` (U6). Ruled (manager, D1): (a), specified as a FINISH row
   on `CR_VM` (4.2) so "verify a candidate" keeps its one D156 home, with (c)
   filed as the end state (4.6). F7 holds literally.
5. **D38's per-binding `user` vs anonymous segments.** Not a conflict, a gap:
   a segment has no binding, so its `user` is NULL in v1 (3.5); the
   `user=SYM` attribute is the D38-shaped way to fill it later.
6. **Requirements R-P3 (a match-start field in `rx_ctx`).** Resolved without
   touching the frozen struct: slot 0 carries the attempt start at a site,
   saved and restored around the call because it is `\K`'s register (1.3).
7. **Requirements R-P2/R-S4 ("the segment IS PCRE2's `(?C{...})`").**
   Superseded by Q1/Q3: `{` remains a valid delimiter, but code needs its
   tag (`(?C{c: ...})`); an untagged `(?C{x=1;})`, as the requirements'
   examples wrote it, is a binding-name string and is refused as not an
   identifier.
8. `[r1 D9]` **D163 add. 6 Q1 (one budget meter per exported call) vs
   §8.1's "`rx_ctx` unchanged".** Resolved by splitting the ruling (1.11): the
   per-fire step (FR4) needs no carrier and lands at 1b; a pcrec-matcher callee
   charging the caller's meter needs the session member and waits for
   [IFACE-PUSH], with an explicitly temporary spec row meanwhile.
9. `[r1 SLOT-18c]` **Q5's endorsed text vs §5.1 on config `pcrec` lines.**
   This note is stricter (no config line may carry the opt-in); the reason is
   in 5.1. A departure from the endorsed text, listed for the manager.
10. `[r1 FR6]` **`verify`'s veto re-run vs a class 1-2 site's bound.**
    Resolved without a downgrade: for such a site the veto proves "no match at
    `s`", so the FINISH row's veto edge is FIN4 and the site fires once (4.2,
    4.4 item 4).
11. `[r1 FR1]` **The libpcre2 leg of the control after FR1.** Read as a
    filtered cross-check (1.7, 9.2); if the manager reads FR1 as dropping it,
    goal 2 (b) and the libpcre2 leg go, and nothing else moves.

One observation for the build lane, not a conflict: the registry has a single
flavour bit (`FLAV_PCRE2`), and the pcrec-only `${name}` row carries it; the
`(?{` rows follow that precedent rather than adding a flavour.
