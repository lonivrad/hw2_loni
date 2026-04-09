"""
HW2 — LLM Application using Anthropic Claude API
"""

import json
import os
import sys
from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question clearly and concisely."""


def query(user_input: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Send a single query to Claude and return the response text."""
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_input}],
    )
    return message.content[0].text


def run_eval(eval_path: str = "eval_set.json") -> list[dict]:
    """Run all evaluation cases and return results."""
    with open(eval_path) as f:
        eval_set = json.load(f)

    results = []
    for case in eval_set:
        response = query(case["input"])
        results.append(
            {
                "id": case["id"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": response,
            }
        )
        print(f"[{case['id']}] done")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--eval":
        results = run_eval()
        with open("eval_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nEvaluation complete — {len(results)} cases written to eval_results.json")
    else:
        # Interactive mode
        print("Enter a prompt (Ctrl+C to quit):")
        while True:
            try:
                user_input = input("> ")
                print(query(user_input))
            except KeyboardInterrupt:
                print("\nBye!")
                break
