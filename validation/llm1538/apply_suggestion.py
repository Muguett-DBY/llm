import hashlib
import json
from pathlib import Path
import sys

spec=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for item in spec:
    path=Path(item["path"])
    original=path.read_text(encoding="utf-8")
    assert hashlib.sha256(original.encode()).hexdigest()==item["beforeSha256"],str(path)
    assert original.count(item["old"])==1,str(path)
    updated=original.replace(item["old"],item["new"])
    assert hashlib.sha256(updated.encode()).hexdigest()==item["afterSha256"]
    path.write_text(updated,encoding="utf-8")
    print("Proposed fixture change:",path,item["afterSha256"])
