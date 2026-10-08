# normscope — scope of the R4h layout-normalization pre-commit (Q-R4h-1 (b))

Lane normscope, 2026-10-08, sonnet, read-only (main 9029f5db; build/pcrec only, no make). Recorded verbatim-in-substance by the manager from the lane's hand-back.

## Headline
The filed G2 under-lists the delta. Reading `memfn/src/generic.c` `stmt_advance`, the kit's ADVANCE text differs from pcrec's in FOUR ways, not two:
- (a) condition wrapped or single-line, and the body spelled `) step;` vs `) { step; }` (the filed G2);
- (b) the kit wraps `more` as `((more) && ...)` and the member test as `&& (member)`. pcrec writes `more` bare at all four sites, and the member bare at STAY/EDGE (already parenthesized at VMSPAN);
- (c) the cap suffix: the kit writes `%lluULL`, pcrec `%dUL` (EDGE bounded, VMSPAN `it_`);
- (d) the kit's body is always a braced multi-line block, with `cnt++;` on its own line only when there is a counter.

Target per generic.c:
```
ind  while ((MORE)[ && CNT < NULL] && (MEMBER)) {
ind      STEP;
ind      CNT++;      (only with a counter)
ind  }
```
**Prerequisite:** the kit freezes the exact target text as a pinned render (tests/memfn/arm_fixtures.c `render_adv`) of all four shapes with real hook texts. r4hprep's finding says a byte-identical row may paste `member` bare.

## Sites (lines at 9029f5db)
1. `src/gen/emit_dfa.c` `dir_fwd_skip` :7414-7416. Now one line, `while (scan_position [+ 1 <|<] subject_length && <p>_<m>_stay<K>[subject[scan_position]]) scan_position++;`.
2. `emit_dfa.c` `dir_rev_skip` :7441-7443. Same shape, rewinding.
3. `emit_dfa.c` `emit_scan_edge`, the unbounded loop :9099-9101.
4. `emit_scan_edge`, the bounded loop :9109-9115. It becomes one condition line plus `ADV;` and `scan_run_length++;`. The peeled ADV, the `= 1` declaration and the `== NUL` cap test stay pcrec's.
5. `src/gen/emit_vm.c` `vm_emit_span_scan` :4670-4686. Normalize all strides in one printf sequence.

Not touched: the lazy cursor loops (emit_vm.c:4979-4983, :5058) and the PF walks (already the kit's).

## Movers (grep sample, 697 tests/base patterns; 642 compile)
- Default engine: STAY 39, EDGE 231, VMSPAN 80. The union is 319 of 642 (50%); DFA-side only, 267.
- `--engine=vm`: VMSPAN 360 (56%).
- cpset EMITTED_BYTES: about 4-5 of 12 rows.
- Secondary effects:
  - (i) +10-35 code bytes per site, so size-cap refusals near the caps could flip;
  - (ii) the VM entry-shape knee at 4096. 15 of 440 span-loop VM artifacts sit in [3900,4300] bytes, so RX_VM_ENTRY_SHAPE flips are possible, an object-code mover to be declared by id;
  - (iii) RX_VM_PROGRAM_BYTES moves.

## Overlap with refactor B
Disjoint by function. The only shared file is emit_vm.c (the VM_PREFILTER_WHY writer at :11264, far from :4670). The interaction is in the gates: B's zero-mover sweep needs a ref after the normalization lands, and both self-pin the recursion (B) FILEPIN. Order: normalization first; B's census in parallel; B's build after the normalization merges.

## abi 66 -> 67 readers (by grep)
- emit_dfa.c:54.
- run_codegen_tests.sh:3042 ABI_EXPECT plus :3044.
- match_api.md: the §6 change-log and the :302 example.
- run_recursion_identity.sh:1186 FILEPIN, self-pinned.
- The cpset manifest's `.abi` digit.

Byte-count readers:
- m5_stage1_stamps.tsv;
- tests/resource K59-PREMUL pins and the size_moved witnesses;
- run_size_term.sh pool ratios;
- the tests/size tripwire and artifact_size_log.tsv.

Text-shape readers:
- run_codegen_tests.sh :94/:243/:256 (they grep the one-line stay loop);
- tuning.md:1519-1523 (the scan-edge example, a D80 hunk);
- src/gen and tests/codegen CLAUDE.md.

Sabotage: S214 (the `scan_run_length < %dUL` printf) and S72 (the rev-skip printf), plus whatever sabotage_anchors.py / SABANCHOR find.

**Hidden cost:** run_recursion_identity.sh (A) compares call-free program regions against the frozen ac4917d. VMSPAN is in-region, so every cursor-rung VM artifact differs. It needs a named exception in the `bref_rename_rewrite()` style, with a text-census non-vacuity arm.

## Recommendation
- ONE declared-mover commit: the five edits, abi 67, all re-pins, spec and CLAUDE.md hunks, and the (A) exception.
- No shared helper (R4h deletes this text; D77).
- Tier: sonnet.

Validation:
1. make and make strict.
2. A ref binary from 9029f5db, compiled with the same -o basename.
3. emit_sweep --ref over all streams: movers == a grep text-census on the REF artifacts, 0 off-diagonal both ways, the refusal set identical, and emit-ir/facts/dumps unmoved. Positive control: c-default/c-vm/composition MUST move.
4. run_object_neutrality.sh over the movers: .text/.rodata identical except the listed entry-shape flips, and 0 refusal flips.
5. Kit render_adv of the four shapes diffed char-for-char against the emitted lines.
6. A failing-direction plant.
7. test-codegen, cpset-structure, recursion, resource, size-term, the size tripwire, then a full make test.
8. S214/S72 re-aimed and run solo; SABANCHOR clean.
9. A bench inbox note (abi 67, object-identical) and the FILEPIN recorded.
