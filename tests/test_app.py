import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_root_endpoint(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"

def test_cors_headers(client):
    rv = client.get("/")
    assert "Access-Control-Allow-Origin" in rv.headers
    assert "Access-Control-Allow-Methods" in rv.headers
    assert "Access-Control-Allow-Headers" in rv.headers

def test_jwks(client):
    rv = client.get("/.well-known/jwks.json")
    assert rv.status_code == 200
    assert "keys" in rv.get_json()

def test_jwks_has_valid_keys(client):
    rv = client.get("/.well-known/jwks.json")
    keys = rv.get_json()["keys"]
    assert len(keys) > 0
    assert "kid" in keys[0]
    assert "kty" in keys[0]
    assert keys[0]["kty"] == "RSA"

def test_auth_unexpired(client):
    rv = client.post("/auth")
    assert rv.status_code == 200
    assert "token" in rv.get_json()

def test_auth_token_has_kid(client):
    import jwt
    rv = client.post("/auth")
    token = rv.get_json()["token"]
    header = jwt.get_unverified_header(token)
    assert "kid" in header

def test_auth_expired(client):
    rv = client.post("/auth?expired=true")
    assert rv.status_code == 200
    assert "token" in rv.get_json()

def test_auth_token_payload(client):
    import jwt
    rv = client.post("/auth")
    token = rv.get_json()["token"]
    payload = jwt.decode(token, options={"verify_signature": False})
    assert payload["sub"] == "fake-user"