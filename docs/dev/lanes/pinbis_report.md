# pinbis report: what moved the fd-pres-pick differ pin

## Counts
Corpus patterns whose `c-default` output differs under `--memfn=no-fd-pres-pick` (job 320-main-pinbis-count, each commit's own corpus, `emit_sweep.py` arm, ref-bin = bin):

| commit | byte | utf8 |
|---|---|---|
| 99f310c49 (pin set) | 167 | 231 |
| 657e23231^1 | 171 | 235 |
| 657e23231 (R-30) | 171 | 235 |
| dc6a40dfb (P1 merge) | 142 | 224 |
| 564db08c5 (main) | 142 | 224 |

R-30 moved nothing. The whole drop (byte -29, utf8 -11) is in 657e23231..dc6a40dfb. The +4 (99f310c49 -> 657e23231^1) is a corpus addition, not explained further (not cheap, not needed).

## Cause
Re-run by hand (scratch pinbis2/drv.py, importing emit_sweep's own corpus enumeration and compile helpers), prebuilt 657e232 and dc6a40d compilers, ONE fixed population (dc6a40d's corpus, 5,014 distinct patterns), default vs `--memfn=no-fd-pres-pick`:
- byte: 177 differ at 657e232, 142 at dc6a40d; 35 LEFT the differing set, 0 joined.
- utf8: 242 -> 224; 18 left, 0 joined.
- 142/224 at dc6a40d reproduce the job exactly. The job's net -29/-11 is the 35/18 leavers minus 6/7 patterns that joined the corpus between the two commits (they differ at 657e232, so they inflate its count on the larger corpus; on the job's smaller 657e232 corpus they were absent).

What changed for the leavers: all 35 byte and all 18 utf8 stamp `_DFA_SCAN "unanchored"` at 657e232 and `_DFA_SCAN "landmark-walk"` at dc6a40d (P1's LOCATE row, D184). At dc6a40d the default output is byte-identical with and without the deny for every one, so the deny no longer reaches them: the landmark walk replaces the presence pick there. That is 35/35 (100%) of the byte leavers and 18/18 of the utf8 leavers; nothing else moved.

Examples (byte): `a+b`, `a++c`, `ab*c`, `a(?:b|c)*d`, `a+xyz`, `[0-9]+ABCDEFGHI` (and the 20 siblings of that shape), `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`, `(?:a+)+b`, `(?>a+)b`. All are an unbounded-run-then-landmark shape, the shape P1's landmark walk is for.

Verdict: INTENDED consequence of P1 (landmark walk takes patterns the pick served). No lost reach; the stop rule did not trigger.

## Proposed pins
Population check: the floor cells in `scripts/emit_sweep.py` apply when `full_population` (no `--no-corpus`/`--limit`/`--every`), over corpus plus any `--patterns-file` rows. The pin job reads the corpus alone: 142 / 224. The kit's identity sweep adds three pattern files (`spanpick_bench_patterns.txt`, scratch `p588.txt`, `pzzz.txt`): measured by me at 564db08 over corpus+files, byte 154 (matches the kit's 154) and utf8 244. The floor is a `<` check, so the corpus-only value is valid for both populations. Propose the corpus values:

    ("byte", "--memfn=no-fd-pres-pick", "c-default"): (142, 0, b"a.{1,5}z"),    # P1 re-pin (was 167): the landmark walk (D184) takes 35 patterns the pick served (29 net of corpus growth)
    ("utf8", "--memfn=no-fd-pres-pick", "c-default"): (224, 0, b"a.{1,5}z"),    # P1 re-pin (was 231): the landmark walk (D184) takes 18 patterns the pick served (11 net)

(Optionally keep floors from rising with kit-local pattern files: 154/244 are those files' population and would be wrong as pins.)

## STATE AT HANDOFF
- OWED: none.
- Done: counts, cause, verdict, proposed pins. emit_sweep.py NOT edited (main's re-pin).
- Scratch: /var/tmp/pcrec-pcrec/scratch/pinbis2/ (drv.py, drv2.py, an.py, res.pkl).
- Prebuilt trees pinbis-{99f310c,ee0dc8a,657e232,dc6a40d,564db08} removed via wtprune.
- Rulings file pinbis_rulings.md: no entries applied.
