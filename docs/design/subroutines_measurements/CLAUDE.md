# docs/design/subroutines_measurements — the [DD-14] lane's instruments

Probes, a prototype and archived output for `../subroutines_design.md`, the
module `recursion` design gate (subroutine calls: `(?1)`, `(?&name)`,
`\g<1>`, `(?R)`, `(?0)`, `\g<0>`). Same shape as
`../lookaround_measurements/` and `../backrefs_measurements/`, and it borrows
rather than copies: `probes/sr_oracle.py` loads
`../lookaround_measurements/probes/la_oracle.py`, which loads
`../backrefs_measurements/probes/br_oracle.py`, which loads
`../eng_brep_measurements/probes/pcre2_ctypes.py`. **Three levels of
borrowing, no second binding** — a lane that re-implements the binding it is
checking cannot detect that the original moved.

**NO INSTRUMENT HERE READS A SUBROUTINE CALL THROUGH pcrec, because pcrec
cannot compile one.** Every in-pcrec arm therefore measures a SEPARATE AXIS on
things pcrec CAN answer: the refusals and the 26 registry rows themselves
(§1), the give-up code space and every site the `ERR_FLOOR` move touches (§1),
the emitted primitives quoted from `src/` (§1), and — for the prefilter
question — the INLINED EQUIVALENTS of call-bearing patterns, which pcrec
compiles today and which are verified equivalent against libpcre2 before any
timing (§8). The design marks each claim MEASURED / STRUCTURAL / PROTOTYPE /
ARGUED accordingly.

**AND ONE INSTRUMENT IS NEW TO THIS PROJECT: `sr_oracle.callout_trace()`.**
`pcre2_set_callout` with a ctypes callback that reads the LIVE ovector at a
`(?C1)` placed inside a called body. It exists because the charter's capture
questions are all about the state AFTER the call, and two hypotheses —
"the callee never writes the slots" and "the callee writes them and the return
restores them" — produce the SAME after-the-fact table and completely
different emitted code. §3.1 is decided by two callout firings.

## Files

- `probes/sr_oracle.py` — the lane's oracle helper. Re-exports la_oracle's
  surface and adds three things no earlier lane needed: `match_limits()`,
  which returns the **RAW** `pcre2_match` rc so a match-time give-up is a CELL
  rather than a python traceback (the oracle's `search()` raises, and
  `^(?R)*$` is `rc -52`); `callout_trace()`; and `depth_of()`, a
  depth-limit bisector with a reachability guard. `SELFCHECK` is behavioural
  and runs at import — it asserts that calls exist in this libpcre2, that
  python has none, that the depth and match limits really gate and give the
  documented codes, that the bisection lands strictly inside its interval, and
  that the `pcre2_callout_block` field offsets read the fields they claim
  (two cells, the second separating `current_position` from its `size_t`
  neighbours).
- `probes/probe_premises.sh` — §1, against this worktree's `build/pcrec` and
  against `src/`. Seven axes: the refusals under both feature sets, the
  registry rows, the give-up code space **and every site the −4 → −5 floor
  move touches**, the VM primitives quoted by line, the `[M6.5]` resolution
  machinery a call re-uses, the label-address/`goto *` census, and the
  capacity stamps.
- `probes/probe_spellings.py` — §2. Ten call spellings and nine
  reference spellings separated by ONE cell (`(a|b)X` on `"ab"`); the relative
  and forward forms; `(?R)`/`(?0)`/`\g<0>`; two-digit group numbers; the
  `(?(DEFINE))` idiom against a DEFINE-less substitute over 11 subjects;
  python's verdict on the whole vocabulary.
- `probes/probe_captures.py` — §3.1/§3.4. The callout probe. Capture state
  after return, DURING the call, at depth > 1, after a failed call;
  inheritance; `\K`; `(?J)` duplicate names with the unset-first-declaration
  discriminator that separates a CALL's resolution from a REFERENCE's.
- `probes/probe_atomicity.py` — §3.2. The naive cell that decides nothing and
  the DEFINE-isolated cell that decides it; four atomic controls; quantified
  calls and the twelve-spelling `quant`-column check; calls inside
  lookaround/atomic/lookbehind; and the retry COST against an inlined control.
- `probes/probe_leftrec.py` — §3.3. Direct, indirect and nullable-prefix left
  recursion; the two guards; **the decisive sweep that refutes the
  same-position reading of `rc -52`**; `(?R)` under a quantifier; a call inside
  a lookbehind; the depth requirement against the subject; and the error-140
  sweep showing the charter's premise names a different construct entirely.
  **Says explicitly it did NOT pin 10.46's exact predicate by black-box
  probing** (`out/leftrec.txt` L5b) — `probe_recurse_loop.py` below is that
  predicate, found by reading the source `probe_leftrec.py` only sweeps.
- `probes/probe_recurse_loop.py` — `docs/dev/known_issues.md` K34 / plan row
  [DD-14.K34]. **Reads `pcre2_match.c`'s `OP_RECURSE` handler itself** (10.46,
  fetched from the project's GitHub release tarball into the scratch dir per
  the scope mandate — never into this tree) rather than sweeping harder, and
  states the rule cited to that source before testing it to falsification.
  THE RULE: a call to group `number` is flagged `PCRE2_ERROR_RECURSELOOP`
  (`rc -52`, a bare `return` that aborts the WHOLE match, not a backtrack)
  only when ALL of — (G) the call happens while ALREADY inside some active
  recursion (`Fcurrent_recurse != RECURSE_UNSET`; the outermost entry into
  any group is never checked); (A) walking the enclosing "special group"
  frame chain (`last_group_offset`) finds the NEAREST ancestor frame that is
  itself a recursion of the SAME group (not any ancestor — the first one
  found, and the search can walk past unrelated groups to find it); (P) the
  current subject pointer equals that ancestor's OWN caller's subject
  pointer at the moment IT made the same call (zero cursor progress since);
  (U) `mb->last_used_ptr` — PCRE2's own running high-water mark of the
  furthest subject byte ANY opcode has examined, bumped at every
  backtrack-return (`RETURN_SWITCH`) and at assertion/word-boundary
  completion, not just literal compares — is ALSO unchanged since that same
  moment; and (D) the match-time option `PCRE2_DISABLE_RECURSELOOP_CHECK`
  (0x00040000) is not set. Any construct that forces (P) or (U) to advance
  between successive same-group entries — a mandatory literal before the
  call, or a base-case alternative whose FAILED attempt merely peeks one
  byte further than the ancestor's own attempt did — defers or defeats the
  guard indefinitely, which is what makes design §3.3's 199-deep
  same-position match possible: the guard is not about position at all, it
  is about whether progress OR mere lookahead has happened since the last
  time this exact recursion was entered. **65/65 cells agree with the rule
  as stated** — first-item/consuming-prefix/nullable-prefix families
  crossed with base-case presence, anchored and unanchored, all K34-cited
  spellings ((?1)/(?R)/(?&name)/`\g<n>`/`\g'name'`/(?P>name)), a 3-node
  indirect cycle proving the search is NOT limited to the immediate parent,
  and K34's own case-study patterns re-derived from the rule rather than
  re-discovered. **Two decisive confirmations beyond restating the rule**:
  R4 shows the `return` (not `RRETURN`) really does swallow a sibling
  top-level alternative that never touches the recursion at all (`^(a|(?1)a)$|^Y$`
  on `"Y"` is `rc -52`, not the match `^Y$` would give alone); R5 sets
  `PCRE2_DISABLE_RECURSELOOP_CHECK` on an otherwise-`-52` cell and, under an
  explicit small `depth_limit`, gets `rc -53` (DEPTHLIMIT) instead — proof
  the read targets the actual gating `&&` term in the source, not just its
  externally observable effect. **One instrument defect found and fixed
  in-flight, itself now a permanent finding (§R1.5)**: five cells the rule
  first mispredicted `-52` for all turned out to be intercepted by a
  DIFFERENT PCRE2 mechanism — the compile-time START-OPTIMIZE pass
  (minlength / required-byte prescan) rejecting a subject that is empty or
  missing a byte the pattern structurally requires, BEFORE the recursive
  matcher ever runs even one level (`depth_limit=1` already shows NOMATCH).
  `PCRE2_NO_START_OPTIMIZE` (0x00010000, compile-time) flips all five back
  to the predicted `-52`, confirming the confound rather than the rule was
  wrong — and is now the sweep's own warning to a corpus author: testing a
  runaway-recursion cell on too-short or required-byte-missing subjects
  measures the wrong PCRE2 mechanism.
- `probes/probe_linkage.sh` + `prototype/gen_linkage.py` — §6, PROTOTYPE. The
  generator writes three hand-written matchers in the EMITTER's own idiom
  (computed goto, the resume array, the trail, `RX_SET`/`RX_PUSH` spelled as
  `emit_vm.c` spells them) differing only in linkage; the probe runs a 52-cell
  agreement control first and refuses to print a number until the three agree,
  then measures `rx_match_anchored`'s size from `nm -S` and times two corpora.
  **Nothing in `src/` was changed to produce these numbers.**
- `probes/probe_slotfamilies.py` + `prototype/slotproto_pending.c` +
  `prototype/slotproto_cutmark.c` — §5.3b, PROTOTYPE. **The two prototypes are
  the R34 C2 panel's own and are ADOPTED UNCHANGED**, for the reason
  `docs/design/CLAUDE.md` records about `simvm.py` one lane over: a lane that
  rewrites the instrument which refuted it cannot be trusted not to soften it.
  Only their header block is this lane's. The probe REBUILDS both from source
  and re-runs the comparison, which is how the refutation was confirmed before
  §5.3 was touched. Each prototype is compiled two ways differing in ONE slot:
  captures-only `W` **loses matches** on `SLOT_GROUP<n>_PENDING` (11 agree / 2
  disagree) and produces **FALSE MATCHES** on `SLOT_CUT_MARK<n>` (4 / 6) whose
  language is exactly the non-atomic control's; the general rule is 13/0 and
  10/0. It ends by stating **why this lane's own corpus could not see it**.
- `probes/probe_callproto.py` + `prototype/callproto.c` — §5.9, PROTOTYPE.
  **§5's whole lowering, built by hand in the emitter's idiom and run against
  libpcre2**: the frame that carries the return label, the non-popping return,
  the fail label's one added line, and the `|W|` trailed save/restore, for four
  patterns each of which is a design claim. Compiled TWICE — the second with
  `-DBROKEN_ARRAY`, which is §5.2's REJECTED design (a separate `call_stack[]`
  indexed by depth, popped at the return) — so the bug that kills it is
  REPRODUCED rather than argued. **45 agree with libpcre2, 4 agreed-in-kind
  (both refused), 0 disagree; the broken build gets 3 of 50 wrong including a
  FALSE MATCH and agrees on the other 47**, which is what localises the failure
  to the clobber sequence. It is also where the design's `W` definition was
  found to be wrong — `g`'s OWN slots must be restored, and without them a
  correct match reports a wrong span.
- `probes/probe_prefilter.py` — §8.3. What a DFA prefilter is worth on
  call-SHAPED patterns, measured on their INLINED equivalents: 15 hand-written
  pairs, each verified equivalent against libpcre2 over 28 subjects (420 cells,
  0 disagreements) BEFORE any timing, then timed with and without
  `-fno-prefilter` on a 1 MB sparse-candidate subject.
- `probes/probe_population.py` — §8.4. A pure-text census of
  `tests/**/*.rxt`'s 2,161 `pattern` lines, with a character-class masking pass
  so `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` is not counted as a call.
- `probes/archive.sh` — **the ONLY writer of `out/`.**
- `probes/check_selfconsistency.py` — **the catcher for R34's V-7/V-12 class**,
  and the one instrument here that reads the DESIGN rather than libpcre2.
  Three checks, all exiting NONZERO on any miss (never print-and-continue):
  (1) **archive freshness** — every `probe_X.{py,sh}` has an `out/X.txt` that
  is not older than it, which is what a table citing a number from a probe a
  later edit changed looks like (V-7) and what a number with no archive at all
  looks like (V-11); (2) **sabotage-row coverage** — every `S-SR` id in §9.3's
  table appears in some §11 landing bar's DETECTED list; (3) **corpus-file
  coverage** — every `*.rxt` in §10.2 appears in some §11 bar (V-12).
  **Exercised in the FAILING DIRECTION before landing — seven sabotages, 7/7
  failing correctly, clean tree passing** (the list is in its header; sabotages
  3 and 4 are the two ids a range once hid, and sabotage 3 is the one the
  file's own first version PASSED). It had TWO
  defects of its own that only that exercise found — both in its header, and
  the second is this project's check-design lesson reproduced inside the
  check: an earlier version asked whether an id appeared ANYWHERE in §11 and
  PASSED a sabotage deleting S-SR7 from every bar, because §11 also contains
  a sentence ABOUT S-SR7. Prose about an id satisfied the check for that id.
- `prototype/gen_linkage.py` — the §6 generator. Its header records that the
  charter's "once-emitted-with-two-linkages" COLLAPSES when written out, and
  why, so the next reader does not re-derive it.

## The rule this lane worked under

Every PCRE2 behaviour claim is PROBED, never recalled, and every sweep carries
a REACHABILITY guard that prints and says VACUOUS when it fails. That rule
earned its place here: **ten instrument defects** were found by running these
probes, each producing a confident wrong number or silently exercising nothing.
`out/CLAUDE.md` lists them. Two changed a design conclusion — and **twice more,
EXECUTION changed one**: building §5's mechanism (`prototype/callproto.c`)
found the restore set missing `g`'s own slots, and R34's C2 panel, building it
again with a second lexical construct in play
(`prototype/slotproto_*.c`), found the whole capture-slots-only RULE wrong. A
design section that can be executed should be — and by someone who did not
write it.

- `email_specimen/` — (2026-08-24, thirty-ninth session) the RFC 5322
  email pattern, original vs `{0}`-idiom subroutine-factored, measured by
  the srEmail lane on post-A2 main and lane/srBC against libpcre2 10.46:
  85 subjects (0 answer disagreements; 5 FRAMES give-ups on deep
  repetition for the factored form), three 1 MB throughput subjects
  (prefilter loss ~23×; a STEPS give-up where the DFA takes 4 ms). Its
  README carries the conclusion that sets wave G's bar (byte-identity
  with the hand-inlined pattern). Scripts regenerate the subjects.
