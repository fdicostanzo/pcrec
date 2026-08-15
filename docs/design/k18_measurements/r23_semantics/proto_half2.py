#!/usr/bin/env python3
"""HALF-PROTOTYPE (2): change (2) ALONE — the redirect trigger becomes
"this loop is OPEN on my path", but the memo stays keyed on the STATE alone.

The note's §1.4 marks BELIEVED that neither half fixes K18 on its own and asks
(§6 ruling 2) whether it should be measured. This builds one half.
Implementation: prototype A with the memo key's context forced to 0, so the
memo degenerates to exactly the shipped per-state memo while the open-loop
stack and the open-set redirect trigger are kept."""
import subprocess, sys
path = sys.argv[1]
subprocess.run([sys.executable,
  "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_a.py", path], check=True)
src = open(path).read()
old = "        if (!pmemo_add(cl->memo, s, cl->ctx)) break;"
assert old in src, "anchor drift"
src = src.replace(old, "        if (!pmemo_add(cl->memo, s, 0)) break;   /* HALF-2: state-only memo */")
open(path, "w").write(src); print("half2 applied")
