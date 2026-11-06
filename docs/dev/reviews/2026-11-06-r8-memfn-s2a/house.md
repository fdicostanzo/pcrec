# house — memfn-s2a
## Findings
(line numbers at SUBJECT f8c513ec8; all maintenance unless marked; none changes behaviour today)

HOUSE-1 [maintenance, medium effort] Per-format choice is an inline `set->format == 2` ternary/if at 7 sites, not one declared row.
 src/core/ks_measures.c:274 (digest role), :280 (cell width), :286 (cell column list), :342 (format parse, a second
 strcmp pair at :340 decides validity then `[0]=='2'?2:1` re-decides), :432 (noise_load gate), :567 (events check),
 :727 (noise_parsed view field). Fits one `static const struct {int format; const KsDigest *role; const char *const *cell_cols;
 size_t ncell; bool noise;} meas_formats[]` first-match/indexed table; :340-342 would then validate AND set format from the
 same row (a format 3 = one row). Python repeats it: tests/knowledge/ks_ref.py `two` / `doc["format"]=="2"` in digest, handed, decode, load
 (CELL vs CELL2 chosen at load AND decode). Third family member = per-format digest ROLE: kind row .item/.stamp
 (ks_measures.c:803-804) still names the format-1 role while pcrec_ks_meas_digest picks per set (h:151-153 admits it). No
 reader of kind->stamp/item for measures today (grep), so latent only; a future generic reader digests a format-2 set with
 the wrong role and no test would see it. Either make the kind row's role a function of the set or add a trap comment/check.

HOUSE-2 [maintenance, small] Second FNV-1a and second canonical sort in the trace path.
 src/gen/memfn_sites.c:124-130 `meas_fnv` re-implements core/ksrc.c:520 `pcrec_ks_fnv1a`, and :164 hard-codes
 0xcbf29ce484222325 where `pcrec_ks_fnv_basis` (ksrc.h:302) exists. libpcrec links both, memfn_sites.c may include core/ksrc.h;
 call `pcrec_ks_fnv1a(h, part[k], strlen(part[k]))`. :133-136 `meas_key_cmp` + qsort (:168) is a second canonical sort: rows
 come from the loader already in key order (load_rows qsort, ks_measures.c:434) and memfn_measures (:85-96) filters in order,
 so the sort is redundant unless handed rows can arrive unsorted (art_begin callers other than memfn_measures: none in pcrec) -
 if the intent is "sort what the KIT was handed", say so in the comment; otherwise delete it plus the arena alloc.
 (ks_ref.py handed() deliberately re-implements: independence, fine.)

HOUSE-3 [maintenance, small] Sentinel vs state: pcrec derives the kit's state from a sentinel.
 memfn_sites.c:92 `measured = r->noise_e6 != KS_MEAS_EMPTY`. memfn.h:1233-1239 says "a state, never a sentinel, because a measured
 noise may round to 0"; pcrec's own KsMeasRow keeps INT64_MIN as the sentinel for both value_e6 and noise_e6 (ks_measures.h:78-82), and
 meas_record maps state->name with a nested ternary (:160-162, "unstated" fallback) that is a 3-row table. Correct today (noise
 is validated >=0 so it never equals INT64_MIN), but a format-2 `-` and a format-1 row are indistinguishable from "measured
 nowhere" only through that sentinel; a state byte on KsMeasRow (or reuse of one helper `noise_state_of(row)`) would be the
 same fact in one place. Not behaviour-changing.

HOUSE-4 [maintenance, small] Magic digest buffer sizes and dead work. ks_measures.c:236-243: `unsigned char b[18]`, `noise ? 18 : 10`,
 b[2+k]/b[10+k] offsets are bare numbers; format 1 still computes `nz` and fills b[10..17] it never hashes. Name the two
 widths (enum: ROW_V1 = 10, ROW_V2 = ROW_V1 + 8) and compute `n = noise ? ... : ...`. `bool noise` flag + two wrapper
 folds (meas_fold/meas_fold2, both `(void)subkey`) is acceptable but is the 4th place the format is chosen (see HOUSE-1).

HOUSE-5 [maintenance, small] Altitude: check_rows (ks_measures.c:~466-590) grew an anonymous `{ ... }` block (:559-572) mixing
 duplicate-cell-id (O(n^2)) and format-2 events validation, with a local `e` and `w`. Extract `check_cells(set, where, err)`;
 the duplicate-id loop and the events rule are unrelated rules sharing a loop only for the index.

HOUSE-6 [maintenance, small] Duplicate helpers in tests/knowledge/mfixtures.py: `edit_rows` (:233) is a third copy of the
 "find row by key, set column" loop beside bad_sets' `rowfix` (:287) and f2_bad_sets' inner `cell` (:251, same loop over the
 `cells` section keyed by cell id). One `edit_section(text, section, key, col, v)` serves all three. Also `if name.startswith("f2-")`
 (:365) is a name-prefix used as a flag: have f2_bad_sets return a 4th tuple field `redigest`.

HOUSE-7 [maintenance, small] scripts/ksgen.c:355-361: two copies of "EMPTY ? emit macro : emit %lldLL" (value_e6, noise_e6); a
 `put_i64(out, v)` helper removes both. Also the empty-rows literal `{ { 0 }, 0, 0, 0, 0 }` (:362) must track KsMeasRow's field
 count by hand (ks_measures.h says "Appended last: ksgen writes the pre-parse positionally"); `{ { 0 } }` is the form
 that cannot drift, and the positional emit of rows is the real hazard (meas_store_check's raw compare covers it - good).

HOUSE-8 [maintenance, small] tests/knowledge/meas_store_check.c: two `check_all` variants under #ifdef MSC_TABLE (:158-:196 region)
 plus `(void)pcrec_meas_defaults;` to silence an unused symbol; `static char buf[1<<20]` fread with no short/oversize check
 (a set over 1 MiB would be truncated and fail confusingly as "does not parse"). raw_same prints `header %d differs` by index, not by
 KS_MEAS_HEADER name. Include `"../../memfn/include/memfn.h"` follows src/dump/axes_dump.c:90 precedent (held).

HOUSE-9 [maintenance, tiny] compose.c measures_check noise block: if / else-if / else on noise_state is a switch with
 `case`s (one unknown-state message already covers default); unify the three messages' shape. mf_measure.noise_state is
 `uint8_t` documented as mf_noise_state: the enum-in-a-byte is intentional for layout, comment says so only by "(appended LAST)".

HOUSE-10 [doc, tiny] ks_measures.h:151-153 comment "The kind row names the format-1 role" is accurate but is documentation of
 the HOUSE-1 trap rather than a guard. main.c comment on harness_measures_load ("reads no `format`") is accurate: it hand-parses
 TSV columns and now hardcodes UNMEASURED - correct for format-2 sets it would silently drop noise, as claimed.

## PROBED-AND-HELD
- ksrc dependency rule: ks_measures.c includes only libc + core/ks_measures.h + core/ksrc.h (grep, 7 include lines); KS_MEAS_MAX is a
  second home of 10^15 as the rule forces, with a _Static_assert equality in meas_store_check.c:40 - held.
- Comment-vs-code checks: meas_fold_rows, noise_load (three rules in comment = three branches), meas_record trace-field list (7 columns,
  `-`/`-` for NULL set), memfn.h noise comment (refuses UNSTATED, MEASURED outside 0..MAX, UNMEASURED !=0) vs compose.c:902-910 - all match.
- compose.c refusal cases vs g2_gen.c table: 8 rows (5 refused, 3 accepted) consistent with the code.
- ks_ref.py digest layout matches C (domain, class+NUL, key+NUL, unit, status, value LE, noise LE): by inspection.
- Names (D174): noise_state/noise_e6/KS_MEAS_EMPTY/pcrec_ks_meas_cell_w describe what the caller sees; no kit/proof names leaked.
