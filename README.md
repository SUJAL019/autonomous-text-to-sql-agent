# Autonomous Text-to-SQL AI Agent (Native Python)

A containerized, autonomous Text-to-SQL analyst built from scratch using raw Python and OpenRouter's tool-calling interface—free from orchestration frameworks (no LangChain/CrewAI).

## Key Architecture Features

- **Native Execution Loop:** Custom `while` loop managing parallel tool calling, dynamic function dispatch, and message state history without third-party wrapper overhead.
- **Circuit Breaker:** Hard threshold (`max_iterations = 5`) to prevent runaway API recursion and compute cost blowouts.
- **Strict Read-Only Guardrails:** Deterministic AST/string inspection intercepting queries prior to database execution. Non-`SELECT` statements (`UPDATE`, `DROP`, `INSERT`) trigger immediate security violations returned to agent memory.
- **Self-Healing Loop:** Catches SQLite execution syntax and schema mismatches, feeding raw error tracebacks back into the conversation context for autonomous self-correction.

## Tech Stack

- **Runtime:** Python 3.11, Docker
- **Database:** SQLite3
- **Inference:** OpenRouter (`meta-llama/llama-3.3-70b-instruct`)

## Quickstart

### Run with Docker

1. Clone the repository:
   ```bash
   git clone [https://github.com/sujal019/autonomous-text-to-sql-agent.git](https://github.com/sujal019/autonomous-text-to-sql-agent.git)
   cd autonomous-text-to-sql-agent