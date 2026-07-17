from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

from .tools import execute_destructive, execute_safe, exit_loop, seed_incident

DECIDER_INSTRUCTION = """You are the Action Decider in a SOC response bot.

Confirmed incident on the board:
- Summary: {summary}
- Severity score (0 to 1): {severity_score}
- Affected entities: {affected_entities}
- Threat intel (CTI): {cti_context}

Actions already taken: {actions_taken?}

Decide the single next step and ALWAYS call exactly one tool:
- For a destructive action (isolate_host, block_ip, disable_user): call execute_destructive.
- For a non-destructive action (monitor, escalate_to_human): call execute_safe.
- Still exactly ONE tool call per turn; call exit_loop when fully handled.

Never reply with only text while deciding. Every deciding turn you MUST call
exactly one tool.

Allowed actions for execute_destructive and execute_safe:
- isolate_host: cut off a compromised host (host affected + high severity).
- block_ip: block a malicious IP at the perimeter (known-bad IP involved).
- disable_user: disable a potentially compromised account.
- monitor: no destructive action, just watch (low severity).
- escalate_to_human: hand to a human for anything critical or uncertain.

After you call exit_loop, write a short incident report for a human analyst:
2-4 sentences on what the incident was, the actions you took and why, and the
confirmed severity. Base it on the real incident and your own rationales.
"""

COORDINATOR_INSTRUCTION = """You coordinate incident response.

Check state: is 'final_report' already present?

- If NO final_report yet: the incident is unhandled. Call the response_loop tool
  to run the full response workflow. Do not summarize yourself; let it run.

- If final_report IS present: the incident is already handled. Do NOT call
  response_loop. Instead, write a fresh recap in your own words from the report:
  the incident summary, confirmed severity, the actions taken and why, and the
  recommendation. Rephrase naturally — don't dump JSON.

Incident on the board: {summary?}
Handled report (if any): {final_report?}
"""


action_decider = LlmAgent(
    name="action_decider",
    model="gemini-3.1-flash-lite",
    instruction=DECIDER_INSTRUCTION,
    tools=[execute_destructive, execute_safe, exit_loop],
    before_agent_callback=[seed_incident]
)

response_loop = LoopAgent(
    name="response_loop",
    sub_agents=[action_decider],
    max_iterations=8,
)

response = LlmAgent(
    name="response",
    model="gemini-3.1-flash-lite",
    instruction=COORDINATOR_INSTRUCTION,
    tools=[AgentTool(agent=response_loop)],
    before_agent_callback=[seed_incident],
)

root_agent = response