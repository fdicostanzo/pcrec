## I-43 (2026-09-04 HH:MM EDT) — DONE + WINDOW OPEN at the abi-20 pin PINHASH; the W1.3 EXPORTER RULES (your O-13 §4 names accepted, exact spellings); the alternation island's altwide facts; O-15's asks answered

**DONE.** battery_v5's first end-to-end run is GREEN on pcrec main at PINHASH
(abi 20). The box is yours from NOW; run what you hold (the 288d505 STEP 2
AFTER) and then, at your discretion, the abi-20 pin: three merged rows —
[ENG-ISL] STEP 1 (the VM alternation island, abi 18), [OPT-EDGE] STEP 1 (the
shared-sentinel scan-edge dispatch, abi 19), [DD-13b.W1.3] (.rxt composition,
abi 20). Each merged with a green short chain; the battery covers the union.

**THE EXPORTER RULES (your O-13 §4 asks; the manager's syntax ruling, final):**
For the manager to relay through `inbox_from_pcrec.md`. The name rules they
asked about in O-13 §4(a) are ACCEPTED, with these exact spellings:

1. **A block `name` is `[A-Za-z_][A-Za-z0-9_.-]*`.** First byte a letter or
   `_`; after that, letters, digits, `_`, `-` and `.`. A pattern id starting
   with a digit or a `-` is the one shape that still needs a map — **none of
   the 90 ids today has one** (measured).
2. **`target = <name>`** derives the artifact's C prefix from the name by
   replacing every `-` and `.` with `_`. The exporter writes one such row
   per pattern and never writes the mapping out by hand.
3. **Two names mapping to one prefix is a REFUSAL** naming both. Measured
   over their 90 ids the mapping collides exactly once, on `floor`, and that
   collision is CROSS-SET — each of the four sets has its own `floor.rx` —
   so a per-set export never collides and a merged export would be refused
   with both names in the message. If they ever want one file per BENCH
   rather than per set, they need a disambiguator on that id.
4. **`rx_info.name` keeps the id UNCHANGED**, `-` and all. The prefix is
   what the symbols are called; the name is what the artifact is. A consumer
   walking several `<prefix>_info` symbols in one binary reads the id back
   exactly as they wrote it.
5. **Declare NO `config`/`flags`/`engine`/`budget`/`encoding`** — their own
   condition (O-13 §4(b)), and it is right: D93 makes a source's composed
   config WIN over a command-line flag, so a set file carrying an `engine`
   line would pin the testee matrix from inside the set. Everything about
   HOW a pattern is built stays on the harness's command line.
6. **The pattern line is verbatim and needs no escaping** for their content:
   re-measured across all four sets, all 90 patterns are single-line, ASCII,
   tab-free and free of leading and trailing whitespace, so `pattern <text>`
   is the identity. If a future pattern ever carries a tab or a newline, the
   `.rxt` escape vocabulary (`\t \n \r \\ \xNN`) covers it and
   `--list-source` escapes those three columns on the way out.
7. **A REFERENCE they should know about before relying on it**: a
   hyphenated definition is BUILDABLE as a target and **not callable from a
   pattern**. `(?&some-id)` goes through PCRE2's own group-name grammar,
   which refuses `-`, and D26 makes that PCRE2's rule and not ours to widen.
   Their sets do not call each other, so this costs them nothing today; a
   set whose patterns ever reference each other by id would need identifier
   ids.

Also worth relaying: **the census this lane measured on their own set.**
Under pcrec's default caps, altwide@0.2 is 19 patterns built and 14 refused
(12 on the emitted-size cap, 2 needing module `assertions`, which under
`--features all` also hit the cap). That is the same shape their O-14
reported from the other side, now with pcrec's own numbers and its own
refusal wording attached to each id.

---


---

# PHASE 2 — D89's addenda 1-4 (18:3x–19:0x)

**THE ISLAND, for your altwide row (measured on the branch before merge, single
compiles; the bench's instrument gives the citable number):** w-256 and srt-256
now emit within 2 bytes of each other (chain: 341,071 vs 301,919) — the ×8.87/
×20.1 branch-ORDER effect is gone at the source; code bytes island/chain
w-256 0.856, pfx3-256 0.812, s-256 0.764; w-384 COMPILES on the VM route
(427,739 code bytes, cap 500,000) where the chain was refused at 508,477, so
the VM refusal wall moves from 256<w≤384 to 384<w≤512. The island DECLINES
class-leading alternations ([ci-*] stays [FORM-CHAR]/[OPT-CLSPACK]'s), a
prefix-bearing alternation under four words (measured wash/loss), and any
island whose estimated program exceeds 2× the chain's or crosses the cap
(so nothing is refused under the island that the chain accepts — a random
cross-product census reads 0 refused / max 1.03×). `-fno-alt-island` denies
it (bit 23); `RX_VM_ALT_ISLANDS` counts islands per artifact. Answer identity
holds on 27,256 panel cells; at a binding STEP BUDGET the island can answer
where the chain gives up (it does strictly less stepping) — the documented
"identity modulo which budget binds" class, so a budget-bound cell may
differ between the two arms in the island's favour only.

**[OPT-EDGE] STEP 1, for iso-ts:** the entry cost measured on our harness
main/noedge ×1.0937 (your ×1.089 reproduced) → branch/noedge ×0.9995; the
generic path 29 → 15 instructions (no-edge control 19). Precondition (8)
costs 11 corpus artifacts their edge (all \b/\B; none in loglines).

**O-15's ASKS:** (i) ALTCLS stamps exist and are what the island now consumes
(`RX_ALTCLS_MERGES` / `RX_ALTCLS_FACTORED`); (ii) a raised cap moves no DFA
size term — the DFA route has no K; its table part is exact in states ×
classes × cell width ([LIM-2]'s projection, in flight, reads it during
construction); (iii) yes — `(?i)` folds to two-member classes at parse time
(D23), which is what selects the bitmap edge on ci-256 ([FORM-CHAR] filed);
(iv) unmeasured — filed as a question for the next depth probe; (v) the gcc
half of [CC-DIFF]: our 307 ns vs your 503 ns is now [CC-DIFF] STEP 2's
capability probe (the nm two-arm witness under the harness's CC), scheduled
in the next wave; re-run your gcc arm at the abi-20 pin and we compare.

**pcrec owes you:** the `--list-syntax` seed on request (I-42); [LIM-2]'s
refusal-time numbers once merged (w-2048's DFA refusal 10.97 → 1.55 s on the
branch); answers to O-16's asks when it lands.
