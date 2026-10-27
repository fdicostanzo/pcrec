static const char *bn[8] = {"reqrun_precheck","reqrun_whole_precheck","startset_loop","vm_at_https_www","vm_elsewhere","reset","",""};
static void attr_print(void) {
    uint64_t a = pmc_now(); uint64_t b = pmc_now(); uint64_t ov = b - a;
    for (int i = 0; i < 8; i++) if (g_n[i]) printf("  %-24s n=%llu instr=%llu (minus probe ~%llu each) net=%lld per=%.1f\n", bn[i], g_n[i], g_b[i], (unsigned long long)ov, (long long)(g_b[i] - ov*g_n[i]), (double)(g_b[i] - ov*g_n[i]) / g_n[i]);
    memset(g_b, 0, sizeof g_b); memset(g_n, 0, sizeof g_n);
}
