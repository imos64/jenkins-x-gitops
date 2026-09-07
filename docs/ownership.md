# Reconciliation ownership

| Tool | Primary ownership |
| --- | --- |
| Argo CD / Flux / Fleet / Kluctl | Selected Git source and delivered Kubernetes objects |
| PipeCD | Registered application's deployment pipeline and target identity |
| Jenkins X | Developer pipelines and environment release promotion |
| werf | Build inputs, images and release artifacts; requires a delivery/reconciliation integration |
| Argo Rollouts / Flagger | Progressive workload revisions and traffic handoff |
| Crossplane | Infrastructure API requests and composed/managed resources |

Choose one Git delivery owner per input object. A progressive controller may then own descendants and selected fields; do not force Git's replicas or Service selectors over those changes. Crossplane should own composed resources while Git delivers their requests. Use separate namespaces, service accounts and repository paths for distinct examples.

Review branch protection, immutable promotion references, RBAC, secret storage, pruning, finalizers and rollback retention for the actual environment. Suspending a controller stops future reconciliation; it does not restore previous state or remove created resources. Test deletion and rollback in staging before enabling automated pruning.
