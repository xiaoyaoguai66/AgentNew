# M4: Integration Tests And Final Showcase

This phase closed the gap between “the project works locally” and “the project is ready for a public repository.”

## What Was Added

- backend integration test:
  - [integration_api.py](D:/Code/Fastapi/AgentNews/backend/tests/integration_api.py)
- CI linkage:
  - [.github/workflows/ci.yml](D:/Code/Fastapi/AgentNews/.github/workflows/ci.yml)
- public showcase materials:
  - [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md)
  - [final-delivery-checklist.md](D:/Code/Fastapi/AgentNews/docs/final-delivery-checklist.md)
  - [github-showcase-guide.md](D:/Code/Fastapi/AgentNews/docs/github-showcase-guide.md)

## Why It Matters

Integration coverage verifies the key product path instead of isolated helpers only. The public showcase materials keep the repo readable for outside viewers.

Together, this stage strengthens:

- regression confidence
- demo readiness
- public GitHub presentation quality

## Verification

Run the repo-level check:

```powershell
cd D:\Code\Fastapi\AgentNews
powershell -ExecutionPolicy Bypass -File .\scripts\dev-check.ps1
```

Then confirm the repository root README still explains:

- the product scope
- the architecture
- the validation path
