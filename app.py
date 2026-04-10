"""
HW2 — AFH Resident Reimbursement Optimization Tool
Uses Anthropic Claude API to analyze resident profiles and generate
structured reimbursement recommendation memos for Adult Family Home operators.
"""

import json
import sys
import os
from datetime import datetime
from anthropic import Anthropic

client = Anthropic()

# ---------------------------------------------------------------------------
# Configurable system prompt — edit this to tune model behavior
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Medicaid reimbursement specialist for Adult Family Homes (AFH) in Washington State. Your job is to analyze a resident's clinical and demographic profile and produce a structured recommendation memo for the AFH operator.

You must follow this exact output structure:

## 1. Rate Tier Assessment
Evaluate whether the resident's current Medicaid rate tier matches their documented acuity. Compare the resident's ADL dependencies, behavioral needs, and medical complexity against Washington State DSHS tier criteria. State clearly whether the current tier is appropriate or whether an upgrade is warranted, and explain why.

## 2. Specialty Contract Eligibility
Identify any specialty contracts the resident may qualify for, such as:
- Expanded Community Services (ECS)
- Specialized Behavior Support (SBS)
- Enhanced Adult Residential Care (EARC)
For each, explain why the resident does or does not qualify based on their profile.

## 3. Estimated Revenue Impact
Provide a rough estimate of the daily and monthly revenue difference between the current rate and the recommended rate or contract. Use approximate Washington State DSHS rate ranges. Be transparent that these are estimates.

## 4. Recommended Next Steps
Provide specific, actionable next steps the operator should take, including:
- Whether to request a DSHS reassessment
- What documentation to prepare
- Suggested language for the reassessment request
- Any additional clinical documentation that would strengthen the case

Important rules:
- If the resident's current tier appears appropriate, say so clearly. Do not fabricate upgrade opportunities.
- If information is missing or insufficient, identify exactly what is missing and why it matters. Do not guess.
- If the classification system does not match Washington State DSHS terminology, flag this immediately and ask for clarification before proceeding.
- Be specific and cite the resident's actual clinical details in your reasoning.
- Do not hallucinate rate numbers — use approximate ranges and label them as estimates."""


def format_resident_profile(profile: dict) -> str:
    """Convert a resident profile dict into a readable text block for the prompt."""
    lines = []
    lines.append(f"Name: {profile.get('name', 'Unknown')}")
    lines.append(f"Age: {profile.get('age', 'Unknown')}")
    lines.append(f"Diagnoses: {', '.join(profile.get('diagnoses', []))}")
    lines.append(f"Current Medicaid Tier: {profile.get('current_medicaid_tier', 'Unknown')}")
    lines.append(f"ADL Dependencies: {', '.join(profile.get('adl_dependencies', []))}")
    lines.append(f"Behavioral Notes: {profile.get('behavioral_notes', 'None reported')}")

    meds = profile.get('medications_requiring_delegation', [])
    lines.append(f"Medications Requiring Nurse Delegation: {', '.join(meds) if meds else 'None'}")

    services = profile.get('services_currently_provided', [])
    lines.append(f"Services Currently Provided: {', '.join(services) if services else 'None listed'}")

    months = profile.get('months_since_last_assessment', 'Unknown')
    lines.append(f"Months Since Last DSHS Assessment: {months}")

    return "\n".join(lines)


def analyze_resident(profile: dict, model: str = "claude-sonnet-4-20250514") -> str:
    """Send a resident profile to Claude and return the recommendation memo."""
    profile_text = format_resident_profile(profile)

    user_message = f"""Please analyze the following Adult Family Home resident profile and produce a reimbursement optimization recommendation memo.

RESIDENT PROFILE:
{profile_text}

Produce your recommendation memo following the required structure (Rate Tier Assessment, Specialty Contract Eligibility, Estimated Revenue Impact, Recommended Next Steps)."""

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def run_single(profile_path: str) -> None:
    """Analyze a single resident profile from a JSON file."""
    with open(profile_path) as f:
        data = json.load(f)

    # Support both a bare profile dict and an eval-set entry with resident_profile key
    profile = data.get("resident_profile", data)
    name = profile.get("name", "Unknown")

    print(f"\n{'='*60}")
    print(f"  Analyzing resident: {name}")
    print(f"{'='*60}\n")

    memo = analyze_resident(profile)
    print(memo)

    # Save output
    safe_name = name.replace(" ", "_").replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_{safe_name}_{timestamp}.md"
    with open(output_file, "w") as f:
        f.write(f"# Reimbursement Recommendation Memo — {name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(memo)

    print(f"\n[Saved to {output_file}]")


def run_eval(eval_path: str = "eval_set.json") -> None:
    """Run all evaluation cases and save results."""
    with open(eval_path) as f:
        eval_set = json.load(f)

    results = []
    for case in eval_set:
        case_id = case["id"]
        label = case.get("label", f"case_{case_id}")
        profile = case["resident_profile"]
        name = profile.get("name", "Unknown")

        print(f"\n[Case {case_id}: {label}] Analyzing {name}...")

        memo = analyze_resident(profile)
        results.append({
            "id": case_id,
            "label": label,
            "resident_name": name,
            "memo": memo,
            "expected_output_notes": case.get("expected_output_notes", ""),
        })
        print(f"[Case {case_id}] Done.")

    # Save all results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"eval_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nEvaluation complete — {len(results)} cases written to {output_file}")


def print_usage():
    print("""
AFH Resident Reimbursement Optimization Tool
=============================================

Usage:
  python app.py --eval                   Run all cases in eval_set.json
HW2 — AFH Resident Reimbursement Optimization Tool
Uses Anthropic Claude API to analyze resident profiles and generate
structured reimbursement recommendation memos for Adult Family Home operators.
"""

import json
import sys
import os
from datetime import datetime
from anthropic import Anthropic

client = Anthropic()

# ---------------------------------------------------------------------------
# Configurable system prompt — edit this to tune model behavior
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Medicaid reimbursement specialist for Adult Family Homes (AFH) in Washington State. Your job is to analyze a resident's clinical and demographic profile and produce a structured recommendation memo for the AFH operator.

You must follow this exact output structure:

## 1. Rate Tier Assessment
Evaluate whether the resident's current Medicaid rate tier matches their documented acuity. Compare the resident's ADL dependencies, behavioral needs, and medical complexity against Washington State DSHS tier criteria. State clearly whether the current tier is appropriate or whether an upgrade is warranted, and explain why.

## 2. Specialty Contract Eligibility
Identify any specialty contracts the resident may qualify for, such as:
- Expanded Community Services (ECS)
- Specialized Behavior Support (SBS)
- Enhanced Adult Residential Care (EARC)
For each, explain why the resident does or does not qualify based on their profile.

## 3. Estimated Revenue Impact
Provide a rough estimate of the daily and monthly revenue difference between the current rate and the recommended rate or contract. Use approximate Washington State DSHS rate ranges. Be transparent that these are estimates.

## 4. Recommended Next Steps
Provide specific, actionable next steps the operator should take, including:
- Whether to request a DSHS reassessment
- What documentation to prepare
- Suggested language for the reassessment request
- Any additional clinical documentation that would strengthen the case

Important rules:
- If the resident's current tier appears appropriate, say so clearly. Do not fabricate upgrade opportunities.
- If information is missing or insufficient, identify exactly what is missing and why it matters. Do not guess.
- If the classification system does not match Washington State DSHS terminology, flag this immediately and ask for clarification before proceeding.
- Be specific and cite the resident's actual clinical details in your reasoning.
- Do not hallucinate rate numbers — use approximate ranges and label them as estimates."""


def format_resident_profile(profile: dict) -> str:
    """Convert a resident profile dict into a readable text block for the prompt."""
    lines = []
    lines.append(f"Name: {profile.get('name', 'Unknown')}")
    lines.append(f"Age: {profile.get('age', 'Unknown')}")
    lines.append(f"Diagnoses: {', '.join(profile.get('diagnoses', []))}")
    lines.append(f"Current Medicaid Tier: {profile.get('current_medicaid_tier', 'Unknown')}")
    lines.append(f"ADL Dependencies: {', '.join(profile.get('adl_dependencies', []))}")
    lines.append(f"Behavioral Notes: {profile.get('behavioral_notes', 'None reported')}")

    meds = profile.get('medications_requiring_delegation', [])
    lines.append(f"Medications Requiring Nurse Delegation: {', '.join(meds) if meds else 'None'}")

    services = profile.get('services_currently_provided', [])
    lines.append(f"Services Currently Provided: {', '.join(services) if services else 'None listed'}")

    months = profile.get('months_since_last_assessment', 'Unknown')
    lines.append(f"Months Since Last DSHS Assessment: {months}")

    return "\n".join(lines)


def analyze_resident(profile: dict, model: str = "claude-sonnet-4-20250514") -> str:
    """Send a resident profile to Claude and return the recommendation memo."""
    profile_text = format_resident_profile(profile)

    user_message = f"""Please analyze the following Adult Family Home resident profile and produce a reimbursement optimization recommendation memo.

RESIDENT PROFILE:
{profile_text}

Produce your recommendation memo following the required structure (Rate Tier Assessment, Specialty Contract Eligibility, Estimated Revenue Impact, Recommended Next Steps)."""

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def run_single(profile_path: str) -> None:
    """Analyze a single resident profile from a JSON file."""
    with open(profile_path) as f:
        data = json.load(f)

    # Support both a bare profile dict and an eval-set entry with resident_profile key
    profile = data.get("resident_profile", data)
    name = profile.get("name", "Unknown")

    print(f"\n{'='*60}")
    print(f"  Analyzing resident: {name}")
    print(f"{'='*60}\n")

    memo = analyze_resident(profile)
    print(memo)

    # Save output
    safe_name = name.replace(" ", "_").replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_{safe_name}_{timestamp}.md"
    with open(output_file, "w") as f:
        f.write(f"# Reimbursement Recommendation Memo — {name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(memo)

    print(f"\n[Saved to {output_file}]")


def run_eval(eval_path: str = "eval_set.json") -> None:
    """Run all evaluation cases and save results."""
    with open(eval_path) as f:
        eval_set = json.load(f)

    results = []
    for case in eval_set:
        case_id = case["id"]
        label = case.get("label", f"case_{case_id}")
        profile = case["resident_profile"]
        name = profile.get("name", "Unknown")

        print(f"\n[Case {case_id}: {label}] Analyzing {name}...")

        memo = analyze_resident(profile)
        results.append({
            "id": case_id,
            "label": label,
            "resident_name": name,
            "memo": memo,
            "expected_output_notes": case.get("expected_output_notes", ""),
        })
        print(f"[Case {case_id}] Done.")

    # Save all results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"eval_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nEvaluation complete — {len(results)} cases written to {output_file}")


def print_usage():
    print("""
AFH Resident Reimbursement Optimization Tool
=============================================

Usage:
  python app.py --eval                   Run all cases in eval_set.json
  python app.py --eval path/to/set.json  Run all cases in a custom eval file
  python app.py --profile path/to/p.json Analyze a single resident profile
  python app.py                          Interactive mode (enter profile as JSON)
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--eval":
        eval_path = sys.argv[2] if len(sys.argv) > 2 else "eval_set.json"
        run_eval(eval_path)

    elif len(sys.argv) > 1 and sys.argv[1] == "--profile":
        if len(sys.argv) < 3:
            print("Error: --profile requires a path to a JSON file.")
            sys.exit(1)
        run_single(sys.argv[2])

    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()

    else:
        # Interactive mode — paste a JSON profile
        print_usage()
        print("Enter a resident profile as JSON (then press Ctrl+D when done):\n")
        try:
            raw = sys.stdin.read()
            profile = json.loads(raw)
            profile = profile.get("resident_profile", profile)
            memo = analyze_resident(profile)
            print(f"\n{'='*60}")
            print(memo)
        except json.JSONDecodeError:
            print("Error: Could not parse input as JSON.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nBye!")
