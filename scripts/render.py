from pathlib import Path
import json,subprocess,os
r=Path(__file__).resolve().parents[1];m=json.loads((r/'package.json').read_text())
def render():
    text=[]
    for chart in m['charts']:
        release=chart.split('.')[0] if chart=='fleet-crd.tgz' else m['key']
        text.append(subprocess.check_output(['helm','template',release,str(r/'vendor'/chart),'--namespace',m['namespace'],'--include-crds','--api-versions','apiregistration.k8s.io/v1','--kube-version','1.35.0','-f',str(r/'values.yaml')],text=True))
    for key,file in [('flux','flux-install.yaml'),('rollouts','rollouts-install.yaml')]:
        if m['key']==key:text.append((r/'vendor'/file).read_text())
    return '\n---\n'.join(text) or '# Use the documented native bootstrap procedure; no fabricated controller chart.\n'
if __name__=='__main__':
    (r/'rendered/install.yaml').write_text(render())
    print('Rendered files only; no cluster accessed.')
