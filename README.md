# 🔥 Agent Forge — One-Shot Agent Builder

![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/powered%20by-Claude-d97757)
![Pydantic](https://img.shields.io/badge/contracts-Pydantic%20v2-e92063)
![License](https://img.shields.io/badge/license-MIT-green)

**Describe an app in one sentence. Get back a complete, reviewed, documented codebase.**

Agent Forge is a multi-agent AI pipeline that takes a plain-English idea and produces shippable code
in a single run. Seven specialized Claude agents (a strategist, architect, designer, two builders, a
reviewer, and a release engineer) work through five phases that mirror a real software team, passing
validated JSON contracts to each other instead of meetings.

```bash
agent-forge "Build a todo app with Next.js and Supabase"
```

---

## Table of Contents

- [What You Get](#what-you-get)
- [The Pipeline](#the-pipeline)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [The Agents](#the-agents)
- [Why 7 Agents Instead of 14 Roles?](#why-7-agents-instead-of-14-roles)
- [Configuration](#configuration)
- [Using It as a Library](#using-it-as-a-library)
- [Project Structure](#project-structure)
- [Extending Agent Forge](#extending-agent-forge)
- [Cost and Runtime](#cost-and-runtime)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What You Get

From one idea, a single run writes a full project to your output directory:

| Output | Produced by |
|--------|-------------|
| Pages, components, styles, and frontend tests | Frontend Builder |
| API routes, database schema and migrations, middleware, backend tests | Backend Builder |
| Fixes for every critical issue the reviewer found | Builders, via the review loop |
| `README.md`, `CONTRIBUTING.md` | Shipper |
| `.github/workflows/ci.yml`, deploy config (`vercel.json`, `docker-compose.yml`, …) | Shipper |
| `.agent-forge-log.json`: a log of every agent's decisions | Orchestrator |

Along the way you see each phase in the terminal:

```
╭──────────────────────────────────────────────────╮
│ 🚀 Agent Forge Pipeline                          │
│                                                  │
│ Build a todo app with Next.js and Supabase       │
╰──────────────────────────────────────────────────╯

──────────────────────────────────────────────────
Phase 1 — Scope
  ⚡ strategist thinking... (claude-sonnet-5-5)
  ✓ Project scoped: TaskFlow
    Type: fullstack
    Features: 5
    Tech decisions: 6

──────────────────────────────────────────────────
Phase 2 — Design
  ✓ Architecture: 7 endpoints, 2 tables
  ✓ Design system: 12 components, 4 pages

──────────────────────────────────────────────────
Phase 3 — Build
  ✓ Frontend: 24 files
  ✓ Backend: 11 files

──────────────────────────────────────────────────
Phase 4 — Harden
  🔍 Review pass 1/3
    Findings: 2 critical, 5 warnings
  ↩ Sending 2 critical findings back to builders...
    ✓ Backend revised 2 files
  🔍 Review pass 2/3
    Findings: 0 critical, 3 warnings
  ✓ Code passed review

──────────────────────────────────────────────────
Phase 5 — Ship
  ✓ Docs & deploy config: 5 files
```

*(Illustrative output. Names and counts vary from run to run.)*

---

## The Pipeline

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

---

## Quick Start

**Prerequisites**

- Python 3.11 or newer
- An Anthropic API key ([get one here](https://console.anthropic.com/))

**Install**

```bash
git clone https://github.com/John-W-Callaghan/one-shot-agent-builder.git
cd one-shot-agent-builder

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

**Configure your API key**

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder:

```
ANTHROPIC_API_KEY=sk-ant-...
```

`.env` is git-ignored, so your key never gets committed.

**Run it**

```bash
agent-forge "Build a todo app with Next.js and Supabase" -o todo-app
```

When it finishes, your new project is in `./todo-app/`. Follow the generated `todo-app/README.md`
to install and run it.

---

## Usage

```
agent-forge [OPTIONS] [IDEA]
```

| Argument / Option | Default | Description |
|-------------------|---------|-------------|
| `IDEA` | *(prompted)* | Your project idea in plain English. Omit it to be asked interactively. |
| `-o`, `--output` | `output` | Directory to write the generated project into. |
| `-r`, `--max-reviews` | `3` | Maximum Sentinel review passes, 1–5. Lower is faster and cheaper. |
| `--help` | | Show help and exit. |

**Examples**

```bash
# A full-stack web app
agent-forge "Build a habit tracker with streaks, reminders, and a dashboard" -o habits

# A backend-only API, one review pass for speed
agent-forge "Create a REST API for a bookstore with inventory and orders" -o bookstore-api -r 1

# Use a longer prompt from a file
agent-forge "$(cat examples/todo-app/input.txt)" -o examples/todo-app/output

# Interactive mode
agent-forge
```

**Tips for better results**

- Name the stack if you care about it ("Next.js and Supabase", "FastAPI and Postgres"). Otherwise
  the Strategist defaults to Next.js + TypeScript + Supabase + Tailwind.
- List the 3–7 features that matter most. The Strategist trims anything beyond an MVP.
- Mention constraints such as auth, dark mode, mobile-first, or accessibility. Each one flows
  through every later phase.

---

## How It Works

Every agent is a Claude call with its own system prompt and its own output contract. The
orchestrator holds a single `PipelineState` object and passes each agent exactly what it needs.

1. **Scope.** The Strategist turns the idea into a `ProjectSpec`: name, type, features, tech stack
   with reasoning, user stories with acceptance criteria, an explicit out-of-scope list, and a
   proposed file tree.

2. **Design.** The Architect and the Designer run **in parallel** on the spec. The Architect returns
   an `ArchitectureDoc` (endpoints, tables, auth strategy, env vars, deploy target). The Designer
   returns a `DesignSystem` (color tokens with dark mode, typography, 8–15 components, routes,
   accessibility notes).

3. **Build.** The Frontend and Backend builders run **in parallel**. Each returns a
   `{path: content}` map of complete files, with no `TODO` placeholders.

4. **Harden.** The Sentinel reviews every file at once for bugs, security, accessibility,
   performance, and code quality, and returns an `AuditReport`. Each critical finding is routed
   to the builder that owns the affected file, along with that builder's previous output and a
   specific fix instruction. The builder returns corrected files, and the Sentinel reviews again.
   The loop stops when there are no critical findings or the iteration limit is reached.

5. **Ship.** The Shipper (on a cheaper, faster model) writes the README, CI workflow, deploy
   config, and contributing guide for the generated project.

All outputs are validated with Pydantic. If an agent's response doesn't match its schema, it gets
one automatic retry with the validation error attached.

For the full data-flow diagram and design rationale, see [docs/architecture.md](docs/architecture.md).

---

## The Agents

| Agent | Phase | Default model | Reads | Produces | Prompt |
|-------|-------|---------------|-------|----------|--------|
| **Strategist** | 1 — Scope | `claude-sonnet-5-5` | Idea | `ProjectSpec` | [strategist.md](src/agent_forge/prompts/strategist.md) |
| **Architect** | 2 — Design | `claude-sonnet-5-5` | Spec | `ArchitectureDoc` | [architect.md](src/agent_forge/prompts/architect.md) |
| **Designer** | 2 — Design | `claude-sonnet-5-5` | Spec | `DesignSystem` | [designer.md](src/agent_forge/prompts/designer.md) |
| **Frontend Builder** | 3 — Build | `claude-sonnet-5-5` | Spec, design, architecture | Frontend files | [frontend.md](src/agent_forge/prompts/frontend.md) |
| **Backend Builder** | 3 — Build | `claude-sonnet-5-5` | Spec, architecture | Backend files | [backend.md](src/agent_forge/prompts/backend.md) |
| **Sentinel** | 4 — Harden | `claude-sonnet-5-5` | All files | `AuditReport` | [sentinel.md](src/agent_forge/prompts/sentinel.md) |
| **Shipper** | 5 — Ship | `claude-haiku-5-5` | Spec, architecture, file list | Docs, CI, deploy config | [shipper.md](src/agent_forge/prompts/shipper.md) |

The data contracts live in [`schemas/spec.py`](src/agent_forge/schemas/spec.py).

---

## Why 7 Agents Instead of 14 Roles?

Traditional enterprise software follows a pipeline that looks like this:

**The 14-Role Enterprise Model:**

| Phase | Roles | What They Do |
|-------|-------|-------------|
| Discovery | Product Manager, User Researcher, Business Analyst | 3 people scope the project over days/weeks |
| Design | System Architect, UX Designer, API Designer | 3 people design the system in parallel-ish |
| Build | Frontend Dev, Backend Dev, Fullstack Dev, DevOps | 4 people write code across sprints |
| Review | Senior Engineer, QA Engineer, Security Analyst | 3 people review in sequence (code → QA → security) |
| Ship | Technical Writer, Release Manager | 2 people document and deploy |

That's **14 roles**, **5+ handoff points**, and **weeks to months** from idea to production.
It exists because human beings can't hold the full context of a system in their heads — so
the work is split across specialists who each understand one slice.

**The problem with this for AI:** these constraints don't apply.

### What AI Changes

1. **No context window limits per role.** An AI agent can read the entire project spec, all the
   code, and the design system in one pass. A human security reviewer can't also be doing the
   UX audit — an AI agent can.

2. **No communication overhead.** In an enterprise, the biggest time sink isn't the work — it's
   the meetings, Jira tickets, Slack threads, and alignment sessions between roles. Agents pass
   structured JSON contracts. Zero ambiguity, zero meetings.

3. **No sequential bottlenecks for parallel work.** The Architect and Designer can genuinely
   run in parallel with no calendar coordination. The Frontend and Backend builders read from
   the same spec simultaneously.

4. **Review doesn't need to be sequential.** In an enterprise, code review → QA → security →
   accessibility is a sequential pipeline because each reviewer has a different skillset. One
   AI agent with the right prompt can check all four dimensions in a single pass.

### The 7-Agent Model

| Phase | Agent | Replaces | Why It Works |
|-------|-------|----------|-------------|
| Scope | **Strategist** | PM + Researcher + BA | AI can research, analyze, and scope in one pass — no need for 3 people to converge on a PRD |
| Design | **Architect** | System Architect + API Designer | System design and API design are the same decision space — splitting them creates interface conflicts |
| Design | **Designer** | UX Designer | Focused on visual/interaction design with access to the full spec |
| Build | **Frontend Builder** | Frontend Dev + some Fullstack | Writes all frontend code + tests. No handoff to a separate test writer |
| Build | **Backend Builder** | Backend Dev + DevOps + some Fullstack | Writes API routes, DB schema, and infra config. Each builder owns their domain end-to-end |
| Harden | **Sentinel** | Senior Engineer + QA + Security + UX Reviewer | **The key insight**: one agent with the right prompt reviews for bugs, security, a11y, and performance in a single pass. This replaces 4 sequential review stages |
| Ship | **Shipper** | Tech Writer + Release Manager | Docs and deploy config are mechanical given the spec — a lightweight model handles both |

### What Gets Cut (and Why It's Fine)

- **5 separate review gates → 1 comprehensive review.** The Sentinel checks everything at once.
  If it fails, it sends specific fix instructions back to the builders. Maximum 3 rounds, then ship
  with warnings. This replaces the traditional code review → QA → security → a11y → UAT pipeline.

- **Sprint ceremonies and planning → nothing.** There's no team to coordinate. The orchestrator
  runs the phases in order and handles the feedback loop programmatically.

- **Separate test writers → builders write their own tests.** Each builder generates tests alongside
  their code. The Sentinel verifies test quality during review.

- **User Researcher as a separate role → folded into Strategist.** For a code-generation pipeline,
  user research is "understand what the user described" — not a weeks-long ethnographic study.

### The Numbers

| Metric | Enterprise (14 roles) | Agent Forge (7 agents) |
|--------|----------------------|----------------------|
| Roles/Agents | 14 | 7 |
| Handoff points | 5+ (with meetings) | 4 (structured JSON) |
| Review stages | 4 sequential | 1 comprehensive |
| Feedback loops | Multiple, slow | 1 targeted loop (max 3 passes) |
| Time to first output | Days to weeks | Minutes |
| Context loss between stages | High (documentation, meetings) | Zero (shared state object) |

---

## Configuration

### Models

Each agent's model is one line in [`src/agent_forge/config.py`](src/agent_forge/config.py):

```python
STRATEGIST_MODEL: str = "claude-sonnet-5-5"
ARCHITECT_MODEL: str = "claude-sonnet-5-5"
SENTINEL_MODEL: str = "claude-sonnet-5-5"
FRONTEND_MODEL: str = "claude-sonnet-5-5"
BACKEND_MODEL: str = "claude-sonnet-5-5"
DESIGNER_MODEL: str = "claude-sonnet-5-5"
SHIPPER_MODEL: str = "claude-haiku-5-5"
```

The defaults keep costs reasonable. For higher-quality output, move the judgment roles
(Strategist, Architect, Sentinel) to `claude-opus-5-5`, where better decisions early in the
pipeline pay off in every later phase.

### Refusal fallback

Calls to non-Haiku models opt into the Claude API's server-side refusal fallback: if a safety
classifier declines a request, the API reruns it on a fallback model within the same call. If your
account doesn't have access to this beta, set:

```python
USE_REFUSAL_FALLBACK: bool = False
```

### Review depth

`--max-reviews` controls how many times the Sentinel can send work back. `1` gives a single review
with no fix loop; `3` (the default) is a good balance; `5` is the most thorough.

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key. Read from the environment or from `.env`. |

---

## Using It as a Library

Run the whole pipeline from Python:

```python
from dotenv import load_dotenv
from agent_forge.orchestrator import Pipeline

load_dotenv()

state = Pipeline(output_dir="todo-app", max_review_iterations=2).run(
    "Build a todo app with Next.js and Supabase"
)

print(state.spec.project_name)
print(state.audit.summary)
for finding in state.audit.findings:
    print(f"[{finding.severity}] {finding.file_path}: {finding.description}")
```

Or run a single agent on its own:

```python
from agent_forge.agents import Strategist, Architect

spec = Strategist().run({"idea": "A CLI that tracks time spent per git branch"})
architecture = Architect().run({"spec": spec})

print(spec.model_dump_json(indent=2))
print([f"{e.method} {e.path}" for e in architecture.api_endpoints])
```

---

## Project Structure

```
one-shot-agent-builder/
├── README.md
├── LICENSE
├── pyproject.toml             # Package config and the `agent-forge` entry point
├── .env.example               # Template for your API key
├── docs/
│   └── architecture.md        # Data flow, model strategy, quality gate
├── examples/
│   └── todo-app/
│       └── input.txt          # A complete example prompt
└── src/
    └── agent_forge/
        ├── cli.py             # Command-line interface
        ├── orchestrator.py    # Runs the 5 phases and the review loop
        ├── config.py          # Per-agent model selection
        ├── schemas/
        │   ├── spec.py        # Pydantic models for every agent output
        │   └── contracts.py   # PipelineState: shared state across agents
        ├── agents/
        │   ├── base.py        # API calls, streaming, JSON parsing, retries, errors
        │   ├── strategist.py  # Phase 1 — Scope
        │   ├── architect.py   # Phase 2 — System design
        │   ├── designer.py    # Phase 2 — UI/UX design
        │   ├── frontend.py    # Phase 3 — Frontend code
        │   ├── backend.py     # Phase 3 — Backend code
        │   ├── sentinel.py    # Phase 4 — Review and audit
        │   └── shipper.py     # Phase 5 — Docs and deploy config
        ├── prompts/           # One system prompt per agent (Markdown)
        └── tools/             # Filesystem, shell, and search helpers
```

---

## Extending Agent Forge

**Change an agent's behavior.** Edit its prompt in `src/agent_forge/prompts/`. Prompts are plain
Markdown, loaded at runtime, so there's no code change needed.

**Add a new agent** (for example, a test-runner or a database seeder):

1. If it returns structured data, add a Pydantic model to `schemas/spec.py`.
2. Create `agents/<name>.py`, subclass `BaseAgent`, and implement `run()`. Use
   `_call_model_structured()` for schema outputs or `_generate_files()` for file maps.
3. Add a system prompt at `prompts/<name>.md` (the file name must match the agent's `name`).
4. Add its model to `config.py` and call it from `orchestrator.py`.

`BaseAgent` handles streaming, response parsing, schema validation with retry, and error
messages, so a new agent is usually 20–30 lines.

---

## Cost and Runtime

A full run makes about 8 API calls, plus 2–3 more for each review iteration. Code generation
dominates both the time and the token usage. As a rough guide:

- **Time:** a few minutes for a typical web app, longer for large projects or extra review passes.
- **Cost:** depends on project size and models. Using `-r 1` and keeping the default Sonnet/Haiku
  mix is the cheapest setup; moving roles to Opus raises quality and cost.

Check your usage in the [Anthropic Console](https://console.anthropic.com/) after your first run
to calibrate.

---

## Troubleshooting

| Message | Fix |
|---------|-----|
| `ANTHROPIC_API_KEY not set` | Copy `.env.example` to `.env` and add your key, or `export ANTHROPIC_API_KEY=...`. |
| `authentication failed` | The key is wrong or revoked. Create a new one in the Anthropic Console. |
| `model '…' not found` | Your account can't access that model. Change it in `config.py`. |
| `API error 400` mentioning fallbacks or betas | Set `USE_REFUSAL_FALLBACK = False` in `config.py`. |
| `rate limited after retries` | Wait a minute and rerun, or use `-r 1` to make fewer calls. |
| `hit max_tokens; output may be truncated` | The project is very large. Narrow the idea to fewer features. |
| `returned no parseable files` | Rare formatting failure. Rerun; the raw output preview shows what came back. |
| `Dropped unsafe path` in `.agent-forge-log.json` | A generated path tried to escape the output directory and was blocked on purpose. |

---

## Limitations

- **Generated code is a strong first draft, not a guarantee.** The Sentinel reviews the code, but
  nothing is compiled or executed during the run. Install and test the output before deploying it.
- **No live research.** Agents rely on the model's training knowledge; `tools/search.py` is a stub.
- **One project per run.** There's no incremental "add a feature to my existing repo" mode yet.
- **Very large apps** can exceed a single builder response. Smaller, focused ideas work best.

---

## Roadmap

- [ ] Run the generated project's install, lint, and tests, and feed failures into the review loop
- [ ] Real web search for library docs and current versions
- [ ] Structured outputs for guaranteed schema conformance
- [ ] Incremental mode: extend an existing codebase instead of generating a new one
- [ ] Per-run cost and token report

---

## Contributing

Issues and pull requests are welcome.

```bash
git clone https://github.com/John-W-Callaghan/one-shot-agent-builder.git
cd one-shot-agent-builder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
agent-forge --help
```

Good first contributions: improving an agent's prompt, adding an example under `examples/`, or
picking up a roadmap item. Please keep pull requests focused, and describe what you changed and how
you tested it.

## License

[MIT](LICENSE)
