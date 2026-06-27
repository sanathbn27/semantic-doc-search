import httpx

DOCUMENTS = [
    {
        "title": "Solar Panel Deployment Sequence",
        "content": "Detailed steps for deploying the photovoltaic arrays after orbital insertion. Includes hinge release commands, deployment angle monitoring, and power generation confirmation checks.",
    },
    {
        "title": "Thermal Control System Overview",
        "content": "Description of the passive and active thermal regulation mechanisms onboard Nyx. Covers heat pipe routing, multi-layer insulation zones, and heater activation thresholds.",
    },
    {
        "title": "Communication Link Budget",
        "content": "Analysis of the S-band uplink and downlink margins. Includes antenna gain figures, free-space path loss calculations, and minimum required Eb/N0 for command reception.",
    },
    {
        "title": "Propellant Tank Pressurisation Procedure",
        "content": "Step-by-step guide for pressurising the hydrazine tank prior to orbital manoeuvre. Covers regulator settings, pressure transducer readings, and abort criteria.",
    },
]

for doc in DOCUMENTS:
    response = httpx.post("http://127.0.0.1:8000/documents", json=doc)
    print(response.status_code, response.json()["id"], response.json()["title"])