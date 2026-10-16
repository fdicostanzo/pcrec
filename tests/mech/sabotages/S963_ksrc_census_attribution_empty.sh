# S963 — [KNOW-SRC] K0 (docs/design/measure_sets.md rev 3 §8.5, §9.3): the
# data-mover census's ANALYSIS ARM WRITES ITS ATTRIBUTION EMPTY
# (scripts/emit_sweep.py, `run_data_census`): every mover still lands in the
# movers TSV, but with no reader named, so a data change's movers could not
# be traced to the selection that moved them — the census reduced to a byte
# diff.
#
# Detector: run_findings_tests.sh §13 runs the census on data_census/'s
# fixture change; an empty attribution on a moved artifact fails it
# (UNATTRIBUTED), and so the census disagrees with the hand-made list.
SAB_ID="S963-ksrc-census-attribution-empty"
SAB_FILE="scripts/emit_sweep.py"
SAB_SUITES="findings"
SAB_DESC="emit_sweep.py --data analysis writes every mover's attribution empty: the lookup trace is read and then dropped, so a moved artifact names no reader (measure_sets.md §9.3's one attribution mechanism lost)"
SAB_DOC_FIGURE="findings red on §13 (UNATTRIBUTED on each of the fixture's 8 movers). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S963."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                att = ",".join(sorted({f"{q}@{rd}" for q, rd, _ in a[4] + z[4]}))'
SAB_AFTER='                att = ""   # SABOTAGE S963: the attribution dropped'
