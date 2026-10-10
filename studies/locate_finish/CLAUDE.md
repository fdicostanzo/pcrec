# studies/locate_finish/ — the LOCATE × FINISH census (lane locfin, D156)

Compile-side census behind `docs/design/locate_finish.md` (§3, §4): which
locator and which finisher every corpus and bench artifact gets TODAY, and the
populations the note's new rows would reach. No subject is matched and no
clock is read. First pin: main `525dec33` (abi 71), Linux dev box, gcc 15.2;
pcrec-bench read at `76e13c1d` (read-only). RE-RUN pin (lane locfin2, panel
LF-C10): main `7efca415`, src identical to `525dec33`; pcrec-bench read at
`76e13c1d624739a069afe863297c262f4d936b4f`; 5,798 rows (5,355 compiled), 17 s
at JOBS=6. Every pre-existing `rows.tsv` cell and every T1-T8 line is
byte-identical to the first run; only the control block moved. SECOND RE-RUN
(lane locfin21, rev 2.1, re-check LR-G4/LR-S1): main `00ddf7d5` (src
identical), the same pcrec-bench commit, JOBS=2 (a kit run held the box); two
TEXT columns added (`t_fwd`, `t_anch`), every pre-existing cell of all 5,798
rows byte-identical (checked column by column), every summary line identical
except the new control C5.

- `census.py` — builds the two populations and runs the end-pin probe by
  IMPORTING `docs/dev/optloop/revend/census.py` (`bench_pop`, `corpus_pop`,
  `run_probe`), so this census and [OPT-REVEND]'s count the same rows the
  same way; the probe is `docs/dev/optloop/revend/revend_probe.c` built from
  its committed source against this tree's `build/libpcrec.a`
  (`gcc -O1 -Ilib -Isrc docs/dev/optloop/revend/revend_probe.c build/libpcrec.a -o PROBE`).
  Per row: `pcrec --emit-facts` (the `kinds`/`start_anchor`/`end_window`
  facts, the end_window decline reason `f_end_window_why`, and the decision
  stamps, now including `VM_RESEED`) and the emitted C itself (TEXT: a reverse
  machine present, an inlined prefilter present, and since rev 2.1 a forward
  and an anchored machine present: any `rx_forward_` / `rx_anchored_`
  identifier). Env and the exact command
  are in its docstring. Writes `results/rows.tsv` (committed gzipped).
- `analyze.py` — five CONTROLS first (C1 stamp vs text on the reverse
  machine; C2 stamp vs text on the inlined prefilter; C3 the borrowed probe vs
  the SHIPPED `end_window` fact, TWO-SIDED; C4 the census's exact/superset
  hybrid classifier vs the `RX_VM_RESEED` stamp — PLUMBING since rev 2.1
  (re-check LR-S2/LR-G3: the stamp's row predicate is `Vm.mrl_win`, the same
  conjuncts the classifier's stamps come from, so it checks that two readers
  of one derivation agree, not that the derivation is right); C5 [rev 2.1,
  LR-G4/LR-S1] the machine MEMBERSHIP rule the three membership readers spell
  today ("forward always, reverse unless pinned, anchored iff unwrapped",
  nothing on attempt/empty), read off the stamps, vs which of
  `rx_forward_`/`rx_reverse_`/`rx_anchored_` the emitted C carries, hybrids
  included: 0 disagreements over 5,355 artifacts, the membership the L0 path
  derivation must reproduce); it exits 1 and prints no table if any
  disagrees. Then tables T1-T8 (today's pairs, hybrids
  by their prefilter's locator, the end-pinned population by pair, the
  stage-1 / stage-2 / relaxed-reverse populations, their bench members, D-2's
  population). `results/summary.txt` is its verbatim output.
  - C3 forward: shipped numeric `end_window` => probe view in {`$`,`\z`}
    (400 rows, 0 disagree). C3 forward-width: shipped numeric => probe cwmax
    finite, except the DECLARED exception "pattern calls a group" (138 rows,
    all corpus): the probe never runs the call expansion, so it reads
    `^(a|b)\g<1>$` unbounded where the shipped fact says 3; classified from
    the pattern text. C3 converse: probe pinned AND probe cwmax finite =>
    shipped numeric, except the two DECLARED exceptions endwin.c's header
    names that can reach the premise: multibyte encoding (22 rows, all
    utf8, 16 distinct) and `\G` (2 rows, `\G\z`, `\G$`). They are classified
    from the row's encoding and the probe's `gstart`, never from the shipped
    answer; the shipped decline reason (`f_end_window_why`) is read only to
    confirm it matches. The other endwin.c declines (unbounded, multiline,
    not end-anchored) cannot reach the premise. A converse failure outside
    the declared exceptions exits 1.
  - C4: every compiled hybrid, classifier `F-vm-span` iff `RX_VM_RESEED` is
    `exact` (the RETRY row `exact`, first in its slot, deny mask 0, predicate
    `Vm.mrl_win`): 759/0/0/734; no structural exception; also asserts the
    stamp exists on every hybrid and on no non-hybrid, and prints the
    atomic/lookaround/lang counts as a positive control on the kind-name
    spellings. Sabotage-validated (a flipped stamp, a flipped fact, a flipped
    superset stamp each exit 1).
- **[OPT-REVEND] L0's controls (lane lfl0, the BUILD, 2026-10-09).** With
  `PCREC_TRACE` set to a `-DPCREC_CAND_TRACE` build of the same tree,
  `census.py` adds a PATH instrument per compiled row (appended columns
  `p_ok p_finish p_locate p_members p_asks p_erased p_oldexact t_asks`, every
  earlier column unchanged): the trace build's `CANDPATH` record (the L0 path
  derivation's own routes, member set and asked cells, and on a hybrid the
  lowering's recorded erasure set beside the conjuncts it replaced) and its
  `CANDROW ... ask` hits, SEGMENTED per emission attempt (a size-ladder retry
  emits twice in one process). `analyze.py` then runs three more controls and
  exits 1 on any: **C5-L0** C5 with the stamp side replaced by the
  derivation's members (text side kept); **C6** the TRACE vs `asks` (the
  emitters' asked cells against the closure's, up to the DECLARED stamp-only
  asks in `asks_declared_L0.tsv`, entry slots compared without route; a
  declaration no row uses fails as stale); **C7** LR-G3's no-mover compare
  (`Nfa.erased` empty iff the old atomic/lookaround/collapse conjuncts read
  exact, every hybrid). Measured at the L0 tip: C5-L0 0 / 5,355, C6 5,355
  agree (six declared shapes, all used), C7 0 / 1,495 hybrids. The census
  results committed under `results/` are the locfin21 run and are NOT
  regenerated by L0 (the PATH columns live in the lane's scratch run, cited in
  `docs/dev/lanes/lfl0_report.md`).
- `asks_declared_L0.tsv` — the stamp-only asks C6 allows (a stamp reports a
  slot's selection off the path: `RX_DFA_START` on attempt/empty bodies,
  `RX_DFA_PREFILTER`/`RX_REQ_*` on empty bodies, `RX_VM_START_SCAN` on DFA
  artifacts); L2.1's generated stamp rule empties it.
- `trace_declared_L0.txt` — the L0 tip's declared trace multiplicity for
  `emit_sweep.py --trace` (the three new sites `locate`, `finish-match`,
  `boundary`), with why the moved-but-not-added records are not declared.
- `mk_l0_rows.py` — [lane lfl0] writes L0's ten new sabotage rows (the
  note's §5 L0 plants 1-10, each plant-validated DETECTED at landing,
  `docs/dev/lanes/lfl0_report.md` §2.3) under the ids the manager assigns:
  `python3 studies/locate_finish/mk_l0_rows.py tests/mech/sabotages ID1 ... ID10`.
  Its anchors are the L0 tip's text.
- `results/l0_build_sabotage_anchors.tsv`, `.summary` — [lane lfl0] the
  derivation at the L0 BUILD tip, `--step L0=e1e387b9..<tip>` over the
  edit set with the seven build lines appended: 8 re-aim (the planned
  eight), 55 rows re-run at L0 (54 by hunk, 1 by reach), 75 sites after; the
  same 3 pre-existing unresolved sites (exit 2).
- `finish_sites.sh` — the FINISH decision as spelled today: every code line
  under `src/gen/` testing `fit.chosen`, `fit.prefilter` or `prefn`.
  `results/finish_sites.txt` is its output; the note's §3.3 dispositions it.

- `l0_edit_set.tsv` — [lane lfl0 appended the seven lines the BUILD changed
  beyond the plan; the derivation at the L0 tip with `--step
  L0=e1e387b9..<tip>` reads 8 re-aim (the planned eight), 55 rows re-run at
  L0, 75 sites after; lfl0_report.md §2] [lane locfin2, panel id C3; extended by lane
  locfin21, re-check LR-S6] the text `locate_finish.md` rev 2.1's L0 CHANGES,
  written once as data (55 entries: 18 `def`, 2 `token`, 35 `line`, each with
  its reason; rev 2 had 31), in `docs/design/start_table/refactor_edit_set.tsv`'s
  format. Rev 2.1 added the path derivation's readers (LR-S1's three
  membership functions, `emit_vm.c:11330`, the F-9 spellings incl.
  `compile.c:229`/`:2381`, two of the eight `dfa_engine_is_empty` callers as
  precise lines), the erasure-set record (LR-G3, three `src/ir/nfa.c` arms and
  `pcrec_vm_prefilter_window`), the boundary projection's one assignment
  (`emit_vm.c:10368`), the match axis's listing sites and the three RETRY
  `.contract` rows (LR-S11). The re-aim list is DERIVED from it, never stated:
  `python3 -I docs/design/start_table/sabotage_anchors.py . CALL_GRAPH
  studies/locate_finish/l0_edit_set.tsv --final after-L0`, where CALL_GRAPH is
  `docs/design/start_table/call_graph.py .`'s output at the same pin (not
  committed; regenerate it). `results/l0_sabotage_anchors.tsv` and `.summary`
  are that run at main `00ddf7d5` (rev 2.1): 8 re-aim (S140, S494, S566, S599,
  S606-S609), 35 rows / 36 sites re-run at L0, 76 rows / 78 sites after L0; 3
  pre-existing unresolved `src/` sites outside the family (S176, S640, S571),
  so the tool exits 2 as it did for rev 2. (Rev 2's run at `7efca415`: 6
  re-aim, 18 re-run, 98 after.) `sabotage_anchors.py`'s ORDER gained `L0`/`L2`
  for this (byte-neutral for the C/B labels). A build lane re-derives at its
  own pin before numbering.

**The instrument defect it caught in itself (recorded, not hidden).** The
first run's TEXT marker was `rx_reverse_next_state`; C1 read 146
disagreements, all artifacts whose reverse machine uses the uniform-fold
representation (`[CC-DIFF]`), which has no next-state accessor. The marker is
now any `rx_reverse_` identifier and C1 reads 0; without the control the
census would have reported 146 reverse-pass artifacts as having no reverse
machine.

Regenerating `rows.tsv.gz` (a new pin, a grown corpus) moves `summary.txt` and
every population number in `docs/design/locate_finish.md`; no check reads
these files.

- `l2_movers.py` — [lane revbuild] [OPT-REVEND] L2's MOVER CENSUS: every
  corpus pattern compiled by two pcrec binaries (parent and change) at one
  option set, each differing artifact classified by which stamps and
  `rx_info` fields moved (else `text`). Its runs are cited in
  `docs/dev/lanes/revbuild_report.md` (L2.1: 638 rows, all
  `DFA_START`/`search_form` reverse-pass -> attempt-start; L2.2: 274 rows).
  Its outputs are `results/l2_movers_l21.tsv` (L2.1 against L1) and
  `results/l2_movers_l22.tsv` (L2.2 against L2.1); `results/l2_stage2_movers.txt`
  lists the `stage2_captures.rxt` patterns stage 2 moves (default vs
  `-fno-rev-end`).
- `mk_l2_rows.py` — [lane revbuild] writes L2's sabotage rows S758-S781
  (revend.md §9.2's sixteen recast, L2.1's stamp fork, the deference, the
  size-ladder clause and its reader, stage 2's four) from the CURRENT source:
  `python3 -I studies/locate_finish/mk_l2_rows.py tests/mech/sabotages`.
