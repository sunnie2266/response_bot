from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

from response_bot.mock import FAKE_INCIDENT

def seed_incident(callback_context: CallbackContext):
    """Runs before the agent. Puts the mock incident on the whiteboard,
    but only once — don't re-seed if it's already there."""
    state = callback_context.state
    if "incident_id" not in state:
        for key, value in FAKE_INCIDENT.items():
            state[key] = value

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-3.5-flash",
    instruction="""You are a SOC assistant. Say hi and wait.
    A confirmed security incident is on the board:
- Summary: {summary}
- Severity score (0 to 1): {severity_score}
- Affected entities: {affected_entities}
- Threat intel (CTI): {cti_context}

Your job: choose the SINGLE next response action for this incident.

Allowed actions:
- isolate_host: cut a compromised host off the network. Use when a host is affected and severity is high.
- block_ip: block a malicious IP at the perimeter. Use when a known-bad IP is involved.
- disable_user: disable a potentially compromised account.
- monitor: no destructive action, just watch. Use for low severity.
- escalate_to_human: hand to a human for anything critical or uncertain.
- done: no further action needed.

Respond with ONLY a JSON object, no other text:
{"action": "<one allowed action>", "rationale": "<one sentence why>"}
""",
    output_key="latest_decision",
    before_agent_callback=seed_incident,
)