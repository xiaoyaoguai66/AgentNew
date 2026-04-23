# M4: Dev Check And Demo Materials

This stage focused on making the repository easier to validate and easier to demo.

## What Was Added

- repo-level dev check script: [scripts/dev-check.ps1](D:/Code/Fastapi/AgentNews/scripts/dev-check.ps1)
- smoke and integration validation paths
- public demo material entry points:
  - [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md)
  - [final-delivery-checklist.md](D:/Code/Fastapi/AgentNews/docs/final-delivery-checklist.md)
  - [github-showcase-guide.md](D:/Code/Fastapi/AgentNews/docs/github-showcase-guide.md)

## Why It Matters

The project had already reached a feature-complete stage. The next problem was not “what feature should be added next,” but “how can the repo be validated and shown clearly.”

This step made the project easier to:

- validate before commits or demos
- present in GitHub without extra explanation
- hand over as a cleaner, more enterprise-style repository

## Verification

Run:

```powershell
cd D:\Code\Fastapi\AgentNews
powershell -ExecutionPolicy Bypass -File .\scripts\dev-check.ps1
```

This covers:

- backend compile
- backend smoke
- backend integration
- frontend build
