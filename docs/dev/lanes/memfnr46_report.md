# memfnr46 — integration.md rev 4.6: the r5 panel applied

Lane `memfnr46`, kit session, 2026-10-05. Branch `lane/memfnr46`, cut from
`lane/memfn-r45` at df041954. Serves request R-2 (`memfn/docs/requests.md`)
after its panel. Charter: `docs/dev/reviews/2026-10-05-r5-memfn-rev45.md`
(23 findings, all ACCEPTED). DESIGN DOC ONLY: no code, no `make`, no
emitted byte moves. Rules nothing; Q53-Q55 stay OPEN.

## Files changed

- `docs/design/memfn/integration.md`: rev 4.6. New header block, new
  top-level §R4.6 (above §R4.5), `[rev4.6]` marks in place.
- `docs/design/memfn/probes/twins/gates_sync.sh`: comments only (check
  (4) scoped to DFA routes). No logic change.
- `docs/design/memfn/probes/twins/tb_r4b.c`: comments only (the lead's
  need per route; the `nosl` "three lines" scoped to DFA routes; one
  mislabel fixed, see "Found" below).
- `memfn/CLAUDE.md`: rev line → rev 4.6, read §R4.6 then §R4.5 (B10).
- `docs/design/memfn/CLAUDE.md`: rev 4.6 entry (B10).
- `docs/dev/lanes/CLAUDE.md`: this report's entry.
- NOT touched: `memfn/docs/wake.md` (the kit session's, at its pause).

## By id: each finding and the passages changed

| id | passages changed |
|---|---|
| A1 | §14.0 `mf_pred.need` comment; §14.3 ALL_PRESENT paragraph (inline qualifier + `[rev4.6]` note); §14.5 ("lead excepted" deleted; OPTIONAL list qualified; new block "The lead's need is PER ROUTE" with the emitter facts, witness and pins); §14.10 bit 45 row; §15.3 `pred` row; §15.5 part 0 row, `[rev4.6]` note on "Bit 45 still removes part 0", new item 6 (run-first obligation); §19 row 5; §R4.5.1 item 1 (new bullet); §R4.5.5 item 3; §22 R4d; `gates_sync.sh` header (4) and check-(4) comment; `tb_r4b.c` composite-site comment and `nosl_cn` comment |
| A2 | §14.0 `use` comment; §14.5 `[rev4.6]` block after the `use` paragraph (per-instance from `req_use(cx)`, ceiling, C10 per instance); §17.6 `[rev4.6]` block (row reworded); §22 R4c |
| A3 | §14.9 item 1; §19 row 3; §22 R4d (spec-hunk bullet); §R4.3.5 note; Q55 |
| A4 | §16 new item 4; §22 R4c |
| A5 | §14.3 note; §14.4 new `[rev4.6]` block; §15.4 `empty` row; §15.5 numbering block |
| A6 | §14.0 `ret_pred` comment; §14.2 note after `note_tag`; §15.4 `note` row; §15.5 numbering block and item 4 |
| A7 | §15.5 new "On the VM hybrid route" paragraph (witness OWED at R4c); §22 R4c |
| A8 | §14 head (sources list rewritten to function names, plus a `[rev4.6]` note); every former `file:line` in §14.1, §14.2, §14.3, §14.4, §14.5, §14.7, §14.8, §14.10, §15.1-§15.7, §16 now names a function, struct or table. The 9 → 3 memchr count kept, its six and three sites named by function |
| A9 | §15.1: two `[rev4.6]` notes (locals `ha`, `hb`, `fresh`; deny literals `-fno-req-run-fold`, `-fno-req-byte`; the one/two memchr stream wording as frozen form text) |
| A10 | §15.5 item 7; §22 R4d |
| A11 | §14.2 sink bullet (`emit_comment_safe_byte` is stateful; no kit comment uses it at M1) |
| A12 | §15.7 new PF byte-class bullet |
| B1 | §R4.3.5 `[rev4.6]` note; Q55 |
| B2 | §R4.4.1 new block (bench attributes by build recipe; `<PREFIX>_MEMFN_OPTS` filed); §R4.3.5; §22 R4a′ bullet and "Filed, not scheduled"; Q55 |
| B3 | §10.5 `[rev4.6]` note; §17.6 block; §18.2; §21.2 C11 row; §22 R4d; Q55 |
| B4 | §R4.3.3 refined-form block (proposed, Q53 open); §10.5 note; §17.6 two new rows (`memcmp`, `memcpy`); §21.2 libc row; Q53 |
| B5 | §R4.3.3 refined-form block; §22 R4a′ bullet; Q53 |
| B6 | §R4.3.4 (definition widened, cite corrected, C17 item 1 scope); §8.5 N7 row; §22 M7; Q54 |
| B7 | §22 R4a′ trigger |
| B8 | §R4.3.3 "Its event" (the `[rev4.5]` sentence with the literal replaced, marked `[rev4.5]`, corrected `[rev4.6]`); §22 R4a′ abi bullet |
| B9 | §16 `[rev4.5]` note gains a `[rev4.6]` pointer to §R4.5.5 item 1 as the one authority |
| B10 | `memfn/CLAUDE.md`; `docs/design/memfn/CLAUDE.md` |
| B11 | §R4.3.5 note; Q55 |
| Q53-Q55 | §23: each question's text replaced by the review's refined form and recommendation, with a short `[rev4.6]` note saying what rev 4.3 asked. All three remain OPEN. A `[rev4.6]` line heads §23's question lists |

23 of 23 placed; §R4.6.0 carries the same table as the in-document
completeness check.

## Verified by this lane (read-only, `build/pcrec` of main at abi 61)

- A1 emitter facts, read in `src/gen/emit_dfa.c`: `emit_req_set_rest`
  returns at once when `pcrec_artifact_has_dfa_scan`, and otherwise sets
  `done[req_lead_byte(cx)]`; `req_set_leads_applies` has no DFA-route
  conjunct.
- A1 witness reproduced: `--features all -p rx --pattern
  '(x?)([a-z]+)+Z.user\1'` → `RX_ENGINE "vm"`, `RX_VM_PREFILTER "none"`,
  lead `memchr(…, 90, …)`, no `rq_set`; `-fno-req-set-lead` removes the
  three lead lines and adds `rq_set[] = { 90 }`.
- union-select (`(?i)union.*?select.*?from`) is `RX_ENGINE "dfa"`,
  `RX_REQ_HANDOFF "none"`: a DFA-route site, as the review states.
- A7: `req_handoff_applies` and `vm_emit_search_body`'s
  `pcrec_emit_req_run_blocks` / `pcrec_emit_req_byte_check` / `first`
  read as stated. No witness artifact searched for (owed at R4c).
- A9, A11, A12 texts read in `emit_dfa.c` as cited.
- A8: every function name cited was mapped from the `1c2ba975` line
  (`git show 1c2ba975:src/gen/…`) and checked to exist at the branch base.

## Found, and questions for the kit session

1. **`tb_r4b.c` mislabelled union-select's lead column "none (no-DFA
   route)".** The artifact is DFA-route (above). I changed the label to
   "none (no handoff)", comment only. Flagging in case the original
   meant something I missed.
2. **A4's census.** The review names S185 … S472 from critic A's
   count of "about 28". My own quick anchor-to-function pass (first
   line of `SAB_BEFORE` located in today's `emit_dfa.c`) found 19
   unambiguous rows plus one ambiguous anchor (S264); it did not place
   S267, S293, S448 (multi-line or non-unique first lines). It also
   found **S470** (`emit_req_handoff`'s clamp), which the review does
   not name; the doc now lists it pcrec-side with S463/S471/S472. The
   exact count is stated as the REPLACE commit's job. No ruling needed.
3. **Earlier-revision text vs "rewrite".** Three places replace text
   rather than annotate, on the brief's instruction: (a) Q53-Q55's
   bodies (each keeps a `[rev4.6]` note summarising rev 4.3's wording);
   (b) §R4.3.3's `[rev4.5]` sentence carrying the literal (B8); (c) the
   §14-§16 line citations (A8; one `[rev4.6]` note at §14's head covers
   them). Everything else is annotated in place.
4. **Not converted (out of A8's scope):** 36 `file:NNNN` citations
   remain outside §14-§16 (§R4.3.1's `axes.def` lines, §8.5, §19, §20.2
   and the history sections). §19 row 5 still cites `emit_dfa.c:6601`
   beside my `[rev4.6]` text. Say if A8 should extend to §19.
5. **B4/B5 placement.** The libc record's refined form is written as
   Q53's PROPOSAL (§R4.3.3 block, §17.6 rows "spelling waits on Q53"),
   not as design of record, since Q53 is open. The `memcpy` sabotage
   row is declared UNREACHED if the corpus has no non-constant-length
   `memcpy`, which I expect today (the `rx_wN` loads are constant-size,
   excluded).
6. **B6 conditionality.** The D23 → D58/DD-12 cite fix and the widened
   definition are unconditional. C17's `src/enc/` scope and M7's
   `MF_VOCAB` bump are written "should Q54 rule yes".

Nothing contradicted a ruling.

## Final grep pass (run on the committed tree)

```
F=docs/design/memfn/integration.md
grep -c "lead excepted" $F
```
→ **1**: line 143, §R4.6.0's A1 row quoting the deleted phrase. No live
occurrence.

```
grep -n -i "optional" $F | grep -i "lead" | wc -l
```
→ **13**. Every one is route-qualified on its own line or the next, or is
§R4.6/`[rev4.6]` text describing the fix (lines 126, 143, 171, 4115,
4290, 4294, 4389, 4392, 4413, 4623, 4779, 4866, 5524). A filter for
lines lacking "DFA-scan"/"no-DFA"/"per route"/"rev4.6" returns 5, each
qualified on the adjacent line (126 heading prose, 4115 code comment
continued on 4116, 4389/4392/4413 inside the §14.5 per-route block).

```
grep -n -E "\b62\b" $F
```
→ **2**: lines 359-360, §R4.5.2's table (revision 4.5's record of what
it changed; history). No live literal.

```
grep -c -E "abi 6[0-9]" $F
```
→ **11**, all provenance (what a reading was taken at: abi 60/61), none
an R4a′ number.

```
S14=$(grep -n "^## 14\. " $F | cut -d: -f1); S17=$(grep -n "^## 17\. " $F | cut -d: -f1)
awk -v a=$S14 -v b=$S17 'NR>=a && NR<b' $F | grep -c -E ':[0-9]{2,5}'
```
→ **0** in §14-§16 (lines 4048..5166).

```
grep -c -E '\.(c|sh|def|h):[0-9]{2,5}' $F
```
→ **36** in the whole document, all outside §14-§16 (item 4 above).

## Validation

Design-only: no build, no suite. The probe edits are comment-only
(`gates_sync.sh` logic and its fail message unchanged; `tb_r4b.c` code
unchanged). No digest pins `tb_r4b.c` (grep of `docs/` and `tests/` for
a sha over it: none).

## Resume point

If a follow-up round is needed, start from §R4.6.0 (the by-id table) and
item 2-4 above. The design questions are Q53-Q55, unchanged in number,
refined in text.
