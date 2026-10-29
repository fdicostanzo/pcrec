# [DATA-PLAN] — large data is paid only where used and shared where repeated

**Status: PROPOSED** (lane `datad`, opus, 2026-10-24, on main `74ecca07a`,
abi 84). Design only: nothing under `src/`, `tests/`, `docs/spec/`. Plan row
`docs/dev/plan.md` [DATA-PLAN]; asked by Frank 2026-10-24 ("Ship them but we
need a way to only load when needed. A general data plan for extra stuff"),
widened by ruling R1 (`docs/dev/lanes/datad_rulings.md`): **two problems, both
need solutions** — (A) pcrec's own size, (B) sharing Unicode data across
generated artifacts.

Every number below was measured on the Linux dev box (Ryzen 7 7700X, gcc 15.2
`-O2 -c`, GNU binutils `size -A`) with main's `build/pcrec` at `74ecca07a`,
unless tagged ESTIMATE or cited from a named file. Recipe: Appendix A; instruments in `data_plan/`.

---

## 0. The headline (the brief's STOP RULE fires, in part)

**The 185 KB of a `\p{L}` matcher is not Unicode property data. It is the
byte-level DFA that encodes the class, so it is specific to the pattern and
cannot be shared.** Its object is 3.9 KB of code and 180 KB of `.rodata`, and
that `.rodata` is two transition tables (`next_state[29900]`, 299 states × 100
byte classes, forward and anchored) plus two accept arrays of the same length.
No property table is in it. The same class on the VM route is a 4.5 KB
three-level lookup table (the [CLS-TREE] kit predicate) plus 3.8 KB of code:
8.5 KB in all, 22x smaller.

So the note is shaped this way:

- **(B) is mostly a FORM problem, not a sharing problem.** The big lever is
  which form a wide class takes: the byte automaton (180-260 KB per class per
  matcher) or decode-plus-predicate (4-6 KB). Sharing across matchers comes
  second. It saves the 4-12 KB general tables that DO repeat today (the kit
  predicate, the caseless back-reference fold table), and it matters once the
  record, fold and grapheme tables arrive.
- **(A) is a FORMAT problem, as Frank suspected (ruling R2).** The property
  data is stored as 8-byte `{lo, hi}` pairs: ~160 KB of UCD-derived data in a
  1.42 MB compiler today (11%), and **208 KB of pairs alone after
  [UPROP-MORE]** (measured on `upropb`'s generated table: 26,015 intervals
  over 747 sets; its WIP build's `mod_uprops.o` is 255 KB, up from 110 KB).
  The same intervals as delta-varints take **57.6 KB** (3.6x, no decompressor
  needed, the whole pool decodes in 39 µs). zlib on top gives 22.9 KB (9x) but
  needs an inflater in pcrec. One property is 0.02-1.7 KB in any compact form,
  so Frank's "a few k at worst" holds per property. All 747 together are what
  reach 58 KB.

Correction to the D178 and plan-row figure: "110 KB of a 5.9 MB build/pcrec"
compares an object's loadable bytes with a file that is mostly debug
information. The binary's loadable size is 1.42 MB (`.text` 702 KB, `.rodata`
541 KB, `.data.rel.ro` 173 KB), plus 141 KB of dynamic relocations
(`.rela.dyn`, PIE); the stripped file is 1.67 MB.

---

## 1. Inventory, measured

### 1.1 Problem A: data inside pcrec (the compiler and `libpcrec.a`)

Generated tables (`make gen-tables`, from `third_party/*/generate.py`) and
their size in the linked binary (`nm -S build/pcrec`):

| table (source `.inc`) | host object | symbol(s) | bytes |
|---|---|---|---:|
| `src/parse/uprops_tables.inc` (232 KB of C) | `mod_uprops.o` (110 KB) | `pcrec_uprop_iv` (10,961 intervals × 8 B) | 87,688 |
| ditto | ditto | `pcrec_uprop_names` (312 sets) | 17,208 |
| `src/core/fold_tables.inc` | `fold.o` (25 KB) | `pcrec_ucd_fold_links` + simple fold | 23,504+ |
| `src/enc/utf8_fold_pairs.inc` | `enc_utf8.o` (40 KB) | `u8_defs_bref_ci` (the caseless back-reference helper's C TEXT, fold pairs inside) | 27,152 |
| `src/parse/cls_bits.inc` | `mod_classes.o` | POSIX/class bits | <7 K |
| `src/core/case_tables.inc` (used on `lane/substland` only) | the subst support unit's text | upper/lower maps (1,466 + 1,416 entries) | ~23 K (as emitted) |
| `findings_store.inc`, `measures_store.inc` | `findings.o`, `measures.o` | not Unicode; measurement and findings stores | ~35 K |

**UCD-derived total: ~160 KB of 1.42 MB loadable (~11%).** The rest of the
binary is emitter code (`emit_dfa.o` 198 KB, `emit_vm.o` 150 KB) and the
emitted-text string literals in `.rodata`. For comparison, the system's
`libpcre2-8.so` 10.46 carries ALL of its Unicode data (every property it
accepts, including the binary properties and Bidi_Class [UPROP-MORE] is
adding) inside 158 KB of `.rodata`, as a two-stage per-code-point record
table.

**Growth.** [UPROP-MORE] is MEASURED (lane `upropb`'s WIP, `d2e112042`; its
generated `uprops_tables.inc` and its build of 2026-10-24 11:52). The rest are
ESTIMATES:

| arrival | adds | source |
|---|---:|---|
| [UPROP-MORE] (a)+(b): binary properties, Bidi_Class, Block, Age: 26,015 intervals, 747 sets, 1,384 name rows | **+145 KB** to `mod_uprops.o` (110 → 255 KB); binary `.rodata` +128 KB, `.data.rel.ro` +16 KB, `.rela.dyn` +16 KB | measured |
| [GRAPHEME]: Grapheme_Cluster_Break + Extended_Pictographic + InCB | +10-20 KB | ESTIMATE |
| [SEQ-FOLD]: full case fold (104 F entries), canonical/compatibility decompositions (~5.7 k mappings), combining classes | +50-90 KB | ESTIMATE |
| [CLASS-SETOPS] | 0 (interval algebra on existing sets) | — |
| **UCD data, in today's format** | **~370-420 KB, ~21-23% of a ~1.8 MB compiler** | |

RAM is not the issue. `.rodata` is demand-paged, so a compile touches only
the pages its pattern's properties live on. The cost of A is the size of
the file on disk and in a download, and of `libpcrec.a` inside a program that
links the compiler.

### 1.2 Problem A: the storage FORMAT, measured (ruling R2)

The whole interval pool, encoded several ways (`data_plan/formats.py`, Appendix A).
"Today" is main's table; "after" is `upropb`'s.

| format | today (10,961 iv, 312 sets) | after [UPROP-MORE] (26,015 iv, 747 sets) | needs at use |
|---|---:|---:|---|
| `{lo, hi}` u32 pairs (shipped) | 87,688 | 208,120 | nothing |
| **delta-varint** (lo - previous hi, hi - lo) | **24,323** (3.6x) | **57,583** (3.6x) | a ~15-line decoder |
| zlib -9 of the pairs | 20,316 | 49,051 | an inflater |
| zlib -9 of the varints | 10,674 (8.2x) | 22,887 (9.1x) | an inflater + the decoder |
| xz -9 of the varints | 10,136 | 20,044 (10.4x) | an LZMA decoder |
| a compressed BITMAP per property (0x110000 bits, zlib -9) | 71,644 | 167,619 (1.24x) | an inflater, 139 KB of scratch per property |
| one shared two-stage table, code point → membership record over every set (block 128) | 122,231 | 331,734 | nothing (direct lookup) |

Per property, after [UPROP-MORE] (bytes):

| property | intervals | pairs | varint | zlib bitmap |
|---|---:|---:|---:|---:|
| `L` | 677 | 5,416 | 1,426 | 1,445 |
| `Lu` | 651 | 5,208 | 1,325 | 492 |
| `XID_Continue` | 800 | 6,400 | 1,679 | 1,556 |
| `Alphabetic` | 757 | 6,056 | 1,585 | 1,510 |
| `Emoji` | 150 | 1,200 | 319 | 435 |
| `Greek` | 36 | 288 | 82 | 253 |
| `White_Space` | 10 | 80 | 23 | 191 |

**Decode cost** (`data_plan/dec.c`, gcc -O2, this box, while a `make test` ran, so
read it as an order of magnitude). Decoding the WHOLE varint pool takes
22 µs today and 39 µs after. One property is ~1 µs. zlib-inflating the whole
varint blob takes 39/76 µs, before the varint decode. A trivial
`pcrec -e utf8` compile takes under 10 ms wall, so the decode is under 1% of
the smallest compile.

What the format table says:

1. **Varint is the knee.** 3.6x with no new dependency and a decoder small
   enough to review in one sitting. Compression buys 2.5x more on top and
   costs an inflater. pcrec has no dependencies (APPROACH.md), so that means
   either writing one (a few hundred lines) or vendoring zlib.
2. **Frank's compressed bitmaps are good PER PROPERTY for dense sets** (`Lu`
   492 B against 1,325 B varint), but they are the worst format in TOTAL
   (167 KB). Each small property pays zlib's fixed cost and the empty
   stretches. They also need a 139 KB scratch bitmap at decode.
3. **A naive shared two-stage table is bigger, not smaller** (332 KB). It
   records each code point's membership in all 747 sets, and those sets
   overlap heavily. PCRE2's 158 KB holds everything because its record
   FACTORS: general category, script and Bidi_Class are small enums, and the
   binary properties are an index into a shared list of bitsets. That is a
   different generator, worth it only if the record also serves the
   artifacts ([UCD-RECORD], §3.2 A-c).
4. **The name table has a format cost too.** `pcrec_uprop_names` holds a
   `const char *` per row. In a PIE that is 8 B of pointer plus a 24 B
   `R_X86_64_RELATIVE` relocation per row, ~32 B of overhead for each of
   1,384 rows (~44 KB after [UPROP-MORE], against ~13 KB of actual name
   bytes). The usual fix is one string blob with u16/u32 offsets: no
   relocations, the table goes to `.rodata`, and it is ~3x smaller.

### 1.3 Problem B: data inside generated matchers

The artifact side, split into CODE (`.text`) and TABLES (`.rodata`), with
`-e utf8` unless noted. `load` = text + rodata + data.

| pattern | engine | C bytes | code | tables | **load** |
|---|---|---:|---:|---:|---:|
| `hello` | dfa | 19,343 | 3,131 | 775 | **4,130** |
| `[a-z]+` | dfa | 19,446 | 2,971 | 902 | 4,097 |
| `\d+` (ASCII; `--ucp` `\d+` below) | dfa | 19,436 | 2,971 | 899 | 4,094 |
| `\p{Greek}` | dfa | 47,403 | 3,899 | 10,152 | **14,275** |
| `\p{Han}` | dfa | 74,705 | 3,899 | 19,073 | 23,196 |
| `\p{Lu}` | dfa | 137,629 | 3,899 | 39,999 | 44,122 |
| `\p{N}` | dfa | 147,603 | 3,899 | 43,834 | 47,957 |
| `\p{L}` | dfa | 586,042 | 3,899 | 180,269 | **184,392** |
| `\P{L}` | dfa | 568,497 | 3,899 | 179,688 | 183,811 |
| `\p{L}+` | dfa | 891,903 | 3,899 | 269,362 | 273,485 |
| `a\p{L}b` | dfa | 758,509 | 3,387 | 232,284 | 235,895 |
| `[\p{L}\p{N}]+` | dfa | 624,739 | 3,899 | 234,459 | 238,582 |
| `\p{Xwd}+` | dfa | 679,178 | 3,899 | 255,934 | 260,057 |
| `(\p{L})-(\p{L})-(\p{N})` | vm (hybrid: DFA prefilter fwd + rev) | 866,431 | 21,659 | 363,097 | 384,980 |
| same, `--no-captures` | dfa | 835,941 | 4,091 | 357,367 | 361,682 |
| `--ucp \d+` | dfa | 66,313 | 3,899 | 15,697 | 19,820 |
| `--ucp \s+` | dfa | 23,577 | 3,899 | 2,321 | 6,444 |
| `--ucp \w+` | — | REFUSED: "UCP \w is a wide set (930 intervals) and is refused under encoding 'utf8' until a kit-sized class route exists" | | | |
| **VM route (`--engine=vm`)** | | | | | |
| `\p{L}` | vm | 33,769 | 3,771 | **4,499** | **8,494** |
| `\p{L}+` | vm | 35,749 | 5,563 | 4,484 | 10,271 |
| `[\p{L}\p{N}]+` | vm | 36,795 | 5,563 | 4,875 | 10,662 |
| `\p{Xwd}+` | vm | 40,939 | 5,563 | 5,790 | 11,577 |
| **the size dial (`--tune`)** | | | | | |
| `\p{L}` `--tune=min-size` | dfa | 256,855 | 3,899 | 121,068 | 125,191 |
| `\p{L}+` `--tune=min-size` | dfa | 381,886 | 3,899 | 180,758 | 184,881 |
| **caseless (`-i`)** | | | | | |
| `straße` | dfa | 25,402 | 5,243 | 2,271 | 7,738 |
| `σοφία` | dfa | 22,423 | 2,779 | 1,988 | 4,991 |
| `\p{Lu}` | dfa | 133,704 | 3,899 | 39,418 | 43,541 |
| `\p{Ll}+` | dfa | 194,648 | 3,899 | 58,147 | 62,270 |
| `(\w+) \1` (`--features all`) | vm | 53,318 | 9,435 | 12,227 | 21,886 |
| **subst support unit** (`lane/substland`'s `--emit-support`, one per program) | — | 85,939 | ~4.6 K | 23,056 (case maps) | 27,712 |

What the table says:

1. **The tables are the byte automaton, and code is flat.** Code is
   3-6 KB in every DFA row. The tables grow with the class's UTF-8 automaton
   (299 states for `\p{L}`, which [CLS-TREE] §3.1 proved minimal). A
   pattern-specific automaton cannot be shared: `\p{L}`, `\p{L}+` and
   `a\p{L}b` each have their own.
2. **Caseless costs nothing extra.** The fold happens when the set is built
   (CT-7). A caseless class costs what its folded set costs.
3. **The small form exists and the dial does not reach it.** `--tune=min-size`
   gets `\p{L}` to 125 KB by dropping the anchored twin. It never chooses the
   VM's 8.5 KB form.
4. **Wide classes are a capability gap, not only a size cost.** UCP `\w`
   under utf8 is refused because its byte automaton is too big to build
   (`mod_ucp.c`'s route table: "330 KB, 66 s" compile).
5. **General tables that already repeat across matchers.** Each one is
   identical in every artifact that carries it:
   - the caseless UTF-8 back-reference fold table `rx_span_ci_fold_pairs`:
     **11,872 B**, byte-identical between two different patterns (checked
     with `cmp`);
   - a kit predicate for a given set: 4.5 KB for `\p{L}`, 5.8 KB for
     `\p{Xwd}` (the same set, same form, same bytes);
   - the subst case maps: 23 KB, ALREADY shared through the support unit.
6. **Side finding (a size lever inside the DFA form):** the premultiplied
   table's accept arrays are indexed by cell, not by state.
   `rx_forward_is_accepting[29900]` holds 100 ones and 29,800 zeros. The two
   accept arrays are 59.8 KB of `\p{L}`'s 180 KB (33%). This is deliberate
   (`premultiplied_dfa_table.md`: the probe reads the new premultiplied state
   with no divide). A per-state form would need a renumbering (accepting
   states contiguous, so that accepting means `state >= A`), and that would
   meet the top-of-range stop test and the dead row. Recorded as an idea with
   its own trigger (§4), not proposed.
7. **DFA tables do not compress well in place.** In `\p{L}`'s forward table
   all 299 rows are distinct, there are 95 distinct columns of 100, and 14,616
   of 29,900 cells differ from their row's most common value. Comb or
   row-displacement compression would give at most ~2x, and it adds a check
   to the hot loop.

**Data vs code, in Frank's terms (R2).** On the default (DFA) route a big
class's cost is ~100% CODE in Frank's sense: the class spelled out as UTF-8
byte branches. Those branches happen to be stored as a transition table
rather than as `if`s, but no property data is present, so there is nothing
to compact or share. The DATA part appears only on the decode-plus-predicate
route (the VM today, the island later): the 4.5 KB kit predicate for `\p{L}`.
Frank's format idea applies there, with one constraint the compiler side
does not have. A matcher must answer "is this code point in the set?" on
every character, so the form must be probed in place. A varint list (1.4 KB)
or a compressed bitmap (1.4 KB) cannot be probed in place. Decoding it on
first use into a buffer is a mutable static with a thread-safety question
and a first-call cost, which B1 rules out (§3.1 B-c). The probe-able compact
forms are what the [CLS-TREE] kit's DP already chooses between: page
tables, bitmaps, a binary search over the pairs (5.4 KB), ranges. So for
matchers, the format lever is ~1x over today's kit. The large lever is
leaving the byte-branch form (22x).

---

## 2. Goals (ranked, checkable)

### 2.1 Problem B — generated matchers

| # | goal | who benefits | measurable form |
|---|---|---|---|
| **B1** | A matcher stays self-contained: no runtime library, no data file at match time, and it compiles and links ALONE | every user (the AOT promise, APPROACH.md) | an artifact `.c` compiles and links with nothing else; any sharing is a link-time saving only, never a requirement |
| **B2** | The default setting does not get slower | speed users (positioning: fastest complete pcre) | utf8-bench cells at default tune within the A/A floor of today |
| **B3** | A wide Unicode class costs about its predicate, not its byte automaton, at a size-leaning setting | size-conscious users; and UCP `\w` becomes buildable | `\p{L}` matcher ≤ 16 KB loadable at `--tune=size` (today 184 KB); the speed cost there measured, stamped, and ≤ 1.5x on the utf8 bench's regimes (the island twin's measured envelope) |
| **B4** | N matchers in one program that use the same general table pay for it once | programs with many patterns ([ART-MGR]) | linking N artifacts that share a table: total ≤ one table + N × (the rest), checked with `size` on the linked program |

**Priority:** B1 > B2 > B3 > B4. B1 is the product's contract. B2 beats B3
because the default is what the bench measures and what users get. B3 beats
B4 because the form choice is worth 22x per matcher and sharing ~1x per
extra matcher.

**Non-goals:** compressing DFA tables (§1.3 point 7); loading data at
match time from a file or the network; sharing pattern-specific automata
between patterns; a smaller C source as a goal in itself (compile time is
measured, but the target is the object).

### 2.2 Problem A — pcrec itself

| # | goal | who benefits | measurable form |
|---|---|---|---|
| **A1** | pcrec stays one self-contained binary, and `libpcrec.a` one archive: nothing to install beside it, and nothing to find at run time | every user of the CLI and the library | `build/pcrec` runs when copied alone to another machine |
| **A2** | UCD-derived data stays a minor share of pcrec as Unicode features land | distributors, library embedders | UCD data ≤ 15% of the compiler's loadable size (today 11%; ~20% once [UPROP-MORE] lands in today's format), re-measured at each Unicode feature's landing |
| **A3** | Compile time does not regress from the data's encoding | every compile | per-pattern compile time of the `tests/utf8` `\p` corpus within noise |
| **A4** | One source of truth: the vendored UCD files through `generate.py` | maintainers | unchanged: `make gen-tables` + the staleness check |

**Priority:** A1 > A4 > A3 > A2. **Non-goal:** RAM use (demand paging
already gives "load only what is touched").

---

## 3. Options

### 3.1 Problem B

**(B-a) A shared data part, linked once per program.** A general table
(a predicate for a set, the fold pairs, the case maps, later the record and
the fold and grapheme tables) is emitted under a CONTENT-ID name:
`pcrec_d_<hash>`, where the hash covers a table-format tag and the bytes.
There are three ways to link it, and they are ROWS of one linkage table (UCP
design's T7, generalized from "a `\p`/UCP set or the record" to every general
data part):

| # | row | applies | action | measured |
|---|---|---|---|---|
| 1 | `comdat` | ELF + gcc/GNU as; the table ≥ a pinned floor; the content is general (not pattern-specific) | `__attribute__((section(".rodata.pcrec_d_<h>,\"aG\",@progbits,pcrec_d_<h>,comdat#")))`, hidden visibility. The linker keeps one copy, and each artifact still carries its own definition (B1 holds) | **3 TUs × 8 KB table: plain link 26,061 B → 9,677 B with comdat, no link flags needed.** `weak` alone: no dedup (26,061 B) unless the user adds `-fdata-sections -Wl,--gc-sections` (9,645 B) |
| 2 | `support-unit` | the caller asked for an explicit shared file (`--emit-support`'s precedent, `subst_api.md` §10) | `extern` reference; the definition is in the unit, with the content id checked at setup (§10¶3) | the subst unit: 27.7 KB once per program, 23 KB of it case maps |
| 3 | `static` | always | `static const` in the artifact (today) | — |

- *Cost:* emitted scaffolding moves (an abi event, D76/D94). There are
  naming rules (format tag + abi in the hash, so two pcrec builds fold only
  identical bytes). Hidden visibility, because a default-visibility global
  read from `-fPIC` code goes through the GOT, an extra load on the hot path,
  where `static` gets direct addressing. Darwin needs its own spelling
  (ld64's weak-definition coalescing; NOT VERIFIED here, a Mac probe is owed
  before the row admits Darwin). The row's predicate names the toolchain
  facts it relies on, and any other toolchain falls to `static`.
- *Speed:* none at the matcher (same bytes, same addressing with hidden
  visibility). It may be positive in a program running several matchers
  (one copy in cache).
- *Unlocks:* B4 for every general table without a support unit, and [UCD-RECORD]
  becomes affordable: one ~100+ KB record linked once instead of per
  matcher. It is the shape [XART-TABLES] asked for, and that row's trigger ("the
  first LARGE GENERAL table ships in emitted artifacts") has arguably
  already fired: the 11.9 KB fold-pairs table.
- *What it saves today:* little. 11.9 KB per extra caseless-utf8-backref
  matcher, 4-6 KB per extra matcher repeating a wide class on the VM route.
  It cannot touch the 180 KB.

**(B-b) The compact class form, chosen by a declared size/speed row.** A
wide class takes decode + kit predicate instead of its byte automaton. Two
routes exist or are designed:

- *the VM route*: built ([CLS-TREE] S4). `\p{L}` 8.5 KB, `\p{Xwd}+` 11.6 KB.
  Its per-character speed against the DFA is **not measured** (the CLS-TREE
  note §2.3 says so, and no S4 report times it). The engine changes too, so
  the speed difference is the VM's, not only the class test's.
- *the DFA island*: designed (UCP design UD-3, T4's `bytes-under-theta` row,
  θ as a `--tune` cell), chartered as U3 on capability grounds, not built.
  Hand-twin timing (`ucp_measurements/u3_island_twin.md` §3, ubuntubudu):
  for `\p{L}`, 1.04-1.49x slower than the all-byte DFA across ascii/latin1/cjk/mixed,
  and 0.83x (faster) on `\p{Xwd}`/cjk. Its size was not measured. ESTIMATE:
  the predicate (~4.5 KB) plus a few ASCII-width rows, about 5-8 KB.

The decision is already a table in the UCP design (T4 picks the machine form
with θ; T6 picks the vector producer). [DATA-PLAN] adds no new table here. It
adds a GOAL that sets θ per tune position: at `size`/`min-size`, θ admits
no wide class to the byte form; at `balanced` and above, θ keeps today's
artifacts (B2).

- *Cost:* the VM route needs no new mechanism. It needs a row in engine
  selection that routes a wide class to the VM at the size-leaning
  positions. The island is U3's build (its design exists).
- *Speed:* measured for the island (above), unmeasured for the VM route.
  This is the measurement that decides (§5 stage 1).
- *Unlocks:* B3; UCP `\w`/`[:alpha:]` under utf8 at a size-leaning setting
  first, and at default once the island lands; captured wide classes (CT-8,
  already on the VM); then sharing (B-a) has tables worth sharing.

**(B-c) Compression.** Rejected for DFA tables (§1.3 point 7). For general
tables, a compressed copy needs a decompressor in the artifact, writable
memory and a first-use initialization (thread-safety, a startup cost on every
matcher). That breaks the `const`-table property, and with it B1's spirit.
The kit's DP already chooses compact forms such as page tables and bitmaps
(CT-1). **Not recommended.**

**(B-d) Shrinking the DFA form itself.** Two levers inside the byte
automaton: the anchored twin (already dropped by the K53 ladder when large;
`--tune=min-size` drops it: 184 → 125 KB), and the per-cell accept arrays
(33% of `\p{L}`). Both are bounded at about 1.5-2x and both are speed-shaped
questions owned by existing rows ([OPT-3], [OPT-D]). **Filed as ideas; not
the plan.**

**(B-e) Sibling-of-a-family lens.** There are three members, and they are
one question: *at what scope is a reused piece shared?*
- within an artifact, CODE: `--part-layout` (`tuning.md` §2.51: `shared` /
  `inline` per part, a declared table);
- across artifacts, CODE + DATA, explicit: the subst support unit (content id,
  `subst_api.md` §10);
- across artifacts, DATA, implicit: [XART-TABLES] / UCP T7 (filed).

[COMPOUND] is NOT a member: its sub-artifacts are private to their
controller and pattern-specific. **The general form proposed:** a *data part*
has a content id, and ONE linkage table (rows `comdat`, `support-unit`,
`static`) decides its scope, the way the part-layout table decides a code
part's. The support unit becomes the explicit row of that table rather than
a parallel mechanism. Its case maps would be data parts it carries, and the
unit's own content id stays as today. This is three members, the point
where the house rule says to propose the unification
(architecture.md, "Notice siblings"). Building it waits for B-a's trigger.

### 3.2 Problem A

| option | what | size effect | cost | verdict |
|---|---|---|---|---|
| **A-a** embed as today | `{lo, hi}` pairs, pointer name table, fold links | 160 KB today, ~305 KB after [UPROP-MORE], ~370-420 KB with [GRAPHEME]/[SEQ-FOLD] | none now | the baseline |
| **A-b** delta-varint interval lists + a string-blob name table | the generator writes varints and one name blob with offsets; `mod_uprops` decodes the one property a pattern names | **measured: pool 208 → 58 KB after [UPROP-MORE]** (3.6x); the names lose ~32 B/row of pointer + relocation (~44 KB → ~15 KB, ESTIMATE); together ~305 → ~90 KB | generator + a ~15-line decoder; ~1 µs per property per compile (§1.2); no dependency; a decoder bug is caught by the `uprops` differential against `oracle_store/libpcre2-10.46` (independent of the generator) | **recommended** |
| **A-b+z** A-b, then zlib/xz over the blob, inflated on first use | | 58 → 20-23 KB (9-10x over pairs) | an inflater in pcrec, written or vendored (pcrec has no dependencies today), plus a heap copy and a first-use step. Buys ~35 KB more than A-b | **not now**; trigger: a size budget that A-b misses |
| **A-c** a per-code-point record table (PCRE2's shape) from which every set is derived | one factored two-stage table | PCRE2 holds everything in 158 KB; a NAIVE shared table measured 332 KB (§1.2 point 3); only a factored record approaches PCRE2 | a different generator and set derivation (a remodel of `mod_uprops`) | only if [UCD-RECORD] is built for artifacts anyway (one table, two readers) |
| **A-d** read the tables at compile time from a data file shipped beside pcrec | file next to the binary, or a path compiled in | the whole UCD share leaves the binary | breaks A1 (install layout, finding the file, a library user ships it too); version skew between file and binary must be refused by a content id or it miscompiles silently; the identity gates must pin the file; startup I/O per compile. And after A-b it saves only ~90 KB | **not recommended** |
| **A-e** build-time data groups (`make` drops groups) | e.g. a build without Block/Age or the binary properties | removes a group entirely | a new build-configuration axis the suite must cover (two builds), CI matrix; a pattern needing a dropped group says "requires module 'X'" (D26's existing tier, so the user-facing part is free) | **file with a trigger**: a library embedder asks for a smaller `libpcrec.a` |
| **A-f** compressed bitmaps per property (Frank's R2 suggestion) | one zlib'd 0x110000-bit map each | **measured 168 KB total after [UPROP-MORE]** (1.24x); good per DENSE property (`Lu` 492 B), poor in total | an inflater + 139 KB of scratch per decode | **not recommended**: measured worse than A-b in total |

---

## 4. Recommendation and staged plan

**Problem B: the form first, then sharing.**

| stage | what | lanes | trigger / gate (D77) |
|---|---|---|---|
| **B1-measure** | Time the VM route against the DFA route for wide classes (`\p{L}`, `\p{L}+`, `[\p{L}\p{N}]+`, `\p{Xwd}+`, `a\p{L}b`) on the utf8 bench regimes (ascii, latin1, cjk, mixed), with sizes beside each cell | 1 sonnet lane, plus a night window on the dev box (cleared with Frank) | none: it is the measurement every later stage reads |
| **B1-route** | At `--tune=size`/`min-size`, a row in engine selection routes a machine with a wide class to the VM kit form. Default and speed positions byte-identical. Stamped (`RX_ENGINE_SEL`). Spec hunk: `tuning.md` §5's preset cells | 1 lane (opus: engine selection) | B1-measure shows the VM route within the bound B3 names (≤ 1.5x) on the regimes that matter. If it is far worse, skip to the island |
| **B2-island** | UCP U3, as designed (T4 with θ per tune position). It also makes UCP `\w` buildable at default | 2-3 lanes (already UCP's) | U3's existing charter. [DATA-PLAN] adds the size goal and asks for the island's SIZE to be measured in its acceptance (the twin did not) |
| **B3-shared** | Data parts with content ids; the linkage table (`comdat` / `support-unit` / `static`); first clients the fold-pairs table and the kit predicates; the support unit's case maps re-expressed as data parts | 1 design + 1-2 build lanes; Mac probe for Darwin | the first general table ≥ ~16 KB that repeats across matchers ships ([UCD-RECORD], [SEQ-FOLD]'s fold table, [GRAPHEME]'s break table), OR a measured program with several matchers shows the duplicates as a material share. Today's 4-12 KB duplicates do not meet it |
| (idea) per-state accept | renumber accepting states so the accept probe is a compare | — | a size-leaning position still lands on the DFA form for a large automaton after B2 |

**Problem A: fix the format, nothing exotic.**

| stage | what | lanes | trigger |
|---|---|---|---|
| **A1-compact** | `generate.py` writes delta-varint interval lists and a string-blob name table (fold links too if they carry over); `mod_uprops` decodes at lookup. Byte-identical artifacts (the compiler's output does not change) | 1 sonnet lane, after `upropb` lands (no addendum to the running lane) | **already met**: [UPROP-MORE] takes UCD data from 11% to ~20% of the compiler (A2's 15% line), measured on `upropb`'s build. Expected: ~305 → ~90 KB, back to ~6% |
| A-groups | build-time data groups | — | a library embedder asks |
| A-record | the compiler derives sets from the [UCD-RECORD] table | — | [UCD-RECORD] is built for artifacts |

Stage order: B1-measure → A1-compact (independent, can run beside it) →
B1-route → B2-island (UCP's queue) → B3-shared at its trigger.

---

## 5. The three standing questions

**1. Measurement regime: RELEVANT.** Sizes: gcc 15.2 `-O2 -c`, x86-64 ELF,
`size -A` sections. The tables are `.rodata` and barely depend on `-O`
level, while code does (3-6 KB here). A different compiler would not
flip any decision, because the decisions rest on 20x ratios. Link-time
dedup depends on the toolchain (GNU ld measured; gold/lld/ld64 not), and
that is why B-a's row names its toolchain. The speed figures cited are the
island twin's (ubuntubudu, Zen 1, find-all, ns per code point). B1-measure
must name its own regime (find-all over the utf8 bench subjects, which box)
and say whether a hit-dense subject flips the VM-vs-DFA call. It might:
the VM pays per character where the DFA pays per byte.

**2. Independent control: RELEVANT for B-a, B-b and A-b.**
- B-a (shared tables): the danger is that a name collision makes the linker
  silently keep the wrong bytes. The control is a link-level check that reads
  the LINKED program's bytes for each `pcrec_d_<h>` (objdump, not the
  emitter) and compares them with each artifact's own `.o` copy, plus
  answer-identity for each artifact linked alone against all of them linked
  together. Neither shares a source with the hash function.
- B-b (routing): answer identity, default against size-leaning positions,
  over the whole corpus (`make test-axes` already sweeps `--tune`
  positions), plus the PC-4 live oracle (libpcre2), which is independent of
  both routes.
- A-b (compact encoding): the existing `uprops` differential against
  `oracle_store/libpcre2-10.46` checks every set's membership. It is
  independent of the generator, so a decoder bug cannot hide behind it.
  The population (every property row decoded at least once) is counted by
  the differential's own set list, not by the decoder.

**3. What moves when the data is regenerated: RELEVANT.**
- A-b: the `.inc` text changes form once (a generator change). After that,
  a UCD regeneration moves the same bytes it moves today. The compiler's
  output does not change, so this is not an abi event.
- B-a: a content id changes whenever a table's bytes change (UCD
  regeneration, a kit form change). The symbol names then change, so old
  and new artifacts in one program each keep their own copy. That is
  correct, but it costs size and is never wrong. Introducing the naming is
  an emitted-scaffolding change: an abi event, with readers of the abi
  number found by grep (D94) and the identity gates re-pinned. The spec gains
  the data-part linkage section (D80). [ART-SIZE]/the size log must count a
  shared table once per program; that is a reader to update in the same
  change.
- B-b: routing at size-leaning positions moves those positions' artifacts
  only. It is stamped, and the default is byte-identical. Per house practice
  it is still an abi event for the positions that move.

---

## 6. Questions for Frank (plain words)

1. **Default or opt-in?** A matcher for a big Unicode class (all letters)
   can be about 20 times smaller, but it may run up to about one and a half
   times slower on accented or mixed text. Do you want the small form only
   when someone asks for small (`--tune=size`), or should it become the
   default once we have measured it? *Leaning:* opt-in first, measure, then
   decide the default. Speed is the default promise.
2. **Is there a size you are aiming at?** For example, a matcher on a small
   device, or a limit for pcrec itself. Or is the aim just "don't be
   wasteful"? *Leaning:* no hard number. Keep Unicode data under about 15% of
   pcrec, and make big classes small on request.
3. **pcrec's own size: you were right, it is the format.** The new
   properties take pcrec's Unicode data from about 160 KB to about 305 KB,
   because each range is stored as two 4-byte numbers. Stored as small
   differences instead, the same data is about 3.6 times smaller (208 KB of
   ranges become 58 KB), with no decompression library, and it unpacks in
   about a microsecond per property. Real compression (zlib) gets it to about
   23 KB, but pcrec would then need a decompressor it does not have today.
   Compressed bitmaps per property measured worse in total (168 KB), because
   each of the 747 properties pays a fixed overhead. Is "small differences,
   no compression library" enough, or do you want the last 35 KB too?
   *Leaning:* small differences only, as the next step after the new
   properties land. Keep pcrec a single file (no data file beside it).
4. **Sharing across matchers: automatic or an explicit file?** On Linux with
   gcc the linker can keep one copy automatically (measured: three copies
   became one), with nothing extra for the user to build. The other way is an
   explicit shared file like subst's support unit. *Leaning:* automatic where
   the toolchain supports it, with the explicit file as the portable
   fallback. Build it when the first big shared table (the Unicode record,
   fold or grapheme tables) arrives, not now.

---

## Appendix A. Reproduction

Scratch only (`/tmp/claude-1001/datad/`, outside the repo). Artifact sizes:

    P=build/pcrec; $P -e utf8 -p rx --pattern '\p{L}' -o pL.c
    gcc -O2 -c pL.c -o pL.o; size -A pL.o   # .text = code, .rodata* = tables

and the same for every row of §1.3 (`--engine=vm`, `--tune=min-size`, `-i`,
`--ucp`, `--features all` as listed). Compiler symbols: `nm -S --size-sort
build/pcrec`; `size -A build/pcrec`. Support unit:
`worktrees/substland/build/pcrec --emit-support -o support.h`, compiled with
`PCREC_SUPPORT_IMPLEMENTATION`. Delta-varint: the `pcrec_uprop_iv` pairs
parsed from `src/parse/uprops_tables.inc`; for each list, varint(lo - previous
hi) + varint(hi - lo), restarting at 0 at each list boundary. Link dedup: three
TUs each defining one 8 KB `const` table under the same name, linked with a
2-line `main`. Variants: `__attribute__((weak))` (26,061 B), weak +
`-fdata-sections -Wl,--gc-sections` (9,645 B), and the section-attribute
comdat (`readelf -g` shows the COMDAT group; 9,677 B). DFA table
compressibility: rows/columns of `rx_forward_next_state` from `pL.c`.

Storage formats (§1.2): `data_plan/formats.py INC OUTDIR` parses `pcrec_uprop_iv`
and `pcrec_uprop_names` from a `uprops_tables.inc` (main's, and
`worktrees/upropb`'s at `d2e112042`, read-only). Distinct sets are keyed by
their pool span. It writes the varint blob and its zlib form, and prints every
row of the format table and the per-property table. The two-stage row
partitions code points by membership over all distinct sets (an event sweep
over interval ends), with blocks of 128 and u16 ids. Decode cost: `data_plan/dec.c`
(gcc -O2 -lz, scratch only) decodes the whole varint blob and zlib-inflates
its compressed form, 2,000 passes each, and reports µs per pass. The
`upropb` sizes are `size -A`/`size` on that worktree's `build/pcrec` and
`build/obj/parse/mod_uprops.o` (built 2026-10-24 11:52; the lane is still
running, so these are WIP numbers).
