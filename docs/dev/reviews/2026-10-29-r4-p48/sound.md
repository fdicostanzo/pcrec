# CRITIC sound — p48

Twins (mine, built once each under scratch/crit-p48/sound/, from `git archive` of the
review tree 02a054851):
- `tentry` = review tree + ENTRY rule as written: the four sites' `scan_span != 0` ->
  `scan_span > 0` (emit_dfa.c:12874 `dfa_start_is_scan_head`, :12896-12897
  `dfa_seed_can_be_scan_head`, :13705-13706 and :13768 the two revend `entry_head`
  writers). Patch: sound/entry.patch.
- `trelax` = review tree + RELAX as written, keeping (6) and (8): `shaped()` accepts a
  split exit iff the keyed set's target is the state itself (one-state self-loop), with
  a private exit value (-1000-s) so it never chains or is anyone's predecessor.
  Patch: sound/relax.patch. Composition (RELAX + ENTRY) = trelax artifacts with the
  entry `goto` line hand-deleted where no entry state is a bounded head.
- Driver (sound/drv/): for every subject and EVERY `search_from` 0..n, `rx_search`
  with all capture spans; for every pos 0..n, `rx_match` (anchored length). Oracle:
  libpcre2-8 10.46, same loops (start_offset / PCRE2_ANCHORED). Harness: sound/run.sh.

## Findings

**Answer to the one question: no match answer moved.** Neither rule, applied as written
to the review tree's real emitter output, moved match/no-match, start, end or any
capture span against libpcre2 on any witness, at any `search_from` (0..n) or any
anchored `rx_match` position (0..n). The two findings below are about how the rule is
STATED and CHECKED, not about its soundness.

### SOUND-1 `dfa_start_is_scan_head` is not an entry-dispatch site; patching it as written also moves the prefilter
- status: CONFIRMED (code reading + twin text)
- severity: design      part: ENTRY
- effort: S      blast radius: which of the "four sites" the build edits; emitted text of artifacts whose `s0` is an unbounded head
- where: subject §Design "The entry rule" (line ~612-615: "It sits at the four sites above") and §One-state relaxation (~503-506); emit_dfa.c:12855-12875, :12920, :12982-12984, :13059
- claim: the design lists `dfa_start_is_scan_head` as one of four entry sites. Its own
  header (emit_dfa.c:12855-12871) says its ONE reader since [OPT-EDGE] STEP 1.1 is the
  prefilter placement (`s0head`, :12920 -> :12982/:12984 generic path vs :13059 edge
  path); the entry question is `dfa_seed_can_be_scan_head` (:12890), which merely calls
  it first (:12892). Changing it to `scan_span > 0` (what my `tentry` and, per the
  subject, `patch_nogoto.py` did) therefore also changes "where does the prefilter live"
  for an `s0` that is an UNBOUNDED head: it moves from the edge path to the generic
  path, which never holds `s0` again after entry (every step back onto `s0` goes to the
  edge path) — so after entry the prefilter is never reached.
- why it is not an answer move today: scanedge.c:500 refuses every NON-accepting `s0`
  self-loop, so an unbounded `s0` head always accepts (plain, class-invariant, (2)),
  and the prefilter's own guard `state == s0 && recv == (size_t)-1` (pf_open,
  emit_dfa.c:6624) is false from the first probe on, in both arms; at entry both arms
  run probe-then-prefilter at the same position. On `[a-z]*` the twin's text differs
  from stock only by the entry `goto`/label (4 lines, 2 machines) and no prefilter is
  selected. So it is answer-neutral by a fact about the PASS (the s0 refusal), the same
  kind of cross-file coupling the header at :12862-12871 says STEP 1.1 removed.
- proposal: state the rule at THREE sites: `dfa_seed_can_be_scan_head` (its `s0` test
  spelled locally with `> 0`, or a `dfa_state_is_bounded_head` helper) and the two
  revend `entry_head` writers; leave `dfa_start_is_scan_head` (`!= 0`) as the prefilter
  placement predicate. That keeps the prefilter question and the entry question on
  their own predicates, as the STEP 1.1 comment demands, and the build's diff stops
  depending on scanedge.c:500.

### SOUND-2 The entry rule's first sabotage witness cannot be seen by any answer check
- status: CONFIRMED
- severity: design (check)      part: ENTRY
- effort: S      blast radius: the sabotage row the build adds
- where: subject §"The three standing questions" item 2, sabotage bullet ("Planting
  `!= 0` back must break the first; planting `< 0` must break the second's answers")
- claim: "planting `!= 0` back" restores today's entry jump on a seeded UNBOUNDED head,
  which is answer-identical by the rule's own argument (and measured: stock vs `tentry`
  answers identical on base10num-noatomic, base10num-grok (auto/hybrid), `(?<=a)[a-z]*`,
  `[a-z]*`, `\b\w*`, `\s+$`; the C differs exactly by the goto + label lines). So that
  half of the sabotage pair is detectable only by a TEXT/structure check (or an
  instruction count), never by the corpus/differential sections the subject's
  empirical check ran. The second half holds and is a real answer witness: deleting the
  entry jump on `(?<=a)[0-9]{0,4}|(?<=b)[a-z]*` (a seeded BOUNDED head) moved 8 of 84
  answers (e.g. subject 1, search_from 1: oracle 1,5 vs 1,1) — which is also my harness's
  positive control that it can see a broken entry.
- proposal: name the detector for the first witness: a codegen structural assertion
  ("a seeded machine whose entry states are all unbounded heads carries no
  `goto <m>_scan_edge;`"), e.g. in the codegen structural checks, plus the base10num
  artifact pin; keep the bounded witness as the answer sabotage.

## PROBED-AND-HELD
- Code fact "the kill loop runs `if (ch->span > 0)`" — held: scanedge.c:711-714, inside
  the take loop (an untaken chain kills nothing). scanedge.c is unchanged b05ccfc0b ->
  02a054851 (`git diff --stat`), so it held at both.
- Code fact "`emit_scan_edge`, `span < 0`, never reads an exit" — held: emit_dfa.c:12573-12583
  emits advance, the kit loop and the constant accept record, then returns; the only
  exit-adjacent read is `facc` from `scan_next` (:12527-12529), which for an unbounded head
  is the head itself and is unused on that path.
- Code fact "`dfa_form_derive` re-derives (8) and refuses" — held: emit_dfa.c:12745-12757,
  any non-`s0` seed target with `scan_span != 0` on a reseeding prefilter is a loud
  internal error; it tests `!= 0`, so dropping (8) for unbounded heads must move it too
  (the subject says so). Also "(6) and (8) already apply to unbounded heads": held,
  scanedge.c:430 (view-target) and :479 (reseed) both precede the unbounded branch :499.
- ENTRY, accepting unbounded head as the entry state, last-accept before the first step,
  start at end / empty subject (every `search_from` 0..n incl. n, empty subject lines):
  `[a-z]*` (constant-seed unconditional goto removed, s0 accepting head), `(?<=a)[a-z]*`
  (seeded, accepting head), base10num-noatomic (seeded blocked head) — stock, `tentry`,
  oracle identical: 52 + 70 + 114 lines (all spans, all from, all anchored positions).
- ENTRY, VM hybrid locate machine: base10num-grok default engine (stamp "vm", DFA locate
  with the seeded goto) — 114 lines identical across stock/`tentry`/`trelax`/oracle.
  (`--engine=vm` emits no DFA at all: not a witness.)
- ENTRY, anchored machines: every witness above also ran `rx_match` at every position;
  the anchored machine's goto is removed by the twin too (`[a-z]*`, base10num) — held.
- ENTRY, bounded + unbounded entry candidates together: `(?<=a)[0-9]{0,4}|(?<=b)[a-z]*`
  — the rule keeps the jump; `tentry` text identical to stock; 84 lines identical to oracle.
- ENTRY, reverse/revend and END views: `\s+$`, `[a-z]*\d*$`, `[a-z]*\z`, `\b\w*`: the twin
  is text-identical to stock (no entry jump either way). By code: the revend seeds are
  view targets (`revend_seed_state`, emit_dfa.c:13662-13674) and (6) (scanedge.c:430)
  never lets a view target be a head, so those two writers can only fire where the seed
  state has no view; no witness found one (not a soundness matter).
- ENTRY, "any step from the head that is not the generic table step": by code, the
  generic path at loop top runs probe, prefilter (`state == s0 && recv == -1`), stays
  (heads excluded, emit_dfa.c:5113), views, step; for an unbounded head every one is
  either the edge path's own (probe, prefilter) or vacuous, and the step reads an intact
  cell. The prefilter's reseed cannot install a head ((8)). Held.
- RELAX, forward split-exit runs, accept at the stop position, rare-byte restart loops:
  `\d+-`, `[^<]*</`, `oodo|xzxj`, `\x93[\x20-\x7e]*\x94`, `foo[a-z]*bar`, base10num
  (new accepting split-exit digit head in forward and anchored machines) — `trelax` vs
  oracle 0 differing over 200 + 200 + 200 + 200 + 206 + 114 lines.
- RELAX, reverse direction / leftmost start / captures: `"([^"\\]+)"\s*:\s*` (group 1
  spans), `a.*?(?i:select)`, `a.{1,50}z`, `\b(?:fail|abort|panic)\b.{0,40}\b(?:disk|net)\b`,
  `x[0-9]{3}[a-z]*(?:1|2)` (relaxed head in the reverse machine, rewind side) — 0
  differing over 206 + 218 x 4 lines.
- RELAX, `\b` / class context half of (2): `\b[a-z]+(?:1|2x)?\b` — the class-variant
  head is refused by `member_ok` exactly as today (no edge), 218 lines identical.
- RELAX, [OPT-VEDGE] END view: `[a-z]+(?:1|2)?\z` — 218 lines identical.
- RELAX, cap and ranking: `a+1|b+2|c+3|d+4|e+5|f+6` (more than 4 split-exit candidates per
  machine) — 218 lines identical. By code the ranking is answer-neutral: the (7) clash
  test (scanedge.c:671-672) is symmetric and pairwise, so any order yields a set that
  passes it; a relaxed head enters (7) only as a fall-through (`ch->next == ch->head`),
  exactly like today's unbounded heads; kills happen only for taken bounded chains.
- RELAX, (7) with a bounded chain whose fall-through is a relaxed head: not reached —
  `x[0-9]{3}[a-z]*(?:1|2)` and `x[a-z]{2,5}[0-9]*(?:!|\?)` formed no bounded chain in any
  machine (gap: no witness of that seam; the argument above covers it).
- RELAX + ENTRY composition (a newly admitted split-exit head that is a seed target):
  `(?<=[a-z])[a-z]*(?:1x)?` and `(?<=[a-z])[a-z]*(?:1|2x)` (stock: no edge; `trelax`:
  relaxed seeded heads with the entry goto), base10num-noatomic and -grok — with the
  goto hand-deleted (the entry rule applied, all heads unbounded): 104 + 104 + 114 + 114
  lines, 0 differing vs oracle and vs `trelax`.
- New default reader since b05ccfc0b: the `cover` LOCATE row is routed by default at
  02a054851 (emit_dfa.c:4846-4849) and reads scan annotations through known.c `kn_step`
  (known.c:52-60); for an unbounded (incl. relaxed) head it returns the head itself,
  equal to the intact self-loop cell — answer-neutral for both rules. Not in the subject's
  seam list (it was harness-only at b05ccfc0b).
- Not probed: the retry machine (`RX_ITER_RETRY` != "none") — no witness found within the
  compile budget; covered only by the generic argument. 53 pcrec compiles in total.
