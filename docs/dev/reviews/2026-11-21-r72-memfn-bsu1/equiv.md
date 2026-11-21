# CRITIC EQUIV — r72 memfn-bsu1

## Findings

No defect found: 0 SILENT-MOVE, 0 LOUD across 799 compiles. Two low notes, EQUIV-1 (the floor is reachable only from the kit layer, so it is held by reading) and EQUIV-2 (a wfS trace record carries no stretch identity), are written out in full just below the PROBED-AND-HELD heading. The file was appended to, so they landed there.

## PROBED-AND-HELD


(No defect found. I read the equivalence argument fully and probed 799 compiles; every BASE vs SUBJECT compare was SAME. Two notes follow, neither a defect.)

### EQUIV-1 — the floor's (E-generic) stretch list cannot be reached from a pcrec compile; it is held by reading alone
SUSPECTED gap in evidence, not a defect. Severity: maintenance (evidence). Effort: none for this lens; the CHECKS/CORPUS lenses would confirm it.
Blast radius: only the floor's `wf_stretches` call (window.c wf_plan_site's E_GENERIC branch, ~:2696).
In a CLI compile the floor is never chosen. `--memfn=no-window-search` hands the site to E-stmt (legacy); the MF_TRACE wfE END record read `chosen=E-stmt moved_from=E-func` on `[0-9]{10}[0-9a-f]{10}[0-9]{10}`. That matches window.c's note "no byte of a default artifact, wsc6's sweep". So no pcrec-layer compile exercises the floor's new enumerator call.
By reading it is identical. plan_of sets `w->skip = -1`, the value the old C-floor passed explicitly. Only wf_find_prepare (E_FIND only) writes `skip`. The rows walk the same site/art facts as the retired wf_span_head. The floor's `grp` is the same array the old wf_loop_len read.
Its byte evidence must come from the kit layer: memfn/tests/g2 (g2_win_gen.c carries the span-head lever) and d27_frame floors.tsv. I could not run these (no make). To confirm, find the G2-window case count on E-generic sites under span-head and span-loop in the identity gate's record.

### EQUIV-2 — a wfS record does not say which stretch it chose for
Severity: doc (trace legibility), low. Effort: small, one field (i/k) on the END record if wanted. Blast radius: MF_TRACE readers only.
A site gets one wfS SEL/ROW/END group per stretch, but the record carries only art/site/phase. The stretch's entry, length and h appear nowhere. Today this is harmless: every row's predicate is site- or art-wide, so all of a site's stretches get the same row, and the C's loops pair with the records by order. Seen on `[0-9a-f]{12}abcdefgh[0-9a-f]{12}` --memfn=span-loop: 2 T-force ENDs, and the C shows loops J=0..11 and J=20..31 with the C-run at 12..19. On `[0-9]{10}[0-9a-f]{10}[0-9]{10}`: 3 T-force ENDs, 3 loops.
The first per-stretch predicate (the §3 later rows) makes the pairing ambiguous. Trigger: the first wfS row whose `holds` reads `x->i`/`x->k`.

## PROBED-AND-HELD (continued below the heading above)
(The findings above landed after the PROBED-AND-HELD heading because the file was appended to. EQUIV-1 and EQUIV-2 are the findings.)

**(a) Reading. The equivalence argument HOLDS in every case below.**
- Partition. wf_loop_len's breaks per entry (skip, grp, !core, not-WIDE) do not depend on where the stretch starts. Its breaks between entries are "consecutive offset", plus table and set EQUAL to entry i's. Equality is transitive, so a run started anywhere inside a head-0 stretch [s,e) runs exactly to e. The old per-position call with head h therefore returned exactly what the new call returns inside the stored stretch.
- Outside every stretch, old wf_loop_len(i,h) > 0 implies wf_loop_len(i,0) >= 2. The greedy enumerator either starts a stretch at such an i or has already jumped over it, so the new `i < end` guard drops nothing.
- The test loop never jumps past a stored stretch's start. A loop always ends at its stretch's end, and the starts never sit on `skip` or on grp entries, which the test loop skips. So `si` stays in step.
- The minimum of two: a stretch whose part at or above h is one entry gives 0 (a lone test) in both old and new.
- A stretch that begins below the head: entries below h are lone, then one loop from the first entry at or above h. Seen under the lever at N=1: 40 loops start at J=1.
- Negative offsets: the lever is parsed as unsigned 0..MF_SPAN_HEAD_MAX (cli/main.c:1571, compose.c:1651), so no head below 0 exists. The head-0 enumeration is therefore the finest. A negative h, if one existed, would differ: old would start a loop below 0, new would not. That case is unreachable.
- `w->skip`. stop_skip reads stop_alone/stop_ix and hors_skip reads hl/grp. All four are final when wf_find_prepare computes skip: stop_alone at its top, find_groups before, hl in srch->prepare before. Nothing writes them later (the renderer's plan is const). The old head() read the same values at render time, including the early-return path of base d_hors_head, where `*skip` is set after the probe text. The fused path returns before skip and the stretches, but it renders no wf_test_to (B-fn is ofsskip's).
- `build == 0`. find_groups still runs, so grp, skip and the stretches are formed. That plan is a phase-1 or quiet plan that is never rendered (the define would also dereference a NULL `runs` in BASE).
- The gate. Every field in fields.def (63) is MF_ANY in WF_CT_S (I compared WF_SERVES_FRAME+REST+WINDOW+moved+entry+core against fields.def: no difference). use_nothing names no field, no row has an opt or a deny, and kit_walk is passed denies=0. So the gate cannot decline T-deny, T-force or T-lever, and no later row can win by refusal. The row order and predicates match the retired wf_span_head: deny < 0, force > 0, `art && levers`, else 64.
- The floor: see EQUIV-1, held by reading.
- The arena: the extra allocation of `w->str` changes no bytes.

**(b) Probes: 799 compiles in total, every one rc 0 on both sides, each compare classed SAME / SILENT-MOVE / LOUD.**
- SPAN-SEED, all 41 `pattern` lines × 8 configs: default, --memfn=span-loop, --memfn=no-span-loop, --engine=vm, -e utf8, and harness span-head=0/1/64. That is 328 BASE vs SUBJECT compares: **328 SAME**, 0 SILENT-MOVE, 0 LOUD. 108 of the outputs hold span loops (36 each in span-loop, lev0 and lev1).
- Crafted seams, 13 patterns × 5 configs (default, span-loop, lev1, `no-window-search,span-loop`, `no-window-search`+lev1). That is 65 compares: **65 SAME**. The patterns covered two-entry stretches (`x[0-9]{2}y[a-f]{2}z`), set breaks (`[0-9]{10}[0-9a-f]{10}[0-9]{10}`), lookbehind, alternation, `\d{3}-\d{3}-\d{4}`, `[0-9]{15}q[0-9]{15}`, `[0-9]{30}z`, plus several that route legacy (E-func) and so are trivially SAME.
- A C-run beside a one-class stretch on E-find: `[0-9a-f]{12}abcdefgh[0-9a-f]{12}` under span-loop, BASE vs SUBJECT **SAME**. Route-checked with trace (E-find, 2 T-force records, loops at 0..11 and 20..31, run compare in between). Three more C-run+stretch E-find witnesses were route-checked on the subject only (out of compile budget for their pairs).
- The skip/probe entry ending a stretch (D-hors): `[0-9a-f]{32}` under span-loop gives probe at 31 and loop 0..30: SAME.
- The MF_TRACE pair (trace:base vs trace:subject, d3, span-loop): rx.c is byte-identical. Stderr with the `table=wfS` lines removed is 105 vs 105 lines, diff empty. Nothing else moved. BASE emits 0 wfS lines.
- Not reached from the CLI: any loop at offset 64 or above. No window plan's tested offsets exceeded 32 in any probe, so T-head's H(64) never renders a loop; the head-mid-stretch logic was exercised through the lever (N=1) instead. The floor was not reached either (EQUIV-1).
- Witness lengths. Patterns ran from 2 positions (`[0-9]{2}`) to 1002 (`[0-9a-f]{1002}`). Loop stretches ran from 2 entries to 32; the largest offset in a loop was 31.

CRITIC COMPLETE
