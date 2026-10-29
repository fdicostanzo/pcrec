# Full-suite ledger (D177)

The record behind D177's schedule: what has landed since the last green full suite, and every full-suite
run with its retained verdict. The full suite is `scripts/battery.sh` (stages test, strict, axes, san,
alloc, lint, mech, recidentity), queued by `scripts/fullsuite_job.sh`. The manager adds a line here at each
landing and checks D177's triggers; a run's summary line (`LOGDIR/summary.txt`) is copied into "Runs" by
the manager (the job never commits). When a run reads green, the counters below reset: move the listed
landings under "Covered by run <date> <sha>" in the Runs section's notes and start the list afresh.

Line format: `date commit class — why`. Class: `major` (new capability, abi event, refactor of a shared
mechanism, new engine path), `minor` (a fix, a re-pin, a code or check change that is not major), `none`
(no change under src/ cli/ lib/ memfn/src/ tests/ scripts/ Makefile or data stores: docs, design notes,
studies; listed, not counted).

## Since the last green full suite

Baseline: the last full run on record is about 2026-10-08 (docs/dev/gate_census_2026-10-23.md: full mech
~10-08, san 10-03, alloc 10-08, axes 10-20 only); no battery verdict is retained from it.

**major: 31, minor: 84** (plus 107 no-code landings, not counted). Seeded 2026-10-23 from
`git log --first-parent --merges --since=2026-10-08 main` (merges named "merge main into" excluded).
PROVISIONAL: class is set by a mechanical rule (path touched, abi-event wording in the merge subject,
a short capability keyword list); manager to confirm. Landings dated 2026-10-08 may predate the
last run.

Trigger state (D177): rows 1, 4 and 5 are FIRED (tonight's run; far past 2-3 major and 4-6 minor);
row 3 fires if the manager classes any of the majors below as a refactor (corefix, dd10b, attrtab, rpunion
are candidates); row 2 not applicable until a major version shift is named. Next window: the first run,
after the iterator landing.

### major

- 2026-10-29 ebcc10aa1 major — merge lane/trailgc: [K134] VM trail compaction at checkpoints (D183; backward gotos + region returns, quarter-room stop, fast tier never compacts), abi 92 -> 93 (VM artifacts whose program writes the trail on a cycle gain the checkpoints and `trail_gc_floor`; every other artifact moves in the abi digits only). Validated on the branch: job 690 run 2 red ONLY on identity (A) = the filed [RECID-A] (make test 81/81 green, (B) zero-diff, trail-stripped regions = base on 4,983 patterns), 691 mech GREEN; the landing re-ran codegen/registry/rxtsource/identity (see trailgc3_report.md "Landing 2026-10-29 (landtgc)"). Owed: tonight's full suite.
- 2026-10-29 b156d8f18 major — merge lane/ic3: [INLINE-C] stage 3 (sha-pinned include/lib lines, every-chain rule, definition-site view, lib code-headers, `--include-block`, `--list-callouts`, F27, F38; no abi bump, main stays 92). Validated on the branch: 680-ic3-test GREEN (1519 s), 681-ic3-mech GREEN (5/5 rows); post-merge check queued as 696-landic3-check. D177 triggers: rows 1, 4, 5 already FIRED (counts only grow); row 3 not claimed (a capability, not a refactor).
- 2026-10-29 0f425c2d0 major — merge lane/memfn-s3m (+ lane/memfn-r30 notes 4a32fc474): kit D172 S3 (cover LOCATE row routed by default, D-hors), abi 91 -> 92 (artifacts it does not take move in the abi digits only); recursion-identity (B) FILEPIN re-pinned; [SWEEP-COMP-FLOOR] floor 100 -> 86. Validated: kit job 622 20/21 green (the one red = that floor); lands3 identity gate + test-codegen/registry/rxtsource per its report.
- 2026-10-29 02229045e major — merge lane/reqvm1m: [REQRUN-VM] required-run handoff and re-entry widened to VM consumers (VM-only attempt loop, VM-hybrid prefilter re-entry) + the drop-handoff fit rung; abi 90 -> 91 (emitted text moved). Validated: 660-reqvm1m-test GREEN (build, strict, mover census 0 unexpected vs 78627dbca@abi90, make test 81/81).
- 2026-10-28 c6707bb5a major — merge lane/ic2fix: [INLINE-C] stage 2 (tagged (?C`c: ...`), `--allow-code=c`, span helpers) + review 2026-10-27 r1 ic2 FIX-NOW fixes; abi 89 -> 90 (emitted text moved in callout/embedded-code artifacts). Validated: 640 test GREEN + strict GREEN, mover census rows=221 unexpected=0, 641 mech GREEN, 642 axes GREEN (14,448 s).
- 2026-10-28 c2f0344db none — merge lane/vartmp: temp files under /var/tmp/pcrec-<user> (PCREC_TMPDIR), prune at queue job start (Frank 2026-10-28; scripts/docs only)
- 2026-10-27 719a17ccb major — merge lane/ic1b: [INLINE-C] stage 1b, the callout call site (module callouts, `--callout`, firing classes, `once` reading-rule refusals with fix verdicts; abi 89). Validated: 563 test2 GREEN (80/80, movers 0/32,775), 561 mech GREEN (39 rows), 564 axes2 GREEN (13,654 s, batched shape).
- 2026-10-26 7234c2e86 major — merge lane/emitbidi: [EMIT-BIDI] one C-text escaper, emitted text ASCII-only, abi 86 (abi event: emitted text moves on every -fcomments artifact; job 800 green: strict, test-codegen, AXES=-fcomments, mech S1620-S1622, make test)
- 2026-10-25 415eade4d none — merge lane/benchres: [BENCH-RESERVE] bench reservations (scripts only)
- 2026-10-25 4dd8af50b none — merge lane/suiteresume: [SUITE-RESUME] owner-commanded resume of a red full suite (scripts only)
- 2026-10-25 82abd6b87 none — merge lane/queuemon: [MON-SCRIPT] script-only box-queue monitor (scripts + hook only)
- 2026-10-25 7592e1397 none — merge lane/hookguards: [HOOK-GUARDS] no_commit_all + lane_writes_in_worktree hooks (scripts/hooks + settings only)
- 2026-10-24 9ae59f5d4 major — merge lane/substland: [M4-SUBST] compiled substitution (job 623 make test green 79/79)
- 2026-10-24 731228fb2 major — merge lane/upropb: [UPROP-MORE] B, 55 binary properties, bc=, Block/Age
- 2026-10-23 b8c66a739 major — merge lane/iterland: find-all iterators, abi 84
- 2026-10-21 813f43ec8 major — Merge lane/m0build: [MEASURE-SET] M0, the measures kind + <PREFIX>_MEASURES / rx_info.measures, abi 81 -> 82 (
- 2026-10-20 73c2bb655 major — Merge lane/ctxp2d: P2d (\A/\z at the NFA layer), zero movers, abi 81
- 2026-10-20 d06b530f7 major — Merge lane/ctxbuild: [DD-11.5] P2a-P2c, (?m)^/(?m)$ into A_CTX, abi 80 -> 81 (heavy validation green)
- 2026-10-18 7c0a90479 major — Merge lane/e1: [ENTRY-TABLE] E1, the part-layout controls (abi 80; review r1 fixes)
- 2026-10-17 168a399c7 major — Merge lane/ksrc23: [KNOW-SRC] K2+K3 (ksgen, canonical/decoded views, analyze --dump-doc, test-knowledge R1-R3/
- 2026-10-17 a997a97ce major — Merge lane/int5: E-1 analysis object ([WINDOW-E1]) + kit R-24 (mf_prov bytes/fidelity, MF_SITE_ABI 15) + wirin
- 2026-10-13 206cf0a0b major — Merge branch 'lane/b3tri' ([OPT-REVEND] B3: match-end mark on rev-end, abi 78; b3land landing; b3tri instrumen
- 2026-10-13 e842fe537 major — Merge branch 'lane/cpb4' ([COMPOUND] B4, abi 76 -> 77)
- 2026-10-12 2a54c3e71 major — Merge branch 'lane/cpb02' ([COMPOUND] B0-B2: entry table, part mode, derive; zero movers)
- 2026-10-12 4cd82e8de major — Merge lane/seamtri (lane/seambuild + fold-check fix): [LOSS-REVIEW] candidate 1, seam helpers static inline; a
- 2026-10-11 00c97769e major — Merge branch 'lane/rlhbuild' ([REQ-HANDOFF-L1], abi 74 -> 75)
- 2026-10-10 67f59d244 major — Merge lane/flagacc: [FLAG-ACCESS] one accessor block for every option-word read + reader-census gate (S792); N
- 2026-10-10 b8337c33b major — Merge lane/sltri (contains lane/slbuild): [START-LANDING] SL1-SL4, abi 74, bits 53/54
- 2026-10-10 7388f1c0d major — Merge lane/revfloor: [OPT-REVEND] L1 + L2 with stage 2 (revbuild, abi 73) + triage fixes (revtri) + census flo
- 2026-10-10 a15fb77bc major — Merge lane/memfn-vmlazy: [MEMFN] R-12 VMLAZY (abi 72; slot19 clean)
- 2026-10-09 631771b7f major — Merge lane/rq3 (0890ed9b): memfn RQ-3 landing, abi 71
- 2026-10-09 82ff94323 major — Merge lane/memfn-r4e0b: [MEMFN] R-11 step R4e′.0b, SIMD-off routed through <fn>__body, abi 69 -> 70 (+139..+18
- 2026-10-09 32a1c91f0 major — Merge lane/decattr: [DEC-VAR-ATTRIB] + [DEC-COLLAPSE-WASTE], abi 68 -> 69 (declared movers: ENGINE_SEL on 9 nu
- 2026-10-09 131c173a8 major — Merge lane/memfn-r4e0: [MEMFN] R-11 step R4e′.0 (fn_rows[] BODY/PREFIX seam, one kit walk; zero movers, no abi
- 2026-10-09 09ce1b366 major — Merge lane/decfbB7: [DEC-FALLBACK] B7, the declared listing commit (--list-axes exactly as declared, 0 artifac
- 2026-10-08 7c5bef635 major — Merge lane/decfbB6: [DEC-FALLBACK] B6, the fallback listings project the tables (--list-axes byte-identical; m
- 2026-10-08 6e7fc41e5 major — Merge lane/memfn-m7: [MEMFN] R-8 / M7 (zero movers, no abi event; slot12+slot13 green: census, identity gate 7
- 2026-10-08 399eb53fb major — Merge lane/decfbB5: [DEC-FALLBACK] B5, the token derivations read the tables (no movers; light + heavy green, 
- 2026-10-08 ceff04211 major — Merge lane/decfbB4: [DEC-FALLBACK] B4, T2 replaces the prefilter admission (no movers; light + heavy green, me

- 2026-10-26 93ef76746 major — [INLINE-C] stage 1a: the per-kind attribute row kindrow.def read by 8 pass sites (refactor of a shared mechanism; 0 movers over 6,185 corpus artifacts; removes an A_VAR union misread in pcrec_bref_mark)
- 2026-10-26 456dbc09e major — [SCANEDGE-SET] scan edges over a byte-class set (abi 87; lane scanset + scansetfix)
### minor

- 2026-10-29 0a6ca838d minor — merge lane/ic2d27m: [INLINE-C] stage 2 D27 spec-first suite (tests/code/d27, test arm 12, sabotage S1740-S1741) + two small CLI diagnostic fixes; no abi event (stays 91). Validated: 665-ic2d27m-test GREEN (strict 0, make test 81/81); landing build, strict, test-codegen GREEN with no re-pin.
- 2026-10-26 81454bbf4 minor — [INLINE-C] stage 0: shared-block call-site comment "traps on" -> "propagates" (abi 88; size pin +2 B re-recorded)
- 2026-10-24 f50d6372e minor — merge lane/qwquiet2: queuewatch QUIET/PENDING-STUCK
- 2026-10-24 91670a624 minor — merge lane/lockyield: boxlock waits for ready queue jobs
- 2026-10-24 b11b69add minor — merge lane/qwstart: queuewatch JOB-START once per real run
- 2026-10-24 187608482 minor — merge lane/flagfix: [FLAG-SPELL] empty-node removal in concatenations
- 2026-10-23 2c33a6515 minor — merge lane/casespell: case-spelling identity check in test-codegen (Frank's ask; no case leak on main)
- 2026-10-23 5c9bde73b minor — merge lane/recpin: recursion-identity (B) FILEPIN re-pinned to the corefix merge (abi 83); (A) left red pendin
- 2026-10-22 c4164f15b minor — Merge lane/memfn-ws: kit R-29 (D172 S2), MF_SITE_ABI 20, 586 green
- 2026-10-22 bf33d2dab minor — Merge lane/corefix: K128 (capture after empty repeat iteration), K129 (unset vars missed by _search), vm_count
- 2026-10-22 5db8c4c6a minor — Merge lane/substcase: simple case-map table (ucd-16.0.0 4th output) + case-map oracle check vs libpcre2 10.46 
- 2026-10-22 a623ced02 minor — Merge lane/memfn-r28: kit R-28 stack-frame trim
- 2026-10-22 ce54c42de minor — Merge lane/dd10b: [DD-10] stack depth
- 2026-10-22 3e8989e85 minor — Merge lane/vrepin: re-pinned lowered-cap variant floors (cause M0 stamps 813f43ec8; 715 green)
- 2026-10-22 cbb22bcc1 minor — Merge lane/hotpath: 4 KB limit row for hot-path CLAUDE.md (docs, docs/dev, docs/dev/lanes, scripts); text to N
- 2026-10-22 faa656ff3 minor — Merge lane/claudecap: CLAUDE.md is orientation only (12 KB / root 20 KB check, pre-commit + test-claudemd-size
- 2026-10-22 70cf1b9ef minor — Merge lane/ctxfix: no_stale_claudemd hook (32 KB), tests/harness CLAUDE.md de-bulk, 6 worktrees pruned
- 2026-10-22 19be546b1 minor — Merge lane/langfix2: pattern-language spec + language fixes (K115-K118, K122-K127)
- 2026-10-21 5893e47dc minor — Merge lane/memfn-b4scope: kit B4' (walk default lockdown; R0/R5/R7 withdrawn; MF_SITE_ABI 19; no pcrec abi eve
- 2026-10-21 6a0ad4029 minor — Merge lane/k113: K113 compound parts inherit the walk's analysis chain and object
- 2026-10-21 4c9c19e7b minor — Merge lane/stfix: sectiontimes reads/writes bytes so a non-UTF-8 byte can no longer kill make (610 truncation)
- 2026-10-21 65ae3041c minor — Merge lane/debulka: src/ cli/ lib/ memfn/ scripts/ tools/ docs/ CLAUDE.md files over 200 lines become short in
- 2026-10-21 a2e4b990c minor — Merge lane/debulkb: tests/ and studies/ CLAUDE.md files over 200 lines become short indexes (21,267 -> 1,981 l
- 2026-10-21 aeb381c25 minor — Merge lane/z2build: [KIT-VERIFY] U1 Z2, pcrec's producer, cover row and emitter, routed ONLY through the harne
- 2026-10-21 6a4b90dbd minor — Merge lane/runnerfix: boxqueue runner logs every skipped job with a reason; re-execs itself between jobs when 
- 2026-10-21 83ff3efad minor — Merge lane/partmeas: compound parts inherit the parent's RESOLVED measure set (PcrecEmitIn.meas); MEASURES uni
- 2026-10-21 f99b335f3 minor — Merge lane/watchidle: [WATCH-IDLE] queue honesty checks (shapes 1-3) + the idle-box alarm (IDLE-SUSPECT, never
- 2026-10-21 1f277f27f minor — Merge lane/memfn-setdig: kit interim-set digests fixed (all five kit sets load under measures.md; kit-syntheti
- 2026-10-21 c7c4ce015 minor — Merge lane/memfn-b4prep: B4 pre-brief items closed (manifest of record at abi 82: 1,766 movers, lost 0; trace-
- 2026-10-21 ec10382cf minor — Merge lane/memfn-r26 @ 838c6f51e: kit R-26.6 Zk (REPORT row UNROUTED, mf_preview; no pcrec file, no abi or MF_
- 2026-10-21 5cc3d7179 minor — Merge lane/memfn-r26 @ 6ff4ea64b: kit R-26 Z1 (R-26.1-R-26.5; MF_SITE_ABI 17->18, no pcrec abi event, 0 movers
- 2026-10-21 a9e10b53c minor — Merge lane/reachonly: [MECH-REACHONLY] REACH_ONLY=1 sweep (847 rows, 0 undeclared unreached, 89 s)
- 2026-10-21 f2dae53f9 minor — Merge lane/adm1021: F-3 registry ^ text (A_CTX pin row), [MECH-REACHONLY] + [RECUR-AUDIT] filed
- 2026-10-21 ee183c004 minor — Merge branch 'lane/ctxp2e'
- 2026-10-21 b42c0e8f1 minor — Merge lane/boxqueue: [BOXQUEUE] the box-wide job queue (scripts/boxqueue), TOOL: DONE completion convention
- 2026-10-20 20e0fe126 minor — Merge lane/cifix: test-lookaround population pins re-pinned for 2619ced1b's three multiline blocks (CI 3948422
- 2026-10-20 8b89477df minor — Merge lane/memfn-r25: kit R-25, proven0/proven_prev honour need (heavy slot at d49ff5515: 0 movers every arm, 
- 2026-10-20 e294c1a62 minor — Merge lane/hooks: light pre-push gate (installed), no-cd PreToolUse hook (project settings), box lock on sanit
- 2026-10-20 a0c2ec9c4 minor — Merge lane/runkit: boxlock + chainrun + watchrun + verdict, one tool family with self-tests; heavy entry point
- 2026-10-18 5e1333b40 minor — Merge lane/memfn-pinfix: emit_sweep --arms start back to rc 0 (a.{1,5}z joins presence_deny.rxt; pins re-deriv
- 2026-10-18 fe3eb5c86 minor — Merge lane/memfn-rowfix: S689/S1085 restored; n2_census floors read by field
- 2026-10-18 d18cee085 minor — Merge lane/memfn-b3b: kit R17-b' B3b
- 2026-10-18 be008236f minor — Merge lane/spechook: conditional spec checks in the opt-in pre-commit hook (staged content)
- 2026-10-18 18e1421b8 minor — Merge lane/wtpforce: wtprune --force for named dirty/unmerged/nested worktrees (friendly first, never rm -rf)
- 2026-10-18 7d3587441 minor — Merge lane/attrtab: [ATTR-TABLE] one guarded attribute-text table for the four GNU-attribute writers (zero mov
- 2026-10-18 82e48e806 minor — Merge lane/b3afix: R17-b' B3a (req_start_set one source, DELEG_SITE entry column, c17 use points, c10_presence
- 2026-10-17 1c06b8a0c minor — Merge lane/rpunion: RP (one render point after mf_art_end) + knowledge stamp = union over attempts (abi 79, D1
- 2026-10-17 d1a1fdf4b minor — Merge lane/lmfacts: landmark admission input as facts, one price source (proven0), memfn_sites.h D157 comment
- 2026-10-17 e71a5d256 minor — Merge lane/c1017: C10 one-byte fixtures by kind + C17 live site_kind rule (S1091)
- 2026-10-17 3f04dff85 minor — Merge lane/memfn-r23: memfn R-23 (mf_site.body a stated fact, MF_SITE_ABI 14)
- 2026-10-17 0ec28bddd minor — Merge lane/int4: memfn R17-b' B1+B2 (R-22/R-MS6) + main's review fixes
- 2026-10-16 6ca1589e6 minor — Merge lane/int3: e0c + ksrc + kit B0 (10d9f43f4) integration
- 2026-10-16 61c92ed22 minor — Merge branch 'lane/e0sw'
- 2026-10-13 ddfac0b93 minor — Merge branch 'lane/restri' (re-pin test-resource's a{5,25000} rescue size: +27 B from B4's RX_COMPOUND stamp)
- 2026-10-13 e34bcbeb4 minor — Merge branch 'lane/cishard3' (re-pin test-rxtsource census after s157tri's quantified.rxt cells)
- 2026-10-13 be9b255e5 minor — Merge branch 'lane/cishard2' (shard rebalance from runner seconds; SHARD -> CISHARD: make's exported SHARD col
- 2026-10-13 e656dfa56 minor — Merge branch 'lane/s636tri' (S636 detection gap since OPT-REVEND L2: sdr fstate cells + default-path seq-anchl
- 2026-10-13 f3aecbe71 minor — Merge branch 'lane/mechwit' (9 unreached mech rows get default-path witnesses: START-LANDING/OPT-REVEND moved 
- 2026-10-13 df5bf9750 minor — Merge branch 'lane/s157tri' (S157 detection gap since k93fix: uncalled-group a? witnesses)
- 2026-10-13 d67e07507 minor — Merge branch 'lane/cishard' (CI make test as a 3-shard matrix from a declared table; per-section timings uploa
- 2026-10-13 657d4fd0f minor — Merge branch 'lane/citri' (CI red since 2026-10-10: gcc 13 maybe-uninitialized in rxt_source.c row_check)
- 2026-10-12 6177d1189 minor — Merge branch 'lane/planlint' ([PLAN-LINT] step 3: format A rows, strict plan linter, opt-in pre-commit hook)
- 2026-10-12 e8ae2e4f4 minor — Merge branch 'lane/plclean' ([PLAN-LINT] step 2: plan.md cleanup)
- 2026-10-12 e1a6c9dc9 minor — Merge branch 'lane/k110fix' (K110: RX_ENGINE_WHY source offsets)
- 2026-10-12 fad634534 minor — Merge branch 'lane/sweeppins'
- 2026-10-11 14cce6e4a minor — Merge branch 'lane/memfn-r16' (memfn R-16: KB at w32 only; SIMD-off byte-identical)
- 2026-10-11 d37547755 minor — Merge branch 'lane/memfn-r15'
- 2026-10-11 f18935d44 minor — Merge lane/memfn-r14: R-14 vrun padded word + trimmed verify (deny vrun-pad / vrun-trim); SIMD-off byte-identi
- 2026-10-10 f5ad4a06a minor — Merge lane/sweepfloor: re-pin five start-sweep floors moved by REVEND (95 end-pinned patterns to rev-end, veri
- 2026-10-10 480ac70b9 minor — Merge lane/memfn-r13: [MEMFN] R-13 (SIMD-off byte-identical; slot18 clean)
- 2026-10-10 e33fb8219 minor — Merge lane/sstri: pin rev2corp's start-set movers (test-startset stale manifests)
- 2026-10-10 c85a1aac9 minor — Merge lane/lfl0: locate x finish L0 (no-mover)
- 2026-10-10 0259253e6 minor — Merge lane/rxtread: [RXT-READERS] one .rxt grammar for oracle/var across all three readers
- 2026-10-10 2c6779489 minor — Merge lane/rev2corp: [OPT-REVEND] stage-2 capture corpus (tests/revend/stage2_captures.rxt, 119 blocks, libpcr
- 2026-10-10 59ecac1b0 minor — Merge lane/spectune: [SPEC-CLEAN] tuning.md facts-only, numbered (every section number kept)
- 2026-10-10 25ea505e2 minor — Merge lane/specrxt: [SPEC-CLEAN] rxt_format.md numbered, facts-only
- 2026-10-10 4d6beafb8 minor — Merge lane/specsmall: [SPEC-CLEAN] facts_listing/ir_listing/findings facts-only; -i --help follows the encodin
- 2026-10-10 63d0f4a41 minor — Merge lane/speclim: [SPEC-CLEAN] limits.md + cli.md facts-only, numbered
- 2026-10-10 51f4b625b minor — Merge lane/specreg: [SPEC-CLEAN] registry.md + table_contract.md facts-only, numbered
- 2026-10-09 709c8ff6b minor — Merge lane/specnum: [SPEC-CLEAN] match_api.md facts-only + spec numbering/TOC; S748/S749; spectri triage
- 2026-10-09 7b98a046f minor — Merge lane/rq2 (9c830637): memfn RQ-2 — D157 ranked rarity array (MF_SITE_ABI 9), S731-S737, emit_sweep varian
- 2026-10-09 5761cd03e minor — Merge lane/clibundle: [SIZE-CAP-FLAG] --fast-or-fail -> --size-cap=refuse
- 2026-10-09 2b7f403ab minor — Merge lane/k100: K100 (restart restores the caller's K) + K98 (--pattern-esc honoured by --emit-ir/--emit-fact
- 2026-10-09 223134c7a minor — Merge lane/mechpar: [TT-MECHPAR] mech rows as a slot pool (the PROCS>1 throttle waited on the OLDEST row's pid
- 2026-10-09 287133bae minor — Merge lane/memfn-m6: [MEMFN] R-10 / M6 (N6 + VMSTRIDE, zero movers, no abi event; slot14 green: identity gate 
- 2026-10-08 1debbd043 minor — Merge branch 'lane/decfbB3' ([DEC-FALLBACK] B3: the dispatch replaced — one fit_walk over the arrival labels, 

### none (not counted)

- 2026-10-23 f04019218 none — merge lane/fileq: D176 stop-ranking rulings, three plan rows, kit addendum rules (Frank)
- 2026-10-23 9fbca5b9e none — merge lane/guide: living coding/architecture/style/critics guide in docs/dev/guide/ (Frank)
- 2026-10-22 c3ea619c3 none — Merge lane/r29rev: review of kit R-29 (verdict MERGE)
- 2026-10-21 c24a6c458 none — Merge lane/memfn-r27: walk_vs_v1 record, ruling notices, R-27 design, kit wake/journal
- 2026-10-21 8f4075694 none — Merge lane/memfn-adatwin: kit adatwin work
- 2026-10-21 84ddb7926 none — Merge lane/memfn-flat: kit flat work
- 2026-10-21 5919896ac none — Merge lane/memfn-e8min: kit e8min work
- 2026-10-21 735b91865 none — Merge lane/covertime: part 1 cover timing harness + RESULT (1080 rows, gate passed; NO-GO for B1 as routed: co
- 2026-10-21 d6145f838 none — Merge lane/memfn-setdig @ 0d713d053: kit wake + journal
- 2026-10-21 c5535bbb6 none — Merge lane/parity: [FINDALL-NEXT] pre-build parity slot (twin rev 3 + timing driver); result: batch cell OFF, 
- 2026-10-21 5cceda570 none — Merge lane/x0fix: kit_proof rev 2.2 (R1 emitted-entry read, R2 true set incl. view bytes, K35 recount, U20); X
- 2026-10-21 63a7c3315 none — Merge lane/x0oracle: kit_proof X0 run (NOT passed: R1 unseeded-entry reading, R2 eol-view hull; clean core 0 d
- 2026-10-21 4c46ddcba none — Merge lane/memfn-b4: r17b_prime rev 4.1 (B4 design, docs only; D169 default)
- 2026-10-20 a6b539ffd none — Merge lane/b4ruling: D169
- 2026-10-20 2967e9f0a none — Merge lane/memfn-r25: kit wake.md in-flight note (c111ca99b)
- 2026-10-20 9b3b2dc11 none — Merge lane/qskill: /q (owner's next question) and /idle skills
- 2026-10-20 72c8dccaa none — Merge lane/procdocs: BRIEF_TEMPLATE + build-go stop rule; superseded doctrine refreshed (apply_here 1, 7)
- 2026-10-20 441ce7e6f none — Merge lane/devmethods: dev-methods handoff for other projects + apply_here proposals (docs only)
- 2026-10-18 f5fc8dcd6 none — Merge lane/citri4: ctx_span readers.txt no longer cites plan.md by line (PL14; CI 39187335028 red)
- 2026-10-18 3a3e1c271 none — Merge lane/ctxspan21: ctx_span.md rev 2.1 (re-check R1-R4 applied; per-thread narrowing; row-gated absent)
- 2026-10-18 891df789c none — Merge lane/ctxspan2: ctx_span.md rev 2 (9-cell table, A1 fix, derived lists, \A/\z census) + kit_proof r4 edit
- 2026-10-18 cb9f4f801 none — Merge lane/ctxspan: ctx_span.md design note for re-scoped [DD-11.5] (D168)
- 2026-10-18 e90028226 none — Merge lane/lostset (dd11set): the [DD-11] family survey for the DD-11.5 review
- 2026-10-18 b1effe937 none — Merge lane/u1rev21: kit_proof.md revision 2.1 (re-check applied; admitted-set delta 0)
- 2026-10-18 25489ec59 none — Merge lane/u1rev: kit_proof.md revision 2 (r3 panel applied)
- 2026-10-18 03c469692 none — Merge lane/u1design: [KIT-VERIFY] U1 design note (kit_proof.md), PROPOSED, panel next
- 2026-10-18 1be8db215 none — Merge lane/kvcensus: [KIT-VERIFY] proof census (D161 add. 16 gate): whole-cover 87 bench / 1,060 corpus, DFA p
- 2026-10-18 b39a69c2e none — Merge lane/rwfix: [REGIME-CORPUS] four bad nonenglish files replaced, CRLF/head-bias caveats recorded
- 2026-10-18 550d91f9a none — Merge lane/memfn-b3: kit docs (journal, responses, wake)
- 2026-10-16 a96934d59 none — Merge branch 'lane/iterrev3' (findall_iter.md rev 3: panel r5 discharged, no owner check, batch setter)
- 2026-10-16 dbd7498ca none — Merge branch 'lane/cmprev4' (compound_entries.md rev 4: part-layout controls, dial presets)
- 2026-10-16 37df1ab28 none — Merge branch 'lane/wcfix' (window_contract.md rev 3.1: r4 panel discharged, C-PERT, one render point)
- 2026-10-16 335551be7 none — Merge branch 'lane/iterrev' (findall_iter.md rev 2: iterator as compound controllers)
- 2026-10-16 ee858ac95 none — Merge branch 'lane/cmprev2' (compound_entries.md rev 3: panel r3 discharged)
- 2026-10-16 64e77cf9a none — Merge branch 'lane/wcrev3' (window_contract.md rev 3: E-1 design, C-1..C-16 applied)
- 2026-10-16 14feaf4d9 none — Merge branch 'lane/msrev3' (measure_sets.md rev 3: r2 re-check discharged)
- 2026-10-16 74ac73f7f none — Merge branch 'lane/cmprev' (compound_entries.md rev 2: five pinned part-layout positions, L0-L11 first-match t
- 2026-10-14 9044e42c1 none — Merge branch 'lane/cmpentry' (compound_entries.md: entries as compound controllers, the dial's part-layout row
- 2026-10-14 86a9638da none — Merge branch 'lane/rwquest2' ([REGIME-CORPUS] J1b sealed reserve: 165 blinded questions, hash-only)
- 2026-10-14 e735ea26d none — Merge branch 'lane/iterdes' ([FINDALL-NEXT] D165 iterator design note, docs + compile-only probes)
- 2026-10-14 54f350c44 none — Merge branch 'lane/msetrev' (measure_sets.md rev 2.1: panel r1 applied, D166 add. 2 ruled, [KNOW-SRC] module +
- 2026-10-14 24c914758 none — Merge branch 'lane/rwquest' ([REGIME-CORPUS] step 2: 177 blinded user questions over the real-world corpus)
- 2026-10-14 7fd669ea9 none — Merge branch 'lane/msetdes' ([MEASURE-SET] design note, docs only; D166 + add. 1/1.1)
- 2026-10-14 c63e272e0 none — Merge branch 'lane/rwcorpus' ([REGIME-CORPUS] step 1: licensed real-world subject corpus, fetch script + manif
- 2026-10-14 9afeee362 none — Merge branch 'lane/memfn-docs' (kit design/record docs onto main: regime_eval, r17b_prime, costmodel/gridread,
- 2026-10-13 32adad7ea none — Merge branch 'lane/armread' (facts: per-engine C_call/C_match/c_byte from the joint regime slot)
- 2026-10-13 3182dddf5 none — Merge branch 'lane/slotarms' (pcrec engine arms for the joint regime slot, kit harness contract layout)
- 2026-10-13 c4e30f413 none — Merge branch 'lane/regimefacts' (facts: liner/dinghy cost constants and crossovers from existing data)
- 2026-10-13 5fede9b20 none — Merge branch 'lane/origsurvey' (search-origin survey over the kit's R17-b loss table)
- 2026-10-13 ebb90adce none — Merge branch 'lane/o101ans' (facts for bench O-101's four asks)
- 2026-10-13 68bd5fea6 none — Merge branch 'lane/memfn-g2isa' (kit: G2 SIMD arms gated on host ISA; loud named skips)
- 2026-10-13 37084389c none — Merge branch 'lane/ci4tri' (CI shard 1 red: kit G2 x86-64-v4 SIGILL on a non-AVX-512 runner)
- 2026-10-13 43e741e25 none — Merge branch 'lane/memfn-g2pin' (kit: G2 SIMD taskset pin derives from available CPUs; CI shard 1 red)
- 2026-10-13 52c2c3917 none — Merge branch 'lane/citime' (CI make test timeout: growth, not a hang)
- 2026-10-12 acd382238 none — Merge branch 'lane/plantri' (plan.md triage report)
- 2026-10-12 690dc4e03 none — Merge branch 'lane/cprev22' (compound.md rev 2.2)
- 2026-10-12 c8b7a7e9e none — Merge branch 'lane/b3rev'
- 2026-10-12 3e6a15424 none — Merge branch 'lane/cpcall'
- 2026-10-12 076431df5 none — Merge branch 'lane/wcrev2'
- 2026-10-12 2a8eda971 none — Merge branch 'lane/wcrev'
- 2026-10-12 faefb587d none — Merge branch 'lane/b3meas'
- 2026-10-12 9ca57e4d3 none — Merge branch 'lane/d161note'
- 2026-10-12 096f7d703 none — Merge branch 'lane/b3cost'
- 2026-10-12 3bcb4fe0a none — Merge branch 'lane/endmark'
- 2026-10-12 cb1b9e68f none — Merge branch 'lane/mscomp2'
- 2026-10-12 f24c81282 none — Merge lane/mssurvey: [MATCH-SPLIT] step-0 survey (pin-only 35, bench 0; quadratic confirmed on 11 trim shapes;
- 2026-10-12 9a1381a24 none — Merge branch 'lane/a5inv'
- 2026-10-11 f9250a4e4 none — Merge branch 'lane/wingame2' (window-search game: Frank's refine policy)
- 2026-10-11 d56ae8231 none — Merge branch 'lane/wingame' (D161 window-search game, counts only)
- 2026-10-11 6d80ba45d none — Merge branch 'lane/twintime' ([LOSS-REVIEW] quiet-box twin timing: seam helpers, T5)
- 2026-10-11 6a697d72a none — Merge branch 'lane/pcureport' (report: the cost family's input formulas)
- 2026-10-11 bf460fa33 none — Merge branch 'lane/pcurev' ([PRIOR-COST-UNIFY] design note rev 2)
- 2026-10-11 2a3b839d0 none — Merge branch 'lane/pcudes' ([PRIOR-COST-UNIFY] design note rev 1)
- 2026-10-11 7768e74dc none — Merge branch 'lane/msthink' ([MATCH-SPLIT] requirements note)
- 2026-10-11 edddc3812 none — Merge branch 'lane/lrrev' ([LOSS-REVIEW] fixes.md revision 2)
- 2026-10-11 211bc5f3d none — Merge branch 'lane/lrfix'
- 2026-10-11 28b3df8aa none — Merge branch 'lane/lrdfa'
- 2026-10-11 c32eb1e15 none — Merge branch 'lane/lrvm'
- 2026-10-11 df949ed41 none — Merge branch 'lane/lrmisc'
- 2026-10-11 a7715af43 none — Merge branch 'lane/memfn-ideas3'
- 2026-10-11 48343196e none — Merge lane/memfn-r15: R-15 scoping notice + report (docs only)
- 2026-10-11 873041927 none — Merge lane/rewtwin: rev-end-width measurement (K103 fix (b); scratch tier; docs/harness only)
- 2026-10-11 8c11e4bd2 none — Merge lane/rlhtwin: one-byte handoff measurement — entry-only captures 0-6%, re-entered handoff 109-120% of re
- 2026-10-11 5950c406e none — Merge lane/rincensus: rev-inner census under the ruled gates + multi-branch model (branch composition finding)
- 2026-10-11 50835b064 none — Merge lane/rinmodel: rinner_model gains the factor-free G2 arm (D151 add. 5): 0 wrong arm-only on libpcre2 10.
- 2026-10-11 3d8f1143a none — Merge lane/memfn-ideas2: Q-RQ4-1 ruled by Frank (keep KB; trim vrun verify; re-time) — notice, ideas, journal
- 2026-10-10 6e925916b none — Merge lane/et1twin: [ENG-TACTICS] stage 1 trigger (K12 recount under G2 + reverse-inner hand twins; docs/harne
- 2026-10-10 2aaa2bd15 none — Merge lane/memfn-rq4: RQ-4 tier-U timing (kit slot20) — harness, table, report addendum, responses notice (doc
- 2026-10-10 a2f66450f none — Merge lane/memfn-ideas: memfn/docs/ideas.md (docs only)
- 2026-10-10 f9eb4094a none — Merge lane/revpred: REVEND acceptance-cell predictions for bench O-91 ask 2
- 2026-10-10 6dd1394ef none — Merge lane/planaudit: plan STATE audit (ART-POSS-ARMS closed; 6 rows retagged with landed/remaining notes)
- 2026-10-09 856b632d7 none — Merge lane/landrev: [START-LANDING] rev 2 (24 panel ids; linear skip guard; derived edit set)
- 2026-10-09 f008e1fbb none — Merge lane/landdes: [START-LANDING] design note + twins (design only)
- 2026-10-09 34766669a none — Merge lane/locfin21: locate_finish.md rev 2.1 (path derivation in L0; 27 re-check ids dispositioned)
- 2026-10-09 1ec2d53bc none — Merge lane/locfin2: locate_finish.md rev 2 (all 38 panel ids dispositioned), where_to_start.md §2.2 E1 fix, ce
- 2026-10-09 d8c1b489c none — Merge lane/encinv: [ENC-DATA] encoding data inventory + layout proposal (design only)
- 2026-10-09 bd8c41867 none — Merge lane/walksurvey: gratuitous-walk survey (docs/dev/walk_survey.md + studies/walk_survey; measurement only
- 2026-10-09 57fe04efb none — Merge lane/locfin (6d64f4b0): D156 locate x finish design note + census (design only)
- 2026-10-09 8536a75a4 none — Merge lane/u8pick0 (1a02f131): [U8-PICK] STEP 0 twin (studies only)
- 2026-10-09 49bc507bb none — Merge lane/revrev (82763dc0): [OPT-REVEND] rev 2 (walk-only primary, X1-X13 dispositioned) + r2 twin/timing
- 2026-10-09 d33d38990 none — Merge lane/revq1: REVEND Q1 bounded-pattern timing (studies only)
- 2026-10-09 7a6c7d506 none — Merge lane/revdes (a161e4e4): [OPT-REVEND] design note + hand-twin (docs/studies only)
- 2026-10-09 df66a0323 none — Merge lane/memfn-r12 (f7811f57): R-12 step 1 scoping, VMLAZY + N7U (docs only)
- 2026-10-09 47842ee33 none — Merge lane/memfn-r4e0b tail (2c1ff669): kit journal + wake.md, R-11 complete (docs only)
- 2026-10-09 6b70cd391 none — Merge lane/memfn-skill: pcrec-memfn-manager skill, deadlock check folded into the heartbeat (Frank 2026-10-09)
- 2026-10-09 ee1c79b23 none — Merge lane/r9d (ad3d9ea4): [MEMFN] R-9 done, r9b light re-check applied (docs only)
- 2026-10-09 f27ff639f none — Merge lane/memfn-m7: kit wake.md + journal at session reset (docs only)

## Runs

One line per full run, copied from the job's `summary.txt`: date, commit, verdict per stage, log path,
duration. Retained logs live under `build/full_suite/<date>_<sha>/` (gitignored, kept on this box).

| date | commit | test | strict | axes | san | alloc | lint | mech | recidentity | log | duration |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 | 5596c3207 | green | green | RED (rc=2) | green | green | green | RED (rc=2) | RED (rc=2, known [RECID-A]) | build/full_suite/20261023_5596c3207/ | 36877 s |
| 2026-10-27 | 7d3be7ec7 | green | green | green | RED (rc=2) | green | green | green | RED (rc=2, known [RECID-A]) | build/full_suite/20261027_7d3be7ec7/ | 40149 s |

RED run: counters do not reset. Fixes: lane fsfix (axes allowance keys, mech row re-aims). Triage and dispositions: `full_suite_runs/20261023_5596c3207/`.

RED run: counters do not reset. san = one LSan leak from [INLINE-C] 1b `--callout` (cli_parse realloc never freed), FIXED by lane/sanred (merged after the run; san-only re-run 610-main-sanrerun). recidentity = only the known (A), counts identical to 7234c2e86 (167/381/167/111); bref-rename bucket 328 (was 366, census 411). mech green: unexpected 0, anomalies 31 = plants that do not compile (14 -Werror, 11 stale, 6 designed compile catches) -> [MECH-NOCOMPILE]. Triage: docs/dev/lanes/suitetri_report.md, sanred_report.md.
san re-run on main 3e550f92d (after lane/sanred), job 610-main-sanrerun: GREEN, run_san_group 41/41, wall 3441 s. The run's only stage-level red besides the known [RECID-A] is cleared.
