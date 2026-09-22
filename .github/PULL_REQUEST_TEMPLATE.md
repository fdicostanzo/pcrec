<!--
Short checklist per [REL-1.6] (rel16). See CONTRIBUTING.md for the full
version of each of these; kept to five lines here on purpose.
-->

- [ ] `make strict` is clean
- [ ] `make test` is green, or every failure is a documented, pre-existing skip
- [ ] If a caller can observe this change (an entry, a flag, a diagnostic, a limit), `docs/spec/` has a hunk in this PR
- [ ] Any behaviour change has a test
- [ ] The touched directory's `CLAUDE.md` is updated if files/roles changed
