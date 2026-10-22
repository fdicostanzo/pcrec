# tests/assertions — module `assertions` ([M6.2])

The module's own corpus and its FIVE non-`.rxt` scripts (plus three drivers they compile). **ALL FIVE WAVES ARE
IN**: `\A`, `\Z`, `\z`, `\b`, `\B`, `(?m)`, `\G` and `\K` are built, which
is every construct module `assertions` owns
(`docs/design/assertions_design.md` §10). tests/reject's whole
`reject_gated assertions` enabled-but-unbuilt paragraph retired with wave E —
and NOT the mechanism behind it, which turned out to have a large live
population in other modules; see that file for the measurement and where the
pin was re-homed to.

## Files

- **absolute.rxt** — `\A`, `\Z`, `\z`: the three-way position distinction (`b\Z` on `"ab\n"` matches at `(1,2)`, `b\z` does not, `b$` agrees with `\Z`), the bare ...
- **gate.rxt** — the D47.5 possessification gate from the assertions side (`assertions_design.md` §8; D62).
- **view_edge.rxt** — [OPT-VEDGE] (lane vedge, 2026-10-03): counted single-class chains under `\z`/`\Z`/`$`, every start position searched, subjects straddling the count ...
- **wordb_basic.rxt, wordb_empty_compose.rxt, wordb_engattempt.rxt, wordb_vm.rxt** — [M6.2] WAVE B: `\b` and `\B`, in four shards.
- **multiline.rxt** — [M6.2] WAVE C: `(?m)`.
- **gpos.rxt** — [M6.2] WAVE D: `\G`, the first matching position.
- **kreset.rxt** — [M6.2] WAVE E: `\K`, which RESETS THE REPORTED START. **This file is different from every other one here in what its cells are ABOUT.** The other four ...
- **kreset_entries.c** — [M6.2] WAVE E's driver, and the only one in the tree that drives ALL THREE entries of one artifact (`<prefix>_search`, `<prefix>_match`, ...
- **run_kreset_diff.sh** — [M6.2] WAVE E's behavioural instrument, run by `make test-assertions`.
- **gstart_findall.c** / **gstart_entries.c** — [M6.2] WAVE D's two drivers, each for a property no `.rxt` block can express.
- **run_gstart_diff.sh** — [M6.2] WAVE D's behavioural instrument, run by `make test-assertions`.
- **run_mline_diff.sh** — [M6.2] WAVE C's DIFFERENTIAL SWEEP, run by `make test-assertions`.
- **ctxfn_table_check.py** — [DD-11.5] CK-8 (`docs/design/ctx_span.md` §6): every row of `src/core/ctxfn.def`, the one 9-cell A_CTX truth table, against LIBPCRE2. A row is ...
- **verify_pcre2.py** — the libpcre2 oracle for this directory's corpus.
- **d27/** — the [M6.2] D27-BLINDED ACCEPTANCE CORPUS, written at module close from the PCRE2 goal by an author denied `src/` and `tests/` (cell allowlist: ...
- **run_assertions_tests.sh** — the three things a `.rxt` file structurally cannot check, run by `make test-assertions`: 1. the libpcre2 re-verification above; 2. the ...

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

(Rest of this section: see the history file.)

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

- **`rev_end.rxt`** — [OPT-REVEND] L2's ANSWER NET (lane revbuild,
  2026-10-10; `docs/design/revend.md` §9.3): 46 end-pinned blocks, 215
  cells and 25 group slots (38 capture-free blocks, and family G, stage 2's
  captures net from `locate_finish.md` §5 L3, which runs on the VM hybrid), GENERATED by `tests/revend/gen_rev_end.py` from libpcre2
  10.46's answers (every block `# pcre2-only`) and re-verified by
  `tests/revend/verify_stage2.py`. Families: the two seeds and their ties
  (lazy and greedy), startpos at 0/mid/n-1/n, empty and nullable bodies, the
  X1 trailing-lookaround dead seeds, mixed pins, utf8 tails and a utf8 tie,
  word context at the start edge, end_pin's declines (`(?:a$)?`, `(?m)a$`,
  `\Ga$|b$`), a superset hybrid, and the bounded widths the end window used to
  serve. The default build runs the walk; the axes sweep runs `-fno-rev-end`,
  `-fno-anchored-dfa` (the tie relocates) and `--engine=vm`.
- **`end_window.rxt`** — [OPT-ENDWIN], `[OPTLOOP.1]` batch 1 (2026-09-22):
  the END-ANCHOR START WINDOW's correctness carve-outs, 66 cases over eleven
  blocks. The mechanism raises a search's start position to
  `subject_length - (maxw + eps)` on any pattern whose every alternative ends
  in `$`/`\Z`/`\z` outside multiline with a finite width
  (`docs/spec/tuning.md` §2.26), so a window one byte too narrow DELETES a
  legal match — silently, and only on subjects longer than the window.
  **EVERY CLAIM IS CARRIED TWICE, at a subject length that leaves the clamp
  inert and at one that makes it fire**, because a 3-byte subject exercises
  the guard's false arm and nothing else. The blocks cover the final-newline
  allowance that IS `eps`, `\z` against `$` on the same subject (a different
  WINDOW WIDTH, not only a different accept test), `\Z` as `$`'s exact alias,
  and the four declines (multiline, unbounded width, `\G`, a trailing
  lookaround). `\Z` blocks carry `# pcre2-only` under this directory's own
  oracle rule; the rest agree with python3 `re` under the documented mapping
  (`\z` is python's `\Z`), checked by the lane against an independently
  written reader as well as by the directory's own verifier.

(Rest of this section: see the history file.)

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__assertions.md`.
