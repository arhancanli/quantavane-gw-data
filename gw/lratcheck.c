/* lratcheck.c -- our own LRAT proof checker (Quantavane foundations lane, 2026-11-11).
 *
 * usage: lratcheck FORMULA.cnf PROOF.lrat
 * Checks every addition step of an ASCII LRAT proof (RUP hints, and RAT steps with negative hints)
 * against the clauses of the formula (ids 1..m in file order) and earlier steps, applies deletions,
 * and prints "s VERIFIED UNSAT" only if every step checks and the empty clause is derived.
 * Strict: a hint that is satisfied, non-unit and non-falsified, or missing is an error.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef long long ll;

static void die(const char *msg, ll a, ll b) {
  fprintf(stderr, "c ERROR: %s (%lld, %lld)\n", msg, a, b);
  printf("s NOT VERIFIED\n");
  exit(1);
}

/* ---------- buffered integer reader ---------- */
typedef struct { FILE *f; char *buf; size_t len, pos; int eof; } Reader;
static Reader *ropen(const char *path) {
  Reader *r = calloc(1, sizeof(Reader));
  r->f = fopen(path, "rb");
  if (!r->f) die("cannot open file", 0, 0);
  r->buf = malloc(1 << 22);
  return r;
}
static int rgetc(Reader *r) {
  if (r->pos == r->len) {
    if (r->eof) return EOF;
    r->len = fread(r->buf, 1, 1 << 22, r->f);
    r->pos = 0;
    if (r->len == 0) { r->eof = 1; return EOF; }
  }
  return (unsigned char) r->buf[r->pos++];
}
/* returns 1 and sets *out for an integer token, 2 for the token 'd', 0 at EOF; skips 'c' comment lines */
static int rtoken(Reader *r, ll *out) {
  int c;
  for (;;) {
    c = rgetc(r);
    if (c == EOF) return 0;
    if (c == ' ' || c == '\n' || c == '\t' || c == '\r') continue;
    if (c == 'c') { while (c != '\n' && c != EOF) c = rgetc(r); continue; }
    break;
  }
  if (c == 'd') return 2;
  if (c == 'p') { /* 'p cnf V C' header: return special marker */
    return 3;
  }
  int neg = 0;
  if (c == '-') { neg = 1; c = rgetc(r); }
  if (c < '0' || c > '9') die("bad character in input", c, 0);
  ll v = 0;
  while (c >= '0' && c <= '9') { v = v * 10 + (c - '0'); c = rgetc(r); }
  *out = neg ? -v : v;
  return 1;
}

/* ---------- clause store: hash map id -> arena offset ---------- */
static int *arena; static size_t acap, alen, awaste;
static uint64_t *hkeys; static size_t *hvals; static size_t hcap, hcount, hused; /* key 0 empty, key ~0 tomb */
#define TOMB (~(uint64_t)0)
static size_t hslot(uint64_t k) { k ^= k >> 33; k *= 0xff51afd7ed558ccdULL; k ^= k >> 33; return (size_t)(k & (hcap - 1)); }
static void hinit(size_t cap) { hcap = cap; hkeys = calloc(hcap, 8); hvals = calloc(hcap, sizeof(size_t)); hcount = hused = 0; }
static void hput_raw(uint64_t k, size_t v) {
  size_t i = hslot(k);
  while (hkeys[i] != 0 && hkeys[i] != TOMB) i = (i + 1) & (hcap - 1);
  if (hkeys[i] == 0) hused++;
  hkeys[i] = k; hvals[i] = v; hcount++;
}
static void hrehash(size_t ncap) {
  uint64_t *ok = hkeys; size_t *ov = hvals; size_t oc = hcap;
  hinit(ncap);
  for (size_t i = 0; i < oc; i++) if (ok[i] != 0 && ok[i] != TOMB) hput_raw(ok[i], ov[i]);
  free(ok); free(ov);
}
static long hfind(uint64_t k) {
  size_t i = hslot(k);
  while (hkeys[i] != 0) { if (hkeys[i] == k) return (long) i; i = (i + 1) & (hcap - 1); }
  return -1;
}
static void store_clause(ll id, const int *lits, int n) {
  if (id <= 0) die("non-positive clause id", id, 0);
  if (hfind((uint64_t) id) >= 0) die("duplicate clause id", id, 0);
  if (alen + n + 1 > acap) { while (alen + n + 1 > acap) acap = acap ? acap * 2 : (1 << 20); arena = realloc(arena, acap * sizeof(int)); if (!arena) die("out of memory (arena)", 0, 0); }
  size_t off = alen; arena[alen++] = n; memcpy(arena + alen, lits, n * sizeof(int)); alen += n;
  if ((hused + 1) * 2 > hcap) { size_t nc = 1 << 16; while (nc < (hcount + 1) * 4) nc <<= 1; hrehash(nc); }
  hput_raw((uint64_t) id, off);
}
static void delete_clause(ll id) {
  long s = hfind((uint64_t) id);
  if (s < 0) die("deleting unknown clause", id, 0);
  awaste += arena[hvals[s]] + 1;
  hkeys[s] = TOMB; hcount--;
}
static void compact(void) {
  int *na = malloc((alen - awaste + 16) * sizeof(int)); size_t nl = 0;
  for (size_t i = 0; i < hcap; i++) if (hkeys[i] != 0 && hkeys[i] != TOMB) {
    int n = arena[hvals[i]]; memcpy(na + nl, arena + hvals[i], (n + 1) * sizeof(int)); hvals[i] = nl; nl += n + 1;
  }
  free(arena); arena = na; acap = alen - awaste + 16; alen = nl; awaste = 0;
  hrehash(hcap);
}

/* ---------- assignment ---------- */
static signed char *val; static int nvars; static int *trail; static size_t tlen, tcap;
static void ensure_var(int v) {
  if (v <= nvars) return;
  int nv = nvars ? nvars : 1024; while (nv < v) nv *= 2;
  val = realloc(val, nv + 1); memset(val + nvars + 1, 0, nv - nvars); nvars = nv;
}
static inline int litval(int l) { int v = l > 0 ? l : -l; if (v > nvars) return 0; int x = val[v]; return l > 0 ? x : -x; }
static inline void assign(int l) { int v = l > 0 ? l : -l; ensure_var(v); val[v] = l > 0 ? 1 : -1;
  if (tlen == tcap) { tcap = tcap ? tcap * 2 : 1024; trail = realloc(trail, tcap * sizeof(int)); } trail[tlen++] = v; }
static void undo_to(size_t mark) { while (tlen > mark) val[trail[--tlen]] = 0; }

/* 11 Nov 2026: optional --skip-satisfied-hints. CaDiCaL 3.0.1 sometimes lists a hint clause that is already satisfied
   (drat-trim warns "hint already satisfied" and accepts). Skipping such a clause is sound: it assigns nothing, and the
   remaining hints must still reach the conflict. Off by default (strict); every skip is counted and reported. */
static int skip_sat = 0; static ll nskipped = 0; static FILE *cleanf = NULL; /* --write-clean OUT: proof without satisfied/unused hints */
/* process one positive hint: returns 1 on conflict, 0 if a unit was assigned (or a satisfied hint skipped); dies otherwise */
static int use_hint(ll h, ll step) {
  long s = hfind((uint64_t) h);
  if (s < 0) die("hint refers to unknown clause (step, hint)", step, h);
  int *c = arena + hvals[s]; int n = c[0]; int unassigned = 0, ulit = 0;
  for (int i = 1; i <= n; i++) {
    int x = litval(c[i]);
    if (x == 1) { if (skip_sat) { nskipped++; return 0; } die("hint clause is satisfied (step, hint)", step, h); }
    if (x == 0) { if (unassigned == 0 || c[i] != ulit) { unassigned++; ulit = c[i]; } }
  }
  if (unassigned == 0) return 1;
  if (unassigned > 1) die("hint clause is not unit (step, hint)", step, h);
  assign(ulit);
  return 0;
}

int main(int argc, char **argv) {
  if (argc == 4 && strcmp(argv[1], "--skip-satisfied-hints") == 0) { skip_sat = 1; argv++; argc--; }
  if (argc == 5 && strcmp(argv[1], "--write-clean") == 0) { skip_sat = 1; cleanf = fopen(argv[2], "w"); if (!cleanf) die("cannot open clean output", 0, 0);
    setvbuf(cleanf, NULL, _IOFBF, 1 << 24); argv += 2; argc -= 2; }
  if (argc != 3) { fprintf(stderr, "usage: lratcheck [--skip-satisfied-hints | --write-clean OUT.lrat] FORMULA.cnf PROOF.lrat\n"); return 2; }
  hinit(1 << 16);
  /* read formula */
  Reader *r = ropen(argv[1]); ll x; int t; ll nclauses = 0, id = 0;
  int *lits = NULL; size_t lcap = 0, ln = 0;
  int got_header = 0;
  while ((t = rtoken(r, &x)) != 0) {
    if (t == 3) { /* skip "p cnf" line */ int c; while ((c = rgetc(r)) != '\n' && c != EOF); got_header = 1; continue; }
    if (t != 1) die("unexpected token in formula", t, 0);
    if (x == 0) { id++; store_clause(id, lits, (int) ln); ln = 0; nclauses++; }
    else { if (ln == lcap) { lcap = lcap ? lcap * 2 : 1024; lits = realloc(lits, lcap * sizeof(int)); } lits[ln++] = (int) x; ensure_var((int) (x > 0 ? x : -x)); }
  }
  if (!got_header) die("formula has no header", 0, 0);
  fprintf(stderr, "c formula: %lld clauses\n", nclauses);
  /* read proof */
  Reader *p = ropen(argv[2]);
  ll steps = 0, dels = 0, rats = 0; int empty_derived = 0;
  ll *hints = NULL; size_t hcap2 = 0, hn = 0; char *keep = NULL; size_t keepcap = 0;
  ll last_id = id;
  for (;;) {
    t = rtoken(p, &x);
    if (t == 0) break;
    if (t != 1) die("proof line must start with an id", t, 0);
    ll sid = x;
    t = rtoken(p, &x);
    if (t == 2) { /* deletion */
      if (cleanf) fprintf(cleanf, "%lld d", sid);
      for (;;) { t = rtoken(p, &x); if (t != 1) die("bad deletion line", sid, 0); if (x == 0) break; delete_clause(x); dels++; if (cleanf) fprintf(cleanf, " %lld", x); }
      if (cleanf) fprintf(cleanf, " 0\n");
      if (awaste > 1000000 && awaste * 2 > alen) compact();
      continue;
    }
    if (t != 1) die("bad addition line", sid, 0);
    if (sid <= last_id) die("addition ids must increase (id, last)", sid, last_id);
    ln = 0;
    while (x != 0) {
      if (ln == lcap) { lcap = lcap ? lcap * 2 : 1024; lits = realloc(lits, lcap * sizeof(int)); }
      lits[ln++] = (int) x; ensure_var((int) (x > 0 ? x : -x));
      t = rtoken(p, &x); if (t != 1) die("bad literal in addition", sid, 0);
    }
    hn = 0;
    for (;;) { t = rtoken(p, &x); if (t != 1) die("bad hint list", sid, 0); if (x == 0) break;
      if (hn == hcap2) { hcap2 = hcap2 ? hcap2 * 2 : 1024; hints = realloc(hints, hcap2 * sizeof(ll)); } hints[hn++] = x; }
    /* check the step */
    size_t mark = tlen; int taut = 0;
    for (size_t i = 0; i < ln; i++) {
      int v = litval(lits[i]);
      if (v == 1) { taut = 1; break; }        /* clause contains l and -l */
      if (v == 0) assign(-lits[i]);
    }
    int conflict = taut; size_t k = 0;
    if (cleanf) { if (hn > keepcap) { keepcap = hn; keep = realloc(keep, keepcap); } memset(keep, 0, hn); }
    while (!conflict && k < hn && hints[k] > 0) { ll before = nskipped; conflict = use_hint(hints[k], sid); if (cleanf && nskipped == before) keep[k] = 1; k++; }
    if (cleanf && conflict) { fprintf(cleanf, "%lld", sid); for (size_t i = 0; i < ln; i++) fprintf(cleanf, " %d", lits[i]); fprintf(cleanf, " 0");
      for (size_t i = 0; i < hn; i++) if (keep[i]) fprintf(cleanf, " %lld", hints[i]); fprintf(cleanf, " 0\n"); }
    if (!conflict) {
      if (cleanf) die("--write-clean does not handle RAT steps (step)", sid, 0);
      if (k == hn) die("RUP hints do not reach a conflict (step)", sid, 0);
      /* RAT step: pivot = first literal; every active clause containing -pivot must be refuted */
      if (ln == 0) die("RAT step with empty clause", sid, 0);
      rats++;
      int piv = lits[0];
      size_t base = tlen;
      /* collect the listed candidates */
      ll *listed = NULL; size_t nl = 0;
      while (k < hn) {
        if (hints[k] > 0) die("expected negative hint (step, hint)", sid, hints[k]);
        ll j = -hints[k]; k++;
        listed = realloc(listed, (nl + 1) * sizeof(ll)); listed[nl++] = j;
        long s = hfind((uint64_t) j); if (s < 0) die("RAT hint refers to unknown clause", sid, j);
        int *c = arena + hvals[s]; int n = c[0], has = 0, sat = 0;
        for (int i = 1; i <= n; i++) {
          if (c[i] == -piv) { has = 1; continue; }
          int v = litval(c[i]);
          if (v == 1) { sat = 1; } else if (v == 0) assign(-c[i]);
        }
        if (!has) die("RAT candidate does not contain -pivot", sid, j);
        int conf = sat;
        while (!conf && k < hn && hints[k] > 0) { conf = use_hint(hints[k], sid); k++; }
        while (k < hn && hints[k] > 0) k++; /* extra hints after conflict are ignored */
        if (!conf) die("RAT candidate not refuted (step, candidate)", sid, j);
        undo_to(base);
      }
      /* every active clause with -pivot must be listed, unless its resolvent is a tautology */
      for (size_t i = 0; i < hcap; i++) if (hkeys[i] != 0 && hkeys[i] != TOMB) {
        int *c = arena + hvals[i]; int n = c[0], has = 0;
        for (int q = 1; q <= n; q++) if (c[q] == -piv) { has = 1; break; }
        if (!has) continue;
        int found = 0; for (size_t q = 0; q < nl; q++) if ((uint64_t) listed[q] == hkeys[i]) { found = 1; break; }
        if (found) continue;
        int tautr = 0; for (int q = 1; q <= n && !tautr; q++) if (c[q] != -piv) for (size_t w = 0; w < ln; w++) if (lits[w] == -c[q]) { tautr = 1; break; }
        if (!tautr) die("RAT step misses a candidate clause (step, clause)", sid, (ll) hkeys[i]);
      }
      free(listed);
    }
    undo_to(mark);
    store_clause(sid, lits, (int) ln);
    last_id = sid;
    steps++;
    if (ln == 0) { empty_derived = 1; break; }
  }
  fprintf(stderr, "c checked %lld additions (%lld RAT), %lld deletions\n", steps, rats, dels);
  if (skip_sat) fprintf(stderr, "c skipped %lld satisfied hint clauses\n", nskipped);
  if (cleanf) { fclose(cleanf); fprintf(stderr, "c wrote clean proof (satisfied and unused hints dropped)\n"); }
  if (!empty_derived) die("proof ends without the empty clause", steps, 0);
  printf("s VERIFIED UNSAT\n");
  return 0;
}
