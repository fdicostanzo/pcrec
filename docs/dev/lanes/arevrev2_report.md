# Lane arevrev2 — A-REV design note rev 2 (re-check 2026-11-06 r1 applied)

Lane: arevrev2 (opus), 2026-11-06. Branch `lane/arevrev2` from main `6e01c810b`. Text and probes
only: nothing under `src/`, `cli/`, `lib/`, `memfn/` or `tests/` was edited. `vlookbehind.md` and
`manifesto.md` were not edited (ruling 1; the brief).

## What changed

- `docs/design/stream/arev.md` → **PROPOSED rev 2**. A REVISION 2 block at the top; corrections
  tagged `[r1-1106 <id>]` inline; a new §12 maps every id of the re-check (A1-A3, D1-D6, R1-R8,
  N1-N7) and vlookbehind rev 3's eleven pick-ups (plus client-4/5/6) to sections.
- `docs/design/stream/roadmap.md` A-REV area and its summary row → rev 2 (ownership, the host as
  members, the admission additions, S3's prerequisites, PLAN items, S1M's size).
- `docs/design/stream/CLAUDE.md`, `docs/design/CLAUDE.md`: the `arev.md` line says rev 2.
- `docs/dev/lanes/arevrev2_evidence/`: `probe.c` (libpcre2 10.46 probe, copied from the review's
  critics), `premise.out` (every new cell and pcrec's NFA-cap refusals at 6e01c810b), `model.py` +
  `sweep.py` (the review's literal model and sweep, with A1's rule applied; `model_a1.diff` is the
  rule as a diff against the critic's model), `sweep.summary`.

## The fixes, in plain words

- **A1 (answer).** On the non-atomic `(?<*` form, the existence row now pushes the next branch's
  retry frame (at the cursor, not on the last branch, exactly as the `one-length` row does) before
  it reports success. Re-ran the review's 552,900-cell sweep through this rule: **0 differences**
  against libpcre2 10.46 (rev 1's rule: 1,702; the `range` control: 0). The composition argument
  now lists every continuation of every removed frame (the review's new soundness rule). Witness
  `HO-NA`. Also found: the review's third A1 cell (`(?<*a{1,2}|(b))x\1` on `abxb`) does not reach
  the hole; the unpatched model already gives libpcre2's answer there.
- **A2 (answer).** A new first conjunct (c0): an upper bound on the branch's NFA states, computed
  on the AST before any NFA is built, against the same effective cap; above it the branch declines
  to `range`. Its control is the builder's real count (a check that the built NFA never exceeds the
  bound). An optional NFA build and a retry rung were considered and argued against in §2.5.
  Premise reproduced: `\p{L}{255}b` under `-e utf8` refuses at the NFA cap today (`{36}` passes,
  `{37}` fails, so one `\p{L}` costs 3,543-3,641 states), `(?<=\p{L}{255})b` compiles, and
  libpcre2 accepts `(?<=\p{L}{1,255})b`. Witness `HO-N`.
- **A3.** The part's read set is clipped at both edges and includes `subject_length`; at `from`,
  the POSITION selects the start view (end, end-of-line, base) before any byte is read. Cells:
  `(?<=a{1,2}$)\nb` on `aa\nb` nomatch, `(?<=a{1,2}\z)\n` on `aa\n` nomatch, controls with `\Z` and
  `(?m)$`. K74 ([UTF-END-ASSERT]) is named in the gate beside D142.
- **Rulings applied.** (1) §3.1's rows are now proposals P1-P11 for vlookbehind's adopting
  revision, with their own witness ids (`HO-*`) and a mapping to vlookbehind rev 3's WD1-WD6; that
  revision is an S3 prerequisite. (2) The in-body call is four MEMBERS of existing lists (a result
  local, a `VP_AUTO` piece, a cursor-from-local seek, a typed work operand); the part uses the
  code-segment declaration slot; only its declared EFFECT SET waits for [VMREC] (c), as one
  declaration shared with kit windows and code segments, and S3 does not wait for it. (3)
  [ROWCONJ] is an S3 prerequisite; R19 does not rise. (4) The lever is a `--harness=` arm, which
  `make test-axes` already runs as an internal arm, so GIVEUP1 compares it with no new mechanism.
- **The rest.** The record's missing fields with owners, and the two kit replies that keep render
  impure (D2); S1M's swap as roles every reader uses, `nedfa` in, `xprio` out, the reader grep
  recipe (160 sites), cost restated to L (D3); stems per instance (D4); rev 3's pick-ups (D6);
  the oracle per `lang` with the callout form (R1); unit ownership of the round trip, oracle and
  golden check (R4); stage 1's witnesses kept on `range` by the deny arm (R5); the recorded
  per-branch row as the key (R6); the rung's readers, all-or-nothing, a `trlowsize` witness, built
  in S3 only (R7); ratchet recipe words (R8); N1-N7.

## STATE AT HANDOFF

- STATE: delivered. All commits on `lane/arevrev2`.
- Rulings file `docs/dev/lanes/arevrev2_rulings.md`: empty at every re-read (last re-read before
  this report); no entry to apply.
- STOP RULE: did not fire. A1 and A2 were both fixed soundly; S3's row is not restricted.
- Validation: the A1 sweep (552,900 cells, 0 differences) and the premise probes, both in
  `arevrev2_evidence/`. `make test-plan-lint` and `make test-spec-history` pass (no plan.md edit;
  no spec line cites added). One `make -j4` build of the worktree for the pcrec-side probes. No
  suite run is owed (text only).
- No DELIVER block was written for this lane (`docs/dev/lanes/arevrev2_deliver.txt` does not
  exist), so `scripts/lanecheck` was not run.

## Owed elsewhere (PLAN items for the manager; not edited by this lane)

1. [GIVEUP-DIFF]'s plan row: widen its trigger and scope to the lookbehind row (arev §3.1).
2. roadmap §5: the R28'/R03'/R10' rows with rev 2's recipe words (arev §4.3); a prerequisite of
   S1's gate.
3. vlookbehind's adopting revision of P1-P11, when the proof step is designed for build (ruling 1).
4. The [STREAM] status line was left as is (still accurate).

## Open questions (plain words)

None for Frank. One for the manager, answer-free: the witness id prefix `HO-*` (hand-off) was
chosen so vlookbehind's adopting revision can take the list whole; rename at adoption if you prefer
vlookbehind's `WD` space.
