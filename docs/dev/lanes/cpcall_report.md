# cpcall — compound/callout alignment (D163 addendum 5): report

Lane `cpcall`, 2026-10-12, opus, docs only, from main `ca4a5f22` (abi 76). Branch
`lane/cpcall`. Deliverable: `docs/design/compound_callout_alignment.md`, plus entries in
`docs/design/CLAUDE.md` and `docs/dev/lanes/CLAUDE.md`. Nothing under `src/`, `tests/` or
`docs/spec/` changed. No build and no suite were run (a box hold was in force, and the lane
did not need either).

## Headline

- **There is no B0 conflict.** Keep the default "every entry exported" (D38.3). Do not
  model callout bindings as entries. Never classify an undefined reference as omittable.
- **Two MUST-change items in compound.md before B4:**
  1. `match_api.md` §4¶10 binds "a composed submatcher" call site, and says the first
     emitted one takes the obligation. B4's controller is that first site. compound.md
     §B.2's `if (r != 0) return r;` returns STARTPOS and INTERNAL where §4¶10 traps.
     Proposal: one first-match call-site code table, keyed by what the callee can return,
     for parts and callouts alike. B4 emits rows 1, 2 and 8, a dead trap under each part
     call. The §4¶10 spec hunk goes in B4's commit.
  2. D163 add. 3 says each part declares the groups it writes and reads, but `CompPart`
     has no such field. Add `groups` (identity for split; the pad rule is read off it).
- **Soft and cheap now on cpb02:**
  - B1: give `CompPart` the `groups` field;
  - B1: build `PB_ONE_ATTEMPT` as a general emission option (unlock U1: one-attempt
    `_match` on every attempt route);
  - B2: word `RF_CROSSES_ATTEMPTS` as "observes or changes the attempt sequence".

## What is built for callouts today

The ABI types (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_renderfn`) and `<prefix>_match`
typed `rx_matchfn` are built. So is the `(?C` registry row (PLANNED; refuses with "requires
module 'callouts'"). Everything else is design-only:

- the call sites and the §4¶10 trap;
- the binding;
- captures-so-far (`ncap` is always 0);
- the syntax (D38 item 7, open);
- the PCRE2-compat block.

No test binds an `rx_callout_ref`.

## The one design (note §3)

A part and a callout are one thing, a pcrec-compiled callee, bound at compile time inside
one artifact or at link time to another. Each seam gets one rule:

- **Return codes:** the code table (§5).
- **Captures (§6):** one group map per binding, one inbound channel (`rx_ctx.caps`, which
  client 7 needs as much as callouts do; no engine consumes it today) and
  delivery-on-success. D38 item 5's v2 is re-specified as an `rx_matchcapsfn` plus `ncaps`
  on `rx_callout_ref`; the non-const `rx_ctx` is withdrawn.
- **Budgets:** one meter per exported call (§7, Q1).
- **Naming:** a namespace reservation table with `__` as row 1, plus a finding: the
  [EMIT-ENTRIES] public request needs D38.3 re-ruled (§8).
- **State:** `rx_ctx.session` with a shared half and an owner-tagged cache (§9). Without
  the tag, a compound used as a callout would read the outer artifact's cache.
- **Stamps:** a link-level kind (§10.1).

## Unlocks and questions

- **Unlocks U1-U6 (§13)**, among them validate-once across a call chain (U2: today a
  `-futf-check` callee re-validates per fire, O(n²), derived from the spec and not
  measured) and "a callout to a known pattern lowers to a part" (U3).
- **Questions for Frank (§11):**
  - Q1: the budget unit. Lean: one meter per exported call.
  - Q2: callout purity. Lean: yes; A3 is lifted later.
  - Q3: INTERNAL from a callee. Lean: propagate.

## Resume point

The note is complete. Next is the manager's call: fold §14.1 into compound.md (a light
revision, rev 2.2) before the B4 brief, pass §14.3 to cpb02, and relay Q1-Q3.
