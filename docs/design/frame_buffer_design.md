# The caller-provided frame buffer — the API shape ([DD-14.FB], D71 item 2)

**Status: PROPOSED. Nothing in this note is built.** It is the design record
behind `docs/spec/match_api.md` §10, which states the contract as it WILL be;
this document carries the alternatives, their measured costs, and the reasoning
the spec deliberately does not repeat (docs/spec/CLAUDE.md's charter: a spec may
reference a design document informationally, never normatively).

## 0. How to read this

### 0.1 Claim marking

Every load-bearing claim below is marked, and the marking is not decoration —
this project has been bitten repeatedly by design prose quoting numbers with no
probe behind them (subroutines_design.md's own V-7/V-11 residue).

- **MEASURED** — a number this lane produced on this box, with the command that
  produced it recoverable from §2's inventory.
- **CITED** — a number another lane measured and archived; the citation names it.
- **ARGUED** — reasoning, no measurement. Treated as the weakest kind.

### 0.2 The design in one paragraph

The three existing entry points keep their signatures, their return spaces and
their behaviour exactly. Three new entries — `<prefix>_search_in`,
`<prefix>_match_in`, `<prefix>_match_caps_in` — take one extra argument, a
`<prefix>_buffers` descriptor carrying `{frames, nframes, trail, ntrail}`, and
a `NULL` descriptor means "the stamped default", implemented by delegating to
the un-suffixed entry so there is exactly one copy of the default storage in
the artifact. **Both arrays are caller-providable, not just the resume stack**,
because §4 MEASURES that on the ruling's own worked specimen the TRAIL is the
binding array and a frames-only version of this feature would buy a caller
literally nothing. The default artifact's storage stays where it is today — on
the C stack of whichever un-suffixed entry the caller called — because §5.5
shows every other home is closed (a static breaks §5.3 thread-safety and TS-1;
a thread-local breaks callout reentrancy; allocation is forbidden by
construction). What the new entries buy is measured in §3: a `<prefix>_search`
frame of **131,296 bytes** becomes a `<prefix>_search_in` frame of **224
bytes**, and the arm that SIGSEGVs on a musl-default 128 KB thread today
returns a match instead.

---

## 1. The ruling, and the two things it does not say

D71 item 2, in full:

> The resume-frame buffer becomes CALLER-PROVIDED (pointer + capacity in the
> run struct instead of the inline `resume_stack[<PREFIX>_RESUME_FRAMES]`
> array; NULL → the stamped default, unchanged behaviour). A caller may hand
> over an mmap'd, lazily-committed reservation and get PCRE2-depth recursion
> with pcrec still never allocating; the stamped default (larger for
> call-bearing patterns per ASK 2, both implied subject sizes in the release
> note) is a DEFAULT, not the limit. Takes the frame array off the C stack
> ([TS-4]/DD-10's musl concern). A deliberate pre-v1 API addition — new entry
> point or run-state object, shape decided at docs/spec/match_api.md under D40,
> versioning per [DD-3].

**It does not say the TRAIL is included.** It names the resume-frame buffer and
the `resume_stack` array. §4 settles that by measurement rather than by the
manager's prior: the trail must be included, and a frames-only feature is
inert on the specimen the ruling itself cites.

**It does not say the default path comes off the C stack.** "Takes the frame
array off the C stack" is true of the NEW entry and false of the three existing
ones, which must stay byte-for-byte behaviourally identical — the two goals are
in direct tension and only the new entry can have both. §3 measures what that
means in practice, and §7's ASK-1 is the residue.

**[TS-4]/DD-10 as WRITTEN are about the COMPILER, not the matcher.** plan.md's
[DD-10] row (line 1240) and [TS-4] row (line 1549) both name `compile_ast` and
`clo_visit`'s t1 edge — pcrec's own compile path — against musl's 128 KB thread
stack. D71.2 invokes the same 128 KB ceiling for the EMITTED matcher's run
struct, which is a second, disjoint instance of the same concern. §3 shows the
matcher instance is live today and is worse than the compiler one, because it
does not need a 400-nested-branch-point pattern to fire: `^(a(?1)?b)$` on a
2-byte subject is enough.

---

## 2. The measurements this note produced

All on this box (x86-64, gcc as configured for the tree), against the worktree
build at `lane/srFB`. Scratch under the session scratchpad, never committed.

| # | axis | what it establishes |
|---|---|---|
| M1 | `sizeof` the emitted run struct, two artifact kinds | §3 — the C-stack cost, and that DD-14's own frame fields are what pushed it past 128 KB |
| M2 | `gcc -fstack-usage` on each entry, prototype included | §3 — 131,296 B → 224 B, the number the ruling is about |
| M3 | a 128 KB `pthread_attr_setstacksize` thread, three arms | §3 — the musl concern REPRODUCED as a SIGSEGV, and the remedy shown to fix it |
| M4 | give-up depth vs capacity, `^(a(?1)?b)$` on aⁿbⁿ, 9 capacities | §7 — the depth↔subject-size table, measured not reasoned |
| M5 | resume and trail capacities swept INDEPENDENTLY | §4 — 2.000 frames and 8.982 trail entries per nesting level; the trail binds |
| M6 | the pointer+capacity shape benchmarked against the inline shape | §6 — the push-site load costs nothing measurable |
| M7 | a 2 × 64 MB `MAP_NORESERVE` reservation driven to its ceiling | §8 — the worked example, run rather than computed |
| M8 | constant-time refusal of the runaway `^(a\|(?1)a)$` | §7 — the release note's second subject size, on the shipped artifact |

The prototype the M2/M3/M6/M7 arms exercise is a mechanical transform of a real
emitted artifact: the run struct's two inline arrays become
`rx_frame *resume_stack; unsigned resume_cap;` and
`rx_trailent *trail; unsigned trail_cap;`, the seven capacity-reading sites
(§11) read the fields, and a hand-written `rx_search_in` is appended. It agreed
with the unmodified artifact on every cell of an equivalence matrix INCLUDING
the give-up boundary (n = 342 matches, n = 343 returns `PCREC_ERR_FRAMES`, both
shapes, MEASURED) — which is what makes the timing and stack numbers comparable
rather than a comparison of two different programs.

---

## 3. The C-stack finding: [TS-4]'s matcher instance is LIVE, not prospective

**MEASURED (M1).** `sizeof(rx_run_state)` on a captures-default `-p rx
--features all` build:

| pattern | engine shape | `RX_RESUME_FRAMES` / `_TRAIL_FRAMES` | `sizeof(rx_run_state)` |
|---|---|---|---|
| `a(b\|c)+d` | statically bounded (`cost.frames + 1`) | 1 / 3 | **128 bytes** |
| `(a\|aa)+b` | unbounded, no calls | 2048 / 3072 | **98,360 bytes** (96.1 KB) |
| `^(a(?1)?b)$` | unbounded, call-bearing | 2048 / 3072 | **131,144 bytes** (128.07 KB) |

The breakdown for the last row: `slot_values` 40 B, `resume_stack` 2048 × 40 B
= 81,920 B, `trail` 3072 × 16 B = 49,152 B. A statically-bounded pattern pays
nothing — `src/gen/emit_vm.c:7106-7114` sizes the arrays exactly where
`vm_cost` can bound them and only falls back to `VM_DEFAULT_RESUME_FRAMES` /
`VM_DEFAULT_TRAIL_FRAMES` (`:87-88`, 2048 and 3072) when it cannot. **So this
cost is confined to the unbounded class, and the recursive patterns [DD-14]
exists for are all in it** (a recursive callee is `Cost.unbounded` by
construction, subroutines_design.md §5.7).

**MEASURED (M2), `gcc -O2 -fstack-usage`**, per entry, on the call-bearing
artifact:

| entry | stack frame |
|---|---|
| `rx_search` | 131,296 B |
| `rx_match` | 131,200 B |
| `rx_match_caps` | 131,216 B |
| `rx_match_anchored` (the shared internal) | 56 B |
| **`rx_search_in` (this design's prototype)** | **224 B** |

**586×**, and the reason it is that large a ratio rather than a modest one is
structural: the run state is the entry's own local, so the arrays are in the
entry's frame, and an entry handed a caller's pointers has no arrays to
declare.

**MEASURED (M3) — the concern reproduced.** A thread created with
`pthread_attr_setstacksize(&a, 128*1024)`, which is musl's default thread stack
size, calling the call-bearing artifact:

| arm | call | result |
|---|---|---|
| A | `rx_search(s, 684, 0, caps)` — a 684-byte subject | **SIGSEGV** (exit 139, core dumped) |
| B | `rx_search_in(...)` with 2 × 64 MB `MAP_NORESERVE` buffers, same subject | `rc = 1`, thread returns normally |
| C | arm B at n = 400,000 — an **800,000-byte** subject | `rc = 1`, thread returns normally |

Arm C is the one worth pausing on: on the SAME 128 KB thread that cannot
survive a 684-byte subject today, the new entry matches a subject **1,169×
larger**.

**AND THIS IS A LIVE DEFECT AGAINST A SHIPPED PROMISE, not only an input to
this design.** `docs/spec/match_api.md` §5.3 states, as a CONTRACT binding on
future emitters, that "any number of threads may call the same artifact's entry
points concurrently, provided each call has its own caps buffer". For a
call-bearing artifact on a musl-default thread that promise is false today, and
the caps buffer has nothing to do with it. The arithmetic locates the
regression precisely: the non-call unbounded artifact's `rx_search` frame is
98,512 B (MEASURED, M2) and fits; [DD-14] waves B+C added `call_ret` and
`call_top` to every frame (`src/gen/emit_vm.c:7443`), taking the frame from 24
to 40 bytes, and 2048 × 16 = 32,768 B is exactly the difference that pushes
131,248 over 131,072. **The manager should treat this as a finding independent
of whether this design lands**; §13 carries it as FINDING-1.

---

## 4. Frames or trail? The question D71.2 leaves open, SETTLED by measurement

subroutines_design.md §5.7 names `TRAIL_FRAMES` as the resume stack's sibling
and warns that "an artifact that under-sizes `trail_frames` returns
`PCREC_ERR_FRAMES` on a pattern it can match — S87/S95's exact failure mode".
The manager's prior was that the trail is caller-provided too, same mechanism,
one struct. **The prior is right, and it is not a matter of taste: a
frames-only feature would be INERT on the ruling's own worked specimen.**

**MEASURED (M5).** `^(a(?1)?b)$` matched against aⁿbⁿ, sweeping one capacity
with the other held far above binding, binary-searching the largest n that
matches:

| resume capacity | trail capacity | largest matching n | per nesting level |
|---|---|---|---|
| 1024 | 400,000 | 512 | **2.000 frames** |
| 2048 | 400,000 | 1024 | **2.000 frames** |
| 4096 | 400,000 | 2048 | **2.000 frames** |
| 200,000 | 1024 | 114 | **8.982 trail entries** |
| 200,000 | 3072 | 342 | **8.982 trail entries** |
| 200,000 | 8192 | 910 | **9.002 trail entries** |

Both are exactly linear in the nesting depth, and the ratio is **4.49 trail
entries per resume frame**. Against the stamped default of 2048 frames / 3072
trail, the trail runs out first by a wide margin:

- the default artifact gives up at **n = 342** (MEASURED, M4) — 342 × 8.982 =
  3,072, the trail capacity to the entry;
- at that n the resume stack holds 684 of its 2048 frames — **67% of the
  resume stack is unreachable**;
- and MEASURED directly: with the resume capacity raised to 200,000 and the
  trail left at its stamped 3,072, the give-up n is **still 342**.

So a caller who handed pcrec a gigabyte of resume frames under a frames-only
version of this feature would get `PCREC_ERR_FRAMES` at the same 684-byte
subject as today. **Both arrays, one descriptor.**

**Two implementation consequences follow, and neither is optional.**

1. `--backtrack-frames=N` sets BOTH capacities to N (`src/gen/emit_vm.c:7102-7105`,
   `cli/main.c:287-296`) and there is no separate trail control. Given the 4.49
   ratio that is the wrong shape — `--backtrack-frames=N` over-provisions the
   resume stack by ~4.5× relative to the trail it pairs it with. The descriptor
   makes it moot for a caller-buffer user; the CLI flag's own asymmetry is
   filed as §11's item 10 rather than fixed here.
2. `PCREC_ERR_FRAMES` already means "either array ran out" — both guards return
   it (`src/gen/emit_vm.c:7565`, `:7574`). This design does not change that,
   and §5's spec text says so plainly, because a caller who has just been told
   "frames" and doubles only the array named "frames" will not get a different
   answer.

---

## 5. The shape

### 5.1 Candidate (a): a caller-allocated run-state object

`<prefix>_run_state_size()` returns a byte count; the caller allocates that
much, calls `<prefix>_run_state_init(void *)`, and passes it to
`<prefix>_search_in(run, ...)`.

**Rejected**, on three grounds, the first of which is fatal:

- **It does not deliver the feature.** The run state's size is fixed at compile
  time by `RX_RESUME_FRAMES`/`RX_TRAIL_FRAMES` (`src/gen/emit_vm.c:7399-7407`).
  A caller allocating a bigger block does not get more frames unless the arrays
  become pointers or flexible members — which is candidate (b)'s mechanism,
  arrived at by a longer road and wrapped in an object the caller cannot size.
  To let the caller CHOOSE the capacity, `_run_state_size()` would have to take
  the two capacities as arguments, at which point the object is a descriptor
  with extra steps.
- It exposes a lifecycle where §5.2 of the spec promises none ("no match-data
  object, no allocation, no lifecycle to manage"). That promise is scoped to
  the match path and is one of the surface's genuinely distinctive properties
  against PCRE2's `pcre2_match_data`.
- The run state's LAYOUT varies per artifact (`v.has_calls` adds two fields per
  frame, `v.tracing` adds one more) — an opaque object whose size a caller
  queries at runtime invites the caller to cache the number across a recompile
  of the pattern, which is a silent buffer overrun rather than a diagnostic.

### 5.2 Candidate (b): a buffer descriptor on three new entries — RECOMMENDED

```c
typedef struct {
    void   *frames;    /* storage for resume frames; NULL = use the default */
    size_t  nframes;   /* CAPACITY IN FRAMES, not bytes */
    void   *trail;     /* storage for trail entries */
    size_t  ntrail;    /* capacity in entries, not bytes */
} <prefix>_buffers;

int       <prefix>_search_in    (const unsigned char *s, size_t n, size_t startpos,
                                 ptrdiff_t (*caps)[2], const <prefix>_buffers *buf);
ptrdiff_t <prefix>_match_in     (const rx_ctx *ctx, const <prefix>_buffers *buf);
ptrdiff_t <prefix>_match_caps_in(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2],
                                 const <prefix>_buffers *buf);
```

Recommended because it is the only candidate that delivers the feature without
inventing a lifecycle, and because the `NULL` case has a shape that keeps ONE
copy of the default storage in the artifact:

```c
int rx_search_in(..., const rx_buffers *buf)
{
    rx_run_state run;                       /* 224 bytes: no arrays here */
    if (!buf) return rx_search(s, n, startpos, caps);   /* the delegation */
    run.resume_stack = buf->frames;  run.resume_cap = buf->nframes;
    ...
}
```

**The delegation direction is load-bearing and is the opposite of the obvious
one.** The instinct is to make the old entry a thin wrapper —
`rx_search(...) { return rx_search_in(..., NULL); }` — but then `rx_search_in`
must own the default storage, so it declares the 128 KB of arrays on its own
frame unconditionally, and the caller who supplied buffers pays the stack cost
anyway. C has no way to declare a local conditionally. Delegating the other way
(`_in` with NULL calls the un-suffixed entry, which owns the default storage on
its own frame) gives both callers exactly what they asked for and costs the
NULL caller one tail call. **MEASURED (M2): this is where the 224 B comes
from** — the prototype's `rx_search_in` declares no `rx_run_buffers`.

There is still exactly one implementation of the matching loop underneath
(`<prefix>_match_anchored`, 56 B of frame), so this is not a second mechanism;
it is a second way to point the one mechanism's run state at storage.

### 5.3 Candidate (c): a per-artifact setter — declined, three ways

`<prefix>_set_buffers(void *frames, size_t nframes, ...)`, stashing the
pointers in a file-scope object.

**Declined, and the reasons are not stylistic:**

- **It is a mutable non-const static in the emitted file, which TS-1 fails by
  construction** (spec §5.3: TS-1 "scans every emitted file across nine
  emission shapes and fails on any non-const static object"). The check would
  reject the artifact, and it would be right to.
- **It breaks §5.3's concurrency contract outright.** Two threads calling the
  same artifact would share one buffer — a data race in pcrec's code, not the
  caller's, which is precisely the line §5.3 draws.
- **A thread-local does not rescue it**, and this is the version worth writing
  down because it is the one that looks like it works. `_Thread_local` fixes
  the cross-thread race and still breaks reentrancy: §5.3 promises "the same
  holds for one thread re-entering a matcher (from a callout, say)", and a
  re-entering call would resume on top of the outer call's live frames.
  It also makes every thread in a pool pay the memory whether it ever matches
  or not, and it is unavailable in the freestanding profile (§9).

### 5.4 `void *` or a typed per-artifact frame pointer? — settled, opaque

The type-safe alternative is to name the two structs (`<prefix>_frame`,
`<prefix>_trail_entry`), export them in the header, and type the descriptor's
pointers. A caller then writes `rx_frame frames[8192];` and gets size and
alignment right by construction, with the compiler enforcing it.

**Settled against it, on one decisive ground plus two supporting ones.**

- **The frame layout is genuinely per-artifact and would be exported as ABI.**
  `call_ret`/`call_top` exist only when `v.has_calls` (`src/gen/emit_vm.c:7443`)
  and `id` only under `--trace` (`:7404`) — MEASURED: 24 bytes on
  `(a|aa)+b`, 40 on `^(a(?1)?b)$`. Exporting that into the header pins an
  internal layout that three axes already move, pre-v1, for no contract gain.
- A caller with no C header — a `ctypes`/FFI/`dlopen` consumer — cannot use a
  typed pointer at all, and that caller is exactly the one who most wants a
  large reservation.
- The header does not carry the run-state types today (MEASURED: a split-form
  `.h` declares `RX_NCAPS`, the five entries and `rx_info`, and nothing about
  the run state), so the typed spelling is also the more invasive change.

**What replaces the type safety is arithmetic the caller can actually do**, and
it must be emitted or the opaque form is a trap. The header gains two sizing
macros beside the two capacity macros, and `rx_info` gains the same four facts
for the FFI caller who has no macros:

```c
#define RX_RESUME_FRAMES     2048   /* the stamped default CAPACITY */
#define RX_TRAIL_FRAMES      3072
#define RX_RESUME_FRAME_SIZE   40   /* bytes per resume frame, THIS artifact */
#define RX_TRAIL_FRAME_SIZE    16
#define RX_BUFFER_ALIGN         8   /* alignment both buffers require */
```

The descriptor takes CAPACITIES, not byte counts, deliberately: a caller who
gets the unit wrong by a factor of 40 under-allocates loudly rather than
silently, and the byte arithmetic appears exactly once, in the caller's own
`mmap` call.

### 5.5 Where the default lives when `buf == NULL`

**On the C stack of the un-suffixed entry, unchanged from today.** The brief
asks for the trade to be stated rather than assumed, and the trade is that
every alternative is closed:

| home | verdict |
|---|---|
| the entry's own frame (today) | **KEPT.** Thread-safe, reentrant, zero lifecycle, zero cost. Costs 128 KB of stack on an unbounded call-bearing artifact (§3) — the objection [TS-4] raises, and the one the new entry answers. |
| a file-scope static | closed by TS-1 and by §5.3 (§5.3 above) |
| `_Thread_local` | closed by reentrancy (§5.3 above) |
| `malloc` on demand | closed by construction — the emitted file's own header comment says "Allocated by the caller on the stack; this file never allocates" (`src/gen/emit_vm.c:7389`), and PC-5/D38 rules `COPY_MATCHED_SUBJECT` = NEVER on the same ground |

**The ruling proposed:** `buf == NULL` is defined to be exactly equivalent to
calling the un-suffixed entry, and the spec says so in those words rather than
describing where the storage sits — which keeps the storage location
non-contractual and leaves a future emitter free to shrink it.

---

## 6. What the pointer costs: the push-site load, MEASURED

The plan row accepts the cost in advance ("the push-site check reads the
capacity field — a load, not an immediate; codegen rule"). It is worth
measuring because it is the one objection that could sink the design, and
because the push site is the VM's hot path.

**MEASURED (M6).** The prototype against the unmodified artifact,
`^(a(?1)?b)$` on a²·³⁴²  subject, 20,000 iterations per run, five alternating
runs:

| run | inline arrays | pointer + capacity |
|---|---|---|
| 1 | 5.453 µs/call | 5.926 µs/call |
| 2 | 5.388 | 5.293 |
| 3 | 5.400 | 5.822 |
| 4 | 5.411 | 5.783 |
| 5 | 5.569 | 5.414 |

and on the non-recursive push-heavy `(a|aa)+b` over a 2,000-byte subject, three
runs each: inline 15.3 / 12.2 / 12.3 ms, pointer 12.3 / 12.4 / 12.7 ms.

**The honest reading is "no measurable difference", not "free".** The pointer
arm's mean is 5.65 µs against the inline arm's 5.44 — 4% slower — but the
ranges overlap on both arms, the inline arm's own spread is 3.3% and the
pointer arm's is 12%, and the non-recursive arm puts the pointer shape ahead.
Following §5.6 of the subroutines design's own discipline ("the seconds are one
run and the shape is the claim"), **the claim is that this instrument cannot
resolve a difference smaller than about 10%, and there is none larger than
that.** A lane that wants a sharper number should count instructions rather than
seconds; nothing in this design depends on the sharper number existing.

---

## 7. The stamped default (ASK 2) — **ASK-1**, with the numbers

### 7.1 The depth↔capacity table, MEASURED

**MEASURED (M4).** `^(a(?1)?b)$` against aⁿbⁿ, `--backtrack-frames=N` (which
sets both capacities to N), largest n that matches:

| `--backtrack-frames` | largest matching n | subject bytes | run-struct size |
|---|---|---|---|
| 256 | 29 | 58 | 16.5 KB |
| 512 | 57 | 114 | 32.0 KB |
| 1024 | 114 | 228 | 64.0 KB |
| **2048** | **228** | **456** | 128.0 KB |
| 4096 | 455 | 910 | 256.0 KB |
| 8192 | 910 | 1,820 | 512.0 KB |
| 16384 | 1,821 | 3,642 | 1.0 MB |
| 32768 | 3,641 | 7,282 | 2.0 MB |
| 65536 | 7,282 | 14,564 | 4.0 MB |

and at the artifact's actual stamped default — 2048 frames / **3072** trail,
which `--backtrack-frames` cannot express — **n = 342, a 684-byte subject**,
`PCREC_ERR_FRAMES` at n = 343.

**This corrects a CITED number.** subroutines_design.md §5.6's table says the
legitimate deep recursion "gives up at a ~2 KB subject at 1024 frames". That
was the design prototype's `RX_CALL_DEPTH = 1024` counter, which D71.1 then
ruled out of the default artifact; the shipped artifact's give-up is at **684
bytes**, three times smaller. The design's own conclusion is unchanged and in
fact sharpened — libpcre2 was CITED matching 800 KB where pcrec now refuses at
684 B, a factor of **1,169**, not the 390 the design computed.

### 7.2 The runaway, on the shipped artifact

**MEASURED (M8).** `^(a|(?1)a)$` — the left-recursive runaway — against aⁿb on
the current default artifact:

| n | 100 | 1,000 | 4,000 | 10,000 | 20,000 | 100,000 |
|---|---|---|---|---|---|---|
| result | `-3` | `-3` | `-3` | `-3` | `-3` | `-3` |
| time | 0.00060 s | 0.00078 | 0.00063 | 0.00059 | 0.00060 | 0.00059 |

**Flat across a 1,000× range of subject size** — the constant-time refusal
DD-2/D22 asks for, on the shipped artifact rather than on a prototype. CITED
against it, from subroutines_design.md §5.6 / `out/leftrec.txt` axis L9b:
libpcre2 10.46 spends 2.6–5.6 s at n = 20,000 finding out, growing with a
measured exponent of 2.04.

### 7.3 The release note's two subject sizes

Per D71.2's requirement that the release note state both:

> A pattern whose recursion depth grows with the subject gives up
> (`PCREC_ERR_FRAMES`) at a **684-byte** subject on `^(a(?1)?b)$`-shaped input
> at the stamped default, where libpcre2 10.46 matches 800 KB. The same
> default refuses the left-recursive runaway `^(a|(?1)a)$` in **0.0006 s at
> every subject size measured, from 100 bytes to 100 KB**, where libpcre2 pays
> a cost growing as the square of the subject — 2.6–5.6 s at n = 20,000. The
> stamped number is a DEFAULT, not a limit: a caller that hands pcrec a
> 128 MB `MAP_NORESERVE` reservation matches the same 800 KB subject in
> 0.056 s, touching 90 MB, with pcrec still never allocating (§8).

### 7.4 ASK-1: should the stamped default for call-bearing patterns be RAISED?

D71 item 2 carries forward ASK 2's "larger for call-bearing patterns". **The
measurements say raising it makes the [TS-4] problem the SAME ruling cites
strictly worse, and I cannot settle a release-note-visible number that Frank
has already ruled on once.** Three options, with the numbers:

| option | frames / trail | run struct | give-up n | musl 128 KB thread |
|---|---|---|---|---|
| **(a) keep 2048 / 3072 — RECOMMENDED** | 2048 / 3072 | 128.07 KB | 342 (684 B) | already SIGSEGVs (§3) |
| (b) raise, e.g. 8192 / 12288 | 8192 / 12288 | 512.0 KB | 1,366 (2,732 B) | 4× further over |
| (c) LOWER to fit musl, e.g. 512 / 2304 | 512 / 2304 | 56.0 KB | 256 (512 B) | fits, with headroom |

**Recommendation (a), keep it.** The reasoning is the failure-direction
asymmetry the step budget's 500M (D51.3) and the work budget's 10⁹ (D49.2) were
both calibrated by, applied to a resource those two do not spend. The step and
work budgets buy TIME and were calibrated to tolerate ~1 GB of ordinary
subject, because refusing an ordinary large-subject match on the shipped path
is the worse error. The frame capacity buys DEPTH and is paid for in C STACK —
a resource with a hard, small, platform-imposed ceiling that no amount of
"ordinary subject" reasoning can move. At 2048/3072 pcrec is already 0.07 KB
over musl's entire thread stack; option (b) buys 4× the depth for 4× a cost
that is already past its ceiling, and buys it for exactly the artifacts that
have a better remedy available. **Once a caller buffer exists, the honest
calibration target for the DEFAULT stops being "how deep can we go" and becomes
"how little stack can we spend while still handling the shallow case", which is
an argument for (c), not (b).**

I recommend (a) rather than (c) only because (c) is a behaviour change to
shipped artifacts that deserves its own evidence — how shallow is "shallow
enough" is a population question this lane has no population for. Filed as
§11's item 11.

---

## 8. mmap'd, lazily-committed reservations — worked and MEASURED

**MEASURED (M7).** Two 64 MB `MAP_NORESERVE` reservations handed to the
prototype's `rx_search_in`, on `^(a(?1)?b)$`:

```
reserved 2 x 64 MB MAP_NORESERVE -> 1,677,721 frames (40 B each),
                                    4,194,304 trail entries (16 B each)
RSS before match: 1,704 KB
```

| n | subject | result | time | RSS after |
|---|---|---|---|---|
| 342 | 684 B | `rc = 1` | 0.0001 s | 2,088 KB |
| 100,000 | 200 KB | `rc = 1` | 0.0135 s | 24,104 KB |
| **400,000** | **800 KB** | **`rc = 1`** | **0.0556 s** | **90,284 KB** |
| 466,000 | 932 KB | `rc = 1` | 0.0654 s | 104,876 KB |
| 470,000 | 940 KB | `PCREC_ERR_FRAMES` | 0.0690 s | 105,132 KB |

with the NULL-buffer control on the SAME artifact returning `PCREC_ERR_FRAMES`
at every one of those n.

Three things this establishes rather than asserts:

1. **The 800 KB row is libpcre2's own measured depth**, CITED at 0.24–0.34 s
   from the heap (subroutines_design.md §5.6). pcrec reaches it in 0.056 s and
   never allocates. The ruling's claim — "PCRE2-depth recursion with pcrec
   still never allocating" — is met with margin.
2. **`MAP_NORESERVE` does what the ruling wants it to.** 128 MB reserved costs
   1.7 MB of RSS until touched; at n = 400,000 the process has touched 88 MB,
   which is the arithmetic exactly (400,000 × 2 frames × 40 B = 32.0 MB, plus
   400,000 × 8.982 trail × 16 B = 57.5 MB, = 89.5 MB against 88.6 measured).
   The caller reserves for the worst case and pays for the actual one.
3. **The ceiling is predictable from the emitted numbers.** Predicted binding:
   trail, at 4,194,304 / 8.982 = 466,967 levels. Measured: 466,000 matches,
   470,000 does not. A caller CAN size a reservation from `RX_TRAIL_FRAME_SIZE`
   and its own knowledge of the pattern.

The spec's §10 carries a shortened version of this as its worked example, with
the `mmap` call written out.

---

## 9. The freestanding / embedded profile (M7's)

A caller with no `mmap` has two routes and neither needs one:

- **Pass `NULL`** and get the stamped default, which is what every caller gets
  today. Nothing about the freestanding profile changes.
- **Point the descriptor at the caller's OWN static storage.** This is legal and
  is worth saying explicitly, because it looks like it should violate TS-1:
  it does not. TS-1 scans the EMITTED FILE for non-const statics; storage the
  embedder declares in its own translation unit is the embedder's business, and
  the embedder is the one who knows whether its own matcher calls are
  concurrent. An embedded caller that knows it has exactly one matching context
  puts the buffer in `.bss`, keeps its stack tiny, and pays nothing.

Both routes make this design STRICTLY better for the freestanding profile than
the status quo, where a call-bearing artifact's only option is 128 KB of stack.

---

## 10. Versioning ([DD-3], D40) and the identity gate

**[DD-3] has no policy yet** — plan.md:1238, `STATE:not-started`,
"generated-API versioning/compat policy for vendored consumers". So D40 governs
alone: pre-v1, breaking changes are "unconstrained in substance and governed
only in FORM — one announced break commit, populations conserved and
accounted, never silent drift".

**What breaks and what does not:**

| surface | verdict |
|---|---|
| the three existing entry points' signatures, return spaces, semantics | **UNCHANGED.** Source- and binary-compatible. A consumer that never calls an `_in` entry recompiles with no edit. |
| the emitted run-struct text | changes on every VM artifact. Never contractual — it is `.c`-private today (MEASURED: absent from the split-form header) and spec §5.2 promises there is no match-data object. |
| `rx_info`'s layout | **BREAKS.** Four new fields ⇒ `abi` 2 → 3. Spec §6 already says `abi` is "a layout version and nothing more… do not build version negotiation on it until v1". |
| the header's macro inventory | grows by three (`_RESUME_FRAME_SIZE`, `_TRAIL_FRAME_SIZE`, `_BUFFER_ALIGN`) plus the two capacity macros moving `.c` → `.h`. Additive. |

**The identity gate's control needs restating, and [ABI-NS] is the precedent.**
subroutines_design.md §9.1's gate asserts that a call-free pattern's artifact
is byte-identical across the module axis. This change is not on that axis — it
is unconditional emitter surgery on every VM artifact, exactly the shape
[ABI-NS] (D60) had when it moved eleven macros and changed every artifact's
emitted text. That was handled as an announced pre-v1 boundary with populations
conserved, and this should be too. **The controls that survive, and they are
stronger than byte-identity:**

1. **The whole `.rxt` corpus is the behavioural control** — every cell must
   give the identical answer through the un-suffixed entries, populations
   conserved and accounted. 25,271 cells at the lane's baseline.
2. **A structural control on the entries**: `tests/codegen/` asserts that the
   three existing entries' emitted DECLARATIONS are unchanged, character for
   character, so a wrapper that quietly changed a signature fails the check
   rather than the corpus.
3. **The module-axis identity gate is untouched** — a call-free artifact still
   differs from a call-bearing one in exactly `v.has_calls`'s fields, and this
   change is orthogonal to that axis.

A design that instead gated the whole feature on `v.has_calls` would preserve
byte-identity for non-call artifacts and is rejected on Frank's standing
direction (2026-08-23: general mechanisms, no special-case folds) and on the
merits — §3 MEASURES the non-call unbounded artifact at 98 KB of stack, which
is the same problem one size smaller, and §4's trail exhaustion is not a
recursion-specific failure either.

---

## 11. The implementation lane's checklist

Ordered, with the section that specifies each. Nothing here is built.

1. **Name the two anonymous structs** (`src/gen/emit_vm.c:7401-7406`) so the
   run state can hold pointers to them. Per-artifact spelling, `.c`-private —
   NOT exported (§5.4).
2. **Split the run state**: the arrays leave `<prefix>_run_state`, which gains
   `resume_stack`/`resume_cap`/`trail`/`trail_cap`; a new `<prefix>_run_buffers`
   holds the two stamped-default arrays (§5.2). MEASURED target: the run state
   at 224 B of frame (§3).
3. **Convert the SEVEN capacity-reading sites** to read the fields
   (`src/gen/emit_vm.c:5705` — the region-exit `_R_INTERNAL` guard — plus the
   `RX_TRAIL`/`RX_PUSH` pairs at `:7565`/`:7574` and their tracing twins at
   `:7599`/`:7610`, and the two `RX_CALL` variants at `:7664`/`:7677`). §6
   measures the cost of the load; §11.3's sabotage row is where a missed site
   is caught.
4. **`<prefix>_run_state_init` (`:7702-7719`) must NOT clobber the four new
   fields** — they are wired before it is called. This is §5.6 site 5a's exact
   failure mode one field further along, and the initialiser's current shape
   (it writes every field it knows about) is what makes the mistake likely.
5. **`<prefix>_reset_for_next_attempt` (`:7736-7746`) must not touch them
   either** — a bump-along keeps the caller's buffers, and keeps its budgets,
   for the same reason.
6. **Emit the three `_in` entries** with the delegation direction of §5.2
   (`_in` with NULL calls the un-suffixed entry, never the reverse), plus the
   `<prefix>_buffers` typedef. Declarations join the header.
7. **Emit the sizing surface** (§5.4): `_RESUME_FRAME_SIZE`, `_TRAIL_FRAME_SIZE`,
   `_BUFFER_ALIGN` macros, the two capacity macros moved into the header, and
   `rx_info`'s four new fields with `abi` 2 → 3 (§10).
8. **Emit the whole surface on a DFA artifact too, inert** — the three `_in`
   entries, the descriptor type and all five macros, with the four sizing
   macros and the four `rx_info` fields reading `0` and an `_in` entry
   ignoring its descriptor. This is §4's "reserved but unreachable" shape,
   the one the give-up codes already have, and it is a DEPARTURE from §6.3's
   rule that per-artifact capacity macros are VM-only. The reason the
   departure is right: §6.3's macros report what the artifact DID, so a
   DFA artifact genuinely has nothing to report; these report what a caller
   needs in order to CALL it, and engine selection is not the caller's
   choice. §6.3's own closing warning — "a consumer that `#if`s on
   `RX_ENGINE` is writing code that does not compile against half the
   artifacts pcrec produces" — is the failure this avoids. Spec §10.4.
9. **The capacity type.** The descriptor's counts are `size_t`; the depth
   counters are `unsigned` (`:7407`). Either widen the counters or clamp and
   document the ceiling — a caller passing `nframes > UINT_MAX` must not get a
   silently truncated capacity. §12's P-3 is this.
10. `--backtrack-frames=N` sets both capacities to N with no trail control
   (§4). Filed, not fixed here.
11. The stamped default's own value — **ASK-1** (§7.4), Frank's call.

**The cells** (§10.3 of the subroutines design records that the harness has no
way to EXPECT a give-up; a `gu` directive has since landed per D72):

- a `^(a(?1)?b)$` cell at n = 343 that EXPECTS `PCREC_ERR_FRAMES` through the
  default entry, and the same subject MATCHING through `_search_in` with a
  larger buffer. **This needs a harness route the `.rxt` format does not have**:
  `budget frames=` sizes the ARTIFACT, not the call. Two candidates —
  (i) a `frames-buffer=N` directive that makes the harness driver allocate and
  call `_search_in`, or (ii) a C-driver cell in `tests/recursion/` outside the
  `.rxt` corpus. **Recommend (i)**: it keeps the oracle comparison in the
  corpus where every other semantic cell lives, and the driver already
  synthesises the call.
- the arm-A/arm-B pair of §3 as a `tests/cli`-style stack case — a 128 KB
  thread that must SIGSEGV on `_search` and must NOT on `_search_in`. This is
  also the test [TS-4] itself has been missing ("case 8 covers branch COUNT,
  nothing covers nesting DEPTH").
- an `_in(..., NULL)` cell asserting bit-identical output to the un-suffixed
  entry across a spread of patterns — the delegation's own control.

**The sabotage rows** (each must be caught, or the check fails itself):

| row | sabotage | what must catch it |
|---|---|---|
| S-FB1 | `_search_in` passes `RX_RESUME_FRAMES` (the stamped constant) instead of `buf->nframes` | the larger-buffer cell stops matching at n > 342 |
| S-FB2 | `_search_in` passes `buf->nframes` as the TRAIL capacity and vice versa | the equivalence matrix diverges; with the 4.49 ratio it will over-run the frame array before it reports |
| S-FB3 | `run_state_init` re-zeroes `resume_stack`/`resume_cap` (item 4) | every `_in` call with a buffer faults or gives up at 0 |
| S-FB4 | one of the seven capacity sites keeps the immediate (item 3) | a buffer larger than the default over-runs at exactly the stamped capacity — this is the row that justifies enumerating all seven |
| S-FB5 | the `buf == NULL` delegation is dropped and `_in` runs with a NULL `resume_stack` | the NULL-equivalence cell |
| S-FB6 | `_RESUME_FRAME_SIZE` is stamped from the wrong struct | a cell that allocates `N * RX_RESUME_FRAME_SIZE` bytes and runs to the ceiling under ASan |

---

## 12. What would refute this — predictions

- **P-1.** The 4.49 trail:frame ratio is a property of THIS specimen's `|W|`
  (three slots — MEASURED, the artifact's three `RX_SET` restore lines), not a
  universal constant. A callee with a larger `|W|` moves it. What is NOT
  specimen-specific is the CONCLUSION: the trail can bind, so it must be
  caller-providable. A specimen where the frames bind first would not refute
  §4; only a proof that the trail can NEVER bind would, and §5.7 of the
  subroutines design already names the failure mode (S87/S95).
- **P-2.** If a real emitter change measures a throughput regression larger
  than §6's ~10% resolution, the pointer shape is wrong for the hot path and
  the fallback is to keep the inline arrays for the default entry and emit a
  SECOND matching loop for the `_in` entry — two copies of the loop, which is
  the parallel mechanism Frank's standing direction rules out, so the honest
  fallback is instead to accept the regression or drop the feature.
- **P-3.** The `size_t` → `unsigned` narrowing (item 9) is the most likely
  place a real implementation introduces a silent bug, because a 4 GB
  reservation is a plausible thing for the very caller this feature targets to
  hand over. Predict: the first implementation clamps without documenting it.
- **P-4.** `rx_info` gaining four fields will break something that reads the
  struct positionally. Predict: nothing in-tree, because nothing reads it
  positionally; a vendored consumer is D40's announced-boundary problem.

---

## 13. Findings and ASKs

**FINDING-1 (independent of this design, for the manager).** A call-bearing
VM artifact's `rx_search`/`_match`/`_match_caps` SIGSEGV when called from a
musl-default 128 KB thread — MEASURED (§3, M3), on a 684-byte subject. The
entries' stack frames are 131,296 / 131,200 / 131,216 bytes. This makes
`docs/spec/match_api.md` §5.3's concurrency CONTRACT false for that artifact
class today. It arrived with [DD-14] waves B+C (the two per-frame call fields
took the frame from 24 to 40 bytes, and 2048 × 16 B is exactly the difference
that crosses 128 KB); the non-call unbounded artifact sits just under, at
98,512 B. This design's `_in` entries fix it for callers who use them; they do
not fix it for the default path (§7.4's option (c) would).

**ASK-1 (§7.4).** The stamped default for call-bearing patterns: keep
2048/3072 (recommended), raise it per ASK 2's original direction, or lower it
so the default path fits a musl thread. All three measured in §7.4's table.
Frank ruled "(b) — a LARGER stamped default" on 2026-08-23 before the C-stack
cost was measured; this lane's measurements point the other way, so the ruling
is re-put rather than quietly reinterpreted.

**Settled without an ASK, recorded so a reviewer can disagree deliberately:**
the trail is caller-providable too (§4, by measurement); the descriptor is
opaque rather than typed (§5.4); the `NULL` default stays on the C stack
(§5.5); the delegation runs `_in` → un-suffixed, not the reverse (§5.2); the
feature is emitted on every VM artifact rather than gated on `v.has_calls`
(§10).
