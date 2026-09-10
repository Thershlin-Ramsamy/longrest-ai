from agent.loop import run_agent

ISSUE = """
Bug report: calculator.add(2, 2) is returning 5 instead of 4.
There's a test in test_calculator.py that reproduces this. Please investigate and fix it.
"""

if __name__ == "__main__":
    run_agent(ISSUE)
