# SIM — critic round memfn-spanpick5, lens simulate (span_pick rev 5 at 9c9aadb60)

Question: run rev 5's priced action (§The pick 1-7, the price formula, the band, "With data") over
the real data: does it pick what the design claims, and where does it mispick?

Method. (1) `SIM/mysim.py` implements §The pick's formula and step 3 from the design TEXT only
(written before smp20.py was opened); output `SIM/mysim.out`. (2) `witness.sh` re-run with the
review tree's `build/pcrec` + `build/pcrec-analyze` into `SIM/w/` (16 compiles + 4 listings):
`SIM/witness.out` is byte-identical to `population/span_pick/witness.out`. (3) `counts.py` re-run on
R-33's raw `sweep.jsonl`: `SIM/counts.rerun` identical to `counts.out`. (4) `SIM/drills.py` runs
step 3 literally on constructed outcomes; output `SIM/drills.out`. No make; 16 compiles in total.

Short answer: every number the design quotes is reproduced by an independent implementation of
its own formula (one P digest is borrowed from another tool). The rule picks what the design claims at
smp20. It fails in the places below: the tie set's anchor, the with-data argument, and the
provenance seam.

## Findings

### SIM-1  The tie set is anchored on "the cheapest qualifier", so a candidate that is never picked can still flip the pick
- status: CONFIRMED (constructed; `SIM/drills.py` (i), `drills.out`)
- severity: design
- effort: one paragraph (choose and state the property) ; blast radius: every priced row, plus the growth rule ; where: §The pick 3; §The tables "Growth rule"
- body: step 3 says "those within band of the CHEAPEST go to TIE's rows". The within-band relation
  does not chain (pairwise quadrature bands), so the tie set depends on which qualifier is cheapest.
  Construction: incumbent I 100; q1 80; q2 84; every pairwise band 5; TIE order q2 before q1. Step 3
  picks q2 (tie set {q1,q2}). Add c_new at 78, a qualifier that TIE ranks last. It becomes the
  anchor, and q2 (84 - 78 = 6 > 5) drops out of the tie set. The pick flips to q1, yet c_new is
  never picked. The design only claims "a never-QUALIFYING candidate cannot move the pick". That
  claim holds (`drills.out`, PROBED-AND-HELD). The prompt's stronger property (a never-PICKED
  candidate) fails.
  Second effect: at an exact price tie between two cheapest qualifiers, the anchor is undefined. With
  different pairwise bands the two anchors give different tie sets ((i-b): anchor a gives {a,b,c},
  anchor b gives {a,b}).
  Why it matters: the growth rule ("a new method adds a T-FIND row and card") then moves picks at
  sites the new method never wins. The new row's movers census has to count those sites, and the
  §Staging per-row census reads movers only from the row's own wins.
  Fix: either state the weaker property and add the growth-rule caveat, or define the tie set
  without an anchor. For example, TIE could rank all qualifiers first and price only break within
  TIE's own classes. Neither makes a non-transitive band IIA; the design should say which one it
  accepts.

### SIM-2  The "With data" argument's "no dearer than c_P" is false once TIE acts
- status: CONFIRMED (constructed; `drills.py` "(proof)")
- severity: design (the claim in the argument; also doc)
- effort: one sentence ; blast radius: [BENCH-WITHDATA]'s stated property ; where: §The pick, "Why the structure gives it"
- body: "if [c_P] qualifies under B the pick is no dearer than it". Step 3 does not guarantee
  this. The pick is a TIE choice among the qualifiers within band of the cheapest, so it can be up
  to band(cheapest, pick) dearer than c_P. Construction: inc 100, cheapest cs 70, c_P 72, c3 74,
  every band 5, TIE prefers c3. c_P qualifies and the pick is c3 at 74, dearer than c_P. The bound
  that does hold is "no dearer than price(c_P) + band". The property ("matches or beats beyond
  noise") survives only if the model band is no wider than the measured noise. The argument should
  say so.

### SIM-3  One candidate set for blind and with-data compiles: false whenever the two incumbents differ outside the row's levels, and row 1's admission reads the rate-dependent incumbent
- status: CONFIRMED by text and code. smp20 under `prose` is a real instance of the admission split (harmless there). A LOSS instance is SUSPECTED: confirming it needs a census of PARKED+RESEED sites whose MARGIN choice flips between P and a bundle. That is a compile sweep of more than 50, not run here.
- severity: design
- effort: a paragraph plus a census line ; blast radius: the [BENCH-WITHDATA] property and row 1's condition ; where: §The pick 1-2; "Why the structure gives it"; "NOT covered"; §Staging "Row 1"
- body: step 1 says candidates are "built from site facts alone (no rate input), so a blind and a
  with-data compile of one site see ONE candidate set". But they are "the complete plans that differ
  from the INCUMBENT only at the row's levels", and step 2's incumbent is evaluated under the handed
  rates. Three things read r:
  - KEY's A-mass position.
  - M's alternative choice: MARGIN compares `a[].cost`, computed from `kit_set_mass(d->rate, ...)`
    (window.c :420-421, :472, :491; `d->rate = kit_byte_rate(art)` :991; MARGIN :669-684).
  - C-model's verify order.
  So inc_P and inc_B can differ at the alternative level (PARKED vs RESEED) or in verify order. A
  row whose levels exclude those gives c_P ∉ cand(inc_B).
  The text routes this case to "the NOT-covered census below". That paragraph defines only "sites no
  priced row ADMITS", but these sites ARE admitted. The closing claim "a with-data loss is therefore a
  broken (i)-(iv) ... never a trade" also misses this fifth cause.
  Real instance: row 1 admits "NONE alternatives whose default is a two-member stop". That condition
  reads the incumbent, a kit output under r, not a stated fact as D186's "a condition on stated
  facts" requires. smp20 is admitted blind (P: {X,x}) and NOT admitted with `prose` (incumbent '4',
  `witness.out`). One site therefore gets two different candidate sets and two different row
  memberships. It is harmless there, because '4' is prose's least at all 3,536 grid points.
  Fix: either make every priced row's levels include alternative and verify order, or state "one
  candidate set" only where inc_P = inc_B outside the levels. Name the differing-incumbent sites as
  their own census line under [BENCH-WITHDATA]. Phrase row 1's condition on stated facts (a NONE
  alternative whose core position 0 is a two-member set), not on "its default".

### SIM-4  Provenance stays at the seam, against D186 add. 2 on main ("leave the seam in span_pick stage 1")
- status: CONFIRMED (text vs ruling; code)
- severity: design
- effort: one stage-1 unit row plus an MF_SITE_ABI event ; blast radius: memfn.h, src/gen/memfn_sites.c, §What moves across ; where: §pcrec-side findings "The rate source"; §The designer/emitter split "What moves across"; §Owner rulings "For main"
- body: main 7f55a62f9's D186 add. 2 reads: "The provenance fields (`mf_prov.source`, the bundle
  'default' label, memfn.h) leave the seam in span_pick stage 1: the kit never sees the source."
  Rev 5 instead says "whether the field stays is main's call" and lists `mf_prov.source`'s future
  "For main". None of units 1a-1f removes the field, and "What moves across" says stage 1's only
  MF_SITE_ABI event is 1f.
  The fields are live today. `mf_prov` {source, bundle, digest, bytes, fidelity} rides
  `mf_analysis` on `mf_art_begin` (memfn.h :1213-1238; the cites :1212/:1224-1225 are off by one
  for the enum). pcrec fills them at memfn_sites.c :187-190, :599.
  Item 4 of my question (does the rule depend on the SOURCE?): the price, the qualifier test and
  rule 4 as written read only the table, its digest and any stated noise. No kit .c reads
  `source`; I grepped memfn/src for `PRIOR_AUTHORED|.source|->source|prov.` and got 0 hits. The
  band text, however, keys "no sampling term" on "an authored default, a `fidelity synthesized`
  bundle". Those are provenance facts, and `fidelity` and `bytes` are `mf_prov` fields the kit can
  still see.
  Fix: add a stage-1 unit (or put it in 1f's MF_SITE_ABI event) that removes source, bundle label
  and fidelity from the seam. Rephrase the band as "pcrec states no sampling noise", so the kit
  reads no provenance.

### SIM-5  The smp20 table's "pick" column and the with-data grid counts use a different arithmetic (band 0) from the design's own rule
- status: CONFIRMED (smp20.py :34-36, :97-101 vs §The pick 3-4)
- severity: doc
- effort: one sentence under the table ; blast radius: §Robustness, §The watched witness readings ; where: §Robustness table and "With data over the grid"
- body: smp20.py qualifies `p[c] < p[inc]` (band 0). The design's rule 4 says "Unpriced candidate
  (no card, or a card without noise): cannot qualify", and no stand-in carries noise. So the
  design's own rule keeps the incumbent at EVERY point. The smp20.py docstring says this; the design
  does not.
  The parentheticals "('/', 1.086x)" and "('4', 1.438x)" are band-0 picks at hit(PAIR) 40. Under
  the text's rule they are not picks at all.
  "With data ... log {X,x} 1,502, '/' 2,034; weblog '4' 3,438, {X,x} 98" are argmins (B's least).
  They equal the text's "B's cheapest qualifier" only at band 0. Label them "band 0, argmin".

### SIM-6  P is identified by an R-33-local hash, not by the digest the kit is handed
- status: CONFIRMED (sha256 prefix of the default table's ppm list joined by "," = `a322116b1b87f9f6`, r33_sim/collect.py :126)
- severity: doc
- effort: trivial ; blast radius: §Robustness ; where: §Robustness "PRIOR_AUTHORED (`a322116b1b87f9f6`)"
- body: §Robustness names P "PRIOR_AUTHORED (`a322116b1b87f9f6`)". That string is R-33 collect.py's
  own hash of the table. pcrec's digest, the one the kit is handed and its trace names (rev 5's
  rule), is `1822fb973b95a4da` (`witness.out`, quoted in §The watched witness). Two identities for
  one table in a design whose kit sees only the digest. Use the stamp digest.

### SIM-7  The price's verify_r orders positions by ascending mass; T-VERIFY's plan puts the run member first and compares the run as one T-CMP stretch
- status: SUSPECTED (structural mismatch, confirmed in text. The numeric effect is negligible on smp20, where every pass rate is at most 0.75 % and verify is about 2.51 per candidate either way. A site with a high-pass run member would show it; that needs the card values, so it can't be shown before stage 2.)
- severity: design (small)
- effort: one formula clause ; blast radius: priced rows' verify term ; where: §The pick price formula `verify_r`; §The tables T-VERIFY
- body: the formula sums cmp over "the other positions in ascending mass". T-VERIFY is "a DECLARED
  STEP LIST ... first step the run member" with C-bound, C-pin and C-run. smp20's real plan is
  `path mass+pin` with the run "/1234" compared by runcmp, not per position. The price therefore
  prices a verify plan that the plan does not run. Fix: price verify_r over T-VERIFY's own step list.

### SIM-8  Rule 4 is silent on an incumbent that reads a noiseless card
- status: CONFIRMED (text gap)
- severity: design (small)
- effort: one sentence ; blast radius: stage-2 partial card sets (for example SIMD-form cards measured before scalar noise) ; where: §The pick 4; band paragraph
- body: rule 4 makes a candidate reading "a card without noise" unable to qualify, and says
  "Unpriced incumbent: keep". It does not say whether an incumbent reading a noiseless card counts
  as unpriced. In that case band(inc, c) has an UNMEASURED term whenever the coefficients differ.
  smp20 example: inc reads find.byte/find.hit(PAIR); '/' reads memchr's. If the PAIR cards land
  without noise, '/' is "priced" and the band is undefined.
  Fix: "any card with a nonzero coefficient difference and no noise means no departure".

### SIM-9  §The shape mixes arms in one sentence
- status: CONFIRMED (counts.out)
- severity: doc
- effort: trivial ; where: §The shape `[rev3 R4]`
- body: "1,429 state PARKED + RESEED" is RTE only, but "of the 1,454 RESEED alternatives 740 ... 714"
  is RTE+DEF (1,429 + 25; 733 + 7; 696 + 18). The RTE-only split is 1,429: 733 / 696. Review r2 R4
  asked for counts split by arm.

## PROBED-AND-HELD

- smp20 prices, independent implementation (`mysim.out`) vs the design table: 24 prices at
  hit(PAIR) 20 plus 4 at hit(PAIR) 40, all EQUAL. Examples: P {X,x} 144,694 (166,634), '/'
  153,476, '3'/'4' 228,231; prose 168,871 (212,311) / 72,938 / 66,143 / 63,555; log 128,384
  (135,824) / 385,409 / 760,657 / 854,238; weblog 286,612 (434,532) / 1,225,432 / 441,512 / 302,235.
  Ratios 1.086x and 1.438x hold. The least per source holds.
- k*, exact: all 16 cells reproduce in rationals (1.382, 1.637, 2.146, 3.165; 1.291, 1.454, 1.781,
  2.434; 1.108, 1.088, 1.049, 0.971; 8x 0.742, 0.357, -0.413, -1.954, all under 1).
  - At k 2, the hit(PAIR) boundary is -28.8 at h1 5 and -9.86 at h1 10, so '/' wins at every
    hit(PAIR); it is 28.006 at h1 20 and 103.740 at h1 40. "28.0 / 103.7" holds.
  - Re-sweeping finer adds nothing. Prices are linear in k with only PAIR's slope, so the argmin is
    PAIR below k* and the cheapest one-member stop above it; no third winner can appear between
    grid points.
- DEF arm: '/' is P's cheapest one-member stop at every h1, with mass 4,154 below '1'-'4' at 7,476.
  "No move" holds; it is trivially true, because all one-member stops share byte and hit.
- With-data grid: 16 hit pairs x 221 k = 3,536 points. prose '4' 3,536; log {X,x} 1,502 / '/'
  2,034; weblog '4' 3,438 / {X,x} 98. All EQUAL (argmin, see SIM-5).
  - Not quoted: the blind P argmin over the same grid is '/' at 3,381 of 3,536 points (504 of 656 for
    k ≤ 3).
  - The stand-in point (k 2, hit 20/20) is in {X,x}'s minority region. The design's "the cards may
    land above k*" is honest; "P keeps {X,x}" is a single-point reading.
- Bundle rates from the re-made listings:
  - P: {x,X} 997 + 100 = 1,097; '/' 4,154.
  - prose: {x,X} 1,971 + 201 = 2,172; '/' 575; '4' 158. These rest on 137 / 40 / 11 counts out of
    69,462 bytes, which is noisy (Poisson about 30 % on '4'), but the incumbent and least are '4'
    regardless.
  - log: '/' 14,462 vs {x,X} 372.
  - weblog: '/' 51,754 vs {x,X} 7,396.
  All hold.
- Job 588 quotes: candidates 2,338 / 1,026, 1,388 / 0, 21,788 / 10,856 (t588tri_report.md :9); RTE/DEF
  1.58-4.03x (xcheck_588.tsv: search_short/real 1.578 ... throughput/random 4.028). Both hold.
- Populations, `counts.py` re-run on sweep.jsonl (identical): 1,742 / 1,767 PF sites; 1,429 / 291 / 22;
  1,454 = 740 + 714; A-floor 1,420 of 1,835 (1,397 of 1,800 RTE); 371 of 371 OFS sites with no kind.
  All hold.
  - Probed: 186 RTE + 14 DEF pre-check parts carry wfA ends but `alts` = None. counts.py's zip drops
    them. All are NONE/A-mass, so the quoted RESEED/A-floor counts are unaffected.
- Drill (i), never-qualifying candidate: cannot enter the qualifier set, the anchor or the tie set.
  "A never-qualifying candidate cannot move the pick" HOLDS. The pairwise quadrature band is
  per-pair, so adding a candidate changes no existing band.
- Drill (iii):
  - A candidate cheapest but within band of the incumbent (c 90, band 12) does not qualify. A dearer
    qualifier with a narrow band (q 93, band 4) is picked (`drills.out`). This is consistent with
    "only qualifiers" and the with-data bound pick ≤ inc still holds.
  - "Two qualifiers within band of each other, one within band of the incumbent" cannot occur: a
    qualifier is beyond band(inc, c) by definition. The incumbent never enters the tie set.
- Drill (iv):
  - Unpriced candidate: cannot qualify. No rates: keep, with the NONE answer, consistent with D186
    add. 2's member-count ranking (kit_byte_rate NULL, presence.c :48-56).
  - Unpriced incumbent: keep. A noiseless card is held by rule 4 except on the incumbent side
    (SIM-8).
  - Utf8 compiles get rate-source row 3 (none), so they keep their pick.
- Drill (v): see SIM-3. Where the incumbents agree outside the levels, the bound pick ≤ price(inc_B) ≤
  price(c_P) + band(inc_B, c_P) holds.
- The rule against D186 add. 2 (item 4): the kit receives one table plus its digest, or none, and the
  pick reads nothing else. HOLDS in the formula. Grep of memfn/src: no reader of `mf_prov.source`.
  The seam itself does not follow the ruling (SIM-4).
- witness.sh: 16 compiles reproduce `witness.out` byte for byte (stamps included).

## Text vs script divergences

My text-only implementation (`mysim.py`) against smp20.py / smp20.out: every printed number is
equal. The divergences are in the rule each one encodes:

1. Qualifier test. Text: `price(inc) - price(c)` exceeds their band, and a noiseless card cannot
   qualify (rule 4). Script: `p[c] < p[inc]` (band 0). The script's docstring declares this; the
   design's table and grid text do not (SIM-5).
2. Ties. Text: qualifiers within band of the cheapest go to TIE's rows. Script: `min((price, offset))`,
   the lowest offset at equal price; no tie set.
3. Rounding. Text: "the price is rounded to an integer at its end", so comparisons are on integers.
   Script: compares exact rationals and rounds only for printing. No smp20 outcome differs; P's
   '1'-'4' are exactly equal either way.
4. Verify. Both price cmp over ALL other positions in ascending mass, flat cmp (cmp0 = cmp½ = 2.5).
   Neither follows T-VERIFY's run-member-first step list or C-bound (SIM-7).
5. Incumbent. Text step 2: KEY/M/TIE evaluated under r. Script: READ from witness.out, not
   recomputed. They agree on smp20 because the compile is the incumbent. The DEF+prose incumbent ('/'
   and '4') is "not one modelled stop", so it is unpriced in the script and unmentioned in the text's
   table.
6. Grid. Text: "With data over the grid ... (3,536 points)" beside "the target is B's cheapest
   QUALIFIER". Script: B's argmin with a position tie-break. They agree only at band 0 (SIM-5).
7. Boundary listing. Script prints 4x/h1 40 as "departs at every k >= 1 (k* 0.9714)". Text lists
   0.971 among the "{X,x} kept for k < k*" values and says "under 1" only for the 8x row.
8. DEF arm. Script filters PAIR and prices the five one-member stops; text "no move" is the same
   reading.
9. Script omits walk and Horspool lines and SIMD-form cards (declared). The text table does too.
   Consistent.
