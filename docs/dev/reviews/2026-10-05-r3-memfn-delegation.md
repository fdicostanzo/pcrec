# 2026-10-05 r3 — light D6 panel: [MEMFN] integration.md revision 3 (D146 delegation)

Subject: `docs/design/memfn/integration.md` rev 3 (lane memfndel, merged 412d81c0). Two read-only critics:

- **delcrit1** (opus): the contract and migration soundness, checked against the emitters at main.
- **delcrit2** (sonnet): guards, coupling and build order.

Verdict: NO BLOCKER. The delegation architecture holds. But byte-identical zero-mover migration is NOT reachable through the hooks as specified, because today's sites have shapes the contract cannot express. And two errors repeat earlier ones: the stamp rule contradicts Frank's Q3 ruling, and the shipped in-emitter deny flags are unswept. All findings ACCEPTED (manager); revision lane memfndel4.

## Contract and migration (delcrit1)

| id | sev | finding | disposition |
|---|---|---|---|
| F1 | MAJOR | Hooks only write values. Real sites return on a miss (emit_dfa.c:5679-5683, :1221-1249), break (:8762), are whole functions (`ofs_test_emit_fn` :6180), or are expressions inside pcrec's own `if (guard && EXPR) goto` (runcmp.c:211, emit_vm.c:4481, :8627). There are no indent / function-name / on-miss hooks. | Add MF_H_EXPR, an on_miss statement hook, indent, and a function-form site (name and params). |
| F2 | MAJOR | ADVANCE returns only the cursor, but pcrec's post-loop reads the kit's run counter (emit_dfa.c:7587-7594); scan_test reads through `dir->peek`. | ADVANCE gains a count / bound-reached output and a `peek` hook. |
| F3 | MAJOR | In-emitter deny flags (`-fno-run-overlap` runcmp.c:65/73, `-fno-req-run-fold` arms) have no channel to the kit; I2 cannot see them silently die. | Carry every in-emitter deny onto mf_site; I2 sweeps every axes.def axis and every comment tier. |
| F4 | MAJOR | pcrec tracks emitted forms (`<PREFIX>_RUN_WORDS`, lazy helper placement, the returned row name); mf_result has no tally, and helper placement moves. | mf_result reports form counts; helpers are emitted "before first use". |
| F5 | MAJOR | Empty and wrapped ranges are undefined (bounded forms leave the cursor alone; `hi = n-1` wraps at n=0). | lo ≥ hi means "no write"; require `hi` without wrap. |
| F6 | MAJOR | The K82 handoff gate is one site of lead-byte + run + whole-run + rest-of-set; ALL_PRESENT has no position; set-leads' order is a rarity choice pcrec still makes; ON_CAND gives no order. | An "ALL_PRESENT + RETURN the leftmost of predicate i" op; ascending ON_CAND (descending if reverse); DELEG_SITES marks the ops that may feed a handoff. |
| F7 | MAJOR | Rule 3 (every term holds) contradicts `consumer` weighting and M5 (prefix_k drops terms, i.e. returns a superset). | REQUIRED vs OPTIONAL terms: RETURN promises c ≤ the true leftmost, with every REQUIRED term holding. |
| F8 | MAJOR | Totality needs every kit table to END in a generic scalar row, tested over a generated predicate space. BASELINE is not total for new shapes, so a deny would fail the compile (breaks D82). Shape limits are unchecked. | Require the generic row; baseline for a new shape = the portable scalar arm, declared, UNREACHED for G1; check shape bounds when the site is built. |
| F9 | MAJOR | plan_hint is "transitional", but the FROZEN baseline needs it forever. | pcrec keeps computing plan_hint, or M5 re-pins the baseline as a ruled abi event. |
| F10/F11 | MINOR | on_cand text may be copied (labels, statics, control flow out of the loop); no lower read guard (N3 reads subject[start-k], the reseed reads [from-1]). | Forbid those constructs; add a lower read-limit hook and a backward reach. |
| F12 | MINOR | Pinning the baseline to the whole artifact at the parent forces re-pins on unrelated abi changes; baseline arms duplicate pcrec helpers. | C5 checks a per-arm manifest digest. |
| F13 | NOTE | pcrec still prices kit-owned search code (dfa_cand_scan/ppm, hyb_reseed cost rows, set-leads, k82b). | List them under D146's "no cost comparison", each with its fate. |

## Guards, coupling, build order (delcrit2)

| id | sev | finding | disposition |
|---|---|---|---|
| G-F1 | HIGH | The movers-only stamp contradicts Frank's Q3 ruling (litscan_k82h.md: every artifact of the family, `none` where n/a; D81). | Stamp every artifact; do NOT stamp the kit version (form ids / MF_VOCAB only); the stamp's introduction is its own every-artifact abi event, landed before M1's replace with the byte-count re-pins (k82h §2.3a list); C11 on value, not presence. |
| G-F2 | HIGH | The shipped denies on the migrating sites (bits 32, 43, 44, 45, -fno-offset-skip) are not named and not swept; the kit's per-form switches are not axes (D144 item 4). | State each shipped deny's fate; add all of them to I2; per-form switches as real axes. |
| G-F3 | HIGH | The C9 cross-target syntax check fails on the Mac ("string.h not found") and is vacuous under `portable`. | A sysroot/header shim, a native-enabled config, and a K35 floor on arms compiled. |
| G-F4 | MED | armv8 has no verdict-grade guard. | State it plainly. |
| G-F5 | MED | G1's population comes from the kit's own `moved`; thin bins; undeclared regime. | Derive movers from a pcrec-side default-vs-deny artifact diff; declare the regime (standing question 1). |
| G-F6 | MED | G1's cadence misses kit re-tunes. | G1 runs on the movers of EVERY memfn abi event. |
| G-F7 | MED | C4's held-out plant is overclaimed and box-dependent. | Honest scope; case-insensitive matching. |
| G-F8 | MED-HIGH | Sabotage rows may not be mech-runnable (git archive, no history); the baseline digest lives in the kit. | Per-pattern pin digests under tests/; an in-tree C11 census; SAB_REACH on every row. |
| G-F9 | MED | The standing design questions are not answered. | Add the three sections (docs/design/CLAUDE.md). |
| G-F10 | MED | Freezing the baseline now would freeze K85's open regression and collide with live edits; the handoff is unmerged. | Sequence M1 after lane/k82hbuild merges and after K85's re-measure; post-migration edits to delegated emitters become kit-lane work. |
| G-F11 | MED-LOW | M1's scope exceeds its trigger cell; R4a/R4f are circular. | Narrow M1 to the triggering site class; fix the circularity. |
| G-F12 | MED-LOW | `-fno-memfn-native` polarity is inverted against house convention. | Axis `memfn-native` default OFF, enabled by `-fmemfn-native`; R4f is the flip (D112 shape). |
| G-F13 | LOW-MED | One shared request file breaks D78's single-writer rule (and the rulings-file-in-worktree failure). | Two files from day one; the manager is the sole writer of requests. |
| G-F14 | LOW | analyze/ is the inverse precedent (a leaf tool); the kit links into libpcrec, so `mf_*` symbols are exported unprefixed; Rust memchr provenance. | A symbol policy; per-file Unlicense provenance. |

## Reflection

The first revision with no blocker. The remaining gap is concrete, not conceptual: a contract written from the design's ideal sites rather than from the emitters' actual shapes. The critic who read the emitters line by line found every missing hook. Two items repeat because the lane was not given the rulings they contradict (Q3; the shipped denies). A design brief should name the standing rulings it must honour.

## Addendum: focused re-check of revision 4 (del4check, sonnet, 2026-10-05)

No blocker. CHECK 1: every §15 example reproduces the emitter format strings byte for byte (all cites verified, including the K82 gate on lane/k82hbuild 9bb97c7c and the memchr ratchet, 9 now and 3 after M1). CHECK 2: all 27 findings and all 7 rulings are mapped. CHECK 3: the stamp honours Q3 (a).

Residuals, all ACCEPTED to a small text fix:
- **C1-1 MED:** the K82 composite is written at two points in the buffer (file-scope FUNC parts, then the STMT at entry). Specify a define/use split and show it in §15.5.
- **C1-2:** a note tag hook for the block-indexed run comment.
- **C1-3:** the scan edge's peeled first ADVANCE (M3).
- **C2-1/C2-2:** stale row text (`mf_plan`, the "opening-keyword hook").
- **C3-1:** stale "movers only" text and MF_VOCAB wording.
- **C3-2:** weaken assertion 3 to `none` ⇒ identical, plus non-`none` ⇒ a non-baseline arm rendered, with a G2 fixture property.
- **C3-3:** add tests/litscan/reqcube.rxt to §18.3.
- **Notes:** C2-3, C2-4.
