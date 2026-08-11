# pcrec — A PCRE-to-C Regex Compiler

## Approach Document (v1)

> **About the "req. N" citations** (DOC-1, 2026-08-11): the numbered
> requirements cited throughout ("req. 5", "req. 8", ...) are the founding
> project brief's list. That brief predates this repository and is not
> checked in, so the numbers are NOT resolvable references here — each
> citation's surrounding sentence is the requirement's only in-repo record.
> They are kept because they preserve the original numbering should the
> brief be added to docs/ later.

`pcrec` is an ahead-of-time compiler: it takes a PCRE pattern and emits specialized,
self-contained C source (gcc dialect) that matches exactly that pattern. The generated
matcher has no runtime interpreter, no dispatch tables to walk generically, and no
dependency on pcrec itself — gcc sees straight-line, branch-predictable code it can
optimize aggressively.

---

## 1. Architecture Overview

```
 pattern ──► [Parser] ──► AST ──► [Lowering] ──► IR ──► [Optimizer] ──► IR' ──► [Codegen] ──► .c file
                │                     │                     │                       │
          syntax modules        feature check         algorithmic passes      engine + encoding
          (drop-in)             (engine select)       (see §5)                backends (drop-in)
```

Five stages, each behind a narrow interface so components drop in without touching the core:

1. **Parse** — pattern text → AST. A small core parser plus registered *syntax modules*.
2. **Lower** — AST → IR. Also classifies the pattern: pure-regular constructs go to the
   automaton engine; irregular features (backreferences, lookaround) force the
   backtracking engine for the affected region.
3. **Optimize** — algorithmic transformations on the IR (the pass required by req. 5).
   This is where regex-domain knowledge lives; gcc can't discover these.
4. **Codegen** — IR → C source, parameterized by an *engine backend* (DFA / backtracking VM)
   and an *encoding backend* (ASCII / UTF-8).
5. **Runtime shim** — a small header-only support layer (input abstraction for
   string vs. stream) that is embedded into or `#include`d by the generated file.

### Division of optimization labor (reqs. 4 & 5)

- **pcrec does what gcc cannot**: automaton construction and minimization, literal
  extraction and prefiltering, anchoring analysis, class-set computation, alternation
  factoring. These change the *algorithm*.
- **gcc does the rest**: register allocation, branch layout, inlining, unrolling,
  autovectorization of scan loops. Generated code is written to be gcc-friendly:
  computed goto, `__builtin_expect`, `restrict`, flat local state, hot loops with
  simple exit conditions.

---

## 2. Two Engines, One IR

PCRE semantics are **leftmost-first with greedy/lazy quantifier preference** — not
POSIX leftmost-longest. That drives the engine design:

| Engine | Handles | Generated shape |
|---|---|---|
| **DFA engine** | Pure-regular patterns, "does it match / where does it end" | Computed-goto state machine, one label per DFA state; O(n), streaming-native |
| **Backtracking VM engine** | Captures, backreferences, lookaround, \G, recursion | Threaded-code backtracker (explicit stack, no C recursion), same semantics as PCRE |

Selection is automatic per pattern (overridable). The workhorse hybrid, used whenever
possible: **DFA as prefilter + backtracker for capture extraction** — the DFA scans the
long input fast and finds candidate match starts/ends; the backtracker runs only on the
small candidate window. This is how we honor req. 8 (optimize for long texts) without
giving up full PCRE semantics.

The IR is a single program form (an NFA-with-instructions graph, close to a Pike/PCRE2
"regex program"): nodes for `char`, `class`, `split`, `jump`, `save` (capture),
`assert` (anchors, \b, lookaround entry), `backref`, `repeat`. Both engines lower from
it; the DFA engine additionally runs subset construction + Hopcroft minimization on the
regular fragments.

**Determinization safety valve (req. 11):** subset construction is capped. On blowup,
the fragment will fall back to the VM engine once it exists (M4); until then pcrec
fails with a clean diagnostic. *Amended after checkpoint R1 (A-3):* the binding
constraint is not pcrec's own speed but **gcc's superlinear compile time on huge
computed-goto functions** (measured: 2048 states → 63 s at -O2; 8192 states → DNF).
The emitter therefore goes hybrid in M2 — computed goto for small DFAs, table-driven
(data arrays + one dispatch loop) for large ones — and the state cap is re-grounded
in a measured gcc-time budget enforced by a bench regression test.

### DFA islands inside the VM engine

When the VM engine is selected, its regular *fragments* are still compiled to DFA code
where semantics allow. A DFA reports the **set** of positions a fragment could end at;
the backtracker must try end positions in **preference order** (greedy: longest-first,
lazy: shortest-first) and retry on continuation failure — so islands come in three
strengths:

1. **Exact islands** — fragments the auto-possessification analysis proves atomic in
   context (e.g. `[^"]*` before `"`): DFA and backtracking semantics coincide, emit a
   plain DFA loop with a single answer. This targets the hot cases (`.*`, class
   repeats, alternation tries) where VM stepping is slowest.
2. **Accept-list islands** — *amended after checkpoint R1 (A-1):* valid ONLY for
   fragments whose backtracking end-position preference is provably monotone
   (longest-first for greedy, shortest-first for lazy — e.g. a single quantified
   class), because nested quantified fragments like `(?:aa|a)*` enumerate end
   positions in a non-position-sorted order that a sorted accept list would
   misrepresent. The island automaton is a separate NON-pruning DFA of the fragment
   (the D3 leftmost-first machine prunes exactly the threads an accept list needs,
   so it cannot be reused for this). One scan records the accepting positions; the
   VM consumes them in the monotone order. Non-monotone fragments take the VM path.
   Memory gated by max-match-length analysis.
3. **VM fallback** — fragments containing capture groups (islands split at capture
   boundaries; tagged automata are a later upgrade), or fragments too small to amortize
   island entry/exit overhead.

At the whole-pattern level, the same idea gives the prefilter hybrid described above:
an over-approximating DFA (backrefs → their referenced sub-pattern, lookarounds
dropped) that cannot false-negative finds candidate windows; the VM runs only inside
them. Precedent: RE2 and Rust regex's meta-engine use exactly this division.

---

## 3. Modular Construction (req. 3)

A **component** = parser hooks + IR lowering + (optional) codegen support + its test
slice. Components register into tables at compiler startup; the core never names them.

### Parser extension points

The core parser owns the grammar skeleton (sequencing, `|`, postfix quantifiers,
grouping) and exposes three hook tables:

- **escape table** — `\d \w \b \A \z \p{...} \k<name> ...` keyed by escape char
- **group-open table** — constructs starting `(?` : `(?: (?= (?! (?<= (?<! (?<name> (?P (?| (?# (?i) ...`
- **atom table** — special atoms: `[` class parsing, `.`, anchors

A drop-in module (e.g. `parse/lookaround.c`) registers its handlers and provides a
lowering function for the AST nodes it introduces. Unregistered constructs produce a
clean "feature not compiled in: (?=…) requires module 'lookaround'" error.

### Planned component ladder

| Tier | Components | Engine impact |
|---|---|---|
| **base** | literals, `.`, `[...]` classes, `|`, `* + ? {m,n}` (greedy/lazy), `^ $`, non-capturing groups | DFA-only |
| **captures** | `(...)`, `(?<name>...)`, `$1` refs in CLI replace | VM (or tagged-DFA later) |
| **classes+** | POSIX classes `[:alpha:]`, `\d \w \s` and negations, class union semantics | DFA |
| **assertions** | `\b \B \A \z \Z`, multiline `^ $` | DFA-with-context bit |
| **lookaround** | `(?= (?! (?<= (?<!` | VM |
| **backrefs** | `\1`, `\k<name>` | VM |
| **modifiers** | `(?i) (?m) (?s) (?x)`, inline and scoped | parse/lower only |
| **unicode-props** | `\p{L}` etc. (UTF-8 tier) | class-set expansion |
| **advanced** | conditionals `(?(1)...)`, atomic groups `(?>...)`, possessive quantifiers, recursion | VM |

Each tier is a milestone with its own tests; the compiler is useful after **base**.

---

## 4. Encodings (req. 6)

Codegen targets an abstract *cursor* interface: `PEEK`, `NEXT`, `AT_START`, `AT_END`,
class-membership tests. Encoding backends inline these:

- **ascii / byte** (`-e ascii`): 1 byte = 1 code unit. Class tests compile to 256-bit
  bitmaps (`uint64_t cls[4]`) or range compares — gcc turns small ones into arithmetic.
- **utf8** (`-e utf8`): the DFA operates **byte-wise** — Unicode classes/properties are
  compiled into the automaton as byte-sequence sub-automata (the RE2/Hyperscan
  approach: UTF-8 ranges → byte-range trees). No runtime decode step in the hot path,
  malformed input handled by automaton structure. The VM engine decodes code points at
  match time with an inlined decoder.

Adding UTF-16/32 later = new encoding backend, no core changes.

---

## 5. The Algorithmic Optimization Pass (req. 5)

Runs on the IR before codegen — the same playbook proven in PCRE2 (`pcre2_study`/JIT),
RE2, and Hyperscan:

**Scan-avoidance (biggest win on long texts, req. 8):**
- *Required-literal extraction*: a mandatory substring (prefix or interior "dominant
  literal") → generated code calls `memchr`/`memmem` to skip, then verifies. On typical
  long-text workloads this is the difference between "regex speed" and "memchr speed".
- *First-byte set*: the set of bytes any match can start with → `memchr` (1 byte) or a
  256-bit bitmap skip loop (gcc autovectorizes it).
- *Anchoring analysis*: `^`-anchored or `\A` patterns skip the scan loop entirely;
  `$`-only patterns scan from the end.
- *Min/max match length*: bail early near end of input; bound the backtracker's window.

**Automaton-level:**
- ε-elimination, dead/unreachable state removal
- Subset construction + **Hopcroft minimization** for DFA fragments
- *Alternation factoring*: `foo|for|fob` → trie → shared prefix states (also shrinks code)
- *Bounded-repeat handling*: small `{m,n}` unrolled into the automaton; large counts
  become counter loops instead of state blowup

**VM-level:**
- Atomic-group/possessive inference where backtracking provably can't help
  (auto-possessification, as in PCRE2) — prunes exponential blowups
- Peephole: merge adjacent literal chars into `memcmp`-able runs

Each pass is independent and toggleable (`--fno-<pass>`) — useful for testing and for
compile-speed tuning (req. 11).

---

## 6. Generated Code & Runtime Interface (reqs. 8, 9, 10)

One pattern → one `.c` file (+ matching `.h`), prefix-namespaced, zero dependencies
beyond libc (and libc is optional: `memchr`/`memcmp` fallbacks for freestanding
embedded builds, req. 10).

```c
/* generated API, --prefix myrx */
typedef struct { size_t start, end; } myrx_span;
typedef struct { /* fixed-size: capture spans, engine state */ } myrx_match;

/* string source: one shot over a buffer */
int myrx_search(const uint8_t *s, size_t n, size_t startpos, myrx_match *m);

/* stream source: incremental, constant memory for the DFA engine */
typedef struct { /* current DFA state, counters, partial-match window */ } myrx_stream;
void myrx_stream_init(myrx_stream *st);
int  myrx_stream_feed(myrx_stream *st, const uint8_t *chunk, size_t n, myrx_match *m);
int  myrx_stream_end (myrx_stream *st, myrx_match *m);   /* flush: $ / \z resolution */
```

- **String + long text**: the search loop is `skip-scan (memchr/bitmap) → attempt →
  advance`, structured so the skip scan is the hot path.
- **Stream**: natural for the DFA engine (state is an int + counters across chunks).
  *Amended after checkpoint R1 (A-4, A-5):* the streaming matcher is emitted as an
  **integer-state dispatch loop**, not the string-search computed-goto shape — gcc
  label addresses are invalid once their function returns, so `&&label` state cannot
  survive across `feed()` calls; and the streaming automaton is the single
  "search-from-anywhere" self-loop machine (M2 adopts the same shape for string
  search, which also removes the per-start-restart O(n²)). For VM-engine patterns the
  bounded look-behind window has two explicitly distinct outcomes: `PARTIAL`
  (pcre2-style: match may complete when more data arrives — window still holds the
  candidate) and `WINDOW_EXCEEDED` (history a match would need was discarded off the
  back — reported as such, never silently degraded to nomatch). Patterns with
  bounded max match length never see `WINDOW_EXCEEDED`; unbounded ones document it.
- **GNU C usage**: computed goto (`&&state_label`) for the DFA, `__builtin_expect` on
  match/fail edges, `static inline` runtime shims. `--std-c` fallback flag emits a
  `switch`-based machine for non-gcc compilers (slower, but keeps the library portable).

### Deliverables (req. 10)

- **`libpcrec`** — the compiler as an embeddable C library:
  `pcrec_compile(pattern, opts) → C source in a memory buffer`. Static-linkable, arena
  allocator, no globals (usable in build systems, code generators, IDEs).
- **`pcrec` CLI** — `pcrec -e utf8 --prefix myrx -o myrx.c 'pattern'`, plus
  `--emit-main` to produce a standalone grep-like binary for smoke testing, and
  `--emit-ir` / `--emit-dot` for debugging the IR and automata.

---

## 7. Testing (req. 7)

Tests are organized **by component**, and the corpus comes from **PCRE2's testdata**
(`testinput1`/`testoutput1` are the dialect-conformance files — BSD-licensed, importable).

1. **Harness**: a `pcre2test`-subset runner. It reads pattern/subject/expected-match
   blocks, invokes pcrec, compiles the emitted C with gcc into a shared object, loads
   it, runs subjects, diffs results against expected output. One process caches gcc
   invocations batch-wise so the suite stays fast.
2. **Corpus slicing**: a classifier tags each PCRE2 test with the components it needs;
   each component directory (`tests/base/`, `tests/lookaround/`, …) owns its slice.
   Tests for not-yet-built components are *expected-unsupported* (must fail with the
   clean "module required" error, not miscompile) — the suite is green at every tier.
3. **Differential fuzzing** (later): random patterns + subjects, pcrec vs. libpcre2
   result comparison — the strongest correctness signal for a regex engine.
4. **Compile-speed + codegen-size benchmarks** as tests (req. 11): pattern corpus must
   compile under time/size budgets; regressions fail CI.

---

## 8. Repository Layout

```
pcrec/
├── APPROACH.md              # this document
├── Makefile                 # plain make + gcc; no build-system dependency
├── src/
│   ├── core/                # driver, options, arena, diagnostics, AST defs
│   ├── parse/               # parse.c (skeleton) + one file per syntax module
│   ├── ir/                  # IR defs, lowering, nfa/dfa construction
│   ├── opt/                 # one file per optimization pass
│   ├── gen/
│   │   ├── engine_dfa.c     # computed-goto DFA emitter
│   │   ├── engine_vm.c      # backtracking VM emitter
│   │   ├── enc_ascii.c      # encoding backends
│   │   └── enc_utf8.c
│   └── rt/                  # header-only runtime shims embedded in output
├── lib/                     # public API for libpcrec (pcrec.h)
├── cli/                     # main.c for the pcrec tool
├── tests/
│   ├── harness/             # pcre2test-subset runner
│   ├── base/  classes/  assertions/  captures/  lookaround/  backrefs/ ...
│   └── bench/               # long-text throughput + compile-speed budgets
└── third_party/pcre2-testdata/   # imported test corpus (license preserved)
```

---

## 9. Build Order / Milestones

| # | Milestone | Contents | Exit criterion |
|---|---|---|---|
| 0 | Scaffold | Makefile, arena, diagnostics, CLI skeleton, test harness running a trivial hand-written matcher | harness green on 1 dummy test |
| 1 | **base** end-to-end | base-tier parser → IR → DFA engine → ASCII codegen, string source | base slice of PCRE2 tests green |
| 2 | Optimizer + long text | §5 scan-avoidance + minimization passes, throughput bench | ≥ memchr-class speed on literal-bearing patterns |
| 3 | Streaming | `*_stream_*` API for DFA engine | stream results ≡ string results on chunked corpus |
| 4 | Captures + VM engine | backtracking emitter, DFA-prefilter hybrid | captures slice green |
| 5 | UTF-8 | byte-wise UTF-8 automata, `\p{...}` module | UTF-8 slices green |
| 6 | PCRE drop-ins | lookaround, backrefs, modifiers, atomic groups… one module at a time | per-module slices green |
| 7 | Hardening | differential fuzzing vs libpcre2, embedded (freestanding) build profile | fuzzer-quiet |

Each milestone leaves a working, tested compiler — the modular ladder is also the
delivery schedule.

---

## 10. Key Design Decisions (and their reasoning)

1. **Semantics = PCRE leftmost-first**, verified against PCRE2's own tests — not POSIX.
   This forces the two-engine design; a pure-DFA tool couldn't claim PCRE compatibility.
2. **DFA-prefilter + VM-verify hybrid** as the default for capture patterns — the only
   way to be both PCRE-correct and fast on long texts.
3. **Byte-wise UTF-8 automata** (no hot-path decoding) — proven by RE2/Hyperscan,
   and it makes ASCII and UTF-8 share one DFA emitter.
4. **Generated code is standalone** — embeds its runtime shims; embedded users vendor
   one `.c`/`.h` pair with no license/dependency drag.
5. **Compile-speed guardrails are structural**, not aspirational: capped subset
   construction with VM fallback, arena allocation, single-pass parser, per-pass
   opt-out flags, code-size caps so gcc's own compile time stays bounded.
