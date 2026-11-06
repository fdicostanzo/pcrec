# vlbrev4 — vlookbehind design rev 4 (review 2026-11-06 r2 applied)

Lane vlbrev4, opus, 2026-11-06. Text and probes only: no build go, nothing under `src/`, `cli/`,
`lib/`, `memfn/` or `tests/` was edited. Branch `lane/vlbrev4`, from main `a8f5d4721`.

## Stage 1 in plain words (for the build-go question)

**What stage 1 builds.** Lookbehinds whose alternatives can match a RANGE of lengths, such as
`(?<=a{1,3})x` or `(?<=ab?|c)x`, start compiling instead of being refused, up to 255 characters
per alternative (PCRE2's default), and nothing longer than 65,535 characters in any alternative.
For each such alternative the matcher tries the possible start positions farthest first, runs the
alternative forward from each one, and keeps the first that ends exactly at the current position.
That is what PCRE2 does. Fixed-length lookbehinds keep their exact code today: the compiler picks
the old code whenever an alternative has one length. Concretely the build adds:
- the width rule with the two limits, and two rows in the limits table;
- the candidate loop and the two-row emission table ("one length: today's code; a range: the
  loop");
- one position slot per varying alternative (in the existing span-loop slot family, as its own
  sub-block), one shared count variable per artifact, and a few new members in the VM's record
  vocabulary;
- one new encoding helper, `$_fwd_step` ("one character forward, never past the cursor"), beside
  the existing `$_back_step`. It appears only in artifacts that use the loop;
- two encoding checks that now read the list of encoding helpers FROM the encoding layer instead
  of a hand-written list, a three-mode (`byte`, `utf8`, `utf8-invalid`) libpcre2 differential, new
  and re-aimed sabotage rows, 32 corpus rows flipped from "refused" to real answers, and the spec
  paragraphs that change.

**What it gates on** (§6 of the note):
1. 0 answer differences from libpcre2 10.46 over a generated cell set in all three modes, outside
   one stated, already-documented divergence class;
2. every artifact that compiles today stays byte-identical (the identity gate, re-pinned only for
   the patterns that newly compile);
3. pcrec accepts nothing libpcre2 refuses (one stated exception: a zero-width repeat inside a
   lookbehind), and its per-alternative "one length or not" judgment equals libpcre2's;
4. a long-subject budget cell answers or gives up at a stated size, never on frame capacity;
5. every sabotage row is red when planted and green when not;
6. the encoding checks are green with the new derivations.

**What it leaves for stage 2.** Backreferences inside a lookbehind (`(a|bc)(?<=\1)x`): the width
memo per group, the deferral, and five refusal rules. Stage 3 (a reverse-automaton source of
candidates, for speed) stays HELD.

## What changed (rev 4, marked `[r2-1106 Fn]` inline)

- **F1 (the ruled design choice).** The forward step is a seam ENTRY, `$_fwd_step`, engine-callable
  and inline like `$_back_step`, in the mask only for `range` branches. Contract: `next_pos` over
  the prefix `[0, bound)`. The VM body holds one call line, identical under both encodings, so:
  DD12a(i)'s body comparison holds; the entry-shape knee never reads an encoding-dependent length
  (`RX_VM_PROGRAM_BYTES` is equal across encodings for today's lookbehinds, measured); the step's
  prose is a D112 doc pair, gone under `-fno-comments`; every "one splice" sentence stays true.
  - DD12a(i) derives region (1) from the seam: a seam function `pcrec_enc_entry_symbols` names each
    entry's defined symbols, a test reader `tests/codegen/enc_entry_list.c` prints them, and the
    Python block replaces `SIG_RE`'s two alternations, `TWINNED`, the `span_ci_helper` mapping and
    the residual floor keys with that table. Judged PROPORTIONATE (about 40 + 60 lines plus a
    shrinking Python block; it deletes hand lists whose drift the file records three times), so the
    named-region fallback was not taken; the note states what the fallback would have been.
  - K49 reads its sites from a seam-declared mask, `PCREC_ENC_BOUNDARY_ENTRIES`, and ties each
    member to `next_pos` over every bound; the retry advance keeps its anchored extraction (a field,
    not an entry).
  - W14's byte-step arm: two plants, two named detectors ([M5-SEAM]'s `fwd_step` count; K49's tie).
  - STOP RULE: NOT triggered. No existing encoding's output moves a byte: inline definitions are
    emitted only for masked entries, and only newly compiling patterns set the bit.
- **F2.** Premise reproduced: `(?:(?*.*(?<*a?))b)*$` on `bc` is [2-2] in libpcre2 10.46 (byte and
  UTF, every start). W-low is an answer witness; the trail on `LO_i` is stated as necessary; the
  plant is the buildable "untrailed local" form; the overrun's expected outcome is a give-up, never
  an out-of-bounds read, confirmed at build under asan with a small `--work-budget`.
- **F3.** One artifact-wide `<p>_lb_count`; `VmFrame.lb_count` from the count pass's
  `nlblow_total`; one name source, `pcrec_vm_local_name`.
- **F4.** `LO_i` slots are an arithmetic sub-block at the top of the `low` family
  (`vm_slot_lblow`); readers named: `vm_slot_name`, the listing, `VmSnap.lblow` and the region
  saves.
- **F5.** S133 keeps its one builder line (both rows' first back-step go through it; the far step
  has its own builder and twin); S123 keeps one site; the operand's absent spelling is `byloc`;
  S-U4 re-aimed on `(?<=ab)x` (measured: `(?<=a)x` has no lookbehind label); W12(a)'s K134
  mechanism stated.
- **F6.** Gate 1's oracle and diff script gain the `byte`, `utf8` and `utf8-invalid` modes, with
  per-mode populations.
- **F7.** [VMREC]'s list: `docs/design/plan_row_bodies/VMREC.md`, written by the build commit; §13
  Q5/Q6 marked ANSWERED.
- **F8/F9 (doc).** The model's claim restated as "the candidate sequence"; the 160-byte claim and
  rev 1's sentence corrected; G2's question closed.
- **§6 gains the complete stage-1 build-unit table (U1-U9)** with every reader of what each unit
  changes. **§16d** maps every finding.

## Evidence

`docs/dev/lanes/vlbrev4_evidence/premise.out` (libpcre2 10.46 via `tests/lib/p2probe.c`; pcrec built
in this worktree, one `nice make -j4`, rc 0): F2's cell; pcrec's refusal of it today; the S-U4
labels; the `[K49]` comment under `-fno-comments`; equal program-bytes stamps and the `back_step`
definition's placement; a lookbehind-free artifact carries no `back_step`.

## Observations for the manager (not acted on)

- PRE-EXISTING: the retry loop's `advance` text emits its five-line `[K49]` comment even under
  `-fno-comments` (measured), which contradicts enc.h's D112 note that `advance` "ships ... all
  code". Splitting it into a doc pair would move every utf8 `-fno-comments` artifact (an abi
  event), so it is out of stage 1. Worth a filed row.
- F10 (out of delta; `(?<!\G|é)` on ill-formed `\xc3`): whether the compliance page lists it was
  not checked here.
- §6's U7 row: a corpus change moves pins beyond the identity gate (start-set manifests, axes
  allowances, size tripwires); the build's `make test` finds them.

## STATE AT HANDOFF

STATE: done. Design rev 4 committed on `lane/vlbrev4`; no validation run is owed (text and probes
only). Rulings file `docs/dev/lanes/vlbrev4_rulings.md`: empty at every checkpoint (no entry to
apply). Files: `docs/design/vlookbehind.md` (rev 4), `docs/design/CLAUDE.md` (status line),
`docs/dev/lanes/vlbrev4_evidence/premise.out`, this report, the history-index line. arev.md was
not edited (its pick-up list gained item 12 and a note on item 9 in §16c).
