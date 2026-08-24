# tests/assertions — module `assertions` ([M6.2])

The module's own corpus and its FIVE non-`.rxt` scripts (plus three drivers they compile). **ALL FIVE WAVES ARE
IN**: `\A`, `\Z`, `\z`, `\b`, `\B`, `(?m)`, `\G` and `\K` are built, which
is every construct module `assertions` owns
(`docs/design/assertions_design.md` §10). tests/reject's whole
`reject_gated assertions` enabled-but-unbuilt paragraph retired with wave E —
and NOT the mechanism behind it, which turned out to have a large live
population in other modules; see that file for the measurement and where the
pin was re-homed to.

## THE ORACLE RULE IS DIFFERENT HERE, and it is the first thing to know

CLAUDE.md's project-wide rule is that expectations are oracle-verified with
python3 `re`. **For `\Z` that rule produces WRONG expectations, silently.**
MEASURED, both oracles, by the [M6.1] design lane and reproduced by this one:

| pattern | subject | libpcre2 10.46 | python 3.14 |
|---|---|---|---|
| `b\Z`  | `"ab\n"`  | `(1, 2)` | `None` — no match at all |
| `a*\Z` | `"aaa\n"` | `(0, 3)` | `(4, 4)` — a different SPAN |

**python's `\Z` IS PCRE2's `\z`.** python has no single escape for PCRE2's
`\Z`; the only spelling is `(?=\n?\z)`, which needs module `lookaround`. Both
divergences run in the dangerous direction — python reports no match, or a
shorter one, exactly where PCRE2 matches — so a cell written from python would
encode `\z` and this suite would go green on a `\Z`-compiled-as-`\z`
miscompile.

**AND FOR `\G` AND `\K` THE ORACLE DOES NOT EXIST AT ALL** ([M6.2] waves D
and E, U11c and U11d). `re.compile(r"\G")` raises `error: bad escape \G` and
`re.compile(r"a\Kb")` raises `error: bad escape \K`; there is no flag, no
dialect and no rewriting that expresses either, because python's `re` has no
way to assert against a search's start offset from inside a pattern and no way
for a pattern to move its own match's REPORTED START. Those are TOTAL
exclusions rather than U11's wrong-answer one or U11b's different-answer one,
so `gpos.rxt` and `kreset.rxt` are `# pcre2-only` in their entirety.

**THE LIST IS NOW COMPLETE, AND THAT IS WHAT MAKES IT A STATEMENT ABOUT FOUR
CONSTRUCTS RATHER THAN ABOUT THE MODULE.** THREE of the module's eight
constructs are excluded WHOLLY — `\Z` (python answers WRONGLY), `\G` and
`\K` (python has no such escape) — and a fourth PARTLY: `(?m)`, whose `^`
half python answers DIFFERENTLY while its `$` half agrees. `\A`, `\z`, `\b`,
`\B` and `(?m)$` are python-verified cell for cell at 0 divergences. A reader
deciding whether a new cell can be python-verified should check WHICH
construct it uses — and, for `(?m)`, which half — never assume the directory's
rule.

**DO NOT REACH FOR A LOOKBEHIND TO GET `\K` A PYTHON ORACLE.** `(?<=a)b` is
close to `a\Kb` and is not the same construct — different backtracking, and
it cannot express the variable-width shapes `\K` exists for — so a cell
written that way would encode a translation and then check the translation.
It also needs module `lookaround`, which SHIPS since [M6.6.2] — so the reason
this paragraph stands is now the FIRST one alone (a lookbehind is a different
construct, not a translation of `\K`), and no longer the availability of the
module.

**Every block whose pattern contains `\Z` therefore carries `# pcre2-only`**
(which makes `tests/harness/verify_rxt.py` skip it) and is verified against
libpcre2 by `verify_pcre2.py` instead. The rule is applied to every `\Z` block
whether or not this directory's own subject set happens to expose the
divergence on it: a subject added later must not silently start lying. `\A`
and `\z` blocks are python-verifiable and are deliberately NOT marked — python
3.14's `\z` has PCRE2's meaning and its `\A` has PCRE2's absolute semantics
under `pos`, checked cell for cell at 0 divergences.

Recorded as `docs/dev/upstream_issues.md` U11, per the standing rule that
every oracle exclusion has an entry there.

## Files

- **absolute.rxt** — `\A`, `\Z`, `\z`: the three-way position distinction
  (`b\Z` on `"ab\n"` matches at `(1,2)`, `b\z` does not, `b$` agrees with
  `\Z`), the bare assertions at every position of fifteen subject shapes,
  `startpos` behaviour (`\A` is absolute offset 0 — it is A_BOL, the node `^`
  builds — so it is not satisfied at a nonzero `startpos`), anchored literals,
  quantifier interactions, alternation and grouping, and the syntax refusals
  with the module ENABLED (a bare quantified anchor is PCRE2 error 109 and a
  GROUPED one compiles; both halves are here, because a rule tested in one
  direction is not tested). Every expectation produced by libpcre2 through
  `tests/fuzz/pcre2_oracle`, never written by hand.
- **gate.rxt** — the D47.5 possessification gate from the assertions side
  (`assertions_design.md` §8; D62). The `$`-follow shapes `eng_brep_design.md`
  §2.5 measures safe, the same shapes with `\z` and with `\Z` in the follow,
  and the FAILING DIRECTION (`\A`/`^` in the follow, which must make the
  analysis decline). It cannot see whether a quantifier was possessified —
  that is what `run_assertions_tests.sh`'s STRATS check is for — and it cannot
  see the scoped-`(?m)` miscompile at all, because `(?m)` does not compile
  yet. **D62's controls 1 and 2 (the widened scoped test cells, the permanent
  flag-reader sabotage) belong to WAVE C**, where the flag can actually be
  true and those rows can actually go red; writing them now would be a check
  with no failing direction.
- **wordb_basic.rxt, wordb_empty_compose.rxt, wordb_engattempt.rxt,
  wordb_vm.rxt** — [M6.2] WAVE B: `\b` and `\B`, in four shards. **Split
  2026-08-21** ([M6.2.2] plan row) along the corpus's own section
  boundaries so `tests/harness/run.sh`'s file-granularity `PROCS=N`
  parallelism does not serialize the corpus section's wall time behind one
  4,608-case file; every case moved verbatim (proven by a byte-diff of the
  section bodies against the pre-split file). **The `ms`/`ns` cells,
  present in all four, are what makes this corpus different from
  `absolute.rxt`, and they are not decoration.** `\b`/`\B` are the module's
  first CONTEXT assertions — their truth at a position depends on the bytes
  on EITHER SIDE of it — while `<prefix>_search(s, n, startpos, caps)`
  searches `s[startpos, n)` and `s[startpos-1]` sits OUTSIDE that window
  and INSIDE the subject. A `startpos > 0` cell is therefore the only thing
  in this corpus that can see mechanism 4 (`assertions_design.md` §3.8) at
  all, and 5 of that section's 10 measured cells differ between searching
  from `startpos` and searching the SLICE — in BOTH directions, so no
  conservative reading exists.
  - **wordb_basic.rxt** — the plain, un-anchored, non-capturing forms: the
    ten §3.8 cells (`\bfoo`, `\Bfoo`, `foo\b`, `foo\B`) and both-ended /
    interior forms (`\bfoo\b`, `\b\w+\b`, `a\bb`, …). **The LEADING `\B`
    cells at `startpos > 0` carry §3.8.3.1's reverse TERMINATION defect,
    which a leading-`\b` population structurally cannot see**: `\b`'s blind
    assumption (no left context means non-word) coincides with its own
    truth condition, so a `\b`-only suite reports clean against an
    implementation that throws matches away. The named cell is `\Bfoo` on
    `"xfoo"` at startpos 1 → `(1,4)`, and sabotage S74 is its failing
    direction. Carries the family-wide header (oracle rule, mechanism-4
    background) the other three shards point back to.
  - **wordb_empty_compose.rxt** — the empty-match family (`\b`, `\bx*` —
    whose start state ACCEPTS, which is what §3.6.1's widened `start_acc`
    is about) and composition with the module's other position assertions,
    `$`/`\z`/`\Z`/`\A` (§3.6.2's two axes: the view axis by position, the
    class axis by next byte, scalar at `pos == n`). The two `\Z` blocks
    here (`\bfoo\Z`, `\Bo\Z`) carry `# pcre2-only`.
  - **wordb_engattempt.rxt** — the ENG_ATTEMPT block: every pattern here
    leads with `^`, which routes it to the computed-goto engine, where
    §3.6's table and §3.8's seed take a different emitted shape (baked into
    the label body rather than read from an array) than a corpus with no
    `^` cells would ever exercise. **THREE ANCHORED CELLS WERE DELIBERATELY
    ABSENT AND ARE NOW BACK** ([M6.2] repair slice, 2026-08-19) — `^\Bfoo`,
    `^\Bo`, `^a\bb`, never-matching patterns whose emitted C tripped a
    PRE-EXISTING `-Werror=maybe-uninitialized` (K28, base-tier reproducer
    `^a^b`) until that wrapper was fixed. The live equivalents STAY beside
    them: same impossibility, live sibling branch, different emitted shape.
  - **wordb_vm.rxt** — the VM half: every block here carries a capturing
    group, which forces VM routing (`src/opt/select_engine.c`'s
    `forces_captures`). Its ABSENCE was measured: sabotage S75 first came
    back UNDETECTED because every pre-existing block in the corpus was
    capture-free, so nothing reached `src/gen/emit_vm.c`'s `\b` arm at all
    — this shard exists because that measurement found the gap. Includes
    the `ms`/`ns` cells on the VM's own guarded spelling (design §9.3,
    which reads `s[pos-1]` directly and has no mechanism-4 seed to get
    wrong), pinned separately from the DFA's rather than assumed identical.
  Every expectation in all four shards libpcre2-produced.
- **multiline.rxt** — [M6.2] WAVE C: `(?m)`. **The SCOPING is what makes this
  file different from the other two.** `(?m)` is a scoped inline option, so
  the answer depends on the state in force AT EACH `^`/`$` rather than on the
  pattern's final option state — and the shipped pre-cure code got the
  leading-`(?m)` shape right and every other spelling wrong, which is D47.5's
  addendum and D62's control 1. So the file carries `(?m:...)`,
  `(?m)...(?-m)`, a mid-pattern `(?m)`, a trailing `(?m)`, and a section where
  a multiline `$` and a non-multiline `$` occur in the SAME compile — cells
  nothing but a per-node resolution can answer, because a pass-wide flag has
  one value.
  Also here: §8.7's four D47.5 gate cells (the recommended guard is
  `(?m)[^c]{1,3}$` on `"a\nc"` → `(0,1)`, the strongest of the four because a
  possessified compile produces NO MATCH AT ALL and the cell cannot pass by
  accident on an off-by-one — sabotage S77 is its failing direction); the
  `(?m)$`-with-quantifier family §3.6.1 names as the population the
  scan-avoidance cure can actually break; `(?m)^` shapes for D63's
  candidate-start prefilter; `\A`/`\Z`/`\z` under `(?m)`, which is the
  failing direction for `mod_assertions.c`'s pinned-false flag; and `(?m)`
  composed with `\b`, the case that makes the class axis three-valued rather
  than a bool.
  **ORACLES, and the split is wider than the other two files'.** A leading
  `(?m)` and `(?m:...)` are verifiable against BOTH python3 `re` and libpcre2
  and every such cell agrees on both. Python rejects a bare `(?-m)`, a
  mid-pattern `(?m)` and a trailing `(?m)` OUTRIGHT ("global flags not at the
  start of the expression"), so those blocks carry `# pcre2-only` — the same
  convention wave A established for `\Z`, applied for a different reason
  (python cannot express the pattern at all, rather than expressing it with
  different semantics). Every expectation libpcre2-produced.
  **ONE MID-PATTERN SHAPE WAS DELIBERATELY ABSENT AND IS NOW BACK**
  ([M6.2] repair slice, 2026-08-19): `a(?m)^b`, a never-matching pattern
  whose emitted C tripped the PRE-EXISTING `-Werror=maybe-uninitialized`
  (K28, base-tier reproducer `^a^b`) until that wrapper was fixed. The live
  equivalents `a(?m)$` and `a(?m)^b|c` STAY beside it.
- **gpos.rxt** — [M6.2] WAVE D: `\G`, the first matching position. **The
  `ms`/`ns` cells are the point of this file more sharply than they are even
  in the wordb shards**: `\G` is true iff `pos == startpos`, so at the default
  `startpos == 0` it is INDISTINGUISHABLE from `\A` on every subject, and a
  corpus written entirely at offset 0 would go green on a compiler that
  lowered `\G` to `A_BOL`. Every block sweeps startpos across the whole
  subject, and the `\Ax` / `\Gx` pair in section 5 is the explicit control.
  Also here: the fully-anchored family (`start_max = startpos`), the partial
  family (`\Gfoo|bar`, where the three start states are visible from outside),
  the impossible mid-pattern shape carried on live sibling branches, `\G`
  composed with `\A`/`\z`/`$`/`\b`/`(?m)^` — the last of those being D63's
  prefilter cell, whose failing direction (sabotage S82) exists only in the
  INTERSECTION of waves C and D — the grammar refusals with the module
  enabled, and section 7's possessification witnesses as ANSWERS rather than
  as a stamp (sabotage S84). Every expectation libpcre2-produced; the whole
  file is `# pcre2-only`, see above.
  **`a\Gb` AND `x\G` WERE DELIBERATELY ABSENT AND ARE NOW BACK** ([M6.2]
  repair slice, 2026-08-19) — both compile to a single dead state, K28's
  shape, so their artifacts were not warnings-clean under the harness's `-O1`
  GENCFLAGS until that wrapper was fixed. They were the THIRD wave's
  additions to an exclusion list that CLOSED AT SIX. `run_gstart_diff.sh` §4
  still asserts the class over its own generated sweep at `-O2`; these cells
  pin the two named shapes.
- **kreset.rxt** — [M6.2] WAVE E: `\K`, which RESETS THE REPORTED START.
  **This file is different from every other one here in what its cells are
  ABOUT.** The other four corpora ask "does this assertion hold at this
  position"; `\K` is not an assertion — it asks nothing, cannot fail, and has
  a SIDE EFFECT — so the interesting cells are the ones where several
  candidate writes compete and only one SURVIVES to the end of the winning
  path. Three families carry the file and none is decoration:
  the UNDO cells (§3, §4), where a `\K` is crossed on a path that then
  LOSES — `(?:a\K|ax)c` on `"axc"` is (0,3), so the write of 1 must be GONE,
  and `(?:a\K)*ab` on `"aaab"` is (2,4), so the third iteration's write must
  be gone AND the second's must stand (a trail that CLEARED instead of
  restoring gets the first right and the second wrong; sabotage S86 fires on
  exactly 6 cases, all here); the NOT-CROSSED cells (§5), where the artifact's
  PCREC_UNSET means "no `\K` on this path" and `(?:a\K)?b` answers (1,2) on
  `"ab"` and (0,1) on `"b"`; and the START == END cells (§6), where `ab\K`
  reports the empty span (2,2) after consuming two bytes — the only place in
  the tree the reported width and the consumed length differ, and the reason
  the match-here entries' RETURN is a separate question from their span.
  Also here: `\K` with captures (a group that starts BEFORE the reported
  match start, `g` lines LIVE since `\K` forces the VM), `\K` composed with
  all seven of the module's other constructs — `\Ga\Kb` being the sharpest,
  the only pattern carrying both constructs that need something from outside
  `(s, n, pos)` — and the grammar refusals with the module enabled.
  Section 11 is the file's own capacity witness and exists for a sabotage:
  `\K` is the only member of this module that is NOT free to `vm_cost` (its
  write is a trail entry), and the shallow cells cannot see a missing charge
  because a one-write pattern fits the capacity anyway. `(?:a\K){0,10}ab`
  declares 13 trail entries and, with the charge removed, declares 3 and
  returns `PCREC_ERR_FRAMES` from eleven `a`s onward. The subjects there are
  chosen to EXCEED the repeat's count rather than to be long — sabotage S87,
  which `codegen` cannot see at all.
  `ms`/`ns` cells throughout, for a THIRD reason after wave B's and wave D's:
  the reported start is the one quantity `\K` can move and a nonzero startpos
  also moves, so a cell at startpos > 0 is what distinguishes "the VM reported
  its `\K` write" from "the prefilter's span start was written out".
  Every expectation libpcre2-produced; the whole file is `# pcre2-only`.
  **NOTHING IS EXCLUDED FROM THIS FILE.** It is the first wave since B to add
  no spelling to K28's list — no shape here compiles to a single dead state.
- **kreset_entries.c** — [M6.2] WAVE E's driver, and the only one in the tree
  that drives ALL THREE entries of one artifact (`<prefix>_search`,
  `<prefix>_match`, `<prefix>_match_caps`) side by side. `\K` is what makes
  the third one necessary: `<prefix>_match` delivers no captures, so its
  RETURN is the only thing a caller — a D38 callout among them — can act on,
  and on a `\K` pattern that number and the reported span are different
  quantities. Driving only the caps-delivering sibling would print a
  plausible pair and miss the one an entry deriving its return from `caps`
  gets wrong.
- **run_kreset_diff.sh** — [M6.2] WAVE E's behavioural instrument, run by
  `make test-assertions`. Six sections: the subject sweep on both engines with
  startpos taking EVERY value in `[0, n]`; THE THREE ENTRIES against libpcre2;
  the ADVANCE property by name; the `--engine=dfa` refusal in both directions;
  docs/spec/match_api.md §3.1's FIND-ALL LOOP against libpcre2 driven through
  the same loop — the empty-reported-span arm `\K` is what makes reachable,
  with the population counted from the ORACLE so pcrec cannot vouch for its
  own coverage; and `--no-captures`, which sounds like it conflicts with `\K`
  and does not (the flag drops GROUP slots, the whole-match span is not a
  group, so the artifact is still VM-routed and still reports the post-`\K`
  start). No `.rxt` block can pass that flag, which is the same reason
  `run_assertions_tests.sh` §2b exists one construct family over.
  **ITS ORACLE FOR THE MATCH-HERE ENTRIES IS `\G`, and that is the idea the
  script turns on.** `tests/fuzz/pcre2_oracle` has no anchored mode, so there
  is no flag with which to ask libpcre2 "does this match AT offset sp" — but
  PCRE2 already has a spelling for it, and wave D built it: `\G(?:PAT)` at
  startpos `sp` IS that question. Two things fall out with no arithmetic of
  the script's own: a match there means the entry must not reject it (the
  FILTER half), and the oracle's match END minus `sp` IS the consumed length
  (the RETURN half), which on a `\K` pattern is generally not `end - start`.
  A NON-VACUITY counter reports how many cells have those two numbers
  DIFFERING, because without it the whole section could be passing on cells
  where they coincide — which is every cell of every `\K`-free pattern.
  **THE POPULATION CLAIM IS CHECKED**, as in its two siblings: every
  pattern's artifact is inspected for BOTH halves of the machinery (the
  trailed write and the `\K`-aware `caps_out`), the table is printed every
  run, and a pattern carrying only one is reported by name — because either
  half alone reports the prefilter's start and a sweep would pass over it.
  **The python arm** is wave D's, on `\K`-free controls, for U11d's reason.
- **gstart_findall.c** / **gstart_entries.c** — [M6.2] WAVE D's two drivers,
  each for a property no `.rxt` block can express. The first is
  docs/spec/match_api.md §3.1's find-all loop, TRANSCRIBED from
  tests/encseam/findall_driver.c rather than re-interpreted (the claim is
  about what §3.1's loop does, so a second reading of §3.1 would prove
  nothing); the second drives `<prefix>_search` and `<prefix>_match_caps` side
  by side on one artifact, which is R30 E8's replacement obligation.
- **run_gstart_diff.sh** — [M6.2] WAVE D's behavioural instrument, run by
  `make test-assertions`. Four sections: find-all CONTIGUITY against libpcre2
  driven through the SAME §3.1 loop (never a hand-written span list); a
  subject sweep on both engines with startpos taking EVERY value in `[0, n]`;
  the SCOPED entry test (fully-`\G` patterns must agree, partial ones must
  DISAGREE — an unscoped version would be red on correct behaviour); and the
  K28-excluded impossible shapes.
  **THE STARTPOS AXIS IS SWEPT EXHAUSTIVELY where wave C's sweep uses two
  values, and that is not thoroughness for its own sake**: `(?m)`'s truth is a
  fact about the SUBJECT, `\G`'s is a fact about the ARGUMENT, so a sweep that
  fixes the argument measures nothing about the construct.
  **THERE IS NO SECOND ORACLE HERE and §0 is what remains of one.** Wave C
  runs python beside libpcre2 to catch the SCRIPT driving the oracle wrongly;
  python cannot express `\G` at all, so that arm points at the sweep's own
  `\G`-free CONTROL patterns instead — same subjects, same startpos values,
  same oracle invocation. Weaker than wave C's, and the strongest available.
  Its population claim is checked the way run_mline_diff.sh's is: every
  pattern's artifact is inspected for the `\G`-aware start dispatch and the
  script FAILS if too few carry one.
- **run_mline_diff.sh** — [M6.2] WAVE C's DIFFERENTIAL SWEEP, run by
  `make test-assertions`. A `.rxt` file pins chosen cells; this sweeps a
  generated subject space over the `(?m)$` family against libpcre2 and
  python3 `re`, on BOTH pcrec engines.
  **It exists because of what §3.6.1 says can break.** `\b`'s accept bit is
  pinned across a skipped run; `(?m)$`'s is not — "is the next byte a
  newline" genuinely varies inside a run a skip set admits — so this is the
  only population in the tree where a scan-avoidance mechanism can jump past
  an accepting position. D11's own record is why it is measured rather than
  argued: the first attempt at M2.12 got rule 1 right and still produced 53
  divergences over 27 patterns x 69 subjects.
  **THE POPULATION CLAIM IS CHECKED, NOT ASSUMED**: every pattern's artifact
  is inspected for a LIVE mechanism (`_fs<N>`/`_rs<N>` skip tables, a
  `memchr`, a `_first[]` bitmap, a class-indexed accept), the per-pattern
  table is printed every run, and the script FAILS if too few carry one — a
  sweep over patterns the cure never touches would be green against a
  completely broken cure.
  **The python arm checks the ORACLE, not pcrec**, and says so: D26 makes
  libpcre2 the truth, so "python agrees with pcrec" adds nothing once pcrec
  agrees with libpcre2. What python CAN see is this script driving the oracle
  wrongly — a startpos convention, a subject that lost a byte — because it
  shares no code with libpcre2. Patterns python cannot express are SKIPPED
  and COUNTED, never silently passed.
  Its own first run reported 366 "divergences" that were entirely
  `startpos > n` cells on the empty subject, where libpcre2 returns
  BADOFFSET; the skip is now explicit and the skipped count is printed.
- **verify_pcre2.py** — the libpcre2 oracle for this directory's corpus.
  IMPORTS `tests/harness/verify_rxt.py`'s `.rxt` parser rather than copying it
  (one implementation of the file format) and builds
  `tests/fuzz/pcre2_oracle.c` rather than carrying a third ctypes binding (one
  libpcre2 access path, the one PC-3 and the fuzzer already share). SKIPS
  LOUDLY when libpcre2 is absent — exit 0 with a skip line, never a silent
  pass. Since the [M6.2] d27 merge review it also skips-and-COUNTS any block
  carrying a `flags` directive: the shared oracle binary is pinned at
  options=0 by deliberate project-wide rule, so a flagged block is outside
  its domain, and before this it was MIS-VERIFIED (with-flags expectation
  vs without-flags oracle — wrong in the silent direction; the d27 corpus's
  one `flags i` cell was scored a disagreement, the first flagged block this
  directory ever carried). Spell per-block caselessness inline (`(?i)...`)
  to keep a cell verifiable here.
- **d27/** — the [M6.2] D27-BLINDED ACCEPTANCE CORPUS, written at module
  close from the PCRE2 goal by an author denied `src/` and `tests/`
  (cell allowlist: docs/testing.md, docs/spec/match_api.md, build/ — see
  d27/README.md, which is the acceptance record and stays as authored).
  8 topic files, 145 blocks: the eight constructs alone and composed,
  startpos context cells, the \Z/\z/$ trailing-newline triad, hand-replayed
  §3.1 find-all loops for \G and \K, PCRE2 syntax rejections, and the
  feature-gating direction (including the measured fact that `(?m)` is a
  TWO-module construct — `modifiers` owns the group syntax, `assertions`
  the multiline effect; gating.rxt exercises all four combinations).
  ORACLE MECHANICS DIFFER FROM THE PARENT DIRECTORY, deliberately: no
  block carries `# pcre2-only` (that marker serves verify_rxt.py, which
  has no automated invocation over this tree and none over d27/); instead
  d27/oracle.py — the author's own independent re-checker, over its
  ctypes binding d27/lib_pcre2.py, a THIRD libpcre2 access path that
  exists because the author's cell had no tests/fuzz/ — re-verifies every
  cell, and verify_pcre2.py's own recursive walk covers d27/ on every
  `make test` as well (two independent checkers, no shared parser on the
  author's side). The 18 `# pcrec-gate-only` perr blocks in gating.rxt
  are pcrec POLICY (module gates), not PCRE2 facts — valid PCRE2 patterns
  deliberately refused — so BOTH checkers skip them and run.sh is what
  asserts them. d27/mkcorpus.py is provenance only; nothing trusts it.
  At merge review the corpus ran 0 divergences against the shipped module
  (the acceptance result), and returned one two-sided finding: the
  `flags i` cell vs the options=0 oracle pin, resolved by respelling the
  cell inline and by verify_pcre2.py's flags-skip guard above.
- **run_assertions_tests.sh** — the three things a `.rxt` file structurally
  cannot check, run by `make test-assertions`:
  1. the libpcre2 re-verification above;
  2. the CONTROL under `tests/reject/`'s two-answer pins — the constructs the
     module has BUILT must COMPILE with the gate open (wave B added `\b`/`\B`
     here as it deleted their rows over there, in the same change; both a
     LEADING and a TRAILING spelling of each, because the two reach different
     machinery — the forward seed and the reverse one — and a control that
     only ever compiled the leading form would not notice the reverse half
     failing to build; wave C added the four `(?m)` spellings on the same
     move as it retired their two reject rows — the bare run, the scoping
     form, the unset `(?-m)` and a `(?m)^`, because those take four different
     paths and the last one ROUTES TO ENG_ATTEMPT, where a build failure
     would otherwise surface only as a slow pattern). The refusal
     TEXTS live in tests/reject/ (the house home for "which module does a
     diagnostic name", both gate states adjacent in its `== assertions ==`
     section); what cannot live there is the fact that stops the
     "is not implemented yet" rows measuring an EMPTY module rather than a
     partly-landed one;
  3. the D47.5 exemption ACTUALLY FIRING, read off the artifact's own
     `<PREFIX>_VM_STRATS` stamp in both directions — `\z`/`\Z`/`$` in the
     follow must possessify, `\A`/`^`/`\b`/`\B` must not. A possessified
     quantifier and a backtracking one match identically by construction, so
     `gate.rxt` stays green either way; the stamp is the only thing that can
     see it. Wave B's own rows are the last two: the exemption rests on UPWARD
     CLOSURE and a word boundary is closed in NEITHER direction (`\w{0,4}\b`
     on "abcd" is a boundary at the maximal exit 4 and not at the retreat 3),
     so `\b` must take `^`'s arm and not `$`'s;
  4b. [M6.2 wave E] THE ENGINE STAMP ON A `\K` ARTIFACT, on all THREE
     surfaces that carry it — `RX_ENGINE`, `RX_ENGINE_WHY` and
     `rx_info.engine` — because they are produced at different places and a
     build could get one right while another says nothing (D43 makes the
     STRUCT canonical and keeps the macros for compile-time consumers). The
     WHY is the interesting half: a capture-free `\K` pattern must be
     explained as `\K`, since "capture group" would send a user to
     `--no-captures`, which cannot help. Its control is a `\K`-free capture
     pattern, VM-forced for the OTHER reason — without it, a build that
     stamped `\K` on everything, or that had hardcoded the VM, would pass.
  4. [M6.2 wave B] that the COMPOSED STATE BUDGET (§3.5.1) REFUSES rather
     than miscompiling, on BOTH caps — `PCREC_MAX_DFA_STATES_TABLE` for
     ENG_UNANCH and the 3.2x tighter `PCREC_MAX_DFA_STATES_GOTO` for
     ENG_ATTEMPT, which §3.4.1 discloses the design's whole corpus
     measurement was blind to. The check pins the PROPERTY (states-cap
     diagnostic, no output file written) and not the boundary's location: the
     located boundary is a MEASUREMENT and lives in
     `docs/design/assertions_measurements/out/wordctx_budget.txt`. Its
     control is the same family an order of magnitude smaller, which must
     compile.

## What guards what, and why none of it substitutes for another

Four instruments touch this module and they see different things:

| instrument | sees |
|---|---|
| `tests/harness/run.sh` over `*.rxt` | what pcrec's emitted matcher ANSWERS |
| `verify_rxt.py` | whether the non-`\Z` expectations describe python `re` |
| `verify_pcre2.py` | whether ALL of them describe libpcre2 — the only check that can validate a `\Z` cell |
| `run_assertions_tests.sh` | the gate's two answers, and whether the possessification exemption fired |
| `run_gstart_diff.sh` | what `\G` means under §3.1's find-all LOOP, and what the two ENTRIES of one artifact answer — neither expressible as a `.rxt` cell |
| `run_kreset_diff.sh` | what the THREE entries answer about an ANCHORED match, and whether the consumed length is derived from positions or from `caps` — a number no span comparison contains |

and three more live outside this directory entirely.
`tests/codegen/run_endvar_identity.sh` is the byte-identity gate for the claim
that `\z`'s third closure view costs a `\z`-free pattern nothing; its failing
direction is sabotage S69 — the design's own refuted first draft, restored.
`tests/codegen/run_wordctx_identity.sh` is wave B's, for the much larger claim
that the alphabet refinement, the second closure, the class-indexed accept and
the third start state cost a `\b`-free pattern nothing (sabotage S71). **Its
reference knob was RE-PLACED by the [M6.2] repair slice, 2026-08-19**: wave D
measured the sweep staying 1135/1135 identical under S71, so the row was
scored detected only through an orphaned-parameter warning; with the knob
around the refinement ACTION rather than around the `has_word` FLAG, S71 now
moves 1178 of 1186 artifacts. Same re-placement on wave C's
`run_mlinectx_identity.sh` (S76). Wave A's `run_endvar_identity.sh` was
already at its action and did not move.
`tests/codegen/run_gstart_identity.sh` is wave D's, for the claim that the
`\G` closure bit, the second start family, the `gseed[]` table, the three-way
dispatch and the third `start_max` string cost a `\G`-free pattern nothing
(sabotage S83). **Its reference knob is at the EMITTER rather than in the
analysis**, which is what makes S83 visible where the same shape is invisible
to its two predecessors, and moving it is what found a dead `gseed[]` table
this wave had emitted on every `\b`/`(?m)` artifact. **Wave E deliberately built NO identity gate**, which is the one place this
module's waves differ in shape: `\K` is VM-forced and the emitter reads its
counter into a DEFAULT ARTIFACT at exactly ONE site, so "a `\K`-free pattern
pays nothing" is a claim about one predicate rather than about a
construction. It is pinned as
`[M6.2-KRESET rule 1b]`, which quotes the pre-wave `caps_out` body as a
LITERAL so a rewrite into a third shape fails too; the corpus-wide half was
measured ONCE against the genuine pre-wave COMPILER (1,208/1,208 default,
1,209/1,209 under `--engine=vm`), a reference sharing no sources with the
subject and therefore immune to the cancellation wave D measured in the knob
builds. And
`tests/codegen/run_codegen_tests.sh`'s `[M6.2-WORDB]` block carries three
rules no correctness test can see — no accept table indexed at `pos == n`
(§3.6.2, sabotage S73), no `match_start_position` recorded blind at the reverse boundary by
ANY writer including the skip's (§3.8.3.1, sabotage S72), and exactly one
word-set spelling per artifact (§7.2 item 3) — and its `[M6.2-KRESET]` block
carries wave E's four: `caps[0][0]`'s PROVENANCE on a `\K` artifact and on a
`\K`-free one (sabotages S85 and S86, with DISJOINT symptoms, which is why
they are two rows), and the two match-here entry SHAPES, the second checked
on a `\K`-free artifact because a `\K` pattern never has a DFA entry to
inspect.

## Maintenance

Update this file when files are added or removed. The five waves are in and
the pair-to-move-together rule below has no remaining customer in this
module — kept because the next partially-landed module inherits it verbatim.
When a later wave lands a construct, the pair to move together is:
`tests/reject/`'s `reject_gated` row for it (delete — it is built now) and the
module's own cells (add). **Wave E adds a third item that wave D's note got
wrong**: do NOT also delete the enabled-but-unbuilt MECHANISM when a module's
last row leaves. Its population is every registry row whose module is enabled
and whose port is unwired, which is large and live; what has to move is the
PIN, and wave E re-homed it to `backrefs`/`lookaround`/`atomic-groups`/
`quoting` in the same change. Leaving the first behind turns a true statement into a false one
the day the producer lands, which is exactly the `(?J)` wording history
recorded in `src/parse/mod_modifiers.c`.
