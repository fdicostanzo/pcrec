# FAITH critic — docfmt2
## Findings
Verdict for unit 1's control as written: **not ready** (FAITH-1, FAITH-2 and FAITH-3 let a wrong split through; the other findings are text fixes). Scripts and plants: faith/w/ (scan.py, control.py = a literal §5.2 (i)-(iii) over a toy file, plants.py, plants2.py).

### FAITH-1 — the open scan misses 13 bare-line markers, including D122 addendum 4, which sits inside D123 (CONFIRMED; answer; NEW in rev 2, the F1 fix's scan rule)
- §5.2's scan opens on `**`, `- **`, `##`, `###` only. decisions.md (build tree e9687de27, byte-identical to 6638e3679) has 13 markers that start the line with plain text: `D122 ADDENDUM` (8351), `D122 ADDENDUM 2/3` (8367, 8393), `D122 ADDENDUM 4` (8506, **inside D123's span**, cited by D123 at 8550/8560), and `D123 ADDENDUM`, 2, 3, 3a, 4, 5, 6, 7, 8 (8426-8572). Repro: `grep -n -E '^D12[23] ADDENDUM' docs/dev/decisions.md` gives 13 lines; faith/w/scan.py (the rule taken literally) finds none of them.
- What it does: none of the 13 gets a table row, so the converter leaves them as body text. D122.a4 stays inside D123. Controls (i)-(iii) PASS, because the census gives the control its owners, and the cite resolver agrees for the same reason. Only the D123-a3a witness can go red, and only because it happens to be named. A fix limited to D123 leaves D122.a4 under the wrong owner. Appendix A itself lists "D123 `ADDENDUM 3a`", so the appendix knows about markers its own scan rule cannot see.
- Fix (text): open the scan to any line, bare or after a list or bold prefix, with `addend` in the first 120 chars, all through the exclusion list; add D122 to the witness table (a1-a4, a4 out of D123). Effort: small. Blast radius: D122 and D123, 13 addenda.

### FAITH-2 — (ii) only checks rows against headings, so an invented or split addendum passes (CONFIRMED; answer; NEW)
- (ii) loops over owner-table rows. Nothing says every `### Dn.aN` heading in the details has a row. Heading lines are excluded from (iii), and C6 checks only position and rising order. Plants P17 (a made-up `### D2.a1` heading put into a body) and P17b (a real addendum split by a made-up `### D3.a3`) both PASS (faith/w/plants2.py). The same gap passes P18, an extra `(was: "...")` line carrying a false old label, and P19, a `rulings:` block written in unit 1. Both are excluded forms that add text nobody checks.
- Fix: make (ii) a bijection (heading set == table `new_id` set per owner); allow 0 `rulings:` blocks and 0 stray `(was:)` lines until 1.S, and exactly one `(was:)` per heading-form row. Effort: small.

### FAITH-3 — the per-owner multiset cannot see an owner's body versus its addenda, line order, or headings (CONFIRMED; answer; NEW)
Literal plants (faith/w/plants.py, plants2.py):
- P4, an addendum line moved into its owner's body: **PASSES**.
- P3b, non-first lines moved from D3.a2 to D3.a1: **PASSES**. P3 is CAUGHT only when the moved line is the hashed first line. A cite `D147 add. 3` would then land on the wrong text.
- P15, lines reordered within an entry: **PASSES**.
- P7, a fence dropped plus a fence duplicated in one owner (the code block breaks): **PASSES**. Repeated lines exist in only 5 of 191 entries today, so the risk is low.
- P14, a blank line dropped so two paragraphs merge: **PASSES** (non-blank lines only).
- P8 and P9, a body heading dropped or moved to another entry: **PASSES**. "Heading lines on both sides" excludes all 49 non-marker body headings, for example D30's `### 1. Resolution is by DECLARED RANK` (2313) and D31's `### 5. PURITY IS PER-DOORWAY` (2825).
- P10, an entry title rewritten: **PASSES**. P16, an addendum heading's date or title wrong: **PASSES**. No rule compares the "old text after the id, verbatim" with the original.
- Fix: run (iii) per ADDENDUM (each table row's old_line..old_end against its `### new_id` section) and per body, as ordered sequences, not multisets. Exclude only marker headings. Check `## ` text after the slug against the old heading (D98 joined). Effort: small to medium.

### FAITH-4 — `body_hash` has no meaning for 33 one-line addenda, and the "line after the label" is the next marker or entry (CONFIRMED; maintenance and answer; NEW)
- In 33 of 180 scan markers, the first non-blank line after the marker line is another marker or a `## `/`### ` heading. Examples: 9035 `D147 addendum 4` is followed by the a5 marker; 9006 is followed by `## D147`; 9350 `Addendum 4.1` is followed by `### D155 addendum 5`; and D151 a1-a7 run one after another (9226-9238). Given the §B definition, (ii) either goes falsely red, because the details put a different heading there, or hashes text outside the addendum. A converter author facing that red will bend the definition, which puts the control on the converter's side. Fix: hash the label line itself (inline) or the addendum's whole extent.

### FAITH-5 — appendix A's 148 does not match the scan as written: 195 hits = 180 markers + 15 non-markers (CONFIRMED; doc; NEW)
- faith/w/scan.py on the build tree: 195 lines. 180 are markers: 70 `### Dn addendum`, 1 `### D31 ADDENDUM`, 7 `## Dn ADDENDUM`/`SECOND`, 54 `**Dn addendum`, 8 `**Dn ADDENDUM`, 15 `**Addendum`, 6 `**ADDENDUM`, 17 `- **Addendum`, 2 RULING-5. 15 are cites or prose that the exclusion list must name: 3804, 9056, 9058, 9126, 9132, 9156, 9158, 9349, 9445, 9494, 9506, 9691, 9728, 10091, 10115. Adding FAITH-1's 13 gives 193 markers. The appendix's own spelling counts add up to more than 148 as well. The appendix says no hand-typed census again, but 148 is one. Fix: drop the number or mark it superseded by the table's row count.

### FAITH-6 — old_label is cut at 160 chars, and 20 heading-form markers are longer (CONFIRMED; answer, small; NEW)
- (ii) wants the `(was:)` text to equal `old_label`, which §B cuts at 160 chars. The marker heading line itself is excluded from (iii). So for the 20 heading markers over 160 chars (4208, 4256, 5641, 7799, 9345, 9352, 9468, 9502, 9508, 9519, 9528, 9547, 9566, 9647, 9677, 9682, 9745, 9801, 9820, 9839 with 251 chars), either a full `(was:)` goes falsely red, or a cut one loses the tail and nothing checks it. Fix: keep the full label; cut only for display.

### FAITH-7 — D98's heading wraps onto TWO continuation lines, not one (CONFIRMED; doc; F17 text)
- The heading runs over decisions.md:6886-6888. Appendix A says "wraps onto a second line". An exclusion or join written from that text handles one line and goes red, or leaves line 6888 as body. A join applied to some other heading is CAUGHT by (iii) (P11), as long as the exclusion names D98 alone. Fix: say "two continuation lines" and scope the exclusion to D98 only.

## PROBED-AND-HELD
- Plants CAUGHT by the literal (i)-(iii) (faith/w/control.py, toy original plus a correct conversion; the baseline PASSES clean):
  - P1, an addendum under the wrong owner when the table is right: (ii) heading check plus (iii).
  - P2, a body line moved between entries: (iii).
  - P3, the first line of an addendum moved: the (ii) hash.
  - P5, a line dropped; P6, a line duplicated: (iii).
  - P11, the D98 join applied to another heading: (iii).
  - P12 and P13, an original body line rewritten into the `(was:)` or `rulings:` form: (iii) goes red, because the original side still counts the line.
- The exclusion set swallowing content: decisions.md has 0 lines opening `(was:` and 0 opening `rulings:`. 4 lines open `Ruling:`/`RULING:`/`ruling:` (3948, 4574, 4990, 6429); they are safe only if the match is exact-case `rulings:`. Swallowing in either direction gives a red, never a pass. Adding text in an excluded form is the gap (FAITH-2).
- Spellings outside the scan prefixes besides FAITH-1: 0 indented list-item markers, 0 bold markers in the middle of a line, 0 numbered-list markers. No addend marker in a prefix-form line falls past char 120 (the late hits are cites). `add.` occurs only in cites (5016's `D168 add. 1`, 9534's `add. 11`), and `Addenda` only in prose (3555, 8503). Non-addendum amendments (CORRECTION ×~10, POSTSCRIPT ×2, `- **Note (Frank, 2026-10-21...)` 9873, `- **Correction (kit...)` 9526) stay where they are in the text; each one checked sits inside its own entry or an addendum's extent.
- The "already converted" test: 0 old headings match `^## Dn (<slug>|-) — `, and 0 decisions lines open `- Dn `. It holds.
- The witnesses: every appendix B witness is a named check on the converter's output, so each can fail when the converter departs from the table. D123-a3a FAILS today on a scan implemented literally, which is how the D123 half of FAITH-1 would surface. None of them can catch a WRONG TABLE ROW: the BEFORE side of the resolver reads the table too, so it shares a source with the control. That is by design (the census has an independent author), and the cost is FAITH-1's D122.a4.
- The build tree's decisions.md is byte-identical to 6638e3679's (diff empty), so the census numbers are comparable.
