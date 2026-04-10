# Evaluation Report

## Summary

Ran 6 evaluation cases against the AFH Resident Reimbursement Optimization tool using Claude Sonnet (`claude-sonnet-4-20250514`). The tool performed well on standard cases and most edge cases. 5 of 6 cases passed, with 1 partial failure on the out-of-state terminology detection case.

## Methodology

- **Model:** `claude-sonnet-4-20250514` (Anthropic Claude API)
- **System prompt version:** v1 (see `prompts.md` / `app.py` SYSTEM_PROMPT)
- **Eval cases:** 6 (see `eval_set.json`)
- **Metrics:** Manual review against expected output notes — evaluated on correctness of tier assessment, specialty contract identification, hallucination avoidance, and handling of missing/ambiguous information
- **Date run:** 2026-04-09

## Results

| ID | Label | Resident | Pass/Fail | Notes |
|----|-------|----------|-----------|-------|
| 1 | normal_case_clear_upgrade | Margaret T. | **PASS** | Correctly identified Tier 1 as inappropriate. Recommended Tier 2/3 upgrade. Flagged overdue assessment (14 months). Identified Specialized Behavior Support eligibility due to wandering/sundowning. Revenue impact estimate included. |
| 2 | normal_case_already_optimized | Robert K. | **PASS** | Correctly confirmed Tier 1 is appropriate. Did not hallucinate upgrade opportunities. Acknowledged operator is billing correctly. No specialty contract eligibility identified. |
| 3 | edge_case_multiple_specialty_contracts | David L. | **PASS** | Identified Tier 2 → Tier 3 upgrade. Flagged multiple specialty contract eligibility (SBS, ECS, EARC). Provided reasoning about overlapping eligibility. Included revenue impact estimates and sequencing guidance. |
| 4 | edge_case_incomplete_information | Yun S. | **PASS** | Correctly refused to guess. Identified missing information: specific ADL dependencies, medication list, current tier, last assessment date. Provided concrete checklist for the operator. Did not hallucinate a confident recommendation from vague input. |
| 5 | likely_failure_out_of_state_resident | Clara M. | **PARTIAL FAIL** | Did not immediately flag that "Level of Care B" is not WA DSHS terminology. Instead proceeded with analysis using the non-WA classification, though did note the terminology was atypical. The system prompt instructs the model to flag classification mismatches, but the model only partially followed this — it noted the issue but still provided WA-specific advice rather than declining until clarification. |
| 6 | edge_case_new_admission_no_rate_yet | Helen P. | **PASS** | Adapted workflow to pre-assignment scenario. Recommended initial Tier 3 based on clinical profile. Identified specialty contract eligibility to pursue once Medicaid is active. Advised on documentation from day one. Did not rigidly follow upgrade-detection pattern. |

## Analysis

### What worked well
- **Tier assessment accuracy:** The model correctly assessed tier appropriateness in all standard cases — both when an upgrade was warranted (Case 1) and when the current tier was correct (Case 2).
- **Hallucination avoidance:** Case 2 (already optimized) and Case 4 (incomplete info) both tested whether the model would fabricate recommendations. It did not — it correctly said "no upgrade needed" and "insufficient information" respectively.
- **Complex reasoning:** Case 3 required reasoning about multiple overlapping specialty contracts without double-counting. The model handled this well, identifying SBS, ECS, and EARC eligibility with appropriate nuance.
- **Workflow adaptation:** Case 6 (new admission, no tier yet) required the model to shift from its default "compare current vs. recommended tier" pattern to a "recommend initial tier" pattern. It adapted correctly.
- **Structured output:** All 6 cases followed the required 4-section memo format consistently.

### What didn't work well
- **Out-of-state detection (Case 5):** This was the predicted failure case. The system prompt explicitly instructs the model to flag classification mismatches, but the model only partially complied. It noted "Level of Care B" was atypical but still provided WA-specific analysis rather than stopping and requesting clarification. This is a known LLM tendency — models prefer to give helpful-sounding answers rather than declining to answer.

### Prompt improvement opportunities
1. **Stronger guardrail for classification mismatch:** The system prompt could be more forceful — e.g., "If the classification system does not match WA DSHS terminology, you MUST stop and refuse to proceed until the state is confirmed. Do NOT provide WA-specific advice if the terminology is from another state."
2. **Rate number specificity:** The model uses approximate ranges as instructed, but some outputs could be more specific about which DSHS rate schedule they reference.
3. **Assessment timeline flagging:** Case 1 correctly flagged the overdue assessment, but this could be made a standard check across all cases via prompt engineering.

## Conclusion

The AFH Resident Reimbursement Optimization tool performs well across standard and edge cases. It correctly identifies upgrade opportunities, avoids hallucination on already-optimized or incomplete cases, handles complex multi-contract eligibility, and adapts to non-standard scenarios like new admissions. The primary weakness is insufficient guardrailing on out-of-state classification detection — a prompt iteration adding stronger refusal language for terminology mismatches would likely fix this. Overall, 5/6 cases passed on the first prompt version, which is a strong baseline for iteration.
