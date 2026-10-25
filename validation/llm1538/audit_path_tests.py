import argparse
import json
import os
from pathlib import Path
import platform
import sys

parser=argparse.ArgumentParser()
parser.add_argument("phase",choices=("before","after"))
parser.add_argument("--output",type=Path,required=True)
parser.add_argument("--basetemp",required=True)
args=parser.parse_args()
normalize=lambda p: os.path.normcase(os.path.abspath(p))
targets={normalize("/tmp/llm-keys-test"),normalize("/tmp/llm-user-path")}
attempts=[]
existed={p:Path(p).exists() for p in targets}
def audit(event,values):
    if event=="os.mkdir" and normalize(values[0]) in targets:
        attempts.append(normalize(values[0]))
sys.addaudithook(audit)
import pytest
class Results:
    def __init__(self):self.reports=[]
    def pytest_runtest_logreport(self,report):
        if report.when=="call":self.reports.append({"nodeid":report.nodeid,"outcome":report.outcome})
results=Results()
status=pytest.main(["tests/test_keys.py::test_keys_in_user_path","tests/test_llm_logs.py::test_logs_path","-q","--basetemp",args.basetemp],plugins=[results])
report={"phase":args.phase,"platform":sys.platform,"python":platform.python_version(),"exitCode":int(status),"tests":results.reports,"rootTargets":sorted(targets),"mkdirAttempts":attempts,"rootTargetsExistedBefore":existed,"rootTargetsExistAfter":{p:Path(p).exists() for p in targets},"observationsDoNotChangeFilesystemCalls":True}
args.output.write_text(json.dumps(report,indent=2)+"\n")
print("LLM1538_RESULT="+json.dumps(report,sort_keys=True))
assert status==0 and len(results.reports)==4 and all(x["outcome"]=="passed" for x in results.reports),report
if args.phase=="before":
    assert set(attempts)==targets and all(Path(p).is_dir() for p in targets),report
else:
    assert not attempts,report
