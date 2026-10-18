# rwfix report ([REGIME-CORPUS] nonenglish fix, 2026-10-18)

Lane rwfix (sonnet), branch `lane/rwfix`. Light work only (no make, no suites).

## Audit
New `docs/dev/lanes/rwcorpus/audit.py` (read-only): per file strict UTF-8
decode, mojibake-sequence count, script mix, CRLF count, PG `Language:`.
All 28 nonenglish files are strict UTF-8 with 0 sequence hits (the mojibake
is valid UTF-8, so the script mix is the detector). Four files were bad:

| file | defect | replaced by |
|---|---|---|
| pg8186 | French, accents stripped (52 non-ASCII chars in 922 KB) | pg798 (Stendhal, French) |
| pg8453 | same | pg2650 (Proust, French) |
| pg20175 | Greek stored as Windows-1253-as-Latin-1: 91% Latin letters, 0 Greek | pg27073 (Modern Greek, 92% Greek letters) |
| pg9000 | "Sanskrit" is ASCII transliteration, no non-Latin script | pg27081 (Polish: Latin-extended) |

Replacements audited before adoption: all strict UTF-8, accents / script
present, 0 mojibake hits, Project Gutenberg license basis unchanged
(public domain US, same family row in PROVENANCE). The Sanskrit slot became
Polish because Devanagari/Arabic have no usable Gutenberg text; language
coverage otherwise unchanged (zh, ja, ru/bg/sr, el, he, de, fr). Not
dropped but noted: pg4572/pg4573/pg4580 are the same Chinese work (partly
duplicated).

## Caveats recorded
PROVENANCE.md "Data caveats": every PG file is CRLF (files untouched); the
head-bias list per file (five files cut at 40 MiB; code `.src` sorted by path
whole; the Census gazetteer sorted by state).

## Manifest / fetch
`sources.tsv` rows for the four files replaced (retrieval 2026-10-18);
`manifest.tsv` re-pinned by `fetch.sh --write-manifest` (see git diff: only
the four nonenglish rows should differ). fetch.sh unchanged. The four old
files were moved out of `worktrees/.corpus/nonenglish/` (into this lane's
scratch); the cache now holds the new four.

## Questions that reference replaced files (not rewritten)
- N11 `nonenglish/pg8186.txt` French words with an accented e (`\b\w*[éèêë]\w*\b`): old file has no accents so it matched nothing; it would now match.
- N20 `nonenglish/pg20175.txt` runs of Latin-1 accented letters (garbled text): the question targeted the mojibake itself; no replacement file has the property.
- No question names pg8453 or pg9000.

Other consumers naming the old files (not touched, kept for [REGIME-EVAL]'s
owner): `docs/design/memfn/regime_eval/rev22_population.py` (MISLABELLED set,
lines 45-46), `rev22_population.tsv/_out.txt`, `docs/design/memfn/regime_eval.md`
caveat (c) (lines 106, 362, 855-862, 2790). Their per-file shape numbers in
`rwcorpus_report.md` (pg8186 etc.) describe the old bytes and were not
regenerated. With the files replaced, caveat (c) no longer applies to the
current corpus, but those documents are the kit's to update.
