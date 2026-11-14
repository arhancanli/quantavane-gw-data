#!/usr/bin/env python3
"""Cube runner for the GW(4;4,4) lane (12 Nov 2026; FIFO streaming adapted from the foundations lane's cuberun.py).

usage: run44.py --base BASE.cnf --cubes CUBES.txt --log RUN.log --work DIR --n N --R R
                [--jobs J] [--cpu-limit SEC] [--no-proof] [--tags-file F] [--stop-file F]

CUBES.txt: one cube per line, "TAG lit lit ...".  The cube CNF is BASE plus one unit clause per literal, appended
after BASE's clauses (so BASE's clause ids are unchanged).  With proofs (default) CaDiCaL 3.0.1 writes its LRAT proof
(--lrat=true --binary=false --vivifyinst=false) into a named FIFO; this script hashes it (SHA-256), counts its bytes
and streams it into `lratcheck --skip-satisfied-hints CUBE.cnf /dev/stdin`, so no proof is ever stored on disk.
A cube is UNSAT_CHECKED only if CaDiCaL exits 20 AND the checker prints "s VERIFIED UNSAT" and exits 0.
SAT (exit 10): the model is decoded (x(i,c) = i*R + c + 1) and the colouring is checked by two separate programs
(../k4/check_k4.py and the C checker ../k5/check_k5); the colouring is kept in WORK/sat/TAG.txt.
Each solver gets RLIMIT_CPU = --cpu-limit CPU seconds (pauses by the load governor do not count): TIMEOUT.
Log lines: START tag ... / FINISH tag status=STATUS cpu=... wall=... proof_bytes=... proof_sha256=... cnf_sha256=...
Resumable: tags with a FINISH line of final status are skipped.  --fifo-cnf: the cube CNF is never written to disk;
it is streamed into two named pipes (one for CaDiCaL, one for the checker); its sha256 is computed from the same bytes.  --no-proof: plain solve (for time sampling only;
its UNSAT answers are status UNSAT_NOPROOF and count for nothing).
"""
import argparse, datetime, hashlib, os, resource, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = {"UNSAT_CHECKED", "UNSAT_CHECK_FAILED", "UNSAT_NOPROOF", "SAT_VERIFIED", "SAT_VERIFY_FAILED", "TIMEOUT"}
CAD = os.environ.get("CADICAL", "cadical")
CHK = os.environ.get("LRATCHECK", os.path.join(os.path.dirname(HERE), "lratcheck"))
PY = sys.executable

def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class Log:
    def __init__(self, path):
        self.path, self.lock = path, threading.Lock()
    def write(self, line):
        with self.lock:
            with open(self.path, "a") as fh:
                fh.write(line + "\n"); fh.flush(); os.fsync(fh.fileno())

def finished(path):
    done = set()
    if os.path.exists(path):
        for line in open(path):
            p = line.split()
            if len(p) >= 3 and p[0] == "FINISH" and p[2].startswith("status=") and p[2][7:] in FINAL:
                done.add(p[1])
    return done

def decode(outfile, n, R):
    m = set()
    for line in open(outfile):
        if line.startswith("v"):
            m.update(int(t) for t in line.split()[1:] if int(t) > 0)
    return "".join(str(next(c for c in range(R) if i * R + c + 1 in m)) for i in range(n))

def verify(col, work, tag, k=4, l=4, R=4):
    sd = os.path.join(work, "sat"); os.makedirs(sd, exist_ok=True)
    fn = os.path.join(sd, tag + ".txt")
    open(fn, "w").write(col + "\n")
    a = subprocess.run([PY, "-I", os.path.join(HERE, "..", "k4", "check_k4.py"), str(k), str(l), col],
                       capture_output=True, text=True).stdout.strip()
    b = subprocess.run([os.path.join(HERE, "check_k5"), str(k), str(l)], input=col + "\n",
                       capture_output=True, text=True).stdout.strip()
    ok = a.endswith("GOOD") and b.endswith("GOOD") and f"colours={R}" in a
    return ok, a.replace(" ", "_"), b.replace(" ", "_")

def run_cube(a, hdr, body, tag, lits, log):
    nv, nc = hdr
    cnf = os.path.join(a.work, tag + ".cnf"); fifo = os.path.join(a.work, tag + ".fifo")
    out = os.path.join(a.work, tag + ".out")
    h = hashlib.sha256()
    head = f"p cnf {nv} {nc + len(lits)}\n".encode(); tail = "".join(f"{l} 0\n" for l in lits).encode()
    h.update(head); h.update(body); h.update(tail)
    cnf_chk = cnf
    if getattr(a, "fifo_cnf", False):
        # no disk writes: the cube CNF is streamed into two named pipes, one read by CaDiCaL, one by the checker
        cnf_chk = cnf + ".chk"
        for f in (cnf, cnf_chk):
            if os.path.exists(f): os.unlink(f)
            os.mkfifo(f)
        def feed(path):
            try:
                with open(path, "wb") as fh: fh.write(head); fh.write(body); fh.write(tail)
            except (BrokenPipeError, OSError): pass
        for f in (cnf, cnf_chk) if not a.no_proof else (cnf,):
            threading.Thread(target=feed, args=(f,), daemon=True).start()
    else:
        with open(cnf, "wb") as fh: fh.write(head); fh.write(body); fh.write(tail)
    cnf_sha = h.hexdigest()
    log.write(f"START {tag} nlits={len(lits)} lits={','.join(map(str, lits)) or '-'} utc={utc()}")
    t0 = time.time(); lim = a.cpu_limit
    def pre():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if lim: resource.setrlimit(resource.RLIMIT_CPU, (lim, lim + 60))
        os.nice(10)
    st = {"opened": False, "bytes": 0, "sha": hashlib.sha256(), "broken": False}
    chk = None
    if a.no_proof:
        cad = subprocess.Popen([CAD, "-q", cnf], stdout=open(out, "wb"), stderr=subprocess.STDOUT, preexec_fn=pre)
    else:
        if os.path.exists(fifo): os.unlink(fifo)
        os.mkfifo(fifo)
        chk = subprocess.Popen([CHK, "--skip-satisfied-hints", cnf_chk, "/dev/stdin"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=lambda: os.nice(10))
        cad = subprocess.Popen([CAD, "-q", "--lrat=true", "--binary=false", "--vivifyinst=false", cnf, fifo],
                               stdout=open(out, "wb"), stderr=subprocess.STDOUT, preexec_fn=pre)
        def pump():
            with open(fifo, "rb", buffering=0) as f:
                st["opened"] = True
                while True:
                    b = f.read(1 << 20)
                    if not b: break
                    st["sha"].update(b); st["bytes"] += len(b)
                    if not st["broken"]:
                        try: chk.stdin.write(b)
                        except (BrokenPipeError, OSError): st["broken"] = True
            try: chk.stdin.close()
            except (BrokenPipeError, OSError): pass
        th = threading.Thread(target=pump, daemon=True); th.start()
    _, status, ru = os.wait4(cad.pid, 0)
    rc = os.waitstatus_to_exitcode(status); cpu = ru.ru_utime + ru.ru_stime
    verdict, info = "none", "-"
    if chk is not None:
        if not st["opened"]:
            try:
                fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK); os.close(fd)
            except OSError: pass
        th.join()
        txt = chk.stdout.read().decode(errors="replace"); chk.wait()
        os.unlink(fifo)
        v = [l for l in txt.splitlines() if l.startswith("s ")]; verdict = v[-1] if v else "none"
        info = " | ".join(l.strip() for l in txt.splitlines() if l.startswith("c ")).replace(" ", "_") or "-"
    wall = time.time() - t0
    extra = ""
    if rc == 20:
        if a.no_proof: status_s = "UNSAT_NOPROOF"
        else: status_s = "UNSAT_CHECKED" if (verdict == "s VERIFIED UNSAT" and chk.returncode == 0) else "UNSAT_CHECK_FAILED"
    elif rc == 10:
        col = decode(out, a.n, a.R); ok, c1, c2 = verify(col, a.work, tag, getattr(a, "k", 4), getattr(a, "l", 4), a.R)
        status_s = "SAT_VERIFIED" if ok else "SAT_VERIFY_FAILED"; extra = f" check1={c1} check2={c2}"
    elif cpu >= (lim or 10 ** 9) - 5 or rc in (-24, 0):
        status_s = "TIMEOUT"
    else:
        status_s = "ERROR"; extra = f" rc={rc}"
    log.write(f"FINISH {tag} status={status_s} cpu={cpu:.1f} wall={wall:.1f} proof_bytes={st['bytes']} "
              f"proof_sha256={st['sha'].hexdigest() if st['bytes'] else '-'} cnf_sha256={cnf_sha} "
              f"checker={verdict.replace(' ', '_')} info={info}{extra} utc={utc()}")
    for f in (cnf, out, cnf + ".chk"):
        if (status_s != "ERROR" or getattr(a, "fifo_cnf", False)) and os.path.exists(f): os.unlink(f)
    return status_s

def main():
    ap = argparse.ArgumentParser()
    for k in ("--base", "--cubes", "--log", "--work"): ap.add_argument(k, required=True)
    ap.add_argument("--n", type=int, required=True); ap.add_argument("--R", type=int, default=4)
    ap.add_argument("--k", type=int, default=4); ap.add_argument("--l", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--cpu-limit", type=int, default=0)
    ap.add_argument("--no-proof", action="store_true"); ap.add_argument("--tags-file", default=None)
    ap.add_argument("--stop-file", default=None)
    ap.add_argument("--fifo-cnf", action="store_true", help="stream cube CNFs through named pipes (no disk writes)")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    raw = open(a.base, "rb").read()
    lines = raw.split(b"\n")
    k = next(i for i, l in enumerate(lines) if l.startswith(b"p cnf"))
    hdr = tuple(map(int, lines[k].split()[2:4])); body = b"\n".join(lines[k + 1:])
    if not body.endswith(b"\n"): body += b"\n"
    log = Log(a.log); done = finished(a.log)
    want = set(open(a.tags_file).read().split()) if a.tags_file else None
    q = []
    for line in open(a.cubes):
        p = line.split()
        if p and p[0] not in done and (want is None or p[0] in want): q.append((p[0], [int(x) for x in p[1:]]))
    log.write(f"RUN_START cubes={len(q)} jobs={a.jobs} cpu_limit={a.cpu_limit} proof={not a.no_proof} base={a.base} "
              f"pid={os.getpid()} utc={utc()}")
    lock = threading.Lock(); state = {"sat": False}
    def worker():
        while True:
            with lock:
                if state["sat"] or not q or (a.stop_file and os.path.exists(a.stop_file)): return
                tag, lits = q.pop(0)
            try: s = run_cube(a, hdr, body, tag, lits, log)
            except Exception as e:
                log.write(f"FINISH {tag} status=ERROR exc={type(e).__name__}:{e} utc={utc()}"); s = "ERROR"
            if s.startswith("SAT"):
                with lock: state["sat"] = True
    ths = [threading.Thread(target=worker) for _ in range(a.jobs)]
    for t in ths: t.start()
    for t in ths: t.join()
    log.write(f"RUN_END left={len(q)} sat={state['sat']} utc={utc()}")

if __name__ == "__main__":
    main()
