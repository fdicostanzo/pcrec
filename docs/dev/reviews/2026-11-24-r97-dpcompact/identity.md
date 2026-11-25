# CRITIC identity: dpcompact (r97)

## Findings


### IDENTITY-1 — group-name character check is 1.2x-1.5x slower per character; whole compile +5% to +11% with many named groups (CONFIRMED, speed)
- Where: src/parse/ucd_tables.c:156-176 (`pcrec_ucd_contains`), called per name character from src/parse/mod_named_groups.c:103-104 (`pcrec_group_name_cp`, which src/parse/subst_template.c:86/92 also uses).
- Loop bounds. BASE: one row scan (`uprops_lookup`, every row up to the match: mask test, then strlen+memcmp) plus a binary search, O(log n), over the span. SUBJECT: the same row scan plus a LINEAR varint decode up to `cp`. That is up to 677 intervals (1354 varints) for "L", and for a non-first character that is not a letter, a second scan and decode for "ND". Nothing is cached between calls. The row scan is the main cost in BOTH trees, so the ratio stays modest. It is worst at high code points.
- Repro, per call (gcc -O2 probe gnb.c linked against each tree's build/libpcrec.a, 200k calls, `pcrec_group_name_cp(cp,false)`), ns per call BASE -> SUBJECT: U+3134A 758 -> 1158 (1.53x), U+1D7CE 1688 -> 2087 (1.24x), U+1FBF9 1850 -> 2189 (1.18x), U+10FFFD 1909 -> 2159 (1.13x), U+00E9 811 -> 688.
- Repro, whole compile (`perf stat -e instructions:u`, `--features named-groups -e utf8`). Input: n groups `(?<a + U+1FBF9 x29 + 3 ASCII>x)`. n=40: 316.1M -> 333.0M (1.054). n=80: 431.0M -> 464.9M (1.079). n=160: 664.3M -> 732.0M (1.102). The U+3134A x30 names give 1.056 / 1.083 / 1.110. The extra cost is linear in total name characters, about 0.42M instructions per 30-character name, about 14k per character. BASE's other per-group work grows about 2.9M per group, so the ratio levels off near 1.14x. Emitted C is byte-identical.
- Against the charter: data_plan.md §4 A1-compact says "compile time unchanged". On this path it is not unchanged, though it stays linear and the absolute cost is small (about 2 us per name character). Group names are capped at 128 bytes (PCREC_MAX_GROUP_NAME), but the number of groups, back-references and template references is not.
- Effort: small. For example, a `pcrec_ucd_contains` variant that decodes once into a caller's arena and binary-searches, or a header line that states the per-call cost and the measured regression. The module header already describes contains as "an early-exit decode" and gives no per-call cost.
- Blast radius: compile time only, named-groups and subst templates under a wide encoding. No answer change.

### IDENTITY-2 — every \p item now copies its set into the compile arena: peak memory +5.4 KB per \p{L}, linear in \p count (CONFIRMED, size/speed)
- Where: src/parse/ucd_tables.c:119-135 (`ucd_decode`, an arena allocation of cnt*8 bytes on every `pcrec_ucd_find`), called from src/parse/mod_uprops.c:342 and :483. BASE handed out a pointer into the static table and allocated nothing.
- Also: find is called before the `want == WANT_RESULT` test (mod_uprops.c:342/483), so a probe-only pass also decodes and allocates.
- Repro: `--features unicode-props,classes -e utf8 --pattern '[' + '\p{L}'*n + ']'`, peak RSS from /usr/bin/time, BASE -> SUBJECT. n=4000: 78.1 MB -> 100.0 MB. n=16000: 278.1 MB -> 366.4 MB (+32%, +5.5 KB per item, which is 677 intervals x 8 bytes). Wall time 2.24 s -> 2.58 s at n=16000. Instructions (mixed `\p{L}\p{Han}\p{sc=Greek}` x n in one class): 1.0019 / 1.0026 / 1.0031 at n=200/400/800. Output byte-identical at every size.
- Severity: modest. BASE's own per-item cost (about 16 KB) is already linear, so this is a constant-factor increase in memory, not a new growth class. But the number of \p items is user-controlled and nothing caps it apart from pattern size.
- Effort: small. Options: decode only when `want == WANT_RESULT`, or have the decode reuse a per-Ctx cache keyed by set index. The cache conflicts with the module's "nothing is cached" rule, so the owner of that rule would need to decide.

## PROBED-AND-HELD
- Row data, find path: the BASE TSV (kit/base_sets.py) and the SUBJECT TSV (ucd_dump) match byte for byte in all 1384 rows, in the same row order. Names, masks, case-sensitive sets and caseless sets all agree. No set is empty. The highest code point is 0x10FFFF (in Any, Cn, Co and others), so 4-byte varints are covered.
- contains path, exhaustive (probe.c against SUBJECT libpcrec.a, reference = binary search over BASE sets): all code points 0..0x110001 for L, ND, BIDICONTROL and DEFAULTIGNORABLECODEPOINT. For every other first-BARE row (486 names in total), each interval's lo-1, lo, mid, hi and hi+1, plus 0, 0x7F, 0x80, 0xFFFF, 0x10000, 0x10FFFE, 0x10FFFF, 0x110000 and 0xFFFFFFFF. 4,627,596 checks, 0 mismatches. An unknown name and the empty name both return -1.
- Emitted C + rc + stderr, BASE vs SUBJECT (cmp.sh, same basename), all SAME:
  - 211 `\p` patterns (a random sample over every namespace with forms \p, \P, \p{^..}, in a class, negated class, (?i); plus single-letter \pL/\pl/(?i)\pu, L&, Lc, spacing and underscore variants, unknown names, a wrong-namespace name, gc=, malformed escapes, Any, Cn/Co/Cs, ZZZZ). Run under utf8, under utf8+modifiers, and the last 60 under byte.
  - 58 named-group patterns: letters and Nd beyond ASCII in first and later position, astral code points, combining marks, the U+3134A/U+3134B edge, U+10FFFD.
  - 52 subst templates: ${n}, $n, ${n:-}, ${n:+} under utf8.
  - 20 code segments: Bidi_Control and Default_Ignorable members, U+E0FFF/U+E1000 edges, U+10FFFF, U+FEFF, U+180E, line ends.
  - 25 UCP recipes: \w \d \s \b, every POSIX class, (?i).
- --version, --help and every --list-* (syntax, definitions, verbs, families, axes, limits, cpu-targets, schema): SAME.
- Cost of the code-segment path: unchanged (instructions ratio 0.998 at 2000, 4000 and 8000 code points of U+10FFFD). Output byte-identical.
- Witness sizes: the smallest are single escapes. The largest are a code segment of 8000 code points (32 KB), 160 named groups of 30-31 non-ASCII characters (about 20 KB), and 16000 `\p{L}` in one class (80 KB).
- About 1,350 compiles used, under the cap of 2,000.

CRITIC COMPLETE
