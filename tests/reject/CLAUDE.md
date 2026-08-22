# tests/reject — the "never miscompile" mandate, tested

The project rule is that a construct outside the base tier must fail with a
clean `requires module 'X'` error and never miscompile. Until 2026-08-09
nothing checked that, and the gap was not hypothetical — see below.

## Files

- **run_reject_tests.sh** — 306 rows asserted by hand (moved 268→275 at
  MOD-0.6's K10 slice: the seven `[\N{U+41}]`-shaped in-class cells,
  offset-pinned, the first hand-written coverage that row ever had;
  275→296 at MOD-0.6's mod_uprops.c slice: the full malformed-vs-
  unknown-name `\p`/`\P` taxonomy, offset-pinned, plus two pre-existing
  K12 endpoint pins re-pinned to the new position-invariant wording;
  296→299 at the S33/S34 mech-finding closure — caret-boundary pair +
  the fold-guard `\p{c}`; 299→303 at R19 close — offsets added to the two
  last message-only `\p`/`\P` pins, plus the has_eq/digit/K16-hostile-byte
  cells the differential's letters-only generator cannot produce;
  303→304 at R20/OPTRUN-1 — truncated `(?P`, the cell PC-3's tail-sweep
  template structurally cannot generate; 304→306 at R20/SPEC-1 — the two
  QUANTIFIED lexical rows `a\Q\E*` and `a(?#c)*`, which are CONTROLS rather
  than findings: libpcre2 COMPILES both, because a quote span and a comment
  are TRANSPARENT and let the quantifier reach back to the preceding atom,
  and these two say pcrec's leftmost-construct answer for them must not move
  when the bare-option-run fix lands beside it)
  (naming a module, or the
  base-grammar brace errors K5/K6/K8 and FIX-3's in-class octal ceiling, or
  since Q1 the verb doorway's four
  outcomes, or since Q2 the `(?` doorway's module names and its refusals, or
  since A1 the ten `unknown escape` pins for `\U \u \F \L \l` in both
  spellings — the rowless surface the extension design §7.1 plans to change),
  99 more reached by iterating `pcrec --list-syntax`, 65
  accept-controls, and **zero** known-wrong pins — FIX-2 graduated the last five
  into the normal tables. Since MOD-0.5c there is a FOURTH class: 15 GATED
  pins (`reject_gated`, its own counter in the ratchet), run with
  `--features modifiers` — the per-letter attribution diagnostics for `m`
  (-> 'assertions') and `J` (-> 'named-groups') and the module's own
  malformed/truncated-run wording, none of which exist in the default
  config and none of which a `perr` block can assert. **R20/SPEC-1 took this
  class from 4 to 15**: a bare option run is NOT a repeatable item, and
  `--features modifiers --emit-main 'a(?i)*'` was exiting 0 with a matcher
  that matched a/aa/aaa where libpcre2 gives err 109 — a tier-1 MISCOMPILE,
  found by the D27 blinded writer's generated sweep, reachable only through
  this gated class because the construct does not exist in the default
  config. Eleven rows, OFFSETS INCLUDED (this refusal shares one wording
  with three other sites in `p_rep`, so a message-only pin cannot tell them
  apart — the S27 lesson), spanning every quantifier form, both pattern
  positions and five accepted bare spellings. Ends with a MANIFEST
  naming the handful of rows whose deletion an exact count would not catch,
  plus the exact counts themselves. Part of `make test`; env: PCREC, KEEP=1.

  **[M6.2] wave A added a SECOND KIND of gated pin, and the pairing is the
  point.** Until now a `reject_gated` row existed because the diagnostic does
  not exist in the default config at all. These exist because ONE CONSTRUCT
  ANSWERS TWO WAYS: `\b` with module `assertions` off says "requires module
  'assertions'", and with it ON says "module 'assertions' is enabled but \b is
  not implemented yet" — the first sentence becomes a lie the moment the
  module is enabled, since it asks the user to do what they have already done.
  A module landing its constructs across several waves (this is the first)
  has that interval by construction. The seven rows sit DIRECTLY UNDER the six
  gate-closed ones in the `== assertions ==` section so a reader sees one
  construct answering two ways depending on a fact about the invocation rather
  than about the pattern, and `tests/assertions/run_assertions_tests.sh`
  carries the control they cannot: the three constructs the wave DOES build
  must COMPILE with the gate open, or every "is not implemented yet" row is
  measuring an empty module. Sabotage S70.

  **The pair to move together when a later wave lands a construct**: delete
  its `reject_gated assertions` row (it is built now) and add its cells to
  tests/assertions/. Leaving the row behind turns a true statement into a
  false one the day the producer lands — the `(?J)` wording history recorded
  in src/parse/mod_modifiers.c, exactly.

  **[STD1b] (D37, 2026-08-13) re-baseline: 306→274 hand-written, 65→99
  accept-controls, 15→55 gated, 0 known-wrong throughout.** The bare
  default flipped from empty to the frozen named set `std1` = {classes,
  modifiers} (docs/dev/decisions.md D37), so every row whose bare-default
  refusal depended on the old empty set had its OLD behaviour re-pinned as
  `reject_gated none <pattern> <expect>` (the literal old-default spec,
  explicit now instead of implicit) rather than deleted — the
  coverage-conservation rule: a construct invalidated by a default-set
  flip is never just weakened, its old pin moves behind an explicit
  `--features` spec and its new bare-default behaviour gets its own pin
  alongside (an `accept` control where the construct now simply compiles,
  a fresh `reject`/`reject_gated` pair where the diagnostic TEXT itself
  changed — `\d{3,1}`, the three malformed-hyphen option runs, `(?aP)`,
  the six `(?…)a` rows, plus a bare proof of the R20/SPEC-1 tier-1
  miscompile guard and of the std1 module BOUNDARY itself via `(?J)a`
  staying refused). `reject_gated` itself moved earlier in the file (right
  after `accept()`) so rows anywhere can call it as `reject_gated none
  ...`, not just the MOD-0.5c gate-open block that originally defined it.
  The iterated SR-4 loop also changed: it now reads the dump's MODULE
  column too, and probes a `classes`/`modifiers` row with `--features
  none` instead of bare — otherwise it silently stops testing the row's
  declared closed-gate `expect` text and starts testing something else
  (`(?J)`/`(?m)` are the sharpest case: their OWN row declares module
  'modifiers', but their live per-letter attribution once the gate is
  actually open dissents to 'named-groups'/'assertions' — a bare probe
  after the flip would have silently started asserting the WRONG text
  against the dump's own expectation). Per this directory's maintenance
  rule ("a construct cannot be both accepted-by-default and
  asserted-rejected"), every row affected was decided by state, not by
  reflex, at the same commit as the flip.

  **These four figures are hand-copied, and every attempt to maintain them by
  hand has failed — including twice in one review.** FIX-2 updated the first
  (180 → 201) and left the other three describing the tree as it was before the
  same commit: 66 iterated when the harness said 67, 45 accept-controls when it
  said 59, and 5 known-wrong pins in the very change whose headline claim was
  that there are now none (R9/C4-3). R9 then corrected them to 201/67/59 —
  and immediately invalidated its own correction by removing three DUPLICATE
  rows in the same review, so the real numbers became 200/67/57 while this
  paragraph, written to warn about hand-copied figures, carried the wrong ones
  (R9/C4V-3). Two authors, two commits, the same failure, once inside the
  warning itself. They moved again at Q2/SR-9 (200 → 235 hand-written, 67 → 99
  iterated), which is the third time in three consecutive checkpoints. The harness prints
  all four in its own summary block — `rejections checked / rows iterated /
  accept controls / known-wrong pinned` — so **read them from a run, never from
  here**, and re-run it before editing this paragraph. MECH-1 is the planned
  fix: generate the figures instead of copying them.

## What the verb rows do and do not pin (Q1, and R8 measured the difference)

`tests/registry/pcre2_check.c` sweeps ~75,000 generated verb names against
libpcre2 and is a far wider net than anything here — but it SKIPS when
libpcre2-8-0 is absent, so these rows are what still holds on such a box.

**That claim was checked rather than asserted.** A critic deleted verb rows one
at a time with PC-3 disabled: deleting `F`, `NO_JIT` or `scs` fails here;
deleting `LIMIT_HEAP` or `naplb` failed NOTHING. So the rows pin one name per
FORM GROUP — there are five — and the honest statement is that the remaining 26
names are covered by PC-3 alone. Do not read the block as "the verb tables are
pinned".

Five rules get a row of their own because each is the only check of itself: an
unknown name is not promised a module (`(*NOTAVERB)`), the lower table exists
and is chosen by case (`(*accept)`), one name carries its own message
(`(*MARK)`), an option away from the start is invalid (`a(*CR)`), and an empty
name is a quantifier error (`(*)`). All five are in the MANIFEST.

**Two boundaries are pinned on BOTH sides**, because a boundary row on one side
says a number exists, not where it is: `(*LIMIT_MATCH=4294967289)` compiles-side
against `=4294967290` rejected, and a 128-byte name against a 129-byte one.

**And one row pins a NON-defect on purpose.** `(*FAIL)*` is libpcre2 error 109
and pcrec says "requires module 'verbs'", because pcrec reports the leftmost
construct it cannot handle and stops. `\d{3,1}` beside it is the same shape at
a different doorway and has been true since the registry existed. Both are here
so that changing that rule has to be deliberate rather than accidental.

**Ten rows now pin the OFFSET too** (MOD-0.4c/S27, widened MOD-0.4d/S30): one
representative per REFUSE(at, ...) site in `pcrec_ext_verb`, both tables where
the site is genuinely per-table (too-long name, unknown name, form mismatch —
`(*NOTAVERB)`/`(*accept)`, `(*CR:x)`/`(*pla)`, the two 129-byte boundary rows,
`(*:x)`/`(*scs:x)`), one representative where it is not (`a(*CR)` for the
at-start check, `a(*ACCEPT)` — pulled out of the accepted-forms loop — for the
terminal module refusal). The reason is the same as the brace rows' above:
a message-only pin cannot distinguish `REFUSE(at, ...)` from a "blame a more
precise position" refactor to `REFUSE(nstart, ...)` or similar, because most
of these probes share one unprefixed pattern shape and every internal
position (`star`, `nstart`, the name's own end) collapses to the SAME text at
`at == 0` — only the OFFSET differs. Unlike the brace rows, which pin PCRE2
agreement, these offsets are pcrec's OWN stability under refactoring, not a
libpcre2 fact — PC-3 (`pcre2_check.c`) never compares offsets, so this really
is the only place any of these ten positions is checked. Mech rows
`tests/mech/sabotages/S27_verb_blame_offset.sh` and
`S30_verb_unknown_name_blames_nstart.sh` validate the shape live.

## Two layers, and why neither replaces the other (SR-4)

SR-4's plan text said to iterate the dump INSTEAD of the hand-written rows.
That trade was not taken, and the reason is measurable rather than aesthetic.

Since SR-2, module names live in exactly ONE place — `src/parse/registry.c` —
and the parser renders its diagnostics from it. A test that reads that same
table and asks "does the diagnostic match the table" therefore cannot see a
WRONG name: change `\d`'s row from `classes` to `misc` and the parser and the
loop agree, in unison, about the wrong answer.

Measured on a sabotaged copy of the tree:

| sabotage (exact edit) | hand-written | iterated |
|---|---|---|
| `ESC('d', "\d", classes, ...)` → `ESC('d', "\d", misc, ...)` | **2 fail** | 0 |
| `ESC('s', "\s", ...)` → `ESC('s', "zz", ...)` (a `syntax` that does not reach its doorway) | 0 | **1 fail** |
| `pcrec_syntax_tsv` returns an empty string | 0 | 0, but the vacuity guard fires |
| a NEW row with a plausible wrong module and no hand-written entry | 0 | 0 |

The last row is the honest limit: **SR-4 did not close R4's residual
circularity.** Iteration guarantees COVERAGE — no row escapes a probe, and
adding a row needs no edit here. The hand-written rows are an independent HUMAN
source for the name a caller is actually given. The maintenance cost of the
second one IS the check; that is the same rule the accept-controls follow and
the same lesson the trie-identity check learned. An external answer for the
remaining gap needs libpcre2, not another reading of our own table — see PC-3.

## What iteration structurally cannot reach

Three things, so "the dump covers it" is never read as more than it is:

- `\x{...}` and the possessive `+` have **no registry row** — they are
  sub-cases of base constructs, deliberately (D24) — so they are hand-written
  and always will be.
- the **in-class spelling** of an escape (`[\d]`) is a different diagnostic
  from the atom spelling that the `syntax` field probes.
- anything rejected by the **base grammar** (`a{1,2`, unmatched `)`, an
  out-of-order range) has no row at all.

## Why it cannot live in the .rxt corpus

A `perr` block cannot express the part that matters most — that the diagnostic
names the RIGHT module. That name is the caller's only pointer to what would
implement the construct, and `perr` asserts only that compilation failed.

There is a second, weaker reason: a `perr` block normally requires the python
oracle to ALSO fail (`verify_rxt.py` fails the block if `re.compile`
succeeds), and python happily compiles `\d`, `\b`, `(?i)`, `\p{L}` and nearly
every other module-routed construct.

**CORRECTED 2026-08-10 (FIX-1).** This section used to say the `# pcre2-only`
escape hatch "does not help either: `verify_rxt.py` consults `cur_skip` only on
`m`/`n` lines, never in its `perr` branch." That is FALSE and had never been
measured. The `cur_skip` test at `verify_rxt.py:218` comes BEFORE the `perr`
branch at `:222`, so a marked block's `perr` line is skipped like any other
case, while `run.sh` — which does not read the marker at all — still asserts
the rejection against pcrec. Measured: `tests/base/syntax_errors.rxt` carries
seven `# pcre2-only` `perr` blocks for K5, `verify_rxt.py` reports 9 skipped,
and `run.sh` runs all 61 cases. So the escape hatch works for `perr`; it just
still cannot assert a name.

## What each row asserts

1. exit status is exactly **1** — not 0 (accepted, therefore possibly
   miscompiled) and not >= 124 (crash/timeout). A crash must never satisfy a
   rejection expectation; the .rxt harness applies the same rule to `perr`
   (R1 P-C1).
2. the diagnostic contains the expected text — normally `requires module
   'NAME'`, and for the 20 base-grammar brace rows a PCRE2 error wording. Since
   R7 the brace rows also pin the OFFSET, because nothing in the repo asserted
   one and `try_quant` keeps a per-number end position for no other purpose.
   Since MOD-0.4c/d ten of the verb rows do too, for the analogous reason —
   see "What the verb rows do and do not pin" below.
3. no output file is left behind by a failed compile.

## The accept-controls are not optional

A parser that rejected EVERYTHING would score 100% on a table made only of
rejections. The 45 `accept` rows (literals, alternation, groups, every
quantifier form, classes, `.`, anchors, the character escapes, escaped
punctuation, and since FIX-1/R7 the malformed and whitespace-bearing braces)
are what stop that, and they are the same lesson the trie identity check
learned the hard way — a control has to sit inside the range of what it
certifies.

**A control has to be symmetric with the code it controls, too** (R7/T-5).
K5's over-reach guard had three accept-controls and all three overflowed the
FIRST number, so mirroring the mistake onto the second number rejected five
patterns libpcre2 compiles with every suite green. The four `a{1,65536x}`-shaped
rows close that half.

The summary enforces exact counts AND a manifest. The counts alone are not
enough: a critic moved the 65535 ceiling by one, deleted the single row that
caught it, bumped the count as the failure message itself invites, and got a
green `make test` in a two-line diff. The manifest names those rows by pattern,
so deleting one fails with a message that does not offer a number to edit.

## Over-rejection is the opposite failure, and just as wrong

The POSIX collating rows are the reason the accept-controls are not decoration.
PCRE2 rejects `[[.a.]]`, but only when a matching `.]` terminator is present —
`[.a]`, `[.]`, `[[.]`, `[a[.b]`, `[^.a.]` and `[a.b.]` are all ordinary classes
that PCRE2 compiles. A naive "reject any `[.` in a class" would have passed
every rejection row here while silently breaking patterns that work today. All
18 forms were checked against libpcre2 10.46 and pcrec now agrees on every one;
the six that must compile are accept-controls for exactly that reason.

## The bug that motivated this

`\v` was decoded as vertical tab (0x0B). PCRE2 defines it as vertical
WHITESPACE — measured against libpcre2 10.46, `\v` matches 0x0a 0x0b 0x0c 0x0d
0x85. Six bytes against one, inside classes as well as outside, and a silent
miscompile rather than a rejection.

It survived because **python `re` also reads `\v` as 0x0B**, so the base-tier
oracle agreed with the bug and `tests/base/escapes.rxt` asserted the wrong
answer and passed. Where python and PCRE2 disagree, a python-verified corpus
certifies the divergence instead of catching it — recorded in
`docs/dev/upstream_issues.md` and in `docs/pcre2_compliance.md`.

## Validated sabotages

Record the exact edit, not just the count. **The counts below are HISTORICAL
— measured against the pre-SR-2 tree shape (a separate `esc_modules[]` table
that no longer exists) — and MECH-1 measured their modern equivalents higher
(3–4 fails, because A1's pins and FIX-3's class coverage widened the net
since). Current figures come from `bash tests/mech/run_sabotage_matrix.sh`
(S15..S20 cover this suite); the rows below keep the edits and the lessons.**
One MECH-1 root-cause worth keeping: the "NEW row with a plausible wrong
module and no hand-written entry" sabotage, 0/0-undetected when first
measured, now trips exactly ONE check — the exact iterated-row count (100 ≠
99) — whose own failure message invites bumping the number (R8/C4-10). So it
is visible-in-the-diff now, not fail-proof: the SR-4 residual blind spot is
narrowed, not closed, and PC-3 remains the only external answer.

| sabotage (exact edit) | result |
|---|---|
| drop `{'d', "classes"},` from `esc_modules` so `\d` reports `unknown escape` instead of naming its module | 2 reject checks, **0** corpus cases |
| add `case 'd': return 'd';` to `esc_char_value` so `\d` silently compiles as the literal `d` — the exact shape of the `\v` bug | 2 reject checks, **0** corpus cases, **0** codegen checks |

The second is the one to remember: a silent miscompile of a class escape is
invisible to every other test in this repo.

Maintenance: when a module lands, decide each of its constructs' rows by
STATE, not by reflex (rule updated at MOD-0.3, the first landing): the
enabled set is empty by default and this suite runs the DEFAULT state, so a
gated construct is still honestly rejected here — `\d` stays, with corpus
coverage under the `features` directive carrying the supported half, and
docs/pcre2_compliance.md carrying `OK-GATED`. Only when a module becomes
default-on (MOD-0.8 policy) do its rows leave this table in the SAME change
that flips the default — a construct cannot be both accepted-by-default and
asserted-rejected. Update `docs/pcre2_compliance.md` in the same change
either way; its `REJECTED`/`OK-GATED` rows are only true because this table
and the corpus say so.

**[TT-2] (2026-08-15): `PROCS=N` internal parallelism.** The 528-check total
above is now shardable — every check call increments a shared call-index
counter and only does its real work in the shard whose turn it is
(`callidx % SHARD_TOTAL == SHARD_INDEX`), rather than by file (there is only
one file). `PROCS=1` (default) is byte-for-byte the pre-TT-2 script; `PROCS=N`
re-invokes the whole script N times and aggregates. Measured: 59.5s ->
~5.8s at PROCS=12. Output order is NOT preserved at PROCS>1 (shard-grouped,
not call-order), though the checked set and the `== Summary ==` figures are
exact either way. See docs/testing.md "Internal parallelism and section
composition ([TT-2])" for the mechanism and the sabotage validation
(a killed shard hard-fails, never silently passes).

## [M6.2 wave E] the enabled-but-unbuilt pin was RE-HOMED, not retired

`\K` was the last `reject_gated assertions` row and the LAST
enabled-but-unbuilt row in the tree; wave E built the construct, so the row
became a lie and the whole `assertions` paragraph went with it.

**Wave D's own note predicted the next step and was WRONG about it, which is
the part to read.** It said the row that had to go WITH the paragraph was
"the epilogue's own pin in `src/parse/ext.c` (the `UNBUILT` arm). A refusal
mechanism with no population is machinery nothing can test." The mechanism's
population is not module `assertions`' rows — it is EVERY registry row whose
module is enabled and whose port is unwired, and that set is large and live.
MEASURED on the shipped compiler by wave E:

    --features backrefs       '\k'     -> "module 'backrefs' is enabled but
                                           \k is not implemented yet"
    --features lookaround     '(?=a)'  -> ... '(?=...)' ...
    --features atomic-groups  '(?>a)'  -> ... '(?>...)' ...
    --features quoting        '[\Q]'   -> ... '\Q in a class' ...

So deleting the arm would have deleted a live diagnostic. What WAS true is
narrower and is what the wave actually fixed: `\K`'s row was the ONLY
hand-written pin on that arm anywhere in the tree, so retiring it would have
left a large population with no literal expectation — the exact shape this
directory exists to prevent, arriving through a wave doing the right thing to
its own rows. Four rows now stand in its place, across THREE modules and BOTH
positions: the diagnostic is assembled from each row's own `module` and
`syntax`, so a single-module pin cannot tell "the sentence is right" from
"the sentence happens to be right for `backrefs`", and the in-class wording is
spliced at a DIFFERENT site in `ext.c` from the `UNBUILT` macro's.

Gated count 61 -> 64 (one row left, four arrived). The generalisation for the
next module: when a module's last unbuilt construct lands, move the PIN, not
the MECHANISM.

## [SR-11] the row iterator now resolves columns by NAME (2026-08-21)

D65's `NF != 15` hardcode (below) was the minimal repair. The durable fix
(docs/spec/table_contract.md, [SR-11]) routes the iterator through
tests/lib/table.sh: `table_awk_map` resolves `status`/`syntax`/`module`/
`expect` by NAME into an `awk -v` string, and `table_header_ncols` supplies
the field-count guard from the header's OWN declared count rather than a
literal — so the next appended column is a non-event here, not a fourth
site to fix by hand. Both calls are checked for failure BEFORE the awk
runs: an unresolved column would otherwise leave `$AWKVARS`/`$NHDR` empty
and let awk read an undefined field variable as 0/"" — a silent mis-parse,
not a failure — so a resolution failure now `bad()`s the section by name
and forces the coverage floor's `nexpected` to `-1` (never a legitimate
count), which cannot coincidentally agree with `$niter` and mask the
failure. Sabotage-validated end to end: a wrapper `pcrec` that drops
`module` from the dump's header fails this section naming "could not
resolve --list-syntax's columns by name" AND the coverage floor ("dump has
-1 non-base rows"), never a silent zero-coverage pass.

## [D65] the row iterator is a FORMAT consumer of `--list-syntax`, and the
## first survey of its consumers missed that (2026-08-21, tail lane)

The `--list-syntax` dump gained a 16th column, `built`
(docs/design/registry_built_status_memo.md, D65). The row-iterator loop just
above (`"$PCREC" --list-syntax > "$WORKDIR/syntax.tsv"` and the `awk` that
follows) hard-coded `NF != 15` when filtering the dump to non-base rows —
this directory's field-count guard for exactly this dump, added when the
15th column (`class_expect`) landed and never revisited since. Every row
failed the check the moment the 16th column existed, so the filter matched
NOTHING, `niter` went to 0, and the section's own non-vacuity floor is what
caught it ("iterated 0 rows, dump has 0 non-base rows (floor 60) — the
iteration is not covering the table") rather than a silent pass — the exact
shape this file's own header quotes as the founding incident (`\v`'s silent
miscompile) one level up, in test infrastructure rather than in pcrec
itself.

Fixed by changing both `NF != 15` occurrences (the `awk` filter and the
`nexpected` count two dozen lines below it) to `NF != 16`, with a comment
naming D65 at the fix site. `$3`/`$4`/`$8`/`$11` (syntax/module/status/
expect — the columns this loop actually reads) are unmoved: SR-4's own
"columns are APPENDED, never reordered" rule is what makes a field-count
bump the ONLY thing that needed to change here.

**The lesson for the registry's own maintenance rule, one level up from
"decide each construct's row by state, not by reflex" above**: a new
APPENDED column to `--list-syntax` is a FORMAT change to an interface this
directory (and tests/cli's case10) asserts an exact shape of, not merely a
new fact a content reader might or might not notice. `docs/design/
registry_built_status_memo.md`'s own "Correction" section (2026-08-21, tail
lane) has the full FORMAT-vs-CONTENT consumer survey this incident argued
for, done properly the second time.
