# [DD-13b.W1] Implementation note — wave 1 of the grown `.rxt` format

**Status: DESIGN-FIRST DELIVERABLE 1. NO CODE IS WRITTEN.** The lane
brief stops here for the manager's review and a critic panel. What
follows is the plan a reviewer is meant to attack, not a record of work
done.

Against: `format_design.md` (revision 2, the ratified note), D87, D88,
D61, D85, D80, D76, D77, D26, and the r44 panel record
(`docs/dev/reviews/2026-08-29-r44-dd13b-format.md`). Where this note
DEPARTS from the format note it says so at the point of departure, with
the code that forced it; those departures are collected in §6 for the
manager, because two of them change a number the format note published.

## 0. How to read this

### 0.1 Claim marking

Same three kinds the format note uses (its §0.1), and for the same
reason:

- **MEASURED** — a command was run and its output is quoted. Every
  measurement in this note was taken under the manager's HOLD, so the
  population is small by construction: file reads, and **three single
  compiles** of `/home/duxevents/pcrec/build/pcrec` at main `3372e1e`
  (§1.6). No `make`, no sweep, no battery.
- **CITED** — quoted from a ruling, a decision, a spec or the tree, with
  its `file:line`.
- **ARGUED** — reasoning from the above. The panel's natural target, and
  marked so it is not mistaken for either of the others.

A fourth mark appears in this note and not in the format note:

- **DECIDED** — a point the format note left to the implementer, or one
  where the tree contradicts the note. Each is flagged inline and
  repeated in §6 so the manager can ratify or reverse it. There are
  **six**, and four of them make W1 smaller.

### 0.2 The design in one paragraph

W1 splits the `.rxt` parser along the seam the format note already
draws: **pcrec owns the HEAD grammar and the whole-file resolution, the
harness keeps its BODY parser**, because pcrec must read the file anyway
to resolve `lib`/`name`/`target`/`config` for `--source`, and a second
implementation of the head in bash would be two derivations of one
grammar (learnings §3). run.sh gains three block-scoped arms and one
call out to `pcrec --list-source`; its thirteen existing arms are not
touched, which is how INV-COMPAT is discharged by construction rather
than by re-verification. **The composer is a sub-parse on one `Ctx`**:
save the cursor and the numbering scope, parse the definition's own text
in its own number space, restore, then re-base the subtree by a walk —
which is D87 rule 7(i) executed literally. A bound definition is
injected as `A_REP{0,0}( A_CAP{no} ( body ) )` — **the AST shape
`(?(DEFINE)…)` already desugars to** (`mod_recursion.c:418`) — so
`A_CALL.target` binds to it through `callgraph.c`'s existing
number-to-`A_CAP` bind with no new mechanism and no new node kind. Two
consequences fall out of that shape and both make the design better: the
definition's wrapper takes an assigned number, so the composer and the
harness's textual control agree slot for slot with **no derived offset**
(§2.6, and it reverses a recommendation in the format note's §2.3.3);
and provenance never becomes a field on `Ast`, because a sub-parse's
offsets are already local to the definition's own text (§2.9, and it
preserves PARSE-1, which the format note's §2.12 would have broken).
`--emit-composed` is a **text splice driven by a position list**, not an
AST serializer, so no second "AST → PCRE2 text" mechanism is created
(§2.10).

### 0.3 What this note does not design

- **The struct TYPE** — `struct { rx_span local, domain; } from;` is
  [V-I]'s (plan.md:737). W1 delivers the SLOTS, the scope paths and the
  two refusals; it emits no struct. §2.8 states the interface, which is
  the format note's §2.13 list unchanged.
- **W2 and W3 productions.** Nothing in `include`, `@file:`, `mc`,
  `tag`, `freq`, `analysis`, `use`, `oracle`, `variant`, `testee`,
  `option` is built, and the head parser REFUSES each by name with "not
  in this build" (§1.3). D77 at wave granularity, per the format note's
  §1.4.
- **Diagnostic wording** — D26. This note says what must be refused and
  what a refusal must NAME; it does not write the sentences.
- **[LIB]'s store scan** — §6.0's two mechanical refusals (subject
  anchors, `\K`) are the [LIB] row's, not W1's. W1 builds no store.

---

## 1. What lands where

### 1.1 The seam: who parses the `.rxt` file

**CITED, the tree as it stands.** There are two `.rxt` parsers today and
they are both the harness's:

| file | language | lines | what it parses |
|---|---|---|---|
| `tests/harness/run.sh` | bash | 1051 | the whole file; an `if/elif` chain of 13 `[[ =~ ]]` arms (`run.sh:811-1021`), catch-all hard error at `run.sh:1016-1021` |
| `tests/harness/verify_rxt.py` | python3 | 418 | `parse_rxt` (`verify_rxt.py:113-182`), 10 kinds, its own oracle path; `# pcre2-only` has meaning HERE and nowhere else (`verify_rxt.py:121`) |

**CITED, `run.sh:1016-1021` and r44-grammar G6:** any non-blank,
non-`#` line before the first `pattern` is a hard error today, so a head
cannot change the meaning of an existing file — it can only make new
files parse.

**W1 adds a THIRD parser, in pcrec, and that is the design's first
choice.** `--source <file.rxt>` must resolve `lib`, `name`, `target` and
`config` before it can compile anything, so pcrec has to read the file.
The alternative — the harness parses the head in bash and hands pcrec a
flattened command line — was considered and rejected on two grounds:

1. `config c from a, b` (cascade), `with c1, c2` (MAX-WINS on caps,
   later-wins per flag), block scalars and the four lexical contexts are
   a dictionary problem, and bash has one associative array and no
   nesting. **ARGUED**, but see the counter-case below.
2. It puts the head grammar in the harness, where pcrec cannot see it —
   and pcrec's `--source` would then need its own copy. Two
   implementations of one grammar is the drift hazard learnings §3
   exists to name.

**So the split is: pcrec owns the HEAD; run.sh keeps the BODY.** And
because a `target` names a block's `name` — a BODY line — pcrec must
read the body too, at least as far as `pattern` / `name` / `description`
/ `flags` / `features` / `encoding` / `engine` / `budget`. It ignores
every expectation line (`m`, `n`, `ms`, `ns`, `g`, `gp`, `gu`, `perr`,
`frames-buffer=`), which are the harness's business and no part of a
compile.

**This leaves the BODY grammar with two implementations, deliberately,
and §3.1 is the control that keeps them honest.** That is a worse
position than one implementation and a better one than three: the two
are in different languages, written by different authors, and the
differential over the 179-file corpus is a real control rather than a
self-join (learnings §3's requirement on a control).

**The counter-case, stated because a reviewer will raise it** (ARGUED):
one could instead have run.sh read pcrec's dump for EVERYTHING and keep
only its case-line parsing. That collapses the body to one
implementation. It is rejected because it rewrites the parser
R-COMPAT-1 protects, on the wave that must prove R-COMPAT-1 — the change
and its own proof would share a source, which is precisely learnings
§3's shape. If W2 or W3 wants that collapse later, INV-COMPAT will by
then be a check with history rather than a promise.

### 1.2 File by file

| # | file | language | change |
|---|---|---|---|
| F1 | `src/parse/rxt_source.c` (**new**) | C | the HEAD grammar + the body's directive lines; the four lexical contexts; block scalars; `config` cascade and composition; `target` resolution; the definition set. Produces one `RxtSource` (arena-owned). |
| F2 | `src/core/internal.h` | C | `RxtSource`, `RxtDef`, `RxtTarget`, `RxtConfig` declarations; `NamedGroup` gains `scope` (§2.7); `Ast.u.cap` gains `at` (§2.10); `Ctx` gains the composer's scope stack and assignment table (§2.2, §2.9) |
| F3 | `cli/main.c` | C | `--source`, `--target <prefix>`, `--lib-path DIR`, `--emit-composed`, `--list-source`; `-o <dir>` semantics (§1.5). Today's option chain is `if/else strcmp` from `main.c:203`; `-o` writes exactly one `.c` + one `.h` (`main.c:740-786`) |
| F4 | `src/core/compile.c` | C | one new call in `compile_driver` between `pcrec_parse` (`compile.c:874`) and `pcrec_altcls` (`compile.c:890`) — §2.1; `ctx_fail` (`compile.c:16-29`) consults the provenance scope — §2.9 |
| F5 | `src/parse/mod_named_groups.c` | C | B1: `(?<3>…)` and `(?<name=3>…)`, dispatched after `(?<` — §1.4 |
| F6 | `src/parse/mod_recursion.c` | C | B2 `(?&^.name)` and B3 `(?&site=name)` / `(?&=name)`, in `rc_name_call` (`mod_recursion.c:269`) — §1.4 |
| F7 | `src/parse/registry.c` | C | three `RegRow`s for B1/B2/B3, so `--list-syntax` carries them (D24/D65; format note §3.3) |
| F8 | `src/opt/postresolve.c` | C | the two delivery refusals (recursive definition; call under a repeat) — both need the call graph, which is what this file is for (`internal.h:3241`) |
| F9 | `src/gen/emit_dfa.c` | C | `rx_info.name`; `.abi` 12 → 13 (`emit_dfa.c:1375`); `rx_group_entry.ref` populated for injected groups (`emit_dfa.c:1192` emits literal `NULL` today) |
| F10 | `tests/harness/run.sh` | bash | three new block arms (`name`, `description`, `encoding`), `features only`; one `--list-source` call per file with a head; cells; H11's target build |
| F11 | `tests/harness/driver.c` | C | the prefix stops being hard-coded (`driver.c:304`, `352-355` call `rx_*` literally) — H11 |
| F12 | `tests/harness/verify_rxt.py` | python3 | the counted, named skip for a composed block (§1.7, H4) |
| F13 | `docs/spec/*` | md | §4 |

### 1.3 The grammar W1 accepts, and what it refuses

W1 implements exactly the format note's §1.4 W1 row. Restated as the
parser's dispatch, with the diagnostic each arm raises.

**Head (file-level), four productions:**

```
lib <path-ref>
target <ident> = <ident> [with <ident>{, <ident>}]
  description <prose>                    (indented attr)
description <prose>                      (file-level; one-line or `|` block)
config <ident> [from <ident>{, <ident>}]
  pcrec <rest-of-line>
  flags <letters>
  features [only] <module-list>
  encoding <ident>
  engine vm|dfa
  budget steps=N | frames=N
```

**Body (block-scoped), three new arms plus one modifier:**

```
name <ident>
description <prose>
encoding <ident>
features only <module-list>      (`only` is new on an existing arm)
```

**Refusals, by tier (D26).** Every one names the FILE, the LINE and the
CONSTRUCT; none of them reproduces a PCRE2 sentence.

| situation | tier | what the refusal must name |
|---|---|---|
| a W2/W3 keyword in the head (`include`, `use`, `oracle`, `tag`, `freq`, `testee`, `option`, `analysis`) | 3 | the keyword, and that it is **not in this build** — never "unknown", because it IS a real keyword of the format and a reader must not be sent to look for a typo |
| an unknown first token in a context | 3 | the token AND the context ("`testee` is not a pattern-block directive") — format note §1.2's four-contexts rule |
| a head line after the first `pattern` | 3 | the line and the head/body boundary |
| a duplicate `config`/`target`-prefix/definition name in scope | 2 | **both** declaration sites (§2.2's namespace rule; "refused by name, never shadowed") |
| a cycle in `config … from` | 3 | the cycle's members |
| `target … = <name>` where `<name>` is no definition in scope | 2 | the name, and the `lib` chain that was searched |
| `-o <file>` with N > 1 targets | 3 | the targets and the two ways to proceed (§1.5) |
| a `lib` path that does not resolve | 3 | the path and the `--lib-path` list searched |

**DECIDED (1): a W2/W3 keyword is refused as "not in this build", not
as "unknown".** The format note's §1.3 says a parser "may ship W1 alone
and reject W2/W3 keywords with 'not in this build'"; it does not say it
must. It must: the alternative sends a reader hunting a typo in a word
that is in the spec, which is K14's shape (promising a namespace a name
is not in — and here, the mirror: denying a name the namespace does
contain).

### 1.4 The three pattern-level extensions

**MEASURED, `build/pcrec` at main `3372e1e`, three single compiles**
(this is the whole of §1.6's budget, and it is the measurement that
matters most because the format note's own freeness table was taken on
`lane/dd13b` BEFORE [DD-11] landed new parser rows):

```
$ build/pcrec -p rx --features all -o - -- '(?<3>a)'
pcrec: subpattern name expected (a name starts with a letter or '_',
       never a digit) (pattern offset 3)                        rc=1
$ build/pcrec -p rx --features all -o - -- '(?&^.w)'
pcrec: subpattern name expected (a name starts with a letter or '_',
       never a digit) (pattern offset 0)                        rc=1
$ build/pcrec -p rx --features all -o - -- '(?&from=email)'
pcrec: invalid subpattern name (pattern offset 0)               rc=1
```

All three are still refused, so B1/B2/B3 remain free at `3372e1e` and
the format note's constraint ("no legal PCRE2 pattern may change
meaning") still holds after [DD-11]. The refusal SITES are the useful
part: each extension displaces exactly one existing refusal, and the
offsets say which.

| ext | spelling | doorway | displaces | module |
|---|---|---|---|---|
| B1 | `(?<3>…)`, `(?<name=3>…)` | `(?<` | the name-start validator, `mod_named_groups.c:187` region | **`named-groups`** |
| B2 | `(?&^.name)` | `(?&` | the same validator reached through `rc_name_call` (`mod_recursion.c:269`) | **`recursion`** |
| B3 | `(?&site=name)`, `(?&=name)` | `(?&` | "invalid subpattern name" on the `=` | **`recursion`** |

**DECIDED (2): module ownership as tabled.** The format note leaves it
open. B1 belongs to `named-groups` because a group's number and its name
are two halves of one identity and `(?<` is that module's doorway; B2
and B3 belong to `recursion` because `(?&` is its doorway and both are
properties of a CALL. Each gets a `RegRow` (D24) so `--list-syntax`
carries it, per the format note's §3.3 — three DIALECT rows, the shape
`pcre2_compliance.md` already handles.

**A consequence worth stating: `(?&^.name)` and `(?&site=name)` require
module `recursion`, and `(?<3>…)` requires `named-groups`.** A file
using composition therefore needs those modules enabled, which the
harness already does per block via `features`. Nothing new; stated so a
reviewer does not have to derive it.

### 1.5 `config`, `from`, `target`, and how many `.c` files come out

**Scoping and precedence are the format note's §2.6 verbatim; the
implementation notes are these:**

- `config c from a, b` expands to `a`'s lines, then `b`'s, then `c`'s
  own; **the expansion is materialised once at parse, not at each use**,
  so a cycle is caught by a visited set on the same walk that expands
  (one mechanism, not a separate cycle check).
- `with c1, c2` composes into ONE option set. Per-kind composition:
  `features` UNION unless the block wrote `features only`; `flags`,
  `encoding`, `engine`, `budget` more-specific-wins; `pcrec <raw>`
  accumulated, later-wins per flag; size caps **MAX WINS** (r44-sem M15
  — max-wins is order-insensitive and the raise-only law
  `docs/spec/limits.md` states then follows automatically instead of
  being enforced by a refusal).
- **`pcrec <raw>` is re-parsed by the CLI's own option parser, not by a
  second one.** `cli/main.c:203`'s chain is factored into a function
  taking `(argc, argv, pcrec_options*)` and `rxt_source.c` calls it with
  the config line's tokens. One derivation, two readers — otherwise a
  flag would mean one thing on the command line and another in a
  `config` block, which is exactly the drift the situation index warns
  about.

**Output naming** (format note §2.7's table, r44-sem M10, D88):

| invocation | result |
|---|---|
| `--source f.rxt --target <prefix> -o out.c` | that one target → `out.c` + `out.h` |
| `--source f.rxt -o <dir>` with N ≥ 1 targets | `<dir>/<prefix>.c` + `.h` per target |
| `--source f.rxt -o out.c` with N > 1 targets | **refused**, naming the targets and both ways forward |

`-o` today derives the `.h` path by replacing a trailing `.c`
(`main.c:740-786`); the directory form derives both from the prefix.
**D88 holds by construction**: each target is a separate
`pcrec_compile()` call producing its own `.c`/`.h`. There is no
multi-artifact translation unit and no code path that could create one.

**The compatibility default** (Frank §6.4): a file with no `target` and
exactly one **unnamed** block is `target rx = <that block>`. MEASURED by
the format note (r44-sem M11): **two** corpus files have exactly one
block — `tests/mrl/11_motivating_shape_small.rxt` and
`tests/base/d27_nested_min_boundary.rxt` — and would build as `target
rx` under `--source`. Every other file builds nothing. Nothing in
`make test` invokes `--source`, so this changes no existing run.

### 1.6 `rx_info.name`, and the abi's FOUR sites

**CITED, and the format note is stale here: the abi is 12, not 11.**
The note's §2.7 says "currently **11**, MEASURED at
`src/gen/emit_dfa.c:1310`". Three independent sources in the tree say
12:

```
src/gen/emit_dfa.c:1375       sb_puts(c,   "    .abi = 12,\n");
tests/codegen/run_codegen_tests.sh:2707   ABI_EXPECT=12
docs/spec/match_api.md:159    ... `rx_info.abi` is `12` ([OPT-4], the
                              prefilter-language stamp; ...)
```

[OPT-4] bumped 11 → 12 after the note was written. **So W1's bump is 12
→ 13**, and the four D76 sites are, exactly:

| # | site | what changes |
|---|---|---|
| 1 | `src/gen/emit_dfa.c:1375` | `.abi = 12` → `13`, and the `rx_info` struct text at `emit_dfa.c:596-660` gains `const char *name;` |
| 2 | `tests/codegen/run_codegen_tests.sh:2707` | `ABI_EXPECT=12` → `13`, and the `bad` message at :2709 gains the 12→13 clause (that message is the bump ledger) |
| 3 | `docs/spec/match_api.md:159` **and** §6's struct block (~:1340) | the "`rx_info.abi` is `12`" sentence, and the new member with its NULL rule |
| 4 | `tests/codegen/run_recursion_identity.sh:456` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-c275aef}"` → this change's LAST src-touching commit |

**Site 4 carries a rule that has already broken once and is written
where the pin is set** (CITED, `run_recursion_identity.sh:394-406`,
[ART-SIZE]): *"THE PIN MOVES WITH THE LAST SCAFFOLDING CHANGE OF THE
`abi`, NOT THE FIRST — RE-RUN THIS GATE AFTER EVERY src-TOUCHING COMMIT
THAT FOLLOWS A RE-PIN."* A stale pin made (B) report 952 differing
artifacts. W1's target step touches src more than once, so the pin is set
**last**, and §5 puts it in the step's exit criteria rather than in its
middle.

`rx_info.name` is the block's `name`, or the prefix when the block is
unnamed, so **no artifact ever carries a NULL name** (Frank §6.3).
Comparison (A) — the program region against `ac4917d` — is expected
byte-identical, because a stamped string in `rx_info` sits above
`goto <prefix>_L0;`, the same argument [ENG-ABS] made for `match_form`.

**A drive-by the spec hunk must fix** (CITED, `match_api.md:1345-1355`):
the `nnames` comment still reads *"0 until module 'named-groups' lands
(still true as of this writing — verified: `'(?<g>a)'` still refuses)"*.
Module `named-groups` shipped 2026-08-18 (`src/parse/mod_named_groups.c`
exists and populates `Ctx.named_groups`). W1 is editing that struct's
doc for `name` and touching `nnames`'s meaning for composed artifacts
(§2.7), so the stale sentence goes in the same hunk. It is not W1's bug,
but leaving it beside a hunk that contradicts it would be.

### 1.7 What the harness gains, and what it does not

- **H1 is pcrec's, not run.sh's** (§1.1). run.sh calls
  `pcrec --list-source <file>` **once per file, and only for a file whose
  first non-comment line is not `pattern`** — MEASURED, that is **zero**
  of the 179 corpus files (the format note's §1.2 census; independently
  reproduced by r44-grammar G1, and re-confirmed for this note: `grep -rlE
  '^[[:space:]]+[^[:space:]]' tests --include='*.rxt'` prints nothing).
  So the corpus pays no new process.
- **run.sh's 13 existing arms are not touched.** The three new arms
  (`name`, `description`, `encoding`) and `features only` are appended to
  the `if/elif` chain. Order matters in that chain because bash's
  `[[ =~ ]]` clobbers `BASH_REMATCH` (`run.sh:841-843`); the new arms go
  after `features` and before the catch-all.
- **H3 cells**: a block runs once per resolved config. The `perr`
  one-cell rule is a guard at the dispatch, not a filter afterwards —
  MEASURED by the format note, re-running `perr` under a config's
  `--features all` would silently change the meaning of **384** blocks.
- **H11**: `driver.c` calls `rx_*` literally (`driver.c:304`, `352-355`)
  and run.sh passes `-p rx` (`run.sh:441`) — two independent hard-codings
  that must agree. **DECIDED (3): the driver takes the prefix as a `-D`
  macro**, not a generated shim: `-DRXP=<prefix>` plus token pasting
  keeps `driver.c` one file that compiles for any prefix, where a
  generated shim adds a code generator to the harness whose output nobody
  reviews. The default stays `rx`, so every existing invocation is
  unchanged.
- **H4** (`verify_rxt.py`): python `re` has **no** subroutine call at all
  (CITED, `subroutines_design.md` §10.1: "not different semantics, an
  ABSENCE"), so a composed block cannot be python-verified. **DECIDED
  (4): the skip is STRUCTURAL and COUNTED, never a caught `re.error`.**
  `verify_rxt.py` skips a block when the file declares a `lib` or a
  `name` AND the block's pattern carries a by-name subroutine reference,
  reports it in the existing per-file skip line (`verify_rxt.py:388`),
  and its skip counter (`:221`) rises. Catching `re.error` instead would
  make a skip that nobody counted — AR-3's failure mode exactly, and the
  one H4 was flagged for.
  In W1 there is no `oracle` line (it is W3), so this structural test is
  the ONLY thing that can route a composed block away from python.
- **NOT built in W1**: H5 (`include`), H6 (`@file:` and the driver
  protocol change), H7 (`mc`), H8 (`tag`), H9 (data blocks), H10
  (`use`/`variant`/testees). D77 at wave granularity.

---

## 2. The composer

This is the design's centre. Everything above is grammar; this is the
part that changes what pcrec compiles.

### 2.1 Where it runs

**CITED, `src/core/compile.c`'s `compile_driver`** — the ordered stages
of one compile attempt:

```
compile.c:840  pcrec_parse_mods_init(&cx)
compile.c:874  root = pcrec_parse(&cx)          <- returns a resolved tree
        ...    << THE COMPOSER RUNS HERE >>
compile.c:890  root = pcrec_altcls(&cx, root)
compile.c:906  root = pcrec_discharge_atomic(&cx, root)
compile.c:925  pcrec_callgraph_build(&cx, root)
compile.c:952  pcrec_select_engine(&cx, root)
compile.c:963  pcrec_postresolve(&cx, root)
compile.c:1128 pcrec_emit_vm / pcrec_emit_dfa
```

**After `pcrec_parse`, before `pcrec_altcls`.** Both bounds are forced,
not chosen:

- **After parse**, because the composer needs the caller's `ncap`
  (the re-basing base), its `named_groups` (lexical-scope-wins) and its
  resolved `pending_refs` (which by-name calls did NOT resolve locally,
  i.e. which are FILE references).
- **Before `callgraph_build`**, absolutely: that pass is the only writer
  of `A_CALL.u.call.body`, it is driven from `u.call.target` over the
  FINAL tree, and `callgraph.c`'s header comment (`callgraph.c:20-57`)
  records why — a `.body` captured earlier names a subtree `altcls` has
  since rebuilt, which is "TWO DIFFERENT PROGRAMS FOR ONE GROUP".
- **Before `altcls`** rather than after, so an injected definition gets
  the same optimization every other subtree gets. Putting it after would
  make a called body's emitted code differ from an inline one's for no
  semantic reason — option (c) in `callgraph.c`'s own list of three, and
  rejected there for the same reason.

**ARGUED, and it is the one ordering risk:** the composer runs before
`altcls`, and `altcls` rebuilds `A_CAP` nodes (`*r = *a; r->l = body;`).
That is safe here precisely because the composer's output is expressed in
`u.cap.no` and `u.call.target` — **numbers, which `altcls` copies** —
and not in pointers. If a future version of the composer wanted to hold
an `Ast*` to a definition, it would inherit `callgraph.c`'s staleness
problem. §2.4 keeps it to numbers for exactly this reason.

### 2.2 The sub-parse: one `Ctx`, one arena, a saved scope

A definition lives in a different `pattern` line — a different STRING —
from its caller. To bind it, pcrec must parse that string. The two
candidate mechanisms:

- **(a) A second `Ctx` with its own arena, then deep-copy the nodes into
  the caller's arena.** Needs a node-clone pass covering every `AKind`
  and every payload in the D70 union — including `u.bref.refs` and
  `u.call.save`, which are arena `const int *`. A clone pass is a second
  place that must know the whole node vocabulary, and it goes stale
  silently when a kind is added.
- **(b) A SUB-PARSE on the SAME `Ctx`**: save the cursor and the
  numbering scope, point `cx->pat`/`patlen`/`pos` at the definition's
  text, call `pcrec_parse_info`, restore. One arena, one error channel,
  one `mods` seed.

**(b), and the tree makes it cheap.** `Arena arena` is a member of `Ctx`
(`internal.h:1553`), and `pat`/`patlen`/`pos` are plain fields
(`internal.h:1554-1556`) that `compile.c:576-577` and `compile.c:1410-1411`
simply assign. There is already a precedent for building a `Ctx` and
calling a parser entry directly outside `compile_driver`: the
`--explain`/`--probe-ask` surfaces do it (`pcrec_parse_mods_init`'s own
comment, `parse.c` — *"`--explain`/`--probe-ask` build a bare Ctx and
call a doorway directly"*), and `pcrec_parse_mods_init` is documented as
IDEMPOTENT for that reason.

**The scope that must be saved and restored — and each entry is
load-bearing, not defensive:**

| field | why it must be swapped |
|---|---|
| `pat`, `patlen`, `pos` | the definition's own text is what is being parsed |
| `ncap` | **the definition's groups must be numbered from 1 in its OWN space.** `ncap` is read DURING the parse — `internal.h:1603` records PCRE2's rule that `\12` is a backreference iff the RUNNING count ≥ 12, else octal. Parsing a definition with the caller's `ncap` already advanced would decide that rule differently and change what the definition MEANS. This is D87 rule 7(i)'s "preserving local order and gaps" enforced at the only place it can be. |
| `named_groups`, `n_named_groups` | the definition's `(?&w)` must bind to the DEFINITION's `w` (D87 rule 2, lexical scope wins). Resolution is a walk of this list (`mod_backrefs.c:681-691`, first declaration wins), so the caller's list must not be visible |
| `pending_refs`, `n_pending_refs` | `pcrec_parse_info` ends by calling `pcrec_bref_resolve` on the WHOLE list (`parse.c:1321`). Without swapping, a sub-parse would try to resolve the caller's not-yet-complete references against the definition's `ncap` |
| `mods` | the caller's `(?i)`/`(?J)` must not reach into the definition. `pcrec_parse_mods_init` re-seeds from `cx->opt`, which is the file's config — the right seed |
| `first_cap_pos`, `first_vmonly_pos` | these are diagnostic offsets into `cx->pat`; leaving a definition's offset behind would make a later `engine_why` stamp point into the wrong string |

**A `RxtParseScope` struct holds exactly these, and one function saves
and one restores.** ARGUED: the list is long enough that a reviewer
should ask what happens when `Ctx` gains a field that belongs on it.
The answer is a check, not vigilance — §3.4's S-W6 plants a forgotten
swap and names the check that must catch it.

### 2.3 Which references are FILE references

**CITED, format note §2.3.2, steps 1-4, and the tree agrees with the
step order.** After `pcrec_parse` returns, `pcrec_bref_resolve` has
already run and has either bound every by-name call or failed. So the
composer cannot simply read a list of unresolved names — by then the
compile has been refused with *"refers to a capture group named 'X',
which this pattern does not declare"* (`mod_backrefs.c:707-725`).

**DECIDED (5): under `--source`, `pcrec_bref_resolve` DEFERS an
unresolved by-name reference instead of failing, and the composer
resolves it or re-raises the original refusal.** Two candidate shapes
were weighed:

- run the composer BEFORE `pcrec_bref_resolve`, i.e. inside
  `pcrec_parse_info`. Rejected: `pcrec_parse_info` is the one parse
  entry point and is shared by `--count-groups`, `--explain` and the
  built-status probe (its own comment says so, `parse.c:1315-1320`);
  making it composition-aware puts a file-level concern inside the
  parser.
- defer. A single flag on `Ctx` (set only when `--source` supplied a
  definition set) makes `pcrec_bref_resolve` leave an unresolved
  **by-name** reference pending instead of calling `ctx_fail`. Numeric
  refs are unaffected: a numeric reference out of range is still a local
  error, because a number cannot be a file reference.

**This preserves the refusal for the corpus exactly.** MEASURED by the
format note (§2.4): four blocks reference an undeclared name, all in
`tests/recursion/d27/sr_refusals.rxt`, all `perr`, in a file with no
`name` and no `lib`. With no definition set the flag is off, the deferral
never engages, and those four refuse today's refusal at today's offset.

Steps 2-4 are the format note's unchanged: resolve against the file's own
`name`d blocks then its `lib`s in declaration order, transitively; a
visited-set fixpoint with dedup (cycles ALLOWED — self- and mutual
recursion compile and match on both oracles, r44-sem M8); and **a
block's own `name` joins the names its pattern declares**, so a block
named `x` calling `(?&x)` is calling itself and is not a request to
inject a copy of itself.

**DECIDED (6): the closure's ORDER is depth-first, in first-reference
order, dedup on first visit — and it is REPORTED, not re-derived.** The
format note requires the harness's control to derive its offset "from the
closure the composer reports, never re-derive it" (§2.3.4). Under §2.6
the offset is zero, but the ORDER still has to agree for the numbers to
line up, so the composer reports the ordered closure (via
`--list-source` and in `--emit-composed`'s own output) and the control
consumes it. A closure-SIZE or closure-ORDER mismatch is a failure in
its own right, never a silently-passing comparison.

### 2.4 Injection: the shape already in the tree

**A bound definition is injected as:**

```
A_REP{rmin=0, rmax=0, greedy}( A_CAP{no = base} ( <the definition's body> ) )
```

concatenated onto the caller's root, in closure order.

**This is not a new shape. It is what `(?(DEFINE)…)` already desugars
to** — CITED, `mod_recursion.c:418-476` (`pcrec_rcport_define`) and its
header at `:356-417`, quoting D71 item 4: *"the `{0}` layout rule the
R34 verifier forced already IS DEFINE's semantics"*. The port builds no
special node; it produces the same `A_REP{0,0}` that `(?:BODY){0}`
produces, *"so no downstream pass (`callgraph.c`, `vm_count_slots`,
`emit_vm.c`) needed a new line for it."*

**Why an `A_CAP` wrapper is REQUIRED and not a choice.** CITED,
`callgraph.c:162` and `:178`: the bind walks the final tree and matches
*"the `A_CAP` whose `u.cap.no` matches"* the call's `u.call.target`.
`A_CALL.target` is an `int` group number — it is the durable fact, and
`.body` is a cache the binder recomputes (`callgraph.c:22`). So **a
callable body must be an `A_CAP` with a number.** There is no other key.

The alternative — the composer sets `u.call.body` directly and
`callgraph.c` learns to accept a pre-bound edge — is rejected on
`callgraph.c`'s own recorded reasoning: a pointer captured before
`altcls`/`discharge_atomic` names a subtree that is no longer in the
tree, which is `callgraph.c`'s founding bug (commit 513de65, detector
S144).

**So what W1 reuses, in full, and adds nothing beside:**

| mechanism | where | what the composer does with it |
|---|---|---|
| `(?(DEFINE)…)`'s AST shape | `mod_recursion.c:418` | builds the same `A_REP{0,0}` wrapper |
| `A_CAP.u.cap.no` | `internal.h:553`, `parse.c:839-864` | assigns the re-based number |
| call binding by number | `callgraph.c:162,178` | unchanged; the injected `A_CAP` is found the ordinary way |
| linkage / splice choice | `callgraph.c`'s `cg_eligibility` | unchanged. **The format pins the answer; the compiler chooses the linkage** (format note §2.3.5) |
| `NamedGroup` list | `internal.h:1479`, `mod_named_groups.c:219` | the definition's names join it, scope-qualified (§2.7) |
| `rx_group_entry.ref` | `emit_dfa.c:596-660`, emitted `NULL` at `:1192` | the scope path (§2.7) |
| the caps slot layout | D61; `emit_dfa.c:392-395` | delivered slots land above `ngroups` by arithmetic, not by a new region |
| deferred offset-bearing refusals | `src/opt/postresolve.c`, `internal.h:3238` | the two delivery refusals (§2.8) |

**No parallel mechanism is added.** The memory rule
(`pcrec-general-mechanisms-not-special-cases`) is satisfied not by
assertion but because every alternative that would have created one —
a definition id space beside group numbers, a pre-bound `.body` edge, a
node-clone pass, an AST serializer — was rejected on a reason recorded
in the tree.

### 2.5 Re-basing: one walk, three fields

After the sub-parse returns a definition subtree that is resolved in its
OWN number space (`1..k`), the composer walks it once and adds `base`
to exactly three things:

| field | node kind | note |
|---|---|---|
| `u.cap.no` | `A_CAP` | the group's assigned number |
| `u.bref.refs[i]` | `A_BREF` | the resolved backreference targets; arena `const int *`, and this subtree's own — a definition is bound ONCE (dedup), so nothing else points at it |
| `u.call.target` | `A_CALL` | except `target == 0`, which is `(?R)`/`(?0)` — the ROOT, and it must NOT be re-based |

**The `target == 0` carve-out is the walk's one special case and it is
real:** `callgraph.c:162` says the region list *"may begin with 0"* and
that 0 is the root. A definition's `(?R)` means "this whole pattern",
which after injection means the CALLER's root — which is almost
certainly not what a library author meant. **This note refuses `(?R)`
and `(?0)` inside a bound definition**, naming the construct and the
definition's `file:line`, because both possible readings (the caller's
root, the definition's own body) are defensible and the format may not
pick one silently. That is the piece rule's shape — a construct whose
meaning depends on the site — and it is a SIXTH member of §6.0's class
that the format note does not list. It goes to the manager (§6).

**Relative forms need no re-basing.** CITED, D87 rule 7(g) and r44-sem's
R0-R6: `(?-1)` and `\g{-1}` mean textual position, and relocation
preserves the body's internal order.

**MEASURED by the format note, and the arithmetic this design produces
matches it.** M1's cell: library `dd` = `(\d)\1`, caller
`^(\d)-(?&dd)$` whose `ngroups` is 1. Base for `dd` is 2 (the wrapper);
`dd`'s own group 1 re-bases to 3; `\1` becomes `\3`. The composed
pattern matches `5-77` and rejects `5-75` — the library's own meaning,
restored. That is exactly the note's re-based row, and §2.6 explains why
the number is 3 here and 2 in the note's own recommendation.

### 2.6 The wrapper takes a number — and the control's offset becomes ZERO

**This reverses a RECOMMENDED choice in the format note's §2.3.3, and it
is the most important thing in this note for a reviewer to check.**

The format note says: *"the composer assigns a definition's own groups
the base `ngroups+1` and gives the definition itself no slot — so under
the composer `dd`'s group 1 becomes 2, not 3"*, and §2.3.4 then builds a
DERIVED OFFSET into the oracle control: *"a definition's group `k` is the
composer's `ngroups + k` and the control's `ngroups + k + j`, where `j`
is the number of definitions preceding it."*

**That cannot be implemented without a parallel mechanism.** The
argument, in one line: `A_CALL.target` is a group number and
`callgraph.c` binds by matching `A_CAP.u.cap.no`, so a callable body
must hold a number in the same space every other group is in. Giving
definitions a separate id space means a second key, a second lookup in
`callgraph.c`, and a second thing `--emit-composed` must spell.

**So the wrapper takes the number `base`, and the definition's own
groups take `base+1 .. base+k`.** The format note's own reason for
denying the wrapper a number survives intact — *"§2.13's struct has no
member for the definition itself"* — because that is a statement about
the STRUCT VIEW, and the struct view is a view (D87 rule 6's own
framing: "only the STRUCT VIEW merges"). A number is not a member. The
wrapper gets a number, no struct member, and a `rx_group_entry` row whose
`.ref` names its scope.

**And this makes the control strictly better, which is the part worth
arguing rather than merely reporting.** PCRE2's own left-to-right
numbering of the textual append form spends exactly one number per
definition on the `(?<name>…)` wrapper it requires. Under this design so
does the composer. Therefore:

| | caller `(\d)` | wrapper `dd` | `dd`'s `(\d)` |
|---|---|---|---|
| textual control `…(?(DEFINE)(?<dd>(\d)\3))` | 1 | 2 | 3 |
| the composer | 1 | 2 | 3 |

**The offset is zero and the control compares slot for slot.** The
format note's §2.3.4 identifies the derived offset as *"exactly the shape
learnings §3 warns about — a control that 'obviously' compares equal,
then quietly stops comparing the thing it names"*. This design deletes
the offset rather than deriving it carefully, which is the better answer
to the same hazard. What survives from §2.3.4 is the requirement that the
composer REPORT its closure (order and size) and that a mismatch there be
its own failure (§2.3, decision 6) — the control still must not
re-derive the closure from its own text.

**What a reviewer should attack:** whether `ngroups` then means what
§2.7 says. It does — see below — but the two numbers now differ in a way
the format note's arithmetic hid, and §4's S9b hunk is where a caller is
told.

### 2.7 `ngroups`, `nnames`, `RX_NCAPS`, and one derivation

**CITED, D61 and format note §2.7:** `rx_info.ngroups` and
`rx_info.nnames` stay the PRIMARY's own on a composed artifact; the
composition's delivered slots sit above.

**The implementation is a distinction between two counters that today
are one.** `cx->ncap` is both "the primary's own group count" and "the
highest assigned number", because until now nothing assigned a number
out of order. After composition they differ:

```
cx->ncap_primary   the caller's own count, frozen when the sub-parse
                   scope is first pushed          -> rx_info.ngroups
cx->ncap           the highest assigned number after composition
                                                  -> RX_NCAPS - 1
```

`dfa_artifact_ncaps()` (`emit_dfa.c:392-395`) already reads
`cx->ncap + 1`; it keeps doing exactly that and needs no change. The
emitted `.ngroups` (`emit_dfa.c:1492`) changes from `cx->ncap` to
`cx->ncap_primary`. On every non-composed compile the two are equal by
construction, so **every artifact pcrec emits today is byte-identical**,
which is what makes the identity gate's (A) comparison a real check of
this change rather than a formality.

**`nnames` and the name table.** `NamedGroup` gains one field:

```c
const char *scope;   /* NULL for the primary's own groups; else the
                        scope path this name was injected under */
```

- `nnames` counts entries with `scope == NULL` — the primary's own,
  per D61.
- Every entry, injected or not, is emitted into the `rx_group_entry`
  array. The injected ones fill `.ref` — **the column that already
  exists for exactly this** (CITED, `emit_dfa.c:596-660`:
  `const char *ref; /* NULL/empty for the primary's own groups */`,
  emitted as literal `NULL` at `emit_dfa.c:1192` today). D61's "labeled
  insertion path" reserved it; W1 is its first producer.
- The sort key is unchanged: `(name, number)` (`ng_cmp_name`,
  `emit_dfa.c:1136`), which the [M6.5-DUPNAMES] structural check reads
  off the artifact. Injected rows sort in among the primary's by name;
  they are distinguished by `.ref`, not by position, so that check is
  unaffected.

**Name qualification (D87 rule 2) is the `scope` field doing its second
job.** A caller's `(?&w)` must not bind to an injected `w`. Two things
make that true and they are independent:

1. By the time a definition is injected, its own internal `(?&w)` is
   ALREADY resolved to a number — the sub-parse resolved it against the
   definition's own `named_groups` (§2.2). Nothing later can re-bind it.
2. The caller's own by-name resolution walks `cx->named_groups`, and the
   composer writes injected entries with a non-NULL `scope`.
   `pcrec_bref_resolve`'s walk skips them (a one-line predicate at
   `mod_backrefs.c:681-691`), so a caller's `(?&w)` can never see one.
   A caller reaches an injected group only through B2's explicit path,
   which is the whole point of B2.

**MEASURED by the format note (M2), and this design reproduces the fixed
row:** library `outer` = `(?&w)`, `w` = `[a-z]+`; caller
`(?J)^(?<w>Q)(?&outer)$` matches `Qabc` and rejects `QQ` — the library's
own `w`, and `(?J)` becomes irrelevant because there is no duplicate to
make legal.

**One derivation, three readers** (D87 rule 5's last clause, and
learnings §3): the ASSIGNMENT TABLE — an ordered list of
`(number, scope, name-or-NULL, provenance)` built by the composer — is
the single source for `RX_NCAPS`, for the `rx_group_entry` array, and
for `--emit-composed`. None of the three re-derives it. §3.3 is the check
that they agree.

### 2.8 Delivery, and the two refusals

**W1 delivers SLOTS and scope paths. It emits no struct** — that is
[V-I]'s row (plan.md:737), and §0.3 says so.

A delivering call `(?&from=email)` (B3) marks its call site. What the
composer does with the mark:

- the definition's injected groups get `scope = "from"` (or the
  definition's own name for `(?&=email)`), which is the member path
  §2.13 promises and the `.ref` column carries;
- their numbers are already above `ngroups` by §2.5's arithmetic, so
  D61's append-only promise holds by construction rather than by a check;
- **an undeclared call changes nothing.** It stays capture-transparent
  at zero cost (D87 rule 5), which is PCRE2's default and pcrec's, so a
  file that declares no delivery emits exactly what it emits today.

**Two shapes are refused** (CITED, D87 rule 5; format note §2.13):

| shape | why | where the refusal lives |
|---|---|---|
| a delivering declaration on a **recursive** definition (self- or mutual) | the nesting depth is a runtime fact; the member type would be infinite | `src/opt/postresolve.c` — it needs the CALL GRAPH's cycle information, and `internal.h:3241` describes that file as the home for *"every rule that (a) must refuse a pattern AT A PATTERN OFFSET and (b) cannot be decided until the call graph exists"* |
| a delivering call **under a repeat** | one member, many activations; which one is delivered has no answer the format may pick | same file — a walk carrying a repeat-depth counter, run in postresolve's existing **ascending pattern offset** order (`internal.h:3256`) so the leftmost site is named |

**Neither needs a new pass.** That is the point of putting them there:
postresolve exists, it already walks in offset order, and it already has
the graph.

**Iterated capture is out of this row** (D87 rule 5). The refusals are
the honest answer while no mechanism exists, not a policy against one.

### 2.9 Provenance — and why it is NOT a field on the node

**The format note's §2.12 says:** *"provenance is a FIELD ON THE NODE,
carried from its parse"*, and calls the revision-1 span map the wrong
shape.

**CITED, and it contradicts a stated invariant of this compiler.**
`internal.h:3247-3249`: *"a module's parse hook is the only place in this
compiler that holds a pattern offset, and `Ast` carries no position of
any kind (PARSE-1)"*. The same statement is repeated at
`internal.h:734-737`. The established discipline is that a position which
must survive to a later pass is an EXTRA SCALAR ON THE SPECIFIC NODE
THAT NEEDS IT (`A_LOOK.u.look.at`, `internal.h:745`) or a scalar on `Ctx`
(`first_cap_pos`, `first_vmonly_pos`) — never a generic node field.

**A generic `Ast.prov` would be a parallel mechanism** on top of an
invariant the tree states twice, and it would pay for every node in every
compile to serve a feature only `--source` reaches.

**DECIDED: provenance is a property of the SUB-PARSE and of the
ASSIGNMENT TABLE, both of which have to exist anyway.**

1. **A scope stack on `Ctx`.** Each sub-parse pushes
   `(file, line, the pattern text's own base)`. `cx->pos` during a
   sub-parse is ALREADY an offset into the definition's own text — that
   is what swapping `pat`/`patlen`/`pos` means — so a refusal raised
   inside a definition already carries the right offset. What the stack
   adds is the FILE and LINE to report it against.
2. **`ctx_fail` is the one reporting site** (`compile.c:16-29`, writes
   `err->msg`/`pos`/`input` then `longjmp`s), so it is the one place that
   consults the stack. `pcrec_error` (`lib/pcrec.h:611-615`) gains the
   file/line the CLI prints beside the offset it already prints
   (`main.c:774`). One change, one site.
3. **Rule 7(c)'s duplicate-number error names BOTH sites** because the
   assignment table (§2.7) records provenance per assignment. The two
   sites may be in two files, and the table is where that is known —
   not the AST, which by then holds only numbers.

**This is strictly more capable than a node field for the case that
matters** and strictly less machinery: an ordinary compile error inside a
bound definition reports that definition's `file:line` and its own local
offset, which is the obligation §2.12 states, and it does so without any
node carrying anything.

**One thing the node DOES gain, and it is `A_LOOK`'s precedent exactly:**
`u.cap.at`, the pattern offset of a group's opening `(`. It is needed by
`--emit-composed` (§2.10) and by rule 7(c)'s message. `parse.c:839-864`
already has `apos` in hand at the assignment site — it is the value
`first_cap_pos` is set from — so this is a store, not a computation.

### 2.10 `--emit-composed` is a text splice, not a serializer

**CITED, D87 rule 4:** the explicit-number spelling is a SERIALIZATION
pcrec both emits and accepts, and the harness's `A == B` control
recompiles it.

**pcrec has no AST → pattern-text renderer**, and building one is the
obvious reading of "emit the composed pattern". It would have to cover
the entire language — every class, every quantifier, every assertion,
every escape — and it would be a second answer to "what does this AST
mean" for the parser to disagree with. That is learnings §3's drift
hazard, and it is the same reason D87 rule 4 gives for refusing an
external textual renumberer.

**DECIDED: `--emit-composed` splices the ORIGINAL TEXTS, driven by a
position list.** The composed pattern is:

```
<the caller's text, with `?<N>` inserted at each group's own `(` >
(?(DEFINE)
  <each definition's text, same insertion, wrapped `(?<name=N>…)` >
  ... in closure order ...
)
```

Every insertion point is a `u.cap.at` (§2.9) and every inserted number is
an assignment-table entry (§2.7). Nothing is re-derived and no construct
outside `(?<` is ever rendered — the rest of the pattern is the bytes the
author wrote.

**Three properties follow, and they are what make it a control:**

- it **round-trips by construction** under D87 rule 7(j): what it writes
  is a pattern whose groups are all explicitly numbered, and B1 is the
  spelling that reads them back;
- it cannot drift from the parser, because it emits no syntax the parser
  did not just accept from the same bytes;
- **the `A == B` check has teeth**: build A from `--source`, build B by
  feeding `--emit-composed`'s output back through `--source`-less
  `-p`, and compare. Note the two are NOT expected to agree on
  `rx_info.ngroups` — B is handed text and counts every group in it,
  which is exactly the difference §2.3.4 point 3 records and §4's S9b
  states. They must agree on the emitted PROGRAM and on
  `caps[0..ngroups_A]`. A check that compared `ngroups` would be red for
  a correct build, and one that compared nothing would be green for a
  broken one; §3.2 pins which.

---

## 3. The check and sabotage plan

Written against learnings §3 and memory `pcrec-check-design-lessons`:
**a control must not share a source with what it controls; a population
nobody counts is not a population; a witness that stopped reaching its
site is a green check measuring nothing ([MECH-REACH]).** Every check
below names its witness and asserts its denominator.

### 3.1 INV-COMPAT — that no existing file changes meaning

The format note's §1.1 asks for three independent checks. This design
changes what two of them prove, and the change is in the honest
direction, so it is stated plainly rather than claimed as a win.

**C1 — the cross-implementation dump differential.** `pcrec
--list-source --dump` and a new `run.sh --dump` emit the same canonical,
order-preserving serialisation — block index, `file:line`, pattern text,
every directive with its value — over all 179 files, and the two dumps
must be **byte-identical**. This is the control §1.1 asks for AND the
control §1.1's own two-parser situation needs; the two are in different
languages by different authors, which is what makes it a control.
**Denominator asserted: 179 files, 3,265 blocks.** It does NOT cover
expectation lines, which pcrec never parses — those are C2's and C3's.

**C2 — the answer re-run.** run.sh over the corpus reports the same
`cases passed:`, `cases failed:`, `pattern-compile failures (distinct):`
and `group cases pending-vm:` (`run.sh:1032-1044`). These are a
DIFFERENT partition of the 26,691 expectations than C3's — r44-grammar
G2: a `perr` block and a live `g` line each record independently, and
26,691 = passed + failed + pending-vm. Both partitions are asserted.
**This is the check that catches a parse that is faithful but routed
differently**, e.g. a block that starts running an extra cell.

**C3 — the oracle re-run.** `verify_rxt.py` reports the same verified
count and the same skip count. **The skip count is the load-bearing
half**, because H4 adds a new reason to skip (§1.7): if the structural
composed-block test is wrong in the loose direction it will skip blocks
it should verify, and only the skip COUNT catches that. It must be
unchanged at the corpus, since no corpus file declares a `lib` or a
`name`.

**C0 — the closure is empty, everywhere.** The composer reports the size
of the closure it bound, and **for the corpus that number is 0 in all
3,265 blocks**. §1.1's third clause, and the only one of the four that
tests the composer at all on this population.

**Where this design makes the proof CHEAPER, and where that is a
weakness.** run.sh's 13 existing arms are not touched (§1.7), so C1's
value on the corpus is largely "the two parsers agree that nothing
happened". A reviewer should read that as: **C1 is a strong control for
W1's own new files and a weak one for the 179.** What actually protects
the 179 is that the code path they take is unchanged, and the check that
says so is a diff — which is why S-C7 below plants a change that makes
the head detection fire on a corpus file, since that is the only way the
179 can move.

**Sabotage rows.** The format note's S-C1..S-C8 all still apply, and each
still names the check that must catch it. Two are re-homed and one is
new:

| row | plant | must be caught by |
|---|---|---|
| S-C1 | drop the last `g` line of one block | C2 (count), C3 |
| S-C2 | decode `\x41` as `x41` | C3 |
| S-C3 | let `flags` carry to the next block | C1 (run.sh's dump carries the value) |
| S-C4 | treat `# pcre2-only` as an ordinary comment | C3's skip count |
| S-C5 | make `frames-buffer=` block-scoped rather than positional | C2 — run.sh captures `cur_route` at each case push (`run.sh:931,941,…`), so a block-scoped version changes which route a case runs under. **NOT C1**: pcrec never parses `frames-buffer=`, so the dump cannot see it. The format note assigns this row to the dump differential; that is wrong under this design and the re-homing is the finding |
| S-C6 | accept an unknown `features` name silently | C2 — a `perr` block flips |
| S-C7 | make the head detector fire on a file whose first line is `pattern` | C1 and C2 — and this is the row that guards the 179 |
| S-C8 | assign a definition's re-based numbers from 1 instead of `base+1` | C0 is vacuous here (closure 0 everywhere), which IS the finding: this row is caught by §3.2's W-composer checks and by nothing on the corpus. Stated so nobody reads the corpus's green as covering it |

**S-C8 is the honest one and it should stay uncomfortable.** The corpus
cannot test composition, because no corpus file composes. Every
composition check runs on files W1 writes, which means the author of the
mechanism is the author of its population — the exact shape learnings §3
names. §3.2's answer is that the ORACLE is not W1's.

### 3.2 The composer's checks

**W-1 — the textual EXPAND control (H2b), and the population it is valid
on.** CITED, format note §2.3.4: the control is valid where the append
form means what the composer means — **no absolute numeric reference in
any body, and no name collision between caller and closure**. Outside
that population **the control does not run and says so** — a counted,
NAMED skip, never a silent pass.

Three things this design changes about it, all in the control's favour:

1. the offset is **zero** (§2.6), so the comparison is slot for slot and
   there is no arithmetic to get wrong;
2. the closure ORDER and SIZE come from the composer's report, and a
   mismatch is its own failure (§2.3 decision 6);
3. the validity test runs on the composer's resolved closure, not on the
   control's own reading of the text — so the control cannot decide it is
   applicable on a population the composer disagrees about.

**The skip population must be COUNTED and PRINTED, and it must be
non-empty in the suite.** [MECH-REACH]'s lesson: a control whose
inapplicable branch is never exercised has an untested branch. So W1's
own test files must include at least one definition with an absolute
numeric reference (M1's `dd` = `(\d)\1`) and one caller/closure name
collision (M2's `(?J)` case) — both of which are the shapes that FORCED
D87, so they are the right witnesses and they are already written down
with their answers on both oracles.

**W-2 — `A == B` across `--emit-composed`.** §2.10. Compares the emitted
PROGRAM and `caps[0..ngroups_A]`; explicitly does NOT compare
`rx_info.ngroups`, and the check states why in its own message so a
future reader does not "fix" it.

**W-3 — the hand-verified cells.** M1's four rows and M2's four rows
(format note §2.3.3), which were measured on BOTH oracles and are the
evidence D87 was ruled on. They become `.rxt` cases. They are not an
independent oracle — they are pinned answers — and the check must say so
rather than presenting them as verification.

**W-4 — Q7's residual, unchanged and named.** CITED, format note §7.2
Q7 and the manager's ratification: on the two populations D87 added
mechanism for (absolute refs, colliding names) **no independent oracle
checks the answer**. W1 accepts that with the named trigger — *the first
[LIB] entry that legitimately needs an absolute reference or a colliding
name* — and W1's contribution is to make the uncovered population
COUNTABLE: the control prints how many cells it skipped and why, so the
residual has a number instead of a description.

### 3.3 The one-derivation checks

Three surfaces read the assignment table (§2.7) and they can only
disagree if something computes it twice:

| check | asserts |
|---|---|
| W-5 | `RX_NCAPS - 1` equals the highest number in the emitted `rx_group_entry` array, or the table's max where no name exists |
| W-6 | every `rx_group_entry` with non-NULL `.ref` has `number > rx_info.ngroups` — **D61's promise as a structural assertion on the artifact**, not as a claim in a note |
| W-7 | `--emit-composed`'s explicit numbers, re-parsed, reproduce the same table |

W-6 is the one to keep: it is a property of every composed artifact, it
is checkable by grep on emitted text, and it fails loudly in the
direction that matters (a delivered slot intruding on `1..ngroups`).

### 3.4 The composer's sabotage rows

Each must turn a named check red. A row no check catches is a finding
about the check set, not about the row.

| row | plant | must be caught by |
|---|---|---|
| S-W1 | re-base `u.cap.no` but not `u.bref.refs` | W-1 on M1's `dd` cell — the library's meaning inverts, which is the measured M1 defect returning |
| S-W2 | re-base `u.call.target` including `target == 0` | W-3: a definition's `(?R)` silently becomes the caller's root. (Under §2.5's refusal this row instead plants "accept `(?R)` in a definition") |
| S-W3 | drop the `scope` predicate in `pcrec_bref_resolve`'s walk | W-1 on M2's `(?J)` cell — the caller's `w` captures the library's call again |
| S-W4 | give the injected wrapper no number and shift the definition's groups down by one | W-1 (every composed cell's slots move by one) and W-7 |
| S-W5 | count injected names in `nnames` | W-6 and the C1 dump |
| S-W6 | forget to restore one field in `RxtParseScope` — specifically `ncap` | a dedicated check: a file with a definition used at two call sites must produce the SAME numbers as one with a single site, and a two-definition file must not renumber the first when the second is bound. **This is the row with no natural detector**, which is why the check is written for it rather than hoped for |
| S-W7 | make the closure a plain walk with no visited set | a self-recursive definition compiles twice as big / a mutually recursive pair does not terminate; the check asserts the REPORTED closure size, which is why §2.3 decision 6 requires it to be reported |
| S-W8 | let the harness's control re-derive the closure from its own text | the control's closure-size comparison — the check that exists because §2.3.4 says the control must not do this |

### 3.5 The identity gate and the abi

**D76's ritual, at the four sites §1.6 lists, in ONE change.** Two
lanes in one night have missed sites 2 and 3 (CLAUDE.md's situation
index), so:

- `make test-codegen` runs before delivering the target step;
- comparison **(A)** (program region vs the unchanged `ac4917d`) is
  expected **byte-identical** — `rx_info.name` is a stamped string above
  `goto <prefix>_L0;`, the argument [ENG-ABS] made for `match_form`. If
  (A) moves, something changed the program and the step is wrong, not
  the gate;
- comparison **(B)** is re-pinned to the step's **LAST** src-touching
  commit, per the rule written at `run_recursion_identity.sh:394-406`.

---

## 4. The spec deltas (D80)

A parser landing without its spec hunk is rejected on sight. W1's hunks
are the format note's §3.4 rows tagged W1, and they land with the STEP
that makes each observable — not all at the end.

| hunk | file | lands with |
|---|---|---|
| **S1** HEAD and BODY; the four W1 head declarations; the head ends at the first `pattern`; the four lexical contexts; the block scalar as a property of the VALUE production | `docs/spec/rxt_format.md` | W1.1 |
| **S3** the CELL notion, the `perr` one-cell rule, and the summary's new quantities | `docs/spec/rxt_format.md` | W1.1 |
| **S10** `limits.md`'s "Handling an oversized artifact" item 1 stops being a forward reference and points at S1 | `docs/spec/limits.md` | W1.1 |
| **S11** `--source`, `--target <prefix>`, `--lib-path DIR`, `--emit-composed`, `--list-source`, and §1.5's output-naming rule | `docs/spec/cli.md` | W1.2 (`--emit-composed` with W1.3) |
| **S9** `rx_info.name`; the `abi` 12 → 13 sentence; **and the stale `nnames` sentence** (§1.6) | `docs/spec/match_api.md` §6 | W1.2 — one of D76's four sites |
| **S2** a new "Composition" section: the AST-level model, D87 rule 7(a)-(j), lexical-scope-wins with internal qualification, the visited-set closure, the five namespaces, and that a composed block's oracle is necessarily `pcre2` | `docs/spec/rxt_format.md` | W1.3 |
| **S2b** the three pattern-language extensions with the "no legal PCRE2 pattern changes meaning" constraint and §1.4's measurement; the three registry rows | `docs/spec/` + `--list-syntax` | W1.3 |
| **S9b** D61 made concrete by its first producer: `ngroups`/`nnames` are the PRIMARY's own; delivered slots occupy `ngroups+1..`; `RX_NCAPS` may move across library versions while `1..ngroups` holds still; and the difference between `--source` composition and handing composed TEXT to plain `-p` | `docs/spec/match_api.md` §2/§5 | W1.3 |
| **S2c** "Delivered results": the scope path, first-set-wins for duplicate names in one path, the two non-deliverable shapes and their refusals, and the sentence that two call sites of one definition are distinct C types needing `__typeof__` | `docs/spec/rxt_format.md` | W1.4 |

`docs/guide/` points at these and never restates them (D80). W1 adds one
guide page — "compiling from a `.rxt` source" — with no edge cases.

---

## 5. Steps and merge points

Four steps, each with its own acceptance measurement and a merge after
it. The order is forced twice: `target` before the composer (a composed
file has several blocks and therefore builds nothing without a
`target` — so without step .2 the composer has no way to be run at all),
and the abi ritual on the step where `rx_info.name` first has a value a
check can read (M9's complaint about H11, one level down).

### What can be measured BEFORE building (D77)

Already measured, in this note, under the HOLD:

- the three spellings are still free at `3372e1e` (§1.4) — the one
  measurement that could have killed B1/B2/B3;
- the abi is **12**, from three independent sites (§1.6) — the format
  note says 11;
- **0** corpus files have a head, and **0** lines begin with whitespace,
  so §1.2's continuation rule is free and step .1 cannot move the 179;
- **0** of the 32 candidate keywords occur as a first token (format note
  §1.1, r44-grammar G1);
- `rx_group_entry.ref` exists and is emitted `NULL` today
  (`emit_dfa.c:1192`), so §2.7 needs no new column.

Not measurable before building, and named as such: whether the sub-parse
scope list (§2.2) is complete. That is S-W6's row, and it is why the row
gets a purpose-built check instead of a hoped-for detector.

### The steps

**[DD-13b.W1.1] — the head grammar, the source reader, and the corpus
identity proof.**
Builds: F1, F2 (the `Rxt*` types only), F3's `--source`/`--lib-path`/
`--list-source`, F10's three block arms + `features only`, F12's
structural skip. No composer, no targets, no abi change.
Acceptance: C1 byte-identical over 179 files / 3,265 blocks; C2 and C3
unchanged with both denominators asserted; S-C1..S-C7 each turn their
named check red. `make strict` clean.
Merge. **This is the natural first merge** — it is the whole of
R-COMPAT-1's proof and it touches nothing a caller can observe.

**[DD-13b.W1.2] — targets, `rx_info.name`, the abi ritual, H11.**
Builds: `target … [with]`, `config` composition and `from`, the output
naming rule and `-o <dir>`, F9's `rx_info.name`, F11's prefix-taking
driver, run.sh's target build path.
Acceptance: a target file builds N artifacts with N prefixes and one
`rx_info.name`; §6.3's three-config worked file compiles three ways and
the three agree on the block's cases (the format note calls that identity
"a free control" and it is); the abi is 13 at **all four sites**;
identity gate (A) byte-identical, (B) re-pinned to this step's LAST src
commit; `make test-codegen` green.
Merge.

**[DD-13b.W1.3] — the composer, the three extensions, `--emit-composed`.**
Builds: F4, F5, F6, F7, F8's infrastructure, the sub-parse, re-basing,
qualification, injection, the assignment table, provenance, H2b's
control, H2c's round trip.
Acceptance: W-1 through W-7; the M1 and M2 cells reproduce the note's
measured answers; the control's skip population is non-empty and
counted; S-W1..S-W8 each turn a named check red; C0 still reports closure
0 on all 3,265 corpus blocks.
Merge. **This is the step to schedule the panel on**, not W1 as a whole.

**[DD-13b.W1.4] — delivery.**
Builds: B3's semantics end to end — `scope` on injected groups, `.ref`
populated, delivered slots above `ngroups`, and F8's two refusals.
Acceptance: W-6 on every composed artifact; both refusals fire with the
construct named, and each has a witness that REACHES it (a recursive
definition with a delivering declaration; a delivering call under `{2}`);
`§6.1`'s `mail.rxt` worked file builds with `rx_info.name ==
"from_line"`, `ngroups == 0`, and three delivered slots above it.
Merge. [V-I] then has its interface (§2.8) and W1 is closed.

---

## 6. Open questions for the manager

Short, because the brief says to decide what I can. Six decisions are
recorded inline and marked **DECIDED**; four of them are routine
(1: refusal wording tier; 2: module ownership; 3: `-D` prefix over a
generated shim; 4: a structural rather than exception-caught skip) and I
do not need them re-ratified unless the manager disagrees. **Three
things do need a ruling**, and the first two change a number the format
note published.

**Q-W1 — the definition's wrapper takes an assigned number, so the
control's derived OFFSET is zero (§2.6). Format note §2.3.3's
RECOMMENDED says it takes none and §2.3.4 builds an offset `j` on that.**
`A_CALL.target` is a group number and `callgraph.c:162,178` binds by
matching `A_CAP.u.cap.no`, so a callable body must hold a number in the
same space as every other group; a separate id space would be a second
key in the binder. Under my reading this is an implementation fact the
note did not have, it makes the oracle control strictly better (no
arithmetic to get wrong), and it changes `dd`'s composed group 1 from
**2** to **3** — the number §2.3.3 spells out. **Recommendation: adopt,
and amend §2.3.3/§2.3.4 in the format note.** This is arguably a
semantics change (a caller can observe the numbering through
`--emit-composed`), so it may be Frank's rather than the manager's.

**Q-W2 — `(?R)` / `(?0)` inside a bound definition is a SIXTH member of
§6.0's piece-rule class, and I propose to refuse it (§2.5).** A
definition's `(?R)` means "this whole pattern"; after injection the only
two readings are the caller's root and the definition's own body, and
both are defensible. `callgraph.c:162` treats target 0 as the root, so
the re-basing walk must either skip it (the caller's root — silently
changing what a library meant) or rewrite it (the definition's body —
inventing a meaning). §6.0 does not list this shape.
**Recommendation: refuse, naming the construct and the definition's
`file:line`, and add it to §6.0's class as member (vi) with fate
"refused by the store scan" — it is a lexical property of the
definition's own text, so it is checkable exactly where (i) and (iii)
are.** Semantics; for Frank via the manager.

**Q-W3 — the [DD-11] table is W1's LISTING interface, not its BINDING
one, and the format note's §4.2 can be read either way.** D85 says a
library definition is "a row whose predicate is the library's presence",
and the tree already reserves `DEF_LIB_NAME_BOUND` with "NO PRODUCER
YET — [LIB]/[DD-13b]" (`internal.h:2536`) and names `DEFK_TEXTFN` as
what "[DD-13b]'s [LIB] name-bound rows reuse later"
(`internal.h:2564-2577`). But `DefTextFn` is
`Ast *(*)(const char *operand, size_t len, Ctx *cx)` and its contract is
to return the core AST **spliced at the occurrence** — i.e. INLINING.
Composition must produce a CALL: a call restores the callee's capture
state on return and inlining does not (format note §2.3.5's first
difference), and the splice/linkage choice is `cg_eligibility`'s with its
`SLOT_SPLICE_SAVE` machinery. **So W1 adds no `DEF_LIB_NAME_BOUND`
producer.** The composer resolves names itself, and
`--list-definitions`'s "what did `lib` bring into scope" surface (format
note §3.3) reads the composer's resolved set — one derivation, two
readers. **Recommendation: confirm, and let §4.2 say "listing" where it
today says "interface".** Syntax/architecture; the manager's.

**Not asked, recorded as residuals:** Q7's uncovered population stands as
ratified (§3.2 W-4) with its named trigger; the format note's stale
`abi 11` and `emit_dfa.c:1310` (§1.6) and its S-C5 row assignment
(§3.1) are corrections I will make in the same change rather than
questions.
