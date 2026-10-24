# How a code critic uses the guide

First version; the 2026-10-23 S3 code-review round will refine it.

The procedure for running a round (freeze, blind, pick lenses, verify, compile)
is the `pcrec-code-critic` skill (`.claude/skills/pcrec-code-critic/SKILL.md`);
this page holds the rules it reviews against. Lenses are chosen per change from
the skill's lens table; no lens set is standard because an earlier round used it.

A critic reviews a diff against the guide (`coding.md`, `architecture.md`,
`style.md`, the area's `addenda/`). Critics are read-only and never run `make`
(D6). Where a finding is already known, use blinded critics (D27). Label
findings CONFIRMED (with repro) or SUSPECTED and carry a PROBED-AND-HELD list
(`docs/dev/reviews/CLAUDE.md`).

## Standing lenses
1. **Design compliance.** Does the change follow `architecture.md`? Is each
   selection a declared table, with no private copy of an existing mechanism?
2. **Emitted code vs what it replaces.** Read the generated C and asm of the
   new path AND of the path it replaces; compare, do not infer from the source.
3. **House rules.** `coding.md`, including the altitude rubric (length is a
   trigger, never a verdict; common extracts first) and `style.md`.
4. **Test and gate adequacy.** Does each new check have an independent control,
   a witness that reaches its site, and a counted population
   (`docs/dev/learnings.md` section 3)? Does it still pass when the code is wrong?
5. **Sibling of a family.** Is a new predicate or table a sibling of an
   existing decision family? Name the family.
6. **Propose the general form and unlocks.** Beyond refutation: name the general
   form of the change and what it would unlock, with triggers.

## Rules
- **A re-pinned floor or count is a TRADE to judge, never bookkeeping.** Example:
  a SIMD floor dropping 39 to 33 in a re-pin hid a 29x caseless-literal
  slowdown (2026-10-23). Ask what moved and why.
- A finding contradicting a ruled D-row, a design note's ruled section, or a
  recorded panel disposition must cite it and argue against it, or drop (A1 of
  `docs/dev/reviews/code_review_criteria_draft.md`).
- A duplication finding names the shared abstraction: signature, call sites
  replaced, what varies (A2).
- A finding cluster names the checks and anchors that bind the code it would
  move (A3), and carries severity, effort and blast radius (A4).
- Cite metric artifacts where one applies (A5, `tools/review/`).
- Review the function population length-ordered and say where you stopped (the
  draft's Addendum 2); a long function that passes the five altitude questions
  stays long, and the finding says so.

## Lessons from review rounds

Round 2026-10-23 r1, kit S3 (D172's REPORT routing), four blinded critics
(`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, landing with lane/memfn-s3,
§4). Three of four caught a 29x caseless-literal slowdown from the code alone.
1. **Review the EMITTED artifact, both arms.** The emitted-vs-replaced lens
   caught it with loops and asm; the source-only code-quality lens missed it.
2. **Trace every slot to its named table.** The design lens caught it by
   showing a declared row (the PAIR find form) was unreachable. This is how a
   parallel mechanism shows up.
3. **A lowered performance-form floor is a trade to judge,** not a pin (the
   rule above).
4. **Blinding leaks** through report headers and git log. Give each blinded
   critic a clean worktree at the subject sha plus a denylist.
5. **The manager's rulings are review subjects too.** The defect entered
   through a ruling.
6. **Staffing:** at least one strong-model critic on emitted behaviour and one
   on design; the weaker-model lenses found real but smaller issues.

Round 2026-10-23 r2, find-all iterators (`docs/dev/reviews/2026-10-23-r2-iter-code.md`), the
first run of the `pcrec-code-critic` skill, five lenses picked by profile.
1. **Pick lenses by what the change touches.** The contract and slot-tracing lenses, absent from
   the earlier fixed four, found the answer bug and its cause (a private copy of the anchored body).
2. **Only the emitted-vs-replaced lens saw a regression to EXISTING entries.** Ask that lens to
   diff every pre-existing entry BASE vs SUBJECT, not only the new path.
3. **A known result re-found blind calibrates the round** (`_next_n` at k=1 slower than `_next`).

Round 2026-10-23 r2, kit S3 C1 build (`docs/dev/reviews/2026-10-23-r2-memfn-s3-c1-code.md`, lane/memfn-s3, §6), the skill's first use by the kit.
1. **The hidden-issue test passed again with the strong lenses:** both opus lenses found, blind, that two-or-more-member non-case-pair stops get a scalar walk.
2. **Verification earns its place:** it corrected a modelled magnitude (same-set windows re-read 1.1-2.5 bytes/byte on dense input, not 6-12) and showed the lane's example patterns were controls, not witnesses.
3. **Keep the check-adequacy lens whenever checks or flags change:** it alone found a broken gate (`make test-axes`'s memfn arm: MEMFN_CLASS lacked the new forms).
4. **The slot lens lists each ruling's CONSEQUENCES,** not only its agreement with the design.

- (2026-10-24, memfn-s3-final) **A change to the DEFAULT search gets a find-all, real-text instruction sweep per new find form.** The emitted lens runs find-all over one real text and one adversarial text per new form, BASE vs SUBJECT, by instruction count. Both large losses (a quadratic two-stream find-all, a set stop walked where BASE ran memchr) were invisible to the stated timing bar, whose sample held neither shape.
- (2026-10-24) **A new stamp VALUE or a new pre-empting row is a D94-style reader hunt.** Grep every enumeration of the stamp's values and every witness sentence for the rows it now pre-empts. Six stale spec passages came from this.
- (2026-10-24) **Critics are launched unnamed, and their results travel only as files.** A coordinator's spawns could not be named, and all six final replies were lost; the files carried everything.
