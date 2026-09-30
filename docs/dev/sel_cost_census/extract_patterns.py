#!/usr/bin/env python3
"""Extract the PATTERNS tuple from pcrec-bench's bench/syntax/gen_patterns.py
by importing the module directly (read-only; pcrec-bench is not modified)."""
import importlib.util
import json
import sys

path = "/Users/fdicostanzo/pcrec-bench/bench/syntax/gen_patterns.py"
spec = importlib.util.spec_from_file_location("gen_patterns", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

out = {}
for row in mod.PATTERNS:
    pid, family, constructs, text, note = row
    out[pid] = {
        "family": family,
        "constructs": list(constructs),
        "text": text,
        "note": note,
    }

print(json.dumps(out, indent=1))
print(f"# total patterns: {len(out)}", file=sys.stderr)
