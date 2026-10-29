# CRITIC contract — vmtrail
## Findings

### CONTRACT-1 Callout read set must be §11.3¶3's pattern ncap, not NCAPS: under --no-captures B/U delete or untrail writes a callout reads
- status: CONFIRMED (the trap exists and changes an answer; whether a build would fall into it is SUSPECTED)
- severity: answer
- effort: S      blast radius: vmbc row 7 / trailgen row 4 wording; one sabotage row
- where: vmbc_report "declared rule table" rows 7 and 9; trailgen "Proposed general cleanup" (row 7 "unchanged"); spec match_api.md §11.3¶3
- claim: row 9 (accept) reads capture slots `0 .. 2*NCAPS-1`. Row 7 (callout/code site) says only "every capture slot". The emitted callout view is `rx_co_ctx.caps = (const ptrdiff_t (*)[2])slot_values; rx_co_ctx.ncap = <pattern groups + 1>`. Per §11.3¶3, ncap is the PATTERN's group count "whatever --no-captures says". Under `--no-captures`, NCAPS=1, but the callout still reads slots 0..2*ncap-1. A row 7 keyed on NCAPS (the natural reuse of row 9's set) leaves the group writes dead, so DELETE removes them; and UNTRAIL leaves them stale across resumes and attempts.
- evidence / repro: review-tree pcrec, `--allow-code=c --no-captures --emit-main -p rx --features all --pattern '(a)(?:(b)|c)(?C\`c: return RX_CAP_SET(2) ? RX_FAIL : RX_PASS;\`)d'`. In the emitted code, RX_NCAPS is 1, RX_NSLOTS is 8 and `rx_co_ctx.ncap = 3`. A twin (mine) deletes the six group RX_SET lines, which is what B does if the callout read set is {0,1}. On `abd`, stock gives `nomatch` and the twin gives `match 0 3`; on `acd` both match. The stock answer is the spec's: group 2 is closed and visible to the site, so the site fails.
- proposal: state row 7's read set as `slot_values[0 .. 2*ncap-1]`, with ncap from §11.3¶3 (the pattern's group count), plus the slots it publishes (slot 0, written raw around the call). Add this witness as a sabotage row: row 7's set taken from NCAPS must be DETECTED. Also note it in the D row 8 cross-reference.

### CONTRACT-2 B+C (and D) blind sabotage S180 and change S179's premise; neither doc lists the mech rows or run_frame_buffer.sh as readers
- status: CONFIRMED (computed from vmbc's own numbers)
- severity: maintenance (a control silently stops detecting)
- effort: M      blast radius: tests/recursion/framebuffer.rxt cells 1-4; tests/mech/sabotages/S179, S180; tests/recursion/run_frame_buffer.sh, fb_mmap_driver.c; match_api §10.2¶4
- where: vmbc "Interaction with D183" item 7 and Standing question 3 (reader list: fb_exact_driver.c, framebuffer.rxt, sr_depth, ts4); altd "What moves" ("the same readers B+C re-pin")
- claim: S180 (the capacities are swapped between the two arrays) is detected ONLY by framebuffer.rxt cells 2 (2048,8192) and 3 (200000,3072), at n=764. Those cells rely on the specimen needing 3,073 trail entries (S180 header: "insufficient transposed (2,048 trail entries against 3,073 needed)"; for cell 3, swapping writes past the 3,072-entry region). After B+C the specimen's trail is "a constant 5 entries" (vmbc Summary). Swapped, cell 2 gets trail 2,048 ≥ 5 and frames 8,192 ≥ 1,528: it matches, so the row is not detected. Swapped, cell 3 gets frames 3,072 ≥ 1,528 and a trail need of 5 inside a 3,072 region: no overflow and no crash, so it is not detected. Cell 3's expectation flips too (gu → match), and its comment "THE TRAIL IS THE ARRAY THAT BINDS" becomes false. S179 still has a detector (cell 4, 512 frames < 763-1,528 needed), but its header numbers are stale. The spec's own justification for requiring both regions, match_api §10.2¶4 ("measured on ^(a(?1)?b)$ the trail binds first at the stamped defaults, so raising only nframes would change nothing"), becomes false and is in no doc's re-pin list. That list covers limits §4¶1-3, §5¶6, match_api §10.1¶1, §10.6¶2-3, tuning §2.11¶2 and the guide.
- evidence / repro: `grep -n 3,073 tests/mech/sabotages/S180_buffers_capacities_swapped.sh` (line 11), S179 line 15; framebuffer.rxt lines 47-63; match_api.md line 3580. Grep for readers: `grep -rln -E '838860|\b763\b|\b764\b|4n ?\+ ?17' tests` also finds run_frame_buffer.sh, fb_mmap_driver.c, sr_gen.py, S179 and S180, which are not all in vmbc's list.
- proposal: add to the landing's reader census the mech sabotage rows (S179, S180), run_frame_buffer.sh, fb_mmap_driver.c and match_api §10.2¶4. Give S180 a NEW witness whose trail still grows per level after B+C+U: per vmbc, a capture kept live inside a possessive loop, which D183 still compacts. Re-validate S179 and S180 with run_sabotage_matrix before landing ([MECH-REACH]). Restate §10.2¶4's justification with that witness, not the specimen.

### CONTRACT-3 D can make a framed artifact frameless; _VM_FRAMELESS / _VM_ENTRY_SHAPE / tuning §2.21¶3 are unnamed readers, and a post-pass breaks their "iff"
- status: CONFIRMED (the artifact class exists today; the move follows from altd's rule)
- severity: doc + design (a stamp would lie if not recomputed)
- effort: M      blast radius: match_api §6.3.8¶10-12, tuning §2.21¶3, the entry-shape selector's input order
- where: altd "Emission" ("One candidate means no push"), "What moves on regeneration" (lists only RX_VM_PROGRAM_BYTES); trailgen row 4 (SETU)
- claim: §6.3.8¶10 says `<PREFIX>_VM_FRAMELESS` is 1 "if and only if the VM program emits no RX_PUSH site and no linked call". `--engine=vm 'a(?:\dx|[a-z]y)c'` stamps FRAMELESS 0, ENTRY_SHAPE "plain", RESUME_FRAMES 2, and its ONLY push is the 2-way alternation (choicepoints: `L2 L6`). Its arms' first bytes are disjoint, so under D row 2 every class has at most 1 candidate and the program has no push. FRAMELESS must then read 1, and the entry rung (eligible for inline/forward, always_inline) and RESUME_FRAMES move. That rung is chosen from `_VM_PROGRAM_BYTES` and framelessness DURING emission. D is designed as a pass over the finished program, so the selection must be re-run after D, or the stamp breaks its iff. Likewise tuning §2.21¶3 makes the forward/shared rungs depend on "no RX_SET ... the trail is real storage even on a frameless artifact". After U, an artifact whose writes are all SETU never touches the trail, so that rule's spelling and the eligibility both need a ruling.
- evidence / repro: review-tree build, `pcrec -p rx --features all --engine=vm --emit-main --pattern 'a(?:\dx|[a-z]y)c'` gives RX_VM_FRAMELESS 0, RX_VM_ENTRY_SHAPE "plain", RX_RESUME_FRAMES 2. `--emit-ir` choicepoints has one row, `L2 L6 branch 1 of 2`.
- proposal: altd adds §6.3.8¶10-12 and tuning §2.21 to its readers. The build order is: D (and SLOT-FLOW verdicts), then framelessness, size and entry-shape selection, then stamps. Add a codegen check that the FRAMELESS iff holds against the final text. trailgen states whether SETU counts as "RX_SET" for §2.21¶3.

### CONTRACT-4 D has no size bound and no size-cap rung; limits §8.4¶4 promises the smallest answer-preserving artifact
- status: CONFIRMED (spec quote vs design text)
- severity: size (a pattern that compiles today can be refused)
- effort: S      blast radius: limits §8.4 table; D's admission table
- where: altd "Artifact size" ("Emitted C ... +9.8 %, +9.1 % ... the emitted code cap must be checked on the census")
- claim: the island, D's sibling, is "bounded against the chain, so the axis never makes a pattern exceed a cap the chain fits" (tuning §2.20¶2). D's admission table has no such row, and the size-cap ladder (limits §8.4, `fit_rungs[]`) has no D rung. limits §8.4¶4 says an over-cap artifact is refused "with the figures of the smallest artifact pcrec could make without changing an answer", and the D-free artifact is smaller. A census only samples; it is not a guarantee.
- proposal: either add a structural admission row (dispatch emitted only where its estimated size ≤ k × the chain's, as the island does), or add a ladder rung "drop-dispatch" (own deny `-fno-…`) before refusal. Add a limits §8.4/§8.5 spec hunk either way.

### CONTRACT-5 No new stamp for D, and no deny/force axis for B/U/C: contrary to D46, tuning §2¶1, and [IFACE-PUSH]'s own rule; the flag-bit budget is not addressed
- status: CONFIRMED (quotes)
- severity: design / doc
- effort: S-M      blast radius: lib/pcrec.h flag bits, axes.def, tuning §2 table, test-axes
- where: altd "Observability: ... No new header stamp now; [IFACE-PUSH] batches stamps"; trailgen review table row 2 "spec cost: none (private)"; no deny flag proposed for B, U or C in vmbc or trailgen
- claim:
  - D46 says every strategy-selection point is OBSERVABLE (a stamp) and FORCEABLE. tuning §2¶1 requires each axis section to state "the stamp it leaves", and every answer-identical row of the §2¶4 table names one (the island: `_VM_ALT_ISLANDS`).
  - plan [IFACE-PUSH] says "a capability/optimization row that needs a new field or stamp adds it the usual way (D76 ritual), not a remodel". The push therefore does NOT batch it.
  - B/U/C select an emitted form per write. Without a deny axis, after landing nothing in-tree can produce the stock form for `make test-axes` or a differential (tuning §1¶7: "a strategy that cannot be denied cannot be differentially tested"). The docs' independent checkers (vmopt_tg.py, altd.py) are scratch twin tools, not in-tree axes.
  - Bits 4-56 are used, bit 57 is the filed [IFACE-PUSH] candidate, and the push's HARD TRIGGER is "<= 4 flag bits remain". D's bit plus deny bits for the write verdicts (and possibly C) reach that trigger, so the build would open [IFACE-PUSH].
  - tuning §1¶2 also requires the D section to state where and in which direction the give-up surface moves. Following the §2.20¶5 precedent: one-way, toward answers.
- proposal: decide explicitly. Either (a) one deny axis for the SLOT-FLOW verdicts and one for D, each with a count stamp (e.g. a dispatched-site count beside `_VM_ALT_ISLANDS`, an untrailed/deleted-write count), knowingly spending bits and tripping the trigger; or (b) a recorded D46 exception with the reason, the way D183 shipped without an axis. Put the choice before Frank, not "batched later".

### CONTRACT-6 `--emit-ir` contract: §1¶4 (rows rendered from the emitting call's own event stream) versus a post-pass; ir_listing.md is named by no doc
- status: CONFIRMED (quotes); severity depends on the build's mechanism
- severity: doc / design
- effort: M      blast radius: docs/spec/ir_listing.md §1¶4, §3.1 summary rows, §3.2 `slots` "written", §3.4 op vocabulary, §3.5
- where: trailgen standing Q3 ("--emit-ir ... must show the verdicts"); vmbc Q3 ("Elided writes must leave the event stream too, or the listing lies"); altd ("--emit-ir roles", note column)
- claim:
  - ir_listing §1¶4's "one absolute constraint": every row is rendered from the VEvent stream "the emitting call itself appended ... never a second description". All three passes run over the FINISHED program. Editing events after the fact, or rendering verdicts from the pass, makes the listing a second description unless the C is re-emitted from the verdict-annotated walk.
  - The op vocabulary (§3.4, append-only) has `set` but no untrailed write and no return-label restore (C), so new ops must be appended there.
  - `slots`' "Written" is derived from VE_SET (§3.2¶1), so B-deleted families change verdict.
  - `summary`'s `trail-entries`, `resume-frames` and `subject-ceiling` move with the stamps.
  - D's roles in `note` carry no promise (§3.1¶1, D26). The island precedent already lists its switch as bare `goto` rows, so that part is not new.
- proposal: name docs/spec/ir_listing.md in the landing's reader list. Specify the mechanism as "analysis on the first walk's events, a second emission walk takes the verdicts as inputs, the listing renders the second walk", which keeps §1¶4 true. Otherwise amend §1¶4. Append the ops (`setu`, `restore`, `dispatch`) to §3.4.

### CONTRACT-7 "Stamps follow the verdicts": the cost model is per AST node, the verdicts are per emitted site; the mapping, and its S87 under-charge direction, is unstated
- status: SUSPECTED
- severity: answer if done wrong (FRAMES on a matchable subject), else design
- effort: M      blast radius: vm_cost*, rx_info.trail_frames/frame_capacity/subject_ceiling, UNROLL_K_WHY "capacity-declined"
- where: trailgen "The cost model" ("run SLOT-FLOW on the emitted program first, then size"); review row 1 "stamped TRAIL_FRAMES shrink"
- claim: `vm_cost` charges per AST node (emit_vm.c around 2760-2900: atomic +1, look +2, call 2*|W|), and one node can emit several SET sites with different verdicts. Examples: replicated bounded repeats, unrolled counters, and C's per-site K_c (one call node, many sites). Sizing "from verdicts" is sound only if a node's charge drops when EVERY emitted site of it is DELETE/UNTRAIL. The alternative is a program-level heaviest-path count, a second description of trail use. S87/S95/S-SR7 guard the under-charge direction. A verdict-aware cost also moves rx_info `subject_ceiling` and the unroll ladder's "capacity-declined" comparison (match_api §6.3.9), both unnamed. The safe option ("leave the charge") is fine, but then the trailgen claims ([ART-TRAIL-ELIDE]'s "FRAMES give-up goes", the shrinking rx_info) do not hold.
- proposal: pick and state one rule. Recommended: a node is charged unless all its sites are uncharged, plus a sabotage that charges a UNTRAIL node's KEEP replica as free, which must be detected. List subject_ceiling and UNROLL_K_WHY among the movers.

### CONTRACT-8 Give-up surface: a ceiling is promised (holds), but the per-change disclosure the spec practises (limits §7) is not planned
- status: CONFIRMED (quotes); low
- severity: doc
- effort: S      blast radius: limits.md §7
- where: altd Soundness "Limits" ("needs a spec check that limits.md and match_api §10 promise a ceiling, not a count")
- claim: the check passes. limits §1¶1-2: a give-up is never a false answer. §3.1¶1: steps are "a robustness bound". §7¶3: "two counters, not an accounting". match_api §10.3¶2: the sufficient count is not reported. D, B, C and U only lower steps, work, frames and trail, so the movement is one-way, toward answers. However, the spec records each emitter change that moves a tuned caller's edge (limits §7¶2 unroll, §7¶4 possessify, each with a stamp to see it). Under the DEFAULT capacities the surface moves too (specimen 763 → 1024 → 2049, framebuffer cell 3). None of the docs plans a §7 paragraph.
- proposal: one limits §7 paragraph covering the SLOT-FLOW verdicts and D: one-way toward answers, steps/frames/trail/work never rise, which stamp shows it (CONTRACT-5).

## PROBED-AND-HELD
- Zero trail capacity on a VM artifact (U removing every trailed site, e.g. bak-2) — held: the sizer floors at 1. Today `--engine=vm 'a(?:b|bc)d'` (no capture SET) stamps TRAIL_FRAMES 1, and `(a)b` and bak-2 stamp 1/3 and 1/7. So match_api §10.4¶4's "0 means no buffers" (DFA-only) is not hit. A build must keep the floor (the run struct's `trail[RX_TRAIL_FRAMES]` array).
- Callout fire suppression by D — held: altd row 8 makes any continuation reaching a site before its first byte OPAQUE. Fire count is unspecified (§11.6¶1) and D never adds fires, so §11.8's classes hold. The NCAPS trap of CONTRACT-1 does not apply to D (it is a control rule, not a slot rule).
- The callout view under U/C with default captures — held by argument: the view is a live pointer into slot_values (`rx_co_ctx.caps = slot_values`). With row 7 reading 0..2*ncap-1, a stale value would be a live read, so the slot stays trailed. The only gap is CONTRACT-1's read-set definition.
- Step/work monotonicity under D — held: a dropped continuation costs ≥1 resume in stock, and the dispatch is uncharged. Fewer frames means fewer frames discarded at cuts (work). This matches the island's one-way §2.20¶5 precedent.
- Tiered default (§10.9) — held: B/C/D/U/R change neither the escalation rule nor the per-call budget refill. FAST_* follow the frame/trail SIZES, which none of the three changes (P, packed entries, is filed separately and would move them).
- Frame high-water / page-fault claims vs a memory contract — held: §10.3¶4 leaves buffer contents unspecified, no spec promises a touch pattern, and §10.6's RSS table is already in the re-pin list (§10.6¶2-3).
- `-fno-first-byte-dispatch` under D174 — weak, not filed: it names a mechanism a regex user can read, and the shipped neighbours (`-fno-alt-island`, `-fno-splice-calls`) are the same style. A behaviour name (e.g. skipping branches that cannot start here) would fit D174 better; that is Frank's naming call, folded into CONTRACT-5.
- R's "spec cost none" vs limits §5¶2-3 stack numbers — not verifiable without a build. test-stackdepth asserts only < 4096 B for the entry, and the numbers are prose. Flag for the stage-0 card: re-measure §5¶2/¶3/¶6 and match_api §10.9¶10.
- Gaps (denylist): the twins' evidence dirs were not read; the claims above use only the reports, the spec and review-tree probes (12 compiles).
