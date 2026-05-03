import pytest
from httpx import AsyncClient

REGISTER = {
    "tenant_name": "Fittings Test Co",
    "email": "fittings@test.com",
    "full_name": "Fittings User",
    "password": "Fittings@123",
}

FITTING_PAYLOAD = {
    "name": "90-Degree Elbow 12x12",
    "fitting_type": "elbow",
    "material": "galvanized",
    "connection_type": "slip",
    "dimensions": {
        "width_inlet": 12.0,
        "height_inlet": 12.0,
        "angle": 90.0,
        "radius": 18.0,
    },
    "gauge": "26",
    "description": "Standard 90-degree elbow for HVAC ducting",
}


async def _get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/register", json=REGISTER)
    resp = await client.post("/api/v1/auth/login", json={"email": REGISTER["email"], "password": REGISTER["password"]})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_fitting(client: AsyncClient):
    token = await _get_token(client)
    response = await client.post("/api/v1/fittings/", json=FITTING_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == FITTING_PAYLOAD["name"]
    assert data["fitting_type"] == "elbow"
    assert "geometry_data" in data
    assert data["geometry_data"]["type"] == "elbow"


@pytest.mark.asyncio
async def test_get_fitting(client: AsyncClient):
    token = await _get_token(client)
    create_resp = await client.post("/api/v1/fittings/", json=FITTING_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    fitting_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/fittings/{fitting_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == fitting_id


@pytest.mark.asyncio
async def test_list_fittings(client: AsyncClient):
    token = await _get_token(client)
    await client.post("/api/v1/fittings/", json=FITTING_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    response = await client.get("/api/v1/fittings/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_geometry_engine_produces_data(client: AsyncClient):
    token = await _get_token(client)
    response = await client.post("/api/v1/fittings/", json=FITTING_PAYLOAD, headers={"Authorization": f"Bearer {token}"})
    geo = response.json()["geometry_data"]
    assert geo["type"] == "elbow"
    assert "inlet" in geo
    assert "outlet" in geo
    assert geo["angle_deg"] == 90.0


@pytest.mark.asyncio
async def test_create_tee_fitting(client: AsyncClient):
    token = await _get_token(client)
    tee = {**FITTING_PAYLOAD, "name": "Tee 12x12x8", "fitting_type": "tee",
           "dimensions": {"width_inlet": 12, "height_inlet": 12, "neck_width": 8, "neck_height": 8, "length": 24}}
    response = await client.post("/api/v1/fittings/", json=tee, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["geometry_data"]["type"] == "tee"
