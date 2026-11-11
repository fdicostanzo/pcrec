# vlb_d27_extract.md — the [VLOOKBEHIND] stage-2 blinded author's extract

Cut from `docs/design/vlookbehind.md` rev 5.1 (§6.2.2's refusal table, §6.2.5's acceptance table,
§6.2.8's spec text, §0 G1's divergences, §9's list) by lane vlbrev51, 2026-11-10, at main
`3a190b8d7`. Rev 5's cut (lane vlbrev5) is superseded: review 2026-11-10 r5 vlb3 G20 asked for a
re-cut after the DEFINE and ceiling choices, which change the promise. Re-cut it from that note;
never edit it on its own (docs/design/CLAUDE.md).

The blinded author (D27) gets THIS FILE. You work BEFORE stage 2 is built, so the spec in the tree
still says a backreference in a lookbehind is refused. §0 below is the spec text stage 2 will
land; for references in lookbehinds it SUPERSEDES `pattern_language.md` §7.3¶6, §7.4¶5 and §9¶2.
This file states the PROMISE: which patterns compile, what they match, and how the others are
refused. It says nothing about how pcrec computes any of it, and you must not need that.

Every libpcre2 answer below was run against libpcre2 10.46. "lb" is libpcre2's
`PCRE2_INFO_MAXLOOKBEHIND`. pcrec's promise about it is `match_api.md` §9.4¶2 (LB is PCRE2's
`max_lookbehind` fact), observable through `_valid_upto` under `-futf-check`. The artifact's
`<prefix>_VALID_LB` macro is internal (`match_api.md` §6.3.1¶10), so do not write cells on it. A
subject in brackets is a whole-match span, `[start-end)` in characters. An offset `@n` is the
refusal's pattern offset.

## 0. The spec text stage 2 lands (read it in place of the tree's current sentences)

- **§2.4, the refusal shapes.** Shape 5 covers "a lookbehind whose length depends on a variable or
  a consuming callout". Shape 7 also covers "a backreference by a duplicated name, or a length
  that depends on a group containing the lookbehind".
- **§7.3¶6.** A backreference inside a lookbehind counts its group's length (§7.4¶5c). By name to a
  duplicated name it is refused (`(?J)(?:(?<n>a)|(?<n>b))(?<=\k<n>)x`). A numbered reference to
  such a group is not refused (`(?J)(?<n>a)|(?<n>bc)(?<=\1)x` compiles).
- **§7.4¶5.**
  - A lookbehind whose length depends on a module `vars` variable or a consuming callout,
    directly or through a backreference or a call, is refused (`(?<=${v})`,
    `(?<=a(?C"c,consume"))`, `(${v})(?<=\1)`: shape 5). It is refused as unbounded if an
    alternative is unbounded without them (`(?<=a+|${v})`: shape 7).
  - Whether a length is bounded is read from the pattern's text. An unbounded construct under
    `{0}` still makes the alternative unbounded (`(?<=(?:a+){0}x)y` is refused), though its length
    counts 0 (`(?<=(?:a{1,300}){0}x|b{1,2})y` compiles, and the 255 cap does not apply).
  - A `(?(DEFINE)...)` body is not part of the length at all (`(?<=a(?(DEFINE)(?<g>b+)))x`
    compiles).
  - Stated divergences: §5 below.
- **§7.4¶5c (new): backreferences.**
  - A reference counts its group's length at both ends (`(a|bc)(?<=\1)x` on `bcx` → `[0, 3)`). A
    fixed group makes it one length. This holds for forward, chained and through-a-call
    references.
  - Sums count against the 255 cap and the 65535 ceiling (`(a{1,128})(?<=\1\1)x` and
    `(a{40000})(?<=\1\1)x` are refused).
  - An unset group fails the reference.
  - A lookbehind is refused when its length reaches a group whose length is not bounded. That
    includes a group that depends on itself through references or calls, and anything under
    `{0}`.
  - It is refused, with its own sentence, when its length reaches a group that CONTAINS it,
    through a reference or a call (`(a(?<=\1))x`, `((?<=(?1))a)x`).
  - It is refused in a pattern that uses `(?|` (latent: §2's last row).
  - A reference by name to a duplicated name is refused, directly or through a referenced or
    called group.
  - A reference inside a nested lookahead, or inside a `(?(DEFINE)...)` body, is not part of the
    length (`(a(?=\1)|b)(?<=\1)x` and `((?<=x(?(DEFINE)\1))a)` compile). One under `{0}` is part
    of it (`((?<=x(?:\1){0})a)` is refused).
- **§7.4¶5a.** The call twin of the `{0}` rule: `(a(?1){0})(?<=(?1))x` is refused.
- **§9¶2/¶2a.** Shape 5 for "a lookbehind whose length depends on a variable or a consuming
  callout". The divergence clause names §5's classes 1 and 2.

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
   - inside another group that the lookbehind references (chained: `(a)(\1)(?<=\2)x`), in either
     order (`(\2)(\3)(a)(?<=\1)x`);
   - inside a group the lookbehind CALLS (`(a)(\1)(?<=(?2))x`, `(a)(?(DEFINE)(?<g>\1b))(?<=(?&g))x`).
3. Several references ADD UP, against the cap and the ceiling alike: `(a{1,127})(?<=\1\1)x`
   compiles (lb 254), and `(a{1,128})(?<=\1\1)x` does not.
4. A reference to a group that has not matched (unset) FAILS, as it does outside a lookbehind.
5. Matching is stage 1's: the farthest candidate start first, then nearer ones. The reference
   compares the text its group captured, caseless under `(?i)`, in characters under UTF.
6. A `(?(DEFINE)...)` body inside the lookbehind (or inside a group it reaches) contributes
   nothing, not even to whether the length is bounded. A `{0}` repeat contributes 0 characters
   but its body still counts for boundedness.

## 2. What is refused

A lookbehind is refused (at the lookbehind's own offset) when any of these holds. libpcre2
refuses every one of them too, with its error 125, except where noted. The SHAPE is the
refusal shape of §0's §2.4.

| class | example (each refused by libpcre2, err 125) | pcrec's sentence (shape) |
|---|---|---|
| a reached group has no bound: it is unbounded | `(a+)(?<=\1)x` @4; chained `(a+)(b\1)(?<=\2)x`; quantified `(a\|bc)(?<=\1{2,})x` | the unbounded sentence (7) |
| ... recursive (calls itself) | `(a(?1)?)(?<=\1)x`; `(a(?2){0})(b(?2)?){0}(?<=\1)x` | unbounded (7) |
| ... references itself on its own length | `(?<=(a\1))x`, `(a\|b\1)(?<=\1)x`, `(a\1?)x(?<=\1)` | unbounded (7) |
| ... is part of a reference cycle | `(a\|\2)(b\|\1)(?<=\1)x`, `(a\2)?(b\1)?(?<=\1)x` | unbounded (7) |
| ... is part of a call-and-reference cycle | `(a(?2)?)(b\1)(?<=\2)x` | unbounded (7) |
| ... any of the above, through a call | `(?(DEFINE)(?<g>a\2))(b+)(?<=(?&g))x`; `(?(DEFINE)(?<g>a\1))(?<=(?&g))x`; `(?(DEFINE)(?<g>\1))(a)(?<=(?&g))x` (`g` IS group 1); `(?<=(a(?2)))x(b\1)?` | unbounded (7) |
| ... any of the above, even under `{0}` | `(a(?1){0})(?<=\1)x` @10, `(a\1{0})(?<=\1)x`, `(a(?1){0})(?<=(?1))x` @10, `(?(DEFINE)(?<g>a(?&g){0}))(?<=(?&g))x`, `(a(?1)?)(?<=(?1){0}x)y`, `(a+)(?<=\1{0}x)y`, `(?<=(?:\1+){0}x)(b)y` @0, and with no reference `(?<=(?:a+){0}x)y` @0, `(?<=a(?:b+){0})x` @0 | unbounded (7) |
| the lookbehind's length reaches a group that CONTAINS the lookbehind | `(a(?<=\1))x` @2, `(a(?<=\1)\|b)x`, `(?<=(a(?<=\1)))x` @6, `((?<=\2)a)(b(?1))?x`, through a call `((?<=(?1))a)x` @1, under `{0}` `((?<=x(?:\1){0})a)` @1, from inside a DEFINE `(a(?(DEFINE)(?<g>(?<=\1)b)))x` @17 | "a lookbehind's length may not depend on a group that contains it" (7) |
| a by-NAME reference to a duplicated name | `(?J)(?:(?<n>a)\|(?<n>b))(?<=\k<n>)x`; same widths `(?J)(?<n>a)(?<n>a)?(?<=\k<n>)x`; through a call `(?J)(?<n>a)(?<n>b)?(?(DEFINE)(?<g>\k<n>))(?<=(?&g))x`; through a reference `(?J)(?<n>a)(?<n>b)?(c\k<n>)(?<=\3)x` @27; under `{0}` `(?J)(?<n>a)(?<n>b)?(?<=x(?:\k<n>){0})y` @19 | "a lookbehind may not contain a backreference by a duplicated group name" (7) |
| a reference inside the lookbehind, in a pattern that uses `(?\|` anywhere | `(?\|(a)\|(b))(?<=\1)x`; written after it `(a)(?<=\1)(?\|b\|c)x`; reached through a call or a chain `(?\|(a)\|(bc))(?(DEFINE)(?<g>\1))(?<=(?&g))x` @31, `(?\|(a)\|(bc))(d\1)(?<=\2)x` @17 | today pcrec refuses every `(?\|` (module `branch-reset` is not implemented). This class is promised for the day it is |
| over the cap or the ceiling | `(a{300})(?<=\1\|b{1,2})x` (err 200); `(a{1,256})(?<=\1)x` (err 200); through a call `(a)(?(DEFINE)(?<g>\1{1,300}))(?<=(?&g))x` (err 200); `(a{65535})(?<=\1b)x` (err 187); `(a{40000})(?<=\1\1)x` (err 187); a doubling chain `(a{65535})(\1\1)(\2\2)(?<=\3)x` (err 187 @22) | stage 1's cap and ceiling sentences (7), never "unbounded" for a finite length |
| pcrec-only: a variable or a consuming callout | `(${v})(?<=\1)x`; `(a)(?<=\1${v})x`; through a call `(${v})(?<=(?1))x`, `(?(DEFINE)(?<g>${v}))(?<=(?&g))x` | "a lookbehind whose length depends on a variable or a consuming callout, directly or through a backreference or a call, is not implemented (its length is known only when matching)" (5) |
| pcrec-only: an alternative unbounded without the variable | `(?<=a+\|${v})x` | the unbounded sentence (7) |

Stage 2 changes the rule-0 (shape 5) sentence: it no longer names "a backreference". Under
stage 1 every reference lookbehind printed that sentence.

A reference to a group that does not exist reports the reference error, not a lookbehind
refusal: `(a)(?<=\2)x` (libpcre2: err 115).

**Nested lookbehinds: the inner one's fault is reported at the inner one's offset.**
`(a(?<=b(?<=\1)))x` @7, `(?J)(?<n>a)(?<n>b)?(?<=c(?<=\k<n>))x` @24, `(a(?<=b(?<=(?1))))x` @7,
`(a)(?<=b(?<=\1+)c+)x` @8, `(?<=x(a(?<=b(?<=\1))))y` @12, `(?<=b(?<=(a\1)))x` @5. A lookbehind
reached through a group is judged at its own offset too: `(?J)(?<=\3)(?<n>a)(?<n>b)?(c(?<=\k<n>))x`
@28, `(?<=\1)(c(?<=\1))x` @9. When the cycle runs through the FIRST lookbehind, the first is
reported: `((?<=(?2)))(a(?<=(?1)))` @1, `((?<=\2))(a(?<=\1))` @1.

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
| `(?J)(?<n>a)(?<n>b)?(?<=x(?=\k<n>))y` (the name sits under a lookahead); `(?J)(?<n>a)(?<n>b)?(?<=x(?(DEFINE)\k<n>))y` (under a DEFINE) | 1; 1 | |
| `(a)(\1)(?<=\2)x`, `(a)(b\1)(?<=\2)x`, `(a\|bc)(d\1)(?<=\2)x`, `((a\|bc)\2)(?<=\1)x`, `(?<=(a\|bc)(d\1))x`, `(a\|bc)(\1)(?<=\2)x` | 1, 2, 3, 4, 5, 2 | `aax` → [0-3); `bcbcx` → [0-5) for the last |
| `(\2)(\3)(a)(?<=\1)x`, `(\2)?(\3)?(a\|bc)(?<=\1)x`, `(?<=\1)(\2)(\3)(a)x` (forward chains) | 1, 2, 1 | |
| `(a{300})(\1)(?<=\2)x` | 300 | |
| `(a\2)?(b)(?<=\1)x`, `(a\|\2)(b)(?<=\1)x`, `(b\2)(a)(?<=\1)x` | 2, 1, 2 | |
| `(a\|\3)(b\|\1)(c)(?<=\3)x` (a cycle the lookbehind does not reach) | 1 | `abcx` → [0-4) |
| `(a(?2))(b){0}(?<=\1)x` | 2 | `abx` → [0-3) |
| `(a)(\1)(?<=(?2))x`, `(a)(?(DEFINE)(?<g>\1b))(?<=(?&g))x`, `(?(DEFINE)(?<g>a\2))(b)(?<=(?&g))x`, `(?(DEFINE)(?<g>a\2))(b\|cd)(?<=(?&g))x`, `(b)(?(DEFINE)(?<g>a\1))(?<=(?&g))x`, `(?(DEFINE)(?<g>\2))(a)(?<=(?&g))x` | 1, 2, 2, 3, 2, 1 | `aaax` → [1-4) for the first; `aax` → [1-3) for the last |
| `(?<=(?1))(a(?2){0})(b)x`, `(a)(?<=(?1))x`, `(a)(?<=\1(?1))x`, `(a\|bc)(?<=\1(?1))x` | 1, 1, 2, 4 | `aax` → [1-3) for the second |
| `(a(?=\1)\|b)(?<=\1)x`, `(a(?=\1))(?<=\1)x`, `(a(?=(?1)))(?<=\1)x`, `(a(?=\2))(b\1)?(?<=\1)x` (a self-reference under a LOOKAHEAD does not count) | 1 each | `bbx` → [1-3) for the first |
| `(a(?<=b(?=\1)))x` (a lookahead inside a nested lookbehind) | 1 | |
| `(a(?<=\2))(b)(?<=\1)x`, `(a)(b(?<=\1))(?<=\2)x`, `(?<=\2)(a)(b(?<=\1))x` (nested lookbehinds that do not reach their own group) | 1 each | |
| `(?<=a(?(DEFINE)(?<g>b+)))x`, `(?<=a(?(DEFINE)b+))x`, `(?<=a(?(DEFINE)(?<g>(?&g)b)))x`, `(?<=(?(DEFINE)a+)x)y` (a DEFINE body is skipped) | 1 each | |
| `(a(?(DEFINE)(?<g>b+)))(?<=\1)x`, `(?<=(?1))(a(?(DEFINE)(b+)))x`, `(a(?(DEFINE)(?<g>\1)))(?<=\1)x`, `((?<=x(?(DEFINE)\1))a)`, `((?<=x(?(DEFINE)(?1)))a)`, `(a(?(DEFINE)(?<g>b{40000}c{40000})))(?<=\1)x` | 1 each | |
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
- `(?i)`: `(?i)(a|bc)(?<=\1)x` on `BCx` → [0-3). Under UTF with `(?i)`: `(?i)(k)(?<=\1)x` on `kKx`
  → [1-3), and on `kKx` where `K` is U+212A KELVIN SIGN → [1-3) as well (lb 1); `(?i)(s)(?<=\1)x`
  on `s` + U+017F LATIN SMALL LETTER LONG S + `x` → [1-3). A caseless reference may match text of
  a different byte length; lengths are in CHARACTERS on both sides.
- Byte mode, UTF-8 and UTF-8 with invalid input: answers equal libpcre2's in each mode.

## 5. Stated divergences: write these cells as pcrec's answer, not libpcre2's

1. **Zero-width repeats, through a reference.** A group that CONTAINS an unbounded repeat of
   something that matches no characters (`(?:)*`, `(?:\b)*`) counts that repeat as zero
   characters. So `((?:)*)(?<=\1)x`, `((?:)*a)(?<=\1)x` and `(a(?:\b)*)(?<=\1)x` COMPILE in pcrec.
   libpcre2 refuses them (err 125). The divergence is deliberate (§7.4¶5 states it), and it is
   stage 1's `(?<=(?:)*a)x` divergence reached through a reference.
2. **The 65535 ceiling under `{0}`.** libpcre2 applies its ceiling to each `{0}` body on its own;
   pcrec applies it to the length, where a `{0}` body counts 0. So `(?<=(?:a{30000}b{35536}){0}x)y`,
   `(a{40000}b{40000})(?<=\1{0}x)y` and `(a(?:b{40000}c{40000}){0})(?<=\1)x` COMPILE in pcrec
   (lb 1), and libpcre2 refuses them (err 187). With 35535 in place of 35536 both accept, and
   `(?<=(?:a{30000}){0}(?:b{30000}){0}(?:c{30000}){0}x)y` is accepted by both (lb 1).
3. **D142's UTF start-position class.** Under UTF with a start offset above 0, libpcre2 clips
   backward reads at `startpos - lb`, and pcrec does not (`match_api.md` §9.4¶8). For example,
   `(?<=\ba{1,2})x` on `baax` from offset 3 is nomatch in byte mode and [3-4) under UTF. A
   reference lookbehind exposes the same class wherever its body reads one character beyond its
   length.
4. **A ruled refusal, reversed by stage 1.** [DD-14.LB] once refused a call that is a lookbehind's
   one branch when the callee has different fixed lengths. Since stage 1 that compiles:
   `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$` and `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$` (lb 2, each [0-2)
   on `ab`). `sr_d27_extract.md`'s old cell for it is history.

## 6. Diagnostics: shape and offset, not wording

Write refusal cells on the SHAPE (§0's §2.4) and the OFFSET, which is the refusing lookbehind's own
(for nested lookbehinds, §2's last paragraph). D26 does not promise wording. The sentences in §2
are pcrec's as designed, so a cell may quote them. The wording facts you can rely on: the
unbounded, duplicate-name and contains-it sentences differ from one another, and a finite length
over a limit never says "unbounded".

**Write each refusal cell with ONE fault.** When a pattern has two faults (a lookbehind's and a
later one, or a lookbehind's and a callout's), which one pcrec reports is a filed known issue, not
part of the promise: libpcre2 reports the first lookbehind's, and pcrec may report another.
