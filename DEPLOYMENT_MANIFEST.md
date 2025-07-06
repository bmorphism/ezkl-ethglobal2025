# Deployment Manifest: Darkhaven

This document serves as the formal record of the "Darkhaven" milestone deployment.

## Versioning

- **Framework Version:** 0.2.0
- **EZKL Version:** 10.4.2
- **Node.js Version:** 18.x
- **Python Version:** 3.10

## Deployed Contracts (Sepolia Testnet)

| Contract                 | Address                                    |
| ------------------------ | ------------------------------------------ |
| `ProductionRWKVVerifier`   | `0x52b5e61fA6Ae53BA08B9094eA077820283Dcec01` |
| `ProductionMambaVerifier`  | `0x89dFdcC74Ed05bf2a76eF788b15e5cbC8Ad8C5cD` |
| `ProductionxLSTMVerifier`  | `0x52a55dEBE04124376841dF391Ef0e4eF1dd6835B` |
| `AgentRegistry`          | Deployed via `deploy_maximal_framework.js` |
| `ProofChainOrchestrator` | Deployed via `deploy_maximal_framework.js` |

## Key Artifacts

- **CI/CD Pipeline:** `.github/workflows/ci.yml`
- **Reproducible Environment:** `Dockerfile`
- **Pinned Dependencies:** `requirements.lock`
- **Architectural Philosophy:** `PHILOSOPHY.md`
- **Design Choices:** `DESIGN_CHOICES.md`
- **Security Policy:** `SECURITY.md`

This manifest represents a stable, secure, and reproducible state of the project, ready for the next phase of development.
