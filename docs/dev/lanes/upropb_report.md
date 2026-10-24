# upropb report — [UPROP-MORE] build (lane upropb, sonnet, 2026-10-24)

Branch `lane/upropb`. Design of record: `docs/design/uprop_more.md`; rulings D178 and R1 (`upropb_rulings.md`).

## Files vendored (`third_party/ucd-16.0.0/`, curl -o, from unicode.org/Public/16.0.0/ucd/)

| file | bytes | sha256 |
|---|---|---|
| PropList.txt | 144,253 | 53d614508e2a0b2305a8aa21cd60d993de9326cdf65993660dfcce4503548583 |
| DerivedCoreProperties.txt | 1,115,959 | 39d35161f2954497f69e08bdb9e701493f476a3d30222de20028feda36c1dabd |
| emoji-data.txt | 113,024 | f1365a5173eee18e1f98b240cdc492e84a25f1ce7e0c9d1094eb29c41a22696a |
| DerivedBidiClass.txt | 171,034 | 71ed943a49c58568d8d92e80ecc2ba2f06e62aee9c8ebb0e6e8bd2c3ed8b180e |
| PropertyAliases.txt | 9,389 | 33a9f2266ad6b8e8de05c0ea3dfac411ac62cf8839ff1c94057471e4c5f6a2b3 |
| Blocks.txt | 11,397 | f3907b395d410f1b97342292ca6bc83dd12eb4b205f2a0c48efdef99e517d7b0 |
| DerivedAge.txt | 134,680 | 60caa81b99a4dfb0bc5d38440d323073e3f356f46f9ca7869da848cd0715408b |

Headers name 16.0.0 except `emoji-data.txt` (header `# emoji-data.txt`, dated 2024-05-01; recorded in PROVENANCE.md). URLs in PROVENANCE.md.

## What shipped

- Generator: ranged-file reader, counted promise lists (55 binary long names, 23 bc short names, every `blk`/`age` value), hard failure on a missing source line; `@missing` defaults of DerivedBidiClass applied (a later line overrides an earlier default, never a data line); `Bidi_Mirrored` from UnicodeData field 9.
- Table: 717 -> 1384 rows, 312 -> 747 sets, 10,961 -> 26,199 intervals (limit 65,535), 242,808 bytes.
- `mod_uprops.c`: prefixes `bc`/`bidiclass`, `blk`/`block`, `age` (3 new namespaces). No abi event, no parser/engine change; Block/Age ride module `unicode-props` (R1.2).
- Block and Age were the same ranged setup; no stop. Age = exactly the first-assignment version (the file's definition); `Age=NA` unassigned; `blk=NB` No_Block.
- Spec: `cli.md` §1.17.1¶1-5, `pattern_language.md` §7.9¶1 and §9¶2. Compliance page rows (store + regenerated blocks), upstream issue U22.
- Wording: "properties as defined by the Unicode 16.0.0 data files"; no conformance level.

## Verification

- Whole-space differential vs libpcre2 10.46 (= the pin, EXACT tier): all 78 new names agree except `Bidi_Mirrored` (PCRE2 428, UCD 554, python 554; 126 math symbols; U22; exact-126 exception `UPSTREAM_SUPERSET` in `uprops_compare.py`). Full utf8 arm green (45 checks at the time, 466 properties compared). The first sweep caught a real generator bug (bc defaults not overriding), fixed.
- `tests/uprops` now 50 checks (byte arm): §6 Block/Age vs data files + structure (utf8: 367 sweeps exact, Age a function, `age=NA` completes, blocks + `blk=NB` tile), python unicodedata 16.0.0 cross-check (Bidi_Mirrored, bc, 292,531 assigned cps), spelling/negation/caseless identities; §7 six generator sabotage cells + control + wrong-alias (no mech ids used; S1570-S1579 unused).
- PC-3 (`pcre2_check.c`): the "real-but-unshipped" clause is gone (population empty); replaced by the converse (T2) over a committed list (139 binary spellings + 46 bc values x 3 forms x 2 selectors), both directions, plus the Block/Age extension arm (pcrec accepts, PCRE2 must refuse), floors. Registry pin 213 -> 214.
- Corpora: `tests/utf8/uprop_more.rxt` (+gen.py, libpcre2-generated, 278 cases) and `uprop_blk_age.rxt` (69 cases); retired 5 axis05 + 1 axis12 refusal blocks (PCRE2 accepts Emoji_Modifier/Grapheme_Base/Grapheme_Extend; Block/blk are extensions). `tests/utf8` harness 3636 cases, 0 failed. Not extended: the committed `oracle_store` (79 names fall back to the live 10.46 oracle).

## Size (default axes, `-e utf8 --features unicode-props`, gcc -O2 -c; text/data bytes of the .o)

| pattern | .c bytes | text | data |
|---|---|---|---|
| `\p{Emoji}` | 85,372 | 27,712 | 224 |
| `\p{Alphabetic}` | 603,115 | 190,069 | 224 |
| `\p{Default_Ignorable_Code_Point}` | 37,587 | 11,326 | 224 |
| `\p{Bidi_Class=R}` | 53,157 | 16,491 | 224 |
| `\p{Block=Greek}` | 18,258 | 3,858 | 224 |
| (refs) `\p{L}` / `\p{bc=L}` / `\p{Greek}` | 586,042 / 425,862 / 47,399 | 184,680 / 140,977 / 14,563 | 224 |

`\p{Alphabetic}` has `\p{L}`'s profile (warns at 250 KB; compiles). Compiler growth: `mod_uprops.o` text 93,192 -> 220,636, data 17,272 -> 33,376 (file 200,048 -> 359,464); `build/pcrec` 5,892,960 -> 6,052,280 (+159,320); `libpcrec.a` 11,781,178 -> 11,940,594. Existing patterns' emitted bytes unchanged (new names only).

## Re-pins (old -> new, each from the check's own output)

- rxtsource: files 294->296, blocks 6048->6157, lines 74005->74346; run.sh 270->272 files; C3 PASS 21957->21952, SKIP 51962->52308, pcre2-only 19377->19723, verifiable 24189->24184. Re-run green (298 checks).
- codegen dfa_stamps empty-engine manifest 104 -> 141 (37 byte-empty property patterns). Re-run green (40).
- reject: controls 120 -> 123, gated 112 (two rows swapped for `\p{gc=L}`, `\p{Hyphen}`); green (660).
- registry: PC-3 passing 213 -> 214; needles replaced (T2, extension, converse liveness); registry/uprops in the light chain green.
- `make strict` clean.

## Open points for the manager

- Plan row [UPROP-MORE] state and the D178 amendment (Block/Age ride unicode-props; U22) are yours; I did not touch plan.md / decisions.md / journal.
- No `docs/guide/` page written (emoji digit gotcha, Trojan-Source example are doc-only unlocks).
- Not run: the full `make test` (owed, job `616-upropb-test`), `make test-axes`, sanitizers.

## STATE AT HANDOFF

Everything committed on `lane/upropb`; rulings applied through R1. Light chain (rxtsource, codegen, registry, uprops) was green after the pins above except the two re-pinned suites, which were re-run green separately; the codegen suite's other groups ran in the first chain without other reds. OWED: job `616-upropb-test` (make test through perfrun, 77 sections), queued last.

QUEUED (last act): `616-upropb-test` via `scripts/boxqueue add` (cap 3600, expect sections=77, witness `sections ran: 77/77`). Verdict: `scripts/boxqueue state upropb-test`, log in `worktrees/.boxqueue/*/616-upropb-test/job.log.make`; a red is read with its `.perfrun` note.
