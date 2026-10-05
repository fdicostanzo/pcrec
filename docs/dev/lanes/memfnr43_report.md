# memfnr43: integration.md revision 4.3, Frank's 2026-10-05 rulings folded

Lane memfnr43, 2026-10-05, opus, docs only. Branch `lane/memfnr43`
from main 7f94b0cd. Inputs: D146, D147 and D147 addenda 1-7
(`docs/dev/decisions.md`), and integration.md rev 4.2.

## Delivered

1. **integration.md rev 4.3.** A header block at the top, and a new
   top-level §R4.3 (read first) before §L:
   - **R4.3.0:** each ruling mapped to where it now lives.
   - **R4.3.1, the ONE SIMD switch** (addenda 6-7, Q38, Q50). OFF is
     portable C; ON is hardware-optimized and may not run elsewhere;
     what ON contains is the kit's per-site choice. It is default OFF,
     and the flip is a ruled event.
     - **Spelling chosen:** axis `memfn-simd`, a deny/force pair
       `-fno-memfn-simd` / `-fmemfn-simd`, `PCREC_AXIS_DEFAULT_OFF`.
       That is D112's `-fcomments` shape: a capability that ships OFF
       is enabled by `-fX`, born a pair, and R4f changes only
       `default_state`.
     - The policy bit `MF_P_PORTABLE_ONLY` is kept, because its name is
       the ruled meaning.
     - A spelling table maps every old `native`/`portable`/`baseline`/
       `memfn-native` spelling. R4i (`--isa=`) is withdrawn as a pcrec
       axis (addendum 6: a level is a kit form question).
   - **R4.3.2, cascading levels** (addendum 2): SIMD-on only; kit charter
     item K-6 added to §8.6.
   - **R4.3.3, the stamp:** Q39 as ruled, plus addendum 6's libc
     record.
     - `MEMFN_FORMS` is `none` iff identical to the `-fno-memfn-simd`
       compile, else the forms used (every delegated site's id, with
       carried levels `ID@L+L`).
     - New sibling line `<PREFIX>_MEMFN_LIBC`. Both lines are born in
       R4a′.
   - **R4.3.4, completeness** (Q42 reversed). Every search site
     migrates, N6, N7 and the strided VM span included (M6/M7 added).
     - **C17, the checked site manifest**
       (`tests/memfn/site_manifest.tsv`, born at R4a with every row
       `pending`). It has a static half (C12's vocabulary) and a dynamic
       half (`mf_emit_site` census). Its limit is stated: a search
       spelled outside the vocabulary escapes the static half.
     - The ratchet's end state is 0. Migration steps trigger on
       completeness; MOVER steps keep measured triggers.
   - **R4.3.5:** Q40 as M5 (live planner, zero movers) plus M5′ (the
     ruled adoption event).
   - **R4.3.6:** Q51/Q52 rejected, and what stands.
   - **R4.3.7:** the conflict table.
2. **In-place `[rev4.3]` annotations** (41 marks): §L.1, §L.5, §8.5
   (new two-row switch table), §8.6 (K-6), §9.4, §9.5, §10.5 (C17
   defined), §10.6, §14.10, §15.7, §16, §17.2, §17.3, §17.6 (three
   sabotage rows), §18.1, §19, §20.2, §21.2 (two control rows), §21.3,
   **§22** (a full rev 4.3 build order at its head) and **§23**:
   - a status table;
   - RULED/REJECTED marks on Q37-Q42 and Q50-Q52;
   - Q43, Q46 and Q49 re-spelled;
   - **Q53-Q55 new**;
   - no ruled question renumbered.
3. **option_sets.md:** a rev 4.3 cross-note (family `memfn` over
   `memfn-simd`; the `isa` token axis withdrawn).
4. **memfn/:**
   - `CLAUDE.md`: the switch, completeness, the stamps, and the boundary
     table rows;
   - `README.md`: the one-switch paragraph;
   - `src/`/`tests/` CLAUDE.md: SIMD forms, K-6, C17;
   - `docs/wake.md`: read §R4.3 first;
   - `docs/journal.md`: an entry.
5. **docs/design/CLAUDE.md and docs/design/memfn/CLAUDE.md:** rev 4.3
   entries.

## Judgement calls for the manager (check these)

- **Q51's rejection, my reading** (§R4.3.6; also sent to main
  mid-lane). The SIMD-off arm (`-fno-memfn-simd`) is kept as a
  permanent arm. The frozen-baseline bits (`-fno-memfn-scan/-loop`,
  `memfn-off`, `off.tsv`) STAY withdrawn, because D147 consequence 1
  retires a frozen baseline independently of Q51. If Frank meant those
  bits to return, the fix is §R4.3.6 plus §20.2's two rows.
- **"The forms used"** (addendum 3) is read literally: when not
  `none`, every delegated site's id is listed, scalar ones included.
  Rev 4.2's Q52 had listed only native ids.
- **The libc record as a second line** (Q53), covering pending sites
  through `mf_art_note_libc`, so it is true from R4a′.
- **N7 counted as a search site** (Q54). The alternative is a third
  manifest state, which addendum 5's reasoning argues against.
- **The addendum 3 / addendum 4 tension** (Q55): a SIMD-off plan change
  reads `MEMFN_FORMS "none"`.
- **R4i / the `isa` token axis are withdrawn** by addendum 6's "kit
  form question, not a pcrec profile".
- **The axis lands at R4c**, inert until R4e′, as rev 4.2 had it. Both
  readings are reported from the first.

## Owed to others (not this lane's to write)

- `memfn/docs/requests.md` R-1 still says its SIMD-off reading is
  "R4c's trigger". Under rev 4.3 it is R4d's (M1 triggers on
  completeness). The manager is the only writer of that file.
- `docs/dev/plan.md`'s [MEMFN] row has no rev 4.3 note yet.
- K85's re-measure and the handoff's Linux alpha are still owed. They
  gate R4c and R4b.

## Validation

Docs only: nothing under `src/`, `cli/`, `lib/` or `tests/` changed, so
no build or suite applies. All `[rev4.3]` anchors were inserted by
exact-match edits (each asserted unique). The question order Q35-Q55
was checked by grep. Validation is COMPLETE; nothing is owed.
