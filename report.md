# Report — AFH Reimbursement Optimization Memo Generator

**Author:** Loni Vrad
**Course:** Week 2 GenAI Workflow Assignment
**Model:** Anthropic Claude Sonnet 4 (`claude-sonnet-4-20250514`)
**Date:** April 2026

---

## Business Use Case

Adult Family Homes (AFHs) in Washington State are small, licensed residential care facilities — typically 2–6 beds — serving aging and disabled adults under DSHS Medicaid contracts. Operators are generally clinically capable but rarely have the administrative expertise to optimize reimbursement under DSHS's tiered rate structure and specialty contract system (Expanded Community Services, Specialized Behavior Support, Enhanced Adult Residential Care).

This prototype automates the first pass of a reimbursement review: given a semi-structured resident profile (diagnoses, ADL dependencies, nurse delegation tasks, current Medicaid tier, behavioral notes), the system produces a structured memo assessing tier accuracy, specialty contract eligibility, estimated revenue impact, and a draft DSHS reassessment request.

The revenue opportunity is material: the difference between a base Tier 1 rate and a correctly documented Tier 2 or specialty contract rate can exceed $50–100/resident/day. Most operators lose this revenue not through fraud or negligence, but through lack of awareness — DSHS does not proactively flag mismatches, and dominant AFH compliance platforms do not address reimbursement strategy.

---

## Model Selection

**Primary model: Anthropic Claude Sonnet 4 (`claude-sonnet-4-20250514`)** via the Anthropic Messages API.

Chosen for three reasons: (1) strong instruction-following on structured, multi-section output tasks, which matters for this workflow because operators need a consistent memo format they can review at a glance; (2) demonstrated caution on refusal-style edge cases (flagging incomplete information instead of guessing), which directly maps to the hallucination-avoidance requirements of a clinical/regulatory domain; (3) practical fit with the 2048-token memo length this workflow requires.

Only Claude Sonnet was tested in this prototype cycle. The prompt design is model-agnostic and could be ported to GPT-4o or Gemini with minor adjustment — the structure of the four-section memo and the "Important rules" block would carry over cleanly. A production version would benefit from A/B testing across models on the same evaluation set before committing.

---

## Baseline vs. Final Design

All three prompt versions were benchmarked against the same 6-case evaluation set (`eval_set.json`). Full memo outputs are in `output.md`; the full iteration rationale is in `prompts.md`.

### Initial Version (Baseline)
A minimal system prompt with no output structure, no named specialty contracts, and no uncertainty guardrails. Observed failure modes: inconsistent output format across cases (sometimes bullets, sometimes prose); fabricated specific dollar figures with false precision (e.g., "$3,847/month"); confident tier recommendations even on vague input (Case 4); underweighting of behavioral complexity on multi-contract cases (Case 3).

### Revision 1
Added a required four-section output structure, named the three specialty contracts (ECS, SBS, EARC), swapped specific revenue figures for ranges with disclaimers, and added an explicit "say so rather than guess" instruction for vague inputs. Observed improvement: consistent formatting across all cases; Case 4 (Yun S., incomplete info) started correctly flagging data gaps; revenue figures shifted to properly caveated ranges. Remaining issue: tone was still generic, and Case 3 (David L., multiple contracts) still under-weighted Specialized Behavior Support because the prompt did not spell out SBS eligibility criteria.

### Revision 2 (Final — current version in `app.py`)
Added a dedicated "Important rules" block including a guardrail against non-WA classification systems (motivated by Case 5, the anticipated out-of-state failure), explicit "do not fabricate upgrade opportunities" language, and stronger cite-your-reasoning requirements.

**Final results on the 6-case eval set:** 5 clean passes, 1 partial failure.

| ID | Case | Pass/Fail | Key observation |
|----|------|-----------|-----------------|
| 1 | Margaret T. (clear upgrade) | **PASS** | Correctly flagged Tier 1 as inappropriate; identified SBS eligibility; flagged 14-month-overdue assessment |
| 2 | Robert K. (already optimized) | **PASS** | Correctly held Tier 1; did not hallucinate any upgrade opportunity |
| 3 | David L. (multi-contract) | **PASS** | Identified Tier 2→3 upgrade plus overlapping SBS/ECS/EARC eligibility with sequencing notes |
| 4 | Yun S. (incomplete info) | **PASS** | Refused to guess; produced concrete data-gathering checklist |
| 5 | Clara M. (out-of-state) | **PARTIAL FAIL** | Noted "Level of Care B" as atypical but still produced WA-specific advice |
| 6 | Helen P. (new admission, no tier yet) | **PASS** | Adapted workflow to pre-assignment scenario instead of rigidly comparing tiers |

The iteration cycle directly demonstrates evidence-based prompt improvement: each revision was motivated by a specific failure mode observed in the preceding version's outputs, and each measurable improvement can be traced back to a specific prompt change.

---

## Where the Prototype Still Fails

The partial failure on **Case 5 (out-of-state resident)** is the most important gap. The Revision 2 rule ("flag this immediately and ask for clarification") is too soft — the model acknowledged the classification mismatch but still produced a full WA-specific memo rather than refusing to proceed. This is a known LLM tendency to prefer helpful-sounding output over refusal, and in this domain it could mislead an operator into applying WA-specific guidance to a non-WA case. A Revision 3 would need categorical refusal language ("you MUST stop and refuse to provide any tier or contract recommendations until the operator confirms the state").

Three additional gaps require human review in any deployed version: (1) **Revenue estimates are imprecise** — the model uses labeled ranges as instructed, but without a live DSHS rate-table lookup, figures may drift as annual rates change; (2) **Documentation quality assumption** — the system trusts the operator's input profile and cannot detect undocumented nurse delegation tasks that would weaken a reassessment request; (3) **Specialty contract eligibility is advisory, not determinative** — DSHS outcomes depend on in-person assessment, so model outputs should be treated as screening flags, not guarantees.

---

## Deployment Recommendation

**Conditionally recommended for deployment as a screening and drafting tool — not as a standalone decision system.**

The evaluation shows that Claude Sonnet 4 with the Revision 2 prompt handles the core workflow reliably: it correctly assesses tier appropriateness in both directions (upgrade warranted vs. already optimized), avoids hallucination on incomplete input, reasons about overlapping specialty contract eligibility, and adapts to non-standard scenarios like new admissions. This is meaningful value — operators currently leave significant revenue on the table because no first-pass review exists at their scale.

However, deployment should require four conditions: (1) **human review** by a knowledgeable advisor (a care manager, social worker, or experienced operator) before any memo is sent to DSHS; (2) a **connected DSHS rate table**, updated at least annually, to ground revenue estimates; (3) **explicit disclosure** to operators that outputs are advisory and require professional verification; (4) a **confidence indicator** in the UI — memos generated from incomplete profiles (like Case 4) or flagged classification mismatches (like Case 5) should be visually marked as low-confidence, and the out-of-state guardrail must be hardened via a Revision 3 prompt before go-live.

Under these conditions, the tool meaningfully reduces time spent on first-pass review and surfaces revenue operators are entitled to but currently missing. Without them — particularly without human review and the Case 5 fix — the risk of a misapplied recommendation in a clinical/regulatory context outweighs the workflow benefit.
