# CODING STANDARDS V9

> **Core Philosophy**: Fail Fast, Fail Clearly. Explicit is better than implicit. Convention over configuration—except when clarity demands otherwise. Keep code concise, performant, configurable, maintainable, and secure.
Only optional packages imports can be put in try except blocks
Internal projects will not ever be import or used as option packages

---

## Project Tasks
- Every Package work session should begin with an update to the projects STATE.md
- Always write CHANGES-<PROJECT>.md files for changes needed in other projects

---

## 1. Project Structure & Workspace

### Standard Project Structure Template
```
project-name/
├── project/
│   ├── __init__.py
│   └── cli.py          # Entry point
├── docs/
│   └── index.md        # Developer Documentation
├── skills/
│   └── project-name/
│       └── SKILL.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── README.md            # Project overview and quick start
├── STATE.md             # Current status, work in progress
├── pyproject.toml       # Package metadata and dependencies
├── CHANGES.md           # Changelog (or CHANGES-<project>.md)
├── CODING_STANDARDS.md  # Project coding standards
├── LICENSE              # License file
├── .gitattributes       # Git attributes for LFS, line endings
└── .gitignore           # Git ignore patterns
```

### Shared Workspace (EDN)
```
~/EDN/Documents/SHARED_WORKSPACE/
├── guides/             # Standards and documentation
├── templates/          # Reusable file templates
├── assets/             # Shared images, configs
└── archives/           # Historical versions
```

### Path Discovery Priority (Highest → Lowest)
1. Workspace `projects/` folder
2. Workspace `skills/` folder
3. SHARED_WORKSPACE `~/EDN/Documents/SHARED_WORKSPACE`
4. Python environments in `~/ENVs/`

> **Rule**: Never hardcode absolute paths. Use dynamic workspace resolution.

```python
# ❌ Bad - hardcoded path
data_path = "~/.<[agent-name]>/sessions/data.json"

# ✅ Good - dynamic resolution
from dalphin import WorkspaceResolver
workspace = WorkspaceResolver()
data_path = workspace.get_path("sessions", "data.json")
```

---

## 2. Import Management

### The tuh Environment (REQUIRED - General)
All agent imports **MUST** use the `tuh` non-GUI virtual environment:
- Core agent dependencies
- CLI tools, data processing, API integrations
- NOT for GUI projects

```bash
source ~/ENVs/tuh/bin/activate
```

### The zuh Environment (REQUIRED - GUI)
All agent GUI imports **MUST** use the `zuh` virtual environment:
- Contains PySide6, PyQt5, and other GUI dependencies
- Use for projects that need desktop GUI (nchantrs, etc.)

```bash
source ~/ENVs/zuh/bin/activate
```

### Python Environment Strategy
```
~/ENVs/
├── tuh   # Core agent dependencies (REQUIRED for CLI/imports)
├── uh    # User-specific customizations
├── truh  # Testing/validation
├── fruh  # Feature development
├── fuh   # Function utilities
└── zuh   # GUI-specific dependencies (PySide6, PyQt5, nchantrs)
```

### Subproject Import Ban (CRITICAL)
> Never import workspace projects as subprojects.

Instead, clone each project separately in `projects/`:
```
projects/senbot/
projects/ogma/
projects/wigumhammer/
```

### Dependency Handling
**Fail fast on required dependencies.** Only use try/except for optional packages.

```python
# ❌ Bad - hides missing dependencies
try:
    import required_package
except ImportError:
    pass  # Silently fails later

# ✅ Good - explicit dependency (fails immediately)
import required_package

# ✅ Good - optional dependency
try:
    import optional_package
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False
```

---

## 3. Git Workflow (MANDATORY)

### Branch Convention
- **Local development**: `local/<agent>-<feature>`
- **Shared integration**: `gamma`
- **Release**: `release/X.Y.Z`

### Agent Git Workflow (CRITICAL RULE)

> **The AGENT will ALWAYS merge FROM gamma TO their `<agent>-ws` branch, never the reverse.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT GITHUB WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   GitVein (origin)              Agent Workspace                  │
│   ┌──────────────┐              ┌──────────────┐               │
│   │    gamma     │◄─────────────│   morg-ws    │               │
│   │  (shared)   │   merge FROM │  (agent work)│               │
│   └──────────────┘              └──────┬───────┘               │
│        ▲                            │                         │
│        │                            │                         │
│        │                      push to                         │
│        │                    origin (morg-ws)                   │
│        │                            │                         │
│   USER MERGES                        │                         │
│        │                            ▼                         │
│   ┌────────┐                  ┌──────────────┐                  │
│   │ gamma  │◄────────────────│   morg-ws   │                  │
│   │  (sink)│   user merges   │   (source)  │                  │
│   └────────┘                  └─────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Step-by-Step Workflow:

1. **Start of session**: Merge gamma → `<agent>-ws`
   ```bash
   git checkout morg-ws
   git merge origin/gamma
   ```

2. **Development**: Work on `<agent>-ws` branch

3. **End of session**: Push changes to origin `<agent>-ws`
   ```bash
   git push origin morg-ws
   ```

4. **NEVER**: Merge `<agent>-ws` back to gamma directly

5. **User responsibility**: User reviews and merges agent changes to gamma

> **RULE**: The AGENT pushes to their `<agent>-ws` branch only. The USER merges from `<agent>-ws` to gamma. The AGENT never merges their own changes into gamma.

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Anti-Patterns
| Anti-Pattern | Why | Fix |
|--------------|-----|-----|
| Large commits | Hard to review | Atomic commits |
| Force push to gamma | Destroys history | Never force push shared |
| Work on gamma directly | Breaks workflow | Use agent-ws branches |
| Merge to gamma from agent | Bypasses user review | Push to agent-ws only |

---

## 4. Internal Projects

### Working with Internal Projects
- **DO NOT include internal projects as dependencies in pyproject.toml** - there is an issue with them being registered even on install
- Always attempt to leverage internal projects for features in a project
- Write `CHANGES-<project>.md` files for changes needed in other projects
- Analyze the Project to implement, don't assume implementations

### Internal Projects List (Alphabetical)

| Project | Purpose | When to Use |
|---------|---------|-------------|
| **APIg** | API gateway and utilities | Need REST API endpoints, rate limiting, request routing |
| **AXN** | Task management system | Need structured task workflows, hierarchical task decomposition |
| **CADLib** | CAD library utilities | Need CAD file processing, geometry calculations |
| **Condor** | YAML-based configuration cascade | Need multi-environment config management, YAML merging with `<(INCL)>` |
| **Elv1r4** | Web3 Interface | Need blockchain interactions, smart contract calls, crypto utilities |
| **Falcon** | Test generation | Need automated test case creation from code analysis |
| **Glain** | Long-term memory & knowledge engine | Need RAG, vector search, document ingestion, semantic memory |
| **Maxine** | Markets middleware | Need financial data processing, market data APIs |
| **Metrologic** | Statistics & calculations | Need statistical analysis, mathematical computations |
| **MicroMole** | Data collection & storage | Need data ingestion from files, APIs, databases |
| **MindOT** | Decision engine | Need structured decision-making, trade-off analysis for complex choices |
| **Nchantrs** | PySide6/PyQt5 GUI framework | Need rapid desktop GUI development with YAML config, SQLite backend |
| **Ogma** | ZMQ messaging & logging | Need inter-agent communication, rich logging, message protocols |
| **Owl** | ML aggregation | Need machine learning model orchestration, training pipelines |
| **ProjectAXN** | Project management | Need project-level task tracking, milestone management |
| **Pyffice** | Office automation | Need document processing (spreadsheets, PDFs, calendars, contacts) |
| **Pycurity** | Security suite | Need encryption, hashing, keystore, credential management |
| **Sasquatch** | Package management | Need Git-based package distribution, local package indexes |
| **SenBot** | Agent loop framework | Need AI agent automation, LLM integration, tool calling |
| **Sentinel** | Supervisory agent loop | Need nested worker management, task orchestration with AI |
| **Shroud** | GUI testing harness | Need automated GUI testing for agent loops |
| **Skillator** | Skill management | Need capability discovery and invocation system |
| **SQuiRL** | Storage format aggregator | Need unified API for files, databases, caches, text files |
| **Subtrix** | Text substitution | Need dynamic text templating, macro expansion |
| **Titan** | Container management | Need multi-machine Docker/container orchestration |
| **TwoF** | Two-factor authentication | Need 2FA for packages, DNS security |
| **WigumHammer** | Subagent tools | Need Ralph coding loops, WiggumClock task decomposition |
| **WorldBridgeServer** | API aggregator | Need unified API across Web2 and Web3 endpoints |

---

### Internal Projects Detailed Usage

#### AXN - Task Management System
```python
from axn import AXN, Task

# Create a task workflow
workflow = AXN(name="my_project")
task = Task(name="build", action="npm run build")
workflow.add_task(task)
```

**Use when**: Building structured task pipelines with dependencies and progress tracking.

---

#### Glain - Long-term Memory
```python
from glain import ContextEngine

engine = ContextEngine(db_path="memory.db")
engine.add_context("Important fact", metadata={"source": "user"})
results = engine.query("What fact was shared?")
```

**Use when**: Need semantic search over documents, RAG implementation, or persistent context.

---

#### Condor - Configuration Management
```python
import kahndor

config = kahndor.Instruct("config.yaml").select("Production").override("local.yaml")
```

**Use when**: Managing multiple environment configs with cascading overrides and YAML includes.

---

#### Pycurity - Security
```python
from pycurity import encrypt_aes, decrypt_aes

encrypted = encrypt_aes("message", key="secret-key")
decrypted = decrypt_aes(encrypted, key="secret-key")
```

**Use when**: Need encryption, hashing, keystore, or credential management.

---

#### Ogma - ZMQ Messaging
```python
from ogma import OgmaPublisher, OgmaSubscriber

pub = OgmaPublisher(port=5555)
pub.publish({"task": "process", "data": "..."})
```

**Use when**: Need inter-process communication between agents. Use ogma library for standardized messaging.

---

#### Nchantrs - GUI Framework
```python
import nchantrs

config = nchantrs.load_config('app.yaml')
app = nchantrs.Application(config)
app.run()
```

**Use when**: Building PySide6/PyQt5 desktop apps with YAML-defined UI and SQLite backend.

---

#### SQuiRL - Unified Storage
```python
import squirrl

storage = squirrl.Storage(config)
data = storage.read('key')
storage.write('key', data)
```

**Use when**: Need unified API for files, databases, caches with pluggable backends.

---

#### MicroMole - Data Collection
```python
import micromole

collector = micromole.Collector(config)
data = collector.fetch()
```

**Use when**: Ingesting data from APIs, files, databases into storage systems.

---

#### MindOT - Decision Engine
```python
from mindot import DecisionEngine

engine = DecisionEngine()
decision = engine.decide(options=[...], criteria=[...])
```

**Use when**: Complex trade-offs need structured analysis with multiple criteria.

---

#### Sentinel - Worker Orchestration
```python
from sentinel import Sentinel

sentinel = Sentinel(num_workers=4)
result = sentinel.submit(task_function, args)
```

**Use when**: Need multiprocessing/threading with nested worker hierarchies.

---

## 5. Security & Configuration

### Encryption & Secrets
- **NEVER** show encrypted data or blob contents
- Use `pycurity` for keystore operations
- Credentials stored in `~/.local/share/pycurity/`

---

## 6. Async Patterns

### Core Guidelines
1. **Await I/O-bound operations**: file reads, network calls, ZMQ
2. **Use `asyncio.to_thread()`** for blocking calls in async context
3. **Never block the event loop**: offload to thread pool

### ZMQ/ogma (Optional - Only for IPC)
> **Note**: ZMQ is optional. Only install/use when your project needs interprocess communication with other agents. Use the **ogma** library.

```python
# Only use if IPC is required
try:
    import ogma
    HAS_IPC = True
except ImportError:
    HAS_IPC = False
```

### Error Handling
```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Failed: {e}")
    raise  # Fail fast, fail clearly
```

---

## 7. CLI Implementation

### Use Actual Python CLI Frameworks
**Not bash scripts.** Use `click` or `typer`.

```python
import click

@click.command()
@click.option("--shared", is_flag=True, help="Use shared workspace")
def main(shared):
    workspace = get_workspace(shared)
    # ...
```

---

## 8. Testing Standards

### Test Structure
```
tests/
├── unit/
├── integration/
└── e2e/
```

### Naming Convention
- Unit: `test_<module>_<function>.py`
- Integration: `test_integration_<feature>.py`
- E2E: `test_e2e_<workflow>.py`

### Code Coverage
- Minimum 80% for new features
- Critical paths: 95%+

---

## 9. Team Coding Rules

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] Has docstrings for public APIs
- [ ] No hardcoded secrets
- [ ] Handles errors explicitly
- [ ] Tests cover happy path AND edge cases
- [ ] No blocking calls in async code
- [ ] Imports use correct environment (tuh or zuh)

### Documentation Requirements
| Code Type | Requirement |
|-----------|-------------|
| Public functions | Docstrings (Google/NumPy style) |
| Complex algorithms | Inline comments explaining "why" |
| Configuration | Comments for non-obvious values |
| API endpoints | OpenAPI spec or equivalent |

---

## 10. Data Formats

| Data Type | Format |
|-----------|--------|
| Config | YAML or JSON |
| Tasks/Projects | AXN or PAXN (YAML) |
| Documents | Native format with clear extension |

---

## 11. Anti-Patterns (DO NOT DO)

### Code Anti-Patterns
| Anti-Pattern | Why | Fix |
|--------------|-----|-----|
| `except: pass` | Swallows all errors | Catch specific exceptions |
| Global state | Unpredictable behavior | Dependency injection |
| Blocking in async | Deadlocks, poor perf | `asyncio.to_thread()` |
| Magic numbers | Unclear intent | Named constants |
| Duplicate code | Maintenance burden | Extract to function |
| Hardcoded paths | Breaks portability | Dynamic resolution |

---

## 12. Environment Variables

| Variable | Purpose |
|----------|---------|
| `<[agent-name]>_WORKSPACE` | Workspace root path |
| `<[agent-name]>_ENV` | Environment name (dev/staging/prod) |
| `<[agent-name]>_AGENT` | Current agent name |

---

## 13. Shared Workspace Guidelines

### Permission Issue Rule (IMPORTANT)
When encountering permission denied errors on shared workspace files:
1. **Default to creating a versioned copy** with `_v{n}` suffix (e.g., `AGENTS_v3.md`)
2. Notify user of the permission issue
3. Provide the new versioned file path
4. Never attempt sudo without explicit user permission

### Access Patterns
- **Direct edit**: Local workspace (`~/.<[agent-name]>/workspace/`)
- **Shared read**: `~/EDN/Documents/SHARED_WORKSPACE/`
- **Sync**: Use rclone bisync for bidirectional sync

### Conflict Resolution
1. Edit conflict → user decides which version wins
2. Never auto-merge shared workspace changes
3. Communicate changes in #shared-workspace channel

---

## 14. Quick Reference

### Common Commands
```bash
# Activate tuh environment (REQUIRED for imports)
source ~/ENVs/tuh/bin/activate

# Activate zuh environment (REQUIRED for GUI imports)
source ~/ENVs/zuh/bin/activate

# Start of session: merge gamma to agent-ws
git checkout morg-ws
git merge origin/gamma

# End of session: push to agent-ws
git push origin morg-ws

# Spawn a coding subagent
spawn label="my-task" task="Fix the auth bug"

# List running subagents
list_subagents

# Kill a subagent
kill_subagent <subagent_id>

# Check workspace paths
dalphin action="workspace_paths"

# Discover projects
dalphin action="discover"
```

### Key Paths
```python
WORKSPACE = "~/.<[agent-name]>/workspace"
PROJECTS = "~/.<[agent-name]>/workspace/projects"
SKILLS = "~/.<[agent-name]>/workspace/skills"
MEMORY = "~/.<[agent-name]>/workspace/memory"
EDN = "~/EDN"
SHARED_WORKSPACE = "~/EDN/Documents/SHARED_WORKSPACE"
```

### Port Configuration (Required for ZMQ only)
| Service | Port | Protocol | Required |
|---------|------|----------|----------|
| SenBot Gateway | 5555 | ZMQ | Only if using ZMQ |
| Subagent Bus | 5556 | ZMQ | Only if using ZMQ |
| Telemetry | 5557 | ZMQ | Only if using ZMQ |
| Telegram Bot | 8443 | HTTPS | No |
| SSH | 22 | SSH | No |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V1 | 2026-01 | Initial concatenation of 5 source documents |
| V2 | 2026-03 | Consolidated and deduplicated |
| V3 | 2026-03-05 | Removed bottom duplication, unified all concepts |
| V4 | 2026-03-05 | Added mandatory Git workflow diagram, TODOs implemented, expanded internal projects list |
| V5 | 2026-03-05 | Fixed TODOs, added .gitignore to template, added Port Configuration, added Shared Workspace Guidelines (aligned with AGENTS.md), fixed internal projects list alphabetically |
| V6 | 2026-03-05 | Added project descriptions section |
| V7 | 2026-03-05 | TODOs implemented - added detailed usage examples for each internal project, when-to-use guidance, ZMQ clarification (optional - use ogma for IPC only) |
| V8 | 2026-03-05 | Import details on internal project |
| V9 | 2026-03-06 | Fixed zuh copy-paste error (was using tuh path), clarified tuh/zuh purposes, fixed docs formatting TODO, added LICENSE to template, added zuh to Quick Reference |

---

*Last updated: 2026-03-06*
*Maintained by: Orin (AI Agent)*
