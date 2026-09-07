from pathlib import Path
import json,hashlib,subprocess,yaml,sys,tempfile,os
from jsonschema import Draft4Validator
from render import render,r,m

def objects(text):return [o for o in yaml.safe_load_all(text) if o]
for s in m['sources']:assert hashlib.sha256((r/s['file']).read_bytes()).hexdigest()==s['sha256'],s['file']
for chart in m['charts']:subprocess.run(['helm','lint','--strict',str(r/'vendor'/chart),'-f',str(r/'values.yaml')],check=True)
text=render();assert text==(r/'rendered/install.yaml').read_text(),'Run make render'
installed=objects(text);samples=[]
for folder in ['examples','bootstrap','apps/demo']:
    for p in (r/folder).glob('*.yaml'):
        for o in objects(p.read_text()):
            # Tool configuration is not submitted to the Kubernetes API.
            if 'apiVersion' in o and o['apiVersion'] not in ['pipecd.dev/v1beta1','kustomize.config.k8s.io/v1beta1']:samples.append(o)
all_objects=installed+samples
schema_objects=list(all_objects)
if (r/'vendor/kluctl-crd.yaml').exists():schema_objects+=objects((r/'vendor/kluctl-crd.yaml').read_text())
crd_schema=json.loads((r/'vendor/kubernetes-crd-openapi.json').read_text());crd_schema['$ref']='#/components/schemas/io.k8s.apiextensions-apiserver.pkg.apis.apiextensions.v1.CustomResourceDefinition'
crd_validator=Draft4Validator(crd_schema);custom={}
for o in schema_objects:
    if o['kind']=='CustomResourceDefinition':
        crd_validator.validate(o)
        for v in o['spec']['versions']:
            custom[(o['spec']['group']+'/'+v['name'],o['spec']['names']['kind'])]=v['schema']['openAPIV3Schema']
    if o['kind']=='CompositeResourceDefinition':
        for v in o['spec']['versions']:custom[(o['spec']['group']+'/'+v['name'],o['spec']['names']['kind'])]=v['schema']['openAPIV3Schema']
def schemas(items):
    standard=[];count=0
    for o in items:
        if o['kind']=='CustomResourceDefinition':continue
        schema=custom.get((o['apiVersion'],o['kind']))
        if schema is not None:Draft4Validator(schema).validate(o);count+=1
        else:standard.append(o)
    if standard:subprocess.run([str(r/'.tools/kubeconform'),'-strict','-summary','-kubernetes-version','1.35.0'],input=yaml.safe_dump_all(standard),text=True,check=True)
    print('Custom resources checked against upstream schemas:',count)
schemas(all_objects)
def contract(o):
    s=o.get('spec',{});k=o.get('kind')
    if k=='Application':assert 'automated' not in s.get('syncPolicy',{})
    if k=='AppProject':assert s['sourceRepos']!=['*'] and not s['clusterResourceWhitelist']
    if k=='Kustomization' and o.get('apiVersion','').startswith('kustomize.toolkit'):assert s['prune'] is False and s['serviceAccountName']=='delivery-reconciler'
    if k=='Rollout':assert s['strategy']['blueGreen']['autoPromotionEnabled'] is False
    if k=='GitRepo':assert s['targets'][0]['clusterSelector']['matchLabels']=={'environment':'staging'}
    if k=='KluctlDeployment':assert not s['prune'] and not s['delete'] and 'git' in s['source']
    if k=='Deployment' and o['metadata']['name']=='delivery-demo':
        pod=s['template']['spec'];assert not pod['automountServiceAccountToken']
        assert all('@sha256:' in c['image'] and not c['securityContext']['allowPrivilegeEscalation'] for c in pod['containers'])
for o in samples:contract(o)
# Verify that unsafe policy regressions are actually rejected.
for bad in [{'kind':'AppProject','spec':{'sourceRepos':['*'],'clusterResourceWhitelist':[]}},{'kind':'Rollout','spec':{'strategy':{'blueGreen':{'autoPromotionEnabled':True}}}}]:
    try:contract(bad)
    except AssertionError:pass
    else:raise AssertionError('Unsafe mutation accepted')
if m['key']=='jx':
    subprocess.run([str(r/'.tools/jx-gitops'),'lint','--dir',str(r/'apps')],check=True)
    req=yaml.safe_load((r/'jx-requirements.yml').read_text());assert not req['spec']['autoUpdate']['enabled']
    assert [e['key'] for e in req['spec']['environments']]==['dev','staging','production']
    subprocess.run(['helm','lint','--strict',str(r/'charts/demo')],check=True)
    schemas(objects(subprocess.check_output(['helm','template','demo',str(r/'charts/demo'),'-n',m['demoNamespace']],text=True)))
if m['key']=='kluctl':
    for target in ['staging','production']:
        output=subprocess.check_output([str(r/'.tools/kluctl'),'render','--project-dir',str(r),'--target',target,'--offline-kubernetes','--print-all','--no-update-check'],text=True)
        schemas(objects(output))
if m['key']=='werf':
    output=subprocess.check_output([str(r/'.tools/werf'),'render','--stub-tags','--dev','--namespace',m['demoNamespace'],'--release','delivery-demo','--log-color-mode','off'],cwd=r,text=True)
    schemas(objects(output))
if m['key']=='pipecd':
    app=yaml.safe_load((r/'apps/demo/app.pipecd.yaml').read_text())
    assert [s['name'] for s in app['spec']['pipeline']['stages']]==['WAIT_APPROVAL','K8S_PRIMARY_ROLLOUT']
    assert all((r/'apps/demo'/f).is_file() for f in app['spec']['input']['manifests'])
    values=yaml.safe_load((r/'values.yaml').read_text());assert not values['secret']['create'] and not values['args']['insecure'] and not values['rbac']['create']
    config=yaml.safe_load((r/'examples/piped-config.yaml').read_text());assert config['spec']['pipedKeyFile']=='/etc/piped-secret/piped-key'
print('PASS: artifact hashes, exact rendering, Kubernetes schemas and delivery guardrails. No deployment was run.')
