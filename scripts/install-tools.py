from pathlib import Path
import hashlib,io,tarfile,urllib.request
root=Path(__file__).resolve().parents[1]
tool=root/'.tools/kubeconform'
if not tool.exists():
    url='https://github.com/yannh/kubeconform/releases/download/v0.8.0/kubeconform-linux-amd64.tar.gz'
    blob=urllib.request.urlopen(url,timeout=60).read()
    assert hashlib.sha256(blob).hexdigest()=='9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883'
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as archive:
        binary=archive.extractfile('kubeconform').read()
    tool.parent.mkdir(parents=True,exist_ok=True);tool.write_bytes(binary);tool.chmod(0o755)

import json
for entry in json.loads((root/'package.json').read_text())['tools']:
    target=root/'.tools'/entry['name']
    if target.exists():continue
    blob=urllib.request.urlopen(entry['url'],timeout=120).read()
    assert hashlib.sha256(blob).hexdigest()==entry['sha256']
    if entry['archive']:
        with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as archive:
            member=next(m for m in archive.getmembers() if m.isfile() and m.name.split('/')[-1]==entry['name'])
            blob=archive.extractfile(member).read()
    target.write_bytes(blob);target.chmod(0o755)
