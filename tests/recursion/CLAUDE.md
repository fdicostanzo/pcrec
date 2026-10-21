# tests/recursion — module `recursion` ([DD-14])

Subroutine calls: `(?1)`..`(?9)` and beyond, `(?-N)`/`(?+N)` relative forms
(with their leading-zero and relative-zero variants), `(?&name)`,
`(?P>name)`, `\g<N>`/`\g<name>`/`\g<±N>`, `\g'N'`/`\g'name'`, `(?R)`, `(?0)`,
and the two spellings the charter's list did not have, `\g<0>`/`\g'0'`.
Design: `docs/design/subroutines_design.md` (PROPOSED, not yet paneled at the
time this corpus was written). Decisions: `docs/dev/decisions.md` D71 (the
give-up-code diagnostic axis, D71.1 in particular) and D72
(`PCREC_ERR_INTERNAL`).

**WAVE D HAS ALSO LANDED, AND THIS SECTION IS AGAIN THE PRESENT TENSE.**
Wave B+C shipped the three `(?` ports, the resolver's call rule,
`src/opt/callgraph.c` and the emitter's call linkage, leaving the `\g<`/`\g'`
family `unbuilt` (below). Wave D wired `pcrec_brport_g`'s `<`/`'` arms
(`src/parse/mod_backrefs.c`, design §4.2's "NOT A NEW PORT" ruling), so
`\g<N>`/`\g<name>`/`\g<±N>`/`\g<0>` and `\g'N'`/`\g'name'`/`\g'0'` all compile
and match now too. **This directory runs 371 cases / 0 failures** — the 22
`\g` blocks (below) went from `perr` to real `m`/`n`/`g` lines by ONE edit to
`gen_corpus.py` (deleting each block's `wave='D'` keyword argument) and a
re-run, exactly as the paragraph below always said they would; nothing about
the CELLS changed, only what pcrec answers them with.

## Files

- **`framebuffer.rxt`** — **[DD-14.FB], 2026-08-25.** The caller-provided buffer's behavioural cells, through run.sh's `frames-buffer=` route (docs/testing.md). 16 cases ...
- **`fb_mmap_driver.c`** — **[DD-14.FB]** spec §10.6's `MAP_NORESERVE` worked example, RUN rather than quoted: two 64 MB reservations driven to their ceiling, printing ...
- **`fb_exact_driver.c`** — **[DD-14.FB]** the SEVEN CAPACITY SITES measured exact in BOTH directions, on buffers with NO SLACK, under AddressSanitizer.
- **`run_frame_buffer.sh`** — **[DD-14.FB]** the three checks the corpus cannot hold, `make test-frame-buffer`, OPT-IN. §1 compares `<prefix>_search_in(..., NULL)` against ...
- **`refused.rxt`** — the `conditionals` refusals this module does NOT unlock: `(?(R)`, `(?(1)`, each pinned by running today's built `build/pcrec`.
- **`gated.rxt`** — the two D65 diagnostics (`requires module 'recursion'` under std1 vs `... is enabled but ... is not implemented yet` under a partial set), P2's masking ...
- **`spellings.rxt`** — design §2.1's one-cell call-vs-reference discriminator (`(a|b)\1` nomatch vs `(a|b)(?1)` match on `"ab"`), then every shipped call spelling ...
- **`relative.rxt`** — `(?±N)`/`\g<±N>` at four distances each direction, the leading-zero relative forms, and the four relative-zero error cells (all real PCRE2 compile ...
- **`whole.rxt`** — `(?R)`/`(?0)`/`\g<0>`/`\g'0'` and the anchor cells: `^(a(?1)?b)$` on `"aabb"` is `(0,4)`, `^(a(?R)?b)$` is nomatch, because `(?R)` re-runs the anchors ...
- **`captures.rxt`** — after return, at depth 3, after a failed call, and the inheritance cell `^(a)(b\1)(?2)$` on `"ababa"` with its `"abab"` control (needs `backrefs`).
- **`atomicity.rxt`** — the isolated discriminator (a callee reachable only by the call) over three quantifier shapes, the depth-retry cell, and all four atomic controls ...
- **`leftrec.rxt`** — three EMPTY-LANGUAGE cells (direct, indirect, nullable-prefix), the `^(a|(?1)a)$` on `"a"×200` cell that MUST match, and the right-recursion contrast.
- **`dupnames.rxt`** — design §3.4(c)'s call/reference split (a call resolves a duplicated name STATICALLY to the first declaration; a reference resolves it dynamically to ...
- **`kreset.rxt`** — design §3.4(b)'s three `\K` cells: `\K` inside a called body moves the reported start and SURVIVES the return, because pcrec spells `\K` as a write to ...
- **`zerodef.rxt`** — the `X{0}` callee family (plain, recursive, atomic, rung-bearing), each with its `(?(DEFINE)` TWIN (`[DD-14]` wave F: the two spellings lower to one ...
- **`define.rxt`** (`[DD-14]` wave F) — D71 item 4's construct: the library idiom itself, a numbered callee inside a DEFINE, the body-does-not-run-lexically pair, two ...
- **`realworld.rxt`** (`[DD-14]` wave F, `[LIB]` entry #1) — the RFC 5322 email specimen in all THREE spellings (hand-inlined `orig.rx`, `{0}`-factored `factored.rx`, and ...
- **`leadingzero.rxt`** — design §2.4a's pair on the ANCHORED discriminator: `^(a(?01)?b)$` on `"aabb"` is `(0,4)` (group 1), `^(a(?00)?b)$` is nomatch (the root) — the ...
- **`mrl.rxt`** — design §4.4b's fixpoint PAIR: the mutual-recursion witness that refuted the withdrawn "least fixpoint over non-recursive branches" gloss (must MATCH at ...
- **`slotfamilies.rxt`** — design §5.3b's two MEASURED slot families: AXIS P (`SLOT_GROUP<n>_PENDING`, a LOST MATCH without it — `^(a(?1)?b)\1$` on ...
- **`quantified.rxt`** — design §2.6's twelve quantified spellings, the empty-body guard (a nullable or empty callee under `*` terminates), and `^(?R)*$`'s unconditional ...
- **`inlookaround.rxt`** — design §3.4(d)/(e) (a call INSIDE a lookbehind needing a width, refusing on a recursive callee; ordinary inside a lookahead/atomic group) and ...
- **`run_lookbehind_call_sweep.py`** — [DD-14.LB], ON-DEMAND, not part of `make test`.
- **`prefilter.rxt`** — **[DD-14 wave E]** design §8.2's own counterexample: `a(?1)b` with group 1 = `x` matches `"axb"`, and the call-ERASED pattern `ab` does not — so ...
- **`k69.rxt`** — K69 (lane k69fix, 2026-09-27): a call's nullability is the LEAST call-graph fixpoint.
- **`k93.rxt`** — K93 (lane k93fix, 2026-10-07): a quantifier inside a call TARGET must hold its possessify verdict under every call site's follow, not only the group's ...
- **`nocaptures.rxt`** — design §4.3's marked-set cells (one-hop, two-hop), written on the ORDINARY (captures-on) axis.
- **`d27/`** — the `[DD-14.D27]` BLINDED corpus, delivered 2026-08-24 (sr27, opus) and LANDED the same day (sr27land, sonnet): 200 blocks, 558 cases (m=276 n=251 ms=8 ...

## THE CORPUS IS GENERATED, and there is no python arm

`gen_corpus.py` wrote every expectation in every `.rxt` here — **including
every `g` line** — by driving the cell through libpcre2 10.46 (via
`docs/design/subroutines_measurements/probes/sr_oracle.py`, which borrows
`la_oracle.py` → `br_oracle.py` → `pcre2_ctypes.py`, three levels of
borrowing rather than a fourth copy of the ctypes binding) BEFORE it was
written. The generator never asks pcrec anything.

**Unlike every earlier generated corpus in this tree, there is no python
arm and no `# pcre2-only` marking.** Design §10.1 MEASURED it: python3's
`re` has NO subroutine-call construct at all — not different semantics, an
ABSENCE. Every one of the nine call spellings plus both zero spellings
raises `re.error` at compile time. `\1` and `(?P=n)` DO compile in python,
but they are `backrefs`'s reference construct, not this module's call
construct (design §2.1's one-cell discriminator is why `spellings.rxt`
opens with it) — treating python's agreement on those two spellings as
coverage of this module would be the exact trap §10.1 names.

Re-run after changing a cell list:

    python3 tests/recursion/gen_corpus.py

It rewrites the `.rxt` files in place and prints a per-file census. A
second run with no source change is a no-op (`git diff` empty — checked,
see below).

(Rest of this section: see the history file.)

## [K37, srMech 2026-08-25] every `pcrec` call in this directory is BUDGETED

`run_recursion_diff.sh`, `run_frame_buffer.sh` and `run_specimen_identity.sh`
invoked the COMPILER bare — fourteen call sites, and `run_recursion_diff.sh`
did not source `tests/lib/gen_timeout.sh` at all. K37 is what that costs:
sabotage row S159 (`mark-follows-body`) makes the emitter loop forever on
`((?1)*a)`, so the mech row that should have read one FAILED ARM instead burned
49 min 58 s of CPU and had to be killed by PID, taking the whole 180-row
matrix's evidence with it. **A hang is the one outcome no verdict can be
derived from**, which is why this is a correctness property of the directory
and not a convenience. All fourteen now run under `"$TIMEOUT_BIN"
"$(pcrec_timeout_secs)"` — D45's own knob, 20 s plain / 60 s sanitizer, scaled
off `-fsanitize=` in the flags — and every one of those sites already routed a
non-zero exit to `bad`/`die`, so a non-terminating compiler is now DETECTION.

**CLOSED (srRun2, 2026-08-25):** `run_recursion_diff.sh`'s generated-code
compiles (`$CC $GENCFLAGS`, 4 sites) and matcher runs (`"$d/t" ...`/
`"$d2/t" ...`, 3 sites, including the batch driver `run_arm` shares between
§3's 18-row sweep and §5's ~150-pattern corpus sweep) now route through
`gen_cc`/`gen_run` — the exact mechanism `tests/harness/run.sh` already used
for both, and the per-pattern shape those two functions are for (`run_arm`
pays the fixed watchdog cost once per pattern, not once per cell — its own
batch driver already reads every subject/startpos cell over one stdin
stream). `export WATCHDOG_SECTION="recursion"` added beside the
`gen_timeout.sh` source so its `build/watchdog.log` lines are attributable.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__recursion.md`.
