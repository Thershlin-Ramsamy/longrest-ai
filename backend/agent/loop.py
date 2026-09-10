"""
The core agent loop.

This is the heart of Longrest: give Claude a bug report and a set of tools,
let it look around, make a fix, and check its own work by running tests -
looping until the tests pass or it runs out of turns.

No GitHub, no sandboxing, no approval step yet. Those come later, once this
loop is solid on its own.
"""

import os

import anthropic
from dotenv import load_dotenv

from agent.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-5"
MAX_TURNS = 8

SYSTEM_PROMPT = """You are Longrest, an autonomous coding agent. You are given a bug report for a
small repository. Your job is:

1. Explore the repo with list_files and read_file to understand the bug.
2. Use write_file to apply the smallest fix that resolves it. Never rewrite unrelated code.
3. Run run_tests after every fix attempt.
4. Stop as soon as the tests pass, and reply with a short plain-language summary of what
   you changed and why, in your final message, with no further tool calls.

If tests still fail after your fix, look closely at the failure output and try again.
"""


def run_agent(issue_description: str) -> str:
    messages = [{"role": "user", "content": issue_description}]

    for turn in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            summary = "\n".join(block.text for block in response.content if block.type == "text")
            print("\n=== AGENT SUMMARY ===")
            print(summary)
            return summary

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n[turn {turn}] calling {block.name}({block.input})")
                fn = TOOL_FUNCTIONS[block.name]
                try:
                    result = fn(block.input)
                except Exception as e:  # noqa: BLE001 - surface any tool error back to the model
                    result = f"ERROR: {e}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )

        messages.append({"role": "user", "content": tool_results})

    message = "Hit the turn limit without the agent finishing on its own - check the log above."
    print(f"\n{message}")
    return message
