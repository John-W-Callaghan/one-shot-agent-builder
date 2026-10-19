# Agent Forge Architecture

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        IDEA (natural language)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1 — SCOPE                                            │
│  ┌───────────┐                                              │
│  │ Strategist│ → ProjectSpec (features, tech stack, scope)  │
│  └───────────┘                                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2 — DESIGN                                           │
│  ┌──────────┐   ┌──────────┐                                │
│  │ Architect│   │ Designer │  (run in parallel)             │
│  └────┬─────┘   └────┬─────┘                                │
│       │              │                                      │
│       ▼              ▼                                      │
│  ArchitectureDoc  DesignSystem                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3 — BUILD                                            │
│  ┌──────────────────┐   ┌─────────────────┐                 │
│  │ Frontend Builder │   │ Backend Builder │ (parallel)      │
│  └────────┬─────────┘   └────────┬────────┘                 │
│           │                      │                          │
│           ▼                      ▼                          │
│      frontend files         backend files                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4 — HARDEN                                           │
│  ┌──────────┐                                               │
│  │ Sentinel │ → AuditReport                                 │
│  └────┬─────┘                                               │
│       │                                                     │
│       ├── PASS → continue to Phase 5                        │
│       │                                                     │
│       └── FAIL → feedback loop to Phase 3                   │
│           (max 3 iterations, then proceed with warnings)    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5 — SHIP                                             │
│  ┌─────────┐                                                │
│  │ Shipper │ → README, CI/CD, deploy config                 │
│  └─────────┘                                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT DIRECTORY (complete project)            │
└─────────────────────────────────────────────────────────────┘
```

## Model Strategy

| Agent     | Role              | Model Tier   | Why                                      |
|-----------|-------------------|-------------|------------------------------------------|
| Strategist| Scoping           | High (Opus) | Needs judgment to make the right calls   |
| Architect | System design     | High (Opus) | Architecture mistakes are expensive      |
| Designer  | UI/UX design      | Mid (Sonnet)| Creative work with structured output     |
| Frontend  | Code generation   | Mid (Sonnet)| Fast, capable coding                     |
| Backend   | Code generation   | Mid (Sonnet)| Fast, capable coding                     |
| Sentinel  | Review & audit    | High (Opus) | Needs to catch what builders missed      |
| Shipper   | Docs & deploy     | Low (Haiku) | Templated, mechanical output             |

The shipped default config (`src/agent_forge/config.py`) runs the High-tier roles on Sonnet to
keep API costs down; swap any agent to Opus by changing one line.

## Data Flow

Every agent produces structured output (Pydantic models) that the next agent consumes:

1. **Idea** (string) → Strategist → **ProjectSpec**
2. **ProjectSpec** → Architect → **ArchitectureDoc**
3. **ProjectSpec** → Designer → **DesignSystem**
4. **ProjectSpec + ArchitectureDoc + DesignSystem** → Builders → **files** (dict[path, content])
5. **files** → Sentinel → **AuditReport**
6. **AuditReport** (if failed) → Builders (with fix instructions) → updated **files**
7. **ProjectSpec + ArchitectureDoc + files** → Shipper → **more files** (docs, CI, deploy)

All of this lives on a single `PipelineState` object (`schemas/contracts.py`), which also records
which builder owns each file so review findings can be routed back to the right agent.

## Quality Gate

The only feedback loop is Phase 4 → Phase 3:

- Sentinel reviews ALL code in one pass (bugs, security, a11y, performance, style)
- If critical issues are found, each finding is routed to the builder that owns the file
  (findings on unknown or cross-cutting files go to both builders)
- Builders regenerate the affected files with the findings and their previous output as context
- Sentinel reviews again
- Maximum 3 iterations (configurable with `--max-reviews`), then proceeds with warnings logged

This replaces 5 separate review gates in a traditional pipeline with 1 comprehensive pass.

## Robustness

- **Structured parsing**: agents are asked for JSON matching a Pydantic schema. The parser
  tolerates code fences and surrounding prose; if validation still fails, the agent retries once
  with the validation error included.
- **Streaming**: every API call streams, so long code-generation responses don't hit HTTP timeouts.
- **Error handling**: authentication, rate limit, connection, and refusal errors surface as a
  single `AgentError` with a clear message instead of a stack trace.
- **Safe writes**: generated paths are normalized, and any path that tries to escape the output
  directory (`../`) is skipped.
