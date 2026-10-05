# memfn/docs/ — the kit's coordination and record files

- `requests.md` — pcrec manager → kit: requests `R-n` and defects `D-n`.
  ONE writer, the pcrec manager, as a single-file `[requests]` commit on
  main (D78; integration.md §20.1, file names per lane memfnsetup). The
  kit never edits it.
- `responses.md` — kit → pcrec manager: `ack:`/`done:` per item and the
  kit's own durable notices. ONE writer, the kit session, as a single-
  file `[responses]` commit on its branch, merged by the manager. The
  manager never edits it.
- `journal.md` — the kit's own append-only dated journal (the kit
  session and kit lanes append; nothing is edited away).
- `wake.md` — the kit session's orientation file. Born as a TEMPLATE; the
  kit session rewrites it from scratch at every session end or pause.

Items in the ledger pair are numbered and never deleted; a superseded
item says so in place. Live coordination stays interprocess
(SendMessage); these files carry what must survive a session boundary.
