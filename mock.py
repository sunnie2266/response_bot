INCIDENTS = {
    "critical_host": {
        "incident_id": "inc-001",
        "severity_score": 0.88,
        "summary": "Credential dumping on host-12",
        "affected_entities": [
            {"type": "host", "value": "host-12"},
            {"type": "ip", "value": "185.203.116.4"},
        ],
        "cti_context": {"ttps": ["T1003"], "iocs": ["185.203.116.4"]},
    },
    "low_noise": {
        "incident_id": "inc-002",
        "severity_score": 0.15,
        "summary": "Single failed login for user alice from a known corporate IP",
        "affected_entities": [{"type": "user", "value": "alice@corp.local"}],
        "cti_context": {"ttps": [], "iocs": []},
    },
    "user_compromise": {
        "incident_id": "inc-003",
        "severity_score": 0.7,
        "summary": "Impossible-travel logins for svc-backup; likely stolen credentials",
        "affected_entities": [
            {"type": "user", "value": "svc-backup@corp.local"},
            {"type": "host", "value": "host-30"},
        ],
        "cti_context": {"ttps": ["T1078"], "iocs": []},
    },
    "critical_escalate": {
        "incident_id": "inc-004",
        "severity_score": 0.96,
        "summary": "Active ransomware encryption spreading across finance subnet",
        "affected_entities": [
            {"type": "host", "value": "fin-07"},
            {"type": "host", "value": "fin-08"},
            {"type": "ip", "value": "91.240.118.22"},
            {"type": "user", "value": "cfo@corp.local"},
        ],
        "cti_context": {"ttps": ["T1486", "T1021"], "iocs": ["91.240.118.22"]},
    },
}

# Pick which incident to run. Change this and restart adk web to test another.
ACTIVE = "user_compromise"
FAKE_INCIDENT = INCIDENTS[ACTIVE]

SEVERITY_BANDS = [(0.85, "CRITICAL"), (0.6, "HIGH"), (0.3, "MEDIUM"), (0.0, "LOW")]