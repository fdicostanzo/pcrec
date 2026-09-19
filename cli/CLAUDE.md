# cli — command-line compiler tool

Entry point: pcrec command-line tool. Parses flags, calls pcrec_compile(), writes output to disk or stdout.

**[M4.4] (D43.2/D44.8, 2026-08-14):** `-i` and `--emit-main` set
`opt.flags |= PCREC_CASELESS` / `PCREC_EMIT_MAIN` — `pcrec_options` no
longer has separate `caseless`/`emit_main` int fields (lib/CLAUDE.md).

**[M4.5b] (2026-08-15):** five GENERATION AXES for the VM engine
(docs/design/engine_m4.md §4.6/§5.3/§5.6). `--no-captures` sets
`PCREC_NO_CAPTURES`; `--engine=dfa|vm|auto`, `--step-budget=N`,
`--fno-step-budget` and `--backtrack-frames=N` set the new `pcrec_options`
members. They are axes rather than runtime parameters because D18 compiles
options away — and, for the budget specifically, because that is the only
shape the ruled ABI leaves open at all: `rx_matchfn`'s signature is frozen
with no slot for a budget, and adding one to `rx_ctx` is a DD-3 struct
revision D38 reserved for capture export.

**[M4.5c] (2026-08-15):** DD-8's two debug surfaces. `--emit-ir` is a QUERY
shaped like `--count-groups` — it runs the real pipeline (nothing cheaper
could honestly describe the emitted program), prints the VM program listing,
takes no `-o` and emits no C. On a pattern that compiles to the DFA engine it
REFUSES and names the two ways to get a listing, which is an as-built decision:
engine_m4.md §10 and DD-8's row are both silent, and the alternatives were
inventing a DFA listing this milestone was not asked for or printing an empty
one that looks like a bug.

**[DD-8] (2026-09-19):** `--emit-ir`'s OUTPUT FORMAT is now
`docs/spec/table_contract.md` TSV — every table a named `#section` with its
own column header, the PROGRAM body included, rendered through the [REVW.1]
wave-1 emission kit's `sb_row` (D106 + addenda, D108). `docs/spec/
ir_listing.md` is the format's contract: sections, columns, the `prefilter`
value vocabulary, what is and is not promised. Column WIDTH is not a
contract. Nothing about the flag's SHAPE changed — still a query, still no
`-o`, still VM-only with the same refusal — and no emitted `.c` byte moved.
Consumers read it through `tests/lib/table.sh`, never a fixed-position grep.

**[REVW.4] wave 4 (D111, 2026-09-19):** the `-f`/`-fno-` grammar is ONE LOOP.
`cli_axis_apply` walks `src/core/axes.def`, which carries each axis's deny
bit, its spellings and its default polarity; the twenty-two `else if
(!strcmp(a, "-fno-X")) opt.flags |= PCREC_NO_X;` arms that stood in
`cli_parse` are gone, and with them one of the three hand-maintained
spellings of that table. Two `awk` scrapers that rebuilt the pairing out of
THIS FILE'S TEXT are deleted (`tests/registry/axes_registry_check.sh`,
`tests/axes/run_axes.sh`) — after the extraction the parser and the
`--list-axes` dump read the same row, so there is nothing to reconcile. An
unknown `-f...` still falls through to the unknown-option diagnostic
unchanged, and the seven `--list-*` dumps are byte-identical across the
change. **The same wave made `--tune=`'s refusal render its alias MENU from
`src/core/tune.c`** (`pcrec_tune_names`) rather than hand-typing the same
five words D103 already made that file's own (`pcrec_enc_names`' shape,
one surface over).

**[REVW.4] wave 4 (L11-F4):** `main`'s MODE MUTUAL-EXCLUSION relation is
written once. `CLI_MODE_TABLE` (beside `CliState`) names the fourteen modes
and their field shapes; `cli_modes_active` builds a bitmask; four named
masks, each defined from the one below it, replace six hand-spelled `||`
chains over four different memberships. The summed-count exclusivity among
the seven registry queries and `--explain` stays a SECOND relation
(`cli_modes_count`) by ruling — one mechanism per relation kind. Acceptance
is unchanged on every pair and triple of modes (measured; see
`docs/dev/lanes/w4_report.md`), and no diagnostic's text moved.

`--trace` is a generation axis (`PCREC_TRACE`)
producing an instrumented artifact that prints every resume-frame push/pop and
capture write to stderr; never the default, and the artifact stamps that it is
traced.

**[ENG-BREP] (2026-08-16):** `-fno-possessify` (`PCREC_NO_POSSESSIFY`) is the
first member of D47.3's DENY family — gcc-style spelling, bare flag, a TESTING
AND TUNING AXIS rather than a user feature. It denies the possessification
rewrite (docs/design/eng_brep_design.md §2), which changes no answer by
construction, so the only reason to turn it off is to CHECK that: the row's
primary instrument compiles the same pattern both ways and compares. DENY
rather than FORCE is load-bearing per D47.3 — each quantifier walks its own
ladder skipping denied steps, so a denial composes per-quantifier with no need
to ADDRESS one quantifier inside a pattern. The do-or-die half lives in
OBSERVABILITY rather than in a refusal: the artifact stamps
`<PREFIX>_VM_STRATS`, and a denied strategy appearing there is a hard test
failure.

`-fno-revdet` (`PCREC_NO_REVDET`) is the family's SECOND member, arriving with
the reverse-deterministic rung it denies (docs/design/engine_m4.md §2.5), and
everything above applies to it unchanged — including that its do-or-die is
asserted against `<PREFIX>_VM_RUNGS`'s REVDET bit rather than against the flag
having been passed. What is specific to it: denying the rung drops a qualifying
quantifier one rung to FRAMES, which for a bounded repeat is literal
replication, which is the semantic ground truth its differential compares
against — so the deny flag is not merely how the rung is tested, it is what
makes the ground truth reachable at all. Denying it must not, and does not, deny
possessification: the two are independent, and possessification is a modifier at
every rung rather than a rung of its own.

`-fno-counter` (`PCREC_NO_COUNTER`) is the family's THIRD and final v1 member,
arriving with the counter rung (docs/design/counterk_impl/counterk_design.md),
and everything above applies to it unchanged — including that its do-or-die is
asserted against `<PREFIX>_VM_RUNGS`'s COUNTER bit (`0x10`) rather than against
the flag having been passed. What is specific to it: denying the rung drops a
bounded repeat to FRAMES, which for a bounded repeat is literal replication,
which is exactly what ships today — so, as with `-fno-revdet`, the deny flag is
what makes the differential's ground truth reachable at all. `--unroll=K`
(1..4096) is its value parameter, ONE value per artifact and never per
quantifier (D47 ADDENDUM).

**[M4.6d] (2026-08-17):** `-fno-length-prune` (`PCREC_NO_LENGTH_PRUNE`) is the
family's FOURTH member, arriving with MINIMUM-REMAINING-LENGTH pruning
(docs/design/k23_impl/k23_design.md, D51 ruling 1 — K23's fix of record), and
everything above applies to it unchanged. What is specific to it is that MRL is
NOT A RUNG: it is a bound emitted ON whichever rung a quantifier already took,
so denying it changes no rung, no slot and no capacity, and an artifact built
with it is byte-for-byte the one pcrec emitted before MRL existed. That makes
the denied build the differential's ground truth in the strongest available
sense — and it is why the denial has to leave NO TRACE, including in the
stamps: `<PREFIX>_VM_PRUNE_CEILING` reads `"none"` under the denial, exactly as
it does for a pattern that carries no bound, and the do-or-die is asserted by
the ABSENCE of a bound in the artifact rather than by a stamp announcing that
the flag was passed. `tests/mrl/run_mrl_tests.sh` holds both halves over every
pattern in the tree.

None of the five appears in `--help`, deliberately and per D47.3: these are
testing and tuning axes, documented here and in docs/testing.md, not sprawling
top-level user features. `--work-budget=N` DOES appear, and the difference is
the point — it is a real generation axis on the same footing as
`--step-budget=N` (the third DD-2 bound, settlement 4), not a strategy denial.

**[OPT-ALTCLS] (2026-08-17):** `-fno-altcls-merge` (`PCREC_NO_ALTCLS_MERGE`)
and `-fno-altcls-factor` (`PCREC_NO_ALTCLS_FACTOR`) join the DENY family —
also absent from `--help` for the same reason. Two flags, not one: stage 2
(prefix factoring, `src/opt/altcls.c`) runs on stage 1's output (single-char
alternation merging), so denying stage 1 alone must still let stage 2 factor
an unmerged run's literal spelling, and denying stage 2 alone must still
leave stage 1's merge live — a differential holding one stage constant needs
both knobs separately reachable. Unlike `-fprefilter`/`-fno-prefilter`
immediately above, this pass is BACK to the deny-only shape: each
mergeable/factorable alternation run is its own selection point, addressed
independently, the same reason the five flags above it are deny-only rather
than a force pair.

**[M4.6f] (2026-08-17):** `-fno-prefilter` (`PCREC_NO_PREFILTER`) and
`-fprefilter` (`PCREC_FORCE_PREFILTER`) are the D46 close-out for the
PREFILTER axis, and also do not appear in `--help` for the same reason. A
FORCE PAIR rather than a deny-only flag — `fit.prefilter` is one verdict for
the whole artifact rather than a per-quantifier ladder step, so the D47.3
reasoning that picks DENY over FORCE for the five flags above does not apply
here: before this pair existed, the only way to get the hybrid OFF under an
otherwise-auto selection was to also force `--engine=vm`, and the only way to
get it back ON under `--engine=vm` was not to pass `--engine=vm` at all.
`-fprefilter` is DO-OR-DIE like `--engine` itself: it REFUSES on a pattern
that compiles to the DFA engine, since there is no VM artifact to attach a
prefilter to. `-fno-prefilter` never refuses — `--engine=vm` already ships
that exact prefilter-free configuration today. See lib/CLAUDE.md for the
bit values and src/opt/CLAUDE.md for where the refusal is asserted.

`--engine` is DO-OR-DIE: a request the pattern cannot honour is a clean
refusal, never a silent downgrade. `--engine=vm` additionally turns the DFA
prefilter OFF (D44/R21 E-6), which is what makes it usable as an independent
cross-check rather than an echo of the DFA — without that, `span(VM) ==
span(DFA)` is close to a tautology, because the hybrid hands the VM the DFA's
own answer as its starting window.

## [REVW.1] wave 1 — `cli_err`, the diagnostic channel (2026-09-18)

`"pcrec: "` + the message + a newline, on stderr, in ONE place, returning 1 so
a refusing site stays `return cli_err(...)`. 71 of `main.c`'s 79 stderr sites
route through it; D26 keeps every word, proven by a message-set derivation over
the source's own call statements and by a 1.68 MB live argv/`--source` sweep,
both byte-identical.

**IT IS CLI-LOCAL AND STAYS THAT WAY** — the library does not print, and this
channel must not become the crack in that. **NO `where` PARAMETER**: lens 2's
sketch and the wave-1 charter both give it a leading `const char *where`
rendered `" (<where>)"`, and MEASURED on this tree not one site has that shape
(the parentheticals in these messages are prose inside the sentence). D77.

**EIGHT SITES DECLINED, each with its reason at the site.** `write_file`'s
`"%s: write error"` is deliberately path-prefixed like `perror()` and is not a
`"pcrec: "` message; the other seven are the two PIECEWISE builders
(`--target`'s *"it declares: a, b"* and the multi-target *"(a, b) and `-o` ..."*),
which assemble ONE logical message across five statements and would need a
buffer to route through a single call — a change of SHAPE, not of channel.

## Files

- **main.c** — CLI: option parsing ([-p PREFIX] [-e byte|utf8 | --encoding=byte|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'; -i is ASCII case-insensitive, folded into the automaton at parse time — see OS-1/D23); output file writing; the SR-3 syntax queries (--list-syntax, --explain, --flavour, --list-verbs, **--list-families** ([M6.6.2] wave F, D71 item 3 — one line per construct FAMILY: the rows sharing a key, with `built` ANDed over the members and every member spelling listed. It takes no `--flavour`, and for a reason of its own rather than by inheritance from --list-verbs: a family is a grouping OF rows, so filtering its members would print families whose membership silently depends on the filter, and the ANDed `built` would then mean something different per invocation); **--list-definitions** ([DD-11.2], D85 — the replacement/definition table, the FIFTH registry surface: one row per (row, definitions-array entry), joining `--list-syntax` on `kind`/`selector`/`syntax`; DOES take `--flavour`, unlike `--list-families`/`--list-axes`, since it walks the same rows `--list-syntax` filters — `docs/spec/registry.md` §9 is the column contract); **--explain was REWRITTEN at MOD-0.7** from a prefix match on the `syntax` column into a live doorway call — it prints the ROW's declared attribution beside the LIVE recogniser's answer and compares them per row, and it has a THIRD exit code: 0 answered-and-agreed, 1 the query could not be answered (unchanged), **3 at least one row DISSENTS** — a defect surfaced, not a bad question, which is why it is not folded into 1); --count-groups (MOD-0.1 §18.1); and --probe-ask WANT [--] CONSTRUCT (MOD-0.1 §18.2 — one doorway call at ask level claim|verdict|result, real cursor reported before/after; check06's cursor-rule channel; a doorway REFUSING is a normal exit-0 outcome, only a channel that could not run exits 1); --features LIST (MOD-0.1 slice 9 — the enabled set: module names from --list-syntax's module column, a frozen named set (`std1`, D37), or all/none, unknown names refused by name; composes with every mode; installs the set via pcrec_enabled_set_spec before anything consults the gate. **[STD1] phase A (D37, 2026-08-13):** a bare invocation (no `--features` at all) now ALSO resolves through `pcrec_enabled_set_spec`, using `PCREC_DEFAULT_FEATURES` (src/parse/enabled.c, currently `"none"`) instead of skipping the call — behaviourally identical to before (mask stays 0) but gives the enabled-set machinery a named answer for a bare invocation too, which is what lets src/gen's artifact stamp report something honest ("Feature set: none") rather than nothing. An explicit `--features` always overrides the default; the default constant is the SOLE point that later flips to `"std1"`)

**A DOORWAY THAT RAISES (R20/MOD07-1)** is a third reason `--explain` and
`--probe-ask` return NULL, and each now prints a different sentence for it.
Both surfaces used to hand the doorways a `Ctx` with no `setjmp`, which was
safe only while no port could `ctx_fail`; once module ports began recursing
into `pcrec_parse_body` the surfaces SIGSEGVed (139) on any query whose body
fails at an open gate — `--features modifiers --explain '(?i:['`. They now
`setjmp`, abandon the answer, and fill a `pcrec_error`. An EMPTY `err->msg`
still means the pre-existing misuse ("no construct matches", "WANT must be
claim, verdict or result"); a FILLED one means the port ran a real parse of
the operator's text and that parse failed, so the operator gets the COMPILE
path's own shape — `pcrec: --explain: <diagnostic> (pattern offset N)` — and
not advice to fix a command line that is fine. Exit 1 either way; cli case12
pins the shape (nonzero AND below 128, which is what separates diagnosed from
killed-by-a-signal).

`--explain`'s exit-3 summary pluralizes its VERB as well as its noun since
R20/MOD07-9: "1 row DISAGREES", "2 rows DISAGREE".

## Conventions

The tool normalizes output paths (e.g., -o out.c generates out.h automatically; -o - prints self-contained C to stdout). It writes the generated .c/.h files to the filesystem.

Compilation goes through lib/pcrec.h, the public header. The SR-3 syntax queries are the one exception: they include src/core/internal.h, because the construct registry is deliberately NOT public surface — the CLI and the test suite are its only consumers today. main.c touches no registry type even so; it calls two functions that return finished text. Promoting one of them into lib/pcrec.h if a library caller ever wants it is easy in a way that un-promoting it would not be.

Maintenance: update this file when files are added/removed or their roles change.

**[M5-SEAM] (2026-08-18, D58):** `--encoding=byte|utf8`, the long spelling
of the pre-existing `-e`, in the `=value` MODE form `--engine=` already
uses (the separate-argument forms are for files and names). Both spellings
reach ONE helper, `set_encoding`, so they cannot drift into two answers.

Three things about that helper are the point of the change rather than
incidental to it:

- **It resolves the name through the encoding REGISTRY**
  (`src/enc/enc.h`), never by mapping strings here. This file
  hand-mapping `"utf8"` while `src/core/compile.c` separately hand-wrote
  the diagnostic for it is [SR-10]'s recorded motivating instance; both
  sites now read the one table, and the unknown-encoding diagnostic renders
  its menu from that table too, so a new backend cannot leave a stale list
  behind.
- **It does NOT ask whether the encoding is implemented.**
  `pcrec_compile()` owns that refusal, so a CLI user and a library caller
  get the same answer for the same request.
- **It sets a field of THIS invocation's options** and nothing else. The
  encoding is a per-compile-call scalar (D58 ruling 2); there is no global
  for a CLI flag to set.

`-e ascii` is no longer accepted: D58 renamed the encoding `byte`
(lib/CLAUDE.md carries the reasoning). Pinned in tests/cli case13, which
also pins that the DEFAULT artifact is byte-identical to the explicitly
`-e byte` one — a stronger statement than "it compiles", since it says the
default and the explicit request are the same request.

## [DD-13b.W1.2] ONE OPTION PARSER, and `--source` / `--target` / `--lib-path`

`main`'s argument loop became **`cli_parse` over a `CliState`**, and the
reason is not tidiness: a `.rxt` source's `config` block carries a
`pcrec <raw>` line, and w1_impl §1.5 requires it to be re-parsed by this
CLI's OWN option parser so a flag cannot mean one thing on the command line
and another in a config block. That is D24's two-homes argument one surface
over. The config block is a second CALLER, never a second parser.

**THE CONTAINMENT IS ONE TEST OVER A SPAN, NOT A LIST OF FLAG NAMES.**
`pcrec_options opt` is `CliState`'s FIRST member and everything else follows
it; `cli_extras_clean` checks that the bytes PAST `opt` are all zero, i.e.
that this invocation asked for compile options and nothing else. A config
block that reached for an output path, a pattern, a query mode, another
`--source` or `-h` is refused by that one test — and so is a flag added to
this CLI tomorrow, with no edit here. **`saw_prefix` is in the tail rather
than being inferred from `opt.prefix`** for exactly that reason: `-p` writes
INSIDE `opt`, where the span cannot see it, and a config silently
overruling its target's declared prefix is the one escape that would
compile perfectly.

`-h`/`--help` sets a flag instead of printing and exiting, so a config
block's `pcrec -h` cannot print usage and exit 0 in the middle of a compile.
The flag lives in the tail, so the same one test refuses it.

**THE THREE NEW FLAGS** all take their value as a separate argument, like
`-o`/`-p`/`-e` and unlike the `=value` MODE flags — a file, a name and a
directory are exactly what that spelling is for. `--source FILE` is a
COMPILE MODE (it takes `-o`, honours every compile flag, and refuses a
positional pattern, since the file's `pattern` blocks are the patterns);
`--target NAME` selects one target by prefix; `--lib-path DIR` is
REPEATABLE and its order is the search order — the one flag here that
accumulates rather than replacing, because a single-valued form would make
two libraries an either/or. `docs/spec/cli.md` §1 is the contract,
including the `-o` naming rule (a FILE for one target, an existing
DIRECTORY for several, `-` for one on stdout) and the precedence rule (the
FILE wins over the command line, `run.sh`'s own `RXTFLAGS` precedent).

## [DD-14 wave G] `-fno-splice-calls`

The deny family's sixth member, and it is `-fno-atomic-discharge`'s SHAPE rather
than `-fno-possessify`'s: denying the splice leaves a call taking the CALL
LINKAGE, a linked call is structurally VM-only (design §8.1) and carries no
prefilter (§8.2), so **this denial can change which ENGINE a pattern gets** —
`--engine=dfa -fno-splice-calls '(a)(?1)'` REFUSES where `--engine=dfa
--no-captures '(a)(?1)'` compiles. An optimisation flag must not do that, which
is why it is its own flag and not a clause on another.

WHAT IT IS FOR is design §9.2's second control: the denied build is EXACTLY the
artifact wave B+C shipped, so `A == B` over the corpus compares two genuinely
different programs from one compiler rather than two spellings of one. The
option bit is `PCREC_NO_SPLICE_CALLS` (lib/pcrec.h); this file's only job is the
argv spelling and the one-line reason beside it.

## [DD-13b.W1.3] two small changes, both about single-homing

- `compile_source` calls **`pcrec_compile_defs`** rather than
  `pcrec_compile`, handing it the file's definition closure. `t->defs` is
  never NULL (a file with no named block gets an empty set), so there is one
  call and no branch on whether this source composes.
- `apply_target`'s `flags`-letter loop is gone, replaced by a call to
  **`pcrec_rxt_flags_from_letters`** (`src/parse/rxt_source.c`). A
  DEFINITION's own `flags` are read there too, and a letter added to one
  loop and not the other would make a library mean one thing built as a
  target and another bound into a caller — the D24 shape one tier down.

## [LIM-2] N1: THE GENERAL RAISE-ONLY SURFACE (2026-09-04)

`--max-emit-code-bytes=N`/`--max-emit-bytes=N` (D84 ruling 1) used to be two
hand-written `else if` blocks, each calling the shared `parse_raise_only`
helper with its own flag string, floor and destination field. N1 needed four
more such flags (`--max-nfa-states=N`, `--max-dfa-states-goto=N`,
`--max-subset-elems=N`, `--max-auto-dfa-elems=N`) and generalized the
DISPATCH rather than writing four more blocks: `raise_only_limits[]` is one
table of `{flag, floor, offsetof(pcrec_options, field)}` rows, and
`raise_only_match(a)` (called once per argv token, into a local computed
before the whole `else if` chain begins) tells the ONE new branch below
whether `a` is spelled `<flag>=<value>` for any row. `parse_raise_only`
itself is unchanged — it still owns the one "below the built-in default is
malformed" rule and its one error message.

`PCREC_MAX_DFA_STATES_TABLE` carries NO row, deliberately: its consumer is
the table-engine's emitted transition cell, a C `short`/`unsigned short`
(`src/gen/emit_dfa.c`), so raising the CHECK past what that format can
represent would be a lever whose number the artifact cannot honour. See
`src/core/limits.def`'s own comment on that row and `docs/spec/limits.md`
§3.3.

`--help`'s wording for the new flags sits beside the existing
`--max-emit-*` block, in the same style. None of the six flags is
data-driven at the `--help` text level — only the PARSING dispatch is
generalized, per this file's own "one general shape" convention.

## [DD-13b.W23.1] `--list-schema`, the SEVENTH registry dump

One more no-flavour listing surface, joining `--list-axes`/`--list-limits`
in the exclusion list and in the mutually-exclusive-queries guard: it
reports what THIS BUILD's `src/parse/rxt_schema.def` says about the `.rxt`
FILE FORMAT, which has no flavour axis at all — a flavour is a
PATTERN-syntax dialect (SR-7), and the file format that carries a pattern
is the same format whichever dialect the pattern is in. Contract:
`docs/spec/cli.md` §2 and `docs/spec/rxt_format.md`'s schema section.

## [DD-13b.W23.3] `--pattern-esc`

The PATTERN operand is taken in the `.rxt` format's own quoted-escape
form and decoded by `pcrec_rxt_decode_escaped` (`src/parse/rxt_source.c`)
before anything else sees it. **It is in `--help`**, unlike the deny
family above, and the difference is the point: those are testing and
tuning axes, this is an INPUT SPELLING a user chooses.

**ONE DECODER, THREE CALLERS** — this flag, `--source` and
`--list-source` — which is the whole reason the flag exists rather than
the harness approximating the decode with `printf %b`. A second escape
vocabulary drifts from the first by construction (D24's shape at the
lexer), and `format_design.md` §2.19 rules it out by name: *no bash
decoding anywhere*.

`\x00` is refused by name citing K9 (`docs/dev/known_issues.md`): the
compile entry takes no pattern length, so a NUL-bearing pattern would
compile as its prefix and report SUCCESS. The refusal names the lifting
trigger (`rx_info.pattern_len`'s API half), so the limit is a known one
with an owner rather than a silence.

The flag lives in `CliState`'s TAIL, past `opt`, so `cli_extras_clean`
refuses it inside a `config` block's `pcrec` line with no edit — a
definition that decoded its own pattern differently from its caller is
exactly the escape that span exists to close.

## [RULEFIX] `apply_target`'s `engine` row is the one axis the CLI can win

Frank's ruling, 2026-09-15 (w235 finding 2): `apply_target` used to let a
target's own `engine vm` row silently overwrite `ts.opt.engine`
regardless of whether the actual command line had asked for `--engine=`
explicitly — `docs/spec/cli.md`'s own "the file wins" rule, applied with
no exception. An explicit CLI `--engine=` now wins instead, with a
non-fatal stderr diagnostic naming both sources and both values;
`engine_name()` (right above `apply_target`) exists only to render the
three values back as text for that message.

**"Explicit" is `ts.opt.engine != PCREC_ENGINE_AUTO` at the point this
function reaches the `engine` row, and nothing more elaborate — there is
no separate tracking field.** The only two writers of `pcrec_options
.engine` in the whole tree are this exact `--engine=` flag (parsed
identically whether it came from the real argv or from a `config`
block's own `pcrec <raw>` line, reparsed above through the SAME
`cli_parse`) and the `engine` row itself, so a non-AUTO value at that
point can only mean a flag was typed. `--engine=auto` typed explicitly
is INDISTINGUISHABLE from no flag at all (`PCREC_ENGINE_AUTO` is both the
field's zero default and `auto`'s own value) and this is DELIBERATE, per
the ruling's own terms: inventing machinery to tell the two apart was
explicitly declined, because the two cases want the identical outcome —
the general "file wins" rule — regardless of which one happened.

Every other axis `target`/`config` can set (`flags`, `encoding`,
`budget`) is UNCHANGED by this ruling and still follows the plain
file-wins rule `docs/spec/cli.md` states. `engine` is the one named
exception, not a precedent for widening.
