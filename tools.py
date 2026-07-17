from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from response_bot.mock import FAKE_INCIDENT, SEVERITY_BANDS

AUTO_APPROVE = False

def seed_incident(callback_context: CallbackContext):
    state = callback_context.state
    if "incident_id" not in state:
        for key, value in FAKE_INCIDENT.items():
            state[key] = value

def _band(score: float) -> str:
    for threshold, name in SEVERITY_BANDS:
        if score >= threshold:
            return name
    return "LOW"


def _recommend(confirmed: str, actions: list) -> str:
    if any(a["action"] == "escalate_to_human" for a in actions):
        return "escalate"
    if confirmed in ("LOW", "MEDIUM"):
        return "monitor"
    return "contained"


def _record(action, rationale, tool_context, note=""):
    observation = f"[DRY-RUN] would perform '{action}'{note}"
    history = tool_context.state.get("actions_taken", [])
    history.append({"action": action, "rationale": rationale, "result": observation})
    tool_context.state["actions_taken"] = history
    tool_context.actions.skip_summarization = True
    return {"status": "ok", "observation": observation}


def execute_destructive(action: str, rationale: str, tool_context: ToolContext) -> dict:
    """Execute a DESTRUCTIVE containment action (isolate_host, block_ip, disable_user),
    subject to the approval policy.

    Args:
        action: one of 'isolate_host', 'block_ip', 'disable_user'.
        rationale: one sentence explaining why.
    """
    if not AUTO_APPROVE:
        # gate CLOSED: do not execute; record as pending instead
        history = tool_context.state.get("actions_taken", [])
        history.append({
            "action": action,
            "rationale": rationale,
            "result": "[BLOCKED - awaiting human approval, NOT executed]",
        })
        tool_context.state["actions_taken"] = history
        tool_context.actions.skip_summarization = True
        return {"status": "blocked", "observation": "awaiting human approval"}

    # gate OPEN: execute normally
    return _record(action, rationale, tool_context, note=" [approved]")


def execute_safe(action: str, rationale: str, tool_context: ToolContext) -> dict:
    """Execute a NON-destructive action (no approval needed).

    Args:
        action: one of 'monitor', 'escalate_to_human'.
        rationale: one sentence explaining why.
    """
    return _record(action, rationale, tool_context)


def exit_loop(tool_context: ToolContext) -> dict:
    """Call ONLY when the incident is fully handled. Confirms severity,
    builds the final report, and ends the response loop."""
    state = tool_context.state
    actions = state.get("actions_taken", [])
    score = state.get("severity_score", 0.0)

    confirmed = _band(score)
    state["confirmed_severity"] = confirmed

    report = {
        "incident_id": state.get("incident_id"),
        "summary": state.get("summary"),
        "confirmed_severity": confirmed,
        "actions_taken": [
            {"action": a["action"], "rationale": a["rationale"]} for a in actions
        ],
        "recommendation": _recommend(confirmed, actions),
    }
    state["final_report"] = report

    tool_context.actions.escalate = True
    # no skip_summarization here — we WANT the prose report now
    return {"status": "incident_handled", "final_report": report}