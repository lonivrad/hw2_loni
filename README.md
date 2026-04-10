# HW2 — LLM Application with Evaluation

## Overview
This project implements an LLM-powered application using the Anthropic Claude API, along with a structured evaluation set and performance report.

## Files
- `app.py` — Main application script
- `prompts.md` — Prompt templates and design rationale
- `eval_set.json` — Evaluation test cases (input/expected output pairs)
- `report.md` — Analysis of prompt performance and evaluation results

## Setup
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
python app.py
```

## Usage
```bash
python app.py
```

## Business Workflow
**Workflow:** Resident reimbursement optimization: converting a resident's clinical and demographic profile into a structured recommendation memo that identifies whether the AFH operator is billing at the correct Medicaid rate tier and whether the resident qualifies for higher-paying specialty contracts.

**User:** An Adult Family Home (AFH) operator in Washington State: typically a small business owner running a licensed 2–6 bed residential care facility for aging or disabled adults. Most operators are clinically capable but lack expertise navigating DSHS reimbursement structures, rate tiers, and specialty contract applications.

**Input:** A semi-structured resident profile including diagnosis, age, current Medicaid rate classification, ADL (activities of daily living) dependencies, behavioral notes, medications requiring nurse delegation, and services currently being provided in the home.

**Output:** A structured memo containing:
1. An assessment of whether the resident's current rate tier matches their documented acuity
2. Identification of any specialty contracts the resident may qualify for (e.g., Expanded Community Services, Specialized Behavior Support)
3. An estimated revenue impact of upgrading
4. A draft next-steps section with suggested language for requesting a DSHS reassessment

**Why automate?**
AFH operators routinely under-bill because they don't recognize when a resident's condition has changed enough to justify a higher rate tier, or they don't know specialty contracts exist. The difference between a base rate and an optimized rate can be $50–100+ per resident per day. Most operators have no advisor helping them identify this. DSHS doesn't proactively flag it, and compliance software like Synkwise doesn't touch reimbursement strategy. Even a partially automated screening tool that flags likely mismatches and drafts the recommendation saves hours of manual review and captures revenue the operator is already entitled to but isn't receiving.

## Youtube Link
https://youtu.be/eihKha3dB4U
