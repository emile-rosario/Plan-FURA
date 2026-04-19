"""
Tests de autenticación — registro, login, perfil, token inválido.
"""
import pytest

_USER = {
    "nombre": "Test Usuario",
    "email": "test_auth_user@example.com",
    "telefono": "8090000099",
    "password": "Test@1234",
}


def test_register_ok(client):
    res = client.post("/register", json=_USER)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == _USER["email"]
    assert data["rol"] == "cliente"
    assert "password" not in data


def test_register_duplicate_email(client):
    res = client.post("/register", json=_USER)
    assert res.status_code == 409
    assert "correo" in res.json()["detail"].lower()


def test_register_weak_password(client):
    bad = {**_USER, "email": "other@example.com", "password": "sinumeros"}
    res = client.post("/register", json=bad)
    assert res.status_code == 422  # Pydantic validation


def test_login_ok(client):
    res = client.post("/login", json={"email": _USER["email"], "password": _USER["password"]})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_email"] == _USER["email"]


def test_login_wrong_password(client):
    res = client.post("/login", json={"email": _USER["email"], "password": "Wrongpass1"})
    assert res.status_code == 401


def test_login_nonexistent_email(client):
    res = client.post("/login", json={"email": "noexiste@example.com", "password": "Test@1234"})
    assert res.status_code == 401


def test_me_with_valid_token(client):
    login = client.post("/login", json={"email": _USER["email"], "password": _USER["password"]})
    token = login.json()["access_token"]

    res = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == _USER["email"]


def test_me_with_invalid_token(client):
    res = client.get("/me", headers={"Authorization": "Bearer token.invalido.xyz"})
    assert res.status_code == 401


def test_me_without_token(client):
    res = client.get("/me")
    assert res.status_code == 401
