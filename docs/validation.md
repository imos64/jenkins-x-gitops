# Validation record

Passed local static checks on 2026-09-07: vendored artifact checksums, Helm lint where a chart is used, exact committed rendering, strict Kubernetes 1.35.0 resource schemas, upstream CRD schema checks and regression checks for overly broad application permissions or unintended automatic promotion.

Native checks vary by package: Fleet emits a Bundle without applying it; Kluctl renders staging and production offline; Jenkins X uses jx-gitops YAML lint and Helm app rendering; werf renders with stub image references. Flagger smoke testing checks both healthy and unavailable canary responses. werf's separate Docker smoke test builds the actual Dockerfile and exercises HTTP over localhost. PipeCD configuration checks cover structure and referenced manifests, not a connected control plane. Crossplane composition functions were not executed.

No test installs controllers, applies manifests, registers clusters, creates IAM identities or pushes registry artifacts. Kubernetes CEL, admission policies, live Git reconciliation, authentication, webhooks, progressive traffic handoff, cloud provisioning and disaster recovery require a separately reviewed staging deployment. Passing CI is not production certification.
