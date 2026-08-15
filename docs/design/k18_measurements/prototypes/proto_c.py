#!/usr/bin/env python3
"""Prototype C — prototype A with the memo REMOVED (the naive path-local walk).

MEASUREMENT ARTIFACT, NOT A PROPOSED PATCH. Its only job is to price the memo:
C and A implement the SAME empty-iteration rule and produce the same answers,
so any cost difference between them is the memo's contribution and nothing
else. That makes it the control the design note needs for "the memo is what
makes the exact rule affordable", rather than an assertion that it is.

C keeps the open-loop stack (which is what breaks cycles, so it still
terminates) and keeps the global N_CLASS emission dedup (so DFA states are
identical); it simply never suppresses a re-arrival. A visit budget aborts the
compile with a distinctive message so a blowup is REPORTED as a number rather
than showing up as a hang.
"""
import subprocess
import sys

path = sys.argv[1]
subprocess.run([sys.executable,
                __file__.replace("proto_c.py", "proto_a.py"), path], check=True)

src = open(path).read()

old = """        if (k18_stats_on) k18_stats.memo_probes++;
        if (!pmemo_add(cl->memo, s, cl->ctx)) break;
        if (k18_stats_on) k18_stats.expansions++;"""

new = """        /* PROTOTYPE C: no memo. The (state,ctx) pair is recorded for the
         * counters only; the walk is never suppressed by it. */
        pmemo_add(cl->memo, s, cl->ctx);
        k18_stats.expansions++;
        if (k18_stats.expansions > 300000000L) {
            fprintf(stderr, "K18BUDGET exceeded 3e8 visits\\n");
            exit(97);
        }"""

assert old in src, "proto A anchor drift"
src = src.replace(old, new)

# the visit counter must run even without PCREC_K18_STATS, since the budget
# reads it
src = src.replace("        if (k18_stats_on) k18_stats.visits++;",
                  "        k18_stats.visits++;")
open(path, "w").write(src)
print("proto C applied to", path)
