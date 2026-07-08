from app import app


def test_wizard_asks_questions_one_by_one():
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Does the contract specify which country's law to use?" in response.data

    response = client.post("/", data={"step": "0", "explicit_law": "N"})
    assert response.status_code == 200
    assert b"Do you know which nationality should be used for Party 1?" in response.data

    response = client.post("/", data={"step": "1", "party1_country": "Singapore"})
    assert response.status_code == 200
    assert b"Do you know which nationality should be used for Party 2?" in response.data


def test_wizard_resolves_party2_nationality_and_contract_place():
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "step": "0",
            "explicit_law": "N",
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/",
        data={
            "step": "1",
            "party1_country": "Singapore",
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/",
        data={
            "step": "2",
            "party2_country": "N",
        },
    )
    assert response.status_code == 200
    assert b"Is Party 2 a natural person or a juristic person?" in response.data

    response = client.post(
        "/",
        data={
            "step": "3",
            "party2_person_type": "natural",
        },
    )
    assert response.status_code == 200
    assert b"List all countries of nationality for Party 2" in response.data

    response = client.post(
        "/",
        data={
            "step": "4",
            "party2_person_type": "natural",
            "party2_nationalities": "Philippines, Cambodia",
            "party2_last_acquired": "Philippines, Cambodia",
            "party2_domicile": "Cambodia",
        },
    )
    assert response.status_code == 200
    assert b"Where was the contract made?" in response.data
    assert b"Previous questions and answers" in response.data
    assert b"Does the contract specify which country&#39;s law to use?" in response.data
    assert b"N" in response.data

    response = client.post(
        "/",
        data={
            "step": "5",
            "party1_country": "Singapore",
            "party2_country": "N",
            "party2_person_type": "natural",
            "party2_nationalities": "Philippines, Cambodia",
            "party2_last_acquired": "Philippines, Cambodia",
            "party2_domicile": "Cambodia",
            "contract_place": "Malaysia",
        },
    )
    assert response.status_code == 200
    assert b"laws of Malaysia" in response.data
