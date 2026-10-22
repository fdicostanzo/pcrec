# stfix report

Cause confirmed: scripts/sectiontimes `stamp` read stdin as strict UTF-8 text.
Fix: stamp reads/writes bytes (matching on a latin-1 view; patterns are ASCII),
so every byte passes through unchanged. scripts/perfrun's errnames `grep` now
uses `-a` (a 0xff in the log made grep print "Binary file matches" instead of
the verdict lines). The `awk` filters read only perfrun's own TSVs.
No self-test exists for sectiontimes; none added. Probe: `printf 'ok\xff\n..'`
through `stamp` and `stamp SIDE`: rc 0, non-debug output byte-identical.

STATE AT HANDOFF: committed on lane/stfix; no rulings file entries applied.
