#include "/home/pcrec/projects/pcrec/worktrees/crit-memfn-r45/memfn/include/memfn.h"
#include <stdio.h>
#include <stddef.h>
/* twins per r45_reply.md §5 table */
typedef struct { uint16_t has_scan, scan, ver_lo, ver_len; } run16;   /* "fields widen to uint16_t" (all four) */
typedef struct { uint8_t has_scan; uint16_t scan, ver_lo, ver_len; } run16b; /* has_scan stays u8 */
#define CLS_BODY \
    uint8_t v, exists, libc_free; uint8_t proven0[32]; uint32_t includes; uint16_t npres; \
    mf_link pres[MF_MAX_PRES]; uint8_t proven_prev[32]; uint8_t pres_row[MF_MAX_PRES]; uint8_t pres_led[MF_MAX_PRES];
typedef struct { CLS_BODY run16 run; uint32_t proof_n; const uint8_t (*proof)[32]; } cls_a;
typedef struct { CLS_BODY run16b run; uint32_t proof_n; const uint8_t (*proof)[32]; } cls_b;
typedef struct { CLS_BODY uint8_t proven[MF_MAX_FWD - MF_PROOF_LO][32]; mf_run_reply run; } cls_today;
typedef struct { char form_id[48]; uint32_t handle; uint8_t moved, reads_table; uint32_t includes; cls_a cls; char row[8]; } res_a;
typedef struct { int32_t start; uint16_t len; uint8_t verify, core; uint16_t core_lo, core_len;
                 const uint8_t (*set)[32]; const uint32_t *table_ref; } wspan_p;
typedef struct {
    uint8_t alt, reseed, has_stop; int32_t stop; uint8_t stop_set[32];
    uint16_t nplan; const int32_t *plan; const uint16_t *plan_term;
    uint8_t pinned, run_stated; int32_t run_member; int32_t run_lo; uint16_t run_len; char path[16];
    uint8_t framed; char frame_row[12]; char method[8]; uint8_t search, stream, fused;
    const uint8_t *plan_test; uint8_t stop_test; } wreply_p;
#define P(x) printf("%-12s %zu\n", #x, sizeof(x))
int main(void){
  P(cls_today); P(cls_a); P(cls_b); P(res_a); P(wspan_p); P(wreply_p);
  printf("8 classes today %zu proposed %zu\n", 8*sizeof(mf_class), 8*sizeof(cls_a));
  printf("3 wreply today %zu proposed %zu\n", 3*sizeof(mf_wreply), 3*sizeof(wreply_p));
  int ks[] = {32, 500, 4095};
  for (int i = 0; i < 3; i++) { int k = ks[i];
    printf("k=%d proof_n=%d rows=%d B; host span arrays 36*k=%d; plan entries k+1+8=%d x7=%d\n",
      k, k+1+MF_MAX_BACK, (k+1+MF_MAX_BACK)*32, 36*k, k+9, (k+9)*7); }
  printf("inline class at 4104 offsets: %zu\n", sizeof(cls_today) - sizeof(((cls_today*)0)->proven) + 4104*32 + 4);
  printf("MF_MAX_PRES %d sizeof mf_link %zu\n", MF_MAX_PRES, sizeof(mf_link));
  return 0; }
