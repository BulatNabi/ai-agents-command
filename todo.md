

# 🚀 Project: Agentic Web Factory

**Goal:** A "Prompt-to-Deploy" system that orchestrates multiple agents to design, build, and deploy full-stack web applications to GitHub automatically.

---

## 🏗 Phase 1: Orchestration & Infrastructure

* [ ] **Orchestrator System Prompt:** Define the logic for `project-orchestrator` to decompose high-level ideas into technical specs for sub-agents.
* [ ] **Context Handover Protocol:** Establish a standard (e.g., via `.agent_logs/` or JSON schemas) so that the `react-frontend-expert` knows exactly what the `future-design-architect` proposed.
* [ ] **Agent Workspace Setup:** Configure `.claude/agents/` permissions to allow agents to execute bash commands and trigger each other.

## 🎨 Phase 2: User Interface (The Control Center)

* [ ] **Central Dashboard (React + Shadcn):**
* [ ] Create a "Main Idea" input field with high-level prompt support.
* [ ] Implement a real-time "Agent Status" tracker (showing which agent is currently working).
* [ ] Build a "Project Gallery" to list all deployed GitHub repositories.


* [ ] **Design Language:** Use `future-design-architect` to generate a futuristic, clean UI theme for the factory itself.

## ⚙️ Phase 3: Backend & MCP Integration

* [ ] **FastAPI Core:** Build the bridge between the UI and the Claude Code CLI.
* [ ] **GitHub MCP Configuration:** - [ ] Ensure the agent can create new private/public repositories.
* [ ] Automate the injection of GitHub Actions secrets.


* [ ] **Playwright Integration:** Set up `playwright` MCP for the "Reviewer" phase to perform automated UI testing before deployment.

## 🤖 Phase 4: Agent Workflow Pipeline

* [ ] **Step A: Planning:** `project-orchestrator` creates the roadmap.
* [ ] **Step B: Design:** `future-design-architect` generates the UI/UX components and color palettes.
* [ ] **Step C: Parallel Dev:**
* [ ] `fastapi-backend-dev` builds the API and DB schema.
* [ ] `react-frontend-expert` builds the UI using `shadcn` MCP.


* [ ] **Step D: Quality Control:** `project-orchestrator` runs tests and requests fixes if the build fails.
* [ ] **Step E: Deployment:** `devops-architect` configures CI/CD and pushes to GitHub.

## 🚀 Phase 5: CI/CD & DevOps Automation

* [ ] **Universal Workflow Template:** Create a reusable `.github/workflows/main.yml` for auto-deploying generated sites.
* [ ] **Environment Setup:** Automate the provisioning of hosting (GitHub Pages, Vercel, or VPS).

---

## 🛠 Active Sprint (Priority)

1. [ ] **Initialize** the "Factory" repository.
2. [ ] **Prompt Engineering:** Create the specialized instructions for the `devops-architect` to handle GitHub Actions.
3. [ ] **Proof of Concept:** Manually trigger the chain to deploy a simple "Hello World" site via the agents.

---

### Pro-Tip for your Setup:

Since you have the **GitHub MCP**, you should start by asking `devops-architect`:

> *"Using the GitHub MCP, create a new repository named 'agent-factory-core' and initialize it with a basic CI/CD workflow template."*

