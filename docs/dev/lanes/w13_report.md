# lane w13 — [DD-13b.W1.3] report

**Branch `lane/w13`, 16 commits on `main` 9d8401a. Status: BUILT, NOT
SUITE-VALIDATED.** Two phases on 2026-09-03, both entirely under the box
hold, which forbids every script under `tests/`. So nothing here rests on
`make test`; what it rests on is `make strict`, ~260 single compiles, and a
set of matcher runs against outside oracles, each named below with what it
measured.

- **PHASE 1, 17:00–17:5x** — the composer, the name grammar, the altwide
  dogfood, the identity proof. §§1-8.
- **PHASE 2, 18:3x–19:0x** — Frank's D89 addenda 1-4 arrived and changed the
  DELIVERY MODEL. **§§9-12 are the current state; where §§1-8 and §§9-12
  disagree, §§9-12 win**, and §9 says exactly where they disagree.

---

## 1. What exists on the branch

### The composer — `src/parse/rxt_compose.c` (new, ~470 lines)

One file, because every mechanism in it is meaningless without the others.
`pcrec_rxt_compose` runs between `pcrec_parse` and `pcrec_altcls`
(`src/core/compile.c`), both bounds forced by `w1_impl.md` §2.1, and is one
pointer test when `cx->defs` is NULL.

**D89 made §2 unbuildable as written, and §8.0 of `w1_impl.md` is the
correction.** Frank's Q-W1 ruling replaced the note's one-tier injection
with three tiers:

| tier | which lib group | slot | `groups[]` row |
|---|---|---|---|
| delivered | one the definition NAMES | above `ngroups` | yes, `ref` = the definition's name |
| hidden | unnamed, the definition references it itself | above `ngroups` | no |
| **erased** | unnamed and referenced by nothing inside it | **none — the `A_CAP` is deleted** | no |

A tier that spends no number is not expressible by §2.5's "add `base` to
every `A_CAP`" walk, because the survivors must close up. **So the offset
became a MAP** (`local -> final, or 0`), which is the assignment table §2.7
already names as the one derivation with three readers, and which
degenerates to `+base` exactly when nothing is erased — so §2.5's MEASURED
cell is still the expected answer.

### The rest, file by file

- **`src/parse/rxt_source.c`** — a `lib` file is READ now, transitively; a
  fixpoint with a visited set keyed on the RESOLVED path (a diamond reads
  once, a cycle terminates), in `lib` declaration order, depth first, this
  file's own blocks first. A duplicate definition name across the closure is
  a refusal naming both files. The name grammar (`defname_ok`) admits `-`
  and `.` after the first byte; `pcrec_rxt_prefix_from_name` is the ONE home
  of the `-`/`.` -> `_` mapping; `target = <def>` derives the prefix;
  `pcrec_rxt_flags_from_letters` moved here from `cli/main.c`.
- **`src/parse/mod_backrefs.c`** — `pcrec_bref_resolve` DEFERS an unresolved
  by-name `PEND_CALL` under `Ctx.defer_file_refs`. The `PEND_BREF` name arm
  is NOT deferred (D87 rule 2). `deferred` is written explicitly in both
  arms; the arena zero is the unsound direction.
- **`src/core/internal.h` / `compile.c`** — `RxtDef`/`RxtDefs`,
  `NamedGroup.scope`, `PendingRef.deferred`, `Ctx.ncap_primary`/`defs`/
  `defer_file_refs`, and `pcrec_compile_defs` (internal; NOT a
  `pcrec_options` field — D20).
- **`src/gen/emit_dfa.c`** — `ng_cmp_name` gains the leading `ref-is-NULL`
  key, `.ngroups` reads `ncap_primary`, `.nnames` counts the primary's rows,
  `.nentries` counts the array, and `.ref` stops being a literal `NULL`.
- **`tests/harness/run.sh` and `verify_rxt.py`** — legs B and C of the name
  grammar, moved in the same change as leg A.
- **Spec (D80)** — `rxt_format.md` (the name grammar, the prefix mapping,
  `target = <def>`, the collision refusal, the not-callable-from-a-pattern
  boundary), `match_api.md` §6 (S9b as D89 revised it, plus a new
  composition subsection), `cli.md` (a `lib` file is read).
- **Tests** — six fixtures and a W1.3 section in `tests/rxtsource/`; the
  altwide dogfood fixture; `tests/definitions/` with its own section
  (`make test-definitions`).

---

## 2. What was MEASURED tonight, and how

Every row is a command that ran under the hold's allowances (single
compiles, gcc on one artifact, one run each, `python3 -c` oracle checks).

| # | claim | how | result |
|---|---|---|---|
| M1 | the §2.5 cell: a library's own meaning survives re-basing | composed `^(\d)-(?&dd)$` over `dd` = `(\d)\1`, built, run on four subjects | `5-77` match (0,4), `5-75` NOMATCH, `5-11` match (0,4), `55-77` NOMATCH — the definition's `\1` re-based to `\3` |
| M2 | **`nentries > nnames`, first time in the tree** | a definition naming one group, composed | row `{ "word", 2, 2, "local" }`; `ngroups` 0, `nnames` 0, `nentries` 1 |
| M3 | the ERASED tier is worth a slot, against an EXTERNAL referent | the three-tier fixture composed vs the PCRE2 textual control | composed `NCAPS 4`, control `NCAPS 5` — and the control's `groups[]` exposes BOTH the wrapper name and the lib group to the caller with `ref NULL`, which is what D89(2) forbids |
| M4 | **IDENTITY (A): a non-composed artifact is unchanged** | a compiler built from `main` 9d8401a vs this branch, artifacts compared with `cmp` | **81 artifacts, 0 differing** — 12 patterns on the default path, 10 across `--no-captures`/`--engine=vm`/`--engine=dfa`, 59 distinct `tests/base` patterns |
| M5 | the altwide set is losslessly representable | byte-for-byte round trip out of the `.rxt`, plus a scan for newline/tab/non-ASCII/edge whitespace | 33/33 identical; and across all four bench sets **90 patterns** (O-13 said 77) with the claim holding for every one |
| M6 | the prefix mapping's collision surface | the mapping applied to all 90 bench ids | exactly one collision, `floor`, and it is **CROSS-SET** — no single-set export collides |
| M7 | the altwide compile census | 33 sequential single compiles, 54 s wall, load under 1 | 19 built (18 over `--warn-emit-bytes`), 12 refused on the emitted-size cap, 2 refused for module `assertions` (`\b`) under the default set; under `--features all` those two hit the cap too, so 19 built / 14 refused |
| M8 | the flat control patterns are right | `python3 -c` with `re` over all 15 cases | 15/15 as written |
| M9 | the tree compiles clean | `make strict` | clean, twice |
| M10 | the six new fixtures behave | one `--list-source` and one `--source` each | all six as designed; diagnostics quoted in §5 |
| M11 | W1.2's own fixtures still behave now that libs are READ | `head_basic`, `lib_missing` with and without `--lib-path`, `common.rxt` | all four unchanged |

---

## 3. What is UNVERIFIED, and it is a real list

Everything below is owed to tomorrow's lift. None of it is a doubt about a
particular line; it is the absence of the suites.

- **`make test`** in full. In particular `test-corpus` (the composer runs on
  every compile as a pointer test, and M4 is the evidence it costs nothing,
  but M4 is 81 artifacts and the corpus is 3,325 blocks).
- **`make test-codegen`**, which owns the abi expectation and
  [M6.5-DUPNAMES]'s `groups[]` order check — **that check's expectation
  MOVES in this change**, because a new leading sort key changes what
  "non-decreasing" means. It is the single most likely red tomorrow.
- **The identity gate**, comparisons (A) and (B). (A) is what M4 samples;
  (B) needs the abi bump and the re-pin, which this branch deliberately does
  not do.
- **`make test-definitions`** — the new section has never run. Its pieces
  were exercised by hand (M1, M8) and its awk helpers were run directly
  against the fixtures, but the script as a whole has not executed.
- **The W1.3 section of `tests/rxtsource/`** — same: every command in it was
  run by hand, the section was not.
- **`make test-axes`, the sanitizers, `mech`.** Two of the seven sabotage
  rows named in `w1_impl.md` §8.4 have no witness yet.

---

## 4. The abi event

**The branch does NOT bump the number.** `w1_impl.md` §8.7 carries the D94
grep, run over the branch: **six readers of the current value 17**, of which
a hand-enumerated four would have missed two (`match_api.md:1754` and the
bump ledger clause at `run_codegen_tests.sh:2760`) — D94's own lesson
reproduced on the very next bump after the ruling. Two further grep hits are
recorded as NOT readers, because a list that silently dropped them would be
indistinguishable from one that missed a real site.

The `FILEPIN` moves to this step's **last** src-touching commit, never its
first (`run_recursion_identity.sh:394-406`; getting it backwards cost 952
falsely-differing artifacts once).

---

## 5. The refusals this step adds, quoted

```
definitions 'a.b' and 'a-b' (line 1) both map to target prefix 'a_b';
  a name's '-'/'.' become '_', so give one an explicit prefix
definition 'selfy' (…:14) uses whole-pattern recursion ((?R), (?0) or \g<0>)
  inside a definition, which this build refuses: after composition it could
  mean the caller's whole pattern or the definition's own body, and the
  ruling that picks one is not written yet
(?&nosuch) refers to a capture group named 'nosuch', which this pattern
  does not declare (pattern offset 1)
definition 'word' is declared twice in the lib closure: also at …:15
'name' wants a definition name — a letter or '_' then letters, digits,
  '_', '-' or '.' (got '9bad')
```

The third is `mod_backrefs.c`'s own sentence, RE-RAISED at its own offset,
which is what keeps the four `perr` blocks in
`tests/recursion/d27/sr_refusals.rxt` at today's wording.

The collision message was shortened once during the lane: its first form was
TRUNCATED by `pcrec_error.msg`'s 256 bytes at a realistic path length. It
still met its contract — both names and the prefix come first, the advice
was the part cut — which is the discipline lane w12 paid for; it was
shortened anyway so the message is whole.

---

## 6. Questions for the manager — ALL FIVE NOW RULED (see §9)

**Every question below was answered the same evening**, four of them by Frank
(D89 addenda 1-4) and one by the manager. They are kept as written because §9
is easier to read against them. Q-W3's answer went AGAINST the provisional
choice, which is the one that mattered.

1. **Q-W3 — is EVERY named group in a definition delivered?** Implemented
   **yes**: naming is the only interface declaration W1 has (D89 point 4
   leaves delivery to "the lib's own names"). The cost is that a library
   author cannot name a group PRIVATELY; today's workaround is `(?:…)` plus
   a comment. The alternative — a head line listing the delivered names —
   was rejected as a SECOND place an interface is declared, but it is a real
   alternative and Frank may prefer it.
2. **Q-W4 — does a definition inherit the target's config?** Implemented
   **no**: a definition block's own `flags` seed its sub-parse (r45sem M2)
   and nothing else reaches it, so a library means the same thing in every
   file that binds it. `encoding` is the case worth a ruling: D58 makes it a
   per-PATTERN scalar and a composed artifact has only one, so a definition
   block that wrote a different `encoding` cannot be honoured. Today it is
   silently ignored; it should probably be a refusal, and I did not build
   one because "silently ignored" and "refused" are both defensible and only
   one of them is reversible cheaply.
3. **Q-W5 — `target = <name>`, or an implicit target per `name`d block?**
   Implemented as the explicit shorthand, because format_design §2.7's
   "every other file builds nothing unless it says so" is a shipped rule and
   an implicit target would repeal it. The consequence is that the bench's
   exporter writes one `target =` row per pattern — 33 for altwide. If that
   is judged noise, the implicit form is the alternative and it is a small
   change.
4. **The `run.sh` composed-block path, deliberately NOT written.** A
   composed block cannot be compiled from its own text, so
   `tests/definitions/`'s fixtures are `.rxtin` and are not in the
   harness-scored corpus. Making them corpus files needs run.sh to compile
   such a block through `--source --target` instead of `-p rx`, plus a LOUD
   floor for a composed block with no target (its cases would otherwise go
   unscored). I did not write it blind: it is a change to the most
   load-bearing script in the tree, its blast radius is bounded only by the
   fact that no corpus file declares a `name` today, and it wants a real run
   behind it. `verify_rxt.py` already carries the matching skip predicate,
   with a population of zero.
5. **A delivered slot does not hold the definition's offsets yet**, and the
   spec now says so plainly. A subroutine call is capture-transparent, so a
   callee's captures are restored on return and a delivered slot reads
   `(-1,-1)` — **which is PCRE2's own behaviour** for
   `(?(DEFINE)(?<g>a))(?&g)`. W1.3 delivers the NAME TABLE; making a call
   RETAIN what its callee matched is a property of the CALL SITE and its
   syntax is W1.4's. If the manager reads W1.3's charter as requiring live
   values, that is a scope disagreement worth settling before the merge, and
   the answer is §2.8's two named mechanisms plus D89 point 4's grouplist
   semantics — i.e. W1.4.

---

## 7. The ask to pcrec-bench, with the exact rules their exporter needs

For the manager to relay through `inbox_from_pcrec.md`. The name rules they
asked about in O-13 §4(a) are ACCEPTED, with these exact spellings:

1. **A block `name` is `[A-Za-z_][A-Za-z0-9_.-]*`.** First byte a letter or
   `_`; after that, letters, digits, `_`, `-` and `.`. A pattern id starting
   with a digit or a `-` is the one shape that still needs a map — **none of
   the 90 ids today has one** (measured).
2. **`target = <name>`** derives the artifact's C prefix from the name by
   replacing every `-` and `.` with `_`. The exporter writes one such row
   per pattern and never writes the mapping out by hand.
3. **Two names mapping to one prefix is a REFUSAL** naming both. Measured
   over their 90 ids the mapping collides exactly once, on `floor`, and that
   collision is CROSS-SET — each of the four sets has its own `floor.rx` —
   so a per-set export never collides and a merged export would be refused
   with both names in the message. If they ever want one file per BENCH
   rather than per set, they need a disambiguator on that id.
4. **`rx_info.name` keeps the id UNCHANGED**, `-` and all. The prefix is
   what the symbols are called; the name is what the artifact is. A consumer
   walking several `<prefix>_info` symbols in one binary reads the id back
   exactly as they wrote it.
5. **Declare NO `config`/`flags`/`engine`/`budget`/`encoding`** — their own
   condition (O-13 §4(b)), and it is right: D93 makes a source's composed
   config WIN over a command-line flag, so a set file carrying an `engine`
   line would pin the testee matrix from inside the set. Everything about
   HOW a pattern is built stays on the harness's command line.
6. **The pattern line is verbatim and needs no escaping** for their content:
   re-measured across all four sets, all 90 patterns are single-line, ASCII,
   tab-free and free of leading and trailing whitespace, so `pattern <text>`
   is the identity. If a future pattern ever carries a tab or a newline, the
   `.rxt` escape vocabulary (`\t \n \r \\ \xNN`) covers it and
   `--list-source` escapes those three columns on the way out.
7. **A REFERENCE they should know about before relying on it**: a
   hyphenated definition is BUILDABLE as a target and **not callable from a
   pattern**. `(?&some-id)` goes through PCRE2's own group-name grammar,
   which refuses `-`, and D26 makes that PCRE2's rule and not ours to widen.
   Their sets do not call each other, so this costs them nothing today; a
   set whose patterns ever reference each other by id would need identifier
   ids.

Also worth relaying: **the census this lane measured on their own set.**
Under pcrec's default caps, altwide@0.2 is 19 patterns built and 14 refused
(12 on the emitted-size cap, 2 needing module `assertions`, which under
`--features all` also hit the cap). That is the same shape their O-14
reported from the other side, now with pcrec's own numbers and its own
refusal wording attached to each id.

---


---

# PHASE 2 — D89's addenda 1-4 (18:3x–19:0x)

## 9. What changed, and what it cost

Frank ruled Q-W3 the other way. **Delivery is no longer "every named group";
it is TWO declarations, and neither alone does anything**: the definition
lists what it offers (`export a, b`, default NOTHING) and a call site asks
for it (`(?&site=name)`). §§1-8's model — every named group injected flat
into the caller's table — is **withdrawn and removed, not left dormant**.

What SURVIVED unchanged: the composer's spine, the three tiers, the MAP that
replaced the offset, the name grammar with `-`/`.`, the prefix mapping and
its collision refusal, the altwide dogfood, the D94 site list, the abi event.

**Three things forced real restructuring, and each is worth knowing:**

1. **The composer became FOUR PASSES.** Numbering used to happen inside the
   bind, which was right while "which of a definition's groups survive" was
   answerable from the definition alone. Addendum 4(1) makes it a property of
   the whole COMPOSITION — a group survives if it is referenced inside the
   definition or exported AND DELIVERED BY SOME SITE — and the delivering
   sites are not all known until the fixpoint has bound everything, because a
   definition bound later may itself carry the delivering call.
2. **`pcrec_has_live_capture` needed a delivering arm, and without it the
   feature fails silently and completely.** `w1_impl` §2.8's B1 predicted this
   and it reproduced exactly: a composed pattern whose captures all live in
   definitions is the caller's text plus `A_REP{0,0}(A_CAP(body))`, whose
   zero-repetition arm PRUNES — so the whole pattern looks capture-DEAD, takes
   the DFA, and every delivered slot reads `(-1,-1)`. One arm, keyed on the
   CALL and never on the wrapper's shape.
3. **A delivering site is FORCED to `CALL_SPLICE`, for a different reason
   than the design note gave.** §2.2 wanted per-site `W` exclusion. What
   actually forces it is TIMING: under `CALL_LINKAGE` the callee's SHARED
   region restores its whole `W` at its own exit, BEFORE control reaches the
   caller's return label, so a copy at the site would move the caller's own
   values. Under `CALL_SPLICE` the restore is emitted AT the site. This is the
   per-site option `callgraph.c:402-412` declined ON PURPOSE and RESERVED.

## 10. What was MEASURED in phase 2

| # | claim | how | result |
|---|---|---|---|
| M12 | the three new spellings are FREE on libpcre2 | `pcre2_ctypes.py` against libpcre2 10.46 | `(?&site=x)`, `(?&=x)`, `(?&*=x)` all REFUSED, so adopting them re-interprets no legal pattern. Both recorded controls reproduced first: `(?&^.w)` refused, `(?<from>&email)` COMPILES and stays disqualified |
| M13 | the four call forms differ exactly where they should | one fixture, four targets, ONE definition | plain: no rows, `RX_NCAPS` 2. `(?&s=…)`: `s.kept`, `s.other`. `(?&=…)`: `piece.kept`, `piece.other`. `(?&*=…)`: `kept`, `other` |
| M14 | **the per-composition erasure** | the same fixture's plain-call target | `RX_NCAPS` **2** — a definition exporting two of its three groups costs a plain caller NOTHING. A build keeping exported-but-undelivered groups reads 4, and so does the withdrawn every-named-group model |
| M15 | `ref` and `nnames` are one decision seen twice | the emitted rows | a site row carries `ref="piece"` and is NOT counted by `nnames`; a flat row carries `ref=NULL` and IS |
| M16 | **RETENTION delivers real spans** | three delivering targets built, run, compared against addendum 4(2)'s inlined-body oracle | `(?&w=w)` → `w.word` (0,3); `(?&h=hostname)` → `h.host` (3,8); two flat imports → `word` (0,2), `host` (3,6). **Every one agrees with python `re` on the renamed inlined pattern** |
| M17 | two sites of one definition do not alias | `^(?&a=piece)(?&b=piece)$` on "abcabc" | `a.*` = (0,1),(1,2) and `b.*` = (3,4),(4,5); oracle agrees. The definition's own hidden copies read (-1,-1) throughout |
| M18 | identity (A) still holds | a compiler built from `main` vs this branch | **176 artifacts, 0 differing** under `--features all` after the restructure |
| M19 | eight refusals, each once | single compiles | export-names-no-group; delivering-call-on-a-non-exporter; flat-import clash with a caller group; two flat imports clashing; two sites sharing a name; a delivering call to a LOCAL group; a definition's `encoding` differing from the artifact's; a delivering call to a recursive definition |

## 11. Two defects found in phase 2, both in checks rather than in code

1. **The forced splice had a flag that turned it off.** It was first written
   as a branch inside `cg_publish_link`, which is reached from the END of
   `cg_eligibility` — and that function **returns early under
   `PCREC_NO_SPLICE_CALLS`**. So under `-fno-splice-calls` a delivering call
   would have kept `CALL_LINKAGE` silently and delivered nothing: the refusal
   that exists to make a half-feature impossible was itself disabled by a
   flag. It is now its own walk, run on every path, keyed on the FINAL `link`
   value rather than on the eligibility table that produced it.
2. **My first `export`-column change would have stopped the C1 differential
   covering it.** `export` is appended to leg B's dump row after `perr`, and
   the A-vs-B projection truncated with `NF = 13` — which drops `perr`
   deliberately and would have dropped `export` accidentally. A directive
   absent from BOTH sides leaves the differential byte-identical while it
   quietly stops covering that directive, which is the hazard that file's own
   manifest comment names. Both sides now SELECT fields explicitly.

There is also one process note. The first attempt at one commit put backticks
inside a double-quoted shell message and the shell ran the quoted identifier
as a command — lane w12's own recorded defect, met from the other direction:
I had guarded against it in the test scripts and then walked into it in a
commit message. Message files from there on.

## 12. What is left, and one thing I did not build

**The `run.sh` composed-block path is NOT built**, per the manager's own
ordering: it is the LAST item and comes after every suite is green, and no
suite can run under the hold. Its shape is unchanged from §6(4) and is
written out in `tests/definitions/CLAUDE.md`. **If it does not fit tomorrow it
is a W1.3.1 row** — the manager's instruction, and I am saying so at the
point I know it rather than at the end of the day.

**`(?&site.group)` is measured FREE but NOT built**, and the manager asked
either way. It is a call to a delivered group, which needs a reference class
that resolves AFTER composition against the site table — a new
deferred-reference kind rather than a widening of an existing one, so not
cheap in the sense the question meant. Nothing about the rows or retention
forecloses it.

**Everything in §3 is still owed** and phase 2 adds to it: the delivering
path has never been through `make test`, `test-codegen`, the identity gate,
or `mech`. The specific new risks a suite will find first:

- `[M6.5-DUPNAMES]`'s `groups[]` order check — still the most likely red,
  and now for two reasons rather than one (the leading sort key, and rows
  whose names contain a `.`).
- **The forced splice makes a MIXED linkage state reachable** — one callee
  with a spliced delivering site and a shared region for its plain sites.
  `callgraph.c:402-412` reserved this and named three readers that must cope;
  `<PREFIX>_VM_CALLS` can no longer give one answer per callee. Nothing in
  the tree has exercised it before this branch.
- The trail charge grew by `2 * deliver_n` per delivering site. It is 0 on
  every non-delivering pattern, so no existing artifact's arithmetic moves,
  but the frame-buffer suites are where a mistake would surface.

**One judgement worth flagging for the merge.** A FLAT import's rows carry
`ref = NULL` and are counted by `nnames`, so a caller cannot tell them from
groups it declared itself. That is what "flat into the caller's own scope"
has to mean if §6's bsearch is to find them, and the clash refusal is what
pays for it — but it does lose provenance, and an alternative (keep `ref` and
have §6's algorithm span `nentries` for flat rows) exists. I picked the one
that keeps §6's shipped algorithm correct unchanged.

## 8. Disclosure

Spawn-time context that shaped decisions: the repo `CLAUDE.md` (its
situation-index rows on `gnutimeout`, the abi ritual, D80's spec-in-the-
same-change rule, and the general-mechanisms-not-special-cases memory) and
the memory index line for `pcrec-check-design-lessons`, which is what put
the "what must this check NOT share a source with" column in `w1_impl.md`
§8.4 and the outside oracle in `tests/definitions/`.
