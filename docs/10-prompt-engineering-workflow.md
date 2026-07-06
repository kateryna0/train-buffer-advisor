# 10 — Prompt Engineering Workflow

## Purpose

This document explains how GenAI / Claude Code will be used in the project. The goal is to make the project credible for a CV without falsely claiming that the app itself is an LLM product.

## Correct positioning

Before implementation:

> Designed a product concept and technical specification for an AI-assisted decision-support app for German rail travel.

After implementation:

> Built a Python/Streamlit decision-support app using AI-assisted development workflows with Claude Code, structured prompting, iterative debugging, and transparent rule-based logic.

Avoid saying:

> Built a GenAI app that predicts Deutsche Bahn delays.

That would be inaccurate unless the deployed product actually uses an LLM in the user-facing experience.

## What prompt engineering means in this project

Prompt engineering is used to:

- turn a vague idea into a structured product concept;
- critique the product from multiple professional roles;
- convert market research into requirements;
- generate and refine a v1 specification;
- break implementation into small tasks;
- ask Claude Code for code changes with clear acceptance criteria;
- debug errors by providing context and expected behavior;
- generate tests from rule specifications;
- improve README and documentation.

## Workflow structure

### Step 1 — Product discovery prompts

Goal: clarify problem, user, competition, and scope.

Example prompt:

```text
Act as a Product Owner and Business Analyst. Evaluate this idea for a portfolio project: TrainBuffer, a deadline-based buffer advisor for Deutsche Bahn trips. Identify user segments, competitors, core use cases, and why users would open this instead of DB Navigator.
```

### Step 2 — Four-role critique prompts

Goal: pressure-test the idea before coding.

Example prompt:

```text
Act as a Staff Engineer, Engineering Manager, Product Owner, and Business Analyst. Audit this product concept. Identify critical missing requirements, technical risks, scope risks, business risks, and measurement gaps. Give a priority table.
```

### Step 3 — Specification prompts

Goal: convert idea into buildable requirements.

Example prompt:

```text
Convert this product concept into a v1 product specification. Include in-scope/out-of-scope, inputs, outputs, functional requirements, non-functional requirements, acceptance criteria, and Definition of Done. Keep v1 realistic for a beginner Python/Streamlit portfolio project.
```

### Step 4 — Rule-design prompts

Goal: create transparent, testable logic.

Example prompt:

```text
Design a simple rule-based risk engine for TrainBuffer. Use historical late rate, cancellation rate, sample size confidence, weather modifiers, trip type, and arrival deadline. Calculate recommended buffer and latest_safe_planned_arrival = deadline - buffer. Avoid machine learning. Return explicit thresholds and test cases.
```

### Step 5 — Implementation prompts for Claude Code

Goal: build small pieces, one at a time.

Example prompt:

```text
Implement only the risk engine. Do not build Streamlit UI yet.
Create src/risk_engine.py with calculate_recommendation().
Use the rules in docs/07-risk-rule-spec.md.
Create pytest tests for Low, Medium, High, No Data, cancellation upgrade, and weather cap cases.
Do not add external dependencies unless necessary.
```

### Step 6 — Debugging prompts

Goal: debug with context, not vague complaints.

Bad prompt:

```text
It does not work. Fix it.
```

Good prompt:

```text
The test test_cancellation_upgrade fails. Expected risk_level='Medium' but got 'Low'. Here is the rule: cancel_rate > 5% upgrades risk by one level. Inspect src/risk_engine.py and update only the cancellation logic. Do not change unrelated tests.
```

### Step 7 — Documentation prompts

Goal: turn the build into a portfolio asset.

Example prompt:

```text
Update README.md for a recruiter and technical reviewer. Include problem, solution, demo, architecture, data sources, limitations, how to run locally, and what I learned. Keep it honest: this is a rule-based decision-support app, not an exact delay predictor.
```

## Prompt log format

Create a file later:

```text
docs/prompt-log.md
```

Each important prompt should be logged as:

```text
## Prompt 001 — Product critique
Date:
Goal:
Prompt:
Output used:
Decision made:
What I changed manually:
```

## Why this matters for CV

A recruiter or hiring manager should see that AI was not used randomly. It was used as a structured development partner.

This demonstrates:

- prompt engineering;
- product thinking;
- technical decomposition;
- iterative development;
- code review mindset;
- ability to use GenAI responsibly.

## AI-assisted development rules

1. **Never accept generated code blindly.** Read and test it.
2. **Prompt for one small task at a time.** Avoid “build the whole app”.
3. **Use docs as source of truth.** Claude Code should follow the spec, not invent product logic.
4. **Write tests before UI polish.** Core logic must be reliable.
5. **Log important prompts and decisions.** This proves the workflow.
6. **Be honest in README and CV.** Say AI-assisted development, not user-facing GenAI, unless an LLM feature exists.

## Recommended Claude Code build sequence

```text
1. Create repo structure.
2. Add docs.
3. Implement risk engine.
4. Add tests.
5. Add sample station reliability data.
6. Add weather module.
7. Add explanation generator.
8. Build Streamlit UI.
9. Add README and screenshots.
10. Deploy.
```

## Interview explanation

Use this framing:

> I used Claude Code as an AI-assisted development partner, but I controlled the product logic through documentation and acceptance criteria. I first defined the product, researched competitors, wrote the v1 specification and risk rules, then prompted Claude Code to implement small testable modules. The project demonstrates prompt engineering, product thinking, data reasoning, and beginner-friendly Python/Streamlit implementation.
