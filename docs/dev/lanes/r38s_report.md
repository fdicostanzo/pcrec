# r38s — R-38 interface sheet (span arms L2/L3 seam)

STATE: delivered. Lane r38s (kit design lane, opus), 2026-11-09, branch lane/memfn-r38s off
lane/u3mech 404cff6ea. Design only: no code, no `make`, no boxqueue job.

## Summary

Wrote `docs/design/memfn/span_runs_sheet.md` (rev 0): what crosses the pcrec <-> kit seam for
R-38, as facts, so L2/L3 can build against it. Read: R-38 and span_arms.md rev 2.2 (§5.2, §5.4,
§5.5, §8, §12a, §12b) and D157/D172/D187/D190/D191 from main; plan_frame.md rev 2.2 from
lane/memfn-s30a; memfn.h, compose.c `pres_layout_check`, presence.c `kit_pres_picks`,
emit_dfa.c `req_run_member`/`req_pres_spans`/`req_site_define` and req.c `pcrec_req_window` at
this base. One measurement: `build/pcrec --emit-facts` (main's binary, read-only) on
`xabcdefghijkq\w` gives `req_run 65666768696a6b71@7`, `req_run_maxoff 5`,
`req_landmark_maxoff 5` (the cut window at `at` 5), the input to the sheet's question 1.

## The interface sheet

- **Statement (Part A).** The run crosses ONCE: the run's `pspans` entry carries it in SET form
  as one D172 span (`mf_pred.nalt` 1, one `mf_wspan`: `start` 0, `len` n <= `MF_WSPAN_POS`, set per
  position, core all, verify NO), `nterm` 0 (the `MF_T_RUN` term retires), with `omin` its
  attempt-relative placement. ONE run FUNC part with no window of its own (the kit derives it);
  [K66]'s second whole-run part retires. No maxoff and nothing about consumption crosses.
- **Entry.** NEW pure `mf_run_decide(art, run_span, opts, &mf_run_reply)`; the reply is
  {`scan`, `ver_lo`, `ver_len`}, one decision over any position. Neither `mf_wdecide` (needs the
  run stated a second time as a window site) nor `mf_pres_ports` (reads `handoff`/`head_max`,
  decided after fact derivation) serves. The reply holds for every layer and target the art may
  render (stronger than plan_frame §2.3's OFF-only gap), because the earned skip relies on it.
- **Retired checks.** `req_run_member`'s internal error and `pres_layout_check`'s run half (its
  head/rest halves stay). Replacement controls with independent sources: C1 libpcre2 answers,
  C2 G2 text classification, C4 the artifact text against the stamp; C3 (purity) shares the
  function by design and is named so.
- **Part B.** `omin` may be negative on the run span only; the kit sets NO bound (int32 range),
  so pcrec's step-back bound is `lb_bytes`. `head_max` becomes `int64_t`, K = the assigned
  landmark's position-0 offset; the assigned value is the occurrence's position 0; none state
  unchanged. The twin admission reads `max(K, 0)`. Contract: floor `max(0, origin + omin)` with
  no wrap; no whole-run occurrence in `[floor, c)`; exact where verified; reads in `[0, n)`.
- **Numbers.** ONE `MF_SITE_ABI` event for A+B (agrees with the kit manager), `MF_CLASS_V` in the
  same commit (`mf_link.member` on the run span retires); pcrec abi only if a named mover lands.
- **Units.** K38-1 (M, one run decision, zero movers, no seam), K38-2 (L, the seam event with
  pcrec's same-commit hunks), K38-3 (S, the `enter` card's step-back cells and the below-zero
  guard-page population over U2's levels). K38-1 after 3.0a; K38-2 after 3.0b recommended
  (3.0b's ASK-2 is void either way). No new method; first general-set run position adds its
  `verify_set` card.

## What pcrec reads

- `scan` -> `<PREFIX>_REQ_RUN`'s `@idx`, `--emit-facts` `req_run`, `req_note_run`,
  `req_set_leads_own`, `req_pick_shadow` (replacing `ReqRun.idx` via `req_run_member`).
- `ver_lo`/`ver_len` -> the stamp's and listing's shown stretch (question 2), the earned skip
  (`ver_lo` 0, `ver_len` n, plus pcrec's own exact-whole-attempt fact), [MATCH-KNOWN] later.
- the assigned `c` (position 0) -> pcrec's move `max(posvar, c - K)`.
- `<PREFIX>_REQ_BYTE` reads NOTHING from the reply: pcrec's pick among consumed positions.
- `ReqRun.idx/at/bytes/len` retire with the cut; the fact-time call needs the Job's art from
  `src/facts/` (question 6).

## Open questions

1. K becomes the run's position-0 offset (no `at`): same moves, but `RX_REQ_HANDOFF`,
   `req_landmark_maxoff` and the margin admission move on cut runs. Recommend yes.
2. `<PREFIX>_REQ_RUN` shows the verified extent with `@scan` (recommend), not the whole run.
3. The run span states verify NO (YES forbids the kit's extent choice). Recommend confirm.
4. Parts A+B in one `MF_SITE_ABI` event. Recommend yes.
5. Accept the run-part block-name movers (one part instead of two) over a name-id convention.
6. The facts-side hook to the Job's art for the fact-time call (pcrec layering). Recommend a
   driver-set hook.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| Part A: one uncut span, sets at signed offsets, no consumption | sheet §2.1 |
| the kit's reply: scan + verify extent, one decision | sheet §2.2-§2.3 |
| the verified-extent fact (D187 add. 1 earned skip) | sheet §2.2, §3.3 item 3, §3.4 |
| the fact-time entry, existing vs new and why | sheet §2.2 (new `mf_run_decide`) |
| retiring `req_run_member`/`pres_layout_check`, replacement controls | sheet §2.4 |
| Part B: negative omin, signed K, twin admission, none state, step-back bound, clamp at 0, entry/re-entry contract | sheet §3.1-§3.3, §3.5 |
| field names, types, homes, MF_SITE_ABI events | sheet §2.1, §2.2, §3.2, §5.1 |
| kit build sketch with witnesses, sizes, measurement card | sheet §5, §5.2 |
| interactions with 3.0a/3.0b and U2 over-read | sheet §5 Order, §2.3, §3.3 item 4, W-K4 |
| open questions with recommendations | sheet §6 |
| standing questions | sheet §7 |
| CLAUDE.md line | docs/design/memfn/CLAUDE.md |
| REFERENCES.md | not needed: no paper cited |
| history-index line | docs/dev/history/claude_md/docs__dev__lanes.md |

## STATE AT HANDOFF

OWED: none (design lane; no runs queued).
Delivered and committed on lane/memfn-r38s. No rulings
file was named in the brief. Next: main rules §6's six questions; the kit manager reviews the
sheet (a readiness critic is the manager's call) before K38-1's brief.
