from app import app

def test_empty_sentence():
    client = app.test_client()
    response = client.post('/polish', json = {"sentence": ""})
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Sentence cannot be empty"


def test_empty_spaces():
    client = app.test_client()
    response = client.post('/polish', json = {"sentence": "  "})
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Sentence cannot be empty"

def test_empty_json():
    client = app.test_client()
    response = client.post('/polish', json={})
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Sentence is not available for correction"

def test_valid_response():
    client = app.test_client()
    response = client.post('/polish', json={"sentence": "I was in car"})
    assert response.status_code == 200

    data = response.get_json()
    assert "polished_answer" in data
    assert isinstance(data["polished_answer"], str)
    assert data["polished_answer"].strip() != ""

