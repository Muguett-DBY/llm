import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument("phase",choices=("before","after"))
parser.add_argument("--output",type=Path,required=True)
parser.add_argument("--baseline",type=Path)
args=parser.parse_args()
files=["tests/test_keys.py","tests/test_llm_logs.py"]
p=subprocess.run([sys.executable,"-m","ruff","check",*files,"--output-format","json"],capture_output=True,text=True,encoding="utf-8")
assert p.returncode in (0,1),(p.returncode,p.stdout,p.stderr)
diagnostics=json.loads(p.stdout)
identities=[]
for d in diagnostics:
    path=Path(d["filename"])
    lines=path.read_text(encoding="utf-8").splitlines()
    excerpt="\n".join(lines[d["location"]["row"]-1:d["end_location"]["row"]])
    identities.append([path.relative_to(Path.cwd()).as_posix(),d["code"],d["message"],excerpt])
report={"phase":args.phase,"ruffExitCode":p.returncode,"diagnosticCount":len(diagnostics),"diagnosticIdentities":identities,"scope":files,"fullRuffCheckPassed":p.returncode==0}
if args.phase=="after":
    before=json.loads(args.baseline.read_text(encoding="utf-8"))
    assert Counter(tuple(x) for x in identities)==Counter(tuple(x) for x in before["diagnosticIdentities"]),(before,report)
    report["sameDiagnosticsAsBaseline"]=True
args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("LLM1538_LINT="+json.dumps(report,sort_keys=True))
