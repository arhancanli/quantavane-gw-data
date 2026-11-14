/* Separate checker (k5 agent, 12 Nov 2026; shares no code with the encoders or constructions): for each colouring
   (one line of symbols 0-9a-zA-Z, one symbol per point of [1,n]; '#' lines are skipped and in a line with
   spaces only the last field is read) print n, the number of colours, the colour counts,
   the number of rainbow k-APs (k pairwise distinct colours) and of monochromatic l-APs (x, x+d, ..., d >= 1, inside
   [1,n]), and GOOD/BAD.  Usage: check_k5 k l < file   (or: echo STRING | check_k5 k l) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int val(int ch) {
  if (ch >= '0' && ch <= '9') return ch - '0';
  if (ch >= 'a' && ch <= 'z') return 10 + ch - 'a';
  if (ch >= 'A' && ch <= 'Z') return 36 + ch - 'A';
  return -1;
}
int main(int argc, char **argv) {
  if (argc != 3) { fprintf(stderr, "usage: check_k5 k l < colourings\n"); return 2; }
  int k = atoi(argv[1]), l = atoi(argv[2]);
  size_t cap = 1 << 20; char *line = malloc(cap); int *c = malloc(sizeof(int) * cap);
  int ch, n = 0, any = 0, comment = 0;
  for (;;) {
    ch = getchar();
    if (n == 0 && !comment && ch == '#') comment = 1;          /* '#' lines are comments */
    if (comment && ch != '\n' && ch != EOF) continue;
    if (ch == ' ' || ch == '\t') { n = 0; continue; }           /* "r n colouring": only the last field counts */
    if (ch == '\n' || ch == EOF) {
      comment = 0;
      if (n > 0) {
        long long rainbow = 0, mono = 0; long long cnt[62] = {0}; int ncol = 0;
        for (int i = 0; i < n; i++) cnt[c[i]]++;
        for (int v = 0; v < 62; v++) if (cnt[v]) ncol++;
        for (int a = 0; a < n; a++)
          for (int d = 1; a + d < n; d++) {
            if (a + (k - 1) * d < n) {
              int ok = 1;
              for (int i = 0; i < k && ok; i++) for (int j = i + 1; j < k; j++) if (c[a + i * d] == c[a + j * d]) { ok = 0; break; }
              if (ok) rainbow++;
            }
            if (a + (l - 1) * d < n) {
              int j; for (j = 1; j < l; j++) if (c[a + j * d] != c[a]) break;
              if (j == l) mono++;
            }
            if (a + (k - 1) * d >= n && a + (l - 1) * d >= n) break;
          }
        printf("n=%d colours=%d counts=[", n, ncol);
        int first = 1; for (int v = 0; v < 62; v++) if (cnt[v]) { printf(first ? "%lld" : ", %lld", cnt[v]); first = 0; }
        printf("] rainbow%d=%lld mono%d=%lld %s\n", k, rainbow, l, mono, (rainbow == 0 && mono == 0) ? "GOOD" : "BAD");
        any = 1;
      }
      n = 0;
      if (ch == EOF) break;
      continue;
    }
    int v = val(ch);
    if (v < 0) continue;
    if ((size_t)n >= cap) { cap *= 2; c = realloc(c, sizeof(int) * cap); }
    c[n++] = v;
  }
  free(line); free(c);
  return any ? 0 : 1;
}
