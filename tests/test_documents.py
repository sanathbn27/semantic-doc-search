SAMPLE_DOCUMENTS = [
    {
        "title": "RCS Thruster Firing Procedure",
        "content": "This procedure describes the cold gas thruster ignition sequence for the reaction control system. It covers pre-ignition checks, valve actuation order, and post-firing telemetry verification.",
    },
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


def seed_documents(client):
    ids = []
    for doc in SAMPLE_DOCUMENTS:
        response = client.post("/documents", json=doc)
        assert response.status_code == 201
        ids.append(response.json()["id"])
    return ids


def test_search_returns_semantically_relevant_top_result(client):
    seed_documents(client)

    response = client.get("/documents/search", params={"q": "thruster firing sequence"})

    assert response.status_code == 200
    results = response.json()

    assert len(results) > 0
    assert results[0]["title"] == "RCS Thruster Firing Procedure"
    assert results[0]["score"] > results[-1]["score"]


def test_search_respects_top_k_limit(client):
    seed_documents(client)

    response = client.get(
        "/documents/search", params={"q": "spacecraft systems", "top_k": 2}
    )

    assert response.status_code == 200
    results = response.json()

    assert len(results) == 2
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_delete_removes_document_from_search_results(client):
    ids = seed_documents(client)
    rcs_thruster_id = ids[0]

    delete_response = client.delete(f"/documents/{rcs_thruster_id}")
    assert delete_response.status_code == 204

    search_response = client.get(
        "/documents/search", params={"q": "thruster firing sequence"}
    )
    results = search_response.json()
    returned_titles = [r["title"] for r in results]

    assert "RCS Thruster Firing Procedure" not in returned_titles


def test_create_document_rejects_empty_title(client):
    response = client.post(
        "/documents", json={"title": "", "content": "Some valid content here."}
    )

    assert response.status_code == 422


def test_delete_nonexistent_document_returns_404(client):
    response = client.delete("/documents/99999")

    assert response.status_code == 404


def test_create_document_returns_correct_shape(client):
    response = client.post(
        "/documents",
        json={"title": "Test Document", "content": "Some test content."},
    )

    assert response.status_code == 201
    body = response.json()

    assert body["title"] == "Test Document"
    assert body["content"] == "Some test content."
    assert "id" in body
    assert "created_at" in body
    assert "embedding" not in body


def test_search_rejects_empty_query(client):
    response = client.get("/documents/search", params={"q": "   "})

    assert response.status_code == 422