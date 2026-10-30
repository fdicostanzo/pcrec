# Emit backends: forward notes (not a design, nothing scheduled)

Status: FORWARD THINKING ONLY. Frank, 2026-10-30: "We do nothing now to be
clear. Just forward thinking." No plan row, no lane, no trigger armed. This
note records the conversation so a future design starts from it instead of
re-deriving it. When a design is written, it opens with GOALS
(`docs/design/CLAUDE.md`) and answers the standing questions there; this
note does neither.

## Where the thought came from

The record-first VM emitter (review r6/r8/r9, lane vmrec, step (a) built
2026-10-30): every statement the VM emitter writes is a typed record (29
kinds, `src/gen/vm_stmt.h/.c`), and one renderer per kind turns it into C.
r8's ruling: "the record is the source, text rendered from it". Once that
holds, the renderer is the ONLY place that knows the target is GNU C.

## Ideas recorded (Frank, 2026-10-30)

1. **Record-level cleanups.** Some emitted code is plainly redundant, e.g. a
   jump to the very next instruction. With records these become record
   transforms (r9: post-render rewrites are record transforms), not text
   edits. Expected payoff: artifact size, the user's compile time,
   readability. Match speed probably does not move, since gcc -O2 likely
   folds such jumps already: measure it, don't assume. They change emitted
   bytes, so they cannot ride step (a) (byte identity); each is an abi event,
   and as a simplification it gets no flag (memory
   pcrec-flag-follows-caller-effect).
2. **A different code target.** A second renderer could write something
   other than GNU C. Candidates in rough order of user value: portable C (a
   `switch` instead of computed goto, so MSVC can build it), Rust/Zig
   source, LLVM IR or WASM directly. Frank: no short-term target plans.
3. **A bytecode VM.** The records are already close to an instruction set
   (typed kinds, operands, labels). Writing them as a bytecode array plus one
   generic interpreter would be a real bytecode VM: tiny artifacts, no C
   compile (relevant where gcc compile time explodes, R1 A-3), and a possible
   runtime-compile mode. The cost is match speed and pcrec's stated identity
   ("specialized C, no runtime interpreter", CLAUDE.md / APPROACH.md). That
   is a POSITIONING question for Frank, so at most an optional backend, never
   the default.
4. **A standard interface, pluggable target libraries** (Frank's framing):
   pcrec parses, analyses and optimizes, then emits a versioned record stream
   (a "matcher IR" with its own spec, like the abi); backend libraries each
   consume it and write one target.
5. **memfn on the other side of the wall** (Frank). The kit turns facts into
   target text (scalar loops, libc calls, SIMD forms), which is target
   specific by nature. In a backend world pcrec emits a search-site record
   carrying FACTS; the C backend hands it to memfn; another backend serves
   the same fact its own way (e.g. a built-in scan instruction in bytecode).

## Why the present design already points this way

- D146/D157: pcrec -> kit carries facts only and never presumes the kit's
  method. That is exactly the shape of an IR/backend boundary.
- r9 ruling for VM step (c): kit windows are opaque, with KIT-DECLARED
  EFFECTS. pcrec needs the effects (its side of the wall); the text is the
  backend's.
- Coupling would get cleaner: today a kit byte move is a pcrec abi event
  (memfn/CLAUDE.md, D146/D147); with backends it would be a version event of
  the C backend, and pcrec's IR would not move.

## Prerequisites (if this is ever taken up)

1. The DFA engines on records. Today only the VM emitter has them
   (`emit_dfa.c` writes text; [ENG-FORM]/D82 holds its form as a value, not
   as statement records), so an interface would cover half the artifacts.
2. The kit's windows: either records, or a per-backend kit.
3. A public IR is a contract: spec hunks (D80), versioning, stability, and
   slower change to the record set. Internal records can change freely.

## Leaning recorded with the ideas

- Do not publish the interface before a SECOND backend actually exists. With
  one consumer, any contract is shaped by GNU C and gets its first real test
  from the second backend anyway (D77, build under measurement).
- Meanwhile it costs nothing to keep new emitter work record-shaped (VM steps
  (b) and (c) already are) and to keep the kit boundary facts-in, text-out.
- Plausible future triggers: a user need for a non-GNU-C target (MSVC is the
  likeliest), a need for runtime compile, or a pattern class whose C compile
  time is the bottleneck.
