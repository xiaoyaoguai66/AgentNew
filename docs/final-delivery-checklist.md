# AgentNews Final Delivery Checklist

Use this checklist before pushing a public-facing update or demonstrating the project.

## 1. Core Runtime

- backend starts correctly
- frontend starts correctly
- `.env` uses placeholder-safe values for anything that could leak secrets
- `.env.example` stays aligned with the real runtime configuration

## 2. Validation

- `powershell -ExecutionPolicy Bypass -File .\scripts\dev-check.ps1` passes
- backend compile check passes
- backend smoke check passes
- backend integration check passes
- frontend production build passes

## 3. Public Documentation

- [README.md](D:/Code/Fastapi/AgentNews/README.md) is up to date
- [architecture-overview.md](D:/Code/Fastapi/AgentNews/docs/architecture-overview.md) matches the current implementation
- [architecture-diagrams.md](D:/Code/Fastapi/AgentNews/docs/architecture-diagrams.md) still reflects the real workflow
- [documentation-map.md](D:/Code/Fastapi/AgentNews/docs/documentation-map.md) points only to public project docs
- [github-showcase-guide.md](D:/Code/Fastapi/AgentNews/docs/github-showcase-guide.md) matches the current repo layout

## 4. Demo Readiness

- [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md) has been reviewed
- the core user flow still works: home -> detail -> AI -> session switch
- at least one retrieval + trace + evaluation path is working end-to-end

## 5. Clean Repository Rules

- no personal keys or secrets are tracked
- no local data directories are tracked
- no private resume or interview notes are tracked
- public repo content is limited to project implementation, architecture, testing, and delivery materials

## 6. Optional Final Polish

- prepare screenshots or short demo clips
- check the GitHub repo homepage renders the root README correctly
- confirm the default branch points to the latest public project version
