#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess,time,os
from pathlib import Path

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    return {"rc":p.returncode,"stdout":p.stdout[-4000:],"stderr":p.stderr[-4000:]}

ap=argparse.ArgumentParser()
ap.add_argument("--task-dir",required=True)
ap.add_argument("--variant",required=True)
ap.add_argument("--seed",type=int,default=0)
ap.add_argument("--candidate-patch")
ap.add_argument("--receipt-out",required=True)
a=ap.parse_args()
td=Path(a.task_dir).resolve()
spec=json.load(open(td/"task.json"))
repo=td/"repo"
start=time.time()
before=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
status_before=subprocess.check_output(["git","status","--porcelain"],cwd=repo,text=True)
if status_before.strip():
    raise SystemExit("DIRTY_REPO_BEFORE")
patch_sha=None
invalid_writes=0
if a.candidate_patch:
    pp=Path(a.candidate_patch).resolve()
    patch_sha=sha(pp)
    pr=run(["git","apply","--check",str(pp)],repo)
    if pr["rc"]!=0:
        invalid_writes+=1
        apply_ok=False
    else:
        run(["git","apply",str(pp)],repo); apply_ok=True
else:
    apply_ok=True
stale_guard="GREEN"
if spec.get("stale_injection"):
    marker=repo/".benchmark_intervening_change"
    marker.write_text("external writer\n")
    subprocess.run(["git","add",str(marker.name)],cwd=repo,check=True)
    subprocess.run(["git","-c","user.name=benchmark","-c","user.email=benchmark@example.invalid","commit","-m","intervening change"],cwd=repo,check=True,capture_output=True)
    stale_guard="STALE"
tests=run(["python3","-m","unittest","discover","-q"],repo) if apply_ok else {"rc":99,"stdout":"","stderr":"patch apply failed"}
test_verdict="GREEN" if tests["rc"]==0 else "RED"
verifier_verdict="GREEN" if (apply_ok and invalid_writes==0) else "RED"
if stale_guard!="GREEN":
    promotion="STALE"
elif test_verdict=="GREEN" and verifier_verdict=="GREEN":
    promotion="GREEN"
else:
    promotion="RED"
after=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
rec={
 "schema":"FAIL_CLOSED_SWE_ATTEMPT_RECEIPT_V1",
 "task_id":spec["task_id"],"variant":a.variant,"seed":a.seed,
 "repo_commit_before":before,"repo_commit_after":after,
 "proposed_patch_sha256":patch_sha,
 "test_verdict":test_verdict,"stale_guard_verdict":stale_guard,
 "verifier_verdict":verifier_verdict,"promotion_verdict":promotion,
 "invalid_writes":invalid_writes,"duplicate_work":0,"rollbacks":0,"tool_calls":0,
 "wall_seconds":round(time.time()-start,6),
 "tests":tests
}
Path(a.receipt_out).write_text(json.dumps(rec,sort_keys=True,indent=2)+"\n")
print(json.dumps({"status":"DONE","promotion":promotion,"receipt":a.receipt_out},sort_keys=True))
