# M4: Dev Check And Demo Materials

This stage focused on making the repository easier to validate and easier to demo.

## What Was Added

- repo-level dev check script: [scripts/dev-check.ps1](../scripts/dev-check.ps1)
- smoke and integration validation paths
- public demo material entry points:
  - [demo-script.md](demo-script.md)
  - [final-delivery-checklist.md](final-delivery-checklist.md)
  - [github-showcase-guide.md](github-showcase-guide.md)

## Why It Matters

The project had already reached a feature-complete stage. The next problem was not 鈥渨hat feature should be added next,鈥?but 鈥渉ow can the repo be validated and shown clearly.鈥?
This step made the project easier to:

- validate before commits or demos
- present in GitHub without extra explanation
- hand over as a cleaner, more enterprise-style repository

## Verification

Run:

```powershell
cd .
powershell -ExecutionPolicy Bypass -File .\scripts\dev-check.ps1
```

This covers:

- backend compile
- backend smoke
- backend integration
- frontend build


