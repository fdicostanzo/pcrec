# Addendum: the memfn kit (`memfn/`)

Seed only. The kit's own rules are in `memfn/CLAUDE.md`; read it and do not
restate it here. Adds to `../architecture.md`.

## Facts, not methods, across the pcrec->memfn boundary
pcrec sends facts about the pattern or site; the kit chooses the method. Never
say how the kit "would" use a fact. **Why:** a method-shaped field freezes one
method into the contract. **Source:** D157, D146. Detail: `../architecture.md`.

## Delegated sites are the kit's
A site delegated to the kit is emitted by the kit; both layers (scalar, SIMD)
are read when changing search or scan emission. **Source:** D146, D147,
`memfn/CLAUDE.md`.

## A kit byte move is a pcrec abi event
A change to bytes the kit returns that land in emitted text bumps the abi, with
the identity re-pin and spec hunk, in the same commit. **Source:** D76/D94,
`coding.md` §3.1, root `CLAUDE.md` situation index.

## One table per slot
The kit's declared FIND (Table B) is the ONE find mechanism. A private smaller
copy beside it is the failure mode: extend the table and call it.
**Source:** 2026-10-23 S3 code review (E-find); `../architecture.md`.
