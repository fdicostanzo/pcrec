# [M5.0] STAGE 3 — module `unicode-props`, general categories (lane `utf8s3`)

2026-09-06, opus, `worktrees/utf8s3`, branch `lane/utf8s3`, branch point
`d71a03c9`.

**Delivered: `\p{L}` compiles.** 45 property names, both encodings, both
polarities, in a class, under `-i`. The acceptance bar the brief named is met
in all three parts, and the four traps it named in advance all fired — two of
them differently from how the brief predicted, which §6 is about.

---

## 1. What landed

| | |
|---|---|
| `third_party/` | chartered with the general shape: `README.md` (index + the rule *a data source compiles to generated tables*), one directory per source with the version in its name, `PROVENANCE.md` naming **what derives from** the source, `LICENSE.txt`, and the generator beside its data |
| `third_party/ucd-16.0.0/` | `UnicodeData.txt` at Unicode 16.0.0, unmodified, SHA-256 recorded, plus `generate.py` |
| `src/parse/uprops_tables.inc` | GENERATED: 45 properties, 8,437 intervals, 67,392 bytes of table |
| `make gen-tables` | iterates `third_party/*/generate.py` and **names no source** |
| `src/parse/mod_uprops.c` | the producer; the hand-written 7-letter table retires into the generated one |
| `src/parse/parse.c` | `pcrec_ast_class_from_iv`, the interval-shaped constructor — **and a cursor fix, §5** |
| `src/parse/ext.c` | `in_class` passed through to the uprops marker dispatch |
| `tests/uprops/` | four sections, `make test-uprops` / `make test-uprops-utf8` |
| `tests/registry/pcre2_check.c` | `check_gated_uprops_space`, the gate-open arm |
| `tests/utf8/axis04_p_categories.rxt` | the D27-blinded corpus PROMOTED |
| `tests/known_fail/k53_uprops_oversize.rxt` | 12 blocks, K53 |
| `docs/dev/known_issues.md` | **K53** (an engine issue) |
| `docs/dev/upstream_issues.md` | **U15** (two halves) |

**The 45 names**: the seven one-letter general categories (`C L M N P S Z`),
all thirty two-letter ones, `L&` and `Lc`, `Any`, and PCRE2's `Xan Xps Xsp Xuc
Xwd`. Scripts are stage 5; booleans and `Bidi_Class` are declined by design.

---

## 2. Acceptance, with numbers

**(1) PC-3's name axis green — and it gained the arm it needed.** The
closed-gate uprops differential still reads GREEN and **stopped certifying
what its name claims the day a producer landed**: its own per-cell wall
asserts *"`\p`/`\P` has no producer this phase, so a compile here can only
mean the doorway was never reached"*, which was true for three milestones. So
the sweep was left alone (its refusal taxonomy and offsets do not change when
the gate opens) and `check_gated_uprops_space` was added beside it, on
`check_gated_option_space`'s own rule that a second producing module gets its
OWN call. Measured: **118 probes, libpcre2 accepted 28 / rejected 90, pcrec
accepted exactly the same 28, 28 real-but-unshipped names refused as the
module's gap, 6 new PASS lines.**

**(2) the membership differential over the category population — built as its
own suite, at whole-space resolution.**

| arm | result |
|---|---|
| `byte` | **14 passed / 0 failed**, 45 properties, **ZERO** code points attributed to drift |
| `utf8` | **14 passed / 0 failed**, 45 properties x 1,112,064 code points, **62,121** attributed to Unicode-version drift, **none unexplained** |

**(3) the D65 `built` column flips.** `--list-syntax` reads `built` for `\p{L}`
and `\P{L}`; the tally moves `138 = 108 + 14 + 16` -> `138 = 110 + 12 + 16`.
`\N{U+0041}` — the module's third row — correctly stays `unbuilt`, which is the
discriminating fact rather than an omission.

**And the sharpest result is not on that list.** `tests/utf8/
axis04_p_categories.rxt` is a **D27-blinded** corpus, written against the
pre-stage-2 tree from the goal, with each block's oracle answer carried as a
comment above a `perr` line. Promoted mechanically and run:

> **462 of 506 cases green on the first run. ZERO semantic divergences.** All
> 44 failures were the SAME compile-size refusal on six patterns.

No wrong span, no wrong membership, no wrong negation, on a corpus the
implementation had never seen. `axis05`'s 34 permanent error-147 refusals
still refuse, unchanged.

**Other suites**, all with the numbers from a run on this branch:
reject 610/0 (gated 80 -> 92, re-pinned), registry_check 225/0, known-fail
ratchet 2 still-failing / 0 now-passing, `make strict` clean, S121 solo mech
run UNREACHED-as-expected with 0 anomalies.

---

## 3. K53 — an ENGINE issue, found through `\p`

**Five of the 45 names refuse under `--encoding=utf8` at default axes**
(`C`, `Cn`, `L`, `Xan`, `Xwd`, both polarities). All 45 compile under `byte`
(largest artifact 23,350 bytes) and 40 under `utf8`.

The diagnosis is not about Unicode. A DFA artifact is three tables — forward,
reverse and **anchored** — of `states x byte-equivalence-classes` entries. For
`\p{L}` that is 299 x 100 twice and 453 x 100 once, and the premultiplied
values run to six digits.

| build | emitted bytes |
|---|---:|
| default | 1,076,640 (cap 1,000,000) |
| `-fno-anchored-dfa` | **772,412 — compiles** |
| `-fno-premul-table` | 478,719 |

`anchored_match_unwrapped.md` §2/§5.2 says the third machine is *"built
OPTIONAL — an overflow is a selection outcome, never a diagnostic"*, and
`src/core/compile.c` keeps that promise for the SUBSET-ELEMS budget (it saves
and restores `Ctx.dfa_overflowed` around the build for exactly this reason)
and **not** for the emit-BYTES one, because that cap is applied after all
three machines are emitted. So an optional machine refuses patterns that
compile without it.

**Not built here** (D77, and it wants its own row with its own stamp and spec
hunk): the cure is a `[SEL-1]`-shaped retry — on exceeding `max_emit_bytes`
with an optional anchored machine present, drop it and re-emit. It is
observable rather than silent (`RX_DFA_MATCH` stamps `unwrapped` vs the
wrapped form) and strictly better than a refusal.

**It refutes a design claim.** `utf8_design.md` §3.3 concludes *"the
'table-size problem' the charter names is, for the DFA route, measured not to
be a problem"* on the strength of `\p{L}` being 283 minimized states. The
state count was right; the conclusion does not follow, because the emitted
size is `states x CLASSES x digits` and under a multi-byte encoding the class
count is ~100 rather than the handful an ASCII pattern has. **The design
measured one factor of a three-factor product.**

---

## 4. U15 — and half of it is about the whole tree

**(a) libpcre2 changed `\p{Xwd}`'s definition** between 10.42 (`Xan` +
underscore) and 10.46 (`Xan` + `Mn` + `Pc`). Confirmed by a light probe of the
REFERENCE box; transcript in §7. pcrec follows the reference.

**(b) THE dlopen SHIM RESOLVES macOS's SYSTEM libpcre2 10.42, NOT HOMEBREW's
10.48.** `tests/fuzz/pcre2_abi.h` lists bare SONAMEs before the Homebrew
absolute paths, and on macOS a bare name resolves through the dyld shared
cache. Measured by dlopening each candidate in turn:

| candidate | resolves to | libpcre2 | Unicode |
|---|---|---|---|
| `libpcre2-8.dylib` | `/usr/lib/libpcre2-8.0.dylib` | **10.42** | 14.0.0 |
| `/opt/homebrew/lib/libpcre2-8.dylib` | Homebrew Cellar | 10.48 | 17.0.0 |

**This contradicts the project's own notes.** `BOILERPLATE.md` says "local
libpcre2 is 10.48-Homebrew"; the `[MACPORT]` PC-3 escalation is filed as
**U13, "VERSION DRIFT 10.46 -> 10.48"**. The pkg-config/header toolchain IS
10.48, so a probe written with `#include <pcre2.h>` sees 10.48 while the SUITE
sees 10.42 — and U13's classifying probe was of the first kind. **Whether
U13's 119 PC-3 failures are 10.48 behaviour or 10.42 behaviour is an open
question this re-opens**, and it matters: 10.42 predates 10.43, where U2's
`{,n}` change landed.

**A RULING IS OWED and this lane deliberately did not take it.** Reordering
the candidate list changes which oracle the WHOLE suite compares against, on
one box, in one line — a project-wide re-baseline, not a stage-3 edit. What
stage 3 did instead: added `pcre2_abi_unicode_version()` to the shim
(`PCRE2_CONFIG_UNICODE_VERSION` is **10**; 9 is `PCRE2_CONFIG_UNICODE`, a
uint32 that reads as an empty string in a char buffer — which is how the
constant was got wrong the first time here) and made `tests/uprops/` print the
resolved oracle's version on every run, so a result can be attributed.

---

## 5. The bug §4 of the new suite found, and why nothing else could

`esc_class_value` (src/parse/parse.c) never advanced the cursor for a produced
`EXT_MEMBERS`. So after `\p`, the `{`, `L` and `}` were re-read as ordinary
class members:

    [^\p{L}]   excluded `{` and `}` as well as the letters
    [\p{L}-z]  never saw its own dash

Every earlier class producer's construct **is** its two-byte escape (`\d`,
`\w`, and `[[:alpha:]]`'s own doorway one branch up), so the advance was
invisible and nothing had ever needed it. `\p{L}` is the first member producer
with a BODY.

**It is `esc_atom`'s [M6.5.2] lesson at the class position, and that entry
predicted this one in advance**: *"a LONGER-BODIED ATOM PRODUCER must carry
its own end and advance here."* Same failure shape too — not a refusal, a
silently different language.

**The membership differential could not see it**, and neither could the
corpus: both sides of the differential compile `\p{L}` at an ATOM, and the
blinded corpus's `\p` blocks are atom-position. Only the oracle-free invariant
`[^\p{L}] == \P{L}` was asking a question whose answer depended on the class
path. The transferable form: **an agreement check between two engines is blind
to a construct's other POSITION.**

---

## 6. The brief's four traps, scored

**Trap 1 (oracle versions) — fired, and bigger than stated.** The brief said
local is 10.48 and the reference 10.46. Local is 10.48 for headers and
**10.42 for the suite** (§4b), so the gap is TWO major Unicode versions, not
one, and in the other direction. Handled by making the drift budget SYMMETRIC
and derived from both sides' own `\p{Cn}` rather than from a version number.
Contested cells got the light 10.46 probe the brief asked for (§7).

**Trap 2 (S121 goes live) — fired INVERTED.** The brief said S121's hazard
returns at this stage and the row must be flipped. **It does not, and stage
1's reach probe would have said it had.** That probe asked whether `\p{L}`
COMPILES, reasoning that `\p{L}` is ~770 intervals so compiling it means
`n > 255` exists. Stage 3's own encoding CLAMP falsifies the implication:
under `byte`, `\p{L}` is eight Latin-1 runs. The probe would have matched and
the runner would have reported `NOW REACHED` over a population that does not
exist — the S70/S155 shape one level down, in a REACH DECLARATION.

Re-measured, the hazard is **structurally unreachable**, which is stronger
than stage 1's arithmetic argument: `n > 255` requires a code point above
0xFF, and a class holding one DECLINES the reverse-deterministic rung, because
`pcrec_cls_bits_widen` answers ALL BYTES for an out-of-range class. Proven
with a `\p`-FREE control, so it is a fact about wide classes:

    ((H)|I){3}J          -e utf8   ->  RX_VM_RUNGS 0x8u   (revdet taken)
    ((\x{100}|H)|I){3}J  -e utf8   ->  RX_VM_RUNGS 0x2u   (declined)
    ((\p{Ll})|1){3}!     -e utf8   ->  RX_VM_RUNGS 0x2u   (declined, caps raised 20x)

Probe re-aimed at the real question; solo mech run **UNREACHED (EXPECTED), 0
anomalies**. The guard stays — it is correct for a reason about `k`.

**Trap 3 (`\x{...}` is BASE grammar) — no collision.** The producer only ever
sees a `{` immediately after `\p`/`\P`; the K10/K12 boundaries are untouched
and `tests/reject/`'s pins for them are unmoved.

**Trap 4 (generated tables) — done, and the third instance of a known defect
caught.** `uprops_tables.inc` is generated by a committed script from vendored
data. It joined the Makefile's object prerequisites — **the same defect
`cls_bits.inc` (MOD-0.3e) and `limits.def` (twice) already record** — found
within minutes: adding the `Lc` row rebuilt nothing and the binary still
refused `\p{Lc}`.

---

## 7. The reference probe (light, per the brief)

One `python3 -` over ssh, reading nothing and writing nothing on that box.

    libpcre2 10.46 2025-08-27 | unicode 16.0.0 | from libpcre2-8.so.0
      \p{Xwd}   U+0300 COMBINING GRAVE ACCENT (Mn)    -> match
      \p{Xwd}   U+005F LOW LINE (Pc)                  -> match
      \p{Xwd}   U+203F UNDERTIE (Pc, non-ASCII)       -> match
      \p{Xwd}   U+0061 a (Ll)   -- control            -> match
      \p{Xwd}   U+0021 ! (Po)   -- control            -> nomatch
      \p{Xps}   U+0085 NEXT LINE                      -> match
      \p{Xps}   U+180E MONGOLIAN VOWEL SEPARATOR      -> match
      \p{Xps}   U+0009 TAB      -- control            -> match
      \p{Assigned}                                    -> COMPILE-ERR 147
      \p{Lc}                                          -> match
      \p{Mn}    U+1171E                               -> nomatch
      \p{Mc}    U+1171E                               -> match
      \p{L&}    U+0061          -- control            -> match

It confirms the pin (Unicode 16.0.0) and settles four contested cells at once.
**It also confirms the pin independently a second way**: the generator's
output has `L` = 677 intervals, `Lu` = 651, `Nd` = 71 and `Xan` = 770, which
are EXACTLY the four numbers `utf8_design.md` §3.3 measured by sweeping 10.46
itself.

---

## 8. Three `utf8_design.md` §3.4 claims refuted

1. **`\p{Assigned}` is NOT shipped.** §3.4 says SHIP. It is error 147 on
   10.42, 10.46 AND 10.48 — no libpcre2 this project can reach has the name,
   though §3.1's survey lists it as compiling. `\P{Cn}` is the same set on all
   three, so it costs nothing.
2. **`Lc` IS shipped.** §3.1's accept list does not name it because the survey
   did not try it; it compiles on all three versions.
3. **`Xps`/`Xsp` are not a pure category union.** §3.4 calls the whole
   X-family "derived, no new data". `Xps` needs U+0085 and U+180E, which no
   category holds — measured as a 2-code-point disagreement over the whole
   space before the generator was corrected from `man pcre2pattern`'s own
   (complete) horizontal- and vertical-space lists.

**And one §3.3.2 claim describes a repository that does not exist**: it says
`third_party/` should "retro-fit" PCRE2's vendored testdata into the new
shape. There is no `third_party/` before this change and no `*testdata*`
anywhere in the tree. Recorded in `third_party/README.md` rather than silently
dropped.

---

## 9. The caseless rule, because it is the one a reader will assume wrong

**Measured two ways, no exception on either**: a 44-name x 12,290-code-point
differential (`(?i)\p{X}` against `\p{X}` and against `\p{L&}`) and a
full-space interval comparison.

> Under caseless, `\p{Lu}`, `\p{Ll}` and `\p{Lt}` are **exactly** `\p{L&}`.
> **Every** other property is caseless-INVARIANT.

It is NOT the general "close the set under case mapping" rule, and the
discriminating cell is the one a reasonable implementer gets wrong: **U+0345
COMBINING GREEK YPOGEGRAMMENI is `Mn` and its uppercase mapping is U+0399
(`Lu`)** — so a general closure would put it in a caseless `\p{L}`, and
measured, `(?i)\p{L}` does not match it. U+212A KELVIN SIGN vs ASCII `k` is
the same shape one property over.

**Consequence for the code**: each table row carries its set TWICE and D23's
`cls_casefold` is never applied to a property set. Folding `\p{Lu}` by ASCII
partners would give `A-Z` plus `a-z` plus the non-ASCII uppercase letters,
which is neither `Lu` nor `L&` and is wrong on every non-ASCII cased letter.

**This also means stage 4 was not a precondition after all.** An earlier draft
of this lane was going to REFUSE caseless `\p` until the fold closure landed,
on the strength of `(?i)\p{Lu}` matching U+00E9. Measuring the rule instead of
the symptom made the refusal unnecessary.

---

## 10. What is owed

- **A ruling on the dlopen candidate order** (§4b). Project-wide.
- **K53's cure** — an engine row. It is the difference between `\p{L}` working
  and not working under UTF-8 at default settings.
- **The Linux slot**: the `utf8` differential arm re-run against the 10.46
  reference, where the policy demands EXACT agreement rather than a drift
  budget. That is the run that turns "62,121 attributed to drift" into "0
  disagreements", and it is the only place tier (1) of the policy is
  exercised.
- **The full battery** — the manager's at merge, per BOILERPLATE. This lane
  ran targeted sections only; §2 lists them with their numbers.
- **`--list-properties`, NOT built** (D77, naming the measurement): the
  suite's name population is a hand-written promise-side list checked against
  the `.inc`'s row count in both directions, which closes both directions
  without a new CLI surface. A dump would earn its place when a SECOND
  consumer needs the list — the guide, or a user-facing `--explain`.
