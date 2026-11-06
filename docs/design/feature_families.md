# Feature families: `basic`, `extended`, `pcre2` ([FEAT-FAMILIES])

Status: PROPOSED rev 0 (lane featfam, 2026-11-06). Docs and measurement only; no
code, no change to any named set. Nothing here is ruled except what section 1 quotes
as ruled. Evidence labels: MEASURED (run on this box, 2026-11-06, main `cc7edf500`,
`build/pcrec` of this worktree) or READ (taken from a file, not re-run by this lane).

## GOALS

1. **A stranger's bare `pcrec` compiles the patterns real users write.** Who: a first-time
   user. Measure: bare-default refusals of the bench's 392 patterns, 150 "requires
   module" today (section 5); the target family must cut that by at least half.
2. **No project is surprised mid-way** (D37, Frank 2026-08-12). Who: a developer with an
   existing build. Measure: every frozen name compiles identically forever; the bare
   default and every moving family name change only at an announced version boundary.
3. **The family names say what a caller gets**, not how pcrec is built. Who: someone
   reading a stamp in an artifact. Measure: a stamp names a frozen member (`extended1`)
   and its expanded module list, so the artifact reproduces without remembering
   what a moving name meant that year.
4. **`basic` is derived, not asserted.** Who: the maintainers. Measure: `basic1` equals
   what the registry's engine column yields (section 3), checkable by one command.

Priority on conflict: 2 over 1 over 3 over 4. Non-goals: no new module, no producer for
an unbuilt module, no callouts in any named family (Frank 2026-10-27), no change to
`std1`, no decision here on the default move itself (it waits for [IFACE-PUSH] and a
version tag, Frank 2026-11-06).

## 1. What is ruled (quoted, not re-argued)

- Frank 2026-10-27, the three families: **basic** = modules whose constructs never force
  the backtracking engine; **extended** = basic plus `backrefs`, `lookaround`,
  `atomic-groups`, `conditionals`, `branch-reset`; **pcre2** = extended plus `recursion`,
  `verbs`; callouts opt-in everywhere. Versioned frozen members (`basic1`, `extended1`,
  `pcre2-1`) under moving family names; `std1` kept, unadvertised; `all` and `none` the
  unfrozen ends. The default moves to `extended` at an announced boundary after the
  graduation criterion holds for its modules.
- Frank 2026-11-06: "yes" (design plus graduation check now; the actual default move
  waits for [IFACE-PUSH] and a version tag); "the pcrec family is `all`".
- D37 (READ, `docs/dev/decisions.md`): a frozen set's contents never change; graduates
  form the NEXT set; the bare default advances only at an announced version boundary;
  artifacts stamp the set name AND the expanded module list; the graduation criterion
  is a checkpoint panel AND PC-3 differential coverage.

## 2. The mechanism (what a build would add; not built)

Today `g_named_sets` (`src/parse/enabled.c`) holds one row, `std1`, and
`pcrec_default_features = "std1"` is the one mapping point. READ.

- Frozen members are further rows in that table, each an explicit module list (never a
  reference to another set, so a later `basic2` cannot alter `extended1`):
  `basic1`, `extended1`, `pcre2-1`. The hyphen in `pcre2-1` is only so the name does not
  read as "pcre 21"; the other two follow `std1`'s digit-suffix shape.
- A moving family name (`basic`, `extended`, `pcre2`) resolves to the newest frozen
  member of that family. The stamp records the resolved FROZEN name, never the moving
  one (goal 3).
- **A moving name moves only at an announced boundary, like the bare default.** If
  `--features extended` could change mid-version it would be the surprise D37 forbids;
  a developer who wants unconditional protection writes `extended1`. This is a reading
  of D37, not a ruling; section 6 asks.
- Invariant to test when a build exists: for every version, `basicN` is a subset of
  `extendedN` which is a subset of `pcre2-N` (expanded lists), and each frozen member
  never changes after the commit that shipped it.
- `all` = every module in `--list-syntax`'s `module` column, unfrozen: a new module
  joins it automatically. `none` = empty. `std1` stays resolvable and is dropped from
  the advertised vocabulary text.

### What `all` contains today (MEASURED)

`--features all` stamps `PCREC_FEATURE_MODULES "classes,unicode-props,assertions,
backrefs,recursion,quoting,misc,lookaround,named-groups,atomic-groups,comments,callouts,
branch-reset,conditionals,extended-classes,modifiers,ucp,verbs,vars"`: 19 modules,
including the six with no producer (`misc`, `comments`, `branch-reset`, `conditionals`,
`extended-classes`, `verbs`) and including **`callouts` and `vars`**. `(?C1)a`
compiles under `all`; `${x}a` compiles under `all`. `code-c` is NOT in `all` (it is code,
enabled by `--allow-code`, `cli.md` §1.17¶3, READ). So the pcrec-only modules today are
`vars` (and `callouts`, which exists in PCRE2 as a syntax but whose firing contract is
pcrec's); both live in `all` and in no named family, which is what the rulings ask.

## 3. Deriving `basic` from the registry (MEASURED)

The registry has a usable engine column (`--list-syntax`, column 7: `dfa|vm` or `vm`).
Rule used: a module is a basic candidate iff no row of it is `vm`-only.

    build/pcrec --list-syntax | awk -F'\t' '$8=="module"{m[$4]=1; if($7=="vm")v[$4]=1}
        END{for(k in m) if(!(k in v)) print k}' | sort

Result:

| engine column | modules |
|---|---|
| every row `dfa\|vm` | `classes`, `modifiers`, `named-groups`, `quoting`, `ucp`, `unicode-props`, `comments`, `misc`, `extended-classes` |
| mixed | `assertions` (6 rows `dfa\|vm`, `\K` is `vm`), `backrefs` (12 `vm`, `\0` is `dfa\|vm`), `recursion` (35 `vm`, `(?(DEFINE)...)` is `dfa\|vm`) |
| every row `vm` | `atomic-groups`, `lookaround`, `conditionals`, `branch-reset`, `verbs`, `callouts`, `vars` |

Three things the derivation shows that the agreed text does not say:

**3.1 `assertions` fails the rule on one row.** `\K` is `vm`-only (confirmed:
`--engine=dfa` refuses it with "requires the VM engine"). `\b \B \A \z \Z \G (?m)^$` are
`dfa|vm`. The agreed families put `assertions` in basic implicitly (it is not in the
extended-adds list), and RE2 has all of them except `\K` and `\G`. Options, not chosen:
(a) `assertions` is in `extended` only, and `basic` is the strict derivation (bench cost:
43 patterns, section 5); (b) `assertions` is in basic and `\K` (and `\G`, which is
`dfa|vm` here but stateful) is refused under basic by a row-level exclusion, a new
mechanism the module gate does not have; (c) `\K` becomes its own module (a registry
change, an abi event: the module column is read by stamps and `--list-syntax` pins), so the
module-level rule is exact.

**3.2 "Never forces the backtracking engine" is a construct-level statement, not a
pattern-level one.** Under `--engine=auto`, ANY capture group selects the VM
(`(?<n>a)` stamps `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture group at pattern offset 0"`,
MEASURED); a DFA-only artifact needs `--no-captures`. So a basic pattern with a capture
runs on the VM engine, which is the threaded-code backtracker (APPROACH.md, READ). This
lane did not measure whether the VM is linear-time on basic constructs. The plan row's
"basic is roughly RE2's feature set (linear time)" is therefore a spec claim nobody has
checked; the safe wording is "no construct that requires backtracking", not "linear".

**3.3 Four of the derived-basic modules have no producer or only part of one.** `misc`
(`\R \X \C \c \o`), `comments` (`(?#...)`), `extended-classes` (`(?[...])`) are `unbuilt`
in every row; `unicode-props` has one `unbuilt` row (`\N{U+hhhh}`) and a property gap.
`-e utf8` enables `unicode-props` and `ucp` whatever the list says (`pattern_language.md`
§2.3¶4), so a utf8 compile of a basic family also carries those two; the stamp's expanded
list must show it (it already does for explicit lists, READ; not re-checked for utf8).

## 4. The unbuilt-member problem (options, not chosen)

A frozen set promises "compiles identically forever". If `basic1` lists `comments` and
`comments` later gains a producer, `basic1` starts ACCEPTING `(?#...)`: the module list is
unchanged, the accepted language grew. Same for `unicode-props` growing properties, which
already happens inside std1-era modules. Which promise is frozen?

- **P1, list frozen, language may only grow.** Anything `basic1` accepted keeps its
  meaning and its engine; new acceptances are allowed when a listed module gains a
  producer. Cheap, matches what has happened to `classes` and `modifiers`. A pattern
  refused by `basic1` today may compile tomorrow, so "refused in the stamp's contract"
  is not stable.
- **P2, language frozen.** A frozen member lists only BUILT modules; an unbuilt module
  joins the next version when it ships (`extended2` adds `conditionals`). Strictest, and
  exactly D37's "graduates form the NEXT set". Means `extended1` cannot name
  `conditionals` or `branch-reset` today, so it is smaller than Frank's definition until
  they are built.
- **P3, ship the family when its unbuilt members are built.** Delay `extended1` until
  `conditionals` and `branch-reset` exist, and `pcre2-1` until `verbs` exists. Honest to
  the definition; the default move waits on two or three module builds that no plan
  row schedules (see report: none of them has a not-started row with a trigger).

Per family, what P2 yields today (built modules only): `basic1` = `classes`, `modifiers`,
`named-groups`, `quoting`, `ucp`, `unicode-props`, plus `assertions` per 3.1;
`extended1` = that + `backrefs`, `lookaround`, `atomic-groups`; `pcre2-1` = that +
`recursion`. `verbs`, `conditionals`, `branch-reset`, `misc`, `comments`,
`extended-classes` wait for their producers. Section 5's numbers use the full
definitions (unbuilt members named) because the refusal text then separates "family
does not include it" from "family includes it, pcrec has not built it".

## 5. The bench effect (MEASURED)

Method: every `bench/*/patterns/*.rx` of pcrec-bench (392; read-only), compiled to C only
(no gcc) with `build/pcrec --features LIST -p rx -o scratch --pattern <bytes>`, byte
encoding, no other flags; as the scoreboard lane's (`docs/dev/lanes/scoreboard_report.md`).
"gated" = the first stderr line has `requires module 'X'`; "unbuilt" = `module 'X' is
enabled but ... is not implemented yet`; "fixed" = refusals no family can change: 7
size limits, 5-6 `\x{...}` above U+FF in byte mode, 1 `(*SKIP)` (out of scope), 1
variable-length lookbehind (`all`/extended/pcre2 only; under narrower sets the gate hides it).

Premise test: bare default (`std1`) = 229 compile, 163 refused, of which **150 are
"requires module"**, reproducing the scoreboard's 150-of-392 (its histogram too:
assertions 58, lookaround 21, unicode-props 14, atomic-groups 11). The other 13 are the
"fixed" class. `--features all`: 366 compile.

The families, written as module lists (the names do not exist yet):

- basic = classes, modifiers, quoting, named-groups, ucp, unicode-props, assertions, comments, misc, extended-classes
- basic-strict = basic minus assertions (the 3.1 derivation)
- extended = basic + backrefs, lookaround, atomic-groups, conditionals, branch-reset
- pcre2 = extended + recursion, verbs

| feature set | compiles | refused | gated | unbuilt | fixed |
|---|---|---|---|---|---|
| none | 153 | 239 | 227 | 0 | 12 |
| std1 (= bare default today) | 229 | 163 | 150 | 0 | 13 |
| basic-strict | 250 | 142 | 121 | 8 | 13 |
| basic | 293 | 99 | 78 | 8 | 13 |
| extended | 333 | 59 | 34 | 10 | 15 |
| pcre2 | 350 | 42 | 17 | 10 | 15 |
| all | 366 | 26 | 1 | 10 | 15 |

(`all`'s one gated refusal is `verbs`, which uses the gated shape at every gate state,
`pattern_language.md` §2.4. The `unbuilt` count of 8 for basic vs 10 for extended is
`conditionals` and `branch-reset`, one pattern each.)

Refusal-module histogram (gated plus unbuilt; counts are patterns, each counted once at
its first refusal):

| set | histogram |
|---|---|
| std1 | assertions 58, lookaround 21, unicode-props 14, atomic-groups 11, recursion 9, named-groups 9, backrefs 8, misc 5, ucp 5, callouts 2, vars 2, conditionals 1, quoting 1, branch-reset 1, comments 1, verbs 1, extended-classes 1 |
| basic-strict | assertions 60, lookaround 21, recursion 12, atomic-groups 11, backrefs 10, callouts 2, vars 2, conditionals 1, branch-reset 1, verbs 1; unbuilt: misc 5, comments 1, extended-classes 1, unicode-props 1 |
| basic | lookaround 22, recursion 15, atomic-groups 14, backrefs 12, callouts 8, vars 4, conditionals 1, branch-reset 1, verbs 1; unbuilt: misc 5, comments 1, extended-classes 1, unicode-props 1 |
| extended | recursion 17, callouts 12, vars 4, verbs 1; unbuilt: misc 5, conditionals 1, branch-reset 1, comments 1, extended-classes 1, unicode-props 1 |
| pcre2 | callouts 12, vars 4, verbs 1; unbuilt as extended |
| all | verbs 1; unbuilt as extended |

(Strict basic shows assertions 60 against std1's 58 because two patterns that std1 reports
first as `ucp`/`named-groups` surface `assertions` once those are on.)

Reading it, with the limits stated:

- `extended` as the bare default: 229 -> 333 compiling (58% -> 85%). Its 59 refusals
  split 34 gated (17 `recursion`, which is the `pcre2` family, 12 `callouts` and 4
  `vars`, which are opt-in/pcrec-only by ruling), 10 unbuilt, 15 fixed. No refusal under
  `extended` is a module the family promises and pcrec has built.
- The bench is a DESIGNED capability suite (the `capability`, `syntax` and `unusual`
  directories probe constructs on purpose), not a usage census; the scoreboard lane found
  real-world frequency 0 for every gap it could count. Of the 34 rows with a non-empty
  `source_url` in a `provenance.tsv` ("wild"; the scoreboard said 32 for two directories,
  this counts four), compiling: std1 17, basic-strict 17, basic 24, extended 30, pcre2 33,
  all 33. That is the better user-facing number: `extended` 30 of 34, `basic` 24 of 34.
- Goal 1's bar (cut the 150 gated refusals by half): met by `basic` (78), `extended` (34).
  Not met by strict basic (121).

## 6. Questions this note leaves open (plain words in the report)

1. Does a moving family name (`--features extended`) move only at announced boundaries,
   like the bare default? (Lean: yes.)
2. What does "frozen" promise: the module list, or the accepted language (section 4)?
   (Lean: P2 for modules that are built; list the unbuilt ones only in the next version.)
3. `assertions`: basic, extended, or split `\K` out (section 3.1)? (Lean: (c), `\K` its
   own module, if it is cheap; otherwise (a) with a note.)
4. Do the D6 design panels count as the "checkpoint panel" for a module whose
   implementation never had a close panel (section 7)? (No lean; Frank's text.)
5. Is "linear time" claimed for `basic`? (Lean: no, until measured.)

## 7. The graduation table (the criterion applied)

Criterion (D37): a D6 panel recorded in `docs/dev/reviews/` AND PC-3 libpcre2
differential coverage of the module. Two readings are needed before a verdict:

- **PC-3 as written is an EXISTENCE check** (`tests/registry/pcre2_check.c` header, READ):
  libpcre2 must COMPILE the probe of every `RS_MODULE` row. It does not compare matches.
  The semantic differential that decides behaviour is PC-4 (classes only,
  `tests/registry/pc4_check.c`) plus each module's own libpcre2 differential script.
  The table gives both columns; "differential" below means the module's own match/span
  comparison against libpcre2, which is what std1's two modules were held to.
- **Panel kind.** "Design" = a D6 panel on the design note before the build. "Close" = a
  panel on the landed implementation. I found close panels by file name for 4 modules;
  for the rest only a design panel (or none). Whether a design panel satisfies D37's
  "checkpoint panel" is question 4.

All "READ" below means: the file exists, is in a `make test-X` target (Makefile targets
list, MEASURED by grep), and its header says what it compares; this lane did NOT re-run
PC-3, PC-4 or any module differential (the kit's gate jobs hold the box lock).

| module | built (registry rows) | family | D6 panel (file) | libpcre2 evidence | meets? |
|---|---|---|---|---|---|
| classes | 12/12 | basic | close: `2026-08-12-r16-mod03.md` | PC-3 existence; PC-4 semantic, 62,872 cells (`pc4_check.c`); fuzz gate `test-capturediff` | yes (in std1) |
| modifiers | 12/12 | basic | close: `2026-08-12-r17-mod05.md`; surface panel `2026-08-12-r20-mod08.md` | PC-3 existence; R20's three PC-3 option-run differentials; fuzz gate | yes (in std1) |
| quoting | 2/2 | basic | none with it as subject (named only inside design panels r13, r14) | PC-3 existence; `tests/quoting/` d27 corpus; no match differential script found | panel NOT FOUND; semantic differential not found |
| named-groups | 3/3 | basic | none as subject (named inside r10, r14, r20, r32) | PC-3 existence; `tests/named_groups/CLAUDE.md`: pcre2-only blocks translated or manager-verified against libpcre2 10.46, no differential script | panel NOT FOUND; partial oracle |
| ucp | 3/3 | basic | design only, light (2 critics): `2026-09-28-r1-ucp-design.md` | PC-3 existence; `tests/ucp/` compares every cell against the resolved libpcre2 on `test-ucp` (`ucp_compare.py`) | design panel; differential yes |
| unicode-props | 2/3 (`\N{U+hhhh}` unbuilt) | basic | close: `2026-08-12-r19-mod06.md` | PC-3 existence; whole-space `\p` membership differential `tests/uprops/` (`test-uprops`) | yes for built rows; partial module |
| assertions | 7/7 | basic or extended (3.1) | design: `2026-08-18-r30-assertions-design.md` | PC-3 existence; `run_gstart_diff.sh`, `run_kreset_diff.sh`, `run_mline_diff.sh`, `verify_pcre2.py` | design panel; differential yes |
| atomic-groups | 5/5 | extended | design: `2026-08-22-r31-atomic-groups-design.md` (3 rounds) | PC-3 existence; `run_atomic_diff.sh` + `atomic_oracle.py` | design panel; differential yes |
| backrefs | 13/13 | extended | design: `2026-08-22-r32-backrefs-design.md` (3 rounds) | PC-3 existence; `run_backref_diff.sh`, `run_dupnames_diff.sh` | design panel; differential yes |
| lookaround | 18/18 | extended | design: `2026-08-23-r33-lookaround-design.md` (3 rounds) | PC-3 existence; `run_lookaround_diff.sh`, `run_expansion_diff.sh` | design panel; differential yes |
| conditionals | 0/1 UNBUILT | extended | none | PC-3 existence only (row accepted by libpcre2) | no: no producer |
| branch-reset | 0/1 UNBUILT | extended | none | PC-3 existence only | no: no producer |
| recursion | 36/36 | pcre2 | design `2026-08-23-r34-subroutines-design.md`; wave `2026-08-25-r35-wave-g-panel.md`; code `2026-08-25-r36-frame-buffer-code-panel.md` | PC-3 existence; `run_recursion_diff.sh`; D27 blinded corpus 1,031 cells (plan_completed DD-14) | design + wave/code panels; differential yes |
| verbs | 0/1 UNBUILT (name tables only) | pcre2 | `2026-08-12-r18-mod04.md` covered the verb TABLES (migration test), not a producer | PC-3 verb-name differential (part 3 of `pcre2_check.c`) | no: no producer |
| comments | 0/1 UNBUILT | basic | none | PC-3 existence only | no: no producer |
| misc | 0/5 UNBUILT | basic | none | PC-3 existence only | no: no producer |
| extended-classes | 0/1 UNBUILT | basic | none | PC-3 existence only | no: no producer |
| callouts | 1/1 | none (opt-in; in `all`) | none as subject; callout ABI design in r21 (READ) | `tests/callouts/co_oracle.c` + `gen_diff.py` (READ: header not opened) | n/a by ruling |
| vars | 1/1 | `all` only | design: `2026-09-23-r1-var-design.md` | PC-3 CANNOT cover it: libpcre2 reads `${name}` as `$` then literal `{name}`, so the existence probe passes vacuously (INFERRED from PCRE2 syntax, not run) | n/a (pcrec-only) |
| code-c | row of the column, not a feature module | none (not in `all`) | inline-C panels r1-r2 (2026-10-26/27, READ names) | n/a | n/a |

Today's strongest case: `classes`, `modifiers` (already std1), `unicode-props` (built
part), `atomic-groups`, `backrefs`, `lookaround`, `recursion`, `assertions`, `ucp`: panel
(design at least) plus module differential. Weakest: `quoting` and `named-groups`
(both built, both in the basic definition, neither has a panel I could find nor a match
differential against libpcre2). That is a measured gap in the evidence for the very
modules `basic` is made of; closing it is a light panel and one differential each, not a
build.

Family-member consequences, unbuilt members listed (no choice made here):

- `basic1` names `comments`, `misc`, `extended-classes` (no producer). Options P1/P2/P3
  of section 4.
- `extended1` names `conditionals`, `branch-reset` (no producer) on top of the above.
- `pcre2-1` names `verbs` (no producer; `(*ACCEPT)` and every verb is refused at every
  gate state) and inherits all of the above. Verbs also includes two constructs PCRE2
  has that pcrec calls out of scope for good (`(*SKIP)` family, `pattern_language.md`
  §8.2), so `pcre2-1` can never equal "all of PCRE2" and the name must not claim it:
  D26 says "compatible", not "the same".

## 8. Standing questions

1. Measurement regime: refusal counts are compile-to-C verdicts, byte encoding, one
   box, no gcc; a different encoding (`-e utf8`) enables `unicode-props` and `ucp`
   anyway and would move `unicode-props` 14 -> 0 and `ucp` 5 -> 0 under std1; no
   decision here depends on that.
2. Independent control: the registry's engine column is pcrec's own, so deriving
   `basic` from it shares a source with what it controls. The control is `--engine=dfa`
   refusing the `vm` rows (MEASURED for `\K`, `\1`, captures) and PC-3 for existence.
   The family boundary itself (what RE2 users expect) has no external control here.
3. What moves when regenerated: the stamp strings in every default-compiled artifact when
   the default moves (an abi event, D76/D94); nothing moves when only NAMES are added.
