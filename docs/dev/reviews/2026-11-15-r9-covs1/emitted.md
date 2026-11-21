# EMITTED — covs1

## Findings


### EMITTED-1 — `hex32-id` (and `hex32`) artifacts grow in machine code: `.text` x2.1 / x1.8 (hex32-id), x1.3 (hex32)
CONFIRMED (size). Repro: `kit/cmp.sh OUT '\b[0-9a-f]{32}\b' [-e utf8]`, then `gcc -O2 -std=gnu11 -c rx.c; size -A rx.o` (gcc 15, this box).
Per bench mover, BASE -> SUBJECT (C bytes | `.text` | `size` text+rodata | total):
| mover | enc | C | .text | text+ro | total |
|---|---|---|---|---|---|
| lit-l31 | byte | 32965 -> 21993 | 1592 -> 1400 | 8815 -> 5282 | 9039 -> 5506 |
| lit-l31 | utf8 | 36923 -> 25735 | 3099 -> 2331 | 10430 -> 6305 | 10654 -> 6529 |
| hex32 | byte | 19993 -> 18915 | 1528 -> **1960** | 3076 -> 2903 | 3300 -> 3127 |
| hex32 | utf8 | 23737 -> 21583 | 3131 -> **4219** | 4771 -> **4886** | 4995 -> **5110** |
| dig-exact-32 | byte | 16893 -> 14021 | 1496 -> **1624** | 2518 -> 2049 | 2742 -> 2273 |
| dig-exact-32 | utf8 | 20637 -> 17765 | 3067 -> **3227** | 4149 -> 3632 | 4373 -> 3856 |
| hex32-id | byte | 18852 -> **18891** | 1512 -> **3176** | 3809 -> **4683** | 4033 -> **4907** |
| hex32-id | utf8 | 22596 -> 21559 | 2835 -> **5139** | 5216 -> **6402** | 5440 -> **6626** |
(`litrun.rxt:1204`/`:1320` behave like lit-l31: total 9039 -> 5506 / 9528 -> 5739 byte.)
Cause: the DFA tables (rodata) are replaced by a fully unrolled 32-position class test plus both `\b` neighbour tests inside one statement expression (SUBJECT `rx.c`: `rx_mf1_s[rx_mf1_c + 0..31]` each a two-range compare); the class-heavy movers trade table bytes for instruction bytes. Literal movers shrink everywhere.
Expected? The design (§7) asks for size beside each timing and names D198 (f)'s cold-artifact risk; it does not predict the direction. This is the input for that regime: hex32-id is the one mover whose WHOLE object grows (+22% total, `.text` x2.1 byte / x1.8 utf8), and the cold-artifact timing should include it explicitly. Effort: none now (measure at re-timing); blast radius: class-run covers k ~ 24..32 (the 18 k = 1 gains all shrink, `.text` 3059..8357 -> 2209..3412).

### EMITTED-2 — the class-run movers lose 3x-10x on dense near-miss text (verify fails late, the window advances by 1)
CONFIRMED (speed; micro, indicative only: one box, load average 2.3-5.5 from other work, same gcc 15 -O2 for both trees, 20 scans of a 1 MiB subject, no hits in either tree). Driver `emitted/bin/tdrv.c`, binaries `emitted/speed/<mover>-{base,subj}`; ns/byte BASE -> SUBJECT:
| mover (byte) | 'z'*n (miss) | 30 digits + `g`, repeated | 31 digits + `g` | 31 hex + `g` | 15 hex + `g` |
|---|---|---|---|---|---|
| dig-exact-32 | 0.20 -> 0.18 | 0.39 -> **3.4 / 5.0** (two runs) | 0.42 -> **3.4 / 5.5** | 0.32 -> **1.03** | 0.36 -> **1.30** |
| hex32 | 0.19 -> 0.06 | 0.56 -> **2.01** | 0.53 -> 0.06 | 0.52 -> 0.07 | 0.45 -> 0.06 |
| hex32-id | 0.19 -> 0.06 | 1.15 -> 0.98 | 1.10 -> 0.06 | 1.10 -> 0.06 | 1.11 -> 0.06 |
| lit-l31 | 3.8 -> 4.1 | (31-literal near miss + X: 0.12 -> 0.13; period-30 run: 0.13 -> 0.13) | | | |
Cause (SUBJECT `mv/dig-exact-32-byte/subj/rx.c:69`): the cover form finds a class byte, then tests positions 1..31 in one `&&` chain; on a failure it does `rx_mf1_c` + 1 (dig-exact-32), or + `rx_mf1_sh[b]` = 1 when the probe byte at `c + 31` is in the class (hex32's skip-probe form). In a run of m < 32 class bytes every start in the run re-tests up to m bytes: O(k) work per byte, k = 32, against BASE's one DFA step per byte. Stage 1 doubles the worst case k (24 -> 32) for every cover form that restarts this way.
Against the rulings: D198 Consequences and cover_cap.md §7 name a near-miss regime in the re-timing; this is a concrete witness for that cell (dig-exact-32 in digit-dense text, e.g. long numeric ids / phone/card numbers of 30-31 digits, is the bad case; hex32 in digit-only runs). Blast radius: class-run covers k ~ 25..32 (the four bench movers bar lit-l31). Effort: kit side (D146/D157: pcrec states facts; a restart after the failing position when every position's set is the same class, i.e. skip to fail+1, would make it linear) or route by measurement at re-timing. SUSPECTED at bench scale until the §7 near-miss cell runs.

## PROBED-AND-HELD
Compiles used: about 470 (cap 700). Kit: `kit/cmp.sh`, `kit/ans.sh` (libpcre2 10.46, every startoffset + find-all), my generators `emitted/bin/gen.py` (33 adversarial subjects per pattern: n-1/n/n+1, near miss at the last position, match at the end, adjacent and overlapping matches, `\n` endings, `é`/`€` neighbours, `\b` neighbours `g`/`_`/`0`/`-`) and `emitted/bin/gen2.py` (all 259 strings of length 0..3 over `{a,0,-,A,space,b}` + 16 extra with `é`, `\n`, `ﬀ`).
- (a) MOVERS, answers: the 6 movers (lit-l31, hex32, dig-exact-32, hex32-id, litrun.rxt:1204, :1320) x byte/utf8 all route `cover` and answer like libpcre2 on all 33 subjects, plain pcrec AND through the kit-proof harness lever (5 re-runs). The 18 k = 1 gains (10 patterns, `-{0,}?(?<!\W)-` and `\W*(?<!\W)\w` byte only, both stay `unanchored` under utf8 as §2 says) all move to `cover`, and all answer like libpcre2 on 275 subjects each, plus `-i` for `a*\bA`, `[a-c]*\ba`: 0 DIFF.
- (a) new covers k 25..32 and variants, 0 DIFF across 65 patterns: `a{25}`, `[ab]{26}`, `\w{27}`, caseless 28-literal, `[^\n]{29}`, `.{30}`, `[a-z]{30}\b`, `(?<![a-z])[a-z]{31}`, `ab{30}c`, `x{31}(?:y|yz)`, `a{32}|a{32}b`, `a\z\W|b{32}`, `a{30}(?:b|c\z\W)`, `\b-[0-9]{30}`, `\B-[0-9]{30}\B`, `\B\d{32}`, `\d{32}\B`, `(?<=x)`/`(?<!x)` contexts, `(?<!\d)\d{32}(?!\d)`, `\d{28}(?=x)`, `\b\d{25}\b` (both enc), `(?m)[0-9a-f]{32}$`, `-fno-rev-end` `\d{32}\z` and `(?m)\d{30}$` (utf8) and `\d{31}(?m:$)`, `\d{30}\n`, `(?i)[k-s]{32}`, utf8 multi-byte covers `é{16}`, `[é-ê]{16}`, `[é-ê]{8}\w{16}`, `[\x{100}-\x{7ff}]{16}`, `\w{32}` utf8; and non-cover neighbours (`$`/`\z`/`\Z` rev-end, `^`/`\G` attempt, utf8 `.{32}`, `é{25}`, `€{26}`, caseless utf8 literals) also 0 DIFF.
- (b) NON-MOVERS byte identity (abi lines dropped), both encodings: 67 + 51 random/targeted corpus patterns (seeds 1115, 20261115) + 8 reclassified shapes = 252 artifact pairs. Every pair byte-identical except the predicted movers it hit (`(?i)permission is hereby granted` byte only, §6 "outside the population"; `\d*(?<=a)\w`, `\d{0,}?\B-` from the k = 1 list). Covers that already existed (19 + 25 compiles: `ab|abc|ad`, `a*?a`, `(?:S(?i:ab)|(?i:sab))`, ...) are identical. Declines held identical: C1 captures `\b([0-9a-f]{32})\b`, `(ab){300}`, `(a)\1{31}`; C15 k > 32 `[0-9a-f]{33}`, `\d{40}`, `a{100}`, `[0-9a-f]{64}`, `\b[0-9a-f]{40}\b`, uuid, `a{40}(?:b|cc)`, `a{30}(?:b{30}c|d)`, `[a-z]{33}\b`, `x{32}(?:y|yz)`; machine-inexact `(?:ab|cd){16}`/`{20}`, `a[xy]c|b[xy]d`, `ac|bd`; `report-served/refused` `(?s).{32}`; `finisher-dfa` `x[^\n]{31}`; `no-eol-view` `[0-9a-f]{32}$`; compile errors identical in text (`(?<=a{300}|b{1,2})x`, 7 more). Oversized `(*UCP)\w{16}` utf8 (7.3 MB) identical under `--max-emit-bytes=20000000`.
- Mover metadata: `RX_REQ_WHY "untestable"` -> `"dominated"` on hex32-id is the spec'd cover reading (`tuning.md` §2.29¶10, the `RX_REQ_WHY` value table; cite re-spelled by section on copy).
- Compile cost (watchdog -s 60 -m 2g -c 60 + `/usr/bin/time -v`), BASE -> SUBJECT, user CPU s / max RSS kB: `a{4095}` byte 0.46/86744 -> 0.46/86760, utf8 0.45/86844 -> 0.45/87136 (SUBJECT walks it to 4095: `statement-fits 4095`); `[ab]*a[ab]{10}-{2000}` byte 0.24/29116 -> 0.22/27156, utf8 0.24/29340 -> 0.22/27432; `[ab]*a[ab]{8}-{300}` byte 0.02/24280 -> 0.02/23912, utf8 0.02/24480 -> 0.02/23976. All six artifacts identical BASE vs SUBJECT (only the `#include` basename differs). No cost regression.
