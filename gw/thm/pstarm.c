/* Unified family: m-th power residue colouring of Z_p (p = 1 mod m) with the zero class as an (m+1)-th colour.
   (i) for every position i in 0..m of the zero point in an (m+1)-AP of difference 1, the m residues j - i (j != i)
       do NOT lie in m distinct classes (so no rainbow (m+1)-AP through the zero class);
   (ii) no l consecutive elements of {1..p-1} lie in one class (no monochromatic l-AP).
   Then GW(m+1; m+1, l) >= (l-1)p + 1. Exhaustive below sqrt(p) > m^l((m-1)l/m - 1 + m^-l) + l.  Usage: pstarm m lmin lmax */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static int isprime(uint64_t n){ if(n<2) return 0; for(uint64_t d=2; d*d<=n; d++) if(n%d==0) return 0; return 1; }
static uint64_t pw(uint64_t b, uint64_t e, uint64_t p){ uint64_t r=1; b%=p; while(e){ if(e&1) r=(__uint128_t)r*b%p; b=(__uint128_t)b*b%p; e>>=1;} return r; }
int main(int argc, char **argv){
  int m = atoi(argv[1]), lmin = atoi(argv[2]), lmax = atoi(argv[3]);
  for (int l = lmin; l <= lmax; l++){
    double c = pow(m, l) * ((m - 1.0) * l / m - 1 + pow(m, -l)) + l; uint64_t cut = (uint64_t)(c * c) + 1;
    uint64_t best = 0; int count = 0;
    for (uint64_t p = m + 1; p <= cut; p++){ if (p % m != 1 || !isprime(p)) continue;
      uint64_t e = (p - 1) / m; int ok = 1;
      for (int i = 0; i <= m && ok; i++){            /* condition (i) */
        uint64_t cls[16]; int k = 0, distinct = 1;
        for (int j = 0; j <= m; j++) if (j != i){ int64_t r = (int64_t)j - i; uint64_t x = (uint64_t)((r % (int64_t)p + (int64_t)p) % (int64_t)p); cls[k++] = pw(x, e, p); }
        for (int a = 0; a < k && distinct; a++) for (int b = a + 1; b < k; b++) if (cls[a] == cls[b]) { distinct = 0; break; }
        if (distinct) ok = 0;
      }
      if (!ok) continue;
      int run = 0, bad = 0; uint64_t prev = 0;
      for (uint64_t a = 1; a < p; a++){ uint64_t x = pw(a, e, p); run = (x == prev) ? run + 1 : 1; prev = x; if (run >= l){ bad = 1; break; } }
      if (!bad){ best = p; count++; }
    }
    printf("RESULT m=%d l=%d cutoff=%llu qualifying=%d largest=%llu => GW(%d;%d,%d) >= %llu\n", m, l, (unsigned long long)cut, count, (unsigned long long)best, m + 1, m + 1, l, (unsigned long long)(best ? (l - 1) * best + 1 : 0));
    fflush(stdout);
  }
  return 0;
}
