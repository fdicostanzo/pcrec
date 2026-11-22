# CRITIC SOUND (opus): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first. Your lens dir: .../crit-memfn-bsu3/sound/
Findings file (pre-created, APPEND only): .../crit-memfn-bsu3/sound.md. Deliver file: .../sound_deliver.txt.

## Your ONE question
Does the emitted `w32` level block (`vs_w32_block` in memfn/src/window.c; design §4.1) answer
EXACTLY as the BASE artifact and as libpcre2, for every stretch the V rows admit, and does it read
ONLY the bytes [p, p + K) that §4.2 claims, with guard pages at both ends of the subject?
- sub-part (a) the boundary: the B choice and the final flush block at k = 16, 17, 31, 32, 33, 63,
  64, 65 and the top of each row (window 16..1000, scan 24..64; §3), and a stretch whose offset LO is
  not 0 (a prefix before the class run; a stretch that is not the site's first);
- sub-part (b) the set: nibble-table values over 127 (members with high nibble 7 or 15), the 255-byte
  `[^\n]`, `[\x80-\xbf]`, a one-byte set, a set with members in both nibble halves, caseless sets, and
  `-e utf8` artifacts (set `ORACLE_OPTS=--utf`; feed valid UTF-8 subjects as well as random bytes).

Method: the kit's `check.sh` on SUBJECT at `--features all -fmemfn-simd=x86-64-v3` (both default width
and `--window-search-width=4095`), plus a BASE vs SUBJECT answer diff on the same subjects. Build
subjects that put a near-miss byte at EVERY position of the stretch (first, last, the block seams at
i = B and K - B), lengths from just below to just above the match width, and matches flush against
each guard. Confirm each probed artifact really renders the block (`grep -c __w32_b art.c` > 0, and
`MEMFN_FORMS` = `span-vector@w32`): a probe that never reached the block is not evidence; COUNT them.
Also hand-check (by reading, not compiling) `vs_table`'s lane order and `wf_at`'s offset text.

Compile cap: 600 compiles (an emit + its gcc = 1; a BASE/SUBJECT pair = 2). State your matrix
product before you run it. Do not plant anything (the CHECKS lens owns plants).
