# AI Agent Governance Framework

Enterprise-grade governance framework for AI agents in regulated environments (Financial Services).

## Research Context

**Thesis Title:** Designing Robust Evaluation Metrics and Governance Frameworks for AI Agents Across Enterprise Workflows

**Research Question:** How can a regulated enterprise design, implement, and sustain a unified evaluation and governance framework, anchored by a formal Agent Registry, that reliably assesses the performance, safety, and accountability of autonomous AI agents across diverse and regulated business workflows?

## Features

- **Two-Layer Evaluation Framework:** Universal metrics + workflow-specific metrics
- **Agent Registry:** Persistent storage with CRUD operations
- **Governance Engine:** Rule-based compliance checking with audit trails
- **Risk-Based Controls:** Different rules for low/medium/high/critical risk agents
- **Immutable Audit Logs:** Tamper-evident logging with hash chains
- **Validation:** Pydantic models for data integrity

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python run_demo.py

# Or run sample
python framework/sample_run.py
