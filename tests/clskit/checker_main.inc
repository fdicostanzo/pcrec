/* tests/clskit/checker_main.inc — the checker's main(), included at the end
 * of every chunk clskit_driver writes (VARS, SETS and COMPS are the chunk's).
 *
 * For every set, every code point 0..0x10FFFF plus three beyond it: the
 * reference (a sequential walk of the set's own interval arrays, which no
 * kit code wrote) against every variant. Then the composition law: for each
 * COMP, variant V of set c must equal op(V of a, V of b) on every code
 * point, for V in {K4, P3} — the law provenance-blindness makes testable
 * (clskit.h, Constraint 1). Prints one CHECKED line per set and a TOTAL.
 */
static const unsigned BEYOND[] = { 0x110000u, 0x7FFFFFFFu, 0xFFFFFFFFu };

/* The VARS index of variant `var` of set `idx`, or -1. */
static int find_var(int idx, const char *var)
{
    for (unsigned v = 0; v < sizeof VARS / sizeof VARS[0]; v++)
        if (VARS[v].set == idx && !strcmp(VARS[v].var, var)) return (int)v;
    return -1;
}

int main(void)
{
    enum { NV = sizeof VARS / sizeof VARS[0], NS = sizeof SETS / sizeof SETS[0] };
    unsigned long long checks = 0, bad = 0, cchecks = 0;

    for (int s = 0; s < NS; s++) {
        int vs[64], nv = 0;
        unsigned long long vbad[64] = { 0 }, sbad = 0;
        for (int v = 0; v < NV && nv < 64; v++)
            if (VARS[v].set == SETS[s].idx) vs[nv++] = v;
        int j = 0;
        for (unsigned cp = 0; cp <= 0x10FFFFu; cp++) {
            while (j < SETS[s].n && SETS[s].hi[j] < cp) j++;
            int ref = j < SETS[s].n && SETS[s].lo[j] <= cp;
            for (int q = 0; q < nv; q++)
                if ((VARS[vs[q]].fn(cp) != 0) != ref && vbad[q]++ < 3)
                    fprintf(stderr, "MISMATCH set=%s var=%s cp=U+%04X got=%d want=%d\n",
                            SETS[s].name, VARS[vs[q]].var, cp, !ref, ref);
        }
        for (unsigned b = 0; b < sizeof BEYOND / sizeof BEYOND[0]; b++)
            for (int q = 0; q < nv; q++)
                if (VARS[vs[q]].fn(BEYOND[b]) != 0 && vbad[q]++ < 3)
                    fprintf(stderr, "MISMATCH set=%s var=%s cp=0x%X beyond the code space\n",
                            SETS[s].name, VARS[vs[q]].var, BEYOND[b]);
        for (int q = 0; q < nv; q++) sbad += vbad[q];
        checks += (unsigned long long)nv * (0x110000ULL + 3);
        bad += sbad;
        printf("CHECKED %s variants=%d mismatches=%llu\n", SETS[s].name, nv, sbad);
    }

    static const char *const LAWVARS[] = { "K4", "P3" };
    for (int k = 0; k < NCOMP; k++)
        for (unsigned w = 0; w < sizeof LAWVARS / sizeof LAWVARS[0]; w++) {
            int vc = find_var(COMPS[k].c, LAWVARS[w]), va = find_var(COMPS[k].a, LAWVARS[w]),
                vb = find_var(COMPS[k].b, LAWVARS[w]);
            unsigned long long lbad = 0;
            if (vc < 0 || va < 0 || vb < 0) { fprintf(stderr, "COMP %d: variant %s missing\n", k, LAWVARS[w]); bad++; continue; }
            for (unsigned cp = 0; cp <= 0x10FFFFu; cp++) {
                int a = VARS[va].fn(cp) != 0, b = VARS[vb].fn(cp) != 0, want = 0;
                switch (COMPS[k].op) {
                case 'u': want = a || b; break;
                case 'i': want = a && b; break;
                case 'd': want = a && !b; break;
                case 'c': want = !a; break;
                }
                if ((VARS[vc].fn(cp) != 0) != want && lbad++ < 3)
                    fprintf(stderr, "LAW MISMATCH comp=%d op=%c var=%s cp=U+%04X\n",
                            k, COMPS[k].op, LAWVARS[w], cp);
            }
            cchecks += 0x110000ULL;
            bad += lbad;
            printf("LAW %s op=%c var=%s mismatches=%llu\n", SETS[0].name, COMPS[k].op, LAWVARS[w], lbad);
        }
    printf("TOTAL checks=%llu law_checks=%llu mismatches=%llu\n", checks, cchecks, bad);
    return bad != 0;
}
