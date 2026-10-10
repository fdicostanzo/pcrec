# 2026-10-09 — D6 panel on [START-LANDING] (docs/design/start_landing.md, lane landdes)

Three read-only critics, session 102: **slcrit1** (opus) exactness against libpcre2;
**slcrit2** (sonnet) table fit, checks, readers and census; **slcrit3** (opus)
generality, family and unlocks. Dispositions are the manager's and are applied by
the revision lane. Status is ACCEPTED unless marked otherwise.

## slcrit3 — generality / family / unlocks (SL-G1..G9)

| id | sev | finding | disposition |
|---|---|---|---|
| SL-G1 | HIGH | The §2.5 utf8 guard's restart is QUADRATIC per call on runs of ill-formed lead bytes. On utf8 `.` over `C3`×k `a`, every restart lands, scans to e and fires again: k=4096 costs 8.4M forward byte-steps where today's is ~k. The identity twins compare answers, not work, and the timing used well-formed subjects, so neither could see it. A general LINEAR form removes the re-entry: on a decode failure, start = the first well-formed character start at or after L (proof sketch in the finding: any well-formed p in (L,s) is dead, contradicting finality, or accepting, contradicting leftmostness). The guard is the ⊥ rule (ucp_design) applied once, not a RAISE edge (E5 is NEXT→VERIFIER). | ACCEPT: the skip form; re-twin in assert mode; keep the no-guard control; add a timing control (64 KiB of `C3` then `a`, guarded vs today) that must read linear |
| SL-G2 | MED | Λ.2, Λ.3 and the guard spell UTF-8 as literals (`0x80..0xBF`, `depth >= 3`, "a byte ≥ 0x80", multibyte keyed on `has_entry(DECODE)`), a sixth spelling of a rule the seam owns (`PcrecEnc.start_cls`, `onebyte_max`). | ACCEPT: state Λ.2/Λ.3/the guard over `start_cls`/`onebyte_max`, with depth bounded by the walk; say whether K50's wrap gate already implies Λ.2, checked not assumed. Also feeds [ENC-DATA] |
| SL-G3 | MED | `fixed_width` is kset_walk's own union-frontier walk; the general fact is the machine's BYTE WIDTH INTERVAL [bmin, bmax] (W = bmin==bmax), the fifth member of a width family (`pcrec_minw`, cwmin/cwmax, endwin's W, this). The shared object is a frontier ITERATOR with per-depth flags, not a helper with a mode. | ACCEPT: one iterator; [bmin, bmax] as its output |
| SL-G4 | MED | The RECOVER hand's CT_END/CT_SEED duplicate LR-G2's product vocabulary: VERIFIER→RECOVER is the filed "exists" mask, and rev-end's seed is the "window" mask. | ACCEPT: spell the hand as product masks, giving §7.5's "exists" mask its first real producer; keep the mandatory hand and abort-on-0 |
| SL-G5 | LOW | RECOVER is a 2×3 grid (start side vs end side × no / bounded / unbounded evidence), not a ranked list of four; `pinned` and `landing` are one action ("start = the start-side record"). | ACCEPT: write the grid into §10 and the listing descs; do NOT merge rows (pinned's stamps and deny stay) |
| SL-G6 | — | Q1 judgment: Λ's one character is DERIVED, not chosen. Past k=1 a criterion that does not read F's state ids is unsound (`ab` on "aab": landing 0, true start 1); the k>1 condition IS die-together. | ACCEPT: state the argument in §2.3 |
| SL-G7 | — | Q2: the guard, in the skip form. Q3: the hand, in SL-G4's vocabulary. Q4: emw first by DOMINANCE (identical answers on the overlap, strictly smaller `.needs`), not by timing. Q5: file rev-end-width and label its 10% threshold. | ACCEPT as the leanings put to Frank |
| SL-G8 | LOW | Constants: no tuning constant reaches the artifact (state it). Label the encoding literals (SL-G2), the two trigger thresholds and the instrument caps. | ACCEPT |
| SL-G9 | UNLOCKS | U1 FIXED-MARGIN CAPTURES: groups whose boundaries sit at fixed byte offsets from s or e on every path (`"([^"]*)"`, `<(\w+)>`, `(\d{4})-(\d{2})-(\d{2})`) let an EXACT hybrid `report` arithmetic captures with no VM run; the degenerate case of [CAP-EARLY-STOP]; D142's family. U2: SL-G3's bmax is [OPT-ENDWIN-ENC]'s missing fact (W1 under utf8). U3: rev-end-width. U4: §7.6 candidate-verify reuses B2's record site, and SL-G1's skip is its DECODE-verifier instance. No material unlock for the VM hat, ATTEMPT, or [FINDALL-REENTRY]. | FILE U1 (on [CAP-EARLY-STOP] / D142, with D142's trigger restricted to an all-fixed-margin census) and U2 (on [OPT-ENDWIN-ENC]); U3/U4 as filed |

## slcrit1 — exactness

PENDING.

## slcrit2 — fit / checks / readers / census

PENDING.
