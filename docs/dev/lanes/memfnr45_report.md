# Lane memfnr45: integration.md revision 4.5 (memfn R-2 item 1)

Design only. No code, no make, no byte moves. Rules nothing: Q53-Q55 stay open.
File: `docs/design/memfn/integration.md`.

## 1. Passages changed (section, what)

- Title block: REVISION 4.5 paragraph added above 4.4.
- New top-level section R4.5, above R4.4: R4.5.0 (input table), R4.5.1 (what changed), R4.5.2 (every changed passage), R4.5.3 (spellings chosen), R4.5.4 (the three standing questions).
- Section 8.6: K-7 added (D149), with the `swar` 2x unroll as the first labelled default.
- Section R4.3.3, "Its event": abi note (61 is the handoff's at f116cff5; 62 if nothing lands first; never a literal).
- Section 15.5: correction note after "Why ONE site", plus a new subsection "The lead order and the regime boundary" (lead order as the kit's per-site choice, default lead first; the future "lead can reject" fact, not built; the 0.18 ns/B boundary with mod-i gate 1m and cls-n-uc gate numbers; handoff contract unchanged; D149).
- Section 16: `[rev4.5]` note after the rev 4.3 status block (K85 re-measure and handoff alpha reads exist: k82halpha_report.md §3).
- Section R4.3.7 table row for section 16: annotated.
- Section 19 row 5: lead order is the kit's choice.
- Section 21.1, R4b bullet: marked measured, with the regime flips named.
- Section 22: head note; rev 4.3 block rows R4a′ (abi), R4b (DONE), R4d (trigger MET, lead order, D149), R4e′ (16 B note); "Filed, not scheduled" gains the density fact; the rev 4 R4d line ("K85's general answer") annotated as history; "Status is at main 7f94b0cd" annotated.
- Section R4.4.0, Q48 row: annotated.
- `docs/design/memfn/CLAUDE.md`: integration.md entry bumped to rev 4.5.
- `memfn/CLAUDE.md`: one line under "The layers" (kit forms obey D149).
- `docs/dev/lanes/CLAUDE.md`: this report listed.

Earlier revisions' text was annotated, not rewritten.

## 2. Contradictions found and NOT resolved (for the kit session)

1. **Wait 2 and the handoff alpha.** Sections 16, 22 (rev 4.3 block R4b/R4c rows) say K85's re-measure and the handoff's Linux alpha are OWED. `k82halpha_report.md` exists and reads both (K85 persists, +0.023..+0.036 ns/B, new vs deny). I annotated the pointer but did not declare the waits MET or R4c's prerequisite satisfied. That is a manager reading.
2. **Q48's trigger.** It is "a K85-shaped cell the R4d fused arm does not cure". R-1 found the single early-hit gate call on dense text still loses at SIMD-off. Whether that is the Q48 cell (and so whether optional sites get a trigger) is not decided here.
3. **Lead order and the registry.** Whether lead order is a separate form needing its own `--memfn=no-NAME` row, or part of R4d's one form, is open. R4.5.3 item 3 says "a row is born if separate".
4. **Rev 3 and rev 4 "delivered" blocks in section 23 and the plan-row text** still describe R4b as pending. Only the section 22 head note covers them. Not rewritten, by the history rule.

## 3. Checklist of inputs against committed passages

- [x] Input 1, lead order in 15.5, default lead first, userpass evidence, future fact named and not built (D77), regime boundary with 0.18 ns/B, mod-i gate 1m +2.4 ns, cls-n-uc gate 64k/256k: 15.5 subsection; R4.5.1 items 1-2.
- [x] Section 22 R4b DONE with refs (08caf4a3, 348c0a49, `R4B-DONE status=0`); R4d trigger MET on union-select, 1.4-2.0x, form carries lead order: 22 R4b and R4d.
- [x] R4e′ 16 B note (+0.36/+0.64 ns): 22 R4e′; R4.5.1 item 6.
- [x] K85 (greps for "K85" read; fixed 15.5, 16, 19, 21.1, 22, Q48 row, rev 4 R4d line).
- [x] Section 21.1 marked measured.
- [x] Input 2, D149 in 8.6 (K-7), 22 R4d, first label recorded (`tb_r4b.c`), `memfn/CLAUDE.md` line.
- [x] Input 3, abi staleness: R4.3.3 and 22 R4a′ with `[rev4.5]`; "never a literal" kept.
- [x] Grep for other contradictions: items above; unresolved ones in section 2.
- [x] Every changed passage in R4.5.2's table.
- [x] `docs/design/memfn/CLAUDE.md` bumped; lanes `CLAUDE.md` entry in the same change.
- [x] Header/status lines: rev 4.5 current, Q53-Q55 open, rules nothing.
