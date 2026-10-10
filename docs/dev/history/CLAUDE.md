# docs/dev/history/ — build history moved out of the spec tier

docs/spec/ states contracts and carries no build history (docs/spec/CLAUDE.md;
`make test-spec-history`). When a spec document is cleaned to facts only, the
history it carried — revision notes, rulings, walkbacks, superseded wordings,
dated row notes — comes here, so nothing is lost and nothing here is mistaken
for a promise. Files here are RECORDS: never normative, never cited as the
contract. Created by lane specclean (2026-10-09, `[SPEC-CLEAN]`).

## Files

- `match_api_record.md` — FROZEN. The history `docs/spec/match_api.md`
  carried until its facts-only rewrite: every flagged paragraph of the old
  text, verbatim and in order, each tagged with its old section and line
  range, plus docs/spec/CLAUDE.md's old `match_api.md` entry. The complete
  old text is `git show aee1a570:docs/spec/match_api.md`;
  `studies/specclean/claims.tsv` maps its claims to the new document.
- `abi_changelog.md` — LIVING. The `abi` change log, newest first, one entry
  per bump (D76 addendum [REVW.A1] named its home; it moved here verbatim
  from match_api.md §6). **An `abi` bump adds its entry here in the bump's
  own commit**, beside the spec's `rx_info.abi` sentence (D76/D94's readers).

Maintenance: a future spec cleanup adds its own `<doc>_record.md` here and a
line above.
