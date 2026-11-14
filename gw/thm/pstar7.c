/* Endpoint variant (11 Nov 2026 21:xx): primes p = 7 (mod 8) (chi(2) = 1, chi(-1) = -1) such that
   (a) p > l, (b) no l consecutive elements of {1,...,p-1} have equal quadratic character, and
   (c) chi(1), ..., chi(l-1) are not all equal.
   Colouring of [1,(l-1)p+1]: x -> chi(x-1) for x != 1 (mod p); zero-class points 1+jp, 0 < j < l-1, get main colour +1;
   point 1 gets a new colour (r = 3); for even l the point (l-1)p+1 gets a second new colour (r = 4).
   Exhaustive up to the same Weil-type cutoff as pstar.c:  sqrt(p) > 2^l (l/2 - 1 + 2^-l) + l.
   Usage: pstar7 lmin lmax */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static int isprime(uint64_t n){ if(n<2) return 0; for(uint64_t d=2; d*d<=n; d++) if(n%d==0) return 0; return 1; }
static int chi(uint64_t a, uint64_t p){ uint64_t e=(p-1)/2, r=1, b=a%p; while(e){ if(e&1) r=(__uint128_t)r*b%p; b=(__uint128_t)b*b%p; e>>=1;} return r==1 ? 1 : -1; }
int main(int argc, char **argv){
  int lmin = atoi(argv[1]), lmax = atoi(argv[2]);
  for (int l = lmin; l <= lmax; l++){
    double c = pow(2.0, l) * (l / 2.0 - 1 + pow(2.0, -l)) + l; uint64_t cut = (uint64_t)(c * c) + 1;
    uint64_t best = 0; int count = 0;
    for (uint64_t p = 7; p <= cut; p += 8){ if (p <= (uint64_t)l || !isprime(p)) continue;
      int same = 1; for (int t = 2; t < l; t++) if (chi(t, p) != chi(1, p)) same = 0;
      if (same) continue;
      int run = 0, prev = 0, bad = 0;
      for (uint64_t a = 1; a < p; a++){ int x = chi(a, p); run = (x == prev) ? run + 1 : 1; prev = x; if (run >= l){ bad = 1; break; } }
      if (!bad){ best = p; count++; if (count <= 40) printf("l=%d p=%llu\n", l, (unsigned long long)p); }
    }
    printf("RESULT7 l=%d cutoff=%llu qualifying=%d largest=%llu  =>  (l-1)p+2 = %llu\n", l, (unsigned long long)cut, count,
           (unsigned long long)best, (unsigned long long)((l-1)*best+2));
    fflush(stdout);
  }
  return 0;
}
