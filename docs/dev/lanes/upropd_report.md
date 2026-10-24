# Lane upropd report — [UPROP-MORE] design note

Deliverable: `docs/design/uprop_more.md` (PROPOSED), index line in `docs/design/CLAUDE.md`.

Findings: libpcre2 10.46 accepts 53 binary properties (106 spellings) + Bidi_Class
short names; rejects Age/Block/Assigned/other axes. So Emoji, Default_Ignorable,
Bidi_Class are catch-up; only Block/Age are extensions. One missing mechanism:
a ranged-file reader in third_party/ucd-16.0.0/generate.py. No engine/abi change.
Premise test recorded in the note. Caseless: binary props unchanged under -i (measured).

## STATE AT HANDOFF
- Rulings file `docs/dev/lanes/upropd_rulings.md`: empty, no entries applied.
- No code, no plan rows edited. Nothing built; no owed runs.
- Estimates (not measured): emitted size of big props, added interval count (15-20k).
- Unconfirmed: which file carries Grapheme_Link (generator coverage check settles it).
- Scratch: /tmp/claude-1001/upropd/ (probe.py, emitted .c samples), not committed.
