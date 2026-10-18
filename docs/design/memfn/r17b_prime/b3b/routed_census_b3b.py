#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3b/routed_census_b3b.py -- R17-b' B3b's
ROUTED-RECORD COUNT (lane b3b; r17b_prime.md rev 3 §1.6 [rev3 B5] item 1,
§8.1 "the routed-record floors per (kind, row) from B2", §8.3 SN-1).

    routed_census_b3b.py <fdb2/routed_census.py's own arguments>

B2's census (../fdb2/routed_census.py) IMPORTED, never copied, with the rows
routed at B3b added to its ROUTED set: D2 and slot PRES's P0, P2, P3, P4, P9.
pcrec prints one `MFROUTED<TAB>PRE<TAB>kind<TAB>row` record per presence span
the kit's routed PRES rows decided (src/gen/memfn_sites.c
`pcrec_memfn_pres_routed`, read off the links pcrec consumed: the define's
class, or the admission's ask where P2 drops the pre-check), so a PRES row
that stops routing (SN-1) shows as a cell under its floor, and a row routing
early (a B4 row) as a record of a row outside ROUTED. Floors:
routed_floors_B3b.tsv, floor(0.9 x measured) per (site, kind, row).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("routed_census", os.path.join(HERE, "..", "fdb2", "routed_census.py"))
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
rc.ROUTED = set(rc.ROUTED) | {"D2", "P0", "P2", "P3", "P4", "P9"}
sys.exit(rc.main())
