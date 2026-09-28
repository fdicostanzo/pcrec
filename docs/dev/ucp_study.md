# [UCP] — THE STUDY: demand, oracle semantics, and three ideas, measured

Lane `ucpthink` (opus), branch `lane/ucpthink`, worktree `worktrees/ucpthink`,
on `main` at `13b7c202`. **Study only**: nothing under `src/`, `tests/` or
`docs/spec/`, no design and no decision. The UCP design and implementation are
a later scheduled task (plan row [UCP], Frank 2026-09-28). This memo is the
"thinking and testing now" that row asks for.

Every probe, transcript and census is committed under `studies/ucp_study/`
(its `CLAUDE.md` says how to reproduce each). Oracle numbers come from
**libpcre2 10.46** (the reference, `ubuntubudu` over the tailnet, light
ssh-stdin probes that write nothing on the remote box) and **10.48** (local
Homebrew). Every relation below holds on both versions. Only the set SIZES
differ, because the two versions ship different Unicode versions. pcrec
numbers are from this worktree's own `build/pcrec` (abi 43), on the Mac,
`gcc-16 -O2`. Sizes are object `__text + __const/__cstring/__literal8`, using
the same rule as `cls_tree_study.md` so the two memos compare. No timing
number appears anywhere. Darwin timing is not citable, and nothing here needs
it.

---

## 0. Headlines

1. **Demand is dominated by `\b`.** UCP changes `\w \d \s \b \B` and the
   POSIX classes. In the pcrec corpus, 185 unique patterns use one of these,
   and 115 of them (62%) use `\b` or `\B`. In 98 of those 115, `\b`/`\B` is
   the ONLY UCP-sensitive construct. The bench is more realistic: 91
   sensitive patterns, of which 29 (32%) need `\b`, and **46 (51%) need only
   `\d`/`\s`/small POSIX sets**, the cheap tier. No real-world UTF-8 pattern
   harvest exists yet ([UTF-RW] is not started), so the only true UCP demand
   on file is the bench's five designed `(*UCP)` twins. What the
   wild-sourced bench patterns look like is §A.3.
2. **The oracle semantics are simple and exactly property-shaped.** Under
   `PCRE2_UCP`, 10.46 gives `\w ≡ \p{Xwd} ≡ [\p{L}\p{N}\p{Mn}\p{Pc}]`
   (Mn and Pc ARE in, 2,029 code points beyond `[\p{L}\p{N}_]`),
   `\d ≡ \p{Nd}`, and `\s ≡ \p{Xsp} ≡ \p{Xps} ≡ [\h\v]`. Every POSIX class
   maps to a property or property union, and `[:xdigit:]` gains the 22
   fullwidth hex digits. **UCP does not change caseless LITERAL folding
   under UTF.** It changes exactly two caseless things: POSIX
   `[:lower:]`/`[:upper:]` STOP folding at all under UCP, while
   `(?i)\p{Ll}` folds with or without UCP. And without UTF, UCP turns on
   Latin-1 folding (30 pairs).
3. **`\b` IS its lookaround spelling, exactly.** The test used 579,195
   subjects over a 14-character alphabet mixing ASCII, 2/3/4-byte word
   characters (including Mn and Pc members) and 2/3/4-byte non-word
   characters, in three modes (bytes, UTF, UTF|UCP), for `\b` and `\B`, on
   both library versions: **0 disagreements**. pcrec's own `\b` (DFA and
   VM) and its lookaround spelling (VM) give answers identical to libpcre2
   on all 12 streams, under `-e byte` and `-e utf8`. As a REWRITE, though,
   the spelling moves **85% of the \b population off the DFA** (111 of
   130, no-captures census). Spelled with `\p{Xwd}` for UCP, it is
   **REFUSED on every engine today** (2.28 MB of emitted VM code against
   the 500 KB cap).
4. **The head-state idea already has a mechanism that fits it.** It is not
   the scan edge itself. It is the DFA's POSITION-VIEW selector (`eolvar` /
   `endvar`): a runtime predicate on `(subject, pos)` that picks a variant
   state, and minimization already treats it as an extra alphabet symbol. A
   UCP `\b` is one more predicate of that shape: decode the previous and
   next character and compare their word-ness. The predicate reads the
   SUBJECT, not the machine, so it is direction-independent and the reverse
   pass evaluates it unchanged. [OPT-EDGE]'s top-rows renumbering is how the
   loop would find the states that need it at no generic-path cost (§D).
   **The general form covers 492 of the 1,101 no-captures VM-routed corpus
   and bench patterns (45%)**, those whose only DFA-excluding constructs are
   lookarounds. Its hazard is that an unbounded lookahead evaluated per
   position loses linearity.
5. **[CLS-TREE] is a hard prerequisite, and measurably so.** `\p{Xwd}`
   costs 197,685 object bytes on the DFA today, against 2,035 for ASCII
   `\w` (97×) and ~5.3 KB as a kit matcher. On the VM it is REFUSED
   (576 KB > 500 KB cap). So **any captured UCP `\w`, such as `(\p{Xwd})`,
   cannot be built today**, because captures route to the VM.
   `\p{Xwd}+` takes **66 s** to compile, 99% in subset construction's
   closure (sampled). The [CLS-TREE] kit is itself a code-point matcher,
   so for the DFA it needs the SAME insertion mechanism as idea 1 (its plan
   row's item (2), "tree-classes as a rung/edge in the hybrid"). **Ideas 1,
   2 and [CLS-TREE]'s DFA seam are one mechanism.**

Side findings, outside UCP but found here (§G): **`(?r)` is silently
ignored under `-e utf8`**, a four-cell answer divergence from 10.46. The
`RX_ENGINE_WHY` stamp names one construct's kind at another construct's
offset. `\p{Xwd}` on the DFA is 33% smaller than the CLS-TREE study measured
at `13b56a12`.

---

## A. DEMAND

### A.1 Population and method

`studies/ucp_study/census.py` enumerates every `pattern`/`pattern-esc` block
of every `.rxt` under `tests/` and `examples/` (240 files; `--list-source`,
with each file's head `encoding`/`flags` rows applied, `config`/`with`
cascades not resolved) plus every `bench/*/patterns/*.rx` in pcrec-bench (read
only). That gives **4,394 rows and 3,659 unique (pattern, encoding,
caseless)** triples, 3,359 corpus and 331 bench. Features are LEXICAL (a
class-aware tokenizer: `\b` inside a class is backspace, POSIX names are read
inside classes only, `\Q..\E` is skipped), so a count is "the pattern spells
it", not "the construct is reachable". The corpus includes the reject tables,
so a few POSIX names are junk (`[:foo:]`, `[:<:]`). They are counted and
harmless. Tables: `census_analysis.txt`.

### A.2 What the patterns need

| population | n | UCP-sensitive | `\w` | `\d` | `\s` | `\b` | `\B` | POSIX | needs `\b`/`\B` | `\b`/`\B` the ONLY sensitive construct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| corpus, all | 3,359 | 185 (5.5%) | 39 | 22 | 4 | 77 | 43 | 27 | **115 (62%)** | 98 |
| corpus, utf8 blocks | 292 | 9 | 4 | 0 | 0 | 0 | 3 | 2 | 3 | 3 |
| bench, all sets | 331 | 91 (27.5%) | 17 | 38 | 19 | 27 | 2 | 2 | **29 (32%)** | 23 |
| bench/utf8 | 75 | 12 | 2 | 2 | 3 | 3 | 1 | 1 | 4 | 4 |

**The partial-UCP split** (`census_analysis.txt` §A2). "Small sets" means
only `\d` (Nd, 71 intervals), `\s` (Xsp, 11) and the small POSIX names
(digit, space, blank, cntrl, xdigit). "Big set" means `\w`, `\b`, `\B`, or
alpha/alnum/word/lower/upper/graph/print/punct, each of which is `\p{Xwd}`-
or `\p{L}`-sized.

| | sensitive | small sets only | big set, no `\b` | needs `\b`/`\B` |
|---|---:|---:|---:|---:|
| corpus | 185 | 28 | 42 | 115 |
| bench | 91 | **46** | 16 | 29 |

**Case interaction.** 11 corpus and 4 bench sensitive patterns are also
caseless. Of these, the one cell where UCP×CASELESS actually changes an
answer (caseless `[:lower:]`/`[:upper:]`, §B.3) appears in 5 corpus
patterns and 0 bench patterns. Its oracle sits in the modifiers/classes
corpus, not in any realistic set.

**Verbs.** The only start-of-pattern verbs in the whole population are the
bench's five `(*UCP)`s. The corpus has none.

### A.3 The real-world question, answered as far as the tree allows

**There is no real-world UTF-8 pattern harvest in either repository.**
[UTF-RW] (plan.md:225) is chartered and not started, and pcrec's
`tests/utf8/` is designed axis coverage (0 sensitive patterns with non-ASCII
bytes). The bench's five `(*UCP)` patterns are DESIGNED twins (O-71; the
utf8 set's `cls-w-ucp`, `cls-d-ucp`, `cls-s-ucp`, `ci-ucp-invariance`,
`asr-b-cyr-ucp`). Classified: `\w` 1, `\d` 1, `\s` 1, `\b` 1, and 1
caseless literal that is the invariance CONTROL. That control is already
answered by pcrec without UCP (§B.3), so it would pass the day `(*UCP)` is
merely recognised.

The nearest thing to real-world evidence is `bench/capability`'s 29
wild-sourced patterns and the SEMANTICS OF THE ECOSYSTEMS THEY CAME FROM.
Those semantics are general knowledge, **not verified by this lane**. They
are a question for the design pass to check, not a finding:

| provenance | wild patterns | UCP-sensitive ones | origin `\w`/`\b`/`\d` semantics |
|---|---:|---|---|
| rebar-wild (noseyparker secrets, datefinder) | 5 | aws-key `\b`, github-pat `\b`, user-pass `\s`, datefinder `\d \s` | Rust `regex`: Unicode by default |
| vscode-json-grammar (TextMate/Oniguruma) | 5 | json-constant `\b`, json-number `\d` | Oniguruma on UTF-8: Unicode by default |
| grok | 7 | syslogbase `\b \d` | Logstash/Joni: probably Unicode |
| moment-js | 1 | iso8601 `\d \s` | JS: `\d`/`\w`/`\b` ASCII, `\s` Unicode (NOT PCRE's Xsp: JS includes U+FEFF) |
| crs (ModSecurity) | 5 | 942140/942360 `\b` (caseless) | PCRE without UCP: ASCII, as pcrec is |
| owasp-validation | 3 | us-zip `\d` | Java: ASCII unless UNICODE_CHARACTER_CLASS |
| pcre2-testdata, rust-regex-testdata | 3 | 1 `\d` | as tested |

So **at least 7 of the 29 wild patterns carry UCP-sensitive constructs whose
origin reads them as Unicode.** An import of those into pcrec under `-e utf8`
today gets the ASCII reading, and the answer differs whenever a subject puts
a non-ASCII letter or digit next to the token. That is the practical UCP
demand: **silent drift for imported patterns**, not users writing `(*UCP)`.
Whether the bench's subjects exercise it is a bench question (for pcrecdev2,
not this lane).

---

## B. SEMANTICS BY ORACLE

Probes: `classify.c` (1.1M code points × 39 patterns × {UTF, UTF|UCP}, local
C) and `classify_remote.py` (the same question as ONE `pcre2_substitute` per
pattern, deleting every non-member from an all-code-points subject; the two
methods agree byte for byte on 10.48, then the Python one ran on 10.46). The
relations are computed by `analyze.py` (`analyze.out`). The point probes are
`probe_misc.py` and `latin1.py`. **10.46 and 10.48 agree on every relation
and every point probe.** Only the set sizes differ (Unicode version).

### B.1 What UCP changes, as sets (10.46 sizes)

| construct | without UCP (UTF) | with UCP | equal to |
|---|---:|---:|---|
| `\w` | 63 | 144,969 | `\p{Xwd}` ≡ `[\p{L}\p{N}\p{Mn}\p{Pc}]` |
| `\d` | 10 | 760 | `\p{Nd}` |
| `\s` | 6 | 26 | `\p{Xsp}` ≡ `\p{Xps}` ≡ `[\h\v]` |
| `\h`, `\v` | 19, 7 | 19, 7 | **unchanged**: already Unicode under UTF |
| `[:alpha:]` | 52 | 141,028 | `\p{L}` |
| `[:digit:]` | 10 | 760 | `\p{Nd}` |
| `[:alnum:]` | 62 | 142,939 | `\p{Xan}` |
| `[:space:]` | 6 | 26 | `\p{Xps}` |
| `[:word:]` | 63 | 144,969 | `\w` |
| `[:lower:]` / `[:upper:]` | 26 / 26 | 2,258 / 1,858 | `\p{Ll}` / `\p{Lu}` |
| `[:blank:]` | 2 | 19 | `\h` |
| `[:cntrl:]` | 33 | 65 | `\p{Cc}` |
| `[:punct:]` | 32 | 864 | `\p{P}` ∪ (`\p{S}` ∩ ASCII) |
| `[:xdigit:]` | 22 | 44 | ASCII hex + the 22 fullwidth hex digits (U+FF10-19, FF21-26, FF41-46) |
| `[:graph:]` / `[:print:]` | 94 / 95 | 154,973 / 154,991 | not reduced to a formula here (PCRE2 special-cases them) |

**Mn and Pc joined `\w` in 10.43, and 10.46 has them**: `\w` minus
`[\p{L}\p{N}_]` is 2,029 code points, starting U+0300. The `\p{...}` sets
themselves are UCP-independent (`\p{Xwd}` etc. identical with and without
UCP), which is what lets pcrec's existing `unicode-props` tables serve UCP
unchanged. **The UCP `\w` is 930 intervals and 144,906 of its members are
above 0x7F.**

### B.2 `\b`

`\b` reads UCP's `\w`. Under UTF without UCP it reads ASCII `\w` (§C proves
both exhaustively). The bench's own pair confirms it: `\bМосква\b` on
" Москва " is nomatch under UTF and (1,13) under UTF|UCP.

### B.3 Caseless interaction: two cells, both narrow

| probe | UTF | UTF\|UCP |
|---|---|---|
| `(?i)é` vs `É`; `(?i)k` vs U+212A; `(?i)[a-z]` vs U+017F | match | match: **caseless literal folding under UTF is Unicode with or without UCP** (the bench's `ci-ucp-invariance` control is right) |
| `(?i)[[:lower:]]` vs `A` | match | **nomatch**: under UCP, caseless does NOT apply to `[:lower:]` (it is exactly `\p{Ll}`, 2,258) |
| `(?i)[[:lower:]]` vs `É` | nomatch (the non-UCP fold is ASCII-only) | nomatch |
| `(?i)\p{Ll}` vs `A` | match | match: `(?i)\p{Ll}` ≡ `(?i)\p{Lu}` = Lu∪Ll∪Lt (4,147; the extra 31 are Lt) |

So under UCP, `(?i)[[:lower:]]` and `(?i)\p{Ll}` DIFFER even though
`[[:lower:]]` ≡ `\p{Ll}` without `(?i)`. A construction that lowers
`[:lower:]` to `\p{Ll}` BEFORE applying the fold would get this wrong. That
is the one UCP×CASELESS trap.

**Without UTF** (what a `(*UCP)` under `-e byte` would owe, `latin1.py`):
UCP makes the bytes Latin-1 code points. `\w` becomes 134 bytes (71 above
0x7F), `\s` adds 0x85 and 0xA0, `\d` is unchanged, `[:alpha:]` becomes 117
bytes, `[:punct:]` 39, and `\b` follows `\w` (`x\b` on `x\xE9`: match
without UCP, nomatch with it). **`CASELESS` alone folds only ASCII.
`UCP|CASELESS` folds 30 Latin-1 pairs** (utf8_design.md §4.5's measurement,
re-confirmed on 10.46). Every one of these is a 256-bit set, so a byte-tier
UCP is cheap. It is still NOT a no-op, so a `(*UCP)` under `-e byte` cannot
be accepted and ignored.

### B.4 The verbs and PCRE2's own partial-UCP knobs

- `(*UCP)` must be at the pattern's start, before any option setting.
  `(?i)(*UCP)` is a compile error, and so is `a(*UCP)`. It combines with
  `(*UTF)` in either order and is valid without UTF.
- **PCRE2 10.43+ already ships a partial UCP**: `(?aD)`, `(?aS)`, `(?aW)`,
  `(?aP)`, `(?aT)` and `(?a)` restrict `\d`, `\s`, `\w`, POSIX, and POSIX
  digit/xdigit to ASCII under UCP. `\b` follows `(?aW)` (`(?aW)x\b` on
  `xé`: match). pcrec ACCEPTS all six today as no-ops
  (`src/parse/mod_modifiers.c:407`). That is correct without UCP, because
  they only restrict UCP, and the compliance record says so. It stops being
  correct the day UCP exists.
- `(?r)` (caseless-restrict) is NOT a UCP knob, but it IS real under UTF
  without UCP. See §G.1.

---

## C. `\b` AS A REPLACEMENT FORM (Frank's idea 3)

### C.1 The equivalence, per libpcre2: exact

`bequiv.py` uses a 14-character alphabet: `a _ 5` (ASCII word), space and
`-` (ASCII non-word), `é` (2-byte L), `٣` (2-byte Nd), U+0301 (2-byte Mn,
word under UCP only), `日` (3-byte Lo), `‿` U+203F (3-byte Pc, UCP only),
U+20000 (4-byte Lo), NBSP (2-byte Zs), `€` (3-byte Sc), U+1F600 (4-byte
So). It runs every string of length 0..5 (579,195 subjects, empty included,
so the edge-of-subject positions are covered). For each subject, ONE
`pcre2_substitute` marks every position where the zero-width pattern
matches. `\b` is compared against `(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))`, and
`\B` against `(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))`:

| mode | `\b` positions holding | disagreements | `\B` positions holding | disagreements |
|---|---:|---:|---:|---:|
| no flags (bytes) | 1,013,364 | **0** | 5,676,021 | **0** |
| UTF | 1,013,364 | **0** | 2,417,253 | **0** |
| UTF\|UCP | 1,788,048 | **0** | 1,642,569 | **0** |

The table is identical on 10.46 and 10.48, down to the sha1 of the marked
output (`bequiv_10.46.txt`, `bequiv_10.48.txt`). Two further facts sit in
the table. **Bytes and UTF give the same `\b` marks** (sha1
`37d5403a56d3`): §5.4's LEG 1, measured rather than argued. A byte-level
`\b` never fires inside a multi-byte character, because both sides are
non-word bytes. **UCP raises the `\b` count by a net 774,684 positions**. That is
the difference the upc_of_class mechanism cannot express.

Composition needs no separate sweep. Both spellings are zero-width,
capture-free and atomic (PCRE2 lookarounds are atomic), and each one's truth
is a function of (subject, position) alone. So substituting one for the
other inside any pattern changes no answer.

### C.2 pcrec today: answers agree, engines do not

`run_bdrive.sh` compiles six artifacts per encoding: `\b` auto, the
lookaround spelling auto, `\b --engine=vm`, and the same three for `\B`.
`pcrec_bdrive.c` drives each over the SAME alphabet and order and prints
bequiv's marked stream (`bdrive_main.txt`):

| encoding | artifact | engine (stamp) | sha1 of stream | = libpcre2? |
|---|---|---|---|---|
| byte and utf8 | `\b` auto | dfa `selected` | `37d5403a56d3` | yes |
| byte and utf8 | lookaround `\b` | **vm** `declined-nullable-default` | `37d5403a56d3` | yes |
| byte and utf8 | `\b` forced VM | vm `forced` | `37d5403a56d3` | yes |
| byte | `\B` ×3 | dfa / vm / vm | `56979cb72385` | yes |
| utf8 | `\B` ×3 | dfa / vm / vm | `594c96035f53` | yes |

**All 12 streams agree with libpcre2 on all 579,195 subjects.** pcrec's `\b`
and its lookaround spelling are answer-identical. The rewrite is sound
today, under non-UCP.

### C.3 What the rewrite costs: the DFA population

The census compiled every `\b`/`\B` pattern three ways: at its own encoding,
under `-e utf8`, and with the rewrite (`census_*_analysis.txt` §C):

| census | \b patterns (compiled) | DFA today (own enc = utf8, identical) | VM after rewrite | **moved DFA→VM** |
|---|---:|---:|---:|---:|
| default (captures ON) | 130 | 95 | 129 (+1 REFUSED) | **94 (72%)** |
| `--no-captures` | 130 | 112 | 129 (+1 REFUSED) | **111 (85%)** |

The one refusal is `altwide/wb-512`. Its rewrite exceeds the 1 MB emit
cap. On the bench, the DFA-route `\b` patterns that would move are the
realistic ones: loglines `bignum`, `hex32-id`, `uuid`, `kv-quoted`,
`stack-frame`, `http-5xx`; capability `json-constant`, `aws-access-key-id`,
`github-pat`, WAF CRS 942140/942360; altwide `wb-256`/`wb-512`.

Four of them, rewritten under `-e utf8` (`rewrite_sizes_13b7c202.tsv`):

| pattern | original | rewrite | object bytes |
|---|---|---|---|
| loglines/bignum `\b[0-9]{10,19}\b` | dfa | vm + hybrid prefilter | 3,053 → 5,651 (×1.85) |
| loglines/uuid | dfa | vm + hybrid | 5,407 → 7,535 (×1.39) |
| capability/json-constant `\b(?:true\|false\|null)\b` | dfa | vm + hybrid | 3,913 → 6,123 (×1.56) |
| utf8/asr-b-cyr `\bМосква\b` | dfa | vm + hybrid | 3,615 → 6,143 (×1.70) |

Throughput is **not measured** (darwin). The per-search cost of moving a
DFA-route pattern onto VM+prefilter is a bench question. The prefilter keeps
the DFA on the candidate side, so the loss is the verification pass.

**Under UCP the rewrite is not buildable at all today.** The spelling over
`\p{Xwd}` is REFUSED on every engine: 2,275,105 bytes of emitted VM code
against the 500,000 cap, and `--engine=dfa` refuses the lookaround
(`sizes_13b7c202.tsv`). Idea 3 therefore depends on [CLS-TREE] even before
the engine question.

**Reading.** As a TEXT rewrite, idea 3 is correct and cheap to state. It
costs the DFA route for ~3/4 of `\b` patterns, and it needs a buildable
`\p{Xwd}`. As a DEFINITION, "`\b` means this lookaround pair", it is the
cleanest statement of what an inserted check must compute, and §D uses it
that way.

---

## D. VM INSERTION VIA HEAD STATES (Frank's ideas 1-2): a sketch

### D.1 Today's mechanisms, precisely

**How ASCII `\b` works on the DFA today (the thing UCP breaks).**
- The alphabet is refined by the word set first: `src/ir/dfa.c:177`,
  `refine_by(d, ncls, pcrec_cls_word_esc)`. So every byte class is
  homogeneous in word-ness.
- `upc_of_class` (`src/core/internal.h:3654`) reads a class's
  REPRESENTATIVE byte to answer "the byte about to be consumed is a word
  byte". That is the forward side, the class VIEWS `DState.up[UPC_N]`
  (`internal.h:1761`). The transition row bakes the choice in: "`tr[c]` is
  built from `up[upc_of_class(c)]`" (`internal.h:1749`).
- The CONSUMED side is carried in state IDENTITY (pre-sets that differ in it
  intern apart). It seeds through `Dfa.s1u[UPC_N]` (`internal.h:1859`).
- Both sides are one BYTE. Under UCP both are one CHARACTER (1-4 bytes), so
  the representative is a sample, not a proof. That is utf8_design.md
  §5.4.1 LEG 2, and §C.1's net +774,684 positions are its size.

**The scan edge ([OPT-5] STEP 1, `src/opt/scanedge.c`).**
- A chain of states that are scan-shaped for one class C and a uniform exit
  E (`scanedge.c:1-120`, the five preconditions) collapses to its HEAD.
- The emitter replaces the chain with an address-independent counted loop:
  the VM's cursor shape inside the DFA (opt5_step0_profile.md §3).
- The loop then RESUMES at the fall-through F.
- The head's own class-C cell is set dead, "because the scan owns that
  byte" (`scanedge.c:620`).
- At most `PCREC_MAX_SCAN_EDGES` = 4 per machine (`limits.def:383`).

**[OPT-EDGE] STEP 1's shared sentinel.**
- The compaction permutation moves the surviving heads to the machine's TOP
  rows (`scanedge.c:624-666`).
- The dead sentinel already sits above every live cell in both
  representations: premultiplied dead is 65535, and indexed dead is -1 read
  unsigned. So "dead or a head" is ONE compare,
  `(unsigned)s >= FLOOR` with `FLOOR = cell_of(n - nheads)` (`token_stop`,
  `src/gen/emit_dfa.c:4651`).
- The emitter checks this layout rather than assuming it
  (`emit_dfa.c:7016-7040`).
- The generic path pays nothing per edge. The EDGE path is entered from
  that one stop test.

**The position views, which are the closer precedent.**
- `DState.eolvar`/`endvar` (`internal.h:1762-1776`) are VARIANT STATES:
  the same pre-set closed under a different assertion truth (`$`, `\z`).
- The emitted loop's AXIS C "view selector" (`emit_dfa.c:4888ff`) evaluates
  a predicate on `(subject, pos)` and swaps the state for its variant,
  e.g. `pos + 1 >= n && ... subject[pos] == '\n'`.
- Minimization treats each view link as an extra alphabet symbol
  (`src/opt/minimize.c:4-16, 49-61`).
- Scan edges refuse any state carrying a view (precondition (3)).

**The pipeline.** For the unanchored search (D7): forward priority DFA →
match END; reverse non-pruning DFA → match START; both minimized, then
scan-edged (`src/core/compile.c:1673-1707`). `ENG_ATTEMPT` (patterns with
`^`) is a per-start computed-goto loop with the same view mechanism.

### D.2 The sketch: a predicate view, dispatched from the top rows

**The inserted check.** `P_b(s, pos) := isword(char ending at pos) !=
isword(char starting at pos)`, false at a missing side. It decodes one
character backward (the `back_step` seam entry, utf8_design.md §5.2) and one
forward (`next_pos`), and tests each against the word set: a [CLS-TREE] kit
matcher, or today's `\p{Xwd}` in whatever form is buildable. **It is a pure
function of the subject and the position**, and that property carries the
rest of the sketch.

**Construction.**
- Subset construction closes each pre-set TWICE where its closure crosses
  a `\b`/`\B` node: once with the boundary true, once false.
- If the closures differ, the state gets a `bvar` link, a third view kind
  beside `eolvar`/`endvar`, exactly as `$` does today.
- All `\b` and `\B` nodes read the SAME bit at a position, so one
  predicate gives at most one extra variant per state.
- The class-view word context (`upc_of_class`'s `UPC_WORD`) is simply not
  used for a UCP machine. This is "replaced, not extended", as §5.4.1 said
  it must be, but the replacement is a general mechanism rather than a
  word-specific one.

**Dispatch (idea 1).**
- States with a live `bvar` are renumbered into the top-row range with the
  scan-edge heads, the same permutation, one more key. The generic path's
  single `(unsigned)s >= FLOOR` test then also catches "this state needs its
  predicate".
- The edge path evaluates `P_b` and swaps the state for its variant, then
  rejoins, like the view select does.
- This is the scan-edge protocol with TWO fall-throughs and zero consumed
  bytes instead of one fall-through and a counted run.

**What must survive the exit and the resume.** Only `(state, pos)`: the
check reads the subject and returns a bit. No match-so-far context crosses
the boundary, because the DFA's accept bookkeeping (last accept position)
never enters the check. That is the difference from a general "VM island"
that must carry captures or a backtracking stack. A check with NO state
passing is the cheapest insertion that exists.

**The reverse DFA and the two-pass search.** The reverse NFA contains the
same assertion nodes and gets the same `bvar` treatment. Because `P_b` reads
the subject at an absolute position, the reverse walk evaluates the identical
predicate at the identical positions. There is no forward/reverse view swap
of the kind `upc_of_class`'s two sides need (`internal.h:1720`'s "the forward
and reverse machines swap which side is which"). The forward end and the
reverse start therefore agree by construction. `ENG_ATTEMPT` gets the same
view.

**Minimization and state identity.**
- `bvar` is one more alphabet symbol in minimize.c's partition refinement,
  the `eolvar` precedent.
- State identity grows by at most ×2 on states whose closure crosses `\b`.
  That is far cheaper than the exact alternative (below).
- Scan edges keep refusing view-bearing states. [OPT-VEDGE], the
  view-tolerant edge, is the row that would relax that.

**The exact alternative, for contrast.** UCP `\b` IS regular over bytes (the
word set is a finite set of byte strings). An exact DFA could carry "the
previous character was a word character" by tracking the lead/continuation
bytes of the character just consumed, and take the product with the
`\p{Xwd}` UTF-8 byte automaton for the lookahead side. It needs no runtime
check, but it multiplies every state crossing `\b` by that automaton's
states (the 197 KB table of §E). RE2 declines Unicode `\b` outright. Rust's
regex-automata handles it in its DFAs only HEURISTICALLY: a
`unicode_word_boundary` config makes the DFA QUIT on any non-ASCII byte and
the meta engine falls back to another engine (general knowledge, not
re-verified here). That quit is a coarse version of exactly this
exit-to-another-form idea.

**Hazards, named.**
- **(H1) Per-position cost when `\b` is at the start.** An unanchored
  scan's start thread crosses a leading `\b` at EVERY position, so the
  predicate runs per byte: two decodes and two set tests. It stays O(n) with
  a larger constant. It is still cheaper than the whole pattern on the VM,
  which is today's alternative. The prefilter keeps most positions away from
  it.
- **(H2) Candidate-start prefilters and the skip loops** (stay skips, scan
  edges) assume a state's behaviour at a byte depends on the byte's class
  alone. Any state with a live view must be excluded from them, as
  `pick_skip_states` and scanedge's (3) already exclude view states. That is
  a real throughput cost for `\b`-dense machines.
- **(H3) The predicate must agree with the automaton's ill-formed-byte
  rule** (utf8_design.md §2.6). A decoder that reads an ill-formed
  neighbour differently from the automaton re-opens K50's class of bug. The
  [CLS-TREE] row's item (1) names the same seam: "the class test's decoder
  rejects exactly the automaton's ill-formed set".
- **(H4) Premultiplied-table capacity.** Doubling states counts against
  `PREMUL_MAX_ENTRIES`.
- **(H5) The seam's `back_step` becomes a hot-path read**, not only a retry
  path. That is its width finding (utf8_design.md §5.2) under load.

### D.3 The general question: what forces a pattern off the DFA, and which could be a check

A pattern's route is recorded by its engine stamps. There are two censuses
over the same 3,659 unique rows, the default and `--no-captures`, because
captures are ON by default and dominate everything else:

- **Default:** 1,647 VM, of which **949 are `capture group`**. That share
  is not reachable by any inserted check. It is [ENG-TACTICS]' and the
  one-pass-DFA ranking's territory (captures_via_dfa_survey.md).
- **`--no-captures`:** 1,101 VM (`census_nocap_analysis.txt`). The WHY
  stamp names only the FIRST excluding row, so §D2 of that file also reads
  EVERY excluding family per pattern lexically.

| family set present (no-captures VM rows) | rows | inserted check? |
|---|---:|---|
| lookahead only | 179 | **yes**: a position predicate. Bounded bodies are O(w). Unbounded bodies are a sub-search per position (**H6: linearity lost**) |
| lookbehind only | 176 | **yes**: bounded by construction (pcrec refuses variable-length); a reverse anchored run of ≤ w bytes |
| non-atomic lookaround `(?*…)` only | 103 | **yes when capture-free**: with no captures, backtracking into a zero-width group cannot change the outer answer |
| lookahead + lookbehind, + non-atomic mixes | 32+ | yes, several predicates. States get up to 2^k variants over k distinct predicates (**H7**: variant explosion, bounded in practice by which predicates a state's closure actually crosses) |
| backref (± others) | 126+ | **no**: the check needs the CAPTURED SPAN, which the DFA does not track |
| atomic `(?>…)`, possessive | 86 / 43 | **no**: not predicates. They prune the priority order. A different question (a priority-aware subset construction) |
| `\K` | 61 | **no**: moves the reported start, not a predicate |
| call `(?1)` `(?R)` `(?&n)` | 63 | non-recursive calls are a REPLACEMENT FORM (inline expansion), not a check. Recursive: no |
| `${name}` variable | 18 | **yes, as a CONSUMING island**: compare against a run-time value then resume. The scan edge's own shape with a variable run |
| dfa overflow | 8 | not a construct: capacity ([ENG-ISL]) |

**Population: 492 of the 1,101 no-captures VM rows (44.7%) have
lookarounds as their ONLY excluding family**: 475 of 1,055 corpus, 17 of 49
bench. Add UCP's own `\b` and the UCP classes and variables, and the check
family is the largest single VM-forcing group once captures are set aside.
The corpus is a test corpus and over-represents lookaround-module tests. The
bench's 17/49 (35%) is the less biased number.

### D.4 Relation to the rows on file

- **[ENG-ISL]** (plan.md:832, Frank 2026-09-02) already frames "islands of
  VM in DFA". It names the scan edge as the first instance ("the VM's
  address-only counted loop embedded in the DFA scan loop at a head state,
  resuming at a fall-through state") and asks for ONE DEV SOURCE for loop
  bodies both engines read. This IS the "[OPT-5] STEP 3 one-dev-source
  reframing" the charter names: STEP 3's construction-time counted node plus
  [ENG-ISL]'s splice protocol. **Idea 2 is [ENG-ISL] with a new island
  kind**: the ZERO-WIDTH PREDICATE island (two fall-throughs, nothing
  consumed, nothing carried). It is simpler than the consuming islands on
  file, because its exit and resume states are both known at construction
  and it carries no counter.
- **[ENG-TACTICS]** (plan.md:468) composes engines ACROSS a search
  (seed, reverse-start, reverse-then-skip). Insertion composes them WITHIN a
  state walk. They are complementary. The backref and capture populations
  above belong to [ENG-TACTICS], and the predicate population to insertion.
- **[CLS-TREE]** item (2) (plan.md:1562): "a byte-wise DFA cannot search
  mid-state — tree-classes as a rung/edge in the hybrid". A kit matcher on
  the DFA route is a CONSUMING one-character island: decode, test, resume
  at F or dead. **So the DFA side of [CLS-TREE] and ideas 1-2 need the same
  splice.** Whichever lands first builds it.
- **[OPT-VEDGE]** (the view-tolerant edge) becomes relevant because views
  would multiply.

---

## E. THE [CLS-TREE] DEPENDENCY: sizes today versus the kit

`sizes.sh`, `-e utf8 --features all`, per engine (`sizes_13b7c202.tsv`).
Kit numbers are cls_tree_study.md's `mid` policy (§3, results/sweep_uprops.tsv).

| pattern | DFA obj | VM obj | kit (mid) | note |
|---|---:|---:|---:|---|
| `\w` (ASCII, today's meaning) | 2,035 | 1,043 | — | the baseline UCP replaces |
| `\p{Xwd}` (UCP `\w`) | **197,685** | **REFUSED** (576,063 B code > 500,000) | 5,326 | the study measured 294,153 DFA at `13b56a12`; −33% since |
| `\p{Nd}` (UCP `\d`) | 19,151 | 9,383 | 706 | study: 19,109 |
| `\p{Xsp}` (UCP `\s`) | 3,573 | 2,815 | 212 (Xps) | study: 3,531 |
| `\p{Xwd}+` | 330,885, **66 s compile** | REFUSED (1.14 MB) | — | 99% of compile in `make_state`'s closure (sampled) |
| `(\p{Xwd})` (captures default → VM) | — | **REFUSED** (579,674) | — | **any captured UCP `\w` is unbuildable today** |
| `\p{Nd}{4}` | 68,886 | 31,815 | — | |
| `a\p{Xsp}b` | 3,965 | 2,947 | — | |
| lookaround `\b` over `\p{Xwd}` | REFUSED (VM-only construct) | REFUSED (2,275,105) | — | §C.3 |
| `\bМосква\b` (ASCII meaning) | 3,615 | 2,355 | — | |

**What UCP costs WITHOUT [CLS-TREE]:**
- The small tier (`\d`, `\s`, the small POSIX names) is affordable today on
  both engines: 3-19 KB DFA per use, 3-9 KB VM.
- `\w`/`\b` and the letter-POSIX tier cost ~200-330 KB per use on the DFA,
  with minute-scale compiles for a repeated `\w`. On the VM they are
  REFUSED, and so is every captured form.
- So a full UCP without [CLS-TREE] is not "expensive", it is **not
  buildable** for the most common shape (`(\w+)`, `\b\w+\b` with a group).

**What UCP costs WITH [CLS-TREE]:**
- The kit is ~5.3 KB object per `\p{Xwd}` matcher, one matcher per
  artifact if shared, plus a decode per character. It makes the VM route
  work immediately: the VM already decodes (the stage-4 caseless-backref
  precedent).
- On the DFA route the kit is not usable until the insertion mechanism of
  §D exists (a consuming island per class test, a predicate island per
  `\b`).
- Neither the kit's ns/char nor the island's per-position cost is measured
  (cls_tree_study.md §11 owes ns/char on ubuntubudu).

---

## F. OPTIONS (no decision; the ruling is Frank's)

| | (a) no UCP, correct refusal | (b) partial UCP | (c) full UCP |
|---|---|---|---|
| **what ships** | `(*UCP)` refused BY NAME under both encodings, a D26-exact owner (not module 'verbs'); `(*UTF)` recognised under `-e utf8` (O-71). Optionally, a caller-visible note that `\w`/`\b` are ASCII under `-e utf8` | `(*UCP)` accepted. `\d`→Nd, `\s`→Xsp, and the small POSIX names lowered to existing `unicode-props` sets. `\w`, `\b`, `\B` and the letter-POSIX names refused by name *under UCP* ("requires [CLS-TREE]"-shaped). The byte-tier UCP (256-bit sets + Latin-1 fold) is cheap and could ride here | everything in §B, both encodings |
| **measured demand it serves** | the 5 bench twins get a clear refusal instead of a misleading one | bench: 46/91 sensitive patterns need only small sets; corpus 28/185. Of the 5 twins: `\d`, `\s`, the caseless control (3 of 5) | all: bench 91 sensitive (29 with `\b`); the ≥7 wild imports whose origin is Unicode (§A.3) |
| **cost** | registry row + spec hunk; no engine work | lowering + the `[:lower:]`/`[:upper:]` no-fold rule under caseless (§B.3) + the `(?a…)` knobs becoming real (they are PCRE2's own partial-UCP spelling) + D80 spec; sizes 3-19 KB DFA per use (§E) | (b) + the `\w`-sized sets (**unbuildable on the VM today**, 200-330 KB and slow compiles on the DFA) + a UCP `\b` on the DFA (the §D predicate view, or the rewrite's DFA→VM move for ~3/4 of `\b` patterns) |
| **depends on** | nothing | nothing for the small tier; `-e byte` UCP needs a Latin-1 fold in `src/core/fold.c` | **[CLS-TREE]** (hard: VM refusal), plus, for DFA-route `\b`, the insertion splice of §D (shared with [CLS-TREE]'s DFA seam) or acceptance of the VM move |
| **Frank's ideas used** | none | none. Idea 3 would not help here: without `\w` there is no `\b` | idea 3 as the DEFINITION and a stopgap route (VM); ideas 1-2 to keep `\b` patterns on the DFA; the same splice serves [CLS-TREE] on the DFA |

Two sequencing observations, not recommendations. First, (a) is a strict
prefix of (b), which is a strict prefix of (c). Second, the refusal wording
of (a) is needed in every option for whatever is not yet built.

### Open questions for the scheduled design

1. **Is UCP an axis or a verb?** `(*UCP)` in the pattern, a `-u`/`--ucp`
   CLI flag, an `.rxt` `flags u`, or UCP-by-default under `-e utf8`? The
   last is Frank's O-71 direction for `unicode-props`, applied here. It
   changes the answers of every existing `\w`/`\b` utf8 pattern, so it is
   a contract ruling (D80), not a lane's.
2. **The registry owner for `(*UCP)`/`(*UTF)`** (O-71, D26 exact tier).
   Which module? And does `(*UTF)` under `-e byte` refuse (encoding is
   per-compile, by `-e`) or override?
3. **Byte-tier UCP**: in (b), or later? It is cheap (§B.3) and distinct.
   Does anyone want Latin-1 `\w`?
4. **The `(?a…)` knobs**: they are accepted as no-ops today and become real
   under UCP. The design must implement them or start refusing them under
   UCP. Accepting and ignoring them would be a miscompile.
5. **Which island first**: [CLS-TREE]'s consuming class island or UCP's
   predicate island. Both need the §D splice, and the other one reuses it.
6. **H6/H7 bounds**: which lookaheads are bounded-width (a [PATFACTS] fact),
   and what variant count a real machine reaches. Both need a census that
   builds machines rather than reading text.
7. **Throughput**: rewrite-to-VM versus predicate view versus exact product,
   on the bench's `\b` loglines and capability cells, run on ubuntubudu.
   This is the measurement that would trigger building anything (D77).
8. **Imported-pattern drift** (§A.3): verify the ecosystem semantics claims.
   Should `-e utf8` warn when a pattern uses `\w`/`\b`/`\d` with no UCP
   decision? That is a diagnostic question, not a semantic one.
9. `[:graph:]`/`[:print:]` under UCP were not reduced to a formula here
   (PCRE2 special-cases them). The design must derive them from the oracle,
   not guess.

---

## G. Side findings (outside UCP; for the manager's triage)

1. **`(?r)` is silently ignored under `-e utf8`. This is an answer
   divergence.** `src/parse/mod_modifiers.c:405-406` treats `(?r)` as a
   "measured no-op at options=0", and pcre2_compliance.md:1032/1168 records
   that it "become[s] real under UTF/UCP: MOD-0.6/M5 own that day". M5
   shipped `-e utf8` with Unicode caseless folding and `(?r)` stayed a
   no-op. The 10.46 oracle, under **UTF alone**, disagrees with pcrec
   `-e utf8 --features all` on four cells:

   | pattern | subject | 10.46 | pcrec |
   |---|---|---|---|
   | `(?i)(?r)k` | U+212A | nomatch | match 0 3 |
   | `(?i)(?r)s` | U+017F | nomatch | match 0 2 |
   | `(?i)(?r)[a-z]` | U+212A | nomatch | match 0 3 |
   | `(?i)(?r)\x{212a}` | `k` | nomatch | match 0 1 |

   The non-ASCII pair `(?i)(?r)\x{e9}`/`É` still matches on both (correct).
   Transcripts: `probe_misc_10.46.txt`. This is a tier-1 miscompile class
   (D26 exact tier), `modifiers` module, `-e utf8` only.
2. **`RX_ENGINE_WHY` names one construct's kind at another's offset.**
   `x(?<=a)(?!b)` stamps `"(?!...) at pattern offset 1"`, and offset 1 is
   the `(?<=`. The \b spelling stamps `(?=...)` at the `(?<=`'s offset.
   `forces_registry` (`src/opt/select_engine.c:327`) takes the kind from
   `first_dfa_excluding(a)` and the offset from `cx->first_vmonly_pos`: two
   sources for one sentence. A lone lookbehind is labelled correctly.
3. **`\p{Xwd}+` compiles in 66 s** (and `\p{L}+` similarly; it held this
   lane's census for over a minute). `sample` puts 99% in `make_state`'s
   inlined closure inside `pcrec_build_dfa`. That is the K53/K55 family's
   compile-time face. [CLS-TREE] would remove it for these sets.
4. **The cls_tree_study baseline has moved**: `\p{Xwd}` on the DFA is
   197,685 object bytes at `13b7c202` against the study's 294,153 at
   `13b56a12` (the rodata shrank; `\p{Nd}`/`\p{Xps}` are unchanged). The
   study's 55× headline for Xwd is now ~37×. Any design citing the study
   should re-baseline.
5. **One census row carries no stamp**: `altwide/s-2048`'s stamps sit past
   the census's 20 KB header window, because its pattern comment is 24 KB.
   Its engine is unrecorded in both censuses. That is an instrument limit,
   stated rather than guessed.

---

## Reproduction, verification totals, disclosure

**Where everything is.** Every script and transcript is in
`studies/ucp_study/` (its `CLAUDE.md` lists them). The censuses are the only
heavy step: a compile-only pass, ~3 min each on 3 workers, run under the
boxlock.

**Verification totals.**
- Oracle set relations: 31 × 2 versions.
- `\b` equivalence: 579,195 subjects × 3 modes × 2 assertions × 2 versions,
  0 disagreements.
- pcrec drive: 12 streams × 579,195 subjects, all equal to libpcre2.
- Point probes: 46 rows × 2 versions, identical.
- Latin-1 probe: 2 versions, identical.

**Disclosure.** The session-root CLAUDE.md and the manager's memory index
were present at spawn. Beyond the brief, nothing in them shaped a
conclusion. The ecosystem-semantics column of §A.3 and the regex-automata
reference in §D.2 are general knowledge, marked as unverified, and no
conclusion rests on them. pcrec-bench was read (outbox O-71 via `git show
origin/master`; its pattern files) and never written.
