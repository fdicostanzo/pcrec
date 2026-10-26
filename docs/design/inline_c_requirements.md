# Inline C in patterns and templates — requirements ([INLINE-C])

**Status: REQUIREMENTS, rev 0 (lane inlinecreq, 2026-10-26).** A requirements
note, not a design: it says what the feature must do, for whom, and what it
must not break. Every design choice below is a PROPOSAL with reasons, none is
decided, and there is NO BUILD GO (Frank, 2026-10-26: "I'd like it to start
with a requirements lane"). Nothing under `src/`, `cli/`, `lib/`, `memfn/` or
`tests/` was touched. Names such as `cinclude`, `RX_CAP_S` and
`callouts-c` are ILLUSTRATIVE spellings so a scenario can be written out; the
design note chooses the real ones.

Inputs read: `docs/design/design_callout_abi.md`,
`docs/design/compound_callout_alignment.md`, `docs/design/replace_design.md`,
`docs/spec/{rxt_format,subst_api,match_api,cli}.md`, decisions D22, D26, D36,
D38, D163 (addenda 5 and 6), plan rows [M4-CALLOUTS], [MATCH-EVENTS], APPROACH.md.

Facts this note leans on were MEASURED on the Linux dev box on 2026-10-26
against libpcre2 10.46 (a throwaway C probe linked to `-lpcre2-8`, built in
this worktree's gitignored `build/probe/`, not committed). They are marked
(probe) and tabulated in section 1.

## Goals

The feature is two surfaces that share one idea: the user's C runs inside
pcrec's generated matcher. Ranked; an earlier goal wins a conflict.

1. **A pattern file can say "and check this" in C, and the answer is the
   same as PCRE2's would be for the same pattern.** Who benefits: a developer
   with a validation rule a regex cannot express (an octet is <= 255, a
   checksum, a date is real). Measurable form: for every draft usage test in
   section 2 that is pure-predicate, pcrec's answer equals libpcre2 10.46's
   answer when libpcre2 runs the same predicate through
   `pcre2_set_callout`, on the same subjects (a differential, zero
   disagreements, with the PCRE2 start-optimization flags that change fire
   points named per case, section 4.4).
2. **Convenience: calling the user's own C from a pattern or template file
   needs no `extern` plumbing a casual user cannot guess.** Who benefits: the
   casual C user (Frank, 2026-10-26: referencing a user function from an
   `.rxt` today is awkward and unclear). Measurable form: the "own header"
   scenario (UC-3) builds with ONE added declaration in the `.rxt` head and
   the user's ordinary compile line (`gcc main.c gen.c own.c`), and a
   stranger given only the README sentence for it gets it right first try
   (a usability check, run on a person, not a gate).
3. **Speed: the cost of the feature is paid only by patterns that use it,
   and a pattern whose C can run after the match keeps its DFA.** Who
   benefits: the user with a hot validation pattern. Measurable form: (a) a
   pattern with no inline C emits byte-identical output to today (the
   identity gate, no abi event for them); (b) a post-match-eligible pattern
   (section 4) emits the same engine as the same pattern without the C, and
   its search time is within the A/A floor of the DFA plus a direct call of
   the same predicate by hand; (c) an in-pattern callout costs the VM and
   nothing beyond it (Frank: "it's fast-ish. The only cost is the drop into
   vm").
4. **A pattern file stays reviewable and a third party's file never
   silently becomes code.** Who benefits: whoever compiles a pattern file
   they did not write. Measurable form: with the feature off (the default),
   every pattern containing user C is refused by name (zero emitted
   output); with it on, a listing command prints every C segment with its
   file and line (section 7).
5. **The coolness factor: "putting C inside a regex? Who does that?"** Who
   benefits: adoption and the project's story. Measurable form: the claim in
   section 6 survives a survey search (it can be falsified, and the note
   says how). Lowest priority: it never justifies a cost the other four
   would refuse.

**Priority order for conflicts:** 4 (trust) over 1 (same answer as PCRE2)
over 3 (speed) over 2 (convenience) over 5 (cool). Rationale: a feature
that turns data into code must not default-on to win convenience; a
speedup that changes the answer (post-match where it is not equivalent) is a
miscompile, so 1 outranks 3; convenience yields to both.

**Non-goals.** Tokenizer/lexer generation (re2c and flex exist; Frank
2026-10-26). A C interpreter or any embedded scripting. Making pcrec parse,
type-check or optimize the user's C (the snippet is opaque text to pcrec
except for finding its end). Sandboxing the user's C (D22: pcrec is not a
service for untrusted patterns; this note adds a gate, not a sandbox).
Per-piece event callbacks for the FINAL match ([MATCH-EVENTS] owns that, and
Frank's JSON-pieces use case is its, not this note's). A PCRE2 compat layer
for `pcre2_set_callout` (that is V-A's trampoline over the same primitive).
Dynamic loading or run-time binding.

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT, once, at the later design: goal 3's
   numbers are throughput on a hit-dense versus hit-sparse subject with a
   predicate that fails rarely versus often (post-match mode wastes work in
   proportion to failures, section 4.3), warm and cold, on the dev box, gcc,
   glibc. A different regime flips the post-match decision: if predicates
   mostly FAIL, the optimistic mode is slower than the VM. Nothing is
   measured in this note beyond the PCRE2 behaviour probes of section 1.
2. **Independent control.** RELEVANT. libpcre2 is the control for the
   pattern side (same predicate, same subject, its own callout machinery),
   and it shares no source with pcrec's emitter. The control's gap: PCRE2's
   own answers move with its start-optimization flags (section 1, probe
   row 5), so the differential must pin the flags per case and mark
   backtracking-dependent predicates "engine-relative". For the template
   side there is no libpcre2 control for the C (PCRE2 has no code in a
   replacement); the control is the same function called by hand in a
   driver, plus `pcre2_substitute` for the non-C parts of a mixed template.
   Population count: the draft cases (section 2.8) are counted there, not
   assumed.
3. **What moves on regeneration.** NOT RELEVANT today: no table or data file
   is introduced. The stamp/abi impact of the feature itself is section 3.6.

## 1. Premises, and what is true today

Premise test (the brief's): `build/pcrec -p rx --emit-main -o /dev/null
--pattern 'a(?C{x=1;})b'` prints `pcrec: (?C...) requires module 'callouts'
(pattern offset 1)`. TRUE. `--list-syntax` lists the row as
`(?C1) ... (?C{text}) -- PLANNED (D36): M4-hosted, VM-only ... planned ... unbuilt`.

STOP RULE check: PCRE2 DOES allow `(?C{...})`. Verified by running libpcre2
10.46 itself (probe), not from memory. The delimiter set is `` ` ' " ^ % # $ { ``,
with `{` closed by `}`; a `(` delimiter is refused (error 182). The string
reaches the program's callout in `callout_string` (NUL-terminated, with
`callout_string_offset` and `callout_number == 0`). So the pattern-side
premise holds and the proposal needs no adapting to a different syntax.
The template-side premise also holds: `${{ x; }}` and `${(1+1)}` are refused
by pcrec today ("a ${...} variable name must start with a letter or an
underscore") and so, by the namespace rule (D38 Q5: every pcrec-only form
must be a spelling PCRE2 rejects), `${{`/`${(` are available; the libpcre2
refusal of both is OWED a probe at design time (this note did not run
`pcre2_substitute` on them).

What the probe found about PCRE2's `(?C{...})`, load-bearing below:

| # | probe (libpcre2 10.46) | result |
|---|---|---|
| P1 | `a(?C{x=1;})b` on `ab`, callout returns 0 / 1 / -1 | fires once at pos 1; returns 0: match [0,2); returns 1: no match. A second probe (`a(?C{x})` on `aaa`): return 1 fires 3 times (once per start, rc -1); return -1 or -5 fires ONCE and `pcre2_match` returns the callout's own value (-1, -5): a negative return abandons the whole search, later starts included |
| P2 | `a(?C{if (x) {y;}})b` | COMPILE ERROR 181 "missing terminating delimiter": the string ends at the first single `}`; **a literal `}` inside a `{...}` string must be written `}}`** |
| P3 | `a(?C{if (x) {y;}}})b` | OK, string is `if (x) {y;}` — the same text with every `}` doubled |
| P4 | `a(?C{s = "}";})b` | COMPILE ERROR 139 — a C string literal holding `}` has the same rule; a C-aware lexer would NOT be PCRE2-valid |
| P5 | `a(?C#if (x) {y;}#)b`, `` (?C`x`) ``, `(?C^x^)`, `(?C%x%)`, `(?C$x$)`, `(?C'x')` | all valid; the string is verbatim; `"` doubles as `""`. `$` is the delimiter least likely to occur in C text |
| P6 | `(?x) a (?C{#x\n}) b` | a `#` inside the string is NOT a comment under `(?x)`: the string is taken verbatim, newline included |
| P7 | `(\d+)(?C{p})` on `1234`, p fails when the capture > 255 | default flags: match [1,4) ("234"), 2 fires. With `PCRE2_NO_AUTO_POSSESS\|NO_START_OPTIMIZE`: match [0,3) ("123"), 2 fires. **The same pattern and callout give different ANSWERS under PCRE2's own optimization flags** |
| P8 | `(\d+)(?C{p})x\|(\d+)y` on `12y` | the callout fires once on a path that then fails; match comes from the second alternative. A fire counter reads 1 while the callout's alternative did not match |
| P9 | `(a+)(?C{p})ab` on `aaab`, p returns 0 / returns 1 | returns 0: fires at pos 3 (capture `aaa`), then pos 2; match [0,4). returns 1 with all optimizations off: 6 fires over 3 start positions. Fire counts and positions are engine-relative |
| P10 | `(\d{1,3})(?C{p})\.` on `999.5`, fail when > 255 | match [1,4): the callout rejected `999`, then `99` from offset 1 passed and `99.` matched. A validation callout without anchoring accepts a substring |

pcrec's current plan for callouts is [M4-CALLOUTS] (boonies, not started):
VM only, static `extern` binding `rx_callout_<name>` of type `rx_callout_ref`
(D38), return `rx_matchfn`-shaped (length >= 0, -1 fail, typed give-ups
propagate, below `PCREC_ERR_FLOOR` traps), PCRE2's 0/>0/<0 contract
mirrored only in a compat layer, native abort NONE in v1 (D38 item 4). The
callout purity contract (D163 add. 6 Q2): a callout's return depends only on
what `rx_ctx` carries for that call; side effects see an unspecified fire
sequence. Today's template escape hatch is a caller-side computation: the
`${!name}` variables (module `subst-pcrec`) and the `rx_renderfn` TYPE, which
has no template spelling yet and no emitted function.

Two pre-existing facts constrain everything below:

- **`rx_callout_ref` binds a NAME, the inline form has none.** An inline
  segment is anonymous C text at a pattern position. It needs a generated
  name, and the D38 per-binding `user` pointer has no source for it
  (section 3.1, R-P7).
- **The template is compiled INDEPENDENTLY of the regex** (subst_api.md §3¶1:
  references resolve per call through an optional map; `$k` is a slot only
  when no map is given). C inside a template therefore cannot know a group
  number at template-compile time (section 3.3, R-T3).

## 2. Use cases, draft usage tests, and the user's artifacts

Notation: `[NEW]` marks a spelling that does not exist today. `.rxt` syntax is
the real one (`pattern <regex>` verbatim to end of line, `m "subject" start
end`, `n "subject"`, `features <list>`, whole-line `#` comments; rxt_format.md
§1.5). Callout return convention in the examples is PCRE2's (R-P5): `0`
continue, positive fail this path. Capture accessors `RX_CAP_S(n)`/`RX_CAP_E(n)`
(start/end byte offsets, -1 unset) and `RX_SUBJ` are ILLUSTRATIVE macro names
standing for `ctx->caps[n][0]`, `[1]` and `ctx->subject` so the examples read.
Every case below is a DRAFT USAGE TEST, UNBUILT, to be oracle-checked
(libpcre2 for the pattern side) before it becomes a test.

### UC-1 Validating predicate: an IPv4 octet <= 255 (pattern side)

The need: `\d{1,3}` matches `999`. The regex alone cannot say "<= 255".

**UC-1a, per-octet callout (in-pattern, rejects early).** The user's header
`octet.h`:

```c
/* octet.h */
#include <stddef.h>
static inline int octet_le255(const unsigned char *s, size_t n)
{
    unsigned v = 0;
    for (size_t i = 0; i < n; i++) v = v * 10 + (s[i] - '0');
    return v <= 255;
}
```

`ipv4.rxt`:

```
description IPv4 dotted quad with octets <= 255
cinclude "octet.h"                                        # [NEW] head line
features callouts-c                                       # [NEW] module (opt-in, R-P1)
pattern ^(\d{1,3})(?C{ return octet_le255(RX_SUBJ + RX_CAP_S(1), RX_CAP_E(1) - RX_CAP_S(1)) ? 0 : 1; })\.(\d{1,3})(?C{ return octet_le255(RX_SUBJ + RX_CAP_S(2), RX_CAP_E(2) - RX_CAP_S(2)) ? 0 : 1; })$
```

(Third and fourth octets elided for the page; the real file has all four.)
CLI: `pcrec -o ipv4.c ipv4.rxt` (builds the unnamed block as target `rx`,
rxt_format §1.3¶7; `--features` is the file's own line). Hand CLI form:
`pcrec -p ipv4 --features callouts-c --c-include '"octet.h"' --emit-main
-o ipv4.c --pattern '...'` (`--c-include` [NEW]).

The user's program `main.c`:

```c
#include <stdio.h>
#include <string.h>
#include "ipv4.h"

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        ptrdiff_t caps[IPV4_NCAPS][2];
        const unsigned char *s = (const unsigned char *)argv[i];
        int rc = ipv4_search(s, strlen(argv[i]), 0, caps);
        printf("%s: %s\n", argv[i], rc > 0 ? "valid" : rc == 0 ? "no" : "error");
    }
    return 0;
}
```

Build: `gcc -O2 -o chk main.c ipv4.c` (`octet.h` is found by `-I.`; nothing to link).

**UC-1b, one tail callout (post-match eligible, keeps the DFA).** Same
helper, one callout at the very end:

```
pattern ^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$(?C{ return all_le255(RX_SUBJ, ctx->caps, 4) ? 0 : 1; })
```

Draft usage tests (UC-1a and UC-1b must give the same answers):

| id | subject | expected | property it tests |
|---|---|---|---|
| DT-1.1 | `10.0.0.1` | `m 0 8` | predicate passing lets the match stand |
| DT-1.2 | `10.0.0.256` | `n` | a failing predicate rejects the only candidate |
| DT-1.3 | `255.255.255.255` | `m 0 15` | boundary value passes (<=, not <) |
| DT-1.4 | `1.2.3.4.5` | `n` | the regex's `$` still binds when the callout passes |
| DT-1.5 | `999.1.1.1` | `n` | UC-1 anchored: no substring rescue |
| DT-1.6 | (UC-1a without `^`/`$`) `999.1.1.1` | oracle (P10): libpcre2 10.46 answers `[1,9)` ("99.1.1.1") | the casual-user trap, section 2.6 W1: a predicate is not a validator unless the pattern is anchored |

### UC-2 Lookup and transform in a template (template side)

Templates compile independently of the pattern (subst_api.md §3, §5), via
`pcrec -p NAME -o OUT.c --subst-file FILE`. [NEW] forms: `${( expr )}` a C
expression whose value is rendered; `${{ stmts }}` a C statement block that
emits bytes through an output macro (`RX_PUT(ptr,len)`, `RX_PUT_Z(cstr)`,
`RX_PUT_BYTE(b)`, illustrative). Inside the C, group `n` is read as
`RX_G(n)`, an `{const unsigned char *p; size_t len;}` span (illustrative;
the named/number problem is R-T3).

**UC-2a, `Mon` to `Monday`** (inline table, no user header):

`day.tmpl` (one line, via `--subst-file`):

```
${{ static const char *const t[][2] = {{"Mon","Monday"},{"Tue","Tuesday"},{"Wed","Wednesday"}}; for (size_t i = 0; i < 3; i++) if (RX_EQ(RX_G(1), t[i][0])) { RX_PUT_Z(t[i][1]); break; } }}
```

Note the C braces: the template language has no PCRE2 constraint on its own
`${{ ... }}` form (PCRE2 refuses the form), so the segment can use a C-aware
end rule (R-S4); it would not be valid under P2's doubling rule.

**UC-2b, a number plus one** (`${( )}` with a number to bytes):

```
item-${( rx_atou(RX_G(1)) + 1 )}
```

over pattern `item-(\d+)`; the value is formatted into the template's
scratch (the case-forcing scratch mechanism of subst_api.md §4¶22).

**UC-2c, hex decode** (a URL-decode): pattern `%([0-9A-Fa-f]{2})`, template

```
${{ RX_PUT_BYTE((unsigned char)(hexval(RX_G(1).p[0]) * 16 + hexval(RX_G(1).p[1]))); }}
```

The user's driver `render.c` follows the documented element recipe
(subst_api.md §6): `rx_iter` over the pattern's `_next`, the template's
`<s>_render`, then the support unit's replace-all. Build: `pcrec -p pct -o
pct.c --pattern '%([0-9A-Fa-f]{2})'`; `pcrec -p dec -o dec.c --subst-file
dec.tmpl`; `pcrec --emit-support -o support.c`; `gcc main.c pct.c dec.c
support.c`. The no-map form (`$k` is slot k) applies because template and
pattern are written together (subst_api.md §3¶3).

| id | pattern / template | subject | expected | property |
|---|---|---|---|---|
| DT-2.1 | `\b(Mon\|Tue\|Wed)\b` / UC-2a | `Mon and Wed` | `Monday and Wednesday` | lookup hit |
| DT-2.2 | same | `Thu` | `Thu` | no pattern match, subject copied (replace-all) |
| DT-2.3 | same, subject `Mon` but table lacks it (variant) | `Mon` | `` (empty piece), or an error: the segment emitted nothing; the contract must say which (R-T6) | a C segment that emits no bytes |
| DT-2.4 | `item-(\d+)` / UC-2b | `item-9 item-199` | `item-10 item-200` | number to bytes, two matches, scratch reused per match |
| DT-2.5 | UC-2c | `a%41b%2Fc` | `aAb/c` | byte emission, mixed with literal text |
| DT-2.6 | UC-2c | `%4` | `%4` | a non-match is untouched |
| DT-2.7 | UC-2a with a side effect `++calls;` in the segment | 3 matches | `calls == 3`, NOT 6 | sizing pass vs render pass (R-T5): the segment must not be observably called twice |

### UC-3 Calling the user's OWN functions from their own header and source

The need Frank named: "if the user wanted to include their own files for
functions to be referenced by the embedded C code". Today: a pattern cannot
reach user code at all; a template reaches it only through `${!name}`
(precomputed by the caller).

User files: `geoip.h` declares `int geo_is_private(const unsigned char *s,
size_t n);`; `geoip.c` defines it. Pattern `.rxt`:

```
cinclude "geoip.h"                  # [NEW] file-level head line; emitted in the .c
features callouts-c
pattern \b(\d{1,3}(?:\.\d{1,3}){3})\b(?C{ return geo_is_private(RX_SUBJ + RX_CAP_S(1), RX_CAP_E(1) - RX_CAP_S(1)) ? 1 : 0; })
```

Answers to the questions in the brief, as REQUIREMENTS (R-S1 to R-S3):

- **How a pattern or `.rxt` says "include my header":** a file-level head
  declaration (`cinclude`, [NEW]; the head ends at the first block,
  rxt_format §1¶2, so one place to look), plus the CLI option
  `--c-include` for non-`.rxt` use and a `config`-body line for per-config
  use. Two spellings, as C and `lib` already have: `"local"` and `<system>`.
  A `cdecl "int geo_is_private(const unsigned char *, size_t);"` form
  [NEW] covers the user who has no header (it emits the declaration only).
- **Where the `#include` goes in the generated code:** the generated `.c`
  ONLY, after pcrec's own includes and before the first use, never the
  generated `.h` (a program that merely includes `ipv4.h` to call
  `ipv4_search` must not need `geoip.h`; and the `.h` is the stable contract,
  match_api.md §8). `-o -` (one self-contained `.c` to stdout, cli.md
  §1.2¶2) still prints the `#include` lines; that output is then
  "self-contained of pcrec" but not "self-contained of the user's headers",
  and it stays so because the user's symbols are the user's.
- **What APPROACH.md's self-contained rule means now:** the rule is "no
  dependency on pcrec in the generated code". It stays true: the artifact
  depends on the user's declared headers and symbols, never on libpcrec or
  `rx_*` runtime beyond the emitted block. The note requires the
  stamps to say so (R-S7): the `.c` records that it has user dependencies, so
  an artifact diff or `-o -` comparison explains itself.
- **How the user's build links it:** pcrec writes no build rule. The user's
  compile line adds `geoip.c` and `-I` for the header, as for any C program.
  pcrec never opens the header (it is not read at compile time), which keeps
  generation hermetic and the trust surface small (section 7). For the
  `.rxt` harness a test needs to compile and link user code: [NEW]
  `clink "geoip.c"` (harness-only, never emitted) and a flags line; named by
  the later design.
- **Path resolution:** `cinclude "x.h"` is emitted AS WRITTEN (the C
  compiler's `-I` resolves it), not resolved against the `.rxt` directory
  the way `lib "path"` is (that one pcrec opens; this one it must not).
  The design decides whether `--c-include-dir` rewrites to an absolute path
  for hermetic builds.

Draft usage tests (a stub `geoip.c` that treats `10.*` and `192.168.*` as private):

| id | subject | expected | property |
|---|---|---|---|
| DT-3.1 | `host 10.1.2.3 up` | `n` (callout rejects: private) | user function reached, return honoured |
| DT-3.2 | `host 8.8.8.8 up` | `m 5 12` | non-private passes |
| DT-3.3 | none (build check): `.rxt` with a `cinclude` but the header missing | build fails in the C compile, diagnostic names `geoip.h` and the `.rxt` line | R-S5 |
| DT-3.4 | none (build check): the generated `.h` of DT-3.2's artifact | contains no `#include "geoip.h"` | R-S2: the header carries no user dependency |

### UC-4 Stateful accumulation: counting and collecting

**UC-4a, a counter** in a pattern: count the octets that passed. The user
writes a global and bumps it in the callout:

```
cinclude "stats.h"                 # extern unsigned long octets_seen;
pattern ...(\d{1,3})(?C{ octets_seen++; return 0; })...
```

This is the MOST natural thing to write and it is WRONG as a count of
matched octets (P8, P9: fires happen on tentative paths and the sequence is
engine-relative). Section 2.6 W2. The CORRECT ways, which the requirements
must make easy: (i) count matches with the find-all iterator in the caller;
(ii) a TEMPLATE segment `${{ octets_seen++; }}` (it runs once per FINAL match,
after the match; subject to R-T5); (iii) post-match mode (section 4) where the
code runs once on the final match. State pointer: R-P7.

**UC-4b, collecting** matched values into the user's array from a template:

```
${{ collect_push(RX_G(1).p, RX_G(1).len); RX_PUT(RX_G(0).p, RX_G(0).len); }}
```

(emit the match unchanged, collect group 1 as a side effect). Draft tests:

| id | pattern / subject | expected | property |
|---|---|---|---|
| DT-4.1 | UC-4a pattern `(\d+)(?C{n++;return 0;})x\|(\d+)y` on `12y` | `n == 1` under pcrec VM and libpcre2 (P8) — **but the test asserts the DOCUMENTED engine-relative rule, not the number**: it asserts `n >= 1` and that `m` is `[0,3)`; a fire-count equality is a CHECK that must not exist ([MECH-REACH], "engine-relative") | a counting callout over-counts by construction |
| DT-4.2 | UC-4b over `id=(\d+)`, subject `id=5 id=7` | collected `{5,7}` in order, output unchanged | template side-effects run once per final match, in subject order |
| DT-4.3 | UC-4b with replace-all given `k = 1` (limit) | collected `{5}` | no side effect for a match the caller did not take |

### 2.6 The cases a casual user will plausibly write wrong

Each one is a requirement on diagnostics, documentation or defaults.

- **W1, an unanchored validator** (DT-1.6, P10). `(\d{1,3})(?C{le255})\.`
  accepts `999.5` as `99.` at offset 1. The predicate is correct and the pattern
  is wrong. A documentation requirement (the guide's first example is
  anchored or `\b`-bounded), not a compiler one.
- **W2, counting in-pattern** (UC-4a, P8/P9). Fires are tentative and
  engine-relative; D36 and D163 add. 6 Q2 already say so for callouts. The
  guide must say it where the user will read it, and `--list-callouts`
  (section 7) should flag a callout whose code writes to a global, only
  as a hint, never a refusal (pcrec does not parse the C).
- **W3, the brace** (P2/P4). `(?C{ if (x) { y; } })` is not valid PCRE2: a
  literal `}` must be `}}`. The first single `}` ends the segment, the
  rest is a pattern parse error far from the cause. The diagnostic must name
  the doubling rule and the offset of the segment's start (R-P9).
- **W4, the return convention.** PCRE2's contract is 0 continue, >0 fail this
  path, <0 abort. pcrec's native callout ABI is `rx_matchfn`: length >= 0 /
  -1 fail, and a user writing `return 5;` to mean "fail" would, if the
  inline form reused `rx_matchfn`, CONSUME five bytes. R-P5: the inline form
  has its own fixed contract, named constants (`RX_CO_OK`, `RX_CO_FAIL`,
  `RX_CO_ABORT`), and the generated wrapper does the mapping. A bare
  `return 1;` meaning "pass" (the C-natural reading of a predicate) is the
  most likely mistake; the constants and the guide's examples fight it.
- **W5, reading an unset group.** `RX_CAP_S(2)` inside group 1's callout is
  -1 (group 2 has not closed); `RX_SUBJ + -1` is out of bounds. The accessor
  set must give a guarded form and `ncap` (the watermark, match_api §2¶6) is
  the contract that says which are set (R-P3).
- **W6, a side effect in a template segment that runs twice** (DT-2.7). The
  `rx_renderfn` sizing protocol calls with `out == NULL` first
  (match_api.md §2¶7). A segment with a side effect then runs in the sizing
  pass and again in the write pass. R-T5.
- **W7, assuming the callout sees the match end.** In-pattern, `RX_CAP_E(0)`
  is not set yet; the position is `ctx->pos`. R-P3 names which of start,
  position and end each side can see.

### 2.8 Population

Draft tests above: DT-1.1..1.6 (6), DT-2.1..2.7 (7), DT-3.1..3.4 (4),
DT-4.1..4.3 (3): 20 drafts, all UNBUILT. Of these 4 are build or
diagnostic checks without a subject answer (DT-3.3, DT-3.4, DT-4.1's
assertion shape, DT-2.3's open contract). The later design turns each into a
`.rxt` block, a subst test or a build test and counts them there.

## 3. Requirements

Numbered so a design and a test can cite them. MUST = required by the goals;
SHOULD = wanted, may be cut by a ruling; each has a one-line reason.

### 3.1 Pattern side (R-P)

- **R-P1 Opt-in, never default.** MUST: a pattern containing `(?C{...})` is
  refused by name unless a module/flag enables inline C (suggested module
  `callouts-c`, a sibling of `callouts`, so the D26 "requires module" story
  holds and the plain `(?C1)`/`(?C"text")` forms need not carry the risk).
  Reason: goal 4. Whether the module is ever default-on is a D37 question the
  note recommends answering NO (section 7).
- **R-P2 Syntax rides PCRE2's own.** MUST: the segment IS PCRE2's
  `(?C{ string })`; the C text is the string with PCRE2's own escaping
  applied (`}}` is one `}`). A pattern file with inline C stays a VALID PCRE2
  pattern (P1, P5), so a PCRE2 program reading the same file gets the string
  in `callout_string`. Reason: the compatibility goal and the "coolness"
  claim (a regex any PCRE2 tool parses). Other delimiters (P5) are accepted
  for the same text: SHOULD, since they avoid the `}}` tax for C code full of
  braces; `$` and `` ` `` are the least C-colliding.
- **R-P3 What the code can see.** MUST (the contents of `rx_ctx` for the
  call, design_callout_abi.md §1): `subject` and `len`; the current position
  `pos`; the captures completed so far by NUMBER, with `ncap` as the
  watermark and `{-1,-1}` for unset (match_api.md §2¶6); the user context
  pointer (R-P7). The code must NOT be given a pointer it may write through:
  `caps`, `subject` are `const`. MISSING today and MUST be supplied by
  the design: the START of the current match attempt (PCRE2 gives
  `start_match`; `rx_ctx` has no such field, and group 0's start is not in
  `caps` mid-match) — this may be an `rx_ctx` field (abi event, D76/D94) or
  slot 0's start written at the callout. Named captures: pcrec knows every
  name at emit time (M6.3 name grammar), so the generated code can offer
  per-pattern constants (`IPV4_G_octet == 1`) — SHOULD — with NO rewriting
  of the user's text (pcrec treats the snippet as opaque; Goal 2's
  convenience never buys a C parser). PCRE2's `callout_number` is 0 for a
  string callout; there is no number to read.
- **R-P4 What the code may NOT assume.** MUST be stated in the spec: it may
  fire on paths the engine later abandons, zero or several times per final
  match, at positions that depend on the engine and its optimizations (D36;
  PCRE2 itself: P7 and P9); a pure predicate over `rx_ctx` is the supported
  use (D163 add. 6 Q2). A side effect is permitted and its sequence
  unspecified.
- **R-P5 What it may return.** MUST: one fixed contract, PCRE2's (so the same
  string means the same in both programs): 0 continue; a positive value fail
  THIS path (the engine backtracks); a negative value abort the whole match
  attempt. Named constants (`RX_CO_OK`, `RX_CO_FAIL`, `RX_CO_ABORT`) are in
  scope of the user's snippet. The inline contract is NOT `rx_matchfn`'s
  (length/-1, W4). Tension to resolve in the design: D38 item 4 ruled native
  abort NONE in v1 (match-or-fail only; `< RX_ERR_FLOOR` traps), and
  D38 section 4 discharged compat-mode abort as generation-time control flow
  ("jump to the fail epilogue"). The requirement: a negative return must not
  trap and must not be silently a plain fail; the design chooses between
  "abort = this search returns no match without trying later starts (PCRE2's
  effect, P1)" and "abort is refused at compile (module says fail-only)".
- **R-P6 Side effects and purity.** MUST: documented, not enforced (D22: no
  hardening, D163 Q2: a contract, not a check). The generated code must not
  make a callout observable more often than the engine needs: it fires on
  engine-chosen positions only.
- **R-P7 State.** MUST decide one source for the user context pointer.
  Options and forces: (a) none: snippets use `static` locals or
  user-header globals (simplest; not thread-safe; matches D38's rejection of
  a per-call parameter, "ouch"); (b) a per-artifact `user` pointer in the
  entry call or `rx_iter` (D38 rejected a per-call `user`); (c) a per-pattern
  `extern void *PREFIX_user;` the generated code reads (thread-safe if
  `_Thread_local`, user-defined). Reason it matters: UC-4. The note
  recommends (a) for v1 plus (c) later, and `ctx->user` stays whatever
  D38 says for named callouts.
- **R-P8 Number of callouts and identity.** MUST: each segment becomes one
  generated function with a stable generated name derived from the artifact
  prefix and the segment's index (so two artifacts in one program never
  collide, [EMIT-ENTRIES]'s `<prefix>__<role>` rule); the pattern's textual
  order is the index. SHOULD: an optional user-chosen name in a form PCRE2
  also accepts (`(?C{name: ...})` is NOT proposed — it would put pcrec syntax
  inside the string that a PCRE2 program receives, which is allowed but
  must be a deliberate ruling).
- **R-P9 Errors in the user's C.** MUST: a compile error in a snippet is
  reported against the user's file and line, not the generated file's. The
  mechanism the requirement implies: every emitted segment is bracketed by a
  `#line N "file"` directive naming the `.rxt` (or the template file, or
  `<command line>`), with the snippet's own line offsets (a multi-line
  `pattern-esc` carries newlines; one `pattern` line is one line); restored
  after. pcrec itself cannot compile-check C and must not run a C compiler by
  default (it would be a subprocess exec on every compile, a trust and
  portability cost); an opt-in `--check-c` that runs `$CC -fsyntax-only` is
  a SHOULD, named in the design. pcrec's own errors (unterminated segment)
  name the segment's start offset and the rule (W3).
- **R-P10 Where a segment may appear.** MUST: anywhere PCRE2 allows `(?C`,
  because the syntax is PCRE2's; inside lookarounds and atomic groups the
  semantics are PCRE2's (a callout inside a lookahead fires during the
  assertion, with the captures at that time). The design must list the
  positions it supports in v1 and refuse the rest by name, never miscompile
  (house rule: unsupported constructs fail with a clean message). Recursion
  and subroutine calls (`(?1)`) multiply fire points: SHOULD be refused in v1.
- **R-P11 Encoding.** MUST: under `-e utf8` the snippet's bytes are the
  pattern's bytes (UTF-8) and `ctx->pos` and captures are BYTE offsets, as
  everywhere in the artifact's API; the code sees raw bytes.
- **R-P12 Engine forcing.** MUST: an in-pattern segment forces the VM engine
  (the DFA erases positions, D36). A pattern that opts into post-match mode
  (R-P13) need not.
- **R-P13 Post-match predicate mode.** MUST be answered in the design (the
  analysis is section 4). Requirement on the spelling: a FLAG, not a second
  syntax, so the same `(?C{...})` text means in-pattern by default and
  "after the match" under the flag, at per-pattern granularity at least
  (`features callouts-c-post` or `callout-mode post`, [NEW]) and per-segment
  as a SHOULD. The flag must never silently change an answer (section 4.2:
  it is refused or downgraded to in-pattern where not equivalent).

### 3.2 Template side (R-T)

- **R-T1 Forms.** MUST: `${( expression )}` (a C expression, its value is
  rendered) and `${{ statements }}` (a block that emits bytes). Both are
  refused today by PCRE2's grammar (a pcrec-only extension, namespace rule D38
  Q5), live under module `subst-extended` OR a new `subst-c` module (the
  note recommends the new one: the C forms carry the trust cost, R-S1, and
  `subst-extended` is "PCRE2's extended syntax, libpcre2 10.46's answer,
  D26 exact" — putting C in it would break that sentence).
- **R-T2 Each segment becomes one generated `static inline` function**
  (Frank's wording) in the template's `.c`, run per MATCH after the match,
  from the same `rx_ctx` family (subst_api.md §4¶27: `rx_ctx` is the one
  context; `rx_renderfn` is the existing type for "one completed match to
  one segment's bytes").
- **R-T3 What it sees: groups by number and name.** MUST. The problem: a
  template is compiled independently of the regex (subst_api §3¶1); `$k`
  with no map reads slot k and a name needs a map. So a `RX_G(n)`/`RX_G(name)`
  accessor must resolve through the SAME reference list and map that `$n`
  and `$name` use (one table per slot: no private copy). Requirement: every
  group a snippet reads is DECLARED to the compiler (so `refs[]` is complete
  and the map check, §3¶8, can refuse a template whose C reads a group the
  regex lacks). Proposal: a snippet reads groups only through an accessor
  macro with a literal argument, which pcrec scans for (a text scan is a
  C-lexing dependency; the alternative is `${{ ... }}` taking an explicit
  declaration list `${{ $1 $name | stmts }}`, which avoids scanning).
  This is the template side's one hard design problem; it does not exist on
  the pattern side (there group numbers are the pattern's own).
- **R-T4 What else it sees.** MUST: the whole match (`$0`), the subject and
  the match span (so `` $` `` and `$'` equivalents), the iteration's start
  position, the user context pointer. The caller's variables (`${!name}`,
  module `subst-pcrec`) SHOULD be readable (`RX_VAR("name")`), since they are
  already the sanctioned channel for caller data and cover the UC-3 need
  without any `#include` (a user can pass a function-computed value or a
  table pointer as a variable).
- **R-T5 Called once per match.** MUST: observably once per rendered match.
  The sizing-pass/write-pass protocol (`out == NULL` first) means a function
  is invoked twice; the requirement is that user-visible side effects happen
  once. Options (design): render into scratch in the sizing pass and copy;
  or split a segment into a pure "compute" the element calls once per match
  into scratch, then the pieces point at the scratch (how case forcing works,
  `PCREC_SUBST_USES_SCRATCH`). The first fits pieces' no-allocation rule
  (replace_design R4 goal 2).
- **R-T6 What it may return and its failure.** MUST define: a segment emits
  bytes (possibly none), or FAILS the element (`rx_renderfn`'s -1, "or -1 to
  fail"): the existing contract says what a failure does to a
  replace-all (a prefix of a failed run, subst_api §6). DT-2.3 asks the open
  question: no bytes emitted is an empty piece, not an error. A typed
  error code space for "my C says this match is invalid" SHOULD reuse the
  `PCREC_ERR_*` partition (below `PCREC_ERR_FLOOR` is reserved: the design
  picks a code, an abi/spec event).
- **R-T7 Scratch and size.** MUST: output through a scratch bounded by the
  caller-supplied scratch (no allocation, subst_api R4.0 item 5); a segment
  that would exceed it returns the existing NOSPACE class. The sizing pass
  must return the same length the write pass produces (a segment is
  deterministic in `(ctx)`; documented, not enforced).
- **R-T8 No VM, no DFA question.** CONFIRMED: the template runs after the
  match is found, per completed match, over the final captures. It forces no
  engine and changes no search; the post-match semantics section 4 asks
  about the PATTERN side is the template's native mode. A template segment
  cannot reject a match (the match already happened); "reject" is a pattern
  feature, R-T6's failure is an error, not a retry. This is the cleanest
  place the feature lands: no engine analysis, only emission and ABI.
- **R-T9 Encoding.** MUST: a template's text is read in `-e`'s encoding
  (subst_api §2¶5); the C text inside a segment is bytes passed through
  untouched. A `utf8` template with a non-UTF-8 byte inside a C string
  literal: the well-formedness check of §2¶4 must NOT reject a segment's C
  text for being non-UTF-8 only if the design says C text is exempt; the
  default is it is checked like the rest (a C source file is UTF-8 in
  practice) — a requirement to DECIDE, with the check order stated.
- **R-T10 The existing escape hatch stays.** MUST: `rx_renderfn`'s typedef
  and `${!name}` variables remain; inline C is sugar over the same
  primitive, never a replacement (D38 Q6: renderer bindings use the
  ref-struct shape; one table per slot).

### 3.3 Shared (R-S)

- **R-S1 One trust gate.** MUST: both sides sit behind an explicit opt-in
  (section 7); the CLI refuses a source containing inline C without it,
  naming the first segment.
- **R-S2 Include and declaration lines.** MUST: `cinclude` and `cdecl`
  (spellings illustrative) are file-level/config/CLI constructs shared by
  pattern and template builds; they go in the generated `.c` and never the
  `.h` (UC-3); they are emitted in the order written; pcrec never opens the
  files they name.
- **R-S3 The user's build.** MUST: no pcrec-written build rule, no required
  link library; the user's link line is the whole story. The design notes
  how the `.rxt` harness and `examples/makefile/` (D118) carry user sources.
- **R-S4 The end-of-segment rule.** MUST be one rule per spelling, stated in
  the spec with a table of test inputs:
  - Pattern side `(?C{...})`: PCRE2's rule exactly: the first single `}` ends
    the segment; `}}` is one literal `}` in the string (P2, P3). Reason:
    keeping the file valid PCRE2 (goal 1). A C-aware lexer here would make a
    perfectly good C snippet PCRE2-invalid (P4), forfeiting compatibility,
    and would make pcrec's segment end differ from PCRE2's for the SAME pattern
    text (a miscompile risk of the worst kind: same bytes, different
    pattern). Recommended: PCRE2's rule, strictly; the other delimiters (P5)
    are the relief valve.
  - Template side `${{...}}` and `${(...)}`: PCRE2 has no such form, so there
    is no compat constraint; a C-aware scan is allowed: track braces/parens
    depth, skip over string and character literals (with their escapes), line
    and block comments, and raw preprocessor lines; the segment ends at the
    terminator at depth zero. Edge cases the spec must enumerate with a test
    per row: `"}}"` inside a string; `'}'`; `/* }} */`; `// }}` to end of
    line (but a template is not line oriented: a `//` comment swallows the
    terminator unless a newline follows — the rule needs a stated answer);
    `?:` and a trailing `)` in `${( a ? b : c )}`; a `}}` that is two closing
    braces of nested blocks (`for(...){ if(..){...}}}` at depth 2 and then
    `}}`); a digraph or trigraph (`??>`) — recommend: refused as unsupported;
    a `#include`-like line inside; wide/prefixed string literals `L"}"`,
    `u8"}"`, raw strings are C23/C++ (not C): `R"x(}})x"` is not C. An
    unterminated segment is refused with the segment's start offset.
  - Same text, same segment, on both sides, would be ideal (one rule); it is
    not possible without breaking PCRE2 validity on the pattern side. The
    note records the asymmetry as a deliberate cost (section 8 Q3).
- **R-S5 Diagnostics.** MUST: C compile errors land on the user's line
  (R-P9) for both sides; pcrec's own refusals name offset and rule; a
  segment's generated function name appears in no user-facing message.
- **R-S6 Escaping.** MUST: the pattern side's escaping is PCRE2's (`}}`,
  `""` under `"`); under `pattern-esc "..."` the `.rxt` escape table applies
  FIRST (rxt_format §1.5¶3), so a C string `"\n"` inside `pattern-esc`
  needs `\\n`. A second reading rule that costs the user: the guide must show
  one worked example of each of the three layers (rxt, PCRE2, C). SHOULD:
  `--list-source` shows the DECODED snippet so the user sees the C that
  arrives.
- **R-S7 Abi, stamps and the identity gate.** MUST: (a) a pattern or
  template with NO inline C emits byte-identical text to today (so no
  mass re-pin); (b) the `.c` records that it has user code (a stamp line,
  e.g. `<PREFIX>_USER_C 1` or an entry in the module stamp
  `<PREFIX>_MODULES`), and the used modules are stamped like
  `subst`/`subst-extended` are (subst_api §5¶2); (c) any NEW `rx_ctx` field
  (the match start, R-P3) or `rx_info` member is an abi event per D76/D94
  (bump, readers by GREP, re-pin the identity gate, the spec hunk in the
  same change); the later design counts its abi movers before asking for a
  go. (d) `PCREC_ERR_*` additions (R-T6, R-P5) are below the floor and need
  the same ritual.
- **R-S8 Spec impact (D80).** MUST, in the same change as the build:
  `docs/spec/match_api.md` (§2 the callout block and return contract, §6
  `rx_info` fields), `docs/spec/rxt_format.md` (head `cinclude`/`cdecl`,
  the schema rows, `--list-schema`), `docs/spec/cli.md` (options, the
  module), `docs/spec/subst_api.md` (§2 forms, §9 differences-from-PCRE2
  rows, the module list), `docs/pcre2_compliance.md` (the `(?C{` row moves
  from PLANNED; the compliance-refresh skill), `docs/guide/` (a human
  use-case page; it points at the spec, never restates it).
- **R-S9 Tests.** MUST (a requirement on the later test plan, not on this
  note): the pattern side gets a libpcre2 differential in which the SAME
  predicate text drives both engines through a generated adapter (a table of
  segment index to function, built from the same snippets); per-case PCRE2
  flags pinned (P7); backtracking-dependent cases marked engine-relative and
  asserted on the DOCUMENTED rule only, never on fire counts. The
  template side's control is the by-hand call plus `pcre2_substitute` for the
  non-C bytes. A test that needs the user's C compiled in uses the harness
  link declaration (UC-3).
- **R-S10 `--list-*` introspection.** SHOULD: `pcrec --list-callouts FILE`
  prints every segment (file, line, delimiter, the decoded C, the position
  in the pattern, whether post-match-eligible and why) — the reviewer's view
  (section 7) and the "observable" requirement of the decisions-as-tables
  rule for the eligibility table (section 4.5).
- **R-S11 Budgets and give-ups.** MUST: an in-pattern callout runs under the
  same step/frame meters as the VM; a callout that takes a long time is the
  user's problem, not metered by pcrec (it cannot see inside), and the
  document says so. The typed give-up propagation of D49/D163 Q3 is unchanged.
- **R-S12 Reentrancy.** MUST: a generated matcher stays reentrant; user C
  that is not is the user's. A callout must not call back into the SAME
  artifact's entries on the same iterator (undefined; documented). Calling a
  DIFFERENT pcrec artifact as a submatcher is the D38 composition path and is
  supported by the named-binding form, not by inline C.

## 4. Engine: the in-pattern cost, and Frank's post-match predicate

### 4.1 What the in-pattern form forces

A callout fires at a pattern position (between two items, mid-alternation,
inside a quantified group). The DFA has no pattern positions, only states;
captures-so-far need the VM's capture machinery (design_callout_abi.md §2).
So an in-pattern callout forces the VM for the WHOLE pattern (no mixed
engine for one pattern except the DFA-island/compound machinery of D163,
which declines callouts today under A3 until the purity contract lands). It
fires on every tentative path, including ones the engine later abandons
(P8, P9). The cost is the VM's, plus one call per fire.

### 4.2 The idea: a post-match predicate (Frank, 2026-10-26)

"Determining if the callout/embedded C could be run after the pattern match
as a post match predicate (flag?) allowing DFA." The code runs ONCE, after
the engine has found a match, over the final captures; if it returns "fail",
the match is rejected. The DFA is kept for the pattern minus the callout. The
questions are exactly: when does that give the SAME answer as the in-pattern
callout, when does it differ, and what does a rejection do.

**Definitions.** A *candidate* is a match of the pattern (callouts treated as
always-pass) at a given start position. The in-pattern engine explores
candidates in priority order at a start `s`, and at each fire the callout
may veto the path, in which case the engine backtracks into the next
candidate path; only when every path at `s` fails does it advance to `s+1`.
The post-match engine finds the FIRST-priority candidate in the callout-free
pattern (the DFA's answer) and asks the predicate once. Call a callout
*pure* if its return depends only on `rx_ctx` (D163 Q2) and *tail* if it is
the last item on every path to the pattern's end (nothing after it can
consume input or change captures; lookarounds and atomic groups around it
count as "not tail" in v1).

### 4.3 When post-match is EQUIVALENT

Equivalence of ANSWERS (the match returned, or no match) holds when ALL of:

- **E1, pure.** The predicate reads only `rx_ctx` (subject, position, captures
  so far, vars). (A side-effecting callout is outside the contract in both
  modes, so equivalence is about answers; side-effect sequences differ and
  are unspecified in both, R-P4.)
- **E2, the predicate's inputs are the same in both modes.** For a TAIL
  callout the position is the match end and the captures are the final
  captures: same inputs. For a NON-tail callout the in-pattern inputs are the
  captures and position AT THE SITE, which the DFA's final answer does not
  carry unless the engine records a snapshot at the site on the winning path
  (the [MATCH-EVENTS]/[CAP-SPAN] shape: events recorded on the match path
  and delivered for the final match only). With such a snapshot the
  inputs are the same; without it the mode is NOT available to non-tail
  callouts.
- **E3, the candidate is UNIQUE at its start, or every other candidate also
  fails the predicate.** If the first-priority candidate passes, post-match
  returns it, and the in-pattern engine would have returned that same
  candidate (it explores in the same priority order, and earlier candidates
  at this or earlier starts do not exist or the DFA would have found them).
  If the first candidate FAILS: in-pattern backtracks to the NEXT candidate
  at the same start; post-match, with the rule "reject and resume at `s+1`",
  does not. They agree only when no other candidate exists at `s`, or the
  predicate would reject all of them (typically: the predicate depends only
  on something all candidates share).

The common sufficient condition for E3 is a pattern DETERMINISTIC at the
start: its candidates at a start have one span (each item's extent is forced
by what follows). The strict-anchored IPv4 pattern of UC-1b is the model.

**Worked example, EQUIVALENT (UC-1b):**
`^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$` + tail `(?C{all four <= 255})`.
Subject `10.0.0.256`. In-pattern: the VM reaches the end with 256, the callout
fails, the engine backtracks: `\d{1,3}` for the last octet can only be `256`
(the `$` forces the extent), so no other candidate; no match. Post-match: the
DFA finds `[0,10)`, the predicate fails, rejected; resume at 1: `^` anchors, no
candidate. Answers equal: no match. Subject `1.2.3.4`: both return `[0,7)`.

**Worked example, EQUIVALENT with a FAILING predicate and several starts:**
`\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b(?C{le255 all})`
on `300.1.1.1 4.4.4.4`. In-pattern: start 0 candidate `300.1.1.1`, callout
fails; the `\b`-bounded pattern has no other candidate at 0 (each `\d{1,3}`
is forced by the next `.` and the final `\b`); starts 1 and 2 hit `\b`
failures (a `\b` between digits is false), so no candidate; start 4's
candidate (`1.1.1`) has too few octets; start 10 `4.4.4.4` passes: `[10,17)`.
Post-match with "reject, resume at s+1" reaches the same `[10,17)`. Equal
because the candidates at each start are unique.

### 4.4 When post-match DIFFERS

- **D1, backtracking into a different capture length.** `(\d+)(?C{p})` on
  `1234` with `p` = "capture <= 255" (the PCRE2 probe P7, with its own
  caveat). In-pattern (optimizations off): the VM tries `1234` (fails), then
  `123` (passes): answer `[0,3)`. Post-match: the DFA's first-priority
  candidate is the greedy `1234`, the predicate fails, "reject and resume
  at s+1" gives start 1: `234` fails; start 2: `34` passes: answer `[2,4)`.
  **DIFFERENT ANSWERS** from the same pattern. And libpcre2 itself answers
  `[1,4)` with default flags and `[0,3)` with
  `NO_AUTO_POSSESS|NO_START_OPTIMIZE` (P7): so there are THREE answers in
  play, and the "right" in-pattern answer is itself engine-relative. This
  example is the standing proof that a backtracking-dependent predicate is
  not portable even across PCRE2's own flags; pcrec's contract is the purity
  contract plus "the answer is the engine's, in priority order, with the
  vetoes applied along the VM path".
- **D2, a failing predicate on an alternation choice.**
  `(a|ab)(?C{group 1 == "ab"})` on `ab`. In-pattern: path `a` reaches the
  callout, the predicate vetoes it, the engine backtracks into the second
  alternative `ab`, the predicate passes: `[0,2)`. Post-match (M1): the
  DFA's first-priority candidate is `[0,1)` (`a`), the predicate rejects it,
  resume at start 1: `b` has no candidate: NO MATCH. Different. (Whether the
  first-priority candidate is `a` is the usual leftmost-first rule; the
  pattern is ambiguous at its start, so E3 fails.)
- **D3, a veto that must steer a later part of the pattern.** Any non-tail
  callout whose rejection should select an alternative AFTER it
  (`(\d+)(?C{p})(?:x|y)`): the alternation after the callout never sees a
  vetoed path in-pattern; post-match, the DFA picks a path before the
  predicate runs. Same class as D1.
- **D4, fire-time inputs for a non-tail callout.** Without a recorded
  snapshot (E2), post-match cannot offer the site's position at all.
- **D5, side-effect observability.** In-pattern: tentative-path fires happen
  (P8). Post-match: the predicate runs once per candidate considered. NOT an
  answer difference, but a user who relied on counting (W2) sees different
  numbers; both are "unspecified" by contract.

### 4.5 What a rejection does (the semantics options)

The post-match predicate's FAIL needs a defined action. Options:

- **M1, reject-and-resume-at-s+1** ("this start has no valid match, as if
  every path at `s` failed"): equals in-pattern whenever E1-E3 hold and the
  start has a unique candidate; DIFFERS when the start has several
  candidates (D1, D2). Cost: DFA restarts; a pathological subject (a long
  run of vetoed candidates) is O(n) restarts each O(match length): worst
  quadratic, like any restart (a documented measure, goal 3).
- **M2, next-match-in-priority-order at the same start** (the exact
  in-pattern semantics): not available from a DFA (it returns one answer).
  Providing it means enumerating alternative candidates, which is the VM's
  backtracking: a VM part used only on a veto. This is
  **optimistic DFA with VM verification**: run the DFA; if the predicate
  passes on its first-priority candidate, return it (answer-equivalent for
  pure predicates, E1, tail or snapshot per E2: argued in 4.3: any
  higher-priority candidate does not exist, any earlier start has no
  candidate even without vetoes, so the in-pattern engine would return the
  same match); if it FAILS, rerun the search from `s` in the in-pattern VM
  with the real callouts, the exact semantics. This is ALWAYS answer-
  equivalent for pure predicates (it only skips the VM when the cheap path
  is provably the answer). Costs: a failing predicate pays DFA + VM (about
  1 + VM), a passing one pays DFA only. It wins when failures are rare
  (validation of mostly-valid data), loses when they are common. This is the
  recommended shape of the mode (section 8 Q4).
- **M3, report the rejection** ("no match, stop", or an error code):
  PCRE2's negative-return abort effect (R-P5); not a general predicate
  semantics; belongs to abort only.

Recommendation (a proposal, not decided): offer the flag in two strengths.
(1) `post` = M1, available ONLY where an eligibility table proves E3
(deterministic-at-start pattern, tail or snapshot callout), else REFUSED
by name ("the pattern is ambiguous at its start; the callout is not
equivalent post-match"), so it can never change an answer. (2) `verify` = M2:
available whenever E1+E2 hold; falls back to the VM on a veto; always
answer-equivalent. A table of named eligibility predicates with a deny per
row (the decisions-as-tables rule: declared rows, one selector, observable),
printable through `--list-callouts` (R-S10).

### 4.6 Eligibility facts the engine would need (what pcrec knows today)

pcrec analyses start-determinism and unique ends already for the compound
machinery (D163 add. 7: "X has a UNIQUE end from a given start" is client
8's admission rule). That is the same fact as E3. This requirement is
therefore NOT a new analysis but a reuse of an existing one (one table per
slot): the design must read the compound's admission predicate rather than
write a second. [CAP-SPAN] (filed 2026-10-26, "place captures inside a
proven span without, or with less, VM") is the same family: a snapshot at a
callout site is a capture placement. Overlap rows and triggers belong in the
design.

### 4.7 The template side

CONFIRMED: no VM and no post-match question. The element runs after each
match from the final `rx_ctx` (subst_api.md §4), so the template side is
natively post-match, equivalent to nothing in-pattern; its failure cannot
steer the engine (R-T8).

## 5. Compatibility

- **PCRE2, same pattern.** libpcre2 accepts `(?C{...})` and delivers the
  string to the program's callout function in `callout_string` (P1);
  a PCRE2 program that sets no callout (`pcre2_set_callout` unset) ignores
  it and matches as if the callout returned 0. So a pattern file with
  inline C is valid PCRE2; the C meaning is pcrec's, the string is PCRE2's
  (R-P2). pcrec compiling the string as C does not alter PCRE2's reading.
- **D26 tiering.** The PATTERN layer (syntax, where a callout may appear, what
  a callout veto does to the match) is D26-exact, as D36 ruled: a callout
  returning 0 matches as PCRE2 does, and a positive return fails the path as
  PCRE2 does (P1). The CALLBACK CONTRACT (block fields, return codes) mirrors
  PCRE2 in the compat layer only; the inline form's `rx_ctx` is pcrec's.
  The REGISTRATION is pcrec-native: there is no registration, the code IS
  the callout. Fire points are engine-relative, with PCRE2's own latitude as
  the precedent (P7, P9: PCRE2's answer moves with `NO_AUTO_POSSESS` and
  `NO_START_OPTIMIZE`, which is a stronger fact than D36 cited). D26's
  "wording of a diagnostic" tier applies to R-P9's messages (not exact); the
  pattern's MATCHING is exact for pure predicates over a deterministic pattern.
- **Perl `(?{ code })` and `(??{ code })`.** The nearest prior art (section 6):
  Perl runs interpreted Perl at the pattern position on tentative paths and
  exposes `$^R` (last result) and `$^N` (last close); `(?{ })`'s result is
  discarded for matching, a TRUE/FALSE condition is `(?(?{ code })yes|no)`;
  `(??{ code })` returns a sub-pattern. PCRE2's `(?C)` is the compiled-host-
  function descendant. pcrec's inline predicate corresponds to the Perl
  CONDITIONAL form `(?(?{ code }) ...)` more than to `(?{ })`. pcrec's
  contract is PCRE2's (0/pos/neg), not Perl's (truthiness of the block's
  value): a Perl user's `(?{ $x > 3 })` has no pcrec spelling; the guide
  maps it. Perl's own caveat is the same fire-count caveat (perlre "Embedded
  Code Execution Frequency", from memory).
- **Perl precedent for the trust gate.** Perl requires `use re 'eval'` for
  code blocks in a pattern built at run time from interpolated strings
  (literal blocks in a literal pattern are allowed): a precedent for an
  explicit opt-in that targets the dangerous case (R-P1).
- **Where pcrec's form is NOT PCRE2-compatible, by design:** the template
  `${{`/`${(` forms (pcrec-only, refused by PCRE2's grammar); the
  `cinclude`/`cdecl`/flag additions (head and CLI, invisible to PCRE2);
  a post-match mode's refusal rows. Each lands as a `subst_api.md` §9
  differences row or a compliance-document row.

## 6. Prior art, honestly

Written from knowledge of these tools, NOT re-fetched this session (no web
survey was done); any statement here that is used in public text must be
re-verified first.

| tool | what it embeds | when it runs | compiled or interpreted |
|---|---|---|---|
| Perl `(?{ })`, `(??{ })` | Perl code at a pattern position; `(??{ })` returns a sub-pattern; conditional form | during the match, on tentative paths, at engine-chosen frequency | Perl code compiled to the interpreter's ops with the pattern; the regex engine is interpreted |
| PCRE2 callouts `(?C)`, `(?Cn)`, `(?C"str")` incl. `(?C{...})` | nothing: a number or a string passed to ONE program-registered host function | during the match at the position; JIT supports callouts (from memory, recheck) | the string is data; the host function is the program's compiled C |
| Oniguruma callouts | callouts "of contents" `(?{...})` and "of name" `(*FAIL)`/`(*name{args})` calling registered C functions | during the match, in progress/retraction hooks | host functions are compiled C; the contents string is data passed to them |
| .NET Regex | no code in a pattern. `MatchEvaluator` delegate in `Replace`; `RegexOptions.Compiled`/source generator compile the regex, not user code into it | the evaluator, after each match | evaluator is compiled managed code (the template-side analogue) |
| Ragel | C (or other host) actions attached to state-machine transitions, entering, leaving, to-state | as the DFA consumes input, no backtracking, no retraction | the machine compiles to C tables/gotos with the actions inlined: COMPILED, DFA |
| re2c | C code per rule (the rule's action), plus `/*!re2c ... */` regions; conditions/tags for captures | after the rule matches (longest-match), once | compiled to C, DFA; the action is post-match by design |
| flex | C action per rule, `REJECT` to retry | after the rule matches, once | compiled tables plus action switch |
| RE2, Rust regex, Hyperscan, Go regexp | none inside a pattern. Hyperscan: a match callback per match; Go/Rust: replace-with-closure at the API | after the match, in the caller | compiled/interpreted engine, user code outside the pattern |

What is not a precedent: Ragel/re2c/flex actions are DFA-world (they run once
per transition or rule, never on a backtracked path, and have no
captures-so-far veto semantics); Perl/PCRE2/Oniguruma are backtracking-world
(vetoes, tentative fires). The post-match mode of section 4 is re2c's
shape on a PCRE2-syntax pattern; the in-pattern mode is PCRE2's shape with
the host function compiled in.

**The claim pcrec could truthfully make:** "an ahead-of-time compiler for
PCRE2-syntax patterns that compiles the pattern's own `(?C{...})` string as
C into the generated matcher". The qualifiers matter: AOT, PCRE2 syntax, the
string compiled into the matcher. The unqualified "first regex with inline
code" is false (Perl, 1990s). **"First PCRE-compatible compiler with inline
C"** is plausible but UNVERIFIED: it is falsified by (a) any existing
PCRE-syntax AOT compiler or JIT that lowers callout strings to native code
(search PCRE2 forks, Hyperscan-derived tools, the Rust/Go ecosystems, regex-to-C
projects), or (b) an existing re2c/Ragel extension taking PCRE2 syntax with
C actions. Before it is used in a README the survey is re-run with the
web (owed, not done here), and the wording stays "believe", not "first".

## 7. Trust and safety

A pattern file with inline C is a PROGRAM. Compiling a third party's
`.rxt` or pattern collection now puts their C into the user's binary, and
running that binary runs it. This is a code-execution vector in a feature
whose D22 stance ("pcrec compiles patterns a developer controls; hostile
patterns are out of scope") assumed patterns were data. D22's own
"Revisit-when" is exactly this: someone runs pcrec on patterns from a source
the developer does not control. The note does not reopen D22 (no sandbox is
proposed) but requires:

- **T1 Opt-in, never default.** A pattern or template containing user C is
  REFUSED unless the invocation enables the module (R-P1, R-T1): a flag or
  config line that is visible in the command line and in the `.rxt` source.
  No environment variable, no auto-detect. A `.rxt` file's enabling
  `features callouts-c` line is in the file, so a reviewer sees it; a
  stricter option is a CLI-only enable (`--allow-inline-c`) that a file cannot
  grant itself (the recommendation: CLI-only for the file kinds that arrive
  from outside, section 8 Q5).
- **T2 Corpus and tool paths never enable it.** Anything that compiles
  pattern collections it does not author (pcrec-bench's loaders, the
  oracle store, `third_party/` data, fuzzers, `--analysis` of exemplar
  files) must never pass the enable; a pattern with inline C in such a
  corpus is a refusal, counted. A test (a check with a way to fail) asserts
  the default refusal for every entry point (CLI, library `pcrec_compile`,
  `.rxt` harness, `--list-*`).
- **T3 A reviewer can see it.** `pcrec --list-callouts FILE` (R-S10) prints
  every segment with file:line, delimiter, DECODED C text and the include
  and declaration lines; a `--print-c-segments` that emits the C alone for
  `grep`/review. The generated `.c` marks each segment with a `#line`
  directive and a one-line comment naming its source (so an artifact review
  sees where user C lives without a source), and the stamp says user C is
  present (R-S7).
- **T4 pcrec itself executes nothing.** The compiler never runs, compiles or
  loads the user's C (no `--check-c` by default, no header opened, R-S2).
  Compiling a third-party file with the module OFF is as safe as today; with
  it ON, the generated C file is the artifact to review before building.
- **T5 No privilege by the file.** A `.rxt` head line cannot widen the
  trust a CLI invocation gave: the enable may narrow, never grant, when the
  file is an input rather than the invoker's own (Q5).
- **T6 Honest documentation.** The guide states the model in one paragraph
  (a pattern file with C is code: review it, build it as you would a
  dependency) and names Perl's `use re 'eval'` as the precedent.
- **T7 The two sides differ in risk, not in kind:** a template's C runs at
  render time in the user's process, a pattern's C at match time on every
  subject. Both run with the program's privileges; neither needs a different
  gate.

## 8. Open questions for Frank (plain words, each with a recommendation)

1. **One feature or two?** The pattern side (C inside the regex, VM unless the
   post-match mode applies) and the template side (C in a substitution
   template, no engine impact) have different costs, risks and test needs.
   Recommendation: SPLIT. Template side first: it needs no VM, no engine
   analysis, a smaller abi footprint, and it covers the lookup/transform/hex
   needs. The pattern side follows, behind [M4-CALLOUTS]'s named-binding
   primitive that it rides.
2. **Does inline C ride the planned callout primitive or replace it?**
   [M4-CALLOUTS] plans a NAMED extern binding (`rx_callout_ref`). An inline
   segment is an anonymous function that the generator binds itself.
   Recommendation: inline C is a SECOND spelling for the same call site
   (the generated function is the binding), so one call-site emitter,
   one fire contract, one test population. Do not build a parallel
   mechanism (the "general mechanisms, not special cases" rule).
3. **The brace rule on the pattern side.** To keep the file valid PCRE2, a
   `}` in your C has to be written `}}` (or use another delimiter such as
   `$...$`). That is ugly for code with loops. The alternative (a C-aware
   scan that handles nested braces) breaks PCRE2 validity for the same text
   and risks reading the same pattern two ways. Recommendation: PCRE2's rule
   on the pattern side, strictly; push the user to `(?C$ ... $)` or to
   calling a helper function (UC-3) for anything with braces; a C-aware rule
   on the template side, where PCRE2 has no say.
4. **Post-match mode: which semantics?** `post` (reject and resume, refused
   unless provably equivalent) versus `verify` (optimistic DFA, falls back
   to the VM on a veto, always equivalent). Recommendation: build `verify`
   first, because it can never give a wrong answer; add `post` only when a
   measured pattern shows the fallback cost matters. Do you want one flag
   per pattern or per callout?
5. **Where does the enable live?** A line in the `.rxt` file (visible but
   grantable by whoever wrote the file) versus the command line only.
   Recommendation: CLI-only `--allow-inline-c`, which a `config`'s `pcrec`
   line may carry in the author's own repo; never granted by a bare head line
   of an included or third-party file.
6. **Return convention.** PCRE2's (0 continue, positive fail, negative abort)
   versus the existing native one (length/-1). Recommendation: PCRE2's for
   inline segments (a user copying a pattern from a PCRE2 program must get the
   same behaviour), mapped by the generated wrapper; and decide abort
   (D38 says none in v1) before this ships.
7. **How much sugar?** Named-group constants and `RX_CAP_S(n)`-style macros
   are generated identifiers (no parsing of the user's C). Text rewriting
   such as `$1` inside C would need a C lexer. Recommendation: macros and
   generated constants only; no `$1` in C. The template side's group
   declaration (R-T3) is the one place a declaration list or a scan is
   unavoidable.
8. **Do you want the "first PCRE-compatible compiler with inline C" claim
   in the README?** Recommendation: not until the survey is re-run with the
   web (section 6); then "believe" wording.

### Frank's answers (recorded as given)

- **Q1 (2026-10-26): PATTERN SIDE FIRST** (not the recommended template-first split). Frank: "Pattern first. The pcrec syntax might also be to support high level languages embedded so it might be different from what we're doing." Consequence for the design: the embedding spelling is a pcrec syntax decision, not necessarily PCRE2's `(?C{...})` callout string, and it must leave room for a LANGUAGE TAG (C first; other embedded languages later). Q3 (the brace rule) is reopened under that frame.

- **Q2 (2026-10-26): AGREED, one call site.** Inline code is a second way to supply the function at [M4-CALLOUTS]'s call site (one emitter, one fire contract, one test population); each embedded language only has to produce a callable function (C directly, others through generated glue). Consequence: the callout call site is the first build step of the pattern side.

- **Q3 (2026-10-26): BOTH SPELLINGS, one node.** Frank: "Why can't we do both? We have duplicate spellings elsewhere." (a) the PCRE2-valid string callout with a language tag and a user-chosen delimiter (e.g. ``(?C`c: ... `)``), and (b) a pcrec/Perl-style `(?{ ... })` (PCRE2 rejects it today: "unrecognized character after (? or (?-"; Perl reads it as embedded code). Both parse to the SAME callout-site node, like the existing duplicate spellings (`(?<n>)`/`(?P<n>)`/`(?'n')`). The design note decides (b)'s end rule (balanced braces with the language's strings/comments skipped, C first) and how (b) carries a language tag.

- **Q4 (2026-10-26): AGREED.** `verify` first (DFA finds the match, the segment runs on it; on a veto the region re-runs on the VM with the segment inline: always PCRE2-equivalent); `post` only when a measured pattern needs it. The mode is set PER SEGMENT, not per pattern.

- **Q5 (2026-10-26): command-line opt-in PLUS per-include pinning.** Frank: "Yes you need a command line option. But also, you should opt in to embedded code in referenced rx from included files... You could also have a sha in the include line as a version so that should the library change you have to reinspect it and update the version sha. Not including the sha version in the include line means embedded c is not allowed. Perhaps local rxt is exempt." So: (1) a CLI option enables embedded code at all; (2) embedded code from an INCLUDED file runs only when its include line carries a content hash of that file, and only while the hash matches (a changed library fails until re-inspected and re-pinned); (3) an include without a hash may still supply patterns, but any embedded code in it is refused; (4) "local" files may be exempt. The design note defines "local" (leaning: the top-level file(s) named on the command line; anything reached through an include needs a pin), the hash (leaning: SHA-256 of the included file's bytes), and transitivity (leaning: each include line pins its own target; a pinned file's own includes need their own pins).

- **Q6 (2026-10-26): pcrec's NATIVE convention** (not the recommended PCRE2 one). Frank: "How about it returns pcrec default so we can use regex artifacts as callouts. Then, use a pcre2 compatibility macro or similar for outside fns. Honestly, I doubt this would ever come up." So an embedded segment returns what a pcrec matcher returns (length consumed, or -1 for no match), which lets a compiled regex artifact BE a callout (composition); PCRE2-convention functions plug in through a provided compatibility macro/wrapper. Abort: none in v1 (D38 stands); the design note reserves a code for it if a need is ever measured.

### What the later design note must decide

1. The module names (`callouts-c`, `subst-c`) and the flag spelling for post-match
   and its strengths; default-off confirmed.
2. The pattern-side segment spelling accepted (`{ }` only, or all PCRE2
   delimiters) and the abort semantics for a negative return.
3. The generated function's name, signature and the macro/identifier set
   (`RX_CAP_S`, named-group constants, `RX_CO_*`, the template's `RX_G`,
   `RX_PUT`), and the user-state pointer (R-P7).
4. The `rx_ctx` change for the match start (abi event), or slot 0's start.
5. `cinclude`/`cdecl`/`clink` spellings in `.rxt`, the CLI and `config`,
   and how the harness and `examples/makefile/` carry user sources (R-S2/S3).
6. The `#line` and diagnostic plan (R-P9), and whether `--check-c` exists.
7. The end-of-segment scanner: the per-row test table of R-S4 for the
   template form (comments, literals, digraphs, depth), and the one rule for
   the pattern form.
8. The template group-declaration mechanism (R-T3) and the once-per-match
   protocol against the sizing pass (R-T5).
9. The post-match eligibility table (named predicates, deny per row) and its
   reuse of the compound's unique-end admission rule; the snapshot mechanism
   for non-tail callouts (against [CAP-SPAN] and [MATCH-EVENTS]).
10. The test plan: the differential adapter, engine-relative case marking, the
    refusal-by-default check for every entry point, and a way for each check
    to fail (the check-design lessons).
11. The abi movers, counted by GREP, and the spec hunks (R-S7, R-S8).
12. What the template segment does on "no bytes" and "fail" (R-T6, DT-2.3).
