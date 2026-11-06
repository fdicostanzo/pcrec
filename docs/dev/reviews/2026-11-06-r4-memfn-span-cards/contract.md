# CONTRACT findings

Lens: every caller-observable contract span_cards.md rev 0 moves, its readers, and the pcrec->kit seam
round trip. Code cites are at the build tree worktrees/crit-memfn-span-cards (= main fb22c62a6).

## Findings

### CONTRACT-1 — finder_check.py is a format-1-only digest reader of EVERY file in memfn/data/sets/, and §3.8 puts a FORMAT-2 set there; the design lists it "UNCHANGED"
CONFIRMED (text + code). Severity: maintenance (a red `make test` at S2e, or a silently skipped check if
"fixed" by excluding the file). Effort: small. Blast radius: the kit's check C over all interim sets.
- §3.8 step 1: "`read.py` writes the kit's interim set `memfn/data/sets/kit-interim-grid3.tsv` (FORMAT 2, §5)".
- §5: "`memfn/data/sets/generate.py:79` and `tests/memfn/finder_check.py:320` (the kit's synthetic sets stay
  format 1: UNCHANGED)".
- tests/memfn/finder_check.py:343-374: `for fn in sorted(os.listdir(sdir))` over every `.tsv` in
  memfn/data/sets, then `hdr.get("values_digest") == digest(rows)` where `digest()` (:313-324) feeds
  `b"pcrec-meas-1\0"` and no noise. A format-2 file there fails "values_digest X, recomputed Y".
  It also runs `ks_ref.py digest` (:376) and `pcrec --list-measurements` (:381) on it — those the design does move.
- Fix: list finder_check.py's `digest()` as a format-dispatching reader (or keep the format-2 interim out of
  memfn/data/sets/), and add a sabotage row: format-2 interim checked with the format-1 rule.

### CONTRACT-2 — "noise reaches the kit ONLY from a set whose digest covers it" is not enforceable on the two test paths the design says "follow the same rule"
CONFIRMED (code). Severity: design (the claim is the stated close of the no-shadowing hole, §4.2/§0 row 3).
Effort: small (state the rule per path). Blast radius: row 1's witnesses, which drive kit rows through
these paths.
- `cli/main.c:93-175` (`--harness=measures=FILE`): copies `values_digest` from the header VERBATIM (:139),
  never recomputes or checks it, and reads no `format` key (its `want[]` is key/value/unit/value_e6/status/
  source, :131). Any noise it hands is covered by no checked digest, whatever the format.
- `tests/memfn/arm_fixtures.c:1527-1567` (`fd_load_set`): reads ONLY the rows section (key, value_e6);
  `ms->id = path`, `values_digest` NULL (memset), no header, no status (a `null`-status row with a value
  would be handed). There is no digest at all to cover anything.
- §4.2: "The harness reader (`cli/main.c`) and `arm_fixtures.c` follow the same rule." Under that text both
  would hand format-2 noise as MEASURED from an unverified file. Also nothing crossing the seam tells the
  kit the format or digest domain (`mf_measures` has no format field, memfn.h:1232-1241), so the kit
  cannot check the claim either: it is a pcrec-only invariant of the shipped loader path
  (`memfn_sites.c` `memfn_measures`) alone.
- Fix: restate the claim as "on the shipped path"; for the two harness paths say explicitly what they do
  (e.g. harness: hand noise only from a file `pcrec_ks_meas_parse` accepted — reuse the loader instead of a
  second parser; arm_fixtures: UNMEASURED always, or a `--fd-noise` lever that is named as unverified).

### CONTRACT-3 — the embedded pre-parse (`scripts/ksgen.c` -> committed `src/core/measures_table.inc`) is a positional KsMeasRow writer the design does not list; meas_store_check.c compares pre vs fresh
CONFIRMED (code). Severity: maintenance (red knowledge suite, or wrong decoded view of the embedded set).
Effort: small. Blast radius: every embedded set, incl. zen4-grid1@1.
- §4.5 adds `KsMeasRow.noise_e6`; its file list is ks_measures.{c,h}, memfn_sites.c, cli/main.c,
  measures_dump.c, ks_ref.py, mfixtures.py. Not ksgen.c.
- scripts/ksgen.c:347-358 writes each row positionally `{ {cols}, value_e6, unit_code, status_code }`. An
  appended `noise_e6` field is zero-initialized in the pre-parse (0 = "measured noise 0") while a fresh
  parse gives KS_MEAS_EMPTY for `-`. tests/knowledge/meas_store_check.c:72-78 decodes BOTH `pre` and
  `fresh` and the suite compares them, so either the check goes red or (if the decoded view omits the
  field) the embedded set silently carries a different noise than its text.
- Regenerating moves `src/core/measures_table.inc` bytes for grid1 too; §5/§8.2 claim grid1's artifacts
  "byte for byte" — true of set.tsv, but the .inc is a committed derived file that moves (gen-tables drift
  gate). List it in §8.2.
- Same family: the KsKind row has ONE `.item`/`.stamp` role (ks_measures.c:724-725) with a FIXED domain
  (`KS_DOMAIN` in the role, ksrc.c:533 hashes `role->domain` before the fold), so "a second KsDigest role
  beside the first" (§5) must also say which role the kind row names (no generic reader of `.item` exists
  today; grep shows only the declarations, so this is a spec-of-the-table gap, not a live bug).

### CONTRACT-4 — Goal 1's measurable form contradicts the recommended DEFAULTS reading (B), and (B) breaks S1229's anchor
CONFIRMED (text + probe). Severity: doc/maintenance. Effort: trivial. Blast radius: S2e's witness.
- Goal 1 (§1): "`--list-measurements` changes by exactly the new set's row". `build/pcrec --list-measurements`
  today prints grid1's row with `default_for` = `idk` (column 8). Under §8.3 (B) DEFAULTS -> zen4-grid3@1,
  so grid1's row ALSO changes (`default_for` empties) — two rows move, not one.
- tests/mech/sabotages/S1229_meas_default_table_class.sh:13 anchors `SAB_BEFORE='    { "idk", "zen4-grid1", 1u },'`
  in measures_table.inc (:130). Under (B) that line becomes `{ "idk", "zen4-grid3", 1u }` and the row's
  anchor no longer exists. §8.3 (B)'s package (DEFAULTS, DEFAULTS.log row 2, movers/0002.tsv) does not list
  it. Also tests/knowledge/run_measures_tests.sh:78-94 (DEFAULTS vs default_for vs DEFAULTS.log) is a reader
  of the flip (fine as written, but it is the check that S1229 plants into).
- §8.2's "every test pinning the set LIST ... each re-pinned by a count that grows by one": grep finds no
  count pin (run_measures_tests.sh:75 is a floor `>= 1`); the readers are S1229/S1241 anchors and the
  DEFAULTS check. Replace the imagined pin with these.

### CONTRACT-5 — the noise spelling admits values the kit refuses, and a kit refusal of a set is a caller-visible "internal error" on EVERY compile (today, for values)
CONFIRMED (probe). Severity: answer-adjacent (a legal input refuses every compile with an internal-error
text). Effort: small. Blast radius: every `--measures=FILE` user.
- Probe (today): set with a new id `bigset`, one kit row `value_e6 2000000000000000` (> MF_MEASURE_MAX 1e15),
  digest fixed. `build/pcrec -p rx -o p5.c --measures=p5.tsv --pattern P` for 4 patterns (`a[bc]+d`,
  `x[ab]y.*z`, `[0-9]+abc`, `foo|bar`): all rc=1, "pcrec: internal error: the memfn kit refused the window
  family's phase-1 ask on the DFA prefilter (src/gen/emit_dfa.c, window_reply_ask)". The loader accepted the
  set (measures.md §2.2¶3 has no bound), no kit row READS the value, yet every compile dies.
- The design copies the shape for noise: §4.4 spelling "`-` or a non-negative integer"; §4.1 kit check
  "MEASURED: 0 <= noise_e6 <= MF_MEASURE_MAX", refused. The §7 refusal rows (§4.4) do not include "noise past
  MF_MEASURE_MAX", so a format-2 FILE with noise 2e15 is admitted by pcrec and becomes the same internal
  error. Fix: the pcrec loader refuses |value_e6| and noise past the kit's bound (a §7 row each, its spec
  sentence), so the kit's refusal is unreachable from a loaded set; or file the existing value case as a
  K-row and mirror it for noise.

### CONTRACT-6 — the per-derivation noise rules (§4.3) are unenforced on the population they were added for (FILE sets)
CONFIRMED (text). Severity: design/doc. Effort: small. Blast radius: format-2 FILE sets with derived rows.
- §4.3: the rule is "in the format because ... a FILE set (the install tool's) may carry derived rows";
  the enforcement named is "checked by §8.2's recompute" = the pcrec-side recompute from `raw.tsv`, which
  exists only for committed sets with raw.tsv. The loader's refusals (§4.4 §7 rows) are spelling-only.
  So a format-2 FILE with an `interp-log2` row carrying numeric noise (table: UNMEASURED), a `step` row
  with noise 5 (table: 0), or a derived row with an UNMEASURED input but numeric noise is admitted and
  handed MEASURED. Today's values follow §3.2¶2 (no reader recomputes), so this may be intended — then
  §4.3 should say the noise column is the PRODUCER's rule (like values), unchecked at load, and drop the
  FILE-set argument; or add the cheap structural refusals (interp-log2/null-input -> must be `-`).

### CONTRACT-7 — format-1 decoded view and KsMeasRow.noise_e6 on a format-1 set are unspecified
CONFIRMED (text). Severity: doc. Effort: trivial.
- §4.5: "the decoded view gains `noise_e6` as parsed"; §4.5 parses noise "on format 2". measures.md §6¶3
  defines the decoded view's fields and ks_ref.py `decode` must equal pcrec's byte for byte
  (run_measures_tests.sh:58-64, R5). For a format-1 set — where noise stays free provenance TEXT (probe:
  a zen4-grid1@1 FILE with noise "abc xyz" loads, rc=0, and its canonical view carries "abc xyz") — the
  design says neither whether the parsed line appears nor what it holds (EMPTY? absent?). Grid1's decoded
  view (R5 for the store) then moves or not by the implementer's choice. State it: format 1 emits no
  parsed-noise line (grid1's decoded view byte-identical), or emits `-`.

### CONTRACT-8 — no stage-2 witness checks the noise VALUE handed to the kit; the MEASURED count cannot see a wrong column or scale
SUSPECTED (would confirm: a sabotage handing `abs_ns_e6` as noise — every S2a witness stays green). Severity:
design (the seam's whole payload is unchecked until row 1). Effort: small.
- S2a's witness: "a compile under a format-2 `--measures=FILE` shows the MEASURED count in MFMEAS". Sabotages
  (3)/(5) are STATE errors; none plants a value error (wrong column, e3 vs e6, sign). No kit row reads noise
  (§4.1), emit_sweep and the data-mover census cannot move. measure_sets.md:1551/1980 already records the
  symmetric column-swap class (S983) for this exact column.
- Fix: MFMEAS (or the harness's handed-set dump) prints a digest of the handed (key, state, noise) triples,
  compared with ks_ref.py's from the file; add the column-swap sabotage.
- Seam note (principle 9): MFMEAS today prints two `%p` addresses (memfn_sites.c:123-132), which do not
  survive a write/read across processes; the new count is fine, but a value witness should be text-only.

### CONTRACT-9 — doc readers of "the digest excludes noise_e6" missing from §4.4/§5's lists; "four constructors" vs three; mfixtures' refusal fixture uses `format 2`
CONFIRMED (text). Severity: doc/maintenance. Effort: trivial.
- docs/design/measure_sets.md:491-495 "What the digest excludes ... `noise_e6`" becomes false for format 2;
  §4.4 amends only §4.1 (:948), §5 lists :476 and :1923.
- §4.1 says "the three positional constructors found by grep" (correct: cli/main.c:160, memfn_sites.c:89,
  arm_fixtures.c:1562 — my grep agrees); §8.2's MF_SITE_ABI row says "the four constructors (§4.1)".
- tests/knowledge/mfixtures.py:177 `("format", hdr("format", "2"), "format 2")` is the refused-format
  fixture; it must move to `3` (the design names mfixtures goldens generically; name this row, it is a
  refusal that S2a makes legal).
- Seam layout (low): mf_measures crosses at mf_art_begin, but the only abi field (`mf_site.abi`) is checked
  at mf_define (compose.c:1001/1057); measures_check (compose.c:891) walks `rows[]` with the new stride before
  any abi check. In-tree single build, so unreachable today; say so rather than "MF_SITE_ABI covers it".

## PROBED-AND-HELD

- Format 1 today with a noise column (probes p1/p2): a FILE claiming zen4-grid1@1 with noise "abc xyz" or
  "12345" on all 68 rows loads (rc=0, same digest 13a6536315af1520, no-shadowing passes). This CONFIRMS the
  hole §4.2 describes; the design's format-1 rule (never handed, all UNMEASURED) closes it on the shipped path.
- Format 2 today (p3): refused "format 2 (this pcrec reads format 1)" — so no committed or user file can be
  format 2 before S2a; no silent reinterpretation of existing files.
- New-id format-1 FILE with garbage noise (p4): loads; under the design it is handed UNMEASURED. Held.
- A FILE reusing a committed id under the design: format-1 grid1@1 + noise -> same digest, accepted, noise
  UNMEASURED; format-2 claiming grid1@1 -> meas-2 digest != 13a6..., refused as shadowing (§5¶4); format-1
  claiming grid3@1 (format 2 committed) -> meas-1 digest != grid3's, refused. Held for all 3 classes.
- Null rows: none in grid1 (68 rows: 42 measured, 26 derived, all noise `-`); the kit is never handed a null
  row (memfn_sites.c:88 skips KS_MEAS_EMPTY; cli/main.c:153 skips status null). The design's "`-` on a null
  row" + §7 refusal is consistent. (arm_fixtures does NOT skip status null — CONTRACT-2.)
- Digest byte layout (§5): unambiguous (domain 13 bytes, key NUL unit status value LE noise LE, INT64_MIN for
  `-`); measured-0 vs `-` digest apart. ks_ref.py:91 and finder_check.py:320 are the independent twins;
  from_interim.py:31 listed.
- MF_SITE_ABI readers: no test pins the number (g2_gen.c uses `MF_SITE_ABI + 1` symbolically); the three
  positional constructors zero-init the appended fields, so an unedited one is refused (UNSTATED), not
  "measured 0" — the design's forcing argument holds (but see CONTRACT-5 for how a refusal surfaces).
- match_api NO hunk: §6¶14a / §6.3.10¶12-¶13 state grammar and defer the digest to measures.md; nothing in
  them moves under format 2. Held (the example literal `zen4-grid1@1:13a6...` stays a valid example even
  under (B)).
- Seam round trip: mf_measure/mf_measures cross only strings, integers and an enum — writable as text and
  re-readable; the facts are key/value/unit/noise state+value, no method (D157). census/cells.tsv/raw.tsv
  are TSV text. Pointers appear only in MFMEAS (CONTRACT-8 note).
- "Nothing moves" proof (§5, §8.1): it CAN fail — the default set is handed on every compile, so an UNSTATED
  regression makes every compile an internal error (CONTRACT-5's mechanism) and emit_sweep goes red; an
  accidental reader makes a stamp non-empty. It cannot see noise-value errors (CONTRACT-8).
- Probe count: 9 build/pcrec invocations (4 load probes, 1 listing, 4 kit-refusal compiles).
