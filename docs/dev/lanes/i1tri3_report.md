# i1tri3 — I1's compound-part failures, round 3 (lane report)

Lane i1tri3 (opus), 2026-10-21, continuing `lane/i1build` from `f5956a2e9`.
Brief: fix job `609-i1build-solo`'s two failure shapes (B1's one-TU part
builds; the partlayout `held-compound` fixture), decide on evidence whether
round 2's fix (b) is right, check whether round 2's other C fixes share
shape (1)'s naming root, see test-compound green, re-queue the chain.
Rulings file `i1tri3_rulings.md` (gitignored, like round 2's): empty at
every checkpoint, no entry applied.

## 0. Premise

`scripts/verdict`-shape grep of 609's `job.log`: two red lines, not one:
`test-compound` (shape 1: 60 B1 failures, every one `implicit declaration of
function 'kz__f_next_pos'; did you mean 'kz__f__next_pos'?`, which left B1's
population at 0 cells) and `test-partlayout` (shape 2: the `held-compound`
fixture). The brief's "test-compound only" is off by one section; shape 2
lives in test-partlayout. Every other section of 609 passed.

## 1. Shape 1: B1's hand controller named the pre-I1 static residual

The call site is not an emission: it is `tests/compound/check_parts.py`'s
HAND CONTROLLER (the stand-in for the split combinator B1 links with the two
parts), which called F's residuals as `<p>__f_next_pos` and, under
`-futf-check`, `<p>__f_valid_upto`. Under I1's F-1 rule (enc.c,
`pcrec_enc_emit_twins`/`pcrec_enc_emit_defs`) an out-of-line residual entry
is written once as its static twin `<prefix>__<name>`, and a STATIC (kept)
entry is "its twin alone", with no `<prefix>_<name>` at all. A part is
compiled with every entry static, so part F's next_pos is `<p>__f__next_pos`
(prefix `<p>__f` + `__next_pos`). The emission is one naming primitive,
applied everywhere (the twin text, every internal call, the forwarders, the
real compound controller's `<p>__next_pos` call in emit_compound.c); nothing
in `src/` builds the stale name. So the fix is the test's: the controller
calls `@P__f__next_pos` / `@P__f__valid_upto` (commit `bb32945c8`). The
`nm -g` leak check (`"__f_" in name`) still catches a global part symbol
under the new spelling.

Same root as round 2's other fixes? Fix (c) (enc decls) is the SAME root:
F-1 renamed a static residual to its twin, and (c) removed the last
emission of the old static name (a stray `static size_t rx_<name>(...)`
declaration); round 2's B0 keep-stub re-map and this B1 controller are the
two test readers of the old name. Grep over tests/ for hand-written calls
to a part's or a static residual: no other reader (split_diff.c and
loads_drv.c call exported `pl_next_pos`/`rx_next_pos`, which are
forwarders and still exist). Fix (a) (owned_inline FIND) is a different
root: caller counting, not naming.

Design text still spelling the pre-I1 names (NOT edited, design notes are
a record): `docs/design/compound.md` §B (`<p>__f_next_pos`,
`<p>__f_valid_upto`), `docs/design/compound_callout_alignment.md`.

## 2. Shape 2: fix (b) is RIGHT; the fixture's premise was stale

Evidence, on `^\s+|\s+$ --part-layout=compound:inline` at this head:

- Part F's `rx__f_search` is a one-line wrapper,
  `static inline __attribute__((always_inline))`, whose body is `return
  rx__f__find(...)`; the label tables (`rx__f_targets_N`) are inside
  `static __attribute__((noinline)) rx__f__find`. gcc 15.2 `-O2 -Wall
  -Wextra -Werror` compiles it clean and `rx__f_search` leaves no symbol
  (inlined). H1 ("can never be copied") applies to `__find`, which is no
  part-layout subject in I1 (emit_dfa.c's own comment), not to the subject.
- `--emit-facts`: comp_a 4 callers (`_search`, `_next`, `_match`,
  `_match_caps`), comp_b 2 (`_search`, `_next`), both copyable, both P5.
  The `_next` caller comes from fix (a): the shell's `__find` is
  `always_inline`, so it folds into both `_search` and `_next`.
- The independent evaluator (section 1, which asks gcc itself whether a
  function copies and counts callers from the text) already judged the
  `split` witness under 25 control settings green in 609, agreeing with
  the part table.

So P2 for F (pinned by H1 on its attempt-route label table) and P3 for Q
(one caller) were both true of the pre-I1 shape and both stopped being true
when I1 moved the label table into `__find` and added `_next`. This is a fact
about the emitted code, not a copyability design choice, so I did not stop.

What `held-compound` witnessed: that a compound-class request is held by a
constraint row (P1-P3) and stamped `compound=V/held`. Under I1 no CLI input
reaches that: compound parts are DFA, their label tables are in `__find`,
and every part has `_search` and `_next` as callers; a single-caller part
needs a driver-tier entry request that drops `_next` (B0's tier, no CLI
spelling). The `/held` marker itself is one stamp path for every class and
stays witnessed by `constraint-copy`/`-single`/`-rung` (prefilter class;
S1118 still detected through them). The row is re-pinned as
`compound-inline` (P5/P5, stamp `compound=inline`): it now witnesses that
a compound class value reaches both parts, with a header note saying why
it moved. `held-other-class` keeps `compound=inline/none`.

Caller-observable move, so D80 hunks in the same commit:
`tuning.md` §2.51¶1a (a `compound` value lays out split's parts, stamp
`compound=inline`) and `match_api.md` §6.3.11's stamp example (`/held`
shown on `^(a)b` prefilter, split shown as `compound=inline`); every
example line verified against the CLI. S1118's comment no longer names the
fixture.

Finding for the manager (not fixed, outside this round): `tuning.md`
§2.51's class table still says `find`'s parts "none exist, the iterator is
not built", stale under I1 (the iterator is built; `find` has no subject).
Design note `compound_entries.md` (Held requests, [r4]) still states
split stamps `compound=inline/held`.

## 3. Validation (seen, this box, box free, single make target each)

- `make test-compound` at the fix (log
  `worktrees/i1build/build/i1tri3/compound1.log`): `test-compound: PASS`.
  B0 0 failures x3 arms; E0 fixture 10/0, re-seed 584/0; B1 `6 witnesses x
  5 arms x 2 prefixes; 438462 cells, 44732 matches; 328110 bounded-request
  cells; 0 failures`; B2, B4 (declines, admitted 97/97, G3, G7, lever,
  shell structure), G2+G4, G1 all PASS.
- `make test-partlayout` (log `build/i1tri3/partlayout1.log`): checks
  passed 49, failed 0; `PASS: fixture compound-inline`.
- `make test-spec-history`: 11/0. Commit hook: staged checks 62/0.
- No C changed this round, so no `make strict`/abi event.

## 4. Ids

None used. No D/K proposal.

## STATE AT HANDOFF

Head of `lane/i1build`: the commit carrying this report (fix commit
`bb32945c8`). Rulings file: empty, no entry applied. Main NOT merged into
the branch.

Queue (owner i1build; scripts in `worktrees/i1build/build/i1jobs/`):
`612-i1build-maketest` CANCELLED (it waited on the failed `i1build-solo`);
`613-i1build-maketest` added: 612's script with readiness unconditional
(make -j8, make strict, `scripts/perfrun --label i1build --shape 8,8`), key
`i1build-maketest`. `621-i1build-mech`, `631-i1build-census`,
`641-i1build-parity` wait on that key (re-added with the same keys if the
cancel cascaded; see the handback). Green lines: 613 `scripts/verdict` on
`job.log.make` VERDICT GREEN, perfrun `DONE rc=0`; 621 `== mech run
COMPLETE: 21 rows`, 0 unexpected; 631 exit 0; 641 cells c1, c3, c4 `GATE I
PASS`. OWED: all four; a fresh agent reads the verdicts.
