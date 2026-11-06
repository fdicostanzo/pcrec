# Lane arevdesign: report

Lane arevdesign (opus, 2026-11-05), branch lane/arevdesign from main 7cebea04e. Design only: no
edits under src/, cli/, lib/, memfn/ or tests/. Deliverables: `docs/design/stream/arev.md`
(PROPOSED rev 0), the A-REV row and section of `docs/design/stream/roadmap.md`, and the CLAUDE.md
lines for the new file in `docs/design/stream/` and `docs/design/`.

## Summary in plain words

- **The premise holds, and it is cheaper than the roadmap assumed.** Three of the four reverse
  walks on main (the reverse pass that finds where a match starts, the reverse-from-the-end search
  and the landmark walk) already use ONE piece of code to write their loop. The landmark walk is
  merged now (dc6a40dfb), so it no longer blocks anything. What the three do not share is how a
  walk is DESCRIBED. Each one has its own named machine slot, its own frozen copy of the direction
  strings (the landmark walk's copy repeats the reverse pass's text under a new name), and fixed
  variable names. Any exit other than "the leftmost start" is written by hand in the caller.
- **revdet is a reverse walk too**, just written differently. Its walk is a reverse machine shown
  as one VM step per pattern node, and it already runs INSIDE a VM body. So it is the precedent
  for the thing the lookbehind needs.
- **The kind.** The proposed "kind" is one record that describes any reverse walk: which machine,
  where it starts, how far back it may go, what it returns, the tags it collects, its names, and
  where it is hosted. Each existing walk would fill that record in, and nothing new would render
  it. A walk only ever does one of two things: it runs back as far as it can and remembers the
  leftmost accept, or it stops at the first accept. The manifesto's five exits are what the caller
  does with that result. "Enumerate" is a loop around the first behaviour with a moving floor, so
  it is not a third walk.
- **Hosting in a VM body.** Add one new VM record whose output is a call to a small static
  function per walk, containing the existing loop code. The function boundary gives every walk its
  own names for free.
- **The lookbehind client is sound.** The reverse machine answers the lookbehind ALONE only when
  it is exact and the branch has no capture group. Otherwise it is a filter: "no accept" decides,
  and "accept" hands over to the ordinary loop. This means the atomic counter-example (an atomic
  group the machine has to ignore) cannot give a wrong answer. The machine's own recorded
  exactness makes the "answer" row decline. The STOP RULE did not fire.
- **Order.**
  - (1) Give the three DFA walks the shared record: no output change, and the landmark copy of the
    direction strings goes away.
  - (2) Move revdet onto the same record: no output change.
  - (3) Add the VM-hosted form, with lookbehind as its first user. This step changes output only
    for patterns that take the new row, and it is built only when a measurement asks for it.
  - (4) Write the landmark walk out as records. This waits for the DFA top-level proof (P-b).

  Steps (1) and (2) ride along with any change that touches those files.

## Premise test (the brief's list, at main 7cebea04e)

Every cited symbol exists. Locations are in `arev.md` §1.

- revdet: `src/opt/revdet.c`, `vm_revdet_rep`, `vm_rev_emit`, `Rev`, `VK_CONSUME_BACK`.
- DFA side: `dfa_member_machines` (now four machines), `DfaDir`, `dfa_dir_landmark`,
  `dfa_dir_lmverify`, `emit_reverse_block`, `emit_scan_loop`, `emit_landmark_walk`.
- Machine building: `lmwalk_build`, `revend_build_one`, `Job.lmnfa`/`lmdfa`, `CAND_ML`,
  `Nfa.erased`, `lmwalk_conj[]`.

One name in vlookbehind.md §3 does not exist as written: `rx_reverse_accepts_class`. The accessor
is emitted once per machine as `<p>_<dir>_accepts_class`. p1build is merged
(dc6a40dfb, abi 95). Two facts the brief did not name and the design rests on:

- The count-collapse is a BUILD OPTION, `b->collapse` in `src/ir/nfa.c`. A bounded repeat built
  with it turns into an unbounded superset and records `NFA_ERASED_COUNT`. So "exact or collapsed"
  is something each walk instance states (G7).
- The reverse walk reads the byte just below its floor as context (mech row S74). So a floor set
  as a width bound is sound only because no branch can have an accept below it (G11).

## Findings that change something outside this note

1. **R03's recipe can never fall.** "`src/opt/revdet.c` present" counts the ANALYSIS, and the end
   state keeps the analysis: it is the admission test for the structural representation. Proposed
   restatement: "`} Rev;` in `src/gen/emit_vm.c` present: 1". It reads 1 at 7cebea04e.
2. **The inventory is missing a member, R28.** `dfa_dir_landmark` is a second reverse direction
   object, and its own comment calls it a character-for-character copy of `dfa_dir_reverse`.
   Proposed recipe: "`static const DfaDir` with `reverse` true in `src/gen/emit_dfa.c`, minus 1".
   It reads 1 at 7cebea04e. S1 deletes it.
3. **The roadmap's A-REV anchors were p1build's, and p1build is now on main.** The §1 row and the
   A-REV section are rewritten at 7cebea04e. Other areas still cite 3f777330e or "p1build". That is
   left to the manager, and only A-REV was re-grepped.
4. **The unbounded-lookbehind HELD row (review r3-F16) is not filed yet.** Checked on lane/vlbrev1
   at 2056360d7 and in its working tree: no plan edit. When it is filed, it should name `arev.md`'s
   `exist`/`gate` rows as the reverse form and [ENG-LOOK] as the forward one.
5. **The bench blocks the pricing cell today.** `negation-scope-lookbehind-var` is BLOCKED on
   pcrec-auto by a capability declaration (`lookbehind-variable`, checked by pcrec-bench
   `tools/selfcheck.py`). The cell that would trigger S3 does not exist until vlookbehind stage 1
   ships and the manager sends the bench an inbox entry lifting the block.

## Proposed manifesto paragraph (optional; the manifesto is NOT edited)

None is required: the design fits §2's five exits as written. If the owner wants the reading
recorded, one sentence after the automaton-records sentence:

> "A walk itself does one of two things, runs to its bound keeping the farthest accept or stops at
> the first; the five exits are what its consumer does with that result, declared as the type of
> the hand it gives."

## Draft decision entry (D-next; for the manager, NOT written to decisions.md)

> **D-next: A-REV moves up the roadmap as one reverse automaton kind, hostable in a VM body, with
> variable lookbehind's `reverse-dfa` row as its first client** (lane arevdesign, 2026-11-05;
> PROPOSED, owner's go per step)
>
> - **Decision (proposed):** every reverse walk becomes one record kind: one operand record per
>   instance (machine per site, representation, seed, floor, exit, tags, names, host).
>   - Two walk behaviours carry the manifesto's five exits as hand types.
>   - Hosts: inline, as today, and a new VM record kind that calls a per-instance static function
>     built from the shared reverse-block renderer.
>   - Machines come from one per-site table built by one optional-machine builder.
>   - The first client built ON it is variable lookbehind's `reverse-dfa` candidate source, as two
>     exit rows: `exist`, the answer on an exact capture-free branch, and `gate`, a filter in front
>     of `range`. A HELD `commit` row comes later.
>   - revdet (structural representation) and the landmark walk migrate onto it byte-identically.
>   - The roadmap's A-REV area takes the step list of docs/design/stream/arev.md §4. Its first step
>     (the operand record for the three DFA walks) is no longer behind P-b.
> - **Why:** the owner's 2026-11-05 direction, "cross-engine pieces used where needed".
>   - Three of the walks already share one renderer, so the kind is mostly a description, which
>     makes it cheap.
>   - A VM-hosted lookbehind walk built outside it would be a third hand-written walk, and the
>     ratchet (D185) rejects that.
>   - Soundness rests on the machine's recorded exactness (`Nfa.erased`), never on the kind. The
>     atomic counter-example of vlookbehind.md §2 is a witness of the `exist` row.
> - **Ratchet:** R03 is restated (revdet's private walk record, not the analysis file), and R28 is
>   added (the second reverse `DfaDir`). The steps delete R28, R03 and R10 in that order. The
>   lookbehind client is ratchet-neutral (an instance).
> - **Not decided:** the `commit` row and a single-pass enumerator (HELD); tag unification for
>   revdet on table machines (HELD); unbounded lookbehind (its own HELD row); P-b's order.
> - **Revisit when:** a client needs a third walk behaviour, or the structural representation
>   proves to be a second mechanism rather than a representation row (owner question 2 below).

## Questions for Frank (plain words; leanings are not rulings)

1. **Should the reverse-walk cleanup land before anyone needs the lookbehind speed-up?** The
   first two steps change no generated code. They only make the four reverse walks share one
   description.
   - The lookbehind step itself waits for a measurement (D77).
   - Leaning: yes, as ride-alongs. Step 1 with the next change that touches the reverse pass
     (likely [REVBLOCK-VIEW]), step 2 with the next change to revdet's code. Neither gets a lane of
     its own. They make the lookbehind piece an instance of the kind instead of a new walk.
2. **Is revdet's walk the same thing as the DFA walks, drawn differently, or a separate
   mechanism?** It walks the pattern's nodes backward as VM steps instead of a table.
   - My reading: it is the same reverse machine in a different representation. revdet's checks
     prove that machine is deterministic. So it would keep its own drawing code, as a declared
     "representation" next to the table one, the way the DFA already has several table forms.
   - The alternative: rewrite it as a table walk. That changes code and needs capture tags on DFA
     tables, which do not exist today.
   - Leaning: count it as a representation (ratchet row R03 falls when its private record goes),
     and hold the table rewrite until a measurement shows it would be faster.
3. **The landmark walk's last step (writing its whole search body as records) is the smallest real
   example of the "DFA top level as records" proof (P-b).** Should it be P-b's first instance
   rather than waiting behind it?
   - Leaning: leave the roadmap's order (P-c, then P-b, then this). The landmark body uses every
     record family at once, which makes it a good falsifier but a poor first step.
4. **For a lookbehind, should the reverse machine ever give the answer on its own, or always just
   filter?** Answering alone is exact only for lookbehinds with no atomic parts, no nested
   lookarounds and no capture groups.
   - Leaning: build both rows together when the measurement asks. Filtering is the safe default
     everywhere. Answering alone is one more row with its own witness. The bench's negative
     pattern has no captures, so it would get the larger win.

## What the design does NOT decide

See `arev.md` §8:

- C names and layout of the record.
- Whether the machine table lands with S1 or with S3 (leaning S3).
- The `commit` row and a single-pass enumerator.
- TDFA tags for revdet.
- Tagged single machines for multi-branch lookbehinds.
- Unbounded lookbehind.
- P-b's order.
- Any manifesto or APPROACH.md change.

## Ranked goals and the standing questions

Goals (`arev.md` §0, ranked):

1. G1: answers never move.
2. G2: one mechanism (ratchet R28/R03/R10 to 0, no new member).
3. G3: a cross-engine piece where needed.
4. G4: no blindness at the seam.
5. G5: speed as a gate.

The standing questions are answered in `arev.md` §7:

- Measurement: relevant to S3/S5 only.
- Independent control: relevant; libpcre2 10.46 plus the comparator plus the recipes. A choice
  row's witness is checked in its default build.
- Regeneration: mostly not relevant. S3 is an abi event plus a `tuning.md` section.

## Evidence (this lane)

- **libpcre2 10.46 answers**, from the harness vlbdesign wrote
  (`docs/dev/lanes/vlbdesign_evidence/startpos.c`), compiled into
  `$PCREC_TMPDIR/scratch/arevdesign/`:
  - `a+b` on "aab" from 1: [1-3]
  - `[a-z]+@x` on "ab@x" from 1: [1-4]
  - `[ab]+[bc]` on "aab" from 1: [1-3]
  - `(?<=a{1,2})b` on "aab" from 2: [2-3]
- **Routes**, read from the stamps of main's `build/pcrec`: `RX_DFA_SCAN "landmark-walk"` for the
  first two and `"unanchored"` for the third.
- **Not measured:** no timing, no build, no `make`.
- **Interpretation of "the witness that can fail in both builds".**
  - For the byte-identical steps (S1, S2, S4): the same sabotage is red at the old site on the base
    build and at the new site on the step's build. The rows are carried and re-aimed: S74, S1825,
    S1827, S759, S760, S50-S52, S94, S160, plus the two floor cells above.
  - For the lookbehind's choice rows: red in the default build, where the row admits. In the deny
    build, stage 1's `range` witnesses are the control.
  - If the manager meant something else (for example both kit layers), that is a text fix.

## Validation

- `scripts/check_claudemd_size.sh --all`: 349 files within limits.
- `scripts/plan_lint.sh`: 299 rows, 0 violations.
- No `docs/spec` line cites in the new text.
- The [STREAM] plan row was not changed: the area plan lives in the roadmap and the row's status
  is still accurate.

## STATE AT HANDOFF

- STATE: delivered (design only). Branch lane/arevdesign; commits dd89fa9bb (note + roadmap +
  CLAUDE.md) and this report.
- Rulings file `docs/dev/lanes/arevdesign_rulings.md`: present and EMPTY at every checkpoint. No
  entry was applied.
- DELIVER block: `docs/dev/lanes/arevdesign_deliver.txt` does not exist, in the worktree or the
  main tree.
- Next: the critic round on `arev.md` rev 0 and the roadmap A-REV hunk. Then the manager restates
  §5's R03 and R28 rows, and Frank answers the four questions.
- For a resuming agent:
  - Every anchor is at 7cebea04e.
  - The roadmap edit touches only the §1 A-REV row and the A-REV section.
  - The manifesto, vlookbehind.md and its review are untouched.
