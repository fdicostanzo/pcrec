# The `pcrec` command-line interface

This is the **spec**, not the design record, per `docs/spec/CLAUDE.md`'s
charter: every flag below was checked against `cli/main.c` (this worktree's
build, `cli/main.c:1-632`) AND a live run of `build/pcrec`, and disagreements
between the two are reported as drift rather than silently resolved in the
help text's favour. `docs/spec/tuning.md` ([SPEC-1.3]) owns the `-f`/`-fno-`
optimization-axis family in full; this document states only that the family
exists and how it composes. `docs/spec/limits.md` ([SPEC-1.1]) owns the
budget NUMBERS; this document states only which flag sets which one.
`docs/pcre2_compliance.md` owns per-construct compliance detail; this
document's `--features` section states only the module roster and each
module's shipped status.

## 1. Compiling a pattern

```
pcrec [options] -o OUT.c [--] 'PATTERN'
```

A bare invocation needs exactly one pattern and an output path; everything
else defaults. `--` ends option parsing, which is how a pattern that starts
with `-` is passed (`cli/main.c:159`, case5 `tests/cli/run_cli_tests.sh`)
— any other leading-`-` argument is diagnosed as an unknown option
(`cli/main.c:345-350`) rather than treated as the pattern.

### `-o FILE` — where the C goes

Writes `FILE` (the `.c`) and a matching header `FILE` with its extension
swapped to `.h` (`cli/main.c:601-611`: if `FILE` ends `.c` the header is
`FILE` with `.c` → `.h`; otherwise `.h` is appended whole). The header's
name, stripped to its basename, becomes `pcrec_options.header_name` (D38's
naming point — the field itself is `lib/pcrec.h:pcrec_options`, documented
at spec-tier in `docs/spec/match_api.md` §8.2), which is what the `.c` file
`#include`s.

**`-o -` is a distinct mode, not a filename**: it prints ONE self-contained
`.c` to stdout and writes no header at all — "self-contained" means
literally that, verified live (`build/pcrec -p rx -o - 'a(b|c)+d'` emits the
full `PCREC_RX_ABI_H` block and the matcher inline, no `#include "...h"`
line) and pinned as a structural assertion
(`tests/cli/run_cli_tests.sh` case1: "-o - produces no header #include").
It is the idiom several suites reuse to compare two artifacts byte-for-byte
without the comparison tripping over an emitted `#include` naming a
different basename (case9/case10's own note, `tests/cli/CLAUDE.md`).

### `-p PREFIX` — the symbol prefix

Every generated identifier is `<PREFIX>_search`, `<PREFIX>_match`, etc.
(the five-to-eight entry points `docs/spec/match_api.md` §3/§10 name in
full — read there for what a caller actually calls, not here). `PREFIX`
must be an ordinary C identifier: non-empty, at most
`PCREC_MAX_PREFIX_LEN` = **60** characters, first character a letter or
`_`, every later character alphanumeric or `_`
(`src/core/compile.c:49-56`, the bound named at `src/core/limits.h:38`).
A prefix outside that grammar is refused with a diagnostic naming "prefix"
(`src/core/compile.c:161-163`), never silently truncated or mangled —
verified live at all three boundaries and pinned at
`tests/cli/run_cli_tests.sh` case3 (60 chars accepted, 61 rejected, a
leading digit rejected, empty rejected). Default: `rx`.

### `-e ENCODING`, `--encoding=ENCODING` — subject encoding

**Byte-only today.** The only encoding that compiles is `byte` (the
default); `utf8` is a real, registered name that is refused by name with
the milestone that delivers it, not by an unknown-name error
(`cli/main.c:113-124`, resolved through the encoding registry at
`src/gen/enc/enc.h` rather than hand-mapped in the CLI — see
`cli/CLAUDE.md`'s `[M5-SEAM]` note for why that used to be two hand-written
tables that could drift). Verified live: `--encoding=ascii` is an unknown
encoding (D58 renamed it `byte`, one spelling, one namespace member) and
`--encoding=utf8`/`-e utf8` both refuse naming milestone M5, never writing
any C (`tests/cli/run_cli_tests.sh` case13). The encoding is a **per-compile
scalar** (D58 ruling 2) — two patterns in one binary may use different
encodings, since there is no process-global to set; `docs/spec/match_api.md`
§8.2 states the library-level rule this flag is the CLI spelling of.
`-e byte` and the bare default are BYTE-IDENTICAL artifacts (case13), not
merely equivalent-behaving ones — the default IS the explicit request.

### `-i` — ASCII case-insensitivity

Folds case at PARSE time into the automaton (`opt.flags |= PCREC_CASELESS`,
`cli/main.c:165`); no runtime cost, ASCII letters only (D23). Composes with
`--` and with a pattern that itself looks like a flag
(`tests/cli/run_cli_tests.sh` case9).

### `--emit-main` — a runnable binary

Appends a standalone `main()` taking the subject as `argv[1]`
(`opt.flags |= PCREC_EMIT_MAIN`, `cli/main.c:164`). The emitted program's
own exit code is a **separate vocabulary from `pcrec`'s own** (§3 below is
about the CLI's exit codes, not the emitted program's): `0` on match, `1`
on no-match, `2` on a usage error (wrong argc), and `3` on an honest
give-up — `PCREC_ERR_STEPS`/`_FRAMES`/`_WORK` printed as `steps`/`frames`/
`work` rather than a fabricated match, pinned with two witness patterns
driven to their own budget/capacity ceiling plus non-firing controls at
`tests/cli/run_cli_tests.sh` case15 (K21's fix). What the `main()` body
prints and its argv contract are otherwise out of this document's scope —
`docs/spec/match_api.md` or a future codegen note owns the C-level detail
(survey row C6).

### `--no-captures` — capture-free artifact

Emits `RX_NCAPS 1` and forces the DFA engine (`opt.flags |=
PCREC_NO_CAPTURES`, `cli/main.c:170-171`) — the pre-M4.5 pure-DFA artifact
shape for a group-bearing pattern. Captures are ON by default; this flag is
what recovers the old behaviour.

### `--engine=E` — `dfa` | `vm` | `auto` (default `auto`)

**Do-or-die for `dfa` and `vm`**: a request the pattern cannot honour
REFUSES, never silently downgrades (`cli/main.c:262-272` parses the value;
the refusal itself is asserted in `src/opt/select_engine.c`, not the CLI).
Verified live: `--engine=dfa --features recursion -o ... '(a)(?1)'` refuses
naming that the pattern requires captures and suggesting `--no-captures` or
dropping `--engine=dfa`. `--engine=vm` additionally disables the DFA
prefilter, so the VM derives the whole span independently — the property
that makes it usable as a cross-check against the DFA rather than an echo
of it (R21 E-6). The refusal-plus-control pair is pinned at
`tests/recursion/run_recursion_diff.sh` §4 (`--engine=dfa` on a recursive
pattern refuses by name; a spliceable call still compiles under it — two
different reasons a call-bearing pattern can or cannot take `--engine=dfa`,
both asserted).

**[SEL-1] (2026-08-28) `auto` HAS ONE EXCEPTION TO DO-OR-DIE, AND IT IS
ABOUT A CAP RATHER THAN A CONSTRUCT.** Every refusal above is decided from
the pattern's AST, before any automaton exists. A DFA build can additionally
overflow a compile-time CAP (state count, table entries, the K7 subset-
element budget — `docs/spec/limits.md`, `docs/spec/tuning.md` §2.11) that no
AST-level check can see in advance, and under `auto` — with `-fprefilter`
not also requested — that overflow is a SELECTION OUTCOME: the compile
falls back to the VM (`RX_ENGINE_WHY` names the cap), and if the overflow
was in an auto-selected prefilter rather than the chosen engine itself, the
prefilter is dropped (`docs/spec/tuning.md` §2.5) instead of the whole
compile refusing. `--engine=dfa` and `-fprefilter` are UNCHANGED — both
still refuse with the same "pattern too complex for the DFA engine" text as
before this row, because a caller who named the engine or forced the
prefilter explicitly asked for the machine that cannot be built. See
`docs/spec/tuning.md` §2.11 for the mechanism and the cost bound.

### `--step-budget=N`, `--work-budget=N`, `--fno-step-budget`

Two SEPARATE counters on the emitted VM — step (backtrack resumptions) and
work (forward-only progress the fail label does not see) — each returning
its own typed give-up code on exhaustion. `--fno-step-budget` is ONE
existence gate for BOTH counters; there is deliberately no
`--fno-work-budget` (D49). Defaults, the exact codes, and the worked
give-up example are `docs/spec/limits.md` §2/§3.1 — this document states
only that `--step-budget=N`/`--work-budget=N` (`cli/main.c:56-64`, parsed
at `cli/main.c:273-295`) override them per compile, positive integers only,
diagnosed otherwise.

### `--warn-emit-bytes=N` — advisory size warning

**[OPT-4] (2026-08-29).** Warn on stderr when an ACCEPTED artifact exceeds `N`
total emitted bytes. Default `250000`; `0` disables. A warning, never a
refusal — the compile succeeds and the artifact is written either way — and
NOT a tuning axis: it selects nothing and is stamped nowhere.

Unlike `--max-emit-code-bytes` / `--max-emit-bytes`, which are raise-only so
they cannot be used to manufacture a refusal, this option may be **lowered**:
a warning cannot fail a build, so tightening it is a project's own business.
The line it prints names the unroll factor and its reason, the prefilter
language, and a pointer to `tuning.md` — see `limits.md` for the full text and
the reasoning.

### `--backtrack-frames=N`

Raises the emitted resume-stack (and its trail) capacity above the
compiled-in default, clamped at an internal ceiling when left at
auto-sizing (`cli/main.c:67-69`, parsed at `cli/main.c:296-306`, `1..
1,000,000`). The array is a LOCAL of the search entry — i.e. C stack, per
the flag's own diagnostic text — which is exactly the fact
`docs/spec/limits.md` §5 (K33) is about; the numbers and the caller-facing
remedy (the `_in` entries) live there, not here.

### `--features LIST` — the module gate

Comma-separated module names, a frozen named set (`std1`), `all`, or
`none` (`cli/main.c:85-94`, installed at `cli/main.c:379-386` before
anything consults the gate — composes with every mode, not just a
compile). An explicit `--features` always wins over the bare default;
a bare invocation resolves through `PCREC_DEFAULT_FEATURES`, which is
`std1` today (D37, `src/parse/enabled.c:80-85`). `std1` = {`classes`,
`modifiers`} — the frozen set's contents never change after it ships;
`--features std1` compiles identically forever, and `--features none` is
the permanent escape hatch reproducing the pre-`std1` bare behaviour
verbatim (case14, `tests/cli/run_cli_tests.sh`). An unknown module name is
refused BY NAME, listing the real vocabulary
(`cli/main.c:380-385`; verified live: `--features bogus_mod` answers
"unknown module 'bogus_mod' (names are --list-syntax's module column;
also 'all', 'none', or a named set: std1)"). A construct outside the
enabled set is refused with `requires module 'X'` — D26's tier-3 discharge
in full (verified live: a bare invocation on `(?<name>a)` answers
"requires module 'named-groups'"; `--features named-groups` accepts it).

**The 17 module names** (confirmed live,
`build/pcrec --list-syntax | cut -f4 | sort -u`), each with its shipped
status measured the same way
(`build/pcrec --list-syntax | awk -F'\t' '$4!="" {print $4,$16}' | sort -u`
— every module reads uniformly `built` or `unbuilt` across its own rows,
no module is split):

| module | status | one line |
|---|---|---|
| `classes` | **built** (in `std1`) | `\d`/`\s`/`\w`/POSIX classes and kin |
| `modifiers` | **built** (in `std1`) | `(?i)`/`(?m)`/`(?s)`/`(?x)` inline option groups |
| `assertions` | **built** | `\A`/`\Z`/`\z`/`\b`/`\B`/`(?m)`/`\G`/`\K` |
| `named-groups` | **built** | `(?<name>…)`/`(?'name'…)`/`(?P<name>…)` |
| `atomic-groups` | **built** | `(?>…)` and the possessive quantifier suffixes |
| `backrefs` | **built** | `\1`..`\9`, `(?P=name)`, `(?J)`/DUPNAMES |
| `lookaround` | **built** | `(?=X)` `(?!X)` `(?*X)` and lookbehind |
| `recursion` | **built** | `(?N)`/`(?&name)`/`(?R)`/`\g<…>` subroutine calls |
| `branch-reset` | not built | `(?\|…)` |
| `callouts` | not built | `(?C…)` |
| `comments` | not built | `(?#…)` |
| `conditionals` | not built | `(?(cond)yes\|no)` |
| `extended-classes` | not built | nested/set-operation character classes |
| `misc` | not built | scattered rarer constructs |
| `quoting` | not built | `\Q…\E` |
| `unicode-props` | not built | `\p{…}`/`\P{…}` (recogniser-only, no producer — D37) |
| `verbs` | not built (per-name; the 12 alpha-spelled lookaround verbs are attributed to `lookaround`/`assertions` instead, D71 item 3) | `(*PRUNE)`/`(*COMMIT)`/etc. |

For what any one construct under a module actually does today —
per-construct divergences, `OK-LIMITED` caveats, the ones with known
issues — `docs/pcre2_compliance.md` is the authority, not this table; this
table exists so a reader does not have to walk that whole page to learn
the roster. `--list-syntax`'s own `built` column (§2 below) is the live
source these numbers were read from and stays the thing to re-run rather
than trusting a table that can go stale.

### The `-f`/`-fno-` tuning-axis family

A dozen-odd flags (`-fno-possessify`, `-fno-revdet`, `-fno-counter`,
`--unroll=K`, `-fno-length-prune`, `-fno-prefilter`/`-fprefilter`,
`-fno-altcls-merge`/`-fno-altcls-factor`, `-fno-atomic-discharge`,
`-fno-splice-calls`, `-fno-tiered-entry`, `-fno-premul-table`,
`-fno-offset-skip`, `-fno-anchored-dfa`, `-fno-size-term`)
deliberately do **not** appear in `--help` (D47.3:
these are testing and tuning axes, not user features — `cli/CLAUDE.md`
states the reasoning per flag). Each denies one optimization strategy
(mostly byte-identity-safe controls for a differential; `-fno-splice-calls`
and `-fno-atomic-discharge` can change which ENGINE a pattern gets, and
`-fprefilter` is do-or-die like `--engine` itself). `--work-budget=N` is
NOT part of this family despite sharing the `--flag=value` shape — it is a
real generation axis on the give-up-code footing (§4/§8 above), which is
why it alone is documented in `--help`. Full per-flag semantics, the
force-vs-deny distinction, and the byte-identity/engine-selecting split:
`docs/spec/tuning.md` ([SPEC-1.3]).

## 2. Listing surfaces

Six TSV dumps, each a query taking no pattern and no `-o` (mixing either
in is refused). Five answer from pcrec's own registries; the sixth,
`--list-source`, reads a FILE named by its own value. The column CONTRACT itself — `#`
comments, a header row naming every column, append-only columns, resolve
by header name never position — is `docs/spec/table_contract.md`,
adopted by every table surface at birth; this section states only what
each listing answers.

### `--list-syntax`

Every non-base construct pcrec knows, one row per spelling: `kind`,
`selector`, `syntax`, `module`, `feature`, `flavours`, `engines`,
`status`, `diag`, `flags`, `expect`, `note`, `roadmap`, `quantifiable`,
`class_expect`, `built`, `family` — 17 columns, confirmed live (verified
this pass: header exactly matches). `status`/`roadmap` are PCRE2/base-
grammar facts (is this real syntax, is it planned/never); `built` (D65) is
orthogonal — has THIS construct's owning module's producer actually
landed, derived live by driving the construct through a gate-forced-open
doorway call, never hand-declared. Confusing the two once cost a lane a
whole review pass (`docs/CLAUDE.md`'s wave-E incident record) — `built`
exists precisely so a reader does not have to re-derive it from `status`
plus a module's shipped-or-not memory. `family` (D71 item 3) names the
canonical spelling a row is grouped under, empty when the row is its own
family; grouping is index-layer only and never changes a row's own
dispatch identity (R6).

### `--list-verbs`

The `(*VERB)` names pcrec recognises, in PCRE2's own two case-selected
tables (`table`, which of the two; `unknown`, what pcrec says for a name
neither table has); `forms` records what libpcre2 ACCEPTS, measured, not
declared.

### `--list-families`

One line per FAMILY (D71 item 3) — the rows sharing a `--list-syntax` key
— with `built` ANDed over every member (a family reads built only if
EVERY spelling does) and `members` listing every spelling, canonical
first. Strictly fewer lines than `--list-syntax` (a family view collapses
rows; measured floor 60 against the row view's own floor, case10). Takes
no `--flavour`: a family is a grouping OF rows, so filtering members would
make the family line's own `built` mean something different per
invocation (`cli/main.c:517-523`'s own comment states the reasoning).

### `--list-axes`

The optimization-axis registry ([CHK-2], `docs/spec/registry.md` §6 — the
fourth surface): one row per (axis, candidate), in the emitter's own
preference order, with the candidate's stamp macro/value, its
`-fno-*`/`-f*` deny/force bit and CLI spelling, and a one-line
description. Reports what THIS BUILD thinks its own tuning machinery is
— `registry.md` §6 states the boundary in full and points at the
independent-side check. Takes no `--flavour` (the same reason
`--list-families` doesn't: it is not a claim about PCRE2 syntax).

### `--list-definitions`

The replacement/definition table ([DD-11.2], D85, `docs/spec/registry.md`
§9 — the fifth surface): one row per (row, definition-array entry),
`kind`/`selector`/`syntax` matching the owning row's own `--list-syntax`
line so the two dumps join, `order` (1-based, dense per row), `predicate`
(the option-scope tag's own name — a closed vocabulary, never
hand-authored prose), `definition` (the core-syntax substitution text, a
human-readable template for an operand-parameterized entry, the row's own
`syntax` restated for an identity entry, or the literal `<builder>` for an
AST-operand entry), and `applies` (`active` or `identity`, read directly
from the entry's kind — no row uses `identity` yet; see `registry.md` §9
for the rows still pending a `RegRow` of their own before they can carry
one). Reports what the table THINKS a construct's substitution is
— `registry.md` §9 states the boundary in full (it is not evidence the
substitution parses cleanly or matches the same strings, which are
separate checks). Takes `--flavour`, unlike `--list-verbs`/
`--list-families`/`--list-axes`: it walks the same `RegRow`s
`--list-syntax` does, so an unfiltered dump would print a definition for
a construct `--list-syntax --flavour=X` says does not exist under that
flavour.

### `--list-source FILE`

The `.rxt` SOURCE file named by the option's own value, AS WRITTEN: one
row per head declaration and per pattern block, in FILE ORDER, fifteen
columns. **The full column table, the `kind` vocabulary, the escaping
rule and the "as written, never resolved" contract are
`docs/spec/rxt_format.md`'s** — this section does not restate them.

It takes its file as the option's VALUE rather than as the bare
positional argument, because that slot belongs to the PATTERN: a query
that quietly reinterpreted it would make `pcrec --list-source 'a(b|c)'`
try to read a file named after a regex.

Exit status distinguishes two outcomes a caller must not confuse: a file
that PARSES but declares no pattern block prints its head rows and exits
0 (a pure library file is exactly that shape), while a file whose head
does not parse exits 1 with a diagnostic naming the file, the line and
the construct.

`--list-source --resolved` — the file with its `config` composition and
`with`/`from` cascades APPLIED — is named here and is not built.

### `--explain SYNTAX` / `--flavour NAME`

`--explain` is the one surface that is a CROSS-SOURCE query rather than a
plain dump: it prints the registry ROW's declared attribution beside what
the LIVE doorway parser actually answers for that text, and compares them
— agreement is the expected, common case; a disagreement is a pcrec
DEFECT surfaced (exit 3, below), not a bad question. `--flavour` restricts
either query; only `pcre2` exists today (a second flavour is future work,
SR-7).

### `--count-groups [--] PATTERN`

Runs the real parser, parse only, nothing emitted, and prints the ending
capturing-group count. A pattern pcrec refuses is refused here with the
identical diagnostic a compile would give (`cli/main.c:468-494`; verified
live: `a(b)(c(d))` → `3`).

### `--probe-ask WANT [--] CONSTRUCT`

Internal/test-only by its own source comment (`cli/main.c:12-15`): "the
CLI and the test suite are its only consumers... not part of the public
surface." Drives one construct doorway once at ask level
`claim`/`verdict`/`result` and reports the parser cursor before and after
— survey row A11 flags this explicitly so a future spec author does not
accidentally document it as public surface. Mentioned here only for
completeness; `tests/spec_mod0/CLAUDE.md` and `docs/testing.md` are its
real home.

## 3. Diagnostics

### Exit codes

Verified live this pass, each command shown:

| exit | when | verified with |
|---|---|---|
| `0` | success — a compile that wrote its files, or a query that answered | `build/pcrec -p rx --emit-main -o out.c 'a(b\|c)+d'` |
| `1` | usage error, compile refusal, or a query that could not be answered | `build/pcrec 'a(b'` (unclosed group) → "missing closing ) for group"; `build/pcrec --bogus-flag` → "unknown option"; `build/pcrec -o /nonexistent_dir/out.c 'a'` → the OS's own `fopen` error |
| `3` | **`--explain` DISSENT ONLY** — the registry's declared attribution disagrees with what the live doorway parser actually answers (`cli/main.c:577-586`, the sole `return 3` in the file) | not currently reproducible against the shipped table — `tests/cli/run_cli_tests.sh` case11 measures and asserts **zero** dissents over the full row/query sweep (81 row blocks, 19 queries, all agree), which is the intended steady state; exit 3 exists for the day that stops being true |

**These are `pcrec`'s own exit codes.** They are a completely separate
vocabulary from an `--emit-main` binary's exit codes (§1 above:
0/1/2/3 there mean match/no-match/usage-error/give-up on the EMITTED
program, not on `pcrec` itself) and separate again from a give-up CODE
(`PCREC_ERR_STEPS` etc., `docs/spec/match_api.md` §4, a C-level return
value from a generated function) — three numbering schemes that happen to
share small integers and nothing else. A caller scripting against `pcrec`
should not confuse any of the three.

### The D26 tiers, stated caller-side

`docs/dev/decisions.md` D26 rules pcrec's compatibility standard in four
tiers; restated here for what a CALLER should expect from a diagnostic,
not the reasoning behind the ruling (informational reference only, per
this tier's charter):

- **What a pattern MATCHES**, for syntax pcrec implements, is EXACT. A
  wrong match is always a bug.
- **Whether a construct is REAL PCRE2 syntax and which module owns it**
  is EXACT. Naming a module that will never implement a construct, or
  rejecting syntax PCRE2 accepts, is a defect.
- **The WORDING, error number, and PCRE2's OWN offset** for something
  pcrec does not implement are NOT promised. `requires module 'X'`
  discharges this obligation in full — a caller should match on the
  module name, never on the sentence around it.
- **pcrec's OWN offset is still exact**, and this is the one place D26's
  "don't chase the wording" advice is easy to over-read: a diagnostic's
  offset must blame the construct pcrec itself actually recognised,
  checked against pcrec's OWN convention, never against what PCRE2 would
  have reported at the same input (D26's tension addendum,
  `docs/dev/decisions.md`, the `[[.a[.b.].]` worked example — pcrec
  reports the nested opener it actually walked into, offset 4; PCRE2
  reports offset 9, pointing at the input's end, which is neither right
  nor wrong for pcrec to differ from). A caller may rely on the offset
  pointing at a real position in the pattern that pcrec's own parse
  reached; they may not rely on it matching PCRE2's number for the same
  input.

### `requires module 'X'`

The full, permanent discharge of tier 3 for a construct pcrec recognises
but has not built a producer for (verified live throughout §1's
`--features` examples above). It is not a promise of a timeline; check
`--list-syntax`'s `built` column or the module table in §1 for shipped
status.

## 4. What the CLI does not do

Stated plainly rather than left for a stranger to discover by trial:

- **No runtime.** `pcrec` is an ahead-of-time compiler; there is no mode
  that interprets a pattern against a subject without first generating
  and compiling C. `--emit-main`'s appended `main()` (§1) is the closest
  thing to a quick try, and it still goes through a real `cc` invocation.
- **No multi-pattern compilation units.** Every invocation compiles
  exactly one pattern to one artifact. A unit that can hold several
  named, cross-referencing patterns is `[V-E]`, `docs/dev/plan.md:581`,
  **STATE:not-started** — confirmed at this commit, not shipped in any
  form.
- **No `--lib FILE`.** A library of reusable named subpatterns a pattern
  could call by name is `[LIB]`, `docs/dev/plan.md:580`,
  **STATE:not-started**, and its own plan row records that its place
  relative to the project's roadmap has not even been ruled yet ("planned
  but I don't know that I'd put them on the spine," Frank, 2026-08-24).
- **`--emit-ir` ships; `--emit-dot` does not.** `--emit-ir` (§1's `-h`
  text and `cli/main.c:440-466`) prints the VM program listing and is a
  real, working query, verified live. A DOT-format graph dump was
  promised alongside it in `APPROACH.md` §6 but was never built; the
  combined row is `[DD-8]`, `docs/dev/plan.md:1069`, still
  **STATE:not-started** at this commit — `docs/spec/table_contract.md`'s
  own "TO BE CONSIDERED" note about `--emit-ir`'s tabular sections
  (whether they should adopt the table contract) is therefore current,
  not stale: it is explicitly waiting on `[DD-8]` reopening, and `[DD-8]`
  has not. `--trace` (an instrumented, non-default matcher variant) DOES
  ship and is unrelated to either row — see §1.

## Revision history

- 2026-08-25 ([SPEC-1.2]): first version, written against `cli/main.c` at
  this worktree's branch point (`0e2b23d`) plus a live `build/pcrec` from
  a clean `make -j4`. Folds in [SPEC-1.7] (diagnostics, §3) and [SPEC-1.8]
  (modules, §1's `--features` table) as sections rather than separate
  files, per this row's brief.
