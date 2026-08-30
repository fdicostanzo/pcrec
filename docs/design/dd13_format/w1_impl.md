# [DD-13b.W1] Implementation note — wave 1 of the grown `.rxt` format

**Status: REVISION 2.2, post-panel (r45), post-BOTH re-checks and post-rulings. NO CODE IS
WRITTEN.** Revision 1 (`bf843a7`) went to a three-critic D6 panel
(`docs/dev/reviews/2026-08-30-r45-w1-impl.md`): **4 blockers, 6 must-fix,
and a verdict that the spine stands and §2 is not buildable as written.**
This revision is the answer. It stops here for a focused re-check before
[DD-13b.W1.1] is chartered.

Against: `format_design.md` (revision 2), D87, D88, D61, D85, D80, D76,
D77, D26, the r44 panel record, r45's findings and the manager's triage,
and the manager's rulings of 2026-08-30 (the parser seam, `--list-source`,
the `have_block` guard, and B4's sort key).

## 0. How to read this

### 0.1 Claim marking

- **MEASURED** — a command was run and its output quoted. Everything here
  was taken under the manager's HOLD: file reads, corpus greps, and
  **five single compiles** of `build/pcrec` in total across both
  revisions. No `make`, no sweep, no battery.
- **CITED** — quoted from a ruling, decision, spec or the tree, with its
  `file:line`.
- **ARGUED** — reasoning from the above; the panel's natural target.
- **DECIDED** — a point the format note left to the implementer, or where
  the tree contradicts it. Each is flagged inline and collected in §6.

### 0.2 The design in one paragraph

pcrec owns the `.rxt` **HEAD** grammar and the whole-file resolution;
run.sh keeps its **BODY** parser and **gains no head arms at all** — for
a head-bearing file it calls `--list-source` once and starts its existing
per-line loop at the `line` column of the first `pattern` row, so the head
is an untouched byte range whose boundary comes from the one head parser
(manager's seam ruling). The composer is a **sub-parse on one `Ctx`**:
save the cursor and the numbering scope, parse a definition in its own
number space, re-base by a walk. A bound definition is injected as
`A_REP{0,0}( A_CAP{no} ( body ) )` — the shape `(?(DEFINE)…)` already
desugars to — so `callgraph.c`'s number-to-`A_CAP` bind is reused
unchanged and **no new AST shape or node kind is added**. Provenance is a
property of the sub-parse and of the assignment table, never a field on
`Ast` (which `internal.h:3247` forbids). **Four things revision 1 got
wrong and this revision names as mechanisms**: a delivering call must
*defeat* two capture-transparency mechanisms rather than ride them (§2.8);
the re-basing walk must not touch caller-scope references (§2.5);
`--emit-composed` must render injected by-name references *numerically*
or it re-creates the collision D87 exists to fix (§2.10); and `nnames`
cannot mean "the primary's" while `groups[]` holds every row without
breaking a shipped bsearch contract (§2.7).

### 0.3 What this note does not design

- **The struct TYPE** — [V-I]'s (plan.md:737). W1 delivers slots, scope
  paths and refusals; it emits no struct.
- **W2/W3 productions** — refused by name as "not in this build" (§1.3).
- **Diagnostic wording** — D26.
- **[LIB]'s store scan** — §6.0's two mechanical refusals are [LIB]'s.

### 0.4 Revision record — r45 finding by finding

The panel's own numbering; the manager's dispositions are in the review's
triage table. Where a finding changed a MECHANISM rather than a sentence,
the section is named.

| finding | landed |
|---|---|
| **sem B1** delivery is refuted by two measured mechanisms | **§2.8 rewritten.** Delivery is now a NAMED deviation from capture-transparency: a live-capture arm for a delivering call, and the callee's capture indices excluded from `W`. §2.4's reuse table says both are touched |
| **sem B2** the walk corrupts caller-scope refs | **§2.5**: the walk is keyed on the `PendingRef`, and caller-scope refs are resolved AFTER it; §2.3 classifies B2 explicitly |
| **sem B3** `--emit-composed` re-introduces by-name binding | **§2.10**: injected by-name references render NUMERICALLY; S4's unrenderable spellings are a counted, named skip |
| **sem B4** `nnames` vs `groups[]` breaks the bsearch contract | **§2.7**, on the manager's ruling: sort key `(ref-is-NULL, name, number)` so the primary's rows are a genuine PREFIX; `nnames` stays the primary's; NEW `nentries` rides abi 13; §4 gains the §6 algorithm hunk |
| **sem M1** restoring `first_cap_pos` is wrong | §2.2: a THIRD state from the scope stack, never "restore" |
| **sem M2** the `mods` seed imposes the caller's flags | §2.2: seed from the DEFINITION block's own resolved `flags` |
| **sem M3** one of three walkers named, and the wrong pass | §2.7: all three enumerated; the composer's re-resolution owns the rule |
| **sem M4** `target == 0` cannot tell root from unresolved | §2.5: the carve-out is DELETED; the walk keys on the `PendingRef` |
| **sem M5 / S1** the repeat walk refuses every delivering call | §2.8: the bound is a CALL-GRAPH property (activation ≤ 1 on every path), not lexical repeat depth |
| **sem S2** the deferral loses leftmost-failure ordering | §2.3: ordered by (file, line, offset) from the scope stack |
| **sem S3** "a block's own `name` joins the names its pattern declares" is unimplementable | §2.3, **DECIDED (7)**: the block's `name` is in the FILE namespace, not the pattern's |
| **sem S4/S5/S6** the splice's insertion, modifier leakage, the round-trip claim | §2.10: `(?<name=N>` is a REPLACEMENT needing the header extent; an explicit modifier reset per spliced wrapper; the claim restated in its weaker true form |
| **chk F1** C0 is empty-vs-empty and its row was deleted | **§3.1**: format_design's S-C7 restored as its own row; C0 redesigned so its number comes from an invocation that happens |
| **chk F2** C1 is a differential on the half it does not need | §3.1: C1 is THREE-WAY — `verify_rxt.py --dump` joins it |
| **chk F3** nothing sees the dump's coverage shrink | §3.1: a per-block field MANIFEST + S-C11 |
| **chk F4** the one-derivation checks cannot fail | §3.3 re-scoped; W-8 added, its expectation from libpcre2 |
| **chk F5** the control's APPLICABLE population has no floor | §3.2: an N-run / M-skipped manifest, both pinned, both plant-validated |
| **chk F6** `nnames` is asserted by nothing | §3.3 W-6b; S-W5 re-homed |
| **chk F7** S-W2's population is empty | §3.4: a `(?R)` witness with `SAB_REACH_EXPECT`, four spellings |
| **chk F8** the FILEPIN rule is per-ABI, not per-step | §3.5 and §5: the gate re-runs and the pin moves at EVERY merge of the abi-13 change |
| **chk F9** the gate is blind to `rx_info.name`'s VALUE | §3.5: a structural assertion over the corpus's artifacts |
| **chk F10** S-W8 plants independence and expects a red | §2.3 **DECIDED (8)**, rewriting revision 1's rule on the manager's ruling: the control RE-DERIVES; S-W8 becomes "make the composer's report disagree with the text" |
| **chk F11** `ncap`'s octal reason is untested | §3.2 W-1c: the `\12` cell, answer from libpcre2 |
| **chk F12** "by construction" has no check | §3.1: run.sh's arm block is hash-pinned; the 32-keyword census becomes a CHECK |
| **chk F13** mechanical gaps vs `tests/mech/sabotages/CLAUDE.md` | §3.4: `SAB_REACH*` on every row, the `SAB_SUITES` arm registered first, rows land with their code, `verify_rxt` gains a TOTAL |
| **chk F14 / gram 3 / gram 4** citations | fixed: `compile.c:882`, `mod_backrefs.c:733-734`, `emit_dfa.c:1190-1191` |
| **gram 1 / gram 2** the seam and `--list-source`'s contract | RESOLVED by the manager's rulings; §1.1 rewritten, new §1.8 |
| **gram 5 / gram 9** `with c1,c2`; the step-order reason | one sentence each (§1.5, §5) |

**Revision 2.1** folds in the r45chk RE-CHECK's four items (F1-F13 all
closed; go/no-go = charter .1 and .2, with N1 as the condition):

| item | landed |
|---|---|
| **N1** (MUST-FIX, the condition on .1) — C3 and C1's leg C are specified against a script `make test` does not run, whose discovery is a one-level glob | **§3.1.1**, new. Measured: the only Makefile mention is a COMMENT; the naive wiring `verify_rxt.py tests` covers **0** files; today's default covers **40 of 179 / 3,603 of 26,691 (13.5%)**; and S-C4's population is **7.7%** reached at that scope. W1.1 must wire it with a short-list hard fail and pin its totals |
| **N2** (SHOULD) — C1 asserts 179 where run.sh's no-arg branch yields 178 | §3.1: leg B is invoked through run.sh's `$@` branch (`:187-195`, no exclusion), with the manifest's total-line assertion as the backstop |
| **N3** (SHOULD) — the arm-block hash pin sits inside the range W1.1 edits | §3.1: BEGIN/END marker comments delimit the protected region, the check hashes between them, and the update rule lives in the failure message |
| **N4** (NOTE) — C0a conflated two kinds of fact | §3.1: W1's own invocation counter and the independent head-bearing-file census are named separately, with why neither alone suffices |

**Revision 2.2** folds in the r45sem RE-CHECK (B2/B3/B4 and M1-M5, S1-S6
all CLOSED; B1's DIAGNOSIS closed but its REMEDY refuted):

| item | landed |
|---|---|
| **sem N1** (the remedy) — `W` is a per-REGION property while "delivering" is per CALL SITE, so excluding capture indices from `W` would exclude them for every other site of the same definition | **§2.8 rewritten again.** RULED (manager, architecture): **a delivering call is FORCED to `CALL_SPLICE`**, because `vm_splice` allocates `base = v->nsplice` FRESH PER SITE — so the exclusion is per-site by construction. §2.4's table gains a FOURTH changed row (`cg_eligibility` gains one input). The two refusals turn out to be the forcing's precondition |
| **sem N2** — the restore is index-coupled | §2.8: the restore runs over the CALLEE REGION's own index space (`vm_region`, `emit_vm.c:6036-6046`); `vm_publish_saves`'s *"three readers, one write"* named; `vm_splice`'s overflow `ctx_fail` (`:5924-5932`) cited as the loud detector; and the trail-coherence argument — `vm_set` is trailed, so a dropped restore keeps the callee's value and is undone on backtrack |
| **sem N3** — where the delivering bit lives | §2.4: ON the `A_CALL` node (a bare `const Ast *` walker cannot reach a memo), written EXPLICITLY on every call, because the arena zero is the unsound direction — `link`'s own situation and `link`'s own answer (`callgraph.c:246`, `:337`) |
| **sem N4** — the sub-parse's pending list | §2.5: the list is CAPTURED into the scope record, not overwritten by the restore; the re-basing is TWO passes (a tree walk for `A_CAP`, a pass over the captured list) rather than one |
| **sem N5** — the region start vs the first delivered group | §4's S9b: the region starts at `ngroups+1` with the wrapper there; the first delivered GROUP is at `ngroups+2`. Revision 2.1 said the second and implied the first |
| **sem N6** — `match_api.md:1504` becomes reachable-false | §4's S9c, and noted as the SECOND instance of §1.6's staleness shape in one struct's docs |

**What the panel could NOT refute, and is not re-argued below:** the
sub-parse on one `Ctx`; injection as `A_REP{0,0}(A_CAP)`; re-basing by a
walk; provenance on the scope stack (r45sem: "the best section; its
PARSE-1 argument against format_design §2.12 should be adopted"); the
abi's four sites (all verified, and format_design's "11 at :1310"
confirmed stale on both value and line); §1.3's grammar as a complete
restatement of format_design §1.4's W1 row; and the "what can be measured
before building" discipline (r45chk: "the best D77 discipline in a lane
note this round").

---

## 1. What lands where

### 1.1 The seam: who parses the `.rxt` file — RULED

**CITED, the tree.** Two `.rxt` parsers exist today, both the harness's:
`tests/harness/run.sh` (bash, 1051 lines; an `if/elif` chain of 13
`[[ =~ ]]` arms at `:811-1021`, catch-all hard error at `:1016-1021`) and
`tests/harness/verify_rxt.py` (python3, 418 lines; `parse_rxt` at
`:113-182`, 10 kinds, the only place `# pcre2-only` means anything, at
`:121`).

**W1 adds a third, in pcrec**, because `--source` must resolve
`lib`/`name`/`target`/`config` before it can compile anything. The head
grammar therefore has ONE implementation. r45gram's blocker was that
revision 1 never said how run.sh's per-line loop gets PAST head lines
without hitting its unmodified catch-all. **The manager ruled it, and the
ruling is the reason this section is now short:**

> For a file whose first non-comment line is not `pattern`, run.sh calls
> `--list-source` ONCE, reads the `line` column of the FIRST `pattern`
> row, and starts its existing per-line loop AT that line. The head is an
> **untouched byte range** whose boundary comes from the one head parser.
> run.sh gains **no head arms** and no head recogniser, shallow or
> otherwise.

So the two readings r45gram named — (a) pre-scan, (b) ignore-arms — are
resolved as neither: run.sh does not scan for the boundary and does not
recognise head syntax; it is TOLD the boundary. That kills the drift
hazard (b) would have created, and it makes the `line` column
load-bearing, which is why it has its own sabotage row (§3.4 S-C10).

**MEASURED — the 179 files never make the call**, so their code path is
byte-identical: every corpus file's first non-comment line is `pattern`
(format_design §1.2's census; r44-grammar G1; re-confirmed here at §1.7).

**What still has two implementations, deliberately: the BODY grammar** —
run.sh's and pcrec's (which must read `pattern`/`name`/`description`/
`flags`/`features`/`encoding`/`engine`/`budget` to find definitions and
targets, and ignores every expectation line). That is a control, and
r45chk's F2 is the correction revision 1 needed: it is a control for the
BODY and **not for the HEAD**, where W1 has exactly one parser. §3.1's C1
is now three-way and says which half each leg covers.

### 1.2 File by file

| # | file | lang | change |
|---|---|---|---|
| F1 | `src/parse/rxt_source.c` (**new**) | C | the HEAD grammar + the body's directive lines; four lexical contexts; block scalars; `config` cascade and composition; `target` resolution; the definition set. Produces one arena-owned `RxtSource` |
| F2 | `src/core/internal.h` | C | `RxtSource`/`RxtDef`/`RxtTarget`/`RxtConfig`; `NamedGroup` gains `scope`; `Ast.u.cap` gains `at` and the header extent (§2.10); `PendingRef` gains the scope discriminator (§2.5); `Ctx` gains the scope stack and the assignment table |
| F3 | `cli/main.c` | C | `--source`, `--target`, `--lib-path`, `--emit-composed`, `--list-source`; `-o <dir>` (today `-o` writes one `.c` + one `.h`, `main.c:740-786`) |
| F4 | `src/core/compile.c` | C | one call in `compile_driver` between `pcrec_parse` (**`compile.c:882`** — r45gram 3; `:874` is an encoding `ctx_fail`) and `pcrec_altcls` (`:890`); `ctx_fail` (`:16-29`) consults the provenance scope |
| F5 | `src/parse/mod_named_groups.c` | C | B1's `(?<3>…)` / `(?<name=3>…)` |
| F6 | `src/parse/mod_recursion.c` | C | B2's `(?&^.name)` and B3's `(?&site=name)` / `(?&=name)`, in `rc_name_call` (`:269`) |
| F7 | `src/parse/registry.c` | C | three `RegRow`s so `--list-syntax` carries them (D24/D65) |
| F8 | `src/opt/callgraph.c` | C | **NEW in revision 2**: the `W` fixpoint excludes a delivering call's callee capture indices (§2.8) |
| F9 | `src/opt/atomic.c` | C | **NEW in revision 2**: `pcrec_has_live_capture` gains a delivering-call arm (§2.8) |
| F10 | `src/opt/postresolve.c` | C | the delivery refusals, on a call-graph activation bound (§2.8) |
| F11 | `src/gen/emit_dfa.c` | C | `rx_info.name`; `nentries`; the sort key; `.abi` 12→13 (`:1375`); `.ref` populated (emitted `NULL` today at **`:1190-1191`** — r45chk F14; the struct comment at `:602`) |
| F12 | `tests/harness/run.sh` | bash | three block arms + `features only`; the `have_block` guard on the case arms; one `--list-source` call per head-bearing file; cells; H11's target build; the C1 dump |
| F13 | `tests/harness/driver.c` | C | the prefix stops being hard-coded (`:304`, `:352-355`) |
| F14 | `tests/harness/verify_rxt.py` | python3 | the composed-block skip, a skip TOTAL (F13d), and `--dump` (C1's third leg) |
| F15 | `docs/spec/*` | md | §4 |

### 1.3 The grammar W1 accepts, and what it refuses

Exactly format_design §1.4's W1 row. Head: `lib`, `target … [with]`,
`description` (both forms), `config` (with `pcrec`/`flags`/`features`/
`encoding`/`engine`/`budget` and `from`). Body: `name`, `description`,
`encoding`, and `only` on `features`.

Refusals, by D26 tier; every one names the FILE, the LINE and the
CONSTRUCT:

| situation | tier | names |
|---|---|---|
| a W2/W3 keyword in the head | 3 | the keyword, and that it is **not in this build** |
| an unknown first token in a context | 3 | the token AND the context |
| a head line after the first `pattern` | 3 | the line and the boundary |
| a duplicate `config`/prefix/definition name | 2 | **both** sites (§2.2's namespace rule) |
| a `from` cycle | 3 | the cycle's members |
| `target … = <name>` with no such definition | 2 | the name and the `lib` chain searched |
| `-o <file>` with N > 1 targets | 3 | the targets and both ways forward |
| an unresolvable `lib` path | 3 | the path and the `--lib-path` list |

**DECIDED (1): a W2/W3 keyword is "not in this build", never "unknown".**
The alternative sends a reader hunting a typo in a word that is in the
spec — K14's shape mirrored.

### 1.4 The three pattern-level extensions

**MEASURED, `build/pcrec` at main `3372e1e`** (the format note's freeness
table predates [DD-11]'s new parser rows, so it was re-taken):

```
$ build/pcrec -p rx --features all -o - -- '(?<3>a)'
pcrec: subpattern name expected (a name starts with a letter or '_',
       never a digit) (pattern offset 3)                        rc=1
$ build/pcrec -p rx --features all -o - -- '(?&^.w)'
pcrec: subpattern name expected (...never a digit) (offset 0)   rc=1
$ build/pcrec -p rx --features all -o - -- '(?&from=email)'
pcrec: invalid subpattern name (pattern offset 0)               rc=1
```

All three still refused, so B1/B2/B3 remain free. Each displaces exactly
one existing validator:

| ext | spelling | doorway | displaces | module |
|---|---|---|---|---|
| B1 | `(?<3>…)`, `(?<name=3>…)` | `(?<` | the name-start validator (`mod_named_groups.c:187` region) | **`named-groups`** |
| B2 | `(?&^.name)` | `(?&` | the same validator via `rc_name_call` (`mod_recursion.c:269`) | **`recursion`** |
| B3 | `(?&site=name)`, `(?&=name)` | `(?&` | "invalid subpattern name" on the `=` | **`recursion`** |

**DECIDED (2): module ownership as tabled** — B1 to `named-groups`
(a group's number and name are two halves of one identity, and `(?<` is
that module's doorway), B2/B3 to `recursion` (both are properties of a
CALL). Each gets a `RegRow` so `--list-syntax` carries it (format_design
§3.3): three DIALECT rows, the shape `pcre2_compliance.md` already
handles.

### 1.5 `config`, `target`, and how many `.c` files come out

format_design §2.6 governs; the implementation notes are:

- **`with c1, c2` and the per-kind table are TWO DIFFERENT MECHANISMS**
  (r45gram 5, and revision 1 conflated them). `with c1, c2` composes
  CONFIGS: `c1`'s lines, then `c2`'s, later wins — one flat
  later-wins rule, no per-kind logic. The per-kind table (`features`
  UNION unless `only`; `flags`/`encoding`/`engine`/`budget`
  more-specific-wins; size caps MAX WINS) governs how the resulting
  config composes against a BLOCK's own directives. Two levels, two
  rules; conflating them would make `with` order-sensitive in exactly
  the way r44-sem M15 rejected.
- `config c from a, b` materialises ONCE at parse, so the `from` cycle
  check is the visited set of the expansion walk, not a separate pass.
- **`pcrec <raw>` is re-parsed by the CLI's own option parser**
  (`main.c:203`'s chain factored into a function taking
  `(argc, argv, pcrec_options*)`), so a flag cannot mean one thing on the
  command line and another in a `config` block.

Output naming (format_design §2.7, r44-sem M10, D88): `--target <p> -o
out.c` → one pair; `-o <dir>` → `<dir>/<prefix>.c` + `.h` per target;
`-o out.c` with N > 1 → refused. **D88 holds by construction** — each
target is a separate `pcrec_compile()` call; there is no code path that
could make a multi-artifact TU.

Compatibility default (Frank §6.4): no `target` and exactly one UNNAMED
block ⇒ `target rx`. MEASURED (r44-sem M11): two corpus files qualify
(`tests/mrl/11_motivating_shape_small.rxt`,
`tests/base/d27_nested_min_boundary.rxt`). Nothing in `make test` invokes
`--source`, so no existing run changes.

### 1.6 `rx_info.name`, `nentries`, and the abi's FOUR sites

**CITED — format_design §2.7 is stale: the abi is 12, not 11.** Three
sites agree, and r45gram 8 verified all four independently:

| # | site | change |
|---|---|---|
| 1 | `src/gen/emit_dfa.c:1375` | `.abi = 12` → `13`; the emitted `rx_info` struct text (`:596-660`) gains `const char *name` and `int nentries` |
| 2 | `tests/codegen/run_codegen_tests.sh:2707` | `ABI_EXPECT=12` → `13`, and the bump ledger in the `bad` message at `:2709` |
| 3 | `docs/spec/match_api.md:159` **and** §6's struct (~`:1340`) | the "`abi` is `12`" sentence, the two new members, and B4's §6 algorithm hunk |
| 4 | `tests/codegen/run_recursion_identity.sh:456` | `FILEPIN="${…:-c275aef}"` → the abi-13 change's last src-touching commit |

**Site 4's rule is per-ABI, not per-step (r45chk F8).** The file states it
at `:394-406`: *"THE PIN MOVES WITH THE LAST SCAFFOLDING CHANGE OF THE
`abi`, NOT THE FIRST — RE-RUN THIS GATE AFTER EVERY src-TOUCHING COMMIT
THAT FOLLOWS A RE-PIN"*, and a stale pin once reported 952 falsely
differing artifacts ([ART-SIZE]). W1.3 and W1.4 both touch
`emit_dfa.c` after W1.2's pin, so **the gate re-runs and the pin moves at
every merge of the abi-13 change** (§5).

`rx_info.name` is the block's `name`, or the prefix when unnamed, so no
artifact carries a NULL name (Frank §6.3) — and r45chk F9 is right that
nothing would have checked that, so §3.5 adds the assertion.
Comparison (A) is expected byte-identical: a stamped string in `rx_info`
sits above `goto <prefix>_L0;`, the argument [ENG-ABS] made for
`match_form`.

### 1.7 What the harness gains — and the guard

- **No head arms** (§1.1). One `--list-source` call per head-bearing
  file; MEASURED **zero** of the 179.
- **run.sh's 13 existing arms are not touched**; three new block arms
  (`name`, `description`, `encoding`) and `features only` append to the
  chain, after `features` and before the catch-all (order matters —
  `[[ =~ ]]` clobbers `BASH_REMATCH`, `run.sh:841-843`).
- **The case arms gain the `have_block` guard they were missing** —
  RULED. Today it is checked at only seven arms (`run.sh:844,855,866,880,
  886,912` — the six directive arms — plus `:1007`'s `g`/`gp`); `m`, `n`,
  `ms`, `ns`, `gu` and `perr` push unconditionally (`m` at `:922-931`),
  and the EOF flush is gated (`[ "$have_block" = "1" ] && flush_block`,
  `:1024`), so a case line with no open block was silently dropped rather
  than refused. **MEASURED — the guard is free:**

  ```
  $ find tests -name '*.rxt' -print0 | xargs -0 awk '
      FNR==1 { files++; seen=0 }
      /^pattern[ \t]/ { seen=1; pat++; next }
      /^(m|n|ms|ns|gu|perr|g|gp)([ \t]|$)/ {
          cases++; if (!seen) { print "VIOLATION " FILENAME ":" FNR; bad++ } }
      END { printf "files %d  pattern %d  cases %d  pre-pattern %d\n",
                   files, pat, cases, bad+0 }'
  files 179  pattern 3265  cases 26691  pre-pattern 0
  ```

  Zero of 26,691, so the 179 files never take the new branch and
  INV-COMPAT's argument is untouched. **The denominators are asserted
  rather than assumed** (the [DD-13c] lesson §3.1 makes a requirement of;
  a first run printing a bare `0` was discarded for exactly that reason),
  and they **independently reproduce format_design §1.1's census to the
  digit** — 179 / 3,265 / 26,691 — from a different direction, since the
  awk was written from run.sh's arm list and not from that census. That
  population has now been derived three ways (the note's own,
  r44-grammar G1's recognizer, and this).
  The guard is the GENERAL form of a guard seven arms already carry, not
  a special case, and §3.4's S-C10 case 3 becomes harness-detected
  because of it.
- **H3 cells**: one run per resolved config; the `perr` one-cell rule is
  a guard at dispatch, not a filter after (re-running `perr` under a
  config's `--features all` would silently change **384** blocks).
- **H11**: **DECIDED (3) — `driver.c` takes the prefix as a `-D` macro**,
  not a generated shim (a shim adds a code generator to the harness whose
  output nobody reviews). Default `rx`, so every existing invocation is
  unchanged.
- **H4**: **DECIDED (4) — the composed-block skip is STRUCTURAL and
  COUNTED**, never a caught `re.error`. python `re` has no subroutine
  call at all (CITED, `subroutines_design.md` §10.1: "not different
  semantics, an ABSENCE"). `verify_rxt.py` skips when the file declares a
  `lib` or a `name` and the block's pattern carries a by-name reference,
  and — r45chk F13(d) — it gains a **TOTAL** skip line, since today it
  prints a per-file line only `if skipped:` (`:387-388`) and C3 needs an
  aggregate to compare.
- **NOT built**: H5-H10 (`include`, `@file:`, `mc`, `tag`, data blocks,
  `use`/`variant`/testees). D77 at wave granularity.

**MEASURED — the corpus is 179 files but run.sh dispatches 178 workers,
and the manager asked which one and why.** `run.sh:184-186` discovers with
`find "$ROOT_DIR/tests" -name '*.rxt' -not -path "*/known_fail/*"`. The
excluded file is exactly one:

```
$ find tests -name '*.rxt' -path '*/known_fail/*'
tests/known_fail/k34_leftrec_giveup.rxt
```

So **179 files exist, 178 are dispatched, and the 179th is the known-fail
ratchet's own file** — deliberately outside the corpus run (CLAUDE.md's
"the known-fail ratchet"). Consequence for §3: **C1's and C2's
denominators are different numbers on purpose** — C1 (a parse
differential, which can and should read every file) asserts **179**,
while C2 (the answer re-run, which is run.sh's own population) asserts
**178 workers**. Revision 1 would have asserted 179 in both and the
second would have been wrong. Both numbers are pinned in §3.1.

### 1.8 `--list-source` — the output contract (RULED)

r45gram 2 was right that revision 1 cited two incompatible uses and
specified neither. The manager ruled the format; this section is it.

**TSV under `docs/spec/table_contract.md`** — the house wire format:
`\n` line ends, `#` comment lines, the LAST `#` line before data is the
header, columns **append-only**, an empty field means "none", **no field
contains a TAB**. **One row per declaration and per block, in FILE
ORDER.**

| # | column | on | value |
|---|---|---|---|
| 1 | `kind` | all | `lib` \| `target` \| `config` \| `description` \| `pattern` |
| 2 | `line` | all | 1-based first line of the declaration/block |
| 3 | `name` | target, config, pattern | the target's PREFIX; the config's name; the block's `name` (empty if unnamed) |
| 4 | `value` | lib, target, description | `lib`'s path-ref; `target`'s definition name; `description`'s text |
| 5 | `pattern` | pattern | the block's pattern text |
| 6 | `flags` | pattern, config | the letters |
| 7 | `features` | pattern, config | the module list |
| 8 | `features_only` | pattern | `1` if the block wrote `features only` |
| 9 | `encoding` | pattern, config | the ident |
| 10 | `engine` | pattern, config | `vm` \| `dfa` |
| 11 | `budget_steps` | pattern, config | N |
| 12 | `budget_frames` | pattern, config | N |
| 13 | `with` | target | the config list |
| 14 | `from` | config | the config list |
| 15 | `pcrec` | config | the raw flag text |

**DECIDED (5): `kind` carries the DECLARATION NAME, not a `head`/`pattern`
supercategory** — one column instead of two (a `head` row still needs
something to say which declaration it is), it matches `--list-syntax`'s
own `kind` column, and **"is this a head row" needs no column at all**:
the head ends at the first `pattern` line, so a head row is exactly one
preceding the first `pattern` row. That is a property of the ORDER, which
is what C1 compares — a column for it would be a second home for a fact
the row order already carries, free to disagree with it.

**SECTIONLESS for W1, with a named trigger.** The contract's `#section`
mechanism exists for "one command, several tables, different columns" and
is declined here on purpose: the head/body INTERLEAVING is what C1
checks, and it is expressible only as row order in ONE stream — two
sections would make "the head ends at the first `pattern` line"
unrepresentable in the very output whose job is to prove it.
Backwards-compatible-by-absence means adopting later is free, and the
trigger is concrete: **W2's `freq` data block**, whose
`row <offset> <16 counts>` cannot be a column here under any reading. The
spec hunk says so (§4).

**AS-WRITTEN, not resolved.** C1's job is to prove the two PARSERS agree;
resolution is a third thing only pcrec does, so a resolved dump would
compare pcrec's resolver against no counterpart — and would force a
second resolver into run.sh, the duplication this seam exists to avoid.
`--list-source --resolved` is NAMED and UNBUILT (D77).

**THE TAB HAZARD, and it is live.** A `pattern` line is REST-OF-LINE
verbatim, so a pattern may contain a literal tab; a `description` block
scalar contains newlines by construction. MEASURED:

```
$ grep -rP '^pattern .*\t' tests --include='*.rxt' | wc -l      -> 3
$ grep -rP '^pattern .*\t' tests --include='*.rxt' | cat -A
tests/base/bounded_repeats.rxt:pattern a{^I1}$
tests/base/bounded_repeats.rxt:pattern a{ 1^I,^I2 }$
tests/modifiers/xxmode.rxt:pattern (?xx)[a^Ib]$
```

Three blocks, and **in every one the tab is the thing under test** — a
tab inside a brace quantifier (so `a{\t1}` is a literal brace run, not a
quantifier) and a tab inside a class under `(?xx)` (where extended mode
strips class whitespace). Emitted raw, the field splits and every later
column shifts on exactly those rows.

**RULED: columns 4, 5 and 15 are escaped in the `.rxt` format's OWN
subject-escape vocabulary** (`\t \n \r \\ \xNN`) — already specified in
`rxt_format.md`, already implemented in `driver.c`'s `decode()`, already
what a `.rxt` author knows. No second decoder is invented for the
differential to drift across. Sabotage row S-C9 (§3.4).

**A precedent and a divergence, worth stating because both dumps live in
run.sh.** `RXTDUMP` (`run.sh:56-62`, `:484-490`) is an existing TSV dump —
one line per CASE OUTCOME, for [CHK-2]'s axis sweep — and it handles the
same hazard by **lossy squashing**: `flat_err="$(printf '%s' "$pcrec_err"
| tr '\n\t' '  ')"`. That is correct THERE (it is diffed against itself
across axes, so a squash that is applied identically on both sides loses
nothing that matters) and would be **wrong here** (C1 is a
cross-implementation differential, where a squash could hide exactly the
disagreement being looked for). Two dumps, two disciplines, one script —
so the note names both rather than letting a later reader assume the
older one's rule.

---

## 2. The composer

### 2.1 Where it runs

**CITED, `compile_driver` (`src/core/compile.c`)** — the ordered stages,
with r45gram 3's correction:

```
compile.c:840  pcrec_parse_mods_init(&cx)
compile.c:882  root = pcrec_parse(&cx)        <- (revision 1 said 874;
        ...    << THE COMPOSER RUNS HERE >>       :874 is an encoding ctx_fail)
compile.c:890  root = pcrec_altcls(&cx, root)
compile.c:906  root = pcrec_discharge_atomic(&cx, root)
compile.c:925  pcrec_callgraph_build(&cx, root)
compile.c:952  pcrec_select_engine(&cx, root)
compile.c:963  pcrec_postresolve(&cx, root)
compile.c:1128 pcrec_emit_vm / pcrec_emit_dfa
```

**After `pcrec_parse`, before `pcrec_altcls`** — both bounds forced:
after parse because the composer needs the caller's `ncap`,
`named_groups` and resolved references; before `callgraph_build`
absolutely, because that pass is the only writer of `u.call.body`, is
driven from `u.call.target` over the FINAL tree, and `callgraph.c:20-57`
records why (a `.body` captured earlier names a subtree `altcls` has
rebuilt — "TWO DIFFERENT PROGRAMS FOR ONE GROUP"); before `altcls` so an
injected definition gets the same optimization every other subtree gets.

**The output is expressed in NUMBERS, not pointers** — `u.cap.no` and
`u.call.target`, which `altcls` copies when it rebuilds a node. A future
composer holding an `Ast*` would inherit `callgraph.c`'s staleness
problem; §2.5 keeps it to numbers for that reason.

### 2.2 The sub-parse: one `Ctx`, one arena, a saved scope

A definition lives in a different `pattern` line — a different STRING.
Two candidate mechanisms: a second `Ctx` with its own arena plus a deep
node-clone pass (a second place that must know every `AKind` and every
D70 payload, going stale silently when a kind is added), or a **sub-parse
on the SAME `Ctx`**. The tree makes the second cheap: `Arena arena` is a
member of `Ctx` (`internal.h:1553`) and `pat`/`patlen`/`pos` are plain
fields (`:1554-1556`) that `compile.c:576-577` simply assigns; and
`pcrec_parse_mods_init` is documented IDEMPOTENT precisely because
`--explain`/`--probe-ask` already build a bare `Ctx` and call a parser
entry directly.

**The scope that is swapped, and why each entry is load-bearing:**

| field | why |
|---|---|
| `pat`, `patlen`, `pos` | the definition's own text is what is parsed |
| `ncap` | **the definition's groups must number from 1 in its OWN space.** `ncap` is read DURING the parse — `internal.h:1603` records PCRE2's rule that `\12` is a backreference iff the RUNNING count ≥ 12, else octal — so parsing with the caller's count advanced would change what the definition MEANS. This is D87 rule 7(i)'s "preserving local order and gaps" enforced where it can be, and r45chk F11 is right that §3 must TEST the meaning failure and not only the renumbering one (§3.2 W-1c) |
| `named_groups`, `n_named_groups` | the definition's `(?&w)` must bind to the DEFINITION's `w` (D87 rule 2); resolution walks this list (`mod_backrefs.c:683-687`, lowest number wins) |
| `pending_refs`, `n_pending_refs` | `pcrec_parse_info` ends by resolving the WHOLE list (`parse.c:1321`); without swapping, a sub-parse would resolve the caller's incomplete list against the definition's `ncap` |
| `mods` | **SEEDED FROM THE DEFINITION BLOCK'S OWN RESOLVED `flags`, not restored and not inherited** — r45sem M2. `pcrec_parse_mods_init` seeds `.caseless` from `cx->opt->flags`, which is the TARGET's options; format_design §2.6 makes `flags` block-scoped, so a definition block that wrote `flags i` must get it and one that did not must not. Blast radius: `flags i` |

**`first_cap_pos` / `first_vmonly_pos` are NOT restored — they take a
THIRD state** (r45sem M1, and revision 1 had this wrong). These are
diagnostic offsets into `cx->pat`. `forces_captures` walks the COMPOSED
tree and then reads `cx->first_cap_pos`; if the only capture is inside a
DEFINITION, a restore leaves `(size_t)-1` and `engine_why` stamps
`18446744073709551615` — or, under `--engine=dfa`, `ctx_fail` reports
it. `forces_registry` has the same hole with offset 0. So the fields
become "unset / this pattern's offset / **a scope-stack reference**", and
§2.9's stack is the supply for the third state: the diagnostic names the
definition's `file:line` and its own local offset, which is the same
answer §2.9 gives every other refusal.

**A `RxtParseScope` holds these; one function saves and one restores.**
The obvious question — what happens when `Ctx` gains a field that belongs
on it — is answered by a check, not by vigilance: §3.4's S-W6 plants a
forgotten swap and names the check that must catch it, and after F11 that
check tests MEANING as well as numbering.

### 2.3 Which references are FILE references

**DECIDED (6): under `--source`, `pcrec_bref_resolve` DEFERS an
unresolved BY-NAME reference instead of failing, and the composer
resolves it or re-raises.** By the time `pcrec_parse` returns, resolution
has already run (`parse.c:1321`) and would have refused with *"refers to
a capture group named 'X', which this pattern does not declare"*
(**`mod_backrefs.c:733-734`** — r45gram 4; `:707-725` is the counts-back
refusal). Running the composer earlier, inside `pcrec_parse_info`, was
rejected: that is the ONE parse entry point, shared by `--count-groups`,
`--explain` and the built-status probe (`parse.c:1318`), and making it
composition-aware puts a file-level concern inside the parser. So a flag
on `Ctx`, set only when `--source` supplied a definition set, defers.
Numeric references are unaffected — a number cannot be a file reference.

**The corpus refusal is preserved exactly.** MEASURED (format_design
§2.4): four blocks reference an undeclared name, all `perr`, all in
`tests/recursion/d27/sr_refusals.rxt`, a file with no `name` and no
`lib`. With no definition set the flag is off and those four refuse
today's refusal at today's offset.

**The deferral must keep leftmost-failure ordering** (r45sem S2).
`mod_backrefs.c:655-658` states the rule — *"THE LEFTMOST FAILURE IS THE
ONE REPORTED. The list is prepended, so it is in reverse source order"* —
and it compares `pr->at`, a bare offset. Under composition `at` may be an
offset into a DEFINITION's text, so bare offsets are no longer totally
ordered. **The ordering key becomes (file, line, offset)**, all three
available from §2.9's scope stack.

**The three reference classes, and B2 is now one of them** (r45sem B2 —
revision 1 never classified it):

| class | spelling | resolved | re-based? |
|---|---|---|---|
| local | `(?&w)` where `w` is this pattern's own | during the sub-parse | YES, with the body |
| **file** | `(?&email)` naming a definition | by the composer, after the walk | it IS the injected body's number |
| **caller-scope** | **`(?&^.w)`** (B2) | by the composer, **AFTER the re-basing walk** | **NO — never** |

**B2 is the one that bites**, and r45sem's example is exact: `d` =
`(?&^.w)x` bound into `^(?<w>a)(?&d)$` (caller `ngroups` 1, base 2). The
reference targets the CALLER's group 1; a walk that adds `base` makes it
3, which is `d`'s own first group. The library would silently read its
own group instead of its caller's. §2.5 is where this is prevented.

Steps 2-4 otherwise stand: resolve against the file's own `name`d blocks
then its `lib`s in declaration order, transitively; a **visited-set
fixpoint with dedup** (cycles ALLOWED — self- and mutual recursion
compile and match on both oracles, r44-sem M8).

**DECIDED (7) — a block's own `name` is in the FILE namespace, not the
pattern's.** r45sem S3 showed revision 1's phrasing ("a block's own
`name` joins the names its pattern declares") is both ambiguous and
unimplementable in the sub-parse: the names are swapped out, and `base`
is not known until after. And it has no answer for a block named `x`
whose pattern also declares `(?<x>…)`. So: **a `name` line names the
block in the FILE's definition namespace and is never a name the pattern
declares.** A block calling itself writes `(?&self)` — a reserved word
in the call namespace, resolving to the enclosing block — and lexical
scope wins inside, unchanged. This is the manager's ruling; the cost is
one reserved word, and the benefit is that the two namespaces stop
overlapping at exactly the point revision 1 could not describe.

**DECIDED (8) — REWRITTEN on the manager's ruling (r45chk F10): the
textual control RE-DERIVES the closure from its own text.** Revision 1
had the control CONSUME the composer's reported closure and
simultaneously called a closure mismatch "a failure in its own right" —
with one derivation there is nothing to mismatch against, so S-W8
("let the control re-derive") planted INDEPENDENCE and expected a red,
which a correct composer would pass. Now: the control derives its own
closure from the source text, the comparison against the composer's
report is REAL, and **S-W8 becomes "make the composer's report disagree
with the text"**. The composer still REPORTS its closure (order and
size); what changed is that the report is now checked rather than
trusted.

### 2.4 Injection: the shape already in the tree

**A bound definition is injected as
`A_REP{rmin=0, rmax=0}( A_CAP{no = base} ( body ) )`, concatenated onto
the caller's root in closure order.** This is not a new shape — CITED,
`mod_recursion.c:418-476` and its header at `:356-417`, quoting D71 item
4: *"the `{0}` layout rule the R34 verifier forced already IS DEFINE's
semantics"*; the port builds no special node, *"so no downstream pass
(`callgraph.c`, `vm_count_slots`, `emit_vm.c`) needed a new line for
it."*

**An `A_CAP` wrapper is REQUIRED, not chosen.** CITED, `callgraph.c:162`
and `:178`: the bind walks the final tree and matches *"the `A_CAP` whose
`u.cap.no` matches"* the call's `u.call.target`; `target` is an `int`
group number and is the durable fact, `.body` a cache the binder
recomputes (`:22`). There is no other key. Setting `u.call.body` directly
is rejected on `callgraph.c`'s own recorded reasoning (its founding bug,
commit 513de65, detector S144).

**What W1 reuses — and, after r45sem B1, what it must CHANGE.** Revision
1's table claimed six mechanisms reused and nothing touched; two of those
entries were wrong.

| mechanism | where | W1 |
|---|---|---|
| `(?(DEFINE)…)`'s AST shape | `mod_recursion.c:418` | reused unchanged |
| `A_CAP.u.cap.no` | `internal.h:553`, `parse.c:839-864` | reused; the composer assigns the re-based number |
| call binding by number | `callgraph.c:162,178` | reused unchanged |
| splice/linkage choice | `callgraph.c`'s `cg_eligibility` | reused unchanged — *the format pins the answer; the compiler chooses the linkage* |
| the caps slot layout | D61; `emit_dfa.c:392-395` | reused; delivered slots land above `ngroups` by arithmetic |
| deferred offset-bearing refusals | `src/opt/postresolve.c` (`internal.h:3241`) | reused for the delivery refusals |
| **`pcrec_has_live_capture`** | `src/opt/atomic.c:744-760` | **CHANGED — a delivering-call arm (§2.8)** |
| **`vm_splice`'s per-site save block** | `emit_vm.c:5915-5985`, `vm_region`'s restore `:6036-6046` | **CHANGED — a delivering site's delivered capture indices are omitted from ITS OWN save block (§2.8)** |
| **`cg_eligibility`** | `src/opt/callgraph.c:446`, the link write at `:423` | **CHANGED — one input: a delivering site forces `CALL_SPLICE` (§2.8)** |
| **the `groups[]` sort key** | `emit_dfa.c:1136`, `:1156-1166` | **CHANGED — (ref-is-NULL, name, number) (§2.7)** |

**N3 — the "delivering" bit lives ON the `A_CALL` node, and is written
EXPLICITLY on every call.** It cannot be a side table: `internal.h:3247`'s
walkers are bare `const Ast *` descents with no context and no memo (the
reason `callgraph.c` exists at all), so a predicate asked of a node must
be answerable from the node. And the arena zero is **the unsound
direction** — a flag defaulting to "not delivering" turns a missed write
into a silently capture-transparent call, i.e. delivery that quietly does
not happen, which no check downstream can distinguish from a site the
author never declared. This is `link`'s own situation and gets `link`'s
own answer: `callgraph.c:246` and `:337` record that *"the arena zeroes
to `CALL_SPLICE`, which is the WRONG default"*, so wave B+C sets `link`
on every node rather than relying on the zero. **The composer likewise
sets the delivering bit on EVERY `A_CALL` — true and false alike —
before selection runs**, so "never written" is not a reachable state.

The three CHANGED rows are the honest form of revision 1's claim. Every
alternative that would have created a parallel mechanism — a definition
id space beside group numbers, a pre-bound `.body` edge, a node-clone
pass, an AST serializer — is still rejected on a reason recorded in the
tree; what revision 1 got wrong was not the reuse argument but the
assumption that delivery needed no mechanism at all.

### 2.5 Re-basing: one walk, keyed on the `PendingRef`

After the sub-parse returns a definition subtree resolved in its own
number space (`1..k`), the composer walks it once and adds `base` to:

| field | node | note |
|---|---|---|
| `u.cap.no` | `A_CAP` | the assigned number |
| `u.bref.refs[i]` | `A_BREF` | the resolved backreference targets — this subtree's own (a definition is bound ONCE, by dedup) |
| `u.call.target` | `A_CALL` | **only for a LOCAL call** — see below |

**The `target == 0` carve-out of revision 1 is DELETED** (r45sem M4).
Revision 1 skipped `target == 0` as "the root". That is not decidable
from the field: the arena zeroes it, `mod_recursion.c:41` and `:128` set
`0` for `(?R)` **and queue no pending record at all**, and DECIDED (6)'s
deferred cross-definition `(?&other)` also reads `0` when the walk runs.
Three different situations, one value.

**So the walk is keyed on the `PendingRef`, not on the node's current
value.** Every call the sub-parse resolved LOCALLY has a `PendingRef`
recording that it was resolved and to what; the walk re-bases exactly
those. A call with no pending record is `(?R)` (refused, below); a call
whose pending record is still deferred is a file or caller-scope
reference and is resolved AFTER the walk, at its final number.

**N4 — the sub-parse's pending list must be CAPTURED, not merely
restored, and revision 2.1 left that ambiguous.** §2.2 swaps
`pending_refs`/`n_pending_refs` into the scope record and restores them
afterwards. If the restore simply puts the CALLER's list back, the
definition's own records — the very things this walk is keyed on — are
gone by the time the walk runs. **So the scope record CAPTURES the
definition's list head**: on leaving the sub-parse the caller's list is
restored to `cx` *and* the definition's head is retained in the scope
record, which the composer then owns.

The walk is therefore **two passes over two structures, not one**:

- a **tree walk** over the definition's subtree, re-basing `u.cap.no` on
  every `A_CAP` (a group is a node and nothing else records it);
- a **pass over the captured `PendingRef` list**, re-basing the resolved
  `u.call.target` and `u.bref.refs[]` of exactly the references that
  sub-parse resolved locally.

Stating it as one walk hid the fact that the two need different
iteration; stating it as two makes the `(?R)`/deferred cases fall out —
they are simply not in the captured list.

**`PendingRef` gains a scope discriminator** (r45sem B2), because
`(?&^.w)` and `(?&w)` are the same node kind with the same field. The
discriminator is written where the spelling is parsed — `rc_name_call`
(`mod_recursion.c:269`) sees the `^.` prefix — so it is a parse fact
recorded at the one place that knows it, not an inference later. A
caller-scope reference is then never re-based and is resolved against the
CALLER's `named_groups` after the walk.

**Relative forms need no re-basing** (D87 rule 7(g); r44-sem R0-R6):
`(?-1)` and `\g{-1}` mean textual position, and relocation preserves the
body's internal order.

**`(?R)`, `(?0)`, `(?00)` and `\g<0>`/`\g'0'` inside a bound definition
are REFUSED for W1** — Q-W2, parked for Frank with this recommendation.
A definition's `(?R)` means "this whole pattern"; after injection the two
readings (the caller's root; the definition's own body, i.e. its wrapper)
are both defensible, and D87 chose mechanisms over silent defaults. The
refusal is raised **at the sub-parse**, because nothing later can tell it
from M4's other zeros. r45sem's counter-argument is recorded rather than
buried: D87 rule 1's "absolute references are LOCAL to the pattern they
are written in" applies verbatim to 0, whose local meaning after
injection is the wrapper — so re-basing 0 would be rule 7(i) executed
consistently. **The reason for refusing is that the RULING is missing,
not that the meaning is unclear.** §6.0 gains this as piece-rule member
(vi).

**MEASURED, and this design reproduces the fixed row.** M1's cell:
library `dd` = `(\d)\1`, caller `^(\d)-(?&dd)$`, `ngroups` 1, base 2,
`dd`'s own group 1 → 3, `\1` → `\3`; the composed pattern matches `5-77`
and rejects `5-75` — the library's own meaning restored (format_design
§2.3.3, both oracles).

### 2.6 The wrapper takes a number — the control's offset is ZERO

**This reverses format_design §2.3.3's RECOMMENDED and deletes §2.3.4's
derived offset `j`.** `A_CALL.target` is a group number and
`callgraph.c:162,178` binds by matching `A_CAP.u.cap.no`, so a callable
body must hold a number in the same space every other group is in; a
separate id space is a second key in the binder. The format note's own
reason for denying the wrapper a number survives — §2.13's struct has no
member for the definition itself — because that is about the struct VIEW,
and a number is not a member.

So the wrapper takes `base` and the definition's own groups take
`base+1 .. base+k`, and PCRE2's textual append spends one number per
definition on its `(?<name>…)` wrapper exactly as the composer does:

| | caller `(\d)` | wrapper `dd` | `dd`'s `(\d)` |
|---|---|---|---|
| textual control `…(?(DEFINE)(?<dd>(\d)\3))` | 1 | 2 | 3 |
| the composer | 1 | 2 | 3 |

**The offset is zero and the control compares slot for slot** — a better
answer to the hazard format_design §2.3.4 names ("a control that
obviously compares equal, then quietly stops comparing the thing it
names") than deriving the offset carefully.

**r45sem ratified the mechanism and added the correction this note owed:
it IS caller-observable.** Each bound definition costs one permanently
unset slot, and every delivered number shifts by one — **so the first
delivered group is at `ngroups+2`, not `ngroups+1`**, and §4's S9b hunk
must say the wrapper consumes a slot. Q-W1 goes to Frank with that
attached. r45sem also confirmed PCRE2 parity twice: format_design's cells
F/G/J, and `atomic.c`'s own 10.46 re-measurement that the DEFINE wrapper
consumes a number.

### 2.7 `ngroups`, `nnames`, `nentries` — and the ABI contract

**CITED, D61 and format_design §2.7:** `ngroups`/`nnames` stay the
PRIMARY's own; delivered slots sit above.

Two counters that are one today:

```
cx->ncap_primary   the caller's own count, frozen at the first sub-parse
                                                  -> rx_info.ngroups
cx->ncap           the highest assigned number after composition
                                                  -> RX_NCAPS - 1
```

`dfa_artifact_ncaps()` (`emit_dfa.c:392-395`) already reads `cx->ncap + 1`
and needs no change; `.ngroups` (`emit_dfa.c:1492`) changes from
`cx->ncap` to `cx->ncap_primary`. On every non-composed compile the two
are equal by construction, so **every artifact pcrec emits today is
byte-identical** — which is what makes identity gate (A) a real check of
this change.

**B4 — revision 1's `nnames` rule broke a SHIPPED contract, and the
manager ruled the fix.** `NamedGroup` gains `const char *scope` (NULL for
the primary's own). Revision 1 then said `nnames` counts `scope == NULL`
while `groups[]` holds every row. r45sem showed that is an ABI break:
`emit_dfa.c:1156-1166` builds the array from ALL of `cx->named_groups`
sorted by `(name, number)` and `:1493` emits `.nnames =
cx->n_named_groups`, so today `nnames` IS the array length — and
`match_api.md:1349` documents it as *"entries in groups[]"*, with
`:1684-1695` giving the caller a bsearch that walks BACK to a name run's
first row and FORWARD to the first row that participated. If injected
rows sort AMONG the primary's while `nnames` counts only the primary's, a
caller can miss its own name or land on a library's private group —
**D87 rule 2 violated at the artifact tier**, one level below where the
composer enforces it.

**RULED (manager):**

1. **The sort key becomes `(ref-is-NULL first, name, number)`**, so the
   primary's rows are a genuine PREFIX of `groups[]`.
2. **`nnames` keeps its meaning** — the primary's entries — and a caller
   that ignores composition runs `match_api.md` §6's algorithm unchanged
   over `groups[0..nnames)`, correctly, forever.
3. **A NEW `int nentries`** (total rows) rides the abi-13 bump, for a
   caller that wants the injected rows.
4. The §6 algorithm hunk states it; **[M6.5-DUPNAMES]'s expectation moves
   in the same change** — it reads the emitted rows' order off the
   artifact and asserts non-decreasing `(name, number)`, which a new
   leading key changes.

**Name qualification, and the THREE walkers** (r45sem M3 — revision 1
named one, and the wrong pass). `cx->named_groups` is walked by:

| walker | site | effect of injected rows |
|---|---|---|
| the `PEND_CALL` name arm | `mod_backrefs.c:683-687` | a caller's `(?&w)` could bind an injected `w` |
| `br_name_run` (the `PEND_BREF` arm) | `mod_backrefs.c` | a caller's `\k<w>` could SEE an injected row |
| `emit_info_def` | `emit_dfa.c:1160` | the artifact's name table |

**The pass revision 1 named has already run** at injection time
(`parse.c:1321`), so the rule cannot live there. It belongs to **the
composer's re-resolution** (DECIDED (6)): when the composer resolves a
deferred by-name reference, it walks only rows with `scope == NULL` for a
caller's reference, and only the definition's own scope for a
definition's. The artifact walker gets the scope through `.ref`.

**`rx_group_entry.ref` is the column this fills, and it already exists** —
CITED, `emit_dfa.c:602`: `const char *ref; /* NULL/empty for the
primary's own groups */`, emitted as literal `NULL` today at
**`:1190-1191`**. D61's "labeled insertion path" reserved it; W1 is its
first producer.

**One derivation, three readers** (D87 rule 5; learnings §3): the
ASSIGNMENT TABLE — ordered `(number, scope, name-or-NULL, provenance)` —
is the single source for `RX_NCAPS`, the `rx_group_entry` array and
`--emit-composed`. r45chk F4 is right that this makes W-5 and W-7
consistency checks rather than controls, and §3.3 re-scopes them and adds
one whose expectation comes from libpcre2.

### 2.8 Delivery — a NAMED deviation, not a free ride

**Revision 1 said "W1 delivers SLOTS" and r45sem refuted it with two
measured mechanisms. Both are real, and together they mean a delivering
call as revision 1 described it delivers NOTHING.**

**(a) The pattern looks capture-DEAD, so the DFA takes it.** CITED,
`src/opt/atomic.c`'s `pcrec_has_live_capture` (`:744-760`): the `A_CALL`
arm returns **false** with no descent — its header says *"A subroutine
call is CAPTURE-TRANSPARENT — the capture state after the call is exactly
the state before it, whatever the call did"* — and the `A_REP` arm prunes
`rmin == 0 && rmax == 0`, **which is exactly §2.4's injection wrapper**.
So a composed pattern whose only captures live in definitions has no live
capture anywhere, `forces_captures` (`select_engine.c`) permits the DFA,
and `dfa_artifact_ncaps` promises pairs no match can set: every delivered
slot reads `-1,-1`.

**And PCRE2 agrees, which is why this is a deviation and not a bug.**
CITED, the same header, MEASURED on 10.46: `(?(DEFINE)(?<g>a))(?&g)` has
CAPTURECOUNT 1 and answers g1 **UNSET**. Delivery is a pcrec feature that
PCRE2 does not have; it cannot fall out of reusing PCRE2's semantics.

**(b) Even on the VM, the return WIPES them.** CITED,
`internal.h:826-849`: `u.call.nsave`/`save` is `|W|`, *"the CALLEE
REGION's SLOT WRITE SET: EVERY slot family any node in the callee's
transitive body can write"*, restored on return, with **only slots 0 and
1 excluded** (because `\K` is measured not to be restored). A delivering
call's captures are inside `W` and are put back.

**So delivery needs TWO named mechanisms, and §2.4's table now says both
are touched:**

1. **A live-capture arm for a DELIVERING call** (`src/opt/atomic.c`). A
   delivering call reports live, so `forces_captures` keeps the VM. The
   polarity is the safe one by that function's own rule — its header:
   *"`true` ('something is live') keeps the VM… a walk that over-reports
   costs an engine and never a wrong span. A walk that UNDER-reports puts
   a writable group on an engine that cannot record it, which is a lost
   capture."* We are moving from under-reporting to correct.
   **It keys on the CALL being delivering, never on the wrapper's shape.**
   That file's header explicitly warns against the alternative: *"a
   `DEFINE`-shaped special case would have been a parallel mechanism for
   two thirds of its own population."* One predicate, keyed on the fact
   that actually matters.
2. **A delivering call is FORCED to `CALL_SPLICE`** — RULED (manager,
   architecture, on r45sem's re-check), and revision 2.1's version of
   this mechanism was NOT IMPLEMENTABLE as it was scoped.

**Why the obvious form does not work, and it is a scoping mismatch rather
than a bug.** Revision 2.1 said "the callee's capture indices excluded
from `W`". **`W` is a per-REGION property; "delivering" is a per-CALL-SITE
one** (D87 rule 5: *"Per CALL SITE, not per definition"*). CITED,
`vm_publish_saves` (`emit_vm.c:5716-5735`):

```c
case A_CALL: {
    int i = pcrec_callgraph_index(v->cg, a->u.call.target);
    ...
    a->u.call.save  = v->rgn_w[i];
    a->u.call.nsave = v->rgn_nw[i];
```

The index is the call's TARGET, so **every call site of one region is
handed the same `W` array**. Excluding a delivered group's capture
indices there would exclude them for every OTHER site of the same
definition too — including non-delivering ones, which must stay
capture-transparent. One definition called twice, delivering at one site
and not the other, is precisely the case §2.13 exists for, and it is the
case the exclusion cannot express.

**The splice makes the exclusion per-site by construction.** CITED,
`vm_splice` (`emit_vm.c:5915-5985`):

```c
const int base = v->nsplice;
v->nsplice += a->u.call.nsave;
```

`base` is **fresh at each site**, so a spliced call's save slots are that
site's own. Forcing a delivering call to `CALL_SPLICE` therefore puts the
capture exclusion exactly where "delivering" lives, and no other site of
the definition is touched.

**Two things keep the forcing finite, and both are already rules of this
design**: a recursive definition is non-deliverable (the first refusal
below), so a forced splice can never be asked to inline a cycle; and the
activation bound (≤ 1 along every path) is what bounds the splice's
expansion. The forcing is thus safe *because* of the two refusals, which
is worth stating — they were written for the struct's sake and turn out
to be the splice's precondition as well.

**`cg_eligibility` gains one input**: a site's delivering flag forces
`CALL_SPLICE` for that node. Today `callgraph.c:423` writes the link from
a per-REGION decision (`if (i >= 0 && cg->splice[i]) … = CALL_SPLICE`),
so the per-site force is an override at that write, not a new pass.

**N2 — the restore's INDEX SPACE, and why a dropped capture is coherent
rather than merely absent.** The restore is emitted in `vm_region`
(`emit_vm.c:6036-6046`) over `v->rgn_w[i][j]` — **the callee region's OWN
index space**, not the caller's and not the lexical occurrence's
(`internal.h:826-849`: *"THE INDICES ARE THE CALLEE REGION'S OWN … a
restore written against the wrong indices is §5.3b's axis-C miscompile
arriving by a second route"*). `vm_publish_saves`'s own header states the
coupling this design must not break: *"Three readers, one write"* —
`vm_call`'s save emission, `vm_region`'s restore emission, and
`vm_cost`'s `2 * |W|` trail charge. **A change that drops an index from
the save must drop it from all three**, and the loud detector already
exists: `vm_splice`'s overflow `ctx_fail` (`emit_vm.c:5924-5932`), which
names K27's class explicitly — *"the pre-pass and this walk disagreed
about how many sites there are or how big `W` is … LOUD, because the
alternative is an out-of-bounds write in EMITTED code."*

And the omission is **trail-coherent**, which is the part that makes it
safe rather than merely selective: the restore is a `vm_set`, and
`vm_set` is TRAILED — the emitted comment says so, *"restore the caller's
value, itself TRAILED so a retreat into this callee re-establishes the
callee's own"*. So a delivered capture that is NOT restored keeps the
callee's value after the return, and a later backtrack through the call
undoes it exactly as it undoes every other trailed write. Delivery does
not need a second undo mechanism; it needs one fewer restore.

**Every other slot family stays in `W`** — `SLOT_GROUP<n>_PENDING`,
`SLOT_CUT_MARK<n>` and the rest — because `internal.h:826-849` records
that the capture-only version of `W` was **refuted twice** (two lost
matches, six false matches). This is a targeted omission of a named
subset at one site, not a return to that rule, and the note says so
because the failure mode is recorded and expensive.

**The two non-deliverable shapes, and M5/S1's correction.** Revision 1
said "a call under a repeat" and checked lexical repeat depth. r45sem M5
showed that refuses EVERY delivering call, since every injected
definition sits under `A_REP{0,0}` — and exempting the wrapper is exactly
the DEFINE-shaped special case above. S1 added that `{1,1}` and `?` bound
activations at ≤ 1 and are fine (`parse.c:1113` builds `A_REP`
unconditionally).

**RULED: the bound is a CALL-GRAPH property — activation ≤ 1 along every
path — not lexical repeat depth.**

| shape | why | where |
|---|---|---|
| a **recursive** definition (self- or mutual) | depth is a runtime fact; the member type would be infinite | `postresolve.c` — it needs the graph's cycle information, and `internal.h:3241` names that file as the home for rules that *"must refuse a pattern AT A PATTERN OFFSET"* and cannot be decided until the call graph exists |
| a call whose site can activate **more than once** | one member, many activations; which one is delivered has no answer the format may pick | same file, same pass — and being a graph question it also catches a delivering call inside a definition reached from a repeated site, which a lexical walk would miss |

Both run in postresolve's existing **ascending pattern offset** order
(`internal.h:3256`), so the leftmost site is named.

**Iterated capture is out of this row** (D87 rule 5). These refusals are
the honest answer while no mechanism exists, not a policy against one.

### 2.9 Provenance — a property of the parse, not of the node

**The format note's §2.12 says provenance is "a FIELD ON THE NODE". The
tree forbids it.** CITED, `internal.h:3247`: *"a module's parse hook is
the only place in this compiler that holds a pattern offset, and `Ast`
carries no position of any kind (PARSE-1)"*. The discipline is that a
position surviving to a later pass is an extra scalar on the SPECIFIC
node that needs it — and `A_LOOK.u.look.at` (`internal.h:745`) exists for
exactly that reason, its own comment saying *"IT EXISTS BECAUSE `Ast`
CARRIES NO POSITION OF ANY KIND (PARSE-1's own note)"*. A generic
`Ast.prov` would be a parallel mechanism on top of an invariant stated
twice, paid for by every node in every compile.

**So: provenance is a property of the SUB-PARSE and of the ASSIGNMENT
TABLE**, both of which must exist anyway.

1. **A scope stack on `Ctx`** — each sub-parse pushes `(file, line, the
   text's own base)`. `cx->pos` during a sub-parse is ALREADY an offset
   into the definition's own text, so a refusal raised inside a
   definition already carries the right offset; the stack supplies the
   file and line to report it against, and (r45sem M1) the third state
   `first_cap_pos`/`first_vmonly_pos` now need.
2. **`ctx_fail` is the one reporting site** (`compile.c:16-29`), so it is
   the one place that consults the stack. `pcrec_error`
   (`lib/pcrec.h:611-615`) gains the file/line the CLI prints beside the
   offset it already prints (`main.c:774`).
3. **Rule 7(c)'s duplicate-number error names BOTH sites** from the
   assignment table, which records provenance per assignment. The two
   sites may be in two files; the AST by then holds only numbers.

r45sem: *"§2.9 the best section; its PARSE-1 argument against
format_design §2.12 should be adopted."* The format note's §2.12 is
amended in the same change (§4).

**The node gains ONE thing**, and it is `A_LOOK`'s precedent exactly:
`u.cap.at`, the offset of the group's opening `(` — plus, after r45sem
S4, the **header's END offset** (§2.10 needs to REPLACE `(?<w>` and not
merely insert into it). `parse.c:839-864` already has `apos` in hand at
the assignment site.

### 2.10 `--emit-composed` — a text splice, and what it cannot do

**pcrec has no AST → pattern-text renderer**, and building one would have
to cover the entire language and would be a second answer to "what does
this AST mean" for the parser to disagree with — learnings §3's drift
hazard, and D87 rule 4's own reason for refusing an external renumberer.

**So `--emit-composed` splices the ORIGINAL TEXTS, driven by a position
list**: the caller's text with each group's number made explicit, then
`(?(DEFINE) … )` holding each definition's text, same treatment, in
closure order. Every insertion point is a `u.cap.at` and every number an
assignment-table entry.

**r45sem found four things wrong with revision 1's version of this, and
three change the mechanism.**

**B3 — explicit numbers do NOT fix by-name binding, and revision 1's
round-trip claim was false.** An injected definition's internal `(?&w)`
is re-bound by `pcrec_bref_resolve`'s name arm over the WHOLE composed
text (`mod_backrefs.c:683-687`, lowest number with that name) — which is
M2's naive-append collision reintroduced by the serializer. Two
libraries' `email` become two `(?<email=N>` wrappers in one text; without
`(?J)` that is a loud refusal. **RULED: `--emit-composed` renders every
by-name reference inside an injected definition NUMERICALLY** (`(?3)`,
`\g{3}`), which the assignment table already knows. Where a spelling
cannot be rendered numerically, it is a **counted, NAMED skip**, never a
silent one.

**S4 — the insertion is a REPLACEMENT of unknown length.** `?<N>` cannot
simply be inserted into `(?<w>…)`, `(?'w'…)` or `(?P<w>…)`: the result
must be `(?<name=N>…)`, which replaces the whole header. Hence the header
END offset in §2.9. `(?|…)` (branch reset) is recognised and its
alternatives' numbering follows D87 rule 7(e).

**S5 — modifier leakage across the splice is LIVE.** A top-level bare
`(?i)` is never restored (`internal.h:1557-1575`), so a definition
spliced after one inherits it: python `re` agrees the hazard is real
(`re.fullmatch('(?i)a(?:Q)','aq')` is a match), and the sub-parse's
re-seeded `mods` (§2.2) would disagree with the serialization. `(?x)` is
worse — `#` swallows the rest of the line. **Fix: an explicit modifier
reset on each spliced wrapper**, so the serialization means what the
composer meant.

**S6 — "it cannot drift from the parser" is FALSE as stated**, and this
note now says the weaker true thing: *the serializer emits no CONSTRUCT
the parser did not just accept from the same bytes, but bytes accepted in
one modifier context can mean something else in another (S5), so the
round trip is guaranteed only with the modifier reset and the numeric
rendering in place.* `\Q…\E` is a latent member of the same class and is
named here rather than discovered later.

**What survives, and it is the point of the mechanism:** no second
"AST → PCRE2 text" renderer exists, so there is nothing to drift from the
parser structurally; the `A == B` control recompiles the serialization
and compares the emitted PROGRAM and `caps[0..ngroups_A]` — **not**
`rx_info.ngroups`, which differs by design (B is handed text and counts
every group in it; §2.3.4 point 3 and §4's S9b).

---

## 3. The check and sabotage plan

Rewritten after r45chk, whose verdict was that revision 1's §3 "protects
the corpus in one direction only… but it does not prove the composer:
C0 is empty-vs-empty with its validating row deleted, W-2/W-5/W-7 compare
the composer to itself, and every composition cell is written by the
mechanism's author." Every one of those is answered below, and the two
that cannot be fully answered are named as residuals rather than closed.

Written against learnings §3 and memory `pcrec-check-design-lessons`:
**a control must not share a source with what it controls; a population
nobody counts is not a population; a witness that stopped reaching its
site is a green check measuring nothing ([MECH-REACH]).**

### 3.0 The two denominators, and why they differ

**MEASURED, and this closes a discrepancy revision 1 would have shipped.**
The corpus census counts every `.rxt` file; run.sh's own population
excludes one:

```
census (all files)                179 files / 3,265 blocks / 26,691 lines
tests/known_fail/k34_leftrec_giveup.rxt    1 file  /     3 blocks /     11 lines
                                  ---------------------------------------------
run.sh's population               178 files / 3,262 blocks / 26,680 lines
```

`run.sh:184-186` discovers with `-not -path "*/known_fail/*"`, so the
known-fail ratchet's own file is never dispatched. **26,691 − 11 = 26,680,
which is exactly the clean-corpus baseline below** — so the two
denominators are not an inconsistency but a derivable relationship, and
C2's denominator now has an independent derivation. Revision 1 would have
asserted 179 in both checks and the second would have been wrong.

**C1 asserts 179 / 3,265 / 26,691** (a parse differential can and should
read every file). **C2 and C3 assert 178 / 3,262 / 26,680.**

### 3.1 INV-COMPAT — that no existing file changes meaning

**PINNED BASELINES (r45chk item 6), from battery 3's `make test` corpus
section on code `0f5a98f`, main `4d12a81`** — the before-values, with
their provenance line, so "unchanged" is a comparison and not a hope:

| quantity | value | note |
|---|---|---|
| `cases passed:` | **26651** | |
| `cases failed:` | **29** | all in `tests/counterk/counterk.rxt`'s `((a)\|ab){4000}c` LOAD cell; solo that file is 1,634/0 |
| clean-corpus equivalent | **26,680 / 0** | = 26651 + 29; and = 26,691 − known_fail's 11 (§3.0) |
| `pattern-compile failures (distinct):` | **1** | the same load cell; clean **0** |
| `group cases pending-vm:` | **0** | |
| `size-log rows:` | **2877** | |
| parallel dispatch | **178 of 178 file workers** | §3.0 |
| libpcre2 §1 pcre2-only sweep | **69 blocks / 6,693 cells / 0 disagreements** | |
| libpcre2 §0 expansion table | **42 patterns / 2,646 cells** | |

The 29 failures and the 1 distinct compile failure are a KNOWN load cell,
not a red suite; they are pinned as-is so a comparison is exact rather
than approximately right. A step that changes them must say why.

**C1 — the parse differential, now THREE-WAY (r45chk F2).** Revision 1
claimed C1 was a control because "the two are in different languages by
different authors". True of the BODY; **false of the HEAD**, where the
seam ruling gives W1 exactly one parser, so C1 would have compared pcrec
to itself on W1.1's entire deliverable. The third parser already exists
in the tree:

| leg | source | covers |
|---|---|---|
| A | `pcrec --list-source` (§1.8) | head + body directives |
| B | `run.sh --dump` | body: blocks, directives, expectations |
| C | **`verify_rxt.py --dump`** (`parse_rxt`, `:113-182`, 10 kinds — python, a different author, already in the tree) | body: blocks, patterns, expectations |

A==B on their overlap and B==C on theirs, byte-identical over 179 / 3,265.
**The head still has no differential control and this note says so
plainly** rather than implying one: what covers the head is (i) the
grammar's own refusals, (ii) the field manifest below, and (iii) the fact
that on the corpus the head is EMPTY, which C1's row-order comparison
asserts.

**N2 — leg B's invocation must be the `$@` branch, not the default.**
C1 asserts **179**, but run.sh's no-argument branch discovers **178**
(`run.sh:184-186`'s `known_fail` exclusion, §3.0). So leg B is invoked
with an explicit file list — run.sh's `else` branch at `:187-195`, which
takes files or directories as arguments and applies no exclusion — and
the dump then covers all 179. Naming the branch matters because the two
differ by exactly the file whose absence C2 depends on: leg B and C2 run
the SAME script over DIFFERENT populations, deliberately, and a reader
who assumes one invocation would find the 179/178 split inexplicable.
**The field manifest's total-line assertion is the backstop**: if leg B
were ever invoked the default way, its line count would fall short of the
179-file census and C1 goes red on the count before anyone reads the
diff.

**C1's runtime is stated** (r45chk F12 asked): 179 `--list-source`
invocations plus one bash pass and one python pass. Each `--list-source`
is a parse with no compile, so this is bounded by the corpus's parse
cost, not its compile cost — but the number is UNMEASURED until the
binary exists, and §5 makes measuring it part of W1.1's acceptance rather
than assuming it is small.

**C1's FIELD MANIFEST (r45chk F3), because a differential can silently
stop comparing.** Both dumps are new code by one author; a sabotage that
drops one directive key from BOTH emitters leaves C1 byte-identical and
the differential quietly stops covering that directive. So C1 asserts, in
addition to byte-identity:

- the exact directive-key list per block kind (the 15 columns of §1.8);
- the exact field count per row (the header's own count — the table
  contract's HEADER TRUTHFULNESS check, `table_contract.md`);
- the exact TOTAL dump-line count, against the 179-file census.

Row **S-C11** plants "delete `encoding` from both dump emitters" and must
turn it red.

**C2 — the answer re-run.** run.sh reports the same four numbers
(`run.sh:1032-1044`), against the pinned baselines above. These are a
DIFFERENT partition of the expectations than C3's (r44-grammar G2: a
`perr` block and a live `g` line each record independently), and both
partitions are asserted. This is the check that catches a parse that is
faithful but routed differently.

**C3 — the oracle re-run.** `verify_rxt.py` reports the same verified
count and the same skip count. **The skip count is the load-bearing
half**, because H4 adds a new reason to skip: if the structural
composed-block test is loose, it skips blocks it should verify, and only
the COUNT catches that. r45chk F13(d): the file prints a per-file line
only `if skipped:` (`:387-388`) and no total, so **it gains a TOTAL
line** — without which C3's "same skip count" has nothing to read.

**But see §3.1.1 first: C3 is currently specified against a script that
does not run.**

### 3.1.1 N1 — wiring `verify_rxt.py`, the condition on W1.1

**MEASURED, and it is worse than "not wired".** The re-check's N1 found
that `tests/harness/verify_rxt.py` is executed by nothing in `make test`.
Confirmed, and then sharpened:

```
$ grep -rn 'verify_rxt' --include='*.sh' --include='Makefile' . | grep -v worktrees
Makefile:528:  # ... `tests/harness/verify_rxt.py` skips every cell in it —   <- A COMMENT
  (every other hit is a comment in another script)
```

The only Makefile mention is prose. Its one real consumer,
`tests/assertions/verify_pcre2.py`, imports it as a MODULE
(`verify_pcre2.py:54`, `importlib` on `harness/verify_rxt.py`, so that
"there is exactly one" `.rxt` reader) — **and that script has zero
Makefile hits either.** So neither the oracle run nor, through it, the
parser has a live consumer in `make test`.

**And its discovery is a ONE-LEVEL glob** (`verify_rxt.py:191`, `:195`):

```
files = sorted(glob.glob(os.path.join(a, "*.rxt")))          # a directory arg
files = sorted(glob.glob(os.path.join(BASE_DIR, "*.rxt")))   # the default
BASE_DIR = <repo>/tests/base                                 # :20
```

Not recursive. So the obvious wiring is the dangerous one:

| invocation | files | blocks | expectation lines |
|---|---|---|---|
| `verify_rxt.py tests` (the naive wiring) | **0** | 0 | 0 |
| `verify_rxt.py` (today's default, `tests/base`) | **40** | 763 | 3,603 |
| the corpus | 179 | 3,265 | 26,691 |

**`verify_rxt.py tests` verifies ZERO files and exits reporting
success**, because no `.rxt` file sits directly in `tests/`
(`ls tests/*.rxt` → 0). And the default covers **40 of 179 files and
3,603 of 26,691 expectation lines — 13.5%** — while C3 would claim to be
the oracle leg over "the corpus".

**This matters most because C3 is the SOLE detector for two sabotage
rows, and their populations are mostly outside its default scope:**

| row | its population | corpus-wide | in `tests/base` | reached |
|---|---|---|---|---|
| S-C4 | `# pcre2-only` marks | **571** | **44** | **7.7%** |
| S-C2 | subjects carrying a `\x` escape | 171 | 90 | 53% |

A sabotage planted outside `tests/base` would go undetected by the very
check named as its detector — [MECH-REACH] with the witness and the site
in different directories.

**A precision worth recording, because two numbers in this project
disagree and only one is operative.** r44-grammar G1 counts **636**
`# pcre2-only` marks; the exact-match count is **571**. Both are right:
G1 matched the line PREFIX, and the mechanism matches the stripped line
EXACTLY — `verify_rxt.py:121`, `if line.strip() == '# pcre2-only':`. The
65-line difference is lines beginning `# pcre2-only` with trailing text,
which the parser treats as ordinary comments. **S-C4's detector
population is the mechanism's 571, not the census's 636**, and a check
written against 636 would be asserting a number no code produces.

**What W1.1 must do (the manager's condition):**

1. **Wire it into `make test`** as its own target, over a **`find`-derived
   list** (not the one-level glob), with a **SHORT-LIST HARD FAIL** —
   [M5-SEAM]'s shape: if the discovered list is shorter than the census,
   the target is RED, so a discovery that silently narrows can never read
   as a pass. This is the one property the current script structurally
   cannot have.
2. **Pin its verified and skip totals** in §3.1's baseline table, under
   the same provenance line as the other baselines. **NOT MEASURED HERE
   AND DELIBERATELY SO**: `verify_rxt.py` is a script under `tests/`, and
   the HOLD forbids those by shape. The numbers are owed at W1.1's
   first run and are part of its acceptance, not of this note.
3. **C3's denominator comes from verify_rxt's OWN discovery**, never from
   run.sh's 178 / 3,262 / 26,680 carried across. The two populations are
   different by construction (verify_rxt has no `known_fail` exclusion and
   its own skip rules), and carrying a denominator between two checks that
   discover independently is the split-identity-gate lesson: a number that
   looks authoritative because it came from somewhere else.

**Until (1) lands, C3 is a specification, not a check** — and this note
says so rather than listing it beside C1 and C2 as though all three run.

**C0 — REDESIGNED, because revision 1's version could not fail
(r45chk F1, the blocker).** Revision 1 said "the composer reports the
size of the closure it bound, and for the corpus that number is 0 in all
3,265 blocks." But by DECIDED (6) the deferral flag is set only when
`--source` supplied a definition set, and by §1.1 the harness calls
`--list-source` only for a head-bearing file — MEASURED zero of 179. **So
on the corpus the composer is never invoked at all, and "0" is satisfied
by a composer that is absent, disabled, or hard-coded to return 0.**
Empty-vs-empty. Redesigned into two checks whose numbers come from
invocations that HAPPEN:

- **C0a (corpus)** — TWO assertions from TWO sources, and N4 asks that
  the note say which is which, because they are not the same kind of
  fact:
  - **W1's own counter**: `--list-source` was invoked **exactly 0 times**
    across the run. This is the harness reporting on its own behaviour —
    it can only catch the machinery calling out when it should not.
  - **The independent census**: the number of head-bearing files in
    `tests/` is **0**, derived by scanning the corpus rather than by
    asking the harness. This is what catches a future file growing a head
    without the rest of the machinery, and it holds even if the counter
    is broken.
  Neither alone is enough: the counter shares a source with the thing it
  counts, and the census cannot see a spurious invocation. Both are
  asserted, and a disagreement between them is itself a failure.
- **C0b (W1's fixtures)** — on every composed cell, the composer's
  reported closure (size AND order) is compared against the control's
  **RE-DERIVED** closure (DECIDED (8)). This is the comparison revision 1
  did not have, because revision 1 had the control consume the composer's
  report.

**F12 — "discharged by construction" is a diff argument, so it gets a
check.** run.sh's existing arm block is **hash-pinned**: any change to it
fails, so "the 13 arms are not touched" is asserted rather than
asserted-in-prose. And format_design §1.1's **32-keyword census becomes a
CHECK** rather than a one-time measurement — the appended arms change one
thing (lines that previously hit the catch-all now parse), the census is
what makes that safe, and a census can rot.

**N3 — the pin cannot be a LINE RANGE, because W1.1 edits inside it.**
Revision 2 pinned `run.sh:811-1015`. But W1.1 appends three block arms
and adds the `have_block` guard to six others — *inside that range* — so
a line-range hash would be broken by the very change it is meant to
protect, and the only way to "fix" it would be to re-pin, which discards
the protection entirely. **So the protected region is delimited by
explicit marker comments in run.sh** — `# --- BEGIN PINNED 13-ARM REGION
(w1 N3) ---` / `# --- END PINNED 13-ARM REGION ---` — and the check
hashes the text BETWEEN the markers. The new arms are appended AFTER the
END marker, and the guard lines are added inside their arms, which means
the guard edits are inside the region and DO move the hash: that is
correct and intended, since the guard is a change to the 13 arms and
should require a deliberate re-pin.

**The update rule lives in the check's own failure message**, not in this
note: when the hash moves, the message names the two markers, says that a
change inside them is a change to the arms R-COMPAT-1 protects, and
requires the re-pin to be a separate reviewed commit citing what moved.
That is the [ART-SIZE] lesson applied one level over — the rule that
governs a pin belongs where the pin is set, because that is the only
place a person looking at the failure will read.

**Where this is still weak, stated rather than buried.** C1's value on
the 179 is largely "three parsers agree that nothing happened", because
the corpus has no head and no composition. What protects the corpus is
that its code path is unchanged, and the checks that say so are the hash
pin, the census, and S-C7/S-C12. Every COMPOSITION check runs on
fixtures W1 itself writes — the author-writes-the-population shape — and
§3.2's answer is that the ORACLE is not W1's and §5's is that a D27
BLINDED author writes the composition cells at step .3.

### 3.2 The composer's checks

**W-1 — the textual EXPAND control, with BOTH populations floored.**
CITED, format_design §2.3.4: the control is valid where the append form
means what the composer means — no absolute numeric reference in any
body, no name collision between caller and closure. Outside it the
control **does not run and says so**.

Revision 1 counted and floored the INAPPLICABLE branch (right, and better
than the format note). **r45chk F5: nothing floored the branch where the
control actually RAN** — if every composed cell carried an absolute
reference or a colliding name, W-1 would skip everything and go green
having compared nothing (K35's shape). So:

> **W-1 publishes a MANIFEST: N cells run, M cells skipped, each skip
> with its reason. Both N and M are PINNED, and both are validated by a
> PLANT** — one that should move a cell from run to skipped, one the
> reverse. A run where N is 0, or where N+M ≠ the composed-cell count, is
> red.

The skip population has live witnesses by construction, and they are the
two shapes that FORCED D87: M1's `dd` = `(\d)\1` (absolute reference) and
M2's `(?J)` caller/closure collision. Both are already measured on both
oracles.

**W-1c — the `\12` octal cell (r45chk F11).** §2.2 argues `ncap` must be
swapped because it is read DURING the parse for PCRE2's
`\12`-is-a-backreference-iff-the-running-count-≥-12 rule
(`internal.h:1603`) — a MEANING failure, where revision 1's S-W6 tested
only renumbering. The cell: a caller with ≥ 12 groups binding a definition
whose body contains `\12`, **answer from libpcre2**. Under a correct
sub-parse the definition's `\12` is octal (its own running count is
below 12); under a leaked `ncap` it becomes a backreference, and the two
answers differ.

**W-2 — `A == B` across `--emit-composed`, RE-SCOPED (r45chk F4).**
Revision 1 called this a control; it recompiles the composer's own
serialization, so it catches parser/serializer drift and **structurally
cannot catch a wrong assignment**. Its claim is narrowed to exactly that,
in its own text, so a later reader does not mistake it for an oracle. It
compares the emitted PROGRAM and `caps[0..ngroups_A]`, explicitly NOT
`rx_info.ngroups` (which differs by design, §2.10) — and the check says
why in its own message so nobody "fixes" it. After B3 its population is
whole except for S4's unrenderable spellings, which are a counted NAMED
skip.

**W-3 — the hand-verified M1/M2 cells.** Pinned answers, measured on both
oracles, and the evidence D87 was ruled on. **They are not an independent
oracle** and the check says so rather than presenting them as
verification.

**W-8 — NEW, and it is the one whose expectation comes from outside
(r45chk F4).** On W-1's valid population, libpcre2's own
`PCRE2_INFO_CAPTURECOUNT` and ovector are read for the textual EXPAND and
compared against the composed artifact's `RX_NCAPS` and `caps`. The probe
is already wired
(`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`), the
population is exactly where the two are comparable, and — this is the
point — the expectation is derived from a different implementation of the
regex language rather than from pcrec's assignment table. This is the
check that can catch a wrong ASSIGNMENT, which W-2, W-5 and W-7 cannot.

**W-4 — Q7's residual, unchanged and named.** On the two populations D87
added mechanism for (absolute references, colliding names) no independent
oracle checks the answer. Accepted for W1 with the ratified trigger — the
first [LIB] entry that legitimately needs either — and W1's contribution
is to make the uncovered population COUNTABLE: W-1's manifest prints how
many cells were skipped and why, so the residual has a number.

### 3.3 The one-derivation checks, re-scoped

CITED, §2.7: the assignment table is the single source for `RX_NCAPS`,
the `rx_group_entry` array and `--emit-composed`. **r45chk F4 is right
that this makes most of these consistency checks INSIDE one derivation,
not controls**, and revision 1 presented them as the latter. Re-scoped:

| check | asserts | what it can and cannot catch |
|---|---|---|
| W-5 | `RX_NCAPS - 1` == the highest number in the emitted table | two renderings of ONE table agree. Catches a rendering bug; **cannot** catch a wrong assignment |
| W-6 | every `rx_group_entry` with non-NULL `.ref` has `number > rx_info.ngroups` | **a genuine STRUCTURAL assertion** — D61's promise, checkable by grep on emitted text, failing loudly in the direction that matters (a delivered slot intruding on `1..ngroups`) |
| **W-6b** | `nnames == count(.ref == NULL)` and `nentries == total rows` | **NEW (r45chk F6).** MEASURED: `grep -rn nnames tests/codegen/*.sh` returns NOTHING — `nnames` is asserted by nothing in the tree today, which is why revision 1's S-W5 had two named detectors that both could not see it |
| W-7 | `--emit-composed`'s numbers re-parse to the same table | a real check **of B1's parser**, mislabelled in revision 1 as a table check |
| **W-8** | libpcre2's CAPTURECOUNT + ovector vs the artifact | §3.2 — the only one whose expectation is external |

W-6, W-6b and W-8 are the three that can fail for a reason outside the
composer's own head. The others are kept because a rendering bug is real,
but their claims are now the narrow true ones.

### 3.4 The sabotage rows

Each must turn a NAMED check red. Per r45chk F13 and
`tests/mech/sabotages/CLAUDE.md`: **every row declares `SAB_REACH` /
`SAB_REACH_EXPECT` / `SAB_REACH_POP`** (a row whose detector is a
construct must declare its reach); the **`SAB_SUITES` arm is registered
BEFORE the rows that need it** (a closed vocabulary, R31 C11); and **rows
land in the SAME COMMIT as their code**, or the anchor tripwire (191
sites) goes red.

**Corpus rows** (format_design's S-C1..S-C8 plus W1's):

| row | plant | caught by |
|---|---|---|
| S-C1 | drop the last `g` line of one block | C2 (count), C3 |
| S-C2 | decode `\x41` as `x41` | C3 |
| S-C3 | let `flags` carry to the next block | C1 (the value is in the dump) |
| S-C4 | treat `# pcre2-only` as an ordinary comment | C3's skip count |
| S-C5 | make `frames-buffer=` block-scoped rather than positional | **C2** — CORRECTED from format_design's "(1) dump differential", which cannot catch it: pcrec never parses `frames-buffer=`, so it appears in only one dump. run.sh captures `cur_route` at each case push (`:931,941,951,961,990`), so the counts move |
| S-C6 | accept an unknown `features` name silently | C2 — a `perr` block flips |
| **S-C7** | **RESTORED (r45chk F1)** — make the composer bind a definition on a block that references none (treat a lexically-declared name as a file reference) | **C0a** — the invocation count is no longer 0. Revision 1 silently replaced this row with a different S-C7 while claiming the format note's rows all still applied; the row that would have validated C0 was the one deleted |
| S-C8 | assign a definition's re-based numbers from 1 instead of `base+1` | **nothing on the corpus** — no corpus file composes. Caught by W-1/W-8 on W1's fixtures. Stated so nobody reads the corpus's green as covering it |
| **S-C9** | emit the `pattern` column unescaped | C1 — and the check must **NAME the three tab blocks** (§1.8), since three rows out of 3,265 is exactly the size of finding a summary swallows |
| **S-C10** | `--list-source` reports the first `pattern` row's `line` wrong | **three cases, three DIFFERENT detectors** — see below |
| **S-C11** | delete `encoding` from both dump emitters | C1's field manifest (§3.1) |
| **S-C12** | make the head detector fire on a file whose first line is `pattern` | C1 and C2 — the row that guards the 179 (revision 1's mis-numbered S-C7) |

**S-C10's three cases, because the ruling's stated detector covers one.**
Verified by reading run.sh, not by argument:

| case | what happens | detector |
|---|---|---|
| line **too early** | the loop starts on a head line; no arm matches | the catch-all hard error (`run.sh:1016-1021`) |
| line **too late**, file with ONE block | the `pattern` line is skipped, `blocks_in_file` stays 0 | the **P-C2 floor** (`run.sh:1025`, "no pattern blocks parsed from file") — an existing check, better suited than the catch-all |
| line **too late**, several blocks | the first block's cases push with `have_block=0`; the next `pattern` line's reset discards them | **the `have_block` guard** (§1.7) — a case line with no open block is now a hard error. **Before the guard this case was silent**, detected only by C2's count |

The guard is what makes case 3 loud, which is why §1.7 measures it free
rather than asserting it. C2's count remains the second detector.

**A file with a head and NO `pattern` blocks** (the grammar permits it):
run.sh runs zero blocks and the **P-C2 floor fires on its own**. The spec
hunk states it, and states that "no pattern rows" and "the call failed"
are DISTINCT observables (different exit status and stderr), so the two
can never be confused.

**Composer rows:**

| row | plant | caught by |
|---|---|---|
| S-W1 | re-base `u.cap.no` but not `u.bref.refs` | W-1 on M1's `dd` cell — the measured M1 defect returning |
| **S-W2** | accept `(?R)` inside a bound definition (or re-base its 0) | **a NAMED witness cell** — r45chk F7: neither M1 (`(\d)\1`) nor M2 (`(?&w)`) contains `(?R)`, so revision 1's detector had a **zero-member population** ([MECH-REACH]/S107 exactly). The row declares `SAB_REACH_EXPECT` on the refusal's text and covers **all four spellings** (`(?R)`, `(?0)`, `(?00)`, `\g<0>`/`\g'0'`) |
| S-W3 | drop the `scope` predicate in the composer's re-resolution | W-1 on M2's `(?J)` cell |
| **S-W3b** | drop the discriminator so a caller-scope `(?&^.w)` is re-based | a B2 witness cell: `d` = `(?&^.w)x` in `^(?<w>a)(?&d)$`, answer from libpcre2 via the textual control |
| S-W4 | give the injected wrapper no number, shifting the definition's groups down one | W-1 (every composed cell's slots move) and W-7 |
| S-W5 | count injected names in `nnames` | **W-6b** — re-homed (r45chk F6). Revision 1 homed it on "W-6 and the C1 dump": C1's dump is over `.rxt` files and cannot see an artifact field, and W-6 moves neither of its terms |
| S-W6 | forget to restore one `RxtParseScope` field — specifically `ncap` | **W-1c**, the `\12` cell (meaning), plus the two-call-site numbering cell (renumbering). Revision 1 tested only the second |
| S-W7 | make the closure a plain walk with no visited set | the reported closure size vs C0b's re-derivation; a self-recursive definition doubles, a mutual pair does not terminate |
| **S-W8** | **REWRITTEN (r45chk F10)** — make the composer's REPORT disagree with the text | C0b. Revision 1 planted "let the control re-derive the closure", which under a correct composer AGREES — it planted independence and expected a red (S108's shape) |
| **S-W9** | drop the delivering-call live-capture arm | a delivering cell's slots read `-1,-1` on a DFA-selected artifact — the B1(a) defect, which is what the arm exists to prevent |
| **S-W10** | leave the callee's capture indices in `W` | a delivering cell's slots are wiped on return — B1(b) |

### 3.5 The identity gate and the abi

**D76's ritual at the four sites of §1.6, in one change** — and two
corrections from r45chk:

- **F8: the pin is per-ABI, not per-step.** `run_recursion_identity.sh:394-406`
  states the rule and the [OPT-4] note records abi 12 moving its pin five
  times inside one change. W1.3 and W1.4 both touch `emit_dfa.c` after
  W1.2's pin. **So the gate re-runs, and the pin moves if any emitted
  byte moved, at EVERY merge of the abi-13 change** (§5's exit criteria
  for .2, .3 and .4, not .2 alone).
- **F9: the gate is blind to the new field's VALUE.** (A) and (B) compare
  artifacts from a corpus with no composed file, so Frank's §6.3 rule
  ("no artifact ever carries a NULL name") is asserted by nothing. **A
  structural assertion over the corpus's own emitted artifacts**: every
  artifact's `rx_info.name` is non-NULL, and equals the prefix wherever
  no block name exists.

Comparison **(A)** is expected byte-identical (a stamped string above
`goto <prefix>_L0;`); if it moves, the step changed the program and the
step is wrong, not the gate. `make test-codegen` runs before delivering
any step that touches the four sites.

---

## 4. The spec deltas (D80)

W1's hunks land with the STEP that makes each observable, not all at the
end. A parser landing without its spec hunk is rejected on sight.

| hunk | file | lands with |
|---|---|---|
| **S1** HEAD and BODY; the four W1 head declarations; the head ends at the first `pattern`; the four lexical contexts; the block scalar as a property of the VALUE production | `rxt_format.md` | W1.1 |
| **S1b** **`--list-source`'s table** (§1.8): the 15 columns, the `kind` vocabulary, the rxt-escape rule for columns 4/5/15, **sectionless with the `#section`-arrives-with-`freq` trigger sentence**, AS-WRITTEN, and `--list-source --resolved` named-and-unbuilt | `rxt_format.md` + `cli.md` | W1.1 |
| **S3** the CELL notion, the `perr` one-cell rule, the summary's new quantities, **and the zero-`pattern`-block file's distinct observable** | `rxt_format.md` | W1.1 |
| **S10** `limits.md`'s "Handling an oversized artifact" item 1 stops being a forward reference | `limits.md` | W1.1 |
| **S11** `--source`, `--target`, `--lib-path`, `--emit-composed`, `--list-source`, and §1.5's output-naming rule | `cli.md` | W1.2 (`--emit-composed` with .3) |
| **S9** `rx_info.name`; **`nentries`**; the `abi` 12→13 sentence | `match_api.md` §6 | W1.2 — one of D76's four sites |
| **S9c** **NEW (B4)**: the `groups[]` SORT KEY becomes (ref-is-NULL, name, number); the primary's rows are a genuine PREFIX; §6's caller algorithm is unchanged over `groups[0..nnames)`; `nentries` is how a caller reaches injected rows. **Plus N6**: `match_api.md:1504` says `groups`/`nnames` stay `NULL`/`0` *"for every pattern until module `named-groups` is enabled"* — under composition an injected definition's names populate `groups[]`, so that sentence becomes REACHABLE-FALSE and is corrected here. **It is the same staleness shape as the `nnames` comment §1.6 already fixes** — it too carries a live verification (`'(?<g>a)'` still refuses) that keeps reproducing while the claim it supports rots, because the module is GATED rather than absent. Two instances of one pattern, in one struct's documentation | `match_api.md` §6 | W1.3 |
| **S2** "Composition": the AST-level model, D87 rule 7(a)-(j), lexical-scope-wins with qualification, the visited-set closure, the five namespaces, **DECIDED (7)'s file-namespace rule and `(?&self)`**, and that a composed block's oracle is necessarily `pcre2` | `rxt_format.md` | W1.3 |
| **S2b** the three pattern extensions with the "no legal PCRE2 pattern changes meaning" constraint and §1.4's measurement; the three registry rows | `docs/spec/` + `--list-syntax` | W1.3 |
| **S9b** D61 made concrete by its first producer: `ngroups`/`nnames` are the PRIMARY's own; **the delivered REGION starts at `ngroups+1`, and the definition's WRAPPER sits there, so the first delivered GROUP is at `ngroups+2`** (N5; Q-W1, r45sem's correction — the region's start and the first readable group are two different numbers and revision 2.1 conflated them in one sentence); `RX_NCAPS` may move across library versions while `1..ngroups` holds still; and the difference between `--source` composition and handing composed TEXT to plain `-p` | `match_api.md` §2/§5 | W1.3 |
| **S2c** "Delivered results": the scope path, first-set-wins within a path, **the two non-deliverable shapes as CALL-GRAPH activation bounds**, and the `__typeof__` sentence | `rxt_format.md` | W1.4 |

**Amendments to `format_design.md` itself**, in the same change (already
partly landed at `9506e8d`):

- §4.2 — the [DD-11] table is a **LISTING** interface (Q-W3, ruled);
- §1.1 — S-C5's detector corrected to the answer re-run;
- §2.7 — the stale `abi 11 / emit_dfa.c:1310`, now 12 → 13 with all four
  sites line-cited;
- **§2.12 — provenance is NOT a field on the node** (r45sem: adopt §2.9's
  PARSE-1 argument);
- **§2.3.3/§2.3.4 — the wrapper's number and the zero offset** (Q-W1,
  pending Frank);
- **§6.0 — piece-rule member (vi)**, `(?R)`/`(?0)` inside a definition
  (Q-W2, pending Frank).

`docs/guide/` gains one page — "compiling from a `.rxt` source" — and
points at the spec without restating it (D80).

---

## 5. Steps and merge points

Four steps, a merge after each. **r45gram 9's correction to the stated
reason:** .2 precedes .3 not because of code dependencies (the composer
sits inside `compile_driver`, which every `-p` invocation traverses) but
because of **END-TO-END TESTABILITY** — a composed file has several blocks
and therefore builds nothing without a `target`, so without .2 there is no
way to RUN the composer through `--source` at all.

### What can be measured BEFORE building (D77)

Already measured, under the HOLD:

- the three spellings are still free at `3372e1e` (§1.4) — the one
  measurement that could have killed B1/B2/B3;
- the abi is **12**, from three independent sites (§1.6);
- **0** corpus files have a head; **0** lines begin with whitespace;
- **0 of 26,691** case lines precede a `pattern` line, so the
  `have_block` guard is free (§1.7);
- the corpus is **179 files** but run.sh dispatches **178**, and
  **26,691 − 11 = 26,680** reconciles the two exactly (§3.0);
- **3** corpus blocks carry a literal tab in their pattern text, all
  three where the tab is the thing under test (§1.8);
- `rx_group_entry.ref` exists and is emitted `NULL` today
  (`emit_dfa.c:1190-1191`);
- `nnames` is asserted by **nothing** in `tests/codegen/*.sh` (§3.3).

Not measurable before building, and named: whether the `RxtParseScope`
list is complete (S-W6's row exists for that), and C1's runtime (W1.1's
acceptance measures it rather than assuming it).

### The steps

**[DD-13b.W1.1] — the head grammar, `--list-source`, and the corpus
identity proof.**
Builds F1, F2's types, F3's `--source`/`--lib-path`/`--list-source`,
F12's three block arms + `features only` + the `have_block` guard + the
C1 dump, F14's structural skip + skip TOTAL + `--dump`. No composer, no
targets, no abi change.
**Acceptance, with N1 as an explicit CONDITION:**
- **`verify_rxt.py` is WIRED into `make test`** over a `find`-derived
  list with a short-list hard fail, and its verified/skip totals are
  measured and pinned in §3.1's baseline table under the same provenance
  line (§3.1.1). Without this, C3 is a specification and S-C2/S-C4 have
  no detector — so this is a gate on the step, not a nice-to-have;
- C1 three-way byte-identical over **179 / 3,265 / 26,691** with the
  field manifest asserted, leg B invoked through the `$@` branch (N2);
- C2 equal to §3.1's pinned baselines over **178 / 3,262 / 26,680**;
  **C3 against its OWN discovery's denominator**, never run.sh's;
- C0a's two assertions — W1's invocation counter at 0 AND the independent
  head-bearing-file census at 0 (N4);
- S-C1..S-C7, S-C9..S-C12 each turn their NAMED check red;
- the arm-block hash pin (between its BEGIN/END markers, N3) and the
  32-keyword census run as checks;
- **C1's runtime measured and recorded**; `make strict` clean.
Merge.

**[DD-13b.W1.2] — targets, `rx_info.name`, `nentries`, the abi ritual,
H11.**
Builds `target … [with]`, `config` composition and `from`, the output
naming rule, F11's `rx_info.name` + `nentries`, F13's prefix-taking
driver, run.sh's target build path.
Acceptance: N targets → N artifacts, N prefixes, one `rx_info.name`;
§6.3's three-config file compiles three ways and the three agree on the
block's cases (a free control); abi **13** at all four sites; F9's
`.name` assertion over the corpus's artifacts; identity gate (A)
byte-identical, **(B) re-pinned to this step's last src commit**;
`make test-codegen` green.
Merge.

**[DD-13b.W1.3] — the composer, the three extensions, `--emit-composed`.**
Builds F4-F7, F10's infrastructure, the sub-parse, re-basing, the
`PendingRef` discriminator, qualification, the assignment table,
provenance, the B4 sort key + S9c, H2b's control, H2c's round trip.
Acceptance: W-1 (with its **N-run / M-skipped manifest pinned and
plant-validated**), W-1c, W-2 (re-scoped), W-3, W-5, W-6, W-6b, W-7,
**W-8 (libpcre2-derived)**; the M1/M2 cells reproduce their measured
answers; C0b compares the composer's report against the control's
re-derivation; S-W1..S-W8 each turn a NAMED check red with `SAB_REACH*`
declared; C0a still reports 0 on the corpus; **the gate re-runs and the
pin moves again**.
Merge. **A D27-BLINDED author writes the composition cells at this
step's merge** (r45chk's population list is the manager's, not the
author's — they are handed the landed spec hunks and a cut extract of
format_design §2.3 + D87 rule 7 + §6.0, never the axis list).
**This is the step to schedule the focused re-check on.**

**[DD-13b.W1.4] — delivery.**
Builds B3's semantics end to end: F9's live-capture arm, F8's `W`
exclusion, `scope` on injected groups, `.ref` populated, delivered slots
above `ngroups`, and the two call-graph refusals.
Acceptance: W-6 on every composed artifact; **S-W9 and S-W10 each turn a
delivering cell red** (the two B1 mechanisms, each with a witness that
reaches it); both refusals fire with the construct named, each with a
reaching witness (a recursive definition with a delivering declaration; a
delivering call at a site the graph says can activate twice); §6.1's
`mail.rxt` builds with `rx_info.name == "from_line"`, `ngroups == 0`, and
its delivered slots above — **the first at `ngroups+2`** (Q-W1);
**the gate re-runs and the pin moves a third time**.
Merge. [V-I] then has its interface (§2.8) and W1 is closed.

---

## 6. Open questions

Eight points are marked **DECIDED** inline. Six are routine and need no
ratification unless the manager disagrees: (1) W2/W3 keywords refused as
"not in this build"; (2) module ownership B1→`named-groups`,
B2/B3→`recursion`; (3) a `-D` prefix macro rather than a generated shim;
(4) a structural, counted composed-block skip; (5) `kind` = the
declaration name; and (7) a block's `name` lives in the FILE namespace
with `(?&self)` for a self-call (the manager's ruling on r45sem S3).
Two are rulings already received and recorded: (6) the deferral, and
(8) the control re-derives the closure (r45chk F10).

**Two questions remain, both Frank's, both parked with the manager:**

**Q-W1 — the definition's wrapper takes an assigned number, so the
control's derived offset is zero (§2.6).** r45sem ratified the mechanism
("the mechanism argument is SOUND… an id space is a second key"; PCRE2
parity CITED-true twice) and added the correction: **it IS
caller-observable** — one permanently unset slot per definition, every
delivered number shifted, so the first delivered group is at
**`ngroups+2`**. Recommendation: adopt, with S9b stating the wrapper
consumes a slot, and amend format_design §2.3.3/§2.3.4.

**Q-W2 — `(?R)`/`(?0)`/`(?00)`/`\g<0>` inside a bound definition (§2.5).**
Recommendation: **refuse for W1**, raised at the sub-parse (nothing later
can distinguish it from M4's other zeros), covering all four spellings,
and added to format_design §6.0 as piece-rule member (vi). r45sem's
counter-reading is recorded and reserved: D87 rule 1's "absolute
references are LOCAL" applies verbatim to 0, whose local meaning after
injection is the wrapper, so re-basing 0 would be rule 7(i) executed
consistently. **The reason to refuse is that the RULING is missing, not
that the meaning is unclear.**

**Two residuals, named rather than closed:**

- **Q7 (ratified)** — on the two populations D87 added mechanism for, no
  independent oracle checks the answer. W-1's manifest makes the
  uncovered population countable; the trigger is the first [LIB] entry
  that needs an absolute reference or a colliding name.
- **The composition population is written by the mechanism's author.**
  Every composition check runs on fixtures W1 writes. The mitigations are
  real but partial: W-8's expectation comes from libpcre2, W-1's control
  is a third independent path, and a **D27-blinded author** writes the
  cells at .3's merge. It is the weakest joint in the plan and it is
  better for the re-check to hit it than for step .3 to.

---

## 7. [DD-13b.W1.1] — the step brief

Written so the hold's lift starts CODE, not planning. W1.1 and W1.2 are
CHARTERED (manager, on the r45 re-checks); .3 waits on Frank's
Q-W1/Q-W2 and .4 on a one-critic re-check of §2.8 after this revision.
This section is W1.1 only.

### 7.1 Build order, and why it is this order

Each item is landable and checkable before the next begins; nothing here
touches the composer, `target`, `rx_info` or the abi.

| # | build | why here |
|---|---|---|
| 1 | **`--list-source`'s TSV** (§1.8) and the `RxtSource` types — head grammar, the four W1 declarations, the four lexical contexts, block scalars, `config` cascade/composition, `target` PARSING (not building) | everything else in .1 reads its output. Landing the dump first means items 2-5 are written against a real artifact rather than a spec |
| 2 | **the rxt-escape on columns 4/5/15** and its round trip | the three tab blocks (§1.8) are live in the corpus, so item 3's differential is WRONG without this — build it before the check that would silently pass |
| 3 | **C1 leg A + the field manifest** — pcrec's own dump plus the key-list/field-count/total-line assertions | the manifest is what makes legs B and C comparable at all |
| 4 | **run.sh: the three block arms, `features only`, the `have_block` guard, the BEGIN/END pin markers** (§1.7, N3) | the guard is measured free (0 of 26,691), and the markers must exist before the pin check can |
| 5 | **C1 leg B** — `run.sh --dump`, invoked through the `$@` branch (N2) | needs item 4's arms to have something to dump |
| 6 | **WIRE `verify_rxt.py`** — the `make test` target over a `find`-derived list with the short-list hard fail; then **C1 leg C** (`--dump`), the composed-block structural skip, and the skip TOTAL | **chk N1, the CONDITION on this step.** It is item 6 and not item 1 because the wiring's acceptance is a measurement (its verified/skip totals) that only exists once items 1-5 make the corpus dumpable |
| 7 | **C0a, the hash pin, the 32-keyword census as checks**; the sabotage rows S-C1..S-C7, S-C9..S-C12 | the rows land in the SAME COMMIT as the code they detect (F13) |

### 7.2 Acceptance — the numbers, all pinned before the step starts

**Denominators (§3.0), and they differ on purpose:**

- C1 asserts **179 files / 3,265 blocks / 26,691 expectation lines**;
- C2 asserts **178 / 3,262 / 26,680** (run.sh excludes
  `tests/known_fail/k34_leftrec_giveup.rxt`; 26,691 − its 11 = 26,680);
- **C3 asserts verify_rxt's OWN discovery**, never either of the above.

**Before-values, from battery 3 on code `0f5a98f` / main `4d12a81`:**

| quantity | value |
|---|---|
| `cases passed:` / `cases failed:` | **26651 / 29** (the 29 are `tests/counterk/counterk.rxt`'s `((a)\|ab){4000}c` load cell; solo 1,634/0) |
| clean-corpus equivalent | **26,680 / 0** |
| `pattern-compile failures (distinct):` | **1** (same cell; clean **0**) |
| `group cases pending-vm:` | **0** |
| `size-log rows:` | **2877** |
| parallel dispatch | **178 of 178 file workers** |
| libpcre2 §1 / §0 | **69 blocks / 6,693 cells / 0 disagreements**; **42 patterns / 2,646 cells** |
| verify_rxt verified / skipped | **OWED** — measurable only once item 6 wires it; part of this step's acceptance, not a pre-existing pin |

**Measured facts this step must not move** (each already taken, §5):
0 head-bearing files; 0 leading-whitespace lines; 0 of 26,691 case lines
before a `pattern` line; 3 pattern lines carrying a literal tab; 0 of the
32 candidate keywords in first-token position.

**Green means, exactly:**

1. C1 three-way byte-identical over 179/3,265, field manifest asserted,
   leg B through the `$@` branch;
2. C2 equal to the pins above over 178/3,262/26,680;
3. C3 runs at all (it does not today), over its own discovery, with a
   short list HARD FAILING, and its two totals pinned;
4. C0a's two independent assertions both 0 (§3.1's N4 split);
5. every sabotage row turns its NAMED check red — S-C1..S-C7, S-C9,
   S-C10 (all three cases), S-C11, S-C12; **S-C8 is excluded and the
   reason is written in the row**, not left to inference;
6. the arm-block hash pin and the keyword census run as checks;
7. **C1's runtime measured and recorded** — unmeasured today, and stated
   as an output of this step rather than an assumption;
8. `make strict` clean; the spec hunks S1, S1b, S3, S10 land in the same
   change (D80).

### 7.3 What W1.1 does NOT touch

No composer, no `--emit-composed`, no delivery, no `target` BUILD path,
no `rx_info` change, **no abi bump** — so the identity gate is untouched
and comparison (A)/(B) are not in this step's exit criteria. The first
abi movement is W1.2's, and from there the gate re-runs and the pin moves
at every merge of the abi-13 change (F8).

### 7.4 The two risks worth naming before starting

- **C1's runtime is unknown.** 179 `--list-source` invocations plus a
  bash pass plus a python pass. Each is a parse with no compile, so it is
  bounded by parse cost — but if it lands badly the differential becomes
  something a lane skips, which is worse than a slower check. Measure it
  at item 3 and report before item 6.
- **Item 6 is the step's only irreversible-feeling piece**: wiring a
  previously-dead oracle over the whole corpus will, on its first run,
  either be clean or reveal expectations that were never checked against
  python `re` outside `tests/base`. **That is a discovery, not a
  regression**, and it must be reported as one — 139 files have never
  been through this oracle. If it produces failures, they are pre-existing
  and the right response is a triage list for the manager, not a fix
  inside W1.1.
