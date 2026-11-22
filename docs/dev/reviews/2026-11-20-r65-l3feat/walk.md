# CRITIC WALK: l3feat (r65)

## Findings

### WALK-1 (CONFIRMED; severity speed + doc; effort small; blast radius: patterns with a NESTED lookbehind whose guard reaches past the widest single lookbehind)

`lb_bytes` (src/facts/facts_derive.h:146-153 comment, src/facts/req.c `rb_top_back_when` :1670-1673, set at src/facts/facts.c:252-254) is `pcrec_lb_max(cx) * max_char_bytes`, and the comment says it is "the most BYTES a required run may begin before the attempt start". That is not true when lookbehinds nest. `Ctx.lb_max` copies PCRE2's `max_lookbehind` rule, and internal.h:4148-4150 says so itself: "Nesting does not accumulate (... a max, not a sum)". The walk's left guard DOES accumulate (`rb_look_item` does `rn_pre(br->lg, g)`). So a sound BACK candidate is turned down by the cap.

Repro (`$K/pc subject --features all --emit-facts --pattern P`):
- `(?<=(?<=x)a)b`: `req_whole_run none`, K=0. The true run is `xab` at -2 (lg.n=2, lb_max=1).
- `(?<=(?<=xy)a)b` and `(?<=(?<=x)ya)b`: also `none`.
- Control: `(?<=(?<=x)a)b(?<=..b)` adds a wider lookbehind that has nothing to do with the run. lb_max goes to 3, and the walk now states `786162` (`xab`) at K=-2. Answers stay correct on both routes (sm.sh vs libpcre2 on `xabyabxabbab`, all 13 starts).

No answer is wrong. D-11 rules the cap a cost cap, not a soundness bound. What is wrong is the comment, which states a bound that the nested case breaks, plus the speed lost on nested shapes.

Fix, either one:
(a) Reword the comment to "the declared (PCRE2 max_lookbehind) length; a nested lookbehind's guard may reach further, and is then declined".
(b) Cap by the walk's own reach (lg.n is already bounded by PCREC_MAX_REQ_RUN_SCAN). This needs the design's say on why the cap exists (§5.5).

## PROBED-AND-HELD


How I tested (WALK lens, my one question: is the BACK run true?):
- I read the code: `rb_top_back_when`/`rb_top_back`/`rb_top`, `rb_look_item`, `rb_ctx_item`, `rr_cat` (CAT-L/CAT-EDGE lg steps), `rr_alt` (lg = common tail), the repeat rows (`rr_pow`, `rr_rep_exact`, `rr_rep_split`, `rb_rep_unit_val`), `pcrec_req_pick` over `pcrec_run_cons`, and `pcrec_run_pin`/`pin_around` over [clo, chi).
- In every one, lg is placed at the exact offsets [-lg.n, 0) from the subtree start:
  - it crosses a left neighbour only when that neighbour is `all`;
  - an alternation keeps only the common tail;
  - a min-0 repeat or a gap drops it;
  - a repeat keeps its first copy's lg.
- So in BACK the left guard is adjacent to the head, which sits at offset 0, and K = -lg.n is exact.
- I found no candidate whose lg is unfixed or not adjacent.

## PROBED-AND-HELD
- Answers, three-way (libpcre2 10.46 vs BASE vs SUBJECT, every start offset), on the default (VM hybrid) route and `--engine=vm`: 176 patterns, 352 diff3 runs. All OK, except one compile refusal that libpcre2 also makes (`(?<=a+)b`).
  - Subjects were 3 to 70 bytes. Each one held the run at p+K (true matches) AND decoys where the consumed part is present but the lookbehind bytes are absent, or the lookbehind bytes are present and the tail fails (re-entry).
  - Shapes covered:
    - alternation of equal and unequal widths inside the lookbehind (`(?<=ab|b)c`, `(?<=ab|cd)x`, `(?<=ab|abc)d`, `(?<=bc|abc)d`, `(?<=aaa|bba)c`, `(?<=ab|)c`, `(?<=ab|^)c`);
    - variable bounded bodies (`(?<=x?ab)c`, `(?<=a{0,2}b)c`: the walk declines them, which is sound);
    - nested lookbehind (`(?<=a(?<=xa))b`, `(?<=a(?<=xya))b`, `(?<=ab(?<=b))c`, `(?<=a(?<=x[ab]))b`);
    - lookbehind not at the pattern start (`a(?<=xa)b`, `x(?<=ab)c`, `ab(?<=xab)cd`, `a{3}(?<=xaaa)b`, `(?:abc){2}(?<=xabcabc)d`, `(?:ab|cd)(?<=xab)e`, `(?:a|b)(?<=xa)c`, `b{0}(?<=xa)c`);
    - lookbehind inside a group, capture, atomic group, alternation, optional, `+`, `{2}`, `{1,2}`, `{1,3}`, possessive, or lookahead, and `(?R)`;
    - two or three lookbehinds in a row;
    - `\b`, `^`, `$`, `\G` inside a lookbehind, and `(?m)` with `\n`;
    - `\K` before or after a lookbehind;
    - a capture used by a later `\1`;
    - `(?i)` and `-i` (CLI);
    - an empty consumed extent (`(?<=foo)`, `(?<=ab)$`, `(?<=foo)(?=bar)`);
    - the stored bound (`(?<=a{32})b`, `(?<=a{33})b`, `(?<=a{40})bc`, 31/32/33-byte literal lookbehinds);
    - self-overlapping runs (`(?<=aa)a`, `(?<=abab)ac`, `(?<=aba)bac`, `(?<=ab)ab`).
  - Conditionals are not built (`(?(` refused), so I could not probe them.
- UTF-8 (`-e utf8`, 24 patterns, both routes):
  - characters of 2, 3 and 4 bytes, `(?<=é{16})x` (32 B) and `é{17}` (34 B, truncated);
  - `(?i)` k/K/U+212A and s/S/U+017F (`(?i)(?<=ss)x` states [sS\xbf\xc5][sS\xbf]x at -2: correct);
  - mixed-width classes (sound decline).
  - B is in bytes (u02 `(?<=éa)b` K=-3; u03 `(?<=a€)b` K=-4).
- Long subjects, oracle vs SUBJECT, both routes: 12 patterns x 700-byte seeded random subjects (500-700 matches each) and 4 UTF-8 patterns x 400 B, all starts. All held. `-fno-prefilter` on 4 of the long ones: held.
- Facts survey (~250 calls): every K<0 run checked by hand against the pattern. The consumed extent, `req_byte` and the run pin lie on consumed bytes in every case (`req_byte` falls to the set's pick or none when the extent is empty; the pin is `none` or inside [lo, hi)).
- ASan build of the generated matcher (my own gcc `-fsanitize=address` compile, both routes, 7 edge patterns: run at subject offset 0, run longer than the subject, empty extent, 33-byte lookbehind, UTF-8 32 B): no out-of-bounds read before the subject.
- Budget used: about 770 compiles (cap 800) and about 250 facts calls (the brief suggested about 200).
- NOT probed: L2 (lookbehind together with lookahead), the accepted interim state; whether ruling R-1's re-entry decline is complete (the MOVE lens's question).

CRITIC COMPLETE
