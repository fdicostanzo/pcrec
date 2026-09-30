#!/usr/bin/env python3
"""Extract engine_metadata (pcrec's own compile-time stamps) per pattern for
the auto-caps and auto-nocaps testees, form='plain' (the search-regime
artifact) and form='whole-subject' (the match-compliance artifact) separately.
Read-only against pcrec-bench's store/records/."""
import json

FILES = {
    ("caps", "plain"): "store/records/syntax@0.1/pcrec_751b9c6d_auto-caps-simdna/syntax@0.1__pcrec_751b9c6d_auto-caps-simdna__budu-ryzen1600__20260927T113954Z.jsonl",
    ("nocaps", "plain"): "store/records/syntax@0.1/pcrec_751b9c6d_auto-nocaps-simdna/syntax@0.1__pcrec_751b9c6d_auto-nocaps-simdna__budu-ryzen1600__20260927T122553Z.jsonl",
}

out = {"caps": {}, "nocaps": {}}
base = "/Users/fdicostanzo/pcrec-bench/"
for (cap, wantform), relpath in FILES.items():
    with open(base + relpath) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("kind") != "compile":
                continue
            form = d.get("form", "plain")
            if form != wantform:
                continue
            pid = d.get("pattern_id")
            if pid in out[cap]:
                continue
            em = d.get("engine_metadata", {})
            out[cap][pid] = {
                "engine": em.get("engine"),
                "engine_sel": em.get("engine_sel"),
                "dfa_prefilter": em.get("dfa_prefilter"),
                "dfa_prefilter_offsets": em.get("dfa_prefilter_offsets"),
                "dfa_scan": em.get("dfa_scan"),
                "dfa_scan_edge": em.get("dfa_scan_edge"),
                "dfa_start": em.get("dfa_start"),
                "dfa_match": em.get("dfa_match"),
                "end_window": em.get("end_window"),
                "req_byte": em.get("req_byte"),
                "req_run": em.get("req_run"),
                "req_why": em.get("req_why"),
                "ncaps": em.get("ncaps"),
                "ngroups": em.get("ngroups"),
                "resume_frames": em.get("resume_frames"),
                "artifact_bytes": d.get("artifact_bytes"),
                "emit_bytes": em.get("emit_bytes"),
            }

import sys
json.dump(out, open("engine_meta.json", "w"), indent=1)
print(f"caps: {len(out['caps'])} nocaps: {len(out['nocaps'])}", file=sys.stderr)
