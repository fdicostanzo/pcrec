# CRITIC CONTRACT — r67 k152

## Findings

### CONTRACT-1 — ¶3 "+ or {2} ... refused after using at most 312,560 bytes" is a BASE figure; SUBJECT peaks at 190,224
CONFIRMED. Repro: `kit/nest.sh '' '(a|b' c ')+' d 250 > f; kit/stack.sh subject 442368 f` (and `)+` no element, `){2}` with/without `d`).
Observed SUBJECT: `(a|b…c)+` 190,016; `+d` 190,224; `{2}` 188,352; `{2}d` 188,560 (all rc=-1, too large).
BASE: `+` 313,840; `+d` 314,224; `{2}d` 312,560. So 312,560 is BASE's `{2}d` figure (the base text said 314,224, the lane
rewrote it to another base number), and no SUBJECT run reproduces it. The sentence is true as an upper bound but its figure
is ~122 KB stale; every other refusal figure in ¶3 (242,224 for the multi-atom `+`) was re-measured. Expected: "at most 190,224 bytes".
Severity doc; effort trivial; blast radius one sentence, limits.md §3.10¶3.

### CONTRACT-2 — ¶3's search-code figures (`abc` 24,120; `a`, `(a)` ~62 KB; "24 KB to 63 KB") reproduce on neither tree (pre-existing)
CONFIRMED. Repro: pattern files holding `abc`, `a`, `(a)`; `kit/stack.sh {subject,base} 442368 f`.
Observed, SUBJECT = BASE: `abc` 38,448; `a` 36,864; `(a)` 40,848. Stated: 24,120 / ~62 KB / ~62 KB. Order is even inverted
(`a` is the CHEAPEST, not the dearest). Unchanged text in this diff, so PRE-EXISTING; but the lane restated ¶3 "figure by figure" and
left this sentence unre-run. The sentence's conclusion (paid after the parse, a compile uses the larger) is unaffected at depth 250.
Severity doc; effort trivial (re-measure, restate); limits.md §3.10¶3 last sentence.

### CONTRACT-3 — 317,744 B is not the SUBJECT's worst: the litpost family with longer/distinct-letter atoms and its compound route cost up to 319,504 B
CONFIRMED. Repro (442,368-byte thread, depth 250, SUBJECT): `kit/nest.sh PRE OPEN abe ')*' POST 250 > f; kit/stack.sh subject 442368 f`:
- `^(abcdefghijklmnopqrstuvwxyz|abcdefghijklmnopqrstuvwxy_(…abe)*)*|b$` 319,504 (BASE n/a, not run; its 16-letter sibling below is BASE = SUBJECT)
- `(abcdefghijklmnopqrstuvwxyz|abcdefghijklmnopqrstuvwxy_(…abe)*)*d` 319,216 (BASE 440,560, so new-in-name only: it is the K152 shape)
- `^(abcdefghijklmnop|abcdefghijklmnoq(…abe)*)*|b$` 318,864 (BASE 318,864: PRE-EXISTING)
- `(abcdefghijklmnop|abcdefghijklmnoq(…)*)*d` 318,576; `(abcdef|abcdeg(…)*)*d` 317,936 (BASE 440,560); `^(abc|abd(…abe)*)*|b$` 318,032 (BASE 318,032, pre-existing)
Not per-character (64/256-char `a…ab|a…ac` atoms: 317,552; a 5,000-char pair at depth 1: 41,776), so ¶1 holds; the excess grows with
DISTINCT letters (an alphabet-sized pass, not the nest). Consequences: limits.def "317,744 bytes" and ¶3 "the measured worst … 317,744"
are false by up to 1,760 B; "1.39x" still rounds true (442,368/319,504 = 1.385) and ¶2/¶5 "at least 20%" still hold (1.2x = 383,405).
¶3 also says the capturing compound route is not named: only `^(?:abc|abd…)*|b$` (307,056) is; the capturing compound (318,032+) exceeds the stated worst.
Fix: name the capturing compound shape and the distinct-letter sensitivity, restate the worst as measured (or "about 318-320 KB"), and
consider a litcompound-capturing row in DEPTH_FAMILIES. Severity doc (no overflow; margin intact); effort small; limits.md §3.10¶3, limits.def:177.

### CONTRACT-4 — an unnamed `-e utf8` class nest costs more than the stated worst (still inside the budget on SUBJECT; overflowed BASE)
CONFIRMED as a ranking, SUSPECTED as a figure (the kit's driver cannot set the encoding, so this used the CLI on a main thread
capped by `ulimit -s`, which adds argv/env overhead). Pattern: `nest.sh '' '([é-ü]bc|[é-ü]bd' abe ')*' d 250`, compiled
`build/pcrec -p rx --features all -e utf8` under `ulimit -s N` (KB). SUBJECT: dies at 326 KB, compiles at 330/333/340/432 KB;
the byte litpost `(abc|abd…abe)*d` on the same harness compiles at 326 KB and dies at 318 KB; `-e utf8` with literal atoms `(ébc|ébd…)*d`
compiles at 326. So the utf8 class-island nest is the costliest shape found (~4-8 KB over litpost, est. ~322-326 KB, under 1.2x = 383 KB).
Its compound route `^([é-ü]bc|…)*|b$` compiles at 333 KB. BASE: the class nest DIES at 432 KB (pre-existing K152 instance, fixed by SUBJECT).
Not named in ¶3; test-stackdepth cannot reach it (the driver has no encoding parameter). Confirm: add an encoding arg to the driver and
measure. Severity doc/test-coverage; effort small; limits.md §3.10¶3 "measured worst", tests/thread/compile_stack_driver.c.

### CONTRACT-5 — ¶4's "88 levels of the quantified lookahead `(?=a|b(?=a|b…c)*+)*+`" holds only with the element; the written pattern reaches 87 (pre-existing)
CONFIRMED. `nest.sh '' '(?=a|b' c ')*+' '' D` on 131,072: SUBJECT d=87 rc=0 hw=130,352, d=88 DIED 139 (BASE d=88 DIED too); with `d`
appended d=88 rc=0, d=89 DIED. ¶4's preamble says "with the element beside the nest", but this item, alone among those with an element, is
spelt without the `d`, so a reader reproducing it as written gets 87. Severity doc (cosmetic); effort trivial; limits.md §3.10¶4.

## PROBED-AND-HELD

Matrix: about 185 compiles (149 SUBJECT stack, 12 BASE stack, 4 SUBJECT depth-1/0 stack, about 19 CLI `ulimit -s` runs, BASE and SUBJECT); share 300.
Depth range reached: 0 (search-code singles) to 251; nests from 78 (musl) to 251. Raw outputs: contract/{a1..a4,b1..b6}.out.
- ¶3 at depth 250 on 442,368, SUBJECT, 43 figures, all reproduce exactly: litpost 317,744 / alone 317,504 / prefix element 317,744 / named 317,744 / `*?` 317,744 /
  `*+` 293,792; `(ab|ac…ad)*` 317,440; nclitrep 293,744 / +d 292,864; nclit `+` refused at 242,016 / 242,224 ("at most 242,224" exact); altrep 257,552 /
  +d 257,792, named/atomic/`*?` 257,552; ncaltrep 229,904 / +d 230,352 / `?`+d 230,352; altpos 293,552 / +d 293,792; `\1` 257,552 / 257,792; `\1…\250` 257,552 / 257,792;
  `\1` `*+`d 293,792; lookrep 297,536 / 297,776; optnest 185,936 / 186,176; look 204,552, lookbehind 204,552, atomic 196,552, named 200,552, inlineopt 212,696 (= "at most");
  grp 120,552; callouter/callinner 120,552 (no more than plain); compound 225,496 (12,800 over plain `(?i:` = "about 13 KB"); litcompound 307,056;
  conditionals / branch reset refused at 18,552; depth-251 refusals (8 families) 122,152 .. 214,152 (= "at most 214,152").
- Per-level rates (slope depth 200 to 250): litpost 1,184 B ("about 1.25 KB"), lookahead 1,043 ("1.0"), optional 656 / total-over-250 745 ("0.75"), look 752, inlineopt 784
  ("0.75"), grp 416 ("0.4"): all held as approximations.
- ¶4 at 131,072, SUBJECT, every stated depth passes and depth+1 dies (26 runs): 88 litpost, 92 nclitpost, 78 litcompound, 100 `*+`d, 115 altpost, 115 `\1`d,
  120 ncaltpost, 88 lookahead+d, 166 optpost, 129 compound, 145 (inlineopt, dies 146) .. 159 (atomic, dies 160), look/lookbehind/named at 145 pass, grp 250 passes.
- ¶2/¶5 "at least 20%" and limits.def "1.39x": hold even over the CONTRACT-3/-4 shapes (442,368 / 319,504 = 1.385; est. utf8 ~326 KB = 1.36).
- (b) probes that stayed at or under 317,744 (SUBJECT): element prefix AND suffix, `de`, `[de]`, `d+`, `$`, `d$`, `\b`, `(?=d)` tails, `$` in the core (nfa_eol),
  `(?1)`/`(?250)` calls (nfa_splice) 317,744; atomic multi-atom `(?>…)*d` 257,792, `*+` 293,552; multi-atom lookahead `(?=abc|…)*+d` 297,776; `\b` in branch 257,792;
  `(?i)` prefix 317,744; `(?i:` wrapper at 249 (capturing 316,560/compound 316,848, nc compound 306,032); `(?=a)` in core at 249 316,560; one-atom compound 258,080;
  `{0,1}`/`{0,}`/`?`/`??` 317,744; `{0,2}`/`+`/`{2}` capturing multi-atom refused at 241,904..242,224; 3 and 6 alternatives 317,744; class atoms `[a-c]bc` 317,744;
  64/256-char atoms 317,552 (not per character; 5,000-char pair at depth 1 41,776, ¶1 held); `--engine=vm` 317,744 (nc 297,264); `--engine=dfa` refused at 128,760.
- No shape at depth <= 250 died on the 442,368-byte thread on SUBJECT (0 of 149). BASE died/overflowed on the K152 shapes as expected (utf8 class nest at 432 KB).
CRITIC COMPLETE
