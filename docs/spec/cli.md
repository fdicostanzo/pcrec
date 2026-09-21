# The `pcrec` command-line interface

This is the **spec**, not the design record, per `docs/spec/CLAUDE.md`'s
charter: every flag below was checked against `cli/main.c` (this worktree's
build, `cli/main.c`) AND a live run of `build/pcrec`, and disagreements
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
with `-` is passed (`cli_parse`'s `!strcmp(a, "--")` arm, case5
`tests/cli/run_cli_tests.sh`) — any other leading-`-` argument is diagnosed
as an unknown option (`cli_parse`'s `a[0] == '-' && a[1]` arm, the last one
before the pattern operand) rather than treated as the pattern.

### `--version` — print the pcrec version and exit

Prints one line, `pcrec 0.1.0-beta`, to stdout and exits 0 — verified live
(`build/pcrec --version`). The string is `PCREC_VERSION` (`lib/pcrec.h`,
D115, [REL-1.4]), a semver product version that names THIS TOOL and is
**independent of `abi`** (`docs/spec/match_api.md` §6): `abi` versions one
artifact's emitted scaffolding and bumps far more often than a release
does, while `PCREC_VERSION` changes only at a release. The same string is
stamped in every emitted artifact's provenance line, beside the abi digit
(`docs/spec/match_api.md` §6) — `pcrec --version` and a generated file's
own header always agree on which pcrec produced it.

Parsed identically to `-h`/`--help` (`cli_parse`'s adjacent arm): it sets a
flag rather than printing and exiting inside `cli_parse` itself, because
that function has a second caller — a `.rxt` source's `config` block's own
`pcrec --version` must not print and exit 0 in the middle of a `--source`
compile. `cli_extras_clean`'s existing byte-span refusal (no clause of its
own needed) already refuses it there, exactly as it refuses a `config`
block's own `-h`.

### `-o FILE` — where the C goes

Writes `FILE` (the `.c`) and a matching header `FILE` with its extension
swapped to `.h` (`main`'s `strcmp(hpath + len - 2, ".c")` derivation: if
`FILE` ends `.c` the header is
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

**Two encodings compile: `byte` (the default) and `utf8`** ([M5.0] stage 2).
An unknown value is refused with the registry's rendered menu
(`--encoding=ascii` is unknown — D58 renamed it `byte`, one spelling, one
namespace member); a real name with no backend would refuse by its own name,
which is what `utf8` did through stage 1 and no longer does. Both are resolved
through the encoding registry (`src/enc/enc.h`) rather than hand-mapped in
the CLI — see `cli/CLAUDE.md`'s `[M5-SEAM]` note for why that used to be two
hand-written tables that could drift.

**Under `-e utf8`** the pattern's subjects are matched as UTF-8 text: a
character is one to four bytes, `.` and a class match a whole character, `\x{…}`
accepts code points above `0xFF`, and an ill-formed byte sequence in the
subject **matches nothing** — there is no validation pass and no error return
(the byte-wise UTF-8 automaton simply has no path through malformed input;
`docs/design/utf8_design.md` §2.6, ruled 2026-09-04). One consequence a caller
must observe: **`startpos` passed to `<prefix>_search` must be a character
boundary of the encoding.** A non-boundary start gets a defined but
PCRE2-divergent answer; `<prefix>_next_pos` is the supported way to produce a
valid `startpos`, and the find-all loop of `docs/spec/match_api.md` §3.1
already uses it.

**Under `-e byte`** a code point above `0xFF` written as `\x{…}` is a compile
error (as PCRE2's `options=0` gives error 134); a NEGATED class or `.`
complements within `[0, 0xFF]`, unchanged from before this milestone.

The encoding is a **per-compile scalar** (D58 ruling 2) — two patterns in one
binary may use different encodings, since there is no process-global to set;
`docs/spec/match_api.md` §8.2 states the library-level rule this flag is the
CLI spelling of. `-e byte` and the bare default are BYTE-IDENTICAL artifacts
(`tests/cli/run_cli_tests.sh` case13), not merely equivalent-behaving ones —
the default IS the explicit request.

### `-i` — case-insensitivity, and WHICH FOLD is the encoding's

Folds case at PARSE time into the automaton (`opt.flags |= PCREC_CASELESS`,
`cli_parse`'s `-i` arm); no runtime cost — no flag, no branch and no `tolower()` in
the emitted matcher (D23). Composes with `--` and with a pattern that itself
looks like a flag (`tests/cli/run_cli_tests.sh` case9).

**WHICH characters fold is a property of `-e`** ([M5.0] stage 4, DD-1). The
two relations DISAGREE rather than nest, so no clamp derives one from the
other and each encoding names its own:

| under | a literal or a range folds by | so `(?i)k` matches | and `(?i)\xe9` matches |
|---|---|---|---|
| `--encoding=byte` (default) | the 52 ASCII letters, and nothing else | `k`, `K` | `\xe9` only |
| `--encoding=utf8` | Unicode DEFAULT SIMPLE case folding | `k`, `K`, U+212A KELVIN SIGN | U+00E9, U+00C9 |

Both are libpcre2's own answers at the matching option word — `PCRE2_CASELESS`
for `byte`, `PCRE2_UTF|PCRE2_CASELESS` for `utf8` — measured, not inferred.

Four consequences worth stating because each one surprises:

- **A caseless class can reach far outside what it wrote.** `(?i)[a-z]` under
  `--encoding=utf8` matches U+212A and U+017F LATIN SMALL LETTER LONG S,
  neither of which is anywhere near `a-z`. The fold is computed over CODE
  POINTS before the byte lowering, so a partner's distance is irrelevant.
- **A caseless single character can consume a variable number of bytes.**
  Fold partners have different encoded lengths, so `(?i)k` matching U+212A is
  a match of length 3. Nothing in the API changes; the span simply reports it.
- **A NAMED byte set does not gain Unicode partners.** `\d`, `\w`, `\s` and
  the POSIX brackets are ASCII-alphabet sets, so `(?i)[[:lower:]]` does NOT
  match U+212A at either encoding, while `(?i)[[:lower:]k]` does — the literal
  `k` beside it is what reaches. That is PCRE2's own split without
  `PCRE2_UCP`, which pcrec has no axis for. Likewise `\p{...}`: under `-i`,
  `\p{Lu}`/`\p{Ll}`/`\p{Lt}` are `\p{L&}` and every other property is
  unchanged, so a property set is never folded on top of that substitution.
- **A caseless BACKREFERENCE is the one place the fold reaches the artifact.**
  Its operand is subject text, so it cannot fold at compile time; under `utf8`
  the emitted matcher carries the ~1,500-entry fold map (about 26 KB of table
  text, outside the emitted-CODE cap by D84's own definition, and present only
  in an artifact that HAS a caseless backreference) and folds each character
  through it. That entry is internal to the artifact — it is called from the
  matcher, not by a caller — and carries its own contract comment in the
  emitted `.c`; `docs/spec/match_api.md` §3.1.1 specifies `<prefix>_next_pos`,
  the residual entry a caller does call.

The fold data is pinned at Unicode 16.0.0 (`third_party/ucd-16.0.0/`), the
reference oracle's version, exactly as the property tables are. A libpcre2 at
a different Unicode version will disagree about recently-assigned code points;
that is a re-measurement event under D26, not a defect.

### `--pattern-esc` — the pattern operand in `.rxt` escaped form

**[DD-13b.W23.3]** Takes the PATTERN OPERAND as double-quoted, escaped
text and decodes it before compiling. The vocabulary is the `.rxt`
format's own subject vocabulary and no other — `\"` `\\` `\n` `\t` `\r`
`\f` `\v` `\xHH` — decoded by the very function that decodes a
`pattern-esc` block, so this flag, `--source` and `--list-source` cannot
drift into three tables that only agree today.

```
pcrec --pattern-esc -o out.c '"a\tb\x41"'     # compiles the 4 bytes a<TAB>bA
```

- **The operand must be double-quoted**, quotes included, and an operand
  that is not is refused by name. An unescaped `"` inside the text, a
  trailing backslash, an unknown escape, and `\x` without exactly two
  hex digits are each refused with what was wrong; every refusal exits
  `1` before anything is compiled or written.
- **`\x00` is refused, naming K9**: the compile entry takes no pattern
  length, so a NUL-bearing pattern would compile as its prefix and report
  success. The diagnostic states the lifting trigger
  (`rx_info.pattern_len`) rather than leaving the limit silent.
- **It composes with everything and changes only how the OPERAND is
  read.** `--` still ends option parsing, and the artifact's own header
  comment carries the DECODED pattern. In a mode that takes no pattern
  operand (`--source`, any listing surface) the flag has nothing to
  decode and is inert.
- `docs/spec/rxt_format.md`'s `pattern-esc` production is the format half
  and owns the escape table itself.

### `--emit-main` — a runnable binary

Appends a standalone `main()` taking the subject as `argv[1]`
(`opt.flags |= PCREC_EMIT_MAIN`, `cli_parse`'s `--emit-main` arm). The emitted program's
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
PCREC_NO_CAPTURES`, `cli_parse`'s `--no-captures` arm) — the pre-M4.5 pure-DFA artifact
shape for a group-bearing pattern. Captures are ON by default; this flag is
what recovers the old behaviour.

### `--engine=E` — `dfa` | `vm` | `auto` (default `auto`)

**Do-or-die for `dfa` and `vm`**: a request the pattern cannot honour
REFUSES, never silently downgrades (`cli_parse`'s `--engine=` arm parses the value;
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

### `--tune=N` — the SPEED-VS-SIZE DIAL

**[OPT-DIAL] (2026-09-16).** An ordinal in `-2..+2`, `0` the default, or
one of five mnemonic aliases accepted on equal terms —
`min-size`/`size`/`balanced`/`speed`/`max-speed` (`cli_parse`'s `--tune=`
arm, parsing both spellings through `pcrec_tune_parse`, `src/core/tune.c`,
so the CLI and the artifact's stamp cannot drift; since [REVW.4] wave 4 the
refusal's own MENU of aliases is rendered from that same table by
`pcrec_tune_names` rather than hand-typed beside it). Sets a GROUP of the
`docs/spec/tuning.md` §2 axes from one pinned policy table instead of a
caller composing them one flag at a time; the full table, the reason
codes and the acceptance are `docs/spec/tuning.md` §5.

**A negative value needs the `=` form.** Verified live:

```
$ build/pcrec -p rx --tune -2 -o /tmp/x.c -- 'abc'
pcrec: --tune takes its value with '=' (--tune=-2, --tune=min-size)
$ build/pcrec -p rx --tune=-2 -o /tmp/x.c -- 'abc'
$
```

`--tune -2` is two tokens whose second begins with `-`; the separated
form is refused BY NAME rather than accepted by look-ahead, which would
make `--tune -o out.c` mean something nobody typed. The aliases have no
leading dash and are the preferred spelling for exactly this reason.

**Out of range is refused, never clamped.** Verified live:

```
$ build/pcrec -p rx --tune=3 -o /tmp/x.c -- 'abc'
pcrec: --tune wants -2..2 or one of min-size, size, balanced, speed, max-speed (got '3')
```

A clamp would let a caller believe they had asked for something the
artifact does not have.

**Every position answers identically**, over the whole corpus — the same
D46 observable/forceable principle every axis in this document's tuning
family carries, at the dial's own coarser grain. `<PREFIX>_TUNE`, a
closed five-token stamp, is emitted on every artifact regardless of
engine, including at `balanced` (verified live: `build/pcrec -p rx -o -
-- 'abc' | grep RX_TUNE` reads `#define RX_TUNE "balanced"`).

**The `tune` config-block directive.** A `tune` line in a `.rxt`
`config`/`target` block takes the identical vocabulary, per D93's own
framing that a config block's directive set is the format's named axes
(`docs/spec/rxt_format.md`). Its precedence against an explicit CLI
`--tune=` is stated in this document's own file-wins section below —
`tune` is **not** a second exception to it.

### `--step-budget=N`, `--work-budget=N`, `--fno-step-budget`

Two SEPARATE counters on the emitted VM — step (backtrack resumptions) and
work (forward-only progress the fail label does not see) — each returning
its own typed give-up code on exhaustion. `--fno-step-budget` is ONE
existence gate for BOTH counters; there is deliberately no
`--fno-work-budget` (D49). Defaults, the exact codes, and the worked
give-up example are `docs/spec/limits.md` §2/§3.1 — this document states
only that `--step-budget=N`/`--work-budget=N` (`cli_parse`'s own arms for
each) override them per compile, positive integers only,
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
auto-sizing (`cli_parse`'s `--backtrack-frames=` arm, `1..1,000,000`). The array is a LOCAL of the search entry — i.e. C stack, per
the flag's own diagnostic text — which is exactly the fact
`docs/spec/limits.md` §5 (K33) is about; the numbers and the caller-facing
remedy (the `_in` entries) live there, not here.

### `--features LIST` — the module gate

Comma-separated module names, a frozen named set (`std1`), `all`, or
`none` (`cli_parse`'s `--features` arm takes the value; `main` installs it
through `pcrec_enabled_set_spec` before anything consults the gate — composes with every mode, not just a
compile). An explicit `--features` always wins over the bare default;
a bare invocation resolves through `pcrec_default_features`, which is
`std1` today (D37, `src/parse/enabled.c:80-85`). `std1` = {`classes`,
`modifiers`} — the frozen set's contents never change after it ships;
`--features std1` compiles identically forever, and `--features none` is
the permanent escape hatch reproducing the pre-`std1` bare behaviour
verbatim (case14, `tests/cli/run_cli_tests.sh`). An unknown module name is
refused BY NAME, listing the real vocabulary
(`main`'s `pcrec_enabled_set_spec` call renders the refusal; verified live:
`--features bogus_mod` answers
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
| `quoting` | **built** | `\Q…\E` literal quoting, including inside a character class |
| `unicode-props` | **built (partial)** | `\p{…}`/`\P{…}` — the Unicode GENERAL CATEGORIES and PCRE2's derived families ([M5.0] stage 3) plus the SCRIPTS, bare and under `sc=`/`scx=` ([M5.0] stage 5). See the note below for exactly which names |
| `verbs` | not built (per-name; the 12 alpha-spelled lookaround verbs are attributed to `lookaround`/`assertions` instead, D71 item 3) | `(*PRUNE)`/`(*COMMIT)`/etc. |

**`unicode-props` is the first module in this table to ship a PROPER SUBSET
of its own construct, so "built" needs a sentence.** Two families compile.

**The GENERAL CATEGORIES, 45 names**: the seven one-letter codes
(`C L M N P S Z`), all 30 two-letter ones (`Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No
Pc Pd Ps Pe Pi Pf Po Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn`), the cased-letter
set under both its spellings (`L&`, `Lc`), `Any`, and PCRE2's own
`Xan Xps Xsp Xuc Xwd`.

**The SCRIPTS, 171 values** — every `Script` value the Unicode Character
Database declares at the pinned version except `Katakana_Or_Hiragana`, which
is excluded because no libpcre2 this project can reach accepts it either.
Each answers to its long name, its four-letter code and any deprecated alias
the UCD lists (`\p{Greek}`, `\p{Grek}`; `\p{Inherited}`, `\p{Zinh}`,
`\p{Qaai}`), in three namespaces:

| spelling | denotes |
|---|---|
| `\p{Greek}` | `Script` **union** `Script_Extensions` |
| `\p{sc=Greek}`, `\p{Script=Greek}` | `Script` alone |
| `\p{scx=Greek}`, `\p{Script_Extensions=Greek}` | the same set as the bare spelling |

**The bare spelling is NOT the `Script` property**, and that is PCRE2's
behaviour rather than a choice pcrec made: U+0342 COMBINING GREEK
PERISPOMENI has `Script=Inherited` and `Script_Extensions={Greek}`, and
`\p{Greek}` matches it while `\p{sc=Greek}` does not — measured against
libpcre2 10.42, 10.46 and 10.48, all three agreeing.

Either separator works (`sc=Greek`, `sc:Greek`) and the prefix is
case-insensitive and loosely matched exactly as the value is, so
`\p{S c r i p t _ Extensions = G-r-e-e-k}` is the same property. There is no
`gc=` namespace, because libpcre2 has none: a general category is spelled
bare or not at all.

Every name works at both `--encoding=byte` and `--encoding=utf8`, negated as
`\P{X}` or `\p{^X}` (the two compose: `\P{^X}` is `\p{X}`), and inside a
character class. Under `--encoding=byte` a property is clamped to the
Latin-1 universe, which is PCRE2's own 8-bit non-UTF behaviour — for 154 of
the 171 scripts that leaves the empty set, and a pattern whose class is
empty compiles to a matcher that never matches.

**Names libpcre2 has that this does not ship REFUSE, and refuse as the
MODULE's gap rather than as unknown names** — the boolean-property
(`\p{Alphabetic}`) and `Bidi_Class` (`\p{bc=L}`) families are declined by
design. A name no libpcre2 has (`\p{Foo}`, block spellings like
`\p{InGreek}`, `\p{Hrkt}`) refuses too, and on the one-letter axis — where
pcrec's table is exhaustive — it says so as an unknown NAME with no module
clause, because no module will ever implement it. A KNOWN axis with an
unknown value (`\p{sc=Nosuch}`) takes the module's gap wording, since pcrec
cannot tell a misspelling from a value it has not got.

**Under `-i`, `\p{Lu}`, `\p{Ll}` and `\p{Lt}` are `\p{L&}`** and every
other property is unchanged — including every script, measured exhaustively
over the code points that participate in the case-fold relation at all,
which is where a difference could only ever appear. That substitution IS the caseless rule for a
property, and no fold is applied on top of it: [M5.0] stage 4's Unicode
closure ships for literals, ranges and classes (see `-i` above) and a
property set is deliberately not one of its customers. The discriminating
cell is U+0345, an `Mn` that folds with Greek iota — `(?i)[\p{Lu}x]` does not
match it, while `(?i)[\p{Lu}k]` does match U+212A because the literal `k`
beside the property is what folds.

**Six names exceed the emitted-artifact size cap under `--encoding=utf8`
at default settings** — `\p{C}`, `\p{Cn}`, `\p{L}`, `\p{Xan}`, `\p{Xwd}`
and (from stage 5) `\p{Unknown}` in all three of its namespaces — and refuse
with the ordinary "pattern too large" diagnostic. Their `\P` forms compile;
so does every other script, the largest at about a third of the cap. `-fno-premul-table` compiles all of them;
`docs/dev/known_issues.md` K53 has the cause and the cure.

**The property tables are pinned at Unicode 16.0.0** (`third_party/
ucd-16.0.0/`), which is the reference oracle's version. A libpcre2 whose
Unicode version differs will disagree about recently-assigned code points;
that is a re-measurement event under D26, not a defect.

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
`-fno-offset-skip`, `-fno-anchored-dfa`, `-fno-size-term`,
`-fno-scan-edge`, `-fno-start-pinned`, `-fno-alt-island`,
`-fno-cls-fold`, `-fno-startpos-guard`)
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

**`-fcomments` / `-fno-comments` share the family's spelling and are not a
tuning axis** ([EMIT-VERB], D112; `tuning.md` §2.24). They control the
emitted artifact's HUMAN COMMENTARY and nothing else. The default is
`-fno-comments`: an artifact carries only its ESSENTIAL comments — the
generated-by line naming pcrec AND THE ABI and echoing the pattern, and
the shared `PCREC_RX_ABI_H` type block's doc-comments. `-fcomments` restores
the rest
(the orientation block, the table legends, the per-label role text), which
is what you want when you are going to READ the artifact. Deny wins over
force, so `-fcomments -fno-comments` is comment-free.

Nothing else changes with them: the object file is byte-identical, the
comment-excluded source size is identical, every emitted `#define` is
identical, and the emitted-size caps — which are defined on comment-excluded
bytes — cannot see the flag at all, so no pattern is rescued or refused by
it. They are absent from `--help` for the family's own reason. A `config`
block or a `--source` target may set either spelling, and an explicit flag on
the command line wins (§the `--source` precedence rule below).

### `--source FILE` — compiling from a `.rxt` source ([DD-13b.W1.2])

`pcrec --source FILE -o OUT` compiles the `target` declarations of a `.rxt`
source file (`docs/spec/rxt_format.md`). It is a COMPILE MODE, not a listing
surface: it honours every compile flag in §1 and it writes artifacts.

**It takes no pattern argument.** The file's `pattern` blocks are the
patterns; accepting a positional pattern as well would leave "which one did
I build" answerable two ways. A `--source` invocation carrying a pattern, or
composed with any query surface of §2, is refused.

**WHICH ARTIFACTS GET BUILT.** The file's `target <prefix> = <definition>`
lines, in file order, one artifact each — or, when the file declares no
`target` at all and holds exactly ONE UNNAMED pattern block, the implicit
`target rx`, which is what makes an ordinary single-pattern `.rxt` file
buildable with no head. **A file with no `target` and anything else builds
NOTHING**: it is a library of definitions, `pcrec` says so on stderr and
exits 0. That is deliberately not an error — a library ships nothing by
itself — and it is a different observable from a file `pcrec` refuses.

A target's definition names a pattern block's `name`, which lives in the
FILE namespace. A name this file does not declare is refused, naming both
the name and the `lib` chain that was searched: today `pcrec` reads no
library's contents, so a definition that lives in one is out of reach and
the diagnostic says which situation you are in.

**`-o`'s THREE FORMS, chosen by the SHAPE of its value.**

| `-o` value | result | targets |
|---|---|---|
| an existing DIRECTORY | `<dir>/<prefix>.c` and `<dir>/<prefix>.h`, one pair per target | any number |
| any other name | that `.c` plus its `.h` sibling, exactly as §1's `-o FILE` | exactly one |
| `-` | one self-contained `.c` on stdout, exactly as §1's `-o -` | exactly one |

A directory is an *existing* directory; anything else is a file name, so
`-o out.c` behaves the same whether or not `out.c` exists yet. `-o FILE`
or `-o -` on a file with several targets is REFUSED, naming the targets and
both ways forward (`--target`, or an existing directory). **Each target is a
separate compile writing its own translation unit** — there is no code path
that could produce a multi-artifact TU (D88).

**`--target NAME`** builds only the target whose PREFIX is `NAME`. An
unknown name is refused and the message lists the targets the file does
declare.

**`--lib-path DIR`** adds a directory to the search path a `lib "path"`
reference resolves against. **Repeatable**, and the order given is the
search order, after the source file's own directory — the one flag in this
CLI that accumulates rather than replacing, because a single-valued form
would make two libraries an either/or. A `lib <store-name>` reference (the
other spelling the grammar has) is refused as not in this build. Both flags
apply to `--source` alone.

**[DD-13b.W1.3] A `lib` FILE IS NOW READ, AND ITS DEFINITIONS ARE IN
SCOPE.** Until this step a `lib` reference was resolved only far enough to
say whether it named a readable file. It is now PARSED, transitively, and
its `name`d blocks join the definition set the target pattern's `(?&name)`
calls resolve against:

- The closure is this file's own named blocks first, then each `lib` file's
  in DECLARATION ORDER, depth first, deduplicated **by resolved path** — so
  two files each naming a third read it once, and a cycle terminates.
- **One definition name declared twice in the closure is refused**, naming
  both files. Within one file the same rule already applies to a duplicate
  block `name`.
- A definition is compiled in its OWN scope: its groups number from 1 in its
  own space and are re-based into the caller's, and its own `flags` seed its
  parse. A definition does not inherit the target's `flags`.
- **What a caller sees of a definition's groups is `docs/spec/match_api.md`
  §6's composition subsection**, and the short version is: a library's
  groups are non-capturing to the caller unless the definition NAMES them,
  and a named one is delivered BY NAME with a `groups[]` row whose `ref` is
  the definition's name.

**HOW A TARGET'S OPTIONS ARE COMPOSED, and what wins.** Two mechanisms, and
they are not the same rule at different scales:

1. `target … with c1, c2` composes CONFIGS by one flat LATER-WINS rule, and
   `config c from a, b` is that same rule one level down, materialised once.
2. The resulting config then composes against the pattern BLOCK's own
   directives by kind: `features` is the UNION of the two unless the block
   wrote `features only`, and everything else — `flags`, `encoding`,
   `engine`, `budget` — is MORE-SPECIFIC-WINS, i.e. the block.

Within one target, a `config`'s `pcrec <raw>` flags apply FIRST and the
typed directives on top: the typed spellings are the format's own named
axes and the only ones a block can write, so they are the more specific of
the two.

**THE FILE WINS OVER THE COMMAND LINE, ON THE AXES THE TARGET ACTUALLY
SPEAKS ABOUT — AND ONLY THOSE.** In one sentence: a command-line flag
applies unless the target's own configs or block set the SAME axis, in
which case the file's value is used. Every other flag you pass reaches the
compile untouched; this is not a general "flags lose" rule, and there is no
axis where naming a target silently discards an option you gave.

The narrow form is the point. A `.rxt` source states the build its patterns
are meant to have, and that build should not change with the invocation
that triggered it — which is exactly how a `.rxt` config directive already
behaves under `tests/harness/run.sh`'s `RXTFLAGS` env var ("appended LAST
so a directive on the same axis wins"), so a `target` behaves like the
config block it is. **It does invert the usual CLI convention** that an
explicit flag beats a file, so if you need the command line to win on an
axis the file sets, remove it from the file rather than expecting the flag
to override it.

**`--engine` IS THE ONE NAMED EXCEPTION** (Frank's ruling, 2026-09-15,
w235 finding 2). An EXPLICIT `--engine=` on the actual command line wins
over a target's `engine vm` row rather than being silently discarded by
it, and a conflict is reported on stderr — non-fatal, naming both sources
and both values — with the compile proceeding under the CLI's choice:

```
pcrec: FILE:LINE: target 'PREFIX': CLI --engine=dfa and this file's
`engine vm` disagree; using the CLI's explicit choice
```

"Explicit" means a `--engine=dfa` or `--engine=vm` was actually typed —
`PCREC_ENGINE_AUTO` is both the field's zero default AND `--engine=auto`'s
own value, so an explicitly-typed `auto` is indistinguishable from no flag
at all; both cases yield the general rule above (the file's `engine` row
applies, silently) rather than a stated boundary case. No tracking
machinery exists to tell the two apart, on the ruling's own terms: the
substance is that an explicit NON-DEFAULT CLI choice is never silently
overridden, and `auto` is the default. This exception applies to `engine`
alone; every other axis `target`/`config` can set (`flags`, `encoding`,
`budget`, `tune`) still follows the file-wins rule stated above unchanged.

**`tune` IS NOT A SECOND EXCEPTION** (D93 addendum, Frank's ruling
2026-09-16 — `docs/spec/tuning.md` §5.1 states the option in full). The
structure above invites a reader to assume a new axis joins the
exception list the moment it feels forceable; `tune` does not, and the
reasoning is worth a sentence because it is not the same reasoning
`--engine`'s exception rests on: `tune` is answer-preserving by its own
acceptance criterion, so it carries none of the H11 free-identity-control
stake `--engine`'s definition argument turns on, and it has no
`--engine=dfa`-shaped power to make a pattern refuse — an exception needs
a reason, and copying the shape of the last one is not one. A conflict
between an explicit non-default CLI `--tune=` and the file's own `tune`
row is reported the same way `--engine`'s is, with the FILE winning
rather than the CLI:

```
pcrec: FILE:LINE: target 'PREFIX': CLI --tune=min-size and this file's
`tune speed` disagree; using the file's value (--tune is not the
--engine exception)
```

**There is no `--force-tune`.** A diagnostic advertising a flag no
section of this document defines would be worse than one naming no
recourse at all; if a caller needs the command line to win on this axis,
D93's own revisit-when names the shape such an override would take (an
explicit loud flag, never a silent precedence flip), which this document
does not promise today.

**A `config` block's `pcrec <raw>` is re-parsed by this CLI's own option
parser**, so a flag cannot mean one thing on the command line and another in
a config block. It may set COMPILE OPTIONS only: an output path, a pattern,
a prefix (`-p`, which would silently overrule the target's own), a query
mode or another `--source` are all refused. The raw text is split on
whitespace and there is no quoting — no flag in this CLI takes a value
containing a space.

**Every artifact stamps `rx_info.name`** with the block's `name`, or with
its own `<prefix>` when the block is unnamed, so one definition built under
three configs is three artifacts, three prefixes and one name
(`docs/spec/match_api.md` §6). Diagnostics from a `--source` compile lead
with `FILE:LINE`, then the target, then `pcrec`'s own pattern offset.

## 2. Listing surfaces

**EIGHT** TSV dumps, each a query taking no pattern and no `-o` (mixing
either in is refused). Seven answer from what THIS BUILD of pcrec knows —
six about pattern SYNTAX and its machinery, and `--list-schema` about the
`.rxt` FILE FORMAT — while the eighth, `--list-source`, reads a FILE named
by its own value. ([DD-13b.W23.1] moved this count; `docs/spec/registry.md`
§10 is the reconciled numbering every document here agrees with.) The column CONTRACT itself — `#`
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
invocation (`main`'s `--list-families` block states the reasoning in its own
comment).

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

### `--list-limits`

Every numeric limit in `src/core/limits.def`, D90/[LIM-1] — the SIXTH
surface: one row per limit, `name`, `value`, `unit`, `kind` (`compile
budget` | `runtime capacity` | `size cap` | `selection knee` |
`identifier cap`), `override` (`flag` | `-D` | `none`), `anchor` (the
`docs/spec/limits.md` §N this number is documented in, empty when it is
not — that document states caller-facing PROMISES, not an internals
catalogue, so most compile-budget internals have none) and `desc` (a
one-line "what this bounds"). Reports the SAME numbers every `#define`/
`enum` in the tree now generates from — a row's `value` is spliced
straight into the generating site, so this dump and the compiled binary
cannot disagree about what a limit's value IS. It does not by itself
prove `docs/spec/limits.md` still states that value correctly —
`tests/registry/limits_check.sh` is the independent side of that claim,
`registry.md`'s own pattern for every other surface here. Takes no
`--flavour` (the same reason `--list-axes` doesn't: a numeric limit has
no flavour axis).

### `--list-schema`

The `.rxt` FORMAT's own schema, [DD-13b.W23.1] — the **SEVENTH** registry
surface and the eighth conforming table producer. One row per (scope,
line-kind), in two named sections:

- **`#section schema`**, ten columns: `scope`, `kind`, `value`,
  `opens_group`, `children`, `cardinality`, `constraints`, `source`,
  `validated_by`, `wave`. `docs/spec/rxt_format.md`'s "The schema and its
  surface" is the column contract itself.
- **`#section surface`**, four columns (`surface`, `scope`, `kind`,
  `reason`): the DECLARED NON-COVERAGE — what the schema does not claim to
  validate, and why. It is a section rather than a wider `validated_by`
  cell because two of its rows are not (scope, line-kind) facts at all.

The dump walks the SAME table the parser enforces — one derivation, two
readers — so a dump that disagrees with the parser about which rows exist
is not expressible. It does not by itself prove the parser ENFORCES what a
row declares; `tests/rxtsource/`'s W23-S3 is the independent side of that
claim, and it drives each row's own BEHAVIOUR rather than comparing the
dump to the table, which would be the same source twice.

A trailing `# schema-rows: N` comment carries the table's COMPILE-TIME row
total, so a consumer iterating the rows has a denominator it does not get
from the rows themselves: a check whose population is defined by the thing
it checks agrees with a truncated table by construction. Two more trailer
comments carry the `wave` column's boundaries — `# wave-built: N` (the
wave this build implements) and `# wave-reserved: N` (the RESERVED
sentinel; a row at it is a word the format owns with no delivery behind
it, refused BY NAME as RESERVED rather than as NOT IN THIS BUILD) — so a
consumer partitioning rows by wave reads both boundaries from the dump
instead of copying a constant.

Takes no `--flavour`, and for `--list-axes`' reason rather than a new one:
a flavour is a PATTERN-syntax dialect, and the file format that carries a
pattern is the same file format whichever dialect the pattern is in.

### `--list-source FILE`

The `.rxt` SOURCE file named by the option's own value, AS WRITTEN: one
row per head declaration and per pattern block, in FILE ORDER, nineteen
columns, **plus [DD-13b.W23.4]'s four `#section` blocks
(`provenance`/`variants`/`cases`/`aux`) emitted unconditionally when
non-empty, always after the main table**. **The full column table, the
`kind` vocabulary, every section's own column list, the escaping rule and
the "as written, never resolved" contract are
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

### `--emit-ir` — the VM program listing ([DD-8])

A QUERY, like the eight dumps above and unlike a compile: it takes a
PATTERN, takes no `-o`, and emits no C. It prints the VM program listing —
labels, every instruction with its branch target, choice points with their
preference order, capture-slot assignments, island boundaries, callout sites
and the artifact-wide summary facts — and exits.

It is **VM-only**. On a pattern that compiles to the DFA engine it REFUSES
and names `--engine=vm` as the way to get a VM program; a DFA listing is
future work ([DD-8], D106 addendum items 3 and 4), as is `--emit-dot`.

**Since 2026-09-19 ([DD-8]) the output is `docs/spec/table_contract.md` TSV**
— every table a named `#section` with its own column header, the program body
included. `docs/spec/ir_listing.md` is that format's contract: its nine
sections, their columns, the `prefilter` value vocabulary, the `op`
vocabulary, and what is and is not promised. Two things a consumer must take
from it: resolve a column BY NAME (column WIDTH is not a contract), and treat
the listing as a DEBUG surface — complete for control structure, LOSSY on
operands, and not an IR anything consumes.

It **derives from the emitter's own walk** rather than describing it
(`docs/design/engine_m4.md` §10): every row is rendered from the event stream
the emitting call itself appended, so the listing cannot drift from the code
it describes.

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
identical diagnostic a compile would give (`main`'s `--count-groups` block;
verified
live: `a(b)(c(d))` → `3`).

### `--probe-ask WANT [--] CONSTRUCT`

Internal/test-only by its own source comment (`cli/main.c`'s own
`core/internal.h` include note): "the
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
| `3` | **`--explain` DISSENT ONLY** — the registry's declared attribution disagrees with what the live doorway parser actually answers (`main`'s `--explain` block, the sole `return 3` in the file) | not currently reproducible against the shipped table — `tests/cli/run_cli_tests.sh` case11 measures and asserts **zero** dissents over the full row/query sweep (81 row blocks, 19 queries, all agree), which is the intended steady state; exit 3 exists for the day that stops being true |

**These are `pcrec`'s own exit codes.** They are a completely separate
vocabulary from an `--emit-main` binary's exit codes (§1 above:
0/1/2/3 there mean match/no-match/usage-error/give-up on the EMITTED
program, not on `pcrec` itself) and separate again from a give-up CODE
(`PCREC_ERR_STEPS` etc., `docs/spec/match_api.md` §4, a C-level return
value from a generated function) — three numbering schemes that happen to
share small integers and nothing else. A caller scripting against `pcrec`
should not confuse any of the three.

### The diagnostic CLASS tag (`.rxt` source diagnostics)

**[DD-13b.W23.1]** Every diagnostic pcrec emits while reading a `.rxt`
SOURCE file (`--source`, `--list-source`) carries a machine-read CLASS tag
naming WHICH RULE was violated, ahead of the message:

```
pcrec: [structure-attachment] path/to/file.rxt:12: indented line continues nothing (...)
```

**The tag's POSITION is stable** — first, in square brackets, before the
`file:line:` an author acts on — **and its SET is CLOSED**, four values:

| class | what was violated |
|---|---|
| `structure-attachment` | S0/S1/S2/S3: where a line attaches, or may not |
| `unknown-token-in-scope` | the kind has no schema row in this scope, or has one whose wave is above this build's |
| `schema-constraint` | a declared rule over lines: cardinality, a closed set, a uniqueness or resolution rule |
| `value-shape` | the line attached and is legal here; its VALUE does not parse |

**The SENTENCE beside the tag is not a contract** (D26). The tag exists so
a consumer — in particular the three-way `.rxt` parser differential — can
compare WHICH RULE fired rather than an exit code: a reader that refuses
every unrecognised line with one sentence agrees with pcrec on the verdict
while having no rule at all, and only the class can tell the two apart.

One channel, on stderr, beside the message. There is no second, structured
output mode: a second channel would be a second mechanism to keep in step.

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
- **No multi-pattern compilation UNITS**, which since [DD-13b.W1.2] is a
  narrower statement than it was. `--source` (§1) compiles SEVERAL
  patterns in one invocation, but each target is its own separate compile
  writing its own translation unit — one artifact per TU, D88. A single
  unit holding several named, CROSS-REFERENCING patterns is still `[V-E]`,
  `docs/dev/plan.md:581`, **STATE:not-started**.
- **No `--lib FILE`, and `--lib-path` is not it.** `--lib-path` supplies
  the search path a `lib "path"` reference in a `.rxt` source resolves
  against, and today that resolution goes exactly far enough to say
  whether the file exists: pcrec reads no library's CONTENTS and no
  pattern can call a definition that lives in one. The library of reusable
  named subpatterns is `[LIB]`, `docs/dev/plan.md:580`,
  **STATE:not-started**, and its own plan row records that its place
  relative to the project's roadmap has not even been ruled yet ("planned
  but I don't know that I'd put them on the spine," Frank, 2026-08-24).
- **`--emit-ir` ships; `--emit-dot` does not.** `--emit-ir` prints the VM
  program listing and is a real, working query — §2 above is its entry and
  `docs/spec/ir_listing.md` its format contract. A DOT-format graph dump was
  promised alongside it in `APPROACH.md` §6 but was never built; the combined
  row is `[DD-8]`, which is **STATE:started** and whose table-contract
  adoption LANDED 2026-09-19, while `--emit-dot`, the DFA/prefilter listing
  section and the enriched trace remain not-started within it. `--trace` (an
  instrumented, non-default matcher variant) DOES ship and is unrelated to
  either — see §1.

## Revision history

- 2026-09-21 ([REL-1.4], D115): §1 gains a `--version` entry (the flag had
  none). No existing flag's shape changed.
- 2026-09-19 ([DD-8]): §2 gains a `--emit-ir` entry (the flag had none, being
  neither a dump nor a compile), pointing at the new
  `docs/spec/ir_listing.md` for its format; §4's bullet is corrected — the
  row is STATE:started, the table-contract adoption landed, and the
  "TO BE CONSIDERED" note it cited no longer exists. No flag's SHAPE changed.
- 2026-09-03 ([DD-13b.W1.3]): §1's `--lib-path` entry gains the composition
  paragraph — a `lib` file is READ now, its definitions are in scope, the
  closure's order and dedup are stated, and a duplicate definition name
  across the closure is a refusal. `target [<prefix>] = <definition>`'s
  omitted-prefix form and the `-`/`.` name grammar are
  `docs/spec/rxt_format.md`'s; what a caller sees of a library's groups is
  `docs/spec/match_api.md` §6's.
- 2026-08-31 ([DD-13b.W1.2]): §1 gains `--source` / `--target` /
  `--lib-path` and the output-naming rule; §4's multi-pattern and
  `--lib` bullets are narrowed to what is now true. Nothing in §1's
  single-pattern surface changed.
- 2026-08-25 ([SPEC-1.2]): first version, written against `cli/main.c` at
  this worktree's branch point (`0e2b23d`) plus a live `build/pcrec` from
  a clean `make -j4`. Folds in [SPEC-1.7] (diagnostics, §3) and [SPEC-1.8]
  (modules, §1's `--features` table) as sections rather than separate
  files, per this row's brief.
