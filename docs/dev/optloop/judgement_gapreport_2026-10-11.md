**LANE DRAFT (gaprep3, sonnet, 2026-10-11) - the manager replaces or extends this file.** It carries the
owner mapping, the caveats, the relay questions and "for the manager" list; the ruling is the manager's.
No timing was taken on this box; every number is the bench's, read through `gapreport.sh`.

**Inputs and the CROSS-WINDOW rule.** pcrec is b8337c33 (abi 74, [B135] state 3, landing reports of
2026-10-11). No window has both pcrec b8337c33 and peers, so the peers come from the latest report that
holds them, per set (`--peer-group`, new): capability from `2026-10-08 ...first-255bcdd8` (the only
window that ran the full roster at capability@0.2), bounded / email-specimen / litrun / loglines /
syntax / utf8 from the 2026-10-05 `round1-c4c70f2c` reports, whose peer rows are the September
measurements (jit 09-02..09-28, rust 09-20..09-26). altwide has no b8337c33 record, so it is **absent**
(30 cells; the 10-05 WIDE-ALT breadth of 31 is therefore not a closure).

Drift bounds actually available:

- pcrec side: the bench's own control, 7388f1c0 vs b8337c33, median 1.000, p5-p95 0.995-1.007 over 422
  cells (O-97).
- peer side (this lane's measurement, from the two published capability reports): jit, interp, rust, re2
  and oniguruma on the 63 capability cells whose subject count is unchanged between the 09-17 and 10-08
  windows (identical subjects, three weeks apart): jit median 0.999 (p5-p95 0.924-1.052), interp 0.999
  (0.951-1.021), rust 1.008 (0.976-1.079), re2 1.010 (0.986-1.031), onig 1.000 (0.993-1.010).
- no peer control exists for the September peers (the sentinel set carries jit only from 2026-10-10).

`gapconfig` bands (x1.10 tier A, x1.15 tier B) cover the jit p5-p95 spread; no gap inside those bands is
claimed. 30 of the 80 trailing cells are under x1.5 and 3 under x1.2, all synthetic-leaning
(syntax 48 of 80), so they are the ones a peer refresh could still move.

**The one subject-set break.** capability went 0.1 -> 0.2 between the 10-05 and 10-08 reports: the
throughput regime grew from 3 to 11 subjects (eight [B125] hazard subjects: evil/trim match and
near-miss, tail-* 1 MiB prose). Set-grain medians sum over subjects, so a capability throughput ratio
at 10-05 and now are over different bytes. The Movement section (9.1) therefore reports 17 capability
cells as SUBJECTS-CHANGED and makes no claim about them; section 9.2 compares b8337c33 against the
255bcdd8 window instead (same version, same peers), capability only.

**Headline counts (vs jit / best non-SIMD peer / best peer incl. rust)**: trail 80 / 87 / 113, lead 476 /
455 / 412, level 18 / 32 / 49, of 574 cells. The 10-05 instance read 515 / 20 / 96 of 631 (different
population: altwide gone, capability 0.2 added). 73 of the 80 trailing cells have pcre2-interp slower
than pcrec, so jit is winning on code generation or SIMD, not on a mechanism pcrec lacks.

**Ranked groups, owner row, algorithmic evidence** (mechanical order from section 2, reordering left to
the manager):

| # | group | worst cell | scalar peer also beats pcrec? | owner (grep of plan.md, 2026-10-11) |
|---|---|---|---|---|
| 1 | START-SET (14 cells) | capability quoted-delim x3.79 jit; json-constant x9.04 rust (re2 only x1.14); utf8 asr-b-ascii x5.05 rust; loglines stack-frame x2.75 | weak: re2 x1.14 json-constant, re2-longest x1.65 dbnames | [OPT-FIRSTSET] (started; stages 0-3 landed, remains the round gate and K90/K91 retry slot under [START-DENSE]); [OPT-VMSEED] (not-started, unclear whether stage 2 discharged it); ipv6-class: [REQ-HANDOFF-L1] (built, not merged, waits kit R-15). CORRECTION (session 108, from lossreview/dfa.md §2/§6): stack-frame is NOT an L1 mover (L1's census does not move it; its loss is HIT-RESTART, the `a` run gate after set-leads, owner memfn R4d + an ofsskip body row) |
| 2 | CI (11) | capability union-select **x9.49 jit** (unchanged since 255bcdd8); slack-webhook x2.25; syntax mod-i/mod-r x1.81; utf8 ci-sigma x3.43 rust | re2-longest x1.33 on union-select only | [OPT-LITSCAN] S4 (the caseless run shape; waf_attribution.md names union-select its one customer); [WORD-FOLD] (not-started) |
| 3 | ANCH-ATTEMPT (2, **NEW**) | capability wild-datetime-moment-iso8601 **x10.7 jit, x39.8 re2**; validator-email-owasp x7.22 jit | yes (re2, x39.8 on moment) | **NEW, no row.** Both are fully anchored attempt-scan artifacts that trailed nothing at 10-05; they appear only on capability@0.2 (set-grain 46-69 us vs jit 6.4 us), i.e. on the eight added hazard subjects. Same at 255bcdd8, so not a b8337c33 regression. Needs the per-subject split before a row (relay Q2) |
| 4 | U8-PICK (10, utf8) | lit-sharp-s x10.5 rust (x10.4 re2); lit-offset-at-head x8.0 re2; lit-1ch-4b x2.9 re2 | yes | [U8-PICK] (started; step 0 done, the authored-vs-generated prior question is open for Frank). pcrec leads jit on all 137 utf8 cells |
| 5 | CARET (2) | capability concat-sqli x4.80 re2 | yes (re2) | [OPT-ATTEMPT-SPLIT], [ENG-ABS-CARET] (both not-started) |
| - | LKA (10) | syntax lka-pos / lka-verb x2.98 jit | no (interp slower) | [OPT-HYB-RESEED-XCALL] (held), [CTX-PREFILTER] (not-started) |
| - | DENSE (15) | syntax cls-fold-pair x1.68, keyword-prefix-order x1.59 jit; x2.39 rust | rust only | no dedicated row (x1.3-1.7); **NEW if wanted** |
| - | BACKTRACK (11) | syntax mod-j-uc x1.59 jit | no | none; FUNDAMENTAL (D119) |
| - | CTX (7) | bounded ctx-* x1.6 jit, x7.6 rust; level-context closed vs jit (x3.83 -> x0.76), still x2.09 rust | rust only | [OPT-VMLIT] trigger, [CTX-PREFILTER], [ENG-TACTICS] |
| - | SEL-LIT (4, litrun) | lit-l40 x2.42 jit | no (litrun has no scalar peer) | [SEL-COST], [OPT-VMLIT] |
| - | BCLS (6) | bounded line-80 x2.34 jit | rust ns-scale only | [OPT-NEG] (not-started) |
| - | CALL-FLOOR, ENDWIN-ENC | +3.2 / +6.7 ns per call | - | null scale, nothing filed (D144 addendum 1) |

**SIMD-attributable, kept apart (section 8)**: SCAN-SIMD 20 cells (litrun alt-foo-tails x8.20 jit,
capability altorder-foo-foobar x4.04, file-ext-order x3.00, syntax mod-s / cls-v / esc-octal-0 / anc-m-*
x2.0-2.6; rust x6.90 / x4.46 on the first two); WIDE-ALT 1 cell (utf8 alt-distinct-lead x7.35 rust;
altwide itself not re-run); and **11 cells where only rust is ahead** (loglines level-context x2.09,
utf8 alt-nearmiss x1.85, lit-cyr-run x1.59, loglines hex32-id x1.48, ipv6 x1.42, syntax cls-i-class x1.40,
...). Owners: [OPT-SIMD] (started), [MEMFN], [SIMD-META] (not-started). pcre2-jit is itself a SIMD-using
peer on SCAN-SIMD cells, so those 20 are SIMD-attributable only by cause, not by the peer-role test.

**Movement since 10-05 (sections 9.1 and 9.2)**, by cause:

- CLOSED or gone: NULLABLE-ANCH (x5.98 jit / x1081 re2 -> 0; [NULLABLE-ANCH] landed abi 68); K82-AT-PIN
  (cured at abi 60; the userpass cell now x0.12); INNER-LIT (x23.7 -> 0); loglines level-context vs jit
  (x3.83 -> x0.76); capability aws-access-key-id (x43.9 -> x0.61, but that is a SUBJECTS-CHANGED cell, and
  the 255bcdd8 window already had it behind us: START-SET at 255bcdd8 is the same six cells, worst x3.88).
  **REVEND-TAIL** (new group name, 5 capability tail cells, re2 x77.7 / x7240 and rust x24 at 255bcdd8)
  is closed at b8337c33: that is [OPT-REVEND]'s doing and 9.2's only changed row.
- SHRANK: START-SET non-capability cells (stack-frame x4.85 -> x2.75, litrun aws x5.31 -> x2.59);
  syntax mod-i / mod-r x3.9 -> x1.81 and cls-fold-pair x3.05 -> x1.68 (the K82 handoff); lkb-neg
  x3.47 -> x2.00; SEL-LIT l40 x3.20 -> x2.42; bounded ctx-* short-subject x1.2 -> x1.1.
- GREW: syntax bak-2 x1.32 -> x1.55 (BACKTRACK, within the peer drift band). Capability union-select
  x7.74 -> x9.49 is SUBJECTS-CHANGED and flat across 255bcdd8 -> b8337c33, so it is not a regression.
- UNCHANGED: SCAN-SIMD (x8.20 alt-foo-tails), CARET, BCLS, bounded ctx-* vs rust, U8-PICK ceiling
  (x15.7 -> x10.5 is the one utf8 shrink; pcrec side changed, rust is September's).
- START-LANDING and LITSCAN S4: neither moves a vs-jit verdict in this view beyond the rows above; the
  bench's pcrec-vs-pcrec reading (O-97, 298 movers) is where their effect lives.

**Caveats.**

1. Cross-window: see above. The peers for six of seven sets are 2-6 weeks older than pcrec.
2. altwide absent; the 10-05 31-cell WIDE-ALT group is mostly not re-measured.
3. Stamps (and therefore the cause assignments' stamp reads) were compiled by this worktree's build at
   main e878687b, abi 74, same abi as the pin but not the pin commit. Section 5 diffs against the
   2026-10-03 census (abi 55) and is clutter (307 "differ"); `stamps_e878687b.json` is the baseline to
   use next time.
4. The first-run `causes.tsv` left four capability cells unassigned; this lane assigned them (hex8-bounded
   -> FS-DFA, utf8-lead-no-cont -> LKA, moment-iso8601 and email-owasp -> new ANCH-ATTEMPT) and added
   REVEND-TAIL for the 255bcdd8 comparison. These are judgements, the manager's to overrule.
5. "Best peer" includes rust, a NO-class `captures_at`-per-call driver (I-100); vectorscan is excluded.
6. litrun has no scalar peer; email-specimen is 5 cells; 6 utf8 and 15 syntax patterns have no pcrec
   record (section 4).
7. Instrument changes this instance (documented in gapreport/CLAUDE.md): `--peer-group`, `extract.py
   --peers`, `--prev-dir` / `extras.py`, new sections 7-9. `--check` fixture re-blessed (adds sections 7
   and 8 only). The default `--remote` (tailnet address) does not answer from this box; pass
   `--remote duxevents@192.168.1.100`.

**Relay questions for the bench (pcrecdev2).**

1. Can the next window re-run jit + interp (cheapest) on bounded, loglines, syntax, utf8, litrun and
   email-specimen at the current versions, so the September peers stop being the comparison? Without it
   every sub-x1.5 trailing cell (30) stays inside an unquantified drift.
2. Per-subject split of capability@0.2 `wild-datetime-moment-iso8601` and `wild-validator-email-owasp`
   throughput: which of the eight hazard subjects carries the 46-69 us (jit 6.4 us)? Same for
   `wild-waf-crs-942270-union-select`.
3. altwide@0.3 at b8337c33 (jit and rust rows already exist from 10-02).
4. Can the sentinel jit row be summarised across 10-10..11 so a peer-drift number exists for the next
   gap report, and be kept in every window?
5. Would the capability report carry a "0.1 subjects only" set-grain median, to keep trend continuity
   across the 0.1 -> 0.2 break?

**For the manager (calls this report needs).**

a. Order: accept the mechanical order, or re-rank (the first-instance practice was to rank by what an
   owner row can act on: START-SET, CI, U8-PICK, CARET above ANCH-ATTEMPT, whose cause is unknown).
b. ANCH-ATTEMPT: a NEW group with no owner and no per-subject evidence. File a row now, or hold for relay
   Q2? It is also the largest single jit ratio (x10.7) in the table.
c. CI / union-select x9.49 jit has not moved across three pins. Is S4's caseless shape the next round's
   item, or does [WORD-FOLD] go first?
d. START-SET's remainder is mostly capability quoted-delim x3.79 and the syntax asr-* family x2.4: is it
   [OPT-VMSEED] (decide whether stage 2 discharged it), [START-DENSE], or both?
e. U8-PICK still has ten cells behind re2/rust: the open prior question for Frank gates it.
f. DENSE (15 cells, <= x1.68) and BCLS have no row: apply the one-pass loss rule (one bounded survey, then
   accept), or leave unfiled?
g. SIMD list (section 8) is ready for the SIMD thread; ask the bench for the altwide refresh when that
   thread opens.
h. Whether to adopt `--peer-group` / sections 7-9 as the instrument going forward and bless the fixture
   change.

**MANAGER CALLS (2026-10-11, session 107).** Priority proposal goes to Frank; the calls below are the manager's.

a. RE-RANKED by what an owner row can act on, then size: (1) CI / union-select x9.49 (stuck across three pins);
   (2) START-SET remainder (quoted-delim x3.79, syntax asr-* x2.4); (3) U8-PICK (gated on Frank's prior
   question); (4) ANCH-ATTEMPT (largest single ratio, cause unknown); (5) CARET. Every item waits behind
   [REQ-HANDOFF-L1] and Frank's queued [PRIOR-COST-UNIFY] where it touches their sites (D153 remodel-first).
b. ANCH-ATTEMPT: HOLD; relay Q2 (per-subject split) rides I-147. A row is filed when the split names a cause.
c. CI: [WORD-FOLD] is already a member of [OPT-LITSCAN] S4, so there is no ordering choice. The next step is a
   read-only attribution of why C3's measured -0.4..-0.52 ns/B did not move union-select's verdict against jit
   (per-subject split, relay Q2), before any build.
d. START-SET remainder: [OPT-VMSEED] (stage 2's VM hat did not build the row's own necessary-run seed, so it
   is NOT discharged); [START-DENSE] stays gated on its own trigger.
e. U8-PICK: put to Frank again with the report.
f. DENSE (<= x1.68) and BCLS: leave UNFILED (near-noise sizes, cross-window data; revisit on a same-window peer run).
g. SIMD list: held for the SIMD thread; altwide refresh asked when it opens.
h. `--peer-group`, `--prev-dir` and sections 7-9 ADOPTED; the fixture change blessed.
NEXT INSTANCE: ask the bench for a same-window peer run at post-L1 main (relay Q1), so the next report is not cross-window.
