/* Primes for the pigeonhole family (k5 agent, 12 Nov 2026): p prime, p = 1 (mod m), p > max(l, m+1), and
   (ii) no l consecutive elements of {1,...,p-1} lie in one m-th power class.  Then the m-th power residue colouring
   with a split zero class has no rainbow (m+2)-AP at all (pigeonhole) and gives GW(m+s; m+2, l) >= (l-1)p + 2.
   Exhaustive below the Weil cutoff sqrt(p) > m^l((m-1)l/m - 1 + m^-l) + l (same cutoff as thm/pstarm.c, which also
   requires condition (i)); an optional bound scans further.  Usage: pstar_pig m lmin lmax [bound] */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static int isprime(uint64_t n){ if(n<2) return 0; for(uint64_t d=2; d*d<=n; d++) if(n%d==0) return 0; return 1; }
static uint64_t pw(uint64_t b, uint64_t e, uint64_t p){ uint64_t r=1; b%=p; while(e){ if(e&1) r=(__uint128_t)r*b%p; b=(__uint128_t)b*b%p; e>>=1;} return r; }
int main(int argc, char **argv){
  int m = atoi(argv[1]), lmin = atoi(argv[2]), lmax = atoi(argv[3]);
  uint64_t bound = argc > 4 ? strtoull(argv[4], 0, 10) : 0;
  for (int l = lmin; l <= lmax; l++){
    double c = pow(m, l) * ((m - 1.0) * l / m - 1 + pow(m, -l)) + l; uint64_t cut = (uint64_t)(c * c) + 1;
    uint64_t top = bound > cut ? bound : cut;
    uint64_t best = 0; int count = 0; uint64_t lo = (uint64_t)(l > m + 1 ? l : m + 1);
    printf("m=%d l=%d cutoff=%llu scan to %llu: primes", m, l, (unsigned long long)cut, (unsigned long long)top);
    for (uint64_t p = lo + 1; p <= top; p++){ if (p % m != 1 || !isprime(p)) continue;
      uint64_t e = (p - 1) / m; int run = 0, bad = 0; uint64_t prev = 0;
      for (uint64_t a = 1; a < p; a++){ uint64_t x = pw(a, e, p); run = (x == prev) ? run + 1 : 1; prev = x; if (run >= l){ bad = 1; break; } }
      if (!bad){ best = p; count++; printf(" %llu", (unsigned long long)p); }
    }
    printf("\nRESULT m=%d l=%d qualifying=%d largest=%llu => GW(%d+s;%d,%d) >= %llu\n", m, l, count, (unsigned long long)best, m, m + 2, l, (unsigned long long)(best ? (l - 1) * best + 2 : 0));
    fflush(stdout);
  }
  return 0;
}
