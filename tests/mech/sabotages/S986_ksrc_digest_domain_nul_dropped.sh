# S986 — [KNOW-SRC] K1 (docs/design/measure_sets.md rev 3 §8.5, §9.2 part
# 5): `pcrec_ks_digest` HASHES A SUB-KEYED DOMAIN WITHOUT ITS TRAILING NUL
# (src/core/ksrc.c). The shipped stamp tag is `pcrec-find-1\0byte-rate\0`,
# hashed with `sizeof` so the terminator is part of it; a parts rewrite that
# treated the domain as a C string would move EVERY `<PREFIX>_FINDINGS`
# stamp — an abi event as a side effect, which is why the domains are
# literal bytes with an explicit length.
#
# Detector: run_findings_tests.sh §4 (the library's default digest against
# findings_ref.py's independent FNV over default_ppm.tsv, and every stamp
# check that names it), §6's stamps against bundle-digest.
SAB_ID="S986-ksrc-digest-domain-nul-dropped"
SAB_FILE="src/core/ksrc.c"
SAB_SUITES="findings"
SAB_DESC="pcrec_ks_digest drops the trailing NUL of a sub-keyed role's domain (pcrec-find-1 hashed as 12 bytes, not 13), so every _FINDINGS stamp digest moves while every rows_digest (no sub-key) stays"
SAB_DOC_FIGURE="findings red on §4 (the default digest no longer the independent FNV's) and on every §6 stamp naming a digest. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S986."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    uint64_t h = pcrec_ks_fnv1a(pcrec_ks_fnv_basis, role->domain, role->domain_len);'
SAB_AFTER='    uint64_t h = pcrec_ks_fnv1a(pcrec_ks_fnv_basis, role->domain,
                                role->domain_len - (role->subkey == KS_SUB_QUERY)); /* SABOTAGE S986 */'
