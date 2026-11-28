import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core import auth
from app.core.auth import AuthenticatedIdentity
from app.main import app


client = TestClient(app)


def test_auth_me_rejects_missing_bearer_token():
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_me_returns_only_verified_identity(monkeypatch):
    expected = AuthenticatedIdentity(issuer="https://identity.example.test/", subject="provider-user-123")
    monkeypatch.setattr(auth, "verify_access_token", lambda token: expected)

    response = client.get("/auth/me", headers={"Authorization": "Bearer signed-token"})

    assert response.status_code == 200
    assert response.json() == {"issuer": expected.issuer, "subject": expected.subject}


def test_verification_fails_closed_when_provider_is_unconfigured(monkeypatch):
    monkeypatch.setattr(auth.settings, "oidc_issuer", None)
    monkeypatch.setattr(auth.settings, "oidc_audience", None)
    monkeypatch.setattr(auth.settings, "oidc_jwks_url", None)

    with pytest.raises(HTTPException) as error:
        auth.verify_access_token("anything")

    assert error.value.status_code == 503


def test_invalid_token_is_rejected(monkeypatch):
    class SigningKey:
        key = "test-public-key"

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, token):
            return SigningKey()

    monkeypatch.setattr(auth.settings, "oidc_issuer", "https://issuer.example.test/")
    monkeypatch.setattr(auth.settings, "oidc_audience", "atlas-api")
    monkeypatch.setattr(auth.settings, "oidc_jwks_url", "https://issuer.example.test/.well-known/jwks.json")
    monkeypatch.setattr(auth, "_jwks_client", lambda url: FakeJwksClient())
    monkeypatch.setattr(auth.jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(auth.jwt.InvalidTokenError("signature mismatch")))

    with pytest.raises(HTTPException) as error:
        auth.verify_access_token("forged-token")

    assert error.value.status_code == 401
