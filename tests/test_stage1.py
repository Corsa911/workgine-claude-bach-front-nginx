import uuid
import pytest
from jose import jwt
from app.platform.config import settings
from app.platform.security import ALGORITHM


async def account(client, name):
    payload = {"email": f"{name}@example.com", "password": "test-password-123"}
    registered = await client.post("/api/v1/auth/register", json=payload)
    assert registered.status_code == 201, registered.text
    login = await client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    return headers, me.json()


def draft(**extra):
    return {
        "title": "Дизайн сайта",
        "description": "Нужен дизайн трех страниц интернет-магазина",
        "budget_minor": 5000000,
        **extra,
    }


@pytest.mark.asyncio
async def test_identity_roles_and_duplicate_registration(client):
    headers, me = await account(client, "owner")
    assert me["active_role"] is None
    for role in ["customer", "executor", "customer"]:
        result = await client.patch(
            "/api/v1/auth/me/role", json={"active_role": role}, headers=headers
        )
        assert result.status_code == 200
        assert result.json()["workspace_id"] == me["workspace_id"]
        assert (await client.get("/api/v1/auth/me", headers=headers)).json()[
            "active_role"
        ] == role
    assert (
        await client.patch(
            "/api/v1/auth/me/role", json={"active_role": "admin"}, headers=headers
        )
    ).status_code == 422
    assert (
        await client.post(
            "/api/v1/auth/register",
            json={"email": "OWNER@example.com", "password": "another-password"},
        )
    ).status_code == 409
    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "wrong"},
        )
    ).status_code == 401


@pytest.mark.asyncio
async def test_private_draft_and_ownership(client):
    alice, a = await account(client, "alice")
    bob, b = await account(client, "bob")
    assert (await client.post("/api/v1/orders", json=draft())).status_code == 401
    assert (
        await client.post(
            "/api/v1/orders",
            json=draft(customer_workspace_id=b["workspace_id"]),
            headers=alice,
        )
    ).status_code == 422
    created = await client.post("/api/v1/orders", json=draft(), headers=alice)
    assert created.status_code == 201
    order = created.json()
    assert order["customer_workspace_id"] == a["workspace_id"]
    path = "/api/v1/orders/" + order["id"]
    assert (await client.get(path, headers=bob)).status_code == 404
    assert (await client.get("/api/v1/orders", headers=bob)).json() == []
    assert (
        await client.put(path, json=draft(version=1), headers=bob)
    ).status_code == 404
    assert (
        await client.post(path + "/publish", json={"version": 1}, headers=bob)
    ).status_code == 404
    assert (
        len((await client.get("/api/v1/orders?scope=mine", headers=alice)).json()) == 1
    )
    assert (
        await client.post(path + "/publish", json={"version": 1}, headers=alice)
    ).status_code == 422
    updated = await client.put(
        path, json=draft(title="Новый заголовок", version=1), headers=alice
    )
    assert updated.status_code == 200 and updated.json()["version"] == 2
    assert (
        await client.put(path, json=draft(version=1), headers=alice)
    ).status_code == 409


@pytest.mark.asyncio
async def test_profile_isolation_and_validation(client):
    alice, a = await account(client, "alice")
    bob, b = await account(client, "bob")
    r = await client.put(
        "/api/v1/profiles/me",
        json={"description": "Дизайнер", "hourly_rate_minor": 100000},
        headers=alice,
    )
    assert r.status_code == 200
    assert r.json()["workspace_id"] == a["workspace_id"]
    assert (await client.get("/api/v1/profiles/me", headers=bob)).json()[
        "description"
    ] == ""
    assert (
        await client.put(
            "/api/v1/profiles/me",
            json={"description": "Чужое", "workspace_id": b["workspace_id"]},
            headers=alice,
        )
    ).status_code == 422
    assert (
        await client.post("/api/v1/orders", json=draft(budget_minor=-1), headers=alice)
    ).status_code == 422
    assert (
        await client.post(
            "/api/v1/orders", json=draft(category_id=str(uuid.uuid4())), headers=alice
        )
    ).status_code == 422


@pytest.mark.asyncio
async def test_bad_tokens_and_disabled_legacy_endpoints(client):
    for sub in ["not-a-uuid", None]:
        token = jwt.encode({"sub": sub}, settings.SECRET_KEY, algorithm=ALGORITHM)
        assert (
            await client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer " + token}
            )
        ).status_code == 401
    for path in [
        "payments/",
        "applications/",
        "disputes/",
        "notifications/",
        "chat/rooms/",
    ]:
        assert (await client.get("/api/v1/" + path)).status_code == 404


@pytest.mark.asyncio
async def test_publish_full_journey(client):
    from app.platform.database import get_db
    from app.main import app
    from app.modules.catalog.models import Category

    category_id = uuid.uuid4()
    async for db in app.dependency_overrides[get_db]():
        db.add(Category(id=category_id, name="Дизайн", slug="design"))
        await db.commit()
    alice, a = await account(client, "alice")
    bob, b = await account(client, "bob")
    created = await client.post(
        "/api/v1/orders", json=draft(category_id=str(category_id)), headers=alice
    )
    assert created.status_code == 201
    path = "/api/v1/orders/" + created.json()["id"]
    result = await client.post(path + "/publish", json={"version": 1}, headers=alice)
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "published"
    assert (await client.get(path, headers=bob)).status_code == 200
    assert len((await client.get("/api/v1/orders", headers=bob)).json()) == 1
    assert (await client.get("/api/v1/orders", headers=alice)).json() == []
    assert (
        await client.post(path + "/publish", json={"version": 2}, headers=alice)
    ).status_code == 409
    assert (
        await client.put(path, json=draft(version=2), headers=alice)
    ).status_code == 409
    assert (
        await client.get("/api/v1/orders?q=несуществующий", headers=bob)
    ).json() == []
    assert (await client.get("/api/v1/orders?offset=1", headers=bob)).json() == []
