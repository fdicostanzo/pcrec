# vlb_d27_extract.md — the [VLOOKBEHIND] stage-2 blinded author's extract

Cut from `docs/design/vlookbehind.md` rev 5 (§6.2.2's refusal table, §6.2.5's acceptance table,
§6.2.8's spec text, §0 G1's divergences, §9's list) by lane vlbrev5, 2026-11-10, at main
`eb83f0902`. Re-cut it from that note; never edit it on its own (docs/design/CLAUDE.md).

The blinded author (D27) gets THIS FILE and `pattern_language.md` §7.4 as revised by stage 2. It
states the PROMISE: which patterns compile, what they match, and how the others are refused. It
says nothing about how pcrec computes any of it, and the author must not need that.

Every libpcre2 answer below was run against libpcre2 10.46. "lb" is libpcre2's
`PCRE2_INFO_MAXLOOKBEHIND`. pcrec's `<PREFIX>_VALID_LB` stamp is promised to equal it for every
pattern both accept. A subject in brackets is a whole-match span, `[start-end)` in characters.

## 1. The rule

1. A backreference inside a lookbehind counts as THE LENGTH ITS GROUP CAN HAVE, at both ends:
   the shortest the group can match and the longest. A group of fixed length makes the reference
   fixed, and a varying group makes the alternative vary. Stage 1's limits then apply unchanged:
   every alternative bounded, at most 65535 characters, at most 255 once any alternative varies.
2. That holds wherever the reference is written:
   - before the lookbehind;
   - inside it;
   - inside it but before its group (`(?<=\1(a))x`);
   - after it (forward: `(?<=\1)(a)`);
   - inside another group that the lookbehind references (chained: `(a)(\1)(?<=\2)x`);
   - inside a group the lookbehind CALLS (`(a)(\1)(?<=(?2))x`, `(a)(?(DEFINE)(?<g>\1b))(?<=(?&g))x`).
3. Several references ADD UP, against the cap and the ceiling alike: `(a{1,127})(?<=\1\1)x`
   compiles (lb 254), and `(a{1,128})(?<=\1\1)x` does not.
4. A reference to a group that has not matched (unset) FAILS, as it does outside a lookbehind.
5. Matching is stage 1's: the farthest candidate start first, then nearer ones. The reference
   compares the text its group captured, caseless under `(?i)`, in characters under UTF.

## 2. What is refused

A lookbehind is refused (at the lookbehind's own offset) when any of these holds. libpcre2
refuses every one of them too, with its error 125, except where noted. The SHAPE is the
refusal shape of `pattern_language.md` §2.4.

| class | example (each refused by libpcre2, err 125) | pcrec's sentence (shape) |
|---|---|---|
| a reached group has no bound: it is unbounded | `(a+)(?<=\1)x`; chained `(a+)(b\1)(?<=\2)x`; quantified `(a\|bc)(?<=\1{2,})x` | the unbounded sentence (7) |
| ... recursive (calls itself) | `(a(?1)?)(?<=\1)x`; `(a(?2){0})(b(?2)?){0}(?<=\1)x` | unbounded (7) |
| ... references itself on its own length | `(?<=(a\1))x`, `(a\|b\1)(?<=\1)x`, `(a\1?)x(?<=\1)` | unbounded (7) |
| ... is part of a reference cycle | `(a\|\2)(b\|\1)(?<=\1)x`, `(a\2)?(b\1)?(?<=\1)x` | unbounded (7) |
| ... is part of a call-and-reference cycle | `(a(?2)?)(b\1)(?<=\2)x` | unbounded (7) |
| ... any of the above, through a call | `(?(DEFINE)(?<g>a\2))(b+)(?<=(?&g))x`; `(?(DEFINE)(?<g>a\1))(?<=(?&g))x`; `(?(DEFINE)(?<g>\1))(a)(?<=(?&g))x` (`g` IS group 1); `(?<=(a(?2)))x(b\1)?` | unbounded (7) |
| ... any of the above, even under `{0}` | `(a(?1){0})(?<=\1)x`, `(a\1{0})(?<=\1)x`, `(a(?1){0})(?<=(?1))x`, `(a+)(?<=\1{0}x)y`, and with no reference `(?<=(?:a+){0}x)y` | unbounded (7) |
| the lookbehind's length reaches a group that CONTAINS the lookbehind | `(a(?<=\1))x`, `(a(?<=\1)\|b)x`, `(?<=(a(?<=\1)))x`, `((?<=\2)a)(b(?1))?x` | unbounded (7) |
| a by-NAME reference to a duplicated name | `(?J)(?:(?<n>a)\|(?<n>b))(?<=\k<n>)x`; same widths `(?J)(?<n>a)(?<n>a)?(?<=\k<n>)x`; through a call `(?J)(?<n>a)(?<n>b)?(?(DEFINE)(?<g>\k<n>))(?<=(?&g))x`; through a reference `(?J)(?<n>a)(?<n>b)?(c\k<n>)(?<=\3)x` | "a lookbehind may not contain a backreference by a duplicated group name" (7) |
| a reference inside the lookbehind, in a pattern that uses `(?\|` anywhere | `(?\|(a)\|(b))(?<=\1)x`; written after it `(a)(?<=\1)(?\|b\|c)x` | today pcrec refuses every `(?\|` (module `branch-reset` is not implemented). This class is promised for the day it is |
| over the cap or the ceiling | `(a{300})(?<=\1\|b{1,2})x` (err 200); `(a{1,256})(?<=\1)x` (err 200); `(a{40000})(?<=\1\1)x` (err 187) | stage 1's cap and ceiling sentences (7) |
| pcrec-only: a variable or a consuming callout | `(${v})(?<=\1)x` | "a lookbehind containing a variable or a consuming callout is not implemented (its length is known only when matching)" (5) |

Stage 2 changes the rule-0 (shape 5) sentence: it no longer names "a backreference". Under
stage 1 every reference lookbehind printed that sentence.

A reference to a group that does not exist reports the reference error, not a lookbehind
refusal: `(a)(?<=\2)x` (libpcre2: err 115).

## 3. What compiles (cells; each libpcre2 ACCEPT with the stated lb)

| cell | lb | on a subject |
|---|---|---|
| `(a\|bc)(?<=\1)x` | 2 | `bcx` → [0-3), group 1 [0-2) |
| `(a)(?<=\1)x` | 1 | `aax` → [1-3) |
| `(a{300})(?<=\1)x`; `(a)(?<=\1\|b{300})x` | 300; 300 | |
| `(a{1,255})(?<=\1)x` | 255 | |
| `(?<=(a\|bc)\1)x`; `(?<=(a)\1)x`; `(?<=\1(a))x` | 4; 2; 2 | |
| `(?<=\1)(a)`, `(?<=\g{+1})(a)x`, `(?<=\1)(a{300})x` | 1, 1, 300 | |
| `(a)?(?<=\1)x` | 1 | `ax` → [0-2) |
| `(?J)(?<n>a)\|(?<n>bc)(?<=\1)x` (numbered, not by name) | 1 | |
| `(?J)(?<n>a)(?<n>b)?(?<=x(?=\k<n>))y` (the name sits under a lookahead) | 1 | |
| `(a)(\1)(?<=\2)x`, `(a)(b\1)(?<=\2)x`, `(a\|bc)(d\1)(?<=\2)x`, `((a\|bc)\2)(?<=\1)x`, `(?<=(a\|bc)(d\1))x`, `(a\|bc)(\1)(?<=\2)x` | 1, 2, 3, 4, 5, 2 | `aax` → [0-3); `bcbcx` → [0-5) for the last |
| `(a{300})(\1)(?<=\2)x` | 300 | |
| `(a\2)?(b)(?<=\1)x`, `(a\|\2)(b)(?<=\1)x`, `(b\2)(a)(?<=\1)x` | 2, 1, 2 | |
| `(a\|\3)(b\|\1)(c)(?<=\3)x` (a cycle the lookbehind does not reach) | 1 | `abcx` → [0-4) |
| `(a(?2))(b){0}(?<=\1)x` | 2 | `abx` → [0-3) |
| `(a)(\1)(?<=(?2))x`, `(a)(?(DEFINE)(?<g>\1b))(?<=(?&g))x`, `(?(DEFINE)(?<g>a\2))(b)(?<=(?&g))x`, `(?(DEFINE)(?<g>a\2))(b\|cd)(?<=(?&g))x`, `(b)(?(DEFINE)(?<g>a\1))(?<=(?&g))x`, `(?(DEFINE)(?<g>\2))(a)(?<=(?&g))x` | 1, 2, 2, 3, 2, 1 | `aaax` → [1-4) for the first; `aax` → [1-3) for the last |
| `(?<=(?1))(a(?2){0})(b)x`, `(a)(?<=(?1))x`, `(a)(?<=\1(?1))x`, `(a\|bc)(?<=\1(?1))x` | 1, 1, 2, 4 | `aax` → [1-3) for the second |
| `(a(?=\1)\|b)(?<=\1)x`, `(a(?=\1))(?<=\1)x`, `(a(?=(?1)))(?<=\1)x`, `(a(?=\2))(b\1)?(?<=\1)x` (a self-reference under a LOOKAHEAD does not count) | 1 each | `bbx` → [1-3) for the first |
| `(a(?<=\2))(b)(?<=\1)x` (a nested lookbehind that does not reach its own group) | 1 | |
| `(a)(?<=\1{0}x)y`, `(?<=(?:a{0,2}){0}x)y`, `(?<=(?:a{1,300}){0}x\|b{1,2})y`, `(a{1,300})(?<=\1{0}x\|b{1,2})y` (`{0}` counts 0 characters; a bounded body under it does not reach the cap) | 1, 1, 2, 2 | |
| `(a{65535})(?<=\1)x`; `(a{30000})(?<=\1\1)x`; `(a{200})(?<=\1\1)x` | 65535; 60000; 400 | |
| `(a\|bc)(?<=\1{2})x`, `(a\|bc)(?<=\1?)x` | 4, 2 | |
| `()(?<=\1a)x`, `(a{0})(?<=\1)x`, `(a?)(?<=\1)x` | 1, 0, 1 | |
| `(a)(?<=a(?=\1))x` | 1 | |

Refusals that keep their stage-1 reason: `(a)(?<=\1|b+)x` (unbounded, at offset 3) and
`(a{1,128})(?<=\1\1)x` (cap).

## 4. Spellings, polarity, case, encoding

- Every reference spelling behaves the same: `\1`, `\g1`, `\g{1}`, `\g{-1}`, `\g{+1}` (forward),
  `\k<n>`, `\k'n'`, `\k{n}`, `(?P=n)`, `\g{n}`. Each gives lb 2 on `(a|bc)` / `(?<n>a|bc)`.
- Every polarity: `(a|bc)(?<!\1)x` (nomatch on `bcax`), `(a|bc)(?<*\1)x` (on `bcbcx`: [2-5),
  group 1 [2-4)), and the alpha spellings of §2.1 of `la_d27_extract.md`.
- `(?i)`: `(?i)(a|bc)(?<=\1)x` on `BCx` → [0-3). Under UTF with `(?i)`, `(?i)(k)(?<=\1)x` on `kKx`
  → [1-3), and a caseless reference may match text of a different byte length (K vs U+212A,
  s vs U+017F). Lengths are in CHARACTERS on both sides.
- Byte mode, UTF-8 and UTF-8 with invalid input: answers equal libpcre2's in each mode.

## 5. Stated divergences: write these cells as pcrec's answer, not libpcre2's

1. **Zero-width repeats, through a reference.** A group that CONTAINS an unbounded repeat of
   something that matches no characters (`(?:)*`, `(?:\b)*`) counts that repeat as zero
   characters. So `((?:)*)(?<=\1)x`, `((?:)*a)(?<=\1)x` and `(a(?:\b)*)(?<=\1)x` COMPILE in pcrec.
   libpcre2 refuses them (err 125). The divergence is deliberate (§7.4¶5 states it), and it is
   stage 1's `(?<=(?:)*a)x` divergence reached through a reference.
2. **D142's UTF start-position class.** Under UTF with a start offset above 0, libpcre2 clips
   backward reads at `startpos - lb`, and pcrec does not (`match_api.md` §9.4¶8). For example,
   `(?<=\ba{1,2})x` on `baax` from offset 3 is nomatch in byte mode and [3-4) under UTF. A
   reference lookbehind exposes the same class wherever its body reads one character beyond its
   length.
3. **A ruled refusal, reversed by stage 1.** [DD-14.LB] once refused a call that is a lookbehind's
   one branch when the callee has different fixed lengths. Since stage 1 that compiles:
   `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$` and `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$` (lb 2, each [0-2)
   on `ab`). `sr_d27_extract.md`'s old cell for it is history.

## 6. Diagnostics: shape and offset, not wording

Write refusal cells on the SHAPE (`pattern_language.md` §2.4) and the OFFSET, which is the
lookbehind's own. D26 does not promise wording. The sentences in §2 are pcrec's as designed, so a
cell may quote them. The one wording fact the author can rely on is that the unbounded sentence
and the duplicate-name sentence differ: a duplicated-name refusal must not say "unbounded".
