# landwalk-measure critic (measurement lens), subject p1dsg_report.md @ 3afd1a439

Scripts in `measure/`: `gen.py` (class-word subject generator), `drv.c` (find-all driver over the
shipped 5b artifact `m5b.c`), `shipped_sweep.txt` (shipped instr per q). I could NOT build the twin
(denylist), so everything below reproduces only the SHIPPED side and re-derives the twin from the
report's own ratio column.

## Findings

### MEAS-1 (design, CONFIRMED) the card's unit `instr` cannot exist in a measurement set
Subject §Measurement card: `unit instr`, `gate_e6 30000*`, `aa_rule pair-per-group`. docs/spec/measures.md
§3.1 closes the unit list to `ratio/walkbytes/bytes/count`; every row's value is derived from
`abs_ns` against the unit row, and measure_sets.md §7.4a says no set, card or gate may REQUIRE perf
counters ("Every set must be producible from TIMING ALONE"); §7.3 gates read A/A floors of timing.
A card whose unit is retired instructions, run at install on a box with `perf_event_paranoid=4`,
is unproducible; an instruction count has no A/A noise, so `gate_e6` is meaningless for it. The
report's "instructions because the box was loaded" is a design-time evidence choice that was
carried into the card unchanged. Fix: card unit `walkbytes`/`ratio` against the pinned unit row
(timing), with instr kept as lane evidence only. Effort: small (doc). Blast: the rarity row's inputs,
spec/measures.md, card row. Ref: subject "Measurement card", measure_sets.md §7.2-7.4a.

### MEAS-2 (design, CONFIRMED) `c(route)` does not exist as a measured row; no `pcrec.*` rows exist
`grep` of measure_store/zen4-grid1/1/set.tsv: 0 `pcrec.` keys (only `kit.beta/f/gstar/...`), no
`measure/` directory, no `cards.tsv` (the subject's "does not exist yet" is TRUE). The subject says
the rarity row "pairs with the route's existing per-byte cost (the DFA-step and VM-start rows the
stop choice already reads)". No such rows are in the store, measures.md, or measure_sets.md
(grep c(route), lwhit, dfa-step: nothing). `kit.beta.WALK` is the kit's scalar walk, not the generated
DFA with prefilter+RECOVER (~15 instr/B here). So the rarity inequality has ONE measured side
(lwhit, lwbyte, themselves new) and the other side is a number the lane took from one run.
Stage 1 therefore adds TWO new card families (lwhit/lwbyte AND c(route)), not one. Also `route=vm`
has no subject: the crossover sweep is DFA-only (mask-email), yet lwhit dims are `route;wlen` and
the text prices "VM hat: + attempt setup (VM stubbed)". The VM half is unmeasured.

### MEAS-3 (speed, CONFIRMED by derivation + reproduction) instr break-even is not the cycle break-even
Report's own numbers: shipped 5b acc-main 5,477.6M instr / 2,370M cyc = IPC 2.31; twin 77.8M / 58M =
IPC 1.34 (x70 instr but x40 cycles). I reproduced shipped on a 4 MiB class-word subject: 61.13M instr /
23.33M cyc (IPC 2.62; instr deterministic, cycles within 0.4% over 3 pinned runs on a loaded box, so
"cycles unusable because loaded" does not hold for pinned `cycles:u`; the lane only gave cycles as a
ratio and gave NO cycles for the crossover sweep or fz-me). If the twin keeps IPC ~1.34 per-hit
(branchy walk, kit find + indirect verify), break-even in cycles sits at twin_instr/shipped_instr ~=
1.3/2.6 ~ 0.5, i.e. about one hit per 35-40 B, roughly TWICE as rare as "1 per 19 B". The F=2 interim
happens to sit near that; but the card prices in instr (MEAS-1) and the "H=294, c=15.4" figures
would be mis-priced in the time that matters. Confirm: run the twin's crossover q-sweep with
`instructions:u,cycles:u`. Severity speed (rarity admission wrong for 5-7.5 ratio rows: csv5, kv-quoted,
stack-frame, dotted4/ipv4). Effort small. Subject §Measurement card, §Crossover sweep.

### MEAS-4 (design, CONFIRMED) fit: sound for ONE word length, says nothing about wlen
Re-derivation (measure/shipped_sweep.txt + subject's ratios): on my regenerated subject (8-char words,
1-byte separator, hits counted exactly), H = (ratio*shipped - 0.13*B)/hits comes out 305, 300, 298, 304,
305, 302 for q = 1, .5, .25, .1, .03, .01. So a linear per-hit model with H~300 is well supported
(good; matches 294), and shipped c = 14.6-15.5 instr/B (reproduced; it is NOT constant: 14.58 at q=1
to 15.47 at q=.001, 6%, because dense q shortens runs the DFA scans). Break-even (c-0.13)/H = one
hit per ~19.6 B holds. BUT: (a) all seven points share wlen=8, so `lwhit(dfa, wlen)` as a FUNCTION is
unsupported: the card promises wlen in {2,8,32} yet the report shows one; ~180 of the 300 instr
look like fixed per-hit cost (a walk of 8 B at the shipped 15/B would be 120), so H = a + b*wlen
with a dominating; the rarity row's `wlen-hat` input could matter little or much and nothing says
which. (b) The q=0.001 row is inconsistent with the stated floor: ratio .008 * 64.9M = 0.52M, below
0.13*B = 0.55M before any of the 483 hits (+0.14M); predicted ratio ~.0106, so lwbyte 0.13 is not
supported by its own sweep (the table prints one significant figure). (c) every hit in the sweep
FAILS verify at `@ `; a successful hit consumes the match (verify + span, shipped pays it too) so
H is a lower-cost miss price, not the price of an admitted hit. Fix: a wlen sweep {2,8,32} (and a
hit-succeeds arm) before the number enters any card; label lwbyte provisional.

### MEAS-5 (design, CONFIRMED) the negative control cannot be passed by the rarity row
Acceptance cell "fz-me per line as NEGATIVE control (it must DECLINE or not lose)". fz-me runs the
SAME pattern (5b mask-email) as acc-main, which stage 1 admits at ratio 1237 "at any F". A compile
decides from p(L) = builtin prior (findings.md `byte-rate`, or an `--analysis` bundle the user
supplied); the subject is not seen. One artifact cannot decline for fz-me and admit for acc-main.
So the cell is either (i) a documented, accepted loss (x1.25 instr, and by MEAS-3 likely worse in
cycles), in which case it "loses" by design and must not be an acceptance gate, or (ii) it needs a
runtime density guard, which the memory notes (adaptive run-time switching unproven, walk_vs_v1
CLOSED) rule out. The report's own sensitivity text implies (i); the card list says (ii). Reconcile.
It also means the rarity row's fz-me evidence argues for a user-visible limit (--analysis), not a
number.

### MEAS-6 (design, SUSPECTED) twin acceptance cells would not catch several build regressions
(a) 5b x70 cell: the report shows denying the scan edge changes 77.76M -> 79.66M (2.4%), so a
broken or absent edge (and a mis-seeded stop: row 3's constant-width inclusion) still passes "x70"
unless the cell names a tolerance tighter than 2.4%; give the cell a band (e.g. 77.8M +/- 1%) and a
sibling ablation count. (b) No cell sits on the 5-7.5 ratio rows (csv5, kv-quoted, ipv4, dotted4,
qnt-plus) that the F decision is ABOUT; a mispriced rarity row (F=2 vs 8) changes nothing any listed
cell sees. (c) dup-param cells are per line (bench has no `&`), so stage-2 acceptance is not on
the bench at all (the subject asks the bench for a subject; until then it is lane-only). (d) the
fz-me cell: see MEAS-5. (e) the sabotage ids (max-start, floor ctx, reach guard, EXCLUSION, seed at j)
are listed for the answer net; the "reach guard removed" witness is only an instruction-count witness
and needs a subject whose verify re-reads (quadratic), which is not among the listed cells.

### MEAS-7 (design, CONFIRMED) regime and independence statements are thinner than the standing questions require
Regime (docs/design/CLAUDE.md q1): find-all over acc-main (whole file for 5b, PER LINE for dup-param
because whole-file gives PCREC_ERR_FRAMES on both) mixes two call shapes; per-line means 1.6M calls
each with fixed per-call entry cost in both arms (dilutes the ratio, so x1.45 is a floor for the
walk, not what a whole-file user sees); no hit-vs-miss or dependent-vs-independent statement; one
box (Zen 4 queue-loaded), `-O2`/compiler not stated in the report. A different regime flipping a
decision is shown in the report itself (dense @) but not for cycles (MEAS-3).
Independence (q2): "span hashes compare against the SHIPPED artifact, which shares no start code
with the twin" is true of start LOCATION but the twin's walk machine is "pcrec's own reverse-pass
text of P.L" (extract_rw.py) and its VERIFY is the shipped `rx_match`/`rx_match_anchored`. So the
walk and the final verification share the compiler's own reverse DFA builder with the control;
identity on acc-main (80123 matches, one pattern class) cannot see a builder bug that shipped
RECOVER shares. The libpcre2 `unique_model.py` is independent of pcrec but checks the DESIGN's
algorithm (a model), not the twin or a later build; it is a mutation-sensitive check only
via `--sabotage unique` (10/12 detected: two sabotage rows undetected, the report does not say which).
Population (K35): the census counts "uncounted (reader)" 933 corpus / 34 bench rows (18% / 10%)
and the corpus route split (>50 compiles) is unmeasured, so the 259/43 admitted figures are
ranges, not counts.
Moves-on-regeneration (q3): stated (W tables, two stamps, abi event) but silent on the card:
a regenerated lwhit/c(route) changes the rarity row's selections and therefore which artifacts
differ in `RX_DFA_SCAN` stamps; the card's data is then a P1 set row and its re-measure is a
selection event, not just a stamp (measure_sets.md §2.4 staleness; §3.6 abi readers) -- the report
states the abi event for W's tables but not for the set that prices admission.

### MEAS-8 (doc, CONFIRMED) card row details
(a) Column ORDER matches measure_sets.md §7.2 (owner quantity ver dims unit subject lengths launches
rounds aa_rule gate_e6 env deps). (b) `env` and `gate_e6` spelled `-` and `30000*`: the format uses an
EMPTY field for none (table_contract §2¶5), not `-`, and there is no field for the asterisk label,
the "labelled UNMEASURED default (D149)" must be a card-checked mark or a P2 limits.def row, not a
footnote. (c) `30000` = 3.0% in e6; grid1's per-group A/A p90 is 3.37% (F1), unit group gate is half
(1.5%), so a 3% default would refuse about half the F1 groups; the default is unmeasured and not
even grid1-consistent. (d) `subject landed:crossover-q`: §7.2's `landed:<g-ladder>` token is a
ladder; q-sweeps are not a ladder and `lengths` carries "4 MiB, q in {...}" mixing a length with
a parameter. (e) F=2 is a D149 constant: its home (P2 `limits.def`, with the label) is not named.
(f) rarity inequality: units are consistent (p(L)*lwhit instr/hit * hits/B vs instr/B) and the sign
is right, but the admission table row 5 (`p(L)*H(w) >= c(route)`) omits the `- lwbyte` that the card
text includes (<1% here; spec the same inequality once).

## PROBED-AND-HELD
- Reproduced shipped 5b cost: 14.58-15.47 instr/B at 7 densities (7 builds-runs, 4 MiB each);
  acc-main's 5,477.6M/362MB = 15.1/B agrees. c ~15.4 HOLDS.
- H ~300 per hit re-derived at 6 of 7 q points from the report's ratios (294 stated): linear model
  HOLDS for wlen 8; break-even ~1 hit/19.6 B HOLDS (instr).
- Pinned `cycles:u` repeatability on a loaded box: 6 runs, spread < 0.4%, instr identical.
- Card column order vs §7.2: HOLDS. `measure/cards.tsv` absent: HOLDS ("does not exist yet" true).
- Rarity inequality units/sign: HOLDS (MEAS-8f minor).
- Match count/span hash of my driver: 0 matches on non-matching subjects (sanity only; no twin run).
