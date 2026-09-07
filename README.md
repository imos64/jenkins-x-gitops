# Jenkins X GitOps

[![Validate](https://github.com/imos64/jenkins-x-gitops/actions/workflows/validate.yml/badge.svg)](https://github.com/imos64/jenkins-x-gitops/actions/workflows/validate.yml)

**Developer CI/CD and GitOps environment delivery.** Jenkins X CLI v3.17.98, jx-gitops plugin v1.4.14, a pinned upstream cluster-template snapshot and a sample application chart. This is a bootstrap/integration package, not a preconfigured Jenkins X installation.

Independent deployment examples maintained by imos64. Upstream software remains maintained by its respective authors. This collection does not claim a measured ranking or that every tool independently performs continuous Git reconciliation.

## Local validation

Requirements: Linux amd64, Python 3.12+, Helm 3.21.3 and Make. CLI downloads are checksum-verified and placed in ignored `.tools/`. Internet access is needed for tools and Kubernetes schemas. Docker is needed for werf's container smoke test.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
make validate
```

`make render` refreshes the committed controller installation preview. CI has read-only repository permissions and no deployment credentials. It checks artifact checksums, exact rendering, strict Kubernetes 1.35.0 schemas, pinned upstream custom-resource schemas and delivery guardrails. Schema validation does not execute CEL, admission webhooks or controllers, and does not establish compatibility with every cluster version.

## Prepare the cluster Git repository

Use an existing supported Kubernetes cluster with deliberate choices for DNS/TLS, storage, registry authentication, bot identity, Lighthouse webhooks and secret storage. Jenkins X includes multiple controllers and pipelines; a small app chart alone is not a Jenkins X installation.

```bash
make validate
python3 scripts/prepare-cluster-repo.py --output site
```

The helper expands the immutable upstream `jx3-gitops-repositories/jx3-kubernetes` snapshot and overlays the example `jx-requirements.yml`. It rejects archive traversal/links and refuses overwrites. The prepared directory contains the upstream Helmfile, Lighthouse pipeline and version-stream configuration. Replace all `REPLACE_*` values and review upstream `todo` settings before using it as your cluster's Git repository. Its version stream and transitive controller versions need their own compatibility review; pin the version stream for an actual rollout.

The requirements preserve separate dev, staging and production environments and disable automatic version-stream updates. The upstream seed uses local secret storage; choose and configure a supported production secret store before bootstrapping. Do not put secret values in the prepared public repository. `.tools/jx` and `.tools/jx-gitops` are pinned downloaded binaries; the Jenkins X CLI may install additional plugins when commands are invoked, so review/pin those as needed.

Follow the official Jenkins X 3 installation workflow for your provider, then import the application using the normal Jenkins X project workflow. `charts/demo` is a locally linted application chart; `examples/helmfile.yaml` shows how to add it to an environment release set. Merge the release into the appropriate generated Helmfile instead of overwriting the cluster's core releases. Register bot credentials and webhooks outside Git.

Validate pull-request pipelines, preview cleanup, release publishing and staging/production promotion on the real installation before use. This package validates the template checksum, requirements layout, native jx-gitops YAML lint and app Helm rendering; it does not claim a booted Jenkins X platform. Roll back environment release versions through Git, preserve version-stream history and avoid removing shared controllers before their resources are migrated.

## Operations and provenance

Local validation was completed on 2026-09-07. No GitOps controller, cloud resource, external cluster registration or live delivery pipeline was deployed. See [validation scope](docs/validation.md), [controller ownership](docs/ownership.md), and [official upstream documentation](https://jenkins-x.io/v3/admin/).

Exact upstream URLs and artifact SHA-256 checksums are recorded in `package.json`. Controller versions follow the pinned upstream release/chart; demo workload images are digest-pinned. Review image digests, release notes and CRD lifecycle during upgrades. Upstream charts/manifests retain their own licensing; repository-authored integration files use MIT. Secrets and private site files must remain outside this public repository.
