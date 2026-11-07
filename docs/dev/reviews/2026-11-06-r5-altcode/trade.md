# trade findings — altcode
STATE: done
## Findings

### TRD-1: the island->chain flip is not "near the knee" and not off the corpus; it costs ~2.6x matcher work at DEFAULT flags
- status: CONFIRMED. repro (SUBJECT=S build, BASE=B build, utf8, `--engine=vm`, NO other flag):
  `x(?:é|à|q2|r3)y`, `x(?:[éà]|q2|r3)y`, `x(?:[éà]|qq|rr)y`, `x(?:[éà]|foo|bar|baz)y`: RX_VM_ALT_ISLANDS 1 (B) -> 0 (S); `-fno-altcls-merge` restores 1. Emitted C GROWS (23907 -> 25461 B on the first). Instruction count (`taskset -c 7 perf stat -e instructions:u`, --emit-main, gcc -O1, 4804-byte subject of `abcdefq1xrr2xéq`*300+`xr3y`): B 168,639, S 250,069; minus the 118.8k process baseline, 49.8k -> 131.3k (2.6x) matching work. Same-subject reruns repeat to +-2.
  Counter-cases that held: `x(?:[éà]|foo|bar)y`, `(?:[éà]|cat|dog)s`, `x(?:[я]|cat|dog)y` keep the island 1 -> 1.
- severity: speed
- effort: M (narrow the island-admission or the knee test to read the UNMERGED chain size, or exempt a class inside an enclosing island); blast radius: every utf8 VM alternation mixing a 2-box wide class (accented letters) with literals, 3-4 branches wide
- where: design §4.4 ERRATUM (alt_normal_form.md ~1070-1079), §5 stage 1 U4; emit_vm.c knee `isl_bytes > chain_bytes * VM_ISL_SIZE_FACTOR`
- argument: the ERRATUM calls it "near the size knee" and "no corpus or bench pattern is in it". The probes are tiny patterns (23-25 KB programs), the flip is on a 3-branch mix, nothing near an absolute size cap. Judge: the design text itself (ERRATUM) cites "manager rulings R1/R2" in a lane file (denied to this critic), and commit 866668a4f's own subject line calls the knee evidence "a clear loss: STOP". D186 (eeff8964 decisions.md): a choice change "that cannot be made loss-free is an explicit EXCEPTION the owner approves ... never a side effect"; a losing regime "narrows the row's condition". The branch ships an accepted loss judged by manager rulings, not an owner exception, and the "narrow the row" remedy was not taken. Ruling gap, unless R1/R2 contains an owner approval the design does not cite. Also the spec: tuning §2.20 says the set reading admits "exactly as before" and §2.6¶2 mentions only the BARE-class island restoration; neither says that a class INSIDE an enclosing alternation can lose its island to the knee. Abi changelog entry likewise says only "a bare wide class's own VM island gone".

### TRD-2: abi 96 changelog says "every byte artifact moves only the number"; at SUBJECT it is false (stage 2b, K139)
- status: CONFIRMED. repro: `build/pcrec -p rx --engine=vm -o x.c --pattern '(?:ab|ba|aa|bb){24}c'` (byte): B 29,839 B, RX_VM_ALT_ISLANDS 8, ALTCLS_MERGES 0; S 18,606 B, ISLANDS 0, ALTCLS_MERGES 1. `x(?:ab|ba|aa|bb)y` vm: B ISLANDS 1 / 18,990 B; S ISLANDS 0 / 18,147 B. Auto engine also moves (27,953 -> 24,960 and 10,809 -> 11,580 B). The drop-islands row additionally changes byte VM artifacts that used to be refused.
- severity: doc (abi ritual D76/D94); effort S; blast radius: anyone reading the changelog or the 96-pin to know what moved; (B) gate reasoning
- where: docs/dev/history/abi_changelog.md (diff hunk "Every other artifact, every `byte` artifact included, moves only the number. No answer moves.")
- argument: the entry was written at stage 1 and not revised after 2b/K139 landed on the same abi number. D94: the site list is every reader of the number; the prose is one. Speed here is a GAIN in the measured case (`(?:ab|ba|aa|bb){24}c` over `abbaabba`*500: 3.15M -> 1.88M instructions, B vs S, 118.8k baseline), so the trade is good but unrecorded.

### TRD-3: -fno-cls-kit refusal entry + floor 60 deleted; tuning §2.33¶7 still promises `make test-axes` records it, and the "-fno-cls-kit -fno-altcls-merge restores the refusals" claim is untested
- status: CONFIRMED (the claim is true when run; its record is gone). repro: `\p{Xwd}`, `\P{Unknown}`, `\p{L}+` `-e utf8 --engine=vm -fno-cls-kit`: B refused (608,075 / 556,412 / 888,054 code bytes vs 500,000); S compiles (305,269 / 286,492 / 460,052 B C); `-fno-cls-kit -fno-altcls-merge` on S refuses again (608,021 / 556,358 / 887,946). grep of tests/ for the deny pair as a combination: 0 hits (only a comment in run_axes.sh:616).
- severity: maintenance (coverage); effort S (an axes entry for the pair, or amend §2.33¶7); blast radius: the axis' documented limit
- where: tests/axes/run_axes.sh:605-616; docs/spec/tuning.md §2.33¶7 (still ends "`make test-axes` records the refusal as this axis's documented limit")
- argument: given up = a K35 floor of 60 refusals on a real population (104 refusal lines per the deleted comment). Judge: the design FIX-3 row ("only FEWER refusals") and the K55 precedent cited in the comment; those cover deleting a vacuous entry, which is sound. What nobody judged is the spec sentence, now false, and the lost sabotage of "the merge is what keeps wide classes under the cap": nothing fails if rule M's lowering call silently stops merging at big classes EXCEPT the N5 box-count pins (\p{Lu}=67, \p{Nd}=39, \p{L}=330, .=8), which test box counts, not the cap. N5 is a fixed UCD 16.0.0 pin (a UCD bump re-pins by hand, stated in the test).

### TRD-4: K139 retry roughly doubles compile cost for EVERY size-refused island-bearing VM compile, including the ones refused anyway; K139 reports only the "retried and fit" case
- status: CONFIRMED. repro (`--engine=vm`, `perf stat -e instructions:u -x,`, compile only): 1000 random 8-letter words `(?:...)Z`: B refuses, 244.8M; S ships chain + note, 490.1M; S `-fno-alt-island` direct 235.9M (2.08x the direct). 3000 words (refused by every build): B 699.5M, S 1373.5M, S `-fno-alt-island` 642.0M (S pays 2.14x its own deny, 1.96x base) and the refusal message now quotes the chain figure (1,257,724 vs base's 1,474,628), not the island's.
- severity: speed (compile time) ; effort S-M (the row is `applies` on `job->vm_islands` only; a cheap pre-check would skip hopeless cases); blast radius: callers who hit the size cap on the VM with any alternation island; bounded: `.repeat = FIT_REP_ONCE`, COMPILE_MAX_ATTEMPTS grows by one ladder run (5*(N+1) + 1), so at most one extra attempt
- where: src/core/compile.c `drop-islands` row; docs/dev/known_issues.md K139 ("~1.6-2x the direct")
- argument: who pays = the compile of an over-cap pattern, in exchange for acceptance (a real gain: patterns base refuses now compile). Bounded yes; K139 states 1.6-2x only for the rescued case, not that a hopeless refusal now costs ~2x base (and `--size-cap=refuse` / refuse-after-failed-rescue). Judge: manager ruling R4 (lane file, denied); the spec text (limits.md §8.4¶2c) states the rung but no cost. The comment in compile.c says the in-emitter guard stays as a shortcut; no measure of how often it saves the attempt.

### TRD-5: PCREC_MAX_REQ_PIECES=10 sits exactly on the observed peak; the census is not reproducible from the tree; design says "collapse", code drops
- status: CONFIRMED for the facts; SUSPECTED for the census (cannot re-run, forbidden; its output file is under the denied lane evidence dir).
  repro: `(?:` + words of lengths 4..(4+n-1) `)` `--emit-facts`: n=10 -> req_pieces derived; n=11 and 12 -> `declined ... decline:over-bound`. bench altwide patterns (grepped, read-only): distinct word-length counts per group 4,7,9,10 only, 27 groups at exactly 10; so the limit equals the bench peak with zero headroom (a bench list of widths 4-14 falls off).
- severity: design (low today: `req_pieces` is inert, `facts.h` says "no reader"; run is derived as before); effort S
- where: src/core/limits.def PCREC_MAX_REQ_PIECES; src/facts/desc.c:103; design §3.4 "Bound"
- argument: given up above 10 = the entire description for the subtree (PD_OVER drops it; nothing collapses), whereas §3.4 says "Over the bound a subtree's groups collapse to today's common head/tail". Code and design disagree; the code is the sound-but-weaker reading. PCREC_MAX_ALTNF_WORK rounds the measured peak up a power of ten; this one takes the peak itself. Judge: design §3.4 Bound + r4 RDY-6a ("measured, never presumed") cover the method, not a bound at the peak. When the first reader lands, the bound becomes a coverage cliff for bench-style keyword lists wider than 10 distinct lengths. Note: sticky: one over-bound child drops every ancestor's description (desc.c:124).

### TRD-6: bare wide class island losses (stage 1) are real, default-off but by-design; judge is design r7 RDY-1, which itself defers to a "choice cell"
- status: CONFIRMED. repro `-e utf8 --engine=vm -fno-cls-kit`: `a[éÉ]b` ISLANDS 1 -> 0; `(?i)aéb` 1 -> 0 (24,510 -> 24,347 B); `(?i)xé+y` 2 -> 0 and RX_VM_RUNGS 0x4u -> 0x1u (25,384 -> 23,712 B). At default flags (kit on) these already had 0 islands in B, so the loss exists only on the `-fno-cls-kit` axis; the cost lands on users of that deny.
- severity: speed (axis-scoped)
- effort S (none needed unless the axis matters); blast radius: `-fno-cls-kit` users only
- where: design §4.4 RDY-1 text, tuning §2.6¶2 (documents the restoration)
- argument: this one IS covered: design names it, spec §2.6¶2 documents it, `-fno-altcls-merge` restores it (S1882/S1883 and N4 pin it). The rung flip 0x4u -> 0x1u is the "cursor rung" the design calls a strict improvement; program shrinks ~7%. Not a finding against it. Included for completeness; the cost is bounded by an axis nobody ships by default.

### TRD-7: recursion identity (B) FILEPIN is the stage-1 commit; later src commits (2p, 2b, K139) are not covered by it
- status: SUSPECTED. FILEPIN=`e3df76804` (stage 1). `git log e3df76804..SUBJECT -- src` lists e318a18f1 (2b owner), 4e6e0a4fe (2p), 06db77410, cfd28cf38 (K139). Artifacts moved by 2b/K139 (TRD-2 above) are not byte-identical to a stage-1 reference, so (B)'s "differing" count at SUBJECT should be non-zero on those patterns unless the gate declares them. What would confirm: run tests/codegen/run_recursion_identity.sh at SUBJECT (forbidden here) or build e3df76804 and compile the TRD-2 patterns for a diff. The self-pin comment says "re-pinned per later stage"; no later re-pin is in the diff.
- severity: maintenance; effort S; blast radius: the (B) gate at landing; the manager re-pins to the landing merge (convention), so cost is a re-pin
- where: tests/codegen/run_recursion_identity.sh (FILEPIN line, [RUN-POS-SET] SELF-PIN paragraph)
- argument: a pin moved without recording which emitted-byte movers it absorbs is the pin-without-judge shape; the island manifest swap `(?:ab|ba|aa|bb){24}c` -> `(?:ab|cd|aqr|cst){8}z` (also run_size_term.sh pool member, counterk.rxt) is the same: replaced because the old member "stamped no island" after the merge. Old shape: no longer exercises the pool's "island merged away" case (TRD-2 pattern shows the merged form is FASTER); new shape still has 8 islands and identical B/S bytes (32,578 B both), so it is a sound reference. The old pattern is retained in counterk.rxt as an answer witness. Judge: lane altbuild2 "ruling R4 (a)" (manager, denied file). Covered by a ruling the critic cannot read; the replacement itself held.

### TRD-8: "U2/U4 census floors (run_wclass_census.sh)" not found in the diff
- status: SUSPECTED. The diff of run_wclass_census.sh adds PART 4 [N1]-[N5] only (pins: island counts, \p{Lu}=67, \p{Nd}=39, \p{L}=330, .=8); no floor numbers named U2/U4. Commit 866668a4f's subject says "U4 census floor + refusal-retired class", but those live outside the non-denied diff (lane/evidence dirs). Cannot judge a floor I cannot see.
- severity: doc; effort S

## PROBED-AND-HELD
- Stage-1 island census claims: `x(?:[éà]1|q2|r3)y` and `x(?:1[éè]|q2|r3)y` equality 1->1, 0->0 at default and -fno-cls-kit (4 compiles) held.
- Rule-M/size trade on `(?:ab|ba|aa|bb){24}c`: S faster (1.9M vs 3.2M instr over the base-subject), answers equal in the one subject run (`match 3952 4001` both).
- drop-islands row bounded: `FIT_REP_ONCE`, attempt cap raised by exactly one ladder run and one; artifact equals `-fno-alt-island`'s (the S-off 1000-word compile reports 446177 vs 446174 C bytes: only the stamp differs, consistent with §8.5¶1b).
- tuning §2.6/§2.7/§2.20, limits §8.4 rows 2b / ¶2c / ¶3 ("all ten") read against the table: consistent.
- limits_check manifest count 78 -> 80 matches the two added rows.
- Compiles used: ~75 (budget 1,500).

## Notes
- Denied files (lane reports, rulings R1/R2/R4, evidence TSVs) were not opened; every "judge: ruling R*" above is the design/comments' pointer only.
- Census scripts, make, suites not run (COMMON). p2_census / U4 census figures not re-measured.
- No PLANT-REQUEST needed. For TRD-7 a one-off build of e3df76804 would settle it.
