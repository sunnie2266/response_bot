FAKE_INCIDENT = {
    "incident_id": "inc-001",
    "severity_score": 0.88,
    "summary": "Credential dumping on host-12",
    "affected_entities": [
        {"type": "host", "value": "host-12"},
        {"type": "ip", "value": "185.203.116.4"},
    ],
    "cti_context": {"ttps": ["T1003"], "iocs": ["185.203.116.4"]},
}