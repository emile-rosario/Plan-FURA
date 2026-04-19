"""
Tests de planes funerarios — listado público, CRUD admin, soft delete.
"""
import pytest

_PLAN = {
    "nombre": "Plan Test",
    "descripcion": "Plan creado en tests automatizados.",
    "precio_mensual": "999.00",
    "beneficios": ["Beneficio 1", "Beneficio 2"],
    "activo": True,
    "destacado": False,
}


def test_list_plans_public(client):
    """El listado de planes es público y devuelve estructura paginada."""
    res = client.get("/planes")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)


def test_list_plans_pagination(client):
    res = client.get("/planes?skip=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


def test_list_plans_limit_max(client):
    """limit > 100 debe ser rechazado."""
    res = client.get("/planes?limit=200")
    assert res.status_code == 422


def test_create_plan_requires_auth(client):
    res = client.post("/planes", json=_PLAN)
    assert res.status_code == 401


def test_create_plan_as_admin(client, admin_token):
    res = client.post(
        "/planes",
        json=_PLAN,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["nombre"] == _PLAN["nombre"]
    assert isinstance(data["beneficios"], list)
    assert data["beneficios"] == _PLAN["beneficios"]
    return data["id"]


def test_get_plan_by_id(client, admin_token):
    # Crear un plan primero
    create_res = client.post(
        "/planes",
        json={**_PLAN, "nombre": "Plan Get Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    plan_id = create_res.json()["id"]

    res = client.get(f"/planes/{plan_id}")
    assert res.status_code == 200
    assert res.json()["id"] == plan_id


def test_get_plan_not_found(client):
    res = client.get("/planes/99999")
    assert res.status_code == 404


def test_update_plan_as_admin(client, admin_token):
    create_res = client.post(
        "/planes",
        json={**_PLAN, "nombre": "Plan Update Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    plan_id = create_res.json()["id"]

    res = client.put(
        f"/planes/{plan_id}",
        json={"nombre": "Plan Actualizado"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    assert res.json()["nombre"] == "Plan Actualizado"


def test_soft_delete_plan(client, admin_token):
    """El DELETE desactiva el plan (soft delete) — no aparece en el listado."""
    create_res = client.post(
        "/planes",
        json={**_PLAN, "nombre": "Plan Soft Delete"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    plan_id = create_res.json()["id"]

    # Eliminar (soft delete)
    del_res = client.delete(
        f"/planes/{plan_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert del_res.status_code == 204

    # El plan aún existe en BD (accesible por ID)
    get_res = client.get(f"/planes/{plan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["activo"] is False

    # Pero NO aparece en el listado público (que filtra activo=True)
    list_res = client.get("/planes")
    ids_activos = [p["id"] for p in list_res.json()["items"]]
    assert plan_id not in ids_activos


def test_delete_plan_requires_admin(client):
    res = client.delete("/planes/1")
    assert res.status_code == 401
