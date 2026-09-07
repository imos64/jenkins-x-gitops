from pathlib import Path
import tarfile,json,hashlib,argparse,shutil
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='Expand pinned upstream Jenkins X cluster template locally; no cluster or GitHub writes.')
p.add_argument('--output',type=Path,default=r/'site');a=p.parse_args()
assert not a.output.exists(), 'Refuse to overwrite an existing directory'
blob=r/'vendor/jx3-kubernetes.tar.gz'
meta=json.loads((r/'package.json').read_text());source=next(s for s in meta['sources'] if s['file']==str(blob.relative_to(r)))
assert hashlib.sha256(blob.read_bytes()).hexdigest()==source['sha256']
with tarfile.open(blob) as archive:
    members=archive.getmembers()
    for member in members:
        parts=Path(member.name).parts
        assert '..' not in parts and not Path(member.name).is_absolute()
        assert member.isdir() or member.isfile(), 'No archive links or device files allowed'
    a.output.mkdir(parents=True)
    for member in members:
        relative=Path(*Path(member.name).parts[1:])
        if str(relative)=='.':continue
        target=a.output/relative
        if member.isdir():target.mkdir(parents=True,exist_ok=True)
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.extractfile(member).read());target.chmod(member.mode & 0o777)
shutil.copy(r/'jx-requirements.yml',a.output/'jx-requirements.yml')
print('Template expanded. Replace site values and configure identities, secrets, storage, ingress and webhooks before bootstrapping Jenkins X.')
