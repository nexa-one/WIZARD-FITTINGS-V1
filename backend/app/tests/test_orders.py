import pytest
from httpx import AsyncClient

REGISTER = {
    "tenant_name": "Orders Test Co",
    "email": "orders@test.com",
    "full_name": "Orders User",
    "password": "Orders@123",
}

ORDER_PAYLOAD = {
    "request_number": "REQ-001",
    "requester_name": "John Doe",
    "order_date": "2026-05-03",
    "urgency": "high",
    "piece_quantity": 5,
    "status": "draft",
    "order_type": "standard",
    "notes": "Priority order for zone A",
    "tags": ["urgent", "zone-a"],
    "items": [
        {"description": "90-degree elbow 12x12", "quantity": 2, "unit": "ea"},
        {"description": "Straight duct 24in", "quantity": 3, "unit": "ea"},
    ],
}


async def _get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/register", json=REGISTER)
    resp = await client.post("/api/v1/auth/login", json={"email": REGISTER["email"], "password": REGISTER["password"]})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient):
    token = await _get_token(client)
    response = await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["request_number"] == "REQ-001"
    assert data["status"] == "draft"
    assert len(data["items"]) == 2
    assert "zone-a" in data["tags"]


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient):
    token = await _get_token(client)
    create_resp = await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    order_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == order_id


@pytest.mark.asyncio
async def test_update_order_status(client: AsyncClient):
    token = await _get_token(client)
    create_resp = await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    order_id = create_resp.json()["id"]
    response = await client.patch(
        f"/api/v1/orders/{order_id}",
        json={"status": "pending"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_search_orders(client: AsyncClient):
    token = await _get_token(client)
    await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    response = await client.get("/api/v1/orders/search?search=REQ-001", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_delete_order(client: AsyncClient):
    token = await _get_token(client)
    create_resp = await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    order_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    get_resp = await client.get(f"/api/v1/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_order_tenant_isolation(client: AsyncClient):
    # Create order with tenant 1
    token = await _get_token(client)
    create_resp = await client.post("/api/v1/orders/", json=ORDER_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    order_id = create_resp.json()["id"]

    # Register a different tenant
    register2 = {**REGISTER, "email": "other@tenant.com", "tenant_name": "Other Co"}
    await client.post("/api/v1/auth/register", json=register2)
    login2 = await client.post("/api/v1/auth/login", json={"email": register2["email"], "password": REGISTER["password"]})
    token2 = login2.json()["access_token"]

    # Should not be able to access tenant 1's order
    response = await client.get(f"/api/v1/orders/{order_id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404
