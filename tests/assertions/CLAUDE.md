# tests/assertions — module `assertions` ([M6.2])

The module's own corpus and its four non-`.rxt` checks. **WAVES A, B, C AND D
so far**: `\A`, `\Z`, `\z`, `\b`, `\B`, `(?m)` and `\G` are built; `\K` is
recognised, attributed and refused, and lands in wave E
(`docs/design/assertions_design.md` §10). `\K` is now the LAST
enabled-but-unbuilt row in the tree — when wave E lands, tests/reject's whole
`reject_gated assertions` paragraph retires with it.

## THE ORACLE RULE IS DIFFERENT HERE, and it is the first thing to know

CLAUDE.md's project-wide rule is that expectations are oracle-verified with
python3 `re`. **For `\Z` that rule produces WRONG expectations, silently.**
MEASURED, both oracles, by the [M6.1] design lane and reproduced by this one:

| pattern | subject | libpcre2 10.46 | python 3.14 |
|---|---|---|---|
| `b\Z`  | `"ab\n"`  | `(1, 2)` | `None` — no match at all |
| `a*\Z` | `"aaa\n"` | `(0, 3)` | `(4, 4)` — a different SPAN |

**python's `\Z` IS PCRE2's `\z`.** python has no single escape for PCRE2's
`\Z`; the only spelling is `(?=\n?\Z)`, which needs module `lookaround`. Both
divergences run in the dangerous direction — python reports no match, or a
shorter one, exactly where PCRE2 matches — so a cell written from python would
encode `\z` and this suite would go green on a `\Z`-compiled-as-`\z`
miscompile.

**AND FOR `\G` THE ORACLE DOES NOT EXIST AT ALL** ([M6.2] wave D, U11c).
`re.compile(r"\G")` raises `error: bad escape \G`; there is no flag, no
dialect and no rewriting that expresses it, because python's `re` has no way
to assert against a search's start offset from inside a pattern. That is a
TOTAL exclusion rather than U11's wrong-answer one or U11b's different-answer
one, so `gpos.rxt` is `# pcre2-only` in its entirety.

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
- **wordb.rxt** — [M6.2] WAVE B: `\b` and `\B`. **The `ms`/`ns` cells are what
  makes this file different from `absolute.rxt`, and they are not decoration.**
  `\b`/`\B` are the module's first CONTEXT assertions — their truth at a
  position depends on the bytes on EITHER SIDE of it — while
  `<prefix>_search(s, n, startpos, caps)` searches `s[startpos, n)` and
  `s[startpos-1]` sits OUTSIDE that window and INSIDE the subject. A
  `startpos > 0` cell is therefore the only thing in this corpus that can see
  mechanism 4 (`assertions_design.md` §3.8) at all, and 5 of that section's 10
  measured cells differ between searching from `startpos` and searching the
  SLICE — in BOTH directions, so no conservative reading exists.
  **The LEADING `\B` cells at `startpos > 0` carry §3.8.3.1's reverse
  TERMINATION defect, which a leading-`\b` population structurally cannot
  see**: `\b`'s blind assumption (no left context means non-word) coincides
  with its own truth condition, so a `\b`-only suite reports clean against an
  implementation that throws matches away. The named cell is `\Bfoo` on
  `"xfoo"` at startpos 1 → `(1,4)`, and sabotage S74 is its failing direction.
  Also here: both-ended and interior forms, the empty-match family (`\b`,
  `\bx*` — whose start state ACCEPTS, which is what §3.6.1's widened
  `start_acc` is about), composition with `$`/`\z`/`\Z` (§3.6.2's two axes),
  and an ENG_ATTEMPT block, since a `^` routes the pattern to the
  computed-goto engine where §3.6's table and §3.8's seed take a different
  emitted shape. Every expectation libpcre2-produced. **THREE ANCHORED CELLS
  ARE DELIBERATELY ABSENT and the file's own header says which and why** —
  `^\Bfoo`, `^\Bo`, `^a\bb` are never-matching patterns whose emitted C trips
  a PRE-EXISTING `-Werror=maybe-uninitialized` in the `<prefix>_match`
  wrapper (base-tier reproducer `^a^b`, measured on the pre-wave compiler);
  live equivalents stand in their place.
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
  **ONE MID-PATTERN SHAPE IS DELIBERATELY ABSENT and the file's own header
  says which and why**: `a(?m)^b` is a never-matching pattern whose emitted C
  trips the PRE-EXISTING `-Werror=maybe-uninitialized` in the
  `<prefix>_match` wrapper — known issue K28, base-tier reproducer `^a^b`,
  the same exclusion `wordb.rxt` records for three `\b`/`\B` shapes. The live
  equivalents `a(?m)$` and `a(?m)^b|c` stand in its place.
- **gpos.rxt** — [M6.2] WAVE D: `\G`, the first matching position. **The
  `ms`/`ns` cells are the point of this file more sharply than they are even
  in wordb.rxt**: `\G` is true iff `pos == startpos`, so at the default
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
  **`a\Gb` AND `x\G` ARE DELIBERATELY ABSENT and the file's own header says
  which and why** — both compile to a single dead state, K28's shape, so their
  artifacts are not warnings-clean under the harness's `-O1` GENCFLAGS. This
  is the THIRD wave to add spellings to K28's exclusion list, which that
  entry's own text predicts. `run_gstart_diff.sh` §4 asserts them instead, at
  `-O2`.
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
  pass.
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

and three more live outside this directory entirely.
`tests/codegen/run_endvar_identity.sh` is the byte-identity gate for the claim
that `\z`'s third closure view costs a `\z`-free pattern nothing; its failing
direction is sabotage S69 — the design's own refuted first draft, restored.
`tests/codegen/run_wordctx_identity.sh` is wave B's, for the much larger claim
that the alphabet refinement, the second closure, the class-indexed accept and
the third start state cost a `\b`-free pattern nothing (sabotage S71 — but
read that row's annotation first: wave D MEASURED its identity sweep staying
1135/1135 identical under it, so the row is scored detected only through an
orphaned-parameter warning).
`tests/codegen/run_gstart_identity.sh` is wave D's, for the claim that the
`\G` closure bit, the second start family, the `gseed[]` table, the three-way
dispatch and the third `start_max` string cost a `\G`-free pattern nothing
(sabotage S83). **Its reference knob is at the EMITTER rather than in the
analysis**, which is what makes S83 visible where the same shape is invisible
to its two predecessors, and moving it is what found a dead `gseed[]` table
this wave had emitted on every `\b`/`(?m)` artifact. And
`tests/codegen/run_codegen_tests.sh`'s `[M6.2-WORDB]` block carries three
rules no correctness test can see — no accept table indexed at `pos == n`
(§3.6.2, sabotage S73), no `sfound` recorded blind at the reverse boundary by
ANY writer including the skip's (§3.8.3.1, sabotage S72), and exactly one
word-set spelling per artifact (§7.2 item 3).

## Maintenance

Update this file when files are added or removed. When a later wave lands a
construct, the pair to move together is: `tests/reject/`'s `reject_gated
assertions` row for it (delete — it is built now) and this directory's own
cells (add). Leaving the first behind turns a true statement into a false one
the day the producer lands, which is exactly the `(?J)` wording history
recorded in `src/parse/mod_modifiers.c`.
