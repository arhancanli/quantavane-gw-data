/* Cubic family: primes p = 1 (mod 3) with (i) the classes of 1, 2, 3 not all distinct (no rainbow 4-AP through 0)
   and (ii) no l consecutive elements of {1..p-1} in one cubic class. Exhaustive below the Weil-type cutoff
   sqrt(p) > 3^l (2l/3 - 1 + 3^-l) + l. Then GW(4;4,l) >= (l-1)p + 1.  Usage: pstar3 lmin lmax */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static int isprime(uint64_t n){ if(n<2) return 0; for(uint64_t d=2; d*d<=n; d++) if(n%d==0) return 0; return 1; }
static uint64_t pw(uint64_t b, uint64_t e, uint64_t p){ uint64_t r=1; b%=p; while(e){ if(e&1) r=(__uint128_t)r*b%p; b=(__uint128_t)b*b%p; e>>=1;} return r; }
int main(int argc, char **argv){
  int lmin = atoi(argv[1]), lmax = atoi(argv[2]);
  for (int l = lmin; l <= lmax; l++){
    double c = pow(3.0, l) * (2.0 * l / 3.0 - 1 + pow(3.0, -l)) + l; uint64_t cut = (uint64_t)(c * c) + 1;
    uint64_t best = 0; int count = 0;
    for (uint64_t p = 7; p <= cut; p += 6){ if (!isprime(p)) continue;
      uint64_t e = (p - 1) / 3, v2 = pw(2, e, p), v3 = pw(3, e, p);
      if (v2 != 1 && v3 != 1 && v2 != v3) continue;           /* (i) fails: classes of 1, 2, 3 all distinct */
      int run = 0, bad = 0; uint64_t prev = 0;
      for (uint64_t a = 1; a < p; a++){ uint64_t x = pw(a, e, p); run = (x == prev) ? run + 1 : 1; prev = x; if (run >= l){ bad = 1; break; } }
      if (!bad){ best = p; count++; if (l == 4) printf("l=4 p=%llu\n", (unsigned long long)p); }
    }
    printf("RESULT cubic l=%d cutoff=%llu qualifying=%d largest=%llu => GW(4;4,%d) >= %llu\n", l, (unsigned long long)cut, count, (unsigned long long)best, l, (unsigned long long)((l-1)*best+1));
    fflush(stdout);
  }
  return 0;
}
